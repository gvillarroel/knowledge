from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path
from types import ModuleType

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = REPO_ROOT / "skills" / "build-semantic-okf-classical"
SCRIPTS = SKILL_ROOT / "scripts"
BUILD = SCRIPTS / "build_semantic_okf_classical.py"
VALIDATE = SCRIPTS / "validate_semantic_okf_classical.py"


def write_fixture(root: Path) -> tuple[Path, Path]:
    sources = root / "sources"
    sources.mkdir(parents=True)
    (sources / "alpha.md").write_text(
        "---\ntitle: Alpha Graph Note\ncode: A-1\n---\n\n"
        "# Alpha Graph Note\n\n"
        "Graph retrieval connects entities, relations, paths, and grounded evidence. "
        "Community summaries organize global themes while source passages preserve citations.\n",
        encoding="utf-8",
    )
    (sources / "beta.md").write_text(
        "---\ntitle: Beta Retrieval Note\ncode: B-1\n---\n\n"
        "# Beta Retrieval Note\n\n"
        "Lexical ranking finds exact terminology. Topic analysis expands related queries, "
        "and association statistics connect recurring concepts for diverse retrieval.\n",
        encoding="utf-8",
    )
    (sources / "auxiliary.md").write_text(
        "---\ntitle: Auxiliary Note\ncode: X-1\n---\n\n"
        "# Auxiliary Note\n\nThis authority is intentionally excluded from retrieval.\n",
        encoding="utf-8",
    )
    manifest = {
        "schema_version": "1.0",
        "bundle": {
            "title": "Classical retrieval fixture",
            "description": "A deterministic fixture for classical retrieval tests.",
            "base_iri": "https://example.org/classical-fixture/",
            "ontology_iri": "https://example.org/ontology/classical-fixture",
            "version_iri": "https://example.org/ontology/classical-fixture/1.0.0",
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
                "message": "Every document requires a reviewed code.",
                "basis": {"kind": "operational-policy", "references": ["FIXTURE-1"]},
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
            for source_id in ("alpha", "auxiliary", "beta")
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
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    plan_path.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
    return manifest_path, plan_path


def run_build(manifest: Path, plan: Path, output: Path) -> subprocess.CompletedProcess[str]:
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
        timeout=90,
        check=False,
    )


def tree_hashes(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def load_retrieval_module() -> ModuleType:
    sys.path.insert(0, str(SCRIPTS))
    try:
        name = "test_classical_retrieval_builder"
        spec = importlib.util.spec_from_file_location(name, SCRIPTS / "_classical_retrieval.py")
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
        return module
    finally:
        sys.path.remove(str(SCRIPTS))


def test_skill_metadata_and_standalone_boundary_are_complete() -> None:
    skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
    metadata = yaml.safe_load(skill.split("---", 2)[1])

    assert set(metadata) == {"name", "description"}
    assert metadata["name"] == "build-semantic-okf-classical"
    assert "## Standalone and authority boundary" in skill
    assert "non-authoritative" in skill
    assert "$build-semantic-okf-classical" in (
        SKILL_ROOT / "agents" / "openai.yaml"
    ).read_text(encoding="utf-8")
    assert "TODO" not in "\n".join(
        path.read_text(encoding="utf-8")
        for path in SKILL_ROOT.rglob("*")
        if path.is_file() and path.suffix in {".md", ".py", ".yaml"}
    )
    assert not any("embeddings" in path.name for path in SKILL_ROOT.rglob("*"))
    assert (SKILL_ROOT / "references" / "classical-plan.md").is_file()
    assert (SKILL_ROOT / "references" / "classical-format.md").is_file()


def test_plan_parser_is_closed_and_rejects_duplicate_keys(tmp_path: Path) -> None:
    module = load_retrieval_module()
    _, plan_path = write_fixture(tmp_path)
    plan = module.load_plan(plan_path)

    assert plan.source_ids == ("alpha", "beta")
    assert plan.raw["reranking"]["max_per_evidence_identity"] == 1
    plan_path.write_text(
        '{"schema_version":"1.0","schema_version":"1.0"}', encoding="utf-8"
    )
    with pytest.raises(module.ClassicalError, match="duplicate member 'schema_version'"):
        module.load_plan(plan_path)


@pytest.mark.parametrize(
    ("path", "value", "message"),
    [
        (("bm25", "b"), 1.1, "plan.bm25.b"),
        (("topics", "topic_count"), 1, "topic_count"),
        (("associations", "max_vocabulary"), 31, "max_vocabulary"),
        (("reranking", "candidate_pool"), True, "candidate_pool"),
    ],
)
def test_plan_rejects_out_of_contract_parameters(
    tmp_path: Path, path: tuple[str, str], value: object, message: str
) -> None:
    module = load_retrieval_module()
    _, plan_path = write_fixture(tmp_path)
    payload = json.loads(plan_path.read_text(encoding="utf-8"))
    payload[path[0]][path[1]] = value
    plan_path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(module.ClassicalError, match=message):
        module.load_plan(plan_path)


def test_atomic_build_is_deterministic_and_excludes_auxiliary_source(tmp_path: Path) -> None:
    manifest, plan = write_fixture(tmp_path)
    first = tmp_path / "bundle-a"
    second = tmp_path / "bundle-b"

    first_run = run_build(manifest, plan, first)
    second_run = run_build(manifest, plan, second)

    assert first_run.returncode == second_run.returncode == 0, first_run.stdout + first_run.stderr
    first_report = json.loads(first_run.stdout)
    assert first_report["status"] == "pass"
    assert first_report["summary"]["inputs"] == 2
    assert first_report["summary"]["records"] == 2
    assert first_report["summary"]["documents"] == 2
    assert first_report["summary"]["topics"] == 3
    assert first_report["selection"]["eligible_source_ids"] == ["alpha", "beta"]
    assert first_report["selection"]["excluded_source_ids"] == ["auxiliary"]
    assert tree_hashes(first) == tree_hashes(second)
    assert {path.name for path in (first / "classical").iterdir()} == {
        "index.json",
        "documents.jsonl",
        "lexicon.json",
        "associations.jsonl",
        "topics.json",
        "build-report.json",
    }
    index = json.loads((first / "classical" / "index.json").read_text(encoding="utf-8"))
    assert index["authoritative"] is False
    assert set(index["algorithms"]) == {
        "bm25",
        "associations",
        "topics",
        "topic_scoring",
        "association_scoring",
        "fusion",
        "reranking",
    }
    assert "auxiliary" not in (first / "classical" / "documents.jsonl").read_text(
        encoding="utf-8"
    )


def test_validator_rederives_artifacts_and_rejects_tampering(tmp_path: Path) -> None:
    manifest, plan = write_fixture(tmp_path)
    bundle = tmp_path / "bundle"
    completed = run_build(manifest, plan, bundle)
    assert completed.returncode == 0, completed.stdout + completed.stderr

    passing = subprocess.run(
        [sys.executable, str(VALIDATE), str(bundle), "--output-format", "json"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=60,
        check=False,
    )
    assert passing.returncode == 0
    assert json.loads(passing.stdout)["valid"] is True

    documents_path = bundle / "classical" / "documents.jsonl"
    rows = [json.loads(line) for line in documents_path.read_text(encoding="utf-8").splitlines()]
    rows[0]["body_terms"]["invented"] = 1
    documents_path.write_text(
        "".join(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n" for row in rows),
        encoding="utf-8",
    )
    failing = subprocess.run(
        [sys.executable, str(VALIDATE), str(bundle), "--output-format", "json"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=60,
        check=False,
    )
    result = json.loads(failing.stdout)
    assert failing.returncode == 2
    assert result["valid"] is False
    assert "deterministic authoritative derivation" in result["errors"][0]["message"]


def test_invalid_plan_leaves_no_output_or_candidate(tmp_path: Path) -> None:
    manifest, plan = write_fixture(tmp_path)
    payload = json.loads(plan.read_text(encoding="utf-8"))
    payload["reranking"]["relevance_weight"] = 0.9
    plan.write_text(json.dumps(payload), encoding="utf-8")
    output = tmp_path / "not-published"

    completed = run_build(manifest, plan, output)

    assert completed.returncode == 2
    assert json.loads(completed.stdout)["code"] == "classical-error"
    assert not output.exists()
    assert not list(tmp_path.glob(".not-published.classical-candidate-*"))
