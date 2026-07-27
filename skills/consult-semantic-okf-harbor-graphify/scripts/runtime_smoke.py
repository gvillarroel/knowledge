#!/usr/bin/env python3
"""Verify the pinned read-only Graphify query runtime."""

from __future__ import annotations

import argparse
import importlib
import importlib.metadata
import json


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    version = importlib.metadata.version("graphifyy")
    serve = importlib.import_module("graphify.serve")
    required = ("_query_terms", "_score_query", "_pick_seeds", "_bfs")
    missing = [name for name in required if not hasattr(serve, name)]
    valid = version == "0.9.17" and not missing
    payload = {
        "distribution": "graphifyy",
        "expected": "0.9.17",
        "found": version,
        "missing": missing,
        "status": "pass" if valid else "fail",
    }
    print(json.dumps(payload, sort_keys=True) if args.format == "json" else (
        f"graphifyy {version}: {'pass' if valid else 'fail'}"
    ))
    return 0 if valid else 2


if __name__ == "__main__":
    raise SystemExit(main())
