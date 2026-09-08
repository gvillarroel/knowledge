"""Register complete, immutable native generations without selecting or scoring."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
sys.path.insert(0, str(REPO / "evaluations/skill-evolution"))
from aggregate_development import host_path, read
from prepare_experiment import sha, write_json
from prepare_study import organize
from run_search import assert_frozen


def completed_job(path, record):
    """Keep errors in evidence; completion alone is not candidate qualification."""
    result = read(path / "result.json")
    summary = record["summary"]
    trials = [read(item) for item in path.glob("*/result.json")]
    if (not result["finished_at"] or result["n_total_trials"] != 32
            or result["stats"]["n_completed_trials"] != 32
            or summary["expectedTrials"] != 32 or summary["completedTrials"] != 32
            or len(trials) != 32 or len({row["task_name"] for row in trials}) != 32):
        raise ValueError("The exact 32 native trials must finish before registration")
    return {"candidate": record["candidateId"], "job_result_sha256": sha(path / "result.json"),
            "native_errors": result["stats"]["n_errored_trials"], "completed_trials": 32}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--generation", type=int, choices=(0, 1), required=True)
    args = parser.parse_args()
    state = assert_frozen()
    if state["stages"]["evolve"]["status"] != "running" or state["validationRelease"] is not None:
        raise ValueError("Native development registration requires active evolution")
    word = ("zero", "one")[args.generation]
    label = f"generation-{args.generation:03d}"
    source = ROOT / "pareto/development" / label / "pareto-archive.json"
    archive = read(source)
    if (archive["searchId"] != "knowledge-retrieval-e5" or archive["generation"] != args.generation
            or archive["holdoutDataUsed"] is not False or archive["source"] != "harbor"):
        raise ValueError("Expected this study's actual native development archive")
    native = ROOT / "native-reports" / ("development-" + label) / "final-report.json"
    public = REPO / "evaluations/reports/evolution/e5" / label
    aggregate = read(public / "aggregates.json")
    if aggregate["archive_sha256"] != sha(source) or aggregate["native_report_sha256"] != sha(native):
        raise ValueError("The reviewed report must bind the exact native sources")
    records, checks = [], []
    for candidate in archive["candidateResults"]:
        path = host_path(candidate["jobDirectory"])
        checks.append(completed_job(path, candidate))
        records.append((f"generation-{word}-{candidate['candidateId']}-native-job", "native-job", "development", "private", path))
    records.extend([
        (f"generation-{word}-native-archive", "evolution-report", "development", "private", source),
        (f"generation-{word}-native-report", "final-report", "development", "private", native),
        (f"generation-{word}-public-report", "final-report", "report", "public", public),
    ])
    destination = ROOT / "diagnostics" / (label + "-registration.json")
    if destination.exists():
        raise ValueError("Preserve the prior registration receipt")
    added, previous = [], []
    for identifier, kind, role, visibility, path in records:
        if identifier in state["evidence"]:
            existing = state["evidence"][identifier]
            if (Path(existing["source"]).resolve() != path.resolve() or existing["kind"] != kind
                    or existing["role"] != role or existing["stageId"] != "evolve"
                    or existing["visibility"] != visibility):
                raise ValueError("An existing evidence ID has a different binding")
            previous.append(identifier)
        else:
            organize("record-evidence", "--evidence-id", identifier, "--stage-id", "evolve",
                     "--kind", kind, "--role", role, "--visibility", visibility, "--path", path)
            added.append(identifier)
    checked = assert_frozen()
    if any(identifier not in checked["evidence"] for identifier, *_ in records):
        raise ValueError("Evidence registration did not persist")
    write_json(destination, {"status": "registered", "generation": args.generation, "jobs": checks,
               "added_evidence": added, "previously_verified_evidence": previous,
               "archive_sha256": sha(source), "native_report_sha256": sha(native),
               "script_sha256": sha(Path(__file__)), "native_jobs_started": 0,
               "private_validation_released": False, "selection_established": False})
    print(json.dumps({"status": "registered", "generation": args.generation,
                      "added": len(added), "previously_verified": len(previous),
                      "native_trials": 32 * len(checks), "receipt_sha256": sha(destination)}))


if __name__ == "__main__":
    main()
