"""Preserve a wholly unscored infrastructure-aborted campaign without retrying it."""
from __future__ import annotations

import json
from datetime import datetime, timezone

from prepare_experiment import WORK, sha, write_json
from prepare_study import organize
from run_search import verified_state


def main():
    state = verified_state()
    if state["validationRelease"] is not None or state["holdoutRelease"] is not None:
        raise ValueError("This preparation correction cannot follow a private release")
    root = WORK / "pareto/development/generation-000/harbor-jobs"
    jobs = list(root.iterdir())
    if len(jobs) != 1 or not jobs[0].name.endswith("-baseline"):
        raise ValueError("Expected only the initial baseline job")
    results = list(jobs[0].glob("*/result.json"))
    if len(results) != 2:
        raise ValueError("Unexpected failure envelope")
    for path in results:
        value = json.loads(path.read_text())
        if value["agent_result"] is None or value["verifier_result"] is not None or value.get("verifier") is not None:
            raise ValueError("Expected completed agents before any verifier")
        error = value["exception_info"]
        if error["exception_type"] != "OSError" or "[Errno 5]" not in error["exception_message"] or "_record_mounted_artifacts_dir" not in error["exception_traceback"]:
            raise ValueError("Unexpected infrastructure exception")
    target = WORK / "infrastructure-stop.json"
    if target.exists():
        raise ValueError("Preserve the original stop receipt")
    files = [jobs[0] / "config.json", jobs[0] / "lock.json", jobs[0] / "result.json", WORK / "logs/search-generation-000-development.log", *results]
    write_json(target, {"schema_version": "unscored-infrastructure-stop/1.0", "recorded_at": datetime.now(timezone.utc).isoformat(),
                       "study": WORK.name, "status": "aborted-before-fitness", "completed_agents": 2, "verifier_runs": 0, "valid_scores": 0,
                       "native_root_incomplete": True, "validation_released": False,
                       "source_files": {str(path.relative_to(WORK)): sha(path) for path in files},
                       "failure": "Harbor 0.18.0 errno-5 during mounted artifact directory stat on DrvFS; no verifier started",
                       "recovery_contract": "Inapplicable: this deterministic incomplete root has no Pi trace or sealed selective-retry journal. Do not derive or forge an effective job.",
                       "next_step": "Preserve this campaign; independently test shorter native artifact paths and use a newly reviewed infrastructure campaign under the frozen protocol's correction rule. The same validation remains unconsumed."})
    organize("record-evidence", "--evidence-id", "unscored-infrastructure-stop", "--stage-id", "evolve", "--kind", "other", "--role", "lineage", "--path", target)
    for stage in ("evolve", "validate", "publish"):
        organize("transition", "--stage-id", stage, "--status", "stopped", "--note", "Unscored infrastructure abort; preserve original evidence and unused validation; no retry or promotion.")
    print(json.dumps({"status": "preserved-and-stopped", "completed_agents": 2, "valid_scores": 0, "private_gate_consumed": False}))


if __name__ == "__main__":
    main()
