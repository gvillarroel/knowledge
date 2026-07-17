"""Tests for the checked q034 independent holdout semantic review."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def load_validator():
    """Load the standalone q034 report validator."""

    path = ROOT / "validate_q034_semantic_review.py"
    spec = importlib.util.spec_from_file_location("q034_semantic_review_validator", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_checked_q034_review_has_complete_pairs_and_valid_arithmetic() -> None:
    report = load_validator().validate()
    assert len(report["reviews"]) == 12
    assert {review["family"] for review in report["reviews"]} == {
        "legacy", "embeddings", "classical", "adaptive", "entity-graph", "ensemble"
    }
    assert all("-holdout-" in review["result_binding"]["path"] for review in report["reviews"])


def test_checked_q034_review_matches_closed_json_schema() -> None:
    jsonschema = pytest.importorskip("jsonschema")
    validator = load_validator()
    report = validator.validate()
    schema = json.loads((ROOT / "reports/q034-semantic-review.schema.json").read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(report)


def test_q034_final_answer_extraction_uses_last_nonempty_assistant_text(tmp_path: Path) -> None:
    trace = tmp_path / "pi.jsonl"
    events = [
        {"type": "message_end", "message": {"role": "assistant", "content": [{"type": "text", "text": "draft"}]}},
        {"type": "message_end", "message": {"role": "user", "content": [{"type": "text", "text": "ignore"}]}},
        {"type": "message_end", "message": {"role": "assistant", "content": [{"type": "thinking", "thinking": "hidden"}, {"type": "text", "text": "final"}]}},
    ]
    trace.write_text("\n".join(json.dumps(event) for event in events), encoding="utf-8")
    assert load_validator().final_answer_text(trace) == "final"


def test_q034_status_classification_distinguishes_contract_and_json_failures() -> None:
    validator = load_validator()
    valid = {"verifier_result": {"rewards": {"response_contract": 1}}}
    invalid_contract = {"verifier_result": {"rewards": {"response_contract": 0}}}
    timeout = {"exception_info": {"exception_type": "AgentTimeoutError"}}
    assert validator._expected_status(valid, "{}") == "valid_answer"
    assert validator._expected_status(invalid_contract, "{}") == "contract_invalid"
    assert validator._expected_status(invalid_contract, "not-json") == "invalid_json"
    assert validator._expected_status(timeout, None) == "timeout"


def test_q034_raw_bindings_when_local_harbor_artifacts_are_retained() -> None:
    validator = load_validator()
    report = validator.validate()
    paths = [validator.ROOT / review["result_binding"]["path"] for review in report["reviews"]]
    if not all(path.is_file() for path in paths):
        pytest.skip("append-only Harbor artifacts are intentionally not checked in")
    validator.validate(verify_artifacts=True)
