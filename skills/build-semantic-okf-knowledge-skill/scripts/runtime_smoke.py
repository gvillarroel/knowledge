#!/usr/bin/env python3
"""Smoke-test exact package-local builder and consultant runtimes by family."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any

from _direct_skill import SCHEMA_VERSION
from _family_registry import PROFILES, vendor_root


def _smoke(script: Path) -> dict[str, Any]:
    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    completed = subprocess.run(
        [sys.executable, "-B", str(script)],
        cwd=script.parent,
        env=environment,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="strict",
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError((completed.stderr or completed.stdout).strip())
    output = completed.stdout.strip()
    try:
        payload = json.loads(output)
    except json.JSONDecodeError:
        accepted_text = {
            "graphifyy 0.9.17: pass",
            "graphifyy 0.9.17: pass; mode=markdown-structural-no-llm",
        }
        if output not in accepted_text:
            raise RuntimeError(f"Smoke script emitted an unknown payload: {script}")
        payload = {"status": "pass", "native_output": output}
    if not isinstance(payload, dict) or payload.get("status") != "pass":
        raise RuntimeError(f"Smoke script did not pass: {script}")
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--family", choices=(*sorted(PROFILES), "all"), default="legacy")
    args = parser.parse_args(argv)
    root = Path(__file__).resolve().parents[1]
    families = sorted(PROFILES) if args.family == "all" else [args.family]
    try:
        results = {}
        for family in families:
            results[family] = {
                role: _smoke(vendor_root(root, family, role) / "scripts" / "runtime_smoke.py")
                for role in ("builder", "consultant")
            }
    except (OSError, UnicodeError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, sort_keys=True))
        return 2
    print(
        json.dumps(
            {
                "schema_version": SCHEMA_VERSION,
                "status": "pass",
                "runtime": "build-semantic-okf-knowledge-skill-python",
                "families": results,
                "model_download_required": False,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
