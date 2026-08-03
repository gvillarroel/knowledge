#!/usr/bin/env python3
"""Evaluate four frozen classical retrieval routes on the 40-question corpus."""

from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
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
SCHEMA_VERSION = "software-architecture-books-retrieval-evaluation/1.0"
MODES = ("bm25", "topic", "association", "fusion")
DEFAULT_BUNDLE = STUDY_ROOT / "processed" / "bundle"
DEFAULT_QUESTIONS = STUDY_ROOT / "benchmark" / "retrieval-questions.jsonl"
DEFAULT_HARD_TRUTH = STUDY_ROOT / "benchmark" / "hard-ground-truth.jsonl"
DEFAULT_JSON = STUDY_ROOT / "reports" / "direct-retrieval-evaluation.json"
DEFAULT_MARKDOWN = STUDY_ROOT / "reports" / "direct-retrieval-evaluation.md"
CLASSICAL_HELPER = (
    REPO_ROOT
    / "skills"
    / "consult-semantic-okf-classical"
    / "scripts"
    / "_classical_snapshot.py"
)


class EvaluationError(RuntimeError):
    """Raised when an input, snapshot, ranking, or metric is invalid."""


def load_module(name: str, path: Path) -> ModuleType:
    """Load one pinned helper without modifying its package directory."""

    specification = importlib.util.spec_from_file_location(name, path)
    if specification is None or specification.loader is None:
        raise EvaluationError(f"Cannot load classical helper from {path}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


CLASSICAL = load_module("software_books_classical_snapshot", CLASSICAL_HELPER)


def sha256_file(path: Path) -> str:
    """Return a streaming SHA-256 for one file."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def portable_path(path: Path) -> str:
    """Render repository paths portably while allowing explicit external inputs."""

    resolved = path.resolve()
    try:
        return resolved.relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return str(resolved)


def fingerprint(path: Path) -> dict[str, Any]:
    """Describe one immutable evaluation input."""

    return {
        "path": portable_path(path),
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def load_jsonl(path: Path, label: str) -> list[dict[str, Any]]:
    """Load a nonblank JSON-object sequence."""

    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(),
        start=1,
    ):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise EvaluationError(
                f"{label} line {line_number} is invalid JSON: {exc}"
            ) from exc
        if not isinstance(row, dict):
            raise EvaluationError(f"{label} line {line_number} is not an object")
        rows.append(row)
    return rows


def load_questions(path: Path) -> list[dict[str, Any]]:
    """Validate the frozen 30-development/10-hard question contract."""

    rows = load_jsonl(path, "questions")
    if len(rows) != 40:
        raise EvaluationError(f"Expected 40 questions, found {len(rows)}")
    identifiers: list[str] = []
    normalized: list[dict[str, Any]] = []
    for index, row in enumerate(rows, start=1):
        identifier = row.get("id")
        question = row.get("question")
        question_type = row.get("question_type")
        qrels = row.get("qrels")
        expected_prefix = f"q{index:03d}-"
        if (
            not isinstance(identifier, str)
            or not identifier.startswith(expected_prefix)
            or not isinstance(question, str)
            or not question.strip()
            or question_type
            != ("hard" if index >= 31 else "cross-document")
            or not isinstance(qrels, dict)
        ):
            raise EvaluationError(f"Question {index} has an invalid contract")
        document_ids = qrels.get("document_ids")
        source_ids = qrels.get("source_ids")
        if (
            not isinstance(document_ids, list)
            or not document_ids
            or document_ids != sorted(set(document_ids))
            or not all(isinstance(item, str) and item for item in document_ids)
            or not isinstance(source_ids, list)
            or not source_ids
            or source_ids != sorted(set(source_ids))
            or not all(isinstance(item, str) and item for item in source_ids)
            or len(document_ids) != len(source_ids)
            or any(
                source_id != f"book-{document_id}"
                for document_id, source_id in zip(
                    document_ids,
                    source_ids,
                    strict=True,
                )
            )
        ):
            raise EvaluationError(f"{identifier}: invalid qrels")
        identifiers.append(identifier)
        normalized.append(
            {
                "id": identifier,
                "question": question.strip(),
                "question_type": question_type,
                "document_ids": document_ids,
                "source_ids": source_ids,
            }
        )
    if len(identifiers) != len(set(identifiers)):
        raise EvaluationError("Question identifiers are not unique")
    return normalized


def load_hard_truth(
    path: Path,
    hard_ids: set[str],
) -> dict[str, list[dict[str, Any]]]:
    """Load exact reviewed locator identities without loading copyrighted excerpts."""

    rows = load_jsonl(path, "hard ground truth")
    if len(rows) != 10:
        raise EvaluationError(f"Expected 10 hard-ground-truth rows, found {len(rows)}")
    result: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        identifier = row.get("id")
        evidence = row.get("authoritative_evidence")
        if (
            not isinstance(identifier, str)
            or identifier not in hard_ids
            or identifier in result
            or not isinstance(evidence, list)
            or not evidence
        ):
            raise EvaluationError("Hard-ground-truth identity or evidence is invalid")
        normalized: list[dict[str, Any]] = []
        for item in evidence:
            if not isinstance(item, dict):
                raise EvaluationError(f"{identifier}: evidence row is not an object")
            source_id = item.get("source_id")
            document_id = item.get("document_id")
            page_number = item.get("page_number")
            text_sha256 = item.get("text_sha256")
            interpretation = item.get("interpretation")
            if (
                not isinstance(source_id, str)
                or not isinstance(document_id, str)
                or source_id != f"book-{document_id}"
                or not isinstance(page_number, int)
                or page_number <= 0
                or not isinstance(text_sha256, str)
                or len(text_sha256) != 64
                or any(character not in "0123456789abcdef" for character in text_sha256)
                or not isinstance(interpretation, str)
                or not interpretation.strip()
            ):
                raise EvaluationError(f"{identifier}: invalid reviewed evidence")
            normalized.append(
                {
                    "source_id": source_id,
                    "document_id": document_id,
                    "page_number": page_number,
                    "text_sha256": text_sha256,
                }
            )
        result[identifier] = normalized
    if set(result) != hard_ids:
        raise EvaluationError("Hard-ground-truth rows do not cover the hard cohort")
    return result


def first_source_ranks(
    results: Sequence[Mapping[str, Any]],
) -> dict[str, int]:
    """Map every returned source to its first page rank."""

    ranks: dict[str, int] = {}
    for row in results:
        source_id = row.get("source_id")
        rank = row.get("rank")
        if (
            not isinstance(source_id, str)
            or not isinstance(rank, int)
            or rank <= 0
        ):
            raise EvaluationError("Search result has an invalid source rank")
        ranks.setdefault(source_id, rank)
    return ranks


def retrieval_metrics(
    results: Sequence[Mapping[str, Any]],
    relevant_sources: Sequence[str],
    top_k: int,
) -> dict[str, float]:
    """Compute duplicate-safe document-level metrics for one question."""

    relevant = set(relevant_sources)
    ranks = first_source_ranks(results)
    relevant_ranks = sorted(
        rank
        for source_id, rank in ranks.items()
        if source_id in relevant and rank <= top_k
    )
    recall = len(relevant_ranks) / len(relevant)
    reciprocal_rank = 1.0 / relevant_ranks[0] if relevant_ranks else 0.0
    dcg = sum(1.0 / math.log2(rank + 1) for rank in relevant_ranks)
    ideal = sum(
        1.0 / math.log2(rank + 1)
        for rank in range(1, min(len(relevant), top_k) + 1)
    )
    unique_returned = {
        source_id for source_id, rank in ranks.items() if rank <= top_k
    }
    precision = (
        len(unique_returned & relevant) / len(unique_returned)
        if unique_returned
        else 0.0
    )
    return {
        f"recall@{top_k}": recall,
        f"mrr@{top_k}": reciprocal_rank,
        f"ndcg@{top_k}": dcg / ideal if ideal else 0.0,
        f"source_precision@{top_k}": precision,
        f"full_qrel_coverage@{top_k}": float(len(relevant_ranks) == len(relevant)),
    }


def exact_evidence_metrics(
    results: Sequence[Mapping[str, Any]],
    reviewed: Sequence[Mapping[str, Any]],
    top_k: int,
) -> dict[str, float]:
    """Measure recall of exact reviewed page identities for one hard question."""

    returned = {
        (row.get("source_id"), row.get("text_sha256"))
        for row in results
        if isinstance(row.get("rank"), int) and row["rank"] <= top_k
    }
    expected = {
        (row["source_id"], row["text_sha256"])
        for row in reviewed
    }
    found = returned & expected
    return {
        f"reviewed_locator_recall@{top_k}": len(found) / len(expected),
        f"full_reviewed_locator_coverage@{top_k}": float(found == expected),
    }


def percentile_95(values: Sequence[float]) -> float:
    """Return a nearest-rank P95 for a nonempty latency sample."""

    if not values:
        raise EvaluationError("Cannot compute latency from an empty sample")
    ordered = sorted(values)
    index = max(0, math.ceil(0.95 * len(ordered)) - 1)
    return ordered[index]


def safe_result(row: Mapping[str, Any]) -> dict[str, Any]:
    """Retain rank and evidence identity while excluding private passage text."""

    return {
        key: row.get(key)
        for key in (
            "rank",
            "document_id",
            "source_id",
            "record_id",
            "record_sha256",
            "concept_id",
            "concept_path",
            "source_path",
            "ordinal",
            "locator",
            "text_sha256",
        )
    }


def evaluate(
    bundle: Path,
    questions_path: Path,
    hard_truth_path: Path,
    top_k: int,
) -> dict[str, Any]:
    """Deep-validate once and evaluate every route on every frozen question."""

    questions = load_questions(questions_path)
    hard_ids = {
        row["id"] for row in questions if row["question_type"] == "hard"
    }
    hard_truth = load_hard_truth(hard_truth_path, hard_ids)
    try:
        snapshot = CLASSICAL.load_snapshot(bundle, deep_validation=True)
    except Exception as exc:
        raise EvaluationError(f"Classical deep validation failed: {exc}") from exc

    mode_reports: list[dict[str, Any]] = []
    for mode in MODES:
        per_question: list[dict[str, Any]] = []
        latencies: list[float] = []
        metric_values: defaultdict[str, list[float]] = defaultdict(list)
        for question in questions:
            started = time.perf_counter()
            try:
                result = CLASSICAL.search_snapshot(
                    snapshot,
                    question["question"],
                    mode,
                    top_k,
                )
            except Exception as exc:
                raise EvaluationError(
                    f"{mode}/{question['id']} search failed: {exc}"
                ) from exc
            latency_ms = (time.perf_counter() - started) * 1000.0
            latencies.append(latency_ms)
            if (
                result.get("status") != "pass"
                or result.get("requested_mode") != mode
                or result.get("effective_mode") != mode
                or result.get("top_k") != top_k
            ):
                raise EvaluationError(
                    f"{mode}/{question['id']} route contract drift"
                )
            results = result.get("results")
            if not isinstance(results, list):
                raise EvaluationError(
                    f"{mode}/{question['id']} returned invalid results"
                )
            metrics = retrieval_metrics(results, question["source_ids"], top_k)
            if question["id"] in hard_truth:
                metrics.update(
                    exact_evidence_metrics(
                        results,
                        hard_truth[question["id"]],
                        top_k,
                    )
                )
            for name, value in metrics.items():
                metric_values[name].append(value)
            per_question.append(
                {
                    "question_id": question["id"],
                    "cohort": (
                        "hard"
                        if question["question_type"] == "hard"
                        else "development"
                    ),
                    "latency_ms": round(latency_ms, 3),
                    "metrics": {
                        name: round(value, 6)
                        for name, value in sorted(metrics.items())
                    },
                    "results": [safe_result(row) for row in results],
                }
            )
        aggregates = {
            name: round(statistics.fmean(values), 6)
            for name, values in sorted(metric_values.items())
        }
        mode_reports.append(
            {
                "mode": mode,
                "question_count": len(per_question),
                "aggregates": aggregates,
                "latency_ms": {
                    "median": round(statistics.median(latencies), 3),
                    "p95": round(percentile_95(latencies), 3),
                    "maximum": round(max(latencies), 3),
                },
                "questions": per_question,
            }
        )

    primary_metric = f"recall@{top_k}"
    ranking = sorted(
        (
            {
                "mode": row["mode"],
                primary_metric: row["aggregates"][primary_metric],
                f"ndcg@{top_k}": row["aggregates"][f"ndcg@{top_k}"],
                f"full_qrel_coverage@{top_k}": row["aggregates"][
                    f"full_qrel_coverage@{top_k}"
                ],
                f"reviewed_locator_recall@{top_k}": row["aggregates"].get(
                    f"reviewed_locator_recall@{top_k}",
                    0.0,
                ),
                "p95_latency_ms": row["latency_ms"]["p95"],
            }
            for row in mode_reports
        ),
        key=lambda row: (
            -row[primary_metric],
            -row[f"ndcg@{top_k}"],
            row["p95_latency_ms"],
            row["mode"],
        ),
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "pass",
        "dataset_id": DATASET_ID,
        "evaluation_kind": "direct-deterministic-retrieval",
        "answer_quality_evaluated": False,
        "qrel_policy": "non-exhaustive-focus-set",
        "top_k": top_k,
        "question_count": len(questions),
        "hard_question_count": len(hard_ids),
        "inputs": {
            "questions": fingerprint(questions_path),
            "hard_ground_truth": fingerprint(hard_truth_path),
            "classical_index": fingerprint(bundle / "classical" / "index.json"),
            "semantic_records": fingerprint(bundle / "semantic" / "records.jsonl"),
        },
        "snapshot": {
            "deep_validation": True,
            "core_tree_sha256": snapshot.index["core"]["tree_sha256"],
            "classical_index_sha256": snapshot.index_sha256,
            "classical_plan_sha256": snapshot.index["classical_plan_sha256"],
        },
        "ranking": ranking,
        "modes": mode_reports,
    }


def render_markdown(report: Mapping[str, Any]) -> str:
    """Render the metric-only primary report table."""

    top_k = report["top_k"]
    rows = [
        "# Software Architecture Books Retrieval Evaluation",
        "",
        (
            "This report compares deterministic discovery routes on 40 frozen "
            "questions. It evaluates retrieval, not generated-answer quality. "
            "Qrels are non-exhaustive focus sets."
        ),
        "",
        (
            f"| Rank | Route | Recall@{top_k} | nDCG@{top_k} | "
            "Full qrel coverage | Reviewed locator recall | P95 latency |"
        ),
        "|---:|---|---:|---:|---:|---:|---:|",
    ]
    for rank, row in enumerate(report["ranking"], start=1):
        rows.append(
            "| {rank} | {mode} | {recall:.3f} | {ndcg:.3f} | {full:.3f} | "
            "{locator:.3f} | {latency:.1f} ms |".format(
                rank=rank,
                mode=row["mode"],
                recall=row[f"recall@{top_k}"],
                ndcg=row[f"ndcg@{top_k}"],
                full=row[f"full_qrel_coverage@{top_k}"],
                locator=row[f"reviewed_locator_recall@{top_k}"],
                latency=row["p95_latency_ms"],
            )
        )
    rows.extend(
        [
            "",
            (
                "The JSON companion contains duplicate-safe per-question ranks, "
                "source identities, hashes, and exact locators, but excludes all "
                "private passage text."
            ),
            "",
        ]
    )
    return "\n".join(rows)


def build_parser() -> argparse.ArgumentParser:
    """Build the retrieval evaluation command line."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, default=DEFAULT_BUNDLE)
    parser.add_argument("--questions", type=Path, default=DEFAULT_QUESTIONS)
    parser.add_argument("--hard-truth", type=Path, default=DEFAULT_HARD_TRUTH)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--output-markdown", type=Path, default=DEFAULT_MARKDOWN)
    parser.add_argument("--top-k", type=int, default=10)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the frozen direct retrieval comparison."""

    args = build_parser().parse_args(argv)
    if not 1 <= args.top_k <= 100:
        raise SystemExit("--top-k must be between 1 and 100")
    try:
        report = evaluate(
            args.bundle.resolve(),
            args.questions.resolve(),
            args.hard_truth.resolve(),
            args.top_k,
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
        EvaluationError,
        OSError,
        UnicodeError,
        json.JSONDecodeError,
        ValueError,
        TypeError,
        KeyError,
        IndexError,
    ) as exc:
        print(
            json.dumps(
                {"status": "error", "error": str(exc)},
                ensure_ascii=False,
                sort_keys=True,
            )
        )
        return 2
    print(
        json.dumps(
            {
                "status": "pass",
                "dataset_id": DATASET_ID,
                "best_route": report["ranking"][0]["mode"],
                "output_json": portable_path(args.output_json),
                "output_markdown": portable_path(args.output_markdown),
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
