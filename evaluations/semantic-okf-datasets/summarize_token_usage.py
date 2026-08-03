#!/usr/bin/env python3
"""Build a reproducible two-stage Semantic OKF token-usage report."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Mapping, Sequence

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
DEFAULT_EVIDENCE = HERE / "token-usage-evidence.json"
DEFAULT_JSON = (
    HERE / "reports/20260730-semantic-okf-token-usage.json"
)
DEFAULT_MARKDOWN = (
    HERE / "reports/20260730-semantic-okf-token-usage.md"
)
EVIDENCE_SCHEMA = "semantic-okf-token-usage-evidence/2.0"
REPORT_SCHEMA = "semantic-okf-token-usage-report/2.0"
REGISTERED_FAMILIES = {
    "adaptive",
    "classical",
    "embeddings",
    "ensemble",
    "entity-graph",
    "graphify",
    "legacy",
    "turso",
}


class TokenUsageError(ValueError):
    """Raised when pinned token evidence is missing or inconsistent."""


def load_json(path: Path) -> dict[str, Any]:
    """Load one JSON object with a path-specific diagnostic."""

    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise TokenUsageError(f"cannot read JSON object: {path}") from exc
    if not isinstance(value, dict):
        raise TokenUsageError(f"expected a JSON object: {path}")
    return value


def sha256_file(path: Path) -> str:
    """Hash one immutable evidence file."""

    return hashlib.sha256(path.read_bytes()).hexdigest()


def repo_path(
    value: object,
    label: str,
    *,
    must_exist: bool = True,
) -> Path:
    """Resolve one repository-relative evidence path without escaping."""

    if not isinstance(value, str) or not value:
        raise TokenUsageError(f"{label} must be a repository-relative path")
    relative = Path(value)
    if relative.is_absolute():
        raise TokenUsageError(f"{label} must not be absolute")
    path = (REPO / relative).resolve()
    try:
        path.relative_to(REPO.resolve())
    except ValueError as exc:
        raise TokenUsageError(f"{label} escapes the repository") from exc
    if must_exist and not path.is_file():
        raise TokenUsageError(f"{label} does not exist: {value}")
    return path


def pinned_json(
    record: Mapping[str, Any],
    path_key: str,
    digest_key: str,
) -> tuple[Path, dict[str, Any]]:
    """Load a JSON object only when its declared digest still matches."""

    path = repo_path(record.get(path_key), path_key)
    expected = record.get(digest_key)
    actual = sha256_file(path)
    if not isinstance(expected, str) or actual != expected:
        raise TokenUsageError(
            f"{path_key} digest mismatch: expected {expected}, got {actual}"
        )
    return path, load_json(path)


def token_count(value: object, label: str) -> int:
    """Require one non-negative integral Harbor token count."""

    if (
        not isinstance(value, int)
        or isinstance(value, bool)
        or value < 0
    ):
        raise TokenUsageError(f"{label} must be a non-negative integer")
    return value


def positive_count(value: object, label: str) -> int:
    """Require one positive integral denominator."""

    result = token_count(value, label)
    if result == 0:
        raise TokenUsageError(f"{label} must be positive")
    return result


def model_name(result: Mapping[str, Any]) -> str:
    """Read the fully qualified model name bound into a Harbor result."""

    config = result.get("config")
    agent = config.get("agent") if isinstance(config, Mapping) else None
    value = agent.get("model_name") if isinstance(agent, Mapping) else None
    if not isinstance(value, str) or not value:
        raise TokenUsageError("Harbor result has no bound model name")
    return value


def result_usage(result: Mapping[str, Any]) -> dict[str, int]:
    """Extract Harbor usage using input-includes-cache semantics."""

    agent = result.get("agent_result")
    if not isinstance(agent, Mapping):
        raise TokenUsageError("Harbor result has no agent_result")
    input_tokens = token_count(
        agent.get("n_input_tokens"), "n_input_tokens"
    )
    cache_tokens = token_count(
        agent.get("n_cache_tokens"), "n_cache_tokens"
    )
    output_tokens = token_count(
        agent.get("n_output_tokens"), "n_output_tokens"
    )
    if cache_tokens > input_tokens:
        raise TokenUsageError("cache tokens exceed input tokens")
    return {
        "input_tokens_including_cache": input_tokens,
        "cache_tokens_reported_separately": cache_tokens,
        "output_tokens": output_tokens,
        "total_tokens": input_tokens + output_tokens,
    }


def declared_usage(record: Mapping[str, Any]) -> dict[str, int]:
    """Validate one compact usage snapshot from the evidence manifest."""

    usage = record.get("usage")
    if not isinstance(usage, Mapping):
        raise TokenUsageError("build trial has no compact usage snapshot")
    input_tokens = token_count(
        usage.get("input_tokens_including_cache"),
        "input_tokens_including_cache",
    )
    cache_tokens = token_count(
        usage.get("cache_tokens_reported_separately"),
        "cache_tokens_reported_separately",
    )
    output_tokens = token_count(
        usage.get("output_tokens"), "output_tokens"
    )
    total_tokens = token_count(
        usage.get("total_tokens"), "total_tokens"
    )
    if (
        cache_tokens > input_tokens
        or total_tokens != input_tokens + output_tokens
    ):
        raise TokenUsageError(
            "compact usage violates Harbor token semantics"
        )
    return {
        "input_tokens_including_cache": input_tokens,
        "cache_tokens_reported_separately": cache_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
    }


def mean_usage(
    rows: Sequence[Mapping[str, Any]],
    denominator: int,
) -> dict[str, float]:
    """Compute weighted means over one explicit unit denominator."""

    if denominator <= 0:
        raise TokenUsageError("token mean denominator must be positive")
    fields = (
        "input_tokens_including_cache",
        "cache_tokens_reported_separately",
        "output_tokens",
        "total_tokens",
    )
    return {
        f"mean_{field}": (
            sum(token_count(row.get(field), field) for row in rows)
            / denominator
        )
        for field in fields
    }


def _expected_gates(
    result: Mapping[str, Any],
    expected: Mapping[str, Any],
    label: str,
) -> None:
    verifier = result.get("verifier_result")
    rewards = (
        verifier.get("rewards")
        if isinstance(verifier, Mapping)
        else None
    )
    if not isinstance(rewards, Mapping):
        raise TokenUsageError(f"{label} has no verifier rewards")
    for name, value in expected.items():
        if rewards.get(name) != value:
            raise TokenUsageError(
                f"{label} gate {name} is {rewards.get(name)!r}, "
                f"expected {value!r}"
            )


def build_folder_usage(
    evidence: Mapping[str, Any],
) -> dict[str, Any]:
    """Summarize historical builder-only trials per generated folder."""

    methods = evidence.get("build_methodologies")
    if not isinstance(methods, list) or not methods:
        raise TokenUsageError("build_methodologies must be a non-empty list")

    method_rows: list[dict[str, Any]] = []
    trial_evidence: list[dict[str, Any]] = []
    for method in methods:
        if not isinstance(method, Mapping):
            raise TokenUsageError("build methodology must be an object")
        methodology = method.get("methodology")
        label = method.get("label")
        expected_model = method.get("model")
        expected_gates = method.get("expected_gates")
        trials = method.get("trials")
        if (
            not isinstance(methodology, str)
            or not methodology
            or not isinstance(label, str)
            or not label
            or not isinstance(expected_model, str)
            or not expected_model
            or not isinstance(expected_gates, Mapping)
            or not isinstance(trials, list)
            or not trials
        ):
            raise TokenUsageError(
                f"invalid build methodology record: {methodology!r}"
            )

        usage_rows: list[dict[str, int]] = []
        folder_count = 0
        for index, trial in enumerate(trials):
            if not isinstance(trial, Mapping):
                raise TokenUsageError(
                    f"{methodology} trial {index} must be an object"
                )
            path = repo_path(
                trial.get("result_path"),
                "result_path",
                must_exist=False,
            )
            expected_digest = trial.get("result_sha256")
            if (
                not isinstance(expected_digest, str)
                or len(expected_digest) != 64
            ):
                raise TokenUsageError(
                    f"{methodology} trial {index} has no result digest"
                )
            expected_task = trial.get("task_name")
            usage = declared_usage(trial)
            raw_result_available = path.is_file()
            if raw_result_available:
                actual_digest = sha256_file(path)
                if actual_digest != expected_digest:
                    raise TokenUsageError(
                        f"result_path digest mismatch: expected "
                        f"{expected_digest}, got {actual_digest}"
                    )
                result = load_json(path)
                if result.get("task_name") != expected_task:
                    raise TokenUsageError(
                        f"{methodology} task identity drifted at {path}"
                    )
                actual_model = model_name(result)
                if actual_model != expected_model:
                    raise TokenUsageError(
                        f"{methodology} model is {actual_model}, "
                        f"expected {expected_model}"
                    )
                _expected_gates(
                    result,
                    expected_gates,
                    f"{methodology} trial {index}",
                )
                if result_usage(result) != usage:
                    raise TokenUsageError(
                        f"{methodology} compact usage differs from {path}"
                    )
            folders = positive_count(
                trial.get("generated_folders"), "generated_folders"
            )
            usage_rows.append(usage)
            folder_count += folders
            trial_evidence.append(
                {
                    "methodology": methodology,
                    "task_name": expected_task,
                    "result_path": path.relative_to(REPO).as_posix(),
                    "result_sha256": expected_digest,
                    "generated_folders": folders,
                    "usage": usage,
                }
            )

        method_rows.append(
            {
                "methodology": methodology,
                "label": label,
                "model": expected_model,
                "strictly_qualified": bool(
                    method.get("strictly_qualified")
                ),
                "qualification": method.get("qualification"),
                "trial_count": len(usage_rows),
                "generated_folder_count": folder_count,
                **mean_usage(usage_rows, folder_count),
                "mean_total_tokens_per_builder_trial": (
                    sum(row["total_tokens"] for row in usage_rows)
                    / len(usage_rows)
                ),
            }
        )

    models = {row["model"] for row in method_rows}
    if len(models) != 1:
        raise TokenUsageError(
            "build rollup would mix different model contracts"
        )
    all_usage = [
        item["usage"] for item in trial_evidence
    ]
    all_folders = sum(
        int(item["generated_folders"]) for item in trial_evidence
    )
    qualified_names = {
        row["methodology"]
        for row in method_rows
        if row["strictly_qualified"]
    }
    qualified_evidence = [
        item
        for item in trial_evidence
        if item["methodology"] in qualified_names
    ]
    qualified_usage = [item["usage"] for item in qualified_evidence]
    qualified_folders = sum(
        int(item["generated_folders"])
        for item in qualified_evidence
    )
    return {
        "unit": "one generated knowledge folder",
        "model": next(iter(models)),
        "methodologies": method_rows,
        "all_measured_rollup": {
            "methodology_count": len(method_rows),
            "trial_count": len(trial_evidence),
            "generated_folder_count": all_folders,
            **mean_usage(all_usage, all_folders),
        },
        "strictly_qualified_rollup": {
            "methodology_count": len(qualified_names),
            "trial_count": len(qualified_evidence),
            "generated_folder_count": qualified_folders,
            **mean_usage(qualified_usage, qualified_folders),
        },
        "trials": trial_evidence,
    }


def _matrix_contract(
    record: Mapping[str, Any],
    *,
    mode: str,
) -> tuple[str, str, str]:
    """Validate the shared registered-strategy execution contract."""

    if (
        record.get("dataset_id") != "graphrag-papers-40"
        or record.get("mode") != mode
        or record.get("family_count") != len(REGISTERED_FAMILIES)
    ):
        raise TokenUsageError(f"registered {mode} matrix identity drift")
    model = record.get("model")
    pi_version = record.get("pi_version")
    thinking = record.get("thinking")
    if any(
        not isinstance(value, str) or not value
        for value in (model, pi_version, thinking)
    ):
        raise TokenUsageError(
            f"registered {mode} execution contract is incomplete"
        )
    return model, pi_version, thinking


def _verify_compact_result(
    trial: Mapping[str, Any],
    *,
    expected_model: str,
    expected_task: str,
    expected_usage: Mapping[str, int],
    expected_gates: Mapping[str, Any] | None = None,
    expected_error: bool | None = None,
) -> tuple[Path, bool]:
    """Verify a compact trial against raw Harbor evidence when available."""

    path = repo_path(
        trial.get("result_path"),
        "result_path",
        must_exist=False,
    )
    digest = trial.get("result_sha256")
    if not isinstance(digest, str) or len(digest) != 64:
        raise TokenUsageError(f"trial has no valid result digest: {path}")
    available = path.is_file()
    if not available:
        return path, False
    if sha256_file(path) != digest:
        raise TokenUsageError(f"raw result digest drift: {path}")
    result = load_json(path)
    if result.get("task_name") != expected_task:
        raise TokenUsageError(f"raw task identity drift: {path}")
    if model_name(result) != expected_model:
        raise TokenUsageError(f"raw model identity drift: {path}")
    if result_usage(result) != expected_usage:
        raise TokenUsageError(f"compact usage differs from raw result: {path}")
    if expected_gates is not None:
        _expected_gates(result, expected_gates, str(path))
    if (
        expected_error is not None
        and (result.get("exception_info") is not None) != expected_error
    ):
        raise TokenUsageError(f"compact error state differs from raw result: {path}")
    return path, True


def _verify_compact_builder_diagnostics(
    trial: Mapping[str, Any],
    *,
    methodology: str,
    expected_tree_sha256: str,
) -> tuple[Path, bool]:
    """Verify optional raw diagnostics for one compact builder result."""

    path = repo_path(
        trial.get("diagnostics_path"),
        "diagnostics_path",
        must_exist=False,
    )
    digest = trial.get("diagnostics_sha256")
    if not isinstance(digest, str) or len(digest) != 64:
        raise TokenUsageError(
            f"builder trial has no valid diagnostics digest: {path}"
        )
    if not path.is_file():
        return path, False
    if sha256_file(path) != digest:
        raise TokenUsageError(f"raw diagnostics digest drift: {path}")
    diagnostics = load_json(path)
    bundles = diagnostics.get("bundles")
    if (
        diagnostics.get("schema_version")
        != "semantic-okf-builder-token-diagnostics/2.0"
        or diagnostics.get("status") != "qualified-single-folder"
        or diagnostics.get("family") != methodology
        or not isinstance(bundles, list)
        or len(bundles) != 1
        or not isinstance(bundles[0], Mapping)
        or bundles[0].get("tree_sha256") != expected_tree_sha256
    ):
        raise TokenUsageError(f"raw builder diagnostics drift: {path}")
    return path, True


def _ranked(
    rows: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Return ascending total-token ranks with deterministic tie handling."""

    ordered = sorted(
        rows,
        key=lambda row: (
            float(row["mean_total_tokens"]),
            str(row["methodology"]),
        ),
    )
    return [
        {**dict(row), "token_rank_low_to_high": index}
        for index, row in enumerate(ordered, start=1)
    ]


def registered_build_usage(
    evidence: Mapping[str, Any],
) -> dict[str, Any]:
    """Summarize the complete same-contract eight-family builder matrix."""

    record = evidence.get("registered_build_matrix")
    if not isinstance(record, Mapping):
        raise TokenUsageError("registered_build_matrix must be an object")
    model, pi_version, thinking = _matrix_contract(
        record, mode="builder-token"
    )
    families = record.get("families")
    replicates = positive_count(
        record.get("replicates_per_family"),
        "replicates_per_family",
    )
    folders_per_replicate = positive_count(
        record.get("generated_folders_per_replicate"),
        "generated_folders_per_replicate",
    )
    if not isinstance(families, list) or len(families) != len(
        REGISTERED_FAMILIES
    ):
        raise TokenUsageError("registered builder family rows are incomplete")

    rows: list[dict[str, Any]] = []
    trial_evidence: list[dict[str, Any]] = []
    observed_families: set[str] = set()
    for family in families:
        if not isinstance(family, Mapping):
            raise TokenUsageError("registered builder family must be an object")
        methodology = family.get("methodology")
        label = family.get("label")
        trials = family.get("trials")
        cross_replicate_tree_sha256 = family.get(
            "cross_replicate_tree_sha256"
        )
        if (
            not isinstance(methodology, str)
            or methodology in observed_families
            or not isinstance(label, str)
            or not isinstance(trials, list)
            or len(trials) != replicates
            or not isinstance(cross_replicate_tree_sha256, str)
            or len(cross_replicate_tree_sha256) != 64
        ):
            raise TokenUsageError("invalid registered builder family row")
        observed_families.add(methodology)
        usage_rows: list[dict[str, int]] = []
        qualified_count = 0
        raw_count = 0
        for trial in trials:
            if not isinstance(trial, Mapping):
                raise TokenUsageError("registered builder trial must be an object")
            usage = declared_usage(trial)
            task_name = trial.get("task_name")
            expected_gates = trial.get("expected_gates")
            output_tree_sha256 = trial.get("output_tree_sha256")
            if (
                not isinstance(task_name, str)
                or not isinstance(expected_gates, Mapping)
                or output_tree_sha256 != cross_replicate_tree_sha256
            ):
                raise TokenUsageError(
                    f"{methodology} builder trial contract is incomplete"
                )
            folders = positive_count(
                trial.get("generated_folders"),
                "generated_folders",
            )
            if folders != folders_per_replicate:
                raise TokenUsageError(
                    f"{methodology} generated-folder denominator drift"
                )
            path, available = _verify_compact_result(
                trial,
                expected_model=model,
                expected_task=task_name,
                expected_usage=usage,
                expected_gates=expected_gates,
                expected_error=False,
            )
            raw_count += int(available)
            diagnostics_path, diagnostics_available = (
                _verify_compact_builder_diagnostics(
                    trial,
                    methodology=methodology,
                    expected_tree_sha256=cross_replicate_tree_sha256,
                )
            )
            qualified = trial.get("qualified") is True
            qualified_count += int(qualified)
            usage_rows.append(usage)
            trial_evidence.append(
                {
                    "methodology": methodology,
                    "replicate": trial.get("replicate"),
                    "task_name": task_name,
                    "result_path": path.relative_to(REPO).as_posix(),
                    "result_sha256": trial["result_sha256"],
                    "diagnostics_path": diagnostics_path.relative_to(
                        REPO
                    ).as_posix(),
                    "diagnostics_sha256": trial["diagnostics_sha256"],
                    "diagnostics_available": diagnostics_available,
                    "output_tree_sha256": output_tree_sha256,
                    "generated_folders": folders,
                    "qualified": qualified,
                    "usage": usage,
                }
            )
        folder_count = replicates * folders_per_replicate
        rows.append(
            {
                "methodology": methodology,
                "label": label,
                "model": model,
                "builder_call_count": replicates,
                "generated_folder_count": folder_count,
                "qualified_builder_call_count": qualified_count,
                "raw_result_count": raw_count,
                "cross_replicate_tree_sha256": (
                    cross_replicate_tree_sha256
                ),
                "replicates_byte_identical": True,
                **mean_usage(usage_rows, folder_count),
                "mean_total_tokens_per_builder_call": (
                    sum(row["total_tokens"] for row in usage_rows)
                    / replicates
                ),
            }
        )
    if observed_families != REGISTERED_FAMILIES:
        raise TokenUsageError("registered builder family identity set drift")
    ranked = _ranked(rows)
    all_usage = [trial["usage"] for trial in trial_evidence]
    all_folders = sum(
        int(trial["generated_folders"]) for trial in trial_evidence
    )
    return {
        "unit": "one generated knowledge folder",
        "dataset_id": record["dataset_id"],
        "model": model,
        "pi_version": pi_version,
        "thinking": thinking,
        "runtime_image_id": record.get("runtime_image_id"),
        "family_count": len(ranked),
        "new_model_calls": token_count(
            record.get("new_model_calls"), "new_model_calls"
        ),
        "methodologies": ranked,
        "lowest_token_methodology": ranked[0],
        "highest_token_methodology": ranked[-1],
        "overall": {
            "builder_call_count": len(trial_evidence),
            "generated_folder_count": all_folders,
            **mean_usage(all_usage, all_folders),
        },
        "trials": trial_evidence,
    }


def registered_consultation_usage(
    evidence: Mapping[str, Any],
) -> dict[str, Any]:
    """Summarize the common six-query matrix for all eight consultants."""

    record = evidence.get("registered_consultation_matrix")
    if not isinstance(record, Mapping):
        raise TokenUsageError(
            "registered_consultation_matrix must be an object"
        )
    model, pi_version, thinking = _matrix_contract(
        record, mode="consult-only"
    )
    question_ids = record.get("question_ids")
    queries_per_family = positive_count(
        record.get("queries_per_family"),
        "queries_per_family",
    )
    families = record.get("families")
    if (
        record.get("cohort") != "holdout"
        or not isinstance(question_ids, list)
        or len(question_ids) != queries_per_family
        or len(set(question_ids)) != queries_per_family
        or not isinstance(families, list)
        or len(families) != len(REGISTERED_FAMILIES)
    ):
        raise TokenUsageError(
            "registered consultation matrix is incomplete"
        )

    rows: list[dict[str, Any]] = []
    trial_evidence: list[dict[str, Any]] = []
    observed_families: set[str] = set()
    for family in families:
        if not isinstance(family, Mapping):
            raise TokenUsageError(
                "registered consultation family must be an object"
            )
        methodology = family.get("methodology")
        label = family.get("label")
        trials = family.get("trials")
        if (
            not isinstance(methodology, str)
            or methodology in observed_families
            or not isinstance(label, str)
            or not isinstance(trials, list)
            or len(trials) != queries_per_family
        ):
            raise TokenUsageError("invalid consultation family row")
        observed_families.add(methodology)
        by_question: dict[str, Mapping[str, Any]] = {}
        for trial in trials:
            if not isinstance(trial, Mapping):
                raise TokenUsageError(
                    "registered consultation trial must be an object"
                )
            identifier = trial.get("question_id")
            if (
                not isinstance(identifier, str)
                or identifier in by_question
            ):
                raise TokenUsageError(
                    f"{methodology} consultation question identity drift"
                )
            by_question[identifier] = trial
        if set(by_question) != set(question_ids):
            raise TokenUsageError(
                f"{methodology} does not contain the fixed question set"
            )

        usage_rows: list[dict[str, int]] = []
        complete_rows: list[dict[str, int]] = []
        runtime_errors = 0
        raw_count = 0
        for identifier in question_ids:
            trial = by_question[identifier]
            usage = declared_usage(trial)
            task_name = trial.get("task_name")
            runtime_error = trial.get("runtime_error")
            if (
                not isinstance(task_name, str)
                or not isinstance(runtime_error, bool)
            ):
                raise TokenUsageError(
                    f"{methodology}/{identifier} trial contract is incomplete"
                )
            path, available = _verify_compact_result(
                trial,
                expected_model=model,
                expected_task=task_name,
                expected_usage=usage,
                expected_error=runtime_error,
            )
            raw_count += int(available)
            runtime_errors += int(runtime_error)
            usage_rows.append(usage)
            if not runtime_error:
                complete_rows.append(usage)
            trial_evidence.append(
                {
                    "methodology": methodology,
                    "question_id": identifier,
                    "task_name": task_name,
                    "result_path": path.relative_to(REPO).as_posix(),
                    "result_sha256": trial["result_sha256"],
                    "runtime_error": runtime_error,
                    "exception_type": trial.get("exception_type"),
                    "usage": usage,
                }
            )
        complete_count = len(complete_rows)
        row: dict[str, Any] = {
            "methodology": methodology,
            "label": label,
            "model": model,
            "submitted_query_count": queries_per_family,
            "runtime_error_count": runtime_errors,
            "complete_query_count": complete_count,
            "raw_result_count": raw_count,
            **mean_usage(usage_rows, queries_per_family),
        }
        if complete_count:
            row["complete_response_usage"] = {
                "complete_query_count": complete_count,
                **mean_usage(complete_rows, complete_count),
            }
        else:
            row["complete_response_usage"] = None
        rows.append(row)
    if observed_families != REGISTERED_FAMILIES:
        raise TokenUsageError("registered consultation family identity set drift")
    ranked = _ranked(rows)
    zero_error_rows = _ranked(
        [row for row in rows if row["runtime_error_count"] == 0]
    )
    all_usage = [trial["usage"] for trial in trial_evidence]
    all_queries = len(trial_evidence)
    return {
        "unit": "one submitted consult-only Harbor query",
        "dataset_id": record["dataset_id"],
        "cohort": record["cohort"],
        "question_ids": question_ids,
        "model": model,
        "pi_version": pi_version,
        "thinking": thinking,
        "family_count": len(ranked),
        "source_campaign": record.get("source_campaign"),
        "fairness_basis": record.get("fairness_basis"),
        "methodologies": ranked,
        "lowest_observed_submitted_cost": ranked[0],
        "highest_observed_submitted_cost": ranked[-1],
        "zero_runtime_error_methodologies": zero_error_rows,
        "lowest_zero_error_methodology": (
            zero_error_rows[0] if zero_error_rows else None
        ),
        "highest_zero_error_methodology": (
            zero_error_rows[-1] if zero_error_rows else None
        ),
        "overall": {
            "submitted_query_count": all_queries,
            "runtime_error_count": sum(
                int(row["runtime_error_count"]) for row in rows
            ),
            **mean_usage(all_usage, all_queries),
        },
        "trials": trial_evidence,
    }


def direct_retrieval_usage(
    evidence: Mapping[str, Any],
) -> dict[str, Any]:
    """Report the zero-LLM-token unit for every deterministic retrieval route."""

    record = evidence.get("direct_retrieval_routes")
    if not isinstance(record, Mapping):
        raise TokenUsageError("direct_retrieval_routes must be an object")
    path, comparison = pinned_json(
        record,
        "comparison_path",
        "comparison_sha256",
    )
    routes = record.get("routes")
    alternatives = comparison.get("alternatives")
    route_count = positive_count(record.get("route_count"), "route_count")
    if (
        not isinstance(routes, list)
        or len(routes) != route_count
        or not isinstance(alternatives, list)
        or len(alternatives) != route_count
    ):
        raise TokenUsageError("direct-retrieval route inventory is incomplete")
    expected = [
        {
            "strategy": alternative.get("id"),
            "label": alternative.get("label"),
        }
        for alternative in alternatives
        if isinstance(alternative, Mapping)
    ]
    if routes != expected:
        raise TokenUsageError("direct-retrieval route inventory drift")
    calls = token_count(
        record.get("llm_calls_per_retrieval"),
        "llm_calls_per_retrieval",
    )
    tokens = token_count(
        record.get("llm_tokens_per_retrieval"),
        "llm_tokens_per_retrieval",
    )
    if calls != 0 or tokens != 0:
        raise TokenUsageError(
            "deterministic direct retrieval must not claim LLM usage"
        )
    return {
        "unit": "one deterministic direct-retrieval helper invocation",
        "strategy_count": route_count,
        "llm_calls_per_retrieval": calls,
        "llm_tokens_per_retrieval": tokens,
        "scope": record.get("scope"),
        "strategies": routes,
        "source": {
            "path": path.relative_to(REPO).as_posix(),
            "sha256": sha256_file(path),
        },
    }


def resource_total(
    cell: Mapping[str, Any],
    resource: str,
) -> tuple[int, int]:
    """Read one integral aggregate resource total and observation count."""

    resources = cell.get("resources")
    measure = (
        resources.get(resource)
        if isinstance(resources, Mapping)
        else None
    )
    if not isinstance(measure, Mapping):
        raise TokenUsageError(f"campaign cell has no {resource}")
    total = measure.get("total")
    observed = measure.get("observed_trials")
    if (
        not isinstance(total, (int, float))
        or isinstance(total, bool)
        or not float(total).is_integer()
    ):
        raise TokenUsageError(f"{resource} total is not integral")
    return int(total), positive_count(observed, f"{resource} observed")


def controlled_consultation_usage(
    evidence: Mapping[str, Any],
) -> dict[str, Any]:
    """Summarize the balanced same-model live consultation pilot."""

    record = evidence.get("controlled_consultation")
    if not isinstance(record, Mapping):
        raise TokenUsageError("controlled_consultation must be an object")
    report_path, campaign_report = pinned_json(
        record, "campaign_report_path", "campaign_report_sha256"
    )
    manifest_path, campaign = pinned_json(
        record, "campaign_manifest_path", "campaign_manifest_sha256"
    )
    if (
        campaign_report.get("status") != "complete"
        or campaign_report.get("campaign_id")
        != campaign.get("campaign_id")
    ):
        raise TokenUsageError("controlled campaign is not complete and bound")
    runtime = campaign.get("runtime")
    model = runtime.get("model") if isinstance(runtime, Mapping) else None
    families = campaign.get("families")
    live_cases = campaign.get("live_cases")
    aggregates = campaign_report.get("aggregates")
    if (
        not isinstance(model, str)
        or not model
        or not isinstance(families, list)
        or not families
        or not isinstance(live_cases, Mapping)
        or not isinstance(aggregates, Mapping)
    ):
        raise TokenUsageError("controlled campaign metadata is incomplete")

    rows: list[dict[str, Any]] = []
    all_usage_rows: list[dict[str, int]] = []
    for family in families:
        if not isinstance(family, str) or not family:
            raise TokenUsageError("campaign family identity is invalid")
        for generation in ("baseline", "evolved"):
            usage_rows: list[dict[str, int]] = []
            query_count = 0
            runtime_errors = 0
            for cohort in live_cases:
                cohort_rows = aggregates.get(cohort)
                family_rows = (
                    cohort_rows.get(family)
                    if isinstance(cohort_rows, Mapping)
                    else None
                )
                cell = (
                    family_rows.get(generation)
                    if isinstance(family_rows, Mapping)
                    else None
                )
                if not isinstance(cell, Mapping):
                    raise TokenUsageError(
                        f"missing {cohort}/{family}/{generation} cell"
                    )
                trials = positive_count(
                    cell.get("trials"), "campaign cell trials"
                )
                input_tokens, input_observed = resource_total(
                    cell, "input_tokens"
                )
                cache_tokens, cache_observed = resource_total(
                    cell, "cache_tokens"
                )
                output_tokens, output_observed = resource_total(
                    cell, "output_tokens"
                )
                if {
                    input_observed,
                    cache_observed,
                    output_observed,
                } != {trials}:
                    raise TokenUsageError(
                        f"incomplete token observations for "
                        f"{cohort}/{family}/{generation}"
                    )
                if cache_tokens > input_tokens:
                    raise TokenUsageError(
                        "campaign cache tokens exceed input tokens"
                    )
                usage = {
                    "input_tokens_including_cache": input_tokens,
                    "cache_tokens_reported_separately": cache_tokens,
                    "output_tokens": output_tokens,
                    "total_tokens": input_tokens + output_tokens,
                }
                usage_rows.append(usage)
                all_usage_rows.append(usage)
                query_count += trials
                runtime_errors += token_count(
                    cell.get("runtime_errors"),
                    "campaign runtime_errors",
                )
            rows.append(
                {
                    "methodology": family,
                    "generation": generation,
                    "model": model,
                    "submitted_query_count": query_count,
                    "runtime_error_count": runtime_errors,
                    **mean_usage(usage_rows, query_count),
                }
            )

    all_queries = sum(row["submitted_query_count"] for row in rows)
    return {
        "unit": "one submitted consult-only Harbor query",
        "campaign_id": campaign["campaign_id"],
        "model": model,
        "question_ids": [
            question_id
            for cohort in live_cases.values()
            for question_id in cohort
        ],
        "methodologies": rows,
        "overall": {
            "methodology_generation_count": len(rows),
            "submitted_query_count": all_queries,
            "runtime_error_count": sum(
                row["runtime_error_count"] for row in rows
            ),
            **mean_usage(all_usage_rows, all_queries),
        },
        "sources": [
            {
                "path": report_path.relative_to(REPO).as_posix(),
                "sha256": sha256_file(report_path),
            },
            {
                "path": manifest_path.relative_to(REPO).as_posix(),
                "sha256": sha256_file(manifest_path),
            },
        ],
    }


def strategy_name(row: Mapping[str, Any]) -> str:
    """Derive the registered task strategy from its native test path."""

    value = row.get("native_task_tests")
    if not isinstance(value, str):
        raise TokenUsageError("raw trial has no native_task_tests")
    parts = Path(value.replace("\\", "/")).parts
    try:
        index = parts.index("consult-only") + 1
    except ValueError as exc:
        raise TokenUsageError(
            f"cannot derive strategy from {value}"
        ) from exc
    if index >= len(parts):
        raise TokenUsageError(f"cannot derive strategy from {value}")
    return parts[index]


def graphrag_complete_response_usage(
    evidence: Mapping[str, Any],
) -> dict[str, Any]:
    """Aggregate complete GraphRAG responses without mixing models."""

    record = evidence.get("graphrag_complete_responses")
    if not isinstance(record, Mapping):
        raise TokenUsageError(
            "graphrag_complete_responses must be an object"
        )
    report_path, report = pinned_json(
        record,
        "current_metrics_report_path",
        "current_metrics_report_sha256",
    )
    trials = report.get("raw_trials")
    if not isinstance(trials, list):
        raise TokenUsageError("current-metrics report has no raw_trials")

    grouped: defaultdict[
        tuple[str, str], list[dict[str, int]]
    ] = defaultdict(list)
    answer_count = 0
    for trial in trials:
        if not isinstance(trial, Mapping):
            raise TokenUsageError("raw trial must be an object")
        trace = trial.get("trace")
        if (
            not isinstance(trace, Mapping)
            or trace.get("outcome") != "answer-emitted"
        ):
            continue
        answer_count += 1
        model = trial.get("model")
        usage = trial.get("usage")
        if (
            not isinstance(model, str)
            or not model
            or not isinstance(usage, Mapping)
        ):
            continue
        input_tokens = token_count(
            usage.get("input_tokens_including_cache"),
            "archive input tokens",
        )
        cache_tokens = token_count(
            usage.get("cache_tokens_reported_separately"),
            "archive cache tokens",
        )
        output_tokens = token_count(
            usage.get("output_tokens"), "archive output tokens"
        )
        total_tokens = token_count(
            usage.get("total_tokens"), "archive total tokens"
        )
        if (
            cache_tokens > input_tokens
            or total_tokens != input_tokens + output_tokens
        ):
            raise TokenUsageError(
                "archive usage violates Harbor token semantics"
            )
        grouped[(strategy_name(trial), model)].append(
            {
                "input_tokens_including_cache": input_tokens,
                "cache_tokens_reported_separately": cache_tokens,
                "output_tokens": output_tokens,
                "total_tokens": total_tokens,
            }
        )

    rows = []
    by_model: defaultdict[str, list[dict[str, int]]] = defaultdict(list)
    for (strategy, model), usage_rows in sorted(grouped.items()):
        by_model[model].extend(usage_rows)
        rows.append(
            {
                "strategy": strategy,
                "model": model,
                "complete_response_count": len(usage_rows),
                **mean_usage(usage_rows, len(usage_rows)),
            }
        )
    model_rows = [
        {
            "model": model,
            "complete_response_count": len(usage_rows),
            **mean_usage(usage_rows, len(usage_rows)),
        }
        for model, usage_rows in sorted(by_model.items())
    ]
    return {
        "unit": "one answer-emitting GraphRAG Harbor query",
        "raw_trial_count": len(trials),
        "answer_emitted_count": answer_count,
        "complete_usage_count": sum(
            row["complete_response_count"] for row in rows
        ),
        "methodology_model_rows": rows,
        "model_rollups": model_rows,
        "source": {
            "path": report_path.relative_to(REPO).as_posix(),
            "sha256": sha256_file(report_path),
        },
    }


def generate_report(
    evidence_path: Path = DEFAULT_EVIDENCE,
    report_date: str = "2026-07-30",
) -> dict[str, Any]:
    """Generate the exhaustive registered-strategy two-stage report."""

    evidence = load_json(evidence_path)
    if evidence.get("schema_version") != EVIDENCE_SCHEMA:
        raise TokenUsageError("unsupported token evidence schema")
    registered_build = registered_build_usage(evidence)
    registered_consult = registered_consultation_usage(evidence)
    historical_build = build_folder_usage(evidence)
    return {
        "schema_version": REPORT_SCHEMA,
        "report_date": report_date,
        "report_kind": (
            "complete-registered-strategy-two-stage-token-usage"
        ),
        "new_model_calls": registered_build["new_model_calls"],
        "reused_consultation_model_calls": registered_consult["overall"][
            "submitted_query_count"
        ],
        "evidence_manifest": {
            "path": evidence_path.resolve().relative_to(
                REPO.resolve()
            ).as_posix(),
            "sha256": sha256_file(evidence_path),
        },
        "token_semantics": {
            "input": (
                "Harbor n_input_tokens already includes cached input"
            ),
            "cache": (
                "Harbor n_cache_tokens is reported separately as a subset "
                "of input and is not added to total"
            ),
            "total": "n_input_tokens + n_output_tokens",
        },
        "registered_build_folder_usage": registered_build,
        "registered_consultation_query_usage": registered_consult,
        "direct_retrieval_usage": direct_retrieval_usage(evidence),
        "historical_build_folder_usage": historical_build,
        "build_folder_usage": historical_build,
        "controlled_consultation_usage": (
            controlled_consultation_usage(evidence)
        ),
        "graphrag_complete_response_diagnostic": (
            graphrag_complete_response_usage(evidence)
        ),
        "limitations": [
            (
                "Each registered family has two independent single-folder "
                "builder calls. Their same-environment folder inventories "
                "must be byte-identical, and the per-folder mean has no "
                "cross-folder orchestration amortization."
            ),
            (
                "The consultation ranking measures submitted-query cost. "
                "Graphify and Ensemble look inexpensive only because all six "
                "of their common trials ended in runtime errors; use the "
                "separate zero-error comparison for an operational choice."
            ),
            (
                "The common consultation matrix is a legacy Harbor campaign "
                "with equal tasks, model, Pi version, and thinking level, but "
                "it predates the immutable runtime input-binding v2 contract."
            ),
            (
                "Construction and consultation are different causal stages "
                "and remain separate rankings even though their primary rows "
                "use the same model and corpus."
            ),
            (
                "Token rank does not measure wall-clock latency, CPU, memory, "
                "storage, or provider price. Script-heavy builders can use few "
                "agent tokens while performing substantial local computation."
            ),
            (
                "The 25 direct-retrieval routes make no LLM call themselves. "
                "Their zero-token unit excludes any later grounded answer "
                "generation and must not be substituted for consultant cost."
            ),
            (
                "Two stopped builder rehearsals are excluded from the primary "
                "matrix: one amortized two folders inside a call and timed "
                "out on Embeddings; the next compared output bytes against a "
                "snapshot produced in a different environment. Their partial "
                "or non-comparable costs are not strategy means."
            ),
            (
                "Historical builder and consultation tables use other "
                "contracts or uneven archives and remain supplemental rather "
                "than part of the eight-family primary ranking."
            ),
        ],
    }


def number(value: object) -> str:
    """Format a report token count."""

    return "—" if value is None else f"{float(value):,.2f}"


def markdown(report: Mapping[str, Any]) -> str:
    """Render primary rankings plus clearly separated diagnostics."""

    build = report["registered_build_folder_usage"]
    consult = report["registered_consultation_query_usage"]
    lowest_build = build["lowest_token_methodology"]
    highest_build = build["highest_token_methodology"]
    lowest_query = consult["lowest_observed_submitted_cost"]
    highest_query = consult["highest_observed_submitted_cost"]
    lowest_zero_error = consult["lowest_zero_error_methodology"]
    highest_zero_error = consult["highest_zero_error_methodology"]
    lines = [
        "# Semantic OKF two-stage token usage",
        "",
        (
            "This report covers **all eight registered build/consult strategy "
            "pairs**. Its primary matrix contains "
            f"**{report['new_model_calls']} newly submitted, qualified "
            "builder-direct trials** "
            "and reused "
            f"**{report['reused_consultation_model_calls']} existing "
            "same-question consult-only calls**. Construction and "
            "consultation remain separate units."
        ),
        "",
        "## Results at a glance",
        "",
        (
            f"- Lowest construction cost: **{lowest_build['label']}**, "
            f"{number(lowest_build['mean_total_tokens'])} tokens per folder."
        ),
        (
            f"- Highest construction cost: **{highest_build['label']}**, "
            f"{number(highest_build['mean_total_tokens'])} tokens per folder."
        ),
        (
            f"- Lowest observed submitted-query cost: "
            f"**{lowest_query['label']}**, "
            f"{number(lowest_query['mean_total_tokens'])} tokens, with "
            f"{lowest_query['runtime_error_count']}/"
            f"{lowest_query['submitted_query_count']} runtime errors."
        ),
        (
            f"- Highest observed submitted-query cost: "
            f"**{highest_query['label']}**, "
            f"{number(highest_query['mean_total_tokens'])} tokens, with "
            f"{highest_query['runtime_error_count']}/"
            f"{highest_query['submitted_query_count']} runtime errors."
        ),
        "",
    ]
    if lowest_zero_error is not None and highest_zero_error is not None:
        lines.extend(
            [
                (
                    f"Among strategies with zero runtime errors, "
                    f"**{lowest_zero_error['label']}** used the least "
                    f"({number(lowest_zero_error['mean_total_tokens'])}) and "
                    f"**{highest_zero_error['label']}** used the most "
                    f"({number(highest_zero_error['mean_total_tokens'])}) "
                    "per submitted query."
                ),
                "",
            ]
        )
    lines.extend(
        [
        (
            "Harbor input already includes cached input. Total is input plus "
            "output; cache is displayed separately and is never added twice."
        ),
        "",
        "## Knowledge-folder construction: all registered strategies",
        "",
        (
            f"Contract: `{build['dataset_id']}`, `{build['model']}`, Pi "
            f"`{build['pi_version']}`, `{build['thinking']}` thinking. Each "
            "strategy has two independent builder calls and two validated "
            "folders. Combined build-and-consult trials are excluded."
        ),
        "",
        (
            "| Rank (low→high) | Strategy | Calls | Folders | Qualified | "
            "Mean input/folder | Mean cache/folder | Mean output/folder | "
            "Mean total/folder |"
        ),
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in build["methodologies"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    str(row["token_rank_low_to_high"]),
                    str(row["label"]),
                    str(row["builder_call_count"]),
                    str(row["generated_folder_count"]),
                    (
                        f"{row['qualified_builder_call_count']}/"
                        f"{row['builder_call_count']}"
                    ),
                    number(
                        row["mean_input_tokens_including_cache"]
                    ),
                    number(
                        row[
                            "mean_cache_tokens_reported_separately"
                        ]
                    ),
                    number(row["mean_output_tokens"]),
                    number(row["mean_total_tokens"]),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            (
                "Construction rank is based on mean total tokens per generated "
                "folder. Every primary row passed artifact integrity, record "
                "identity, independent validation, cross-replicate inventory "
                "identity, command coverage, and workflow-safety gates."
            ),
            "",
            "## Consultation: all registered strategies",
            "",
            (
                f"Contract: `{consult['dataset_id']}` `{consult['cohort']}` "
                f"questions {', '.join(consult['question_ids'])}; "
                f"`{consult['model']}`, Pi `{consult['pi_version']}`, "
                f"`{consult['thinking']}` thinking. Every strategy received "
                "the same six questions. Failed attempts remain in the "
                "denominator because they consumed tokens."
            ),
            "",
            (
                "| Rank (low→high) | Strategy | Queries | Runtime errors | "
                "Complete | Mean input | Mean cache | Mean output | "
                "Mean total/submitted query | Mean total/complete response |"
            ),
            "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in consult["methodologies"]:
        complete_usage = row["complete_response_usage"]
        lines.append(
            "| "
            + " | ".join(
                [
                    str(row["token_rank_low_to_high"]),
                    str(row["label"]),
                    str(row["submitted_query_count"]),
                    str(row["runtime_error_count"]),
                    str(row["complete_query_count"]),
                    number(
                        row["mean_input_tokens_including_cache"]
                    ),
                    number(
                        row[
                            "mean_cache_tokens_reported_separately"
                        ]
                    ),
                    number(row["mean_output_tokens"]),
                    number(row["mean_total_tokens"]),
                    number(
                        complete_usage["mean_total_tokens"]
                        if complete_usage is not None
                        else None
                    ),
                ]
            )
            + " |"
        )
    direct = report["direct_retrieval_usage"]
    lines.extend(
        [
            "",
            (
                "Graphify and Ensemble are the two lowest observed submitted "
                "costs, but both are 0/6 complete. They are cheap because the "
                "runtime stopped early, not because they delivered efficient "
                "answers. Complete-response means are diagnostic because "
                "strategies with failures completed different question "
                "subsets. The zero-error comparison contains Legacy and Turso."
            ),
            "",
            "## All deterministic direct-retrieval routes",
            "",
            (
                f"All {direct['strategy_count']} registered direct-retrieval "
                "helpers use **0 LLM tokens per retrieval invocation**. This "
                "unit covers only deterministic retrieval; it excludes a later "
                "answer-generation agent."
            ),
            "",
            "| Strategy | LLM calls/retrieval | LLM tokens/retrieval |",
            "|---|---:|---:|",
        ]
    )
    for row in direct["strategies"]:
        lines.append(
            f"| {row['label']} | "
            f"{direct['llm_calls_per_retrieval']} | "
            f"{direct['llm_tokens_per_retrieval']} |"
        )

    historical_build = report["historical_build_folder_usage"]
    lines.extend(
        [
            "",
            "## Historical builder diagnostics",
            "",
            (
                "These earlier builder-direct rows use "
                f"`{historical_build['model']}` and are retained for audit. "
                "They are not mixed into the primary eight-family ranking."
            ),
            "",
            (
                "| Methodology | Strict | Trials | Folders | "
                "Mean total/folder |"
            ),
            "|---|---|---:|---:|---:|",
        ]
    )
    for row in historical_build["methodologies"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    str(row["label"]),
                    "yes" if row["strictly_qualified"] else "no",
                    str(row["trial_count"]),
                    str(row["generated_folder_count"]),
                    number(row["mean_total_tokens"]),
                ]
            )
            + " |"
        )

    pilot = report["controlled_consultation_usage"]
    lines.extend(
        [
            "",
            "## Historical controlled consultation pilot",
            "",
            (
                "The earlier baseline/evolved pilot remains available as a "
                "separate diagnostic and is not the primary registered-family "
                "ranking."
            ),
            "",
            (
                "| Methodology | Generation | Queries | Errors | "
                "Mean total/query |"
            ),
            "|---|---|---:|---:|---:|",
        ]
    )
    for row in pilot["methodologies"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    str(row["methodology"]),
                    str(row["generation"]),
                    str(row["submitted_query_count"]),
                    str(row["runtime_error_count"]),
                    number(row["mean_total_tokens"]),
                ]
            )
            + " |"
        )

    diagnostic = report["graphrag_complete_response_diagnostic"]
    lines.extend(
        [
            "",
            "## Uneven GraphRAG archive diagnostic",
            "",
            (
                "The current artifact archive has "
                f"{diagnostic['complete_usage_count']} answer-emitting trials "
                "with complete usage. Coverage is uneven, so these rows are "
                "not a methodology ranking. Models remain separate."
            ),
            "",
            (
                "| Strategy | Model | Complete responses | Mean input | "
                "Mean cache | Mean output | Mean total/response |"
            ),
            "|---|---|---:|---:|---:|---:|---:|",
        ]
    )
    for row in diagnostic["methodology_model_rows"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    str(row["strategy"]),
                    f"`{row['model']}`",
                    str(row["complete_response_count"]),
                    number(
                        row["mean_input_tokens_including_cache"]
                    ),
                    number(
                        row[
                            "mean_cache_tokens_reported_separately"
                        ]
                    ),
                    number(row["mean_output_tokens"]),
                    number(row["mean_total_tokens"]),
                ]
            )
            + " |"
        )
    lines.extend(["", "## Limitations", ""])
    lines.extend(
        f"- {limitation}" for limitation in report["limitations"]
    )
    lines.append("")
    return "\n".join(lines)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse report generation arguments."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", type=Path, default=DEFAULT_EVIDENCE)
    parser.add_argument("--report-date", default="2026-07-30")
    parser.add_argument("--json-output", type=Path, default=DEFAULT_JSON)
    parser.add_argument(
        "--markdown-output", type=Path, default=DEFAULT_MARKDOWN
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Fail unless existing outputs exactly match regeneration.",
    )
    return parser.parse_args(argv)


def write_or_check(
    path: Path,
    content: str,
    check: bool,
) -> None:
    """Write one report or verify deterministic regeneration."""

    if check:
        try:
            existing = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            raise TokenUsageError(f"cannot check report: {path}") from exc
        if existing != content:
            raise TokenUsageError(f"generated report drifted: {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def main(argv: Sequence[str] | None = None) -> int:
    """Generate or validate both token report formats."""

    args = parse_args(argv)
    report = generate_report(
        args.evidence.resolve(), report_date=args.report_date
    )
    rendered_json = (
        json.dumps(report, indent=2, sort_keys=True) + "\n"
    )
    rendered_markdown = markdown(report)
    write_or_check(args.json_output, rendered_json, args.check)
    write_or_check(
        args.markdown_output, rendered_markdown, args.check
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except TokenUsageError as exc:
        raise SystemExit(str(exc)) from exc
