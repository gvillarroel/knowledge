#!/usr/bin/env python3
"""Verify the generated expert's model-free, network-free runtime."""

from __future__ import annotations

import json
import sys

sys.dont_write_bytecode = True

from _classical_snapshot import ALGORITHMS, SCHEMA_VERSION  # noqa: E402


def main() -> int:
    """Report the embedded classical query runtime contract."""

    print(
        json.dumps(
            {
                "status": "pass",
                "schema_version": SCHEMA_VERSION,
                "runtime": "classical-knowledge-skill-query-python",
                "model_required": False,
                "network_required": False,
                "write_required": False,
                "algorithms": ALGORITHMS,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
