"""Trusted Linux bridge to the installed native Harbor owner and reporter.

This module never proposes candidates or reads private task payloads. Live
operations require a broker-written request with exactly one new native ID.
The owner authenticates locks, provenance, qualification and Pareto membership.
"""
from __future__ import annotations

import argparse
import copy
import subprocess
import sys
from pathlib import Path

from .files import host, inventory, load, read, sha, write
from .executor_policy import install
from .planner import ProtocolError, exact


def run(request: dict) -> dict:
    """Execute one finite native operation; never retry an allocated job."""
    exact(request, {"operation", "owner", "owner_sha256", "config", "candidate_id", "output",
                    "task_families", "reporter", "reporter_sha256", "runtime_contract", "runtime_contract_sha256"}, "native worker request")
    contract_path = host(request["runtime_contract"])
    if sha(contract_path) != request["runtime_contract_sha256"]:
        raise ProtocolError("Native runtime contract changed")
    install(read(contract_path))
    owner_path = host(request["owner"])
    if sha(owner_path) != request["owner_sha256"]:
        raise ProtocolError("Native owner source drift")
    owner = load("enterprise_e16_native_owner", owner_path)
    config_path, output = host(request["config"]), host(request["output"])
    raw, config = read(config_path), owner.normalize_config(config_path)
    operation = request["operation"]
    if operation in ("development", "recalculation"):
        new_id = request["candidate_id"]
        candidates = {row["id"]: row for row in raw["candidates"]}
        if new_id not in candidates or "jobDirectory" in candidates[new_id]:
            raise ProtocolError("New native identity is missing or already consumed")
        template = owner.load_job_template(config["developmentJob"])
        job = template.model_dump(mode="json")
        expected_count = len(request["task_families"])
        if (job["n_attempts"] != 1 or job["retry"]["max_retries"] != 0
                or job["n_concurrent_trials"] != (1 if expected_count == 1 else 2)
                or len(job["tasks"]) != expected_count or len(job["agents"]) != 1 or job.get("datasets")):
            raise ProtocolError("Native trial allocation differs from the fixed resource contract")
        records = owner.run_candidate_jobs(config, phase="development", analyze_only=False, candidate_ids=[new_id])
        if len(records) != 1 or records[0]["candidateId"] != new_id:
            raise ProtocolError("Native owner changed the requested identity")
        record = records[0]
        # Preserve original failures before attempting archive construction.
        write(output / "record.json", record)
        analyzed = copy.deepcopy(raw)
        candidate = next(c for c in analyzed["candidates"] if c["id"] == new_id)
        candidate.update(skill=record["evaluatedSkill"], jobDirectory=record["jobDirectory"])
        analyzed["search"]["baselineSkill"] = next(c["skill"] for c in analyzed["candidates"] if c["id"] == analyzed["search"]["baselineCandidate"])
        write(output / "analyzed.json", analyzed)
        if operation == "recalculation":
            if (not record["qualification"]["passed"] or not record["evaluable"]
                    or not record["promotionEligibleProvenance"] or record["exploratory"]
                    or record["summary"]["errorCount"] != 0
                    or record["summary"]["expectedTrials"] != 8 or record["summary"]["completedTrials"] != 8
                    or len(record["cases"]) != 8):
                raise ProtocolError("Original all-500 arm is incomplete or unqualified; no second allocation")
            return {"record": str(output / "record.json"), "record_sha256": sha(output / "record.json"),
                    "config": str(output / "analyzed.json")}
        result = owner.development(owner.normalize_config(output / "analyzed.json"), analyze_only=True)
        archive_path = host(result["archive"])
        archive = read(archive_path)
        owner.validate_archive_seal(archive, "native-development")
        if archive["holdoutDataUsed"] or not archive["promotionEligibleProfile"]:
            raise ProtocolError("Native archive did not retain its declared public profile")
        authentic = next(row for row in archive["candidateResults"] if row["candidateId"] == new_id)
        if authentic["skillDigest"] != record["skillDigest"] or authentic["jobDirectory"] != record["jobDirectory"]:
            raise ProtocolError("Native archive differs from the original allocated job")
        family_scores = {}
        mapping = request["task_families"]
        for row in authentic["cases"]:
            if row["taskName"] not in mapping or mapping[row["taskName"]] in family_scores:
                raise ProtocolError("Unexpected or repeated native case")
            family_scores[mapping[row["taskName"]]] = row["meanReward"]
        return {"candidate_id": new_id, "skill_digest": inventory(host(record["evaluatedSkill"]))[0],
                "evaluable": authentic["evaluable"], "qualified": authentic["qualification"]["passed"],
                "promotion_eligible": authentic["promotionEligibleProvenance"], "exploratory": authentic["exploratory"],
                "expected_trials": authentic["summary"]["expectedTrials"],
                "completed_trials": authentic["summary"]["completedTrials"], "error_count": authentic["summary"]["errorCount"],
                "case_scores": family_scores, "native_record_sha256": sha(output / "record.json"),
                "archive_sha256": sha(archive_path),
                "archive_member": any(row["candidateId"] == new_id for row in archive["archive"])}
    if operation == "verify-selection":
        archive = read(config["developmentArchive"])
        owner.validate_development_archive_binding(config, archive)
        return {"verified": True, "archive_sha256": sha(config["developmentArchive"])}
    if operation == "compare":
        records = owner.run_candidate_jobs(config, phase="development", analyze_only=True,
                                          candidate_ids=[c["id"] for c in config["candidates"]])
        owner.validate_comparable(records)
        if len(records) != 2 or any(not r["qualification"]["passed"] or not r["evaluable"]
                                   or not r["promotionEligibleProvenance"] or r["summary"]["errorCount"]
                                   or r["summary"]["completedTrials"] != 8 for r in records):
            raise ProtocolError("Incomplete or unqualified all-500 comparison")
        reporter = host(request["reporter"])
        if sha(reporter) != request["reporter_sha256"]:
            raise ProtocolError("Native reporter changed")
        with (output / "reporter.log").open("xb") as stream:
            subprocess.run([sys.executable, "-B", str(reporter), *[r["jobDirectory"] for r in records],
                            "--compare", "--pass-threshold", "0.8", "--output-dir", str(output / "reports")],
                           stdout=stream, stderr=subprocess.STDOUT, check=True)
        write(output / "comparison.json", {"records": records, "native_comparability_verified": True,
                                           "selection_permitted": False, "question_count": 500,
                                           "retrieval_eligible": 470, "documents": 6000})
        return {"comparison_sha256": sha(output / "comparison.json"), "complete": True}
    raise ProtocolError("Unknown native worker operation")


def main() -> None:
    """Run a broker-authored request and persist its bounded return envelope."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("request", type=Path)
    args = parser.parse_args()
    request = read(args.request)
    result = run(request)
    write(host(request["output"]) / "response.json", result)


if __name__ == "__main__":
    main()
