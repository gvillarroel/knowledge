#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


DATE_HEADING_RE = re.compile(r"^##\s+\d{4}-\d{2}-\d{2}\s*$")


@dataclass
class ValidationError:
    """A single OKF validation problem."""

    path: Path
    message: str


def split_frontmatter(text: str) -> tuple[dict[str, Any], str, bool]:
    """Return YAML frontmatter, Markdown body, and whether frontmatter exists."""
    if not text.startswith("---\n"):
        return {}, text, False
    marker = "\n---\n"
    end_index = text.find(marker, 4)
    if end_index == -1:
        return {}, text, False
    raw_frontmatter = text[4:end_index]
    body = text[end_index + len(marker):]
    try:
        payload = yaml.safe_load(raw_frontmatter)
    except yaml.YAMLError:
        return {}, text, False
    if not isinstance(payload, dict):
        return {}, text, False
    return payload, body.lstrip("\n"), True


def validate_bundle(bundle_root: Path) -> list[ValidationError]:
    """Validate a directory tree against OKF v0.1 conformance rules."""
    errors: list[ValidationError] = []
    if not bundle_root.exists() or not bundle_root.is_dir():
        return [ValidationError(bundle_root, "bundle root must be an existing directory")]

    for path in sorted(bundle_root.rglob("*.md")):
        rel = path.relative_to(bundle_root)
        text = path.read_text(encoding="utf-8", errors="replace")
        if path.name == "index.md":
            errors.extend(_validate_index(path, rel, text))
            continue
        if path.name == "log.md":
            errors.extend(_validate_log(path, text))
            continue
        errors.extend(_validate_concept(path, text))
    return errors


def _validate_concept(path: Path, text: str) -> list[ValidationError]:
    frontmatter, _body, has_frontmatter = split_frontmatter(text)
    if not has_frontmatter:
        return [ValidationError(path, "concept document must start with parseable YAML frontmatter")]
    concept_type = frontmatter.get("type")
    if not isinstance(concept_type, str) or not concept_type.strip():
        return [ValidationError(path, "concept frontmatter must include a non-empty top-level 'type'")]
    return []


def _validate_index(path: Path, rel: Path, text: str) -> list[ValidationError]:
    frontmatter, _body, has_frontmatter = split_frontmatter(text)
    if has_frontmatter and rel.parts != ("index.md",):
        return [ValidationError(path, "only the bundle-root index.md may declare frontmatter")]
    if has_frontmatter:
        version = frontmatter.get("okf_version")
        if version is not None and str(version) != "0.1":
            return [ValidationError(path, "root index.md okf_version should be '0.1'")]
    return []


def _validate_log(path: Path, text: str) -> list[ValidationError]:
    errors: list[ValidationError] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        if line.startswith("## ") and not DATE_HEADING_RE.match(line):
            errors.append(ValidationError(path, f"log date heading on line {line_number} must use YYYY-MM-DD"))
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
