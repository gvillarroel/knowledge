#!/usr/bin/env python3
"""Consolidate sanitized Harbor final reports into Markdown and static SVGs."""

# Ruff cannot wrap complete SVG element literals without making the templates harder to audit.
# ruff: noqa: E501

from __future__ import annotations

import argparse
import hashlib
import html
import json
import math
import re
import sys
import tempfile
import unicodedata
from collections import Counter
from collections.abc import Iterable
from contextlib import suppress
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1
MAX_INPUT_BYTES = 32 * 1024 * 1024
MAX_TOTAL_INPUT_BYTES = 64 * 1024 * 1024
MAX_REPORTS = 24
MAX_RUNS = 24
MAX_TRIALS_PER_RUN = 10_000
MAX_COMPLETENESS_PROBLEMS = 128
MAX_TEXT_CHARS = 1_024
MAX_JSON_NUMBER_CHARS = 256
OUTPUT_FILES = (
    "comparison-report.json",
    "comparison-report.md",
    "quality-comparison.svg",
    "resource-comparison.svg",
    "efficiency-frontier.svg",
)
PALETTE = (
    "#38BDF8",
    "#A78BFA",
    "#34D399",
    "#FBBF24",
    "#FB7185",
    "#22D3EE",
    "#C084FC",
    "#A3E635",
    "#F97316",
    "#60A5FA",
    "#F472B6",
    "#2DD4BF",
)
ID_PATTERN = re.compile(r"[^a-zA-Z0-9._-]+")
FAIRNESS_BASES = {None, "lock-and-trial-results", "trial-results"}
BIDI_CONTROL_CLASSES = {"LRE", "RLE", "LRO", "RLO", "PDF", "LRI", "RLI", "FSI", "PDI"}


class ReportError(ValueError):
    """Raised for invalid or unsafe report input."""


def canonical_json(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            allow_nan=False,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def require_object(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ReportError(f"{label} must be an object")
    return value


def require_list(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise ReportError(f"{label} must be an array")
    return value


def require_text(
    value: Any,
    label: str,
    *,
    maximum_length: int = MAX_TEXT_CHARS,
) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ReportError(f"{label} must be a non-empty string")
    normalized = value.strip()
    if len(normalized) > maximum_length:
        raise ReportError(f"{label} exceeds the {maximum_length}-character limit")
    if any(
        ord(character) < 32
        or ord(character) == 127
        or unicodedata.bidirectional(character) in BIDI_CONTROL_CLASSES
        or unicodedata.category(character) == "Cs"
        or 0xFDD0 <= ord(character) <= 0xFDEF
        or ord(character) & 0xFFFF in {0xFFFE, 0xFFFF}
        for character in normalized
    ):
        raise ReportError(
            f"{label} contains control, noncharacter, surrogate, or "
            "bidirectional formatting characters"
        )
    return normalized


def reject_json_constant(value: str) -> Any:
    """Reject non-standard JSON constants such as NaN and Infinity."""

    raise ReportError(f"non-standard JSON constant is not allowed: {value}")


def strict_json_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    """Build a JSON object while rejecting ambiguous duplicate keys."""

    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ReportError("duplicate JSON key is not allowed")
        result[key] = value
    return result


def strict_json_integer(value: str) -> int:
    """Bound integer parsing before Python allocates an arbitrary-precision value."""

    if len(value.removeprefix("-")) > MAX_JSON_NUMBER_CHARS:
        raise ReportError("JSON integer exceeds the numeric length limit")
    return int(value)


def strict_json_float(value: str) -> float:
    """Reject finite-syntax JSON numbers that overflow the runtime float range."""

    if len(value) > MAX_JSON_NUMBER_CHARS:
        raise ReportError("JSON number exceeds the numeric length limit")
    numeric = float(value)
    if not math.isfinite(numeric):
        raise ReportError("JSON number exceeds the finite numeric range")
    return numeric


def require_number(
    value: Any,
    label: str,
    *,
    minimum: float | None = None,
    maximum: float | None = None,
    integer: bool = False,
) -> float | int:
    if integer:
        if type(value) is not int:
            raise ReportError(f"{label} must be an integer")
        numeric: float | int = value
    elif isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ReportError(f"{label} must be a finite number")
    else:
        try:
            numeric = float(value)
        except (OverflowError, ValueError) as error:
            raise ReportError(f"{label} must be a finite number") from error
    if not integer and not math.isfinite(float(numeric)):
        raise ReportError(f"{label} must be a finite number")
    if minimum is not None and numeric < minimum:
        raise ReportError(f"{label} must be >= {minimum}")
    if maximum is not None and numeric > maximum:
        raise ReportError(f"{label} must be <= {maximum}")
    return numeric


def normalize_timestamp(value: Any, label: str) -> tuple[str, datetime]:
    """Validate an aware ISO-8601 timestamp and normalize it to UTC."""

    text = require_text(value, label, maximum_length=128)
    candidate = text[:-1] + "+00:00" if text.endswith("Z") else text
    try:
        parsed = datetime.fromisoformat(candidate)
    except ValueError as error:
        raise ReportError(f"{label} must be a valid ISO-8601 timestamp: {error}") from error
    if parsed.tzinfo is None:
        raise ReportError(f"{label} must include a timezone")
    normalized = parsed.astimezone(timezone.utc)
    rendered = normalized.isoformat().replace("+00:00", "Z")
    return rendered, normalized


def parse_job_timestamp(value: Any, label: str) -> datetime:
    """Parse a native Harbor job timestamp without inventing a missing timezone."""

    text = require_text(value, label, maximum_length=128)
    candidate = text[:-1] + "+00:00" if text.endswith("Z") else text
    try:
        return datetime.fromisoformat(candidate)
    except (OverflowError, ValueError) as error:
        raise ReportError(f"{label} must be a valid ISO-8601 timestamp: {error}") from error


def optional_number(
    value: Any,
    label: str,
    *,
    minimum: float | None = None,
    maximum: float | None = None,
) -> float | None:
    if value is None:
        return None
    return float(
        require_number(value, label, minimum=minimum, maximum=maximum)
    )


def preflight_report_paths(paths: list[Path]) -> list[tuple[Path, int]]:
    """Resolve and size all inputs before loading any report body."""

    if len(paths) > MAX_REPORTS:
        raise ReportError(f"at most {MAX_REPORTS} input reports are allowed")
    prepared: list[tuple[Path, int]] = []
    seen: set[Path] = set()
    total_size = 0
    for index, path in enumerate(paths):
        if path.is_symlink():
            raise ReportError(f"report[{index}] must not be a symbolic link")
        try:
            source = path.resolve(strict=True)
        except OSError as error:
            raise ReportError(f"report[{index}] does not exist") from error
        if source in seen:
            raise ReportError(f"report[{index}] duplicates an earlier input")
        seen.add(source)
        if not source.is_file():
            raise ReportError(f"report[{index}] is not a regular file")
        size = source.stat().st_size
        if size > MAX_INPUT_BYTES:
            raise ReportError(
                f"report[{index}] exceeds the {MAX_INPUT_BYTES}-byte input limit"
            )
        total_size += size
        if total_size > MAX_TOTAL_INPUT_BYTES:
            raise ReportError(
                f"input reports exceed the {MAX_TOTAL_INPUT_BYTES}-byte aggregate limit"
            )
        prepared.append((source, size))
    return prepared


def read_report(
    path: Path,
    input_index: int,
    expected_size: int | None = None,
) -> dict[str, Any]:
    source = path.resolve(strict=True)
    size = source.stat().st_size if expected_size is None else expected_size
    if size > MAX_INPUT_BYTES:
        raise ReportError(
            f"report[{input_index}] exceeds the {MAX_INPUT_BYTES}-byte input limit"
        )
    with source.open("rb") as handle:
        raw = handle.read(size + 1)
    if len(raw) != size:
        raise ReportError(f"report[{input_index}] changed after input preflight")
    try:
        decoded = raw.decode("utf-8")
        value = json.loads(
            decoded,
            object_pairs_hook=strict_json_object,
            parse_float=strict_json_float,
            parse_int=strict_json_integer,
            parse_constant=reject_json_constant,
        )
    except UnicodeDecodeError as error:
        raise ReportError(f"report[{input_index}] is not valid UTF-8") from error
    except (ValueError, RecursionError) as error:
        raise ReportError(f"report[{input_index}] is not valid strict JSON: {error}") from error
    report = require_object(value, f"report[{input_index}]")
    if (
        type(report.get("schemaVersion")) is not int
        or report.get("schemaVersion") != 1
        or report.get("source") != "harbor"
    ):
        raise ReportError(
            f"report[{input_index}] must be a schemaVersion 1 Harbor final-report.json"
        )
    require_text(report.get("title"), f"report[{input_index}].title")
    generated_at, generated_at_value = normalize_timestamp(
        report.get("generatedAt"), f"report[{input_index}].generatedAt"
    )
    jobs = require_list(report.get("jobs"), f"report[{input_index}].jobs")
    if not jobs:
        raise ReportError(f"report[{input_index}].jobs must not be empty")
    comparison = require_object(
        report.get("comparison", {}), f"report[{input_index}].comparison"
    )
    comparison_enabled = comparison.get("enabled")
    if type(comparison_enabled) is not bool:
        raise ReportError(f"report[{input_index}].comparison.enabled must be a boolean")
    fairness_basis = comparison.get("fairnessBasis")
    if fairness_basis not in FAIRNESS_BASES:
        raise ReportError(
            f"report[{input_index}].comparison.fairnessBasis is not recognized"
        )
    warning = comparison.get("warning")
    if warning is not None:
        require_text(
            warning,
            f"report[{input_index}].comparison.warning",
            maximum_length=4_096,
        )
    if comparison_enabled and fairness_basis is None:
        raise ReportError(
            f"report[{input_index}].comparison requires a recognized fairness basis"
        )
    if not comparison_enabled and (fairness_basis is not None or warning is not None):
        raise ReportError(
            f"report[{input_index}].comparison metadata is inconsistent with enabled=false"
        )
    digest = sha256_bytes(raw)
    source_id = f"source-{digest.removeprefix('sha256:')[:12]}"
    return {
        "index": input_index,
        "sourceId": source_id,
        "sha256": digest,
        "generatedAt": generated_at,
        "_generatedAt": generated_at_value,
        "fairnessBasis": fairness_basis,
        "comparisonEnabled": comparison_enabled,
        "comparisonWarningCode": (
            "missing-locks"
            if fairness_basis == "trial-results"
            else "native-warning-redacted"
            if warning is not None
            else None
        ),
        "jobs": jobs,
    }


def normalize_metric_summary(
    value: Any,
    label: str,
    *,
    nonnegative: bool,
    completed_trials: int,
) -> dict[str, Any] | None:
    if value is None:
        return None
    metric = require_object(value, label)
    count = require_number(
        metric.get("count"),
        f"{label}.count",
        minimum=0,
        maximum=completed_trials,
        integer=True,
    )
    total = require_number(
        metric.get("total"),
        f"{label}.total",
        minimum=0 if nonnegative else None,
    )
    average = require_number(
        metric.get("average"),
        f"{label}.average",
        minimum=0 if nonnegative else None,
    )
    if count == 0:
        raise ReportError(f"{label}.count must be positive when the metric is present")
    derived_total = float(average) * count
    if not math.isfinite(derived_total) or not math.isclose(
        float(total), derived_total, rel_tol=1e-9, abs_tol=1e-9
    ):
        raise ReportError(f"{label}.total and average are inconsistent")
    return {
        "count": count,
        "total": float(total),
        "average": float(average),
        "observedTrials": count,
        "totalTrials": completed_trials,
        "complete": count == completed_trials,
    }


def normalized_token_value(
    token_map: dict[str, Any],
    aliases: tuple[str, ...],
    label: str,
) -> float | None:
    """Validate aliases for one token field and return its normalized value."""

    present = [alias for alias in aliases if token_map.get(alias) is not None]
    normalized_aliases = [
        float(
            require_number(
                token_map[alias],
                f"{label}.{alias}",
                minimum=0,
            )
        )
        for alias in present
    ]
    if len(normalized_aliases) > 1 and not all(
        math.isclose(normalized_aliases[0], value, rel_tol=0, abs_tol=0)
        for value in normalized_aliases[1:]
    ):
        raise ReportError(f"{label} has conflicting aliases for {aliases[0]}")
    return normalized_aliases[0] if normalized_aliases else None


def trial_metric(
    trials: list[Any], field: str, label: str
) -> dict[str, Any] | None:
    values: list[float] = []
    for index, raw_trial in enumerate(trials):
        trial = require_object(raw_trial, f"{label}.trials[{index}]")
        tokens = trial.get("tokens")
        if tokens is None:
            continue
        token_map = require_object(tokens, f"{label}.trials[{index}].tokens")
        aliases = {
            "cache": ("cachedInput", "cache"),
            "reasoning": ("reasoning", "reasoningTokens"),
        }.get(field, (field,))
        normalized = normalized_token_value(
            token_map,
            aliases,
            f"{label}.trials[{index}].tokens",
        )
        if normalized is not None:
            values.append(normalized)
    if not values:
        return None
    total_trials = len(trials)
    try:
        total = math.fsum(values)
    except OverflowError as error:
        raise ReportError(f"{label}.trials token totals overflow") from error
    if not math.isfinite(total):
        raise ReportError(f"{label}.trials token totals must be finite")
    return {
        "total": total,
        "average": total / len(values),
        "observedTrials": len(values),
        "totalTrials": total_trials,
        "complete": len(values) == total_trials,
    }


def trial_scalar_metric(
    trials: list[Any],
    field: str,
    label: str,
    *,
    nonnegative: bool,
) -> dict[str, Any] | None:
    """Recompute one scalar aggregate from native trial rows."""

    values: list[float] = []
    for index, raw_trial in enumerate(trials):
        trial = require_object(raw_trial, f"{label}.trials[{index}]")
        raw_value = trial.get(field)
        if raw_value is None:
            continue
        values.append(
            float(
                require_number(
                    raw_value,
                    f"{label}.trials[{index}].{field}",
                    minimum=0 if nonnegative else None,
                )
            )
        )
    if not values:
        return None
    try:
        total = math.fsum(values)
    except OverflowError as error:
        raise ReportError(f"{label}.trials.{field} total overflowed") from error
    if not math.isfinite(total):
        raise ReportError(f"{label}.trials.{field} total must be finite")
    return {
        "total": total,
        "observedTrials": len(values),
    }


def validate_trial_token_accounting(trials: list[Any], label: str) -> None:
    """Validate token subset and total semantics independently for every row."""

    for index, raw_trial in enumerate(trials):
        trial = require_object(raw_trial, f"{label}.trials[{index}]")
        raw_tokens = trial.get("tokens")
        if raw_tokens is None:
            continue
        token_map = require_object(raw_tokens, f"{label}.trials[{index}].tokens")
        token_label = f"{label}.trials[{index}].tokens"
        input_tokens = normalized_token_value(token_map, ("input",), token_label)
        cache_tokens = normalized_token_value(
            token_map, ("cachedInput", "cache"), token_label
        )
        output_tokens = normalized_token_value(token_map, ("output",), token_label)
        total_tokens = normalized_token_value(token_map, ("total",), token_label)
        if cache_tokens is not None:
            if input_tokens is None:
                raise ReportError(f"{token_label}.cachedInput requires input tokens")
            if cache_tokens > input_tokens + 1e-9:
                raise ReportError(f"{token_label}.cachedInput exceeds input tokens")
        components_present = input_tokens is not None and output_tokens is not None
        if total_tokens is None and components_present:
            raise ReportError(f"{token_label}.total is required when input and output exist")
        if total_tokens is not None and not components_present:
            raise ReportError(f"{token_label}.total requires both input and output")
        if total_tokens is not None:
            try:
                derived_total = math.fsum((input_tokens, output_tokens))
            except OverflowError as error:
                raise ReportError(f"{token_label} component total overflowed") from error
            if not math.isfinite(derived_total) or not math.isclose(
                total_tokens, derived_total, rel_tol=1e-9, abs_tol=1e-9
            ):
                raise ReportError(f"{token_label}.total must equal input plus output")


def parse_wall_seconds(started: Any, finished: Any, label: str) -> float | None:
    start = parse_job_timestamp(started, f"{label}.startedAt")
    if finished is None:
        return None
    finish = parse_job_timestamp(finished, f"{label}.finishedAt")
    if (start.utcoffset() is None) != (finish.utcoffset() is None):
        raise ReportError(
            f"{label}.startedAt and finishedAt must either both include a timezone or both omit it"
        )
    elapsed = (finish - start).total_seconds()
    if elapsed < 0:
        raise ReportError(f"{label}.finishedAt precedes startedAt")
    return elapsed


def validate_trial_outcomes(
    trials: list[Any],
    label: str,
    *,
    passed: int,
    verifier_failed: int,
    errored: int,
    complete: bool,
) -> None:
    """Validate aggregate outcome counts against the native trial rows."""

    observed_passed = 0
    observed_verifier_failed = 0
    observed_errored = 0
    for index, raw_trial in enumerate(trials):
        trial = require_object(raw_trial, f"{label}.trials[{index}]")
        trial_passed = trial.get("passed")
        if type(trial_passed) is not bool:
            raise ReportError(f"{label}.trials[{index}].passed must be a boolean")
        error = trial.get("error")
        reward = trial.get("reward")
        if error is not None:
            require_text(
                error,
                f"{label}.trials[{index}].error",
                maximum_length=16_384,
            )
            if trial_passed:
                raise ReportError(
                    f"{label}.trials[{index}] cannot both pass and contain an error"
                )
            observed_errored += 1
        elif trial_passed:
            if reward is None:
                raise ReportError(
                    f"{label}.trials[{index}] cannot pass without a primary reward"
                )
            observed_passed += 1
        else:
            if complete and reward is None:
                raise ReportError(
                    f"{label}.trials[{index}] in a complete job requires a primary reward"
                )
            observed_verifier_failed += 1
    if (observed_passed, observed_verifier_failed, observed_errored) != (
        passed,
        verifier_failed,
        errored,
    ):
        raise ReportError(f"{label} outcome counts do not match its trial rows")


def validate_metric_matches_trials(
    summary: dict[str, Any] | None,
    observed: dict[str, Any] | None,
    label: str,
) -> None:
    """Reject aggregate summaries that drift from native trial rows."""

    if summary is None and observed is None:
        return
    if summary is None or observed is None:
        raise ReportError(f"{label} presence does not match its trial rows")
    if summary["count"] != observed["observedTrials"]:
        raise ReportError(f"{label}.count does not match its trial rows")
    if not math.isclose(
        float(summary["total"]),
        float(observed["total"]),
        rel_tol=1e-9,
        abs_tol=1e-9,
    ):
        raise ReportError(f"{label}.total does not match its trial rows")


def normalize_job(source: dict[str, Any], raw_job: Any, job_index: int) -> dict[str, Any]:
    label = f"report[{source['index']}].jobs[{job_index}]"
    job = require_object(raw_job, label)
    original_label = require_text(job.get("label"), f"{label}.label")
    summary = require_object(job.get("summary"), f"{label}.summary")
    requested = require_number(
        summary.get("requestedTrials"),
        f"{label}.summary.requestedTrials",
        minimum=1,
        maximum=MAX_TRIALS_PER_RUN,
        integer=True,
    )
    completed = require_number(
        summary.get("completedTrials"),
        f"{label}.summary.completedTrials",
        minimum=0,
        maximum=MAX_TRIALS_PER_RUN,
        integer=True,
    )
    passed = require_number(
        summary.get("passedTrials"),
        f"{label}.summary.passedTrials",
        minimum=0,
        maximum=completed,
        integer=True,
    )
    verifier_failed = require_number(
        summary.get("verifierFailedTrials"),
        f"{label}.summary.verifierFailedTrials",
        minimum=0,
        maximum=completed,
        integer=True,
    )
    errored = require_number(
        summary.get("erroredTrials"),
        f"{label}.summary.erroredTrials",
        minimum=0,
        maximum=completed,
        integer=True,
    )
    if requested < completed:
        raise ReportError(f"{label} completed more trials than requested")
    if passed + verifier_failed + errored != completed:
        raise ReportError(
            f"{label} pass, verifier-failure, and error counts must sum to completed trials"
        )
    pass_rate = require_number(
        summary.get("passRate"),
        f"{label}.summary.passRate",
        minimum=0,
        maximum=1,
    )
    expected_rate = passed / completed if completed else 0
    if not math.isclose(float(pass_rate), expected_rate, rel_tol=1e-9, abs_tol=1e-9):
        raise ReportError(f"{label}.summary.passRate is inconsistent with pass counts")

    reward = normalize_metric_summary(
        summary.get("reward"),
        f"{label}.summary.reward",
        nonnegative=False,
        completed_trials=completed,
    )
    total_tokens = normalize_metric_summary(
        summary.get("totalTokens"),
        f"{label}.summary.totalTokens",
        nonnegative=True,
        completed_trials=completed,
    )
    latency_ms = normalize_metric_summary(
        summary.get("agentLatencyMs"),
        f"{label}.summary.agentLatencyMs",
        nonnegative=True,
        completed_trials=completed,
    )
    cost = normalize_metric_summary(
        summary.get("costUsd"),
        f"{label}.summary.costUsd",
        nonnegative=True,
        completed_trials=completed,
    )
    complete = job.get("complete")
    if type(complete) is not bool:
        raise ReportError(f"{label}.complete must be a boolean")
    trials = require_list(job.get("trials"), f"{label}.trials")
    if len(trials) != completed:
        raise ReportError(f"{label}.trials must match completedTrials")
    validate_trial_outcomes(
        trials,
        label,
        passed=passed,
        verifier_failed=verifier_failed,
        errored=errored,
        complete=complete,
    )
    scalar_metrics = {
        "reward": trial_scalar_metric(
            trials, "reward", label, nonnegative=False
        ),
        "costUsd": trial_scalar_metric(
            trials, "costUsd", label, nonnegative=True
        ),
        "agentLatencyMs": trial_scalar_metric(
            trials, "agentLatencyMs", label, nonnegative=True
        ),
    }
    validate_metric_matches_trials(
        reward, scalar_metrics["reward"], f"{label}.summary.reward"
    )
    validate_metric_matches_trials(
        cost, scalar_metrics["costUsd"], f"{label}.summary.costUsd"
    )
    validate_metric_matches_trials(
        latency_ms,
        scalar_metrics["agentLatencyMs"],
        f"{label}.summary.agentLatencyMs",
    )
    validate_trial_token_accounting(trials, label)
    token_metrics = {
        field: trial_metric(trials, field, label)
        for field in ("input", "cache", "output", "reasoning", "total")
    }
    validate_metric_matches_trials(
        total_tokens, token_metrics["total"], f"{label}.summary.totalTokens"
    )
    if (
        token_metrics["input"]
        and token_metrics["output"]
        and token_metrics["input"]["complete"]
        and token_metrics["output"]["complete"]
        and (total_tokens is None or not total_tokens["complete"])
    ):
        raise ReportError(
            f"{label}.summary.totalTokens must cover every trial when input and output do"
        )
    if (
        token_metrics["input"]
        and token_metrics["cache"]
        and token_metrics["input"]["complete"]
        and token_metrics["cache"]["complete"]
        and token_metrics["cache"]["total"]
        > token_metrics["input"]["total"] + 1e-9
    ):
        raise ReportError(f"{label} cached input exceeds total input tokens")
    if (
        total_tokens
        and token_metrics["input"]
        and token_metrics["output"]
        and token_metrics["input"]["complete"]
        and token_metrics["output"]["complete"]
    ):
        try:
            derived_total = math.fsum(
                (token_metrics["input"]["total"], token_metrics["output"]["total"])
            )
        except OverflowError as error:
            raise ReportError(f"{label} total token accounting overflowed") from error
        if not math.isfinite(derived_total):
            raise ReportError(f"{label} total token accounting must be finite")
        if not math.isclose(
            total_tokens["total"], derived_total, rel_tol=1e-6, abs_tol=1e-6
        ):
            raise ReportError(
                f"{label} total tokens must equal input plus output; cache is already included in input"
            )

    completeness_problems = require_list(
        job.get("completenessProblems"), f"{label}.completenessProblems"
    )
    if len(completeness_problems) > MAX_COMPLETENESS_PROBLEMS:
        raise ReportError(
            f"{label}.completenessProblems exceeds the "
            f"{MAX_COMPLETENESS_PROBLEMS}-item limit"
        )
    for problem_index, problem in enumerate(completeness_problems):
        require_text(
            problem,
            f"{label}.completenessProblems[{problem_index}]",
            maximum_length=16_384,
        )
    wall_seconds = parse_wall_seconds(job.get("startedAt"), job.get("finishedAt"), label)
    if complete and requested != completed:
        raise ReportError(f"{label}.complete=true requires every requested trial")
    if complete and completeness_problems:
        raise ReportError(f"{label}.complete=true cannot include completeness problems")
    if not complete and not completeness_problems:
        raise ReportError(f"{label}.complete=false requires a completeness problem")
    if complete and wall_seconds is None:
        raise ReportError(f"{label}.complete=true requires finishedAt")
    job_identity = require_text(
        job.get("jobId"), f"{label}.jobId", maximum_length=512
    )
    run_id = hashlib.sha256(
        f"{source['sha256']}\0{job_identity}\0{original_label}".encode("utf-8")
    ).hexdigest()[:16]
    public_label = f"run-{run_id[:8]}"
    total_cost = cost["total"] if cost else None
    agent_seconds = latency_ms["total"] / 1000 if latency_ms else None
    total_token_value = total_tokens["total"] if total_tokens else None
    return {
        "runId": run_id,
        "label": public_label,
        "sourceIndex": source["index"],
        "sourceReportId": source["sourceId"],
        "sourceReportSha256": source["sha256"],
        "complete": complete,
        "requestedTrials": requested,
        "completedTrials": completed,
        "passedTrials": passed,
        "verifierFailedTrials": verifier_failed,
        "erroredTrials": errored,
        "passRate": float(pass_rate),
        "averageReward": reward["average"] if reward else None,
        "rewardObservedTrials": reward["count"] if reward else 0,
        "rewardComplete": bool(reward and reward["complete"]),
        "tokens": {
            "input": token_metrics["input"],
            "cache": token_metrics["cache"],
            "output": token_metrics["output"],
            "reasoning": token_metrics["reasoning"],
            "total": total_tokens,
            "semantics": "total=input+output; cache is a subset of input and is not added again; reasoning is reported separately",
        },
        "costUsd": total_cost,
        "costObservedTrials": cost["count"] if cost else 0,
        "costComplete": bool(cost and cost["complete"]),
        "agentTimeSeconds": agent_seconds,
        "agentTimeObservedTrials": latency_ms["count"] if latency_ms else 0,
        "agentTimeComplete": bool(latency_ms and latency_ms["complete"]),
        "wallTimeSeconds": wall_seconds,
        "tasksPerMinute": completed * 60 / wall_seconds
        if wall_seconds and wall_seconds > 0
        else None,
        "tokensPerTrial": total_token_value / completed
        if total_tokens is not None and total_tokens["complete"] and completed
        else None,
        "costPerTrialUsd": total_cost / completed
        if cost is not None and cost["complete"] and completed
        else None,
        "costPerPassUsd": total_cost / passed
        if cost is not None and cost["complete"] and passed
        else None,
        "agentSecondsPerTrial": agent_seconds / completed
        if latency_ms is not None and latency_ms["complete"] and completed
        else None,
    }


def assign_display_labels(runs: list[dict[str, Any]]) -> None:
    """Assign opaque labels without exposing native Harbor labels or paths."""

    short_counts = Counter(run["label"] for run in runs)
    for run in runs:
        if short_counts[run["label"]] > 1:
            run["label"] = f"run-{run['runId']}"


def choose_baseline(runs: list[dict[str, Any]], requested: str | None) -> dict[str, Any]:
    if requested is None:
        return runs[0]
    matches = [
        run
        for run in runs
        if requested in {run["runId"], run["label"]}
    ]
    if len(matches) != 1:
        raise ReportError(
            f"--baseline must identify exactly one run by opaque label or runId; matched {len(matches)}"
        )
    return matches[0]


def numeric_delta(current: float | None, baseline: float | None) -> dict[str, float | None]:
    if current is None or baseline is None:
        return {"absolute": None, "percent": None}
    absolute = current - baseline
    if not math.isfinite(absolute):
        raise ReportError("metric delta overflowed")
    percent = absolute / abs(baseline) * 100 if baseline != 0 else None
    if percent is not None and not math.isfinite(percent):
        raise ReportError("metric percentage delta overflowed")
    return {"absolute": absolute, "percent": percent}


def build_deltas(runs: list[dict[str, Any]], baseline: dict[str, Any]) -> list[dict[str, Any]]:
    fields = {
        "passRate": "higher-is-better",
        "averageReward": "higher-is-better",
        "tokensPerTrial": "lower-is-better",
        "costPerTrialUsd": "lower-is-better",
        "agentSecondsPerTrial": "lower-is-better",
        "wallTimeSeconds": "lower-is-better",
        "tasksPerMinute": "higher-is-better",
    }
    rows = []
    for run in runs:
        if run is baseline:
            continue
        metrics = {}
        for field, direction in fields.items():
            current = run.get(field)
            baseline_value = baseline.get(field)
            if field == "averageReward" and not (
                run["rewardComplete"] and baseline["rewardComplete"]
            ):
                current = None
                baseline_value = None
            change = numeric_delta(current, baseline_value)
            improvement = change["absolute"]
            if improvement is not None and direction == "lower-is-better":
                improvement = -improvement
            metrics[field] = {
                **change,
                "direction": direction,
                "signedImprovement": improvement,
            }
        rows.append(
            {
                "baselineRunId": baseline["runId"],
                "candidateRunId": run["runId"],
                "candidateLabel": run["label"],
                "metrics": metrics,
            }
        )
    return rows


def build_report(
    sources: list[dict[str, Any]],
    *,
    title: str,
    baseline_selector: str | None,
    generated_at: str | None,
) -> dict[str, Any]:
    run_count = sum(len(source["jobs"]) for source in sources)
    if run_count > MAX_RUNS:
        raise ReportError(f"at most {MAX_RUNS} runs can be rendered in one report")
    runs = [
        normalize_job(source, raw_job, index)
        for source in sources
        for index, raw_job in enumerate(source["jobs"])
    ]
    run_ids = [run["runId"] for run in runs]
    if len(run_ids) != len(set(run_ids)):
        raise ReportError("input reports contain duplicate run identities")
    assign_display_labels(runs)
    baseline = choose_baseline(runs, baseline_selector)
    if generated_at is None:
        latest_source = max(sources, key=lambda source: source["_generatedAt"])
        resolved_generated_at = latest_source["generatedAt"]
    else:
        resolved_generated_at, _ = normalize_timestamp(generated_at, "--generated-at")
    source_records = [
        {
            "inputIndex": source["index"],
            "sourceReportId": source["sourceId"],
            "sha256": source["sha256"],
            "generatedAt": source["generatedAt"],
            "comparabilityCode": (
                "not-declared"
                if not source["comparisonEnabled"]
                else "lock-verified"
                if source["fairnessBasis"] == "lock-and-trial-results"
                else "trial-evidence-only"
            ),
            "comparisonWarningCode": source["comparisonWarningCode"],
        }
        for source in sources
    ]
    return {
        "schemaVersion": SCHEMA_VERSION,
        "source": "harbor-final-report-consolidation",
        "title": title,
        "generatedAt": resolved_generated_at,
        "baselineRunId": baseline["runId"],
        "baselineLabel": baseline["label"],
        "sourceReports": source_records,
        "runs": runs,
        "deltas": build_deltas(runs, baseline),
        "metricSemantics": {
            "passRate": "passedTrials divided by completedTrials",
            "totalTokens": "Harbor input tokens plus output tokens; cached input is already part of input and is never added twice",
            "reasoningTokens": "shown separately when present because provider accounting may overlap output tokens",
            "agentTime": "sum of complete Harbor agent_execution timings; excludes environment setup and verifier time",
            "wallTime": "finishedAt minus startedAt for the Harbor job",
            "cost": "sum of Harbor-reported USD cost values for observed trials",
            "efficiencyCoverage": "per-trial token, cost, and agent-time values and their deltas are emitted only when the corresponding aggregate covers every completed trial",
            "privacy": "only aggregate metrics, input report commitments, and run labels are emitted; task and trial details are omitted",
        },
        "outputFiles": list(OUTPUT_FILES),
    }


def markdown_text(value: Any) -> str:
    """Render untrusted text as inert Markdown content."""

    escaped = html.escape(str(value).replace("\r", " ").replace("\n", " "), quote=True)
    return re.sub(r"([\\`*_{}\[\]()#+.!|>~-])", r"\\\1", escaped)


def md_cell(value: Any) -> str:
    return markdown_text(value)


def format_number(value: float | int | None, digits: int = 2) -> str:
    if value is None:
        return "n/a"
    return f"{value:,.{digits}f}"


def format_integer(value: float | int | None) -> str:
    if value is None:
        return "n/a"
    return f"{value:,.0f}"


def format_percent(value: float | None, digits: int = 1) -> str:
    if value is None:
        return "n/a"
    return f"{value * 100:.{digits}f}%"


def token_total(run: dict[str, Any], field: str) -> float | None:
    metric = run["tokens"].get(field)
    return metric.get("total") if metric else None


def token_coverage(run: dict[str, Any], field: str) -> str:
    metric = run["tokens"].get(field)
    if not metric:
        return "n/a"
    suffix = "" if metric["complete"] else f" ({metric['observedTrials']}/{metric['totalTrials']})"
    return format_integer(metric["total"]) + suffix


def summary_coverage(
    value: float | int | None,
    observed: int,
    completed: int,
    formatter: Any,
    *,
    always: bool = False,
) -> str:
    if value is None:
        return "n/a"
    suffix = f" ({observed}/{completed})" if always or observed != completed else ""
    return formatter(value) + suffix


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        f"# {markdown_text(report['title'])}",
        "",
        f"Generated from reviewed Harbor reports: {markdown_text(report['generatedAt'])}. "
        f"Baseline: {md_cell(report['baselineLabel'])}.",
        "",
        "The charts and tables contain aggregate metrics only. Cached input is a subset "
        "of input tokens and is not added a second time; reasoning tokens are shown "
        "separately when a provider reports them.",
        "",
        "## Visual comparison",
        "",
        "- [Quality comparison](quality-comparison.svg)",
        "- [Token, cost, and time comparison](resource-comparison.svg)",
        "- [Cost-quality efficiency frontier](efficiency-frontier.svg)",
        "",
        "## Runs",
        "",
        "| Run | Complete | Requested | Passed / completed | Verifier failed | Execution errors | Pass rate | Mean reward (coverage) | Input tokens | Cached subset | Output tokens | Reasoning tokens | Total tokens | Cost USD (coverage) | Agent time (coverage) | Wall time | Tasks/min |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for run in report["runs"]:
        total_metric = run["tokens"]["total"]
        lines.append(
            "| "
            + " | ".join(
                [
                    md_cell(run["label"]),
                    "yes" if run["complete"] else "no",
                    str(run["requestedTrials"]),
                    f"{run['passedTrials']} / {run['completedTrials']}",
                    str(run["verifierFailedTrials"]),
                    str(run["erroredTrials"]),
                    format_percent(run["passRate"]),
                    summary_coverage(
                        run["averageReward"],
                        run["rewardObservedTrials"],
                        run["completedTrials"],
                        lambda value: format_number(value, 3),
                        always=True,
                    ),
                    token_coverage(run, "input"),
                    token_coverage(run, "cache"),
                    token_coverage(run, "output"),
                    token_coverage(run, "reasoning"),
                    summary_coverage(
                        total_metric["total"] if total_metric else None,
                        total_metric["count"] if total_metric else 0,
                        run["completedTrials"],
                        format_integer,
                    ),
                    summary_coverage(
                        run["costUsd"],
                        run["costObservedTrials"],
                        run["completedTrials"],
                        lambda value: format_number(value, 4),
                    ),
                    summary_coverage(
                        run["agentTimeSeconds"],
                        run["agentTimeObservedTrials"],
                        run["completedTrials"],
                        lambda value: format_number(value, 1) + " s",
                    ),
                    format_number(run["wallTimeSeconds"], 1) + " s"
                    if run["wallTimeSeconds"] is not None
                    else "n/a",
                    format_number(run["tasksPerMinute"], 2),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "A parenthesized coverage fraction such as `(3/4)` means only three "
            "of four completed trials reported that metric; it is not a complete total.",
            "",
            "## Deltas from baseline",
            "",
            "| Candidate | Pass-rate delta | Reward delta | Tokens/trial delta | Cost/trial delta | Agent sec/trial delta | Wall-time delta | Throughput delta |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in report["deltas"]:
        metrics = row["metrics"]
        lines.append(
            "| "
            + " | ".join(
                [
                    md_cell(row["candidateLabel"]),
                    format_number(metrics["passRate"]["absolute"] * 100, 1) + " pp"
                    if metrics["passRate"]["absolute"] is not None
                    else "n/a",
                    format_number(metrics["averageReward"]["absolute"], 3),
                    format_integer(metrics["tokensPerTrial"]["absolute"]),
                    format_number(metrics["costPerTrialUsd"]["absolute"], 4),
                    format_number(metrics["agentSecondsPerTrial"]["absolute"], 2),
                    format_number(metrics["wallTimeSeconds"]["absolute"], 1) + " s"
                    if metrics["wallTimeSeconds"]["absolute"] is not None
                    else "n/a",
                    format_number(metrics["tasksPerMinute"]["absolute"], 2),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "Positive deltas mean the candidate is numerically higher; consult the "
            "metric rather than assuming that every positive delta is desirable.",
            "",
            "## Source commitments and comparability",
            "",
            "| Input | Generated | SHA-256 | Comparability code | Warning code |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for source in report["sourceReports"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    md_cell(source["sourceReportId"]),
                    md_cell(source["generatedAt"]),
                    f"`{source['sha256']}`",
                    md_cell(source["comparabilityCode"]),
                    md_cell(source["comparisonWarningCode"] or "none"),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "This consolidation does not establish cross-report fairness. Preserve the "
            "native report's task, model, agent, attempt, lock, and hardware checks when "
            "making a comparative claim.",
            "",
        ]
    )
    return "\n".join(lines)


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def compact(value: float | int | None, *, money: bool = False) -> str:
    if value is None:
        return "n/a"
    numeric = float(value)
    prefix = "$" if money else ""
    absolute = abs(numeric)
    for divisor, suffix in ((1_000_000_000, "B"), (1_000_000, "M"), (1_000, "K")):
        if absolute >= divisor:
            return f"{prefix}{numeric / divisor:.2f}{suffix}"
    digits = 4 if money and absolute < 1 else 2
    return f"{prefix}{numeric:.{digits}f}"


def truncate(value: str, limit: int) -> str:
    return value if len(value) <= limit else value[: max(1, limit - 1)] + "…"


def nice_max(value: float, floor: float = 1.0) -> float:
    value = max(value, floor)
    exponent = math.floor(math.log10(value))
    fraction = value / (10**exponent)
    nice_fraction = 1 if fraction <= 1 else 2 if fraction <= 2 else 5 if fraction <= 5 else 10
    candidate = nice_fraction * 10**exponent
    try:
        rendered = float(candidate)
    except OverflowError:
        return value
    return rendered if math.isfinite(rendered) else value


def svg_document(title: str, description: str, width: int, height: int, body: str) -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="chart-title chart-desc">
  <title id="chart-title">{esc(title)}</title>
  <desc id="chart-desc">{esc(description)}</desc>
  <defs>
    <linearGradient id="background" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#070B18"/>
      <stop offset="0.55" stop-color="#10172A"/>
      <stop offset="1" stop-color="#071827"/>
    </linearGradient>
    <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="8" stdDeviation="14" flood-color="#000000" flood-opacity="0.28"/>
    </filter>
    <style>
      text {{ font-family: Inter, Segoe UI, Arial, sans-serif; fill: #E5EEF9; }}
      .eyebrow {{ font-size: 14px; font-weight: 700; letter-spacing: 2px; fill: #7DD3FC; }}
      .title {{ font-size: 34px; font-weight: 750; }}
      .subtitle {{ font-size: 15px; fill: #94A3B8; }}
      .section {{ font-size: 18px; font-weight: 700; }}
      .label {{ font-size: 14px; font-weight: 650; }}
      .small {{ font-size: 12px; fill: #94A3B8; }}
      .value {{ font-size: 14px; font-variant-numeric: tabular-nums; }}
      .grid {{ stroke: #334155; stroke-width: 1; opacity: 0.55; }}
      .panel {{ fill: #111827; stroke: #263247; stroke-width: 1; filter: url(#shadow); }}
    </style>
  </defs>
  <rect width="{width}" height="{height}" rx="24" fill="url(#background)"/>
{body}
</svg>
'''


def svg_header(report: dict[str, Any], width: int, subtitle: str) -> str:
    return "\n".join(
        [
            '<rect x="56" y="44" width="248" height="30" rx="15" fill="#0C4A6E" opacity="0.72"/>',
            '<text x="74" y="65" class="eyebrow">HARBOR · RUN COMPARISON</text>',
            f'<text x="56" y="119" class="title">{esc(truncate(report["title"], 66))}</text>',
            f'<text x="56" y="151" class="subtitle">{esc(subtitle)}</text>',
            f'<rect x="{width - 340}" y="62" width="284" height="64" rx="14" fill="#0F2234" stroke="#155E75"/>',
            f'<text x="{width - 320}" y="87" class="small">BASELINE</text>',
            f'<text x="{width - 320}" y="111" class="label">{esc(truncate(report["baselineLabel"], 34))}</text>',
        ]
    )


def render_quality_svg(report: dict[str, Any]) -> str:
    runs = report["runs"]
    width = 1480
    row_height = 54
    height = max(620, 290 + len(runs) * row_height)
    panel_y = 196
    panel_h = len(runs) * row_height + 100
    left_x, right_x, panel_w = 48, 752, 680
    body = [
        svg_header(
            report,
            width,
            "Correctness first: pass rate and mean reward, with failures kept visible.",
        ),
        f'<rect x="{left_x}" y="{panel_y}" width="{panel_w}" height="{panel_h}" rx="20" class="panel"/>',
        f'<rect x="{right_x}" y="{panel_y}" width="{panel_w}" height="{panel_h}" rx="20" class="panel"/>',
        f'<text x="{left_x + 28}" y="{panel_y + 38}" class="section">Pass rate</text>',
        f'<text x="{right_x + 28}" y="{panel_y + 38}" class="section">Mean reward</text>',
    ]
    reward_values = [run["averageReward"] for run in runs if run["averageReward"] is not None]
    reward_ceiling = nice_max(max([abs(value) for value in reward_values] or [1.0]))
    bar_w = panel_w - 250
    for tick in range(5):
        pass_x = left_x + 190 + bar_w * tick / 4
        reward_x = right_x + 190 + bar_w * tick / 4
        reward_tick = reward_ceiling * (-1 + tick / 2)
        body.append(f'<line x1="{pass_x:.1f}" y1="{panel_y + 60}" x2="{pass_x:.1f}" y2="{panel_y + panel_h - 30}" class="grid"/>')
        body.append(f'<text x="{pass_x:.1f}" y="{panel_y + panel_h - 12}" text-anchor="middle" class="small">{tick * 25}%</text>')
        body.append(f'<line x1="{reward_x:.1f}" y1="{panel_y + 60}" x2="{reward_x:.1f}" y2="{panel_y + panel_h - 30}" class="grid"/>')
        body.append(f'<text x="{reward_x:.1f}" y="{panel_y + panel_h - 12}" text-anchor="middle" class="small">{esc(compact(reward_tick))}</text>')
    for index, run in enumerate(runs):
        color = PALETTE[index % len(PALETTE)]
        y = panel_y + 78 + index * row_height
        is_baseline = run["runId"] == report["baselineRunId"]
        baseline_mark = "● " if is_baseline else ""
        for panel_x in (left_x, right_x):
            body.append(f'<text x="{panel_x + 28}" y="{y + 18}" class="label">{esc(baseline_mark + truncate(run["label"], 20))}</text>')
        pass_width = (panel_w - 250) * run["passRate"]
        body.append(f'<rect x="{left_x + 190}" y="{y}" width="{panel_w - 250}" height="24" rx="12" fill="#1E293B"/>')
        body.append(f'<rect x="{left_x + 190}" y="{y}" width="{pass_width:.1f}" height="24" rx="12" fill="{color}"/>')
        body.append(f'<text x="{left_x + panel_w - 24}" y="{y + 18}" text-anchor="end" class="value">{format_percent(run["passRate"])}</text>')
        reward = run["averageReward"]
        reward_center = right_x + 190 + bar_w / 2
        body.append(f'<rect x="{right_x + 190}" y="{y}" width="{panel_w - 250}" height="24" rx="12" fill="#1E293B"/>')
        if reward is not None:
            reward_width = min(
                bar_w / 2, (abs(reward) / reward_ceiling) * (bar_w / 2)
            )
            reward_x = reward_center if reward >= 0 else reward_center - reward_width
            body.append(f'<rect x="{reward_x:.1f}" y="{y}" width="{reward_width:.1f}" height="24" rx="12" fill="{color}"/>')
        reward_label = summary_coverage(
            reward,
            run["rewardObservedTrials"],
            run["completedTrials"],
            lambda value: format_number(value, 3),
            always=True,
        )
        body.append(f'<text x="{right_x + panel_w - 24}" y="{y + 18}" text-anchor="end" class="value">{esc(reward_label)}</text>')
        if run["erroredTrials"]:
            body.append(f'<circle cx="{left_x + 171}" cy="{y + 12}" r="9" fill="#FB7185"/>')
            body.append(f'<text x="{left_x + 171}" y="{y + 16}" text-anchor="middle" font-size="10" fill="#111827">{run["erroredTrials"]}</text>')
    body.append(f'<text x="56" y="{height - 34}" class="small">A red badge is the number of execution errors. A dot marks the selected baseline. Aggregate views do not replace native fairness checks.</text>')
    return svg_document(
        f"{report['title']} — quality comparison",
        "Horizontal bars compare pass rate and mean reward for each Harbor execution.",
        width,
        height,
        "\n".join(body),
    )


def render_resource_svg(report: dict[str, Any]) -> str:
    runs = report["runs"]
    width = 1640
    row_height = 86
    height = max(680, 302 + len(runs) * row_height)
    panel_y = 196
    panel_h = len(runs) * row_height + 128
    body = [
        svg_header(
            report,
            width,
            "Resource accounting: token composition, reported cost, agent time, and wall time.",
        ),
        f'<rect x="48" y="{panel_y}" width="1544" height="{panel_h}" rx="20" class="panel"/>',
        f'<text x="72" y="{panel_y + 42}" class="section">Run</text>',
        f'<text x="318" y="{panel_y + 42}" class="section">Tokens · input includes cache</text>',
        f'<text x="1030" y="{panel_y + 42}" class="section">Cost USD</text>',
        f'<text x="1280" y="{panel_y + 42}" class="section">Time</text>',
    ]
    total_values = []
    for run in runs:
        input_metric = run["tokens"]["input"]
        cache_metric = run["tokens"]["cache"]
        output_metric = run["tokens"]["output"]
        input_tokens = token_total(run, "input")
        output_tokens = token_total(run, "output")
        stack_is_complete = bool(
            input_metric
            and cache_metric
            and output_metric
            and input_metric["complete"]
            and cache_metric["complete"]
            and output_metric["complete"]
        )
        if stack_is_complete:
            try:
                drawn_total = math.fsum((input_tokens, output_tokens))
            except OverflowError as error:
                raise ReportError("token chart total overflowed") from error
            if not math.isfinite(drawn_total):
                raise ReportError("token chart total must be finite")
            total_values.append(drawn_total)
        else:
            reported_total = token_total(run, "total")
            if reported_total is not None:
                total_values.append(reported_total)
    cost_values = [run["costUsd"] for run in runs if run["costUsd"] is not None]
    time_values = [
        value
        for run in runs
        for value in (run["agentTimeSeconds"], run["wallTimeSeconds"])
        if value is not None
    ]
    token_max = nice_max(max(total_values or [1]))
    cost_max = nice_max(max(cost_values or [1]), floor=0.01)
    time_max = nice_max(max(time_values or [1]))
    token_x, token_w = 318, 610
    cost_x, cost_w = 1030, 180
    time_x, time_w = 1280, 260
    legend_y = panel_y + panel_h - 42
    body.extend(
        [
            f'<rect x="{token_x}" y="{legend_y - 10}" width="12" height="12" rx="3" fill="#38BDF8"/><text x="{token_x + 18}" y="{legend_y}" class="small">fresh input</text>',
            f'<rect x="{token_x + 112}" y="{legend_y - 10}" width="12" height="12" rx="3" fill="#A78BFA"/><text x="{token_x + 130}" y="{legend_y}" class="small">cached input</text>',
            f'<rect x="{token_x + 238}" y="{legend_y - 10}" width="12" height="12" rx="3" fill="#34D399"/><text x="{token_x + 256}" y="{legend_y}" class="small">output</text>',
            f'<rect x="{time_x}" y="{legend_y - 10}" width="12" height="12" rx="3" fill="#FBBF24"/><text x="{time_x + 18}" y="{legend_y}" class="small">agent</text>',
            f'<rect x="{time_x + 86}" y="{legend_y - 10}" width="12" height="12" rx="3" fill="#FB7185"/><text x="{time_x + 104}" y="{legend_y}" class="small">wall</text>',
        ]
    )
    for index, run in enumerate(runs):
        y = panel_y + 72 + index * row_height
        label = ("● " if run["runId"] == report["baselineRunId"] else "") + truncate(run["label"], 25)
        body.append(f'<text x="72" y="{y + 22}" class="label">{esc(label)}</text>')
        input_tokens = token_total(run, "input")
        cache_tokens = token_total(run, "cache")
        output_tokens = token_total(run, "output")
        input_metric = run["tokens"]["input"]
        cache_metric = run["tokens"]["cache"]
        output_metric = run["tokens"]["output"]
        stack_is_complete = bool(
            input_metric
            and cache_metric
            and output_metric
            and input_metric["complete"]
            and cache_metric["complete"]
            and output_metric["complete"]
        )
        total_metric = run["tokens"]["total"]
        total_tokens = total_metric["total"] if total_metric else None
        body.append(f'<rect x="{token_x}" y="{y}" width="{token_w}" height="26" rx="8" fill="#1E293B"/>')
        if stack_is_complete:
            cache = min(cache_tokens or 0, input_tokens)
            fresh = max(0, input_tokens - cache)
            cursor = token_x
            for value, color in ((fresh, "#38BDF8"), (cache, "#A78BFA"), (output_tokens, "#34D399")):
                remaining = max(0.0, token_w - (cursor - token_x))
                segment = min(remaining, (value / token_max) * token_w)
                if segment > 0:
                    body.append(f'<rect x="{cursor:.1f}" y="{y}" width="{segment:.1f}" height="26" rx="5" fill="{color}"/>')
                    cursor += segment
        elif total_tokens is not None:
            segment = min(float(token_w), (total_tokens / token_max) * token_w)
            body.append(f'<rect x="{token_x}" y="{y}" width="{segment:.1f}" height="26" rx="8" fill="#64748B"/>')
        cache_label = token_coverage(run, "cache")
        reasoning_label = token_coverage(run, "reasoning")
        total_label = summary_coverage(
            total_tokens,
            total_metric["count"] if total_metric else 0,
            run["completedTrials"],
            compact,
        )
        body.append(f'<text x="{token_x}" y="{y + 48}" class="small">total {esc(total_label)} · cache {esc(cache_label)} · reasoning {esc(reasoning_label)}</text>')
        body.append(f'<rect x="{cost_x}" y="{y}" width="{cost_w}" height="18" rx="9" fill="#1E293B"/>')
        if run["costUsd"] is not None:
            cost_width = min(float(cost_w), (run["costUsd"] / cost_max) * cost_w)
            body.append(f'<rect x="{cost_x}" y="{y}" width="{cost_width:.1f}" height="18" rx="9" fill="#22D3EE"/>')
        cost_label = summary_coverage(
            run["costUsd"],
            run["costObservedTrials"],
            run["completedTrials"],
            lambda value: compact(value, money=True),
        )
        body.append(f'<text x="{cost_x}" y="{y + 43}" class="value">{esc(cost_label)}</text>')
        for offset, value, color, prefix in (
            (0, run["agentTimeSeconds"], "#FBBF24", "A"),
            (24, run["wallTimeSeconds"], "#FB7185", "W"),
        ):
            body.append(f'<text x="{time_x - 20}" y="{y + offset + 13}" text-anchor="end" class="small">{prefix}</text>')
            body.append(f'<rect x="{time_x}" y="{y + offset}" width="{time_w}" height="15" rx="7.5" fill="#1E293B"/>')
            if value is not None:
                bar_width = min(float(time_w), (value / time_max) * time_w)
                body.append(f'<rect x="{time_x}" y="{y + offset}" width="{bar_width:.1f}" height="15" rx="7.5" fill="{color}"/>')
        agent_label = summary_coverage(
            run["agentTimeSeconds"],
            run["agentTimeObservedTrials"],
            run["completedTrials"],
            lambda value: compact(value) + "s",
        )
        body.append(f'<text x="{time_x}" y="{y + 62}" class="small">{esc(agent_label)} agent · {esc(compact(run["wallTimeSeconds"]))}s wall</text>')
    body.append(f'<text x="56" y="{height - 32}" class="small">Token scale: {esc(compact(token_max))}. Cost scale: {esc(compact(cost_max, money=True))}. Time scale: {esc(compact(time_max))} seconds. Reasoning is supplemental and never silently added to total.</text>')
    return svg_document(
        f"{report['title']} — token, cost, and time comparison",
        "Stacked token bars distinguish fresh input, cached input, and output. Separate bars compare cost, agent time, and wall time.",
        width,
        height,
        "\n".join(body),
    )


def pareto_runs(points: list[tuple[dict[str, Any], float, float]]) -> set[str]:
    frontier: set[str] = set()
    for run, cost, quality in points:
        dominated = any(
            other_cost <= cost
            and other_quality >= quality
            and (other_cost < cost or other_quality > quality)
            for other, other_cost, other_quality in points
            if other is not run
        )
        if not dominated:
            frontier.add(run["runId"])
    return frontier


def render_efficiency_svg(report: dict[str, Any]) -> str:
    runs = report["runs"]
    width = 1540
    height = max(860, 300 + len(runs) * 52)
    chart_x, chart_y, chart_w, chart_h = 104, 250, 910, 490
    points = [
        (run, run["costPerTrialUsd"], run["passRate"])
        for run in runs
        if run["complete"]
        and run["costPerTrialUsd"] is not None
        and run["tokensPerTrial"] is not None
        and run["agentSecondsPerTrial"] is not None
    ]
    cost_max = nice_max(max([point[1] for point in points] or [1]), floor=0.001)
    frontier = pareto_runs(points)
    body = [
        svg_header(
            report,
            width,
            "Higher quality and lower cost define the aggregate Pareto frontier; bubble area reflects tokens per trial.",
        ),
        '<rect x="48" y="190" width="1000" height="600" rx="20" class="panel"/>',
        f'<rect x="1076" y="190" width="416" height="{max(600, 110 + len(runs) * 52)}" rx="20" class="panel"/>',
        f'<text x="{chart_x}" y="{chart_y - 14}" class="section">Pass rate vs. cost per completed trial</text>',
        '<text x="1104" y="232" class="section">Efficiency details</text>',
    ]
    for tick in range(5):
        x = chart_x + chart_w * tick / 4
        y = chart_y + chart_h - chart_h * tick / 4
        body.append(f'<line x1="{x:.1f}" y1="{chart_y}" x2="{x:.1f}" y2="{chart_y + chart_h}" class="grid"/>')
        body.append(f'<line x1="{chart_x}" y1="{y:.1f}" x2="{chart_x + chart_w}" y2="{y:.1f}" class="grid"/>')
        body.append(f'<text x="{x:.1f}" y="{chart_y + chart_h + 26}" text-anchor="middle" class="small">{esc(compact(cost_max * (tick / 4), money=True))}</text>')
        body.append(f'<text x="{chart_x - 16}" y="{y + 4:.1f}" text-anchor="end" class="small">{tick * 25}%</text>')
    body.append(f'<text x="{chart_x + chart_w / 2}" y="{chart_y + chart_h + 58}" text-anchor="middle" class="small">cost per completed trial (USD) →</text>')
    body.append(f'<text x="28" y="{chart_y + chart_h / 2}" transform="rotate(-90 28 {chart_y + chart_h / 2})" text-anchor="middle" class="small">pass rate →</text>')
    frontier_points = sorted(
        [point for point in points if point[0]["runId"] in frontier], key=lambda item: item[1]
    )
    if len(frontier_points) > 1:
        path_data = " ".join(
            ("M" if index == 0 else "L")
            + f" {chart_x + (cost / cost_max) * chart_w:.1f} {chart_y + chart_h * (1 - quality):.1f}"
            for index, (_, cost, quality) in enumerate(frontier_points)
        )
        body.append(f'<path d="{path_data}" fill="none" stroke="#FBBF24" stroke-width="2" stroke-dasharray="7 7" opacity="0.8"/>')
    token_values = [run["tokensPerTrial"] for run, _, _ in points if run["tokensPerTrial"] is not None]
    token_max = max(token_values or [1])
    for index, (run, cost, quality) in enumerate(points):
        color = PALETTE[runs.index(run) % len(PALETTE)]
        x = chart_x + (cost / cost_max) * chart_w
        y = chart_y + chart_h * (1 - quality)
        token_value = run["tokensPerTrial"] or 0
        radius = 10 + 17 * math.sqrt(token_value / token_max) if token_max else 12
        if run["runId"] in frontier:
            body.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{radius + 7:.1f}" fill="none" stroke="#FBBF24" stroke-width="2"/>')
        if run["runId"] == report["baselineRunId"]:
            body.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{radius + 12:.1f}" fill="none" stroke="#E2E8F0" stroke-width="2" stroke-dasharray="4 5"/>')
        body.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{radius:.1f}" fill="{color}" fill-opacity="0.86" stroke="#F8FAFC" stroke-width="1.5"/>')
        label_y = y - radius - 18 if index % 2 == 0 else y + radius + 28
        body.append(f'<text x="{x:.1f}" y="{label_y:.1f}" text-anchor="middle" class="label">{esc(truncate(run["label"], 22))}</text>')
    if not points:
        body.append(f'<text x="{chart_x + chart_w / 2}" y="{chart_y + chart_h / 2}" text-anchor="middle" class="subtitle">No run with complete token, cost, and agent-time coverage is available for a frontier.</text>')
    for index, run in enumerate(runs):
        y = 274 + index * 52
        color = PALETTE[index % len(PALETTE)]
        body.append(f'<circle cx="1108" cy="{y - 5}" r="7" fill="{color}"/>')
        body.append(f'<text x="1126" y="{y}" class="label">{esc(truncate(run["label"], 28))}</text>')
        body.append(f'<text x="1126" y="{y + 19}" class="small">{esc(compact(run["tokensPerTrial"]))} tok/trial · {esc(compact(run["costPerPassUsd"], money=True))}/pass · {esc(compact(run["agentSecondsPerTrial"]))}s agent/trial</text>')
    footer_y = height - 30
    body.append(f'<text x="56" y="{footer_y}" class="small">Gold rings mark non-dominated aggregate points; dashed white marks the baseline. Missing or partial token, cost, or agent-time values are omitted from the frontier and its deltas.</text>')
    return svg_document(
        f"{report['title']} — efficiency frontier",
        "A scatter plot compares pass rate with cost per completed trial. Bubble size represents total tokens per trial.",
        width,
        height,
        "\n".join(body),
    )


def output_payloads(report: dict[str, Any]) -> dict[str, bytes]:
    return {
        "comparison-report.json": canonical_json(report),
        "comparison-report.md": render_markdown(report).encode("utf-8"),
        "quality-comparison.svg": render_quality_svg(report).encode("utf-8"),
        "resource-comparison.svg": render_resource_svg(report).encode("utf-8"),
        "efficiency-frontier.svg": render_efficiency_svg(report).encode("utf-8"),
    }


def require_clean_output_directory(target: Path) -> None:
    """Require an existing publication directory to contain one complete generation."""

    if target.is_symlink() or not target.is_dir():
        raise ReportError("existing output must be a real directory")
    entries = list(target.iterdir())
    names = {entry.name for entry in entries}
    expected = set(OUTPUT_FILES)
    if names != expected:
        raise ReportError(
            "existing output directory is not a closed consolidated report generation"
        )
    if any(entry.is_symlink() or not entry.is_file() for entry in entries):
        raise ReportError("existing output artifacts must be regular files")


def cleanup_generation(path: Path | None) -> None:
    """Remove a known temporary generation without traversing arbitrary content."""

    if path is None or not path.exists() or path.is_symlink():
        return
    for name in OUTPUT_FILES:
        with suppress(OSError):
            (path / name).unlink(missing_ok=True)
    with suppress(OSError):
        path.rmdir()


def write_outputs(output: Path, payloads: dict[str, bytes], overwrite: bool) -> None:
    nominal = output.absolute()
    if nominal.is_symlink():
        raise ReportError("output directory must not be a symbolic link")
    target = nominal.resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    lock_name = ID_PATTERN.sub("-", target.name).strip("-.") or "report"
    lock = target.parent / f".{lock_name}.publish-lock"
    try:
        lock.mkdir()
    except FileExistsError as error:
        raise ReportError("another publication is already targeting this output") from error
    temporary: Path | None = None
    backup: Path | None = None
    try:
        target_was_present = target.exists()
        if target_was_present:
            if not overwrite:
                raise ReportError("refusing to overwrite an existing output directory")
            require_clean_output_directory(target)
        temporary = Path(
            tempfile.mkdtemp(prefix=f".{lock_name}.tmp-", dir=target.parent)
        )
        for name in OUTPUT_FILES:
            (temporary / name).write_bytes(payloads[name])
        if target_was_present:
            if not target.exists():
                raise ReportError("existing output disappeared during publication")
            require_clean_output_directory(target)
            backup = Path(
                tempfile.mkdtemp(prefix=f".{lock_name}.backup-", dir=target.parent)
            )
            backup.rmdir()
            target.replace(backup)
            try:
                temporary.replace(target)
            except OSError:
                if not target.exists() and backup.exists():
                    backup.replace(target)
                    backup = None
                raise
            temporary = None
        else:
            if target.exists():
                raise ReportError("output appeared during publication")
            temporary.replace(target)
            temporary = None
        cleanup_generation(backup)
        backup = None
    except OSError as error:
        raise ReportError(f"cannot write consolidated report: {error}") from error
    finally:
        cleanup_generation(temporary)
        if backup is not None and backup.exists() and not target.exists():
            with suppress(OSError):
                backup.replace(target)
                backup = None
        with suppress(OSError):
            lock.rmdir()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Consolidate one or more Harbor final-report.json files into a sanitized "
            "Markdown comparison and three self-contained SVG charts."
        )
    )
    parser.add_argument("reports", nargs="+", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--title", default="Harbor execution comparison")
    parser.add_argument(
        "--baseline",
        help="opaque run label or runId; defaults to the first run",
    )
    parser.add_argument(
        "--generated-at",
        help="deterministic report timestamp; defaults to the latest source report timestamp",
    )
    parser.add_argument("--overwrite", action="store_true")
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        prepared = preflight_report_paths(args.reports)
        sources = [
            read_report(path, index, size)
            for index, (path, size) in enumerate(prepared)
        ]
        report = build_report(
            sources,
            title=require_text(args.title, "--title", maximum_length=160),
            baseline_selector=args.baseline,
            generated_at=args.generated_at,
        )
        write_outputs(args.output_dir, output_payloads(report), args.overwrite)
        sys.stdout.buffer.write(
            canonical_json(
                {
                    "ok": True,
                    "baselineRunId": report["baselineRunId"],
                    "runCount": len(report["runs"]),
                    "outputFiles": list(OUTPUT_FILES),
                }
            )
        )
        return 0
    except (OSError, ReportError, OverflowError, TypeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
