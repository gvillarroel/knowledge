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
CORPUS_ROOT = REPO_ROOT / "evaluations" / "graphrag-cross-paper"
PLAN_TEMPLATE = REPO_ROOT / "evaluations" / "semantic-okf-entity-graph" / "entity-graph-plan.json"
BUILD_ROOT = REPO_ROOT / "skills" / "build-semantic-okf-entity-graph"
CONSULT_ROOT = REPO_ROOT / "skills" / "consult-semantic-okf-entity-graph"
BUILD_SCRIPTS = BUILD_ROOT / "scripts"
CONSULT_SCRIPTS = CONSULT_ROOT / "scripts"
BUILD = BUILD_SCRIPTS / "build_semantic_okf_entity_graph.py"
VALIDATE = BUILD_SCRIPTS / "validate_semantic_okf_entity_graph.py"
QUERY = CONSULT_SCRIPTS / "query_semantic_okf_entity_graph.py"
SELECTED_SOURCE_IDS = {
    "paper-2402-07630v3",
    "claims-2402-07630v3",
    "analysis-vocabulary",
}


def _canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _tree(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def _jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def _load_module(name: str, path: Path) -> ModuleType:
    sys.path.insert(0, str(path.parent))
    try:
        spec = importlib.util.spec_from_file_location(name, path)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
        return module
    finally:
        sys.path.remove(str(path.parent))


def _write_subset_fixture(root: Path) -> tuple[Path, Path]:
    manifest = json.loads((CORPUS_ROOT / "manifest.json").read_text(encoding="utf-8"))
    manifest["bundle"]["title"] = "Entity graph integration fixture"
    manifest["bundle"]["description"] = "One paper, its reviewed claims, and the declared vocabulary."
    manifest["sources"] = [
        source for source in manifest["sources"] if source["id"] in SELECTED_SOURCE_IDS
    ]
    assert {source["id"] for source in manifest["sources"]} == SELECTED_SOURCE_IDS
    for source in manifest["sources"]:
        source_path = Path(source["path"])
        target = root / source_path
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(CORPUS_ROOT / source_path, target)

    plan = json.loads(PLAN_TEMPLATE.read_text(encoding="utf-8"))
    plan["selection"] = {
        "paper_source_ids": ["paper-2402-07630v3"],
        "claim_source_ids": ["claims-2402-07630v3"],
        "vocabulary_source_id": "analysis-vocabulary",
    }
    manifest_path = root / "manifest.json"
    plan_path = root / "entity-graph-plan.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    plan_path.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
    return manifest_path, plan_path


def _write_generic_fixture(root: Path) -> tuple[Path, Path]:
    manifest = json.loads((CORPUS_ROOT / "manifest.json").read_text(encoding="utf-8"))
    manifest["bundle"].update(
        {
            "title": "Source-generic entity graph fixture",
            "description": "Two source identities, multiple Markdown records, and no paper metadata.",
            "base_iri": "https://example.org/entity-graph-generic/",
            "ontology_iri": "https://example.org/ontology/entity-graph-generic",
            "version_iri": "https://example.org/ontology/entity-graph-generic/2.0.0",
        }
    )
    source_template = {
        "kind": "markdown",
        "concept_type": "Technical Document",
        "ontology_class": "AnalysisTerm",
        "fields": {"title": "termLabel"},
    }
    manifest["sources"] = [
        {"id": "generic-a", "path": "sources/*.md", **source_template},
        {"id": "generic-b", "path": "sources/shared.md", **source_template},
    ]
    sources = root / "sources"
    sources.mkdir(parents=True, exist_ok=True)
    (sources / "shared.md").write_text(
        """---
title: Portable Routing Guide
---

# Portable Routing Guide

The island architecture routes UI components through explicit adapters.

## Endpoint adapters

Endpoint adapters preserve request context and deterministic route priority.

```md
## This fenced line is not a section
```

## Rendering boundaries

Rendering boundaries isolate server output from client hydration behavior.
""",
        encoding="utf-8",
    )
    (sources / "headerless.md").write_text(
        """---
title: Headerless Deployment Notes
---

Headerless deployment material still becomes exact bounded evidence. """
        + "Deterministic adapters preserve source identity across repeated records. " * 8,
        encoding="utf-8",
    )
    plan = {
        "schema_version": "2.0",
        "selection": {"source_ids": ["generic-a", "generic-b"]},
        "sectioning": {
            "strategy": "markdown-headings-or-bounded-record-v1",
            "maximum_characters": 160,
        },
        "tokenization": {
            "tokenizer": "ascii-alphanumeric-v1",
            "stopwords": "english-v1",
            "min_token_length": 2,
        },
        "extraction": {
            "ngram_range": [1, 3],
            "minimum_section_frequency": 1,
            "maximum_section_fraction": 1.0,
            "maximum_candidates": 200,
            "top_candidates_per_section": 12,
        },
        "bm25": {"k1": 1.2, "b": 0.75},
        "graph": {
            "max_co_mentions_per_section": 12,
            "minimum_co_mention_sections": 1,
            "max_co_mention_neighbors": 12,
            "max_edge_evidence_sections": 8,
        },
        "query": {
            "resolved_entities": 32,
            "max_hops": 3,
            "hop_decay": 0.65,
            "reviewed_edge_weight": 1.0,
            "candidate_edge_weight": 0.3,
            "mention_weight": 1.0,
            "candidate_pool": 150,
            "max_per_document": 2,
            "rrf_k": 60,
        },
    }
    manifest_path = root / "manifest.json"
    plan_path = root / "entity-graph-plan.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    plan_path.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
    return manifest_path, plan_path


def _run_build(manifest: Path, plan: Path, output: Path) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment.pop("PYTHONPATH", None)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run(
        [
            sys.executable,
            str(BUILD),
            str(manifest),
            str(plan),
            str(output),
            "--output-format",
            "json",
        ],
        cwd=manifest.parent,
        env=environment,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=120,
        check=False,
    )


def _run_query(bundle: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment.pop("PYTHONPATH", None)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run(
        [sys.executable, str(QUERY), str(bundle), *arguments],
        cwd=bundle.parent,
        env=environment,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=120,
        check=False,
    )


@pytest.fixture(scope="module")
def entity_graph_bundle(tmp_path_factory: pytest.TempPathFactory) -> Path:
    root = tmp_path_factory.mktemp("entity-graph-integration")
    manifest, plan = _write_subset_fixture(root)
    output = root / "bundle"
    completed = _run_build(manifest, plan, output)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    return output


@pytest.fixture(scope="module")
def generic_entity_graph_bundle(tmp_path_factory: pytest.TempPathFactory) -> Path:
    root = tmp_path_factory.mktemp("entity-graph-generic-integration")
    manifest, plan = _write_generic_fixture(root)
    output = root / "bundle"
    completed = _run_build(manifest, plan, output)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    return output


def test_skill_packages_are_standalone_closed_and_installable() -> None:
    for root, name in (
        (BUILD_ROOT, "build-semantic-okf-entity-graph"),
        (CONSULT_ROOT, "consult-semantic-okf-entity-graph"),
    ):
        skill = (root / "SKILL.md").read_text(encoding="utf-8")
        metadata = yaml.safe_load(skill.split("---", 2)[1])
        assert set(metadata) == {"name", "description"}
        assert metadata["name"] == name
        assert f"${name}" in (root / "agents" / "openai.yaml").read_text(encoding="utf-8")
        assert "TODO" not in "\n".join(
            path.read_text(encoding="utf-8")
            for path in root.rglob("*")
            if path.is_file() and path.suffix in {".md", ".py", ".yaml"}
        )
        assert (root / "scripts" / "runtime_smoke.py").is_file()
    assert "authoritative" in (BUILD_ROOT / "SKILL.md").read_text(encoding="utf-8")
    assert "read-only" in (CONSULT_ROOT / "SKILL.md").read_text(encoding="utf-8")
    assert (BUILD_SCRIPTS / "_entity_graph_model.py").read_bytes() == (
        CONSULT_SCRIPTS / "_entity_graph_model.py"
    ).read_bytes()


def test_closed_plan_rejects_duplicate_and_unknown_members(tmp_path: Path) -> None:
    model = _load_module("test_entity_graph_plan_model", BUILD_SCRIPTS / "_entity_graph_model.py")
    _, plan_path = _write_subset_fixture(tmp_path)
    plan = model.load_plan(plan_path)
    assert plan.paper_source_ids == ("paper-2402-07630v3",)
    assert plan.claim_source_ids == ("claims-2402-07630v3",)
    plan_path.write_text('{"schema_version":"1.0","schema_version":"1.0"}', encoding="utf-8")
    with pytest.raises(model.EntityGraphError, match="duplicate member 'schema_version'"):
        model.load_plan(plan_path)

    _, replacement = _write_subset_fixture(tmp_path / "unknown")
    value = json.loads(replacement.read_text(encoding="utf-8"))
    value["unexpected"] = True
    with pytest.raises(model.EntityGraphError, match="closed schema"):
        model.parse_plan(value)


def test_generic_plan_is_closed_and_uses_source_record_identity(tmp_path: Path) -> None:
    model = _load_module("test_entity_graph_generic_plan_model", BUILD_SCRIPTS / "_entity_graph_model.py")
    _, plan_path = _write_generic_fixture(tmp_path)
    plan = model.load_plan(plan_path)
    assert plan.schema_version == "2.0"
    assert plan.source_ids == ("generic-a", "generic-b")
    assert plan.paper_source_ids == plan.claim_source_ids == ()
    assert plan.vocabulary_source_id == ""

    value = json.loads(plan_path.read_text(encoding="utf-8"))
    value["selection"]["paper_source_ids"] = []
    with pytest.raises(model.EntityGraphError, match="closed schema"):
        model.parse_plan(value)
    value = json.loads(plan_path.read_text(encoding="utf-8"))
    value["sectioning"]["strategy"] = "pdf-page-headings-v1"
    with pytest.raises(model.EntityGraphError, match="markdown-headings-or-bounded-record-v1"):
        model.parse_plan(value)


def test_atomic_build_is_deterministic_and_projects_reviewed_and_candidate_graphs(
    tmp_path: Path,
) -> None:
    manifest, plan = _write_subset_fixture(tmp_path)
    first = tmp_path / "first"
    second = tmp_path / "second"
    first_run = _run_build(manifest, plan, first)
    second_run = _run_build(manifest, plan, second)
    assert first_run.returncode == second_run.returncode == 0, first_run.stdout + first_run.stderr
    assert _tree(first) == _tree(second)

    report = json.loads(first_run.stdout)
    assert report["status"] == "pass"
    assert report["valid"] is True
    assert report["summary"]["inputs"] == 3
    assert report["summary"]["sections"] > 10
    assert report["summary"]["reviewed_entities"] > 50
    assert report["summary"]["candidate_entities"] > 0
    assert report["summary"]["reviewed_edges"] > 0
    assert report["summary"]["candidate_edges"] > 0

    graph = first / "entity-graph"
    assert {path.name for path in graph.iterdir()} == {
        "index.json",
        "build-report.json",
        "entities.jsonl",
        "sections.jsonl",
        "mentions.jsonl",
        "edges.jsonl",
        "lexicon.json",
    }
    index = json.loads((graph / "index.json").read_text(encoding="utf-8"))
    assert index["authoritative"] is False
    assert index["discovery_only"] is True
    assert set(index["algorithms"]) == {
        "sectioning",
        "entity_extraction",
        "mention_matching",
        "reviewed_relations",
        "candidate_relations",
        "lexical_scoring",
        "entity_scoring",
        "graph_scoring",
        "fusion",
        "reranking",
    }
    entities = _jsonl(graph / "entities.jsonl")
    sections = _jsonl(graph / "sections.jsonl")
    edges = _jsonl(graph / "edges.jsonl")
    assert {entity["review_state"] for entity in entities} == {"reviewed", "candidate"}
    assert all(section["locator"]["kind"] == "character-range" for section in sections)
    assert all(
        hashlib.sha256(section["text"].encode()).hexdigest() == section["text_sha256"]
        for section in sections
    )
    assert any(edge["predicate"] == "supportedBySection" for edge in edges)
    assert any(
        edge["review_state"] == "reviewed" and len(edge["evidence_section_ids"]) > 1
        for edge in edges
    )
    assert any(edge["predicate"] == "coMentionedWith" for edge in edges)


def test_generic_build_is_deterministic_collision_safe_and_exact(tmp_path: Path) -> None:
    manifest, plan = _write_generic_fixture(tmp_path)
    first = tmp_path / "generic-first"
    second = tmp_path / "generic-second"
    first_run = _run_build(manifest, plan, first)
    second_run = _run_build(manifest, plan, second)
    assert first_run.returncode == second_run.returncode == 0, first_run.stdout + first_run.stderr
    assert _tree(first) == _tree(second)

    report = json.loads(first_run.stdout)
    assert report["schema_version"] == "2.0"
    assert report["summary"]["inputs"] == 2
    assert report["summary"]["selected_records"] == 3
    graph = first / "entity-graph"
    index = json.loads((graph / "index.json").read_text(encoding="utf-8"))
    assert index["selection"]["requested_source_ids"] == ["generic-a", "generic-b"]
    assert index["algorithms"]["sectioning"] == "markdown-atx-heading-or-bounded-record-character-range-v1"
    sections = _jsonl(graph / "sections.jsonl")
    records = {
        (record["source_id"], record["record_id"]): record
        for record in _jsonl(first / "semantic" / "records.jsonl")
    }
    assert len(sections) > len(records)
    assert all(len(section["text"]) <= 160 for section in sections)
    assert all("paper_id" not in section for section in sections)
    assert all(section["locator"]["target"] == "record-body" for section in sections)
    assert "This fenced line is not a section" not in {section["heading"] for section in sections}
    for section in sections:
        record = records[(section["source_id"], section["record_id"])]
        locator = section["locator"]
        assert record["body"][locator["start"] : locator["end"]] == section["text"]
        assert hashlib.sha256(section["text"].encode()).hexdigest() == section["text_sha256"]
        assert section["record_sha256"] == record["record_sha256"]
        assert section["source_content_sha256"] == record["source_content_sha256"]

    shared = [
        section
        for section in sections
        if section["record_id"].endswith("sources/shared") and section["ordinal"] == 0
    ]
    assert {section["source_id"] for section in shared} == {"generic-a", "generic-b"}
    assert len({section["document_id"] for section in shared}) == 2
    edges = _jsonl(graph / "edges.jsonl")
    assert {"partOfDocument", "mentionedInSection", "coMentionedWith"}.issubset(
        {edge["predicate"] for edge in edges}
    )


def test_invalid_plan_never_publishes_output_or_candidate(tmp_path: Path) -> None:
    manifest, plan = _write_subset_fixture(tmp_path)
    value = json.loads(plan.read_text(encoding="utf-8"))
    value["query"]["max_hops"] = 7
    plan.write_text(json.dumps(value), encoding="utf-8")
    output = tmp_path / "not-published"
    completed = _run_build(manifest, plan, output)
    assert completed.returncode == 2
    assert json.loads(completed.stdout)["code"] == "entity-graph-error"
    assert not output.exists()
    assert not list(tmp_path.glob(".not-published.entity-graph-candidate-*"))


def test_validator_rederives_projection_and_rejects_tampering(
    entity_graph_bundle: Path, tmp_path: Path
) -> None:
    passing = subprocess.run(
        [sys.executable, str(VALIDATE), str(entity_graph_bundle), "--output-format", "json"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=120,
        check=False,
    )
    assert passing.returncode == 0
    assert json.loads(passing.stdout)["valid"] is True

    changed = tmp_path / "changed"
    shutil.copytree(entity_graph_bundle, changed)
    sections_path = changed / "entity-graph" / "sections.jsonl"
    sections = _jsonl(sections_path)
    sections[0]["text"] += " tampered"
    sections_path.write_text("".join(_canonical(row) + "\n" for row in sections), encoding="utf-8")
    failing = subprocess.run(
        [sys.executable, str(VALIDATE), str(changed), "--output-format", "json"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=120,
        check=False,
    )
    result = json.loads(failing.stdout)
    assert failing.returncode == 2
    assert result["valid"] is False
    assert "section text digest" in result["errors"][0]["message"]


@pytest.mark.parametrize("mode", ["lexical", "entity", "traversal", "fusion"])
def test_all_query_routes_return_exact_sections_and_graph_explanations(
    entity_graph_bundle: Path, mode: str
) -> None:
    completed = _run_query(
        entity_graph_bundle,
        "search",
        "--query",
        "Prize-Collecting Steiner Tree relevant subgraph",
        "--mode",
        mode,
        "--top-k",
        "1",
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    result = json.loads(completed.stdout)
    assert result["status"] == "pass"
    assert result["requested_mode"] == result["effective_mode"] == mode
    assert result["authoritative"] is False
    assert result["discovery_only"] is True
    assert result["returned"] == 1
    hit = result["results"][0]
    assert hit["paper_id"] == "2402.07630v3"
    assert hit["locator"]["kind"] == "character-range"
    assert hashlib.sha256(hit["text"].encode()).hexdigest() == hit["text_sha256"]
    assert hit["supporting_edge_ids"]
    if mode in {"entity", "traversal", "fusion"}:
        claims = [
            entity
            for entity in result["resolved_entities"]
            if entity["entity_type"] == "claim" and entity["review_state"] == "reviewed"
        ]
        assert claims
        assert claims[0]["record_id"].startswith("claim-2402-07630v3-")
        assert claims[0]["concept_path"].startswith("concepts/claims-2402-07630v3/")
        assert claims[0]["claim_evidence"]


@pytest.mark.parametrize("mode", ["lexical", "entity", "traversal", "fusion"])
def test_generic_query_routes_return_exact_source_record_sections(
    generic_entity_graph_bundle: Path, mode: str
) -> None:
    completed = _run_query(
        generic_entity_graph_bundle,
        "search",
        "--query",
        "endpoint adapters deterministic route priority",
        "--mode",
        mode,
        "--top-k",
        "2",
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    result = json.loads(completed.stdout)
    assert result["schema_version"] == "2.0"
    assert result["requested_mode"] == result["effective_mode"] == mode
    assert result["returned"] >= 1
    for hit in result["results"]:
        assert hit["document_identity"] == {
            "kind": "source-record",
            "source_id": hit["source_id"],
            "record_id": hit["record_id"],
        }
        assert hit["concept_type"] == "Technical Document"
        assert hit["locator"]["target"] == "record-body"
        assert hashlib.sha256(hit["text"].encode()).hexdigest() == hit["text_sha256"]
        assert hit["supporting_edge_ids"]
        assert "paper_id" not in hit


def test_query_cache_preserves_payloads_and_invalidates_exact_context(
    generic_entity_graph_bundle: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runtime = _load_module(
        "test_entity_graph_query_cache",
        CONSULT_SCRIPTS / "_entity_graph_snapshot.py",
    )
    snapshot = runtime.load_snapshot(generic_entity_graph_bundle, deep_validation=True)
    query = "endpoint adapters deterministic route priority"
    modes = ("lexical", "entity", "traversal", "fusion")

    uncached: dict[str, dict[str, Any]] = {}
    for mode in modes:
        runtime._LAST_QUERY_CACHE = None
        uncached[mode] = runtime.search_snapshot(snapshot, query, mode, 3)
    runtime._LAST_QUERY_CACHE = None
    cached = {
        mode: runtime.search_snapshot(snapshot, query, mode, 3) for mode in modes
    }
    assert cached == uncached

    if cached["lexical"]["resolved_entities"]:
        cached["lexical"]["resolved_entities"][0]["matched_terms"].append(
            "caller-mutation"
        )
        repeated = runtime.search_snapshot(snapshot, query, "entity", 3)
        assert all(
            "caller-mutation" not in row["matched_terms"]
            for row in repeated["resolved_entities"]
        )

    original = runtime._compute_query
    calls: list[tuple[str, tuple[str, ...]]] = []

    def counted(active_snapshot, active_query, source_filter, *filters):
        calls.append((active_query, tuple(sorted(source_filter))))
        return original(
            active_snapshot,
            active_query,
            source_filter,
            *filters,
        )

    monkeypatch.setattr(runtime, "_compute_query", counted)
    runtime._LAST_QUERY_CACHE = None
    selected_sources = ["generic-a", "generic-b"]
    runtime.search_snapshot(
        snapshot, query, "lexical", 1, source_ids=selected_sources
    )
    runtime.search_snapshot(
        snapshot, query, "fusion", 10, source_ids=list(reversed(selected_sources))
    )
    assert len(calls) == 1

    runtime.search_snapshot(
        snapshot, query + " changed", "fusion", 3, source_ids=selected_sources
    )
    runtime.search_snapshot(
        snapshot, query + " changed", "fusion", 3, source_ids=["generic-a"]
    )
    second_snapshot = runtime.load_snapshot(
        generic_entity_graph_bundle, deep_validation=True
    )
    runtime.search_snapshot(
        second_snapshot,
        query + " changed",
        "fusion",
        3,
        source_ids=["generic-a"],
    )
    assert len(calls) == 4


def test_generic_filters_are_collision_safe_and_legacy_paper_filter_fails_closed(
    generic_entity_graph_bundle: Path,
) -> None:
    records = _jsonl(generic_entity_graph_bundle / "semantic" / "records.jsonl")
    shared_record_id = next(
        record["record_id"] for record in records if record["record_id"].endswith("sources/shared")
    )
    searched = _run_query(
        generic_entity_graph_bundle,
        "search",
        "--query",
        "rendering boundaries hydration",
        "--mode",
        "fusion",
        "--top-k",
        "10",
        "--record-id",
        shared_record_id,
    )
    assert searched.returncode == 0, searched.stdout + searched.stderr
    payload = json.loads(searched.stdout)
    assert payload["filters"]["record_ids"] == [shared_record_id]
    assert {hit["source_id"] for hit in payload["results"]} == {"generic-a", "generic-b"}
    assert all(hit["record_id"] == shared_record_id for hit in payload["results"])

    rejected = _run_query(
        generic_entity_graph_bundle,
        "search",
        "--query",
        "routing",
        "--paper-id",
        "invented-paper",
    )
    assert rejected.returncode == 2
    assert "legacy schema 1.0" in json.loads(rejected.stdout)["error"]


def test_consultation_is_read_only_and_deep_validation_rederives_everything(
    entity_graph_bundle: Path,
) -> None:
    before = _tree(entity_graph_bundle)
    inspected = _run_query(entity_graph_bundle, "inspect", "--deep-validation")
    searched = _run_query(
        entity_graph_bundle,
        "search",
        "--query",
        "graph retrieval",
        "--mode",
        "fusion",
        "--top-k",
        "1",
        "--paper-id",
        "2402.07630v3",
    )
    after = _tree(entity_graph_bundle)
    assert inspected.returncode == searched.returncode == 0
    inspection = json.loads(inspected.stdout)
    assert inspection["status"] == "pass"
    assert inspection["deep_validation"] is True
    assert json.loads(searched.stdout)["filters"]["paper_ids"] == ["2402.07630v3"]
    assert before == after


def test_generic_consultation_is_read_only_and_rejects_locator_tampering(
    generic_entity_graph_bundle: Path, tmp_path: Path
) -> None:
    before = _tree(generic_entity_graph_bundle)
    inspected = _run_query(generic_entity_graph_bundle, "inspect", "--deep-validation")
    after = _tree(generic_entity_graph_bundle)
    assert inspected.returncode == 0, inspected.stdout + inspected.stderr
    assert json.loads(inspected.stdout)["schema_version"] == "2.0"
    assert before == after

    changed = tmp_path / "generic-changed"
    shutil.copytree(generic_entity_graph_bundle, changed)
    sections_path = changed / "entity-graph" / "sections.jsonl"
    sections = _jsonl(sections_path)
    sections[0]["locator"]["target"] = "raw-source"
    sections_path.write_text("".join(_canonical(row) + "\n" for row in sections), encoding="utf-8")
    failing = subprocess.run(
        [sys.executable, str(VALIDATE), str(changed), "--output-format", "json"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=120,
        check=False,
    )
    result = json.loads(failing.stdout)
    assert failing.returncode == 2
    assert result["valid"] is False
    assert "locator target or kind" in result["errors"][0]["message"]


def test_runtime_smokes_run_without_repository_imports() -> None:
    environment = os.environ.copy()
    environment.pop("PYTHONPATH", None)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    for script in (BUILD_SCRIPTS / "runtime_smoke.py", CONSULT_SCRIPTS / "runtime_smoke.py"):
        completed = subprocess.run(
            [sys.executable, str(script)],
            cwd=script.parent,
            env=environment,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=30,
            check=False,
        )
        assert completed.returncode == 0, completed.stdout + completed.stderr
        assert "pass" in completed.stdout.casefold()
