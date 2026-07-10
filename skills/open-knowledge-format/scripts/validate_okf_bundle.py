#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

import yaml


OKF_VERSION = "0.1"
DATE_HEADING_RE = re.compile(r"^##\s+(\d{4}-\d{2}-\d{2})\s*$")
INDEX_ENTRY_RE = re.compile(r"^\*\s+\[[^\]]+\]\([^)]+\)(?:\s+-\s+.+)?\s*$")


@dataclass(frozen=True)
class ValidationError:
    """A single OKF validation problem."""

    path: Path
    message: str


@dataclass(frozen=True)
class _ParsedFrontmatter:
    payload: dict[str, Any]
    body: str
    present: bool
    error: str | None = None


def split_frontmatter(text: str) -> tuple[dict[str, Any], str, bool]:
    """Return YAML frontmatter, Markdown body, and whether a valid block exists."""
    parsed = _parse_frontmatter(text)
    if parsed.error:
        return {}, text, False
    return parsed.payload, parsed.body, parsed.present


def validate_bundle(bundle_root: Path) -> list[ValidationError]:
    """Validate a directory tree against the normative OKF v0.1 rules."""
    errors: list[ValidationError] = []
    if not bundle_root.exists() or not bundle_root.is_dir():
        return [ValidationError(bundle_root, "bundle root must be an existing directory")]

    markdown_files = sorted(
        path for path in bundle_root.rglob("*") if path.is_file() and path.suffix.lower() == ".md"
    )
    for path in markdown_files:
        rel = path.relative_to(bundle_root)
        try:
            text = path.read_bytes().decode("utf-8-sig")
        except UnicodeDecodeError as exc:
            errors.append(ValidationError(path, f"document must be valid UTF-8: {exc}"))
            continue
        if path.name == "index.md":
            errors.extend(_validate_index(path, rel, text))
            continue
        if path.name == "log.md":
            errors.extend(_validate_log(path, text))
            continue
        errors.extend(_validate_concept(path, text))
    return errors


def _parse_frontmatter(text: str) -> _ParsedFrontmatter:
    normalized = text.removeprefix("\ufeff")
    lines = normalized.splitlines()
    if not lines or lines[0] != "---":
        return _ParsedFrontmatter({}, normalized, False)
    try:
        end_index = lines.index("---", 1)
    except ValueError:
        return _ParsedFrontmatter({}, normalized, True, "unterminated YAML frontmatter block")
    raw_frontmatter = "\n".join(lines[1:end_index])
    try:
        payload = yaml.safe_load(raw_frontmatter)
    except yaml.YAMLError as exc:
        return _ParsedFrontmatter({}, normalized, True, f"invalid YAML frontmatter: {exc}")
    if not isinstance(payload, dict):
        return _ParsedFrontmatter({}, normalized, True, "YAML frontmatter must be a mapping")
    body = "\n".join(lines[end_index + 1 :]).lstrip("\n")
    return _ParsedFrontmatter(payload, body, True)


def _validate_concept(path: Path, text: str) -> list[ValidationError]:
    parsed = _parse_frontmatter(text)
    if not parsed.present:
        return [ValidationError(path, "concept document must start with YAML frontmatter")]
    if parsed.error:
        return [ValidationError(path, parsed.error)]
    concept_type = parsed.payload.get("type")
    if not isinstance(concept_type, str) or not concept_type.strip():
        return [ValidationError(path, "concept frontmatter must include a non-empty top-level 'type'")]
    return []


def _validate_index(path: Path, rel: Path, text: str) -> list[ValidationError]:
    errors: list[ValidationError] = []
    parsed = _parse_frontmatter(text)
    if parsed.present and parsed.error:
        return [ValidationError(path, parsed.error)]
    if parsed.present and rel.parts != ("index.md",):
        errors.append(ValidationError(path, "only the bundle-root index.md may declare frontmatter"))
    if parsed.present and rel.parts == ("index.md",):
        version = parsed.payload.get("okf_version")
        if str(version) != OKF_VERSION:
            errors.append(ValidationError(path, f"root index.md frontmatter must declare okf_version: '{OKF_VERSION}'"))
        unexpected = set(parsed.payload) - {"okf_version"}
        if unexpected:
            fields = ", ".join(sorted(str(field) for field in unexpected))
            errors.append(ValidationError(path, f"root index.md frontmatter has unsupported fields: {fields}"))
    body = parsed.body if parsed.present and not parsed.error else text
    errors.extend(_validate_index_body(path, body))
    return errors


def _validate_index_body(path: Path, body: str) -> list[ValidationError]:
    errors: list[ValidationError] = []
    has_section = False
    for line_number, raw_line in enumerate(body.splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("# "):
            has_section = True
            continue
        if INDEX_ENTRY_RE.match(line):
            if not has_section:
                errors.append(ValidationError(path, f"index entry on line {line_number} must follow a section heading"))
            continue
        errors.append(
            ValidationError(
                path,
                f"index line {line_number} must be a level-one section heading or '* [Title](target)' entry",
            )
        )
    return errors


def _validate_log(path: Path, text: str) -> list[ValidationError]:
    parsed = _parse_frontmatter(text)
    if parsed.present:
        message = parsed.error or "log.md must not contain YAML frontmatter"
        return [ValidationError(path, message)]

    errors: list[ValidationError] = []
    previous_date: date | None = None
    has_title = False
    has_date = False
    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("# ") and not has_title and not has_date:
            has_title = True
            continue
        if line.startswith("## "):
            match = DATE_HEADING_RE.match(line)
            if not match:
                errors.append(ValidationError(path, f"log date heading on line {line_number} must use YYYY-MM-DD"))
                continue
            try:
                current_date = date.fromisoformat(match.group(1))
            except ValueError:
                errors.append(ValidationError(path, f"log date heading on line {line_number} is not a real date"))
                continue
            if previous_date is not None and current_date > previous_date:
                errors.append(ValidationError(path, f"log date heading on line {line_number} must be newest first"))
            previous_date = current_date
            has_date = True
            continue
        if line.startswith("* ") and has_date:
            continue
        errors.append(
            ValidationError(path, f"log line {line_number} must be a title, ISO date heading, or dated list entry")
        )
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate an Open Knowledge Format v0.1 bundle.")
    parser.add_argument("bundle_root", type=Path)
    args = parser.parse_args(argv)

    errors = validate_bundle(args.bundle_root)
    if errors:
        for error in errors:
            print(f"{error.path}: {error.message}", file=sys.stderr)
        return 1
    print(f"OKF validation passed: {args.bundle_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
