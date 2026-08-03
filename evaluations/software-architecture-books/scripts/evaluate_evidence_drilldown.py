#!/usr/bin/env python3
"""Evaluate source-filtered page drill-down after first-stage fusion retrieval."""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
from pathlib import Path
import statistics
import sys
import time
from types import ModuleType
from typing import Any, Mapping, Sequence


sys.dont_write_bytecode = True
SCRIPT_PATH = Path(__file__).resolve()
STUDY_ROOT = SCRIPT_PATH.parents[1]
REPO_ROOT = SCRIPT_PATH.parents[3]
DATASET_ID = "software-architecture-books-40"
SCHEMA_VERSION = "software-architecture-books-evidence-drilldown/1.0"
DEFAULT_BUNDLE = STUDY_ROOT / "processed" / "bundle"
DEFAULT_DIRECT = STUDY_ROOT / "reports" / "direct-retrieval-evaluation.json"
DEFAULT_QUESTIONS = STUDY_ROOT / "benchmark" / "retrieval-questions.jsonl"
DEFAULT_TRUTH = STUDY_ROOT / "benchmark" / "hard-ground-truth.jsonl"
DEFAULT_JSON = STUDY_ROOT / "reports" / "evidence-drilldown-evaluation.json"
DEFAULT_MARKDOWN = STUDY_ROOT / "reports" / "evidence-drilldown-evaluation.md"
BASE_EVALUATOR = STUDY_ROOT / "scripts" / "evaluate_retrieval.py"
CUTOFFS = (1, 3, 5, 10)


class DrilldownError(RuntimeError):
    """Raised when the first-stage report or drill-down result is invalid."""


def load_module(name: str, path: Path) -> ModuleType:
    """Load the frozen direct evaluator and its read-only classical runtime."""

    specification = importlib.util.spec_from_file_location(name, path)
    if specification is None or specification.loader is None:
        raise DrilldownError(f"Cannot load evaluator from {path}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


BASE = load_module("software_books_direct_evaluator_for_drilldown", BASE_EVALUATOR)


def load_json(path: Path, label: str) -> dict[str, Any]:
    """Load one JSON object."""

    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise DrilldownError(f"{label} must be a JSON object")
    return value


def first_stage_questions(
    report: Mapping[str, Any],
) -> dict[str, dict[str, Any]]:
    """Index the accepted fusion results by full question ID."""

    if (
        report.get("schema_version")
        != "software-architecture-books-retrieval-evaluation/1.0"
        or report.get("status") != "pass"
        or report.get("dataset_id") != DATASET_ID
        or report.get("top_k") != 10
        or report.get("snapshot", {}).get("deep_validation") is not True
    ):
        raise DrilldownError("Direct retrieval report is incompatible")
    modes = report.get("modes")
    if not isinstance(modes, list):
        raise DrilldownError("Direct retrieval report has no modes")
    fusion = next(
        (
            row
            for row in modes
            if isinstance(row, dict) and row.get("mode") == "fusion"
        ),
        None,
    )
    if not isinstance(fusion, dict):
        raise DrilldownError("Direct retrieval report has no fusion route")
    rows = fusion.get("questions")
    if not isinstance(rows, list):
        raise DrilldownError("Fusion route has no questions")
    result = {
        str(row["question_id"]): row
        for row in rows
        if isinstance(row, dict) and row.get("cohort") == "hard"
    }
    if len(result) != 10:
        raise DrilldownError("Fusion route does not cover ten hard questions")
    return result


def evidence_score(
    pages: Sequence[Mapping[str, Any]],
    reviewed: Sequence[Mapping[str, Any]],
) -> tuple[float, float, int]:
    """Return exact reviewed-page recall, full coverage, and match count."""

    returned = {
        (row.get("source_id"), row.get("text_sha256"))
        for row in pages
    }
    expected = {
        (row["source_id"], row["text_sha256"])
        for row in reviewed
    }
    matches = returned & expected
    return (
        len(matches) / len(expected),
        float(matches == expected),
        len(matches),
    )


def percentile_95(values: Sequence[float]) -> float:
    """Return the nearest-rank P95."""

    if not values:
        raise DrilldownError("Latency sample is empty")
    ordered = sorted(values)
    return ordered[max(0, math.ceil(0.95 * len(ordered)) - 1)]


def evaluate(
    bundle: Path,
    direct_path: Path,
    questions_path: Path,
    truth_path: Path,
) -> dict[str, Any]:
    """Run source-filtered BM25 page retrieval for the hard cohort."""

    direct = load_json(direct_path, "direct retrieval report")
    first_stage = first_stage_questions(direct)
    questions = {
        row["id"]: row
        for row in BASE.load_questions(questions_path)
        if row["question_type"] == "hard"
    }
    truth = BASE.load_hard_truth(truth_path, set(questions))
    try:
        snapshot = BASE.CLASSICAL.load_snapshot(bundle, deep_validation=False)
    except Exception as exc:
        raise DrilldownError(f"Classical snapshot validation failed: {exc}") from exc
    if (
        snapshot.index_sha256
        != direct["snapshot"]["classical_index_sha256"]
        or snapshot.index["core"]["tree_sha256"]
        != direct["snapshot"]["core_tree_sha256"]
    ):
        raise DrilldownError("Direct report and live snapshot hashes disagree")

    per_question: list[dict[str, Any]] = []
    aggregate_recalls: dict[int, list[float]] = {cutoff: [] for cutoff in CUTOFFS}
    aggregate_full: dict[int, list[float]] = {cutoff: [] for cutoff in CUTOFFS}
    aggregate_any: dict[int, list[float]] = {cutoff: [] for cutoff in CUTOFFS}
    aggregate_matches: dict[int, int] = {cutoff: 0 for cutoff in CUTOFFS}
    aggregate_expected = 0
    aggregate_pages: dict[int, list[int]] = {cutoff: [] for cutoff in CUTOFFS}
    latencies: list[float] = []
    baseline_recalls: list[float] = []
    baseline_full: list[float] = []
    baseline_any: list[float] = []
    baseline_matches = 0
    baseline_page_counts: list[int] = []
    source_recalls: list[float] = []

    for identifier, question in questions.items():
        first = first_stage[identifier]
        first_results = first.get("results")
        if not isinstance(first_results, list):
            raise DrilldownError(f"{identifier}: invalid first-stage results")
        candidate_sources: list[str] = []
        for row in first_results:
            source_id = row.get("source_id") if isinstance(row, Mapping) else None
            if isinstance(source_id, str) and source_id not in candidate_sources:
                candidate_sources.append(source_id)
        relevant_sources = set(question["source_ids"])
        source_recall = len(relevant_sources & set(candidate_sources)) / len(
            relevant_sources
        )
        source_recalls.append(source_recall)

        baseline_recall, baseline_complete, baseline_count = evidence_score(
            first_results,
            truth[identifier],
        )
        baseline_recalls.append(baseline_recall)
        baseline_full.append(baseline_complete)
        baseline_any.append(float(baseline_count > 0))
        baseline_matches += baseline_count
        baseline_page_counts.append(len(first_results))

        pages_by_source: dict[str, list[dict[str, Any]]] = {}
        started = time.perf_counter()
        for source_id in candidate_sources:
            try:
                result = BASE.CLASSICAL.search_snapshot(
                    snapshot,
                    question["question"],
                    "bm25",
                    max(CUTOFFS),
                    source_ids=[source_id],
                )
            except Exception as exc:
                raise DrilldownError(
                    f"{identifier}/{source_id}: filtered search failed: {exc}"
                ) from exc
            if (
                result.get("status") != "pass"
                or result.get("requested_mode") != "bm25"
                or result.get("effective_mode") != "bm25"
                or result.get("filters", {}).get("source_ids") != [source_id]
            ):
                raise DrilldownError(
                    f"{identifier}/{source_id}: filtered route contract drift"
                )
            rows = result.get("results")
            if not isinstance(rows, list):
                raise DrilldownError(
                    f"{identifier}/{source_id}: invalid filtered results"
                )
            pages_by_source[source_id] = [BASE.safe_result(row) for row in rows]
        elapsed_ms = (time.perf_counter() - started) * 1000.0
        latencies.append(elapsed_ms)

        cutoff_rows: dict[str, Any] = {}
        for cutoff in CUTOFFS:
            pages = [
                page
                for source_id in candidate_sources
                for page in pages_by_source[source_id][:cutoff]
            ]
            recall, complete, matches = evidence_score(
                pages,
                truth[identifier],
            )
            aggregate_recalls[cutoff].append(recall)
            aggregate_full[cutoff].append(complete)
            aggregate_any[cutoff].append(float(matches > 0))
            aggregate_matches[cutoff] += matches
            aggregate_pages[cutoff].append(len(pages))
            cutoff_rows[str(cutoff)] = {
                "pages_opened": len(pages),
                "reviewed_locator_recall": round(recall, 6),
                "full_reviewed_locator_coverage": complete,
                "matched_reviewed_locators": matches,
            }
        aggregate_expected += len(truth[identifier])
        per_question.append(
            {
                "question_id": identifier,
                "first_stage_source_count": len(candidate_sources),
                "first_stage_source_recall": round(source_recall, 6),
                "baseline_reviewed_locator_recall": round(
                    baseline_recall,
                    6,
                ),
                "drilldown_latency_ms": round(elapsed_ms, 3),
                "cutoffs": cutoff_rows,
                "pages_by_source": pages_by_source,
            }
        )

    summary: list[dict[str, Any]] = [
        {
            "route": "single-pass-fusion",
            "pages_per_selected_source": None,
            "mean_source_recall": round(statistics.fmean(source_recalls), 6),
            "mean_reviewed_locator_recall": round(
                statistics.fmean(baseline_recalls),
                6,
            ),
            "micro_reviewed_locator_recall": round(
                baseline_matches / aggregate_expected,
                6,
            ),
            "full_reviewed_locator_coverage": round(
                statistics.fmean(baseline_full),
                6,
            ),
            "any_reviewed_locator_coverage": round(
                statistics.fmean(baseline_any),
                6,
            ),
            "average_pages_opened": round(
                statistics.fmean(baseline_page_counts),
                3,
            ),
        }
    ]
    for cutoff in CUTOFFS:
        summary.append(
            {
                "route": "fusion-source-selection-plus-filtered-bm25",
                "pages_per_selected_source": cutoff,
                "mean_source_recall": round(statistics.fmean(source_recalls), 6),
                "mean_reviewed_locator_recall": round(
                    statistics.fmean(aggregate_recalls[cutoff]),
                    6,
                ),
                "micro_reviewed_locator_recall": round(
                    aggregate_matches[cutoff] / aggregate_expected,
                    6,
                ),
                "full_reviewed_locator_coverage": round(
                    statistics.fmean(aggregate_full[cutoff]),
                    6,
                ),
                "any_reviewed_locator_coverage": round(
                    statistics.fmean(aggregate_any[cutoff]),
                    6,
                ),
                "average_pages_opened": round(
                    statistics.fmean(aggregate_pages[cutoff]),
                    3,
                ),
            }
        )
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "pass",
        "dataset_id": DATASET_ID,
        "evaluation_kind": "unsupervised-two-stage-evidence-drilldown",
        "answer_quality_evaluated": False,
        "hard_question_count": len(questions),
        "reviewed_locator_binding_count": aggregate_expected,
        "first_stage": {
            "route": "fusion",
            "top_k": 10,
            "source_selection_uses_qrels": False,
            "direct_report_sha256": BASE.sha256_file(direct_path),
        },
        "second_stage": {
            "route": "bm25",
            "filter": "each-distinct-first-stage-source-id",
            "page_cutoffs": list(CUTOFFS),
            "qrels_or_ground_truth_used_for_ranking": False,
        },
        "snapshot": {
            "classical_index_sha256": snapshot.index_sha256,
            "core_tree_sha256": snapshot.index["core"]["tree_sha256"],
            "prior_deep_validation_bound": True,
        },
        "summary": summary,
        "latency_ms": {
            "median_per_hard_question": round(statistics.median(latencies), 3),
            "p95_per_hard_question": round(percentile_95(latencies), 3),
        },
        "questions": per_question,
    }


def render_markdown(report: Mapping[str, Any]) -> str:
    """Render a concise metric-only comparison."""

    rows = [
        "# Evidence Drill-Down Evaluation",
        "",
        (
            "Fusion first selects up to ten distinct books without qrel access. "
            "BM25 then retrieves a bounded number of pages inside each selected "
            "book. This is an exact-page diagnostic, not answer-quality scoring."
        ),
        "",
        "| Route | Pages per selected book | Source recall | Mean locator recall | Micro locator recall | Any locator coverage | Full locator coverage | Average pages opened |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in report["summary"]:
        cutoff = row["pages_per_selected_source"]
        rows.append(
            "| {route} | {cutoff} | {source:.3f} | {mean:.3f} | {micro:.3f} "
            "| {any:.3f} | {full:.3f} | {pages:.1f} |".format(
                route=row["route"],
                cutoff="—" if cutoff is None else cutoff,
                source=row["mean_source_recall"],
                mean=row["mean_reviewed_locator_recall"],
                micro=row["micro_reviewed_locator_recall"],
                any=row["any_reviewed_locator_coverage"],
                full=row["full_reviewed_locator_coverage"],
                pages=row["average_pages_opened"],
            )
        )
    rows.extend(
        [
            "",
            (
                "The machine-readable companion preserves only source identities, "
                "locators, and hashes; private passage text is excluded."
            ),
            "",
        ]
    )
    return "\n".join(rows)


def build_parser() -> argparse.ArgumentParser:
    """Build the drill-down evaluation command line."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, default=DEFAULT_BUNDLE)
    parser.add_argument("--direct-report", type=Path, default=DEFAULT_DIRECT)
    parser.add_argument("--questions", type=Path, default=DEFAULT_QUESTIONS)
    parser.add_argument("--hard-truth", type=Path, default=DEFAULT_TRUTH)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--output-markdown", type=Path, default=DEFAULT_MARKDOWN)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the bounded source-filtered evidence drill-down."""

    args = build_parser().parse_args(argv)
    try:
        report = evaluate(
            args.bundle.resolve(),
            args.direct_report.resolve(),
            args.questions.resolve(),
            args.hard_truth.resolve(),
        )
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
    except (
        DrilldownError,
        OSError,
        UnicodeError,
        json.JSONDecodeError,
        KeyError,
        TypeError,
        ValueError,
    ) as exc:
        print(
            json.dumps(
                {"status": "error", "error": str(exc)},
                ensure_ascii=False,
                sort_keys=True,
            )
        )
        return 2
    best = max(
        report["summary"],
        key=lambda row: (
            row["mean_reviewed_locator_recall"],
            row["full_reviewed_locator_coverage"],
        ),
    )
    print(
        json.dumps(
            {
                "status": "pass",
                "dataset_id": DATASET_ID,
                "best_pages_per_selected_source": best[
                    "pages_per_selected_source"
                ],
                "best_mean_reviewed_locator_recall": best[
                    "mean_reviewed_locator_recall"
                ],
                "output_json": BASE.portable_path(args.output_json),
                "output_markdown": BASE.portable_path(args.output_markdown),
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
