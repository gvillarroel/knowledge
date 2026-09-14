"""Prepare public, versioned EnterpriseRAG inputs without opening a study."""
from __future__ import annotations

import argparse
import copy
from pathlib import Path
import shutil

from .composition import compose, rebind_task
from .executor_policy import TRIAL_SOURCE_SHA256
from .files import PROFILE, REPO, SKILL_NAME, host, inventory, load, posix, read, sha, write
from .launcher import docker
from .planner import FAMILIES, OPEN_FAMILIES, ProtocolError, digest, validate_plan

HERE = Path(__file__).parent
PREDECESSOR_PLAN = REPO / "tmp/enterprise-next-preparation/e15-runtime-001/execution-plan.json"


def prepare(work: Path, *, curator_source: Path | None = None) -> dict:
    """Create public references and tasks; independent registration stays required."""
    from .authority import safe_path
    work = safe_path(work.absolute(), REPO)
    work.mkdir(parents=True, exist_ok=False)
    prior = read(PREDECESSOR_PLAN)
    source, expected, external, family_rows = {}, {}, {}, {}
    catalog_path = REPO / "evaluations/enterprise-stratified-evolution/profiles.py"
    catalogs = load("enterprise_frozen_catalog_preparation", catalog_path)
    caps = dict(zip(FAMILIES, (55, 55, 100, 40, 85, 65, 80, 105)))
    claims = dict(zip(FAMILIES, (16, 16, 29, 6, 37, 24, 9, 3)))
    for family in FAMILIES:
        if family in OPEN_FAMILIES:
            row = prior["prospective_first_measurements"][family]
            path, checksum = row["candidate"], row["candidate_tree_sha256"]
            identifier, score = row["identity"], None
            external[family] = row["allowed_external_ancestry_drift"]
        else:
            row = prior["terminal_imports"][family]
            path, checksum = row["winner_skill"], row["winner_tree_sha256"]
            identifier, score = row["winner_id"], row["score"]
            if sha(REPO / row["result"]) != row["result_sha256"]:
                raise ProtocolError("Closed development import changed")
            external[family] = []
        source[family], expected[family] = REPO / path, checksum
        if inventory(source[family])[0] != checksum:
            raise ProtocolError("Prospective family source changed")
        profile = read(source[family] / PROFILE)[family]
        family_rows[family] = {"reference_id": identifier, "reference_score": score, "source_tree_sha256": checksum,
                              "profile": profile, "claims": claims[family], "cap": caps[family],
                              "seen_profile_digests": [], "catalog": catalogs.inventory(family) if family in OPEN_FAMILIES else []}
    base = REPO / prior["reference_base"]["path"]
    composition = work / "composition/reference" / SKILL_NAME
    composition_receipt = compose(base, source, composition, expected=expected, external_drift=external)
    write(work / "composition/reference-receipt.json", composition_receipt)
    jobs, task_families, version_receipts = {}, {}, {}
    groups = [*OPEN_FAMILIES, "joint", "recalculation"]
    for group in groups:
        source_job = REPO / (prior["prospective_first_measurements"][group]["source_job"] if group in OPEN_FAMILIES
                            else prior["joint_jobs"]["development" if group == "joint" else "recalculation"]["source"])
        job = read(source_job)
        tasks, mapping = [], {}
        for entry in job["tasks"]:
            original = host(entry["path"])
            family = read(original / "tests/contract.json")["family"]
            bound_skill = source[family] if group in OPEN_FAMILIES else composition
            suffix = digest({"study": "enterprise-e16", "group": group, "family": family,
                             "source": inventory(original)[0], "skill": inventory(bound_skill)[0]})[:20]
            task = work / "public/tasks" / ("retrieval-" + suffix)
            receipt = rebind_task(original, task, bound_skill)
            version_receipts[group + ":" + family] = receipt
            tasks.append({"path": posix(task)})
            mapping[task.name] = family
        job["tasks"] = tasks
        job["job_name"] = "enterprise-e16-" + group
        job["jobs_dir"] = posix(work / "native-jobs")
        job["agents"][0]["skills"] = [posix(source[group] if group in OPEN_FAMILIES else composition)]
        job_path = work / "public/jobs" / (group + ".json")
        write(job_path, job)
        jobs[group], task_families[group] = posix(job_path), mapping
    write(work / "public/task-versions.json", version_receipts)
    foundation = {"schema": "enterprise-e16-public-foundation/1.0", "predecessor_plan_sha256": sha(PREDECESSOR_PLAN),
                  "terminal_predecessors": {"enterprise-e14": "terminal-incomplete", "enterprise-e15": "terminal-incomplete"},
                  "inheritance_is_evidence_only": True, "catalog_sha256": sha(catalog_path),
                  "tasks": version_receipts, "reference_composition_sha256": composition_receipt["tree_sha256"],
                  "development_questions": 120, "all500_questions": 500, "documents": 6000,
                  "six_closed_catalogs_reopened": False, "mutation_model_calls": 0,
                  "executor_policy": "separate-feedback-readonly-root-private-disk-workspace",
                  "harbor_trial_source_sha256": TRIAL_SOURCE_SHA256,
                  "validation_policy": {"groups_per_family": 2, "families": 8, "arms": 2,
                                        "native_strict_aggregate_gain": True, "family_paired_mean_minimum": 0,
                                        "individual_case_regressions_allowed": True},
                  "public_roles_overlap_within_one_development_registry": True,
                  "all500_information_available_to_optimizer": False}
    write(work / "public/foundation.json", foundation)
    plan = {"schema": "enterprise-isolated-planner/1.0", "study_id": "enterprise-e16", "families": family_rows,
            "authority_sha256": digest(foundation), "policy": {"maximum_rounds": 5, "consecutive_misses": 3,
             "maximum_batch_size": 2, "initial_claims": 140, "cumulative_cap": 585, "strict_gain_epsilon": 1e-12}}
    validate_plan(plan)
    write(work / "plan.json", plan)
    code = work / "optimizer-code"
    code.mkdir()
    for name in ("bootstrap.py", "planner.py", "sandbox_runtime.py"):
        shutil.copyfile(HERE / name, code / name)
    authority = prior["runtime_authority"]
    agent_directory = work / "public/agents"
    agent_directory.mkdir()
    for field in ("development_agent", "recalculation_agent"):
        shutil.copyfile(REPO / authority[field], agent_directory / Path(authority[field]).name)
    fixed_files = [PREDECESSOR_PLAN, catalog_path, work / "plan.json", work / "public/foundation.json",
                   REPO / "tmp/enterprise-next-preparation/e14-terminal-closure-001/terminal-receipt.json",
                   REPO / "tmp/enterprise-next-preparation/e15-terminal-closure-001/terminal-receipt.json"]
    authority_paths = {key: (REPO / authority[key]).absolute() if not Path(authority[key]).is_absolute() else Path(authority[key])
                       for key in ("owner", "organizer", "realizer")}
    reporter = Path("C:/Users/villa/.codex/skills/harbor-run-results/scripts/report_harbor_jobs.py")
    fixed_files += [*authority_paths.values(), reporter,
                    REPO / authority["development_agent"], REPO / authority["recalculation_agent"]]
    fixed_files += list(HERE.glob("*.py"))
    fixed_files += [REPO / row["result"] for row in prior["terminal_imports"].values()]
    trees = [*source.values(), base, composition, work / "public", code, REPO / "tmp/e5/models/hub"]
    import json
    image = json.loads(docker("image", "inspect", "python:3.12-slim"))[0]
    contract = {"schema": "enterprise-e16-runtime/1.0", "plan_sha256": digest(plan),
                **{key: posix(path) for key, path in authority_paths.items()},
                "owner_sha256": sha(authority_paths["owner"]), "reporter": posix(reporter), "reporter_sha256": sha(reporter),
                "source_files": {posix(p): sha(p) for p in fixed_files}, "source_trees": {posix(p): inventory(p)[0] for p in trees},
                "sources": {f: posix(p) for f, p in source.items()}, "reference_base": posix(base),
                "reference_composition": posix(composition), "external_drift": external,
                "jobs": jobs, "task_families": task_families,
                "harbor_python": "/home/villa/.local/share/uv/tools/harbor/bin/python",
                "agent_directory": posix(agent_directory),
                "executor_policy": posix(HERE / "executor_policy.py"),
                "harbor_trial_source_sha256": TRIAL_SOURCE_SHA256,
                "validation_job": posix(work / "curator/validation-job.json"),
                "curator_authority": posix(work / "curator/authority.py"),
                "optimizer_image": image["Id"], "optimizer_code": posix(code), "optimizer_code_sha256": inventory(code)[0],
                "registration_grants_execution": False, "independent_seal_required": True}
    if curator_source is not None:
        contract["source_files"][contract["curator_authority"]] = sha(curator_source)
        contract["curator_public_source_sha256"] = sha(curator_source)
    write(work / "runtime-contract.json", contract)
    receipt = {"status": "public-prepared-not-registered", "work": str(work), "task_count": sum(len(v) for v in task_families.values()),
               "plan_sha256": digest(plan), "runtime_contract_sha256": sha(work / "runtime-contract.json"),
               "native_calls": 0, "private_data_created": False}
    write(work / "public-preparation.json", receipt)
    return receipt


def main() -> None:
    """Create an append-only public preparation root; do not seal or execute."""
    import json
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("work", type=Path)
    parser.add_argument("--curator-source", type=Path,
                        help="Independently reviewed self-contained authority; required for a future live seal")
    args = parser.parse_args()
    print(json.dumps(prepare(args.work, curator_source=args.curator_source), sort_keys=True))


if __name__ == "__main__":
    main()
