#!/usr/bin/env python3
"""Aggregate repeated direct-retrieval reports into one generalization table."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import statistics
from typing import Any, Mapping, Sequence


SCHEMA_VERSION = "graphrag-unseen-generalization-comparison/1.0"
METRICS = ("recall_at_10", "mrr_at_10", "ndcg_at_10")


class AggregateError(ValueError):
    """Describe incompatible or incomplete direct-retrieval reports."""


def _load(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise AggregateError(f"Cannot read report {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise AggregateError(f"Report is not an object: {path}")
    return value


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _percent(value: float) -> str:
    return f"{value * 100:.2f}%"


def _candidate_row(candidate_id: str, paths: Sequence[Path]) -> dict[str, Any]:
    if len(paths) != 3:
        raise AggregateError(f"{candidate_id} requires exactly three reports")
    reports = [_load(path) for path in paths]
    if any(report.get("status") != "pass" for report in reports):
        raise AggregateError(f"{candidate_id} has a non-passing report")
    bindings = {
        (
            report.get("inputs", {}).get("questions", {}).get("sha256"),
            report.get("query_count"),
            report.get("top_k"),
        )
        for report in reports
    }
    if len(bindings) != 1:
        raise AggregateError(f"{candidate_id} report inputs drifted")
    routes = [report.get("routes") for report in reports]
    if any(not isinstance(route_rows, list) or len(route_rows) != 1 for route_rows in routes):
        raise AggregateError(f"{candidate_id} has an invalid route list")
    route_rows = [route_rows[0] for route_rows in routes]
    if any(route.get("error_count") != 0 for route in route_rows):
        raise AggregateError(f"{candidate_id} has query errors")
    if any(route.get("evidence_validity", {}).get("ratio") != 1.0 for route in route_rows):
        raise AggregateError(f"{candidate_id} has invalid evidence")
    rankings = [
        [
            (query.get("question_id"), query.get("paper_ids"))
            for query in route.get("queries", [])
        ]
        for route in route_rows
    ]
    question_count = len(rankings[0])
    if any(len(ranking) != question_count for ranking in rankings[1:]):
        raise AggregateError(f"{candidate_id} query rows drifted")
    stable_queries = sum(
        1
        for index in range(question_count)
        if rankings[0][index] == rankings[1][index] == rankings[2][index]
    )
    metric_values = {}
    replicate_metrics = {}
    for metric in METRICS:
        values = [float(route["paper_metrics"][metric]) for route in route_rows]
        replicate_metrics[metric] = values
        metric_values[metric] = statistics.median(values)
    p95_values = [float(route["timing_ms"]["p95"]) for route in route_rows]
    binding = next(iter(bindings))
    return {
        "candidate_id": candidate_id,
        "query_sha256": binding[0],
        "query_count": binding[1],
        "top_k": binding[2],
        "metrics": metric_values,
        "replicate_metrics": replicate_metrics,
        "representative_p95_ms": statistics.median(p95_values),
        "replicate_p95_ms": p95_values,
        "evidence_validity": 1.0,
        "deterministic": stable_queries == question_count,
        "stable_query_count": stable_queries,
        "query_stability_ratio": stable_queries / question_count,
        "ranking_sha256s": [
            hashlib.sha256(
                json.dumps(
                    ranking,
                    ensure_ascii=False,
                    sort_keys=True,
                    separators=(",", ":"),
                ).encode("utf-8")
            ).hexdigest()
            for ranking in rankings
        ],
        "reports": [
            {"path": str(path), "sha256": _sha256(path)}
            for path in paths
        ],
    }


def aggregate(
    candidate_specs: Sequence[str],
    *,
    benchmark_manifest: Path,
    title: str = "Post-v51 unseen-question retrieval comparison",
    scope: str = (
        "Post-v51 unseen questions over the same frozen fifteen-paper corpus; "
        "direct Top-10 paper retrieval only"
    ),
    limitations: Sequence[str] = (),
) -> dict[str, Any]:
    """Aggregate all candidate repetitions under one frozen contract."""

    if not title.strip() or not scope.strip():
        raise AggregateError("Title and scope must not be empty")
    rows = []
    seen: set[str] = set()
    for spec in candidate_specs:
        parts = spec.split("=", 1)
        if len(parts) != 2 or not parts[0]:
            raise AggregateError(f"Invalid --candidate specification: {spec}")
        candidate_id, raw_paths = parts
        if candidate_id in seen:
            raise AggregateError(f"Duplicate candidate: {candidate_id}")
        seen.add(candidate_id)
        paths = [Path(value).resolve() for value in raw_paths.split(",")]
        rows.append(_candidate_row(candidate_id, paths))
    if len(rows) < 2:
        raise AggregateError("At least two candidates are required")
    contracts = {
        (row["query_sha256"], row["query_count"], row["top_k"])
        for row in rows
    }
    if len(contracts) != 1:
        raise AggregateError("Candidate reports do not share one contract")
    rows.sort(
        key=lambda row: (
            -row["metrics"]["ndcg_at_10"],
            -row["metrics"]["recall_at_10"],
            row["representative_p95_ms"],
            row["candidate_id"],
        )
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "pass",
        "ranking_eligible": True,
        "title": title,
        "scope": scope,
        "limitations": list(limitations)
        or [
            "Questions were authored from the known corpus after candidates were frozen.",
            "Expected answers bind to previously reviewed claims but lack a new independent human adjudication.",
            "This study measures unseen-query retrieval, not unseen-corpus or generated-answer generalization.",
            "Metrics and latency are medians of three independent process runs; stability is the share of questions with an identical complete Top-10 paper order in all runs.",
        ],
        "benchmark_manifest": {
            "path": str(benchmark_manifest.resolve()),
            "sha256": _sha256(benchmark_manifest.resolve()),
        },
        "contract": {
            "questions_sha256": next(iter(contracts))[0],
            "question_count": next(iter(contracts))[1],
            "top_k": next(iter(contracts))[2],
            "identity": "canonical versioned paper_id",
            "metrics": list(METRICS),
            "replicates": 3,
        },
        "ranking": [
            {"position": position, **row}
            for position, row in enumerate(rows, start=1)
        ],
    }


def _render(report: Mapping[str, Any]) -> str:
    lines = [
        f"# {report['title']}",
        "",
        "Status: pass. This table is ranking-eligible only for its declared scope:",
        str(report["scope"]) + ".",
        "",
        "| Pos. | Frozen expert strategy | Recall@10 | MRR@10 | nDCG@10 | Stable queries | P95 |",
        "|---:|---|---:|---:|---:|---:|---:|",
    ]
    for row in report["ranking"]:
        metrics = row["metrics"]
        lines.append(
            f"| {row['position']} | `{row['candidate_id']}` | "
            f"{_percent(metrics['recall_at_10'])} | "
            f"{_percent(metrics['mrr_at_10'])} | "
            f"{_percent(metrics['ndcg_at_10'])} | "
            f"{_percent(row['query_stability_ratio'])} | "
            f"{row['representative_p95_ms']:.2f} ms |"
        )
    lines.extend(
        [
            "",
            "All candidates returned exact authoritative evidence and completed every",
            "query without error. Ranking stability is reported rather than assumed.",
            "",
            "## Interpretation limits",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in report["limitations"])
    lines.append("")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", action="append", required=True)
    parser.add_argument("--benchmark-manifest", type=Path, required=True)
    parser.add_argument(
        "--title",
        default="Post-v51 unseen-question retrieval comparison",
    )
    parser.add_argument(
        "--scope",
        default=(
            "Post-v51 unseen questions over the same frozen fifteen-paper "
            "corpus; direct Top-10 paper retrieval only"
        ),
    )
    parser.add_argument("--limitation", action="append", default=[])
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-markdown", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Aggregate or check a comparison."""

    args = build_parser().parse_args(argv)
    try:
        report = aggregate(
            args.candidate,
            benchmark_manifest=args.benchmark_manifest.resolve(),
            title=args.title.strip(),
            scope=args.scope.strip(),
            limitations=args.limitation,
        )
        json_text = json.dumps(
            report,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
            allow_nan=False,
        ) + "\n"
        markdown_text = _render(report)
        outputs = (
            (args.output_json.resolve(), json_text),
            (args.output_markdown.resolve(), markdown_text),
        )
        if args.check:
            for path, expected in outputs:
                if not path.is_file() or path.read_text(encoding="utf-8") != expected:
                    raise AggregateError(f"Aggregate report drifted: {path}")
        else:
            for path, _ in outputs:
                if path.exists():
                    raise AggregateError(f"Refusing to replace report: {path}")
            for path, text in outputs:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text, encoding="utf-8", newline="\n")
    except (AggregateError, OSError, UnicodeError, KeyError, TypeError, ValueError) as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, sort_keys=True))
        return 2
    print(json.dumps({"status": "pass", "candidates": len(report["ranking"])}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
