#!/usr/bin/env python3
"""Merge successful narrow retries into an immutable Skill Arena result copy."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "semantic-okf-skill-arena-retry-merge/1.0"
QUESTION_RE = re.compile(r"Set\s+`?question_id`?\s+to\s+`([^`]+)`")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _rows(value: dict[str, Any], path: Path) -> list[dict[str, Any]]:
    rows = value.get("results", {}).get("results")
    if not isinstance(rows, list):
        raise ValueError(f"Missing Promptfoo result rows: {path}")
    return rows


def _provider_id(row: dict[str, Any]) -> str:
    provider = row.get("provider")
    if isinstance(provider, dict):
        provider = provider.get("id")
    if not isinstance(provider, str) or not provider:
        raise ValueError("Promptfoo row has no provider id")
    return provider


def _prompt_question_id(row: dict[str, Any]) -> str:
    variables = row.get("vars")
    prompt = variables.get("taskPrompt") if isinstance(variables, dict) else None
    if not isinstance(prompt, str):
        raise ValueError("Promptfoo row has no taskPrompt variable")
    match = QUESTION_RE.search(prompt)
    if match is None:
        raise ValueError("Promptfoo taskPrompt has no question_id instruction")
    return match.group(1)


def _key(row: dict[str, Any]) -> tuple[str, str]:
    return _provider_id(row), _prompt_question_id(row)


def _usable(row: dict[str, Any]) -> bool:
    output = row.get("response", {}).get("output")
    if not isinstance(output, str):
        return False
    try:
        value = json.loads(output)
    except json.JSONDecodeError:
        return False
    return isinstance(value, dict) and value.get("question_id") == _prompt_question_id(row)


def merge(primary: Path, retries: list[Path]) -> tuple[dict[str, Any], dict[str, Any]]:
    primary_value = json.loads(primary.read_text(encoding="utf-8"))
    merged = copy.deepcopy(primary_value)
    primary_rows = _rows(merged, primary)
    keys = [_key(row) for row in primary_rows]
    if len(set(keys)) != len(keys):
        raise ValueError("Primary result contains duplicate provider/question cells")

    candidates: dict[tuple[str, str], list[tuple[Path, int, dict[str, Any]]]] = {}
    retry_inputs = []
    for retry in retries:
        retry_value = json.loads(retry.read_text(encoding="utf-8"))
        retry_rows = _rows(retry_value, retry)
        retry_inputs.append({"path": retry.as_posix(), "sha256": _sha256(retry), "row_count": len(retry_rows)})
        for index, row in enumerate(retry_rows):
            if _usable(row):
                candidates.setdefault(_key(row), []).append((retry, index, row))

    replacements = []
    unresolved = []
    for index, (key, row) in enumerate(zip(keys, primary_rows, strict=True)):
        if _usable(row):
            continue
        available = candidates.get(key, [])
        if not available:
            unresolved.append({"provider": key[0], "question_id": key[1], "primary_row": index})
            continue
        retry_path, retry_index, retry_row = available[0]
        primary_rows[index] = copy.deepcopy(retry_row)
        replacements.append(
            {
                "provider": key[0],
                "question_id": key[1],
                "primary_row": index,
                "retry_path": retry_path.as_posix(),
                "retry_row": retry_index,
            }
        )

    if unresolved:
        cells = ", ".join(f"{item['provider']}/{item['question_id']}" for item in unresolved)
        raise ValueError(f"No successful retry for unresolved cells: {cells}")
    if not all(_usable(row) for row in primary_rows):
        raise AssertionError("Merged result still contains an unusable row")

    manifest = {
        "schema_version": SCHEMA_VERSION,
        "primary": {
            "path": primary.as_posix(),
            "sha256": _sha256(primary),
            "row_count": len(primary_rows),
        },
        "retries": retry_inputs,
        "replacement_count": len(replacements),
        "replacements": replacements,
        "final_usable_row_count": len(primary_rows),
    }
    merged["semanticOkfRetryMerge"] = manifest
    return merged, manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--primary", type=Path, required=True)
    parser.add_argument("--retry", type=Path, action="append", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() or args.manifest.exists():
        raise FileExistsError("Output and manifest paths must be absent for append-only publication")
    merged, manifest = merge(args.primary, args.retry)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(merged, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    args.manifest.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n"
    )
    print(json.dumps({"status": "pass", "replacements": manifest["replacement_count"], "rows": manifest["final_usable_row_count"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
