#!/usr/bin/env python3
"""Validate a Semantic OKF core and its hash-bound Graphify projection."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from _graphify_projection import validate_graphify_projection
from _semantic_okf import configure_utf8_output, validate_semantic_bundle


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle", type=Path)
    parser.add_argument("--output-format", choices=("text", "json"), default="text")
    return parser


def main(argv: list[str] | None = None) -> int:
    configure_utf8_output()
    args = build_parser().parse_args(argv)
    semantic_result = validate_semantic_bundle(args.bundle)
    semantic = semantic_result.to_dict()
    graphify = validate_graphify_projection(args.bundle, require_runtime=True)
    valid = bool(semantic_result.valid and graphify["valid"])
    errors = [
        {"layer": "semantic", **error} for error in semantic_result.errors
    ] + [
        {"layer": "graphify", "message": error} for error in graphify["errors"]
    ]
    report = {
        "errors": errors,
        "graphify": graphify,
        "semantic": semantic,
        "status": "pass" if valid else "fail",
        "valid": valid,
    }
    if args.output_format == "json":
        print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    elif valid:
        print(f"Semantic OKF + Graphify validation passed: {args.bundle.resolve()}")
    else:
        for error in report["errors"]:
            if error["layer"] == "semantic":
                print(
                    f"validation-error [{error['code']}] {error['path']}: {error['message']}"
                )
            else:
                print(f"validation-error [graphify]: {error['message']}")
    return 0 if valid else 2


if __name__ == "__main__":
    raise SystemExit(main())
