#!/usr/bin/env python3
"""Classify the terminal outcome of one Pi JSONL trace without exposing its content."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


def message_text(message: Mapping[str, Any]) -> str | None:
    """Extract concatenated text blocks from one Pi message."""

    content = message.get("content")
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        return None
    parts = [
        block["text"]
        for block in content
        if isinstance(block, Mapping)
        and block.get("type") == "text"
        and isinstance(block.get("text"), str)
    ]
    return "".join(parts) if parts else None


def provider_outcome(error: object) -> tuple[str, str | None]:
    """Map one terminal provider error to a stable redacted outcome and code."""

    text = error if isinstance(error, str) else ""
    lowered = text.casefold()
    if "usage_limit_reached" in lowered:
        return "provider-quota", "usage_limit_reached"
    if "context_length_exceeded" in lowered:
        return "provider-context-limit", "context_length_exceeded"
    if "rate_limit" in lowered or "status_code\":429" in lowered or "status code 429" in lowered:
        return "provider-rate-limit", "rate_limit"
    return "provider-error", None


def sanitize_provider_reset(
    reset_at: object, remaining_seconds: object
) -> dict[str, Any] | None:
    """Return a canonical reset object containing only allowlisted scalar fields."""

    result: dict[str, Any] = {}
    timestamp: int | None = None
    if isinstance(reset_at, int) and not isinstance(reset_at, bool) and reset_at >= 0:
        timestamp = reset_at
    elif (
        isinstance(reset_at, str)
        and reset_at.isascii()
        and reset_at.isdecimal()
        and len(reset_at) <= 20
    ):
        timestamp = int(reset_at)
    if timestamp is not None:
        try:
            result["at"] = datetime.fromtimestamp(timestamp, tz=timezone.utc).isoformat()
        except (OverflowError, OSError, ValueError):
            pass
    elif isinstance(reset_at, str) and reset_at.isascii() and len(reset_at) <= 64:
        try:
            instant = datetime.fromisoformat(reset_at.replace("Z", "+00:00"))
        except ValueError:
            pass
        else:
            if instant.tzinfo is not None:
                result["at"] = instant.astimezone(timezone.utc).isoformat()

    remaining: int | None = None
    if (
        isinstance(remaining_seconds, int)
        and not isinstance(remaining_seconds, bool)
        and remaining_seconds >= 0
    ):
        remaining = remaining_seconds
    elif (
        isinstance(remaining_seconds, str)
        and remaining_seconds.isascii()
        and remaining_seconds.isdecimal()
        and len(remaining_seconds) <= 20
    ):
        remaining = int(remaining_seconds)
    if remaining is not None:
        result["remaining_seconds"] = remaining
    return result or None


def _embedded_provider_payload(error: object) -> Mapping[str, Any] | None:
    """Decode a structured provider payload without returning its surrounding text."""

    if isinstance(error, Mapping):
        return error
    if not isinstance(error, str):
        return None
    decoder = json.JSONDecoder()
    for offset, character in enumerate(error):
        if character != "{":
            continue
        try:
            value, _ = decoder.raw_decode(error[offset:])
        except json.JSONDecodeError:
            continue
        if isinstance(value, Mapping):
            return value
    return None


def provider_reset(error: object) -> dict[str, Any] | None:
    """Extract only a usage-limit reset instant and remaining-second count."""

    payload = _embedded_provider_payload(error)
    if payload is None:
        return None
    details = payload.get("error")
    if not isinstance(details, Mapping):
        details = payload
    error_type = details.get("type")
    if not isinstance(error_type, str) or error_type.casefold() != "usage_limit_reached":
        return None
    return sanitize_provider_reset(
        details.get("resets_at"), details.get("resets_in_seconds")
    )


def _provider_classification(error: object, parsed_events: int) -> dict[str, Any]:
    """Build one redacted provider classification with optional safe reset metadata."""

    outcome, code = provider_outcome(error)
    result: dict[str, Any] = {
        "outcome": outcome,
        "failure_domain": "provider",
        "error_code": code,
        "answer_text": None,
        "stop_reason": "error",
        "parsed_events": parsed_events,
    }
    reset = provider_reset(error) if code == "usage_limit_reached" else None
    if reset is not None:
        result["provider_reset"] = reset
    return result


def classify_pi_trace(path: Path) -> dict[str, Any]:
    """Return a stable terminal classification plus the final answer text when present."""

    raw = path.read_text(encoding="utf-8")
    try:
        direct = json.loads(raw.strip())
    except json.JSONDecodeError:
        direct = None
    if isinstance(direct, Mapping) and set(direct) == {"question_id", "answer", "evidence"}:
        return {
            "outcome": "answer-emitted",
            "failure_domain": None,
            "error_code": None,
            "answer_text": raw.strip(),
            "stop_reason": "direct-json",
            "parsed_events": 0,
        }
    last_assistant: tuple[int, Mapping[str, Any]] | None = None
    last_failed_retry: tuple[int, str] | None = None
    parsed_events = 0
    saw_tool_activity = False
    for index, line in enumerate(raw.splitlines()):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(event, Mapping):
            continue
        parsed_events += 1
        event_type = event.get("type")
        if event_type in {"tool_execution_start", "tool_execution_end", "tool_result"}:
            saw_tool_activity = True
        if event_type == "auto_retry_end" and event.get("success") is False:
            error = event.get("finalError")
            last_failed_retry = (index, error if isinstance(error, str) else "")
        if event_type != "message_end":
            continue
        message = event.get("message")
        if isinstance(message, Mapping) and message.get("role") == "assistant":
            last_assistant = (index, message)

    if last_assistant is None:
        if last_failed_retry is not None:
            return _provider_classification(last_failed_retry[1], parsed_events)
        return {
            "outcome": "missing-response" if raw.strip() else "missing-trace",
            "failure_domain": "agent",
            "error_code": None,
            "answer_text": None,
            "stop_reason": None,
            "parsed_events": parsed_events,
        }

    assistant_index, message = last_assistant
    stop_reason = message.get("stopReason")
    stop_reason = stop_reason if isinstance(stop_reason, str) else None
    text = message_text(message)
    answer_text = text.strip() if isinstance(text, str) and text.strip() else None
    error = message.get("errorMessage")
    error = error if isinstance(error, str) else ""

    if last_failed_retry is not None and last_failed_retry[0] > assistant_index:
        error = last_failed_retry[1]
        stop_reason = "error"
    if stop_reason == "error" or error:
        result = _provider_classification(error, parsed_events)
        result["stop_reason"] = stop_reason
        return result
    if stop_reason == "length":
        return {
            "outcome": "output-limit",
            "failure_domain": "agent",
            "error_code": "output_length_limit",
            "answer_text": answer_text,
            "stop_reason": stop_reason,
            "parsed_events": parsed_events,
        }
    if stop_reason in {None, "stop"} and answer_text is not None:
        return {
            "outcome": "answer-emitted",
            "failure_domain": None,
            "error_code": None,
            "answer_text": answer_text,
            "stop_reason": stop_reason,
            "parsed_events": parsed_events,
        }
    if stop_reason == "toolUse" or saw_tool_activity:
        return {
            "outcome": "agent-interrupted",
            "failure_domain": "agent",
            "error_code": None,
            "answer_text": None,
            "stop_reason": stop_reason,
            "parsed_events": parsed_events,
        }
    return {
        "outcome": "empty-response",
        "failure_domain": "agent",
        "error_code": None,
        "answer_text": None,
        "stop_reason": stop_reason,
        "parsed_events": parsed_events,
    }
