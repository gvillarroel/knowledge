#!/usr/bin/env python3
"""Independently validate a Semantic OKF core and its retrieval projection."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from _embedding_retrieval import validate_retrieval_bundle
from _semantic_okf import configure_utf8_output


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate Semantic OKF/RDF coherence and all embedding retrieval bindings."
    )
    parser.add_argument("bundle", type=Path)
    parser.add_argument("--output-format", choices=("text", "json"), default="text")
    return parser


def main(argv: list[str] | None = None) -> int:
    configure_utf8_output()
    args = build_parser().parse_args(argv)
    result = validate_retrieval_bundle(args.bundle)
    if args.output_format == "json":
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    elif result["valid"]:
        summary = result["summary"]
        print(
            "Semantic OKF embeddings validation passed: "
            f"{summary['chunks']} chunks, {summary['embeddings']} vectors"
        )
    else:
        for error in result["errors"]:
            print(f"{error['code']} {error['path']}: {error['message']}", file=sys.stderr)
    return 0 if result["valid"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
