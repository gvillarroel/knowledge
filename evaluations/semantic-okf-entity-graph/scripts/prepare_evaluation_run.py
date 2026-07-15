#!/usr/bin/env python3
"""Atomically prepare or audit an append-only Semantic OKF evaluation run."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any, Iterable


SCHEMA_VERSION = "semantic-okf-entity-graph-run-inputs/1.0"
DERIVED_DIRECTORIES = frozenset({"entity-graph"})


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _relative_files(root: Path, *, core_only: bool = False) -> list[str]:
    paths = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if core_only and relative.parts and relative.parts[0] in DERIVED_DIRECTORIES:
            continue
        paths.append(relative.as_posix())
    return sorted(paths)


def _logical_file_sha256(path: Path) -> str:
    data = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()


def _logical_tree_sha256(root: Path, relative_paths: Iterable[str]) -> str:
    payload = [
        {"path": relative, "sha256": _logical_file_sha256(root / Path(relative))}
        for relative in sorted(relative_paths)
    ]
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _bundle_fingerprint(bundle: Path) -> dict[str, Any]:
    all_files = _relative_files(bundle)
    core_files = _relative_files(bundle, core_only=True)
    return {
        "file_count": len(all_files),
        "total_bytes": sum((bundle / Path(relative)).stat().st_size for relative in all_files),
        "logical_tree_sha256": _logical_tree_sha256(bundle, all_files),
        "core_file_count": len(core_files),
        "core_total_bytes": sum((bundle / Path(relative)).stat().st_size for relative in core_files),
        "logical_core_tree_sha256": _logical_tree_sha256(bundle, core_files),
        "semantic_records_sha256": _sha256_file(bundle / "semantic" / "records.jsonl"),
    }


def _load_status(bundle: Path, derived_directory: str | None) -> dict[str, Any]:
    core_report_path = bundle / "semantic" / "build-report.json"
    core_report = json.loads(core_report_path.read_text(encoding="utf-8"))
    if core_report.get("status") != "pass" or core_report.get("valid") is not True:
        raise ValueError(f"Core report is not passing: {core_report_path}")
    result: dict[str, Any] = {
        "core_report_path": core_report_path.relative_to(bundle).as_posix(),
        "core_report_sha256": _sha256_file(core_report_path),
    }
    if derived_directory is not None:
        report_path = bundle / derived_directory / "build-report.json"
        report = json.loads(report_path.read_text(encoding="utf-8"))
        if report.get("status") != "pass" or report.get("valid") is not True:
            raise ValueError(f"Derived report is not passing: {report_path}")
        result.update(
            {
                "derived_report_path": report_path.relative_to(bundle).as_posix(),
                "derived_report_sha256": _sha256_file(report_path),
                "declared_core_tree_sha256": report.get("core", {}).get("tree_sha256"),
            }
        )
    return result


def _manifest(run: Path, *, run_id: str | None = None) -> dict[str, Any]:
    workspaces = run / "workspaces"
    specs = {"entity-graph": "entity-graph"}
    bundles: dict[str, Any] = {}
    for name, derived_directory in specs.items():
        bundle = workspaces / name / "knowledge"
        if not bundle.is_dir():
            raise ValueError(f"Missing {name} bundle: {bundle}")
        bundles[name] = {
            "workspace_path": bundle.parent.relative_to(run).as_posix(),
            "bundle_path": bundle.relative_to(run).as_posix(),
            "status": _load_status(bundle, derived_directory),
            "fingerprint": _bundle_fingerprint(bundle),
        }

    core_hashes = {value["fingerprint"]["logical_core_tree_sha256"] for value in bundles.values()}
    record_hashes = {value["fingerprint"]["semantic_records_sha256"] for value in bundles.values()}
    if len(core_hashes) != 1 or len(record_hashes) != 1:
        raise ValueError("Entity-graph run has inconsistent authoritative-core fingerprints")
    declared_hashes = {
        value["status"].get("declared_core_tree_sha256")
        for value in bundles.values()
        if value["status"].get("declared_core_tree_sha256") is not None
    }
    if declared_hashes and declared_hashes != core_hashes:
        raise ValueError("Derived reports disagree with independently computed authoritative-core hash")
    return {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id or run.name,
        "publication": {
            "append_only": True,
            "inputs_published_atomically": True,
            "derived_directories_excluded_from_core": sorted(DERIVED_DIRECTORIES),
        },
        "parity": {
            "status": "pass",
            "logical_core_tree_sha256": next(iter(core_hashes)),
            "semantic_records_sha256": next(iter(record_hashes)),
        },
        "bundles": bundles,
    }


def _write_manifest(run: Path, *, run_id: str | None = None) -> Path:
    target = run / "input-manifest.json"
    if target.exists():
        raise FileExistsError(f"Append-only manifest already exists: {target}")
    value = _manifest(run, run_id=run_id)
    temporary = run / ".input-manifest.json.tmp"
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    os.replace(temporary, target)
    return target


def _copy_workspace(template: Path, bundle: Path, destination: Path) -> None:
    shutil.copytree(template, destination)
    shutil.copytree(bundle, destination / "knowledge")


def _prepare(args: argparse.Namespace) -> Path:
    output_root = args.output_root.resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    target = output_root / args.run_id
    if target.exists():
        raise FileExistsError(f"Append-only run already exists: {target}")
    stage = Path(tempfile.mkdtemp(prefix=f".{args.run_id}.staging-", dir=output_root))
    try:
        _copy_workspace(
            args.workspace_template.resolve(),
            args.entity_graph_bundle.resolve(),
            stage / "workspaces" / "entity-graph",
        )
        _write_manifest(stage, run_id=args.run_id)
        os.replace(stage, target)
    except BaseException:
        shutil.rmtree(stage, ignore_errors=True)
        raise
    return target / "input-manifest.json"


def _finalize(run: Path, external: list[str]) -> Path:
    target = run / "run-manifest.json"
    if target.exists():
        raise FileExistsError(f"Append-only run manifest already exists: {target}")
    input_manifest = run / "input-manifest.json"
    if not input_manifest.is_file():
        raise ValueError(f"Missing input manifest: {input_manifest}")
    published_inputs = json.loads(input_manifest.read_text(encoding="utf-8"))
    try:
        current_inputs = _manifest(run)
    except ValueError as exc:
        raise ValueError(
            f"Run workspaces changed after the immutable input manifest was published: {exc}"
        ) from exc
    if published_inputs != current_inputs:
        raise ValueError("Run workspaces changed after the immutable input manifest was published")
    required = [
        run / "retrieval" / "top10" / "comparison.json",
        run / "retrieval" / "pool100" / "comparison.json",
        run / "skill-arena" / "entity-graph" / "promptfoo-results.json",
        run / "skill-arena" / "reviews" / "reviews.json",
    ]
    missing = [path for path in required if not path.is_file()]
    if missing:
        raise ValueError("Run cannot be finalized; missing: " + ", ".join(str(path) for path in missing))
    artifacts = []
    for path in sorted(candidate for candidate in run.rglob("*") if candidate.is_file()):
        relative = path.relative_to(run)
        if relative.parts and relative.parts[0] == "workspaces":
            continue
        if path == target or path.name.startswith(".input-manifest.json"):
            continue
        artifacts.append(
            {
                "path": relative.as_posix(),
                "bytes": path.stat().st_size,
                "sha256": _sha256_file(path),
            }
        )
    external_artifacts = []
    for item in external:
        name, separator, raw_path = item.partition("=")
        if not separator or not name or not raw_path:
            raise ValueError("Each --external must be NAME=PATH")
        path = Path(raw_path).resolve()
        if not path.is_file():
            raise ValueError(f"External artifact does not exist: {path}")
        external_artifacts.append(
            {
                "name": name,
                "path": Path(raw_path).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": _sha256_file(path),
            }
        )
    value = {
        "schema_version": "semantic-okf-entity-graph-run/1.0",
        "status": "pass",
        "run_id": run.name,
        "append_only": True,
        "input_manifest": {
            "path": input_manifest.relative_to(run).as_posix(),
            "sha256": _sha256_file(input_manifest),
        },
        "artifact_count": len(artifacts),
        "artifacts": artifacts,
        "external_artifacts": sorted(external_artifacts, key=lambda item: item["name"]),
    }
    temporary = run / ".run-manifest.json.tmp"
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    os.replace(temporary, target)
    return target


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    prepare = subparsers.add_parser("prepare", help="atomically publish a new run's immutable workspaces")
    prepare.add_argument("--run-id", required=True)
    prepare.add_argument("--output-root", type=Path, required=True)
    prepare.add_argument("--workspace-template", type=Path, required=True)
    prepare.add_argument("--entity-graph-bundle", type=Path, required=True)

    audit = subparsers.add_parser("audit-existing", help="verify and append the missing input manifest")
    audit.add_argument("--run", type=Path, required=True)

    finalize = subparsers.add_parser("finalize", help="hash completed outputs and publish the final run manifest")
    finalize.add_argument("--run", type=Path, required=True)
    finalize.add_argument("--external", action="append", default=[])

    args = parser.parse_args()
    if args.command == "prepare":
        manifest = _prepare(args)
    elif args.command == "audit-existing":
        manifest = _write_manifest(args.run.resolve())
    else:
        manifest = _finalize(args.run.resolve(), args.external)
    print(manifest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
