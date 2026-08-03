#!/usr/bin/env python3
"""Audit replicated expert retrieval and calculate its comparable table position."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence


REPORT_SCHEMA = "semantic-okf-specialized-expert-retrieval/1.0"
AUDIT_SCHEMA = "semantic-okf-specialized-expert-retrieval-audit/1.0"
COMPARISON_SCHEMA = "final-report-comparison/1.0"
CANDIDATE_ID = "specialized-expert-lexical"
CANDIDATE_LABEL = "Specialized expert lexical"
SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[3]


class AuditError(RuntimeError):
    """Describe a drifted, incomplete, or incomparable replicated run."""


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


def _route(report: Mapping[str, Any]) -> Mapping[str, Any]:
    routes = report.get("routes")
    if not isinstance(routes, list) or len(routes) != 1:
        raise AuditError("Each expert report must contain exactly one route")
    route = routes[0]
    if not isinstance(route, dict) or route.get("name") != "specialized_expert_lexical":
        raise AuditError("Expert report route identity drifted")
    return route


def _binding_signature(report: Mapping[str, Any]) -> dict[str, Any]:
    inputs = report["inputs"]
    expert = report["expert"]
    trace_evidence = inputs["trace_evidence"]
    if not isinstance(trace_evidence, list) or not trace_evidence:
        raise AuditError("Expert report lacks trace-distillation evidence")
    return {
        "candidate_id": report["candidate_id"],
        "expert_tree_sha256": expert["tree_sha256"],
        "expert_manifest_sha256": inputs["expert_manifest"]["sha256"],
        "query_helper_sha256": inputs["query_helper"]["sha256"],
        "guidance_sha256": inputs["guidance"]["sha256"],
        "builder_tree_sha256": inputs["builder_skill"]["tree_sha256"],
        "trace_evidence": [
            {
                "bytes": row["bytes"],
                "sha256": row["sha256"],
            }
            for row in trace_evidence
        ],
    }


def _validate_report(
    report: Mapping[str, Any],
    *,
    top_k: int,
    label: str,
) -> None:
    if (
        report.get("schema_version") != REPORT_SCHEMA
        or report.get("status") != "pass"
        or report.get("dataset_id") != "graphrag-papers-40"
        or report.get("query_count") != 40
        or report.get("top_k") != top_k
        or report.get("ranking_eligible") is not True
    ):
        raise AuditError(f"{label} does not satisfy the canonical report contract")
    route = _route(report)
    if route.get("error_count") != 0:
        raise AuditError(f"{label} contains query errors")
    evidence = route.get("evidence_validity")
    if not isinstance(evidence, dict) or evidence.get("ratio") != 1.0:
        raise AuditError(f"{label} does not have perfect evidence validity")


def _same_ranked_output(
    first: Mapping[str, Any],
    second: Mapping[str, Any],
    *,
    label: str,
) -> None:
    first_rows = _route(first)["queries"]
    second_rows = _route(second)["queries"]
    if [_query_signature(row) for row in first_rows] != [
        _query_signature(row) for row in second_rows
    ]:
        raise AuditError(
            f"The two expert variants did not reproduce exact {label} output"
        )


def _pool_prefix(top10: Mapping[str, Any], pool100: Mapping[str, Any], *, label: str) -> None:
    top_rows = _route(top10)["queries"]
    pool_rows = _route(pool100)["queries"]
    if len(top_rows) != len(pool_rows):
        raise AuditError(f"{label} Top-10 and pool-100 question counts differ")
    for top, pool in zip(top_rows, pool_rows, strict=True):
        if top["question_id"] != pool["question_id"]:
            raise AuditError(f"{label} question identity drifted")
        top_hits = top["hits"]
        prefix = pool["hits"][: len(top_hits)]
        if top_hits != prefix:
            raise AuditError(
                f"{label} pool-100 output does not retain its exact Top-10 prefix "
                f"for {top['question_id']}"
            )
        for key in ("paper_metrics", "source_metrics"):
            if top[key] != pool[key]:
                raise AuditError(
                    f"{label} metric prefix drifted for {top['question_id']}"
                )


def _metric_map(report: Mapping[str, Any]) -> dict[str, float]:
    selected = report["selected_metrics"]
    all_40 = selected["all_40"]
    timing = selected["timing_ms"]
    return {
        "recall_at_10": 100.0 * float(all_40["recall_at_10"]),
        "ndcg_at_10": 100.0 * float(all_40["ndcg_at_10"]),
        "p95_latency_ms": float(timing["p95"]),
    }


def _augment_comparison(
    reference: Mapping[str, Any],
    metrics: Mapping[str, float],
    *,
    report_name: str,
) -> tuple[dict[str, Any], int]:
    if reference.get("schema_version") != COMPARISON_SCHEMA:
        raise AuditError("Unsupported reference comparison schema")
    scope = reference.get("dataset_scope")
    expected_scope = {
        "candidate_budget": "top-10",
        "cohort": "all-40",
        "dataset_id": "graphrag-papers-40",
        "identity_grouping": "authoritative-paper",
        "metric_contract": "graphrag-direct-retrieval/1.0",
    }
    if scope != expected_scope:
        raise AuditError("Reference comparison scope is not the expert evaluation scope")
    alternatives = reference.get("alternatives")
    if not isinstance(alternatives, list):
        raise AuditError("Reference comparison lacks alternatives")
    existing = [
        row
        for row in alternatives
        if row.get("id") == CANDIDATE_ID
    ]
    if len(existing) > 1:
        raise AuditError("Reference comparison contains duplicate expert candidates")
    if existing and existing[0].get("label") != CANDIDATE_LABEL:
        raise AuditError("Reference expert candidate label drifted")
    candidate = {
        "id": CANDIDATE_ID,
        "label": CANDIDATE_LABEL,
        "metrics": dict(metrics),
    }
    ranked = [
        *(row for row in alternatives if row.get("id") != CANDIDATE_ID),
        candidate,
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
        if row["id"] == CANDIDATE_ID
    )
    comparison = {
        **reference,
        "alternatives": ranked,
        "report": report_name,
    }
    return comparison, position


def audit(args: argparse.Namespace) -> tuple[dict[str, Any], dict[str, Any]]:
    """Validate four runs and create one augmented metric-only comparison."""

    inputs = {
        "v39_top10": args.v39_top10.resolve(),
        "v42_top10": args.v42_top10.resolve(),
        "v39_pool100": args.v39_pool100.resolve(),
        "v42_pool100": args.v42_pool100.resolve(),
        "reference_comparison": args.reference_comparison.resolve(),
    }
    reports = {
        key: _load_json(path, label=key)
        for key, path in inputs.items()
        if key != "reference_comparison"
    }
    _validate_report(reports["v39_top10"], top_k=10, label="v39 Top-10")
    _validate_report(reports["v42_top10"], top_k=10, label="v42 Top-10")
    _validate_report(reports["v39_pool100"], top_k=100, label="v39 pool-100")
    _validate_report(reports["v42_pool100"], top_k=100, label="v42 pool-100")

    bindings = {
        key: _binding_signature(report)
        for key, report in reports.items()
    }
    if bindings["v39_top10"] != bindings["v39_pool100"]:
        raise AuditError("v39 Top-10 and pool-100 input bindings differ")
    if bindings["v42_top10"] != bindings["v42_pool100"]:
        raise AuditError("v42 Top-10 and pool-100 input bindings differ")
    if (
        bindings["v39_top10"]["candidate_id"]
        == bindings["v42_top10"]["candidate_id"]
    ):
        raise AuditError("v39 and v42 must be distinct expert artifacts")
    builder_digests = {
        binding["builder_tree_sha256"]
        for binding in bindings.values()
    }
    if len(builder_digests) != 1:
        raise AuditError("Expert runs do not bind the same builder skill")
    if (
        bindings["v39_top10"]["guidance_sha256"]
        == bindings["v42_top10"]["guidance_sha256"]
    ):
        raise AuditError("Expert variants do not bind distinct guidance")

    v39_expert = reports["v39_top10"]["expert"]
    v42_expert = reports["v42_top10"]["expert"]
    for key in (
        "knowledge_tree_sha256",
        "knowledge_file_count",
        "record_count",
        "knowledge_inventory_sha256",
    ):
        if v39_expert.get(key) != v42_expert.get(key):
            raise AuditError(f"Expert variants differ in embedded knowledge: {key}")
    v39_helper = reports["v39_top10"]["inputs"]["query_helper"]["sha256"]
    v42_helper = reports["v42_top10"]["inputs"]["query_helper"]["sha256"]
    if v39_helper != v42_helper:
        raise AuditError("Expert variants do not use the same query helper")

    _same_ranked_output(
        reports["v39_top10"],
        reports["v42_top10"],
        label="Top-10",
    )
    _same_ranked_output(
        reports["v39_pool100"],
        reports["v42_pool100"],
        label="pool-100",
    )
    _pool_prefix(
        reports["v39_top10"],
        reports["v39_pool100"],
        label="v39",
    )
    _pool_prefix(
        reports["v42_top10"],
        reports["v42_pool100"],
        label="v42",
    )

    selected_metrics = _metric_map(reports["v39_top10"])
    replay_metrics = _metric_map(reports["v42_top10"])
    if any(
        selected_metrics[key] != replay_metrics[key]
        for key in ("recall_at_10", "ndcg_at_10")
    ):
        raise AuditError("Expert variants do not reproduce exact Top-10 quality metrics")
    reference = _load_json(
        inputs["reference_comparison"],
        label="reference comparison",
    )
    comparison, position = _augment_comparison(
        reference,
        selected_metrics,
        report_name=args.output_markdown.name,
    )
    audit_report = {
        "schema_version": AUDIT_SCHEMA,
        "status": "pass",
        "dataset_id": "graphrag-papers-40",
        "candidate_id": CANDIDATE_ID,
        "candidate_label": CANDIDATE_LABEL,
        "ranking_eligible": True,
        "position": position,
        "alternative_count": len(comparison["alternatives"]),
        "selection_basis": (
            "v39 is the prospectively selected metric row; v42 is an independent "
            "guidance-variant replay over the same immutable knowledge and helper"
        ),
        "replication": {
            "exact_top10_across_experts": True,
            "exact_pool100_across_experts": True,
            "exact_top10_prefix_in_pool100": True,
            "knowledge_binding_equal": True,
            "query_helper_equal": True,
            "exact_input_binding_within_variants": True,
            "builder_skill_equal": True,
            "evidence_validity": 1.0,
        },
        "selected_metrics": selected_metrics,
        "replay_metrics": replay_metrics,
        "expert_variants": [
            reports["v39_top10"]["candidate_id"],
            reports["v42_top10"]["candidate_id"],
        ],
        "knowledge": {
            "tree_sha256": v39_expert["knowledge_tree_sha256"],
            "file_count": v39_expert["knowledge_file_count"],
            "record_count": v39_expert["record_count"],
            "inventory_sha256": v39_expert["knowledge_inventory_sha256"],
        },
        "builder_skill": {
            "tree_sha256": bindings["v39_top10"]["builder_tree_sha256"],
        },
        "inputs": {
            key: _fingerprint(path)
            for key, path in inputs.items()
        },
    }
    return audit_report, comparison


def _format_metric(value: float, metric: Mapping[str, Any]) -> str:
    precision = int(metric["display_precision"])
    unit = metric["unit"]
    if unit == "percent":
        return f"{value:.{precision}f}%"
    if unit == "ms":
        return f"{value:.{precision}f} ms"
    return f"{value:.{precision}f}"


def render_markdown(
    audit_report: Mapping[str, Any],
    comparison: Mapping[str, Any],
) -> str:
    """Render the exact metric-only ranking followed by audit conclusions."""

    metrics = comparison["metrics"]
    lines = [
        "# Specialized Expert Canonical Retrieval Audit",
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
    lines.extend(
        [
            "",
            "## Audit result",
            "",
            f"The specialized expert lexical route is position "
            f"**{audit_report['position']} of {audit_report['alternative_count']}** "
            "under the shared all-40 Top-10 contract.",
            "",
            "Both independently packaged guidance variants produced identical "
            "Top-10 rankings and metrics, identical pool-100 rankings, exact "
            "Top-10 prefixes, and 100% exact evidence validity. Their guidance "
            "does not participate in this deterministic retrieval score; grounded "
            "answer quality remains a separate Harbor evaluation.",
            "",
        ]
    )
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line interface."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--v39-top10", type=Path, required=True)
    parser.add_argument("--v42-top10", type=Path, required=True)
    parser.add_argument("--v39-pool100", type=Path, required=True)
    parser.add_argument("--v42-pool100", type=Path, required=True)
    parser.add_argument("--reference-comparison", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-markdown", type=Path, required=True)
    parser.add_argument("--output-comparison", type=Path, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Close one append-only replicated audit."""

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
