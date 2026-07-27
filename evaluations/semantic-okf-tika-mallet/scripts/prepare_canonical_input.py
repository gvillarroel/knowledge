#!/usr/bin/env python3
"""Prepare a deterministic evaluator-free Tika/MALLET canonical input tree."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import stat
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any, Sequence


HERE = Path(__file__).resolve().parent
EVALUATION = HERE.parent
REPO = EVALUATION.parents[1]
SPEC = EVALUATION / "canonical" / "graphrag-papers-40"
DEFAULT_OUTPUT = EVALUATION / "generated" / "graphrag-papers-40" / "input"
REPARSE_POINT = 0x0400


class PreparationError(RuntimeError):
    """Describe an unsafe, drifting, or non-deterministic input preparation."""


def _load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise PreparationError(f"cannot read {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise PreparationError(f"{path} must contain one JSON object")
    return value


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _regular_file(path: Path, label: str) -> Path:
    try:
        value = path.lstat()
    except OSError as exc:
        raise PreparationError(f"cannot inspect {label}: {exc}") from exc
    if stat.S_ISLNK(value.st_mode) or (
        getattr(value, "st_file_attributes", 0) & REPARSE_POINT
    ):
        raise PreparationError(f"{label} cannot be a link or reparse point: {path}")
    if not stat.S_ISREG(value.st_mode):
        raise PreparationError(f"{label} must be a regular file: {path}")
    return path


def _safe_relative(value: Any) -> Path:
    if not isinstance(value, str) or not value:
        raise PreparationError("inventory path must be a nonempty string")
    pure = PurePosixPath(value)
    if pure.is_absolute() or ".." in pure.parts or "." in pure.parts:
        raise PreparationError(f"unsafe inventory path: {value}")
    return Path(*pure.parts)


def _tree_inventory(root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted(
        root.rglob("*"), key=lambda item: item.relative_to(root).as_posix()
    ):
        if path.is_symlink():
            raise PreparationError(f"prepared input contains a symlink: {path}")
        if path.is_file():
            rows.append(
                {
                    "path": path.relative_to(root).as_posix(),
                    "bytes": path.stat().st_size,
                    "sha256": _sha256_file(path),
                }
            )
    return rows


def _canonical_digest(value: Any) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _materialize(
    target: Path,
    inventory_path: Path,
    ingestion_plan: Path,
    retrieval_plan: Path,
) -> dict[str, Any]:
    inventory = _load_json(inventory_path)
    if inventory.get("schema_version") != "semantic-okf-tika-mallet-canonical-input/1.0":
        raise PreparationError("unsupported source inventory schema")
    source_root = REPO / str(inventory.get("source_root"))
    target.mkdir()
    for name, source_path in (
        ("ingestion-plan.json", ingestion_plan),
        ("retrieval-plan.json", retrieval_plan),
    ):
        source = _regular_file(source_path, name)
        shutil.copyfile(source, target / name)
    copied: list[dict[str, Any]] = []
    for row in inventory.get("files", []):
        if not isinstance(row, dict):
            raise PreparationError("inventory files must contain objects")
        relative = _safe_relative(row.get("path"))
        source = _regular_file(source_root / relative, str(relative))
        if source.stat().st_size != row.get("bytes"):
            raise PreparationError(f"source byte count drift: {relative.as_posix()}")
        digest = _sha256_file(source)
        if digest != row.get("sha256"):
            raise PreparationError(f"source hash drift: {relative.as_posix()}")
        destination = target / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
        copied.append(
            {
                "path": relative.as_posix(),
                "bytes": destination.stat().st_size,
                "sha256": _sha256_file(destination),
            }
        )
    payload_inventory = _tree_inventory(target)
    receipt = {
        "schema_version": "semantic-okf-tika-mallet-prepared-input/1.0",
        "dataset_id": inventory["dataset_id"],
        "evaluator_material_included": False,
        "source_inventory_sha256": _sha256_file(inventory_path),
        "ingestion_plan_sha256": _sha256_file(target / "ingestion-plan.json"),
        "retrieval_plan_sha256": _sha256_file(target / "retrieval-plan.json"),
        "source_files": copied,
        "payload_file_count": len(payload_inventory),
        "payload_inventory_sha256": _canonical_digest(payload_inventory),
    }
    _write_json(target / "input-manifest.json", receipt)
    return receipt


def prepare(
    output: Path,
    *,
    check: bool,
    inventory: Path = SPEC / "source-inventory.json",
    ingestion_plan: Path = SPEC / "ingestion-plan.json",
    retrieval_plan: Path = SPEC / "retrieval-plan.json",
) -> dict[str, Any]:
    """Create or deterministically compare one prepared input tree."""

    output = output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    candidate = Path(
        tempfile.mkdtemp(prefix=f".{output.name}.candidate-", dir=output.parent)
    )
    candidate.rmdir()
    try:
        receipt = _materialize(
            candidate,
            inventory.resolve(),
            ingestion_plan.resolve(),
            retrieval_plan.resolve(),
        )
        if check:
            if not output.is_dir() or output.is_symlink():
                raise PreparationError(f"prepared input is absent: {output}")
            if _tree_inventory(candidate) != _tree_inventory(output):
                raise PreparationError("prepared input differs from deterministic regeneration")
            shutil.rmtree(candidate)
            return {**receipt, "status": "pass", "check": True}
        if output.exists() or output.is_symlink():
            raise PreparationError(f"output already exists: {output}")
        os.replace(candidate, output)
        return {**receipt, "status": "pass", "check": False}
    finally:
        if candidate.exists():
            shutil.rmtree(candidate)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--inventory", type=Path, default=SPEC / "source-inventory.json"
    )
    parser.add_argument(
        "--ingestion-plan", type=Path, default=SPEC / "ingestion-plan.json"
    )
    parser.add_argument(
        "--retrieval-plan", type=Path, default=SPEC / "retrieval-plan.json"
    )
    parser.add_argument("--check", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = prepare(
            args.output,
            check=args.check,
            inventory=args.inventory,
            ingestion_plan=args.ingestion_plan,
            retrieval_plan=args.retrieval_plan,
        )
    except (PreparationError, OSError, UnicodeError, ValueError, TypeError) as exc:
        print(json.dumps({"status": "error", "error": str(exc)}))
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
