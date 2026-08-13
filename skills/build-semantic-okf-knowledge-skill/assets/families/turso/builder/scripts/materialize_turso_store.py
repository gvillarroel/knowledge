#!/usr/bin/env python3
"""Materialize a validated Semantic OKF bundle into Turso Database."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import _turso_store  # noqa: E402


DATABASE_RELATIVE_PATH = _turso_store.DATABASE_RELATIVE_PATH
TursoStoreError = _turso_store.TursoStoreError
materialize_turso_store = _turso_store.materialize_turso_store


def build_parser() -> argparse.ArgumentParser:
    """Build the Turso materializer command-line parser."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "bundle", type=Path, help="Validated Semantic OKF bundle directory."
    )
    parser.add_argument(
        "--database",
        type=Path,
        help=f"Output database path (default: BUNDLE/{DATABASE_RELATIVE_PATH}).",
    )
    parser.add_argument("--output-format", choices=("text", "json"), default="text")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Build one Turso projection and return a classified result."""

    args = build_parser().parse_args(argv)
    try:
        report = materialize_turso_store(args.bundle, args.database)
    except (TursoStoreError, OSError, ValueError) as exc:
        if args.output_format == "json":
            print(
                json.dumps(
                    {"status": "error", "code": "turso-build-error", "error": str(exc)},
                    sort_keys=True,
                )
            )
        else:
            print(f"turso-build-error: {exc}", file=sys.stderr)
        return 2
    if args.output_format == "json":
        print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    else:
        print(f"Turso projection passed: {report['database']}")
        print(f"Logical SHA-256: {report['logical_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
