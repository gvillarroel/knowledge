from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import shutil
import sys
from pathlib import Path
from types import ModuleType
from typing import Any, Callable

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = REPO_ROOT / "evaluations" / "semantic-okf-ensemble" / "scripts"
PRIORITY_ORDER = "persisted-idf-facet-consensus-priority-v1"
PRIORITY_CLAIM_IDS = ["claim-1", "claim-2"]
PRIORITY_ORDER_SHA256 = hashlib.sha256(
    json.dumps(
        PRIORITY_CLAIM_IDS,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")
).hexdigest()
PREPARED_ANSWER_SCHEMA = "semantic-okf-prepared-answer/1.0"
CONFIRMATION_SCHEMA = "semantic-okf-answer-confirmation-receipt/1.0"
BOOTSTRAP_SCHEMA = "semantic-okf-skill-bootstrap/1.0"
BOOTSTRAP_SKILL_ID = "consult-semantic-okf-ensemble"
SHELL_ISOLATION_SCHEMA = "semantic-okf-shell-isolation-receipt/1.0"
CONFIG_MANIFEST_SCHEMA = "semantic-okf-hard-answer-configs/2.2"
FIXTURE_SKILL_MARKDOWN = (
    "---\n"
    "name: consult-semantic-okf-ensemble\n"
    "description: Frozen fixture treatment skill.\n"
    "---\n\n"
    "# Fixture treatment skill\n"
)


def _load_module() -> ModuleType:
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    spec = importlib.util.spec_from_file_location(
        "semantic_okf_ensemble_trace_attestor",
        SCRIPTS / "attest_skill_arena_mcp_runtime.py",
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def attestor() -> ModuleType:
    return _load_module()


def _strict_dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _result(value: Any) -> dict[str, Any]:
    text = value if isinstance(value, str) else json.dumps(
        value, ensure_ascii=False, separators=(",", ":")
    )
    return {
        "content": [{"type": "text", "text": text}],
        "structured_content": None,
    }


def _failed_result(message: str) -> dict[str, Any]:
    result = _result({"status": "error", "message": message})
    result["isError"] = True
    return result


def _prepared_envelope(candidate_json: str) -> str:
    encoded = candidate_json.encode("utf-8")
    return json.dumps(
        {
            "schema": PREPARED_ANSWER_SCHEMA,
            "candidate_json": candidate_json,
            "response_sha256": hashlib.sha256(encoded).hexdigest(),
            "byte_count": len(encoded),
        },
        ensure_ascii=False,
        separators=(",", ":"),
    )


def _confirmation_receipt(candidate_json: str) -> dict[str, Any]:
    encoded = candidate_json.encode("utf-8")
    return {
        "schema": CONFIRMATION_SCHEMA,
        "status": "confirmed",
        "response_sha256": hashlib.sha256(encoded).hexdigest(),
        "byte_count": len(encoded),
    }


def _bootstrap_response(markdown: str = FIXTURE_SKILL_MARKDOWN) -> str:
    payload = markdown.encode("utf-8")
    return json.dumps(
        {
            "schema": BOOTSTRAP_SCHEMA,
            "skill_id": BOOTSTRAP_SKILL_ID,
            "skill_sha256": hashlib.sha256(payload).hexdigest(),
            "byte_count": len(payload),
            "skill_markdown": markdown,
        },
        ensure_ascii=False,
        separators=(",", ":"),
    )


def _shell_isolation_receipt() -> str:
    return json.dumps(
        {
            "schema": SHELL_ISOLATION_SCHEMA,
            "skill_id": BOOTSTRAP_SKILL_ID,
            "shell_tool_disabled": True,
        },
        ensure_ascii=False,
        separators=(",", ":"),
    ) + "\n"


def _tool_pair(
    identity: str,
    item_type: str,
    *,
    server: str | None = None,
    tool: str | None = None,
    arguments: dict[str, Any] | None = None,
    result: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    common: dict[str, Any] = {"id": identity, "type": item_type}
    if server is not None:
        common["server"] = server
    if tool is not None:
        common["tool"] = tool
    if arguments is not None:
        common["arguments"] = arguments
    started = {**common, "result": None, "error": None, "status": "in_progress"}
    completed = {
        **common,
        "result": result,
        "error": None,
        "status": "completed",
    }
    return [
        {"type": "item.started", "data": {"type": "item.started", "item": started}},
        {"type": "item.completed", "data": {"type": "item.completed", "item": completed}},
    ]


def _trace(output: str, label: str, treatment: bool) -> dict[str, Any]:
    events: list[dict[str, Any]] = [
        {"type": "thread.started", "data": {"type": "thread.started", "thread_id": label}}
    ]
    if treatment:
        events.extend(
            _tool_pair(
                "bootstrap",
                "mcp_tool_call",
                server="semantic_okf",
                tool="semantic_okf_bootstrap_skill",
                arguments={},
                result=_result(_bootstrap_response()),
            )
        )
        events.extend(
            _tool_pair(
                "inspect",
                "mcp_tool_call",
                server="semantic_okf",
                tool="semantic_okf_inspect",
                arguments={},
                result=_result({"schema_version": "fixture/1.0", "status": "pass"}),
            )
        )
        query = f"fixture query {label}"
        for page in (1, 2):
            arguments = {
                "query": query,
                "top_k": 30,
                "per_facet": 12,
                "maximum_facets": 12,
                "page": page,
                "page_size": 48,
            }
            payload = {
                "status": "pass",
                "query": query,
                "parameters": {
                    "top_k": 30,
                    "per_facet": 12,
                    "maximum_facets": 12,
                    "page": page,
                    "page_size": 48,
                },
                "pagination": {
                    "page": page,
                    "page_size": 48,
                    "total_pages": 2,
                    "total_claims": len(PRIORITY_CLAIM_IDS),
                },
                "claims": [{"claim_id": PRIORITY_CLAIM_IDS[page - 1]}],
                "full_coverage": {
                    "sha256": "c" * 64,
                    "priority_order": PRIORITY_ORDER,
                    "priority_order_sha256": PRIORITY_ORDER_SHA256,
                    "unique_claims": len(PRIORITY_CLAIM_IDS),
                    "recomputed": True,
                },
            }
            events.extend(
                _tool_pair(
                    f"coverage-{page}",
                    "mcp_tool_call",
                    server="semantic_okf",
                    tool="semantic_okf_coverage_brief",
                    arguments=arguments,
                    result=_result(payload),
                )
            )
        candidate = output
        question_id = json.loads(output)["question_id"]
        events.extend(
            _tool_pair(
                "prepare",
                "mcp_tool_call",
                server="semantic_okf",
                tool="semantic_okf_prepare_answer",
                arguments={
                    "question_id": question_id,
                    "query": query,
                    "draft": {"summary": "fixture", "facets": []},
                    "top_k": 30,
                    "per_facet": 12,
                    "maximum_facets": 12,
                    "page_size": 48,
                },
                result=_result(_prepared_envelope(candidate)),
            )
        )
        encoded = candidate.encode("utf-8")
        events.extend(
            _tool_pair(
                "confirm",
                "mcp_tool_call",
                server="semantic_okf",
                tool="semantic_okf_confirm_answer",
                arguments={"response_sha256": hashlib.sha256(encoded).hexdigest()},
                result=_result(_confirmation_receipt(candidate)),
            )
        )
    else:
        events.extend(_tool_pair("command", "command_execution", result={"output": "fixture"}))
    events.extend(
        [
            {
                "type": "item.completed",
                "data": {
                    "type": "item.completed",
                    "item": {"id": "answer", "type": "agent_message", "text": output},
                },
            },
            {"type": "turn.completed", "data": {"type": "turn.completed"}},
        ]
    )
    for index, event in enumerate(events):
        event["index"] = index
    tool_events = [
        copy.deepcopy(event)
        for event in events
        if event["type"] in {"item.started", "item.completed"}
        and isinstance(event["data"].get("item"), dict)
        and event["data"]["item"].get("type") in {"mcp_tool_call", "command_execution"}
    ]
    return {
        "schemaVersion": 1,
        "generatedAt": label,
        "adapter": "codex",
        "providerId": "codex:command:gpt-5.6-luna",
        "backend": "command",
        "command": "publication-runtime\\run_codex.cmd",
        "args": [],
        "exitCode": 0,
        "stdout": "",
        "stderr": _shell_isolation_receipt() if treatment else None,
        "eventCount": len(events),
        "toolEventCount": len(tool_events),
        "events": events,
        "toolEvents": tool_events,
        "extra": {"fixture": label},
    }


def _fixture(
    root: Path,
    attestor: ModuleType,
) -> tuple[dict[str, Any], dict[str, Path]]:
    benchmark = {
        "id": "semantic-okf-ensemble-hard10-three-arm",
        "profiles": [
            "knowledge-only-control",
            "adaptive-consult-control",
            "ensemble-consult-treatment",
        ],
        "variant_id": "codex-luna-tools",
        "question_ids": [f"q{number:03d}-fixture" for number in range(31, 41)],
        "repetitions_per_cell": 3,
        "total_answers": 90,
    }
    contract = {"benchmark": benchmark}
    paths = {
        "contract": root / "evaluations/semantic-okf-ensemble/contract.json",
        "config": root / "evaluations/semantic-okf-ensemble/skill-arena/compare.yaml",
        "manifest": root / "evaluations/semantic-okf-ensemble/skill-arena/manifest.json",
        "answer": root / "evaluations/semantic-okf-ensemble/answer.json",
        "promptfoo": root / "results/run/promptfoo-results.json",
        "attestor": root / "evaluations/semantic-okf-ensemble/scripts/attestor.py",
        "publication_script": root
        / "skills/consult-semantic-okf-ensemble/publication-runtime/confirmed_output_gate.py",
        "publication_launcher": root
        / "skills/consult-semantic-okf-ensemble/publication-runtime/run_codex.cmd",
        "treatment_skill": root / "skills/consult-semantic-okf-ensemble/SKILL.md",
    }
    _strict_dump(paths["contract"], contract)
    paths["config"].parent.mkdir(parents=True, exist_ok=True)
    paths["config"].write_text("comparison: fixture\n", encoding="utf-8")
    fixture_skill_bytes = FIXTURE_SKILL_MARKDOWN.encode("utf-8")
    fixture_skill_sha256 = hashlib.sha256(fixture_skill_bytes).hexdigest()
    _strict_dump(
        paths["manifest"],
        {
            "schema_version": CONFIG_MANIFEST_SCHEMA,
            "mcp_runtime": {
                "server_version": "1.5.0",
                "allowed_skill_id": BOOTSTRAP_SKILL_ID,
                "controls_expose_tools": False,
                "bootstrap_tool": "semantic_okf_bootstrap_skill",
                "bootstrap_schema": BOOTSTRAP_SCHEMA,
                "bootstrap_key_order": [
                    "schema",
                    "skill_id",
                    "skill_sha256",
                    "byte_count",
                    "skill_markdown",
                ],
                "bootstrap_skill_id": BOOTSTRAP_SKILL_ID,
                "bootstrap_skill_sha256": fixture_skill_sha256,
                "bootstrap_skill_byte_count": len(fixture_skill_bytes),
                "bootstrap_exactly_once": True,
                "bootstrap_first": True,
                "bootstrap_failure_poison": True,
                "tools": [
                    "semantic_okf_bootstrap_skill",
                    "semantic_okf_inspect",
                    "semantic_okf_coverage_brief",
                    "semantic_okf_prepare_answer",
                    "semantic_okf_confirm_answer",
                ],
            },
            "publication_runtime": {
                "treatment_skill_id": BOOTSTRAP_SKILL_ID,
                "treatment_shell_tool_disabled": True,
                "shell_disable_arguments": ["--disable", "shell_tool"],
                "shell_isolation_receipt_schema": SHELL_ISOLATION_SCHEMA,
                "shell_isolation_receipt_key_order": [
                    "schema",
                    "skill_id",
                    "shell_tool_disabled",
                ],
                "controls_shell_policy_unchanged": True,
            },
            "consult_skills": [
                {
                    "skill_id": BOOTSTRAP_SKILL_ID,
                    "path": "skills/consult-semantic-okf-ensemble",
                    "skill_md_sha256": fixture_skill_sha256,
                }
            ],
        },
    )
    paths["attestor"].parent.mkdir(parents=True, exist_ok=True)
    paths["attestor"].write_text("# fixture attestor\n", encoding="utf-8")
    paths["publication_script"].parent.mkdir(parents=True, exist_ok=True)
    paths["publication_script"].write_text("# fixture publication gate\n", encoding="utf-8")
    paths["publication_launcher"].write_text("@echo off\r\n", encoding="utf-8")
    paths["treatment_skill"].write_text(
        FIXTURE_SKILL_MARKDOWN, encoding="utf-8", newline="\n"
    )

    rows: list[dict[str, Any]] = []
    traces = root / "raw-traces"
    for profile_index, profile in enumerate(benchmark["profiles"]):
        for question_index, question in enumerate(benchmark["question_ids"]):
            for repetition in range(1, 4):
                label = f"{profile_index}-{question_index}-{repetition}"
                output = json.dumps(
                    {
                        "question_id": question,
                        "answer": None,
                        "evidence": [],
                    },
                    separators=(",", ":"),
                )
                trace_path = traces / f"trace-{label}.json"
                trace = _trace(output, label, profile == "ensemble-consult-treatment")
                _strict_dump(trace_path, trace)
                hook = {
                    "path": str(trace_path.resolve()),
                    "relativePath": f"raw-traces/{trace_path.name}",
                    "eventCount": trace["eventCount"],
                    "toolEventCount": trace["toolEventCount"],
                }
                variant = benchmark["variant_id"]
                rows.append(
                    {
                        "id": f"row-{profile_index}-{question_index}-{repetition}",
                        "provider": {"id": profile},
                        "metadata": {
                            "benchmarkId": benchmark["id"],
                            "profileId": profile,
                            "promptId": question,
                            "variantId": variant,
                            "scenarioId": f"{variant}-{profile}",
                            "rowId": f"{variant}:{question}",
                        },
                        "vars": {"variantId": variant},
                        "response": {
                            "output": output,
                            "metadata": {
                                "profileId": profile,
                                "variantId": variant,
                                "scenarioId": f"{variant}-{profile}",
                                "stderr": (
                                    _shell_isolation_receipt()[:-1]
                                    if profile == "ensemble-consult-treatment"
                                    else None
                                ),
                                "executionEventHook": hook,
                            },
                        },
                    }
                )
    _strict_dump(paths["promptfoo"], {"results": {"results": rows}})
    relative = lambda path: path.resolve().relative_to(root.resolve()).as_posix()
    prompt_binding = {"path": relative(paths["promptfoo"]), "sha256": _sha(paths["promptfoo"])}
    config_binding = {"path": relative(paths["config"]), "sha256": _sha(paths["config"])}
    manifest_binding = {"path": relative(paths["manifest"]), "sha256": _sha(paths["manifest"])}
    answer_report = {
        "status": "pass",
        "answer_count": 90,
        "benchmark": {
            **benchmark,
            "answer_count": benchmark["total_answers"],
        },
        "inputs": {"promptfoo": {**prompt_binding, "promptfoo_eval_id": "fixture"}},
        "skill_arena": {
            "config": config_binding,
            "config_manifest": manifest_binding,
        },
    }
    answer_report["benchmark"].pop("total_answers")
    _strict_dump(paths["answer"], answer_report)
    return contract, paths


def _build(
    attestor: ModuleType,
    contract: dict[str, Any],
    paths: dict[str, Path],
    root: Path,
    *,
    archived_workspace_roots: dict[str, Path | str] | None = None,
) -> dict[str, Any]:
    return attestor.build_attestation(
        paths["promptfoo"],
        contract,
        contract_path=paths["contract"],
        config_path=paths["config"],
        manifest_path=paths["manifest"],
        answer_report_path=paths["answer"],
        publication_gate_script_path=paths["publication_script"],
        publication_gate_launcher_path=paths["publication_launcher"],
        treatment_skill_path=paths["treatment_skill"],
        attestor_path=paths["attestor"],
        repository_root=root,
        archived_workspace_roots=archived_workspace_roots,
    )


def _archived_fixture_workspaces(
    paths: dict[str, Path], root: Path, *, remove_live: bool
) -> dict[str, Path]:
    promptfoo = json.loads(paths["promptfoo"].read_text(encoding="utf-8"))
    rows = promptfoo["results"]["results"]
    profiles = {row["metadata"]["profileId"] for row in rows}
    roots = {
        profile: root / "results/trace-archives" / profile / "workspace"
        for profile in profiles
    }
    for archive_root in roots.values():
        archive_root.mkdir(parents=True)
    for row in rows:
        profile = row["metadata"]["profileId"]
        hook = row["response"]["metadata"]["executionEventHook"]
        source = Path(hook["path"])
        target = roots[profile].joinpath(*hook["relativePath"].split("/"))
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    if remove_live:
        shutil.rmtree(root / "raw-traces")
    return roots


def _rewrite_trace(path: Path, mutate: Callable[[dict[str, Any]], None]) -> None:
    trace = json.loads(path.read_text(encoding="utf-8"))
    mutate(trace)
    _strict_dump(path, trace)


def _reindex_trace(trace: dict[str, Any]) -> None:
    for index, event in enumerate(trace["events"]):
        event["index"] = index
    trace["toolEvents"] = [
        copy.deepcopy(event)
        for event in trace["events"]
        if event["type"] in {"item.started", "item.completed"}
        and isinstance(event["data"].get("item"), dict)
        and event["data"]["item"].get("type")
        in {"mcp_tool_call", "command_execution"}
    ]
    trace["eventCount"] = len(trace["events"])
    trace["toolEventCount"] = len(trace["toolEvents"])


def _command_start(identity: str, command: str, *, status: str = "in_progress") -> dict[str, Any]:
    return {
        "type": "item.started",
        "data": {
            "type": "item.started",
            "item": {
                "id": identity,
                "type": "command_execution",
                "command": command,
                "aggregated_output": "",
                "exit_code": None,
                "status": status,
            },
        },
    }


def _set_fixture_control_retry(
    trace: dict[str, Any],
    command: str,
    *,
    status: str = "completed",
    exit_code: int = 0,
) -> None:
    for event in trace["events"]:
        item = event["data"].get("item")
        if isinstance(item, dict) and item.get("id") == "command":
            item["command"] = command
            item["aggregated_output"] = "" if event["type"] == "item.started" else "fixture"
            item["exit_code"] = None if event["type"] == "item.started" else exit_code
            item["status"] = "in_progress" if event["type"] == "item.started" else status


def _persist_trace_mutation(
    paths: dict[str, Path], trace_path: Path, trace: dict[str, Any], row_id: str
) -> None:
    _reindex_trace(trace)
    _strict_dump(trace_path, trace)
    _refresh_promptfoo_binding(paths, trace, row_id)


def _cloned_call_events(
    trace: dict[str, Any], source_identity: str, new_identity: str
) -> list[dict[str, Any]]:
    events = [
        copy.deepcopy(event)
        for event in trace["events"]
        if isinstance(event["data"].get("item"), dict)
        and event["data"]["item"].get("id") == source_identity
    ]
    assert len(events) == 2
    for event in events:
        event["data"]["item"]["id"] = new_identity
    return events


def _refresh_promptfoo_binding(
    paths: dict[str, Path], trace: dict[str, Any], row_id: str
) -> None:
    promptfoo = json.loads(paths["promptfoo"].read_text(encoding="utf-8"))
    row = next(
        item for item in promptfoo["results"]["results"] if item["id"] == row_id
    )
    hook = row["response"]["metadata"]["executionEventHook"]
    hook["eventCount"] = trace["eventCount"]
    hook["toolEventCount"] = trace["toolEventCount"]
    _strict_dump(paths["promptfoo"], promptfoo)
    _refresh_answer_promptfoo_sha(paths)


def _refresh_answer_promptfoo_sha(paths: dict[str, Path]) -> None:
    answer = json.loads(paths["answer"].read_text(encoding="utf-8"))
    answer["inputs"]["promptfoo"]["sha256"] = _sha(paths["promptfoo"])
    _strict_dump(paths["answer"], answer)


def _refresh_manifest_binding(paths: dict[str, Path]) -> None:
    answer = json.loads(paths["answer"].read_text(encoding="utf-8"))
    answer["skill_arena"]["config_manifest"]["sha256"] = _sha(paths["manifest"])
    _strict_dump(paths["answer"], answer)


def test_valid_three_arm_trace_attestation_is_compact_and_canonical(
    attestor: ModuleType, tmp_path: Path
) -> None:
    contract, paths = _fixture(tmp_path, attestor)
    report = _build(attestor, contract, paths, tmp_path)

    assert report["status"] == "pass"
    assert report["schema_version"] == (
        "semantic-okf-ensemble-skill-arena-mcp-runtime-attestation/1.7"
    )
    assert report["trace_contract"]["mcp_server_version"] == "1.5.0"
    assert report["trace_contract"]["config_manifest_runtime_contract"][
        "schema_version"
    ] == CONFIG_MANIFEST_SCHEMA
    assert report["aggregates"]["answer_count"] == 90
    assert report["aggregates"]["confirmed_treatment_count"] == 30
    assert report["aggregates"]["bootstrapped_treatment_count"] == 30
    assert report["aggregates"]["shell_isolated_treatment_count"] == 30
    assert report["aggregates"]["publication_correction_count"] == 0
    assert report["aggregates"]["archived_trace_count"] == 0
    assert all(row["trace_archived"] is False for row in report["rows"])
    assert report["aggregates"]["profiles"]["knowledge-only-control"]["semantic_okf_calls"] == 0
    assert report["aggregates"]["profiles"]["adaptive-consult-control"]["semantic_okf_calls"] == 0
    assert all("path" not in row for row in report["rows"])
    assert "raw-traces" not in json.dumps(report)
    assert attestor.validate_report(
        report,
        contract,
        answer_report=json.loads(paths["answer"].read_text(encoding="utf-8")),
        contract_path=paths["contract"],
        config_path=paths["config"],
        manifest_path=paths["manifest"],
        answer_report_path=paths["answer"],
        publication_gate_script_path=paths["publication_script"],
        publication_gate_launcher_path=paths["publication_launcher"],
        treatment_skill_path=paths["treatment_skill"],
        attestor_path=paths["attestor"],
        repository_root=tmp_path,
    ) == report
    markdown = attestor.render_markdown(report)
    assert markdown.startswith("# Skill Arena MCP Runtime Attestation\n")
    assert str(tmp_path) not in markdown


def test_exact_successful_control_retry_classifies_one_superseded_start(
    attestor: ModuleType, tmp_path: Path
) -> None:
    contract, paths = _fixture(tmp_path, attestor)
    trace_path = tmp_path / "raw-traces/trace-0-0-1.json"
    trace = json.loads(trace_path.read_text(encoding="utf-8"))
    command = '"pwsh" -Command \'rg --files knowledge\''
    _set_fixture_control_retry(trace, command)
    retry_start = next(
        index
        for index, event in enumerate(trace["events"])
        if event["type"] == "item.started"
        and event["data"].get("item", {}).get("id") == "command"
    )
    trace["events"].insert(
        retry_start, _command_start("superseded-command", command)
    )
    _persist_trace_mutation(paths, trace_path, trace, "row-0-0-1")

    report = _build(attestor, contract, paths, tmp_path)
    row = report["rows"][0]
    assert row["tool_counts"] == {
        "recorded_events": 3,
        "completed_calls": 1,
        "superseded_control_command_starts": 1,
        "mcp_calls": 0,
        "semantic_okf_calls": 0,
        "shell_or_command_calls": 1,
        "failed_mcp_calls": 0,
    }
    assert report["aggregates"]["superseded_control_command_start_count"] == 1
    assert report["aggregates"]["profiles"]["knowledge-only-control"][
        "superseded_control_command_starts"
    ] == 1
    assert report["aggregates"]["profiles"]["adaptive-consult-control"][
        "superseded_control_command_starts"
    ] == 0
    assert report["aggregates"]["profiles"]["ensemble-consult-treatment"][
        "superseded_control_command_starts"
    ] == 0
    assert (
        "unpaired control command starts as superseded runtime diagnostics"
        in attestor.render_markdown(report)
    )


def test_completed_control_call_without_start_is_rejected(
    attestor: ModuleType, tmp_path: Path
) -> None:
    contract, paths = _fixture(tmp_path, attestor)
    trace_path = tmp_path / "raw-traces/trace-0-0-1.json"
    trace = json.loads(trace_path.read_text(encoding="utf-8"))
    trace["events"] = [
        event
        for event in trace["events"]
        if not (
            event["type"] == "item.started"
            and event["data"].get("item", {}).get("id") == "command"
        )
    ]
    _persist_trace_mutation(paths, trace_path, trace, "row-0-0-1")

    with pytest.raises(attestor.AttestationError, match="without a matching start"):
        _build(attestor, contract, paths, tmp_path)


def test_control_mcp_orphan_is_rejected(attestor: ModuleType, tmp_path: Path) -> None:
    contract, paths = _fixture(tmp_path, attestor)
    trace_path = tmp_path / "raw-traces/trace-0-0-1.json"
    trace = json.loads(trace_path.read_text(encoding="utf-8"))
    trace["events"].insert(
        1,
        {
            "type": "item.started",
            "data": {
                "type": "item.started",
                "item": {
                    "id": "orphan-mcp",
                    "type": "mcp_tool_call",
                    "server": "semantic_okf",
                    "tool": "semantic_okf_inspect",
                    "arguments": {},
                    "status": "in_progress",
                },
            },
        },
    )
    _persist_trace_mutation(paths, trace_path, trace, "row-0-0-1")

    with pytest.raises(attestor.AttestationError, match="not a classifiable.*command_execution"):
        _build(attestor, contract, paths, tmp_path)


def test_treatment_command_orphan_is_rejected_even_with_exact_successful_retry(
    attestor: ModuleType, tmp_path: Path
) -> None:
    contract, paths = _fixture(tmp_path, attestor)
    trace_path = tmp_path / "raw-traces/trace-2-0-1.json"
    trace = json.loads(trace_path.read_text(encoding="utf-8"))
    command = '"pwsh" -Command \'rg --files knowledge\''
    answer_index = next(
        index
        for index, event in enumerate(trace["events"])
        if event["data"].get("item", {}).get("type") == "agent_message"
    )
    retry = _tool_pair("treatment-retry", "command_execution")
    retry[0]["data"]["item"].update(
        {"command": command, "aggregated_output": "", "exit_code": None}
    )
    retry[1]["data"]["item"].update(
        {"command": command, "aggregated_output": "fixture", "exit_code": 0}
    )
    trace["events"][answer_index:answer_index] = [
        _command_start("treatment-orphan", command),
        *retry,
    ]
    _persist_trace_mutation(paths, trace_path, trace, "row-2-0-1")

    with pytest.raises(attestor.AttestationError, match="treatment trace.*unpaired"):
        _build(attestor, contract, paths, tmp_path)


@pytest.mark.parametrize(
    ("command", "status"),
    [("", "in_progress"), ("rg --files knowledge", "completed")],
)
def test_control_orphan_requires_nonempty_in_progress_command(
    attestor: ModuleType, tmp_path: Path, command: str, status: str
) -> None:
    contract, paths = _fixture(tmp_path, attestor)
    trace_path = tmp_path / "raw-traces/trace-0-0-1.json"
    trace = json.loads(trace_path.read_text(encoding="utf-8"))
    trace["events"].insert(1, _command_start("invalid-orphan", command, status=status))
    _persist_trace_mutation(paths, trace_path, trace, "row-0-0-1")

    with pytest.raises(attestor.AttestationError, match="not a classifiable"):
        _build(attestor, contract, paths, tmp_path)


def test_control_orphan_without_later_retry_is_rejected(
    attestor: ModuleType, tmp_path: Path
) -> None:
    contract, paths = _fixture(tmp_path, attestor)
    trace_path = tmp_path / "raw-traces/trace-0-0-1.json"
    trace = json.loads(trace_path.read_text(encoding="utf-8"))
    answer_index = next(
        index
        for index, event in enumerate(trace["events"])
        if event["data"].get("item", {}).get("type") == "agent_message"
    )
    trace["events"].insert(
        answer_index, _command_start("orphan-without-retry", "rg --files knowledge")
    )
    _persist_trace_mutation(paths, trace_path, trace, "row-0-0-1")

    with pytest.raises(attestor.AttestationError, match="no exact later successful"):
        _build(attestor, contract, paths, tmp_path)


def test_control_orphan_with_different_later_command_is_rejected(
    attestor: ModuleType, tmp_path: Path
) -> None:
    contract, paths = _fixture(tmp_path, attestor)
    trace_path = tmp_path / "raw-traces/trace-0-0-1.json"
    trace = json.loads(trace_path.read_text(encoding="utf-8"))
    _set_fixture_control_retry(trace, "rg --files knowledge")
    trace["events"].insert(1, _command_start("changed-command", "rg knowledge"))
    _persist_trace_mutation(paths, trace_path, trace, "row-0-0-1")

    with pytest.raises(attestor.AttestationError, match="no exact later successful"):
        _build(attestor, contract, paths, tmp_path)


@pytest.mark.parametrize(
    ("status", "exit_code"),
    [("failed", 1), ("declined", -1), ("completed", 1)],
)
def test_control_orphan_with_unsuccessful_exact_retry_is_rejected(
    attestor: ModuleType,
    tmp_path: Path,
    status: str,
    exit_code: int,
) -> None:
    contract, paths = _fixture(tmp_path, attestor)
    trace_path = tmp_path / "raw-traces/trace-0-0-1.json"
    trace = json.loads(trace_path.read_text(encoding="utf-8"))
    command = "rg --files knowledge"
    _set_fixture_control_retry(
        trace, command, status=status, exit_code=exit_code
    )
    trace["events"].insert(1, _command_start("failed-command", command))
    _persist_trace_mutation(paths, trace_path, trace, "row-0-0-1")

    with pytest.raises(attestor.AttestationError, match="no exact later successful"):
        _build(attestor, contract, paths, tmp_path)


def test_control_orphan_after_final_response_is_rejected(
    attestor: ModuleType, tmp_path: Path
) -> None:
    contract, paths = _fixture(tmp_path, attestor)
    trace_path = tmp_path / "raw-traces/trace-0-0-1.json"
    trace = json.loads(trace_path.read_text(encoding="utf-8"))
    command = "rg --files knowledge"
    retry = _tool_pair("post-response-retry", "command_execution")
    retry[0]["data"]["item"].update(
        {"command": command, "aggregated_output": "", "exit_code": None}
    )
    retry[1]["data"]["item"].update(
        {"command": command, "aggregated_output": "fixture", "exit_code": 0}
    )
    turn_index = next(
        index
        for index, event in enumerate(trace["events"])
        if event["type"] == "turn.completed"
    )
    trace["events"][turn_index:turn_index] = [
        _command_start("post-response-orphan", command),
        *retry,
    ]
    _persist_trace_mutation(paths, trace_path, trace, "row-0-0-1")

    with pytest.raises(attestor.AttestationError, match="after the final agent response"):
        _build(attestor, contract, paths, tmp_path)


def test_missing_live_traces_use_exact_profile_archives(
    attestor: ModuleType, tmp_path: Path
) -> None:
    contract, paths = _fixture(tmp_path, attestor)
    archives = _archived_fixture_workspaces(paths, tmp_path, remove_live=True)

    report = _build(
        attestor,
        contract,
        paths,
        tmp_path,
        archived_workspace_roots=archives,
    )

    assert report["aggregates"]["archived_trace_count"] == 90
    assert all(row["trace_archived"] is True for row in report["rows"])
    assert all(
        profile["archived_trace_count"] == 30
        for profile in report["aggregates"]["profiles"].values()
    )
    assert "trace-archives" not in json.dumps(report)
    assert "recovered 90 traces" in attestor.render_markdown(report)


def test_missing_live_trace_without_archive_roots_fails_closed(
    attestor: ModuleType, tmp_path: Path
) -> None:
    contract, paths = _fixture(tmp_path, attestor)
    _archived_fixture_workspaces(paths, tmp_path, remove_live=True)

    with pytest.raises(attestor.AttestationError, match="no archived workspace root"):
        _build(attestor, contract, paths, tmp_path)


@pytest.mark.parametrize("mutation", ["incomplete", "unknown"])
def test_archive_roots_require_exact_profile_coverage(
    attestor: ModuleType, tmp_path: Path, mutation: str
) -> None:
    contract, paths = _fixture(tmp_path, attestor)
    archives = _archived_fixture_workspaces(paths, tmp_path, remove_live=False)
    if mutation == "incomplete":
        archives.pop("adaptive-consult-control")
    else:
        archives["unknown-profile"] = tmp_path / "results/trace-archives/unknown/workspace"
        archives["unknown-profile"].mkdir(parents=True)

    with pytest.raises(attestor.AttestationError, match="exact benchmark profiles"):
        _build(
            attestor,
            contract,
            paths,
            tmp_path,
            archived_workspace_roots=archives,
        )


def test_archive_root_must_exist_even_when_profile_assignment_is_complete(
    attestor: ModuleType, tmp_path: Path
) -> None:
    contract, paths = _fixture(tmp_path, attestor)
    archives = _archived_fixture_workspaces(paths, tmp_path, remove_live=False)
    archives["knowledge-only-control"] = tmp_path / "results/missing/workspace"

    with pytest.raises(attestor.AttestationError, match="cannot resolve archived workspace root"):
        _build(
            attestor,
            contract,
            paths,
            tmp_path,
            archived_workspace_roots=archives,
        )


def test_archive_root_rejects_traversal(
    attestor: ModuleType, tmp_path: Path
) -> None:
    contract, paths = _fixture(tmp_path, attestor)
    archives = _archived_fixture_workspaces(paths, tmp_path, remove_live=False)
    archives["knowledge-only-control"] = Path(
        "results/trace-archives/knowledge-only-control/../knowledge-only-control/workspace"
    )

    with pytest.raises(attestor.AttestationError, match="contains traversal"):
        _build(
            attestor,
            contract,
            paths,
            tmp_path,
            archived_workspace_roots=archives,
        )


def test_archive_root_must_remain_inside_repository(
    attestor: ModuleType, tmp_path: Path
) -> None:
    repository = tmp_path / "repository"
    outside = tmp_path / "outside/workspace"
    outside.mkdir(parents=True)
    contract, paths = _fixture(repository, attestor)
    archives = _archived_fixture_workspaces(paths, repository, remove_live=False)
    archives["knowledge-only-control"] = outside

    with pytest.raises(attestor.AttestationError, match="inside the repository"):
        _build(
            attestor,
            contract,
            paths,
            repository,
            archived_workspace_roots=archives,
        )


def test_archive_root_rejects_directory_symlink(
    attestor: ModuleType, tmp_path: Path
) -> None:
    contract, paths = _fixture(tmp_path, attestor)
    archives = _archived_fixture_workspaces(paths, tmp_path, remove_live=False)
    profile = "knowledge-only-control"
    alias = tmp_path / "results/trace-archives/knowledge-alias"
    try:
        alias.symlink_to(archives[profile], target_is_directory=True)
    except OSError as exc:
        pytest.skip(f"directory symlinks are unavailable: {exc}")
    archives[profile] = alias

    with pytest.raises(attestor.AttestationError, match="link or junction"):
        _build(
            attestor,
            contract,
            paths,
            tmp_path,
            archived_workspace_roots=archives,
        )


def test_archive_candidate_rejects_file_symlink(
    attestor: ModuleType, tmp_path: Path
) -> None:
    contract, paths = _fixture(tmp_path, attestor)
    archives = _archived_fixture_workspaces(paths, tmp_path, remove_live=True)
    promptfoo = json.loads(paths["promptfoo"].read_text(encoding="utf-8"))
    first = promptfoo["results"]["results"][0]
    hook = first["response"]["metadata"]["executionEventHook"]
    candidate = archives[first["metadata"]["profileId"]].joinpath(
        *hook["relativePath"].split("/")
    )
    target = candidate.with_name("symlink-target.json")
    shutil.copyfile(candidate, target)
    candidate.unlink()
    try:
        candidate.symlink_to(target)
    except OSError as exc:
        pytest.skip(f"file symlinks are unavailable: {exc}")

    with pytest.raises(attestor.AttestationError, match="link or junction"):
        _build(
            attestor,
            contract,
            paths,
            tmp_path,
            archived_workspace_roots=archives,
        )


def test_archive_fallback_preserves_hook_absolute_relative_agreement(
    attestor: ModuleType, tmp_path: Path
) -> None:
    contract, paths = _fixture(tmp_path, attestor)
    archives = _archived_fixture_workspaces(paths, tmp_path, remove_live=True)
    promptfoo = json.loads(paths["promptfoo"].read_text(encoding="utf-8"))
    hook = promptfoo["results"]["results"][0]["response"]["metadata"][
        "executionEventHook"
    ]
    hook["path"] = str(tmp_path / "deleted-workspace/wrong-trace.json")
    _strict_dump(paths["promptfoo"], promptfoo)
    _refresh_answer_promptfoo_sha(paths)

    with pytest.raises(attestor.AttestationError, match="absolute and relative paths disagree"):
        _build(
            attestor,
            contract,
            paths,
            tmp_path,
            archived_workspace_roots=archives,
        )


def test_existing_hook_paths_take_precedence_over_supplied_archives(
    attestor: ModuleType, tmp_path: Path
) -> None:
    contract, paths = _fixture(tmp_path, attestor)
    archives = _archived_fixture_workspaces(paths, tmp_path, remove_live=False)
    archived_trace = next(archives["knowledge-only-control"].rglob("*.json"))
    archived_trace.write_text("not JSON\n", encoding="utf-8")

    report = _build(
        attestor,
        contract,
        paths,
        tmp_path,
        archived_workspace_roots=archives,
    )

    assert report["aggregates"]["archived_trace_count"] == 0
    assert all(row["trace_archived"] is False for row in report["rows"])


def test_archive_cli_specs_reject_duplicates_and_preserve_paths(
    attestor: ModuleType,
) -> None:
    parsed = attestor._parse_archived_workspace_specs(
        ["knowledge-only-control=results/knowledge/workspace"]
    )
    assert parsed == {
        "knowledge-only-control": Path("results/knowledge/workspace")
    }
    with pytest.raises(attestor.AttestationError, match="duplicate archived workspace"):
        attestor._parse_archived_workspace_specs(
            [
                "knowledge-only-control=results/one",
                "knowledge-only-control=results/two",
            ]
        )


@pytest.mark.parametrize(
    "mutation",
    [
        "schema",
        "server-version",
        "bootstrap-tool",
        "bootstrap-key-order",
        "bootstrap-digest",
        "bootstrap-byte-count",
        "bootstrap-replay-policy",
        "tool-sequence",
        "shell-disable-arguments",
        "shell-receipt-schema",
        "shell-receipt-key-order",
        "control-shell-policy",
        "consult-skill-digest",
        "duplicate-consult-skill",
    ],
)
def test_manifest_2_2_runtime_contract_is_cross_bound_to_skill_and_isolation(
    attestor: ModuleType, tmp_path: Path, mutation: str
) -> None:
    contract, paths = _fixture(tmp_path, attestor)
    manifest = json.loads(paths["manifest"].read_text(encoding="utf-8"))
    mcp = manifest["mcp_runtime"]
    publication = manifest["publication_runtime"]
    if mutation == "schema":
        manifest["schema_version"] = "semantic-okf-hard-answer-configs/2.1"
    elif mutation == "server-version":
        mcp["server_version"] = "1.4.0"
    elif mutation == "bootstrap-tool":
        mcp["bootstrap_tool"] = "semantic_okf_inspect"
    elif mutation == "bootstrap-key-order":
        mcp["bootstrap_key_order"] = list(reversed(mcp["bootstrap_key_order"]))
    elif mutation == "bootstrap-digest":
        mcp["bootstrap_skill_sha256"] = "0" * 64
    elif mutation == "bootstrap-byte-count":
        mcp["bootstrap_skill_byte_count"] += 1
    elif mutation == "bootstrap-replay-policy":
        mcp["bootstrap_failure_poison"] = False
    elif mutation == "tool-sequence":
        mcp["tools"] = mcp["tools"][1:]
    elif mutation == "shell-disable-arguments":
        publication["shell_disable_arguments"] = ["--disable", "web_search"]
    elif mutation == "shell-receipt-schema":
        publication["shell_isolation_receipt_schema"] = (
            "semantic-okf-shell-isolation-receipt/9.9"
        )
    elif mutation == "shell-receipt-key-order":
        publication["shell_isolation_receipt_key_order"] = list(
            reversed(publication["shell_isolation_receipt_key_order"])
        )
    elif mutation == "control-shell-policy":
        publication["controls_shell_policy_unchanged"] = False
    elif mutation == "consult-skill-digest":
        manifest["consult_skills"][0]["skill_md_sha256"] = "f" * 64
    else:
        manifest["consult_skills"].append(copy.deepcopy(manifest["consult_skills"][0]))
    _strict_dump(paths["manifest"], manifest)
    _refresh_manifest_binding(paths)

    with pytest.raises(attestor.AttestationError, match="manifest"):
        _build(attestor, contract, paths, tmp_path)


def test_bootstrap_is_first_canonical_and_binds_frozen_skill(
    attestor: ModuleType, tmp_path: Path
) -> None:
    contract, paths = _fixture(tmp_path, attestor)
    trace = json.loads(
        (tmp_path / "raw-traces/trace-2-0-1.json").read_text(encoding="utf-8")
    )
    started = next(
        event["data"]["item"]
        for event in trace["events"]
        if event["type"] == "item.started"
        and event["data"]["item"].get("id") == "bootstrap"
    )
    completed = next(
        event["data"]["item"]
        for event in trace["events"]
        if event["type"] == "item.completed"
        and event["data"]["item"].get("id") == "bootstrap"
    )
    payload_text = completed["result"]["content"][0]["text"]
    payload = json.loads(payload_text)
    skill_bytes = paths["treatment_skill"].read_bytes()

    assert started["arguments"] == {}
    assert list(payload) == [
        "schema",
        "skill_id",
        "skill_sha256",
        "byte_count",
        "skill_markdown",
    ]
    assert payload_text == json.dumps(
        payload, ensure_ascii=False, separators=(",", ":")
    )
    assert payload["schema"] == BOOTSTRAP_SCHEMA
    assert payload["skill_id"] == BOOTSTRAP_SKILL_ID
    assert payload["skill_sha256"] == hashlib.sha256(skill_bytes).hexdigest()
    assert payload["byte_count"] == len(skill_bytes)
    assert payload["skill_markdown"].encode("utf-8") == skill_bytes

    report = _build(attestor, contract, paths, tmp_path)
    row = next(
        item
        for item in report["rows"]
        if item["profile_id"] == "ensemble-consult-treatment"
    )
    assert row["ordered_tool_names"][:2] == [
        "semantic_okf_bootstrap_skill",
        "semantic_okf_inspect",
    ]
    assert row["bootstrap"] == {
        "schema": BOOTSTRAP_SCHEMA,
        "skill_id": BOOTSTRAP_SKILL_ID,
        "skill_sha256": hashlib.sha256(skill_bytes).hexdigest(),
        "byte_count": len(skill_bytes),
    }
    receipt_bytes = _shell_isolation_receipt().encode("utf-8")
    assert row["shell_isolation"] == {
        "schema": SHELL_ISOLATION_SCHEMA,
        "skill_id": BOOTSTRAP_SKILL_ID,
        "shell_tool_disabled": True,
        "receipt_sha256": hashlib.sha256(receipt_bytes).hexdigest(),
        "byte_count": len(receipt_bytes),
    }


@pytest.mark.parametrize("mutation", ["missing", "replay", "after-inspect", "failed"])
def test_bootstrap_must_be_one_successful_first_call(
    attestor: ModuleType, tmp_path: Path, mutation: str
) -> None:
    contract, paths = _fixture(tmp_path, attestor)
    trace_path = tmp_path / "raw-traces/trace-2-0-1.json"
    trace = json.loads(trace_path.read_text(encoding="utf-8"))
    bootstrap_events = [
        event
        for event in trace["events"]
        if isinstance(event["data"].get("item"), dict)
        and event["data"]["item"].get("id") == "bootstrap"
    ]
    assert len(bootstrap_events) == 2
    if mutation == "missing":
        trace["events"] = [event for event in trace["events"] if event not in bootstrap_events]
    elif mutation == "replay":
        replay = copy.deepcopy(bootstrap_events)
        for event in replay:
            event["data"]["item"]["id"] = "bootstrap-replay"
        inspect_end = next(
            index + 1
            for index, event in enumerate(trace["events"])
            if event["type"] == "item.completed"
            and event["data"]["item"].get("id") == "inspect"
        )
        trace["events"][inspect_end:inspect_end] = replay
    elif mutation == "after-inspect":
        trace["events"] = [event for event in trace["events"] if event not in bootstrap_events]
        inspect_end = next(
            index + 1
            for index, event in enumerate(trace["events"])
            if event["type"] == "item.completed"
            and event["data"]["item"].get("id") == "inspect"
        )
        trace["events"][inspect_end:inspect_end] = bootstrap_events
    else:
        for event in bootstrap_events:
            if event["type"] == "item.completed":
                event["data"]["item"]["result"] = _failed_result(
                    "fixture bootstrap poisoned the session"
                )
    _reindex_trace(trace)
    _strict_dump(trace_path, trace)
    _refresh_promptfoo_binding(paths, trace, "row-2-0-1")

    with pytest.raises(attestor.AttestationError, match="bootstrap|non-protocol"):
        _build(attestor, contract, paths, tmp_path)


def test_bootstrap_arguments_are_exactly_empty(
    attestor: ModuleType, tmp_path: Path
) -> None:
    contract, paths = _fixture(tmp_path, attestor)
    trace_path = tmp_path / "raw-traces/trace-2-0-1.json"
    trace = json.loads(trace_path.read_text(encoding="utf-8"))
    for event in trace["events"]:
        item = event["data"].get("item")
        if isinstance(item, dict) and item.get("id") == "bootstrap":
            item["arguments"] = {"path": "SKILL.md"}
    _reindex_trace(trace)
    _strict_dump(trace_path, trace)
    _refresh_promptfoo_binding(paths, trace, "row-2-0-1")

    with pytest.raises(attestor.AttestationError, match="bootstrap arguments"):
        _build(attestor, contract, paths, tmp_path)


@pytest.mark.parametrize(
    "mutation",
    [
        "field-order",
        "schema",
        "skill-id",
        "digest",
        "byte-count",
        "markdown",
        "extra-key",
        "noncanonical",
    ],
)
def test_bootstrap_response_fails_closed_on_contract_drift(
    attestor: ModuleType, tmp_path: Path, mutation: str
) -> None:
    contract, paths = _fixture(tmp_path, attestor)
    trace_path = tmp_path / "raw-traces/trace-2-0-1.json"
    trace = json.loads(trace_path.read_text(encoding="utf-8"))
    completed = next(
        event["data"]["item"]
        for event in trace["events"]
        if event["type"] == "item.completed"
        and event["data"]["item"].get("id") == "bootstrap"
    )
    payload = json.loads(completed["result"]["content"][0]["text"])
    if mutation == "field-order":
        payload = {
            "skill_id": payload["skill_id"],
            "schema": payload["schema"],
            "skill_sha256": payload["skill_sha256"],
            "byte_count": payload["byte_count"],
            "skill_markdown": payload["skill_markdown"],
        }
    elif mutation == "schema":
        payload["schema"] = "semantic-okf-skill-bootstrap/9.9"
    elif mutation == "skill-id":
        payload["skill_id"] = "consult-semantic-okf-adaptive"
    elif mutation == "digest":
        payload["skill_sha256"] = "0" * 64
    elif mutation == "byte-count":
        payload["byte_count"] += 1
    elif mutation == "markdown":
        payload["skill_markdown"] += "\ncorruption"
    elif mutation == "extra-key":
        payload["status"] = "ready"
    text = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    if mutation == "noncanonical":
        text = json.dumps(payload, ensure_ascii=False, indent=2)
    completed["result"] = _result(text)
    _reindex_trace(trace)
    _strict_dump(trace_path, trace)

    with pytest.raises(
        attestor.AttestationError,
        match="bootstrap response|frozen skill bytes",
    ):
        _build(attestor, contract, paths, tmp_path)


@pytest.mark.parametrize(
    "mutation",
    [
        "missing-response",
        "missing-trace",
        "mismatch",
        "wrong-value",
        "duplicate",
        "unstripped-response",
    ],
)
def test_treatment_shell_isolation_receipt_is_exact_and_cross_bound(
    attestor: ModuleType, tmp_path: Path, mutation: str
) -> None:
    contract, paths = _fixture(tmp_path, attestor)
    trace_path = tmp_path / "raw-traces/trace-2-0-1.json"
    trace = json.loads(trace_path.read_text(encoding="utf-8"))
    promptfoo = json.loads(paths["promptfoo"].read_text(encoding="utf-8"))
    row = next(
        item for item in promptfoo["results"]["results"] if item["id"] == "row-2-0-1"
    )
    receipt = _shell_isolation_receipt()
    wrong = json.dumps(
        {
            "schema": SHELL_ISOLATION_SCHEMA,
            "skill_id": BOOTSTRAP_SKILL_ID,
            "shell_tool_disabled": False,
        },
        separators=(",", ":"),
    ) + "\n"
    if mutation == "missing-response":
        row["response"]["metadata"]["stderr"] = None
    elif mutation == "missing-trace":
        trace["stderr"] = None
    elif mutation == "mismatch":
        row["response"]["metadata"]["stderr"] = wrong
    elif mutation == "wrong-value":
        trace["stderr"] = wrong
        row["response"]["metadata"]["stderr"] = wrong
    elif mutation == "unstripped-response":
        row["response"]["metadata"]["stderr"] = receipt
    else:
        trace["stderr"] = receipt + receipt
        row["response"]["metadata"]["stderr"] = receipt + receipt
    _strict_dump(trace_path, trace)
    _strict_dump(paths["promptfoo"], promptfoo)
    _refresh_promptfoo_binding(paths, trace, "row-2-0-1")

    with pytest.raises(attestor.AttestationError, match="shell-isolation receipt"):
        _build(attestor, contract, paths, tmp_path)


def test_controls_must_not_emit_treatment_shell_isolation_receipt(
    attestor: ModuleType, tmp_path: Path
) -> None:
    contract, paths = _fixture(tmp_path, attestor)
    trace_path = tmp_path / "raw-traces/trace-0-0-1.json"
    trace = json.loads(trace_path.read_text(encoding="utf-8"))
    trace["stderr"] = _shell_isolation_receipt()
    _strict_dump(trace_path, trace)
    promptfoo = json.loads(paths["promptfoo"].read_text(encoding="utf-8"))
    row = next(
        item for item in promptfoo["results"]["results"] if item["id"] == "row-0-0-1"
    )
    row["response"]["metadata"]["stderr"] = _shell_isolation_receipt()
    _strict_dump(paths["promptfoo"], promptfoo)
    _refresh_promptfoo_binding(paths, trace, "row-0-0-1")

    with pytest.raises(attestor.AttestationError, match="control contains"):
        _build(attestor, contract, paths, tmp_path)


def test_control_diagnostic_stderr_is_allowed_only_when_cross_bound(
    attestor: ModuleType, tmp_path: Path
) -> None:
    contract, paths = _fixture(tmp_path, attestor)
    trace_path = tmp_path / "raw-traces/trace-0-0-1.json"
    trace = json.loads(trace_path.read_text(encoding="utf-8"))
    diagnostic = "ERROR tool request rejected: blocked by policy\n\n"
    trace["stderr"] = diagnostic
    _strict_dump(trace_path, trace)
    promptfoo = json.loads(paths["promptfoo"].read_text(encoding="utf-8"))
    row = next(
        item for item in promptfoo["results"]["results"] if item["id"] == "row-0-0-1"
    )
    row["response"]["metadata"]["stderr"] = diagnostic.rstrip("\n")
    _strict_dump(paths["promptfoo"], promptfoo)
    _refresh_promptfoo_binding(paths, trace, "row-0-0-1")

    report = _build(attestor, contract, paths, tmp_path)
    assert report["aggregates"]["profiles"]["knowledge-only-control"][
        "shell_isolated_answers"
    ] == 0

    promptfoo = json.loads(paths["promptfoo"].read_text(encoding="utf-8"))
    row = next(
        item for item in promptfoo["results"]["results"] if item["id"] == "row-0-0-1"
    )
    row["response"]["metadata"]["stderr"] = "different diagnostic\n"
    _strict_dump(paths["promptfoo"], promptfoo)
    _refresh_answer_promptfoo_sha(paths)
    with pytest.raises(attestor.AttestationError, match="stderr metadata and trace disagree"):
        _build(attestor, contract, paths, tmp_path)


def test_treatment_raw_mutation_is_corrected_to_confirmed_publication(
    attestor: ModuleType, tmp_path: Path
) -> None:
    contract, paths = _fixture(tmp_path, attestor)
    trace_path = tmp_path / "raw-traces/trace-2-0-1.json"

    def mutate(trace: dict[str, Any]) -> None:
        for event in trace["events"]:
            item = event["data"].get("item")
            if isinstance(item, dict) and item.get("type") == "agent_message":
                item["text"] = item["text"].replace(
                    "q031-fixture", "q031-mutated-by-agent"
                )

    _rewrite_trace(trace_path, mutate)
    report = _build(attestor, contract, paths, tmp_path)
    row = next(
        item
        for item in report["rows"]
        if item["profile_id"] == "ensemble-consult-treatment"
        and item["question_id"] == "q031-fixture"
        and item["repetition"] == 1
    )

    assert row["publication_corrected"] is True
    assert row["raw_output_sha256"] != row["output_sha256"]
    assert row["output_sha256"] == row["confirmation_sha256"]
    assert report["aggregates"]["publication_correction_count"] == 1
    assert report["aggregates"]["profiles"]["ensemble-consult-treatment"][
        "publication_corrections"
    ] == 1


def test_unneeded_treatment_publication_is_recorded_without_correction(
    attestor: ModuleType, tmp_path: Path
) -> None:
    contract, paths = _fixture(tmp_path, attestor)
    report = _build(attestor, contract, paths, tmp_path)
    row = next(
        item
        for item in report["rows"]
        if item["profile_id"] == "ensemble-consult-treatment"
    )

    assert row["publication_corrected"] is False
    assert row["raw_output_sha256"] == row["output_sha256"]
    assert row["raw_output_byte_count"] == row["output_byte_count"]


def test_wrong_trace_command_is_rejected(
    attestor: ModuleType, tmp_path: Path
) -> None:
    contract, paths = _fixture(tmp_path, attestor)
    trace_path = tmp_path / "raw-traces/trace-2-0-1.json"
    _rewrite_trace(trace_path, lambda trace: trace.__setitem__("command", "codex"))

    with pytest.raises(attestor.AttestationError, match="publication wrapper"):
        _build(attestor, contract, paths, tmp_path)


def test_control_promptfoo_output_must_equal_final_raw_agent_message(
    attestor: ModuleType, tmp_path: Path
) -> None:
    contract, paths = _fixture(tmp_path, attestor)
    trace_path = tmp_path / "raw-traces/trace-0-0-1.json"

    def mutate(trace: dict[str, Any]) -> None:
        for event in trace["events"]:
            item = event["data"].get("item")
            if isinstance(item, dict) and item.get("type") == "agent_message":
                item["text"] = item["text"].replace(
                    "q031-fixture", "q031-control-mutated"
                )

    _rewrite_trace(trace_path, mutate)
    with pytest.raises(attestor.AttestationError, match="control Promptfoo output differs"):
        _build(attestor, contract, paths, tmp_path)


def test_missing_publication_runtime_binding_is_rejected(
    attestor: ModuleType, tmp_path: Path
) -> None:
    contract, paths = _fixture(tmp_path, attestor)
    paths["publication_script"].unlink()

    with pytest.raises((attestor.AttestationError, FileNotFoundError)):
        _build(attestor, contract, paths, tmp_path)


def test_successful_prepare_revision_before_final_prepare_is_accepted(
    attestor: ModuleType, tmp_path: Path
) -> None:
    contract, paths = _fixture(tmp_path, attestor)
    trace_path = tmp_path / "raw-traces/trace-2-0-1.json"
    trace = json.loads(trace_path.read_text(encoding="utf-8"))
    prepare_index = next(
        index
        for index, event in enumerate(trace["events"])
        if event["type"] == "item.started"
        and event["data"]["item"].get("id") == "prepare"
    )
    earlier_candidate = json.dumps(
        {
            "question_id": "q031-fixture",
            "answer": "superseded draft revision",
            "evidence": [],
        },
        separators=(",", ":"),
    )
    trace["events"][prepare_index:prepare_index] = _tool_pair(
        "prepare-revision",
        "mcp_tool_call",
        server="semantic_okf",
        tool="semantic_okf_prepare_answer",
        arguments={
            "question_id": "q031-fixture",
            "query": "fixture query 2-0-1",
            "draft": {"summary": "superseded fixture", "facets": []},
            "top_k": 30,
            "per_facet": 12,
            "maximum_facets": 12,
            "page_size": 48,
        },
        result=_result(_prepared_envelope(earlier_candidate)),
    )
    _reindex_trace(trace)
    _strict_dump(trace_path, trace)
    _refresh_promptfoo_binding(paths, trace, "row-2-0-1")

    report = _build(attestor, contract, paths, tmp_path)

    row = next(
        item
        for item in report["rows"]
        if item["profile_id"] == "ensemble-consult-treatment"
        and item["question_id"] == "q031-fixture"
        and item["repetition"] == 1
    )
    assert row["ordered_tool_names"].count("semantic_okf_prepare_answer") == 2
    assert row["ordered_tool_names"].count("semantic_okf_confirm_answer") == 1
    assert row["confirmation_sha256"] == row["output_sha256"]


def test_failed_confirm_recovered_by_fresh_prepare_is_attested(
    attestor: ModuleType, tmp_path: Path
) -> None:
    contract, paths = _fixture(tmp_path, attestor)
    trace_path = tmp_path / "raw-traces/trace-2-0-1.json"
    trace = json.loads(trace_path.read_text(encoding="utf-8"))
    terminal_confirm_index = next(
        index
        for index, event in enumerate(trace["events"])
        if event["type"] == "item.started"
        and event["data"]["item"].get("id") == "confirm"
    )
    prepared_digest = trace["events"][terminal_confirm_index]["data"]["item"][
        "arguments"
    ]["response_sha256"]
    mismatched_digest = "0" * 64
    assert mismatched_digest != prepared_digest
    failed_confirm = _tool_pair(
        "failed-confirm-recovered",
        "mcp_tool_call",
        server="semantic_okf",
        tool="semantic_okf_confirm_answer",
        arguments={"response_sha256": mismatched_digest},
        result=_failed_result(
            "response_sha256 does not match the outstanding prepared response"
        ),
    )
    recovery_prepare = _cloned_call_events(
        trace, "prepare", "fresh-prepare-after-failed-confirm"
    )
    trace["events"][terminal_confirm_index:terminal_confirm_index] = [
        *failed_confirm,
        *recovery_prepare,
    ]
    _reindex_trace(trace)
    _strict_dump(trace_path, trace)
    _refresh_promptfoo_binding(paths, trace, "row-2-0-1")

    report = _build(attestor, contract, paths, tmp_path)
    row = next(
        item
        for item in report["rows"]
        if item["profile_id"] == "ensemble-consult-treatment"
        and item["question_id"] == "q031-fixture"
        and item["repetition"] == 1
    )
    treatment = report["aggregates"]["profiles"]["ensemble-consult-treatment"]

    assert row["recovered_protocol_failure_count"] == 1
    assert row["tool_counts"]["failed_mcp_calls"] == 1
    assert row["ordered_tool_names"][-4:] == [
        "semantic_okf_prepare_answer",
        "semantic_okf_confirm_answer",
        "semantic_okf_prepare_answer",
        "semantic_okf_confirm_answer",
    ]
    assert row["protocol_call_outcomes"] == [
        {"tool": "semantic_okf_prepare_answer", "status": "success"},
        {"tool": "semantic_okf_confirm_answer", "status": "failed"},
        {"tool": "semantic_okf_prepare_answer", "status": "success"},
        {"tool": "semantic_okf_confirm_answer", "status": "success"},
    ]
    assert treatment["recovered_protocol_failures"] == 1
    assert treatment["answers_with_protocol_recovery"] == 1
    assert report["aggregates"]["recovered_protocol_failure_count"] == 1
    assert report["aggregates"]["protocol_recovery_answer_count"] == 1
    for profile in ("knowledge-only-control", "adaptive-consult-control"):
        assert report["aggregates"]["profiles"][profile][
            "recovered_protocol_failures"
        ] == 0
        assert report["aggregates"]["profiles"][profile][
            "answers_with_protocol_recovery"
        ] == 0


def test_failed_confirm_without_fresh_prepare_is_rejected(
    attestor: ModuleType, tmp_path: Path
) -> None:
    contract, paths = _fixture(tmp_path, attestor)
    trace_path = tmp_path / "raw-traces/trace-2-0-1.json"
    trace = json.loads(trace_path.read_text(encoding="utf-8"))
    terminal_confirm_index = next(
        index
        for index, event in enumerate(trace["events"])
        if event["type"] == "item.started"
        and event["data"]["item"].get("id") == "confirm"
    )
    prepared_digest = trace["events"][terminal_confirm_index]["data"]["item"][
        "arguments"
    ]["response_sha256"]
    trace["events"][terminal_confirm_index:terminal_confirm_index] = _tool_pair(
        "failed-confirm-without-reprepare",
        "mcp_tool_call",
        server="semantic_okf",
        tool="semantic_okf_confirm_answer",
        arguments={"response_sha256": prepared_digest},
        result=_failed_result("fixture failed confirmation"),
    )
    _reindex_trace(trace)
    _strict_dump(trace_path, trace)
    _refresh_promptfoo_binding(paths, trace, "row-2-0-1")

    with pytest.raises(attestor.AttestationError, match="prepare|recover|confirm"):
        _build(attestor, contract, paths, tmp_path)


def test_failed_prepare_recovered_by_fresh_prepare_is_attested(
    attestor: ModuleType, tmp_path: Path
) -> None:
    contract, paths = _fixture(tmp_path, attestor)
    trace_path = tmp_path / "raw-traces/trace-2-0-1.json"
    trace = json.loads(trace_path.read_text(encoding="utf-8"))
    recovery_prepare = _cloned_call_events(
        trace, "prepare", "fresh-prepare-after-failed-prepare"
    )
    for event in trace["events"]:
        item = event["data"].get("item")
        if (
            event["type"] == "item.completed"
            and isinstance(item, dict)
            and item.get("id") == "prepare"
        ):
            item["result"] = _failed_result("fixture failed preparation")
    terminal_confirm_index = next(
        index
        for index, event in enumerate(trace["events"])
        if event["type"] == "item.started"
        and event["data"]["item"].get("id") == "confirm"
    )
    trace["events"][terminal_confirm_index:terminal_confirm_index] = recovery_prepare
    _reindex_trace(trace)
    _strict_dump(trace_path, trace)
    _refresh_promptfoo_binding(paths, trace, "row-2-0-1")

    report = _build(attestor, contract, paths, tmp_path)
    row = next(
        item
        for item in report["rows"]
        if item["profile_id"] == "ensemble-consult-treatment"
        and item["question_id"] == "q031-fixture"
        and item["repetition"] == 1
    )

    assert row["protocol_call_outcomes"] == [
        {"tool": "semantic_okf_prepare_answer", "status": "failed"},
        {"tool": "semantic_okf_prepare_answer", "status": "success"},
        {"tool": "semantic_okf_confirm_answer", "status": "success"},
    ]
    assert row["recovered_protocol_failure_count"] == 1
    assert row["tool_counts"]["failed_mcp_calls"] == 1
    assert report["aggregates"]["recovered_protocol_failure_count"] == 1
    assert report["aggregates"]["protocol_recovery_answer_count"] == 1


def test_failed_prepare_without_fresh_prepare_is_rejected(
    attestor: ModuleType, tmp_path: Path
) -> None:
    contract, paths = _fixture(tmp_path, attestor)
    trace_path = tmp_path / "raw-traces/trace-2-0-1.json"
    trace = json.loads(trace_path.read_text(encoding="utf-8"))
    for event in trace["events"]:
        item = event["data"].get("item")
        if (
            event["type"] == "item.completed"
            and isinstance(item, dict)
            and item.get("id") == "prepare"
        ):
            item["result"] = _failed_result("fixture failed preparation")
    _reindex_trace(trace)
    _strict_dump(trace_path, trace)
    _refresh_promptfoo_binding(paths, trace, "row-2-0-1")

    with pytest.raises(attestor.AttestationError, match="prepare|recover|confirm"):
        _build(attestor, contract, paths, tmp_path)


def test_confirm_before_final_prepare_is_rejected(
    attestor: ModuleType, tmp_path: Path
) -> None:
    contract, paths = _fixture(tmp_path, attestor)
    trace_path = tmp_path / "raw-traces/trace-2-0-1.json"
    trace = json.loads(trace_path.read_text(encoding="utf-8"))
    confirm_events = [
        event
        for event in trace["events"]
        if isinstance(event["data"].get("item"), dict)
        and event["data"]["item"].get("id") == "confirm"
    ]
    trace["events"] = [
        event
        for event in trace["events"]
        if not (
            isinstance(event["data"].get("item"), dict)
            and event["data"]["item"].get("id") == "confirm"
        )
    ]
    prepare_index = next(
        index
        for index, event in enumerate(trace["events"])
        if event["type"] == "item.started"
        and event["data"]["item"].get("id") == "prepare"
    )
    trace["events"][prepare_index:prepare_index] = confirm_events
    _reindex_trace(trace)
    _strict_dump(trace_path, trace)
    _refresh_promptfoo_binding(paths, trace, "row-2-0-1")

    with pytest.raises(attestor.AttestationError, match="confirm"):
        _build(attestor, contract, paths, tmp_path)


def test_earlier_successful_confirm_cannot_be_recovered(
    attestor: ModuleType, tmp_path: Path
) -> None:
    contract, paths = _fixture(tmp_path, attestor)
    trace_path = tmp_path / "raw-traces/trace-2-0-1.json"
    trace = json.loads(trace_path.read_text(encoding="utf-8"))
    terminal_confirm_index = next(
        index
        for index, event in enumerate(trace["events"])
        if event["type"] == "item.started"
        and event["data"]["item"].get("id") == "confirm"
    )
    earlier_confirm = _cloned_call_events(
        trace, "confirm", "earlier-successful-confirm"
    )
    later_prepare = _cloned_call_events(
        trace, "prepare", "prepare-after-successful-confirm"
    )
    trace["events"][terminal_confirm_index:terminal_confirm_index] = [
        *earlier_confirm,
        *later_prepare,
    ]
    _reindex_trace(trace)
    _strict_dump(trace_path, trace)
    _refresh_promptfoo_binding(paths, trace, "row-2-0-1")

    with pytest.raises(attestor.AttestationError, match="confirm"):
        _build(attestor, contract, paths, tmp_path)


def test_prepare_and_confirm_arguments_use_split_protocol_without_modes(
    attestor: ModuleType, tmp_path: Path
) -> None:
    contract, paths = _fixture(tmp_path, attestor)
    trace = json.loads(
        (tmp_path / "raw-traces/trace-2-0-1.json").read_text(encoding="utf-8")
    )
    started = {
        event["data"]["item"]["id"]: event["data"]["item"]
        for event in trace["events"]
        if event["type"] == "item.started"
        and isinstance(event["data"].get("item"), dict)
        and event["data"]["item"].get("type") == "mcp_tool_call"
    }

    assert started["prepare"]["tool"] == "semantic_okf_prepare_answer"
    assert "mode" not in started["prepare"]["arguments"]
    assert started["confirm"]["tool"] == "semantic_okf_confirm_answer"
    assert set(started["confirm"]["arguments"]) == {"response_sha256"}
    completed_prepare = next(
        event["data"]["item"]
        for event in trace["events"]
        if event["type"] == "item.completed"
        and event["data"]["item"].get("id") == "prepare"
    )
    envelope_text = completed_prepare["result"]["content"][0]["text"]
    envelope = json.loads(envelope_text)
    assert list(envelope) == [
        "schema",
        "candidate_json",
        "response_sha256",
        "byte_count",
    ]
    candidate_bytes = envelope["candidate_json"].encode("utf-8")
    assert envelope["schema"] == PREPARED_ANSWER_SCHEMA
    assert envelope["response_sha256"] == hashlib.sha256(candidate_bytes).hexdigest()
    assert envelope["byte_count"] == len(candidate_bytes)
    assert started["confirm"]["arguments"]["response_sha256"] == envelope[
        "response_sha256"
    ]
    assert _build(attestor, contract, paths, tmp_path)["status"] == "pass"


def test_prepared_envelope_with_corrupted_field_order_is_rejected(
    attestor: ModuleType, tmp_path: Path
) -> None:
    contract, paths = _fixture(tmp_path, attestor)
    trace_path = tmp_path / "raw-traces/trace-2-0-1.json"
    trace = json.loads(trace_path.read_text(encoding="utf-8"))
    for event in trace["events"]:
        item = event["data"].get("item")
        if (
            event["type"] == "item.completed"
            and isinstance(item, dict)
            and item.get("id") == "prepare"
        ):
            envelope = json.loads(item["result"]["content"][0]["text"])
            reordered = {
                "candidate_json": envelope["candidate_json"],
                "schema": envelope["schema"],
                "response_sha256": envelope["response_sha256"],
                "byte_count": envelope["byte_count"],
            }
            item["result"] = _result(
                json.dumps(reordered, ensure_ascii=False, separators=(",", ":"))
            )
    _reindex_trace(trace)
    _strict_dump(trace_path, trace)
    _refresh_promptfoo_binding(paths, trace, "row-2-0-1")

    with pytest.raises(attestor.AttestationError, match="envelope.*field order"):
        _build(attestor, contract, paths, tmp_path)


def test_prepared_envelope_digest_mismatch_is_rejected(
    attestor: ModuleType, tmp_path: Path
) -> None:
    contract, paths = _fixture(tmp_path, attestor)
    trace_path = tmp_path / "raw-traces/trace-2-0-1.json"
    trace = json.loads(trace_path.read_text(encoding="utf-8"))
    for event in trace["events"]:
        item = event["data"].get("item")
        if (
            event["type"] == "item.completed"
            and isinstance(item, dict)
            and item.get("id") == "prepare"
        ):
            envelope = json.loads(item["result"]["content"][0]["text"])
            envelope["response_sha256"] = "0" * 64
            item["result"] = _result(
                json.dumps(envelope, ensure_ascii=False, separators=(",", ":"))
            )
    _reindex_trace(trace)
    _strict_dump(trace_path, trace)
    _refresh_promptfoo_binding(paths, trace, "row-2-0-1")

    with pytest.raises(attestor.AttestationError, match="envelope digest"):
        _build(attestor, contract, paths, tmp_path)


def test_confirm_digest_mismatch_is_rejected(
    attestor: ModuleType, tmp_path: Path
) -> None:
    contract, paths = _fixture(tmp_path, attestor)
    trace_path = tmp_path / "raw-traces/trace-2-0-1.json"
    trace = json.loads(trace_path.read_text(encoding="utf-8"))
    for event in trace["events"]:
        item = event["data"].get("item")
        if isinstance(item, dict) and item.get("id") == "confirm":
            item["arguments"]["response_sha256"] = "0" * 64
    _reindex_trace(trace)
    _strict_dump(trace_path, trace)
    _refresh_promptfoo_binding(paths, trace, "row-2-0-1")

    with pytest.raises(attestor.AttestationError, match="confirm digest differs"):
        _build(attestor, contract, paths, tmp_path)


def test_stale_digest_after_failed_call_and_fresh_prepare_is_rejected(
    attestor: ModuleType, tmp_path: Path
) -> None:
    contract, paths = _fixture(tmp_path, attestor)
    trace_path = tmp_path / "raw-traces/trace-2-0-1.json"
    trace = json.loads(trace_path.read_text(encoding="utf-8"))
    terminal_confirm_index = next(
        index
        for index, event in enumerate(trace["events"])
        if event["type"] == "item.started"
        and event["data"]["item"].get("id") == "confirm"
    )
    failed_confirm = _tool_pair(
        "failed-confirm-before-new-digest",
        "mcp_tool_call",
        server="semantic_okf",
        tool="semantic_okf_confirm_answer",
        arguments={"response_sha256": "0" * 64},
        result=_failed_result("fixture failed digest confirmation"),
    )
    recovery_prepare = _cloned_call_events(
        trace, "prepare", "fresh-prepare-with-new-digest"
    )
    revised_candidate = json.dumps(
        {
            "question_id": "q031-fixture",
            "answer": "fresh response after failed confirmation",
            "evidence": [],
        },
        separators=(",", ":"),
    )
    for event in recovery_prepare:
        if event["type"] == "item.completed":
            event["data"]["item"]["result"] = _result(
                _prepared_envelope(revised_candidate)
            )
    trace["events"][terminal_confirm_index:terminal_confirm_index] = [
        *failed_confirm,
        *recovery_prepare,
    ]
    _reindex_trace(trace)
    _strict_dump(trace_path, trace)
    _refresh_promptfoo_binding(paths, trace, "row-2-0-1")

    with pytest.raises(attestor.AttestationError, match="confirm digest differs"):
        _build(attestor, contract, paths, tmp_path)


def test_confirmation_receipt_mismatch_is_rejected(
    attestor: ModuleType, tmp_path: Path
) -> None:
    contract, paths = _fixture(tmp_path, attestor)
    trace_path = tmp_path / "raw-traces/trace-2-0-1.json"
    trace = json.loads(trace_path.read_text(encoding="utf-8"))
    for event in trace["events"]:
        item = event["data"].get("item")
        if (
            event["type"] == "item.completed"
            and isinstance(item, dict)
            and item.get("id") == "confirm"
        ):
            receipt = json.loads(item["result"]["content"][0]["text"])
            receipt["byte_count"] += 1
            item["result"] = _result(
                json.dumps(receipt, ensure_ascii=False, separators=(",", ":"))
            )
    _reindex_trace(trace)
    _strict_dump(trace_path, trace)
    _refresh_promptfoo_binding(paths, trace, "row-2-0-1")

    with pytest.raises(attestor.AttestationError, match="receipt does not bind"):
        _build(attestor, contract, paths, tmp_path)


def test_legacy_confirm_candidate_argument_is_rejected(
    attestor: ModuleType, tmp_path: Path
) -> None:
    contract, paths = _fixture(tmp_path, attestor)
    trace_path = tmp_path / "raw-traces/trace-2-0-1.json"
    trace = json.loads(trace_path.read_text(encoding="utf-8"))
    candidate_json = ""
    for event in trace["events"]:
        item = event["data"].get("item")
        if (
            event["type"] == "item.completed"
            and isinstance(item, dict)
            and item.get("id") == "prepare"
        ):
            envelope = json.loads(item["result"]["content"][0]["text"])
            candidate_json = envelope["candidate_json"]
    assert candidate_json
    for event in trace["events"]:
        item = event["data"].get("item")
        if isinstance(item, dict) and item.get("id") == "confirm":
            item["arguments"] = {"candidate_json": candidate_json}
    _reindex_trace(trace)
    _strict_dump(trace_path, trace)
    _refresh_promptfoo_binding(paths, trace, "row-2-0-1")

    with pytest.raises(attestor.AttestationError, match="confirm arguments"):
        _build(attestor, contract, paths, tmp_path)


def test_legacy_prepare_mode_argument_is_rejected(
    attestor: ModuleType, tmp_path: Path
) -> None:
    contract, paths = _fixture(tmp_path, attestor)
    trace_path = tmp_path / "raw-traces/trace-2-0-1.json"
    trace = json.loads(trace_path.read_text(encoding="utf-8"))
    for event in trace["events"]:
        item = event["data"].get("item")
        if isinstance(item, dict) and item.get("id") == "prepare":
            item["arguments"]["mode"] = "prepare"
    _reindex_trace(trace)
    _strict_dump(trace_path, trace)
    _refresh_promptfoo_binding(paths, trace, "row-2-0-1")

    with pytest.raises(attestor.AttestationError, match="mode|prepare.*arguments"):
        _build(attestor, contract, paths, tmp_path)


@pytest.mark.parametrize(
    ("source_call_id", "suffix"),
    [
        ("bootstrap", "bootstrap"),
        ("inspect", "inspect"),
        ("coverage-2", "coverage"),
        ("prepare", "prepare"),
        ("confirm", "confirm"),
    ],
)
@pytest.mark.parametrize("failed", [False, True], ids=["successful", "failed"])
def test_confirm_is_terminal_for_every_semantic_tool(
    attestor: ModuleType,
    tmp_path: Path,
    source_call_id: str,
    suffix: str,
    failed: bool,
) -> None:
    contract, paths = _fixture(tmp_path, attestor)
    trace_path = tmp_path / "raw-traces/trace-2-0-1.json"
    trace = json.loads(trace_path.read_text(encoding="utf-8"))
    post_confirm_events = [
        copy.deepcopy(event)
        for event in trace["events"]
        if isinstance(event["data"].get("item"), dict)
        and event["data"]["item"].get("id") == source_call_id
    ]
    assert len(post_confirm_events) == 2
    for event in post_confirm_events:
        event["data"]["item"]["id"] = f"post-confirm-{suffix}"
        if failed and event["type"] == "item.completed":
            event["data"]["item"]["result"] = _failed_result(
                "fixture post-confirm failure"
            )
    insertion_index = next(
        index + 1
        for index, event in enumerate(trace["events"])
        if event["type"] == "item.completed"
        and isinstance(event["data"].get("item"), dict)
        and event["data"]["item"].get("id") == "confirm"
    )
    trace["events"][insertion_index:insertion_index] = post_confirm_events
    _reindex_trace(trace)
    _strict_dump(trace_path, trace)
    _refresh_promptfoo_binding(paths, trace, "row-2-0-1")

    with pytest.raises(attestor.AttestationError):
        _build(attestor, contract, paths, tmp_path)


@pytest.mark.parametrize(
    ("field", "changed_value"),
    [
        ("priority_order", "fixture-priority-order-drift-v2"),
        (
            "priority_order_sha256",
            hashlib.sha256(
                json.dumps(
                    ["claim-1", "claim-X"],
                    sort_keys=True,
                    ensure_ascii=False,
                    separators=(",", ":"),
                ).encode("utf-8")
            ).hexdigest(),
        ),
    ],
)
def test_coverage_pages_with_changed_priority_binding_are_rejected(
    attestor: ModuleType,
    tmp_path: Path,
    field: str,
    changed_value: str,
) -> None:
    contract, paths = _fixture(tmp_path, attestor)
    trace_path = tmp_path / "raw-traces/trace-2-0-1.json"
    trace = json.loads(trace_path.read_text(encoding="utf-8"))
    for event in trace["events"]:
        item = event["data"].get("item")
        if (
            event["type"] == "item.completed"
            and isinstance(item, dict)
            and item.get("id") == "coverage-2"
        ):
            payload = json.loads(item["result"]["content"][0]["text"])
            payload["full_coverage"][field] = changed_value
            item["result"] = _result(payload)
    _reindex_trace(trace)
    _strict_dump(trace_path, trace)
    _refresh_promptfoo_binding(paths, trace, "row-2-0-1")

    with pytest.raises(attestor.AttestationError, match="coverage.*(?:bind|pack)"):
        _build(attestor, contract, paths, tmp_path)


def test_control_semantic_okf_call_is_rejected(attestor: ModuleType, tmp_path: Path) -> None:
    contract, paths = _fixture(tmp_path, attestor)
    trace_path = tmp_path / "raw-traces/trace-0-0-1.json"

    def mutate(trace: dict[str, Any]) -> None:
        for collection in (trace["events"], trace["toolEvents"]):
            for event in collection:
                item = event["data"].get("item")
                if isinstance(item, dict) and item.get("id") == "command":
                    item.update(
                        {
                            "type": "mcp_tool_call",
                            "server": "semantic_okf",
                            "tool": "semantic_okf_inspect",
                            "arguments": {},
                        }
                    )
                    if event["type"] == "item.completed":
                        item["result"] = _result({"status": "pass"})

    _rewrite_trace(trace_path, mutate)
    with pytest.raises(attestor.AttestationError, match="control trace invoked"):
        _build(attestor, contract, paths, tmp_path)


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        ("remove-confirm", "confirm"),
        ("shell", "shell or command"),
        ("coverage-drift", "different query parameters"),
        ("failed-mcp", "failed non-.*MCP call"),
        ("failed-inspect", "failed non-.*MCP call"),
    ],
)
def test_treatment_trace_gates_fail_closed(
    attestor: ModuleType,
    tmp_path: Path,
    mutation: str,
    message: str,
) -> None:
    contract, paths = _fixture(tmp_path, attestor)
    trace_path = tmp_path / "raw-traces/trace-2-0-1.json"

    def mutate(trace: dict[str, Any]) -> None:
        if mutation == "remove-confirm":
            remove = {
                event["data"]["item"]["id"]
                for event in trace["events"]
                if isinstance(event["data"].get("item"), dict)
                and event["data"]["item"].get("id") == "confirm"
            }
            trace["events"] = [
                event
                for event in trace["events"]
                if not (
                    isinstance(event["data"].get("item"), dict)
                    and event["data"]["item"].get("id") in remove
                )
            ]
            for index, event in enumerate(trace["events"]):
                event["index"] = index
            trace["toolEvents"] = [
                copy.deepcopy(event)
                for event in trace["events"]
                if event["type"] in {"item.started", "item.completed"}
                and isinstance(event["data"].get("item"), dict)
                and event["data"]["item"].get("type") == "mcp_tool_call"
            ]
            trace["eventCount"] = len(trace["events"])
            trace["toolEventCount"] = len(trace["toolEvents"])
        elif mutation == "shell":
            for collection in (trace["events"], trace["toolEvents"]):
                for event in collection:
                    item = event["data"].get("item")
                    if isinstance(item, dict) and item.get("id") == "inspect":
                        item["type"] = "command_execution"
                        item.pop("server", None)
                        item.pop("tool", None)
                        item.pop("arguments", None)
        elif mutation == "coverage-drift":
            for collection in (trace["events"], trace["toolEvents"]):
                for event in collection:
                    item = event["data"].get("item")
                    if isinstance(item, dict) and item.get("id") == "coverage-2":
                        item["arguments"]["top_k"] = 31
                        if event["type"] == "item.completed":
                            payload = json.loads(item["result"]["content"][0]["text"])
                            payload["parameters"]["top_k"] = 31
                            item["result"] = _result(payload)
        else:
            failed_call_id = {
                "failed-inspect": "inspect",
            }.get(mutation, "coverage-1")
            for collection in (trace["events"], trace["toolEvents"]):
                for event in collection:
                    item = event["data"].get("item")
                    if (
                        isinstance(item, dict)
                        and item.get("id") == failed_call_id
                        and event["type"] == "item.completed"
                    ):
                        item["error"] = "fixture failure"

    _rewrite_trace(trace_path, mutate)
    promptfoo = json.loads(paths["promptfoo"].read_text(encoding="utf-8"))
    row = next(row for row in promptfoo["results"]["results"] if row["id"] == "row-2-0-1")
    changed = json.loads(trace_path.read_text(encoding="utf-8"))
    row["response"]["metadata"]["executionEventHook"]["eventCount"] = changed["eventCount"]
    row["response"]["metadata"]["executionEventHook"]["toolEventCount"] = changed["toolEventCount"]
    _strict_dump(paths["promptfoo"], promptfoo)
    answer = json.loads(paths["answer"].read_text(encoding="utf-8"))
    answer["inputs"]["promptfoo"]["sha256"] = _sha(paths["promptfoo"])
    _strict_dump(paths["answer"], answer)

    with pytest.raises(attestor.AttestationError, match=message):
        _build(attestor, contract, paths, tmp_path)


def test_published_output_must_equal_confirmed_candidate(
    attestor: ModuleType, tmp_path: Path
) -> None:
    contract, paths = _fixture(tmp_path, attestor)
    promptfoo = json.loads(paths["promptfoo"].read_text(encoding="utf-8"))
    row = next(row for row in promptfoo["results"]["results"] if row["id"] == "row-2-0-1")
    changed = row["response"]["output"].replace("q031-fixture", "q031-mutated")
    row["response"]["output"] = changed
    _strict_dump(paths["promptfoo"], promptfoo)
    answer = json.loads(paths["answer"].read_text(encoding="utf-8"))
    answer["inputs"]["promptfoo"]["sha256"] = _sha(paths["promptfoo"])
    _strict_dump(paths["answer"], answer)

    with pytest.raises(attestor.AttestationError, match="published Promptfoo output differs"):
        _build(attestor, contract, paths, tmp_path)


def test_strict_json_rejects_duplicates_and_non_finite_values(attestor: ModuleType) -> None:
    with pytest.raises(attestor.AttestationError, match="duplicate JSON key"):
        attestor.strict_json_text('{"status":"pass","status":"error"}', "fixture")
    with pytest.raises(attestor.AttestationError, match="non-finite"):
        attestor.strict_json_text('{"score":NaN}', "fixture")
