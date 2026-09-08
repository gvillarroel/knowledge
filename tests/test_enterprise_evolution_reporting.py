"""Prevent false plateau claims and incorrect native source rebinding."""
import copy
import importlib.util
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parents[1] / "evaluations/enterprise-evolution"


def load(name):
    sys.path.insert(0, str(HERE))
    try:
        spec = importlib.util.spec_from_file_location("enterprise_reporting_test_"+name, HERE / (name+".py"))
        value = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(value)
        return value
    finally:
        sys.path.remove(str(HERE))


report = load("report")
runner = load("run")


def fixture():
    strategies = [{"id": "length", "variants": [{"bm25.b": n} for n in (.25, .0, .5, 1.0)]}]
    profile = report.baseline_profile()
    state = report.Sweep(strategies, "baseline", .5, profile)
    outcomes = [{"candidate": "baseline", "score": .5}]
    index = 0
    while proposed := state.next():
        strategy, variant = proposed
        child = report.mutate(state.profile, "classical", variant)
        if not state.claim(child):
            continue
        index += 1
        identifier = f"candidate-{index:03d}"
        improved = state.observe(identifier, child, .4)
        outcomes.append({"candidate": identifier, "score": .4, "qualified": True, "strategy": strategy["id"], "variant": variant, "improved": improved, "consecutive_failures": state.failures, "best_candidate": state.best_id, "best_score": state.best_score})
    return strategies, {"family": "classical", "baseline_score": .5, "generation": index, "winner": {"id": state.best_id}, "profile": state.profile, "outcomes": outcomes, "events": state.events}


def test_full_stopping_ledger_replays():
    strategies, result = fixture()
    report.audit_family(result, strategies)


def test_missing_attempt_cannot_be_claimed_as_exhaustion():
    strategies, result = fixture()
    result["outcomes"].pop()
    with pytest.raises(ValueError, match="Missing or reordered"):
        report.audit_family(result, strategies)


def test_fabricated_improvement_or_miss_streak_rejected():
    strategies, result = fixture()
    result["outcomes"][1]["improved"] = True
    with pytest.raises(ValueError, match="incumbent or miss streak"):
        report.audit_family(result, strategies)


def test_extra_attempt_after_three_misses_rejected():
    strategies, result = fixture()
    result["outcomes"].append(copy.deepcopy(result["outcomes"][-1]))
    with pytest.raises(ValueError, match="budget"):
        report.audit_family(result, strategies)


def test_forged_final_winner_rejected():
    strategies, result = fixture()
    result["winner"]["id"] = "unmeasured"
    with pytest.raises(ValueError, match="Terminal ledger or winner"):
        report.audit_family(result, strategies)


def test_config_uses_exact_native_staged_control_path():
    path = "/independent/search/generation-000/candidate-staging/baseline/skills/build-semantic-okf-knowledge-skill"
    candidates = [{"id": "baseline", "skill": path, "parents": [], "jobDirectory": "/independent/completed-native-job"}]
    result = runner.raw_config("legacy", 1, candidates)
    assert result["search"]["baselineSkill"] == path
    assert result["candidates"][0]["jobDirectory"] == "/independent/completed-native-job"
    assert Path(result["search"]["previousGenerationLog"]).parts[-2:] == ("generation-000", "pareto-archive.json")


@pytest.mark.parametrize("value", [True, "0.5", float("inf"), -0.1, 1.1])
def test_public_quality_must_be_a_real_bounded_measurement(value):
    with pytest.raises(ValueError, match="aggregate quality"):
        report.quality(value)


def test_native_timing_is_not_invented():
    assert report.seconds(None) is None
    assert report.seconds({"started_at": "2026-09-07T10:00:00", "finished_at": None}) is None
    assert report.seconds({"started_at": "2026-09-07T10:00:00", "finished_at": "2026-09-07T10:00:03"}) == 3
    with pytest.raises(ValueError, match="Reversed"):
        report.seconds({"started_at": "2026-09-07T10:00:03", "finished_at": "2026-09-07T10:00:00"})
