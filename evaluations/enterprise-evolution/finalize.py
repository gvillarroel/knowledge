"""Freeze one development winner and run one terminal independent native gate."""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from prepare import WORK, NAME, OWNER, read, write, sha, organize
from report import host
from run import load, verify_frozen


def prepare_selection():
    if os.name != "nt":
        raise ValueError("Register selection on the Windows organizer host")
    from study_guard import verify
    verify("development")
    result = read(WORK / "development-result.json")
    if result["status"] != "complete" or len(result["families"]) != 8:
        raise ValueError("Every knowledge family must finish before selection")
    source = host(result["final_config"])
    config = read(source)
    family = result["selected_family"]
    selected = result["selected_candidate"]
    archive_path = WORK / "search" / family / "development" / f"generation-{config['search']['generation']:03d}" / "pareto-archive.json"
    archive = read(archive_path)
    if selected["id"] != archive["bestAggregateCandidate"]:
        raise ValueError("Finalist differs from the native development archive")
    member = next(row for row in archive["archive"] if row["candidateId"] == selected["id"])
    config["search"].update(selectedCandidate=selected["id"], developmentArchive=str(archive_path).replace("\\", "/").replace("C:/", "/mnt/c/"))
    write(WORK / "gate.json", config)
    unchanged = member["skillDigest"] == archive["developmentProfile"]["baselineSkillDigest"]
    write(WORK / "selection.json", {"family": family, "candidate": selected["id"], "source": selected["skill"], "skill_digest": member["skillDigest"], "archive_sha256": sha(archive_path), "gate_config_sha256": sha(WORK / "gate.json"), "unchanged": unchanged, "private_gate_opened": False})
    for row in result["families"]:
        organize("record-evidence", "--evidence-id", "development-"+row["family"], "--stage-id", "evolve", "--kind", "evolution-report", "--role", "development", "--path", WORK / "search" / row["family"] / "development")
    organize("record-evidence", "--evidence-id", "completed-sweep", "--stage-id", "evolve", "--kind", "decision", "--role", "decision", "--path", WORK / "development-result.json")
    organize("record-evidence", "--evidence-id", "frozen-finalist", "--stage-id", "evolve", "--kind", "candidate", "--role", "development", "--path", host(selected["skill"]))
    organize("record-evidence", "--evidence-id", "selection", "--stage-id", "evolve", "--kind", "decision", "--role", "decision", "--path", WORK / "selection.json")
    if unchanged:
        write(WORK / "terminal-decision.json", {"decision": "baseline-retained", "reason": "No new family incumbent surpassed the selected unchanged control.", "selected_family": family, "private_gate_opened": False, "promoted": False, "further_evolution_permitted": False})
        organize("record-evidence", "--evidence-id", "terminal-decision", "--stage-id", "evolve", "--kind", "decision", "--role", "decision", "--path", WORK / "terminal-decision.json")
    organize("transition", "--stage-id", "evolve", "--status", "completed")
    if unchanged:
        organize("transition", "--stage-id", "validate", "--status", "stopped", "--note", "Unchanged finalist; private portfolio remains unopened")
        organize("transition", "--stage-id", "publish", "--status", "stopped", "--note", "No validation release; reviewed development reports remain available externally")
    else:
        organize("release-validation", "--selection-id", "finalist", "--selected-stage", "evolve", "--candidate-evidence", host(selected["skill"]))
        organize("transition", "--stage-id", "validate", "--status", "running")
    print(json.dumps({"selected_family": family, "unchanged": unchanged, "next": "publication" if unchanged else "native-terminal-gate"}))


def run_gate():
    if os.name == "nt":
        raise ValueError("Native gate requires Linux/WSL")
    verify_frozen("validation")
    selection = read(WORK / "selection.json")
    if selection["unchanged"] or sha(WORK / "gate.json") != selection["gate_config_sha256"]:
        raise ValueError("Frozen selection or gate configuration changed")
    owner = load("enterprise_terminal_pareto", OWNER)
    config = owner.normalize_config(WORK / "gate.json")
    selected = next(row for row in config["candidates"] if row["id"] == config["selectedCandidate"])
    if str(selected["skill"]) != selection["source"]:
        raise ValueError("Native finalist differs from registered selection")
    result = owner.holdout(config, analyze_only=False)
    write(WORK / "gate-execution.json", result)
    print(json.dumps({"event": "terminal-native-gate-complete", "family": selection["family"]}), flush=True)


def close_gate():
    if os.name != "nt":
        raise ValueError("Close on the Windows organizer host")
    from study_guard import verify
    verify("validation")
    selection = read(WORK / "selection.json")
    source = WORK / "search" / selection["family"] / "holdout/promotion.json"
    promotion = read(source)
    gate = promotion["holdout"]
    rules = {"minimumMeanGain": 0.0, "allowCaseRegressions": False, "requireNoErrors": True}
    if gate["promotionRules"] != rules or len(gate["perCase"]) != 2 or promotion["selectedSkillDigest"] != selection["skill_digest"]:
        raise ValueError("Native gate scope or frozen candidate mismatch")
    decision = {"schema_version": "enterprise-terminal-decision/1.0", "source": "native-harbor-reflective-pareto", "selected_family": selection["family"], "selected_candidate": selection["candidate"], "selected_skill_digest": selection["skill_digest"], "native_promotion_sha256": sha(source), "decision": "accepted-for-declared-scope" if gate["promoted"] else "keep-baseline", "promoted": gate["promoted"], "private_gate_opened": True, "source_groups": 2, "questions_per_group": 12, "native_status": gate["status"], "mean_gain": gate["meanGain"], "baseline_mean": gate["baselineMeanReward"], "candidate_mean": gate["candidateMeanReward"], "baseline_qualified": gate["baselineQualified"], "candidate_qualified": gate["candidateQualified"], "regressed_group_count": len(gate["regressedCases"]), "rules": rules, "further_evolution_permitted": False, "canonical_skill_installed": False}
    write(WORK / "terminal-decision.json", decision)
    organize("record-evidence", "--evidence-id", "terminal-native-gate", "--stage-id", "validate", "--kind", "evolution-report", "--role", "validation", "--path", source.parent)
    organize("record-evidence", "--evidence-id", "terminal-decision", "--stage-id", "validate", "--kind", "decision", "--role", "decision", "--path", WORK / "terminal-decision.json")
    organize("transition", "--stage-id", "validate", "--status", "completed")
    organize("transition", "--stage-id", "publish", "--status", "running")
    print(json.dumps({"decision": decision["decision"], "promoted": decision["promoted"], "further_evolution_permitted": False}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=["prepare-selection", "run-gate", "close-gate"])
    phase = parser.parse_args().phase
    {"prepare-selection": prepare_selection, "run-gate": run_gate, "close-gate": close_gate}[phase]()
