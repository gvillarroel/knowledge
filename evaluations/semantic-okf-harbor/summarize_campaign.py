#!/usr/bin/env python3
"""Aggregate an explicitly bound Semantic OKF Harbor campaign.

The input is deliberately a ledger, not a directory to scan.  Every binding
names one job root and one trial directory and pins the SHA-256 of both Harbor
``result.json``/``lock.json`` pairs.  This prevents a later run with a similar
name from being selected accidentally.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import statistics
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Mapping, Sequence

HERE = Path(__file__).resolve().parent
SCHEMA = "semantic-okf-harbor-campaign-bindings/1.0"
REPORT_SCHEMA = "semantic-okf-harbor-campaign-summary/1.0"
GENERATIONS = ("baseline", "evolved")
COHORTS = ("train", "dev", "holdout")
EXCLUSION_CATEGORIES = ("pre_agent_auth_failure", "delayed_duplicate", "pre_fix_grader")
REWARD_DIMENSIONS = (
    "reward",
    "quality_gate",
    "response_contract",
    "non_null_answer",
    "reference_validity",
    "all_evidence_valid",
    "evidence_validity",
    "evidence_recall",
    "evidence_precision",
    "complete_qrel_coverage",
    "mrr",
    "ndcg",
    "required_document_coverage",
    "authoritative_evidence_completeness",
    "atomic_claim_evidence_completeness",
    "important_negative_evidence_completeness",
)
HARD_COMPLETENESS = (
    "authoritative_evidence_completeness",
    "atomic_claim_evidence_completeness",
    "important_negative_evidence_completeness",
)
EXACT_GATES = (
    "response_contract",
    "non_null_answer",
    "reference_validity",
    "all_evidence_valid",
    "quality_gate",
)


class CampaignSummaryError(ValueError):
    """Raised when campaign evidence is ambiguous, mutated, or incomparable."""


def load_json(path: Path) -> Any:
    """Read one UTF-8 JSON object."""

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CampaignSummaryError(f"cannot read JSON {path}: {exc}") from exc


def sha256_file(path: Path) -> str:
    """Return the lowercase SHA-256 of one immutable input."""

    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError as exc:
        raise CampaignSummaryError(f"cannot hash {path}: {exc}") from exc


def _closed_keys(value: Mapping[str, Any], allowed: set[str], where: str) -> None:
    extras = sorted(set(value) - allowed)
    if extras:
        raise CampaignSummaryError(f"{where} has unknown fields: {', '.join(extras)}")


def _relative_path(raw: Any, where: str) -> Path:
    if not isinstance(raw, str) or not raw:
        raise CampaignSummaryError(f"{where} must be a non-empty relative POSIX path")
    posix = PurePosixPath(raw)
    if posix.is_absolute() or ".." in posix.parts or "." in posix.parts:
        raise CampaignSummaryError(f"{where} must stay within the evaluation directory")
    return Path(*posix.parts)


def _hash(raw: Any, where: str) -> str:
    if not isinstance(raw, str) or len(raw) != 64 or any(char not in "0123456789abcdef" for char in raw):
        raise CampaignSummaryError(f"{where} must be a lowercase SHA-256")
    return raw


def _number(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return float(value)


def _seconds(timing: Any) -> float | None:
    if not isinstance(timing, Mapping):
        return None
    start, finish = timing.get("started_at"), timing.get("finished_at")
    if not isinstance(start, str) or not isinstance(finish, str):
        return None
    try:
        duration = (datetime.fromisoformat(finish) - datetime.fromisoformat(start)).total_seconds()
    except ValueError:
        return None
    return duration if duration >= 0 else None


def _check_hash(path: Path, expected: Any, where: str) -> str:
    pinned = _hash(expected, where)
    actual = sha256_file(path)
    if actual != pinned:
        raise CampaignSummaryError(f"{where} mismatch: expected {pinned}, found {actual}")
    return actual


def _question_from_result(result: Mapping[str, Any]) -> str | None:
    task_name = result.get("task_name")
    if not isinstance(task_name, str):
        return None
    tail = task_name.rsplit("__", 1)[-1]
    return tail if len(tail) == 4 and tail.startswith("q") and tail[1:].isdigit() else None


def _skill_identity(lock: Mapping[str, Any]) -> tuple[str | None, str | None]:
    skills = lock.get("skills")
    if not isinstance(skills, list) or len(skills) != 1 or not isinstance(skills[0], Mapping):
        return None, None
    return skills[0].get("source"), skills[0].get("digest")


def _validate_runtime(result: Mapping[str, Any], lock: Mapping[str, Any], campaign: Mapping[str, Any]) -> None:
    runtime = campaign.get("runtime")
    runtime = runtime if isinstance(runtime, Mapping) else {}
    agent = result.get("agent_info")
    agent = agent if isinstance(agent, Mapping) else {}
    model_info = agent.get("model_info")
    model_info = model_info if isinstance(model_info, Mapping) else {}
    actual_model = f"{model_info.get('provider')}/{model_info.get('name')}"
    expected_model = runtime.get("model")
    if expected_model and actual_model != expected_model:
        raise CampaignSummaryError(f"trial model mismatch: expected {expected_model}, found {actual_model}")
    if runtime.get("agent") and agent.get("name") != runtime.get("agent"):
        raise CampaignSummaryError("trial agent does not match campaign runtime")
    if runtime.get("pi_version") and agent.get("version") != runtime.get("pi_version"):
        raise CampaignSummaryError("trial Pi version does not match campaign runtime")
    lock_agent = lock.get("agent")
    lock_agent = lock_agent if isinstance(lock_agent, Mapping) else {}
    if expected_model and lock_agent.get("model_name") != expected_model:
        raise CampaignSummaryError("trial lock model does not match campaign runtime")
    if runtime.get("mcp_used") is False and lock_agent.get("mcp_servers") not in ([], None):
        raise CampaignSummaryError("trial lock unexpectedly enables MCP")


def load_binding(entry: Mapping[str, Any], campaign: Mapping[str, Any], base: Path) -> dict[str, Any]:
    """Validate and load one exact append-only job/trial binding."""

    _closed_keys(
        entry,
        {
            "family", "generation", "cohort", "question_id", "result_root",
            "job_result_sha256", "job_lock_sha256", "trial_relative_dir",
            "trial_result_sha256", "trial_lock_sha256",
        },
        "binding",
    )
    family, generation = entry.get("family"), entry.get("generation")
    cohort, question = entry.get("cohort"), entry.get("question_id")
    if family not in campaign.get("families", []):
        raise CampaignSummaryError(f"unknown campaign family: {family}")
    if generation not in GENERATIONS:
        raise CampaignSummaryError(f"invalid generation: {generation}")
    if cohort not in COHORTS:
        raise CampaignSummaryError(f"invalid cohort: {cohort}")
    declared_questions = campaign.get("live_cases", {}).get(cohort, [])
    if question not in declared_questions:
        raise CampaignSummaryError(f"{question} is not declared in campaign cohort {cohort}")

    root = base / _relative_path(entry.get("result_root"), "result_root")
    trial_dir = root / _relative_path(entry.get("trial_relative_dir"), "trial_relative_dir")
    job_result_path, job_lock_path = root / "result.json", root / "lock.json"
    trial_result_path, trial_lock_path = trial_dir / "result.json", trial_dir / "lock.json"
    hashes = {
        "job_result_sha256": _check_hash(job_result_path, entry.get("job_result_sha256"), "job_result_sha256"),
        "job_lock_sha256": _check_hash(job_lock_path, entry.get("job_lock_sha256"), "job_lock_sha256"),
        "trial_result_sha256": _check_hash(trial_result_path, entry.get("trial_result_sha256"), "trial_result_sha256"),
        "trial_lock_sha256": _check_hash(trial_lock_path, entry.get("trial_lock_sha256"), "trial_lock_sha256"),
    }
    job_result, job_lock = load_json(job_result_path), load_json(job_lock_path)
    trial_result, trial_lock = load_json(trial_result_path), load_json(trial_lock_path)
    if not all(isinstance(value, Mapping) for value in (job_result, job_lock, trial_result, trial_lock)):
        raise CampaignSummaryError("bound Harbor files must contain JSON objects")
    trials = job_lock.get("trials")
    if not isinstance(trials, list) or len(trials) != 1 or trials[0] != trial_lock:
        raise CampaignSummaryError("job lock must contain exactly the bound trial lock")
    trial_config = trial_result.get("config")
    trial_config = trial_config if isinstance(trial_config, Mapping) else {}
    if trial_config.get("job_id") != job_result.get("id"):
        raise CampaignSummaryError("trial result is not owned by the bound Harbor job")
    if _question_from_result(trial_result) != question:
        raise CampaignSummaryError("bound trial result has a different question id")
    task = trial_lock.get("task")
    task = task if isinstance(task, Mapping) else {}
    if task.get("name") != question or task.get("source") != cohort or trial_result.get("source") != cohort:
        raise CampaignSummaryError("bound result/lock cohort or question does not match the ledger")
    _validate_runtime(trial_result, trial_lock, campaign)
    skill_source, skill_digest = _skill_identity(trial_lock)
    marker = f"/snapshots/content/{generation}/{family}/"
    normalized_source = str(skill_source).replace("\\", "/") if skill_source else ""
    if marker not in normalized_source:
        raise CampaignSummaryError(f"trial skill is not the bound {generation}/{family} snapshot")
    if not isinstance(skill_digest, str) or not skill_digest.startswith("sha256:"):
        raise CampaignSummaryError("trial lock does not pin one skill digest")

    verifier = trial_result.get("verifier_result")
    rewards_raw = verifier.get("rewards") if isinstance(verifier, Mapping) else {}
    rewards_raw = rewards_raw if isinstance(rewards_raw, Mapping) else {}
    rewards = {name: _number(rewards_raw.get(name)) for name in REWARD_DIMENSIONS}
    unexpected_rewards = sorted(set(rewards_raw) - set(REWARD_DIMENSIONS))
    if unexpected_rewards:
        raise CampaignSummaryError(f"trial has unknown reward dimensions: {', '.join(unexpected_rewards)}")
    out_of_range = [name for name, value in rewards.items() if value is not None and not 0.0 <= value <= 1.0]
    if out_of_range:
        raise CampaignSummaryError(f"trial reward dimensions must be within [0, 1]: {', '.join(out_of_range)}")
    task_checksum = trial_result.get("task_checksum")
    if not isinstance(task_checksum, str) or not task_checksum:
        raise CampaignSummaryError("trial result does not expose a task checksum")
    exception = trial_result.get("exception_info")
    exception_type = exception.get("exception_type") if isinstance(exception, Mapping) else None
    agent_result = trial_result.get("agent_result")
    agent_result = agent_result if isinstance(agent_result, Mapping) else {}
    return {
        "family": family,
        "generation": generation,
        "cohort": cohort,
        "question_id": question,
        "result_root": entry["result_root"],
        "trial_relative_dir": entry["trial_relative_dir"],
        **hashes,
        "task_checksum": task_checksum,
        "skill_digest": skill_digest,
        "rewards": rewards,
        "exception_type": exception_type,
        "latency_seconds": _seconds(trial_result.get("agent_execution")),
        "input_tokens": _number(agent_result.get("n_input_tokens")),
        "cache_tokens": _number(agent_result.get("n_cache_tokens")),
        "output_tokens": _number(agent_result.get("n_output_tokens")),
    }


def _mean(values: Iterable[float]) -> float | None:
    present = list(values)
    return statistics.fmean(present) if present else None


def aggregate(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Aggregate every declared dimension without inventing missing scores."""

    errors = Counter(str(row["exception_type"]) for row in rows if row.get("exception_type"))
    metrics: dict[str, Any] = {}
    for name in REWARD_DIMENSIONS:
        values = [row["rewards"][name] for row in rows if row["rewards"].get(name) is not None]
        metrics[name] = {"mean": _mean(values), "observed_trials": len(values), "total_trials": len(rows)}
    resources: dict[str, Any] = {}
    for name in ("latency_seconds", "input_tokens", "cache_tokens", "output_tokens"):
        values = [float(row[name]) for row in rows if row.get(name) is not None]
        resources[name] = {"mean": _mean(values), "total": sum(values) if values else None, "observed_trials": len(values)}
    return {
        "trials": len(rows),
        "runtime_errors": sum(errors.values()),
        "runtime_errors_by_type": dict(sorted(errors.items())),
        "metrics": metrics,
        "resources": resources,
    }


def _pair_rows(rows: Sequence[Mapping[str, Any]], expected: set[tuple[str, str, str]]) -> tuple[dict[Any, Any], list[Any]]:
    indexed: dict[tuple[str, str, str, str], Mapping[str, Any]] = {}
    for row in rows:
        key = (row["family"], row["cohort"], row["question_id"], row["generation"])
        if key in indexed:
            raise CampaignSummaryError(f"duplicate campaign binding: {'/'.join(key)}")
        indexed[key] = row
    missing = []
    pairs: dict[tuple[str, str, str], dict[str, Mapping[str, Any]]] = {}
    for key in sorted(expected):
        pair = {generation: indexed.get((*key, generation)) for generation in GENERATIONS}
        absent = [generation for generation, value in pair.items() if value is None]
        if absent:
            missing.extend({"family": key[0], "cohort": key[1], "question_id": key[2], "generation": generation} for generation in absent)
        else:
            if pair["baseline"]["task_checksum"] != pair["evolved"]["task_checksum"]:
                raise CampaignSummaryError(f"baseline/evolved task checksum differs for {'/'.join(key)}")
            pairs[key] = pair
    extras = sorted(set(indexed) - {(*key, generation) for key in expected for generation in GENERATIONS})
    if extras:
        raise CampaignSummaryError(f"bindings contain undeclared matrix entries: {extras}")
    return pairs, missing


def _metric_mean(summary: Mapping[str, Any], name: str) -> float | None:
    return summary["metrics"][name]["mean"]


def _promotion(family: str, aggregates: Mapping[str, Any], external: Mapping[str, Any]) -> dict[str, Any]:
    baseline = aggregates.get("dev", {}).get(family, {}).get("baseline")
    evolved = aggregates.get("dev", {}).get(family, {}).get("evolved")
    checks: dict[str, bool | None] = {}
    if baseline is None or evolved is None:
        checks["dev_pair_available"] = False
    else:
        checks["dev_pair_available"] = True
        checks["runtime_errors_zero"] = evolved["runtime_errors"] == 0
        for metric in EXACT_GATES:
            checks[f"{metric}_is_one"] = _metric_mean(evolved, metric) == 1.0
        before_reward, after_reward = _metric_mean(baseline, "reward"), _metric_mean(evolved, "reward")
        checks["dev_reward_no_regression"] = (
            None if before_reward is None or after_reward is None else after_reward >= before_reward
        )
        before_hard = [_metric_mean(baseline, name) for name in HARD_COMPLETENESS]
        after_hard = [_metric_mean(evolved, name) for name in HARD_COMPLETENESS]
        checks["dev_hard_completeness_no_regression"] = (
            None
            if any(value is None for value in before_hard + after_hard)
            else min(after_hard) >= min(before_hard)
        )
    deterministic = external.get(family, {}).get("deterministic_retrieval_no_regression")
    checks["deterministic_retrieval_no_regression"] = deterministic if isinstance(deterministic, bool) else None
    if any(value is False for value in checks.values()):
        decision = "rejected"
    elif any(value is None for value in checks.values()):
        decision = "pending"
    else:
        decision = "promoted"
    return {
        "decision": decision,
        "checks": checks,
        "semantic_correctness_assessed": False,
        "note": "Passing evidence and contract gates does not establish semantic answer correctness.",
    }


def summarize(bindings_path: Path, campaign_path: Path, *, allow_incomplete: bool = False) -> dict[str, Any]:
    """Validate a binding ledger and return a compact campaign report."""

    bindings, campaign = load_json(bindings_path), load_json(campaign_path)
    if not isinstance(bindings, Mapping) or not isinstance(campaign, Mapping):
        raise CampaignSummaryError("bindings and campaign files must contain JSON objects")
    _closed_keys(
        bindings,
        {"schema_version", "campaign_id", "entries", "external_gates", "excluded_runs"},
        "bindings document",
    )
    if bindings.get("schema_version") != SCHEMA:
        raise CampaignSummaryError(f"bindings schema must be {SCHEMA}")
    if bindings.get("campaign_id") != campaign.get("campaign_id"):
        raise CampaignSummaryError("bindings campaign_id does not match campaign.json")
    entries = bindings.get("entries")
    if not isinstance(entries, list):
        raise CampaignSummaryError("bindings entries must be an array")
    external = bindings.get("external_gates", {})
    if not isinstance(external, Mapping):
        raise CampaignSummaryError("external_gates must be an object")
    unknown_external_families = sorted(set(external) - set(campaign.get("families", [])))
    if unknown_external_families:
        raise CampaignSummaryError(f"external_gates has unknown families: {', '.join(unknown_external_families)}")
    for family, gates in external.items():
        if not isinstance(gates, Mapping):
            raise CampaignSummaryError(f"external_gates.{family} must be an object")
        _closed_keys(gates, {"deterministic_retrieval_no_regression"}, f"external_gates.{family}")
        value = gates.get("deterministic_retrieval_no_regression")
        if value is not None and not isinstance(value, bool):
            raise CampaignSummaryError(
                f"external_gates.{family}.deterministic_retrieval_no_regression must be boolean or null"
            )
    rows = [load_binding(entry, campaign, bindings_path.resolve().parent) for entry in entries if isinstance(entry, Mapping)]
    if len(rows) != len(entries):
        raise CampaignSummaryError("every binding entry must be an object")
    excluded_raw = bindings.get("excluded_runs", [])
    if not isinstance(excluded_raw, list):
        raise CampaignSummaryError("excluded_runs must be an array")
    excluded: list[dict[str, str]] = []
    bound_roots = {row["result_root"] for row in rows}
    seen_excluded: set[str] = set()
    for index, item in enumerate(excluded_raw):
        if not isinstance(item, Mapping):
            raise CampaignSummaryError("every excluded_runs entry must be an object")
        _closed_keys(item, {"result_root", "category", "reason"}, f"excluded_runs[{index}]")
        relative = _relative_path(item.get("result_root"), f"excluded_runs[{index}].result_root")
        root_name = PurePosixPath(*relative.parts).as_posix()
        if root_name in seen_excluded:
            raise CampaignSummaryError(f"duplicate excluded result root: {root_name}")
        if root_name in bound_roots:
            raise CampaignSummaryError(f"result root cannot be both bound and excluded: {root_name}")
        if not (bindings_path.resolve().parent / relative).is_dir():
            raise CampaignSummaryError(f"excluded result root does not exist: {root_name}")
        category, reason = item.get("category"), item.get("reason")
        if category not in EXCLUSION_CATEGORIES:
            raise CampaignSummaryError(f"invalid exclusion category: {category}")
        if not isinstance(reason, str) or not reason.strip():
            raise CampaignSummaryError(f"excluded_runs[{index}].reason must be a non-empty string")
        seen_excluded.add(root_name)
        excluded.append({"result_root": root_name, "category": category, "reason": reason.strip()})
    expected = {
        (family, cohort, question)
        for family in campaign.get("families", [])
        for cohort in COHORTS
        for question in campaign.get("live_cases", {}).get(cohort, [])
    }
    pairs, missing = _pair_rows(rows, expected)
    if missing and not allow_incomplete:
        raise CampaignSummaryError(f"campaign matrix is incomplete ({len(missing)} missing bindings)")

    aggregates: dict[str, Any] = {}
    for cohort in COHORTS:
        aggregates[cohort] = {}
        for family in campaign.get("families", []):
            aggregates[cohort][family] = {}
            for generation in GENERATIONS:
                selected = [
                    row for row in rows
                    if row["cohort"] == cohort and row["family"] == family and row["generation"] == generation
                ]
                if selected:
                    aggregates[cohort][family][generation] = aggregate(selected)
    promotions = {
        family: _promotion(family, aggregates, external)
        for family in campaign.get("families", [])
    }
    compact_trials = [
        {key: row[key] for key in (
            "family", "generation", "cohort", "question_id", "result_root", "trial_relative_dir",
            "job_result_sha256", "job_lock_sha256", "trial_result_sha256", "trial_lock_sha256",
            "task_checksum", "skill_digest", "exception_type",
        )}
        for row in sorted(rows, key=lambda item: (COHORTS.index(item["cohort"]), item["family"], item["generation"], item["question_id"]))
    ]
    return {
        "schema_version": REPORT_SCHEMA,
        "campaign_id": campaign.get("campaign_id"),
        "status": "complete" if not missing else "incomplete",
        "binding_ledger_sha256": sha256_file(bindings_path),
        "campaign_sha256": sha256_file(campaign_path),
        "reward_dimensions": list(REWARD_DIMENSIONS),
        "paired_cases": len(pairs),
        "missing_bindings": missing,
        "aggregates": aggregates,
        "promotion": promotions,
        "excluded_runs": sorted(excluded, key=lambda item: item["result_root"]),
        "trials": compact_trials,
        "interpretation": {
            "semantic_correctness_assessed": False,
            "statement": "Harbor evidence sufficiency, retrieval, validity, and response-contract metrics are not a semantic correctness judgment.",
            "promotion_scope": "Promotion applies only the declared mechanical gates; semantic answer review remains a separate evaluation dimension.",
        },
    }


def _fmt(value: Any, *, integer: bool = False) -> str:
    if value is None:
        return "—"
    return f"{value:,.0f}" if integer else f"{value:.4f}"


def _gate(value: bool | None) -> str:
    """Render one non-compensating gate disposition without collapsing unknowns."""

    return "pass" if value is True else "fail" if value is False else "pending"


def _metric_table(report: Mapping[str, Any], cohort: str, dimensions: Sequence[str]) -> list[str]:
    labels = [name.replace("_", "<br>") for name in dimensions]
    lines = [
        "| Family | Generation | Trials | " + " | ".join(labels) + " |",
        "|---|---|---:|" + "---:|" * len(dimensions),
    ]
    for family, generations in report["aggregates"][cohort].items():
        for generation in GENERATIONS:
            summary = generations.get(generation)
            if summary is None:
                continue
            metrics = [_fmt(summary["metrics"][name]["mean"]) for name in dimensions]
            lines.append(f"| {family} | {generation} | {summary['trials']} | " + " | ".join(metrics) + " |")
    return lines


def markdown(report: Mapping[str, Any]) -> str:
    """Render cohort-separated English score, completeness, and resource tables."""

    lines = [
        "# Semantic OKF Harbor Campaign Comparison",
        "",
        f"Campaign: `{report['campaign_id']}`. Status: `{report['status']}`. Paired cases: {report['paired_cases']}.",
        "",
        "All sixteen Harbor reward dimensions are reported below. A dash means Harbor did not emit that dimension; it is not silently converted to zero.",
    ]
    core = REWARD_DIMENSIONS[:10]
    completeness = REWARD_DIMENSIONS[10:]
    for cohort in COHORTS:
        lines.extend(["", f"## {cohort.title()}", "", "### Gates and retrieval", ""])
        lines.extend(_metric_table(report, cohort, core))
        lines.extend(["", "### Ranking and hard-question completeness", ""])
        lines.extend(_metric_table(report, cohort, completeness))
        lines.extend([
            "", "### Runtime and resources", "",
            "| Family | Generation | Errors | Mean latency (s) | Total input tokens | Total cache tokens | Total output tokens |",
            "|---|---|---:|---:|---:|---:|---:|",
        ])
        for family, generations in report["aggregates"][cohort].items():
            for generation in GENERATIONS:
                summary = generations.get(generation)
                if summary is None:
                    continue
                resources = summary["resources"]
                lines.append(
                    f"| {family} | {generation} | {summary['runtime_errors']} | "
                    f"{_fmt(resources['latency_seconds']['mean'])} | "
                    f"{_fmt(resources['input_tokens']['total'], integer=True)} | "
                    f"{_fmt(resources['cache_tokens']['total'], integer=True)} | "
                    f"{_fmt(resources['output_tokens']['total'], integer=True)} |"
                )
    lines.extend([
        "", "## Promotion gates", "",
        "| Family | Decision | Runtime | Contract | Non-null | Reference | All evidence | Quality | Dev reward | Hard completeness | Deterministic 40 |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ])
    for family, promotion in report["promotion"].items():
        checks = promotion["checks"]
        lines.append(
            f"| {family} | {promotion['decision']} | {_gate(checks.get('runtime_errors_zero'))} | "
            f"{_gate(checks.get('response_contract_is_one'))} | {_gate(checks.get('non_null_answer_is_one'))} | "
            f"{_gate(checks.get('reference_validity_is_one'))} | {_gate(checks.get('all_evidence_valid_is_one'))} | "
            f"{_gate(checks.get('quality_gate_is_one'))} | {_gate(checks.get('dev_reward_no_regression'))} | "
            f"{_gate(checks.get('dev_hard_completeness_no_regression'))} | "
            f"{_gate(checks.get('deterministic_retrieval_no_regression'))} |"
        )
    lines.extend([
        "", "## Excluded runs", "",
        "These roots are documented for auditability but never participate in any aggregate or promotion decision.",
        "", "| Result root | Category | Reason |", "|---|---|---|",
    ])
    for item in report.get("excluded_runs", []):
        lines.append(f"| `{item['result_root']}` | {item['category']} | {item['reason']} |")
    lines.extend([
        "",
        "Promotion gates are non-compensating: one failed required check rejects the candidate. Mechanical evidence sufficiency and response-contract compliance do **not** establish semantic answer correctness; that requires a separate answer review.",
        "",
    ])
    return "\n".join(lines)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bindings", type=Path, required=True, help="Explicit hash-pinned campaign ledger")
    parser.add_argument("--campaign", type=Path, default=HERE / "campaign.json")
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-markdown", type=Path, required=True)
    parser.add_argument("--allow-incomplete", action="store_true", help="Report missing matrix entries instead of failing")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    report = summarize(args.bindings.resolve(), args.campaign.resolve(), allow_incomplete=args.allow_incomplete)
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_markdown.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.output_markdown.write_text(markdown(report), encoding="utf-8")
    print(json.dumps({"status": report["status"], "paired_cases": report["paired_cases"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
