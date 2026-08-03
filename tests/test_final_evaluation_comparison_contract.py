"""Tests for aggregate dataset semantics in final comparison tables."""

from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import sys
from types import ModuleType

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = REPO_ROOT / "evaluations" / "validate_comparison_contract.py"
CONTRACT_PATH = REPO_ROOT / "evaluations" / "LATEST-REPORT.comparison.json"
LATEST_REPORT = REPO_ROOT / "evaluations" / "LATEST-REPORT.md"


def load_validator() -> ModuleType:
    """Load the standalone aggregate comparison validator."""

    specification = importlib.util.spec_from_file_location(
        "knowledge_final_comparison_contract_validator",
        VALIDATOR_PATH,
    )
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    return module


def base_version_contract() -> dict[str, object]:
    """Return the handwritten base/version comparison as a valid contract."""

    return {
        "schema_version": "final-report-comparison/1.0",
        "report": "comparison.md",
        "heading": "## Direct comparison",
        "dataset_scope": {
            "dataset_id": "example-dataset",
            "cohort": "all",
            "candidate_budget": "same",
            "identity_grouping": "item",
            "metric_contract": "example/1.0",
        },
        "metrics": [
            {
                "id": "accuracy",
                "label": "Accuracy",
                "unit": "percent",
                "aggregation": "mean",
                "direction": "higher",
                "display_precision": 0,
            },
            {
                "id": "latency_ms",
                "label": "Mean latency",
                "unit": "ms",
                "aggregation": "mean",
                "direction": "lower",
                "display_precision": 0,
            },
        ],
        "alternatives": [
            {
                "id": "base",
                "label": "Base",
                "metrics": {"accuracy": 70, "latency_ms": 120},
            },
            {
                "id": "v1",
                "label": "V1",
                "metrics": {"accuracy": 60, "latency_ms": 200},
            },
            {
                "id": "v2",
                "label": "V2",
                "metrics": {"accuracy": 71, "latency_ms": 100},
            },
        ],
    }


def base_version_markdown() -> str:
    """Render the expected base/version primary table."""

    return """# Evaluation

## Direct comparison

| Pos. | Pair / strategy | Accuracy | Mean latency |
|---:|---|---:|---:|
| 1 | Base | 70% | 120 ms |
| 2 | V1 | 60% | 200 ms |
| 3 | V2 | 71% | 100 ms |
"""


def test_latest_report_matches_aggregate_dataset_contract() -> None:
    """Every current primary row and metric is machine-bound to one scope."""

    validator = load_validator()
    contract = validator.load_contract(CONTRACT_PATH)
    table = validator.validate_report_against_contract(
        LATEST_REPORT.read_text(encoding="utf-8"),
        contract,
    )

    assert len(table.rows) == 25
    assert [metric["aggregation"] for metric in contract["metrics"]] == [
        "mean",
        "mean",
        "mean",
        "ratio",
        "percentile_95",
    ]
    assert (
        contract["dataset_scope"]["dataset_id"]
        == "graphrag-papers-parallel-eval-60-v1"
    )


def test_base_version_rows_are_alternatives_and_columns_are_aggregates() -> None:
    """The intended handwritten example is accepted without status columns."""

    validator = load_validator()
    table = validator.validate_report_against_contract(
        base_version_markdown(),
        base_version_contract(),
    )

    assert [row[1] for row in table.rows] == ["Base", "V1", "V2"]
    assert table.headers[2:] == ("Accuracy", "Mean latency")


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (
            lambda contract: contract["alternatives"][0]["metrics"].pop("latency_ms"),
            "provide exactly",
        ),
        (
            lambda contract: contract["metrics"][0].update({"aggregation": "raw"}),
            "aggregate dataset metric",
        ),
        (
            lambda contract: contract["alternatives"][0].update(
                {"decision": "accepted"}
            ),
            "keys differ",
        ),
        (
            lambda contract: contract["alternatives"][1].update({"id": "base"}),
            "Duplicate alternative id",
        ),
    ],
)
def test_contract_rejects_incomplete_or_nonmetric_comparisons(
    mutation,
    message: str,
) -> None:
    """Completeness, aggregation, and governance separation are mandatory."""

    validator = load_validator()
    contract = base_version_contract()
    mutation(contract)

    with pytest.raises(validator.ComparisonContractError, match=message):
        validator.validate_contract(contract)


def test_markdown_projection_cannot_drift_from_numeric_contract() -> None:
    """A formatted table value must equal its bound aggregate value."""

    validator = load_validator()
    markdown = base_version_markdown().replace(
        "| 3 | V2 | 71% | 100 ms |",
        "| 3 | V2 | 73% | 100 ms |",
    )

    with pytest.raises(validator.ComparisonContractError, match="row 3 differs"):
        validator.validate_report_against_contract(
            markdown,
            base_version_contract(),
        )


def test_cli_uses_contract_relative_report_path(tmp_path: Path) -> None:
    """The semantic validator is a standalone reproducible command."""

    contract = base_version_contract()
    (tmp_path / "comparison.md").write_text(
        base_version_markdown(),
        encoding="utf-8",
        newline="\n",
    )
    contract_path = tmp_path / "comparison.json"
    contract_path.write_text(
        json.dumps(contract, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )

    import subprocess

    completed = subprocess.run(
        [sys.executable, str(VALIDATOR_PATH), str(contract_path)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    assert "3 alternatives, 2 aggregate dataset metrics" in completed.stdout
