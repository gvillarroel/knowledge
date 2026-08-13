#!/usr/bin/env python3
"""Verify the package-local base runtime without importing optional backends."""

from __future__ import annotations

import json
import platform

import pyshacl
import rdflib
import yaml


def main() -> int:
    print(
        json.dumps(
            {
                "python": platform.python_version(),
                "pyshacl": pyshacl.__version__,
                "pyyaml": yaml.__version__,
                "rdflib": rdflib.__version__,
                "optional_backends_loaded": False,
                "status": "pass",
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
