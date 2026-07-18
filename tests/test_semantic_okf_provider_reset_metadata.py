"""Regression tests for sanitized provider reset metadata propagation."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
GRADER_ROOT = REPO / "evaluations/semantic-okf-harbor/grader"
DATASET_ROOT = REPO / "evaluations/semantic-okf-datasets"
sys.path.insert(0, str(GRADER_ROOT))
sys.path.insert(0, str(DATASET_ROOT))

import run_consult_campaign as CAMPAIGN  # noqa: E402
from trace_status import classify_pi_trace  # noqa: E402


RESET = {
    "at": "2026-07-23T14:24:32+00:00",
    "remaining_seconds": 489909,
}
SECRET = "Bearer private-credential-and-answer"


def usage_limit_error(*, include_body_reset: bool = True) -> str:
    """Return a realistic prefixed provider error containing private decoys."""

    details: dict[str, object] = {
        "type": "usage_limit_reached",
        "message": f"raw private provider message {SECRET}",
        "plan_type": "private-plan",
        "eligible_promo": {"private": True},
    }
    if include_body_reset:
        details.update({"resets_at": 1784816672, "resets_in_seconds": 489909})
    payload = {
        "type": "error",
        "error": details,
        "status_code": 429,
        "headers": {
            "Authorization": SECRET,
            "X-Codex-Primary-Reset-At": "1999999999",
            "X-Codex-Primary-Reset-After-Seconds": "999999",
        },
        "answer": SECRET,
        "unrelated_provider_metadata": {"account": SECRET},
    }
    return "API Error 429: " + json.dumps(payload)


def write_assistant_error(path: Path, error: str) -> None:
    """Write one terminal Pi assistant error event."""

    event = {
        "type": "message_end",
        "message": {
            "role": "assistant",
            "content": [{"type": "text", "text": SECRET}],
            "stopReason": "error",
            "errorMessage": error,
        },
    }
    path.write_text(json.dumps(event) + "\n", encoding="utf-8")


def assert_private_material_absent(value: object) -> None:
    """Assert that a durable or redacted value contains no fixture secrets."""

    serialized = json.dumps(value, sort_keys=True)
    for forbidden in (
        SECRET,
        "raw private provider message",
        "Authorization",
        "headers",
        "plan_type",
        "eligible_promo",
        "status_code",
        "unrelated_provider_metadata",
        "answer\"",
    ):
        assert forbidden not in serialized


def test_usage_limit_trace_exposes_only_canonical_body_reset(tmp_path: Path) -> None:
    trace = tmp_path / "pi.jsonl"
    write_assistant_error(trace, usage_limit_error())

    classified = classify_pi_trace(trace)

    assert classified == {
        "answer_text": None,
        "error_code": "usage_limit_reached",
        "failure_domain": "provider",
        "outcome": "provider-quota",
        "parsed_events": 1,
        "provider_reset": RESET,
        "stop_reason": "error",
    }
    assert_private_material_absent(classified)


def test_reset_headers_are_not_a_metadata_fallback(tmp_path: Path) -> None:
    trace = tmp_path / "pi.jsonl"
    write_assistant_error(trace, usage_limit_error(include_body_reset=False))

    classified = classify_pi_trace(trace)

    assert classified["outcome"] == "provider-quota"
    assert classified["error_code"] == "usage_limit_reached"
    assert "provider_reset" not in classified
    assert_private_material_absent(classified)


def test_historical_retry_error_shape_still_classifies_without_reset(tmp_path: Path) -> None:
    trace = tmp_path / "pi.jsonl"
    event = {
        "type": "auto_retry_end",
        "success": False,
        "finalError": "usage_limit_reached legacy private detail",
    }
    trace.write_text(json.dumps(event) + "\n", encoding="utf-8")

    classified = classify_pi_trace(trace)

    assert classified["outcome"] == "provider-quota"
    assert classified["error_code"] == "usage_limit_reached"
    assert classified["answer_text"] is None
    assert "provider_reset" not in classified
    assert "legacy private detail" not in json.dumps(classified)


def test_campaign_outcome_and_checkpoint_allowlist_reset_only(tmp_path: Path) -> None:
    cell = {
        "cohort": "discovery",
        "family": "adaptive",
        "question_id": "q001",
        "sequence": 1,
    }
    raw_outcome = {
        "answer_text": SECRET,
        "credentials": SECRET,
        "error_code": "usage_limit_reached",
        "failure_domain": "provider",
        "headers": {"Authorization": SECRET},
        "outcome": "provider-quota",
        "parsed_events": 31,
        "provider_reset": {**RESET, "account": SECRET, "headers": {"secret": SECRET}},
        "raw_error": SECRET,
        "run_exit_code": 2,
        "stop_reason": "error",
        "trace_path": "q001__fixture/artifacts/pi.jsonl",
        "unrelated_provider_metadata": {"plan": SECRET},
    }
    campaign = tmp_path / "campaign"

    persisted = CAMPAIGN._persist_outcome(campaign, cell, raw_outcome)
    checkpoint = CAMPAIGN._persist_terminal_checkpoint(
        campaign,
        "aborted",
        "a" * 64,
        {1: persisted},
        trigger=persisted,
    )

    assert persisted["provider_reset"] == RESET
    assert checkpoint["trigger"]["provider_reset"] == RESET
    assert_private_material_absent(persisted)
    assert_private_material_absent(checkpoint)
    assert json.loads((campaign / "outcomes/0001.json").read_text(encoding="utf-8")) == persisted
    assert json.loads(
        (campaign / "checkpoints/aborted.json").read_text(encoding="utf-8")
    ) == checkpoint
    non_quota = CAMPAIGN._bind_outcome(
        cell,
        {
            "answer_text": SECRET,
            "error_code": None,
            "failure_domain": None,
            "outcome": "answer-emitted",
            "provider_reset": RESET,
        },
    )
    assert "provider_reset" not in non_quota
    assert_private_material_absent(non_quota)


def test_historical_checkpoint_trigger_remains_valid_without_reset() -> None:
    historical = {
        "cohort": "discovery",
        "error_code": "usage_limit_reached",
        "family": "adaptive",
        "outcome": "provider-quota",
        "question_id": "q001",
        "sequence": 1,
    }

    assert CAMPAIGN.checkpoint_trigger(historical) == historical
