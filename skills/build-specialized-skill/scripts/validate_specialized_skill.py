#!/usr/bin/env python3
"""Validate a generated standalone expert skill and its knowledge binding."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from _specialized_skill import SpecializedSkillError, tree_binding, validate_generated_skill


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skill", type=Path, help="Generated expert skill directory")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Validate one generated expert skill."""

    args = build_parser().parse_args(argv)
    skill = args.skill.resolve()
    try:
        manifest = validate_generated_skill(skill)
        binding = tree_binding(skill)
    except (OSError, SpecializedSkillError) as exc:
        raise SystemExit(f"Specialized skill validation failed: {exc}") from exc
    result = {
        "status": "pass",
        "skill_name": manifest["skill_name"],
        "record_count": manifest["knowledge"]["record_count"],
        "tree_sha256": binding.sha256,
        "file_count": binding.file_count,
    }
    if "retrieval_profile" in manifest:
        result["retrieval_profile"] = {
            "mode": manifest["retrieval_profile"]["mode"],
            "promotion_eligible": False,
        }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
