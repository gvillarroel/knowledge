"""Report the frozen finalist rule over an existing native Pareto archive.

This reporter neither scores tasks nor creates candidates, starts evaluations,
releases private data, or promotes a package. The native owner verifies the
archive and exact selected-package binding before an audit can be published.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import subprocess
from pathlib import Path

from aggregate_development import number, read
from prepare_experiment import REPO, WORK, sha, write_json, wsl_path
from run_search import CONTROLLER, HARBOR_PYTHON, assert_frozen


RULES = {
    "minimum_mean_gain": .01,
    "order": ["native_aggregate_mean_descending", "fewer_baseline_cell_regressions", "fewer_profile_operations", "lexical_candidate_id"],
    "archive_scope": "qualified members of the final native generation archive",
    "expected_cells_per_profile": 32,
}


def native_value(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not 0 <= value <= 1:
        raise ValueError("Expected a finite native binary nDCG value")
    return value


def complete(record):
    summary = record["summary"]
    return (record["evaluable"] is True and record["qualification"]["passed"] is True
            and record["promotionEligibleProvenance"] is True and record["lockPresent"] is True
            and summary["expectedTrials"] == summary["completedTrials"] == 32
            and summary["errorCount"] == 0)


def project(archive, operation_counts):
    """Apply only the already frozen tie-breaks to owner-provided scores."""
    if (archive.get("source") != "harbor" or archive.get("strategy") != "reflective-pareto-search"
            or archive.get("holdoutDataUsed") is not False or archive.get("promotionEligibleProfile") is not True
            or archive.get("requiredRewardThresholds") != {"evidence_integrity": 1}):
        raise ValueError("Expected the qualified development-only native profile")
    cases = archive["caseKeys"]
    if len(cases) != 32 or len(set(cases)) != 32:
        raise ValueError("The final archive must retain all 32 development cells")
    records = {row["candidateId"]: row for row in archive["candidateResults"]}
    if len(records) != len(archive["candidateResults"]) or "baseline" not in records:
        raise ValueError("Expected unique native candidates and the frozen baseline")
    baseline = records["baseline"]
    baseline_complete = complete(baseline)
    baseline_cases = {row["caseKey"]: row["meanReward"] for row in baseline["cases"]}
    if set(baseline_cases) != set(cases) or len(baseline["cases"]) != 32:
        raise ValueError("Baseline coverage differs from the archive")
    baseline_mean = native_value(baseline["summary"]["meanReward"]) if baseline_complete else None
    if baseline_complete:
        for value in baseline_cases.values():
            native_value(value)
    rows, seen = [], set()
    for entry in archive["archive"]:
        identifier = entry["candidateId"]
        if identifier in seen or identifier not in records:
            raise ValueError("Archive membership is duplicated or unsupported")
        seen.add(identifier)
        record = records[identifier]
        if not complete(record) or any(entry.get(key) is not True for key in ("qualified", "evaluable", "promotionEligibleProvenance")):
            raise ValueError("Final archive membership is not completely qualified")
        if entry["skillDigest"] != record["skillDigest"]:
            raise ValueError("Archive package digest differs from its native result")
        values = {row["caseKey"]: native_value(row["meanReward"]) for row in entry["vector"]}
        if set(values) != set(cases) or len(entry["vector"]) != 32:
            raise ValueError("A finalist omits or duplicates development cells")
        mean = native_value(entry["aggregateMean"])
        if not math.isclose(mean, native_value(record["summary"]["meanReward"]), rel_tol=0, abs_tol=1e-12):
            raise ValueError("Native archive and candidate means disagree")
        operations = operation_counts[identifier]
        if isinstance(operations, bool) or not isinstance(operations, int) or not 0 <= operations <= 4 or (identifier == "baseline") != (operations == 0):
            raise ValueError("Unexpected closed-profile operation count")
        rows.append({"candidate": identifier, "skill_digest": entry["skillDigest"], "native_mean_ndcg_at_10": mean,
                     "mean_gain": mean - baseline_mean if baseline_complete else None,
                     "regressed_cells": sum(values[key] < baseline_cases[key] for key in cases) if baseline_complete else None,
                     "operations": operations})
    rows.sort(key=lambda row: (-row["native_mean_ndcg_at_10"], row["regressed_cells"] if baseline_complete else 0, row["operations"], row["candidate"]))
    first = rows[0] if rows else None
    eligible = baseline_complete and first is not None and first["candidate"] != "baseline" and first["mean_gain"] >= RULES["minimum_mean_gain"]
    return {"schema_version": "retrieval-final-selection/1.0", "phase": "final-development-selection-audit",
            "rules": RULES, "generation": archive["generation"], "generation_seal": archive["generationSeal"],
            "development_profile_digest": archive["developmentProfileDigest"], "baseline_qualified": baseline_complete,
            "baseline_mean_ndcg_at_10": baseline_mean, "ranked_first": first["candidate"] if first else None,
            "selected_candidate": first["candidate"] if eligible else None,
            "selected_skill_digest": first["skill_digest"] if eligible else None,
            "eligible_for_one_way_validation": eligible,
            "decision": "freeze-finalist-for-independent-validation" if eligible else "retain-baseline-and-keep-validation-sealed",
            "archive_members": rows, "native_candidate_count": len(records),
            "qualified_native_candidate_count": sum(complete(row) for row in records.values()),
            "private_validation_used": False, "promotion_established": False}


def owner_binding(config, archive, output):
    """Ask the actual owner to verify its seal, profile and package binding."""
    code = """import importlib.util,json,sys
from pathlib import Path
spec=importlib.util.spec_from_file_location('selection_native_owner',sys.argv[1])
owner=importlib.util.module_from_spec(spec); sys.modules[spec.name]=owner; spec.loader.exec_module(owner)
settings=owner.normalize_config(Path(sys.argv[2]))
archive=owner.read_json(Path(sys.argv[3]))
owner.validate_archive_seal(archive,'final-development-selection')
records={row['candidateId']:row for row in archive['candidateResults']}
if set(records)!={row['id'] for row in settings['candidates']}:
    raise ValueError('Selection config and native candidate membership differ')
for candidate in settings['candidates']:
    if owner.compute_skill_digest(candidate['skill'])!=records[candidate['id']]['skillDigest']:
        raise ValueError('A candidate package changed after native development')
if settings.get('selectedCandidate'):
    selected,digest=owner.validate_development_archive_binding(settings,archive)
    print(json.dumps({'status':'pass','selectedCandidate':selected['candidateId'],'skillDigest':digest,'verifiedCandidatePackages':len(records)}))
else:
    print(json.dumps({'status':'pass','selectedCandidate':None,'gateBinding':'not-applicable-no-eligible-finalist','verifiedCandidatePackages':len(records)}))
"""
    command = ["env", "PYTHONDONTWRITEBYTECODE=1", "TMPDIR=" + wsl_path(WORK / "host-cache/tmp"),
               "XDG_CACHE_HOME=" + wsl_path(WORK / "host-cache/xdg"), HARBOR_PYTHON, "-B", "-c", code,
               wsl_path(CONTROLLER), wsl_path(config), wsl_path(archive)]
    result = subprocess.run((["wsl", "-d", "Ubuntu", "--exec"] if os.name == "nt" else []) + command,
                            capture_output=True, text=True, encoding="utf-8", check=False)
    (output / "owner.stdout.log").write_text(result.stdout, encoding="utf-8")
    (output / "owner.stderr.log").write_text(result.stderr, encoding="utf-8")
    if result.returncode:
        raise ValueError("The native owner rejected selection binding; inspect the preserved audit logs")
    return json.loads(result.stdout)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--generation", type=int, choices=(0, 1), required=True)
    args = parser.parse_args()
    state = assert_frozen()
    if (state["validationRelease"] is not None or state["holdoutRelease"] is not None
            or state["stages"]["evolve"]["status"] != "running"):
        raise ValueError("Final selection must precede completed evolution and every private release")
    if args.generation == 0 and (WORK / "pareto/development/generation-001").exists():
        raise ValueError("Use the final generation; an earlier archive cannot replace later work")
    source = WORK / f"pareto/development/generation-{args.generation:03d}/pareto-archive.json"
    archive = read(source)
    if archive["generation"] != args.generation or archive["searchId"] != "knowledge-retrieval-" + WORK.name:
        raise ValueError("Archive does not belong to this study and generation")
    config_path = WORK / f"search-generation-{args.generation:03d}.yaml"
    config = read(config_path)
    paths = {row["id"]: row["skill"] for row in config["candidates"]}
    from aggregate_development import host_path
    counts = {}
    for identifier, path in paths.items():
        if identifier == "baseline":
            counts[identifier] = 0
        else:
            counts[identifier] = len(read(host_path(path) / "assets/retrieval-profile.json")["operations"])
    report = project(archive, counts)
    audit = WORK / "decisions/final-selection"
    audit.mkdir(parents=True, exist_ok=False)
    if report["selected_candidate"] is not None:
        config["search"]["selectedCandidate"] = report["selected_candidate"]
        config["search"]["developmentArchive"] = wsl_path(source)
    binding_config = audit / "binding-config.json"
    write_json(binding_config, config)
    binding = owner_binding(binding_config, source, audit)
    if binding["selectedCandidate"] != report["selected_candidate"] or (report["selected_candidate"] and binding["skillDigest"] != report["selected_skill_digest"]):
        raise ValueError("Native owner and selection audit disagree")
    report.update(study=WORK.name, archive_sha256=sha(source), source_config_sha256=sha(config_path),
                  binding_config_sha256=sha(binding_config), native_owner_binding=binding,
                  native_owner_sha256=sha(CONTROLLER), reporter_sha256=sha(Path(__file__)))
    write_json(audit / "selection.json", report)
    output = REPO / "evaluations/reports/evolution" / WORK.name / "selection"
    output.mkdir(parents=True, exist_ok=False)
    write_json(output / "aggregates.json", report)
    lines = ["# Frozen development selection", "", "[Study overview](../README.md) · [Exact aggregate audit](aggregates.json)", "",
             f"Decision: **{report['decision']}**. This applies the predeclared finalist rule to generation {args.generation}'s native archive. It does not establish independent validation or promotion.", "",
             "The order is greatest native mean nDCG@10, then fewer cell regressions against baseline, fewer profile operations, and lexical candidate ID. Both baseline and finalist must be complete and qualified. Opening validation requires at least one percentage point of mean gain.", "",
             "| Final-archive member | Native nDCG@10 | Gain, pp | Regressed cells / 32 | Operations |", "|---|---:|---:|---:|---:|"]
    for row in report["archive_members"]:
        lines.append(f"| {row['candidate']} | {number(row['native_mean_ndcg_at_10'])} | {number(row['mean_gain'])} | {row['regressed_cells']} | {row['operations']} |")
    lines += ["", "Scores and gains use a 0–100 display scale. Gains are percentage points; ties and regressions use unrounded native values. The reporter creates no score, archive, candidate, private release or promotion. The installed owning controller separately verified its archive seal and, where eligible, the exact selected package/profile binding.", "",
              "The organizer must record the exact selected package, complete evolution and release the terminal portfolio before validation may execute. If no candidate qualifies, retain baseline and leave validation sealed.", ""]
    (output / "README.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"status": "selection-audit-published", "decision": report["decision"], "selected_candidate": report["selected_candidate"]}))


if __name__ == "__main__":
    main()
