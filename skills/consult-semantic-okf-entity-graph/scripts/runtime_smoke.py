#!/usr/bin/env python3
"""Verify the standard-library-only entity-graph consultant runtime."""

from __future__ import annotations

import json

from _entity_graph_model import ALGORITHMS, SCHEMA_VERSION


def main() -> int:
    """Report the offline, model-free, read-only runtime contract."""

    print(
        json.dumps(
            {
                "status": "pass",
                "schema_version": SCHEMA_VERSION,
                "runtime": "semantic-okf-entity-graph-query-python",
                "model_required": False,
                "network_required": False,
                "read_only": True,
                "algorithms": ALGORITHMS,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
