"""Execute an exact staged multi-family package without reading relevance labels."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import statistics
import stat
import shutil
import subprocess
import sys
import time
from pathlib import Path


FAMILIES = ("legacy", "embeddings", "classical", "adaptive", "entity-graph", "ensemble", "graphify", "turso")
PRIMARY = {"legacy": "lexical", "embeddings": "hybrid", "classical": "fusion", "adaptive": "adaptive", "entity-graph": "fusion", "ensemble": "quality", "graphify": "search", "turso": "lexical-sql"}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tree(root):
    def linked(path):
        return path.is_symlink() or bool(getattr(path.lstat(), "st_file_attributes", 0) & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0))
    if not root.is_dir() or linked(root):
        raise ValueError("Linked skill roots are forbidden")
    result = {}
    for p in sorted(root.rglob("*")):
        if linked(p):
            raise ValueError("Linked skill content is forbidden")
        if p.is_file():
            result[p.relative_to(root).as_posix()] = sha256(p)
    return result


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")


def execute(argv, log):
    with log.open("w", encoding="utf-8") as stream:
        result = subprocess.run(argv, stdout=stream, stderr=subprocess.STDOUT, timeout=2400, check=False)
    if result.returncode:
        raise RuntimeError(f"Runtime command failed: {Path(argv[2]).name}; see {log.name}")


def build_family(skill, family, source, target, plan, log_root):
    scripts = skill / "assets/families" / family / "builder/scripts"
    slug = "" if family in {"legacy", "turso"} else "_" + family.replace("-", "_")
    args = [sys.executable, "-B", str(scripts / f"build_semantic_okf{slug}.py"), str(source / "manifest.json")]
    if plan is not None:
        args.append(str(plan))
    args.extend([str(target), "--output-format", "json"])
    execute(args, log_root / f"{target.name}-build.log")
    execute([sys.executable, "-B", str(scripts / f"validate_semantic_okf{slug}.py"), str(target), "--output-format", "json"], log_root / f"{target.name}-validate.log")
    if family == "turso":
        execute([sys.executable, "-B", str(scripts / "validate_turso_store.py"), str(target / "semantic/knowledge.db"), "--bundle", str(target), "--output-format", "json"], log_root / f"{target.name}-turso.log")


def routes(skill, family, bundle, evaluator, attestation):
    scripts = skill / "assets/families" / family / "consultant/scripts"

    def module(name, filename):
        path = scripts / filename
        attestation[path.relative_to(skill).as_posix()] = sha256(path)
        return load(name, path)

    if family == "legacy":
        comparator = load("legacy_comparator", Path(__file__).parent / "legacy_comparator.py")
        index = comparator.LegacyLexicalIndex.from_ledger(comparator.AuthoritativeLedger.from_bundle(bundle))
        return {"lexical": lambda q: index.search(q, 10)}
    if family == "turso":
        runtime = module("_turso_read", "_turso_read.py")
        # The read-only SQLite driver creates WAL sidecars. Use an exact scratch
        # copy so the authoritative built knowledge stays byte-for-byte fixed.
        scratch = bundle.parent / "query-scratch"
        scratch.mkdir()
        database = scratch / "knowledge.db"
        shutil.copyfile(bundle / "semantic/knowledge.db", database)
        if sha256(database) != sha256(bundle / "semantic/knowledge.db"):
            raise ValueError("SQL consultation copy changed database bytes")
        connection = runtime.connect_read_only(database)
        runtime.require_valid_database(connection, full=True)
        return {"lexical-sql": lambda q: evaluator.turso_search(connection, q, 10)}
    if family == "entity-graph":
        module("_entity_graph_model", "_entity_graph_model.py")
    if family == "ensemble":
        module("_entity_graph_model", "_entity_graph_model.py")
        for name in ("_adaptive_snapshot", "_embedding_snapshot", "_entity_graph_snapshot"):
            module(name, name + ".py")
    name = "_embedding_snapshot" if family == "embeddings" else "_" + family.replace("-", "_") + "_snapshot"
    runtime = module(name, name + ".py")
    if family == "graphify":
        snapshot = runtime.Snapshot(bundle)
        return {"search": lambda q: evaluator.payload_results(snapshot.search(q, depth=2, top_k=10))}
    snapshot = runtime.load_snapshot(bundle, **({} if family == "embeddings" else {"deep_validation": True}))
    modes = {"embeddings": ["lexical", "vector", "hybrid"], "classical": ["bm25", "topic", "association", "fusion"], "adaptive": ["adaptive"], "entity-graph": ["lexical", "entity", "traversal", "fusion"], "ensemble": ["fast", "quality", "robust"]}[family]
    if family == "embeddings":
        return {mode: lambda q, m=mode: evaluator.payload_results(runtime.search_snapshot(snapshot, q, requested_mode=m, top_k=10)) for mode in modes}
    return {mode: lambda q, m=mode: evaluator.payload_results(runtime.search_snapshot(snapshot, q, m, 10)) for mode in modes}


def run(skill, family, input_root, output):
    if family not in FAMILIES or not (skill / "SKILL.md").is_file():
        raise ValueError("Invalid family or staged package")
    if output.exists():
        raise ValueError("Output already exists")
    before = tree(skill)
    source = input_root / "input"
    work = output.parent
    work.mkdir(parents=True, exist_ok=True)
    helpers = Path(__file__).parent
    evaluator = load("frozen_evaluator", helpers / "evaluate_all_routes.py")
    plans = load("frozen_build_plans", helpers / "prepare_strategy_bundles.py")
    selection = plans.source_ids(json.loads((source / "manifest.json").read_text(encoding="utf-8")))
    plan = None
    if family in {"embeddings", "classical", "adaptive", "entity-graph", "ensemble"}:
        name = ("embedding" if family == "embeddings" else family.replace("-", "_")) + "_plan"
        value = getattr(plans, name)(selection)
        profile_script = skill / "scripts/apply_retrieval_profile.py"
        plan = work / "plan.json"
        write_json(plan, value)
        if profile_script.exists():
            adjusted = work / "adjusted-plan.json"
            execute([sys.executable, "-B", str(profile_script), "--family", family, "--input", str(plan), "--output", str(adjusted)], work / "profile.log")
            plan = adjusted
    build_start = time.monotonic()
    for target in (work / "knowledge", work / "rebuild"):
        build_family(skill, family, source, target, plan, work)
    first, second = tree(work / "knowledge"), tree(work / "rebuild")
    if first != second:
        raise ValueError("Repeated build changed artifact bytes")
    build_seconds = time.monotonic() - build_start
    bundle = work / "knowledge"
    _, records = evaluator.ledger(bundle)
    questions = json.loads((input_root / "queries.json").read_text(encoding="utf-8"))
    if any(set(row) != {"id", "question"} for row in questions) or len({r["id"] for r in questions}) != len(questions):
        raise ValueError("Query inputs must be unique and evaluator-free")
    attestation = {}
    operations = routes(skill, family, bundle, evaluator, attestation)
    results = {}
    for mode, operation in operations.items():
        rows, timings = [], []
        for question in questions:
            started = time.perf_counter()
            hits = evaluator.normalize_hits(operation(question["question"]), records, 10)
            elapsed = (time.perf_counter() - started) * 1000
            timings.append(elapsed)
            rows.append({"id": question["id"], "hits": hits, "milliseconds": elapsed})
        results[mode] = {"queries": rows, "p95_ms": evaluator.percentile_95(timings)}
    if tree(skill) != before or tree(bundle) != first:
        raise ValueError("Skill or knowledge changed during consultation")
    write_json(output, {
        "schema_version": "skill-retrieval-trial/1.0", "family": family,
        "primary_route": PRIMARY[family], "routes": results,
        "skill_files": before, "imported_candidate_modules": attestation,
        "knowledge_files": first, "record_identities": {key: {field: row[field] for field in ("record_id", "record_sha256", "source_id", "concept_id", "concept_path")} for key, row in records.items()},
        "plan_sha256": sha256(plan) if plan else None,
        "build_seconds": build_seconds, "builds_byte_identical": True,
        "knowledge_bytes": sum(p.stat().st_size for p in bundle.rglob("*") if p.is_file()),
        "llm_calls": 0, "answer_quality_evaluated": False,
    })


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skill", type=Path, required=True)
    parser.add_argument("--family", choices=FAMILIES, required=True)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    run(args.skill.absolute(), args.family, args.input.resolve(), args.output.resolve())
