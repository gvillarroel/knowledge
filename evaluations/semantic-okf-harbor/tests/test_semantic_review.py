"""Tests for the checked q031 independent semantic review."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def load_validator():
    """Load the standalone report validator."""

    path = ROOT / "validate_semantic_review.py"
    spec = importlib.util.spec_from_file_location("semantic_review_validator", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_checked_semantic_review_has_complete_pairs_and_valid_arithmetic() -> None:
    report = load_validator().validate()
    assert len(report["reviews"]) == 12
    assert {review["family"] for review in report["reviews"]} == {
        "legacy", "embeddings", "classical", "adaptive", "entity-graph", "ensemble"
    }


def test_checked_semantic_review_matches_closed_json_schema() -> None:
    jsonschema = pytest.importorskip("jsonschema")
    validator = load_validator()
    report = validator.validate()
    schema = __import__("json").loads(
        (ROOT / "reports/q031-semantic-review.schema.json").read_text(encoding="utf-8")
    )
    jsonschema.Draft202012Validator(schema).validate(report)
