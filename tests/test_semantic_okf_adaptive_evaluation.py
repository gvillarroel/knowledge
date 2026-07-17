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
EVALUATION_ROOT = REPO_ROOT / "evaluations" / "semantic-okf-adaptive"
EMBEDDING_ROOT = REPO_ROOT / "evaluations" / "semantic-okf-embeddings"
HISTORICAL_ADAPTIVE_SKILL_MD_SHA256 = (
    "d44f364fc50d3c41721d12f5ea782036c1192ad6bdd4b2254dce42d956c6afbb"
)
HISTORICAL_ADAPTIVE_SKILL_TREE_SHA256 = (
    "e520ac45d7e1d01608be56b82d8be3a444a04c29a18b4448e454fcbacc2070f4"
)
HISTORICAL_ADAPTIVE_RUNTIME_SHA256 = (
    "877e06a1e553d3afa625aed2e40dbf596940ac142665446b045821ae42778057"
)


def _jsonl(path: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _tree_manifest_sha256(root: Path) -> str:
    rows = []
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        if "__pycache__" in path.parts:
            continue
        rows.append(f"{path.relative_to(root).as_posix()}\0{_sha256(path)}\n")
    return hashlib.sha256("".join(rows).encode("utf-8")).hexdigest()


def _load_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _synthetic_raw(summary: dict[str, object]) -> dict[str, object]:
    routes = summary["routes"]
    raw_routes = []
    for name in summary["route_order"]:
        route = routes[name]
        queries = [
            {
                "question_id": f"q{number:03d}",
                "paper_metrics": dict(route["all_40"]),
            }
            for number in range(1, 41)
        ]
        raw_routes.append(
            {
                "name": name,
                "query_count": 40,
                "error_count": route["error_count"],
                "evidence_validity": dict(route["evidence_validity"]),
                "paper_metrics": dict(route["all_40"]),
                "cohorts": {
                    "original_30": {"paper_metrics": dict(route["original_30"])},
                    "hard_10": {"paper_metrics": dict(route["hard_10"])},
                },
                "timing_ms": dict(route["timing_ms"]),
                "queries": queries,
            }
        )
    return {
        "schema_version": "1.5",
        "query_count": 40,
        "top_k": 10,
        "comparison": "synthetic contract fixture",
        "extends_evidence_schema": "1.2",
        "core_semantic_parity": {"status": "pass", "pairs": [1]},
        "bundles": {
            "adaptive": {
                "fingerprint": {
                    "key_artifacts": {
                        "semantic/records.jsonl": {"sha256": "0" * 64}
                    }
                }
            }
        },
        "routes": raw_routes,
    }


def test_expanded_benchmark_preserves_thirty_and_same_ten_hard_questions() -> None:
    baseline = _jsonl(EMBEDDING_ROOT / "retrieval-questions.jsonl")
    hard = _jsonl(EVALUATION_ROOT / "hard-questions.jsonl")
    expanded = _jsonl(EVALUATION_ROOT / "retrieval-questions.jsonl")

    assert len(baseline) == 30
    assert len(hard) == 10
    assert expanded == baseline + hard
    assert [row["id"].split("-", 1)[0] for row in hard] == [
        f"q{number:03d}" for number in range(31, 41)
    ]


def test_adaptive_plan_is_closed_and_records_conservative_no_regression_policy() -> None:
    plan = json.loads((EVALUATION_ROOT / "adaptive-plan.json").read_text(encoding="utf-8"))

    assert set(plan) == {
        "schema_version",
        "selection",
        "passages",
        "evidence_identity",
        "tokenization",
        "bm25",
        "associations",
        "topics",
        "expansion",
        "reranking",
        "adaptive",
    }
    assert plan["adaptive"] == {
        "maximum_aspects": 8,
        "minimum_aspect_tokens": 4,
        "full_query_weight": 2.0,
        "aspect_weight": 0.25,
        "best_aspect_weight": 0.0,
        "rrf_k": 0,
        "protected_full_results": 9,
        "maximum_novel_aspect_rank": 1,
    }
    assert len(plan["selection"]["source_ids"]) == 30
    assert plan["passages"]["default_mode"] == "full-record"
    assert len(plan["passages"]["markdown_pdf_page_source_ids"]) == 15
    assert plan["evidence_identity"]["default_mode"] == "source-record"
    assert len(plan["evidence_identity"]["paper_ids_by_source"]) == 30


def test_skill_arena_config_is_isolated_paired_and_hash_bound() -> None:
    config_path = EVALUATION_ROOT / "skill-arena" / "adaptive-hard10.yaml"
    coverage_path = EVALUATION_ROOT / "skill-arena" / "prompt-coverage.json"
    manifest = json.loads(
        (EVALUATION_ROOT / "skill-arena" / "config-manifest.json").read_text(encoding="utf-8")
    )
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    profiles = {profile["id"]: profile for profile in config["comparison"]["profiles"]}

    assert set(profiles) == {"knowledge-only-control", "adaptive-consult-treatment"}
    assert profiles["knowledge-only-control"]["capabilities"] == {}
    skills = profiles["adaptive-consult-treatment"]["capabilities"]["skills"]
    assert len(skills) == 1
    assert skills[0]["source"]["skillId"] == "consult-semantic-okf-adaptive"
    assert len(config["workspace"]["sources"]) == 1
    assert len(config["task"]["prompts"]) == 10
    assert config["comparison"]["variants"][0]["agent"]["model"] == "openai-codex/gpt-5.6-luna"
    assert manifest["configs"][0]["sha256"] == _sha256(config_path)
    assert manifest["coverage_sha256"] == _sha256(coverage_path)
    assert manifest["adaptive_plan_file_sha256"] == _sha256(
        EVALUATION_ROOT / "adaptive-plan.json"
    )
    assert manifest["consult_skill_md_sha256"] == HISTORICAL_ADAPTIVE_SKILL_MD_SHA256
    assert manifest["consult_skill_tree_sha256"] == HISTORICAL_ADAPTIVE_SKILL_TREE_SHA256


def test_retrieval_summary_compares_thirteen_routes_with_valid_evidence() -> None:
    summary = json.loads((EVALUATION_ROOT / "retrieval-summary.json").read_text(encoding="utf-8"))

    assert summary["schema_version"] == "semantic-okf-adaptive-retrieval-summary/1.0"
    assert summary["question_count"] == 40
    assert len(summary["route_order"]) == 13
    assert summary["route_order"][-1] == "adaptive_fusion"
    assert summary["core_semantic_parity"]["status"] == "pass"
    for route in summary["routes"].values():
        assert route["query_count"] == 40
        assert route["error_count"] == 0
        assert route["evidence_validity"]["ratio"] == 1.0
        assert route["evidence_validity"]["invalid"] == 0

    adaptive = summary["routes"]["adaptive_fusion"]
    classical = summary["routes"]["classical_fusion"]
    assert adaptive["all_40"]["recall_at_10"] > classical["all_40"]["recall_at_10"]
    assert adaptive["all_40"]["ndcg_at_10"] > classical["all_40"]["ndcg_at_10"]
    assert adaptive["hard_10"] == classical["hard_10"]
    assert summary["winners"]["all_40"]["recall_at_10"]["routes"] == ["adaptive_fusion"]
    assert summary["latency_ratio_vs_classical_fusion"] > 3.0
    impact = summary["paired_question_impact"]
    assert impact["any_metric_changed_question_ids"] == ["q011-vector-graph-hybrid"]
    assert impact["metrics"]["recall_at_10"]["positive_questions"] == 1
    assert impact["metrics"]["recall_at_10"]["negative_questions"] == 0
    assert impact["metrics"]["recall_at_10"]["bootstrap_95_percentile_ci"][0] == 0


def test_compact_summarizer_rejects_a_weakened_route_contract(tmp_path: Path) -> None:
    summarizer = _load_module(
        "test_adaptive_retrieval_summarizer",
        EVALUATION_ROOT / "scripts" / "summarize_retrieval.py",
    )
    summary = json.loads((EVALUATION_ROOT / "retrieval-summary.json").read_text(encoding="utf-8"))
    raw = _synthetic_raw(summary)
    raw["routes"][-1]["evidence_validity"]["ratio"] = 0.99
    changed = tmp_path / "changed.json"
    changed.write_text(json.dumps(raw), encoding="utf-8")

    with pytest.raises(ValueError, match="fully valid evidence"):
        summarizer.summarize(changed)


def test_compact_summarizer_interpretation_follows_metrics() -> None:
    summarizer = _load_module(
        "test_adaptive_retrieval_summarizer_interpretation",
        EVALUATION_ROOT / "scripts" / "summarize_retrieval.py",
    )
    summary = json.loads((EVALUATION_ROOT / "retrieval-summary.json").read_text(encoding="utf-8"))
    adaptive = summary["routes"]["adaptive_fusion"]
    classical = summary["routes"]["classical_fusion"]
    adaptive["all_40"]["recall_at_10"] = classical["all_40"]["recall_at_10"] - 0.1
    adaptive["all_40"]["ndcg_at_10"] = classical["all_40"]["ndcg_at_10"] - 0.1
    adaptive["hard_10"]["recall_at_10"] = classical["hard_10"]["recall_at_10"] - 0.1
    summary["adaptive_vs_classical_fusion"]["all_40"]["recall_at_10"] = -0.1
    summary["adaptive_vs_classical_fusion"]["all_40"]["ndcg_at_10"] = -0.1
    summary["adaptive_vs_classical_fusion"]["hard_10"]["recall_at_10"] = -0.1

    rendered = summarizer.render_markdown(summary)

    assert "not the sole all-40 winner" in rendered
    assert "adaptive versus classical deltas" in rendered
    assert "tie exactly" not in rendered


def test_reproducibility_and_manual_reports_are_hash_bound_and_read_only() -> None:
    environment = json.loads(
        (EVALUATION_ROOT / "evaluation-environment.json").read_text(encoding="utf-8")
    )
    determinism = json.loads(
        (EVALUATION_ROOT / "determinism-report.json").read_text(encoding="utf-8")
    )
    manual = json.loads(
        (EVALUATION_ROOT / "manual-query-verification.json").read_text(encoding="utf-8")
    )

    assert environment["bindings"]["comparator_sha256"] == _sha256(
        EVALUATION_ROOT / "scripts" / "compare_retrieval.py"
    )
    assert (
        environment["bindings"]["adaptive_runtime_module_sha256"]
        == HISTORICAL_ADAPTIVE_RUNTIME_SHA256
    )
    assert (
        environment["bindings"]["consult_skill_md_sha256"]
        == HISTORICAL_ADAPTIVE_SKILL_MD_SHA256
    )
    assert (
        environment["bindings"]["consult_skill_tree_sha256"]
        == HISTORICAL_ADAPTIVE_SKILL_TREE_SHA256
    )
    assert environment["skill_arena_runtime"]["accepted_eval_id"] == (
        "eval-Iue-2026-07-14T17:50:18"
    )
    assert environment["skill_arena_runtime"]["completed_cells"] == 20
    assert environment["skill_arena_runtime"]["execution_errors"] == 0
    assert environment["bindings"]["grounded_answer_summary_sha256"] == _sha256(
        EVALUATION_ROOT / "grounded-answer-summary.json"
    )
    assert environment["bindings"]["answer_final_run_summary_sha256"] == _sha256(
        EVALUATION_ROOT / "skill-arena" / "final-run-summary.json"
    )
    assert determinism["status"] == "pass"
    assert determinism["clean_rebuild"]["file_count_each"] == 890
    assert determinism["clean_rebuild"]["differing_file_hashes"] == 0
    assert determinism["hash_seed_replay"]["differing_outputs"] == 0
    assert manual["status"] == "pass"
    assert manual["inspection"]["independent_rederivation"] is True
    assert manual["query"]["evidence_rows_complete"] is True
    assert manual["read_only_check"]["unchanged"] is True


def test_english_conclusions_cover_every_route_and_the_single_question_limit() -> None:
    conclusions = (EVALUATION_ROOT / "EVALUATION-CONCLUSIONS.md").read_text(encoding="utf-8")
    for label in (
        "Legacy",
        "Embedding",
        "Entity graph",
        "Classical",
        "Adaptive",
        "BM25",
        "topic",
        "association",
        "traversal",
        "vector",
        "hybrid",
    ):
        assert label.lower() in conclusions.lower()
    assert "q011-vector-graph-hybrid" in conclusions
    assert "other 39" in conclusions
    assert "do not establish answer correctness" in conclusions
    assert "Actual grounded-answer comparison" in conclusions
    assert "93.58%" in conclusions
    assert "57.25%" in conclusions
    assert "serializer outside the answer model" in conclusions
    assert (REPO_ROOT / ".specs" / "adr" / "0021-adaptive-evidence-fusion-semantic-okf-retrieval.md").is_file()


def test_grounded_answer_summary_compares_five_paired_methods_and_one_hundred_answers() -> None:
    summary = json.loads(
        (EVALUATION_ROOT / "grounded-answer-summary.json").read_text(encoding="utf-8")
    )

    assert summary["schema_version"] == "semantic-okf-grounded-answer-comparison/1.1"
    assert summary["question_count"] == 10
    assert summary["answer_count"] == 100
    assert summary["method_count"] == 5
    assert summary["profiles_per_method"] == 2
    assert summary["method_order"] == [
        "legacy",
        "embedding",
        "classical",
        "entity_graph",
        "adaptive",
    ]
    assert len(summary["answers"]) == 100
    assert len({row["answer_id"] for row in summary["answers"]}) == 100
    assert sum(report["review_count"] for report in summary["reviews"]) == 100
    assert all(report["blinded"] is True for report in summary["reviews"])

    for method in summary["method_order"]:
        profiles = summary["aggregates"][method]
        assert len(profiles) == 2
        assert {aggregate["answer_count"] for aggregate in profiles.values()} == {10}
        for aggregate in profiles.values():
            assert aggregate["strict_full_pass_rate"] == 0.0
            assert all(0.0 <= value <= 1.0 for value in aggregate["metrics"].values())

    adaptive = summary["aggregates"]["adaptive"]
    control = adaptive["knowledge-only-control"]["metrics"]
    treatment = adaptive["adaptive-consult-treatment"]["metrics"]
    delta = summary["paired_deltas"]["adaptive"]
    assert treatment["claim_correctness"] == pytest.approx(0.93583333)
    assert treatment["semantic_completeness"] == pytest.approx(0.5725)
    assert treatment["evidence_validity"] == pytest.approx(0.59333333)
    assert treatment["grounding"] == pytest.approx(0.6)
    assert control["semantic_completeness"] > treatment["semantic_completeness"]
    assert delta["semantic_completeness"] == pytest.approx(-0.33)
    assert delta["exact_atomic_evidence_coverage"] == pytest.approx(-0.54)


def test_final_answer_run_is_bound_without_requiring_ignored_raw_outputs() -> None:
    final = json.loads(
        (EVALUATION_ROOT / "skill-arena" / "final-run-summary.json").read_text(
            encoding="utf-8"
        )
    )
    diagnostic = json.loads(
        (EVALUATION_ROOT / "skill-arena" / "diagnostic-run-summary.json").read_text(
            encoding="utf-8"
        )
    )

    assert final["schema_version"] == "semantic-okf-adaptive-answer-final-run/1.0"
    assert final["status"] == "accepted-final-observation"
    assert final["eval_id"] == "eval-Iue-2026-07-14T17:50:18"
    assert final["cells"] == {
        "requested": 20,
        "completed": 20,
        "errors": 0,
        "strict_passes": 0,
        "duration_ms": 1029977,
    }
    assert final["bindings"]["grounded_answer_summary_sha256"] == _sha256(
        EVALUATION_ROOT / "grounded-answer-summary.json"
    )
    assert final["bindings"]["grounded_answer_markdown_sha256"] == _sha256(
        EVALUATION_ROOT / "grounded-answer-summary.md"
    )
    assert final["bindings"]["consult_skill_md_sha256"] == HISTORICAL_ADAPTIVE_SKILL_MD_SHA256
    assert final["bindings"]["consult_skill_tree_sha256"] == HISTORICAL_ADAPTIVE_SKILL_TREE_SHA256
    for digest in final["bindings"].values():
        assert len(digest) == 64
        assert set(digest) <= set("0123456789abcdef")

    assert diagnostic["status"] == "superseded-after-diagnostic-fix"
    assert diagnostic["eval_id"] != final["eval_id"]
    assert "not an untouched generalization estimate" in diagnostic["interpretation_boundary"]
