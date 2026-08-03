"""Tests for the post-v51 unseen-question evaluation utilities."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
BUILD_PATH = (
    ROOT
    / "evaluations"
    / "graphrag-unseen-generalization"
    / "scripts"
    / "build_benchmark.py"
)
AGGREGATE_PATH = (
    ROOT
    / "evaluations"
    / "graphrag-unseen-generalization"
    / "scripts"
    / "aggregate_reports.py"
)
PARALLEL_BUILD_PATH = (
    ROOT
    / "evaluations"
    / "graphrag-unseen-generalization"
    / "scripts"
    / "build_parallel_benchmark.py"
)
POLICY_PATH = (
    ROOT
    / "evaluations"
    / "graphrag-unseen-generalization"
    / "scripts"
    / "validate_evaluation_only.py"
)
COHORT_AGGREGATE_PATH = (
    ROOT
    / "evaluations"
    / "graphrag-unseen-generalization"
    / "scripts"
    / "aggregate_cohorts.py"
)
GENERAL_FREEZE_PATH = (
    ROOT
    / "evaluations"
    / "graphrag-unseen-generalization"
    / "scripts"
    / "freeze_general_strategies.py"
)
GENERAL_AGGREGATE_PATH = (
    ROOT
    / "evaluations"
    / "graphrag-unseen-generalization"
    / "scripts"
    / "aggregate_general_strategies.py"
)
QUALITY_LATENCY_PATH = (
    ROOT
    / "evaluations"
    / "graphrag-unseen-generalization"
    / "scripts"
    / "analyze_quality_latency.py"
)
CONTRADICTION_BUILD_PATH = (
    ROOT
    / "evaluations"
    / "graphrag-unseen-generalization"
    / "scripts"
    / "build_contradiction_benchmark.py"
)
CONTRADICTION_FREEZE_PATH = (
    ROOT
    / "evaluations"
    / "graphrag-unseen-generalization"
    / "scripts"
    / "freeze_contradiction_population.py"
)
CONTRADICTION_AGGREGATE_PATH = (
    ROOT
    / "evaluations"
    / "graphrag-unseen-generalization"
    / "scripts"
    / "aggregate_contradiction_strategies.py"
)


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


BUILD = _load("test_generalization_build", BUILD_PATH)
AGGREGATE = _load("test_generalization_aggregate", AGGREGATE_PATH)
PARALLEL_BUILD = _load("test_parallel_generalization_build", PARALLEL_BUILD_PATH)
POLICY = _load("test_evaluation_only_policy", POLICY_PATH)
COHORT_AGGREGATE = _load(
    "test_generalization_cohort_aggregate",
    COHORT_AGGREGATE_PATH,
)
GENERAL_FREEZE = _load("test_general_strategy_freeze", GENERAL_FREEZE_PATH)
GENERAL_AGGREGATE = _load(
    "test_general_strategy_aggregate",
    GENERAL_AGGREGATE_PATH,
)
QUALITY_LATENCY = _load(
    "test_general_strategy_quality_latency",
    QUALITY_LATENCY_PATH,
)
CONTRADICTION_BUILD = _load(
    "test_contradiction_benchmark_build",
    CONTRADICTION_BUILD_PATH,
)
CONTRADICTION_FREEZE = _load(
    "test_contradiction_population_freeze",
    CONTRADICTION_FREEZE_PATH,
)
CONTRADICTION_AGGREGATE = _load(
    "test_contradiction_strategy_aggregate",
    CONTRADICTION_AGGREGATE_PATH,
)


def test_ngram_novelty_helpers() -> None:
    assert BUILD._tokens("Graph-RAG, graph.") == ("graph-rag", "graph")
    assert ("one", "two") in BUILD._ngrams("one two three", 2)
    assert BUILD._jaccard({"a"}, {"a", "b"}) == pytest.approx(0.5)


def test_source_ids_are_sorted_and_complete() -> None:
    assert BUILD._source_ids(["2502.14902v2"]) == [
        "claims-2502-14902v2",
        "paper-2502-14902v2",
    ]


def test_parallel_question_plan_is_large_and_stratified() -> None:
    papers, _ = PARALLEL_BUILD._load_papers()
    specs = PARALLEL_BUILD._question_specs(papers)
    assert len(specs) == 60
    assert sum(len(spec["papers"]) == 1 for spec in specs) == 30
    assert sum(len(spec["papers"]) == 2 for spec in specs) == 20
    assert sum(len(spec["papers"]) == 3 for spec in specs) == 10
    assert all(len(PARALLEL_BUILD._tokens(spec["question"])) >= 55 for spec in specs)


def test_contradiction_question_plan_is_large_and_multi_source() -> None:
    specs = CONTRADICTION_BUILD._question_specs()
    assert len(specs) == 40
    assert sum(len(spec["sides"]) == 2 for spec in specs) == 15
    assert sum(len(spec["sides"]) == 3 for spec in specs) == 20
    assert sum(len(spec["sides"]) == 4 for spec in specs) == 5
    signatures = {
        tuple(
            sorted(
                (
                    side["paper_id"],
                    tuple(side["claim_indices"]),
                )
                for side in spec["sides"]
            )
        )
        for spec in specs
    }
    assert len(signatures) == 40


def test_contradiction_build_binds_exact_evidence_and_policy() -> None:
    outputs = CONTRADICTION_BUILD.build()
    questions = [
        json.loads(line)
        for line in outputs["retrieval-questions.jsonl"].splitlines()
    ]
    truth = [
        json.loads(line)
        for line in outputs["ground-truth.jsonl"].splitlines()
    ]
    policy = json.loads(outputs["EVALUATION_ONLY.json"])
    assert len(questions) == len(truth) == 40
    assert sum(len(row["evidence"]) for row in truth) == 230
    assert all(2 <= len(row["qrels"]["paper_ids"]) <= 4 for row in questions)
    assert all(
        evidence["source_markdown_sha256"]
        for row in truth
        for evidence in row["evidence"]
    )
    assert policy["classification"] == "evaluation-only"
    assert "skill or query-adapter evolution" in policy["forbidden_uses"]


def test_contradiction_metrics_require_every_evidence_side() -> None:
    qrels = {
        "q1": {"paper-a", "paper-b"},
        "q2": {"paper-a", "paper-b", "paper-c"},
    }
    rankings = {
        "q1": ["paper-a", "paper-b"],
        "q2": ["paper-a", "paper-b", "irrelevant"],
    }
    metrics = CONTRADICTION_AGGREGATE._ranking_metrics(rankings, qrels)
    assert metrics["recall_at_10"] == pytest.approx(5 / 6)
    assert metrics["full_evidence_set_rate_at_10"] == pytest.approx(0.5)
    assert metrics["mrr_at_10"] == pytest.approx(1.0)
    assert 0.0 < metrics["ndcg_at_10"] < 1.0


def test_evaluation_only_purpose_rejects_optimizer_use(
    tmp_path: Path,
) -> None:
    questions = tmp_path / "questions.jsonl"
    questions.write_text('{"id":"q001"}\n', encoding="utf-8", newline="\n")
    digest = POLICY._sha256(questions)
    rows = [
        {
            "dataset_id": "fixture-evaluation-only",
            "questions_sha256": digest,
        }
    ]
    with pytest.raises(POLICY.EvaluationOnlyError, match="evaluation-only"):
        POLICY.validate_purpose(rows, questions, "evolution")
    assert (
        POLICY.validate_purpose(rows, questions, "evaluation")["dataset_id"]
        == "fixture-evaluation-only"
    )


def _report(path: Path, *, candidate: str, question_sha: str = "a" * 64) -> None:
    route = {
        "name": candidate,
        "error_count": 0,
        "evidence_validity": {"ratio": 1.0},
        "paper_metrics": {
            "recall_at_10": 0.8,
            "mrr_at_10": 0.9,
            "ndcg_at_10": 0.85,
        },
        "queries": [
            {"question_id": "q101-a", "paper_ids": ["2402.07630v3"]}
        ],
        "timing_ms": {"p95": 10.0},
    }
    path.write_text(
        json.dumps(
            {
                "status": "pass",
                "inputs": {"questions": {"sha256": question_sha}},
                "query_count": 1,
                "top_k": 10,
                "routes": [route],
            }
        ),
        encoding="utf-8",
    )


def test_aggregate_requires_three_reports_and_records_stability(
    tmp_path: Path,
) -> None:
    paths = []
    for number in range(3):
        path = tmp_path / f"run-{number}.json"
        _report(path, candidate="candidate")
        paths.append(path)
    row = AGGREGATE._candidate_row("candidate", paths)
    assert row["metrics"]["ndcg_at_10"] == pytest.approx(0.85)
    assert row["representative_p95_ms"] == pytest.approx(10.0)
    assert row["deterministic"] is True
    assert row["query_stability_ratio"] == pytest.approx(1.0)


def test_aggregate_reports_ranking_drift_and_uses_metric_medians(
    tmp_path: Path,
) -> None:
    paths = []
    for number in range(3):
        path = tmp_path / f"run-{number}.json"
        _report(path, candidate="candidate")
        paths.append(path)
    payload = json.loads(paths[-1].read_text(encoding="utf-8"))
    payload["routes"][0]["queries"][0]["paper_ids"] = ["2404.16130v2"]
    payload["routes"][0]["paper_metrics"]["ndcg_at_10"] = 0.80
    paths[-1].write_text(json.dumps(payload), encoding="utf-8")
    row = AGGREGATE._candidate_row("candidate", paths)
    assert row["deterministic"] is False
    assert row["query_stability_ratio"] == pytest.approx(0.0)
    assert row["metrics"]["ndcg_at_10"] == pytest.approx(0.85)


def _cohort_report(
    path: Path,
    *,
    candidate_metrics: dict[str, float],
    question_count: int,
) -> None:
    ranking = []
    for position, (candidate, ndcg) in enumerate(
        candidate_metrics.items(),
        start=1,
    ):
        ranking.append(
            {
                "position": position,
                "candidate_id": candidate,
                "metrics": {
                    "recall_at_10": ndcg,
                    "mrr_at_10": ndcg,
                    "ndcg_at_10": ndcg,
                },
                "query_stability_ratio": 1.0,
                "representative_p95_ms": float(position),
                "deterministic": True,
            }
        )
    path.write_text(
        json.dumps(
            {
                "status": "pass",
                "contract": {"question_count": question_count},
                "ranking": ranking,
            }
        ),
        encoding="utf-8",
        newline="\n",
    )


def test_multi_cohort_rank_is_controlled_by_evaluation_only_report(
    tmp_path: Path,
) -> None:
    canonical = tmp_path / "canonical.json"
    post_v51 = tmp_path / "post-v51.json"
    parallel = tmp_path / "parallel.json"
    _cohort_report(
        canonical,
        candidate_metrics={"profile": 1.0, "hybrid": 0.8},
        question_count=40,
    )
    _cohort_report(
        post_v51,
        candidate_metrics={"profile": 0.5, "hybrid": 0.9},
        question_count=20,
    )
    _cohort_report(
        parallel,
        candidate_metrics={"profile": 0.4, "hybrid": 0.99},
        question_count=60,
    )

    report = COHORT_AGGREGATE.combine(canonical, post_v51, parallel)

    assert report["ranking"][0]["candidate_id"] == "hybrid"
    assert report["ranking"][1]["candidate_id"] == "profile"
    assert report["cohorts"]["parallel_evaluation_only_60"][
        "question_count"
    ] == 60


def test_general_strategy_definitions_cover_the_historical_table() -> None:
    historical = json.loads(
        GENERAL_FREEZE.HISTORICAL_TABLE.read_text(encoding="utf-8")
    )
    expected = {row["id"] for row in historical["alternatives"]}
    assert len(expected) == 25
    assert set(GENERAL_FREEZE._strategy_artifacts()) == expected


def test_general_strategy_aggregate_requires_three_reports() -> None:
    with pytest.raises(GENERAL_AGGREGATE.AggregateError, match="exactly three"):
        GENERAL_AGGREGATE._row_from_three_reports(
            "legacy-lexical",
            [],
            "legacy_lexical",
        )


def test_general_strategy_aggregate_rejects_question_drift() -> None:
    report = {
        "dataset_id": GENERAL_AGGREGATE.DATASET_ID,
        "query_count": 60,
        "top_k": 10,
        "inputs": {"questions": {"sha256": "0" * 64}},
    }
    with pytest.raises(GENERAL_AGGREGATE.AggregateError, match="question set"):
        GENERAL_AGGREGATE._validate_report_contract(report, "candidate")


def test_general_strategy_aggregate_accepts_ensemble_benchmark_binding() -> None:
    report = {
        "query_count": 60,
        "top_k": 10,
        "benchmark": {
            "benchmark_id": GENERAL_AGGREGATE.DATASET_ID,
            "question_sha256": GENERAL_AGGREGATE.QUERY_SHA256,
        },
    }
    GENERAL_AGGREGATE._validate_report_contract(report, "ensemble")


def test_general_comparison_companion_preserves_all_metrics() -> None:
    ranking = []
    for position in range(1, 26):
        ranking.append(
            {
                "position": position,
                "strategy_id": f"strategy-{position:02d}",
                "label": f"Strategy {position:02d}",
                "metrics": {
                    "recall_at_10": 0.8,
                    "mrr_at_10": 0.9,
                    "ndcg_at_10": 0.85,
                },
                "query_stability_ratio": 1.0,
                "representative_p95_ms": float(position),
            }
        )
    companion = GENERAL_AGGREGATE.comparison_companion({"ranking": ranking})
    assert len(companion["alternatives"]) == 25
    assert list(companion["alternatives"][0]["metrics"]) == [
        "recall_at_10",
        "mrr_at_10",
        "ndcg_at_10",
        "query_stability_ratio",
        "representative_p95_ms",
    ]


def _quality_latency_report() -> dict[str, object]:
    definitions = [
        ("classical-association", "Classical association", 0.9960, 664.65),
        ("rust-mallet-bm25", "RustMallet BM25", 0.9811, 650.81),
        ("tantivy-bm25", "Tantivy BM25", 0.9625, 128.27),
        ("tika-mallet-fusion", "Tika/MALLET fusion", 0.9128, 99.48),
        ("legacy-lexical", "Legacy lexical", 0.6054, 9.96),
    ]
    definitions.extend(
        (f"dominated-{number:02d}", f"Dominated {number:02d}", 0.50, 1000.0)
        for number in range(1, 21)
    )
    ranking = [
        {
            "strategy_id": strategy_id,
            "label": label,
            "metrics": {
                "recall_at_10": 1.0 if ndcg >= 0.90 else 0.80,
                "mrr_at_10": ndcg,
                "ndcg_at_10": ndcg,
            },
            "evidence_validity": 1.0,
            "query_stability_ratio": 1.0,
            "representative_p95_ms": latency,
        }
        for strategy_id, label, ndcg, latency in definitions
    ]
    return {
        "status": "pass",
        "ranking_eligible": True,
        "dataset_id": QUALITY_LATENCY.DATASET_ID,
        "query_count": 60,
        "strategy_count": 25,
        "top_k": 10,
        "ranking": ranking,
    }


def test_quality_latency_analysis_selects_explicit_skill_groups(
    tmp_path: Path,
) -> None:
    source = tmp_path / "ranking.json"
    source.write_text(
        json.dumps(_quality_latency_report()),
        encoding="utf-8",
    )

    report = QUALITY_LATENCY.analyze(source)

    recommendations = {
        row["recommendation_id"]: row for row in report["recommendations"]
    }
    assert recommendations["quality-first"]["strategy_id"] == "classical-association"
    assert recommendations["balanced-default"]["strategy_id"] == "tantivy-bm25"
    assert recommendations["balanced-default"]["skills"][
        "evaluated_builder_lineage"
    ] == "build-semantic-okf-classical"
    assert recommendations["balanced-default"]["skills"][
        "new_build_candidate"
    ] == "build-semantic-okf-tantivy"
    assert "not-evaluated" in recommendations["balanced-default"]["skills"][
        "construction_evidence"
    ]
    assert (
        recommendations["ultra-fast-experimental"]["strategy_id"]
        == "tika-mallet-fusion"
    )
    assert [
        row["strategy_id"] for row in report["pareto_frontier"]
    ] == [
        "classical-association",
        "rust-mallet-bm25",
        "tantivy-bm25",
        "tika-mallet-fusion",
        "legacy-lexical",
    ]


def test_quality_latency_analysis_rejects_source_digest_drift(
    tmp_path: Path,
) -> None:
    source = tmp_path / "ranking.json"
    source.write_text(json.dumps(_quality_latency_report()), encoding="utf-8")

    with pytest.raises(QUALITY_LATENCY.AnalysisError, match="digest differs"):
        QUALITY_LATENCY.analyze(source, "0" * 64)
