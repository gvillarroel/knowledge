#!/usr/bin/env python3
"""Verify the package-local entity-graph builder runtime."""

from __future__ import annotations

import json

from _entity_graph_model import GENERIC_SCHEMA_VERSION, SCHEMA_VERSION


def main() -> int:
    """Import required packages and report the offline runtime."""

    import pyshacl
    import rdflib
    import yaml

    print(
        json.dumps(
            {
                "status": "pass",
                "runtime": "semantic-okf-entity-graph-python",
                "schema_versions": [SCHEMA_VERSION, GENERIC_SCHEMA_VERSION],
                "model_required": False,
                "network_required": False,
                "packages": {
                    "pyshacl": getattr(pyshacl, "__version__", "unknown"),
                    "rdflib": getattr(rdflib, "__version__", "unknown"),
                    "yaml": getattr(yaml, "__version__", "unknown"),
                },
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
