"""Aggregate exports retain failed denominators and omit private case payloads."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest


@pytest.fixture
def reporter(monkeypatch):
    root = Path(__file__).resolve().parents[1] / "evaluations/skill-evolution"
    monkeypatch.syspath_prepend(str(root))
    spec = importlib.util.spec_from_file_location("tested_evolution_reporter", root / "aggregate_development.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def put(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def evidence(tmp_path):
    directory = tmp_path / "native-job"
    put(directory / "result.json", {"stats": {"n_input_tokens": 0, "n_output_tokens": 0, "n_cache_tokens": 0, "cost_usd": 0}})
    put(directory / "lock.json", {"native": "test fixture"})
    put(directory / "one/result.json", {"task_name": "opaque-task", "exception_info": {"exception_type": "RuntimeError"}})
    candidate = {"candidateId": "candidate", "qualification": {"passed": False}, "summary": {"expectedTrials": 1, "completedTrials": 1, "errorCount": 1, "evaluableTrials": 0, "meanReward": None},
                 "skillDigest": "fixture-digest", "sourceSkillDigest": "fixture-digest", "jobId": "fixture-job", "jobDirectory": str(directory)}
    return ({"holdoutDataUsed": False, "candidateResults": [candidate]},
            {"source": "harbor", "jobs": [{"jobDirectory": str(directory), "complete": True}]},
            {"opaque-task": {"source_cohort": "synthetic", "family": "legacy", "question": "DO NOT EXPORT THIS PRIVATE QUESTION"}})


def test_failures_remain_explicit_and_private_content_is_not_exported(reporter, tmp_path):
    data = reporter.collect(*evidence(tmp_path))
    assert data["candidates"][0]["completed_trials"] == 1
    assert data["candidates"][0]["errors"] == 1
    assert data["routes"] == []
    assert data["failures"] == [{"candidate": "candidate", "dataset": "synthetic", "family": "legacy", "status": "non-evaluable", "error_type": "RuntimeError"}]
    assert "PRIVATE QUESTION" not in json.dumps(data)
    assert "opaque-task" not in json.dumps(data)


def test_reporter_rejects_incomplete_native_evidence(reporter, tmp_path):
    archive, report, metadata = evidence(tmp_path)
    report["jobs"][0]["complete"] = False
    with pytest.raises(ValueError, match="complete native"):
        reporter.collect(archive, report, metadata)


def test_unqualified_native_mean_is_preserved_only_as_a_diagnostic(reporter, tmp_path):
    archive, report, metadata = evidence(tmp_path)
    archive["candidateResults"][0]["summary"]["meanReward"] = .9
    data = reporter.collect(archive, report, metadata)
    assert data["candidates"][0]["mean_ndcg_at_10"] is None
    assert data["candidates"][0]["native_diagnostic_mean_reward"] == .9
    assert data["candidates"][0]["scored_trials"] == 0


def test_native_timing_preserves_missing_phases_and_crosses_midnight(reporter):
    assert reporter.elapsed_seconds(None) is None
    assert reporter.elapsed_seconds({"started_at": "2026-09-06T23:59:59Z", "finished_at": None}) is None
    assert reporter.elapsed_seconds({"started_at": "2026-09-06T23:59:59Z", "finished_at": "2026-09-07T00:00:02.5Z"}) == 3.5
    with pytest.raises(ValueError, match="reversed"):
        reporter.elapsed_seconds({"started_at": "2026-09-06T00:00:02Z", "finished_at": "2026-09-06T00:00:01Z"})


def test_dataset_winners_exclude_failed_profiles_and_secondary_routes(reporter):
    data = {"candidates": [{"candidate": "stable", "qualified": True}, {"candidate": "failed-elsewhere", "qualified": False}],
            "routes": [
                {"candidate": "stable", "dataset": "one", "family": "classical", "primary": True, "ndcg_at_10": .7},
                {"candidate": "stable", "dataset": "one", "family": "graphify", "primary": True, "ndcg_at_10": .7},
                {"candidate": "stable", "dataset": "one", "family": "embeddings", "primary": False, "ndcg_at_10": 1.0},
                {"candidate": "failed-elsewhere", "dataset": "one", "family": "classical", "primary": True, "ndcg_at_10": .99},
                {"candidate": "failed-elsewhere", "dataset": "two", "family": "classical", "primary": True, "ndcg_at_10": .99},
            ]}
    assert reporter.best_by_dataset(data) == [
        {"dataset": "one", "winners": [{"family": "classical", "profile": "stable"}, {"family": "graphify", "profile": "stable"}], "ndcg_at_10": .7},
        {"dataset": "two", "winners": [], "ndcg_at_10": None},
    ]


def test_navigation_preserves_a_profile_with_only_errors(reporter, tmp_path):
    data = reporter.collect(*evidence(tmp_path))
    assert reporter.best_by_dataset(data) == [{"dataset": "synthetic", "winners": [], "ndcg_at_10": None}]
    output = tmp_path / "published"
    output.mkdir()
    links = reporter.write_navigation_views(output, data)
    assert links == {"by-skill": ["legacy"], "by-profile": ["candidate"], "by-dataset": ["synthetic"]}
    for directory, keys in links.items():
        content = (output / directory / (keys[0] + ".md")).read_text(encoding="utf-8")
        assert "non-evaluable" in content and "RuntimeError" in content
        assert "PRIVATE QUESTION" not in content and "opaque-task" not in content


def test_primary_deltas_preserve_regressions_and_exclude_secondary_routes(reporter):
    data = {"candidates": [{"candidate": "baseline", "qualified": True}, {"candidate": "profile", "qualified": True}],
            "failures": [], "routes": []}
    for dataset, before, after in (("improved", .4, .6), ("tied", 0, 0), ("regressed", .8, .5)):
        for candidate, value in (("baseline", before), ("profile", after)):
            data["routes"].append({"candidate": candidate, "dataset": dataset, "family": "classical", "primary": True, "ndcg_at_10": value})
    data["routes"].append({"candidate": "profile", "dataset": "regressed", "family": "classical", "primary": False, "ndcg_at_10": 1})
    changes = reporter.primary_changes(data)
    assert reporter.change_counts("profile", changes) == {"improved_cells": 1, "unchanged_cells": 1, "regressed_cells": 1}
    assert reporter.change_counts("baseline", changes) == {"improved_cells": 0, "unchanged_cells": 3, "regressed_cells": 0}
    regression = next(row for row in changes if row["candidate"] == "profile" and row["dataset"] == "regressed")
    assert regression["delta_ndcg_at_10"] == pytest.approx(-.3)


def test_failed_profiles_keep_all_cells_and_only_diagnostic_differences(reporter):
    data = {"candidates": [{"candidate": "baseline", "qualified": True}, {"candidate": "profile", "qualified": False}],
            "failures": [{"candidate": "profile", "dataset": "failed", "family": "classical"}],
            "routes": [
                {"candidate": "baseline", "dataset": "scored", "family": "classical", "primary": True, "ndcg_at_10": .4},
                {"candidate": "baseline", "dataset": "failed", "family": "classical", "primary": True, "ndcg_at_10": .7},
                {"candidate": "profile", "dataset": "scored", "family": "classical", "primary": True, "ndcg_at_10": .9},
            ]}
    changes = reporter.primary_changes(data)
    candidate = [row for row in changes if row["candidate"] == "profile"]
    assert len(candidate) == 2
    assert all(row["delta_ndcg_at_10"] is None for row in candidate)
    assert next(row for row in candidate if row["dataset"] == "scored")["diagnostic_measured_delta"] == .5
    assert next(row for row in candidate if row["dataset"] == "failed")["candidate_ndcg_at_10"] is None
    assert reporter.change_counts("profile", changes) == {"improved_cells": None, "unchanged_cells": None, "regressed_cells": None}


def test_all_route_diagnostics_do_not_replace_predeclared_default_winners(reporter):
    data = {"candidates": [{"candidate": "baseline", "qualified": True}, {"candidate": "invalid", "qualified": False}],
            "routes": [
                {"candidate": "baseline", "dataset": "one", "family": "legacy", "route": "lexical", "primary": True, "ndcg_at_10": .57},
                {"candidate": "baseline", "dataset": "one", "family": "entity-graph", "route": "fusion", "primary": True, "ndcg_at_10": .47},
                {"candidate": "baseline", "dataset": "one", "family": "entity-graph", "route": "lexical", "primary": False, "ndcg_at_10": .59},
                {"candidate": "invalid", "dataset": "one", "family": "classical", "route": "bm25", "primary": False, "ndcg_at_10": 1},
            ]}
    assert reporter.best_by_dataset(data)[0]["winners"] == [{"family": "legacy", "profile": "baseline"}]
    assert reporter.best_by_dataset(data, primary_only=False) == [{"dataset": "one", "winners": [{"family": "entity-graph", "profile": "baseline", "route": "lexical"}], "ndcg_at_10": .59}]
