#!/usr/bin/env python3
"""Prepare a deterministic interrupted refresh transaction for recovery testing."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def tree_sha256(root: Path) -> str:
    entries = [
        {"path": path.relative_to(root).as_posix(), "sha256": sha256_bytes(path.read_bytes())}
        for path in sorted(
            (candidate for candidate in root.rglob("*") if candidate.is_file()),
            key=lambda candidate: candidate.relative_to(root).as_posix(),
        )
    ]
    encoded = json.dumps(entries, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return sha256_bytes(encoded)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle", type=Path)
    args = parser.parse_args()
    workspace = Path.cwd().resolve()
    bundle = args.bundle.resolve()
    if workspace not in bundle.parents or not bundle.is_dir() or bundle.is_symlink():
        raise ValueError("bundle must be an existing local workspace directory")

    token = "b" * 32
    parent = bundle.parent
    candidate = parent / f".sokf-{token}.stage"
    backup = parent / f".sokf-{token}.backup"
    journal = parent / f".{bundle.name}.refresh.json"
    if candidate.exists() or backup.exists() or journal.exists():
        raise FileExistsError("transaction fixture already exists")

    shutil.copytree(bundle, candidate)
    old_hash = tree_sha256(bundle)
    new_hash = tree_sha256(candidate)
    payload = {
        "schema_version": "1.0",
        "output": bundle.name,
        "candidate": candidate.name,
        "backup": backup.name,
        "old_tree_sha256": old_hash,
        "new_tree_sha256": new_hash,
        "state": "old_moved",
    }
    journal.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    bundle.replace(backup)
    print(json.dumps(payload, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

