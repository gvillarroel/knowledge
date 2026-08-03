#!/usr/bin/env python3
"""Derive reproducible quality/latency recommendations from a sealed ranking."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Iterable, Sequence


DATASET_ID = "graphrag-papers-parallel-eval-60-v1"
EXPECTED_STRATEGY_COUNT = 25
QUALITY_METRIC = "ndcg_at_10"
BALANCED_NDCG_FLOOR = 0.95
ULTRA_FAST_NDCG_FLOOR = 0.90
RECALL_FLOOR = 0.95
SKILL_GROUPS = {
    "classical-association": {
        "evaluated_builder_lineage": "build-semantic-okf-classical",
        "consultant": "consult-semantic-okf-classical",
        "mode": "association",
        "new_build_candidate": "build-semantic-okf-classical",
        "construction_evidence": "evaluated-bundle-and-consult-route",
    },
    "tantivy-bm25": {
        "evaluated_builder_lineage": "build-semantic-okf-classical",
        "consultant": "consult-semantic-okf-tantivy",
        "mode": "tantivy-bm25",
        "new_build_candidate": "build-semantic-okf-tantivy",
        "construction_evidence": (
            "consult-route-evaluated-on-frozen-classical-bundle; "
            "intended-new-builder-not-evaluated-on-this-holdout"
        ),
    },
    "tika-mallet-fusion": {
        "evaluated_builder_lineage": "build-semantic-okf-tika-mallet",
        "consultant": "consult-semantic-okf-tika-mallet",
        "mode": "fusion",
        "new_build_candidate": "build-semantic-okf-tika-mallet",
        "construction_evidence": "evaluated-bundle-and-consult-route",
    },
}


class AnalysisError(RuntimeError):
    """Describe invalid, incomplete, or drifting quality/latency evidence."""


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise AnalysisError(f"cannot load ranking report: {exc}") from exc
    if not isinstance(payload, dict):
        raise AnalysisError("ranking report must be a JSON object")
    return payload


def _finite(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise AnalysisError(f"{label} must be numeric")
    result = float(value)
    if not math.isfinite(result):
        raise AnalysisError(f"{label} must be finite")
    return result


def _eligible_rows(report: dict[str, Any]) -> list[dict[str, Any]]:
    if (
        report.get("status") != "pass"
        or report.get("ranking_eligible") is not True
        or report.get("dataset_id") != DATASET_ID
        or report.get("query_count") != 60
        or report.get("strategy_count") != EXPECTED_STRATEGY_COUNT
        or report.get("top_k") != 10
    ):
        raise AnalysisError("ranking report does not match the sealed comparison contract")
    ranking = report.get("ranking")
    if not isinstance(ranking, list) or len(ranking) != EXPECTED_STRATEGY_COUNT:
        raise AnalysisError("ranking report must contain exactly 25 strategies")
    result: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in ranking:
        if not isinstance(row, dict):
            raise AnalysisError("strategy row must be an object")
        strategy_id = row.get("strategy_id")
        label = row.get("label")
        metrics = row.get("metrics")
        if (
            not isinstance(strategy_id, str)
            or not isinstance(label, str)
            or strategy_id in seen
            or not isinstance(metrics, dict)
        ):
            raise AnalysisError("strategy identity or metrics are invalid")
        seen.add(strategy_id)
        normalized = {
            "strategy_id": strategy_id,
            "label": label,
            "metrics": {
                name: _finite(metrics.get(name), f"{strategy_id}.{name}")
                for name in ("recall_at_10", "mrr_at_10", "ndcg_at_10")
            },
            "evidence_validity": _finite(
                row.get("evidence_validity"), f"{strategy_id}.evidence_validity"
            ),
            "query_stability_ratio": _finite(
                row.get("query_stability_ratio"), f"{strategy_id}.stability"
            ),
            "representative_p95_ms": _finite(
                row.get("representative_p95_ms"), f"{strategy_id}.p95"
            ),
        }
        if any(
            not 0.0 <= value <= 1.0
            for value in (
                *normalized["metrics"].values(),
                normalized["evidence_validity"],
                normalized["query_stability_ratio"],
            )
        ) or normalized["representative_p95_ms"] < 0.0:
            raise AnalysisError(f"{strategy_id} has an out-of-range metric")
        if (
            normalized["evidence_validity"] == 1.0
            and normalized["query_stability_ratio"] == 1.0
        ):
            result.append(normalized)
    if not result:
        raise AnalysisError("no deterministic, evidence-valid strategy is eligible")
    return result


def _dominates(left: dict[str, Any], right: dict[str, Any]) -> bool:
    left_quality = left["metrics"][QUALITY_METRIC]
    right_quality = right["metrics"][QUALITY_METRIC]
    left_latency = left["representative_p95_ms"]
    right_latency = right["representative_p95_ms"]
    return (
        left_quality >= right_quality
        and left_latency <= right_latency
        and (left_quality > right_quality or left_latency < right_latency)
    )


def pareto_frontier(rows: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return non-dominated strategies ordered from highest to lowest quality."""

    materialized = list(rows)
    frontier = [
        row
        for row in materialized
        if not any(
            _dominates(other, row)
            for other in materialized
            if other["strategy_id"] != row["strategy_id"]
        )
    ]
    return sorted(
        frontier,
        key=lambda row: (
            -row["metrics"][QUALITY_METRIC],
            row["representative_p95_ms"],
            row["strategy_id"],
        ),
    )


def _quality_key(row: dict[str, Any]) -> tuple[float, float, float, float, str]:
    return (
        row["metrics"]["ndcg_at_10"],
        row["metrics"]["mrr_at_10"],
        row["metrics"]["recall_at_10"],
        -row["representative_p95_ms"],
        row["strategy_id"],
    )


def _fastest(
    rows: Iterable[dict[str, Any]], *, ndcg_floor: float
) -> dict[str, Any]:
    eligible = [
        row
        for row in rows
        if row["metrics"]["ndcg_at_10"] >= ndcg_floor
        and row["metrics"]["recall_at_10"] >= RECALL_FLOOR
    ]
    if not eligible:
        raise AnalysisError(f"no strategy satisfies the nDCG floor {ndcg_floor}")
    return min(
        eligible,
        key=lambda row: (
            row["representative_p95_ms"],
            -row["metrics"]["ndcg_at_10"],
            row["strategy_id"],
        ),
    )


def _recommendation(
    recommendation_id: str,
    objective: str,
    row: dict[str, Any],
    quality_winner: dict[str, Any],
) -> dict[str, Any]:
    skills = SKILL_GROUPS.get(row["strategy_id"])
    if skills is None:
        raise AnalysisError(f"no skill group is declared for {row['strategy_id']}")
    quality_loss = (
        quality_winner["metrics"]["ndcg_at_10"]
        - row["metrics"]["ndcg_at_10"]
    ) * 100.0
    quality_latency = quality_winner["representative_p95_ms"]
    latency = row["representative_p95_ms"]
    return {
        "recommendation_id": recommendation_id,
        "objective": objective,
        "strategy_id": row["strategy_id"],
        "label": row["label"],
        "skills": skills,
        "metrics": row["metrics"],
        "evidence_validity": row["evidence_validity"],
        "query_stability_ratio": row["query_stability_ratio"],
        "representative_p95_ms": latency,
        "ndcg_loss_vs_quality_winner_percentage_points": quality_loss,
        "latency_reduction_vs_quality_winner_percent": (
            100.0 * (1.0 - latency / quality_latency)
        ),
        "speedup_vs_quality_winner": quality_latency / latency,
    }


def analyze(report_path: Path, expected_sha256: str | None = None) -> dict[str, Any]:
    """Analyze a sealed ranking under explicit, non-tunable decision rules."""

    actual_sha256 = _sha256(report_path)
    if expected_sha256 is not None and actual_sha256 != expected_sha256:
        raise AnalysisError(
            f"ranking report digest differs: expected {expected_sha256}, "
            f"found {actual_sha256}"
        )
    report = _load(report_path)
    rows = _eligible_rows(report)
    quality = max(rows, key=_quality_key)
    balanced = _fastest(rows, ndcg_floor=BALANCED_NDCG_FLOOR)
    ultra_fast = _fastest(rows, ndcg_floor=ULTRA_FAST_NDCG_FLOOR)
    return {
        "schema_version": "graphrag-quality-latency-recommendation/1.1",
        "status": "pass",
        "dataset_id": DATASET_ID,
        "source_report": {
            "path": str(report_path.resolve()),
            "sha256": actual_sha256,
        },
        "decision_status": "provisional-operational-recommendation-not-promotion",
        "decision_rules": {
            "hard_gates": {
                "evidence_validity": 1.0,
                "query_stability_ratio": 1.0,
            },
            "quality_first": (
                "maximize nDCG@10, then MRR@10, Recall@10, and lower P95"
            ),
            "balanced": {
                "minimum_ndcg_at_10": BALANCED_NDCG_FLOOR,
                "minimum_recall_at_10": RECALL_FLOOR,
                "objective": "minimize representative P95",
            },
            "ultra_fast_experimental": {
                "minimum_ndcg_at_10": ULTRA_FAST_NDCG_FLOOR,
                "minimum_recall_at_10": RECALL_FLOOR,
                "objective": "minimize representative P95",
            },
        },
        "recommendations": [
            _recommendation(
                "quality-first",
                "maximum direct-retrieval quality",
                quality,
                quality,
            ),
            _recommendation(
                "balanced-default",
                "best quality/latency under the 95% nDCG and recall floors",
                balanced,
                quality,
            ),
            _recommendation(
                "ultra-fast-experimental",
                "lowest P95 under the 90% nDCG and 95% recall floors",
                ultra_fast,
                quality,
            ),
        ],
        "pareto_frontier": pareto_frontier(rows),
        "limitations": [
            "The evidence measures direct retrieval, not generated-answer correctness.",
            "The decision rules were documented after evaluation and do not constitute holdout-qualified promotion.",
            "Do not tune, fuse, cascade, or evolve these strategies against this evaluation-only dataset.",
            "A production default change requires a new sealed validation cohort.",
            "The Tika/MALLET pair remains experimental because its builder uses preview Tika software.",
            "Tantivy latency and quality were measured on a frozen classical bundle; the intended Tantivy builder was not rebuilt or evaluated on this holdout.",
        ],
    }


def _percent(value: float) -> str:
    return f"{100.0 * value:.2f}%"


def render_frontier(report: dict[str, Any]) -> str:
    """Render the metric-only Pareto frontier for safe publication."""

    lines = [
        "# GraphRAG quality-latency Pareto frontier",
        "",
        "## Quality-latency Pareto frontier",
        "",
        "| Pos. | Pair / strategy | Recall@10 | MRR@10 | nDCG@10 | Stable queries | P95 |",
        "|---:|---|---:|---:|---:|---:|---:|",
    ]
    for position, row in enumerate(report["pareto_frontier"], 1):
        lines.append(
            f"| {position} | {row['label']} | "
            f"{_percent(row['metrics']['recall_at_10'])} | "
            f"{_percent(row['metrics']['mrr_at_10'])} | "
            f"{_percent(row['metrics']['ndcg_at_10'])} | "
            f"{_percent(row['query_stability_ratio'])} | "
            f"{row['representative_p95_ms']:.2f} ms |"
        )
    lines.extend(
        [
            "",
            "A strategy is on the frontier when no other deterministic, "
            "evidence-valid strategy has both equal-or-higher nDCG@10 and "
            "equal-or-lower representative P95, with at least one strict gain.",
            "",
        ]
    )
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--expected-sha256")
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-markdown", type=Path, required=True)
    args = parser.parse_args(argv)
    if any(
        path.exists() or path.is_symlink()
        for path in (args.output_json, args.output_markdown)
    ):
        print(json.dumps({"status": "error", "error": "output already exists"}))
        return 2
    try:
        result = analyze(args.report, args.expected_sha256)
    except (AnalysisError, OSError, UnicodeError, ValueError, TypeError) as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, sort_keys=True))
        return 2
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_markdown.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    args.output_markdown.write_text(
        render_frontier(result),
        encoding="utf-8",
        newline="\n",
    )
    print(
        json.dumps(
            {
                "status": "pass",
                "quality_first": result["recommendations"][0]["strategy_id"],
                "balanced_default": result["recommendations"][1]["strategy_id"],
                "pareto_count": len(result["pareto_frontier"]),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
