#!/usr/bin/env python3
"""Validate a Semantic OKF entity-graph snapshot by deterministic rederivation."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from _entity_graph_build import validate_entity_graph_bundle


def main(argv: list[str] | None = None) -> int:
    """Run the package-local entity-graph validator."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle", type=Path)
    parser.add_argument("--output-format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)
    result = validate_entity_graph_bundle(args.bundle)
    if args.output_format == "json":
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    elif result["valid"]:
        print(f"Semantic OKF entity-graph validation passed: {args.bundle.resolve()}")
    else:
        print(result["errors"][0]["message"], file=sys.stderr)
    return 0 if result["valid"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
