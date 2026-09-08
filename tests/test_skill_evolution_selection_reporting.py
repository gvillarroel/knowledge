"""The final audit must obey the frozen order and never consume a private gate."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


@pytest.fixture
def reporter(monkeypatch):
    root = Path(__file__).resolve().parents[1] / "evaluations/skill-evolution"
    monkeypatch.syspath_prepend(str(root))
    spec = importlib.util.spec_from_file_location("tested_selection_reporter", root / "report_selection.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def archive_fixture(candidates):
    keys = [f"synthetic-cell-{i}" for i in range(32)]

    def record(identifier, values, mean):
        return {"candidateId": identifier, "skillDigest": "sealed-" + identifier,
                "evaluable": True, "qualification": {"passed": True}, "promotionEligibleProvenance": True, "lockPresent": True,
                "summary": {"expectedTrials": 32, "completedTrials": 32, "errorCount": 0, "meanReward": mean},
                "cases": [{"caseKey": key, "meanReward": value} for key, value in zip(keys, values, strict=True)]}

    records = [record("baseline", [.5] * 32, .5)]
    entries = []
    for identifier, mean, pair in candidates:
        values = [*pair, *([mean] * 30)]
        item = record(identifier, values, mean)
        records.append(item)
        entries.append({"candidateId": identifier, "skillDigest": item["skillDigest"], "qualified": True,
                        "evaluable": True, "promotionEligibleProvenance": True, "aggregateMean": mean,
                        "vector": item["cases"]})
    return {"source": "harbor", "strategy": "reflective-pareto-search", "holdoutDataUsed": False,
            "promotionEligibleProfile": True, "requiredRewardThresholds": {"evidence_integrity": 1},
            "caseKeys": keys, "candidateResults": records, "archive": entries,
            "generation": 0, "generationSeal": "synthetic-seal", "developmentProfileDigest": "synthetic-profile"}


def test_native_mean_has_priority_over_regression_count(reporter):
    archive = archive_fixture([("no-regression", .6, (.51, .69)), ("larger-mean", .61, (.49, .73))])
    output = reporter.project(archive, {"no-regression": 1, "larger-mean": 1})
    assert output["selected_candidate"] == "larger-mean"
    assert output["archive_members"][0]["regressed_cells"] == 1
    assert output["eligible_for_one_way_validation"] is True
    assert output["promotion_established"] is False


def test_equal_means_use_regressions_then_operations_then_identifier(reporter):
    archive = archive_fixture([("one-regression", .6, (.49, .71)), ("two-operations", .6, (.51, .69)),
                               ("z-one-operation", .6, (.52, .68)), ("a-one-operation", .6, (.53, .67))])
    output = reporter.project(archive, {"one-regression": 1, "two-operations": 2, "z-one-operation": 1, "a-one-operation": 1})
    assert [row["candidate"] for row in output["archive_members"]] == ["a-one-operation", "z-one-operation", "two-operations", "one-regression"]
    assert output["selected_candidate"] == "a-one-operation"
    assert output["native_candidate_count"] == 5


def test_subthreshold_gain_keeps_the_gate_sealed(reporter):
    archive = archive_fixture([("small-gain", .509, (.508, .510))])
    output = reporter.project(archive, {"small-gain": 1})
    assert output["ranked_first"] == "small-gain"
    assert output["selected_candidate"] is None
    assert output["selected_skill_digest"] is None
    assert output["decision"] == "retain-baseline-and-keep-validation-sealed"


def test_incomplete_baseline_cannot_support_an_apparent_improvement(reporter):
    archive = archive_fixture([("large-apparent-gain", .8, (.79, .81))])
    archive["candidateResults"][0]["summary"].update(completedTrials=31, errorCount=1)
    output = reporter.project(archive, {"large-apparent-gain": 1})
    assert output["baseline_qualified"] is False
    assert output["baseline_mean_ndcg_at_10"] is None
    assert output["archive_members"][0]["mean_gain"] is None
    assert output["selected_candidate"] is None


@pytest.mark.parametrize("defect,match", [("private", "development-only"), ("unqualified", "completely qualified"),
                                         ("missing-cell", "omits or duplicates"), ("digest", "digest differs")])
def test_invalid_finalist_evidence_fails_closed(reporter, defect, match):
    archive = archive_fixture([("candidate", .6, (.59, .61))])
    if defect == "private":
        archive["holdoutDataUsed"] = True
    elif defect == "unqualified":
        archive["archive"][0]["qualified"] = False
    elif defect == "missing-cell":
        archive["archive"][0]["vector"].pop()
    elif defect == "digest":
        archive["archive"][0]["skillDigest"] = "other-package"
    with pytest.raises(ValueError, match=match):
        reporter.project(archive, {"candidate": 1})


@pytest.mark.parametrize("invalid", [float("nan"), float("inf"), True])
def test_nonfinite_or_boolean_native_means_cannot_win(reporter, invalid):
    archive = archive_fixture([("candidate", .6, (.59, .61))])
    archive["archive"][0]["aggregateMean"] = invalid
    with pytest.raises(ValueError, match="finite native"):
        reporter.project(archive, {"candidate": 1})
