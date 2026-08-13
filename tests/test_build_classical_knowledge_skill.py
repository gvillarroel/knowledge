"""Tests for the integrated classical knowledge-skill generator."""

from __future__ import annotations

from collections import Counter
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


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = REPO_ROOT / "skills" / "build-classical-knowledge-skill"
SCRIPTS = SKILL_ROOT / "scripts"
BUILD = SCRIPTS / "build_classical_knowledge_skill.py"
VALIDATE = SCRIPTS / "validate_classical_knowledge_skill.py"
SEPARATE_QUERY = (
    REPO_ROOT
    / "skills"
    / "consult-semantic-okf-classical"
    / "scripts"
    / "query_semantic_okf_classical.py"
)
PARITY_REPORT = (
    REPO_ROOT
    / "evaluations"
    / "integrated-classical-knowledge-skill"
    / "reports"
    / "20260813-parity-verification.json"
)


def _write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _write_fixture(root: Path) -> tuple[Path, Path, Path]:
    sources = root / "sources"
    sources.mkdir(parents=True)
    rows = [
        {
            "id": "record-alpha",
            "title": "Graph retrieval",
            "code": "A-1",
            "summary": (
                "Graph retrieval connects entities, relations, paths, and grounded "
                "evidence through community summaries."
            ),
        },
        {
            "id": "record-beta",
            "title": "Lexical retrieval",
            "code": "B-1",
            "summary": (
                "Lexical ranking uses exact terminology while association statistics "
                "expand related concepts for diverse retrieval."
            ),
        },
    ]
    (sources / "documents.jsonl").write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
        newline="\n",
    )
    manifest = {
        "schema_version": "1.0",
        "bundle": {
            "title": "Integrated classical fixture",
            "description": "A deterministic fixture for generated knowledge skills.",
            "base_iri": "https://example.org/integrated-classical/",
            "ontology_iri": "https://example.org/ontology/integrated-classical",
            "version_iri": "https://example.org/ontology/integrated-classical/1.0.0",
            "prefix": "fixture",
            "owl_profile": "rl",
        },
        "ontology": {
            "classes": [{"name": "Document", "label": "document"}],
            "properties": [
                {
                    "name": name,
                    "kind": "datatype",
                    "domain": "Document",
                    "range": "xsd:string",
                }
                for name in ("code", "summary")
            ],
        },
        "rules": [
            {
                "name": "DocumentCodeRule",
                "target_class": "Document",
                "path": "code",
                "min_count": 1,
                "datatype": "xsd:string",
                "message": "Every document requires a reviewed code.",
                "basis": {"kind": "operational-policy", "references": ["FIXTURE-1"]},
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
                "schema": {
                    "id": "string",
                    "title": "string",
                    "code": "string",
                    "summary": "string",
                },
                "fields": {"code": "code", "summary": "summary"},
            }
        ],
    }
    plan = {
        "schema_version": "1.0",
        "selection": {"source_ids": ["documents"]},
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
            "max_vocabulary": 64,
            "max_neighbors": 8,
            "minimum_ppmi": 0.0,
        },
        "topics": {"topic_count": 3, "max_iterations": 10, "top_terms": 6},
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
            "max_per_evidence_identity": 2,
            "rrf_k": 60,
        },
    }
    guidance = root / "guidance.md"
    guidance.write_text(
        """# Retrieval Evidence Expert

## Scope

Answer questions about the two bundled retrieval records. Keep graph and
lexical mechanisms distinct and do not introduce knowledge outside the snapshot.

## Application workflow

Search with the complete question, inspect the exact selected records, compare
the requested mechanisms, and cite every physical bundled evidence location.

## Decision rules

Use direct record language before synthesis. Treat association, topic, and BM25
scores as discovery only. Preserve differences and important negative limits.

## Evidence and limits

Cite exact physical Markdown paths and packed-record anchors. Label inference
and stop when the immutable two-record snapshot cannot support a conclusion.
""",
        encoding="utf-8",
        newline="\n",
    )
    manifest_path = root / "manifest.json"
    plan_path = root / "classical-plan.json"
    _write_json(manifest_path, manifest)
    _write_json(plan_path, plan)
    return manifest_path, plan_path, guidance


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
        timeout=120,
        check=False,
    )


def _tree_bytes(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def _build_arguments(
    manifest: Path,
    plan: Path,
    output: Path,
    guidance: Path,
) -> list[object]:
    return [
        BUILD,
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


def test_skill_metadata_and_package_are_standalone() -> None:
    skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
    metadata = yaml.safe_load(skill.split("---", 2)[1])
    assert set(metadata) == {"name", "description"}
    assert metadata["name"] == "build-classical-knowledge-skill"
    assert "ready-to-use" in metadata["description"]
    assert "build-semantic-okf-classical" not in skill
    assert "consult-semantic-okf-classical" not in skill
    assert "## Standalone authority boundary" in skill
    assert "## Consultation acceptance" in skill
    assert (SCRIPTS / "requirements.txt").is_file()
    assert (SKILL_ROOT / "references" / "expert-skill-contract.md").is_file()


def test_packaged_implementation_matches_the_accepted_classical_sources() -> None:
    pairs = (
        (
            SCRIPTS / "_semantic_okf.py",
            REPO_ROOT / "skills/build-semantic-okf-classical/scripts/_semantic_okf.py",
        ),
        (
            SCRIPTS / "_build_semantic_okf_core.py",
            REPO_ROOT
            / "skills/build-semantic-okf-classical/scripts/_build_semantic_okf_core.py",
        ),
        (
            SCRIPTS / "_classical_retrieval.py",
            REPO_ROOT
            / "skills/build-semantic-okf-classical/scripts/_classical_retrieval.py",
        ),
        (
            SCRIPTS / "_classical_snapshot.py",
            REPO_ROOT
            / "skills/consult-semantic-okf-classical/scripts/_classical_snapshot.py",
        ),
        (
            SCRIPTS / "requirements.in",
            REPO_ROOT / "skills/build-semantic-okf-classical/scripts/requirements.in",
        ),
        (
            SCRIPTS / "requirements.txt",
            REPO_ROOT / "skills/build-semantic-okf-classical/scripts/requirements.txt",
        ),
    )
    for packaged, accepted in pairs:
        assert packaged.read_bytes() == accepted.read_bytes()


def test_build_validate_check_query_and_packed_citations(tmp_path: Path) -> None:
    manifest, plan, guidance = _write_fixture(tmp_path)
    output = tmp_path / "retrieval-evidence-expert"
    build = _run(*_build_arguments(manifest, plan, output, guidance))
    assert build.returncode == 0, build.stderr or build.stdout
    result = json.loads(build.stdout)
    assert result["status"] == "pass"
    assert result["record_count"] == 2
    assert result["concept_layout"] == "source-packed-v1"
    assert not (output / "concepts").exists()
    assert (output / "references" / "knowledge" / "concepts" / "documents.md").is_file()

    before = _tree_bytes(output)
    validate = _run(VALIDATE, output, "--deep-validation")
    assert validate.returncode == 0, validate.stdout
    assert json.loads(validate.stdout)["valid"] is True
    check = _run(*_build_arguments(manifest, plan, output, guidance), "--check")
    assert check.returncode == 0, check.stderr or check.stdout
    assert json.loads(check.stdout)["mode"] == "check"
    assert _tree_bytes(output) == before

    helper = output / "scripts" / "query_expert_knowledge.py"
    verify = _run(helper, "verify", "--deep-validation", cwd=tmp_path)
    assert verify.returncode == 0, verify.stdout
    verified = json.loads(verify.stdout)
    assert verified["evidence_records_verified"] == 2
    search = _run(
        helper,
        "search",
        "--query",
        "graph relations and grounded evidence",
        "--top-k",
        "2",
        cwd=tmp_path,
    )
    assert search.returncode == 0, search.stdout
    payload = json.loads(search.stdout)
    assert payload["requested_mode"] == "fusion"
    assert payload["effective_mode"] == "fusion"
    assert payload["results"]
    document_rows = {
        row["document_id"]: row
        for row in (
            json.loads(line)
            for line in (
                output
                / "references"
                / "knowledge"
                / "classical"
                / "documents.jsonl"
            )
            .read_text(encoding="utf-8")
            .splitlines()
            if line.strip()
        )
    }
    for hit in payload["results"]:
        assert hit["physical_concept_path"] == "concepts/documents.md"
        assert hit["evidence_path"] == "references/knowledge/concepts/documents.md"
        assert hit["evidence_anchor"].startswith("record-")
        physical = output / Path(hit["evidence_path"])
        text = physical.read_text(encoding="utf-8")
        assert f'<a id="{hit["evidence_anchor"]}"></a>' in text
        assert hit["text"] == document_rows[hit["document_id"]]["text"]
    assert _tree_bytes(output) == before


def test_generated_query_matches_separate_classical_consultation(tmp_path: Path) -> None:
    manifest, plan, guidance = _write_fixture(tmp_path)
    output = tmp_path / "parity-expert"
    build = _run(*_build_arguments(manifest, plan, output, guidance))
    assert build.returncode == 0, build.stderr or build.stdout
    helper = output / "scripts" / "query_expert_knowledge.py"
    knowledge = output / "references" / "knowledge"
    queries = (
        "exact lexical terminology",
        "related recurring concepts",
        "graph entities relations and paths",
    )
    for mode in ("bm25", "topic", "association", "fusion"):
        for query in queries:
            integrated = _run(
                helper,
                "search",
                "--query",
                query,
                "--mode",
                mode,
                "--top-k",
                "2",
                cwd=tmp_path,
            )
            separate = _run(
                SEPARATE_QUERY,
                knowledge,
                "search",
                "--query",
                query,
                "--mode",
                mode,
                "--top-k",
                "2",
                cwd=tmp_path,
            )
            assert integrated.returncode == separate.returncode == 0
            integrated_ids = [
                row["document_id"] for row in json.loads(integrated.stdout)["results"]
            ]
            separate_ids = [
                row["document_id"] for row in json.loads(separate.stdout)["results"]
            ]
            assert integrated_ids == separate_ids


def test_tamper_and_invalid_inputs_fail_closed(tmp_path: Path) -> None:
    manifest, plan, guidance = _write_fixture(tmp_path)
    output = tmp_path / "tamper-expert"
    assert _run(*_build_arguments(manifest, plan, output, guidance)).returncode == 0
    helper = output / "scripts" / "query_expert_knowledge.py"
    (output / "references" / "guidance.md").write_text(
        "tampered\n",
        encoding="utf-8",
    )
    tamper = _run(helper, "verify", cwd=tmp_path)
    assert tamper.returncode == 2
    assert "drift" in json.loads(tamper.stdout)["error"]

    bad_output = tmp_path / "wrong-name"
    bad = _run(
        BUILD,
        manifest,
        plan,
        bad_output,
        "--name",
        "different-name",
        "--description",
        "A valid description that should fail only because the output name differs.",
        "--guidance",
        guidance,
        "--output-format",
        "json",
    )
    assert bad.returncode == 2
    assert json.loads(bad.stdout)["code"] == "knowledge-skill-error"
    assert not bad_output.exists()


def test_packed_evidence_body_must_follow_its_unique_anchor(tmp_path: Path) -> None:
    manifest, plan, guidance = _write_fixture(tmp_path)
    output = tmp_path / "anchor-expert"
    assert _run(*_build_arguments(manifest, plan, output, guidance)).returncode == 0
    ledger = [
        json.loads(line)
        for line in (
            output / "references" / "knowledge" / "semantic" / "records.jsonl"
        ).read_text(encoding="utf-8").splitlines()
    ]
    first = ledger[0]
    packed = output / "references" / "knowledge" / "concepts" / "documents.md"
    text = packed.read_text(encoding="utf-8")
    marker = f'<a id="record-{first["record_sha256"][:16]}"></a>'
    marker_offset = text.index(marker)
    body_offset = text.index(first["body"], marker_offset + len(marker))
    text = (
        text[:body_offset]
        + text[body_offset + len(first["body"]) :]
        + "\n"
        + first["body"]
        + "\n"
    )
    packed.write_text(text, encoding="utf-8", newline="\n")

    scripts = output / "scripts"
    previous_runtime = sys.modules.pop("_classical_snapshot", None)
    previous_bytecode = sys.dont_write_bytecode
    sys.path.insert(0, str(scripts))
    try:
        helper_path = scripts / "query_expert_knowledge.py"
        spec = importlib.util.spec_from_file_location("_anchor_expert_query", helper_path)
        assert spec is not None and spec.loader is not None
        helper = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(helper)
        counts = Counter(str(row["source_id"]) for row in ledger)
        with pytest.raises(helper.ExpertQueryError, match="not bound to its exact anchor"):
            helper._evidence_location(
                first,
                layout="source-packed-v1",
                source_counts=counts,
            )
    finally:
        sys.path.remove(str(scripts))
        sys.modules.pop("_classical_snapshot", None)
        if previous_runtime is not None:
            sys.modules["_classical_snapshot"] = previous_runtime
        sys.dont_write_bytecode = previous_bytecode


def test_unbound_generated_skill_files_fail_closed(tmp_path: Path) -> None:
    manifest, plan, guidance = _write_fixture(tmp_path)
    output = tmp_path / "closed-surface-expert"
    assert _run(*_build_arguments(manifest, plan, output, guidance)).returncode == 0
    (output / "references" / "unbound-instructions.md").write_text(
        "# Unbound instructions\n",
        encoding="utf-8",
        newline="\n",
    )
    validation = _run(VALIDATE, output)
    assert validation.returncode == 2
    assert "surface is not closed" in json.loads(validation.stdout)["errors"][0][
        "message"
    ]
    verification = _run(
        output / "scripts" / "query_expert_knowledge.py",
        "verify",
        cwd=tmp_path,
    )
    assert verification.returncode == 2
    assert "surface is not closed" in json.loads(verification.stdout)["error"]


def test_copied_generator_remains_executable(tmp_path: Path) -> None:
    copied = tmp_path / "copied-skill"
    shutil.copytree(SKILL_ROOT, copied)
    help_result = _run(copied / "scripts" / "build_classical_knowledge_skill.py", "--help")
    validate_help = _run(
        copied / "scripts" / "validate_classical_knowledge_skill.py",
        "--help",
    )
    smoke = _run(copied / "scripts" / "runtime_smoke.py")
    assert help_result.returncode == 0
    assert "ready-to-use skill" in help_result.stdout
    assert validate_help.returncode == 0
    assert smoke.returncode == 0
    assert json.loads(smoke.stdout)["status"] == "pass"


def test_package_files_are_lf_and_no_bytecode_is_shipped() -> None:
    for path in SKILL_ROOT.rglob("*"):
        if not path.is_file():
            continue
        assert "__pycache__" not in path.parts
        assert path.suffix != ".pyc"
        data = path.read_bytes()
        assert b"\r\n" not in data
    requirements = (SCRIPTS / "requirements.txt").read_text(encoding="utf-8")
    assert "pyshacl==0.40.0" in requirements
    assert "rdflib==7.6.0" in requirements
    assert hashlib.sha256(requirements.encode("utf-8")).hexdigest()


def test_canonical_dataset_parity_report_is_complete_and_passing() -> None:
    report = json.loads(PARITY_REPORT.read_text(encoding="utf-8"))
    assert report["schema_version"] == (
        "integrated-classical-knowledge-skill-comparison/1.0"
    )
    assert report["status"] == "pass"
    assert [row["dataset_id"] for row in report["datasets"]] == [
        "graphrag-papers-40",
        "astro-40",
        "quantum-error-correction-papers-40",
    ]
    for row in report["datasets"]:
        assert row["question_count"] == 40
        assert row["route_count"] == 4
        assert row["query_route_cells"] == 160
        assert row["exact_payload_cells"] == 160
        assert row["exact_ranking_cells"] == 160
        assert row["payload_mismatches"] == 0
        assert row["ranking_mismatches"] == 0
        assert row["integrated_citation_hits"] == row["returned_hits"]
        assert row["authoritative_evidence_records_verified"] == row[
            "authoritative_records"
        ]
        assert row["knowledge_bytes_equal"] is True
        assert row["runtime_bytes_equal"] is True
        assert row["public_fusion_probe_cells"] == 1
    totals = report["totals"]
    assert totals["question_count"] == 120
    assert totals["query_route_cells"] == 480
    assert totals["exact_payload_rate"] == 1.0
    assert totals["integrated_citation_resolution_rate"] == 1.0
    assert totals["citation_resolution_gain_hits"] >= 0
    assert "not a new model-judged Harbor" in report["boundary"]
