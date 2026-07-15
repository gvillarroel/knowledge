#!/usr/bin/env python3
"""Create a compact, evidence-preserving summary of embedding comparison reports."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Sequence


SCHEMA_VERSION = "semantic-okf-embeddings-comparison-summary/1.0"
ROUTES = ("legacy_lexical", "new_lexical", "vector", "hybrid")


class SummaryError(ValueError):
    """Describe an invalid source report or unsafe output request."""


def _object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise SummaryError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_report(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_object)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise SummaryError(f"cannot load comparison report {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise SummaryError(f"comparison report must be an object: {path}")
    return value


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _route_summary(route: Any, expected_questions: list[str]) -> dict[str, Any]:
    if not isinstance(route, dict):
        raise SummaryError("route must be an object")
    queries = route.get("queries")
    if not isinstance(queries, list):
        raise SummaryError(f"route {route.get('name')!r} has no query array")
    question_ids = [query.get("question_id") for query in queries if isinstance(query, dict)]
    if question_ids != expected_questions:
        raise SummaryError(f"route {route.get('name')!r} question identities differ")
    compact_queries: list[dict[str, Any]] = []
    for query in queries:
        if not isinstance(query, dict):
            raise SummaryError("query must be an object")
        compact_queries.append(
            {
                key: query[key]
                for key in (
                    "question_id",
                    "elapsed_ms",
                    "error",
                    "hit_count",
                    "paper_ids",
                    "source_ids",
                    "paper_metrics",
                    "source_metrics",
                    "evidence_validity",
                )
            }
        )
    summary = {
        key: route[key]
        for key in (
            "name",
            "query_count",
            "error_count",
            "errors",
            "timing_scope",
            "timing_ms",
            "paper_metrics",
            "source_metrics",
            "evidence_validity",
        )
    }
    if "setup_ms" in route:
        summary["setup_ms"] = route["setup_ms"]
    summary["queries"] = compact_queries
    return summary


def _cohort(report: dict[str, Any], expected_top_k: int) -> dict[str, Any]:
    if report.get("schema_version") != "1.2" or report.get("top_k") != expected_top_k:
        raise SummaryError(f"source report must use schema 1.2 and top_k={expected_top_k}")
    routes = report.get("routes")
    if not isinstance(routes, list) or [route.get("name") for route in routes if isinstance(route, dict)] != list(ROUTES):
        raise SummaryError("source report route identities differ")
    first_queries = routes[0].get("queries")
    if not isinstance(first_queries, list):
        raise SummaryError("source report has no query rows")
    question_ids = [query.get("question_id") for query in first_queries if isinstance(query, dict)]
    if len(question_ids) != 30 or len(set(question_ids)) != 30:
        raise SummaryError("source report must contain 30 unique questions")
    compact_routes = [_route_summary(route, question_ids) for route in routes]
    return {
        "top_k": expected_top_k,
        "query_count": len(question_ids),
        "question_ids": question_ids,
        "routes": compact_routes,
    }


def summarize(primary_path: Path, diagnostic_path: Path) -> dict[str, Any]:
    primary = load_report(primary_path)
    diagnostic = load_report(diagnostic_path)
    primary_cohort = _cohort(primary, 100)
    diagnostic_cohort = _cohort(diagnostic, 10)
    if primary_cohort["question_ids"] != diagnostic_cohort["question_ids"]:
        raise SummaryError("primary and diagnostic question identities differ")
    for field in (
        "bundles",
        "core_semantic_parity",
        "inputs",
        "metric_contract",
        "evidence_contract",
        "timing_methodology",
    ):
        if primary.get(field) != diagnostic.get(field):
            raise SummaryError(f"primary and diagnostic {field} contracts differ")

    cohorts = {
        "primary_identity_collapsed": primary_cohort,
        "chunk_concentration_diagnostic": diagnostic_cohort,
    }
    route_rows = [*primary_cohort["routes"], *diagnostic_cohort["routes"]]
    errors_absent = all(route["error_count"] == 0 and route["errors"] == [] for route in route_rows)
    evidence_valid = all(route["evidence_validity"].get("ratio") == 1.0 for route in route_rows)
    parity = primary["core_semantic_parity"]
    core_parity = (
        parity.get("status") == "pass"
        and parity.get("authoritative_file_set", {}).get("equal") is True
        and parity.get("logical_core_tree_equal") is True
        and parity.get("key_artifacts_equal") is True
    )
    gates = {
        "thirty_questions_in_both_cohorts": True,
        "route_identities_equal": True,
        "zero_query_errors": errors_absent,
        "all_retained_evidence_valid": evidence_valid,
        "authoritative_core_parity": core_parity,
    }
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "pass" if all(gates.values()) else "fail",
        "source_reports": {
            "primary": {
                "path": primary_path.as_posix(),
                "sha256": sha256(primary_path),
                "bytes": primary_path.stat().st_size,
            },
            "diagnostic": {
                "path": diagnostic_path.as_posix(),
                "sha256": sha256(diagnostic_path),
                "bytes": diagnostic_path.stat().st_size,
            },
        },
        "inputs": primary["inputs"],
        "bundles": primary["bundles"],
        "core_semantic_parity": parity,
        "metric_contract": primary["metric_contract"],
        "evidence_contract": primary["evidence_contract"],
        "timing_methodology": primary["timing_methodology"],
        "cohorts": cohorts,
        "gates": gates,
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--primary", type=Path, required=True)
    parser.add_argument("--diagnostic", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        if args.output.exists():
            raise SummaryError(f"refusing to overwrite existing summary: {args.output}")
        result = summarize(args.primary, args.diagnostic)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
    except (SummaryError, OSError, KeyError) as exc:
        print(f"error: {exc}")
        return 2
    print(json.dumps({"status": result["status"], "output": args.output.as_posix()}))
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
