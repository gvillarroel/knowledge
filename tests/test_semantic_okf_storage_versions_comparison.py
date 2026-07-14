from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = (
    REPO_ROOT
    / "evaluations"
    / "semantic-okf-storage-versions"
    / "scripts"
    / "compare_operational.py"
)


def load_comparator() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "semantic_okf_storage_comparator", SCRIPT_PATH
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def comparator() -> ModuleType:
    return load_comparator()


def test_percentile_interpolates_small_samples(comparator: ModuleType) -> None:
    assert comparator.percentile([10.0, 20.0, 30.0], 0.5) == 20.0
    assert comparator.percentile([10.0, 20.0], 0.95) == pytest.approx(19.5)


def test_tree_digest_uses_logical_database_identity(
    comparator: ModuleType, tmp_path: Path
) -> None:
    bundle = tmp_path / "bundle"
    database = bundle / "semantic" / "knowledge.db"
    database.parent.mkdir(parents=True)
    (bundle / "index.md").write_text("# Index\n", encoding="utf-8")
    database.write_bytes(b"first physical layout")
    first = comparator.tree_fingerprint(
        bundle,
        exclude_database=True,
        database_logical_sha256="a" * 64,
    )
    database.write_bytes(b"a different and larger physical page layout")
    second = comparator.tree_fingerprint(
        bundle,
        exclude_database=True,
        database_logical_sha256="a" * 64,
    )
    assert first["logical_tree_sha256"] == second["logical_tree_sha256"]
    assert first["total_bytes"] != second["total_bytes"]


def test_published_database_sidecars_are_rejected(
    comparator: ModuleType, tmp_path: Path
) -> None:
    bundle = tmp_path / "bundle"
    semantic = bundle / "semantic"
    semantic.mkdir(parents=True)
    (semantic / "knowledge.db").write_bytes(b"database")
    (semantic / "knowledge.db-wal").write_bytes(b"active")
    with pytest.raises(comparator.ComparisonError, match="sidecar"):
        comparator.ordinary_tree_entries(bundle)


def test_source_fingerprint_excludes_python_caches(
    comparator: ModuleType, tmp_path: Path
) -> None:
    package = tmp_path / "skill"
    cache = package / "scripts" / "__pycache__"
    cache.mkdir(parents=True)
    (package / "SKILL.md").write_text("# Skill\n", encoding="utf-8")
    bytecode = cache / "helper.cpython-312.pyc"
    bytecode.write_bytes(b"first")
    first = comparator.source_tree_fingerprint(package)
    bytecode.write_bytes(b"different")
    second = comparator.source_tree_fingerprint(package)
    assert first == second
    assert first["file_count"] == 1


def test_aggregate_normalization_matches_storage_surfaces(
    comparator: ModuleType,
) -> None:
    records = [
        {
            "ontology_class_iri": "https://example.org/ontology#Paper",
            "concept_type": "Research Paper",
        }
    ]
    sparql = {
        "rows": [
            {
                "source_id": {"value": "papers"},
                "concept_type": {"value": "https://example.org/ontology#Paper"},
                "record_count": {"value": "2"},
            }
        ]
    }
    sql = {
        "rows": [
            {
                "source_id": "papers",
                "concept_type": "Research Paper",
                "record_count": 2,
            }
        ]
    }
    expected = [("papers", "Research Paper", 2)]
    assert comparator.normalize_legacy_aggregates(sparql, records) == expected
    assert comparator.normalize_turso_aggregates(sql) == expected


def test_markdown_report_keeps_performance_caveats(comparator: ModuleType) -> None:
    route = {
        "recall_at_10": 0.5,
        "mrr_at_10": 0.6,
        "ndcg_at_10": 0.4,
        "evidence_validity": 1.0,
        "mean_ms": 10.0,
    }
    report = {
        "status": "pass",
        "corpus": {"records": 10, "sources": 2},
        "versions": {
            "file-backed": {
                "bundle": {"file_count": 10, "total_bytes": 100},
                "build_ms": {"mean": 100.0},
                "deterministic_rebuild": True,
                "core_semantic_parity": "baseline",
            },
            "embedding-backed": {
                "bundle": {"file_count": 14, "total_bytes": 200},
                "build_ms": {"mean": 1000.0},
                "deterministic_rebuild": True,
                "core_semantic_parity": "pass",
                "routes": {
                    name: route
                    for name in ("legacy_lexical", "new_lexical", "vector", "hybrid")
                },
                "timing_warning": "Execution scopes differ.",
            },
            "turso-backed": {
                "bundle": {"file_count": 11, "total_bytes": 500},
                "build_ms": {"mean": 120.0},
                "deterministic_rebuild": True,
                "core_semantic_parity": "pass",
                "database_logical_sha256": "b" * 64,
            },
        },
        "operational_queries": {
            "exact_record": {
                "file-backed": {"median_ms": 10.0},
                "turso-backed": {"median_ms": 15.0},
                "result_parity": True,
            },
            "aggregate": {
                "file-backed": {"median_ms": 20.0},
                "turso-backed": {"median_ms": 15.0},
                "result_parity": True,
            },
        },
        "parity": {
            "records": True,
            "authoritative_core": True,
            "queries": True,
            "read_only": True,
        },
    }
    markdown = comparator.render_markdown(report)
    assert "single exact lookup was 50.0% slower" in markdown
    assert "grouped aggregation was 25.0% faster" in markdown
    assert "after quality tuning" in markdown
    assert "not an in-process engine microbenchmark" in markdown
