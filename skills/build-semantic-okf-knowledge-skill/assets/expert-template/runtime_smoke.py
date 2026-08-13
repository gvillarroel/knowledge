#!/usr/bin/env python3
"""Smoke-test the generated expert's bound read-only runtime."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode = True


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    completed = subprocess.run(
        [
            sys.executable,
            "-B",
            str(root / "scripts" / "query_expert_knowledge.py"),
            "verify",
        ],
        cwd=root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="strict",
        check=False,
    )
    if completed.returncode != 0:
        print(completed.stdout or completed.stderr, end="", file=sys.stderr)
        return completed.returncode
    payload = json.loads(completed.stdout)
    print(
        json.dumps(
            {
                "status": "pass",
                "runtime": "semantic-okf-family-expert-python",
                "skill_name": payload["skill_name"],
                "family": payload["family"],
                "record_count": payload["record_count"],
                "read_only": payload["read_only"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
