#!/usr/bin/env python3
"""Query a validated Semantic OKF Graphify snapshot without modifying it."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from _graphify_snapshot import Snapshot, SnapshotError, snapshot_sha256


def _configure_utf8_output() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(encoding="utf-8", errors="strict")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("snapshot", type=Path, help="Published Semantic OKF bundle.")
    parser.add_argument("--format", choices=("json", "paths"), default="json")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("verify", help="Validate the complete core/projection binding.")

    exact = subparsers.add_parser("records", help="Look up one exact authoritative record.")
    exact.add_argument("--source-id", required=True)
    exact.add_argument("--record-id", required=True)
    exact.add_argument("--show-content", action="store_true")

    search = subparsers.add_parser("search", help="Run Graphify scoring and BFS discovery.")
    search.add_argument("question")
    search.add_argument("--depth", type=int, default=2)
    search.add_argument("--top-k", type=int, default=10)
    search.add_argument("--show-content", action="store_true")

    read = subparsers.add_parser("read", help="Open one authoritative concept path.")
    read.add_argument("concept_path")

    subparsers.add_parser(
        "aggregate", help="Group authoritative ledger records by source and type."
    )
    return parser


def _emit(payload: dict[str, object], output_format: str) -> None:
    if output_format == "paths":
        records = payload.get("records")
        if isinstance(records, list):
            for record in records:
                if isinstance(record, dict) and record.get("concept_path"):
                    print(record["concept_path"])
        return
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))


def main(argv: list[str] | None = None) -> int:
    _configure_utf8_output()
    args = build_parser().parse_args(argv)
    try:
        before = snapshot_sha256(args.snapshot.expanduser().resolve())
        snapshot = Snapshot(args.snapshot)
        if args.command == "verify":
            payload = snapshot.verify()
        elif args.command == "records":
            payload = snapshot.exact(
                args.source_id, args.record_id, show_content=args.show_content
            )
        elif args.command == "search":
            payload = snapshot.search(
                args.question,
                depth=args.depth,
                top_k=args.top_k,
                show_content=args.show_content,
            )
        elif args.command == "read":
            payload = snapshot.read(args.concept_path)
        else:
            payload = snapshot.aggregate()
        after = snapshot_sha256(args.snapshot.expanduser().resolve())
        if before != after:
            raise SnapshotError("published snapshot bytes changed during consultation")
        payload = {**payload, "read_only_sha256": after}
    except (
        SnapshotError,
        OSError,
        UnicodeError,
        ValueError,
        KeyError,
        TypeError,
        AttributeError,
    ) as exc:
        print(
            json.dumps(
                {"status": "error", "code": "invalid-snapshot-or-query", "error": str(exc)},
                ensure_ascii=False,
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 2
    _emit(payload, args.format)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
