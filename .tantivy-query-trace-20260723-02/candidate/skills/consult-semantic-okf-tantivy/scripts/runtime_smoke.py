#!/usr/bin/env python3
"""Verify the pinned Tantivy consultation runtime."""

from __future__ import annotations

import json
from importlib.metadata import PackageNotFoundError, version


EXPECTED_VERSION = "0.26.0"


def runtime_report() -> dict[str, object]:
    """Return the installed Tantivy runtime identity or a clear diagnostic."""

    try:
        installed = version("tantivy")
    except PackageNotFoundError:
        return {
            "status": "error",
            "code": "tantivy-missing",
            "expected_version": EXPECTED_VERSION,
        }
    if installed != EXPECTED_VERSION:
        return {
            "status": "error",
            "code": "tantivy-version-mismatch",
            "expected_version": EXPECTED_VERSION,
            "installed_version": installed,
        }
    import tantivy

    return {
        "status": "pass",
        "package": "tantivy",
        "package_version": installed,
        "binding_version": tantivy.__version__,
        "engine": "Tantivy",
        "implementation": "Rust",
        "scoring": "BM25",
        "index_storage": "memory",
        "model_required": False,
        "network_required": False,
    }


def main() -> int:
    """Print the runtime report and fail when the pin is unavailable."""

    report = runtime_report()
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0 if report["status"] == "pass" else 2


if __name__ == "__main__":
    raise SystemExit(main())
