#!/usr/bin/env python3
"""Build the unchanged eight skill families and measure 18 reduced-corpus routes."""

from __future__ import annotations

import argparse
import importlib.metadata
import importlib.util
import json
import os
import platform
import re
import statistics
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import dataset_tool as dataset

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
FAMILIES = ("legacy", "embeddings", "classical", "adaptive", "entity-graph", "ensemble", "graphify", "turso")
HELPERS = REPO / "evaluations/private-book-strategy-comparison/scripts"


def load_helper(name: str, filename: str) -> Any:
    """Import an existing repository evaluator without changing its contracts."""
    spec = importlib.util.spec_from_file_location(name, HELPERS / filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def execute(command: list[str], log: Path) -> float:
    """Run one bounded stage and retain raw output only in the ignored workspace."""
    log.parent.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    with log.open("w", encoding="utf-8", newline="\n") as output:
        result = subprocess.run(command, cwd=REPO, stdout=output, stderr=subprocess.STDOUT,
                                timeout=3600, check=False)
    if result.returncode:
        raise ValueError(f"stage failed; inspect local log: {log.relative_to(REPO)}")
    return time.monotonic() - started


def code_binding() -> dict[str, str]:
    """Freeze every executable input before scoring and check it again at publication."""
    paths = [*ROOT.glob("*.py"), ROOT / "descriptor.json", *HELPERS.glob("*.py")]
    for family in FAMILIES:
        suffix = "" if family == "legacy" else f"-{family}"
        for role in ("build", "consult"):
            skill = REPO / "skills" / f"{role}-semantic-okf{suffix}"
            paths.extend(path for path in skill.rglob("*") if path.is_file()
                         and "__pycache__" not in path.parts and path.suffix != ".pyc")
    return {path.relative_to(REPO).as_posix(): dataset.sha256(path) for path in sorted(set(paths))}


def build(run_root: Path, prepared: Path) -> None:
    """Build every family twice, validate both copies, and require deterministic parity."""
    run_root.mkdir(parents=True, exist_ok=False)
    binding = {"code": code_binding(), "data": dataset.tree_hashes(prepared)}
    (run_root / "input-binding.json").write_bytes(dataset.json_bytes(binding))
    helper = load_helper("enterprise_build_helper", "prepare_strategy_bundles.py")
    manifest_path = prepared / "input/manifest.json"
    selection = helper.source_ids(json.loads(manifest_path.read_text(encoding="utf-8")))
    plans = {family: getattr(helper, ("embedding" if family == "embeddings" else family.replace("-", "_")) + "_plan")(selection)
             for family in ("embeddings", "classical", "adaptive", "entity-graph", "ensemble")}
    plan_root = run_root / "plans"
    plan_root.mkdir()
    for family, plan in plans.items():
        (plan_root / f"{family}.json").write_bytes(dataset.json_bytes(plan))
    receipts = []
    for family in FAMILIES:
        print(f"Building and verifying {family}", flush=True)
        elapsed = []
        for copy in ("bundles", "rebuild"):
            target = run_root / copy / family
            target.parent.mkdir(exist_ok=True)
            if family == "legacy":
                script_root = REPO / "skills/build-semantic-okf/scripts"
                command = [sys.executable, str(script_root / "build_semantic_okf.py"),
                           str(manifest_path), str(target), "--output-format", "json"]
                validators = [[sys.executable, str(script_root / "validate_semantic_okf.py"),
                               str(target), "--output-format", "json"]]
            else:
                command, validators = helper.family_commands(family, manifest_path,
                                                              plan_root / f"{family}.json", target)
            elapsed.append(execute(command, run_root / "logs" / f"{family}-{copy}-build.log"))
            for index, validator in enumerate(validators):
                execute(validator, run_root / "logs" / f"{family}-{copy}-validate-{index}.log")
        first = dataset.tree_hashes(run_root / "bundles" / family)
        second = dataset.tree_hashes(run_root / "rebuild" / family)
        # Turso's physical page layout is not the logical database identity.
        # Its independent validator checks all rows and the logical digest on each build.
        excluded = {"semantic/knowledge.db"} if family == "turso" else set()
        if {k: v for k, v in first.items() if k not in excluded} != {k: v for k, v in second.items() if k not in excluded}:
            raise ValueError(f"deterministic rebuild drift: {family}")
        receipts.append({"family": family, "status": "pass", "build_seconds": elapsed,
                         "file_count": len(first), "byte_identical": first == second,
                         "database_logical_validation": family == "turso"})
        (run_root / "build-receipt.json").write_bytes(dataset.json_bytes(receipts))


def check_binding(run_root: Path, prepared: Path) -> None:
    """Fail on input drift before and after measurement."""
    expected = json.loads((run_root / "input-binding.json").read_text(encoding="utf-8"))
    if expected != {"code": code_binding(), "data": dataset.tree_hashes(prepared)}:
        raise ValueError("code or prepared data changed after the build was frozen")


def evaluate_one(run_root: Path, prepared: Path, route: str, result_path: Path) -> None:
    """Evaluate one route in an isolated process with no sibling-route cache priming."""
    check_binding(run_root, prepared)
    helper = load_helper("enterprise_retrieval_helper", "evaluate_all_routes.py")
    bundles = {family: run_root / "bundles" / family for family in FAMILIES}
    authoritative, _ = helper.validate_core_parity(bundles)
    questions = json.loads((prepared / "evaluator/questions.json").read_text(encoding="utf-8"))
    runtimes = helper.load_runtimes(bundles)
    routes = helper.route_functions(runtimes, 10)
    if route not in routes:
        raise ValueError("unknown route")
    evaluated = helper.evaluate_route(route, routes[route], questions, authoritative, 3, 10)
    categories = {row["id"]: row["category"] for row in questions}
    evaluated["categories"] = {}
    for category in sorted(set(categories.values())):
        rows = [row for row in evaluated["replicates"][0]["queries"]
                if categories[row["question_id"]] == category]
        evaluated["categories"][category] = {
            "question_count": len(rows),
            **{key: statistics.fmean(row["metrics"][key] for row in rows)
               for key in evaluated["metrics"]}}
    check_binding(run_root, prepared)
    result_path.write_bytes(dataset.json_bytes(evaluated))


def public_row(row: dict[str, Any]) -> dict[str, Any]:
    """Publish only the reviewed aggregate allowlist, without per-question results."""
    keys = ("strategy_id", "family", "label", "metrics", "query_stability_ratio",
            "evidence_validity", "representative_p95_ms", "categories")
    return {key: row[key] for key in keys}


def score(run_id: str, run_root: Path, prepared: Path) -> None:
    """Measure every route and publish a complete, bound aggregate comparison."""
    check_binding(run_root, prepared)
    helper = load_helper("enterprise_retrieval_helper", "evaluate_all_routes.py")
    result_root = ROOT / "results" / run_id
    report_root = ROOT / "reports" / run_id
    if result_root.exists() or report_root.exists():
        raise ValueError("results already exist; choose an append-only run ID")
    result_root.mkdir(parents=True)
    rows = []
    started = time.monotonic()
    for route in sorted(helper.ROUTE_LABELS):
        print(f"Evaluating {route}: 40 questions x 3 repetitions", flush=True)
        result_path = result_root / f"{route}.json"
        execute([sys.executable, str(Path(__file__)), "route", "--run-id", run_id,
                 "--route", route], run_root / "logs" / f"{route}-evaluation.log")
        rows.append(public_row(json.loads(result_path.read_text(encoding="utf-8"))))
    check_binding(run_root, prepared)
    ranking = sorted(rows, key=lambda row: (-row["metrics"]["ndcg_at_10"],
                                           -row["metrics"]["mrr_at_10"],
                                           -row["metrics"]["recall_at_10"], row["strategy_id"]))
    for position, row in enumerate(ranking, 1):
        row["position"] = position
    report = {"schema_version": "enterprise-rag-comparison/1.0", "status": "pass",
              "title": "EnterpriseRAG-Bench 40-question reduced-corpus comparison",
              "dataset_id": dataset.read_descriptor()["dataset_id"], "question_count": 40,
              "top_k": 10, "replicates": 3, "strategy_count": len(rows),
              "answer_quality_evaluated": False, "promotion_eligible": False,
              "model_calls": 0, "llm_tokens": 0, "provider_cost_usd": 0,
              "local_compute_cost_usd": None, "wall_seconds": time.monotonic() - started,
              "runtime": {"python": platform.python_version(), "platform": platform.platform(),
                          "processor": platform.processor(), "logical_cpus": os.cpu_count(),
                          "concurrency": 1, "cache_policy": "one fresh process per route; repeated-query warm caches",
                          "dependencies": {name: importlib.metadata.version(name)
                                           for name in ("rdflib", "pyshacl", "pyturso", "graphifyy")}},
              "preparation": json.loads((prepared / "preparation.json").read_text(encoding="utf-8")),
              "builds": json.loads((run_root / "build-receipt.json").read_text(encoding="utf-8")),
              "input_binding_sha256": dataset.sha256(run_root / "input-binding.json"),
              "private_result_sha256": {route: dataset.sha256(result_root / f"{route}.json")
                                        for route in sorted(helper.ROUTE_LABELS)},
              "ranking": ranking}
    report_root.mkdir(parents=True)
    (report_root / "comparison.json").write_bytes(dataset.json_bytes(report))
    text = helper.render_markdown(report)
    text += ("\nThis is a reference-enriched reduced corpus with 85 reference documents and 900 fixed distractors, "
             "not an official Onyx leaderboard run over all 511,962 documents. The 40 questions cover eight "
             "grounded categories; high-level and information-not-found questions require a separate answer-quality contract.\n\n"
             "The embedding backend is deterministic 384-dimensional hashing. No model was called. Provider cost and "
             "LLM tokens are zero for retrieval; local compute cost and generated-answer correctness were not measured. "
             "Each route has a fresh process; initialization is excluded from P95, and three repetitions reuse that route's caches.\n")
    (report_root / "comparison.md").write_text(text, encoding="utf-8", newline="\n")
    print(json.dumps({"status": "pass", "routes": len(rows), "query_executions": 40 * 3 * len(rows),
                      "highest_ndcg_route": ranking[0]["strategy_id"]}), flush=True)


def main() -> int:
    """Run reproducible builds, the complete comparison, or one internal route."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["build", "evaluate", "route"])
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--route")
    args = parser.parse_args()
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,79}", args.run_id):
        parser.error("run ID must be a safe lowercase label")
    run_root = ROOT / "generated" / args.run_id
    prepared = ROOT / "processed" / dataset.read_descriptor()["dataset_id"]
    try:
        if args.command == "build":
            build(run_root, prepared)
        elif args.command == "evaluate":
            score(args.run_id, run_root, prepared)
        else:
            if args.route not in load_helper("enterprise_routes", "evaluate_all_routes.py").ROUTE_LABELS:
                raise ValueError("unknown route")
            result = ROOT / "results" / args.run_id / f"{args.route}.json"
            if result.exists():
                raise ValueError("route result already exists")
            evaluate_one(run_root, prepared, args.route, result)
        return 0
    except (ValueError, OSError, subprocess.TimeoutExpired) as exc:
        print(json.dumps({"status": "error", "error": str(exc)}), flush=True)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
