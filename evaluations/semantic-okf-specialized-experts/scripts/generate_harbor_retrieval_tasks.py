#!/usr/bin/env python3
"""Generate sealed Harbor tasks for specialized-expert retrieval Pareto search."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shlex
import shutil
import tempfile
from typing import Any, Mapping, Sequence


SCRIPT_PATH = Path(__file__).resolve()
EVALUATION_ROOT = SCRIPT_PATH.parents[1]
REPO_ROOT = SCRIPT_PATH.parents[3]
GRADER_ROOT = EVALUATION_ROOT / "harbor" / "grader"
TRACE_STATUS = (
    REPO_ROOT
    / "evaluations"
    / "semantic-okf-harbor"
    / "grader"
    / "trace_status.py"
)
DEFAULT_QUESTIONS = (
    REPO_ROOT
    / "evaluations"
    / "semantic-okf-adaptive"
    / "retrieval-questions.jsonl"
)
RUNTIME_TAG = "semantic-okf-harbor-runtime:1.0"


class GenerationError(ValueError):
    """Raised when a frozen retrieval task set cannot be generated."""


def write_text(path: Path, value: str) -> None:
    """Write LF-normalized UTF-8 text."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        value.replace("\r\n", "\n"),
        encoding="utf-8",
        newline="\n",
    )


def write_json(path: Path, value: Any) -> None:
    """Write deterministic JSON."""

    write_text(
        path,
        json.dumps(
            value,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
            allow_nan=False,
        )
        + "\n",
    )


def sha256_file(path: Path) -> str:
    """Hash one file."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def tree_inventory(root: Path) -> list[dict[str, Any]]:
    """Return a deterministic regular-file inventory."""

    rows: list[dict[str, Any]] = []
    for path in sorted(root.rglob("*"), key=lambda item: item.relative_to(root).as_posix()):
        if path.is_symlink():
            raise GenerationError(f"tree contains a symlink: {path}")
        if path.is_file():
            rows.append(
                {
                    "path": path.relative_to(root).as_posix(),
                    "bytes": path.stat().st_size,
                    "sha256": sha256_file(path),
                }
            )
    return rows


def canonical_digest(value: Any) -> str:
    """Hash one canonical JSON value."""

    payload = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def load_json(path: Path) -> Mapping[str, Any]:
    """Load one JSON object."""

    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, Mapping):
        raise GenerationError(f"expected a JSON object: {path}")
    return value


def load_questions(path: Path) -> list[Mapping[str, Any]]:
    """Load and validate the frozen retrieval questions."""

    rows: list[Mapping[str, Any]] = []
    seen: set[str] = set()
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, Mapping):
            raise GenerationError(f"question line {number} is not an object")
        identifier = value.get("id")
        question = value.get("question")
        qrels = value.get("qrels")
        if (
            not isinstance(identifier, str)
            or not identifier
            or identifier in seen
            or not isinstance(question, str)
            or not question.strip()
            or not isinstance(qrels, Mapping)
            or not isinstance(qrels.get("paper_ids"), list)
            or not qrels["paper_ids"]
        ):
            raise GenerationError(f"invalid question contract on line {number}")
        seen.add(identifier)
        rows.append(value)
    if not rows:
        raise GenerationError("question set is empty")
    return rows


def resolve_ids(
    questions: Sequence[Mapping[str, Any]],
    requested: Sequence[str],
    *,
    label: str,
) -> list[Mapping[str, Any]]:
    """Resolve full or qNNN-prefixed question identifiers."""

    if not requested:
        raise GenerationError(f"{label} question ids are required")
    if len(set(requested)) != len(requested):
        raise GenerationError(f"{label} question ids must be unique")
    by_id: dict[str, Mapping[str, Any]] = {}
    for row in questions:
        identifier = str(row["id"])
        short = identifier.split("-", 1)[0]
        for key in (identifier, short):
            if key in by_id and by_id[key] is not row:
                raise GenerationError(f"ambiguous question identifier: {key}")
            by_id[key] = row
    missing = [identifier for identifier in requested if identifier not in by_id]
    if missing:
        raise GenerationError(
            f"unknown {label} question ids: {', '.join(sorted(missing))}"
        )
    return [by_id[identifier] for identifier in requested]


def task_toml(identifier: str, cohort: str) -> str:
    """Render one native Harbor task declaration."""

    name = f"knowledge/graphrag-papers-40__expert-retrieval__{identifier}"
    return f"""schema_version = "1.3"
artifacts = [
  {{ source = "/logs/agent/pi.txt", destination = "pi.jsonl" }},
  {{ source = "/logs/agent/retrieval.json", destination = "retrieval.json" }},
]

[task]
name = {json.dumps(name)}
description = {json.dumps(f"Specialized-expert retrieval case in the {cohort} cohort.")}
keywords = ["semantic-okf", "graphrag-papers-40", "expert-retrieval", "pareto"]

[metadata]
difficulty = "easy"
category = "knowledge-retrieval-evaluation"
dataset_id = "graphrag-papers-40"
mode = "expert-retrieval"
cohort = {json.dumps(cohort)}

[agent]
timeout_sec = 180.0
network_mode = "public"

[verifier]
timeout_sec = 60.0
environment_mode = "separate"
network_mode = "public"

[verifier.environment]
os = "linux"
network_mode = "public"
memory_mb = 2048

[environment]
docker_image = {json.dumps(RUNTIME_TAG)}
os = "linux"
network_mode = "public"
memory_mb = 4096
storage_mb = 8192
workdir = "/workspace"
"""


def instruction(
    row: Mapping[str, Any],
    *,
    skill_name: str,
) -> str:
    """Render a retrieval-only instruction without exposing qrels."""

    question = str(row["question"])
    command = (
        f"python -B /root/.agents/skills/{skill_name}/scripts/"
        "query_expert_knowledge.py search "
        f"--contains {shlex.quote(question)} --limit 10 "
        "> /logs/agent/retrieval.json"
    )
    return f"""Use only the sole installed `{skill_name}` skill and its embedded
read-only knowledge. Do not use the web, model memory, or any other skill. Read its
complete `SKILL.md`, then execute this exact retrieval command once:

```bash
{command}
```

After the command succeeds, return exactly `{{"status":"retrieval-written"}}` as
the final answer. Do not open, rewrite, summarize, or manually copy the retrieval
artifact.
"""


def create_task(
    output: Path,
    cohort: str,
    row: Mapping[str, Any],
    *,
    expected: Mapping[str, Any],
    ledger: Path,
) -> None:
    """Create one complete Harbor task."""

    identifier = str(row["id"])
    task = output / cohort / identifier
    tests = task / "tests"
    (task / "environment").mkdir(parents=True)
    tests.mkdir(parents=True)
    write_text(task / "instruction.md", instruction(row, skill_name=str(expected["skill_name"])))
    write_text(task / "task.toml", task_toml(identifier, cohort))
    write_json(
        tests / "question.json",
        {
            "id": identifier,
            "question": row["question"],
            "qrels": {"paper_ids": list(row["qrels"]["paper_ids"])},
            "top_k": 10,
            "expected": dict(expected),
        },
    )
    for source in (
        GRADER_ROOT / "score.py",
        GRADER_ROOT / "test.sh",
        GRADER_ROOT / "Dockerfile",
        TRACE_STATUS,
    ):
        if not source.is_file():
            raise GenerationError(f"grader asset is missing: {source}")
        shutil.copyfile(source, tests / source.name)
    shutil.copyfile(ledger, tests / "records.jsonl")


def generate(
    *,
    expert: Path,
    questions_path: Path,
    development_ids: Sequence[str],
    holdout_ids: Sequence[str],
    output: Path,
) -> None:
    """Generate one sealed development/holdout task tree."""

    if output.exists() or output.is_symlink():
        raise GenerationError(f"output already exists: {output}")
    manifest_path = expert / "expert-manifest.json"
    ledger = expert / "references" / "knowledge" / "semantic" / "records.jsonl"
    if not manifest_path.is_file() or not ledger.is_file():
        raise GenerationError("expert lacks its manifest or embedded ledger")
    manifest = load_json(manifest_path)
    knowledge = manifest.get("knowledge")
    tree = knowledge.get("tree") if isinstance(knowledge, Mapping) else None
    if (
        manifest.get("schema_version") != "semantic-okf-expert-skill/1.0"
        or manifest.get("skill_name") != expert.name
        or not isinstance(tree, Mapping)
    ):
        raise GenerationError("expert manifest binding is invalid")
    expected = {
        "skill_name": manifest["skill_name"],
        "knowledge_tree_sha256": tree.get("sha256"),
        "knowledge_file_count": tree.get("file_count"),
        "record_count": knowledge.get("record_count"),
    }
    if (
        not isinstance(expected["knowledge_tree_sha256"], str)
        or not isinstance(expected["knowledge_file_count"], int)
        or not isinstance(expected["record_count"], int)
    ):
        raise GenerationError("expert knowledge binding is incomplete")

    questions = load_questions(questions_path)
    development = resolve_ids(questions, development_ids, label="development")
    holdout = resolve_ids(questions, holdout_ids, label="holdout")
    development_names = {str(row["id"]) for row in development}
    holdout_names = {str(row["id"]) for row in holdout}
    overlap = sorted(development_names & holdout_names)
    if overlap:
        raise GenerationError(
            "development and holdout overlap: " + ", ".join(overlap)
        )

    output.mkdir(parents=True)
    for cohort, rows in (("development", development), ("holdout", holdout)):
        for row in rows:
            create_task(
                output,
                cohort,
                row,
                expected=expected,
                ledger=ledger,
            )
    inventory = tree_inventory(output)
    write_json(
        output / "dataset-manifest.json",
        {
            "schema_version": "specialized-expert-harbor-retrieval-tasks/1.1",
            "dataset_id": "graphrag-papers-40",
            "evaluation_mode": "expert-retrieval",
            "expert": {
                "skill_name": expert.name,
                "manifest_sha256": sha256_file(manifest_path),
                **expected,
            },
            "questions": {
                "path": questions_path.as_posix(),
                "sha256": sha256_file(questions_path),
            },
            "cohorts": {
                "development": [str(row["id"]) for row in development],
                "holdout": [str(row["id"]) for row in holdout],
            },
            "payload_file_count": len(inventory),
            "payload_inventory_sha256": canonical_digest(inventory),
        },
    )


def compare_trees(expected: Path, actual: Path) -> None:
    """Require byte-identical generated trees."""

    expected_inventory = tree_inventory(expected)
    actual_inventory = tree_inventory(actual)
    if expected_inventory != actual_inventory:
        raise GenerationError("generated task tree drift")


def build_parser() -> argparse.ArgumentParser:
    """Build the task generator CLI."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--expert", type=Path, required=True)
    parser.add_argument("--questions", type=Path, default=DEFAULT_QUESTIONS)
    parser.add_argument("--development-id", action="append", default=[])
    parser.add_argument("--holdout-id", action="append", default=[])
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Generate or deterministically verify one task tree."""

    args = build_parser().parse_args(argv)
    try:
        if args.check:
            if not args.output.is_dir():
                raise GenerationError(f"checked output is absent: {args.output}")
            with tempfile.TemporaryDirectory(
                prefix="specialized-expert-harbor-check-"
            ) as temporary:
                rebuilt = Path(temporary) / args.output.name
                generate(
                    expert=args.expert.resolve(),
                    questions_path=args.questions.resolve(),
                    development_ids=args.development_id,
                    holdout_ids=args.holdout_id,
                    output=rebuilt,
                )
                compare_trees(args.output.resolve(), rebuilt)
        else:
            generate(
                expert=args.expert.resolve(),
                questions_path=args.questions.resolve(),
                development_ids=args.development_id,
                holdout_ids=args.holdout_id,
                output=args.output.resolve(),
            )
    except (
        GenerationError,
        OSError,
        UnicodeError,
        json.JSONDecodeError,
        TypeError,
        KeyError,
    ) as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, sort_keys=True))
        return 2
    print(
        json.dumps(
            {
                "status": "pass",
                "mode": "check" if args.check else "generate",
                "output": str(args.output),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
