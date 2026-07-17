#!/usr/bin/env python3
"""Build an authoritative Semantic OKF core plus a derived entity-section graph."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from _build_semantic_okf_core import build as build_core
from _entity_graph_build import atomic_build
from _entity_graph_model import EntityGraphError
from _semantic_okf import BundleError, ManifestError, configure_utf8_output


def build_parser() -> argparse.ArgumentParser:
    """Build the entity-graph lifecycle command parser."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path, help="Closed Semantic OKF manifest")
    parser.add_argument("entity_graph_plan", type=Path, help="Closed entity-graph plan JSON")
    parser.add_argument("output", type=Path, help="New output directory")
    parser.add_argument("--output-format", choices=("text", "json"), default="text")
    return parser


def _code(exc: Exception) -> str:
    if isinstance(exc, ManifestError):
        return "manifest-error"
    if isinstance(exc, EntityGraphError):
        return "entity-graph-error"
    if isinstance(exc, BundleError):
        return "semantic-error"
    if isinstance(exc, (OSError, UnicodeError, ValueError, json.JSONDecodeError)):
        return "source-error"
    return ""


def main(argv: list[str] | None = None) -> int:
    """Run one atomic entity-graph build."""

    configure_utf8_output()
    args = build_parser().parse_args(argv)
    try:
        report = atomic_build(args.manifest, args.entity_graph_plan, args.output, build_core)
    except Exception as exc:
        code = _code(exc)
        if not code:
            raise
        if args.output_format == "json":
            print(json.dumps({"status": "error", "code": code, "error": str(exc)}, ensure_ascii=False, sort_keys=True))
        else:
            print(f"{code}: {exc}", file=sys.stderr)
        return 2
    if args.output_format == "json":
        print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    else:
        summary = report["summary"]
        print(f"Semantic OKF entity-graph build passed: {args.output.resolve()}")
        print(
            f"Inputs: {summary['inputs']}; records: {summary['selected_records']}; sections: {summary['sections']}; "
            f"entities: {summary['entities']}; edges: {summary['edges']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
