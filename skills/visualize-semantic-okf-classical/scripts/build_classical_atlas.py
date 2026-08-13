from __future__ import annotations

import argparse
from pathlib import Path
import sys

from _classical_atlas import AtlasError, format_result, write_atlas


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a deterministic read-only atlas from a Classical Semantic OKF bundle."
    )
    parser.add_argument("knowledge", type=Path, help="Validated Classical Semantic OKF bundle")
    parser.add_argument("output", type=Path, help="Absent external output directory")
    parser.add_argument("--check", action="store_true", help="Verify deterministic output without writing")
    parser.add_argument("--output-format", choices=("text", "json"), default="text")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    template = Path(__file__).resolve().parents[1] / "assets" / "classical-atlas-template.html"
    try:
        result = write_atlas(args.knowledge, args.output, template, check=args.check)
    except AtlasError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(format_result(result, args.output_format))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
