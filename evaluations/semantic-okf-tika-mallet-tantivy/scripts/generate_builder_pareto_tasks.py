#!/usr/bin/env python3
"""Generate the frozen direct-builder tasks used by reflective Pareto search."""

from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_OUTPUT = (
    REPO_ROOT
    / "evaluations"
    / "semantic-okf-tika-mallet-tantivy"
    / "generated"
    / "reflective-pareto"
    / "builder-direct-tasks-v6"
)
SCORER = (
    REPO_ROOT
    / "evaluations"
    / "semantic-okf-tika-mallet-tantivy"
    / "builder_pareto_score.py"
)


@dataclass(frozen=True)
class Task:
    cohort: str
    task_id: str
    outputs: tuple[str, str]


TASKS = (
    Task(
        "development",
        "qualified-runtime-a",
        ("/workspace/knowledge-primary", "/workspace/knowledge-replay"),
    ),
    Task(
        "development",
        "qualified-runtime-b",
        ("/workspace/release-primary", "/workspace/release-replay"),
    ),
    Task(
        "holdout",
        "qualified-runtime-c",
        ("/workspace/candidate-primary", "/workspace/candidate-replay"),
    ),
    Task(
        "holdout",
        "qualified-runtime-d",
        ("/workspace/snapshot-primary", "/workspace/snapshot-replay"),
    ),
)


def instruction(task: Task) -> str:
    first, second = task.outputs
    return f"""Use the installed `build-semantic-okf-tika-mallet` skill to build and
independently validate two byte-identical Semantic OKF snapshots from the immutable
`/dataset/ingestion-plan.json` and `/dataset/retrieval-plan.json` inputs.

Use the qualified runtime already supplied through `SEMANTIC_OKF_JAVA`,
`SEMANTIC_OKF_TIKA_HOME`, and `SEMANTIC_OKF_MALLET_HOME`. Do not download tools,
dependencies, models, or source documents, and do not modify system packages.
Both destinations are absent and must remain atomic no-replace publications:

1. `{first}`
2. `{second}`

Run the builder and independent validator for each destination. Compare a sorted
relative-path and SHA-256 inventory of both completed trees and require exact
equality. Do not consult, search, or answer from either snapshot. Return a concise
JSON object reporting only the completion status and the two output paths.
"""


def task_toml(task: Task) -> str:
    first, second = task.outputs
    return f"""schema_version = "1.3"
artifacts = [
  {{ source = "/logs/agent/pi.txt", destination = "pi.jsonl" }},
  {{ source = "{first}", destination = "snapshot-primary" }},
  {{ source = "{second}", destination = "snapshot-replay" }},
]

[task]
name = "knowledge/graphrag-papers-40__builder-direct__tika-mallet__{task.task_id}"
description = "Direct mechanical qualification of the Tika/MALLET builder."
keywords = ["semantic-okf", "graphrag-papers-40", "builder-direct", "tika-mallet", "{task.cohort}"]

[metadata]
difficulty = "hard"
category = "knowledge-evaluation"
dataset_id = "graphrag-papers-40"
family = "tika-mallet-tantivy"
mode = "builder-direct-development"
cohort = "{task.cohort}"

[agent]
timeout_sec = 7200.0
network_mode = "public"

[verifier]
timeout_sec = 600.0
environment_mode = "separate"
network_mode = "public"

[verifier.environment]
os = "linux"
network_mode = "public"
memory_mb = 4096

[environment]
docker_image = "semantic-okf-harbor-runtime:1.0"
os = "linux"
network_mode = "public"
memory_mb = 8192
storage_mb = 24576
workdir = "/workspace"
"""


def files_for(task: Task) -> dict[str, bytes]:
    config = {
        "schema_version": "semantic-okf-builder-pareto-task/1.2",
        "task_id": task.task_id,
        "cohort": task.cohort,
        "outputs": list(task.outputs),
        "verifier_network_mode": "public",
        "verifier_uses_network": False,
    }
    return {
        "instruction.md": instruction(task).encode(),
        "task.toml": task_toml(task).encode(),
        "tests/Dockerfile": (
            "FROM semantic-okf-harbor-runtime:1.0\n"
            "COPY . /tests\n"
            "RUN chmod 0555 /tests/test.sh /tests/score.py\n"
            "WORKDIR /tests\n"
        ).encode(),
        "tests/test.sh": (
            "#!/usr/bin/env bash\n"
            "set -euo pipefail\n"
            "python /tests/score.py \\\n"
            "  --config /tests/task-config.json \\\n"
            "  --pi-log /logs/agent/pi.txt \\\n"
            "  --reward /logs/verifier/reward.json \\\n"
            "  --diagnostics /logs/verifier/diagnostics.json\n"
        ).encode(),
        "tests/score.py": SCORER.read_bytes(),
        "tests/task-config.json": (
            json.dumps(config, indent=2, sort_keys=True) + "\n"
        ).encode(),
    }


def materialize(output: Path) -> None:
    if output.exists():
        raise ValueError(f"Refusing to overwrite existing task tree: {output}")
    for task in TASKS:
        root = output / task.cohort / task.task_id
        (root / "environment").mkdir(parents=True, exist_ok=True)
        for relative, payload in files_for(task).items():
            destination = root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(payload)


def tree_digest(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        digest.update(("D:" if path.is_dir() else "F:").encode())
        digest.update(relative.encode())
        digest.update(b"\0")
        if path.is_file():
            digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def check(output: Path) -> None:
    if not output.is_dir():
        raise ValueError(f"Task tree does not exist: {output}")
    with tempfile.TemporaryDirectory(prefix="builder-pareto-tasks-") as temporary:
        expected = Path(temporary) / "tasks"
        materialize(expected)
        if tree_digest(output) != tree_digest(expected):
            raise ValueError("Task tree differs from deterministic regeneration")
        for task in TASKS:
            environment = output / task.cohort / task.task_id / "environment"
            if not environment.is_dir():
                raise ValueError(f"Task environment directory is missing: {environment}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    output = args.output.resolve()
    if args.check:
        check(output)
        status = "pass"
    else:
        materialize(output)
        status = "generated"
    print(
        json.dumps(
            {
                "status": status,
                "output": str(output),
                "task_count": len(TASKS),
                "tree_sha256": tree_digest(output),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
