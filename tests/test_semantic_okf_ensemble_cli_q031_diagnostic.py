from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "evaluations/semantic-okf-ensemble/scripts/summarize_cli_q031_skill_arena.py"
REPORT = ROOT / "evaluations/semantic-okf-ensemble/cli-q031-skill-arena-diagnostic.json"


def _module():
    spec = importlib.util.spec_from_file_location("summarize_cli_q031_skill_arena", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_checked_diagnostic_is_reproducible() -> None:
    result = subprocess.run([sys.executable, str(SCRIPT), "--check"], cwd=ROOT, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert "artifacts are current" in result.stdout


def test_run_disposition_scores_and_no_mcp_attestation() -> None:
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    rejected, accepted = report["runs"]
    assert (rejected["eval_id"], rejected["disposition"]) == ("eval-vuT-2026-07-15T20:00:38", "rejected")
    assert rejected["cells"]["knowledge-only-control"]["score"] == 0.4
    assert rejected["cells"]["ensemble-cli-consult-treatment"]["response"].get("output") is None
    assert "timed out after 240 seconds" in rejected["cells"]["ensemble-cli-consult-treatment"]["error"]
    assert accepted["eval_id"] == "eval-3TJ-2026-07-15T20:07:20"
    assert accepted["cells"]["knowledge-only-control"]["score"] == 0.6
    treatment = accepted["cells"]["ensemble-cli-consult-treatment"]
    assert treatment["score"] == 0.8
    assert treatment["named_scores"] == {
        "response-format": 1,
        "response-contract": 1,
        "evidence-validity": 0,
        "atomic-answer-completeness": 1,
        "important-negative-coverage": 1,
    }
    assert report["no_mcp_attestation"]["passed"] is True
    assert report["no_mcp_attestation"]["declared_treatment_capabilities"] == ["skills"]


def test_only_two_dotted_source_path_bindings_were_mutated() -> None:
    diagnostic = json.loads(REPORT.read_text(encoding="utf-8"))["accepted_treatment_evidence_diagnostic"]
    assert diagnostic["field_check_count"] == 55
    assert diagnostic["passed_field_check_count"] == 53
    assert diagnostic["all_other_evidence_fields_match"] is True
    assert diagnostic["mismatches"] == [
        {"claim_id": "claim-2506-05690v3-002", "field": "source_path", "expected": "sources/claims/2506.05690v3.jsonl", "actual": "sources/claims/2506-05690v3.jsonl"},
        {"claim_id": "claim-2506-05690v3-044", "field": "source_path", "expected": "sources/claims/2506.05690v3.jsonl", "actual": "sources/claims/2506-05690v3.jsonl"},
    ]


def test_checked_run_is_a_valid_fallback_when_raw_runs_are_absent() -> None:
    module = _module()
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    recovered = module._checked_run(report, module.RUN_SPECS[1])
    assert recovered["eval_id"] == module.RUN_SPECS[1]["eval_id"]
    assert recovered["cells"]["ensemble-cli-consult-treatment"]["summary"] == module._summary(
        recovered["cells"]["ensemble-cli-consult-treatment"]["response"]
    )


def test_direct_finalizer_reference_stays_distinct_from_agent_result() -> None:
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    direct = report["direct_cli_finalizer_reference"]
    assert direct["score"] == 1.0
    assert direct["mcp_used"] is False
    assert direct["named_gates"] == {gate: 1 for gate in module_gates()}


def module_gates() -> tuple[str, ...]:
    return _module().GATES
