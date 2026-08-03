#!/usr/bin/env python3
"""Evaluate one reference-aware RustMallet candidate on the canonical 40 questions."""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
import time
from pathlib import Path
from types import ModuleType
from typing import Any, Sequence


SCHEMA_VERSION = "semantic-okf-rust-mallet-canonical-retrieval/1.0"
MODES = ("bm25", "topic", "association", "fusion")
REFERENCE_ID_RE = re.compile(r"ref-[0-9a-f]{24}\Z")
SCRIPT_PATH = Path(__file__).resolve()
COMPARATOR_PATH = SCRIPT_PATH.with_name("compare_retrieval.py")


class CanonicalEvaluationError(RuntimeError):
    """Describe an invalid candidate or incomplete canonical evaluation."""


def _load_module(name: str, path: Path) -> ModuleType:
    specification = importlib.util.spec_from_file_location(name, path)
    if specification is None or specification.loader is None:
        raise CanonicalEvaluationError(f"cannot load Python module from {path}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


def _load_candidate_runtime(consult_script: Path) -> ModuleType:
    support = consult_script.parent / "_rust_mallet_snapshot.py"
    if not support.is_file():
        raise CanonicalEvaluationError(
            f"RustMallet consultation support is missing: {support}"
        )
    scripts = support.parent.resolve()
    sys.path.insert(0, str(scripts))
    try:
        return _load_module(
            "semantic_okf_reference_rust_mallet_canonical_runtime", support
        )
    except (ImportError, OSError, RuntimeError, SyntaxError) as exc:
        raise CanonicalEvaluationError(
            f"cannot load the reference-aware RustMallet runtime: {exc}"
        ) from exc
    finally:
        sys.path.remove(str(scripts))


COMPARATOR = _load_module(
    "semantic_okf_rust_mallet_canonical_comparator", COMPARATOR_PATH
)
BASE = COMPARATOR.BASE


def _require_absent(path: Path) -> None:
    if path.exists() or path.is_symlink():
        raise CanonicalEvaluationError(f"output already exists: {path}")


def _reference_contract(snapshot: Any, bundle: Path) -> dict[str, Any]:
    references = getattr(snapshot, "references_by_document", None)
    documents = getattr(snapshot, "documents", None)
    if not isinstance(references, dict) or not isinstance(documents, (list, tuple)):
        raise CanonicalEvaluationError(
            "candidate runtime did not expose documents and references"
        )
    document_ids = [
        row.get("document_id") for row in documents if isinstance(row, dict)
    ]
    if (
        len(document_ids) != len(documents)
        or len(set(document_ids)) != len(document_ids)
        or set(references) != set(document_ids)
    ):
        raise CanonicalEvaluationError(
            "reference dictionary does not cover every candidate document"
        )
    reference_ids = [
        row.get("reference_id") for row in references.values() if isinstance(row, dict)
    ]
    if (
        len(reference_ids) != len(references)
        or len(set(reference_ids)) != len(reference_ids)
        or any(
            not isinstance(reference_id, str)
            or REFERENCE_ID_RE.fullmatch(reference_id) is None
            for reference_id in reference_ids
        )
    ):
        raise CanonicalEvaluationError(
            "reference dictionary IDs are missing, duplicated, or malformed"
        )
    artifact = bundle / "classical" / "references.json"
    if not artifact.is_file():
        raise CanonicalEvaluationError(
            f"reference dictionary artifact is missing: {artifact}"
        )
    return {
        "status": "pass",
        "count": len(reference_ids),
        "artifact": COMPARATOR._file_fingerprint(artifact),
    }


def _load_inputs(
    args: argparse.Namespace,
) -> tuple[dict[str, Any], list[Any], Path, Path]:
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
    baseline = args.baseline_bundle.resolve()
    if not bundle.is_dir():
        raise CanonicalEvaluationError(f"candidate bundle is missing: {bundle}")
    if not baseline.is_dir():
        raise CanonicalEvaluationError(f"baseline bundle is missing: {baseline}")
    if not args.consult_script.resolve().is_file():
        raise CanonicalEvaluationError(
            f"candidate consultation script is missing: {args.consult_script}"
        )
    return inventory, questions, bundle, baseline


def evaluate(args: argparse.Namespace) -> dict[str, Any]:
    """Run all four RustMallet routes with canonical metrics and timing."""

    inventory, questions, bundle, baseline = _load_inputs(args)
    raw_verification = BASE.verify_input_inventory(args.input_root, inventory)
    if raw_verification["status"] != "pass":
        raise CanonicalEvaluationError("raw input inventory verification failed")
    core_parity = COMPARATOR._compare_core(baseline, bundle)
    if core_parity["status"] != "pass" and not args.allow_core_drift:
        raise CanonicalEvaluationError(
            "candidate authoritative core differs from the canonical baseline"
        )

    evaluation_started = time.perf_counter()
    runtime = _load_candidate_runtime(args.consult_script.resolve())
    ledger = BASE.AuthoritativeLedger.from_bundle(bundle)
    setup_started = time.perf_counter()
    try:
        snapshot = runtime.load_snapshot(
            bundle, deep_validation=args.deep_validation
        )
    except Exception as exc:
        if isinstance(exc, (KeyboardInterrupt, SystemExit)):
            raise
        raise CanonicalEvaluationError(
            f"candidate snapshot validation failed: {exc}"
        ) from exc
    setup_ms = (time.perf_counter() - setup_started) * 1000.0
    references = _reference_contract(snapshot, bundle)

    routes: list[dict[str, Any]] = []
    for route_name, mode in (
        ("rust_mallet_bm25", "bm25"),
        ("rust_mallet_topic", "topic"),
        ("rust_mallet_association", "association"),
        ("rust_mallet_fusion", "fusion"),
    ):
        route = BASE.evaluate_route(
            route_name,
            bundle,
            ledger,
            questions,
            lambda query, selected=mode: COMPARATOR._classical_hits(
                runtime, snapshot, query, selected, args.top_k
            ),
            continue_on_error=False,
        )
        route["setup_ms"] = setup_ms if mode == "bm25" else 0.0
        route["timing_scope"] = (
            "In-process search after one shared read-only snapshot load and "
            "independent deep validation; setup is reported on BM25 only."
        )
        routes.append(route)

    original_ids = {question.identifier for question in questions[:30]}
    hard_ids = {question.identifier for question in questions[30:]}
    for route in routes:
        if args.canonical_cohorts:
            COMPARATOR._attach_cohorts(route, original_ids, hard_ids)
        if route["error_count"] != 0:
            raise CanonicalEvaluationError(
                f"route {route['name']} produced query errors"
            )
        if route["evidence_validity"]["ratio"] != 1.0:
            raise CanonicalEvaluationError(
                f"route {route['name']} produced invalid evidence"
            )

    return {
        "schema_version": SCHEMA_VERSION,
        "status": "pass",
        "candidate_state": "experimental-comparator-not-registry-family",
        "dataset_id": args.dataset_id,
        "query_count": len(questions),
        "top_k": args.top_k,
        "deep_validation": args.deep_validation,
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
        },
        "timing_contract": {
            "unit": "milliseconds",
            "query_scope": "one in-process search against one reused snapshot",
            "setup_scope": (
                "one snapshot load plus independent fixed-seed RustMallet "
                "rederivation before timed queries"
            ),
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
            "inventory": COMPARATOR._file_fingerprint(args.inventory.resolve()),
            "questions": COMPARATOR._file_fingerprint(args.questions.resolve()),
            "consult_script": COMPARATOR._file_fingerprint(
                args.consult_script.resolve()
            ),
            "base_comparator_script": COMPARATOR._file_fingerprint(
                COMPARATOR.BASE_COMPARATOR_PATH
            ),
            "rust_comparator_script": COMPARATOR._file_fingerprint(COMPARATOR_PATH),
            "evaluator_script": COMPARATOR._file_fingerprint(SCRIPT_PATH),
            "raw_input_verification": raw_verification,
        },
        "bundle": COMPARATOR._bundle_report(bundle, inventory),
        "baseline_bundle": COMPARATOR._bundle_report(baseline, inventory),
        "core_semantic_parity": core_parity,
        "reference_dictionary": references,
        "routes": routes,
    }


def _percent(value: Any) -> str:
    return f"{100.0 * float(value):.2f}%"


def _milliseconds(value: Any) -> str:
    return f"{float(value):.2f}"


def render_markdown(report: dict[str, Any]) -> str:
    """Render candidate rows in the canonical direct-retrieval shape."""

    has_canonical_cohorts = "cohorts" in report["routes"][0]
    lines = [
        "# Reference-aware RustMallet Canonical Retrieval Run",
        "",
        f"Status: **{report['status']}**. Questions: {report['query_count']}. "
        f"Returned pool: {report['top_k']}. Deep validation: "
        f"{str(report['deep_validation']).lower()}.",
        "",
    ]
    if has_canonical_cohorts:
        lines.extend(
            [
                "| Family | Route | All-40 Recall@10 | All-40 MRR@10 | "
                "All-40 nDCG@10 | Hard-10 Recall@10 | Hard-10 MRR@10 | "
                "Hard-10 nDCG@10 | Evidence validity | Mean ms | P95 ms |",
                "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
    else:
        lines.extend(
            [
                f"| Family | Route | All-{report['query_count']} Recall@10 | "
                f"All-{report['query_count']} MRR@10 | "
                f"All-{report['query_count']} nDCG@10 | Evidence validity | Mean ms | P95 ms |",
                "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
    for route in report["routes"]:
        all_paper = route["paper_metrics"]
        prefix = (
            f"| RustMallet + references | `{route['name']}` | "
            f"{_percent(all_paper['recall_at_10'])} | "
            f"{_percent(all_paper['mrr_at_10'])} | "
            f"{_percent(all_paper['ndcg_at_10'])} | "
        )
        if has_canonical_cohorts:
            hard = route["cohorts"]["hard_10"]
            prefix += (
                f"{_percent(hard['paper_metrics']['recall_at_10'])} | "
                f"{_percent(hard['paper_metrics']['mrr_at_10'])} | "
                f"{_percent(hard['paper_metrics']['ndcg_at_10'])} | "
            )
        lines.append(
            prefix
            + f"{_percent(route['evidence_validity']['ratio'])} | "
            f"{_milliseconds(route['timing_ms']['mean'])} | "
            f"{_milliseconds(route['timing_ms']['p95'])} |"
        )
    timing = report["timing_contract"]
    references = report["reference_dictionary"]
    lines.extend(
        [
            "",
            "## Timing and validation",
            "",
            f"- Shared deep-validation setup: "
            f"{_milliseconds(timing['shared_setup_ms'])} ms.",
            f"- Full evaluator wall time: "
            f"{_milliseconds(timing['evaluation_wall_ms'])} ms.",
            f"- Reference dictionary: {references['count']} IDs; "
            f"SHA-256 `{references['artifact']['sha256']}`.",
            "- Authoritative-core parity, raw-input inventory, all route executions, "
            "and exact evidence validity passed.",
            f"- {timing['cross_family_warning']}",
            "",
        ]
    )
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inventory", type=Path, required=True)
    parser.add_argument("--questions", type=Path, required=True)
    parser.add_argument("--input-root", type=Path, required=True)
    parser.add_argument("--baseline-bundle", type=Path, required=True)
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
    parser.add_argument("--allow-core-drift", action="store_true")
    parser.add_argument("--deep-validation", action="store_true")
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-markdown", type=Path, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        _require_absent(args.output_json)
        _require_absent(args.output_markdown)
        report = evaluate(args)
    except (
        CanonicalEvaluationError,
        COMPARATOR.ComparisonError,
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
                "routes": [route["name"] for route in report["routes"]],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
