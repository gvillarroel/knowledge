#!/usr/bin/env python3
"""Build and independently validate one RustMallet Semantic OKF release."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from _build_semantic_okf_core import build as build_core
from _rust_mallet_retrieval import (
    ClassicalError,
    atomic_build,
    validate_classical_bundle,
)
from _semantic_okf import BundleError, ManifestError, configure_utf8_output


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("classical_plan", type=Path)
    parser.add_argument("output", type=Path)
    return parser


def _code(exc: Exception) -> str:
    if isinstance(exc, ManifestError):
        return "manifest-error"
    if isinstance(exc, ClassicalError):
        return "classical-error"
    if isinstance(exc, BundleError):
        return "semantic-error"
    if isinstance(exc, (OSError, UnicodeError, ValueError, json.JSONDecodeError)):
        return "source-error"
    return ""


def main(argv: list[str] | None = None) -> int:
    configure_utf8_output()
    args = build_parser().parse_args(argv)
    try:
        build_report = atomic_build(
            args.manifest,
            args.classical_plan,
            args.output,
            build_core,
        )
        validation = validate_classical_bundle(args.output)
        if not validation["valid"]:
            raise ClassicalError(
                "independent validation rejected the published release"
            )
    except Exception as exc:
        code = _code(exc)
        if not code:
            raise
        print(
            json.dumps(
                {"status": "error", "code": code, "error": str(exc)},
                ensure_ascii=False,
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 2
    print(
        json.dumps(
            {
                "status": "pass",
                "output": str(args.output.resolve()),
                "build": build_report,
                "validation": validation,
            },
            ensure_ascii=False,
            sort_keys=True,
            allow_nan=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
