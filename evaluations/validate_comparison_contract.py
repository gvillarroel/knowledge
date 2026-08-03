"""Validate aggregate dataset semantics behind a final Markdown comparison table."""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
from pathlib import Path
import re
import sys
from types import ModuleType
from typing import Any, Sequence


SCHEMA_VERSION = "final-report-comparison/1.0"
ALLOWED_AGGREGATIONS = {
    "mean",
    "ratio",
    "percentile_50",
    "percentile_95",
    "sum",
    "count",
}
ALLOWED_UNITS = {"percent", "score", "ms", "seconds", "count", "bytes"}
ALLOWED_DIRECTIONS = {"higher", "lower"}
SCOPE_KEYS = {
    "dataset_id",
    "cohort",
    "candidate_budget",
    "identity_grouping",
    "metric_contract",
}
TOP_LEVEL_KEYS = {
    "schema_version",
    "report",
    "heading",
    "dataset_scope",
    "metrics",
    "alternatives",
}
METRIC_KEYS = {
    "id",
    "label",
    "unit",
    "aggregation",
    "direction",
    "display_precision",
}
ALTERNATIVE_KEYS = {"id", "label", "metrics"}
METRIC_ID_RE = re.compile(r"^[a-z][a-z0-9_]*$")
ALTERNATIVE_ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*$")


class ComparisonContractError(ValueError):
    """Raised when aggregate comparison semantics are missing or inconsistent."""


def _load_markdown_validator() -> ModuleType:
    path = Path(__file__).with_name("validate_final_report.py")
    specification = importlib.util.spec_from_file_location(
        "knowledge_final_report_validator_for_contract",
        path,
    )
    if specification is None or specification.loader is None:
        raise ComparisonContractError(f"Cannot load Markdown table validator: {path}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    return module


def load_contract(path: Path) -> dict[str, Any]:
    """Load one aggregate comparison contract."""

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ComparisonContractError(f"Cannot read comparison contract: {exc}") from exc
    if not isinstance(payload, dict):
        raise ComparisonContractError("Comparison contract must be a JSON object")
    return payload


def _require_exact_keys(payload: dict[str, Any], expected: set[str], label: str) -> None:
    actual = set(payload)
    if actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        raise ComparisonContractError(
            f"{label} keys differ; missing={missing}, extra={extra}"
        )


def validate_contract(contract: dict[str, Any]) -> None:
    """Validate aggregate scope, metric definitions, and complete alternative rows."""

    _require_exact_keys(contract, TOP_LEVEL_KEYS, "Top-level")
    if contract["schema_version"] != SCHEMA_VERSION:
        raise ComparisonContractError("Unsupported comparison contract schema")
    if not isinstance(contract["report"], str) or not contract["report"].strip():
        raise ComparisonContractError("report must be a non-empty relative path")
    report_path = Path(contract["report"])
    if report_path.is_absolute() or ".." in report_path.parts:
        raise ComparisonContractError("report must be a safe relative path")
    if not isinstance(contract["heading"], str) or not contract["heading"].startswith(
        "## "
    ):
        raise ComparisonContractError("heading must be a level-two Markdown heading")

    scope = contract["dataset_scope"]
    if not isinstance(scope, dict):
        raise ComparisonContractError("dataset_scope must be an object")
    _require_exact_keys(scope, SCOPE_KEYS, "dataset_scope")
    for key, value in scope.items():
        if not isinstance(value, str) or not value.strip():
            raise ComparisonContractError(f"dataset_scope.{key} must not be empty")

    metrics = contract["metrics"]
    if not isinstance(metrics, list) or not metrics:
        raise ComparisonContractError("metrics must be a non-empty array")
    metric_ids: list[str] = []
    metric_labels: set[str] = set()
    for index, metric in enumerate(metrics):
        if not isinstance(metric, dict):
            raise ComparisonContractError(f"metrics[{index}] must be an object")
        _require_exact_keys(metric, METRIC_KEYS, f"metrics[{index}]")
        metric_id = metric["id"]
        label = metric["label"]
        if not isinstance(metric_id, str) or not METRIC_ID_RE.fullmatch(metric_id):
            raise ComparisonContractError(f"Invalid metric id: {metric_id!r}")
        if metric_id in metric_ids:
            raise ComparisonContractError(f"Duplicate metric id: {metric_id}")
        if not isinstance(label, str) or not label.strip():
            raise ComparisonContractError(f"Metric {metric_id} has no label")
        if label in metric_labels:
            raise ComparisonContractError(f"Duplicate metric label: {label}")
        if metric["unit"] not in ALLOWED_UNITS:
            raise ComparisonContractError(f"Metric {metric_id} has an invalid unit")
        if metric["aggregation"] not in ALLOWED_AGGREGATIONS:
            raise ComparisonContractError(
                f"Metric {metric_id} is not an aggregate dataset metric"
            )
        if metric["direction"] not in ALLOWED_DIRECTIONS:
            raise ComparisonContractError(f"Metric {metric_id} has invalid direction")
        precision = metric["display_precision"]
        if isinstance(precision, bool) or not isinstance(precision, int):
            raise ComparisonContractError(
                f"Metric {metric_id} display_precision must be an integer"
            )
        if not 0 <= precision <= 9:
            raise ComparisonContractError(
                f"Metric {metric_id} display_precision is outside 0..9"
            )
        metric_ids.append(metric_id)
        metric_labels.add(label)

    alternatives = contract["alternatives"]
    if not isinstance(alternatives, list) or not alternatives:
        raise ComparisonContractError("alternatives must be a non-empty array")
    alternative_ids: set[str] = set()
    alternative_labels: set[str] = set()
    required_metric_ids = set(metric_ids)
    for index, alternative in enumerate(alternatives):
        if not isinstance(alternative, dict):
            raise ComparisonContractError(f"alternatives[{index}] must be an object")
        _require_exact_keys(alternative, ALTERNATIVE_KEYS, f"alternatives[{index}]")
        alternative_id = alternative["id"]
        label = alternative["label"]
        if (
            not isinstance(alternative_id, str)
            or not ALTERNATIVE_ID_RE.fullmatch(alternative_id)
        ):
            raise ComparisonContractError(f"Invalid alternative id: {alternative_id!r}")
        if alternative_id in alternative_ids:
            raise ComparisonContractError(f"Duplicate alternative id: {alternative_id}")
        if not isinstance(label, str) or not label.strip():
            raise ComparisonContractError(f"Alternative {alternative_id} has no label")
        if label in alternative_labels:
            raise ComparisonContractError(f"Duplicate alternative label: {label}")
        values = alternative["metrics"]
        if not isinstance(values, dict) or set(values) != required_metric_ids:
            raise ComparisonContractError(
                f"Alternative {alternative_id} must provide exactly "
                f"{sorted(required_metric_ids)}"
            )
        for metric_id, value in values.items():
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ComparisonContractError(
                    f"Alternative {alternative_id} metric {metric_id} is not numeric"
                )
            if not math.isfinite(float(value)):
                raise ComparisonContractError(
                    f"Alternative {alternative_id} metric {metric_id} is not finite"
                )
        alternative_ids.add(alternative_id)
        alternative_labels.add(label)


def format_metric(value: int | float, metric: dict[str, Any]) -> str:
    """Format one numeric aggregate exactly as it must appear in Markdown."""

    precision = metric["display_precision"]
    rendered = f"{float(value):.{precision}f}"
    unit = metric["unit"]
    if unit == "percent":
        return f"{rendered}%"
    if unit == "ms":
        return f"{rendered} ms"
    if unit == "seconds":
        return f"{rendered} s"
    if unit == "bytes":
        return f"{rendered} B"
    return rendered


def validate_report_against_contract(
    markdown: str,
    contract: dict[str, Any],
) -> Any:
    """Cross-check a Markdown primary table against the aggregate contract."""

    validate_contract(contract)
    markdown_validator = _load_markdown_validator()
    try:
        table = markdown_validator.validate_report(
            markdown,
            heading=contract["heading"],
        )
    except markdown_validator.ReportFormatError as exc:
        raise ComparisonContractError(str(exc)) from exc

    metric_headers = tuple(metric["label"] for metric in contract["metrics"])
    if table.headers[2:] != metric_headers:
        raise ComparisonContractError(
            f"Markdown metric columns {table.headers[2:]!r} do not match "
            f"contract metrics {metric_headers!r}"
        )
    alternatives = contract["alternatives"]
    if len(table.rows) != len(alternatives):
        raise ComparisonContractError(
            "Markdown alternative count does not match comparison contract"
        )
    for position, (row, alternative) in enumerate(
        zip(table.rows, alternatives, strict=True),
        start=1,
    ):
        expected = (
            str(position),
            alternative["label"],
            *(
                format_metric(alternative["metrics"][metric["id"]], metric)
                for metric in contract["metrics"]
            ),
        )
        if row != expected:
            raise ComparisonContractError(
                f"Markdown row {position} differs from aggregate contract; "
                f"expected={expected!r}, actual={row!r}"
            )
    return table


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("contract", type=Path, help="Comparison contract JSON")
    parser.add_argument(
        "--report",
        type=Path,
        help="Markdown report override; defaults to contract-relative report",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Validate one contract and its Markdown projection."""

    args = build_parser().parse_args(argv)
    contract_path = args.contract.resolve()
    try:
        contract = load_contract(contract_path)
        report_path = (
            args.report.resolve()
            if args.report is not None
            else (contract_path.parent / contract.get("report", "")).resolve()
        )
        markdown = report_path.read_text(encoding="utf-8")
        table = validate_report_against_contract(markdown, contract)
    except (OSError, UnicodeError, ComparisonContractError) as exc:
        raise SystemExit(f"Comparison contract validation failed: {exc}") from exc
    print(
        "Final report comparison contract passed: "
        f"{len(table.rows)} alternatives, {len(table.headers) - 2} "
        "aggregate dataset metrics."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
