"""Tests for the empirical knowledge-methodology proposal experiment."""

from __future__ import annotations

import importlib.util
from copy import deepcopy
import json
import math
from pathlib import Path
import subprocess
import sys

import pytest


REPO = Path(__file__).resolve().parents[1]
ROOT = (
    REPO
    / "evaluations"
    / "knowledge-methodology-proposal-experiments"
)
RUNNER = ROOT / "scripts" / "run_offline_ablation.py"
VALIDATOR = ROOT / "scripts" / "validate_experiment.py"
REPORT = ROOT / "reports" / "offline-ablation-01.json"


def _load_module(path: Path, name: str):
    specification = importlib.util.spec_from_file_location(
        name,
        path,
    )
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    return module


def _load_runner():
    return _load_module(
        RUNNER,
        "knowledge_methodology_offline_ablation",
    )


def test_document_metrics_use_non_exhaustive_qrels_consistently() -> None:
    """Recall, reciprocal rank, and nDCG follow the frozen document contract."""

    module = _load_runner()
    metrics = module._query_metrics(
        ["paper-c", "paper-a", "paper-d", "paper-b"],
        frozenset({"paper-a", "paper-b"}),
        cutoff=3,
    )
    assert metrics["recall_at_10"] == 0.5
    assert metrics["mrr_at_10"] == 0.5
    expected_dcg = 1.0 / math.log2(3.0)
    expected_ideal = 1.0 + 1.0 / math.log2(3.0)
    assert metrics["ndcg_at_10"] == expected_dcg / expected_ideal


def test_fixed_chunking_preserves_identity_and_overlap() -> None:
    """Fixed units are stable and the registered overlap changes the step."""

    module = _load_runner()
    paper = module.Paper(
        identifier="0000.00000v1",
        path=Path("paper.md"),
        pages=(" ".join(f"token{index}" for index in range(20)),),
    )
    units = module._fixed_units(paper, size=8, overlap=2)
    assert [unit.identifier for unit in units] == [
        "0000.00000v1:fixed:00001",
        "0000.00000v1:fixed:00002",
        "0000.00000v1:fixed:00003",
    ]
    assert all(unit.paper_id == paper.identifier for unit in units)
    assert units[0].text.split()[-2:] == units[1].text.split()[:2]


def test_accepted_experiment_validates_and_keeps_exposure_label() -> None:
    """The accepted report covers every cell and cannot claim promotion."""

    completed = subprocess.run(
        [sys.executable, str(VALIDATOR)],
        cwd=REPO,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    validation = json.loads(completed.stdout)
    assert validation["status"] == "pass"
    assert validation["dataset_count"] == 2
    assert validation["treatment_count"] == 42
    assert validation["question_result_count"] == 1680
    assert validation["decision_count"] == 10

    report = json.loads(REPORT.read_text(encoding="utf-8"))
    assert report["candidate_state"] == "retrospective-all-qrels-exposed"
    assert report["promotion_eligible"] is False
    assert report["analysis"]["proposal_findings"] == {
        "KM-004": {
            "finding": "strong-support",
            "registered_rule_satisfied": True,
            "strong_rule_satisfied": True,
        },
        "KM-005": {
            "domain_winners_differ": True,
            "finding": "partial-support",
            "pareto_frontier_size": 14,
            "registered_rule_satisfied": True,
        },
        "KM-006": {
            "finding": "support",
            "maximum_recall_interval_width": 0.16249999999999998,
            "registered_rule_satisfied": True,
        },
    }
    decisions = json.loads(
        (
            ROOT
            / "reports"
            / "offline-ablation-01-decisions.json"
        ).read_text(encoding="utf-8")
    )
    assert decisions["promotion_eligible"] is False
    assert {
        row["classification"] for row in decisions["decisions"]
    } == {
        "does-not-exist",
        "does-not-work",
        "cost-balanced-tradeoff",
        "inconclusive",
        "mixed-domain-dependent",
        "quality-dominant-tradeoff",
        "useful-control-inconclusive-recall",
        "works-strongly",
        "works-with-recall-caveat",
    }


def test_validator_rejects_reported_input_drift() -> None:
    """Accepted evidence remains bound to the exact question and paper bytes."""

    module = _load_module(
        VALIDATOR,
        "validate_knowledge_methodology_offline_ablation",
    )
    config = json.loads(
        (ROOT / "experiment.json").read_text(encoding="utf-8")
    )
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    datasets = deepcopy(report["deterministic"]["datasets"])
    datasets["graphrag-papers-40"]["inputs"]["papers"]["sha256"] = "0" * 64
    with pytest.raises(module.ValidationError, match="input binding drift"):
        module._validate_dataset_inputs(config, datasets)


def test_hybrid_runtime_accounts_for_both_retrievers_and_fusion() -> None:
    """The invalid attempt cannot recur through partial hybrid timing."""

    report = json.loads(REPORT.read_text(encoding="utf-8"))
    runtime = report["runtime"]["datasets"]
    for dataset in runtime.values():
        for treatment_id, timing in dataset.items():
            if treatment_id.endswith("::rrf-hybrid"):
                assert timing["accounting"] == (
                    "bm25-plus-tfidf-plus-fusion"
                )
            else:
                assert timing["accounting"] == (
                    "retriever-score-and-document-aggregation"
                )
