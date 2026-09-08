"""Behavioral checks for a bounded, leakage-safe Enterprise evolution schedule."""
from __future__ import annotations

import copy
import importlib.util
import math
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / "evaluations/enterprise-evolution"


def module(name):
    spec = importlib.util.spec_from_file_location("enterprise_test_"+name, HERE / (name+".py"))
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


profiles, scheduler = module("profiles"), module("sweep")


def schedule():
    return scheduler.Sweep([{"id": "first", "variants": [1, 2, 3, 4, 5, 6]}, {"id": "second", "variants": [7, 8, 9, 10]}], "baseline", 0.5, {"x": 0})


def test_three_consecutive_misses_advance_strategy():
    sweep = schedule()
    for index in range(3):
        strategy, variant = sweep.next()
        assert strategy["id"] == "first"
        sweep.observe(str(index), {"x": variant}, 0.4)
    assert sweep.next()[0]["id"] == "second"
    finish = next(e for e in sweep.events if e["event"] == "strategy-finished")
    assert finish == {"event": "strategy-finished", "strategy": "first", "reason": "three-consecutive-failures", "failures": 3, "unused_variants": 3}


def test_success_resets_streak_and_preserves_parent():
    sweep = schedule()
    for index, score in enumerate((0.4, 0.5, 0.6, 0.55, 0.59)):
        assert sweep.next()[0]["id"] == "first"
        sweep.observe(str(index), {"x": index}, score)
    assert sweep.failures == 2
    assert sweep.best_id == "2" and sweep.profile == {"x": 2}
    assert sweep.next()[1] == 6


def test_exhaustion_without_three_failures_is_explicit():
    sweep = scheduler.Sweep([{"id": "small", "variants": [1]}], "baseline", .5, {})
    sweep.next()
    sweep.observe("winner", {"x": 1}, .6)
    assert sweep.next() is None
    assert sweep.events[-1]["reason"] == "catalog-exhausted"
    assert sweep.events[-1]["failures"] == 0


def test_duplicates_do_not_spend_trials_or_failures():
    sweep = schedule()
    assert not sweep.claim({"x": 0})
    assert sweep.claim({"x": 1})
    assert not sweep.claim({"x": 1})
    assert sweep.failures == 0


def test_unavailable_is_not_a_semantic_zero():
    sweep = schedule()
    with pytest.raises(RuntimeError, match="Non-evaluable"):
        sweep.observe("external", {}, .9, evaluable=False)
    assert sweep.best_score == .5 and sweep.failures == 0
    assert sweep.events[-1]["score"] is None


def test_integrity_failure_cannot_win_even_with_high_score():
    sweep = schedule()
    assert not sweep.observe("bad", {}, 1.0, qualified=False)
    assert sweep.best_id == "baseline" and sweep.failures == 1


@pytest.mark.parametrize("score", [math.nan, math.inf, -math.inf, True, "0.9"])
def test_invalid_measurements_rejected(score):
    with pytest.raises(ValueError):
        schedule().observe("bad", {}, score)


def test_finite_inventory_and_treatment_isolation():
    assert sum(len(s["variants"]) for f in profiles.FAMILIES for s in profiles.inventory(f)) == 116
    base = profiles.baseline_profile()
    for family in profiles.FAMILIES:
        for strategy in profiles.inventory(family):
            for variant in strategy["variants"]:
                child = profiles.mutate(base, family, variant)
                assert {k: v for k, v in child.items() if k != family} == {k: v for k, v in base.items() if k != family}
                channel = "search" if family in profiles.CONSTRUCTION else "plan"
                assert child[family][channel] == base[family][channel]
    assert base == profiles.baseline_profile()


def test_plan_cannot_change_source_or_invent_field():
    plan = {"selection": {"source_ids": ["fixture"]}, "bm25": {"b": .75}}
    baseline = copy.deepcopy(plan)
    profile = profiles.baseline_profile()
    profile["classical"]["plan"] = {"bm25.b": .25}
    assert profiles.apply_plan(plan, profile, "classical") == {"selection": baseline["selection"], "bm25": {"b": .25}}
    assert plan == baseline
    profile["classical"]["plan"] = {"bm25.missing": 4}
    with pytest.raises(ValueError, match="invent"):
        profiles.apply_plan(plan, profile, "classical")


def test_bm25_is_deterministic_and_returns_exact_authoritative_rows():
    rows = [{"record_id": "b", "title": "Amber", "body": "amber amber violet", "record_sha256": "b"}, {"record_id": "a", "title": "Violet", "body": "violet amber", "record_sha256": "a"}]
    original = copy.deepcopy(rows)
    index = profiles.LexicalIndex(rows, {"k1": 1.2, "b": .25})
    assert index.search("amber") == index.search("amber")
    assert all(row in original for row in index.search("amber"))
    assert rows == original
    assert index.search("absent") == []
    assert profiles.LexicalIndex([], {}).search("anything") == []


def test_rrf_uses_both_rankings_without_duplicate_evidence():
    a, b, c = ({"record_id": x} for x in "abc")
    result = profiles.fuse([a, b], [c, b], {"lexical_weight": 2, "rrf_k": 0})
    assert result == [c, b, a]
    assert len({r["record_id"] for r in result}) == 3


def test_staged_helper_matches_profile_api():
    text = (HERE / "prepare.py").read_text(encoding="utf-8")
    assert "mutable_skill_paths\"] = [\"assets/retrieval-profile.json\"]" in text
    # Scope-level guard: no benchmark questions or labels in the mutation bundle.
    for name in ("profiles.py", "sweep.py"):
        content = (HERE / name).read_text(encoding="utf-8")
        assert "-qrels" not in content and "tests/contract.json" not in content
