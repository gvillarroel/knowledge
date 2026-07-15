#!/usr/bin/env python3
"""Atomically build an authoritative Semantic OKF core and ensemble projections."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from _adaptive_retrieval import AdaptiveError
from _build_semantic_okf_core import build as build_core
from _embedding_retrieval import RetrievalError
from _ensemble_build import EnsembleError, atomic_build
from _entity_graph_model import EntityGraphError
from _semantic_okf import BundleError, ManifestError, configure_utf8_output


def build_parser() -> argparse.ArgumentParser:
    """Build the ensemble command-line parser."""

    parser = argparse.ArgumentParser(
        description=(
            "Build a Semantic OKF/RDF v1 snapshot plus hash-bound adaptive lexical, "
            "entity-graph, embedding, and quality-gated ensemble projections."
        )
    )
    parser.add_argument("manifest", type=Path, help="Closed Semantic OKF manifest")
    parser.add_argument("ensemble_plan", type=Path, help="Closed ensemble plan JSON")
    parser.add_argument("output", type=Path, help="New output directory")
    parser.add_argument("--output-format", choices=("text", "json"), default="text")
    return parser


def _code(exc: Exception) -> str:
    if isinstance(exc, ManifestError):
        return "manifest-error"
    if isinstance(exc, (EnsembleError, AdaptiveError, EntityGraphError, RetrievalError)):
        return "ensemble-error"
    if isinstance(exc, BundleError):
        return "semantic-error"
    if isinstance(exc, (OSError, UnicodeError, ValueError, json.JSONDecodeError)):
        return "source-error"
    return ""


def main(argv: list[str] | None = None) -> int:
    """Run one atomic ensemble build."""

    configure_utf8_output()
    args = build_parser().parse_args(argv)
    try:
        report = atomic_build(args.manifest, args.ensemble_plan, args.output, build_core)
    except Exception as exc:
        code = _code(exc)
        if not code:
            raise
        if args.output_format == "json":
            print(
                json.dumps(
                    {"status": "error", "valid": False, "code": code, "error": str(exc)},
                    ensure_ascii=False,
                    sort_keys=True,
                )
            )
        else:
            print(f"{code}: {exc}", file=sys.stderr)
        return 2
    if args.output_format == "json":
        print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    else:
        summary = report["summary"]
        print(f"Semantic OKF ensemble build passed: {args.output.resolve()}")
        print(
            f"Components: {summary['required_components']}; policies: {summary['policies']}; "
            f"default policy: {summary['default_policy']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
