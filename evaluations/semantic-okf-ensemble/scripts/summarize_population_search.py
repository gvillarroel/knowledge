#!/usr/bin/env python3
"""Summarize and validate the completed deterministic ensemble population search."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from pathlib import Path
from typing import Any, Mapping, Sequence

from _evaluation import (
    ENSEMBLE_PLAN,
    FROZEN_MANIFEST,
    REPO_ROOT,
    EvaluationError,
    canonical_json,
    find_route,
    load_json,
    sha256,
    validate_frozen,
    write_new,
)


EVALUATION_ROOT = REPO_ROOT / "evaluations/semantic-okf-ensemble"
CONFIG_PATH = EVALUATION_ROOT / "population-search.json"
GENERATION_ZERO_PATH = EVALUATION_ROOT / "generation-000.json"
CONTRACT_PATH = EVALUATION_ROOT / "evaluation-contract.json"
CHECKED_JSON = EVALUATION_ROOT / "population-search-results.json"
CHECKED_MARKDOWN = EVALUATION_ROOT / "population-search-results.md"

CONFIG_KEYS = {
    "schema_version",
    "search_id",
    "status",
    "bindings",
    "population",
    "candidate_boundary",
    "result_schema",
    "selection",
    "completion",
}
GENERATION_KEYS = {
    "schema_version",
    "search_id",
    "generation",
    "status",
    "benchmark_visibility",
    "execution",
    "survivors",
    "candidates",
}
GENERATION_CANDIDATE_KEYS = {
    "candidate_id",
    "parent_ids",
    "operator",
    "policy",
    "tie_break",
    "gate_status",
    "fitness",
    "failed_metric_floors",
    "decision",
}
REPORT_KEYS = {
    "schema_version",
    "status",
    "search_id",
    "bindings",
    "selection_scope",
    "execution",
    "pre_winner_route_trace",
    "accepted_current_policy",
    "generations",
    "winner",
    "plateau",
    "rejected_variant_families",
    "validation",
}
RESULT_KEYS = {
    "schema_version",
    "status",
    "candidate_id",
    "fitness",
    "policy",
    "tie_break",
    "requests",
    "query_count_per_request",
    "effective_parallelism",
    "ranking_sha256",
    "metrics",
    "gates",
}
POLICY_KEYS = {"routes", "weights", "rrf_k", "protected_route", "promotion"}
PROMOTION_KEYS = {
    "route",
    "confirmation_routes",
    "confirmation_depth",
    "minimum_confirmations",
    "maximum_protected_rank",
}
METRIC_KEYS = {
    "all_recall_at_10",
    "all_mrr_at_10",
    "all_ndcg_at_10",
    "hard_recall_at_10",
    "hard_mrr_at_10",
    "hard_ndcg_at_10",
}
GATE_KEYS = {
    "deterministic_three_repetitions",
    "protected_set_preserved",
    "evidence_validity_inherited",
    "metric_floors",
}
HEX_SHA256 = re.compile(r"[0-9a-f]{64}\Z")
WINDOWS_ABSOLUTE = re.compile(r"^[A-Za-z]:[\\/]")
PROHIBITED_TIME_KEYS = {
    "timestamp",
    "generated_at",
    "recorded_at",
    "ranked_at",
    "recordedAt",
    "rankedAt",
}


def exact_keys(value: Any, expected: set[str], label: str) -> dict[str, Any]:
    """Require an object with one exact closed key set."""

    if not isinstance(value, dict):
        raise EvaluationError(f"{label} must be an object")
    actual = set(value)
    if actual != expected:
        raise EvaluationError(
            f"{label} uses a closed schema; missing={sorted(expected - actual)}, "
            f"unknown={sorted(actual - expected)}"
        )
    return value


def finite(value: Any, label: str, minimum: float, maximum: float) -> float:
    """Return one bounded finite number while rejecting booleans."""

    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise EvaluationError(f"{label} must be numeric")
    result = float(value)
    if not math.isfinite(result) or not minimum <= result <= maximum:
        raise EvaluationError(f"{label} must be finite in {minimum}..{maximum}")
    return result


def _binding(entry: Any, label: str) -> tuple[Path, str]:
    """Validate one repository-relative path and byte hash binding."""

    value = exact_keys(entry, {"path", "sha256"}, label)
    path_text = value["path"]
    expected = value["sha256"]
    if not isinstance(path_text, str) or not isinstance(expected, str):
        raise EvaluationError(f"{label} path and sha256 must be strings")
    path = (REPO_ROOT / path_text).resolve(strict=True)
    try:
        path.relative_to(REPO_ROOT.resolve())
    except ValueError as exc:
        raise EvaluationError(f"{label} escapes the repository") from exc
    if not HEX_SHA256.fullmatch(expected) or sha256(path) != expected:
        raise EvaluationError(f"{label} SHA-256 differs")
    return path, expected


def _string_array(value: Any, label: str, *, nonempty: bool = False) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(item, str) or not item for item in value):
        raise EvaluationError(f"{label} must be an array of nonempty strings")
    if nonempty and not value:
        raise EvaluationError(f"{label} must not be empty")
    if len(value) != len(set(value)):
        raise EvaluationError(f"{label} must be unique")
    return value


def validate_config(config: dict[str, Any]) -> dict[str, Any]:
    """Validate the completed search contract and current checked bindings."""

    exact_keys(config, CONFIG_KEYS, "population config")
    if config["schema_version"] != "semantic-okf-ensemble-population-search/1.1":
        raise EvaluationError("population config schema_version differs")
    if config["search_id"] != "semantic-okf-ensemble-offline-population-v1":
        raise EvaluationError("population config search_id differs")
    if config["status"] != "complete":
        raise EvaluationError("population config status must be complete")

    bindings = exact_keys(
        config["bindings"],
        {"frozen_benchmark", "ensemble_plan", "evaluation_contract", "raw_replay_report"},
        "population bindings",
    )
    frozen_path, _ = _binding(bindings["frozen_benchmark"], "frozen benchmark binding")
    plan_path, _ = _binding(bindings["ensemble_plan"], "ensemble plan binding")
    contract_path, _ = _binding(bindings["evaluation_contract"], "evaluation contract binding")
    if frozen_path != FROZEN_MANIFEST.resolve() or plan_path != ENSEMBLE_PLAN.resolve():
        raise EvaluationError("population config binds an unexpected frozen benchmark or ensemble plan")
    if contract_path != CONTRACT_PATH.resolve():
        raise EvaluationError("population config binds an unexpected evaluation contract")
    validate_frozen(frozen_path)
    raw_binding = exact_keys(bindings["raw_replay_report"], {"role", "sha256"}, "raw replay binding")
    if not isinstance(raw_binding["role"], str) or "Pre-winner" not in raw_binding["role"]:
        raise EvaluationError("raw replay binding must disclose its pre-winner role")
    if not isinstance(raw_binding["sha256"], str) or not HEX_SHA256.fullmatch(raw_binding["sha256"]):
        raise EvaluationError("raw replay report SHA-256 is invalid")

    population = exact_keys(
        config["population"],
        {
            "size",
            "survivors",
            "offspring_per_generation",
            "repetitions_per_candidate",
            "questions_per_repetition",
            "effective_parallelism",
            "plateau_generations",
            "maximum_generations",
            "completed_generations",
        },
        "population",
    )
    expected_population = {
        "size": 10,
        "survivors": 2,
        "offspring_per_generation": 8,
        "repetitions_per_candidate": 3,
        "questions_per_repetition": 40,
        "effective_parallelism": 1,
        "plateau_generations": 2,
        "maximum_generations": 6,
        "completed_generations": 4,
    }
    if population != expected_population:
        raise EvaluationError(f"population execution must be exactly {expected_population}")

    boundary = exact_keys(config["candidate_boundary"], {"allowed", "forbidden"}, "candidate boundary")
    _string_array(boundary["allowed"], "candidate boundary allowed", nonempty=True)
    _string_array(boundary["forbidden"], "candidate boundary forbidden", nonempty=True)

    schema = exact_keys(
        config["result_schema"],
        {"schema_version", "exact_root_keys", "gate_keys", "metric_keys", "policy_keys"},
        "candidate result schema",
    )
    if schema["schema_version"] != "semantic-okf-ensemble-population-candidate/1.0":
        raise EvaluationError("candidate result schema_version differs")
    declarations = {
        "exact_root_keys": RESULT_KEYS,
        "gate_keys": GATE_KEYS,
        "metric_keys": METRIC_KEYS,
        "policy_keys": POLICY_KEYS,
    }
    for key, expected in declarations.items():
        values = _string_array(schema[key], f"result schema {key}", nonempty=True)
        if set(values) != expected:
            raise EvaluationError(f"result schema {key} differs")

    selection = exact_keys(
        config["selection"],
        {
            "failed_gate_fitness",
            "passing_fitness",
            "ranking",
            "keep",
            "discard",
            "simplicity_tie_rule",
            "plateau_rule",
        },
        "selection",
    )
    if selection["failed_gate_fitness"] != 0.0 or selection["ranking"] != ["fitness_desc", "candidate_id_asc"]:
        raise EvaluationError("population ranking rule differs")
    if selection["keep"] != 2 or selection["discard"] != 8:
        raise EvaluationError("population keep/discard counts differ")
    if any(not isinstance(selection[key], str) or not selection[key] for key in ("passing_fitness", "simplicity_tie_rule", "plateau_rule")):
        raise EvaluationError("selection descriptions must be nonempty strings")

    completion = exact_keys(
        config["completion"],
        {"candidate_evaluations", "replay_requests", "question_rankings", "stop_reason", "compact_results"},
        "completion",
    )
    if completion["candidate_evaluations"] != 40 or completion["replay_requests"] != 120 or completion["question_rankings"] != 4800:
        raise EvaluationError("population completion totals differ")
    if completion["stop_reason"] != "two-generation-plateau":
        raise EvaluationError("population stop reason differs")
    compact = exact_keys(completion["compact_results"], {"json", "markdown"}, "compact result paths")
    if compact != {
        "json": "evaluations/semantic-okf-ensemble/population-search-results.json",
        "markdown": "evaluations/semantic-okf-ensemble/population-search-results.md",
    }:
        raise EvaluationError("compact result paths differ")
    return config


def _validate_policy_summary(value: Any, label: str) -> dict[str, Any]:
    policy = exact_keys(value, {"routes", "weights", "rrf_k"}, label)
    routes = _string_array(policy["routes"], f"{label}.routes", nonempty=True)
    weights = policy["weights"]
    if not isinstance(weights, list) or len(weights) != len(routes):
        raise EvaluationError(f"{label}.weights must align with routes")
    for index, weight in enumerate(weights):
        finite(weight, f"{label}.weights[{index}]", 0.01, 100.0)
    if isinstance(policy["rrf_k"], bool) or not isinstance(policy["rrf_k"], int) or policy["rrf_k"] < 0:
        raise EvaluationError(f"{label}.rrf_k must be a nonnegative integer")
    return policy


def validate_generation(generation: dict[str, Any], config: dict[str, Any]) -> list[str]:
    """Validate the compact completed generation-zero ledger."""

    exact_keys(generation, GENERATION_KEYS, "generation zero")
    if generation["schema_version"] != "semantic-okf-ensemble-population-generation/1.1":
        raise EvaluationError("generation zero schema_version differs")
    if generation["search_id"] != config["search_id"] or generation["generation"] != 0:
        raise EvaluationError("generation zero identity differs")
    if generation["status"] != "complete":
        raise EvaluationError("generation zero status must be complete")
    if not isinstance(generation["benchmark_visibility"], str) or "evaluator-only" not in generation["benchmark_visibility"]:
        raise EvaluationError("generation zero must disclose evaluator-only benchmark visibility")
    if generation["execution"] != {
        "candidate_count": 10,
        "repetitions_per_candidate": 3,
        "questions_per_repetition": 40,
        "effective_parallelism": 1,
    }:
        raise EvaluationError("generation zero execution facts differ")
    survivors = _string_array(generation["survivors"], "generation zero survivors", nonempty=True)
    if survivors != ["candidate-04", "candidate-06"]:
        raise EvaluationError("generation zero survivor identities differ")
    candidates = generation["candidates"]
    if not isinstance(candidates, list) or len(candidates) != 10:
        raise EvaluationError("generation zero must contain ten candidates")
    ids: list[str] = []
    kept: list[str] = []
    for index, candidate in enumerate(candidates):
        exact_keys(candidate, GENERATION_CANDIDATE_KEYS, f"generation zero candidate {index}")
        expected_id = f"candidate-{index:02d}"
        if candidate["candidate_id"] != expected_id or candidate["parent_ids"] != []:
            raise EvaluationError(f"generation zero candidate {index} identity or parents differ")
        operator = exact_keys(candidate["operator"], {"type", "focus", "hypothesis"}, f"{expected_id} operator")
        if any(not isinstance(operator[key], str) or not operator[key] for key in operator):
            raise EvaluationError(f"{expected_id} operator fields must be nonempty strings")
        _validate_policy_summary(candidate["policy"], f"{expected_id} policy")
        if candidate["tie_break"] not in {"paper_id", "consensus"}:
            raise EvaluationError(f"{expected_id} tie_break differs")
        if candidate["gate_status"] not in {"pass", "fail"}:
            raise EvaluationError(f"{expected_id} gate_status must be binary")
        fitness = finite(candidate["fitness"], f"{expected_id}.fitness", 0.0, 100.0)
        failures = _string_array(candidate["failed_metric_floors"], f"{expected_id} failed floors")
        if (candidate["gate_status"] == "pass") != (not failures and fitness > 0.0):
            raise EvaluationError(f"{expected_id} gate status, failures, and fitness disagree")
        if candidate["decision"] not in {"keep", "discard"}:
            raise EvaluationError(f"{expected_id} decision must be binary")
        if candidate["decision"] == "keep":
            kept.append(expected_id)
        ids.append(expected_id)
    if kept != survivors:
        raise EvaluationError("generation zero decisions differ from survivors")
    return ids


def _validate_full_policy(value: Any, label: str) -> dict[str, Any]:
    policy = exact_keys(value, POLICY_KEYS, label)
    routes = _string_array(policy["routes"], f"{label}.routes", nonempty=True)
    weights = policy["weights"]
    if not isinstance(weights, list) or len(weights) != len(routes):
        raise EvaluationError(f"{label}.weights must align with routes")
    for index, weight in enumerate(weights):
        finite(weight, f"{label}.weights[{index}]", 0.01, 100.0)
    if policy["protected_route"] != "adaptive" or "adaptive" not in routes:
        raise EvaluationError(f"{label} must protect the adaptive route")
    if isinstance(policy["rrf_k"], bool) or not isinstance(policy["rrf_k"], int) or policy["rrf_k"] < 0:
        raise EvaluationError(f"{label}.rrf_k must be a nonnegative integer")
    promotion = exact_keys(policy["promotion"], PROMOTION_KEYS, f"{label}.promotion")
    _string_array(promotion["confirmation_routes"], f"{label}.confirmation_routes", nonempty=True)
    if not isinstance(promotion["route"], str) or not promotion["route"]:
        raise EvaluationError(f"{label}.promotion.route must be nonempty")
    for key in ("confirmation_depth", "minimum_confirmations"):
        if isinstance(promotion[key], bool) or not isinstance(promotion[key], int) or promotion[key] < 1:
            raise EvaluationError(f"{label}.promotion.{key} must be a positive integer")
    if (
        isinstance(promotion["maximum_protected_rank"], bool)
        or not isinstance(promotion["maximum_protected_rank"], int)
        or promotion["maximum_protected_rank"] < 0
    ):
        raise EvaluationError(f"{label}.promotion.maximum_protected_rank must be nonnegative")
    return policy


def validate_candidate_result(result: dict[str, Any], expected_id: str, config: dict[str, Any]) -> dict[str, Any]:
    """Validate one actual candidate replay result and recompute its fitness."""

    exact_keys(result, RESULT_KEYS, f"candidate result {expected_id}")
    if result["schema_version"] != config["result_schema"]["schema_version"]:
        raise EvaluationError(f"candidate result {expected_id} schema_version differs")
    if result["candidate_id"] != expected_id or result["status"] not in {"pass", "fail"}:
        raise EvaluationError(f"candidate result {expected_id} identity or status differs")
    if result["tie_break"] not in {"paper_id", "consensus"}:
        raise EvaluationError(f"candidate result {expected_id} tie_break differs")
    _validate_full_policy(result["policy"], f"candidate result {expected_id}.policy")
    population = config["population"]
    if result["requests"] != population["repetitions_per_candidate"]:
        raise EvaluationError(f"candidate result {expected_id} request count differs")
    if result["query_count_per_request"] != population["questions_per_repetition"]:
        raise EvaluationError(f"candidate result {expected_id} query count differs")
    if result["effective_parallelism"] != population["effective_parallelism"]:
        raise EvaluationError(f"candidate result {expected_id} parallelism differs")
    hashes = result["ranking_sha256"]
    if not isinstance(hashes, list) or len(hashes) != 3 or any(not isinstance(value, str) or not HEX_SHA256.fullmatch(value) for value in hashes):
        raise EvaluationError(f"candidate result {expected_id} ranking hashes differ")
    metrics = exact_keys(result["metrics"], METRIC_KEYS, f"candidate result {expected_id}.metrics")
    metric_values = {key: finite(value, f"{expected_id}.{key}", 0.0, 1.0) for key, value in metrics.items()}
    gates = exact_keys(result["gates"], GATE_KEYS, f"candidate result {expected_id}.gates")
    for key in GATE_KEYS - {"metric_floors"}:
        if type(gates[key]) is not bool:
            raise EvaluationError(f"candidate result {expected_id}.{key} must be boolean")
    floors = exact_keys(gates["metric_floors"], METRIC_KEYS, f"candidate result {expected_id}.metric_floors")
    if any(type(value) is not bool for value in floors.values()):
        raise EvaluationError(f"candidate result {expected_id} floor outcomes must be booleans")
    if gates["deterministic_three_repetitions"] != (len(set(hashes)) == 1):
        raise EvaluationError(f"candidate result {expected_id} determinism gate differs")
    passed = all(gates[key] for key in GATE_KEYS - {"metric_floors"}) and all(floors.values())
    expected_status = "pass" if passed else "fail"
    expected_fitness = 100.0 * math.prod(metric_values.values()) ** (1.0 / len(metric_values)) if passed else 0.0
    if result["status"] != expected_status or not math.isclose(float(result["fitness"]), expected_fitness, rel_tol=0.0, abs_tol=1e-10):
        raise EvaluationError(f"candidate result {expected_id} status or recomputed fitness differs")
    finite(result["fitness"], f"candidate result {expected_id}.fitness", 0.0, 100.0)
    return result


def _portable(value: Any, label: str = "compact output") -> None:
    """Reject absolute paths and machine timestamps from checked compact output."""

    if isinstance(value, dict):
        for key, item in value.items():
            if key in PROHIBITED_TIME_KEYS:
                raise EvaluationError(f"{label} contains prohibited time key {key}")
            _portable(item, f"{label}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _portable(item, f"{label}[{index}]")
    elif isinstance(value, str):
        if WINDOWS_ABSOLUTE.match(value) or value.startswith("/") or value.startswith("file://"):
            raise EvaluationError(f"{label} contains an absolute machine path")


def _result_set_sha256(rows: list[tuple[str, Path]]) -> str:
    values = [{"candidate_id": candidate_id, "result_sha256": sha256(path)} for candidate_id, path in rows]
    return hashlib.sha256(canonical_json(values).encode("utf-8")).hexdigest()


def _raw_generation(raw_root: Path, generation_number: int, config: dict[str, Any]) -> dict[str, Any]:
    """Validate and compact one ignored generation without copying timestamps or paths."""

    generation_id = f"generation-{generation_number:03d}"
    root = raw_root / generation_id
    generation = load_json(root / "generation.json")
    ranking = load_json(root / "ranking.json")
    candidates = generation.get("candidates")
    if not isinstance(candidates, list) or len(candidates) != config["population"]["size"]:
        raise EvaluationError(f"raw {generation_id} must contain ten candidates")
    manifest_by_id = {row.get("candidateId"): row for row in candidates if isinstance(row, dict)}
    expected_ids = [f"candidate-{index:02d}" for index in range(10)]
    if sorted(manifest_by_id) != expected_ids:
        raise EvaluationError(f"raw {generation_id} candidate identities differ")
    rows: list[dict[str, Any]] = []
    result_paths: list[tuple[str, Path]] = []
    for candidate_id in expected_ids:
        candidate_root = root / "candidates" / candidate_id
        manifest = load_json(candidate_root / "candidate.json")
        if manifest.get("candidateId") != candidate_id or manifest.get("generation") != generation_id:
            raise EvaluationError(f"raw {generation_id}/{candidate_id} manifest identity differs")
        # The population helper's generation-zero skeleton retains generic seed
        # operators. The per-candidate manifest is the evaluated mutation record.
        # Later ranking logs also bind that per-candidate operator.
        result_path = candidate_root / "result.json"
        result = validate_candidate_result(load_json(result_path), candidate_id, config)
        result_paths.append((candidate_id, result_path))
        rows.append(
            {
                "variant": f"{generation_id}/{candidate_id}",
                "focus": manifest["operator"]["focus"],
                "hypothesis": manifest["operator"].get("hypothesis", "Carried validated survivor."),
                "status": result["status"],
                "fitness": result["fitness"],
                "policy": result["policy"],
                "tie_break": result["tie_break"],
                "metrics": result["metrics"],
                "gates": result["gates"],
                "ranking_sha256": result["ranking_sha256"][0],
            }
        )
    expected_order = sorted(rows, key=lambda row: (-float(row["fitness"]), row["variant"]))
    raw_ranking = ranking.get("ranking")
    if not isinstance(raw_ranking, list) or [row.get("candidateId") for row in raw_ranking] != [row["variant"].split("/")[1] for row in expected_order]:
        raise EvaluationError(f"raw {generation_id} ranking order differs")
    survivors = ranking.get("survivors")
    expected_survivors = [row["variant"].split("/")[1] for row in expected_order[:2]]
    if survivors != expected_survivors:
        raise EvaluationError(f"raw {generation_id} survivors differ")
    return {
        "generation": generation_number,
        "generation_id": generation_id,
        "candidate_count": len(rows),
        "pass_count": sum(row["status"] == "pass" for row in rows),
        "fail_count": sum(row["status"] == "fail" for row in rows),
        "survivors": [f"{generation_id}/{candidate_id}" for candidate_id in survivors],
        "best_variant": expected_order[0]["variant"],
        "best_fitness": expected_order[0]["fitness"],
        "result_set_sha256": _result_set_sha256(result_paths),
        "candidate_rows": rows,
    }


def _generation_zero_matches_checked(raw: dict[str, Any], checked: dict[str, Any]) -> None:
    """Bind the checked generation-zero ledger to the actual ignored results."""

    by_id = {row["variant"].split("/")[1]: row for row in raw["candidate_rows"]}
    raw_survivors = [value.split("/")[1] for value in raw["survivors"]]
    if checked["survivors"] != raw_survivors:
        raise EvaluationError("checked generation zero survivors differ from raw results")
    for row in checked["candidates"]:
        actual = by_id[row["candidate_id"]]
        if row["operator"]["focus"] != actual["focus"] or row["operator"]["hypothesis"] != actual["hypothesis"]:
            raise EvaluationError(f"checked generation zero operator differs for {row['candidate_id']}")
        expected_policy = {key: actual["policy"][key] for key in ("routes", "weights", "rrf_k")}
        if row["policy"] != expected_policy or row["tie_break"] != actual["tie_break"]:
            raise EvaluationError(f"checked generation zero policy differs for {row['candidate_id']}")
        failures = sorted(key for key, value in actual["gates"]["metric_floors"].items() if not value)
        expected_decision = "keep" if row["candidate_id"] in raw_survivors else "discard"
        if (
            row["gate_status"] != actual["status"]
            or not math.isclose(float(row["fitness"]), float(actual["fitness"]), rel_tol=0.0, abs_tol=1e-12)
            or row["failed_metric_floors"] != failures
            or row["decision"] != expected_decision
        ):
            raise EvaluationError(f"checked generation zero outcome differs for {row['candidate_id']}")


def _pre_winner_trace(raw_report: Path, config: dict[str, Any]) -> dict[str, Any]:
    """Validate the real pre-winner route trace used as replay input."""

    if sha256(raw_report) != config["bindings"]["raw_replay_report"]["sha256"]:
        raise EvaluationError("raw replay report SHA-256 differs")
    report = load_json(raw_report)
    route = find_route(report, "ensemble_quality")
    if route.get("query_count") != 40 or route.get("error_count") != 0:
        raise EvaluationError("raw replay route must contain forty successful queries")
    evidence = route.get("evidence_validity")
    if not isinstance(evidence, dict) or evidence.get("ratio") != 1.0 or evidence.get("invalid") != 0:
        raise EvaluationError("raw replay evidence validity differs")
    queries = route.get("queries")
    if not isinstance(queries, list) or len(queries) != 40:
        raise EvaluationError("raw replay query rows differ")
    policies = [row.get("ensemble_trace", {}).get("policy") for row in queries if isinstance(row, dict)]
    if len(policies) != 40 or any(policy != policies[0] for policy in policies):
        raise EvaluationError("raw replay route policy is not stable across forty questions")
    policy = policies[0]
    expected = {
        "algorithm": "protected-multisignal-paper-rerank-v1",
        "disabled_routes": {},
        "effective_scoring_routes": ["adaptive", "graph_fusion", "bm25", "embedding_hybrid"],
        "routes": ["adaptive", "graph_fusion", "bm25", "embedding_hybrid"],
        "rrf_k": 0,
        "weights": [1, 2, 3, 2],
    }
    if policy != expected:
        raise EvaluationError("raw replay route is not the declared pre-winner trace")
    return {
        "role": "Fixed component rankings, protected candidate sets, and inherited evidence-validity input for offline policy replay.",
        "accepted_policy": False,
        "algorithm": policy["algorithm"],
        "routes": policy["routes"],
        "weights": policy["weights"],
        "rrf_k": policy["rrf_k"],
        "question_count": route["query_count"],
        "error_count": route["error_count"],
        "evidence_validity": {
            "returned": evidence["returned"],
            "valid": evidence["valid"],
            "invalid": evidence["invalid"],
            "ratio": evidence["ratio"],
        },
        "sha256": sha256(raw_report),
    }


def _find(rows: list[dict[str, Any]], generation: int, focus: str) -> dict[str, Any]:
    matches = [row for row in rows[generation]["candidate_rows"] if row["focus"] == focus]
    if len(matches) != 1:
        raise EvaluationError(f"expected one generation {generation} candidate focused on {focus}")
    return matches[0]


def _rejected_families(generations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return compact, evidence-backed lessons from representative rejected variants."""

    failures = [_find(generations, 0, focus) for focus in ("adaptive-only", "semantic-heavy", "rrf-smoothing")]
    ablations = [_find(generations, 0, focus) for focus in ("embedding", "fast-policy", "no-promotion")]
    emphasis = [_find(generations, 0, focus) for focus in ("bm25-heavy", "graph-heavy")]
    local = [_find(generations, 2, focus) for focus in ("adaptive-minus-one", "graph-plus-one", "semantic-plus-one", "k-minus-one")]
    smoothing = [_find(generations, 3, focus) for focus in ("k-plus-one", "k-plus-two")]
    scaled = _find(generations, 3, "scaled-control")
    return [
        {
            "family": "hard-gate failures",
            "representatives": [row["variant"] for row in failures],
            "best_fitness": 0.0,
            "outcome": "discard",
            "reason": "Adaptive-only missed the all-question nDCG floor; semantic-heavy and the initial smoothed RRF missed the hard-ten nDCG floor.",
        },
        {
            "family": "route and promotion ablations",
            "representatives": [row["variant"] for row in ablations],
            "best_fitness": max(row["fitness"] for row in ablations),
            "outcome": "discard",
            "reason": "Removing semantic scoring, using the fast route set, or removing graph promotion all passed gates but ranked below the accepted policy.",
        },
        {
            "family": "single-signal emphasis",
            "representatives": [row["variant"] for row in emphasis],
            "best_fitness": max(row["fitness"] for row in emphasis),
            "outcome": "discard",
            "reason": "BM25-heavy and graph-heavy generation-zero policies did not beat the later balanced lexical policy.",
        },
        {
            "family": "local weight neighbors",
            "representatives": [row["variant"] for row in local],
            "best_fitness": max(row["fitness"] for row in local),
            "outcome": "discard",
            "reason": "Nearby adaptive, graph, semantic, BM25, and smoothing changes passed but reduced balanced fitness.",
        },
        {
            "family": "larger smoothing constants",
            "representatives": [row["variant"] for row in smoothing],
            "best_fitness": max(row["fitness"] for row in smoothing),
            "outcome": "discard",
            "reason": "RRF constants eight and nine were stable but scored below seven.",
        },
        {
            "family": "ratio-equivalent scaling",
            "representatives": [scaled["variant"]],
            "best_fitness": scaled["fitness"],
            "outcome": "discard",
            "reason": "Doubling every weight reproduced the winner exactly, so the simpler 4:1:5:1 representation won the deterministic simplicity tie.",
        },
    ]


def build_summary(
    raw_root: Path,
    raw_report: Path,
    config_path: Path = CONFIG_PATH,
    generation_path: Path = GENERATION_ZERO_PATH,
) -> dict[str, Any]:
    """Build the portable compact report from the completed ignored run."""

    config_path = config_path.resolve(strict=True)
    generation_path = generation_path.resolve(strict=True)
    raw_root = raw_root.resolve(strict=True)
    raw_report = raw_report.resolve(strict=True)
    config = validate_config(load_json(config_path))
    checked_generation = load_json(generation_path)
    validate_generation(checked_generation, config)
    trace = _pre_winner_trace(raw_report, config)
    generations = [_raw_generation(raw_root, number, config) for number in range(4)]
    _generation_zero_matches_checked(generations[0], checked_generation)

    plan = load_json(ENSEMBLE_PLAN)
    contract = load_json(CONTRACT_PATH)
    accepted_policy = plan["policies"]["quality"]
    winner = _find(generations, 1, "balanced-lexical-rrf")
    if winner["policy"] != accepted_policy or winner["tie_break"] != "consensus":
        raise EvaluationError("population winner differs from the accepted current quality policy")
    best_values = [float(row["best_fitness"]) for row in generations]
    if not (
        best_values[1] > best_values[0]
        and math.isclose(best_values[2], best_values[1], rel_tol=0.0, abs_tol=1e-12)
        and math.isclose(best_values[3], best_values[1], rel_tol=0.0, abs_tol=1e-12)
    ):
        raise EvaluationError("raw generations do not establish the required two-generation plateau")
    carried: list[dict[str, Any]] = []
    for generation_number in (2, 3):
        matches = [
            row
            for row in generations[generation_number]["candidate_rows"]
            if row["focus"] == "validated-winner"
            and row["policy"] == winner["policy"]
            and row["tie_break"] == winner["tie_break"]
        ]
        if len(matches) != 1:
            raise EvaluationError(
                f"expected one accepted-policy carryover in generation {generation_number}"
            )
        carried.append(matches[0])
    if any(not math.isclose(float(row["fitness"]), float(winner["fitness"]), rel_tol=0.0, abs_tol=1e-12) for row in carried):
        raise EvaluationError("winner carryovers changed fitness")

    generation_summaries = [
        {key: row[key] for key in (
            "generation",
            "candidate_count",
            "pass_count",
            "fail_count",
            "survivors",
            "best_variant",
            "best_fitness",
            "result_set_sha256",
        )}
        for row in generations
    ]
    result = {
        "schema_version": "semantic-okf-ensemble-population-search-results/1.0",
        "status": "pass",
        "search_id": config["search_id"],
        "bindings": {
            "frozen_benchmark": config["bindings"]["frozen_benchmark"],
            "ensemble_plan": config["bindings"]["ensemble_plan"],
            "evaluation_contract": config["bindings"]["evaluation_contract"],
            "population_config": {
                "path": config_path.relative_to(REPO_ROOT).as_posix(),
                "sha256": sha256(config_path),
            },
            "generation_zero": {
                "path": generation_path.relative_to(REPO_ROOT).as_posix(),
                "sha256": sha256(generation_path),
            },
            "raw_replay_report": config["bindings"]["raw_replay_report"],
        },
        "selection_scope": {
            "benchmark_role": "Frozen optimization and regression target; not an untouched holdout.",
            "method": "Deterministic offline replay over one fixed set of real component route rankings.",
            "retrieval_ranking_selected": True,
            "live_runtime_measured": False,
            "grounded_answers_evaluated": False,
            "skill_arena_causality_evaluated": False,
            "later_validation_rule": "Real runtime, grounded-answer, and isolated Skill Arena results are separate evidence and must not be inferred from this report.",
            "post_selection_change": "The final-03 reviewed semantic-claim coverage gate is non-ranking answer preparation. It was evaluated separately and does not alter the selected paper-ranking policy or replay metrics.",
        },
        "execution": {
            "completed_generations": 4,
            "candidates_per_generation": 10,
            "candidate_evaluations": 40,
            "repetitions_per_candidate": 3,
            "replay_requests": 120,
            "questions_per_repetition": 40,
            "question_rankings": 4800,
            "effective_parallelism": 1,
            "pass_outcomes": sum(row["pass_count"] for row in generations),
            "fail_outcomes": sum(row["fail_count"] for row in generations),
            "all_outcomes_binary": True,
        },
        "pre_winner_route_trace": trace,
        "accepted_current_policy": {
            "algorithm": "protected-multisignal-paper-rerank-v2",
            "policy": accepted_policy,
            "tie_break": contract["ranking_contract"]["stable_tie_break"],
            "promotion_description": "Promote the graph-lexical rank-one protected paper only with at least three confirmations among five routes within depth three.",
            "protected_candidate_set": "adaptive",
        },
        "generations": generation_summaries,
        "winner": {
            "variant": winner["variant"],
            "carried_as": [row["variant"] for row in carried],
            "decision": "keep",
            "fitness": winner["fitness"],
            "policy": winner["policy"],
            "tie_break": winner["tie_break"],
            "metrics": winner["metrics"],
            "ranking_sha256": winner["ranking_sha256"],
            "gates": winner["gates"],
            "evidence_validity": {
                **trace["evidence_validity"],
                "source": "inherited from the fixed pre-winner route trace",
            },
            "reason": "It passed every binary gate, produced MRR@10 of 1.0 on both cohorts, had the highest balanced six-metric fitness, and remained unchanged through two later generations.",
        },
        "plateau": {
            "required_non_improving_generations": 2,
            "best_fitness_by_generation": best_values,
            "last_improvement_generation": 1,
            "non_improving_generations_after_winner": [2, 3],
            "stop_reason": "two-generation-plateau",
            "satisfied": True,
        },
        "rejected_variant_families": _rejected_families(generations),
        "validation": {
            "closed_candidate_results": True,
            "deterministic_three_repetitions_for_every_candidate": True,
            "protected_set_preserved_for_every_candidate": True,
            "evidence_validity_inherited_from_bound_trace": True,
            "generation_zero_matches_raw_results": True,
            "current_plan_matches_winner": True,
            "portable_paths_only": True,
            "timestamps_omitted": True,
        },
    }
    validate_report(result, config, checked_generation)
    return result


def validate_report(report: dict[str, Any], config: dict[str, Any], generation: dict[str, Any]) -> dict[str, Any]:
    """Validate the checked compact report without requiring ignored raw files."""

    exact_keys(report, REPORT_KEYS, "population results")
    if report["schema_version"] != "semantic-okf-ensemble-population-search-results/1.0":
        raise EvaluationError("population results schema_version differs")
    if report["status"] != "pass" or report["search_id"] != config["search_id"]:
        raise EvaluationError("population results status or identity differs")
    _portable(report)
    bindings = exact_keys(
        report["bindings"],
        {"frozen_benchmark", "ensemble_plan", "evaluation_contract", "population_config", "generation_zero", "raw_replay_report"},
        "population result bindings",
    )
    if bindings["frozen_benchmark"] != config["bindings"]["frozen_benchmark"]:
        raise EvaluationError("population results frozen binding differs")
    if bindings["ensemble_plan"] != config["bindings"]["ensemble_plan"]:
        raise EvaluationError("population results plan binding differs")
    if bindings["evaluation_contract"] != config["bindings"]["evaluation_contract"]:
        raise EvaluationError("population results contract binding differs")
    if bindings["raw_replay_report"] != config["bindings"]["raw_replay_report"]:
        raise EvaluationError("population results raw replay binding differs")
    for key, path in (("population_config", CONFIG_PATH), ("generation_zero", GENERATION_ZERO_PATH)):
        bound, _ = _binding(bindings[key], f"population results {key}")
        if bound != path.resolve():
            raise EvaluationError(f"population results {key} path differs")

    execution = report["execution"]
    expected_execution = {
        "completed_generations": 4,
        "candidates_per_generation": 10,
        "candidate_evaluations": 40,
        "repetitions_per_candidate": 3,
        "replay_requests": 120,
        "questions_per_repetition": 40,
        "question_rankings": 4800,
        "effective_parallelism": 1,
        "pass_outcomes": 37,
        "fail_outcomes": 3,
        "all_outcomes_binary": True,
    }
    if execution != expected_execution:
        raise EvaluationError("population result execution totals differ")
    scope = report["selection_scope"]
    if scope.get("retrieval_ranking_selected") is not True or any(
        scope.get(key) is not False
        for key in ("live_runtime_measured", "grounded_answers_evaluated", "skill_arena_causality_evaluated")
    ):
        raise EvaluationError("population result selection boundary differs")
    trace = report["pre_winner_route_trace"]
    if trace.get("accepted_policy") is not False or trace.get("sha256") != config["bindings"]["raw_replay_report"]["sha256"]:
        raise EvaluationError("population result pre-winner trace boundary differs")
    if trace.get("weights") != [1, 2, 3, 2] or trace.get("rrf_k") != 0:
        raise EvaluationError("population result pre-winner trace policy differs")
    if trace.get("evidence_validity") != {"returned": 400, "valid": 400, "invalid": 0, "ratio": 1.0}:
        raise EvaluationError("population result inherited evidence validity differs")

    accepted = report["accepted_current_policy"]
    plan = load_json(ENSEMBLE_PLAN)
    contract = load_json(CONTRACT_PATH)
    if accepted.get("policy") != plan["policies"]["quality"]:
        raise EvaluationError("population result accepted policy differs from current plan")
    if accepted.get("tie_break") != contract["ranking_contract"]["stable_tie_break"]:
        raise EvaluationError("population result accepted tie order differs from the contract")
    winner = report["winner"]
    if winner.get("variant") != "generation-001/candidate-02" or winner.get("decision") != "keep":
        raise EvaluationError("population result winner identity or decision differs")
    expected_metrics = {
        "all_recall_at_10": 0.8381619769119769,
        "all_mrr_at_10": 1.0,
        "all_ndcg_at_10": 0.8520010047809912,
        "hard_recall_at_10": 0.9550000000000001,
        "hard_mrr_at_10": 1.0,
        "hard_ndcg_at_10": 0.8827017520626285,
    }
    if winner.get("metrics") != expected_metrics or not math.isclose(float(winner.get("fitness", -1)), 91.88915060557923, rel_tol=0.0, abs_tol=1e-12):
        raise EvaluationError("population result winner metrics or fitness differ")
    if winner.get("evidence_validity", {}).get("ratio") != 1.0:
        raise EvaluationError("population result winner evidence validity differs")
    generations = report["generations"]
    if not isinstance(generations, list) or [row.get("generation") for row in generations] != [0, 1, 2, 3]:
        raise EvaluationError("population result generation sequence differs")
    if [(row.get("pass_count"), row.get("fail_count")) for row in generations] != [(7, 3), (10, 0), (10, 0), (10, 0)]:
        raise EvaluationError("population result generation outcomes differ")
    plateau = report["plateau"]
    if plateau.get("satisfied") is not True or plateau.get("non_improving_generations_after_winner") != [2, 3]:
        raise EvaluationError("population result plateau differs")
    families = report["rejected_variant_families"]
    if not isinstance(families, list) or len(families) != 6 or any(row.get("outcome") != "discard" for row in families):
        raise EvaluationError("population result rejected-variant summary differs")
    if report["validation"] != {
        "closed_candidate_results": True,
        "deterministic_three_repetitions_for_every_candidate": True,
        "protected_set_preserved_for_every_candidate": True,
        "evidence_validity_inherited_from_bound_trace": True,
        "generation_zero_matches_raw_results": True,
        "current_plan_matches_winner": True,
        "portable_paths_only": True,
        "timestamps_omitted": True,
    }:
        raise EvaluationError("population result validation gates differ")
    validate_generation(generation, config)
    return report


def render_markdown(report: dict[str, Any]) -> str:
    """Render a portable English explanation of the compact result."""

    winner = report["winner"]
    metrics = winner["metrics"]
    lines = [
        "# Definitive ensemble population search",
        "",
        "Status: `pass`. The search selected a retrieval-ranking policy over the frozen forty-question benchmark.",
        "",
        "## Execution",
        "",
        "| Generations | Candidates per generation | Replays per candidate | Questions per replay | Effective parallelism | Candidate outcomes |",
        "| ---: | ---: | ---: | ---: | ---: | ---: |",
        f"| {report['execution']['completed_generations']} | {report['execution']['candidates_per_generation']} | {report['execution']['repetitions_per_candidate']} | {report['execution']['questions_per_repetition']} | {report['execution']['effective_parallelism']} | {report['execution']['candidate_evaluations']} |",
        "",
        f"The evaluator executed {report['execution']['replay_requests']} deterministic candidate replays, covering {report['execution']['question_rankings']} question rankings. Every candidate received a binary pass/fail gate outcome and a keep/discard decision. Thirty-seven candidate evaluations passed and three failed.",
        "",
        "## Winner",
        "",
        f"The accepted variant is `{winner['variant']}` with fitness `{winner['fitness']:.10f}`. It uses adaptive, graph-fusion, BM25, and embedding-hybrid weights `4:1:5:1`, RRF `k=7`, the consensus tie order, protected adaptive candidates, and the three-of-five graph-lexical promotion gate.",
        "",
        "| Cohort | Recall@10 | MRR@10 | nDCG@10 | Evidence validity |",
        "| --- | ---: | ---: | ---: | ---: |",
        f"| All 40 | {metrics['all_recall_at_10']:.10f} | {metrics['all_mrr_at_10']:.10f} | {metrics['all_ndcg_at_10']:.10f} | {winner['evidence_validity']['ratio']:.10f} |",
        f"| Hard 10 | {metrics['hard_recall_at_10']:.10f} | {metrics['hard_mrr_at_10']:.10f} | {metrics['hard_ndcg_at_10']:.10f} | {winner['evidence_validity']['ratio']:.10f} |",
        "",
        "## Generations and plateau",
        "",
        "| Generation | Pass | Fail | Best fitness | Best variant |",
        "| ---: | ---: | ---: | ---: | --- |",
    ]
    for row in report["generations"]:
        lines.append(
            f"| {row['generation']} | {row['pass_count']} | {row['fail_count']} | "
            f"{row['best_fitness']:.10f} | `{row['best_variant']}` |"
        )
    lines.extend(
        [
            "",
            "Generation one produced the final improvement. Generations two and three retained the same best fitness, satisfying the two-generation plateau. A ratio-equivalent doubled-weight candidate tied the winner in generation three, but the simpler 4:1:5:1 representation won the deterministic simplicity tie.",
            "",
            "## Rejected alternatives",
            "",
            "| Family | Best fitness | Outcome | Reason |",
            "| --- | ---: | --- | --- |",
        ]
    )
    for row in report["rejected_variant_families"]:
        lines.append(
            f"| {row['family']} | {row['best_fitness']:.10f} | {row['outcome']} | {row['reason']} |"
        )
    lines.extend(
        [
            "",
            "## Evidence boundary",
            "",
            "The bound raw report is a pre-winner real route trace using weights 1:2:3:2 and RRF k=0. The population evaluator reused only its component rankings, protected paper sets, and independently valid evidence rows to replay candidate ranking policies. It did not rerun the selected policy through the live semantic runtime.",
            "",
            "Final-03 adds bounded reviewed semantic-claim retrieval to the post-ranking `coverage-pack` operation. That gate prepares exact answer evidence only after the direct paper order has been selected; it does not change the paper-ranking routes, weights, RRF constant, protected candidate set, promotion rule, or tie order. The profile-gated MCP transport exposes the same coverage operation without altering that ranking policy. Accordingly, the selected ranking and its replay metrics remain applicable to final-03, while the accepted semantic coverage result is evaluated separately in `hard10-coverage-pack-multisignal-mcp-runtime-gate.json`.",
            "",
            "Accordingly, this report supports deterministic ranking selection on a frozen optimization target. It does not measure generated-answer correctness or completeness and is not causal Skill Arena evidence. Real runtime, grounded-answer, and isolated Skill Arena control/treatment results are separate evaluations.",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=CONFIG_PATH)
    parser.add_argument("--generation", type=Path, default=GENERATION_ZERO_PATH)
    parser.add_argument("--raw-root", type=Path)
    parser.add_argument("--raw-report", type=Path)
    parser.add_argument("--output-json", type=Path)
    parser.add_argument("--output-markdown", type=Path)
    parser.add_argument("--check", action="store_true", help="Validate checked compact artifacts and optionally reproduce them from raw inputs.")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        config = validate_config(load_json(args.config.resolve(strict=True)))
        generation = load_json(args.generation.resolve(strict=True))
        validate_generation(generation, config)
        if args.check:
            if args.output_json is not None or args.output_markdown is not None:
                raise EvaluationError("--check does not accept output paths")
            report = load_json(CHECKED_JSON)
            validate_report(report, config, generation)
            if CHECKED_MARKDOWN.read_text(encoding="utf-8") != render_markdown(report):
                raise EvaluationError("checked population markdown differs from deterministic rendering")
            if (args.raw_root is None) != (args.raw_report is None):
                raise EvaluationError("deep reproduction requires both --raw-root and --raw-report")
            if args.raw_root is not None:
                reproduced = build_summary(args.raw_root, args.raw_report, args.config, args.generation)
                if reproduced != report:
                    raise EvaluationError("checked population report differs from raw reproduction")
            print(json.dumps({"status": "pass", "winner": report["winner"]["variant"], "fitness": report["winner"]["fitness"]}))
            return 0
        if args.raw_root is None or args.raw_report is None or args.output_json is None or args.output_markdown is None:
            raise EvaluationError("generation requires --raw-root, --raw-report, --output-json, and --output-markdown")
        if args.output_json.exists() or args.output_markdown.exists():
            raise EvaluationError("refusing to overwrite an existing compact output")
        report = build_summary(args.raw_root, args.raw_report, args.config, args.generation)
        write_new(args.output_json, json.dumps(report, indent=2, ensure_ascii=False) + "\n")
        write_new(args.output_markdown, render_markdown(report))
    except (EvaluationError, OSError, ValueError) as exc:
        print(f"error: {exc}")
        return 2
    print(json.dumps({"status": "pass", "winner": report["winner"]["variant"], "fitness": report["winner"]["fitness"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
