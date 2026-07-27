#!/usr/bin/env python3
"""Generate deterministic Oracle Harbor tasks for Tantivy retrieval evolution."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence


SCHEMA_VERSION = "semantic-okf-tantivy-evolution-tasks/1.0"
COHORT_SCHEMA = "semantic-okf-evaluation-cohorts/1.0"
TASK_IMAGE = "semantic-okf-tantivy-evolution-runtime:1.0"
TASKS_PER_PARTITION = 4


class TaskGenerationError(RuntimeError):
    """Describe invalid inputs or generated-task drift."""


def json_bytes(value: Any) -> bytes:
    """Serialize stable human-readable JSON."""

    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def strict_json(text: str, label: str) -> Any:
    """Load strict JSON while rejecting duplicate keys and non-finite values."""

    def reject_constant(value: str) -> Any:
        raise TaskGenerationError(f"{label} contains non-standard number {value!r}")

    def reject_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise TaskGenerationError(f"{label} contains duplicate key {key!r}")
            result[key] = value
        return result

    try:
        return json.loads(
            text,
            object_pairs_hook=reject_duplicates,
            parse_constant=reject_constant,
        )
    except json.JSONDecodeError as exc:
        raise TaskGenerationError(f"{label} is invalid JSON: {exc}") from exc


def read_json(path: Path, label: str) -> Any:
    """Read one strict UTF-8 JSON file."""

    try:
        return strict_json(path.read_text(encoding="utf-8"), label)
    except (OSError, UnicodeError) as exc:
        raise TaskGenerationError(f"cannot read {label}: {exc}") from exc


def read_questions(path: Path) -> dict[str, dict[str, Any]]:
    """Load the canonical paper-qrel questions by short identifier."""

    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        raise TaskGenerationError(f"cannot read questions: {exc}") from exc
    result: dict[str, dict[str, Any]] = {}
    for number, line in enumerate(lines, start=1):
        row = strict_json(line, f"questions:{number}")
        if not isinstance(row, dict) or set(row) != {"id", "question", "qrels"}:
            raise TaskGenerationError(f"questions:{number} has an invalid schema")
        identifier = row["id"]
        question = row["question"]
        qrels = row["qrels"]
        if (
            not isinstance(identifier, str)
            or not isinstance(question, str)
            or not question
            or not isinstance(qrels, dict)
            or set(qrels) != {"paper_ids", "source_ids"}
        ):
            raise TaskGenerationError(f"questions:{number} has invalid values")
        short_id = identifier.split("-", 1)[0]
        if short_id in result:
            raise TaskGenerationError(f"duplicate question prefix {short_id!r}")
        paper_ids = qrels["paper_ids"]
        if (
            not isinstance(paper_ids, list)
            or not paper_ids
            or any(not isinstance(value, str) or not value for value in paper_ids)
            or len(paper_ids) != len(set(paper_ids))
        ):
            raise TaskGenerationError(f"{identifier} paper qrels are invalid")
        result[short_id] = {
            "id": identifier,
            "short_id": short_id,
            "question": question,
            "paper_ids": sorted(paper_ids),
        }
    if len(result) != 40:
        raise TaskGenerationError(
            f"canonical task generation requires 40 questions, found {len(result)}"
        )
    return result


def read_cohorts(path: Path) -> dict[str, tuple[str, ...]]:
    """Load the canonical GraphRAG development and holdout partitions."""

    payload = read_json(path, "cohort registry")
    if (
        not isinstance(payload, dict)
        or payload.get("schema_version") != COHORT_SCHEMA
        or payload.get("dataset_id") != "graphrag-papers-40"
        or not isinstance(payload.get("cohorts"), dict)
    ):
        raise TaskGenerationError("cohort registry has an invalid schema")
    required = {
        "development": tuple(payload["cohorts"].get("discovery", ())),
        "holdout": tuple(
            [
                *payload["cohorts"].get("holdout", ()),
                *payload["cohorts"].get("hard", ()),
            ]
        ),
    }
    for name, values in required.items():
        if (
            not values
            or any(not isinstance(value, str) or not value for value in values)
            or len(values) != len(set(values))
        ):
            raise TaskGenerationError(f"{name} cohort is invalid")
    if set(required["development"]) & set(required["holdout"]):
        raise TaskGenerationError("development and holdout cohorts overlap")
    return required


def partitions(values: Sequence[str]) -> list[tuple[str, ...]]:
    """Split a cohort into stable four-question cases."""

    return [
        tuple(values[index : index + TASKS_PER_PARTITION])
        for index in range(0, len(values), TASKS_PER_PARTITION)
    ]


RUN_CANDIDATE = r'''#!/usr/bin/env python3
"""Run the installed Tantivy candidate over this task's question partition."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path


QUESTIONS = Path("/solution/questions.json")
OUTPUT = Path("/logs/agent/tantivy-results.json")
QUERY = Path(
    "/harbor/skills/consult-semantic-okf-tantivy/scripts/"
    "query_semantic_okf_tantivy.py"
)
TOKEN_RE = re.compile(r"[A-Za-z0-9]+")


def main() -> int:
    questions = json.loads(QUESTIONS.read_text(encoding="utf-8"))
    results = []
    for row in questions:
        query = " ".join(TOKEN_RE.findall(row["question"]))
        completed = subprocess.run(
            [
                sys.executable,
                str(QUERY),
                "/knowledge",
                "search",
                "--query",
                query,
                "--top-k",
                "10",
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=120,
            check=False,
        )
        payload = None
        if completed.stdout.strip():
            payload = json.loads(completed.stdout)
        results.append(
            {
                "question_id": row["id"],
                "return_code": completed.returncode,
                "response": payload,
                "stderr": completed.stderr[-1000:],
            }
        )
    OUTPUT.write_text(
        json.dumps(
            {"schema_version": "tantivy-oracle-retrieval/1.0", "results": results},
            ensure_ascii=False,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''


SCORE = r'''#!/usr/bin/env python3
"""Score one deterministic Tantivy retrieval partition."""

from __future__ import annotations

import hashlib
import json
import math
import re
from pathlib import Path, PurePosixPath


OUTPUT = Path("/logs/agent/tantivy-results.json")
QRELS = Path("/tests/qrels.json")
REWARD = Path("/logs/verifier/reward.json")
DIAGNOSTICS = Path("/logs/verifier/diagnostics.json")
HEX_64 = re.compile(r"[0-9a-f]{64}")


def write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def dcg(relevance: list[int]) -> float:
    return sum(value / math.log2(rank + 1) for rank, value in enumerate(relevance, 1))


def valid_path(value: object) -> bool:
    if not isinstance(value, str) or not value or "\\" in value:
        return False
    path = PurePosixPath(value)
    return (
        not path.is_absolute()
        and bool(path.parts)
        and all(part not in {"", ".", ".."} for part in path.parts)
    )


def valid_hit(hit: object, rank: int) -> bool:
    if not isinstance(hit, dict) or hit.get("rank") != rank:
        return False
    strings = (
        "document_id",
        "source_id",
        "record_id",
        "record_sha256",
        "concept_id",
        "concept_type",
        "concept_path",
        "source_path",
        "text",
        "text_sha256",
    )
    if any(not isinstance(hit.get(name), str) or not hit[name] for name in strings):
        return False
    if not HEX_64.fullmatch(hit["record_sha256"]) or not HEX_64.fullmatch(
        hit["text_sha256"]
    ):
        return False
    if hashlib.sha256(hit["text"].encode("utf-8")).hexdigest() != hit["text_sha256"]:
        return False
    if not valid_path(hit["concept_path"]) or not valid_path(hit["source_path"]):
        return False
    locator = hit.get("locator")
    return locator == {"kind": "record"} or (
        isinstance(locator, dict)
        and set(locator) == {"kind", "start", "end"}
        and locator.get("kind") == "character-range"
        and isinstance(locator.get("start"), int)
        and isinstance(locator.get("end"), int)
        and 0 <= locator["start"] < locator["end"]
    )


def main() -> int:
    try:
        output = json.loads(OUTPUT.read_text(encoding="utf-8"))
        qrels = json.loads(QRELS.read_text(encoding="utf-8"))
        rows = output["results"]
        expected = qrels["questions"]
        if len(rows) != len(expected):
            raise ValueError("candidate result count differs from the task partition")
        recall_values = []
        mrr_values = []
        ndcg_values = []
        evidence_rows = 0
        valid_evidence_rows = 0
        errors = []
        for row, truth in zip(rows, expected, strict=True):
            if row.get("question_id") != truth["id"] or row.get("return_code") != 0:
                errors.append(str(truth["id"]))
                continue
            response = row.get("response")
            if not isinstance(response, dict) or response.get("status") != "pass":
                errors.append(str(truth["id"]))
                continue
            hits = response.get("results")
            if not isinstance(hits, list) or len(hits) > 10:
                errors.append(str(truth["id"]))
                continue
            evidence_rows += len(hits)
            valid_evidence_rows += sum(
                valid_hit(hit, rank) for rank, hit in enumerate(hits, 1)
            )
            relevant = set(truth["paper_ids"])
            ranked = []
            seen = set()
            for hit in hits:
                paper = hit.get("paper_id")
                if not isinstance(paper, str) or not paper or paper in seen:
                    continue
                seen.add(paper)
                ranked.append(paper)
            relevance = [1 if paper in relevant else 0 for paper in ranked[:10]]
            covered = sum(relevance)
            recall_values.append(covered / len(relevant))
            first = next(
                (rank for rank, value in enumerate(relevance, 1) if value),
                None,
            )
            mrr_values.append(1.0 / first if first else 0.0)
            ideal = dcg([1] * min(10, len(relevant)))
            ndcg_values.append(dcg(relevance) / ideal if ideal else 0.0)
        complete = not errors and len(recall_values) == len(expected)
        evidence_validity = (
            valid_evidence_rows / evidence_rows if evidence_rows else 0.0
        )
        recall = sum(recall_values) / len(recall_values) if complete else 0.0
        mrr = sum(mrr_values) / len(mrr_values) if complete else 0.0
        ndcg = sum(ndcg_values) / len(ndcg_values) if complete else 0.0
        mechanical = 1.0 if complete else 0.0
        evidence_gate = 1.0 if evidence_validity == 1.0 else 0.0
        rewards = {
            "reward": mechanical * evidence_gate * ((recall + mrr + ndcg) / 3.0),
            "recall_at_10": recall,
            "mrr_at_10": mrr,
            "ndcg_at_10": ndcg,
            "evidence_contract_gate": evidence_gate,
            "mechanical_qualification_gate": mechanical,
        }
        diagnostics = {
            "schema_version": "tantivy-retrieval-diagnostics/1.0",
            "status": "scored-response" if mechanical and evidence_gate else "candidate-failure",
            "failure_domain": None,
            "terminal_outcome": "complete" if complete else "invalid-output",
            "error_code": None if complete else "candidate-output-invalid",
            "question_count": len(expected),
            "candidate_errors": errors,
            "evidence_rows": evidence_rows,
            "valid_evidence_rows": valid_evidence_rows,
        }
    except Exception as exc:
        rewards = {
            "reward": 0.0,
            "recall_at_10": 0.0,
            "mrr_at_10": 0.0,
            "ndcg_at_10": 0.0,
            "evidence_contract_gate": 0.0,
            "mechanical_qualification_gate": 0.0,
        }
        diagnostics = {
            "schema_version": "tantivy-retrieval-diagnostics/1.0",
            "status": "verifier-error",
            "failure_domain": "evaluator",
            "terminal_outcome": "verifier-error",
            "error_code": type(exc).__name__,
        }
    write(REWARD, rewards)
    write(DIAGNOSTICS, diagnostics)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''


TEST_SH = """#!/usr/bin/env bash
set -euo pipefail
python /tests/score.py
"""


SOLVE_SH = """#!/usr/bin/env bash
set -euo pipefail
mkdir -p /logs/agent
python /solution/run_candidate.py
"""


def task_toml(phase: str, index: int) -> str:
    """Render one Harbor task declaration."""

    return f"""schema_version = "1.3"
artifacts = [
  {{ source = "/logs/agent/tantivy-results.json", destination = "tantivy-results.json" }},
]

[task]
name = "knowledge/tantivy-consult-evolution__{phase}__part-{index:02d}"
description = "Deterministic Tantivy consultation {phase} retrieval partition."
keywords = ["semantic-okf", "tantivy", "retrieval", "evolution", "{phase}"]

[metadata]
difficulty = "medium"
category = "retrieval-evaluation"
dataset_id = "graphrag-papers-40"
family = "tantivy"
phase = "{phase}"

[agent]
timeout_sec = 300.0
network_mode = "public"

[verifier]
timeout_sec = 120.0
environment_mode = "separate"
network_mode = "public"

[verifier.environment]
os = "linux"
network_mode = "public"
memory_mb = 2048

[environment]
docker_image = "{TASK_IMAGE}"
os = "linux"
network_mode = "public"
memory_mb = 4096
storage_mb = 8192
workdir = "/workspace"
"""


def instruction(phase: str, identifiers: Sequence[str]) -> str:
    """Render a qrel-free public instruction."""

    joined = ", ".join(identifiers)
    return (
        "Use the sole installed `consult-semantic-okf-tantivy` skill and the "
        "read-only snapshot at `/knowledge` to run the declared retrieval "
        f"partition. This is a deterministic {phase} task covering {joined}. "
        "Do not build, repair, or modify knowledge. Preserve exact evidence "
        "identities and write no files into the snapshot.\n"
    )


def expected_files(
    questions_path: Path,
    cohorts_path: Path,
) -> dict[str, bytes]:
    """Build the complete deterministic generated tree in memory."""

    questions = read_questions(questions_path)
    cohorts = read_cohorts(cohorts_path)
    files: dict[str, bytes] = {}
    manifest_tasks: list[dict[str, Any]] = []
    for phase, identifiers in cohorts.items():
        for index, group in enumerate(partitions(identifiers), start=1):
            task = f"{phase}/part-{index:02d}"
            selected = [questions[identifier] for identifier in group]
            files[f"{task}/task.toml"] = task_toml(phase, index).encode("utf-8")
            files[f"{task}/instruction.md"] = instruction(phase, group).encode(
                "utf-8"
            )
            files[f"{task}/solution/solve.sh"] = SOLVE_SH.encode("utf-8")
            files[f"{task}/solution/run_candidate.py"] = RUN_CANDIDATE.encode(
                "utf-8"
            )
            files[f"{task}/solution/questions.json"] = json_bytes(
                [
                    {
                        "id": row["id"],
                        "short_id": row["short_id"],
                        "question": row["question"],
                    }
                    for row in selected
                ]
            )
            files[f"{task}/tests/test.sh"] = TEST_SH.encode("utf-8")
            files[f"{task}/tests/score.py"] = SCORE.encode("utf-8")
            files[f"{task}/tests/qrels.json"] = json_bytes(
                {
                    "schema_version": "tantivy-retrieval-qrels/1.0",
                    "questions": [
                        {"id": row["id"], "paper_ids": row["paper_ids"]}
                        for row in selected
                    ],
                }
            )
            files[f"{task}/tests/Dockerfile"] = (
                f"FROM {TASK_IMAGE}\n"
                "COPY . /tests\n"
                "RUN chmod 0555 /tests/test.sh /tests/score.py\n"
                "WORKDIR /tests\n"
            ).encode("utf-8")
            manifest_tasks.append(
                {
                    "phase": phase,
                    "task": task,
                    "question_ids": list(group),
                }
            )
    file_rows = [
        {"path": path, "sha256": hashlib.sha256(payload).hexdigest()}
        for path, payload in sorted(files.items())
    ]
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "status": "pass",
        "task_image": TASK_IMAGE,
        "questions_per_task": TASKS_PER_PARTITION,
        "tasks": manifest_tasks,
        "file_count_excluding_manifest": len(files),
        "tree_sha256_excluding_manifest": hashlib.sha256(
            json.dumps(
                file_rows,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest(),
    }
    files["manifest.json"] = json_bytes(manifest)
    return files


def publish(files: Mapping[str, bytes], output: Path, check: bool) -> None:
    """Create or verify the exact generated tree."""

    if check:
        if not output.is_dir():
            raise TaskGenerationError(f"generated task root is missing: {output}")
        actual = {
            path.relative_to(output).as_posix(): path.read_bytes()
            for path in sorted(output.rglob("*"))
            if path.is_file()
        }
        if actual != files:
            missing = sorted(set(files) - set(actual))
            unknown = sorted(set(actual) - set(files))
            changed = sorted(
                path
                for path in set(files) & set(actual)
                if files[path] != actual[path]
            )
            raise TaskGenerationError(
                "generated task drift: "
                f"missing={missing}, unknown={unknown}, changed={changed}"
            )
        return
    if output.exists() or output.is_symlink():
        raise TaskGenerationError(f"output already exists: {output}")
    output.mkdir(parents=True)
    for relative, payload in sorted(files.items()):
        path = output / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)


def build_parser() -> argparse.ArgumentParser:
    """Build the task generator CLI."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--questions", type=Path, required=True)
    parser.add_argument("--cohorts", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Generate or verify the deterministic task tree."""

    args = build_parser().parse_args(argv)
    try:
        files = expected_files(args.questions.resolve(), args.cohorts.resolve())
        publish(files, args.output.resolve(), args.check)
    except (TaskGenerationError, OSError, UnicodeError, ValueError, TypeError) as exc:
        print(
            json.dumps(
                {"schema_version": SCHEMA_VERSION, "status": "error", "error": str(exc)},
                sort_keys=True,
            )
        )
        return 2
    print(
        json.dumps(
            {
                "schema_version": SCHEMA_VERSION,
                "status": "pass",
                "mode": "check" if args.check else "generate",
                "file_count": len(files),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
