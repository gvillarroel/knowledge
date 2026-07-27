#!/usr/bin/env python3
"""Atomically build an authoritative Semantic OKF core plus Graphify projection."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
from pathlib import Path

from _build_semantic_okf_core import build as build_core
from _graphify_projection import (
    GraphifyProjectionError,
    materialize_graphify_projection,
    validate_graphify_projection,
)
from _semantic_okf import BundleError, ManifestError, configure_utf8_output


def build(manifest: Path, output: Path) -> dict[str, object]:
    output = output.expanduser().resolve()
    if output.exists():
        raise GraphifyProjectionError(f"output already exists: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    workspace = Path(
        tempfile.mkdtemp(prefix=f".{output.name}-graphify-", dir=output.parent)
    )
    candidate = workspace / "bundle"
    promoted = False
    try:
        core_report = build_core(manifest, candidate)
        projection = materialize_graphify_projection(candidate)
        if output.exists():
            raise GraphifyProjectionError(
                f"output appeared while the candidate was building: {output}"
            )
        candidate.replace(output)
        promoted = True
        projection = validate_graphify_projection(output, require_runtime=True)
        if not projection["valid"]:
            raise GraphifyProjectionError("; ".join(projection["errors"]))
        return {
            "core": core_report,
            "graphify": projection,
            "status": "pass",
            "summary": core_report["summary"],
        }
    except Exception:
        if promoted and output.exists():
            try:
                shutil.rmtree(output)
            except OSError as exc:
                raise GraphifyProjectionError(
                    f"cannot remove failed promoted output {output}: {exc}"
                ) from exc
        raise
    finally:
        shutil.rmtree(workspace, ignore_errors=True)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path, help="Closed Semantic OKF manifest.")
    parser.add_argument("output", type=Path, help="New output directory.")
    parser.add_argument("--output-format", choices=("text", "json"), default="text")
    return parser


def _code(exc: Exception) -> str:
    if isinstance(exc, ManifestError):
        return "manifest-error"
    if isinstance(exc, GraphifyProjectionError):
        return "graphify-error"
    if isinstance(exc, BundleError):
        return "semantic-error"
    if isinstance(exc, (OSError, UnicodeError, ValueError, json.JSONDecodeError)):
        return "source-error"
    return ""


def main(argv: list[str] | None = None) -> int:
    configure_utf8_output()
    args = build_parser().parse_args(argv)
    try:
        report = build(args.manifest, args.output)
    except Exception as exc:
        code = _code(exc)
        if not code:
            raise
        if args.output_format == "json":
            print(json.dumps({"status": "error", "code": code, "error": str(exc)}, sort_keys=True))
        else:
            print(f"{code}: {exc}", file=sys.stderr)
        return 2
    if args.output_format == "json":
        print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    else:
        summary = report["summary"]
        print(f"Semantic OKF + Graphify build passed: {args.output.resolve()}")
        print(f"Records: {summary['records']}; sources: {summary['sources']}")
        print(f"Graph logical SHA-256: {report['graphify']['logical_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
