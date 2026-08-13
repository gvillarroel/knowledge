#!/usr/bin/env python3
"""Verify the pinned Graphify runtime and private query primitives."""

from __future__ import annotations

import argparse
import importlib
import importlib.metadata
import json


PIN = "0.9.17"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    found = importlib.metadata.version("graphifyy")
    graphify = importlib.import_module("graphify")
    serve = importlib.import_module("graphify.serve")
    required = ("extract", "build_from_json")
    query_required = ("_query_terms", "_score_query", "_pick_seeds", "_bfs")
    missing = [name for name in required if not hasattr(graphify, name)]
    missing.extend(name for name in query_required if not hasattr(serve, name))
    valid = found == PIN and not missing
    payload = {
        "distribution": "graphifyy",
        "expected": PIN,
        "found": found,
        "missing": missing,
        "mode": "markdown-structural-no-llm",
        "status": "pass" if valid else "fail",
    }
    print(json.dumps(payload, sort_keys=True) if args.format == "json" else (
        f"graphifyy {found}: {'pass' if valid else 'fail'}; mode={payload['mode']}"
    ))
    return 0 if valid else 2


if __name__ == "__main__":
    raise SystemExit(main())
