#!/usr/bin/env python3
"""Audit and summarize one consult-only Semantic OKF Harbor campaign."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Any, Mapping, Sequence

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
GRADER = REPO / "evaluations/semantic-okf-harbor/grader"
for import_root in (HERE, GRADER):
    if str(import_root) not in sys.path:
        sys.path.insert(0, str(import_root))

import dataset_tool as data  # noqa: E402
import campaign_binding as frozen  # noqa: E402
import run_consult_campaign as campaign_runner  # noqa: E402
import run_harbor as harbor_runner  # noqa: E402
import score as grader  # noqa: E402
from trace_status import classify_pi_trace  # noqa: E402

EXPECTED_MODEL = "openai-codex/gpt-5.3-codex-spark"
EXPECTED_PI_VERSION = "0.73.1"
METRICS = (
    "reward",
    "mechanical_utility",
    "mechanical_qualification_gate",
    "evidence_contract_gate",
    "minimum_document_gate",
    "minimum_document_coverage",
    "response_contract",
    "non_null_answer",
    "reference_validity",
    "evidence_validity",
    "all_evidence_valid",
    "complete_qrel_coverage",
    "evidence_precision",
    "evidence_recall",
    "mrr",
    "ndcg",
    "required_document_coverage",
    "authoritative_evidence_anchor_coverage",
    "answer_claim_anchor_coverage",
    "important_negative_anchor_coverage",
)
LEGACY_METRICS = {
    "evidence_contract_gate": "quality_gate",
    "authoritative_evidence_anchor_coverage": "authoritative_evidence_completeness",
    "answer_claim_anchor_coverage": "atomic_claim_evidence_completeness",
    "important_negative_anchor_coverage": "important_negative_evidence_completeness",
}
PROVIDER_OUTCOMES = {
    "provider-quota",
    "provider-rate-limit",
    "provider-context-limit",
    "provider-error",
}
CURRENT_SCORER_STATUSES = {"scored-response", "agent-invalid-response"}
HEX64 = frozenset("0123456789abcdef")


class SummaryError(ValueError):
    """Raised when campaign artifacts are incomplete, drifted, or not comparable."""


def load_json(path: Path) -> dict[str, Any]:
    """Load one JSON object with a path-specific diagnostic."""

    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise SummaryError(f"cannot read JSON object: {path}") from exc
    if not isinstance(value, dict):
        raise SummaryError(f"expected a JSON object: {path}")
    return value


def parse_time(value: object) -> datetime | None:
    """Parse a Harbor ISO timestamp when present."""

    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _validate_v3_execution_receipt(
    run: Path, receipt: Mapping[str, Any]
) -> bool:
    """Validate live completion metadata and return whether Harbor finished cleanly."""

    exit_code = receipt.get("harbor_exit_code")
    terminal_outcomes = receipt.get("terminal_outcomes")
    if (
        not isinstance(exit_code, int)
        or isinstance(exit_code, bool)
        or not isinstance(terminal_outcomes, Mapping)
        or any(
            not isinstance(outcome, str)
            or not outcome
            or not isinstance(count, int)
            or isinstance(count, bool)
            or count <= 0
            for outcome, count in terminal_outcomes.items()
        )
        or sum(terminal_outcomes.values()) > 1
    ):
        raise SummaryError(f"{run.name}: live receipt has invalid completion counters")
    provider_failure = any(
        terminal_outcomes.get(outcome, 0) for outcome in PROVIDER_OUTCOMES
    )
    expected_status = (
        "provider-failure"
        if provider_failure
        else "completed"
        if exit_code == 0
        else "runner-failure"
    )
    if (
        receipt.get("provider_failure_detected") is not provider_failure
        or receipt.get("run_status") != expected_status
    ):
        raise SummaryError(f"{run.name}: live receipt completion status is inconsistent")
    started = parse_time(receipt.get("run_started_at"))
    finished = parse_time(receipt.get("run_finished_at"))
    if (
        started is None
        or finished is None
        or started.tzinfo is None
        or finished.tzinfo is None
        or started.utcoffset() is None
        or finished.utcoffset() is None
        or finished < started
    ):
        raise SummaryError(f"{run.name}: live receipt timestamps are invalid")
    return expected_status == "completed"


def _validate_v3_outcome_exit(
    run: Path,
    outcome: Mapping[str, Any],
    receipt: Mapping[str, Any],
) -> None:
    """Require the campaign runner exit code to agree with the live receipt."""

    harbor_exit_code = receipt["harbor_exit_code"]
    expected = harbor_runner.completion_status(
        harbor_exit_code, receipt["terminal_outcomes"]
    )["effective_exit_code"]
    actual = outcome.get("run_exit_code")
    if (
        not isinstance(actual, int)
        or isinstance(actual, bool)
        or actual != expected
    ):
        raise SummaryError(f"{run.name}: campaign outcome exit code differs from its receipt")


def _validate_scheduled_trace_outcome(
    run: Path,
    outcome: Mapping[str, Any],
) -> None:
    """Bind one scheduled outcome's semantic fields to its exact Pi trace layout."""

    question_id = outcome.get("question_id")
    if not isinstance(question_id, str) or not question_id:
        raise SummaryError(f"{run.name}: scheduled outcome has no question identity")
    all_traces = sorted(run.glob("**/artifacts/pi.jsonl"))
    traces = sorted(run.glob(f"{question_id}__*/artifacts/pi.jsonl"))
    if all_traces != traces:
        raise SummaryError(f"{run.name}: Pi trace has an off-contract trial path")
    if any(
        trace.is_symlink()
        or trace.parent.is_symlink()
        or trace.parent.parent.is_symlink()
        for trace in traces
    ):
        raise SummaryError(f"{run.name}: Pi trace path contains a symlink")
    if len(traces) > 1:
        raise SummaryError(f"{run.name}: scheduled shard has multiple Pi traces")
    if not traces:
        if "parsed_events" in outcome or "stop_reason" in outcome:
            raise SummaryError(
                f"{run.name}: missing-trace outcome has impossible trace metadata"
            )
        underlying_fields = {
            key for key in outcome if key.startswith("underlying_trace_")
        }
        if underlying_fields:
            expected_underlying = {
                "underlying_trace_error_code",
                "underlying_trace_failure_domain",
                "underlying_trace_outcome",
            }
            expected = {
                "binding_error_type": outcome.get("binding_error_type"),
                "error_code": "input_binding_drift",
                "failure_domain": "runner",
                "outcome": "runner-error",
                "trace_path": None,
                "underlying_trace_error_code": "missing_pi_trace",
                "underlying_trace_failure_domain": "runner",
                "underlying_trace_outcome": "runner-error",
            }
            if (
                underlying_fields != expected_underlying
                or not isinstance(outcome.get("binding_error_type"), str)
                or not outcome.get("binding_error_type")
            ):
                raise SummaryError(
                    f"{run.name}: missing-trace wrapper has an invalid shape"
                )
        else:
            if "binding_error_type" in outcome:
                raise SummaryError(
                    f"{run.name}: direct missing-trace outcome has wrapper metadata"
                )
            expected = {
                "error_code": "missing_pi_trace",
                "failure_domain": "runner",
                "outcome": "runner-error",
                "trace_path": None,
            }
        if any(outcome.get(key) != value for key, value in expected.items()):
            raise SummaryError(
                f"{run.name}: scheduled outcome differs from its missing-trace state"
            )
        return

    classified = classify_pi_trace(traces[0])
    trace_path = traces[0].relative_to(run).as_posix()
    underlying_fields = {
        key for key in outcome if key.startswith("underlying_trace_")
    }
    if underlying_fields:
        expected_underlying_fields = {
            "underlying_trace_error_code",
            "underlying_trace_failure_domain",
            "underlying_trace_outcome",
        }
        if classified.get("provider_reset") is not None:
            expected_underlying_fields.add("underlying_trace_provider_reset")
        expected = {
            "outcome": "runner-error",
            "failure_domain": "runner",
            "underlying_trace_outcome": classified.get("outcome"),
            "underlying_trace_failure_domain": classified.get("failure_domain"),
            "underlying_trace_error_code": classified.get("error_code"),
            "underlying_trace_provider_reset": classified.get("provider_reset"),
            "parsed_events": classified.get("parsed_events"),
            "stop_reason": classified.get("stop_reason"),
            "trace_path": trace_path,
        }
        wrapper_error = outcome.get("error_code")
        binding_error_type = outcome.get("binding_error_type")
        run_exit_code = outcome.get("run_exit_code")
        valid_wrapper = (
            wrapper_error == "input_binding_drift"
            and isinstance(binding_error_type, str)
            and bool(binding_error_type)
        ) or (
            wrapper_error == "nonzero_runner_exit"
            and classified.get("outcome") not in PROVIDER_OUTCOMES
            and "binding_error_type" not in outcome
            and isinstance(run_exit_code, int)
            and not isinstance(run_exit_code, bool)
            and run_exit_code != 0
        )
        if not valid_wrapper or underlying_fields != expected_underlying_fields:
            raise SummaryError(f"{run.name}: scheduled trace wrapper has an invalid shape")
    else:
        if "binding_error_type" in outcome:
            raise SummaryError(f"{run.name}: direct trace outcome has wrapper metadata")
        if (
            classified.get("outcome") not in PROVIDER_OUTCOMES
            and outcome.get("run_exit_code") not in (None, 0)
        ):
            raise SummaryError(
                f"{run.name}: non-provider trace omitted its nonzero runner wrapper"
            )
        expected = {
            "outcome": classified.get("outcome"),
            "failure_domain": classified.get("failure_domain"),
            "error_code": classified.get("error_code"),
            "provider_reset": classified.get("provider_reset"),
            "parsed_events": classified.get("parsed_events"),
            "stop_reason": classified.get("stop_reason"),
            "trace_path": trace_path,
        }
    if any(outcome.get(key) != value for key, value in expected.items()):
        raise SummaryError(f"{run.name}: scheduled outcome differs from its terminal trace")


def _validate_v3_scheduled_completion(
    run: Path,
    outcome: Mapping[str, Any] | None,
    receipt: Mapping[str, Any],
) -> None:
    """Bind receipt completion to traces and outcome even when no result exists."""

    if receipt.get("schema_version") != "semantic-okf-evaluation-harbor-run/3.0":
        return
    observed_terminal_outcomes = harbor_runner.completed_trace_outcomes(run)
    if receipt.get("terminal_outcomes") != observed_terminal_outcomes:
        raise SummaryError(f"{run.name}: receipt terminal outcomes differ from its traces")
    if outcome is not None:
        _validate_v3_outcome_exit(run, outcome, receipt)
        _validate_scheduled_trace_outcome(run, outcome)


def installed_skill_names(value: object) -> list[str]:
    """Normalize legacy string and current object skill receipts to directory names."""

    if not isinstance(value, list):
        return []
    result: list[str] = []
    for row in value:
        path = row.get("path") if isinstance(row, Mapping) else row
        if isinstance(path, str):
            result.append(Path(path).name)
    return result


def is_sha256(value: object) -> bool:
    """Return whether a value is one lowercase hexadecimal SHA-256 digest."""

    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in HEX64 for character in value)
    )


def _valid_host_runtime_binding(value: object) -> bool:
    """Validate the closed, non-secret host runtime identity recorded by v2."""

    if not isinstance(value, Mapping) or set(value) != {
        "campaign_python",
        "harbor",
        "docker",
    }:
        return False
    python = value.get("campaign_python")
    harbor = value.get("harbor")
    docker = value.get("docker")
    if (
        not isinstance(python, Mapping)
        or set(python) != {"implementation", "version", "executable_sha256"}
        or python.get("implementation") != "CPython"
        or not isinstance(python.get("version"), str)
        or not is_sha256(python.get("executable_sha256"))
        or not isinstance(docker, Mapping)
        or set(docker) != {"version", "executable_sha256"}
        or not isinstance(docker.get("version"), str)
        or not is_sha256(docker.get("executable_sha256"))
        or not isinstance(harbor, Mapping)
        or set(harbor)
        != {
            "version",
            "entrypoint",
            "entrypoint_sha256",
            "interpreter_sha256",
            "distribution_tree_sha256",
            "dependencies",
        }
        or harbor.get("version") != frozen.HARBOR_VERSION
        or harbor.get("entrypoint") != "frozen/repo/vendor/harbor-cli"
        or not all(
            is_sha256(harbor.get(key))
            for key in (
                "entrypoint_sha256",
                "interpreter_sha256",
                "distribution_tree_sha256",
            )
        )
    ):
        return False
    dependencies = harbor.get("dependencies")
    if not isinstance(dependencies, Mapping) or set(dependencies) != {
        "count",
        "sha256",
        "packages",
    }:
        return False
    packages = dependencies.get("packages")
    if (
        not isinstance(packages, list)
        or dependencies.get("count") != len(packages)
        or not is_sha256(dependencies.get("sha256"))
        or packages != sorted(packages)
    ):
        return False
    payload = json.dumps(
        packages, ensure_ascii=True, separators=(",", ":")
    ).encode("ascii")
    return hashlib.sha256(payload).hexdigest() == dependencies.get("sha256")


def current_scorer_observability(
    rewards: Mapping[str, Any],
    diagnostics: Mapping[str, Any],
    *,
    has_ground_truth: bool | None = None,
) -> tuple[bool, list[str]]:
    """Require a complete, bounded metric vector from the current verifier contract."""

    errors: list[str] = []
    if diagnostics.get("status") not in CURRENT_SCORER_STATUSES:
        errors.append("scorer-status")
    for metric in METRICS:
        value = rewards.get(metric)
        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(float(value))
            or not 0.0 <= float(value) <= 1.0
        ):
            errors.append(f"metric:{metric}")
    binary_fields = (
        "response_contract",
        "non_null_answer",
        "reference_validity",
        "all_evidence_valid",
        "evidence_contract_gate",
        "minimum_document_gate",
        "mechanical_qualification_gate",
    )
    if not any(f"metric:{field}" in errors for field in binary_fields):
        if any(float(rewards[field]) not in {0.0, 1.0} for field in binary_fields):
            errors.append("algebra:binary-gates")
        evidence_gate = math.prod(
            float(rewards[field])
            for field in (
                "response_contract",
                "non_null_answer",
                "reference_validity",
                "all_evidence_valid",
            )
        )
        if not math.isclose(
            float(rewards["evidence_contract_gate"]), evidence_gate, abs_tol=1e-12
        ):
            errors.append("algebra:evidence-contract-gate")
        qualification = evidence_gate * float(rewards["minimum_document_gate"])
        if not math.isclose(
            float(rewards["mechanical_qualification_gate"]),
            qualification,
            abs_tol=1e-12,
        ):
            errors.append("algebra:mechanical-qualification-gate")
    if not any(
        f"metric:{field}" in errors
        for field in ("reward", "mechanical_qualification_gate", "mechanical_utility")
    ) and not math.isclose(
        float(rewards["reward"]),
        float(rewards["mechanical_qualification_gate"])
        * float(rewards["mechanical_utility"]),
        abs_tol=1e-12,
    ):
        errors.append("algebra:reward")
    utility_fields = (
        "mechanical_utility",
        "evidence_recall",
        "evidence_precision",
        "mrr",
        "ndcg",
        "required_document_coverage",
        "authoritative_evidence_anchor_coverage",
        "answer_claim_anchor_coverage",
        "important_negative_anchor_coverage",
    )
    if not any(f"metric:{field}" in errors for field in utility_fields):
        standard_utility = (
            0.35 * float(rewards["evidence_recall"])
            + 0.15 * float(rewards["evidence_precision"])
            + 0.20 * float(rewards["mrr"])
            + 0.30 * float(rewards["ndcg"])
        )
        grounded_utility = (
            0.15 * float(rewards["evidence_recall"])
            + 0.10 * float(rewards["ndcg"])
            + 0.15 * float(rewards["required_document_coverage"])
            + 0.15 * float(rewards["authoritative_evidence_anchor_coverage"])
            + 0.30 * float(rewards["answer_claim_anchor_coverage"])
            + 0.15 * float(rewards["important_negative_anchor_coverage"])
        )
        expected_utilities = (
            (grounded_utility,)
            if has_ground_truth is True
            else (standard_utility,)
            if has_ground_truth is False
            else (standard_utility, grounded_utility)
        )
        if not any(
            math.isclose(
                float(rewards["mechanical_utility"]), expected, abs_tol=1e-12
            )
            for expected in expected_utilities
        ):
            errors.append("algebra:mechanical-utility")
    status = diagnostics.get("status")
    response_contract = rewards.get("response_contract")
    if status == "scored-response" and response_contract != 1:
        errors.append("algebra:status-response-contract")
    if status == "agent-invalid-response" and response_contract != 0:
        errors.append("algebra:status-response-contract")
    return not errors, errors


def scheduled_contract(
    campaign: Path,
    *,
    dataset_id: str,
    families: Sequence[str],
    question_to_cohort: Mapping[str, str],
) -> dict[str, Any] | None:
    """Load and validate an optional fair-run schedule, outcomes, and checkpoint."""

    schedule_path = campaign / "schedule.json"
    digest_path = campaign / "schedule.sha256"
    if not schedule_path.exists() and not digest_path.exists():
        return None
    if not schedule_path.is_file() or not digest_path.is_file():
        raise SummaryError("campaign has an incomplete schedule binding")

    schedule = load_json(schedule_path)
    try:
        campaign_runner.validate_schedule(schedule)
    except campaign_runner.CampaignRunError as exc:
        raise SummaryError(f"invalid campaign schedule: {exc}") from exc
    try:
        recorded_digest = digest_path.read_text(encoding="ascii").strip().split()[0]
    except (OSError, UnicodeError, IndexError) as exc:
        raise SummaryError(f"cannot read campaign schedule digest: {digest_path}") from exc
    actual_digest = hashlib.sha256(schedule_path.read_bytes()).hexdigest()
    canonical_digest = campaign_runner.schedule_digest(schedule)
    if recorded_digest != actual_digest or actual_digest != canonical_digest:
        raise SummaryError("campaign schedule SHA-256 does not verify")
    if (
        schedule.get("dataset_id") != dataset_id
        or schedule.get("mode") != "consult-only"
        or schedule.get("families") != list(families)
    ):
        raise SummaryError("campaign schedule dataset, mode, or family identity drift")

    bindings_path = campaign / "input-bindings.json"
    bindings_digest_path = campaign / "input-bindings.sha256"
    bindings: dict[str, Any] | None = None
    bindings_digest: str | None = None
    if bindings_path.exists() or bindings_digest_path.exists():
        if not bindings_path.is_file() or not bindings_digest_path.is_file():
            raise SummaryError("campaign has an incomplete input-binding manifest")
        bindings = load_json(bindings_path)
        canonical_bindings = campaign_runner.canonical_json_bytes(bindings)
        bindings_digest = hashlib.sha256(bindings_path.read_bytes()).hexdigest()
        try:
            recorded_bindings_digest = (
                bindings_digest_path.read_text(encoding="ascii").strip().split()[0]
            )
        except (OSError, UnicodeError, IndexError) as exc:
            raise SummaryError("cannot read campaign input-binding digest") from exc
        if (
            hashlib.sha256(canonical_bindings).hexdigest() != bindings_digest
            or recorded_bindings_digest != bindings_digest
        ):
            raise SummaryError("campaign input-binding SHA-256 does not verify")
        expected_bindings = {
            "dataset_id": dataset_id,
            "mode": "consult-only",
            "schedule_sha256": actual_digest,
            "model": EXPECTED_MODEL,
            "pi_version": EXPECTED_PI_VERSION,
            "thinking": "high",
        }
        if any(bindings.get(key) != value for key, value in expected_bindings.items()):
            raise SummaryError("campaign input-binding runtime identity drift")
        binding_schema = bindings.get("schema_version")
        if binding_schema == campaign_runner.INPUT_BINDING_SCHEMA_V1:
            try:
                runtime_binding = campaign_runner.runtime_build_binding(
                    str(bindings.get("runtime_image"))
                )
            except campaign_runner.CampaignRunError as exc:
                raise SummaryError(f"campaign runtime build binding is invalid: {exc}") from exc
            if any(bindings.get(key) != value for key, value in runtime_binding.items()):
                raise SummaryError("campaign runtime build receipt drift")
        elif binding_schema == campaign_runner.INPUT_BINDING_SCHEMA_V2:
            expected_keys = {
                "schema_version",
                "dataset_id",
                "mode",
                "schedule_sha256",
                "model",
                "pi_version",
                "thinking",
                "runtime_image",
                "runtime_image_id",
                "runtime_build",
                "grader_tree_sha256",
                "families_registry_sha256",
                "dataset_descriptor_sha256",
                "pipeline_sources_sha256",
                "host_runtime",
                "execution_contract",
                "frozen_inputs",
                "offline_model_snapshots",
                "auditor",
                "families",
            }
            if set(bindings) != expected_keys:
                raise SummaryError("campaign input-binding v2 has an open or incomplete shape")
            try:
                frozen_manifest = frozen.verify_frozen_inputs(campaign)
            except frozen.BindingError as exc:
                raise SummaryError(f"campaign frozen inputs are invalid: {exc}") from exc
            frozen_repo = campaign / "frozen/repo"
            expected_pipeline = {
                relative: data.sha256_file(
                    frozen_repo / Path(*PurePosixPath(relative).parts)
                )
                for relative in frozen.PIPELINE_SOURCE_PATHS
            }
            descriptor = (
                frozen_repo
                / "evaluations/semantic-okf-datasets/datasets"
                / f"{dataset_id}.json"
            )
            expected_frozen = {
                "manifest_sha256": data.sha256_file(campaign / "frozen-inputs.json"),
                "source_campaign": frozen_manifest["source_campaign"],
                "frozen_repo": frozen_manifest["frozen_repo"],
                "task_runtime": frozen_manifest["task_runtime"],
                "harbor_adapter": frozen_manifest["harbor_adapter"],
            }
            expected_model_key = (
                f"{frozen.HF_MODEL_ID}@{frozen.HF_REVISION}"
            )
            expected_v2 = {
                "runtime_image": frozen_manifest["task_runtime"][
                    "runtime_image_reference"
                ],
                "runtime_image_id": frozen_manifest["task_runtime"]["runtime_image_id"],
                "grader_tree_sha256": data.tree_digest(
                    frozen_repo / "evaluations/semantic-okf-harbor/grader"
                ),
                "families_registry_sha256": data.sha256_file(
                    frozen_repo / "evaluations/semantic-okf-datasets/families.json"
                ),
                "dataset_descriptor_sha256": data.sha256_file(descriptor),
                "pipeline_sources_sha256": expected_pipeline,
                "frozen_inputs": expected_frozen,
                "offline_model_snapshots": {
                    expected_model_key: frozen_manifest["offline_model"]
                },
                "execution_contract": campaign_runner.execution_contract(
                    campaign_runner.RunSettings(
                        auth_file=Path("<private-auth>"),
                        hf_cache=Path("<frozen-hf>"),
                        max_concurrency=1,
                    )
                ),
            }
            if any(bindings.get(key) != value for key, value in expected_v2.items()):
                raise SummaryError("campaign input-binding v2 frozen identity drift")
            runtime_build = bindings.get("runtime_build")
            try:
                expected_runtime_build = campaign_runner.pinned_runtime_build_binding(
                    str(bindings.get("runtime_image_id"))
                )
            except campaign_runner.CampaignRunError as exc:
                raise SummaryError(
                    f"campaign input-binding v2 runtime receipt is invalid: {exc}"
                ) from exc
            if runtime_build != expected_runtime_build:
                raise SummaryError("campaign input-binding v2 runtime receipt is invalid")
            host_runtime = bindings.get("host_runtime")
            if not _valid_host_runtime_binding(host_runtime):
                raise SummaryError("campaign input-binding v2 host runtime is invalid")
            auditor = bindings.get("auditor")
            if (
                not isinstance(auditor, Mapping)
                or auditor.get("summarizer_sha256")
                != expected_pipeline[
                    "evaluations/semantic-okf-datasets/summarize_consult_campaign.py"
                ]
                or auditor.get("grader_tree_sha256")
                != bindings.get("grader_tree_sha256")
            ):
                raise SummaryError("campaign input-binding v2 auditor identity drift")
        else:
            raise SummaryError("campaign input-binding schema is unsupported")
        bound_families = bindings.get("families")
        if not isinstance(bound_families, Mapping) or set(bound_families) != set(families):
            raise SummaryError("campaign input-binding family matrix drift")

    cells_by_run: dict[str, Mapping[str, Any]] = {}
    cells_by_sequence: dict[int, Mapping[str, Any]] = {}
    for cell in schedule["cells"]:
        question_id = str(cell["question_id"])
        if cell.get("cohort") != question_to_cohort.get(question_id):
            raise SummaryError(f"campaign schedule cohort drift for {question_id}")
        relative_run = str(cell["shard_path"])
        sequence = int(cell["sequence"])
        cells_by_run[relative_run] = cell
        cells_by_sequence[sequence] = cell

    runs_root = campaign / "runs"
    if runs_root.is_dir():
        unexpected = sorted(
            path.relative_to(campaign).as_posix()
            for path in runs_root.iterdir()
            if path.is_dir() and path.relative_to(campaign).as_posix() not in cells_by_run
        )
        if unexpected:
            raise SummaryError(f"campaign has off-schedule run directories: {unexpected}")

    outcomes: dict[int, dict[str, Any]] = {}
    outcomes_root = campaign / "outcomes"
    if outcomes_root.exists():
        if outcomes_root.is_symlink() or not outcomes_root.is_dir():
            raise SummaryError("campaign outcomes path is not a regular directory")
        for path in sorted(outcomes_root.iterdir()):
            if (
                path.is_symlink()
                or not path.is_file()
                or path.suffix != ".json"
                or not path.stem.isdigit()
            ):
                raise SummaryError(f"campaign has an invalid outcome artifact: {path}")
            sequence = int(path.stem)
            cell = cells_by_sequence.get(sequence)
            if cell is None or path.name != f"{sequence:04d}.json":
                raise SummaryError(f"campaign has an off-schedule outcome artifact: {path}")
            outcome = load_json(path)
            expected = {
                "schema_version": "semantic-okf-consult-campaign-outcome/1.0",
                "sequence": sequence,
                "family": cell["family"],
                "cohort": cell["cohort"],
                "question_id": cell["question_id"],
            }
            if (
                type(outcome.get("sequence")) is not int
                or any(outcome.get(key) != value for key, value in expected.items())
            ):
                raise SummaryError(f"campaign outcome identity drift: {path}")
            required_outcome_keys = {"error_code", "failure_domain", "outcome"}
            if (
                bindings is not None
                and bindings.get("schema_version")
                == campaign_runner.INPUT_BINDING_SCHEMA_V2
            ):
                required_outcome_keys.update({"run_exit_code", "trace_path"})
            if (
                not required_outcome_keys.issubset(outcome)
                or campaign_runner._bind_outcome(cell, outcome) != outcome
                or campaign_runner.canonical_json_bytes(outcome) != path.read_bytes()
            ):
                raise SummaryError(f"campaign outcome has an invalid closed shape: {path}")
            if "provider_reset" in outcome:
                sanitized_reset = campaign_runner.checkpoint_trigger(outcome).get(
                    "provider_reset"
                )
                if outcome.get("provider_reset") != sanitized_reset:
                    raise SummaryError(f"campaign outcome provider reset is invalid: {path}")
            outcomes[sequence] = outcome

    checkpoints_root = campaign / "checkpoints"
    allowed_checkpoint_names = {"aborted.json", "completed.json"}
    if checkpoints_root.exists():
        if checkpoints_root.is_symlink() or not checkpoints_root.is_dir():
            raise SummaryError("campaign checkpoints path is not a regular directory")
        for path in checkpoints_root.iterdir():
            if (
                path.name not in allowed_checkpoint_names
                or path.is_symlink()
                or not path.is_file()
            ):
                raise SummaryError(f"campaign has an invalid checkpoint artifact: {path}")
    checkpoint_files = [
        checkpoints_root / name
        for name in sorted(allowed_checkpoint_names)
        if (checkpoints_root / name).is_file()
    ]
    if len(checkpoint_files) > 1:
        raise SummaryError("campaign has conflicting terminal checkpoints")
    checkpoint: dict[str, Any] | None = None
    if checkpoint_files:
        checkpoint_path = checkpoint_files[0]
        checkpoint = load_json(checkpoint_path)
        expected_status = checkpoint_path.stem
        trigger: Mapping[str, Any] | None = None
        if expected_status == "completed":
            if len(outcomes) != len(cells_by_sequence):
                raise SummaryError("completed checkpoint does not cover the full schedule")
            if any(
                row.get("outcome") in campaign_runner.ABORT_OUTCOMES
                for row in outcomes.values()
            ):
                raise SummaryError("completed checkpoint contains aborting outcomes")
        if expected_status == "aborted":
            aborts = [
                row
                for row in outcomes.values()
                if row.get("outcome") in campaign_runner.ABORT_OUTCOMES
            ]
            if not aborts:
                raise SummaryError("aborted checkpoint has no aborting outcome")
            trigger = min(aborts, key=lambda row: int(row["sequence"]))
        try:
            checkpoint = campaign_runner._validate_terminal_checkpoint(
                checkpoint,
                status=expected_status,
                digest=actual_digest,
                outcomes=outcomes,
                trigger=trigger,
                input_bindings_digest=bindings_digest,
            )
        except campaign_runner.CampaignRunError as exc:
            raise SummaryError(f"campaign checkpoint drift: {checkpoint_path}") from exc

    return {
        "schedule": schedule,
        "schedule_sha256": actual_digest,
        "cells_by_run": cells_by_run,
        "cells_by_sequence": cells_by_sequence,
        "outcomes": outcomes,
        "checkpoint": checkpoint,
        "input_bindings": bindings,
        "input_bindings_sha256": bindings_digest,
        "input_binding_schema_version": (
            bindings.get("schema_version") if bindings is not None else None
        ),
        "execution_complete": bool(
            checkpoint
            and checkpoint.get("status") == "completed"
            and bindings is not None
            and bindings.get("schema_version")
            == campaign_runner.INPUT_BINDING_SCHEMA_V2
        ),
    }


def scheduled_task_manifests(
    tasks_root: Path, dataset_id: str, families: Sequence[str]
) -> dict[str, dict[str, Any]]:
    """Load the exact generated task manifests used to validate scheduled receipts."""

    manifests: dict[str, dict[str, Any]] = {}
    for family in families:
        path = tasks_root / family / "manifest.json"
        if not path.is_file():
            raise SummaryError(f"scheduled task manifest is absent: {path}")
        manifest = load_json(path)
        expected = {"dataset_id": dataset_id, "family": family, "mode": "consult-only"}
        if any(manifest.get(key) != value for key, value in expected.items()):
            raise SummaryError(f"scheduled task manifest identity drift: {path}")
        manifests[family] = {
            "manifest_sha256": data.sha256_file(path),
            "tasks_tree_sha256": data.tree_digest(path.parent),
            "reference_bundle_tree_sha256": manifest.get("reference_bundle_tree_sha256"),
            "reference_records_sha256": manifest.get("reference_records_sha256"),
            "runtime_image": manifest.get("runtime_image"),
        }
        if not all(
            is_sha256(manifests[family][key])
            for key in (
                "manifest_sha256",
                "tasks_tree_sha256",
                "reference_bundle_tree_sha256",
                "reference_records_sha256",
            )
        ) or not isinstance(manifests[family]["runtime_image"], str):
            raise SummaryError(f"scheduled task manifest has invalid bindings: {path}")
    return manifests


def _expected_frozen_job_configs(
    run: Path,
    receipt: Mapping[str, Any],
    *,
    expected_skill: str,
    input_binding: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Return the exact submitted and Harbor-persisted frozen job configurations."""

    campaign = run.parent.parent
    frozen_repo = campaign / "frozen/repo"
    family = str(receipt["family"])
    cohort = str(receipt["cohort"])
    dataset_id = str(receipt["dataset_id"])
    mounts: list[dict[str, Any]] = [
        {
            "type": "bind",
            "source": str((campaign / "bundles" / family).resolve()),
            "target": "/knowledge",
            "read_only": True,
            "bind": {"create_host_path": False},
        },
        {
            "type": "bind",
            "source": "<ephemeral-auth-directory>",
            "target": "/root/.pi/agent",
            "bind": {"create_host_path": False},
        },
    ]
    if input_binding.get("offline_model_snapshot") is not None:
        mounts.append(
            {
                "type": "bind",
                "source": str((campaign / "frozen/model-cache/hub").resolve()),
                "target": "/models/huggingface/hub",
                "read_only": True,
                "bind": {"create_host_path": False},
            }
        )
    agents = [
        {
            "name": "pi",
            "model_name": EXPECTED_MODEL,
            "n_concurrent": 1,
            "skills": [str((frozen_repo / "skills" / expected_skill).resolve())],
            "kwargs": {"version": EXPECTED_PI_VERSION, "thinking": "high"},
            "env": {"PI_CODING_AGENT_DIR": "/root/.pi/agent"},
        }
    ]
    datasets = [
        {
            "path": str(
                (
                    frozen_repo
                    / "evaluations/semantic-okf-datasets/generated/tasks"
                    / dataset_id
                    / "consult-only"
                    / family
                    / cohort
                ).resolve()
            ),
            "task_names": list(receipt["task_ids"]),
        }
    ]
    effective = {
        "job_name": run.name,
        "jobs_dir": str(run.parent.resolve()),
        "n_concurrent_trials": 1,
        "environment": {"type": "docker", "mounts": mounts},
        "agents": agents,
        "datasets": datasets,
    }
    submitted = {
        **effective,
        "n_attempts": 1,
        "quiet": False,
        "retry": {"max_retries": 0},
        "environment": {"type": "docker", "delete": True, "mounts": mounts},
    }
    return submitted, effective


def _validate_frozen_effective_config(
    run: Path,
    receipt: Mapping[str, Any],
    *,
    expected_skill: str,
    input_binding: Mapping[str, Any],
) -> None:
    """Bind the submitted redacted config and Harbor's effective persisted config."""

    redacted_path = run / "job-config.redacted.json"
    actual_path = run / "config.json"
    if not redacted_path.is_file() or not actual_path.is_file():
        raise SummaryError(f"{run.name}: frozen execution config is incomplete")
    submitted, effective = _expected_frozen_job_configs(
        run,
        receipt,
        expected_skill=expected_skill,
        input_binding=input_binding,
    )
    if load_json(redacted_path) != submitted:
        raise SummaryError(f"{run.name}: submitted frozen job config drift")
    actual = load_json(actual_path)
    environment = actual.get("environment")
    mounts = environment.get("mounts") if isinstance(environment, Mapping) else None
    auth = next(
        (
            mount
            for mount in mounts
            if isinstance(mount, Mapping) and mount.get("target") == "/root/.pi/agent"
        ),
        None,
    ) if isinstance(mounts, list) else None
    auth_source = auth.get("source") if isinstance(auth, Mapping) else None
    auth_path = PurePosixPath(auth_source) if isinstance(auth_source, str) else None
    expected_auth_path = PurePosixPath(
        harbor_runner.frozen_auth_session_directory(
            str(receipt.get("campaign_input_bindings_sha256"))
        ).as_posix()
    )
    if (
        auth_path is None
        or auth_path != expected_auth_path
    ):
        raise SummaryError(f"{run.name}: effective auth mount source is invalid")
    normalized = json.loads(json.dumps(actual))
    for mount in normalized["environment"]["mounts"]:
        if mount.get("target") == "/root/.pi/agent":
            mount["source"] = "<ephemeral-auth-directory>"
    if normalized != effective:
        raise SummaryError(f"{run.name}: effective frozen job config drift")


def validate_scheduled_receipt(
    run: Path,
    receipt: Mapping[str, Any],
    *,
    expected_skill: str,
    task_manifest: Mapping[str, Any],
    input_binding: Mapping[str, Any] | None,
    input_bindings_sha256: str | None,
    runtime_image_id: str | None,
) -> str:
    """Validate versioned task, resource, and skill hashes for one scheduled shard."""

    v2 = input_binding is not None and "offline_model_snapshot" in input_binding
    expected = {
        "schema_version": (
            "semantic-okf-evaluation-harbor-run/3.0"
            if v2
            else "semantic-okf-evaluation-harbor-run/2.0"
        ),
        "generated_tasks_manifest_sha256": task_manifest["manifest_sha256"],
        "resource_tree_sha256": task_manifest["reference_bundle_tree_sha256"],
        "records_sha256": task_manifest["reference_records_sha256"],
    }
    if any(receipt.get(key) != value for key, value in expected.items()):
        raise SummaryError(f"{run.name}: scheduled task or resource hash drift")
    if v2:
        _validate_v3_execution_receipt(run, receipt)
    skills = receipt.get("installed_skills")
    if not isinstance(skills, list) or len(skills) != 1 or not isinstance(skills[0], Mapping):
        raise SummaryError(f"{run.name}: scheduled receipt has no exact skill binding")
    skill_path = skills[0].get("path")
    skill_hash = skills[0].get("tree_sha256")
    if not isinstance(skill_path, str) or Path(skill_path).name != expected_skill or not is_sha256(skill_hash):
        raise SummaryError(f"{run.name}: scheduled receipt skill hash drift")
    if input_binding is not None:
        expected_binding = {
            "consult_skill": expected_skill,
            "consult_skill_tree_sha256": skill_hash,
            "generated_tasks_tree_sha256": task_manifest["tasks_tree_sha256"],
            "reference_bundle_tree_sha256": task_manifest[
                "reference_bundle_tree_sha256"
            ],
            "reference_records_sha256": task_manifest["reference_records_sha256"],
            "runtime_image": task_manifest["runtime_image"],
            "task_manifest_sha256": task_manifest["manifest_sha256"],
        }
        if v2:
            expected_binding["offline_model_snapshot"] = input_binding.get(
                "offline_model_snapshot"
            )
        if input_binding != expected_binding:
            raise SummaryError(f"{run.name}: receipt differs from campaign input bindings")
    if v2:
        campaign = run.parent.parent
        redacted_config = run / "job-config.redacted.json"
        if (
            receipt.get("campaign_input_bindings_sha256")
            != input_bindings_sha256
            or receipt.get("frozen_inputs_manifest_sha256")
            != data.sha256_file(campaign / "frozen-inputs.json")
            or receipt.get("runtime_image") != task_manifest["runtime_image"]
            or receipt.get("runtime_image_id") != runtime_image_id
            or receipt.get("authentication_continuity")
            != "binding-scoped-shared-session"
            or not redacted_config.is_file()
            or receipt.get("job_config_redacted_sha256")
            != data.sha256_file(redacted_config)
        ):
            raise SummaryError(f"{run.name}: frozen execution receipt drift")
        _validate_frozen_effective_config(
            run,
            receipt,
            expected_skill=expected_skill,
            input_binding=input_binding,
        )
    return str(skill_hash)


def validate_run_identity(
    run: Path,
    *,
    dataset_id: str,
    family: str,
    cohort: str,
    task_ids: Sequence[str],
    allow_partial: bool,
) -> dict[str, Any] | None:
    """Validate model, Pi, skill, mode, resource, and task bindings for one job."""

    config_path = run / "config.json"
    receipt_path = run / "run-receipt.json"
    if not config_path.is_file() or not receipt_path.is_file():
        if allow_partial:
            return None
        missing = config_path if not config_path.is_file() else receipt_path
        raise SummaryError(f"missing run identity artifact: {missing}")
    config = load_json(config_path)
    receipt = load_json(receipt_path)
    agents = config.get("agents")
    if not isinstance(agents, list) or len(agents) != 1 or not isinstance(agents[0], dict):
        raise SummaryError(f"{run.name}: expected exactly one agent")
    agent = agents[0]
    kwargs = agent.get("kwargs", {})
    if (
        agent.get("name") != "pi"
        or agent.get("model_name") != EXPECTED_MODEL
        or not isinstance(kwargs, dict)
        or kwargs.get("version") != EXPECTED_PI_VERSION
        or kwargs.get("thinking") != "high"
    ):
        raise SummaryError(f"{run.name}: model, Pi version, or thinking level drift")
    expected_skill = data.load_families()[family]["consult_skill"]
    config_skills = agent.get("skills")
    if (
        not isinstance(config_skills, list)
        or len(config_skills) != 1
        or not isinstance(config_skills[0], str)
        or Path(config_skills[0]).name != expected_skill
    ):
        raise SummaryError(f"{run.name}: expected only {expected_skill}")
    datasets = config.get("datasets")
    configured = (
        datasets[0].get("task_names")
        if isinstance(datasets, list)
        and len(datasets) == 1
        and isinstance(datasets[0], dict)
        else None
    )
    if configured != list(task_ids):
        raise SummaryError(f"{run.name}: configured task IDs differ from its receipt")
    expected = {
        "dataset_id": dataset_id,
        "family": family,
        "mode": "consult-only",
        "cohort": cohort,
        "task_ids": list(task_ids),
        "attempts": 1,
        "model": EXPECTED_MODEL,
        "pi_version": EXPECTED_PI_VERSION,
        "public_mount_target": "/knowledge",
        "prebuilt_knowledge_mounted": True,
        "raw_sources_mounted": False,
    }
    if any(receipt.get(key) != value for key, value in expected.items()):
        raise SummaryError(f"{run.name}: run receipt identity drift")
    if installed_skill_names(receipt.get("installed_skills")) != [expected_skill]:
        raise SummaryError(f"{run.name}: receipt must bind exactly {expected_skill}")
    if receipt.get("resource_kind") != "processed-knowledge":
        raise SummaryError(f"{run.name}: receipt is not bound to processed knowledge")
    return receipt


def trace_for_trial(result_path: Path) -> dict[str, Any]:
    """Classify a trial trace, including a stable fallback for absent artifacts."""

    for candidate in (
        result_path.parent / "artifacts/pi.jsonl",
        result_path.parent / "agent/pi.txt",
    ):
        if candidate.is_file():
            return classify_pi_trace(candidate)
    return {
        "outcome": "missing-trace",
        "failure_domain": "agent",
        "error_code": None,
        "answer_text": None,
        "stop_reason": None,
        "parsed_events": 0,
    }


def rescore_trial(
    result_path: Path,
    *,
    tasks_root: Path,
    family: str,
    cohort: str,
    question_id: str,
) -> tuple[dict[str, float], dict[str, Any]]:
    """Apply the current checked grader to one immutable historical Pi trace."""

    tests = tasks_root / family / cohort / question_id / "tests"
    pi_log = result_path.parent / "artifacts/pi.jsonl"
    required = (
        pi_log,
        tests / "question.json",
        tests / "records.jsonl",
        tests / "source-combination.json",
    )
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise SummaryError(f"cannot rescore {family}/{question_id}; missing: {missing}")
    ground_truth = tests / "hard-ground-truth.json"
    try:
        return grader.score(
            argparse.Namespace(
                pi_log=pi_log,
                question=tests / "question.json",
                ledger=tests / "records.jsonl",
                crosswalk=tests / "source-combination.json",
                ground_truth=ground_truth if ground_truth.is_file() else None,
                authority_root=tests / "authority",
            )
        )
    except (OSError, UnicodeError, grader.ScoreError, KeyError, TypeError, ValueError) as exc:
        raise SummaryError(f"corrected grader failed for {family}/{question_id}: {exc}") from exc


def normalized_metrics(rewards: Mapping[str, Any]) -> dict[str, float | None]:
    """Normalize current metrics and explicitly named historical compatibility aliases."""

    result: dict[str, float | None] = {}
    for metric in METRICS:
        value = rewards.get(metric)
        if value is None and metric in LEGACY_METRICS:
            value = rewards.get(LEGACY_METRICS[metric])
        if value is None and metric == "mechanical_qualification_gate":
            value = rewards.get("quality_gate")
        result[metric] = (
            float(value)
            if isinstance(value, (int, float)) and not isinstance(value, bool)
            else None
        )
    return result


def trial_row(
    run: Path,
    dataset_id: str,
    family: str,
    cohort: str,
    question_id: str,
    result_path: Path,
    *,
    rescore: bool = False,
    tasks_root: Path | None = None,
    require_current_scorer: bool = False,
) -> dict[str, Any]:
    """Normalize one immutable Harbor trial with provider-aware status."""

    result = load_json(result_path)
    task_name = result.get("task_name")
    expected_task_name = (
        f"knowledge/{dataset_id}__consult-only__{family}__{question_id}"
    )
    if task_name != expected_task_name:
        raise SummaryError(f"{result_path}: task name does not match its directory")
    verifier = result.get("verifier_result")
    historical_rewards = verifier.get("rewards", {}) if isinstance(verifier, dict) else {}
    if not isinstance(historical_rewards, dict):
        historical_rewards = {}
    historical_diagnostics_path = result_path.parent / "verifier/diagnostics.json"
    historical_diagnostics = (
        load_json(historical_diagnostics_path)
        if not rescore and historical_diagnostics_path.is_file()
        else {}
    )
    historical_reward_path = result_path.parent / "verifier/reward.json"
    historical_reward_artifact = (
        load_json(historical_reward_path)
        if not rescore and historical_reward_path.is_file()
        else None
    )
    if rescore:
        if tasks_root is None:
            raise SummaryError("rescore requested without a generated task root")
        rewards, diagnostics = rescore_trial(
            result_path,
            tasks_root=tasks_root,
            family=family,
            cohort=cohort,
            question_id=question_id,
        )
        scoring_source = "corrected-rescore"
    else:
        rewards, diagnostics = historical_rewards, historical_diagnostics
        scoring_source = "historical-verifier"

    trace = trace_for_trial(result_path)
    outcome = str(trace["outcome"])
    exception = result.get("exception_info")
    exception_type = exception.get("exception_type") if isinstance(exception, dict) else None
    scorer_observable: bool | None = None
    observability_errors: list[str] = []
    if require_current_scorer:
        ground_truth = (
            tasks_root
            / family
            / cohort
            / question_id
            / "tests/hard-ground-truth.json"
            if tasks_root is not None
            else None
        )
        scorer_observable, observability_errors = current_scorer_observability(
            rewards,
            diagnostics,
            has_ground_truth=ground_truth.is_file() if ground_truth is not None else None,
        )
        integrity_errors: list[str] = []
        if (
            diagnostics.get("schema_version")
            != "semantic-okf-harbor-redacted-diagnostics/2.0"
        ):
            integrity_errors.append("diagnostics:schema-version")
        if diagnostics.get("question_id") != question_id:
            integrity_errors.append("diagnostics:question-id")
        if not rescore:
            if historical_reward_artifact is None:
                integrity_errors.append("verifier-artifact:missing-reward-json")
            elif historical_reward_artifact != historical_rewards:
                integrity_errors.append("verifier-artifact:reward-mismatch")
        observability_errors.extend(integrity_errors)
        scorer_observable = bool(scorer_observable) and not integrity_errors
        evaluator_failure = diagnostics.get("status") == "verifier-error" or (
            outcome == "answer-emitted" and not scorer_observable
        )
    else:
        evaluator_failure = (
            outcome == "answer-emitted" and diagnostics.get("status") == "verifier-error"
        )
    evaluable = outcome == "answer-emitted" and not evaluator_failure
    if require_current_scorer:
        evaluable = evaluable and bool(scorer_observable)
    if evaluator_failure:
        status = "evaluator-failure"
    elif outcome in PROVIDER_OUTCOMES:
        status = "provider-failure"
    elif outcome != "answer-emitted":
        status = "agent-execution-failure"
    elif diagnostics.get("status") == "agent-invalid-response":
        status = "scored-invalid-response"
    else:
        status = "scored-response"

    metrics = normalized_metrics(rewards)
    if not evaluable:
        metrics = {metric: None for metric in METRICS}
    agent = result.get("agent_result") if isinstance(result.get("agent_result"), dict) else {}
    started = parse_time(result.get("started_at"))
    finished = parse_time(result.get("finished_at"))
    duration = (finished - started).total_seconds() if started and finished else None
    return {
        "family": family,
        "cohort": cohort,
        "question_id": question_id,
        "trial_id": result.get("id"),
        "run": run.relative_to(run.parents[1]).as_posix() if len(run.parents) > 1 else run.name,
        "status": status,
        "agent_outcome": outcome,
        "failure_domain": trace.get("failure_domain"),
        "error_code": trace.get("error_code"),
        "provider_reset": trace.get("provider_reset"),
        "complete_response_observed": outcome == "answer-emitted",
        "evaluable": evaluable,
        "evaluator_failure": evaluator_failure,
        "scorer_observable": scorer_observable,
        "scorer_observability_errors": observability_errors,
        "secondary_anomalies": [exception_type] if isinstance(exception_type, str) else [],
        "scoring_source": scoring_source,
        "duration_seconds": duration,
        "tokens": {
            "input": int(agent.get("n_input_tokens") or 0),
            "cache": int(agent.get("n_cache_tokens") or 0),
            "output": int(agent.get("n_output_tokens") or 0),
        },
        "metrics": metrics,
        "diagnostics": {
            "status": diagnostics.get("status"),
            "parse_error": diagnostics.get("parse_error"),
            "contract_errors": diagnostics.get("contract_errors", []),
            "evidence_count": diagnostics.get("evidence_count"),
            "covered_qrel_count": diagnostics.get("covered_qrel_count"),
            "minimum_document_count": diagnostics.get("minimum_document_count"),
            "semantic_correctness": diagnostics.get("semantic_correctness", "not-scored"),
        },
        "historical_metrics": normalized_metrics(historical_rewards) if rescore else None,
    }


def aggregate(rows: Sequence[Mapping[str, Any]], expected_trials: int) -> dict[str, Any]:
    """Aggregate only evaluable response metrics and expose terminal outcome counts."""

    metrics: dict[str, Any] = {}
    for metric in METRICS:
        values = [row["metrics"][metric] for row in rows if row["metrics"][metric] is not None]
        metrics[metric] = {
            "mean": statistics.fmean(values) if values else None,
            "observed": len(values),
        }
    outcomes = Counter(str(row["agent_outcome"]) for row in rows)
    statuses = Counter(str(row["status"]) for row in rows)
    anomalies = Counter(
        str(value) for row in rows for value in row.get("secondary_anomalies", [])
    )
    tokens = {
        name: sum(int(row["tokens"][name]) for row in rows)
        for name in ("input", "cache", "output")
    }
    durations = [
        float(row["duration_seconds"])
        for row in rows
        if row["duration_seconds"] is not None
    ]
    return {
        "expected_trials": expected_trials,
        "result_trials": len(rows),
        "evaluable_trials": sum(bool(row["evaluable"]) for row in rows),
        "complete_response_trials": sum(bool(row["complete_response_observed"]) for row in rows),
        "agent_outcomes": dict(sorted(outcomes.items())),
        "scoring_statuses": dict(sorted(statuses.items())),
        "secondary_anomalies": dict(sorted(anomalies.items())),
        "metrics": metrics,
        "tokens": tokens,
        "mean_duration_seconds": statistics.fmean(durations) if durations else None,
    }


def mechanical_ranking(
    by_family: Mapping[str, Mapping[str, Any]],
) -> tuple[list[str], list[str], str | None]:
    """Order rewards and represent a top-score tie without a false singular winner."""

    ranked = sorted(
        (
            (family, float(row["metrics"]["reward"]["mean"]))
            for family, row in by_family.items()
        ),
        key=lambda item: (-item[1], item[0]),
    )
    ranking = [family for family, _score in ranked]
    top_score = ranked[0][1]
    leaders = [
        family
        for family, score in ranked
        if math.isclose(score, top_score, rel_tol=0.0, abs_tol=1e-12)
    ]
    return ranking, leaders, leaders[0] if len(leaders) == 1 else None


def run_directories(campaign: Path) -> list[Path]:
    """Discover legacy cohort jobs and current one-task shards by durable markers."""

    root = campaign / "runs"
    if not root.is_dir():
        return []
    directories = {path.parent for path in root.rglob("run-receipt.json")}
    directories.update(path.parent for path in root.rglob("job-config.redacted.json"))
    return sorted(directories)


def summarize(
    campaign: Path,
    dataset_id: str,
    *,
    allow_partial: bool = False,
    allow_invalid: bool = False,
    rescore: bool = False,
    tasks_root: Path | None = None,
) -> dict[str, Any]:
    """Validate a campaign matrix and distinguish structural presence from rankability."""

    dataset = data.load_dataset(dataset_id)
    cohorts = data.dataset_cohorts(dataset)
    cohort_names = list(dataset["partition_cohorts"])
    families = sorted(data.load_families())
    question_to_cohort = {
        identifier: cohort for cohort in cohort_names for identifier in cohorts[cohort]
    }
    expected_keys = {
        (family, identifier)
        for family in families
        for identifier in question_to_cohort
    }
    default_tasks = HERE / "generated/tasks" / dataset_id / "consult-only"
    selected_tasks = (tasks_root or default_tasks).resolve()
    scheduled = scheduled_contract(
        campaign,
        dataset_id=dataset_id,
        families=families,
        question_to_cohort=question_to_cohort,
    )
    task_manifests = (
        scheduled_task_manifests(selected_tasks, dataset_id, families)
        if scheduled is not None
        else {}
    )
    rows_by_key: dict[tuple[str, str], dict[str, Any]] = {}
    receipts: list[dict[str, Any]] = []
    incomplete_run_identities: list[str] = []
    skill_hashes: dict[str, set[str]] = {family: set() for family in families}

    for run in run_directories(campaign):
        scheduled_cell: Mapping[str, Any] | None = None
        if scheduled is not None:
            relative_run = run.relative_to(campaign).as_posix()
            scheduled_cell = scheduled["cells_by_run"].get(relative_run)
            if scheduled_cell is None:
                raise SummaryError(f"off-schedule run identity: {relative_run}")
        receipt_path = run / "run-receipt.json"
        if not receipt_path.is_file():
            incomplete_run_identities.append(str(run.relative_to(campaign)))
            continue
        receipt_preview = load_json(receipt_path)
        family = receipt_preview.get("family")
        cohort = receipt_preview.get("cohort")
        task_ids = receipt_preview.get("task_ids")
        if family not in families or cohort not in cohort_names or not isinstance(task_ids, list):
            raise SummaryError(f"{run}: receipt has an invalid family, cohort, or task list")
        allowed = cohorts[str(cohort)]
        if (
            not task_ids
            or len(task_ids) != len(set(task_ids))
            or any(identifier not in allowed for identifier in task_ids)
        ):
            raise SummaryError(f"{run}: task IDs are not a unique subset of {cohort}")
        if scheduled_cell is not None and (
            family != scheduled_cell["family"]
            or cohort != scheduled_cell["cohort"]
            or task_ids != [scheduled_cell["question_id"]]
        ):
            raise SummaryError(f"{run.name}: scheduled one-task shard identity drift")
        receipt = validate_run_identity(
            run,
            dataset_id=dataset_id,
            family=str(family),
            cohort=str(cohort),
            task_ids=task_ids,
            allow_partial=allow_partial,
        )
        if receipt is None:
            incomplete_run_identities.append(str(run.relative_to(campaign)))
            continue
        if scheduled_cell is not None:
            expected_skill = data.load_families()[str(family)]["consult_skill"]
            skill_hashes[str(family)].add(
                validate_scheduled_receipt(
                    run,
                    receipt,
                    expected_skill=expected_skill,
                    task_manifest=task_manifests[str(family)],
                    input_binding=(
                        scheduled["input_bindings"]["families"][str(family)]
                        if scheduled["input_bindings"] is not None
                        else None
                    ),
                    input_bindings_sha256=scheduled["input_bindings_sha256"],
                    runtime_image_id=(
                        scheduled["input_bindings"].get("runtime_image_id")
                        if scheduled["input_bindings"] is not None
                        else None
                    ),
                )
            )
        scheduled_outcome: Mapping[str, Any] | None = None
        if scheduled_cell is not None:
            sequence = int(scheduled_cell["sequence"])
            scheduled_outcome = scheduled["outcomes"].get(sequence)
            if scheduled_outcome is None:
                incomplete_run_identities.append(f"outcomes/{sequence:04d}.json")
            _validate_v3_scheduled_completion(run, scheduled_outcome, receipt)
        receipts.append(receipt)
        for question_id in task_ids:
            matches = list(run.glob(f"{question_id}__*/result.json"))
            if len(matches) > 1:
                raise SummaryError(f"{run.name}: duplicate result for {question_id}")
            if not matches:
                continue
            key = (str(family), str(question_id))
            if key in rows_by_key:
                raise SummaryError(f"duplicate campaign result for {family}/{question_id}")
            row = trial_row(
                run,
                dataset_id,
                str(family),
                str(cohort),
                str(question_id),
                matches[0],
                rescore=rescore,
                tasks_root=selected_tasks,
                require_current_scorer=True,
            )
            if scheduled_cell is not None:
                outcome = scheduled_outcome
                if outcome is not None:
                    if (
                        receipt.get("schema_version")
                        != "semantic-okf-evaluation-harbor-run/3.0"
                    ):
                        _validate_scheduled_trace_outcome(run, outcome)
                    if receipt.get("terminal_outcomes") != {row["agent_outcome"]: 1}:
                        raise SummaryError(
                            f"{run.name}: receipt terminal outcomes differ from its trace"
                        )
            rows_by_key[key] = row

    if scheduled is not None:
        for family, values in skill_hashes.items():
            if len(values) > 1:
                raise SummaryError(f"scheduled campaign mixed {family} skill tree hashes")
        if scheduled["input_bindings"] is None:
            incomplete_run_identities.append("input-bindings.json")
        if not scheduled["execution_complete"]:
            incomplete_run_identities.append("checkpoints/completed.json")

    missing_keys = sorted(expected_keys - set(rows_by_key))
    rows = list(rows_by_key.values())
    by_family: dict[str, Any] = {}
    for family in families:
        family_rows = [row for row in rows if row["family"] == family]
        by_family[family] = {
            **aggregate(family_rows, len(question_to_cohort)),
            "cohorts": {
                cohort: aggregate(
                    [row for row in family_rows if row["cohort"] == cohort],
                    len(cohorts[cohort]),
                )
                for cohort in cohort_names
            },
        }

    incomplete_run_identities = sorted(set(incomplete_run_identities))
    scheduled_execution_complete = scheduled is None or bool(scheduled["execution_complete"])
    execution_receipts_clean = (
        scheduled is None
        or scheduled.get("input_binding_schema_version")
        != campaign_runner.INPUT_BINDING_SCHEMA_V2
        or all(receipt.get("run_status") == "completed" for receipt in receipts)
    )
    structurally_complete = (
        not missing_keys and not incomplete_run_identities and scheduled_execution_complete
    )
    provider_clean = all(row["agent_outcome"] not in PROVIDER_OUTCOMES for row in rows)
    evaluator_clean = all(not row["evaluator_failure"] for row in rows)
    cohort_observable = all(
        any(
            row["family"] == family and row["cohort"] == cohort and row["evaluable"]
            for row in rows
        )
        for family in families
        for cohort in cohort_names
    )
    all_responses_evaluable = len(rows) == len(expected_keys) and all(
        row["evaluable"] for row in rows
    )
    evaluation_complete = (
        structurally_complete
        and execution_receipts_clean
        and provider_clean
        and evaluator_clean
        and cohort_observable
    )
    immutable_inputs_bound = bool(
        scheduled is not None
        and scheduled.get("input_binding_schema_version")
        == campaign_runner.INPUT_BINDING_SCHEMA_V2
        and scheduled.get("execution_complete")
    )
    ranking_eligible = (
        evaluation_complete and all_responses_evaluable and immutable_inputs_bound
    )
    invalid_reasons: list[str] = []
    if not structurally_complete:
        invalid_reasons.append("incomplete-or-missing-artifacts")
    if not scheduled_execution_complete:
        invalid_reasons.append("scheduled-execution-incomplete")
    if not execution_receipts_clean:
        invalid_reasons.append("non-completed-harbor-receipts")
    if not provider_clean:
        invalid_reasons.append("provider-failures")
    if not evaluator_clean:
        invalid_reasons.append("evaluator-failures")
    if not cohort_observable:
        invalid_reasons.append("unobservable-family-cohorts")
    if not all_responses_evaluable:
        invalid_reasons.append("not-all-trials-produced-evaluable-responses")
    if not immutable_inputs_bound:
        invalid_reasons.append("no-complete-immutable-v2-input-contract")

    ranking: list[str] = []
    mechanical_leaders: list[str] = []
    winner: str | None = None
    if ranking_eligible:
        ranking, mechanical_leaders, winner = mechanical_ranking(by_family)
    records_hashes = sorted(
        {str(receipt.get("records_sha256")) for receipt in receipts if receipt.get("records_sha256")}
    )
    report = {
        "schema_version": "semantic-okf-consult-campaign-summary/2.0",
        "campaign": campaign.name,
        "dataset_id": dataset_id,
        "mode": "consult-only",
        "model": EXPECTED_MODEL,
        "pi_version": EXPECTED_PI_VERSION,
        "thinking": "high",
        "attempts": 1,
        "families": families,
        "cohorts": {name: cohorts[name] for name in cohort_names},
        "expected_trials": len(expected_keys),
        "result_trials": len(rows),
        "evaluable_trials": sum(bool(row["evaluable"]) for row in rows),
        "structurally_complete": structurally_complete,
        "provider_clean": provider_clean,
        "evaluator_clean": evaluator_clean,
        "execution_receipts_clean": execution_receipts_clean,
        "cohort_observable": cohort_observable,
        "evaluation_complete": evaluation_complete,
        "ranking_eligible": ranking_eligible,
        "immutable_inputs_bound": immutable_inputs_bound,
        "invalid_reasons": invalid_reasons,
        "missing_trials": [f"{family}/{question}" for family, question in missing_keys],
        "incomplete_run_identities": incomplete_run_identities,
        "records_sha256_values": records_hashes,
        "scheduled_execution": scheduled is not None,
        "scheduled_execution_complete": scheduled_execution_complete,
        "schedule_sha256": scheduled["schedule_sha256"] if scheduled is not None else None,
        "input_bindings_sha256": (
            scheduled["input_bindings_sha256"] if scheduled is not None else None
        ),
        "input_binding_schema_version": (
            scheduled["input_binding_schema_version"]
            if scheduled is not None
            else None
        ),
        "campaign_checkpoint_status": (
            scheduled["checkpoint"].get("status")
            if scheduled is not None and scheduled["checkpoint"] is not None
            else None
        ),
        "input_bindings": (
            {
                family: {
                    **task_manifests[family],
                    "consult_skill_tree_sha256_values": sorted(skill_hashes[family]),
                }
                for family in families
            }
            if scheduled is not None
            else None
        ),
        "scoring_source": "corrected-rescore" if rescore else "historical-verifier",
        "grader_tree_sha256": data.tree_digest(GRADER) if rescore else None,
        "auditor_provenance": {
            "report_summarizer_sha256": data.sha256_file(Path(__file__).resolve()),
            "report_grader_tree_sha256": data.tree_digest(GRADER),
            "execution_auditor": (
                scheduled["input_bindings"].get("auditor")
                if scheduled is not None
                and isinstance(scheduled.get("input_bindings"), Mapping)
                else None
            ),
        },
        "semantic_correctness": "manual-review-required",
        "ranking": ranking,
        "mechanical_leaders": mechanical_leaders,
        "winner": winner,
        "by_family": by_family,
        "trials": sorted(rows, key=lambda row: (row["family"], row["question_id"])),
    }
    if not allow_partial and not structurally_complete:
        raise SummaryError(
            f"campaign is incomplete: {len(missing_keys)} missing trial results and "
            f"{len(incomplete_run_identities)} incomplete run identities"
        )
    if not allow_partial and not allow_invalid and not ranking_eligible:
        raise SummaryError(
            "campaign is not ranking-eligible: " + ", ".join(invalid_reasons)
        )
    return report


def number(value: object, digits: int = 3) -> str:
    """Format one optional report number."""

    return "—" if value is None else f"{float(value):.{digits}f}"


def gate_count(row: Mapping[str, Any], metric: str) -> str:
    """Format passes over the evaluable metric denominator."""

    values = row["metrics"][metric]
    mean = values["mean"]
    observed = values["observed"]
    return f"{round((mean or 0.0) * observed)}/{observed}"


def markdown(summary: Mapping[str, Any]) -> str:
    """Render a comparison only when eligible, otherwise a forensic audit table."""

    valid = bool(summary["ranking_eligible"])
    state = "VALID FOR MECHANICAL RANKING" if valid else "INVALID FOR COMPARISON"
    lines = [
        "# Semantic OKF papers consultation campaign audit",
        "",
        f"> **{state}.** "
        + (
            "Every expected trial produced an evaluable final response."
            if valid
            else "No winner or family ordering may be inferred from this campaign."
        ),
        "",
        f"- Dataset: `{summary['dataset_id']}`",
        f"- Mode: `{summary['mode']}`",
        f"- Runtime: Pi `{summary['pi_version']}` with `{summary['model']}` (`{summary['thinking']}` thinking)",
        f"- Structural artifacts complete: `{str(summary['structurally_complete']).lower()}`",
        f"- Evaluable final responses: {summary['evaluable_trials']}/{summary['expected_trials']}",
        f"- Evaluation complete: `{str(summary['evaluation_complete']).lower()}`",
        f"- Ranking eligible: `{str(summary['ranking_eligible']).lower()}`",
        f"- Invalid reasons: {', '.join(summary['invalid_reasons']) if summary['invalid_reasons'] else 'none'}",
        "- Semantic correctness: requires a separate blinded/manual review; deterministic anchor coverage is not entailment.",
        "",
        "| Family | Results | Evaluable | Quota | Context | Output limit | Interrupted | Contract gate | Min-doc gate | Observed reward |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    family_items = list(summary["by_family"].items())
    if valid:
        order = {family: index for index, family in enumerate(summary["ranking"])}
        family_items.sort(key=lambda item: order[item[0]])
    else:
        family_items.sort(key=lambda item: item[0])
    for family, row in family_items:
        outcomes = row["agent_outcomes"]
        lines.append(
            "| "
            + " | ".join(
                [
                    family,
                    f"{row['result_trials']}/{row['expected_trials']}",
                    str(row["evaluable_trials"]),
                    str(outcomes.get("provider-quota", 0)),
                    str(outcomes.get("provider-context-limit", 0)),
                    str(outcomes.get("output-limit", 0)),
                    str(outcomes.get("agent-interrupted", 0)),
                    gate_count(row, "evidence_contract_gate"),
                    gate_count(row, "minimum_document_gate"),
                    number(row["metrics"]["reward"]["mean"]),
                ]
            )
            + " |"
        )
    lines.extend(["", "## Cohort observability", ""])
    cohort_names = list(summary["cohorts"])
    lines.append("| Family | " + " | ".join(cohort_names) + " |")
    lines.append("|---|" + "|".join("---:" for _ in cohort_names) + "|")
    for family, row in family_items:
        cells = [
            f"{row['cohorts'][cohort]['evaluable_trials']}/{row['cohorts'][cohort]['expected_trials']} evaluable"
            for cohort in cohort_names
        ]
        lines.append(f"| {family} | " + " | ".join(cells) + " |")
    if valid:
        leader_text = (
            f"The mechanically ranked leader is `{summary['winner']}`."
            if summary["winner"] is not None
            else "The top mechanical score is tied among "
            + ", ".join(f"`{family}`" for family in summary["mechanical_leaders"])
            + "."
        )
        lines.extend(
            [
                "",
                "## Mechanical ranking",
                "",
                leader_text + " This does not establish semantic correctness.",
            ]
        )
    lines.extend(
        [
            "",
            "Metrics above use only complete, scorer-observable final responses. Provider and execution failures are not converted into semantic zeroes. Contract, retrieval, minimum-document, and exact-anchor checks remain distinct from semantic review.",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse campaign audit and report arguments."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("campaign", type=Path)
    parser.add_argument("--dataset", default="graphrag-papers-40", choices=data.available_datasets())
    parser.add_argument("--allow-partial", action="store_true")
    parser.add_argument("--allow-invalid", action="store_true")
    parser.add_argument("--rescore", action="store_true")
    parser.add_argument("--tasks-root", type=Path)
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    """Generate checked JSON and Markdown campaign audit reports."""

    args = parse_args(argv)
    report = summarize(
        args.campaign.resolve(),
        args.dataset,
        allow_partial=args.allow_partial,
        allow_invalid=args.allow_invalid,
        rescore=args.rescore,
        tasks_root=args.tasks_root,
    )
    rendered_json = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    rendered_markdown = markdown(report)
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(rendered_json, encoding="utf-8", newline="\n")
    else:
        print(rendered_json, end="")
    if args.markdown_output:
        args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
        args.markdown_output.write_text(rendered_markdown, encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SummaryError as exc:
        raise SystemExit(str(exc)) from exc
