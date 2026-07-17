#!/usr/bin/env python3
"""Create a Graphify projection for an existing validated Semantic OKF bundle."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from _graphify_projection import GraphifyProjectionError, materialize_graphify_projection
from _semantic_okf import validate_semantic_bundle


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle", type=Path, help="Validated Semantic OKF bundle directory.")
    parser.add_argument("--output-format", choices=("text", "json"), default="text")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        semantic = validate_semantic_bundle(args.bundle)
        if not semantic["valid"]:
            raise GraphifyProjectionError(
                "Semantic OKF validation failed: " + "; ".join(semantic["errors"])
            )
        report = materialize_graphify_projection(args.bundle)
    except (GraphifyProjectionError, OSError, ValueError) as exc:
        payload = {"status": "error", "code": "graphify-build-error", "error": str(exc)}
        if args.output_format == "json":
            print(json.dumps(payload, sort_keys=True))
        else:
            print(f"graphify-build-error: {exc}", file=sys.stderr)
        return 2
    if args.output_format == "json":
        print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    else:
        print(f"Graphify projection passed: {report['graph']}")
        print(f"Logical SHA-256: {report['logical_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
