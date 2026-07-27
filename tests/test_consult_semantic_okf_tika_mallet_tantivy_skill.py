from __future__ import annotations

import hashlib
import importlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from types import ModuleType

import pytest
import yaml

from tika_mallet_test_support import (
    REPO_ROOT,
    build_portable_bundle,
    tree_hashes,
)


SKILL_ROOT = (
    REPO_ROOT / "skills" / "consult-semantic-okf-tika-mallet-tantivy"
)
SCRIPTS = SKILL_ROOT / "scripts"
QUERY = SCRIPTS / "query_semantic_okf_tika_mallet_tantivy.py"


@pytest.fixture(scope="module")
def bundle(tmp_path_factory: pytest.TempPathFactory) -> Path:
    root = tmp_path_factory.mktemp("consult-tika-mallet-tantivy")
    output, *_ = build_portable_bundle(root)
    return output


def run_query(
    bundle_path: Path,
    *args: str,
    skill_root: Path = SKILL_ROOT,
) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment.pop("PYTHONPATH", None)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run(
        [
            sys.executable,
            "-B",
            str(
                skill_root
                / "scripts"
                / "query_semantic_okf_tika_mallet_tantivy.py"
            ),
            str(bundle_path),
            *args,
        ],
        cwd=skill_root,
        env=environment,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=60,
        check=False,
    )


def load_module() -> ModuleType:
    for name in (
        "_safe_paths",
        "_mallet_topics",
        "_tika_snapshot",
        "_tika_mallet_tantivy_snapshot",
    ):
        sys.modules.pop(name, None)
    sys.path.insert(0, str(SCRIPTS))
    try:
        return importlib.import_module("_tika_mallet_tantivy_snapshot")
    finally:
        sys.path.remove(str(SCRIPTS))


def test_skill_package_is_valid_standalone_and_pinned() -> None:
    skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
    metadata = yaml.safe_load(skill.split("---", 2)[1])
    implementation = (
        SCRIPTS / "_tika_mallet_tantivy_snapshot.py"
    ).read_text(encoding="utf-8")
    package_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in SKILL_ROOT.rglob("*")
        if path.is_file() and path.suffix in {".md", ".py", ".yaml"}
    )

    assert set(metadata) == {"name", "description"}
    assert metadata["name"] == "consult-semantic-okf-tika-mallet-tantivy"
    assert "read-only" in metadata["description"]
    assert "## Standalone and read-only boundary" in skill
    assert "TODO" not in package_text
    assert "tantivy.Index(builder.build())" in implementation
    assert "_bm25_scores" not in implementation
    assert "import a sibling skill" in skill
    assert (SCRIPTS / "requirements.in").read_text(encoding="utf-8").splitlines() == [
        "pyyaml==6.0.3",
        "tantivy==0.26.0",
    ]
    assert "$consult-semantic-okf-tika-mallet-tantivy" in (
        SKILL_ROOT / "agents" / "openai.yaml"
    ).read_text(encoding="utf-8")
    assert (SKILL_ROOT / "references" / "tantivy-runtime.md").is_file()
    assert QUERY.is_file()


def test_runtime_inspection_and_copied_package_are_read_only(
    bundle: Path,
    tmp_path: Path,
) -> None:
    copied = tmp_path / SKILL_ROOT.name
    shutil.copytree(
        SKILL_ROOT,
        copied,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
    )
    runtime = subprocess.run(
        [sys.executable, "-B", str(copied / "scripts" / "runtime_smoke.py")],
        cwd=copied,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=30,
        check=False,
    )
    before = tree_hashes(bundle)
    inspected = run_query(bundle, "inspect", skill_root=copied)
    after = tree_hashes(bundle)

    assert runtime.returncode == 0, runtime.stdout + runtime.stderr
    runtime_payload = json.loads(runtime.stdout)
    assert runtime_payload["packages"] == {
        "pyyaml": "6.0.3",
        "tantivy": "0.26.0",
    }
    assert runtime_payload["engine"]["implementation"] == "Rust"
    assert inspected.returncode == 0, inspected.stdout + inspected.stderr
    payload = json.loads(inspected.stdout)
    assert payload["status"] == "pass"
    assert payload["tika"]["tika_version"] == "4.0.0-beta-1"
    assert payload["mallet"]["version"] == "2.1.0"
    assert payload["engine"]["package_version"] == "0.26.0"
    assert payload["engine"]["index_storage"] == "memory"
    assert payload["capabilities"] == [
        "tantivy",
        "topic",
        "association",
        "fusion",
    ]
    assert before == after


@pytest.mark.parametrize(
    "mode",
    ["tantivy", "topic", "association", "fusion"],
)
def test_all_modes_use_tantivy_and_return_exact_evidence(
    bundle: Path,
    mode: str,
) -> None:
    before = tree_hashes(bundle)
    completed = run_query(
        bundle,
        "search",
        "--query",
        "audit evidence extraction",
        "--mode",
        mode,
        "--top-k",
        "5",
    )
    after = tree_hashes(bundle)

    assert completed.returncode == 0, completed.stdout + completed.stderr
    result = json.loads(completed.stdout)
    assert result["requested_mode"] == result["effective_mode"] == mode
    assert result["parsed_query"] == "audit evidence extraction"
    assert result["engine"]["id"] == "tika-mallet-tantivy-0.26.0-fusion-v1"
    assert result["engine"]["implementation"] == "Rust"
    assert result["engine"]["index_storage"] == "memory"
    assert result["engine"]["indexed_documents"] == 2
    assert set(result["engine"]["lexical_queries"]) == {
        "tantivy",
        "association",
        "topic",
    }
    assert result["results"]
    records = {
        (row["source_id"], row["record_id"]): row
        for row in (
            json.loads(line)
            for line in (bundle / "semantic" / "records.jsonl")
            .read_text(encoding="utf-8")
            .splitlines()
        )
    }
    for hit in result["results"]:
        record = records[(hit["source_id"], hit["record_id"])]
        assert hit["locator"] == {"kind": "record"}
        assert hit["text"] == record["body"]
        assert hit["text_sha256"] == hashlib.sha256(
            record["body"].encode()
        ).hexdigest()
        assert (bundle / hit["concept_path"]).is_file()
    assert before == after


def test_filters_precede_indexing_and_syntax_is_preserved(bundle: Path) -> None:
    filtered = run_query(
        bundle,
        "search",
        "--query",
        '"audit evidence" OR workbook',
        "--mode",
        "fusion",
        "--source-id",
        "office-documents",
        "--concept-type",
        "Office Document",
    )

    assert filtered.returncode == 0, filtered.stdout + filtered.stderr
    result = json.loads(filtered.stdout)
    assert result["parsed_query"] == '"audit evidence" OR workbook'
    assert result["engine"]["query_normalization"] == "preserved-syntax"
    assert result["engine"]["indexed_documents"] == 1
    assert result["filters"] == {
        "source_ids": ["office-documents"],
        "concept_ids": [],
        "concept_types": ["Office Document"],
    }
    assert result["results"]
    assert {row["source_id"] for row in result["results"]} == {
        "office-documents"
    }


def test_compact_evidence_discloses_engine_and_validates_answer(
    bundle: Path,
    tmp_path: Path,
) -> None:
    compact = run_query(
        bundle,
        "batch-search",
        "--query",
        "audit evidence",
        "--query",
        "spreadsheet validation",
        "--mode",
        "fusion",
        "--top-k",
        "2",
        "--evidence-only",
    )

    assert compact.returncode == 0, compact.stdout + compact.stderr
    payload = json.loads(compact.stdout)
    assert payload["query_count"] == 2
    assert all(
        search["engine"]["package_version"] == "0.26.0"
        for search in payload["searches"]
    )
    evidence = [
        search["results"][0]["evidence"]
        for search in payload["searches"]
    ]
    candidate = {
        "question_id": "q-hybrid",
        "answer": {
            "summary": "The exact supports cover both retrieval intents.",
            "claims": [
                {
                    "statement": "The first support is grounded.",
                    "evidence_indices": [0],
                },
                {
                    "statement": "The second support is grounded.",
                    "evidence_indices": [1],
                },
            ],
        },
        "evidence": evidence,
    }
    answer = tmp_path / "answer.json"
    answer.write_text(json.dumps(candidate), encoding="utf-8")
    validated = run_query(
        bundle,
        "validate-answer",
        "--answer",
        str(answer),
    )

    assert validated.returncode == 0, validated.stdout + validated.stderr
    assert json.loads(validated.stdout)["exact_evidence"] is True


def test_answer_pack_finalizes_support_ids_without_mutating_bundle(
    bundle: Path,
    tmp_path: Path,
) -> None:
    before = tree_hashes(bundle)
    pack_path = tmp_path / "pack.json"
    packed = run_query(
        bundle,
        "answer-pack",
        "--query",
        "audit evidence",
        "--query",
        "spreadsheet validation",
        "--mode",
        "fusion",
        "--top-k",
        "2",
        "--max-sources",
        "4",
        "--output",
        str(pack_path),
    )

    assert packed.returncode == 0, packed.stdout + packed.stderr
    pack = json.loads(packed.stdout)
    assert pack["schema_version"] == (
        "semantic-okf-tika-mallet-tantivy-answer-pack/1.0"
    )
    assert pack["engine"]["package_version"] == "0.26.0"
    assert pack["engine"]["index_storage"] == "memory"
    assert pack["queries"] == ["audit evidence", "spreadsheet validation"]
    assert [row["query"] for row in pack["retrieval"]] == pack["queries"]
    assert all("lexical_queries" in row for row in pack["retrieval"])
    assert [row["support_id"] for row in pack["results"]] == ["s01", "s02"]
    draft = {
        "question_id": "q-hybrid-pack",
        "summary": "Both exact supports ground the synthesized response.",
        "claims": [
            {
                "statement": "The two supports cover distinct source formats.",
                "support_ids": ["s02", "s01"],
            }
        ],
    }
    draft_path = tmp_path / "draft.json"
    draft_path.write_text(json.dumps(draft), encoding="utf-8")
    output_path = tmp_path / "final.json"
    finalized = run_query(
        bundle,
        "finalize-answer",
        "--pack",
        str(pack_path),
        "--draft",
        str(draft_path),
        "--output",
        str(output_path),
    )

    assert finalized.returncode == 0, finalized.stdout + finalized.stderr
    confirmation = json.loads(finalized.stdout)
    assert confirmation["status"] == "pass"
    assert confirmation["support_count"] == 2
    final = json.loads(output_path.read_text(encoding="utf-8"))
    assert final["answer"]["claims"][0]["evidence_indices"] == [0, 1]
    assert tree_hashes(bundle) == before


def test_invalid_query_and_tampered_projection_fail_closed(
    bundle: Path,
    tmp_path: Path,
) -> None:
    invalid = run_query(
        bundle,
        "search",
        "--query",
        "(",
        "--mode",
        "tantivy",
    )
    altered = tmp_path / "altered"
    shutil.copytree(bundle, altered)
    documents = altered / "classical" / "documents.jsonl"
    documents.write_bytes(documents.read_bytes() + b"\n")
    tampered = run_query(altered, "inspect")

    assert invalid.returncode == 2
    assert "invalid Tantivy query" in json.loads(invalid.stdout)["error"]
    assert tampered.returncode == 2
    assert json.loads(tampered.stdout)["code"] == "tika-mallet-tantivy-error"


def test_helpers_reject_unsupported_bm25_and_escape_only_safe_expansions() -> None:
    module = load_module()
    plan = {
        "bm25": {
            "k1": 1.5,
            "b": 0.75,
            "title_weight": 2.0,
            "body_weight": 1.0,
        }
    }
    with pytest.raises(module.SnapshotError, match="k1=1.2"):
        module._validate_tantivy_bm25(plan)

    assert module._expanded_query(
        '"audit evidence"',
        ["retention", "bad*term", "retention"],
        explicit_syntax=True,
    ) == '("audit evidence") OR retention'
