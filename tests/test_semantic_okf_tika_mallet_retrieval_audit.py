"""Tests for replicated canonical Tika/MALLET retrieval auditing."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from types import ModuleType

import pytest


REPO = Path(__file__).resolve().parents[1]
SCRIPT = (
    REPO
    / "evaluations"
    / "semantic-okf-tika-mallet"
    / "scripts"
    / "audit_canonical_retrieval.py"
)


def load_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("tika_mallet_retrieval_audit", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def fake_report(top_k: int) -> dict[str, object]:
    routes = []
    for route_name in (
        "tika_mallet_bm25",
        "tika_mallet_topic",
        "tika_mallet_association",
        "tika_mallet_fusion",
    ):
        queries = []
        for index in range(40):
            hits = [
                {
                    "paper_id": f"paper-{rank:03d}",
                    "rank": rank,
                    "score": float(101 - rank),
                }
                for rank in range(1, min(top_k, 12) + 1)
            ]
            queries.append(
                {
                    "question_id": f"q{index + 1:03d}",
                    "elapsed_ms": 1.0,
                    "hits": hits,
                    "paper_ids": [row["paper_id"] for row in hits],
                    "source_ids": [f"source-{row['paper_id']}" for row in hits],
                }
            )
        routes.append(
            {
                "name": route_name,
                "query_count": 40,
                "error_count": 0,
                "errors": [],
                "evidence_validity": {"ratio": 1.0},
                "paper_metrics": {"recall_at_10": 0.5},
                "source_metrics": {"recall_at_10": 0.5},
                "cohorts": {"hard_10": {"paper_metrics": {"recall_at_10": 0.4}}},
                "queries": queries,
            }
        )
    return {
        "schema_version": "semantic-okf-tika-mallet-canonical-retrieval/1.0",
        "status": "pass",
        "ranking_eligible": True,
        "query_count": 40,
        "top_k": top_k,
        "selected_route": "tika_mallet_fusion",
        "bundle": {
            "inventory_sha256": "a" * 64,
            "records": {"sha256": "b" * 64},
        },
        "selected_metrics": {
            "all_40": {
                "recall_at_10": 0.5,
                "mrr_at_10": 0.6,
                "ndcg_at_10": 0.55,
            },
            "hard_10": {"recall_at_10": 0.4},
            "evidence_validity": {"ratio": 1.0},
            "timing_ms": {"mean": 2.0, "p95": 3.0},
        },
        "routes": routes,
    }


def write(path: Path, value: object) -> None:
    path.write_text(json.dumps(value), encoding="utf-8")


def test_retrieval_audit_accepts_exact_replicates_and_prefixes(
    tmp_path: Path,
) -> None:
    module = load_module()
    paths = {
        "attempt_10_top10": tmp_path / "a10.json",
        "attempt_11_top10": tmp_path / "a11.json",
        "attempt_10_pool100": tmp_path / "p10.json",
        "attempt_11_pool100": tmp_path / "p11.json",
    }
    for name, path in paths.items():
        write(path, fake_report(10 if "top10" in name else 100))

    report = module.audit(**paths)

    assert report["status"] == "pass"
    assert report["ranking_eligible"] is True
    assert all(report["parity"].values())
    assert report["selected_metrics"]["recall_at_10"] == 0.5
    assert "Top-10/pool-100 prefix parity" in module.render_markdown(report)


def test_retrieval_audit_rejects_pool_prefix_drift(tmp_path: Path) -> None:
    module = load_module()
    top = fake_report(10)
    pool = fake_report(100)
    pool["routes"][0]["queries"][0]["hits"][0]["paper_id"] = "drift"
    paths = {
        "attempt_10_top10": tmp_path / "a10.json",
        "attempt_11_top10": tmp_path / "a11.json",
        "attempt_10_pool100": tmp_path / "p10.json",
        "attempt_11_pool100": tmp_path / "p11.json",
    }
    write(paths["attempt_10_top10"], top)
    write(paths["attempt_11_top10"], top)
    write(paths["attempt_10_pool100"], pool)
    write(paths["attempt_11_pool100"], pool)

    with pytest.raises(module.AuditError, match="hits prefix drifted"):
        module.audit(**paths)
