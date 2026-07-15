#!/usr/bin/env python3
"""Generate evidence-valid hard questions and the expanded retrieval benchmark."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Any, Iterable


BLUEPRINT_SCHEMA = "semantic-okf-hard-question-evidence/1.0"
GROUND_TRUTH_SCHEMA = "semantic-okf-hard-ground-truth/1.0"
MANIFEST_SCHEMA = "semantic-okf-hard-ground-truth-manifest/1.0"
HARD_QUESTION_COUNT = 10
BASELINE_QUESTION_COUNT = 30
EXPECTED_CORE_FILES = 30
PAGE_HEADING_RE = re.compile(r"(?m)^## PDF page ([1-9][0-9]*)[ \t]*$")
LOCATOR_RE = re.compile(r"^(sources/markdown/([^/]+)\.md)#(PDF-page-([1-9][0-9]*))$")
CLAIM_ID_RE = re.compile(r"^claim-(.+)-([0-9]{3})$")
ALLOWED_DERIVATIONS = {"join", "contrast", "conditional", "exclusion"}


class GenerationError(RuntimeError):
    """Raised when evidence or a generated artifact violates the contract."""


def logical_text(path: Path) -> str:
    return path.read_bytes().decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def jsonl_text(records: Iterable[dict[str, Any]]) -> str:
    return "".join(canonical_json(record) + "\n" for record in records)


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(logical_text(path))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise GenerationError(f"cannot read JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise GenerationError(f"expected a JSON object in {path}")
    return value


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for line_number, line in enumerate(logical_text(path).splitlines(), start=1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise GenerationError(f"invalid JSONL at {path}:{line_number}: {exc}") from exc
        if not isinstance(value, dict):
            raise GenerationError(f"expected an object at {path}:{line_number}")
        records.append(value)
    return records


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, path)
    except BaseException:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise


def validate_inventory(repo_root: Path, inventory_path: Path) -> tuple[dict[str, Any], Path]:
    inventory = load_json(inventory_path)
    if inventory.get("schema_version") != "1.0":
        raise GenerationError("unsupported corpus inventory schema")
    files = inventory.get("files")
    if not isinstance(files, list) or len(files) != EXPECTED_CORE_FILES:
        raise GenerationError(f"corpus inventory must contain exactly {EXPECTED_CORE_FILES} files")
    corpus_root = repo_root / "evaluations" / "graphrag-cross-paper"
    roles = {"paper-markdown": 0, "reviewed-claims": 0}
    seen_paths: set[str] = set()
    for entry in files:
        if not isinstance(entry, dict):
            raise GenerationError("inventory file entries must be objects")
        relative = entry.get("path")
        role = entry.get("role")
        if not isinstance(relative, str) or relative in seen_paths:
            raise GenerationError("inventory paths must be unique strings")
        if role not in roles:
            raise GenerationError(f"unexpected inventory role for {relative}: {role!r}")
        seen_paths.add(relative)
        roles[role] += 1
        source_path = corpus_root / Path(relative)
        if not source_path.is_file():
            raise GenerationError(f"missing pinned corpus file: {relative}")
        actual_hash = sha256_file(source_path)
        if actual_hash != entry.get("sha256"):
            raise GenerationError(f"pinned corpus hash mismatch: {relative}")
    if roles != {"paper-markdown": 15, "reviewed-claims": 15}:
        raise GenerationError(f"expected 15 papers and 15 claim files, got {roles}")
    return inventory, corpus_root


def line_records(path: Path) -> list[tuple[int, int, int, str, dict[str, Any]]]:
    text = logical_text(path)
    records: list[tuple[int, int, int, str, dict[str, Any]]] = []
    offset = 0
    for line_number, with_ending in enumerate(text.splitlines(keepends=True), start=1):
        line = with_ending[:-1] if with_ending.endswith("\n") else with_ending
        if line.strip():
            try:
                value = json.loads(line)
            except json.JSONDecodeError as exc:
                raise GenerationError(f"invalid claim JSON at {path}:{line_number}: {exc}") from exc
            if not isinstance(value, dict):
                raise GenerationError(f"claim at {path}:{line_number} must be an object")
            records.append((line_number, offset, offset + len(line), line, value))
        offset += len(with_ending)
    return records


def build_claim_index(
    repo_root: Path, corpus_root: Path, inventory: dict[str, Any]
) -> dict[str, dict[str, Any]]:
    claims: dict[str, dict[str, Any]] = {}
    for entry in inventory["files"]:
        if entry["role"] != "reviewed-claims":
            continue
        relative = entry["path"]
        path = corpus_root / relative
        paper_id = entry["paper_id"]
        for line_number, char_start, char_end, line, claim in line_records(path):
            claim_id = claim.get("id")
            if not isinstance(claim_id, str) or not CLAIM_ID_RE.fullmatch(claim_id):
                raise GenerationError(f"invalid claim id at {relative}:{line_number}")
            if claim_id in claims:
                raise GenerationError(f"duplicate claim id: {claim_id}")
            if claim.get("review_state") != "reviewed":
                raise GenerationError(f"hard-question evidence must be reviewed: {claim_id}")
            claims[claim_id] = {
                "record": claim,
                "paper_id": paper_id,
                "source": {
                    "path": (Path("evaluations/graphrag-cross-paper") / relative).as_posix(),
                    "line_number": line_number,
                    "char_start": char_start,
                    "char_end": char_end,
                    "record_sha256": sha256_text(line),
                },
            }
    return claims


def page_ranges(path: Path) -> dict[str, tuple[int, int, str]]:
    text = logical_text(path)
    matches = list(PAGE_HEADING_RE.finditer(text))
    if not matches:
        raise GenerationError(f"paper has no PDF-page locators: {path}")
    ranges: dict[str, tuple[int, int, str]] = {}
    for index, match in enumerate(matches):
        locator = f"PDF-page-{match.group(1)}"
        if locator in ranges:
            raise GenerationError(f"duplicate locator {locator} in {path}")
        start = match.start()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        ranges[locator] = (start, end, text[start:end])
    return ranges


def resolve_paper_evidence(
    repo_root: Path, expected_paper_id: str, evidence_locator: str
) -> list[dict[str, Any]]:
    if not evidence_locator:
        raise GenerationError(f"claim {expected_paper_id} has an empty evidence locator")
    resolved: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for raw_locator in evidence_locator.split(";"):
        match = LOCATOR_RE.fullmatch(raw_locator)
        if not match:
            raise GenerationError(f"invalid evidence locator: {raw_locator}")
        source_relative, paper_id, locator = match.group(1), match.group(2), match.group(3)
        if paper_id != expected_paper_id:
            raise GenerationError(
                f"locator paper {paper_id} does not match claim paper {expected_paper_id}"
            )
        key = (source_relative, locator)
        if key in seen:
            raise GenerationError(f"duplicate evidence locator: {raw_locator}")
        seen.add(key)
        source_path = repo_root / "evaluations" / "graphrag-cross-paper" / source_relative
        if not source_path.is_file():
            raise GenerationError(f"missing paper evidence file: {source_relative}")
        ranges = page_ranges(source_path)
        if locator not in ranges:
            raise GenerationError(f"missing paper locator {locator} in {source_relative}")
        start, end, segment = ranges[locator]
        resolved.append(
            {
                "path": (Path("evaluations/graphrag-cross-paper") / source_relative).as_posix(),
                "locator": locator,
                "char_start": start,
                "char_end": end,
                "text_length": len(segment),
                "text_sha256": sha256_text(segment),
            }
        )
    return resolved


def require_string_list(value: Any, label: str, *, minimum: int = 1) -> list[str]:
    if not isinstance(value, list) or len(value) < minimum:
        raise GenerationError(f"{label} must contain at least {minimum} strings")
    if any(not isinstance(item, str) or not item.strip() for item in value):
        raise GenerationError(f"{label} must contain non-empty strings")
    if len(value) != len(set(value)):
        raise GenerationError(f"{label} must not contain duplicates")
    return value


def validate_blueprint(blueprint: dict[str, Any], claims: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    if blueprint.get("schema_version") != BLUEPRINT_SCHEMA:
        raise GenerationError("unsupported hard-question evidence schema")
    workflow = blueprint.get("workflow")
    if not isinstance(workflow, dict) or workflow.get("question_count") != HARD_QUESTION_COUNT:
        raise GenerationError("hard-question workflow must declare ten questions")
    questions = blueprint.get("questions")
    if not isinstance(questions, list) or len(questions) != HARD_QUESTION_COUNT:
        raise GenerationError(f"expected exactly {HARD_QUESTION_COUNT} hard questions")
    expected_ids = [f"q{number:03d}" for number in range(31, 41)]
    observed_prefixes: list[str] = []
    all_answer_ids: set[str] = set()
    all_question_texts: set[str] = set()
    for question in questions:
        if not isinstance(question, dict):
            raise GenerationError("hard-question entries must be objects")
        question_id = question.get("id")
        if not isinstance(question_id, str):
            raise GenerationError("hard-question id must be a string")
        observed_prefixes.append(question_id.split("-", 1)[0])
        text = question.get("question")
        if not isinstance(text, str) or len(text.split()) < 18:
            raise GenerationError(f"question {question_id} is too short")
        if text in all_question_texts:
            raise GenerationError(f"duplicate hard-question text: {question_id}")
        all_question_texts.add(text)
        selected = require_string_list(question.get("evidence_claim_ids"), f"{question_id}.evidence_claim_ids", minimum=3)
        missing = [claim_id for claim_id in selected if claim_id not in claims]
        if missing:
            raise GenerationError(f"{question_id} references missing claims: {missing}")
        paper_ids = {claims[claim_id]["paper_id"] for claim_id in selected}
        if len(paper_ids) < 3:
            raise GenerationError(f"{question_id} must join evidence from at least three papers")
        answer_claims = question.get("answer_claims")
        if not isinstance(answer_claims, list) or len(answer_claims) < 3:
            raise GenerationError(f"{question_id} must contain at least three atomic answer claims")
        local_answer_ids: set[str] = set()
        referenced_evidence: set[str] = set()
        for answer_claim in answer_claims:
            if not isinstance(answer_claim, dict):
                raise GenerationError(f"{question_id} answer claims must be objects")
            answer_id = answer_claim.get("id")
            statement = answer_claim.get("statement")
            if not isinstance(answer_id, str) or not answer_id.startswith(f"{question_id.split('-', 1)[0]}-a"):
                raise GenerationError(f"invalid atomic answer id in {question_id}: {answer_id!r}")
            if answer_id in all_answer_ids or answer_id in local_answer_ids:
                raise GenerationError(f"duplicate atomic answer id: {answer_id}")
            if not isinstance(statement, str) or len(statement.split()) < 9:
                raise GenerationError(f"atomic answer {answer_id} is too short")
            evidence_ids = require_string_list(
                answer_claim.get("evidence_claim_ids"), f"{answer_id}.evidence_claim_ids"
            )
            if not set(evidence_ids).issubset(selected):
                raise GenerationError(f"atomic answer {answer_id} uses unselected evidence")
            referenced_evidence.update(evidence_ids)
            local_answer_ids.add(answer_id)
            all_answer_ids.add(answer_id)
        derivation = question.get("derivation")
        if not isinstance(derivation, list) or len(derivation) < 2:
            raise GenerationError(f"{question_id} needs at least two explicit derivation steps")
        operations: set[str] = set()
        for step in derivation:
            if not isinstance(step, dict):
                raise GenerationError(f"{question_id} derivation steps must be objects")
            operation = step.get("operation")
            if operation not in ALLOWED_DERIVATIONS:
                raise GenerationError(f"unsupported derivation operation in {question_id}: {operation!r}")
            operations.add(operation)
            inputs = require_string_list(step.get("inputs"), f"{question_id}.derivation.inputs")
            if not set(inputs).issubset(local_answer_ids):
                raise GenerationError(f"{question_id} derivation refers to unknown atomic answers")
            conclusion = step.get("conclusion")
            if not isinstance(conclusion, str) or len(conclusion.split()) < 8:
                raise GenerationError(f"{question_id} derivation conclusion is too short")
        if len(operations) < 2:
            raise GenerationError(f"{question_id} must use at least two derivation operation types")
        require_string_list(question.get("acceptable_variants"), f"{question_id}.acceptable_variants")
        negatives = question.get("important_negatives")
        if not isinstance(negatives, list) or not negatives:
            raise GenerationError(f"{question_id} must define important negatives")
        negative_ids: set[str] = set()
        for negative in negatives:
            if not isinstance(negative, dict):
                raise GenerationError(f"{question_id} negatives must be objects")
            negative_id = negative.get("id")
            statement = negative.get("statement")
            if not isinstance(negative_id, str) or negative_id in negative_ids:
                raise GenerationError(f"invalid or duplicate negative id in {question_id}")
            if not isinstance(statement, str) or len(statement.split()) < 8:
                raise GenerationError(f"negative {negative_id} is too short")
            evidence_ids = require_string_list(
                negative.get("evidence_claim_ids"), f"{negative_id}.evidence_claim_ids"
            )
            if not set(evidence_ids).issubset(selected):
                raise GenerationError(f"negative {negative_id} uses unselected evidence")
            referenced_evidence.update(evidence_ids)
            negative_ids.add(negative_id)
        if referenced_evidence != set(selected):
            unused = sorted(set(selected) - referenced_evidence)
            raise GenerationError(f"{question_id} has selected but unused evidence: {unused}")
    if observed_prefixes != expected_ids:
        raise GenerationError(f"hard-question ids must run from q031 through q040: {observed_prefixes}")
    return questions


def materialize_ground_truth(
    repo_root: Path,
    questions: list[dict[str, Any]],
    claims: dict[str, dict[str, Any]],
    inventory_path: Path,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    ground_truth: list[dict[str, Any]] = []
    hard_questions: list[dict[str, Any]] = []
    inventory_hash = sha256_file(inventory_path)
    for question in questions:
        selected_claims: list[dict[str, Any]] = []
        paper_ids: set[str] = set()
        for claim_id in question["evidence_claim_ids"]:
            indexed = claims[claim_id]
            claim = indexed["record"]
            paper_id = indexed["paper_id"]
            paper_ids.add(paper_id)
            selected_claims.append(
                {
                    "claim_id": claim_id,
                    "paper_id": paper_id,
                    "claim_kind": claim["claim_kind"],
                    "review_state": claim["review_state"],
                    "interpretation": claim["interpretation"],
                    "interpretation_sha256": sha256_text(claim["interpretation"]),
                    "claim_source": indexed["source"],
                    "paper_evidence": resolve_paper_evidence(
                        repo_root, paper_id, claim["evidence_locator"]
                    ),
                }
            )
        sorted_paper_ids = sorted(paper_ids)
        source_ids = sorted(
            [f"claims-{paper_id.replace('.', '-')}" for paper_id in sorted_paper_ids]
            + [f"paper-{paper_id.replace('.', '-')}" for paper_id in sorted_paper_ids]
        )
        qrels = {"paper_ids": sorted_paper_ids, "source_ids": source_ids}
        hard_questions.append(
            {"id": question["id"], "question": question["question"], "qrels": qrels}
        )
        ground_truth.append(
            {
                "schema_version": GROUND_TRUTH_SCHEMA,
                "id": question["id"],
                "corpus_inventory": {
                    "path": inventory_path.relative_to(repo_root).as_posix(),
                    "sha256": inventory_hash,
                },
                "authoritative_evidence": selected_claims,
                "ground_truth": {
                    "answer_claims": question["answer_claims"],
                    "required_paper_ids": sorted_paper_ids,
                    "required_source_ids": source_ids,
                    "derivation": question["derivation"],
                    "acceptable_variants": question["acceptable_variants"],
                    "important_negatives": question["important_negatives"],
                },
                "question": question["question"],
            }
        )
    return ground_truth, hard_questions


def build_outputs(
    repo_root: Path,
    blueprint_path: Path,
    baseline_path: Path,
    inventory_path: Path,
) -> dict[str, str]:
    inventory, corpus_root = validate_inventory(repo_root, inventory_path)
    claims = build_claim_index(repo_root, corpus_root, inventory)
    blueprint = load_json(blueprint_path)
    questions = validate_blueprint(blueprint, claims)
    baseline_questions = load_jsonl(baseline_path)
    if len(baseline_questions) != BASELINE_QUESTION_COUNT:
        raise GenerationError(f"expected {BASELINE_QUESTION_COUNT} baseline questions")
    ground_truth, hard_questions = materialize_ground_truth(
        repo_root, questions, claims, inventory_path
    )
    baseline_ids = [record.get("id") for record in baseline_questions]
    hard_ids = [record["id"] for record in hard_questions]
    if len(set(baseline_ids + hard_ids)) != BASELINE_QUESTION_COUNT + HARD_QUESTION_COUNT:
        raise GenerationError("expanded benchmark question ids are not unique")
    ground_truth_text = jsonl_text(ground_truth)
    hard_questions_text = jsonl_text(hard_questions)
    expanded_text = jsonl_text([*baseline_questions, *hard_questions])
    output_hashes = {
        "hard-ground-truth.jsonl": sha256_text(ground_truth_text),
        "hard-questions.jsonl": sha256_text(hard_questions_text),
        "retrieval-questions.jsonl": sha256_text(expanded_text),
    }
    manifest = {
        "schema_version": MANIFEST_SCHEMA,
        "generator": "scripts/generate_hard_questions.py",
        "contracts": {
            "evidence_offsets": "zero-based Unicode code-point offsets over UTF-8 text after CRLF/CR normalization to LF; char_end is exclusive",
            "paper_segment": "from the exact PDF-page heading through the character before the next PDF-page heading, or EOF",
            "claim_record": "one non-empty logical JSONL line without its LF terminator",
            "question_prompt": "question text only; evaluator ground truth is never exposed",
        },
        "inputs": {
            "blueprint": {
                "path": blueprint_path.relative_to(repo_root).as_posix(),
                "sha256": sha256_text(logical_text(blueprint_path)),
            },
            "baseline_questions": {
                "path": baseline_path.relative_to(repo_root).as_posix(),
                "sha256": sha256_text(logical_text(baseline_path)),
                "count": BASELINE_QUESTION_COUNT,
            },
            "corpus_inventory": {
                "path": inventory_path.relative_to(repo_root).as_posix(),
                "sha256": sha256_file(inventory_path),
                "core_file_count": EXPECTED_CORE_FILES,
            },
        },
        "outputs": {
            name: {
                "path": f"evaluations/semantic-okf-classical/{name}",
                "sha256": digest,
                "count": (
                    HARD_QUESTION_COUNT
                    if name != "retrieval-questions.jsonl"
                    else BASELINE_QUESTION_COUNT + HARD_QUESTION_COUNT
                ),
            }
            for name, digest in sorted(output_hashes.items())
        },
    }
    return {
        "hard-ground-truth.jsonl": ground_truth_text,
        "hard-questions.jsonl": hard_questions_text,
        "retrieval-questions.jsonl": expanded_text,
        "hard-ground-truth-manifest.json": json.dumps(
            manifest, ensure_ascii=False, sort_keys=True, indent=2
        )
        + "\n",
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    default_root = Path(__file__).resolve().parents[3]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=default_root)
    parser.add_argument(
        "--blueprint",
        type=Path,
        default=Path("evaluations/semantic-okf-classical/hard-question-evidence.json"),
    )
    parser.add_argument(
        "--baseline-questions",
        type=Path,
        default=Path("evaluations/semantic-okf-embeddings/retrieval-questions.jsonl"),
    )
    parser.add_argument(
        "--inventory",
        type=Path,
        default=Path("evaluations/semantic-okf-embeddings/input-inventory.json"),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("evaluations/semantic-okf-classical"),
    )
    parser.add_argument("--check", action="store_true", help="fail if checked-in outputs differ")
    return parser.parse_args(argv)


def absolute_under(root: Path, value: Path) -> Path:
    return value if value.is_absolute() else root / value


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    repo_root = args.repo_root.resolve()
    blueprint_path = absolute_under(repo_root, args.blueprint).resolve()
    baseline_path = absolute_under(repo_root, args.baseline_questions).resolve()
    inventory_path = absolute_under(repo_root, args.inventory).resolve()
    output_dir = absolute_under(repo_root, args.output_dir).resolve()
    try:
        outputs = build_outputs(repo_root, blueprint_path, baseline_path, inventory_path)
        if args.check:
            mismatches = []
            for name, expected in outputs.items():
                path = output_dir / name
                if not path.is_file() or logical_text(path) != expected:
                    mismatches.append(name)
            if mismatches:
                raise GenerationError(
                    "checked-in hard-question artifacts are stale: " + ", ".join(mismatches)
                )
            print("Hard-question artifacts are deterministic and current.")
            return 0
        for name, content in outputs.items():
            atomic_write(output_dir / name, content)
        print(
            "Generated 10 evidence-first hard questions, 10 ground-truth records, "
            "and the 40-question retrieval benchmark."
        )
        return 0
    except GenerationError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
