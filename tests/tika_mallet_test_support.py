from __future__ import annotations

import hashlib
import importlib
import json
import sys
from pathlib import Path
from types import ModuleType
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
BUILD_ROOT = REPO_ROOT / "skills" / "build-semantic-okf-tika-mallet"
BUILD_SCRIPTS = BUILD_ROOT / "scripts"
CONSULT_ROOT = REPO_ROOT / "skills" / "consult-semantic-okf-tika-mallet"
CONSULT_SCRIPTS = CONSULT_ROOT / "scripts"
MODULE_NAMES = (
    "_safe_paths",
    "_semantic_okf",
    "_build_semantic_okf_core",
    "validate_okf_bundle",
    "_tika_ingestion",
    "_tika_mallet_retrieval",
    "build_semantic_okf_tika_mallet",
)


def write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def tree_hashes(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def plans(root: Path) -> tuple[Path, Path]:
    inputs = root / "inputs"
    inputs.mkdir(parents=True)
    (inputs / "guide.pdf").write_bytes(b"portable fake PDF input\n")
    (inputs / "metrics.xlsx").write_bytes(b"portable fake XLSX input\n")
    ingestion = {
        "schema_version": "1.0",
        "bundle": {
            "title": "Portable Tika MALLET test",
            "description": "A unit fixture for format-aware Semantic OKF.",
            "base_iri": "https://example.org/tika-mallet-test/",
            "ontology_iri": "https://example.org/ontology/tika-mallet-test",
            "version_iri": "https://example.org/ontology/tika-mallet-test/1.0.0",
            "prefix": "tmtest",
            "owl_profile": "rl",
        },
        "sources": [
            {
                "id": "office-documents",
                "path": "inputs/*.xlsx",
                "concept_type": "Office Document",
            },
            {
                "id": "pdf-documents",
                "path": "inputs/*.pdf",
                "concept_type": "PDF Document",
            },
        ],
        "tika": {
            "version": "4.0.0-beta-1",
            "verify_default_markdown": True,
            "timeout_seconds": 30,
            "max_input_bytes": 1024,
        },
    }
    retrieval = {
        "schema_version": "1.0",
        "selection": {"source_ids": ["office-documents", "pdf-documents"]},
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
            "max_neighbors": 6,
            "minimum_ppmi": 0.0,
        },
        "topics": {
            "topic_count": 2,
            "num_iterations": 20,
            "num_threads": 1,
            "num_icm_iterations": 0,
            "optimize_interval": 0,
            "optimize_burn_in": 0,
            "alpha_sum": 2.0,
            "beta": 0.01,
            "random_seed": 42,
            "min_document_frequency": 1,
            "max_document_fraction": 1.0,
            "top_terms": 6,
            "timeout_seconds": 30,
        },
        "expansion": {
            "association_terms": 4,
            "topic_terms": 4,
            "association_weight": 0.35,
            "topic_weight": 0.2,
        },
        "reranking": {
            "candidate_pool": 20,
            "relevance_weight": 0.7,
            "topic_novelty_weight": 0.15,
            "source_novelty_weight": 0.15,
            "max_per_evidence_identity": 1,
            "rrf_k": 60,
        },
    }
    ingestion_path = root / "ingestion-plan.json"
    retrieval_path = root / "retrieval-plan.json"
    write_json(ingestion_path, ingestion)
    write_json(retrieval_path, retrieval)
    return ingestion_path, retrieval_path


def load_build_modules() -> tuple[ModuleType, ModuleType, ModuleType]:
    for name in MODULE_NAMES:
        sys.modules.pop(name, None)
    sys.path.insert(0, str(BUILD_SCRIPTS))
    try:
        ingestion = importlib.import_module("_tika_ingestion")
        retrieval = importlib.import_module("_tika_mallet_retrieval")
        wrapper = importlib.import_module("build_semantic_okf_tika_mallet")
    finally:
        sys.path.remove(str(BUILD_SCRIPTS))
    return ingestion, retrieval, wrapper


def fake_topics(
    retrieval: ModuleType,
    documents: list[dict[str, Any]],
    plan: Any,
    runtime: Any,
) -> dict[str, Any]:
    del runtime
    terms = sorted(
        {
            term
            for document in documents
            for term in (
                retrieval._unigrams(document["title"], plan)
                + retrieval._unigrams(document["text"], plan)
            )
        }
    )
    topic_count = plan.raw["topics"]["topic_count"]
    labels = {term: index % topic_count for index, term in enumerate(terms)}
    for document_index, document in enumerate(documents):
        preferred = document_index % topic_count
        weights = [0.2 / (topic_count - 1) for _ in range(topic_count)]
        weights[preferred] = 0.8
        document["topic_weights"] = [
            {"topic_id": f"topic-{index:02d}", "weight": round(weight, 8)}
            for index, weight in enumerate(weights)
        ]
    topic_rows = []
    for topic_index in range(topic_count):
        ordered = sorted(
            terms,
            key=lambda term: (labels[term] != topic_index, term),
        )
        selected = ordered[: plan.raw["topics"]["top_terms"]]
        total = sum(range(1, len(selected) + 1))
        weighted = [
            {
                "term": term,
                "weight": round((len(selected) - rank) / total, 8),
            }
            for rank, term in enumerate(selected)
        ]
        topic_rows.append(
            {
                "topic_id": f"topic-{topic_index:02d}",
                "seed": weighted[0]["term"],
                "term_count": sum(1 for value in labels.values() if value == topic_index),
                "terms": weighted,
            }
        )
    return {
        "schema_version": "1.0",
        "algorithm": retrieval.ALGORITHMS["topics"],
        "requested_topic_count": topic_count,
        "topic_count": topic_count,
        "iterations": plan.raw["topics"]["num_iterations"],
        "term_topics": [
            {"term": term, "topic_id": f"topic-{labels[term]:02d}"}
            for term in terms
        ],
        "topics": topic_rows,
    }


def build_portable_bundle(root: Path) -> tuple[Path, Any, Any, Any]:
    ingestion_path, retrieval_path = plans(root)
    ingestion, retrieval, wrapper = load_build_modules()
    tika_inventory = (
        {
            "path": "tika-app-4.0.0-beta-1.jar",
            "sha256": "a" * 64,
        },
    )
    tika_runtime = ingestion.TikaRuntime(
        java=root / "java",
        java_version='openjdk version "17.0.12"',
        tika_home=root / "tika",
        tika_jar=root / "tika" / "tika-app-4.0.0-beta-1.jar",
        tika_version="4.0.0-beta-1",
        jar_inventory=tika_inventory,
        jar_tree_sha256=ingestion.sha256_json(list(tika_inventory)),
    )
    mallet_inventory = (
        {"path": "lib/mallet-2.1.0.jar", "sha256": "b" * 64},
    )
    mallet_runtime = retrieval.MalletRuntime(
        java=root / "java",
        java_version='openjdk version "17.0.12"',
        mallet_home=root / "mallet",
        mallet_version="2.1.0",
        jar_inventory=mallet_inventory,
        jar_tree_sha256=retrieval.sha256_canonical(list(mallet_inventory)),
    )

    original_preflight_tika = ingestion.preflight_tika
    original_extract_one = ingestion._extract_one
    original_topics = retrieval._derive_topics
    original_preflight_mallet = wrapper.preflight_mallet
    ingestion.preflight_tika = lambda *args, **kwargs: tika_runtime

    def extract_one(runtime: Any, input_path: Path, *, timeout: int) -> tuple[str, dict[str, Any]]:
        del runtime, timeout
        if input_path.suffix == ".pdf":
            body = (
                "Document audit evidence preserves attachment preview, provenance, "
                "and exact source citations."
            )
            media_type = "application/pdf"
        else:
            body = (
                "Spreadsheet validation compares metrics, workbook formulas, audit "
                "evidence, and reproducible extraction."
            )
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        return body, {
            "Content-Type": media_type,
            "X-TIKA:resourceName": input_path.name,
        }

    ingestion._extract_one = extract_one
    retrieval._derive_topics = lambda documents, plan, runtime: fake_topics(
        retrieval, documents, plan, runtime
    )
    wrapper.preflight_mallet = lambda *args, **kwargs: mallet_runtime
    output = root / "bundle"
    try:
        wrapper.atomic_build(
            ingestion_path,
            retrieval_path,
            output,
            java=root / "java",
            tika_home=root / "tika",
            mallet_home=root / "mallet",
        )
    finally:
        ingestion.preflight_tika = original_preflight_tika
        ingestion._extract_one = original_extract_one
        retrieval._derive_topics = original_topics
        wrapper.preflight_mallet = original_preflight_mallet
    return output, ingestion, retrieval, wrapper
