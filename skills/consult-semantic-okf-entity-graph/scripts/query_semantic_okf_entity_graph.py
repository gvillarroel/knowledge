#!/usr/bin/env python3
"""Inspect or query a Semantic OKF entity-section graph read-only."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from _entity_graph_snapshot import SnapshotError, inspect_snapshot, load_snapshot, search_snapshot


def _configure_utf8() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    """Build the read-only entity-graph consultation parser."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle", type=Path, help="Published entity-graph Semantic OKF bundle")
    commands = parser.add_subparsers(dest="command", required=True)
    inspect = commands.add_parser("inspect", help="Validate and describe the graph projection")
    inspect.add_argument("--deep-validation", action="store_true", help="rederive all graph artifacts in memory")
    search = commands.add_parser("search", help="retrieve exact entity-linked source sections")
    search.add_argument("--query", required=True)
    search.add_argument("--mode", choices=("lexical", "entity", "traversal", "fusion"), default="fusion")
    search.add_argument("--top-k", type=int, default=10)
    search.add_argument("--source-id", action="append", default=[])
    search.add_argument("--paper-id", action="append", default=[])
    search.add_argument("--document-id", action="append", default=[])
    search.add_argument("--record-id", action="append", default=[])
    return parser


def main(argv: list[str] | None = None) -> int:
    """Validate the snapshot and execute one non-mutating operation."""

    _configure_utf8()
    args = build_parser().parse_args(argv)
    try:
        snapshot = load_snapshot(args.bundle, deep_validation=bool(getattr(args, "deep_validation", False)))
        if args.command == "inspect":
            result = inspect_snapshot(snapshot)
        else:
            result = search_snapshot(
                snapshot,
                args.query,
                args.mode,
                args.top_k,
                source_ids=args.source_id,
                paper_ids=args.paper_id,
                document_ids=args.document_id,
                record_ids=args.record_id,
            )
    except (SnapshotError, OSError, UnicodeError, ValueError, TypeError, KeyError, IndexError) as exc:
        print(json.dumps({"status": "error", "code": "entity-graph-error", "error": str(exc)}, ensure_ascii=False, sort_keys=True))
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
