#!/usr/bin/env python3
"""Validate the immutable Semantic OKF adaptive evolution benchmark."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "semantic-okf-adaptive-frozen-benchmark/1.0"
ROOT_KEYS = {
    "schema_version",
    "benchmark_id",
    "status",
    "frozen_on",
    "mutation_policy",
    "cohorts",
    "support_files",
    "evaluator_files",
    "incumbent_reports",
    "invariants",
}
COHORT_KEYS = {"path", "sha256", "count", "ordered_ids"}
BOUND_FILE_KEYS = {"role", "path", "sha256"}
INVARIANT_KEYS = {
    "retrieval_composition",
    "ground_truth_alignment",
    "prompt_isolation",
    "fitness_boundary",
}


class FrozenBenchmarkError(ValueError):
    """Raised when the frozen benchmark differs from its accepted manifest."""


def _object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise FrozenBenchmarkError(f"duplicate JSON key: {key}")
        value[key] = item
    return value


def _load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_object)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise FrozenBenchmarkError(f"cannot read JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise FrozenBenchmarkError(f"expected a JSON object: {path}")
    return value


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        raise FrozenBenchmarkError(f"cannot read JSONL {path}: {exc}") from exc
    for number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line, object_pairs_hook=_object)
        except json.JSONDecodeError as exc:
            raise FrozenBenchmarkError(f"invalid JSONL {path}:{number}: {exc}") from exc
        if not isinstance(row, dict):
            raise FrozenBenchmarkError(f"expected an object at {path}:{number}")
        rows.append(row)
    return rows


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _exact_keys(value: dict[str, Any], expected: set[str], label: str) -> None:
    if set(value) != expected:
        raise FrozenBenchmarkError(
            f"{label} keys differ: expected {sorted(expected)}, found {sorted(value)}"
        )


def _safe_file(repo_root: Path, raw_path: Any) -> Path:
    if not isinstance(raw_path, str) or not raw_path or "\\" in raw_path:
        raise FrozenBenchmarkError(f"invalid repository-relative path: {raw_path!r}")
    candidate = repo_root.joinpath(*raw_path.split("/"))
    try:
        resolved = candidate.resolve(strict=True)
        resolved.relative_to(repo_root)
    except (OSError, ValueError) as exc:
        raise FrozenBenchmarkError(f"unsafe or missing bound path: {raw_path}") from exc
    if not resolved.is_file():
        raise FrozenBenchmarkError(f"bound path is not a regular file: {raw_path}")
    return resolved


def _validate_hash(repo_root: Path, entry: dict[str, Any], label: str) -> Path:
    _exact_keys(entry, BOUND_FILE_KEYS, label)
    if not isinstance(entry.get("role"), str) or not entry["role"]:
        raise FrozenBenchmarkError(f"{label} has an invalid role")
    expected = entry.get("sha256")
    if not isinstance(expected, str) or len(expected) != 64:
        raise FrozenBenchmarkError(f"{label} has an invalid SHA-256")
    path = _safe_file(repo_root, entry["path"])
    actual = _sha256(path)
    if actual != expected:
        raise FrozenBenchmarkError(
            f"{label} changed: {entry['path']} expected {expected}, found {actual}"
        )
    return path


def _validate_cohort(
    repo_root: Path, name: str, entry: dict[str, Any]
) -> tuple[Path, list[dict[str, Any]]]:
    _exact_keys(entry, COHORT_KEYS, f"cohorts.{name}")
    path = _safe_file(repo_root, entry["path"])
    expected_hash = entry.get("sha256")
    if _sha256(path) != expected_hash:
        raise FrozenBenchmarkError(f"frozen cohort changed: {entry['path']}")
    rows = _load_jsonl(path)
    if entry.get("count") != len(rows):
        raise FrozenBenchmarkError(f"cohorts.{name} row count changed")
    ordered_ids = [row.get("id") for row in rows]
    if entry.get("ordered_ids") != ordered_ids:
        raise FrozenBenchmarkError(f"cohorts.{name} ordered IDs changed")
    if len(ordered_ids) != len(set(ordered_ids)):
        raise FrozenBenchmarkError(f"cohorts.{name} contains duplicate IDs")
    return path, rows


def validate(repo_root: Path, manifest_path: Path) -> dict[str, Any]:
    """Validate all frozen files and cross-cohort invariants."""
    repo_root = repo_root.resolve(strict=True)
    manifest_path = manifest_path.resolve(strict=True)
    try:
        manifest_path.relative_to(repo_root)
    except ValueError as exc:
        raise FrozenBenchmarkError("manifest must be inside the repository root") from exc
    manifest = _load_json(manifest_path)
    _exact_keys(manifest, ROOT_KEYS, "manifest")
    if manifest.get("schema_version") != SCHEMA_VERSION:
        raise FrozenBenchmarkError("unexpected frozen benchmark schema")
    if manifest.get("status") != "frozen":
        raise FrozenBenchmarkError("benchmark status must remain frozen")
    if not isinstance(manifest.get("mutation_policy"), str) or not manifest["mutation_policy"]:
        raise FrozenBenchmarkError("mutation policy must be nonempty")
    cohorts = manifest.get("cohorts")
    if not isinstance(cohorts, dict) or set(cohorts) != {
        "retrieval_questions",
        "hard_questions",
        "hard_ground_truth",
    }:
        raise FrozenBenchmarkError("cohort declarations differ")

    _, retrieval = _validate_cohort(repo_root, "retrieval_questions", cohorts["retrieval_questions"])
    _, hard = _validate_cohort(repo_root, "hard_questions", cohorts["hard_questions"])
    _, truth = _validate_cohort(repo_root, "hard_ground_truth", cohorts["hard_ground_truth"])

    support = manifest.get("support_files")
    evaluators = manifest.get("evaluator_files")
    incumbents = manifest.get("incumbent_reports")
    if not all(isinstance(group, list) and group for group in (support, evaluators, incumbents)):
        raise FrozenBenchmarkError("bound file groups must be nonempty lists")
    bound_paths: set[str] = set()
    for group_name, group in (
        ("support_files", support),
        ("evaluator_files", evaluators),
        ("incumbent_reports", incumbents),
    ):
        roles: set[str] = set()
        for number, entry in enumerate(group, 1):
            if not isinstance(entry, dict):
                raise FrozenBenchmarkError(f"{group_name}[{number}] must be an object")
            _validate_hash(repo_root, entry, f"{group_name}[{number}]")
            if entry["role"] in roles or entry["path"] in bound_paths:
                raise FrozenBenchmarkError(f"duplicate bound role or path in {group_name}")
            roles.add(entry["role"])
            bound_paths.add(entry["path"])

    original_entry = next(
        item for item in support if item["role"] == "original-thirty-question-cohort"
    )
    original = _load_jsonl(_safe_file(repo_root, original_entry["path"]))
    if retrieval[:30] != original:
        raise FrozenBenchmarkError("retrieval prefix no longer equals the original thirty questions")
    if retrieval[30:] != hard:
        raise FrozenBenchmarkError("retrieval suffix no longer equals the ten hard questions")
    if [row["id"] for row in hard] != [row["id"] for row in truth]:
        raise FrozenBenchmarkError("hard question and ground-truth IDs differ")
    for question, ground_truth in zip(hard, truth, strict=True):
        _exact_keys(question, {"id", "qrels", "question"}, f"question {question.get('id')}")
        if ground_truth.get("question") != question["question"]:
            raise FrozenBenchmarkError(f"question text differs for {question['id']}")
        truth_value = ground_truth.get("ground_truth")
        if not isinstance(truth_value, dict):
            raise FrozenBenchmarkError(f"missing ground truth for {question['id']}")
        qrels = question.get("qrels")
        if not isinstance(qrels, dict) or set(qrels) != {"paper_ids", "source_ids"}:
            raise FrozenBenchmarkError(f"invalid qrels for {question['id']}")
        if qrels["paper_ids"] != truth_value.get("required_paper_ids"):
            raise FrozenBenchmarkError(f"paper qrels differ for {question['id']}")
        if qrels["source_ids"] != truth_value.get("required_source_ids"):
            raise FrozenBenchmarkError(f"source qrels differ for {question['id']}")

    invariants = manifest.get("invariants")
    if not isinstance(invariants, dict):
        raise FrozenBenchmarkError("invariants must be an object")
    _exact_keys(invariants, INVARIANT_KEYS, "invariants")
    if not all(isinstance(value, str) and value for value in invariants.values()):
        raise FrozenBenchmarkError("every invariant description must be nonempty")

    return {
        "status": "pass",
        "schema_version": SCHEMA_VERSION,
        "benchmark_id": manifest["benchmark_id"],
        "manifest_sha256": _sha256(manifest_path),
        "retrieval_questions": len(retrieval),
        "hard_questions": len(hard),
        "bound_files": 3 + len(support) + len(evaluators) + len(incumbents),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--manifest", type=Path)
    args = parser.parse_args()
    repo_root = args.repo_root.resolve()
    manifest = args.manifest or Path(__file__).resolve().parents[1] / "frozen-benchmark.json"
    try:
        result = validate(repo_root, manifest)
    except (FrozenBenchmarkError, OSError) as exc:
        print(json.dumps({"status": "fail", "error": str(exc)}, sort_keys=True))
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
