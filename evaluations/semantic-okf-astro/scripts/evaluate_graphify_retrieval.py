#!/usr/bin/env python3
"""Evaluate the Graphify consultation route on the frozen 40-question Astro benchmark."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Sequence


SCRIPT = Path(__file__).resolve()
EVALUATION = SCRIPT.parents[1]
REPO = SCRIPT.parents[3]
BASE_EVALUATOR = SCRIPT.with_name("evaluate_retrieval.py")
GRAPHIFY_RUNTIME = (
    REPO / "skills/consult-semantic-okf-graphify/scripts/_graphify_snapshot.py"
)


def _load_base() -> Any:
    specification = importlib.util.spec_from_file_location(
        "semantic_okf_astro_retrieval_base", BASE_EVALUATOR
    )
    if specification is None or specification.loader is None:
        raise RuntimeError(f"cannot load evaluator: {BASE_EVALUATOR}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    return module


def evaluate(args: argparse.Namespace) -> dict[str, Any]:
    """Run Graphify twice-gated discovery without modifying the published bundle."""

    base = _load_base()
    identity, documents = base.load_identity_map(args.source_combination)
    questions = base.load_questions(args.questions, documents)
    ledger = base.Ledger(args.bundle, identity)
    before = base.bundle_identity(args.bundle)

    setup_started = time.perf_counter()
    runtime = base._load_module("astro_graphify_snapshot", GRAPHIFY_RUNTIME)
    snapshot = runtime.Snapshot(args.bundle)
    inspection = snapshot.verify()
    setup_ms = (time.perf_counter() - setup_started) * 1000.0

    def search(query: str) -> list[Any]:
        payload = snapshot.search(
            query, depth=args.depth, top_k=base.RAW_POOL, show_content=False
        )
        if payload.get("fallback") is not None:
            raise base.EvaluationError("graphify used a fallback")
        results = []
        for raw in payload.get("records", []):
            record = ledger.by_identity[(raw["source_id"], raw["record_id"])]
            body = record["body"]
            results.append(
                {
                    **raw,
                    "text": body,
                    "text_sha256": base.sha256_bytes(body.encode("utf-8")),
                    "locator": {"kind": "record"},
                    "score": raw.get("graphify_score"),
                }
            )
        return base.normalize_hits(
            {
                **payload,
                "status": "pass",
                "results": results,
            },
            ledger,
        )

    routes = base.evaluate_family_routes(
        "graphify",
        ("graphify",),
        questions,
        ledger,
        {"graphify": search},
        "warm in-process Graphify lexical scoring plus bounded BFS depth 2",
        progress=True,
    )
    standalone = base.standalone_route_timing(
        "graphify", "graphify", questions, search, progress=True
    )
    after = base.bundle_identity(args.bundle)
    if before != after:
        raise base.EvaluationError("Graphify consultation modified its published bundle")

    winner = routes[0]
    report = {
        "schema_version": "semantic-okf-astro-graphify-retrieval/1.0",
        "status": "pass" if winner["status"] == standalone["status"] == "pass" else "fail",
        "benchmark": {
            "questions_path": args.questions.relative_to(REPO).as_posix(),
            "questions_sha256": base.sha256_file(args.questions),
            "question_count": len(questions),
            "hard_question_count": sum(row.cohort == "hard" for row in questions),
            "candidate_pool": base.RAW_POOL,
        },
        "bundle": {
            "path": args.bundle.relative_to(REPO).as_posix(),
            "before_sha256": before,
            "after_sha256": after,
            "unchanged": before == after,
        },
        "source_combination": {
            "path": args.source_combination.relative_to(REPO).as_posix(),
            "sha256": base.sha256_file(args.source_combination),
            "record_count": len(identity),
        },
        "inspections": {"graphify": inspection},
        "runtime_setup": {
            "graphify": {
                "elapsed_ms": round(setup_ms, 3),
                "snapshot_loads": 1,
                "included_in_query_timings": False,
            }
        },
        "standalone_best_route_timing": {"graphify": standalone},
        "routes": routes,
        "families": [
            {
                "family": "graphify",
                "status": winner["status"],
                "best_route": "graphify",
                "overall": winner["overall"],
                "hard": winner["hard"],
            }
        ],
    }
    return report


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse Graphify evaluation paths and limits."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument(
        "--questions",
        type=Path,
        default=EVALUATION / "benchmark/retrieval-questions.jsonl",
    )
    parser.add_argument(
        "--source-combination",
        type=Path,
        default=EVALUATION / "corpus/source-combination.json",
    )
    parser.add_argument("--depth", type=int, default=2)
    parser.add_argument("--raw-output", type=Path, required=True)
    parser.add_argument("--compact-json", type=Path, required=True)
    parser.add_argument("--compact-markdown", type=Path, required=True)
    args = parser.parse_args(argv)
    for name in (
        "bundle",
        "questions",
        "source_combination",
        "raw_output",
        "compact_json",
        "compact_markdown",
    ):
        setattr(args, name, getattr(args, name).resolve())
    if not args.bundle.is_dir():
        parser.error(f"bundle does not exist: {args.bundle}")
    if args.depth < 0:
        parser.error("--depth cannot be negative")
    return args


def main(argv: Sequence[str] | None = None) -> int:
    """Execute Graphify evaluation and publish append-only evidence."""

    args = parse_args(argv)
    base = _load_base()
    try:
        report = evaluate(args)
        base.append_only_write(args.raw_output, base.pretty_json(report))
        compact = dict(report)
        compact["routes"] = [
            {key: value for key, value in row.items() if key != "queries"}
            for row in report["routes"]
        ]
        base.atomic_write(args.compact_json, base.pretty_json(compact))
        base.atomic_write(args.compact_markdown, base.render_markdown(compact))
    except (OSError, RuntimeError, ValueError, TypeError, KeyError) as exc:
        print(json.dumps({"status": "error", "error": str(exc)}), file=sys.stderr)
        return 1
    print(json.dumps({"status": report["status"], "routes": 1}))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    os.environ.setdefault("PYTHONDONTWRITEBYTECODE", "1")
    raise SystemExit(main())
