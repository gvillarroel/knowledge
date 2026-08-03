from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from types import ModuleType
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    REPO_ROOT
    / "evaluations"
    / "semantic-okf-classical-token-efficiency-study-v1"
    / "scripts"
    / "evaluate_acceptance.py"
)
METRICS = [
    "reward",
    "response_contract",
    "non_null_answer",
    "reference_validity",
    "all_evidence_valid",
    "evidence_contract_gate",
    "evidence_precision",
    "evidence_recall",
    "minimum_document_coverage",
    "required_document_coverage",
    "mrr",
    "ndcg",
    "mechanical_utility",
]


def load_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("classical_token_acceptance", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_job(
    root: Path,
    cases: dict[str, tuple[int, int, int, dict[str, float], bool]],
) -> None:
    write_json(root / "result.json", {"n_total_trials": len(cases)})
    for case_id, (input_tokens, cache_tokens, output_tokens, rewards, errored) in cases.items():
        write_json(
            root / f"{case_id}__trial" / "result.json",
            {
                "task_id": {"path": f"/dataset/{case_id}"},
                "trial_name": f"{case_id}__trial",
                "agent_result": {
                    "n_input_tokens": input_tokens,
                    "n_cache_tokens": cache_tokens,
                    "n_output_tokens": output_tokens,
                },
                "verifier_result": {"rewards": rewards},
                "exception_info": {"type": "failure"} if errored else None,
            },
        )


def write_policy(path: Path) -> None:
    write_json(
        path,
        {
            "policyId": "test-policy",
            "nativeUsage": {
                "developmentMeanMaximumBaselineRatio": 0.8,
                "holdoutMeanMaximumBaselineRatio": 0.8,
                "minimumCasesWithStrictReduction": 2,
            },
            "quality": {
                "candidateErrorsMaximum": 0,
                "caseMetrics": METRICS,
                "comparisonTolerance": 1e-12,
            },
        },
    )


def uniform_rewards(value: float = 1.0) -> dict[str, float]:
    return {metric: value for metric in METRICS}


def test_acceptance_uses_input_plus_output_without_double_counting_cache(tmp_path: Path) -> None:
    module = load_module()
    baseline = tmp_path / "baseline"
    candidate = tmp_path / "candidate"
    policy = tmp_path / "policy.json"
    write_policy(policy)
    write_job(
        baseline,
        {
            "q001": (900, 700, 100, uniform_rewards(), False),
            "q002": (1_800, 1_400, 200, uniform_rewards(), False),
        },
    )
    write_job(
        candidate,
        {
            "q001": (450, 350, 50, uniform_rewards(), False),
            "q002": (900, 700, 100, uniform_rewards(), False),
        },
    )

    report = module.compare(baseline, candidate, policy, "development")

    assert report["accepted"] is True
    assert report["summary"]["baselineMeanTotalTokens"] == 1_500
    assert report["summary"]["candidateMeanTotalTokens"] == 750
    assert report["summary"]["baselineMeanCacheTokens"] == 1_050
    assert report["summary"]["meanTokenChangePercent"] == -50
    assert all(gate["passed"] for gate in report["gates"].values())


def test_any_case_metric_regression_rejects_an_otherwise_cheaper_candidate(
    tmp_path: Path,
) -> None:
    module = load_module()
    baseline = tmp_path / "baseline"
    candidate = tmp_path / "candidate"
    policy = tmp_path / "policy.json"
    write_policy(policy)
    before = uniform_rewards()
    after = uniform_rewards()
    after["evidence_precision"] = 0.75
    write_job(
        baseline,
        {
            "q001": (900, 700, 100, before, False),
            "q002": (900, 700, 100, before, False),
        },
    )
    write_job(
        candidate,
        {
            "q001": (400, 300, 50, after, False),
            "q002": (400, 300, 50, before, False),
        },
    )

    report = module.compare(baseline, candidate, policy, "development")

    assert report["accepted"] is False
    assert report["gates"]["meanTokenReduction"]["passed"] is True
    assert report["gates"]["caseQualityNonRegression"] == {
        "passed": False,
        "regressionCount": 1,
    }
    assert report["qualityRegressions"] == [
        {
            "caseId": "q001",
            "metric": "evidence_precision",
            "baseline": 1.0,
            "candidate": 0.75,
            "delta": -0.25,
        }
    ]
