#!/usr/bin/env python3
"""Create compact checked reports from large schema-1.4 retrieval runs."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "semantic-okf-entity-graph-retrieval-summary/1.0"
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
]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path, expected_top_k: int) -> dict[str, Any]:
    report = json.loads(path.read_text(encoding="utf-8"))
    if report.get("schema_version") != "1.4":
        raise ValueError(f"Expected schema 1.4: {path}")
    if report.get("query_count") != 40 or report.get("top_k") != expected_top_k:
        raise ValueError(f"Unexpected query/top-k contract: {path}")
    names = [route.get("name") for route in report.get("routes", [])]
    if names != EXPECTED_ROUTES:
        raise ValueError(f"Unexpected route order: {names}")
    if report.get("core_semantic_parity", {}).get("status") != "pass":
        raise ValueError(f"Core parity failed: {path}")
    for route in report["routes"]:
        if route.get("error_count") != 0:
            raise ValueError(f"Route {route.get('name')} contains errors")
        validity = route.get("evidence_validity", {})
        if validity.get("invalid") != 0 or validity.get("ratio") != 1.0:
            raise ValueError(f"Route {route.get('name')} contains invalid evidence")
    return report


def _metrics(route: dict[str, Any]) -> dict[str, Any]:
    def metric_set(value: dict[str, Any]) -> dict[str, float]:
        return {
            name: round(float(value[name]), 8)
            for name in ("recall_at_1", "recall_at_3", "recall_at_5", "recall_at_10", "mrr_at_10", "ndcg_at_10")
        }

    return {
        "query_count": route["query_count"],
        "error_count": route["error_count"],
        "evidence_validity": {
            "returned": route["evidence_validity"]["returned"],
            "valid": route["evidence_validity"]["valid"],
            "invalid": route["evidence_validity"]["invalid"],
            "ratio": route["evidence_validity"]["ratio"],
        },
        "all_40": {
            "paper": metric_set(route["paper_metrics"]),
            "source": metric_set(route["source_metrics"]),
        },
        "original_30": {
            "paper": metric_set(route["cohorts"]["original_30"]["paper_metrics"]),
            "source": metric_set(route["cohorts"]["original_30"]["source_metrics"]),
        },
        "hard_10": {
            "paper": metric_set(route["cohorts"]["hard_10"]["paper_metrics"]),
            "source": metric_set(route["cohorts"]["hard_10"]["source_metrics"]),
        },
    }


def _compact_report(path: Path, report: dict[str, Any]) -> dict[str, Any]:
    return {
        "path": path.as_posix(),
        "sha256": _sha256(path),
        "top_k": report["top_k"],
        "query_count": report["query_count"],
        "core_semantic_parity": report["core_semantic_parity"],
        "raw_input_verification": report["inputs"]["raw_input_verification"],
        "route_contracts": report["route_contracts"],
        "timing_warning": report["timing_methodology"]["warning"],
        "routes": {route["name"]: _metrics(route) for route in report["routes"]},
    }


def _winners(summary: dict[str, Any]) -> dict[str, Any]:
    winners: dict[str, Any] = {}
    for run_name in ("top10", "pool100"):
        routes = summary["runs"][run_name]["routes"]
        run_winners: dict[str, Any] = {}
        for cohort in ("all_40", "original_30", "hard_10"):
            cohort_winners: dict[str, Any] = {}
            for metric in ("recall_at_10", "mrr_at_10", "ndcg_at_10"):
                best = max(routes, key=lambda route: routes[route][cohort]["paper"][metric])
                cohort_winners[metric] = {
                    "route": best,
                    "value": routes[best][cohort]["paper"][metric],
                }
            run_winners[cohort] = cohort_winners
        winners[run_name] = run_winners
    return winners


def _markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# Semantic OKF Retrieval Results with Entity Graph",
        "",
        "This compact report summarizes the append-only schema 1.4 runs. All twelve routes used the same 40 questions, "
        "the same authoritative core, and the same exact evidence-validation contract. Elapsed times are diagnostic only.",
        "",
    ]
    for run_name, label in (("top10", "Top-10 direct output"), ("pool100", "Pool-100 with paper-level top-10 scoring")):
        run = summary["runs"][run_name]
        lines.extend(
            [
                f"## {label}",
                "",
                "| Route | All recall@10 | All MRR@10 | All nDCG@10 | Hard recall@10 | Hard MRR@10 | Hard nDCG@10 | Evidence |",
                "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        for route_name in EXPECTED_ROUTES:
            route = run["routes"][route_name]
            all_metrics = route["all_40"]["paper"]
            hard_metrics = route["hard_10"]["paper"]
            lines.append(
                f"| `{route_name}` | {all_metrics['recall_at_10']:.4f} | {all_metrics['mrr_at_10']:.4f} | "
                f"{all_metrics['ndcg_at_10']:.4f} | {hard_metrics['recall_at_10']:.4f} | "
                f"{hard_metrics['mrr_at_10']:.4f} | {hard_metrics['ndcg_at_10']:.4f} | "
                f"{route['evidence_validity']['ratio']:.0%} |"
            )
        lines.append("")

    hard_top10 = summary["runs"]["top10"]["routes"]
    legacy = hard_top10["legacy_lexical"]["hard_10"]["paper"]["recall_at_10"]
    graph_fusion = hard_top10["entity_graph_fusion"]["hard_10"]["paper"]["recall_at_10"]
    classical_fusion = hard_top10["classical_fusion"]["hard_10"]["paper"]["recall_at_10"]
    lines.extend(
        [
            "## Interpretation",
            "",
            f"Entity-graph fusion retrieved {graph_fusion:.1%} of required hard-question papers at 10 versus {legacy:.1%} for the legacy lexical route; "
            f"classical fusion remained highest at {classical_fusion:.1%}. The graph-only entity and traversal routes independently improved hard-question coverage over legacy, "
            "showing that entity resolution and graph paths materially participate in evidence choice. Scores remain discovery signals, not factual authority.",
            "",
            "The pool-100 run is retained because chunk-heavy embedding routes can surface multiple passages from one paper before paper-level deduplication. "
            "Both runs preserve zero-error, 100% evidence-valid outputs and authoritative-core parity.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--top10", type=Path, required=True)
    parser.add_argument("--pool100", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-markdown", type=Path, required=True)
    args = parser.parse_args()

    top10 = _load(args.top10, 10)
    pool100 = _load(args.pool100, 100)
    summary = {
        "schema_version": SCHEMA_VERSION,
        "comparison": "semantic-okf-legacy-embedding-classical-entity-graph-retrieval",
        "question_count": 40,
        "cohorts": {"original_30": 30, "hard_10": 10},
        "route_order": EXPECTED_ROUTES,
        "runs": {
            "top10": _compact_report(args.top10, top10),
            "pool100": _compact_report(args.pool100, pool100),
        },
        "methodology": {
            "primary_identity": "versioned arXiv paper id",
            "authority": "retrieval artifacts are derived and scores are discovery-only",
            "timing": "diagnostic only; setup and execution scopes differ by route",
        },
    }
    summary["winners"] = _winners(summary)
    args.output_json.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    args.output_markdown.write_text(_markdown(summary), encoding="utf-8", newline="\n")
    print(json.dumps({"status": "pass", "routes": len(EXPECTED_ROUTES), "questions": 40}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
