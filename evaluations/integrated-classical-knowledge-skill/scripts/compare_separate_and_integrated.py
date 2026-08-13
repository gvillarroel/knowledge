#!/usr/bin/env python3
"""Compare generated classical knowledge skills with the separate classical stack."""

from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from types import ModuleType
from typing import Any, Iterator


SCHEMA_VERSION = "integrated-classical-knowledge-skill-comparison/1.0"
MODES = ("bm25", "topic", "association", "fusion")
TOP_K = 10
EXPECTED_QUESTIONS = 40
LOCATION_FIELDS = {
    "logical_concept_path",
    "physical_concept_path",
    "evidence_path",
    "evidence_anchor",
    "citation",
}


class ComparisonError(ValueError):
    """Describe an invalid artifact or a baseline-parity failure."""


@dataclass(frozen=True)
class Case:
    """Bind one canonical question set to separate and integrated artifacts."""

    dataset_id: str
    questions: str
    baseline: str
    expert: str


CASES = (
    Case(
        dataset_id="graphrag-papers-40",
        questions="evaluations/semantic-okf-adaptive/retrieval-questions.jsonl",
        baseline=(
            "evaluations/semantic-okf-datasets/generated/"
            "integrated-classical-comparison/graphrag-papers-40/baseline"
        ),
        expert=(
            "evaluations/semantic-okf-datasets/generated/experts/"
            "graphrag-classical-integrated-expert"
        ),
    ),
    Case(
        dataset_id="astro-40",
        questions="evaluations/semantic-okf-astro/benchmark/retrieval-questions.jsonl",
        baseline=(
            "evaluations/semantic-okf-datasets/generated/"
            "integrated-classical-comparison/astro-40/baseline"
        ),
        expert=(
            "evaluations/semantic-okf-datasets/generated/experts/"
            "astro-classical-integrated-expert"
        ),
    ),
    Case(
        dataset_id="quantum-error-correction-papers-40",
        questions=(
            "evaluations/quantum-error-correction-papers/benchmark/"
            "retrieval-questions.jsonl"
        ),
        baseline=(
            "evaluations/semantic-okf-datasets/generated/"
            "integrated-classical-comparison/"
            "quantum-error-correction-papers-40/baseline"
        ),
        expert=(
            "evaluations/semantic-okf-datasets/generated/experts/"
            "qec-classical-integrated-expert"
        ),
    ),
)


def canonical_json(value: Any) -> str:
    """Serialize JSON deterministically and reject non-finite values."""

    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def sha256_bytes(value: bytes) -> str:
    """Return a lowercase SHA-256 digest."""

    return hashlib.sha256(value).hexdigest()


def regular_files(root: Path) -> Iterator[Path]:
    """Yield a closed, sorted tree of regular files."""

    if not root.is_dir() or root.is_symlink():
        raise ComparisonError(f"Directory is absent or unsafe: {root}")
    files: list[Path] = []
    for path in root.rglob("*"):
        if path.is_symlink():
            raise ComparisonError(f"Symlink is not allowed: {path}")
        if path.is_file():
            files.append(path)
        elif not path.is_dir():
            raise ComparisonError(f"Special file is not allowed: {path}")
    yield from sorted(files, key=lambda item: item.relative_to(root).as_posix())


def tree_binding(root: Path) -> tuple[str, dict[str, str]]:
    """Hash exact paths, lengths, and bytes and return a per-file map."""

    digest = hashlib.sha256()
    files: dict[str, str] = {}
    for path in regular_files(root):
        relative = path.relative_to(root).as_posix()
        data = path.read_bytes()
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(str(len(data)).encode("ascii"))
        digest.update(b"\0")
        digest.update(data)
        digest.update(b"\0")
        files[relative] = sha256_bytes(data)
    return digest.hexdigest(), files


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    """Load a closed JSONL file with useful line diagnostics."""

    if not path.is_file() or path.is_symlink():
        raise ComparisonError(f"Question set is absent or unsafe: {path}")
    rows: list[dict[str, Any]] = []
    for line_number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            raise ComparisonError(f"Blank JSONL line at {path}:{line_number}")
        try:
            value = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ComparisonError(f"Invalid JSON at {path}:{line_number}: {exc}") from exc
        if not isinstance(value, dict):
            raise ComparisonError(f"Question at {path}:{line_number} is not an object")
        rows.append(value)
    if len(rows) != EXPECTED_QUESTIONS:
        raise ComparisonError(
            f"Expected {EXPECTED_QUESTIONS} questions at {path}; found {len(rows)}"
        )
    identifiers = [row.get("id") for row in rows]
    if any(not isinstance(item, str) or not item for item in identifiers):
        raise ComparisonError(f"Question identifiers are invalid at {path}")
    if len(set(identifiers)) != len(identifiers):
        raise ComparisonError(f"Question identifiers are not unique at {path}")
    if any(not isinstance(row.get("question"), str) or not row["question"].strip() for row in rows):
        raise ComparisonError(f"Questions are invalid at {path}")
    return rows


def load_module(path: Path, name: str) -> ModuleType:
    """Load one Python file under an isolated module name."""

    if not path.is_file() or path.is_symlink():
        raise ComparisonError(f"Runtime is absent or unsafe: {path}")
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ComparisonError(f"Cannot load runtime: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def load_expert_query(expert: Path, generated_runtime: ModuleType, name: str) -> ModuleType:
    """Load the actual generated query helper against its embedded runtime."""

    sentinel = object()
    previous: object = sys.modules.get("_classical_snapshot", sentinel)
    sys.modules["_classical_snapshot"] = generated_runtime
    try:
        return load_module(expert / "scripts" / "query_expert_knowledge.py", name)
    finally:
        if previous is sentinel:
            sys.modules.pop("_classical_snapshot", None)
        else:
            sys.modules["_classical_snapshot"] = previous  # type: ignore[assignment]


def record_identity(row: dict[str, Any]) -> tuple[str, str]:
    """Return the exact ledger identity used by the generated helper."""

    source_id = row.get("source_id")
    record_id = row.get("record_id")
    if not isinstance(source_id, str) or not isinstance(record_id, str):
        raise ComparisonError("Ledger identity is invalid")
    return source_id, record_id


def strip_integrated_fields(payload: dict[str, Any]) -> dict[str, Any]:
    """Project an integrated public-query payload onto the classical contract."""

    projected = {key: value for key, value in payload.items() if key != "expert"}
    results = projected.get("results")
    if not isinstance(results, list):
        raise ComparisonError("Integrated public query has no result array")
    projected["results"] = [
        {key: value for key, value in row.items() if key not in LOCATION_FIELDS}
        for row in results
    ]
    return projected


def compare_case(repo_root_raw: str, case: Case) -> dict[str, Any]:
    """Run one exhaustive dataset comparison in an isolated process."""

    repo_root = Path(repo_root_raw).resolve()
    baseline = repo_root / case.baseline
    expert = repo_root / case.expert
    knowledge = expert / "references" / "knowledge"
    questions = load_jsonl(repo_root / case.questions)
    runtime_source = (
        repo_root / "skills" / "consult-semantic-okf-classical" / "scripts"
        / "_classical_snapshot.py"
    )
    generated_source = expert / "scripts" / "_classical_snapshot.py"
    runtime_sha256 = sha256_bytes(runtime_source.read_bytes())
    generated_runtime_sha256 = sha256_bytes(generated_source.read_bytes())
    if runtime_sha256 != generated_runtime_sha256:
        raise ComparisonError(f"Runtime bytes drift for {case.dataset_id}")

    baseline_tree_sha256, baseline_files = tree_binding(baseline)
    knowledge_tree_sha256, knowledge_files = tree_binding(knowledge)
    if baseline_files != knowledge_files or baseline_tree_sha256 != knowledge_tree_sha256:
        raise ComparisonError(f"Knowledge bytes drift for {case.dataset_id}")

    suffix = case.dataset_id.replace("-", "_")
    separate_runtime = load_module(runtime_source, f"_separate_classical_{suffix}")
    integrated_runtime = load_module(generated_source, f"_integrated_classical_{suffix}")
    expert_query = load_expert_query(
        expert,
        integrated_runtime,
        f"_integrated_query_{suffix}",
    )
    separate_snapshot = separate_runtime.load_snapshot(baseline, deep_validation=True)
    manifest, integrated_snapshot, records, verification = expert_query._verify(
        deep_validation=True
    )
    if verification.get("knowledge_tree_sha256") != knowledge_tree_sha256:
        raise ComparisonError(f"Generated manifest tree binding drift for {case.dataset_id}")
    if manifest.get("generation", {}).get("default_query_mode") != "fusion":
        raise ComparisonError(f"Generated default route drift for {case.dataset_id}")

    by_identity = {record_identity(row): row for row in records}
    if len(by_identity) != len(records):
        raise ComparisonError(f"Duplicate ledger identity for {case.dataset_id}")
    source_counts = Counter(str(row["source_id"]) for row in records)
    concept_layout = verification["concept_layout"]
    all_locations = [
        expert_query._evidence_location(
            row,
            layout=concept_layout,
            source_counts=source_counts,
        )
        for row in records
    ]
    if any(not location.get("citation") for location in all_locations):
        raise ComparisonError(f"Empty evidence citation for {case.dataset_id}")

    exact_payload_cells = 0
    exact_ranking_cells = 0
    returned_hits = 0
    integrated_citation_hits = 0
    legacy_logical_path_hits = 0
    public_probe_cells = 0
    mismatches: list[dict[str, Any]] = []
    first_fusion_payload: dict[str, Any] | None = None

    for question in questions:
        query = question["question"]
        for mode in MODES:
            separate_payload = separate_runtime.search_snapshot(
                separate_snapshot,
                query,
                mode,
                TOP_K,
            )
            integrated_payload = integrated_runtime.search_snapshot(
                integrated_snapshot,
                query,
                mode,
                TOP_K,
            )
            separate_ids = [row["document_id"] for row in separate_payload["results"]]
            integrated_ids = [row["document_id"] for row in integrated_payload["results"]]
            ranking_equal = separate_ids == integrated_ids
            payload_equal = canonical_json(separate_payload) == canonical_json(integrated_payload)
            exact_ranking_cells += int(ranking_equal)
            exact_payload_cells += int(payload_equal)
            if not ranking_equal or not payload_equal:
                mismatches.append(
                    {
                        "question_id": question["id"],
                        "mode": mode,
                        "ranking_equal": ranking_equal,
                        "payload_equal": payload_equal,
                    }
                )
            if mode == "fusion" and first_fusion_payload is None:
                first_fusion_payload = integrated_payload
            for hit in integrated_payload["results"]:
                returned_hits += 1
                identity = (hit.get("source_id"), hit.get("record_id"))
                record = by_identity.get(identity)
                if record is None:
                    raise ComparisonError(
                        f"Orphaned hit for {case.dataset_id}: {identity!r}"
                    )
                logical = knowledge.joinpath(*Path(record["concept_path"]).parts)
                legacy_logical_path_hits += int(logical.is_file() and not logical.is_symlink())
                location = expert_query._evidence_location(
                    record,
                    layout=concept_layout,
                    source_counts=source_counts,
                )
                evidence_raw = location.get("evidence_path")
                if not isinstance(evidence_raw, str) or not evidence_raw.startswith(
                    "references/knowledge/"
                ):
                    raise ComparisonError(f"Invalid evidence path for {case.dataset_id}")
                target = expert.joinpath(*Path(evidence_raw).parts)
                if not target.is_file() or target.is_symlink():
                    raise ComparisonError(f"Unresolvable evidence path for {case.dataset_id}")
                integrated_citation_hits += 1

    if first_fusion_payload is None:
        raise ComparisonError(f"Fusion probe was not captured for {case.dataset_id}")
    public_payload = expert_query.search(
        questions[0]["question"],
        "fusion",
        TOP_K,
        source_ids=(),
        concept_ids=(),
        concept_types=(),
    )
    public_expected = json.loads(canonical_json(first_fusion_payload))
    public_expected["snapshot"]["deep_validation"] = False
    if canonical_json(strip_integrated_fields(public_payload)) != canonical_json(public_expected):
        raise ComparisonError(f"Public fusion wrapper drift for {case.dataset_id}")
    public_probe_cells = 1

    cell_count = len(questions) * len(MODES)
    if mismatches:
        raise ComparisonError(
            f"Classical payload parity failed for {case.dataset_id}: {mismatches[:3]!r}"
        )
    if integrated_citation_hits != returned_hits:
        raise ComparisonError(f"Evidence coverage failed for {case.dataset_id}")
    return {
        "dataset_id": case.dataset_id,
        "question_count": len(questions),
        "route_count": len(MODES),
        "query_route_cells": cell_count,
        "top_k": TOP_K,
        "exact_ranking_cells": exact_ranking_cells,
        "exact_payload_cells": exact_payload_cells,
        "ranking_mismatches": cell_count - exact_ranking_cells,
        "payload_mismatches": cell_count - exact_payload_cells,
        "returned_hits": returned_hits,
        "integrated_citation_hits": integrated_citation_hits,
        "legacy_logical_path_hits": legacy_logical_path_hits,
        "citation_resolution_gain_hits": integrated_citation_hits - legacy_logical_path_hits,
        "authoritative_records": len(records),
        "authoritative_evidence_records_verified": len(all_locations),
        "knowledge_files": len(knowledge_files),
        "knowledge_tree_sha256": knowledge_tree_sha256,
        "knowledge_bytes_equal": True,
        "runtime_sha256": runtime_sha256,
        "runtime_bytes_equal": True,
        "public_fusion_probe_cells": public_probe_cells,
        "default_query_mode": "fusion",
        "mismatches": mismatches,
    }


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Create one deterministic cross-dataset result."""

    totals = {
        "dataset_count": len(rows),
        "question_count": sum(row["question_count"] for row in rows),
        "query_route_cells": sum(row["query_route_cells"] for row in rows),
        "exact_ranking_cells": sum(row["exact_ranking_cells"] for row in rows),
        "exact_payload_cells": sum(row["exact_payload_cells"] for row in rows),
        "ranking_mismatches": sum(row["ranking_mismatches"] for row in rows),
        "payload_mismatches": sum(row["payload_mismatches"] for row in rows),
        "returned_hits": sum(row["returned_hits"] for row in rows),
        "integrated_citation_hits": sum(row["integrated_citation_hits"] for row in rows),
        "legacy_logical_path_hits": sum(row["legacy_logical_path_hits"] for row in rows),
        "citation_resolution_gain_hits": sum(
            row["citation_resolution_gain_hits"] for row in rows
        ),
        "authoritative_records": sum(row["authoritative_records"] for row in rows),
        "authoritative_evidence_records_verified": sum(
            row["authoritative_evidence_records_verified"] for row in rows
        ),
        "knowledge_files": sum(row["knowledge_files"] for row in rows),
        "public_fusion_probe_cells": sum(row["public_fusion_probe_cells"] for row in rows),
    }
    totals["exact_payload_rate"] = round(
        totals["exact_payload_cells"] / totals["query_route_cells"], 6
    )
    totals["integrated_citation_resolution_rate"] = round(
        totals["integrated_citation_hits"] / totals["returned_hits"], 6
    )
    totals["legacy_logical_path_resolution_rate"] = round(
        totals["legacy_logical_path_hits"] / totals["returned_hits"], 6
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "pass",
        "comparison": {
            "baseline": "separate build-semantic-okf-classical plus consult-semantic-okf-classical",
            "candidate": "build-classical-knowledge-skill generated expert",
            "routes": list(MODES),
            "top_k": TOP_K,
            "payload_equality_scope": (
                "complete classical query payload, including ranks, scores, expansions, "
                "filters, and retrieved text"
            ),
        },
        "datasets": rows,
        "totals": totals,
        "boundary": (
            "This is a deterministic build, retrieval, and citation parity evaluation. "
            "It is not a new model-judged Harbor answer-quality run."
        ),
    }


def render_markdown(report: dict[str, Any]) -> str:
    """Render the compact evidence-first parity report."""

    lines = [
        "# Integrated Classical Knowledge Skill Parity Verification",
        "",
        "| Dataset | Records | Questions | Query-route cells | Exact payloads | Rank mismatches | Hit citations | Legacy logical paths | Citation gain | Knowledge files equal | Runtime bytes equal |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in report["datasets"]:
        lines.append(
            "| {dataset_id} | {authoritative_records} | {question_count} | "
            "{query_route_cells} | {exact_payload_cells}/{query_route_cells} | "
            "{ranking_mismatches} | {integrated_citation_hits}/{returned_hits} | "
            "{legacy_logical_path_hits}/{returned_hits} | "
            "+{citation_resolution_gain_hits} | {knowledge_files}/{knowledge_files} | 1/1 |".format(
                **row
            )
        )
    totals = report["totals"]
    lines.extend(
        [
            "",
            (
                f"Result: **PASS**. The generated experts matched all "
                f"{totals['query_route_cells']} separate-stack query payloads exactly "
                f"across {totals['question_count']} canonical questions and four routes, "
                f"with {totals['ranking_mismatches']} ranking mismatches and "
                f"{totals['payload_mismatches']} payload mismatches."
            ),
            "",
            (
                f"All {totals['authoritative_evidence_records_verified']} authoritative "
                f"records and all {totals['integrated_citation_hits']} retained hits have "
                "verified physical citations. The generated citation contract resolves "
                f"{totals['citation_resolution_gain_hits']} retained hits whose legacy "
                "logical `concept_path` is intentionally not a physical file in the "
                "source-packed layout."
            ),
            "",
            "Each dataset also passed a public generated-skill fusion query, deep snapshot validation, exact knowledge-tree comparison, and exact classical-runtime comparison. The generated skills default to `fusion` while retaining explicit `bm25`, `topic`, `association`, and `fusion` routes.",
            "",
            f"Boundary: {report['boundary']}",
            "",
        ]
    )
    return "\n".join(lines)


def write_or_check(path: Path, data: bytes, *, check: bool) -> None:
    """Write one report atomically or require exact deterministic reproduction."""

    if check:
        if not path.is_file() or path.is_symlink() or path.read_bytes() != data:
            raise ComparisonError(f"Report drift: {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_bytes(data)
    temporary.replace(path)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""

    default_root = Path(__file__).resolve().parents[3]
    parser = argparse.ArgumentParser(
        description="Compare separate classical skills with integrated generated experts."
    )
    parser.add_argument("--repo-root", type=Path, default=default_root)
    parser.add_argument(
        "--output-json",
        type=Path,
        default=(
            default_root
            / "evaluations/integrated-classical-knowledge-skill/reports/"
            "20260813-parity-verification.json"
        ),
    )
    parser.add_argument(
        "--output-markdown",
        type=Path,
        default=(
            default_root
            / "evaluations/integrated-classical-knowledge-skill/reports/"
            "20260813-parity-verification.md"
        ),
    )
    parser.add_argument("--workers", type=int, default=len(CASES))
    parser.add_argument("--check", action="store_true")
    return parser.parse_args()


def main() -> int:
    """Run every comparison and publish deterministic reports."""

    args = parse_args()
    repo_root = args.repo_root.resolve()
    if not repo_root.is_dir() or repo_root.is_symlink():
        raise ComparisonError(f"Repository root is absent or unsafe: {repo_root}")
    if isinstance(args.workers, bool) or not 1 <= args.workers <= len(CASES):
        raise ComparisonError(f"--workers must be from 1 through {len(CASES)}")
    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        futures = [executor.submit(compare_case, str(repo_root), case) for case in CASES]
        rows = [future.result() for future in futures]
    report = summarize(rows)
    json_bytes = (json.dumps(report, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    markdown_bytes = render_markdown(report).encode("utf-8")
    write_or_check(args.output_json.resolve(), json_bytes, check=args.check)
    write_or_check(args.output_markdown.resolve(), markdown_bytes, check=args.check)
    print(canonical_json(report["totals"]))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ComparisonError, OSError, ValueError) as exc:
        print(
            canonical_json(
                {
                    "schema_version": SCHEMA_VERSION,
                    "status": "error",
                    "error": str(exc),
                }
            ),
            file=sys.stderr,
        )
        raise SystemExit(1) from exc
