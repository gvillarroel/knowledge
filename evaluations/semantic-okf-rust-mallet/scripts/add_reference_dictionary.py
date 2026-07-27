#!/usr/bin/env python3
"""Copy a validated RustMallet snapshot and add a bound reference dictionary."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import shutil
import sys
import uuid
from pathlib import Path
from types import ModuleType
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]
ORIGINAL_SCRIPTS = (
    REPO_ROOT / "skills" / "consult-semantic-okf-rust-mallet" / "scripts"
)
EVOLVED_SCRIPTS = (
    REPO_ROOT / "skills" / "consult-semantic-okf-rust-mallet-evolved" / "scripts"
)


class UpgradeError(RuntimeError):
    """Describe an invalid input or failed atomic reference upgrade."""


def _module(name: str, path: Path, import_root: Path) -> ModuleType:
    sys.path.insert(0, str(import_root))
    try:
        spec = importlib.util.spec_from_file_location(name, path)
        if spec is None or spec.loader is None:
            raise UpgradeError(f"cannot load module: {path}")
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
        return module
    finally:
        sys.path.remove(str(import_root))


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _tree_sha256(root: Path) -> str:
    rows = [
        (path.relative_to(root).as_posix(), _sha256_file(path))
        for path in sorted(root.rglob("*"))
        if path.is_file()
    ]
    payload = json.dumps(
        rows,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise UpgradeError(f"expected a JSON object: {path}")
    return value


def _write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(
            value,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
            allow_nan=False,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _artifact(root: Path, relative: str, count: int | None = None) -> dict[str, Any]:
    path = root / relative
    result: dict[str, Any] = {
        "path": relative,
        "bytes": path.stat().st_size,
        "sha256": _sha256_file(path),
    }
    if count is not None:
        result["count"] = count
    return result


def _upgrade(source: Path, output: Path) -> dict[str, Any]:
    source = source.expanduser().resolve()
    output = output.expanduser().resolve()
    if not source.is_dir() or source.is_symlink():
        raise UpgradeError(f"source snapshot is missing or unsafe: {source}")
    if output.exists() or output.is_symlink():
        raise UpgradeError(f"output already exists: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)

    original = _module(
        "reference_upgrade_original_snapshot",
        ORIGINAL_SCRIPTS / "_rust_mallet_snapshot.py",
        ORIGINAL_SCRIPTS,
    )
    original_snapshot = original.load_snapshot(source, deep_validation=False)
    reference_module = _module(
        "reference_upgrade_dictionary",
        EVOLVED_SCRIPTS / "_reference_dictionary.py",
        EVOLVED_SCRIPTS,
    )
    dictionary = reference_module.derive_reference_dictionary(
        original_snapshot.documents
    )
    source_tree_sha256 = _tree_sha256(source)
    candidate = output.parent / f".{output.name}.reference-candidate-{uuid.uuid4().hex}"
    try:
        shutil.copytree(source, candidate, symlinks=True)
        classical = candidate / "classical"
        reference_path = classical / "references.json"
        _write_json(reference_path, dictionary)
        reference_artifact = _artifact(
            candidate,
            "classical/references.json",
            dictionary["reference_count"],
        )

        index_path = classical / "index.json"
        index = _load_json(index_path)
        artifacts = index.get("artifacts")
        if not isinstance(artifacts, dict) or "references" in artifacts:
            raise UpgradeError("classical index artifact schema is not upgradeable")
        artifacts["references"] = reference_artifact
        _write_json(index_path, index)

        report_path = classical / "build-report.json"
        report = _load_json(report_path)
        report_artifacts = report.get("artifacts")
        if not isinstance(report_artifacts, dict) or "references" in report_artifacts:
            raise UpgradeError("classical build report schema is not upgradeable")
        report_artifacts["references"] = reference_artifact
        report_artifacts["index"] = _artifact(candidate, "classical/index.json")
        _write_json(report_path, report)

        evolved = _module(
            "reference_upgrade_evolved_snapshot",
            EVOLVED_SCRIPTS / "_rust_mallet_snapshot.py",
            EVOLVED_SCRIPTS,
        )
        validated = evolved.load_snapshot(candidate, deep_validation=False)
        if len(validated.references_by_document) != dictionary["reference_count"]:
            raise UpgradeError("evolved validation returned an incomplete dictionary")
        if _tree_sha256(source) != source_tree_sha256:
            raise UpgradeError("source snapshot changed during the upgrade")
        os.replace(candidate, output)
    except Exception:
        if candidate.exists():
            shutil.rmtree(candidate)
        raise
    return {
        "schema_version": "semantic-okf-rust-mallet-reference-upgrade/1.0",
        "status": "pass",
        "source": str(source),
        "output": str(output),
        "source_tree_sha256": source_tree_sha256,
        "output_tree_sha256": _tree_sha256(output),
        "reference_count": dictionary["reference_count"],
        "reference_dictionary": _artifact(
            output,
            "classical/references.json",
            dictionary["reference_count"],
        ),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = _upgrade(args.source, args.output)
    except (UpgradeError, OSError, UnicodeError, ValueError, TypeError) as exc:
        print(
            json.dumps(
                {"status": "error", "code": "reference-upgrade-error", "error": str(exc)},
                ensure_ascii=False,
                sort_keys=True,
            )
        )
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
