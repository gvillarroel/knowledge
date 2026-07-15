#!/usr/bin/env python3
"""Prepare mechanical scores and blinded review tasks from one live 90-row run."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path, PurePosixPath
from typing import Sequence

from _answer_output import (
    DEFAULT_CONTRACT,
    AnswerEvaluationError,
    load_contract,
    load_final_bundle,
    load_ground_truth,
    prepare_answers,
    task_text,
)
from _evaluation import REPO_ROOT, display_path, sha256, write_new


def _contract_path(contract: dict, section: str, key: str) -> Path:
    relative = contract[section][key]
    logical = PurePosixPath(relative)
    return REPO_ROOT.joinpath(*logical.parts)


def _safe_output_dir(path: Path, contract: dict) -> Path:
    output = path.resolve(strict=False)
    raw = _contract_path(contract, "publication", "raw_root").resolve(strict=False)
    try:
        output.relative_to(raw)
    except ValueError as exc:
        raise AnswerEvaluationError(
            f"raw preparation output must remain under ignored root {display_path(raw)}"
        ) from exc
    if output.exists():
        raise AnswerEvaluationError(f"append-only output directory already exists: {display_path(output)}")
    for parent in (output.parent, *output.parent.parents):
        if parent.exists() and parent.is_symlink():
            raise AnswerEvaluationError("output path contains a symbolic link")
        if parent == REPO_ROOT.parent:
            break
    output.mkdir(parents=True, exist_ok=False)
    return output


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--promptfoo-results", type=Path, required=True)
    parser.add_argument("--bundle", type=Path)
    parser.add_argument("--ground-truth", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        contract_path = args.contract.resolve(strict=True)
        contract = load_contract(contract_path)
        bundle_path = args.bundle or _contract_path(contract, "bundle", "repository_path")
        truth_path = args.ground_truth or _contract_path(contract, "ground_truth", "path")
        ledger = load_final_bundle(bundle_path, contract, deep_validate=True)
        truth = load_ground_truth(truth_path, contract, ledger)
        contract_binding = {"path": display_path(contract_path), "sha256": sha256(contract_path)}
        mechanical, manifest, tasks = prepare_answers(
            args.promptfoo_results,
            ledger,
            truth,
            contract,
            contract_binding,
        )
        output = _safe_output_dir(args.output_dir, contract)
        write_new(output / "review-tasks.jsonl", task_text(tasks))
        write_new(
            output / "review-manifest.json",
            json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        )
        write_new(
            output / "mechanical-results.json",
            json.dumps(mechanical, indent=2, ensure_ascii=False) + "\n",
        )
    except (AnswerEvaluationError, OSError, UnicodeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(
        json.dumps(
            {
                "status": "prepared",
                "answers": mechanical["answer_count"],
                "blinded": manifest["blinded"],
                "output_dir": display_path(output),
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
