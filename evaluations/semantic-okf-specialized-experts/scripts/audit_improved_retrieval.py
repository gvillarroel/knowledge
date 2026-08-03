#!/usr/bin/env python3
"""Audit one improved expert and replace its predecessor in the shared ranking."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence


REPORT_SCHEMA = "semantic-okf-specialized-expert-retrieval/1.0"
AUDIT_SCHEMA = "semantic-okf-specialized-expert-improvement-audit/1.0"
COMPARISON_SCHEMA = "final-report-comparison/1.0"
CANDIDATE_ID = "specialized-expert-trace-bm25"
CANDIDATE_LABEL = "Specialized expert trace BM25"
SUPERSEDED_ID = "specialized-expert-lexical"
EXPECTED_ROUTE = "specialized_expert_trace_bm25"
EXPECTED_RETRIEVAL_CONTRACT = "trace-bm25-field-fusion-v1"
SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[3]


class AuditError(RuntimeError):
    """Describe a drifted, incomplete, or incomparable expert run."""


def _load_json(path: Path, *, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise AuditError(f"Cannot read {label} at {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise AuditError(f"{label} must be a JSON object: {path}")
    return value


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _portable_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return str(resolved)


def _fingerprint(path: Path) -> dict[str, Any]:
    return {
        "path": _portable_path(path),
        "bytes": path.stat().st_size,
        "sha256": _sha256_file(path),
    }


def _route(
    report: Mapping[str, Any],
    *,
    expected_route: str,
) -> Mapping[str, Any]:
    routes = report.get("routes")
    if not isinstance(routes, list) or len(routes) != 1:
        raise AuditError("Each expert report must contain exactly one route")
    route = routes[0]
    if not isinstance(route, dict) or route.get("name") != expected_route:
        raise AuditError("Improved expert route identity drifted")
    return route


def _validate_report(
    report: Mapping[str, Any],
    *,
    top_k: int,
    label: str,
    expected_route: str,
    expected_retrieval_contract: str,
) -> None:
    scope = report.get("evaluation_scope")
    metric_contract = report.get("metric_contract")
    if (
        report.get("schema_version") != REPORT_SCHEMA
        or report.get("status") != "pass"
        or report.get("dataset_id") != "graphrag-papers-40"
        or report.get("query_count") != 40
        or report.get("top_k") != top_k
        or report.get("ranking_eligible") is not True
        or not isinstance(scope, dict)
        or scope.get("canonical") is not True
        or not isinstance(metric_contract, dict)
        or metric_contract.get("retrieval_contract_id")
        != expected_retrieval_contract
    ):
        raise AuditError(f"{label} does not satisfy the canonical report contract")
    route = _route(report, expected_route=expected_route)
    if route.get("error_count") != 0:
        raise AuditError(f"{label} contains query errors")
    evidence = route.get("evidence_validity")
    if not isinstance(evidence, dict) or evidence.get("ratio") != 1.0:
        raise AuditError(f"{label} does not have perfect evidence validity")
    expert = report.get("expert")
    if (
        not isinstance(expert, dict)
        or expert.get("knowledge_unchanged_after_evaluation") is not True
        or expert.get("expert_unchanged_after_evaluation") is not True
    ):
        raise AuditError(f"{label} did not prove expert immutability")


def _binding_signature(report: Mapping[str, Any]) -> dict[str, Any]:
    inputs = report["inputs"]
    expert = report["expert"]
    trace_evidence = inputs["trace_evidence"]
    if not isinstance(trace_evidence, list) or len(trace_evidence) < 2:
        raise AuditError("Improved expert report lacks trace-distillation evidence")
    return {
        "candidate_id": report["candidate_id"],
        "expert_tree_sha256": expert["tree_sha256"],
        "knowledge_tree_sha256": expert["knowledge_tree_sha256"],
        "expert_manifest_sha256": inputs["expert_manifest"]["sha256"],
        "query_helper_sha256": inputs["query_helper"]["sha256"],
        "guidance_sha256": inputs["guidance"]["sha256"],
        "builder_tree_sha256": inputs["builder_skill"]["tree_sha256"],
        "packager_tree_sha256": inputs["packager_skill"]["tree_sha256"],
        "questions_sha256": inputs["questions"]["sha256"],
        "evaluator_sha256": inputs["evaluator_script"]["sha256"],
        "trace_evidence": [
            {
                "bytes": row["bytes"],
                "sha256": row["sha256"],
            }
            for row in trace_evidence
        ],
    }


def _query_signature(row: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "question_id": row["question_id"],
        "error": row["error"],
        "hit_count": row["hit_count"],
        "paper_ids": row["paper_ids"],
        "source_ids": row["source_ids"],
        "hits": row["hits"],
        "paper_metrics": row["paper_metrics"],
        "source_metrics": row["source_metrics"],
        "evidence_validity": row["evidence_validity"],
    }


def _validate_pool_prefix(
    top10: Mapping[str, Any],
    pool100: Mapping[str, Any],
    *,
    expected_route: str,
) -> None:
    top_rows = _route(top10, expected_route=expected_route)["queries"]
    pool_rows = _route(pool100, expected_route=expected_route)["queries"]
    if len(top_rows) != len(pool_rows):
        raise AuditError("Top-10 and pool-100 question counts differ")
    for top, pool in zip(top_rows, pool_rows, strict=True):
        if top["question_id"] != pool["question_id"]:
            raise AuditError("Top-10 and pool-100 question identity drifted")
        top_hits = top["hits"]
        if top_hits != pool["hits"][: len(top_hits)]:
            raise AuditError(
                "Pool-100 does not retain the exact Top-10 prefix for "
                f"{top['question_id']}"
            )
        for key in ("paper_metrics", "source_metrics"):
            if top[key] != pool[key]:
                raise AuditError(
                    f"Metric prefix drifted for {top['question_id']}: {key}"
                )
        if _query_signature(top) != {
            **_query_signature(pool),
            "hit_count": top["hit_count"],
            "paper_ids": top["paper_ids"],
            "source_ids": top["source_ids"],
            "hits": top["hits"],
            "evidence_validity": top["evidence_validity"],
        }:
            raise AuditError(
                f"Top-10 and pool-100 query contract drifted for {top['question_id']}"
            )


def _metric_map(
    report: Mapping[str, Any],
    *,
    expected_route: str,
) -> dict[str, float]:
    selected = report["selected_metrics"]
    all_40 = selected["all_40"]
    timing = selected["timing_ms"]
    _route(report, expected_route=expected_route)
    return {
        "recall_at_10": 100.0 * float(all_40["recall_at_10"]),
        "ndcg_at_10": 100.0 * float(all_40["ndcg_at_10"]),
        "p95_latency_ms": float(timing["p95"]),
    }


def _replace_comparison(
    reference: Mapping[str, Any],
    metrics: Mapping[str, float],
    *,
    report_name: str,
    candidate_id: str,
    candidate_label: str,
    superseded_id: str,
) -> tuple[dict[str, Any], int, int, dict[str, float]]:
    if reference.get("schema_version") != COMPARISON_SCHEMA:
        raise AuditError("Unsupported reference comparison schema")
    expected_scope = {
        "candidate_budget": "top-10",
        "cohort": "all-40",
        "dataset_id": "graphrag-papers-40",
        "identity_grouping": "authoritative-paper",
        "metric_contract": "graphrag-direct-retrieval/1.0",
    }
    if reference.get("dataset_scope") != expected_scope:
        raise AuditError("Reference comparison scope is not the expert scope")
    alternatives = reference.get("alternatives")
    if not isinstance(alternatives, list):
        raise AuditError("Reference comparison lacks alternatives")
    predecessors = [
        row
        for row in alternatives
        if isinstance(row, dict) and row.get("id") == superseded_id
    ]
    if len(predecessors) != 1:
        raise AuditError("Reference comparison must contain one superseded expert")
    previous_position = next(
        index
        for index, row in enumerate(alternatives, start=1)
        if isinstance(row, dict) and row.get("id") == superseded_id
    )
    previous_metrics = predecessors[0].get("metrics")
    if not isinstance(previous_metrics, dict):
        raise AuditError("Superseded expert lacks metrics")
    if any(
        isinstance(row, dict) and row.get("id") == candidate_id
        for row in alternatives
    ):
        raise AuditError("Reference comparison already contains the improved expert")

    ranked = [
        *(
            row
            for row in alternatives
            if isinstance(row, dict) and row.get("id") != superseded_id
        ),
        {
            "id": candidate_id,
            "label": candidate_label,
            "metrics": dict(metrics),
        },
    ]
    ranked.sort(
        key=lambda row: (
            -float(row["metrics"]["ndcg_at_10"]),
            float(row["metrics"]["p95_latency_ms"]),
            str(row["id"]),
        )
    )
    position = next(
        index
        for index, row in enumerate(ranked, start=1)
        if row["id"] == candidate_id
    )
    comparison = {
        **reference,
        "alternatives": ranked,
        "report": report_name,
    }
    return comparison, position, previous_position, {
        key: float(value)
        for key, value in previous_metrics.items()
    }


def audit(args: argparse.Namespace) -> tuple[dict[str, Any], dict[str, Any]]:
    """Validate the frozen candidate and create its replacement ranking."""

    inputs = {
        "candidate_top10": args.candidate_top10.resolve(),
        "candidate_pool100": args.candidate_pool100.resolve(),
        "reference_comparison": args.reference_comparison.resolve(),
    }
    top10 = _load_json(inputs["candidate_top10"], label="candidate Top-10")
    pool100 = _load_json(inputs["candidate_pool100"], label="candidate pool-100")
    _validate_report(
        top10,
        top_k=10,
        label="candidate Top-10",
        expected_route=args.expected_route,
        expected_retrieval_contract=args.expected_retrieval_contract,
    )
    _validate_report(
        pool100,
        top_k=100,
        label="candidate pool-100",
        expected_route=args.expected_route,
        expected_retrieval_contract=args.expected_retrieval_contract,
    )
    if _binding_signature(top10) != _binding_signature(pool100):
        raise AuditError("Top-10 and pool-100 input bindings differ")
    _validate_pool_prefix(
        top10,
        pool100,
        expected_route=args.expected_route,
    )

    selected_metrics = _metric_map(
        top10,
        expected_route=args.expected_route,
    )
    replay_metrics = _metric_map(
        pool100,
        expected_route=args.expected_route,
    )
    for key in ("recall_at_10", "ndcg_at_10"):
        if selected_metrics[key] != replay_metrics[key]:
            raise AuditError(f"Top-10 quality metric drifted in pool-100: {key}")

    reference = _load_json(
        inputs["reference_comparison"],
        label="reference comparison",
    )
    comparison, position, previous_position, previous_metrics = _replace_comparison(
        reference,
        selected_metrics,
        report_name=args.output_markdown.name,
        candidate_id=args.candidate_id,
        candidate_label=args.candidate_label,
        superseded_id=args.superseded_id,
    )
    expert = top10["expert"]
    inputs_top10 = top10["inputs"]
    report = {
        "schema_version": AUDIT_SCHEMA,
        "status": "pass",
        "dataset_id": "graphrag-papers-40",
        "candidate_id": args.candidate_id,
        "candidate_label": args.candidate_label,
        "candidate_skill": top10["candidate_id"],
        "candidate_route": top10["selected_route"],
        "retrieval_contract_id": top10["metric_contract"][
            "retrieval_contract_id"
        ],
        "ranking_eligible": True,
        "position": position,
        "previous_position": previous_position,
        "alternative_count": len(comparison["alternatives"]),
        "selected_metrics": selected_metrics,
        "previous_metrics": previous_metrics,
        "deltas": {
            key: selected_metrics[key] - previous_metrics[key]
            for key in selected_metrics
        },
        "validation": {
            "exact_top10_prefix_in_pool100": True,
            "exact_input_binding_between_runs": True,
            "expert_immutable": True,
            "knowledge_immutable": True,
            "evidence_validity": 1.0,
            "query_error_count": 0,
        },
        "expert": {
            "tree_sha256": expert["tree_sha256"],
            "file_count": expert["file_count"],
            "knowledge_tree_sha256": expert["knowledge_tree_sha256"],
            "knowledge_file_count": expert["knowledge_file_count"],
            "record_count": expert["record_count"],
            "manifest_sha256": inputs_top10["expert_manifest"]["sha256"],
            "query_helper_sha256": inputs_top10["query_helper"]["sha256"],
            "guidance_sha256": inputs_top10["guidance"]["sha256"],
        },
        "provenance": {
            "builder_skill": inputs_top10["builder_skill"],
            "packager_skill": inputs_top10["packager_skill"],
            "trace_evidence": inputs_top10["trace_evidence"],
        },
        "inputs": {
            key: _fingerprint(path)
            for key, path in inputs.items()
        },
    }
    return report, comparison


def _format_metric(value: float, metric: Mapping[str, Any]) -> str:
    precision = int(metric["display_precision"])
    if metric["unit"] == "percent":
        return f"{value:.{precision}f}%"
    if metric["unit"] == "ms":
        return f"{value:.{precision}f} ms"
    return f"{value:.{precision}f}"


def render_markdown(
    audit_report: Mapping[str, Any],
    comparison: Mapping[str, Any],
) -> str:
    """Render the replacement ranking and validated improvement."""

    metrics = comparison["metrics"]
    lines = [
        "# Trace-Improved Specialized Expert Retrieval Audit",
        "",
        "## Direct comparison",
        "",
        "| Pos. | Pair / strategy | "
        + " | ".join(metric["label"] for metric in metrics)
        + " |",
        "|---:|---|" + "|".join("---:" for _ in metrics) + "|",
    ]
    for position, alternative in enumerate(comparison["alternatives"], start=1):
        values = [
            _format_metric(float(alternative["metrics"][metric["id"]]), metric)
            for metric in metrics
        ]
        lines.append(
            f"| {position} | {alternative['label']} | "
            + " | ".join(values)
            + " |"
        )
    selected = audit_report["selected_metrics"]
    previous = audit_report["previous_metrics"]
    lines.extend(
        [
            "",
            "## Improvement result",
            "",
            f"The frozen `{audit_report['candidate_skill']}` candidate is position "
            f"**{audit_report['position']} of "
            f"{audit_report['alternative_count']}**, replacing its predecessor at "
            f"position {audit_report['previous_position']}.",
            "",
            f"Recall@10 changed from {previous['recall_at_10']:.2f}% to "
            f"{selected['recall_at_10']:.2f}%; nDCG@10 changed from "
            f"{previous['ndcg_at_10']:.2f}% to "
            f"{selected['ndcg_at_10']:.2f}%. The Top-10 result is an exact prefix "
            "of the pool-100 run, every query completed without error, all returned "
            "evidence was exact, and the expert remained byte-identical.",
            "",
        ]
    )
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line interface."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate-top10", type=Path, required=True)
    parser.add_argument("--candidate-pool100", type=Path, required=True)
    parser.add_argument("--reference-comparison", type=Path, required=True)
    parser.add_argument("--candidate-id", default=CANDIDATE_ID)
    parser.add_argument("--candidate-label", default=CANDIDATE_LABEL)
    parser.add_argument("--superseded-id", default=SUPERSEDED_ID)
    parser.add_argument("--expected-route", default=EXPECTED_ROUTE)
    parser.add_argument(
        "--expected-retrieval-contract",
        default=EXPECTED_RETRIEVAL_CONTRACT,
    )
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-markdown", type=Path, required=True)
    parser.add_argument("--output-comparison", type=Path, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Close one append-only improved-expert audit."""

    args = build_parser().parse_args(argv)
    outputs = (
        args.output_json,
        args.output_markdown,
        args.output_comparison,
    )
    if any(path.exists() or path.is_symlink() for path in outputs):
        print(json.dumps({"status": "error", "error": "output already exists"}))
        return 2
    try:
        audit_report, comparison = audit(args)
    except (AuditError, OSError, UnicodeError, ValueError, TypeError, KeyError) as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, sort_keys=True))
        return 2

    for output in outputs:
        output.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(
        json.dumps(
            audit_report,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
            allow_nan=False,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    args.output_comparison.write_text(
        json.dumps(
            comparison,
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
        render_markdown(audit_report, comparison),
        encoding="utf-8",
        newline="\n",
    )
    print(
        json.dumps(
            {
                "status": audit_report["status"],
                "position": audit_report["position"],
                "alternative_count": audit_report["alternative_count"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
