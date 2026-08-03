#!/usr/bin/env python3
"""Bind the pre-existing 25-strategy population to the contradiction benchmark."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Sequence


DATASET_ID = "graphrag-papers-contradiction-eval-40-v1"


class FreezeError(RuntimeError):
    """Describe an invalid population or benchmark binding."""


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _ref(path: Path) -> dict[str, Any]:
    return {
        "path": str(path.resolve()),
        "bytes": path.stat().st_size,
        "sha256": _sha256(path),
    }


def freeze(selection: Path, questions: Path, output: Path) -> dict[str, Any]:
    """Freeze the exhaustive population without selecting from evaluation results."""

    if output.exists() or output.is_symlink():
        raise FreezeError(f"refusing to overwrite selection: {output}")
    source = json.loads(selection.read_text(encoding="utf-8"))
    strategies = source.get("strategies")
    if (
        source.get("strategy_count") != 25
        or not isinstance(strategies, list)
        or len(strategies) != 25
    ):
        raise FreezeError("source selection must contain exactly 25 strategies")
    identifiers = [
        row.get("strategy_id")
        for row in strategies
        if isinstance(row, dict)
    ]
    if len(identifiers) != 25 or len(set(identifiers)) != 25:
        raise FreezeError("source strategy identities are incomplete or duplicated")
    question_count = sum(
        1
        for line in questions.read_text(encoding="utf-8").splitlines()
        if line.strip()
    )
    if question_count != 40:
        raise FreezeError(f"expected 40 contradiction questions, found {question_count}")
    result = {
        "schema_version": "graphrag-contradiction-strategy-freeze/1.0",
        "dataset_id": DATASET_ID,
        "selection_id": "exhaustive-historical-general-table-contradiction-v1",
        "selection_rule": (
            "Include every representative row from the pre-existing 25-strategy "
            "general table. Do not filter, tune, evolve, merge, or replace a strategy "
            "after contradiction-question release."
        ),
        "question_count": question_count,
        "questions": _ref(questions),
        "parent_selection": _ref(selection),
        "strategy_count": 25,
        "strategies": strategies,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return result


def main(argv: Sequence[str] | None = None) -> int:
    """Freeze the population from command-line inputs."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selection", type=Path, required=True)
    parser.add_argument("--questions", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        result = freeze(
            args.selection.resolve(),
            args.questions.resolve(),
            args.output.resolve(),
        )
    except (FreezeError, OSError, UnicodeError, ValueError, TypeError) as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, sort_keys=True))
        return 2
    print(
        json.dumps(
            {
                "status": "pass",
                "selection_id": result["selection_id"],
                "strategy_count": result["strategy_count"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
