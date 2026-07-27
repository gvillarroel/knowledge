#!/usr/bin/env python3
"""Audit a complete, hash-bound Tika/MALLET Harbor candidate campaign."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence


SCHEMA_VERSION = "semantic-okf-tika-mallet-harbor-candidate-audit/1.0"
DATASET_ID = "graphrag-papers-40"
FAMILY_ID = "tika-mallet"
MODE = "consult-only"
EXPECTED_MODEL = "openai-codex/gpt-5.3-codex-spark"
EXPECTED_PI_VERSION = "0.73.1"
HERE = Path(__file__).resolve().parent
EVALUATION = HERE.parent
REPO = EVALUATION.parents[1]
DATASET_ROOT = REPO / "evaluations" / "semantic-okf-datasets"
GRADER_ROOT = REPO / "evaluations" / "semantic-okf-harbor" / "grader"
for import_root in (DATASET_ROOT, GRADER_ROOT):
    if str(import_root) not in sys.path:
        sys.path.insert(0, str(import_root))

import candidate_family as candidates  # noqa: E402
import dataset_tool as data  # noqa: E402
import run_harbor as runner  # noqa: E402
import score as grader  # noqa: E402
import summarize_consult_campaign as common  # noqa: E402


class AuditError(ValueError):
    """Describe an incomplete, drifting, or non-observable candidate campaign."""


def load_json(path: Path) -> dict[str, Any]:
    """Load one JSON object with a path-specific failure."""

    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise AuditError(f"cannot read JSON object: {path}") from exc
    if not isinstance(value, dict):
        raise AuditError(f"expected one JSON object: {path}")
    return value


def sha256_file(path: Path) -> str:
    """Hash one regular file."""

    if not path.is_file() or path.is_symlink():
        raise AuditError(f"required regular file is absent: {path}")
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def repo_path(path: Path, label: str) -> Path:
    """Resolve a repository-local path without accepting symlinks."""

    resolved = path.resolve()
    try:
        resolved.relative_to(REPO.resolve())
    except ValueError as exc:
        raise AuditError(f"{label} must be inside the repository: {path}") from exc
    if resolved.is_symlink() or any(
        parent.is_symlink() for parent in resolved.parents if parent != REPO.parent
    ):
        raise AuditError(f"{label} cannot traverse a symlink: {path}")
    return resolved


def relative(path: Path) -> str:
    """Return one repository-relative POSIX path."""

    return path.resolve().relative_to(REPO.resolve()).as_posix()


def expected_cells(tasks: Path) -> tuple[dict[str, str], dict[str, Any]]:
    """Bind all forty generated task identities to their declared cohorts."""

    manifest = load_json(tasks / "manifest.json")
    expected_manifest = {
        "dataset_id": DATASET_ID,
        "family": FAMILY_ID,
        "mode": MODE,
        "question_count": 40,
    }
    if any(manifest.get(key) != value for key, value in expected_manifest.items()):
        raise AuditError("generated task manifest identity drift")
    dataset = data.load_dataset(DATASET_ID)
    cohorts = data.dataset_cohorts(dataset)
    cells = {
        question_id: cohort
        for cohort in dataset["partition_cohorts"]
        for question_id in cohorts[cohort]
    }
    if len(cells) != 40:
        raise AuditError(f"expected 40 unique questions, found {len(cells)}")
    for question_id, cohort in cells.items():
        task = tasks / cohort / question_id
        if not task.is_dir() or task.is_symlink():
            raise AuditError(f"generated task is absent: {cohort}/{question_id}")
    return cells, manifest


def matrix_status(
    expected: Mapping[str, str], rows: Sequence[Mapping[str, Any]]
) -> tuple[bool, list[str]]:
    """Require every expected question exactly once and scorer-observable."""

    reasons: list[str] = []
    observed: dict[str, int] = {}
    for row in rows:
        identifier = str(row.get("question_id"))
        observed[identifier] = observed.get(identifier, 0) + 1
        if expected.get(identifier) != row.get("cohort"):
            reasons.append(f"cohort-drift:{identifier}")
        if not row.get("evaluable"):
            reasons.append(f"not-evaluable:{identifier}")
    for identifier in expected:
        count = observed.get(identifier, 0)
        if count == 0:
            reasons.append(f"missing:{identifier}")
        elif count > 1:
            reasons.append(f"duplicate:{identifier}")
    for identifier in observed:
        if identifier not in expected:
            reasons.append(f"unexpected:{identifier}")
    return not reasons, sorted(set(reasons))


def rescore(
    task: Path, trace: Path
) -> tuple[dict[str, float], dict[str, Any]]:
    """Apply the current checked grader to one immutable retained trace."""

    tests = task / "tests"
    ground_truth = tests / "hard-ground-truth.json"
    try:
        return grader.score(
            argparse.Namespace(
                pi_log=trace,
                question=tests / "question.json",
                ledger=tests / "records.jsonl",
                crosswalk=tests / "source-combination.json",
                ground_truth=ground_truth if ground_truth.is_file() else None,
                authority_root=tests / "authority",
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
        raise AuditError(f"current grader failed for {task.parent.name}/{task.name}: {exc}") from exc


def trial_row(
    *,
    run: Path,
    trial_result: Path,
    question_id: str,
    cohort: str,
    task: Path,
) -> dict[str, Any]:
    """Validate and normalize one completed Harbor trial."""

    result = load_json(trial_result)
    expected_task_name = (
        f"knowledge/{DATASET_ID}__{MODE}__{FAMILY_ID}__{question_id}"
    )
    if (
        result.get("task_name") != expected_task_name
        or result.get("source") != cohort
        or result.get("exception_info") is not None
    ):
        raise AuditError(f"{run.name}/{question_id}: trial identity or exception drift")
    agent_info = result.get("agent_info")
    model_info = agent_info.get("model_info") if isinstance(agent_info, Mapping) else None
    if (
        not isinstance(agent_info, Mapping)
        or agent_info.get("name") != "pi"
        or agent_info.get("version") != EXPECTED_PI_VERSION
        or not isinstance(model_info, Mapping)
        or model_info.get("name") != "gpt-5.3-codex-spark"
        or model_info.get("provider") != "openai-codex"
    ):
        raise AuditError(f"{run.name}/{question_id}: agent identity drift")

    trial = trial_result.parent
    reward_path = trial / "verifier" / "reward.json"
    diagnostics_path = trial / "verifier" / "diagnostics.json"
    trace = trial / "artifacts" / "pi.jsonl"
    if not trace.is_file():
        trace = trial / "agent" / "pi.txt"
    rewards = load_json(reward_path)
    diagnostics = load_json(diagnostics_path)
    verifier = result.get("verifier_result")
    if not isinstance(verifier, Mapping) or verifier.get("rewards") != rewards:
        raise AuditError(f"{run.name}/{question_id}: verifier reward artifact drift")
    ground_truth = (task / "tests" / "hard-ground-truth.json").is_file()
    observable, observability_errors = common.current_scorer_observability(
        rewards,
        diagnostics,
        has_ground_truth=ground_truth,
    )
    if (
        diagnostics.get("schema_version")
        != "semantic-okf-harbor-redacted-diagnostics/2.0"
        or diagnostics.get("question_id") != question_id
    ):
        observability_errors.append("diagnostics-identity")
        observable = False
    trace_status = runner.classify_pi_trace(trace)
    if trace_status.get("outcome") != "answer-emitted":
        observable = False
        observability_errors.append(f"trace:{trace_status.get('outcome')}")

    rescored_rewards, rescored_diagnostics = rescore(task, trace)
    if rescored_rewards != rewards or rescored_diagnostics != diagnostics:
        raise AuditError(f"{run.name}/{question_id}: current grader replay drift")

    agent = result.get("agent_result")
    if not isinstance(agent, Mapping):
        agent = {}
    started = common.parse_time(result.get("started_at"))
    finished = common.parse_time(result.get("finished_at"))
    duration = (
        (finished - started).total_seconds()
        if started is not None and finished is not None
        else None
    )
    return {
        "question_id": question_id,
        "cohort": cohort,
        "run": relative(run),
        "trial": trial.name,
        "task_checksum": result.get("task_checksum"),
        "evaluable": bool(observable),
        "complete_response_observed": trace_status.get("outcome") == "answer-emitted",
        "agent_outcome": trace_status.get("outcome"),
        "status": diagnostics.get("status"),
        "observability_errors": sorted(set(observability_errors)),
        "duration_seconds": duration,
        "tokens": {
            "input": int(agent.get("n_input_tokens") or 0),
            "cache": int(agent.get("n_cache_tokens") or 0),
            "output": int(agent.get("n_output_tokens") or 0),
        },
        "metrics": common.normalized_metrics(rewards),
        "diagnostics": {
            "evidence_count": diagnostics.get("evidence_count"),
            "covered_qrel_count": diagnostics.get("covered_qrel_count"),
            "minimum_document_count": diagnostics.get("minimum_document_count"),
            "semantic_correctness": diagnostics.get("semantic_correctness"),
        },
        "artifacts": {
            "trial_result_sha256": sha256_file(trial_result),
            "reward_sha256": sha256_file(reward_path),
            "diagnostics_sha256": sha256_file(diagnostics_path),
            "trace_sha256": sha256_file(trace),
        },
    }


def audit_run(
    *,
    run: Path,
    expected: Mapping[str, str],
    tasks: Path,
    task_manifest_sha256: str,
    candidate_binding: Mapping[str, Any],
    skill_sha256: str,
    bundle_sha256: str,
    records_sha256: str,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Validate one append-only Harbor job and return its trial rows."""

    receipt_path = run / "run-receipt.json"
    config_path = run / "job-config.redacted.json"
    result_path = run / "result.json"
    receipt = load_json(receipt_path)
    config = load_json(config_path)
    result = load_json(result_path)
    expected_receipt = {
        "schema_version": "semantic-okf-evaluation-harbor-run/2.0",
        "dataset_id": DATASET_ID,
        "family": FAMILY_ID,
        "mode": MODE,
        "model": EXPECTED_MODEL,
        "pi_version": EXPECTED_PI_VERSION,
        "public_mount_target": "/knowledge",
        "prebuilt_knowledge_mounted": True,
        "raw_sources_mounted": False,
        "resource_kind": "processed-knowledge",
        "resource_tree_sha256": bundle_sha256,
        "records_sha256": records_sha256,
        "generated_tasks_manifest_sha256": task_manifest_sha256,
        "candidate_family": dict(candidate_binding),
        "run_status": "completed",
        "harbor_exit_code": 0,
        "provider_failure_detected": False,
    }
    if any(receipt.get(key) != value for key, value in expected_receipt.items()):
        raise AuditError(f"{run.name}: run receipt identity or completion drift")
    skills = receipt.get("installed_skills")
    if (
        not isinstance(skills, list)
        or len(skills) != 1
        or skills[0].get("tree_sha256") != skill_sha256
    ):
        raise AuditError(f"{run.name}: installed skill identity drift")
    task_ids = receipt.get("task_ids")
    cohort = receipt.get("cohort")
    if (
        not isinstance(task_ids, list)
        or not task_ids
        or len(task_ids) != len(set(task_ids))
        or any(expected.get(identifier) != cohort for identifier in task_ids)
    ):
        raise AuditError(f"{run.name}: receipt task set or cohort drift")
    if receipt.get("terminal_outcomes") != {"answer-emitted": len(task_ids)}:
        raise AuditError(f"{run.name}: terminal outcomes are not all answer-emitted")
    if receipt.get("job_config_redacted_sha256") != sha256_file(config_path):
        raise AuditError(f"{run.name}: redacted job config hash drift")

    concurrency = config.get("n_concurrent_trials")
    agents = config.get("agents")
    if (
        not isinstance(concurrency, int)
        or isinstance(concurrency, bool)
        or not 1 <= concurrency <= 4
        or not isinstance(agents, list)
        or len(agents) != 1
        or agents[0].get("n_concurrent") != concurrency
        or config.get("n_attempts") != 1
        or config.get("retry") != {"max_retries": 0}
    ):
        raise AuditError(f"{run.name}: bounded execution contract drift")
    if receipt.get("concurrency") not in (None, concurrency):
        raise AuditError(f"{run.name}: receipt concurrency drift")
    stats = result.get("stats")
    if (
        result.get("n_total_trials") != len(task_ids)
        or result.get("finished_at") is None
        or not isinstance(stats, Mapping)
        or stats.get("n_completed_trials") != len(task_ids)
        or stats.get("n_errored_trials") != 0
        or stats.get("n_running_trials") != 0
        or stats.get("n_pending_trials") != 0
        or stats.get("n_cancelled_trials") != 0
        or stats.get("n_retries") != 0
    ):
        raise AuditError(f"{run.name}: Harbor job did not complete exactly once")

    trial_results = sorted(run.glob("q*__*/result.json"))
    if len(trial_results) != len(task_ids):
        raise AuditError(f"{run.name}: trial result count does not match receipt")
    rows: list[dict[str, Any]] = []
    observed: set[str] = set()
    for trial_result in trial_results:
        result_value = load_json(trial_result)
        task_name = str(result_value.get("task_name", ""))
        question_id = task_name.rsplit("__", 1)[-1]
        if question_id in observed or question_id not in task_ids:
            raise AuditError(f"{run.name}: duplicate or unexpected trial {question_id}")
        observed.add(question_id)
        rows.append(
            trial_row(
                run=run,
                trial_result=trial_result,
                question_id=question_id,
                cohort=str(cohort),
                task=tasks / str(cohort) / question_id,
            )
        )
    if observed != set(task_ids):
        raise AuditError(f"{run.name}: retained trials do not match the receipt")
    return (
        {
            "path": relative(run),
            "cohort": cohort,
            "task_ids": task_ids,
            "concurrency": concurrency,
            "result_sha256": sha256_file(result_path),
            "receipt_sha256": sha256_file(receipt_path),
            "config_sha256": sha256_file(config_path),
        },
        rows,
    )


def metric_mean(aggregate: Mapping[str, Any], name: str) -> float:
    """Read one complete aggregate mean."""

    value = aggregate["metrics"][name]["mean"]
    if not isinstance(value, (int, float)) or not math.isfinite(float(value)):
        raise AuditError(f"aggregate metric is absent: {name}")
    return float(value)


def markdown(report: Mapping[str, Any]) -> str:
    """Render a compact human-readable audit."""

    lines = [
        "# Tika/MALLET Harbor Candidate Audit",
        "",
        f"- Status: `{report['status']}`",
        f"- Ranking eligible: `{str(report['ranking_eligible']).lower()}`",
        f"- Complete/evaluable trials: `{report['evaluable_trials']}/{report['expected_trials']}`",
        f"- Dataset: `{report['dataset_id']}`",
        f"- Candidate: `{report['candidate_id']}`",
        "",
        "| Cohort | Trials | Reward | Qualification gate | Evidence recall | Evidence precision | MRR | nDCG |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for cohort in (*report["cohort_order"], "all"):
        row = report["cohorts"][cohort] if cohort != "all" else report["overall"]
        lines.append(
            "| "
            + " | ".join(
                [
                    cohort,
                    str(row["evaluable_trials"]),
                    f"{metric_mean(row, 'reward'):.4f}",
                    f"{metric_mean(row, 'mechanical_qualification_gate'):.4f}",
                    f"{metric_mean(row, 'evidence_recall'):.4f}",
                    f"{metric_mean(row, 'evidence_precision'):.4f}",
                    f"{metric_mean(row, 'mrr'):.4f}",
                    f"{metric_mean(row, 'ndcg'):.4f}",
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "Every retained answer was replayed through the current checked grader. "
            "Ranking eligibility means that all forty declared cells are present exactly "
            "once, scorer-observable, provider-clean, evaluator-clean, and bound to the "
            "same tasks, bundle, candidate contract, skill tree, model, and Pi version.",
            "",
            "The verifier's `semantic_correctness` field remains "
            "`manual-review-required`; these mechanical scores do not substitute for a "
            "blinded prose-level semantic review.",
            "",
        ]
    )
    return "\n".join(lines)


def write_json(path: Path, value: Mapping[str, Any]) -> None:
    """Write stable UTF-8 JSON without replacing an existing report."""

    if path.exists():
        raise AuditError(f"refusing to overwrite report: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def write_markdown(path: Path, value: str) -> None:
    """Write stable Markdown without replacing an existing report."""

    if path.exists():
        raise AuditError(f"refusing to overwrite report: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8", newline="\n")


def audit(
    *,
    runs: Sequence[Path],
    tasks: Path,
    candidate_spec: Path,
    skill: Path,
    bundle: Path,
) -> dict[str, Any]:
    """Audit one complete candidate matrix and return its closed report."""

    tasks = repo_path(tasks, "generated task root")
    skill = repo_path(skill, "candidate consult skill")
    bundle = repo_path(bundle, "candidate bundle")
    candidate_spec = repo_path(candidate_spec, "candidate specification")
    if not tasks.is_dir() or not skill.is_dir() or not bundle.is_dir():
        raise AuditError("tasks, skill, and bundle must be directories")
    expected, task_manifest = expected_cells(tasks)
    _family, candidate_binding = candidates.resolve(
        DATASET_ID, FAMILY_ID, MODE, candidate_spec
    )
    if candidate_binding is None or task_manifest.get("candidate_family") != candidate_binding:
        raise AuditError("candidate binding drift between specification and tasks")
    records = bundle / "semantic" / "records.jsonl"
    task_manifest_sha256 = sha256_file(tasks / "manifest.json")
    skill_sha256 = data.tree_digest(skill)
    bundle_sha256 = data.tree_digest(bundle)
    records_sha256 = sha256_file(records)
    if (
        task_manifest.get("reference_bundle_tree_sha256") != bundle_sha256
        or task_manifest.get("reference_records_sha256") != records_sha256
    ):
        raise AuditError("generated tasks are not bound to the supplied bundle")

    run_rows: list[dict[str, Any]] = []
    trials: list[dict[str, Any]] = []
    for run_path in runs:
        run = repo_path(run_path, "Harbor result root")
        if not run.is_dir():
            raise AuditError(f"Harbor result root is absent: {run}")
        run_row, trial_rows = audit_run(
            run=run,
            expected=expected,
            tasks=tasks,
            task_manifest_sha256=task_manifest_sha256,
            candidate_binding=candidate_binding,
            skill_sha256=skill_sha256,
            bundle_sha256=bundle_sha256,
            records_sha256=records_sha256,
        )
        run_rows.append(run_row)
        trials.extend(trial_rows)

    complete, invalid_reasons = matrix_status(expected, trials)
    if not complete:
        raise AuditError("campaign is not ranking-eligible: " + ", ".join(invalid_reasons))
    cohort_order = list(data.load_dataset(DATASET_ID)["partition_cohorts"])
    by_cohort = {
        cohort: common.aggregate(
            [row for row in trials if row["cohort"] == cohort],
            sum(value == cohort for value in expected.values()),
        )
        for cohort in cohort_order
    }
    overall = common.aggregate(trials, len(expected))
    report: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "status": "pass",
        "dataset_id": DATASET_ID,
        "candidate_id": FAMILY_ID,
        "mode": MODE,
        "model": EXPECTED_MODEL,
        "pi_version": EXPECTED_PI_VERSION,
        "expected_trials": len(expected),
        "result_trials": len(trials),
        "evaluable_trials": sum(bool(row["evaluable"]) for row in trials),
        "structurally_complete": True,
        "evaluation_complete": True,
        "ranking_eligible": True,
        "invalid_reasons": [],
        "cohort_order": cohort_order,
        "identities": {
            "candidate_binding": candidate_binding,
            "candidate_specification_sha256": sha256_file(candidate_spec),
            "tasks_path": relative(tasks),
            "tasks_tree_sha256": data.tree_digest(tasks),
            "task_manifest_sha256": task_manifest_sha256,
            "skill_path": relative(skill),
            "skill_tree_sha256": skill_sha256,
            "bundle_path": relative(bundle),
            "bundle_tree_sha256": bundle_sha256,
            "records_sha256": records_sha256,
        },
        "runs": sorted(run_rows, key=lambda row: (str(row["cohort"]), str(row["path"]))),
        "cohorts": by_cohort,
        "overall": overall,
        "trials": sorted(trials, key=lambda row: row["question_id"]),
        "interpretation": {
            "mechanical_metrics_only": True,
            "semantic_correctness": "manual-review-required",
            "ranking_scope": (
                "Rankable as one complete graphrag-papers-40 candidate row; "
                "not a replacement for an unrun same-cycle eight-family comparison."
            ),
        },
    }
    return report


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse the strict candidate-audit command line."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", action="append", type=Path, required=True)
    parser.add_argument("--tasks", type=Path, required=True)
    parser.add_argument("--candidate-spec", type=Path, required=True)
    parser.add_argument("--skill", type=Path, required=True)
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-markdown", type=Path, required=True)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    """Audit, render, and publish one immutable candidate report."""

    args = parse_args(argv)
    try:
        report = audit(
            runs=args.run,
            tasks=args.tasks,
            candidate_spec=args.candidate_spec,
            skill=args.skill,
            bundle=args.bundle,
        )
        write_json(args.output_json, report)
        write_markdown(args.output_markdown, markdown(report))
        print(
            json.dumps(
                {
                    "status": report["status"],
                    "ranking_eligible": report["ranking_eligible"],
                    "evaluable_trials": report["evaluable_trials"],
                    "output_json": str(args.output_json),
                    "output_markdown": str(args.output_markdown),
                },
                sort_keys=True,
            )
        )
        return 0
    except (AuditError, data.DatasetError, candidates.CandidateFamilyError) as exc:
        raise SystemExit(str(exc)) from exc


if __name__ == "__main__":
    raise SystemExit(main())
