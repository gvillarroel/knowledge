"""Build or score a frozen generator version on a declared full-text projection.

This is a retrospective retrieval diagnostic, not an evolution controller or a
Harbor answer-quality evaluator. Run each version in an isolated process with
the same input, plan, runtime and evaluator. Keep output in an ignored directory.
"""
from __future__ import annotations

import argparse
from contextlib import ExitStack
import importlib.util
import json
from pathlib import Path
import shutil
import statistics
import subprocess
import sys
import tempfile
import time

import fulltext_projection as fidelity


def module(name: str, path: Path):
    """Load an explicit trusted runtime, never an implementation from the data."""
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    sys.modules[name] = result
    spec.loader.exec_module(result)
    return result


def write_once(path: Path, value: dict) -> None:
    """Preserve completed evidence instead of silently replacing it."""
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2,
                         allow_nan=False) + "\n"
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(encoded)


def build(args) -> dict:
    """Use the complete standalone generator and verify its source-text fidelity."""
    before = fidelity.tree_hashes(args.input)
    generator_before = fidelity.tree_hashes(args.generator)
    command = [sys.executable, "-B", str(args.generator / "scripts/build_semantic_okf_knowledge_skill.py"),
               str(args.input / "manifest.json"), str(args.expert), "--family", args.family,
               "--name", args.expert.name, "--description", "Consult enterprise records with exact source evidence.",
               "--guidance", str(args.input / "guidance.md"), "--concept-layout", "source-packed-v1",
               "--output-format", "json"]
    if args.plan:
        command += ["--plan", str(args.plan)]
    started = time.monotonic()
    completed = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", timeout=3600)
    (args.output.parent / "build-stdout.log").write_text(completed.stdout, encoding="utf-8")
    (args.output.parent / "build-stderr.log").write_text(completed.stderr, encoding="utf-8")
    if completed.returncode:
        raise ValueError(f"Generator failed with exit {completed.returncode}; inspect the local build logs")
    native = json.loads(completed.stdout)
    if native.get("status") != "pass" or native.get("deep_validation") is not True:
        raise ValueError("The generator did not attest successful deep validation")
    source = fidelity.verify(args.input, args.expert / "references/knowledge/semantic/records.jsonl")
    if before != fidelity.tree_hashes(args.input) or generator_before != fidelity.tree_hashes(args.generator):
        raise ValueError("Build input or generator changed")
    return {"status": "pass", "family": args.family, "build_seconds": time.monotonic() - started,
            "build": native, "source_fidelity": source, "files": fidelity.tree_hashes(args.expert)}


def turso_connection(database: Path, runtime, resources: ExitStack):
    """Contain engine sidecars using the canonical consultant's working-copy policy."""
    before = runtime.database_file_state(database)
    if set(before) != {database.name}:
        raise ValueError("Published Turso database is missing or has active sidecars")
    temporary = Path(resources.enter_context(tempfile.TemporaryDirectory(prefix="enterprise-turso-")))
    working = temporary / database.name
    shutil.copy2(database, working)
    if runtime.database_file_state(working) != before:
        raise ValueError("Turso working copy differs from the published database")
    connection = runtime.connect_read_only(working)
    resources.callback(connection.close)
    runtime.require_valid_database(connection, full=True)
    return connection


def routes(expert: Path, family: str, helpers: Path, evaluator, resources: ExitStack) -> dict:
    """Use the generated consultant; retain the two historical comparator routes."""
    bundle, native = expert / "references/knowledge", expert / "scripts/native"
    sys.path.insert(0, str(native))
    payload = evaluator.payload_results
    if family == "legacy":
        legacy = module("generator_comparison_legacy", helpers / "compare_retrieval.py")
        index = legacy.LegacyLexicalIndex.from_ledger(legacy.AuthoritativeLedger.from_bundle(bundle))
        return {"legacy-lexical": lambda q: index.search(q, 10)}
    if family == "turso":
        runtime = module("generator_comparison_turso", native / "_turso_read.py")
        connection = turso_connection(bundle / "semantic/knowledge.db", runtime, resources)
        return {"turso-lexical-sql": lambda q: evaluator.turso_search(connection, q, 10)}
    if family == "graphify":
        runtime = module("generator_comparison_graphify", native / "_graphify_snapshot.py")
        snapshot = runtime.Snapshot(bundle)
        return {"graphify-search": lambda q: payload(snapshot.search(q, depth=2, top_k=10))}
    stems = {"embeddings": "embedding", "classical": "classical", "adaptive": "adaptive",
             "entity-graph": "entity_graph", "ensemble": "ensemble"}
    runtime = module("generator_comparison_runtime", native / f"_{stems[family]}_snapshot.py")
    snapshot = (runtime.load_snapshot(bundle) if family == "embeddings"
                else runtime.load_snapshot(bundle, deep_validation=True))
    modes = {"embeddings": ("lexical", "vector", "hybrid"),
             "classical": ("bm25", "topic", "association", "fusion"),
             "adaptive": ("adaptive",), "entity-graph": ("lexical", "entity", "traversal", "fusion"),
             "ensemble": ("fast", "quality", "robust")}
    result = {}
    for mode in modes[family]:
        route = "adaptive-fusion" if family == "adaptive" else f"{family}-{mode}"
        if family == "embeddings":
            result[route] = lambda q, m=mode: payload(runtime.search_snapshot(snapshot, q, requested_mode=m, top_k=10))
        else:
            result[route] = lambda q, m=mode: payload(runtime.search_snapshot(snapshot, q, m, 10))
    return result


def validate_questions(rows: list, authoritative: dict) -> None:
    """Reject malformed, repeated or unresolved retrieval questions before scoring."""
    if not isinstance(rows, list) or not rows:
        raise ValueError("No questions")
    identifiers = []
    for row in rows:
        if (not isinstance(row, dict) or not isinstance(row.get("id"), str)
                or not row["id"] or not isinstance(row.get("question"), str)
                or not row["question"].strip() or not isinstance(row.get("relevant"), list)
                or not row["relevant"] or any(not isinstance(x, str) for x in row["relevant"])
                or len(set(row["relevant"])) != len(row["relevant"])
                or not set(row["relevant"]).issubset(authoritative)
                or not isinstance(row.get("category"), str) or not isinstance(row.get("cohort"), str)):
            raise ValueError("Invalid or unresolved question")
        identifiers.append(row["id"])
    if len(set(identifiers)) != len(identifiers):
        raise ValueError("Duplicate question identity")


def score(args) -> dict:
    """Measure unchanged document metrics, keeping per-question data local."""
    before = fidelity.tree_hashes(args.expert)
    question_bytes = args.questions.read_bytes()
    evaluator = module("generator_comparison_evaluator", args.helpers / "evaluate_all_routes.py")
    _, authoritative = evaluator.ledger(args.expert / "references/knowledge")
    questions = json.loads(question_bytes)
    validate_questions(questions, authoritative)
    measured = []
    with ExitStack() as resources:
        for route, search in routes(args.expert, args.family, args.helpers, evaluator, resources).items():
            value = evaluator.evaluate_route(route, search, questions, authoritative, 1, 10)
            value.pop("query_stability_ratio")  # A single pass does not test stability.
            categories = {q["id"]: q["category"] for q in questions}
            value["categories"] = {}
            for category in sorted(set(categories.values())):
                rows = [r for r in value["replicates"][0]["queries"] if categories[r["question_id"]] == category]
                value["categories"][category] = {"question_count": len(rows), "metrics": {
                    key: statistics.fmean(r["metrics"][key] for r in rows) for key in value["metrics"]}}
            measured.append(value)
    if before != fidelity.tree_hashes(args.expert) or args.questions.read_bytes() != question_bytes:
        raise ValueError("Expert or questions changed during retrieval")
    return {"status": "pass", "family": args.family, "question_count": len(questions),
            "expert_unchanged": True, "routes": measured}


def main() -> int:
    """Select one isolated operation against explicit, previously frozen paths."""
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("build", "score"):
        item = sub.add_parser(name)
        item.add_argument("--family", required=True, choices=["legacy", "embeddings", "classical", "adaptive",
                                                             "entity-graph", "ensemble", "graphify", "turso"])
        item.add_argument("--expert", required=True, type=Path)
        item.add_argument("--output", required=True, type=Path)
        if name == "build":
            item.add_argument("--generator", required=True, type=Path)
            item.add_argument("--input", required=True, type=Path)
            item.add_argument("--plan", type=Path)
        else:
            item.add_argument("--questions", required=True, type=Path)
            item.add_argument("--helpers", required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Output already exists; use a fresh ignored destination")
    result = build(args) if args.command == "build" else score(args)
    write_once(args.output, result)
    print(json.dumps({"status": result["status"], "family": args.family, "operation": args.command}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
