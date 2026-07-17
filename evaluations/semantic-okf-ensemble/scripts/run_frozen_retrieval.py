#!/usr/bin/env python3
"""Query a real ensemble bundle over the frozen forty-question benchmark."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path
from types import ModuleType
from typing import Any, Mapping, Sequence

from _evaluation import (
    REPO_ROOT,
    EvaluationError,
    benchmark_rows,
    canonical_json,
    display_path,
    module_from_path,
    sha256,
    write_new,
)


SCHEMA_VERSION = "semantic-okf-ensemble-retrieval-run/1.0"
EVIDENCE_SCHEMA_VERSION = "1.2"
DEFAULT_POLICIES = ("fast", "robust")
POLICIES = frozenset({"quality", "fast", "robust"})
CONSULT_SCRIPTS = REPO_ROOT / "skills/consult-semantic-okf-ensemble/scripts"
EVIDENCE_EVALUATOR = REPO_ROOT / "evaluations/semantic-okf-embeddings/scripts/compare_retrieval.py"


def _runtime() -> ModuleType:
    """Load the standalone consultant runtime from its explicit package path."""

    if str(CONSULT_SCRIPTS) not in sys.path:
        sys.path.insert(0, str(CONSULT_SCRIPTS))
    return module_from_path("semantic_okf_ensemble_evaluation_runtime", CONSULT_SCRIPTS / "_ensemble_snapshot.py")


def _evidence_evaluator() -> ModuleType:
    """Load the accepted schema-1.2 evidence validator used by embedding evaluations."""

    return module_from_path("semantic_okf_ensemble_evidence_12", EVIDENCE_EVALUATOR)


def _number(value: Any, label: str) -> float | None:
    """Normalize an optional finite score while rejecting booleans."""

    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise EvaluationError(f"{label} must be numeric or null")
    result = float(value)
    if not math.isfinite(result):
        raise EvaluationError(f"{label} must be finite")
    return result


def _hits(
    payload: Mapping[str, Any], policy: str, top_k: int, evaluator: ModuleType
) -> list[Any]:
    """Validate one runtime response and adapt its exact evidence rows to schema 1.2."""

    if payload.get("status") != "pass" or payload.get("effective_policy") != policy:
        raise EvaluationError(f"ensemble runtime did not execute policy {policy}")
    if payload.get("top_k") != top_k or payload.get("returned") != top_k:
        raise EvaluationError(f"ensemble runtime policy {policy} did not return top-k {top_k}")
    gate = payload.get("candidate_set_gate")
    if not isinstance(gate, dict) or gate.get("preserved_exactly") is not True:
        raise EvaluationError(f"ensemble runtime policy {policy} failed its candidate-set gate")
    rows = payload.get("results")
    if not isinstance(rows, list) or len(rows) != top_k:
        raise EvaluationError(f"ensemble runtime policy {policy} results are incomplete")
    paper_ids: list[str] = []
    result: list[Any] = []
    for rank, row in enumerate(rows, 1):
        if not isinstance(row, dict) or row.get("rank") != rank:
            raise EvaluationError(f"ensemble runtime policy {policy} has an invalid rank {rank}")
        ensemble = row.get("ensemble")
        paper_id = row.get("paper_id")
        if not isinstance(ensemble, dict) or ensemble.get("policy") != policy:
            raise EvaluationError(f"ensemble runtime policy metadata differs at rank {rank}")
        if not isinstance(paper_id, str) or not paper_id or paper_id in paper_ids:
            raise EvaluationError(f"ensemble runtime policy {policy} has an invalid paper identity")
        paper_ids.append(paper_id)
        result.append(
            evaluator.RetrievalHit(
                source_id=row.get("source_id"),
                paper_id=paper_id,
                chunk_id=row.get("chunk_id"),
                ordinal=row.get("ordinal"),
                concept_path=row.get("concept_path"),
                concept_id=row.get("concept_id"),
                record_id=row.get("record_id"),
                record_sha256=row.get("record_sha256"),
                source_path=row.get("source_path"),
                locator=row.get("locator"),
                text=row.get("text"),
                text_sha256=row.get("text_sha256"),
                score=_number(row.get("score"), f"policy {policy} rank {rank} score"),
            )
        )
    if paper_ids != gate.get("selected_paper_ids"):
        raise EvaluationError(f"ensemble runtime policy {policy} selected ranking differs from results")
    return result


def _route(
    snapshot: Any,
    runtime: ModuleType,
    evaluator: ModuleType,
    ledger: Any,
    questions: Sequence[Any],
    policy: str,
    top_k: int,
    continue_on_error: bool,
) -> dict[str, Any]:
    """Execute one real policy and retain its ensemble gate traces per question."""

    traces: list[dict[str, Any] | None] = []

    def search(question: str) -> list[Any]:
        try:
            payload = runtime.search_snapshot(snapshot, question, policy, top_k)
            hits = _hits(payload, policy, top_k, evaluator)
        except (runtime.SnapshotError, EvaluationError, ValueError, TypeError, KeyError, IndexError) as exc:
            traces.append(None)
            raise evaluator.ComparisonError(str(exc)) from exc
        traces.append(
            {
                "candidate_set_gate": payload["candidate_set_gate"],
                "promotion_gate": payload["promotion_gate"],
                "route_rankings": payload["route_rankings"],
                "policy": payload["policy"],
                "snapshot": payload["snapshot"],
            }
        )
        return hits

    route = evaluator.evaluate_route(
        f"ensemble_{policy}",
        snapshot.root,
        ledger,
        questions,
        search,
        continue_on_error=continue_on_error,
    )
    if len(traces) != len(route["queries"]):
        raise EvaluationError(f"ensemble policy {policy} trace count differs")
    for row, trace in zip(route["queries"], traces, strict=True):
        row["ensemble_trace"] = trace
    route["runtime_policy"] = policy
    ranking_identity = [
        {
            "question_id": row["question_id"],
            "hits": [
                {
                    "rank": hit["rank"],
                    "paper_id": hit["paper_id"],
                    "source_id": hit["source_id"],
                    "record_id": hit["record_id"],
                    "text_sha256": hit["text_sha256"],
                }
                for hit in row["hits"]
            ],
        }
        for row in route["queries"]
    ]
    route["rankings_sha256"] = hashlib.sha256(
        canonical_json(ranking_identity).encode("utf-8")
    ).hexdigest()
    route["timing_scope"] = "in-process validated component retrieval, ensemble fusion, and gate execution"
    return route


def _markdown(report: dict[str, Any]) -> str:
    """Render a compact run summary."""

    lines = [
        "# Semantic OKF ensemble frozen retrieval run",
        "",
        f"Status: **{report['status']}**. Bundle index: `{report['bundle']['ensemble_index_sha256']}`. ",
        "",
        "| Policy | Repetitions | Recall@10 | MRR@10 | nDCG@10 | Source Recall@10 | Evidence validity | Mean ms | P95 ms | Errors |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for route in report["routes"]:
        paper = route["paper_metrics"]
        source = route["source_metrics"]
        timing = route["timing_ms"]
        evidence = route["evidence_validity"]
        lines.append(
            f"| `{route['runtime_policy']}` | {route['determinism']['repetitions']} | {paper['recall_at_10']:.2%} | "
            f"{paper['mrr_at_10']:.2%} | {paper['ndcg_at_10']:.2%} | "
            f"{source['recall_at_10']:.2%} | {float(evidence['ratio'] or 0):.2%} | "
            f"{timing['mean']:.2f} | {timing['p95']:.2f} | {route['error_count']} |"
        )
    lines.extend(
        [
            "",
            "Every retained hit was revalidated against `semantic/records.jsonl`, its exact concept path, identity fields, retained-text hash, and record or character-range locator under evidence contract 1.2.",
            "The frozen questions remain evaluator-only and are not copied into the skill or bundle.",
            "",
        ]
    )
    return "\n".join(lines)


def run(args: argparse.Namespace) -> dict[str, Any]:
    """Load a deeply validated bundle once and execute every requested policy."""

    manifest, frozen_rows, _ = benchmark_rows()
    runtime = _runtime()
    evaluator = _evidence_evaluator()
    bundle = args.bundle.resolve(strict=True)
    snapshot = runtime.load_snapshot(bundle, deep_validation=True)
    inspection = runtime.inspect_snapshot(snapshot)
    if inspection.get("status") != "pass" or inspection.get("deep_validation") is not True:
        raise EvaluationError("ensemble bundle deep validation did not pass")
    question_path = REPO_ROOT / manifest["cohorts"]["retrieval_questions"]["path"]
    questions = evaluator.load_questions(question_path)
    if [item.identifier for item in questions] != [row["id"] for row in frozen_rows]:
        raise EvaluationError("evidence evaluator question identities differ from the frozen benchmark")
    ledger = evaluator.AuthoritativeLedger.from_bundle(bundle)
    policies = args.policy or list(DEFAULT_POLICIES)
    if len(set(policies)) != len(policies):
        raise EvaluationError("policies must not contain duplicates")
    routes: list[dict[str, Any]] = []
    for policy in policies:
        repetitions = [
            _route(
                snapshot,
                runtime,
                evaluator,
                ledger,
                questions,
                policy,
                args.top_k,
                args.continue_on_error,
            )
            for _ in range(args.repetitions)
        ]
        ranking_hashes = [route["rankings_sha256"] for route in repetitions]
        if len(set(ranking_hashes)) != 1:
            raise EvaluationError(f"ensemble policy {policy} rankings differ across repetitions")
        primary = repetitions[0]
        primary["determinism"] = {
            "repetitions": args.repetitions,
            "all_rankings_equal": True,
            "rankings_sha256": ranking_hashes[0],
            "per_repetition_timing_ms": [route["timing_ms"] for route in repetitions],
        }
        routes.append(primary)
    status = "pass" if all(
        route["error_count"] == 0 and route["evidence_validity"]["ratio"] == 1.0 for route in routes
    ) else "fail"
    return {
        "schema_version": SCHEMA_VERSION,
        "extends_evidence_schema": EVIDENCE_SCHEMA_VERSION,
        "status": status,
        "comparison": "semantic-okf-definitive-ensemble-frozen-retrieval",
        "query_count": len(questions),
        "top_k": args.top_k,
        "benchmark": {
            "benchmark_id": manifest["benchmark_id"],
            "manifest_sha256": "2f905bd9a7ad07991fe215e0b82b3c7bfdcccbff9431ee5bd20095d99b8f4414",
            "question_path": display_path(question_path),
            "question_sha256": sha256(question_path),
        },
        "bundle": {
            "path": display_path(bundle),
            "ensemble_index_sha256": inspection["ensemble_index_sha256"],
            "ensemble_plan_sha256": inspection["ensemble_plan_sha256"],
            "core": inspection["core"],
            "deep_validation": True,
            "read_only": inspection["read_only"],
        },
        "runtime": {
            "consult_script": display_path(CONSULT_SCRIPTS / "query_semantic_okf_ensemble.py"),
            "consult_script_sha256": sha256(CONSULT_SCRIPTS / "query_semantic_okf_ensemble.py"),
            "ensemble_runtime": display_path(CONSULT_SCRIPTS / "_ensemble_snapshot.py"),
            "ensemble_runtime_sha256": sha256(CONSULT_SCRIPTS / "_ensemble_snapshot.py"),
            "evidence_evaluator": display_path(EVIDENCE_EVALUATOR),
            "evidence_evaluator_sha256": sha256(EVIDENCE_EVALUATOR),
        },
        "evidence_contract": {
            "schema_version": EVIDENCE_SCHEMA_VERSION,
            "ledger": ledger.fingerprint(),
            "validation": "exact authoritative ledger identity, safe concept path, concept file, text hash, and exact locator resolution",
        },
        "routes": routes,
    }


def _args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--policy", action="append", choices=sorted(POLICIES))
    parser.add_argument("--top-k", type=int, default=10, choices=[10])
    parser.add_argument("--repetitions", type=int, default=1, choices=range(1, 11))
    parser.add_argument("--continue-on-error", action="store_true")
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-markdown", type=Path, required=True)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    """Execute the append-only real-bundle runner."""

    try:
        args = _args(argv)
        if args.output_json.exists() or args.output_markdown.exists():
            raise EvaluationError("refusing to overwrite existing output")
        report = run(args)
        write_new(args.output_json, json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n")
        write_new(args.output_markdown, _markdown(report))
    except (EvaluationError, OSError, ValueError, TypeError, KeyError, IndexError) as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, sort_keys=True), file=sys.stderr)
        return 2
    print(
        json.dumps(
            {
                "status": report["status"],
                "routes": [
                    {
                        "name": route["name"],
                        "recall_at_10": route["paper_metrics"]["recall_at_10"],
                        "mrr_at_10": route["paper_metrics"]["mrr_at_10"],
                        "evidence_validity": route["evidence_validity"]["ratio"],
                    }
                    for route in report["routes"]
                ],
            },
            sort_keys=True,
        )
    )
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
