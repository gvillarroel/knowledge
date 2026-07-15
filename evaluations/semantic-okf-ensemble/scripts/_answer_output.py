#!/usr/bin/env python3
"""Closed-contract helpers for the definitive ensemble answer evaluation."""

from __future__ import annotations

import hashlib
import json
import math
import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Mapping, Sequence

import yaml

from _evaluation import (
    REPO_ROOT,
    canonical_json,
    display_path,
    load_json,
    load_jsonl,
    sha256,
)


EVALUATION_ROOT = REPO_ROOT / "evaluations/semantic-okf-ensemble"
DEFAULT_CONTRACT = EVALUATION_ROOT / "answer-output-evaluation-contract.json"
SKILL_ARENA_CONFIG = EVALUATION_ROOT / "skill-arena/ensemble-hard10.yaml"
CONTRACT_SCHEMA = "semantic-okf-ensemble-answer-evaluation-contract/1.5"
MECHANICAL_SCHEMA = "semantic-okf-ensemble-answer-mechanical/1.2"
REVIEW_MANIFEST_SCHEMA = "semantic-okf-ensemble-answer-review-manifest/1.2"
REVIEW_TASK_SCHEMA = "semantic-okf-ensemble-answer-review-task/1.0"
IMPLEMENTATION_PROJECT_ROOT = Path(__file__).resolve().parents[3]
MECHANICAL_RUNTIME = Path(__file__).resolve()
PREPARER = EVALUATION_ROOT / "scripts/prepare_answer_output_evaluation.py"
REVIEWER = EVALUATION_ROOT / "scripts/run_blinded_answer_reviews.py"
PAPER_RE = re.compile(r"^(\d{4})\.(\d{5})v(\d+)$", re.IGNORECASE)
PAPER_IN_TEXT_RE = re.compile(r"(\d{4})[.-](\d{5})v(\d+)", re.IGNORECASE)
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
PAGE_RE = re.compile(r"^PDF-page-(\d+)$")

MECHANICAL_METRICS = (
    "response_contract",
    "evidence_validity",
    "grounding",
    "exact_atomic_evidence_coverage",
    "required_paper_coverage",
    "required_source_coverage",
    "exact_negative_evidence_coverage",
)
SEMANTIC_METRICS = (
    "claim_correctness",
    "semantic_completeness",
    "important_negative_coverage",
)

EXPECTED_MCP_CONFIG = {
    "mcp_servers": {
        "semantic_okf": {
            "command": "cmd.exe",
            "args": ["/d", "/c", "mcp-runtime\\run_server.cmd"],
            "env_vars": [
                "SKILL_ARENA_ALLOWED_SKILLS",
                "CODEX_HOME",
                "SEMANTIC_OKF_BUNDLE",
                "SEMANTIC_OKF_PYTHON",
                "SEMANTIC_OKF_HF_HUB_CACHE",
                "HF_HUB_OFFLINE",
                "TRANSFORMERS_OFFLINE",
                "PYTHONDONTWRITEBYTECODE",
            ],
            "enabled_tools": [
                "semantic_okf_bootstrap_skill",
                "semantic_okf_inspect",
                "semantic_okf_coverage_brief",
                "semantic_okf_prepare_answer",
                "semantic_okf_confirm_answer",
            ],
            "startup_timeout_sec": 60,
            "tool_timeout_sec": 600,
        }
    }
}
PROFILE_SKILLS = {
    "knowledge-only-control": None,
    "adaptive-consult-control": "consult-semantic-okf-adaptive",
    "ensemble-consult-treatment": "consult-semantic-okf-ensemble",
}
PROMPTFOO_ASSERTION_METRICS = [
    "response-format",
    "response-contract",
    "evidence-validity",
    "atomic-answer-completeness",
    "important-negative-coverage",
]


class AnswerEvaluationError(ValueError):
    """Describe a fail-closed answer-evaluation contract violation."""


@dataclass(frozen=True)
class BundleLedger:
    """Validated final-03 bundle state needed for evidence checks."""

    root: Path
    identity: dict[str, Any]
    records: dict[str, dict[str, Any]]
    paper_records: dict[str, dict[str, Any]]


def exact_keys(value: Any, expected: set[str], label: str) -> dict[str, Any]:
    """Require one closed JSON object."""

    if not isinstance(value, dict):
        raise AnswerEvaluationError(f"{label} must be an object")
    actual = set(value)
    if actual != expected:
        raise AnswerEvaluationError(
            f"{label} uses a closed schema; missing={sorted(expected - actual)}, "
            f"unknown={sorted(actual - expected)}"
        )
    return value


def _ordered_keys(value: Any, expected: Sequence[str]) -> bool:
    return isinstance(value, dict) and list(value) == list(expected)


def _string_list(value: Any, *, nonempty: bool = False) -> bool:
    return (
        isinstance(value, list)
        and (not nonempty or bool(value))
        and all(isinstance(item, str) and bool(item) for item in value)
    )


def _sorted_unique(values: Any, *, nonempty: bool = False) -> bool:
    return (
        _string_list(values, nonempty=nonempty)
        and len(values) == len(set(values))
        and values == sorted(values)
    )


def _valid_hash(value: Any) -> bool:
    return isinstance(value, str) and SHA256_RE.fullmatch(value) is not None


def _implementation_binding(path: Path) -> dict[str, str]:
    resolved = path.resolve(strict=True)
    return {
        "path": resolved.relative_to(IMPLEMENTATION_PROJECT_ROOT).as_posix(),
        "sha256": sha256(resolved),
    }


def preparation_implementation() -> dict[str, dict[str, str]]:
    """Bind the exact code that created mechanical scores and review tasks."""

    return {
        "mechanical_runtime": _implementation_binding(MECHANICAL_RUNTIME),
        "preparer": _implementation_binding(PREPARER),
    }


def _repo_path(relative: Any, label: str, *, must_exist: bool = True) -> Path:
    if not isinstance(relative, str) or not relative:
        raise AnswerEvaluationError(f"{label} must be a nonempty repository-relative path")
    logical = PurePosixPath(relative.replace("\\", "/"))
    if logical.is_absolute() or not logical.parts or any(part in {"", ".", ".."} for part in logical.parts):
        raise AnswerEvaluationError(f"{label} must be a safe repository-relative path")
    candidate = REPO_ROOT.joinpath(*logical.parts).resolve(strict=must_exist)
    try:
        candidate.relative_to(REPO_ROOT.resolve(strict=True))
    except ValueError as exc:
        raise AnswerEvaluationError(f"{label} escapes the repository") from exc
    return candidate


def _regular_file(root: Path, relative: Any, label: str) -> Path:
    if not isinstance(relative, str) or not relative:
        raise AnswerEvaluationError(f"{label} must be a nonempty relative path")
    logical = PurePosixPath(relative.replace("\\", "/"))
    if logical.is_absolute() or not logical.parts or any(part in {"", ".", ".."} for part in logical.parts):
        raise AnswerEvaluationError(f"{label} is unsafe")
    try:
        candidate = root.joinpath(*logical.parts).resolve(strict=True)
        candidate.relative_to(root.resolve(strict=True))
    except (OSError, ValueError) as exc:
        raise AnswerEvaluationError(f"{label} does not resolve inside the bundle") from exc
    if not candidate.is_file() or candidate.is_symlink():
        raise AnswerEvaluationError(f"{label} must resolve to a regular non-link file")
    return candidate


def load_contract(path: Path = DEFAULT_CONTRACT) -> dict[str, Any]:
    """Load and validate the closed answer-evaluation contract."""

    contract = load_json(path)
    exact_keys(
        contract,
        {
            "schema_version",
            "benchmark",
            "bundle",
            "ground_truth",
            "response_contract",
            "review",
            "metrics",
            "publication",
        },
        "answer evaluation contract",
    )
    if contract["schema_version"] != CONTRACT_SCHEMA:
        raise AnswerEvaluationError("answer evaluation contract schema_version differs")

    benchmark = exact_keys(
        contract["benchmark"],
        {
            "id",
            "profiles",
            "variant_id",
            "command_path",
            "question_ids",
            "repetitions_per_cell",
            "total_answers",
        },
        "benchmark contract",
    )
    if not isinstance(benchmark["id"], str) or not benchmark["id"]:
        raise AnswerEvaluationError("benchmark id must be a nonempty string")
    if benchmark["profiles"] != [
        "knowledge-only-control",
        "adaptive-consult-control",
        "ensemble-consult-treatment",
    ]:
        raise AnswerEvaluationError("benchmark profiles differ from the reviewed three-arm design")
    if benchmark["variant_id"] != "codex-luna-tools":
        raise AnswerEvaluationError("benchmark variant differs")
    if benchmark["command_path"] != r"publication-runtime\run_codex.cmd":
        raise AnswerEvaluationError("benchmark command path differs")
    if not _string_list(benchmark["question_ids"], nonempty=True) or len(set(benchmark["question_ids"])) != 10:
        raise AnswerEvaluationError("benchmark must contain ten unique question IDs")
    repetitions = benchmark["repetitions_per_cell"]
    if not isinstance(repetitions, int) or isinstance(repetitions, bool) or repetitions != 3:
        raise AnswerEvaluationError("benchmark repetitions_per_cell must be three")
    expected_total = len(benchmark["profiles"]) * len(benchmark["question_ids"]) * repetitions
    if benchmark["total_answers"] != expected_total or expected_total != 90:
        raise AnswerEvaluationError("benchmark total_answers must equal the exact 90-cell design")

    bundle = exact_keys(
        contract["bundle"],
        {
            "run_id",
            "repository_path",
            "file_count",
            "tree_sha256",
            "ensemble_index_sha256",
            "ensemble_plan_sha256",
            "core_tree_sha256",
            "records_sha256",
            "record_count",
            "source_manifest_sha256",
        },
        "bundle contract",
    )
    if bundle["run_id"] != "20260715-ensemble-final-03":
        raise AnswerEvaluationError("bundle run_id differs from final-03")
    _repo_path(bundle["repository_path"], "bundle repository_path", must_exist=False)
    for key in (
        "tree_sha256",
        "ensemble_index_sha256",
        "ensemble_plan_sha256",
        "core_tree_sha256",
        "records_sha256",
        "source_manifest_sha256",
    ):
        if not _valid_hash(bundle[key]):
            raise AnswerEvaluationError(f"bundle {key} is not a lowercase SHA-256")
    if bundle["file_count"] != 904 or bundle["record_count"] != 874:
        raise AnswerEvaluationError("bundle file or record count differs from final-03")

    ground_truth = exact_keys(
        contract["ground_truth"],
        {
            "path",
            "sha256",
            "schema_version",
            "benchmark_manifest_path",
            "benchmark_manifest_sha256",
            "benchmark_id",
        },
        "ground-truth contract",
    )
    ground_truth_path = _repo_path(ground_truth["path"], "ground-truth path")
    if not _valid_hash(ground_truth["sha256"]):
        raise AnswerEvaluationError("ground-truth SHA-256 is invalid")
    if sha256(ground_truth_path) != ground_truth["sha256"]:
        raise AnswerEvaluationError("ground-truth SHA-256 differs from the reviewed file")
    if ground_truth["schema_version"] != "semantic-okf-hard-ground-truth/1.0":
        raise AnswerEvaluationError("ground-truth schema_version differs")
    benchmark_manifest_path = _repo_path(
        ground_truth["benchmark_manifest_path"],
        "ground-truth benchmark manifest path",
    )
    if not _valid_hash(ground_truth["benchmark_manifest_sha256"]):
        raise AnswerEvaluationError("ground-truth benchmark manifest SHA-256 is invalid")
    if sha256(benchmark_manifest_path) != ground_truth["benchmark_manifest_sha256"]:
        raise AnswerEvaluationError("ground-truth benchmark manifest SHA-256 differs")
    benchmark_manifest = load_json(benchmark_manifest_path)
    exact_keys(
        benchmark_manifest,
        {
            "schema_version",
            "benchmark_id",
            "status",
            "frozen_on",
            "mutation_policy",
            "parent_frozen_benchmark",
            "amendments",
            "generator",
            "cohorts",
            "invariants",
            "audit_summary",
        },
        "ground-truth benchmark manifest",
    )
    if (
        benchmark_manifest["schema_version"]
        != "semantic-okf-frozen-answer-benchmark/1.0"
        or benchmark_manifest["status"] != "frozen"
        or benchmark_manifest["benchmark_id"] != ground_truth["benchmark_id"]
    ):
        raise AnswerEvaluationError("ground-truth benchmark manifest identity differs")
    cohorts = benchmark_manifest.get("cohorts")
    hard_cohort = (
        cohorts.get("hard_ground_truth") if isinstance(cohorts, dict) else None
    )
    exact_keys(
        hard_cohort,
        {"path", "sha256", "count", "ordered_ids"},
        "ground-truth benchmark hard cohort",
    )
    if hard_cohort != {
        "path": ground_truth["path"],
        "sha256": ground_truth["sha256"],
        "count": len(benchmark["question_ids"]),
        "ordered_ids": benchmark["question_ids"],
    }:
        raise AnswerEvaluationError("ground-truth benchmark hard cohort differs")

    response = exact_keys(
        contract["response_contract"],
        {
            "top_level_keys",
            "answer_keys",
            "claim_keys",
            "citation_keys",
            "evidence_keys",
            "summary_min_words",
            "summary_max_words",
        },
        "response contract",
    )
    expected_key_lists = {
        "top_level_keys": ["question_id", "answer", "evidence"],
        "answer_keys": ["summary", "claims", "paper_ids", "citations"],
        "claim_keys": ["statement", "supporting_claim_ids"],
        "citation_keys": ["paper_id", "pages"],
        "evidence_keys": ["claim_id", "concept_path", "paper_id", "source_path", "locators"],
    }
    for key, expected in expected_key_lists.items():
        if response[key] != expected:
            raise AnswerEvaluationError(f"response contract {key} differs")
    if response["summary_min_words"] != 180 or response["summary_max_words"] != 320:
        raise AnswerEvaluationError("response summary word bounds differ")

    review = exact_keys(
        contract["review"],
        {"schema_version", "model", "blinded", "score_values", "maximum_note_words"},
        "review contract",
    )
    if review != {
        "schema_version": "semantic-okf-ensemble-answer-review/1.1",
        "model": "openai-codex/gpt-5.6-luna",
        "blinded": True,
        "score_values": [0, 0.5, 1],
        "maximum_note_words": 35,
    }:
        raise AnswerEvaluationError("review contract differs from the fixed blinded rubric")
    if contract["metrics"] != [
        "response_contract",
        "evidence_validity",
        "grounding",
        "claim_correctness",
        "semantic_completeness",
        "exact_atomic_evidence_coverage",
        "required_paper_coverage",
        "required_source_coverage",
        "important_negative_coverage",
        "exact_negative_evidence_coverage",
    ]:
        raise AnswerEvaluationError("metric order differs from the reviewed contract")
    publication = exact_keys(
        contract["publication"],
        {
            "raw_root",
            "raw_outputs_ignored",
            "compact_schema_version",
            "append_only",
            "mcp_protocol",
        },
        "publication contract",
    )
    protocol = exact_keys(
        publication["mcp_protocol"],
        {
            "tools",
            "bootstrap_schema",
            "bootstrap_key_order",
            "bootstrap_skill_id",
            "bootstrap_skill_sha256",
            "bootstrap_skill_byte_count",
            "bootstrap_exactly_once",
            "bootstrap_first",
            "treatment_shell_tool_disabled",
            "treatment_skill_id",
            "shell_disable_arguments",
            "shell_isolation_receipt_schema",
            "shell_isolation_receipt_key_order",
            "controls_shell_policy_unchanged",
            "mode_argument",
            "minimum_successful_prepares",
            "prepared_answer_schema",
            "prepared_answer_key_order",
            "candidate_digest_binding",
            "confirm_argument",
            "confirm_argument_pattern",
            "confirmation_receipt_schema",
            "confirmation_receipt_key_order",
            "publication_source",
            "confirm_exactly_once",
            "confirm_terminal",
            "confirm_idempotent",
            "failed_protocol_call_publishes",
            "failed_protocol_call_clears_transaction",
            "failure_requires_fresh_prepare",
            "final_transaction_must_be_clean",
            "coverage_priority_order",
            "priority_order_session_bound",
        },
        "publication MCP protocol",
    )
    expected_protocol = {
        "tools": [
            "semantic_okf_bootstrap_skill",
            "semantic_okf_inspect",
            "semantic_okf_coverage_brief",
            "semantic_okf_prepare_answer",
            "semantic_okf_confirm_answer",
        ],
        "bootstrap_schema": "semantic-okf-skill-bootstrap/1.0",
        "bootstrap_key_order": [
            "schema",
            "skill_id",
            "skill_sha256",
            "byte_count",
            "skill_markdown",
        ],
        "bootstrap_skill_id": "consult-semantic-okf-ensemble",
        "bootstrap_skill_sha256": "ec80687beb701f5fc8b6cd13d5ec779cbe5e1f52baffbf3a4a41db4f390717c2",
        "bootstrap_skill_byte_count": 15699,
        "bootstrap_exactly_once": True,
        "bootstrap_first": True,
        "treatment_shell_tool_disabled": True,
        "treatment_skill_id": "consult-semantic-okf-ensemble",
        "shell_disable_arguments": ["--disable", "shell_tool"],
        "shell_isolation_receipt_schema": (
            "semantic-okf-shell-isolation-receipt/1.0"
        ),
        "shell_isolation_receipt_key_order": [
            "schema",
            "skill_id",
            "shell_tool_disabled",
        ],
        "controls_shell_policy_unchanged": True,
        "mode_argument": False,
        "minimum_successful_prepares": 1,
        "prepared_answer_schema": "semantic-okf-prepared-answer/1.0",
        "prepared_answer_key_order": [
            "schema",
            "candidate_json",
            "response_sha256",
            "byte_count",
        ],
        "candidate_digest_binding": "sha256-lowercase-hex-of-utf8-candidate-json",
        "confirm_argument": "response_sha256",
        "confirm_argument_pattern": "^[0-9a-f]{64}$",
        "confirmation_receipt_schema": "semantic-okf-answer-confirmation-receipt/1.0",
        "confirmation_receipt_key_order": [
            "schema",
            "status",
            "response_sha256",
            "byte_count",
        ],
        "publication_source": "prepared-envelope-candidate-json-bytes",
        "confirm_exactly_once": True,
        "confirm_terminal": True,
        "confirm_idempotent": False,
        "failed_protocol_call_publishes": False,
        "failed_protocol_call_clears_transaction": True,
        "failure_requires_fresh_prepare": True,
        "final_transaction_must_be_clean": True,
        "coverage_priority_order": "persisted-idf-facet-consensus-priority-v1",
        "priority_order_session_bound": True,
    }
    if protocol != expected_protocol or publication != {
        "raw_root": "evaluations/semantic-okf-ensemble/results",
        "raw_outputs_ignored": True,
        "compact_schema_version": "semantic-okf-ensemble-answer-output-comparison/1.2",
        "append_only": True,
        "mcp_protocol": expected_protocol,
    }:
        raise AnswerEvaluationError("publication contract differs")
    return contract


def _tree_identity(root: Path) -> tuple[int, str]:
    files = sorted(path for path in root.rglob("*") if path.is_file())
    rows = [
        {"path": path.relative_to(root).as_posix(), "sha256": sha256(path)}
        for path in files
    ]
    return len(files), hashlib.sha256(canonical_json(rows).encode("utf-8")).hexdigest()


def _deep_validate_bundle(root: Path) -> None:
    scripts = REPO_ROOT / "skills/build-semantic-okf-ensemble/scripts"
    if str(scripts) not in sys.path:
        sys.path.insert(0, str(scripts))
    try:
        from _ensemble_build import validate_ensemble_bundle
    except ImportError as exc:
        raise AnswerEvaluationError(f"cannot import the ensemble bundle validator: {exc}") from exc
    report = validate_ensemble_bundle(root)
    if report.get("status") != "pass" or report.get("valid") is not True:
        raise AnswerEvaluationError(f"final-03 bundle deep validation failed: {report.get('errors')}")


def _paper_id(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    match = PAPER_IN_TEXT_RE.search(value)
    if match is None:
        return None
    return f"{match.group(1)}.{match.group(2)}v{match.group(3).lower()}"


def load_final_bundle(
    root: Path,
    contract: Mapping[str, Any],
    *,
    deep_validate: bool = True,
    require_contract_path: bool = True,
) -> BundleLedger:
    """Validate and load the exact frozen final-03 bundle."""

    expected = contract["bundle"]
    root = root.resolve(strict=True)
    if require_contract_path and root != _repo_path(expected["repository_path"], "bundle repository_path"):
        raise AnswerEvaluationError("bundle path differs from the frozen final-03 repository path")
    if not root.is_dir() or root.is_symlink():
        raise AnswerEvaluationError("bundle root must be a regular directory, not a link")
    if deep_validate:
        _deep_validate_bundle(root)
    file_count, tree_hash = _tree_identity(root)
    if file_count != expected["file_count"] or tree_hash != expected["tree_sha256"]:
        raise AnswerEvaluationError("bundle recursive file count or SHA-256 differs from final-03")

    index_path = _regular_file(root, "ensemble/index.json", "ensemble index")
    records_path = _regular_file(root, "semantic/records.jsonl", "semantic records")
    source_manifest = _regular_file(root, "semantic/source-manifest.json", "source manifest")
    if sha256(index_path) != expected["ensemble_index_sha256"]:
        raise AnswerEvaluationError("ensemble index SHA-256 differs from final-03")
    if sha256(records_path) != expected["records_sha256"]:
        raise AnswerEvaluationError("semantic records SHA-256 differs from final-03")
    if sha256(source_manifest) != expected["source_manifest_sha256"]:
        raise AnswerEvaluationError("source manifest SHA-256 differs from final-03")
    index = load_json(index_path)
    if index.get("ensemble_plan_sha256") != expected["ensemble_plan_sha256"]:
        raise AnswerEvaluationError("ensemble plan identity differs from final-03")
    if index.get("core") != {
        "record_count": expected["record_count"],
        "records_sha256": expected["records_sha256"],
        "tree_sha256": expected["core_tree_sha256"],
    }:
        raise AnswerEvaluationError("ensemble authoritative-core identity differs from final-03")

    records: dict[str, dict[str, Any]] = {}
    papers: dict[str, dict[str, Any]] = {}
    for record in load_jsonl(records_path):
        record_id = record.get("record_id")
        if not isinstance(record_id, str) or not record_id or record_id in records:
            raise AnswerEvaluationError(f"semantic ledger has invalid or duplicate record_id: {record_id!r}")
        records[record_id] = record
        paper = _paper_id(record.get("source_id")) or _paper_id(record_id)
        if paper and str(record.get("source_id", "")).startswith("paper-"):
            if paper in papers:
                raise AnswerEvaluationError(f"semantic ledger has duplicate paper record: {paper}")
            papers[paper] = record
    if len(records) != expected["record_count"]:
        raise AnswerEvaluationError("semantic ledger record count differs from final-03")
    identity = {
        "run_id": expected["run_id"],
        "repository_path": expected["repository_path"],
        "file_count": file_count,
        "tree_sha256": tree_hash,
        "ensemble_index_sha256": expected["ensemble_index_sha256"],
        "ensemble_plan_sha256": expected["ensemble_plan_sha256"],
        "core_tree_sha256": expected["core_tree_sha256"],
        "records_sha256": expected["records_sha256"],
        "record_count": len(records),
        "source_manifest_sha256": expected["source_manifest_sha256"],
    }
    return BundleLedger(root=root, identity=identity, records=records, paper_records=papers)


def load_ground_truth(
    path: Path,
    contract: Mapping[str, Any],
    ledger: BundleLedger,
    *,
    require_contract_path: bool = True,
) -> dict[str, dict[str, Any]]:
    """Load the exact ten evidence-first hard ground-truth rows."""

    expected = contract["ground_truth"]
    path = path.resolve(strict=True)
    if require_contract_path and path != _repo_path(expected["path"], "ground-truth path"):
        raise AnswerEvaluationError("ground-truth path differs from the frozen contract")
    if sha256(path) != expected["sha256"]:
        raise AnswerEvaluationError("hard ground-truth SHA-256 differs")
    rows = load_jsonl(path)
    expected_ids = contract["benchmark"]["question_ids"]
    if [row.get("id") for row in rows] != expected_ids:
        raise AnswerEvaluationError("hard ground-truth identities or order differ")
    result: dict[str, dict[str, Any]] = {}
    for row in rows:
        exact_keys(
            row,
            {
                "schema_version",
                "id",
                "question",
                "ground_truth",
                "authoritative_evidence",
                "corpus_inventory",
            },
            f"ground truth {row.get('id')}",
        )
        if row["schema_version"] != expected["schema_version"] or not isinstance(row["question"], str):
            raise AnswerEvaluationError(f"ground truth {row.get('id')} schema or question differs")
        truth = exact_keys(
            row["ground_truth"],
            {
                "acceptable_variants",
                "answer_claims",
                "derivation",
                "important_negatives",
                "required_paper_ids",
                "required_source_ids",
            },
            f"ground truth payload {row['id']}",
        )
        if not _sorted_unique(truth["required_paper_ids"], nonempty=True):
            raise AnswerEvaluationError(f"ground truth {row['id']} required papers must be sorted and unique")
        if not _sorted_unique(truth["required_source_ids"], nonempty=True):
            raise AnswerEvaluationError(f"ground truth {row['id']} required sources must be sorted and unique")
        for kind in ("answer_claims", "important_negatives"):
            items = truth[kind]
            if not isinstance(items, list) or not items:
                raise AnswerEvaluationError(f"ground truth {row['id']} {kind} must be nonempty")
            seen: set[str] = set()
            for item in items:
                exact_keys(item, {"id", "statement", "evidence_claim_ids"}, f"{row['id']} {kind} item")
                if not isinstance(item["id"], str) or item["id"] in seen:
                    raise AnswerEvaluationError(f"ground truth {row['id']} has duplicate {kind} identity")
                seen.add(item["id"])
                if not isinstance(item["statement"], str) or not item["statement"].strip():
                    raise AnswerEvaluationError(f"ground truth {row['id']} has an empty {kind} statement")
                if not _string_list(item["evidence_claim_ids"], nonempty=True) or len(
                    set(item["evidence_claim_ids"])
                ) != len(item["evidence_claim_ids"]):
                    raise AnswerEvaluationError(f"ground truth {row['id']} has invalid evidence claim IDs")
                for claim_id in item["evidence_claim_ids"]:
                    record = ledger.records.get(claim_id)
                    if record is None or record.get("attributes", {}).get("review_state") != "reviewed":
                        raise AnswerEvaluationError(
                            f"ground truth {row['id']} references a missing or unreviewed claim: {claim_id}"
                        )
        result[row["id"]] = row
    return result


def _strict_output(text: str) -> tuple[dict[str, Any] | None, str]:
    def object_hook(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        value: dict[str, Any] = {}
        for key, item in pairs:
            if key in value:
                raise AnswerEvaluationError(f"duplicate output key: {key}")
            value[key] = item
        return value

    try:
        value = json.loads(text, object_pairs_hook=object_hook)
    except (json.JSONDecodeError, AnswerEvaluationError):
        return None, "invalid-json"
    if not isinstance(value, dict):
        return None, "non-object-json"
    return value, "object"


def response_contract_score(
    output: dict[str, Any] | None,
    question_id: str,
    contract: Mapping[str, Any],
) -> float:
    """Independently enforce the exact JSON response contract."""

    expected = contract["response_contract"]
    if not _ordered_keys(output, expected["top_level_keys"]):
        return 0.0
    assert output is not None
    evidence = output["evidence"]
    if output["question_id"] != question_id or not isinstance(evidence, list):
        return 0.0
    answer = output["answer"]
    if answer is None:
        return float(not evidence)
    if not _ordered_keys(answer, expected["answer_keys"]):
        return 0.0
    summary = answer["summary"]
    words = summary.strip().split() if isinstance(summary, str) else []
    if not expected["summary_min_words"] <= len(words) <= expected["summary_max_words"]:
        return 0.0
    claims = answer["claims"]
    paper_ids = answer["paper_ids"]
    citations = answer["citations"]
    if not isinstance(claims, list) or not claims or not _sorted_unique(paper_ids) or not isinstance(citations, list):
        return 0.0
    if not evidence:
        return 0.0
    if any(PAPER_RE.fullmatch(paper) is None for paper in paper_ids):
        return 0.0
    for claim in claims:
        if not _ordered_keys(claim, expected["claim_keys"]):
            return 0.0
        if not isinstance(claim["statement"], str) or not claim["statement"].strip():
            return 0.0
        if not _sorted_unique(claim["supporting_claim_ids"]):
            return 0.0
    citation_papers = [item.get("paper_id") for item in citations if isinstance(item, dict)]
    if len(citation_papers) != len(citations) or not _sorted_unique(citation_papers):
        return 0.0
    for citation in citations:
        if not _ordered_keys(citation, expected["citation_keys"]):
            return 0.0
        pages = citation["pages"]
        if citation["paper_id"] not in paper_ids:
            return 0.0
        if (
            not isinstance(pages, list)
            or not pages
            or any(not isinstance(page, int) or isinstance(page, bool) or page <= 0 for page in pages)
            or len(pages) != len(set(pages))
            or pages != sorted(pages)
        ):
            return 0.0
    evidence_ids = [item.get("claim_id") for item in evidence if isinstance(item, dict)]
    if len(evidence_ids) != len(evidence) or not _sorted_unique(evidence_ids):
        return 0.0
    for item in evidence:
        if not _ordered_keys(item, expected["evidence_keys"]):
            return 0.0
        if any(not isinstance(item[key], str) or not item[key] for key in expected["evidence_keys"][:-1]):
            return 0.0
        if not _sorted_unique(item["locators"]):
            return 0.0
    return 1.0


def _record_pages(record: Mapping[str, Any]) -> set[int]:
    locator = record.get("attributes", {}).get("evidence_locator")
    if not isinstance(locator, str):
        return set()
    pages: set[int] = set()
    for fragment in locator.split(";"):
        match = PAGE_RE.fullmatch(fragment.rsplit("#", 1)[-1])
        if match:
            pages.add(int(match.group(1)))
    return pages


def _concept_integrity(ledger: BundleLedger, record: Mapping[str, Any]) -> bool:
    try:
        path = _regular_file(ledger.root, record.get("concept_path"), "evidence concept path")
        text = path.read_text(encoding="utf-8")
    except (AnswerEvaluationError, OSError, UnicodeError):
        return False
    expected_lines = (
        f"record_id: {record.get('record_id')}",
        f"record_sha256: {record.get('record_sha256')}",
        f"source_id: {record.get('source_id')}",
        f"source_path: {record.get('source_path')}",
    )
    body = record.get("body")
    return all(line in text for line in expected_lines) and isinstance(body, str) and text.endswith(body + "\n")


def _citations(answer: Any) -> dict[str, set[int]]:
    result: dict[str, set[int]] = defaultdict(set)
    if not isinstance(answer, dict) or not isinstance(answer.get("citations"), list):
        return result
    for item in answer["citations"]:
        if not isinstance(item, dict) or not isinstance(item.get("paper_id"), str):
            continue
        pages = item.get("pages")
        if not isinstance(pages, list):
            continue
        for page in pages:
            if isinstance(page, int) and not isinstance(page, bool) and page > 0:
                result[item["paper_id"]].add(page)
    return result


def verify_evidence_item(
    item: Any,
    ledger: BundleLedger,
    cited_pages: Mapping[str, set[int]],
    evidence_keys: Sequence[str],
) -> tuple[bool, str, str | None]:
    """Verify one answer evidence item against the exact authoritative ledger and concept."""

    # JSON field ordering and locator ordering belong to response-contract
    # compliance. Evidence validity is an identity/content check, so a row with
    # the exact closed key set and the exact locator set remains valid even when
    # its serialization order violates the response contract.
    if not isinstance(item, dict) or set(item) != set(evidence_keys):
        return False, "item-schema", None
    claim_id = item["claim_id"]
    if not isinstance(claim_id, str):
        return False, "claim-id-type", None
    record = ledger.records.get(claim_id)
    if record is None or not str(record.get("source_id", "")).startswith("claims-"):
        return False, "claim-not-authoritative", claim_id
    if record.get("attributes", {}).get("review_state") != "reviewed":
        return False, "claim-not-reviewed", claim_id
    paper = _paper_id(record.get("source_id"))
    if paper is None or item["paper_id"] != paper:
        return False, "paper-mismatch", claim_id
    if item["concept_path"] != record.get("concept_path") or not _concept_integrity(ledger, record):
        return False, "concept-mismatch", claim_id
    if item["source_path"] != record.get("source_path"):
        return False, "source-mismatch", claim_id
    locators = item["locators"]
    if (
        not _string_list(locators, nonempty=True)
        or len(locators) != len(set(locators))
    ):
        return False, "locator-schema", claim_id
    pages: set[int] = set()
    for locator in locators:
        match = PAGE_RE.fullmatch(locator)
        if match is None:
            return False, "locator-format", claim_id
        pages.add(int(match.group(1)))
    if not pages.issubset(_record_pages(record)):
        return False, "locator-not-in-ledger", claim_id
    if not pages.issubset(cited_pages.get(paper, set())):
        return False, "locator-not-cited", claim_id
    return True, "valid", claim_id


def _safe_mean(values: Iterable[float]) -> float:
    items = list(values)
    return sum(items) / len(items) if items else 0.0


def _support_ids(answer: Any) -> list[str]:
    if not isinstance(answer, dict) or not isinstance(answer.get("claims"), list):
        return []
    return [
        claim_id
        for claim in answer["claims"]
        if isinstance(claim, dict) and isinstance(claim.get("supporting_claim_ids"), list)
        for claim_id in claim["supporting_claim_ids"]
        if isinstance(claim_id, str)
    ]


def _paper_ids(answer: Any) -> set[str]:
    if not isinstance(answer, dict) or not isinstance(answer.get("paper_ids"), list):
        return set()
    return {paper for paper in answer["paper_ids"] if isinstance(paper, str)}


def _support_context(answer: Any, ledger: BundleLedger) -> list[dict[str, Any]]:
    result = []
    for claim_id in sorted(set(_support_ids(answer))):
        record = ledger.records.get(claim_id)
        if record is None:
            result.append({"claim_id": claim_id, "status": "missing"})
            continue
        attributes = record.get("attributes", {})
        result.append(
            {
                "claim_id": claim_id,
                "status": "present",
                "paper_id": _paper_id(record.get("source_id")),
                "claim_kind": attributes.get("claim_kind"),
                "interpretation": attributes.get("interpretation"),
                "evidence_locator": attributes.get("evidence_locator"),
                "review_state": attributes.get("review_state"),
            }
        )
    return result


def score_mechanical_answer(
    output: dict[str, Any] | None,
    question_id: str,
    truth_row: Mapping[str, Any],
    ledger: BundleLedger,
    contract: Mapping[str, Any],
) -> tuple[dict[str, float], dict[str, int], list[str]]:
    """Compute all non-semantic answer metrics independently of Promptfoo assertions."""

    contract_score = response_contract_score(output, question_id, contract)
    answer = output.get("answer") if isinstance(output, dict) else None
    evidence = output.get("evidence") if isinstance(output, dict) else None
    evidence = evidence if isinstance(evidence, list) else []
    citations = _citations(answer)
    valid_ids: set[str] = set()
    valid_items = 0
    failures: list[str] = []
    for item in evidence:
        valid, reason, claim_id = verify_evidence_item(
            item,
            ledger,
            citations,
            contract["response_contract"]["evidence_keys"],
        )
        if valid and claim_id:
            valid_items += 1
            valid_ids.add(claim_id)
        else:
            failures.append(reason)
    evidence_validity = valid_items / len(evidence) if evidence else 0.0
    supports = _support_ids(answer)
    grounding = sum(claim_id in valid_ids for claim_id in supports) / len(supports) if supports else 0.0

    truth = truth_row["ground_truth"]
    support_set = set(supports)
    atomic = _safe_mean(
        float(bool(set(item["evidence_claim_ids"]) & support_set & valid_ids))
        for item in truth["answer_claims"]
    )
    negatives = _safe_mean(
        float(bool(set(item["evidence_claim_ids"]) & support_set & valid_ids))
        for item in truth["important_negatives"]
    )
    answer_papers = _paper_ids(answer)
    represented_papers = answer_papers & set(citations)
    required_papers = set(truth["required_paper_ids"])
    paper_coverage = len(required_papers & represented_papers) / len(required_papers)
    represented_sources = {
        str(ledger.records[claim_id]["source_id"])
        for claim_id in valid_ids
        if claim_id in ledger.records
    }
    represented_sources.update(
        str(ledger.paper_records[paper]["source_id"])
        for paper in represented_papers
        if paper in ledger.paper_records
    )
    required_sources = set(truth["required_source_ids"])
    source_coverage = len(required_sources & represented_sources) / len(required_sources)
    metrics = {
        "response_contract": contract_score,
        "evidence_validity": evidence_validity,
        "grounding": grounding,
        "exact_atomic_evidence_coverage": atomic,
        "required_paper_coverage": paper_coverage,
        "required_source_coverage": source_coverage,
        "exact_negative_evidence_coverage": negatives,
    }
    counts = {
        "answer_claims": len(answer.get("claims", [])) if isinstance(answer, dict) and isinstance(answer.get("claims"), list) else 0,
        "supporting_claim_references": len(supports),
        "evidence_items": len(evidence),
        "valid_evidence_items": valid_items,
        "required_atomic_claims": len(truth["answer_claims"]),
        "required_papers": len(required_papers),
        "required_sources": len(required_sources),
        "required_negatives": len(truth["important_negatives"]),
    }
    return ({key: round(value, 8) for key, value in metrics.items()}, counts, sorted(failures))


def _normalized_machine_path(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise AnswerEvaluationError(f"{label} must be a nonempty path")
    normalized = value.replace("\\", "/").rstrip("/")
    if not (normalized.startswith("/") or re.match(r"^[A-Za-z]:/", normalized)):
        raise AnswerEvaluationError(f"{label} must be absolute")
    return normalized


def _expected_task_prompts(contract: Mapping[str, Any]) -> dict[str, str]:
    """Load the exact checked Skill Arena prompts used by the command adapter."""

    try:
        payload = yaml.safe_load(SKILL_ARENA_CONFIG.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        raise AnswerEvaluationError(f"cannot load checked Skill Arena config: {exc}") from exc
    task = payload.get("task") if isinstance(payload, dict) else None
    prompts = task.get("prompts") if isinstance(task, dict) else None
    if not isinstance(prompts, list):
        raise AnswerEvaluationError("checked Skill Arena config has no task prompts")
    result: dict[str, str] = {}
    for row in prompts:
        if not isinstance(row, dict):
            raise AnswerEvaluationError("checked Skill Arena prompt must be an object")
        question_id = row.get("id")
        prompt = row.get("prompt")
        if not isinstance(question_id, str) or not isinstance(prompt, str) or question_id in result:
            raise AnswerEvaluationError("checked Skill Arena prompt identity differs")
        result[question_id] = prompt
    if list(result) != list(contract["benchmark"]["question_ids"]):
        raise AnswerEvaluationError("checked Skill Arena prompt order differs from the answer contract")
    return result


def _validate_promptfoo_effective_config(
    report: Mapping[str, Any],
    contract: Mapping[str, Any],
    ground_truth: Mapping[str, Mapping[str, Any]],
) -> str:
    """Validate and hash the machine-independent effective generation contract."""

    config = report.get("config")
    if not isinstance(config, dict):
        raise AnswerEvaluationError("Promptfoo report has no effective config")
    benchmark = contract["benchmark"]
    if config.get("description") != f"{benchmark['id']}:compare":
        raise AnswerEvaluationError("Promptfoo effective config description differs")
    if config.get("prompts") != ["{{taskPrompt}}"]:
        raise AnswerEvaluationError("Promptfoo effective prompt template differs")

    providers = config.get("providers")
    profiles = benchmark["profiles"]
    if not isinstance(providers, list) or [row.get("label") for row in providers if isinstance(row, dict)] != profiles:
        raise AnswerEvaluationError("Promptfoo effective provider order differs")
    normalized_profiles: list[dict[str, Any]] = []
    variant = benchmark["variant_id"]
    for profile, provider in zip(profiles, providers, strict=True):
        if not isinstance(provider, dict):
            raise AnswerEvaluationError(f"Promptfoo provider {profile} must be an object")
        provider_module = str(provider.get("id", "")).replace("\\", "/")
        if not provider_module.endswith("/providers/compare-matrix-provider.js"):
            raise AnswerEvaluationError(f"Promptfoo matrix provider differs for {profile}")
        matrix = exact_keys(
            provider.get("config"),
            {"provider_id", "profile_id", "skill_mode_id", "routes"},
            f"Promptfoo matrix provider {profile}",
        )
        if [matrix.get(key) for key in ("provider_id", "profile_id", "skill_mode_id")] != [
            profile,
            profile,
            profile,
        ]:
            raise AnswerEvaluationError(f"Promptfoo matrix identity differs for {profile}")
        routes = matrix["routes"]
        if not isinstance(routes, dict) or list(routes) != [variant]:
            raise AnswerEvaluationError(f"Promptfoo route set differs for {profile}")
        route = exact_keys(routes[variant], {"scenarioId", "provider"}, f"Promptfoo route {profile}")
        if route["scenarioId"] != f"{variant}-{profile}":
            raise AnswerEvaluationError(f"Promptfoo scenario differs for {profile}")
        inner = exact_keys(route["provider"], {"id", "label", "config"}, f"Promptfoo provider route {profile}")
        inner_module = str(inner["id"]).replace("\\", "/")
        if not inner_module.endswith("/providers/codex-system-provider.js"):
            raise AnswerEvaluationError(f"Promptfoo Codex provider differs for {profile}")
        if inner["label"] != "codex:command:gpt-5.6-luna":
            raise AnswerEvaluationError(f"Promptfoo Codex provider label differs for {profile}")
        agent = inner["config"]
        if not isinstance(agent, dict):
            raise AnswerEvaluationError(f"Promptfoo Codex config must be an object for {profile}")
        expected_agent = {
            "provider_id": "codex:command:gpt-5.6-luna",
            "execution_method": "command",
            "command_path": r"publication-runtime\run_codex.cmd",
            "model": "gpt-5.6-luna",
            "sandbox_mode": "workspace-write",
            "approval_policy": "never",
            "web_search_enabled": False,
            "network_access_enabled": False,
            "model_reasoning_effort": "medium",
            "env_passthrough": ["SEMANTIC_OKF_PYTHON", "SEMANTIC_OKF_HF_HUB_CACHE"],
            "strict_runtime_isolation": True,
        }
        if {key: agent.get(key) for key in expected_agent} != expected_agent:
            raise AnswerEvaluationError(f"Promptfoo Codex runtime differs for {profile}")
        working = _normalized_machine_path(agent.get("working_dir"), f"Promptfoo working_dir {profile}")
        if not working.endswith("/workspace"):
            raise AnswerEvaluationError(f"Promptfoo workspace path differs for {profile}")
        execution_root = working[: -len("/workspace")]
        cli_env = agent.get("cli_env")
        if not isinstance(cli_env, dict):
            raise AnswerEvaluationError(f"Promptfoo CLI environment differs for {profile}")
        required_env = {
            "HF_HUB_OFFLINE": "1",
            "TRANSFORMERS_OFFLINE": "1",
            "PYTHONDONTWRITEBYTECODE": "1",
            "SKILL_ARENA_ISOLATION": "strict",
        }
        if {key: cli_env.get(key) for key in required_env} != required_env:
            raise AnswerEvaluationError(f"Promptfoo offline/isolation environment differs for {profile}")
        bundle = _normalized_machine_path(cli_env.get("SEMANTIC_OKF_BUNDLE"), f"Promptfoo bundle {profile}")
        if bundle != f"{working}/knowledge":
            raise AnswerEvaluationError(f"Promptfoo bundle is outside its isolated workspace for {profile}")
        if _normalized_machine_path(
            cli_env.get("SKILL_ARENA_EXECUTION_ROOT"),
            f"Promptfoo execution root {profile}",
        ) != execution_root:
            raise AnswerEvaluationError(f"Promptfoo execution root differs for {profile}")

        skill_id = PROFILE_SKILLS.get(profile)
        if profile not in PROFILE_SKILLS:
            raise AnswerEvaluationError(f"Promptfoo profile skill contract is unknown: {profile}")
        expected_allowed = skill_id or ""
        if cli_env.get("SKILL_ARENA_ALLOWED_SKILLS") != expected_allowed:
            raise AnswerEvaluationError(f"Promptfoo allowed skill differs for {profile}")
        expected_preamble = (
            ""
            if skill_id is None
            else "Skill activation: explicitly invoke and follow these skills before solving the task: "
            f"${skill_id}."
        )
        if agent.get("prompt_preamble") != expected_preamble:
            raise AnswerEvaluationError(f"Promptfoo skill activation preamble differs for {profile}")

        codex_config = agent.get("codex_config")
        if not isinstance(codex_config, dict) or set(codex_config) != {"mcp_servers", "skills"}:
            raise AnswerEvaluationError(f"Promptfoo Codex tool config differs for {profile}")
        if {"mcp_servers": codex_config["mcp_servers"]} != EXPECTED_MCP_CONFIG:
            raise AnswerEvaluationError(f"Promptfoo MCP config differs for {profile}")
        skills = exact_keys(codex_config["skills"], {"config"}, f"Promptfoo skills config {profile}")
        installed = skills["config"]
        if skill_id is None:
            if installed != []:
                raise AnswerEvaluationError("Promptfoo knowledge-only control unexpectedly installs a skill")
        else:
            if not isinstance(installed, list) or len(installed) != 1:
                raise AnswerEvaluationError(f"Promptfoo installed skill count differs for {profile}")
            skill = exact_keys(installed[0], {"path", "enabled"}, f"Promptfoo installed skill {profile}")
            skill_path = _normalized_machine_path(skill["path"], f"Promptfoo installed skill path {profile}")
            expected_suffix = f"/codex-home/skills/{skill_id}/SKILL.md"
            if skill["enabled"] is not True or skill_path != f"{execution_root}{expected_suffix}":
                raise AnswerEvaluationError(f"Promptfoo installed skill differs for {profile}")
        normalized_profiles.append(
            {
                "profile_id": profile,
                "skill_id": skill_id,
                "agent": expected_agent,
                "offline_env": required_env,
                "mcp": EXPECTED_MCP_CONFIG["mcp_servers"],
                "prompt_preamble_sha256": hashlib.sha256(expected_preamble.encode("utf-8")).hexdigest(),
            }
        )

    expected_prompts = _expected_task_prompts(contract)
    tests = config.get("tests")
    if not isinstance(tests, list) or len(tests) != len(expected_prompts):
        raise AnswerEvaluationError("Promptfoo effective task count differs")
    normalized_tasks: list[dict[str, Any]] = []
    for question_id, test in zip(benchmark["question_ids"], tests, strict=True):
        if not isinstance(test, dict):
            raise AnswerEvaluationError(f"Promptfoo task must be an object for {question_id}")
        variables = test.get("vars")
        metadata = test.get("metadata")
        assertions = test.get("assert")
        if not isinstance(variables, dict) or not isinstance(metadata, dict) or not isinstance(assertions, list):
            raise AnswerEvaluationError(f"Promptfoo task contract differs for {question_id}")
        prompt = variables.get("taskPrompt")
        if prompt != expected_prompts[question_id]:
            raise AnswerEvaluationError(f"Promptfoo task prompt differs for {question_id}")
        question = ground_truth[question_id].get("question")
        if not isinstance(question, str) or f"Question: {question}\n" not in prompt:
            raise AnswerEvaluationError(f"Promptfoo task question differs from ground truth for {question_id}")
        if variables.get("variantId") != variant or metadata.get("benchmarkId") != benchmark["id"]:
            raise AnswerEvaluationError(f"Promptfoo task benchmark/variant differs for {question_id}")
        if metadata.get("promptId") != question_id or metadata.get("variantId") != variant:
            raise AnswerEvaluationError(f"Promptfoo task identity differs for {question_id}")
        if metadata.get("rowId") != f"{variant}:{question_id}":
            raise AnswerEvaluationError(f"Promptfoo task row identity differs for {question_id}")
        metrics = [item.get("metric") for item in assertions if isinstance(item, dict)]
        if metrics != PROMPTFOO_ASSERTION_METRICS:
            raise AnswerEvaluationError(f"Promptfoo assertion metrics differ for {question_id}")
        normalized_tasks.append(
            {
                "question_id": question_id,
                "task_prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
                "assertion_metrics": metrics,
            }
        )
    normalized = {
        "description": config["description"],
        "prompt_template": config["prompts"],
        "variant_id": variant,
        "profiles": normalized_profiles,
        "tasks": normalized_tasks,
    }
    return hashlib.sha256(canonical_json(normalized).encode("utf-8")).hexdigest()


def _raw_rows(path: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    report = load_json(path)
    results = report.get("results")
    if not isinstance(results, dict) or not isinstance(results.get("results"), list):
        raise AnswerEvaluationError("Promptfoo report has no results.results array")
    return report, results["results"]


def _cell_identity(row: Mapping[str, Any], contract: Mapping[str, Any]) -> tuple[str, str, str, str]:
    provider = row.get("provider")
    metadata = row.get("metadata")
    variables = row.get("vars")
    if not isinstance(provider, dict) or not isinstance(metadata, dict) or not isinstance(variables, dict):
        raise AnswerEvaluationError("Promptfoo row lacks provider, metadata, or vars objects")
    profile = metadata.get("profileId")
    question = metadata.get("promptId")
    variant = metadata.get("variantId")
    benchmark = metadata.get("benchmarkId")
    expected = contract["benchmark"]
    if benchmark != expected["id"]:
        raise AnswerEvaluationError(f"Promptfoo row benchmark differs: {benchmark!r}")
    if profile not in expected["profiles"]:
        raise AnswerEvaluationError(f"Promptfoo row profile is unexpected: {profile!r}")
    if question not in expected["question_ids"]:
        raise AnswerEvaluationError(f"Promptfoo row question is unexpected: {question!r}")
    if variant != expected["variant_id"]:
        raise AnswerEvaluationError(f"Promptfoo row variant differs: {variant!r}")
    if provider.get("id") != profile or variables.get("variantId") != variant:
        raise AnswerEvaluationError("Promptfoo provider/vars identity disagrees with row metadata")
    if metadata.get("scenarioId") != f"{variant}-{profile}":
        raise AnswerEvaluationError("Promptfoo scenario identity differs")
    if metadata.get("rowId") != f"{variant}:{question}":
        raise AnswerEvaluationError("Promptfoo rowId identity differs")
    return str(profile), str(variant), str(question), str(benchmark)


def _validate_promptfoo_execution_state(row: Mapping[str, Any], row_id: str) -> None:
    """Separate a completed agent turn from an adapter/runtime failure.

    The Codex command adapter copies recoverable tool-router diagnostics into
    ``response.metadata.stderr`` even when the turn completes and returns a
    usable answer.  Those diagnostics are part of the observed agent behavior,
    not an adapter failure.  Promptfoo reports terminal provider failures in
    ``response.error`` (or by omitting the output), so those remain fail-closed.
    """

    response = row.get("response")
    if not isinstance(response, dict):
        raise AnswerEvaluationError(f"Promptfoo row {row_id} has no response object")
    response_error = response.get("error")
    metadata = response.get("metadata")
    if metadata is not None and not isinstance(metadata, Mapping):
        raise AnswerEvaluationError(f"Promptfoo row {row_id} has malformed response metadata")
    stderr = metadata.get("stderr") if isinstance(metadata, Mapping) else None
    if response_error not in (None, ""):
        raise AnswerEvaluationError(f"Promptfoo row {row_id} is an adapter/runtime failure")
    if stderr is not None and not isinstance(stderr, str):
        raise AnswerEvaluationError(f"Promptfoo row {row_id} has malformed stderr metadata")

    output = response.get("output")
    if not isinstance(output, str) or not output.strip():
        raise AnswerEvaluationError(
            f"Promptfoo row {row_id} has no model output; refusing an adapter-failure or partial run"
        )

    row_error = row.get("error")
    row_success = row.get("success")
    if row_success is not None and not isinstance(row_success, bool):
        raise AnswerEvaluationError(f"Promptfoo row {row_id} has a non-boolean success state")
    if row_error in (None, ""):
        if row_success is False:
            raise AnswerEvaluationError(f"Promptfoo row {row_id} has an unclassified false state")
        return
    if not isinstance(row_error, str):
        raise AnswerEvaluationError(f"Promptfoo row {row_id} has a non-string row error")

    # Promptfoo stores the reason for a failed assertion in the top-level
    # ``error`` field even though the provider completed and returned an answer.
    # Accept that answer outcome only when the grading object proves the error is
    # an assertion result. The independent evaluator never reuses this score.
    grading = row.get("gradingResult")
    if not isinstance(grading, dict):
        raise AnswerEvaluationError(f"Promptfoo row {row_id} has an unclassified row error")
    components = grading.get("componentResults")
    matching_failure = (
        isinstance(components, list)
        and any(
            isinstance(component, dict)
            and component.get("pass") is False
            and component.get("reason") == row_error
            for component in components
        )
    )
    if (
        row_success is True
        or grading.get("pass") is not False
        or grading.get("reason") != row_error
        or not matching_failure
    ):
        raise AnswerEvaluationError(f"Promptfoo row {row_id} has an unclassified row error")


def prepare_answers(
    promptfoo_path: Path,
    ledger: BundleLedger,
    ground_truth: Mapping[str, Mapping[str, Any]],
    contract: Mapping[str, Any],
    contract_binding: Mapping[str, str],
) -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
    """Parse exactly 90 live rows and return mechanical, manifest, and blinded tasks."""

    exact_keys(contract_binding, {"path", "sha256"}, "contract binding")
    if not isinstance(contract_binding["path"], str) or not _valid_hash(contract_binding["sha256"]):
        raise AnswerEvaluationError("contract binding is invalid")
    promptfoo_path = promptfoo_path.resolve(strict=True)
    try:
        promptfoo_path.relative_to(REPO_ROOT.resolve(strict=True))
    except ValueError as exc:
        raise AnswerEvaluationError("Promptfoo report must remain inside the repository") from exc
    report, rows = _raw_rows(promptfoo_path)
    effective_config_sha256 = _validate_promptfoo_effective_config(report, contract, ground_truth)
    expected = contract["benchmark"]
    if len(rows) != expected["total_answers"]:
        raise AnswerEvaluationError(
            f"expected exactly {expected['total_answers']} Promptfoo rows, found {len(rows)}"
        )

    groups: dict[tuple[str, str, str], list[tuple[str, dict[str, Any]]]] = defaultdict(list)
    raw_ids: set[str] = set()
    for row in rows:
        if not isinstance(row, dict):
            raise AnswerEvaluationError("Promptfoo result rows must be objects")
        row_id = row.get("id")
        if not isinstance(row_id, str) or not row_id or row_id in raw_ids:
            raise AnswerEvaluationError(f"Promptfoo row IDs must be unique nonempty strings: {row_id!r}")
        raw_ids.add(row_id)
        profile, variant, question, _ = _cell_identity(row, contract)
        _validate_promptfoo_execution_state(row, row_id)
        groups[(profile, variant, question)].append((row_id, row))

    expected_cells = {
        (profile, expected["variant_id"], question)
        for profile in expected["profiles"]
        for question in expected["question_ids"]
    }
    if set(groups) != expected_cells:
        missing = sorted(expected_cells - set(groups))
        unknown = sorted(set(groups) - expected_cells)
        raise AnswerEvaluationError(f"Promptfoo cells differ; missing={missing}, unknown={unknown}")
    repetitions = expected["repetitions_per_cell"]
    wrong_counts = {"|".join(key): len(value) for key, value in groups.items() if len(value) != repetitions}
    if wrong_counts:
        raise AnswerEvaluationError(f"Promptfoo repetition counts differ: {wrong_counts}")

    promptfoo_sha = sha256(promptfoo_path)
    mechanical_rows: list[dict[str, Any]] = []
    mapping: list[dict[str, Any]] = []
    tasks: list[dict[str, Any]] = []
    for profile in expected["profiles"]:
        for question in expected["question_ids"]:
            cell = sorted(groups[(profile, expected["variant_id"], question)], key=lambda item: item[0])
            for repetition, (row_id, row) in enumerate(cell, start=1):
                output_text = row["response"]["output"]
                output_sha = hashlib.sha256(output_text.encode("utf-8")).hexdigest()
                output, parse_status = _strict_output(output_text)
                answer = output.get("answer") if isinstance(output, dict) else None
                metrics, counts, evidence_failures = score_mechanical_answer(
                    output, question, ground_truth[question], ledger, contract
                )
                answer_id = hashlib.sha256(
                    f"{promptfoo_sha}\0{row_id}\0{profile}\0{question}\0{repetition}\0{output_sha}".encode("utf-8")
                ).hexdigest()[:32]
                raw_score = row.get("score")
                promptfoo_score = float(raw_score) if isinstance(raw_score, (int, float)) and not isinstance(raw_score, bool) else 0.0
                if not math.isfinite(promptfoo_score):
                    raise AnswerEvaluationError(f"Promptfoo row {row_id} has a non-finite score")
                mechanical_rows.append(
                    {
                        "answer_id": answer_id,
                        "profile_id": profile,
                        "variant_id": expected["variant_id"],
                        "question_id": question,
                        "repetition": repetition,
                        "row_id": row_id,
                        "output_sha256": output_sha,
                        "parse_status": parse_status,
                        "promptfoo_full_pass": float(promptfoo_score == 1.0),
                        "metrics": metrics,
                        "counts": counts,
                        "evidence_failure_reasons": evidence_failures,
                    }
                )
                mapping.append(
                    {
                        "answer_id": answer_id,
                        "profile_id": profile,
                        "variant_id": expected["variant_id"],
                        "question_id": question,
                        "repetition": repetition,
                        "row_id": row_id,
                        "output_sha256": output_sha,
                    }
                )
                reviewed = ground_truth[question]
                tasks.append(
                    {
                        "schema_version": REVIEW_TASK_SCHEMA,
                        "answer_id": answer_id,
                        "question": reviewed["question"],
                        "ground_truth": {
                            "answer_claims": reviewed["ground_truth"]["answer_claims"],
                            "derivation": reviewed["ground_truth"]["derivation"],
                            "important_negatives": reviewed["ground_truth"]["important_negatives"],
                            "acceptable_variants": reviewed["ground_truth"]["acceptable_variants"],
                            "required_paper_ids": reviewed["ground_truth"]["required_paper_ids"],
                        },
                        "candidate": answer if isinstance(answer, dict) else None,
                        "candidate_support_records": _support_context(answer, ledger),
                    }
                )

    if len({row["answer_id"] for row in mechanical_rows}) != expected["total_answers"]:
        raise AnswerEvaluationError("prepared answer identities are not unique")
    tasks.sort(key=lambda task: hashlib.sha256(task["answer_id"].encode("utf-8")).hexdigest())
    task_text = "".join(canonical_json(task) + "\n" for task in tasks)
    task_sha = hashlib.sha256(task_text.encode("utf-8")).hexdigest()
    input_binding = {
        "path": display_path(promptfoo_path),
        "sha256": promptfoo_sha,
        "promptfoo_eval_id": report.get("evalId") if isinstance(report.get("evalId"), str) else None,
        "effective_config_sha256": effective_config_sha256,
    }
    ground_truth_binding = {
        "path": contract["ground_truth"]["path"],
        "sha256": contract["ground_truth"]["sha256"],
    }
    benchmark_binding = {
        "id": expected["id"],
        "profiles": expected["profiles"],
        "variant_id": expected["variant_id"],
        "question_ids": expected["question_ids"],
        "repetitions_per_cell": repetitions,
        "answer_count": len(mechanical_rows),
    }
    manifest = {
        "schema_version": REVIEW_MANIFEST_SCHEMA,
        "blinded": True,
        "answer_count": len(mapping),
        "contract": dict(contract_binding),
        "benchmark": benchmark_binding,
        "input": input_binding,
        "bundle": ledger.identity,
        "ground_truth": ground_truth_binding,
        "implementation": preparation_implementation(),
        "task_sha256": task_sha,
        "mapping": mapping,
    }
    mechanical = {
        "schema_version": MECHANICAL_SCHEMA,
        "status": "pass",
        "contract": dict(contract_binding),
        "benchmark": benchmark_binding,
        "bundle": ledger.identity,
        "input": input_binding,
        "ground_truth": ground_truth_binding,
        "implementation": preparation_implementation(),
        "metric_contract": {
            "response_contract": "independent exact ordered JSON response schema and word-bound validation",
            "evidence_validity": "exact reviewed ledger, concept, source, paper, and cited-page binding per evidence item",
            "grounding": "supporting claim references represented by independently valid evidence items",
            "exact_atomic_evidence_coverage": "curated atomic claim identity represented in support and valid evidence",
            "required_paper_coverage": "required paper identity represented in paper_ids and citations",
            "required_source_coverage": "required reviewed-claim and paper source identities represented",
            "exact_negative_evidence_coverage": "curated important-negative identity represented in support and valid evidence",
        },
        "answer_count": len(mechanical_rows),
        "task_sha256": task_sha,
        "answers": mechanical_rows,
    }
    return mechanical, manifest, tasks


def task_text(tasks: Sequence[Mapping[str, Any]]) -> str:
    """Return the canonical JSONL encoding of blinded review tasks."""

    return "".join(canonical_json(task) + "\n" for task in tasks)


def _expected_benchmark_binding(contract: Mapping[str, Any]) -> dict[str, Any]:
    benchmark = contract["benchmark"]
    return {
        "id": benchmark["id"],
        "profiles": benchmark["profiles"],
        "variant_id": benchmark["variant_id"],
        "question_ids": benchmark["question_ids"],
        "repetitions_per_cell": benchmark["repetitions_per_cell"],
        "answer_count": benchmark["total_answers"],
    }


def _validate_contract_binding(binding: Any, contract_path: Path) -> None:
    exact_keys(binding, {"path", "sha256"}, "prepared contract binding")
    if binding != {"path": display_path(contract_path), "sha256": sha256(contract_path)}:
        raise AnswerEvaluationError("prepared contract binding differs from the live contract")


def validate_preparation(
    input_dir: Path,
    contract: Mapping[str, Any],
    contract_path: Path,
) -> tuple[list[dict[str, Any]], dict[str, Any], dict[str, Any]]:
    """Validate the blinded tasks, private mapping, and mechanical scores as one unit."""

    input_dir = input_dir.resolve(strict=True)
    task_path = input_dir / "review-tasks.jsonl"
    manifest_path = input_dir / "review-manifest.json"
    mechanical_path = input_dir / "mechanical-results.json"
    tasks = load_jsonl(task_path)
    manifest = load_json(manifest_path)
    mechanical = load_json(mechanical_path)
    exact_keys(
        manifest,
        {
            "schema_version",
            "blinded",
            "answer_count",
            "contract",
            "benchmark",
            "input",
            "bundle",
            "ground_truth",
            "implementation",
            "task_sha256",
            "mapping",
        },
        "review manifest",
    )
    if manifest["schema_version"] != REVIEW_MANIFEST_SCHEMA or manifest["blinded"] is not True:
        raise AnswerEvaluationError("review manifest schema or blinding status differs")
    total = contract["benchmark"]["total_answers"]
    if manifest["answer_count"] != total:
        raise AnswerEvaluationError("review manifest answer count differs")
    _validate_contract_binding(manifest["contract"], contract_path)
    if manifest["benchmark"] != _expected_benchmark_binding(contract):
        raise AnswerEvaluationError("review manifest benchmark binding differs")
    expected_bundle = contract["bundle"]
    if manifest["bundle"] != {
        "run_id": expected_bundle["run_id"],
        "repository_path": expected_bundle["repository_path"],
        "file_count": expected_bundle["file_count"],
        "tree_sha256": expected_bundle["tree_sha256"],
        "ensemble_index_sha256": expected_bundle["ensemble_index_sha256"],
        "ensemble_plan_sha256": expected_bundle["ensemble_plan_sha256"],
        "core_tree_sha256": expected_bundle["core_tree_sha256"],
        "records_sha256": expected_bundle["records_sha256"],
        "record_count": expected_bundle["record_count"],
        "source_manifest_sha256": expected_bundle["source_manifest_sha256"],
    }:
        raise AnswerEvaluationError("review manifest bundle binding differs")
    if manifest["ground_truth"] != {
        "path": contract["ground_truth"]["path"],
        "sha256": contract["ground_truth"]["sha256"],
    }:
        raise AnswerEvaluationError("review manifest ground-truth binding differs")
    if manifest["implementation"] != preparation_implementation():
        raise AnswerEvaluationError("review manifest implementation binding differs")
    exact_keys(
        manifest["input"],
        {"path", "sha256", "promptfoo_eval_id", "effective_config_sha256"},
        "Promptfoo input binding",
    )
    raw_path = _repo_path(manifest["input"]["path"], "Promptfoo input path")
    if not _valid_hash(manifest["input"]["sha256"]) or sha256(raw_path) != manifest["input"]["sha256"]:
        raise AnswerEvaluationError("Promptfoo input hash differs from the prepared binding")
    if not _valid_hash(manifest["input"]["effective_config_sha256"]):
        raise AnswerEvaluationError("Promptfoo effective config hash differs from the prepared binding")
    actual_task_hash = hashlib.sha256(task_path.read_bytes()).hexdigest()
    if manifest["task_sha256"] != actual_task_hash or task_text(tasks).encode("utf-8") != task_path.read_bytes():
        raise AnswerEvaluationError("review task bytes differ from their canonical manifest binding")
    if len(tasks) != total:
        raise AnswerEvaluationError("review task count differs")
    task_ids: list[str] = []
    for task in tasks:
        exact_keys(
            task,
            {
                "schema_version",
                "answer_id",
                "question",
                "ground_truth",
                "candidate",
                "candidate_support_records",
            },
            "review task",
        )
        if task["schema_version"] != REVIEW_TASK_SCHEMA or not isinstance(task["answer_id"], str):
            raise AnswerEvaluationError("review task schema or identity differs")
        if not isinstance(task["question"], str) or not isinstance(task["candidate_support_records"], list):
            raise AnswerEvaluationError("review task question or support records differ")
        exact_keys(
            task["ground_truth"],
            {
                "answer_claims",
                "derivation",
                "important_negatives",
                "acceptable_variants",
                "required_paper_ids",
            },
            f"review task ground truth {task['answer_id']}",
        )
        task_ids.append(task["answer_id"])
    if len(task_ids) != len(set(task_ids)):
        raise AnswerEvaluationError("review task answer IDs are duplicated")

    mapping = manifest["mapping"]
    if not isinstance(mapping, list) or len(mapping) != total:
        raise AnswerEvaluationError("review manifest mapping count differs")
    mapping_ids: list[str] = []
    cells: set[tuple[str, str, str, int]] = set()
    for row in mapping:
        exact_keys(
            row,
            {
                "answer_id",
                "profile_id",
                "variant_id",
                "question_id",
                "repetition",
                "row_id",
                "output_sha256",
            },
            "review manifest mapping row",
        )
        if row["profile_id"] not in contract["benchmark"]["profiles"]:
            raise AnswerEvaluationError("review manifest mapping profile differs")
        if row["variant_id"] != contract["benchmark"]["variant_id"]:
            raise AnswerEvaluationError("review manifest mapping variant differs")
        if row["question_id"] not in contract["benchmark"]["question_ids"]:
            raise AnswerEvaluationError("review manifest mapping question differs")
        if row["repetition"] not in range(1, contract["benchmark"]["repetitions_per_cell"] + 1):
            raise AnswerEvaluationError("review manifest mapping repetition differs")
        if not isinstance(row["row_id"], str) or not _valid_hash(row["output_sha256"]):
            raise AnswerEvaluationError("review manifest row or output identity differs")
        cell = (row["profile_id"], row["variant_id"], row["question_id"], row["repetition"])
        if cell in cells:
            raise AnswerEvaluationError(f"duplicate prepared answer cell: {cell}")
        cells.add(cell)
        mapping_ids.append(row["answer_id"])
    if set(mapping_ids) != set(task_ids) or len(mapping_ids) != len(set(mapping_ids)):
        raise AnswerEvaluationError("review mapping identities differ from blinded tasks")
    task_by_id = {task["answer_id"]: task for task in tasks}
    prepared_truth: dict[str, dict[str, str]] = {}
    for row in mapping:
        question_id = row["question_id"]
        question = task_by_id[row["answer_id"]]["question"]
        existing = prepared_truth.get(question_id)
        if existing is not None and existing["question"] != question:
            raise AnswerEvaluationError("review tasks disagree on the frozen question text")
        prepared_truth[question_id] = {"question": question}
    if list(prepared_truth) != contract["benchmark"]["question_ids"]:
        # Mapping is profile-major, so insertion order repeats questions. Compare
        # identity sets here and retain contract order for config validation.
        if set(prepared_truth) != set(contract["benchmark"]["question_ids"]):
            raise AnswerEvaluationError("review task question identities differ")
        prepared_truth = {
            question_id: prepared_truth[question_id]
            for question_id in contract["benchmark"]["question_ids"]
        }
    effective_config_sha256 = _validate_promptfoo_effective_config(
        load_json(raw_path), contract, prepared_truth
    )
    if manifest["input"]["effective_config_sha256"] != effective_config_sha256:
        raise AnswerEvaluationError("Promptfoo effective config hash differs from live input")

    exact_keys(
        mechanical,
        {
            "schema_version",
            "status",
            "contract",
            "benchmark",
            "bundle",
            "input",
            "ground_truth",
            "implementation",
            "metric_contract",
            "answer_count",
            "task_sha256",
            "answers",
        },
        "mechanical results",
    )
    if mechanical["schema_version"] != MECHANICAL_SCHEMA or mechanical["status"] != "pass":
        raise AnswerEvaluationError("mechanical results schema or status differs")
    for key in (
        "contract",
        "benchmark",
        "bundle",
        "input",
        "ground_truth",
        "implementation",
        "answer_count",
        "task_sha256",
    ):
        if mechanical[key] != manifest[key]:
            raise AnswerEvaluationError(f"mechanical results {key} differs from the review manifest")
    if set(mechanical["metric_contract"]) != set(MECHANICAL_METRICS):
        raise AnswerEvaluationError("mechanical metric contract differs")
    answers = mechanical["answers"]
    if not isinstance(answers, list) or len(answers) != total:
        raise AnswerEvaluationError("mechanical answer count differs")
    answer_by_id: dict[str, dict[str, Any]] = {}
    mapping_by_id = {row["answer_id"]: row for row in mapping}
    for row in answers:
        exact_keys(
            row,
            {
                "answer_id",
                "profile_id",
                "variant_id",
                "question_id",
                "repetition",
                "row_id",
                "output_sha256",
                "parse_status",
                "promptfoo_full_pass",
                "metrics",
                "counts",
                "evidence_failure_reasons",
            },
            "mechanical answer row",
        )
        answer_id = row["answer_id"]
        if answer_id in answer_by_id or answer_id not in mapping_by_id:
            raise AnswerEvaluationError("mechanical answer identity is duplicate or unknown")
        for key in (
            "answer_id",
            "profile_id",
            "variant_id",
            "question_id",
            "repetition",
            "row_id",
            "output_sha256",
        ):
            if row[key] != mapping_by_id[answer_id][key]:
                raise AnswerEvaluationError(f"mechanical answer {answer_id} differs from its mapping")
        if row["parse_status"] not in {"object", "invalid-json", "non-object-json"}:
            raise AnswerEvaluationError("mechanical parse status differs")
        if row["promptfoo_full_pass"] not in {0.0, 1.0}:
            raise AnswerEvaluationError("mechanical Promptfoo pass value differs")
        if set(row["metrics"]) != set(MECHANICAL_METRICS):
            raise AnswerEvaluationError("mechanical answer metric set differs")
        if any(
            not isinstance(value, (int, float))
            or isinstance(value, bool)
            or not math.isfinite(float(value))
            or not 0.0 <= float(value) <= 1.0
            for value in row["metrics"].values()
        ):
            raise AnswerEvaluationError("mechanical answer metric value differs")
        if not isinstance(row["counts"], dict) or any(
            not isinstance(value, int) or isinstance(value, bool) or value < 0
            for value in row["counts"].values()
        ):
            raise AnswerEvaluationError("mechanical answer counts differ")
        if not _string_list(row["evidence_failure_reasons"]):
            if row["evidence_failure_reasons"] != []:
                raise AnswerEvaluationError("mechanical evidence failure reasons differ")
        answer_by_id[answer_id] = row
    return tasks, manifest, mechanical


def validate_review(review: Any, task: Mapping[str, Any], contract: Mapping[str, Any]) -> dict[str, Any]:
    """Validate one fixed-rubric blinded semantic review."""

    exact_keys(review, {"answer_id", "claim_fidelity", "atomic_scores", "negative_scores", "note"}, "review")
    if review["answer_id"] != task["answer_id"] or not isinstance(review["note"], str):
        raise AnswerEvaluationError(f"review identity or note differs for {task['answer_id']}")
    if len(review["note"].split()) > contract["review"]["maximum_note_words"]:
        raise AnswerEvaluationError(f"review note is too long for {task['answer_id']}")
    candidate = task.get("candidate")
    claims = candidate.get("claims", []) if isinstance(candidate, dict) and isinstance(candidate.get("claims"), list) else []
    fidelity = review["claim_fidelity"]
    if not isinstance(fidelity, list) or len(fidelity) != len(claims):
        raise AnswerEvaluationError(f"review claim count differs for {task['answer_id']}")
    allowed = set(contract["review"]["score_values"])
    for index, item in enumerate(fidelity):
        exact_keys(item, {"index", "score"}, f"review claim {task['answer_id']}:{index}")
        if item["index"] != index or isinstance(item["score"], bool) or item["score"] not in allowed:
            raise AnswerEvaluationError(f"review claim score differs for {task['answer_id']}")
    atom_ids = {item["id"] for item in task["ground_truth"]["answer_claims"]}
    negative_ids = {item["id"] for item in task["ground_truth"]["important_negatives"]}
    if not isinstance(review["atomic_scores"], dict) or set(review["atomic_scores"]) != atom_ids:
        raise AnswerEvaluationError(f"review atomic identities differ for {task['answer_id']}")
    if not isinstance(review["negative_scores"], dict) or set(review["negative_scores"]) != negative_ids:
        raise AnswerEvaluationError(f"review negative identities differ for {task['answer_id']}")
    if any(isinstance(value, bool) or value not in allowed for value in review["atomic_scores"].values()):
        raise AnswerEvaluationError(f"review atomic scores differ for {task['answer_id']}")
    if any(isinstance(value, bool) or value not in allowed for value in review["negative_scores"].values()):
        raise AnswerEvaluationError(f"review negative scores differ for {task['answer_id']}")
    return review


def validate_review_report(
    report: Mapping[str, Any],
    tasks: Sequence[Mapping[str, Any]],
    manifest: Mapping[str, Any],
    contract: Mapping[str, Any],
) -> dict[str, Any]:
    """Validate one complete 90-answer blinded review report."""

    exact_keys(
        report,
        {
            "schema_version",
            "model",
            "blinded",
            "score_values",
            "task_sha256",
            "review_count",
            "implementation",
            "reviews",
        },
        "review report",
    )
    expected = contract["review"]
    if (
        report["schema_version"] != expected["schema_version"]
        or report["model"] != expected["model"]
        or report["blinded"] is not True
        or report["score_values"] != expected["score_values"]
        or report["task_sha256"] != manifest["task_sha256"]
        or report["review_count"] != len(tasks)
    ):
        raise AnswerEvaluationError("review report header differs from the fixed contract")
    if report["implementation"] != {"reviewer": _implementation_binding(REVIEWER)}:
        raise AnswerEvaluationError("review report implementation binding differs")
    reviews = report["reviews"]
    if not isinstance(reviews, list) or len(reviews) != len(tasks):
        raise AnswerEvaluationError("review report count differs")
    validated = [validate_review(review, task, contract) for review, task in zip(reviews, tasks, strict=True)]
    if [review["answer_id"] for review in validated] != [task["answer_id"] for task in tasks]:
        raise AnswerEvaluationError("review report identities or order differ from blinded tasks")
    return dict(report)
