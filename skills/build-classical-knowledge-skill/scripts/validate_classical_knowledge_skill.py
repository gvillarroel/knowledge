#!/usr/bin/env python3
"""Independently validate a generated classical knowledge skill."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from _knowledge_skill import (
    SCHEMA_VERSION,
    KnowledgeSkillError,
    tree_binding,
    validate_generated_skill,
)


def build_parser() -> argparse.ArgumentParser:
    """Build the generated-skill validation parser."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skill", type=Path, help="Generated expert-skill directory")
    parser.add_argument(
        "--deep-validation",
        action="store_true",
        help="Independently rederive every classical retrieval artifact",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Validate one complete generated expert without writing to it."""

    args = build_parser().parse_args(argv)
    try:
        skill = args.skill.expanduser()
        if skill.is_symlink():
            raise KnowledgeSkillError("Generated skill root cannot be a symlink")
        skill = skill.resolve()
        manifest = validate_generated_skill(
            skill,
            deep_validation=args.deep_validation,
        )
        binding = tree_binding(skill)
        result = {
            "schema_version": SCHEMA_VERSION,
            "status": "pass",
            "valid": True,
            "skill_name": manifest["skill_name"],
            "skill_tree_sha256": binding.sha256,
            "skill_file_count": binding.file_count,
            "knowledge_tree_sha256": manifest["knowledge"]["tree"]["sha256"],
            "record_count": manifest["knowledge"]["record_count"],
            "concept_layout": manifest["generation"]["concept_layout"],
            "deep_validation": args.deep_validation,
        }
    except (KnowledgeSkillError, OSError, UnicodeError, ValueError, TypeError) as exc:
        print(
            json.dumps(
                {
                    "schema_version": SCHEMA_VERSION,
                    "status": "error",
                    "valid": False,
                    "errors": [
                        {
                            "code": "knowledge-skill-error",
                            "message": str(exc),
                        }
                    ],
                },
                ensure_ascii=False,
                sort_keys=True,
            )
        )
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
