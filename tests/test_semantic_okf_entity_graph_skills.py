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
