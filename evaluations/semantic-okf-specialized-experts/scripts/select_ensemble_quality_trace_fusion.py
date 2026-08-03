#!/usr/bin/env python3
"""Select one global quality/trace fusion on a frozen development prefix."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from types import ModuleType
from typing import Any, Mapping, Sequence


sys.dont_write_bytecode = True
SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[3]
BASE_PATH = (
    REPO_ROOT
    / "evaluations"
    / "semantic-okf-embeddings"
    / "scripts"
    / "compare_retrieval.py"
)
DEFAULT_QUESTIONS = (
    REPO_ROOT
    / "evaluations"
    / "semantic-okf-adaptive"
    / "retrieval-questions.jsonl"
)
SCHEMA_VERSION = "semantic-okf-ensemble-quality-trace-selection/1.1"
DEVELOPMENT_COUNT = 24
TRACE_CANDIDATE_BUDGET = 10
RRF_K_VALUES = (0, 1, 3, 5, 7, 10, 20, 40, 60)
WEIGHT_VALUES = tuple(range(1, 11))
SCOPES = ("protected", "union")


class SelectionError(ValueError):
    """Describe invalid or incomplete selection evidence."""


def _load_module(name: str, path: Path) -> ModuleType:
    specification = importlib.util.spec_from_file_location(name, path)
    if specification is None or specification.loader is None:
        raise SelectionError(f"Cannot load Python module from {path}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


BASE = _load_module("ensemble_quality_trace_selection_base", BASE_PATH)


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _canonical_sha256(value: Any) -> str:
    encoded = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _load_json(path: Path, *, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise SelectionError(f"Cannot read {label}: {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise SelectionError(f"{label} must be a JSON object")
    return value


def _quality_rankings(
    report: Mapping[str, Any],
    development_ids: set[str],
) -> dict[str, list[str]]:
    routes = report.get("routes")
    if not isinstance(routes, list) or len(routes) != 1:
        raise SelectionError("Quality report must contain exactly one route")
    queries = routes[0].get("queries")
    if not isinstance(queries, list):
        raise SelectionError("Quality report route lacks queries")
    rankings: dict[str, list[str]] = {}
    for row in queries:
        if not isinstance(row, dict):
            raise SelectionError("Quality report contains a non-object query")
        identifier = row.get("question_id")
        if identifier not in development_ids:
            continue
        paper_ids = row.get("paper_ids")
        if (
            not isinstance(paper_ids, list)
            or len(paper_ids) != 10
            or not all(isinstance(item, str) for item in paper_ids)
            or len(set(paper_ids)) != len(paper_ids)
        ):
            raise SelectionError(f"Invalid quality ranking for {identifier}")
        rankings[str(identifier)] = list(paper_ids)
    if set(rankings) != development_ids:
        raise SelectionError("Quality report lacks the complete development prefix")
    return rankings


def _trace_rankings(
    trace_runtime: ModuleType,
    knowledge: Path,
    questions: Sequence[Any],
) -> dict[str, list[str]]:
    trace_runtime.KNOWLEDGE_ROOT = knowledge
    trace_runtime.LEDGER_PATH = knowledge / "semantic" / "records.jsonl"
    rankings: dict[str, list[str]] = {}
    for question in questions:
        rows = trace_runtime.search(
            question.question,
            source_id=None,
            concept_type=None,
            limit=1000,
            show_content=False,
        )
        paper_ids: list[str] = []
        for row in rows:
            paper_id = BASE._paper_id_from_mapping(row)
            if paper_id is not None and paper_id not in paper_ids:
                paper_ids.append(paper_id)
        if len(paper_ids) < 10:
            raise SelectionError(
                f"Trace route returned fewer than ten papers for {question.identifier}"
            )
        rankings[question.identifier] = paper_ids
    return rankings


def _candidate_ranking(
    quality: Sequence[str],
    trace: Sequence[str],
    *,
    scope: str,
    rrf_k: int,
    quality_weight: int,
    trace_weight: int,
) -> list[str]:
    trace_candidates = list(trace[:TRACE_CANDIDATE_BUDGET])
    candidates = (
        list(quality)
        if scope == "protected"
        else list(dict.fromkeys([*quality, *trace_candidates]))
    )
    quality_ranks = {
        paper_id: rank
        for rank, paper_id in enumerate(quality, start=1)
    }
    trace_ranks = {
        paper_id: rank
        for rank, paper_id in enumerate(trace_candidates, start=1)
    }
    scores = {
        paper_id: (
            (
                quality_weight / (rrf_k + quality_ranks[paper_id])
                if paper_id in quality_ranks
                else 0.0
            )
            + (
                trace_weight / (rrf_k + trace_ranks[paper_id])
                if paper_id in trace_ranks
                else 0.0
            )
        )
        for paper_id in candidates
    }
    return sorted(
        candidates,
        key=lambda paper_id: (
            -scores[paper_id],
            quality_ranks.get(paper_id, 1001),
            trace_ranks.get(paper_id, 1001),
            paper_id,
        ),
    )[:10]


def _aggregate_metrics(
    questions: Sequence[Any],
    rankings: Mapping[str, Sequence[str]],
) -> dict[str, float]:
    rows = [
        BASE.evaluate_ranking(
            list(rankings[question.identifier]),
            set(question.paper_ids),
        )
        for question in questions
    ]
    return {
        key: sum(float(row[key]) for row in rows) / len(rows)
        for key in ("recall_at_10", "mrr_at_10", "ndcg_at_10")
    }


def select(args: argparse.Namespace) -> dict[str, Any]:
    """Run the closed global-parameter search on q001-q024 only."""

    quality_report_path = args.quality_report.resolve()
    knowledge = args.knowledge.resolve()
    questions_path = args.questions.resolve()
    trace_helper = args.trace_helper.resolve()
    for path, label in (
        (quality_report_path, "quality report"),
        (knowledge, "knowledge"),
        (questions_path, "questions"),
        (trace_helper, "trace helper"),
    ):
        if not path.exists():
            raise SelectionError(f"{label} is absent: {path}")

    questions = BASE.load_questions(questions_path)
    if len(questions) != 40:
        raise SelectionError("Selection requires the canonical forty questions")
    development = questions[:DEVELOPMENT_COUNT]
    expected_ids = [f"q{index:03d}" for index in range(1, DEVELOPMENT_COUNT + 1)]
    actual_ids = [question.identifier.split("-", 1)[0] for question in development]
    if actual_ids != expected_ids:
        raise SelectionError("Development scope is not the q001-q024 prefix")
    development_ids = {question.identifier for question in development}

    quality_report = _load_json(quality_report_path, label="quality report")
    if quality_report.get("status") != "pass" or quality_report.get("top_k") != 10:
        raise SelectionError("Quality report must be a passing Top-10 run")
    quality = _quality_rankings(quality_report, development_ids)
    trace_runtime = _load_module(
        "ensemble_quality_trace_selection_runtime",
        trace_helper,
    )
    trace = _trace_rankings(trace_runtime, knowledge, development)
    baseline_metrics = _aggregate_metrics(development, quality)

    candidates: list[dict[str, Any]] = []
    for scope in SCOPES:
        for rrf_k in RRF_K_VALUES:
            for quality_weight in WEIGHT_VALUES:
                for trace_weight in WEIGHT_VALUES:
                    rankings = {
                        question.identifier: _candidate_ranking(
                            quality[question.identifier],
                            trace[question.identifier],
                            scope=scope,
                            rrf_k=rrf_k,
                            quality_weight=quality_weight,
                            trace_weight=trace_weight,
                        )
                        for question in development
                    }
                    candidates.append(
                        {
                            "scope": scope,
                            "rrf_k": rrf_k,
                            "quality_weight": quality_weight,
                            "trace_weight": trace_weight,
                            "metrics": _aggregate_metrics(development, rankings),
                            "ranking_sha256": _canonical_sha256(rankings),
                        }
                    )
    selected = sorted(
        candidates,
        key=lambda row: (
            -row["metrics"]["ndcg_at_10"],
            -row["metrics"]["recall_at_10"],
            -row["metrics"]["mrr_at_10"],
            row["rrf_k"],
            row["quality_weight"] + row["trace_weight"],
            row["quality_weight"],
            row["trace_weight"],
            row["scope"],
        ),
    )[0]
    result: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "status": "pass",
        "selection_role": "retrospective-development-only",
        "development_scope": {
            "dataset_id": "graphrag-papers-40",
            "question_ids": [
                question.identifier
                for question in development
            ],
            "question_count": len(development),
            "final_evaluation_opened": False,
            "holdout_available": False,
        },
        "inputs": {
            "quality_report_sha256": _sha256_file(quality_report_path),
            "questions_sha256": _sha256_file(questions_path),
            "trace_helper_sha256": _sha256_file(trace_helper),
            "knowledge_tree_sha256": quality_report["expert"][
                "knowledge_tree_sha256"
            ],
        },
        "search": {
            "trace_candidate_budget": TRACE_CANDIDATE_BUDGET,
            "scopes": list(SCOPES),
            "rrf_k_values": list(RRF_K_VALUES),
            "quality_weight_values": list(WEIGHT_VALUES),
            "trace_weight_values": list(WEIGHT_VALUES),
            "candidate_count": len(candidates),
            "ranking": [
                "ndcg_at_10_desc",
                "recall_at_10_desc",
                "mrr_at_10_desc",
                "rrf_k_asc",
                "weight_sum_asc",
                "quality_weight_asc",
                "trace_weight_asc",
                "scope_asc",
            ],
        },
        "baseline_metrics": baseline_metrics,
        "selected": selected,
    }
    result["seal_sha256"] = _canonical_sha256(result)
    return result


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--quality-report", type=Path, required=True)
    parser.add_argument("--knowledge", type=Path, required=True)
    parser.add_argument("--questions", type=Path, default=DEFAULT_QUESTIONS)
    parser.add_argument("--trace-helper", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Select and write one append-only development result."""

    args = build_parser().parse_args(argv)
    if args.output.exists() or args.output.is_symlink():
        print(json.dumps({"status": "error", "error": "output already exists"}))
        return 2
    try:
        result = select(args)
    except (
        SelectionError,
        BASE.ComparisonError,
        OSError,
        UnicodeError,
        ValueError,
        TypeError,
        KeyError,
    ) as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, sort_keys=True))
        return 2
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(
            result,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
            allow_nan=False,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        json.dumps(
            {
                "status": result["status"],
                "selected": result["selected"],
                "seal_sha256": result["seal_sha256"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
