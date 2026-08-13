#!/usr/bin/env python3
"""Independently validate a complete Semantic OKF ensemble bundle."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from _ensemble_build import validate_ensemble_bundle
from _semantic_okf import configure_utf8_output


def build_parser() -> argparse.ArgumentParser:
    """Build the ensemble validation command-line parser."""

    parser = argparse.ArgumentParser(
        description=(
            "Validate Semantic OKF/RDF coherence, all three derived components, "
            "their shared core binding, and the ensemble report."
        )
    )
    parser.add_argument("bundle", type=Path)
    parser.add_argument("--output-format", choices=("text", "json"), default="text")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Validate one published ensemble bundle."""

    configure_utf8_output()
    args = build_parser().parse_args(argv)
    result = validate_ensemble_bundle(args.bundle)
    if args.output_format == "json":
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    elif result["valid"]:
        summary = result["summary"]
        print(
            "Semantic OKF ensemble validation passed: "
            f"{summary['required_components']} components, {summary['policies']} policies, "
            f"default={summary['default_policy']}"
        )
    else:
        for error in result["errors"]:
            print(f"{error['code']} {error['path']}: {error['message']}", file=sys.stderr)
    return 0 if result["valid"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
