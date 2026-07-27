#!/usr/bin/env python3
"""Verify the package-local RustMallet builder runtime."""

from __future__ import annotations

import json
from importlib.metadata import version


def main() -> int:
    """Import every required package and report the local RustMallet runtime."""

    import pyshacl
    import pyrmallet
    import rdflib
    import yaml

    print(
        json.dumps(
            {
                "status": "pass",
                "runtime": "semantic-okf-rust-mallet-python",
                "model_required": False,
                "network_required": False,
                "packages": {
                    "pyshacl": getattr(pyshacl, "__version__", "unknown"),
                    "rdflib": getattr(rdflib, "__version__", "unknown"),
                    "yaml": getattr(yaml, "__version__", "unknown"),
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
