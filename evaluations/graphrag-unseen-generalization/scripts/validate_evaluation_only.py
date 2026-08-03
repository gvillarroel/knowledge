#!/usr/bin/env python3
"""Validate an evaluation-only dataset and reject optimizer-visible reuse."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence


REGISTRY_SCHEMA = "evaluation-only-registry/1.0"
POLICY_SCHEMA = "evaluation-only-dataset-policy/1.0"
ALLOWED_PURPOSES = frozenset({"evaluation", "aggregate-reporting"})
TEXT_SUFFIXES = frozenset(
    {
        ".json",
        ".jsonl",
        ".md",
        ".py",
        ".toml",
        ".txt",
        ".yaml",
        ".yml",
    }
)
REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_REGISTRY = REPO_ROOT / "evaluations" / "evaluation-only-registry.json"


class EvaluationOnlyError(ValueError):
    """Describe policy, digest, or forbidden-reuse drift."""


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path, *, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise EvaluationOnlyError(f"Cannot read {label} at {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise EvaluationOnlyError(f"{label} must be a JSON object")
    return value


def _registry_rows(registry: Mapping[str, Any]) -> list[dict[str, Any]]:
    if registry.get("schema_version") != REGISTRY_SCHEMA:
        raise EvaluationOnlyError("Unsupported evaluation-only registry schema")
    rows = registry.get("datasets")
    if not isinstance(rows, list) or not rows:
        raise EvaluationOnlyError("Evaluation-only registry has no datasets")
    identifiers: set[str] = set()
    digests: set[str] = set()
    normalized = []
    for row in rows:
        if not isinstance(row, dict):
            raise EvaluationOnlyError("Evaluation-only registry row is not an object")
        dataset_id = row.get("dataset_id")
        questions_sha = row.get("questions_sha256")
        if (
            not isinstance(dataset_id, str)
            or not dataset_id
            or dataset_id in identifiers
            or not isinstance(questions_sha, str)
            or len(questions_sha) != 64
            or questions_sha in digests
            or row.get("classification") != "evaluation-only"
        ):
            raise EvaluationOnlyError("Evaluation-only registry row is invalid")
        identifiers.add(dataset_id)
        digests.add(questions_sha)
        normalized.append(row)
    return normalized


def _registered_by_digest(
    registry_rows: Sequence[Mapping[str, Any]],
    questions: Path,
) -> Mapping[str, Any] | None:
    digest = _sha256(questions)
    return next(
        (row for row in registry_rows if row["questions_sha256"] == digest),
        None,
    )


def validate_dataset(
    registry_rows: Sequence[Mapping[str, Any]],
    dataset_dir: Path,
) -> Mapping[str, Any]:
    """Validate the private payload against its public deny-use registry row."""

    policy = _load(dataset_dir / "EVALUATION_ONLY.json", label="dataset policy")
    if policy.get("schema_version") != POLICY_SCHEMA:
        raise EvaluationOnlyError("Unsupported dataset policy schema")
    dataset_id = policy.get("dataset_id")
    row = next(
        (item for item in registry_rows if item.get("dataset_id") == dataset_id),
        None,
    )
    if row is None:
        raise EvaluationOnlyError(f"Dataset is not registered: {dataset_id}")
    questions = dataset_dir / "retrieval-questions.jsonl"
    truth = dataset_dir / "ground-truth.jsonl"
    if not questions.is_file() or not truth.is_file():
        raise EvaluationOnlyError("Dataset questions or ground truth are absent")
    if _sha256(questions) != row["questions_sha256"]:
        raise EvaluationOnlyError("Evaluation-only question digest drifted")
    if _sha256(truth) != row["ground_truth_sha256"]:
        raise EvaluationOnlyError("Evaluation-only ground-truth digest drifted")
    for key in (
        "classification",
        "questions_sha256",
        "ground_truth_sha256",
        "forbidden_uses",
    ):
        if policy.get(key) != row.get(key):
            raise EvaluationOnlyError(f"Dataset policy disagrees with registry: {key}")
    question_count = sum(
        1
        for line in questions.read_text(encoding="utf-8").splitlines()
        if line.strip()
    )
    if question_count != row.get("question_count"):
        raise EvaluationOnlyError("Evaluation-only question count drifted")
    return row


def validate_purpose(
    registry_rows: Sequence[Mapping[str, Any]],
    questions: Path,
    purpose: str,
) -> Mapping[str, Any] | None:
    """Reject registered question bytes for every optimizer-visible purpose."""

    row = _registered_by_digest(registry_rows, questions)
    if row is not None and purpose not in ALLOWED_PURPOSES:
        raise EvaluationOnlyError(
            f"{row['dataset_id']} is evaluation-only and cannot be used for {purpose}"
        )
    return row


def scan_forbidden_reuse(
    registry_rows: Sequence[Mapping[str, Any]],
    roots: Sequence[Path],
) -> list[str]:
    """Find registered IDs or digests embedded in construction/evolution trees."""

    needles = {
        str(row["dataset_id"])
        for row in registry_rows
    } | {
        str(row["questions_sha256"])
        for row in registry_rows
    } | {
        str(row["ground_truth_sha256"])
        for row in registry_rows
    }
    hits = []
    for root in roots:
        if not root.exists():
            continue
        for path in sorted(root.rglob("*")):
            if path.is_symlink():
                raise EvaluationOnlyError(f"Scan root contains a symlink: {path}")
            if not path.is_file() or path.suffix.casefold() not in TEXT_SUFFIXES:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeError:
                continue
            if any(needle in text for needle in needles):
                hits.append(str(path.resolve()))
    return hits


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--dataset-dir", type=Path)
    parser.add_argument("--questions", type=Path)
    parser.add_argument(
        "--purpose",
        choices=[
            "evaluation",
            "aggregate-reporting",
            "construction",
            "profile-forging",
            "evolution",
            "trace-distillation",
            "candidate-selection",
            "development",
            "validation",
        ],
    )
    parser.add_argument("--scan-root", type=Path, action="append", default=[])
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Validate payload, intended purpose, and optional forbidden-use roots."""

    args = build_parser().parse_args(argv)
    try:
        registry = _load(args.registry.resolve(), label="evaluation-only registry")
        rows = _registry_rows(registry)
        dataset = (
            validate_dataset(rows, args.dataset_dir.resolve())
            if args.dataset_dir is not None
            else None
        )
        if (args.questions is None) != (args.purpose is None):
            raise EvaluationOnlyError("--questions and --purpose must be used together")
        purpose_row = (
            validate_purpose(rows, args.questions.resolve(), args.purpose)
            if args.questions is not None
            else None
        )
        hits = scan_forbidden_reuse(
            rows,
            [root.resolve() for root in args.scan_root],
        )
        if hits:
            raise EvaluationOnlyError(
                "Evaluation-only identity found in forbidden-use tree: "
                + ", ".join(hits)
            )
    except (EvaluationOnlyError, OSError, UnicodeError) as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, sort_keys=True))
        return 2
    print(
        json.dumps(
            {
                "status": "pass",
                "registered_datasets": len(rows),
                "validated_dataset": (
                    dataset.get("dataset_id") if dataset is not None else None
                ),
                "registered_question_match": (
                    purpose_row.get("dataset_id")
                    if purpose_row is not None
                    else None
                ),
                "scan_roots": len(args.scan_root),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
