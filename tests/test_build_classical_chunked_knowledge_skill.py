"""Tests for the token-bounded classical knowledge-skill generator."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Any

import pytest
import yaml

from tests.test_build_semantic_okf_classical_skill import write_fixture as write_classical_fixture


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = REPO_ROOT / "skills" / "build-classical-chunked-knowledge-skill"
SCRIPTS = SKILL_ROOT / "scripts"
BUILD = SCRIPTS / "build_classical_chunked_knowledge_skill.py"
VALIDATE = SCRIPTS / "validate_classical_chunked_knowledge_skill.py"
BASELINE_BUILD = (
    REPO_ROOT
    / "skills"
    / "build-classical-knowledge-skill"
    / "scripts"
    / "build_classical_knowledge_skill.py"
)
SEPARATE_QUERY = (
    REPO_ROOT
    / "skills"
    / "consult-semantic-okf-classical"
    / "scripts"
    / "query_semantic_okf_classical.py"
)


def _write_fixture(root: Path) -> tuple[Path, Path, Path]:
    manifest, plan = write_classical_fixture(root)
    repeated = " ".join(
        [
            "Graph retrieval connects entities, relations, paths, and grounded evidence.",
            "Lexical ranking preserves exact terminology and explicit identifiers.",
            "Association statistics recover related mechanisms without making them facts.",
            "Topic communities support thematic discovery while citations remain authoritative.",
            "A negative result must not be inferred from an incomplete retrieved context.",
        ]
        * 8
    )
    for source_id, focus in (
        ("alpha", "graph relations and grounded community evidence"),
        ("beta", "lexical terminology, association expansion, and topic analysis"),
    ):
        sections = "\n\n".join(
            f"## Section {index}: {focus}\n\n{repeated} Distinct marker {source_id}-{index}."
            for index in range(1, 9)
        )
        path = root / "sources" / f"{source_id}.md"
        original = path.read_text(encoding="utf-8")
        path.write_text(original.rstrip() + "\n\n" + sections + "\n", encoding="utf-8", newline="\n")
    guidance = root / "guidance.md"
    guidance.write_text(
        """# Chunked Retrieval Evidence Expert

## Scope

Answer questions about graph, lexical, association, and topic retrieval from
the bundled fixture. Keep discovery scores separate from authoritative facts.

## Application workflow

Use one complete-question context request, inspect exact selected spans, and
hydrate a linked neighbor only when the quality guard reports a boundary gap.

## Decision rules

Preserve exact terminology, distinct evidence identities, negative findings,
and source roles. Do not treat repeated chunks as independent corroboration.

## Evidence and limits

Cite physical Markdown and exact record character ranges. Label synthesis and
stop when the immutable evidence or context quality guard is insufficient.
""",
        encoding="utf-8",
        newline="\n",
    )
    return manifest, plan, guidance


def _run(*arguments: object, cwd: Path = REPO_ROOT) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment.pop("PYTHONPATH", None)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run(
        [sys.executable, "-B", *map(str, arguments)],
        cwd=cwd,
        env=environment,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=180,
        check=False,
    )


def _tree_bytes(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def _arguments(
    manifest: Path,
    plan: Path,
    output: Path,
    guidance: Path,
    *,
    baseline: bool = False,
) -> list[object]:
    command = BASELINE_BUILD if baseline else BUILD
    return [
        command,
        manifest,
        plan,
        output,
        "--name",
        output.name,
        "--description",
        "Answer retrieval questions from bundled classical knowledge with exact evidence.",
        "--guidance",
        guidance,
        "--concept-layout",
        "source-packed-v1",
        "--output-format",
        "json",
    ]


def test_skill_metadata_and_original_generator_remain_separate() -> None:
    skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
    metadata = yaml.safe_load(skill.split("---", 2)[1])
    assert set(metadata) == {"name", "description"}
    assert metadata["name"] == "build-classical-chunked-knowledge-skill"
    assert "excessive evidence tokens" in metadata["description"]
    assert "original build-classical-knowledge-skill must remain unchanged" in metadata[
        "description"
    ]
    assert "## Standalone authority boundary" in skill
    assert "quality guard" in skill
    assert (SKILL_ROOT / "assets" / "default-context-plan.json").is_file()
    assert (SKILL_ROOT / "references" / "context-projection.md").is_file()


def test_accepted_classical_implementation_is_vendored_byte_for_byte() -> None:
    baseline = REPO_ROOT / "skills" / "build-classical-knowledge-skill"
    for relative in (
        "scripts/_semantic_okf.py",
        "scripts/_build_semantic_okf_core.py",
        "scripts/_classical_retrieval.py",
        "scripts/_classical_snapshot.py",
        "scripts/requirements.in",
        "scripts/requirements.txt",
    ):
        assert (SKILL_ROOT / relative).read_bytes() == (baseline / relative).read_bytes()


def test_build_context_validate_check_and_preserve_knowledge(tmp_path: Path) -> None:
    manifest, plan, guidance = _write_fixture(tmp_path)
    output = tmp_path / "chunked-evidence-expert"
    baseline = tmp_path / "baseline-evidence-expert"
    build = _run(*_arguments(manifest, plan, output, guidance))
    assert build.returncode == 0, build.stderr or build.stdout
    result = json.loads(build.stdout)
    assert result["status"] == "pass"
    assert result["context_chunk_count"] > result["record_count"]
    assert result["default_context_budget_tokens"] == 6000

    baseline_build = _run(*_arguments(manifest, plan, baseline, guidance, baseline=True))
    assert baseline_build.returncode == 0, baseline_build.stderr or baseline_build.stdout
    assert _tree_bytes(output / "references" / "knowledge") == _tree_bytes(
        baseline / "references" / "knowledge"
    )

    manifest_payload = json.loads((output / "expert-manifest.json").read_text(encoding="utf-8"))
    assert manifest_payload["schema_version"] == "classical-chunked-knowledge-skill/1.0"
    assert manifest_payload["generation"]["builder"] == (
        "build-classical-chunked-knowledge-skill"
    )
    chunks = [
        json.loads(line)
        for line in (output / "references" / "context" / "chunks.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
        if line.strip()
    ]
    assert chunks
    assert all("text" not in row for row in chunks)
    assert all(row["record_char_start"] < row["record_char_end"] for row in chunks)
    assert any(row["previous_chunk_id"] for row in chunks)
    assert any(row["next_chunk_id"] for row in chunks)
    context_index = json.loads(
        (output / "references" / "context" / "index.json").read_text(encoding="utf-8")
    )
    assert context_index["algorithm"]["selection"] == (
        "budgeted-query-coverage-mmr-v1"
    )
    assert context_index["plan"]["selection"]["maximum_chunks"] == 48

    before = _tree_bytes(output)
    validation = _run(VALIDATE, output, "--deep-validation")
    assert validation.returncode == 0, validation.stdout
    validated = json.loads(validation.stdout)
    assert validated["valid"] is True
    assert validated["context_chunk_count"] == len(chunks)
    check = _run(*_arguments(manifest, plan, output, guidance), "--check")
    assert check.returncode == 0, check.stderr or check.stdout
    assert json.loads(check.stdout)["mode"] == "check"
    assert _tree_bytes(output) == before


def test_context_is_exact_smaller_and_full_search_rank_is_unchanged(tmp_path: Path) -> None:
    manifest, plan, guidance = _write_fixture(tmp_path)
    output = tmp_path / "bounded-context-expert"
    assert _run(*_arguments(manifest, plan, output, guidance)).returncode == 0
    helper = output / "scripts" / "query_expert_knowledge.py"
    query = (
        "Compare graph relations and grounded evidence with exact lexical terminology, "
        "association expansion, topic analysis, and the incomplete-context negative."
    )
    full = _run(helper, "search", "--query", query, "--mode", "fusion", "--top-k", "2")
    separate = _run(
        SEPARATE_QUERY,
        output / "references" / "knowledge",
        "search",
        "--query",
        query,
        "--mode",
        "fusion",
        "--top-k",
        "2",
    )
    assert full.returncode == separate.returncode == 0
    full_payload = json.loads(full.stdout)
    separate_payload = json.loads(separate.stdout)
    assert [row["document_id"] for row in full_payload["results"]] == [
        row["document_id"] for row in separate_payload["results"]
    ]

    compact = _run(
        helper,
        "context",
        "--query",
        query,
        "--mode",
        "fusion",
        "--format",
        "json",
    )
    markdown = _run(
        helper,
        "context",
        "--query",
        query,
        "--mode",
        "fusion",
        "--format",
        "markdown",
    )
    assert compact.returncode == markdown.returncode == 0, compact.stdout
    payload = json.loads(compact.stdout)
    assert payload["quality_guard"]["complete"] is True
    assert payload["budget"]["used_tokens"] <= payload["budget"]["maximum_tokens"]
    assert len(markdown.stdout.encode("utf-8")) < len(full.stdout.encode("utf-8")) * 0.5
    assert "<exact-evidence>" in markdown.stdout

    ledger = {
        (row["source_id"], row["record_id"]): row
        for row in (
            json.loads(line)
            for line in (output / "references" / "knowledge" / "semantic" / "records.jsonl")
            .read_text(encoding="utf-8")
            .splitlines()
            if line.strip()
        )
    }
    for row in payload["chunks"]:
        body = ledger[(row["source_id"], row["record_id"])]["body"]
        text = body[row["record_char_start"] : row["record_char_end"]]
        assert text == row["text"]
        assert hashlib.sha256(text.encode("utf-8")).hexdigest() == row["text_sha256"]
        assert (output / Path(row["evidence_path"])).is_file()

    first = payload["chunks"][0]
    neighbor = _run(
        helper,
        "chunk",
        "--chunk-id",
        first["chunk_id"],
        "--neighbors",
        "1",
        "--format",
        "json",
    )
    assert neighbor.returncode == 0, neighbor.stdout
    neighbor_payload = json.loads(neighbor.stdout)
    assert 1 <= len(neighbor_payload["chunks"]) <= 3
    assert any(row["chunk_id"] == first["chunk_id"] for row in neighbor_payload["chunks"])


def test_context_tamper_and_unsafe_budget_fail_closed(tmp_path: Path) -> None:
    manifest, plan, guidance = _write_fixture(tmp_path)
    output = tmp_path / "tamper-context-expert"
    assert _run(*_arguments(manifest, plan, output, guidance)).returncode == 0
    helper = output / "scripts" / "query_expert_knowledge.py"
    bad_budget = _run(
        helper,
        "context",
        "--query",
        "graph retrieval",
        "--budget-tokens",
        "200000",
    )
    assert bad_budget.returncode == 2
    assert "budget_tokens" in json.loads(bad_budget.stdout)["error"]

    chunks_path = output / "references" / "context" / "chunks.jsonl"
    chunks_path.write_text(
        chunks_path.read_text(encoding="utf-8") + "\n",
        encoding="utf-8",
        newline="\n",
    )
    tamper = _run(helper, "verify")
    assert tamper.returncode == 2
    assert "context tree digest drift" in json.loads(tamper.stdout)["error"].casefold()


def test_copied_generator_and_package_surface_are_portable(tmp_path: Path) -> None:
    copied = tmp_path / "copied-chunked-generator"
    shutil.copytree(SKILL_ROOT, copied)
    help_result = _run(copied / "scripts" / "build_classical_chunked_knowledge_skill.py", "--help")
    validation_help = _run(
        copied / "scripts" / "validate_classical_chunked_knowledge_skill.py",
        "--help",
    )
    smoke = _run(copied / "scripts" / "runtime_smoke.py")
    assert help_result.returncode == validation_help.returncode == smoke.returncode == 0
    assert "budgeted context" in help_result.stdout
    assert json.loads(smoke.stdout)["context_schema_version"] == (
        "classical-context-projection/1.0"
    )
    for path in SKILL_ROOT.rglob("*"):
        if path.is_file():
            assert "__pycache__" not in path.parts
            assert path.suffix != ".pyc"
            assert b"\r\n" not in path.read_bytes()


def test_context_projection_rejects_directional_or_open_plan(tmp_path: Path) -> None:
    module_path = SCRIPTS / "_context_projection.py"
    scripts_string = str(SCRIPTS)
    previous_bytecode = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    sys.path.insert(0, scripts_string)
    try:
        spec = importlib.util.spec_from_file_location("_chunk_context_test", module_path)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        plan = json.loads(
            (SKILL_ROOT / "assets" / "default-context-plan.json").read_text(
                encoding="utf-8"
            )
        )
        assert module.validate_plan(plan)["selection"]["minimum_query_coverage"] == 0.85
        plan["selection"]["cross_entropy"] = True
        with pytest.raises(module.ContextProjectionError, match="not closed"):
            module.validate_plan(plan)
    finally:
        sys.path.remove(scripts_string)
        sys.modules.pop("_chunk_context_test", None)
        sys.modules.pop("_classical_snapshot", None)
        sys.dont_write_bytecode = previous_bytecode
