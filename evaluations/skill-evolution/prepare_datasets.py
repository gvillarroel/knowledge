"""Curator-side materialization of native task roots; emits aggregate status only.

Private queries, reference labels, source inventories, and task metadata stay
under generated/. No model or candidate is executed by this authoring adapter.
The unchanged canonical core builder is used only to derive oracle identities.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import io
import json
import os
import re
import secrets
import shutil
import subprocess
import sys
import urllib.request
import zipfile
from pathlib import Path

from prepare_experiment import HERE, REPO, WORK, TASKS, copy_manifest_inputs, linux, sha, tree, write_json, wsl_path

FAMILIES = ("legacy", "embeddings", "classical", "adaptive", "entity-graph", "ensemble", "graphify", "turso")
MODES = {"legacy": ["lexical"], "embeddings": ["lexical", "vector", "hybrid"], "classical": ["bm25", "topic", "association", "fusion"], "adaptive": ["adaptive"], "entity-graph": ["lexical", "entity", "traversal", "fusion"], "ensemble": ["fast", "quality", "robust"], "graphify": ["search"], "turso": ["lexical-sql"]}
PRIMARY = {"legacy": "lexical", "embeddings": "hybrid", "classical": "fusion", "adaptive": "adaptive", "entity-graph": "fusion", "ensemble": "quality", "graphify": "search", "turso": "lexical-sql"}


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def internal_inputs(selected=None):
    declarations = {
        "astro": (REPO / "evaluations/semantic-okf-astro/corpus/manifest.json", REPO / "evaluations/semantic-okf-astro/benchmark/retrieval-questions.jsonl"),
        "architecture": (REPO / "evaluations/software-architecture-books/manifest.json", REPO / "evaluations/software-architecture-books/benchmark/retrieval-questions.jsonl"),
        "data-science": (REPO / "evaluations/data-science-ai-ml-books/manifest.json", REPO / "evaluations/data-science-ai-ml-books/benchmark/retrieval-questions.jsonl"),
    }
    for name, (manifest, question_file) in declarations.items():
        if selected is not None and selected != name:
            continue
        target = WORK / "development-inputs" / name
        copy_manifest_inputs(manifest, target / "input")
        rows = read_jsonl(question_file)
        normalized = []
        for row in rows:
            qrels = row["qrels"]
            relevant = next((qrels[key] for key in ("record_ids", "document_ids", "source_ids", "paper_ids") if key in qrels and qrels[key]), None)
            if not relevant:
                raise ValueError("Missing development reference labels")
            normalized.append({"id": row["id"], "question": row["question"], "relevant": sorted(set(relevant))})
        write_json(target / "queries.json", [{"id": row["id"], "question": row["question"]} for row in normalized])
        write_json(WORK / f"curator/development/{name}-qrels.json", normalized)
        write_json(WORK / f"development-inputs/{name}-binding.json", {"source_manifest": sha(manifest), "source_queries": sha(question_file), "files": tree(target), "question_count": len(rows), "exposure": "historical full-workload diagnostic; development-only"})
        print(json.dumps({"stage": "development-input", "dataset": name, "queries": len(rows), "status": "prepared"}), flush=True)


def acquire_beir(name, seed):
    if name not in {"fiqa", "scifact"}:
        raise ValueError("Dataset is outside the predeclared validation portfolio")
    raw = WORK / "curator/validation-raw"
    raw.mkdir(parents=True, exist_ok=True)
    archive = raw / (name + ".zip")
    if archive.exists():
        raise ValueError("Validation acquisition already exists")
    url = f"https://public.ukp.informatik.tu-darmstadt.de/thakur/BEIR/datasets/{name}.zip"
    with urllib.request.urlopen(url, timeout=120) as response, archive.open("xb") as out:
        total = 0
        while block := response.read(1024 * 1024):
            total += len(block)
            if total > 256 * 1024 * 1024:
                raise ValueError("Unexpected acquisition size")
            out.write(block)
    with zipfile.ZipFile(archive) as package:
        wanted = [f"{name}/corpus.jsonl", f"{name}/queries.jsonl", f"{name}/qrels/test.tsv"]
        for key in wanted:
            info = package.getinfo(key)
            if info.file_size > 768 * 1024 * 1024 or info.is_dir():
                raise ValueError("Unexpected source member")
        corpus = {str(row["_id"]): row for line in package.read(wanted[0]).decode("utf-8").splitlines() if (row := json.loads(line))}
        queries = {str(row["_id"]): row["text"] for line in package.read(wanted[1]).decode("utf-8").splitlines() if (row := json.loads(line))}
        qrels = {}
        for row in csv.DictReader(io.StringIO(package.read(wanted[2]).decode("utf-8")), delimiter="\t"):
            if float(row["score"]) > 0:
                qrels.setdefault(row["query-id"], set()).add(row["corpus-id"])
    if not qrels or any(q not in queries or not refs.issubset(corpus) for q, refs in qrels.items()):
        raise ValueError("Incomplete source identities")
    def order(namespace, value):
        return hashlib.sha256(seed + b"\0" + namespace.encode() + b"\0" + str(value).encode()).hexdigest()
    chosen = sorted(qrels, key=lambda q: order("query-" + name, q))[:12]
    included = set().union(*(qrels[q] for q in chosen))
    included.update(sorted(set(corpus) - included, key=lambda d: order("document-" + name, d))[:max(0, 985 - len(included))])
    target = WORK / "curator/validation-inputs" / name
    (target / "input/documents").mkdir(parents=True, exist_ok=False)
    rows = [{"id": key, "title": (corpus[key].get("title", "") or ("Document " + key)).replace("[", "(").replace("]", ")"), "body": corpus[key]["text"]} for key in sorted(included)]
    content = "\n".join(json.dumps(row, sort_keys=True) for row in rows) + "\n"
    (target / "input/documents/corpus.jsonl").write_text(content, encoding="utf-8")
    manifest = {
        "schema_version": "1.0",
        "bundle": {"title": "Curated retrieval corpus", "description": "Frozen source-grounded documents for a private retrieval gate.", "base_iri": f"https://example.org/knowledge/transfer-{name}/", "ontology_iri": f"https://example.org/ontology/transfer-{name}", "version_iri": f"https://example.org/ontology/transfer-{name}/1", "prefix": "transfer", "owl_profile": "rl"},
        "ontology": {"classes": [{"name": "SourceDocument", "label": "source document"}], "properties": []}, "rules": [],
        "sources": [{"id": "documents", "kind": "json", "path": "documents/corpus.jsonl", "concept_type": "Source document", "ontology_class": "SourceDocument", "id_field": "id", "title_field": "title", "schema": {"id": "string", "title": "string", "body": "string"}}],
    }
    write_json(target / "input/manifest.json", manifest)
    normalized = [{"id": hashlib.sha256((name + ":" + q).encode()).hexdigest()[:20], "question": queries[q], "relevant": sorted(qrels[q])} for q in chosen]
    write_json(target / "queries.json", [{"id": row["id"], "question": row["question"]} for row in normalized])
    write_json(WORK / f"curator/validation/{name}-qrels.json", normalized)
    write_json(WORK / f"curator/validation/{name}-provenance.json", {"source": url, "archive_sha256": sha(archive), "source_counts": {"documents": len(corpus), "queries": len(qrels)}, "selected_counts": {"documents": len(rows), "queries": len(chosen)}, "selection": "seeded hash ordering; all positive references plus deterministic distractors; binary relevance", "files": tree(target), "exposure": "new to this campaign; public annotation/pretraining exposure cannot be excluded; reference-enriched diagnostic, not official BEIR scoring"})
    print(json.dumps({"stage": "private-validation-acquisition", "status": "prepared", "cohorts_completed": 1}), flush=True)


def build_oracle(name, split):
    source = (WORK / "development-inputs" / name) if split == "development" else (WORK / "curator/validation-inputs" / name)
    output = WORK / "curator/cores" / name
    original = output
    index = 1
    while output.exists():
        output = original.with_name(f"{name}-replay-{index:03d}")
        index += 1
    output.parent.mkdir(parents=True, exist_ok=True)
    baseline = WORK / "baseline/build-semantic-okf-knowledge-skill/assets/families/legacy/builder/scripts"
    interpreter = REPO / "evaluations/enterprise-rag-bench/.venv/Scripts/python.exe"
    if os.name != "nt":
        interpreter = Path(sys.executable)
    log = WORK / f"logs/oracle-{name}.log"
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("w", encoding="utf-8") as stream:
        command = [str(interpreter), "-B", str(baseline / "build_semantic_okf.py"), str(source / "input/manifest.json"), str(output), "--output-format", "json"]
        result = subprocess.run(command, stdout=stream, stderr=subprocess.STDOUT, timeout=2400, check=False)
    if result.returncode:
        raise ValueError(f"Canonical oracle construction failed; inspect {log.name}")
    if original.exists() and original != output and tree(original) != tree(output):
        raise ValueError("Canonical oracle replay changed bytes")
    rows = read_jsonl(output / "semantic/records.jsonl")
    records = {row["record_id"]: row for row in rows}
    questions = json.loads((WORK / f"curator/{split}/{name}-qrels.json").read_text(encoding="utf-8"))
    aliases = {}
    for key, row in records.items():
        candidates = {key, row["source_id"], str(row.get("record_key", ""))}
        if name == "astro" and row.get("source_path", "").startswith("sources/mdx/"):
            route = Path(row["source_path"]).with_suffix("").as_posix().removeprefix("sources/mdx/")
            candidates.add("/en/" + route.removesuffix("/index") + "/")
        attributes = row.get("attributes", {})
        if isinstance(attributes, dict):
            candidates.update(str(value) for attr, value in attributes.items() if attr in {"id", "document_id", "documentId"})
        for alias in candidates - {""}:
            aliases.setdefault(alias, set()).add(key)
    for question in questions:
        resolved = []
        for key in question["relevant"]:
            matches = {key} if key in records else aliases.get(key, set())
            if len(matches) != 1:
                raise ValueError(f"Ambiguous or missing oracle identity in {name}; inspect curator inputs locally")
            resolved.extend(matches)
        question["relevant"] = sorted(set(resolved))
    identities = {key: {field: row[field] for field in ("record_id", "record_sha256", "source_id", "concept_id", "concept_path")} for key, row in records.items()}
    write_json(WORK / f"curator/{split}/{name}-oracle.json", {"questions": questions, "records": {key: row["record_sha256"] for key, row in records.items()}, "record_identities": identities, "source_binding": tree(source)})
    print(json.dumps({"stage": "oracle-identities", "split": split, "status": "pass", "documents": len(records), "queries": len(questions)}), flush=True)


def task_roots(name, split):
    runtime = json.loads((WORK / "runtime.json").read_text(encoding="utf-8"))
    source = (WORK / "development-inputs" / name) if split == "development" else (WORK / "curator/validation-inputs" / name)
    oracle = json.loads((WORK / f"curator/{split}/{name}-oracle.json").read_text(encoding="utf-8"))
    if tree(source) != oracle["source_binding"]:
        raise ValueError("Source tree drifted after oracle binding")
    manifest = json.loads((source / "input/manifest.json").read_text(encoding="utf-8"))
    allowed = {"queries.json", "input/manifest.json"}
    for declaration in manifest["sources"]:
        pattern = Path(declaration["path"])
        if pattern.is_absolute() or ".." in pattern.parts:
            raise ValueError("Unsafe input manifest path")
        allowed.update(path.relative_to(source).as_posix() for path in (source / "input").glob(pattern.as_posix()) if path.is_file())
    if set(oracle["source_binding"]) != allowed or any(path.is_symlink() for path in source.rglob("*")):
        raise ValueError("Agent input includes undeclared files or links")
    queries = json.loads((source / "queries.json").read_text(encoding="utf-8"))
    if queries != [{"id": row["id"], "question": row["question"]} for row in oracle["questions"]]:
        raise ValueError("Query projection differs from oracle source")
    if linux(["docker", "image", "inspect", runtime["tag"], "--format", "{{.Id}}"] ) != runtime["image"]:
        raise ValueError("Runtime tag no longer resolves to the frozen image digest")
    context = WORK / "curator/image-contexts" / name
    context.mkdir(parents=True, exist_ok=False)
    shutil.copytree(source, context / "dataset")
    (context / "Dockerfile").write_text(f"FROM {runtime['tag']}\nCOPY dataset/ /dataset/\nRUN chmod -R a-w /dataset\nWORKDIR /workspace\n", encoding="utf-8")
    tag = "knowledge-evolution-data:" + hashlib.sha256((name + ":" + WORK.name).encode()).hexdigest()[:20]
    linux(["docker", "build", "--pull=false", "--network=none", "-t", tag, wsl_path(context)], log=WORK / f"logs/image-{name}.log")
    if linux(["docker", "image", "inspect", runtime["tag"], "--format", "{{.Id}}"] ) != runtime["image"] or tree(source) != oracle["source_binding"]:
        raise ValueError("Runtime or source changed during image construction")
    image = linux(["docker", "image", "inspect", tag, "--format", "{{.Id}}"])
    dataset_id = "internal-development-v1" if split == "development" else "transfer-" + name + "-v1"
    task_metadata = []
    plan = json.loads((WORK / "curator/authoring/plan/plan.private.json").read_text(encoding="utf-8"))
    plan_tasks = {task["taskId"]: task for task in plan["tasks"]}
    for family in FAMILIES:
        task_id = "retrieval-" + hashlib.sha256((name + ":" + family).encode()).hexdigest()[:20]
        planned = plan_tasks[task_id]
        if planned["split"] != split:
            raise ValueError("Task split differs from the frozen authoring plan")
        root = TASKS / dataset_id / task_id
        (root / "tests").mkdir(parents=True, exist_ok=False)
        output_path = planned["variantAxes"]["output-root"] + "/" + planned["variantAxes"]["output-name"]
        instruction = {"family": family, "output_path": output_path, "instruction": "Build and independently validate the staged family's knowledge from /dataset/input, then rank each request in /dataset/queries.json at Top-10. Preserve evidence identities and write the declared JSON artifact. Questions carry no relevance labels."}
        (root / "instruction.md").write_text(json.dumps(instruction, sort_keys=True) + "\n", encoding="utf-8")
        (root / "task.toml").write_text(f'''schema_version = "1.3"
artifacts = [{{ source = "{output_path}", destination = "response.json" }}]
[metadata]
capability = "source-grounded-retrieval"
resource_class = "cpu-two-threads"
[agent]
timeout_sec = 3600.0
network_mode = "public"
[verifier]
timeout_sec = 180.0
environment_mode = "separate"
network_mode = "public"
[verifier.environment]
docker_image = "{runtime['image']}"
os = "linux"
network_mode = "public"
cpus = 2
memory_mb = 8192
[environment]
docker_image = "{image}"
os = "linux"
network_mode = "public"
cpus = 2
memory_mb = 12288
storage_mb = 24576
workdir = "/workspace"
''', encoding="utf-8")
        contract = {**oracle, "family": family, "routes": MODES[family], "primary_route": PRIMARY[family], "output_path": output_path, "verifier_output_path": output_path}
        compose = "services:\n  main:\n    network_mode: none\n"
        (root / "environment").mkdir()
        (root / "environment/docker-compose.yaml").write_text(compose, encoding="utf-8")
        (root / "tests/docker-compose.yaml").write_text(compose + "    volumes:\n      - type: bind\n        source: .\n        target: /tests\n        read_only: true\n", encoding="utf-8")
        skill_files = tree(WORK / "baseline/build-semantic-okf-knowledge-skill")
        modules = {"legacy": [], "turso": ["_turso_read"], "embeddings": ["_embedding_snapshot"], "classical": ["_classical_snapshot"], "adaptive": ["_adaptive_snapshot"], "entity-graph": ["_entity_graph_model", "_entity_graph_snapshot"], "ensemble": ["_entity_graph_model", "_adaptive_snapshot", "_embedding_snapshot", "_entity_graph_snapshot", "_ensemble_snapshot"], "graphify": ["_graphify_snapshot"]}[family]
        imported = {f"assets/families/{family}/consultant/scripts/{module}.py": skill_files[f"assets/families/{family}/consultant/scripts/{module}.py"] for module in modules}
        contract.update(skill_files=skill_files, imported_candidate_modules=imported, mutable_skill_paths=["SKILL.md", "scripts/apply_retrieval_profile.py", "assets/retrieval-profile.json", "references/retrieval-profile.md"])
        write_json(root / "tests/contract.json", contract)
        for filename in ("verifier.py",):
            shutil.copyfile(HERE / filename, root / "tests" / filename)
        (root / "tests/runtime/support").mkdir(parents=True)
        shutil.copyfile(REPO / "evaluations/private-book-strategy-comparison/scripts/evaluate_all_routes.py", root / "tests/runtime/support/evaluate_all_routes.py")
        (root / "tests/test.sh").write_text("#!/bin/sh\nset -eu\npython -B -c 'from pathlib import Path; assert sorted(p.name for p in Path(\"/sys/class/net\").iterdir()) == [\"lo\"], \"Verifier must have only loopback networking\"'\npython -B /tests/verifier.py --scoring /tests/runtime/support/evaluate_all_routes.py\n", encoding="utf-8", newline="\n")
        task_metadata.append({"task_id": task_id, "dataset_id": dataset_id, "source_cohort": name, "family": family, "split": split, "response_mode": "structured", "output_path": output_path, "image": image, "source_family": "source-" + hashlib.sha256(name.encode()).hexdigest()[:20]})
    write_json(WORK / f"curator/{split}/{name}-tasks.json", task_metadata)
    print(json.dumps({"stage": "native-tasks", "split": split, "tasks": len(task_metadata), "status": "prepared"}), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=["internal", "acquire-validation", "oracle", "tasks"])
    parser.add_argument("--name")
    parser.add_argument("--split", choices=["development", "validation"])
    args = parser.parse_args()
    if args.stage == "internal":
        internal_inputs(args.name)
    elif args.stage == "acquire-validation":
        seed_path = WORK / "curator/validation-seed.bin"
        seed_path.parent.mkdir(parents=True, exist_ok=True)
        if seed_path.exists():
            seed = seed_path.read_bytes()
        else:
            seed = secrets.token_bytes(32)
            seed_path.write_bytes(seed)
        for name in ([args.name] if args.name else ("fiqa", "scifact")):
            acquire_beir(name, seed)
    elif args.stage == "oracle":
        build_oracle(args.name, args.split)
    else:
        task_roots(args.name, args.split)


if __name__ == "__main__":
    main()
