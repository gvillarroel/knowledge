#!/usr/bin/env python3
"""Inspect or search an immutable embedding-enabled Semantic OKF snapshot."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from _embedding_snapshot import (  # noqa: E402
    ProviderUnavailable,
    SnapshotError,
    inspect_snapshot,
    load_snapshot,
    search_snapshot,
)


def configure_utf8_output() -> None:
    """Preserve multilingual snapshot content on Windows terminals."""

    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            try:
                reconfigure(encoding="utf-8")
            except (AttributeError, OSError, ValueError):
                pass


def build_parser() -> argparse.ArgumentParser:
    """Build the read-only retrieval command parser."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle", type=Path, help="Published Semantic OKF bundle root.")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("inspect", help="Validate bindings and report retrieval capabilities.")

    search = commands.add_parser("search", help="Run lexical, vector, or hybrid discovery.")
    search.add_argument("--query", required=True, help="Natural-language discovery query.")
    search.add_argument(
        "--mode",
        choices=("auto", "lexical", "vector", "hybrid"),
        default="auto",
    )
    search.add_argument("--top-k", type=int, default=10)
    search.add_argument("--source-id", action="append", default=[])
    search.add_argument("--concept-id", action="append", default=[])
    search.add_argument("--concept-type", action="append", default=[])
    search.add_argument(
        "--allow-fallback",
        action="store_true",
        help="Permit explicit vector/hybrid requests to fall back to lexical discovery.",
    )
    return parser


def _error_payload(code: str, message: str, *, command: str | None) -> dict[str, Any]:
    return {
        "status": "error",
        "mode": command,
        "code": code,
        "error": message,
        "read_only": True,
    }


def main(argv: list[str] | None = None) -> int:
    """Validate first, then inspect or search without writing any bundle file."""

    configure_utf8_output()
    args = build_parser().parse_args(argv)
    try:
        snapshot = load_snapshot(args.bundle)
        if args.command == "inspect":
            payload = inspect_snapshot(snapshot)
        else:
            payload = search_snapshot(
                snapshot,
                args.query,
                requested_mode=args.mode,
                top_k=args.top_k,
                source_ids=args.source_id,
                concept_ids=args.concept_id,
                concept_types=args.concept_type,
                allow_fallback=args.allow_fallback,
            )
    except SnapshotError as exc:
        print(json.dumps(_error_payload("bundle-invalid", str(exc), command=args.command), ensure_ascii=False))
        return 3
    except ProviderUnavailable as exc:
        payload = _error_payload("embedding-provider-unavailable", str(exc), command=args.command)
        if args.command == "search":
            payload.update(
                {
                    "requested_mode": args.mode,
                    "effective_mode": None,
                    "fallback": None,
                    "discovery_only": True,
                }
            )
        print(json.dumps(payload, ensure_ascii=False))
        return 4
    except ValueError as exc:
        print(json.dumps(_error_payload("invalid-arguments", str(exc), command=args.command), ensure_ascii=False))
        return 2
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
