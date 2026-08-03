#!/usr/bin/env python3
"""Freeze an ordered set of existing expert directories by complete tree digest."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Sequence


SCHEMA_VERSION = "graphrag-generalization-candidate-selection/1.0"


class FreezeError(ValueError):
    """Describe an invalid candidate selection."""


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _inventory(root: Path) -> list[dict[str, Any]]:
    rows = []
    for path in sorted(
        root.rglob("*"),
        key=lambda item: item.relative_to(root).as_posix(),
    ):
        if path.is_symlink():
            raise FreezeError(f"Candidate contains a symlink: {path}")
        if path.is_file():
            rows.append(
                {
                    "path": path.relative_to(root).as_posix(),
                    "bytes": path.stat().st_size,
                    "sha256": _sha256(path),
                }
            )
    if not rows:
        raise FreezeError(f"Candidate is empty: {root}")
    return rows


def _tree_digest(rows: Sequence[dict[str, Any]]) -> str:
    return hashlib.sha256(
        json.dumps(
            rows,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    ).hexdigest()


def freeze(specs: Sequence[str]) -> dict[str, Any]:
    """Create the exact candidate selection payload."""

    candidates = []
    seen: set[str] = set()
    for spec in specs:
        parts = spec.split("=", 1)
        if len(parts) != 2 or not parts[0] or not parts[1]:
            raise FreezeError(f"Invalid candidate specification: {spec}")
        candidate_id, raw_path = parts
        if candidate_id in seen:
            raise FreezeError(f"Duplicate candidate id: {candidate_id}")
        seen.add(candidate_id)
        path = Path(raw_path).resolve()
        if not path.is_dir():
            raise FreezeError(f"Candidate directory is absent: {path}")
        manifest = path / "expert-manifest.json"
        if not manifest.is_file():
            raise FreezeError(f"Candidate manifest is absent: {manifest}")
        manifest_payload = json.loads(manifest.read_text(encoding="utf-8"))
        if not isinstance(manifest_payload, dict):
            raise FreezeError(f"Candidate manifest is invalid: {manifest}")
        inventory = _inventory(path)
        candidates.append(
            {
                "candidate_id": candidate_id,
                "path": str(path),
                "skill_name": manifest_payload.get("skill_name"),
                "manifest_schema": manifest_payload.get("schema_version"),
                "manifest_sha256": _sha256(manifest),
                "tree_sha256": _tree_digest(inventory),
                "file_count": len(inventory),
                "byte_count": sum(row["bytes"] for row in inventory),
            }
        )
    if len(candidates) < 2:
        raise FreezeError("At least two candidates are required")
    return {
        "schema_version": SCHEMA_VERSION,
        "selection_id": "post-v51-frozen-expert-lineage-v1",
        "selection_rule": (
            "All seven pre-existing comparable expert packages were selected "
            "before release; no new-question metric was available."
        ),
        "mutation_after_selection_allowed": False,
        "candidates": candidates,
    }


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", action="append", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Write or check the frozen selection."""

    args = build_parser().parse_args(argv)
    try:
        payload = freeze(args.candidate)
        rendered = json.dumps(
            payload,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
            allow_nan=False,
        ) + "\n"
        output = args.output.resolve()
        if args.check:
            if not output.is_file() or output.read_text(encoding="utf-8") != rendered:
                raise FreezeError(f"Candidate selection drifted: {output}")
        else:
            if output.exists():
                raise FreezeError(f"Refusing to replace selection: {output}")
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(rendered, encoding="utf-8", newline="\n")
    except (FreezeError, OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, sort_keys=True))
        return 2
    print(json.dumps({"status": "pass", "candidates": len(payload["candidates"])}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
