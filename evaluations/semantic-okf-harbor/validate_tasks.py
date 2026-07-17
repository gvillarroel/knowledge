#!/usr/bin/env python3
"""Validate generated Harbor tasks, hidden-input isolation, and frozen bindings."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
import tomllib
from pathlib import Path
from typing import Any, Mapping, Sequence

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
ASTRO = REPO / "evaluations/semantic-okf-astro"
DEFAULT_TASKS = HERE / "generated/tasks"
EXPECTED_IDS = [f"q{number:03d}" for number in range(1, 41)]
HEX64 = re.compile(r"\b[0-9a-f]{64}\b")


class ValidationError(ValueError):
    """Raised when a task or benchmark binding is invalid."""


def sha256_file(path: Path) -> str:
    """Return a file SHA-256 digest."""

    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> Any:
    """Load one UTF-8 JSON document."""

    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    """Load one UTF-8 JSON Lines document."""

    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def validate_authoritative_mapping(task_dir: Path, truth: Mapping[str, Any]) -> None:
    """Exercise the real grader's raw-file to normalized-record locator join."""

    score_path = task_dir / "tests/score.py"
    spec = importlib.util.spec_from_file_location(f"semantic_okf_harbor_score_{task_dir.name}", score_path)
    if spec is None or spec.loader is None:
        raise ValidationError(f"{task_dir.name}: grader cannot be imported")
    grader = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(grader)
    rows = load_jsonl(task_dir / "tests/records.jsonl")
    ledger = {(str(row.get("source_id")), str(row.get("record_id"))): row for row in rows}
    try:
        ranges = grader.authoritative_ranges(truth, task_dir / "tests/authority", ledger)
    except grader.ScoreError as exc:
        raise ValidationError(f"{task_dir.name}: authoritative locator mapping failed: {exc}") from exc
    expected = {str(row["id"]) for row in truth.get("authoritative_evidence", [])}
    if set(ranges) != expected:
        raise ValidationError(f"{task_dir.name}: authoritative locator mapping is incomplete")


def forbidden_fragments(
    question: Mapping[str, Any], truth: Mapping[str, Any] | None
) -> set[str]:
    """Collect evaluator-only exact values that may not appear in instructions."""

    values: set[str] = set()
    qrels = question.get("qrels", {})
    if isinstance(qrels, Mapping):
        values.update(str(item) for item in qrels.get("document_ids", []))
        values.update(str(item) for item in qrels.get("source_ids", []))
    if truth is not None:
        for row in truth.get("authoritative_evidence", []):
            if not isinstance(row, Mapping):
                continue
            for key in ("path", "locator", "file_sha256", "text_sha256", "upstream_path"):
                if isinstance(row.get(key), str):
                    values.add(row[key])
        ground = truth.get("ground_truth", {})
        if isinstance(ground, Mapping):
            for collection in ("answer_claims", "important_negatives"):
                for row in ground.get(collection, []):
                    if isinstance(row, Mapping) and isinstance(row.get("statement"), str):
                        values.add(row["statement"])
    return {value for value in values if len(value) >= 8}


def validate_task(
    task_dir: Path,
    question: Mapping[str, Any],
    truth: Mapping[str, Any] | None,
    expected_split: str,
) -> list[str]:
    """Validate one generated task and return non-fatal warnings."""

    identifier = str(question["id"])
    required = [
        task_dir / "instruction.md",
        task_dir / "task.toml",
        task_dir / "environment",
        task_dir / "tests/Dockerfile",
        task_dir / "tests/test.sh",
        task_dir / "tests/score.py",
        task_dir / "tests/question.json",
        task_dir / "tests/records.jsonl",
        task_dir / "tests/source-combination.json",
        task_dir / "solution/solve.sh",
        task_dir / "solution/oracle-pi.jsonl",
    ]
    missing = [path.relative_to(task_dir).as_posix() for path in required if not path.exists()]
    if missing:
        raise ValidationError(f"{identifier}: missing {missing}")
    instruction = (task_dir / "instruction.md").read_text(encoding="utf-8")
    if instruction.count(str(question["question"])) != 1:
        raise ValidationError(f"{identifier}: question text is absent or duplicated")
    leaked = sorted(value for value in forbidden_fragments(question, truth) if value in instruction)
    if leaked:
        raise ValidationError(f"{identifier}: evaluator-only value leaked")
    unexpected_hashes = [value for value in HEX64.findall(instruction)]
    if unexpected_hashes:
        raise ValidationError(f"{identifier}: instruction contains a hidden hash")
    config = tomllib.loads((task_dir / "task.toml").read_text(encoding="utf-8"))
    if config.get("schema_version") != "1.3":
        raise ValidationError(f"{identifier}: wrong Harbor schema")
    metadata = config.get("metadata", {})
    if metadata.get("split") != expected_split or metadata.get("question_type") != question["question_type"]:
        raise ValidationError(f"{identifier}: task metadata mismatch")
    if config.get("verifier", {}).get("environment_mode") != "separate":
        raise ValidationError(f"{identifier}: verifier is not separate")
    artifacts = config.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts or artifacts[0].get("source") != "/logs/agent/pi.txt":
        raise ValidationError(f"{identifier}: Pi log artifact is not bound")
    environment_files = [path for path in (task_dir / "environment").rglob("*") if path.is_file()]
    for path in environment_files:
        content = path.read_text(encoding="utf-8", errors="ignore")
        if "solution" in content.lower() or "tests" in content.lower():
            raise ValidationError(f"{identifier}: agent image references hidden directories")
    hidden_question = load_json(task_dir / "tests/question.json")
    if hidden_question != question:
        raise ValidationError(f"{identifier}: hidden question/qrel drift")
    hard_path = task_dir / "tests/hard-ground-truth.json"
    if (truth is not None) != hard_path.exists():
        raise ValidationError(f"{identifier}: hard-ground-truth presence mismatch")
    if truth is not None and load_json(hard_path) != truth:
        raise ValidationError(f"{identifier}: hard-ground-truth drift")
    if truth is not None:
        validate_authoritative_mapping(task_dir, truth)
    return []


def harbor_task_smoke(task_dirs: Sequence[Path]) -> None:
    """Load representative tasks with Harbor when its WSL installation is available."""

    code = """
import sys
from pathlib import Path
from harbor.models.task.task import Task
for value in sys.argv[1:]:
    task = Task(Path(value))
    assert task.config.schema_version == '1.3'
print(len(sys.argv) - 1)
"""
    if sys.platform != "win32":
        try:
            import harbor  # type: ignore  # noqa: F401
        except ImportError:
            return
        subprocess.run([sys.executable, "-c", code, *[str(path) for path in task_dirs]], check=True)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse validation paths."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tasks", type=Path, default=DEFAULT_TASKS)
    parser.add_argument("--skip-generation-check", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    """Validate all forty tasks and deterministic regeneration."""

    args = parse_args(argv)
    tasks = args.tasks.resolve()
    questions = load_jsonl(ASTRO / "benchmark/retrieval-questions.jsonl")
    truths = {row["id"]: row for row in load_jsonl(ASTRO / "benchmark/hard-ground-truth.jsonl")}
    splits = load_json(HERE / "splits.json")["cohorts"]
    split_by_id = {identifier: split for split, identifiers in splits.items() for identifier in identifiers}
    if [row.get("id") for row in questions] != EXPECTED_IDS:
        raise SystemExit("frozen questions are not q001 through q040")
    for row in questions:
        identifier = row["id"]
        validate_task(tasks / split_by_id[identifier] / identifier, row, truths.get(identifier), split_by_id[identifier])
    manifest = load_json(tasks / "manifest.json")
    if manifest.get("question_count") != 40 or manifest.get("cohort_counts") != {"train": 24, "dev": 8, "holdout": 8}:
        raise SystemExit("generated manifest counts are invalid")
    if not args.skip_generation_check:
        subprocess.run(
            [
                sys.executable,
                str(HERE / "generate_tasks.py"),
                "--output",
                str(tasks),
                "--check",
                "--verifier-network-mode",
                str(manifest["verifier_network_mode"]),
                "--agent-network-mode",
                str(manifest["agent_network_mode"]),
            ],
            check=True,
            cwd=REPO,
        )
    representatives = [tasks / "train/q001", tasks / "dev/q032", tasks / "holdout/q034"]
    harbor_task_smoke(representatives)
    print(json.dumps({"status": "pass", "task_count": 40, "leak_checks": "pass", "deterministic": not args.skip_generation_check}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
