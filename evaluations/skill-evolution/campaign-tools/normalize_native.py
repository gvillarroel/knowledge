"""Run the installed reporter on completed native evidence; keep details ignored."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
sys.path.insert(0, str(REPO / "evaluations/skill-evolution"))
from prepare_experiment import wsl_path
from run_search import HARBOR_PYTHON, verified_state

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("phase", choices=["development", "validation"])
parser.add_argument("--generation", type=int, choices=[0, 1], default=0)
args = parser.parse_args()
state = verified_state()
if args.phase == "development":
    source = ROOT / f"pareto/development/generation-{args.generation:03d}/pareto-archive.json"
    archive = json.loads(source.read_text(encoding="utf-8"))
    if archive["holdoutDataUsed"] is not False:
        raise ValueError("Development reporting requires development-only evidence")
    jobs = [row["jobDirectory"] for row in archive["candidateResults"]]
    label = f"development-generation-{args.generation:03d}"
else:
    if state["validationRelease"] is None or state["stages"]["evolve"]["status"] != "completed":
        raise ValueError("The terminal gate must have been released after completed evolution")
    source = ROOT / "pareto/holdout/promotion.json"
    promotion = json.loads(source.read_text(encoding="utf-8"))
    jobs = [promotion["jobs"][role] for role in ("baseline", "candidate")]
    label = "terminal-validation"
output = ROOT / "native-reports" / label
log = ROOT / "logs" / (label + "-native-reporter.log")
if output.exists() or log.exists():
    raise ValueError("Native report output already exists; preserve the first projection")
command = ["wsl", "-d", "Ubuntu", "--exec", "env", "PYTHONDONTWRITEBYTECODE=1",
           "TMPDIR=" + wsl_path(ROOT / "host-cache/tmp"), HARBOR_PYTHON, "-B",
           "/mnt/c/Users/villa/.codex/skills/harbor-run-results/scripts/report_harbor_jobs.py",
           *jobs, "--compare", "--reward-key", "reward", "--pass-threshold", "0.8",
           "--output-dir", wsl_path(output), "--title", "Native retrieval profile " + label]
with log.open("xb") as stream:
    completed = subprocess.run(command, stdout=stream, stderr=subprocess.STDOUT)
if completed.returncode:
    raise ValueError("Native reporter failed; preserve and inspect the private log")
print(json.dumps({"status": "native-reporter-completed", "jobs": len(jobs), "output": str(output / "final-report.json")}))
