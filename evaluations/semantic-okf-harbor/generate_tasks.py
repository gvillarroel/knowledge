#!/usr/bin/env python3
"""Generate the ignored forty-task Harbor dataset from frozen Astro inputs."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import tempfile
from collections import OrderedDict
from pathlib import Path
from typing import Any, Mapping, Sequence

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
ASTRO = REPO / "evaluations/semantic-okf-astro"
DEFAULT_OUTPUT = HERE / "generated/tasks"
DEFAULT_BUNDLE = ASTRO / "results/runs/20260716-astro-generic-01/bundles/legacy-a"
RUNTIME_TAG = "semantic-okf-harbor-runtime:1.0"
EXPECTED_IDS = [f"q{number:03d}" for number in range(1, 41)]


class GenerationError(ValueError):
    """Raised when frozen inputs or generated content violate the contract."""


def sha256_file(path: Path) -> str:
    """Return the SHA-256 digest of one file."""

    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> Any:
    """Load one UTF-8 JSON file."""

    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    """Load a UTF-8 JSON Lines file."""

    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_text(path: Path, value: str) -> None:
    """Write LF-normalized UTF-8 text."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value.replace("\r\n", "\n"), encoding="utf-8", newline="\n")


def write_json(path: Path, value: Any) -> None:
    """Write deterministic pretty JSON."""

    write_text(path, json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def split_map(path: Path) -> dict[str, str]:
    """Load and validate the checked prospective split."""

    value = load_json(path)
    cohorts = value.get("cohorts")
    if not isinstance(cohorts, Mapping):
        raise GenerationError("splits.json has no cohorts object")
    result: dict[str, str] = {}
    for split in ("train", "dev", "holdout"):
        rows = cohorts.get(split)
        if not isinstance(rows, list):
            raise GenerationError(f"splits.json lacks {split}")
        for identifier in rows:
            if not isinstance(identifier, str) or identifier in result:
                raise GenerationError("split IDs must be unique strings")
            result[identifier] = split
    if sorted(result) != EXPECTED_IDS:
        raise GenerationError("split must contain q001 through q040 exactly once")
    return result


def instruction(row: Mapping[str, Any]) -> str:
    """Render a prompt containing no evaluator labels beyond the response ID."""

    return f"""Use only the published Semantic OKF snapshot mounted read-only at `/knowledge`. Do not use the web, model memory, or guesses. You must use the sole installed consultation skill. Do not modify the snapshot. If the snapshot cannot support an answer, return `answer: null` and an empty `evidence` array.

Question: {row['question']}

Return JSON only with top-level keys `question_id`, `answer`, and `evidence`, in that order. Set `question_id` to `{row['id']}`. A non-null `answer` must contain `summary` and `claims`, in that order. Keep the summary substantive and no longer than 450 words. Each claim must contain exactly `statement` and `evidence_indices`; indices are zero-based references into `evidence`. Every evidence row must contain exactly `source_id`, `record_id`, `concept_path`, `source_path`, `record_sha256`, `locator`, and `text_sha256`, copied from an exact validated consultation hit. Keep every evidence row in first-use order and use every row. Do not include benchmark relevance labels or unsupported facts.
"""


def task_toml(
    row: Mapping[str, Any], split: str, verifier_network_mode: str, agent_network_mode: str
) -> str:
    """Render Harbor task schema 1.3 with an isolated verifier."""

    difficulty = "hard" if row["question_type"] == "hard" else "medium"
    agent_hosts = (
        'allowed_hosts = ["auth.openai.com", "chatgpt.com", "api.openai.com"]\n'
        if agent_network_mode == "allowlist"
        else ""
    )
    return f'''schema_version = "1.3"
artifacts = [{{ source = "/logs/agent/pi.txt", destination = "pi.jsonl" }}]

[task]
name = "knowledge/semantic-okf-harbor__{row['id']}"
description = "Frozen Astro {row['question_type']} question in the {split} cohort."
keywords = ["semantic-okf", "astro", "retrieval", "grounding", "{split}"]

[metadata]
difficulty = "{difficulty}"
category = "knowledge-consultation"
question_type = "{row['question_type']}"
split = "{split}"

[agent]
timeout_sec = 600.0
network_mode = "{agent_network_mode}"
{agent_hosts}

[verifier]
timeout_sec = 180.0
environment_mode = "separate"
network_mode = "{verifier_network_mode}"

[verifier.environment]
os = "linux"
network_mode = "{verifier_network_mode}"
memory_mb = 4096

[environment]
docker_image = "{RUNTIME_TAG}"
os = "linux"
network_mode = "public"
memory_mb = 8192
storage_mb = 24576
workdir = "/workspace"
'''


def verifier_dockerfile() -> str:
    """Return the private verifier image definition."""

    return f"""FROM {RUNTIME_TAG}
COPY . /tests
RUN chmod 0555 /tests/test.sh /tests/score.py
WORKDIR /tests
"""


def ledger_index(path: Path) -> tuple[list[dict[str, Any]], dict[tuple[str, str], dict[str, Any]]]:
    """Load the authoritative ledger with unique source-scoped identities."""

    rows = load_jsonl(path)
    index = {(str(row["source_id"]), str(row["record_id"])): row for row in rows}
    if len(index) != len(rows):
        raise GenerationError("authoritative ledger contains duplicate identities")
    return rows, index


def oracle_answer(
    question: Mapping[str, Any],
    truth: Mapping[str, Any] | None,
    combination: Mapping[str, Any],
    ledger: Mapping[tuple[str, str], Mapping[str, Any]],
) -> OrderedDict[str, Any]:
    """Create a structural/evidence oracle used only by Harbor's Oracle agent."""

    by_document = {
        str(row["document_id"]): (str(row["source_id"]), str(row["record_id"]))
        for row in combination["records"]
    }
    evidence: list[OrderedDict[str, Any]] = []
    source_to_index: dict[str, int] = {}
    for document in question["qrels"]["document_ids"]:
        key = by_document[str(document)]
        record = ledger[key]
        body = str(record["body"])
        source_to_index[key[0]] = len(evidence)
        evidence.append(
            OrderedDict(
                [
                    ("source_id", key[0]),
                    ("record_id", key[1]),
                    ("concept_path", record["concept_path"]),
                    ("source_path", record["source_path"]),
                    ("record_sha256", record["record_sha256"]),
                    ("locator", OrderedDict([("kind", "record"), ("target", "record.body")])),
                    ("text_sha256", hashlib.sha256(body.encode("utf-8")).hexdigest()),
                ]
            )
        )
    claims: list[OrderedDict[str, Any]] = []
    if truth is not None:
        evidence_sources = {
            str(row["id"]): str(row["source_id"]) for row in truth["authoritative_evidence"]
        }
        for claim in truth["ground_truth"]["answer_claims"]:
            indices = sorted({source_to_index[evidence_sources[item]] for item in claim["evidence_ids"]})
            claims.append(OrderedDict([("statement", claim["statement"]), ("evidence_indices", indices)]))
        first_use: list[int] = []
        for claim in claims:
            for index in claim["evidence_indices"]:
                if index not in first_use:
                    first_use.append(index)
        first_use.extend(index for index in range(len(evidence)) if index not in first_use)
        old_to_new = {old: new for new, old in enumerate(first_use)}
        evidence = [evidence[index] for index in first_use]
        for claim in claims:
            claim["evidence_indices"] = [old_to_new[index] for index in claim["evidence_indices"]]
    else:
        indices = list(range(len(evidence)))
        claims.append(
            OrderedDict(
                [
                    ("statement", "The answer is grounded in the cited authoritative Semantic OKF records."),
                    ("evidence_indices", indices),
                ]
            )
        )
    summary = " ".join(str(claim["statement"]) for claim in claims)
    return OrderedDict(
        [
            ("question_id", question["id"]),
            ("answer", OrderedDict([("summary", summary), ("claims", claims)])),
            ("evidence", evidence),
        ]
    )


def pi_event(answer: Mapping[str, Any]) -> str:
    """Wrap one oracle response in the built-in Pi message-end event shape."""

    text = json.dumps(answer, ensure_ascii=False, separators=(",", ":"))
    event = {"type": "message_end", "message": {"role": "assistant", "content": [{"type": "text", "text": text}]}}
    return json.dumps(event, ensure_ascii=False, separators=(",", ":")) + "\n"


def generate(
    output: Path, bundle: Path, verifier_network_mode: str, agent_network_mode: str
) -> dict[str, Any]:
    """Generate every task into an empty output directory."""

    questions_path = ASTRO / "benchmark/retrieval-questions.jsonl"
    ground_truth_path = ASTRO / "benchmark/hard-ground-truth.jsonl"
    combination_path = ASTRO / "corpus/source-combination.json"
    ledger_path = bundle / "semantic/records.jsonl"
    questions = load_jsonl(questions_path)
    if [row.get("id") for row in questions] != EXPECTED_IDS:
        raise GenerationError("retrieval questions must be ordered q001 through q040")
    truths = {row["id"]: row for row in load_jsonl(ground_truth_path)}
    combination = load_json(combination_path)
    ledger_rows, ledger = ledger_index(ledger_path)
    splits = split_map(HERE / "splits.json")
    grader_files = [HERE / "grader/score.py", HERE / "grader/test.sh", HERE / "grader/answer.schema.json"]
    for row in questions:
        identifier = str(row["id"])
        task_dir = output / splits[identifier] / identifier
        tests = task_dir / "tests"
        solution = task_dir / "solution"
        (task_dir / "environment").mkdir(parents=True, exist_ok=True)
        tests.mkdir(parents=True, exist_ok=True)
        solution.mkdir(parents=True, exist_ok=True)
        write_text(task_dir / "instruction.md", instruction(row))
        write_text(
            task_dir / "task.toml",
            task_toml(row, splits[identifier], verifier_network_mode, agent_network_mode),
        )
        for source in grader_files:
            shutil.copyfile(source, tests / source.name)
        write_text(tests / "Dockerfile", verifier_dockerfile())
        write_json(tests / "question.json", row)
        shutil.copyfile(combination_path, tests / "source-combination.json")
        shutil.copyfile(ledger_path, tests / "records.jsonl")
        truth = truths.get(identifier)
        if truth is not None:
            write_json(tests / "hard-ground-truth.json", truth)
            for evidence in truth["authoritative_evidence"]:
                source = REPO / evidence["path"]
                target = tests / "authority" / evidence["path"]
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, target)
        oracle = oracle_answer(row, truth, combination, ledger)
        write_text(solution / "oracle-pi.jsonl", pi_event(oracle))
        write_text(
            solution / "solve.sh",
            "#!/usr/bin/env bash\nset -euo pipefail\nmkdir -p /logs/agent\ncp /solution/oracle-pi.jsonl /logs/agent/pi.txt\n",
        )
    manifest = {
        "schema_version": "semantic-okf-harbor-generated-task-manifest/1.0",
        "question_count": len(questions),
        "cohort_counts": {name: sum(value == name for value in splits.values()) for name in ("train", "dev", "holdout")},
        "runtime_image": RUNTIME_TAG,
        "verifier_network_mode": verifier_network_mode,
        "verifier_network_enforcement": verifier_network_mode == "no-network",
        "agent_network_mode": agent_network_mode,
        "agent_network_enforcement": agent_network_mode == "allowlist",
        "source_hashes": {
            "questions": sha256_file(questions_path),
            "hard_ground_truth": sha256_file(ground_truth_path),
            "source_combination": sha256_file(combination_path),
            "records": sha256_file(ledger_path),
        },
    }
    write_json(output / "manifest.json", manifest)
    return manifest


def tree_digest(root: Path) -> str:
    """Hash sorted relative paths and file bytes for deterministic drift checks."""

    digest = hashlib.sha256()
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        relative = path.relative_to(root).as_posix()
        digest.update(relative.encode("utf-8") + b"\0" + path.read_bytes() + b"\0")
    return digest.hexdigest()


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse generation controls."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--bundle", type=Path, default=DEFAULT_BUNDLE)
    parser.add_argument("--replace", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument(
        "--agent-network-mode",
        choices=("public", "allowlist"),
        default="public",
        help="Use public for the current WSL Docker compatibility path; allowlist requires a passing egress-sidecar smoke.",
    )
    parser.add_argument(
        "--verifier-network-mode",
        choices=("public", "no-network"),
        default="public",
        help="Use public for the current WSL Docker compatibility path; the verifier remains separate and offline in code.",
    )
    args = parser.parse_args(argv)
    args.output = args.output.resolve()
    args.bundle = args.bundle.resolve()
    return args


def main(argv: Sequence[str] | None = None) -> int:
    """Generate atomically or compare a fresh candidate with existing tasks."""

    args = parse_args(argv)
    if not (args.bundle / "semantic/records.jsonl").is_file():
        raise SystemExit(f"missing accepted bundle ledger: {args.bundle}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    candidate = Path(tempfile.mkdtemp(prefix=f".{args.output.name}.candidate-", dir=args.output.parent))
    try:
        manifest = generate(
            candidate, args.bundle, args.verifier_network_mode, args.agent_network_mode
        )
        candidate_digest = tree_digest(candidate)
        if args.check:
            if not args.output.is_dir():
                raise SystemExit(f"generated dataset is absent: {args.output}")
            if tree_digest(args.output) != candidate_digest:
                raise SystemExit("generated Harbor dataset drift detected")
            print(json.dumps({"status": "pass", "tree_sha256": candidate_digest, **manifest}, sort_keys=True))
            return 0
        if args.output.exists():
            if not args.replace:
                raise SystemExit(f"output exists; use --replace: {args.output}")
            backup = args.output.with_name(f".{args.output.name}.previous-{os.getpid()}")
            args.output.rename(backup)
            try:
                candidate.rename(args.output)
            except BaseException:
                backup.rename(args.output)
                raise
            shutil.rmtree(backup)
        else:
            candidate.rename(args.output)
        print(json.dumps({"status": "pass", "tree_sha256": candidate_digest, **manifest}, sort_keys=True))
        return 0
    finally:
        if candidate.exists():
            shutil.rmtree(candidate)


if __name__ == "__main__":
    raise SystemExit(main())
