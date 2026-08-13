#!/usr/bin/env python3
"""Verify the locked Turso consultation runtime."""

from __future__ import annotations

import argparse
import importlib
import importlib.metadata
import json
import platform


def build_parser() -> argparse.ArgumentParser:
    """Build the runtime smoke-test command-line parser."""

    return argparse.ArgumentParser(description=__doc__)


def runtime_report() -> dict[str, object]:
    """Import pyturso and return its pinned runtime version."""

    turso = importlib.import_module("turso")

    return {
        "status": "pass",
        "python_implementation": platform.python_implementation(),
        "python_version": platform.python_version(),
        "dependencies": {"pyturso": importlib.metadata.version("pyturso")},
        "database": {
            "engine": "Turso Database",
            "sqlite_compatibility_version": turso.sqlite_version,
            "read_only_guard": "PRAGMA query_only=1",
        },
    }


def main(argv: list[str] | None = None) -> int:
    """Run the dependency smoke test and print one JSON document."""

    build_parser().parse_args(argv)
    print(json.dumps(runtime_report(), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
