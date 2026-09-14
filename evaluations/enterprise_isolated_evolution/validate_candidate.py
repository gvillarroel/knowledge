"""Trusted realizer command that checks one exact public profile mutation."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys


def main() -> None:
    """Reject any file change beyond the bound complete retrieval profile."""
    contract = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    root = Path.cwd()
    # The native realizer executes trusted argv in the candidate skill root.
    profile = "assets/retrieval-profile.json"
    files = {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
             for p in root.rglob("*") if p.is_file()}
    if files.keys() != contract["parent_files"].keys():
        raise ValueError("Candidate file inventory changed")
    if any(files[p] != s for p, s in contract["parent_files"].items() if p != profile):
        raise ValueError("Candidate changed a protected byte")
    if json.loads((root / profile).read_text(encoding="utf-8")) != contract["expected_profile"]:
        raise ValueError("Candidate profile differs from the frozen request")


if __name__ == "__main__":
    main()
