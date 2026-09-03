from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = (
    ROOT
    / "evaluations"
    / "tau3-banking-knowledge"
    / "tau3_banking_knowledge_eval.py"
)
SPEC = importlib.util.spec_from_file_location("tau3_banking_knowledge_eval", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_ranking_metrics_uses_binary_qrels_and_cutoff() -> None:
    metrics = MODULE.ranking_metrics(["other", "a", "b", "late"], ["a", "b"], 3)

    assert metrics["hit"] == 1.0
    assert metrics["recall"] == 1.0
    assert metrics["precision"] == pytest.approx(2 / 3)
    assert metrics["mrr"] == 0.5
    assert metrics["all_relevant"] == 1.0
    assert 0.0 < metrics["ndcg"] < 1.0


def test_ranking_metrics_rejects_empty_qrels() -> None:
    with pytest.raises(MODULE.EvaluationError, match="At least one relevant"):
        MODULE.ranking_metrics(["a"], [], 1)


def test_ranking_metrics_rejects_nonpositive_cutoff() -> None:
    with pytest.raises(MODULE.EvaluationError, match="positive integer"):
        MODULE.ranking_metrics(["a"], ["a"], 0)


def test_normalize_source_id_handles_upstream_punctuation() -> None:
    assert (
        MODULE.normalize_source_id("doc_bank_accounts_bank_accounts_(general)_001")
        == "doc-bank-accounts-bank-accounts-general-001"
    )


def test_tree_digest_is_path_sensitive_and_deterministic(tmp_path: Path) -> None:
    first = tmp_path / "first.txt"
    first.write_text("same", encoding="utf-8")
    digest_a = MODULE.tree_digest(tmp_path)
    digest_b = MODULE.tree_digest(tmp_path)
    first.rename(tmp_path / "second.txt")
    digest_c = MODULE.tree_digest(tmp_path)

    assert digest_a == digest_b
    assert digest_a[1] == 1
    assert digest_a[0] != digest_c[0]


def test_aggregate_rankings_averages_complete_cohort() -> None:
    tasks = [
        {"task_id": "one", "required_documents": ["a"]},
        {"task_id": "two", "required_documents": ["b"]},
    ]
    rankings = {"one": ["a"], "two": ["other"]}

    summary = MODULE.aggregate_rankings(rankings, tasks, [1])

    assert summary["1"]["hit"] == 0.5
    assert summary["1"]["recall"] == 0.5
    assert summary["1"]["all_relevant"] == 0.5
