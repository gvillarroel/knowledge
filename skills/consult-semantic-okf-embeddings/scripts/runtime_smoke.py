#!/usr/bin/env python3
"""Report availability of the base and optional local embedding runtimes."""

from __future__ import annotations

import argparse
import importlib.metadata
import importlib.util
import json
import platform


def build_parser() -> argparse.ArgumentParser:
    """Build the dependency smoke-test parser."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--embedding",
        action="store_true",
        help="Require sentence-transformers 5.6.0 and huggingface-hub 1.23.0.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Verify that the standard-library baseline is always usable."""

    args = build_parser().parse_args(argv)
    sentence_available = importlib.util.find_spec("sentence_transformers") is not None
    hub_available = importlib.util.find_spec("huggingface_hub") is not None
    try:
        sentence_version = (
            importlib.metadata.version("sentence-transformers") if sentence_available else None
        )
    except importlib.metadata.PackageNotFoundError:
        sentence_version = None
    try:
        hub_version = importlib.metadata.version("huggingface-hub") if hub_available else None
    except importlib.metadata.PackageNotFoundError:
        hub_version = None
    embedding_ready = sentence_version == "5.6.0" and hub_version == "1.23.0"
    status = "pass" if not args.embedding or embedding_ready else "fail"
    print(
        json.dumps(
            {
                "status": status,
                "mode": "read-only",
                "network": "none",
                "python_implementation": platform.python_implementation(),
                "python_version": platform.python_version(),
                "base_runtime": "stdlib",
                "sentence_transformers": {
                    "available": sentence_available,
                    "version": sentence_version,
                },
                "huggingface_hub": {"available": hub_available, "version": hub_version},
            },
            sort_keys=True,
        )
    )
    return 0 if status == "pass" else 3


if __name__ == "__main__":
    raise SystemExit(main())
