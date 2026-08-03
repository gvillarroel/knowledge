#!/usr/bin/env python3
"""Evaluate Tika/MALLET/Tantivy on the frozen GraphRAG 40-question contract."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import time
from pathlib import Path
from types import ModuleType
from typing import Any, Mapping, Sequence


SCHEMA_VERSION = "semantic-okf-tika-mallet-tantivy-canonical-retrieval/1.0"
ROUTES = ("tantivy", "topic", "association", "fusion")
SCRIPT_PATH = Path(__file__).resolve()
EVALUATION_ROOT = SCRIPT_PATH.parents[1]
REPO_ROOT = SCRIPT_PATH.parents[3]
TIKA_MALLET_EVALUATOR_PATH = (
    REPO_ROOT
    / "evaluations"
    / "semantic-okf-tika-mallet"
    / "scripts"
    / "evaluate_canonical_retrieval.py"
)
DEFAULT_INVENTORY = (
    REPO_ROOT
    / "evaluations"
    / "semantic-okf-tika-mallet"
    / "canonical"
    / "graphrag-papers-40"
    / "source-inventory.json"
)
DEFAULT_QUESTIONS = (
    REPO_ROOT
    / "evaluations"
    / "semantic-okf-adaptive"
    / "retrieval-questions.jsonl"
)


class EvaluationError(RuntimeError):
    """Describe an incomplete, drifting, or invalid canonical evaluation."""


def _load_module(name: str, path: Path) -> ModuleType:
    specification = importlib.util.spec_from_file_location(name, path)
    if specification is None or specification.loader is None:
        raise EvaluationError(f"cannot load Python module from {path}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


TIKA_MALLET_EVALUATOR = _load_module(
    "semantic_okf_tika_mallet_tantivy_source_evaluator",
    TIKA_MALLET_EVALUATOR_PATH,
)
BASE = TIKA_MALLET_EVALUATOR.BASE


def _load_runtime(consult_script: Path) -> ModuleType:
    support = consult_script.parent / "_tika_mallet_tantivy_snapshot.py"
    if not support.is_file():
        raise EvaluationError(f"consultation support is missing: {support}")
    scripts = support.parent.resolve()
    sys.path.insert(0, str(scripts))
    try:
        return _load_module(
            "semantic_okf_tika_mallet_tantivy_canonical_runtime",
            support,
        )
    except (ImportError, OSError, RuntimeError, SyntaxError) as exc:
        raise EvaluationError(f"cannot load consultation runtime: {exc}") from exc
    finally:
        sys.path.remove(str(scripts))


def _hits(
    runtime: ModuleType,
    snapshot: Any,
    query: str,
    mode: str,
    top_k: int,
) -> list[Any]:
    natural_query = " ".join(BASE.TOKEN_RE.findall(query))
    if not natural_query:
        raise EvaluationError("canonical question has no searchable terms")
    try:
        payload = runtime.search_snapshot(snapshot, natural_query, mode, top_k)
    except Exception as exc:
        if isinstance(exc, (KeyboardInterrupt, SystemExit)):
            raise
        raise BASE.ComparisonError(
            f"Tika/MALLET/Tantivy {mode} search failed: {exc}"
        ) from exc
    normalized = dict(payload)
    normalized["results"] = [
        {**item, "chunk_id": item.get("document_id")}
        for item in payload.get("results", [])
    ]
    return BASE.parse_search_output(normalized, top_k)


def evaluate(args: argparse.Namespace) -> dict[str, Any]:
    """Evaluate every route after one deep validation of an immutable bundle."""

    if not 10 <= args.top_k <= 100:
        raise EvaluationError("--top-k must be from 10 through 100")
    for path, label in (
        (args.bundle, "bundle"),
        (args.consult_script, "consult script"),
        (args.questions, "questions"),
        (args.inventory, "source inventory"),
    ):
        if not path.resolve().exists():
            raise EvaluationError(f"{label} is missing: {path}")
    if args.deep_validation:
        for path, label in (
            (args.java, "Java executable"),
            (args.mallet_home, "MALLET home"),
        ):
            if path is None or not path.resolve().exists():
                raise EvaluationError(f"{label} is missing: {path}")

    source_verification = TIKA_MALLET_EVALUATOR._verify_source_inventory(
        args.inventory.resolve()
    )
    questions = BASE.load_questions(args.questions.resolve())
    if len(questions) != args.expected_question_count:
        raise EvaluationError(
            "evaluation requires "
            f"{args.expected_question_count} questions, found {len(questions)}"
        )
    if args.canonical_cohorts and len(questions) != 40:
        raise EvaluationError("--canonical-cohorts requires exactly 40 questions")

    bundle = args.bundle.resolve()
    before = TIKA_MALLET_EVALUATOR._tree_inventory(bundle)
    evaluation_started = time.perf_counter()
    runtime = _load_runtime(args.consult_script.resolve())
    ledger = BASE.AuthoritativeLedger.from_bundle(bundle)

    setup_started = time.perf_counter()
    try:
        snapshot = runtime.load_snapshot(
            bundle,
            deep_validation=args.deep_validation,
            java=args.java.resolve() if args.java is not None else None,
            mallet_home=(
                args.mallet_home.resolve() if args.mallet_home is not None else None
            ),
        )
    except Exception as exc:
        if isinstance(exc, (KeyboardInterrupt, SystemExit)):
            raise
        raise EvaluationError(f"deep snapshot validation failed: {exc}") from exc
    setup_ms = (time.perf_counter() - setup_started) * 1000.0

    inspection = runtime.inspect_snapshot(snapshot)
    engine = inspection.get("engine", {})
    if (
        inspection.get("status") != "pass"
        or (
            args.deep_validation
            and inspection.get("validation", {}).get("independent_rederivation")
            is not True
        )
        or engine.get("package_version") != "0.26.0"
        or engine.get("implementation") != "Rust"
    ):
        raise EvaluationError("combined runtime identity or deep validation drifted")

    routes: list[dict[str, Any]] = []
    for mode in ROUTES:
        route = BASE.evaluate_route(
            f"tika_mallet_tantivy_{mode}",
            bundle,
            ledger,
            questions,
            lambda query, selected=mode: _hits(
                runtime,
                snapshot,
                query,
                selected,
                args.top_k,
            ),
            continue_on_error=False,
        )
        if args.canonical_cohorts:
            TIKA_MALLET_EVALUATOR._attach_cohorts(route)
        if route["error_count"] != 0:
            raise EvaluationError(f"route {mode} produced query errors")
        if route["evidence_validity"]["ratio"] != 1.0:
            raise EvaluationError(f"route {mode} produced invalid evidence")
        route["setup_ms"] = setup_ms if mode == ROUTES[0] else 0.0
        route["timing_scope"] = (
            "One in-process search against one reused, deeply validated read-only "
            "Tika/MALLET snapshot with a pathless in-memory Tantivy index."
        )
        routes.append(route)

    after = TIKA_MALLET_EVALUATOR._tree_inventory(bundle)
    if before != after:
        raise EvaluationError("evaluation modified the immutable candidate bundle")

    selected = next(
        row
        for row in routes
        if row["name"] == "tika_mallet_tantivy_fusion"
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "pass",
        "dataset_id": args.dataset_id,
        "candidate_id": "tika-mallet-tantivy",
        "candidate_state": "experimental-comparator-not-registry-family",
        "ranking_eligible": True,
        "selected_route": "tika_mallet_tantivy_fusion",
        "selection_basis": (
            "ADR 0055 defined fusion as the reciprocal-rank combination of native "
            "Tantivy, MALLET topic, and PPMI association rankings before this run."
        ),
        "query_count": len(questions),
        "top_k": args.top_k,
        "deep_validation": args.deep_validation,
        "metric_contract": {
            "primary_identity": "paper_id",
            "duplicate_policy": "keep first rank per paper",
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
                "by persisted-unigram normalization; no qrel-aware expansion"
            ),
        },
        "timing_contract": {
            "unit": "milliseconds",
            "query_scope": (
                "one in-process search against one reused snapshot; the pathless "
                "Tantivy index is rebuilt per query by the frozen consultant"
            ),
            "setup_excluded_from_query_latency": True,
            "shared_deep_validation_ms": setup_ms,
            "evaluation_wall_ms": (
                time.perf_counter() - evaluation_started
            )
            * 1000.0,
            "cross_family_warning": (
                "P95 is an operational diagnostic because setup and runtime "
                "boundaries differ across families."
            ),
        },
        "source_verification": source_verification,
        "inputs": {
            "questions": BASE._file_fingerprint(args.questions.resolve()),
            "source_inventory": BASE._file_fingerprint(args.inventory.resolve()),
            "consult_script": BASE._file_fingerprint(args.consult_script.resolve()),
            "runtime_script": BASE._file_fingerprint(
                args.consult_script.resolve().parent
                / "_tika_mallet_tantivy_snapshot.py"
            ),
            "source_evaluator_script": BASE._file_fingerprint(
                TIKA_MALLET_EVALUATOR_PATH
            ),
            "evaluator_script": BASE._file_fingerprint(SCRIPT_PATH),
        },
        "runtime": inspection,
        "bundle": {
            "path": str(bundle),
            "file_count": len(before),
            "inventory_sha256": TIKA_MALLET_EVALUATOR._canonical_digest(before),
            "records": ledger.fingerprint(),
            "unchanged_after_evaluation": True,
        },
        "selected_metrics": {
            **(
                {
                    "all_40": selected["paper_metrics"],
                    "hard_10": selected["cohorts"]["hard_10"]["paper_metrics"],
                }
                if args.canonical_cohorts
                else {"all": selected["paper_metrics"]}
            ),
            "evidence_validity": selected["evidence_validity"],
            "timing_ms": selected["timing_ms"],
        },
        "routes": routes,
    }


def _percent(value: Any) -> str:
    return f"{100.0 * float(value):.2f}%"


def render_markdown(report: Mapping[str, Any]) -> str:
    """Render every route and the prospectively defined fusion result."""

    lines = [
        "# Tika/MALLET/Tantivy Canonical Direct-Retrieval Run",
        "",
        f"Status: **{report['status']}**. Dataset: `{report['dataset_id']}`. "
        f"Questions: {report['query_count']}. Returned pool: {report['top_k']}.",
        "",
    ]
    if "cohorts" in report["routes"][0]:
        lines.extend(
            [
                "| Route | Recall@10 | Hard Recall@10 | MRR@10 | nDCG@10 | "
                "Evidence valid | Mean ms | P95 ms |",
                "|---|---:|---:|---:|---:|---:|---:|---:|",
            ]
        )
    else:
        lines.extend(
            [
                "| Route | Recall@10 | MRR@10 | nDCG@10 | "
                "Evidence valid | Mean ms | P95 ms |",
                "|---|---:|---:|---:|---:|---:|---:|",
            ]
        )
    for route in report["routes"]:
        metrics = route["paper_metrics"]
        selected = " **(selected)**" if route["name"] == report["selected_route"] else ""
        row = (
            f"| `{route['name']}`{selected} | "
            f"{_percent(metrics['recall_at_10'])} | "
        )
        if "cohorts" in route:
            row += f"{_percent(route['cohorts']['hard_10']['paper_metrics']['recall_at_10'])} | "
        lines.append(
            row
            + f"{_percent(metrics['mrr_at_10'])} | "
            f"{_percent(metrics['ndcg_at_10'])} | "
            f"{_percent(route['evidence_validity']['ratio'])} | "
            f"{route['timing_ms']['mean']:.2f} | "
            f"{route['timing_ms']['p95']:.2f} |"
        )
    timing = report["timing_contract"]
    lines.extend(
        [
            "",
            "ADR 0055 defined `fusion` as the combination of native Tantivy, "
            "MALLET topic, and PPMI association rankings before this evaluation.",
            "",
            f"Snapshot validation took {timing['shared_deep_validation_ms']:.2f} ms. "
            f"The {report['bundle']['file_count']}-file bundle remained unchanged.",
            "",
            timing["cross_family_warning"],
            "",
        ]
    )
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--consult-script", type=Path, required=True)
    parser.add_argument("--java", type=Path)
    parser.add_argument("--mallet-home", type=Path)
    parser.add_argument(
        "--deep-validation",
        action=argparse.BooleanOptionalAction,
        default=True,
    )
    parser.add_argument("--questions", type=Path, default=DEFAULT_QUESTIONS)
    parser.add_argument("--inventory", type=Path, default=DEFAULT_INVENTORY)
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
    args = build_parser().parse_args(argv)
    if any(
        path.exists() or path.is_symlink()
        for path in (args.output_json, args.output_markdown)
    ):
        print(json.dumps({"status": "error", "error": "output already exists"}))
        return 2
    try:
        report = evaluate(args)
    except (
        EvaluationError,
        BASE.ComparisonError,
        OSError,
        UnicodeError,
        ValueError,
        TypeError,
        KeyError,
    ) as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, sort_keys=True))
        return 2

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_markdown.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(
        json.dumps(
            report,
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
        render_markdown(report),
        encoding="utf-8",
        newline="\n",
    )
    print(
        json.dumps(
            {
                "status": report["status"],
                "selected_route": report["selected_route"],
                "top_k": report["top_k"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
