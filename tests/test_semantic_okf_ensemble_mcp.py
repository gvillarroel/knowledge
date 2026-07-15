from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import Any

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
MCP_ROOT = REPO_ROOT / "skills" / "consult-semantic-okf-ensemble" / "mcp-runtime"
MCP_SERVER = MCP_ROOT / "semantic_okf_mcp_server.py"
BOOTSTRAP_TOOL = "semantic_okf_bootstrap_skill"
PREPARE_TOOL = "semantic_okf_prepare_answer"
CONFIRM_TOOL = "semantic_okf_confirm_answer"
BOOTSTRAP_SCHEMA = "semantic-okf-skill-bootstrap/1.0"
FROZEN_SKILL = REPO_ROOT / "skills" / "consult-semantic-okf-ensemble" / "SKILL.md"
FROZEN_SKILL_SHA256 = "ec80687beb701f5fc8b6cd13d5ec779cbe5e1f52baffbf3a4a41db4f390717c2"
FROZEN_SKILL_BYTE_COUNT = 15_699
PREPARED_SCHEMA = "semantic-okf-prepared-answer/1.0"
FINAL_BUNDLE = (
    REPO_ROOT
    / "evaluations"
    / "semantic-okf-ensemble"
    / "results"
    / "runs"
    / "20260715-ensemble-final-03"
    / "workspace-a"
    / "knowledge"
)
Q031_QUERY = (
    "A production router must choose among question-only or standalone-model answering, "
    "basic RAG, and GraphRAG before generation. Derive an evidence-based decision boundary "
    "for simple facts, interconnected synthesis, and noisy graph evidence, and explain why "
    "an always-use-the-graph policy is unsupported."
)


@pytest.fixture(scope="module")
def mcp() -> ModuleType:
    spec = importlib.util.spec_from_file_location("_test_semantic_okf_mcp", MCP_SERVER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _fake_runtime(mcp: ModuleType) -> tuple[Any, dict[str, Any]]:
    captured: dict[str, Any] = {}

    def brief(
        _snapshot: Any,
        query: str,
        top_k: int,
        per_facet: int,
        maximum_facets: int,
        page: int,
        page_size: int,
    ) -> dict[str, Any]:
        return {
            "pagination": {"total_pages": 2, "total_claims": 3},
            "full_coverage": {
                "sha256": "a" * 64,
                "priority_order": "persisted-idf-facet-consensus-priority-v1",
                "priority_order_sha256": "b" * 64,
            },
            "facets": [{"facet_index": 1, "facet": query}],
            "claims": [{"claim_id": f"claim-{page}"}],
            "parameters": {
                "top_k": top_k,
                "per_facet": per_facet,
                "maximum_facets": maximum_facets,
                "page_size": page_size,
            },
        }

    def finalize(
        _snapshot: Any,
        _path: Any,
        question_id: str,
        query: str,
        minimum: int,
        maximum: int,
        *,
        top_k: int,
        per_facet: int,
        maximum_facets: int,
        draft_payload: str,
    ) -> dict[str, Any]:
        captured.update(
            question_id=question_id,
            query=query,
            minimum=minimum,
            maximum=maximum,
            top_k=top_k,
            per_facet=per_facet,
            maximum_facets=maximum_facets,
            draft=json.loads(draft_payload),
        )
        return {"question_id": question_id, "answer": {"status": "pass"}, "evidence": []}

    runtime = object.__new__(mcp.SemanticOkfRuntime)
    runtime.mode = "ensemble"
    runtime.scripts = Path("scripts")
    runtime.bundle = Path("knowledge")
    runtime.module = SimpleNamespace(
        inspect_snapshot=lambda _snapshot: {"status": "pass", "deep_validation": True},
        build_coverage_brief=brief,
        finalize_answer=finalize,
    )
    runtime.snapshot = object()
    runtime.validated_snapshot = runtime.snapshot
    runtime.bootstrap_attempted = True
    runtime.bootstrapped = True
    runtime.inspected = False
    runtime.coverage_sessions = {}
    runtime.prepared_response = None
    runtime.confirmation_receipt = None
    return runtime, captured


def _assert_prepared_envelope(
    envelope: dict[str, Any], expected_question_id: str
) -> tuple[str, str]:
    assert list(envelope) == [
        "schema",
        "candidate_json",
        "response_sha256",
        "byte_count",
    ]
    assert envelope["schema"] == PREPARED_SCHEMA
    candidate_json = envelope["candidate_json"]
    assert json.dumps(
        json.loads(candidate_json),
        ensure_ascii=False,
        separators=(",", ":"),
    ) == candidate_json
    assert json.loads(candidate_json)["question_id"] == expected_question_id
    payload = candidate_json.encode("utf-8")
    digest = hashlib.sha256(payload).hexdigest()
    assert envelope["response_sha256"] == digest
    assert envelope["byte_count"] == len(payload)
    return candidate_json, digest


def test_profile_gate_exposes_split_closed_answer_tools(
    mcp: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(REPO_ROOT)
    monkeypatch.setenv("SKILL_ARENA_ALLOWED_SKILLS", "consult-semantic-okf-adaptive")
    control = mcp.SemanticOkfRuntime()
    assert control.mode is None
    assert control.tools() == []

    monkeypatch.setenv("SKILL_ARENA_ALLOWED_SKILLS", "consult-semantic-okf-ensemble")
    monkeypatch.setenv("SEMANTIC_OKF_BUNDLE", str(FINAL_BUNDLE.resolve()))
    treatment = mcp.SemanticOkfRuntime()
    tools = treatment.tools()
    assert [tool["name"] for tool in tools] == [
        BOOTSTRAP_TOOL,
        "semantic_okf_inspect",
        "semantic_okf_coverage_brief",
        PREPARE_TOOL,
        CONFIRM_TOOL,
    ]
    for tool in tools:
        expected_annotations = {
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": tool["name"] not in {BOOTSTRAP_TOOL, CONFIRM_TOOL},
            "openWorldHint": False,
        }
        assert tool["annotations"] == expected_annotations
        assert tool["inputSchema"]["additionalProperties"] is False
        assert not ({"path", "bundle", "cache", "command", "url"} & tool["inputSchema"]["properties"].keys())
    prepare_schema = tools[-2]["inputSchema"]
    assert prepare_schema["required"] == ["question_id", "query", "draft"]
    assert "mode" not in prepare_schema["properties"]
    assert prepare_schema["properties"]["page_size"] == {
        "type": "integer",
        "minimum": 1,
        "maximum": 48,
    }
    confirm_schema = tools[-1]["inputSchema"]
    assert confirm_schema == {
        "type": "object",
        "properties": {
            "response_sha256": {
                "type": "string",
                "pattern": "^[0-9a-f]{64}$",
            }
        },
        "required": ["response_sha256"],
        "additionalProperties": False,
    }


def test_bootstrap_is_exact_hash_bound_canonical_one_shot_and_gates_tools(
    mcp: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(REPO_ROOT)
    monkeypatch.setenv("SKILL_ARENA_ALLOWED_SKILLS", "consult-semantic-okf-ensemble")
    monkeypatch.setenv("SEMANTIC_OKF_BUNDLE", str(FINAL_BUNDLE.resolve()))
    monkeypatch.setenv("CODEX_HOME", str(REPO_ROOT.resolve()))
    runtime = mcp.SemanticOkfRuntime()

    for tool, arguments in [
        ("semantic_okf_inspect", {}),
        ("semantic_okf_coverage_brief", {"query": "q", "page": 1}),
        (PREPARE_TOOL, {}),
        (CONFIRM_TOOL, {"response_sha256": "0" * 64}),
    ]:
        with pytest.raises(mcp.McpRuntimeError, match="bootstrap_skill must pass"):
            runtime.call(tool, arguments)
    response = mcp._handle(
        runtime,
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": BOOTSTRAP_TOOL, "arguments": {}},
        },
    )
    assert response["result"]["isError"] is False
    text = response["result"]["content"][0]["text"]
    envelope = json.loads(text)
    assert list(envelope) == [
        "schema",
        "skill_id",
        "skill_sha256",
        "byte_count",
        "skill_markdown",
    ]
    assert json.dumps(envelope, ensure_ascii=False, separators=(",", ":")) == text
    payload = envelope["skill_markdown"].encode("utf-8")
    assert envelope == {
        "schema": BOOTSTRAP_SCHEMA,
        "skill_id": "consult-semantic-okf-ensemble",
        "skill_sha256": FROZEN_SKILL_SHA256,
        "byte_count": FROZEN_SKILL_BYTE_COUNT,
        "skill_markdown": FROZEN_SKILL.read_text(encoding="utf-8"),
    }
    assert payload == FROZEN_SKILL.read_bytes()
    assert len(payload) == FROZEN_SKILL_BYTE_COUNT
    assert hashlib.sha256(payload).hexdigest() == FROZEN_SKILL_SHA256
    replay = mcp._handle(
        runtime,
        {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {"name": BOOTSTRAP_TOOL, "arguments": {}},
        },
    )
    assert replay["result"]["isError"] is True
    assert "one-shot and was already attempted" in replay["result"]["content"][0]["text"]
    assert runtime.bootstrap_attempted is True
    assert runtime.bootstrapped is True


def test_bootstrap_fails_closed_on_missing_relative_tampered_and_reparse_inputs(
    mcp: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.chdir(REPO_ROOT)
    monkeypatch.setenv("SKILL_ARENA_ALLOWED_SKILLS", "consult-semantic-okf-ensemble")
    monkeypatch.setenv("SEMANTIC_OKF_BUNDLE", str(FINAL_BUNDLE.resolve()))

    def fresh_runtime() -> Any:
        return mcp.SemanticOkfRuntime()

    monkeypatch.delenv("CODEX_HOME", raising=False)
    runtime = fresh_runtime()
    with pytest.raises(mcp.McpRuntimeError, match="CODEX_HOME must identify"):
        runtime.call(BOOTSTRAP_TOOL, {})
    assert runtime.bootstrap_attempted is True
    assert runtime.bootstrapped is False
    monkeypatch.setenv("CODEX_HOME", str(REPO_ROOT.resolve()))
    with pytest.raises(mcp.McpRuntimeError, match="already attempted"):
        runtime.call(BOOTSTRAP_TOOL, {})
    with pytest.raises(mcp.McpRuntimeError, match="bootstrap_skill must pass"):
        runtime.call("semantic_okf_inspect", {})

    monkeypatch.setenv("CODEX_HOME", "relative-home")
    runtime = fresh_runtime()
    with pytest.raises(mcp.McpRuntimeError, match="must be absolute"):
        runtime.call(BOOTSTRAP_TOOL, {})
    assert runtime.bootstrap_attempted is True
    assert runtime.bootstrapped is False

    installed = tmp_path / "skills" / "consult-semantic-okf-ensemble"
    installed.mkdir(parents=True)
    (installed / "SKILL.md").write_bytes(FROZEN_SKILL.read_bytes() + b"tampered")
    monkeypatch.setenv("CODEX_HOME", str(tmp_path.resolve()))
    runtime = fresh_runtime()
    with pytest.raises(mcp.McpRuntimeError, match="frozen skill identity"):
        runtime.call(BOOTSTRAP_TOOL, {})
    assert runtime.bootstrap_attempted is True
    assert runtime.bootstrapped is False
    (installed / "SKILL.md").write_bytes(FROZEN_SKILL.read_bytes())
    with pytest.raises(mcp.McpRuntimeError, match="already attempted"):
        runtime.call(BOOTSTRAP_TOOL, {})

    monkeypatch.setenv("CODEX_HOME", str(REPO_ROOT.resolve()))
    runtime = fresh_runtime()
    with pytest.raises(mcp.McpRuntimeError, match="closed schema"):
        runtime.call(BOOTSTRAP_TOOL, {"path": str(FROZEN_SKILL)})
    assert runtime.bootstrap_attempted is True
    assert runtime.bootstrapped is False
    with pytest.raises(mcp.McpRuntimeError, match="already attempted"):
        runtime.call(BOOTSTRAP_TOOL, {})

    original_lstat = mcp.os.lstat

    def reparse_target(path: Any) -> Any:
        result = original_lstat(path)
        if Path(path).name == "SKILL.md":
            return SimpleNamespace(
                st_mode=result.st_mode,
                st_file_attributes=mcp.FILE_ATTRIBUTE_REPARSE_POINT,
            )
        return result

    monkeypatch.setattr(mcp.os, "lstat", reparse_target)
    monkeypatch.setenv("CODEX_HOME", str(tmp_path.resolve()))
    runtime = fresh_runtime()
    with pytest.raises(mcp.McpRuntimeError, match="link or reparse point"):
        runtime.call(BOOTSTRAP_TOOL, {})
    assert runtime.bootstrap_attempted is True
    assert runtime.bootstrapped is False
    with pytest.raises(mcp.McpRuntimeError, match="already attempted"):
        runtime.call(BOOTSTRAP_TOOL, {})


def test_profile_skill_boundary_rejects_normalized_or_ambiguous_values(
    mcp: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    for malformed in [
        " consult-semantic-okf-ensemble",
        "consult-semantic-okf-ensemble ",
        "consult-semantic-okf-ensemble,,other",
        "consult-semantic-okf-ensemble,consult-semantic-okf-ensemble",
        "Consult-Semantic-OKF-Ensemble",
    ]:
        monkeypatch.setenv("SKILL_ARENA_ALLOWED_SKILLS", malformed)
        with pytest.raises(mcp.McpRuntimeError, match="malformed"):
            mcp._declared_skills()


def test_mcp_gate_requires_inspection_all_pages_and_exact_parameters(mcp: ModuleType) -> None:
    runtime, captured = _fake_runtime(mcp)
    query = "full question"
    with pytest.raises(mcp.McpRuntimeError, match="inspect must pass"):
        runtime.call("semantic_okf_coverage_brief", {"query": query, "page": 1})

    assert runtime.call("semantic_okf_inspect", {})["status"] == "pass"
    first = runtime.call(
        "semantic_okf_coverage_brief",
        {"query": query, "page": 1, "page_size": 48},
    )
    assert first["claims"] == [{"claim_id": "claim-1"}]
    draft = {
        "summary": "one two three",
        "facets": [
            {
                "facet": query,
                "status": "supported",
                "statement": "Supported.",
                "supporting_claim_ids": ["claim-1"],
            }
        ],
    }
    finalize_args = {
        "question_id": "q-test",
        "query": query,
        "draft": draft,
        "summary_min_words": 3,
        "summary_max_words": 10,
    }
    with pytest.raises(mcp.McpRuntimeError, match="every coverage-brief page"):
        runtime.call(PREPARE_TOOL, finalize_args)
    runtime.call("semantic_okf_coverage_brief", {"query": query, "page": 2})
    result = runtime.call(PREPARE_TOOL, finalize_args)
    candidate_json, digest = _assert_prepared_envelope(result, "q-test")
    receipt = runtime.call(
        CONFIRM_TOOL,
        {"response_sha256": digest},
    )
    assert receipt == {
        "schema": "semantic-okf-answer-confirmation-receipt/1.0",
        "status": "confirmed",
        "response_sha256": hashlib.sha256(candidate_json.encode("utf-8")).hexdigest(),
        "byte_count": len(candidate_json.encode("utf-8")),
    }
    assert captured == {
        "draft": draft,
        "maximum": 10,
        "maximum_facets": 12,
        "minimum": 3,
        "per_facet": 12,
        "query": query,
        "question_id": "q-test",
        "top_k": 30,
    }

    with pytest.raises(mcp.McpRuntimeError, match="closed schema"):
        runtime.call("semantic_okf_inspect", {"path": "knowledge"})
    with pytest.raises(mcp.McpRuntimeError, match="every coverage-brief page"):
        runtime.call(PREPARE_TOOL, {**finalize_args, "top_k": 31})


def test_prepare_binds_exact_completed_page_size_session(mcp: ModuleType) -> None:
    runtime, _ = _fake_runtime(mcp)
    query = "full question"
    runtime.call("semantic_okf_inspect", {})
    for page in (1, 2):
        runtime.call(
            "semantic_okf_coverage_brief",
            {"query": query, "page": page, "page_size": 7},
        )

    prepare = {
        "question_id": "q-page-size",
        "query": query,
        "summary_min_words": 3,
        "summary_max_words": 10,
        "draft": {
            "summary": "one two three",
            "facets": [
                {
                    "facet": query,
                    "status": "supported",
                    "statement": "Supported.",
                    "supporting_claim_ids": ["claim-1"],
                }
            ],
        },
    }
    with pytest.raises(mcp.McpRuntimeError, match="page_size"):
        runtime.call(PREPARE_TOOL, prepare)

    result = runtime.call(
        PREPARE_TOOL,
        {**prepare, "page_size": 7},
    )
    _assert_prepared_envelope(result, "q-page-size")
    assert runtime.prepared_response["coverage_key"] == (query, 30, 12, 12, 7)
    assert runtime.prepared_response["coverage_sha256"] == "a" * 64

    with pytest.raises(mcp.McpRuntimeError, match="page_size"):
        runtime.call(
            PREPARE_TOOL,
            {**prepare, "page_size": 49},
        )


def test_split_answer_tools_reject_modes_missing_digest_and_legacy_name(
    mcp: ModuleType,
) -> None:
    runtime, _ = _fake_runtime(mcp)
    runtime.call("semantic_okf_inspect", {})
    with pytest.raises(mcp.McpRuntimeError, match="closed schema"):
        runtime.call(CONFIRM_TOOL, {})
    with pytest.raises(mcp.McpRuntimeError, match="closed schema"):
        runtime.call(
            PREPARE_TOOL,
            {"mode": "prepare", "question_id": "q", "query": "q", "draft": {}},
        )
    with pytest.raises(mcp.McpRuntimeError, match="unknown or unavailable"):
        runtime.call("semantic_okf_finalize_answer", {})


def test_confirmation_fails_closed_and_is_exactly_once(mcp: ModuleType) -> None:
    runtime, _ = _fake_runtime(mcp)
    query = "full question"
    runtime.call("semantic_okf_inspect", {})
    for page in (1, 2):
        runtime.call("semantic_okf_coverage_brief", {"query": query, "page": page})

    with pytest.raises(mcp.McpRuntimeError, match="no prepared response"):
        runtime.call(
            CONFIRM_TOOL,
            {"response_sha256": "0" * 64},
        )

    prepared = runtime.call(
        PREPARE_TOOL,
        {
            "question_id": "q-confirmation",
            "query": query,
            "summary_min_words": 3,
            "summary_max_words": 10,
            "draft": {
                "summary": "one two three",
                "facets": [
                    {
                        "facet": query,
                        "status": "supported",
                        "statement": "Supported.",
                        "supporting_claim_ids": ["claim-1"],
                    }
                ],
            },
        },
    )
    candidate_json, digest = _assert_prepared_envelope(prepared, "q-confirmation")
    expected_pending = runtime.prepared_response
    assert expected_pending is not None
    assert len(candidate_json) > len(digest)

    for invalid, message in [
        ("0" * 64, "does not match"),
        (digest.upper(), "lowercase 64-hex"),
        (digest[:-1], "lowercase 64-hex"),
        ("g" * 64, "lowercase 64-hex"),
    ]:
        with pytest.raises(mcp.McpRuntimeError, match=message):
            runtime.call(
                CONFIRM_TOOL,
                {"response_sha256": invalid},
            )
        assert runtime.prepared_response is expected_pending
        assert runtime.confirmation_receipt is None

    receipt = runtime.call(
        CONFIRM_TOOL,
        {"response_sha256": digest},
    )
    assert receipt["response_sha256"] == hashlib.sha256(
        candidate_json.encode("utf-8")
    ).hexdigest()
    assert runtime.prepared_response is None
    assert runtime.confirmation_receipt == receipt
    with pytest.raises(mcp.McpRuntimeError, match="no prepared response"):
        runtime.call(
            CONFIRM_TOOL,
            {"response_sha256": digest},
        )
    runtime.call(PREPARE_TOOL, {
        "question_id": "q-confirmation-reset",
        "query": query,
        "summary_min_words": 3,
        "summary_max_words": 10,
        "draft": {
            "summary": "one two three",
            "facets": [
                {
                    "facet": query,
                    "status": "supported",
                    "statement": "Supported.",
                    "supporting_claim_ids": ["claim-1"],
                }
            ],
        },
    })
    assert runtime.prepared_response is not None
    runtime.call("semantic_okf_inspect", {})
    assert runtime.prepared_response is None
    assert runtime.confirmation_receipt is None
    assert runtime.coverage_sessions == {}


def test_mcp_transport_confirmation_binds_emitted_final_response_hash(
    mcp: ModuleType,
) -> None:
    runtime, _ = _fake_runtime(mcp)
    query = "full question"
    runtime.call("semantic_okf_inspect", {})
    for page in (1, 2):
        runtime.call("semantic_okf_coverage_brief", {"query": query, "page": page})
    prepared = mcp._handle(
        runtime,
        {
            "jsonrpc": "2.0",
            "id": 10,
            "method": "tools/call",
            "params": {
                "name": PREPARE_TOOL,
                "arguments": {
                    "question_id": "q-trace",
                    "query": query,
                    "summary_min_words": 3,
                    "summary_max_words": 10,
                    "draft": {
                        "summary": "one two three",
                        "facets": [
                            {
                                "facet": query,
                                "status": "supported",
                                "statement": "Supported.",
                                "supporting_claim_ids": ["claim-1"],
                            }
                        ],
                    },
                },
            },
        },
    )
    assert prepared["result"]["isError"] is False
    envelope_text = prepared["result"]["content"][0]["text"]
    envelope = json.loads(envelope_text)
    assert json.dumps(envelope, separators=(",", ":")) == envelope_text
    candidate_json, digest = _assert_prepared_envelope(envelope, "q-trace")
    mismatched = mcp._handle(
        runtime,
        {
            "jsonrpc": "2.0",
            "id": 11,
            "method": "tools/call",
            "params": {
                "name": CONFIRM_TOOL,
                "arguments": {
                    "response_sha256": "0" * 64,
                },
            },
        },
    )
    assert mismatched["result"]["isError"] is True
    assert "does not match" in mismatched["result"]["content"][0]["text"]
    assert runtime.prepared_response is not None
    confirmed = mcp._handle(
        runtime,
        {
            "jsonrpc": "2.0",
            "id": 12,
            "method": "tools/call",
            "params": {
                "name": CONFIRM_TOOL,
                "arguments": {"response_sha256": digest},
            },
        },
    )
    assert confirmed["result"]["isError"] is False
    receipt = json.loads(confirmed["result"]["content"][0]["text"])
    emitted_final_response = candidate_json
    assert receipt["status"] == "confirmed"
    assert receipt["response_sha256"] == hashlib.sha256(
        emitted_final_response.encode("utf-8")
    ).hexdigest()
    assert receipt["byte_count"] == len(emitted_final_response.encode("utf-8"))
    assert json.loads(emitted_final_response)["question_id"] == "q-trace"


def test_mcp_protocol_is_strict_and_returns_tool_errors(mcp: ModuleType) -> None:
    runtime, _ = _fake_runtime(mcp)
    initialized = mcp._handle(
        runtime,
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {"protocolVersion": "2026-07-28"},
        },
    )
    assert initialized["result"]["protocolVersion"] == "2026-07-28"
    assert initialized["result"]["capabilities"] == {"tools": {"listChanged": False}}
    assert initialized["result"]["serverInfo"]["version"] == "1.5.0"
    assert mcp._handle(runtime, {"jsonrpc": "2.0", "method": "notifications/initialized"}) is None
    assert mcp._handle(runtime, {"jsonrpc": "2.0", "id": 2, "method": "ping"})["result"] == {}

    listed = mcp._handle(runtime, {"jsonrpc": "2.0", "id": 3, "method": "tools/list"})
    assert len(listed["result"]["tools"]) == 5
    failed = mcp._handle(
        runtime,
        {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {"name": CONFIRM_TOOL, "arguments": {}},
        },
    )
    assert failed["result"]["isError"] is True
    assert json.loads(failed["result"]["content"][0]["text"])["code"] == "ensemble-error"
    assert mcp._handle(runtime, {"jsonrpc": "2.0", "id": 5, "method": "missing"})["error"]["code"] == -32601

    with pytest.raises(ValueError, match="duplicate JSON key"):
        mcp._strict_json('{"id":1,"id":2}')
    with pytest.raises(ValueError, match="non-finite"):
        mcp._strict_json('{"value":NaN}')


def test_mcp_subprocess_lists_no_control_tools_and_exact_treatment_tools() -> None:
    base_environment = os.environ.copy()
    base_environment["PYTHONDONTWRITEBYTECODE"] = "1"
    initialization = "\n".join(
        [
            json.dumps(
                {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "initialize",
                    "params": {"protocolVersion": "2025-06-18"},
                }
            ),
            json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}),
            json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}),
            "",
        ]
    )
    for allowed, expected in [
        ("consult-semantic-okf-adaptive", []),
        (
            "consult-semantic-okf-ensemble",
            [
                BOOTSTRAP_TOOL,
                "semantic_okf_inspect",
                "semantic_okf_coverage_brief",
                PREPARE_TOOL,
                CONFIRM_TOOL,
            ],
        ),
    ]:
        environment = base_environment.copy()
        environment["SKILL_ARENA_ALLOWED_SKILLS"] = allowed
        environment["SEMANTIC_OKF_BUNDLE"] = str(FINAL_BUNDLE.resolve())
        environment["CODEX_HOME"] = str(REPO_ROOT.resolve())
        completed = subprocess.run(
            [sys.executable, str(MCP_SERVER)],
            input=initialization,
            text=True,
            capture_output=True,
            cwd=REPO_ROOT,
            env=environment,
            timeout=30,
            check=False,
        )
        assert completed.returncode == 0, completed.stderr
        responses = [json.loads(line) for line in completed.stdout.splitlines()]
        assert [tool["name"] for tool in responses[1]["result"]["tools"]] == expected


def test_q031_real_mcp_session_preserves_full_coverage_and_finalizer() -> None:
    runtime_python = Path(
        os.environ.get(
            "SEMANTIC_OKF_PYTHON",
            str(REPO_ROOT / ".venv" / "Scripts" / "python.exe"),
        )
    )
    if not FINAL_BUNDLE.is_dir() or not runtime_python.is_file():
        pytest.skip("the generated final bundle and exact semantic runtime are required")

    program = r'''
import hashlib
import importlib.util
import json
import os
import sys
from pathlib import Path

root = Path(sys.argv[1])
bundle = Path(sys.argv[2])
query = sys.argv[3]
server = root / "skills/consult-semantic-okf-ensemble/mcp-runtime/semantic_okf_mcp_server.py"
spec = importlib.util.spec_from_file_location("mcp_integration", server)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

def tree():
    return {
        path.relative_to(bundle).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(bundle.rglob("*")) if path.is_file()
    }

before = tree()
runtime = module.SemanticOkfRuntime()
bootstrap = runtime.call("semantic_okf_bootstrap_skill", {})
inspection = runtime.call("semantic_okf_inspect", {})
first = runtime.call("semantic_okf_coverage_brief", {"query": query, "page": 1})
pages = [first]
for number in range(2, first["pagination"]["total_pages"] + 1):
    pages.append(runtime.call("semantic_okf_coverage_brief", {"query": query, "page": number}))
draft = json.loads((root / "evaluations/semantic-okf-ensemble/manual-query-q031-draft.json").read_text(encoding="utf-8"))
prepared = module._handle(runtime, {
    "jsonrpc": "2.0",
    "id": 10,
    "method": "tools/call",
    "params": {
        "name": "semantic_okf_prepare_answer",
        "arguments": {
            "question_id": "q031-graph-routing-boundary",
            "query": query,
            "draft": draft,
        },
    },
})
assert prepared["result"]["isError"] is False
envelope_json = prepared["result"]["content"][0]["text"]
envelope = module._strict_json(envelope_json)
assert list(envelope) == ["schema", "candidate_json", "response_sha256", "byte_count"]
candidate_json = envelope["candidate_json"]
assert envelope["response_sha256"] == hashlib.sha256(candidate_json.encode("utf-8")).hexdigest()
assert envelope["byte_count"] == len(candidate_json.encode("utf-8"))
confirmed = module._handle(runtime, {
    "jsonrpc": "2.0",
    "id": 11,
    "method": "tools/call",
    "params": {
        "name": "semantic_okf_confirm_answer",
        "arguments": {"response_sha256": envelope["response_sha256"]},
    },
})
assert confirmed["result"]["isError"] is False
receipt = json.loads(confirmed["result"]["content"][0]["text"])
answer = module._strict_json(candidate_json)
claim_ids = [claim["claim_id"] for page in pages for claim in page["claims"]]
print(json.dumps({
    "bootstrap_bytes": bootstrap["byte_count"],
    "bootstrap_sha256": bootstrap["skill_sha256"],
    "status": inspection["status"],
    "deep_validation": inspection["deep_validation"],
    "pages": len(pages),
    "claims": len(claim_ids),
    "unique_claims": len(set(claim_ids)),
    "hashes": sorted({page["full_coverage"]["sha256"] for page in pages}),
    "question_id": answer["question_id"],
    "non_null": answer["answer"] is not None,
    "evidence": len(answer["evidence"]),
    "confirmation_status": receipt["status"],
    "confirmation_sha256": receipt["response_sha256"],
    "final_response_sha256": hashlib.sha256(candidate_json.encode("utf-8")).hexdigest(),
    "bundle_unchanged": before == tree(),
}, sort_keys=True))
'''
    environment = os.environ.copy()
    environment.update(
        CODEX_HOME=str(REPO_ROOT.resolve()),
        SKILL_ARENA_ALLOWED_SKILLS="consult-semantic-okf-ensemble",
        SEMANTIC_OKF_BUNDLE=str(FINAL_BUNDLE.resolve()),
        PYTHONDONTWRITEBYTECODE="1",
        HF_HUB_OFFLINE="1",
        TRANSFORMERS_OFFLINE="1",
        HF_HUB_DISABLE_PROGRESS_BARS="1",
    )
    governed_cache = environment.get("SEMANTIC_OKF_HF_HUB_CACHE")
    if governed_cache:
        environment["HF_HUB_CACHE"] = governed_cache
    completed = subprocess.run(
        [str(runtime_python), "-c", program, str(REPO_ROOT), str(FINAL_BUNDLE), Q031_QUERY],
        cwd=REPO_ROOT,
        env=environment,
        text=True,
        capture_output=True,
        encoding="utf-8",
        timeout=300,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    result = json.loads(completed.stdout)
    assert result == {
        "bootstrap_bytes": FROZEN_SKILL_BYTE_COUNT,
        "bootstrap_sha256": FROZEN_SKILL_SHA256,
        "bundle_unchanged": True,
        "claims": 206,
        "confirmation_sha256": result["final_response_sha256"],
        "confirmation_status": "confirmed",
        "deep_validation": True,
        "evidence": result["evidence"],
        "final_response_sha256": result["final_response_sha256"],
        "hashes": ["881dec7d573003631c7ee5bb6c55ba4568393df1f911c26dbaa7bfa5c0619ac7"],
        "non_null": True,
        "pages": 5,
        "question_id": "q031-graph-routing-boundary",
        "status": "pass",
        "unique_claims": 206,
    }
    assert result["evidence"] >= 3
    assert len(result["final_response_sha256"]) == 64
