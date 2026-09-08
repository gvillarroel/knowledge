"""Realize only supported native generation-zero merges; never score or select.

This campaign-local glue preserves the frozen controller and job templates.
It must run only after generation zero has its own completed native archive.
"""
from __future__ import annotations

import copy
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
sys.path.insert(0, str(REPO / "evaluations/skill-evolution"))

from aggregate_development import host_path, read
from prepare_experiment import HERE, PROTOCOL, WORK, sha, write_json, wsl_path
from prepare_study import organize
from realize_profiles import call, realize
from report_selection import complete, native_value, owner_binding
from run_search import CONTROLLER, HARBOR_PYTHON, assert_frozen, authorize_phase


SHORT = {
    "neural-record": "neural",
    "quarter-expansion": "expand",
    "bm25-low-b": "bm25",
    "stronger-titles": "titles",
}


def profile_preflight(config, archive, output, generation):
    """Ask the installed owner to reject profile/ancestry drift before any job."""
    code = """import importlib.util,json,sys
from pathlib import Path
spec=importlib.util.spec_from_file_location('merge_profile_owner',sys.argv[1])
owner=importlib.util.module_from_spec(spec); sys.modules[spec.name]=owner; spec.loader.exec_module(owner)
settings=owner.normalize_config(Path(sys.argv[2]))
archive=owner.read_json(Path(sys.argv[3]))
owner.validate_archive_seal(archive,'merge-profile-preflight')
if settings['id']!=archive['searchId'] or settings['generation']!=int(sys.argv[4]):
    raise ValueError('Search or generation identity drift')
profile=owner.development_profile(settings,owner.version('harbor'),archive['developmentProfile']['observedDevelopmentJobSignature'],owner.observed_profiles(archive['candidateResults']))
if profile!=archive['developmentProfile'] or owner.canonical_json_digest(profile)!=archive['developmentProfileDigest']:
    raise ValueError('Native development/promotion profile drift')
previous_seal=owner.validate_previous_generation_archive(settings,profile)
if settings['generation']==1 and previous_seal!=archive['generationSeal']:
    raise ValueError('The exact predecessor archive is required')
print(json.dumps({'status':'pass','generation':settings['generation'],'developmentProfileDigest':owner.canonical_json_digest(profile),'previousGenerationSeal':previous_seal,'nativeJobsStarted':0}))
"""
    command = ["env", "PYTHONDONTWRITEBYTECODE=1", "TMPDIR=" + wsl_path(WORK / "host-cache/tmp"),
               "XDG_CACHE_HOME=" + wsl_path(WORK / "host-cache/xdg"), HARBOR_PYTHON, "-B", "-c", code,
               wsl_path(CONTROLLER), wsl_path(config), wsl_path(archive), str(generation)]
    result = subprocess.run((["wsl", "-d", "Ubuntu", "--exec"] if os.name == "nt" else []) + command,
                            capture_output=True, text=True, encoding="utf-8", check=False)
    prefix = f"profile-generation-{generation:03d}"
    for label, content in (("stdout", result.stdout), ("stderr", result.stderr)):
        with (output / (prefix + "." + label + ".log")).open("x", encoding="utf-8") as stream:
            stream.write(content)
    if result.returncode:
        raise ValueError("Native preflight rejected profile/ancestry; preserve the audit logs")
    return json.loads(result.stdout)


def supported_merges(archive, profiles, grid):
    """Read native ordered merge plans, checking existing complementary support."""
    expected = {
        row["id"]: {k: v for k, v in row.items() if k not in {"id", "mechanism"}}
        for row in grid["generation_zero"]
    }
    if set(expected) != set(SHORT) or set(profiles) != set(expected):
        raise ValueError("Expected the exact four frozen generation-zero profiles")
    for identifier, profile in profiles.items():
        if profile != {"schema_version": "retrieval-profile/1.0", "operations": [expected[identifier]]}:
            raise ValueError("A parent profile differs from the frozen operation grid")
    if (archive.get("source") != "harbor" or archive.get("strategy") != "reflective-pareto-search"
            or archive.get("generation") != 0 or archive.get("holdoutDataUsed") is not False
            or archive.get("promotionEligibleProfile") is not True
            or archive.get("requiredRewardThresholds") != {"evidence_integrity": 1}):
        raise ValueError("Expected a qualified generation-zero development archive")
    records = {row["candidateId"]: row for row in archive["candidateResults"]}
    if len(records) != 5 or len(archive["candidateResults"]) != 5 or set(records) != {"baseline", *expected}:
        raise ValueError("Generation zero must contain the complete five-profile grid")
    if any(row["summary"]["expectedTrials"] != 32 or row["summary"]["completedTrials"] != 32 for row in records.values()):
        raise ValueError("Every registered development trial must finish before merging")
    if not complete(records["baseline"]):
        raise ValueError("A complete qualified baseline is required")
    keys = archive["caseKeys"]
    if len(keys) != 32 or len(set(keys)) != 32:
        raise ValueError("Expected all 32 distinct development cells")
    members = {row["candidateId"]: row for row in archive["archive"]}
    if len(members) != len(archive["archive"]) or not set(members) <= set(records):
        raise ValueError("Archive membership is duplicated or unsupported")
    vectors = {}
    for identifier, member in members.items():
        if not complete(records[identifier]) or any(member.get(k) is not True for k in ("qualified", "evaluable", "promotionEligibleProvenance")):
            raise ValueError("A native parent is not completely qualified")
        if member["skillDigest"] != records[identifier]["skillDigest"]:
            raise ValueError("Native archive and parent package digests disagree")
        values = {row["caseKey"]: native_value(row["meanReward"]) for row in member["vector"]}
        if len(member["vector"]) != 32 or set(values) != set(keys):
            raise ValueError("A parent omits or duplicates development cells")
        vectors[identifier] = values
    # The owner's generation seal does not include mergePlans. Check the full
    # sequence against its sealed, already ordered archive before applying a cap.
    expected_pairs = []
    member_ids = list(members)
    for index, left in enumerate(member_ids):
        for right in member_ids[index + 1:]:
            if any(vectors[left][key] > vectors[right][key] for key in keys) and any(vectors[right][key] > vectors[left][key] for key in keys):
                expected_pairs.append([left, right])
    if [plan["parentIds"] for plan in archive["mergePlans"]] != expected_pairs:
        raise ValueError("Native merge plans are omitted, added or reordered")
    order = {identifier: index for index, identifier in enumerate(expected)}
    chosen, skipped, seen = [], [], set()
    for index, plan in enumerate(archive["mergePlans"]):
        parents = plan["parentIds"]
        if len(parents) != 2 or len(set(parents)) != 2 or not set(parents) <= set(members):
            raise ValueError("Merge parents must be two distinct native archive members")
        pair = frozenset(parents)
        if pair in seen:
            raise ValueError("Duplicate native merge plan")
        seen.add(pair)
        left, right = parents
        left_wins = [key for key in keys if vectors[left][key] > vectors[right][key]]
        right_wins = [key for key in keys if vectors[right][key] > vectors[left][key]]
        if not left_wins or not right_wins or plan["leftStrengths"] != left_wins or plan["rightStrengths"] != right_wins:
            raise ValueError("A native merge plan lacks its recorded complementary evidence")
        if "baseline" in parents:
            skipped.append({"native_plan_index": index, "parents": parents, "reason": "baseline adds no new operation; prior candidate reruns are forbidden"})
            continue
        canonical = sorted(parents, key=order.__getitem__)
        operations = [expected[parent] for parent in canonical]
        if len({row["operation"] for row in operations}) != 2:
            raise ValueError("Only non-conflicting unions of distinct frozen operations are allowed")
        identifier = "-".join(SHORT[parent] for parent in canonical)
        if len(chosen) == 4:
            skipped.append({"native_plan_index": index, "parents": parents, "reason": "four-child budget; retain native plan order"})
            continue
        chosen.append({"candidate": identifier, "native_plan_index": index,
                       "parents": parents, "physical_parent": parents[0],
                       "operations": operations, "left_strengths": left_wins,
                       "right_strengths": right_wins})
    return {"ordering": "native merge-plan order, at most four non-baseline compatible unions",
            "selected_merges": chosen, "skipped_merges": skipped}


def main():
    state = assert_frozen()
    config_path = WORK / "search-generation-000.yaml"
    config = read(config_path)
    authorize_phase(state, config, "development")
    if state["stages"]["evolve"]["status"] != "running":
        raise ValueError("Generation one requires active development")
    if (WORK / "decisions/final-selection").exists() or (WORK / "search-generation-001.yaml").exists() or (WORK / "pareto/development/generation-001").exists():
        raise ValueError("Preserve a prior final decision or generation-one attempt")
    source = WORK / "pareto/development/generation-000/pareto-archive.json"
    archive = read(source)
    if archive["searchId"] != config["search"]["id"] or archive["searchId"] != "knowledge-retrieval-e5":
        raise ValueError("The source native archive belongs to a different study")
    audit = WORK / "decisions/generation-one-merges"
    audit.mkdir(parents=True, exist_ok=False)
    binding = owner_binding(config_path, source, audit)
    profile_binding = profile_preflight(config_path, source, audit, 0)
    paths = {row["id"]: host_path(row["skill"]) for row in config["candidates"]}
    profiles = {identifier: read(paths[identifier] / "assets/retrieval-profile.json") for identifier in SHORT}
    decision = supported_merges(archive, profiles, read(HERE / "proposal-grid.json"))
    decision.update(schema_version="retrieval-native-merge-realization/1.0", study=WORK.name,
                    source_archive=str(source), archive_sha256=sha(source),
                    generation_seal=archive["generationSeal"],
                    development_profile_digest=archive["developmentProfileDigest"],
                    source_config_sha256=sha(config_path), protocol_sha256=sha(PROTOCOL / "protocol.md"),
                    helper_sha256=sha(Path(__file__)), native_owner_binding=binding,
                    native_profile_preflight=profile_binding,
                    private_validation_used=False, starts_evaluation=False,
                    final_selection_established=False, promotion_established=False)
    write_json(audit / "merge-decision.json", decision)
    organize("record-evidence", "--evidence-id", "generation-one-merge-decision", "--stage-id", "evolve", "--kind", "decision", "--role", "development", "--path", audit / "merge-decision.json")
    if not decision["selected_merges"]:
        print(json.dumps({"status": "no-supported-new-merge", "generation_one_created": False}))
        return
    records = {row["candidateId"]: row for row in archive["candidateResults"]}
    new_config = copy.deepcopy(config)
    new_config["search"].update(generation=1, previousGenerationLog=wsl_path(source))
    new_config["candidates"] = [copy.deepcopy(next(row for row in config["candidates"] if row["id"] == "baseline"))]
    for item in decision["selected_merges"]:
        parents = item["parents"]
        identifier = item["candidate"]
        parent = paths[item["physical_parent"]]
        parent_digest = call("digest", parent)["treeSha256"]
        evidence = {**item, "source_archive": str(source), "archive_sha256": sha(source),
                    "generation_seal": archive["generationSeal"],
                    "parent_native_digests": {name: records[name]["skillDigest"] for name in parents},
                    "physical_parent": str(parent), "physical_parent_tree_sha256": parent_digest,
                    "merge_decision_sha256": sha(audit / "merge-decision.json"), "private_validation_used": False}
        evidence_path = audit / (identifier + "-contract.json")
        write_json(evidence_path, evidence)
        instruction = ("Realize the exact compatible union in the digest-bound development contract from native archived parents "
                       + " and ".join(parents) + ". Keep every vendored implementation unchanged and preserve authoritative identities. "
                       "Use only the existing frozen operations and exact reviewed helper. This is a new experimental child, not a promotion.")
        package = realize(identifier, item["operations"], instruction, parent, parent_digest, evidence_path)
        new_config["candidates"].append({"id": identifier, "skill": wsl_path(package), "parents": parents, "rationale": instruction})
        organize("record-evidence", "--evidence-id", "realized-" + identifier, "--stage-id", "evolve", "--kind", "candidate", "--role", "lineage", "--path", WORK / "realizations" / (identifier + "-sealed"))
    authorize_phase(assert_frozen(), new_config, "development")
    destination = WORK / "search-generation-001.yaml"
    write_json(destination, new_config)
    final_binding = profile_preflight(destination, source, audit, 1)
    write_json(audit / "realization-receipt.json", {"status": "sealed-and-verified", "children": len(new_config["candidates"]) - 1,
               "new_config_sha256": sha(destination), "source_archive_sha256": sha(source),
               "native_profile_preflight": final_binding,
               "native_jobs_started": 0, "private_validation_used": False})
    organize("record-evidence", "--evidence-id", "generation-one-realization", "--stage-id", "evolve", "--kind", "other", "--role", "lineage", "--path", audit / "realization-receipt.json")
    print(json.dumps({"status": "generation-one-prepared", "children": len(new_config["candidates"]) - 1,
                      "next": "Run the unchanged controller dry-run and doctor before native development"}))


if __name__ == "__main__":
    main()
