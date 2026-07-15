#!/usr/bin/env python3
"""Inspect or consult a definitive Semantic OKF ensemble without modifying it."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from _ensemble_snapshot import (
    SnapshotError,
    build_coverage_brief,
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
    """Build the read-only ensemble consultation parser."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle", type=Path, help="Published ensemble Semantic OKF bundle")
    parser.add_argument(
        "--deep-validation",
        action="store_true",
        help="independently rederive deterministic lexical and graph artifacts while loading",
    )
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("inspect", help="Validate and describe the complete ensemble")

    search = commands.add_parser("search", help="Retrieve exact protected evidence passages")
    search.add_argument("--query", required=True)
    search.add_argument(
        "--policy",
        choices=("default", "quality", "fast", "robust"),
        default="default",
    )
    search.add_argument("--top-k", type=int, default=10)
    search.add_argument("--source-id", action="append", default=[])
    search.add_argument("--concept-id", action="append", default=[])
    search.add_argument("--concept-type", action="append", default=[])

    evidence = commands.add_parser(
        "evidence-pack",
        help="rank exact reviewed records for compact answer synthesis",
    )
    evidence.add_argument("--query", required=True)
    evidence.add_argument("--top-k", type=int, default=30)

    coverage = commands.add_parser(
        "coverage-pack",
        help="combine lexical facets with bounded reviewed graph-claim expansion",
    )
    coverage.add_argument("--query", required=True)
    coverage.add_argument("--top-k", type=int, default=30)
    coverage.add_argument("--per-facet", type=int, default=12)
    coverage.add_argument("--maximum-facets", type=int, default=12)

    brief = commands.add_parser(
        "coverage-brief",
        help="compute full multisignal coverage and emit a compact reviewed-claim projection",
    )
    brief.add_argument("--query", required=True)
    brief.add_argument("--top-k", type=int, default=30)
    brief.add_argument("--per-facet", type=int, default=12)
    brief.add_argument("--maximum-facets", type=int, default=12)
    brief.add_argument("--page", type=int, default=1)
    brief.add_argument(
        "--page-size",
        type=int,
        default=48,
        help="maximum deduplicated reviewed claims emitted per page (1-48)",
    )

    finalize = commands.add_parser(
        "finalize-answer",
        help="gate every derived facet and rebuild exact evidence and citations",
    )
    finalize.add_argument(
        "--draft",
        required=True,
        help="external JSON draft path, or - to read the draft from standard input",
    )
    finalize.add_argument("--question-id", required=True)
    finalize.add_argument("--query", required=True)
    finalize.add_argument("--summary-min-words", type=int, default=180)
    finalize.add_argument("--summary-max-words", type=int, default=320)
    finalize.add_argument("--top-k", type=int, default=30)
    finalize.add_argument("--per-facet", type=int, default=12)
    finalize.add_argument("--maximum-facets", type=int, default=12)
    return parser


def main(argv: list[str] | None = None) -> int:
    """Validate one immutable snapshot and execute one consultation operation."""

    _configure_utf8()
    args = build_parser().parse_args(argv)
    try:
        snapshot = load_snapshot(args.bundle, deep_validation=args.deep_validation)
        if args.command == "inspect":
            result = inspect_snapshot(snapshot)
        elif args.command == "search":
            result = search_snapshot(
                snapshot,
                args.query,
                args.policy,
                args.top_k,
                source_ids=args.source_id,
                concept_ids=args.concept_id,
                concept_types=args.concept_type,
            )
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
        elif args.command == "coverage-brief":
            result = build_coverage_brief(
                snapshot,
                args.query,
                args.top_k,
                args.per_facet,
                args.maximum_facets,
                args.page,
                args.page_size,
            )
        else:
            from_stdin = args.draft == "-"
            result = finalize_answer(
                snapshot,
                None if from_stdin else Path(args.draft),
                args.question_id,
                args.query,
                args.summary_min_words,
                args.summary_max_words,
                top_k=args.top_k,
                per_facet=args.per_facet,
                maximum_facets=args.maximum_facets,
                draft_payload=sys.stdin.read() if from_stdin else None,
            )
    except (SnapshotError, OSError, UnicodeError, ValueError, TypeError, KeyError, IndexError) as exc:
        print(
            json.dumps(
                {"status": "error", "code": "ensemble-error", "error": str(exc)},
                ensure_ascii=False,
                sort_keys=True,
            )
        )
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
