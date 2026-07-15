#!/usr/bin/env python3
"""Run fixed-rubric blinded semantic reviews for prepared ensemble answers."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Sequence

from _answer_output import (
    DEFAULT_CONTRACT,
    AnswerEvaluationError,
    REVIEWER,
    _implementation_binding,
    load_contract,
    validate_preparation,
    validate_review,
)
from _evaluation import write_new


WINDOWS = os.name == "nt"


def _rubric(tasks: Sequence[dict[str, Any]]) -> str:
    payload = json.dumps(tasks, ensure_ascii=False, separators=(",", ":"))
    return f"""You are a blinded evaluator of grounded research answers. Candidate identifiers reveal no profile, skill, or repetition.
Judge only against each supplied ground truth and authoritative support-record interpretations. Do not use the web or outside knowledge.

For each candidate:
1. Score every candidate claim's semantic fidelity to its cited support records: 1 if fully faithful, 0.5 if partly supported or materially overbroad, 0 if unsupported or contradicted.
2. Score every ground-truth atomic answer claim by id: 1 if fully conveyed, 0.5 if partial or implicit, 0 if missing or contradicted. Accept listed variants and equivalent evidence only when supplied support records justify it.
3. Score every important negative by id using the same 1, 0.5, or 0 scale.
4. Give a neutral note of at most 35 words. Do not reward verbosity, formatting, or citation count.

Return one JSON object only: {{"reviews":[...]}}. Preserve task order. Each review must have exactly:
{{"answer_id":"...","claim_fidelity":[{{"index":0,"score":1}}],"atomic_scores":{{"atomic-id":1}},"negative_scores":{{"negative-id":1}},"note":"..."}}
Claim indexes are zero-based and cover every candidate claim exactly once. Atomic and negative maps contain every supplied id exactly once. Scores are exactly 0, 0.5, or 1.

TASKS:
{payload}
"""


def _extract_json(output: str) -> dict[str, Any]:
    def object_hook(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        value: dict[str, Any] = {}
        for key, item in pairs:
            if key in value:
                raise AnswerEvaluationError(f"duplicate reviewer output key: {key}")
            value[key] = item
        return value

    stripped = output.strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        stripped = "\n".join(lines)
    try:
        value = json.loads(stripped, object_pairs_hook=object_hook)
    except json.JSONDecodeError as exc:
        raise AnswerEvaluationError(f"reviewer output is not JSON: {exc}") from exc
    if not isinstance(value, dict) or set(value) != {"reviews"}:
        raise AnswerEvaluationError("reviewer output must contain only the reviews array")
    return value


def _resolve_command(command: str) -> str:
    path = Path(command)
    if path.is_file():
        return str(path.resolve())
    suffixes = (".ps1", ".cmd", ".exe", "") if WINDOWS else ("",)
    for directory in os.environ.get("PATH", "").split(os.pathsep):
        for suffix in suffixes:
            candidate = Path(directory) / f"{command}{suffix}"
            if candidate.is_file():
                return str(candidate.resolve())
    raise AnswerEvaluationError(f"reviewer command is unavailable: {command}")


def _command(pi_command: str, model: str, prompt_path: Path) -> list[str]:
    prefix = (
        ["pwsh", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-File", pi_command]
        if Path(pi_command).suffix.lower() == ".ps1"
        else [pi_command]
    )
    return prefix + [
        "--model",
        model,
        "--thinking",
        "medium",
        "--no-tools",
        "--no-extensions",
        "--no-skills",
        "--no-prompt-templates",
        "--no-context-files",
        "--no-session",
        "--print",
        f"@{prompt_path.resolve()}",
    ]


def _run_batch(
    number: int,
    tasks: list[dict[str, Any]],
    batch_dir: Path,
    pi_command: str,
    model: str,
    timeout_seconds: int,
    maximum_attempts: int,
    contract: dict[str, Any],
) -> tuple[int, list[dict[str, Any]]]:
    prompt_path = batch_dir / f"batch-{number:03d}.prompt.txt"
    prompt_path.write_text(_rubric(tasks), encoding="utf-8", newline="\n")
    command = _command(pi_command, model, prompt_path)
    failures: list[str] = []
    for attempt in range(1, maximum_attempts + 1):
        prefix = batch_dir / f"batch-{number:03d}-attempt-{attempt:02d}"
        try:
            completed = subprocess.run(
                command,
                cwd=batch_dir,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="strict",
                timeout=timeout_seconds,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            stdout = exc.stdout if isinstance(exc.stdout, str) else ""
            stderr = exc.stderr if isinstance(exc.stderr, str) else ""
            prefix.with_suffix(".stdout.txt").write_text(stdout, encoding="utf-8", newline="\n")
            prefix.with_suffix(".stderr.txt").write_text(stderr, encoding="utf-8", newline="\n")
            failure = f"attempt {attempt}: timed out after {timeout_seconds} seconds"
            prefix.with_suffix(".validation-error.txt").write_text(failure + "\n", encoding="utf-8")
            failures.append(failure)
            continue
        prefix.with_suffix(".stdout.txt").write_text(completed.stdout, encoding="utf-8", newline="\n")
        prefix.with_suffix(".stderr.txt").write_text(completed.stderr, encoding="utf-8", newline="\n")
        try:
            if completed.returncode != 0:
                raise AnswerEvaluationError(
                    f"reviewer exited {completed.returncode}: {completed.stderr.strip()}"
                )
            reviews = _extract_json(completed.stdout)["reviews"]
            if not isinstance(reviews, list) or len(reviews) != len(tasks):
                raise AnswerEvaluationError("reviewer returned the wrong review count")
            validated = [
                validate_review(review, task, contract)
                for review, task in zip(reviews, tasks, strict=True)
            ]
        except (AnswerEvaluationError, TypeError, ValueError) as exc:
            failure = f"attempt {attempt}: {exc}"
            prefix.with_suffix(".validation-error.txt").write_text(failure + "\n", encoding="utf-8")
            failures.append(failure)
            continue
        return number, validated
    raise AnswerEvaluationError(f"review batch {number} exhausted retries: {'; '.join(failures)}")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--batch-size", type=int, default=5)
    parser.add_argument("--max-concurrency", type=int, default=2)
    parser.add_argument("--pi-command", default="pi")
    parser.add_argument("--batch-dir-name", default="review-batches")
    parser.add_argument("--timeout-seconds", type=int, default=600)
    parser.add_argument("--max-attempts", type=int, default=3)
    args = parser.parse_args(argv)
    try:
        if min(args.batch_size, args.max_concurrency, args.timeout_seconds, args.max_attempts) < 1:
            raise AnswerEvaluationError("batch, concurrency, timeout, and attempt values must be positive")
        if re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", args.batch_dir_name) is None:
            raise AnswerEvaluationError("batch directory name must be one safe path segment")
        contract_path = args.contract.resolve(strict=True)
        contract = load_contract(contract_path)
        tasks, manifest, _ = validate_preparation(args.input_dir, contract, contract_path)
        input_dir = args.input_dir.resolve(strict=True)
        output = (args.output or (input_dir / "reviews.json")).resolve(strict=False)
        try:
            output.relative_to(input_dir)
        except ValueError as exc:
            raise AnswerEvaluationError("review output must remain inside the ignored preparation directory") from exc
        if output.exists():
            raise AnswerEvaluationError(f"append-only review output already exists: {output}")
        batch_dir = input_dir / args.batch_dir_name
        batch_dir.mkdir(exist_ok=False)
        pi_command = _resolve_command(args.pi_command)
        batches = [tasks[index : index + args.batch_size] for index in range(0, len(tasks), args.batch_size)]
        completed: dict[int, list[dict[str, Any]]] = {}
        failures: list[str] = []
        with ThreadPoolExecutor(max_workers=args.max_concurrency) as executor:
            futures = {
                executor.submit(
                    _run_batch,
                    number,
                    batch,
                    batch_dir,
                    pi_command,
                    contract["review"]["model"],
                    args.timeout_seconds,
                    args.max_attempts,
                    contract,
                ): number
                for number, batch in enumerate(batches, start=1)
            }
            for future in as_completed(futures):
                number = futures[future]
                try:
                    batch_number, reviews = future.result()
                except Exception as exc:
                    failures.append(f"batch {number}: {exc}")
                    continue
                completed[batch_number] = reviews
                print(json.dumps({"batch": batch_number, "status": "pass", "reviews": len(reviews)}), flush=True)
        if failures:
            raise AnswerEvaluationError("review failures: " + " | ".join(failures))
        reviews = [review for number in sorted(completed) for review in completed[number]]
        if [review["answer_id"] for review in reviews] != [task["answer_id"] for task in tasks]:
            raise AnswerEvaluationError("merged review order differs from the blinded task order")
        report = {
            "schema_version": contract["review"]["schema_version"],
            "model": contract["review"]["model"],
            "blinded": True,
            "score_values": contract["review"]["score_values"],
            "task_sha256": manifest["task_sha256"],
            "review_count": len(reviews),
            "implementation": {"reviewer": _implementation_binding(REVIEWER)},
            "reviews": reviews,
        }
        write_new(output, json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    except (AnswerEvaluationError, OSError, UnicodeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps({"status": "pass", "reviews": len(reviews), "blinded": True}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
