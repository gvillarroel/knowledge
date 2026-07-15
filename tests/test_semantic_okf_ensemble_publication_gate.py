from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import Any

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "skills/consult-semantic-okf-ensemble/publication-runtime/confirmed_output_gate.py"
)
PREPARE_TOOL = "semantic_okf_prepare_answer"
CONFIRM_TOOL = "semantic_okf_confirm_answer"
PREPARED_SCHEMA = "semantic-okf-prepared-answer/1.0"
TREATMENT_SKILL = "consult-semantic-okf-ensemble"
ISOLATION_RECEIPT = (
    b'{"schema":"semantic-okf-shell-isolation-receipt/1.0",'
    b'"skill_id":"consult-semantic-okf-ensemble","shell_tool_disabled":true}\n'
)


@pytest.fixture(scope="module")
def gate() -> ModuleType:
    spec = importlib.util.spec_from_file_location("semantic_okf_publication_gate", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _result(value: Any) -> dict[str, Any]:
    text = value if isinstance(value, str) else json.dumps(
        value, ensure_ascii=False, separators=(",", ":")
    )
    return {"content": [{"type": "text", "text": text}], "structured_content": None}


def _event(
    identity: str,
    tool: str,
    arguments: dict[str, Any],
    result: dict[str, Any],
    *,
    status: str = "completed",
    error: str | None = None,
) -> dict[str, Any]:
    return {
        "type": "item.completed",
        "item": {
            "id": identity,
            "type": "mcp_tool_call",
            "server": "semantic_okf",
            "tool": tool,
            "arguments": arguments,
            "result": result,
            "error": error,
            "status": status,
        },
    }


def _envelope(candidate: str) -> dict[str, Any]:
    payload = candidate.encode("utf-8")
    return {
        "schema": PREPARED_SCHEMA,
        "candidate_json": candidate,
        "response_sha256": hashlib.sha256(payload).hexdigest(),
        "byte_count": len(payload),
    }


def _trace(candidate: str, *, visible: str = "mutated") -> bytes:
    payload = candidate.encode("utf-8")
    digest = hashlib.sha256(payload).hexdigest()
    receipt = {
        "schema": "semantic-okf-answer-confirmation-receipt/1.0",
        "status": "confirmed",
        "response_sha256": hashlib.sha256(payload).hexdigest(),
        "byte_count": len(payload),
    }
    events = [
        _event(
            "prepare",
            PREPARE_TOOL,
            {"question_id": "q031", "query": "query", "draft": {}},
            _result(_envelope(candidate)),
        ),
        _event(
            "confirm",
            CONFIRM_TOOL,
            {"response_sha256": digest},
            _result(receipt),
        ),
        {"type": "item.completed", "item": {"id": "answer", "type": "agent_message", "text": visible}},
    ]
    return ("\n".join(json.dumps(row, ensure_ascii=False) for row in events) + "\n").encode("utf-8")


def test_confirmed_candidate_accepts_exact_two_phase_trace(gate: ModuleType) -> None:
    candidate = '{"question_id":"q031","answer":null,"evidence":[]}'
    assert gate.confirmed_candidate(_trace(candidate)) == candidate.encode("utf-8")


def test_long_candidate_is_never_copied_into_confirmation_arguments(
    gate: ModuleType,
) -> None:
    candidate = json.dumps(
        {
            "question_id": "q-long",
            "answer": {"summary": "évidence " + ("x" * 25_000)},
            "evidence": [],
        },
        ensure_ascii=False,
        separators=(",", ":"),
    )
    rows = [json.loads(line) for line in _trace(candidate).decode().splitlines()]
    confirm_arguments = rows[1]["item"]["arguments"]
    assert confirm_arguments == {
        "response_sha256": hashlib.sha256(candidate.encode("utf-8")).hexdigest()
    }
    assert candidate not in json.dumps(confirm_arguments)
    assert gate.confirmed_candidate(_trace(candidate)) == candidate.encode("utf-8")


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (lambda envelope: envelope.__setitem__("schema", "wrong/1.0"), "wrong schema"),
        (
            lambda envelope: envelope.__setitem__("response_sha256", "0" * 64),
            "digest or length does not bind",
        ),
        (
            lambda envelope: envelope.__setitem__("response_sha256", "A" * 64),
            "lowercase 64-hex",
        ),
        (lambda envelope: envelope.__setitem__("byte_count", 1), "digest or length does not bind"),
        (
            lambda envelope: envelope.__setitem__(
                "candidate_json", envelope["candidate_json"] + " "
            ),
            "not canonical object JSON",
        ),
    ],
)
def test_tampered_prepare_envelope_is_rejected(
    gate: ModuleType, mutation: Any, message: str
) -> None:
    candidate = '{"question_id":"q031","answer":null,"evidence":[]}'
    rows = [json.loads(line) for line in _trace(candidate).decode().splitlines()]
    envelope = json.loads(rows[0]["item"]["result"]["content"][0]["text"])
    mutation(envelope)
    rows[0]["item"]["result"] = _result(envelope)
    stdout = ("\n".join(json.dumps(row) for row in rows) + "\n").encode()
    with pytest.raises(gate.PublicationGateError, match=message):
        gate.confirmed_candidate(stdout)


def test_prepare_envelope_requires_canonical_exact_order_and_closed_schema(
    gate: ModuleType,
) -> None:
    candidate = '{"question_id":"q031","answer":null,"evidence":[]}'
    for envelope, message in [
        (
            {
                "candidate_json": candidate,
                "schema": PREPARED_SCHEMA,
                "response_sha256": hashlib.sha256(candidate.encode()).hexdigest(),
                "byte_count": len(candidate.encode()),
            },
            "required key order",
        ),
        ({**_envelope(candidate), "extra": True}, "closed schema"),
    ]:
        rows = [json.loads(line) for line in _trace(candidate).decode().splitlines()]
        rows[0]["item"]["result"] = _result(envelope)
        stdout = ("\n".join(json.dumps(row) for row in rows) + "\n").encode()
        with pytest.raises(gate.PublicationGateError, match=message):
            gate.confirmed_candidate(stdout)


def test_last_of_multiple_successful_prepares_is_the_only_publishable_candidate(
    gate: ModuleType,
) -> None:
    first = '{"question_id":"q031","answer":null,"evidence":[]}'
    final = '{"question_id":"q031","answer":{"summary":"revised"},"evidence":[]}'
    rows = [json.loads(line) for line in _trace(final).decode().splitlines()]
    rows.insert(
        0,
        _event(
            "prepare-first",
            PREPARE_TOOL,
            {"question_id": "q031", "query": "query", "draft": {}},
            _result(_envelope(first)),
        ),
    )
    stdout = ("\n".join(json.dumps(row) for row in rows) + "\n").encode()
    assert gate.confirmed_candidate(stdout) == final.encode("utf-8")


def test_failed_or_extra_confirm_calls_never_form_an_accepted_suffix(
    gate: ModuleType,
) -> None:
    candidate = '{"question_id":"q031","answer":null,"evidence":[]}'
    payload = candidate.encode("utf-8")
    receipt = {
        "schema": "semantic-okf-answer-confirmation-receipt/1.0",
        "status": "confirmed",
        "response_sha256": hashlib.sha256(payload).hexdigest(),
        "byte_count": len(payload),
    }
    prepare = _event(
        "prepare",
        PREPARE_TOOL,
        {"question_id": "q031", "query": "query", "draft": {}},
        _result(_envelope(candidate)),
    )
    missing_candidate = _event(
        "missing",
        CONFIRM_TOOL,
        {},
        _result({"status": "error"}),
        status="failed",
        error="response_sha256 is required",
    )
    exact_confirm = _event(
        "confirm",
        CONFIRM_TOOL,
        {"response_sha256": receipt["response_sha256"]},
        _result(receipt),
    )
    repeated = _event(
        "repeated",
        CONFIRM_TOOL,
        {"response_sha256": receipt["response_sha256"]},
        _result({"status": "error"}),
        status="failed",
        error="no prepared response",
    )
    for rows, message in (
        ([prepare, missing_candidate, exact_confirm], "no successful preparation"),
        ([prepare, exact_confirm, repeated], "only the final protocol call"),
    ):
        stdout = ("\n".join(json.dumps(row) for row in rows) + "\n").encode()
        with pytest.raises(gate.PublicationGateError, match=message):
            gate.confirmed_candidate(stdout)


def test_failed_confirmation_can_recover_only_after_a_fresh_prepare(
    gate: ModuleType,
) -> None:
    candidate = '{"question_id":"q031","answer":null,"evidence":[]}'
    rows = [json.loads(line) for line in _trace(candidate).decode().splitlines()]
    failed = _event(
        "failed-confirm",
        CONFIRM_TOOL,
        {"response_sha256": "0" * 64},
        _result({"status": "error"}),
        status="failed",
    )
    fresh_prepare = _event(
        "fresh-prepare",
        PREPARE_TOOL,
        {"question_id": "q031", "query": "query", "draft": {}},
        _result(_envelope(candidate)),
    )
    rows[1:1] = [failed, fresh_prepare]
    stdout = ("\n".join(json.dumps(row) for row in rows) + "\n").encode()

    assert gate.confirmed_candidate(stdout) == candidate.encode("utf-8")


def test_failed_preparation_can_recover_with_a_clean_final_transaction(
    gate: ModuleType,
) -> None:
    candidate = '{"question_id":"q031","answer":null,"evidence":[]}'
    rows = [json.loads(line) for line in _trace(candidate).decode().splitlines()]
    failed_prepare = rows[0]
    failed_prepare["item"].update(status="failed", error="draft rejected")
    fresh_prepare = _event(
        "fresh-prepare",
        PREPARE_TOOL,
        {"question_id": "q031", "query": "query", "draft": {}},
        _result(_envelope(candidate)),
    )
    rows.insert(1, fresh_prepare)
    stdout = ("\n".join(json.dumps(row) for row in rows) + "\n").encode()

    assert gate.confirmed_candidate(stdout) == candidate.encode("utf-8")


def test_failed_prepare_clears_an_older_successful_transaction(
    gate: ModuleType,
) -> None:
    candidate = '{"question_id":"q031","answer":null,"evidence":[]}'
    rows = [json.loads(line) for line in _trace(candidate).decode().splitlines()]
    failed_prepare = _event(
        "failed-prepare",
        PREPARE_TOOL,
        {"question_id": "q031", "query": "query", "draft": {}},
        _result({"status": "error"}),
        status="failed",
        error="draft rejected",
    )
    rows.insert(1, failed_prepare)
    stdout = ("\n".join(json.dumps(row) for row in rows) + "\n").encode()

    with pytest.raises(gate.PublicationGateError, match="no successful preparation"):
        gate.confirmed_candidate(stdout)


def test_multiple_successful_confirmations_are_rejected(gate: ModuleType) -> None:
    candidate = '{"question_id":"q031","answer":null,"evidence":[]}'
    rows = [json.loads(line) for line in _trace(candidate).decode().splitlines()]
    rows[2:2] = rows[:2]
    stdout = ("\n".join(json.dumps(row) for row in rows) + "\n").encode()

    with pytest.raises(gate.PublicationGateError, match="only the final protocol call"):
        gate.confirmed_candidate(stdout)


def test_protocol_shape_error_reports_only_sanitized_call_statuses(
    gate: ModuleType,
) -> None:
    candidate = '{"question_id":"q031","answer":null,"evidence":[]}'
    rows = [json.loads(line) for line in _trace(candidate).decode().splitlines()]
    rows[1]["item"].update(status="failed", error="retry required")
    stdout = ("\n".join(json.dumps(row) for row in rows) + "\n").encode()

    with pytest.raises(gate.PublicationGateError) as caught:
        gate.confirmed_candidate(stdout)

    message = str(caught.value)
    assert "observed=[prepare:completed:no-error,confirm:failed:error]" in message
    assert candidate not in message


def test_confirmation_must_be_the_terminal_tool_call(gate: ModuleType) -> None:
    candidate = '{"question_id":"q031","answer":null,"evidence":[]}'
    rows = [json.loads(line) for line in _trace(candidate).decode().splitlines()]
    rows.insert(
        -1,
        {
            "type": "item.completed",
            "item": {
                "id": "after-confirm",
                "type": "mcp_tool_call",
                "server": "other",
                "tool": "other_tool",
                "arguments": {},
                "result": _result({"status": "ok"}),
                "error": None,
                "status": "completed",
            },
        },
    )
    stdout = ("\n".join(json.dumps(row) for row in rows) + "\n").encode()
    with pytest.raises(gate.PublicationGateError, match="terminal tool call"):
        gate.confirmed_candidate(stdout)


def test_run_atomically_replaces_mutated_visible_output(
    gate: ModuleType, tmp_path: Path
) -> None:
    candidate = '{"question_id":"q031","answer":null,"evidence":[]}'
    output = tmp_path / "last-message.json"
    output.write_text("mutated", encoding="utf-8")
    executable = tmp_path / "codex.exe"
    executable.write_bytes(b"fixture")

    def runner(command: list[str], **kwargs: Any) -> SimpleNamespace:
        assert command[0] == str(executable.resolve())
        assert kwargs["input"] == b"prompt"
        return SimpleNamespace(returncode=0, stdout=_trace(candidate), stderr=b"")

    code, stdout, stderr = gate.run(
        ["exec", "--output-last-message", str(output)],
        stdin=b"prompt",
        environ={
            "SEMANTIC_OKF_REAL_CODEX": str(executable),
            "SKILL_ARENA_ALLOWED_SKILLS": "",
        },
        runner=runner,
    )
    assert (code, stderr) == (0, b"")
    assert stdout == _trace(candidate)
    assert output.read_bytes() == candidate.encode("utf-8")
    assert not list(tmp_path.glob("*.confirmed.tmp"))


def test_control_without_finalizer_is_transparent(gate: ModuleType, tmp_path: Path) -> None:
    output = tmp_path / "last-message.txt"
    output.write_text("control", encoding="utf-8")
    executable = tmp_path / "codex.exe"
    executable.write_bytes(b"fixture")
    trace = b'{"type":"item.completed","item":{"type":"agent_message","text":"control"}}\n'

    def runner(*_args: Any, **_kwargs: Any) -> SimpleNamespace:
        return SimpleNamespace(returncode=0, stdout=trace, stderr=b"warning")

    result = gate.run(
        ["exec", "--output-last-message", str(output)],
        stdin=b"",
        environ={
            "SEMANTIC_OKF_REAL_CODEX": str(executable),
            "SKILL_ARENA_ALLOWED_SKILLS": "",
        },
        runner=runner,
    )
    assert result == (0, trace, b"warning")
    assert output.read_text(encoding="utf-8") == "control"


def test_treatment_disables_shell_and_persists_canonical_isolation_receipt(
    gate: ModuleType, tmp_path: Path
) -> None:
    output = tmp_path / "last-message.txt"
    output.write_text("treatment", encoding="utf-8")
    executable = tmp_path / "codex.exe"
    executable.write_bytes(b"fixture")
    trace = b'{"type":"item.completed","item":{"type":"agent_message","text":"treatment"}}\n'

    def runner(command: list[str], **kwargs: Any) -> SimpleNamespace:
        assert command == [
            str(executable.resolve()),
            "--disable",
            "shell_tool",
            "exec",
            "--output-last-message",
            str(output),
        ]
        assert kwargs["env"]["SKILL_ARENA_ALLOWED_SKILLS"] == TREATMENT_SKILL
        return SimpleNamespace(returncode=0, stdout=trace, stderr=b"child-warning\n")

    result = gate.run(
        ["exec", "--output-last-message", str(output)],
        stdin=b"",
        environ={
            "SEMANTIC_OKF_REAL_CODEX": str(executable),
            "SKILL_ARENA_ALLOWED_SKILLS": TREATMENT_SKILL,
        },
        runner=runner,
    )
    assert result == (0, trace, ISOLATION_RECEIPT + b"child-warning\n")
    receipt = json.loads(result[2].splitlines()[0])
    assert list(receipt) == ["schema", "skill_id", "shell_tool_disabled"]
    assert receipt == {
        "schema": "semantic-okf-shell-isolation-receipt/1.0",
        "skill_id": TREATMENT_SKILL,
        "shell_tool_disabled": True,
    }
    assert output.read_text(encoding="utf-8") == "treatment"


@pytest.mark.parametrize(
    "allowed",
    [
        None,
        " consult-semantic-okf-ensemble",
        "consult-semantic-okf-ensemble ",
        "consult-semantic-okf-ensemble,,other",
        "consult-semantic-okf-ensemble,consult-semantic-okf-ensemble",
        "consult-semantic-okf-ensemble,consult-semantic-okf-adaptive",
        "Consult-Semantic-OKF-Ensemble",
    ],
)
def test_profile_boundary_fails_closed_on_missing_malformed_or_ambiguous_values(
    gate: ModuleType,
    tmp_path: Path,
    allowed: str | None,
) -> None:
    executable = tmp_path / "codex.exe"
    executable.write_bytes(b"fixture")
    environment = {"SEMANTIC_OKF_REAL_CODEX": str(executable)}
    if allowed is not None:
        environment["SKILL_ARENA_ALLOWED_SKILLS"] = allowed

    with pytest.raises(gate.PublicationGateError, match="required|malformed|only allowed"):
        gate.run(
            ["exec"],
            stdin=b"",
            environ=environment,
            runner=lambda *_args, **_kwargs: pytest.fail("runner must not execute"),
        )


@pytest.mark.parametrize(
    "arguments",
    [
        ["exec", "--enable", "shell_tool"],
        ["exec", "--enable=shell_tool"],
        ["exec", "--config", "features.shell_tool=true"],
    ],
)
def test_treatment_rejects_any_shell_tool_override(
    gate: ModuleType,
    tmp_path: Path,
    arguments: list[str],
) -> None:
    executable = tmp_path / "codex.exe"
    executable.write_bytes(b"fixture")
    with pytest.raises(gate.PublicationGateError, match="must not override"):
        gate.run(
            arguments,
            stdin=b"",
            environ={
                "SEMANTIC_OKF_REAL_CODEX": str(executable),
                "SKILL_ARENA_ALLOWED_SKILLS": TREATMENT_SKILL,
            },
            runner=lambda *_args, **_kwargs: pytest.fail("runner must not execute"),
        )


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        (lambda rows: rows.__setitem__(1, rows[0]), "must end"),
        (
            lambda rows: rows[1]["item"]["arguments"].__setitem__(
                "response_sha256", "0" * 64
            ),
            "differs from the last prepare",
        ),
        (
            lambda rows: json.loads(
                rows[1]["item"]["result"]["content"][0]["text"]
            ).update({"byte_count": 1}),
            "unused fixture mutation",
        ),
    ],
)
def test_protocol_failures_are_rejected(
    gate: ModuleType, mutate: Any, message: str
) -> None:
    candidate = '{"question_id":"q031","answer":null,"evidence":[]}'
    rows = [json.loads(line) for line in _trace(candidate).decode().splitlines()]
    if message == "unused fixture mutation":
        receipt = json.loads(rows[1]["item"]["result"]["content"][0]["text"])
        receipt["byte_count"] = 1
        rows[1]["item"]["result"] = _result(receipt)
        message = "receipt does not bind"
    else:
        mutate(rows)
    stdout = ("\n".join(json.dumps(row) for row in rows) + "\n").encode()
    with pytest.raises(gate.PublicationGateError, match=message):
        gate.confirmed_candidate(stdout)


def test_duplicate_keys_and_nonfinite_json_are_rejected(gate: ModuleType) -> None:
    with pytest.raises(gate.PublicationGateError, match="duplicate JSON key"):
        gate.strict_json('{"candidate_json":"a","candidate_json":"b"}', "fixture")
    with pytest.raises(gate.PublicationGateError, match="non-finite"):
        gate.strict_json('{"score":NaN}', "fixture")


def test_nonzero_codex_exit_is_propagated_without_publication(
    gate: ModuleType, tmp_path: Path
) -> None:
    output = tmp_path / "last-message.txt"
    output.write_text("unchanged", encoding="utf-8")
    executable = tmp_path / "codex.exe"
    executable.write_bytes(b"fixture")

    def runner(*_args: Any, **_kwargs: Any) -> SimpleNamespace:
        return SimpleNamespace(returncode=17, stdout=b"partial", stderr=b"failure")

    result = gate.run(
        ["exec", "--output-last-message", str(output)],
        stdin=b"",
        environ={
            "SEMANTIC_OKF_REAL_CODEX": str(executable),
            "SKILL_ARENA_ALLOWED_SKILLS": "",
        },
        runner=runner,
    )
    assert result == (17, b"partial", b"failure")
    assert output.read_text(encoding="utf-8") == "unchanged"


def test_confirmed_trace_requires_absolute_unique_output_target(
    gate: ModuleType,
) -> None:
    with pytest.raises(gate.PublicationGateError, match="must be absolute"):
        gate.output_path(["--output-last-message", "relative.json"])
    with pytest.raises(gate.PublicationGateError, match="one output"):
        gate.output_path(
            ["--output-last-message=C:/one", "--output-last-message", "C:/two"]
        )


def test_cmd_launcher_is_fail_closed_and_package_relative() -> None:
    launcher = SCRIPT.with_name("run_codex.cmd").read_text(encoding="utf-8")
    assert "SEMANTIC_OKF_PYTHON" in launcher
    assert "%~dp0confirmed_output_gate.py" in launcher
    assert "exit /b 86" in launcher
    assert "2>&1" not in launcher


def test_real_codex_prefers_windows_command_shim(
    gate: ModuleType, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    shim = tmp_path / "codex.cmd"
    store_binary = tmp_path / "codex.exe"
    shim.write_bytes(b"fixture")
    store_binary.write_bytes(b"fixture")

    def which(name: str) -> str | None:
        return {
            "codex.cmd": str(shim),
            "codex.exe": str(store_binary),
            "codex": None,
        }[name]

    monkeypatch.setattr(gate.shutil, "which", which)
    assert gate._real_codex({}) == str(shim.resolve())
