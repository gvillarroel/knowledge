"""Tests for the canonical multi-family knowledge-skill generator."""

from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from types import ModuleType
from typing import Any

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = REPO_ROOT / "skills" / "build-semantic-okf-knowledge-skill"
SCRIPTS = SKILL_ROOT / "scripts"
BUILD = SCRIPTS / "build_semantic_okf_knowledge_skill.py"
VALIDATE = SCRIPTS / "validate_semantic_okf_knowledge_skill.py"
PARITY_REPORT = (
    REPO_ROOT
    / "evaluations"
    / "integrated-semantic-okf-knowledge-skill"
    / "reports"
    / "20260813-parity-verification.json"
)
FAMILIES = {
    "legacy": ("build-semantic-okf", "consult-semantic-okf"),
    "embeddings": ("build-semantic-okf-embeddings", "consult-semantic-okf-embeddings"),
    "classical": ("build-semantic-okf-classical", "consult-semantic-okf-classical"),
    "adaptive": ("build-semantic-okf-adaptive", "consult-semantic-okf-adaptive"),
    "entity-graph": ("build-semantic-okf-entity-graph", "consult-semantic-okf-entity-graph"),
    "ensemble": ("build-semantic-okf-ensemble", "consult-semantic-okf-ensemble"),
    "graphify": ("build-semantic-okf-graphify", "consult-semantic-okf-graphify"),
    "turso": ("build-semantic-okf-turso", "consult-semantic-okf-turso"),
}


def _run(*arguments: object, cwd: Path = REPO_ROOT) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment.pop("PYTHONPATH", None)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment["HF_HUB_OFFLINE"] = "1"
    environment["TRANSFORMERS_OFFLINE"] = "1"
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


def _write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _write_fixture(root: Path) -> tuple[Path, Path]:
    sources = root / "sources"
    sources.mkdir(parents=True)
    rows = [
        {
            "id": "record-alpha",
            "title": "Graph retrieval",
            "code": "A-1",
            "summary": "Graph retrieval connects entities and exact grounded evidence.",
        },
        {
            "id": "record-beta",
            "title": "Lexical retrieval",
            "code": "B-1",
            "summary": "Lexical retrieval preserves exact terminology and source identity.",
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
            "title": "Multi-family fixture",
            "description": "A deterministic fixture for direct expert generation.",
            "base_iri": "https://example.org/multi-family/",
            "ontology_iri": "https://example.org/ontology/multi-family",
            "version_iri": "https://example.org/ontology/multi-family/1.0.0",
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
    guidance = root / "guidance.md"
    guidance.write_text(
        """# Retrieval Evidence Expert

## Scope

Answer questions about the two bundled retrieval records and do not introduce
knowledge outside this immutable fixture.

## Application workflow

Search with the complete question, inspect exact selected records, compare the
requested mechanisms, and cite every bundled physical evidence location.

## Decision rules

Use direct record language before synthesis. Treat retrieval scores only as
discovery signals and preserve important distinctions and negative limits.

## Evidence and limits

Cite exact physical Markdown paths and packed-record anchors. Label inference
and stop when the two-record snapshot cannot support a conclusion.
""",
        encoding="utf-8",
        newline="\n",
    )
    manifest_path = root / "manifest.json"
    _write_json(manifest_path, manifest)
    return manifest_path, guidance


def _build_arguments(manifest: Path, guidance: Path, output: Path) -> list[object]:
    return [
        BUILD,
        manifest,
        output,
        "--family",
        "legacy",
        "--name",
        output.name,
        "--description",
        "Answer retrieval questions from bundled legacy knowledge with exact evidence.",
        "--guidance",
        guidance,
        "--concept-layout",
        "source-packed-v1",
        "--output-format",
        "json",
    ]


def _tree_bytes(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def _load_query_template() -> ModuleType:
    path = SKILL_ROOT / "assets" / "expert-template" / "query_expert_knowledge.py"
    spec = importlib.util.spec_from_file_location("test_family_expert_query", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_skill_metadata_and_registry_cover_all_canonical_families() -> None:
    skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
    metadata = yaml.safe_load(skill.split("---", 2)[1])
    assert set(metadata) == {"name", "description"}
    assert metadata["name"] == SKILL_ROOT.name
    assert "ready-to-use" in metadata["description"]
    assert "## Standalone family boundary" in skill
    assert "## Generated consultation" in skill

    registry = json.loads(
        (REPO_ROOT / "evaluations/semantic-okf-datasets/families.json").read_text(
            encoding="utf-8"
        )
    )["families"]
    sys.path.insert(0, str(SCRIPTS))
    try:
        import _family_registry

        assert set(_family_registry.PROFILES) == set(registry) == set(FAMILIES)
        for family, contract in registry.items():
            selected = _family_registry.PROFILES[family]
            assert selected.build_skill == contract["build_skill"]
            assert selected.consult_skill == contract["consult_skill"]
            assert selected.build_script == contract["build_script"]
            assert selected.validate_script == contract["validate_script"]
            assert selected.uses_plan is contract["uses_plan"]
    finally:
        sys.path.remove(str(SCRIPTS))


def test_vendored_packages_are_byte_identical_to_every_canonical_pair() -> None:
    vendor = SKILL_ROOT / "assets" / "families"

    def tree(root: Path) -> dict[str, bytes]:
        return {
            path.relative_to(root).as_posix(): path.read_bytes()
            for path in root.rglob("*")
            if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc"
        }

    compared = 0
    for family, (builder, consultant) in FAMILIES.items():
        for role, skill_name in (("builder", builder), ("consultant", consultant)):
            accepted = tree(REPO_ROOT / "skills" / skill_name)
            packaged = tree(vendor / family / role)
            assert packaged == accepted, (family, role)
            compared += len(accepted)
    assert compared >= 200


def test_generated_query_contract_matches_registry_and_all_cli_shapes() -> None:
    query = _load_query_template()
    sys.path.insert(0, str(SCRIPTS))
    try:
        import _family_registry

        assert query.FAMILY_CONTRACTS == {
            family: selected.as_manifest()
            for family, selected in _family_registry.PROFILES.items()
        }
    finally:
        sys.path.remove(str(SCRIPTS))

    contracts = query.FAMILY_CONTRACTS
    common = {
        "query": "graph evidence",
        "top_k": 7,
        "source_ids": (),
        "concept_ids": (),
        "concept_types": (),
        "allow_fallback": False,
    }
    legacy = query._native_search_arguments(contracts["legacy"], mode="ledger", **common)
    assert legacy[1:3] == ["ledger", "--contains"]
    assert legacy[-2:] == ["--format", "json"]
    embeddings = query._native_search_arguments(contracts["embeddings"], mode="hybrid", **common)
    assert embeddings[1:7] == ["search", "--query", "graph evidence", "--mode", "hybrid", "--top-k"]
    ensemble = query._native_search_arguments(contracts["ensemble"], mode="quality", **common)
    assert ensemble[4:6] == ["--policy", "quality"]
    graphify = query._native_search_arguments(contracts["graphify"], mode="graphify", **common)
    assert graphify[0:2] == ["--format", "json"]
    assert graphify[-1] == "--show-content"
    turso = query._native_search_arguments(contracts["turso"], mode="records", **common)
    assert turso[1:3] == ["records", "--contains"]
    assert query._require_search_citations({"hits": [{"citation": "references/x"}]}) == 1
    with pytest.raises(query.ExpertQueryError):
        query._require_search_citations({"results": [{}]})


def test_runtime_smoke_accepts_closed_json_and_graphify_text_contracts(
    tmp_path: Path,
) -> None:
    path = SCRIPTS / "runtime_smoke.py"
    specification = importlib.util.spec_from_file_location(
        "test_family_generator_runtime_smoke",
        path,
    )
    assert specification and specification.loader
    module = importlib.util.module_from_spec(specification)
    sys.path.insert(0, str(SCRIPTS))
    try:
        specification.loader.exec_module(module)
    finally:
        sys.path.remove(str(SCRIPTS))

    passing_json = tmp_path / "passing_json.py"
    passing_json.write_text(
        'print("{\\\"status\\\": \\\"pass\\\", \\\"runtime\\\": \\\"fixture\\\"}")\n',
        encoding="utf-8",
    )
    passing_text = tmp_path / "passing_text.py"
    passing_text.write_text(
        'print("graphifyy 0.9.17: pass; mode=markdown-structural-no-llm")\n',
        encoding="utf-8",
    )
    unknown = tmp_path / "unknown.py"
    unknown.write_text('print("dependency looks fine")\n', encoding="utf-8")

    assert module._smoke(passing_json)["runtime"] == "fixture"
    assert module._smoke(passing_text)["status"] == "pass"
    with pytest.raises(RuntimeError, match="unknown payload"):
        module._smoke(unknown)


def test_build_validate_check_search_get_and_copy_portability(tmp_path: Path) -> None:
    manifest, guidance = _write_fixture(tmp_path)
    output = tmp_path / "retrieval-family-expert"
    build = _run(*_build_arguments(manifest, guidance, output))
    assert build.returncode == 0, build.stderr or build.stdout
    result = json.loads(build.stdout)
    assert result["status"] == "pass"
    assert result["family"] == "legacy"
    assert result["record_count"] == 2
    assert result["concept_layout"] == "source-packed-v1"
    assert (output / "references/knowledge/concepts/documents.md").is_file()
    assert not (output / "assets").exists()
    assert not any("build_semantic" in path.name for path in (output / "scripts").rglob("*.py"))

    before = _tree_bytes(output)
    validation = _run(VALIDATE, output, "--deep-validation", cwd=tmp_path)
    assert validation.returncode == 0, validation.stdout
    assert json.loads(validation.stdout)["valid"] is True
    check = _run(*_build_arguments(manifest, guidance, output), "--check", cwd=tmp_path)
    assert check.returncode == 0, check.stderr or check.stdout
    assert json.loads(check.stdout)["mode"] == "check"
    assert _tree_bytes(output) == before

    helper = output / "scripts/query_expert_knowledge.py"
    search = _run(helper, "search", "--query", "graph", "--top-k", "2", cwd=tmp_path)
    assert search.returncode == 0, search.stdout
    payload = json.loads(search.stdout)
    assert payload["expert"]["family"] == "legacy"
    assert payload["records"]
    for hit in payload["records"]:
        assert hit["physical_concept_path"] == "concepts/documents.md"
        assert hit["evidence_anchor"].startswith("record-")
        assert hit["citation"].startswith("references/knowledge/concepts/documents.md#")

    first = payload["records"][0]
    exact = _run(
        helper,
        "get",
        "--source-id",
        first["source_id"],
        "--record-id",
        first["record_id"],
        "--show-content",
        cwd=tmp_path,
    )
    assert exact.returncode == 0, exact.stdout
    record = json.loads(exact.stdout)["record"]
    assert record["body"]
    assert record["citation"] == first["citation"]
    assert _tree_bytes(output) == before

    portable_parent = tmp_path / "portable"
    portable_parent.mkdir()
    portable = portable_parent / output.name
    shutil.copytree(output, portable)
    copied = _run(VALIDATE, portable, "--deep-validation", cwd=portable_parent)
    assert copied.returncode == 0, copied.stdout
    assert json.loads(copied.stdout)["valid"] is True


def test_copied_generator_builds_without_repository_or_sibling_skills(
    tmp_path: Path,
) -> None:
    copied_generator = tmp_path / "copied-generator"
    shutil.copytree(
        SKILL_ROOT,
        copied_generator,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
    )
    smoke = _run(
        copied_generator / "scripts" / "runtime_smoke.py",
        "--family",
        "legacy",
        cwd=tmp_path,
    )
    assert smoke.returncode == 0, smoke.stderr or smoke.stdout
    assert json.loads(smoke.stdout)["status"] == "pass"

    fixture = tmp_path / "portable-fixture"
    fixture.mkdir()
    manifest, guidance = _write_fixture(fixture)
    output = tmp_path / "portable-generator-expert"
    arguments = _build_arguments(manifest, guidance, output)
    arguments[0] = copied_generator / "scripts" / BUILD.name
    built = _run(*arguments, cwd=tmp_path)

    assert built.returncode == 0, built.stderr or built.stdout
    assert json.loads(built.stdout)["status"] == "pass"
    assert (output / "references/knowledge/semantic/records.jsonl").is_file()


def test_plan_contract_and_tampering_fail_closed(tmp_path: Path) -> None:
    manifest, guidance = _write_fixture(tmp_path)
    missing_plan = tmp_path / "missing-plan-expert"
    failed = _run(
        BUILD,
        manifest,
        missing_plan,
        "--family",
        "embeddings",
        "--name",
        missing_plan.name,
        "--description",
        "Answer only from bundled embedding knowledge with exact evidence.",
        "--guidance",
        guidance,
        "--output-format",
        "json",
    )
    assert failed.returncode == 2
    assert "requires --plan" in json.loads(failed.stdout)["error"]
    assert not missing_plan.exists()

    output = tmp_path / "tamper-evidence-expert"
    built = _run(*_build_arguments(manifest, guidance, output))
    assert built.returncode == 0, built.stdout
    (output / "references/guidance.md").write_text(
        (output / "references/guidance.md").read_text(encoding="utf-8") + "\nTampered.\n",
        encoding="utf-8",
    )
    validation = _run(VALIDATE, output, cwd=tmp_path)
    assert validation.returncode == 2
    error = json.loads(validation.stdout)
    assert error["valid"] is False
    assert "drift" in error["errors"][0]["message"]


def test_canonical_multi_family_parity_report_is_complete_and_passing() -> None:
    report = json.loads(PARITY_REPORT.read_text(encoding="utf-8"))
    assert report["schema_version"] == (
        "integrated-semantic-okf-knowledge-skill-comparison/1.0"
    )
    assert report["status"] == "pass"
    rows = report["datasets"]
    assert len(rows) == 24
    assert {(row["dataset_id"], row["family"]) for row in rows} == {
        (dataset, family)
        for dataset in (
            "astro-40",
            "graphrag-papers-40",
            "quantum-error-correction-papers-40",
        )
        for family in FAMILIES
    }
    for row in rows:
        assert row["question_count"] == 40
        assert row["knowledge_bytes_equal"] is True
        assert row["consultation_bytes_equal"] is True
        assert row["native_payload_equal"] is True
        assert row["facade_payload_equal_before_enrichment"] is True
        assert row["default_query_hits"] > 0
        assert row["verified_hit_citations"] == row["default_query_hits"]
        assert row["exact_get_verified"] is True
    totals = report["totals"]
    assert totals["dataset_count"] == 3
    assert totals["family_count"] == 8
    assert totals["dataset_family_cells"] == 24
    assert totals["bound_question_cells"] == 960
    assert totals["authoritative_record_instances"] == 10_440
    assert totals["native_query_probe_cells"] == 24
    assert totals["facade_query_probe_cells"] == 24
    assert totals["exact_get_cells"] == 24
    assert totals["verified_hit_citations"] == totals["returned_hits"]
    assert totals["knowledge_mismatches"] == 0
    assert totals["consultation_mismatches"] == 0
    assert totals["native_payload_mismatches"] == 0
    assert totals["facade_payload_mismatches"] == 0
    assert "not a new model-judged Harbor" in report["boundary"]
