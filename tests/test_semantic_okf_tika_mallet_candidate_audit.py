"""Tests for the strict Tika/MALLET Harbor candidate auditor."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType


REPO = Path(__file__).resolve().parents[1]
SCRIPT = (
    REPO
    / "evaluations"
    / "semantic-okf-tika-mallet"
    / "scripts"
    / "audit_harbor_candidate.py"
)


def load_module() -> ModuleType:
    """Load the standalone auditor."""

    specification = importlib.util.spec_from_file_location(
        "semantic_okf_tika_mallet_candidate_audit", SCRIPT
    )
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


AUDIT = load_module()


def row(question_id: str, cohort: str, evaluable: bool = True) -> dict[str, object]:
    """Build one minimal matrix row."""

    return {
        "question_id": question_id,
        "cohort": cohort,
        "evaluable": evaluable,
    }


def test_matrix_status_requires_every_cell_exactly_once_and_evaluable() -> None:
    expected = {"q001": "discovery", "q002": "holdout"}

    complete, reasons = AUDIT.matrix_status(
        expected,
        [row("q001", "discovery"), row("q002", "holdout")],
    )

    assert complete is True
    assert reasons == []

    invalid, invalid_reasons = AUDIT.matrix_status(
        expected,
        [
            row("q001", "holdout"),
            row("q001", "discovery"),
            row("q002", "holdout", evaluable=False),
            row("q999", "hard"),
        ],
    )
    assert invalid is False
    assert invalid_reasons == [
        "cohort-drift:q001",
        "cohort-drift:q999",
        "duplicate:q001",
        "not-evaluable:q002",
        "unexpected:q999",
    ]


def test_markdown_exposes_rankability_and_nonsemantic_boundary() -> None:
    metric_names = (
        "reward",
        "mechanical_qualification_gate",
        "evidence_recall",
        "evidence_precision",
        "mrr",
        "ndcg",
    )
    aggregate = {
        "evaluable_trials": 1,
        "metrics": {name: {"mean": 0.75, "observed": 1} for name in metric_names},
    }
    report = {
        "status": "pass",
        "ranking_eligible": True,
        "evaluable_trials": 40,
        "expected_trials": 40,
        "dataset_id": "graphrag-papers-40",
        "candidate_id": "tika-mallet",
        "cohort_order": ["discovery"],
        "cohorts": {"discovery": aggregate},
        "overall": aggregate,
    }

    rendered = AUDIT.markdown(report)

    assert "Ranking eligible: `true`" in rendered
    assert "40/40" in rendered
    assert "manual-review-required" in rendered
