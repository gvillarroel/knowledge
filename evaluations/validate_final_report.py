"""Validate the primary comparison table in a final evaluation report."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import re
from typing import Sequence


DEFAULT_HEADING = "## Direct comparison"
FORBIDDEN_CONCLUSION_TERMS = {
    "acceptance",
    "decision",
    "outcome",
    "promotion",
    "state",
    "status",
}
MISSING_VALUES = {"", "-", "—", "n/a", "na", "none", "null"}
IDENTITY_HEADER = "Pair / strategy"


class ReportFormatError(ValueError):
    """Raised when a final report violates the primary-table contract."""


@dataclass(frozen=True)
class ComparisonTable:
    """Represent the parsed header and rows of a Markdown comparison table."""

    headers: tuple[str, ...]
    rows: tuple[tuple[str, ...], ...]


def _parse_markdown_row(line: str) -> tuple[str, ...]:
    stripped = line.strip()
    if not stripped.startswith("|") or not stripped.endswith("|"):
        raise ReportFormatError(f"Expected a Markdown table row, found: {line!r}")
    return tuple(cell.strip() for cell in stripped[1:-1].split("|"))


def _is_separator(cells: Sequence[str]) -> bool:
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells)


def extract_primary_table(
    markdown: str,
    *,
    heading: str = DEFAULT_HEADING,
) -> ComparisonTable:
    """Extract the first Markdown table following the final-report heading."""

    lines = markdown.splitlines()
    try:
        heading_index = lines.index(heading)
    except ValueError as exc:
        raise ReportFormatError(f"Missing primary comparison heading: {heading}") from exc

    table_start = None
    for index in range(heading_index + 1, len(lines)):
        if lines[index].lstrip().startswith("|"):
            table_start = index
            break
        if lines[index].startswith("## "):
            break
    if table_start is None:
        raise ReportFormatError(f"No Markdown table follows {heading}")

    headers = _parse_markdown_row(lines[table_start])
    if table_start + 1 >= len(lines):
        raise ReportFormatError("Primary comparison table has no separator row")
    separator = _parse_markdown_row(lines[table_start + 1])
    if len(separator) != len(headers) or not _is_separator(separator):
        raise ReportFormatError("Primary comparison table has an invalid separator row")

    rows: list[tuple[str, ...]] = []
    for line in lines[table_start + 2 :]:
        if not line.lstrip().startswith("|"):
            break
        rows.append(_parse_markdown_row(line))
    if not rows:
        raise ReportFormatError("Primary comparison table has no measured rows")
    return ComparisonTable(headers=headers, rows=tuple(rows))


def validate_primary_table(table: ComparisonTable) -> None:
    """Validate identity, metric, completeness, and ordering requirements."""

    if len(table.headers) < 3:
        raise ReportFormatError(
            "Primary comparison table needs position, identity, and at least one metric"
        )
    if table.headers[0] != "Pos.":
        raise ReportFormatError("Primary comparison table must start with 'Pos.'")
    if table.headers[1] != IDENTITY_HEADER:
        raise ReportFormatError(
            f"Primary comparison table must use {IDENTITY_HEADER!r} "
            "as its identity column"
        )

    for header in table.headers[2:]:
        normalized_words = set(re.findall(r"[a-z]+", header.casefold()))
        forbidden = normalized_words & FORBIDDEN_CONCLUSION_TERMS
        if forbidden:
            term = sorted(forbidden)[0]
            raise ReportFormatError(
                f"Primary comparison columns must be dataset metrics, not {term!r}"
            )
        if not header.strip():
            raise ReportFormatError("Metric headers must not be empty")

    seen_identities: set[str] = set()
    for expected_position, row in enumerate(table.rows, start=1):
        if len(row) != len(table.headers):
            raise ReportFormatError(
                f"Row {expected_position} has {len(row)} cells; "
                f"expected {len(table.headers)}"
            )
        if row[0] != str(expected_position):
            raise ReportFormatError(
                f"Expected sequential position {expected_position}, found {row[0]!r}"
            )
        identity = row[1]
        if not identity:
            raise ReportFormatError(
                f"Row {expected_position} has no pair or strategy"
            )
        if identity in seen_identities:
            raise ReportFormatError(f"Duplicate pair or strategy: {identity}")
        seen_identities.add(identity)

        for header, value in zip(table.headers[2:], row[2:], strict=True):
            if value.casefold() in MISSING_VALUES:
                raise ReportFormatError(
                    f"{identity} is missing the displayed metric {header!r}"
                )
            if not re.search(r"\d", value):
                raise ReportFormatError(
                    f"{identity} has a non-measured value for {header!r}: {value!r}"
                )


def validate_report(markdown: str, *, heading: str = DEFAULT_HEADING) -> ComparisonTable:
    """Extract and validate a final report's primary comparison table."""

    table = extract_primary_table(markdown, heading=heading)
    validate_primary_table(table)
    return table


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser for final-report validation."""

    parser = argparse.ArgumentParser(
        description="Validate the metric-only primary table in a final report."
    )
    parser.add_argument("report", type=Path, help="Markdown final report to validate")
    parser.add_argument(
        "--heading",
        default=DEFAULT_HEADING,
        help=f"Heading that introduces the primary table (default: {DEFAULT_HEADING!r})",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Validate one report and return a process exit code."""

    args = build_parser().parse_args(argv)
    try:
        table = validate_report(
            args.report.read_text(encoding="utf-8"),
            heading=args.heading,
        )
    except (OSError, ReportFormatError) as exc:
        raise SystemExit(f"Final report validation failed: {exc}") from exc
    print(
        "Final report primary table passed: "
        f"{len(table.rows)} rows, {len(table.headers) - 2} dataset metrics."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
