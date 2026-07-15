#!/usr/bin/env python3
"""Independently validate hard-question claims, locators, hashes, and benchmark isolation."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


GROUND_TRUTH_SCHEMA = "semantic-okf-hard-ground-truth/1.0"
MANIFEST_SCHEMA = "semantic-okf-hard-ground-truth-manifest/1.0"
EXPECTED_HARD_IDS = [f"q{number:03d}" for number in range(31, 41)]
PAGE_HEADING_RE = re.compile(r"(?m)^## PDF page ([1-9][0-9]*)[ \t]*$")
LOCATOR_RE = re.compile(r"^(sources/markdown/([^/]+)\.md)#(PDF-page-([1-9][0-9]*))$")
TOKEN_RE = re.compile(r"[a-z0-9]+")


class ValidationError(RuntimeError):
    """Raised when checked-in evidence does not reproduce from authoritative sources."""


def logical_text(path: Path) -> str:
    return path.read_bytes().decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")


def digest_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def digest_text(text: str) -> str:
    return digest_bytes(text.encode("utf-8"))


def digest_file(path: Path) -> str:
    return digest_bytes(path.read_bytes())


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(logical_text(path))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValidationError(f"cannot read JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValidationError(f"expected JSON object in {path}")
    return value


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for line_number, line in enumerate(logical_text(path).splitlines(), start=1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValidationError(f"invalid JSONL at {path}:{line_number}: {exc}") from exc
        if not isinstance(value, dict):
            raise ValidationError(f"expected object at {path}:{line_number}")
        result.append(value)
    return result


def resolve_repo_path(repo_root: Path, relative: str) -> Path:
    if not isinstance(relative, str) or not relative or "\\" in relative:
        raise ValidationError(f"invalid portable path: {relative!r}")
    candidate = (repo_root / Path(relative)).resolve()
    try:
        candidate.relative_to(repo_root)
    except ValueError as exc:
        raise ValidationError(f"path escapes repository root: {relative}") from exc
    return candidate


def index_logical_lines(path: Path) -> dict[int, tuple[int, int, str, dict[str, Any]]]:
    lines: dict[int, tuple[int, int, str, dict[str, Any]]] = {}
    offset = 0
    for line_number, with_ending in enumerate(logical_text(path).splitlines(keepends=True), start=1):
        line = with_ending[:-1] if with_ending.endswith("\n") else with_ending
        if line.strip():
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValidationError(f"invalid authoritative claim at {path}:{line_number}") from exc
            if not isinstance(record, dict):
                raise ValidationError(f"authoritative claim is not an object at {path}:{line_number}")
            lines[line_number] = (offset, offset + len(line), line, record)
        offset += len(with_ending)
    return lines


def page_segments(path: Path) -> dict[str, tuple[int, int, str]]:
    text = logical_text(path)
    headings = list(PAGE_HEADING_RE.finditer(text))
    if not headings:
        raise ValidationError(f"paper contains no page headings: {path}")
    result: dict[str, tuple[int, int, str]] = {}
    for index, heading in enumerate(headings):
        locator = f"PDF-page-{heading.group(1)}"
        if locator in result:
            raise ValidationError(f"duplicate page locator {locator}: {path}")
        start = heading.start()
        end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
        result[locator] = (start, end, text[start:end])
    return result


def expected_paper_evidence(
    repo_root: Path, paper_id: str, locator_value: str
) -> list[dict[str, Any]]:
    expected: list[dict[str, Any]] = []
    if not isinstance(locator_value, str) or not locator_value:
        raise ValidationError(f"empty evidence locator for {paper_id}")
    for item in locator_value.split(";"):
        match = LOCATOR_RE.fullmatch(item)
        if not match or match.group(2) != paper_id:
            raise ValidationError(f"claim locator does not match {paper_id}: {item!r}")
        relative_source, locator = match.group(1), match.group(3)
        relative_repo = f"evaluations/graphrag-cross-paper/{relative_source}"
        source_path = resolve_repo_path(repo_root, relative_repo)
        segments = page_segments(source_path)
        if locator not in segments:
            raise ValidationError(f"missing locator {locator}: {relative_repo}")
        start, end, text = segments[locator]
        expected.append(
            {
                "path": relative_repo,
                "locator": locator,
                "char_start": start,
                "char_end": end,
                "text_length": len(text),
                "text_sha256": digest_text(text),
            }
        )
    if len({(item["path"], item["locator"]) for item in expected}) != len(expected):
        raise ValidationError(f"duplicate locator in authoritative claim for {paper_id}")
    return expected


def validate_inventory(repo_root: Path, inventory_path: Path) -> None:
    inventory = load_json(inventory_path)
    files = inventory.get("files")
    if not isinstance(files, list) or len(files) != 30:
        raise ValidationError("pinned inventory must list exactly 30 core files")
    roles: dict[str, int] = {}
    seen: set[str] = set()
    corpus_prefix = "evaluations/graphrag-cross-paper/"
    for entry in files:
        if not isinstance(entry, dict):
            raise ValidationError("inventory file entry is not an object")
        relative = entry.get("path")
        role = entry.get("role")
        if not isinstance(relative, str) or relative in seen:
            raise ValidationError("inventory paths must be unique strings")
        seen.add(relative)
        roles[str(role)] = roles.get(str(role), 0) + 1
        path = resolve_repo_path(repo_root, corpus_prefix + relative)
        if not path.is_file() or digest_file(path) != entry.get("sha256"):
            raise ValidationError(f"pinned inventory mismatch: {relative}")
    if roles != {"paper-markdown": 15, "reviewed-claims": 15}:
        raise ValidationError(f"pinned inventory roles changed: {roles}")


def validate_manifest(repo_root: Path, manifest: dict[str, Any]) -> None:
    if manifest.get("schema_version") != MANIFEST_SCHEMA:
        raise ValidationError("unsupported hard-ground-truth manifest schema")
    inputs = manifest.get("inputs")
    outputs = manifest.get("outputs")
    if not isinstance(inputs, dict) or not isinstance(outputs, dict):
        raise ValidationError("manifest inputs and outputs must be objects")
    expected_outputs = {
        "hard-ground-truth.jsonl": 10,
        "hard-questions.jsonl": 10,
        "retrieval-questions.jsonl": 40,
    }
    if set(outputs) != set(expected_outputs):
        raise ValidationError("manifest output set is not closed")
    for name, expected_count in expected_outputs.items():
        entry = outputs[name]
        if not isinstance(entry, dict) or entry.get("count") != expected_count:
            raise ValidationError(f"manifest count mismatch for {name}")
        path = resolve_repo_path(repo_root, entry.get("path"))
        if digest_text(logical_text(path)) != entry.get("sha256"):
            raise ValidationError(f"manifest output hash mismatch: {name}")
    for name in ("blueprint", "baseline_questions"):
        entry = inputs.get(name)
        if not isinstance(entry, dict):
            raise ValidationError(f"manifest is missing input {name}")
        path = resolve_repo_path(repo_root, entry.get("path"))
        if digest_text(logical_text(path)) != entry.get("sha256"):
            raise ValidationError(f"manifest logical input hash mismatch: {name}")
    inventory_entry = inputs.get("corpus_inventory")
    if not isinstance(inventory_entry, dict) or inventory_entry.get("core_file_count") != 30:
        raise ValidationError("manifest corpus inventory contract is invalid")
    inventory_path = resolve_repo_path(repo_root, inventory_entry.get("path"))
    if digest_file(inventory_path) != inventory_entry.get("sha256"):
        raise ValidationError("manifest inventory hash mismatch")
    validate_inventory(repo_root, inventory_path)


def validate_authoritative_claim(repo_root: Path, evidence: dict[str, Any]) -> tuple[str, str]:
    required_keys = {
        "claim_id",
        "paper_id",
        "claim_kind",
        "review_state",
        "interpretation",
        "interpretation_sha256",
        "claim_source",
        "paper_evidence",
    }
    if set(evidence) != required_keys:
        raise ValidationError(f"authoritative evidence has unexpected keys: {set(evidence) ^ required_keys}")
    claim_id = evidence["claim_id"]
    paper_id = evidence["paper_id"]
    source = evidence["claim_source"]
    if not isinstance(source, dict):
        raise ValidationError(f"claim source is not an object: {claim_id}")
    expected_source_path = f"evaluations/graphrag-cross-paper/sources/claims/{paper_id}.jsonl"
    if source.get("path") != expected_source_path:
        raise ValidationError(f"claim source path does not match paper identity: {claim_id}")
    source_path = resolve_repo_path(repo_root, expected_source_path)
    line_number = source.get("line_number")
    if not isinstance(line_number, int):
        raise ValidationError(f"claim line number is invalid: {claim_id}")
    lines = index_logical_lines(source_path)
    if line_number not in lines:
        raise ValidationError(f"claim line does not exist: {claim_id}")
    start, end, line, record = lines[line_number]
    if record.get("id") != claim_id:
        raise ValidationError(f"claim id does not match authoritative line: {claim_id}")
    if record.get("review_state") != "reviewed" or evidence.get("review_state") != "reviewed":
        raise ValidationError(f"hard-question evidence is not reviewed: {claim_id}")
    expected_source = {
        "path": expected_source_path,
        "line_number": line_number,
        "char_start": start,
        "char_end": end,
        "record_sha256": digest_text(line),
    }
    if source != expected_source:
        raise ValidationError(f"claim source locator or hash mismatch: {claim_id}")
    if evidence.get("claim_kind") != record.get("claim_kind"):
        raise ValidationError(f"claim kind mismatch: {claim_id}")
    interpretation = record.get("interpretation")
    if (
        evidence.get("interpretation") != interpretation
        or not isinstance(interpretation, str)
        or evidence.get("interpretation_sha256") != digest_text(interpretation)
    ):
        raise ValidationError(f"claim interpretation mismatch: {claim_id}")
    expected_pages = expected_paper_evidence(repo_root, paper_id, record.get("evidence_locator"))
    if evidence.get("paper_evidence") != expected_pages:
        raise ValidationError(f"paper locator, offsets, or text hash mismatch: {claim_id}")
    return claim_id, paper_id


def source_ids(paper_ids: list[str]) -> list[str]:
    return sorted(
        [f"claims-{paper_id.replace('.', '-')}" for paper_id in paper_ids]
        + [f"paper-{paper_id.replace('.', '-')}" for paper_id in paper_ids]
    )


def word_set(text: str) -> set[str]:
    return set(TOKEN_RE.findall(text.lower()))


def validate_ground_truth_record(repo_root: Path, record: dict[str, Any]) -> dict[str, Any]:
    if set(record) != {
        "schema_version",
        "id",
        "corpus_inventory",
        "authoritative_evidence",
        "ground_truth",
        "question",
    }:
        raise ValidationError(f"ground-truth record has an open or incomplete schema: {record.get('id')}")
    if record.get("schema_version") != GROUND_TRUTH_SCHEMA:
        raise ValidationError(f"unsupported ground-truth record schema: {record.get('id')}")
    question_id = record.get("id")
    question = record.get("question")
    if not isinstance(question_id, str) or not isinstance(question, str):
        raise ValidationError("ground-truth id and question must be strings")
    evidence_list = record.get("authoritative_evidence")
    if not isinstance(evidence_list, list) or len(evidence_list) < 3:
        raise ValidationError(f"insufficient authoritative evidence: {question_id}")
    claim_ids: list[str] = []
    paper_ids: set[str] = set()
    for evidence in evidence_list:
        if not isinstance(evidence, dict):
            raise ValidationError(f"evidence is not an object: {question_id}")
        claim_id, paper_id = validate_authoritative_claim(repo_root, evidence)
        claim_ids.append(claim_id)
        paper_ids.add(paper_id)
    if len(claim_ids) != len(set(claim_ids)):
        raise ValidationError(f"duplicate authoritative claim: {question_id}")
    if len(paper_ids) < 3:
        raise ValidationError(f"hard question does not require at least three papers: {question_id}")
    ground_truth = record.get("ground_truth")
    if not isinstance(ground_truth, dict) or set(ground_truth) != {
        "answer_claims",
        "required_paper_ids",
        "required_source_ids",
        "derivation",
        "acceptable_variants",
        "important_negatives",
    }:
        raise ValidationError(f"ground truth contract is open or incomplete: {question_id}")
    expected_papers = sorted(paper_ids)
    if ground_truth.get("required_paper_ids") != expected_papers:
        raise ValidationError(f"required paper identities do not match evidence: {question_id}")
    expected_sources = source_ids(expected_papers)
    if ground_truth.get("required_source_ids") != expected_sources:
        raise ValidationError(f"required source identities do not match evidence: {question_id}")
    answers = ground_truth.get("answer_claims")
    if not isinstance(answers, list) or len(answers) < 3:
        raise ValidationError(f"ground truth lacks atomic answers: {question_id}")
    answer_ids: set[str] = set()
    used_claim_ids: set[str] = set()
    question_words = word_set(question)
    for answer in answers:
        if not isinstance(answer, dict) or set(answer) != {"id", "statement", "evidence_claim_ids"}:
            raise ValidationError(f"atomic answer schema mismatch: {question_id}")
        answer_id = answer.get("id")
        statement = answer.get("statement")
        evidence_ids = answer.get("evidence_claim_ids")
        if not isinstance(answer_id, str) or answer_id in answer_ids:
            raise ValidationError(f"duplicate atomic answer id: {question_id}")
        if not isinstance(statement, str) or not isinstance(evidence_ids, list) or not evidence_ids:
            raise ValidationError(f"invalid atomic answer: {answer_id}")
        if not set(evidence_ids).issubset(claim_ids):
            raise ValidationError(f"atomic answer uses unbound evidence: {answer_id}")
        answer_words = word_set(statement)
        if len(answer_words) >= 8 and len(question_words & answer_words) / len(answer_words) > 0.8:
            raise ValidationError(f"question leaks most of atomic answer {answer_id}")
        used_claim_ids.update(evidence_ids)
        answer_ids.add(answer_id)
    derivation = ground_truth.get("derivation")
    if not isinstance(derivation, list) or len(derivation) < 2:
        raise ValidationError(f"missing explicit derivation: {question_id}")
    operations: set[str] = set()
    for step in derivation:
        if not isinstance(step, dict) or set(step) != {"operation", "inputs", "conclusion"}:
            raise ValidationError(f"derivation schema mismatch: {question_id}")
        operation = step.get("operation")
        inputs = step.get("inputs")
        if operation not in {"join", "contrast", "conditional", "exclusion"}:
            raise ValidationError(f"unknown derivation operation: {question_id}")
        if not isinstance(inputs, list) or not inputs or not set(inputs).issubset(answer_ids):
            raise ValidationError(f"derivation input mismatch: {question_id}")
        operations.add(operation)
    if len(operations) < 2:
        raise ValidationError(f"derivation is not structurally hard enough: {question_id}")
    variants = ground_truth.get("acceptable_variants")
    negatives = ground_truth.get("important_negatives")
    if not isinstance(variants, list) or not variants or not all(isinstance(item, str) for item in variants):
        raise ValidationError(f"acceptable variants are missing: {question_id}")
    if not isinstance(negatives, list) or not negatives:
        raise ValidationError(f"important negatives are missing: {question_id}")
    for negative in negatives:
        if not isinstance(negative, dict) or set(negative) != {"id", "statement", "evidence_claim_ids"}:
            raise ValidationError(f"negative schema mismatch: {question_id}")
        evidence_ids = negative.get("evidence_claim_ids")
        if not isinstance(evidence_ids, list) or not evidence_ids or not set(evidence_ids).issubset(claim_ids):
            raise ValidationError(f"negative uses unbound evidence: {question_id}")
        used_claim_ids.update(evidence_ids)
    if used_claim_ids != set(claim_ids):
        raise ValidationError(f"some selected evidence is unused: {question_id}")
    qrels = {"paper_ids": expected_papers, "source_ids": expected_sources}
    return {"id": question_id, "question": question, "qrels": qrels}


def validate_all(repo_root: Path, evaluation_dir: Path) -> None:
    manifest_path = evaluation_dir / "hard-ground-truth-manifest.json"
    manifest = load_json(manifest_path)
    validate_manifest(repo_root, manifest)
    ground_truth_records = load_jsonl(evaluation_dir / "hard-ground-truth.jsonl")
    hard_questions = load_jsonl(evaluation_dir / "hard-questions.jsonl")
    expanded_questions = load_jsonl(evaluation_dir / "retrieval-questions.jsonl")
    baseline_path = resolve_repo_path(
        repo_root, manifest["inputs"]["baseline_questions"]["path"]
    )
    baseline_questions = load_jsonl(baseline_path)
    if len(ground_truth_records) != 10 or len(hard_questions) != 10:
        raise ValidationError("expected ten hard ground truths and ten hard questions")
    validated_questions = [
        validate_ground_truth_record(repo_root, record) for record in ground_truth_records
    ]
    observed_prefixes = [record["id"].split("-", 1)[0] for record in validated_questions]
    if observed_prefixes != EXPECTED_HARD_IDS:
        raise ValidationError("hard question ids are not q031 through q040 in order")
    if hard_questions != validated_questions:
        raise ValidationError("hard-question qrels or prompts differ from independently derived ground truth")
    for prompt in hard_questions:
        if set(prompt) != {"id", "question", "qrels"}:
            raise ValidationError(f"hard prompt exposes unexpected fields: {prompt.get('id')}")
    if expanded_questions[:30] != baseline_questions:
        raise ValidationError("the original 30 retrieval questions were not retained exactly")
    if expanded_questions[30:] != hard_questions or len(expanded_questions) != 40:
        raise ValidationError("expanded benchmark is not exactly the 30 baseline plus 10 hard questions")
    all_ids = [record.get("id") for record in expanded_questions]
    if len(all_ids) != len(set(all_ids)):
        raise ValidationError("expanded benchmark contains duplicate ids")
    inventory_path = resolve_repo_path(
        repo_root, ground_truth_records[0]["corpus_inventory"]["path"]
    )
    expected_inventory_hash = digest_file(inventory_path)
    for record in ground_truth_records:
        if record["corpus_inventory"].get("sha256") != expected_inventory_hash:
            raise ValidationError(f"ground-truth inventory binding changed: {record['id']}")


def parse_args(argv: list[str]) -> argparse.Namespace:
    default_root = Path(__file__).resolve().parents[3]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=default_root)
    parser.add_argument(
        "--evaluation-dir",
        type=Path,
        default=Path("evaluations/semantic-okf-entity-graph"),
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    repo_root = args.repo_root.resolve()
    evaluation_dir = (
        args.evaluation_dir.resolve()
        if args.evaluation_dir.is_absolute()
        else (repo_root / args.evaluation_dir).resolve()
    )
    try:
        validate_all(repo_root, evaluation_dir)
        print(
            "Validated 10 evidence-first hard questions, every authoritative claim line and "
            "paper-page hash, and exact 30+10 benchmark composition."
        )
        return 0
    except ValidationError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
