#!/usr/bin/env python3
"""Evaluate one sealed Tantivy candidate on one declared question cohort."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import time
from pathlib import Path
from types import ModuleType
from typing import Any, Mapping, Sequence


SCHEMA_VERSION = "semantic-okf-tantivy-evolution-retrieval/1.0"
sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
CANONICAL_EVALUATOR = SCRIPT.with_name("evaluate_canonical_retrieval.py")


class EvolutionEvaluationError(RuntimeError):
    """Describe an invalid cohort or candidate evaluation."""


def load_module(name: str, path: Path) -> ModuleType:
    """Load one fixed local module."""

    specification = importlib.util.spec_from_file_location(name, path)
    if specification is None or specification.loader is None:
        raise EvolutionEvaluationError(f"cannot load Python module from {path}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


CANONICAL = load_module(
    "semantic_okf_tantivy_evolution_canonical",
    CANONICAL_EVALUATOR,
)
BASE = CANONICAL.BASE


def strict_json(path: Path, label: str) -> Any:
    """Load strict JSON from one local file."""

    def reject_constant(value: str) -> Any:
        raise EvolutionEvaluationError(
            f"{label} contains non-standard number {value!r}"
        )

    def reject_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise EvolutionEvaluationError(
                    f"{label} contains duplicate key {key!r}"
                )
            result[key] = value
        return result

    try:
        return json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=reject_duplicates,
            parse_constant=reject_constant,
        )
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise EvolutionEvaluationError(f"cannot read {label}: {exc}") from exc


def cohort_ids(path: Path, cohort: str) -> tuple[str, ...]:
    """Load one exact cohort from the canonical registry declaration."""

    payload = strict_json(path, "cohort registry")
    if (
        not isinstance(payload, dict)
        or payload.get("schema_version")
        != "semantic-okf-evaluation-cohorts/1.0"
        or not isinstance(payload.get("cohorts"), dict)
    ):
        raise EvolutionEvaluationError("cohort registry has an invalid schema")
    values = payload["cohorts"].get(cohort)
    if (
        not isinstance(values, list)
        or not values
        or any(not isinstance(value, str) or not value for value in values)
        or len(values) != len(set(values))
    ):
        raise EvolutionEvaluationError(f"cohort {cohort!r} is missing or invalid")
    return tuple(values)


def evaluate(args: argparse.Namespace) -> dict[str, Any]:
    """Evaluate one candidate without loading questions outside its cohort."""

    ids = cohort_ids(args.cohorts, args.cohort)
    inventory = BASE.load_inventory(args.inventory)
    all_questions = BASE.load_questions(args.questions)
    questions_by_short_id: dict[str, Any] = {}
    for question in all_questions:
        short_id = question.identifier.split("-", 1)[0]
        if short_id in questions_by_short_id:
            raise EvolutionEvaluationError(
                f"question prefix {short_id!r} is not unique"
            )
        questions_by_short_id[short_id] = question
    missing = sorted(set(ids) - set(questions_by_short_id))
    if missing:
        raise EvolutionEvaluationError(f"cohort names unknown questions: {missing}")
    questions = [questions_by_short_id[identifier] for identifier in ids]
    if args.top_k < 10:
        raise EvolutionEvaluationError("--top-k must be at least 10")
    bundle = args.bundle.resolve()
    consult_script = args.consult_script.resolve()
    if not bundle.is_dir() or not consult_script.is_file():
        raise EvolutionEvaluationError("bundle or consultation script is missing")
    raw_verification = BASE.verify_input_inventory(args.input_root, inventory)
    if raw_verification["status"] != "pass":
        raise EvolutionEvaluationError("raw input inventory verification failed")

    runtime = CANONICAL.load_runtime(consult_script)
    setup_started = time.perf_counter()
    snapshot = runtime.load_snapshot(bundle)
    setup_ms = (time.perf_counter() - setup_started) * 1000.0
    ledger = BASE.AuthoritativeLedger.from_bundle(bundle)
    route = BASE.evaluate_route(
        "tantivy_bm25",
        bundle,
        ledger,
        questions,
        lambda query: CANONICAL.tantivy_hits(
            runtime,
            snapshot,
            query,
            args.top_k,
        ),
        continue_on_error=False,
    )
    if route["error_count"] != 0:
        raise EvolutionEvaluationError("candidate produced query errors")
    if route["evidence_validity"]["ratio"] != 1.0:
        raise EvolutionEvaluationError("candidate produced invalid evidence")
    runtime_report = runtime.inspect_snapshot(snapshot)
    if runtime_report.get("status") != "pass":
        raise EvolutionEvaluationError("candidate runtime inspection failed")
    paper_metrics = route["paper_metrics"]
    scalar_reward = sum(
        float(paper_metrics[name])
        for name in ("recall_at_10", "mrr_at_10", "ndcg_at_10")
    ) / 3.0
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "pass",
        "cohort": args.cohort,
        "question_ids": list(ids),
        "question_count": len(ids),
        "top_k": args.top_k,
        "scalar_reward": scalar_reward,
        "qualification": {
            "zero_errors": True,
            "evidence_validity": route["evidence_validity"]["ratio"],
            "complete_question_count": len(route["queries"]) == len(ids),
        },
        "metrics": {
            "paper": paper_metrics,
            "source": route["source_metrics"],
        },
        "timing_ms": {
            "setup": setup_ms,
            "query_mean": route["timing_ms"]["mean"],
            "query_p95": route["timing_ms"]["p95"],
        },
        "inputs": {
            "inventory": BASE._file_fingerprint(args.inventory.resolve()),
            "questions": BASE._file_fingerprint(args.questions.resolve()),
            "cohorts": BASE._file_fingerprint(args.cohorts.resolve()),
            "consult_script": BASE._file_fingerprint(consult_script),
            "runtime_script": BASE._file_fingerprint(
                consult_script.parent / "_tantivy_snapshot.py"
            ),
            "bundle": BASE.bundle_fingerprint(bundle),
            "raw_input_verification": raw_verification,
        },
        "runtime": runtime_report,
        "route": route,
    }


def percent(value: Any) -> str:
    """Render one metric as a percentage."""

    return f"{100.0 * float(value):.2f}%"


def render_markdown(report: Mapping[str, Any]) -> str:
    """Render one compact candidate receipt."""

    metrics = report["metrics"]["paper"]
    timing = report["timing_ms"]
    return "\n".join(
        [
            "# Tantivy Consultation Evolution Cohort",
            "",
            f"Status: **{report['status']}**. Cohort: `{report['cohort']}`. "
            f"Questions: {report['question_count']}.",
            "",
            "| Recall@10 | MRR@10 | nDCG@10 | Evidence validity | Mean ms | P95 ms |",
            "| ---: | ---: | ---: | ---: | ---: | ---: |",
            f"| {percent(metrics['recall_at_10'])} | "
            f"{percent(metrics['mrr_at_10'])} | "
            f"{percent(metrics['ndcg_at_10'])} | "
            f"{percent(report['qualification']['evidence_validity'])} | "
            f"{timing['query_mean']:.2f} | {timing['query_p95']:.2f} |",
            "",
            f"Scalar development reward: `{report['scalar_reward']:.10f}`.",
            "",
        ]
    )


def build_parser() -> argparse.ArgumentParser:
    """Build the cohort evaluator CLI."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inventory", type=Path, required=True)
    parser.add_argument("--questions", type=Path, required=True)
    parser.add_argument("--cohorts", type=Path, required=True)
    parser.add_argument("--cohort", required=True)
    parser.add_argument("--input-root", type=Path, required=True)
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--consult-script", type=Path, required=True)
    parser.add_argument("--top-k", type=int, default=10)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-markdown", type=Path, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run one append-only cohort evaluation."""

    args = build_parser().parse_args(argv)
    try:
        CANONICAL.require_absent(args.output_json)
        CANONICAL.require_absent(args.output_markdown)
        report = evaluate(args)
    except (
        EvolutionEvaluationError,
        CANONICAL.CanonicalEvaluationError,
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
        render_markdown(report),
        encoding="utf-8",
        newline="\n",
    )
    print(
        json.dumps(
            {
                "status": report["status"],
                "cohort": report["cohort"],
                "question_count": report["question_count"],
                "scalar_reward": report["scalar_reward"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
