#!/usr/bin/env python3
"""Prepare and run blinded semantic reviews of grounded Semantic OKF answers."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "semantic-okf-grounded-answer-review/1.0"
MODEL = "openai-codex/gpt-5.6-luna"
SCORE_VALUES = {0, 0.5, 1}
PAPER_RE = re.compile(r"(\d{4})[.-](\d{5})v(\d+)", re.IGNORECASE)


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _paper_id(record: dict[str, Any]) -> str | None:
    for value in (record.get("source_id"), record.get("record_id"), record.get("source_path")):
        if not isinstance(value, str):
            continue
        match = PAPER_RE.search(value)
        if match:
            return f"{match.group(1)}.{match.group(2)}v{match.group(3).lower()}"
    return None


def _records(bundle: Path) -> dict[str, dict[str, Any]]:
    result = {}
    for record in _load_jsonl(bundle / "semantic" / "records.jsonl"):
        record_id = record.get("record_id")
        if isinstance(record_id, str):
            result[record_id] = record
    return result


def _rows(path: Path) -> list[dict[str, Any]]:
    value = json.loads(path.read_text(encoding="utf-8"))
    rows = value.get("results", {}).get("results")
    if not isinstance(rows, list):
        raise ValueError(f"Missing Promptfoo result rows: {path}")
    return rows


def _parse_output(row: dict[str, Any]) -> tuple[dict[str, Any], str]:
    output = row.get("response", {}).get("output")
    if not isinstance(output, str):
        raise ValueError("Promptfoo row has no text output")
    value = json.loads(output)
    if not isinstance(value, dict) or not isinstance(value.get("question_id"), str):
        raise ValueError("Grounded-answer output is not a question object")
    return value, output


def _support_context(answer: dict[str, Any], records: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    candidate = answer.get("answer")
    claims = candidate.get("claims", []) if isinstance(candidate, dict) else []
    claim_ids = sorted(
        {
            claim_id
            for claim in claims
            if isinstance(claim, dict)
            for claim_id in claim.get("supporting_claim_ids", [])
            if isinstance(claim_id, str)
        }
    )
    context = []
    for claim_id in claim_ids:
        record = records.get(claim_id)
        if record is None:
            context.append({"claim_id": claim_id, "status": "missing"})
            continue
        attributes = record.get("attributes", {})
        context.append(
            {
                "claim_id": claim_id,
                "paper_id": _paper_id(record),
                "claim_kind": attributes.get("claim_kind"),
                "interpretation": attributes.get("interpretation"),
                "evidence_locator": attributes.get("evidence_locator"),
                "review_state": attributes.get("review_state"),
            }
        )
    return context


def prepare(args: argparse.Namespace) -> int:
    ground_truth = {item["id"]: item for item in _load_jsonl(args.ground_truth)}
    records = _records(args.bundle)
    tasks = []
    mapping: dict[str, Any] = {}
    for item in args.result:
        method, separator, raw_path = item.partition("=")
        if not separator or not method or not raw_path:
            raise ValueError("Each --result must be METHOD=PATH")
        result_path = Path(raw_path)
        for row in _rows(result_path):
            answer, output_text = _parse_output(row)
            question_id = answer["question_id"]
            if question_id not in ground_truth:
                raise ValueError(f"Unknown question id in output: {question_id}")
            provider = row.get("provider", {})
            profile = provider.get("id") if isinstance(provider, dict) else provider
            if not isinstance(profile, str):
                raise ValueError("Promptfoo row has no profile id")
            output_sha256 = _sha256_bytes(output_text.encode("utf-8"))
            answer_id = _sha256_bytes(f"{method}\0{profile}\0{question_id}\0{output_sha256}".encode())[:24]
            if answer_id in mapping:
                raise ValueError(f"Duplicate answer id: {answer_id}")
            reviewed = ground_truth[question_id]
            task = {
                "answer_id": answer_id,
                "question": reviewed["question"],
                "ground_truth": {
                    "answer_claims": reviewed["ground_truth"]["answer_claims"],
                    "derivation": reviewed["ground_truth"]["derivation"],
                    "important_negatives": reviewed["ground_truth"]["important_negatives"],
                    "acceptable_variants": reviewed["ground_truth"]["acceptable_variants"],
                    "required_paper_ids": reviewed["ground_truth"]["required_paper_ids"],
                },
                "candidate": answer.get("answer"),
                "candidate_support_records": _support_context(answer, records),
            }
            tasks.append(task)
            mapping[answer_id] = {
                "method": method,
                "profile": profile,
                "question_id": question_id,
                "output_sha256": output_sha256,
                "result_path": result_path.as_posix(),
            }

    expected = len(args.result) * 20
    if len(tasks) != expected:
        raise ValueError(f"Expected {expected} answers, found {len(tasks)}")
    tasks.sort(key=lambda item: _sha256_bytes(item["answer_id"].encode()))
    args.output_dir.mkdir(parents=True, exist_ok=False)
    task_path = args.output_dir / "review-tasks.jsonl"
    task_path.write_text("".join(_canonical(task) + "\n" for task in tasks), encoding="utf-8", newline="\n")
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "blinded": True,
        "answer_count": len(tasks),
        "task_sha256": _sha256_bytes(task_path.read_bytes()),
        "mapping": mapping,
    }
    (args.output_dir / "review-manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n"
    )
    print(json.dumps({"status": "prepared", "answers": len(tasks), "blinded": True}))
    return 0


def _rubric(tasks: list[dict[str, Any]]) -> str:
    payload = json.dumps(tasks, ensure_ascii=False, separators=(",", ":"))
    return f"""You are a blinded evaluator of grounded research answers. The candidate labels reveal no method or profile.
Judge only against each supplied ground truth and the supplied authoritative support-record interpretations. Do not use the web or outside knowledge.

For each candidate:
1. Score every candidate claim's semantic fidelity to its cited support records: 1 if fully faithful, 0.5 if partly supported or materially overbroad, 0 if unsupported or contradicted.
2. Score every ground-truth atomic answer claim by id: 1 if the candidate fully conveys it, 0.5 if partial/implicit, 0 if missing or contradicted. Accept listed variants and equivalent evidence when support records justify it.
3. Score every important negative by id with the same 1/0.5/0 scale.
4. Give a neutral note of at most 35 words. Do not reward verbosity, formatting, or the number of citations.

Return one JSON object only: {{"reviews":[...]}}. Preserve the task order. Each review must have exactly:
{{"answer_id":"...","claim_fidelity":[{{"index":0,"score":1}}],"atomic_scores":{{"ground-truth-id":1}},"negative_scores":{{"negative-id":1}},"note":"..."}}
Claim indexes are zero-based and must cover every candidate claim exactly once. Atomic and negative maps must contain every supplied id exactly once. Scores must be exactly 0, 0.5, or 1.

TASKS:
{payload}
"""


def _extract_json(output: str) -> dict[str, Any]:
    stripped = output.strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        stripped = "\n".join(lines)
    value = json.loads(stripped)
    if not isinstance(value, dict):
        raise ValueError("Reviewer output must be an object")
    return value


def _validate_review(review: dict[str, Any], task: dict[str, Any]) -> dict[str, Any]:
    if set(review) != {"answer_id", "claim_fidelity", "atomic_scores", "negative_scores", "note"}:
        raise ValueError(f"Reviewer keys are invalid for {task['answer_id']}")
    if review["answer_id"] != task["answer_id"] or not isinstance(review["note"], str):
        raise ValueError(f"Reviewer identity/note is invalid for {task['answer_id']}")
    claims = task.get("candidate", {}).get("claims", []) if isinstance(task.get("candidate"), dict) else []
    fidelity = review["claim_fidelity"]
    if not isinstance(fidelity, list) or [item.get("index") for item in fidelity] != list(range(len(claims))):
        raise ValueError(f"Reviewer claim indexes are invalid for {task['answer_id']}")
    if any(set(item) != {"index", "score"} or item["score"] not in SCORE_VALUES for item in fidelity):
        raise ValueError(f"Reviewer claim scores are invalid for {task['answer_id']}")
    atom_ids = {item["id"] for item in task["ground_truth"]["answer_claims"]}
    negative_ids = {item["id"] for item in task["ground_truth"]["important_negatives"]}
    if set(review["atomic_scores"]) != atom_ids or set(review["negative_scores"]) != negative_ids:
        raise ValueError(f"Reviewer ground-truth IDs are invalid for {task['answer_id']}")
    if any(score not in SCORE_VALUES for score in review["atomic_scores"].values()):
        raise ValueError(f"Reviewer atomic scores are invalid for {task['answer_id']}")
    if any(score not in SCORE_VALUES for score in review["negative_scores"].values()):
        raise ValueError(f"Reviewer negative scores are invalid for {task['answer_id']}")
    if len(review["note"].split()) > 35:
        raise ValueError(f"Reviewer note is too long for {task['answer_id']}")
    return review


def _run_batch(
    batch_number: int,
    tasks: list[dict[str, Any]],
    work_dir: Path,
    pi_command: str,
    model: str,
    timeout_seconds: int,
    max_attempts: int,
) -> tuple[int, list[dict[str, Any]], str, str]:
    prompt_path = work_dir / f"batch-{batch_number:03d}.prompt.txt"
    prompt_path.write_text(_rubric(tasks), encoding="utf-8", newline="\n")
    command = (
        ["pwsh", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-File", pi_command]
        if Path(pi_command).suffix.lower() == ".ps1"
        else [pi_command]
    ) + [
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
    failures = []
    for attempt in range(1, max_attempts + 1):
        prefix = work_dir / f"batch-{batch_number:03d}-attempt-{attempt:02d}"
        try:
            completed = subprocess.run(
                command,
                cwd=work_dir,
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
                raise RuntimeError(f"process exited {completed.returncode}: {completed.stderr.strip()}")
            value = _extract_json(completed.stdout)
            reviews = value.get("reviews")
            if not isinstance(reviews, list) or len(reviews) != len(tasks):
                raise ValueError("returned the wrong review count")
            validated = [
                _validate_review(review, task)
                for review, task in zip(reviews, tasks, strict=True)
            ]
        except Exception as exc:
            failure = f"attempt {attempt}: {exc}"
            prefix.with_suffix(".validation-error.txt").write_text(failure + "\n", encoding="utf-8")
            failures.append(failure)
            continue
        return batch_number, validated, completed.stdout, completed.stderr
    raise RuntimeError(f"Review batch {batch_number} exhausted retries: {'; '.join(failures)}")


def _resolve_command(command: str) -> str:
    path = Path(command)
    if path.is_file():
        return str(path.resolve())
    for directory in os.environ.get("PATH", "").split(os.pathsep):
        candidate = Path(directory) / command
        if candidate.is_file():
            return str(candidate.resolve())
    raise FileNotFoundError(f"Reviewer command is not available: {command}")


def run(args: argparse.Namespace) -> int:
    tasks = _load_jsonl(args.input_dir / "review-tasks.jsonl")
    manifest = json.loads((args.input_dir / "review-manifest.json").read_text(encoding="utf-8"))
    if manifest.get("task_sha256") != _sha256_bytes((args.input_dir / "review-tasks.jsonl").read_bytes()):
        raise ValueError("Review task hash does not match its manifest")
    if args.output.exists():
        raise FileExistsError(f"Append-only review output exists: {args.output}")
    batches = [tasks[index : index + args.batch_size] for index in range(0, len(tasks), args.batch_size)]
    if re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", args.batch_dir_name) is None:
        raise ValueError("Batch directory name must be one safe path segment")
    batch_dir = args.input_dir / args.batch_dir_name
    batch_dir.mkdir(exist_ok=False)
    pi_command = _resolve_command(args.pi_command)
    completed_reviews: dict[int, list[dict[str, Any]]] = {}
    with ThreadPoolExecutor(max_workers=args.max_concurrency) as executor:
        futures = {
            executor.submit(
                _run_batch,
                number,
                batch,
                batch_dir,
                pi_command,
                args.model,
                args.timeout_seconds,
                args.max_attempts,
            ): number
            for number, batch in enumerate(batches, start=1)
        }
        failures = []
        for future in as_completed(futures):
            try:
                number, reviews, stdout, stderr = future.result()
            except Exception as exc:
                failures.append(f"batch {futures[future]}: {exc}")
                continue
            (batch_dir / f"batch-{number:03d}.stdout.txt").write_text(stdout, encoding="utf-8", newline="\n")
            (batch_dir / f"batch-{number:03d}.stderr.txt").write_text(stderr, encoding="utf-8", newline="\n")
            completed_reviews[number] = reviews
            print(json.dumps({"batch": number, "status": "pass", "reviews": len(reviews)}), flush=True)
    if failures:
        raise RuntimeError("Review failures after all batches completed: " + " | ".join(failures))
    reviews = [review for number in sorted(completed_reviews) for review in completed_reviews[number]]
    if {review["answer_id"] for review in reviews} != {task["answer_id"] for task in tasks}:
        raise ValueError("Merged review identities do not match prepared tasks")
    output = {
        "schema_version": SCHEMA_VERSION,
        "model": args.model,
        "blinded": True,
        "score_values": sorted(SCORE_VALUES),
        "task_sha256": manifest["task_sha256"],
        "review_count": len(reviews),
        "reviews": reviews,
    }
    args.output.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"status": "pass", "reviews": len(reviews), "blinded": True}))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    prepare_parser = subparsers.add_parser("prepare")
    prepare_parser.add_argument("--ground-truth", type=Path, required=True)
    prepare_parser.add_argument("--bundle", type=Path, required=True)
    prepare_parser.add_argument("--result", action="append", required=True)
    prepare_parser.add_argument("--output-dir", type=Path, required=True)

    run_parser = subparsers.add_parser("run")
    run_parser.add_argument("--input-dir", type=Path, required=True)
    run_parser.add_argument("--output", type=Path, required=True)
    run_parser.add_argument("--batch-size", type=int, default=5)
    run_parser.add_argument("--max-concurrency", type=int, default=2)
    run_parser.add_argument("--pi-command", default="pi.ps1")
    run_parser.add_argument("--batch-dir-name", default="batches")
    run_parser.add_argument("--model", default=MODEL)
    run_parser.add_argument("--timeout-seconds", type=int, default=600)
    run_parser.add_argument("--max-attempts", type=int, default=3)

    args = parser.parse_args()
    if args.command == "prepare":
        return prepare(args)
    if (
        args.batch_size < 1
        or args.max_concurrency < 1
        or args.timeout_seconds < 1
        or args.max_attempts < 1
    ):
        raise ValueError("Batch size, concurrency, timeout, and attempts must be positive")
    return run(args)


if __name__ == "__main__":
    raise SystemExit(main())
