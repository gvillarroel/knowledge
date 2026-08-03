#!/usr/bin/env python3
"""Audit replicated Top-10 and pool-100 Tika/MALLET/Tantivy reports."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Mapping, Sequence


REPORT_SCHEMA = "semantic-okf-tika-mallet-tantivy-canonical-retrieval/1.0"
AUDIT_SCHEMA = "semantic-okf-tika-mallet-tantivy-retrieval-audit/1.0"
ROUTES = (
    "tika_mallet_tantivy_tantivy",
    "tika_mallet_tantivy_topic",
    "tika_mallet_tantivy_association",
    "tika_mallet_tantivy_fusion",
)
SELECTED_ROUTE = "tika_mallet_tantivy_fusion"


class AuditError(ValueError):
    """Raised when retrieval evidence is incomplete or not reproducible."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_report(path: Path, top_k: int) -> dict[str, Any]:
    """Load one complete canonical retrieval report."""

    if not path.is_file() or path.is_symlink():
        raise AuditError(f"report is absent or linked: {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise AuditError(f"invalid report JSON: {path}: {exc}") from exc
    if (
        not isinstance(value, dict)
        or value.get("schema_version") != REPORT_SCHEMA
        or value.get("status") != "pass"
        or value.get("candidate_id") != "tika-mallet-tantivy"
        or value.get("ranking_eligible") is not True
        or value.get("query_count") != 40
        or value.get("top_k") != top_k
        or value.get("selected_route") != SELECTED_ROUTE
        or value.get("deep_validation") is not True
        or value.get("bundle", {}).get("unchanged_after_evaluation") is not True
    ):
        raise AuditError(f"report contract is incomplete: {path}")
    routes = value.get("routes")
    if (
        not isinstance(routes, list)
        or tuple(route.get("name") for route in routes if isinstance(route, dict))
        != ROUTES
    ):
        raise AuditError(f"report routes are incomplete: {path}")
    for route in routes:
        if (
            route.get("query_count") != 40
            or route.get("error_count") != 0
            or route.get("evidence_validity", {}).get("ratio") != 1.0
            or not isinstance(route.get("queries"), list)
            or len(route["queries"]) != 40
        ):
            raise AuditError(f"route is not completely evaluable: {path}")
    runtime = value.get("runtime", {})
    engine = runtime.get("engine", {}) if isinstance(runtime, dict) else {}
    if (
        runtime.get("status") != "pass"
        or runtime.get("validation", {}).get("independent_rederivation") is not True
        or engine.get("package_version") != "0.26.0"
        or engine.get("implementation") != "Rust"
    ):
        raise AuditError(f"runtime identity is incomplete: {path}")
    return value


def report_fingerprint(path: Path, report: Mapping[str, Any]) -> dict[str, Any]:
    """Bind one input report without embedding its large query traces."""

    return {
        "path": path.as_posix(),
        "sha256": sha256_file(path),
        "top_k": report["top_k"],
        "bundle_inventory_sha256": report["bundle"]["inventory_sha256"],
        "records_sha256": report["bundle"]["records"]["sha256"],
    }


def route_signature(report: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Remove timing only; preserve every rank, score, metric, and identity."""

    result = []
    for route in report["routes"]:
        queries = [
            {key: value for key, value in query.items() if key != "elapsed_ms"}
            for query in route["queries"]
        ]
        result.append(
            {
                "name": route["name"],
                "paper_metrics": route["paper_metrics"],
                "source_metrics": route["source_metrics"],
                "cohorts": route["cohorts"],
                "evidence_validity": route["evidence_validity"],
                "errors": route["errors"],
                "queries": queries,
            }
        )
    return result


def assert_prefix(top: Mapping[str, Any], pool: Mapping[str, Any], label: str) -> None:
    """Require every direct Top-10 result to equal the pool prefix."""

    for top_route, pool_route in zip(
        top["routes"],
        pool["routes"],
        strict=True,
    ):
        if top_route["name"] != pool_route["name"]:
            raise AuditError(f"{label} route order drifted")
        for top_query, pool_query in zip(
            top_route["queries"],
            pool_route["queries"],
            strict=True,
        ):
            if top_query["question_id"] != pool_query["question_id"]:
                raise AuditError(f"{label} question order drifted")
            for key in ("hits", "paper_ids", "source_ids"):
                top_value = top_query[key]
                pool_value = pool_query[key]
                if top_value != pool_value[: len(top_value)]:
                    raise AuditError(
                        f"{label} {top_route['name']} "
                        f"{top_query['question_id']} {key} prefix drifted"
                    )


def finite_metric(value: object, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise AuditError(f"{label} is not numeric")
    parsed = float(value)
    if not math.isfinite(parsed):
        raise AuditError(f"{label} is not finite")
    return parsed


def audit(
    *,
    attempt_10_top10: Path,
    attempt_11_top10: Path,
    attempt_10_pool100: Path,
    attempt_11_pool100: Path,
) -> dict[str, Any]:
    """Close one replicated deterministic retrieval audit."""

    paths = {
        "attempt_10_top10": attempt_10_top10,
        "attempt_11_top10": attempt_11_top10,
        "attempt_10_pool100": attempt_10_pool100,
        "attempt_11_pool100": attempt_11_pool100,
    }
    reports = {
        name: load_report(path, 10 if "top10" in name else 100)
        for name, path in paths.items()
    }
    if reports["attempt_10_top10"]["inputs"] != reports["attempt_11_top10"]["inputs"]:
        raise AuditError("Top-10 evaluator inputs drifted")
    if reports["attempt_10_pool100"]["inputs"] != reports["attempt_11_pool100"]["inputs"]:
        raise AuditError("pool-100 evaluator inputs drifted")
    if reports["attempt_10_top10"]["inputs"] != reports["attempt_10_pool100"]["inputs"]:
        raise AuditError("Top-10 and pool-100 evaluator inputs drifted")

    if route_signature(reports["attempt_10_top10"]) != route_signature(
        reports["attempt_11_top10"]
    ):
        raise AuditError("replicated Top-10 rankings, scores, or metrics drifted")
    if route_signature(reports["attempt_10_pool100"]) != route_signature(
        reports["attempt_11_pool100"]
    ):
        raise AuditError("replicated pool-100 rankings, scores, or metrics drifted")
    assert_prefix(
        reports["attempt_10_top10"],
        reports["attempt_10_pool100"],
        "attempt 10",
    )
    assert_prefix(
        reports["attempt_11_top10"],
        reports["attempt_11_pool100"],
        "attempt 11",
    )

    inventories = {
        report["bundle"]["inventory_sha256"] for report in reports.values()
    }
    records = {
        report["bundle"]["records"]["sha256"] for report in reports.values()
    }
    if len(inventories) != 1 or len(records) != 1:
        raise AuditError("replicated bundle or ledger identity drifted")

    selected = reports["attempt_10_top10"]["selected_metrics"]
    metrics = {
        "recall_at_10": finite_metric(
            selected["all_40"]["recall_at_10"],
            "Recall@10",
        ),
        "hard_recall_at_10": finite_metric(
            selected["hard_10"]["recall_at_10"],
            "hard Recall@10",
        ),
        "mrr_at_10": finite_metric(
            selected["all_40"]["mrr_at_10"],
            "MRR@10",
        ),
        "hard_mrr_at_10": finite_metric(
            selected["hard_10"]["mrr_at_10"],
            "hard MRR@10",
        ),
        "ndcg_at_10": finite_metric(
            selected["all_40"]["ndcg_at_10"],
            "nDCG@10",
        ),
        "hard_ndcg_at_10": finite_metric(
            selected["hard_10"]["ndcg_at_10"],
            "hard nDCG@10",
        ),
        "evidence_valid_rate": finite_metric(
            selected["evidence_validity"]["ratio"],
            "evidence validity",
        ),
        "mean_latency_ms": finite_metric(
            selected["timing_ms"]["mean"],
            "mean latency",
        ),
        "p95_latency_ms": finite_metric(
            selected["timing_ms"]["p95"],
            "p95 latency",
        ),
    }
    return {
        "schema_version": AUDIT_SCHEMA,
        "status": "pass",
        "dataset_id": "graphrag-papers-40",
        "candidate_id": "tika-mallet-tantivy",
        "candidate_state": "experimental-comparator-not-registry-family",
        "question_count": 40,
        "selected_route": SELECTED_ROUTE,
        "ranking_eligible": True,
        "parity": {
            "top10_replicate_exact": True,
            "pool100_replicate_exact": True,
            "attempt_10_top10_pool100_prefix_exact": True,
            "attempt_11_top10_pool100_prefix_exact": True,
            "bundle_inventory_exact": True,
            "records_exact": True,
            "evaluator_inputs_exact": True,
        },
        "bundle_inventory_sha256": next(iter(inventories)),
        "records_sha256": next(iter(records)),
        "selected_metrics": metrics,
        "replicate_latency_ms": {
            name: {
                key: finite_metric(
                    report["selected_metrics"]["timing_ms"][key],
                    key,
                )
                for key in ("mean", "p95")
            }
            for name, report in reports.items()
        },
        "reports": {
            name: report_fingerprint(paths[name], report)
            for name, report in reports.items()
        },
        "interpretation": {
            "metrics_source": "prospectively defined attempt-10 direct Top-10 run",
            "selection_basis": (
                "ADR 0055 defined fusion as the combination of native Tantivy, "
                "MALLET topic, and PPMI association rankings before evaluation."
            ),
            "timing_excludes_setup": True,
            "semantic_answer_quality": "not-measured-by-this-retrieval-audit",
        },
    }


def render_markdown(report: Mapping[str, Any]) -> str:
    metrics = report["selected_metrics"]
    return "\n".join(
        [
            "# Tika/MALLET/Tantivy Canonical Retrieval Audit",
            "",
            f"- Status: `{report['status']}`",
            f"- Ranking eligible: `{str(report['ranking_eligible']).lower()}`",
            f"- Questions: `{report['question_count']}`",
            f"- Selected route: `{report['selected_route']}`",
            "- Replicated Top-10 and pool-100 rankings: exact",
            "- Top-10/pool-100 prefix parity in both bundles: exact",
            "- Evaluator inputs and immutable bundle identities: exact",
            "- Exact evidence validity: `1.0000`",
            "",
            "| Recall@10 | Hard Recall@10 | MRR@10 | nDCG@10 | "
            "Mean ms | P95 ms |",
            "|---:|---:|---:|---:|---:|---:|",
            (
                f"| {metrics['recall_at_10']:.4f} | "
                f"{metrics['hard_recall_at_10']:.4f} | "
                f"{metrics['mrr_at_10']:.4f} | "
                f"{metrics['ndcg_at_10']:.4f} | "
                f"{metrics['mean_latency_ms']:.2f} | "
                f"{metrics['p95_latency_ms']:.2f} |"
            ),
            "",
            "ADR 0055 defined the selected fusion route before this evaluation. "
            "Latency excludes shared deep validation. This audit measures retrieval "
            "and evidence mechanics, not prose-level semantic answer quality.",
            "",
        ]
    )


def write_new(path: Path, content: str) -> None:
    if path.exists() or path.is_symlink():
        raise AuditError(f"refusing to overwrite output: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--attempt-10-top10", type=Path, required=True)
    parser.add_argument("--attempt-11-top10", type=Path, required=True)
    parser.add_argument("--attempt-10-pool100", type=Path, required=True)
    parser.add_argument("--attempt-11-pool100", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-markdown", type=Path, required=True)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        report = audit(
            attempt_10_top10=args.attempt_10_top10,
            attempt_11_top10=args.attempt_11_top10,
            attempt_10_pool100=args.attempt_10_pool100,
            attempt_11_pool100=args.attempt_11_pool100,
        )
        write_new(
            args.output_json,
            json.dumps(
                report,
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
                allow_nan=False,
            )
            + "\n",
        )
        write_new(args.output_markdown, render_markdown(report))
    except (
        AuditError,
        OSError,
        UnicodeError,
        ValueError,
        TypeError,
        KeyError,
    ) as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, sort_keys=True))
        return 2
    print(
        json.dumps(
            {
                "status": report["status"],
                "ranking_eligible": report["ranking_eligible"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
