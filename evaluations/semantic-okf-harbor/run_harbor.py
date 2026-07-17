#!/usr/bin/env python3
"""Run one append-only Harbor family/generation job from Linux or WSL."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import stat
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
RUN = REPO / "evaluations/semantic-okf-astro/results/runs/20260716-astro-generic-01/bundles"
FAMILIES = {
    "legacy": ("legacy-a", "consult-semantic-okf"),
    "embeddings": ("embeddings-a", "consult-semantic-okf-embeddings"),
    "classical": ("classical-a", "consult-semantic-okf-classical"),
    "adaptive": ("adaptive-a", "consult-semantic-okf-adaptive"),
    "entity-graph": ("entity-graph-a", "consult-semantic-okf-entity-graph"),
    "ensemble": ("ensemble-a", "consult-semantic-okf-ensemble"),
}
ATTEMPTS = {"train": 1, "dev": 1, "holdout": 1}


def checked_ids(split: str) -> list[str]:
    """Return the checked IDs for one cohort."""

    value = json.loads((HERE / "splits.json").read_text(encoding="utf-8"))
    return list(value["cohorts"][split])


def resolve_skill(family: str, generation: str, supplied: Path | None) -> Path:
    """Resolve exactly one immutable local snapshot."""

    if supplied is not None:
        candidates = [supplied.resolve()]
    else:
        root = HERE / "snapshots/content" / generation / family
        candidates = sorted(path for path in root.glob("*") if (path / "SKILL.md").is_file()) if root.is_dir() else []
    if len(candidates) != 1 or not (candidates[0] / "SKILL.md").is_file():
        raise SystemExit(f"exactly one frozen {generation} skill snapshot is required for {family}")
    return candidates[0]


def create_auth_dir(auth_file: Path) -> Path:
    """Create a private per-job Pi authentication directory without logging content."""

    if not auth_file.is_file():
        raise SystemExit(f"Pi authentication file is absent: {auth_file}")
    try:
        auth = json.loads(auth_file.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise SystemExit("Pi authentication file is not valid UTF-8 JSON") from exc
    if not isinstance(auth, dict) or not auth.get("openai-codex"):
        raise SystemExit("Pi authentication file has no openai-codex credential")
    directory = Path(tempfile.mkdtemp(prefix="semantic-okf-harbor-auth-"))
    os.chmod(directory, stat.S_IRWXU)
    target = directory / "auth.json"
    shutil.copyfile(auth_file, target)
    os.chmod(target, stat.S_IRUSR | stat.S_IWUSR)
    return directory


def tree_sha256(root: Path) -> str:
    """Hash a bounded file tree without serializing its contents."""

    rows = []
    for path in sorted(item for item in root.rglob("*") if item.is_file() and "__pycache__" not in item.parts):
        rows.append(
            {
                "path": path.relative_to(root).as_posix(),
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }
        )
    encoded = json.dumps(rows, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def job_config(args: argparse.Namespace, output: Path, auth_dir: Path, skill: Path, tasks: list[str]) -> dict[str, Any]:
    """Build one single-skill, single-bundle Harbor job configuration."""

    bundle = (args.bundle or (RUN / FAMILIES[args.family][0])).resolve()
    if not (bundle / "semantic/records.jsonl").is_file():
        raise SystemExit(f"published family bundle is absent: {bundle}")
    mounts: list[dict[str, Any]] = [
        {"type": "bind", "source": str(bundle), "target": "/knowledge", "read_only": True, "bind": {"create_host_path": False}},
        {"type": "bind", "source": str(auth_dir), "target": "/root/.pi/agent", "bind": {"create_host_path": False}},
    ]
    if args.hf_cache is not None:
        if args.family not in {"embeddings", "ensemble"}:
            raise SystemExit("--hf-cache is only valid for embedding-backed families")
        cache = args.hf_cache.resolve()
        if not cache.is_dir():
            raise SystemExit(f"Hugging Face cache is absent: {cache}")
        mounts.append({"type": "bind", "source": str(cache), "target": "/models/huggingface/hub", "read_only": True, "bind": {"create_host_path": False}})
    return {
        "job_name": output.name,
        "jobs_dir": str(output.parent),
        "n_attempts": args.attempts or ATTEMPTS[args.split],
        "n_concurrent_trials": 1,
        "quiet": False,
        "retry": {"max_retries": 0},
        "environment": {"type": "docker", "delete": True, "mounts": mounts},
        "agents": [{
            "name": "pi",
            "model_name": "openai-codex/gpt-5.3-codex-spark",
            "n_concurrent": 1,
            "skills": [str(skill)],
            "kwargs": {"version": "0.73.1", "thinking": "high"},
            "env": {"PI_CODING_AGENT_DIR": "/root/.pi/agent"},
        }],
        "datasets": [{
            "path": str((HERE / "generated/tasks" / args.split).resolve()),
            "task_names": tasks,
        }],
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse one bounded Harbor execution."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--family", choices=tuple(FAMILIES), required=True)
    parser.add_argument("--generation", choices=("baseline", "evolved"), required=True)
    parser.add_argument("--split", choices=tuple(ATTEMPTS), required=True)
    parser.add_argument("--task-id", action="append", default=[])
    parser.add_argument("--skill", type=Path)
    parser.add_argument("--bundle", type=Path)
    parser.add_argument("--hf-cache", type=Path)
    parser.add_argument("--auth-file", type=Path, default=Path.home() / ".pi/agent/auth.json")
    parser.add_argument("--attempts", type=int)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--harbor", default="harbor")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    if os.name != "posix":
        parser.error("run_harbor.py must run inside Linux or WSL")
    if args.attempts is not None and args.attempts < 1:
        parser.error("--attempts must be positive")
    return args


def main(argv: Sequence[str] | None = None) -> int:
    """Create a redacted job config, execute Harbor, and destroy the auth copy."""

    args = parse_args(argv)
    allowed = checked_ids(args.split)
    tasks = args.task_id or allowed
    if len(tasks) != len(set(tasks)) or any(task not in allowed for task in tasks):
        raise SystemExit("task IDs must be unique members of the selected split")
    skill = resolve_skill(args.family, args.generation, args.skill)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output = (args.output or (HERE / "results" / f"{stamp}-{args.family}-{args.split}-{args.generation}")).resolve()
    if output.exists():
        raise SystemExit(f"append-only output already exists: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    auth_dir = create_auth_dir(args.auth_file.expanduser().resolve())
    try:
        config = job_config(args, output, auth_dir, skill, tasks)
        bundle = (args.bundle or (RUN / FAMILIES[args.family][0])).resolve()
        receipt = {
            "schema_version": "semantic-okf-harbor-run-receipt/1.0",
            "family": args.family,
            "generation": args.generation,
            "split": args.split,
            "task_ids": tasks,
            "attempts": config["n_attempts"],
            "model": "openai-codex/gpt-5.3-codex-spark",
            "pi_version": "0.73.1",
            "sole_skill": str(skill),
            "skill_tree_sha256": tree_sha256(skill),
            "bundle_tree_sha256": tree_sha256(bundle),
            "authentication_serialized": False,
            "agent_network_enforcement": False,
            "verifier_network_enforcement": False,
        }
        redacted_config = json.loads(json.dumps(config))
        for mount in redacted_config["environment"]["mounts"]:
            if mount["target"] == "/root/.pi/agent":
                mount["source"] = "<ephemeral-auth-directory>"
        if args.dry_run:
            output.mkdir()
            config_path = output / "job-config.redacted.json"
            config_path.write_text(json.dumps(redacted_config, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            (output / "run-receipt.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            print(json.dumps({"status": "dry-run", "config": str(config_path), **receipt}, sort_keys=True))
            return 0
        with tempfile.TemporaryDirectory(prefix="semantic-okf-harbor-config-") as config_dir:
            config_path = Path(config_dir) / "job-config.json"
            config_path.write_text(json.dumps(config, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            completed = subprocess.run([args.harbor, "run", "-c", str(config_path), "--yes"], cwd=REPO)
        output.mkdir(parents=True, exist_ok=True)
        (output / "job-config.redacted.json").write_text(
            json.dumps(redacted_config, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        (output / "run-receipt.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return completed.returncode
    finally:
        shutil.rmtree(auth_dir, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
