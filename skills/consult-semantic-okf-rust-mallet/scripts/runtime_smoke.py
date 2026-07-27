#!/usr/bin/env python3
"""Verify the RustMallet consultant runtime."""

from __future__ import annotations

import json
from importlib.metadata import version

from _rust_mallet_snapshot import ALGORITHMS, SCHEMA_VERSION


def main() -> int:
    """Report the package's pinned RustMallet runtime contract."""

    import pyrmallet

    print(
        json.dumps(
            {
                "status": "pass",
                "schema_version": SCHEMA_VERSION,
                "runtime": "semantic-okf-rust-mallet-query-python",
                "model_required": False,
                "network_required": False,
                "algorithms": ALGORITHMS,
                "packages": {
                    "pyrmallet": version("pyrmallet"),
                    "pyrmallet_module": pyrmallet.__name__,
                },
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
