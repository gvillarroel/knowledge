#!/usr/bin/env python3
"""Score a direct Tika/MALLET builder trial without consulting the snapshot."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any


EXPECTED_RECORDS_SHA256 = (
    "b64917f411ea57a18114ba44d7a4779564d528542b3c6ec6084d96a4ddf40805"
)
EXPECTED_RECORD_COUNT = 30
CANONICAL_JAVA = "/usr/lib/jvm/java-17-openjdk-amd64/bin/java"
REQUIRED_FILES = (
    "index.md",
    "semantic/records.jsonl",
    "semantic/build-report.json",
    "semantic/validation-report.ttl",
    "tika/index.json",
    "tika/documents.jsonl",
    "classical/index.json",
    "classical/documents.jsonl",
    "classical/associations.jsonl",
    "classical/lexicon.json",
    "classical/topics.json",
    "classical/build-report.json",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def inventory(root: Path) -> list[tuple[str, str]]:
    return [
        (path.relative_to(root).as_posix(), sha256_file(path))
        for path in sorted(root.rglob("*"))
        if path.is_file() and not path.is_symlink()
    ]


def jsonl_count(path: Path) -> int:
    count = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            value = json.loads(line)
            if not isinstance(value, dict):
                raise ValueError("records.jsonl contains a non-object row")
            count += 1
    return count


def bundle_checks(root: Path) -> dict[str, Any]:
    required = {
        relative: (root / relative).is_file() for relative in REQUIRED_FILES
    }
    unsafe_links = [
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_symlink()
    ] if root.is_dir() else []
    records = root / "semantic" / "records.jsonl"
    records_sha256 = sha256_file(records) if records.is_file() else None
    try:
        record_count = jsonl_count(records) if records.is_file() else None
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError):
        record_count = None
    return {
        "exists": root.is_dir(),
        "required_files": required,
        "unsafe_links": unsafe_links,
        "records_sha256": records_sha256,
        "record_count": record_count,
        "artifact_integrity": (
            root.is_dir() and all(required.values()) and not unsafe_links
        ),
        "snapshot_identity": (
            records_sha256 == EXPECTED_RECORDS_SHA256
            and record_count == EXPECTED_RECORD_COUNT
        ),
    }


def tool_commands(pi_log: Path) -> list[str]:
    commands: list[str] = []
    if not pi_log.is_file():
        return commands
    for line in pi_log.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        # Pi emits the same assistant message in both message_start and
        # message_end events. Only the completed event is canonical.
        if event.get("type") != "message_end":
            continue
        message = event.get("message")
        if not isinstance(message, dict):
            continue
        content = message.get("content")
        if not isinstance(content, list):
            continue
        for item in content:
            if not isinstance(item, dict) or item.get("type") != "toolCall":
                continue
            arguments = item.get("arguments")
            if not isinstance(arguments, dict):
                continue
            command = arguments.get("command")
            if isinstance(command, str):
                commands.append(command)
    return commands


def command_checks(commands: list[str]) -> dict[str, Any]:
    joined = "\n".join(commands)
    lowered = joined.casefold()
    build_invocations = len(
        re.findall(
            r"\bbuild_semantic_okf_tika_mallet\.py\b(?!\s+--help(?:\s|$))",
            joined,
        )
    )
    validation_invocations = len(
        re.findall(
            r"\bvalidate_semantic_okf_tika_mallet\.py\b(?!\s+--help(?:\s|$))",
            joined,
        )
    )
    path_discovery = any(
        token in lowered
        for token in (
            "command -v java",
            "which java",
            "whereis java",
            "find /usr",
            "ls /usr/lib/jvm",
        )
    )
    network_install = any(
        token in lowered
        for token in (
            "pip install",
            "apt-get",
            "apt install",
            "curl ",
            "wget ",
        )
    )
    destructive_destination = bool(
        re.search(r"\brm\s+(?:-[^\s]*r[^\s]*\s+|--recursive\s+).*?/workspace/", lowered)
    )
    canonical_runtime = (
        CANONICAL_JAVA in joined
        or '"$SEMANTIC_OKF_JAVA"' in joined
        or "$SEMANTIC_OKF_JAVA" in joined
    ) and "/usr/bin/java" not in joined
    return {
        "command_count": len(commands),
        "build_invocations": build_invocations,
        "validation_invocations": validation_invocations,
        "path_discovery": path_discovery,
        "network_install": network_install,
        "destructive_destination": destructive_destination,
        "canonical_runtime": canonical_runtime,
        "runtime_contract_gate": float(
            canonical_runtime
            and not path_discovery
            and not network_install
            and not destructive_destination
        ),
        "validation_invocation_gate": float(validation_invocations >= 2),
        "workflow_efficiency": sum(
            (
                not path_discovery,
                not network_install,
                not destructive_destination,
                build_invocations == 2,
            )
        )
        / 4.0,
    }


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def score(config: dict[str, Any], pi_log: Path) -> tuple[dict[str, float], dict[str, Any]]:
    outputs = config.get("outputs")
    if (
        not isinstance(outputs, list)
        or len(outputs) != 2
        or any(not isinstance(value, str) for value in outputs)
    ):
        raise ValueError("task config must declare exactly two output paths")
    roots = [Path(value) for value in outputs]
    bundles = [bundle_checks(root) for root in roots]
    artifact_gate = float(all(bundle["artifact_integrity"] for bundle in bundles))
    identity_gate = float(all(bundle["snapshot_identity"] for bundle in bundles))
    reproducibility_gate = 0.0
    if artifact_gate:
        reproducibility_gate = float(inventory(roots[0]) == inventory(roots[1]))
    command = command_checks(tool_commands(pi_log))
    components = (
        artifact_gate,
        identity_gate,
        reproducibility_gate,
        command["runtime_contract_gate"],
        command["validation_invocation_gate"],
        command["workflow_efficiency"],
    )
    reward = sum(float(value) for value in components) / len(components)
    rewards = {
        "reward": reward,
        "artifact_integrity_gate": artifact_gate,
        "snapshot_identity_gate": identity_gate,
        "reproducibility_gate": reproducibility_gate,
        "runtime_contract_gate": float(command["runtime_contract_gate"]),
        "validation_invocation_gate": float(command["validation_invocation_gate"]),
        "workflow_efficiency": float(command["workflow_efficiency"]),
    }
    diagnostics = {
        "schema_version": "semantic-okf-builder-pareto-diagnostics/1.0",
        "status": "scored-builder",
        "failure_domain": None,
        "terminal_outcome": "builder-scored",
        "error_code": None,
        "outputs": outputs,
        "bundles": bundles,
        "commands": command,
    }
    return rewards, diagnostics


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("/tests/task-config.json"))
    parser.add_argument("--pi-log", type=Path, default=Path("/logs/agent/pi.txt"))
    parser.add_argument("--reward", type=Path, default=Path("/logs/verifier/reward.json"))
    parser.add_argument(
        "--diagnostics",
        type=Path,
        default=Path("/logs/verifier/diagnostics.json"),
    )
    args = parser.parse_args()
    try:
        config = json.loads(args.config.read_text(encoding="utf-8"))
        if not isinstance(config, dict):
            raise ValueError("task config must be a JSON object")
        rewards, diagnostics = score(config, args.pi_log)
    except (OSError, UnicodeError, ValueError, TypeError, json.JSONDecodeError) as error:
        rewards = {
            "reward": 0.0,
            "artifact_integrity_gate": 0.0,
            "snapshot_identity_gate": 0.0,
            "reproducibility_gate": 0.0,
            "runtime_contract_gate": 0.0,
            "validation_invocation_gate": 0.0,
            "workflow_efficiency": 0.0,
        }
        diagnostics = {
            "schema_version": "semantic-okf-builder-pareto-diagnostics/1.0",
            "status": "verifier-error",
            "failure_domain": "evaluator",
            "terminal_outcome": "verifier-error",
            "error_code": type(error).__name__,
        }
    write_json(args.reward, rewards)
    write_json(args.diagnostics, diagnostics)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
