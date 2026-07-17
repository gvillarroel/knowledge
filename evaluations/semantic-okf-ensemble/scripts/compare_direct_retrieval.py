#!/usr/bin/env python3
"""Recompute one direct retrieval route against the frozen forty questions."""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path
from typing import Any

from _evaluation import (
    ENSEMBLE_PLAN,
    EvaluationError,
    aggregate_metrics,
    benchmark_rows,
    deduplicate,
    display_path,
    find_route,
    load_json,
    percentile,
    ranking_metrics,
    sha256,
    write_new,
)


SCHEMA_VERSION = "semantic-okf-ensemble-direct-retrieval-comparison/1.0"


def _evaluate(
    report_path: Path,
    route_name: str,
    candidate_label: str,
    incumbent_path: Path,
    plan_path: Path,
) -> dict[str, Any]:
    manifest, questions, _ = benchmark_rows()
    report = load_json(report_path)
    if str(report.get("extends_evidence_schema")) != "1.2":
        raise EvaluationError("candidate report must extend evidence-valid schema 1.2")
    if report.get("query_count") != 40 or report.get("top_k") != 10:
        raise EvaluationError("direct comparison requires exactly forty questions and top-k 10")
    route = find_route(report, route_name)
    query_rows = route.get("queries")
    if not isinstance(query_rows, list):
        raise EvaluationError("route queries must be an array")
    expected_ids = [question["id"] for question in questions]
    actual_ids = [row.get("question_id") for row in query_rows if isinstance(row, dict)]
    if actual_ids != expected_ids:
        raise EvaluationError("candidate route question order or identity differs from the frozen forty")

    scored: list[dict[str, Any]] = []
    issues: list[str] = []
    total_hits = 0
    valid_hits = 0
    latencies: list[float] = []
    for question, row in zip(questions, query_rows, strict=True):
        if not isinstance(row, dict):
            raise EvaluationError(f"query row for {question['id']} is not an object")
        if row.get("error") not in (None, ""):
            issues.append(f"{question['id']}: query error: {row['error']}")
        hits = row.get("hits")
        if not isinstance(hits, list):
            raise EvaluationError(f"{question['id']}: hits must be an array")
        papers: list[str | None] = []
        sources: list[str | None] = []
        row_valid = 0
        for rank, hit in enumerate(hits, 1):
            if not isinstance(hit, dict) or hit.get("rank") != rank:
                issues.append(f"{question['id']}: invalid hit rank {rank}")
                continue
            papers.append(hit.get("paper_id"))
            sources.append(hit.get("source_id"))
            validation = hit.get("evidence_validation")
            valid = (
                isinstance(validation, dict)
                and validation.get("valid") is True
                and validation.get("issues") == []
            )
            row_valid += int(valid)
            if not valid:
                issues.append(f"{question['id']}: hit {rank} failed retained evidence validation")
        paper_ids = deduplicate(papers)
        source_ids = deduplicate(sources)
        qrels = question.get("qrels")
        if not isinstance(qrels, dict):
            raise EvaluationError(f"{question['id']}: frozen qrels are invalid")
        paper_metrics = ranking_metrics(paper_ids, set(qrels["paper_ids"]))
        source_metrics = ranking_metrics(source_ids, set(qrels["source_ids"]))
        declared = row.get("evidence_validity")
        if not isinstance(declared, dict) or (
            declared.get("returned") != len(hits)
            or declared.get("valid") != row_valid
            or declared.get("invalid") != len(hits) - row_valid
        ):
            issues.append(f"{question['id']}: evidence-validity aggregate differs from hits")
        elapsed = row.get("elapsed_ms")
        if not isinstance(elapsed, (int, float)) or isinstance(elapsed, bool) or elapsed < 0:
            issues.append(f"{question['id']}: invalid elapsed_ms")
            elapsed = 0.0
        latencies.append(float(elapsed))
        total_hits += len(hits)
        valid_hits += row_valid
        scored.append(
            {
                "id": question["id"],
                "paper_ids": paper_ids,
                "source_ids": source_ids,
                "paper_metrics": paper_metrics,
                "source_metrics": source_metrics,
                "returned": len(hits),
                "valid_evidence": row_valid,
                "elapsed_ms": float(elapsed),
            }
        )

    cohorts = {
        "all_40": scored,
        "original_30": scored[:30],
        "hard_10": scored[30:],
    }
    aggregates = {
        name: {
            "question_count": len(rows),
            "paper_metrics": aggregate_metrics(rows, "paper_metrics"),
            "source_metrics": aggregate_metrics(rows, "source_metrics"),
        }
        for name, rows in cohorts.items()
    }
    evidence_ratio = valid_hits / total_hits if total_hits else 0.0
    declared_route_validity = route.get("evidence_validity")
    if not isinstance(declared_route_validity, dict) or (
        declared_route_validity.get("returned") != total_hits
        or declared_route_validity.get("valid") != valid_hits
        or declared_route_validity.get("invalid") != total_hits - valid_hits
    ):
        issues.append("route evidence-validity aggregate differs from query hits")

    incumbent = load_json(incumbent_path)
    incumbent_route = incumbent.get("routes", {}).get("adaptive_fusion")
    if not isinstance(incumbent_route, dict):
        raise EvaluationError("incumbent summary has no adaptive_fusion route")
    deltas = {
        cohort: {
            metric: aggregates[cohort]["paper_metrics"][metric] - float(incumbent_route[cohort][metric])
            for metric in ("recall_at_10", "mrr_at_10", "ndcg_at_10")
        }
        for cohort in ("all_40", "hard_10")
    }
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "pass" if not issues and evidence_ratio == 1.0 else "fail",
        "candidate_label": candidate_label,
        "route": route_name,
        "benchmark": {
            "id": manifest["benchmark_id"],
            "manifest_sha256": sha256(Path(__file__).resolve().parents[1].parent / "semantic-okf-adaptive-evolution/frozen-benchmark.json"),
            "question_count": len(questions),
        },
        "inputs": {
            "candidate_report": display_path(report_path),
            "candidate_report_sha256": sha256(report_path),
            "candidate_report_schema": report.get("schema_version"),
            "extends_evidence_schema": report.get("extends_evidence_schema"),
            "incumbent_summary": display_path(incumbent_path),
            "incumbent_summary_sha256": sha256(incumbent_path),
            "ensemble_plan": display_path(plan_path),
            "ensemble_plan_sha256": sha256(plan_path),
        },
        "contract": {
            "top_k": 10,
            "paper_identity": "first occurrence of paper_id",
            "source_identity": "first occurrence of source_id",
            "metric_recomputation": True,
            "raw_text_copied": False,
        },
        "evidence_validity": {
            "returned": total_hits,
            "valid": valid_hits,
            "invalid": total_hits - valid_hits,
            "ratio": evidence_ratio,
        },
        "timing_ms": {
            "mean": statistics.fmean(latencies),
            "median": statistics.median(latencies),
            "p95": percentile(latencies, 0.95),
        },
        "cohorts": aggregates,
        "paper_metric_deltas_vs_adaptive_incumbent": deltas,
        "issues": issues,
        "questions": scored,
    }


def _markdown(result: dict[str, Any]) -> str:
    lines = [
        f"# Direct Retrieval Replay: {result['candidate_label']}",
        "",
        f"Status: **{result['status']}**. Route: `{result['route']}`. This report recomputes metrics from retained hits; route provenance is determined by the bound raw report.",
        "",
        "| Cohort / identity | Recall@1 | Recall@3 | Recall@5 | Recall@10 | MRR@10 | nDCG@10 |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for cohort in ("all_40", "original_30", "hard_10"):
        for identity in ("paper_metrics", "source_metrics"):
            metrics = result["cohorts"][cohort][identity]
            lines.append(
                f"| {cohort} / {identity.removesuffix('_metrics')} | "
                f"{metrics['recall_at_1']:.2%} | {metrics['recall_at_3']:.2%} | "
                f"{metrics['recall_at_5']:.2%} | {metrics['recall_at_10']:.2%} | "
                f"{metrics['mrr_at_10']:.2%} | {metrics['ndcg_at_10']:.2%} |"
            )
    evidence = result["evidence_validity"]
    timing = result["timing_ms"]
    lines.extend(
        [
            "",
            f"Evidence validity: **{evidence['ratio']:.2%}** ({evidence['valid']}/{evidence['returned']}). Mean/median/p95 query time: {timing['mean']:.2f}/{timing['median']:.2f}/{timing['p95']:.2f} ms.",
            "",
            "## Paper-level deltas versus the frozen adaptive incumbent",
            "",
            "| Cohort | Recall@10 | MRR@10 | nDCG@10 |",
            "| --- | ---: | ---: | ---: |",
        ]
    )
    for cohort in ("all_40", "hard_10"):
        delta = result["paper_metric_deltas_vs_adaptive_incumbent"][cohort]
        lines.append(
            f"| {cohort} | {delta['recall_at_10']:+.4%} | {delta['mrr_at_10']:+.4%} | {delta['ndcg_at_10']:+.4%} |"
        )
    if result["issues"]:
        lines.extend(["", "## Issues", "", *[f"- {issue}" for issue in result["issues"]]])
    return "\n".join(lines) + "\n"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--route", required=True)
    parser.add_argument("--candidate-label", required=True)
    parser.add_argument(
        "--incumbent-summary",
        type=Path,
        default=Path("evaluations/semantic-okf-adaptive/retrieval-summary.json"),
    )
    parser.add_argument("--plan", type=Path, default=ENSEMBLE_PLAN)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-markdown", type=Path, required=True)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        result = _evaluate(
            args.report.resolve(strict=True),
            args.route,
            args.candidate_label,
            args.incumbent_summary.resolve(strict=True),
            args.plan.resolve(strict=True),
        )
        write_new(args.output_json, json.dumps(result, indent=2, ensure_ascii=False) + "\n")
        write_new(args.output_markdown, _markdown(result))
    except (EvaluationError, OSError, UnicodeError, KeyError, TypeError) as exc:
        print(json.dumps({"status": "fail", "error": str(exc)}, sort_keys=True), file=sys.stderr)
        return 2
    print(
        json.dumps(
            {
                "status": result["status"],
                "route": result["route"],
                "all_40_recall_at_10": result["cohorts"]["all_40"]["paper_metrics"]["recall_at_10"],
                "hard_10_recall_at_10": result["cohorts"]["hard_10"]["paper_metrics"]["recall_at_10"],
                "evidence_validity": result["evidence_validity"]["ratio"],
            },
            sort_keys=True,
        )
    )
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
