"""Regression tests for the checked benchmark identity and locator audit."""

from __future__ import annotations

import importlib.util
from pathlib import Path


HERE = Path(__file__).resolve().parents[1]


def load_audit_module():
    """Load the standalone audit script from its hyphenated package path."""

    path = HERE / "audit_benchmark_ids.py"
    spec = importlib.util.spec_from_file_location("semantic_okf_harbor_benchmark_id_audit", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_fresh_audit_covers_every_expected_identity_and_locator() -> None:
    module = load_audit_module()
    audit = module.build_audit()

    assert audit["status"] == "pass"
    assert audit["summary"]["question_ids"] == 40
    assert audit["summary"]["split_pairwise_overlap"] == 0
    assert audit["summary"]["qrel_source_ledger_crosswalk_joins"] == 30
    assert audit["summary"]["hard_required_id_sets_matching_qrels"] == 10
    assert audit["summary"]["real_grader_unique_record_body_mappings"] == 46
    assert len(audit["authoritative_evidence_audit"]) == 46
    assert all(row["unique_record_body_match"] for row in audit["authoritative_evidence_audit"])


def test_checked_reports_equal_a_fresh_audit() -> None:
    module = load_audit_module()
    audit = module.build_audit()

    assert (HERE / "reports/benchmark-id-audit.json").read_text(encoding="utf-8") == module.encoded_json(audit)
    assert (HERE / "reports/benchmark-id-audit.md").read_text(encoding="utf-8") == module.markdown_report(audit)

