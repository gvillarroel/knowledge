#!/usr/bin/env python3
"""Create immutable local skill snapshots and a compact ignored receipt."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path
from typing import Sequence

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]


def sha256_file(path: Path) -> str:
    """Hash one file."""

    return hashlib.sha256(path.read_bytes()).hexdigest()


def tree_sha256(root: Path) -> str:
    """Match the frozen Astro skill-tree digest contract."""

    rows = [
        {"path": path.relative_to(root).as_posix(), "sha256": sha256_file(path)}
        for path in sorted(item for item in root.rglob("*") if item.is_file() and "__pycache__" not in item.parts)
    ]
    canonical = json.dumps(rows, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def main(argv: Sequence[str] | None = None) -> int:
    """Copy one package create-only and verify any checked baseline binding."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--generation", choices=("baseline", "evolved"), required=True)
    parser.add_argument("--family", choices=("legacy", "embeddings", "classical", "adaptive", "entity-graph", "ensemble"), required=True)
    parser.add_argument("--source", type=Path)
    args = parser.parse_args(argv)
    manifest_path = HERE / f"snapshots/{args.generation}-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    checked = manifest.get("families", {}).get(args.family)
    if args.source is None:
        if not checked:
            parser.error("--source is required until the evolved manifest binds this family")
        source = REPO / checked["source_path"]
    else:
        source = args.source.resolve()
    if not (source / "SKILL.md").is_file():
        raise SystemExit(f"not a standalone skill package: {source}")
    digest = tree_sha256(source)
    if checked and checked.get("tree_sha256") != digest:
        raise SystemExit(f"source tree does not match checked {args.generation} binding for {args.family}")
    skill_id = source.name
    destination = HERE / "snapshots/content" / args.generation / args.family / f"{skill_id}-{digest[:12]}"
    if destination.exists():
        if tree_sha256(destination) != digest:
            raise SystemExit(f"existing snapshot is corrupt: {destination}")
    else:
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(source, destination, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        if tree_sha256(destination) != digest:
            shutil.rmtree(destination)
            raise SystemExit("copied snapshot digest mismatch")
        for path in destination.rglob("*"):
            if path.is_file():
                path.chmod(0o444)
    receipt = {
        "schema_version": "semantic-okf-harbor-local-snapshot/1.0",
        "generation": args.generation,
        "family": args.family,
        "skill_id": skill_id,
        "tree_sha256": digest,
        "path": destination.relative_to(REPO).as_posix(),
    }
    receipt_path = HERE / "snapshots" / f"{args.generation}-{args.family}.local.json"
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

