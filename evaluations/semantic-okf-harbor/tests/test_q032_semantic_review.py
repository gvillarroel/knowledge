"""Tests for the checked q032 independent semantic review."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def load_validator():
    """Load the standalone q032 report validator."""

    path = ROOT / "validate_q032_semantic_review.py"
    spec = importlib.util.spec_from_file_location("q032_semantic_review_validator", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_checked_q032_review_has_complete_pairs_and_valid_arithmetic() -> None:
    report = load_validator().validate()
    assert len(report["reviews"]) == 12
    assert {review["family"] for review in report["reviews"]} == {
        "legacy", "embeddings", "classical", "adaptive", "entity-graph", "ensemble"
    }
    assert all("-q032-grader-r1/" in review["result_binding"]["path"] for review in report["reviews"])


def test_checked_q032_review_matches_closed_json_schema() -> None:
    jsonschema = pytest.importorskip("jsonschema")
    validator = load_validator()
    report = validator.validate()
    schema = json.loads((ROOT / "reports/q032-semantic-review.schema.json").read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(report)


def test_q032_final_answer_extraction_uses_last_nonempty_assistant_text(tmp_path: Path) -> None:
    trace = tmp_path / "pi.jsonl"
    events = [
        {"type": "message_end", "message": {"role": "assistant", "content": [{"type": "text", "text": "draft"}]}},
        {"type": "message_end", "message": {"role": "user", "content": [{"type": "text", "text": "ignore"}]}},
        {"type": "message_end", "message": {"role": "assistant", "content": [{"type": "thinking", "thinking": "hidden"}, {"type": "text", "text": "final"}]}},
    ]
    trace.write_text("\n".join(json.dumps(event) for event in events), encoding="utf-8")
    assert load_validator().final_answer_text(trace) == "final"


def test_q032_raw_bindings_when_local_harbor_artifacts_are_retained() -> None:
    validator = load_validator()
    report = validator.validate()
    paths = [validator.ROOT / review["result_binding"]["path"] for review in report["reviews"]]
    if not all(path.is_file() for path in paths):
        pytest.skip("append-only Harbor artifacts are intentionally not checked in")
    validator.validate(verify_artifacts=True)
