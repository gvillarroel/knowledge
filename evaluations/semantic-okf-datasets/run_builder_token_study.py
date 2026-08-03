#!/usr/bin/env python3
"""Run the frozen eight-family single-folder builder token study with Harbor."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import stat
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Mapping, Sequence

import prepare_builder_token_study as preparation


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
DEFAULT_STUDY = REPO / "evaluations/semantic-okf-token-efficiency-study-v7"
DEFAULT_FROZEN = DEFAULT_STUDY / "private/frozen"
DEFAULT_JOBS = DEFAULT_STUDY / "private/native-jobs"
DEFAULT_HF_CACHE = (
    HERE
    / "generated/campaigns/20260723-papers-consult-gpt53-spark-05"
    / "frozen/model-cache/hub"
)
DEFAULT_AUTH_FILE = Path.home() / ".pi/agent/auth.json"
DEFAULT_HARBOR: str | None = None
WAVE_SCHEDULE = (
    (
        "replicate-a",
        (
            "adaptive",
            "classical",
            "embeddings",
            "ensemble",
            "entity-graph",
            "graphify",
            "legacy",
            "turso",
        ),
    ),
    (
        "replicate-b",
        (
            "entity-graph",
            "graphify",
            "legacy",
            "turso",
            "adaptive",
            "classical",
            "embeddings",
            "ensemble",
        ),
    ),
)


class StudyRunError(ValueError):
    """Raised when a builder token job is unsafe or incomplete."""


def load_object(path: Path) -> dict[str, Any]:
    """Load one JSON object."""

    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise StudyRunError(f"cannot read JSON object: {path}") from exc
    if not isinstance(value, dict):
        raise StudyRunError(f"expected a JSON object: {path}")
    return value


def verify_frozen(frozen: Path) -> dict[str, Any]:
    """Verify every digest in the frozen-input manifest."""

    manifest = load_object(frozen / "frozen-inputs.json")
    if (
        manifest.get("schema_version")
        != "semantic-okf-builder-token-frozen-inputs/3.0"
    ):
        raise StudyRunError("unsupported frozen-input manifest")
    if (
        manifest.get("model") != preparation.MODEL
        or manifest.get("pi_version") != preparation.PI_VERSION
        or manifest.get("thinking") != preparation.THINKING
        or manifest.get("runtime_image") != preparation.RUNTIME_IMAGE
        or manifest.get("runtime_image_id")
        != preparation.RUNTIME_IMAGE_ID
    ):
        raise StudyRunError("frozen execution contract drift")
    if preparation.sha256_file(frozen / "families.json") != manifest.get(
        "families_registry_sha256"
    ):
        raise StudyRunError("frozen family registry drift")
    families = manifest.get("families")
    if not isinstance(families, Mapping) or set(families) != set(
        preparation.FAMILY_SENTINELS
    ):
        raise StudyRunError("frozen family set drift")
    for family_id, record in families.items():
        if not isinstance(record, Mapping):
            raise StudyRunError(f"invalid frozen family: {family_id}")
        skill_name = record.get("build_skill")
        if not isinstance(skill_name, str):
            raise StudyRunError(f"invalid frozen skill binding: {family_id}")
        checks = {
            "input_tree_sha256": preparation.tree_digest(
                frozen / "inputs" / family_id
            ),
            "skill_tree_sha256": preparation.tree_digest(
                frozen / "skills" / skill_name
            ),
            "task_tree_sha256": preparation.tree_digest(
                frozen / "tasks/development" / family_id
            ),
            "input_manifest_sha256": preparation.sha256_file(
                frozen / "inputs" / family_id / "input-manifest.json"
            ),
        }
        for key, actual in checks.items():
            if record.get(key) != actual:
                raise StudyRunError(f"{family_id} {key} drift")
    harbor = manifest.get("harbor")
    if (
        not isinstance(harbor, Mapping)
        or harbor.get("version") != preparation.HARBOR_VERSION
        or preparation.tree_digest(frozen / "harbor/harbor")
        != harbor.get("patched_tree_sha256")
        or preparation.sha256_file(frozen / "harbor/harbor-cli")
        != harbor.get("patched_entrypoint_sha256")
        or preparation.sha256_file(
            frozen / "harbor/harbor/agents/installed/pi.py"
        )
        != harbor.get("patched_adapter_sha256")
    ):
        raise StudyRunError("frozen patched Harbor drift")
    return manifest


def docker_image_id(reference: str) -> str:
    """Resolve one local Docker image reference."""

    completed = subprocess.run(
        ["docker", "image", "inspect", "--format", "{{.Id}}", reference],
        text=True,
        capture_output=True,
        check=False,
        timeout=60,
    )
    if completed.returncode != 0:
        raise StudyRunError(
            f"cannot inspect runtime image: {completed.stderr.strip()}"
        )
    return completed.stdout.strip()


def docker_runtime_preflight(reference: str) -> None:
    """Prove the exact Node and Pi versions before any Harbor/model call."""

    command = (
        "set -euo pipefail; "
        'test "$(node --version)" = "v22.23.1"; '
        "grep -Fq '\"version\": \"0.73.1\"' "
        "/opt/semantic-okf/pi-coding-agent/node_modules/"
        "@mariozechner/pi-coding-agent/package.json"
    )
    completed = subprocess.run(
        ["docker", "run", "--rm", reference, "bash", "-lc", command],
        text=True,
        capture_output=True,
        check=False,
        timeout=60,
    )
    if completed.returncode != 0:
        raise StudyRunError(
            "runtime Node/Pi preflight failed without a model call"
        )


def bind_mount(source: Path, target: str, *, read_only: bool) -> dict[str, Any]:
    """Build one explicit Harbor bind mount."""

    result: dict[str, Any] = {
        "type": "bind",
        "source": str(source),
        "target": target,
        "bind": {"create_host_path": False},
    }
    if read_only:
        result["read_only"] = True
    return result


def job_name(family_id: str, replicate: str) -> str:
    """Return the append-only native job name."""

    return (
        "20260730-graphrag-papers-builder-token-single-spark-v2-"
        f"{replicate}-{family_id}"
    )


def job_config(
    *,
    frozen: Path,
    jobs: Path,
    manifest: Mapping[str, Any],
    family_id: str,
    replicate: str,
    auth_directory: Path,
    hf_cache: Path,
) -> dict[str, Any]:
    """Build one single-trial Harbor job configuration."""

    family = manifest["families"][family_id]
    mounts = [
        bind_mount(
            frozen / "inputs" / family_id,
            "/dataset",
            read_only=True,
        ),
        bind_mount(auth_directory, "/root/.pi/agent", read_only=False),
    ]
    if family["requires_hf_cache"]:
        mounts.append(
            bind_mount(
                hf_cache,
                "/models/huggingface/hub",
                read_only=True,
            )
        )
    return {
        "job_name": job_name(family_id, replicate),
        "jobs_dir": str(jobs),
        "agent_timeout_multiplier": 1.0,
        "n_concurrent_trials": 1,
        "retry": {
            "max_retries": 0,
            "include_exceptions": [],
            "exclude_exceptions": [
                "AgentTimeoutError",
                "ApiUsageLimitError",
                "RewardFileEmptyError",
                "RewardFileNotFoundError",
                "VerifierOutputParseError",
                "VerifierTimeoutError",
            ],
            "wait_multiplier": 1.0,
            "min_wait_sec": 1.0,
            "max_wait_sec": 60.0,
        },
        "environment": {"type": "docker", "mounts": mounts},
        "agents": [
            {
                "name": "pi",
                "model_name": manifest["model"],
                "n_concurrent": 1,
                "skills": [
                    str(
                        frozen
                        / "skills"
                        / family["build_skill"]
                    )
                ],
                "kwargs": {
                    "version": manifest["pi_version"],
                    "thinking": manifest["thinking"],
                },
                "env": {
                    "PI_CODING_AGENT_DIR": "/root/.pi/agent",
                    "HF_HUB_OFFLINE": "1",
                    "TRANSFORMERS_OFFLINE": "1",
                    "HF_HOME": "/models/huggingface",
                },
            }
        ],
        "datasets": [
            {
                "path": str(
                    frozen / "tasks/development" / family_id
                ),
                "task_names": [replicate],
            }
        ],
    }


def private_auth_copy(source: Path, destination: Path) -> None:
    """Create one private writable authentication session without hashing it."""

    if not source.is_file() or source.is_symlink():
        raise StudyRunError(f"authentication file is absent or unsafe: {source}")
    value = load_object(source)
    if not value.get("openai-codex"):
        raise StudyRunError("authentication has no openai-codex credential")
    destination.mkdir(mode=0o700)
    shutil.copy2(source, destination / "auth.json")
    os.chmod(destination / "auth.json", stat.S_IRUSR | stat.S_IWUSR)
    models_store = source.parent / "models-store.json"
    if models_store.is_file() and not models_store.is_symlink():
        shutil.copy2(models_store, destination / "models-store.json")
        os.chmod(
            destination / "models-store.json",
            stat.S_IRUSR | stat.S_IWUSR,
        )


def terminal_status(job: Path) -> dict[str, Any]:
    """Inspect the one-trial native result after Harbor returns."""

    aggregate = load_object(job / "result.json")
    trial_paths = sorted(job.glob("*__*/result.json"))
    if len(trial_paths) != 1:
        raise StudyRunError(
            f"job must contain exactly one trial result: {job}"
        )
    trial = load_object(trial_paths[0])
    agent = trial.get("agent_result")
    verifier = trial.get("verifier_result")
    rewards = verifier.get("rewards") if isinstance(verifier, Mapping) else None
    usage = (
        {
            "input": agent.get("n_input_tokens"),
            "cache": agent.get("n_cache_tokens"),
            "output": agent.get("n_output_tokens"),
        }
        if isinstance(agent, Mapping)
        else None
    )
    return {
        "job": job.name,
        "completed_trials": aggregate.get("stats", {}).get(
            "n_completed_trials"
        ),
        "errored_trials": aggregate.get("stats", {}).get(
            "n_errored_trials"
        ),
        "exception": trial.get("exception_info") is not None,
        "qualified": bool(
            isinstance(rewards, Mapping)
            and rewards.get("reward") == 1.0
        ),
        "usage": usage,
    }


def run_config(
    harbor: str,
    config: Mapping[str, Any],
    *,
    dry_run: bool,
    install_only: bool,
) -> subprocess.CompletedProcess[str]:
    """Validate or execute one Harbor configuration."""

    with tempfile.TemporaryDirectory(
        prefix="semantic-okf-builder-token-config-"
    ) as temporary:
        config_path = Path(temporary) / "job.json"
        config_path.write_text(
            json.dumps(config, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        command = [harbor, "run", "-c", str(config_path)]
        if dry_run:
            command.append("--print-config")
        elif install_only:
            command.extend(["--install-only", "--yes"])
        else:
            command.append("--yes")
        environment = os.environ.copy()
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        environment["COLUMNS"] = "120"
        environment["LINES"] = "40"
        environment["TERM"] = "xterm"
        environment.pop("PYTHONPATH", None)
        environment.pop("PYTHONHOME", None)
        return subprocess.run(
            command,
            cwd=REPO,
            env=environment,
            text=True,
            check=False,
        )


def selected_schedule(
    families: Sequence[str],
    replicates: Sequence[str],
) -> list[tuple[str, str]]:
    """Filter the fixed balanced schedule without changing its order."""

    family_set = set(families)
    replicate_set = set(replicates)
    return [
        (family_id, replicate)
        for replicate, wave in WAVE_SCHEDULE
        if replicate in replicate_set
        for family_id in wave
        if family_id in family_set
    ]


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frozen", type=Path, default=DEFAULT_FROZEN)
    parser.add_argument("--jobs", type=Path, default=DEFAULT_JOBS)
    parser.add_argument("--hf-cache", type=Path, default=DEFAULT_HF_CACHE)
    parser.add_argument("--auth-file", type=Path, default=DEFAULT_AUTH_FILE)
    parser.add_argument("--harbor", default=DEFAULT_HARBOR)
    parser.add_argument(
        "--family",
        action="append",
        choices=sorted(preparation.FAMILY_SENTINELS),
    )
    parser.add_argument(
        "--replicate",
        action="append",
        choices=sorted(preparation.REPLICATES),
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--install-only",
        action="store_true",
        help="Run one agent setup compatibility check without a model call.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    """Validate or execute the fixed builder token schedule."""

    args = parse_args(argv)
    if args.dry_run and args.install_only:
        raise StudyRunError("--dry-run and --install-only are mutually exclusive")
    frozen = args.frozen.resolve()
    jobs = args.jobs.resolve()
    hf_cache = args.hf_cache.resolve()
    manifest = verify_frozen(frozen)
    harbor = args.harbor or str(frozen / "harbor/harbor-cli")
    observed_image_id = docker_image_id(manifest["runtime_image"])
    if observed_image_id != manifest["runtime_image_id"]:
        raise StudyRunError(
            "runtime image reference does not resolve to its frozen ID"
        )
    docker_runtime_preflight(manifest["runtime_image"])
    families = args.family or sorted(preparation.FAMILY_SENTINELS)
    replicates = args.replicate or list(preparation.REPLICATES)
    schedule = selected_schedule(families, replicates)
    if not schedule:
        raise StudyRunError("filtered builder schedule is empty")
    if args.install_only and len(schedule) != 1:
        raise StudyRunError("--install-only requires exactly one selected cell")
    if any(manifest["families"][family]["requires_hf_cache"] for family, _ in schedule):
        if not hf_cache.is_dir() or hf_cache.is_symlink():
            raise StudyRunError(f"offline model cache is absent: {hf_cache}")
    install_jobs = jobs.parent / "install-preflight-jobs"
    output_root = install_jobs if args.install_only else jobs
    expected_names = [
        (
            f"{job_name(family, replicate)}-install-preflight"
            if args.install_only
            else job_name(family, replicate)
        )
        for family, replicate in schedule
    ]
    existing = [
        output_root / name
        for name in expected_names
        if (output_root / name).exists()
    ]
    if existing:
        raise StudyRunError(
            "append-only job output already exists: "
            + ", ".join(str(path) for path in existing)
        )

    output_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(
        prefix="semantic-okf-builder-token-auth-"
    ) as temporary:
        auth_directory = Path(temporary) / "agent"
        private_auth_copy(args.auth_file.resolve(), auth_directory)
        statuses: list[dict[str, Any]] = []
        for family_id, replicate in schedule:
            verify_frozen(frozen)
            if docker_image_id(manifest["runtime_image"]) != manifest[
                "runtime_image_id"
            ]:
                raise StudyRunError("runtime image drift before submitted cell")
            config = job_config(
                frozen=frozen,
                jobs=output_root,
                manifest=manifest,
                family_id=family_id,
                replicate=replicate,
                auth_directory=auth_directory,
                hf_cache=hf_cache,
            )
            if args.install_only:
                config["job_name"] = (
                    f"{config['job_name']}-install-preflight"
                )
            completed = run_config(
                harbor,
                config,
                dry_run=args.dry_run,
                install_only=args.install_only,
            )
            if completed.returncode != 0:
                raise StudyRunError(
                    f"Harbor {'validation' if args.dry_run else 'run'} "
                    f"failed for {family_id}/{replicate} with "
                    f"status {completed.returncode}"
                )
            if args.dry_run:
                statuses.append(
                    {
                        "family": family_id,
                        "replicate": replicate,
                        "status": "config-valid",
                    }
                )
                continue
            if args.install_only:
                statuses.append(
                    {
                        "family": family_id,
                        "replicate": replicate,
                        "status": "install-compatible",
                    }
                )
                continue
            status = terminal_status(jobs / job_name(family_id, replicate))
            statuses.append(status)
            print(json.dumps(status, sort_keys=True), flush=True)
            if (
                status["exception"]
                or status["usage"] is None
                or not status["qualified"]
            ):
                raise StudyRunError(
                    "stopping balanced schedule after the first failed or "
                    "unqualified "
                    f"submitted cell: {family_id}/{replicate}"
                )
            verify_frozen(frozen)
            if docker_image_id(manifest["runtime_image"]) != manifest[
                "runtime_image_id"
            ]:
                raise StudyRunError("runtime image drift after submitted cell")
    print(
        json.dumps(
            {
                "status": (
                    "dry-run"
                    if args.dry_run
                    else "install-only"
                    if args.install_only
                    else "completed"
                ),
                "new_model_calls": (
                    0
                    if args.dry_run or args.install_only
                    else len(statuses)
                ),
                "cells": statuses,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except StudyRunError as exc:
        raise SystemExit(str(exc)) from exc
