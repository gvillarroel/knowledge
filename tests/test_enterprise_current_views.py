"""Exercise current-view publication using public, immutable E14 aggregates only."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("enterprise_current_views", ROOT / "evaluations/refresh_enterprise_current_views.py")
VIEWS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VIEWS)
CURRENT = "graphify-generation-008-001"
PRIOR = "graphify-generation-007-001"
INVENTORY = "opportunity-accounting-002"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.fixture
def workspace(tmp_path):
    for leaf, names in ((CURRENT, ["README.md", "aggregate.json", "comparison.md", "groups.md", "cta.md"]),
                        (PRIOR, ["aggregate.json"]), ("graphify-generation-004-001", ["aggregate.json"]),
                        ("graphify-generation-003-001", ["aggregate.json"]), ("turso-generation-008-001", ["aggregate.json"]),
                        (INVENTORY, ["README.md", "aggregate.json"])):
        for name in names:
            relative = VIEWS.BASE / leaf / name
            target = tmp_path / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((ROOT / relative).read_bytes())
    for name in [*VIEWS.INDEXES, *[f"evaluations/reports/skills/{family}.md" for family in VIEWS.FAMILIES]]:
        page = tmp_path / name
        page.parent.mkdir(parents=True, exist_ok=True)
        def link(leaf):
            return Path(os.path.relpath(tmp_path / VIEWS.BASE / leaf / "comparison.md", page.parent)).as_posix()
        content = (f"# Authored index\r\n\r\n[Latest general application/category comparison]({link(CURRENT)})\r\n"
                   f"[Latest general application/category comparison]({link(PRIOR)})\r\n")
        if name not in VIEWS.INDEXES and name != "evaluations/reports/skills/graphify.md":
            content = "# Authored family index\r\n"
            if name == "evaluations/reports/skills/turso.md":
                content += f"[Latest general application/category comparison]({link('turso-generation-008-001')})\r\n"
        if name in VIEWS.SECTIONS:
            first, last = VIEWS.SECTIONS[name]
            content += f"\r\n## {first}\r\n\r\nOutdated current table.\r\n\r\n## {last}\r\n"
        content += "\r\nAuthored history: naïve text, | Graphify | 8.12 |; keep exactly.\r\n"
        page.write_bytes(content.encode())
    return tmp_path


def plan(root):
    return VIEWS.plan_views(root, CURRENT, sha(root / VIEWS.BASE / CURRENT / "aggregate.json"),
                           INVENTORY, sha(root / VIEWS.BASE / INVENTORY / "aggregate.json"))


def test_real_aggregate_drives_all_current_tables_and_preserves_history(workspace):
    changes = plan(workspace)
    assert len(changes) == 16
    for name, (before, after) in changes.items():
        assert before.endswith("Authored history: naïve text, | Graphify | 8.12 |; keep exactly.\r\n".encode())
        assert after.endswith(before[before.index(b"Authored history:"):])
        if name in VIEWS.INDEXES or name.endswith(("/graphify.md", "/turso.md")):
            assert b"[Comparison at this observation]" in after
        else:
            assert before == after
        if name in VIEWS.SECTIONS:
            assert b"| Graphify | 52.33 | Qualified |" in after
            assert b"| Legacy | 72.38 | Qualified |" in after
            assert b"| Turso | 72.38 | Qualified |" in after
            assert after.count(b"Unavailable after execution error") == 2
            assert b"61 improve, 4 regress and 47 tie" in after
            assert b"5 catalog stops" in after and b"2 unavailable historical hypotheses" in after
            assert b"120 stratified questions, 112 retrieval-eligible questions" in after
            assert b"Luna answer audit" in after and b"public leaderboard position" in after
            assert b"| Gmail | Legacy, Turso |" in after
            assert b"| Slack | Embeddings |" in after
        assert (workspace / name).read_bytes() == before


def test_check_never_writes_and_apply_is_idempotent(workspace):
    changes = plan(workspace)
    with pytest.raises(ValueError, match="views differ"):
        VIEWS.apply_views(workspace, changes, check=True)
    assert all((workspace / name).read_bytes() == before for name, (before, _) in changes.items())
    assert len(VIEWS.apply_views(workspace, changes)) == 10
    times = {name: (workspace / name).stat().st_mtime_ns for name in changes}
    assert VIEWS.apply_views(workspace, plan(workspace), check=True) == []
    assert VIEWS.apply_views(workspace, plan(workspace)) == []
    assert times == {name: (workspace / name).stat().st_mtime_ns for name in changes}


def test_late_input_drift_prevents_all_writes(workspace):
    changes = plan(workspace)
    last = next(reversed(changes))
    (workspace / last).write_bytes(b"Concurrent authored change")
    with pytest.raises(ValueError, match="changed after planning"):
        VIEWS.apply_views(workspace, changes)
    assert all((workspace / name).read_bytes() == before for name, (before, _) in changes.items() if name != last)


def test_failed_atomic_replacement_preserves_authored_bytes(workspace, monkeypatch):
    changes = plan(workspace)
    def fail_replace(*args):
        raise OSError("Simulated replacement failure")
    monkeypatch.setattr(VIEWS.os, "replace", fail_replace)
    with pytest.raises(OSError, match="Simulated replacement"):
        VIEWS.apply_views(workspace, changes)
    assert all((workspace / name).read_bytes() == before for name, (before, _) in changes.items())
    assert not list(workspace.rglob(".enterprise-current-*"))


def test_duplicate_json_keys_are_rejected(workspace):
    path = workspace / VIEWS.BASE / CURRENT / "aggregate.json"
    path.write_bytes(path.read_bytes().replace(b"{", b'{"goal_complete": false,', 1))
    with pytest.raises(ValueError, match="Duplicate JSON"):
        plan(workspace)


def test_predecessor_digest_must_match_before_relabeling(workspace):
    path = workspace / VIEWS.BASE / PRIOR / "aggregate.json"
    path.write_bytes(path.read_bytes() + b" ")
    with pytest.raises(ValueError, match="digest mismatch"):
        plan(workspace)


def test_indirect_public_predecessor_must_also_match_its_digest(workspace):
    path = workspace / VIEWS.BASE / "graphify-generation-004-001" / "aggregate.json"
    path.write_bytes(path.read_bytes() + b" ")
    with pytest.raises(ValueError, match="digest mismatch"):
        plan(workspace)


def test_other_family_history_loses_only_its_obsolete_latest_label(workspace):
    name = "evaluations/reports/skills/turso.md"
    before, after = plan(workspace)[name]
    assert after == before.replace(b"Latest general application/category comparison", b"Comparison at this observation")


def test_missing_report_companion_prevents_publication(workspace):
    (workspace / VIEWS.BASE / CURRENT / "cta.md").unlink()
    with pytest.raises(ValueError, match="missing file"):
        plan(workspace)


@pytest.mark.parametrize("relative", ["../outside.md", "evaluations/reports/evolution/e14/graphify-generation-008-001/README.md"])
def test_output_cannot_target_history_or_escape(workspace, relative):
    with pytest.raises(ValueError, match="outside mutable"):
        VIEWS.apply_views(workspace, {relative: (b"before", b"after")})


def test_digest_drift_is_rejected_before_planning(workspace):
    with pytest.raises(ValueError, match="digest mismatch"):
        VIEWS.plan_views(workspace, CURRENT, "0" * 64, INVENTORY,
                         sha(workspace / VIEWS.BASE / INVENTORY / "aggregate.json"))


@pytest.mark.parametrize("bad", [True, "0.5", None, -0.1, 1.1, float("nan"), float("inf")])
def test_invalid_metric_never_becomes_a_published_number(workspace, bad):
    path = workspace / VIEWS.BASE / CURRENT / "aggregate.json"
    value = json.loads(path.read_text())
    group = next(g for g in value["cross_family_comparison"]["groups"] if g["dimension"] == "all")
    group["retained_metrics"]["graphify"]["ndcg_at_10"] = bad
    path.write_text(json.dumps(value))
    with pytest.raises(ValueError, match="finite"):
        plan(workspace)


@pytest.mark.parametrize("mutation", ["row", "pair", "leader", "scope", "gap", "duplicate-family"])
def test_contradictory_public_evidence_is_rejected(workspace, mutation):
    path = workspace / VIEWS.BASE / (INVENTORY if mutation == "gap" else CURRENT) / "aggregate.json"
    value = json.loads(path.read_text())
    if mutation == "row":
        value["retained_comparison"][0]["retained_display_value"] = "1.23"
    elif mutation == "pair":
        group = next(g for g in value["family_prefix"]["groups"] if g["dimension"] == "all")
        pair = next(p for p in group["comparisons"] if p["reference"] == "versioned-007" and p["candidate"] == "versioned-008")
        pair["paired_cases"]["improved"] += 1
    elif mutation == "leader":
        next(g for g in value["cross_family_comparison"]["groups"] if g["group"] == "gmail")["descriptive_ndcg_leaders"] = ["graphify"]
    elif mutation == "scope":
        value["cross_family_comparison"]["promoted"] = True
    elif mutation == "gap":
        value["historical_unavailable_hypotheses_among_stopped_families"] = 0
    else:
        value["retained_comparison"][-1] = value["retained_comparison"][0]
    path.write_text(json.dumps(value))
    with pytest.raises(ValueError):
        plan(workspace)


@pytest.mark.parametrize("problem", ["missing", "duplicate", "reverse"])
def test_section_boundaries_must_be_unambiguous(workspace, problem):
    name, (first, last) = next(iter(VIEWS.SECTIONS.items()))
    page = workspace / name
    text = page.read_text()
    if problem == "missing":
        text = text.replace("## " + first, "## Changed heading")
    elif problem == "duplicate":
        text += "\n## " + first + "\n"
    else:
        text = text.replace("## " + first, "## TEMP").replace("## " + last, "## " + first).replace("## TEMP", "## " + last)
    page.write_text(text)
    with pytest.raises(ValueError, match="section boundaries"):
        plan(workspace)


def test_newer_or_unbound_latest_link_cannot_be_downgraded(workspace):
    page = workspace / "evaluations/reports/evolution/e14/README.md"
    page.write_bytes(page.read_bytes().replace(PRIOR.encode(), b"graphify-generation-009-001"))
    with pytest.raises(ValueError, match="predecessor bindings"):
        plan(workspace)


def test_selected_report_must_already_be_exported_to_each_index(workspace):
    page = workspace / "docs/README.md"
    page.write_bytes(page.read_bytes().replace(CURRENT.encode(), PRIOR.encode()))
    with pytest.raises(ValueError, match="has not been exported"):
        plan(workspace)


def test_unknown_source_text_is_not_copied_into_current_views(workspace):
    path = workspace / VIEWS.BASE / CURRENT / "aggregate.json"
    value = json.loads(path.read_text())
    value["question"] = value["gold_answer"] = "DO NOT PUBLISH SOURCE TEXT"
    path.write_text(json.dumps(value))
    assert all(b"DO NOT PUBLISH" not in after for _, after in plan(workspace).values())


def test_cli_requires_explicit_action_and_supports_read_only_check(workspace, monkeypatch, capsys):
    monkeypatch.setattr(VIEWS, "ROOT", workspace)
    argv = ["--comparison", CURRENT, "--comparison-sha256", sha(workspace / VIEWS.BASE / CURRENT / "aggregate.json"),
            "--inventory", INVENTORY, "--inventory-sha256", sha(workspace / VIEWS.BASE / INVENTORY / "aggregate.json")]
    with pytest.raises(SystemExit):
        VIEWS.main(argv)
    assert VIEWS.main([*argv, "--apply"]) == 0
    assert VIEWS.main([*argv, "--check"]) == 0
    assert '"new_native_jobs": 0' in capsys.readouterr().out
