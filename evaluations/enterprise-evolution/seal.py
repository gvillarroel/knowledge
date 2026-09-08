"""Freeze execution inputs after independent qualification, then seal the study."""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from prepare import HERE, REPO, WORK, OLD, NAME, OWNER, ORGANIZER, read, write, tree, sha, posix, organize


def freeze(review):
    if not (review / "review.json").is_file():
        raise ValueError("Independent curator receipt is required")
    source_files = {p.relative_to(REPO).as_posix(): sha(p) for p in sorted(HERE.glob("*.py"))}
    for relative in ("evaluations/private-book-strategy-comparison/scripts/prepare_strategy_bundles.py", "evaluations/private-book-strategy-comparison/scripts/evaluate_all_routes.py", "evaluations/skill-evolution/bridge.py", "evaluations/skill-evolution/native_agent.py", "evaluations/skill-evolution/verifier.py"):
        source_files[relative] = sha(REPO / relative)
    workspace_files = {"protocol.json": sha(WORK / "protocol.json"), "enterprise_agent.py": sha(WORK / "enterprise_agent.py"), "task-map.json": sha(WORK / "task-map.json")}
    for name in ("jobs", "baseline", "runtime", "tasks"):
        workspace_files.update({name+"/"+relative: value for relative, value in tree(WORK / name).items()})
    realizer = Path("C:/Users/villa/.codex/skills/harbor-realize-skill-candidate/scripts/realize_skill_candidate.py")
    external_files = {posix(path): sha(path) for path in (OWNER, ORGANIZER, realizer)}
    model = read(OLD / "model-inventory.json")
    model_root = OLD / "models/hub" / ("models--"+model["model_id"].replace("/", "--")) / "snapshots" / model["revision"]
    if tree(model_root) != model["files"]:
        raise ValueError("Pinned model snapshot changed")
    external_files.update({posix(model_root / relative): value for relative, value in model["files"].items()})
    write(WORK / "execution-contract.json", {"schema_version": "enterprise-execution-contract/1.0", "windows_python": posix(Path(sys.executable)), "source_files": source_files, "workspace_files": workspace_files, "external_read_only_files": external_files,
        "authoring_continuity": {"original_blueprint_sha256": sha(OLD / "curator/authoring/blueprint.json"), "original_plan_sha256": sha(OLD / "curator/authoring/plan/plan.private.json"), "original_model_inventory_sha256": sha(OLD / "model-inventory.json"), "method": "Exact Enterprise task subset and both unconsumed source-separated validation cohorts; retain original task-keyed nuisance surfaces. Independent second-root replay and verifier audit bound in curator receipt."},
        "private_curator_review": tree(review), "previous_study_terminal_decision_sha256": sha(REPO / "evaluations/reports/evolution/e5/closure/decision.json")})
    organize("seal-design", "--protocol", WORK / "execution-contract.json", "--baseline", WORK / "baseline" / NAME, "--review", review)
    organize("verify")
    organize("transition", "--stage-id", "evolve", "--status", "running")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--review", type=Path, required=True)
    args = parser.parse_args()
    freeze(args.review.resolve())
