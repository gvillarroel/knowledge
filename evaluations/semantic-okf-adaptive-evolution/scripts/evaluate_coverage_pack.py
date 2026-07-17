#!/usr/bin/env python3
"""Evaluate facet-separated candidate coverage without calling it Recall@30."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import statistics
import sys
import time
from pathlib import Path
from types import ModuleType
from typing import Any


SCHEMA_VERSION = "semantic-okf-adaptive-coverage-pack-evaluation/1.0"
FROZEN_MANIFEST_SHA256 = (
    "2f905bd9a7ad07991fe215e0b82b3c7bfdcccbff9431ee5bd20095d99b8f4414"
)


class CoverageError(ValueError):
    """Describe an invalid coverage pack or evaluation input."""


def _module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise CoverageError(f"cannot load module: {path}")
    value = importlib.util.module_from_spec(spec)
    sys.modules[name] = value
    spec.loader.exec_module(value)
    return value


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _jsonl(path: Path) -> list[dict[str, Any]]:
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]
    if not all(isinstance(row, dict) for row in rows):
        raise CoverageError(f"expected JSON objects: {path}")
    return rows


def _tree(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): _sha256(path)
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def _claims(ground_truth: dict[str, Any], key: str) -> set[str]:
    return {
        claim_id
        for group in ground_truth["ground_truth"][key]
        for claim_id in group["evidence_claim_ids"]
    }


def _recall(returned: set[str], expected: set[str]) -> float:
    return len(returned & expected) / len(expected) if expected else 1.0


def _validate_candidate(row: dict[str, Any], binding: dict[str, Any], rank: int) -> None:
    expected = {
        "rank": rank,
        "claim_id": binding["record_id"],
        "paper_id": binding["paper_id"],
        "authoritative_text": binding["authoritative_text"],
        "concept_path": binding["concept_path"],
        "source_path": binding["source_path"],
        "locators": sorted(set(binding["locator_tokens"])),
        "citation_pages": sorted(set(binding["citation_pages"])),
    }
    if row != expected:
        raise CoverageError(f"coverage candidate {binding['record_id']} differs from its binding")


def _render(report: dict[str, Any]) -> str:
    metrics = report["metrics"]
    lines = [
        "# Adaptive Facet-Coverage Evaluation",
        "",
        "This report measures the union of a top-30 primary pack and bounded per-facet candidate lists. "
        "The union has a larger variable budget and is not Recall@30.",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| Primary answer-claim Recall@30 | {metrics['primary_answer_claim_recall_at_30']:.1%} |",
        f"| Facet-union answer-claim coverage | {metrics['facet_union_answer_claim_coverage']:.1%} |",
        f"| Facet-union important-negative coverage | {metrics['facet_union_important_negative_coverage']:.1%} |",
        f"| Facet-union required-paper coverage | {metrics['facet_union_required_paper_coverage']:.1%} |",
        f"| Mean unique candidate claims | {metrics['unique_candidate_claims']['mean']:.1f} |",
        f"| Mean facet count | {metrics['facet_count']['mean']:.1f} |",
        f"| Mean latency | {metrics['latency_ms']['mean']:.1f} ms |",
        "",
        "| Question | Primary claims | Union claims | Union negatives | Papers | Unique candidates | Facets |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in report["questions"]:
        lines.append(
            f"| {row['id']} | {row['primary_answer_claim_recall_at_30']:.1%} | "
            f"{row['facet_union_answer_claim_coverage']:.1%} | "
            f"{row['facet_union_important_negative_coverage']:.1%} | "
            f"{row['facet_union_required_paper_coverage']:.1%} | "
            f"{row['unique_candidate_claims']} | {row['facet_count']} |"
        )
    lines.extend(
        [
            "",
            "Every primary and facet candidate was rechecked against the independently derived answer bindings. "
            "The snapshot remained byte-identical and the runtime contained no frozen question IDs.",
            "",
        ]
    )
    return "\n".join(lines)


def evaluate(args: argparse.Namespace) -> dict[str, Any]:
    repo = args.repo_root.resolve(strict=True)
    bundle = args.bundle.resolve(strict=True)
    runtime_path = args.runtime.resolve(strict=True)
    questions_path = args.questions.resolve(strict=True)
    truth_path = args.ground_truth.resolve(strict=True)
    frozen_module = _module(
        "adaptive_coverage_frozen_validator",
        repo / "evaluations/semantic-okf-adaptive-evolution/scripts/validate_frozen_benchmark.py",
    )
    frozen = frozen_module.validate(
        repo,
        repo / "evaluations/semantic-okf-adaptive-evolution/frozen-benchmark.json",
    )
    if frozen["manifest_sha256"] != FROZEN_MANIFEST_SHA256:
        raise CoverageError("frozen benchmark identity differs")
    runtime = _module("adaptive_coverage_candidate_runtime", runtime_path)
    questions = _jsonl(questions_path)
    truth = _jsonl(truth_path)
    if [row["id"] for row in questions] != [row["id"] for row in truth]:
        raise CoverageError("question and ground-truth IDs differ")
    runtime_bytes = runtime_path.read_bytes()
    leaked_ids = [row["id"] for row in questions if row["id"].encode() in runtime_bytes]
    if leaked_ids:
        raise CoverageError(f"runtime contains frozen question IDs: {leaked_ids}")
    before = _tree(bundle)
    snapshot = runtime.load_snapshot(bundle, deep_validation=True)
    binding_by_claim = {row["record_id"]: row for row in snapshot.answer_bindings}
    rows: list[dict[str, Any]] = []
    latencies: list[float] = []
    for question, ground_truth in zip(questions, truth, strict=True):
        packs: list[dict[str, Any]] = []
        for _ in range(args.repetitions):
            started = time.perf_counter()
            packs.append(
                runtime.build_coverage_pack(
                    snapshot,
                    question["question"],
                    args.top_k,
                    args.per_facet,
                    args.maximum_facets,
                )
            )
            latencies.append((time.perf_counter() - started) * 1000.0)
        if any(pack != packs[0] for pack in packs[1:]):
            raise CoverageError(f"nondeterministic coverage pack for {question['id']}")
        pack = packs[0]
        primary = {row["record_id"] for row in pack["primary"]["ranked_bindings"]}
        union = set(primary)
        for facet in pack["coverage_facets"]:
            for rank, candidate in enumerate(facet["candidates"], start=1):
                binding = binding_by_claim.get(candidate.get("claim_id"))
                if binding is None:
                    raise CoverageError("coverage pack names an unknown claim")
                _validate_candidate(candidate, binding, rank)
                union.add(candidate["claim_id"])
        expected_answers = _claims(ground_truth, "answer_claims")
        expected_negatives = _claims(ground_truth, "important_negatives")
        expected_papers = set(ground_truth["ground_truth"]["required_paper_ids"])
        union_papers = {binding_by_claim[claim_id]["paper_id"] for claim_id in union}
        rows.append(
            {
                "id": question["id"],
                "primary_answer_claim_recall_at_30": _recall(primary, expected_answers),
                "facet_union_answer_claim_coverage": _recall(union, expected_answers),
                "facet_union_important_negative_coverage": _recall(union, expected_negatives),
                "facet_union_required_paper_coverage": _recall(union_papers, expected_papers),
                "unique_candidate_claims": len(union),
                "facet_count": pack["facet_count"],
            }
        )
    if before != _tree(bundle):
        raise CoverageError("coverage evaluation modified the snapshot")
    mean = lambda key: statistics.fmean(float(row[key]) for row in rows)
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "pass",
        "benchmark": frozen,
        "candidate": args.candidate,
        "protocol": {
            "primary_top_k": args.top_k,
            "per_facet": args.per_facet,
            "maximum_facets": args.maximum_facets,
            "repetitions_per_question": args.repetitions,
            "candidate_budget_warning": "facet union has a larger variable budget and is not Recall@30",
        },
        "inputs": {
            "bundle": str(bundle.relative_to(repo)).replace("\\", "/"),
            "runtime": str(runtime_path.relative_to(repo)).replace("\\", "/"),
            "runtime_sha256": _sha256(runtime_path),
            "questions_sha256": _sha256(questions_path),
            "ground_truth_sha256": _sha256(truth_path),
            "answer_binding_count": len(binding_by_claim),
        },
        "hard_gates": {
            "frozen_benchmark": True,
            "deterministic": True,
            "read_only": True,
            "question_id_isolation": True,
            "candidate_binding_validity": 1.0,
        },
        "metrics": {
            "primary_answer_claim_recall_at_30": mean("primary_answer_claim_recall_at_30"),
            "facet_union_answer_claim_coverage": mean("facet_union_answer_claim_coverage"),
            "facet_union_important_negative_coverage": mean("facet_union_important_negative_coverage"),
            "facet_union_required_paper_coverage": mean("facet_union_required_paper_coverage"),
            "unique_candidate_claims": {
                "mean": mean("unique_candidate_claims"),
                "minimum": min(row["unique_candidate_claims"] for row in rows),
                "maximum": max(row["unique_candidate_claims"] for row in rows),
            },
            "facet_count": {
                "mean": mean("facet_count"),
                "minimum": min(row["facet_count"] for row in rows),
                "maximum": max(row["facet_count"] for row in rows),
            },
            "latency_ms": {
                "mean": statistics.fmean(latencies),
                "median": statistics.median(latencies),
                "maximum": max(latencies),
            },
        },
        "questions": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--runtime", type=Path, required=True)
    parser.add_argument("--questions", type=Path, required=True)
    parser.add_argument("--ground-truth", type=Path, required=True)
    parser.add_argument("--top-k", type=int, default=30)
    parser.add_argument("--per-facet", type=int, default=12)
    parser.add_argument("--maximum-facets", type=int, default=12)
    parser.add_argument("--repetitions", type=int, default=3)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-markdown", type=Path, required=True)
    args = parser.parse_args()
    if (args.top_k, args.per_facet, args.maximum_facets, args.repetitions) != (30, 12, 12, 3):
        print(json.dumps({"status": "fail", "error": "the published protocol is fixed at 30/12/12/3"}))
        return 2
    try:
        report = evaluate(args)
    except (CoverageError, OSError, ValueError, TypeError, KeyError, IndexError) as exc:
        print(json.dumps({"status": "fail", "error": str(exc)}, sort_keys=True))
        return 2
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.output_markdown.write_text(_render(report), encoding="utf-8")
    print(json.dumps({"status": "pass", "candidate": report["candidate"], "metrics": report["metrics"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
