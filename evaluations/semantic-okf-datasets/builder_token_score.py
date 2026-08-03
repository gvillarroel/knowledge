#!/usr/bin/env python3
"""Score one single-folder Semantic OKF builder token-efficiency trial."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any, Mapping


CORE_FILES = (
    "index.md",
    "semantic/build-report.json",
    "semantic/records.jsonl",
    "semantic/validation-report.ttl",
)


def sha256_file(path: Path) -> str:
    """Return the SHA-256 digest of one regular file."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def inventory(root: Path) -> list[tuple[str, str]]:
    """Return a stable regular-file inventory for one generated folder."""

    return [
        (path.relative_to(root).as_posix(), sha256_file(path))
        for path in sorted(
            root.rglob("*"),
            key=lambda item: item.relative_to(root).as_posix().encode("utf-8"),
        )
        if path.is_file() and not path.is_symlink()
    ]


def tree_digest(root: Path) -> str:
    """Hash one folder tree with the frozen study's path-and-byte contract."""

    entries = list(root.rglob("*"))
    entries.sort(
        key=lambda path: path.relative_to(root).as_posix().encode("utf-8")
    )
    digest = hashlib.sha256()
    for path in entries:
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            raise ValueError(f"symbolic link is forbidden: {relative}")
        digest.update(("D:" if path.is_dir() else "F:").encode())
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        if path.is_file():
            digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def load_json(path: Path) -> Mapping[str, Any] | None:
    """Read a JSON object, returning ``None`` for malformed input."""

    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return None
    return value if isinstance(value, Mapping) else None


def records_count(path: Path) -> int | None:
    """Count non-empty JSONL records while rejecting malformed rows."""

    count = 0
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            value = json.loads(line)
            if not isinstance(value, Mapping):
                return None
            count += 1
    except (OSError, UnicodeError, json.JSONDecodeError):
        return None
    return count


def bundle_checks(
    root: Path,
    *,
    expected_records_sha256: str,
    expected_records_count: int,
    family_sentinel: str,
) -> dict[str, Any]:
    """Inspect one generated folder using mechanical, family-aware gates."""

    required_paths = (*CORE_FILES, family_sentinel)
    required = {
        relative: (root / relative).is_file() for relative in required_paths
    }
    unsafe_links = (
        [
            path.relative_to(root).as_posix()
            for path in root.rglob("*")
            if path.is_symlink()
        ]
        if root.is_dir()
        else []
    )
    records = root / "semantic/records.jsonl"
    build_report = load_json(root / "semantic/build-report.json")
    validation_path = root / "semantic/validation-report.ttl"
    try:
        validation_text = validation_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        validation_text = ""
    observed_records_sha256 = (
        sha256_file(records)
        if records.is_file() and not records.is_symlink()
        else None
    )
    observed_records_count = (
        records_count(records)
        if records.is_file() and not records.is_symlink()
        else None
    )
    report_valid = bool(
        build_report
        and build_report.get("status") == "pass"
        and build_report.get("valid") is True
        and build_report.get("errors") == []
    )
    validation_conforms = bool(
        re.search(
            r"shacl#conforms>\s+\"true\"",
            validation_text,
            flags=re.IGNORECASE,
        )
    )
    records_identity = bool(
        observed_records_sha256 == expected_records_sha256
        and observed_records_count == expected_records_count
    )
    artifact_integrity = bool(
        root.is_dir()
        and all(required.values())
        and not unsafe_links
        and report_valid
        and validation_conforms
    )
    return {
        "exists": root.is_dir(),
        "required_files": required,
        "unsafe_links": unsafe_links,
        "build_report_valid": report_valid,
        "validation_conforms": validation_conforms,
        "observed_records_sha256": observed_records_sha256,
        "observed_records_count": observed_records_count,
        "records_identity": records_identity,
        "artifact_integrity": artifact_integrity,
        "file_count": len(inventory(root)) if root.is_dir() else 0,
        "tree_sha256": tree_digest(root) if root.is_dir() else None,
    }


def tool_commands(pi_log: Path) -> list[str]:
    """Extract distinct shell commands from supported Pi JSONL event shapes."""

    commands: list[str] = []
    seen_call_ids: set[str] = set()
    if not pi_log.is_file():
        return commands
    for line in pi_log.read_text(
        encoding="utf-8", errors="replace"
    ).splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if (
            event.get("type") == "tool_execution_start"
            and event.get("toolName") == "bash"
        ):
            arguments = event.get("arguments")
            if isinstance(arguments, Mapping) and isinstance(
                arguments.get("command"), str
            ):
                call_id = event.get("toolCallId")
                if isinstance(call_id, str):
                    if call_id in seen_call_ids:
                        continue
                    seen_call_ids.add(call_id)
                commands.append(arguments["command"])
        message = event.get("message")
        if not isinstance(message, Mapping):
            continue
        content = message.get("content")
        if not isinstance(content, list):
            continue
        for item in content:
            if not isinstance(item, Mapping) or item.get("type") != "toolCall":
                continue
            arguments = item.get("arguments")
            if not isinstance(arguments, Mapping) or not isinstance(
                arguments.get("command"), str
            ):
                continue
            call_id = item.get("id")
            if isinstance(call_id, str):
                if call_id in seen_call_ids:
                    continue
                seen_call_ids.add(call_id)
            commands.append(arguments["command"])
    return commands


def command_checks(
    commands: list[str],
    *,
    build_script: str,
    validate_script: str,
    outputs: list[str],
) -> dict[str, Any]:
    """Check that the trace reflects the bounded offline builder workflow."""

    joined = "\n".join(commands)
    lowered = joined.casefold()
    network_install = any(
        token in lowered
        for token in (
            "pip install",
            "apt-get",
            "apt install",
            "curl ",
            "wget ",
            "npm install",
        )
    )
    destructive_destination = bool(
        re.search(
            r"\b(?:rm|rmdir)\b[^\n]*?/workspace/"
            r"(?:knowledge|release|candidate|snapshot)",
            lowered,
        )
    )
    build_command_count = sum(
        build_script in command and "--help" not in command
        for command in commands
    )
    validation_command_count = sum(
        validate_script in command and "--help" not in command
        for command in commands
    )
    output_coverage = {
        output: output in joined for output in outputs
    }
    invocation_coverage = bool(
        build_command_count == 1
        and validation_command_count == 1
        and all(output_coverage.values())
    )
    workflow_safety = not network_install and not destructive_destination
    return {
        "command_count": len(commands),
        "build_command_count": build_command_count,
        "validation_command_count": validation_command_count,
        "output_coverage": output_coverage,
        "network_install": network_install,
        "destructive_destination": destructive_destination,
        "invocation_coverage_gate": float(invocation_coverage),
        "workflow_safety_gate": float(workflow_safety),
    }


def write_json(path: Path, value: Mapping[str, Any]) -> None:
    """Write one stable verifier artifact."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def score(
    config: Mapping[str, Any],
    pi_log: Path,
) -> tuple[dict[str, float], dict[str, Any]]:
    """Score one valid, bounded single-folder builder execution."""

    outputs = config.get("outputs")
    if (
        not isinstance(outputs, list)
        or len(outputs) != 1
        or any(not isinstance(value, str) for value in outputs)
    ):
        raise ValueError("task config must declare exactly one output path")
    expected_records_sha256 = config.get("expected_records_sha256")
    if not isinstance(expected_records_sha256, str):
        raise ValueError("expected_records_sha256 must be a string")
    expected_records_count = config.get("expected_records_count")
    if (
        not isinstance(expected_records_count, int)
        or isinstance(expected_records_count, bool)
        or expected_records_count <= 0
    ):
        raise ValueError("expected_records_count must be positive")
    family_sentinel = config.get("family_sentinel")
    build_script = config.get("build_script")
    validate_script = config.get("validate_script")
    if any(
        not isinstance(value, str) or not value
        for value in (family_sentinel, build_script, validate_script)
    ):
        raise ValueError("family and command bindings must be non-empty")

    roots = [Path(value) for value in outputs]
    bundles = [
        bundle_checks(
            root,
            expected_records_sha256=expected_records_sha256,
            expected_records_count=expected_records_count,
            family_sentinel=family_sentinel,
        )
        for root in roots
    ]
    artifact_gate = float(
        all(bundle["artifact_integrity"] for bundle in bundles)
    )
    records_gate = float(
        all(bundle["records_identity"] for bundle in bundles)
    )
    commands = command_checks(
        tool_commands(pi_log),
        build_script=build_script,
        validate_script=validate_script,
        outputs=outputs,
    )
    components = (
        artifact_gate,
        records_gate,
        commands["workflow_safety_gate"],
        commands["invocation_coverage_gate"],
    )
    rewards = {
        "reward": sum(components) / len(components),
        "artifact_integrity_gate": artifact_gate,
        "records_identity_gate": records_gate,
        "workflow_safety_gate": float(commands["workflow_safety_gate"]),
        "invocation_coverage_gate": float(
            commands["invocation_coverage_gate"]
        ),
    }
    diagnostics = {
        "schema_version": "semantic-okf-builder-token-diagnostics/2.0",
        "status": (
            "qualified-single-folder"
            if all(value == 1.0 for value in components)
            else "unqualified-single-folder"
        ),
        "failure_domain": None,
        "terminal_outcome": "builder-scored",
        "error_code": None,
        "family": config.get("family"),
        "outputs": outputs,
        "bundles": bundles,
        "commands": commands,
    }
    return rewards, diagnostics


def main() -> int:
    """Run the direct-builder verifier."""

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
        if not isinstance(config, Mapping):
            raise ValueError("task config must be a JSON object")
        rewards, diagnostics = score(config, args.pi_log)
    except (OSError, UnicodeError, ValueError, TypeError, json.JSONDecodeError) as error:
        rewards = {
            "reward": 0.0,
            "artifact_integrity_gate": 0.0,
            "records_identity_gate": 0.0,
            "workflow_safety_gate": 0.0,
            "invocation_coverage_gate": 0.0,
        }
        diagnostics = {
            "schema_version": "semantic-okf-builder-token-diagnostics/2.0",
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
