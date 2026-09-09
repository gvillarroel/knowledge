"""Execute a sealed finite sweep through the installed native Harbor owner.

Completed jobs are imported at their exact staged skill path; only a new child
is executed. The owning Pareto analyzer verifies every comparison and lineage.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import importlib.util
import json
import math
import os
import shutil
import subprocess
import sys
from pathlib import Path

from prepare import HERE, REPO, WORK, OLD, NAME, OWNER, HPY, ORGANIZER, read, write, tree, sha, posix, organize
from prepare import FAMILIES, CONSTRUCTION, EXECUTION_CONTRACT

REALIZER = Path("/mnt/c/Users/villa/.codex/skills/harbor-realize-skill-candidate/scripts/realize_skill_candidate.py")


def windows_path(value):
    text = str(value)
    if not text.startswith("/mnt/c/"):
        raise ValueError("Expected a path in the shared Windows workspace")
    return "C:/" + text[len("/mnt/c/"):]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def verify_frozen(phase="development"):
    manifest = read(WORK / EXECUTION_CONTRACT)
    # Organizer registrations contain native Windows absolute paths. Verify
    # them on their original host; never reinterpret those paths under Linux.
    guard_path = windows_path(HERE / "study_guard.py")
    result = subprocess.run([manifest["windows_python"], "-B", guard_path, phase], capture_output=True, text=True, check=False)
    if result.returncode:
        raise ValueError("Organizer rejected dispatch: " + result.stderr[-1500:])
    return json.loads(result.stdout)


def realizer(action, path):
    interpreter = read(WORK / EXECUTION_CONTRACT)["windows_python"]
    result = subprocess.run([interpreter, "-B", windows_path(REALIZER), action, windows_path(path)], capture_output=True, text=True, check=False)
    if result.returncode:
        raise ValueError("Realizer rejected candidate: " + result.stderr[-1500:])
    return json.loads(result.stdout)


def realize(family, identifier, parent, profile, strategy, evidence):
    root = WORK / "realizations" / family / identifier
    parent_digest = realizer("digest", parent)["treeSha256"]
    interpreter = windows_path(read(WORK / EXECUTION_CONTRACT)["windows_python"])
    config = {"schemaVersion": 1, "realization": {"id": family+"-"+identifier, "candidateId": identifier,
        "parentSkill": windows_path(parent), "expectedParentTreeSha256": parent_digest,
        "workspaceDir": windows_path(root / "workspace"), "outputDir": windows_path(root / "sealed"),
        "operator": {"operatorId": strategy["id"], "instruction": strategy["rationale"]+" Apply exactly the bound profile change. Preserve all other package bytes.", "origin": "predeclared-development-hypothesis", "parentOperatorIds": []},
        "allowedChanges": ["assets/retrieval-profile.json"],
        "developmentEvidence": [{"id": "native-parent-archive", "role": "development", "path": windows_path(evidence), "sha256": "sha256:"+sha(evidence)}, {"id": "frozen-operator-catalog", "role": "development", "path": windows_path(WORK / "protocol.json"), "sha256": "sha256:"+sha(WORK / "protocol.json")}],
        "trustedValidationCommands": True,
        "validationCommands": [{"id": "closed-profile", "argv": [interpreter, "-B", windows_path(HERE / "validate_profile.py")], "timeoutSeconds": 60}]}}
    write(root / "mutation-contract.json", {"family": family, "strategy": strategy, "parent_digest": parent_digest, "exact_profile": profile, "parent_archive_sha256": sha(evidence)})
    config["realization"]["developmentEvidence"].append({"id": "exact-mutation", "role": "development", "path": windows_path(root / "mutation-contract.json"), "sha256": "sha256:"+sha(root / "mutation-contract.json")})
    path = root / "realizer.json"
    write(path, config)
    prepared = realizer("prepare", path)
    candidate = root / "workspace/candidate/skills" / NAME
    (candidate / "assets/retrieval-profile.json").write_text(json.dumps(profile, indent=2, sort_keys=True, allow_nan=False)+"\n", encoding="utf-8")
    sealed, verified = realizer("seal", path), realizer("verify", path)
    write(root / "receipt.json", {"prepare": prepared, "seal": sealed, "verify": verified})
    return root / "sealed/candidate/skills" / NAME


def raw_config(family, generation, candidates):
    baseline = next(row for row in candidates if row["id"] == "baseline")
    result = {"schemaVersion": 1,
        "search": {"id": "enterprise-e8-"+family, "baselineSkill": baseline["skill"], "baselineCandidate": "baseline", "outputDir": str(WORK / "search" / family), "generation": generation},
        "harbor": {"developmentJob": str(WORK / "jobs" / (family+"-development.json")), "holdoutJob": str(WORK / "jobs" / (family+"-validation.json")), "rewardKey": "reward", "passThreshold": .8, "requiredRewards": {"evidence_integrity": 1}, "requiredEnv": []},
        "candidates": candidates,
        "promotion": {"minimumMeanGain": 0.0, "allowCaseRegressions": family == "joint", "requireNoErrors": True}}
    if generation:
        result["search"]["previousGenerationLog"] = str(archive_path(family, generation-1))
    return result


def archive_path(family, generation):
    return WORK / "search" / family / "development" / f"generation-{generation:03d}" / "pareto-archive.json"


def evaluate_new(owner, family, generation, candidates, new_id):
    verify_frozen()
    root = WORK / "dispatch" / family / f"generation-{generation:03d}"
    raw = raw_config(family, generation, candidates)
    live_path = root / "live.json"
    write(live_path, raw)
    config = owner.normalize_config(live_path)
    # This is the owner's native staging and Job execution, not another scorer.
    record = owner.run_candidate_jobs(config, phase="development", analyze_only=False, candidate_ids=[new_id])[0]
    for candidate in raw["candidates"]:
        if candidate["id"] == new_id:
            candidate["skill"] = record["evaluatedSkill"]
            candidate["jobDirectory"] = record["jobDirectory"]
    raw["search"]["baselineSkill"] = next(c["skill"] for c in raw["candidates"] if c["id"] == "baseline")
    analyzed_path = root / "analyze.json"
    write(analyzed_path, raw)
    analyzed = owner.normalize_config(analyzed_path)
    result = owner.development(analyzed, analyze_only=True)
    archive = read(archive_path(family, generation))
    if not archive["promotionEligibleProfile"]:
        raise ValueError("Native owner rejected declared/observed profile parity")
    for row in archive["candidateResults"]:
        if not row["promotionEligibleProvenance"]:
            raise ValueError("Native candidate provenance is not exact")
    record = next(row for row in archive["candidateResults"] if row["candidateId"] == new_id)
    write(root / "receipt.json", {"owner_result": result, "archive_sha256": sha(archive_path(family, generation)), "new_candidate": new_id, "new_job": record["jobDirectory"], "reused_completed_jobs": [c["jobDirectory"] for c in raw["candidates"] if c["id"] != new_id]})
    return raw["candidates"], record, archive
