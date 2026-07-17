from __future__ import annotations

import importlib.util
import hashlib
import json
from pathlib import Path
from types import ModuleType

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    REPO_ROOT
    / "evaluations"
    / "semantic-okf-storage-versions"
    / "scripts"
    / "compare_graphify.py"
)


@pytest.fixture(scope="module")
def comparator() -> ModuleType:
    spec = importlib.util.spec_from_file_location("graphify_storage_compare", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_ranking_metrics_use_binary_qrels_and_first_rank(comparator: ModuleType) -> None:
    ranked = ["a", "x", "b", "a"]
    relevant = {"a", "b", "c"}
    assert comparator.deduplicate(ranked) == ["a", "x", "b"]
    assert comparator.recall_at_k(ranked, relevant) == pytest.approx(2 / 3)
    assert comparator.mrr_at_k(ranked, relevant) == 1.0
    assert comparator.ndcg_at_k(ranked, relevant) > 0.0


def test_core_fingerprint_excludes_only_graphify_projection(
    comparator: ModuleType, tmp_path: Path
) -> None:
    (tmp_path / "semantic").mkdir()
    (tmp_path / "semantic" / "records.jsonl").write_text("{}\n", encoding="utf-8")
    graphify = tmp_path / "retrieval" / "graphify"
    graphify.mkdir(parents=True)
    (graphify / "graph.json").write_text("{}\n", encoding="utf-8")
    core_before = comparator.tree_fingerprint(tmp_path, exclude_graphify=True)
    full_before = comparator.tree_fingerprint(tmp_path)
    (graphify / "graph.json").write_text('{"changed":true}\n', encoding="utf-8")
    assert comparator.tree_fingerprint(tmp_path, exclude_graphify=True) == core_before
    assert comparator.tree_fingerprint(tmp_path) != full_before


def test_prior_report_digest_is_frozen(comparator: ModuleType) -> None:
    prior = (
        REPO_ROOT
        / "evaluations"
        / "semantic-okf-storage-versions"
        / "operational-report.json"
    )
    assert hashlib.sha256(prior.read_bytes()).hexdigest() == (
        comparator.EXPECTED_PRIOR_REPORT_SHA256
    )


def test_hit_evidence_requires_full_ledger_and_exact_concept_binding(
    comparator: ModuleType, tmp_path: Path
) -> None:
    record = {
        "attributes": {"paper_id": "2401.12345v1"},
        "body": "# Evidence\n\nReviewed statement.",
        "concept_id": "concepts/papers/paper-1",
        "concept_path": "concepts/papers/paper-1.md",
        "concept_type": "Paper",
        "ontology_class_iri": "https://example.org/Paper",
        "record_id": "paper-1",
        "source_id": "papers",
        "source_kind": "json",
        "source_path": "sources/papers.jsonl",
        "subject_iri": "https://example.org/paper-1",
        "title": "Evidence",
    }
    record["record_sha256"] = comparator.record_digest(record)
    concept = tmp_path / record["concept_path"]
    concept.parent.mkdir(parents=True)
    content = f"---\ntitle: Evidence\n---\n\n{record['body']}\n"
    concept.write_text(content, encoding="utf-8", newline="\n")
    concept_sha256 = hashlib.sha256(concept.read_bytes()).hexdigest()
    hit = {
        "attributes": record["attributes"],
        "concept_id": record["concept_id"],
        "concept_path": record["concept_path"],
        "concept_sha256": concept_sha256,
        "concept_type": record["concept_type"],
        "content": content,
        "evidence": {
            "kind": "concept-file",
            "path": record["concept_path"],
            "sha256": concept_sha256,
        },
        "paper_id": "2401.12345v1",
        "record_id": record["record_id"],
        "record_sha256": record["record_sha256"],
        "source_id": record["source_id"],
        "source_path": record["source_path"],
        "title": record["title"],
    }
    valid, paper_id, issues = comparator.validate_hit_evidence(
        tmp_path,
        hit,
        {(record["source_id"], record["record_id"]): record},
        {record["subject_iri"]: record},
    )
    assert valid is True
    assert paper_id == "2401.12345v1"
    assert issues == []

    hit["source_path"] = "forged/source.jsonl"
    valid, _, issues = comparator.validate_hit_evidence(
        tmp_path,
        hit,
        {(record["source_id"], record["record_id"]): record},
        {record["subject_iri"]: record},
    )
    assert valid is False
    assert "source_path does not match the authoritative ledger" in issues


def test_markdown_combines_all_four_versions_and_caveats(comparator: ModuleType) -> None:
    prior = json.loads(
        (
            REPO_ROOT
            / "evaluations"
            / "semantic-okf-storage-versions"
            / "operational-report.json"
        ).read_text(encoding="utf-8")
    )
    versions = dict(prior["versions"])
    versions["graphify-backed"] = {
        "build_ms": {"mean_ms": 42.0},
        "bundle": {"file_count": 886, "total_bytes": 12000000},
        "core_semantic_parity": "pass",
        "deterministic_rebuild": True,
        "projection": {
            "edges": 20,
            "logical_sha256": "a" * 64,
            "nodes": 10,
            "orphans": 0,
        },
    }
    route = {
        "evidence_validity": 1.0,
        "mean_ms": 100.0,
        "mrr_at_10": 0.5,
        "ndcg_at_10": 0.4,
        "recall_at_10": 0.3,
    }
    retrieval = dict(prior["versions"]["embedding-backed"]["routes"])
    retrieval["graphify_structural"] = route
    operations = json.loads(json.dumps(prior["operational_queries"]))
    operations["exact_record"]["graphify-backed"] = {"median_ms": 100.0}
    operations["aggregate"]["graphify-backed"] = {"median_ms": 110.0}
    report = {
        "corpus": {"questions": 30, "records": 874, "sources": 31},
        "operational_queries": operations,
        "parity": {"evidence": True, "queries": True, "read_only": True},
        "retrieval_routes": retrieval,
        "status": "pass",
        "versions": versions,
    }
    markdown = comparator.render_markdown(report)
    assert "graphify-backed" in markdown
    assert "graphify_structural" in markdown
    assert "Latency scopes differ" in markdown
    assert "Graphify did not become a factual authority" in markdown
