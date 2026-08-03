#!/usr/bin/env python3
"""Prepare, generate, validate, and rehearse the private classical Harbor dataset."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence


SCRIPT_PATH = Path(__file__).resolve()
STUDY_ROOT = SCRIPT_PATH.parents[1]
REPO_ROOT = SCRIPT_PATH.parents[3]
REGISTRY_ROOT = STUDY_ROOT / "processed" / "dataset-registry"
DESCRIPTOR_PATH = REGISTRY_ROOT / "software-architecture-books-40.json"
STAGED_INPUT = STUDY_ROOT / "processed" / "staged-input" / "classical"
BUNDLE = STUDY_ROOT / "processed" / "bundle"
TASK_ROOT = STUDY_ROOT / "generated" / "harbor-tasks"
DRY_RUN_ROOT = STUDY_ROOT / "results" / "harbor-dry-runs"
DATASET_ID = "software-architecture-books-40"
FAMILY_ID = "classical"
SEMANTIC_DATASETS = REPO_ROOT / "evaluations" / "semantic-okf-datasets"

sys.dont_write_bytecode = True
sys.path.insert(0, str(SEMANTIC_DATASETS))

import dataset_tool as data  # noqa: E402


data.DATASETS = REGISTRY_ROOT

import candidate_family as candidates  # noqa: E402
import generate_harbor_tasks as generator  # noqa: E402
import run_harbor as runner  # noqa: E402
import validate_harbor_tasks as validator  # noqa: E402


class PrivateHarborError(RuntimeError):
    """Raised when the private descriptor or rehearsal cannot be reproduced."""


def sha256_file(path: Path) -> str:
    """Return a lowercase SHA-256 for one file."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def pinned(relative: str, *, count: int | None = None, **extra: Any) -> dict[str, Any]:
    """Build one checked repository-relative file descriptor."""

    path = REPO_ROOT / relative
    if not path.is_file():
        raise PrivateHarborError(f"Pinned private dataset input is absent: {relative}")
    result: dict[str, Any] = {
        "path": relative,
        "sha256": sha256_file(path),
    }
    if count is not None:
        result["count"] = count
    result.update(extra)
    return result


def descriptor() -> dict[str, Any]:
    """Render the local-only one-family dataset descriptor."""

    plans = {family_id: None for family_id in data.load_families()}
    plans[FAMILY_ID] = pinned(
        "evaluations/software-architecture-books/plans/classical-plan.json"
    )
    return {
        "schema_version": "semantic-okf-evaluation-dataset/1.1",
        "dataset_id": DATASET_ID,
        "title": "Software architecture books 40-question private benchmark",
        "description": (
            "Eighteen private books with thirty development questions and ten "
            "hash-only evidence-first hard questions."
        ),
        "question_format": "document-qrels",
        "source_manifest": pinned(
            "evaluations/software-architecture-books/manifest.json",
            count=18,
        ),
        "questions": pinned(
            "evaluations/software-architecture-books/benchmark/retrieval-questions.jsonl",
            count=40,
        ),
        "semantic_rubric": None,
        "hard_ground_truth": pinned(
            "evaluations/software-architecture-books/benchmark/hard-ground-truth.jsonl",
            count=10,
            format="harbor",
        ),
        "source_combination": pinned(
            "evaluations/software-architecture-books/source-combination.json"
        ),
        "reference_bundle": (
            "evaluations/software-architecture-books/processed/bundle"
        ),
        "cohorts": pinned(
            "evaluations/software-architecture-books/benchmark/cohorts.json"
        ),
        "partition_cohorts": ["development", "hard"],
        "evaluation_policy": {
            "qrel_scope": "non-exhaustive-focus-set",
            "minimum_document_gate_basis": "valid-evidence-document-count",
            "semantic_ranking_gate": "manual-review-required",
            "full_dataset_coverage_required": True,
        },
        "plans": plans,
    }


def descriptor_payload() -> str:
    """Serialize the descriptor deterministically."""

    return (
        json.dumps(
            descriptor(),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
            allow_nan=False,
        )
        + "\n"
    )


def ensure_descriptor(*, check: bool) -> str:
    """Create or compare the ignored private descriptor."""

    payload = descriptor_payload()
    if check:
        if (
            not DESCRIPTOR_PATH.is_file()
            or DESCRIPTOR_PATH.read_text(encoding="utf-8") != payload
        ):
            raise PrivateHarborError("Private dataset descriptor is absent or stale")
    else:
        DESCRIPTOR_PATH.parent.mkdir(parents=True, exist_ok=True)
        DESCRIPTOR_PATH.write_text(payload, encoding="utf-8", newline="\n")
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def prepare_stage() -> Mapping[str, Any]:
    """Materialize and independently regenerate the evaluator-free input."""

    if STAGED_INPUT.is_dir():
        report = data.materialize_stage(
            DATASET_ID,
            FAMILY_ID,
            STAGED_INPUT,
            replace=False,
            check=True,
        )
    else:
        report = data.materialize_stage(
            DATASET_ID,
            FAMILY_ID,
            STAGED_INPUT,
            replace=False,
            check=False,
        )
        data.materialize_stage(
            DATASET_ID,
            FAMILY_ID,
            STAGED_INPUT,
            replace=False,
            check=True,
        )
    return report


def task_arguments(mode: str, task_root: Path, *, check: bool) -> list[str]:
    """Build private task-generation arguments for one isolated mode."""

    arguments = [
        "--dataset",
        DATASET_ID,
        "--family",
        FAMILY_ID,
        "--mode",
        mode,
        "--bundle",
        str(BUNDLE),
        "--output",
        str(task_root),
        "--verifier-network-mode",
        "no-network",
    ]
    if mode == "build-consult":
        arguments.extend(("--input", str(STAGED_INPUT)))
    if check:
        arguments.append("--check")
    return arguments


def generate_and_validate_tasks(mode: str) -> Mapping[str, Any]:
    """Generate, regenerate, and structurally validate one task tree."""

    task_root = TASK_ROOT / mode / FAMILY_ID
    created = not task_root.is_dir()
    status = generator.main(task_arguments(mode, task_root, check=not created))
    if status != 0:
        raise PrivateHarborError(f"{mode}: task generation failed")
    if created and generator.main(task_arguments(mode, task_root, check=True)) != 0:
        raise PrivateHarborError(f"{mode}: deterministic task check failed")
    validation_args = [
        "--dataset",
        DATASET_ID,
        "--family",
        FAMILY_ID,
        "--mode",
        mode,
        "--tasks",
        str(task_root),
        "--bundle",
        str(BUNDLE),
        "--skip-generation-check",
    ]
    if mode == "build-consult":
        validation_args.extend(("--input", str(STAGED_INPUT)))
    if validator.main(validation_args) != 0:
        raise PrivateHarborError(f"{mode}: task validation failed")
    manifest = data.load_json(task_root / "manifest.json")
    return {
        "mode": mode,
        "task_root": task_root.relative_to(REPO_ROOT).as_posix(),
        "tree_sha256": data.tree_digest(task_root),
        "question_count": manifest["question_count"],
    }


def validate_dry_run(path: Path, mode: str, cohort: str) -> Mapping[str, Any]:
    """Check or create one append-only redacted rehearsal receipt."""

    receipt_path = path / "run-receipt.json"
    if path.is_dir():
        receipt = data.load_json(receipt_path)
        if (
            receipt.get("dataset_id") != DATASET_ID
            or receipt.get("family") != FAMILY_ID
            or receipt.get("mode") != mode
            or receipt.get("cohort") != cohort
            or receipt.get("run_status") != "dry-run"
        ):
            raise PrivateHarborError(f"Dry-run receipt drift: {path}")
        return receipt
    arguments = [
        "--dataset",
        DATASET_ID,
        "--family",
        FAMILY_ID,
        "--mode",
        mode,
        "--cohort",
        cohort,
        "--tasks",
        str(TASK_ROOT / mode / FAMILY_ID),
        "--output",
        str(path),
        "--dry-run",
    ]
    if mode == "consult-only":
        arguments.extend(("--bundle", str(BUNDLE)))
    else:
        arguments.extend(("--input", str(STAGED_INPUT)))
    if runner.main(arguments) != 0:
        raise PrivateHarborError(f"{mode}/{cohort}: Harbor dry run failed")
    return data.load_json(receipt_path)


def run_all(*, descriptor_only: bool, check_descriptor: bool) -> dict[str, Any]:
    """Execute the complete private classical dataset rehearsal."""

    descriptor_sha256 = ensure_descriptor(check=check_descriptor)
    if descriptor_only:
        return {
            "status": "pass",
            "dataset_id": DATASET_ID,
            "descriptor_sha256": descriptor_sha256,
        }
    validation = data.validate_dataset(DATASET_ID, FAMILY_ID)
    stage = prepare_stage()
    task_reports = [
        generate_and_validate_tasks(mode)
        for mode in ("build-consult", "consult-only")
    ]
    dry_runs: list[dict[str, Any]] = []
    for mode in ("build-consult", "consult-only"):
        for cohort in ("development", "hard"):
            path = DRY_RUN_ROOT / f"{mode}-{cohort}"
            receipt = validate_dry_run(path, mode, cohort)
            dry_runs.append(
                {
                    "mode": mode,
                    "cohort": cohort,
                    "task_count": len(receipt["task_ids"]),
                    "receipt": (path / "run-receipt.json")
                    .relative_to(REPO_ROOT)
                    .as_posix(),
                }
            )
    return {
        "status": "pass",
        "dataset_id": DATASET_ID,
        "family": FAMILY_ID,
        "descriptor_sha256": descriptor_sha256,
        "validation": validation,
        "staged_input_tree_sha256": stage["tree_sha256"],
        "tasks": task_reports,
        "dry_runs": dry_runs,
    }


def build_parser() -> argparse.ArgumentParser:
    """Build the private Harbor orchestration command line."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "action",
        choices=("descriptor", "all"),
        help="Create only the local descriptor or run the complete rehearsal.",
    )
    parser.add_argument(
        "--check-descriptor",
        action="store_true",
        help="Require the ignored descriptor to match instead of writing it.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the requested private dataset operation."""

    args = build_parser().parse_args(argv)
    try:
        report = run_all(
            descriptor_only=args.action == "descriptor",
            check_descriptor=args.check_descriptor,
        )
    except (
        PrivateHarborError,
        data.DatasetError,
        candidates.CandidateFamilyError,
        generator.GenerationError,
        validator.ValidationError,
        runner.RunError,
        OSError,
        UnicodeError,
        json.JSONDecodeError,
        KeyError,
        TypeError,
        ValueError,
    ) as exc:
        print(
            json.dumps(
                {"status": "error", "error": str(exc)},
                ensure_ascii=False,
                sort_keys=True,
            )
        )
        return 2
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
