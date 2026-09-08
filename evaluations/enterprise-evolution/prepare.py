"""Prepare a fresh prospective sweep without modifying any previous study."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from profiles import FAMILIES, CONSTRUCTION, baseline_profile, inventory

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
WORK = REPO / "tmp/e6"
OLD = REPO / "tmp/e5"
NAME = "build-semantic-okf-knowledge-skill"
ORGANIZER = REPO.parent / "skill-arena/skills/harbor-organize-evaluations/scripts/manage_harbor_evaluations.py"
OWNER = Path("C:/Users/villa/.codex/skills/harbor-reflective-pareto-search/scripts/harbor_reflective_pareto.py") if os.name == "nt" else Path("/mnt/c/Users/villa/.codex/skills/harbor-reflective-pareto-search/scripts/harbor_reflective_pareto.py")
HPY = "/home/villa/.local/share/uv/tools/harbor/bin/python"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tree(root):
    result = {}
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise ValueError("Linked artifact")
        if path.is_file():
            result[path.relative_to(root).as_posix()] = sha(path)
    return result


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n")


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def posix(path):
    path = path.resolve()
    return "/mnt/" + path.drive[0].lower() + "/" + path.as_posix().split(":/", 1)[1] if os.name == "nt" else str(path)


def command(argv, log):
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("xb") as stream:
        result = subprocess.run(argv, stdout=stream, stderr=subprocess.STDOUT, check=False)
    if result.returncode:
        raise RuntimeError(f"Command failed; inspect {log}")


def linux(argv):
    result = subprocess.run((["wsl", "-d", "Ubuntu", "--exec"] if os.name == "nt" else []) + argv, capture_output=True, check=False)
    if result.returncode:
        raise RuntimeError(result.stderr.decode(errors="replace")[-2000:])
    return result.stdout.decode().strip()


def organize(action, *args):
    logs = WORK / "logs/organizer"
    number = len(list(logs.glob("*.log"))) if logs.exists() else 0
    command([sys.executable, "-B", str(ORGANIZER), action, str(WORK / "study"), *map(str, args)], logs / f"{number:03d}-{action}.log")


def make_bridge():
    """Keep the proven build/verifier interface; add explicit consultation hooks."""
    original = (REPO / "evaluations/skill-evolution/bridge.py").read_text(encoding="utf-8")
    original = original.replace('    scripts = skill / "assets/families" / family / "consultant/scripts"', '''    scripts = skill / "assets/families" / family / "consultant/scripts"
    profile = json.loads((skill / "assets/retrieval-profile.json").read_text())
    settings = profile[family]["search"]
    extension = load("closed_search_profile", skill / "scripts/apply_retrieval_profile.py")''')
    original = original.replace('        return {"lexical": lambda q: index.search(q, 10)}', '''        if settings:
            _, records = evaluator.ledger(bundle)
            index = extension.LexicalIndex(list(records.values()), settings)
        return {"lexical": lambda q: index.search(q, 10)}''')
    original = original.replace('        return {"lexical-sql": lambda q: evaluator.turso_search(connection, q, 10)}', '''        if settings:
            records = [json.loads(row[0]) for row in connection.execute("SELECT record_json FROM records ORDER BY record_id").fetchall()]
            index = extension.LexicalIndex(records, settings)
            return {"lexical-sql": lambda q: index.search(q, 10)}
        return {"lexical-sql": lambda q: evaluator.turso_search(connection, q, 10)}''')
    original = original.replace('        return {"search": lambda q: evaluator.payload_results(snapshot.search(q, depth=2, top_k=10))}', '''        if settings.get("lexical_weight", 0) > 0:
            index = extension.LexicalIndex(list(snapshot.records_by_path.values()), settings)
            def hybrid(q):
                graph = evaluator.payload_results(snapshot.search(q, depth=settings.get("depth", 2), top_k=100))
                return extension.fuse(graph, index.search(q, 100), settings)
            return {"search": hybrid}
        return {"search": lambda q: evaluator.payload_results(snapshot.search(q, depth=settings.get("depth", 2), top_k=10))}''')
    return original


def prepare():
    WORK.mkdir(parents=True, exist_ok=False)
    baseline = WORK / "baseline" / NAME
    shutil.copytree(OLD / "baseline" / NAME, baseline)
    shutil.copyfile(HERE / "profiles.py", baseline / "scripts/apply_retrieval_profile.py")
    write(baseline / "assets/retrieval-profile.json", baseline_profile())
    (baseline / "references/retrieval-profile.md").write_text("""# Explicit retrieval profile

Read `assets/retrieval-profile.json` for this package's exact family settings.
For plan-based families run `scripts/apply_retrieval_profile.py --family FAMILY
--input PLAN.json --output PROFILED.json` and supply that plan to the normal
builder. Preserve every matched validator and the authoritative record ledger.

The `search` settings are a separate consultation treatment: Legacy uses
record-level BM25; Turso hydrates original records through read-only SQL before
BM25 ranking; Graphify optionally fuses native graph discovery with lexical
record discovery. The helper exports `LexicalIndex` and `fuse`. Empty settings
retain the original route. Graph traversal uses the declared depth. These
settings do not modify generated evidence or its authority.

Learned embeddings require the pinned, locally available MiniLM revision;
do not download a different model or fall back silently. Profiles are
experimental until their declared scope has passed independent validation.
""", encoding="utf-8")
    skill = baseline / "SKILL.md"
    skill.write_text(skill.read_text(encoding="utf-8") + "\nRead [the explicit retrieval profile](references/retrieval-profile.md) before building or consulting with this experimental package.\n", encoding="utf-8")
    frozen = WORK / "runtime"
    frozen.mkdir()
    (frozen / "bridge.py").write_text(make_bridge(), encoding="utf-8", newline="\n")
    agent = (REPO / "evaluations/skill-evolution/native_agent.py").read_text().replace('return "skill-retrieval"', 'return "enterprise-sweep-retrieval"').replace('return "1.0.0"', 'return "2.0.0"')
    (WORK / "enterprise_agent.py").write_text(agent, encoding="utf-8")
    metadata = {}
    for cohort, split in (("enterprise", "development"), ("fiqa", "validation"), ("scifact", "validation")):
        rows = read(OLD / f"curator/{split}/{cohort}-tasks.json")
        context = WORK / "image-contexts" / cohort
        context.mkdir(parents=True)
        shutil.copyfile(frozen / "bridge.py", context / "bridge.py")
        tags = json.loads(linux(["docker", "image", "inspect", rows[0]["image"], "--format", "{{json .RepoTags}} "]))
        if not tags or linux(["docker", "image", "inspect", tags[0], "--format", "{{.Id}} "]) != rows[0]["image"]:
            raise ValueError("Pinned source image has no matching local tag")
        (context / "Dockerfile").write_text(f"FROM {tags[0]}\nCOPY bridge.py /opt/knowledge/evolution/runtime/bridge.py\n", encoding="utf-8", newline="\n")
        tag = "knowledge-enterprise-sweep:e6-" + cohort
        log = WORK / f"logs/image-{cohort}.log"
        command((["wsl", "-d", "Ubuntu", "--exec"] if os.name == "nt" else []) + ["docker", "build", "--pull=false", "--network=none", "-t", tag, posix(context)], log)
        image = linux(["docker", "image", "inspect", tag, "--format", "{{.Id}}"])
        if linux(["docker", "image", "inspect", tags[0], "--format", "{{.Id}} "]) != rows[0]["image"]:
            raise ValueError("Source image changed during the build")
        for row in rows:
            source = OLD / "tasks" / row["dataset_id"] / row["task_id"]
            target = WORK / "tasks" / split / row["task_id"]
            shutil.copytree(source, target)
            task = target / "task.toml"
            task.write_text(task.read_text().replace(row["image"], image), encoding="utf-8", newline="\n")
            contract_path = target / "tests/contract.json"
            contract = read(contract_path)
            contract["skill_files"] = tree(baseline)
            # Only the profile asset changes; helper, prose, builder and consultant
            # code all remain fixed for this campaign.
            contract["mutable_skill_paths"] = ["assets/retrieval-profile.json"]
            contract_path.write_text(json.dumps(contract, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
            metadata[cohort + ":" + row["family"]] = {"task": posix(target), "image": image}
    write(WORK / "task-map.json", metadata)
    protocol = {
        "schema_version": "enterprise-sweep/1.0", "id": "enterprise-e6", "controller": "harbor-reflective-pareto-search",
        "families": list(FAMILIES), "strategies": {f: inventory(f) for f in FAMILIES},
        "treatments": {f: "construction" if f in CONSTRUCTION else "consultation" for f in FAMILIES},
        "failure_rule": "A unique new evaluable candidate with no strict incumbent nDCG@10 gain greater than 1e-12; semantic integrity failures also count, external failures stop without fitness.",
        "consecutive_failures": 3, "success_resets_failures": True, "duplicate_profiles": "skip without executing or counting a failure",
        "budget": {"baseline_trials": 8, "maximum_new_candidates": sum(len(s["variants"]) for f in FAMILIES for s in inventory(f)), "native_attempts": 1, "native_retries": 0, "family_workers": 2, "llm_calls": 0},
        "selection": "After every family exhausts its catalog or reaches its per-strategy plateau, select the qualified family incumbent with greatest Enterprise primary-route mean, then least changed profile fields, then lexical family ID. Freeze that exact bundle and its family before private release. No cross-family merge.",
        "validation": "The unreleased FiQA and SciFact source portfolio from e5 is reserved for one selected family and one terminal baseline/candidate comparison. Both dataset families must not regress; mean gain must be at least zero and evidence_integrity must be one. No subsequent evolution after opening. Other private family cells remain unexecuted. No additional holdout.",
        "interpretation": "40 previously exposed Enterprise queries / 985 reference-enriched records, one source/annotation independence group. Ranking diagnostics, not official full-corpus answer quality. Three misses mean exhaustion of one declared finite tactic, not proof that no possible algorithm exists.",
        "unchanged_previous_study": "e5 stopped with no private release; its scores are historical development context and are not imported as new trial outcomes.",
        "baseline_selection": "Each family starts from its highest completely measured e5 Enterprise primary-route profile; the new native baseline must reproduce that score within 1e-12 before any child. Historical rows are development context, not new measurements or validated promotions.",
        "baseline_expected_scores": {"legacy": 0.5749695375722894, "embeddings": 0.6319043854152289, "classical": 0.4434644291211766, "adaptive": 0.5068734091416912, "entity-graph": 0.47275963568195856, "ensemble": 0.5566385701162351, "graphify": 0.13626228624863054, "turso": 0.40319114502840775},
        "baseline_historical_evidence_sha256": sha(REPO / "evaluations/reports/evolution/e5/interrupted-development-001/aggregates.json"),
        "baseline_files": tree(baseline), "runtime_files": tree(frozen), "agent_sha256": sha(WORK / "enterprise_agent.py"), "owner_sha256": sha(OWNER),
        "sources": {"profiles.py": sha(HERE / "profiles.py"), "sweep.py": sha(HERE / "sweep.py"), "prepare.py": sha(HERE / "prepare.py")},
        "task_bytes": tree(WORK / "tasks"), "model_inventory_sha256": sha(OLD / "model-inventory.json"),
    }
    write(WORK / "protocol.json", protocol)
    for family in FAMILIES:
        for phase, cohorts in (("development", ["enterprise"]), ("validation", ["fiqa", "scifact"])):
            job = {"job_name": "e6-"+phase+"-"+family, "jobs_dir": posix(WORK / "native-jobs"), "n_attempts": 1, "n_concurrent_trials": 1, "quiet": True, "retry": {"max_retries": 0},
                   "environment": {"type": "docker", "delete": True, "mounts": [{"type": "bind", "source": posix(OLD / "models/hub"), "target": "/models/huggingface/hub", "read_only": True, "bind": {"create_host_path": False}}]},
                   "agents": [{"name": "enterprise-sweep-retrieval", "import_path": "enterprise_agent:SkillRetrievalAgent", "model_name": "local/deterministic-retrieval-v2", "skills": [posix(baseline)]}],
                   "tasks": [{"path": metadata[c+":"+family]["task"]} for c in cohorts]}
            write(WORK / "jobs" / (family+"-"+phase+".json"), job)
    organize("init", "--study-id", "enterprise-e6", "--title", "Enterprise retrieval three-miss evolution sweep", "--objective", protocol["selection"], "--comparison-profile", "enterprise-sweep-v2-offline")
    for split in ("development", "validation"):
        organize("add-dataset", "--dataset-id", split, "--split", split, "--source", WORK / "tasks" / split)
    organize("add-stage", "--stage-id", "evolve", "--kind", "evolution", "--owner-skill", "harbor-reflective-pareto-search", "--dataset-id", "development")
    organize("add-stage", "--stage-id", "validate", "--kind", "validation", "--owner-skill", "harbor-reflective-pareto-search", "--dataset-id", "validation", "--depends-on", "evolve")
    organize("add-stage", "--stage-id", "publish", "--kind", "publication", "--owner-skill", "harbor-organize-evaluations", "--depends-on", "validate")
    print(json.dumps({"status": "prepared-unsealed", "families": 8, "maximum_candidates": protocol["budget"]["maximum_new_candidates"]}), flush=True)


if __name__ == "__main__":
    prepare()
