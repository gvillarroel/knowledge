"""Tests for the canonical Tika/MALLET/Tantivy direct-retrieval audit."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
from types import ModuleType

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
EVALUATION_ROOT = (
    REPO_ROOT / "evaluations" / "semantic-okf-tika-mallet-tantivy"
)
EVALUATOR_PATH = EVALUATION_ROOT / "scripts" / "evaluate_canonical_retrieval.py"
AUDITOR_PATH = EVALUATION_ROOT / "scripts" / "audit_canonical_retrieval.py"
AUDIT_PATH = EVALUATION_ROOT / "reports" / "canonical-retrieval-20260727.json"


def load_module(name: str, path: Path) -> ModuleType:
    """Load one standalone evaluation module from its checked path."""

    specification = importlib.util.spec_from_file_location(name, path)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


def test_checked_audit_is_complete_replicated_and_ranking_eligible() -> None:
    """The published row is backed by all deterministic parity gates."""

    audit = json.loads(AUDIT_PATH.read_text(encoding="utf-8"))

    assert audit["schema_version"] == (
        "semantic-okf-tika-mallet-tantivy-retrieval-audit/1.0"
    )
    assert audit["status"] == "pass"
    assert audit["ranking_eligible"] is True
    assert audit["question_count"] == 40
    assert audit["selected_route"] == "tika_mallet_tantivy_fusion"
    assert all(audit["parity"].values())
    assert audit["bundle_inventory_sha256"] == (
        "bc7db567bb8dfbbe3f3e80c2279f002bdc1e1af57d143bfc1c70707ab029d993"
    )
    assert audit["records_sha256"] == (
        "faac75af34f1a3bd67c10354fbf217850cd1b4d0468a93b1a90416e236e9286c"
    )
    metrics = audit["selected_metrics"]
    assert metrics["recall_at_10"] == pytest.approx(0.735018037518038)
    assert metrics["mrr_at_10"] == pytest.approx(0.847916666666667)
    assert metrics["ndcg_at_10"] == pytest.approx(0.717506531876882)
    assert metrics["hard_recall_at_10"] == pytest.approx(0.738333333333333)
    assert metrics["hard_mrr_at_10"] == pytest.approx(0.541666666666667)
    assert metrics["hard_ndcg_at_10"] == pytest.approx(0.55040747716057)
    assert metrics["evidence_valid_rate"] == 1.0
    assert metrics["p95_latency_ms"] == pytest.approx(470.742695021909)
    assert set(audit["reports"]) == {
        "attempt_10_top10",
        "attempt_11_top10",
        "attempt_10_pool100",
        "attempt_11_pool100",
    }
    assert all(
        len(report["sha256"]) == 64 for report in audit["reports"].values()
    )


def test_canonical_tables_report_the_combined_route() -> None:
    """Both current-facing direct tables expose the audited combined result."""

    latest = (
        REPO_ROOT / "evaluations" / "LATEST-REPORT.md"
    ).read_text(encoding="utf-8")
    conclusions = (
        REPO_ROOT
        / "evaluations"
        / "semantic-okf-ensemble"
        / "EVALUATION-CONCLUSIONS.md"
    ).read_text(encoding="utf-8")

    assert (
        "| 21 | Tika/MALLET/Tantivy fusion | 93.06% | 61.30% | 66.38% | "
        "100.00% | 2883.27 ms |"
        in latest
    )
    assert (
        "| Tika + Java MALLET + Tantivy (experimental) | "
        "`tika_mallet_tantivy_fusion` | 73.50% | 84.79% | 71.75% | "
        "73.83% | 54.17% | 55.04% | 100.00% | 470.74 |"
        in conclusions
    )
    assert "| Tika/MALLET + Tantivy |" not in latest


def test_evaluator_sanitizes_natural_colon_text_before_tantivy() -> None:
    """A natural-language colon cannot become an unintended field selector."""

    evaluator = load_module(
        "semantic_okf_tika_mallet_tantivy_evaluator_test",
        EVALUATOR_PATH,
    )

    class Runtime:
        query: str | None = None

        @classmethod
        def search_snapshot(
            cls,
            _snapshot: object,
            query: str,
            _mode: str,
            _top_k: int,
        ) -> dict[str, object]:
            cls.query = query
            return {"results": []}

    assert evaluator._hits(Runtime, object(), "matrix in prose: which", "fusion", 10) == []
    assert Runtime.query == "matrix in prose which"
    assert evaluator.ROUTES == ("tantivy", "topic", "association", "fusion")


def test_auditor_rejects_pool_prefix_drift() -> None:
    """Pool-100 evidence must preserve every direct Top-10 prefix."""

    auditor = load_module(
        "semantic_okf_tika_mallet_tantivy_auditor_test",
        AUDITOR_PATH,
    )
    top = {
        "routes": [
            {
                "name": "route",
                "queries": [
                    {
                        "question_id": "q001",
                        "hits": ["a"],
                        "paper_ids": ["paper-a"],
                        "source_ids": ["source-a"],
                    }
                ],
            }
        ]
    }
    pool = {
        "routes": [
            {
                "name": "route",
                "queries": [
                    {
                        "question_id": "q001",
                        "hits": ["b", "a"],
                        "paper_ids": ["paper-b", "paper-a"],
                        "source_ids": ["source-b", "source-a"],
                    }
                ],
            }
        ]
    }

    with pytest.raises(auditor.AuditError, match="prefix drifted"):
        auditor.assert_prefix(top, pool, "synthetic")
