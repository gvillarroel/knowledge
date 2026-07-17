#!/usr/bin/env python3
"""Create compact checked reports from one schema-1.5 adaptive comparison."""

from __future__ import annotations

import argparse
import hashlib
import json
import random
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "semantic-okf-adaptive-retrieval-summary/1.0"
EXPECTED_ROUTES = [
    "legacy_lexical",
    "new_lexical",
    "vector",
    "hybrid",
    "entity_graph_lexical",
    "entity_graph_entity",
    "entity_graph_traversal",
    "entity_graph_fusion",
    "classical_bm25",
    "classical_topic",
    "classical_association",
    "classical_fusion",
    "adaptive_fusion",
]
FAMILIES = {
    "legacy_lexical": "Legacy",
    "new_lexical": "Embedding",
    "vector": "Embedding",
    "hybrid": "Embedding",
    "entity_graph_lexical": "Entity graph",
    "entity_graph_entity": "Entity graph",
    "entity_graph_traversal": "Entity graph",
    "entity_graph_fusion": "Entity graph",
    "classical_bm25": "Classical",
    "classical_topic": "Classical",
    "classical_association": "Classical",
    "classical_fusion": "Classical",
    "adaptive_fusion": "Adaptive",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _metric_set(value: dict[str, Any]) -> dict[str, float]:
    return {
        name: round(float(value[name]), 8)
        for name in (
            "recall_at_1",
            "recall_at_3",
            "recall_at_5",
            "recall_at_10",
            "mrr_at_10",
            "ndcg_at_10",
        )
    }


def _route(route: dict[str, Any]) -> dict[str, Any]:
    return {
        "family": FAMILIES[route["name"]],
        "query_count": route["query_count"],
        "error_count": route["error_count"],
        "evidence_validity": {
            "returned": route["evidence_validity"]["returned"],
            "valid": route["evidence_validity"]["valid"],
            "invalid": route["evidence_validity"]["invalid"],
            "ratio": route["evidence_validity"]["ratio"],
        },
        "all_40": _metric_set(route["paper_metrics"]),
        "original_30": _metric_set(route["cohorts"]["original_30"]["paper_metrics"]),
        "hard_10": _metric_set(route["cohorts"]["hard_10"]["paper_metrics"]),
        "timing_ms": {
            "mean": round(float(route["timing_ms"]["mean"]), 4),
            "median": round(float(route["timing_ms"]["median"]), 4),
            "p95": round(float(route["timing_ms"]["p95"]), 4),
        },
    }


def _winners(routes: dict[str, Any], cohort: str, metric: str) -> dict[str, Any]:
    best = max(route[cohort][metric] for route in routes.values())
    return {
        "routes": sorted(name for name, route in routes.items() if route[cohort][metric] == best),
        "value": best,
    }


def _paired_question_impact(raw_routes: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Describe where paired adaptive/classical metric differences occur."""

    adaptive = {
        query["question_id"]: query
        for query in raw_routes["adaptive_fusion"]["queries"]
    }
    classical = {
        query["question_id"]: query
        for query in raw_routes["classical_fusion"]["queries"]
    }
    if adaptive.keys() != classical.keys() or len(adaptive) != 40:
        raise ValueError("paired adaptive/classical query sets must contain the same 40 IDs")

    metrics: dict[str, Any] = {}
    changed_any: set[str] = set()
    bootstrap_seed = 20260714
    bootstrap_samples = 10_000
    for metric in ("recall_at_10", "mrr_at_10", "ndcg_at_10"):
        question_ids = list(adaptive)
        deltas = [
            float(adaptive[question_id]["paper_metrics"][metric])
            - float(classical[question_id]["paper_metrics"][metric])
            for question_id in question_ids
        ]
        changed = [
            question_id
            for question_id, delta in zip(question_ids, deltas, strict=True)
            if abs(delta) > 1e-15
        ]
        changed_any.update(changed)
        rng = random.Random(bootstrap_seed)
        means = sorted(
            sum(deltas[rng.randrange(len(deltas))] for _ in deltas) / len(deltas)
            for _ in range(bootstrap_samples)
        )
        metrics[metric] = {
            "mean_delta": round(sum(deltas) / len(deltas), 8),
            "positive_questions": sum(delta > 1e-15 for delta in deltas),
            "negative_questions": sum(delta < -1e-15 for delta in deltas),
            "tied_questions": sum(abs(delta) <= 1e-15 for delta in deltas),
            "changed_question_ids": changed,
            "bootstrap_95_percentile_ci": [
                round(means[249], 8),
                round(means[9749], 8),
            ],
        }
    return {
        "question_count": 40,
        "any_metric_changed_question_ids": sorted(changed_any),
        "bootstrap": {
            "method": "paired question-level percentile bootstrap",
            "seed": bootstrap_seed,
            "samples": bootstrap_samples,
        },
        "metrics": metrics,
    }


def summarize(path: Path) -> dict[str, Any]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if raw.get("schema_version") != "1.5":
        raise ValueError("comparison must use schema 1.5")
    if raw.get("query_count") != 40 or raw.get("top_k") != 10:
        raise ValueError("comparison must contain the direct top-10 forty-question benchmark")
    names = [route.get("name") for route in raw.get("routes", [])]
    if names != EXPECTED_ROUTES:
        raise ValueError(f"unexpected route order: {names}")
    if raw.get("core_semantic_parity", {}).get("status") != "pass":
        raise ValueError("authoritative core parity failed")
    raw_routes = {route["name"]: route for route in raw["routes"]}
    routes = {name: _route(route) for name, route in raw_routes.items()}
    for name, route in routes.items():
        if route["error_count"] or route["evidence_validity"]["ratio"] != 1.0:
            raise ValueError(f"route {name} did not produce zero-error fully valid evidence")
    adaptive = routes["adaptive_fusion"]
    classical = routes["classical_fusion"]
    summary = {
        "schema_version": SCHEMA_VERSION,
        "comparison": raw["comparison"],
        "question_count": 40,
        "top_k": 10,
        "cohorts": {"original_30": 30, "hard_10": 10},
        "route_order": EXPECTED_ROUTES,
        "raw_report": {
            "path": path.as_posix(),
            "bytes": path.stat().st_size,
            "sha256": _sha256(path),
            "evidence_schema": raw["extends_evidence_schema"],
        },
        "core_semantic_parity": {
            "status": "pass",
            "adaptive_records_sha256": raw["bundles"]["adaptive"]["fingerprint"]["key_artifacts"]
            ["semantic/records.jsonl"]["sha256"],
            "pair_count": len(raw["core_semantic_parity"]["pairs"]),
        },
        "routes": routes,
        "winners": {
            cohort: {
                metric: _winners(routes, cohort, metric)
                for metric in ("recall_at_10", "mrr_at_10", "ndcg_at_10")
            }
            for cohort in ("all_40", "original_30", "hard_10")
        },
        "adaptive_vs_classical_fusion": {
            cohort: {
                metric: round(adaptive[cohort][metric] - classical[cohort][metric], 8)
                for metric in ("recall_at_10", "mrr_at_10", "ndcg_at_10")
            }
            for cohort in ("all_40", "original_30", "hard_10")
        },
        "paired_question_impact": _paired_question_impact(raw_routes),
        "latency_ratio_vs_classical_fusion": round(
            adaptive["timing_ms"]["mean"] / classical["timing_ms"]["mean"], 4
        ),
        "methodology": {
            "primary_identity": "reviewed paper identity",
            "authority": "retrieval artifacts and scores are derived discovery signals",
            "selection": "adaptive parameters were selected on the original 30; the hard 10 were retained as a no-regression cohort",
            "timing": "diagnostic only because route execution scopes differ",
        },
    }
    return summary


def render_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# Semantic OKF Adaptive Retrieval Comparison",
        "",
        "All routes used the same 40 questions, authoritative Semantic OKF core, direct top-10 protocol, and evidence-valid schema 1.2 contract. Metrics are paper-level; evidence validity is independently checked.",
        "",
        "| Builder / consultant | Route | All recall@10 | All MRR@10 | All nDCG@10 | Hard recall@10 | Hard MRR@10 | Hard nDCG@10 | Evidence | Mean ms |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for name in EXPECTED_ROUTES:
        route = summary["routes"][name]
        all_metrics = route["all_40"]
        hard_metrics = route["hard_10"]
        lines.append(
            f"| {route['family']} | `{name}` | {all_metrics['recall_at_10']:.2%} | "
            f"{all_metrics['mrr_at_10']:.2%} | {all_metrics['ndcg_at_10']:.2%} | "
            f"{hard_metrics['recall_at_10']:.2%} | {hard_metrics['mrr_at_10']:.2%} | "
            f"{hard_metrics['ndcg_at_10']:.2%} | {route['evidence_validity']['ratio']:.0%} | "
            f"{route['timing_ms']['mean']:.2f} |"
        )
    routes = summary["routes"]
    adaptive = routes["adaptive_fusion"]
    classical = routes["classical_fusion"]
    delta = summary["adaptive_vs_classical_fusion"]
    recall_winners = _winners(routes, "all_40", "recall_at_10")["routes"]
    ndcg_winners = _winners(routes, "all_40", "ndcg_at_10")["routes"]
    if recall_winners == ["adaptive_fusion"] and ndcg_winners == ["adaptive_fusion"]:
        overall = (
            "Adaptive fusion has the highest observed all-40 recall@10 "
            f"({adaptive['all_40']['recall_at_10']:.2%}) and nDCG@10 "
            f"({adaptive['all_40']['ndcg_at_10']:.2%})."
        )
    else:
        overall = (
            "Adaptive fusion is not the sole all-40 winner on both recall@10 and nDCG@10; "
            f"its values are {adaptive['all_40']['recall_at_10']:.2%} and "
            f"{adaptive['all_40']['ndcg_at_10']:.2%}, respectively."
        )
    overall += (
        " Relative to classical fusion, the deltas are "
        f"{100 * delta['all_40']['recall_at_10']:+.2f} percentage points of recall and "
        f"{100 * delta['all_40']['ndcg_at_10']:+.2f} points of nDCG."
    )

    hard_metrics = ("recall_at_10", "mrr_at_10", "ndcg_at_10")
    hard_tie = all(adaptive["hard_10"][metric] == classical["hard_10"][metric] for metric in hard_metrics)
    if hard_tie:
        hard = (
            "On the hard ten, adaptive and classical fusion tie exactly at "
            f"{adaptive['hard_10']['recall_at_10']:.2%} recall, "
            f"{adaptive['hard_10']['mrr_at_10']:.2%} MRR, and "
            f"{adaptive['hard_10']['ndcg_at_10']:.2%} nDCG."
        )
    else:
        hard = (
            "On the hard ten, adaptive versus classical deltas are "
            f"{100 * delta['hard_10']['recall_at_10']:+.2f} percentage points of recall, "
            f"{100 * delta['hard_10']['mrr_at_10']:+.2f} points of MRR, and "
            f"{100 * delta['hard_10']['ndcg_at_10']:+.2f} points of nDCG."
        )

    impact = summary["paired_question_impact"]
    changed_ids = impact["any_metric_changed_question_ids"]
    recall_ci = impact["metrics"]["recall_at_10"]["bootstrap_95_percentile_ci"]
    ndcg_ci = impact["metrics"]["ndcg_at_10"]["bootstrap_95_percentile_ci"]
    impact_text = (
        f"Only {len(changed_ids)} of 40 questions changed recall@10, MRR@10, or nDCG@10 "
        f"between adaptive and classical fusion: {', '.join(changed_ids) if changed_ids else 'none'}. "
        "The paired descriptive 95% bootstrap intervals, in percentage points, are "
        f"[{100 * recall_ci[0]:+.2f}, {100 * recall_ci[1]:+.2f}] for recall and "
        f"[{100 * ndcg_ci[0]:+.2f}, {100 * ndcg_ci[1]:+.2f}] for nDCG; intervals that include "
        "zero do not establish a general advantage."
    )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            overall,
            "",
            hard,
            "",
            impact_text,
            "",
            f"The trade-off is compute: adaptive mean query time is {summary['latency_ratio_vs_classical_fusion']:.2f}x classical fusion in this in-process diagnostic. Every route returned 100% independently valid evidence with zero errors, so the accuracy difference is not caused by stale or fabricated hits.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-markdown", type=Path, required=True)
    args = parser.parse_args()
    summary = summarize(args.input)
    args.output_json.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    args.output_markdown.write_text(render_markdown(summary), encoding="utf-8", newline="\n")
    print(json.dumps({"status": "pass", "routes": len(EXPECTED_ROUTES), "questions": 40}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
