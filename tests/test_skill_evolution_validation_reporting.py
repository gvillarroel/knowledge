"""Terminal reports must retain rejected outcomes without releasing private cases."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest


@pytest.fixture
def reporter(monkeypatch):
    root = Path(__file__).resolve().parents[1] / "evaluations/skill-evolution"
    monkeypatch.syspath_prepend(str(root))
    spec = importlib.util.spec_from_file_location("tested_terminal_reporter", root / "aggregate_validation.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def evidence(tmp_path):
    paths = {}
    for role in ("baseline", "candidate"):
        path = tmp_path / role
        path.mkdir()
        paths[role] = str(path)
        stats = {"n_completed_trials": 16, "n_errored_trials": 0, "n_retries": 0,
                 "n_input_tokens": 0, "n_output_tokens": 0, "n_cache_tokens": 0, "cost_usd": 0}
        (path / "result.json").write_text(json.dumps({"stats": stats}), encoding="utf-8")
        (path / "lock.json").write_text("{}", encoding="utf-8")
    gate = {"promotionRules": {"minimumMeanGain": .01, "allowCaseRegressions": False, "requireNoErrors": True},
            "perCase": [{"question": "PRIVATE QUESTION", "taskName": f"PRIVATE-TASK-{i}"} for i in range(16)],
            "baselineQualified": True, "candidateQualified": True, "baselineEvaluable": True, "candidateEvaluable": True,
            "baselineMeanReward": .5, "candidateMeanReward": .6, "meanGain": .1,
            "promoted": False, "selectedCandidate": "synthetic-profile", "status": "complete", "evaluable": True,
            "regressedCases": ["PRIVATE-REGRESSION"], "requiredRewardsComplete": True, "profileMatchesDeclared": True}
    promotion = {"source": "harbor", "holdout": gate, "jobs": paths, "holdoutChecksums": [f"PRIVATE-SHA-{i}" for i in range(16)],
                 "selectedSkillDigest": "fixture-skill", "developmentProfileDigest": "fixture-profile"}
    report = {"source": "harbor", "jobs": [{"jobDirectory": path, "complete": True} for path in paths.values()]}
    return promotion, report


def test_rejected_positive_gain_is_preserved_without_private_payloads(reporter, tmp_path):
    output = reporter.project(*evidence(tmp_path))
    assert output["decision"] == "keep-baseline"
    assert output["mean_gain"] == .1
    assert output["regressed_cell_count"] == 1
    assert output["further_evolution_permitted_in_this_study"] is False
    assert "PRIVATE" not in json.dumps(output)
    assert str(tmp_path) not in json.dumps(output)


def test_unqualified_partial_gate_is_not_a_comparable_improvement(reporter, tmp_path):
    promotion, report = evidence(tmp_path)
    promotion["holdout"].update(candidateQualified=False, candidateEvaluable=False, evaluable=False, status="non-evaluable")
    output = reporter.project(promotion, report)
    assert output["decision"] == "keep-baseline"
    assert output["mean_gain"] is None
    assert output["native_diagnostic_mean_gain"] == .1
    assert output["roles"]["candidate"]["mean_ndcg_at_10"] is None
    assert output["roles"]["candidate"]["native_diagnostic_mean_reward"] == .6


@pytest.mark.parametrize("change,match", [
    ("incomplete", "incomplete"), ("portfolio", "16 registered"),
    ("rule", "frozen study"), ("job", "two terminal"),
    ("qualification", "complete-integrity"), ("accounting", "unavailable"),
])
def test_terminal_export_rejects_incomplete_or_inconsistent_evidence(reporter, tmp_path, change, match):
    promotion, report = evidence(tmp_path)
    if change == "incomplete":
        report["jobs"][1]["complete"] = False
    elif change == "portfolio":
        promotion["holdout"]["perCase"].pop()
    elif change == "rule":
        promotion["holdout"]["promotionRules"]["allowCaseRegressions"] = True
    elif change == "job":
        report["jobs"].pop()
    elif change == "qualification":
        promotion["holdout"].update(promoted=True, baselineQualified=False)
    elif change == "accounting":
        path = Path(promotion["jobs"]["candidate"]) / "result.json"
        document = json.loads(path.read_text(encoding="utf-8"))
        document["stats"]["cost_usd"] = None
        path.write_text(json.dumps(document), encoding="utf-8")
    with pytest.raises(ValueError, match=match):
        reporter.project(promotion, report)
