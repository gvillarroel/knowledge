#!/usr/bin/env python3
"""Independently validate Tika, Semantic OKF, and Java MALLET bindings."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from _semantic_okf import configure_utf8_output
from _tika_ingestion import TikaIngestionError, validate_tika_semantic_bindings
from _tika_mallet_retrieval import (
    ClassicalError,
    preflight_mallet,
    validate_classical_bundle,
)


def build_parser() -> argparse.ArgumentParser:
    """Create the integrated validator parser."""

    parser = argparse.ArgumentParser(
        description=(
            "Validate the Tika receipt and Semantic OKF bindings, then retrain "
            "fixed-seed one-thread Java MALLET topics independently."
        )
    )
    parser.add_argument("bundle", type=Path)
    parser.add_argument("--java", type=Path, required=True, help="Java 17+ executable")
    parser.add_argument("--mallet-home", type=Path, required=True)
    parser.add_argument("--output-format", choices=("text", "json"), default="text")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Validate one published Tika and MALLET snapshot."""

    configure_utf8_output()
    args = build_parser().parse_args(argv)
    try:
        tika = validate_tika_semantic_bindings(args.bundle)
        runtime = preflight_mallet(args.java, args.mallet_home)
        mallet = validate_classical_bundle(args.bundle, runtime)
        if not mallet["valid"]:
            raise ClassicalError(mallet["errors"][0]["message"])
        report = {
            "schema_version": "1.0",
            "status": "pass",
            "valid": True,
            "tika": tika,
            "mallet": mallet,
        }
    except (TikaIngestionError, ClassicalError, OSError, ValueError) as exc:
        report = {
            "schema_version": "1.0",
            "status": "error",
            "valid": False,
            "errors": [{"message": str(exc)}],
        }
        if args.output_format == "json":
            print(json.dumps(report, ensure_ascii=False, sort_keys=True))
        else:
            print(f"validation-error: {exc}", file=sys.stderr)
        return 2
    if args.output_format == "json":
        print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    else:
        print(f"Semantic OKF Tika + MALLET validation passed: {args.bundle.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
