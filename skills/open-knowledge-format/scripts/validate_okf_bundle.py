#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any

import yaml


OKF_VERSION = "0.2"
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
    """Validate a directory tree against the normative OKF v0.2 rules."""
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
    return _validate_v02_families(path, parsed.payload)


def _validate_v02_families(path: Path, payload: dict[str, Any]) -> list[ValidationError]:
    """Validate optional OKF v0.2 provenance, trust, lifecycle, and computation fields."""

    errors: list[ValidationError] = []
    generated = payload.get("generated")
    if generated is not None:
        if not isinstance(generated, dict):
            errors.append(ValidationError(path, "'generated' must be a mapping"))
        else:
            _validate_actor_field(errors, path, generated.get("by"), "generated.by")
            if "at" in generated and not _is_iso_datetime(generated["at"]):
                errors.append(ValidationError(path, "'generated.at' must be an ISO 8601 datetime"))

    verified = payload.get("verified")
    if verified is not None:
        events = [verified] if isinstance(verified, dict) else verified
        if not isinstance(events, list) or not events:
            errors.append(ValidationError(path, "'verified' must be a mapping or non-empty list"))
        else:
            for index, event in enumerate(events):
                label = f"verified[{index}]"
                if not isinstance(event, dict):
                    errors.append(ValidationError(path, f"'{label}' must be a mapping"))
                    continue
                _validate_actor_field(errors, path, event.get("by"), f"{label}.by")
                if not _is_iso_datetime(event.get("at")):
                    errors.append(ValidationError(path, f"'{label}.at' must be an ISO 8601 datetime"))

    sources = payload.get("sources")
    if sources is not None:
        if not isinstance(sources, list) or not sources:
            errors.append(ValidationError(path, "'sources' must be a non-empty list"))
        else:
            for index, source in enumerate(sources):
                label = f"sources[{index}]"
                if not isinstance(source, dict):
                    errors.append(ValidationError(path, f"'{label}' must be a mapping"))
                    continue
                if not _non_empty_string(source.get("resource")):
                    errors.append(ValidationError(path, f"'{label}.resource' must be a non-empty string"))
                for field in ("id", "title", "author"):
                    if field in source and not _non_empty_string(source[field]):
                        errors.append(ValidationError(path, f"'{label}.{field}' must be a non-empty string"))
                if "usage_count" in source and (
                    not isinstance(source["usage_count"], int)
                    or isinstance(source["usage_count"], bool)
                    or source["usage_count"] < 0
                ):
                    errors.append(ValidationError(path, f"'{label}.usage_count' must be a non-negative integer"))
                if "last_modified" in source and not _is_iso_date(source["last_modified"]):
                    errors.append(ValidationError(path, f"'{label}.last_modified' must use YYYY-MM-DD"))
                if "usage_window" in source:
                    _validate_usage_window(errors, path, source["usage_window"], f"{label}.usage_window")

    if "usage_window" in payload:
        _validate_usage_window(errors, path, payload["usage_window"], "usage_window")

    status = payload.get("status")
    if status is not None and status not in {"draft", "stable", "deprecated"}:
        errors.append(ValidationError(path, "'status' must be draft, stable, or deprecated"))
    if "stale_after" in payload and not _is_iso_date(payload["stale_after"]):
        errors.append(ValidationError(path, "'stale_after' must use YYYY-MM-DD"))

    if payload.get("type") == "Attested Computation":
        errors.extend(_validate_attested_computation(path, payload))
    return errors


def _validate_attested_computation(
    path: Path,
    payload: dict[str, Any],
) -> list[ValidationError]:
    errors: list[ValidationError] = []
    if not _non_empty_string(payload.get("runtime")):
        errors.append(ValidationError(path, "Attested Computation requires a non-empty 'runtime'"))
    if "computation" in payload and not _non_empty_string(payload["computation"]):
        errors.append(ValidationError(path, "'computation' must be a non-empty path or URI"))
    if "parameters" in payload:
        parameters = payload["parameters"]
        if not isinstance(parameters, list):
            errors.append(ValidationError(path, "'parameters' must be a list"))
        else:
            for index, parameter in enumerate(parameters):
                label = f"parameters[{index}]"
                if not isinstance(parameter, dict):
                    errors.append(ValidationError(path, f"'{label}' must be a mapping"))
                    continue
                if not _non_empty_string(parameter.get("name")):
                    errors.append(ValidationError(path, f"'{label}.name' must be a non-empty string"))
                if not _non_empty_string(parameter.get("type")):
                    errors.append(ValidationError(path, f"'{label}.type' must be a non-empty string"))
                if not isinstance(parameter.get("required"), bool):
                    errors.append(ValidationError(path, f"'{label}.required' must be boolean"))
    for field in ("executor", "attester"):
        contract = payload.get(field)
        if contract is None:
            continue
        if not isinstance(contract, dict):
            errors.append(ValidationError(path, f"'{field}' must be a mapping"))
        elif not _non_empty_string(contract.get("resource")):
            errors.append(ValidationError(path, f"'{field}.resource' must be a non-empty string"))
    executor = payload.get("executor")
    if isinstance(executor, dict) and "receipt" in executor:
        receipt = executor["receipt"]
        if not isinstance(receipt, list) or not receipt or not all(_non_empty_string(item) for item in receipt):
            errors.append(ValidationError(path, "'executor.receipt' must be a non-empty list of field names"))
    return errors


def _validate_actor_field(
    errors: list[ValidationError],
    path: Path,
    value: Any,
    label: str,
) -> None:
    if not _non_empty_string(value):
        errors.append(ValidationError(path, f"'{label}' must be a non-empty actor string"))
        return
    actor = value.strip()
    if actor.startswith(("human:", "process:")):
        valid = bool(actor.split(":", 1)[1])
    else:
        producer, separator, version = actor.partition("/")
        valid = bool(separator and producer and version)
    if not valid or any(character.isspace() for character in actor):
        errors.append(
            ValidationError(
                path,
                f"'{label}' must use <producer>/<version>, human:<id>, or process:<id>",
            )
        )


def _validate_usage_window(
    errors: list[ValidationError],
    path: Path,
    value: Any,
    label: str,
) -> None:
    if not isinstance(value, dict) or set(value) != {"from", "to"}:
        errors.append(ValidationError(path, f"'{label}' must contain exactly 'from' and 'to' dates"))
        return
    if not _is_iso_date(value["from"]) or not _is_iso_date(value["to"]):
        errors.append(ValidationError(path, f"'{label}' dates must use YYYY-MM-DD"))


def _non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _is_iso_date(value: Any) -> bool:
    if isinstance(value, datetime):
        return False
    if isinstance(value, date):
        return True
    if not isinstance(value, str):
        return False
    try:
        return date.fromisoformat(value) == date.fromisoformat(value.strip())
    except ValueError:
        return False


def _is_iso_datetime(value: Any) -> bool:
    if isinstance(value, datetime):
        return True
    if not isinstance(value, str) or "T" not in value:
        return False
    try:
        datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError:
        return False
    return True


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
    parser = argparse.ArgumentParser(description="Validate an Open Knowledge Format v0.2 bundle.")
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
