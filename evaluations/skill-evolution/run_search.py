"""Invoke the owning native Pareto controller with a frozen profile and local caches."""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import subprocess
from pathlib import Path

from prepare_experiment import HERE, PROTOCOL, TASKS, WORK, linux, sha, tree, write_json, wsl_path
from prepare_study import ORGANIZER, STUDY, organize


CONTROLLER = Path("C:/Users/villa/.codex/skills/harbor-reflective-pareto-search/scripts/harbor_reflective_pareto.py")
HARBOR_PYTHON = "/home/villa/.local/share/uv/tools/harbor/bin/python"


def verified_state():
    """Delegate ledger, source, seal and publication verification to its owner."""
    spec = importlib.util.spec_from_file_location("retrieval_study_organizer", ORGANIZER)
    owner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(owner)
    state = owner.build_state(STUDY, verify_sources=True)
    owner.verify_publication_policy(STUDY, state)
    return state


def assert_frozen():
    frozen = json.loads((PROTOCOL / "frozen-inputs.json").read_text(encoding="utf-8"))
    for field, path in [("proposal_sha256", HERE / "proposal-grid.json"), ("bridge_sha256", HERE / "bridge.py"), ("native_agent_sha256", HERE / "native_agent.py"),
                        ("profile_template_sha256", HERE / "apply_retrieval_profile.template.py"), ("verifier_sha256", HERE / "verifier.py"), ("model_inventory_sha256", WORK / "model-inventory.json")]:
        if sha(path) != frozen[field]:
            raise ValueError("Frozen controller input drift: " + field)
    if tree(WORK / "baseline/build-semantic-okf-knowledge-skill") != frozen["baseline"]:
        raise ValueError("Baseline package drift")
    for relative, expected in frozen["controller_file_sha256"].items():
        if sha(HERE / relative) != expected:
            raise ValueError("Frozen orchestration drift: " + relative)
    for name, expected in frozen["job_template_sha256"].items():
        if sha(PROTOCOL / name) != expected:
            raise ValueError("Frozen native job template drift: " + name)
    if tree(TASKS) != frozen["dataset_task_bytes"]:
        raise ValueError("Frozen task artifact drift")
    inventory = json.loads((WORK / "model-inventory.json").read_text(encoding="utf-8"))
    snapshot = WORK / "models/hub" / ("models--" + inventory["model_id"].replace("/", "--")) / "snapshots" / inventory["revision"]
    if tree(snapshot) != inventory["files"]:
        raise ValueError("Offline model snapshot drift")
    runtime = frozen["runtime"]
    if linux(["docker", "image", "inspect", runtime["tag"], "--format", "{{.Id}}"] ) != runtime["image"]:
        raise ValueError("Pinned runtime image drift")
    return verified_state()


def authorize_phase(state, config, mode):
    """Check one-way boundaries before writing logs or dispatching any controller."""
    if state["designSeal"] is None:
        raise ValueError("A sealed study design is required")
    if state["stages"]["realize"]["status"] != "completed":
        raise ValueError("Candidate realization must be completed")
    if config["harbor"]["developmentJob"] != wsl_path(PROTOCOL / "development.yaml") or config["harbor"]["holdoutJob"] != wsl_path(PROTOCOL / "validation.yaml"):
        raise ValueError("Only the frozen native job templates are permitted")
    if config["search"]["generation"] not in (0, 1) or len(config["candidates"]) > 5:
        raise ValueError("The frozen generation and candidate budget was exceeded")
    release = state["validationRelease"]
    if mode == "validation":
        if release is None or state["holdoutRelease"] is not None:
            raise ValueError("The organizer must release the selected validation candidate first")
        if state["stages"]["evolve"]["status"] != "completed" or state["stages"]["validate"]["status"] != "planned":
            raise ValueError("Validation is a single terminal dispatch after completed evolution")
        selected = config["search"].get("selectedCandidate")
        matching = [row for row in config["candidates"] if row["id"] == selected]
        if len(matching) != 1 or matching[0]["skill"] != wsl_path(Path(release["source"])):
            raise ValueError("The validation candidate must equal the organizer's digest-bound selection")
    else:
        if release is not None or state["holdoutRelease"] is not None:
            raise ValueError("Evolution and selection are forbidden after a private gate release")
        status = state["stages"]["evolve"]["status"]
        if status not in {"planned", "running"}:
            raise ValueError("Evolution stage is terminal or blocked")
        if config["search"]["generation"] > 0 and status != "running":
            raise ValueError("Later generations require an active evolution stage")


def prepare_generation_zero():
    state = assert_frozen()
    candidates = json.loads((WORK / "generation-zero-candidates.json").read_text(encoding="utf-8"))
    grid = json.loads((HERE / "proposal-grid.json").read_text(encoding="utf-8"))
    order = ["baseline"] + [row["id"] for row in grid["generation_zero"]]
    config = {"schemaVersion": 1, "search": {"id": "knowledge-retrieval-" + WORK.name, "baselineSkill": wsl_path(Path(candidates["baseline"])), "baselineCandidate": "baseline", "outputDir": wsl_path(WORK / "pareto"), "generation": 0},
              "harbor": {"developmentJob": wsl_path(PROTOCOL / "development.yaml"), "holdoutJob": wsl_path(PROTOCOL / "validation.yaml"), "rewardKey": "reward", "passThreshold": .8, "requiredRewards": {"evidence_integrity": 1}, "requiredEnv": []},
              "candidates": [{"id": name, "skill": wsl_path(Path(candidates[name])), "parents": [] if name == "baseline" else ["baseline"], "rationale": "Frozen baseline" if name == "baseline" else next(row["mechanism"] for row in grid["generation_zero"] if row["id"] == name)} for name in order],
              "promotion": {"minimumMeanGain": .01, "allowCaseRegressions": False, "requireNoErrors": True}}
    authorize_phase(state, config, "prepare")
    path = WORK / "search-generation-000.yaml"
    if path.exists():
        raise ValueError("Search configuration already exists")
    write_json(path, config)
    print(json.dumps({"stage": "search-preparation", "generation": 0, "candidates": len(order)}))


def invoke(config, mode):
    state = assert_frozen()
    settings = json.loads(config.read_text(encoding="utf-8"))
    authorize_phase(state, settings, mode)
    cache = WORK / "host-cache"
    for name in ("tmp", "uv", "xdg"):
        (cache / name).mkdir(parents=True, exist_ok=True)
    flags = {"dry-run": ["--dry-run"], "doctor": ["--doctor"], "development": [], "validation": ["--phase", "holdout"], "analyze": ["--analyze-only"]}[mode]
    command = ["env", "PYTHONDONTWRITEBYTECODE=1", "PYTHONPATH=" + wsl_path(HERE), "TMPDIR=" + wsl_path(cache / "tmp"),
               "UV_CACHE_DIR=" + wsl_path(cache / "uv"), "XDG_CACHE_HOME=" + wsl_path(cache / "xdg"), "HF_HUB_OFFLINE=1", "TRANSFORMERS_OFFLINE=1",
               HARBOR_PYTHON, "-B", wsl_path(CONTROLLER), wsl_path(config), *flags]
    argv = ["wsl", "-d", "Ubuntu", "--exec", *command] if os.name == "nt" else command
    log = WORK / "logs" / (config.stem + "-" + mode + ".log")
    if log.exists():
        raise ValueError("Execution log already exists; preserve prior attempts")
    if mode == "development" and state["stages"]["evolve"]["status"] == "planned":
        organize("transition", "--stage-id", "evolve", "--status", "running")
    if mode == "validation":
        organize("transition", "--stage-id", "validate", "--status", "running")
    with log.open("xb") as stream:
        result = subprocess.run(argv, stdout=stream, stderr=subprocess.STDOUT, check=False)
    if result.returncode:
        raise ValueError(f"Native controller {mode} failed; preserve and inspect {log.name}")
    print(json.dumps({"stage": "native-pareto", "mode": mode, "status": "completed"}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["prepare", "dry-run", "doctor", "development", "validation", "analyze"])
    parser.add_argument("--config", type=Path, default=WORK / "search-generation-000.yaml")
    args = parser.parse_args()
    if args.mode == "prepare":
        prepare_generation_zero()
    else:
        invoke(args.config, args.mode)
