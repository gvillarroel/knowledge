"""Create and replay the private authoring plan before any candidate evaluation."""
from __future__ import annotations

import hashlib
import json
import secrets
import subprocess
import sys

from prepare_experiment import REPO, WORK, write_json


def task_id(cohort, family):
    return "retrieval-" + hashlib.sha256((cohort + ":" + family).encode()).hexdigest()[:20]


def main():
    from prepare_datasets import FAMILIES
    groups = {"internal": ["enterprise", "astro", "architecture", "data-science"], "fiqa": ["fiqa"], "scifact": ["scifact"]}
    families = []
    for group, cohorts in groups.items():
        cases = [{"taskId": task_id(cohort, family), "responseMode": "structured", "variantAxes": {
            "output-name": ["retrieval.json", "ranked-records.json", "search-results.json"],
            "output-root": ["/workspace", "/workspace/results", "/workspace/artifacts/final"],
        }} for cohort in cohorts for family in FAMILIES]
        families.append({"familyId": group + "-annotation-family", "sourceId": group + "-sources", "templateId": group + "-annotation-protocol",
                         "strata": {"capability": "evidence-retrieval", "domain": group, "difficulty": "mixed", "resourceClass": "cpu-two-threads"}, "cases": cases})
    coverage = {}
    for split, domains, count in [("development", {"internal": 1}, 32), ("validation", {"fiqa": 1, "scifact": 1}, 16)]:
        coverage[split] = {"minimumFamilies": len(domains), "minimumTasks": count, "responseModes": {"structured": count},
                           "strata": {"capability": {"evidence-retrieval": len(domains)}, "domain": domains,
                                      "difficulty": {"mixed": len(domains)}, "resourceClass": {"cpu-two-threads": len(domains)}}}
    blueprint = {"schemaVersion": 1, "datasetId": "knowledge-retrieval-transfer-v1", "splitWeights": {"development": 2, "validation": 1},
                 "coverageRequirements": coverage, "families": families}
    root = WORK / "curator/authoring"
    root.mkdir(parents=True, exist_ok=False)
    write_json(root / "blueprint.json", blueprint)
    write_json(root / "seeds.json", {"schemaVersion": 1, "partitionSeed": secrets.token_hex(32), "variantSeeds": {split: secrets.token_hex(32) for split in coverage}})
    planner = REPO / "skills/harbor-author-evaluation-datasets/scripts/plan_harbor_task_datasets.py"
    for command in ("plan", "verify"):
        argv = [sys.executable, "-B", str(planner), command, "--blueprint", str(root / "blueprint.json"), "--seeds", str(root / "seeds.json"), "--output" if command == "plan" else "--plan-dir", str(root / "plan")]
        result = subprocess.run(argv, capture_output=True, text=True, check=False)
        (root / (command + ".log")).write_text(result.stdout + result.stderr, encoding="utf-8")
        if result.returncode:
            raise ValueError("Private authoring plan failed; inspect curator log")
    plan = json.loads((root / "plan/plan.private.json").read_text(encoding="utf-8"))
    for row in plan["tasks"]:
        expected = "development" if row["strata"]["domain"] == "internal" else "validation"
        if row["split"] != expected:
            raise ValueError("Historical exposure partition mismatch; do not search seeds")
    print(json.dumps({"stage": "authoring-plan", "status": "replayed", "development_tasks": 32, "validation_tasks": 16}))


if __name__ == "__main__":
    main()
