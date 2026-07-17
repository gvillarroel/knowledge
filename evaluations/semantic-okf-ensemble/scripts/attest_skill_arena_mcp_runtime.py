#!/usr/bin/env python3
"""Attest the exact MCP execution path of the accepted 90-answer Skill Arena run."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Mapping, Sequence

from _answer_output import DEFAULT_CONTRACT, load_contract
from _evaluation import REPO_ROOT, sha256, write_new


EVALUATION_ROOT = REPO_ROOT / "evaluations/semantic-okf-ensemble"
SKILL_ARENA_CONFIG = EVALUATION_ROOT / "skill-arena/ensemble-hard10.yaml"
SKILL_ARENA_MANIFEST = EVALUATION_ROOT / "skill-arena/config-manifest.json"
ANSWER_OUTPUT_REPORT = EVALUATION_ROOT / "answer-output-comparison-final.json"
FINAL_JSON = EVALUATION_ROOT / "skill-arena-mcp-runtime-attestation-final.json"
FINAL_MARKDOWN = EVALUATION_ROOT / "skill-arena-mcp-runtime-attestation-final.md"
PUBLICATION_RUNTIME = (
    REPO_ROOT / "skills/consult-semantic-okf-ensemble/publication-runtime"
)
PUBLICATION_GATE_SCRIPT = PUBLICATION_RUNTIME / "confirmed_output_gate.py"
PUBLICATION_GATE_LAUNCHER = PUBLICATION_RUNTIME / "run_codex.cmd"
TREATMENT_SKILL = REPO_ROOT / "skills/consult-semantic-okf-ensemble/SKILL.md"

SCHEMA = "semantic-okf-ensemble-skill-arena-mcp-runtime-attestation/1.7"
TRACE_SCHEMA_VERSION = 1
TRACE_ADAPTER = "codex"
TRACE_BACKEND = "command"
MCP_SERVER_VERSION = "1.5.0"
CONFIG_MANIFEST_SCHEMA = "semantic-okf-hard-answer-configs/2.2"
PUBLICATION_TRACE_COMMAND = "publication-runtime/run_codex.cmd"
TREATMENT = "ensemble-consult-treatment"
SEMANTIC_SERVER = "semantic_okf"
BOOTSTRAP = "semantic_okf_bootstrap_skill"
INSPECT = "semantic_okf_inspect"
COVERAGE = "semantic_okf_coverage_brief"
PREPARE = "semantic_okf_prepare_answer"
CONFIRM = "semantic_okf_confirm_answer"
PRIORITY_ORDER = "persisted-idf-facet-consensus-priority-v1"
BOOTSTRAP_SCHEMA = "semantic-okf-skill-bootstrap/1.0"
BOOTSTRAP_SKILL_ID = "consult-semantic-okf-ensemble"
SHELL_ISOLATION_SCHEMA = "semantic-okf-shell-isolation-receipt/1.0"
PREPARED_ANSWER_SCHEMA = "semantic-okf-prepared-answer/1.0"
CONFIRMATION_SCHEMA = "semantic-okf-answer-confirmation-receipt/1.0"
BOOTSTRAP_RESPONSE_KEYS = [
    "schema",
    "skill_id",
    "skill_sha256",
    "byte_count",
    "skill_markdown",
]
SHELL_ISOLATION_KEYS = [
    "schema",
    "skill_id",
    "shell_tool_disabled",
]
PREPARED_ENVELOPE_KEYS = [
    "schema",
    "candidate_json",
    "response_sha256",
    "byte_count",
]
CONFIRMATION_RECEIPT_KEYS = [
    "schema",
    "status",
    "response_sha256",
    "byte_count",
]
EXPECTED_SEMANTIC_TOOLS = {BOOTSTRAP, INSPECT, COVERAGE, PREPARE, CONFIRM}
SEMANTIC_TOOL_SEQUENCE = [BOOTSTRAP, INSPECT, COVERAGE, PREPARE, CONFIRM]
SHELL_DISABLE_ARGUMENTS = ["--disable", "shell_tool"]
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
ABSOLUTE_WINDOWS = re.compile(r"^[A-Za-z]:[\\/]")
TRACE_KEYS = {
    "schemaVersion",
    "generatedAt",
    "adapter",
    "providerId",
    "backend",
    "command",
    "args",
    "exitCode",
    "stdout",
    "stderr",
    "eventCount",
    "toolEventCount",
    "events",
    "toolEvents",
    "extra",
}
ROW_KEYS = {
    "profile_id",
    "question_id",
    "repetition",
    "trace_sha256",
    "trace_archived",
    "raw_output_sha256",
    "raw_output_byte_count",
    "output_sha256",
    "output_byte_count",
    "publication_corrected",
    "bootstrap",
    "shell_isolation",
    "tool_counts",
    "ordered_tool_names",
    "coverage_pages",
    "coverage_total_pages",
    "coverage_priority_order",
    "coverage_priority_order_sha256",
    "protocol_call_outcomes",
    "recovered_protocol_failure_count",
    "confirmation_sha256",
    "confirmation_byte_count",
}
BOOTSTRAP_REPORT_KEYS = {
    "schema",
    "skill_id",
    "skill_sha256",
    "byte_count",
}
SHELL_ISOLATION_REPORT_KEYS = {
    "schema",
    "skill_id",
    "shell_tool_disabled",
    "receipt_sha256",
    "byte_count",
}
TOOL_COUNT_KEYS = {
    "recorded_events",
    "completed_calls",
    "superseded_control_command_starts",
    "mcp_calls",
    "semantic_okf_calls",
    "shell_or_command_calls",
    "failed_mcp_calls",
}
GATE_KEYS = {
    "config_manifest_runtime_contract_bound",
    "exact_cell_coverage",
    "strict_trace_json",
    "trace_runtime_contract",
    "publication_runtime_bound",
    "publication_wrapper_command_bound",
    "outputs_nonempty",
    "controls_output_matches_raw_agent_message",
    "controls_have_no_semantic_okf_calls",
    "controls_have_no_shell_isolation_receipt",
    "controls_have_only_exact_retry_superseded_command_starts",
    "treatment_has_complete_coverage",
    "treatment_binds_coverage_priority_order",
    "treatment_bootstraps_exact_frozen_skill",
    "treatment_bootstrap_is_first_and_one_shot",
    "treatment_uses_split_prepare_confirm",
    "treatment_confirm_is_terminal",
    "treatment_has_no_shell_or_command_calls",
    "treatment_shell_disable_receipt_bound",
    "treatment_has_only_recoverable_protocol_failures",
    "treatment_final_transaction_is_clean",
    "treatment_output_confirmation_matches",
    "answer_output_report_bound",
}


class AttestationError(ValueError):
    """Describe a fail-closed execution-trace attestation violation."""


@dataclass(frozen=True)
class ToolCall:
    """One paired tool call, reduced to the fields needed for attestation."""

    index: int
    item_type: str
    server: str | None
    name: str
    arguments: Mapping[str, Any] | None
    completed: Mapping[str, Any]
    failed_mcp: bool

    @property
    def is_mcp(self) -> bool:
        return self.item_type == "mcp_tool_call"

    @property
    def is_semantic_okf(self) -> bool:
        return self.is_mcp and (
            self.server == SEMANTIC_SERVER or self.name.startswith("semantic_okf_")
        )

    @property
    def is_shell_or_command(self) -> bool:
        lowered_type = self.item_type.lower()
        lowered_name = self.name.lower()
        return (
            "command" in lowered_type
            or "shell" in lowered_type
            or lowered_name in {"shell_command", "exec_command", "command_execution"}
        )


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise AttestationError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _reject_constant(value: str) -> Any:
    raise AttestationError(f"non-finite JSON constant is forbidden: {value}")


def strict_json_text(text: str, label: str) -> Any:
    """Parse one JSON value while rejecting duplicate keys and non-finite values."""

    try:
        return json.loads(
            text,
            object_pairs_hook=_strict_object,
            parse_constant=_reject_constant,
        )
    except (json.JSONDecodeError, AttestationError) as exc:
        raise AttestationError(f"{label} is not strict JSON: {exc}") from exc


def strict_json_file(path: Path, label: str) -> dict[str, Any]:
    """Load one UTF-8 JSON object with the strict parser."""

    try:
        text = path.read_bytes().decode("utf-8")
    except (OSError, UnicodeError) as exc:
        raise AttestationError(f"cannot read {label}: {exc}") from exc
    value = strict_json_text(text, label)
    if not isinstance(value, dict):
        raise AttestationError(f"{label} must be a JSON object")
    return value


def exact_keys(value: Any, expected: set[str], label: str) -> dict[str, Any]:
    """Require a closed JSON object."""

    if not isinstance(value, dict):
        raise AttestationError(f"{label} must be an object")
    actual = set(value)
    if actual != expected:
        raise AttestationError(
            f"{label} uses a closed schema; missing={sorted(expected - actual)}, "
            f"unknown={sorted(actual - expected)}"
        )
    return value


def _hash_bytes(value: str) -> tuple[str, int]:
    payload = value.encode("utf-8")
    return hashlib.sha256(payload).hexdigest(), len(payload)


def _skill_material(path: Path, label: str) -> tuple[str, dict[str, Any]]:
    """Read the frozen treatment skill as exact strict UTF-8 bytes."""

    try:
        payload = path.read_bytes()
        markdown = payload.decode("utf-8", errors="strict")
    except (OSError, UnicodeError) as exc:
        raise AttestationError(f"cannot read {label}: {exc}") from exc
    if not payload or markdown.encode("utf-8") != payload:
        raise AttestationError(f"{label} must be nonempty exact UTF-8")
    return markdown, {
        "schema": BOOTSTRAP_SCHEMA,
        "skill_id": BOOTSTRAP_SKILL_ID,
        "skill_sha256": hashlib.sha256(payload).hexdigest(),
        "byte_count": len(payload),
    }


def _expected_shell_isolation() -> tuple[str, dict[str, Any]]:
    receipt = {
        "schema": SHELL_ISOLATION_SCHEMA,
        "skill_id": BOOTSTRAP_SKILL_ID,
        "shell_tool_disabled": True,
    }
    text = json.dumps(
        receipt,
        ensure_ascii=False,
        separators=(",", ":"),
        allow_nan=False,
    ) + "\n"
    encoded = text.encode("utf-8")
    return text, {
        **receipt,
        "receipt_sha256": hashlib.sha256(encoded).hexdigest(),
        "byte_count": len(encoded),
    }


def _expected_manifest_runtime_contract(
    bootstrap: Mapping[str, Any],
) -> dict[str, Any]:
    """Return the exact manifest fields that authorize this treatment runtime."""

    return {
        "schema_version": CONFIG_MANIFEST_SCHEMA,
        "mcp_runtime": {
            "server_version": MCP_SERVER_VERSION,
            "allowed_skill_id": BOOTSTRAP_SKILL_ID,
            "controls_expose_tools": False,
            "bootstrap_tool": BOOTSTRAP,
            "bootstrap_schema": BOOTSTRAP_SCHEMA,
            "bootstrap_key_order": BOOTSTRAP_RESPONSE_KEYS,
            "bootstrap_skill_id": BOOTSTRAP_SKILL_ID,
            "bootstrap_skill_sha256": bootstrap["skill_sha256"],
            "bootstrap_skill_byte_count": bootstrap["byte_count"],
            "bootstrap_exactly_once": True,
            "bootstrap_first": True,
            "bootstrap_failure_poison": True,
            "tools": SEMANTIC_TOOL_SEQUENCE,
        },
        "publication_runtime": {
            "treatment_skill_id": BOOTSTRAP_SKILL_ID,
            "treatment_shell_tool_disabled": True,
            "shell_disable_arguments": SHELL_DISABLE_ARGUMENTS,
            "shell_isolation_receipt_schema": SHELL_ISOLATION_SCHEMA,
            "shell_isolation_receipt_key_order": SHELL_ISOLATION_KEYS,
            "controls_shell_policy_unchanged": True,
        },
        "consult_skill": {
            "skill_id": BOOTSTRAP_SKILL_ID,
            "path": "skills/consult-semantic-okf-ensemble",
            "skill_md_sha256": bootstrap["skill_sha256"],
        },
    }


def _require_manifest_fields(
    value: Any, expected: Mapping[str, Any], label: str
) -> None:
    """Require type-exact values for a frozen subset of a larger closed manifest."""

    if not isinstance(value, Mapping):
        raise AttestationError(f"{label} must be an object")
    for key, wanted in expected.items():
        if key not in value:
            raise AttestationError(f"{label} is missing frozen field {key}")
        actual = value[key]
        if type(actual) is not type(wanted) or actual != wanted:
            raise AttestationError(f"{label}.{key} differs from the frozen runtime contract")


def _validate_manifest_runtime_contract(
    manifest: Mapping[str, Any], bootstrap: Mapping[str, Any]
) -> dict[str, Any]:
    """Cross-bind manifest 2.2 to the skill bytes and treatment isolation policy."""

    expected = _expected_manifest_runtime_contract(bootstrap)
    if manifest.get("schema_version") != CONFIG_MANIFEST_SCHEMA:
        raise AttestationError("Skill Arena manifest schema differs from 2.2")
    _require_manifest_fields(
        manifest.get("mcp_runtime"),
        expected["mcp_runtime"],
        "Skill Arena manifest mcp_runtime",
    )
    _require_manifest_fields(
        manifest.get("publication_runtime"),
        expected["publication_runtime"],
        "Skill Arena manifest publication_runtime",
    )
    consult_skills = manifest.get("consult_skills")
    if not isinstance(consult_skills, list):
        raise AttestationError("Skill Arena manifest consult_skills must be an array")
    matches = [
        item
        for item in consult_skills
        if isinstance(item, Mapping)
        and item.get("skill_id") == BOOTSTRAP_SKILL_ID
    ]
    if len(matches) != 1:
        raise AttestationError(
            "Skill Arena manifest must bind exactly one treatment consult skill"
        )
    _require_manifest_fields(
        matches[0], expected["consult_skill"], "Skill Arena manifest treatment skill"
    )
    return expected


def _publication_command_identity(value: Any, label: str) -> str:
    """Require the bound publication wrapper, allowing only an absolute workspace prefix."""

    if not isinstance(value, str) or not value:
        raise AttestationError(f"{label} trace command is invalid")
    normalized = value.replace("\\", "/")
    if normalized == PUBLICATION_TRACE_COMMAND:
        return PUBLICATION_TRACE_COMMAND
    absolute = normalized.startswith("/") or ABSOLUTE_WINDOWS.match(value) is not None
    if not absolute or not normalized.endswith(f"/{PUBLICATION_TRACE_COMMAND}"):
        raise AttestationError(
            f"{label} trace command is not the bound publication wrapper"
        )
    return PUBLICATION_TRACE_COMMAND


def _safe_relative(path: Path, root: Path, label: str) -> str:
    resolved = path.resolve(strict=True)
    try:
        relative = resolved.relative_to(root.resolve(strict=True))
    except ValueError as exc:
        raise AttestationError(f"{label} must remain inside the repository") from exc
    if not resolved.is_file() or resolved.is_symlink():
        raise AttestationError(f"{label} must be a regular non-link file")
    return relative.as_posix()


def _binding(path: Path, root: Path, label: str) -> dict[str, str]:
    return {"path": _safe_relative(path, root, label), "sha256": sha256(path)}


def _valid_hash(value: Any) -> bool:
    return isinstance(value, str) and SHA256_RE.fullmatch(value) is not None


def _validate_binding_shape(value: Any, label: str) -> dict[str, str]:
    binding = exact_keys(value, {"path", "sha256"}, label)
    path = binding["path"]
    digest = binding["sha256"]
    if not isinstance(path, str) or not path or not _valid_hash(digest):
        raise AttestationError(f"{label} path or SHA-256 is invalid")
    logical = PurePosixPath(path.replace("\\", "/"))
    if logical.is_absolute() or any(part in {"", ".", ".."} for part in logical.parts):
        raise AttestationError(f"{label} path must be repository-relative")
    return {"path": path, "sha256": digest}


def _expected_benchmark(contract: Mapping[str, Any]) -> dict[str, Any]:
    benchmark = contract.get("benchmark")
    if not isinstance(benchmark, Mapping):
        raise AttestationError("answer contract has no benchmark object")
    profiles = benchmark.get("profiles")
    questions = benchmark.get("question_ids")
    repetitions = benchmark.get("repetitions_per_cell")
    total = benchmark.get("total_answers")
    if (
        not isinstance(profiles, list)
        or profiles != [
            "knowledge-only-control",
            "adaptive-consult-control",
            TREATMENT,
        ]
        or not isinstance(questions, list)
        or len(questions) != 10
        or len(set(questions)) != 10
        or not all(isinstance(item, str) and item for item in questions)
        or repetitions != 3
        or total != 90
    ):
        raise AttestationError("answer contract benchmark differs from the exact 90-row design")
    if benchmark.get("variant_id") != "codex-luna-tools":
        raise AttestationError("answer contract variant differs")
    if not isinstance(benchmark.get("id"), str) or not benchmark["id"]:
        raise AttestationError("answer contract benchmark ID is invalid")
    return {
        "id": benchmark["id"],
        "profiles": profiles,
        "variant_id": benchmark["variant_id"],
        "question_ids": questions,
        "repetitions_per_cell": repetitions,
        "answer_count": total,
    }


def _expected_trace_contract(
    benchmark: Mapping[str, Any],
    bootstrap: Mapping[str, Any],
    manifest_runtime_contract: Mapping[str, Any],
) -> dict[str, Any]:
    """Return the closed split-tool execution contract attested for each treatment."""

    return {
        "schema_version": TRACE_SCHEMA_VERSION,
        "adapter": TRACE_ADAPTER,
        "backend": TRACE_BACKEND,
        "exit_code": 0,
        "publication_command": PUBLICATION_TRACE_COMMAND,
        "mcp_server_version": MCP_SERVER_VERSION,
        "config_manifest_runtime_contract": dict(manifest_runtime_contract),
        "treatment_profile": TREATMENT,
        "control_profiles": [
            profile for profile in benchmark["profiles"] if profile != TREATMENT
        ],
        "control_superseded_command_start_contract": (
            "an unpaired item.started event is classified only as a control-runtime "
            "diagnostic when its item is command_execution with status in_progress and a "
            "nonempty command, it precedes the final agent response, and a distinct later "
            "fully paired command_execution repeats the exact command and completes with "
            "status completed and exit_code 0 before that response; missing starts, MCP or "
            "treatment orphans, and unmatched, changed, failed, declined, or post-response "
            "starts reject the trace"
        ),
        "required_mcp_sequence": [BOOTSTRAP, INSPECT, COVERAGE, PREPARE, CONFIRM],
        "bootstrap_call_contract": (
            "exactly one successful first treatment tool call with empty arguments; its "
            "canonical response contains the exact frozen UTF-8 skill bytes, digest, and "
            "byte count; any bootstrap failure or replay rejects the trace"
        ),
        "bootstrap_response": dict(bootstrap),
        "coverage_call_contract": "complete ascending pages for one exact parameter session",
        "prepare_call_contract": (
            "one or more successful calls without mode in the clean final transaction; each "
            "returns one canonical semantic-okf-prepared-answer/1.0 envelope whose ordered "
            "fields and digest bind the exact UTF-8 candidate bytes; a failed prepare clears "
            "the transaction and publishes nothing"
        ),
        "confirm_call_contract": (
            "exactly one successful terminal call with only response_sha256, matching the "
            "last successful prepared envelope; its canonical receipt and published output "
            "bind the same digest and byte count; failed confirmation clears the transaction "
            "and publishes nothing"
        ),
        "recovery_contract": (
            "a failed prepare or confirmation publishes nothing and is recoverable only "
            "before a fresh successful "
            "prepare and the clean successful prepare-confirm suffix"
        ),
        "coverage_priority_order": PRIORITY_ORDER,
        "coverage_priority_order_sha256_recomputed": True,
        "treatment_shell_policy_attestation": (
            "one exact canonical treatment-only shell-disable receipt in the execution "
            "trace and the same bytes minus the transport-stripped terminal LF in response "
            "metadata, plus zero observed shell or command events; controls contain neither "
            "the receipt nor Semantic OKF calls"
        ),
        "shell_isolation_receipt": _expected_shell_isolation()[1],
    }


def _answer_report_bindings(
    answer_report: Mapping[str, Any],
    benchmark: Mapping[str, Any],
    promptfoo: Mapping[str, str],
    config: Mapping[str, str],
    manifest: Mapping[str, str],
) -> None:
    if answer_report.get("status") != "pass" or answer_report.get("answer_count") != 90:
        raise AttestationError("checked answer-output report is not a complete pass publication")
    if answer_report.get("benchmark") != dict(benchmark):
        raise AttestationError("checked answer-output benchmark differs from the trace benchmark")
    inputs = answer_report.get("inputs")
    skill_arena = answer_report.get("skill_arena")
    if not isinstance(inputs, Mapping) or not isinstance(skill_arena, Mapping):
        raise AttestationError("checked answer-output report lacks input or Skill Arena bindings")
    raw = inputs.get("promptfoo")
    if not isinstance(raw, Mapping):
        raise AttestationError("checked answer-output report lacks its Promptfoo binding")
    if raw.get("path") != promptfoo["path"] or raw.get("sha256") != promptfoo["sha256"]:
        raise AttestationError("trace input differs from the checked answer-output Promptfoo input")
    if skill_arena.get("config") != dict(config):
        raise AttestationError("checked answer-output Skill Arena config binding differs")
    if skill_arena.get("config_manifest") != dict(manifest):
        raise AttestationError("checked answer-output Skill Arena manifest binding differs")


def _cell_identity(
    row: Mapping[str, Any], benchmark: Mapping[str, Any]
) -> tuple[str, str, str]:
    provider = row.get("provider")
    metadata = row.get("metadata")
    variables = row.get("vars")
    response = row.get("response")
    if not all(isinstance(value, Mapping) for value in (provider, metadata, variables, response)):
        raise AttestationError("Promptfoo row lacks provider, metadata, vars, or response objects")
    profile = metadata.get("profileId")
    question = metadata.get("promptId")
    variant = metadata.get("variantId")
    if metadata.get("benchmarkId") != benchmark["id"]:
        raise AttestationError("Promptfoo row benchmark differs")
    if profile not in benchmark["profiles"] or question not in benchmark["question_ids"]:
        raise AttestationError("Promptfoo row profile or question differs")
    if variant != benchmark["variant_id"]:
        raise AttestationError("Promptfoo row variant differs")
    if provider.get("id") != profile or variables.get("variantId") != variant:
        raise AttestationError("Promptfoo provider or variable identity differs")
    if metadata.get("scenarioId") != f"{variant}-{profile}":
        raise AttestationError("Promptfoo scenario identity differs")
    if metadata.get("rowId") != f"{variant}:{question}":
        raise AttestationError("Promptfoo row identity differs")
    response_metadata = response.get("metadata")
    if not isinstance(response_metadata, Mapping):
        raise AttestationError("Promptfoo response lacks execution metadata")
    for key, expected in {
        "profileId": profile,
        "variantId": variant,
        "scenarioId": f"{variant}-{profile}",
    }.items():
        if response_metadata.get(key) != expected:
            raise AttestationError(f"Promptfoo response {key} differs")
    output = response.get("output")
    if not isinstance(output, str) or not output.strip():
        raise AttestationError("Promptfoo response output must be nonempty")
    return str(profile), str(question), str(variant)


def _is_link_or_junction(path: Path) -> bool:
    """Return whether one path entry redirects filesystem traversal."""

    if path.is_symlink():
        return True
    is_junction = getattr(path, "is_junction", None)
    return bool(is_junction is not None and is_junction())


def _validated_archived_workspace_roots(
    supplied: Mapping[str, Path | str] | None,
    profiles: Sequence[str],
    repository_root: Path,
) -> dict[str, Path]:
    """Validate the optional exact per-profile archive-root assignment."""

    if supplied is None:
        return {}
    if not isinstance(supplied, dict) or not all(
        isinstance(key, str) and key for key in supplied
    ):
        raise AttestationError("archived workspace roots must be a profile-to-path object")
    expected = set(profiles)
    actual = set(supplied)
    if actual != expected:
        raise AttestationError(
            "archived workspace roots must cover the exact benchmark profiles; "
            f"missing={sorted(expected - actual)}, unknown={sorted(actual - expected)}"
        )

    root = repository_root.resolve(strict=True)
    validated: dict[str, Path] = {}
    seen: set[Path] = set()
    for profile in profiles:
        raw = supplied[profile]
        if not isinstance(raw, (str, Path)) or not str(raw):
            raise AttestationError(f"archived workspace root for {profile} is invalid")
        path = Path(raw)
        if any(part == ".." for part in path.parts):
            raise AttestationError(
                f"archived workspace root for {profile} contains traversal"
            )
        if path.anchor and not path.is_absolute():
            raise AttestationError(
                f"archived workspace root for {profile} is drive-relative"
            )
        lexical = path if path.is_absolute() else root / path
        try:
            relative = lexical.relative_to(root)
        except ValueError as exc:
            raise AttestationError(
                f"archived workspace root for {profile} must remain inside the repository"
            ) from exc
        if not relative.parts:
            raise AttestationError(
                f"archived workspace root for {profile} must be narrower than the repository"
            )
        cursor = root
        for part in relative.parts:
            cursor /= part
            if _is_link_or_junction(cursor):
                raise AttestationError(
                    f"archived workspace root for {profile} contains a link or junction"
                )
        try:
            resolved = lexical.resolve(strict=True)
        except OSError as exc:
            raise AttestationError(
                f"cannot resolve archived workspace root for {profile}: {exc}"
            ) from exc
        try:
            resolved.relative_to(root)
        except ValueError as exc:
            raise AttestationError(
                f"archived workspace root for {profile} must remain inside the repository"
            ) from exc
        if not resolved.is_dir() or _is_link_or_junction(lexical):
            raise AttestationError(
                f"archived workspace root for {profile} must be a non-link directory"
            )
        if resolved in seen:
            raise AttestationError("archived workspace roots must be distinct per profile")
        seen.add(resolved)
        validated[profile] = resolved
    return validated


def _archived_trace_path(root: Path, logical: PurePosixPath, label: str) -> Path:
    """Resolve one trace below its assigned archive root without following links."""

    candidate = root
    for index, part in enumerate(logical.parts):
        candidate /= part
        if _is_link_or_junction(candidate):
            raise AttestationError(f"{label} archived trace path contains a link or junction")
        if index < len(logical.parts) - 1 and not candidate.is_dir():
            raise AttestationError(f"{label} archived trace parent directory is missing")
    try:
        resolved = candidate.resolve(strict=True)
    except OSError as exc:
        raise AttestationError(f"cannot resolve {label} archived trace: {exc}") from exc
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise AttestationError(f"{label} archived trace escapes its profile root") from exc
    if not resolved.is_file() or _is_link_or_junction(candidate):
        raise AttestationError(f"{label} archived trace must be a regular non-link file")
    return resolved


def _trace_path(
    row: Mapping[str, Any],
    label: str,
    profile: str,
    archived_workspace_roots: Mapping[str, Path],
) -> tuple[Path, Mapping[str, Any], bool]:
    response = row["response"]
    metadata = response["metadata"]
    hook = metadata.get("executionEventHook")
    exact_keys(hook, {"path", "relativePath", "eventCount", "toolEventCount"}, f"{label} hook")
    value = hook["path"]
    if not isinstance(value, str) or not value:
        raise AttestationError(f"{label} hook path is invalid")
    relative_value = hook["relativePath"]
    if not isinstance(relative_value, str) or not relative_value:
        raise AttestationError(f"{label} hook relative path is invalid")
    logical = PurePosixPath(relative_value.replace("\\", "/"))
    if logical.is_absolute() or any(part in {"", ".", ".."} for part in logical.parts):
        raise AttestationError(f"{label} hook relative path is unsafe")
    path = Path(value)
    if not path.is_absolute():
        raise AttestationError(f"{label} hook path must be absolute in the raw runner output")
    normalized_hook = value.replace("\\", "/").rstrip("/")
    if not normalized_hook.endswith(f"/{logical.as_posix()}"):
        raise AttestationError(f"{label} hook absolute and relative paths disagree")
    if _is_link_or_junction(path):
        raise AttestationError(f"{label} trace must be a regular non-link file")
    try:
        resolved = path.resolve(strict=True)
    except FileNotFoundError as exc:
        archive_root = archived_workspace_roots.get(profile)
        if archive_root is None:
            raise AttestationError(
                f"{label} hook trace path no longer exists and no archived workspace root was supplied"
            ) from exc
        return _archived_trace_path(archive_root, logical, label), hook, True
    if not resolved.is_file() or resolved.is_symlink():
        raise AttestationError(f"{label} trace must be a regular non-link file")
    normalized = resolved.as_posix()
    if not normalized.endswith(logical.as_posix()):
        raise AttestationError(f"{label} hook absolute and relative paths disagree")
    return resolved, hook, False


def _trace_events(
    trace: Mapping[str, Any], hook: Mapping[str, Any], label: str
) -> tuple[list[Mapping[str, Any]], list[Mapping[str, Any]]]:
    exact_keys(trace, TRACE_KEYS, f"{label} trace")
    if (
        trace["schemaVersion"] != TRACE_SCHEMA_VERSION
        or trace["adapter"] != TRACE_ADAPTER
        or trace["backend"] != TRACE_BACKEND
        or trace["exitCode"] != 0
    ):
        raise AttestationError(f"{label} trace runtime contract differs")
    _publication_command_identity(trace["command"], label)
    if trace["providerId"] != "codex:command:gpt-5.6-luna":
        raise AttestationError(f"{label} trace provider identity differs")
    if (
        not isinstance(trace["generatedAt"], str)
        or not trace["generatedAt"]
        or not isinstance(trace["command"], str)
        or not trace["command"]
        or not isinstance(trace["args"], list)
        or not all(isinstance(item, str) for item in trace["args"])
        or not isinstance(trace["stdout"], str)
        or trace["stderr"] is not None
        and not isinstance(trace["stderr"], str)
        or not isinstance(trace["extra"], Mapping)
    ):
        raise AttestationError(f"{label} trace header schema differs")
    if not isinstance(trace["events"], list) or not isinstance(trace["toolEvents"], list):
        raise AttestationError(f"{label} trace event collections are invalid")
    events = trace["events"]
    tool_events = trace["toolEvents"]
    if (
        trace["eventCount"] != len(events)
        or trace["toolEventCount"] != len(tool_events)
        or hook["eventCount"] != len(events)
        or hook["toolEventCount"] != len(tool_events)
    ):
        raise AttestationError(f"{label} trace event counts differ")
    by_index: dict[int, Mapping[str, Any]] = {}
    for position, event in enumerate(events):
        exact_keys(event, {"index", "type", "data"}, f"{label} event {position}")
        if event["index"] != position or not isinstance(event["type"], str) or not isinstance(event["data"], Mapping):
            raise AttestationError(f"{label} event ordering or shape differs")
        if event["data"].get("type") != event["type"]:
            raise AttestationError(f"{label} event type disagrees with its payload")
        by_index[position] = event
    previous = -1
    for event in tool_events:
        if not isinstance(event, Mapping) or not isinstance(event.get("index"), int):
            raise AttestationError(f"{label} tool event shape differs")
        index = event["index"]
        if index <= previous or by_index.get(index) != event:
            raise AttestationError(f"{label} tool events are not an ordered exact event subset")
        if event.get("type") not in {"item.started", "item.completed"}:
            raise AttestationError(f"{label} tool event has an unexpected event type")
        item = event.get("data", {}).get("item")
        if not isinstance(item, Mapping) or not isinstance(item.get("id"), str) or not isinstance(item.get("type"), str):
            raise AttestationError(f"{label} tool event lacks a typed item identity")
        previous = index
    return events, tool_events


def _paired_calls(
    tool_events: Sequence[Mapping[str, Any]],
    label: str,
    profile: str,
    last_agent_message_index: int,
) -> tuple[list[ToolCall], int]:
    """Pair completed calls and narrowly classify superseded control command starts."""

    started: dict[str, tuple[int, Mapping[str, Any]]] = {}
    completed: dict[str, tuple[int, Mapping[str, Any]]] = {}
    for event in tool_events:
        item = event["data"]["item"]
        identity = item["id"]
        target = started if event["type"] == "item.started" else completed
        if identity in target:
            raise AttestationError(f"{label} duplicates tool event {identity!r}")
        target[identity] = (event["index"], item)
    missing_starts = set(completed) - set(started)
    if missing_starts:
        raise AttestationError(
            f"{label} contains a completed tool call without a matching start"
        )

    calls: list[ToolCall] = []
    for identity, (finish_index, finish) in sorted(completed.items(), key=lambda pair: pair[1][0]):
        start_index, start = started[identity]
        if start_index >= finish_index or start.get("type") != finish.get("type"):
            raise AttestationError(f"{label} tool call order or type differs")
        item_type = str(finish["type"])
        if item_type == "mcp_tool_call":
            for key in ("server", "tool", "arguments"):
                if start.get(key) != finish.get(key):
                    raise AttestationError(f"{label} MCP {key} changed during the call")
            server = finish.get("server")
            name = finish.get("tool")
            arguments = finish.get("arguments")
            if not isinstance(server, str) or not isinstance(name, str) or not isinstance(arguments, Mapping):
                raise AttestationError(f"{label} MCP call shape differs")
            failed = (
                finish.get("status") != "completed"
                or finish.get("error") is not None
                or not isinstance(finish.get("result"), Mapping)
                or finish.get("result", {}).get("isError") is True
            )
        else:
            server = None
            raw_name = finish.get("tool") or finish.get("name") or item_type
            name = str(raw_name)
            arguments = finish.get("arguments") if isinstance(finish.get("arguments"), Mapping) else None
            failed = False
        calls.append(
            ToolCall(
                index=finish_index,
                item_type=item_type,
                server=server,
                name=name,
                arguments=arguments,
                completed=finish,
                failed_mcp=failed,
            )
        )
    orphan_starts = [
        (identity, *started[identity])
        for identity in set(started) - set(completed)
    ]
    orphan_starts.sort(key=lambda value: value[1])
    if not orphan_starts:
        return calls, 0
    if profile == TREATMENT:
        raise AttestationError(
            f"{label} treatment trace contains an unpaired tool start"
        )

    paired_items = [
        (identity, started[identity], completed[identity])
        for identity in set(started) & set(completed)
    ]
    paired_items.sort(key=lambda value: value[2][0])
    used_retries: set[str] = set()
    for identity, orphan_index, orphan in orphan_starts:
        command = orphan.get("command")
        if (
            orphan.get("type") != "command_execution"
            or orphan.get("status") != "in_progress"
            or not isinstance(command, str)
            or not command.strip()
        ):
            raise AttestationError(
                f"{label} unpaired start {identity!r} is not a classifiable "
                "in-progress command_execution"
            )
        if orphan_index >= last_agent_message_index:
            raise AttestationError(
                f"{label} unpaired command start occurs after the final agent response"
            )
        retry_identity: str | None = None
        for candidate_identity, (start_index, retry_start), (
            finish_index,
            retry_finish,
        ) in paired_items:
            if candidate_identity in used_retries:
                continue
            exit_code = retry_finish.get("exit_code")
            if (
                start_index > orphan_index
                and finish_index < last_agent_message_index
                and retry_start.get("type") == "command_execution"
                and retry_finish.get("type") == "command_execution"
                and retry_start.get("status") == "in_progress"
                and retry_finish.get("status") == "completed"
                and not isinstance(exit_code, bool)
                and exit_code == 0
                and retry_start.get("command") == command
                and retry_finish.get("command") == command
            ):
                retry_identity = candidate_identity
                break
        if retry_identity is None:
            raise AttestationError(
                f"{label} unpaired command start {identity!r} has no exact later "
                "successful command retry before the final agent response"
            )
        used_retries.add(retry_identity)
    return calls, len(orphan_starts)


def _mcp_text(call: ToolCall, label: str) -> tuple[str, Any]:
    if not call.is_mcp or call.failed_mcp:
        raise AttestationError(f"{label} is not a successful completed MCP call")
    result = call.completed.get("result")
    if not isinstance(result, Mapping):
        raise AttestationError(f"{label} MCP result is absent")
    content = result.get("content")
    if (
        not isinstance(content, list)
        or len(content) != 1
        or not isinstance(content[0], Mapping)
        or content[0].get("type") != "text"
        or not isinstance(content[0].get("text"), str)
    ):
        raise AttestationError(f"{label} MCP result must contain exactly one text item")
    text = content[0]["text"]
    value = strict_json_text(text, f"{label} MCP text")
    if isinstance(value, Mapping) and value.get("status") == "error":
        raise AttestationError(f"{label} MCP payload reports an error")
    return text, value


def _last_visible_message(
    events: Sequence[Mapping[str, Any]], label: str
) -> tuple[str, int]:
    messages: list[tuple[str, int]] = []
    for event in events:
        if event.get("type") != "item.completed":
            continue
        item = event.get("data", {}).get("item")
        if isinstance(item, Mapping) and item.get("type") == "agent_message":
            text = item.get("text")
            if isinstance(text, str) and text.strip():
                messages.append((text, event["index"]))
    if not messages:
        raise AttestationError(f"{label} trace has no visible agent response")
    return messages[-1]


def _normalized_coverage_arguments(arguments: Mapping[str, Any], label: str) -> tuple[Any, ...]:
    allowed = {"query", "top_k", "per_facet", "maximum_facets", "page", "page_size"}
    if set(arguments) - allowed or "query" not in arguments or "page" not in arguments:
        raise AttestationError(f"{label} coverage arguments violate the closed runtime schema")
    query = arguments["query"]
    if not isinstance(query, str) or not query.strip():
        raise AttestationError(f"{label} coverage query is invalid")
    values = (
        arguments.get("top_k", 30),
        arguments.get("per_facet", 12),
        arguments.get("maximum_facets", 12),
        arguments["page"],
        arguments.get("page_size", 48),
    )
    if any(isinstance(value, bool) or not isinstance(value, int) or value < 1 for value in values):
        raise AttestationError(f"{label} coverage integer arguments are invalid")
    return query, values[0], values[1], values[2], values[4], values[3]


def _attest_bootstrap(
    call: ToolCall,
    expected_markdown: str,
    expected_identity: Mapping[str, Any],
    label: str,
) -> dict[str, Any]:
    """Validate the one-shot canonical skill bootstrap response."""

    if call.name != BOOTSTRAP or call.arguments is None or dict(call.arguments) != {}:
        raise AttestationError(f"{label} bootstrap arguments violate the closed runtime schema")
    response_text, response = _mcp_text(call, f"{label} bootstrap")
    exact_keys(response, set(BOOTSTRAP_RESPONSE_KEYS), f"{label} bootstrap response")
    if (
        list(response) != BOOTSTRAP_RESPONSE_KEYS
        or json.dumps(
            response,
            ensure_ascii=False,
            separators=(",", ":"),
            allow_nan=False,
        )
        != response_text
    ):
        raise AttestationError(
            f"{label} bootstrap response is not canonical with the required field order"
        )
    markdown = response["skill_markdown"]
    byte_count = response["byte_count"]
    if not isinstance(markdown, str):
        raise AttestationError(f"{label} bootstrap skill_markdown must be a string")
    payload = markdown.encode("utf-8")
    if (
        response["schema"] != BOOTSTRAP_SCHEMA
        or response["skill_id"] != BOOTSTRAP_SKILL_ID
        or not _valid_hash(response["skill_sha256"])
        or response["skill_sha256"] != hashlib.sha256(payload).hexdigest()
        or isinstance(byte_count, bool)
        or not isinstance(byte_count, int)
        or byte_count != len(payload)
        or markdown != expected_markdown
        or response["skill_sha256"] != expected_identity["skill_sha256"]
        or byte_count != expected_identity["byte_count"]
    ):
        raise AttestationError(
            f"{label} bootstrap response does not bind the exact frozen skill bytes"
        )
    return {key: response[key] for key in BOOTSTRAP_RESPONSE_KEYS if key != "skill_markdown"}


def _attest_treatment(
    calls: Sequence[ToolCall],
    output: str,
    question_id: str,
    label: str,
    expected_skill_markdown: str,
    expected_bootstrap: Mapping[str, Any],
) -> tuple[dict[str, Any], list[int], int, str, str, int, str, int]:
    if any(call.is_shell_or_command for call in calls):
        raise AttestationError(f"{label} contains a shell or command tool call")
    if any(not call.is_semantic_okf for call in calls):
        raise AttestationError(f"{label} contains a tool outside the isolated Semantic OKF MCP server")
    if any(call.name not in EXPECTED_SEMANTIC_TOOLS for call in calls):
        raise AttestationError(f"{label} contains an unexpected Semantic OKF tool")
    if any(
        call.failed_mcp and call.name not in {PREPARE, CONFIRM}
        for call in calls
        if call.is_mcp
    ):
        raise AttestationError(f"{label} contains a failed non-protocol MCP call")
    if len(calls) < 5 or calls[0].name != BOOTSTRAP:
        raise AttestationError(f"{label} must begin with semantic_okf_bootstrap_skill")
    if [call.name for call in calls].count(BOOTSTRAP) != 1:
        raise AttestationError(f"{label} must contain exactly one skill bootstrap")
    bootstrap = _attest_bootstrap(
        calls[0], expected_skill_markdown, expected_bootstrap, label
    )
    if calls[1].name != INSPECT:
        raise AttestationError(f"{label} bootstrap must be followed by semantic_okf_inspect")
    if [call.name for call in calls].count(INSPECT) != 1:
        raise AttestationError(f"{label} must contain exactly one inspection")
    inspect_payload = _mcp_text(calls[1], f"{label} inspect")[1]
    if not isinstance(inspect_payload, Mapping) or inspect_payload.get("status") != "pass":
        raise AttestationError(f"{label} inspection did not pass")

    protocol_indexes = [
        index for index, call in enumerate(calls) if call.name in {PREPARE, CONFIRM}
    ]
    if not protocol_indexes:
        raise AttestationError(
            f"{label} must end with one or more prepare calls followed by exactly one final confirm"
        )
    first_protocol = protocol_indexes[0]
    protocol_calls = calls[first_protocol:]
    if any(call.name not in {PREPARE, CONFIRM} for call in protocol_calls):
        raise AttestationError(f"{label} has a non-protocol call after answer preparation began")
    successful_confirms = [
        call for call in protocol_calls if call.name == CONFIRM and not call.failed_mcp
    ]
    if (
        len(successful_confirms) != 1
        or protocol_calls[-1] is not successful_confirms[0]
    ):
        raise AttestationError(f"{label} must contain exactly one successful terminal confirm")
    final_prepare_start = len(protocol_calls) - 2
    while (
        final_prepare_start >= 0
        and protocol_calls[final_prepare_start].name == PREPARE
        and not protocol_calls[final_prepare_start].failed_mcp
    ):
        final_prepare_start -= 1
    final_prepare_start += 1
    prepare_calls = protocol_calls[final_prepare_start:-1]
    if not prepare_calls:
        raise AttestationError(
            f"{label} terminal confirm has no fresh successful prepare after recovery"
        )
    recovered_protocol_failures = sum(call.failed_mcp for call in protocol_calls)

    coverage_calls = calls[2:first_protocol]
    if not coverage_calls or any(call.name != COVERAGE for call in coverage_calls):
        raise AttestationError(f"{label} must read coverage pages between inspect and finalization")

    coverage_pages: list[int] = []
    coverage_signature: tuple[Any, ...] | None = None
    total_pages: int | None = None
    full_sha: str | None = None
    priority_order: str | None = None
    priority_order_sha: str | None = None
    page_claim_ids: dict[int, list[str]] = {}
    for position, call in enumerate(coverage_calls, 1):
        arguments = call.arguments or {}
        normalized = _normalized_coverage_arguments(arguments, f"{label} coverage {position}")
        signature, page = normalized[:-1], normalized[-1]
        if coverage_signature is None:
            coverage_signature = signature
        elif coverage_signature != signature:
            raise AttestationError(f"{label} coverage pages use different query parameters")
        payload = _mcp_text(call, f"{label} coverage {position}")[1]
        if not isinstance(payload, Mapping) or payload.get("status") != "pass":
            raise AttestationError(f"{label} coverage page did not pass")
        parameters = payload.get("parameters")
        pagination = payload.get("pagination")
        full = payload.get("full_coverage")
        if not all(isinstance(value, Mapping) for value in (parameters, pagination, full)):
            raise AttestationError(f"{label} coverage result lacks deterministic bindings")
        expected_parameters = {
            "top_k": signature[1],
            "per_facet": signature[2],
            "maximum_facets": signature[3],
            "page": page,
            "page_size": signature[4],
        }
        if payload.get("query") != signature[0] or parameters != expected_parameters:
            raise AttestationError(f"{label} coverage result differs from its call parameters")
        observed_total = pagination.get("total_pages")
        observed_sha = full.get("sha256")
        observed_priority_order = full.get("priority_order")
        observed_priority_order_sha = full.get("priority_order_sha256")
        if (
            pagination.get("page") != page
            or pagination.get("page_size") != signature[4]
            or isinstance(observed_total, bool)
            or not isinstance(observed_total, int)
            or observed_total < 1
            or not _valid_hash(observed_sha)
            or observed_priority_order != PRIORITY_ORDER
            or not _valid_hash(observed_priority_order_sha)
            or full.get("recomputed") is not True
        ):
            raise AttestationError(f"{label} coverage pagination or full-pack binding differs")
        claims = payload.get("claims")
        if not isinstance(claims, list):
            raise AttestationError(f"{label} coverage page lacks its ordered claims")
        claim_ids: list[str] = []
        for claim in claims:
            claim_id = claim.get("claim_id") if isinstance(claim, Mapping) else None
            if not isinstance(claim_id, str) or not claim_id:
                raise AttestationError(f"{label} coverage page has an invalid claim identity")
            claim_ids.append(claim_id)
        if len(set(claim_ids)) != len(claim_ids) or page in page_claim_ids:
            raise AttestationError(f"{label} coverage page repeats a priority-order claim")
        page_claim_ids[page] = claim_ids
        if total_pages is None:
            total_pages = observed_total
            full_sha = observed_sha
            priority_order = observed_priority_order
            priority_order_sha = observed_priority_order_sha
        elif (
            total_pages != observed_total
            or full_sha != observed_sha
            or priority_order != observed_priority_order
            or priority_order_sha != observed_priority_order_sha
        ):
            raise AttestationError(f"{label} coverage pages do not bind one deterministic pack")
        coverage_pages.append(page)
    assert (
        total_pages is not None
        and coverage_signature is not None
        and priority_order is not None
        and priority_order_sha is not None
    )
    if coverage_pages != list(range(1, total_pages + 1)):
        raise AttestationError(
            f"{label} did not read every coverage page exactly once in ascending order"
        )
    ordered_claim_ids = [
        claim_id
        for page in range(1, total_pages + 1)
        for claim_id in page_claim_ids[page]
    ]
    if len(set(ordered_claim_ids)) != len(ordered_claim_ids):
        raise AttestationError(f"{label} coverage pages repeat a priority-order claim")
    recomputed_priority_sha = hashlib.sha256(
        json.dumps(
            ordered_claim_ids,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    ).hexdigest()
    if recomputed_priority_sha != priority_order_sha:
        raise AttestationError(
            f"{label} coverage priority-order SHA-256 differs from the paged claim order"
        )

    required_prepare = {"question_id", "query", "draft"}
    allowed_prepare = required_prepare | {
        "summary_min_words",
        "summary_max_words",
        "top_k",
        "per_facet",
        "maximum_facets",
        "page_size",
    }
    candidate_json = ""
    candidate_sha = ""
    candidate_bytes = 0
    for position, prepare in enumerate(prepare_calls, 1):
        prepare_arguments = prepare.arguments or {}
        prepare_label = f"{label} prepare {position}"
        if (
            not required_prepare <= set(prepare_arguments)
            or set(prepare_arguments) - allowed_prepare
        ):
            raise AttestationError(
                f"{prepare_label} arguments violate the closed runtime schema"
            )
        if prepare_arguments["question_id"] != question_id:
            raise AttestationError(f"{prepare_label} question identity differs")
        if (
            prepare_arguments["query"],
            prepare_arguments.get("top_k", 30),
            prepare_arguments.get("per_facet", 12),
            prepare_arguments.get("maximum_facets", 12),
            prepare_arguments.get("page_size", 48),
        ) != coverage_signature:
            raise AttestationError(
                f"{prepare_label} parameters differ from the priority-ordered coverage session"
            )
        envelope_text, envelope = _mcp_text(prepare, prepare_label)
        exact_keys(
            envelope,
            set(PREPARED_ENVELOPE_KEYS),
            f"{prepare_label} prepared-answer envelope",
        )
        if (
            list(envelope) != PREPARED_ENVELOPE_KEYS
            or json.dumps(
                envelope,
                ensure_ascii=False,
                separators=(",", ":"),
                allow_nan=False,
            )
            != envelope_text
        ):
            raise AttestationError(
                f"{prepare_label} prepared-answer envelope is not canonical with the "
                "required field order"
            )
        if envelope["schema"] != PREPARED_ANSWER_SCHEMA:
            raise AttestationError(f"{prepare_label} prepared-answer envelope schema differs")
        candidate_json = envelope["candidate_json"]
        if not isinstance(candidate_json, str):
            raise AttestationError(
                f"{prepare_label} prepared-answer candidate_json must be a string"
            )
        candidate = strict_json_text(candidate_json, f"{prepare_label} candidate_json")
        if not isinstance(candidate, Mapping) or candidate.get("question_id") != question_id:
            raise AttestationError(
                f"{prepare_label} did not return the contracted answer object"
            )
        canonical_candidate = json.dumps(
            candidate, ensure_ascii=False, separators=(",", ":"), allow_nan=False
        )
        if candidate_json != canonical_candidate:
            raise AttestationError(f"{prepare_label} candidate is not canonical JSON")
        candidate_sha, candidate_bytes = _hash_bytes(candidate_json)
        envelope_byte_count = envelope["byte_count"]
        if (
            not _valid_hash(envelope["response_sha256"])
            or envelope["response_sha256"] != candidate_sha
            or isinstance(envelope_byte_count, bool)
            or not isinstance(envelope_byte_count, int)
            or envelope_byte_count != candidate_bytes
        ):
            raise AttestationError(
                f"{prepare_label} prepared-answer envelope digest or byte count does not "
                "bind candidate_json"
            )

    confirm = protocol_calls[-1]
    confirm_arguments = confirm.arguments or {}
    if set(confirm_arguments) != {"response_sha256"}:
        raise AttestationError(f"{label} confirm arguments violate the closed runtime schema")
    if (
        not _valid_hash(confirm_arguments.get("response_sha256"))
        or confirm_arguments["response_sha256"] != candidate_sha
    ):
        raise AttestationError(
            f"{label} confirm digest differs from the last prepared-answer envelope"
        )
    receipt_text, receipt = _mcp_text(confirm, f"{label} confirm")
    exact_keys(
        receipt,
        set(CONFIRMATION_RECEIPT_KEYS),
        f"{label} confirmation receipt",
    )
    if (
        list(receipt) != CONFIRMATION_RECEIPT_KEYS
        or json.dumps(
            receipt,
            ensure_ascii=False,
            separators=(",", ":"),
            allow_nan=False,
        )
        != receipt_text
    ):
        raise AttestationError(
            f"{label} confirmation receipt is not canonical with the required field order"
        )
    receipt_byte_count = receipt["byte_count"]
    if (
        receipt["schema"] != CONFIRMATION_SCHEMA
        or receipt["status"] != "confirmed"
        or receipt["response_sha256"] != candidate_sha
        or isinstance(receipt_byte_count, bool)
        or not isinstance(receipt_byte_count, int)
        or receipt_byte_count != candidate_bytes
    ):
        raise AttestationError(
            f"{label} confirmation receipt does not bind the prepared candidate bytes"
        )
    output_sha, output_bytes = _hash_bytes(output)
    if output != candidate_json or output_sha != candidate_sha or output_bytes != candidate_bytes:
        raise AttestationError(
            f"{label} published Promptfoo output differs from the confirmed candidate bytes"
        )
    return (
        bootstrap,
        coverage_pages,
        total_pages,
        priority_order,
        priority_order_sha,
        recovered_protocol_failures,
        candidate_sha,
        candidate_bytes,
    )


def _attest_shell_isolation(
    row: Mapping[str, Any],
    trace: Mapping[str, Any],
    profile: str,
    label: str,
) -> dict[str, Any] | None:
    """Bind the treatment-only wrapper receipt to response metadata and raw trace."""

    response = row.get("response")
    metadata = response.get("metadata") if isinstance(response, Mapping) else None
    if not isinstance(metadata, Mapping):
        raise AttestationError(f"{label} response metadata is absent")
    response_stderr = metadata.get("stderr")
    trace_stderr = trace.get("stderr")
    if profile != TREATMENT:
        expected_text, _ = _expected_shell_isolation()
        if (
            response_stderr is not None
            and not isinstance(response_stderr, str)
            or trace_stderr is not None
            and not isinstance(trace_stderr, str)
        ):
            raise AttestationError(f"{label} control stderr is invalid")
        transport_matches = response_stderr == trace_stderr or (
            isinstance(trace_stderr, str)
            and response_stderr == trace_stderr.rstrip("\n")
        )
        if not transport_matches:
            raise AttestationError(f"{label} control stderr metadata and trace disagree")
        if isinstance(trace_stderr, str) and expected_text.rstrip("\n") in trace_stderr:
            raise AttestationError(
                f"{label} control contains a treatment shell-isolation receipt"
            )
        return None

    expected_text, expected_report = _expected_shell_isolation()
    # The command trace preserves the wrapper's one terminal LF. Promptfoo's
    # response-metadata transport strips exactly that LF and nothing else.
    if response_stderr != expected_text[:-1] or trace_stderr != expected_text:
        raise AttestationError(
            f"{label} treatment shell-isolation receipt is missing or differs"
        )
    receipt_text = expected_text[:-1]
    receipt = strict_json_text(receipt_text, f"{label} shell-isolation receipt")
    exact_keys(
        receipt,
        set(SHELL_ISOLATION_KEYS),
        f"{label} shell-isolation receipt",
    )
    if (
        list(receipt) != SHELL_ISOLATION_KEYS
        or json.dumps(
            receipt,
            ensure_ascii=False,
            separators=(",", ":"),
            allow_nan=False,
        )
        != receipt_text
        or receipt["schema"] != SHELL_ISOLATION_SCHEMA
        or receipt["skill_id"] != BOOTSTRAP_SKILL_ID
        or receipt["shell_tool_disabled"] is not True
    ):
        raise AttestationError(
            f"{label} treatment shell-isolation receipt is not canonical"
        )
    return expected_report


def _row_attestation(
    row: Mapping[str, Any],
    profile: str,
    question: str,
    repetition: int,
    trace_path: Path,
    trace_archived: bool,
    trace: Mapping[str, Any],
    hook: Mapping[str, Any],
    expected_skill_markdown: str,
    expected_bootstrap: Mapping[str, Any],
) -> dict[str, Any]:
    label = f"{profile}/{question}/repetition-{repetition}"
    events, tool_events = _trace_events(trace, hook, label)
    shell_isolation = _attest_shell_isolation(row, trace, profile, label)
    output = row["response"]["output"]
    raw_output, last_agent_message_index = _last_visible_message(events, label)
    calls, superseded_control_command_starts = _paired_calls(
        tool_events, label, profile, last_agent_message_index
    )
    raw_output_sha, raw_output_bytes = _hash_bytes(raw_output)
    output_sha, output_bytes = _hash_bytes(output)
    semantic_count = sum(call.is_semantic_okf for call in calls)
    mcp_count = sum(call.is_mcp for call in calls)
    shell_count = sum(call.is_shell_or_command for call in calls)
    failed_count = sum(call.failed_mcp for call in calls if call.is_mcp)
    protocol_call_outcomes = [
        {
            "tool": call.name,
            "status": "failed" if call.failed_mcp else "success",
        }
        for call in calls
        if call.name in {PREPARE, CONFIRM}
    ]
    coverage_pages: list[int] = []
    coverage_total_pages = 0
    coverage_priority_order: str | None = None
    coverage_priority_order_sha: str | None = None
    recovered_protocol_failures = 0
    confirmation_sha: str | None = None
    confirmation_bytes: int | None = None
    bootstrap: dict[str, Any] | None = None
    if profile == TREATMENT:
        (
            bootstrap,
            coverage_pages,
            coverage_total_pages,
            coverage_priority_order,
            coverage_priority_order_sha,
            recovered_protocol_failures,
            confirmation_sha,
            confirmation_bytes,
        ) = _attest_treatment(
            calls,
            output,
            question,
            label,
            expected_skill_markdown,
            expected_bootstrap,
        )
    else:
        if semantic_count != 0:
            raise AttestationError(f"{label} control trace invoked Semantic OKF MCP")
        if raw_output != output:
            raise AttestationError(
                f"{label} control Promptfoo output differs from the final raw agent message"
            )
    return {
        "profile_id": profile,
        "question_id": question,
        "repetition": repetition,
        "trace_sha256": sha256(trace_path),
        "trace_archived": trace_archived,
        "raw_output_sha256": raw_output_sha,
        "raw_output_byte_count": raw_output_bytes,
        "output_sha256": output_sha,
        "output_byte_count": output_bytes,
        "publication_corrected": raw_output != output,
        "bootstrap": bootstrap,
        "shell_isolation": shell_isolation,
        "tool_counts": {
            "recorded_events": len(tool_events),
            "completed_calls": len(calls),
            "superseded_control_command_starts": (
                superseded_control_command_starts
            ),
            "mcp_calls": mcp_count,
            "semantic_okf_calls": semantic_count,
            "shell_or_command_calls": shell_count,
            "failed_mcp_calls": failed_count,
        },
        "ordered_tool_names": [call.name for call in calls],
        "coverage_pages": coverage_pages,
        "coverage_total_pages": coverage_total_pages,
        "coverage_priority_order": coverage_priority_order,
        "coverage_priority_order_sha256": coverage_priority_order_sha,
        "protocol_call_outcomes": protocol_call_outcomes,
        "recovered_protocol_failure_count": recovered_protocol_failures,
        "confirmation_sha256": confirmation_sha,
        "confirmation_byte_count": confirmation_bytes,
    }


def _aggregates(rows: Sequence[Mapping[str, Any]], profiles: Sequence[str]) -> dict[str, Any]:
    by_profile: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for row in rows:
        by_profile[str(row["profile_id"])].append(row)
    profile_rows: dict[str, Any] = {}
    for profile in profiles:
        values = by_profile[profile]
        profile_rows[profile] = {
            "answer_count": len(values),
            "archived_trace_count": sum(row["trace_archived"] is True for row in values),
            "completed_tool_calls": sum(row["tool_counts"]["completed_calls"] for row in values),
            "superseded_control_command_starts": sum(
                row["tool_counts"]["superseded_control_command_starts"]
                for row in values
            ),
            "mcp_calls": sum(row["tool_counts"]["mcp_calls"] for row in values),
            "semantic_okf_calls": sum(row["tool_counts"]["semantic_okf_calls"] for row in values),
            "shell_or_command_calls": sum(row["tool_counts"]["shell_or_command_calls"] for row in values),
            "failed_mcp_calls": sum(row["tool_counts"]["failed_mcp_calls"] for row in values),
            "bootstrapped_answers": sum(row["bootstrap"] is not None for row in values),
            "shell_isolated_answers": sum(
                row["shell_isolation"] is not None for row in values
            ),
            "recovered_protocol_failures": sum(
                row["recovered_protocol_failure_count"] for row in values
            ),
            "answers_with_protocol_recovery": sum(
                row["recovered_protocol_failure_count"] > 0 for row in values
            ),
            "confirmed_answers": sum(row["confirmation_sha256"] is not None for row in values),
            "publication_corrections": sum(
                row["publication_corrected"] is True for row in values
            ),
        }
    return {
        "answer_count": len(rows),
        "trace_count": len(rows),
        "archived_trace_count": sum(row["trace_archived"] is True for row in rows),
        "unique_trace_sha256_count": len({row["trace_sha256"] for row in rows}),
        "output_nonempty_count": sum(row["output_byte_count"] > 0 for row in rows),
        "control_answer_count": sum(len(by_profile[profile]) for profile in profiles if profile != TREATMENT),
        "treatment_answer_count": len(by_profile[TREATMENT]),
        "confirmed_treatment_count": sum(
            row["confirmation_sha256"] is not None for row in by_profile[TREATMENT]
        ),
        "bootstrapped_treatment_count": sum(
            row["bootstrap"] is not None for row in by_profile[TREATMENT]
        ),
        "shell_isolated_treatment_count": sum(
            row["shell_isolation"] is not None for row in by_profile[TREATMENT]
        ),
        "recovered_protocol_failure_count": sum(
            row["recovered_protocol_failure_count"] for row in by_profile[TREATMENT]
        ),
        "protocol_recovery_answer_count": sum(
            row["recovered_protocol_failure_count"] > 0
            for row in by_profile[TREATMENT]
        ),
        "publication_correction_count": sum(
            row["publication_corrected"] is True for row in rows
        ),
        "superseded_control_command_start_count": sum(
            row["tool_counts"]["superseded_control_command_starts"] for row in rows
        ),
        "profiles": profile_rows,
    }


def build_attestation(
    promptfoo_path: Path,
    contract: Mapping[str, Any],
    *,
    contract_path: Path,
    config_path: Path,
    manifest_path: Path,
    answer_report_path: Path,
    publication_gate_script_path: Path = PUBLICATION_GATE_SCRIPT,
    publication_gate_launcher_path: Path = PUBLICATION_GATE_LAUNCHER,
    treatment_skill_path: Path = TREATMENT_SKILL,
    attestor_path: Path | None = None,
    repository_root: Path = REPO_ROOT,
    archived_workspace_roots: Mapping[str, Path | str] | None = None,
) -> dict[str, Any]:
    """Inspect every raw Codex trace and build one compact attestation report."""

    root = repository_root.resolve(strict=True)
    promptfoo_path = promptfoo_path.resolve(strict=True)
    bindings = {
        "promptfoo": _binding(promptfoo_path, root, "Promptfoo input"),
        "answer_contract": _binding(contract_path, root, "answer contract"),
        "skill_arena_config": _binding(config_path, root, "Skill Arena config"),
        "skill_arena_manifest": _binding(manifest_path, root, "Skill Arena manifest"),
        "answer_output_report": _binding(answer_report_path, root, "answer-output report"),
        "publication_gate_script": _binding(
            publication_gate_script_path, root, "publication gate script"
        ),
        "publication_gate_launcher": _binding(
            publication_gate_launcher_path, root, "publication gate launcher"
        ),
        "treatment_skill": _binding(
            treatment_skill_path, root, "frozen treatment skill"
        ),
    }
    expected_skill_markdown, expected_bootstrap = _skill_material(
        treatment_skill_path, "frozen treatment skill"
    )
    manifest = strict_json_file(manifest_path, "Skill Arena manifest")
    manifest_runtime_contract = _validate_manifest_runtime_contract(
        manifest, expected_bootstrap
    )
    implementation_path = (attestor_path or Path(__file__)).resolve(strict=True)
    implementation = _binding(implementation_path, root, "trace attestor")
    answer_report = strict_json_file(answer_report_path, "checked answer-output report")
    benchmark = _expected_benchmark(contract)
    archive_roots = _validated_archived_workspace_roots(
        archived_workspace_roots, benchmark["profiles"], root
    )
    _answer_report_bindings(
        answer_report,
        benchmark,
        bindings["promptfoo"],
        bindings["skill_arena_config"],
        bindings["skill_arena_manifest"],
    )
    promptfoo = strict_json_file(promptfoo_path, "Promptfoo results")
    result_wrapper = promptfoo.get("results")
    raw_rows = result_wrapper.get("results") if isinstance(result_wrapper, Mapping) else None
    if not isinstance(raw_rows, list) or len(raw_rows) != benchmark["answer_count"]:
        raise AttestationError("Promptfoo results must contain exactly 90 rows")

    grouped: dict[
        tuple[str, str],
        list[tuple[str, Mapping[str, Any], Path, bool, Mapping[str, Any]]],
    ] = defaultdict(list)
    raw_ids: set[str] = set()
    trace_paths: set[Path] = set()
    for raw in raw_rows:
        if not isinstance(raw, Mapping):
            raise AttestationError("Promptfoo result rows must be objects")
        raw_id = raw.get("id")
        if not isinstance(raw_id, str) or not raw_id or raw_id in raw_ids:
            raise AttestationError("Promptfoo raw row IDs must be unique nonempty strings")
        raw_ids.add(raw_id)
        profile, question, _ = _cell_identity(raw, benchmark)
        trace_path, hook, trace_archived = _trace_path(
            raw, f"{profile}/{question}", profile, archive_roots
        )
        if trace_path in trace_paths:
            raise AttestationError("one raw execution trace is reused by multiple Promptfoo rows")
        trace_paths.add(trace_path)
        trace = strict_json_file(trace_path, f"{profile}/{question} trace")
        grouped[(profile, question)].append(
            (raw_id, raw, trace_path, trace_archived, hook | {"_trace": trace})
        )

    expected_cells = {
        (profile, question)
        for profile in benchmark["profiles"]
        for question in benchmark["question_ids"]
    }
    if set(grouped) != expected_cells or any(len(rows) != 3 for rows in grouped.values()):
        raise AttestationError("Promptfoo profile/question/repetition identities differ")

    rows: list[dict[str, Any]] = []
    for profile in benchmark["profiles"]:
        for question in benchmark["question_ids"]:
            cell = sorted(grouped[(profile, question)], key=lambda item: item[0])
            for repetition, (_, raw, trace_path, trace_archived, bundled) in enumerate(
                cell, 1
            ):
                trace = bundled["_trace"]
                hook = {key: value for key, value in bundled.items() if key != "_trace"}
                rows.append(
                    _row_attestation(
                        raw,
                        profile,
                        question,
                        repetition,
                        trace_path,
                        trace_archived,
                        trace,
                        hook,
                        expected_skill_markdown,
                        expected_bootstrap,
                    )
                )

    report = {
        "schema_version": SCHEMA,
        "status": "pass",
        "benchmark": benchmark,
        "inputs": bindings,
        "implementation": implementation,
        "trace_contract": _expected_trace_contract(
            benchmark, expected_bootstrap, manifest_runtime_contract
        ),
        "gates": {key: True for key in sorted(GATE_KEYS)},
        "aggregates": _aggregates(rows, benchmark["profiles"]),
        "rows": rows,
    }
    return validate_report(
        report,
        contract,
        answer_report=answer_report,
        contract_path=contract_path,
        config_path=config_path,
        manifest_path=manifest_path,
        answer_report_path=answer_report_path,
        publication_gate_script_path=publication_gate_script_path,
        publication_gate_launcher_path=publication_gate_launcher_path,
        treatment_skill_path=treatment_skill_path,
        attestor_path=implementation_path,
        repository_root=repository_root,
    )


def _reject_machine_paths(value: Any, label: str = "report") -> None:
    if isinstance(value, Mapping):
        for key, item in value.items():
            _reject_machine_paths(item, f"{label}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _reject_machine_paths(item, f"{label}[{index}]")
    elif isinstance(value, str) and (
        ABSOLUTE_WINDOWS.match(value)
        or value.startswith(("/home/", "/Users/", "/tmp/"))
        or value.startswith("\\\\")
    ):
        raise AttestationError(f"compact report contains an absolute machine path at {label}")


def validate_report(
    report: Mapping[str, Any],
    contract: Mapping[str, Any],
    *,
    answer_report: Mapping[str, Any],
    contract_path: Path = DEFAULT_CONTRACT,
    config_path: Path = SKILL_ARENA_CONFIG,
    manifest_path: Path = SKILL_ARENA_MANIFEST,
    answer_report_path: Path = ANSWER_OUTPUT_REPORT,
    publication_gate_script_path: Path = PUBLICATION_GATE_SCRIPT,
    publication_gate_launcher_path: Path = PUBLICATION_GATE_LAUNCHER,
    treatment_skill_path: Path = TREATMENT_SKILL,
    attestor_path: Path | None = None,
    repository_root: Path = REPO_ROOT,
) -> dict[str, Any]:
    """Validate the compact report without requiring ignored raw traces."""

    exact_keys(
        report,
        {
            "schema_version",
            "status",
            "benchmark",
            "inputs",
            "implementation",
            "trace_contract",
            "gates",
            "aggregates",
            "rows",
        },
        "trace attestation",
    )
    if report["schema_version"] != SCHEMA or report["status"] != "pass":
        raise AttestationError("trace attestation schema or status differs")
    benchmark = _expected_benchmark(contract)
    if report["benchmark"] != benchmark:
        raise AttestationError("trace attestation benchmark binding differs")
    inputs = exact_keys(
        report["inputs"],
        {
            "promptfoo",
            "answer_contract",
            "skill_arena_config",
            "skill_arena_manifest",
            "answer_output_report",
            "publication_gate_script",
            "publication_gate_launcher",
            "treatment_skill",
        },
        "trace attestation inputs",
    )
    for name, value in inputs.items():
        _validate_binding_shape(value, f"trace attestation input {name}")
    root = repository_root.resolve(strict=True)
    expected_current = {
        "answer_contract": _binding(contract_path, root, "answer contract"),
        "skill_arena_config": _binding(config_path, root, "Skill Arena config"),
        "skill_arena_manifest": _binding(manifest_path, root, "Skill Arena manifest"),
        "answer_output_report": _binding(answer_report_path, root, "answer-output report"),
        "publication_gate_script": _binding(
            publication_gate_script_path, root, "publication gate script"
        ),
        "publication_gate_launcher": _binding(
            publication_gate_launcher_path, root, "publication gate launcher"
        ),
        "treatment_skill": _binding(
            treatment_skill_path, root, "frozen treatment skill"
        ),
    }
    for name, binding in expected_current.items():
        if inputs[name] != binding:
            raise AttestationError(f"trace attestation {name} binding differs")
    _answer_report_bindings(
        answer_report,
        benchmark,
        inputs["promptfoo"],
        inputs["skill_arena_config"],
        inputs["skill_arena_manifest"],
    )
    expected_implementation = _binding(
        (attestor_path or Path(__file__)).resolve(strict=True),
        root,
        "trace attestor",
    )
    if report["implementation"] != expected_implementation:
        raise AttestationError("trace attestation implementation binding differs")
    _, expected_bootstrap = _skill_material(
        treatment_skill_path, "frozen treatment skill"
    )
    manifest = strict_json_file(manifest_path, "Skill Arena manifest")
    manifest_runtime_contract = _validate_manifest_runtime_contract(
        manifest, expected_bootstrap
    )
    expected_contract = _expected_trace_contract(
        benchmark, expected_bootstrap, manifest_runtime_contract
    )
    if report["trace_contract"] != expected_contract:
        raise AttestationError("trace attestation runtime contract differs")
    gates = exact_keys(report["gates"], GATE_KEYS, "trace attestation gates")
    if any(value is not True for value in gates.values()):
        raise AttestationError("trace attestation contains a failed gate")
    rows = report["rows"]
    if not isinstance(rows, list) or len(rows) != 90:
        raise AttestationError("trace attestation must contain exactly 90 rows")
    expected_identities = [
        (profile, question, repetition)
        for profile in benchmark["profiles"]
        for question in benchmark["question_ids"]
        for repetition in range(1, benchmark["repetitions_per_cell"] + 1)
    ]
    observed_identities: list[tuple[Any, Any, Any]] = []
    for row in rows:
        exact_keys(row, ROW_KEYS, "trace attestation row")
        observed_identities.append((row["profile_id"], row["question_id"], row["repetition"]))
        if (
            not _valid_hash(row["trace_sha256"])
            or not _valid_hash(row["raw_output_sha256"])
            or not _valid_hash(row["output_sha256"])
        ):
            raise AttestationError("trace attestation row hash is invalid")
        if not isinstance(row["trace_archived"], bool):
            raise AttestationError("trace attestation archive provenance flag is invalid")
        if any(
            isinstance(value, bool) or not isinstance(value, int) or value < 1
            for value in (row["raw_output_byte_count"], row["output_byte_count"])
        ):
            raise AttestationError("trace attestation output byte count is invalid")
        if not isinstance(row["publication_corrected"], bool):
            raise AttestationError("trace attestation publication correction flag is invalid")
        differs = (
            row["raw_output_sha256"] != row["output_sha256"]
            or row["raw_output_byte_count"] != row["output_byte_count"]
        )
        if row["publication_corrected"] is not differs:
            raise AttestationError(
                "trace attestation publication correction flag differs from its hashes"
            )
        counts = exact_keys(row["tool_counts"], TOOL_COUNT_KEYS, "trace attestation tool counts")
        if any(isinstance(value, bool) or not isinstance(value, int) or value < 0 for value in counts.values()):
            raise AttestationError("trace attestation tool count is invalid")
        names = row["ordered_tool_names"]
        pages = row["coverage_pages"]
        if not isinstance(names, list) or not all(isinstance(item, str) and item for item in names):
            raise AttestationError("trace attestation ordered tool names are invalid")
        if (
            counts["completed_calls"] != len(names)
            or counts["recorded_events"]
            != 2 * len(names) + counts["superseded_control_command_starts"]
        ):
            raise AttestationError("trace attestation completed tool/event counts differ")
        if not isinstance(pages, list) or any(isinstance(page, bool) or not isinstance(page, int) or page < 1 for page in pages):
            raise AttestationError("trace attestation coverage page list is invalid")
        outcomes = row["protocol_call_outcomes"]
        recovered = row["recovered_protocol_failure_count"]
        bootstrap = row["bootstrap"]
        shell_isolation = row["shell_isolation"]
        if (
            not isinstance(outcomes, list)
            or isinstance(recovered, bool)
            or not isinstance(recovered, int)
            or recovered < 0
        ):
            raise AttestationError("trace attestation protocol recovery fields are invalid")
        for outcome in outcomes:
            exact_keys(outcome, {"tool", "status"}, "trace attestation protocol outcome")
            if outcome["tool"] not in {PREPARE, CONFIRM} or outcome["status"] not in {
                "success",
                "failed",
            }:
                raise AttestationError("trace attestation protocol outcome differs")
        if row["profile_id"] == TREATMENT:
            exact_keys(
                bootstrap,
                BOOTSTRAP_REPORT_KEYS,
                "trace attestation bootstrap binding",
            )
            exact_keys(
                shell_isolation,
                SHELL_ISOLATION_REPORT_KEYS,
                "trace attestation shell-isolation binding",
            )
            protocol_positions = [
                index for index, name in enumerate(names) if name in {PREPARE, CONFIRM}
            ]
            first_protocol = protocol_positions[0] if protocol_positions else -1
            protocol_suffix = names[first_protocol:] if first_protocol >= 0 else []
            outcome_tools = [outcome["tool"] for outcome in outcomes]
            successful_confirms = [
                index
                for index, outcome in enumerate(outcomes)
                if outcome == {"tool": CONFIRM, "status": "success"}
            ]
            final_prepare = len(outcomes) - 2
            while final_prepare >= 0 and outcomes[final_prepare] == {
                "tool": PREPARE,
                "status": "success",
            }:
                final_prepare -= 1
            clean_final_prepare_count = len(outcomes) - 2 - final_prepare
            recoverable_protocol_valid = (
                first_protocol >= 3
                and names[:2] == [BOOTSTRAP, INSPECT]
                and names.count(BOOTSTRAP) == 1
                and names.count(INSPECT) == 1
                and all(name == COVERAGE for name in names[2:first_protocol])
                and outcome_tools == protocol_suffix
                and len(successful_confirms) == 1
                and successful_confirms[0] == len(outcomes) - 1
                and clean_final_prepare_count >= 1
                and recovered
                == sum(outcome["status"] == "failed" for outcome in outcomes)
            )
            if (
                bootstrap != expected_bootstrap
                or shell_isolation != _expected_shell_isolation()[1]
                or not _valid_hash(row["confirmation_sha256"])
                or row["confirmation_sha256"] != row["output_sha256"]
                or row["confirmation_byte_count"] != row["output_byte_count"]
                or counts["failed_mcp_calls"] != recovered
                or counts["shell_or_command_calls"] != 0
                or counts["superseded_control_command_starts"] != 0
                or counts["mcp_calls"] != counts["completed_calls"]
                or counts["semantic_okf_calls"] != counts["completed_calls"]
                or row["coverage_total_pages"] < 1
                or pages != list(range(1, row["coverage_total_pages"] + 1))
                or row["coverage_priority_order"] != PRIORITY_ORDER
                or not _valid_hash(row["coverage_priority_order_sha256"])
                or not recoverable_protocol_valid
            ):
                raise AttestationError("trace attestation treatment row violates its runtime gates")
        elif (
            bootstrap is not None
            or shell_isolation is not None
            or counts["semantic_okf_calls"] != 0
            or row["raw_output_sha256"] != row["output_sha256"]
            or row["raw_output_byte_count"] != row["output_byte_count"]
            or row["publication_corrected"] is not False
            or pages
            or row["coverage_total_pages"] != 0
            or row["coverage_priority_order"] is not None
            or row["coverage_priority_order_sha256"] is not None
            or outcomes
            or recovered != 0
            or row["confirmation_sha256"] is not None
            or row["confirmation_byte_count"] is not None
        ):
            raise AttestationError("trace attestation control row contains treatment evidence")
    if observed_identities != expected_identities:
        raise AttestationError("trace attestation row identities or order differ")
    aggregates = _aggregates(rows, benchmark["profiles"])
    if report["aggregates"] != aggregates:
        raise AttestationError("trace attestation aggregates differ from its rows")
    if (
        aggregates["answer_count"] != 90
        or aggregates["trace_count"] != 90
        or aggregates["unique_trace_sha256_count"] != 90
        or aggregates["output_nonempty_count"] != 90
        or aggregates["control_answer_count"] != 60
        or aggregates["treatment_answer_count"] != 30
        or aggregates["confirmed_treatment_count"] != 30
        or aggregates["bootstrapped_treatment_count"] != 30
        or aggregates["shell_isolated_treatment_count"] != 30
        or aggregates["profiles"][TREATMENT][
            "superseded_control_command_starts"
        ]
        != 0
    ):
        raise AttestationError("trace attestation aggregate gates differ")
    _reject_machine_paths(report)
    return dict(report)


def render_markdown(report: Mapping[str, Any]) -> str:
    """Render the compact English companion from validated report fields."""

    aggregates = report["aggregates"]
    lines = [
        "# Skill Arena MCP Runtime Attestation",
        "",
        "## Outcome",
        "",
        "The accepted three-arm run contains exactly 90 completed Codex traces routed through the hash-bound publication wrapper. Both controls made zero Semantic OKF MCP calls and published their final raw agent message unchanged. Every ensemble-treatment trace began with exactly one successful one-shot bootstrap that returned the exact frozen skill bytes, then deep-inspected the snapshot, read every deterministic coverage page in the persisted priority order, ended with a clean transaction of one or more successful prepare calls returning canonical digest-bound envelopes and exactly one successful terminal digest confirmation, and published those confirmed candidate bytes even when the raw agent message differed. A failed protocol attempt published nothing and was accepted only when a fresh successful prepare began the final clean transaction. No treatment trace used a shell or command tool, and no bootstrap, inspection, or coverage call failed.",
        "",
        f"The host publication gate corrected {aggregates['publication_correction_count']} of 90 outputs; all corrections, if any, were confined to the 30 treatment answers.",
        f"The treatment recovered {aggregates['recovered_protocol_failure_count']} failed protocol calls across {aggregates['protocol_recovery_answer_count']} answers before their clean final transactions.",
        f"The attestor classified {aggregates['superseded_control_command_start_count']} unpaired control command starts as superseded runtime diagnostics. Each one was an in-progress start followed before the final response by a distinct, fully paired, exact-command retry that completed successfully. These starts are recorded events, not completed tool calls or answer evidence; the same condition remains forbidden in treatment traces.",
        f"The attestor recovered {aggregates['archived_trace_count']} traces from explicit profile-bound archived workspace roots because their original hook paths no longer existed; each recovered file retained the original hook-relative identity and passed the same hash and event checks.",
        "Every treatment response and raw execution trace contains the same canonical wrapper receipt stating that `shell_tool` was disabled. The trace retains the wrapper's one terminal LF and Promptfoo response metadata strips exactly that LF; all other receipt bytes are identical. Every treatment trace independently contains zero shell or command events. Controls contain no such receipt.",
        "",
        "This attests the observed execution path and transport integrity. It does not replace the separate retrieval, answer-quality, or evidence-validity scores.",
        "",
        "## Aggregate evidence",
        "",
        "| Profile | Answers | Archived traces | Bootstrapped | Shell isolated | Tool calls | Superseded control command starts | MCP calls | Semantic OKF calls | Shell/command calls | Failed MCP calls | Recovered protocol failures | Answers with recovery | Confirmed answers | Publication corrections |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for profile in report["benchmark"]["profiles"]:
        row = aggregates["profiles"][profile]
        lines.append(
            f"| `{profile}` | {row['answer_count']} | {row['archived_trace_count']} | "
            f"{row['bootstrapped_answers']} | "
            f"{row['shell_isolated_answers']} | "
            f"{row['completed_tool_calls']} | "
            f"{row['superseded_control_command_starts']} | "
            f"{row['mcp_calls']} | {row['semantic_okf_calls']} | "
            f"{row['shell_or_command_calls']} | {row['failed_mcp_calls']} | "
            f"{row['recovered_protocol_failures']} | "
            f"{row['answers_with_protocol_recovery']} | "
            f"{row['confirmed_answers']} | {row['publication_corrections']} |"
        )
    lines.extend(
        [
            "",
            "## Per-answer trace identities",
            "",
            "No raw prompts, answers, tool arguments, trace paths, workspace paths, or machine identifiers are reproduced below.",
            "",
            "| Profile | Question | Rep. | Trace source | Trace SHA-256 | Bootstrap skill SHA-256 | Shell receipt SHA-256 | Raw agent SHA-256 | Raw bytes | Published SHA-256 | Published bytes | Corrected | Tools | Superseded control command starts | Coverage pages | Recovered failures | Priority-order SHA-256 | Confirmation SHA-256 |",
            "| --- | --- | ---: | --- | --- | --- | --- | --- | ---: | --- | ---: | --- | --- | ---: | --- | ---: | --- | --- |",
        ]
    )
    for row in report["rows"]:
        tools = " → ".join(row["ordered_tool_names"]) or "none"
        pages = ",".join(str(page) for page in row["coverage_pages"]) or "none"
        priority = row["coverage_priority_order_sha256"] or "not applicable"
        confirmation = row["confirmation_sha256"] or "not applicable"
        bootstrap_sha = (
            row["bootstrap"]["skill_sha256"]
            if row["bootstrap"] is not None
            else "not applicable"
        )
        shell_receipt_sha = (
            row["shell_isolation"]["receipt_sha256"]
            if row["shell_isolation"] is not None
            else "not applicable"
        )
        lines.append(
            f"| `{row['profile_id']}` | `{row['question_id']}` | {row['repetition']} | "
            f"{'archived workspace' if row['trace_archived'] else 'live hook path'} | "
            f"`{row['trace_sha256']}` | `{bootstrap_sha}` | `{shell_receipt_sha}` | "
            f"`{row['raw_output_sha256']}` | "
            f"{row['raw_output_byte_count']} | `{row['output_sha256']}` | "
            f"{row['output_byte_count']} | {'yes' if row['publication_corrected'] else 'no'} | "
            f"{tools} | {row['tool_counts']['superseded_control_command_starts']} | "
            f"{pages} | {row['recovered_protocol_failure_count']} | "
            f"`{priority}` | `{confirmation}` |"
        )
    lines.extend(
        [
            "",
            "## Reproducibility bindings",
            "",
        ]
    )
    for name, binding in report["inputs"].items():
        lines.append(f"- `{name}`: `{binding['path']}` (`{binding['sha256']}`).")
    lines.append(f"- `attestor`: `{report['implementation']['path']}` (`{report['implementation']['sha256']}`).")
    lines.append("")
    return "\n".join(lines)


def _parse_archived_workspace_specs(
    specs: Sequence[str] | None,
) -> dict[str, Path] | None:
    """Parse repeated PROFILE=PATH CLI values without losing duplicate detection."""

    if specs is None:
        return None
    roots: dict[str, Path] = {}
    for spec in specs:
        if not isinstance(spec, str) or "=" not in spec:
            raise AttestationError(
                "each --archived-workspace must use PROFILE=PATH"
            )
        profile, raw_path = spec.split("=", 1)
        if not profile or not raw_path:
            raise AttestationError(
                "each --archived-workspace must use nonempty PROFILE=PATH"
            )
        if profile in roots:
            raise AttestationError(
                f"duplicate archived workspace profile: {profile}"
            )
        roots[profile] = Path(raw_path)
    return roots


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="Completed promptfoo-results.json")
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--config", type=Path, default=SKILL_ARENA_CONFIG)
    parser.add_argument("--config-manifest", type=Path, default=SKILL_ARENA_MANIFEST)
    parser.add_argument("--answer-report", type=Path, default=ANSWER_OUTPUT_REPORT)
    parser.add_argument(
        "--publication-gate-script", type=Path, default=PUBLICATION_GATE_SCRIPT
    )
    parser.add_argument(
        "--publication-gate-launcher", type=Path, default=PUBLICATION_GATE_LAUNCHER
    )
    parser.add_argument("--treatment-skill", type=Path, default=TREATMENT_SKILL)
    parser.add_argument(
        "--archived-workspace",
        action="append",
        metavar="PROFILE=PATH",
        help=(
            "Fallback workspace root for one benchmark profile. Repeat once for every "
            "profile; used only when the hook absolute trace path no longer exists."
        ),
    )
    parser.add_argument("--output-json", type=Path, default=FINAL_JSON)
    parser.add_argument("--output-markdown", type=Path, default=FINAL_MARKDOWN)
    args = parser.parse_args(argv)
    try:
        contract_path = args.contract.resolve(strict=True)
        contract = load_contract(contract_path)
        archive_roots = _parse_archived_workspace_specs(args.archived_workspace)
        report = build_attestation(
            args.input,
            contract,
            contract_path=contract_path,
            config_path=args.config.resolve(strict=True),
            manifest_path=args.config_manifest.resolve(strict=True),
            answer_report_path=args.answer_report.resolve(strict=True),
            publication_gate_script_path=args.publication_gate_script.resolve(strict=True),
            publication_gate_launcher_path=args.publication_gate_launcher.resolve(strict=True),
            treatment_skill_path=args.treatment_skill.resolve(strict=True),
            archived_workspace_roots=archive_roots,
        )
        json_text = json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
        markdown = render_markdown(report)
        write_new(args.output_json.resolve(strict=False), json_text)
        write_new(args.output_markdown.resolve(strict=False), markdown)
    except (AttestationError, OSError, UnicodeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(
        json.dumps(
            {
                "status": "pass",
                "answers": report["aggregates"]["answer_count"],
                "bootstrapped_treatment_answers": report["aggregates"]["bootstrapped_treatment_count"],
                "shell_isolated_treatment_answers": report["aggregates"]["shell_isolated_treatment_count"],
                "confirmed_treatment_answers": report["aggregates"]["confirmed_treatment_count"],
                "publication_corrections": report["aggregates"]["publication_correction_count"],
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
