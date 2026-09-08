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
from profiles import FAMILIES, CONSTRUCTION, mutate, baseline_profile
from sweep import Sweep

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
    manifest = read(WORK / "execution-contract.json")
    # Organizer registrations contain native Windows absolute paths. Verify
    # them on their original host; never reinterpret those paths under Linux.
    guard_path = windows_path(HERE / "study_guard.py")
    result = subprocess.run([manifest["windows_python"], "-B", guard_path, phase], capture_output=True, text=True, check=False)
    if result.returncode:
        raise ValueError("Organizer rejected dispatch: " + result.stderr[-1500:])
    return json.loads(result.stdout)


def realizer(action, path):
    interpreter = read(WORK / "execution-contract.json")["windows_python"]
    result = subprocess.run([interpreter, "-B", windows_path(REALIZER), action, windows_path(path)], capture_output=True, text=True, check=False)
    if result.returncode:
        raise ValueError("Realizer rejected candidate: " + result.stderr[-1500:])
    return json.loads(result.stdout)


def realize(family, identifier, parent, profile, strategy, evidence):
    root = WORK / "realizations" / family / identifier
    parent_digest = realizer("digest", parent)["treeSha256"]
    interpreter = windows_path(read(WORK / "execution-contract.json")["windows_python"])
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
        "search": {"id": "enterprise-e6-"+family, "baselineSkill": baseline["skill"], "baselineCandidate": "baseline", "outputDir": str(WORK / "search" / family), "generation": generation},
        "harbor": {"developmentJob": str(WORK / "jobs" / (family+"-development.json")), "holdoutJob": str(WORK / "jobs" / (family+"-validation.json")), "rewardKey": "reward", "passThreshold": .8, "requiredRewards": {"evidence_integrity": 1}, "requiredEnv": []},
        "candidates": candidates,
        "promotion": {"minimumMeanGain": 0.0, "allowCaseRegressions": False, "requireNoErrors": True}}
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


def run_family(family):
    owner = load("pareto_owner_" + family.replace("-", "_"), OWNER)
    protocol = read(WORK / "protocol.json")
    candidates = [{"id": "baseline", "skill": str(WORK / "baseline" / NAME), "parents": [], "rationale": "Frozen new-study control, carrying the previously measured MiniLM construction profile."}]
    candidates, baseline, archive = evaluate_new(owner, family, 0, candidates, "baseline")
    if not baseline["evaluable"] or not baseline["qualification"]["passed"]:
        raise RuntimeError("Family baseline is not evaluable and qualified: " + family)
    if not math.isclose(baseline["summary"]["meanReward"], protocol["baseline_expected_scores"][family], rel_tol=0, abs_tol=1e-12):
        raise RuntimeError("New native control did not reproduce the historical family incumbent: " + family)
    seed_profile = read(Path(candidates[0]["skill"]) / "assets/retrieval-profile.json")
    sweep = Sweep(protocol["strategies"][family], "baseline", baseline["summary"]["meanReward"], seed_profile)
    generation = 0
    outcomes = [{"candidate": "baseline", "strategy": "baseline", "score": sweep.best_score, "job": baseline["jobDirectory"], "archive": str(archive_path(family, 0))}]
    print(json.dumps({"event": "baseline", "family": family, "score": sweep.best_score}), flush=True)
    while item := sweep.next():
        strategy, variant = item
        profile = mutate(sweep.profile, family, variant)
        if not sweep.claim(profile):
            continue
        generation += 1
        identifier = f"candidate-{generation:03d}"
        parent = next(c for c in candidates if c["id"] == sweep.best_id)
        child = realize(family, identifier, Path(parent["skill"]), profile, strategy, archive_path(family, generation-1))
        keep = [c for c in candidates if c["id"] in {"baseline", sweep.best_id}]
        # Old candidates retain original parent declarations; dependencies needed
        # by the owner are included as factual previously evaluated candidates.
        ancestry = {p for c in keep for p in c["parents"]}
        while any(c["id"] in ancestry and c not in keep for c in candidates):
            keep += [c for c in candidates if c["id"] in ancestry and c not in keep]
            ancestry = {p for c in keep for p in c["parents"]}
        keep.append({"id": identifier, "skill": str(child), "parents": [sweep.best_id], "rationale": strategy["rationale"] + " Exact settings are sealed in the realizer mutation contract."})
        current, record, archive = evaluate_new(owner, family, generation, keep, identifier)
        candidates = current
        score = record["summary"]["meanReward"]
        improved = sweep.observe(identifier, profile, score, evaluable=record["evaluable"], qualified=record["qualification"]["passed"])
        outcome = {"candidate": identifier, "strategy": strategy["id"], "variant": variant, "score": score, "qualified": record["qualification"]["passed"], "improved": improved, "consecutive_failures": sweep.failures, "best_candidate": sweep.best_id, "best_score": sweep.best_score, "job": record["jobDirectory"], "archive": str(archive_path(family, generation))}
        outcomes.append(outcome)
        write(WORK / "progress" / family / f"{generation:03d}.json", {"outcome": outcome, "events": sweep.events})
        print(json.dumps({"event": "attempt", "family": family, **{k: outcome[k] for k in ("candidate", "strategy", "score", "improved", "consecutive_failures", "best_score")}}), flush=True)
    winner = next(c for c in candidates if c["id"] == sweep.best_id)
    if archive["bestAggregateCandidate"] != sweep.best_id:
        raise ValueError("Scheduler incumbent differs from native owner's final selection")
    result = {"family": family, "treatment": protocol["treatments"][family], "status": "catalog-exhausted", "generation": generation, "baseline_score": baseline["summary"]["meanReward"], "winner": winner, "score": sweep.best_score, "profile": sweep.profile, "outcomes": outcomes, "events": sweep.events, "final_archive": str(archive_path(family, generation)), "final_config": str(WORK / "dispatch" / family / f"generation-{generation:03d}" / "analyze.json")}
    write(WORK / "family-results" / (family+".json"), result)
    print(json.dumps({"event": "family-complete", "family": family, "attempts": generation, "score": sweep.best_score}), flush=True)
    return result


def run():
    if os.name == "nt":
        raise ValueError("Native execution requires Linux/WSL")
    verify_frozen()
    write(WORK / "dispatch-start.json", {"contract_sha256": sha(WORK / "execution-contract.json"), "families": list(FAMILIES), "resubmission": False})
    errors, results = [], []
    # The order within each knowledge family is strictly sequential. Families
    # are independent lanes sharing the same resource ceiling and fixed design.
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        pending = {pool.submit(run_family, family): family for family in FAMILIES}
        for future in concurrent.futures.as_completed(pending):
            if future.cancelled():
                continue
            try:
                results.append(future.result())
            except Exception as exc:
                import traceback
                error = {"family": pending[future], "type": type(exc).__name__, "message": str(exc), "traceback": traceback.format_exc()}
                errors.append(error)
                write(WORK / "errors" / (pending[future]+".json"), error)
                for other in pending:
                    if other is not future:
                        other.cancel()
                print(json.dumps({"event": "campaign-error", "family": pending[future], "type": type(exc).__name__}), flush=True)
    if errors:
        write(WORK / "development-stop.json", {"status": "blocked", "errors": errors, "completed_families": [r["family"] for r in results], "validation_opened": False})
        raise RuntimeError("Preserve native failures; development did not complete")
    def order(result):
        family = result["family"]
        seed = baseline_profile()[family]
        changed = sum(value != seed[channel].get(key) for channel in ("plan", "search") for key, value in result["profile"][family][channel].items())
        return (-result["score"], changed, result["family"])
    selected = sorted(results, key=order)[0]
    write(WORK / "development-result.json", {"status": "complete", "selected_family": selected["family"], "selected_candidate": selected["winner"], "score": selected["score"], "profile": selected["profile"], "final_config": selected["final_config"], "families": [{k: row[k] for k in ("family", "treatment", "generation", "baseline_score", "score", "final_archive")} for row in sorted(results, key=order)], "validation_opened": False})
    print(json.dumps({"event": "development-complete", "selected_family": selected["family"], "score": selected["score"]}), flush=True)


if __name__ == "__main__":
    run()
