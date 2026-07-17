from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
ROOT = REPO_ROOT / "evaluations" / "semantic-okf-adaptive-evolution"
COVERAGE_SCRIPT = ROOT / "scripts" / "evaluate_coverage_pack.py"
COVERAGE_REPORT = ROOT / "coverage-pack-summary.json"
TASK_SHA256 = "da2fffaf3ea60976802ed6782633e9b2f079a6ddf65510d98a8c426c854d4a4b"
CONFIGS = [
    ROOT / "skill-arena" / "g000-candidate07-hard10.yaml",
    ROOT / "skill-arena" / "g001-candidate10-hard10.yaml",
    ROOT / "skill-arena" / "g002-candidate11-hard10.yaml",
]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _module() -> ModuleType:
    name = "test_semantic_okf_adaptive_coverage_evaluator"
    specification = importlib.util.spec_from_file_location(name, COVERAGE_SCRIPT)
    assert specification and specification.loader
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


def _canonical_sha256(value: object) -> str:
    serialized = json.dumps(value, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def test_generation_tasks_are_identical_and_frozen_across_configs() -> None:
    configs = [yaml.safe_load(path.read_text(encoding="utf-8")) for path in CONFIGS]

    assert all(_canonical_sha256(config["task"]) == TASK_SHA256 for config in configs)
    assert configs[0]["task"] == configs[1]["task"] == configs[2]["task"]
    assert [prompt["id"] for prompt in configs[0]["task"]["prompts"]] == [
        f"q{number:03d}-{suffix}"
        for number, suffix in [
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
        ]
    ]


def test_generation_summaries_bind_current_configs_and_skill_files() -> None:
    generation_1 = json.loads((ROOT / "generation-001-summary.json").read_text(encoding="utf-8"))
    generation_2 = json.loads((ROOT / "generation-002-summary.json").read_text(encoding="utf-8"))
    final_validation = json.loads(
        (ROOT / "final-validation-summary.json").read_text(encoding="utf-8")
    )

    for report in (generation_1, generation_2):
        config_path = REPO_ROOT / report["skill_arena"]["config"]
        assert _sha256(config_path) == report["skill_arena"]["config_sha256"]
        assert report["skill_arena"]["task_canonical_sha256"] == TASK_SHA256
        assert report["skill_arena"]["completed_cells"] == 20
        assert report["skill_arena"]["execution_errors"] == 0

    bindings = generation_2["skill_bindings"]
    assert _sha256(REPO_ROOT / "skills/consult-semantic-okf-adaptive/SKILL.md") == bindings[
        "consult_skill_md_sha256"
    ]
    assert _sha256(
        REPO_ROOT / "skills/consult-semantic-okf-adaptive/scripts/_adaptive_snapshot.py"
    ) == bindings["consult_runtime_sha256"]
    assert _sha256(
        REPO_ROOT / "skills/consult-semantic-okf-adaptive/scripts/query_semantic_okf_adaptive.py"
    ) == bindings["consult_cli_sha256"]
    assert generation_2["decision"] == "keep-pareto-survivor"
    assert generation_1["decision"] == "discard-policy-retain-mechanisms"
    assert final_validation["status"] == "pass"
    assert final_validation["checks"]["deterministic_real_rebuild"]["file_count_each"] == 891
    assert final_validation["checks"]["deterministic_real_rebuild"]["differing_file_hashes"] == 0
    assert final_validation["checks"]["full_repository_tests"]["passed"] == 1226
    assert final_validation["checks"]["application_coverage_gate"][
        "application_coverage_percent"
    ] == pytest.approx(90.9)
    checked_bindings = {
        "expected_id_audit_sha256": ROOT / "expected-id-audit.json",
        "evaluation_conclusions_sha256": ROOT / "EVALUATION-CONCLUSIONS.md",
        "evolution_readme_sha256": ROOT / "README.md",
        "generation_2_summary_sha256": ROOT / "generation-002-summary.json",
        "coverage_pack_summary_sha256": ROOT / "coverage-pack-summary.json",
        "adr_0022_sha256": REPO_ROOT / ".specs/adr/0022-frozen-adaptive-semantic-okf-evolution.md",
        "build_skill_md_sha256": REPO_ROOT / "skills/build-semantic-okf-adaptive/SKILL.md",
        "consult_skill_md_sha256": REPO_ROOT / "skills/consult-semantic-okf-adaptive/SKILL.md",
    }
    for key, path in checked_bindings.items():
        assert _sha256(path) == final_validation["bindings"][key]


def test_coverage_report_is_hash_bound_deterministic_and_budget_labeled() -> None:
    report = json.loads(COVERAGE_REPORT.read_text(encoding="utf-8"))
    runtime = REPO_ROOT / report["inputs"]["runtime"]
    questions = REPO_ROOT / "evaluations/semantic-okf-adaptive/hard-questions.jsonl"
    ground_truth = REPO_ROOT / "evaluations/semantic-okf-adaptive/hard-ground-truth.jsonl"

    assert report["schema_version"] == "semantic-okf-adaptive-coverage-pack-evaluation/1.0"
    assert report["status"] == "pass"
    assert report["protocol"] == {
        "candidate_budget_warning": "facet union has a larger variable budget and is not Recall@30",
        "maximum_facets": 12,
        "per_facet": 12,
        "primary_top_k": 30,
        "repetitions_per_question": 3,
    }
    assert set(report["hard_gates"].values()) == {True, 1.0}
    assert _sha256(runtime) == report["inputs"]["runtime_sha256"]
    assert _sha256(questions) == report["inputs"]["questions_sha256"]
    assert _sha256(ground_truth) == report["inputs"]["ground_truth_sha256"]
    assert len(report["questions"]) == 10
    assert report["metrics"]["primary_answer_claim_recall_at_30"] == pytest.approx(0.6)
    assert report["metrics"]["facet_union_answer_claim_coverage"] == pytest.approx(0.765)
    assert report["metrics"]["facet_union_important_negative_coverage"] == pytest.approx(
        0.8833333333333334
    )
    assert report["metrics"]["facet_union_required_paper_coverage"] == pytest.approx(1.0)
    assert report["metrics"]["unique_candidate_claims"]["mean"] == pytest.approx(81.0)


def test_coverage_candidate_validation_rejects_binding_drift() -> None:
    module = _module()
    binding = {
        "record_id": "claim-1",
        "paper_id": "paper-1",
        "authoritative_text": "reviewed text",
        "concept_path": "concepts/claim-1.md",
        "source_path": "sources/claims/paper-1.jsonl",
        "locator_tokens": ["PDF-page-7", "PDF-page-7"],
        "citation_pages": [7, 7],
    }
    candidate = {
        "rank": 1,
        "claim_id": "claim-1",
        "paper_id": "paper-1",
        "authoritative_text": "reviewed text",
        "concept_path": "concepts/claim-1.md",
        "source_path": "sources/claims/paper-1.jsonl",
        "locators": ["PDF-page-7"],
        "citation_pages": [7],
    }

    module._validate_candidate(candidate, binding, 1)
    changed = {**candidate, "paper_id": "paper-2"}
    with pytest.raises(module.CoverageError, match="differs from its binding"):
        module._validate_candidate(changed, binding, 1)


def test_conclusions_keep_retrieval_and_variable_budget_metrics_separate() -> None:
    conclusions = (ROOT / "EVALUATION-CONCLUSIONS.md").read_text(encoding="utf-8")

    assert "Direct retrieval comparison over the frozen forty questions" in conclusions
    assert "The facet union averages 7.1 facets and 81 unique candidates" in conclusions
    assert "must not be mislabeled as Recall@30" in conclusions
    assert "Exact-ID coverage remains deliberately stricter than semantic correctness" in conclusions
