#!/usr/bin/env python3
"""Aggregate the 25-strategy cross-source contradiction retrieval comparison."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import statistics
from typing import Any, Iterable, Mapping, Sequence


DATASET_ID = "graphrag-papers-contradiction-eval-40-v1"
QUERY_SHA256 = "1cfcd02df8a62b0539b3399661af99dd207ad9a6a57151f5fdf009a7353c27c1"
QUESTION_COUNT = 40
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


class AggregateError(RuntimeError):
    """Describe an incomplete, drifting, or invalid contradiction comparison."""


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


def _ref(path: Path) -> dict[str, Any]:
    return {"path": str(path.resolve()), "sha256": _sha256(path)}


def _finite(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise AggregateError(f"{label} must be numeric")
    result = float(value)
    if not math.isfinite(result):
        raise AggregateError(f"{label} must be finite")
    return result


def _qrels(path: Path) -> dict[str, set[str]]:
    result = {}
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        row = json.loads(line)
        question_id = row.get("id")
        paper_ids = row.get("qrels", {}).get("paper_ids")
        if (
            not isinstance(question_id, str)
            or question_id in result
            or not isinstance(paper_ids, list)
            or not 2 <= len(paper_ids) <= 4
            or any(not isinstance(value, str) or not value for value in paper_ids)
        ):
            raise AggregateError(f"invalid qrel row {number}")
        result[question_id] = set(paper_ids)
    if len(result) != QUESTION_COUNT or _sha256(path) != QUERY_SHA256:
        raise AggregateError("question set does not match the sealed contradiction contract")
    return result


def _route(report: Mapping[str, Any], name: str) -> dict[str, Any]:
    routes = report.get("routes")
    if not isinstance(routes, list):
        route = report.get("route")
        if isinstance(route, dict) and route.get("name") == name:
            return route
        raise AggregateError("report routes must be an array")
    matches = [
        row
        for row in routes
        if isinstance(row, dict) and row.get("name") == name
    ]
    if len(matches) != 1:
        raise AggregateError(f"expected one route named {name}")
    return matches[0]


def _validate_report(report: Mapping[str, Any], label: str) -> None:
    benchmark = report.get("benchmark")
    benchmark_id = (
        benchmark.get("benchmark_id") if isinstance(benchmark, dict) else None
    )
    accepted_dataset_ids = {DATASET_ID}
    if label.startswith("specialized-expert-"):
        # The generic expert evaluator keeps the embedded source-corpus ID at
        # top level. The question-file digest below is the authoritative binding
        # for this evaluation-only extension.
        accepted_dataset_ids.add("graphrag-papers-40")
    if (
        report.get("status") not in (None, "pass")
        or report.get("dataset_id", benchmark_id) not in accepted_dataset_ids
        or report.get("query_count") != QUESTION_COUNT
        or report.get("top_k") != 10
    ):
        raise AggregateError(f"{label} does not match the contradiction contract")
    inputs = report.get("inputs")
    questions = inputs.get("questions") if isinstance(inputs, dict) else None
    digest = (
        questions.get("sha256")
        if isinstance(questions, dict)
        else benchmark.get("question_sha256")
        if isinstance(benchmark, dict)
        else None
    )
    if digest != QUERY_SHA256:
        raise AggregateError(f"{label} does not bind the sealed question bytes")


def _paper_ranking(query: Mapping[str, Any]) -> list[str]:
    hits = query.get("hits")
    if not isinstance(hits, list):
        raise AggregateError("query hits must be an array")
    result = []
    seen = set()
    for hit in hits:
        paper_id = hit.get("paper_id") if isinstance(hit, dict) else None
        if isinstance(paper_id, str) and paper_id not in seen:
            result.append(paper_id)
            seen.add(paper_id)
    return result[:10]


def _route_rankings(
    route: Mapping[str, Any],
    qrels: Mapping[str, set[str]],
) -> dict[str, list[str]]:
    if route.get("query_count") != QUESTION_COUNT or route.get("error_count") != 0:
        raise AggregateError(f"route {route.get('name')} is incomplete")
    evidence = route.get("evidence_validity")
    if (
        not isinstance(evidence, dict)
        or _finite(evidence.get("ratio"), "evidence validity") != 1.0
    ):
        raise AggregateError(f"route {route.get('name')} has invalid evidence")
    queries = route.get("queries")
    if not isinstance(queries, list) or len(queries) != QUESTION_COUNT:
        raise AggregateError(f"route {route.get('name')} query inventory is incomplete")
    result = {}
    for query in queries:
        question_id = query.get("question_id") if isinstance(query, dict) else None
        if not isinstance(question_id, str) or question_id not in qrels or question_id in result:
            raise AggregateError("route query identity differs from qrels")
        result[question_id] = _paper_ranking(query)
    if set(result) != set(qrels):
        raise AggregateError("route does not cover every contradiction question")
    return result


def _ranking_metrics(
    rankings: Mapping[str, Sequence[str]],
    qrels: Mapping[str, set[str]],
) -> dict[str, float]:
    recall = []
    reciprocal = []
    ndcg = []
    complete = []
    for question_id, relevant in qrels.items():
        ranking = list(rankings[question_id])[:10]
        matched = [paper_id in relevant for paper_id in ranking]
        recall.append(sum(matched) / len(relevant))
        first = next((rank for rank, value in enumerate(matched, 1) if value), None)
        reciprocal.append(1.0 / first if first is not None else 0.0)
        dcg = sum(
            1.0 / math.log2(rank + 1)
            for rank, value in enumerate(matched, 1)
            if value
        )
        ideal = sum(
            1.0 / math.log2(rank + 1)
            for rank in range(1, min(len(relevant), 10) + 1)
        )
        ndcg.append(dcg / ideal if ideal else 0.0)
        complete.append(float(relevant.issubset(ranking)))
    return {
        "recall_at_10": statistics.fmean(recall),
        "full_evidence_set_rate_at_10": statistics.fmean(complete),
        "mrr_at_10": statistics.fmean(reciprocal),
        "ndcg_at_10": statistics.fmean(ndcg),
    }


def _p95(route: Mapping[str, Any], label: str) -> float:
    timing = route.get("timing_ms")
    if not isinstance(timing, dict):
        raise AggregateError(f"{label} lacks timing")
    value = _finite(timing.get("p95"), f"{label}.p95")
    if value < 0:
        raise AggregateError(f"{label}.p95 must be non-negative")
    return value


def _row_from_reports(
    strategy_id: str,
    paths: Sequence[Path],
    route_name: str,
    qrels: Mapping[str, set[str]],
) -> dict[str, Any]:
    if len(paths) != 3:
        raise AggregateError(f"{strategy_id} requires exactly three reports")
    rankings = []
    metrics = []
    p95_values = []
    for path in paths:
        report = _load(path)
        _validate_report(report, strategy_id)
        route = _route(report, route_name)
        ranking = _route_rankings(route, qrels)
        rankings.append(ranking)
        metrics.append(_ranking_metrics(ranking, qrels))
        p95_values.append(_p95(route, strategy_id))
    stable = statistics.fmean(
        float(len({tuple(rep[question_id]) for rep in rankings}) == 1)
        for question_id in qrels
    )
    return {
        "strategy_id": strategy_id,
        "query_count": QUESTION_COUNT,
        "top_k": 10,
        "metrics": {
            metric: statistics.median(row[metric] for row in metrics)
            for metric in metrics[0]
        },
        "evidence_validity": 1.0,
        "query_stability_ratio": stable,
        "replicate_p95_ms": p95_values,
        "representative_p95_ms": statistics.median(p95_values),
        "reports": [_ref(path) for path in paths],
    }


def _ensemble_rows(
    path: Path,
    qrels: Mapping[str, set[str]],
) -> list[dict[str, Any]]:
    report = _load(path)
    _validate_report(report, "ensemble")
    result = []
    for policy in ("fast", "robust"):
        strategy_id = f"ensemble-{policy}"
        route = _route(report, f"ensemble_{policy}")
        ranking = _route_rankings(route, qrels)
        determinism = route.get("determinism")
        timings = (
            determinism.get("per_repetition_timing_ms")
            if isinstance(determinism, dict)
            else None
        )
        if (
            not isinstance(determinism, dict)
            or determinism.get("repetitions") != 3
            or not isinstance(timings, list)
            or len(timings) != 3
        ):
            raise AggregateError(f"{strategy_id} lacks three internal repetitions")
        p95_values = [
            _finite(row.get("p95"), f"{strategy_id}.p95")
            for row in timings
            if isinstance(row, dict)
        ]
        if len(p95_values) != 3:
            raise AggregateError(f"{strategy_id} timing repetitions are incomplete")
        result.append(
            {
                "strategy_id": strategy_id,
                "query_count": QUESTION_COUNT,
                "top_k": 10,
                "metrics": _ranking_metrics(ranking, qrels),
                "evidence_validity": 1.0,
                "query_stability_ratio": (
                    1.0 if determinism.get("all_rankings_equal") is True else 0.0
                ),
                "replicate_p95_ms": p95_values,
                "representative_p95_ms": statistics.median(p95_values),
                "reports": [_ref(path)],
            }
        )
    return result


def _labels(selection: Mapping[str, Any]) -> dict[str, str]:
    strategies = selection.get("strategies")
    if (
        selection.get("dataset_id") != DATASET_ID
        or selection.get("strategy_count") != 25
        or not isinstance(strategies, list)
        or len(strategies) != 25
    ):
        raise AggregateError("selection must freeze 25 contradiction strategies")
    result = {
        row["strategy_id"]: row["label"]
        for row in strategies
        if isinstance(row, dict)
        and isinstance(row.get("strategy_id"), str)
        and isinstance(row.get("label"), str)
    }
    if len(result) != 25:
        raise AggregateError("selection labels are incomplete")
    return result


def _sort(rows: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    ranked = sorted(
        rows,
        key=lambda row: (
            -row["metrics"]["full_evidence_set_rate_at_10"],
            -row["metrics"]["ndcg_at_10"],
            -row["metrics"]["mrr_at_10"],
            -row["metrics"]["recall_at_10"],
            row["representative_p95_ms"],
            row["strategy_id"],
        ),
    )
    for position, row in enumerate(ranked, 1):
        row["position"] = position
    return ranked


def aggregate(args: argparse.Namespace) -> dict[str, Any]:
    """Aggregate all frozen strategy families."""

    qrels = _qrels(args.questions)
    selection = _load(args.selection)
    labels = _labels(selection)
    rows = []
    for route_name, strategy_id in ADAPTIVE_ALIASES.items():
        rows.append(
            _row_from_reports(
                strategy_id,
                args.adaptive_report,
                route_name,
                qrels,
            )
        )
    rows.extend(_ensemble_rows(args.ensemble_report, qrels))
    for route_name, strategy_id in RUST_ALIASES.items():
        rows.append(
            _row_from_reports(strategy_id, args.rust_report, route_name, qrels)
        )
    rows.append(
        _row_from_reports(
            "tantivy-bm25",
            args.tantivy_report,
            "tantivy_bm25",
            qrels,
        )
    )
    rows.append(
        _row_from_reports(
            "tika-mallet-fusion",
            args.tika_report,
            "tika_mallet_fusion",
            qrels,
        )
    )
    rows.append(
        _row_from_reports(
            "tika-mallet-tantivy-fusion",
            args.tika_tantivy_report,
            "tika_mallet_tantivy_fusion",
            qrels,
        )
    )
    rows.append(
        _row_from_reports(
            "specialized-expert-trace-early-confidence",
            args.v45_report,
            "specialized_expert_trace_classical_early_confidence",
            qrels,
        )
    )
    rows.append(
        _row_from_reports(
            "specialized-expert-ensemble-quality-trace-v48",
            args.v48_report,
            "specialized_expert_ensemble_quality_trace",
            qrels,
        )
    )
    rows.append(
        _row_from_reports(
            "specialized-expert-supervised-profiles-v51",
            args.v51_report,
            "specialized_expert_supervised_lexical_profiles",
            qrels,
        )
    )
    identifiers = [row["strategy_id"] for row in rows]
    if len(identifiers) != 25 or set(identifiers) != set(labels):
        raise AggregateError("aggregated rows differ from the frozen population")
    for row in rows:
        row["label"] = labels[row["strategy_id"]]
    return {
        "schema_version": "graphrag-contradiction-strategy-comparison/1.0",
        "status": "pass",
        "ranking_eligible": True,
        "dataset_id": DATASET_ID,
        "query_sha256": QUERY_SHA256,
        "query_count": QUESTION_COUNT,
        "strategy_count": 25,
        "top_k": 10,
        "selection": _ref(args.selection),
        "contract": {
            "primary_identity": "authoritative-paper",
            "relevance": "binary claim-bound contradiction-side qrels",
            "replications": 3,
            "primary_metric": "full_evidence_set_rate_at_10",
            "ranking": [
                "full_evidence_set_rate_at_10_desc",
                "ndcg_at_10_desc",
                "mrr_at_10_desc",
                "recall_at_10_desc",
                "representative_p95_ms_asc",
                "strategy_id_asc",
            ],
        },
        "limitations": [
            "Direct retrieval measures whether every contradiction side is available, not whether a generated answer adjudicates the contradiction correctly.",
            "Questions and verdicts are source-derived and mechanically evidence-validated but have no independent human adjudication.",
            "Latency is an operational diagnostic because family setup and runtime boundaries differ.",
            "Graphify and Turso lack a compatible authoritative-paper Top-10 route.",
        ],
        "ranking": _sort(rows),
    }


def _percent(value: Any) -> str:
    return f"{100.0 * float(value):.2f}%"


def render_markdown(report: Mapping[str, Any]) -> str:
    """Render the required compact primary comparison table."""

    lines = [
        "# GraphRAG contradiction-search retrieval ranking",
        "",
        "## Cross-source contradiction retrieval comparison",
        "",
        "| Pos. | Pair / strategy | Full evidence@10 | Recall@10 | MRR@10 | nDCG@10 | Stable queries | P95 |",
        "|---:|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in report["ranking"]:
        metrics = row["metrics"]
        lines.append(
            f"| {row['position']} | {row['label']} | "
            f"{_percent(metrics['full_evidence_set_rate_at_10'])} | "
            f"{_percent(metrics['recall_at_10'])} | "
            f"{_percent(metrics['mrr_at_10'])} | "
            f"{_percent(metrics['ndcg_at_10'])} | "
            f"{_percent(row['query_stability_ratio'])} | "
            f"{row['representative_p95_ms']:.2f} ms |"
        )
    lines.extend(
        [
            "",
            "Scope: 40 evaluation-only contradiction audits over the existing fifteen-paper corpus; "
            "15 questions require two papers, 20 require three, and 5 require four. "
            "Full evidence@10 is the primary metric because a contradiction cannot be adjudicated "
            "when any required side is absent.",
            "",
            "This table measures direct retrieval and exact evidence validity, not generated-answer "
            "correctness. Graphify and Turso are omitted because neither exposes the same paper-level "
            "Top-10 contract.",
            "",
        ]
    )
    return "\n".join(lines)


def comparison_companion(report: Mapping[str, Any]) -> dict[str, Any]:
    """Build the final-report-comparison companion."""

    metric_specs = [
        ("full_evidence_set_rate_at_10", "Full evidence@10", "mean", "percent", "higher", 2),
        ("recall_at_10", "Recall@10", "mean", "percent", "higher", 2),
        ("mrr_at_10", "MRR@10", "mean", "percent", "higher", 2),
        ("ndcg_at_10", "nDCG@10", "mean", "percent", "higher", 2),
        ("query_stability_ratio", "Stable queries", "ratio", "percent", "higher", 2),
        ("representative_p95_ms", "P95", "percentile_95", "ms", "lower", 2),
    ]
    return {
        "schema_version": "final-report-comparison/1.0",
        "heading": "## Cross-source contradiction retrieval comparison",
        "report": "contradiction-strategy-ranking.table.md",
        "dataset_scope": {
            "dataset_id": DATASET_ID,
            "cohort": "evaluation-only-contradiction-40",
            "candidate_budget": "top-10",
            "identity_grouping": "authoritative-paper",
            "metric_contract": "graphrag-contradiction-direct-retrieval/1.0",
        },
        "metrics": [
            {
                "id": metric_id,
                "label": label,
                "aggregation": aggregation,
                "unit": unit,
                "direction": direction,
                "display_precision": precision,
            }
            for metric_id, label, aggregation, unit, direction, precision in metric_specs
        ],
        "alternatives": [
            {
                "id": row["strategy_id"],
                "label": row["label"],
                "metrics": {
                    "full_evidence_set_rate_at_10": 100.0
                    * row["metrics"]["full_evidence_set_rate_at_10"],
                    "recall_at_10": 100.0 * row["metrics"]["recall_at_10"],
                    "mrr_at_10": 100.0 * row["metrics"]["mrr_at_10"],
                    "ndcg_at_10": 100.0 * row["metrics"]["ndcg_at_10"],
                    "query_stability_ratio": 100.0 * row["query_stability_ratio"],
                    "representative_p95_ms": row["representative_p95_ms"],
                },
            }
            for row in report["ranking"]
        ],
    }


def _repeat(parser: argparse.ArgumentParser, flag: str) -> None:
    parser.add_argument(flag, type=Path, action="append", required=True)


def main(argv: Sequence[str] | None = None) -> int:
    """Aggregate reports and write append-only outputs."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selection", type=Path, required=True)
    parser.add_argument("--questions", type=Path, required=True)
    _repeat(parser, "--adaptive-report")
    parser.add_argument("--ensemble-report", type=Path, required=True)
    _repeat(parser, "--rust-report")
    _repeat(parser, "--tantivy-report")
    _repeat(parser, "--tika-report")
    _repeat(parser, "--tika-tantivy-report")
    _repeat(parser, "--v45-report")
    _repeat(parser, "--v48-report")
    _repeat(parser, "--v51-report")
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
        render_markdown(report),
        encoding="utf-8",
        newline="\n",
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
