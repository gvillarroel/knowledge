#!/usr/bin/env python3
"""Generate prospective endocrine-hygiene Harbor tasks for Tantivy queries."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Sequence

import generate_astro_evolution_tasks as source_identity
import generate_evolution_tasks as base


SCHEMA_VERSION = "semantic-okf-tantivy-endocrine-evolution-tasks/1.0"
DATASET_ID = "endocrine-hygiene-30"
IDENTITY_FIELD = "source_id"
QUESTION_COUNT = 30
SCORE = source_identity.ASTRO_SCORE


def read_questions(path: Path) -> dict[str, dict[str, Any]]:
    """Load the frozen endocrine questions while preserving source identity."""

    return source_identity.read_questions(
        path,
        expected_count=QUESTION_COUNT,
        dataset_label="endocrine-hygiene",
    )


def read_cohorts(
    path: Path,
    development_cohort: str,
    holdout_cohort: str,
) -> dict[str, tuple[str, ...]]:
    """Load two disjoint prospective endocrine cohorts."""

    return source_identity.read_cohorts(
        path,
        development_cohort,
        holdout_cohort,
        dataset_id=DATASET_ID,
        dataset_label="endocrine-hygiene",
    )


def task_toml(phase: str, index: int) -> str:
    """Render one prospective endocrine query task declaration."""

    return f"""schema_version = "1.3"
artifacts = [
  {{ source = "/logs/agent/tantivy-results.json", destination = "tantivy-results.json" }},
]

[task]
name = "knowledge/tantivy-consult-endocrine-evolution__{phase}__part-{index:02d}"
description = "Deterministic prospective endocrine-hygiene Tantivy retrieval partition."
keywords = ["semantic-okf", "tantivy", "endocrine", "retrieval", "evolution", "{phase}"]

[metadata]
difficulty = "medium"
category = "retrieval-evaluation"
dataset_id = "{DATASET_ID}"
family = "tantivy"
phase = "{phase}"
identity_field = "{IDENTITY_FIELD}"

[agent]
timeout_sec = 300.0
network_mode = "public"

[verifier]
timeout_sec = 120.0
environment_mode = "separate"
network_mode = "public"

[verifier.environment]
os = "linux"
network_mode = "public"
memory_mb = 2048

[environment]
docker_image = "{base.TASK_IMAGE}"
os = "linux"
network_mode = "public"
memory_mb = 4096
storage_mb = 8192
workdir = "/workspace"
"""


def expected_files(
    questions_path: Path,
    cohorts_path: Path,
    development_cohort: str,
    holdout_cohort: str,
) -> dict[str, bytes]:
    """Build one deterministic prospective endocrine task tree in memory."""

    questions = read_questions(questions_path)
    cohorts = read_cohorts(
        cohorts_path,
        development_cohort,
        holdout_cohort,
    )
    files: dict[str, bytes] = {}
    manifest_tasks: list[dict[str, Any]] = []
    for phase, identifiers in cohorts.items():
        for index, group in enumerate(base.partitions(identifiers), start=1):
            task = f"{phase}/part-{index:02d}"
            selected = [questions[identifier] for identifier in group]
            files[f"{task}/task.toml"] = task_toml(phase, index).encode("utf-8")
            files[f"{task}/instruction.md"] = (
                "Use the sole installed `consult-semantic-okf-tantivy` skill "
                "and the read-only endocrine-hygiene snapshot at `/knowledge` "
                f"to run this deterministic {phase} retrieval partition. Do "
                "not build, repair, or modify knowledge. Preserve exact "
                "evidence identities and write no files into the snapshot.\n"
            ).encode("utf-8")
            files[f"{task}/solution/solve.sh"] = base.SOLVE_SH.encode("utf-8")
            files[f"{task}/solution/run_candidate.py"] = (
                base.RUN_CANDIDATE.encode("utf-8")
            )
            files[f"{task}/solution/questions.json"] = base.json_bytes(
                [
                    {
                        "id": row["id"],
                        "short_id": row["short_id"],
                        "question": row["question"],
                    }
                    for row in selected
                ]
            )
            files[f"{task}/tests/test.sh"] = base.TEST_SH.encode("utf-8")
            files[f"{task}/tests/score.py"] = SCORE.encode("utf-8")
            files[f"{task}/tests/qrels.json"] = base.json_bytes(
                {
                    "schema_version": "tantivy-retrieval-qrels/1.0",
                    "identity_field": IDENTITY_FIELD,
                    "questions": [
                        {
                            "id": row["id"],
                            "identity_ids": row["identity_ids"],
                        }
                        for row in selected
                    ],
                }
            )
            files[f"{task}/tests/Dockerfile"] = (
                f"FROM {base.TASK_IMAGE}\n"
                "COPY . /tests\n"
                "RUN chmod 0555 /tests/test.sh /tests/score.py\n"
                "WORKDIR /tests\n"
            ).encode("utf-8")
            manifest_tasks.append(
                {
                    "phase": phase,
                    "task": task,
                    "question_ids": list(group),
                }
            )
    file_rows = [
        {"path": path, "sha256": hashlib.sha256(payload).hexdigest()}
        for path, payload in sorted(files.items())
    ]
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "status": "pass",
        "dataset_id": DATASET_ID,
        "identity_field": IDENTITY_FIELD,
        "task_image": base.TASK_IMAGE,
        "questions_per_task": base.TASKS_PER_PARTITION,
        "cohort_mapping": {
            "development": development_cohort,
            "holdout": holdout_cohort,
        },
        "tasks": manifest_tasks,
        "file_count_excluding_manifest": len(files),
        "tree_sha256_excluding_manifest": hashlib.sha256(
            json.dumps(
                file_rows,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest(),
    }
    files["manifest.json"] = base.json_bytes(manifest)
    return files


def build_parser() -> argparse.ArgumentParser:
    """Build the prospective endocrine task generator CLI."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--questions", type=Path, required=True)
    parser.add_argument("--cohorts", type=Path, required=True)
    parser.add_argument("--development-cohort", required=True)
    parser.add_argument("--holdout-cohort", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Generate or verify the prospective endocrine task tree."""

    args = build_parser().parse_args(argv)
    try:
        files = expected_files(
            args.questions.resolve(),
            args.cohorts.resolve(),
            args.development_cohort,
            args.holdout_cohort,
        )
        base.publish(files, args.output.resolve(), args.check)
    except (
        base.TaskGenerationError,
        OSError,
        UnicodeError,
        ValueError,
        TypeError,
    ) as exc:
        print(
            json.dumps(
                {
                    "schema_version": SCHEMA_VERSION,
                    "status": "error",
                    "error": str(exc),
                },
                sort_keys=True,
            )
        )
        return 2
    print(
        json.dumps(
            {
                "schema_version": SCHEMA_VERSION,
                "status": "pass",
                "mode": "check" if args.check else "generate",
                "file_count": len(files),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
