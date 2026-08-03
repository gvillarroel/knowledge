#!/usr/bin/env python3
"""Generate the QEC Semantic OKF manifest, plans, questions, and hard truth."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import tempfile
import shutil
from typing import Any, Mapping, Sequence


ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
SELECTION_PATH = ROOT / "paper-selection.json"
BLUEPRINT_PATH = ROOT / "benchmark" / "benchmark-blueprint.json"
SOURCES = ROOT / "sources"
GENERATED_PATHS = (
    "manifest.json",
    "benchmark/retrieval-questions.jsonl",
    "benchmark/hard-ground-truth.jsonl",
    "benchmark/cohorts.json",
    "benchmark/source-combination.json",
    "plans/classical-plan.json",
    "plans/adaptive-plan.json",
    "plans/embedding-plan.json",
    "plans/entity-graph-plan.json",
    "plans/ensemble-plan.json",
    "guidance/qec-expert.md",
)
PAPER_ID_RE = re.compile(r"^(\d{4})\.(\d{4,5})(v\d+)$")


class BenchmarkError(ValueError):
    """Raised when the frozen QEC benchmark cannot be generated."""


def _canonical_json(value: Any) -> str:
    return (
        json.dumps(
            value,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
            allow_nan=False,
        )
        + "\n"
    )


def _compact_json(value: Any) -> str:
    return (
        json.dumps(
            value,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
            allow_nan=False,
        )
        + "\n"
    )


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _write_text(root: Path, relative: str, text: str) -> None:
    target = root / Path(*relative.split("/"))
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8", newline="\n")


def _load_object(path: Path, *, label: str) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise BenchmarkError(f"{label} must be a JSON object")
    return value


def _source_id(paper_id: str) -> str:
    match = PAPER_ID_RE.fullmatch(paper_id)
    if match is None:
        raise BenchmarkError(f"Invalid paper identity: {paper_id}")
    return f"paper-{match.group(1)}-{match.group(2)}{match.group(3)}"


def _evaluation_source_combination(paper_ids: Sequence[str]) -> dict[str, Any]:
    """Map every immutable ledger identity to its versioned paper identity."""

    return {
        "schema_version": "semantic-okf-evaluation-source-combination/1.0",
        "dataset_id": "quantum-error-correction-papers-40",
        "records": [
            {
                "document_id": paper_id,
                "record_id": f"sources/markdown/{paper_id}",
                "source_id": _source_id(paper_id),
            }
            for paper_id in paper_ids
        ],
    }


def _selection_and_metadata() -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    selection = _load_object(SELECTION_PATH, label="paper selection")
    metadata = _load_object(SOURCES / "metadata.json", label="arXiv metadata")
    inventory = _load_object(SOURCES / "inventory.json", label="source inventory")
    if (
        selection.get("dataset_id") != "quantum-error-correction-papers-40"
        or metadata.get("dataset_id") != selection["dataset_id"]
        or inventory.get("dataset_id") != selection["dataset_id"]
        or inventory.get("paper_count") != 15
    ):
        raise BenchmarkError("Selection, metadata, and inventory identities differ")
    metadata_rows = metadata.get("papers")
    if not isinstance(metadata_rows, list):
        raise BenchmarkError("Normalized metadata has no paper array")
    by_id = {
        row["arxiv_id"]: row
        for row in metadata_rows
        if isinstance(row, dict) and isinstance(row.get("arxiv_id"), str)
    }
    selected_ids = [row["arxiv_id"] for row in selection["papers"]]
    if set(by_id) != set(selected_ids):
        raise BenchmarkError("Normalized metadata does not cover the selection")
    inventory_rows = inventory.get("papers")
    if not isinstance(inventory_rows, list):
        raise BenchmarkError("Source inventory has no papers")
    for row in inventory_rows:
        if not isinstance(row, dict):
            raise BenchmarkError("Invalid source inventory row")
        for path_key, hash_key in (
            ("pdf_path", "pdf_sha256"),
            ("markdown_path", "markdown_sha256"),
        ):
            path = SOURCES / Path(*str(row[path_key]).split("/"))
            if (
                not path.is_file()
                or hashlib.sha256(path.read_bytes()).hexdigest() != row[hash_key]
            ):
                raise BenchmarkError(f"Source inventory drift: {path}")
    return selection, by_id


def _manifest(
    selection: Mapping[str, Any],
    metadata: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    properties = [
        ("paperTitle", "xsd:string"),
        ("selectionDimension", "xsd:string"),
        ("paperId", "xsd:string"),
        ("arxivId", "xsd:string"),
        ("arxivVersion", "xsd:string"),
        ("publicationYear", "xsd:integer"),
        ("authors", "xsd:string"),
        ("primaryCategory", "xsd:string"),
        ("abstract", "xsd:string"),
        ("sourceUrl", "xsd:string"),
        ("pdfUrl", "xsd:string"),
        ("pdfSha256", "xsd:string"),
        ("pageCount", "xsd:integer"),
        ("extractedCharacters", "xsd:integer"),
    ]
    field_map = {
        "title": "paperTitle",
        "description": "selectionDimension",
        "paper_id": "paperId",
        "arxiv_id": "arxivId",
        "arxiv_version": "arxivVersion",
        "publication_year": "publicationYear",
        "authors": "authors",
        "primary_category": "primaryCategory",
        "abstract": "abstract",
        "source_url": "sourceUrl",
        "pdf_url": "pdfUrl",
        "pdf_sha256": "pdfSha256",
        "page_count": "pageCount",
        "extracted_characters": "extractedCharacters",
    }
    sources = []
    for paper in selection["papers"]:
        paper_id = paper["arxiv_id"]
        if metadata[paper_id]["title"] != paper["expected_title"]:
            raise BenchmarkError(f"Metadata title drift: {paper_id}")
        sources.append(
            {
                "id": _source_id(paper_id),
                "kind": "markdown",
                "path": f"sources/markdown/{paper_id}.md",
                "concept_type": "Research Paper",
                "ontology_class": "Paper",
                "fields": field_map,
            }
        )
    return {
        "schema_version": "1.0",
        "bundle": {
            "title": "Quantum Error Correction ArXiv Paper Corpus",
            "description": (
                "Fifteen version-pinned papers spanning surface codes, qLDPC "
                "constructions and decoders, and bosonic quantum error correction."
            ),
            "base_iri": "https://example.org/qec-arxiv-papers/",
            "ontology_iri": "https://example.org/ontology/qec-arxiv-papers",
            "version_iri": "https://example.org/ontology/qec-arxiv-papers/1.0.0",
            "prefix": "qec",
            "owl_profile": "rl",
        },
        "ontology": {
            "classes": [{"name": "Paper", "label": "research paper"}],
            "properties": [
                {
                    "name": name,
                    "kind": "datatype",
                    "domain": "Paper",
                    "range": value_range,
                }
                for name, value_range in properties
            ],
        },
        "rules": [
            {
                "name": "PaperIdentifierRule",
                "target_class": "Paper",
                "path": "paperId",
                "min_count": 1,
                "max_count": 1,
                "datatype": "xsd:string",
                "pattern": "^[0-9]{4}\\.[0-9]{4,5}v[0-9]+$",
                "message": "Every paper must retain one exact versioned arXiv ID.",
                "basis": {
                    "kind": "evidence",
                    "references": ["QEC-ARXIV-SELECTION-1"],
                },
            },
            {
                "name": "PaperDigestRule",
                "target_class": "Paper",
                "path": "pdfSha256",
                "min_count": 1,
                "max_count": 1,
                "datatype": "xsd:string",
                "pattern": "^[0-9a-f]{64}$",
                "message": "Every paper must retain the pinned PDF digest.",
                "basis": {
                    "kind": "evidence",
                    "references": ["QEC-ARXIV-INVENTORY-1"],
                },
            },
            {
                "name": "PaperTitleRule",
                "target_class": "Paper",
                "path": "paperTitle",
                "min_count": 1,
                "max_count": 1,
                "datatype": "xsd:string",
                "pattern": ".+",
                "message": "Every paper must retain its official arXiv title.",
                "basis": {
                    "kind": "evidence",
                    "references": ["QEC-ARXIV-METADATA-1"],
                },
            },
        ],
        "sources": sources,
    }


def _classical_plan(source_ids: list[str]) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "selection": {"source_ids": source_ids},
        "tokenization": {
            "tokenizer": "ascii-alphanumeric-v1",
            "stopwords": "english-v1",
            "min_token_length": 2,
            "ngram_range": [1, 2],
        },
        "bm25": {
            "k1": 1.2,
            "b": 0.75,
            "title_weight": 2.0,
            "body_weight": 1.0,
        },
        "associations": {
            "window_size": 8,
            "min_document_frequency": 2,
            "min_cooccurrence": 2,
            "max_vocabulary": 5000,
            "max_neighbors": 10,
            "minimum_ppmi": 0.0,
        },
        "topics": {
            "topic_count": 12,
            "max_iterations": 24,
            "top_terms": 24,
        },
        "expansion": {
            "association_terms": 8,
            "topic_terms": 8,
            "association_weight": 0.35,
            "topic_weight": 0.2,
        },
        "reranking": {
            "candidate_pool": 100,
            "relevance_weight": 0.7,
            "topic_novelty_weight": 0.15,
            "source_novelty_weight": 0.15,
            "max_per_evidence_identity": 1,
            "rrf_k": 60,
        },
    }


def _adaptive_plan(
    source_ids: list[str],
    paper_ids: list[str],
) -> dict[str, Any]:
    value = _classical_plan(source_ids)
    value["schema_version"] = "1.1"
    value["passages"] = {
        "default_mode": "full-record",
        "markdown_pdf_page_source_ids": source_ids,
    }
    value["evidence_identity"] = {
        "default_mode": "source-record",
        "paper_ids_by_source": dict(zip(source_ids, paper_ids)),
    }
    value["adaptive"] = {
        "maximum_aspects": 10,
        "minimum_aspect_tokens": 4,
        "full_query_weight": 2.0,
        "aspect_weight": 0.25,
        "best_aspect_weight": 0.0,
        "rrf_k": 0,
        "protected_full_results": 10,
        "maximum_novel_aspect_rank": 1,
    }
    return value


def _embedding_plan(source_ids: list[str]) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "selection": {"source_ids": source_ids},
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


def _entity_graph_plan(source_ids: list[str]) -> dict[str, Any]:
    return {
        "schema_version": "2.0",
        "selection": {"source_ids": source_ids},
        "sectioning": {
            "strategy": "markdown-headings-or-bounded-record-v1",
            "maximum_characters": 12000,
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
            "maximum_candidates": 1200,
            "top_candidates_per_section": 12,
        },
        "bm25": {"k1": 1.2, "b": 0.75},
        "graph": {
            "max_co_mentions_per_section": 12,
            "minimum_co_mention_sections": 2,
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
            "candidate_pool": 100,
            "max_per_document": 1,
            "rrf_k": 60,
        },
    }


def _ensemble_plan(
    adaptive: Mapping[str, Any],
    embedding: Mapping[str, Any],
    entity: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": "2.0",
        "adaptive": adaptive,
        "embedding": embedding,
        "entity_graph": entity,
        "identity": {"default_grouping": "source-record-v1", "overrides": []},
        "quality_gates": {
            "candidate_edge_weight": 0.0,
            "claim_only_coverage_requires_bindings": True,
            "maximum_embedding_claims_per_facet": 20,
            "maximum_embedding_claims_total": 240,
            "maximum_graph_claims_per_facet": 8,
            "maximum_graph_claims_total": 80,
            "protect_candidate_set": True,
            "require_child_plan_parity": True,
            "require_component_group_parity": True,
            "require_core_parity": True,
            "require_exact_answer_bindings": True,
            "require_exact_passage_evidence": True,
            "require_facet_status": True,
            "require_total_identity_crosswalk": True,
            "required_components": ["adaptive", "entity_graph", "embedding"],
            "reviewed_embedding_claims_only": True,
            "reviewed_graph_claims_only": True,
        },
        "policies": {
            "default": "quality",
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
            "quality": {
                "routes": [
                    "adaptive",
                    "graph_fusion",
                    "bm25",
                    "embedding_hybrid",
                ],
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
        },
    }


def _page_one_evidence(paper_id: str) -> dict[str, Any]:
    path = (
        ROOT / "sources" / "markdown" / f"{paper_id}.md"
    )
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")
    start = text.find("## PDF page 1\n")
    if start < 0:
        raise BenchmarkError(f"Paper has no PDF page 1 locator: {paper_id}")
    end = text.find("\n## PDF page 2\n", start)
    if end < 0:
        end = len(text)
    excerpt = text[start:end]
    return {
        "path": path.relative_to(REPO).as_posix(),
        "locator": "PDF-page-1",
        "char_start": start,
        "char_end": end,
        "text_length": len(excerpt),
        "text_sha256": _sha256_text(excerpt),
    }


def _questions_and_truth(
    blueprint: Mapping[str, Any],
    selected_ids: set[str],
) -> tuple[str, str, dict[str, Any]]:
    rows = blueprint.get("questions")
    if not isinstance(rows, list) or len(rows) != 40:
        raise BenchmarkError("Benchmark blueprint must contain 40 questions")
    question_lines: list[str] = []
    hard_lines: list[str] = []
    seen: set[str] = set()
    for number, row in enumerate(rows, start=1):
        if not isinstance(row, dict):
            raise BenchmarkError(f"Question blueprint row {number} is invalid")
        identifier = row.get("id")
        expected_prefix = f"q{number:03d}-"
        papers = row.get("focus_papers")
        if (
            not isinstance(identifier, str)
            or not identifier.startswith(expected_prefix)
            or identifier in seen
            or not isinstance(row.get("question"), str)
            or not isinstance(papers, list)
            or papers != sorted(set(papers))
            or not papers
            or not set(papers).issubset(selected_ids)
        ):
            raise BenchmarkError(f"Question blueprint row {number} is incomplete")
        seen.add(identifier)
        question = {
            "id": identifier,
            "qrels": {
                "document_ids": papers,
                "paper_ids": papers,
                "source_ids": [_source_id(paper_id) for paper_id in papers],
            },
            "question": row["question"],
            "question_type": "hard" if number >= 31 else "cross-paper",
        }
        question_lines.append(_compact_json(question))
        if number < 31:
            continue

        claim_ids: list[str] = []
        authoritative: list[dict[str, Any]] = []
        for index, paper_id in enumerate(papers, start=1):
            claim_id = (
                f"{identifier.split('-', 1)[0]}-"
                f"{paper_id.replace('.', '-').replace('v', '-v')}-e{index}"
            )
            claim_ids.append(claim_id)
            authoritative.append(
                {
                    "claim_id": claim_id,
                    "claim_kind": "reviewed-paper-evidence",
                    "interpretation": row["required_points"][
                        (index - 1) % len(row["required_points"])
                    ],
                    "paper_evidence": [_page_one_evidence(paper_id)],
                    "paper_id": paper_id,
                    "review_state": "reviewed",
                }
            )
        prefix = identifier.split("-", 1)[0]
        answer_claims = [
            {
                "evidence_claim_ids": [claim_ids[index % len(claim_ids)]],
                "id": f"{prefix}-a{index + 1}",
                "statement": statement,
            }
            for index, statement in enumerate(row["required_points"])
        ]
        negatives = [
            {
                "evidence_claim_ids": claim_ids,
                "id": f"{prefix}-n{index + 1}",
                "statement": statement,
            }
            for index, statement in enumerate(row.get("important_negatives", []))
        ]
        hard = {
            "authoritative_evidence": authoritative,
            "ground_truth": {
                "acceptable_variants": [],
                "answer_claims": answer_claims,
                "derivation": (
                    [
                        {
                            "conclusion": (
                                "The supported answer must join the reviewed "
                                "paper-specific claims without erasing their scope."
                            ),
                            "inputs": [claim["id"] for claim in answer_claims],
                            "operation": "join",
                        }
                    ]
                    if len(answer_claims) > 1
                    else []
                ),
                "important_negatives": negatives,
                "required_paper_ids": papers,
                "required_source_ids": [_source_id(paper_id) for paper_id in papers],
            },
            "id": identifier,
            "question": row["question"],
            "schema_version": "semantic-okf-hard-ground-truth/1.0",
        }
        hard_lines.append(_compact_json(hard))
    cohorts = {
        "schema_version": "semantic-okf-evaluation-cohorts/1.0",
        "dataset_id": "quantum-error-correction-papers-40",
        "cohorts": {
            "development": [f"q{number:03d}" for number in range(1, 31)],
            "hard": [f"q{number:03d}" for number in range(31, 41)],
        },
    }
    return "".join(question_lines), "".join(hard_lines), cohorts


def _guidance() -> str:
    return """# Quantum Error Correction Paper Expert

## Scope

Answer comparative questions about the bundled surface-code, qLDPC decoder and
construction, and bosonic-code papers. Keep experimental results, asymptotic
theorems, reviews, and proposed mechanisms distinct.

## Application workflow

Decompose the request by code family, error model, decoder, evidence type, and
claimed scale. Search the bundled ledger, deduplicate by versioned arXiv paper,
open the selected concepts, and compare only claims supported by exact paper
text.

## Decision rules

Attribute thresholds and logical-error measurements to their reported noise and
experimental setting. Distinguish finite-code simulations from asymptotic
qLDPC theorems. Distinguish break-even memory, fault-tolerant operations, and
universal fault-tolerant computation. Preserve important negative boundaries
when a source reports only one platform, error set, or code family.

## Evidence and limits

Cite exact bundled concept paths and PDF-page headings. Treat the routing
profile as non-authoritative retrospective discovery evidence. Label synthesis
across papers, and stop when the fifteen-paper snapshot does not support a
requested generalization.
"""


def _generate(candidate: Path) -> None:
    selection, metadata = _selection_and_metadata()
    blueprint = _load_object(BLUEPRINT_PATH, label="benchmark blueprint")
    selected_ids = [row["arxiv_id"] for row in selection["papers"]]
    source_ids = [_source_id(paper_id) for paper_id in selected_ids]
    combination = _evaluation_source_combination(selected_ids)
    manifest = _manifest(selection, metadata)
    questions, truth, cohorts = _questions_and_truth(
        blueprint,
        set(selected_ids),
    )
    classical = _classical_plan(source_ids)
    adaptive = _adaptive_plan(source_ids, selected_ids)
    embedding = _embedding_plan(source_ids)
    entity = _entity_graph_plan(source_ids)
    ensemble = _ensemble_plan(adaptive, embedding, entity)
    payloads = {
        "manifest.json": _canonical_json(manifest),
        "benchmark/retrieval-questions.jsonl": questions,
        "benchmark/hard-ground-truth.jsonl": truth,
        "benchmark/cohorts.json": _canonical_json(cohorts),
        "benchmark/source-combination.json": _canonical_json(combination),
        "plans/classical-plan.json": _canonical_json(classical),
        "plans/adaptive-plan.json": _canonical_json(adaptive),
        "plans/embedding-plan.json": _canonical_json(embedding),
        "plans/entity-graph-plan.json": _canonical_json(entity),
        "plans/ensemble-plan.json": _canonical_json(ensemble),
        "guidance/qec-expert.md": _guidance(),
    }
    for relative, text in payloads.items():
        _write_text(candidate, relative, text)


def build_parser() -> argparse.ArgumentParser:
    """Build the deterministic generation command line."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Compare a fresh generation with every accepted output",
    )
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Replace every deterministic generated output with a fresh build",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Generate or check the QEC benchmark contract."""

    args = build_parser().parse_args(argv)
    if args.check and args.refresh:
        raise SystemExit("--check and --refresh are mutually exclusive")
    temporary = Path(tempfile.mkdtemp(prefix=".qec-benchmark-", dir=ROOT))
    candidate = temporary / "candidate"
    candidate.mkdir()
    try:
        _generate(candidate)
        if args.check:
            changed = [
                relative
                for relative in GENERATED_PATHS
                if not (ROOT / relative).is_file()
                or (ROOT / relative).read_bytes()
                != (candidate / relative).read_bytes()
            ]
            if changed:
                raise BenchmarkError(
                    f"Generated benchmark drift: {changed!r}"
                )
            status = "pass"
        elif args.refresh:
            for relative in GENERATED_PATHS:
                target = ROOT / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(candidate / relative, target)
            status = "refreshed"
        else:
            existing = [
                relative for relative in GENERATED_PATHS if (ROOT / relative).exists()
            ]
            if existing:
                raise BenchmarkError(
                    f"Generated benchmark outputs already exist: {existing!r}"
                )
            for relative in GENERATED_PATHS:
                target = ROOT / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(candidate / relative, target)
            status = "created"
        result = {
            "status": status,
            "dataset_id": "quantum-error-correction-papers-40",
            "generated": {
                relative: hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
                for relative in GENERATED_PATHS
            },
        }
    except (BenchmarkError, OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, sort_keys=True))
        return 2
    finally:
        shutil.rmtree(temporary, ignore_errors=True)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
