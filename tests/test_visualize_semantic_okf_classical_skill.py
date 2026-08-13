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
CLASSICAL_BUILDER = (
    REPO_ROOT
    / "skills"
    / "build-semantic-okf-classical"
    / "scripts"
    / "build_semantic_okf_classical.py"
)
SKILL_ROOT = REPO_ROOT / "skills" / "visualize-semantic-okf-classical"
REAL_CLASSICAL_BUNDLE = (
    REPO_ROOT
    / "evaluations"
    / "semantic-okf-classical"
    / "generated"
    / "trace-distillation"
    / "20260727-builder-host-windows-v1"
)


def load_atlas_module() -> ModuleType:
    scripts = SKILL_ROOT / "scripts"
    sys.path.insert(0, str(scripts))
    try:
        name = "test_classical_atlas_runtime"
        spec = importlib.util.spec_from_file_location(name, scripts / "_classical_atlas.py")
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
        return module
    finally:
        sys.path.remove(str(scripts))


def write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tree_hashes(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): file_sha256(path)
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def write_builder_inputs(root: Path) -> tuple[Path, Path]:
    sources = root / "sources"
    sources.mkdir(parents=True)
    source_text = {
        "graph-notes": (
            "Graph Retrieval Notes",
            "2024",
            "Graph retrieval connects entities, relations, paths, and grounded evidence. "
            "Community summaries organize global themes while exact passages preserve citations. "
            "Association statistics reveal recurring terms without asserting ontology facts.",
        ),
        "ranking-notes": (
            "Classical Ranking Notes",
            "2025",
            "Lexical ranking uses document frequency and corpus frequency. BM25 weights titles "
            "and bodies, topic communities expand related queries, and PPMI associations expose "
            "local term neighborhoods for diverse evidence discovery.",
        ),
    }
    for source_id, (title, year, body) in source_text.items():
        (sources / f"{source_id}.md").write_text(
            f"---\ntitle: {title}\nyear: {year}\ncode: {source_id.upper()}\n---\n\n"
            f"# {title}\n\n{body}\n",
            encoding="utf-8",
        )

    manifest = {
        "schema_version": "1.0",
        "bundle": {
            "title": "Classical atlas fixture",
            "description": "A deterministic fixture for read-only knowledge atlas tests.",
            "base_iri": "https://example.org/classical-atlas/",
            "ontology_iri": "https://example.org/ontology/classical-atlas",
            "version_iri": "https://example.org/ontology/classical-atlas/1.0.0",
            "prefix": "atlas",
            "owl_profile": "rl",
        },
        "ontology": {
            "classes": [{"name": "KnowledgeNote", "label": "knowledge note"}],
            "properties": [
                {
                    "name": "code",
                    "kind": "datatype",
                    "domain": "KnowledgeNote",
                    "range": "xsd:string",
                },
                {
                    "name": "year",
                    "kind": "datatype",
                    "domain": "KnowledgeNote",
                    "range": "xsd:integer",
                },
            ],
        },
        "rules": [
            {
                "name": "KnowledgeNoteCodeRule",
                "target_class": "KnowledgeNote",
                "path": "code",
                "min_count": 1,
                "datatype": "xsd:string",
                "message": "Every knowledge note requires a code.",
                "basis": {"kind": "operational-policy", "references": ["ATLAS-1"]},
            }
        ],
        "sources": [
            {
                "id": source_id,
                "kind": "markdown",
                "path": f"sources/{source_id}.md",
                "concept_type": "KnowledgeNote",
                "ontology_class": "KnowledgeNote",
                "fields": {"code": "code", "year": "year"},
            }
            for source_id in sorted(source_text)
        ],
    }
    plan = {
        "schema_version": "1.0",
        "selection": {"source_ids": sorted(source_text)},
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
            "max_vocabulary": 48,
            "max_neighbors": 6,
            "minimum_ppmi": 0.0,
        },
        "topics": {"topic_count": 3, "max_iterations": 10, "top_terms": 8},
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
    write_json(manifest_path, manifest)
    write_json(plan_path, plan)
    return manifest_path, plan_path


def run_script(
    script: Path,
    *arguments: Path | str,
    cwd: Path,
) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment.pop("PYTHONPATH", None)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run(
        [sys.executable, "-B", str(script), *(str(argument) for argument in arguments)],
        cwd=cwd,
        env=environment,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=90,
        check=False,
    )


@pytest.fixture(scope="module")
def portable_context(tmp_path_factory: pytest.TempPathFactory) -> dict[str, Path]:
    root = tmp_path_factory.mktemp("classical-atlas")
    inputs = root / "inputs"
    inputs.mkdir()
    manifest, plan = write_builder_inputs(inputs)
    knowledge = root / "knowledge"
    built = run_script(
        CLASSICAL_BUILDER,
        manifest,
        plan,
        knowledge,
        "--output-format",
        "json",
        cwd=inputs,
    )
    assert built.returncode == 0, built.stdout + built.stderr

    copied_skill = root / "installed-skill"
    shutil.copytree(SKILL_ROOT, copied_skill)
    return {"root": root, "knowledge": knowledge, "skill": copied_skill}


@pytest.fixture()
def generated_atlas(portable_context: dict[str, Path], tmp_path: Path) -> dict[str, Path]:
    knowledge = portable_context["knowledge"]
    skill = portable_context["skill"]
    output = tmp_path / "external-atlas"
    build = run_script(
        skill / "scripts" / "build_classical_atlas.py",
        knowledge,
        output,
        "--output-format",
        "json",
        cwd=skill,
    )
    assert build.returncode == 0, build.stdout + build.stderr
    return {"knowledge": knowledge, "skill": skill, "output": output}


def test_skill_metadata_and_package_are_complete() -> None:
    skill_text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
    metadata = yaml.safe_load(skill_text.split("---", 2)[1])

    assert set(metadata) == {"name", "description"}
    assert metadata["name"] == "visualize-semantic-okf-classical"
    assert "read-only" in metadata["description"]
    assert "contradiction" in metadata["description"]
    assert "non-authoritative" in skill_text
    assert "--check" in skill_text
    assert "$visualize-semantic-okf-classical" in (
        SKILL_ROOT / "agents" / "openai.yaml"
    ).read_text(encoding="utf-8")
    assert (SKILL_ROOT / "assets" / "classical-atlas-template.html").is_file()
    assert (SKILL_ROOT / "references" / "metadata-contract.md").is_file()
    assert {path.name for path in (SKILL_ROOT / "scripts").glob("*.py")} == {
        "_classical_atlas.py",
        "build_classical_atlas.py",
        "runtime_smoke.py",
        "validate_classical_atlas.py",
    }
    assert "TODO" not in "\n".join(
        path.read_text(encoding="utf-8")
        for path in SKILL_ROOT.rglob("*")
        if path.is_file() and path.suffix in {".html", ".md", ".py", ".yaml"}
    )


def test_copied_skill_builds_validates_and_checks_without_mutating_source(
    generated_atlas: dict[str, Path],
) -> None:
    knowledge = generated_atlas["knowledge"]
    skill = generated_atlas["skill"]
    output = generated_atlas["output"]
    before = tree_hashes(knowledge)

    validated = run_script(
        skill / "scripts" / "validate_classical_atlas.py",
        knowledge,
        output,
        "--output-format",
        "json",
        cwd=skill,
    )
    checked = run_script(
        skill / "scripts" / "build_classical_atlas.py",
        knowledge,
        output,
        "--check",
        "--output-format",
        "json",
        cwd=skill,
    )

    assert validated.returncode == checked.returncode == 0, validated.stdout + validated.stderr
    assert json.loads(validated.stdout)["status"] == "pass"
    assert json.loads(checked.stdout)["check"] is True
    assert tree_hashes(knowledge) == before
    assert {path.name for path in output.iterdir()} == {
        "index.html",
        "projection.json",
        "receipt.json",
    }


def test_projection_uses_every_classical_and_semantic_metadata_layer(
    generated_atlas: dict[str, Path],
) -> None:
    knowledge = generated_atlas["knowledge"]
    output = generated_atlas["output"]
    projection = json.loads((output / "projection.json").read_text(encoding="utf-8"))
    lexicon = json.loads((knowledge / "classical" / "lexicon.json").read_text(encoding="utf-8"))
    associations = [
        json.loads(line)
        for line in (knowledge / "classical" / "associations.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
        if line
    ]

    assert projection["schema"] == "classical-knowledge-atlas/1.2"
    assert projection["inventory"]["records"] == len(projection["records"]) == 2
    assert projection["inventory"]["passages"] == len(projection["documents"]) == 2
    assert projection["inventory"]["terms"] == len(lexicon["terms"])
    assert sum(row["count"] for row in projection["lexical"]["document_frequency_buckets"]) == len(
        lexicon["terms"]
    )
    assert projection["inventory"]["association_terms"] == len(associations)
    assert projection["associations"]["directed_edge_count"] == sum(
        len(row["neighbors"]) for row in associations
    )
    assert projection["topics"]
    assert all("association_graph" in topic for topic in projection["topics"])
    assert all("locator" in document and "text_sha256" in document for document in projection["documents"])
    assert all("body" not in record and "attributes" in record for record in projection["records"])
    assert projection["record_types"]
    assert projection["publication_years"] == [
        {"count": 1, "year": 2024},
        {"count": 1, "year": 2025},
    ]
    assert projection["attribute_coverage"]
    assert projection["ontology"]["classes"]
    assert projection["ontology"]["properties"]
    assert projection["ontology"]["rules"]
    assert {source["classical_status"] for source in projection["sources"]} == {"selected"}
    assert set(projection["contracts"]) == {
        "classical_build_report",
        "classical_index",
        "semantic_build_report",
        "semantic_plan",
        "semantic_source_manifest",
    }
    assert projection["integrity"]["classical_valid"] is True
    assert projection["integrity"]["semantic_valid"] is True
    assert projection["integrity"]["source_tree"]["sha256"]
    assert projection["contradictions"]["schema"] == "classical-contradiction-review/2.0"
    assert projection["contradictions"]["summary"]["declared_count"] == 0
    assert projection["contradictions"]["summary"]["strict_candidate_count"] == 0
    assert projection["contradictions"]["summary"]["filtered_loose_signal_count"] == 0
    assert projection["contradictions"]["method"]["ranking_is_probability"] is False


def test_contradiction_projection_separates_persisted_relations_from_review_candidates() -> None:
    module = load_atlas_module()

    def claim(
        record_id: str,
        claim_kind: str,
        interpretation: str,
        *,
        subject: str | None,
        contradiction_target: str | None = None,
    ) -> dict[str, Any]:
        attributes: dict[str, Any] = {
            "claim_kind": claim_kind,
            "interpretation": interpretation,
            "object_term_iri": "urn:dimension:answer-quality",
            "review_state": "reviewed",
            "evidence_locator": f"source.md#{record_id}",
        }
        if subject:
            attributes["subject_term_iri"] = subject
        if contradiction_target:
            attributes["contradicts_record_id"] = contradiction_target
        return {
            "record_id": record_id,
            "concept_id": f"concepts/{record_id}",
            "concept_path": f"concepts/{record_id}.md",
            "concept_type": "Paper Semantic Claim",
            "source_id": f"source-{record_id}",
            "source_path": f"sources/{record_id}.jsonl",
            "title": record_id,
            "record_sha256": record_id * 4,
            "attributes": attributes,
        }

    records = [
        claim(
            "claim-a",
            "strength",
            "Atlas Engine improves answer accuracy for nested questions.",
            subject="urn:method:atlas-engine",
        ),
        claim(
            "claim-b",
            "limitation",
            "Atlas Engine does not improve answer accuracy for nested questions.",
            subject="urn:method:atlas-engine",
        ),
        claim(
            "claim-c",
            "limitation",
            "Atlas Engine does not improve answer accuracy for nested questions.",
            subject="urn:method:different-engine",
        ),
        claim(
            "claim-d",
            "statement",
            "A source-declared statement.",
            subject=None,
            contradiction_target="claim-e",
        ),
        claim(
            "claim-e",
            "statement",
            "The explicitly opposed source statement.",
            subject=None,
        ),
    ]
    term_metrics = {
        term: {"idf": 3.0, "document_frequency": 2, "corpus_frequency": 2}
        for term in ("atlas", "engine", "answer", "accuracy", "nested", "questions")
    }

    result = module.detect_contradictions(records, term_metrics)

    assert result["summary"]["declared_count"] == 1
    assert result["summary"]["declared_relation_count"] == 1
    assert result["declared"][0]["status"] == "source-declared"
    assert {
        result["declared"][0]["claim_a"]["record_id"],
        result["declared"][0]["claim_b"]["record_id"],
    } == {"claim-d", "claim-e"}
    assert result["summary"]["strict_candidate_count"] == 1
    candidate = result["strict_candidates"][0]
    assert candidate["status"] == "strict-review-required"
    assert candidate["detection_kind"] == "exact-negation"
    assert candidate["alignment"]["same_analysis_dimension"] is True
    assert {candidate["claim_a"]["record_id"], candidate["claim_b"]["record_id"]} == {
        "claim-a",
        "claim-b",
    }
    assert "claim-c" not in {
        candidate["claim_a"]["record_id"],
        candidate["claim_b"]["record_id"],
    }
    assert any(signal["kind"] == "strict-negation-conflict" for signal in candidate["signals"])
    assert result["method"]["ranking_is_probability"] is False


def test_strict_contradiction_gate_rejects_compatible_tradeoffs_and_scope_changes() -> None:
    module = load_atlas_module()

    def claim(
        record_id: str,
        claim_kind: str,
        interpretation: str,
        *,
        subject: str,
        dimension: str,
    ) -> dict[str, Any]:
        return {
            "record_id": record_id,
            "concept_id": f"concepts/{record_id}",
            "concept_path": f"concepts/{record_id}.md",
            "concept_type": "Paper Semantic Claim",
            "source_id": f"source-{record_id}",
            "source_path": f"sources/{record_id}.jsonl",
            "title": record_id,
            "record_sha256": record_id * 4,
            "attributes": {
                "claim_kind": claim_kind,
                "interpretation": interpretation,
                "object_term_iri": dimension,
                "review_state": "reviewed",
                "subject_term_iri": subject,
                "evidence_locator": f"source.md#{record_id}",
            },
        }

    records = [
        claim(
            "claim-reduces",
            "strength",
            "The self-correction mechanism improves generated Cypher reliability for nested questions.",
            subject="urn:method:self-correction",
            dimension="urn:dimension:strength",
        ),
        claim(
            "claim-residual",
            "limitation",
            "Generated Cypher can still fail for nested questions.",
            subject="urn:method:self-correction",
            dimension="urn:dimension:limitation",
        ),
        claim(
            "claim-mixed-direction",
            "strength",
            "GraphReader remains stronger than baseline as context length grows, while full-context GPT-4 degrades.",
            subject="urn:method:graphreader",
            dimension="urn:dimension:strength",
        ),
        claim(
            "claim-same-direction",
            "strength",
            "GraphReader degrades much less than full-context GPT-4 as context length grows.",
            subject="urn:method:graphreader",
            dimension="urn:dimension:strength",
        ),
        claim(
            "claim-benchmark-a",
            "comparison",
            "The method increases retrieval accuracy on Benchmark A.",
            subject="urn:method:scope-sensitive",
            dimension="urn:dimension:comparison",
        ),
        claim(
            "claim-benchmark-b",
            "comparison",
            "The method decreases retrieval accuracy on Benchmark B.",
            subject="urn:method:scope-sensitive",
            dimension="urn:dimension:comparison",
        ),
    ]
    vocabulary = {
        token
        for record in records
        for token in module._word_tokens(record["attributes"]["interpretation"])
    }
    term_metrics = {
        term: {"idf": 3.0, "document_frequency": 2, "corpus_frequency": 2}
        for term in vocabulary
    }

    result = module.detect_contradictions(records, term_metrics)

    assert result["summary"]["strict_candidate_count"] == 0
    assert result["strict_candidates"] == []
    assert result["summary"]["loose_signal_count"] >= 1
    assert result["summary"]["filtered_loose_signal_count"] == result["summary"][
        "loose_signal_count"
    ]
    assert result["summary"]["rejection_reasons"]["different-analysis-dimension"] >= 1


def test_strict_contradiction_gate_supports_structured_directional_and_numeric_conflicts() -> None:
    module = load_atlas_module()

    def claim(
        record_id: str,
        interpretation: str,
        *,
        subject: str,
        extra: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        attributes: dict[str, Any] = {
            "claim_kind": "comparison",
            "interpretation": interpretation,
            "object_term_iri": "urn:dimension:comparison",
            "review_state": "reviewed",
            "subject_term_iri": subject,
            "evidence_locator": f"source.md#{record_id}",
        }
        attributes.update(extra or {})
        return {
            "record_id": record_id,
            "concept_id": f"concepts/{record_id}",
            "concept_path": f"concepts/{record_id}.md",
            "concept_type": "Paper Semantic Claim",
            "source_id": f"source-{record_id}",
            "source_path": f"sources/{record_id}.jsonl",
            "title": record_id,
            "record_sha256": record_id * 4,
            "attributes": attributes,
        }

    records = [
        claim(
            "structured-positive",
            "Atlas supports encrypted audit logs.",
            subject="urn:method:structured",
            extra={"proposition_key": "urn:proposition:audit-logs", "proposition_polarity": "affirmed"},
        ),
        claim(
            "structured-negative",
            "Atlas lacks encrypted audit logs.",
            subject="urn:method:structured",
            extra={"proposition_key": "urn:proposition:audit-logs", "proposition_polarity": "negated"},
        ),
        claim(
            "direction-up",
            "Atlas Engine increases retrieval accuracy over Baseline R on Benchmark Z.",
            subject="urn:method:direction",
        ),
        claim(
            "direction-down",
            "Atlas Engine decreases retrieval accuracy over Baseline R on Benchmark Z.",
            subject="urn:method:direction",
        ),
        claim(
            "numeric-high",
            "Atlas Engine reaches 87% retrieval accuracy on Benchmark Z with Model Q.",
            subject="urn:method:numeric",
        ),
        claim(
            "numeric-low",
            "Atlas Engine reaches 42% retrieval accuracy on Benchmark Z with Model Q.",
            subject="urn:method:numeric",
        ),
    ]
    vocabulary = {
        token
        for record in records
        for token in module._word_tokens(record["attributes"]["interpretation"])
    }
    term_metrics = {
        term: {"idf": 3.0, "document_frequency": 2, "corpus_frequency": 2}
        for term in vocabulary
    }

    result = module.detect_contradictions(records, term_metrics)

    assert result["summary"]["strict_candidate_count"] == 3
    assert {row["detection_kind"] for row in result["strict_candidates"]} == {
        "structured-polarity",
        "directional-opposition",
        "numeric-disagreement",
    }
    assert all(row["status"] == "strict-review-required" for row in result["strict_candidates"])
    assert all(row["alignment"]["same_structured_subject"] for row in result["strict_candidates"])


@pytest.mark.skipif(
    not (REAL_CLASSICAL_BUNDLE / "semantic" / "records.jsonl").is_file(),
    reason="real Classical audit bundle is not available",
)
def test_real_classical_contradiction_audit_filters_all_legacy_false_positives() -> None:
    module = load_atlas_module()
    records = module.read_jsonl(REAL_CLASSICAL_BUNDLE / "semantic" / "records.jsonl")
    lexicon = json.loads(
        (REAL_CLASSICAL_BUNDLE / "classical" / "lexicon.json").read_text(encoding="utf-8")
    )
    term_metrics = {str(row.get("term")): row for row in lexicon.get("terms") or []}

    result = module.detect_contradictions(records, term_metrics)

    assert result["summary"]["eligible_claims"] == 831
    assert result["summary"]["evaluated_pairs"] == 22_710
    assert result["summary"]["loose_signal_count"] == 30
    assert result["summary"]["filtered_loose_signal_count"] == 30
    assert result["summary"]["rejection_reasons"] == {"different-analysis-dimension": 30}
    assert result["summary"]["declared_count"] == 0
    assert result["summary"]["strict_candidate_count"] == 0
    assert result["strict_candidates"] == []


def test_atlas_is_self_contained_and_embeds_the_exact_projection(
    generated_atlas: dict[str, Path],
) -> None:
    output = generated_atlas["output"]
    html = (output / "index.html").read_text(encoding="utf-8")
    projection = json.loads((output / "projection.json").read_text(encoding="utf-8"))
    opening = '<script id="atlas-data" type="application/json">'
    embedded = html.split(opening, 1)[1].split("</script>", 1)[0]

    assert json.loads(embedded) == projection
    assert "<script src=" not in html.lower()
    assert "<link href=\"http" not in html.lower()
    assert "fetch(\"http" not in html.lower()
    assert "new websocket" not in html.lower()
    assert "document.documentElement.dataset.ready" in html
    assert "Derived signal." in html
    assert "They are not ontology facts or evidence claims." in html
    assert 'data-view="contradictions"' in html
    assert 'id="contradiction-search"' in html
    assert 'id="contradiction-status-filter"' in html
    assert 'id="contradiction-scope-filter"' in html
    assert 'id="contradiction-signal-filter"' in html
    assert "Strengths, limitations, trade-offs, and loose polarity words are filtered out" in html
    assert "Strict candidate; review still required." in html


def test_output_must_be_external_absent_and_closed(
    portable_context: dict[str, Path], tmp_path: Path
) -> None:
    knowledge = portable_context["knowledge"]
    skill = portable_context["skill"]
    inside_knowledge = knowledge / "atlas"
    rejected_inside = run_script(
        skill / "scripts" / "build_classical_atlas.py",
        knowledge,
        inside_knowledge,
        cwd=skill,
    )
    assert rejected_inside.returncode == 1
    assert "must be disjoint" in rejected_inside.stderr
    assert not inside_knowledge.exists()

    existing = tmp_path / "existing"
    existing.mkdir()
    rejected_existing = run_script(
        skill / "scripts" / "build_classical_atlas.py",
        knowledge,
        existing,
        cwd=skill,
    )
    assert rejected_existing.returncode == 1
    assert "already exists" in rejected_existing.stderr


def test_validator_detects_source_and_output_drift(
    portable_context: dict[str, Path], tmp_path: Path
) -> None:
    skill = portable_context["skill"]
    knowledge = tmp_path / "knowledge"
    shutil.copytree(portable_context["knowledge"], knowledge)
    output = tmp_path / "atlas"
    built = run_script(
        skill / "scripts" / "build_classical_atlas.py",
        knowledge,
        output,
        cwd=skill,
    )
    assert built.returncode == 0, built.stdout + built.stderr

    (knowledge / "index.md").write_text(
        (knowledge / "index.md").read_text(encoding="utf-8") + "\nSource drift.\n",
        encoding="utf-8",
    )
    source_drift = run_script(
        skill / "scripts" / "validate_classical_atlas.py",
        knowledge,
        output,
        cwd=skill,
    )
    assert source_drift.returncode == 1
    assert "source tree changed" in source_drift.stderr

    knowledge = tmp_path / "knowledge-clean"
    shutil.copytree(portable_context["knowledge"], knowledge)
    output = tmp_path / "atlas-drift"
    built = run_script(
        skill / "scripts" / "build_classical_atlas.py",
        knowledge,
        output,
        cwd=skill,
    )
    assert built.returncode == 0, built.stdout + built.stderr
    (output / "index.html").write_text(
        (output / "index.html").read_text(encoding="utf-8") + "\n",
        encoding="utf-8",
    )
    output_drift = run_script(
        skill / "scripts" / "validate_classical_atlas.py",
        knowledge,
        output,
        cwd=skill,
    )
    assert output_drift.returncode == 1
    assert "artifact receipt mismatch" in output_drift.stderr


def test_closed_classical_input_rejects_unknown_entries(
    portable_context: dict[str, Path], tmp_path: Path
) -> None:
    skill = portable_context["skill"]
    knowledge = tmp_path / "knowledge"
    shutil.copytree(portable_context["knowledge"], knowledge)
    (knowledge / "classical" / "unexpected").mkdir()

    rejected = run_script(
        skill / "scripts" / "build_classical_atlas.py",
        knowledge,
        tmp_path / "atlas",
        cwd=skill,
    )

    assert rejected.returncode == 1
    assert "classical closed-file mismatch" in rejected.stderr
