#!/usr/bin/env python3
"""Generate the append-only reviewed Semantic OKF answer benchmark."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Any, Iterable


AMENDMENTS_SCHEMA = "semantic-okf-reviewed-benchmark-amendments/1.0"
GROUND_TRUTH_SCHEMA = "semantic-okf-hard-ground-truth/1.0"
GROUND_TRUTH_MANIFEST_SCHEMA = "semantic-okf-hard-ground-truth-manifest/1.0"
FROZEN_MANIFEST_SCHEMA = "semantic-okf-frozen-answer-benchmark/1.0"
BENCHMARK_ID = "semantic-okf-ensemble-reviewed-answer-40-plus-hard10-v1"
PARENT_BENCHMARK_ID = "semantic-okf-adaptive-frozen-40-plus-hard10-v1"
FROZEN_ON = "2026-07-15"
EXPECTED_HARD_IDS = [f"q{number:03d}" for number in range(31, 41)]
PAGE_HEADING_RE = re.compile(r"(?m)^## PDF page ([1-9][0-9]*)[ \t]*$")
LOCATOR_RE = re.compile(r"^(sources/markdown/([^/]+)\.md)#(PDF-page-([1-9][0-9]*))$")
CLAIM_ID_RE = re.compile(r"^claim-(.+)-([0-9]{3})$")

EVALUATION_ROOT = Path("evaluations/semantic-okf-ensemble")
OUTPUT_ROOT = EVALUATION_ROOT / "reviewed-benchmark"
AMENDMENTS_PATH = EVALUATION_ROOT / "reviewed-answer-benchmark-amendments.json"
GENERATOR_PATH = EVALUATION_ROOT / "scripts/generate_reviewed_answer_benchmark.py"
PARENT_GROUND_TRUTH_PATH = Path("evaluations/semantic-okf-adaptive/hard-ground-truth.jsonl")
PARENT_HARD_QUESTIONS_PATH = Path("evaluations/semantic-okf-adaptive/hard-questions.jsonl")
PARENT_RETRIEVAL_QUESTIONS_PATH = Path(
    "evaluations/semantic-okf-adaptive/retrieval-questions.jsonl"
)
PARENT_FROZEN_MANIFEST_PATH = Path(
    "evaluations/semantic-okf-adaptive-evolution/frozen-benchmark.json"
)
BASELINE_QUESTIONS_PATH = Path("evaluations/semantic-okf-embeddings/retrieval-questions.jsonl")
INVENTORY_PATH = Path("evaluations/semantic-okf-embeddings/input-inventory.json")
CORPUS_ROOT = Path("evaluations/graphrag-cross-paper")

# This independent allowlist prevents a modified amendments document from silently
# widening the benchmark. The JSON carries review rationale; this tuple carries authority.
APPROVED_ADDITIONS: tuple[tuple[str, str, str, tuple[str, ...]], ...] = (
    ("q031-graph-routing-boundary", "answer_claim", "q031-a4", ("claim-2503-13804v1-037",)),
    ("q031-graph-routing-boundary", "important_negative", "q031-n1", ("claim-2506-05690v3-029",)),
    ("q032-incremental-update-maturity", "answer_claim", "q032-a1", ("claim-2410-05779v3-010", "claim-2410-05779v3-053")),
    ("q032-incremental-update-maturity", "answer_claim", "q032-a2", ("claim-2405-14831v3-044",)),
    ("q032-incremental-update-maturity", "answer_claim", "q032-a4", ("claim-2408-04187v2-037",)),
    ("q033-corruption-specific-defenses", "important_negative", "q033-n1", ("claim-2502-14902v2-033", "claim-2409-13731v3-039")),
    ("q034-nonmonotonic-context-budget", "answer_claim", "q034-a1", ("claim-2402-07630v3-037",)),
    ("q034-nonmonotonic-context-budget", "answer_claim", "q034-a3", ("claim-2408-08535v1-032",)),
    ("q034-nonmonotonic-context-budget", "answer_claim", "q034-a4", ("claim-2503-06474v2-042",)),
    ("q034-nonmonotonic-context-budget", "important_negative", "q034-n1", ("claim-2406-14550v2-039", "claim-2503-06474v2-042")),
    ("q035-lossless-enough-evidence-organization", "answer_claim", "q035-a1", ("claim-2402-07630v3-019", "claim-2402-07630v3-055")),
    ("q035-lossless-enough-evidence-organization", "answer_claim", "q035-a2", ("claim-2502-14902v2-031",)),
    ("q035-lossless-enough-evidence-organization", "answer_claim", "q035-a4", ("claim-2404-16130v2-057",)),
    ("q035-lossless-enough-evidence-organization", "important_negative", "q035-n1", ("claim-2402-07630v3-019", "claim-2402-07630v3-055", "claim-2502-14902v2-031", "claim-2404-16130v2-057")),
    ("q036-evaluation-leakage-and-stage-separation", "answer_claim", "q036-a1", ("claim-2506-05690v3-042",)),
    ("q036-evaluation-leakage-and-stage-separation", "answer_claim", "q036-a3", ("claim-2508-19855v3-029",)),
    ("q036-evaluation-leakage-and-stage-separation", "answer_claim", "q036-a5", ("claim-2410-05779v3-054",)),
    ("q036-evaluation-leakage-and-stage-separation", "important_negative", "q036-n1", ("claim-2508-19855v3-029",)),
    ("q036-evaluation-leakage-and-stage-separation", "important_negative", "q036-n2", ("claim-2410-05779v3-054",)),
    ("q037-domain-construction-under-constraints", "answer_claim", "q037-a2", ("claim-2507-03226v3-031",)),
    ("q037-domain-construction-under-constraints", "answer_claim", "q037-a4", ("claim-2508-19855v3-031",)),
    ("q037-domain-construction-under-constraints", "important_negative", "q037-n1", ("claim-2507-03226v3-031",)),
    ("q037-domain-construction-under-constraints", "important_negative", "q037-n2", ("claim-2508-19855v3-031",)),
    ("q038-failure-aware-query-router", "answer_claim", "q038-a3", ("claim-2503-06474v2-018",)),
    ("q038-failure-aware-query-router", "important_negative", "q038-n1", ("claim-2503-06474v2-018",)),
    ("q039-baseline-bound-efficiency-claims", "answer_claim", "q039-a3", ("claim-2410-05779v3-040",)),
    ("q039-baseline-bound-efficiency-claims", "important_negative", "q039-n1", ("claim-2404-16130v2-041", "claim-2410-05779v3-040")),
    ("q040-answer-source-control", "answer_claim", "q040-a1", ("claim-2503-13804v1-015",)),
    ("q040-answer-source-control", "answer_claim", "q040-a2", ("claim-2503-06474v2-024",)),
    ("q040-answer-source-control", "answer_claim", "q040-a4", ("claim-2508-19855v3-029",)),
    ("q040-answer-source-control", "important_negative", "q040-n1", ("claim-2508-19855v3-029",)),
    ("q040-answer-source-control", "important_negative", "q040-n2", ("claim-2503-13804v1-015", "claim-2503-06474v2-024")),
)


class GenerationError(RuntimeError):
    """Raised when a source or generated artifact violates the frozen contract."""


def logical_text(path: Path) -> str:
    """Read UTF-8 text with newlines normalized to LF."""

    return path.read_bytes().decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")


def digest_bytes(data: bytes) -> str:
    """Return a lowercase SHA-256 digest for bytes."""

    return hashlib.sha256(data).hexdigest()


def digest_text(text: str) -> str:
    """Return a SHA-256 digest for UTF-8 text."""

    return digest_bytes(text.encode("utf-8"))


def digest_file(path: Path) -> str:
    """Return a SHA-256 digest for an exact file."""

    return digest_bytes(path.read_bytes())


def canonical_json(value: Any) -> str:
    """Serialize one canonical compact JSON value."""

    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def canonical_jsonl(records: Iterable[dict[str, Any]]) -> bytes:
    """Serialize records as canonical LF-terminated JSON Lines."""

    return "".join(canonical_json(record) + "\n" for record in records).encode("utf-8")


def pretty_json(value: Any) -> bytes:
    """Serialize a deterministic, readable JSON document."""

    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode(
        "utf-8"
    )


def load_json(path: Path) -> dict[str, Any]:
    """Load one JSON object or raise a stable generation error."""

    try:
        value = json.loads(logical_text(path))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise GenerationError(f"cannot read JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise GenerationError(f"expected a JSON object in {path}")
    return value


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    """Load non-empty JSONL object records."""

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


def repo_path(repo_root: Path, relative: Path) -> Path:
    """Resolve a pinned repository-relative path without allowing escape."""

    candidate = (repo_root / relative).resolve()
    try:
        candidate.relative_to(repo_root)
    except ValueError as exc:
        raise GenerationError(f"path escapes repository root: {relative.as_posix()}") from exc
    return candidate


def logical_line_index(path: Path) -> list[tuple[int, int, int, str, dict[str, Any]]]:
    """Index logical JSONL lines with Unicode code-point offsets."""

    rows: list[tuple[int, int, int, str, dict[str, Any]]] = []
    offset = 0
    for line_number, with_ending in enumerate(logical_text(path).splitlines(keepends=True), start=1):
        line = with_ending[:-1] if with_ending.endswith("\n") else with_ending
        if line.strip():
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise GenerationError(f"invalid claim JSON at {path}:{line_number}: {exc}") from exc
            if not isinstance(record, dict):
                raise GenerationError(f"claim at {path}:{line_number} is not an object")
            rows.append((line_number, offset, offset + len(line), line, record))
        offset += len(with_ending)
    return rows


def page_segments(path: Path) -> dict[str, tuple[int, int, str]]:
    """Return exact PDF-page segments and Unicode code-point ranges."""

    text = logical_text(path)
    headings = list(PAGE_HEADING_RE.finditer(text))
    if not headings:
        raise GenerationError(f"paper contains no PDF-page headings: {path}")
    segments: dict[str, tuple[int, int, str]] = {}
    for index, heading in enumerate(headings):
        locator = f"PDF-page-{heading.group(1)}"
        if locator in segments:
            raise GenerationError(f"duplicate paper locator {locator}: {path}")
        start = heading.start()
        end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
        segments[locator] = (start, end, text[start:end])
    return segments


def validate_inventory(repo_root: Path) -> tuple[dict[str, Any], dict[str, str]]:
    """Validate all pinned corpus files and return their paper roles."""

    inventory_path = repo_path(repo_root, INVENTORY_PATH)
    inventory = load_json(inventory_path)
    if inventory.get("schema_version") != "1.0":
        raise GenerationError("unsupported corpus inventory schema")
    if inventory.get("core_file_count") != 30 or inventory.get("core_record_count") != 846:
        raise GenerationError("corpus inventory declared counts changed")
    files = inventory.get("files")
    if not isinstance(files, list) or len(files) != 30:
        raise GenerationError("corpus inventory must contain exactly 30 core files")
    roles = {"paper-markdown": 0, "reviewed-claims": 0}
    path_to_paper: dict[str, str] = {}
    seen: set[str] = set()
    for entry in files:
        if not isinstance(entry, dict):
            raise GenerationError("corpus inventory entries must be objects")
        relative = entry.get("path")
        paper_id = entry.get("paper_id")
        role = entry.get("role")
        if not isinstance(relative, str) or not isinstance(paper_id, str) or relative in seen:
            raise GenerationError("corpus inventory paths and paper identities must be unique strings")
        if role not in roles:
            raise GenerationError(f"unexpected corpus inventory role: {role!r}")
        seen.add(relative)
        roles[role] += 1
        path = repo_path(repo_root, CORPUS_ROOT / relative)
        if not path.is_file() or digest_file(path) != entry.get("sha256"):
            raise GenerationError(f"pinned corpus hash mismatch: {relative}")
        path_to_paper[relative] = paper_id
    if roles != {"paper-markdown": 15, "reviewed-claims": 15}:
        raise GenerationError(f"pinned corpus role counts changed: {roles}")
    return inventory, path_to_paper


def build_claim_index(
    repo_root: Path, inventory: dict[str, Any], path_to_paper: dict[str, str]
) -> dict[str, dict[str, Any]]:
    """Index every reviewed claim from authoritative pinned JSONL sources."""

    claims: dict[str, dict[str, Any]] = {}
    for entry in inventory["files"]:
        if entry["role"] != "reviewed-claims":
            continue
        relative = entry["path"]
        paper_id = path_to_paper[relative]
        path = repo_path(repo_root, CORPUS_ROOT / relative)
        for line_number, start, end, line, record in logical_line_index(path):
            claim_id = record.get("id")
            if not isinstance(claim_id, str) or not CLAIM_ID_RE.fullmatch(claim_id):
                raise GenerationError(f"invalid claim ID at {relative}:{line_number}")
            if claim_id in claims:
                raise GenerationError(f"duplicate claim ID: {claim_id}")
            if record.get("review_state") != "reviewed":
                raise GenerationError(f"claim is not reviewed: {claim_id}")
            claims[claim_id] = {
                "paper_id": paper_id,
                "record": record,
                "source": {
                    "path": (CORPUS_ROOT / relative).as_posix(),
                    "line_number": line_number,
                    "char_start": start,
                    "char_end": end,
                    "record_sha256": digest_text(line),
                },
            }
    if len(claims) != 831:
        raise GenerationError(f"reviewed claim inventory changed: expected 831, got {len(claims)}")
    return claims


def derive_paper_evidence(
    repo_root: Path, paper_id: str, locator_value: Any
) -> list[dict[str, Any]]:
    """Derive exact page ranges and hashes from one claim locator string."""

    if not isinstance(locator_value, str) or not locator_value:
        raise GenerationError(f"claim {paper_id} has an empty evidence locator")
    result: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for raw_locator in locator_value.split(";"):
        match = LOCATOR_RE.fullmatch(raw_locator)
        if not match or match.group(2) != paper_id:
            raise GenerationError(f"claim locator does not match paper {paper_id}: {raw_locator!r}")
        relative_source, locator = match.group(1), match.group(3)
        key = (relative_source, locator)
        if key in seen:
            raise GenerationError(f"duplicate evidence locator: {raw_locator}")
        seen.add(key)
        source_path = repo_path(repo_root, CORPUS_ROOT / relative_source)
        segments = page_segments(source_path)
        if locator not in segments:
            raise GenerationError(f"missing locator {locator}: {relative_source}")
        start, end, text = segments[locator]
        result.append(
            {
                "path": (CORPUS_ROOT / relative_source).as_posix(),
                "locator": locator,
                "char_start": start,
                "char_end": end,
                "text_length": len(text),
                "text_sha256": digest_text(text),
            }
        )
    return result


def derive_authoritative_evidence(
    repo_root: Path, claim_id: str, claims: dict[str, dict[str, Any]]
) -> dict[str, Any]:
    """Derive one closed ground-truth evidence object from authoritative inputs."""

    if claim_id not in claims:
        raise GenerationError(f"approved claim does not exist: {claim_id}")
    indexed = claims[claim_id]
    record = indexed["record"]
    interpretation = record.get("interpretation")
    claim_kind = record.get("claim_kind")
    if not isinstance(interpretation, str) or not interpretation or not isinstance(claim_kind, str):
        raise GenerationError(f"approved claim lacks required reviewed fields: {claim_id}")
    return {
        "claim_id": claim_id,
        "paper_id": indexed["paper_id"],
        "claim_kind": claim_kind,
        "review_state": "reviewed",
        "interpretation": interpretation,
        "interpretation_sha256": digest_text(interpretation),
        "claim_source": indexed["source"],
        "paper_evidence": derive_paper_evidence(
            repo_root, indexed["paper_id"], record.get("evidence_locator")
        ),
    }


def validate_amendments(amendments: dict[str, Any]) -> None:
    """Validate the closed amendments document against the independent allowlist."""

    expected_root = {
        "schema_version",
        "amendment_id",
        "parent_benchmark_id",
        "language",
        "addition_policy",
        "additions",
        "rejected_close_alternatives",
    }
    if set(amendments) != expected_root:
        raise GenerationError("amendments root schema is open or incomplete")
    if amendments.get("schema_version") != AMENDMENTS_SCHEMA:
        raise GenerationError("unsupported amendments schema")
    if amendments.get("parent_benchmark_id") != PARENT_BENCHMARK_ID:
        raise GenerationError("amendments parent benchmark changed")
    if amendments.get("language") != "en":
        raise GenerationError("amendments must be documented in English")
    policy = amendments.get("addition_policy")
    policy_keys = {
        "operation",
        "atomic_or_equivalence",
        "negative_or_equivalence",
        "paper_identity",
        "partial_conjunctions",
    }
    if not isinstance(policy, dict) or set(policy) != policy_keys:
        raise GenerationError("amendments addition policy schema changed")
    if any(not isinstance(value, str) or not value.strip() for value in policy.values()):
        raise GenerationError("amendments policy values must be non-empty English declarations")

    additions = amendments.get("additions")
    if not isinstance(additions, list):
        raise GenerationError("amendments additions must be a list")
    observed: list[tuple[str, str, str, tuple[str, ...]]] = []
    approved_pairs: set[tuple[str, str]] = set()
    for addition in additions:
        if not isinstance(addition, dict) or set(addition) != {
            "question_id",
            "group_kind",
            "group_id",
            "append_claims",
        }:
            raise GenerationError("amendment addition schema changed")
        claims = addition["append_claims"]
        if not isinstance(claims, list) or not claims:
            raise GenerationError("amendment addition must append at least one claim")
        identifiers: list[str] = []
        for claim in claims:
            if not isinstance(claim, dict) or set(claim) != {
                "claim_id",
                "or_equivalence_rationale",
            }:
                raise GenerationError("amendment claim schema changed")
            claim_id = claim["claim_id"]
            rationale = claim["or_equivalence_rationale"]
            if not isinstance(claim_id, str) or not isinstance(rationale, str) or not rationale.strip():
                raise GenerationError("amendment claim fields must be non-empty strings")
            identifiers.append(claim_id)
            approved_pairs.add((addition["group_id"], claim_id))
        if len(identifiers) != len(set(identifiers)):
            raise GenerationError(f"duplicate appended claim in {addition['group_id']}")
        observed.append(
            (
                addition["question_id"],
                addition["group_kind"],
                addition["group_id"],
                tuple(identifiers),
            )
        )
    if tuple(observed) != APPROVED_ADDITIONS:
        raise GenerationError("amendment additions differ from the independently approved allowlist")

    rejected = amendments.get("rejected_close_alternatives")
    if not isinstance(rejected, list) or len(rejected) != 38:
        raise GenerationError("expected exactly 38 reviewed close-alternative rejections")
    rejected_keys: set[tuple[str, str, str]] = set()
    for item in rejected:
        if not isinstance(item, dict) or set(item) != {
            "question_id",
            "group_id",
            "claim_id",
            "reason",
        }:
            raise GenerationError("rejected close-alternative schema changed")
        values = [item[key] for key in ("question_id", "group_id", "claim_id", "reason")]
        if any(not isinstance(value, str) or not value.strip() for value in values):
            raise GenerationError("rejected close-alternative fields must be non-empty strings")
        identity = (item["question_id"], item["group_id"], item["claim_id"])
        if identity in rejected_keys:
            raise GenerationError(f"duplicate rejected close alternative: {identity}")
        if (item["group_id"], item["claim_id"]) in approved_pairs:
            raise GenerationError(f"claim is both approved and rejected for {item['group_id']}")
        rejected_keys.add(identity)


def option_groups(record: dict[str, Any], group_kind: str) -> list[dict[str, Any]]:
    """Return the parent option-group list for one closed group kind."""

    ground_truth = record["ground_truth"]
    if group_kind == "answer_claim":
        return ground_truth["answer_claims"]
    if group_kind == "important_negative":
        return ground_truth["important_negatives"]
    raise GenerationError(f"unsupported option-group kind: {group_kind}")


def count_links(records: list[dict[str, Any]], section: str) -> int:
    """Count expected-claim option links in a ground-truth section."""

    return sum(
        len(group["evidence_claim_ids"])
        for record in records
        for group in record["ground_truth"][section]
    )


def expected_claim_ids(records: list[dict[str, Any]]) -> set[str]:
    """Return unique expected claim IDs across answers and negatives."""

    return {
        claim_id
        for record in records
        for section in ("answer_claims", "important_negatives")
        for group in record["ground_truth"][section]
        for claim_id in group["evidence_claim_ids"]
    }


def apply_amendments(
    repo_root: Path,
    parent: list[dict[str, Any]],
    amendments: dict[str, Any],
    claims: dict[str, dict[str, Any]],
) -> tuple[list[dict[str, Any]], int]:
    """Apply only approved OR-option additions and derive new evidence objects."""

    reviewed = copy.deepcopy(parent)
    by_question = {record.get("id"): record for record in reviewed}
    if list(by_question) != [
        "q031-graph-routing-boundary",
        "q032-incremental-update-maturity",
        "q033-corruption-specific-defenses",
        "q034-nonmonotonic-context-budget",
        "q035-lossless-enough-evidence-organization",
        "q036-evaluation-leakage-and-stage-separation",
        "q037-domain-construction-under-constraints",
        "q038-failure-aware-query-router",
        "q039-baseline-bound-efficiency-claims",
        "q040-answer-source-control",
    ]:
        raise GenerationError("parent hard-ground-truth question order changed")

    new_ids_by_question: dict[str, list[str]] = {question_id: [] for question_id in by_question}
    for addition in amendments["additions"]:
        question_id = addition["question_id"]
        if question_id not in by_question:
            raise GenerationError(f"amendment question does not exist: {question_id}")
        record = by_question[question_id]
        groups = option_groups(record, addition["group_kind"])
        matching = [group for group in groups if group.get("id") == addition["group_id"]]
        if len(matching) != 1:
            raise GenerationError(f"amendment group does not exist exactly once: {addition['group_id']}")
        group = matching[0]
        existing = group.get("evidence_claim_ids")
        if not isinstance(existing, list) or not existing:
            raise GenerationError(f"parent option group is invalid: {addition['group_id']}")
        parent_anchor_papers = {claims[claim_id]["paper_id"] for claim_id in existing}
        required_papers = set(record["ground_truth"]["required_paper_ids"])
        for item in addition["append_claims"]:
            claim_id = item["claim_id"]
            if claim_id in existing:
                raise GenerationError(f"approved addition already exists in parent group: {claim_id}")
            if claim_id not in claims:
                raise GenerationError(f"approved addition does not exist: {claim_id}")
            paper_id = claims[claim_id]["paper_id"]
            if paper_id not in required_papers:
                raise GenerationError(f"approved addition changes required papers: {claim_id}")
            if addition["group_kind"] == "answer_claim" and paper_id not in parent_anchor_papers:
                raise GenerationError(f"atomic alternative changes anchor paper identity: {claim_id}")
            existing.append(claim_id)
            if claim_id not in new_ids_by_question[question_id]:
                new_ids_by_question[question_id].append(claim_id)

    added_objects = 0
    for question_id, record in by_question.items():
        evidence = record.get("authoritative_evidence")
        if not isinstance(evidence, list):
            raise GenerationError(f"parent evidence list is invalid: {question_id}")
        existing_ids = {item.get("claim_id") for item in evidence if isinstance(item, dict)}
        for claim_id in new_ids_by_question[question_id]:
            if claim_id in existing_ids:
                continue
            evidence.append(derive_authoritative_evidence(repo_root, claim_id, claims))
            existing_ids.add(claim_id)
            added_objects += 1

        used = {
            claim_id
            for section in ("answer_claims", "important_negatives")
            for group in record["ground_truth"][section]
            for claim_id in group["evidence_claim_ids"]
        }
        if existing_ids != used:
            raise GenerationError(f"authoritative evidence and option IDs differ: {question_id}")
        if record["ground_truth"]["required_paper_ids"] != parent[
            list(by_question).index(question_id)
        ]["ground_truth"]["required_paper_ids"]:
            raise GenerationError(f"required paper identities changed: {question_id}")
        if record["ground_truth"]["required_source_ids"] != parent[
            list(by_question).index(question_id)
        ]["ground_truth"]["required_source_ids"]:
            raise GenerationError(f"required source identities changed: {question_id}")
    return reviewed, added_objects


def build_hard_ground_truth_manifest(
    repo_root: Path, output_hashes: dict[str, str]
) -> dict[str, Any]:
    """Build a manifest compatible with the classical ground-truth validator."""

    return {
        "schema_version": GROUND_TRUTH_MANIFEST_SCHEMA,
        "generator": GENERATOR_PATH.as_posix(),
        "contracts": {
            "evidence_offsets": "zero-based Unicode code-point offsets over UTF-8 text after CRLF/CR normalization to LF; char_end is exclusive",
            "paper_segment": "from the exact PDF-page heading through the character before the next PDF-page heading, or EOF",
            "claim_record": "one non-empty logical JSONL line without its LF terminator",
            "question_prompt": "question text only; evaluator ground truth is never exposed",
        },
        "inputs": {
            "blueprint": {
                "path": AMENDMENTS_PATH.as_posix(),
                "sha256": digest_text(logical_text(repo_path(repo_root, AMENDMENTS_PATH))),
            },
            "baseline_questions": {
                "path": BASELINE_QUESTIONS_PATH.as_posix(),
                "sha256": digest_text(logical_text(repo_path(repo_root, BASELINE_QUESTIONS_PATH))),
                "count": 30,
            },
            "corpus_inventory": {
                "path": INVENTORY_PATH.as_posix(),
                "sha256": digest_file(repo_path(repo_root, INVENTORY_PATH)),
                "core_file_count": 30,
            },
        },
        "outputs": {
            name: {
                "path": (OUTPUT_ROOT / name).as_posix(),
                "sha256": output_hashes[name],
                "count": 40 if name == "retrieval-questions.jsonl" else 10,
            }
            for name in (
                "hard-ground-truth.jsonl",
                "hard-questions.jsonl",
                "retrieval-questions.jsonl",
            )
        },
    }


def build_frozen_manifest(
    repo_root: Path,
    reviewed: list[dict[str, Any]],
    output_bytes: dict[str, bytes],
    audit_summary: dict[str, int],
) -> dict[str, Any]:
    """Build the closed frozen-answer-benchmark manifest."""

    parent_manifest_path = repo_path(repo_root, PARENT_FROZEN_MANIFEST_PATH)
    parent_manifest = load_json(parent_manifest_path)
    if parent_manifest.get("benchmark_id") != PARENT_BENCHMARK_ID:
        raise GenerationError("parent frozen benchmark ID changed")
    ordered_ids = [record["id"] for record in reviewed]
    retrieval_ids = [
        record["id"]
        for record in load_jsonl(repo_path(repo_root, PARENT_RETRIEVAL_QUESTIONS_PATH))
    ]
    return {
        "schema_version": FROZEN_MANIFEST_SCHEMA,
        "benchmark_id": BENCHMARK_ID,
        "status": "frozen",
        "frozen_on": FROZEN_ON,
        "mutation_policy": "Never edit this reviewed benchmark or its parent in place. A correction requires a new benchmark ID, a new closed amendments document, regenerated outputs, and a new frozen manifest.",
        "parent_frozen_benchmark": {
            "path": PARENT_FROZEN_MANIFEST_PATH.as_posix(),
            "sha256": digest_file(parent_manifest_path),
            "benchmark_id": PARENT_BENCHMARK_ID,
        },
        "amendments": {
            "path": AMENDMENTS_PATH.as_posix(),
            "sha256": digest_file(repo_path(repo_root, AMENDMENTS_PATH)),
        },
        "generator": {
            "path": GENERATOR_PATH.as_posix(),
            "sha256": digest_file(repo_path(repo_root, GENERATOR_PATH)),
        },
        "cohorts": {
            "hard_ground_truth": {
                "path": (OUTPUT_ROOT / "hard-ground-truth.jsonl").as_posix(),
                "sha256": digest_bytes(output_bytes["hard-ground-truth.jsonl"]),
                "count": 10,
                "ordered_ids": ordered_ids,
            },
            "hard_questions": {
                "path": (OUTPUT_ROOT / "hard-questions.jsonl").as_posix(),
                "sha256": digest_bytes(output_bytes["hard-questions.jsonl"]),
                "count": 10,
                "ordered_ids": ordered_ids,
            },
            "retrieval_questions": {
                "path": (OUTPUT_ROOT / "retrieval-questions.jsonl").as_posix(),
                "sha256": digest_bytes(output_bytes["retrieval-questions.jsonl"]),
                "count": 40,
                "ordered_ids": retrieval_ids,
            },
        },
        "invariants": {
            "parent_files_unchanged": "The generator reads the frozen adaptive benchmark only and writes exclusively to the new reviewed-benchmark directory.",
            "question_content_identity": "Hard-question and retrieval-question bytes are identical to the parent cohorts.",
            "qrel_identity": "Every reviewed ground-truth row preserves the parent's required paper and source identities, so independently derived qrels are unchanged.",
            "append_only_option_sets": "Every parent statement and evidence option remains in order; only the independently approved claim IDs are appended to named OR groups.",
            "authoritative_evidence_derivation": "Every newly needed evidence object is rederived from pinned reviewed claim JSONL lines and exact Markdown PDF-page segments with Unicode offsets and SHA-256 hashes.",
            "or_option_semantics": "Each appended ID independently supports its complete atomic or negative group; partial claims are never combined as if an OR option were an AND bundle.",
        },
        "audit_summary": audit_summary,
    }


def build_outputs(repo_root: Path) -> dict[str, bytes]:
    """Build every reviewed-benchmark artifact entirely in memory."""

    inventory, path_to_paper = validate_inventory(repo_root)
    claims = build_claim_index(repo_root, inventory, path_to_paper)
    amendments = load_json(repo_path(repo_root, AMENDMENTS_PATH))
    validate_amendments(amendments)
    parent = load_jsonl(repo_path(repo_root, PARENT_GROUND_TRUTH_PATH))
    if len(parent) != 10 or any(row.get("schema_version") != GROUND_TRUTH_SCHEMA for row in parent):
        raise GenerationError("parent hard ground truth changed")
    parent_hard = repo_path(repo_root, PARENT_HARD_QUESTIONS_PATH).read_bytes()
    parent_retrieval = repo_path(repo_root, PARENT_RETRIEVAL_QUESTIONS_PATH).read_bytes()
    reviewed, added_objects = apply_amendments(repo_root, parent, amendments, claims)
    hard_ground_truth = canonical_jsonl(reviewed)
    output_bytes: dict[str, bytes] = {
        "hard-ground-truth.jsonl": hard_ground_truth,
        "hard-questions.jsonl": parent_hard,
        "retrieval-questions.jsonl": parent_retrieval,
    }
    output_hashes = {name: digest_bytes(data) for name, data in output_bytes.items()}
    hard_manifest = build_hard_ground_truth_manifest(repo_root, output_hashes)
    output_bytes["hard-ground-truth-manifest.json"] = pretty_json(hard_manifest)

    atomic_additions = sum(
        len(ids) for _, kind, _, ids in APPROVED_ADDITIONS if kind == "answer_claim"
    )
    negative_additions = sum(
        len(ids) for _, kind, _, ids in APPROVED_ADDITIONS if kind == "important_negative"
    )
    parent_atomic_links = count_links(parent, "answer_claims")
    parent_negative_links = count_links(parent, "important_negatives")
    reviewed_atomic_links = count_links(reviewed, "answer_claims")
    reviewed_negative_links = count_links(reviewed, "important_negatives")
    audit_summary = {
        "questions": len(reviewed),
        "atomic_answer_claims": sum(len(row["ground_truth"]["answer_claims"]) for row in reviewed),
        "important_negatives": sum(len(row["ground_truth"]["important_negatives"]) for row in reviewed),
        "parent_expected_id_links": parent_atomic_links + parent_negative_links,
        "appended_atomic_option_links": atomic_additions,
        "appended_negative_option_links": negative_additions,
        "reviewed_expected_id_links": reviewed_atomic_links + reviewed_negative_links,
        "parent_unique_expected_claim_ids": len(expected_claim_ids(parent)),
        "added_unique_claim_ids": len(
            {claim_id for _, _, _, ids in APPROVED_ADDITIONS for claim_id in ids}
        ),
        "reviewed_unique_expected_claim_ids": len(expected_claim_ids(reviewed)),
        "parent_authoritative_evidence_objects": sum(
            len(row["authoritative_evidence"]) for row in parent
        ),
        "added_authoritative_evidence_objects": added_objects,
        "reviewed_authoritative_evidence_objects": sum(
            len(row["authoritative_evidence"]) for row in reviewed
        ),
        "rejected_close_alternatives": len(amendments["rejected_close_alternatives"]),
    }
    expected_counts = {
        "questions": 10,
        "atomic_answer_claims": 44,
        "important_negatives": 13,
        "parent_expected_id_links": 72,
        "appended_atomic_option_links": 22,
        "appended_negative_option_links": 19,
        "reviewed_expected_id_links": 113,
        "parent_unique_expected_claim_ids": 42,
        "added_unique_claim_ids": 26,
        "reviewed_unique_expected_claim_ids": 68,
        "parent_authoritative_evidence_objects": 44,
        "added_authoritative_evidence_objects": 27,
        "reviewed_authoritative_evidence_objects": 71,
        "rejected_close_alternatives": 38,
    }
    if audit_summary != expected_counts:
        raise GenerationError(f"reviewed benchmark counts changed: {audit_summary}")
    frozen_manifest = build_frozen_manifest(repo_root, reviewed, output_bytes, audit_summary)
    output_bytes["frozen-answer-benchmark.json"] = pretty_json(frozen_manifest)
    return output_bytes


def atomic_write(path: Path, data: bytes) -> None:
    """Replace one generated file atomically after flushing it."""

    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, path)
    except BaseException:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise


def parse_args(argv: list[str]) -> argparse.Namespace:
    """Parse the closed generator command line."""

    default_root = Path(__file__).resolve().parents[3]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=default_root)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=OUTPUT_ROOT,
        help="write location; manifests always bind the canonical reviewed-benchmark paths",
    )
    parser.add_argument("--check", action="store_true", help="fail if generated files differ")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Generate or drift-check the standalone reviewed answer benchmark."""

    args = parse_args(argv or sys.argv[1:])
    repo_root = args.repo_root.resolve()
    output_dir = args.output_dir if args.output_dir.is_absolute() else repo_root / args.output_dir
    output_dir = output_dir.resolve()
    parent_paths = [
        repo_path(repo_root, PARENT_GROUND_TRUTH_PATH),
        repo_path(repo_root, PARENT_HARD_QUESTIONS_PATH),
        repo_path(repo_root, PARENT_RETRIEVAL_QUESTIONS_PATH),
        repo_path(repo_root, PARENT_FROZEN_MANIFEST_PATH),
    ]
    if output_dir == repo_path(repo_root, PARENT_GROUND_TRUTH_PATH).parent:
        print("error: output directory cannot be the frozen parent benchmark", file=sys.stderr)
        return 2
    before = {path: digest_file(path) for path in parent_paths}
    try:
        outputs = build_outputs(repo_root)
        if args.check:
            stale = [
                name
                for name, expected in outputs.items()
                if not (output_dir / name).is_file()
                or (output_dir / name).read_bytes() != expected
            ]
            if stale:
                raise GenerationError("reviewed benchmark is stale: " + ", ".join(stale))
            print("Reviewed answer benchmark is deterministic and current.")
        else:
            for name, data in outputs.items():
                atomic_write(output_dir / name, data)
            print(
                "Generated the reviewed 40-question/10-answer benchmark with "
                "41 approved OR-option links and 27 independently derived evidence objects."
            )
        after = {path: digest_file(path) for path in parent_paths}
        if after != before:
            raise GenerationError("frozen parent benchmark changed during generation")
        return 0
    except (GenerationError, OSError, UnicodeDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
