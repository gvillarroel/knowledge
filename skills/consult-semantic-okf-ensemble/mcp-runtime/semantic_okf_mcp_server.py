#!/usr/bin/env python3
"""Expose a profile-bound Semantic OKF consultation runtime over read-only MCP."""

from __future__ import annotations

import hashlib
import hmac
import importlib
import json
import os
import re
import stat
import sys
from contextlib import redirect_stdout
from pathlib import Path
from typing import Any, Callable, Mapping


SERVER_VERSION = "1.5.0"
ENSEMBLE_SKILL = "consult-semantic-okf-ensemble"
MAX_REQUEST_BYTES = 1_000_000
BOOTSTRAP_SCHEMA = "semantic-okf-skill-bootstrap/1.0"
BOOTSTRAP_SKILL_SHA256 = "ec80687beb701f5fc8b6cd13d5ec779cbe5e1f52baffbf3a4a41db4f390717c2"
BOOTSTRAP_SKILL_BYTE_COUNT = 15_699
PREPARED_ANSWER_SCHEMA = "semantic-okf-prepared-answer/1.0"
CONFIRMATION_SCHEMA = "semantic-okf-answer-confirmation-receipt/1.0"
SKILL_ID_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
FILE_ATTRIBUTE_REPARSE_POINT = 0x400


class McpRuntimeError(RuntimeError):
    """Fail-closed error returned as an MCP tool error."""


def _object_schema(
    properties: Mapping[str, Any], required: list[str] | None = None
) -> dict[str, Any]:
    return {
        "type": "object",
        "properties": dict(properties),
        "required": required or [],
        "additionalProperties": False,
    }


STRING = {"type": "string", "minLength": 1}
POSITIVE = {"type": "integer", "minimum": 1}
STRING_ARRAY = {"type": "array", "items": {"type": "string", "minLength": 1}}


def _tool(
    name: str,
    description: str,
    schema: Mapping[str, Any],
    *,
    idempotent: bool = True,
) -> dict[str, Any]:
    return {
        "name": name,
        "description": description,
        "inputSchema": dict(schema),
        "annotations": {
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": idempotent,
            "openWorldHint": False,
        },
    }


PREPARE_PROPERTIES = {
    "question_id": STRING,
    "query": STRING,
    "draft": _object_schema(
        {
            "summary": STRING,
            "facets": {
                "type": "array",
                "minItems": 1,
                "items": _object_schema(
                    {
                        "facet": STRING,
                        "status": {
                            "type": "string",
                            "enum": ["supported", "partial", "unresolved"],
                        },
                        "statement": STRING,
                        "supporting_claim_ids": STRING_ARRAY,
                    },
                    ["facet", "status", "statement", "supporting_claim_ids"],
                ),
            },
        },
        ["summary", "facets"],
    ),
    "summary_min_words": {"type": "integer", "minimum": 1, "maximum": 5000},
    "summary_max_words": {"type": "integer", "minimum": 1, "maximum": 5000},
    "top_k": {"type": "integer", "minimum": 1, "maximum": 1000},
    "per_facet": {"type": "integer", "minimum": 1, "maximum": 30},
    "maximum_facets": {"type": "integer", "minimum": 1, "maximum": 32},
    "page_size": {"type": "integer", "minimum": 1, "maximum": 48},
}
PREPARE_SCHEMA = _object_schema(
    PREPARE_PROPERTIES,
    ["question_id", "query", "draft"],
)
CONFIRM_SCHEMA = _object_schema(
    {
        "response_sha256": {
            "type": "string",
            "pattern": "^[0-9a-f]{64}$",
        }
    },
    ["response_sha256"],
)


ENSEMBLE_TOOLS = [
    _tool(
        "semantic_okf_bootstrap_skill",
        "Call this first and exactly once, with no arguments, to load the exact hash-bound consult-semantic-okf-ensemble instructions. Follow the returned skill body before calling any other Semantic OKF tool.",
        _object_schema({}),
        idempotent=False,
    ),
    _tool(
        "semantic_okf_inspect",
        "Deep-validate the immutable profile-bound Semantic OKF snapshot before consultation.",
        _object_schema({}),
    ),
    _tool(
        "semantic_okf_coverage_brief",
        "Recompute full multisignal coverage and emit one compact page of reviewed exact claim bindings. Read every page before drafting.",
        _object_schema(
            {
                "query": STRING,
                "top_k": {"type": "integer", "minimum": 1, "maximum": 1000},
                "per_facet": {"type": "integer", "minimum": 1, "maximum": 30},
                "maximum_facets": {"type": "integer", "minimum": 1, "maximum": 32},
                "page": POSITIVE,
                "page_size": {"type": "integer", "minimum": 1, "maximum": 48},
            },
            ["query", "page"],
        ),
    ),
    _tool(
        "semantic_okf_prepare_answer",
        "Prepare canonical contracted answer JSON from the completed reviewed coverage session. Revise and call again only when the candidate itself needs correction.",
        PREPARE_SCHEMA,
    ),
    _tool(
        "semantic_okf_confirm_answer",
        "Confirm the prepared candidate by its short SHA-256 digest as the terminal tool call. After a failed attempt, prepare a fresh candidate before retrying. After a confirmed receipt, end the turn without another tool call; the host publication gate publishes the stored candidate.",
        CONFIRM_SCHEMA,
        idempotent=False,
    ),
]


def _exact_arguments(
    arguments: Any,
    *,
    required: set[str],
    optional: set[str] = frozenset(),
) -> dict[str, Any]:
    if not isinstance(arguments, dict):
        raise McpRuntimeError("tool arguments must be an object")
    keys = set(arguments)
    missing = sorted(required - keys)
    unknown = sorted(keys - required - optional)
    if missing or unknown:
        raise McpRuntimeError(
            f"tool arguments violate the closed schema: missing={missing}, unknown={unknown}"
        )
    return arguments


def _positive_int(value: Any, label: str, default: int, maximum: int) -> int:
    if value is None:
        return default
    if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= maximum:
        raise McpRuntimeError(f"{label} must be an integer from 1 through {maximum}")
    return value


def _string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise McpRuntimeError(f"{label} must be a nonempty string")
    return value


def _sha256(value: Any, label: str) -> str:
    if (
        not isinstance(value, str)
        or len(value) != 64
        or any(character not in "0123456789abcdef" for character in value)
    ):
        raise McpRuntimeError(f"{label} must be a lowercase 64-hex SHA-256 digest")
    return value


def _declared_skills() -> set[str]:
    """Parse the isolated profile skill boundary without normalizing malformed input."""

    value = os.environ.get("SKILL_ARENA_ALLOWED_SKILLS", "")
    if not value:
        return set()
    items = value.split(",")
    if (
        any(not item or SKILL_ID_PATTERN.fullmatch(item) is None for item in items)
        or len(items) != len(set(items))
    ):
        raise McpRuntimeError("SKILL_ARENA_ALLOWED_SKILLS is malformed")
    return set(items)


def _lstat_no_reparse(path: Path, label: str, *, directory: bool) -> os.stat_result:
    """Reject links/reparse points and require the expected filesystem object type."""

    try:
        result = os.lstat(path)
    except OSError as exc:
        raise McpRuntimeError(f"{label} is unavailable: {exc}") from exc
    attributes = getattr(result, "st_file_attributes", 0)
    if stat.S_ISLNK(result.st_mode) or attributes & FILE_ATTRIBUTE_REPARSE_POINT:
        raise McpRuntimeError(f"{label} must not be a link or reparse point")
    expected = stat.S_ISDIR(result.st_mode) if directory else stat.S_ISREG(result.st_mode)
    if not expected:
        kind = "directory" if directory else "regular file"
        raise McpRuntimeError(f"{label} must be a {kind}")
    return result


def _same_file_snapshot(before: os.stat_result, after: os.stat_result) -> bool:
    fields = ("st_dev", "st_ino", "st_size", "st_mtime_ns")
    return all(getattr(before, field) == getattr(after, field) for field in fields)


class SemanticOkfRuntime:
    """Bind one isolated profile to one immutable bundle and one skill runtime."""

    def __init__(self) -> None:
        self.mode, self.scripts = self._resolve_mode()
        self.bundle = self._resolve_bundle() if self.mode else None
        self.module: Any | None = None
        self.snapshot: Any | None = None
        self.validated_snapshot: Any | None = None
        self.bootstrap_attempted = False
        self.bootstrapped = False
        self.inspected = False
        self.coverage_sessions: dict[
            tuple[str, int, int, int, int], dict[str, Any]
        ] = {}
        self.prepared_response: dict[str, Any] | None = None
        self.confirmation_receipt: dict[str, Any] | None = None

    @staticmethod
    def _resolve_mode() -> tuple[str | None, Path | None]:
        declared = _declared_skills()
        if declared == {ENSEMBLE_SKILL}:
            scripts = (Path.cwd() / "skills" / ENSEMBLE_SKILL / "scripts").resolve()
            if not scripts.is_dir():
                raise McpRuntimeError(f"declared skill runtime is missing: {ENSEMBLE_SKILL}")
            return "ensemble", scripts
        if declared:
            return None, None

        # Direct standalone launch from the definitive package defaults to ensemble mode.
        sibling = (Path(__file__).resolve().parents[1] / "scripts").resolve()
        if (sibling / "_ensemble_snapshot.py").is_file():
            return "ensemble", sibling
        return None, None

    @staticmethod
    def _resolve_bundle() -> Path:
        value = os.environ.get("SEMANTIC_OKF_BUNDLE", "")
        if not value:
            raise McpRuntimeError("SEMANTIC_OKF_BUNDLE must name the immutable snapshot")
        raw = Path(value)
        if not raw.is_absolute():
            raise McpRuntimeError("SEMANTIC_OKF_BUNDLE must be absolute")
        bundle = raw.resolve(strict=True)
        if not bundle.is_dir():
            raise McpRuntimeError("SEMANTIC_OKF_BUNDLE must be a directory")
        return bundle

    def tools(self) -> list[dict[str, Any]]:
        if self.mode == "ensemble":
            return ENSEMBLE_TOOLS
        return []

    def _load(self) -> tuple[Any, Any]:
        if not self.mode or self.scripts is None or self.bundle is None:
            raise McpRuntimeError("this isolated profile has no Semantic OKF consult capability")
        if self.module is None:
            cache = os.environ.get("SEMANTIC_OKF_HF_HUB_CACHE")
            if cache:
                cache_path = Path(cache)
                if not cache_path.is_absolute() or not cache_path.is_dir():
                    raise McpRuntimeError("SEMANTIC_OKF_HF_HUB_CACHE must be an absolute directory")
                os.environ["HF_HUB_CACHE"] = str(cache_path)
            os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")
            os.environ.setdefault("HF_HUB_OFFLINE", "1")
            os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
            sys.dont_write_bytecode = True
            sys.path.insert(0, str(self.scripts))
            with redirect_stdout(sys.stderr):
                self.module = importlib.import_module("_ensemble_snapshot")
                self.validated_snapshot = self.module.load_snapshot(
                    self.bundle, deep_validation=True
                )
                # Retrieval deliberately uses the ordinary published-artifact view after
                # deep validation. This matches the CLI workflow and keeps coverage hashes
                # independent of the diagnostic deep_validation marker.
                self.snapshot = self.module.load_snapshot(
                    self.bundle, deep_validation=False
                )
        return self.module, self.snapshot

    def call(self, name: str, arguments: Any) -> Any:
        handlers: dict[str, Callable[[Any], Any]] = {
            "semantic_okf_bootstrap_skill": self._bootstrap_skill,
            "semantic_okf_inspect": self._inspect,
            "semantic_okf_coverage_brief": self._coverage_brief,
            "semantic_okf_prepare_answer": self._prepare_answer,
            "semantic_okf_confirm_answer": self._confirm_answer_call,
        }
        handler = handlers.get(name)
        if handler is None or name not in {tool["name"] for tool in self.tools()}:
            raise McpRuntimeError(f"unknown or unavailable tool: {name}")
        return handler(arguments)

    @staticmethod
    def _read_frozen_skill() -> tuple[bytes, str]:
        value = os.environ.get("CODEX_HOME", "")
        if not value:
            raise McpRuntimeError("CODEX_HOME must identify the isolated skill home")
        raw_home = Path(value)
        if not raw_home.is_absolute():
            raise McpRuntimeError("CODEX_HOME must be absolute")
        _lstat_no_reparse(raw_home, "CODEX_HOME", directory=True)
        try:
            home = raw_home.resolve(strict=True)
        except OSError as exc:
            raise McpRuntimeError(f"CODEX_HOME cannot be resolved: {exc}") from exc

        skills = home / "skills"
        package = skills / ENSEMBLE_SKILL
        target = package / "SKILL.md"
        _lstat_no_reparse(skills, "CODEX_HOME skills directory", directory=True)
        _lstat_no_reparse(package, "installed ensemble skill directory", directory=True)
        before = _lstat_no_reparse(target, "installed ensemble SKILL.md", directory=False)
        try:
            resolved_target = target.resolve(strict=True)
            resolved_target.relative_to(home)
            payload = target.read_bytes()
        except (OSError, ValueError) as exc:
            raise McpRuntimeError(
                f"installed ensemble SKILL.md is outside CODEX_HOME or unreadable: {exc}"
            ) from exc
        after = _lstat_no_reparse(target, "installed ensemble SKILL.md", directory=False)
        if resolved_target != target or not _same_file_snapshot(before, after):
            raise McpRuntimeError("installed ensemble SKILL.md changed during bootstrap")
        digest = hashlib.sha256(payload).hexdigest()
        if len(payload) != BOOTSTRAP_SKILL_BYTE_COUNT or not hmac.compare_digest(
            digest, BOOTSTRAP_SKILL_SHA256
        ):
            raise McpRuntimeError(
                "installed ensemble SKILL.md differs from the frozen skill identity"
            )
        try:
            markdown = payload.decode("utf-8", errors="strict")
        except UnicodeDecodeError as exc:
            raise McpRuntimeError("installed ensemble SKILL.md is not strict UTF-8") from exc
        if markdown.encode("utf-8") != payload:
            raise McpRuntimeError("installed ensemble SKILL.md does not round-trip as UTF-8")
        return payload, markdown

    def _bootstrap_skill(self, arguments: Any) -> dict[str, Any]:
        if self.bootstrap_attempted:
            raise McpRuntimeError(
                "semantic_okf_bootstrap_skill is one-shot and was already attempted"
            )
        # Poison the one-shot before validating any untrusted argument, path, bytes,
        # or encoding. A failed bootstrap can never be repaired inside this process.
        self.bootstrap_attempted = True
        _exact_arguments(arguments, required=set())
        payload, markdown = self._read_frozen_skill()
        self.bootstrapped = True
        return {
            "schema": BOOTSTRAP_SCHEMA,
            "skill_id": ENSEMBLE_SKILL,
            "skill_sha256": BOOTSTRAP_SKILL_SHA256,
            "byte_count": len(payload),
            "skill_markdown": markdown,
        }

    def _require_bootstrap(self) -> None:
        if not self.bootstrapped:
            raise McpRuntimeError(
                "semantic_okf_bootstrap_skill must pass before any other Semantic OKF tool"
            )

    def _inspect(self, arguments: Any) -> Any:
        self._require_bootstrap()
        _exact_arguments(arguments, required=set())
        module, snapshot = self._load()
        result = module.inspect_snapshot(self.validated_snapshot or snapshot)
        self.coverage_sessions.clear()
        self.prepared_response = None
        self.confirmation_receipt = None
        self.inspected = True
        return result

    def _require_inspection(self) -> None:
        self._require_bootstrap()
        if not self.inspected:
            raise McpRuntimeError("semantic_okf_inspect must pass before consultation")

    def _coverage_brief(self, arguments: Any) -> Any:
        self._require_inspection()
        values = _exact_arguments(
            arguments,
            required={"query", "page"},
            optional={"top_k", "per_facet", "maximum_facets", "page_size"},
        )
        module, snapshot = self._load()
        query = _string(values["query"], "query")
        top_k = _positive_int(values.get("top_k"), "top_k", 30, 1000)
        per_facet = _positive_int(values.get("per_facet"), "per_facet", 12, 30)
        maximum_facets = _positive_int(
            values.get("maximum_facets"), "maximum_facets", 12, 32
        )
        page = _positive_int(values.get("page"), "page", 1, 1_000_000)
        page_size = _positive_int(values.get("page_size"), "page_size", 48, 48)
        result = module.build_coverage_brief(
            snapshot,
            query,
            top_k,
            per_facet,
            maximum_facets,
            page,
            page_size,
        )
        key = (query, top_k, per_facet, maximum_facets, page_size)
        observed = {
            "total_pages": result["pagination"]["total_pages"],
            "total_claims": result["pagination"]["total_claims"],
            "full_sha256": result["full_coverage"]["sha256"],
            "priority_order": result["full_coverage"]["priority_order"],
            "priority_order_sha256": result["full_coverage"][
                "priority_order_sha256"
            ],
            "facets": result["facets"],
        }
        session = self.coverage_sessions.setdefault(key, {**observed, "pages": set()})
        if any(session[field] != observed[field] for field in observed):
            raise McpRuntimeError("coverage pages do not bind to one deterministic full pack")
        session["pages"].add(page)
        return result

    def _prepare_answer(self, arguments: Any) -> Any:
        self._require_inspection()
        required = {"question_id", "query", "draft"}
        optional = {
            "summary_min_words",
            "summary_max_words",
            "top_k",
            "per_facet",
            "maximum_facets",
            "page_size",
        }
        values = _exact_arguments(arguments, required=required, optional=optional)
        module, snapshot = self._load()
        draft = values["draft"]
        if not isinstance(draft, dict):
            raise McpRuntimeError("draft must be an object")
        raw_draft = json.dumps(draft, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
        question_id = _string(values["question_id"], "question_id")
        minimum = _positive_int(values.get("summary_min_words"), "summary_min_words", 180, 5000)
        maximum = _positive_int(values.get("summary_max_words"), "summary_max_words", 320, 5000)
        if minimum > maximum:
            raise McpRuntimeError("summary_min_words cannot exceed summary_max_words")
        query = _string(values["query"], "query")
        top_k = _positive_int(values.get("top_k"), "top_k", 30, 1000)
        per_facet = _positive_int(values.get("per_facet"), "per_facet", 12, 30)
        maximum_facets = _positive_int(
            values.get("maximum_facets"), "maximum_facets", 12, 32
        )
        page_size = _positive_int(values.get("page_size"), "page_size", 48, 48)
        coverage_key = (query, top_k, per_facet, maximum_facets, page_size)
        coverage_session = self.coverage_sessions.get(coverage_key)
        if coverage_session is None or coverage_session["pages"] != set(
            range(1, coverage_session["total_pages"] + 1)
        ):
            raise McpRuntimeError(
                "every coverage-brief page for the exact preparation query, parameters, "
                "and page_size must be read"
            )
        answer = module.finalize_answer(
            snapshot,
            None,
            question_id,
            query,
            minimum,
            maximum,
            top_k=top_k,
            per_facet=per_facet,
            maximum_facets=maximum_facets,
            draft_payload=raw_draft,
        )
        canonical_json = _json_text(answer)
        canonical_value = _strict_json(canonical_json)
        if not isinstance(canonical_value, dict):
            raise McpRuntimeError("the finalizer did not return a contracted JSON object")
        canonical_bytes = canonical_json.encode("utf-8")
        self.prepared_response = {
            "json": canonical_json,
            "bytes": canonical_bytes,
            "sha256": hashlib.sha256(canonical_bytes).hexdigest(),
            "coverage_sha256": coverage_session["full_sha256"],
            "coverage_key": coverage_key,
        }
        self.confirmation_receipt = None
        return {
            "schema": PREPARED_ANSWER_SCHEMA,
            "candidate_json": canonical_json,
            "response_sha256": self.prepared_response["sha256"],
            "byte_count": len(canonical_bytes),
        }

    def _confirm_answer_call(self, arguments: Any) -> dict[str, Any]:
        self._require_inspection()
        values = _exact_arguments(arguments, required={"response_sha256"})
        return self._confirm_answer(values["response_sha256"])

    def _confirm_answer(self, response_sha256: Any) -> dict[str, Any]:
        pending = self.prepared_response
        if pending is None:
            raise McpRuntimeError("no prepared response is awaiting confirmation")
        digest = _sha256(response_sha256, "response_sha256")
        if not hmac.compare_digest(digest, pending["sha256"]):
            raise McpRuntimeError(
                "response_sha256 does not match the outstanding prepared response"
            )
        receipt = {
            "schema": CONFIRMATION_SCHEMA,
            "status": "confirmed",
            "response_sha256": pending["sha256"],
            "byte_count": len(pending["bytes"]),
        }
        self.prepared_response = None
        self.confirmation_receipt = receipt
        return receipt


def _json_text(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), allow_nan=False)


def _reject_constant(value: str) -> Any:
    raise ValueError(f"non-finite JSON constant is forbidden: {value}")


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _strict_json(payload: str) -> Any:
    return json.loads(
        payload,
        object_pairs_hook=_strict_object,
        parse_constant=_reject_constant,
    )


def _result(identifier: Any, value: Any) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": identifier, "result": value}


def _error(identifier: Any, code: int, message: str) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": identifier, "error": {"code": code, "message": message}}


def _handle(runtime: SemanticOkfRuntime, request: Any) -> dict[str, Any] | None:
    if not isinstance(request, dict) or request.get("jsonrpc") != "2.0":
        return _error(request.get("id") if isinstance(request, dict) else None, -32600, "invalid request")
    identifier = request.get("id")
    method = request.get("method")
    if method == "initialize":
        params = request.get("params") if isinstance(request.get("params"), dict) else {}
        protocol = params.get("protocolVersion", "2025-06-18")
        return _result(
            identifier,
            {
                "protocolVersion": protocol,
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": "semantic-okf-read-only", "version": SERVER_VERSION},
            },
        )
    if method in {"notifications/initialized", "notifications/cancelled"}:
        return None
    if method == "ping":
        return _result(identifier, {})
    if method == "tools/list":
        return _result(identifier, {"tools": runtime.tools()})
    if method == "tools/call":
        params = request.get("params")
        if not isinstance(params, dict) or not isinstance(params.get("name"), str):
            return _error(identifier, -32602, "tools/call requires a tool name and arguments")
        try:
            with redirect_stdout(sys.stderr):
                value = runtime.call(params["name"], params.get("arguments", {}))
            serialized = _json_text(value)
            return _result(
                identifier,
                {
                    "content": [{"type": "text", "text": serialized}],
                    "isError": False,
                },
            )
        except Exception as exc:  # MCP must turn fail-closed runtime errors into tool errors.
            serialized = _json_text(
                {"status": "error", "code": "ensemble-error", "error": str(exc)}
            )
            return _result(
                identifier,
                {"content": [{"type": "text", "text": serialized}], "isError": True},
            )
    return _error(identifier, -32601, f"method not found: {method}")


def main() -> int:
    for stream in (sys.stdin, sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(encoding="utf-8")
    try:
        runtime = SemanticOkfRuntime()
    except Exception as exc:
        print(f"semantic-okf MCP startup failed: {exc}", file=sys.stderr, flush=True)
        return 2
    for line in sys.stdin:
        if len(line.encode("utf-8")) > MAX_REQUEST_BYTES:
            response = _error(None, -32700, "request exceeds the MCP size limit")
        else:
            try:
                response = _handle(runtime, _strict_json(line))
            except (json.JSONDecodeError, UnicodeError, TypeError, ValueError) as exc:
                response = _error(None, -32700, f"parse error: {exc}")
        if response is not None:
            print(_json_text(response), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
