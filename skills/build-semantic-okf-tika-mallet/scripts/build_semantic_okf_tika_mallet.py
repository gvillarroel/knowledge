#!/usr/bin/env python3
"""Atomically build Tika-ingested Semantic OKF plus Java MALLET retrieval."""

from __future__ import annotations

import argparse
import ctypes
import errno
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any

from _build_semantic_okf_core import build as build_core
from _semantic_okf import (
    BundleError,
    CONCEPT_LAYOUT_RECORD_PER_FILE,
    CONCEPT_LAYOUTS,
    ManifestError,
    configure_utf8_output,
)
from _safe_paths import (
    UnsafePathError,
    assert_no_links,
    file_identity,
    lexical_absolute,
    reject_overlaps,
    require_identity,
    require_real_directory,
)
from _tika_ingestion import (
    TikaIngestionError,
    copy_tika_tree,
    stage_tika_inputs,
    validate_tika_semantic_bindings,
)
from _tika_mallet_retrieval import (
    ClassicalError,
    build_projection,
    load_plan,
    preflight_mallet,
)


def build_parser() -> argparse.ArgumentParser:
    """Create the integrated Tika and MALLET build parser."""

    parser = argparse.ArgumentParser(
        description=(
            "Extract local documents with Apache Tika 4.0.0-beta-1, build an "
            "authoritative Semantic OKF snapshot, and derive a Java MALLET 2.1.0 "
            "retrieval projection."
        )
    )
    parser.add_argument("ingestion_plan", type=Path, help="Closed Tika ingestion plan")
    parser.add_argument("retrieval_plan", type=Path, help="Closed MALLET retrieval plan")
    parser.add_argument("output", type=Path, help="New output directory")
    parser.add_argument(
        "--concept-layout",
        choices=sorted(CONCEPT_LAYOUTS),
        default=CONCEPT_LAYOUT_RECORD_PER_FILE,
    )
    parser.add_argument("--java", type=Path, required=True, help="Java 17+ executable")
    parser.add_argument(
        "--tika-home", type=Path, required=True, help="Unpacked Tika application directory"
    )
    parser.add_argument(
        "--mallet-home", type=Path, required=True, help="Unpacked MALLET 2.1.0 directory"
    )
    parser.add_argument("--output-format", choices=("text", "json"), default="text")
    return parser


def atomic_build(
    ingestion_plan: Path,
    retrieval_plan: Path,
    output: Path,
    *,
    java: Path,
    tika_home: Path,
    mallet_home: Path,
    concept_layout: str = CONCEPT_LAYOUT_RECORD_PER_FILE,
) -> dict[str, Any]:
    """Build every layer in private paths and publish with one final rename."""

    destination = lexical_absolute(output)
    try:
        assert_no_links(destination, label="output", allow_missing_tail=True)
        reject_overlaps(
            destination,
            (java, tika_home, mallet_home),
            label="output",
        )
    except UnsafePathError as exc:
        raise ClassicalError(str(exc)) from exc
    if os.path.lexists(destination):
        raise ClassicalError(f"output already exists: {destination}")
    stage: Path | None = None
    workspace: Path | None = None
    try:
        load_plan(retrieval_plan)
        mallet_runtime = preflight_mallet(java, mallet_home)
        stage, semantic_manifest, _, _ = stage_tika_inputs(
            ingestion_plan, java=java, tika_home=tika_home
        )
        destination.parent.mkdir(parents=True, exist_ok=True)
        try:
            parent = require_real_directory(destination.parent, label="output parent")
        except UnsafePathError as exc:
            raise ClassicalError(str(exc)) from exc
        parent_identity = file_identity(parent)
        workspace = Path(
            tempfile.mkdtemp(
                prefix=f".{destination.name}.tika-mallet-work-",
                dir=parent,
            )
        )
        candidate = workspace / "bundle"
        if concept_layout == CONCEPT_LAYOUT_RECORD_PER_FILE:
            build_core(semantic_manifest, candidate)
        else:
            build_core(
                semantic_manifest,
                candidate,
                concept_layout=concept_layout,
            )
        copy_tika_tree(stage, candidate)
        tika_report = validate_tika_semantic_bindings(candidate)
        mallet_report = build_projection(candidate, retrieval_plan, mallet_runtime)
        validate_tika_semantic_bindings(candidate)
        try:
            require_real_directory(candidate, label="bundle candidate")
            require_identity(parent, parent_identity, label="output parent")
            assert_no_links(destination, label="output", allow_missing_tail=True)
        except UnsafePathError as exc:
            raise ClassicalError(str(exc)) from exc
        if os.path.lexists(destination):
            raise ClassicalError(f"output appeared during build: {destination}")
        _publish_no_replace(candidate, destination)
        return {
            "schema_version": "1.0",
            "status": "pass",
            "output": str(destination),
            "tika": tika_report,
            "mallet": mallet_report,
        }
    finally:
        if workspace is not None:
            shutil.rmtree(workspace, ignore_errors=True)
        if stage is not None:
            shutil.rmtree(stage, ignore_errors=True)


def _publish_no_replace(source: Path, destination: Path) -> None:
    """Atomically publish a directory while refusing every existing destination."""

    if os.path.lexists(destination):
        raise ClassicalError(f"output already exists: {destination}")
    if os.name == "nt":
        try:
            os.rename(source, destination)
        except OSError as exc:
            if os.path.lexists(destination):
                raise ClassicalError(
                    f"output appeared during publish: {destination}"
                ) from exc
            raise
        return
    if sys.platform.startswith("linux"):
        library = ctypes.CDLL(None, use_errno=True)
        renameat2 = getattr(library, "renameat2", None)
        if renameat2 is None:
            raise ClassicalError("atomic no-replace publication is unavailable on this Linux runtime")
        renameat2.argtypes = [
            ctypes.c_int,
            ctypes.c_char_p,
            ctypes.c_int,
            ctypes.c_char_p,
            ctypes.c_uint,
        ]
        renameat2.restype = ctypes.c_int
        result = renameat2(
            -100,
            os.fsencode(source),
            -100,
            os.fsencode(destination),
            1,
        )
    elif sys.platform == "darwin":
        library = ctypes.CDLL(None, use_errno=True)
        renamex_np = getattr(library, "renamex_np", None)
        if renamex_np is None:
            raise ClassicalError("atomic no-replace publication is unavailable on this macOS runtime")
        renamex_np.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_uint]
        renamex_np.restype = ctypes.c_int
        result = renamex_np(os.fsencode(source), os.fsencode(destination), 4)
    else:
        raise ClassicalError("atomic no-replace publication is unsupported on this platform")
    if result != 0:
        error_number = ctypes.get_errno()
        if error_number in {errno.EEXIST, errno.ENOTEMPTY}:
            raise ClassicalError(f"output appeared during publish: {destination}")
        raise OSError(error_number, os.strerror(error_number), str(destination))


def _code(exc: Exception) -> str:
    if isinstance(exc, TikaIngestionError):
        return "tika-error"
    if isinstance(exc, ManifestError):
        return "manifest-error"
    if isinstance(exc, ClassicalError):
        return "mallet-error"
    if isinstance(exc, BundleError):
        return "semantic-error"
    if isinstance(exc, UnsafePathError):
        return "source-error"
    if isinstance(exc, (OSError, UnicodeError, ValueError, json.JSONDecodeError)):
        return "source-error"
    return ""


def main(argv: list[str] | None = None) -> int:
    """Run one atomic Tika and MALLET Semantic OKF build."""

    configure_utf8_output()
    args = build_parser().parse_args(argv)
    try:
        report = atomic_build(
            args.ingestion_plan,
            args.retrieval_plan,
            args.output,
            java=args.java,
            tika_home=args.tika_home,
            mallet_home=args.mallet_home,
            concept_layout=args.concept_layout,
        )
    except Exception as exc:
        code = _code(exc)
        if not code:
            raise
        if args.output_format == "json":
            print(
                json.dumps(
                    {"status": "error", "code": code, "error": str(exc)},
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
        summary = report["mallet"]["summary"]
        print(f"Semantic OKF Tika + MALLET build passed: {lexical_absolute(args.output)}")
        print(
            f"Tika documents: {report['tika']['documents']}; "
            f"retrieval passages: {summary['documents']}; topics: {summary['topics']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
