#!/usr/bin/env python3
"""Check that ignored evaluation payloads are absent from the Git index."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def tracked_ignored(root: Path = ROOT) -> list[str]:
    """Return explicitly ignored evaluation files still tracked in the index."""
    result = subprocess.run(["git", "ls-files", "-ci", "--exclude-standard", "-z", "--", "evaluations/"],
                            cwd=root, stdout=subprocess.PIPE, check=True)
    return sorted(path.decode("utf-8") for path in result.stdout.split(b"\0") if path)


def untrack_payloads(paths: list[str], root: Path = ROOT) -> dict[str, object]:
    """Remove exact verified payload paths from the index while preserving local bytes."""
    expected: dict[str, str] = {}
    for relative in paths:
        path = root / relative
        if not relative.startswith("evaluations/") or not path.resolve().is_relative_to(root.resolve()):
            raise ValueError("payload path escapes evaluations")
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"payload must be a regular local file: {relative}")
        expected[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
    if paths:
        # argv/stdin carries literal names; no shell expansion and no working-tree deletion.
        subprocess.run(["git", "update-index", "--force-remove", "-z", "--stdin"], cwd=root,
                       input=b"".join(path.encode("utf-8") + b"\0" for path in paths), check=True)
    for relative, digest in expected.items():
        if hashlib.sha256((root / relative).read_bytes()).hexdigest() != digest:
            raise ValueError("working-tree payload changed during index cleanup")
    return {"untracked_files": len(paths), "local_file_hashes_preserved": True,
            "by_evaluation": dict(sorted(Counter(path.split("/")[1] for path in paths).items()))}


def main() -> int:
    """Audit by default; explicitly request the index-only migration with --untrack."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--untrack", action="store_true")
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    if args.receipt and args.receipt.exists():
        raise ValueError("receipt exists; choose an append-only path")
    paths = tracked_ignored()
    if args.untrack:
        result = untrack_payloads(paths)
        result["remaining_tracked_ignored"] = len(tracked_ignored())
    else:
        result = {"status": "pass" if not paths else "fail", "tracked_ignored_files": len(paths),
                  "by_evaluation": dict(sorted(Counter(path.split("/")[1] for path in paths).items()))}
    if args.receipt:
        args.receipt.parent.mkdir(parents=True, exist_ok=True)
        args.receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(result, sort_keys=True))
    return 0 if args.untrack or not paths else 1


if __name__ == "__main__":
    raise SystemExit(main())
