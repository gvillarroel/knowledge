from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
BUILD_ROOT = REPO_ROOT / "skills" / "build-semantic-okf-classical"
BUILD = BUILD_ROOT / "scripts" / "build_semantic_okf_classical.py"
SKILL_ROOT = REPO_ROOT / "skills" / "consult-semantic-okf-classical"
SCRIPTS = SKILL_ROOT / "scripts"
QUERY = SCRIPTS / "query_semantic_okf_classical.py"


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tree_hashes(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): file_sha256(path)
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def write_fixture(root: Path) -> tuple[Path, Path]:
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
            f"---\ntitle: {title}\ncode: {source_id.upper()}-1\n---\n\n# {title}\n\n{body}\n",
            encoding="utf-8",
        )
    manifest = {
        "schema_version": "1.0",
        "bundle": {
            "title": "Consult classical fixture",
            "description": "Two authorities for read-only classical retrieval tests.",
            "base_iri": "https://example.org/consult-classical/",
            "ontology_iri": "https://example.org/ontology/consult-classical",
            "version_iri": "https://example.org/ontology/consult-classical/1.0.0",
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
        "bm25": {"k1": 1.2, "b": 0.75, "title_weight": 2.0, "body_weight": 1.0},
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
    root = tmp_path_factory.mktemp("consult-classical")
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


def run_query(bundle_path: Path, *args: str) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment.pop("PYTHONPATH", None)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run(
        [sys.executable, str(QUERY), str(bundle_path), *args],
        cwd=SKILL_ROOT,
        env=environment,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=60,
        check=False,
    )


def load_snapshot_module() -> ModuleType:
    name = "test_classical_snapshot"
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / "_classical_snapshot.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def test_skill_metadata_documents_and_runtime_are_standalone() -> None:
    skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
    metadata = yaml.safe_load(skill.split("---", 2)[1])

    assert set(metadata) == {"name", "description"}
    assert metadata["name"] == "consult-semantic-okf-classical"
    assert "## Standalone and read-only boundary" in skill
    assert "--deep-validation" in skill
    assert "$consult-semantic-okf-classical" in (
        SKILL_ROOT / "agents" / "openai.yaml"
    ).read_text(encoding="utf-8")
    assert (SCRIPTS / "requirements.txt").read_text(encoding="utf-8").strip() == (
        "# No third-party packages are required."
    )
    source = (SCRIPTS / "_classical_snapshot.py").read_text(encoding="utf-8")
    assert "_classical_retrieval" not in source
    assert "sentence_transformers" not in source
    assert "openai" not in source.casefold()


def test_deep_inspection_independently_rederives_every_artifact(bundle: Path) -> None:
    before = tree_hashes(bundle)
    completed = run_query(bundle, "inspect", "--deep-validation")
    after = tree_hashes(bundle)

    assert completed.returncode == 0, completed.stdout + completed.stderr
    result = json.loads(completed.stdout)
    assert result["status"] == "pass"
    assert result["authoritative"] is False
    assert result["discovery_only"] is True
    assert result["validation"] == {
        "structural": True,
        "independent_rederivation": True,
    }
    assert result["capabilities"] == ["bm25", "topic", "association", "fusion"]
    assert before == after


@pytest.mark.parametrize("mode", ["bm25", "topic", "association", "fusion"])
def test_all_modes_return_exact_read_only_evidence(bundle: Path, mode: str) -> None:
    before = tree_hashes(bundle)
    completed = run_query(
        bundle,
        "search",
        "--query",
        "graph relations evidence retrieval",
        "--mode",
        mode,
        "--top-k",
        "5",
    )
    after = tree_hashes(bundle)

    assert completed.returncode == 0, completed.stdout + completed.stderr
    result = json.loads(completed.stdout)
    assert result["requested_mode"] == result["effective_mode"] == mode
    assert result["authoritative"] is False
    assert result["discovery_only"] is True
    assert result["snapshot"]["deep_validation"] is False
    assert set(result["expansion"]) == {"association_terms", "topic_terms", "query_topics"}
    assert result["results"]
    records = {
        (row["source_id"], row["record_id"]): row
        for row in (
            json.loads(line)
            for line in (bundle / "semantic" / "records.jsonl").read_text(encoding="utf-8").splitlines()
        )
    }
    for hit in result["results"]:
        record = records[(hit["source_id"], hit["record_id"])]
        if hit["locator"] == {"kind": "record"}:
            resolved = record["body"]
        else:
            resolved = record["body"][hit["locator"]["start"] : hit["locator"]["end"]]
        assert hit["text"] == resolved
        assert hit["text_sha256"] == hashlib.sha256(resolved.encode("utf-8")).hexdigest()
        assert (bundle / hit["concept_path"]).is_file()
    if mode != "bm25":
        identities = [hit["paper_id"] or hit["source_id"] for hit in result["results"]]
        assert len(identities) == len(set(identities))
    assert before == after


def test_filters_are_applied_before_ranking(bundle: Path) -> None:
    completed = run_query(
        bundle,
        "search",
        "--query",
        "retrieval topics",
        "--mode",
        "fusion",
        "--top-k",
        "10",
        "--source-id",
        "beta",
        "--concept-type",
        "Document",
    )

    assert completed.returncode == 0
    result = json.loads(completed.stdout)
    assert result["filters"] == {
        "source_ids": ["beta"],
        "concept_ids": [],
        "concept_types": ["Document"],
    }
    assert result["results"]
    assert {hit["source_id"] for hit in result["results"]} == {"beta"}


def update_tampered_hash_bindings(bundle_path: Path) -> None:
    classical = bundle_path / "classical"
    index_path = classical / "index.json"
    report_path = classical / "build-report.json"
    association_path = classical / "associations.jsonl"
    index = json.loads(index_path.read_text(encoding="utf-8"))
    association_artifact = {
        "path": "classical/associations.jsonl",
        "bytes": association_path.stat().st_size,
        "sha256": file_sha256(association_path),
        "count": len(association_path.read_text(encoding="utf-8").splitlines()),
    }
    index["artifacts"]["associations"] = association_artifact
    write_json(index_path, index)
    report = json.loads(report_path.read_text(encoding="utf-8"))
    report["artifacts"]["associations"] = association_artifact
    report["artifacts"]["index"] = {
        "path": "classical/index.json",
        "bytes": index_path.stat().st_size,
        "sha256": file_sha256(index_path),
    }
    write_json(report_path, report)


def test_deep_validation_rejects_hash_consistent_ppmi_tampering(
    bundle: Path, tmp_path: Path
) -> None:
    altered = tmp_path / "altered"
    shutil.copytree(bundle, altered)
    association_path = altered / "classical" / "associations.jsonl"
    rows = [json.loads(line) for line in association_path.read_text(encoding="utf-8").splitlines()]
    target = next(row for row in rows if row["neighbors"])
    target["neighbors"][0]["ppmi"] = round(target["neighbors"][0]["ppmi"] + 0.00000001, 8)
    association_path.write_text(
        "".join(canonical_json(row) + "\n" for row in rows), encoding="utf-8"
    )
    update_tampered_hash_bindings(altered)
    module = load_snapshot_module()

    ordinary = module.load_snapshot(altered)
    assert ordinary.deep_validation is False
    with pytest.raises(module.SnapshotError, match="independent deterministic PPMI derivation"):
        module.load_snapshot(altered, deep_validation=True)


def test_closed_artifact_set_and_invalid_query_fail_cleanly(bundle: Path, tmp_path: Path) -> None:
    altered = tmp_path / "unknown-file"
    shutil.copytree(bundle, altered)
    (altered / "classical" / "cache.json").write_text("{}\n", encoding="utf-8")
    closed = run_query(altered, "inspect")
    empty = run_query(bundle, "search", "--query", "   ", "--mode", "bm25")

    assert closed.returncode == 2
    assert "artifact set is closed" in json.loads(closed.stdout)["error"]
    assert empty.returncode == 2
    assert "query must be nonempty" in json.loads(empty.stdout)["error"]
