#!/usr/bin/env python3
"""Audit frozen hard-question expected IDs against authoritative Semantic OKF evidence."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
from collections import Counter
from pathlib import Path
from types import ModuleType
from typing import Any

import yaml


SCHEMA_VERSION = "semantic-okf-expected-id-audit/1.0"
EXPECTED_QUESTION_IDS = [f"q{number:03d}" for number in range(31, 41)]
DEFAULT_CONFIGS = (
    "evaluations/semantic-okf-adaptive/skill-arena/adaptive-hard10.yaml",
    "evaluations/semantic-okf-adaptive-evolution/skill-arena/g000-candidate07-hard10.yaml",
    "evaluations/semantic-okf-adaptive-evolution/skill-arena/g001-candidate10-hard10.yaml",
    "evaluations/semantic-okf-adaptive-evolution/skill-arena/g002-candidate11-hard10.yaml",
)
FULL_BINDING_BENCHMARK_IDS = {"semantic-okf-ensemble-hard10-three-arm"}

# These are reviewer judgments about how the frozen atomic statement relates to its
# reviewed claim record. All unlisted atomic answers are direct faithful paraphrases.
# The benchmark remains untouched; these annotations make the audit boundary explicit.
SPECIAL_ATOMIC_REVIEWS: dict[str, dict[str, str]] = {
    "q031-a4": {
        "relationship": "bounded-derivation-anchor",
        "note": (
            "The reviewed records report correction in both directions. The conclusion that neither "
            "route is universally dominant is a bounded contrast rather than a literal sentence."
        ),
    },
    "q035-a4": {
        "relationship": "bounded-derivation-anchor",
        "note": (
            "The reviewed record identifies examples, quotations, and citations as details graph "
            "extraction should retain better. Framing that as possible loss from high-level community "
            "summaries is a cautious synthesis."
        ),
    },
    "q036-a4": {
        "relationship": "bounded-derivation-anchor",
        "note": (
            "The record directly supports the contamination concern. Independently verifying a "
            "reference answer is the benchmark-design consequence drawn from that observation."
        ),
    },
    "q038-a4": {
        "relationship": "page-supported-detail-anchor",
        "note": (
            "The reviewed interpretation names DFS traversal; its cited paper page specifies a maximum "
            "depth of five, so the word 'bounded' is supported by the locator rather than repeated in "
            "the interpretation."
        ),
    },
}


class AuditError(RuntimeError):
    """Raised when a frozen expected ID cannot be reproduced or aligned."""


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AuditError(f"expected a JSON object: {path}")
    return value


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise AuditError(f"expected a JSON object at {path}:{line_number}")
        rows.append(value)
    return rows


def load_module(name: str, path: Path) -> ModuleType:
    specification = importlib.util.spec_from_file_location(name, path)
    if specification is None or specification.loader is None:
        raise AuditError(f"cannot load Python module: {path}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


def resolve_repo_path(repo_root: Path, value: str) -> Path:
    if not value or "\\" in value:
        raise AuditError(f"invalid portable path: {value!r}")
    result = (repo_root / value).resolve()
    try:
        result.relative_to(repo_root)
    except ValueError as exc:
        raise AuditError(f"path escapes the repository: {value}") from exc
    return result


def parse_json_constant(script: str, name: str) -> Any:
    match = re.search(rf"const\s+{re.escape(name)}\s*=\s*(.*?);", script, re.DOTALL)
    if not match:
        raise AuditError(f"JavaScript assertion is missing const {name}")
    try:
        return json.loads(match.group(1))
    except json.JSONDecodeError as exc:
        raise AuditError(f"const {name} is not strict JSON: {exc}") from exc


def normalize_allowed(value: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        claim_id: {
            "concept_path": fields["concept_path"],
            "locators": sorted(fields["locators"]),
            "paper_id": fields["paper_id"],
            "source_path": fields["source_path"],
        }
        for claim_id, fields in sorted(value.items())
    }


def normalize_option_sets(value: Any, label: str) -> list[list[str]]:
    """Canonicalize OR-option membership while preserving answer-group order."""

    if not isinstance(value, list):
        raise AuditError(f"{label} must be an array of option arrays")
    normalized: list[list[str]] = []
    for index, options in enumerate(value):
        if (
            not isinstance(options, list)
            or not options
            or any(not isinstance(item, str) or not item for item in options)
        ):
            raise AuditError(f"{label}[{index}] must be a nonempty string array")
        normalized.append(sorted(set(options)))
    return normalized


def expected_allowed(
    evidence: list[dict[str, Any]], bindings: dict[str, dict[str, Any]]
) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for item in evidence:
        claim_id = item["claim_id"]
        binding = bindings[claim_id]
        result[claim_id] = {
            "concept_path": binding["concept_path"],
            "locators": sorted(binding["locator_tokens"]),
            "paper_id": binding["paper_id"],
            "source_path": binding["source_path"],
        }
    return dict(sorted(result.items()))


def expected_all_bindings(
    bindings: dict[str, dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    """Return the closed evidence-validity universe for definitive configs."""

    return {
        claim_id: {
            "concept_path": binding["concept_path"],
            "locators": sorted(binding["locator_tokens"]),
            "paper_id": binding["paper_id"],
            "source_path": binding["source_path"],
        }
        for claim_id, binding in sorted(bindings.items())
    }


def audit_config(
    repo_root: Path,
    path: Path,
    ground_truth_by_id: dict[str, dict[str, Any]],
    bindings: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    config = yaml.safe_load(path.read_text(encoding="utf-8"))
    prompts = config.get("task", {}).get("prompts") if isinstance(config, dict) else None
    if not isinstance(prompts, list):
        raise AuditError(f"config has no task prompts: {path}")
    if [prompt.get("id") for prompt in prompts] != list(ground_truth_by_id):
        raise AuditError(f"config question order differs from frozen ground truth: {path}")

    benchmark = config.get("benchmark", {})
    benchmark_id = benchmark.get("id") if isinstance(benchmark, dict) else None
    full_binding_scope = benchmark_id in FULL_BINDING_BENCHMARK_IDS
    binding_scope = "full-answer-binding-universe" if full_binding_scope else "question-authoritative-evidence"

    cases: list[dict[str, Any]] = []
    for prompt in prompts:
        question_id = prompt["id"]
        ground_truth_record = ground_truth_by_id[question_id]
        contract = ground_truth_record["ground_truth"]
        assertions = prompt.get("evaluation", {}).get("assertions")
        if not isinstance(assertions, list):
            raise AuditError(f"config prompt has no assertions: {path}:{question_id}")
        by_metric = {item.get("metric"): item.get("value") for item in assertions}
        required_metrics = {
            "response-contract",
            "evidence-validity",
            "atomic-answer-completeness",
            "important-negative-coverage",
        }
        if set(by_metric) != required_metrics:
            raise AuditError(f"assertion metric set changed: {path}:{question_id}")

        evidence_script = by_metric["evidence-validity"]
        atomic_script = by_metric["atomic-answer-completeness"]
        negative_script = by_metric["important-negative-coverage"]
        if not all(isinstance(item, str) for item in (evidence_script, atomic_script, negative_script)):
            raise AuditError(f"assertion code is not a string: {path}:{question_id}")

        observed_allowed = normalize_allowed(parse_json_constant(evidence_script, "allowed"))
        wanted_allowed = (
            expected_all_bindings(bindings)
            if full_binding_scope
            else expected_allowed(ground_truth_record["authoritative_evidence"], bindings)
        )
        if observed_allowed != wanted_allowed:
            raise AuditError(f"allowed claim bindings differ from authoritative evidence: {path}:{question_id}")

        observed_papers = parse_json_constant(atomic_script, "requiredPapers")
        wanted_papers = contract["required_paper_ids"]
        if observed_papers != wanted_papers:
            raise AuditError(f"required paper IDs differ from ground truth: {path}:{question_id}")

        observed_atomic = normalize_option_sets(
            parse_json_constant(atomic_script, "expectedSets"),
            f"atomic expected IDs at {path}:{question_id}",
        )
        wanted_atomic = normalize_option_sets(
            [item["evidence_claim_ids"] for item in contract["answer_claims"]],
            f"ground-truth atomic expected IDs at {path}:{question_id}",
        )
        if observed_atomic != wanted_atomic:
            raise AuditError(f"atomic expected IDs differ from ground truth: {path}:{question_id}")

        normalized_observed_negatives = normalize_option_sets(
            parse_json_constant(negative_script, "expectedSets"),
            f"negative expected IDs at {path}:{question_id}",
        )
        normalized_wanted_negatives = normalize_option_sets(
            [item["evidence_claim_ids"] for item in contract["important_negatives"]],
            f"ground-truth negative expected IDs at {path}:{question_id}",
        )
        if normalized_observed_negatives != normalized_wanted_negatives:
            raise AuditError(f"negative expected IDs differ from ground truth: {path}:{question_id}")

        cases.append(
            {
                "question_id": question_id,
                "allowed_binding_scope": binding_scope,
                "allowed_claim_ids": sorted(observed_allowed),
                "required_paper_ids": observed_papers,
                "atomic_expected_sets": observed_atomic,
                "negative_anchor_sets": normalized_observed_negatives,
                "status": "pass",
            }
        )
    return {
        "path": path.relative_to(repo_root).as_posix(),
        "sha256": sha256_file(path),
        "question_count": len(cases),
        "allowed_binding_scope": binding_scope,
        "status": "pass",
        "cases": cases,
    }


def audit_binding(
    repo_root: Path,
    bundle: Path,
    evidence: dict[str, Any],
    binding: dict[str, Any],
) -> dict[str, Any]:
    claim_id = evidence["claim_id"]
    paper_id = evidence["paper_id"]
    expected_source_id = f"claims-{paper_id.replace('.', '-')}"
    expected_source_path = f"sources/claims/{paper_id}.jsonl"
    expected_evidence_path = f"sources/markdown/{paper_id}.md"
    locators = [item["locator"] for item in evidence["paper_evidence"]]
    pages = [int(locator.removeprefix("PDF-page-")) for locator in locators]
    expected_fields = {
        "record_id": claim_id,
        "paper_id": paper_id,
        "review_state": "reviewed",
        "concept_type": "Paper Semantic Claim",
        "source_id": expected_source_id,
        "source_path": expected_source_path,
        "authoritative_text": evidence["interpretation"],
        "authoritative_text_sha256": evidence["interpretation_sha256"],
        "locator_tokens": locators,
        "citation_pages": pages,
        "evidence_paths": [expected_evidence_path],
    }
    for key, wanted in expected_fields.items():
        if binding.get(key) != wanted:
            raise AuditError(f"answer binding {key} mismatch for {claim_id}")
    if sha256_bytes(binding["authoritative_text"].encode("utf-8")) != binding["authoritative_text_sha256"]:
        raise AuditError(f"answer binding text hash mismatch for {claim_id}")
    concept_path = resolve_repo_path(bundle, binding["concept_path"])
    if not concept_path.is_file():
        raise AuditError(f"answer binding concept is missing for {claim_id}: {binding['concept_path']}")
    concept_text = concept_path.read_text(encoding="utf-8")
    if binding["authoritative_text"] not in concept_text:
        raise AuditError(f"concept does not contain authoritative interpretation for {claim_id}")
    authoritative_source = resolve_repo_path(repo_root, evidence["claim_source"]["path"])
    if not authoritative_source.is_file():
        raise AuditError(f"authoritative claim source is missing for {claim_id}")
    for page in evidence["paper_evidence"]:
        if not resolve_repo_path(repo_root, page["path"]).is_file():
            raise AuditError(f"authoritative paper source is missing for {claim_id}")
    return {
        "claim_id": claim_id,
        "paper_id": paper_id,
        "source_id": binding["source_id"],
        "source_path": binding["source_path"],
        "concept_path": binding["concept_path"],
        "locators": binding["locator_tokens"],
        "record_sha256": binding["record_sha256"],
        "authoritative_text_sha256": binding["authoritative_text_sha256"],
        "authoritative_text": binding["authoritative_text"],
        "status": "pass",
    }


def audit_question(
    repo_root: Path,
    bundle: Path,
    record: dict[str, Any],
    bindings: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    evidence_by_id = {item["claim_id"]: item for item in record["authoritative_evidence"]}
    contract = record["ground_truth"]
    all_expected_ids = {
        claim_id
        for section in ("answer_claims", "important_negatives")
        for item in contract[section]
        for claim_id in item["evidence_claim_ids"]
    }
    if all_expected_ids != set(evidence_by_id):
        raise AuditError(f"expected IDs do not exhaust authoritative evidence: {record['id']}")

    binding_rows = {
        claim_id: audit_binding(repo_root, bundle, evidence_by_id[claim_id], bindings[claim_id])
        for claim_id in sorted(all_expected_ids)
    }
    atomic_rows: list[dict[str, Any]] = []
    for item in contract["answer_claims"]:
        review = SPECIAL_ATOMIC_REVIEWS.get(
            item["id"],
            {
                "relationship": "direct-record-anchor",
                "note": "The atomic statement is a faithful paraphrase of the reviewed interpretation.",
            },
        )
        atomic_rows.append(
            {
                "answer_claim_id": item["id"],
                "statement": item["statement"],
                "expected_claim_ids": item["evidence_claim_ids"],
                "relationship": review["relationship"],
                "review_note": review["note"],
                "status": "sensible",
            }
        )
    negative_rows = [
        {
            "negative_id": item["id"],
            "statement": item["statement"],
            "expected_claim_ids": item["evidence_claim_ids"],
            "relationship": "derived-negative-anchor-set",
            "review_note": (
                "The listed IDs are sensible evidence anchors for the explicit join, contrast, "
                "conditional, or exclusion. The negative is not asserted to be a literal sentence in "
                "every individual record."
            ),
            "status": "sensible",
        }
        for item in contract["important_negatives"]
    ]
    return {
        "question_id": record["id"],
        "question": record["question"],
        "required_paper_ids": contract["required_paper_ids"],
        "required_source_ids": contract["required_source_ids"],
        "atomic_answers": atomic_rows,
        "important_negatives": negative_rows,
        "derivation": contract["derivation"],
        "bindings": list(binding_rows.values()),
        "status": "pass",
    }


def build_report(
    repo_root: Path,
    evaluation_dir: Path,
    bundle: Path,
    config_paths: list[Path],
    frozen_manifest: Path | None = None,
) -> dict[str, Any]:
    validator_path = repo_root / "evaluations/semantic-okf-classical/scripts/validate_hard_ground_truth.py"
    validator = load_module("semantic_okf_expected_id_authoritative_validator", validator_path)
    try:
        validator.validate_all(repo_root, evaluation_dir)
    except Exception as exc:
        raise AuditError(f"authoritative hard-ground-truth validation failed: {exc}") from exc

    records = load_jsonl(evaluation_dir / "hard-ground-truth.jsonl")
    prefixes = [item["id"].split("-", 1)[0] for item in records]
    if prefixes != EXPECTED_QUESTION_IDS:
        raise AuditError("hard-question order is not q031 through q040")
    ground_truth_by_id = {item["id"]: item for item in records}

    bindings_path = bundle / "adaptive/answer-bindings.jsonl"
    binding_rows = load_jsonl(bindings_path)
    bindings = {item["record_id"]: item for item in binding_rows}
    if len(bindings) != len(binding_rows):
        raise AuditError("answer-binding record IDs are not unique")
    required_claim_ids = {
        claim_id
        for record in records
        for section in ("answer_claims", "important_negatives")
        for item in record["ground_truth"][section]
        for claim_id in item["evidence_claim_ids"]
    }
    missing = required_claim_ids - set(bindings)
    if missing:
        raise AuditError(f"expected claim IDs are absent from answer bindings: {sorted(missing)}")

    questions = [audit_question(repo_root, bundle, record, bindings) for record in records]
    configs = [audit_config(repo_root, path, ground_truth_by_id, bindings) for path in config_paths]
    atomic_rows = [item for question in questions for item in question["atomic_answers"]]
    negative_rows = [item for question in questions for item in question["important_negatives"]]
    relationships = Counter(item["relationship"] for item in atomic_rows)
    expected_links = [
        claim_id
        for question in questions
        for section in ("atomic_answers", "important_negatives")
        for item in question[section]
        for claim_id in item["expected_claim_ids"]
    ]

    frozen_manifest = frozen_manifest or (
        repo_root / "evaluations/semantic-okf-adaptive-evolution/frozen-benchmark.json"
    )
    bundle_index = bundle / "adaptive/index.json"
    return {
        "schema_version": SCHEMA_VERSION,
        "audit_date": "2026-07-15",
        "status": "pass",
        "conclusion": (
            "All frozen atomic expected IDs are sensible authoritative anchors. Exact-ID coverage is "
            "a strict identity metric, while important-negative ID assertions measure anchor presence "
            "and require separate semantic review of the stated contrast or exclusion."
        ),
        "inputs": {
            "frozen_benchmark": {
                "path": frozen_manifest.relative_to(repo_root).as_posix(),
                "sha256": sha256_file(frozen_manifest),
            },
            "ground_truth": {
                "path": (evaluation_dir / "hard-ground-truth.jsonl").relative_to(repo_root).as_posix(),
                "sha256": sha256_file(evaluation_dir / "hard-ground-truth.jsonl"),
            },
            "bundle": {
                "path": bundle.relative_to(repo_root).as_posix(),
                "adaptive_index_sha256": sha256_file(bundle_index),
                "answer_bindings_sha256": sha256_file(bindings_path),
                "answer_binding_count": len(binding_rows),
            },
        },
        "summary": {
            "questions": len(questions),
            "atomic_answer_claims": len(atomic_rows),
            "important_negatives": len(negative_rows),
            "unique_expected_claim_ids": len(set(expected_links)),
            "expected_id_links": len(expected_links),
            "direct_record_anchors": relationships["direct-record-anchor"],
            "bounded_derivation_anchors": relationships["bounded-derivation-anchor"],
            "page_supported_detail_anchors": relationships["page-supported-detail-anchor"],
            "authoritative_locator_and_hash_checks": len(required_claim_ids),
            "skill_arena_configs_checked": len(configs),
            "config_question_checks": sum(item["question_count"] for item in configs),
            "mismatches": 0,
        },
        "metric_interpretation": {
            "atomic_answer_completeness": (
                "Requires every frozen canonical claim ID. It is intentionally stricter than semantic "
                "correctness and can under-credit a correct answer supported by a different valid record."
            ),
            "important_negative_coverage": (
                "Requires at least one listed evidence anchor for each negative. It does not prove that "
                "the response actually states the required negative; the blinded semantic review checks that."
            ),
            "evidence_validity": (
                "Checks that emitted IDs use the closed authoritative binding, concept path, paper ID, "
                "source path, and declared locator set."
            ),
            "or_option_sets": (
                "Each atomic or negative option array is a logical OR set. Membership is audited "
                "exactly, while option order and duplicate spellings have no scoring meaning; the "
                "ordered sequence of answer and negative groups remains exact."
            ),
        },
        "questions": questions,
        "configuration_checks": configs,
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    repo_root = Path(__file__).resolve().parents[3]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=repo_root)
    parser.add_argument(
        "--evaluation-dir",
        type=Path,
        default=Path("evaluations/semantic-okf-adaptive"),
    )
    parser.add_argument(
        "--bundle",
        type=Path,
        default=Path(
            "evaluations/semantic-okf-adaptive-evolution/results/population-runs/"
            "generation-000/candidate-07"
        ),
    )
    parser.add_argument(
        "--config",
        action="append",
        dest="configs",
        help="Skill Arena config to audit; repeat to override the default four configs.",
    )
    parser.add_argument(
        "--frozen-benchmark",
        type=Path,
        default=Path("evaluations/semantic-okf-adaptive-evolution/frozen-benchmark.json"),
        help="Frozen benchmark manifest that governs this expected-ID audit.",
    )
    parser.add_argument("--output", type=Path)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    repo_root = args.repo_root.resolve()

    def resolved(path: Path) -> Path:
        return path.resolve() if path.is_absolute() else (repo_root / path).resolve()

    evaluation_dir = resolved(args.evaluation_dir)
    bundle = resolved(args.bundle)
    frozen_manifest = resolved(args.frozen_benchmark)
    config_values = args.configs if args.configs else list(DEFAULT_CONFIGS)
    config_paths = [resolved(Path(value)) for value in config_values]
    try:
        report = build_report(
            repo_root,
            evaluation_dir,
            bundle,
            config_paths,
            frozen_manifest=frozen_manifest,
        )
        serialized = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
        if args.output:
            output = resolved(args.output)
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(serialized, encoding="utf-8", newline="\n")
        summary = report["summary"]
        print(
            f"Audited {summary['atomic_answer_claims']} atomic answer groups, "
            f"{summary['expected_id_links']} expected-ID links, "
            f"{summary['important_negatives']} derived-negative anchor sets, "
            f"{summary['unique_expected_claim_ids']} unique authoritative claims, and "
            f"{summary['config_question_checks']} config-question assertion blocks: pass."
        )
        return 0
    except (AuditError, OSError, ValueError, KeyError, TypeError, yaml.YAMLError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
