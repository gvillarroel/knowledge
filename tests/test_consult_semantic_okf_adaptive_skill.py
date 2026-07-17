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
BUILD_ROOT = REPO_ROOT / "skills" / "build-semantic-okf-adaptive"
BUILD = BUILD_ROOT / "scripts" / "build_semantic_okf_adaptive.py"
SKILL_ROOT = REPO_ROOT / "skills" / "consult-semantic-okf-adaptive"
SCRIPTS = SKILL_ROOT / "scripts"
QUERY = SCRIPTS / "query_semantic_okf_adaptive.py"


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
    (sources / "catalog.csv").write_text(
        "id,title,code,notes\n"
        "entry-1,Gamma Renewal Matrix,G-1,renewal risk escalation evidence\n"
        "entry-2,Delta Renewal Matrix,D-1,renewal confidence verification evidence\n",
        encoding="utf-8",
    )
    (sources / "services.csv").write_text(
        "id,title,code,notes\n"
        "entry-1,Epsilon Renewal Service,E-1,renewal risk escalation evidence service boundary\n",
        encoding="utf-8",
    )
    manifest = {
        "schema_version": "1.0",
        "bundle": {
            "title": "Consult adaptive fixture",
            "description": "Two authorities for read-only adaptive retrieval tests.",
            "base_iri": "https://example.org/consult-adaptive/",
            "ontology_iri": "https://example.org/ontology/consult-adaptive",
            "version_iri": "https://example.org/ontology/consult-adaptive/1.0.0",
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
        ]
        + [
            {
                "id": "catalog",
                "kind": "csv",
                "path": "sources/catalog.csv",
                "concept_type": "Document",
                "ontology_class": "Document",
                "id_field": "id",
                "title_field": "title",
                "fields": {"code": "code"},
                "schema": {
                    "id": "string",
                    "title": "string",
                    "code": "string",
                    "notes": "string",
                },
                "options": {"header": "true", "enforceSchema": "false"},
            },
            {
                "id": "services",
                "kind": "csv",
                "path": "sources/services.csv",
                "concept_type": "Document",
                "ontology_class": "Document",
                "id_field": "id",
                "title_field": "title",
                "fields": {"code": "code"},
                "schema": {
                    "id": "string",
                    "title": "string",
                    "code": "string",
                    "notes": "string",
                },
                "options": {"header": "true", "enforceSchema": "false"},
            },
        ],
    }
    plan = {
        "schema_version": "1.1",
        "selection": {"source_ids": ["alpha", "beta", "catalog", "services"]},
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
    write_json(manifest_path, manifest)
    write_json(plan_path, plan)
    return manifest_path, plan_path


def write_evidence_fixture(root: Path) -> tuple[Path, Path]:
    """Extend the regular fixture with one verified reviewed claim."""

    manifest_path, plan_path = write_fixture(root)
    (root / "sources" / "alpha.md").write_text(
        "---\ntitle: Alpha Graph Note\ncode: ALPHA-1\n---\n\n"
        "# Alpha Graph Note\n\n## PDF page 1\n\nIntroductory context.\n\n"
        "## PDF page 2\n\nGraph evidence connects entities and relations.\n",
        encoding="utf-8",
    )
    (root / "sources" / "alpha-claims.jsonl").write_text(
        canonical_json(
            {
                "id": "claim-alpha-001",
                "title": "Reviewed graph evidence claim",
                "evidence_locator": "sources/alpha.md#PDF-page-2",
                "interpretation": "The reviewed mechanism connects entities and relations.",
                "review_state": "reviewed",
            }
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
    write_json(manifest_path, manifest)
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    plan["selection"]["source_ids"] = sorted(
        [*plan["selection"]["source_ids"], "alpha-claims"]
    )
    plan["passages"]["markdown_pdf_page_source_ids"] = ["alpha"]
    plan["evidence_identity"]["paper_ids_by_source"] = {
        "alpha": "2024.12345v1",
        "alpha-claims": "2024.12345v1",
    }
    write_json(plan_path, plan)
    return manifest_path, plan_path


@pytest.fixture(scope="module")
def bundle(tmp_path_factory: pytest.TempPathFactory) -> Path:
    root = tmp_path_factory.mktemp("consult-adaptive")
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


@pytest.fixture(scope="module")
def evidence_bundle(tmp_path_factory: pytest.TempPathFactory) -> Path:
    root = tmp_path_factory.mktemp("consult-adaptive-evidence")
    manifest, plan = write_evidence_fixture(root)
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


def run_query(
    bundle_path: Path,
    *args: str,
    input_text: str | None = None,
) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment.pop("PYTHONPATH", None)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run(
        [sys.executable, str(QUERY), str(bundle_path), *args],
        cwd=SKILL_ROOT,
        env=environment,
        capture_output=True,
        input=input_text,
        text=True,
        encoding="utf-8",
        timeout=60,
        check=False,
    )


def load_snapshot_module() -> ModuleType:
    name = "test_adaptive_snapshot"
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / "_adaptive_snapshot.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def test_skill_metadata_documents_and_runtime_are_standalone() -> None:
    skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
    metadata = yaml.safe_load(skill.split("---", 2)[1])

    assert set(metadata) == {"name", "description"}
    assert metadata["name"] == "consult-semantic-okf-adaptive"
    assert "## Standalone read-only boundary" in skill
    assert "## Response-contract adaptation" in skill
    assert "## Coverage closure" in skill
    assert "evidence ledger" in skill
    assert "#PDF-page-N" in skill
    assert "never place a `sources/...#PDF-page-N` string" in skill
    assert "--deep-validation" in skill
    assert "$consult-semantic-okf-adaptive" in (
        SKILL_ROOT / "agents" / "openai.yaml"
    ).read_text(encoding="utf-8")
    assert (SCRIPTS / "requirements.txt").read_text(encoding="utf-8").strip() == (
        "# No third-party packages are required."
    )
    source = (SCRIPTS / "_adaptive_snapshot.py").read_text(encoding="utf-8")
    assert "_adaptive_retrieval" not in source
    assert "sentence_transformers" not in source
    assert "openai" not in source.casefold()
    querying = (SKILL_ROOT / "references" / "querying.md").read_text(encoding="utf-8")
    assert "user's final response schema" in querying
    assert "evidence-to-citation page equality" in querying


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
    assert result["capabilities"] == [
        "bm25",
        "topic",
        "association",
        "fusion",
        "adaptive",
        "evidence_rows",
        "answer_evidence_pack",
        "facet_coverage_pack",
        "authoritative_answer_finalizer",
    ]
    assert before == after


@pytest.mark.parametrize("mode", ["bm25", "topic", "association", "fusion", "adaptive"])
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
    if mode == "adaptive":
        assert result["adaptive"]["algorithm"] == "protected-full-query-plus-aspect-rrf-v2"
    assert result["evidence_contract"] == {
        "adapter": "exact-authoritative-fields-v2",
        "copy_fields_only": True,
        "authoritative_verification_required": True,
        "locator_basis": "semantic/records.jsonl record.body",
    }
    assert len(result["evidence_rows"]) == len(result["results"])
    for hit, evidence in zip(result["results"], result["evidence_rows"]):
        assert evidence["rank"] == hit["rank"]
        for field in (
            "source_id",
            "paper_id",
            "record_id",
            "record_sha256",
            "concept_id",
            "concept_type",
            "concept_path",
            "source_path",
            "ordinal",
            "locator",
            "text",
            "text_sha256",
        ):
            assert evidence[field] == hit[field]
    if mode != "bm25":
        identities = [
            ("paper", hit["paper_id"])
            if hit["paper_id"]
            else ("source-record", hit["source_id"], hit["record_id"])
            for hit in result["results"]
        ]
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


def test_multirecord_source_uses_record_level_evidence_identity(bundle: Path) -> None:
    completed = run_query(
        bundle,
        "search",
        "--query",
        "renewal evidence matrix confidence risk",
        "--mode",
        "adaptive",
        "--top-k",
        "10",
        "--source-id",
        "catalog",
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr
    result = json.loads(completed.stdout)
    assert [row["source_id"] for row in result["results"]] == ["catalog", "catalog"]
    identities = [row["adaptive"]["evidence_identity"] for row in result["results"]]
    assert len(set(identities)) == 2
    assert set(identities) == {
        '["source-record","catalog","entry-1"]',
        '["source-record","catalog","entry-2"]',
    }


def test_duplicate_local_record_ids_remain_distinct_across_sources(bundle: Path) -> None:
    completed = run_query(
        bundle,
        "search",
        "--query",
        "renewal risk escalation evidence service boundary",
        "--mode",
        "adaptive",
        "--top-k",
        "10",
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr
    result = json.loads(completed.stdout)
    duplicate_rows = [row for row in result["results"] if row["record_id"] == "entry-1"]
    assert {(row["source_id"], row["record_id"]) for row in duplicate_rows} == {
        ("catalog", "entry-1"),
        ("services", "entry-1"),
    }
    assert len({row["adaptive"]["evidence_identity"] for row in duplicate_rows}) == 2


def test_pdf_page_passage_sources_must_be_markdown(tmp_path: Path) -> None:
    manifest, plan = write_fixture(tmp_path)
    payload = json.loads(plan.read_text(encoding="utf-8"))
    payload["passages"]["markdown_pdf_page_source_ids"] = ["services"]
    write_json(plan, payload)
    output = tmp_path / "invalid-page-kind"
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
        cwd=tmp_path,
        env=environment,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=90,
        check=False,
    )

    assert completed.returncode == 2
    assert "kind=markdown" in json.loads(completed.stdout)["error"]
    assert not output.exists()


def test_default_adaptive_mode_decomposes_query_and_copies_index_bindings(bundle: Path) -> None:
    before = tree_hashes(bundle)
    completed = run_query(
        bundle,
        "search",
        "--query",
        "Compare graph relations and contrast lexical ranking mechanisms; explain evidence citation boundaries.",
        "--top-k",
        "2",
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr
    result = json.loads(completed.stdout)
    assert result["requested_mode"] == result["effective_mode"] == "adaptive"
    assert result["adaptive"]["aspects"] == [
        "Compare graph relations and contrast lexical ranking mechanisms",
        "explain evidence citation boundaries",
    ]
    assert result["adaptive"]["protected_full_results"] == 2
    assert result["adaptive"]["maximum_novel_aspect_rank"] == 1
    assert result["evidence_rows"]
    assert all(
        row["adaptive_index_sha256"] == result["snapshot"]["adaptive_index_sha256"]
        and row["core_tree_sha256"] == result["snapshot"]["core_tree_sha256"]
        for row in result["evidence_rows"]
    )
    assert tree_hashes(bundle) == before


def test_evidence_pack_emits_distinct_locator_and_citation_types(
    evidence_bundle: Path,
) -> None:
    before = tree_hashes(evidence_bundle)

    completed = run_query(
        evidence_bundle,
        "evidence-pack",
        "--query",
        "How does graph evidence connect entities and relations?",
        "--top-k",
        "10",
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr
    result = json.loads(completed.stdout)
    assert result["status"] == "pass"
    assert result["algorithm"] == "dual-view-record-interpretation-fusion-v2"
    assert result["expansion"]["record_views"] == [
        {"view": "full-authoritative-record", "weight": 2.0},
        {"view": "reviewed-interpretation", "weight": 1.0},
    ]
    assert result["expansion"]["maximum_initial_claims_per_paper"] == 3
    assert result["returned"] == 1
    assert result["claim_evidence"] == [
        {
            "claim_id": "claim-alpha-001",
            "concept_path": result["ranked_bindings"][0]["concept_path"],
            "paper_id": "2024.12345v1",
            "source_path": "sources/alpha-claims.jsonl",
            "locators": ["PDF-page-2"],
        }
    ]
    assert result["citations"] == [
        {"paper_id": "2024.12345v1", "pages": [2]}
    ]
    assert all(isinstance(locator, str) for locator in result["claim_evidence"][0]["locators"])
    assert all(isinstance(page, int) for page in result["citations"][0]["pages"])
    assert result["ranked_bindings"][0]["authoritative_text"] == (
        "The reviewed mechanism connects entities and relations."
    )
    assert tree_hashes(evidence_bundle) == before


def test_coverage_pack_keeps_enumerated_facets_separate_and_read_only(
    evidence_bundle: Path,
) -> None:
    before = tree_hashes(evidence_bundle)
    completed = run_query(
        evidence_bundle,
        "coverage-pack",
        "--query",
        "Compare GraphRAG, lexical retrieval, and evidence citations; explain relation support.",
        "--top-k",
        "10",
        "--per-facet",
        "5",
        "--maximum-facets",
        "8",
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr
    result = json.loads(completed.stdout)
    assert result["algorithm"] == "enumeration-facet-separated-claim-ranking-v1"
    assert result["coverage_contract"]["ground_truth_inputs"] is False
    assert result["primary"]["algorithm"] == "dual-view-record-interpretation-fusion-v2"
    assert [row["facet"] for row in result["coverage_facets"]] == [
        "Compare GraphRAG",
        "lexical retrieval",
        "evidence citations",
        "explain relation support",
    ]
    assert any(row["candidates"] for row in result["coverage_facets"])
    assert all(row["returned"] == len(row["candidates"]) for row in result["coverage_facets"])
    assert all(
        list(candidate) == [
            "authoritative_text",
            "citation_pages",
            "claim_id",
            "concept_path",
            "locators",
            "paper_id",
            "rank",
            "source_path",
        ]
        for row in result["coverage_facets"]
        for candidate in row["candidates"]
    )
    assert tree_hashes(evidence_bundle) == before


def test_answer_finalizer_rebuilds_sorted_exact_evidence_and_preserves_key_order(
    evidence_bundle: Path, tmp_path: Path
) -> None:
    before = tree_hashes(evidence_bundle)
    summary = " ".join(["grounded"] * 180)
    draft = tmp_path / "draft.json"
    write_json(
        draft,
        {
            "summary": summary,
            "claims": [
                {
                    "statement": "Relations are connected by reviewed graph evidence.",
                    "supporting_claim_ids": [
                        "claim-alpha-001",
                        "claim-alpha-001",
                    ],
                }
            ],
        },
    )

    completed = run_query(
        evidence_bundle,
        "finalize-answer",
        "--draft",
        "-",
        "--question-id",
        "q-contract",
        input_text=draft.read_text(encoding="utf-8"),
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert completed.stdout.index('"question_id"') < completed.stdout.index('"answer"')
    assert completed.stdout.index('"answer"') < completed.stdout.index('"evidence"')
    result = json.loads(completed.stdout)
    assert list(result) == ["question_id", "answer", "evidence"]
    assert list(result["answer"]) == ["summary", "claims", "paper_ids", "citations"]
    assert result["answer"]["claims"] == [
        {
            "statement": "Relations are connected by reviewed graph evidence.",
            "supporting_claim_ids": ["claim-alpha-001"],
        }
    ]
    assert result["answer"]["paper_ids"] == ["2024.12345v1"]
    assert result["answer"]["citations"] == [
        {"paper_id": "2024.12345v1", "pages": [2]}
    ]
    assert result["evidence"] == [
        {
            "claim_id": "claim-alpha-001",
            "concept_path": result["evidence"][0]["concept_path"],
            "paper_id": "2024.12345v1",
            "source_path": "sources/alpha-claims.jsonl",
            "locators": ["PDF-page-2"],
        }
    ]
    assert tree_hashes(evidence_bundle) == before


def test_answer_finalizer_rejects_short_unknown_or_in_bundle_drafts(
    evidence_bundle: Path, tmp_path: Path
) -> None:
    short = tmp_path / "short.json"
    write_json(
        short,
        {
            "summary": "too short",
            "claims": [
                {
                    "statement": "Unsupported.",
                    "supporting_claim_ids": ["claim-missing"],
                }
            ],
        },
    )
    short_result = run_query(
        evidence_bundle,
        "finalize-answer",
        "--draft",
        str(short),
        "--question-id",
        "q-contract",
    )
    assert short_result.returncode == 2
    assert "180 through 320 words" in json.loads(short_result.stdout)["error"]

    write_json(
        short,
        {
            "summary": " ".join(["grounded"] * 180),
            "claims": [
                {
                    "statement": "Unsupported.",
                    "supporting_claim_ids": ["claim-missing"],
                }
            ],
        },
    )
    unknown_result = run_query(
        evidence_bundle,
        "finalize-answer",
        "--draft",
        str(short),
        "--question-id",
        "q-contract",
    )
    assert unknown_result.returncode == 2
    assert "unknown claim IDs" in json.loads(unknown_result.stdout)["error"]

    module = load_snapshot_module()
    snapshot = module.load_snapshot(evidence_bundle)
    inside = evidence_bundle / "draft.json"
    inside.write_text(short.read_text(encoding="utf-8"), encoding="utf-8")
    try:
        with pytest.raises(module.SnapshotError, match="outside the immutable bundle"):
            module.finalize_answer(snapshot, inside, "q-contract", 180, 320)
    finally:
        inside.unlink()


def test_answer_document_view_excludes_noisy_record_metadata(evidence_bundle: Path) -> None:
    module = load_snapshot_module()
    snapshot = module.load_snapshot(evidence_bundle)

    assert len(snapshot.answer_documents) == 1
    document = snapshot.answer_documents[0]
    expected = dict(
        sorted(
            module.Counter(
                module.tokenize(
                    "The reviewed mechanism connects entities and relations.",
                    snapshot.index["plan"],
                )
            ).items()
        )
    )
    assert document["body_terms"] == expected
    assert "evidence_locator" not in document["body_terms"]
    assert "sources" not in document["body_terms"]


def test_answer_diversification_caps_initial_paper_dominance_then_backfills() -> None:
    module = load_snapshot_module()
    ordered = [f"a-{number}" for number in range(5)] + [
        f"b-{number}" for number in range(3)
    ]
    bindings = {
        binding_id: {"paper_id": binding_id[0]}
        for binding_id in ordered
    }

    first_six = module._diversify_answer_bindings(ordered, bindings, 6)
    all_eight = module._diversify_answer_bindings(ordered, bindings, 8)

    assert first_six == ["a-0", "a-1", "a-2", "b-0", "b-1", "b-2"]
    assert all_eight == [
        "a-0",
        "a-1",
        "a-2",
        "b-0",
        "b-1",
        "b-2",
        "a-3",
        "a-4",
    ]


def update_answer_binding_hash_bindings(bundle_path: Path) -> None:
    adaptive = bundle_path / "adaptive"
    binding_path = adaptive / "answer-bindings.jsonl"
    index_path = adaptive / "index.json"
    report_path = adaptive / "build-report.json"
    binding_artifact = {
        "path": "adaptive/answer-bindings.jsonl",
        "bytes": binding_path.stat().st_size,
        "sha256": file_sha256(binding_path),
        "count": len(binding_path.read_text(encoding="utf-8").splitlines()),
    }
    index = json.loads(index_path.read_text(encoding="utf-8"))
    index["artifacts"]["answer_bindings"] = binding_artifact
    write_json(index_path, index)
    report = json.loads(report_path.read_text(encoding="utf-8"))
    report["artifacts"]["answer_bindings"] = binding_artifact
    report["artifacts"]["index"] = {
        "path": "adaptive/index.json",
        "bytes": index_path.stat().st_size,
        "sha256": file_sha256(index_path),
    }
    write_json(report_path, report)


def test_consultant_rejects_hash_consistent_fabricated_answer_locator(
    evidence_bundle: Path, tmp_path: Path
) -> None:
    altered = tmp_path / "fabricated-answer-binding"
    shutil.copytree(evidence_bundle, altered)
    binding_path = altered / "adaptive" / "answer-bindings.jsonl"
    binding = json.loads(binding_path.read_text(encoding="utf-8"))
    binding["locator_tokens"] = ["PDF-page-99"]
    binding["citation_pages"] = [99]
    binding_path.write_text(canonical_json(binding) + "\n", encoding="utf-8")
    update_answer_binding_hash_bindings(altered)

    completed = run_query(altered, "inspect")

    assert completed.returncode == 2
    assert "deterministic authoritative derivation" in json.loads(completed.stdout)["error"]


def test_query_decomposition_preserves_short_operands_and_avoids_full_query_duplicates(
    bundle: Path,
) -> None:
    module = load_snapshot_module()
    plan = json.loads((bundle / "adaptive" / "index.json").read_text(encoding="utf-8"))["plan"]
    compact = "compare mechanisms, conditions, and failure boundaries"
    assert module.decompose_query(compact, plan) == []

    query = (
        "GraphRAG before generation; wrong; support checking and confidence gating; "
        "fact verification insufficient evidence"
    )
    aspects = module.decompose_query(query, plan)
    assert aspects == [
        "GraphRAG before generation wrong support checking and confidence gating",
        "fact verification insufficient evidence",
    ]
    full_tokens = module._unigrams(query, plan)
    aspect_tokens = [token for aspect in aspects for token in module._unigrams(aspect, plan)]
    assert sorted(aspect_tokens) == sorted(full_tokens)
    assert all(module._unigrams(aspect, plan) != full_tokens for aspect in aspects)
    assert all(
        len(module._unigrams(aspect, plan)) >= plan["adaptive"]["minimum_aspect_tokens"]
        for aspect in aspects
    )
    for marker in ("however", "versus", "whereas"):
        contrast = (
            f"alpha evidence {marker} beta limitation; "
            "gamma retrieval mechanism condition"
        )
        contrast_aspects = module.decompose_query(contrast, plan)
        contrast_tokens = [
            token
            for aspect in contrast_aspects
            for token in module._unigrams(aspect, plan)
        ]
        assert sorted(contrast_tokens) == sorted(module._unigrams(contrast, plan))

    repeated = "whereas alpha versus beta alpha zeta whereas alpha"
    repeated_plan = json.loads(json.dumps(plan))
    repeated_plan["adaptive"]["minimum_aspect_tokens"] = 2
    repeated_plan["adaptive"]["maximum_aspects"] = 6
    repeated_aspects = module.decompose_query(repeated, repeated_plan)
    repeated_tokens = [
        token
        for aspect in repeated_aspects
        for token in module._unigrams(aspect, repeated_plan)
    ]
    assert sorted(repeated_tokens) == sorted(module._unigrams(repeated, repeated_plan))
    assert repeated_aspects.count("whereas alpha") == 2


def test_novel_evidence_gate_preserves_full_top_k_and_requires_aspect_confidence() -> None:
    module = load_snapshot_module()
    full_top_k = {"paper:a", "paper:b"}
    aspect_ranks = [{"paper:c": 1, "paper:d": 2}, {"paper:d": 4}]

    assert module._eligible_adaptive_identity("paper:a", full_top_k, aspect_ranks, 1)
    assert module._eligible_adaptive_identity("paper:c", full_top_k, aspect_ranks, 1)
    assert not module._eligible_adaptive_identity("paper:d", full_top_k, aspect_ranks, 1)
    assert not module._eligible_adaptive_identity("paper:missing", full_top_k, aspect_ranks, 1)


def update_tampered_hash_bindings(bundle_path: Path) -> None:
    adaptive = bundle_path / "adaptive"
    index_path = adaptive / "index.json"
    report_path = adaptive / "build-report.json"
    association_path = adaptive / "associations.jsonl"
    index = json.loads(index_path.read_text(encoding="utf-8"))
    association_artifact = {
        "path": "adaptive/associations.jsonl",
        "bytes": association_path.stat().st_size,
        "sha256": file_sha256(association_path),
        "count": len(association_path.read_text(encoding="utf-8").splitlines()),
    }
    index["artifacts"]["associations"] = association_artifact
    write_json(index_path, index)
    report = json.loads(report_path.read_text(encoding="utf-8"))
    report["artifacts"]["associations"] = association_artifact
    report["artifacts"]["index"] = {
        "path": "adaptive/index.json",
        "bytes": index_path.stat().st_size,
        "sha256": file_sha256(index_path),
    }
    write_json(report_path, report)


def test_deep_validation_rejects_hash_consistent_ppmi_tampering(
    bundle: Path, tmp_path: Path
) -> None:
    altered = tmp_path / "altered"
    shutil.copytree(bundle, altered)
    association_path = altered / "adaptive" / "associations.jsonl"
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


def test_structural_validation_rejects_hash_consistent_malformed_topics(
    bundle: Path, tmp_path: Path
) -> None:
    altered = tmp_path / "malformed-topics"
    shutil.copytree(bundle, altered)
    adaptive = altered / "adaptive"
    topics_path = adaptive / "topics.json"
    index_path = adaptive / "index.json"
    report_path = adaptive / "build-report.json"
    topics = json.loads(topics_path.read_text(encoding="utf-8"))
    topics["iterations"] = "one"
    write_json(topics_path, topics)
    topics_artifact = {
        "path": "adaptive/topics.json",
        "bytes": topics_path.stat().st_size,
        "sha256": file_sha256(topics_path),
        "count": topics["topic_count"],
    }
    index = json.loads(index_path.read_text(encoding="utf-8"))
    index["artifacts"]["topics"] = topics_artifact
    write_json(index_path, index)
    report = json.loads(report_path.read_text(encoding="utf-8"))
    report["artifacts"]["topics"] = topics_artifact
    report["artifacts"]["index"] = {
        "path": "adaptive/index.json",
        "bytes": index_path.stat().st_size,
        "sha256": file_sha256(index_path),
    }
    write_json(report_path, report)
    module = load_snapshot_module()

    with pytest.raises(module.SnapshotError, match="topics iterations"):
        module.load_snapshot(altered)


@pytest.mark.parametrize("target_kind", ["file", "directory"])
def test_inspection_rejects_authoritative_symlinks(
    bundle: Path, tmp_path: Path, target_kind: str
) -> None:
    altered = tmp_path / f"symlink-{target_kind}"
    shutil.copytree(bundle, altered)
    if target_kind == "file":
        target = altered / "semantic" / "records.jsonl"
        external = tmp_path / "external-records.jsonl"
        target.replace(external)
        directory = False
    else:
        target = altered / "concepts"
        external = tmp_path / "external-concepts"
        target.replace(external)
        directory = True
    try:
        target.symlink_to(external, target_is_directory=directory)
    except OSError as exc:
        pytest.skip(f"symlink creation is unavailable: {exc}")

    completed = run_query(altered, "inspect", "--deep-validation")
    assert completed.returncode == 2
    assert "symlink or junction" in json.loads(completed.stdout)["error"]


def test_closed_artifact_set_and_invalid_query_fail_cleanly(bundle: Path, tmp_path: Path) -> None:
    altered = tmp_path / "unknown-file"
    shutil.copytree(bundle, altered)
    (altered / "adaptive" / "cache.json").write_text("{}\n", encoding="utf-8")
    closed = run_query(altered, "inspect")
    empty = run_query(bundle, "search", "--query", "   ", "--mode", "bm25")

    assert closed.returncode == 2
    assert "artifact set is closed" in json.loads(closed.stdout)["error"]
    assert empty.returncode == 2
    assert "query must be nonempty" in json.loads(empty.stdout)["error"]
