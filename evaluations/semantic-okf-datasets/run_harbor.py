#!/usr/bin/env python3
"""Run one append-only Harbor job in build-consult or consult-only mode."""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import os
import shutil
import stat
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
GRADER = REPO / "evaluations/semantic-okf-harbor/grader"

import sys

sys.path.insert(0, str(HERE))
sys.path.insert(0, str(GRADER))
import campaign_binding as frozen  # noqa: E402
import dataset_tool as data  # noqa: E402
import generate_harbor_tasks as task_generation  # noqa: E402
from trace_status import classify_pi_trace  # noqa: E402

MODEL = "openai-codex/gpt-5.3-codex-spark"
PI_VERSION = "0.73.1"
PROVIDER_OUTCOMES = {
    "provider-quota",
    "provider-rate-limit",
    "provider-context-limit",
    "provider-error",
}
AUTH_TEMP_ROOT = Path("/tmp")
AUTH_DIRECTORY_PREFIX = "semantic-okf-dataset-harbor-auth-"
FROZEN_AUTH_SESSION_ROOT = AUTH_TEMP_ROOT / "semantic-okf-evaluation-auth-sessions"


class RunError(ValueError):
    """Raised when a requested run is not bound to checked inputs."""


def write_json(path: Path, value: Mapping[str, Any]) -> None:
    """Write stable UTF-8 JSON."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def canonical_json_bytes(value: Mapping[str, Any]) -> bytes:
    """Serialize a mapping exactly as persisted by this runner."""

    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def checked_campaign_binding(
    path: Path,
    *,
    dataset_id: str,
    family_id: str,
    task_root: Path,
    task_manifest: Mapping[str, Any],
    skill: Path,
    resource: Path,
    hf_cache: Path | None,
) -> tuple[str, dict[str, Any]]:
    """Self-verify one shard against the frozen campaign's v2 binding."""

    path = path.resolve()
    sidecar = path.with_suffix(".sha256")
    if not path.is_file() or not sidecar.is_file():
        raise RunError("frozen campaign input binding is incomplete")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        recorded = sidecar.read_text(encoding="ascii").strip().split()[0]
    except (OSError, UnicodeError, json.JSONDecodeError, IndexError) as exc:
        raise RunError("frozen campaign input binding is unreadable") from exc
    if not isinstance(value, dict) or canonical_json_bytes(value) != path.read_bytes():
        raise RunError("frozen campaign input binding is not canonical JSON")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if recorded != digest:
        raise RunError("frozen campaign input-binding SHA-256 does not verify")
    if (
        value.get("schema_version")
        != "semantic-okf-consult-campaign-input-bindings/2.0"
        or value.get("dataset_id") != dataset_id
        or value.get("mode") != "consult-only"
    ):
        raise RunError("frozen campaign input-binding identity drift")
    campaign = path.parent
    if REPO.resolve() != (campaign / "frozen/repo").resolve():
        raise RunError("frozen shard is not running from its campaign repository")
    manifest = frozen.verify_frozen_inputs(
        campaign, verify_model=family_id in {"embeddings", "ensemble"}
    )
    family = value.get("families", {}).get(family_id)
    if not isinstance(family, Mapping):
        raise RunError("frozen campaign has no family input binding")
    expected_family = {
        "consult_skill": skill.name,
        "consult_skill_tree_sha256": data.tree_digest(skill),
        "generated_tasks_tree_sha256": data.tree_digest(task_root),
        "reference_bundle_tree_sha256": data.tree_digest(resource),
        "reference_records_sha256": data.sha256_file(
            resource / "semantic/records.jsonl"
        ),
        "runtime_image": task_manifest.get("runtime_image"),
        "task_manifest_sha256": data.sha256_file(task_root / "manifest.json"),
        "offline_model_snapshot": (
            next(iter(value.get("offline_model_snapshots", {})), None)
            if family_id in {"embeddings", "ensemble"}
            else None
        ),
    }
    if dict(family) != expected_family:
        raise RunError("frozen campaign family input drift")
    if task_manifest.get("runtime_image") != value.get("runtime_image"):
        raise RunError("frozen campaign runtime image drift")
    if family_id in {"embeddings", "ensemble"}:
        expected_hf = (campaign / "frozen/model-cache/hub").resolve()
        if hf_cache is None or hf_cache.resolve() != expected_hf:
            raise RunError("frozen campaign HF mount source drift")
        model = manifest.get("offline_model")
        snapshots = value.get("offline_model_snapshots")
        if not isinstance(snapshots, Mapping) or list(snapshots.values()) != [model]:
            raise RunError("frozen campaign offline model binding drift")
    return digest, value


def resolve_skill(expected_name: str, supplied: Path | None) -> Path:
    """Resolve one runnable local skill without silently changing its strategy identity."""

    candidate = (supplied or REPO / "skills" / expected_name).resolve()
    if not (candidate / "SKILL.md").is_file():
        raise RunError(f"skill is absent or incomplete: {candidate}")
    return candidate


def frozen_auth_session_directory(binding_digest: str) -> Path:
    """Return the exact private, non-artifact session directory for one binding."""

    if (
        len(binding_digest) != 64
        or any(character not in "0123456789abcdef" for character in binding_digest)
    ):
        raise RunError("frozen auth session identity is invalid")
    return FROZEN_AUTH_SESSION_ROOT / binding_digest


def validate_auth_file(auth_file: Path) -> None:
    """Require one regular OpenAI Codex credential file without exposing its content."""

    if auth_file.is_symlink() or not auth_file.is_file():
        raise RunError(f"Pi authentication file is absent or unsafe: {auth_file}")
    try:
        auth = json.loads(auth_file.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise RunError("Pi authentication file is not valid UTF-8 JSON") from exc
    if not isinstance(auth, dict) or not auth.get("openai-codex"):
        raise RunError("Pi authentication file has no openai-codex credential")


def create_auth_dir(auth_file: Path) -> Path:
    """Create a private per-job Pi authentication directory without serializing credentials."""

    validate_auth_file(auth_file)
    directory = Path(
        tempfile.mkdtemp(prefix=AUTH_DIRECTORY_PREFIX, dir=AUTH_TEMP_ROOT)
    )
    os.chmod(directory, stat.S_IRWXU)
    target = directory / "auth.json"
    shutil.copyfile(auth_file, target)
    os.chmod(target, stat.S_IRUSR | stat.S_IWUSR)
    return directory


def execution_auth_directory(
    auth_file: Path, campaign_binding_digest: str | None
) -> tuple[Path, bool]:
    """Select a shared frozen session or an owned one-job authentication copy."""

    if campaign_binding_digest is None:
        return create_auth_dir(auth_file.expanduser().resolve()), True
    supplied_auth = auth_file.expanduser()
    expected_auth = (
        frozen_auth_session_directory(campaign_binding_digest) / "auth.json"
    )
    if supplied_auth.is_symlink() or supplied_auth.resolve() != expected_auth:
        raise RunError("frozen auth session path differs from its binding")
    validate_auth_file(supplied_auth)
    return expected_auth.parent, False


def checked_tasks(
    dataset_id: str,
    family_id: str,
    mode: str,
    cohort: str,
    requested: Sequence[str],
) -> tuple[Path, list[str], dict[str, Any]]:
    """Resolve a generated task cohort and validate the selected question IDs."""

    dataset = data.load_dataset(dataset_id)
    cohorts = data.dataset_cohorts(dataset)
    if cohort not in dataset["partition_cohorts"]:
        raise RunError(f"unknown cohort {cohort!r}; choose from: {', '.join(dataset['partition_cohorts'])}")
    allowed = cohorts[cohort]
    selected = list(requested) if requested else list(allowed)
    if len(selected) != len(set(selected)) or any(value not in allowed for value in selected):
        raise RunError("task IDs must be unique members of the selected cohort")
    root = (HERE / "generated/tasks" / dataset_id / mode / family_id).resolve()
    manifest_path = root / "manifest.json"
    if not manifest_path.is_file():
        raise RunError(f"generated tasks are absent: {root}")
    manifest = data.load_json(manifest_path)
    identity = {"dataset_id": dataset_id, "family": family_id, "mode": mode}
    if any(manifest.get(key) != value for key, value in identity.items()):
        raise RunError("generated task manifest identity mismatch")
    for identifier in selected:
        if not (root / cohort / identifier / "task.toml").is_file():
            raise RunError(f"generated task is absent: {cohort}/{identifier}")
    return root / cohort, selected, manifest


def checked_resource(
    dataset_id: str,
    family_id: str,
    mode: str,
    supplied_bundle: Path | None,
    supplied_input: Path | None,
    task_manifest: Mapping[str, Any],
) -> tuple[Path, str, dict[str, Any]]:
    """Resolve the single public data mount and bind it to the task manifest."""

    dataset = data.load_dataset(dataset_id)
    if mode == "consult-only":
        default = dataset.get("reference_bundle")
        if supplied_bundle is not None:
            resource = supplied_bundle.resolve()
        elif isinstance(default, str):
            resource = data.repo_path(default, f"{dataset_id} reference bundle")
        else:
            raise RunError("--bundle is required for consult-only because no checked bundle is declared")
        ledger = resource / "semantic/records.jsonl"
        if not ledger.is_file():
            raise RunError(f"knowledge bundle is incomplete: {resource}")
        tree_hash = data.tree_digest(resource)
        records_hash = data.sha256_file(ledger)
        if tree_hash != task_manifest.get("reference_bundle_tree_sha256"):
            raise RunError("consult-only bundle differs from the task verifier reference")
        if records_hash != task_manifest.get("reference_records_sha256"):
            raise RunError("consult-only ledger differs from the task verifier reference")
        return resource, "/knowledge", {
            "resource_kind": "processed-knowledge",
            "resource_tree_sha256": tree_hash,
            "records_sha256": records_hash,
        }

    resource = (
        supplied_input or HERE / "generated/inputs" / dataset_id / family_id
    ).resolve()
    receipt_path = resource / "input-manifest.json"
    if not receipt_path.is_file():
        raise RunError(f"prepared raw input is absent: {resource}")
    receipt = data.load_json(receipt_path)
    if receipt.get("dataset_id") != dataset_id or receipt.get("family") != family_id:
        raise RunError("prepared input identity mismatch")
    payload_hash = data.tree_digest(resource, exclude={"input-manifest.json"})
    full_hash = data.tree_digest(resource)
    if payload_hash != receipt.get("payload_tree_sha256"):
        raise RunError("prepared input payload drift")
    if full_hash != task_manifest.get("staged_input_tree_sha256"):
        raise RunError("prepared input differs from the generated build-consult tasks")
    return resource, "/dataset", {
        "resource_kind": "raw-build-input",
        "resource_tree_sha256": full_hash,
        "payload_tree_sha256": payload_hash,
        "evaluator_material_included": receipt.get("evaluator_material_included"),
    }


def bind_mount(source: str, target: str, *, read_only: bool = False) -> dict[str, Any]:
    """Build one Harbor bind-mount entry."""

    result: dict[str, Any] = {
        "type": "bind",
        "source": source,
        "target": target,
        "bind": {"create_host_path": False},
    }
    if read_only:
        result["read_only"] = True
    return result


def job_config(
    *,
    output: Path,
    tasks_path: Path,
    task_ids: Sequence[str],
    attempts: int,
    skills: Sequence[Path],
    resource: Path,
    resource_target: str,
    auth_source: str,
    hf_cache: Path | None,
) -> dict[str, Any]:
    """Build a deterministic Harbor configuration for one mode-isolated job."""

    mounts = [
        bind_mount(str(resource), resource_target, read_only=True),
        bind_mount(auth_source, "/root/.pi/agent"),
    ]
    if hf_cache is not None:
        mounts.append(bind_mount(str(hf_cache), "/models/huggingface/hub", read_only=True))
    return {
        "job_name": output.name,
        "jobs_dir": str(output.parent),
        "n_attempts": attempts,
        "n_concurrent_trials": 1,
        "quiet": False,
        "retry": {"max_retries": 0},
        "environment": {"type": "docker", "delete": True, "mounts": mounts},
        "agents": [
            {
                "name": "pi",
                "model_name": MODEL,
                "n_concurrent": 1,
                "skills": [str(path) for path in skills],
                "kwargs": {"version": PI_VERSION, "thinking": "high"},
                "env": {"PI_CODING_AGENT_DIR": "/root/.pi/agent"},
            }
        ],
        "datasets": [{"path": str(tasks_path), "task_names": list(task_ids)}],
    }


def completed_trace_outcomes(output: Path) -> dict[str, int]:
    """Return redacted terminal Pi outcome counts for a completed Harbor output tree."""

    outcomes = Counter(
        str(classify_pi_trace(path)["outcome"])
        for path in sorted(output.glob("q*__*/artifacts/pi.jsonl"))
    )
    return dict(sorted(outcomes.items()))


def completion_status(harbor_exit_code: int, outcomes: Mapping[str, int]) -> dict[str, Any]:
    """Derive the durable receipt state and effective exit code for one live job."""

    provider_failure = any(outcomes.get(outcome, 0) for outcome in PROVIDER_OUTCOMES)
    wrapper_exit_code = (
        128 + abs(harbor_exit_code) if harbor_exit_code < 0 else harbor_exit_code
    )
    return {
        "provider_failure_detected": provider_failure,
        "run_status": (
            "provider-failure"
            if provider_failure
            else "completed"
            if harbor_exit_code == 0
            else "runner-failure"
        ),
        "effective_exit_code": 2 if provider_failure and wrapper_exit_code == 0 else wrapper_exit_code,
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse one bounded dual-mode Harbor execution."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", choices=data.available_datasets(), required=True)
    parser.add_argument("--family", choices=sorted(data.load_families()), required=True)
    parser.add_argument("--mode", choices=task_generation.MODES, required=True)
    parser.add_argument("--cohort", required=True)
    parser.add_argument("--task-id", action="append", default=[])
    parser.add_argument("--bundle", type=Path)
    parser.add_argument("--input", type=Path)
    parser.add_argument("--consult-skill", type=Path)
    parser.add_argument("--build-skill", type=Path)
    parser.add_argument("--hf-cache", type=Path)
    parser.add_argument("--auth-file", type=Path, default=Path.home() / ".pi/agent/auth.json")
    parser.add_argument("--attempts", type=int, default=1)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--harbor", default="harbor")
    parser.add_argument("--frozen-campaign", action="store_true")
    parser.add_argument("--input-bindings", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    if args.attempts < 1:
        parser.error("--attempts must be positive")
    if args.mode == "consult-only" and args.build_skill is not None:
        parser.error("--build-skill is forbidden in consult-only mode")
    if args.mode == "build-consult" and args.bundle is not None:
        parser.error("--bundle is forbidden in build-consult mode")
    if args.mode == "consult-only" and args.input is not None:
        parser.error("--input is forbidden in consult-only mode")
    if args.frozen_campaign != (args.input_bindings is not None):
        parser.error("--frozen-campaign and --input-bindings must be used together")
    if args.frozen_campaign and args.mode != "consult-only":
        parser.error("--frozen-campaign is supported only for consult-only mode")
    if not args.dry_run and os.name != "posix":
        parser.error("live Harbor execution must run inside Linux or WSL; --dry-run is cross-platform")
    return args


def main(argv: Sequence[str] | None = None) -> int:
    """Create a redacted receipt, optionally execute Harbor, and destroy copied auth."""

    args = parse_args(argv)
    try:
        if not args.frozen_campaign:
            data.validate_dataset(args.dataset, args.family)
        family = data.load_families()[args.family]
        tasks_path, task_ids, task_manifest = checked_tasks(
            args.dataset, args.family, args.mode, args.cohort, args.task_id
        )
        resource, resource_target, resource_receipt = checked_resource(
            args.dataset,
            args.family,
            args.mode,
            args.bundle,
            args.input,
            task_manifest,
        )
        consult_skill = resolve_skill(family["consult_skill"], args.consult_skill)
        skills = [consult_skill]
        if args.mode == "build-consult":
            skills.insert(0, resolve_skill(family["build_skill"], args.build_skill))

        hf_cache: Path | None = None
        if family["requires_hf_cache"]:
            if args.hf_cache is None:
                raise RunError(f"{args.family} requires --hf-cache")
            hf_cache = args.hf_cache.resolve()
            if not hf_cache.is_dir():
                raise RunError(f"Hugging Face cache is absent: {hf_cache}")
        elif args.hf_cache is not None:
            raise RunError("--hf-cache is valid only for embedding-backed families")

        campaign_binding_digest: str | None = None
        campaign_binding: dict[str, Any] | None = None
        if args.frozen_campaign:
            campaign_binding_digest, campaign_binding = checked_campaign_binding(
                args.input_bindings,
                dataset_id=args.dataset,
                family_id=args.family,
                task_root=tasks_path.parent,
                task_manifest=task_manifest,
                skill=consult_skill,
                resource=resource,
                hf_cache=hf_cache,
            )

        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        default_name = f"{stamp}-{args.dataset}-{args.mode}-{args.family}-{args.cohort}"
        output = (args.output or HERE / "results" / default_name).resolve()
        if output.exists():
            raise RunError(f"append-only output already exists: {output}")
        output.parent.mkdir(parents=True, exist_ok=True)

        receipt: dict[str, Any] = {
            "schema_version": (
                "semantic-okf-evaluation-harbor-run/3.0"
                if args.frozen_campaign
                else "semantic-okf-evaluation-harbor-run/2.0"
            ),
            "dataset_id": args.dataset,
            "family": args.family,
            "mode": args.mode,
            "cohort": args.cohort,
            "task_ids": task_ids,
            "attempts": args.attempts,
            "model": MODEL,
            "pi_version": PI_VERSION,
            "installed_skills": [
                {"path": str(path), "tree_sha256": data.tree_digest(path)} for path in skills
            ],
            "public_mount_target": resource_target,
            "prebuilt_knowledge_mounted": resource_target == "/knowledge",
            "raw_sources_mounted": resource_target == "/dataset",
            "generated_tasks_manifest_sha256": data.sha256_file(tasks_path.parent / "manifest.json"),
            "authentication_serialized": False,
            "agent_network_enforcement": False,
            "verifier_network_enforcement": False,
            "run_status": "prepared",
            **resource_receipt,
        }
        if campaign_binding_digest is not None and campaign_binding is not None:
            receipt.update(
                {
                    "campaign_input_bindings_sha256": campaign_binding_digest,
                    "frozen_inputs_manifest_sha256": campaign_binding[
                        "frozen_inputs"
                    ]["manifest_sha256"],
                    "runtime_image": campaign_binding["runtime_image"],
                    "runtime_image_id": campaign_binding["runtime_image_id"],
                    "authentication_continuity": "binding-scoped-shared-session",
                }
            )

        if args.dry_run:
            config = job_config(
                output=output,
                tasks_path=tasks_path,
                task_ids=task_ids,
                attempts=args.attempts,
                skills=skills,
                resource=resource,
                resource_target=resource_target,
                auth_source="<ephemeral-auth-directory>",
                hf_cache=hf_cache,
            )
            output.mkdir()
            receipt["run_status"] = "dry-run"
            receipt["harbor_exit_code"] = None
            receipt["terminal_outcomes"] = {}
            receipt["provider_failure_detected"] = False
            receipt["job_config_redacted_sha256"] = hashlib.sha256(
                canonical_json_bytes(config)
            ).hexdigest()
            write_json(output / "job-config.redacted.json", config)
            write_json(output / "run-receipt.json", receipt)
            print(json.dumps({"status": "dry-run", "output": str(output), **receipt}, sort_keys=True))
            return 0

        auth_dir, owns_auth_dir = execution_auth_directory(
            args.auth_file, campaign_binding_digest
        )
        try:
            config = job_config(
                output=output,
                tasks_path=tasks_path,
                task_ids=task_ids,
                attempts=args.attempts,
                skills=skills,
                resource=resource,
                resource_target=resource_target,
                auth_source=str(auth_dir),
                hf_cache=hf_cache,
            )
            redacted = json.loads(json.dumps(config))
            for mount in redacted["environment"]["mounts"]:
                if mount["target"] == "/root/.pi/agent":
                    mount["source"] = "<ephemeral-auth-directory>"
            receipt["job_config_redacted_sha256"] = hashlib.sha256(
                canonical_json_bytes(redacted)
            ).hexdigest()
            with tempfile.TemporaryDirectory(prefix="semantic-okf-dataset-harbor-config-") as temporary:
                config_path = Path(temporary) / "job-config.json"
                write_json(config_path, config)
                started_at = datetime.now(timezone.utc)
                completed = subprocess.run(
                    [args.harbor, "run", "-c", str(config_path), "--yes"], cwd=REPO
                )
                finished_at = datetime.now(timezone.utc)
            if args.frozen_campaign:
                checked_campaign_binding(
                    args.input_bindings,
                    dataset_id=args.dataset,
                    family_id=args.family,
                    task_root=tasks_path.parent,
                    task_manifest=task_manifest,
                    skill=consult_skill,
                    resource=resource,
                    hf_cache=hf_cache,
                )
            output.mkdir(parents=True, exist_ok=True)
            outcomes = completed_trace_outcomes(output)
            completion = completion_status(completed.returncode, outcomes)
            receipt.update(
                {
                    "run_started_at": started_at.isoformat(),
                    "run_finished_at": finished_at.isoformat(),
                    "harbor_exit_code": completed.returncode,
                    "terminal_outcomes": outcomes,
                    "provider_failure_detected": completion["provider_failure_detected"],
                    "run_status": completion["run_status"],
                }
            )
            write_json(output / "job-config.redacted.json", redacted)
            write_json(output / "run-receipt.json", receipt)
            return int(completion["effective_exit_code"])
        finally:
            if owns_auth_dir:
                shutil.rmtree(auth_dir, ignore_errors=True)
    except (data.DatasetError, frozen.BindingError, RunError, OSError) as exc:
        raise SystemExit(str(exc)) from exc


if __name__ == "__main__":
    raise SystemExit(main())
