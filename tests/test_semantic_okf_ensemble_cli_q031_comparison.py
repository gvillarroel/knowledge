from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "evaluations"
    / "semantic-okf-ensemble"
    / "scripts"
    / "generate_cli_q031_comparison.py"
)
REPORT = ROOT / "evaluations" / "semantic-okf-ensemble" / "cli-q031-comparison.json"
CURRENT = ROOT / "evaluations" / "semantic-okf-ensemble" / "cli-q031-current-output.json"


def _module():
    spec = importlib.util.spec_from_file_location("generate_cli_q031_comparison", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_cli_q031_comparison_artifacts_are_reproducible() -> None:
    completed = subprocess.run(
        [sys.executable, str(SCRIPT), "--check"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr
    assert "artifacts are current" in completed.stdout


def test_current_cli_output_passes_all_five_local_gates() -> None:
    module = _module()
    response = json.loads(CURRENT.read_text(encoding="utf-8"))
    gates = module.compute_current_gates(response, module._load_ground_truth())

    assert list(gates) == list(module.GATES)
    assert gates == {gate: 1 for gate in module.GATES}
    assert response["question_id"] == module.QUESTION_ID
    assert [item["claim_id"] for item in response["evidence"]] == [
        "claim-2402-07630v3-039",
        "claim-2503-13804v1-038",
        "claim-2506-05690v3-043",
        "claim-2506-05690v3-044",
    ]


def test_current_gate_recomputation_rejects_binding_and_atomic_tampering() -> None:
    module = _module()
    truth = module._load_ground_truth()
    response = json.loads(CURRENT.read_text(encoding="utf-8"))

    bad_binding = copy.deepcopy(response)
    bad_binding["evidence"][0]["concept_path"] = "concepts/not-authoritative.md"
    assert module.compute_current_gates(bad_binding, truth)["evidence-validity"] == 0

    incomplete = copy.deepcopy(response)
    incomplete["answer"]["claims"] = [
        item
        for item in incomplete["answer"]["claims"]
        if "claim-2506-05690v3-044" not in item["supporting_claim_ids"]
    ]
    assert module.compute_current_gates(incomplete, truth)["atomic-answer-completeness"] == 0


def test_compact_report_separates_current_cli_from_historical_mcp() -> None:
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    alternatives = report["main_alternatives"]

    assert [entry["id"] for entry in alternatives] == [
        "legacy",
        "embeddings",
        "classical",
        "entity_graph",
        "adaptive",
        "definitive_ensemble_cli",
    ]
    assert [entry["score"] for entry in alternatives] == [0.4, 0.6, 0.4, 0.4, 0.4, 1.0]
    definitive = alternatives[-1]
    assert definitive["provenance"]["mcp_used"] is False
    assert definitive["provenance"]["model_generation"] is False
    assert definitive["provenance"]["result_id"] is None
    assert definitive["provenance"]["finalizer_stdout_without_newline_sha256"] == (
        "e052575835024481527ed7f07c80242a2ab414370f8868323861945931e43d50"
    )

    historical = report["historical_reference"]
    assert historical["id"] == "historical_mcp_ensemble"
    assert historical["score"] == 1.0
    assert "retired MCP" in historical["evaluation_status"]
    assert historical["provenance"]["result_id"] == "3f118e39-ac2e-4b43-8b8c-f16319c06b93"


def test_archived_rows_fall_back_to_checked_objects_when_raw_runs_are_absent(tmp_path: Path) -> None:
    module = _module()
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    module.ROOT = tmp_path

    recovered = [module._archived_entry(spec, report) for spec in module.RAW_SPECS]
    recovered.append(module._archived_entry(module.HISTORICAL_SPEC, report))

    assert [entry["id"] for entry in recovered] == [
        "legacy",
        "embeddings",
        "classical",
        "entity_graph",
        "adaptive",
        "historical_mcp_ensemble",
    ]
    for entry in recovered:
        module._validate_entry(entry)
