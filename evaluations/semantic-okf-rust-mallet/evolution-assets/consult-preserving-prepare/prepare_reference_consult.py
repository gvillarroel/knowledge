#!/usr/bin/env python3
"""Prepare compact retrieval guidance and authoritative reference text once."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from _rust_mallet_snapshot import SnapshotError
from reference_consult import (
    ReferenceConsultError,
    _bounded_int,
    _configure_utf8,
    _search,
    _show,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle", type=Path)
    parser.add_argument("--query", required=True)
    parser.add_argument("--focus", action="append", default=[])
    parser.add_argument(
        "--minimum-sources",
        type=lambda value: _bounded_int(value, 1, 20),
        required=True,
    )
    parser.add_argument(
        "--depth", type=lambda value: _bounded_int(value, 20, 100), default=60
    )
    parser.add_argument(
        "--max-results", type=lambda value: _bounded_int(value, 4, 30), default=18
    )
    parser.add_argument(
        "--max-sources", type=lambda value: _bounded_int(value, 4, 20), default=10
    )
    parser.add_argument(
        "--per-source", type=lambda value: _bounded_int(value, 1, 3), default=2
    )
    parser.add_argument(
        "--preview-chars",
        type=lambda value: _bounded_int(value, 120, 800),
        default=360,
    )
    return parser


def prepare(args: argparse.Namespace) -> dict[str, object]:
    search = _search(args)
    reference_ids = [
        row["reference_id"] for row in search["recommended"]
    ]
    shown = _show(
        argparse.Namespace(bundle=args.bundle, reference_id=reference_ids)
    )
    selected = shown["selected"]
    if [row["reference_id"] for row in selected] != reference_ids:
        raise ReferenceConsultError(
            "selected reference order differs from the recommendation"
        )
    return {**search, "selected": selected}


def main(argv: list[str] | None = None) -> int:
    _configure_utf8()
    args = build_parser().parse_args(argv)
    try:
        result = prepare(args)
    except (
        ReferenceConsultError,
        SnapshotError,
        OSError,
        UnicodeError,
        ValueError,
        TypeError,
        KeyError,
        IndexError,
        json.JSONDecodeError,
    ) as exc:
        print(
            json.dumps(
                {
                    "status": "error",
                    "code": "reference-consult-error",
                    "error": str(exc),
                },
                ensure_ascii=False,
                sort_keys=True,
            )
        )
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
