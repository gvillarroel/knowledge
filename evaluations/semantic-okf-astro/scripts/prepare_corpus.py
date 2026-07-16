#!/usr/bin/env python3
"""Freeze the pinned Astro English documentation and derive the benchmark files."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Mapping

import yaml


REPO_ROOT = Path(__file__).resolve().parents[3]
EVALUATION = REPO_ROOT / "evaluations" / "semantic-okf-astro"
CORPUS = EVALUATION / "corpus"
BENCHMARK = EVALUATION / "benchmark"
PLANS = EVALUATION / "plans"
QUESTION_SPECS = BENCHMARK / "question-specs.json"

COMMIT = "5c37be52c5038e1174be1e838d3dd5852db26a21"
KNOW_KEY = "astro-technical-docs-2026-07"
KNOW_SOURCE_ID = "github-docs.git"
REPOSITORY_URL = "https://github.com/withastro/docs.git"
EXPECTED_DOCUMENTS = 416
ACCEPTED_EXPORT = {
    "filename": "knowledge-export-20260716T085103Z.zip",
    "bytes": 22663290,
    "sha256": "5a49689fb5775c5f03717cbc11af0389d1014082b9f4c44fd21e4a03ffe71bec",
}
GENERATED_BENCHMARK_FILES = (
    "retrieval-questions.jsonl",
    "hard-questions.jsonl",
    "hard-ground-truth.jsonl",
    "benchmark-manifest.json",
)
GENERATED_PLAN_FILES = (
    "adaptive-plan.json",
    "classical-plan.json",
    "embedding-plan.json",
    "ensemble-plan.json",
    "entity-graph-plan.json",
    "plan-manifest.json",
)
HEADING_RE = re.compile(r"^(#{2,6})\s+(.+?)\s*$", re.MULTILINE)


class PreparationError(RuntimeError):
    """Raised when the acquisition snapshot or authored specification is invalid."""


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def pretty_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def jsonl(rows: Iterable[Mapping[str, Any]]) -> bytes:
    return b"".join((canonical_json(row) + "\n").encode("utf-8") for row in rows)


def exact_keys(value: Mapping[str, Any], expected: set[str], label: str) -> None:
    observed = set(value)
    if observed != expected:
        raise PreparationError(
            f"{label} has a closed schema; missing={sorted(expected - observed)}, "
            f"unknown={sorted(observed - expected)}"
        )


def source_root(know_store: Path) -> Path:
    return (
        know_store
        / KNOW_KEY
        / "github"
        / KNOW_SOURCE_ID
        / COMMIT
        / "src"
        / "content"
        / "docs"
        / "en"
    )


def route_for(relative: Path) -> str:
    without_suffix = relative.as_posix().removesuffix(".mdx")
    if without_suffix == "index":
        without_suffix = ""
    elif without_suffix.endswith("/index"):
        without_suffix = without_suffix.removesuffix("/index")
    suffix = f"{without_suffix.strip('/')}/" if without_suffix else ""
    return f"/en/{suffix}"


def source_id_for(route: str) -> str:
    return f"astro-doc-{sha256_bytes(route.encode('utf-8'))[:16]}"


def parse_frontmatter(payload: bytes, label: str) -> dict[str, Any]:
    text = payload.decode("utf-8-sig")
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not match:
        raise PreparationError(f"{label} has no YAML frontmatter")
    value = yaml.safe_load(match.group(1)) or {}
    if not isinstance(value, dict) or not isinstance(value.get("title"), str):
        raise PreparationError(f"{label} frontmatter must contain a string title")
    description = value.get("description")
    if description is not None and not isinstance(description, str):
        raise PreparationError(f"{label} frontmatter description must be a string when present")
    return value


def _export_binding(know_store: Path) -> dict[str, Any]:
    path = know_store / "exports" / ACCEPTED_EXPORT["filename"]
    if not path.is_file():
        raise PreparationError(f"accepted Know export is missing: {path}")
    observed = {"bytes": path.stat().st_size, "sha256": sha256_bytes(path.read_bytes())}
    if observed != {"bytes": ACCEPTED_EXPORT["bytes"], "sha256": ACCEPTED_EXPORT["sha256"]}:
        raise PreparationError(f"accepted Know export differs from its pinned binding: {observed}")
    return {"path": f"exports/{path.name}", **observed}


def build_corpus_outputs(know_store: Path) -> dict[Path, bytes]:
    root = source_root(know_store)
    if not root.is_dir():
        raise PreparationError(f"pinned Know source tree is missing: {root}")
    upstream = sorted(root.rglob("*.mdx"))
    if len(upstream) != EXPECTED_DOCUMENTS:
        raise PreparationError(f"expected {EXPECTED_DOCUMENTS} English MDX files, observed {len(upstream)}")

    outputs: dict[Path, bytes] = {}
    documents: list[dict[str, Any]] = []
    sources: list[dict[str, Any]] = []
    sections: Counter[str] = Counter()
    total_bytes = 0
    for path in upstream:
        relative = path.relative_to(root)
        payload = path.read_bytes()
        metadata = parse_frontmatter(payload, relative.as_posix())
        checked_relative = Path("sources") / "mdx" / relative
        outputs[checked_relative] = payload
        route = route_for(relative)
        record_id = checked_relative.as_posix().removesuffix(".mdx")
        canonical_url = f"https://docs.astro.build{route}"
        source_id = source_id_for(route)
        section = relative.parts[0] if len(relative.parts) > 1 else "(root)"
        sections[section] += 1
        total_bytes += len(payload)
        documents.append(
            {
                "bytes": len(payload),
                "canonical_url": canonical_url,
                "document_id": route,
                "path": f"corpus/{checked_relative.as_posix()}",
                "record_id": record_id,
                "section": section,
                "sha256": sha256_bytes(payload),
                "source_id": source_id,
                "title": metadata["title"],
                "upstream_path": f"src/content/docs/en/{relative.as_posix()}",
            }
        )
        sources.append(
            {
                "concept_type": "Astro Documentation Page",
                "fields": {"description": "pageDescription", "title": "pageTitle"},
                "id": source_id,
                "kind": "markdown",
                "ontology_class": "DocumentationPage",
                "path": checked_relative.as_posix(),
            }
        )

    if len({item["source_id"] for item in documents}) != EXPECTED_DOCUMENTS:
        raise PreparationError("derived source IDs are not unique")
    if len({item["document_id"] for item in documents}) != EXPECTED_DOCUMENTS:
        raise PreparationError("derived document IDs are not unique")

    tree_entries = [{"path": row["upstream_path"], "sha256": row["sha256"]} for row in documents]
    tree_sha256 = sha256_bytes(canonical_json(tree_entries).encode("utf-8"))
    export = _export_binding(know_store)
    acquisition = {
        "authority": {
            "contract": "The pinned official English MDX files are authoritative. Semantic OKF cores are validated projections; every retrieval, graph, embedding, ranking, qrel, and answer score is derived and non-authoritative.",
            "language": "en",
            "preservation": "Checked corpus files are byte-for-byte copies of the accepted Know extraction.",
        },
        "documents": EXPECTED_DOCUMENTS,
        "know": {
            "accepted_export": export,
            "export_is_append_only_and_ignored": True,
            "key": KNOW_KEY,
            "source_id": KNOW_SOURCE_ID,
            "source_type": "github",
        },
        "repository": {
            "commit": COMMIT,
            "content_root": "src/content/docs/en",
            "url": REPOSITORY_URL,
        },
        "schema_version": "semantic-okf-astro-acquisition/1.0",
        "section_counts": dict(sorted(sections.items())),
        "total_bytes": total_bytes,
        "tree_sha256": tree_sha256,
    }
    identity = {
        "documents": [
            {
                "canonical_url": row["canonical_url"],
                "document_id": row["document_id"],
                "path": row["path"],
                "record_id": row["record_id"],
                "source_id": row["source_id"],
                "upstream_path": row["upstream_path"],
            }
            for row in documents
        ],
        "identity_kind": "canonical-route",
        "records": [
            {
                "canonical_url": row["canonical_url"],
                "document_id": row["document_id"],
                "path": row["path"],
                "record_id": row["record_id"],
                "source_id": row["source_id"],
                "upstream_path": row["upstream_path"],
            }
            for row in documents
        ],
        "schema_version": "semantic-okf-astro-source-identity/1.1",
        "source_record_to_document_ids": {
            canonical_json([row["source_id"], row["record_id"]]): row["document_id"]
            for row in documents
        },
        "source_ids_to_document_ids": {row["source_id"]: row["document_id"] for row in documents},
    }
    manifest = {
        "bundle": {
            "base_iri": "https://docs.astro.build/semantic-okf/",
            "description": "Pinned official English Astro technical documentation.",
            "ontology_iri": "https://docs.astro.build/semantic-okf/ontology",
            "owl_profile": "rl",
            "prefix": "astrodocs",
            "title": "Astro Technical Documentation Semantic Corpus",
            "version_iri": f"https://docs.astro.build/semantic-okf/ontology/{COMMIT}",
        },
        "ontology": {
            "classes": [{"label": "documentation page", "name": "DocumentationPage"}],
            "properties": [
                {"domain": "DocumentationPage", "kind": "datatype", "name": "pageTitle", "range": "xsd:string"},
                {"domain": "DocumentationPage", "kind": "datatype", "name": "pageDescription", "range": "xsd:string"},
            ],
        },
        "rules": [],
        "schema_version": "1.0",
        "sources": sources,
    }
    inventory = {
        "authoritative_tree_sha256": tree_sha256,
        "document_count": EXPECTED_DOCUMENTS,
        "documents": documents,
        "schema_version": "semantic-okf-astro-input-inventory/1.0",
        "total_bytes": total_bytes,
    }
    outputs[Path("acquisition-manifest.json")] = pretty_json(acquisition)
    outputs[Path("input-inventory.json")] = pretty_json(inventory)
    outputs[Path("manifest.json")] = pretty_json(manifest)
    outputs[Path("source-combination.json")] = pretty_json(identity)
    return outputs


def load_specs() -> list[dict[str, Any]]:
    value = json.loads(QUESTION_SPECS.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise PreparationError("question specs must be an object")
    exact_keys(value, {"questions", "schema_version"}, "question specs")
    if value["schema_version"] != "semantic-okf-astro-question-specs/1.0":
        raise PreparationError("question specs schema version is unsupported")
    questions = value["questions"]
    if not isinstance(questions, list) or len(questions) != 40:
        raise PreparationError("question specs must contain exactly 40 questions")
    return questions


def _heading_section(payload: bytes, selector: Mapping[str, Any], label: str) -> dict[str, Any]:
    text = payload.decode("utf-8-sig")
    headings = list(HEADING_RE.finditer(text))
    wanted = selector["heading"]
    occurrence = int(selector.get("occurrence", 1))
    matches = [(index, match) for index, match in enumerate(headings) if match.group(2).strip() == wanted]
    if occurrence < 1 or occurrence > len(matches):
        raise PreparationError(f"{label} cannot resolve heading {wanted!r} occurrence {occurrence}")
    index, match = matches[occurrence - 1]
    level = len(match.group(1))
    end = next((item.start() for item in headings[index + 1 :] if len(item.group(1)) <= level), len(text))
    stack: list[tuple[int, str]] = []
    for item in headings[: index + 1]:
        item_level = len(item.group(1))
        while stack and stack[-1][0] >= item_level:
            stack.pop()
        stack.append((item_level, item.group(2).strip()))
    section_text = text[match.start() : end]
    return {
        "end_char": end,
        "heading": wanted,
        "heading_path": [item[1] for item in stack],
        "locator": f"heading={wanted};chars={match.start()}-{end}",
        "start_char": match.start(),
        "text_sha256": sha256_bytes(section_text.encode("utf-8")),
    }


def _corpus_indexes() -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    inventory = json.loads((CORPUS / "input-inventory.json").read_text(encoding="utf-8"))
    by_upstream = {item["upstream_path"]: item for item in inventory["documents"]}
    by_document = {item["document_id"]: item for item in inventory["documents"]}
    return by_upstream, by_document


def build_benchmark_outputs() -> dict[str, bytes]:
    specs = load_specs()
    by_upstream, _ = _corpus_indexes()
    retrieval: list[dict[str, Any]] = []
    hard_questions: list[dict[str, Any]] = []
    hard_ground_truth: list[dict[str, Any]] = []
    ids: list[str] = []
    type_counts: Counter[str] = Counter()
    for number, spec in enumerate(specs, start=1):
        expected_id = f"q{number:03d}"
        if not isinstance(spec, dict):
            raise PreparationError(f"question spec {number} must be an object")
        required = {"documents", "id", "question", "question_type"}
        if spec.get("question_type") == "hard":
            required.add("ground_truth")
        exact_keys(spec, required, f"question spec {number}")
        if spec["id"] != expected_id:
            raise PreparationError(f"question IDs must be sequential; expected {expected_id}")
        if spec["question_type"] not in {"direct", "cross-document", "hard"}:
            raise PreparationError(f"{expected_id} has unsupported question type")
        documents = spec["documents"]
        if not isinstance(documents, list) or not documents or len(documents) != len(set(documents)):
            raise PreparationError(f"{expected_id}.documents must be unique and non-empty")
        try:
            records = [by_upstream[path] for path in documents]
        except KeyError as exc:
            raise PreparationError(f"{expected_id} references unknown upstream document {exc.args[0]}") from exc
        row = {
            "id": expected_id,
            "qrels": {
                "document_ids": sorted(item["document_id"] for item in records),
                "source_ids": sorted(item["source_id"] for item in records),
            },
            "question": spec["question"],
            "question_type": spec["question_type"],
        }
        retrieval.append(row)
        ids.append(expected_id)
        type_counts[spec["question_type"]] += 1
        if spec["question_type"] != "hard":
            continue
        if len(records) < 2:
            raise PreparationError(f"{expected_id} hard question must require multiple documents")
        hard_questions.append(row)
        truth = spec["ground_truth"]
        exact_keys(
            truth,
            {"acceptable_variants", "answer_claims", "derivation", "evidence", "failure_conditions", "important_negatives"},
            f"{expected_id}.ground_truth",
        )
        evidence_rows: list[dict[str, Any]] = []
        evidence_ids: set[str] = set()
        for selector in truth["evidence"]:
            exact_keys(selector, {"heading", "id", "occurrence", "role", "upstream_path"}, f"{expected_id}.evidence")
            if selector["id"] in evidence_ids:
                raise PreparationError(f"{expected_id} has duplicate evidence ID {selector['id']}")
            evidence_ids.add(selector["id"])
            document = by_upstream.get(selector["upstream_path"])
            if document is None or selector["upstream_path"] not in documents:
                raise PreparationError(f"{expected_id} evidence is not bound to a required document")
            checked_path = EVALUATION / document["path"]
            payload = checked_path.read_bytes()
            locator = _heading_section(payload, selector, f"{expected_id}.{selector['id']}")
            evidence_rows.append(
                {
                    "document_id": document["document_id"],
                    "file_sha256": sha256_bytes(payload),
                    "id": selector["id"],
                    **locator,
                    "path": checked_path.relative_to(REPO_ROOT).as_posix(),
                    "role": selector["role"],
                    "source_id": document["source_id"],
                    "upstream_path": selector["upstream_path"],
                }
            )
        for collection_name in ("answer_claims", "important_negatives"):
            for claim in truth[collection_name]:
                if not set(claim["evidence_ids"]).issubset(evidence_ids):
                    raise PreparationError(f"{expected_id} {collection_name} references unknown evidence")
        hard_ground_truth.append(
            {
                "authoritative_evidence": evidence_rows,
                "ground_truth": {
                    "acceptable_variants": truth["acceptable_variants"],
                    "answer_claims": truth["answer_claims"],
                    "derivation": truth["derivation"],
                    "failure_conditions": truth["failure_conditions"],
                    "important_negatives": truth["important_negatives"],
                    "required_document_ids": row["qrels"]["document_ids"],
                    "required_source_ids": row["qrels"]["source_ids"],
                },
                "id": expected_id,
                "question": spec["question"],
                "schema_version": "semantic-okf-astro-hard-ground-truth/1.0",
            }
        )

    if ids != [f"q{number:03d}" for number in range(1, 41)]:
        raise PreparationError("question IDs are incomplete")
    if dict(type_counts) != {"direct": 20, "cross-document": 10, "hard": 10}:
        raise PreparationError(f"question type counts are invalid: {dict(type_counts)}")
    payloads = {
        "retrieval-questions.jsonl": jsonl(retrieval),
        "hard-questions.jsonl": jsonl(hard_questions),
        "hard-ground-truth.jsonl": jsonl(hard_ground_truth),
    }
    counts = {
        "answer_claims": sum(len(row["ground_truth"]["answer_claims"]) for row in hard_ground_truth),
        "cross_document": type_counts["cross-document"],
        "direct": type_counts["direct"],
        "evidence_bindings": sum(len(row["authoritative_evidence"]) for row in hard_ground_truth),
        "hard": type_counts["hard"],
        "important_negatives": sum(len(row["ground_truth"]["important_negatives"]) for row in hard_ground_truth),
        "questions": len(retrieval),
    }
    manifest = {
        "contracts": {
            "authority": "Pinned official Astro MDX is authoritative; benchmark labels and all retrieval artifacts are derived.",
            "evidence_locator": "Every hard evidence binding names the exact repo path, heading path, character interval, file digest, and selected-text digest.",
            "prompt_isolation": "Only the question string is supplied to a consultation alternative; qrels and ground truth remain evaluator-only.",
            "qrels": "Qrels contain canonical English documentation routes and their opaque manifest source IDs.",
        },
        "counts": counts,
        "files": {
            name: {"path": f"evaluations/semantic-okf-astro/benchmark/{name}", "row_count": payloads[name].count(b"\n"), "sha256": sha256_bytes(payloads[name])}
            for name in sorted(payloads)
        },
        "question_specs_sha256": sha256_bytes(QUESTION_SPECS.read_bytes()),
        "schema_version": "semantic-okf-astro-benchmark-manifest/1.0",
    }
    payloads["benchmark-manifest.json"] = pretty_json(manifest)
    return payloads


def build_plan_outputs() -> dict[str, bytes]:
    """Derive leakage-free alternative plans from the frozen manifest selection."""

    inventory = json.loads((CORPUS / "input-inventory.json").read_text(encoding="utf-8"))
    source_ids = sorted(item["source_id"] for item in inventory["documents"])
    if len(source_ids) != EXPECTED_DOCUMENTS or len(set(source_ids)) != EXPECTED_DOCUMENTS:
        raise PreparationError("plan selection must contain every frozen source exactly once")
    selection = {"source_ids": source_ids}
    tokenization = {
        "tokenizer": "ascii-alphanumeric-v1",
        "stopwords": "english-v1",
        "min_token_length": 2,
        "ngram_range": [1, 2],
    }
    bm25 = {"k1": 1.2, "b": 0.75, "title_weight": 2.0, "body_weight": 1.0}
    associations = {
        "window_size": 8,
        "min_document_frequency": 2,
        "min_cooccurrence": 2,
        "max_vocabulary": 6000,
        "max_neighbors": 10,
        "minimum_ppmi": 0.0,
    }
    topics = {"topic_count": 24, "max_iterations": 24, "top_terms": 24}
    expansion = {
        "association_terms": 8,
        "topic_terms": 8,
        "association_weight": 0.35,
        "topic_weight": 0.2,
    }
    reranking = {
        "candidate_pool": 160,
        "relevance_weight": 0.7,
        "topic_novelty_weight": 0.15,
        "source_novelty_weight": 0.15,
        "max_per_evidence_identity": 1,
        "rrf_k": 60,
    }
    classical = {
        "schema_version": "1.0",
        "selection": selection,
        "tokenization": tokenization,
        "bm25": bm25,
        "associations": associations,
        "topics": topics,
        "expansion": expansion,
        "reranking": reranking,
    }
    adaptive = {
        "schema_version": "1.1",
        "selection": selection,
        "passages": {"default_mode": "full-record", "markdown_pdf_page_source_ids": []},
        "evidence_identity": {"default_mode": "source-record", "paper_ids_by_source": {}},
        "tokenization": tokenization,
        "bm25": bm25,
        "associations": associations,
        "topics": topics,
        "expansion": expansion,
        "reranking": reranking,
        "adaptive": {
            "maximum_aspects": 10,
            "minimum_aspect_tokens": 4,
            "full_query_weight": 2.0,
            "aspect_weight": 0.25,
            "best_aspect_weight": 0.0,
            "rrf_k": 0,
            "protected_full_results": 12,
            "maximum_novel_aspect_rank": 1,
        },
    }
    embedding = {
        "schema_version": "1.0",
        "selection": selection,
        "chunking": {
            "implementation": "llamaindex",
            "strategy": "semantic",
            "buffer_size": 1,
            "breakpoint_percentile_threshold": 90,
        },
        "embedding": {
            "provider": "sentence-transformers",
            "model_id": "sentence-transformers/all-MiniLM-L6-v2",
            "revision": "1110a243fdf4706b3f48f1d95db1a4f5529b4d41",
            "dimension": 384,
            "normalize": True,
        },
    }
    entity_graph = {
        "schema_version": "2.0",
        "selection": selection,
        "sectioning": {
            "strategy": "markdown-headings-or-bounded-record-v1",
            "maximum_characters": 4000,
        },
        "tokenization": {
            "tokenizer": "ascii-alphanumeric-v1",
            "stopwords": "english-v1",
            "min_token_length": 2,
        },
        "extraction": {
            "ngram_range": [1, 3],
            "minimum_section_frequency": 2,
            "maximum_section_fraction": 0.35,
            "maximum_candidates": 4000,
            "top_candidates_per_section": 16,
        },
        "bm25": {"k1": 1.2, "b": 0.75},
        "graph": {
            "max_co_mentions_per_section": 16,
            "minimum_co_mention_sections": 2,
            "max_co_mention_neighbors": 16,
            "max_edge_evidence_sections": 8,
        },
        "query": {
            "resolved_entities": 40,
            "max_hops": 3,
            "hop_decay": 0.65,
            "reviewed_edge_weight": 1.0,
            "candidate_edge_weight": 0.3,
            "mention_weight": 1.0,
            "candidate_pool": 180,
            "max_per_document": 1,
            "rrf_k": 60,
        },
    }
    policies = {
        "default": "quality",
        "quality": {
            "routes": ["adaptive", "graph_fusion", "bm25", "embedding_hybrid"],
            "weights": [4, 1, 5, 1],
            "rrf_k": 7,
            "protected_route": "adaptive",
            "promotion": {
                "route": "graph_lexical",
                "confirmation_routes": [
                    "adaptive",
                    "graph_lexical",
                    "graph_fusion",
                    "bm25",
                    "embedding_hybrid",
                ],
                "confirmation_depth": 3,
                "minimum_confirmations": 3,
                "maximum_protected_rank": 10,
            },
        },
        "fast": {
            "routes": ["adaptive", "graph_lexical"],
            "weights": [4, 1],
            "rrf_k": 5,
            "protected_route": "adaptive",
            "promotion": {
                "route": "graph_lexical",
                "confirmation_routes": ["adaptive", "graph_lexical"],
                "confirmation_depth": 3,
                "minimum_confirmations": 2,
                "maximum_protected_rank": 3,
            },
        },
        "robust": {
            "routes": ["adaptive"],
            "weights": [1],
            "rrf_k": 0,
            "protected_route": "adaptive",
            "promotion": {
                "route": "adaptive",
                "confirmation_routes": ["adaptive"],
                "confirmation_depth": 1,
                "minimum_confirmations": 1,
                "maximum_protected_rank": 1,
            },
        },
    }
    quality_gates = {
        "required_components": ["adaptive", "entity_graph", "embedding"],
        "protect_candidate_set": True,
        "require_core_parity": True,
        "reviewed_graph_claims_only": True,
        "reviewed_embedding_claims_only": True,
        "candidate_edge_weight": 0.0,
        "maximum_graph_claims_per_facet": 8,
        "maximum_graph_claims_total": 80,
        "maximum_embedding_claims_per_facet": 20,
        "maximum_embedding_claims_total": 240,
        "require_facet_status": True,
        "require_exact_answer_bindings": True,
        "require_child_plan_parity": True,
        "require_total_identity_crosswalk": True,
        "require_component_group_parity": True,
        "require_exact_passage_evidence": True,
        "claim_only_coverage_requires_bindings": True,
    }
    ensemble = {
        "schema_version": "2.0",
        "adaptive": adaptive,
        "entity_graph": entity_graph,
        "embedding": embedding,
        "identity": {"default_grouping": "source-record-v1", "overrides": []},
        "policies": policies,
        "quality_gates": quality_gates,
    }
    values = {
        "adaptive-plan.json": adaptive,
        "classical-plan.json": classical,
        "embedding-plan.json": embedding,
        "ensemble-plan.json": ensemble,
        "entity-graph-plan.json": entity_graph,
    }
    payloads = {name: pretty_json(value) for name, value in values.items()}
    manifest = {
        "authority": "Plans select the complete frozen corpus and define only reproducible derived retrieval artifacts.",
        "files": {
            name: {"path": f"evaluations/semantic-okf-astro/plans/{name}", "sha256": sha256_bytes(payload)}
            for name, payload in sorted(payloads.items())
        },
        "schema_version": "semantic-okf-astro-plan-manifest/1.0",
        "selected_sources": len(source_ids),
        "selection_sha256": sha256_bytes(canonical_json(source_ids).encode("utf-8")),
    }
    payloads["plan-manifest.json"] = pretty_json(manifest)
    return payloads


def _compare_directory(target: Path, outputs: Mapping[Path, bytes]) -> list[str]:
    expected = {path.as_posix() for path in outputs}
    observed = {path.relative_to(target).as_posix() for path in target.rglob("*") if path.is_file()} if target.is_dir() else set()
    errors = [f"missing generated file: {path}" for path in sorted(expected - observed)]
    errors.extend(f"unexpected generated file: {path}" for path in sorted(observed - expected))
    for relative, payload in outputs.items():
        path = target / relative
        if path.is_file() and path.read_bytes() != payload:
            errors.append(f"stale generated file: {relative.as_posix()}")
    return errors


def _publish_corpus(outputs: Mapping[Path, bytes]) -> None:
    EVALUATION.mkdir(parents=True, exist_ok=True)
    stage_root = Path(tempfile.mkdtemp(prefix=".astro-corpus-stage-", dir=EVALUATION))
    candidate = stage_root / "corpus"
    backup = EVALUATION / ".astro-corpus-backup"
    try:
        for relative, payload in outputs.items():
            path = candidate / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(payload)
        if backup.exists():
            shutil.rmtree(backup)
        if CORPUS.exists():
            os.replace(CORPUS, backup)
        os.replace(candidate, CORPUS)
        if backup.exists():
            shutil.rmtree(backup)
    except Exception:
        if not CORPUS.exists() and backup.exists():
            os.replace(backup, CORPUS)
        raise
    finally:
        shutil.rmtree(stage_root, ignore_errors=True)


def _publish_benchmark(outputs: Mapping[str, bytes]) -> None:
    BENCHMARK.mkdir(parents=True, exist_ok=True)
    for name, payload in outputs.items():
        target = BENCHMARK / name
        temporary = target.with_name(f".{target.name}.tmp")
        temporary.write_bytes(payload)
        os.replace(temporary, target)


def _publish_plans(outputs: Mapping[str, bytes]) -> None:
    PLANS.mkdir(parents=True, exist_ok=True)
    for name, payload in outputs.items():
        target = PLANS / name
        temporary = target.with_name(f".{target.name}.tmp")
        temporary.write_bytes(payload)
        os.replace(temporary, target)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--know-store", type=Path, default=REPO_ROOT / "tmp" / "astro-docs-know")
    parser.add_argument("--check", action="store_true", help="Verify generated artifacts without writing them.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        corpus_outputs = build_corpus_outputs(args.know_store.resolve())
        if args.check:
            errors = _compare_directory(CORPUS, corpus_outputs)
            benchmark_outputs = build_benchmark_outputs()
            for name, payload in benchmark_outputs.items():
                path = BENCHMARK / name
                if not path.is_file() or path.read_bytes() != payload:
                    errors.append(f"stale or missing benchmark file: {name}")
            plan_outputs = build_plan_outputs()
            for name, payload in plan_outputs.items():
                path = PLANS / name
                if not path.is_file() or path.read_bytes() != payload:
                    errors.append(f"stale or missing plan file: {name}")
            if errors:
                raise PreparationError(" | ".join(errors[:20]))
        else:
            _publish_corpus(corpus_outputs)
            _publish_benchmark(build_benchmark_outputs())
            _publish_plans(build_plan_outputs())
        result = {"documents": EXPECTED_DOCUMENTS, "hard_questions": 10, "questions": 40, "status": "pass"}
        print(json.dumps(result, sort_keys=True) if args.json else "Astro corpus and benchmark: pass")
        return 0
    except (OSError, ValueError, KeyError, PreparationError, json.JSONDecodeError, yaml.YAMLError) as exc:
        result = {"error": str(exc), "status": "fail"}
        print(json.dumps(result, sort_keys=True) if args.json else f"Astro corpus and benchmark: fail: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
