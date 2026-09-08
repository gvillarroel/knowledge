"""Keep catalog projections bound to selected, complete public retrieval evidence."""
from __future__ import annotations

import copy
import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "evaluations"))
try:
    SPEC = importlib.util.spec_from_file_location("enterprise_catalog_views", ROOT / "evaluations/build_enterprise_evolution_views.py")
    VIEWS = importlib.util.module_from_spec(SPEC)
    SPEC.loader.exec_module(VIEWS)
finally:
    sys.path.pop(0)


@pytest.fixture
def published():
    value = {"schema_version": "enterprise-sweep-report/1.0", "source": "harbor",
             "answer_quality_evaluated": False, "families": [], "attempts": [], "routes": [],
             "question": "PRIVATE QUESTION", "diagnostics": "PRIVATE TRACE"}
    for family in sorted(VIEWS.FAMILIES):
        value["families"].append({"family": family, "winner": "candidate-002", "winner_ndcg_at_10": .6,
                                  "treatment": "construction", "profile": {"plan": {}, "search": {}}})
        value["attempts"].append({"family": family, "candidate": "candidate-002", "qualified": True,
                                  "ndcg_at_10": .6, "skill_digest": "sha256:"+"a"*64})
        for route in sorted(VIEWS.ROUTES[family], key=lambda name: (name != VIEWS.PRIMARY[family], name)):
            value["routes"].append({"family": family, "candidate": "candidate-002", "primary": route == VIEWS.PRIMARY[family],
                                    "dataset": "enterprise-rag-40", "questions": 40, "treatment": "construction",
                                    "route": route, "ndcg_at_10": .6, "recall_at_10": .7,
                                    "mrr_at_10": .8, "query_p95_ms": 15})
    return value


def test_projection_preserves_selected_route_and_excludes_arbitrary_content(published):
    secondary = copy.deepcopy(published["routes"][0])
    secondary.update(primary=False, route="stronger-secondary", ndcg_at_10=1)
    published["routes"].append(secondary)
    contract, profiles = VIEWS.project(published, "b"*64)
    assert len(contract["alternatives"]) == len(profiles) == 8
    assert all(row["metrics"]["ndcg_at_10"] == 60 for row in contract["alternatives"])
    assert "stronger-secondary" not in json.dumps(contract)
    assert "PRIVATE" not in json.dumps([contract, profiles])
    assert contract["dataset_scope"]["metric_contract"].endswith("b"*64)


@pytest.mark.parametrize("failure", ["missing-family", "duplicate-primary", "unqualified", "cohort", "disagreement", "nan", "answer-quality"])
def test_projection_rejects_incomplete_or_inconsistent_evidence(published, failure):
    if failure == "missing-family":
        published["families"].pop()
    elif failure == "duplicate-primary":
        published["routes"].append(copy.deepcopy(published["routes"][0]))
    elif failure == "unqualified":
        published["attempts"][0]["qualified"] = False
    elif failure == "cohort":
        published["routes"][0]["questions"] = 39
    elif failure == "disagreement":
        published["families"][0]["winner_ndcg_at_10"] = .9
    elif failure == "nan":
        published["routes"][0]["recall_at_10"] = float("nan")
    else:
        published["answer_quality_evaluated"] = True
    with pytest.raises(ValueError):
        VIEWS.project(published, "b"*64)


def test_publication_validates_contract_and_refuses_overwrite(published, tmp_path):
    source = tmp_path / "development" / "aggregates.json"
    source.parent.mkdir()
    source.write_text(json.dumps(published), encoding="utf-8")
    output = tmp_path / "catalog"
    VIEWS.publish(source, output)
    assert sorted(path.name for path in output.iterdir()) == ["comparison.json", "comparison.md", "profiles.md", "routes.md"]
    combined = "\n".join(path.read_text(encoding="utf-8") for path in output.iterdir())
    assert "PRIVATE" not in combined
    assert "../development/README.md" in combined
    assert "60.00%" in combined
    with pytest.raises(FileExistsError):
        VIEWS.publish(source, output)


def test_all_retained_routes_remain_diagnostic_and_reject_missing_secondary_rows(published):
    secondary = next(row for row in published["routes"] if not row["primary"])
    secondary["ndcg_at_10"] = .99
    rejected = copy.deepcopy(secondary)
    rejected.update(candidate="rejected-candidate", ndcg_at_10=1)
    published["routes"].append(rejected)
    routes = VIEWS.retained_routes(published)
    assert len(routes) == 18
    assert sum(row["primary"] for row in routes) == 8
    assert any(row["metrics"]["ndcg_at_10"] == 99 for row in routes)
    assert not any(row["candidate"] == "rejected-candidate" for row in routes)
    contract, _ = VIEWS.project(published, "b"*64)
    assert all(row["metrics"]["ndcg_at_10"] == 60 for row in contract["alternatives"])
    published["routes"].remove(secondary)
    with pytest.raises(ValueError, match="Incomplete"):
        VIEWS.retained_routes(published)


@pytest.fixture
def terminal():
    selection = {"family": "classical", "candidate": "candidate-002", "skill_digest": "sha256:"+"a"*64,
                 "unchanged": False, "source": "PRIVATE CANDIDATE PATH"}
    decision = {"schema_version": "enterprise-terminal-decision/1.0", "selected_family": "classical",
                "selected_candidate": "candidate-002", "selected_skill_digest": selection["skill_digest"],
                "decision": "accepted-for-declared-scope", "promoted": True, "private_gate_opened": True,
                "source_groups": 2, "questions_per_group": 12, "native_status": "complete",
                "baseline_mean": .5, "candidate_mean": .6, "mean_gain": .1,
                "baseline_qualified": True, "candidate_qualified": True, "regressed_group_count": 0,
                "rules": {"minimumMeanGain": 0.0, "allowCaseRegressions": False, "requireNoErrors": True},
                "further_evolution_permitted": False, "canonical_skill_installed": False,
                "perCase": "PRIVATE CASE IDS", "question": "PRIVATE QUESTION"}
    return decision, selection


def write_terminal_inputs(tmp_path, published, terminal):
    source, decision, selection = (tmp_path / name for name in ("aggregates.json", "decision.json", "selection.json"))
    for path, value in zip((source, decision, selection), (published, *terminal)):
        path.write_text(json.dumps(value), encoding="utf-8")
    return source, decision, selection


@pytest.mark.parametrize("outcome", ["accepted", "rejected", "unchanged", "unavailable"])
def test_terminal_projection_preserves_decision_and_omits_private_details(tmp_path, published, terminal, outcome):
    decision, selection = terminal
    if outcome == "rejected":
        decision.update(decision="keep-baseline", promoted=False, regressed_group_count=1)
    elif outcome == "unchanged":
        selection["unchanged"] = True
        decision.update(decision="baseline-retained", promoted=False, private_gate_opened=False)
    elif outcome == "unavailable":
        decision.update(decision="keep-baseline", promoted=False, native_status="non-evaluable",
                        candidate_mean=None, mean_gain=None, candidate_qualified=False)
    inputs = write_terminal_inputs(tmp_path, published, terminal)
    output = tmp_path / "terminal"
    VIEWS.publish_terminal(*inputs, output)
    projection = json.loads((output / "decision.json").read_text())
    report = (output / "README.md").read_text(encoding="utf-8")
    assert projection["decision"] == decision["decision"]
    assert projection["private_gate_opened"] == decision["private_gate_opened"]
    assert projection["canonical_skill_installed"] is False
    assert projection["selected_development_ndcg_at_10"] == .6
    assert len(projection["source_sha256"]) == 3
    assert "PRIVATE" not in json.dumps(projection)+report
    if outcome == "unchanged":
        assert "validation" not in projection
        assert "was not opened" in report
    elif outcome == "unavailable":
        assert projection["validation"]["candidate_mean"] is None
        assert "N/A" in report
    with pytest.raises(FileExistsError):
        VIEWS.publish_terminal(*inputs, output)


@pytest.mark.parametrize("failure", ["candidate", "digest", "release", "scope", "nan", "gain", "regression", "qualification", "unfinished"])
def test_terminal_projection_rejects_unbound_or_inconsistent_decision(tmp_path, published, terminal, failure):
    decision, selection = terminal
    if failure == "candidate":
        selection["candidate"] = "candidate-003"
    elif failure == "digest":
        selection["skill_digest"] = "sha256:"+"b"*64
    elif failure == "release":
        decision["private_gate_opened"] = False
    elif failure == "scope":
        decision["source_groups"] = 3
    elif failure == "nan":
        decision["candidate_mean"] = float("nan")
    elif failure == "gain":
        decision["mean_gain"] = .2
    elif failure == "regression":
        decision["regressed_group_count"] = 1
    elif failure == "qualification":
        decision["candidate_qualified"] = False
    else:
        decision["further_evolution_permitted"] = True
    inputs = write_terminal_inputs(tmp_path, published, terminal)
    output = tmp_path / "terminal"
    with pytest.raises(ValueError):
        VIEWS.publish_terminal(*inputs, output)
    assert not output.exists()
