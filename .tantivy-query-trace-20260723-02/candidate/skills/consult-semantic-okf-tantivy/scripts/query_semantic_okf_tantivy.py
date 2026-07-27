#!/usr/bin/env python3
"""Inspect or search a classical Semantic OKF snapshot through Tantivy."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from _tantivy_snapshot import (
    SnapshotError,
    inspect_snapshot,
    load_snapshot,
    search_snapshot,
)


def _configure_utf8() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            try:
                reconfigure(encoding="utf-8")
            except (AttributeError, OSError, ValueError):
                pass


def build_parser() -> argparse.ArgumentParser:
    """Build the read-only Tantivy consultation parser."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "bundle", type=Path, help="Published classical Semantic OKF bundle"
    )
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser(
        "inspect", help="Validate and describe the Tantivy query surface"
    )
    search = commands.add_parser("search", help="Retrieve exact evidence passages")
    search.add_argument("--query", required=True, help="Tantivy query string")
    search.add_argument("--top-k", type=int, default=10)
    search.add_argument("--source-id", action="append", default=[])
    search.add_argument("--concept-id", action="append", default=[])
    search.add_argument("--concept-type", action="append", default=[])
    return parser


def main(argv: list[str] | None = None) -> int:
    """Validate the supplied snapshot and execute one read-only operation."""

    _configure_utf8()
    args = build_parser().parse_args(argv)
    try:
        snapshot = load_snapshot(args.bundle)
        if args.command == "inspect":
            result = inspect_snapshot(snapshot)
        else:
            result = search_snapshot(
                snapshot,
                args.query,
                args.top_k,
                source_ids=args.source_id,
                concept_ids=args.concept_id,
                concept_types=args.concept_type,
            )
    except (
        SnapshotError,
        OSError,
        UnicodeError,
        ValueError,
        TypeError,
        KeyError,
        IndexError,
    ) as exc:
        print(
            json.dumps(
                {"status": "error", "code": "tantivy-error", "error": str(exc)},
                ensure_ascii=False,
                sort_keys=True,
            )
        )
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
