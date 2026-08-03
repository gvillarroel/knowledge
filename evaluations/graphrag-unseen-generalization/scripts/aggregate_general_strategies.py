#!/usr/bin/env python3
"""Aggregate the frozen 25-strategy GraphRAG evaluation-only comparison."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
from pathlib import Path
from typing import Any, Iterable, Sequence


DATASET_ID = "graphrag-papers-parallel-eval-60-v1"
QUERY_SHA256 = "876cd033471d0bfcfe4440c76b6b70752c075b64bb586008dd3d41cf41992c33"
METRICS = ("recall_at_10", "mrr_at_10", "ndcg_at_10")
ADAPTIVE_ALIASES = {
    "legacy_lexical": "legacy-lexical",
    "new_lexical": "embeddings-lexical",
    "vector": "embeddings-vector",
    "hybrid": "embeddings-hybrid",
    "classical_bm25": "classical-bm25",
    "classical_topic": "classical-topic",
    "classical_association": "classical-association",
    "classical_fusion": "classical-fusion",
    "entity_graph_lexical": "entity-graph-lexical",
    "entity_graph_entity": "entity-graph-entity",
    "entity_graph_traversal": "entity-graph-traversal",
    "entity_graph_fusion": "entity-graph-fusion",
    "adaptive_fusion": "adaptive-fusion",
}
RUST_ALIASES = {
    "rust_mallet_bm25": "rust-mallet-bm25",
    "rust_mallet_topic": "rust-mallet-topic",
    "rust_mallet_association": "rust-mallet-association",
    "rust_mallet_fusion": "rust-mallet-fusion",
}
SPECIALIZED_ALIASES = {
    "v45-early-confidence": "specialized-expert-trace-early-confidence",
    "v48-ensemble-quality-trace": "specialized-expert-ensemble-quality-trace-v48",
    "v51-supervised-profiles": "specialized-expert-supervised-profiles-v51",
}


class AggregateError(RuntimeError):
    """Describe an incomplete, drifting, or invalid strategy comparison."""


def _load(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise AggregateError(f"cannot load {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise AggregateError(f"expected a JSON object: {path}")
    return value


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _finite(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise AggregateError(f"{label} must be numeric")
    result = float(value)
    if not math.isfinite(result):
        raise AggregateError(f"{label} must be finite")
    return result


def _report_ref(path: Path) -> dict[str, Any]:
    return {"path": str(path.resolve()), "sha256": _sha256(path)}


def _validate_report_contract(report: dict[str, Any], label: str) -> None:
    benchmark = report.get("benchmark")
    benchmark_id = (
        benchmark.get("benchmark_id") if isinstance(benchmark, dict) else None
    )
    if (
        report.get("dataset_id", benchmark_id) != DATASET_ID
        or report.get("query_count") != 60
        or report.get("top_k") != 10
    ):
        raise AggregateError(f"{label} does not match the frozen dataset contract")
    questions = report.get("inputs", {}).get("questions")
    question_sha256 = (
        questions.get("sha256")
        if isinstance(questions, dict)
        else benchmark.get("question_sha256")
        if isinstance(benchmark, dict)
        else None
    )
    if question_sha256 != QUERY_SHA256:
        raise AggregateError(f"{label} does not bind the frozen question set")


def _route(report: dict[str, Any], name: str) -> dict[str, Any]:
    routes = report.get("routes")
    if not isinstance(routes, list):
        raise AggregateError("report routes must be an array")
    matches = [row for row in routes if isinstance(row, dict) and row.get("name") == name]
    if len(matches) != 1:
        raise AggregateError(f"expected one route named {name}")
    return matches[0]


def _ranking_identity(route: dict[str, Any]) -> list[dict[str, Any]]:
    queries = route.get("queries")
    if not isinstance(queries, list) or len(queries) != 60:
        raise AggregateError(f"route {route.get('name')} must contain 60 query rows")
    result = []
    for query in queries:
        if not isinstance(query, dict) or not isinstance(query.get("question_id"), str):
            raise AggregateError("query row lacks an identity")
        hits = query.get("hits")
        if not isinstance(hits, list):
            raise AggregateError("query hits must be an array")
        paper_ids = [
            hit.get("paper_id")
            for hit in hits
            if isinstance(hit, dict) and isinstance(hit.get("paper_id"), str)
        ]
        result.append({"question_id": query["question_id"], "paper_ids": paper_ids})
    return result


def _ranking_sha256(route: dict[str, Any]) -> str:
    payload = json.dumps(
        _ranking_identity(route),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _validate_route(route: dict[str, Any], strategy_id: str) -> None:
    if route.get("query_count") != 60 or route.get("error_count") != 0:
        raise AggregateError(f"{strategy_id} has incomplete or errored queries")
    evidence = route.get("evidence_validity")
    if not isinstance(evidence, dict) or _finite(
        evidence.get("ratio"), f"{strategy_id}.evidence_validity"
    ) != 1.0:
        raise AggregateError(f"{strategy_id} has invalid evidence")
    metrics = route.get("paper_metrics")
    if not isinstance(metrics, dict):
        raise AggregateError(f"{strategy_id} lacks paper metrics")
    for name in METRICS:
        value = _finite(metrics.get(name), f"{strategy_id}.{name}")
        if not 0.0 <= value <= 1.0:
            raise AggregateError(f"{strategy_id}.{name} is outside 0..1")


def _row_from_three_reports(
    strategy_id: str,
    paths: Sequence[Path],
    route_name: str,
    *,
    route_container: str = "routes",
) -> dict[str, Any]:
    if len(paths) != 3:
        raise AggregateError(f"{strategy_id} requires exactly three reports")
    routes: list[dict[str, Any]] = []
    for path in paths:
        report = _load(path)
        if report.get("status") not in (None, "pass"):
            raise AggregateError(f"{strategy_id} report did not pass the 60-question contract")
        _validate_report_contract(report, strategy_id)
        if route_container == "route":
            route = report.get("route")
            if not isinstance(route, dict) or route.get("name") != route_name:
                raise AggregateError(f"{strategy_id} report route differs")
        else:
            route = _route(report, route_name)
        _validate_route(route, strategy_id)
        routes.append(route)
    hashes = [_ranking_sha256(route) for route in routes]
    stable = len(set(hashes)) == 1
    metrics = {
        name: statistics.median(
            _finite(route["paper_metrics"][name], f"{strategy_id}.{name}")
            for route in routes
        )
        for name in METRICS
    }
    p95_values = [
        _finite(route["timing_ms"]["p95"], f"{strategy_id}.p95") for route in routes
    ]
    return {
        "strategy_id": strategy_id,
        "query_count": 60,
        "top_k": 10,
        "metrics": metrics,
        "evidence_validity": 1.0,
        "deterministic": stable,
        "query_stability_ratio": 1.0 if stable else 0.0,
        "ranking_sha256s": hashes,
        "replicate_p95_ms": p95_values,
        "representative_p95_ms": statistics.median(p95_values),
        "reports": [_report_ref(path) for path in paths],
    }


def _adaptive_rows(paths: Sequence[Path]) -> list[dict[str, Any]]:
    return [
        _row_from_three_reports(strategy_id, paths, route_name)
        for route_name, strategy_id in ADAPTIVE_ALIASES.items()
    ]


def _rust_rows(paths: Sequence[Path]) -> list[dict[str, Any]]:
    return [
        _row_from_three_reports(strategy_id, paths, route_name)
        for route_name, strategy_id in RUST_ALIASES.items()
    ]


def _ensemble_rows(path: Path) -> list[dict[str, Any]]:
    report = _load(path)
    if report.get("status") != "pass":
        raise AggregateError("ensemble report did not pass the 60-question contract")
    _validate_report_contract(report, "ensemble")
    result = []
    for policy in ("fast", "robust"):
        strategy_id = f"ensemble-{policy}"
        route = _route(report, f"ensemble_{policy}")
        _validate_route(route, strategy_id)
        determinism = route.get("determinism")
        if (
            not isinstance(determinism, dict)
            or determinism.get("repetitions") != 3
            or determinism.get("all_rankings_equal") is not True
        ):
            raise AggregateError(f"{strategy_id} did not complete three stable repetitions")
        timings = determinism.get("per_repetition_timing_ms")
        if not isinstance(timings, list) or len(timings) != 3:
            raise AggregateError(f"{strategy_id} lacks repetition timings")
        p95_values = [
            _finite(row.get("p95"), f"{strategy_id}.p95")
            for row in timings
            if isinstance(row, dict)
        ]
        if len(p95_values) != 3:
            raise AggregateError(f"{strategy_id} repetition timings are incomplete")
        result.append(
            {
                "strategy_id": strategy_id,
                "query_count": 60,
                "top_k": 10,
                "metrics": {
                    name: _finite(route["paper_metrics"][name], f"{strategy_id}.{name}")
                    for name in METRICS
                },
                "evidence_validity": 1.0,
                "deterministic": True,
                "query_stability_ratio": 1.0,
                "ranking_sha256s": [determinism["rankings_sha256"]] * 3,
                "replicate_p95_ms": p95_values,
                "representative_p95_ms": statistics.median(p95_values),
                "reports": [_report_ref(path)],
            }
        )
    return result


def _specialized_rows(path: Path) -> list[dict[str, Any]]:
    report = _load(path)
    ranking = report.get("ranking")
    if report.get("status") != "pass" or not isinstance(ranking, list):
        raise AggregateError("specialized comparison did not pass")
    by_id = {
        row.get("candidate_id"): row
        for row in ranking
        if isinstance(row, dict) and isinstance(row.get("candidate_id"), str)
    }
    result = []
    for candidate_id, strategy_id in SPECIALIZED_ALIASES.items():
        row = by_id.get(candidate_id)
        if not isinstance(row, dict):
            raise AggregateError(f"specialized candidate is missing: {candidate_id}")
        if (
            row.get("query_count") != 60
            or row.get("top_k") != 10
            or row.get("query_sha256") != QUERY_SHA256
            or row.get("evidence_validity") != 1.0
            or not isinstance(row.get("deterministic"), bool)
        ):
            raise AggregateError(f"specialized candidate failed: {candidate_id}")
        metrics = row.get("metrics")
        p95_values = row.get("replicate_p95_ms")
        if not isinstance(metrics, dict) or not isinstance(p95_values, list) or len(p95_values) != 3:
            raise AggregateError(f"specialized candidate metrics are incomplete: {candidate_id}")
        result.append(
            {
                "strategy_id": strategy_id,
                "query_count": 60,
                "top_k": 10,
                "metrics": {
                    name: _finite(metrics.get(name), f"{strategy_id}.{name}")
                    for name in METRICS
                },
                "evidence_validity": 1.0,
                "deterministic": row["deterministic"],
                "query_stability_ratio": _finite(
                    row.get("query_stability_ratio"), f"{strategy_id}.stability"
                ),
                "ranking_sha256s": row.get("ranking_sha256s"),
                "replicate_p95_ms": [
                    _finite(value, f"{strategy_id}.p95") for value in p95_values
                ],
                "representative_p95_ms": _finite(
                    row.get("representative_p95_ms"), f"{strategy_id}.representative_p95"
                ),
                "reports": row.get("reports"),
            }
        )
    return result


def _labels(selection: dict[str, Any]) -> dict[str, str]:
    strategies = selection.get("strategies")
    if (
        selection.get("strategy_count") != 25
        or not isinstance(strategies, list)
        or len(strategies) != 25
    ):
        raise AggregateError("selection must freeze exactly 25 strategies")
    result = {}
    for row in strategies:
        if not isinstance(row, dict):
            raise AggregateError("selection strategy row must be an object")
        strategy_id = row.get("strategy_id")
        label = row.get("label")
        if not isinstance(strategy_id, str) or not isinstance(label, str):
            raise AggregateError("selection strategy identity is invalid")
        result[strategy_id] = label
    if len(result) != 25:
        raise AggregateError("selection strategy IDs must be unique")
    return result


def _sort(rows: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    result = sorted(
        rows,
        key=lambda row: (
            -row["metrics"]["ndcg_at_10"],
            -row["metrics"]["mrr_at_10"],
            -row["metrics"]["recall_at_10"],
            row["representative_p95_ms"],
            row["strategy_id"],
        ),
    )
    for position, row in enumerate(result, 1):
        row["position"] = position
    return result


def aggregate(args: argparse.Namespace) -> dict[str, Any]:
    selection = _load(args.selection)
    labels = _labels(selection)
    rows = [
        *_adaptive_rows(args.adaptive_report),
        *_ensemble_rows(args.ensemble_report),
        *_rust_rows(args.rust_report),
        _row_from_three_reports(
            "tantivy-bm25", args.tantivy_report, "tantivy_bm25", route_container="route"
        ),
        _row_from_three_reports(
            "tika-mallet-fusion", args.tika_report, "tika_mallet_fusion"
        ),
        _row_from_three_reports(
            "tika-mallet-tantivy-fusion",
            args.tika_tantivy_report,
            "tika_mallet_tantivy_fusion",
        ),
        *_specialized_rows(args.specialized_comparison),
    ]
    ids = [row["strategy_id"] for row in rows]
    if len(ids) != 25 or len(set(ids)) != 25 or set(ids) != set(labels):
        raise AggregateError("aggregated rows do not match the frozen 25-strategy selection")
    for row in rows:
        row["label"] = labels[row["strategy_id"]]
    ranking = _sort(rows)
    return {
        "schema_version": "graphrag-general-strategy-comparison/1.0",
        "status": "pass",
        "ranking_eligible": True,
        "dataset_id": DATASET_ID,
        "query_sha256": QUERY_SHA256,
        "query_count": 60,
        "strategy_count": 25,
        "top_k": 10,
        "selection": _report_ref(args.selection),
        "contract": {
            "primary_identity": "authoritative-paper",
            "relevance": "binary reviewed qrels",
            "replications": 3,
            "ranking": [
                "ndcg_at_10_desc",
                "mrr_at_10_desc",
                "recall_at_10_desc",
                "representative_p95_ms_asc",
                "strategy_id_asc",
            ],
        },
        "limitations": [
            "Direct retrieval does not score generated-answer correctness or completeness.",
            "Latency is an operational diagnostic because family setup and runtime boundaries differ.",
            "Non-deterministic strategies remain visible and use median metrics across three repetitions.",
            "Graphify and Turso remain outside the ranked table because no compatible paper-level Top-10 route exists.",
        ],
        "ranking": ranking,
    }


def _percent(value: Any) -> str:
    return f"{100.0 * float(value):.2f}%"


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# General GraphRAG strategy ranking on evaluation-only questions",
        "",
        "## General evaluation-only direct comparison",
        "",
        "| Pos. | Pair / strategy | Recall@10 | MRR@10 | nDCG@10 | Stable queries | P95 |",
        "|---:|---|---:|---:|---:|---:|---:|",
    ]
    for row in report["ranking"]:
        lines.append(
            f"| {row['position']} | {row['label']} | "
            f"{_percent(row['metrics']['recall_at_10'])} | "
            f"{_percent(row['metrics']['mrr_at_10'])} | "
            f"{_percent(row['metrics']['ndcg_at_10'])} | "
            f"{_percent(row['query_stability_ratio'])} | "
            f"{row['representative_p95_ms']:.2f} ms |"
        )
    lines.extend(
        [
            "",
            "Scope: 60 evaluation-only questions, Top-10, authoritative-paper identity, "
            "three repetitions per strategy. Ranking uses nDCG@10, then MRR@10, "
            "Recall@10, latency, and stable strategy ID.",
            "",
            "Graphify and Turso are omitted because neither exposes a compatible "
            "GraphRAG paper-level Top-10 route. This table measures retrieval and "
            "evidence validity, not generated-answer correctness.",
            "",
        ]
    )
    return "\n".join(lines)


def comparison_companion(report: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "final-report-comparison/1.0",
        "heading": "## General evaluation-only direct comparison",
        "report": "general-strategy-ranking.table.md",
        "dataset_scope": {
            "dataset_id": DATASET_ID,
            "cohort": "evaluation-only-60",
            "candidate_budget": "top-10",
            "identity_grouping": "authoritative-paper",
            "metric_contract": "graphrag-direct-retrieval/1.0",
        },
        "metrics": [
            {
                "id": "recall_at_10",
                "label": "Recall@10",
                "aggregation": "mean",
                "unit": "percent",
                "direction": "higher",
                "display_precision": 2,
            },
            {
                "id": "mrr_at_10",
                "label": "MRR@10",
                "aggregation": "mean",
                "unit": "percent",
                "direction": "higher",
                "display_precision": 2,
            },
            {
                "id": "ndcg_at_10",
                "label": "nDCG@10",
                "aggregation": "mean",
                "unit": "percent",
                "direction": "higher",
                "display_precision": 2,
            },
            {
                "id": "query_stability_ratio",
                "label": "Stable queries",
                "aggregation": "ratio",
                "unit": "percent",
                "direction": "higher",
                "display_precision": 2,
            },
            {
                "id": "representative_p95_ms",
                "label": "P95",
                "aggregation": "percentile_95",
                "unit": "ms",
                "direction": "lower",
                "display_precision": 2,
            },
        ],
        "alternatives": [
            {
                "id": row["strategy_id"],
                "label": row["label"],
                "metrics": {
                    **{
                        name: 100.0 * value
                        for name, value in row["metrics"].items()
                    },
                    "query_stability_ratio": 100.0 * row["query_stability_ratio"],
                    "representative_p95_ms": row["representative_p95_ms"],
                },
            }
            for row in report["ranking"]
        ],
    }


def _add_repeated(parser: argparse.ArgumentParser, flag: str) -> None:
    parser.add_argument(flag, type=Path, action="append", required=True)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selection", type=Path, required=True)
    _add_repeated(parser, "--adaptive-report")
    parser.add_argument("--ensemble-report", type=Path, required=True)
    _add_repeated(parser, "--rust-report")
    _add_repeated(parser, "--tantivy-report")
    _add_repeated(parser, "--tika-report")
    _add_repeated(parser, "--tika-tantivy-report")
    parser.add_argument("--specialized-comparison", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-markdown", type=Path, required=True)
    parser.add_argument("--output-companion", type=Path, required=True)
    args = parser.parse_args(argv)
    outputs = (args.output_json, args.output_markdown, args.output_companion)
    if any(path.exists() or path.is_symlink() for path in outputs):
        print(json.dumps({"status": "error", "error": "output already exists"}))
        return 2
    try:
        report = aggregate(args)
    except (AggregateError, OSError, UnicodeError, ValueError, TypeError) as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, sort_keys=True))
        return 2
    for path in outputs:
        path.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    args.output_markdown.write_text(
        render_markdown(report), encoding="utf-8", newline="\n"
    )
    args.output_companion.write_text(
        json.dumps(
            comparison_companion(report),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        json.dumps(
            {
                "status": "pass",
                "strategy_count": report["strategy_count"],
                "winner": report["ranking"][0]["strategy_id"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
