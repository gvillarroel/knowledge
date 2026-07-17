#!/usr/bin/env python3
"""Validate and rank one completed offline ensemble population."""

from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path
from typing import Any, Sequence

from _evaluation import (
    ENSEMBLE_PLAN,
    FROZEN_MANIFEST,
    REPO_ROOT,
    EvaluationError,
    display_path,
    geometric_mean,
    load_json,
    mean,
    sha256,
    validate_frozen,
    write_new,
)


CONFIG_KEYS = {
    "schema_version",
    "search_id",
    "status",
    "bindings",
    "population",
    "candidate_boundary",
    "result_schema",
    "selection",
}
GENERATION_KEYS = {
    "schema_version",
    "search_id",
    "generation",
    "status",
    "benchmark_visibility",
    "candidates",
}
CANDIDATE_KEYS = {
    "candidate_id",
    "parent_ids",
    "operator",
    "hypothesis",
    "mutation_scope",
    "status",
}
RESULT_KEYS = {
    "schema_version",
    "candidate_id",
    "frozen_benchmark_sha256",
    "ensemble_plan_sha256",
    "evaluation_contract_sha256",
    "repetitions",
}
REPETITION_KEYS = {"repetition", "rankings_sha256", "hard_gates", "objectives", "p95_latency_ms"}
HEX_SHA256 = re.compile(r"[0-9a-f]{64}\Z")


def exact_keys(value: Any, expected: set[str], label: str) -> dict[str, Any]:
    """Require one object to use an exact closed key set."""

    if not isinstance(value, dict):
        raise EvaluationError(f"{label} must be an object")
    actual = set(value)
    if actual != expected:
        raise EvaluationError(
            f"{label} uses a closed schema; missing={sorted(expected - actual)}, "
            f"unknown={sorted(actual - expected)}"
        )
    return value


def repo_file(binding: Any, label: str) -> tuple[Path, str]:
    """Resolve and verify one path/SHA binding within the repository."""

    entry = exact_keys(binding, {"path", "sha256"}, label)
    raw_path = entry["path"]
    expected = entry["sha256"]
    if not isinstance(raw_path, str) or not raw_path or not isinstance(expected, str):
        raise EvaluationError(f"{label} path and sha256 must be nonempty strings")
    path = (REPO_ROOT / raw_path).resolve(strict=True)
    try:
        path.relative_to(REPO_ROOT.resolve())
    except ValueError as exc:
        raise EvaluationError(f"{label} escapes the repository") from exc
    if not HEX_SHA256.fullmatch(expected) or sha256(path) != expected:
        raise EvaluationError(f"{label} SHA-256 differs")
    return path, expected


def finite(value: Any, label: str, minimum: float, maximum: float) -> float:
    """Return one bounded finite number while rejecting booleans."""

    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise EvaluationError(f"{label} must be numeric")
    result = float(value)
    if not math.isfinite(result) or not minimum <= result <= maximum:
        raise EvaluationError(f"{label} must be finite in the range {minimum}..{maximum}")
    return result


def validate_config(config: dict[str, Any]) -> dict[str, Any]:
    """Validate the compact population-search configuration and its bindings."""

    exact_keys(config, CONFIG_KEYS, "population config")
    if config["schema_version"] != "semantic-okf-ensemble-population-search/1.0":
        raise EvaluationError("population config schema_version differs")
    if config["status"] != "configured-not-run":
        raise EvaluationError("population config status must be configured-not-run")
    bindings = exact_keys(
        config["bindings"], {"frozen_benchmark", "ensemble_plan", "evaluation_contract"}, "bindings"
    )
    frozen_path, _ = repo_file(bindings["frozen_benchmark"], "frozen benchmark binding")
    plan_path, _ = repo_file(bindings["ensemble_plan"], "ensemble plan binding")
    repo_file(bindings["evaluation_contract"], "evaluation contract binding")
    validate_frozen(frozen_path)
    if frozen_path != FROZEN_MANIFEST.resolve():
        raise EvaluationError("population config does not bind the accepted frozen benchmark")
    if plan_path != ENSEMBLE_PLAN.resolve():
        raise EvaluationError("population config does not bind the ensemble plan")

    population = exact_keys(
        config["population"],
        {
            "size",
            "survivors",
            "offspring_per_generation",
            "repetitions_per_candidate",
            "plateau_generations",
            "maximum_generations",
        },
        "population",
    )
    expected_population = {
        "size": 10,
        "survivors": 2,
        "offspring_per_generation": 8,
        "repetitions_per_candidate": 3,
        "plateau_generations": 2,
        "maximum_generations": 6,
    }
    if population != expected_population:
        raise EvaluationError(f"population policy must be exactly {expected_population}")

    schema = exact_keys(
        config["result_schema"],
        {
            "schema_version",
            "exact_root_keys",
            "exact_repetition_keys",
            "hard_gate_keys",
            "objective_keys",
            "objective_range",
            "latency_range_ms",
        },
        "result_schema",
    )
    if schema["schema_version"] != "semantic-okf-ensemble-population-result/1.0":
        raise EvaluationError("population result schema_version differs")
    if set(schema["exact_root_keys"]) != RESULT_KEYS or len(schema["exact_root_keys"]) != len(RESULT_KEYS):
        raise EvaluationError("result root key declaration differs")
    if set(schema["exact_repetition_keys"]) != REPETITION_KEYS or len(schema["exact_repetition_keys"]) != len(REPETITION_KEYS):
        raise EvaluationError("result repetition key declaration differs")
    gates = schema["hard_gate_keys"]
    objectives = schema["objective_keys"]
    if not isinstance(gates, list) or not gates or len(set(gates)) != len(gates):
        raise EvaluationError("hard_gate_keys must be a unique nonempty array")
    if not isinstance(objectives, list) or not objectives or len(set(objectives)) != len(objectives):
        raise EvaluationError("objective_keys must be a unique nonempty array")
    if schema["objective_range"] != [0.0, 1.0] or schema["latency_range_ms"] != [0.0, 3600000.0]:
        raise EvaluationError("population numeric ranges differ")
    return config


def validate_generation(generation: dict[str, Any], config: dict[str, Any]) -> list[str]:
    """Validate a planned generation without accepting embedded scores."""

    exact_keys(generation, GENERATION_KEYS, "generation")
    if generation["schema_version"] != "semantic-okf-ensemble-population-generation/1.0":
        raise EvaluationError("generation schema_version differs")
    if generation["search_id"] != config["search_id"] or generation["generation"] != 0:
        raise EvaluationError("generation identity differs from the configured generation zero")
    if generation["status"] != "planned":
        raise EvaluationError("unevaluated generation status must be planned")
    candidates = generation["candidates"]
    if not isinstance(candidates, list) or len(candidates) != config["population"]["size"]:
        raise EvaluationError("generation must declare the configured population size")
    ids: list[str] = []
    for index, candidate in enumerate(candidates):
        exact_keys(candidate, CANDIDATE_KEYS, f"candidate {index}")
        expected_id = f"candidate-{index:02d}"
        if candidate["candidate_id"] != expected_id or candidate["status"] != "planned":
            raise EvaluationError(f"candidate {index} identity or status differs")
        for key in ("operator", "hypothesis", "mutation_scope"):
            if not isinstance(candidate[key], str) or not candidate[key].strip():
                raise EvaluationError(f"candidate {expected_id}.{key} must be nonempty")
        parents = candidate["parent_ids"]
        if not isinstance(parents, list) or any(not isinstance(parent, str) for parent in parents):
            raise EvaluationError(f"candidate {expected_id}.parent_ids must be a string array")
        if any(parent >= expected_id for parent in parents):
            raise EvaluationError(f"candidate {expected_id} parents must precede the candidate")
        ids.append(expected_id)
    return ids


def parse_results(values: Sequence[str], candidate_ids: Sequence[str]) -> dict[str, Path]:
    """Parse exact candidate=path arguments and require complete population coverage."""

    result: dict[str, Path] = {}
    for value in values:
        candidate_id, separator, raw_path = value.partition("=")
        if not separator or not raw_path:
            raise EvaluationError("--result must use candidate-id=PATH")
        if candidate_id in result:
            raise EvaluationError(f"duplicate result for {candidate_id}")
        result[candidate_id] = Path(raw_path).resolve(strict=True)
    expected = set(candidate_ids)
    actual = set(result)
    if actual != expected:
        raise EvaluationError(
            f"results must cover the complete population; missing={sorted(expected - actual)}, "
            f"unknown={sorted(actual - expected)}"
        )
    return result


def score_result(
    path: Path, candidate_id: str, config: dict[str, Any]
) -> dict[str, Any]:
    """Validate and aggregate three real repetitions for one candidate."""

    result = load_json(path)
    exact_keys(result, RESULT_KEYS, f"result {candidate_id}")
    schema = config["result_schema"]
    bindings = config["bindings"]
    expected_scalars = {
        "schema_version": schema["schema_version"],
        "candidate_id": candidate_id,
        "frozen_benchmark_sha256": bindings["frozen_benchmark"]["sha256"],
        "ensemble_plan_sha256": bindings["ensemble_plan"]["sha256"],
        "evaluation_contract_sha256": bindings["evaluation_contract"]["sha256"],
    }
    for key, expected in expected_scalars.items():
        if result[key] != expected:
            raise EvaluationError(f"result {candidate_id}.{key} differs")

    repetitions = result["repetitions"]
    expected_count = config["population"]["repetitions_per_candidate"]
    if not isinstance(repetitions, list) or len(repetitions) != expected_count:
        raise EvaluationError(f"result {candidate_id} must contain {expected_count} repetitions")
    gate_keys = schema["hard_gate_keys"]
    objective_keys = schema["objective_keys"]
    objective_rows: list[dict[str, float]] = []
    gate_rows: list[dict[str, bool]] = []
    latencies: list[float] = []
    ranking_hashes: list[str] = []
    for index, row in enumerate(repetitions, 1):
        exact_keys(row, REPETITION_KEYS, f"result {candidate_id} repetition {index}")
        if row["repetition"] != index:
            raise EvaluationError(f"result {candidate_id} repetition numbers must be ordered 1..3")
        ranking_hash = row["rankings_sha256"]
        if not isinstance(ranking_hash, str) or not HEX_SHA256.fullmatch(ranking_hash):
            raise EvaluationError(f"result {candidate_id} repetition {index} ranking hash is invalid")
        gates = exact_keys(row["hard_gates"], set(gate_keys), f"result {candidate_id} gates {index}")
        if any(type(gates[key]) is not bool for key in gate_keys):
            raise EvaluationError(f"result {candidate_id} hard gates must be booleans")
        objectives = exact_keys(
            row["objectives"], set(objective_keys), f"result {candidate_id} objectives {index}"
        )
        objective_rows.append(
            {key: finite(objectives[key], f"result {candidate_id}.{key}", 0.0, 1.0) for key in objective_keys}
        )
        latencies.append(
            finite(row["p95_latency_ms"], f"result {candidate_id}.p95_latency_ms", 0.0, 3600000.0)
        )
        gate_rows.append({key: gates[key] for key in gate_keys})
        ranking_hashes.append(ranking_hash)

    deterministic = len(set(ranking_hashes)) == 1
    aggregate_gates = {key: all(row[key] for row in gate_rows) for key in gate_keys}
    aggregate_gates["deterministic_rankings"] = (
        aggregate_gates.get("deterministic_rankings", False) and deterministic
    )
    aggregate_objectives = {key: mean(row[key] for row in objective_rows) for key in objective_keys}
    all_gates_pass = all(aggregate_gates.values())
    worst = min(aggregate_objectives.values())
    fitness = geometric_mean(aggregate_objectives.values()) if all_gates_pass else 0.0
    return {
        "candidate_id": candidate_id,
        "result_path": display_path(path),
        "result_sha256": sha256(path),
        "all_hard_gates_pass": all_gates_pass,
        "hard_gates": aggregate_gates,
        "objectives": aggregate_objectives,
        "worst_objective": worst,
        "fitness": fitness,
        "p95_latency_ms": max(latencies),
        "ranking_sha256": ranking_hashes[0] if deterministic else None,
    }


def render_markdown(report: dict[str, Any]) -> str:
    """Render a compact human-readable ranking without hiding gate failures."""

    lines = [
        "# Ensemble population ranking",
        "",
        f"Status: `{report['status']}`. Evaluated candidates: {report['candidate_count']}. ",
        "",
        "| Rank | Candidate | Gates | Worst objective | Fitness | P95 latency (ms) | Decision |",
        "| ---: | --- | --- | ---: | ---: | ---: | --- |",
    ]
    for row in report["ranking"]:
        lines.append(
            f"| {row['rank']} | `{row['candidate_id']}` | "
            f"{'pass' if row['all_hard_gates_pass'] else 'fail'} | "
            f"{row['worst_objective']:.8f} | {row['fitness']:.8f} | "
            f"{row['p95_latency_ms']:.4f} | {row['decision']} |"
        )
    lines.extend(
        [
            "",
            "A gate failure forces fitness to zero. A candidate is retained only when every hard gate passes.",
            "This report ranks supplied results; it does not claim causality or untouched holdout performance.",
            "",
        ]
    )
    return "\n".join(lines)


def rank(args: argparse.Namespace) -> dict[str, Any]:
    """Validate all inputs, aggregate candidate fitness, and choose at most two survivors."""

    config_path = args.config.resolve(strict=True)
    generation_path = args.generation.resolve(strict=True)
    config = validate_config(load_json(config_path))
    candidate_ids = validate_generation(load_json(generation_path), config)
    paths = parse_results(args.result, candidate_ids)
    rows = [score_result(paths[candidate_id], candidate_id, config) for candidate_id in candidate_ids]
    rows.sort(
        key=lambda row: (
            -int(row["all_hard_gates_pass"]),
            -row["worst_objective"],
            -row["fitness"],
            row["p95_latency_ms"],
            row["candidate_id"],
        )
    )
    eligible = [row for row in rows if row["all_hard_gates_pass"]]
    survivor_ids = {row["candidate_id"] for row in eligible[: config["population"]["survivors"]]}
    for rank_number, row in enumerate(rows, 1):
        row["rank"] = rank_number
        row["decision"] = "keep" if row["candidate_id"] in survivor_ids else "discard"
    return {
        "schema_version": "semantic-okf-ensemble-population-ranking/1.0",
        "status": "complete" if len(survivor_ids) == config["population"]["survivors"] else "insufficient-passing-candidates",
        "search_id": config["search_id"],
        "generation": 0,
        "candidate_count": len(rows),
        "survivors": sorted(survivor_ids),
        "bindings": config["bindings"],
        "inputs": {
            "config": {"path": display_path(config_path), "sha256": sha256(config_path)},
            "generation": {"path": display_path(generation_path), "sha256": sha256(generation_path)},
        },
        "ranking": rows,
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--generation", type=Path, required=True)
    parser.add_argument("--result", action="append", required=True, help="candidate-id=PATH; repeat for all candidates")
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-markdown", type=Path, required=True)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    """Run the ranking CLI with append-only outputs."""

    try:
        args = parse_args(argv)
        if args.output_json.exists() or args.output_markdown.exists():
            raise EvaluationError("refusing to overwrite an existing output")
        report = rank(args)
        write_new(args.output_json, json.dumps(report, indent=2, ensure_ascii=False) + "\n")
        write_new(args.output_markdown, render_markdown(report))
    except (EvaluationError, OSError) as exc:
        print(f"error: {exc}")
        return 2
    print(f"ranked {report['candidate_count']} candidates; status={report['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
