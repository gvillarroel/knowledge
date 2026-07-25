#!/usr/bin/env python3
"""Recalculate GraphRAG trial tables with the current mechanical metric contract."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
import tempfile
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any, Mapping, Sequence

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
GRADER = REPO / "evaluations/semantic-okf-harbor/grader"
for import_root in (HERE, GRADER):
    if str(import_root) not in sys.path:
        sys.path.insert(0, str(import_root))

import audit_response_coverage as audit  # noqa: E402
import dataset_tool as data  # noqa: E402
import score as grader  # noqa: E402
from trace_status import classify_pi_trace  # noqa: E402

SCHEMA_VERSION = "graphrag-current-metrics-evaluation-table/1.0"
DIAGNOSTICS_SCHEMA = "semantic-okf-harbor-redacted-diagnostics/3.0"
QUESTION_PREFIX = re.compile(r"^(q[0-9]{3})")
WSL_PATH = re.compile(r"^/mnt/([A-Za-z])/(.*)$")
METRIC_FIELDS = (
    "response_contract",
    "non_null_answer",
    "reference_validity",
    "evidence_validity",
    "all_evidence_valid",
    "evidence_precision",
    "evidence_recall",
    "mrr",
    "ndcg",
    "complete_qrel_coverage",
    "required_document_coverage",
    "authoritative_evidence_anchor_coverage",
    "answer_claim_anchor_coverage",
    "important_negative_anchor_coverage",
    "minimum_document_coverage",
    "minimum_document_gate",
    "minimum_focus_document_gate",
    "evidence_contract_gate",
    "mechanical_qualification_gate",
    "mechanical_utility",
    "reward",
)
DEFAULT_TASKS = (
    REPO
    / "evaluations/runs/graphrag-current-metrics-rescore-20260724/tasks"
)
DEFAULT_JSON = (
    HERE
    / "reports/20260724-graphrag-papers-40-current-metrics-table.json"
)
DEFAULT_MARKDOWN = (
    HERE
    / "reports/20260724-graphrag-papers-40-current-metrics-table.md"
)


class RecalculationError(ValueError):
    """Raised when immutable evidence cannot be recalculated consistently."""


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RecalculationError(f"expected a JSON object: {path}")
    return value


def _optional_json(path: Path) -> dict[str, Any]:
    return _load_json(path) if path.is_file() else {}


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _repo_relative(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(REPO.resolve()).as_posix()
    except ValueError:
        return str(resolved)


def _native_path(value: str) -> Path:
    direct = Path(value)
    if direct.exists():
        return direct
    match = WSL_PATH.fullmatch(value)
    if match is not None:
        return Path(f"{match.group(1).upper()}:/{match.group(2)}")
    return direct


def _task_tests_for_trial(trial: Path, question_id: str) -> Path:
    result = _optional_json(trial / "result.json")
    raw_path: Any = None
    task_id = result.get("task_id")
    if isinstance(task_id, Mapping):
        raw_path = task_id.get("path")
    config = result.get("config")
    if not isinstance(raw_path, str) and isinstance(config, Mapping):
        task = config.get("task")
        if isinstance(task, Mapping):
            raw_path = task.get("path")
    if not isinstance(raw_path, str):
        job_config = _load_json(trial.parent / "config.json")
        datasets = job_config.get("datasets")
        if (
            not isinstance(datasets, list)
            or len(datasets) != 1
            or not isinstance(datasets[0], Mapping)
            or not isinstance(datasets[0].get("path"), str)
        ):
            raise RecalculationError(
                f"cannot resolve native task for {trial}"
            )
        raw_path = f"{datasets[0]['path'].rstrip('/')}/{question_id}"
    tests = _native_path(raw_path) / "tests"
    required = (
        tests / "question.json",
        tests / "records.jsonl",
        tests / "source-combination.json",
    )
    missing = [_repo_relative(path) for path in required if not path.is_file()]
    if missing:
        raise RecalculationError(
            f"{trial.name}: native task inputs are absent: {missing}"
        )
    return tests


def _current_task_index(tasks_root: Path) -> tuple[
    dict[str, Path],
    dict[str, Any],
]:
    manifest = _load_json(tasks_root / "manifest.json")
    if (
        manifest.get("dataset_id") != "graphrag-papers-40"
        or manifest.get("family") != "legacy"
        or manifest.get("mode") != "consult-only"
        or manifest.get("question_count") != 40
    ):
        raise RecalculationError(
            "current task tree must be the 40-question legacy consult-only tree"
        )
    descriptor = (
        HERE / "datasets/graphrag-papers-40.json"
    )
    source_hashes = manifest.get("source_hashes")
    if (
        not isinstance(source_hashes, Mapping)
        or source_hashes.get("dataset_descriptor")
        != _sha256_file(descriptor)
    ):
        raise RecalculationError(
            "current task tree is not bound to the current dataset descriptor"
        )
    result: dict[str, Path] = {}
    for question_path in sorted(tasks_root.glob("*/*/tests/question.json")):
        question_id = question_path.parent.parent.name
        if (
            QUESTION_PREFIX.fullmatch(question_id) is None
            or question_id in result
        ):
            raise RecalculationError(
                f"invalid or duplicate current task: {question_path}"
            )
        result[question_id] = question_path.parent
    expected = {f"q{index:03d}" for index in range(1, 41)}
    if set(result) != expected:
        raise RecalculationError(
            "current task tree does not contain q001 through q040 exactly once"
        )
    return result, manifest


def _score_trace(
    pi_log: Path,
    *,
    current_tests: Path,
    native_tests: Path,
) -> tuple[dict[str, float], dict[str, Any]]:
    ground_truth = current_tests / "hard-ground-truth.json"
    authority_root = native_tests / "authority"
    if ground_truth.is_file() and not authority_root.is_dir():
        authority_root = current_tests / "authority"
    try:
        rewards, diagnostics = grader.score(
            argparse.Namespace(
                pi_log=pi_log,
                question=current_tests / "question.json",
                ledger=native_tests / "records.jsonl",
                crosswalk=native_tests / "source-combination.json",
                ground_truth=ground_truth if ground_truth.is_file() else None,
                authority_root=authority_root,
            )
        )
    except (
        OSError,
        UnicodeError,
        grader.ScoreError,
        KeyError,
        TypeError,
        ValueError,
    ) as exc:
        raise RecalculationError(
            f"current grader failed for {pi_log}: {exc}"
        ) from exc
    if diagnostics.get("schema_version") != DIAGNOSTICS_SCHEMA:
        raise RecalculationError(
            f"unexpected diagnostics schema for {pi_log}"
        )
    normalized: dict[str, float] = {}
    for name in METRIC_FIELDS:
        value = rewards.get(name)
        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(float(value))
        ):
            raise RecalculationError(
                f"{pi_log}: missing or non-finite metric {name}"
            )
        normalized[name] = float(value)
    return normalized, diagnostics


def _model_metadata(
    trial_result: Mapping[str, Any],
    job_config: Mapping[str, Any],
) -> tuple[str | None, str | None]:
    agent_info = trial_result.get("agent_info")
    if isinstance(agent_info, Mapping):
        model = agent_info.get("model_info")
        if isinstance(model, Mapping):
            provider = model.get("provider")
            name = model.get("name")
            if isinstance(provider, str) and isinstance(name, str):
                return f"{provider}/{name}", str(
                    agent_info.get("version")
                )
    agents = job_config.get("agents")
    if (
        isinstance(agents, list)
        and agents
        and isinstance(agents[0], Mapping)
    ):
        model_name = agents[0].get("model_name")
        kwargs = agents[0].get("kwargs")
        version = (
            kwargs.get("version") if isinstance(kwargs, Mapping) else None
        )
        return (
            str(model_name) if isinstance(model_name, str) else None,
            str(version) if isinstance(version, str) else None,
        )
    return None, None


def _usage(trial_result: Mapping[str, Any]) -> dict[str, Any]:
    agent_result = trial_result.get("agent_result")
    agent_result = agent_result if isinstance(agent_result, Mapping) else {}
    input_tokens = agent_result.get("n_input_tokens")
    output_tokens = agent_result.get("n_output_tokens")
    cache_tokens = agent_result.get("n_cache_tokens")
    total = (
        int(input_tokens) + int(output_tokens)
        if isinstance(input_tokens, int)
        and not isinstance(input_tokens, bool)
        and isinstance(output_tokens, int)
        and not isinstance(output_tokens, bool)
        else None
    )
    return {
        "input_tokens_including_cache": input_tokens,
        "output_tokens": output_tokens,
        "cache_tokens_reported_separately": cache_tokens,
        "total_tokens": total,
    }


def _original_metrics(
    trial: Path,
    trial_result: Mapping[str, Any],
) -> tuple[dict[str, float], dict[str, Any]]:
    verifier_result = trial_result.get("verifier_result")
    rewards: Any = (
        verifier_result.get("rewards")
        if isinstance(verifier_result, Mapping)
        else None
    )
    if not isinstance(rewards, Mapping):
        rewards = _optional_json(trial / "verifier/reward.json")
    metrics = {
        key: float(value)
        for key, value in rewards.items()
        if isinstance(key, str)
        and isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(float(value))
    }
    diagnostics = _optional_json(trial / "verifier/diagnostics.json")
    return metrics, diagnostics


def _trial_rows(
    results_root: Path,
    *,
    current_tasks: Mapping[str, Path],
    reviewed: Mapping[str, Mapping[str, Any]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for pi_log in sorted(results_root.glob("*/q*__*/agent/pi.txt")):
        trial = pi_log.parents[1]
        job = trial.parent
        match = QUESTION_PREFIX.match(trial.name)
        if match is None or match.group(1) not in current_tasks:
            continue
        question_id = match.group(1)
        response_id = f"raw/{job.name}/{trial.name}"
        trace = classify_pi_trace(pi_log)
        trial_result = _optional_json(trial / "result.json")
        job_config = _load_json(job / "config.json")
        native_tests = _task_tests_for_trial(trial, question_id)
        metrics, diagnostics = _score_trace(
            pi_log,
            current_tests=current_tasks[question_id],
            native_tests=native_tests,
        )
        original, original_diagnostics = _original_metrics(
            trial,
            trial_result,
        )
        model, agent_version = _model_metadata(
            trial_result,
            job_config,
        )
        answer_text = trace.get("answer_text")
        manual = reviewed.get(response_id)
        original_reward = original.get("reward")
        current_reward = metrics["reward"]
        row: dict[str, Any] = {
            "response_id": response_id,
            "question_id": question_id,
            "job": job.name,
            "trial": trial.name,
            "trial_id": trial_result.get("id"),
            "started_at": trial_result.get("started_at"),
            "finished_at": trial_result.get("finished_at"),
            "model": model,
            "agent_version": agent_version,
            "task_checksum": trial_result.get("task_checksum"),
            "native_task_tests": _repo_relative(native_tests),
            "native_ledger_sha256": _sha256_file(
                native_tests / "records.jsonl"
            ),
            "current_question_sha256": _sha256_file(
                current_tasks[question_id] / "question.json"
            ),
            "trace": {
                "outcome": trace.get("outcome"),
                "failure_domain": trace.get("failure_domain"),
                "error_code": trace.get("error_code"),
                "stop_reason": trace.get("stop_reason"),
                "parsed_events": trace.get("parsed_events"),
            },
            "response_sha256": (
                _sha256_text(answer_text)
                if isinstance(answer_text, str)
                else None
            ),
            "reviewable_response": manual is not None,
            "semantic_verdict": (
                manual.get("semantic_verdict")
                if isinstance(manual, Mapping)
                else None
            ),
            "semantic_rationale": (
                manual.get("rationale")
                if isinstance(manual, Mapping)
                else None
            ),
            "original_metric_schema": original_diagnostics.get(
                "schema_version"
            ),
            "original_metrics": original,
            "current_metrics": metrics,
            "current_diagnostics": diagnostics,
            "reward_delta": (
                current_reward - original_reward
                if isinstance(original_reward, (int, float))
                and not isinstance(original_reward, bool)
                else None
            ),
            "exception_present": trial_result.get("exception_info") is not None,
            "usage": _usage(trial_result),
        }
        rows.append(row)
    return rows


def _reference_rows(
    collection: Mapping[str, Any],
    *,
    current_tasks: Mapping[str, Path],
) -> list[dict[str, Any]]:
    reviews = collection.get("reviews")
    validations = collection.get("validations")
    if not isinstance(reviews, list) or not isinstance(validations, list):
        raise RecalculationError("invalid pinned reference-answer collection")
    validation_by_id = {
        str(row.get("question_id")): row
        for row in validations
        if isinstance(row, Mapping)
    }
    rows: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(
        prefix="graphrag-reference-rescore-"
    ) as temporary:
        root = Path(temporary)
        for review in reviews:
            if not isinstance(review, Mapping):
                raise RecalculationError("invalid reference review row")
            question_id = str(review.get("question_id"))
            if question_id not in current_tasks:
                raise RecalculationError(
                    f"unknown reference question: {question_id}"
                )
            response = review.get("proposed_response")
            response_path = root / f"{question_id}.json"
            response_path.write_text(
                json.dumps(response, ensure_ascii=False),
                encoding="utf-8",
            )
            metrics, diagnostics = _score_trace(
                response_path,
                current_tests=current_tasks[question_id],
                native_tests=current_tasks[question_id],
            )
            validation = validation_by_id.get(question_id)
            if (
                not isinstance(validation, Mapping)
                or validation.get("status") != "pass"
                or metrics["mechanical_qualification_gate"] != 1.0
            ):
                raise RecalculationError(
                    f"{question_id}: reference calibration did not pass"
                )
            rows.append(
                {
                    "reference_id": f"reference/{question_id}",
                    "question_id": question_id,
                    "response_sha256": _sha256_file(response_path),
                    "semantic_verdict": "pass",
                    "semantic_target_count": validation.get(
                        "semantic_target_count"
                    ),
                    "hard_anchor_count": validation.get(
                        "hard_anchor_count"
                    ),
                    "current_metrics": metrics,
                    "current_diagnostics": diagnostics,
                    "evidence_count": validation.get("evidence_count"),
                    "independent_document_count": validation.get(
                        "independent_document_count"
                    ),
                    "evidence_source": (
                        "curated-reference-not-live-model-trial"
                    ),
                }
            )
    return rows


def _trial_order(row: Mapping[str, Any]) -> tuple[str, str, str]:
    return (
        str(row.get("finished_at") or row.get("started_at") or ""),
        str(row.get("job") or ""),
        str(row.get("trial") or ""),
    )


def _compact_trial(row: Mapping[str, Any] | None) -> dict[str, Any] | None:
    if row is None:
        return None
    metrics = row["current_metrics"]
    diagnostics = row["current_diagnostics"]
    return {
        "response_id": row["response_id"],
        "started_at": row.get("started_at"),
        "finished_at": row.get("finished_at"),
        "trace": {"outcome": row["trace"]["outcome"]},
        "semantic_verdict": row.get("semantic_verdict"),
        "current_metrics": {
            name: metrics[name]
            for name in (
                "response_contract",
                "mechanical_qualification_gate",
                "mechanical_utility",
                "reward",
            )
        },
        "current_diagnostics": {
            name: diagnostics[name]
            for name in (
                "valid_independent_document_count",
                "covered_qrel_count",
            )
        },
    }


def _compact_reference(row: Mapping[str, Any]) -> dict[str, Any]:
    metrics = row["current_metrics"]
    diagnostics = row["current_diagnostics"]
    return {
        "reference_id": row["reference_id"],
        "semantic_verdict": row["semantic_verdict"],
        "current_metrics": {
            name: metrics[name]
            for name in (
                "mechanical_qualification_gate",
                "mechanical_utility",
                "reward",
            )
        },
        "current_diagnostics": {
            name: diagnostics[name]
            for name in (
                "valid_independent_document_count",
                "covered_qrel_count",
            )
        },
    }


def _question_rows(
    dataset: Mapping[str, Any],
    *,
    trials: Sequence[Mapping[str, Any]],
    historical: Sequence[Mapping[str, Any]],
    references: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    cohorts = data.dataset_cohorts(dataset)
    cohort_by_question = {
        question_id: cohort
        for cohort in dataset["partition_cohorts"]
        for question_id in cohorts[cohort]
    }
    references_by_id = {
        str(row["question_id"]): row for row in references
    }
    result: list[dict[str, Any]] = []
    for index in range(1, 41):
        question_id = f"q{index:03d}"
        question_trials = [
            row for row in trials if row["question_id"] == question_id
        ]
        reviewed_raw = [
            row for row in question_trials if row["reviewable_response"]
        ]
        legacy = [
            row for row in historical if row["question_id"] == question_id
        ]
        verdicts = Counter(
            str(row["semantic_verdict"])
            for row in [*reviewed_raw, *legacy]
        )
        latest_trial = (
            max(question_trials, key=_trial_order)
            if question_trials
            else None
        )
        latest_reviewed = (
            max(reviewed_raw, key=_trial_order) if reviewed_raw else None
        )
        covered = bool(reviewed_raw or legacy)
        result.append(
            {
                "question_id": question_id,
                "cohort": cohort_by_question[question_id],
                "raw_trial_count": len(question_trials),
                "reviewable_raw_response_count": len(reviewed_raw),
                "legacy_reviewable_response_count": len(legacy),
                "reviewable_response_count": len(reviewed_raw) + len(legacy),
                "semantic_verdict_counts": dict(sorted(verdicts.items())),
                "current_mechanical_qualification_count": sum(
                    row["current_metrics"][
                        "mechanical_qualification_gate"
                    ]
                    == 1.0
                    for row in question_trials
                ),
                "latest_trial": _compact_trial(latest_trial),
                "latest_reviewed_response": _compact_trial(
                    latest_reviewed
                ),
                "reference": _compact_reference(
                    references_by_id[question_id]
                ),
                "empirical_coverage": "covered" if covered else "missing",
            }
        )
    return result


def _reward_delta_summary(
    trials: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    comparable = [
        row
        for row in trials
        if isinstance(row.get("reward_delta"), (int, float))
    ]
    increased = sum(float(row["reward_delta"]) > 1e-12 for row in comparable)
    decreased = sum(float(row["reward_delta"]) < -1e-12 for row in comparable)
    unchanged = len(comparable) - increased - decreased
    return {
        "comparable_trial_count": len(comparable),
        "increased_count": increased,
        "decreased_count": decreased,
        "unchanged_count": unchanged,
        "mean_original_reward": (
            sum(float(row["original_metrics"]["reward"]) for row in comparable)
            / len(comparable)
            if comparable
            else None
        ),
        "mean_current_reward": (
            sum(float(row["current_metrics"]["reward"]) for row in comparable)
            / len(comparable)
            if comparable
            else None
        ),
    }


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    """Build a lossless recalculation report without changing Harbor evidence."""

    dataset = data.load_dataset("graphrag-papers-40")
    dataset_validation = data.validate_dataset("graphrag-papers-40")
    questions = data.dataset_questions(dataset)
    question_ids = {row["normalized_id"] for row in questions}
    current_tasks, task_manifest = _current_task_index(args.current_tasks)

    reviewed_raw, discovered_trial_count = audit.raw_responses(
        args.results,
        question_ids,
    )
    raw_digest = audit.apply_raw_adjudications(
        reviewed_raw,
        args.raw_adjudications,
    )
    reviewed_by_id = {
        str(row["response_id"]): row for row in reviewed_raw
    }
    historical, historical_trial_count = audit.historical_responses(
        args.historical_campaign,
        args.historical_manual_review,
        question_ids,
    )
    trials = _trial_rows(
        args.results,
        current_tasks=current_tasks,
        reviewed=reviewed_by_id,
    )
    if len(trials) != discovered_trial_count:
        raise RecalculationError(
            "trial inventory changed between audit and current rescore"
        )

    collection_path = data.pinned_path(
        dataset["reference_answers"],
        "graphrag-papers-40 reference answers",
    )
    collection = _load_json(collection_path)
    references = _reference_rows(
        collection,
        current_tasks=current_tasks,
    )
    question_rows = _question_rows(
        dataset,
        trials=trials,
        historical=historical,
        references=references,
    )
    covered = [
        row["question_id"]
        for row in question_rows
        if row["empirical_coverage"] == "covered"
    ]
    missing = [
        row["question_id"]
        for row in question_rows
        if row["empirical_coverage"] == "missing"
    ]
    trace_outcomes = Counter(
        str(row["trace"]["outcome"]) for row in trials
    )
    semantic_verdicts = Counter(
        str(row["semantic_verdict"])
        for row in [*reviewed_raw, *historical]
    )
    summary_only = _load_json(args.summary_only_cells)
    summary_cells = summary_only.get("cells")
    summary_only_count = (
        len(summary_cells) if isinstance(summary_cells, list) else 0
    )
    descriptor_path = HERE / "datasets/graphrag-papers-40.json"
    grader_path = GRADER / "score.py"
    return {
        "schema_version": SCHEMA_VERSION,
        "report_date": args.report_date,
        "dataset_id": "graphrag-papers-40",
        "report_kind": "artifact-only-current-metrics-recalculation",
        "new_model_calls": 0,
        "dataset_validation": dataset_validation,
        "metric_contract": {
            "dataset_schema_version": dataset["schema_version"],
            "dataset_descriptor_sha256": _sha256_file(descriptor_path),
            "evaluation_policy": dataset["evaluation_policy"],
            "grader_path": _repo_relative(grader_path),
            "grader_sha256": _sha256_file(grader_path),
            "diagnostics_schema_version": DIAGNOSTICS_SCHEMA,
            "reward_semantics": (
                "mechanical-contract-and-focus-coverage-only"
            ),
            "rescore_method": (
                "current question policy plus each immutable trial's native "
                "ledger and source-combination crosswalk"
            ),
            "current_task_manifest_path": _repo_relative(
                args.current_tasks / "manifest.json"
            ),
            "current_task_manifest_sha256": _sha256_file(
                args.current_tasks / "manifest.json"
            ),
            "current_task_tree_sha256": data.tree_digest(
                args.current_tasks
            ),
            "current_task_source_hashes": task_manifest["source_hashes"],
        },
        "summary": {
            "dataset_question_count": 40,
            "raw_harbor_trial_count": len(trials),
            "raw_trials_rescored_with_current_metrics": len(trials),
            "trace_outcome_counts": dict(sorted(trace_outcomes.items())),
            "reviewable_raw_response_count": len(reviewed_raw),
            "legacy_reviewable_response_count": len(historical),
            "reviewable_response_count": len(reviewed_raw) + len(historical),
            "legacy_campaign_trial_count": historical_trial_count,
            "summary_only_cell_count": summary_only_count,
            "summary_only_cells_rescored": False,
            "semantic_verdict_counts": dict(
                sorted(semantic_verdicts.items())
            ),
            "current_mechanical_qualification_count": sum(
                row["current_metrics"]["mechanical_qualification_gate"]
                == 1.0
                for row in trials
            ),
            "current_nonzero_reward_count": sum(
                row["current_metrics"]["reward"] > 0.0
                for row in trials
            ),
            "empirically_covered_question_count": len(covered),
            "missing_empirical_question_ids": missing,
            "full_dataset_empirical_claim_eligible": not missing,
            "reference_calibration_count": len(references),
            "reference_mechanical_qualification_count": sum(
                row["current_metrics"]["mechanical_qualification_gate"]
                == 1.0
                for row in references
            ),
            "reference_semantic_pass_count": sum(
                row["semantic_verdict"] == "pass"
                for row in references
            ),
            "reward_delta_summary": _reward_delta_summary(trials),
        },
        "raw_response_identity_sha256": raw_digest,
        "reference_answer_collection_sha256": _sha256_file(
            collection_path
        ),
        "questions": question_rows,
        "raw_trials": trials,
        "legacy_historical_responses": historical,
        "reference_calibrations": references,
    }


def _metric(row: Mapping[str, Any] | None, name: str) -> float | None:
    if not isinstance(row, Mapping):
        return None
    metrics = row.get("current_metrics")
    value = metrics.get(name) if isinstance(metrics, Mapping) else None
    return float(value) if isinstance(value, (int, float)) else None


def _diagnostic(
    row: Mapping[str, Any] | None,
    name: str,
) -> Any:
    if not isinstance(row, Mapping):
        return None
    diagnostics = row.get("current_diagnostics")
    return (
        diagnostics.get(name)
        if isinstance(diagnostics, Mapping)
        else None
    )


def _number(value: Any, *, digits: int = 3) -> str:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return "—"
    return f"{float(value):.{digits}f}"


def _integer(value: Any) -> str:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return "—"
    return str(int(value))


def _verdict_counts(value: Mapping[str, Any]) -> str:
    return (
        f"P{int(value.get('pass', 0))}/"
        f"Pt{int(value.get('partial', 0))}/"
        f"F{int(value.get('fail', 0))}"
    )


def _latest_label(row: Mapping[str, Any] | None) -> str:
    if not isinstance(row, Mapping):
        return "—"
    outcome = row.get("trace", {}).get("outcome")
    verdict = row.get("semantic_verdict")
    if isinstance(verdict, str):
        return f"{outcome}; {verdict}"
    return str(outcome)


def _outcome_label(row: Mapping[str, Any] | None) -> str:
    if not isinstance(row, Mapping):
        return "—"
    trace = row.get("trace")
    return (
        str(trace.get("outcome"))
        if isinstance(trace, Mapping)
        else "—"
    )


def markdown(report: Mapping[str, Any]) -> str:
    """Render summary, per-question, per-trial, and calibration tables."""

    summary = report["summary"]
    delta = summary["reward_delta_summary"]
    lines = [
        "# GraphRAG 40-question current-metrics evaluation table",
        "",
        "## Interpretation boundary",
        "",
        (
            "This is an artifact-only recalculation of immutable Harbor traces; "
            "**no new model calls were made**. Every discovered raw trial was "
            "rescored with the current dataset policy and diagnostics schema 3.0. "
            "The scorer used each trial's native ledger and crosswalk so exact "
            "evidence identities remain valid across family-specific source "
            "representations."
        ),
        "",
        (
            "The reward is a mechanical contract-and-focus diagnostic, not a "
            "semantic score. Semantic verdicts remain the documented manual "
            "adjudications. The forty curated references are shown only as a "
            "calibration surface and are not counted as live trials."
        ),
        "",
        "## Recalculation summary",
        "",
        "| Measure | Value |",
        "|---|---:|",
        (
            "| Dataset questions | "
            f"{summary['dataset_question_count']} |"
        ),
        (
            "| Raw Harbor trials rescored | "
            f"{summary['raw_trials_rescored_with_current_metrics']} / "
            f"{summary['raw_harbor_trial_count']} |"
        ),
        (
            "| Reviewable raw responses | "
            f"{summary['reviewable_raw_response_count']} |"
        ),
        (
            "| Legacy reviewed responses without raw bodies | "
            f"{summary['legacy_reviewable_response_count']} |"
        ),
        (
            "| Total individually reviewable responses | "
            f"{summary['reviewable_response_count']} |"
        ),
        (
            "| Current mechanical qualification passes | "
            f"{summary['current_mechanical_qualification_count']} / "
            f"{summary['raw_harbor_trial_count']} |"
        ),
        (
            "| Questions with empirical response coverage | "
            f"{summary['empirically_covered_question_count']} / "
            f"{summary['dataset_question_count']} |"
        ),
        (
            "| Reference calibrations passing current contract | "
            f"{summary['reference_mechanical_qualification_count']} / "
            f"{summary['reference_calibration_count']} |"
        ),
        (
            "| Comparable rewards increased / decreased / unchanged | "
            f"{delta['increased_count']} / {delta['decreased_count']} / "
            f"{delta['unchanged_count']} |"
        ),
        (
            "| Mean original / current reward (comparable trials) | "
            f"{_number(delta['mean_original_reward'], digits=6)} / "
            f"{_number(delta['mean_current_reward'], digits=6)} |"
        ),
        "",
        (
            "Trace outcomes: "
            + ", ".join(
                f"`{name}`={count}"
                for name, count in summary["trace_outcome_counts"].items()
            )
            + "."
        ),
        "",
        (
            "Empirical full-dataset claim eligible: "
            f"`{str(summary['full_dataset_empirical_claim_eligible']).lower()}`. "
            "Missing empirical questions: "
            + ", ".join(
                f"`{question_id}`"
                for question_id in summary[
                    "missing_empirical_question_ids"
                ]
            )
            + "."
        ),
        "",
        "## Every question under the current metrics",
        "",
        (
            "| Q | Cohort | Trials | Reviewed raw+legacy | Semantic "
            "(P/Pt/F) | Qualified | Latest trial | Latest reviewed | "
            "Valid/focus docs | Gate | Utility | Reward | Empirical |"
        ),
        "|---|---|---:|---:|---|---:|---|---|---:|---:|---:|---:|---|",
    ]
    for row in report["questions"]:
        latest_trial = row["latest_trial"]
        latest_reviewed = row["latest_reviewed_response"]
        valid = _diagnostic(
            latest_reviewed,
            "valid_independent_document_count",
        )
        focus = _diagnostic(latest_reviewed, "covered_qrel_count")
        reviewed = (
            f"{row['reviewable_raw_response_count']}+"
            f"{row['legacy_reviewable_response_count']}"
        )
        valid_focus = (
            "—"
            if valid is None and focus is None
            else f"{_integer(valid)}/{_integer(focus)}"
        )
        lines.append(
            "| "
            + " | ".join(
                [
                    str(row["question_id"]),
                    str(row["cohort"]),
                    str(row["raw_trial_count"]),
                    reviewed,
                    _verdict_counts(row["semantic_verdict_counts"]),
                    (
                        f"{row['current_mechanical_qualification_count']}/"
                        f"{row['raw_trial_count']}"
                    ),
                    _outcome_label(latest_trial),
                    _latest_label(latest_reviewed),
                    valid_focus,
                    _integer(
                        _metric(
                            latest_reviewed,
                            "mechanical_qualification_gate",
                        )
                    ),
                    _number(
                        _metric(latest_reviewed, "mechanical_utility")
                    ),
                    _number(_metric(latest_reviewed, "reward")),
                    str(row["empirical_coverage"]),
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## Every raw Harbor trial rescored",
            "",
            (
                "| Trial | Q | Outcome | Reviewed | Contract | Valid/focus docs "
                "| Gate | Utility | Original reward | Current reward | Delta | "
                "Semantic |"
            ),
            "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    for row in report["raw_trials"]:
        valid = _diagnostic(row, "valid_independent_document_count")
        focus = _diagnostic(row, "covered_qrel_count")
        original = row["original_metrics"].get("reward")
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{row['response_id']}`",
                    str(row["question_id"]),
                    str(row["trace"]["outcome"]),
                    "1" if row["reviewable_response"] else "0",
                    _integer(_metric(row, "response_contract")),
                    f"{_integer(valid)}/{_integer(focus)}",
                    _integer(
                        _metric(row, "mechanical_qualification_gate")
                    ),
                    _number(_metric(row, "mechanical_utility")),
                    _number(original),
                    _number(_metric(row, "reward")),
                    _number(row["reward_delta"]),
                    str(row.get("semantic_verdict") or "not-reviewed"),
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## Legacy reviewed responses without a raw body",
            "",
            (
                "These rows retain their historical mechanical observations and "
                "manual verdicts, but they cannot be recalculated under schema "
                "3.0 because the original response bodies are absent."
            ),
            "",
            "| Response | Q | Contract | Evidence | Focus docs | Historical reward | Semantic |",
            "|---|---|---:|---:|---:|---:|---|",
        ]
    )
    for row in report["legacy_historical_responses"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{row['response_id']}`",
                    str(row["question_id"]),
                    "1" if row["response_contract"] else "0",
                    _integer(row.get("evidence_count")),
                    _integer(row.get("covered_focus_document_count")),
                    _number(row.get("reward")),
                    str(row["semantic_verdict"]),
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## Curated reference calibration",
            "",
            (
                "| Q | Evidence | Valid/focus docs | Gate | Utility | Reward | "
                "Semantic targets | Hard anchors |"
            ),
            "|---|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in report["reference_calibrations"]:
        valid = _diagnostic(row, "valid_independent_document_count")
        focus = _diagnostic(row, "covered_qrel_count")
        lines.append(
            "| "
            + " | ".join(
                [
                    str(row["question_id"]),
                    _integer(row.get("evidence_count")),
                    f"{_integer(valid)}/{_integer(focus)}",
                    _integer(
                        _metric(row, "mechanical_qualification_gate")
                    ),
                    _number(_metric(row, "mechanical_utility")),
                    _number(_metric(row, "reward")),
                    _integer(row.get("semantic_target_count")),
                    _integer(row.get("hard_anchor_count")),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            (
                "All reference rows are curated evaluator material. Their pass "
                "status validates the metric implementation and expected-answer "
                "surface; it does not improve empirical model coverage."
            ),
            "",
        ]
    )
    return "\n".join(lines)


def _write(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        value.replace("\r\n", "\n")
        + ("" if value.endswith("\n") else "\n"),
        encoding="utf-8",
        newline="\n",
    )


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse immutable evidence and report destinations."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--results",
        type=Path,
        default=HERE / "results",
    )
    parser.add_argument(
        "--current-tasks",
        type=Path,
        default=DEFAULT_TASKS,
    )
    parser.add_argument(
        "--raw-adjudications",
        type=Path,
        default=(
            HERE
            / "reports/"
            "20260724-graphrag-papers-40-raw-semantic-adjudications.json"
        ),
    )
    parser.add_argument(
        "--historical-campaign",
        type=Path,
        default=(
            HERE
            / "reports/"
            "20260717-papers-consult-gpt53-spark-01-audit-v2.json"
        ),
    )
    parser.add_argument(
        "--historical-manual-review",
        type=Path,
        default=(
            HERE
            / "reports/"
            "20260717-papers-consult-gpt53-spark-01-manual-review.md"
        ),
    )
    parser.add_argument(
        "--summary-only-cells",
        type=Path,
        default=(
            REPO
            / "evaluations/graphrag-cross-paper/analysis/"
            "full-baseline-cells.json"
        ),
    )
    parser.add_argument("--report-date", default="2026-07-24")
    parser.add_argument("--output-json", type=Path, default=DEFAULT_JSON)
    parser.add_argument(
        "--output-markdown",
        type=Path,
        default=DEFAULT_MARKDOWN,
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    """Recalculate current metrics and write deterministic report artifacts."""

    args = parse_args(argv)
    try:
        datetime.fromisoformat(args.report_date)
        report = build_report(args)
    except (
        RecalculationError,
        audit.AuditError,
        data.DatasetError,
        OSError,
        UnicodeError,
        json.JSONDecodeError,
        ValueError,
    ) as exc:
        raise SystemExit(str(exc)) from exc
    rendered = json.dumps(
        report,
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
        allow_nan=False,
    )
    _write(args.output_json, rendered)
    _write(args.output_markdown, markdown(report))
    print(
        json.dumps(
            {
                "status": "pass",
                "raw_trials_rescored": report["summary"][
                    "raw_trials_rescored_with_current_metrics"
                ],
                "current_mechanical_qualification_count": report[
                    "summary"
                ]["current_mechanical_qualification_count"],
                "empirically_covered_question_count": report["summary"][
                    "empirically_covered_question_count"
                ],
                "reference_calibration_count": report["summary"][
                    "reference_calibration_count"
                ],
                "output_json": str(args.output_json),
                "output_markdown": str(args.output_markdown),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
