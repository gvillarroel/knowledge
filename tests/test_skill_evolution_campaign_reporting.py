"""Cross-generation publication retains provenance, failed runs and the terminal boundary."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest


@pytest.fixture
def reporter(monkeypatch):
    root = Path(__file__).resolve().parents[1] / "evaluations/skill-evolution"
    monkeypatch.syspath_prepend(str(root))
    spec = importlib.util.spec_from_file_location("tested_campaign_reporter", root / "aggregate_campaign.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def generations(reporter):
    routes = {"adaptive": ["adaptive"], "classical": ["association", "bm25", "fusion", "topic"],
              "embeddings": ["hybrid", "lexical", "vector"], "ensemble": ["fast", "quality", "robust"],
              "entity-graph": ["entity", "fusion", "lexical", "traversal"], "graphify": ["search"],
              "legacy": ["lexical"], "turso": ["lexical-sql"]}
    output = []
    for generation, profiles in enumerate(reporter.PROFILES):
        data = {"schema_version": "retrieval-evolution-aggregates/1.0", "study": "e5", "generation": generation,
                "phase": "development", "validation_used": False, "development_profile_digest": "fixture-profile",
                "execution_kind": "fixture-local-runtime", "hardware_sha256": "fixture-host", "scope": "synthetic development only",
                "generation_seal": f"fixture-seal-{generation}", "archive_sha256": f"fixture-archive-{generation}",
                "native_report_sha256": f"fixture-report-{generation}", "candidates": [], "routes": [], "failures": [], "primary_changes": [],
                "model_accounting": {"input_tokens": 0, "output_tokens": 0, "cache_tokens": 0, "model_provider_cost_usd": 0.0}}
        for profile in sorted(profiles):
            score = .9 if profile == "neural-record" else .5
            data["candidates"].append({"candidate": profile, "qualified": True, "expected_trials": 32, "completed_trials": 32,
                                       "errors": 0, "scored_trials": 32, "mean_ndcg_at_10": score, "native_diagnostic_mean_reward": score,
                                       "skill_digest": "fixture-" + profile, "source_skill_digest": "fixture-" + profile,
                                       "job_id": f"fixture-{generation}-{profile}", "job_result_sha256": "fixture-result", "native_lock_sha256": "fixture-lock",
                                       "mean_gain": score - .5, "improved_cells": 32 if score > .5 else 0, "unchanged_cells": 32 if score == .5 else 0, "regressed_cells": 0})
            for dataset in sorted(reporter.DATASETS):
                for family, strategies in routes.items():
                    for route in strategies:
                        data["routes"].append({"candidate": profile, "dataset": dataset, "family": family, "route": route,
                                               "primary": route == reporter.PRIMARY[family], "questions": 40, "ndcg_at_10": score,
                                               "recall_at_10": score, "mrr_at_10": score, "full_qrel_coverage_at_10": score,
                                               "p95_ms": 2.0, "double_build_seconds": 3.0, "knowledge_bytes": 1024,
                                               "agent_execution_seconds": None, "native_trial_seconds": 5.0})
        output.append(data)
    return output


def test_keeps_repeated_baselines_and_earlier_maxima_without_selecting(reporter, generations):
    data = reporter.project(generations)
    assert (data["measured_runs"], data["unique_profiles"], data["completed_native_trials"]) == (10, 9, 320)
    assert len(data["routes"]) == 720
    assert {row["candidate"] for row in data["candidates"] if row["profile"] == "baseline"} == {"g0-baseline", "g1-baseline"}
    assert all({winner["profile"] for winner in row["winners"]} == {"g0-neural-record"} for row in data["best_default_by_dataset"])
    assert data["selection_established"] is data["promotion_established"] is False
    assert "final native generation archive only" in data["finalist_scope"]
    assert "mean_ndcg_at_10" not in data
    assert generations[0]["candidates"][0]["candidate"] == "baseline"


@pytest.mark.parametrize("change", ["private", "profile", "hardware", "incomplete", "duplicate", "scale", "path"])
def test_rejects_incomparable_or_malformed_inputs(reporter, generations, change):
    candidate = generations[1]["candidates"][0]
    route = generations[1]["routes"][0]
    if change == "private":
        generations[1]["validation_used"] = True
    elif change == "profile":
        generations[1]["development_profile_digest"] = "different-profile"
    elif change == "hardware":
        generations[1]["hardware_sha256"] = "different-host"
    elif change == "incomplete":
        candidate["completed_trials"] = 31
    elif change == "duplicate":
        generations[1]["routes"].append(dict(route))
    elif change == "scale":
        route["ndcg_at_10"] = 90
    else:
        route["dataset"] = "../../outside"
    with pytest.raises(ValueError):
        reporter.project(generations)


def test_unqualified_profile_cannot_win_and_unknown_payload_fields_are_omitted(reporter, generations):
    candidate = next(row for row in generations[0]["candidates"] if row["candidate"] == "neural-record")
    candidate.update(qualified=False, mean_ndcg_at_10=None, mean_gain=None, errors=1, scored_trials=31,
                     improved_cells=None, unchanged_cells=None, regressed_cells=None)
    candidate["question"] = "DO NOT EXPORT THIS QUESTION"
    generations[0]["routes"][0]["references"] = ["DO NOT EXPORT THIS REFERENCE"]
    generations[0]["model_accounting"]["question"] = "DO NOT EXPORT THIS ACCOUNTING PAYLOAD"
    generations[0]["failures"].append({"candidate": "neural-record", "dataset": "astro", "family": "legacy",
                                        "status": "non-evaluable", "error_type": "FixtureError"})
    generations[0]["routes"] = [row for row in generations[0]["routes"] if not (row["candidate"] == "neural-record" and row["dataset"] == "astro" and row["family"] == "legacy")]
    data = reporter.project(generations)
    assert data["native_errors"] == 1 and data["failures"][0]["candidate"] == "g0-neural-record"
    assert all(winner["profile"] != "g0-neural-record" for row in data["best_all_routes_by_dataset"] for winner in row["winners"])
    assert "DO NOT EXPORT" not in json.dumps(data)


def test_render_retains_all_views_and_does_not_overwrite(reporter, generations, tmp_path):
    output = tmp_path / "comparison"
    reporter.render(output, reporter.project(generations))
    assert len(list((output / "by-skill").glob("*.md"))) == 8
    assert len(list((output / "by-dataset").glob("*.md"))) == 4
    assert len(list((output / "by-profile").glob("*.md"))) == 10
    assert len((output / "cta.csv").read_text(encoding="utf-8").splitlines()) == 321
    overview = (output / "README.md").read_text(encoding="utf-8")
    assert "not a combined native Pareto archive" in overview
    assert "g0-neural-record" in overview and "g1-baseline" in overview
    assert "unavailable" in (output / "cta.md").read_text(encoding="utf-8")
    with pytest.raises(FileExistsError):
        reporter.render(output, reporter.project(generations))


@pytest.mark.parametrize("state", [
    {"stages": {"evolve": {"status": "completed"}}, "validationRelease": None, "holdoutRelease": None},
    {"stages": {"evolve": {"status": "running"}}, "validationRelease": {"released": True}, "holdoutRelease": None},
])
def test_main_rejects_terminal_or_released_studies_before_reading_sources(reporter, monkeypatch, state):
    monkeypatch.setattr(reporter, "assert_frozen", lambda: state)
    monkeypatch.setattr(reporter, "read", lambda path: pytest.fail("No source read is allowed after this boundary"))
    with pytest.raises(ValueError, match="before private release"):
        reporter.main()


def test_main_requires_registered_sources_before_loading_them(reporter, monkeypatch):
    state = {"stages": {"evolve": {"status": "running"}}, "validationRelease": None,
             "holdoutRelease": None, "evidence": {}}
    monkeypatch.setattr(reporter, "assert_frozen", lambda: state)
    monkeypatch.setattr(reporter, "read", lambda path: pytest.fail("Unregistered sources must not be loaded"))
    with pytest.raises(ValueError, match="must be registered"):
        reporter.main()


def test_main_binds_fixture_sources_and_publishes_without_evaluating(reporter, generations, monkeypatch, tmp_path):
    work = tmp_path / "tmp/e5"
    monkeypatch.setattr(reporter, "REPO", tmp_path)
    monkeypatch.setattr(reporter, "WORK", work)
    state = {"stages": {"evolve": {"status": "running"}}, "validationRelease": None,
             "holdoutRelease": None, "evidence": {}}
    sources = []
    for generation, word in enumerate(("zero", "one")):
        directory = tmp_path / f"evaluations/reports/evolution/e5/generation-{generation:03d}"
        archive = work / f"pareto/development/generation-{generation:03d}/pareto-archive.json"
        native = work / f"native-reports/development-generation-{generation:03d}/final-report.json"
        for path in (archive, native):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps({"synthetic_test_fixture": True, "generation": generation}), encoding="utf-8")
        generations[generation].update(archive_sha256=reporter.sha(archive), native_report_sha256=reporter.sha(native))
        directory.mkdir(parents=True)
        source = directory / "aggregates.json"
        source.write_text(json.dumps(generations[generation]), encoding="utf-8")
        sources.append((source, reporter.sha(source)))
        state["evidence"][f"generation-{word}-public-report"] = {"source": str(directory), "kind": "final-report",
                                                               "stageId": "evolve", "role": "report", "visibility": "public"}
    monkeypatch.setattr(reporter, "assert_frozen", lambda: state)
    reporter.main()
    output = tmp_path / "evaluations/reports/evolution/e5/comparison"
    report = json.loads((output / "aggregates.json").read_text(encoding="utf-8"))
    assert report["completed_native_trials"] == 320 and report["selection_established"] is False
    assert report["reporter_sha256"] == reporter.sha(Path(reporter.__file__))
    for generation, (source, digest) in enumerate(sources):
        assert reporter.sha(source) == digest == report["sources"][generation]["aggregate_sha256"]
    assert "profile_qualified" in (output / "cta.csv").read_text(encoding="utf-8").splitlines()[0]
