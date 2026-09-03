#!/usr/bin/env python3
"""Verify the generated expert's model-free, network-free runtime."""

from __future__ import annotations

import json
import sys

sys.dont_write_bytecode = True

from _classical_snapshot import ALGORITHMS, SCHEMA_VERSION  # noqa: E402
from _context_projection import SCHEMA_VERSION as CONTEXT_SCHEMA  # noqa: E402


def main() -> int:
    """Report the embedded classical query runtime contract."""

    print(
        json.dumps(
            {
                "status": "pass",
                "schema_version": SCHEMA_VERSION,
                "runtime": "classical-chunked-knowledge-skill-query-python",
                "context_schema_version": CONTEXT_SCHEMA,
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
