#!/usr/bin/env python3
"""Verify the package-local ensemble builder runtime."""

from __future__ import annotations

import json


def main() -> int:
    """Import every base dependency and each package-local ensemble component."""

    import pyshacl
    import rdflib
    import yaml

    from _adaptive_retrieval import SCHEMA_VERSION as adaptive_schema
    from _embedding_retrieval import SCHEMA_VERSION as embedding_schema
    from _ensemble_build import ALGORITHM_ID, SCHEMA_VERSION as ensemble_schema
    from _entity_graph_model import SCHEMA_VERSION as entity_graph_schema

    print(
        json.dumps(
            {
                "status": "pass",
                "runtime": "semantic-okf-ensemble-build-python",
                "base_model_required": False,
                "optional_model_backends": True,
                "ensemble_schema": ensemble_schema,
                "algorithm": ALGORITHM_ID,
                "components": {
                    "adaptive": adaptive_schema,
                    "embedding": embedding_schema,
                    "entity_graph": entity_graph_schema,
                },
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
