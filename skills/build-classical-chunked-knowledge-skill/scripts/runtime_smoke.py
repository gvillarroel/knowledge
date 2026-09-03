#!/usr/bin/env python3
"""Verify the package-local chunked builder and consultation runtime."""

from __future__ import annotations

import json

from _classical_snapshot import ALGORITHMS, SCHEMA_VERSION as CLASSICAL_SCHEMA
from _context_projection import SCHEMA_VERSION as CONTEXT_SCHEMA
from _knowledge_skill import SCHEMA_VERSION as EXPERT_SCHEMA


def main() -> int:
    """Import required packages and report the offline runtime contract."""

    import pyshacl
    import rdflib
    import yaml

    print(
        json.dumps(
            {
                "status": "pass",
                "runtime": "build-classical-chunked-knowledge-skill-python",
                "expert_schema_version": EXPERT_SCHEMA,
                "classical_schema_version": CLASSICAL_SCHEMA,
                "context_schema_version": CONTEXT_SCHEMA,
                "model_required": False,
                "network_required": False,
                "query_runtime_third_party_packages": [],
                "algorithms": ALGORITHMS,
                "builder_packages": {
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
