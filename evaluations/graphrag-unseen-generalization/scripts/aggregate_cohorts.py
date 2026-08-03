#!/usr/bin/env python3
"""Combine exposed and evaluation-only retrieval reports without mixing scopes."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence


SCHEMA_VERSION = "graphrag-multi-cohort-generalization-comparison/1.0"


class CohortAggregateError(ValueError):
    """Describe incompatible or incomplete cohort reports."""


def _load(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise CohortAggregateError(f"Cannot read report {path}: {exc}") from exc
    if not isinstance(value, dict) or value.get("status") != "pass":
        raise CohortAggregateError(f"Cohort report is not passing: {path}")
    return value


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _rows_by_candidate(report: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    ranking = report.get("ranking")
    if not isinstance(ranking, list) or not ranking:
        raise CohortAggregateError("Cohort report has no ranking")
    rows = {}
    for row in ranking:
        if not isinstance(row, dict) or not isinstance(row.get("candidate_id"), str):
            raise CohortAggregateError("Cohort ranking contains an invalid row")
        candidate_id = row["candidate_id"]
        if candidate_id in rows:
            raise CohortAggregateError(f"Duplicate candidate: {candidate_id}")
        rows[candidate_id] = row
    return rows


def combine(
    canonical_path: Path,
    post_v51_path: Path,
    parallel_path: Path,
) -> dict[str, Any]:
    """Combine cohort metrics while ranking only by evaluation-only evidence."""

    paths = {
        "canonical_exposed_40": canonical_path.resolve(),
        "post_v51_opened_20": post_v51_path.resolve(),
        "parallel_evaluation_only_60": parallel_path.resolve(),
    }
    reports = {name: _load(path) for name, path in paths.items()}
    rows = {
        name: _rows_by_candidate(report)
        for name, report in reports.items()
    }
    candidate_sets = {frozenset(value) for value in rows.values()}
    if len(candidate_sets) != 1:
        raise CohortAggregateError("Cohort candidate sets differ")

    combined = []
    for candidate_id in sorted(next(iter(candidate_sets))):
        canonical = rows["canonical_exposed_40"][candidate_id]
        post_v51 = rows["post_v51_opened_20"][candidate_id]
        parallel = rows["parallel_evaluation_only_60"][candidate_id]
        combined.append(
            {
                "candidate_id": candidate_id,
                "canonical_exposed_40": canonical["metrics"],
                "post_v51_opened_20": post_v51["metrics"],
                "parallel_evaluation_only_60": parallel["metrics"],
                "parallel_stability": parallel["query_stability_ratio"],
                "parallel_p95_ms": parallel["representative_p95_ms"],
                "parallel_deterministic": parallel["deterministic"],
                "opened_unseen_ndcg_floor": min(
                    float(post_v51["metrics"]["ndcg_at_10"]),
                    float(parallel["metrics"]["ndcg_at_10"]),
                ),
                "parallel_vs_exposed_ndcg_delta": (
                    float(parallel["metrics"]["ndcg_at_10"])
                    - float(canonical["metrics"]["ndcg_at_10"])
                ),
            }
        )
    combined.sort(
        key=lambda row: (
            -row["parallel_evaluation_only_60"]["ndcg_at_10"],
            -row["parallel_evaluation_only_60"]["recall_at_10"],
            -row["parallel_stability"],
            row["parallel_p95_ms"],
            row["candidate_id"],
        )
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "pass",
        "ranking_rule": (
            "Rank only by parallel evaluation-only nDCG@10, then Recall@10, "
            "stability, P95, and candidate ID. Exposed cohorts are diagnostic."
        ),
        "cohorts": {
            name: {
                "path": str(path),
                "sha256": _sha256(path),
                "question_count": reports[name]["contract"]["question_count"],
            }
            for name, path in paths.items()
        },
        "ranking": [
            {"position": position, **row}
            for position, row in enumerate(combined, start=1)
        ],
        "limitations": [
            "The forty canonical questions are exposed fixed-workload evidence.",
            "The twenty post-v51 questions are now opened evaluation evidence and must not become future holdout evidence.",
            "Only the sixty-question parallel cohort is evaluation-only and controls the formal generalization rank.",
            "All metrics measure direct retrieval rather than generated-answer correctness.",
        ],
    }


def _percent(value: float) -> str:
    return f"{value * 100:.2f}%"


def _render(report: Mapping[str, Any]) -> str:
    lines = [
        "# Three-cohort GraphRAG retrieval comparison",
        "",
        "The formal position is controlled only by the sixty-question",
        "evaluation-only cohort. The exposed cohorts are diagnostic columns.",
        "",
        "| Pos. | Frozen strategy | Exposed-40 nDCG | Post-v51-20 nDCG | Eval-only-60 Recall | Eval-only-60 MRR | Eval-only-60 nDCG | Stability | P95 |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in report["ranking"]:
        lines.append(
            f"| {row['position']} | `{row['candidate_id']}` | "
            f"{_percent(row['canonical_exposed_40']['ndcg_at_10'])} | "
            f"{_percent(row['post_v51_opened_20']['ndcg_at_10'])} | "
            f"{_percent(row['parallel_evaluation_only_60']['recall_at_10'])} | "
            f"{_percent(row['parallel_evaluation_only_60']['mrr_at_10'])} | "
            f"{_percent(row['parallel_evaluation_only_60']['ndcg_at_10'])} | "
            f"{_percent(row['parallel_stability'])} | "
            f"{row['parallel_p95_ms']:.2f} ms |"
        )
    lines.extend(["", "## Interpretation limits", ""])
    lines.extend(f"- {item}" for item in report["limitations"])
    lines.append("")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--canonical", type=Path, required=True)
    parser.add_argument("--post-v51", type=Path, required=True)
    parser.add_argument("--parallel", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-markdown", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Write or verify the multi-cohort comparison."""

    args = build_parser().parse_args(argv)
    try:
        report = combine(args.canonical, args.post_v51, args.parallel)
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
                    raise CohortAggregateError(f"Comparison drifted: {path}")
        else:
            for path, _ in outputs:
                if path.exists():
                    raise CohortAggregateError(f"Refusing to replace output: {path}")
            for path, text in outputs:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text, encoding="utf-8", newline="\n")
    except (CohortAggregateError, OSError, UnicodeError, KeyError, TypeError) as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, sort_keys=True))
        return 2
    print(json.dumps({"status": "pass", "candidates": len(report["ranking"])}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
