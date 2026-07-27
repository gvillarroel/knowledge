#!/usr/bin/env python3
"""Verify the Tika/MALLET consultant's local and optional external runtime."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml

from _mallet_topics import MalletRuntimeError, preflight_mallet
from _tika_mallet_snapshot import ALGORITHMS, SCHEMA_VERSION


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--java", type=Path)
    parser.add_argument("--mallet-home", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    """Report Python support and, when supplied, the exact MALLET runtime binding."""

    args = build_parser().parse_args(argv)
    if (args.java is None) != (args.mallet_home is None):
        raise MalletRuntimeError("--java and --mallet-home must be supplied together")
    result = {
        "status": "pass",
        "schema_version": SCHEMA_VERSION,
        "runtime": "semantic-okf-tika-mallet-query-python",
        "model_required": False,
        "network_required": False,
        "algorithms": ALGORITHMS,
        "packages": {"pyyaml": getattr(yaml, "__version__", "unknown")},
    }
    if args.java is not None and args.mallet_home is not None:
        result["mallet_toolchain"] = preflight_mallet(
            args.java, args.mallet_home
        ).payload()
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
