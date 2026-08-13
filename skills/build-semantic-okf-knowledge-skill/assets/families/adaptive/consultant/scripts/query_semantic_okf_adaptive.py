#!/usr/bin/env python3
"""Inspect or search an adaptive Semantic OKF snapshot read-only."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from _adaptive_snapshot import (
    SnapshotError,
    build_coverage_pack,
    build_evidence_pack,
    finalize_answer,
    inspect_snapshot,
    load_snapshot,
    search_snapshot,
)


def _configure_utf8() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    """Build the read-only adaptive consultation parser."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle", type=Path, help="Published adaptive Semantic OKF bundle")
    commands = parser.add_subparsers(dest="command", required=True)
    inspect = commands.add_parser("inspect", help="Validate and describe the adaptive projection")
    inspect.add_argument(
        "--deep-validation",
        action="store_true",
        help="independently rederive BM25, PPMI, topic, and document artifacts before inspection",
    )
    search = commands.add_parser("search", help="Retrieve exact evidence passages")
    search.add_argument("--query", required=True)
    search.add_argument(
        "--mode",
        choices=("bm25", "topic", "association", "fusion", "adaptive"),
        default="adaptive",
    )
    search.add_argument("--top-k", type=int, default=10)
    search.add_argument("--source-id", action="append", default=[])
    search.add_argument("--concept-id", action="append", default=[])
    search.add_argument("--concept-type", action="append", default=[])
    evidence_pack = commands.add_parser(
        "evidence-pack",
        help="rank reviewed records and emit canonical locator strings plus integer citation pages",
    )
    evidence_pack.add_argument("--query", required=True)
    evidence_pack.add_argument("--top-k", type=int, default=30)
    coverage_pack = commands.add_parser(
        "coverage-pack",
        help="retain separate reviewed-claim candidates for every lexical query facet",
    )
    coverage_pack.add_argument("--query", required=True)
    coverage_pack.add_argument("--top-k", type=int, default=30)
    coverage_pack.add_argument("--per-facet", type=int, default=12)
    coverage_pack.add_argument("--maximum-facets", type=int, default=12)
    finalize = commands.add_parser(
        "finalize-answer",
        help="rebuild exact evidence and citations for a compact answer draft",
    )
    finalize.add_argument(
        "--draft",
        required=True,
        help="external JSON draft path, or - to read the draft from standard input",
    )
    finalize.add_argument("--question-id", required=True)
    finalize.add_argument("--summary-min-words", type=int, default=180)
    finalize.add_argument("--summary-max-words", type=int, default=320)
    return parser


def main(argv: list[str] | None = None) -> int:
    """Validate the supplied snapshot and execute one read-only operation."""

    _configure_utf8()
    args = build_parser().parse_args(argv)
    try:
        snapshot = load_snapshot(
            args.bundle,
            deep_validation=bool(getattr(args, "deep_validation", False)),
        )
        if args.command == "inspect":
            result = inspect_snapshot(snapshot)
        elif args.command == "evidence-pack":
            result = build_evidence_pack(snapshot, args.query, args.top_k)
        elif args.command == "coverage-pack":
            result = build_coverage_pack(
                snapshot,
                args.query,
                args.top_k,
                args.per_facet,
                args.maximum_facets,
            )
        elif args.command == "finalize-answer":
            draft_from_stdin = args.draft == "-"
            result = finalize_answer(
                snapshot,
                None if draft_from_stdin else Path(args.draft),
                args.question_id,
                args.summary_min_words,
                args.summary_max_words,
                draft_payload=sys.stdin.read() if draft_from_stdin else None,
            )
        else:
            result = search_snapshot(
                snapshot,
                args.query,
                args.mode,
                args.top_k,
                source_ids=args.source_id,
                concept_ids=args.concept_id,
                concept_types=args.concept_type,
            )
    except (SnapshotError, OSError, UnicodeError, ValueError, TypeError, KeyError, IndexError) as exc:
        print(json.dumps({"status": "error", "code": "adaptive-error", "error": str(exc)}, ensure_ascii=False, sort_keys=True))
        return 2
    print(
        json.dumps(
            result,
            ensure_ascii=False,
            sort_keys=args.command != "finalize-answer",
            allow_nan=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
