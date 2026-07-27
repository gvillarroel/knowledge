#!/usr/bin/env python3
"""Prepare an isolated schema-v2 Harbor trace-distillation experiment."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parents[1]
REPO = HERE.parents[1]
CANONICAL_TASKS = (
    REPO
    / "evaluations"
    / "semantic-okf-datasets"
    / "generated"
    / "tasks"
    / "graphrag-papers-40"
    / "consult-only"
    / "classical"
)
SNAPSHOT = (
    REPO
    / "evaluations"
    / "semantic-okf-datasets"
    / "generated"
    / "bundles"
    / "graphrag-papers-40"
    / "classical"
)
SKILL = REPO / "skills" / "consult-semantic-okf-tantivy"
DISCOVERY = ("q001", "q013", "q031", "q039")
HOLDOUT = ("q010", "q029")
SOURCE_COHORT = {
    "q001": "discovery",
    "q013": "discovery",
    "q031": "hard",
    "q039": "hard",
    "q010": "holdout",
    "q029": "holdout",
}
MODEL = "openai-codex/gpt-5.6-luna"
PI_VERSION = "0.81.1"
PI_IMPORT_PATH = "pi_luna_agent:PiLuna"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--auth-directory", required=True)
    parser.add_argument(
        "--output",
        type=Path,
        help="Defaults to generated/trace-distillation-<run-id>.",
    )
    return parser.parse_args()


def wsl_path(path: Path) -> str:
    resolved = path.resolve()
    drive = resolved.drive.rstrip(":").lower()
    if not drive:
        raise ValueError(f"expected a Windows drive path: {resolved}")
    suffix = resolved.as_posix().split(":", 1)[1]
    return f"/mnt/{drive}{suffix}"


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def tree_digest(root: Path) -> str:
    digest = hashlib.sha256()
    files = sorted(path for path in root.rglob("*") if path.is_file())
    for path in files:
        relative = path.relative_to(root).as_posix().encode("utf-8")
        payload = path.read_bytes()
        digest.update(len(relative).to_bytes(8, "big"))
        digest.update(relative)
        digest.update(len(payload).to_bytes(8, "big"))
        digest.update(payload)
    return digest.hexdigest()


def require_inputs(auth_directory: str) -> None:
    required = (
        CANONICAL_TASKS / "manifest.json",
        SNAPSHOT / "semantic" / "records.jsonl",
        SNAPSHOT / "classical" / "index.json",
        SKILL / "SKILL.md",
    )
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise ValueError("missing required inputs: " + ", ".join(missing))
    if not auth_directory.startswith("/"):
        raise ValueError("--auth-directory must be an absolute Linux path")


def copy_task(question_id: str, destination: Path) -> dict[str, str]:
    cohort = SOURCE_COHORT[question_id]
    source = CANONICAL_TASKS / cohort / question_id
    if not (source / "task.toml").is_file():
        raise ValueError(f"canonical task is incomplete: {source}")
    shutil.copytree(
        source,
        destination,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo"),
    )

    task_path = destination / "task.toml"
    task = task_path.read_text(encoding="utf-8")
    task = task.replace("__classical__", "__tantivy-consult-distillation__")
    task = task.replace('family = "classical"', 'family = "tantivy"')
    task = task.replace('"classical",', '"tantivy",')
    task = task.replace(
        "consult-only question", "Tantivy consult-only distillation question"
    )
    task_path.write_text(task, encoding="utf-8")

    instruction_path = destination / "instruction.md"
    instruction = instruction_path.read_text(encoding="utf-8")
    source_skill = "consult-semantic-okf-classical"
    if source_skill not in instruction:
        raise ValueError(f"canonical consultant identity missing: {source}")
    instruction_path.write_text(
        instruction.replace(source_skill, "consult-semantic-okf-tantivy"),
        encoding="utf-8",
    )
    return {
        "source": source.relative_to(REPO).as_posix(),
        "source_tree_sha256": tree_digest(source),
        "generated_tree_sha256": tree_digest(destination),
    }


def bind_mount(source: str, target: str, *, read_only: bool = False) -> dict[str, Any]:
    value: dict[str, Any] = {
        "type": "bind",
        "source": source,
        "target": target,
        "bind": {"create_host_path": False},
    }
    if read_only:
        value["read_only"] = True
    return value


def retry_config() -> dict[str, Any]:
    return {
        "max_retries": 0,
        "include_exceptions": [],
        "exclude_exceptions": [],
        "wait_multiplier": 1.0,
        "min_wait_sec": 1.0,
        "max_wait_sec": 60.0,
    }


def job_config(
    *,
    name: str,
    jobs_dir: str,
    task_root: str,
    task_ids: tuple[str, ...],
    snapshot: str,
    skill: str,
    auth_directory: str,
    install_only: bool = False,
) -> dict[str, Any]:
    return {
        "job_name": name,
        "jobs_dir": jobs_dir,
        "n_attempts": 1,
        "n_concurrent_trials": 1,
        "quiet": False,
        "install_only": install_only,
        "retry": retry_config(),
        "environment": {
            "type": "docker",
            "delete": True,
            "mounts": [
                bind_mount(snapshot, "/knowledge", read_only=True),
                bind_mount(auth_directory, "/root/.pi/agent"),
            ],
        },
        "agents": [
            {
                "import_path": PI_IMPORT_PATH,
                "model_name": MODEL,
                "n_concurrent": 1,
                "skills": [skill],
                "kwargs": {"version": PI_VERSION, "thinking": "high"},
                "env": {"PI_CODING_AGENT_DIR": "/root/.pi/agent"},
            }
        ],
        "datasets": [{"path": task_root, "task_names": list(task_ids)}],
    }


def main() -> int:
    args = parse_args()
    require_inputs(args.auth_directory)
    output = (
        args.output.resolve()
        if args.output
        else (HERE / "generated" / f"trace-distillation-{args.run_id}").resolve()
    )
    allowed = (HERE / "generated").resolve()
    if not output.is_relative_to(allowed) or output == allowed:
        raise ValueError(f"output must be a child of {allowed}")
    if output.exists():
        raise ValueError(f"output already exists: {output}")

    task_records: dict[str, dict[str, str]] = {}
    for phase, question_ids in (("discovery", DISCOVERY), ("holdout", HOLDOUT)):
        for question_id in question_ids:
            destination = output / "tasks" / phase / question_id
            task_records[question_id] = copy_task(question_id, destination)

    root_wsl = wsl_path(output)
    snapshot_wsl = wsl_path(SNAPSHOT)
    skill_wsl = wsl_path(SKILL)
    jobs_dir = f"/home/villa/harbor/tantivy-trace-{args.run_id}"
    discovery_job = job_config(
        name=f"tantivy-discovery-{args.run_id}",
        jobs_dir=jobs_dir,
        task_root=f"{root_wsl}/tasks/discovery",
        task_ids=DISCOVERY,
        snapshot=snapshot_wsl,
        skill=skill_wsl,
        auth_directory=args.auth_directory,
    )
    holdout_job = job_config(
        name=f"tantivy-holdout-{args.run_id}",
        jobs_dir=jobs_dir,
        task_root=f"{root_wsl}/tasks/holdout",
        task_ids=HOLDOUT,
        snapshot=snapshot_wsl,
        skill=skill_wsl,
        auth_directory=args.auth_directory,
    )
    install_smoke_job = job_config(
        name=f"tantivy-install-smoke-{args.run_id}",
        jobs_dir=f"{jobs_dir}-install-smoke",
        task_root=f"{root_wsl}/tasks/discovery",
        task_ids=(DISCOVERY[0],),
        snapshot=snapshot_wsl,
        skill=skill_wsl,
        auth_directory=args.auth_directory,
        install_only=True,
    )
    write_json(output / "jobs" / "discovery-development.json", discovery_job)
    write_json(output / "jobs" / "holdout.json", holdout_job)
    write_json(output / "jobs" / "install-smoke.json", install_smoke_job)
    write_json(
        output / "input-manifest.json",
        {
            "schema_version": "semantic-okf-tantivy-trace-distillation-inputs/1.0",
            "run_id": args.run_id,
            "model": MODEL,
            "pi_version": PI_VERSION,
            "pi_import_path": PI_IMPORT_PATH,
            "discovery": list(DISCOVERY),
            "holdout": list(HOLDOUT),
            "snapshot": SNAPSHOT.relative_to(REPO).as_posix(),
            "snapshot_tree_sha256": tree_digest(SNAPSHOT),
            "skill": SKILL.relative_to(REPO).as_posix(),
            "skill_tree_sha256": tree_digest(SKILL),
            "tasks": task_records,
            "retry": retry_config(),
        },
    )
    print(
        json.dumps(
            {
                "status": "pass",
                "output": str(output),
                "output_wsl": root_wsl,
                "discovery_job": f"{root_wsl}/jobs/discovery-development.json",
                "holdout_job": f"{root_wsl}/jobs/holdout.json",
                "install_smoke_job": f"{root_wsl}/jobs/install-smoke.json",
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
