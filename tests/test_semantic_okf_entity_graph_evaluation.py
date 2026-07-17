from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import shutil
import sys
from pathlib import Path
from types import ModuleType

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
EVALUATION_ROOT = REPO_ROOT / "evaluations" / "semantic-okf-entity-graph"
EMBEDDING_ROOT = REPO_ROOT / "evaluations" / "semantic-okf-embeddings"
VALIDATOR = EVALUATION_ROOT / "scripts" / "validate_hard_ground_truth.py"
ANSWER_EVALUATOR = EVALUATION_ROOT / "scripts" / "evaluate_grounded_answers.py"
ANSWER_REVIEWER = EVALUATION_ROOT / "scripts" / "review_grounded_answers.py"
RUN_PREPARER = EVALUATION_ROOT / "scripts" / "prepare_evaluation_run.py"


def _jsonl(path: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_module(name: str, path: Path) -> ModuleType:
    sys.path.insert(0, str(path.parent))
    try:
        spec = importlib.util.spec_from_file_location(name, path)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
        return module
    finally:
        sys.path.remove(str(path.parent))


def test_expanded_benchmark_preserves_thirty_and_appends_ten_verified_questions() -> None:
    baseline = _jsonl(EMBEDDING_ROOT / "retrieval-questions.jsonl")
    hard = _jsonl(EVALUATION_ROOT / "hard-questions.jsonl")
    expanded = _jsonl(EVALUATION_ROOT / "retrieval-questions.jsonl")
    assert len(baseline) == 30
    assert len(hard) == 10
    assert expanded == baseline + hard
    assert [row["id"].split("-", 1)[0] for row in hard] == [
        f"q{number:03d}" for number in range(31, 41)
    ]
    assert all(set(row) == {"id", "question", "qrels"} for row in hard)


def test_ground_truth_validator_rechecks_claim_lines_page_ranges_and_hashes() -> None:
    validator = _load_module("test_entity_graph_ground_truth_validator", VALIDATOR)
    validator.validate_all(REPO_ROOT, EVALUATION_ROOT)
    record = _jsonl(EVALUATION_ROOT / "hard-ground-truth.jsonl")[0]
    changed = copy.deepcopy(record)
    changed["authoritative_evidence"][0]["paper_evidence"][0]["text_sha256"] = "0" * 64
    with pytest.raises(validator.ValidationError, match="paper locator, offsets, or text hash mismatch"):
        validator.validate_ground_truth_record(REPO_ROOT, changed)


def test_skill_arena_config_is_paired_causal_and_hash_bound() -> None:
    config_path = EVALUATION_ROOT / "skill-arena" / "entity-graph-hard10.yaml"
    coverage_path = EVALUATION_ROOT / "skill-arena" / "prompt-coverage.json"
    manifest = json.loads(
        (EVALUATION_ROOT / "skill-arena" / "config-manifest.json").read_text(encoding="utf-8")
    )
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    profiles = {profile["id"]: profile for profile in config["comparison"]["profiles"]}
    assert set(profiles) == {"knowledge-only-control", "entity-graph-consult-treatment"}
    assert profiles["knowledge-only-control"]["capabilities"] == {}
    treatment_skills = profiles["entity-graph-consult-treatment"]["capabilities"]["skills"]
    assert len(treatment_skills) == 1
    assert treatment_skills[0]["source"]["skillId"] == "consult-semantic-okf-entity-graph"
    assert len(config["workspace"]["sources"]) == 1
    assert len(config["task"]["prompts"]) == 10
    assert len(config["comparison"]["variants"]) == 1
    assert manifest["question_count"] == 10
    assert manifest["configs"][0]["sha256"] == _sha256(config_path)
    assert manifest["coverage_sha256"] == _sha256(coverage_path)
    coverage = json.loads(coverage_path.read_text(encoding="utf-8"))
    assert len(coverage["cases"]) == 10
    assert len({case["taskFamily"] for case in coverage["cases"]}) == 9
    assert {case["caseKind"] for case in coverage["cases"]} == {
        "naturalistic-forward",
        "generalization",
        "boundary-recovery",
    }


def test_retrieval_summary_compares_twelve_routes_with_valid_evidence() -> None:
    summary = json.loads((EVALUATION_ROOT / "retrieval-summary.json").read_text(encoding="utf-8"))
    assert summary["schema_version"] == "semantic-okf-entity-graph-retrieval-summary/1.0"
    assert summary["question_count"] == 40
    assert summary["cohorts"] == {"original_30": 30, "hard_10": 10}
    assert summary["route_order"] == [
        "legacy_lexical",
        "new_lexical",
        "vector",
        "hybrid",
        "entity_graph_lexical",
        "entity_graph_entity",
        "entity_graph_traversal",
        "entity_graph_fusion",
        "classical_bm25",
        "classical_topic",
        "classical_association",
        "classical_fusion",
    ]
    for run in summary["runs"].values():
        assert run["query_count"] == 40
        assert run["core_semantic_parity"]["status"] == "pass"
        for route in run["routes"].values():
            assert route["error_count"] == 0
            assert route["evidence_validity"]["ratio"] == 1.0
            assert route["evidence_validity"]["invalid"] == 0

    top = summary["runs"]["top10"]["routes"]
    graph_hard = top["entity_graph_fusion"]["hard_10"]["paper"]["recall_at_10"]
    legacy_hard = top["legacy_lexical"]["hard_10"]["paper"]["recall_at_10"]
    classical_hard = top["classical_fusion"]["hard_10"]["paper"]["recall_at_10"]
    assert graph_hard == pytest.approx(0.91666667)
    assert legacy_hard < graph_hard < classical_hard
    assert top["entity_graph_lexical"]["all_40"]["paper"]["mrr_at_10"] == pytest.approx(
        0.96666667
    )


def test_grounded_answer_summary_separates_retrieval_from_answer_contract_results() -> None:
    summary = json.loads(
        (EVALUATION_ROOT / "grounded-answer-summary.json").read_text(encoding="utf-8")
    )
    assert summary["schema_version"] == "semantic-okf-grounded-answer-comparison/1.1"
    assert summary["question_count"] == 10
    assert summary["answer_count"] == 80
    assert summary["method_order"] == ["legacy", "embedding", "classical", "entity_graph"]
    assert sum(report["review_count"] for report in summary["reviews"]) == 80
    assert all(report["blinded"] is True for report in summary["reviews"])
    expected_profiles = {
        "legacy": {"knowledge-only-control", "legacy-consult-treatment"},
        "embedding": {"knowledge-only-control", "embedding-consult-treatment"},
        "classical": {"knowledge-only-control", "classical-consult-treatment"},
        "entity_graph": {"knowledge-only-control", "entity-graph-consult-treatment"},
    }
    assert {method: set(profiles) for method, profiles in summary["aggregates"].items()} == expected_profiles
    for profiles in summary["aggregates"].values():
        for aggregate in profiles.values():
            assert aggregate["answer_count"] == 10
            assert set(aggregate["metrics"]) == set(summary["metric_contract"])
            assert all(0.0 <= value <= 1.0 for value in aggregate["metrics"].values())
    assert summary["paired_deltas"]["embedding"]["grounding"] > 0
    assert summary["paired_deltas"]["entity_graph"]["grounding"] < 0
    assert len(summary["answers"]) == len({row["answer_id"] for row in summary["answers"]}) == 80
    assert all("output" not in row for row in summary["answers"])


def test_manual_queries_cover_every_graph_route_and_preserve_bundle() -> None:
    report = json.loads(
        (EVALUATION_ROOT / "manual-query-verification.json").read_text(encoding="utf-8")
    )
    assert report["schema_version"] == "semantic-okf-entity-graph-manual-query-verification/1.0"
    assert report["status"] == "pass"
    assert report["bundle_unchanged"] is True
    assert report["bundle_tree_before"] == report["bundle_tree_after"]
    assert [case["mode"] for case in report["results"]] == [
        "lexical",
        "entity",
        "traversal",
        "fusion",
    ]
    assert all(case["all_sections_exact"] for case in report["results"])
    assert all(case["all_concept_paths_exist"] for case in report["results"])
    assert all(case["discovery_only"] is True for case in report["results"])


def test_append_only_run_manifest_binds_workspace_and_completed_outputs(tmp_path: Path) -> None:
    preparer = _load_module("test_entity_graph_run_preparer", RUN_PREPARER)
    run = tmp_path / "run-001"
    bundle = run / "workspaces" / "entity-graph" / "knowledge"
    (bundle / "semantic").mkdir(parents=True)
    (bundle / "semantic" / "build-report.json").write_text(
        json.dumps({"status": "pass", "valid": True}) + "\n", encoding="utf-8"
    )
    (bundle / "semantic" / "records.jsonl").write_text(
        json.dumps({"source_id": "source", "record_id": "record"}) + "\n",
        encoding="utf-8",
    )
    (bundle / "index.md").write_text("authoritative\n", encoding="utf-8")
    core_hash = preparer._logical_tree_sha256(bundle, preparer._relative_files(bundle, core_only=True))
    (bundle / "entity-graph").mkdir()
    (bundle / "entity-graph" / "index.json").write_text("{}\n", encoding="utf-8")
    (bundle / "entity-graph" / "build-report.json").write_text(
        json.dumps(
            {
                "status": "pass",
                "valid": True,
                "core": {"tree_sha256": core_hash},
            }
        )
        + "\n",
        encoding="utf-8",
    )

    manifest = preparer._manifest(run)
    assert manifest["parity"]["status"] == "pass"
    assert manifest["parity"]["logical_core_tree_sha256"] == core_hash
    assert set(manifest["bundles"]) == {"entity-graph"}
    input_manifest = preparer._write_manifest(run)
    assert input_manifest.is_file()
    for relative in (
        "retrieval/top10/comparison.json",
        "retrieval/pool100/comparison.json",
        "skill-arena/entity-graph/promptfoo-results.json",
        "skill-arena/reviews/reviews.json",
    ):
        path = run / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("{}\n", encoding="utf-8")
    external = tmp_path / "compact-summary.json"
    external.write_text("{}\n", encoding="utf-8")
    final = preparer._finalize(run, [f"summary={external}"])
    report = json.loads(final.read_text(encoding="utf-8"))
    assert report["schema_version"] == "semantic-okf-entity-graph-run/1.0"
    assert report["status"] == "pass"
    assert report["append_only"] is True
    assert report["external_artifacts"][0]["name"] == "summary"
    with pytest.raises(FileExistsError, match="run manifest already exists"):
        preparer._finalize(run, [])

    changed = tmp_path / "changed-run"
    shutil.copytree(run, changed)
    (changed / "run-manifest.json").unlink()
    changed_bundle = changed / "workspaces" / "entity-graph" / "knowledge"
    (changed_bundle / "index.md").write_text("drifted\n", encoding="utf-8")
    with pytest.raises(ValueError, match="workspaces changed"):
        preparer._finalize(changed, [])


def test_blinded_reviewer_contract_and_multi_report_evidence_validation() -> None:
    reviewer = _load_module("test_entity_graph_answer_reviewer", ANSWER_REVIEWER)
    task = {
        "answer_id": "opaque",
        "candidate": {"claims": [{"statement": "x", "supporting_claim_ids": ["c"]}]},
        "ground_truth": {
            "answer_claims": [{"id": "a"}],
            "important_negatives": [{"id": "n"}],
        },
    }
    review = {
        "answer_id": "opaque",
        "claim_fidelity": [{"index": 0, "score": 1}],
        "atomic_scores": {"a": 0.5},
        "negative_scores": {"n": 1},
        "note": "Faithful and partly complete.",
    }
    assert reviewer._validate_review(copy.deepcopy(review), task) == review
    broken = copy.deepcopy(review)
    broken["negative_scores"] = {}
    with pytest.raises(ValueError, match="ground-truth IDs"):
        reviewer._validate_review(broken, task)

    evaluator = _load_module("test_entity_graph_answer_evaluator", ANSWER_EVALUATOR)
    bundle = (
        REPO_ROOT
        / "evaluations"
        / "graphrag-cross-paper"
        / "fixtures"
        / "workspaces"
        / "skill-overlay"
        / "knowledge"
    )
    records, paper_records = evaluator._records(bundle)
    record = records["claim-2506-05690v3-043"]
    item = {
        "claim_id": record["record_id"],
        "concept_path": f"knowledge/{record['concept_path']}",
        "paper_id": "2506.05690v3",
        "source_path": record["source_path"],
        "locators": [7, "PDF-page-8"],
    }
    assert evaluator._score_evidence_item(
        item, bundle, records, paper_records, {"2506.05690v3": {7, 8}}
    )[0] is True
