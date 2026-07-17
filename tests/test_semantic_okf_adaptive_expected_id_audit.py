from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
import sys
from pathlib import Path
from types import ModuleType

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
EVALUATION_ROOT = REPO_ROOT / "evaluations" / "semantic-okf-adaptive-evolution"
AUDITOR = EVALUATION_ROOT / "scripts" / "audit_expected_ids.py"
REPORT = EVALUATION_ROOT / "expected-id-audit.json"
GROUND_TRUTH = REPO_ROOT / "evaluations" / "semantic-okf-adaptive" / "hard-ground-truth.jsonl"
REVIEWED_GROUND_TRUTH = (
    REPO_ROOT
    / "evaluations"
    / "semantic-okf-ensemble"
    / "reviewed-benchmark"
    / "hard-ground-truth.jsonl"
)
REVIEWED_CONFIG = (
    REPO_ROOT
    / "evaluations"
    / "semantic-okf-ensemble"
    / "skill-arena"
    / "ensemble-hard10.yaml"
)
AUTHORITATIVE_RECORDS = (
    REPO_ROOT
    / "evaluations"
    / "graphrag-cross-paper"
    / "bundle"
    / "semantic"
    / "records.jsonl"
)
REVIEWED_AUDIT = (
    REPO_ROOT
    / "evaluations"
    / "semantic-okf-ensemble"
    / "expected-id-audit-final.json"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _module() -> ModuleType:
    name = "test_semantic_okf_expected_id_auditor"
    specification = importlib.util.spec_from_file_location(name, AUDITOR)
    assert specification and specification.loader
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


def _ground_truth_by_id() -> dict[str, dict[str, object]]:
    rows = [
        json.loads(line)
        for line in GROUND_TRUTH.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    return {row["id"]: row for row in rows}


def _bindings_from_report(report: dict[str, object]) -> dict[str, dict[str, object]]:
    bindings: dict[str, dict[str, object]] = {}
    for question in report["questions"]:
        for item in question["bindings"]:
            bindings[item["claim_id"]] = {
                "concept_path": item["concept_path"],
                "locator_tokens": item["locators"],
                "paper_id": item["paper_id"],
                "source_path": item["source_path"],
            }
    return bindings


def _reviewed_ground_truth_by_id() -> dict[str, dict[str, object]]:
    rows = [
        json.loads(line)
        for line in REVIEWED_GROUND_TRUTH.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    return {row["id"]: row for row in rows}


def _reviewed_bindings() -> dict[str, dict[str, object]]:
    audit = json.loads(REVIEWED_AUDIT.read_text(encoding="utf-8"))
    published = audit["inputs"]["authoritative_records"]
    assert _sha256(AUTHORITATIVE_RECORDS) == published["sha256"]
    rows = [
        json.loads(line)
        for line in AUTHORITATIVE_RECORDS.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert len(rows) == published["count"]

    bindings: dict[str, dict[str, object]] = {}
    for row in rows:
        source_id = row.get("source_id")
        if not isinstance(source_id, str) or not source_id.startswith("claims-"):
            continue
        attributes = row.get("attributes")
        assert isinstance(attributes, dict)
        assert attributes.get("review_state") == "reviewed"
        locator = attributes.get("evidence_locator")
        assert isinstance(locator, str) and locator
        locator_tokens = sorted(
            {
                fragment.rsplit("#", 1)[1]
                for fragment in locator.split(";")
                if "#" in fragment
            }
        )
        assert locator_tokens and all(token.startswith("PDF-page-") for token in locator_tokens)
        source_path = row.get("source_path")
        claim_id = row.get("record_id")
        assert isinstance(source_path, str) and isinstance(claim_id, str)
        assert claim_id not in bindings
        bindings[claim_id] = {
            "concept_path": row["concept_path"],
            "locator_tokens": locator_tokens,
            "paper_id": Path(source_path).stem,
            "source_path": source_path,
        }

    expected_count = audit["inputs"]["answer_bindings"]["count"]
    assert len(bindings) == expected_count
    return bindings


def test_expected_id_audit_report_is_compact_hash_bound_and_complete() -> None:
    report = json.loads(REPORT.read_text(encoding="utf-8"))

    assert report["schema_version"] == "semantic-okf-expected-id-audit/1.0"
    assert report["status"] == "pass"
    assert report["summary"] == {
        "questions": 10,
        "atomic_answer_claims": 44,
        "important_negatives": 13,
        "unique_expected_claim_ids": 42,
        "expected_id_links": 72,
        "direct_record_anchors": 40,
        "bounded_derivation_anchors": 3,
        "page_supported_detail_anchors": 1,
        "authoritative_locator_and_hash_checks": 42,
        "skill_arena_configs_checked": 4,
        "config_question_checks": 40,
        "mismatches": 0,
    }
    assert report["inputs"]["ground_truth"]["sha256"] == _sha256(GROUND_TRUTH)
    assert len(report["questions"]) == 10
    assert all(question["status"] == "pass" for question in report["questions"])
    for config in report["configuration_checks"]:
        assert config["status"] == "pass"
        assert config["question_count"] == 10
        assert _sha256(REPO_ROOT / config["path"]) == config["sha256"]


def test_every_atomic_mapping_has_an_explicit_semantic_relationship() -> None:
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    atomic = [item for question in report["questions"] for item in question["atomic_answers"]]
    negatives = [
        item for question in report["questions"] for item in question["important_negatives"]
    ]

    assert len(atomic) == 44
    assert {item["status"] for item in atomic} == {"sensible"}
    assert {item["relationship"] for item in atomic} == {
        "direct-record-anchor",
        "bounded-derivation-anchor",
        "page-supported-detail-anchor",
    }
    assert {item["status"] for item in negatives} == {"sensible"}
    assert {item["relationship"] for item in negatives} == {"derived-negative-anchor-set"}


def test_all_four_configs_reproduce_the_frozen_expected_ids() -> None:
    module = _module()
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    ground_truth = _ground_truth_by_id()
    bindings = _bindings_from_report(report)

    results = [
        module.audit_config(REPO_ROOT, REPO_ROOT / config["path"], ground_truth, bindings)
        for config in report["configuration_checks"]
    ]

    assert len(results) == 4
    assert sum(result["question_count"] for result in results) == 40
    assert all(result["status"] == "pass" for result in results)


def test_config_audit_rejects_an_expected_id_change(tmp_path: Path) -> None:
    module = _module()
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    ground_truth = _ground_truth_by_id()
    bindings = _bindings_from_report(report)
    source = REPO_ROOT / report["configuration_checks"][0]["path"]
    destination = tmp_path / "changed.yaml"
    shutil.copy2(source, destination)
    changed = destination.read_text(encoding="utf-8").replace(
        "claim-2506-05690v3-043", "claim-2506-05690v3-042"
    )
    destination.write_text(changed, encoding="utf-8")

    with pytest.raises(module.AuditError, match="allowed claim bindings|atomic expected IDs"):
        module.audit_config(tmp_path, destination, ground_truth, bindings)


def test_reviewed_atomic_or_options_are_order_insensitive() -> None:
    module = _module()
    ground_truth = _reviewed_ground_truth_by_id()
    bindings = _reviewed_bindings()

    result = module.audit_config(
        REPO_ROOT,
        REVIEWED_CONFIG,
        ground_truth,
        bindings,
    )

    assert result["status"] == "pass"
    q031 = result["cases"][0]
    assert q031["atomic_expected_sets"][-1] == [
        "claim-2503-13804v1-037",
        "claim-2503-13804v1-038",
    ]
    assert ground_truth[q031["question_id"]]["ground_truth"]["answer_claims"][-1][
        "evidence_claim_ids"
    ] == [
        "claim-2503-13804v1-038",
        "claim-2503-13804v1-037",
    ]


def test_reviewed_atomic_or_options_reject_changed_membership(tmp_path: Path) -> None:
    module = _module()
    ground_truth = _reviewed_ground_truth_by_id()
    bindings = _reviewed_bindings()
    destination = tmp_path / "changed-reviewed.yaml"
    source = REVIEWED_CONFIG.read_text(encoding="utf-8")
    old = (
        'const expectedSets = [["claim-2506-05690v3-043"],'
        '["claim-2506-05690v3-044"],["claim-2402-07630v3-039"],'
        '["claim-2503-13804v1-037","claim-2503-13804v1-038"]];'
    )
    new = old.replace(
        '["claim-2503-13804v1-037","claim-2503-13804v1-038"]',
        '["claim-2503-13804v1-038"]',
    )
    assert source.count(old) == 1
    destination.write_text(source.replace(old, new, 1), encoding="utf-8", newline="\n")

    with pytest.raises(module.AuditError, match="atomic expected IDs differ"):
        module.audit_config(tmp_path, destination, ground_truth, bindings)


def test_reviewed_config_rejects_drift_in_non_question_allowed_binding(tmp_path: Path) -> None:
    module = _module()
    ground_truth = _reviewed_ground_truth_by_id()
    bindings = _reviewed_bindings()
    destination = tmp_path / "changed-reviewed-allowed.yaml"
    source = REVIEWED_CONFIG.read_text(encoding="utf-8")
    original = '"claim-2402-07630v3-001":'
    replacement = '"claim-bogus-non-question-binding":'
    assert source.count(original) == 10
    destination.write_text(source.replace(original, replacement, 1), encoding="utf-8", newline="\n")

    with pytest.raises(module.AuditError, match="allowed claim bindings differ"):
        module.audit_config(tmp_path, destination, ground_truth, bindings)
