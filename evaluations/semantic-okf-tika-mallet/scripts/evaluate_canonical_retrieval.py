#!/usr/bin/env python3
"""Evaluate Tika/MALLET retrieval on the frozen GraphRAG 40-question corpus."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import os
import statistics
import sys
import time
from pathlib import Path
from types import ModuleType
from typing import Any, Sequence


SCHEMA_VERSION = "semantic-okf-tika-mallet-canonical-retrieval/1.0"
ROUTES = ("bm25", "topic", "association", "fusion")
HERE = Path(__file__).resolve().parent
EVALUATION = HERE.parent
REPO = EVALUATION.parents[1]
SPEC = EVALUATION / "canonical" / "graphrag-papers-40"
BASE_PATH = (
    REPO
    / "evaluations"
    / "semantic-okf-embeddings"
    / "scripts"
    / "compare_retrieval.py"
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


BASE = _load_module("semantic_okf_tika_mallet_evidence_evaluator", BASE_PATH)


def _load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise EvaluationError(f"cannot read {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise EvaluationError(f"{path} must contain one JSON object")
    return value


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _canonical_digest(value: Any) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _tree_inventory(root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted(
        root.rglob("*"), key=lambda item: item.relative_to(root).as_posix()
    ):
        if path.is_symlink():
            raise EvaluationError(f"bundle contains a symlink: {path}")
        if path.is_file():
            rows.append(
                {
                    "path": path.relative_to(root).as_posix(),
                    "bytes": path.stat().st_size,
                    "sha256": _sha256_file(path),
                }
            )
    return rows


def _verify_source_inventory(path: Path) -> dict[str, Any]:
    inventory = _load_json(path)
    if inventory.get("schema_version") != "semantic-okf-tika-mallet-canonical-input/1.0":
        raise EvaluationError("unsupported source inventory schema")
    source_root = REPO / str(inventory.get("source_root"))
    verified = 0
    for row in inventory.get("files", []):
        if not isinstance(row, dict) or not isinstance(row.get("path"), str):
            raise EvaluationError("source inventory contains an invalid row")
        source = source_root / row["path"]
        if (
            not source.is_file()
            or source.is_symlink()
            or source.stat().st_size != row.get("bytes")
            or _sha256_file(source) != row.get("sha256")
        ):
            raise EvaluationError(f"source inventory drift: {row['path']}")
        verified += 1
    if verified != 15:
        raise EvaluationError(f"canonical PDF inventory must contain 15 files, found {verified}")
    contract = inventory.get("ranking_contract")
    if not isinstance(contract, dict) or contract.get("selected_route") != "fusion":
        raise EvaluationError("the predeclared selected route must be fusion")
    return {
        "status": "pass",
        "verified_files": verified,
        "inventory_sha256": _sha256_file(path),
        "selected_route": contract["selected_route"],
    }


def _load_runtime(consult_script: Path) -> ModuleType:
    support = consult_script.parent / "_tika_mallet_snapshot.py"
    if not support.is_file():
        raise EvaluationError(f"consultation support is missing: {support}")
    sys.path.insert(0, str(consult_script.parent))
    try:
        return _load_module("semantic_okf_tika_mallet_canonical_runtime", support)
    except (ImportError, OSError, RuntimeError, SyntaxError) as exc:
        raise EvaluationError(f"cannot load consultation runtime: {exc}") from exc


def _hits(
    runtime: ModuleType,
    snapshot: Any,
    query: str,
    mode: str,
    top_k: int,
) -> list[Any]:
    try:
        payload = runtime.search_snapshot(snapshot, query, mode, top_k)
    except Exception as exc:
        if isinstance(exc, (KeyboardInterrupt, SystemExit)):
            raise
        raise BASE.ComparisonError(f"Tika/MALLET {mode} search failed: {exc}") from exc
    normalized = dict(payload)
    normalized["results"] = [
        {**item, "chunk_id": item.get("document_id")}
        for item in payload.get("results", [])
    ]
    return BASE.parse_search_output(normalized, top_k)


def _mean_metrics(rows: Sequence[dict[str, Any]], key: str) -> dict[str, float]:
    names = [
        *(f"recall_at_{cutoff}" for cutoff in BASE.METRIC_CUTOFFS),
        "mrr_at_10",
        "ndcg_at_10",
    ]
    return {
        name: statistics.fmean(float(row[key][name]) for row in rows)
        for name in names
    }


def _cohort_summary(rows: Sequence[dict[str, Any]]) -> dict[str, Any]:
    returned = sum(int(row["evidence_validity"]["returned"]) for row in rows)
    valid = sum(int(row["evidence_validity"]["valid"]) for row in rows)
    return {
        "query_count": len(rows),
        "error_count": sum(row["error"] is not None for row in rows),
        "paper_metrics": _mean_metrics(rows, "paper_metrics"),
        "source_metrics": _mean_metrics(rows, "source_metrics"),
        "evidence_validity": {
            "returned": returned,
            "valid": valid,
            "invalid": returned - valid,
            "ratio": valid / returned if returned else None,
        },
    }


def _attach_cohorts(route: dict[str, Any]) -> None:
    rows = route["queries"]
    original = [row for row in rows if int(row["question_id"][1:4]) <= 30]
    hard = [row for row in rows if int(row["question_id"][1:4]) >= 31]
    if len(original) != 30 or len(hard) != 10:
        raise EvaluationError(f"route {route['name']} has incomplete cohorts")
    route["cohorts"] = {
        "original_30": _cohort_summary(original),
        "hard_10": _cohort_summary(hard),
    }


def _percentile(values: Sequence[float], percentile: float) -> float:
    ordered = sorted(values)
    if not ordered:
        raise EvaluationError("cannot calculate a percentile from no values")
    if len(ordered) == 1:
        return ordered[0]
    position = (len(ordered) - 1) * percentile
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    weight = position - lower
    return ordered[lower] * (1.0 - weight) + ordered[upper] * weight


def evaluate(args: argparse.Namespace) -> dict[str, Any]:
    """Validate once, evaluate every route, and prove the bundle stayed immutable."""

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
    source_verification = _verify_source_inventory(args.inventory.resolve())
    questions = BASE.load_questions(args.questions.resolve())
    if len(questions) != args.expected_question_count:
        raise EvaluationError(
            "evaluation requires "
            f"{args.expected_question_count} questions, found {len(questions)}"
        )
    if args.canonical_cohorts and len(questions) != 40:
        raise EvaluationError("--canonical-cohorts requires exactly 40 questions")
    bundle = args.bundle.resolve()
    before = _tree_inventory(bundle)
    started = time.perf_counter()
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
    routes: list[dict[str, Any]] = []
    for mode in ROUTES:
        route = BASE.evaluate_route(
            f"tika_mallet_{mode}",
            bundle,
            ledger,
            questions,
            lambda query, selected=mode: _hits(
                runtime, snapshot, query, selected, args.top_k
            ),
            continue_on_error=False,
        )
        if args.canonical_cohorts:
            _attach_cohorts(route)
        if route["error_count"] != 0:
            raise EvaluationError(f"route {mode} produced query errors")
        if route["evidence_validity"]["ratio"] != 1.0:
            raise EvaluationError(f"route {mode} produced invalid evidence")
        route["setup_ms"] = setup_ms if mode == ROUTES[0] else 0.0
        route["timing_scope"] = (
            "One in-process search against one reused, deeply validated read-only snapshot."
        )
        routes.append(route)
    after = _tree_inventory(bundle)
    if before != after:
        raise EvaluationError("evaluation modified the immutable candidate bundle")
    selected = next(row for row in routes if row["name"] == "tika_mallet_fusion")
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "pass",
        "dataset_id": args.dataset_id,
        "candidate_id": "tika-mallet",
        "ranking_eligible": True,
        "selected_route": "tika_mallet_fusion",
        "selection_timing": "frozen-before-canonical-build-and-retrieval",
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
        },
        "timing_contract": {
            "unit": "milliseconds",
            "query_scope": "one in-process search against one reused snapshot",
            "setup_excluded_from_query_latency": True,
            "shared_deep_validation_ms": setup_ms,
            "evaluation_wall_ms": (time.perf_counter() - started) * 1000.0,
        },
        "source_verification": source_verification,
        "inputs": {
            "questions": BASE._file_fingerprint(args.questions.resolve()),
            "source_inventory": BASE._file_fingerprint(args.inventory.resolve()),
            "consult_script": BASE._file_fingerprint(args.consult_script.resolve()),
            "evaluator_script": BASE._file_fingerprint(Path(__file__).resolve()),
        },
        "bundle": {
            "path": str(bundle),
            "file_count": len(before),
            "inventory_sha256": _canonical_digest(before),
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
    return f"{100.0 * float(value):.1f}%"


def _number(value: Any) -> str:
    return f"{float(value):.3f}"


def render_markdown(report: dict[str, Any]) -> str:
    """Render every route and the frozen selected-route conclusion."""

    lines = [
        "# Tika and Java MALLET Canonical Retrieval Evaluation",
        "",
        f"Status: **{report['status']}**. Dataset: `{report['dataset_id']}`. "
        f"Questions: {report['query_count']}. Returned pool: {report['top_k']}.",
        "",
    ]
    if "cohorts" in report["routes"][0]:
        lines.extend(
            [
                "| Route | Recall@10 | Hard Recall@10 | MRR@10 | nDCG@10 | "
                "Evidence valid | Mean ms | p95 ms |",
                "|---|---:|---:|---:|---:|---:|---:|---:|",
            ]
        )
    else:
        lines.extend(
            [
                "| Route | Recall@10 | MRR@10 | nDCG@10 | "
                "Evidence valid | Mean ms | p95 ms |",
                "|---|---:|---:|---:|---:|---:|---:|",
            ]
        )
    for route in report["routes"]:
        all_metrics = route["paper_metrics"]
        selected = " **(selected)**" if route["name"] == report["selected_route"] else ""
        row = (
            f"| `{route['name']}`{selected} | "
            f"{_percent(all_metrics['recall_at_10'])} | "
        )
        if "cohorts" in route:
            row += (
                f"{_percent(route['cohorts']['hard_10']['paper_metrics']['recall_at_10'])} | "
            )
        lines.append(
            row
            + f"{_number(all_metrics['mrr_at_10'])} | "
            f"{_number(all_metrics['ndcg_at_10'])} | "
            f"{_percent(route['evidence_validity']['ratio'])} | "
            f"{route['timing_ms']['mean']:.1f} | "
            f"{route['timing_ms']['p95']:.1f} |"
        )
    lines.extend(
        [
            "",
            "The selected `fusion` route was frozen in the source inventory before "
            "the canonical build and retrieval results existed. Other routes are "
            "diagnostics and do not replace it post hoc.",
            "",
            f"Snapshot validation took "
            f"{report['timing_contract']['shared_deep_validation_ms']:.1f} ms. "
            f"The {report['bundle']['file_count']}-file bundle retained inventory "
            f"SHA-256 `{report['bundle']['inventory_sha256']}` before and after the run.",
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
    parser.add_argument(
        "--questions",
        type=Path,
        default=REPO
        / "evaluations"
        / "semantic-okf-adaptive"
        / "retrieval-questions.jsonl",
    )
    parser.add_argument(
        "--inventory",
        type=Path,
        default=SPEC / "source-inventory.json",
    )
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
    if any(path.exists() or path.is_symlink() for path in (args.output_json, args.output_markdown)):
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
