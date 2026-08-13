from __future__ import annotations

import argparse
from pathlib import Path
import sys

from _classical_atlas import AtlasError, format_result, validate_atlas


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Independently validate a generated Classical Semantic OKF atlas."
    )
    parser.add_argument("knowledge", type=Path, help="Source Classical Semantic OKF bundle")
    parser.add_argument("atlas", type=Path, help="Generated atlas directory")
    parser.add_argument("--output-format", choices=("text", "json"), default="text")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    template = Path(__file__).resolve().parents[1] / "assets" / "classical-atlas-template.html"
    try:
        result = validate_atlas(args.knowledge, args.atlas, template)
    except AtlasError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(format_result(result, args.output_format))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
