from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
BUILD = (
    REPO_ROOT
    / "skills"
    / "build-semantic-okf-tantivy"
    / "scripts"
    / "build_semantic_okf_tantivy.py"
)
SKILL_ROOT = REPO_ROOT / "skills" / "consult-semantic-okf-tantivy"
QUERY = SKILL_ROOT / "scripts" / "query_semantic_okf_tantivy.py"


def write_json(path: Path, value: Any) -> None:
    """Write stable human-readable JSON for the fixture inputs."""

    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def tree_hashes(root: Path) -> dict[str, str]:
    """Return path-to-digest mappings for read-only assertions."""

    return {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def write_fixture(root: Path) -> tuple[Path, Path]:
    """Create a minimal reviewed corpus and classical plan."""

    sources = root / "sources"
    sources.mkdir(parents=True)
    documents = {
        "alpha": (
            "Alpha Graph Note",
            "Graph retrieval connects entities, relations, paths, and grounded evidence. "
            "Community summaries preserve global themes and source passages preserve citations.",
        ),
        "beta": (
            "Beta Lexical Note",
            "Lexical ranking finds terminology. Topic analysis expands related queries and "
            "association statistics connect recurring concepts for diversified retrieval.",
        ),
    }
    for source_id, (title, body) in documents.items():
        (sources / f"{source_id}.md").write_text(
            f"---\ntitle: {title}\ncode: {source_id.upper()}-1\n---\n\n"
            f"# {title}\n\n{body}\n",
            encoding="utf-8",
        )
    manifest = {
        "schema_version": "1.0",
        "bundle": {
            "title": "Consult Tantivy fixture",
            "description": "Two authorities for native Tantivy BM25 tests.",
            "base_iri": "https://example.org/consult-tantivy/",
            "ontology_iri": "https://example.org/ontology/consult-tantivy",
            "version_iri": "https://example.org/ontology/consult-tantivy/1.0.0",
            "prefix": "fixture",
            "owl_profile": "rl",
        },
        "ontology": {
            "classes": [{"name": "Document", "label": "document"}],
            "properties": [
                {
                    "name": "code",
                    "kind": "datatype",
                    "domain": "Document",
                    "range": "xsd:string",
                }
            ],
        },
        "rules": [
            {
                "name": "DocumentCodeRule",
                "target_class": "Document",
                "path": "code",
                "min_count": 1,
                "datatype": "xsd:string",
                "message": "Every document requires a code.",
                "basis": {"kind": "operational-policy", "references": ["TEST-1"]},
            }
        ],
        "sources": [
            {
                "id": source_id,
                "kind": "markdown",
                "path": f"sources/{source_id}.md",
                "concept_type": "Document",
                "ontology_class": "Document",
                "fields": {"code": "code"},
            }
            for source_id in sorted(documents)
        ],
    }
    plan = {
        "schema_version": "1.0",
        "selection": {"source_ids": ["alpha", "beta"]},
        "tokenization": {
            "tokenizer": "ascii-alphanumeric-v1",
            "stopwords": "english-v1",
            "min_token_length": 2,
            "ngram_range": [1, 2],
        },
        "bm25": {
            "k1": 1.2,
            "b": 0.75,
            "title_weight": 2.0,
            "body_weight": 1.0,
        },
        "associations": {
            "window_size": 4,
            "min_document_frequency": 1,
            "min_cooccurrence": 1,
            "max_vocabulary": 32,
            "max_neighbors": 6,
            "minimum_ppmi": 0.0,
        },
        "topics": {"topic_count": 3, "max_iterations": 10, "top_terms": 5},
        "expansion": {
            "association_terms": 4,
            "topic_terms": 4,
            "association_weight": 0.5,
            "topic_weight": 0.25,
        },
        "reranking": {
            "candidate_pool": 20,
            "relevance_weight": 0.7,
            "topic_novelty_weight": 0.2,
            "source_novelty_weight": 0.1,
            "max_per_evidence_identity": 1,
            "rrf_k": 60,
        },
    }
    manifest_path = root / "manifest.json"
    plan_path = root / "classical-plan.json"
    write_json(manifest_path, manifest)
    write_json(plan_path, plan)
    return manifest_path, plan_path


@pytest.fixture(scope="module")
def bundle(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Build one deterministic dedicated bundle for Tantivy consultation."""

    pytest.importorskip("tantivy")
    root = tmp_path_factory.mktemp("consult-tantivy")
    manifest, plan = write_fixture(root)
    output = root / "bundle"
    environment = os.environ.copy()
    environment.pop("PYTHONPATH", None)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    completed = subprocess.run(
        [
            sys.executable,
            str(BUILD),
            str(manifest),
            str(plan),
            str(output),
            "--output-format",
            "json",
        ],
        cwd=root,
        env=environment,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=90,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    return output


def run_query(
    skill: Path,
    bundle_path: Path,
    *args: str,
) -> subprocess.CompletedProcess[str]:
    """Run the copied-package entry point without repository import paths."""

    environment = os.environ.copy()
    environment.pop("PYTHONPATH", None)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run(
        [
            sys.executable,
            str(skill / "scripts" / "query_semantic_okf_tantivy.py"),
            str(bundle_path),
            *args,
        ],
        cwd=skill,
        env=environment,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=60,
        check=False,
    )


def test_skill_metadata_dependency_and_implementation_are_standalone() -> None:
    """Keep the new package explicit, pinned, and free of sibling imports."""

    skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
    metadata = yaml.safe_load(skill.split("---", 2)[1])
    source = (SKILL_ROOT / "scripts" / "_tantivy_snapshot.py").read_text(
        encoding="utf-8"
    )

    assert set(metadata) == {"name", "description"}
    assert metadata["name"] == "consult-semantic-okf-tantivy"
    assert "## Standalone and read-only boundary" in skill
    assert "## Reference routing" in skill
    assert "## Required references" not in skill
    assert "load neither reference" in skill
    assert "in memory" in skill
    assert "$consult-semantic-okf-tantivy" in (
        SKILL_ROOT / "agents" / "openai.yaml"
    ).read_text(encoding="utf-8")
    assert (SKILL_ROOT / "scripts" / "requirements.in").read_text(
        encoding="utf-8"
    ).strip() == "tantivy==0.26.0"
    assert "tantivy.Index(schema)" in source
    assert "field_boosts=" in source
    assert "_bm25_scores" not in source
    assert "_classical_snapshot" not in source
    assert "TODO" not in skill


def test_runtime_and_copied_inspection_are_read_only(
    bundle: Path, tmp_path: Path
) -> None:
    """Exercise the native runtime from a package copied outside the repository."""

    copied = tmp_path / SKILL_ROOT.name
    shutil.copytree(
        SKILL_ROOT,
        copied,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
    )
    runtime = subprocess.run(
        [sys.executable, str(copied / "scripts" / "runtime_smoke.py")],
        cwd=copied,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=30,
        check=False,
    )
    before = tree_hashes(bundle)
    inspected = run_query(copied, bundle, "inspect")
    after = tree_hashes(bundle)

    assert runtime.returncode == 0, runtime.stdout + runtime.stderr
    runtime_payload = json.loads(runtime.stdout)
    assert runtime_payload["package_version"] == "0.26.0"
    assert runtime_payload["implementation"] == "Rust"
    assert runtime_payload["scoring"] == "BM25"
    assert inspected.returncode == 0, inspected.stdout + inspected.stderr
    payload = json.loads(inspected.stdout)
    assert payload["status"] == "pass"
    assert payload["capabilities"] == ["tantivy-bm25"]
    assert payload["engine"]["index_storage"] == "memory"
    assert payload["validation"] == {"locator_bindings": True, "structural": True}
    assert before == after


def test_tantivy_bm25_returns_exact_authoritative_evidence(bundle: Path) -> None:
    """Rank through Tantivy while retaining exact ledger-bound text."""

    before = tree_hashes(bundle)
    completed = run_query(
        SKILL_ROOT,
        bundle,
        "search",
        "--query",
        '"graph retrieval" OR relations',
        "--top-k",
        "5",
    )
    after = tree_hashes(bundle)

    assert completed.returncode == 0, completed.stdout + completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["requested_mode"] == payload["effective_mode"] == "tantivy-bm25"
    assert payload["engine"]["id"] == (
        "tantivy-0.26.0-native-bm25-diversified-v2"
    )
    assert payload["engine"]["implementation"] == "Rust"
    assert payload["engine"]["indexed_documents"] == 2
    assert payload["engine"]["candidate_pool"] == 2
    assert payload["engine"]["identity_cap"] == 1
    assert payload["engine"]["identity_policy"] == "paper_id-or-source_id"
    assert payload["engine"]["ranking"] == (
        "native-score-order-with-identity-cap-v1"
    )
    assert payload["engine"]["query_normalization"] == "preserved-syntax"
    assert payload["parsed_query"] == '"graph retrieval" OR relations'
    assert payload["results"]
    assert payload["results"][0]["source_id"] == "alpha"
    assert payload["engine"]["returned_identities"] == len(payload["results"])
    records = {
        (record["source_id"], record["record_id"]): record
        for record in (
            json.loads(line)
            for line in (bundle / "semantic" / "records.jsonl")
            .read_text(encoding="utf-8")
            .splitlines()
        )
    }
    for hit in payload["results"]:
        record = records[(hit["source_id"], hit["record_id"])]
        if hit["locator"] == {"kind": "record"}:
            resolved = record["body"]
        else:
            resolved = record["body"][hit["locator"]["start"] : hit["locator"]["end"]]
        assert hit["text"] == resolved
        assert hit["text_sha256"] == hashlib.sha256(resolved.encode()).hexdigest()
        assert (bundle / hit["concept_path"]).is_file()
        assert hit["score"] > 0
    assert before == after


def test_natural_query_is_normalized_against_the_snapshot_lexicon(
    bundle: Path,
) -> None:
    """Bound natural-query terms to the persisted lexicon."""

    completed = run_query(
        SKILL_ROOT,
        bundle,
        "search",
        "--query",
        "What does graph retrieval connect across this corpus?",
        "--top-k",
        "2",
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["query"] == "What does graph retrieval connect across this corpus?"
    assert payload["parsed_query"] == "graph retrieval connect"
    assert payload["engine"]["query_normalization"] == (
        "classical-unigram-lexicon-v1"
    )
    assert payload["result_count"] == 2
    assert len({hit["source_id"] for hit in payload["results"]}) == 2


def test_filters_are_applied_before_tantivy_indexing(bundle: Path) -> None:
    """Expose the filtered index size and never rank excluded passages."""

    completed = run_query(
        SKILL_ROOT,
        bundle,
        "search",
        "--query",
        "retrieval topics",
        "--top-k",
        "10",
        "--source-id",
        "beta",
        "--concept-type",
        "Document",
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["filters"] == {
        "source_ids": ["beta"],
        "concept_ids": [],
        "concept_types": ["Document"],
    }
    assert payload["engine"]["indexed_documents"] == 1
    assert payload["results"]
    assert {hit["source_id"] for hit in payload["results"]} == {"beta"}


def test_invalid_queries_and_tampered_artifacts_fail_closed(
    bundle: Path, tmp_path: Path
) -> None:
    """Return stable diagnostics instead of scanning corrupt inputs."""

    empty = run_query(SKILL_ROOT, bundle, "search", "--query", "   ")
    invalid = run_query(SKILL_ROOT, bundle, "search", "--query", "(")
    altered = tmp_path / "altered"
    shutil.copytree(bundle, altered)
    documents = altered / "classical" / "documents.jsonl"
    documents.write_bytes(documents.read_bytes() + b"\n")
    corrupt = run_query(SKILL_ROOT, altered, "inspect")

    assert empty.returncode == 2
    assert "query must be nonempty" in json.loads(empty.stdout)["error"]
    assert invalid.returncode == 2
    assert "invalid Tantivy query" in json.loads(invalid.stdout)["error"]
    assert corrupt.returncode == 2
    assert "is blank" in json.loads(corrupt.stdout)["error"]
