#!/usr/bin/env python3
"""Deterministically generate the definitive ensemble Skill Arena artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Any, Mapping, Sequence

import yaml


REPO_ROOT = Path(__file__).resolve().parents[3]
GROUND_TRUTH_RELATIVE = Path(
    "evaluations/semantic-okf-ensemble/reviewed-benchmark/hard-ground-truth.jsonl"
)
GROUND_TRUTH_MANIFEST_RELATIVE = Path(
    "evaluations/semantic-okf-ensemble/reviewed-benchmark/hard-ground-truth-manifest.json"
)
FROZEN_BENCHMARK_RELATIVE = Path(
    "evaluations/semantic-okf-ensemble/reviewed-benchmark/frozen-answer-benchmark.json"
)
PINNED_BUNDLE_RELATIVE = Path(
    "evaluations/semantic-okf-ensemble/results/runs/"
    "20260715-ensemble-final-03/workspace-a/knowledge"
)
OUTPUT_DIRECTORY_RELATIVE = Path("evaluations/semantic-okf-ensemble/skill-arena")

# The reviewed benchmark is frozen independently of the older classical and
# adaptive copies. Update this only after a new evidence audit and benchmark
# generation; ordinary config regeneration must fail on ground-truth drift.
EXPECTED_GROUND_TRUTH_SHA256 = "c656fc575b0c7e06cd386093d975cd74ef9c9aead743312e3aadec1cbdc08451"
EXPECTED_GROUND_TRUTH_MANIFEST_SHA256 = "450a25cd9fed0009bf2145067f15e6c7f3f58249ed7ce75afaf9897ccc185003"
EXPECTED_FROZEN_BENCHMARK_SHA256 = "257997cc2da3d9afae596ac8b46551a1b1fa73480f15861a25f262bb85a91f62"
EXPECTED_ENSEMBLE_INDEX_SHA256 = "9ce8bac88df8621fd870d718d1166e706516f4c4d56497eecc080d454453e939"
EXPECTED_RECORDS_SHA256 = "df06f8ed7fd0ca4b2b8b5761c637a79d525595a2c180aeaf6885555e266754dc"

GROUND_TRUTH_SCHEMA = "semantic-okf-hard-ground-truth/1.0"
EXPECTED_QUESTION_IDS = [
    f"q{number:03d}-{suffix}"
    for number, suffix in (
        (31, "graph-routing-boundary"),
        (32, "incremental-update-maturity"),
        (33, "corruption-specific-defenses"),
        (34, "nonmonotonic-context-budget"),
        (35, "lossless-enough-evidence-organization"),
        (36, "evaluation-leakage-and-stage-separation"),
        (37, "domain-construction-under-constraints"),
        (38, "failure-aware-query-router"),
        (39, "baseline-bound-efficiency-claims"),
        (40, "answer-source-control"),
    )
]
CASE_METADATA = {
    "q031-graph-routing-boundary": ("boundary-recovery", "retrieval-routing"),
    "q032-incremental-update-maturity": ("generalization", "knowledge-lifecycle"),
    "q033-corruption-specific-defenses": ("boundary-recovery", "robustness-defense"),
    "q034-nonmonotonic-context-budget": ("generalization", "context-budgeting"),
    "q035-lossless-enough-evidence-organization": (
        "naturalistic-forward",
        "evidence-organization",
    ),
    "q036-evaluation-leakage-and-stage-separation": (
        "naturalistic-forward",
        "evaluation-design",
    ),
    "q037-domain-construction-under-constraints": (
        "generalization",
        "graph-construction",
    ),
    "q038-failure-aware-query-router": (
        "boundary-recovery",
        "retrieval-routing",
    ),
    "q039-baseline-bound-efficiency-claims": (
        "naturalistic-forward",
        "efficiency-comparison",
    ),
    "q040-answer-source-control": (
        "boundary-recovery",
        "answer-grounding-policy",
    ),
}

PROFILE_IDS = [
    "knowledge-only-control",
    "adaptive-consult-control",
    "ensemble-consult-treatment",
]
MCP_TOOLS = [
    "semantic_okf_bootstrap_skill",
    "semantic_okf_inspect",
    "semantic_okf_coverage_brief",
    "semantic_okf_prepare_answer",
    "semantic_okf_confirm_answer",
]
MCP_ENVIRONMENT = [
    "SKILL_ARENA_ALLOWED_SKILLS",
    "CODEX_HOME",
    "SEMANTIC_OKF_BUNDLE",
    "SEMANTIC_OKF_PYTHON",
    "SEMANTIC_OKF_HF_HUB_CACHE",
    "HF_HUB_OFFLINE",
    "TRANSFORMERS_OFFLINE",
    "PYTHONDONTWRITEBYTECODE",
]
PUBLICATION_COMMAND_PATH = r"publication-runtime\run_codex.cmd"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")

QUESTION_KEYS = {
    "schema_version",
    "id",
    "corpus_inventory",
    "authoritative_evidence",
    "ground_truth",
    "question",
}
EVIDENCE_KEYS = {
    "claim_id",
    "paper_id",
    "claim_kind",
    "review_state",
    "interpretation",
    "interpretation_sha256",
    "claim_source",
    "paper_evidence",
}
CLAIM_SOURCE_KEYS = {
    "path",
    "line_number",
    "char_start",
    "char_end",
    "record_sha256",
}
PAPER_EVIDENCE_KEYS = {
    "path",
    "locator",
    "char_start",
    "char_end",
    "text_length",
    "text_sha256",
}
GROUND_TRUTH_KEYS = {
    "answer_claims",
    "required_paper_ids",
    "required_source_ids",
    "derivation",
    "acceptable_variants",
    "important_negatives",
}
ANSWER_OPTION_KEYS = {"id", "statement", "evidence_claim_ids"}
DERIVATION_KEYS = {"operation", "inputs", "conclusion"}


class ConfigGenerationError(RuntimeError):
    """Describe a fail-closed config generation violation."""


class LiteralString(str):
    """A YAML scalar rendered as a literal block."""


class Dumper(yaml.SafeDumper):
    """Stable YAML emitter compatible with Skill Arena's static parser."""

    def increase_indent(self, flow: bool = False, indentless: bool = False) -> Any:
        return super().increase_indent(flow, False)


def _represent_literal(dumper: Dumper, value: LiteralString) -> yaml.ScalarNode:
    return dumper.represent_scalar("tag:yaml.org,2002:str", value, style="|")


Dumper.add_representer(LiteralString, _represent_literal)


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ConfigGenerationError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _reject_constant(value: str) -> Any:
    raise ConfigGenerationError(f"non-finite JSON constant is forbidden: {value}")


def _strict_json(text: str, label: str) -> Any:
    try:
        return json.loads(
            text,
            object_pairs_hook=_strict_object,
            parse_constant=_reject_constant,
        )
    except (json.JSONDecodeError, ConfigGenerationError) as exc:
        raise ConfigGenerationError(f"{label} is not strict JSON: {exc}") from exc


def _exact_keys(value: Any, expected: set[str], label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ConfigGenerationError(f"{label} must be an object")
    actual = set(value)
    if actual != expected:
        raise ConfigGenerationError(
            f"{label} uses a closed schema; missing={sorted(expected - actual)}, "
            f"unknown={sorted(actual - expected)}"
        )
    return value


def _regular_file(path: Path, label: str) -> Path:
    if path.is_symlink():
        raise ConfigGenerationError(f"{label} must be a regular non-link file")
    try:
        resolved = path.resolve(strict=True)
    except OSError as exc:
        raise ConfigGenerationError(f"cannot resolve {label}: {exc}") from exc
    if not resolved.is_file():
        raise ConfigGenerationError(f"{label} must be a regular non-link file")
    return resolved


def _strict_json_file(path: Path, label: str) -> dict[str, Any]:
    resolved = _regular_file(path, label)
    try:
        text = resolved.read_bytes().decode("utf-8")
    except UnicodeError as exc:
        raise ConfigGenerationError(f"{label} is not UTF-8") from exc
    value = _strict_json(text, label)
    if not isinstance(value, dict):
        raise ConfigGenerationError(f"{label} must be an object")
    return value


def _portable_relative(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value or "\\" in value:
        raise ConfigGenerationError(f"{label} must be a portable relative path")
    logical = Path(value)
    if logical.is_absolute() or any(part in {"", ".", ".."} for part in logical.parts):
        raise ConfigGenerationError(f"{label} must remain relative")
    return value


def _nonempty_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ConfigGenerationError(f"{label} must be a nonempty string")
    return value


def _string_list(value: Any, label: str, *, nonempty: bool = True) -> list[str]:
    if (
        not isinstance(value, list)
        or (nonempty and not value)
        or not all(isinstance(item, str) and item for item in value)
        or len(value) != len(set(value))
    ):
        raise ConfigGenerationError(f"{label} must be a unique string list")
    return list(value)


def _load_reviewed_ground_truth(repo_root: Path) -> list[dict[str, Any]]:
    _validate_reviewed_freeze(repo_root)
    path = _regular_file(repo_root / GROUND_TRUTH_RELATIVE, "reviewed ground truth")
    observed_sha = _sha256_file(path)
    if observed_sha != EXPECTED_GROUND_TRUTH_SHA256:
        raise ConfigGenerationError(
            "reviewed ground truth SHA-256 drifted; a new evidence audit is required"
        )
    rows: list[dict[str, Any]] = []
    try:
        lines = path.read_bytes().decode("utf-8").splitlines()
    except UnicodeError as exc:
        raise ConfigGenerationError("reviewed ground truth is not UTF-8") from exc
    for line_number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        value = _strict_json(line, f"reviewed ground truth line {line_number}")
        if not isinstance(value, dict):
            raise ConfigGenerationError(
                f"reviewed ground truth line {line_number} must be an object"
            )
        rows.append(value)
    _validate_ground_truth(rows)
    return rows


def _validate_reviewed_freeze(repo_root: Path) -> None:
    manifest_path = _regular_file(
        repo_root / GROUND_TRUTH_MANIFEST_RELATIVE,
        "reviewed ground-truth manifest",
    )
    frozen_path = _regular_file(
        repo_root / FROZEN_BENCHMARK_RELATIVE,
        "frozen answer benchmark",
    )
    if _sha256_file(manifest_path) != EXPECTED_GROUND_TRUTH_MANIFEST_SHA256:
        raise ConfigGenerationError("reviewed ground-truth manifest SHA-256 drifted")
    if _sha256_file(frozen_path) != EXPECTED_FROZEN_BENCHMARK_SHA256:
        raise ConfigGenerationError("frozen answer benchmark SHA-256 drifted")
    manifest = _strict_json_file(manifest_path, "reviewed ground-truth manifest")
    _exact_keys(
        manifest,
        {"contracts", "generator", "inputs", "outputs", "schema_version"},
        "reviewed ground-truth manifest",
    )
    if manifest["schema_version"] != "semantic-okf-hard-ground-truth-manifest/1.0":
        raise ConfigGenerationError("reviewed ground-truth manifest schema differs")
    outputs = _exact_keys(
        manifest["outputs"],
        {"hard-ground-truth.jsonl", "hard-questions.jsonl", "retrieval-questions.jsonl"},
        "reviewed ground-truth manifest outputs",
    )
    ground_truth = _exact_keys(
        outputs["hard-ground-truth.jsonl"],
        {"count", "path", "sha256"},
        "reviewed ground-truth manifest binding",
    )
    if ground_truth != {
        "count": 10,
        "path": GROUND_TRUTH_RELATIVE.as_posix(),
        "sha256": EXPECTED_GROUND_TRUTH_SHA256,
    }:
        raise ConfigGenerationError("reviewed ground-truth manifest binding differs")

    frozen = _strict_json_file(frozen_path, "frozen answer benchmark")
    _exact_keys(
        frozen,
        {
            "amendments",
            "audit_summary",
            "benchmark_id",
            "cohorts",
            "frozen_on",
            "generator",
            "invariants",
            "mutation_policy",
            "parent_frozen_benchmark",
            "schema_version",
            "status",
        },
        "frozen answer benchmark",
    )
    if (
        frozen["schema_version"] != "semantic-okf-frozen-answer-benchmark/1.0"
        or frozen["status"] != "frozen"
        or frozen["benchmark_id"]
        != "semantic-okf-ensemble-reviewed-answer-40-plus-hard10-v1"
    ):
        raise ConfigGenerationError("frozen answer benchmark identity differs")
    cohorts = _exact_keys(
        frozen["cohorts"],
        {"hard_ground_truth", "hard_questions", "retrieval_questions"},
        "frozen answer benchmark cohorts",
    )
    frozen_ground_truth = _exact_keys(
        cohorts["hard_ground_truth"],
        {"count", "ordered_ids", "path", "sha256"},
        "frozen hard-ground-truth cohort",
    )
    if frozen_ground_truth != {
        "count": 10,
        "ordered_ids": EXPECTED_QUESTION_IDS,
        "path": GROUND_TRUTH_RELATIVE.as_posix(),
        "sha256": EXPECTED_GROUND_TRUTH_SHA256,
    }:
        raise ConfigGenerationError("frozen hard-ground-truth cohort differs")


def _validate_ground_truth(rows: Sequence[Mapping[str, Any]]) -> None:
    if len(rows) != 10 or [row.get("id") for row in rows] != EXPECTED_QUESTION_IDS:
        raise ConfigGenerationError(
            "reviewed ground truth must contain q031 through q040 in frozen order"
        )
    for question in rows:
        question_id = str(question.get("id"))
        _exact_keys(question, QUESTION_KEYS, f"{question_id} record")
        if question["schema_version"] != GROUND_TRUTH_SCHEMA:
            raise ConfigGenerationError(f"{question_id} schema version differs")
        _nonempty_string(question["question"], f"{question_id} question")
        inventory = _exact_keys(
            question["corpus_inventory"], {"path", "sha256"}, f"{question_id} inventory"
        )
        _portable_relative(inventory["path"], f"{question_id} inventory path")
        if not isinstance(inventory["sha256"], str) or not SHA256_RE.fullmatch(
            inventory["sha256"]
        ):
            raise ConfigGenerationError(f"{question_id} inventory hash is invalid")

        evidence = question["authoritative_evidence"]
        if not isinstance(evidence, list) or len(evidence) < 3:
            raise ConfigGenerationError(f"{question_id} lacks authoritative evidence")
        claim_ids: list[str] = []
        paper_ids: set[str] = set()
        for position, item in enumerate(evidence):
            item = _exact_keys(item, EVIDENCE_KEYS, f"{question_id} evidence {position}")
            claim_id = _nonempty_string(
                item["claim_id"], f"{question_id} evidence {position} claim"
            )
            paper_id = _nonempty_string(
                item["paper_id"], f"{question_id} evidence {position} paper"
            )
            if item["review_state"] != "reviewed":
                raise ConfigGenerationError(f"{claim_id} is not reviewed")
            _nonempty_string(item["claim_kind"], f"{claim_id} claim kind")
            interpretation = _nonempty_string(
                item["interpretation"], f"{claim_id} interpretation"
            )
            if item["interpretation_sha256"] != _sha256_bytes(
                interpretation.encode("utf-8")
            ):
                raise ConfigGenerationError(f"{claim_id} interpretation hash differs")
            source = _exact_keys(
                item["claim_source"], CLAIM_SOURCE_KEYS, f"{claim_id} claim source"
            )
            _portable_relative(source["path"], f"{claim_id} claim source path")
            if source["path"] != (
                f"evaluations/graphrag-cross-paper/sources/claims/{paper_id}.jsonl"
            ):
                raise ConfigGenerationError(f"{claim_id} claim source identity differs")
            if not isinstance(source["record_sha256"], str) or not SHA256_RE.fullmatch(
                source["record_sha256"]
            ):
                raise ConfigGenerationError(f"{claim_id} record hash is invalid")
            for key in ("line_number", "char_start", "char_end"):
                value = source[key]
                if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                    raise ConfigGenerationError(f"{claim_id} source offset is invalid")
            pages = item["paper_evidence"]
            if not isinstance(pages, list) or not pages:
                raise ConfigGenerationError(f"{claim_id} lacks paper evidence")
            page_keys: set[tuple[str, str]] = set()
            for page_position, page in enumerate(pages):
                page = _exact_keys(
                    page,
                    PAPER_EVIDENCE_KEYS,
                    f"{claim_id} paper evidence {page_position}",
                )
                page_path = _portable_relative(
                    page["path"], f"{claim_id} paper evidence path"
                )
                locator = _nonempty_string(
                    page["locator"], f"{claim_id} paper evidence locator"
                )
                if page_path != (
                    f"evaluations/graphrag-cross-paper/sources/markdown/{paper_id}.md"
                ) or not re.fullmatch(r"PDF-page-[1-9][0-9]*", locator):
                    raise ConfigGenerationError(f"{claim_id} paper locator differs")
                if (page_path, locator) in page_keys:
                    raise ConfigGenerationError(f"{claim_id} repeats a paper locator")
                page_keys.add((page_path, locator))
                if not isinstance(page["text_sha256"], str) or not SHA256_RE.fullmatch(
                    page["text_sha256"]
                ):
                    raise ConfigGenerationError(f"{claim_id} paper hash is invalid")
                for key in ("char_start", "char_end", "text_length"):
                    value = page[key]
                    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                        raise ConfigGenerationError(f"{claim_id} paper offset is invalid")
            claim_ids.append(claim_id)
            paper_ids.add(paper_id)
        if len(claim_ids) != len(set(claim_ids)) or len(paper_ids) < 3:
            raise ConfigGenerationError(f"{question_id} evidence identities are invalid")

        truth = _exact_keys(
            question["ground_truth"], GROUND_TRUTH_KEYS, f"{question_id} ground truth"
        )
        required_papers = _string_list(
            truth["required_paper_ids"], f"{question_id} required papers"
        )
        if required_papers != sorted(paper_ids):
            raise ConfigGenerationError(f"{question_id} required papers differ")
        required_sources = _string_list(
            truth["required_source_ids"], f"{question_id} required sources"
        )
        expected_sources = sorted(
            [f"claims-{paper.replace('.', '-')}" for paper in required_papers]
            + [f"paper-{paper.replace('.', '-')}" for paper in required_papers]
        )
        if required_sources != expected_sources:
            raise ConfigGenerationError(f"{question_id} required sources differ")
        _string_list(truth["acceptable_variants"], f"{question_id} variants")
        used_claims: set[str] = set()
        answer_ids: set[str] = set()
        for kind in ("answer_claims", "important_negatives"):
            options = truth[kind]
            if not isinstance(options, list) or not options:
                raise ConfigGenerationError(f"{question_id} {kind} is empty")
            for option_position, option in enumerate(options):
                option = _exact_keys(
                    option,
                    ANSWER_OPTION_KEYS,
                    f"{question_id} {kind} {option_position}",
                )
                option_id = _nonempty_string(
                    option["id"], f"{question_id} {kind} id"
                )
                _nonempty_string(option["statement"], f"{option_id} statement")
                option_claims = _string_list(
                    option["evidence_claim_ids"], f"{option_id} evidence options"
                )
                if not set(option_claims) <= set(claim_ids):
                    raise ConfigGenerationError(f"{option_id} uses unbound evidence")
                used_claims.update(option_claims)
                if kind == "answer_claims":
                    if option_id in answer_ids:
                        raise ConfigGenerationError(f"{question_id} repeats answer ID")
                    answer_ids.add(option_id)
        if used_claims != set(claim_ids):
            raise ConfigGenerationError(f"{question_id} has unused reviewed evidence")
        derivation = truth["derivation"]
        if not isinstance(derivation, list) or len(derivation) < 2:
            raise ConfigGenerationError(f"{question_id} lacks explicit derivation")
        for position, step in enumerate(derivation):
            step = _exact_keys(
                step, DERIVATION_KEYS, f"{question_id} derivation {position}"
            )
            if step["operation"] not in {"join", "contrast", "conditional", "exclusion"}:
                raise ConfigGenerationError(f"{question_id} derivation operation differs")
            if not set(_string_list(step["inputs"], f"{question_id} derivation inputs")) <= answer_ids:
                raise ConfigGenerationError(f"{question_id} derivation inputs differ")
            _nonempty_string(step["conclusion"], f"{question_id} derivation conclusion")


def _load_claim_records(repo_root: Path) -> tuple[Path, dict[str, dict[str, Any]]]:
    bundle = repo_root / PINNED_BUNDLE_RELATIVE
    index_path = _regular_file(bundle / "ensemble/index.json", "pinned ensemble index")
    records_path = _regular_file(bundle / "semantic/records.jsonl", "pinned Semantic records")
    if _sha256_file(index_path) != EXPECTED_ENSEMBLE_INDEX_SHA256:
        raise ConfigGenerationError("pinned final-03 ensemble index drifted")
    if _sha256_file(records_path) != EXPECTED_RECORDS_SHA256:
        raise ConfigGenerationError("pinned final-03 Semantic records drifted")
    try:
        lines = records_path.read_bytes().decode("utf-8").splitlines()
    except UnicodeError as exc:
        raise ConfigGenerationError("pinned Semantic records are not UTF-8") from exc
    claims: dict[str, dict[str, Any]] = {}
    for line_number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        record = _strict_json(line, f"Semantic record line {line_number}")
        if not isinstance(record, dict):
            raise ConfigGenerationError(f"Semantic record line {line_number} is not an object")
        record_id = record.get("record_id")
        if not isinstance(record_id, str) or not record_id.startswith("claim-"):
            continue
        if record_id in claims:
            raise ConfigGenerationError(f"duplicate Semantic claim record: {record_id}")
        claims[record_id] = record
    return bundle, claims


def _bundle_member(bundle: Path, relative: Any, label: str) -> str:
    value = _portable_relative(relative, label)
    unresolved = bundle / value
    if unresolved.is_symlink():
        raise ConfigGenerationError(f"{label} must identify a regular bundle file")
    candidate = unresolved.resolve(strict=True)
    try:
        candidate.relative_to(bundle.resolve(strict=True))
    except ValueError as exc:
        raise ConfigGenerationError(f"{label} escapes the pinned bundle") from exc
    if not candidate.is_file():
        raise ConfigGenerationError(f"{label} must identify a regular bundle file")
    return value


def _all_claim_bindings(
    bundle: Path,
    records: Mapping[str, Mapping[str, Any]],
) -> dict[str, dict[str, Any]]:
    """Bind every reviewed Semantic claim to its exact published evidence identity."""

    allowed: dict[str, dict[str, Any]] = {}
    for claim_id in sorted(records):
        record = records[claim_id]
        if record.get("record_id") != claim_id:
            raise ConfigGenerationError(f"pinned bundle claim identity differs for {claim_id}")
        attributes = record.get("attributes")
        if not isinstance(attributes, Mapping) or attributes.get("review_state") != "reviewed":
            raise ConfigGenerationError(f"pinned bundle claim is not reviewed: {claim_id}")
        concept_path = _bundle_member(
            bundle, record.get("concept_path"), f"{claim_id} concept path"
        )
        source_path = _portable_relative(
            record.get("source_path"), f"{claim_id} source path"
        )
        match = re.fullmatch(
            r"sources/claims/(\d{4}\.\d{5}v\d+)\.jsonl", source_path
        )
        if match is None:
            raise ConfigGenerationError(f"pinned bundle source differs for {claim_id}")
        paper_id = match.group(1)
        expected_claim_prefix = f"claim-{paper_id.replace('.', '-')}-"
        if not claim_id.startswith(expected_claim_prefix):
            raise ConfigGenerationError(f"pinned bundle paper identity differs for {claim_id}")
        locator_value = attributes.get("evidence_locator")
        if not isinstance(locator_value, str) or not locator_value:
            raise ConfigGenerationError(f"pinned bundle locator is absent for {claim_id}")
        locators = sorted(
            part.rsplit("#", 1)[-1] for part in locator_value.split(";") if "#" in part
        )
        if (
            not locators
            or len(locators) != len(set(locators))
            or any(re.fullmatch(r"PDF-page-[1-9][0-9]*", value) is None for value in locators)
        ):
            raise ConfigGenerationError(f"pinned bundle locators differ for {claim_id}")
        allowed[claim_id] = {
            "concept_path": concept_path,
            "paper_id": paper_id,
            "source_path": source_path,
            "locators": locators,
        }
    if set(allowed) != set(records):
        raise ConfigGenerationError("published claim binding set is incomplete")
    return allowed


def _claim_contract(
    question: Mapping[str, Any],
    bundle: Path,
    records: Mapping[str, Mapping[str, Any]],
    all_allowed: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    reviewed_allowed: dict[str, dict[str, Any]] = {}
    for item in question["authoritative_evidence"]:
        claim_id = item["claim_id"]
        record = records.get(claim_id)
        if not isinstance(record, Mapping):
            raise ConfigGenerationError(f"pinned bundle has no record for {claim_id}")
        if record.get("record_id") != claim_id:
            raise ConfigGenerationError(f"pinned bundle claim identity differs for {claim_id}")
        concept_path = _bundle_member(
            bundle, record.get("concept_path"), f"{claim_id} concept path"
        )
        source_path = _portable_relative(
            record.get("source_path"), f"{claim_id} source path"
        )
        expected_source = f"sources/claims/{item['paper_id']}.jsonl"
        if source_path != expected_source:
            raise ConfigGenerationError(f"pinned bundle source differs for {claim_id}")
        attributes = record.get("attributes")
        locator_value = attributes.get("evidence_locator") if isinstance(attributes, Mapping) else None
        if not isinstance(locator_value, str) or not locator_value:
            raise ConfigGenerationError(f"pinned bundle locator is absent for {claim_id}")
        locators = sorted(
            part.rsplit("#", 1)[-1] for part in locator_value.split(";") if "#" in part
        )
        expected_locators = sorted(
            page["locator"] for page in item["paper_evidence"]
        )
        if locators != expected_locators or len(locators) != len(set(locators)):
            raise ConfigGenerationError(f"pinned bundle locators differ for {claim_id}")
        reviewed_allowed[claim_id] = {
            "concept_path": concept_path,
            "paper_id": item["paper_id"],
            "source_path": source_path,
            "locators": locators,
        }
        if reviewed_allowed[claim_id] != all_allowed.get(claim_id):
            raise ConfigGenerationError(
                f"reviewed ground-truth binding differs from published claim: {claim_id}"
            )
    truth = question["ground_truth"]
    return {
        "allowed": {
            key: dict(all_allowed[key])
            for key in sorted(all_allowed)
        },
        "atom_sets": [
            sorted(set(item["evidence_claim_ids"]))
            for item in truth["answer_claims"]
        ],
        "negative_sets": [
            sorted(set(item["evidence_claim_ids"]))
            for item in truth["important_negatives"]
        ],
        "required_papers": list(truth["required_paper_ids"]),
    }


def _prompt(question: Mapping[str, Any]) -> str:
    question_id = question["id"]
    return (
        "Answer the following research-synthesis question using only the published Semantic OKF "
        "snapshot available at `knowledge/`. Do not use the web, model memory, or guesses. If the "
        "snapshot cannot support an answer, return `answer: null` and an empty `evidence` array.\n"
        f"Question: {question['question']}\n"
        "Return JSON only with top-level keys `question_id`, `answer`, and `evidence`, in that order. "
        f"Set `question_id` to `{question_id}`. A non-null `answer` must contain `summary`, `claims`, "
        "`paper_ids`, and `citations`, in that order. Write a comparative 180-320 word `summary`. "
        "Each `claims` item must have exactly `statement` and `supporting_claim_ids`; use the exact "
        "authoritative claim record IDs that support the statement. Use sorted, unique versioned arXiv "
        "IDs in `paper_ids`. Sort `citations` by `paper_id`; each item must have exactly `paper_id` and "
        "sorted unique integer PDF `pages`. Sort `evidence` by `claim_id`; each item must have exactly "
        "`claim_id`, `concept_path`, `paper_id`, `source_path`, and sorted unique page `locators`. Every "
        "path must exist in the snapshot, and every conclusion must be traceable to the listed evidence."
    )


def _response_contract_js(question_id: str) -> str:
    expected_id = json.dumps(question_id)
    return f"""try {{
  const actual = JSON.parse(output.trim());
  if (JSON.stringify(Object.keys(actual)) !== JSON.stringify(['question_id','answer','evidence'])) return false;
  if (actual.question_id !== {expected_id} || !Array.isArray(actual.evidence)) return false;
  if (actual.answer === null) return actual.evidence.length === 0;
  if (JSON.stringify(Object.keys(actual.answer)) !== JSON.stringify(['summary','claims','paper_ids','citations'])) return false;
  const words = typeof actual.answer.summary === 'string' ? actual.answer.summary.trim().split(/\\s+/).filter(Boolean).length : 0;
  if (words < 180 || words > 320 || !Array.isArray(actual.answer.claims) || actual.answer.claims.length === 0) return false;
  if (!Array.isArray(actual.answer.paper_ids) || !Array.isArray(actual.answer.citations) || actual.evidence.length === 0) return false;
  const sortedUnique = (items) => new Set(items).size === items.length && JSON.stringify([...items].sort()) === JSON.stringify(items);
  if (!actual.answer.paper_ids.every((item) => typeof item === 'string') || !sortedUnique(actual.answer.paper_ids)) return false;
  for (const claim of actual.answer.claims) {{
    if (JSON.stringify(Object.keys(claim)) !== JSON.stringify(['statement','supporting_claim_ids'])) return false;
    if (typeof claim.statement !== 'string' || !claim.statement.trim() || !Array.isArray(claim.supporting_claim_ids) || !sortedUnique(claim.supporting_claim_ids)) return false;
  }}
  const cited = actual.answer.citations.map((item) => item.paper_id);
  if (!sortedUnique(cited)) return false;
  for (const item of actual.answer.citations) {{
    if (JSON.stringify(Object.keys(item)) !== JSON.stringify(['paper_id','pages'])) return false;
    if (!actual.answer.paper_ids.includes(item.paper_id) || !Array.isArray(item.pages) || item.pages.length === 0) return false;
    if (new Set(item.pages).size !== item.pages.length || JSON.stringify([...item.pages].sort((a,b) => a-b)) !== JSON.stringify(item.pages)) return false;
    if (!item.pages.every((page) => Number.isInteger(page) && page > 0)) return false;
  }}
  const evidenceIds = actual.evidence.map((item) => item.claim_id);
  if (!sortedUnique(evidenceIds)) return false;
  return actual.evidence.every((item) =>
    JSON.stringify(Object.keys(item)) === JSON.stringify(['claim_id','concept_path','paper_id','source_path','locators']) &&
    typeof item.claim_id === 'string' && typeof item.concept_path === 'string' && typeof item.paper_id === 'string' &&
    typeof item.source_path === 'string' && Array.isArray(item.locators) && sortedUnique(item.locators)
  );
}} catch {{ return false; }}"""


def _evidence_validity_js(contract: Mapping[str, Any]) -> str:
    allowed = json.dumps(contract["allowed"], sort_keys=True, separators=(",", ":"))
    return f"""try {{
  const actual = JSON.parse(output.trim());
  if (actual.answer === null) return false;
  const allowed = {allowed};
  for (const item of actual.evidence) {{
    const expected = allowed[item.claim_id];
    if (!expected) return false;
    if (item.concept_path !== expected.concept_path || item.paper_id !== expected.paper_id || item.source_path !== expected.source_path) return false;
    if (!item.locators.every((locator) => expected.locators.includes(locator))) return false;
  }}
  const citedPages = new Map(actual.answer.citations.map((item) => [item.paper_id, new Set(item.pages.map((page) => `PDF-page-${{page}}`))]));
  return actual.evidence.every((item) => item.locators.every((locator) => citedPages.get(item.paper_id)?.has(locator)));
}} catch {{ return false; }}"""


def _coverage_js(contract: Mapping[str, Any], *, negative: bool) -> str:
    option_sets = contract["negative_sets" if negative else "atom_sets"]
    expected_sets = json.dumps(option_sets, separators=(",", ":"))
    required_papers = json.dumps(contract["required_papers"], separators=(",", ":"))
    paper_check = "" if negative else (
        f"const requiredPapers = {required_papers};\n"
        "  if (!requiredPapers.every((paper) => actual.answer.paper_ids.includes(paper))) return false;\n  "
    )
    return f"""try {{
  const actual = JSON.parse(output.trim());
  if (actual.answer === null) return false;
  {paper_check}const used = new Set(actual.answer.claims.flatMap((item) => item.supporting_claim_ids));
  const evidence = new Set(actual.evidence.map((item) => item.claim_id));
  const expectedSets = {expected_sets};
  return expectedSets.every((options) => options.some((claimId) => used.has(claimId) && evidence.has(claimId)));
}} catch {{ return false; }}"""


def _prompt_entry(
    question: Mapping[str, Any], contract: Mapping[str, Any]
) -> dict[str, Any]:
    case_kind, task_family = CASE_METADATA[question["id"]]
    return {
        "id": question["id"],
        "description": f"{case_kind}: {task_family}",
        "prompt": LiteralString(_prompt(question)),
        "evaluation": {
            "assertions": [
                {
                    "type": "javascript",
                    "metric": "response-contract",
                    "value": LiteralString(_response_contract_js(question["id"])),
                },
                {
                    "type": "javascript",
                    "metric": "evidence-validity",
                    "value": LiteralString(_evidence_validity_js(contract)),
                },
                {
                    "type": "javascript",
                    "metric": "atomic-answer-completeness",
                    "value": LiteralString(_coverage_js(contract, negative=False)),
                },
                {
                    "type": "javascript",
                    "metric": "important-negative-coverage",
                    "value": LiteralString(_coverage_js(contract, negative=True)),
                },
            ]
        },
    }


def _profiles() -> list[dict[str, Any]]:
    return [
        {
            "id": "knowledge-only-control",
            "description": "Isolated control with the pinned ensemble bundle and no declared consult skill.",
            "isolation": {"inheritSystem": False},
            "capabilities": {},
            "output": {
                "tags": ["control", "knowledge-only", "knowledge-on"],
                "labels": {
                    "capability": "none",
                    "bundle_kind": "ensemble-derived",
                    "causal_role": "passive-control",
                },
            },
        },
        {
            "id": "adaptive-consult-control",
            "description": "Isolated active control using the standalone adaptive consultation skill over the pinned ensemble bundle.",
            "isolation": {"inheritSystem": False},
            "capabilities": {
                "skills": [
                    {
                        "source": {
                            "type": "local-path",
                            "path": "skills/consult-semantic-okf-adaptive",
                            "skillId": "consult-semantic-okf-adaptive",
                        },
                        "install": {"strategy": "workspace-overlay"},
                    }
                ]
            },
            "output": {
                "tags": ["control", "adaptive", "knowledge-on"],
                "labels": {
                    "capability": "consult-semantic-okf-adaptive",
                    "bundle_kind": "ensemble-derived",
                    "causal_role": "active-control",
                },
            },
        },
        {
            "id": "ensemble-consult-treatment",
            "description": "Isolated treatment using the standalone definitive ensemble consultation skill over the same pinned bundle.",
            "isolation": {"inheritSystem": False},
            "capabilities": {
                "skills": [
                    {
                        "source": {
                            "type": "local-path",
                            "path": "skills/consult-semantic-okf-ensemble",
                            "skillId": "consult-semantic-okf-ensemble",
                        },
                        "install": {"strategy": "workspace-overlay"},
                    }
                ]
            },
            "output": {
                "tags": ["treatment", "ensemble", "knowledge-on"],
                "labels": {
                    "capability": "consult-semantic-okf-ensemble",
                    "bundle_kind": "ensemble-derived",
                    "causal_role": "treatment",
                },
            },
        },
    ]


def _config(
    questions: Sequence[Mapping[str, Any]], contracts: Sequence[Mapping[str, Any]]
) -> dict[str, Any]:
    return {
        "schemaVersion": 1,
        "benchmark": {
            "id": "semantic-okf-ensemble-hard10-three-arm",
            "description": "Three-arm isolated comparison of knowledge-only, adaptive consultation, and definitive ensemble consultation over the same pinned ensemble bundle and frozen generation-2 hard questions.",
            "tags": [
                "compare",
                "semantic-okf",
                "hard-questions",
                "isolated",
                "three-arm",
                "ensemble",
            ],
        },
        "task": {
            "prompts": [
                _prompt_entry(question, contract)
                for question, contract in zip(questions, contracts, strict=True)
            ]
        },
        "workspace": {
            "sources": [
                {
                    "id": "semantic-okf-ensemble-final-bundle",
                    "type": "local-path",
                    "path": PINNED_BUNDLE_RELATIVE.as_posix(),
                    "target": "/knowledge",
                },
                {
                    "id": "semantic-okf-profile-gated-mcp-runtime",
                    "type": "local-path",
                    "path": "skills/consult-semantic-okf-ensemble/mcp-runtime",
                    "target": "/mcp-runtime",
                },
                {
                    "id": "semantic-okf-confirmed-output-publication-runtime",
                    "type": "local-path",
                    "path": "skills/consult-semantic-okf-ensemble/publication-runtime",
                    "target": "/publication-runtime",
                },
            ],
            "setup": {
                "initializeGit": True,
                "env": {
                    "HF_HUB_OFFLINE": "1",
                    "PYTHONDONTWRITEBYTECODE": "1",
                    "SEMANTIC_OKF_BUNDLE": "$WORKSPACE/knowledge",
                    "TRANSFORMERS_OFFLINE": "1",
                },
            },
        },
        "evaluation": {
            "assertions": [{"type": "is-json", "metric": "response-format"}],
            "requests": 3,
            "timeoutMs": 600000,
            "tracing": False,
            "maxConcurrency": 2,
            "noCache": True,
        },
        "comparison": {
            "profiles": _profiles(),
            "variants": [
                {
                    "id": "codex-luna-tools",
                    "description": "Codex command backend with GPT-5.6 Luna and one shared, profile-gated, read-only Semantic OKF MCP transport in a network-disabled ephemeral workspace.",
                    "agent": {
                        "adapter": "codex",
                        "model": "gpt-5.6-luna",
                        "executionMethod": "command",
                        "commandPath": PUBLICATION_COMMAND_PATH,
                        "sandboxMode": "workspace-write",
                        "approvalPolicy": "never",
                        "webSearchEnabled": False,
                        "networkAccessEnabled": False,
                        "reasoningEffort": "medium",
                        "additionalDirectories": [],
                        "cliEnv": {},
                        "envPassthrough": [
                            "SEMANTIC_OKF_PYTHON",
                            "SEMANTIC_OKF_HF_HUB_CACHE",
                        ],
                        "config": {
                            "mcp_servers": {
                                "semantic_okf": {
                                    "command": "cmd.exe",
                                    "args": ["/d", "/c", "mcp-runtime\\run_server.cmd"],
                                    "env_vars": MCP_ENVIRONMENT,
                                    "enabled_tools": MCP_TOOLS,
                                    "startup_timeout_sec": 60,
                                    "tool_timeout_sec": 600,
                                }
                            }
                        },
                    },
                    "output": {
                        "tags": ["codex", "gpt-5.6-luna", "isolated", "tool-capable"],
                        "labels": {
                            "variantDisplayName": "Codex GPT-5.6 Luna (isolated CLI tools)"
                        },
                    },
                }
            ],
        },
    }


def _coverage(questions: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    return {
        "schemaVersion": 1,
        "policy": {
            "minimumPrompts": 10,
            "minimumTaskFamilies": 6,
            "maximumPromptWords": 210,
            "maximumPairwiseJaccard": 0.65,
            "requiredCaseKinds": [
                "naturalistic-forward",
                "generalization",
                "boundary-recovery",
            ],
        },
        "cases": [
            {
                "promptId": question["id"],
                "caseKind": CASE_METADATA[question["id"]][0],
                "taskFamily": CASE_METADATA[question["id"]][1],
            }
            for question in questions
        ],
    }


def build_artifacts(repo_root: Path = REPO_ROOT) -> dict[str, bytes]:
    """Build and validate both deterministic output byte strings in memory."""

    root = repo_root.resolve(strict=True)
    questions = _load_reviewed_ground_truth(root)
    bundle, records = _load_claim_records(root)
    all_allowed = _all_claim_bindings(bundle, records)
    contracts = [
        _claim_contract(question, bundle, records, all_allowed)
        for question in questions
    ]
    config = _config(questions, contracts)
    coverage = _coverage(questions)
    _validate_generated(config, coverage, questions, contracts)
    yaml_text = yaml.dump(
        config,
        Dumper=Dumper,
        allow_unicode=True,
        sort_keys=False,
        width=4096,
    )
    coverage_text = json.dumps(coverage, indent=2, ensure_ascii=False) + "\n"
    return {
        "ensemble-hard10.yaml": yaml_text.encode("utf-8"),
        "prompt-coverage.json": coverage_text.encode("utf-8"),
    }


def _validate_generated(
    config: Mapping[str, Any],
    coverage: Mapping[str, Any],
    questions: Sequence[Mapping[str, Any]],
    contracts: Sequence[Mapping[str, Any]],
) -> None:
    _exact_keys(
        config,
        {"schemaVersion", "benchmark", "task", "workspace", "evaluation", "comparison"},
        "generated config",
    )
    prompts = config.get("task", {}).get("prompts")
    if not isinstance(prompts, list) or len(prompts) != 10:
        raise ConfigGenerationError("generated config must contain exactly ten prompts")
    for prompt, question, contract in zip(prompts, questions, contracts, strict=True):
        if prompt.get("id") != question["id"] or prompt.get("prompt") != _prompt(question):
            raise ConfigGenerationError("generated prompt differs from reviewed ground truth")
        assertions = prompt.get("evaluation", {}).get("assertions")
        expected = [
            ("response-contract", _response_contract_js(question["id"])),
            ("evidence-validity", _evidence_validity_js(contract)),
            ("atomic-answer-completeness", _coverage_js(contract, negative=False)),
            ("important-negative-coverage", _coverage_js(contract, negative=True)),
        ]
        if (
            not isinstance(assertions, list)
            or [(item.get("metric"), item.get("value")) for item in assertions] != expected
            or any(item.get("type") != "javascript" for item in assertions)
        ):
            raise ConfigGenerationError("generated assertions differ from reviewed options")
    evaluation = config["evaluation"]
    if evaluation != {
        "assertions": [{"type": "is-json", "metric": "response-format"}],
        "requests": 3,
        "timeoutMs": 600000,
        "tracing": False,
        "maxConcurrency": 2,
        "noCache": True,
    }:
        raise ConfigGenerationError("generated evaluation options differ")
    profiles = config["comparison"]["profiles"]
    if [profile.get("id") for profile in profiles] != PROFILE_IDS:
        raise ConfigGenerationError("generated profile identities differ")
    roles = [profile.get("output", {}).get("labels", {}).get("causal_role") for profile in profiles]
    if roles != ["passive-control", "active-control", "treatment"]:
        raise ConfigGenerationError("generated causal roles differ")
    installed = [
        [
            skill.get("source", {}).get("skillId")
            for skill in profile.get("capabilities", {}).get("skills", [])
        ]
        for profile in profiles
    ]
    if installed != [[], ["consult-semantic-okf-adaptive"], ["consult-semantic-okf-ensemble"]]:
        raise ConfigGenerationError("generated profile skill isolation differs")
    variant = config["comparison"]["variants"]
    if not isinstance(variant, list) or len(variant) != 1:
        raise ConfigGenerationError("generated variant set differs")
    agent = variant[0].get("agent", {})
    mcp = agent.get("config", {}).get("mcp_servers", {}).get("semantic_okf", {})
    if (
        agent.get("commandPath") != PUBLICATION_COMMAND_PATH
        or agent.get("webSearchEnabled") is not False
        or agent.get("networkAccessEnabled") is not False
        or mcp.get("env_vars") != MCP_ENVIRONMENT
        or mcp.get("enabled_tools") != MCP_TOOLS
    ):
        raise ConfigGenerationError("generated publication or MCP contract differs")
    sources = config["workspace"]["sources"]
    if sources != [
        {
            "id": "semantic-okf-ensemble-final-bundle",
            "type": "local-path",
            "path": PINNED_BUNDLE_RELATIVE.as_posix(),
            "target": "/knowledge",
        },
        {
            "id": "semantic-okf-profile-gated-mcp-runtime",
            "type": "local-path",
            "path": "skills/consult-semantic-okf-ensemble/mcp-runtime",
            "target": "/mcp-runtime",
        },
        {
            "id": "semantic-okf-confirmed-output-publication-runtime",
            "type": "local-path",
            "path": "skills/consult-semantic-okf-ensemble/publication-runtime",
            "target": "/publication-runtime",
        },
    ]:
        raise ConfigGenerationError("generated workspace source bindings differ")
    expected_coverage = _coverage(questions)
    if coverage != expected_coverage:
        raise ConfigGenerationError("generated prompt coverage differs")


def _write_atomic(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and (not path.is_file() or path.is_symlink()):
        raise ConfigGenerationError(f"output must be a regular non-link file: {path}")
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as stream:
            temporary = Path(stream.name)
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        temporary = None
    except OSError as exc:
        raise ConfigGenerationError(f"cannot publish {path}: {exc}") from exc
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def _output_directory(repo_root: Path, value: Path) -> Path:
    return value.resolve() if value.is_absolute() else (repo_root / value).resolve()


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIRECTORY_RELATIVE)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Fail if checked outputs differ; never modify files.",
    )
    return parser.parse_args(list(argv))


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    try:
        repo_root = args.repo_root.resolve(strict=True)
        outputs = build_artifacts(repo_root)
        output_dir = _output_directory(repo_root, args.output_dir)
        changed: list[str] = []
        for name, payload in outputs.items():
            path = output_dir / name
            if args.check:
                try:
                    current = _regular_file(path, f"checked output {name}").read_bytes()
                except ConfigGenerationError:
                    changed.append(name)
                    continue
                if current != payload:
                    changed.append(name)
            else:
                _write_atomic(path, payload)
        if changed:
            print(
                "error: generated Skill Arena outputs drifted: " + ", ".join(changed),
                file=sys.stderr,
            )
            return 2
        print(
            json.dumps(
                {
                    "status": "pass",
                    "mode": "check" if args.check else "write",
                    "ground_truth_sha256": EXPECTED_GROUND_TRUTH_SHA256,
                    "outputs": [
                        {
                            "path": (output_dir / name).as_posix(),
                            "sha256": _sha256_bytes(payload),
                        }
                        for name, payload in outputs.items()
                    ],
                },
                ensure_ascii=False,
                separators=(",", ":"),
            )
        )
        return 0
    except (ConfigGenerationError, OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
