#!/usr/bin/env python3
"""Publish the exact Semantic OKF answer bytes confirmed in a Codex JSONL trace."""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Mapping, Sequence


PREPARE_TOOL = "semantic_okf_prepare_answer"
CONFIRM_TOOL = "semantic_okf_confirm_answer"
PROTOCOL_TOOLS = {PREPARE_TOOL, CONFIRM_TOOL}
SERVER = "semantic_okf"
PREPARED_ANSWER_SCHEMA = "semantic-okf-prepared-answer/1.0"
CONFIRMATION_SCHEMA = "semantic-okf-answer-confirmation-receipt/1.0"
REAL_CODEX_ENV = "SEMANTIC_OKF_REAL_CODEX"
ALLOWED_SKILLS_ENV = "SKILL_ARENA_ALLOWED_SKILLS"
ENSEMBLE_SKILL = "consult-semantic-okf-ensemble"
SHELL_ISOLATION_SCHEMA = "semantic-okf-shell-isolation-receipt/1.0"
SKILL_ID_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
PROTOCOL_EXIT = 86


class PublicationGateError(ValueError):
    """Describe a fail-closed confirmed-output publication violation."""


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise PublicationGateError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _reject_constant(value: str) -> Any:
    raise PublicationGateError(f"non-finite JSON constant is forbidden: {value}")


def strict_json(text: str, label: str) -> Any:
    """Parse strict JSON while rejecting duplicate keys and non-finite numbers."""

    try:
        return json.loads(
            text,
            object_pairs_hook=_strict_object,
            parse_constant=_reject_constant,
        )
    except (json.JSONDecodeError, PublicationGateError) as exc:
        raise PublicationGateError(f"{label} is not strict JSON: {exc}") from exc


def _exact_keys(value: Any, expected: set[str], label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise PublicationGateError(f"{label} must be an object")
    actual = set(value)
    if actual != expected:
        raise PublicationGateError(
            f"{label} uses a closed schema; missing={sorted(expected - actual)}, "
            f"unknown={sorted(actual - expected)}"
        )
    return value


def _canonical_json(value: Any) -> str:
    try:
        return json.dumps(
            value,
            ensure_ascii=False,
            separators=(",", ":"),
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise PublicationGateError(f"candidate cannot be canonicalized: {exc}") from exc


def _sha256(value: Any, label: str) -> str:
    if (
        not isinstance(value, str)
        or len(value) != 64
        or any(character not in "0123456789abcdef" for character in value)
    ):
        raise PublicationGateError(
            f"{label} must be a lowercase 64-hex SHA-256 digest"
        )
    return value


def _prepared_candidate(text: str, number: int) -> tuple[bytes, str]:
    label = f"answer prepare {number}"
    envelope = _exact_keys(
        strict_json(text, label),
        {"schema", "candidate_json", "response_sha256", "byte_count"},
        f"{label} envelope",
    )
    expected_order = ["schema", "candidate_json", "response_sha256", "byte_count"]
    if list(envelope) != expected_order or _canonical_json(envelope) != text:
        raise PublicationGateError(
            f"{label} envelope is not canonical with the required key order"
        )
    if envelope["schema"] != PREPARED_ANSWER_SCHEMA:
        raise PublicationGateError(f"{label} envelope has the wrong schema")
    candidate_json = envelope["candidate_json"]
    if not isinstance(candidate_json, str):
        raise PublicationGateError(f"{label} candidate_json must be a string")
    candidate = strict_json(candidate_json, f"{label} candidate_json")
    if not isinstance(candidate, Mapping) or _canonical_json(candidate) != candidate_json:
        raise PublicationGateError(
            f"{label} candidate_json is not canonical object JSON"
        )
    payload = candidate_json.encode("utf-8")
    digest = _sha256(envelope["response_sha256"], f"{label} response_sha256")
    byte_count = envelope["byte_count"]
    if isinstance(byte_count, bool) or not isinstance(byte_count, int):
        raise PublicationGateError(f"{label} byte_count must be an integer")
    if digest != hashlib.sha256(payload).hexdigest() or byte_count != len(payload):
        raise PublicationGateError(
            f"{label} envelope digest or length does not bind candidate_json bytes"
        )
    return payload, digest


def _result_text(item: Mapping[str, Any], label: str) -> str:
    if item.get("status") != "completed" or item.get("error") not in (None, ""):
        raise PublicationGateError(f"{label} did not complete successfully")
    result = item.get("result")
    if not isinstance(result, Mapping):
        raise PublicationGateError(f"{label} has no result object")
    content = result.get("content")
    if (
        not isinstance(content, list)
        or len(content) != 1
        or not isinstance(content[0], Mapping)
        or content[0].get("type") != "text"
        or not isinstance(content[0].get("text"), str)
    ):
        raise PublicationGateError(f"{label} must contain exactly one text result")
    text = content[0]["text"]
    parsed = strict_json(text, f"{label} result")
    if isinstance(parsed, Mapping) and parsed.get("status") == "error":
        raise PublicationGateError(f"{label} returned an error payload")
    return text


def _protocol_sequence(calls: Sequence[Mapping[str, Any]]) -> str:
    """Describe protocol shape without exposing arguments or answer bytes."""

    values: list[str] = []
    for item in calls:
        tool = item.get("tool")
        label = "prepare" if tool == PREPARE_TOOL else "confirm"
        status = item.get("status") if isinstance(item.get("status"), str) else "missing-status"
        outcome = "error" if item.get("error") not in (None, "") else "no-error"
        values.append(f"{label}:{status}:{outcome}")
    return "[" + ",".join(values) + "]"


def _action_label(item: Mapping[str, Any]) -> str:
    item_type = item.get("type")
    if item_type == "mcp_tool_call":
        server = item.get("server")
        tool = item.get("tool")
        return f"mcp_tool_call:{server}:{tool}"
    return str(item_type or "unknown")


def _completed_protocol_calls(stdout: bytes) -> list[Mapping[str, Any]]:
    markers = [name.encode("utf-8") for name in PROTOCOL_TOOLS]
    if not any(marker in stdout for marker in markers):
        return []
    try:
        decoded = stdout.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise PublicationGateError("Codex JSONL containing the answer protocol is not UTF-8") from exc
    calls: list[Mapping[str, Any]] = []
    actions: list[Mapping[str, Any]] = []
    for number, line in enumerate(decoded.splitlines(), 1):
        if not line.strip():
            continue
        event = strict_json(line, f"Codex JSONL line {number}")
        if not isinstance(event, Mapping) or event.get("type") != "item.completed":
            continue
        item = event.get("item")
        if item is None and isinstance(event.get("data"), Mapping):
            item = event["data"].get("item")
        if not isinstance(item, Mapping):
            continue
        item_type = item.get("type")
        if isinstance(item_type, str) and item_type not in {"agent_message", "reasoning"}:
            actions.append(item)
        if (
            item_type == "mcp_tool_call"
            and item.get("server") == SERVER
            and item.get("tool") in PROTOCOL_TOOLS
        ):
            calls.append(item)
    if not calls:
        raise PublicationGateError(
            "Codex output mentions the Semantic OKF answer protocol but has no completed protocol event"
        )
    if not actions or actions[-1] is not calls[-1]:
        raise PublicationGateError(
            "the successful answer confirmation must be the terminal tool call; "
            f"protocol={_protocol_sequence(calls)}; "
            f"terminal={_action_label(actions[-1]) if actions else 'none'}"
        )
    return calls


def confirmed_candidate(stdout: bytes) -> bytes | None:
    """Return exact confirmed bytes, or None when the trace contains no answer protocol."""

    calls = _completed_protocol_calls(stdout)
    if not calls:
        return None
    tools = [item.get("tool") for item in calls]
    if len(tools) < 2 or tools[-1] != CONFIRM_TOOL:
        raise PublicationGateError(
            "answer protocol must end in one successful terminal confirm; "
            f"observed={_protocol_sequence(calls)}"
        )
    prepared: tuple[bytes, str] | None = None
    successful_confirms = 0
    for number, item in enumerate(calls, 1):
        arguments = item.get("arguments")
        if not isinstance(arguments, Mapping):
            raise PublicationGateError(f"answer protocol call {number} has no argument object")
        tool = item["tool"]
        status = item.get("status")
        error = item.get("error")
        if status != "completed" or error not in (None, ""):
            if status != "failed":
                raise PublicationGateError(
                    f"answer protocol call {number} is not a recoverable failed protocol call"
                )
            # A failed protocol call publishes nothing. Discard that transaction;
            # only a new successful preparation may start a recoverable retry.
            prepared = None
            continue
        text = _result_text(item, f"answer protocol call {number}")
        if tool == PREPARE_TOOL:
            required = {"question_id", "query", "draft"}
            optional = {
                "summary_min_words",
                "summary_max_words",
                "top_k",
                "per_facet",
                "maximum_facets",
                "page_size",
            }
            actual = set(arguments)
            if not required <= actual or actual - required - optional:
                raise PublicationGateError(
                    "prepare arguments use a closed schema; "
                    f"missing={sorted(required - actual)}, "
                    f"unknown={sorted(actual - required - optional)}"
                )
            prepared = _prepared_candidate(text, number)
            continue

        if prepared is None:
            raise PublicationGateError("answer confirm has no successful preparation")
        successful_confirms += 1
        if successful_confirms != 1 or number != len(calls):
            raise PublicationGateError(
                "only the final protocol call may be a successful answer confirmation"
            )
        confirm = _exact_keys(
            arguments,
            {"response_sha256"},
            "answer confirm arguments",
        )
        confirmed_digest = _sha256(
            confirm["response_sha256"], "answer confirm response_sha256"
        )
        payload, prepared_digest = prepared
        if confirmed_digest != prepared_digest:
            raise PublicationGateError(
                "confirmed digest differs from the last prepare result"
            )
        receipt = _exact_keys(
            strict_json(text, "finalizer confirmation receipt"),
            {"schema", "status", "response_sha256", "byte_count"},
            "finalizer confirmation receipt",
        )
        if _canonical_json(receipt) != text:
            raise PublicationGateError("confirmation receipt is not canonical JSON")
        byte_count = receipt["byte_count"]
        if (
            receipt["schema"] != CONFIRMATION_SCHEMA
            or receipt["status"] != "confirmed"
            or receipt["response_sha256"] != prepared_digest
            or isinstance(byte_count, bool)
            or not isinstance(byte_count, int)
            or byte_count != len(payload)
        ):
            raise PublicationGateError("confirmation receipt does not bind the prepared bytes")
        return payload
    raise PublicationGateError(
        "answer protocol trace ended without successful confirmation; "
        f"observed={_protocol_sequence(calls)}"
    )


def output_path(arguments: Sequence[str]) -> Path | None:
    """Resolve the single Codex --output-last-message target, if supplied."""

    found: list[str] = []
    for index, value in enumerate(arguments):
        if value == "--output-last-message":
            if index + 1 >= len(arguments):
                raise PublicationGateError("--output-last-message has no value")
            found.append(arguments[index + 1])
        elif value.startswith("--output-last-message="):
            found.append(value.split("=", 1)[1])
    if not found:
        return None
    if len(found) != 1 or not found[0]:
        raise PublicationGateError("Codex arguments must contain one output-last-message target")
    path = Path(found[0])
    if not path.is_absolute():
        raise PublicationGateError("output-last-message target must be absolute")
    return path


def atomic_publish(path: Path, payload: bytes) -> None:
    """Replace a regular output file atomically with exact confirmed bytes."""

    parent = path.parent.resolve(strict=True)
    if not parent.is_dir() or parent.is_symlink():
        raise PublicationGateError("output-last-message parent must be a regular directory")
    if path.exists() and (not path.is_file() or path.is_symlink()):
        raise PublicationGateError("output-last-message target must be a regular non-link file")
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb",
            dir=parent,
            prefix=f".{path.name}.",
            suffix=".confirmed.tmp",
            delete=False,
        ) as stream:
            temporary = Path(stream.name)
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        temporary = None
        if path.read_bytes() != payload:
            raise PublicationGateError("published bytes differ after atomic replacement")
    except OSError as exc:
        raise PublicationGateError(f"cannot publish confirmed output atomically: {exc}") from exc
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def _real_codex(environ: Mapping[str, str]) -> str:
    override = environ.get(REAL_CODEX_ENV)
    # The Windows Store desktop binary can be discoverable through PATH while
    # still denying child-process execution. Prefer the npm command shim on
    # Windows; it resolves the same Codex CLI and is directly executable by
    # subprocess. Unix installations normally fall through to ``codex``.
    candidate = (
        override
        or shutil.which("codex.cmd")
        or shutil.which("codex.exe")
        or shutil.which("codex")
    )
    if not candidate:
        raise PublicationGateError("cannot resolve the real Codex executable")
    path = Path(candidate).resolve(strict=True)
    if not path.is_file() or path.is_symlink():
        raise PublicationGateError("real Codex executable must be a regular non-link file")
    return str(path)


def _allowed_skills(environ: Mapping[str, str]) -> tuple[str, ...]:
    """Parse the exact Skill Arena profile boundary and reject ambiguous values."""

    if ALLOWED_SKILLS_ENV not in environ:
        raise PublicationGateError(f"{ALLOWED_SKILLS_ENV} is required")
    value = environ[ALLOWED_SKILLS_ENV]
    if not isinstance(value, str):
        raise PublicationGateError(f"{ALLOWED_SKILLS_ENV} must be a string")
    if not value:
        return ()
    items = tuple(value.split(","))
    if (
        any(not item or SKILL_ID_PATTERN.fullmatch(item) is None for item in items)
        or len(items) != len(set(items))
    ):
        raise PublicationGateError(f"{ALLOWED_SKILLS_ENV} is malformed")
    if ENSEMBLE_SKILL in items and items != (ENSEMBLE_SKILL,):
        raise PublicationGateError(
            f"{ENSEMBLE_SKILL} must be the only allowed skill in its treatment profile"
        )
    return items


def _treatment_command(
    executable: str,
    arguments: Sequence[str],
    environ: Mapping[str, str],
) -> tuple[list[str], bytes]:
    """Build the Codex command and a persistible treatment isolation receipt."""

    allowed = _allowed_skills(environ)
    if allowed != (ENSEMBLE_SKILL,):
        return [executable, *arguments], b""
    if any("shell_tool" in argument for argument in arguments):
        raise PublicationGateError(
            "Codex arguments must not override the treatment shell-tool restriction"
        )
    command = [executable, "--disable", "shell_tool", *arguments]
    receipt = _canonical_json(
        {
            "schema": SHELL_ISOLATION_SCHEMA,
            "skill_id": ENSEMBLE_SKILL,
            "shell_tool_disabled": True,
        }
    ).encode("utf-8") + b"\n"
    return command, receipt


def run(
    arguments: Sequence[str],
    *,
    stdin: bytes,
    environ: Mapping[str, str],
    runner: Any = subprocess.run,
) -> tuple[int, bytes, bytes]:
    """Run Codex and apply the publication gate after a successful process exit."""

    executable = _real_codex(environ)
    command, isolation_receipt = _treatment_command(executable, arguments, environ)
    completed = runner(
        command,
        input=stdin,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=dict(environ),
        check=False,
    )
    stdout = bytes(completed.stdout or b"")
    stderr = isolation_receipt + bytes(completed.stderr or b"")
    code = int(completed.returncode)
    if code != 0:
        return code, stdout, stderr
    candidate = confirmed_candidate(stdout)
    if candidate is not None:
        target = output_path(arguments)
        if target is None:
            raise PublicationGateError(
                "confirmed Semantic OKF output requires --output-last-message"
            )
        atomic_publish(target, candidate)
    return 0, stdout, stderr


def main(argv: Sequence[str] | None = None) -> int:
    arguments = list(sys.argv[1:] if argv is None else argv)
    stdin = sys.stdin.buffer.read()
    try:
        code, stdout, stderr = run(
            arguments,
            stdin=stdin,
            environ=os.environ,
        )
    except (OSError, PublicationGateError) as exc:
        print(f"Semantic OKF publication gate failed: {exc}", file=sys.stderr, flush=True)
        return PROTOCOL_EXIT
    sys.stdout.buffer.write(stdout)
    sys.stdout.buffer.flush()
    sys.stderr.buffer.write(stderr)
    sys.stderr.buffer.flush()
    return code


if __name__ == "__main__":
    raise SystemExit(main())
