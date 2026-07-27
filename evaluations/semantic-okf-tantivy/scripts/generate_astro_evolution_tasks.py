#!/usr/bin/env python3
"""Generate prospective Astro Harbor tasks for Tantivy query evolution."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

import generate_evolution_tasks as base


SCHEMA_VERSION = "semantic-okf-tantivy-astro-evolution-tasks/1.0"
COHORT_SCHEMA = "semantic-okf-evaluation-cohorts/1.0"
DATASET_ID = "astro-40"
IDENTITY_FIELD = "source_id"

ASTRO_SCORE = base.SCORE.replace(
    'truth["paper_ids"]',
    'truth["identity_ids"]',
).replace(
    'paper = hit.get("paper_id")',
    'paper = hit.get("source_id")',
)
if ASTRO_SCORE == base.SCORE or 'truth["paper_ids"]' in ASTRO_SCORE:
    raise RuntimeError("Astro verifier specialization did not apply")


def read_questions(
    path: Path,
    *,
    expected_count: int = 40,
    dataset_label: str = "Astro",
) -> dict[str, dict[str, Any]]:
    """Load source-identity questions without changing their qrel identities."""

    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        raise base.TaskGenerationError(f"cannot read questions: {exc}") from exc
    result: dict[str, dict[str, Any]] = {}
    for number, line in enumerate(lines, start=1):
        row = base.strict_json(line, f"questions:{number}")
        if (
            not isinstance(row, dict)
            or set(row) != {"id", "qrels", "question", "question_type"}
            or not isinstance(row.get("id"), str)
            or not row["id"]
            or not isinstance(row.get("question"), str)
            or not row["question"]
            or not isinstance(row.get("question_type"), str)
            or not row["question_type"]
            or not isinstance(row.get("qrels"), dict)
            or set(row["qrels"]) not in (
                {"document_ids", "source_ids"},
                {"paper_ids", "source_ids"},
            )
        ):
            raise base.TaskGenerationError(
                f"questions:{number} has an invalid {dataset_label} schema"
            )
        identifier = row["id"]
        identities = row["qrels"]["source_ids"]
        authority_ids = row["qrels"].get(
            "document_ids",
            row["qrels"].get("paper_ids"),
        )
        if (
            not isinstance(identities, list)
            or not identities
            or any(not isinstance(value, str) or not value for value in identities)
            or len(identities) != len(set(identities))
            or not isinstance(authority_ids, list)
            or not authority_ids
            or any(not isinstance(value, str) or not value for value in authority_ids)
            or len(authority_ids) != len(set(authority_ids))
        ):
            raise base.TaskGenerationError(
                f"questions:{number} has invalid qrel identities"
            )
        short_id = identifier.split("-", 1)[0]
        if short_id in result:
            raise base.TaskGenerationError(
                f"duplicate question prefix {short_id!r}"
            )
        result[short_id] = {
            "id": identifier,
            "short_id": short_id,
            "question": row["question"],
            "identity_ids": sorted(identities),
        }
    if len(result) != expected_count:
        raise base.TaskGenerationError(
            f"{dataset_label} task generation requires {expected_count} "
            f"questions, found {len(result)}"
        )
    return result


def read_cohorts(
    path: Path,
    development_cohort: str,
    holdout_cohort: str,
    *,
    dataset_id: str = DATASET_ID,
    dataset_label: str = "Astro",
) -> dict[str, tuple[str, ...]]:
    """Map two disjoint pinned cohorts onto the trace-distillation phases."""

    payload = base.read_json(path, "cohort registry")
    cohorts = payload.get("cohorts") if isinstance(payload, dict) else None
    if (
        not isinstance(payload, dict)
        or payload.get("schema_version") != COHORT_SCHEMA
        or payload.get("dataset_id") != dataset_id
        or not isinstance(cohorts, dict)
    ):
        raise base.TaskGenerationError(
            f"{dataset_label} cohort registry has an invalid schema"
        )
    if development_cohort == holdout_cohort:
        raise base.TaskGenerationError(
            "development and holdout cohort names must differ"
        )
    mapped: dict[str, tuple[str, ...]] = {}
    for phase, cohort_name in (
        ("development", development_cohort),
        ("holdout", holdout_cohort),
    ):
        values = tuple(cohorts.get(cohort_name, ()))
        if (
            not values
            or any(not isinstance(value, str) or not value for value in values)
            or len(values) != len(set(values))
        ):
            raise base.TaskGenerationError(
                f"{dataset_label} {cohort_name!r} cohort is invalid"
            )
        mapped[phase] = values
    if set(mapped["development"]) & set(mapped["holdout"]):
        raise base.TaskGenerationError(
            f"{dataset_label} development and holdout cohorts overlap"
        )
    return mapped


def task_toml(phase: str, index: int) -> str:
    """Render one prospective Astro query task declaration."""

    return f"""schema_version = "1.3"
artifacts = [
  {{ source = "/logs/agent/tantivy-results.json", destination = "tantivy-results.json" }},
]

[task]
name = "knowledge/tantivy-consult-astro-evolution__{phase}__part-{index:02d}"
description = "Deterministic prospective Astro Tantivy consultation partition."
keywords = ["semantic-okf", "tantivy", "astro", "retrieval", "evolution", "{phase}"]

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
    """Build one deterministic prospective task tree in memory."""

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
                "and the read-only Astro snapshot at `/knowledge` to run this "
                f"deterministic {phase} retrieval partition. Do not build, "
                "repair, or modify knowledge. Preserve exact evidence "
                "identities and write no files into the snapshot.\n"
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
            files[f"{task}/tests/score.py"] = ASTRO_SCORE.encode("utf-8")
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
    """Build the prospective Astro task generator CLI."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--questions", type=Path, required=True)
    parser.add_argument("--cohorts", type=Path, required=True)
    parser.add_argument("--development-cohort", required=True)
    parser.add_argument("--holdout-cohort", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Generate or verify the prospective Astro task tree."""

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
