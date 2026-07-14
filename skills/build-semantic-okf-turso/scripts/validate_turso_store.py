#!/usr/bin/env python3
"""Validate a Turso-backed Semantic OKF database and optional bundle parity."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from _turso_store import validate_turso_store  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    """Build the Turso validator command-line parser."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("database", type=Path, help="Path to semantic/knowledge.db.")
    parser.add_argument(
        "--bundle", type=Path, help="Also verify database-to-bundle parity."
    )
    parser.add_argument("--output-format", choices=("text", "json"), default="text")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Validate one Turso store and emit stable text or JSON."""

    args = build_parser().parse_args(argv)
    report = validate_turso_store(args.database, bundle_root=args.bundle)
    if args.output_format == "json":
        print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    elif report["valid"]:
        print(f"Turso store validation passed: {args.database.resolve()}")
        print(f"Records: {report['summary'].get('records', 0)}")
    else:
        for error in report["errors"]:
            print(f"turso-validation-error: {error}", file=sys.stderr)
    return 0 if report["valid"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
