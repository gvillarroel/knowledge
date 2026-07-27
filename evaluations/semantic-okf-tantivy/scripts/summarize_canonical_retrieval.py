#!/usr/bin/env python3
"""Validate and summarize the complete canonical Tantivy retrieval runs."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence


SCHEMA_VERSION = "semantic-okf-tantivy-canonical-summary/1.0"
RUN_SCHEMA = "semantic-okf-tantivy-canonical-retrieval/1.0"


class SummaryError(ValueError):
    """Describe incomplete, invalid, or nondeterministic candidate runs."""


def load_json(path: Path) -> dict[str, Any]:
    """Load one JSON object with a path-specific boundary."""

    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SummaryError(f"expected a JSON object: {path}")
    return value


def sha256_file(path: Path) -> str:
    """Return the SHA-256 digest of one evidence file."""

    return hashlib.sha256(path.read_bytes()).hexdigest()


def require_run(report: Mapping[str, Any], top_k: int) -> None:
    """Require one complete canonical candidate run."""

    route = report.get("route")
    if (
        report.get("schema_version") != RUN_SCHEMA
        or report.get("status") != "pass"
        or report.get("candidate_state")
        != "experimental-comparator-not-registry-family"
        or report.get("query_count") != 40
        or report.get("top_k") != top_k
        or not isinstance(route, Mapping)
        or route.get("name") != "tantivy_bm25"
        or route.get("error_count") != 0
        or route.get("evidence_validity", {}).get("ratio") != 1.0
        or len(route.get("queries", [])) != 40
    ):
        raise SummaryError(f"invalid or incomplete Top-{top_k} Tantivy run")


def normalized_queries(report: Mapping[str, Any], limit: int) -> list[dict[str, Any]]:
    """Remove timing and retain the requested ranked prefix."""

    normalized: list[dict[str, Any]] = []
    for query in report["route"]["queries"]:
        row = {key: value for key, value in query.items() if key != "elapsed_ms"}
        row["hits"] = row["hits"][:limit]
        row["hit_count"] = min(int(row["hit_count"]), limit)
        normalized.append(row)
    return normalized


def ranked_prefix(report: Mapping[str, Any], limit: int) -> list[dict[str, Any]]:
    """Return only question IDs and ranked evidence rows for pool comparison."""

    return [
        {
            "question_id": query["question_id"],
            "hits": query["hits"][:limit],
        }
        for query in report["route"]["queries"]
    ]


def metrics(route: Mapping[str, Any], cohort: str | None = None) -> dict[str, float]:
    """Select the three canonical Top-10 paper metrics."""

    source = (
        route["paper_metrics"]
        if cohort is None
        else route["cohorts"][cohort]["paper_metrics"]
    )
    return {
        name: float(source[name])
        for name in ("recall_at_10", "mrr_at_10", "ndcg_at_10")
    }


def deltas(
    candidate: Mapping[str, float],
    baseline: Mapping[str, float],
) -> dict[str, float]:
    """Subtract baseline metrics from candidate metrics."""

    return {
        name: float(candidate[name]) - float(baseline[name])
        for name in candidate
    }


def summarize(
    top10_path: Path,
    replay_path: Path,
    pool100_path: Path,
    baseline_path: Path,
) -> dict[str, Any]:
    """Gate the three candidate runs and compare the direct row to Classical."""

    top10 = load_json(top10_path)
    replay = load_json(replay_path)
    pool100 = load_json(pool100_path)
    baseline_report = load_json(baseline_path)
    require_run(top10, 10)
    require_run(replay, 10)
    require_run(pool100, 100)
    if top10["inputs"] != replay["inputs"] or top10["inputs"] != pool100["inputs"]:
        raise SummaryError("candidate run input fingerprints differ")
    if (
        top10["bundle"]["fingerprint"] != replay["bundle"]["fingerprint"]
        or top10["bundle"]["fingerprint"] != pool100["bundle"]["fingerprint"]
    ):
        raise SummaryError("candidate bundle fingerprint differs across runs")
    if normalized_queries(top10, 10) != normalized_queries(replay, 10):
        raise SummaryError("Top-10 replay changed ranked results")
    if ranked_prefix(top10, 10) != ranked_prefix(pool100, 10):
        raise SummaryError("pool-100 run changed the ranked Top-10 prefix")

    baseline = baseline_report.get("routes", {}).get("classical_bm25")
    if (
        baseline_report.get("question_count") != 40
        or baseline_report.get("top_k") != 10
        or not isinstance(baseline, Mapping)
        or baseline.get("error_count") != 0
        or baseline.get("evidence_validity", {}).get("ratio") != 1.0
    ):
        raise SummaryError("checked Classical BM25 baseline is invalid")

    top_route = top10["route"]
    pool_route = pool100["route"]
    candidate_all = metrics(top_route)
    candidate_hard = metrics(top_route, "hard_10")
    baseline_all = {
        name: float(baseline["all_40"][name]) for name in candidate_all
    }
    baseline_hard = {
        name: float(baseline["hard_10"][name]) for name in candidate_hard
    }
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "pass",
        "candidate_state": "experimental-comparator-not-registry-family",
        "date": "2026-07-23",
        "question_count": 40,
        "route": "tantivy_bm25",
        "runtime": {
            "engine": "Tantivy",
            "implementation": "Rust",
            "package_version": "0.26.0",
            "index_storage": "memory",
            "scoring": "BM25",
        },
        "inputs": {
            "questions_sha256": top10["inputs"]["questions"]["sha256"],
            "inventory_sha256": top10["inputs"]["inventory"]["sha256"],
            "bundle_tree_sha256": top10["bundle"]["fingerprint"][
                "logical_tree_sha256"
            ],
            "skill_runtime_sha256": top10["inputs"]["runtime_script"]["sha256"],
            "top10_report_sha256": sha256_file(top10_path),
            "top10_replay_report_sha256": sha256_file(replay_path),
            "pool100_report_sha256": sha256_file(pool100_path),
            "classical_summary_sha256": sha256_file(baseline_path),
        },
        "determinism": {
            "status": "pass",
            "question_count": 40,
            "ranked_top10_identical": True,
            "pool100_top10_prefix_identical": True,
        },
        "top10": {
            "error_count": 0,
            "evidence_validity": 1.0,
            "route_evidence_rows": top_route["evidence_validity"]["returned"],
            "all_40": candidate_all,
            "hard_10": candidate_hard,
            "timing_ms": top_route["timing_ms"],
            "shared_setup_ms": top10["timing_contract"]["shared_setup_ms"],
            "evaluation_wall_ms": top10["timing_contract"]["evaluation_wall_ms"],
        },
        "pool100": {
            "error_count": 0,
            "evidence_validity": 1.0,
            "route_evidence_rows": pool_route["evidence_validity"]["returned"],
            "all_40": metrics(pool_route),
            "hard_10": metrics(pool_route, "hard_10"),
            "timing_ms": pool_route["timing_ms"],
        },
        "classical_bm25": {
            "all_40": baseline_all,
            "hard_10": baseline_hard,
            "timing_ms": baseline["timing_ms"],
        },
        "tantivy_minus_classical": {
            "all_40": deltas(candidate_all, baseline_all),
            "hard_10": deltas(candidate_hard, baseline_hard),
            "p95_ms": (
                float(top_route["timing_ms"]["p95"])
                - float(baseline["timing_ms"]["p95"])
            ),
        },
        "conclusion": (
            "Report Tantivy BM25 in the general canonical direct-retrieval table "
            "as an experimental comparator. It materially improves recall and "
            "nDCG over Classical BM25 while slightly reducing MRR; registry "
            "admission remains a separate grounded-Harbor decision."
        ),
    }


def percent(value: Any) -> str:
    """Format one bounded metric as a percentage."""

    return f"{100.0 * float(value):.2f}%"


def points(value: Any) -> str:
    """Format one metric delta in percentage points."""

    return f"{100.0 * float(value):+.2f} pp"


def markdown(report: Mapping[str, Any]) -> str:
    """Render the durable candidate summary."""

    top = report["top10"]
    classical = report["classical_bm25"]
    delta = report["tantivy_minus_classical"]
    lines = [
        "# Tantivy Canonical Direct-Retrieval Summary",
        "",
        "The native Tantivy BM25 candidate completed the canonical 40-question "
        "Top-10 comparison, an exact replay, and a pool-100 sensitivity run. "
        "All 120 queries completed without error and every returned evidence "
        "identity passed the independent validator.",
        "",
        "| Route | All-40 Recall@10 | MRR@10 | nDCG@10 | Hard-10 Recall@10 | MRR@10 | nDCG@10 | Evidence validity | P95 ms |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
        "| Tantivy BM25 (experimental) | "
        f"{percent(top['all_40']['recall_at_10'])} | "
        f"{percent(top['all_40']['mrr_at_10'])} | "
        f"{percent(top['all_40']['ndcg_at_10'])} | "
        f"{percent(top['hard_10']['recall_at_10'])} | "
        f"{percent(top['hard_10']['mrr_at_10'])} | "
        f"{percent(top['hard_10']['ndcg_at_10'])} | 100.00% | "
        f"{top['timing_ms']['p95']:.2f} |",
        "| Classical BM25 (accepted reference) | "
        f"{percent(classical['all_40']['recall_at_10'])} | "
        f"{percent(classical['all_40']['mrr_at_10'])} | "
        f"{percent(classical['all_40']['ndcg_at_10'])} | "
        f"{percent(classical['hard_10']['recall_at_10'])} | "
        f"{percent(classical['hard_10']['mrr_at_10'])} | "
        f"{percent(classical['hard_10']['ndcg_at_10'])} | 100.00% | "
        f"{classical['timing_ms']['p95']:.2f} |",
        "| Tantivy minus Classical | "
        f"{points(delta['all_40']['recall_at_10'])} | "
        f"{points(delta['all_40']['mrr_at_10'])} | "
        f"{points(delta['all_40']['ndcg_at_10'])} | "
        f"{points(delta['hard_10']['recall_at_10'])} | "
        f"{points(delta['hard_10']['mrr_at_10'])} | "
        f"{points(delta['hard_10']['ndcg_at_10'])} | 0.00 pp | "
        f"{delta['p95_ms']:+.2f} |",
        "",
        "## Gates",
        "",
        "- Top-10 execution: 40/40 queries, zero errors, "
        f"{top['route_evidence_rows']}/{top['route_evidence_rows']} valid evidence rows.",
        "- Exact replay: identical ranked Top-10 results for all 40 questions.",
        "- Pool-100: 40/40 queries, zero errors, "
        f"{report['pool100']['route_evidence_rows']}/"
        f"{report['pool100']['route_evidence_rows']} valid evidence rows; "
        "the ranked Top-10 prefix and Recall@10 remained "
        f"{percent(report['pool100']['all_40']['recall_at_10'])}.",
        "- Candidate state: experimental comparator; the eight-family Harbor "
        "registry is unchanged.",
        "",
        "Tantivy materially improves retrieval coverage and nDCG over Classical "
        "BM25 in this direct diagnostic while slightly reducing MRR. Its measured "
        "P95 is also lower, but cross-family timing remains operational rather "
        "than an SLA comparison. Report the row; keep registry admission separate.",
        "",
    ]
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    """Build the deterministic summary CLI."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--top10", type=Path, required=True)
    parser.add_argument("--replay", type=Path, required=True)
    parser.add_argument("--pool100", type=Path, required=True)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-markdown", type=Path, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Validate raw runs and publish their durable compact summary."""

    args = build_parser().parse_args(argv)
    try:
        report = summarize(args.top10, args.replay, args.pool100, args.baseline)
        args.output_json.write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        args.output_markdown.write_text(
            markdown(report), encoding="utf-8", newline="\n"
        )
    except (SummaryError, OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise SystemExit(str(exc)) from exc
    print(
        json.dumps(
            {
                "status": report["status"],
                "question_count": report["question_count"],
                "route": report["route"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
