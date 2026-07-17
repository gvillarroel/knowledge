from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BUILD_SKILL = REPO_ROOT / "skills" / "build-semantic-okf-graphify"
CONSULT_SKILL = REPO_ROOT / "skills" / "consult-semantic-okf-graphify"


def write_fixture(root: Path) -> Path:
    sources = root / "sources"
    sources.mkdir(parents=True)
    (sources / "documents.jsonl").write_text(
        json.dumps(
            {
                "id": "doc-1",
                "title": "Alpha Document",
                "summary": "Local-first connected graph retrieval [Injected](../../escape.md)",
            },
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    manifest = {
        "schema_version": "1.0",
        "bundle": {
            "title": "Graphify semantic fixture",
            "description": "One deterministic document projected with Graphify.",
            "base_iri": "https://example.org/graphify-fixture/",
            "ontology_iri": "https://example.org/ontology/graphify-fixture",
            "version_iri": "https://example.org/ontology/graphify-fixture/1.0.0",
            "prefix": "fixture",
            "owl_profile": "rl",
        },
        "ontology": {
            "classes": [{"name": "Document", "label": "document"}],
            "properties": [
                {
                    "name": "summary",
                    "kind": "datatype",
                    "domain": "Document",
                    "range": "xsd:string",
                }
            ],
        },
        "rules": [
            {
                "name": "DocumentSummaryRule",
                "target_class": "Document",
                "path": "summary",
                "min_count": 1,
                "max_count": 1,
                "datatype": "xsd:string",
                "message": "Each document requires one reviewed summary.",
                "basis": {"kind": "operational-policy", "references": ["GRAPHIFY-1"]},
            }
        ],
        "sources": [
            {
                "id": "documents",
                "kind": "json",
                "path": "sources/documents.jsonl",
                "concept_type": "Document",
                "ontology_class": "Document",
                "id_field": "id",
                "title_field": "title",
                "schema": {"id": "string", "title": "string", "summary": "string"},
                "fields": {"summary": "summary"},
            }
        ],
    }
    path = root / "manifest.json"
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return path


def run_script(
    skill: Path, script: str, *args: str, timeout: int = 180
) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment.pop("PYTHONPATH", None)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run(
        [sys.executable, str(skill / "scripts" / script), *args],
        cwd=skill,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=timeout,
        check=False,
        env=environment,
    )


def payload(result: subprocess.CompletedProcess[str]) -> dict[str, object]:
    assert result.returncode == 0, result.stderr or result.stdout
    value = json.loads(result.stdout.splitlines()[-1])
    assert isinstance(value, dict)
    return value


def tree_sha256(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(
        (candidate for candidate in root.rglob("*") if candidate.is_file()),
        key=lambda item: item.relative_to(root).as_posix(),
    ):
        digest.update(path.relative_to(root).as_posix().encode())
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def record_index_sha256(entries: list[object]) -> str:
    fields = (
        "concept_id",
        "concept_path",
        "concept_type",
        "paper_id",
        "record_id",
        "record_sha256",
        "source_id",
        "view_path",
        "view_sha256",
    )
    canonical = [{field: entry[field] for field in fields} for entry in entries]
    encoded = json.dumps(
        canonical,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def test_graphify_skills_declare_distinct_standalone_authorities() -> None:
    build = (BUILD_SKILL / "SKILL.md").read_text(encoding="utf-8")
    consult = (CONSULT_SKILL / "SKILL.md").read_text(encoding="utf-8")
    assert "name: build-semantic-okf-graphify" in build
    assert "name: consult-semantic-okf-graphify" in consult
    assert "Do not search, answer" in build
    assert "Read-only boundary" in consult
    assert "graphifyy==0.9.17" in (
        BUILD_SKILL / "scripts" / "requirements.in"
    ).read_text(encoding="utf-8")
    assert (CONSULT_SKILL / "scripts" / "requirements.in").read_text(
        encoding="utf-8"
    ).strip() == "graphifyy==0.9.17"


def test_copied_graphify_skills_build_query_deterministically_and_fail_closed(
    tmp_path: Path,
) -> None:
    build_skill = tmp_path / "build-skill"
    consult_skill = tmp_path / "consult-skill"
    shutil.copytree(BUILD_SKILL, build_skill, ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copytree(CONSULT_SKILL, consult_skill, ignore=shutil.ignore_patterns("__pycache__"))
    fixture = tmp_path / "fixture"
    fixture.mkdir()
    manifest = write_fixture(fixture)
    output_a = tmp_path / "bundle-a"
    output_b = tmp_path / "bundle-b"

    first = payload(
        run_script(
            build_skill,
            "build_semantic_okf_graphify.py",
            str(manifest),
            str(output_a),
            "--output-format",
            "json",
        )
    )
    second = payload(
        run_script(
            build_skill,
            "build_semantic_okf_graphify.py",
            str(manifest),
            str(output_b),
            "--output-format",
            "json",
        )
    )
    assert first["graphify"]["summary"]["records"] == 1
    assert first["graphify"]["summary"]["orphans"] == 0
    assert first["graphify"]["logical_sha256"] == second["graphify"]["logical_sha256"]
    assert (output_a / "retrieval" / "graphify" / "graph.json").read_bytes() == (
        output_b / "retrieval" / "graphify" / "graph.json"
    ).read_bytes()
    assert not (output_a / ".graphify-views").exists()
    assert not any(path.name == "graphify-out" for path in output_a.rglob("*"))
    independent_validation = payload(
        run_script(
            build_skill,
            "validate_semantic_okf_graphify.py",
            str(output_a),
            "--output-format",
            "json",
        )
    )
    assert independent_validation["valid"] is True
    assert independent_validation["semantic"]["valid"] is True
    assert independent_validation["graphify"]["valid"] is True

    ledger_record = json.loads(
        (output_a / "semantic" / "records.jsonl").read_text(encoding="utf-8")
    )
    before = tree_sha256(output_a)
    search = payload(
        run_script(
            consult_skill,
            "query_semantic_okf_graphify.py",
            str(output_a),
            "search",
            "connected graph retrieval",
            "--top-k",
            "5",
            "--show-content",
        )
    )
    repeated_search = payload(
        run_script(
            consult_skill,
            "query_semantic_okf_graphify.py",
            str(output_a),
            "search",
            "connected graph retrieval",
            "--top-k",
            "5",
            "--show-content",
        )
    )
    assert repeated_search == search
    assert search["fallback"] is None
    assert "graphify_text" not in search
    assert search["context_nodes"]
    assert search["records"][0]["concept_path"] == ledger_record["concept_path"]
    assert search["records"][0]["concept_sha256"]
    assert search["records"][0]["evidence"]["kind"] == "concept-file"
    assert search["records"][0]["source_path"] == ledger_record["source_path"]
    assert search["records"][0]["content"] == (
        output_a / ledger_record["concept_path"]
    ).read_text(encoding="utf-8")
    graph_before_tamper = json.loads(
        (output_a / "retrieval" / "graphify" / "graph.json").read_text(encoding="utf-8")
    )
    projected_labels = [
        str(node.get("label", ""))
        for node in graph_before_tamper["nodes"]
        if node.get("projection") == "graphify-view"
    ]
    assert all("](" not in label for label in projected_labels)
    exact = payload(
        run_script(
            consult_skill,
            "query_semantic_okf_graphify.py",
            str(output_a),
            "records",
            "--source-id",
            "documents",
            "--record-id",
            "doc-1",
        )
    )
    assert exact["returned"] == 1
    assert exact["records"][0]["attributes"]["summary"] == (
        "Local-first connected graph retrieval [Injected](../../escape.md)"
    )
    assert tree_sha256(output_a) == before

    index_path = output_b / "retrieval" / "graphify" / "index.json"
    index = json.loads(index_path.read_text(encoding="utf-8"))
    index["records"][0]["paper_id"] = "forged-paper"
    index["record_index_sha256"] = record_index_sha256(index["records"])
    index_path.write_text(
        json.dumps(index, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    forged = run_script(
        consult_skill,
        "query_semantic_okf_graphify.py",
        str(output_b),
        "verify",
    )
    assert forged.returncode == 2
    assert "record index identity or view digest mismatch" in forged.stderr
    assert "Traceback" not in forged.stderr

    index["records"][0] = "malformed"
    index_path.write_text(json.dumps(index, sort_keys=True) + "\n", encoding="utf-8")
    malformed = run_script(
        consult_skill,
        "query_semantic_okf_graphify.py",
        str(output_b),
        "verify",
    )
    assert malformed.returncode == 2
    assert "closed schema" in malformed.stderr or "must be an object" in malformed.stderr
    assert "Traceback" not in malformed.stderr

    graph_path = output_a / "retrieval" / "graphify" / "graph.json"
    graph = json.loads(graph_path.read_text(encoding="utf-8"))
    graph["nodes"][0]["label"] = "tampered"
    graph_path.write_text(json.dumps(graph, sort_keys=True) + "\n", encoding="utf-8")
    invalid = run_script(
        consult_skill,
        "query_semantic_okf_graphify.py",
        str(output_a),
        "verify",
    )
    assert invalid.returncode == 2
    assert "graph file digest changed" in invalid.stderr
