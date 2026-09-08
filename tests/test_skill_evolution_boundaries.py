"""The owning organizer's one-way gate must constrain every local dispatch."""
from __future__ import annotations

import copy
import importlib.util
import sys
from pathlib import Path

import pytest


HERE = Path(__file__).resolve().parents[1] / "evaluations/skill-evolution"


@pytest.fixture
def runner(monkeypatch):
    monkeypatch.syspath_prepend(str(HERE))
    for name in ("prepare_experiment", "prepare_study"):
        monkeypatch.delitem(sys.modules, name, raising=False)
    spec = importlib.util.spec_from_file_location("tested_search_boundaries", HERE / "run_search.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def state():
    return {"designSeal": {"sha256": "sealed"}, "validationRelease": None, "holdoutRelease": None,
            "stages": {"realize": {"status": "completed"}, "evolve": {"status": "running"}, "validate": {"status": "planned"}}}


def settings(runner):
    return {"search": {"generation": 0, "selectedCandidate": "selected"},
            "harbor": {"developmentJob": runner.wsl_path(runner.PROTOCOL / "development.yaml"),
                       "holdoutJob": runner.wsl_path(runner.PROTOCOL / "validation.yaml")},
            "candidates": [{"id": "selected", "skill": "/mnt/c/selected"}]}


@pytest.mark.parametrize("mode", ["prepare", "dry-run", "doctor", "development", "analyze"])
def test_all_evolution_entry_points_reject_after_release(runner, state, mode):
    state["validationRelease"] = {"source": "C:/selected"}
    with pytest.raises(ValueError, match="forbidden"):
        runner.authorize_phase(state, settings(runner), mode)


def test_validation_requires_exact_released_candidate_and_unused_gate(runner, state):
    config = settings(runner)
    with pytest.raises(ValueError, match="release"):
        runner.authorize_phase(state, config, "validation")
    state["validationRelease"] = {"source": "C:/selected"}
    state["stages"]["evolve"]["status"] = "completed"
    runner.authorize_phase(state, config, "validation")
    altered = copy.deepcopy(config)
    altered["candidates"][0]["skill"] = "/mnt/c/other"
    with pytest.raises(ValueError, match="digest-bound"):
        runner.authorize_phase(state, altered, "validation")
    for status in ("running", "completed", "stopped", "blocked"):
        state["stages"]["validate"]["status"] = status
        with pytest.raises(ValueError, match="single terminal dispatch"):
            runner.authorize_phase(state, config, "validation")


def test_later_generation_cannot_skip_evolution_transition(runner, state):
    config = settings(runner)
    config["search"]["generation"] = 1
    state["stages"]["evolve"]["status"] = "planned"
    with pytest.raises(ValueError, match="active evolution"):
        runner.authorize_phase(state, config, "development")
    state["stages"]["evolve"]["status"] = "running"
    runner.authorize_phase(state, config, "development")
    state["designSeal"] = None
    with pytest.raises(ValueError, match="sealed study"):
        runner.authorize_phase(state, config, "development")


def test_job_template_substitution_and_budget_expansion_rejected(runner, state):
    config = settings(runner)
    config["harbor"]["developmentJob"] = "/tmp/other.yaml"
    with pytest.raises(ValueError, match="frozen native job"):
        runner.authorize_phase(state, config, "development")
    config = settings(runner)
    config["search"]["generation"] = 2
    with pytest.raises(ValueError, match="budget"):
        runner.authorize_phase(state, config, "development")
