#!/usr/bin/env python3
"""Evaluate Tantivy BM25 on the canonical 40-question retrieval contract."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import time
from pathlib import Path
from types import ModuleType
from typing import Any, Mapping, Sequence


SCHEMA_VERSION = "semantic-okf-tantivy-canonical-retrieval/1.0"
SCRIPT_PATH = Path(__file__).resolve()
REPO = SCRIPT_PATH.parents[3]
BASE_COMPARATOR_PATH = (
    REPO
    / "evaluations"
    / "semantic-okf-embeddings"
    / "scripts"
    / "compare_retrieval.py"
)


class CanonicalEvaluationError(RuntimeError):
    """Describe an invalid input or incomplete canonical Tantivy evaluation."""


def load_module(name: str, path: Path) -> ModuleType:
    """Load one evaluator or candidate runtime from a fixed path."""

    specification = importlib.util.spec_from_file_location(name, path)
    if specification is None or specification.loader is None:
        raise CanonicalEvaluationError(f"cannot load Python module from {path}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


BASE = load_module("semantic_okf_tantivy_canonical_base", BASE_COMPARATOR_PATH)


def require_absent(path: Path) -> None:
    """Preserve raw candidate runs as append-only evidence."""

    if path.exists() or path.is_symlink():
        raise CanonicalEvaluationError(f"output already exists: {path}")


def load_runtime(consult_script: Path) -> ModuleType:
    """Load the standalone Tantivy snapshot implementation."""

    support = consult_script.parent / "_tantivy_snapshot.py"
    if not support.is_file():
        raise CanonicalEvaluationError(f"Tantivy support is missing: {support}")
    scripts = support.parent.resolve()
    sys.path.insert(0, str(scripts))
    try:
        return load_module("semantic_okf_tantivy_canonical_runtime", support)
    except (ImportError, OSError, RuntimeError, SyntaxError) as exc:
        raise CanonicalEvaluationError(
            f"cannot load the Tantivy runtime: {exc}"
        ) from exc
    finally:
        sys.path.remove(str(scripts))


def tantivy_hits(
    runtime: ModuleType,
    snapshot: Any,
    query: str,
    top_k: int,
) -> list[Any]:
    """Search natively and normalize document identities for the base scorer."""

    natural_query = " ".join(BASE.TOKEN_RE.findall(query))
    if not natural_query:
        raise CanonicalEvaluationError("canonical question has no searchable terms")
    try:
        payload = runtime.search_snapshot(snapshot, natural_query, top_k)
    except Exception as exc:
        if isinstance(exc, (KeyboardInterrupt, SystemExit)):
            raise
        raise CanonicalEvaluationError(f"Tantivy BM25 search failed: {exc}") from exc
    normalized = dict(payload)
    normalized["results"] = [
        {**item, "chunk_id": item.get("chunk_id") or item.get("document_id")}
        for item in payload.get("results", [])
    ]
    return BASE.parse_search_output(normalized, top_k)


def mean_metrics(rows: Sequence[dict[str, Any]], key: str) -> dict[str, float]:
    """Compute canonical route metrics for one cohort."""

    import statistics

    names = [
        *(f"recall_at_{cutoff}" for cutoff in BASE.METRIC_CUTOFFS),
        "mrr_at_10",
        "ndcg_at_10",
    ]
    return {
        name: statistics.fmean(float(row[key][name]) for row in rows)
        for name in names
    }


def cohort_summary(rows: Sequence[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate one fixed question cohort."""

    returned = sum(int(row["evidence_validity"]["returned"]) for row in rows)
    valid = sum(int(row["evidence_validity"]["valid"]) for row in rows)
    return {
        "query_count": len(rows),
        "error_count": sum(row["error"] is not None for row in rows),
        "paper_metrics": mean_metrics(rows, "paper_metrics"),
        "source_metrics": mean_metrics(rows, "source_metrics"),
        "evidence_validity": {
            "returned": returned,
            "valid": valid,
            "invalid": returned - valid,
            "ratio": valid / returned if returned else None,
        },
    }


def attach_cohorts(
    route: dict[str, Any],
    original_ids: set[str],
    hard_ids: set[str],
) -> None:
    """Attach the canonical original-30 and hard-10 summaries."""

    rows = route["queries"]
    original = [row for row in rows if row["question_id"] in original_ids]
    hard = [row for row in rows if row["question_id"] in hard_ids]
    if len(original) != 30 or len(hard) != 10:
        raise CanonicalEvaluationError("route did not cover both canonical cohorts")
    route["cohorts"] = {
        "original_30": cohort_summary(original),
        "hard_10": cohort_summary(hard),
    }


def evaluate(args: argparse.Namespace) -> dict[str, Any]:
    """Run the complete native Tantivy route with canonical scoring and timing."""

    if args.top_k < 10:
        raise CanonicalEvaluationError("--top-k must be at least 10")
    inventory = BASE.load_inventory(args.inventory)
    questions = BASE.load_questions(args.questions)
    if len(questions) != args.expected_question_count:
        raise CanonicalEvaluationError(
            "evaluation requires "
            f"{args.expected_question_count} questions, found {len(questions)}"
        )
    if args.canonical_cohorts and len(questions) != 40:
        raise CanonicalEvaluationError(
            "--canonical-cohorts requires exactly 40 questions"
        )
    bundle = args.bundle.resolve()
    consult_script = args.consult_script.resolve()
    if not bundle.is_dir() or not consult_script.is_file():
        raise CanonicalEvaluationError("bundle or consultation script is missing")
    raw_verification = BASE.verify_input_inventory(args.input_root, inventory)
    if raw_verification["status"] != "pass":
        raise CanonicalEvaluationError("raw input inventory verification failed")

    runtime = load_runtime(consult_script)
    evaluation_started = time.perf_counter()
    setup_started = time.perf_counter()
    try:
        snapshot = runtime.load_snapshot(bundle)
    except Exception as exc:
        if isinstance(exc, (KeyboardInterrupt, SystemExit)):
            raise
        raise CanonicalEvaluationError(
            f"candidate snapshot validation failed: {exc}"
        ) from exc
    setup_ms = (time.perf_counter() - setup_started) * 1000.0
    ledger = BASE.AuthoritativeLedger.from_bundle(bundle)
    route = BASE.evaluate_route(
        "tantivy_bm25",
        bundle,
        ledger,
        questions,
        lambda query: tantivy_hits(runtime, snapshot, query, args.top_k),
        continue_on_error=False,
    )
    if args.canonical_cohorts:
        attach_cohorts(
            route,
            {question.identifier for question in questions[:30]},
            {question.identifier for question in questions[30:]},
        )
    if route["error_count"] != 0:
        raise CanonicalEvaluationError("Tantivy route produced query errors")
    if route["evidence_validity"]["ratio"] != 1.0:
        raise CanonicalEvaluationError("Tantivy route produced invalid evidence")
    inspect = runtime.inspect_snapshot(snapshot)
    if inspect.get("status") != "pass" or inspect.get("engine", {}).get(
        "package_version"
    ) != "0.26.0":
        raise CanonicalEvaluationError("Tantivy runtime identity drift")

    return {
        "schema_version": SCHEMA_VERSION,
        "status": "pass",
        "candidate_state": "experimental-comparator-not-registry-family",
        "dataset_id": args.dataset_id,
        "query_count": len(questions),
        "top_k": args.top_k,
        "metric_contract": {
            "primary_identity": "paper_id",
            "duplicate_policy": "keep first rank per identity",
            "recall_cutoffs": list(BASE.METRIC_CUTOFFS),
            "mrr_cutoff": 10,
            "ndcg_cutoff": 10,
            "relevance": "binary reviewed qrels",
            "cohorts": (
                "all 40, original 30, and hard 10"
                if args.canonical_cohorts
                else f"one complete {len(questions)}-question evaluation cohort"
            ),
            "query_adapter": (
                "Unicode-insensitive ASCII alphanumeric token extraction followed "
                "by Tantivy default-parser whitespace terms; no qrel-aware expansion"
            ),
        },
        "timing_contract": {
            "unit": "milliseconds",
            "query_scope": (
                "one in-process native Tantivy search with one pathless index "
                "rebuilt from the reused validated snapshot"
            ),
            "setup_scope": "one closed classical snapshot validation",
            "cross_family_warning": (
                "Timing is an operational diagnostic because family setup and "
                "runtime dependencies differ."
            ),
            "evaluation_wall_ms": (
                time.perf_counter() - evaluation_started
            )
            * 1000.0,
            "shared_setup_ms": setup_ms,
        },
        "inputs": {
            "inventory": BASE._file_fingerprint(args.inventory.resolve()),
            "questions": BASE._file_fingerprint(args.questions.resolve()),
            "consult_script": BASE._file_fingerprint(consult_script),
            "runtime_script": BASE._file_fingerprint(
                consult_script.parent / "_tantivy_snapshot.py"
            ),
            "base_comparator_script": BASE._file_fingerprint(BASE_COMPARATOR_PATH),
            "evaluator_script": BASE._file_fingerprint(SCRIPT_PATH),
            "raw_input_verification": raw_verification,
        },
        "bundle": {
            "path": BASE._report_path(bundle),
            "fingerprint": BASE.bundle_fingerprint(bundle),
            "input_coverage": BASE.bundle_input_coverage(bundle, inventory),
        },
        "runtime": inspect,
        "route": route,
    }


def percent(value: Any) -> str:
    """Format one bounded metric as a percentage."""

    return f"{100.0 * float(value):.2f}%"


def render_markdown(report: Mapping[str, Any]) -> str:
    """Render the single candidate row in the canonical table shape."""

    route = report["route"]
    all_metrics = route["paper_metrics"]
    timing = report["timing_contract"]
    lines = [
            "# Tantivy Canonical Direct-Retrieval Run",
            "",
            f"Status: **{report['status']}**. Questions: {report['query_count']}. "
            f"Returned pool: {report['top_k']}.",
            "",
    ]
    if "cohorts" in route:
        hard = route["cohorts"]["hard_10"]["paper_metrics"]
        lines.extend(
            [
            "| Family | Route | All-40 Recall@10 | All-40 MRR@10 | "
            "All-40 nDCG@10 | Hard-10 Recall@10 | Hard-10 MRR@10 | "
            "Hard-10 nDCG@10 | Evidence validity | Mean ms | P95 ms |",
            "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
            f"| Tantivy (experimental) | `tantivy_bm25` | "
            f"{percent(all_metrics['recall_at_10'])} | "
            f"{percent(all_metrics['mrr_at_10'])} | "
            f"{percent(all_metrics['ndcg_at_10'])} | "
            f"{percent(hard['recall_at_10'])} | "
            f"{percent(hard['mrr_at_10'])} | "
            f"{percent(hard['ndcg_at_10'])} | "
            f"{percent(route['evidence_validity']['ratio'])} | "
            f"{route['timing_ms']['mean']:.2f} | "
            f"{route['timing_ms']['p95']:.2f} |",
            ]
        )
    else:
        lines.extend(
            [
            f"| Family | Route | All-{report['query_count']} Recall@10 | "
            f"All-{report['query_count']} MRR@10 | "
            f"All-{report['query_count']} nDCG@10 | Evidence validity | Mean ms | P95 ms |",
            "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
            f"| Tantivy (experimental) | `tantivy_bm25` | "
            f"{percent(all_metrics['recall_at_10'])} | "
            f"{percent(all_metrics['mrr_at_10'])} | "
            f"{percent(all_metrics['ndcg_at_10'])} | "
            f"{percent(route['evidence_validity']['ratio'])} | "
            f"{route['timing_ms']['mean']:.2f} | "
            f"{route['timing_ms']['p95']:.2f} |",
            ]
        )
    lines.extend(
        [
            "",
            "## Timing and validation",
            "",
            f"- Shared closed-snapshot validation: {timing['shared_setup_ms']:.2f} ms.",
            f"- Full evaluator wall time: {timing['evaluation_wall_ms']:.2f} ms.",
            f"- Raw-input inventory, all {report['query_count']} route executions, and exact evidence "
            "validity passed.",
            f"- {timing['cross_family_warning']}",
            "",
        ]
    )
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    """Build the append-only canonical evaluator CLI."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inventory", type=Path, required=True)
    parser.add_argument("--questions", type=Path, required=True)
    parser.add_argument("--input-root", type=Path, required=True)
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--consult-script", type=Path, required=True)
    parser.add_argument("--top-k", type=int, default=10)
    parser.add_argument("--expected-question-count", type=int, default=40)
    parser.add_argument("--dataset-id", default="graphrag-papers-40")
    parser.add_argument(
        "--canonical-cohorts",
        action=argparse.BooleanOptionalAction,
        default=True,
    )
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-markdown", type=Path, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the evaluator and publish one raw report pair."""

    args = build_parser().parse_args(argv)
    try:
        require_absent(args.output_json)
        require_absent(args.output_markdown)
        report = evaluate(args)
    except (
        CanonicalEvaluationError,
        BASE.ComparisonError,
        OSError,
        UnicodeError,
        ValueError,
        TypeError,
    ) as exc:
        print(
            json.dumps(
                {"schema_version": SCHEMA_VERSION, "status": "error", "error": str(exc)},
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 2
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_markdown.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    args.output_markdown.write_text(
        render_markdown(report), encoding="utf-8", newline="\n"
    )
    print(
        json.dumps(
            {
                "schema_version": SCHEMA_VERSION,
                "status": report["status"],
                "query_count": report["query_count"],
                "route": report["route"]["name"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
