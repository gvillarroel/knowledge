"""Profile changes must preserve evidence authority and affect nested family plans."""
from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def module(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


helper = module("test_profile_helper", "evaluations/skill-evolution/apply_retrieval_profile.template.py")
plans = module("test_profile_plans", "evaluations/private-book-strategy-comparison/scripts/prepare_strategy_bundles.py")


@pytest.mark.parametrize("mechanism", ["neural-record", "quarter-expansion", "bm25-low-b", "stronger-titles"])
def test_profile_has_nested_effect_without_changing_source_or_evidence_contract(mechanism):
    grid = json.loads((ROOT / "evaluations/skill-evolution/proposal-grid.json").read_text(encoding="utf-8"))
    proposal = next(row for row in grid["generation_zero"] if row["id"] == mechanism)
    operation = {key: value for key, value in proposal.items() if key not in {"id", "mechanism"}}
    original = plans.ensemble_plan(["manuals"])
    before = copy.deepcopy(original)
    observed = helper.apply_profile(original, [operation])
    assert original == before and observed != original
    for key in ("identity", "policies", "quality_gates"):
        assert observed[key] == original[key]
    for key in ("adaptive", "entity_graph", "embedding"):
        assert observed[key]["selection"] == original[key]["selection"]
    assert observed["embedding"]["chunking"] == original["embedding"]["chunking"]
    if mechanism == "neural-record":
        assert observed["embedding"]["embedding"]["provider"] == "sentence-transformers"
    elif mechanism == "quarter-expansion":
        assert observed["adaptive"]["expansion"]["association_weight"] == pytest.approx(.0875)
    elif mechanism == "bm25-low-b":
        assert observed["adaptive"]["bm25"]["b"] == observed["entity_graph"]["bm25"]["b"] == .25
    else:
        assert observed["adaptive"]["bm25"]["title_weight"] == 4


def test_nonconflicting_merges_commute_and_do_not_add_missing_fields():
    plan = plans.ensemble_plan(["manuals"])
    first = {"operation": "bm25-b", "value": .25}
    second = {"operation": "expansion-scale", "factor": .25}
    assert helper.apply_profile(plan, [first, second]) == helper.apply_profile(plan, [second, first])
    assert helper.apply_profile({"selection": {"source_ids": ["manuals"]}}, [first, second]) == {"selection": {"source_ids": ["manuals"]}}
