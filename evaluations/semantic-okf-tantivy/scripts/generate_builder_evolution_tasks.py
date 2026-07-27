#!/usr/bin/env python3
"""Generate deterministic Harbor tasks that build before frozen Tantivy consultation."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

import generate_evolution_tasks as base


SCHEMA_VERSION = "semantic-okf-tantivy-builder-evolution-tasks/1.0"
SCRIPT = Path(__file__).resolve()
REPO = SCRIPT.parents[3]
FROZEN_CONSULT = REPO / "skills" / "consult-semantic-okf-tantivy"
FROZEN_CONSULT_TREE = (
    "sha256:8c3666ede3281b96a8630321d9c2fb91d015da96469003ecf22643e041b6f7e7"
)

RUN_CANDIDATE = r'''#!/usr/bin/env python3
"""Build a candidate snapshot, then query it with the frozen Tantivy consumer."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path


QUESTIONS = Path("/solution/questions.json")
CONSULT_LOCK = Path("/solution/consult-lock.json")
CONSULT = Path("/solution/frozen-consult")
OUTPUT = Path("/logs/agent/tantivy-results.json")
BUNDLE = Path("/workspace/knowledge")
BUILDER = Path(
    "/harbor/skills/build-semantic-okf-tantivy/scripts/"
    "build_semantic_okf_tantivy.py"
)
VALIDATOR = Path(
    "/harbor/skills/build-semantic-okf-tantivy/scripts/"
    "validate_semantic_okf_tantivy.py"
)
QUERY = CONSULT / "scripts/query_semantic_okf_tantivy.py"
TOKEN_RE = re.compile(r"[A-Za-z0-9]+")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_consult() -> dict[str, object]:
    lock = json.loads(CONSULT_LOCK.read_text(encoding="utf-8"))
    expected = lock["files"]
    actual_paths = sorted(
        path.relative_to(CONSULT).as_posix()
        for path in CONSULT.rglob("*")
        if path.is_file()
    )
    if actual_paths != sorted(expected):
        raise RuntimeError("frozen consultation file set differs from its lock")
    for relative, expected_hash in expected.items():
        if sha256(CONSULT / relative) != expected_hash:
            raise RuntimeError(f"frozen consultation digest mismatch: {relative}")
    return lock


def run(command: list[str], timeout: int) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=timeout,
        check=False,
    )


def main() -> int:
    questions = json.loads(QUESTIONS.read_text(encoding="utf-8"))
    lock = verify_consult()
    build = run(
        [
            sys.executable,
            str(BUILDER),
            "/dataset/manifest.json",
            "/dataset/plan.json",
            str(BUNDLE),
            "--output-format",
            "json",
        ],
        420,
    )
    validation = None
    if build.returncode == 0:
        validation = run(
            [
                sys.executable,
                str(VALIDATOR),
                str(BUNDLE),
                "--output-format",
                "json",
            ],
            180,
        )
    build_ok = (
        build.returncode == 0
        and validation is not None
        and validation.returncode == 0
    )
    results = []
    for row in questions:
        if not build_ok:
            results.append(
                {
                    "question_id": row["id"],
                    "return_code": build.returncode or validation.returncode,
                    "response": None,
                    "stderr": (build.stderr + (validation.stderr if validation else ""))[-1000:],
                }
            )
            continue
        query = " ".join(TOKEN_RE.findall(row["question"]))
        completed = run(
            [
                sys.executable,
                str(QUERY),
                str(BUNDLE),
                "search",
                "--query",
                query,
                "--top-k",
                "10",
            ],
            120,
        )
        payload = json.loads(completed.stdout) if completed.stdout.strip() else None
        results.append(
            {
                "question_id": row["id"],
                "return_code": completed.returncode,
                "response": payload,
                "stderr": completed.stderr[-1000:],
            }
        )
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(
            {
                "schema_version": "tantivy-builder-oracle-retrieval/1.0",
                "frozen_consult_tree_sha256": lock["tree_sha256"],
                "build_return_code": build.returncode,
                "validation_return_code": (
                    validation.returncode if validation is not None else None
                ),
                "results": results,
            },
            ensure_ascii=False,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''

SOLVE_SH = """#!/usr/bin/env bash
set -euo pipefail
mkdir -p /logs/agent
python /solution/run_candidate.py
"""


def consult_files() -> tuple[dict[str, bytes], dict[str, Any]]:
    """Load the exact frozen consultation tree and construct its file lock."""

    files = {
        path.relative_to(FROZEN_CONSULT).as_posix(): path.read_bytes()
        for path in sorted(FROZEN_CONSULT.rglob("*"))
        if path.is_file() and "__pycache__" not in path.parts
    }
    if not files:
        raise base.TaskGenerationError("frozen Tantivy consultation is missing")
    lock = {
        "schema_version": "semantic-okf-tantivy-consult-lock/1.0",
        "tree_sha256": FROZEN_CONSULT_TREE,
        "files": {
            relative: hashlib.sha256(payload).hexdigest()
            for relative, payload in sorted(files.items())
        },
    }
    return files, lock


def task_toml(phase: str, index: int) -> str:
    """Render one builder evaluation task contract."""

    return f"""schema_version = "1.3"
artifacts = [
  {{ source = "/logs/agent/tantivy-results.json", destination = "tantivy-results.json" }},
]

[task]
name = "knowledge/tantivy-builder-evolution__{phase}__part-{index:02d}"
description = "Build a candidate snapshot before frozen Tantivy retrieval partition."
keywords = ["semantic-okf", "tantivy", "builder", "retrieval", "evolution"]

[metadata]
difficulty = "hard"
category = "retrieval-evaluation"
dataset_id = "graphrag-papers-40"
family = "tantivy"
phase = "{phase}"

[agent]
timeout_sec = 900.0
network_mode = "public"

[verifier]
timeout_sec = 180.0
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
) -> dict[str, bytes]:
    """Build the complete partitioned task tree in memory."""

    questions = base.read_questions(questions_path)
    cohorts = base.read_cohorts(cohorts_path)
    frozen_files, lock = consult_files()
    files: dict[str, bytes] = {}
    manifest_tasks: list[dict[str, Any]] = []
    for phase, identifiers in cohorts.items():
        for index, group in enumerate(base.partitions(identifiers), start=1):
            task = f"{phase}/part-{index:02d}"
            selected = [questions[identifier] for identifier in group]
            files[f"{task}/task.toml"] = task_toml(phase, index).encode("utf-8")
            files[f"{task}/instruction.md"] = (
                "Use the sole installed `build-semantic-okf-tantivy` skill to "
                "build a new snapshot from the read-only `/dataset` inputs. The "
                "solution will consult that snapshot with the digest-locked "
                "Tantivy consumer. Do not read verifier files or alter the "
                "frozen consumer.\n"
            ).encode("utf-8")
            files[f"{task}/solution/solve.sh"] = SOLVE_SH.encode("utf-8")
            files[f"{task}/solution/run_candidate.py"] = RUN_CANDIDATE.encode(
                "utf-8"
            )
            files[f"{task}/solution/consult-lock.json"] = base.json_bytes(lock)
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
            for relative, payload in frozen_files.items():
                files[f"{task}/solution/frozen-consult/{relative}"] = payload
            files[f"{task}/tests/test.sh"] = base.TEST_SH.encode("utf-8")
            files[f"{task}/tests/score.py"] = base.SCORE.encode("utf-8")
            files[f"{task}/tests/qrels.json"] = base.json_bytes(
                {
                    "schema_version": "tantivy-retrieval-qrels/1.0",
                    "questions": [
                        {"id": row["id"], "paper_ids": row["paper_ids"]}
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
        "task_image": base.TASK_IMAGE,
        "frozen_consult_tree_sha256": FROZEN_CONSULT_TREE,
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
    """Build the deterministic generator CLI."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--questions", type=Path, required=True)
    parser.add_argument("--cohorts", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Generate or verify the exact builder task tree."""

    args = build_parser().parse_args(argv)
    try:
        files = expected_files(args.questions.resolve(), args.cohorts.resolve())
        base.publish(files, args.output.resolve(), args.check)
    except (base.TaskGenerationError, OSError, UnicodeError, ValueError, TypeError) as exc:
        print(
            json.dumps(
                {"schema_version": SCHEMA_VERSION, "status": "error", "error": str(exc)},
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
