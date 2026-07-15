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
SKILL_ROOT = REPO_ROOT / "skills" / "build-semantic-okf-adaptive"
SCRIPTS = SKILL_ROOT / "scripts"
BUILD = SCRIPTS / "build_semantic_okf_adaptive.py"
VALIDATE = SCRIPTS / "validate_semantic_okf_adaptive.py"


def write_fixture(root: Path) -> tuple[Path, Path]:
    sources = root / "sources"
    sources.mkdir(parents=True)
    (sources / "alpha.md").write_text(
        "---\ntitle: Release 2024.12345v1 Alpha Graph Note\ncode: A-1\n---\n\n"
        "# Release 2024.12345v1 Alpha Graph Note\n\n## PDF page 1\n\n"
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
            "title": "Adaptive retrieval fixture",
            "description": "A deterministic fixture for adaptive retrieval tests.",
            "base_iri": "https://example.org/adaptive-fixture/",
            "ontology_iri": "https://example.org/ontology/adaptive-fixture",
            "version_iri": "https://example.org/ontology/adaptive-fixture/1.0.0",
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
        "schema_version": "1.1",
        "selection": {"source_ids": ["alpha", "beta"]},
        "passages": {
            "default_mode": "full-record",
            "markdown_pdf_page_source_ids": [],
        },
        "evidence_identity": {
            "default_mode": "source-record",
            "paper_ids_by_source": {},
        },
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
        "adaptive": {
            "maximum_aspects": 8,
            "minimum_aspect_tokens": 4,
            "full_query_weight": 2.0,
            "aspect_weight": 0.25,
            "best_aspect_weight": 0.0,
            "rrf_k": 0,
            "protected_full_results": 9,
            "maximum_novel_aspect_rank": 1,
        },
    }
    manifest_path = root / "manifest.json"
    plan_path = root / "adaptive-plan.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    plan_path.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
    return manifest_path, plan_path


def write_evidence_fixture(root: Path) -> tuple[Path, Path]:
    """Write one paper and reviewed claim with an exact PDF-page binding."""

    manifest_path, plan_path = write_fixture(root)
    (root / "sources" / "alpha.md").write_text(
        "---\ntitle: Alpha Evidence Paper\ncode: A-1\n---\n\n"
        "# Alpha Evidence Paper\n\n## PDF page 1\n\nIntroductory context.\n\n"
        "## PDF page 2\n\nVerified graph evidence connects entities and relations.\n",
        encoding="utf-8",
    )
    (root / "sources" / "alpha-claims.jsonl").write_text(
        json.dumps(
            {
                "id": "claim-alpha-001",
                "title": "Alpha reviewed graph claim",
                "evidence_locator": "sources/alpha.md#PDF-page-2",
                "interpretation": "The reviewed mechanism connects entities and relations.",
                "review_state": "reviewed",
            },
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["ontology"]["classes"].append(
        {"name": "PaperSemanticClaim", "label": "paper semantic claim"}
    )
    manifest["ontology"]["properties"].extend(
        [
            {
                "name": name,
                "kind": "datatype",
                "domain": "PaperSemanticClaim",
                "range": "xsd:string",
            }
            for name in ("evidenceLocator", "interpretation", "reviewState")
        ]
    )
    manifest["sources"] = [
        source for source in manifest["sources"] if source["id"] == "alpha"
    ]
    manifest["sources"].append(
        {
            "id": "alpha-claims",
            "kind": "json",
            "path": "sources/alpha-claims.jsonl",
            "concept_type": "Paper Semantic Claim",
            "ontology_class": "PaperSemanticClaim",
            "id_field": "id",
            "title_field": "title",
            "schema": {
                "id": "string",
                "title": "string",
                "evidence_locator": "string",
                "interpretation": "string",
                "review_state": "string",
            },
            "fields": {
                "evidence_locator": "evidenceLocator",
                "interpretation": "interpretation",
                "review_state": "reviewState",
            },
        }
    )
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    plan["selection"]["source_ids"] = ["alpha", "alpha-claims"]
    plan["passages"]["markdown_pdf_page_source_ids"] = ["alpha"]
    plan["evidence_identity"]["paper_ids_by_source"] = {
        "alpha": "2024.12345v1",
        "alpha-claims": "2024.12345v1",
    }
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
        name = "test_adaptive_retrieval_builder"
        spec = importlib.util.spec_from_file_location(name, SCRIPTS / "_adaptive_retrieval.py")
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
    assert metadata["name"] == "build-semantic-okf-adaptive"
    assert "## Standalone authority boundary" in skill
    assert "non-authoritative" in skill
    assert "$build-semantic-okf-adaptive" in (
        SKILL_ROOT / "agents" / "openai.yaml"
    ).read_text(encoding="utf-8")
    assert "TODO" not in "\n".join(
        path.read_text(encoding="utf-8")
        for path in SKILL_ROOT.rglob("*")
        if path.is_file() and path.suffix in {".md", ".py", ".yaml"}
    )
    assert not any("embeddings" in path.name for path in SKILL_ROOT.rglob("*"))
    assert (SKILL_ROOT / "references" / "adaptive-plan.md").is_file()
    assert (SKILL_ROOT / "references" / "adaptive-format.md").is_file()


def test_plan_parser_is_closed_and_rejects_duplicate_keys(tmp_path: Path) -> None:
    module = load_retrieval_module()
    _, plan_path = write_fixture(tmp_path)
    plan = module.load_plan(plan_path)

    assert plan.source_ids == ("alpha", "beta")
    assert plan.raw["reranking"]["max_per_evidence_identity"] == 1
    assert plan.raw["adaptive"]["protected_full_results"] == 9
    assert plan.raw["adaptive"]["maximum_novel_aspect_rank"] == 1
    plan_path.write_text(
        '{"schema_version":"1.1","schema_version":"1.1"}', encoding="utf-8"
    )
    with pytest.raises(module.AdaptiveError, match="duplicate member 'schema_version'"):
        module.load_plan(plan_path)


def test_adaptive_plan_schema_matches_consultant_validator(tmp_path: Path) -> None:
    builder = load_retrieval_module()
    _, plan_path = write_fixture(tmp_path)
    sys.path.insert(0, str(REPO_ROOT / "skills" / "consult-semantic-okf-adaptive" / "scripts"))
    try:
        name = "test_adaptive_plan_consultant"
        path = REPO_ROOT / "skills" / "consult-semantic-okf-adaptive" / "scripts" / "_adaptive_snapshot.py"
        spec = importlib.util.spec_from_file_location(name, path)
        assert spec and spec.loader
        consultant = importlib.util.module_from_spec(spec)
        sys.modules[name] = consultant
        spec.loader.exec_module(consultant)
    finally:
        sys.path.pop(0)

    raw = builder.load_plan(plan_path).raw
    assert consultant._validate_plan(raw) == raw
    assert builder.PLAN_KEYS == consultant.PLAN_KEYS


@pytest.mark.parametrize(
    ("path", "value", "message"),
    [
        (("bm25", "b"), 1.1, "plan.bm25.b"),
        (("topics", "topic_count"), 1, "topic_count"),
        (("associations", "max_vocabulary"), 31, "max_vocabulary"),
        (("reranking", "candidate_pool"), True, "candidate_pool"),
        (("adaptive", "minimum_aspect_tokens"), 1, "minimum_aspect_tokens"),
        (("adaptive", "maximum_novel_aspect_rank"), 0, "maximum_novel_aspect_rank"),
        (("adaptive", "maximum_novel_aspect_rank"), True, "maximum_novel_aspect_rank"),
        (("adaptive", "maximum_novel_aspect_rank"), 1001, "maximum_novel_aspect_rank"),
        (("passages", "default_mode"), "implicit", "default_mode"),
        (("evidence_identity", "default_mode"), "record-only", "default_mode"),
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

    with pytest.raises(module.AdaptiveError, match=message):
        module.load_plan(plan_path)


def test_plan_rejects_unselected_or_invalid_paper_identity_mapping(tmp_path: Path) -> None:
    module = load_retrieval_module()
    _, plan_path = write_fixture(tmp_path)
    payload = json.loads(plan_path.read_text(encoding="utf-8"))
    payload["evidence_identity"]["paper_ids_by_source"] = {
        "auxiliary": "2024.12345v1"
    }
    plan_path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(module.AdaptiveError, match="selected sources"):
        module.load_plan(plan_path)

    payload["evidence_identity"]["paper_ids_by_source"] = {
        "alpha": "Release 2024.12345v1"
    }
    plan_path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(module.AdaptiveError, match="canonical versioned arXiv IDs"):
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
    assert {path.name for path in (first / "adaptive").iterdir()} == {
        "index.json",
        "documents.jsonl",
        "answer-bindings.jsonl",
        "lexicon.json",
        "associations.jsonl",
        "topics.json",
        "build-report.json",
    }
    index = json.loads((first / "adaptive" / "index.json").read_text(encoding="utf-8"))
    assert index["authoritative"] is False
    documents = [
        json.loads(line)
        for line in (first / "adaptive" / "documents.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    alpha = next(row for row in documents if row["source_id"] == "alpha")
    assert alpha["paper_id"] is None
    assert alpha["locator"] == {"kind": "record"}
    assert set(index["algorithms"]) == {
        "bm25",
        "associations",
        "topics",
        "topic_scoring",
        "association_scoring",
        "fusion",
        "reranking",
        "adaptive",
        "evidence_adapter",
        "answer_evidence_adapter",
        "answer_evidence_ranking",
    }
    assert "auxiliary" not in (first / "adaptive" / "documents.jsonl").read_text(
        encoding="utf-8"
    )


def test_builder_persists_only_verified_reviewed_answer_bindings(tmp_path: Path) -> None:
    manifest, plan = write_evidence_fixture(tmp_path)
    bundle = tmp_path / "evidence-bundle"

    completed = run_build(manifest, plan, bundle)

    assert completed.returncode == 0, completed.stdout + completed.stderr
    bindings = [
        json.loads(line)
        for line in (bundle / "adaptive" / "answer-bindings.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
    ]
    assert len(bindings) == 1
    binding = bindings[0]
    assert binding["record_id"] == "claim-alpha-001"
    assert binding["paper_id"] == "2024.12345v1"
    assert binding["concept_type"] == "Paper Semantic Claim"
    assert binding["source_path"] == "sources/alpha-claims.jsonl"
    assert binding["evidence_paths"] == ["sources/alpha.md"]
    assert binding["locator_tokens"] == ["PDF-page-2"]
    assert binding["citation_pages"] == [2]
    assert binding["authoritative_text"] == (
        "The reviewed mechanism connects entities and relations."
    )
    assert binding["authoritative_text_sha256"] == hashlib.sha256(
        binding["authoritative_text"].encode("utf-8")
    ).hexdigest()
    report = json.loads(completed.stdout)
    assert report["summary"]["answer_bindings"] == 1


def test_builder_skips_reviewed_locator_whose_authoritative_page_does_not_exist(
    tmp_path: Path,
) -> None:
    manifest, plan = write_evidence_fixture(tmp_path)
    claim_path = tmp_path / "sources" / "alpha-claims.jsonl"
    claim = json.loads(claim_path.read_text(encoding="utf-8"))
    claim["evidence_locator"] = "sources/alpha.md#PDF-page-99"
    claim_path.write_text(json.dumps(claim, sort_keys=True) + "\n", encoding="utf-8")
    bundle = tmp_path / "invalid-page-bundle"

    completed = run_build(manifest, plan, bundle)

    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert (bundle / "adaptive" / "answer-bindings.jsonl").read_text(
        encoding="utf-8"
    ) == ""
    assert json.loads(completed.stdout)["summary"]["answer_bindings"] == 0


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

    documents_path = bundle / "adaptive" / "documents.jsonl"
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


def test_validator_rejects_symlinked_authoritative_file(tmp_path: Path) -> None:
    manifest, plan = write_fixture(tmp_path)
    bundle = tmp_path / "bundle"
    completed = run_build(manifest, plan, bundle)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    records = bundle / "semantic" / "records.jsonl"
    external = tmp_path / "external-records.jsonl"
    records.replace(external)
    try:
        records.symlink_to(external)
    except OSError as exc:
        pytest.skip(f"symlink creation is unavailable: {exc}")

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
    assert "symlink or junction" in result["errors"][0]["message"]


def test_invalid_plan_leaves_no_output_or_candidate(tmp_path: Path) -> None:
    manifest, plan = write_fixture(tmp_path)
    payload = json.loads(plan.read_text(encoding="utf-8"))
    payload["reranking"]["relevance_weight"] = 0.9
    plan.write_text(json.dumps(payload), encoding="utf-8")
    output = tmp_path / "not-published"

    completed = run_build(manifest, plan, output)

    assert completed.returncode == 2
    assert json.loads(completed.stdout)["code"] == "adaptive-error"
    assert not output.exists()
    assert not list(tmp_path.glob(".not-published.adaptive-candidate-*"))


def test_broken_output_symlink_cannot_redirect_publication(tmp_path: Path) -> None:
    manifest, plan = write_fixture(tmp_path)
    external_target = tmp_path / "outside" / "published"
    output = tmp_path / "linked-output"
    try:
        output.symlink_to(external_target, target_is_directory=True)
    except OSError as exc:
        pytest.skip(f"symlink creation is unavailable: {exc}")

    completed = run_build(manifest, plan, output)

    assert completed.returncode == 2
    assert "symlink or junction" in json.loads(completed.stdout)["error"]
    assert output.is_symlink()
    assert not external_target.exists()
    assert not list(tmp_path.glob(".linked-output.adaptive-candidate-*"))
