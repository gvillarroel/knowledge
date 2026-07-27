#!/usr/bin/env python3
"""Verify package-local Python plus external Java, Tika, and MALLET runtimes."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from _tika_ingestion import preflight_tika
from _tika_mallet_retrieval import preflight_mallet


def build_parser() -> argparse.ArgumentParser:
    """Create the runtime preflight parser."""

    parser = argparse.ArgumentParser()
    parser.add_argument("--java", type=Path, required=True)
    parser.add_argument("--tika-home", type=Path, required=True)
    parser.add_argument("--mallet-home", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    """Import Python dependencies and verify exact external runtimes."""

    args = build_parser().parse_args(argv)
    import pyshacl
    import rdflib
    import yaml

    tika = preflight_tika(args.java, args.tika_home)
    mallet = preflight_mallet(args.java, args.mallet_home)
    print(
        json.dumps(
            {
                "status": "pass",
                "runtime": "semantic-okf-tika-mallet",
                "network_required": False,
                "packages": {
                    "pyshacl": getattr(pyshacl, "__version__", "unknown"),
                    "rdflib": getattr(rdflib, "__version__", "unknown"),
                    "yaml": getattr(yaml, "__version__", "unknown"),
                },
                "java_version": mallet.java_version,
                "tika_version": tika.tika_version,
                "tika_jar_tree_sha256": tika.jar_tree_sha256,
                "mallet_version": mallet.mallet_version,
                "mallet_jar_tree_sha256": mallet.jar_tree_sha256,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
