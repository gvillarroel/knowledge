"""Tests for the current-facing final evaluation report presentation."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
from types import ModuleType

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = REPO_ROOT / "evaluations" / "validate_final_report.py"
LATEST_REPORT = REPO_ROOT / "evaluations" / "LATEST-REPORT.md"


def load_validator() -> ModuleType:
    """Load the standalone final-report validator."""

    spec = importlib.util.spec_from_file_location(
        "knowledge_final_report_validator",
        VALIDATOR_PATH,
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_latest_report_lists_every_comparable_direct_strategy() -> None:
    """The primary table includes every route under the shared direct contract."""

    validator = load_validator()
    table = validator.validate_report(LATEST_REPORT.read_text(encoding="utf-8"))

    assert table.headers == (
        "Pos.",
        "Pair / strategy",
        "Recall@10",
        "MRR@10",
        "nDCG@10",
        "Stable queries",
        "P95",
    )
    assert len(table.rows) == 25
    assert [row[0] for row in table.rows] == [str(index) for index in range(1, 26)]
    assert all("status" not in header.casefold() for header in table.headers)
    assert all(cell != "—" for row in table.rows for cell in row[2:])


def test_validator_accepts_metrics_specific_to_another_dataset() -> None:
    """Metric names are dataset-specific rather than fixed to retrieval."""

    validator = load_validator()
    report = """# Final report

## Direct comparison

| Pos. | Pair / strategy | Accuracy | Macro F1 | P95 |
|---:|---|---:|---:|---:|
| 1 | Candidate v2 | 91.20% | 88.40% | 42.1 ms |
| 2 | Candidate v1 | 89.10% | 86.75% | 39.8 ms |
"""

    table = validator.validate_report(report)

    assert table.headers[2:] == ("Accuracy", "Macro F1", "P95")


def test_validator_rejects_status_as_a_primary_column() -> None:
    """Governance conclusions remain outside the primary metric table."""

    validator = load_validator()
    report = """# Final report

## Direct comparison

| Pos. | Pair / strategy | Accuracy | Status |
|---:|---|---:|---|
| 1 | Candidate v2 | 91.20% | Accepted |
"""

    with pytest.raises(validator.ReportFormatError, match="dataset metrics"):
        validator.validate_report(report)


def test_validator_rejects_missing_metric_placeholders() -> None:
    """A row without the displayed metrics cannot receive a position."""

    validator = load_validator()
    report = """# Final report

## Direct comparison

| Pos. | Pair / strategy | Accuracy | P95 |
|---:|---|---:|---:|
| 1 | Candidate v2 | 91.20% | 42.1 ms |
| 2 | Candidate v1 | — | — |
"""

    with pytest.raises(validator.ReportFormatError, match="missing"):
        validator.validate_report(report)


def test_validator_rejects_trailing_unmeasured_strategies() -> None:
    """Strategies without comparable results stay outside the ranked table."""

    validator = load_validator()
    report = """# Final report

## Direct comparison

| Pos. | Pair / strategy | Accuracy | P95 |
|---:|---|---:|---:|
| 1 | Candidate v2 | 91.20% | 42.1 ms |
| — | Separate benchmark | — | — |
"""

    with pytest.raises(validator.ReportFormatError, match="sequential position"):
        validator.validate_report(report)


def test_validator_rejects_partial_metrics_in_an_unranked_row() -> None:
    """An unranked row cannot imply cross-contract comparability."""

    validator = load_validator()
    report = """# Final report

## Direct comparison

| Pos. | Pair / strategy | Accuracy | P95 |
|---:|---|---:|---:|
| 1 | Candidate v2 | 91.20% | 42.1 ms |
| — | Separate benchmark | 87.00% | — |
"""

    with pytest.raises(validator.ReportFormatError, match="sequential position"):
        validator.validate_report(report)
