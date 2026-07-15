#!/usr/bin/env python3
"""Compare legacy, embedding, classical, entity-graph, and adaptive retrieval routes."""

from __future__ import annotations

import argparse
import importlib
import importlib.util
import json
import statistics
import sys
import time
from pathlib import Path
from types import ModuleType
from typing import Any, Callable, Sequence


SCHEMA_VERSION = "1.5"
BASE_SCHEMA_VERSION = "1.2"
CLASSICAL_ARTIFACTS = (
    "classical/index.json",
    "classical/documents.jsonl",
    "classical/lexicon.json",
    "classical/associations.jsonl",
    "classical/topics.json",
    "classical/build-report.json",
)
ENTITY_GRAPH_ARTIFACTS = (
    "entity-graph/index.json",
    "entity-graph/entities.jsonl",
    "entity-graph/sections.jsonl",
    "entity-graph/mentions.jsonl",
    "entity-graph/edges.jsonl",
    "entity-graph/lexicon.json",
    "entity-graph/build-report.json",
)
ADAPTIVE_ARTIFACTS = (
    "adaptive/index.json",
    "adaptive/documents.jsonl",
    "adaptive/lexicon.json",
    "adaptive/associations.jsonl",
    "adaptive/topics.json",
    "adaptive/build-report.json",
)


def _load_module(name: str, path: Path) -> ModuleType:
    specification = importlib.util.spec_from_file_location(name, path)
    if specification is None or specification.loader is None:
        raise RuntimeError(f"cannot load Python module from {path}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


SCRIPT_PATH = Path(__file__).resolve()
EVALUATION_ROOT = SCRIPT_PATH.parents[1]
BASE_COMPARATOR_PATH = (
    EVALUATION_ROOT.parent / "semantic-okf-embeddings" / "scripts" / "compare_retrieval.py"
)
BASE = _load_module("semantic_okf_evidence_valid_comparator_v12", BASE_COMPARATOR_PATH)
ComparisonError = BASE.ComparisonError


def _load_classical_runtime(consult_script: Path) -> ModuleType:
    support = consult_script.parent / "_classical_snapshot.py"
    if not support.is_file():
        raise ComparisonError(f"Classical consultation support is missing: {support}")
    try:
        return _load_module("semantic_okf_classical_comparison_runtime", support)
    except (ImportError, OSError, RuntimeError, SyntaxError) as exc:
        raise ComparisonError(f"Cannot load the classical consultation runtime: {exc}") from exc


def _load_adaptive_runtime(consult_script: Path) -> ModuleType:
    support = consult_script.parent / "_adaptive_snapshot.py"
    if not support.is_file():
        raise ComparisonError(f"Adaptive consultation support is missing: {support}")
    try:
        return _load_module("semantic_okf_adaptive_comparison_runtime", support)
    except (ImportError, OSError, RuntimeError, SyntaxError) as exc:
        raise ComparisonError(f"Cannot load the adaptive consultation runtime: {exc}") from exc


def _load_embedding_runtime(consult_script: Path) -> ModuleType:
    support = consult_script.parent / "_embedding_snapshot.py"
    if not support.is_file():
        raise ComparisonError(f"Embedding consultation support is missing: {support}")
    try:
        return _load_module("semantic_okf_embedding_comparison_runtime", support)
    except (ImportError, OSError, RuntimeError, SyntaxError) as exc:
        raise ComparisonError(f"Cannot load the embedding consultation runtime: {exc}") from exc


def _load_entity_graph_runtime(consult_script: Path) -> ModuleType:
    model = consult_script.parent / "_entity_graph_model.py"
    support = consult_script.parent / "_entity_graph_snapshot.py"
    if not model.is_file() or not support.is_file():
        raise ComparisonError(f"Entity-graph consultation support is missing beside: {consult_script}")
    try:
        _load_module("_entity_graph_model", model)
        return _load_module("semantic_okf_entity_graph_comparison_runtime", support)
    except (ImportError, OSError, RuntimeError, SyntaxError) as exc:
        raise ComparisonError(f"Cannot load the entity-graph consultation runtime: {exc}") from exc


def _cached_embedding_provider(runtime: ModuleType, snapshot: Any) -> Callable[..., Any] | None:
    config = snapshot.index["embedding"]
    if config["provider"] != "sentence-transformers":
        return None
    try:
        model_module = importlib.import_module("sentence_transformers")
        model_class = getattr(model_module, "SentenceTransformer")
        model_path = runtime._resolve_sentence_transformer_snapshot(config)
        with runtime._offline_model_environment():
            model = model_class(
                str(model_path),
                device="cpu",
                local_files_only=True,
                trust_remote_code=False,
            )
    except Exception as exc:
        raise ComparisonError(f"Cannot initialize the pinned local embedding model: {exc}") from exc

    def encode(text: str, active_config: dict[str, Any]) -> Any:
        kwargs = {
            "normalize_embeddings": bool(active_config["normalize"]),
            "show_progress_bar": False,
            "convert_to_numpy": True,
        }
        with runtime._offline_model_environment():
            if active_config["encoding"]["query"] == "query" and callable(
                getattr(model, "encode_query", None)
            ):
                value = model.encode_query([text], **kwargs)
            else:
                value = model.encode([text], **kwargs)
        return runtime._sequence_from_model(value)

    return encode


def _embedding_hits(
    runtime: ModuleType,
    snapshot: Any,
    embedder: Callable[..., Any] | None,
    query: str,
    mode: str,
    top_k: int,
) -> list[Any]:
    try:
        payload = runtime.search_snapshot(
            snapshot,
            query,
            requested_mode=mode,
            top_k=top_k,
            embedder=embedder,
        )
    except Exception as exc:
        if isinstance(exc, (KeyboardInterrupt, SystemExit)):
            raise
        raise ComparisonError(f"Embedding {mode} search failed: {exc}") from exc
    return BASE.parse_search_output(payload, top_k)


def _classical_hits(
    runtime: ModuleType,
    snapshot: Any,
    query: str,
    mode: str,
    top_k: int,
) -> list[Any]:
    try:
        payload = runtime.search_snapshot(snapshot, query, mode, top_k)
    except Exception as exc:
        if isinstance(exc, (KeyboardInterrupt, SystemExit)):
            raise
        raise ComparisonError(f"Classical {mode} search failed: {exc}") from exc
    normalized = dict(payload)
    normalized["results"] = [
        {**item, "chunk_id": item.get("chunk_id") or item.get("document_id")}
        for item in payload.get("results", [])
    ]
    return BASE.parse_search_output(normalized, top_k)


def _adaptive_hits(
    runtime: ModuleType,
    snapshot: Any,
    query: str,
    top_k: int,
) -> list[Any]:
    try:
        payload = runtime.search_snapshot(snapshot, query, "adaptive", top_k)
    except Exception as exc:
        if isinstance(exc, (KeyboardInterrupt, SystemExit)):
            raise
        raise ComparisonError(f"Adaptive search failed: {exc}") from exc
    normalized = dict(payload)
    normalized["results"] = [
        {**item, "chunk_id": item.get("chunk_id") or item.get("document_id")}
        for item in payload.get("results", [])
    ]
    return BASE.parse_search_output(normalized, top_k)


def _entity_graph_hits(
    runtime: ModuleType,
    snapshot: Any,
    query: str,
    mode: str,
    top_k: int,
) -> list[Any]:
    try:
        payload = runtime.search_snapshot(snapshot, query, mode, top_k)
    except Exception as exc:
        if isinstance(exc, (KeyboardInterrupt, SystemExit)):
            raise
        raise ComparisonError(f"Entity-graph {mode} search failed: {exc}") from exc
    normalized = dict(payload)
    normalized["results"] = [
        {**item, "chunk_id": item.get("chunk_id") or item.get("section_id")}
        for item in payload.get("results", [])
    ]
    return BASE.parse_search_output(normalized, top_k)


def _mean_metrics(rows: Sequence[dict[str, Any]], key: str) -> dict[str, float]:
    names = [
        *(f"recall_at_{cutoff}" for cutoff in BASE.METRIC_CUTOFFS),
        "mrr_at_10",
        "ndcg_at_10",
    ]
    return {
        name: statistics.fmean(float(row[key][name]) for row in rows)
        for name in names
    }


def _cohort_summary(rows: Sequence[dict[str, Any]]) -> dict[str, Any]:
    returned = sum(int(row["evidence_validity"]["returned"]) for row in rows)
    valid = sum(int(row["evidence_validity"]["valid"]) for row in rows)
    return {
        "query_count": len(rows),
        "error_count": sum(row["error"] is not None for row in rows),
        "paper_metrics": _mean_metrics(rows, "paper_metrics"),
        "source_metrics": _mean_metrics(rows, "source_metrics"),
        "evidence_validity": {
            "returned": returned,
            "valid": valid,
            "invalid": returned - valid,
            "ratio": valid / returned if returned else None,
        },
    }


def _attach_cohorts(route: dict[str, Any], original_ids: set[str], hard_ids: set[str]) -> None:
    rows = route["queries"]
    original = [row for row in rows if row["question_id"] in original_ids]
    hard = [row for row in rows if row["question_id"] in hard_ids]
    if len(original) != len(original_ids) or len(hard) != len(hard_ids):
        raise ComparisonError(f"Route {route['name']} did not evaluate every declared cohort question")
    route["cohorts"] = {
        "original_30": _cohort_summary(original),
        "hard_10": _cohort_summary(hard),
    }


def _bundle_fingerprint(bundle: Path) -> dict[str, Any]:
    result = BASE.bundle_fingerprint(bundle)
    key_artifacts = dict(result["key_artifacts"])
    for relative in (*CLASSICAL_ARTIFACTS, *ENTITY_GRAPH_ARTIFACTS, *ADAPTIVE_ARTIFACTS):
        path = bundle / relative
        if path.is_file():
            key_artifacts[relative] = {
                "bytes": path.stat().st_size,
                "sha256": BASE.sha256_file(path),
            }
    result["key_artifacts"] = dict(sorted(key_artifacts.items()))
    return result


def _bundle_report(bundle: Path, inventory: dict[str, Any]) -> dict[str, Any]:
    return {
        "path": BASE._report_path(bundle),
        "fingerprint": _bundle_fingerprint(bundle),
        "input_coverage": BASE.bundle_input_coverage(bundle, inventory),
    }


def _authoritative_files(bundle: Path) -> list[str]:
    return [
        path.relative_to(bundle).as_posix()
        for path in sorted(bundle.rglob("*"))
        if path.is_file()
        and path.relative_to(bundle).parts[0] not in {"retrieval", "classical", "entity-graph", "adaptive"}
    ]


def _core_fingerprint(bundle: Path) -> dict[str, Any]:
    relative_files = _authoritative_files(bundle)
    key_artifacts = {
        relative: (
            {
                "bytes": (bundle / relative).stat().st_size,
                "sha256": BASE.sha256_file(bundle / relative),
            }
            if (bundle / relative).is_file()
            else None
        )
        for relative in BASE.CORE_KEY_ARTIFACTS
    }
    return {
        "file_count": len(relative_files),
        "logical_tree_sha256": BASE.logical_tree_sha256(bundle, relative_files),
        "key_artifacts": key_artifacts,
    }


def _compare_core(left_bundle: Path, right_bundle: Path) -> dict[str, Any]:
    left_files = set(_authoritative_files(left_bundle))
    right_files = set(_authoritative_files(right_bundle))
    left = _core_fingerprint(left_bundle)
    right = _core_fingerprint(right_bundle)
    artifact_parity = {
        relative: {
            "equal": left["key_artifacts"][relative] is not None
            and right["key_artifacts"][relative] is not None
            and left["key_artifacts"][relative]["sha256"]
            == right["key_artifacts"][relative]["sha256"],
            "legacy": left["key_artifacts"][relative],
            "new": right["key_artifacts"][relative],
        }
        for relative in BASE.CORE_KEY_ARTIFACTS
    }
    file_set_equal = left_files == right_files
    tree_equal = left["logical_tree_sha256"] == right["logical_tree_sha256"]
    return {
        "status": (
            "pass"
            if file_set_equal
            and tree_equal
            and all(item["equal"] for item in artifact_parity.values())
            else "fail"
        ),
        "authoritative_file_set": {
            "equal": file_set_equal,
            "legacy_count": len(left_files),
            "new_count": len(right_files),
            "missing_from_new": sorted(left_files - right_files),
            "unexpected_in_new": sorted(right_files - left_files),
        },
        "logical_core_tree_equal": tree_equal,
        "key_artifacts_equal": all(item["equal"] for item in artifact_parity.values()),
        "key_artifacts": artifact_parity,
        "legacy": left,
        "new": right,
    }


def _file_fingerprint(path: Path) -> dict[str, Any]:
    return {
        "path": BASE._report_path(path),
        "bytes": path.stat().st_size,
        "sha256": BASE.sha256_file(path),
    }


def _parity_report(
    legacy: Path,
    embedding: Path,
    classical: Path,
    entity_graph: Path,
    adaptive: Path,
) -> dict[str, Any]:
    pairs = {
        "legacy_vs_embedding": _compare_core(legacy, embedding),
        "legacy_vs_classical": _compare_core(legacy, classical),
        "legacy_vs_entity_graph": _compare_core(legacy, entity_graph),
        "embedding_vs_classical": _compare_core(embedding, classical),
        "embedding_vs_entity_graph": _compare_core(embedding, entity_graph),
        "classical_vs_entity_graph": _compare_core(classical, entity_graph),
        "legacy_vs_adaptive": _compare_core(legacy, adaptive),
        "embedding_vs_adaptive": _compare_core(embedding, adaptive),
        "classical_vs_adaptive": _compare_core(classical, adaptive),
        "entity_graph_vs_adaptive": _compare_core(entity_graph, adaptive),
    }
    return {
        "status": "pass" if all(value["status"] == "pass" for value in pairs.values()) else "fail",
        "pairs": pairs,
    }


def _validate_inputs(args: argparse.Namespace) -> tuple[dict[str, Any], list[Any], dict[str, Path]]:
    if args.top_k < 10:
        raise ComparisonError("--top-k must be at least 10 for the declared metrics.")
    inventory = BASE.load_inventory(args.inventory)
    questions = BASE.load_questions(args.questions)
    if len(questions) != 40:
        raise ComparisonError("The expanded comparison requires exactly 40 questions.")
    bundles = {
        "legacy": args.legacy_bundle.resolve(),
        "embedding": args.embedding_bundle.resolve(),
        "classical": args.classical_bundle.resolve(),
        "entity_graph": args.entity_graph_bundle.resolve(),
        "adaptive": args.adaptive_bundle.resolve(),
    }
    for label, path in bundles.items():
        if not path.is_dir():
            raise ComparisonError(f"{label} bundle is not a directory: {path}")
    for label, path in (
        ("embedding consultation script", args.embedding_consult_script.resolve()),
        ("classical consultation script", args.classical_consult_script.resolve()),
        ("entity-graph consultation script", args.entity_graph_consult_script.resolve()),
        ("adaptive consultation script", args.adaptive_consult_script.resolve()),
    ):
        if not path.is_file():
            raise ComparisonError(f"{label} is missing: {path}")
    return inventory, questions, bundles


def run_comparison(args: argparse.Namespace) -> dict[str, Any]:
    """Run thirteen routes while retaining schema 1.2 evidence-valid hit contracts."""

    inventory, questions, bundles = _validate_inputs(args)
    raw_verification: dict[str, Any] | None = None
    if args.input_root is not None:
        raw_verification = BASE.verify_input_inventory(args.input_root, inventory)
        if raw_verification["status"] != "pass" and not args.allow_input_drift:
            raise ComparisonError(
                "Raw input inventory verification failed; use --allow-input-drift only for diagnostics."
            )

    ledgers = {
        name: BASE.AuthoritativeLedger.from_bundle(bundle)
        for name, bundle in bundles.items()
    }
    original_ids = {question.identifier for question in questions[:30]}
    hard_ids = {question.identifier for question in questions[30:]}

    legacy_setup_started = time.perf_counter()
    legacy_index = BASE.LegacyLexicalIndex.from_ledger(ledgers["legacy"])
    legacy_setup_ms = (time.perf_counter() - legacy_setup_started) * 1000.0
    routes = [
        BASE.evaluate_route(
            "legacy_lexical",
            bundles["legacy"],
            ledgers["legacy"],
            questions,
            lambda query: legacy_index.search(query, args.top_k),
            continue_on_error=args.continue_on_error,
        )
    ]
    routes[0]["setup_ms"] = legacy_setup_ms
    routes[0]["timing_scope"] = (
        "In-process evaluator TF-IDF-like lexical search after one ledger load and index setup."
    )

    embedding_script = args.embedding_consult_script.resolve()
    embedding_runtime = _load_embedding_runtime(embedding_script)
    embedding_setup_started = time.perf_counter()
    try:
        embedding_snapshot = embedding_runtime.load_snapshot(bundles["embedding"])
        embedding_provider = _cached_embedding_provider(
            embedding_runtime, embedding_snapshot
        )
    except Exception as exc:
        if isinstance(exc, (KeyboardInterrupt, SystemExit)):
            raise
        if isinstance(exc, ComparisonError):
            raise
        raise ComparisonError(f"Embedding snapshot validation failed: {exc}") from exc
    embedding_setup_ms = (time.perf_counter() - embedding_setup_started) * 1000.0
    for route_name, mode in (
        ("new_lexical", "lexical"),
        ("vector", "vector"),
        ("hybrid", "hybrid"),
    ):
        route = BASE.evaluate_route(
            route_name,
            bundles["embedding"],
            ledgers["embedding"],
            questions,
            lambda query, selected=mode: _embedding_hits(
                embedding_runtime,
                embedding_snapshot,
                embedding_provider,
                query,
                selected,
                args.top_k,
            ),
            continue_on_error=args.continue_on_error,
        )
        route["setup_ms"] = embedding_setup_ms if mode == "lexical" else 0.0
        route["timing_scope"] = (
            "In-process search after one read-only embedding snapshot validation and one pinned local "
            "model load; shared setup is reported on new_lexical only."
        )
        routes.append(route)

    entity_runtime = _load_entity_graph_runtime(args.entity_graph_consult_script.resolve())
    entity_setup_started = time.perf_counter()
    try:
        entity_snapshot = entity_runtime.load_snapshot(
            bundles["entity_graph"], deep_validation=True
        )
    except Exception as exc:
        if isinstance(exc, (KeyboardInterrupt, SystemExit)):
            raise
        raise ComparisonError(f"Entity-graph snapshot failed independent deep validation: {exc}") from exc
    entity_setup_ms = (time.perf_counter() - entity_setup_started) * 1000.0
    for route_name, mode in (
        ("entity_graph_lexical", "lexical"),
        ("entity_graph_entity", "entity"),
        ("entity_graph_traversal", "traversal"),
        ("entity_graph_fusion", "fusion"),
    ):
        route = BASE.evaluate_route(
            route_name,
            bundles["entity_graph"],
            ledgers["entity_graph"],
            questions,
            lambda query, selected=mode: _entity_graph_hits(
                entity_runtime,
                entity_snapshot,
                query,
                selected,
                args.top_k,
            ),
            continue_on_error=args.continue_on_error,
        )
        route["setup_ms"] = entity_setup_ms if mode == "lexical" else 0.0
        route["timing_scope"] = (
            "In-process search after one read-only snapshot load and independent full graph rederivation; "
            "the shared deep-validation setup is reported on entity_graph_lexical only."
        )
        routes.append(route)

    classical_runtime = _load_classical_runtime(args.classical_consult_script.resolve())
    classical_setup_started = time.perf_counter()
    try:
        classical_snapshot = classical_runtime.load_snapshot(
            bundles["classical"], deep_validation=True
        )
    except Exception as exc:
        if isinstance(exc, (KeyboardInterrupt, SystemExit)):
            raise
        raise ComparisonError(f"Classical snapshot failed independent deep validation: {exc}") from exc
    classical_setup_ms = (time.perf_counter() - classical_setup_started) * 1000.0
    for route_name, mode in (
        ("classical_bm25", "bm25"),
        ("classical_topic", "topic"),
        ("classical_association", "association"),
        ("classical_fusion", "fusion"),
    ):
        route = BASE.evaluate_route(
            route_name,
            bundles["classical"],
            ledgers["classical"],
            questions,
            lambda query, selected=mode: _classical_hits(
                classical_runtime,
                classical_snapshot,
                query,
                selected,
                args.top_k,
            ),
            continue_on_error=args.continue_on_error,
        )
        route["setup_ms"] = classical_setup_ms if mode == "bm25" else 0.0
        route["timing_scope"] = (
            "In-process search after one read-only snapshot load and independent full rederivation; "
            "the shared deep-validation setup is reported on classical_bm25 only."
        )
        routes.append(route)

    adaptive_runtime = _load_adaptive_runtime(args.adaptive_consult_script.resolve())
    adaptive_setup_started = time.perf_counter()
    try:
        adaptive_snapshot = adaptive_runtime.load_snapshot(
            bundles["adaptive"], deep_validation=True
        )
    except Exception as exc:
        if isinstance(exc, (KeyboardInterrupt, SystemExit)):
            raise
        raise ComparisonError(f"Adaptive snapshot failed independent deep validation: {exc}") from exc
    adaptive_setup_ms = (time.perf_counter() - adaptive_setup_started) * 1000.0
    route = BASE.evaluate_route(
        "adaptive_fusion",
        bundles["adaptive"],
        ledgers["adaptive"],
        questions,
        lambda query: _adaptive_hits(
            adaptive_runtime,
            adaptive_snapshot,
            query,
            args.top_k,
        ),
        continue_on_error=args.continue_on_error,
    )
    route["setup_ms"] = adaptive_setup_ms
    route["timing_scope"] = (
        "In-process adaptive search after one read-only snapshot load and independent full "
        "rederivation; each query includes a protected full-query ranking and bounded aspect rankings."
    )
    routes.append(route)

    for route in routes:
        _attach_cohorts(route, original_ids, hard_ids)

    parity = _parity_report(
        bundles["legacy"],
        bundles["embedding"],
        bundles["classical"],
        bundles["entity_graph"],
        bundles["adaptive"],
    )
    if parity["status"] != "pass" and not args.allow_core_drift:
        raise ComparisonError("Authoritative core parity failed across the five bundles.")
    return {
        "schema_version": SCHEMA_VERSION,
        "extends_evidence_schema": BASE_SCHEMA_VERSION,
        "comparison": "semantic-okf-legacy-embedding-classical-entity-graph-adaptive-retrieval",
        "query_count": len(questions),
        "question_sets": {
            "original_30": {"count": 30, "question_ids": [q.identifier for q in questions[:30]]},
            "hard_10": {"count": 10, "question_ids": [q.identifier for q in questions[30:]]},
        },
        "top_k": args.top_k,
        "metric_contract": {
            "primary_identity": "paper_id",
            "duplicate_policy": "keep first rank per identity",
            "recall_cutoffs": list(BASE.METRIC_CUTOFFS),
            "mrr_cutoff": 10,
            "ndcg_cutoff": 10,
            "relevance": "binary reviewed qrels",
            "cohorts": "overall 40, unchanged original 30, and evidence-first hard 10",
        },
        "evidence_contract": (
            "Schema 1.2 evidence validation is preserved for every retained hit. Exact text remains "
            "in memory through validation against a route-local authoritative ledger; reports omit raw "
            "text and retain identities, exact record or character-range locators, text hashes, byte and "
            "character counts, and per-hit validation issues."
        ),
        "route_contracts": {
            "legacy_lexical": (
                "The evaluator's in-process deterministic TF-IDF-like token-overlap index; this is not rg or grep."
            ),
            "embedding": {
                "routes": ["new_lexical", "vector", "hybrid"],
                "command": "PYTHON SCRIPT BUNDLE search --query QUERY --mode MODE --top-k K",
            },
            "classical": {
                "routes": [
                    "classical_bm25",
                    "classical_topic",
                    "classical_association",
                    "classical_fusion",
                ],
                "validation": "one independent full rederivation before any timed search",
            },
            "entity_graph": {
                "routes": [
                    "entity_graph_lexical",
                    "entity_graph_entity",
                    "entity_graph_traversal",
                    "entity_graph_fusion",
                ],
                "validation": "one independent full entity, mention, relation, and section rederivation before any timed search",
                "authority": "reviewed claim edges mirror authoritative facts; mentions, candidates, co-mentions, and scores are discovery-only",
            },
            "adaptive": {
                "routes": ["adaptive_fusion"],
                "validation": "one independent full lexical, association, topic, and passage rederivation before any timed search",
                "policy": "protected full-query fusion plus deterministic bounded aspect fusion at evidence-identity level",
                "evidence_adapter": "results retain exact authoritative fields; answer-facing evidence_rows are evaluated separately",
            },
        },
        "timing_methodology": {
            "warning": (
                "Latency scopes differ by route family and are operational diagnostics, not a causal "
                "algorithm-speed ranking."
            ),
            "legacy": "one reused in-process evaluator index",
            "embedding": "one reused in-process validated snapshot and pinned local model",
            "classical": "one reused in-process validated snapshot; deep setup is separate",
            "entity_graph": "one reused in-process validated graph snapshot; deep setup is separate",
            "adaptive": "one reused in-process validated adaptive snapshot; deep setup is separate",
        },
        "inputs": {
            "path_contract": (
                "Paths are invocation-relative when possible; external paths are reduced to "
                "external/<basename> and bound by byte count and SHA-256."
            ),
            "inventory": _file_fingerprint(args.inventory.resolve()),
            "questions": _file_fingerprint(args.questions.resolve()),
            "embedding_consult_script": _file_fingerprint(embedding_script),
            "classical_consult_script": _file_fingerprint(
                args.classical_consult_script.resolve()
            ),
            "entity_graph_consult_script": _file_fingerprint(
                args.entity_graph_consult_script.resolve()
            ),
            "adaptive_consult_script": _file_fingerprint(
                args.adaptive_consult_script.resolve()
            ),
            "adaptive_runtime_module": _file_fingerprint(
                args.adaptive_consult_script.resolve().parent / "_adaptive_snapshot.py"
            ),
            "base_comparator_script": _file_fingerprint(BASE_COMPARATOR_PATH),
            "comparator_script": _file_fingerprint(SCRIPT_PATH),
            "raw_input_verification": raw_verification,
        },
        "bundles": {
            name: _bundle_report(bundle, inventory) for name, bundle in bundles.items()
        },
        "core_semantic_parity": parity,
        "routes": routes,
    }


def _metric(value: Any) -> str:
    return "n/a" if value is None else f"{float(value):.4f}"


def _route_table(routes: Sequence[dict[str, Any]], cohort: str | None = None) -> list[str]:
    lines = [
        "| Route | Recall@1 | Recall@3 | Recall@5 | Recall@10 | MRR@10 | nDCG@10 | Source Recall@10 | Evidence valid | Errors |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for route in routes:
        metrics = route if cohort is None else route["cohorts"][cohort]
        paper = metrics["paper_metrics"]
        source = metrics["source_metrics"]
        evidence = metrics["evidence_validity"]
        lines.append(
            f"| {route['name']} | {_metric(paper['recall_at_1'])} | "
            f"{_metric(paper['recall_at_3'])} | {_metric(paper['recall_at_5'])} | "
            f"{_metric(paper['recall_at_10'])} | {_metric(paper['mrr_at_10'])} | "
            f"{_metric(paper['ndcg_at_10'])} | {_metric(source['recall_at_10'])} | "
            f"{_metric(evidence['ratio'])} | {metrics['error_count']} |"
        )
    return lines


def render_markdown(report: dict[str, Any]) -> str:
    """Render overall and cohort-separated metrics without raw evidence text."""

    lines = [
        "# Semantic OKF Adaptive Retrieval Comparison",
        "",
        f"Schema: {report['schema_version']} extending evidence-valid schema "
        f"{report['extends_evidence_schema']}. Questions: {report['query_count']}; top-k: {report['top_k']}.",
        "",
        "## All 40 questions",
        "",
        *_route_table(report["routes"]),
        "",
        "## Original 30 questions",
        "",
        *_route_table(report["routes"], "original_30"),
        "",
        "## Evidence-first hard 10",
        "",
        *_route_table(report["routes"], "hard_10"),
        "",
        "## Corpus and parity",
        "",
        "| Bundle | Core input coverage | Auxiliary declared | Files | Bytes | Logical tree SHA-256 |",
        "| --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for name in ("legacy", "embedding", "classical", "entity_graph", "adaptive"):
        bundle = report["bundles"][name]
        coverage = bundle["input_coverage"]
        fingerprint = bundle["fingerprint"]
        lines.append(
            f"| {name} | {coverage['covered']}/{coverage['expected']} | "
            f"{'yes' if coverage['required_auxiliary_declared'] else 'no'} | "
            f"{fingerprint['file_count']} | {fingerprint['total_bytes']} | "
            f"`{fingerprint['logical_tree_sha256']}` |"
        )
    lines.extend(
        [
            "",
            f"Authoritative core parity: **{report['core_semantic_parity']['status']}**.",
            "",
            "## Timing interpretation",
            "",
            f"{report['timing_methodology']['warning']} Legacy uses "
            f"{report['timing_methodology']['legacy']}; embedding uses "
            f"{report['timing_methodology']['embedding']}; classical uses "
            f"{report['timing_methodology']['classical']}; entity graph uses "
            f"{report['timing_methodology']['entity_graph']}; adaptive uses "
            f"{report['timing_methodology']['adaptive']}.",
        ]
    )
    route_errors = [
        (route["name"], error)
        for route in report["routes"]
        for error in route["errors"]
    ]
    if route_errors:
        lines.extend(["", "## Route errors", ""])
        lines.extend(
            f"- `{name}` / `{error['question_id']}`: {error['error']}"
            for name, error in route_errors
        )
    lines.append("")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inventory", type=Path, required=True)
    parser.add_argument("--questions", type=Path, required=True)
    parser.add_argument("--legacy-bundle", type=Path, required=True)
    parser.add_argument("--embedding-bundle", type=Path, required=True)
    parser.add_argument("--classical-bundle", type=Path, required=True)
    parser.add_argument("--entity-graph-bundle", type=Path, required=True)
    parser.add_argument("--adaptive-bundle", type=Path, required=True)
    parser.add_argument("--embedding-consult-script", type=Path, required=True)
    parser.add_argument("--classical-consult-script", type=Path, required=True)
    parser.add_argument("--entity-graph-consult-script", type=Path, required=True)
    parser.add_argument("--adaptive-consult-script", type=Path, required=True)
    parser.add_argument("--python-executable", default=sys.executable)
    parser.add_argument("--input-root", type=Path)
    parser.add_argument("--top-k", type=int, default=10)
    parser.add_argument("--timeout-seconds", type=float, default=120.0)
    parser.add_argument("--continue-on-error", action="store_true")
    parser.add_argument("--allow-input-drift", action="store_true")
    parser.add_argument("--allow-core-drift", action="store_true")
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-markdown", type=Path, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        report = run_comparison(args)
    except ComparisonError as exc:
        print(f"comparison error: {exc}", file=sys.stderr)
        return 2
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_markdown.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.output_markdown.write_text(render_markdown(report), encoding="utf-8")
    print(
        BASE.canonical_json(
            {
                "query_count": report["query_count"],
                "routes": [route["name"] for route in report["routes"]],
                "schema_version": report["schema_version"],
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
