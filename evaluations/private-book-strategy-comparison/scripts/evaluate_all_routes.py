#!/usr/bin/env python3
"""Evaluate every compatible registered retrieval route on a private book benchmark."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import statistics
import sys
import time
from collections import Counter
from dataclasses import asdict, is_dataclass
from pathlib import Path
from types import ModuleType
from typing import Any, Callable, Iterable, Mapping, Sequence


REPO = Path(__file__).resolve().parents[3]
ROUTE_LABELS = {
    "legacy-lexical": ("Legacy", "Lexical"),
    "embeddings-lexical": ("Embeddings", "Lexical"),
    "embeddings-vector": ("Embeddings", "Vector"),
    "embeddings-hybrid": ("Embeddings", "Hybrid"),
    "classical-bm25": ("Classical", "BM25"),
    "classical-topic": ("Classical", "Topic"),
    "classical-association": ("Classical", "Association"),
    "classical-fusion": ("Classical", "Fusion"),
    "adaptive-fusion": ("Adaptive", "Adaptive fusion"),
    "entity-graph-lexical": ("Entity Graph", "Lexical"),
    "entity-graph-entity": ("Entity Graph", "Entity"),
    "entity-graph-traversal": ("Entity Graph", "Traversal"),
    "entity-graph-fusion": ("Entity Graph", "Fusion"),
    "ensemble-fast": ("Ensemble", "Fast"),
    "ensemble-quality": ("Ensemble", "Quality"),
    "ensemble-robust": ("Ensemble", "Robust"),
    "graphify-search": ("Graphify", "Graph search"),
    "turso-lexical-sql": ("Turso", "Lexical SQL comparator"),
}
TOKEN_RE = __import__("re").compile(r"[A-Za-z0-9]+")


class EvaluationError(RuntimeError):
    """Describe an invalid benchmark, snapshot, route, or result."""


def load_module(name: str, path: Path) -> ModuleType:
    """Load one pinned Python module by path."""

    specification = importlib.util.spec_from_file_location(name, path)
    if specification is None or specification.loader is None:
        raise EvaluationError(f"cannot load module: {path}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


def sha256_file(path: Path) -> str:
    """Return a streaming SHA-256 digest."""

    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def fingerprint(path: Path) -> dict[str, Any]:
    """Describe one immutable input."""

    return {
        "path": str(path.resolve()),
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    """Load a nonblank JSON object sequence."""

    rows: list[dict[str, Any]] = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        row = json.loads(line)
        if not isinstance(row, dict):
            raise EvaluationError(f"{path}:{number}: row must be an object")
        rows.append(row)
    return rows


def load_questions(path: Path) -> list[dict[str, Any]]:
    """Load and validate the frozen 30-development/10-hard benchmark."""

    rows = load_jsonl(path)
    if len(rows) != 40:
        raise EvaluationError(f"expected 40 questions, found {len(rows)}")
    result: list[dict[str, Any]] = []
    for index, row in enumerate(rows, 1):
        identifier = row.get("id")
        question = row.get("question")
        question_type = row.get("question_type")
        qrels = row.get("qrels")
        if (
            not isinstance(identifier, str)
            or not identifier.startswith(f"q{index:03d}-")
            or not isinstance(question, str)
            or not question.strip()
            or question_type
            not in {
                "development",
                "hard",
                "cross-document",
            }
            or not isinstance(qrels, dict)
        ):
            raise EvaluationError(f"question {index} has an invalid contract")
        identities = qrels.get("record_ids")
        if identities is None:
            identities = qrels.get("source_ids")
        if identities is None:
            identities = qrels.get("document_ids")
        if (
            not isinstance(identities, list)
            or not identities
            or identities != sorted(set(identities))
            or not all(isinstance(value, str) and value for value in identities)
        ):
            raise EvaluationError(f"{identifier}: qrels are invalid")
        expected_hard = index >= 31
        is_hard = question_type == "hard"
        if is_hard != expected_hard:
            raise EvaluationError(f"{identifier}: cohort ordering is invalid")
        result.append(
            {
                "id": identifier,
                "question": question.strip(),
                "cohort": "hard" if is_hard else "development",
                "relevant": identities,
            }
        )
    return result


def ledger(bundle: Path) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    """Load one authoritative record ledger keyed by record ID."""

    rows = load_jsonl(bundle / "semantic" / "records.jsonl")
    by_id: dict[str, dict[str, Any]] = {}
    for row in rows:
        record_id = row.get("record_id")
        if not isinstance(record_id, str) or not record_id or record_id in by_id:
            raise EvaluationError(f"{bundle}: invalid or duplicate record ID")
        by_id[record_id] = row
    return rows, by_id


def validate_core_parity(
    bundles: Mapping[str, Path],
) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    """Require identical authoritative identities and record hashes."""

    reference: dict[str, dict[str, Any]] | None = None
    details: dict[str, Any] = {}
    for family, bundle in bundles.items():
        _, current = ledger(bundle)
        identity = {
            record_id: {
                "source_id": row.get("source_id"),
                "record_sha256": row.get("record_sha256"),
                "concept_id": row.get("concept_id"),
                "concept_path": row.get("concept_path"),
            }
            for record_id, row in current.items()
        }
        logical = hashlib.sha256(
            json.dumps(
                identity,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()
        details[family] = {
            "records": len(current),
            "logical_sha256": logical,
            "ledger": fingerprint(bundle / "semantic" / "records.jsonl"),
        }
        if reference is None:
            reference = current
            expected = identity
        elif identity != expected:
            raise EvaluationError(
                f"authoritative record parity failed for family {family}"
            )
    if reference is None:
        raise EvaluationError("no family bundles were supplied")
    return reference, details


def resolve_qrels(
    questions: Sequence[Mapping[str, Any]],
    authoritative: Mapping[str, Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Resolve record IDs or unambiguous source IDs to authoritative record IDs."""

    by_source: dict[str, list[str]] = {}
    for record_id, row in authoritative.items():
        source_id = row.get("source_id")
        if isinstance(source_id, str) and source_id:
            by_source.setdefault(source_id, []).append(record_id)

    resolved: list[dict[str, Any]] = []
    for question in questions:
        identities: list[str] = []
        for identity in question["relevant"]:
            if identity in authoritative:
                identities.append(identity)
                continue
            matches = by_source.get(identity, [])
            if len(matches) != 1:
                raise EvaluationError(
                    f"{question['id']} references an unknown or ambiguous "
                    f"identity: {identity!r}"
                )
            identities.append(matches[0])
        row = dict(question)
        row["relevant"] = sorted(set(identities))
        resolved.append(row)
    return resolved


def as_mapping(value: Any) -> dict[str, Any]:
    """Convert one result object into a plain mapping."""

    if isinstance(value, dict):
        return dict(value)
    if is_dataclass(value):
        return asdict(value)
    if hasattr(value, "__dict__"):
        return dict(vars(value))
    raise EvaluationError(f"unsupported result type: {type(value).__name__}")


def normalize_hits(
    values: Iterable[Any],
    authoritative: Mapping[str, Mapping[str, Any]],
    top_k: int,
) -> list[dict[str, Any]]:
    """Normalize, validate, and record-deduplicate route hits."""

    result: list[dict[str, Any]] = []
    seen: set[str] = set()
    for value in values:
        row = as_mapping(value)
        record_id = row.get("record_id") or row.get("document_id")
        if not isinstance(record_id, str) or record_id not in authoritative:
            raise EvaluationError(f"route returned an unknown record: {record_id!r}")
        if record_id in seen:
            continue
        expected = authoritative[record_id]
        record_sha256 = row.get("record_sha256")
        if (
            isinstance(record_sha256, str)
            and record_sha256 != expected.get("record_sha256")
        ):
            raise EvaluationError(f"record hash drift for {record_id}")
        seen.add(record_id)
        result.append(
            {
                "rank": len(result) + 1,
                "record_id": record_id,
                "source_id": expected.get("source_id"),
                "record_sha256": expected.get("record_sha256"),
                "concept_id": expected.get("concept_id"),
                "concept_path": expected.get("concept_path"),
            }
        )
        if len(result) == top_k:
            break
    return result


def metrics(hits: Sequence[Mapping[str, Any]], relevant: Sequence[str]) -> dict[str, float]:
    """Compute duplicate-safe Top-10 document metrics."""

    required = set(relevant)
    ranks = {
        str(row["record_id"]): int(row["rank"])
        for row in hits
        if row["record_id"] in required
    }
    relevant_ranks = sorted(ranks.values())
    recall = len(relevant_ranks) / len(required)
    mrr = 1.0 / relevant_ranks[0] if relevant_ranks else 0.0
    dcg = sum(1.0 / math.log2(rank + 1) for rank in relevant_ranks)
    ideal = sum(
        1.0 / math.log2(rank + 1)
        for rank in range(1, min(len(required), 10) + 1)
    )
    return {
        "recall_at_10": recall,
        "mrr_at_10": mrr,
        "ndcg_at_10": dcg / ideal if ideal else 0.0,
        "full_qrel_coverage_at_10": float(set(ranks) == required),
    }


def percentile_95(values: Sequence[float]) -> float:
    """Return nearest-rank P95."""

    ordered = sorted(values)
    return ordered[max(0, math.ceil(0.95 * len(ordered)) - 1)]


def payload_results(payload: Mapping[str, Any]) -> list[Any]:
    """Extract the result list from one registered runtime payload."""

    for name in ("results", "records", "hits"):
        value = payload.get(name)
        if isinstance(value, list):
            return value
    raise EvaluationError("route payload does not contain results")


def load_runtimes(bundles: Mapping[str, Path]) -> dict[str, Any]:
    """Load every registered family runtime and its validated snapshot."""

    base = load_module(
        "private_books_legacy_comparator",
        REPO / "evaluations/semantic-okf-embeddings/scripts/compare_retrieval.py",
    )
    legacy_ledger = base.AuthoritativeLedger.from_bundle(bundles["legacy"])
    legacy_index = base.LegacyLexicalIndex.from_ledger(legacy_ledger)

    embedding = load_module(
        "private_books_embedding_runtime",
        REPO
        / "skills/consult-semantic-okf-embeddings/scripts/_embedding_snapshot.py",
    )
    classical = load_module(
        "private_books_classical_runtime",
        REPO
        / "skills/consult-semantic-okf-classical/scripts/_classical_snapshot.py",
    )
    adaptive = load_module(
        "private_books_adaptive_runtime",
        REPO / "skills/consult-semantic-okf-adaptive/scripts/_adaptive_snapshot.py",
    )

    entity_dir = REPO / "skills/consult-semantic-okf-entity-graph/scripts"
    load_module("_entity_graph_model", entity_dir / "_entity_graph_model.py")
    entity = load_module(
        "private_books_entity_runtime",
        entity_dir / "_entity_graph_snapshot.py",
    )

    ensemble_dir = REPO / "skills/consult-semantic-okf-ensemble/scripts"
    load_module(
        "_entity_graph_model",
        ensemble_dir / "_entity_graph_model.py",
    )
    for module_name in (
        "_adaptive_snapshot",
        "_embedding_snapshot",
        "_entity_graph_snapshot",
    ):
        load_module(module_name, ensemble_dir / f"{module_name}.py")
    ensemble = load_module(
        "private_books_ensemble_runtime",
        ensemble_dir / "_ensemble_snapshot.py",
    )
    graphify = load_module(
        "private_books_graphify_runtime",
        REPO / "skills/consult-semantic-okf-graphify/scripts/_graphify_snapshot.py",
    )
    turso = load_module(
        "private_books_turso_runtime",
        REPO / "skills/consult-semantic-okf-turso/scripts/_turso_read.py",
    )
    turso_connection = turso.connect_read_only(
        bundles["turso"] / "semantic" / "knowledge.db"
    )
    turso.require_valid_database(turso_connection, full=True)

    return {
        "legacy": (legacy_index, base),
        "embeddings": (
            embedding.load_snapshot(bundles["embeddings"]),
            embedding,
        ),
        "classical": (
            classical.load_snapshot(bundles["classical"], deep_validation=True),
            classical,
        ),
        "adaptive": (
            adaptive.load_snapshot(bundles["adaptive"], deep_validation=True),
            adaptive,
        ),
        "entity-graph": (
            entity.load_snapshot(bundles["entity-graph"], deep_validation=True),
            entity,
        ),
        "ensemble": (
            ensemble.load_snapshot(bundles["ensemble"], deep_validation=True),
            ensemble,
        ),
        "graphify": (graphify.Snapshot(bundles["graphify"]), graphify),
        "turso": (turso_connection, turso),
    }


def turso_search(connection: Any, query: str, top_k: int) -> list[dict[str, Any]]:
    """Run a deterministic parameterized token-overlap comparator inside Turso."""

    tokens = sorted(
        {
            token.lower()
            for token in TOKEN_RE.findall(query)
            if len(token) >= 2
        }
    )
    if not tokens:
        return []
    score = " + ".join(
        "(CASE WHEN instr(lower(r.title || char(10) || r.body), ?) > 0 THEN 1 ELSE 0 END)"
        for _ in tokens
    )
    sql = (
        "SELECT r.record_json, "
        + score
        + " AS score FROM records AS r "
        "WHERE ("
        + score
        + ") > 0 ORDER BY score DESC, r.record_id ASC LIMIT ?"
    )
    parameters = [*tokens, *tokens, top_k]
    rows = connection.execute(sql, parameters).fetchall()
    return [json.loads(row[0]) for row in rows]


def route_functions(runtimes: Mapping[str, Any], top_k: int) -> dict[str, Callable[[str], list[Any]]]:
    """Bind every route to its validated family snapshot."""

    legacy, _ = runtimes["legacy"]
    embedding_snapshot, embedding = runtimes["embeddings"]
    classical_snapshot, classical = runtimes["classical"]
    adaptive_snapshot, adaptive = runtimes["adaptive"]
    entity_snapshot, entity = runtimes["entity-graph"]
    ensemble_snapshot, ensemble = runtimes["ensemble"]
    graphify_snapshot, _ = runtimes["graphify"]
    turso_connection, _ = runtimes["turso"]

    routes: dict[str, Callable[[str], list[Any]]] = {
        "legacy-lexical": lambda query: legacy.search(query, top_k),
        "adaptive-fusion": lambda query: payload_results(
            adaptive.search_snapshot(adaptive_snapshot, query, "adaptive", top_k)
        ),
        "graphify-search": lambda query: payload_results(
            graphify_snapshot.search(query, depth=2, top_k=top_k)
        ),
        "turso-lexical-sql": lambda query: turso_search(
            turso_connection, query, top_k
        ),
    }
    for mode in ("lexical", "vector", "hybrid"):
        routes[f"embeddings-{mode}"] = (
            lambda query, selected=mode: payload_results(
                embedding.search_snapshot(
                    embedding_snapshot,
                    query,
                    requested_mode=selected,
                    top_k=top_k,
                )
            )
        )
    for mode in ("bm25", "topic", "association", "fusion"):
        routes[f"classical-{mode}"] = (
            lambda query, selected=mode: payload_results(
                classical.search_snapshot(
                    classical_snapshot,
                    query,
                    selected,
                    top_k,
                )
            )
        )
    for mode in ("lexical", "entity", "traversal", "fusion"):
        routes[f"entity-graph-{mode}"] = (
            lambda query, selected=mode: payload_results(
                entity.search_snapshot(
                    entity_snapshot,
                    query,
                    selected,
                    top_k,
                )
            )
        )
    for policy in ("fast", "quality", "robust"):
        routes[f"ensemble-{policy}"] = (
            lambda query, selected=policy: payload_results(
                ensemble.search_snapshot(
                    ensemble_snapshot,
                    query,
                    selected,
                    top_k,
                )
            )
        )
    if set(routes) != set(ROUTE_LABELS):
        raise EvaluationError("route inventory drifted")
    return routes


def evaluate_route(
    route_id: str,
    search: Callable[[str], list[Any]],
    questions: Sequence[Mapping[str, Any]],
    authoritative: Mapping[str, Mapping[str, Any]],
    replicates: int,
    top_k: int,
) -> dict[str, Any]:
    """Evaluate one route with independent repeated query calls."""

    repetitions: list[dict[str, Any]] = []
    for replicate in range(1, replicates + 1):
        latencies: list[float] = []
        rows: list[dict[str, Any]] = []
        metric_values: dict[str, list[float]] = {
            name: []
            for name in (
                "recall_at_10",
                "mrr_at_10",
                "ndcg_at_10",
                "full_qrel_coverage_at_10",
            )
        }
        for question in questions:
            started = time.perf_counter()
            hits = normalize_hits(
                search(str(question["question"])),
                authoritative,
                top_k,
            )
            latency_ms = (time.perf_counter() - started) * 1000.0
            latencies.append(latency_ms)
            measured = metrics(hits, question["relevant"])
            for name, value in measured.items():
                metric_values[name].append(value)
            rows.append(
                {
                    "question_id": question["id"],
                    "cohort": question["cohort"],
                    "latency_ms": round(latency_ms, 3),
                    "metrics": {
                        name: round(value, 8)
                        for name, value in measured.items()
                    },
                    "hits": hits,
                }
            )
        repetitions.append(
            {
                "replicate": replicate,
                "metrics": {
                    name: statistics.fmean(values)
                    for name, values in metric_values.items()
                },
                "p95_ms": percentile_95(latencies),
                "queries": rows,
            }
        )

    ranking_by_question = [
        {
            row["question_id"]: tuple(hit["record_id"] for hit in row["hits"])
            for row in repetition["queries"]
        }
        for repetition in repetitions
    ]
    stable = sum(
        len({ranking[question["id"]] for ranking in ranking_by_question}) == 1
        for question in questions
    )
    family, label = ROUTE_LABELS[route_id]
    return {
        "strategy_id": route_id,
        "family": family,
        "label": label,
        "metrics": {
            name: statistics.median(
                repetition["metrics"][name] for repetition in repetitions
            )
            for name in repetitions[0]["metrics"]
        },
        "query_stability_ratio": stable / len(questions),
        "evidence_validity": 1.0,
        "representative_p95_ms": statistics.median(
            repetition["p95_ms"] for repetition in repetitions
        ),
        "replicates": repetitions,
    }


def render_markdown(report: Mapping[str, Any]) -> str:
    """Render the privacy-safe aggregate comparison table."""

    lines = [
        f"# {report['title']}",
        "",
        (
            f"Direct deterministic retrieval over {report['question_count']} frozen "
            f"questions, Top-{report['top_k']}, with {report['replicates']} repetitions "
            "per route. This evaluates retrieval, not generated-answer quality."
        ),
        "",
        "| Pos. | Family | Route | Recall@10 | MRR@10 | nDCG@10 | Full coverage | Stable queries | P95 |",
        "|---:|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in report["ranking"]:
        metrics_row = row["metrics"]
        lines.append(
            f"| {row['position']} | {row['family']} | {row['label']} | "
            f"{100 * metrics_row['recall_at_10']:.2f}% | "
            f"{100 * metrics_row['mrr_at_10']:.2f}% | "
            f"{100 * metrics_row['ndcg_at_10']:.2f}% | "
            f"{100 * metrics_row['full_qrel_coverage_at_10']:.2f}% | "
            f"{100 * row['query_stability_ratio']:.2f}% | "
            f"{row['representative_p95_ms']:.2f} ms |"
        )
    lines.extend(
        [
            "",
            (
                "All returned identities and hashes passed exact authoritative-ledger "
                "validation. Qrels are reviewed, non-exhaustive focus sets."
            ),
            "",
            (
                "The Turso row is a declared generic SQL token-overlap comparator over "
                "the validated Turso store; Turso does not otherwise expose a canonical "
                "natural-language ranking route."
            ),
            "",
        ]
    )
    return "\n".join(lines)


def evaluate(args: argparse.Namespace) -> dict[str, Any]:
    """Load, validate, execute, aggregate, and rank the complete route population."""

    questions = load_questions(args.questions.resolve())
    bundle_root = args.bundle_root.resolve()
    bundles = {
        family: bundle_root / "bundles" / family
        for family in (
            "embeddings",
            "classical",
            "adaptive",
            "entity-graph",
            "ensemble",
            "graphify",
            "turso",
        )
    }
    bundles["legacy"] = args.legacy_bundle.resolve()
    for family, path in bundles.items():
        if not path.is_dir():
            raise EvaluationError(f"{family} bundle is missing: {path}")
    authoritative, parity = validate_core_parity(bundles)
    questions = resolve_qrels(questions, authoritative)
    runtimes = load_runtimes(bundles)
    routes = route_functions(runtimes, args.top_k)
    route_rows: list[dict[str, Any]] = []
    for route_id in sorted(routes):
        try:
            route_rows.append(
                evaluate_route(
                    route_id,
                    routes[route_id],
                    questions,
                    authoritative,
                    args.replicates,
                    args.top_k,
                )
            )
        except EvaluationError as exc:
            raise EvaluationError(f"{route_id}: {exc}") from exc
    ranking = sorted(
        route_rows,
        key=lambda row: (
            -row["metrics"]["ndcg_at_10"],
            -row["metrics"]["mrr_at_10"],
            -row["metrics"]["recall_at_10"],
            row["representative_p95_ms"],
            row["strategy_id"],
        ),
    )
    for position, row in enumerate(ranking, 1):
        row["position"] = position
    return {
        "schema_version": "private-book-all-route-comparison/1.0",
        "status": "pass",
        "dataset_id": args.dataset_id,
        "title": args.title,
        "question_count": len(questions),
        "top_k": args.top_k,
        "replicates": args.replicates,
        "strategy_count": len(ranking),
        "answer_quality_evaluated": False,
        "qrel_policy": "reviewed-non-exhaustive-focus-sets",
        "inputs": {
            "questions": fingerprint(args.questions.resolve()),
            "core_parity": parity,
        },
        "ranking": ranking,
    }


def build_parser() -> argparse.ArgumentParser:
    """Create the command-line parser."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-id", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--questions", type=Path, required=True)
    parser.add_argument("--legacy-bundle", type=Path, required=True)
    parser.add_argument("--bundle-root", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-markdown", type=Path, required=True)
    parser.add_argument("--replicates", type=int, default=3)
    parser.add_argument("--top-k", type=int, default=10)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the exhaustive private-book route comparison."""

    args = build_parser().parse_args(argv)
    if args.replicates < 1 or args.top_k != 10:
        print(
            json.dumps(
                {
                    "status": "error",
                    "error": "--replicates must be positive and --top-k must be 10",
                },
                sort_keys=True,
            )
        )
        return 2
    try:
        report = evaluate(args)
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_markdown.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(
            json.dumps(
                report,
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
                allow_nan=False,
            )
            + "\n",
            encoding="utf-8",
            newline="\n",
        )
        args.output_markdown.write_text(
            render_markdown(report),
            encoding="utf-8",
            newline="\n",
        )
    except (
        EvaluationError,
        OSError,
        UnicodeError,
        json.JSONDecodeError,
        ValueError,
        TypeError,
        KeyError,
        ImportError,
    ) as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, sort_keys=True))
        return 2
    print(
        json.dumps(
            {
                "status": "pass",
                "dataset_id": report["dataset_id"],
                "strategy_count": report["strategy_count"],
                "winner": report["ranking"][0]["strategy_id"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
