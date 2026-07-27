from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
ROOT = REPO_ROOT / "evaluations" / "semantic-okf-tika-mallet"

def test_real_tool_receipt_binds_fixtures_runtimes_and_reproducibility() -> None:
    report = json.loads(
        (ROOT / "reports" / "real-tool-smoke-20260722-hardened.json").read_text(
            encoding="utf-8"
        )
    )
    fixture_hashes = {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in (ROOT / "fixtures" / "documents").iterdir()
        if path.is_file()
    }

    assert report["status"] == "pass"
    assert report["runtime"]["tika_version"] == "4.0.0-beta-1"
    assert report["runtime"]["mallet_version"] == "2.1.0"
    assert len(report["runtime"]["tika_archive_sha512"]) == 128
    assert report["checks"]["two_clean_builds_byte_identical"] is True
    assert report["checks"]["consultant_deep_retraining_pass"] is True
    assert report["reproducibility"]["file_count"] == 24
    assert report["reproducibility"]["inventory_sha256"] == (
        "fd566c7b53aac3a1680fe6de11bc7908767ba8d943ae181728444e299555c911"
    )
    assert len(report["reproducibility"]["inventory"]) == 24
    assert report["inputs"] == {
        "ingestion_plan_sha256": hashlib.sha256(
            (ROOT / "ingestion-plan.json").read_bytes()
        ).hexdigest(),
        "retrieval_plan_sha256": hashlib.sha256(
            (ROOT / "retrieval-plan.json").read_bytes()
        ).hexdigest(),
        "source_combination_decision_sha256": hashlib.sha256(
            (ROOT / "source-combination-decision.json").read_bytes()
        ).hexdigest(),
    }
    assert report["python_runtime"]["implementation"] == "CPython"
    builder_root = REPO_ROOT / "skills" / "build-semantic-okf-tika-mallet"
    consultant_root = REPO_ROOT / "skills" / "consult-semantic-okf-tika-mallet"
    assert report["locks"] == {
        "builder_requirements_sha256": hashlib.sha256(
            (builder_root / "scripts" / "requirements.txt").read_bytes()
        ).hexdigest(),
        "consultant_requirements_sha256": hashlib.sha256(
            (consultant_root / "scripts" / "requirements.txt").read_bytes()
        ).hexdigest(),
    }
    for label in ("builder", "consultant"):
        receipt = report["skills"][label]
        inventory = receipt["inventory"]
        assert receipt["file_count"] == len(inventory)
        assert receipt["inventory_sha256"] == hashlib.sha256(
            json.dumps(
                inventory,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
                allow_nan=False,
            ).encode("utf-8")
        ).hexdigest()
    # The receipt is immutable historical evidence. Later canonical adapter and
    # bounded consultation development must not rewrite it to match current trees.
    assert report["skills"]["builder"]["inventory_sha256"] == (
        "43eacb3638800b20185ba8f70a0010448e66e566ab8f156fff49436883982c74"
    )
    assert report["skills"]["consultant"]["inventory_sha256"] == (
        "acc716908a5ec56bff333100ee1e486e8ed13e1f722e8e5ee866f8bb3e65a2f7"
    )
    assert fixture_hashes == {
        "integration-preview.pdf": "c78b908d8dd8490e48abd7c970b5a59993a68477cfbcbb87c45d4a8a3d575a84",
        "office-excel-fixture.xlsx": "1d2a9fd643b3ad20d249c6f371b23e436798744a9439d227ca3e59000e8c1ac2",
    }


def test_experiment_plans_keep_tika_mallet_and_okf_boundaries_explicit() -> None:
    ingestion = json.loads((ROOT / "ingestion-plan.json").read_text(encoding="utf-8"))
    retrieval = json.loads((ROOT / "retrieval-plan.json").read_text(encoding="utf-8"))
    results = (ROOT / "RESULTS.md").read_text(encoding="utf-8")
    combination = json.loads(
        (ROOT / "source-combination-decision.json").read_text(encoding="utf-8")
    )
    negative_cases = (ROOT / "NEGATIVE-CASES.md").read_text(encoding="utf-8")

    assert ingestion["tika"] == {
        "version": "4.0.0-beta-1",
        "verify_default_markdown": True,
        "timeout_seconds": 120,
        "max_input_bytes": 1048576,
    }
    assert {source["concept_type"] for source in ingestion["sources"]} == {
        "Office Document",
        "PDF Document",
    }
    assert retrieval["topics"]["num_threads"] == 1
    assert retrieval["topics"]["random_seed"] == 42
    assert retrieval["selection"]["source_ids"] == [
        "office-documents",
        "pdf-documents",
    ]
    assert combination == {
        "approval_reference": "ADR-0044",
        "decision_id": "tika-mallet-fixtures-001",
        "duplicate_policy": "reject-within-identity-scope",
        "governance_reference": "local-immutable-experimental-fixtures",
        "identity_scope": "source-and-record-id",
        "logical_source_id": None,
        "members": ["office-documents", "pdf-documents"],
        "mode": "separate-in-bundle",
        "protocol_version": "1.0",
        "record_fusion": False,
    }
    assert "test_tika_uses_one_private_raw_snapshot" in negative_cases
    assert "test_no_replace_publication_preserves_concurrent_destination" in negative_cases
    normalized_results = " ".join(results.split())
    assert (
        "original two-fixture smoke alone was not evidence that MALLET improves "
        "retrieval quality"
        in normalized_results
    )
    assert "40-question result is valid comparative evidence" in normalized_results
    assert "does not promote the Tika beta" in results


def test_canonical_intake_separates_direct_ranking_from_harbor_admission() -> None:
    intake = json.loads(
        (ROOT / "canonical-evaluation-intake.json").read_text(encoding="utf-8")
    )
    receipt_path = (
        ROOT / "reports" / "real-tool-smoke-20260722-hardened.json"
    )
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    candidate = intake["candidate"]
    evidence = intake["mechanical_evidence"]
    metrics = intake["canonical_metrics"]
    gates = {
        row["gate_id"]: row["status"] for row in intake["admission_gates"]
    }

    assert intake["schema_version"] == "semantic-okf-canonical-evaluation-intake/1.1"
    assert candidate == {
        "candidate_id": "tika-mallet",
        "display_name": "Apache Tika and Java MALLET",
        "build_skill": "build-semantic-okf-tika-mallet",
        "consult_skill": "consult-semantic-okf-tika-mallet",
        "prospective_harbor_consult_skill": "consult-semantic-okf-tika-mallet-bounded",
        "experiment_decision_reference": "ADR-0044",
        "reporting_decision_reference": "ADR-0049",
        "intake_date": "2026-07-23",
        "registry_state": "candidate-not-registered",
        "ranking_eligibility": {
            "direct_retrieval": True,
            "grounded_answer_harbor": False,
            "registry_promotion": False,
        },
        "promotion_decision": "pending-grounded-harbor-and-cross-platform-evaluation",
    }
    assert evidence["inventory_sha256"] == receipt["reproducibility"][
        "inventory_sha256"
    ]
    assert evidence["published_file_count"] == receipt["reproducibility"][
        "file_count"
    ]
    assert evidence["fixture_formats"] == receipt["fixture"]["formats"]
    assert evidence["semantic_records"] == receipt["fixture"]["semantic_records"]
    assert evidence["fusion_smoke_results"] == receipt["search"]["returned"]
    assert metrics == {
        "scope": "deterministic-direct-retrieval",
        "dataset_id": "graphrag-papers-40",
        "question_count": 40,
        "selected_route": "tika_mallet_fusion",
        "recall_at_10": 0.7481727994227995,
        "hard_recall_at_10": 0.7183333333333334,
        "mrr_at_10": 0.875,
        "ndcg_at_10": 0.754359723533816,
        "hard_mrr_at_10": 0.7166666666666667,
        "hard_ndcg_at_10": 0.6180016914364821,
        "evidence_valid_rate": 1.0,
        "evidence_valid_rows": 400,
        "evidence_total_rows": 400,
        "mean_latency_ms": 77.13061498943716,
        "p95_latency_ms": 86.35780498152597,
        "timing_excludes_setup": True,
        "deep_validation_setup_ms": 8641.8861,
        "top10_replicate_exact": True,
        "pool100_replicate_exact": True,
        "top10_pool100_prefix_exact": True,
        "ranking_eligible": True,
    }
    harbor = intake["grounded_harbor"]
    assert harbor["ranking_eligible"] is False
    assert harbor["status"] == "incomplete-external-provider-quota"
    assert harbor["v4_agent_input_tokens"] == 0
    assert harbor["v4_agent_output_tokens"] == 0
    assert harbor["v4_provider_error_code"] == "usage_limit_reached"
    assert all(
        harbor[name] is None
        for name in (
            "harbor_discovery_reward",
            "harbor_holdout_reward",
            "harbor_hard_reward",
        )
    )
    assert gates == {
        "standalone-skill-pair": "pass",
        "real-tool-reproducibility": "pass",
        "canonical-dataset-adapter": "pass",
        "document-format-coverage": "required",
        "extraction-fidelity": "pass",
        "deterministic-retrieval-40": "pass",
        "grounded-answer-harbor": "blocked-external-provider-quota",
        "cross-platform-reproducibility": "required",
        "promotion-review": "blocked-by-grounded-harbor-and-required-gates",
    }
    receipt_evidence = intake["evidence"][0]
    assert receipt_evidence["sha256"] == hashlib.sha256(
        receipt_path.read_bytes()
    ).hexdigest()
    for row in intake["evidence"]:
        path = REPO_ROOT / row["path"]
        assert path.is_file()
        if "sha256" in row:
            assert row["sha256"] == hashlib.sha256(path.read_bytes()).hexdigest()
    canonical_results = (
        REPO_ROOT / "evaluations" / "semantic-okf-harbor" / "RESULTS.md"
    ).read_text(encoding="utf-8")
    registry_readme = (
        REPO_ROOT / "evaluations" / "semantic-okf-datasets" / "README.md"
    ).read_text(encoding="utf-8")
    direct_table = (
        REPO_ROOT
        / "evaluations"
        / "semantic-okf-ensemble"
        / "EVALUATION-CONCLUSIONS.md"
    ).read_text(encoding="utf-8")
    assert (
        "| Tika + Java MALLET | `tika_mallet_fusion` | 74.8% | 71.8%"
        in canonical_results
    )
    assert (
        "| Tika + Java MALLET (experimental) | `tika_mallet_fusion` | "
        "74.82% | 87.50% | 75.44% | 71.83% | 71.67% | 61.80% | "
        "100.00% | 86.36 |"
        in direct_table
    )
    assert "| `tika-mallet` | `build-semantic-okf-tika-mallet`" in registry_readme


def test_harbor_status_binds_receipts_and_excludes_provider_failures() -> None:
    status_path = ROOT / "reports" / "harbor-campaign-status-20260723.json"
    status = json.loads(status_path.read_text(encoding="utf-8"))

    assert status["ranking_eligible"] is False
    assert status["status"] == "incomplete-external-provider-quota"
    assert status["interpretation"]["direct_retrieval_ranking_affected"] is False
    assert status["interpretation"]["provider_failure_values_are_scores"] is False
    treatments = {
        row["treatment_id"]: row for row in status["treatments"]
    }
    assert treatments["v3-original-consult-bounded-prompt"][
        "provider_context_limit_count"
    ] == 1
    bounded = treatments["v4-bounded-consult"]
    assert bounded["provider_error_code"] == "usage_limit_reached"
    assert bounded["input_tokens"] == 0
    assert bounded["output_tokens"] == 0
    assert bounded["agent_tool_calls"] == 0
    assert bounded["diagnostic"]["numeric_verifier_values_are_audit_placeholders"]

    receipts = []
    for treatment in treatments.values():
        receipts.extend(treatment.get("receipts", []))
        if "receipt" in treatment:
            receipts.append(treatment["receipt"])
    assert len(receipts) == 6
    for receipt in receipts:
        path = REPO_ROOT / receipt["path"]
        assert len(receipt["sha256"]) == 64
        if path.is_file():
            assert receipt["sha256"] == hashlib.sha256(path.read_bytes()).hexdigest()


def test_runner_has_no_download_path_and_refuses_overwrite(tmp_path: Path) -> None:
    runner = ROOT / "run_experiment.py"
    source = runner.read_text(encoding="utf-8").casefold()
    assert "requests" not in source
    assert "urlopen" not in source
    assert "download" in runner.read_text(encoding="utf-8")
    existing = tmp_path / "existing"
    existing.mkdir()
    completed = subprocess.run(
        [
            sys.executable,
            str(runner),
            "--java",
            "java",
            "--tika-home",
            "tika",
            "--mallet-home",
            "mallet",
            "--output-root",
            str(existing),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
        timeout=30,
    )

    assert completed.returncode != 0
    assert "already exists" in completed.stderr


def test_builder_only_runner_has_no_consultant_dependency_and_refuses_overwrite(
    tmp_path: Path,
) -> None:
    runner = ROOT / "run_builder_experiment.py"
    source = runner.read_text(encoding="utf-8").casefold()
    assert "consult" not in source
    assert "urlopen" not in source
    assert "requests" not in source
    existing = tmp_path / "existing-builder"
    existing.mkdir()
    completed = subprocess.run(
        [
            sys.executable,
            str(runner),
            "--java",
            "java",
            "--tika-home",
            "tika",
            "--mallet-home",
            "mallet",
            "--output-root",
            str(existing),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
        timeout=30,
    )
    assert completed.returncode != 0
    assert "already exists" in completed.stderr
