"""Tests for separate Semantic OKF construction and consultation token use."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
ROOT = REPO / "evaluations/semantic-okf-datasets"
GRADER = REPO / "evaluations/semantic-okf-harbor/grader"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(GRADER))

import recalculate_graphrag_evaluation_table as RECALCULATE  # noqa: E402
import summarize_consult_campaign as CAMPAIGN  # noqa: E402
import summarize_token_usage as TOKEN_USAGE  # noqa: E402


def test_consult_usage_does_not_invent_zero_or_double_count_cache() -> None:
    rows = [
        {
            "tokens": {"input": 100, "cache": 80, "output": 20},
        },
        {
            "tokens": {"input": 50, "cache": 40, "output": None},
        },
    ]

    usage = CAMPAIGN.token_usage(rows)

    assert usage == {
        "observed_trials": 1,
        "cache_observed_trials": 1,
        "input_tokens_including_cache": {
            "total": 100,
            "mean": 100.0,
        },
        "cache_tokens_reported_separately": {
            "total": 80,
            "mean": 80.0,
        },
        "output_tokens": {"total": 20, "mean": 20.0},
        "total_tokens": {"total": 120, "mean": 120.0},
    }


def test_current_metrics_usage_stays_split_by_model() -> None:
    rows = [
        {
            "model": "provider/model-a",
            "usage": {
                "input_tokens_including_cache": 100,
                "cache_tokens_reported_separately": 80,
                "output_tokens": 20,
            },
        },
        {
            "model": "provider/model-a",
            "usage": {
                "input_tokens_including_cache": 200,
                "cache_tokens_reported_separately": 120,
                "output_tokens": 40,
            },
        },
        {
            "model": "provider/model-b",
            "usage": {
                "input_tokens_including_cache": 50,
                "cache_tokens_reported_separately": 10,
                "output_tokens": 5,
            },
        },
    ]

    by_model = RECALCULATE._usage_by_model(rows)

    assert by_model == [
        {
            "model": "provider/model-a",
            "observed_answer_count": 2,
            "cache_observed_answer_count": 2,
            "mean_input_tokens_including_cache": 150.0,
            "mean_cache_tokens_reported_separately": 100.0,
            "mean_output_tokens": 30.0,
            "mean_total_tokens": 180.0,
        },
        {
            "model": "provider/model-b",
            "observed_answer_count": 1,
            "cache_observed_answer_count": 1,
            "mean_input_tokens_including_cache": 50.0,
            "mean_cache_tokens_reported_separately": 10.0,
            "mean_output_tokens": 5.0,
            "mean_total_tokens": 55.0,
        },
    ]


def test_strategy_rows_publish_model_split_token_usage() -> None:
    strategy_rows = RECALCULATE._strategy_rows(
        [
            {
                "native_task_tests": (
                    "generated/tasks/graphrag-papers-40/"
                    "consult-only/classical/dev/q001/tests"
                ),
                "trace": {"outcome": "answer-emitted"},
                "reviewable_response": True,
                "semantic_verdict": "partial",
                "question_id": "q001",
                "model": "provider/model-a",
                "usage": {
                    "input_tokens_including_cache": 100,
                    "cache_tokens_reported_separately": 80,
                    "output_tokens": 20,
                    "total_tokens": 120,
                },
                "current_metrics": {
                    "response_contract": 1.0,
                    "mechanical_qualification_gate": 1.0,
                    "mechanical_utility": 0.75,
                    "reward": 0.5,
                },
            }
        ]
    )

    assert strategy_rows[0]["answer_token_usage_by_model"] == [
        {
            "model": "provider/model-a",
            "observed_answer_count": 1,
            "cache_observed_answer_count": 1,
            "mean_input_tokens_including_cache": 100.0,
            "mean_cache_tokens_reported_separately": 80.0,
            "mean_output_tokens": 20.0,
            "mean_total_tokens": 120.0,
        }
    ]


def test_compact_builder_evidence_survives_ignored_raw_results() -> None:
    evidence = json.loads(
        TOKEN_USAGE.DEFAULT_EVIDENCE.read_text(encoding="utf-8")
    )
    without_raw_results = copy.deepcopy(evidence)
    for method in without_raw_results["build_methodologies"]:
        for index, trial in enumerate(method["trials"]):
            trial["result_path"] = (
                "evaluations/semantic-okf-datasets/results/"
                f"intentionally-absent-{method['methodology']}-{index}.json"
            )

    build = TOKEN_USAGE.build_folder_usage(without_raw_results)

    assert build["all_measured_rollup"][
        "generated_folder_count"
    ] == 16
    assert build["all_measured_rollup"]["mean_total_tokens"] == pytest.approx(
        102124.0625
    )
    assert build["strictly_qualified_rollup"][
        "mean_total_tokens"
    ] == pytest.approx(111307.66666666667)


def test_token_report_recalculates_all_registered_strategies() -> None:
    report = TOKEN_USAGE.generate_report()

    assert report["new_model_calls"] == 16
    build = report["registered_build_folder_usage"]
    assert build["family_count"] == 8
    assert build["overall"]["builder_call_count"] == 16
    assert build["overall"]["generated_folder_count"] == 16
    assert {
        row["methodology"] for row in build["methodologies"]
    } == TOKEN_USAGE.REGISTERED_FAMILIES
    assert all(
        row["qualified_builder_call_count"] == 2
        and row["replicates_byte_identical"] is True
        for row in build["methodologies"]
    )
    assert build["lowest_token_methodology"]["mean_total_tokens"] == min(
        row["mean_total_tokens"] for row in build["methodologies"]
    )
    assert build["highest_token_methodology"]["mean_total_tokens"] == max(
        row["mean_total_tokens"] for row in build["methodologies"]
    )
    consultation = report["registered_consultation_query_usage"]
    assert consultation["overall"]["submitted_query_count"] == 48
    assert consultation["overall"]["runtime_error_count"] == 19
    assert consultation["overall"]["mean_total_tokens"] == pytest.approx(
        1545100.5208333333
    )
    assert consultation["lowest_observed_submitted_cost"][
        "methodology"
    ] == "graphify"
    assert consultation["highest_observed_submitted_cost"][
        "methodology"
    ] == "entity-graph"
    assert consultation["lowest_zero_error_methodology"][
        "methodology"
    ] == "legacy"
    assert consultation["highest_zero_error_methodology"][
        "methodology"
    ] == "turso"
    assert report["direct_retrieval_usage"]["strategy_count"] == 25
    assert report["direct_retrieval_usage"][
        "llm_tokens_per_retrieval"
    ] == 0
    diagnostic = report["graphrag_complete_response_diagnostic"]
    assert diagnostic["complete_usage_count"] == 209
    assert {
        row["model"] for row in diagnostic["model_rollups"]
    } == {
        "github-copilot/gpt-5.4",
        "openai-codex/gpt-5.3-codex-spark",
        "openrouter/google/gemini-2.5-flash",
        "openrouter/openai/gpt-5.4-mini",
    }
    rendered = TOKEN_USAGE.markdown(report)
    assert "all eight registered build/consult strategy pairs" in rendered
    assert "Graphify" in rendered
    assert "Entity Graph" in rendered
    assert "0 LLM tokens per retrieval invocation" in rendered


def test_checked_token_reports_match_deterministic_regeneration() -> None:
    assert TOKEN_USAGE.main(["--check"]) == 0


def test_compact_usage_rejects_cache_double_count_contract() -> None:
    with pytest.raises(
        TOKEN_USAGE.TokenUsageError,
        match="violates Harbor token semantics",
    ):
        TOKEN_USAGE.declared_usage(
            {
                "usage": {
                    "input_tokens_including_cache": 100,
                    "cache_tokens_reported_separately": 80,
                    "output_tokens": 20,
                    "total_tokens": 200,
                }
            }
        )
