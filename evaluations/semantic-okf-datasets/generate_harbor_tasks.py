#!/usr/bin/env python3
"""Generate Harbor tasks for a checked dataset and one execution mode."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
from collections import OrderedDict
from pathlib import Path
from typing import Any, Mapping, Sequence

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))

import dataset_tool as data  # noqa: E402

RUNTIME_TAG = "semantic-okf-harbor-runtime:1.0"
GRADER = REPO / "evaluations/semantic-okf-harbor/grader"
MODES = ("build-consult", "consult-only")


class GenerationError(ValueError):
    """Raised when a dataset cannot produce isolated Harbor tasks."""


def write_text(path: Path, value: str) -> None:
    """Write LF-normalized UTF-8 text."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value.replace("\r\n", "\n"), encoding="utf-8", newline="\n")


def write_json(path: Path, value: Any) -> None:
    """Write deterministic JSON."""

    write_text(path, json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def normalized_utf8_payload(path: Path) -> bytes:
    """Return the LF-normalized UTF-8 payload used by paper evidence offsets."""

    text = path.read_bytes().decode("utf-8-sig")
    return text.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")


def paper_evidence_segments(text: str, start: int, end: int) -> list[tuple[int, int, str]]:
    """Split exact paper evidence around reader-discarded C0 control characters."""

    if isinstance(start, bool) or isinstance(end, bool) or not 0 <= start < end <= len(text):
        raise GenerationError("paper evidence character range is invalid")
    boundaries = [start]
    for offset in range(start, end):
        character = text[offset]
        if ord(character) < 0x20 and character not in "\n\t\r":
            if boundaries[-1] < offset:
                boundaries.append(offset)
            boundaries.append(offset + 1)
    boundaries.append(end)
    segments: list[tuple[int, int, str]] = []
    for left, right in zip(boundaries, boundaries[1:]):
        if left < right and not (
            right == left + 1 and ord(text[left]) < 0x20 and text[left] not in "\n\t\r"
        ):
            segments.append((left, right, text[left:right]))
    if not segments:
        raise GenerationError("paper evidence contains no indexable text")
    return segments


def normalized_question(
    row: Mapping[str, Any],
    question_format: str,
    rubric: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Normalize source-specific qrels into the source-generic Harbor contract."""

    identifier = data.normalize_question_id(row.get("id"))
    qrels = row.get("qrels")
    if not isinstance(qrels, Mapping):
        raise GenerationError(f"{identifier}: no qrels object")
    if question_format == "document-qrels":
        documents = qrels.get("document_ids")
    elif question_format == "paper-qrels":
        documents = qrels.get("paper_ids")
    else:
        raise GenerationError(f"unsupported question format: {question_format}")
    sources = qrels.get("source_ids")
    if not isinstance(documents, list) or not documents or not isinstance(sources, list):
        raise GenerationError(f"{identifier}: incomplete qrels")
    number = int(identifier[1:])
    question_type = row.get("question_type")
    if not isinstance(question_type, str):
        question_type = "hard" if number >= 31 else "cross-document"
    question = row.get("question")
    if not isinstance(question, str) or not question.strip():
        raise GenerationError(f"{identifier}: empty question")
    result = {
        "id": identifier,
        "source_question_id": row.get("id"),
        "question": question,
        "question_type": question_type,
        "qrels": {
            "document_ids": [str(item) for item in documents],
            "source_ids": [str(item) for item in sources],
        },
    }
    if rubric is not None:
        result["minimum_document_count"] = int(rubric["min_papers"])
        result["semantic_rubric"] = {
            "rubric_id": str(rubric["id"]),
            "dimensions": list(rubric.get("dimensions", [])),
            "required_points": list(rubric["required_points"]),
        }
    return result


def paper_document_id(source_id: str) -> str | None:
    """Derive a reviewed paper identity from one paper or claim source ID."""

    for prefix in ("paper-", "claims-"):
        if source_id.startswith(prefix):
            value = source_id[len(prefix) :]
            match = re.fullmatch(r"([0-9]{4})-([0-9]{5}v[0-9]+)", value)
            return f"{match.group(1)}.{match.group(2)}" if match else value
    return None


def source_combination(
    dataset: Mapping[str, Any], ledger_rows: Sequence[Mapping[str, Any]]
) -> dict[str, Any]:
    """Load or derive a record-to-document crosswalk for scoring."""

    if dataset["question_format"] == "document-qrels":
        spec = dataset.get("source_combination")
        if not isinstance(spec, Mapping):
            raise GenerationError("document-qrels dataset has no source combination")
        value = data.load_json(data.pinned_path(spec, f"{dataset['dataset_id']} source combination"))
        records = value.get("records") if isinstance(value, Mapping) else None
        if not isinstance(records, list):
            raise GenerationError("source combination has no records array")
        return dict(value)
    records = []
    for row in ledger_rows:
        source_id, record_id = row.get("source_id"), row.get("record_id")
        if not isinstance(source_id, str) or not isinstance(record_id, str):
            raise GenerationError("ledger row has no source-scoped identity")
        document_id = paper_document_id(source_id)
        if document_id is not None:
            records.append(
                {"source_id": source_id, "record_id": record_id, "document_id": document_id}
            )
    if not records:
        raise GenerationError("paper crosswalk contains no records")
    return {
        "schema_version": "semantic-okf-evaluation-source-combination/1.0",
        "dataset_id": dataset["dataset_id"],
        "records": records,
    }


def normalize_paper_truth(row: Mapping[str, Any]) -> dict[str, Any]:
    """Convert reviewed paper evidence into the Harbor grader's exact-span schema."""

    identifier = data.normalize_question_id(row.get("id"))
    authoritative: list[dict[str, Any]] = []
    by_claim: dict[str, list[str]] = {}
    for claim in row.get("authoritative_evidence", []):
        if not isinstance(claim, Mapping):
            raise GenerationError(f"{identifier}: invalid authoritative evidence row")
        claim_id, paper_id = claim.get("claim_id"), claim.get("paper_id")
        paper_evidence = claim.get("paper_evidence")
        if not isinstance(claim_id, str) or not isinstance(paper_id, str) or not isinstance(paper_evidence, list):
            raise GenerationError(f"{identifier}: incomplete paper evidence")
        ids: list[str] = []
        for index, evidence in enumerate(paper_evidence, 1):
            if not isinstance(evidence, Mapping):
                raise GenerationError(f"{identifier}: invalid paper evidence span")
            path_value = evidence.get("path")
            if not isinstance(path_value, str):
                raise GenerationError(f"{identifier}: paper evidence has no path")
            path = data.repo_path(path_value, f"{identifier} authority")
            normalized_payload = normalized_utf8_payload(path)
            normalized_text = normalized_payload.decode("utf-8")
            start, end = evidence.get("char_start"), evidence.get("char_end")
            if not isinstance(start, int) or not isinstance(end, int):
                raise GenerationError(f"{identifier}: paper evidence has invalid offsets")
            original_text = normalized_text[start:end]
            if hashlib.sha256(original_text.encode("utf-8")).hexdigest() != evidence.get("text_sha256"):
                raise GenerationError(f"{identifier}: pinned paper evidence span drift")
            segments = paper_evidence_segments(normalized_text, start, end)
            for part, (segment_start, segment_end, segment_text) in enumerate(segments, 1):
                suffix = f"-part-{part}" if len(segments) > 1 else ""
                evidence_id = f"{claim_id}-paper-{index}{suffix}"
                ids.append(evidence_id)
                authoritative.append(
                    {
                        "id": evidence_id,
                        "source_id": f"paper-{paper_id.replace('.', '-', 1)}",
                        "path": path_value,
                        "start_char": segment_start,
                        "end_char": segment_end,
                        "file_sha256": hashlib.sha256(normalized_payload).hexdigest(),
                        "text_sha256": hashlib.sha256(segment_text.encode("utf-8")).hexdigest(),
                    }
                )
        by_claim[claim_id] = ids

    ground = row.get("ground_truth")
    if not isinstance(ground, Mapping):
        raise GenerationError(f"{identifier}: missing ground truth")

    def groups(name: str) -> list[dict[str, Any]]:
        result: list[dict[str, Any]] = []
        for item in ground.get(name, []):
            if not isinstance(item, Mapping):
                raise GenerationError(f"{identifier}: invalid {name} row")
            claim_ids = item.get("evidence_claim_ids")
            if not isinstance(claim_ids, list):
                raise GenerationError(f"{identifier}: {name} row has no evidence claims")
            evidence_ids: list[str] = []
            for claim_id in claim_ids:
                if claim_id not in by_claim:
                    raise GenerationError(f"{identifier}: unknown evidence claim {claim_id}")
                evidence_ids.extend(by_claim[claim_id])
            result.append(
                {
                    "id": item["id"],
                    "statement": item["statement"],
                    "evidence_ids": evidence_ids,
                }
            )
        return result

    return {
        "id": identifier,
        "authoritative_evidence": authoritative,
        "ground_truth": {
            "required_document_ids": [str(item) for item in ground.get("required_paper_ids", [])],
            "required_source_ids": [str(item) for item in ground.get("required_source_ids", [])],
            "answer_claims": groups("answer_claims"),
            "important_negatives": groups("important_negatives"),
            "derivation": list(ground.get("derivation", [])),
            "acceptable_variants": list(ground.get("acceptable_variants", [])),
        },
    }


def normalized_truths(dataset: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    """Load hidden hard-question evidence in the grader's common schema."""

    spec = dataset["hard_ground_truth"]
    rows = data.load_jsonl(data.pinned_path(spec, f"{dataset['dataset_id']} hard ground truth"))
    result: dict[str, dict[str, Any]] = {}
    for row in rows:
        identifier = data.normalize_question_id(row.get("id"))
        if spec.get("format") == "harbor":
            value = dict(row)
            value["id"] = identifier
        elif spec.get("format") == "paper":
            value = normalize_paper_truth(row)
        else:
            raise GenerationError(f"unsupported hard-ground-truth format: {spec.get('format')}")
        result[identifier] = value
    return result


def instruction(
    row: Mapping[str, Any], mode: str, family_id: str, family: Mapping[str, Any]
) -> str:
    """Render an isolated prompt for one execution mode."""

    if mode == "consult-only":
        workflow = (
            "Use only the published Semantic OKF snapshot mounted read-only at `/knowledge`. "
            f"You must use the sole installed `{family['consult_skill']}` consultation skill. "
            "Do not build, repair, or modify knowledge."
        )
    else:
        plan = " and `/dataset/plan.json`" if family["uses_plan"] else ""
        workflow = (
            f"Use the installed `{family['build_skill']}` skill to build a new `{family_id}` Semantic OKF "
            f"snapshot at `/workspace/knowledge` from `/dataset/manifest.json`{plan}. The `/dataset` mount "
            f"is read-only and contains no questions, qrels, or ground truth. Run `{family['validate_script']}` "
            f"against the new snapshot and continue only after validation passes. Then hand that exact snapshot "
            f"to the installed `{family['consult_skill']}` skill and answer from it read-only. No prebuilt "
            "knowledge snapshot is mounted in this mode."
        )
    minimum = row.get("minimum_document_count")
    coverage = (
        f" Use evidence from at least {minimum} independent relevant papers."
        if isinstance(minimum, int)
        else ""
    )
    return f"""{workflow} Do not use the web, model memory, or guesses. If the available knowledge cannot support an answer, return `answer: null` and an empty `evidence` array.{coverage}

Question: {row['question']}

Return JSON only with top-level keys `question_id`, `answer`, and `evidence`, in that order. Set `question_id` to `{row['id']}`. A non-null `answer` must contain `summary` and `claims`, in that order. Keep the summary substantive and no longer than 450 words. Each claim must contain exactly `statement` and `evidence_indices`; indices are zero-based references into `evidence`. Every evidence row must contain exactly `source_id`, `record_id`, `concept_path`, `source_path`, `record_sha256`, `locator`, and `text_sha256`, copied from an exact validated consultation hit. Keep every evidence row in first-use order and use every row. Do not include benchmark relevance labels or unsupported facts.
"""


def task_toml(
    dataset_id: str,
    row: Mapping[str, Any],
    cohort: str,
    mode: str,
    family_id: str,
    verifier_network_mode: str,
    agent_network_mode: str,
) -> str:
    """Render one Harbor task definition."""

    difficulty = "hard" if row["question_type"] == "hard" else "medium"
    agent_hosts = (
        'allowed_hosts = ["auth.openai.com", "chatgpt.com", "api.openai.com"]\n'
        if agent_network_mode == "allowlist"
        else ""
    )
    timeout = 1800.0 if mode == "build-consult" else 600.0
    return f'''schema_version = "1.3"
artifacts = [{{ source = "/logs/agent/pi.txt", destination = "pi.jsonl" }}]

[task]
name = "knowledge/{dataset_id}__{mode}__{family_id}__{row['id']}"
description = "{dataset_id} {mode} question in the {cohort} cohort."
keywords = ["semantic-okf", "{dataset_id}", "{mode}", "{family_id}", "{cohort}"]

[metadata]
difficulty = "{difficulty}"
category = "knowledge-evaluation"
dataset_id = "{dataset_id}"
family = "{family_id}"
mode = "{mode}"
question_type = "{row['question_type']}"
cohort = "{cohort}"

[agent]
timeout_sec = {timeout}
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
    """Return the isolated verifier image definition."""

    return f"""FROM {RUNTIME_TAG}
COPY . /tests
RUN chmod 0555 /tests/test.sh /tests/score.py
WORKDIR /tests
"""


def ledger(path: Path) -> tuple[list[dict[str, Any]], dict[tuple[str, str], dict[str, Any]]]:
    """Load the exact reference ledger and reject duplicate identities."""

    rows = data.load_jsonl(path)
    index = {(str(row.get("source_id")), str(row.get("record_id"))): row for row in rows}
    if len(index) != len(rows):
        raise GenerationError("reference ledger contains duplicate source-scoped identities")
    return rows, index


def oracle_answer(
    question: Mapping[str, Any],
    truth: Mapping[str, Any] | None,
    combination: Mapping[str, Any],
    records: Mapping[tuple[str, str], Mapping[str, Any]],
) -> OrderedDict[str, Any]:
    """Build a structural oracle response for deterministic task validation."""

    by_document: dict[str, list[tuple[str, str]]] = {}
    for row in combination["records"]:
        key = (str(row["source_id"]), str(row["record_id"]))
        if key in records:
            by_document.setdefault(str(row["document_id"]), []).append(key)
    evidence: list[OrderedDict[str, Any]] = []
    source_to_index: dict[str, int] = {}
    for document in question["qrels"]["document_ids"]:
        choices = by_document.get(str(document), [])
        if not choices:
            raise GenerationError(f"{question['id']}: no ledger record for qrel {document}")
        preferred = [
            key
            for key in choices
            if key[0].startswith("paper-") and paper_document_id(key[0]) == str(document)
        ]
        key = sorted(preferred or choices)[0]
        record = records[key]
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
            str(item["id"]): str(item["source_id"]) for item in truth["authoritative_evidence"]
        }
        for claim in truth["ground_truth"]["answer_claims"]:
            indices = sorted(
                {source_to_index[evidence_sources[item]] for item in claim["evidence_ids"]}
            )
            claims.append(
                OrderedDict([("statement", claim["statement"]), ("evidence_indices", indices)])
            )
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
        claims.append(
            OrderedDict(
                [
                    ("statement", "The answer is grounded in the cited authoritative Semantic OKF records."),
                    ("evidence_indices", list(range(len(evidence)))),
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
    """Wrap one oracle response in Pi's message-end log shape."""

    text = json.dumps(answer, ensure_ascii=False, separators=(",", ":"))
    event = {
        "type": "message_end",
        "message": {
            "role": "assistant",
            "content": [{"type": "text", "text": text}],
            "stopReason": "stop",
        },
    }
    return json.dumps(event, ensure_ascii=False, separators=(",", ":")) + "\n"


def copy_authority(truth: Mapping[str, Any], target_root: Path) -> None:
    """Copy only hidden authority, normalizing text when its pinned hash requires it."""

    copied: set[str] = set()
    for row in truth.get("authoritative_evidence", []):
        path_value = row.get("path") if isinstance(row, Mapping) else None
        if not isinstance(path_value, str) or path_value in copied:
            continue
        source = data.repo_path(path_value, "authoritative evidence")
        target = target_root / Path(*Path(path_value).parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        expected_hashes = {
            item.get("file_sha256")
            for item in truth.get("authoritative_evidence", [])
            if isinstance(item, Mapping) and item.get("path") == path_value
        }
        if len(expected_hashes) != 1 or not all(isinstance(value, str) for value in expected_hashes):
            raise GenerationError(f"conflicting authority hashes for {path_value}")
        expected_hash = next(iter(expected_hashes))
        raw_payload = source.read_bytes()
        if hashlib.sha256(raw_payload).hexdigest() == expected_hash:
            payload = raw_payload
        else:
            payload = normalized_utf8_payload(source)
            if hashlib.sha256(payload).hexdigest() != expected_hash:
                raise GenerationError(f"authority hash does not match raw or normalized text: {path_value}")
        target.write_bytes(payload)
        copied.add(path_value)


def generate(
    dataset_id: str,
    family_id: str,
    mode: str,
    output: Path,
    bundle: Path,
    staged_input: Path | None,
    verifier_network_mode: str,
    agent_network_mode: str,
) -> dict[str, Any]:
    """Generate every task below an empty candidate directory."""

    data.validate_dataset(dataset_id, family_id)
    dataset = data.load_dataset(dataset_id)
    family = data.load_families()[family_id]
    if mode == "build-consult":
        if staged_input is None or not (staged_input / "input-manifest.json").is_file():
            raise GenerationError("build-consult requires prepared staged input")
        staged = data.load_json(staged_input / "input-manifest.json")
        if staged.get("dataset_id") != dataset_id or staged.get("family") != family_id:
            raise GenerationError("staged input identity does not match dataset/family")
        if data.tree_digest(staged_input, exclude={"input-manifest.json"}) != staged.get("payload_tree_sha256"):
            raise GenerationError("staged input payload drift")
    ledger_path = bundle / "semantic/records.jsonl"
    if not ledger_path.is_file():
        raise GenerationError(f"reference bundle has no ledger: {bundle}")
    ledger_rows, ledger_index = ledger(ledger_path)
    combination = source_combination(dataset, ledger_rows)
    rubrics = data.dataset_semantic_rubrics(dataset)
    questions = [
        normalized_question(
            row,
            dataset["question_format"],
            rubrics.get(data.normalize_question_id(row.get("id"))),
        )
        for row in data.dataset_questions(dataset)
    ]
    questions_by_id = {row["id"]: row for row in questions}
    truths = normalized_truths(dataset)
    cohorts = data.dataset_cohorts(dataset)
    partition = dataset["partition_cohorts"]
    grader_files = [
        GRADER / "score.py",
        GRADER / "trace_status.py",
        GRADER / "test.sh",
        GRADER / "answer.schema.json",
    ]
    for cohort in partition:
        for identifier in cohorts[cohort]:
            row = questions_by_id[identifier]
            task_dir = output / cohort / identifier
            tests = task_dir / "tests"
            solution = task_dir / "solution"
            (task_dir / "environment").mkdir(parents=True, exist_ok=True)
            tests.mkdir(parents=True, exist_ok=True)
            solution.mkdir(parents=True, exist_ok=True)
            write_text(task_dir / "instruction.md", instruction(row, mode, family_id, family))
            write_text(
                task_dir / "task.toml",
                task_toml(
                    dataset_id,
                    row,
                    cohort,
                    mode,
                    family_id,
                    verifier_network_mode,
                    agent_network_mode,
                ),
            )
            for source in grader_files:
                shutil.copyfile(source, tests / source.name)
            write_text(tests / "Dockerfile", verifier_dockerfile())
            write_json(tests / "question.json", row)
            write_json(tests / "source-combination.json", combination)
            shutil.copyfile(ledger_path, tests / "records.jsonl")
            truth = truths.get(identifier)
            if truth is not None:
                write_json(tests / "hard-ground-truth.json", truth)
                copy_authority(truth, tests / "authority")
            oracle = oracle_answer(row, truth, combination, ledger_index)
            write_text(solution / "oracle-pi.jsonl", pi_event(oracle))
            write_text(
                solution / "solve.sh",
                "#!/usr/bin/env bash\nset -euo pipefail\nmkdir -p /logs/agent\n"
                "cp /solution/oracle-pi.jsonl /logs/agent/pi.txt\n",
            )
    descriptor_path = data.DATASETS / f"{dataset_id}.json"
    manifest = {
        "schema_version": "semantic-okf-evaluation-harbor-tasks/1.0",
        "dataset_id": dataset_id,
        "family": family_id,
        "mode": mode,
        "question_count": len(questions),
        "cohort_counts": {name: len(cohorts[name]) for name in partition},
        "runtime_image": RUNTIME_TAG,
        "reference_bundle_tree_sha256": data.tree_digest(bundle),
        "reference_records_sha256": data.sha256_file(ledger_path),
        "staged_input_tree_sha256": data.tree_digest(staged_input) if staged_input else None,
        "agent_network_mode": agent_network_mode,
        "verifier_network_mode": verifier_network_mode,
        "source_hashes": {
            "dataset_descriptor": data.sha256_file(descriptor_path),
            "questions": dataset["questions"]["sha256"],
            "hard_ground_truth": dataset["hard_ground_truth"]["sha256"],
            "semantic_rubric": (
                dataset["semantic_rubric"]["sha256"]
                if isinstance(dataset.get("semantic_rubric"), Mapping)
                else None
            ),
            "cohorts": dataset["cohorts"]["sha256"],
        },
    }
    write_json(output / "manifest.json", manifest)
    return manifest


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse task generation controls."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", choices=data.available_datasets(), required=True)
    parser.add_argument("--family", choices=sorted(data.load_families()), required=True)
    parser.add_argument("--mode", choices=MODES, required=True)
    parser.add_argument("--bundle", type=Path, help="Validated reference bundle used only by hidden verifiers.")
    parser.add_argument("--input", type=Path, help="Prepared raw input; required for build-consult.")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--replace", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--agent-network-mode", choices=("public", "allowlist"), default="public")
    parser.add_argument("--verifier-network-mode", choices=("public", "no-network"), default="public")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    """Generate atomically or check deterministic task drift."""

    args = parse_args(argv)
    try:
        dataset = data.load_dataset(args.dataset)
        default_bundle = dataset.get("reference_bundle")
        if args.bundle is not None:
            bundle = args.bundle.resolve()
        elif isinstance(default_bundle, str):
            bundle = data.repo_path(default_bundle, "reference bundle")
        else:
            raise GenerationError("--bundle is required because this dataset has no checked reference bundle")
        staged_input = (
            args.input.resolve()
            if args.input is not None
            else (HERE / "generated/inputs" / args.dataset / args.family).resolve()
            if args.mode == "build-consult"
            else None
        )
        output = (
            args.output
            or HERE / "generated/tasks" / args.dataset / args.mode / args.family
        ).resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        candidate = Path(tempfile.mkdtemp(prefix=f".{output.name}.candidate-", dir=output.parent))
        try:
            manifest = generate(
                args.dataset,
                args.family,
                args.mode,
                candidate,
                bundle,
                staged_input,
                args.verifier_network_mode,
                args.agent_network_mode,
            )
            digest = data.tree_digest(candidate)
            if args.check:
                if not output.is_dir():
                    raise GenerationError(f"generated tasks are absent: {output}")
                if data.tree_digest(output) != digest:
                    raise GenerationError(f"generated task drift: {output}")
                print(json.dumps({"status": "pass", "tree_sha256": digest, **manifest}, sort_keys=True))
                return 0
            if output.exists():
                if not args.replace:
                    raise GenerationError(f"output exists; use --replace: {output}")
                backup = output.with_name(f".{output.name}.previous-{os.getpid()}")
                output.rename(backup)
                try:
                    candidate.rename(output)
                except BaseException:
                    backup.rename(output)
                    raise
                shutil.rmtree(backup)
            else:
                candidate.rename(output)
            print(json.dumps({"status": "pass", "tree_sha256": digest, **manifest}, sort_keys=True))
            return 0
        finally:
            if candidate.exists():
                shutil.rmtree(candidate)
    except (data.DatasetError, GenerationError) as exc:
        raise SystemExit(str(exc)) from exc


if __name__ == "__main__":
    raise SystemExit(main())
