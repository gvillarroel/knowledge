from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    REPO_ROOT
    / "evaluations"
    / "semantic-okf-classical-token-efficiency-study-v26"
    / "private"
    / "validation"
    / "evaluate_acceptance.py"
)


def load_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("classical_v26_acceptance", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def trial_result(
    task: str,
    *,
    input_tokens: int = 900,
    cache_tokens: int = 400,
    output_tokens: int = 100,
    errored: bool = False,
    retain_agent_result: bool = False,
) -> dict[str, Any]:
    value: dict[str, Any] = {
        "task_id": {"id": task},
        "task_name": f"task-{task}",
        "task_checksum": f"checksum-{task}",
        "attempt": 0,
        "agent_info": {
            "name": "harbor-agent",
            "version": "1",
            "model_info": {"provider": "synthetic", "name": "model"},
        },
        "config": {
            "agent": {
                "name": "harbor-agent",
                "model_name": "model",
                "kwargs": {"version": "1", "thinking": "high"},
            }
        },
        "exception_info": (
            {"type": "SyntheticFailure", "message": "must remain redacted"}
            if errored
            else None
        ),
    }
    if not errored or retain_agent_result:
        value["agent_result"] = {
            "n_input_tokens": input_tokens,
            "n_cache_tokens": cache_tokens,
            "n_output_tokens": output_tokens,
        }
    if not errored:
        value["verifier_result"] = {"rewards": {"reward": 1.0, "contract": 1.0}}
    return value


def write_job(root: Path, trials: dict[str, dict[str, Any]]) -> None:
    errored = sum(value.get("exception_info") is not None for value in trials.values())
    write_json(
        root / "result.json",
        {
            "n_total_trials": len(trials),
            "finished_at": "2026-08-02T00:00:00Z",
            "stats": {
                "n_completed_trials": len(trials),
                "n_errored_trials": errored,
                "n_running_trials": 0,
                "n_pending_trials": 0,
                "n_cancelled_trials": 0,
                "n_retries": 0,
            },
        },
    )
    for task, value in trials.items():
        write_json(root / f"trial-{task}" / "result.json", value)


def test_candidate_error_is_reported_and_excluded_from_token_aggregates(
    tmp_path: Path,
) -> None:
    module = load_module()
    baseline = tmp_path / "baseline"
    candidate = tmp_path / "candidate"
    write_job(
        baseline,
        {
            "q001": trial_result("q001", input_tokens=900, output_tokens=100),
            "q002": trial_result("q002", input_tokens=1_800, output_tokens=200),
        },
    )
    write_job(
        candidate,
        {
            "q001": trial_result("q001", input_tokens=90, cache_tokens=40, output_tokens=10),
            "q002": trial_result("q002", errored=True),
        },
    )

    report = module.compare_jobs(baseline, candidate, "development")

    assert report["accepted"] is False
    assert report["summary"]["candidateExpectedTrialCount"] == 2
    assert report["summary"]["candidateEvaluableTrialCount"] == 1
    assert report["summary"]["candidateIneligibleTrialCount"] == 1
    assert report["summary"]["candidateTrialCoverageRatio"] == 0.5
    assert report["summary"]["tokenAggregatePairedCaseCount"] == 1
    assert report["summary"]["baselineMeanTotalTokens"] == 1_000
    assert report["summary"]["candidateMeanTotalTokens"] == 100
    assert report["summary"]["meanTokenRatio"] == 0.1

    failed_case = report["cases"][1]
    assert failed_case["candidate"] == {
        "inputTokens": None,
        "cacheTokens": None,
        "outputTokens": None,
        "totalTokens": None,
    }
    assert failed_case["candidateEligibility"] == {
        "evaluable": False,
        "reasons": [
            "harbor-trial-exception",
            "missing-agent-result",
            "missing-verifier-result",
        ],
        "errorDetails": {
            "trialExceptionPresent": True,
            "exceptionInfoShape": "object",
            "agentResultPresent": False,
            "verifierResultPresent": False,
        },
    }
    assert report["qualityIssues"][-1]["kind"] == "candidate-trial-ineligible"
    assert "must remain redacted" not in json.dumps(report)

    assert report["gates"]["baselineJobCompleteAndErrorFree"]["passed"] is True
    for name in (
        "candidateJobCompleteAndErrorFree",
        "candidateTrialCoverageComplete",
        "pairedTaskIdsAndChecksums",
        "sameAgentModelVersionAndAttempt",
        "zeroRetriesFailClosed",
        "caseNumericVerifierNonRegression",
        "meanTokenRatioStrictlyBelowPoint70",
        "medianTokenNonIncrease",
        "independentSemanticPairwiseNonRegression",
    ):
        assert report["gates"][name]["passed"] is False, name

    markdown = module.render_markdown(report, "Synthetic candidate error")
    assert "Candidate token coverage: 1/2 evaluable trials (50.0%)" in markdown
    assert "| case-002 | 2,000 | n/a | n/a | 1 |" in markdown
    assert "harbor-trial-exception, missing-agent-result, missing-verifier-result" in markdown


def test_all_candidate_errors_produce_report_with_null_token_aggregates(
    tmp_path: Path,
) -> None:
    module = load_module()
    baseline = tmp_path / "baseline"
    candidate = tmp_path / "candidate"
    write_job(baseline, {"q001": trial_result("q001")})
    write_job(candidate, {"q001": trial_result("q001", errored=True)})

    first = module.compare_jobs(baseline, candidate, "development")
    second = module.compare_jobs(baseline, candidate, "development")

    assert first == second
    assert first["summary"]["tokenAggregatePairedCaseCount"] == 0
    for key in (
        "baselineMeanInputTokens",
        "candidateMeanInputTokens",
        "baselineMeanTotalTokens",
        "candidateMeanTotalTokens",
        "meanTokenRatio",
        "baselineMedianTotalTokens",
        "candidateMedianTotalTokens",
    ):
        assert first["summary"][key] is None
    assert first["gates"]["meanTokenRatioStrictlyBelowPoint70"]["passed"] is False
    assert first["gates"]["medianTokenNonIncrease"]["passed"] is False
    assert "n/a" in module.render_markdown(first, "All errors")


def test_baseline_missing_agent_result_remains_a_hard_error(tmp_path: Path) -> None:
    module = load_module()
    baseline = tmp_path / "baseline"
    candidate = tmp_path / "candidate"
    write_job(baseline, {"q001": trial_result("q001", errored=True)})
    write_job(candidate, {"q001": trial_result("q001")})

    with pytest.raises(ValueError, match="lacks agent_result"):
        module.compare_jobs(baseline, candidate, "development")


def test_complete_candidate_preserves_existing_token_and_quality_gates(tmp_path: Path) -> None:
    module = load_module()
    baseline = tmp_path / "baseline"
    candidate = tmp_path / "candidate"
    write_job(baseline, {"q001": trial_result("q001")})
    write_job(
        candidate,
        {"q001": trial_result("q001", input_tokens=400, cache_tokens=200, output_tokens=100)},
    )

    report = module.compare_jobs(baseline, candidate, "development")

    assert report["summary"]["candidateCoverageComplete"] is True
    assert report["summary"]["candidateTrialCoverageRatio"] == 1.0
    for name in (
        "baselineJobCompleteAndErrorFree",
        "candidateJobCompleteAndErrorFree",
        "candidateTrialCoverageComplete",
        "pairedTaskIdsAndChecksums",
        "sameAgentModelVersionAndAttempt",
        "zeroRetriesFailClosed",
        "caseNumericVerifierNonRegression",
        "meanTokenRatioStrictlyBelowPoint70",
        "medianTokenNonIncrease",
    ):
        assert report["gates"][name]["passed"] is True, name
    assert report["gates"]["independentSemanticPairwiseNonRegression"]["passed"] is False
    assert report["accepted"] is False
