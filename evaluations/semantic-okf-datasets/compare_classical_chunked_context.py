#!/usr/bin/env python3
"""Compare classical expert payloads with budgeted exact-chunk contexts.

This is a deterministic retrospective regression, not a semantic promotion gate.
It uses disclosed benchmark questions only after the candidate implementation is
frozen. The report therefore measures retrieval parity, evidence integrity, guard
behavior, and provider-visible context size without claiming answer equivalence.
"""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import statistics
import sys
from types import ModuleType
from typing import Any, Mapping, Sequence


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_JSON_REPORT = (
    REPO_ROOT
    / "evaluations"
    / "semantic-okf-datasets"
    / "reports"
    / "20260814-classical-chunked-context-efficiency.json"
)
DEFAULT_MARKDOWN_REPORT = DEFAULT_JSON_REPORT.with_suffix(".md")
MODES = ("fusion",)
TOP_K = 10


@dataclass(frozen=True)
class DatasetBinding:
    """Bind one descriptor to the before and after generated experts."""

    dataset_id: str
    descriptor: str
    baseline_expert: str
    chunked_expert: str


DATASETS = (
    DatasetBinding(
        dataset_id="graphrag-papers-40",
        descriptor="evaluations/semantic-okf-datasets/datasets/graphrag-papers-40.json",
        baseline_expert="graphrag-classical-integrated-expert",
        chunked_expert="graphrag-classical-chunked-expert",
    ),
    DatasetBinding(
        dataset_id="astro-40",
        descriptor="evaluations/semantic-okf-datasets/datasets/astro-40.json",
        baseline_expert="astro-classical-integrated-expert",
        chunked_expert="astro-classical-chunked-expert",
    ),
    DatasetBinding(
        dataset_id="quantum-error-correction-papers-40",
        descriptor=(
            "evaluations/semantic-okf-datasets/datasets/"
            "quantum-error-correction-papers-40.json"
        ),
        baseline_expert="qec-classical-integrated-expert",
        chunked_expert="qec-classical-chunked-expert",
    ),
)


class ComparisonError(ValueError):
    """Describe a failed deterministic comparison invariant."""


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ComparisonError(f"Expected a JSON object: {path}")
    return value


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ComparisonError(f"Expected a JSON object at {path}:{number}")
        rows.append(value)
    return rows


def _load_helper(path: Path, name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ComparisonError(f"Could not import generated helper: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(path.parent))
    try:
        spec.loader.exec_module(module)
    finally:
        sys.path.remove(str(path.parent))
    return module


def _canonical_output(value: Mapping[str, Any]) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        allow_nan=False,
    ) + "\n"


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _percentile(values: Sequence[int], fraction: float) -> int:
    if not values:
        return 0
    ordered = sorted(values)
    index = max(0, math.ceil(len(ordered) * fraction) - 1)
    return ordered[index]


def _size_summary(values: Sequence[int]) -> dict[str, Any]:
    return {
        "total": sum(values),
        "minimum": min(values, default=0),
        "median": round(statistics.median(values), 2) if values else 0,
        "p95": _percentile(values, 0.95),
        "maximum": max(values, default=0),
        "mean": round(statistics.fmean(values), 2) if values else 0,
    }


def _reduction(before: int, after: int) -> float:
    if before <= 0:
        return 0.0
    return round(1.0 - (after / before), 8)


def _questions(binding: DatasetBinding) -> list[dict[str, Any]]:
    descriptor = _load_json(REPO_ROOT / binding.descriptor)
    if descriptor.get("dataset_id") != binding.dataset_id:
        raise ComparisonError(f"Dataset descriptor identity drift: {binding.dataset_id}")
    questions = descriptor.get("questions")
    if not isinstance(questions, dict) or not isinstance(questions.get("path"), str):
        raise ComparisonError(f"Dataset questions binding is invalid: {binding.dataset_id}")
    rows = _load_jsonl(REPO_ROOT / questions["path"])
    if len(rows) != questions.get("count"):
        raise ComparisonError(f"Question count drift: {binding.dataset_id}")
    return rows


def _baseline_payload(
    module: ModuleType,
    snapshot: Any,
    records: Sequence[Mapping[str, Any]],
    verification: Mapping[str, Any],
    query: str,
    mode: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    raw = module.search_snapshot(snapshot, query, mode, TOP_K)
    payload = json.loads(json.dumps(raw))
    by_identity = {
        (str(row["source_id"]), str(row["record_id"])): row for row in records
    }
    counts = Counter(str(row["source_id"]) for row in records)
    layout = module._concept_layout()
    augmented = []
    for result in payload["results"]:
        record = by_identity.get((str(result["source_id"]), str(result["record_id"])))
        if record is None:
            raise ComparisonError("Baseline result is orphaned from its ledger")
        location = module._evidence_location(record, layout=layout, source_counts=counts)
        augmented.append({**result, **location})
    payload["results"] = augmented
    payload["expert"] = {
        "skill_name": verification["skill_name"],
        "knowledge_tree_sha256": verification["knowledge_tree_sha256"],
        "read_only": True,
        "citation_contract": "physical-path-and-optional-record-anchor",
    }
    return raw, payload


def _chunked_payload(
    module: ModuleType,
    snapshot: Any,
    records: Sequence[Mapping[str, Any]],
    projection: Any,
    verification: Mapping[str, Any],
    query: str,
    mode: str,
    *,
    budget_tokens: int | None,
) -> dict[str, Any]:
    payload = module.select_context(
        snapshot,
        projection,
        records,
        query,
        mode,
        budget_tokens=budget_tokens,
        maximum_chunks=None,
    )
    by_identity = {
        (str(row["source_id"]), str(row["record_id"])): row for row in records
    }
    counts = Counter(str(row["source_id"]) for row in records)
    layout = module._concept_layout()
    payload["chunks"] = [
        module._chunk_with_evidence(
            row,
            records=by_identity,
            layout=layout,
            source_counts=counts,
        )
        for row in payload["chunks"]
    ]
    payload["expert"] = {
        "skill_name": verification["skill_name"],
        "knowledge_tree_sha256": verification["knowledge_tree_sha256"],
        "context_plan_sha256": verification["context_plan_sha256"],
        "read_only": True,
        "citation_contract": "physical-path-anchor-and-record-character-range",
    }
    return payload


def _assert_exact_chunks(
    payload: Mapping[str, Any],
    records: Sequence[Mapping[str, Any]],
) -> int:
    by_identity = {
        (str(row["source_id"]), str(row["record_id"])): row for row in records
    }
    verified = 0
    for chunk in payload.get("chunks", []):
        if not isinstance(chunk, Mapping):
            raise ComparisonError("Context contains a non-object chunk")
        identity = (str(chunk["source_id"]), str(chunk["record_id"]))
        record = by_identity.get(identity)
        if record is None:
            raise ComparisonError(f"Context chunk is orphaned: {identity!r}")
        start = int(chunk["record_char_start"])
        end = int(chunk["record_char_end"])
        expected = str(record["body"])[start:end]
        if expected != chunk.get("text"):
            raise ComparisonError(f"Context span reconstruction drift: {chunk['chunk_id']}")
        if _sha256_text(expected) != chunk.get("text_sha256"):
            raise ComparisonError(f"Context span digest drift: {chunk['chunk_id']}")
        if not isinstance(chunk.get("citation"), str) or not chunk["citation"]:
            raise ComparisonError(f"Context citation is missing: {chunk['chunk_id']}")
        verified += 1
    return verified


def _compare_dataset(binding: DatasetBinding) -> dict[str, Any]:
    experts = REPO_ROOT / "evaluations" / "semantic-okf-datasets" / "generated" / "experts"
    baseline_path = experts / binding.baseline_expert / "scripts" / "query_expert_knowledge.py"
    chunked_path = experts / binding.chunked_expert / "scripts" / "query_expert_knowledge.py"
    baseline = _load_helper(baseline_path, f"baseline_{binding.dataset_id.replace('-', '_')}")
    chunked = _load_helper(chunked_path, f"chunked_{binding.dataset_id.replace('-', '_')}")

    _, baseline_snapshot, baseline_records, baseline_verification = baseline._verify(
        deep_validation=False
    )
    _, chunked_snapshot, chunked_records, projection, chunked_verification = chunked._verify(
        deep_validation=False
    )
    if baseline_verification["knowledge_tree_sha256"] != chunked_verification["knowledge_tree_sha256"]:
        raise ComparisonError(f"Knowledge tree changed: {binding.dataset_id}")
    if baseline_snapshot.index_sha256 != chunked_snapshot.index_sha256:
        raise ComparisonError(f"Classical index changed: {binding.dataset_id}")

    maximum_budget = int(projection.index["plan"]["selection"]["maximum_budget_tokens"])
    estimator = sys.modules[chunked.select_context.__module__].estimate_tokens
    before_bytes: list[int] = []
    after_bytes: list[int] = []
    before_tokens: list[int] = []
    after_tokens: list[int] = []
    returned_chunks: list[int] = []
    question_rows: list[dict[str, Any]] = []
    parity_cells = 0
    default_guard_passes = 0
    effective_guard_passes = 0
    escalations = 0
    exact_chunks = 0

    questions = _questions(binding)
    for question in questions:
        query = question.get("question")
        question_id = question.get("id")
        if not isinstance(query, str) or not query.strip() or not isinstance(question_id, str):
            raise ComparisonError(f"Invalid question row: {binding.dataset_id}")
        for mode in MODES:
            baseline_raw, baseline_payload = _baseline_payload(
                baseline,
                baseline_snapshot,
                baseline_records,
                baseline_verification,
                query,
                mode,
            )
            chunked_raw = chunked.search_snapshot(chunked_snapshot, query, mode, TOP_K)
            if baseline_raw != chunked_raw:
                raise ComparisonError(
                    f"Full classical retrieval parity failed: {binding.dataset_id}/{question_id}/{mode}"
                )
            parity_cells += 1

            selected = _chunked_payload(
                chunked,
                chunked_snapshot,
                chunked_records,
                projection,
                chunked_verification,
                query,
                mode,
                budget_tokens=None,
            )
            default_complete = bool(selected["quality_guard"]["complete"])
            default_guard_passes += int(default_complete)
            escalated = False
            if not default_complete:
                selected = _chunked_payload(
                    chunked,
                    chunked_snapshot,
                    chunked_records,
                    projection,
                    chunked_verification,
                    query,
                    mode,
                    budget_tokens=maximum_budget,
                )
                escalated = True
                escalations += 1
            effective_complete = bool(selected["quality_guard"]["complete"])
            effective_guard_passes += int(effective_complete)
            exact_chunks += _assert_exact_chunks(selected, chunked_records)

            baseline_text = _canonical_output(baseline_payload)
            context_text = chunked.format_context_markdown(selected)
            baseline_size = len(baseline_text.encode("utf-8"))
            context_size = len(context_text.encode("utf-8"))
            baseline_proxy = int(estimator(baseline_text))
            context_proxy = int(estimator(context_text))
            before_bytes.append(baseline_size)
            after_bytes.append(context_size)
            before_tokens.append(baseline_proxy)
            after_tokens.append(context_proxy)
            returned_chunks.append(len(selected["chunks"]))
            question_rows.append(
                {
                    "question_id": question_id,
                    "mode": mode,
                    "full_retrieval_parity": True,
                    "default_guard_complete": default_complete,
                    "escalated": escalated,
                    "effective_guard_complete": effective_complete,
                    "query_coverage": selected["quality_guard"]["query_coverage"],
                    "evidence_identities": selected["quality_guard"]["evidence_identities"],
                    "returned_chunks": len(selected["chunks"]),
                    "baseline_bytes": baseline_size,
                    "context_bytes": context_size,
                    "byte_reduction": _reduction(baseline_size, context_size),
                    "baseline_estimated_tokens": baseline_proxy,
                    "context_estimated_tokens": context_proxy,
                    "estimated_token_reduction": _reduction(baseline_proxy, context_proxy),
                }
            )

    cells = len(question_rows)
    return {
        "dataset_id": binding.dataset_id,
        "questions": len(questions),
        "modes": list(MODES),
        "cells": cells,
        "baseline_expert": binding.baseline_expert,
        "chunked_expert": binding.chunked_expert,
        "knowledge_tree_sha256": baseline_verification["knowledge_tree_sha256"],
        "classical_index_sha256": baseline_snapshot.index_sha256,
        "context_plan_sha256": chunked_verification["context_plan_sha256"],
        "full_retrieval_parity": {
            "passing_cells": parity_cells,
            "total_cells": cells,
            "rate": round(parity_cells / cells, 8),
        },
        "quality_guard": {
            "default_passing_cells": default_guard_passes,
            "default_pass_rate": round(default_guard_passes / cells, 8),
            "escalated_cells": escalations,
            "effective_passing_cells": effective_guard_passes,
            "effective_pass_rate": round(effective_guard_passes / cells, 8),
        },
        "exact_chunks_verified": exact_chunks,
        "returned_chunks": _size_summary(returned_chunks),
        "baseline_bytes": _size_summary(before_bytes),
        "context_bytes": _size_summary(after_bytes),
        "byte_reduction": _reduction(sum(before_bytes), sum(after_bytes)),
        "baseline_estimated_tokens": _size_summary(before_tokens),
        "context_estimated_tokens": _size_summary(after_tokens),
        "estimated_token_reduction": _reduction(sum(before_tokens), sum(after_tokens)),
        "question_results": question_rows,
    }


def _aggregate(datasets: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    cells = sum(int(row["cells"]) for row in datasets)
    parity = sum(int(row["full_retrieval_parity"]["passing_cells"]) for row in datasets)
    default_passes = sum(int(row["quality_guard"]["default_passing_cells"]) for row in datasets)
    effective_passes = sum(int(row["quality_guard"]["effective_passing_cells"]) for row in datasets)
    before_bytes = sum(int(row["baseline_bytes"]["total"]) for row in datasets)
    after_bytes = sum(int(row["context_bytes"]["total"]) for row in datasets)
    before_tokens = sum(int(row["baseline_estimated_tokens"]["total"]) for row in datasets)
    after_tokens = sum(int(row["context_estimated_tokens"]["total"]) for row in datasets)
    return {
        "datasets": len(datasets),
        "questions": sum(int(row["questions"]) for row in datasets),
        "cells": cells,
        "full_retrieval_parity_rate": round(parity / cells, 8),
        "default_guard_pass_rate": round(default_passes / cells, 8),
        "effective_guard_pass_rate": round(effective_passes / cells, 8),
        "exact_chunks_verified": sum(int(row["exact_chunks_verified"]) for row in datasets),
        "baseline_bytes": before_bytes,
        "context_bytes": after_bytes,
        "byte_reduction": _reduction(before_bytes, after_bytes),
        "baseline_estimated_tokens": before_tokens,
        "context_estimated_tokens": after_tokens,
        "estimated_token_reduction": _reduction(before_tokens, after_tokens),
    }


def compare() -> dict[str, Any]:
    """Run the closed deterministic context-efficiency comparison."""

    datasets = [_compare_dataset(binding) for binding in DATASETS]
    return {
        "schema_version": "classical-chunked-context-efficiency/1.0",
        "status": "pass",
        "evaluated_at": "2026-08-14",
        "evaluation_kind": "retrospective-deterministic-regression",
        "promotion_claim": False,
        "scope": {
            "retrieval_modes": list(MODES),
            "baseline_top_k": TOP_K,
            "context_policy": "default-budget-then-one-maximum-budget-escalation",
            "token_measurement": (
                "deterministic lexical-or-UTF-8-bytes-divided-by-four proxy; "
                "not a provider tokenizer"
            ),
        },
        "aggregate": _aggregate(datasets),
        "datasets": datasets,
        "limitations": [
            "The questions are disclosed retrospective fixtures, not a sealed semantic holdout.",
            "Retrieval parity and exact reconstruction do not prove answer-quality equivalence.",
            "Estimated tokens are a deterministic conservative proxy, not billed provider tokens.",
        ],
    }


def _markdown(report: Mapping[str, Any]) -> str:
    aggregate = report["aggregate"]
    lines = [
        "# Classical chunked context efficiency",
        "",
        "Status: **pass**",
        "",
        "This is a deterministic retrospective regression. It verifies unchanged classical",
        "retrieval, exact evidence reconstruction, citation presence, context guard behavior,",
        "and provider-visible payload size. It is not a sealed semantic promotion result.",
        "",
        "## Aggregate",
        "",
        f"- Datasets: {aggregate['datasets']}",
        f"- Questions/cells: {aggregate['questions']}/{aggregate['cells']}",
        f"- Full classical retrieval parity: {aggregate['full_retrieval_parity_rate']:.2%}",
        f"- Default quality-guard pass rate: {aggregate['default_guard_pass_rate']:.2%}",
        f"- Effective quality-guard pass rate: {aggregate['effective_guard_pass_rate']:.2%}",
        f"- Exact chunks reconstructed and digest-checked: {aggregate['exact_chunks_verified']}",
        f"- Context byte reduction: {aggregate['byte_reduction']:.2%}",
        f"- Estimated-token reduction: {aggregate['estimated_token_reduction']:.2%}",
        "",
        "## Per dataset",
        "",
        "| Dataset | Cells | Retrieval parity | Default guard | Effective guard | Byte reduction | Estimated-token reduction |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in report["datasets"]:
        lines.append(
            f"| {row['dataset_id']} | {row['cells']} | "
            f"{row['full_retrieval_parity']['rate']:.2%} | "
            f"{row['quality_guard']['default_pass_rate']:.2%} | "
            f"{row['quality_guard']['effective_pass_rate']:.2%} | "
            f"{row['byte_reduction']:.2%} | {row['estimated_token_reduction']:.2%} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation boundary",
            "",
            "The candidate retains the complete immutable knowledge tree and the original",
            "classical search path. The compact context is a derived discovery projection;",
            "linked chunks can be hydrated from exact ledger character ranges, and full search",
            "remains available as a fail-closed diagnostic fallback.",
            "",
            "The token metric is the skill's deterministic lexical/UTF-8 proxy. It must not be",
            "reported as native provider billing or as a semantic-quality result.",
            "",
        ]
    )
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json-report", type=Path, default=DEFAULT_JSON_REPORT)
    parser.add_argument("--markdown-report", type=Path, default=DEFAULT_MARKDOWN_REPORT)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report = compare()
    args.json_report.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_report.parent.mkdir(parents=True, exist_ok=True)
    args.json_report.write_text(
        json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    args.markdown_report.write_text(_markdown(report), encoding="utf-8", newline="\n")
    print(json.dumps(report["aggregate"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
