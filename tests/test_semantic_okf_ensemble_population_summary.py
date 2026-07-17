from __future__ import annotations

import copy
import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
EVALUATION_ROOT = REPO_ROOT / "evaluations/semantic-okf-ensemble"
SCRIPTS = EVALUATION_ROOT / "scripts"


def _load_module() -> ModuleType:
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    spec = importlib.util.spec_from_file_location(
        "semantic_okf_ensemble_population_summary",
        SCRIPTS / "summarize_population_search.py",
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def summary() -> ModuleType:
    return _load_module()


def _json(name: str) -> dict:
    return json.loads((EVALUATION_ROOT / name).read_text(encoding="utf-8"))


def test_checked_population_artifacts_validate_and_render(summary: ModuleType) -> None:
    config = summary.validate_config(_json("population-search.json"))
    generation = _json("generation-000.json")
    assert summary.validate_generation(generation, config) == [
        f"candidate-{index:02d}" for index in range(10)
    ]
    report = summary.validate_report(
        _json("population-search-results.json"),
        config,
        generation,
    )
    assert report["winner"]["fitness"] == pytest.approx(91.88915060557923)
    assert report["execution"] == {
        "completed_generations": 4,
        "candidates_per_generation": 10,
        "candidate_evaluations": 40,
        "repetitions_per_candidate": 3,
        "replay_requests": 120,
        "questions_per_repetition": 40,
        "question_rankings": 4800,
        "effective_parallelism": 1,
        "pass_outcomes": 37,
        "fail_outcomes": 3,
        "all_outcomes_binary": True,
    }
    assert (EVALUATION_ROOT / "population-search-results.md").read_text(
        encoding="utf-8"
    ) == summary.render_markdown(report)


def test_candidate_result_recomputes_fitness_and_enforces_binary_gate(
    summary: ModuleType,
) -> None:
    config = summary.validate_config(_json("population-search.json"))
    winner = _json("population-search-results.json")["winner"]
    result = {
        "schema_version": "semantic-okf-ensemble-population-candidate/1.0",
        "status": "pass",
        "candidate_id": "candidate-02",
        "fitness": winner["fitness"],
        "policy": winner["policy"],
        "tie_break": winner["tie_break"],
        "requests": 3,
        "query_count_per_request": 40,
        "effective_parallelism": 1,
        "ranking_sha256": [winner["ranking_sha256"]] * 3,
        "metrics": winner["metrics"],
        "gates": winner["gates"],
    }
    assert summary.validate_candidate_result(result, "candidate-02", config) == result

    invalid = copy.deepcopy(result)
    invalid["gates"]["metric_floors"]["hard_ndcg_at_10"] = False
    with pytest.raises(summary.EvaluationError, match="status or recomputed fitness"):
        summary.validate_candidate_result(invalid, "candidate-02", config)


def test_compact_report_rejects_machine_path_and_unknown_key(summary: ModuleType) -> None:
    config = summary.validate_config(_json("population-search.json"))
    generation = _json("generation-000.json")
    report = _json("population-search-results.json")

    machine_specific = copy.deepcopy(report)
    machine_specific["selection_scope"]["method"] = r"C:\private\raw-result.json"
    with pytest.raises(summary.EvaluationError, match="absolute machine path"):
        summary.validate_report(machine_specific, config, generation)

    unknown = copy.deepcopy(report)
    unknown["recordedAt"] = "not allowed"
    with pytest.raises(summary.EvaluationError, match="closed schema"):
        summary.validate_report(unknown, config, generation)
