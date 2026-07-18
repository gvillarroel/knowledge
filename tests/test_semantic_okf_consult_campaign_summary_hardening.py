"""Adversarial tests for scheduled Semantic OKF campaign audit bindings."""

from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
EVALUATION_ROOT = REPO / "evaluations" / "semantic-okf-datasets"
GRADER_ROOT = REPO / "evaluations" / "semantic-okf-harbor" / "grader"
sys.path.insert(0, str(EVALUATION_ROOT))
sys.path.insert(0, str(GRADER_ROOT))

import dataset_tool as DATA  # noqa: E402
import run_consult_campaign as CAMPAIGN  # noqa: E402
import summarize_consult_campaign as SUMMARY  # noqa: E402


def write_json(path: Path, value: object) -> None:
    """Write one deterministic JSON fixture."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def response_event() -> dict[str, object]:
    """Return one complete Pi assistant event."""

    return {
        "type": "message_end",
        "message": {
            "role": "assistant",
            "content": [{"type": "text", "text": "{}"}],
            "stopReason": "stop",
        },
    }


def write_trace(path: Path) -> None:
    """Write one compact JSONL Pi event."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(response_event()) + "\n", encoding="utf-8")


def complete_rewards(value: float = 1.0) -> dict[str, float]:
    """Return a complete current-grader metric vector."""

    return {metric: value for metric in SUMMARY.METRICS}


def test_validate_scheduled_receipt_v2_binds_explicit_runtime_image_id(
    tmp_path: Path,
) -> None:
    campaign = tmp_path / "campaign"
    run = campaign / "runs/0001-q001-adaptive"
    frozen_inputs = campaign / "frozen-inputs.json"
    write_json(frozen_inputs, {"schema_version": "fixture/1.0"})

    family = "adaptive"
    task_manifest = {
        "manifest_sha256": "1" * 64,
        "tasks_tree_sha256": "2" * 64,
        "reference_bundle_tree_sha256": "3" * 64,
        "reference_records_sha256": "4" * 64,
        "runtime_image": "semantic-okf-harbor-runtime:2.0",
    }
    skill_hash = "5" * 64
    input_binding = {
        "consult_skill": family,
        "consult_skill_tree_sha256": skill_hash,
        "generated_tasks_tree_sha256": task_manifest["tasks_tree_sha256"],
        "reference_bundle_tree_sha256": task_manifest[
            "reference_bundle_tree_sha256"
        ],
        "reference_records_sha256": task_manifest["reference_records_sha256"],
        "runtime_image": task_manifest["runtime_image"],
        "task_manifest_sha256": task_manifest["manifest_sha256"],
        "offline_model_snapshot": None,
    }
    bound_runtime_image_id = "sha256:" + "a" * 64
    input_bindings_sha256 = "6" * 64
    receipt = {
        "schema_version": "semantic-okf-evaluation-harbor-run/3.0",
        "dataset_id": "graphrag-papers-40",
        "family": family,
        "cohort": "discovery",
        "task_ids": ["q001"],
        "generated_tasks_manifest_sha256": task_manifest["manifest_sha256"],
        "resource_tree_sha256": task_manifest["reference_bundle_tree_sha256"],
        "records_sha256": task_manifest["reference_records_sha256"],
        "installed_skills": [
            {
                "path": str(campaign / "frozen/repo/skills" / family),
                "tree_sha256": skill_hash,
            }
        ],
        "campaign_input_bindings_sha256": input_bindings_sha256,
        "frozen_inputs_manifest_sha256": DATA.sha256_file(frozen_inputs),
        "runtime_image": task_manifest["runtime_image"],
        "runtime_image_id": bound_runtime_image_id,
        "authentication_continuity": "binding-scoped-shared-session",
        "harbor_exit_code": 0,
        "provider_failure_detected": False,
        "run_finished_at": "2026-07-18T00:00:01+00:00",
        "run_started_at": "2026-07-18T00:00:00+00:00",
        "run_status": "completed",
        "terminal_outcomes": {"answer-emitted": 1},
    }
    redacted_config = run / "job-config.redacted.json"
    submitted, effective = SUMMARY._expected_frozen_job_configs(
        run,
        receipt,
        expected_skill=family,
        input_binding=input_binding,
    )
    write_json(redacted_config, submitted)
    actual = json.loads(json.dumps(effective))
    actual["environment"]["mounts"][1]["source"] = (
        "/tmp/semantic-okf-evaluation-auth-sessions/" + input_bindings_sha256
    )
    write_json(run / "config.json", actual)
    receipt["job_config_redacted_sha256"] = DATA.sha256_file(redacted_config)

    assert (
        SUMMARY.validate_scheduled_receipt(
            run,
            receipt,
            expected_skill=family,
            task_manifest=task_manifest,
            input_binding=input_binding,
            input_bindings_sha256=input_bindings_sha256,
            runtime_image_id=bound_runtime_image_id,
        )
        == skill_hash
    )

    receipt["runtime_image_id"] = "sha256:" + "b" * 64
    with pytest.raises(SUMMARY.SummaryError, match="frozen execution receipt drift"):
        SUMMARY.validate_scheduled_receipt(
            run,
            receipt,
            expected_skill=family,
            task_manifest=task_manifest,
            input_binding=input_binding,
            input_bindings_sha256=input_bindings_sha256,
            runtime_image_id=bound_runtime_image_id,
        )

    receipt["runtime_image_id"] = bound_runtime_image_id
    mutations = []
    host_environment = json.loads(json.dumps(actual))
    host_environment["environment"]["type"] = "host"
    mutations.append(host_environment)
    wrong_mount = json.loads(json.dumps(actual))
    wrong_mount["environment"]["mounts"][0]["source"] = "/dataset"
    mutations.append(wrong_mount)
    wrong_skill = json.loads(json.dumps(actual))
    wrong_skill["agents"][0]["skills"] = ["/tmp/wrong-skill"]
    mutations.append(wrong_skill)
    wrong_tasks = json.loads(json.dumps(actual))
    wrong_tasks["datasets"][0]["path"] = "/tmp/wrong-tasks"
    mutations.append(wrong_tasks)
    arbitrary_auth = json.loads(json.dumps(actual))
    arbitrary_auth["environment"]["mounts"][1]["source"] = (
        "/arbitrary/semantic-okf-dataset-harbor-auth-evil"
    )
    mutations.append(arbitrary_auth)
    for mutation in mutations:
        write_json(run / "config.json", mutation)
        with pytest.raises(
            SUMMARY.SummaryError,
            match="effective (?:frozen job config drift|auth mount source is invalid)",
        ):
            SUMMARY.validate_scheduled_receipt(
                run,
                receipt,
                expected_skill=family,
                task_manifest=task_manifest,
                input_binding=input_binding,
                input_bindings_sha256=input_bindings_sha256,
                runtime_image_id=bound_runtime_image_id,
            )
    write_json(run / "config.json", actual)


def test_v3_execution_receipt_requires_consistent_live_completion_metadata(
    tmp_path: Path,
) -> None:
    run = tmp_path / "runs/0001-q001-adaptive"
    receipt = {
        "harbor_exit_code": 0,
        "provider_failure_detected": False,
        "run_finished_at": "2026-07-18T00:00:01+00:00",
        "run_started_at": "2026-07-18T00:00:00+00:00",
        "run_status": "completed",
        "terminal_outcomes": {"answer-emitted": 1},
    }
    assert SUMMARY._validate_v3_execution_receipt(run, receipt) is True
    SUMMARY._validate_v3_outcome_exit(run, {"run_exit_code": 0}, receipt)
    for invalid in ({}, {"run_exit_code": 7}, {"run_exit_code": True}):
        with pytest.raises(SUMMARY.SummaryError, match="outcome exit code"):
            SUMMARY._validate_v3_outcome_exit(run, invalid, receipt)

    runner_failure = {**receipt, "harbor_exit_code": 7, "run_status": "runner-failure"}
    assert SUMMARY._validate_v3_execution_receipt(run, runner_failure) is False
    SUMMARY._validate_v3_outcome_exit(
        run, {"run_exit_code": 7}, runner_failure
    )
    signaled = {**receipt, "harbor_exit_code": -9, "run_status": "runner-failure"}
    assert SUMMARY._validate_v3_execution_receipt(run, signaled) is False
    SUMMARY._validate_v3_outcome_exit(run, {"run_exit_code": 137}, signaled)

    provider_failure = {
        **receipt,
        "provider_failure_detected": True,
        "run_status": "provider-failure",
        "terminal_outcomes": {"provider-quota": 1},
    }
    assert SUMMARY._validate_v3_execution_receipt(run, provider_failure) is False
    SUMMARY._validate_v3_outcome_exit(
        run, {"run_exit_code": 2}, provider_failure
    )

    for drift in (
        {"run_status": "runner-failure"},
        {"provider_failure_detected": True},
        {"run_finished_at": "2026-07-17T23:59:59+00:00"},
        {"terminal_outcomes": {"answer-emitted": 2}},
    ):
        with pytest.raises(SUMMARY.SummaryError, match="live receipt"):
            SUMMARY._validate_v3_execution_receipt(run, {**receipt, **drift})


def test_v3_scheduled_completion_is_audited_without_a_result_file(
    tmp_path: Path, monkeypatch
) -> None:
    run = tmp_path / "runs/0001-q001-adaptive"
    write_trace(run / "q001__fixture/artifacts/pi.jsonl")
    receipt = {
        "schema_version": "semantic-okf-evaluation-harbor-run/3.0",
        "harbor_exit_code": 0,
        "terminal_outcomes": {"answer-emitted": 1},
    }
    outcome = {
        "error_code": None,
        "failure_domain": None,
        "outcome": "answer-emitted",
        "parsed_events": 1,
        "question_id": "q001",
        "run_exit_code": 0,
        "stop_reason": "stop",
        "trace_path": "q001__fixture/artifacts/pi.jsonl",
    }

    SUMMARY._validate_v3_scheduled_completion(run, outcome, receipt)
    assert not list(run.rglob("result.json"))

    with pytest.raises(SUMMARY.SummaryError, match="terminal outcomes"):
        SUMMARY._validate_v3_scheduled_completion(
            run,
            outcome,
            {**receipt, "terminal_outcomes": {"provider-error": 1}},
        )
    with pytest.raises(SUMMARY.SummaryError, match="outcome exit code"):
        SUMMARY._validate_v3_scheduled_completion(
            run, {**outcome, "run_exit_code": 7}, receipt
        )
    with pytest.raises(SUMMARY.SummaryError, match="terminal trace"):
        SUMMARY._validate_v3_scheduled_completion(
            run, {**outcome, "outcome": "provider-error"}, receipt
        )
    with pytest.raises(SUMMARY.SummaryError, match="terminal trace"):
        SUMMARY._validate_v3_scheduled_completion(
            run, {**outcome, "parsed_events": 999}, receipt
        )
    with pytest.raises(SUMMARY.SummaryError, match="omitted its nonzero runner wrapper"):
        SUMMARY._validate_v3_scheduled_completion(
            run,
            {**outcome, "run_exit_code": 7},
            {**receipt, "harbor_exit_code": 7},
        )

    monkeypatch.setattr(
        SUMMARY,
        "classify_pi_trace",
        lambda _path: {
            "error_code": "usage_limit_reached",
            "failure_domain": "provider",
            "outcome": "provider-quota",
            "parsed_events": 1,
            "provider_reset": None,
            "stop_reason": "error",
        },
    )
    with pytest.raises(SUMMARY.SummaryError, match="wrapper has an invalid shape"):
        SUMMARY._validate_scheduled_trace_outcome(
            run,
            {
                "error_code": "nonzero_runner_exit",
                "failure_domain": "runner",
                "outcome": "runner-error",
                "parsed_events": 1,
                "question_id": "q001",
                "run_exit_code": 7,
                "stop_reason": "error",
                "trace_path": "q001__fixture/artifacts/pi.jsonl",
                "underlying_trace_error_code": "usage_limit_reached",
                "underlying_trace_failure_domain": "provider",
                "underlying_trace_outcome": "provider-quota",
            },
        )


def test_missing_trace_outcome_accepts_only_its_exact_binding_wrapper(
    tmp_path: Path,
) -> None:
    run = tmp_path / "runs/0001-q001-adaptive"
    run.mkdir(parents=True)
    direct = {
        "error_code": "missing_pi_trace",
        "failure_domain": "runner",
        "outcome": "runner-error",
        "question_id": "q001",
        "run_exit_code": 1,
        "trace_path": None,
    }
    SUMMARY._validate_scheduled_trace_outcome(run, direct)

    wrapped = {
        **direct,
        "binding_error_type": "CampaignRunError",
        "error_code": "input_binding_drift",
        "underlying_trace_error_code": "missing_pi_trace",
        "underlying_trace_failure_domain": "runner",
        "underlying_trace_outcome": "runner-error",
    }
    SUMMARY._validate_scheduled_trace_outcome(run, wrapped)

    with pytest.raises(SUMMARY.SummaryError, match="wrapper has an invalid shape"):
        SUMMARY._validate_scheduled_trace_outcome(
            run,
            {
                **direct,
                "underlying_trace_error_code": "missing_pi_trace",
                "underlying_trace_failure_domain": "runner",
                "underlying_trace_outcome": "runner-error",
            },
        )


def test_mechanical_ranking_reports_an_exact_top_tie_without_a_winner() -> None:
    by_family = {
        "adaptive": {"metrics": {"reward": {"mean": 0.75}}},
        "classical": {"metrics": {"reward": {"mean": 0.75}}},
        "turso": {"metrics": {"reward": {"mean": 0.50}}},
    }

    ranking, leaders, winner = SUMMARY.mechanical_ranking(by_family)

    assert ranking == ["adaptive", "classical", "turso"]
    assert leaders == ["adaptive", "classical"]
    assert winner is None


def test_current_scorer_observability_and_exact_task_identity(tmp_path: Path) -> None:
    run = tmp_path / "campaign/runs/0001-q001-adaptive"
    trial = run / "q001__fixture"
    write_json(
        trial / "result.json",
        {
            "id": "trial",
            "task_name": "knowledge/graphrag-papers-40__consult-only__adaptive__q001",
            "agent_result": {},
        },
    )
    write_trace(trial / "artifacts/pi.jsonl")

    missing = SUMMARY.trial_row(
        run,
        "graphrag-papers-40",
        "adaptive",
        "discovery",
        "q001",
        trial / "result.json",
        require_current_scorer=True,
    )
    assert missing["complete_response_observed"] is True
    assert missing["evaluable"] is False
    assert missing["evaluator_failure"] is True
    assert "metric:reward" in missing["scorer_observability_errors"]

    result = DATA.load_json(trial / "result.json")
    result["verifier_result"] = {"rewards": complete_rewards()}
    write_json(trial / "result.json", result)
    write_json(trial / "verifier/reward.json", complete_rewards())
    write_json(
        trial / "verifier/diagnostics.json",
        {
            "question_id": "q001",
            "schema_version": "semantic-okf-harbor-redacted-diagnostics/2.0",
            "status": "scored-response",
        },
    )
    observed = SUMMARY.trial_row(
        run,
        "graphrag-papers-40",
        "adaptive",
        "discovery",
        "q001",
        trial / "result.json",
        require_current_scorer=True,
    )
    assert observed["evaluable"] is True
    assert observed["scorer_observable"] is True

    write_json(trial / "verifier/reward.json", complete_rewards(0.0))
    mismatched = SUMMARY.trial_row(
        run,
        "graphrag-papers-40",
        "adaptive",
        "discovery",
        "q001",
        trial / "result.json",
        require_current_scorer=True,
    )
    assert mismatched["evaluable"] is False
    assert "verifier-artifact:reward-mismatch" in mismatched[
        "scorer_observability_errors"
    ]
    write_json(trial / "verifier/reward.json", complete_rewards())

    impossible = complete_rewards()
    impossible["mechanical_qualification_gate"] = 0.0
    clean, algebra_errors = SUMMARY.current_scorer_observability(
        impossible, {"status": "scored-response"}
    )
    assert clean is False
    assert "algebra:mechanical-qualification-gate" in algebra_errors
    assert "algebra:reward" in algebra_errors
    wrong_utility = complete_rewards()
    wrong_utility["mechanical_utility"] = 0.5
    wrong_utility["reward"] = 0.5
    clean, utility_errors = SUMMARY.current_scorer_observability(
        wrong_utility,
        {"status": "scored-response"},
        has_ground_truth=False,
    )
    assert clean is False
    assert "algebra:mechanical-utility" in utility_errors
    clean, status_errors = SUMMARY.current_scorer_observability(
        complete_rewards(), {"status": "agent-invalid-response"}
    )
    assert clean is False
    assert "algebra:status-response-contract" in status_errors

    result["verifier_result"]["rewards"]["reward"] = float("nan")
    write_json(trial / "result.json", result)
    nonfinite = SUMMARY.trial_row(
        run,
        "graphrag-papers-40",
        "adaptive",
        "discovery",
        "q001",
        trial / "result.json",
        require_current_scorer=True,
    )
    assert nonfinite["evaluable"] is False
    assert "metric:reward" in nonfinite["scorer_observability_errors"]

    result["task_name"] = "knowledge/wrong__consult-only__wrong__q001"
    write_json(trial / "result.json", result)
    with pytest.raises(SUMMARY.SummaryError, match="task name"):
        SUMMARY.trial_row(
            run,
            "graphrag-papers-40",
            "adaptive",
            "discovery",
            "q001",
            trial / "result.json",
            require_current_scorer=True,
        )


def build_complete_scheduled_campaign(root: Path) -> tuple[Path, dict[str, object]]:
    """Build a complete synthetic scheduled campaign around the real task manifests."""

    campaign = root / "campaign"
    schedule = CAMPAIGN.build_schedule()
    schedule_digest = CAMPAIGN.persist_schedule(campaign, schedule)
    family_metadata = DATA.load_families()
    family_bindings: dict[str, dict[str, str]] = {}
    runtime_images: set[str] = set()
    for index, family in enumerate(schedule["families"], 1):
        manifest_path = (
            EVALUATION_ROOT
            / "generated/tasks/graphrag-papers-40/consult-only"
            / family
            / "manifest.json"
        )
        manifest = DATA.load_json(manifest_path)
        runtime_images.add(str(manifest["runtime_image"]))
        family_bindings[family] = {
            "consult_skill": family_metadata[family]["consult_skill"],
            "consult_skill_tree_sha256": f"{index:x}" * 64,
            "generated_tasks_tree_sha256": DATA.tree_digest(manifest_path.parent),
            "reference_bundle_tree_sha256": manifest[
                "reference_bundle_tree_sha256"
            ],
            "reference_records_sha256": manifest["reference_records_sha256"],
            "runtime_image": manifest["runtime_image"],
            "task_manifest_sha256": DATA.sha256_file(manifest_path),
        }
    assert len(runtime_images) == 1
    input_bindings = {
        "schema_version": "semantic-okf-consult-campaign-input-bindings/1.0",
        "dataset_id": "graphrag-papers-40",
        "mode": "consult-only",
        "schedule_sha256": schedule_digest,
        "model": SUMMARY.EXPECTED_MODEL,
        "pi_version": SUMMARY.EXPECTED_PI_VERSION,
        "thinking": "high",
        "runtime_image": next(iter(runtime_images)),
        **CAMPAIGN.runtime_build_binding(next(iter(runtime_images))),
        "grader_tree_sha256": DATA.tree_digest(GRADER_ROOT),
        "families_registry_sha256": DATA.sha256_file(DATA.FAMILIES_PATH),
        "families": family_bindings,
    }
    binding_payload = CAMPAIGN.canonical_json_bytes(input_bindings)
    binding_digest = hashlib.sha256(binding_payload).hexdigest()
    (campaign / "input-bindings.json").write_bytes(binding_payload)
    (campaign / "input-bindings.sha256").write_text(
        f"{binding_digest}  input-bindings.json\n", encoding="ascii"
    )

    outcome_counts: Counter[str] = Counter()
    for cell in schedule["cells"]:
        family = str(cell["family"])
        question_id = str(cell["question_id"])
        run = campaign / str(cell["shard_path"])
        trial = run / f"{question_id}__fixture"
        skill = family_metadata[family]["consult_skill"]
        write_json(
            run / "config.json",
            {
                "agents": [
                    {
                        "name": "pi",
                        "model_name": SUMMARY.EXPECTED_MODEL,
                        "skills": [str(REPO / "skills" / skill)],
                        "kwargs": {
                            "version": SUMMARY.EXPECTED_PI_VERSION,
                            "thinking": "high",
                        },
                    }
                ],
                "datasets": [{"task_names": [question_id]}],
            },
        )
        binding = family_bindings[family]
        write_json(
            run / "run-receipt.json",
            {
                "schema_version": "semantic-okf-evaluation-harbor-run/2.0",
                "dataset_id": "graphrag-papers-40",
                "family": family,
                "mode": "consult-only",
                "cohort": cell["cohort"],
                "task_ids": [question_id],
                "attempts": 1,
                "model": SUMMARY.EXPECTED_MODEL,
                "pi_version": SUMMARY.EXPECTED_PI_VERSION,
                "public_mount_target": "/knowledge",
                "prebuilt_knowledge_mounted": True,
                "raw_sources_mounted": False,
                "installed_skills": [
                    {
                        "path": str(REPO / "skills" / skill),
                        "tree_sha256": binding["consult_skill_tree_sha256"],
                    }
                ],
                "resource_kind": "processed-knowledge",
                "resource_tree_sha256": binding[
                    "reference_bundle_tree_sha256"
                ],
                "records_sha256": binding["reference_records_sha256"],
                "generated_tasks_manifest_sha256": binding[
                    "task_manifest_sha256"
                ],
                "terminal_outcomes": {"answer-emitted": 1},
            },
        )
        write_json(
            trial / "result.json",
            {
                "id": f"{family}-{question_id}",
                "task_name": (
                    "knowledge/graphrag-papers-40__consult-only__"
                    f"{family}__{question_id}"
                ),
                "agent_result": {},
                "verifier_result": {"rewards": complete_rewards()},
            },
        )
        write_json(trial / "verifier/reward.json", complete_rewards())
        write_json(
            trial / "verifier/diagnostics.json",
            {
                "question_id": question_id,
                "schema_version": "semantic-okf-harbor-redacted-diagnostics/2.0",
                "status": "scored-response",
            },
        )
        write_trace(trial / "artifacts/pi.jsonl")
        trace_path = f"{question_id}__fixture/artifacts/pi.jsonl"
        outcome = {
            "schema_version": "semantic-okf-consult-campaign-outcome/1.0",
            "sequence": cell["sequence"],
            "family": family,
            "cohort": cell["cohort"],
            "question_id": question_id,
            "outcome": "answer-emitted",
            "failure_domain": None,
            "error_code": None,
            "trace_path": trace_path,
            "parsed_events": 1,
            "stop_reason": "stop",
        }
        write_json(campaign / f"outcomes/{int(cell['sequence']):04d}.json", outcome)
        outcome_counts["answer-emitted"] += 1
    checkpoint = {
        "schema_version": "semantic-okf-consult-campaign-checkpoint/1.0",
        "status": "completed",
        "schedule_sha256": schedule_digest,
        "input_bindings_sha256": binding_digest,
        "completed_cell_count": 320,
        "recorded_at": "2026-07-18T00:00:00+00:00",
        "terminal_outcomes": dict(outcome_counts),
    }
    write_json(campaign / "checkpoints/completed.json", checkpoint)
    return campaign, schedule


def test_scheduled_summary_rejects_every_binding_and_observability_drift(
    tmp_path: Path,
) -> None:
    campaign, schedule = build_complete_scheduled_campaign(tmp_path)
    report = SUMMARY.summarize(
        campaign,
        "graphrag-papers-40",
        allow_partial=True,
        allow_invalid=True,
    )
    assert report["structurally_complete"] is False
    assert report["scheduled_execution_complete"] is False
    assert report["ranking_eligible"] is False
    assert report["input_binding_schema_version"] == CAMPAIGN.INPUT_BINDING_SCHEMA_V1
    assert report["evaluable_trials"] == 320

    checkpoint_path = campaign / "checkpoints/completed.json"
    original_checkpoint = checkpoint_path.read_bytes()
    malformed_checkpoint = DATA.load_json(checkpoint_path)
    malformed_checkpoint["recorded_at"] = "2026-07-18T00:00:00"
    malformed_checkpoint["unexpected"] = True
    write_json(checkpoint_path, malformed_checkpoint)
    with pytest.raises(SUMMARY.SummaryError, match="checkpoint drift"):
        SUMMARY.summarize(campaign, "graphrag-papers-40")
    checkpoint_path.write_bytes(original_checkpoint)

    conflicting_checkpoint = campaign / "checkpoints/aborted.json"
    conflicting_checkpoint.mkdir()
    with pytest.raises(SUMMARY.SummaryError, match="invalid checkpoint artifact"):
        SUMMARY.summarize(campaign, "graphrag-papers-40")
    conflicting_checkpoint.rmdir()

    schedule_path = campaign / "schedule.json"
    schedule_sidecar = campaign / "schedule.sha256"
    persisted_schedule = schedule_path.read_bytes()
    persisted_sidecar = schedule_sidecar.read_bytes()
    schedule_path.unlink()
    schedule_sidecar.unlink()
    unscheduled = SUMMARY.summarize(
        campaign,
        "graphrag-papers-40",
        allow_partial=True,
        allow_invalid=True,
    )
    assert unscheduled["ranking_eligible"] is False
    assert unscheduled["winner"] is None
    assert "no-complete-immutable-v2-input-contract" in unscheduled["invalid_reasons"]
    schedule_path.write_bytes(persisted_schedule)
    schedule_sidecar.write_bytes(persisted_sidecar)

    unexpected = campaign / "runs/off-schedule"
    unexpected.mkdir()
    with pytest.raises(SUMMARY.SummaryError, match="off-schedule run"):
        SUMMARY.summarize(campaign, "graphrag-papers-40")
    unexpected.rmdir()

    second = schedule["cells"][8]
    run = campaign / str(second["shard_path"])
    receipt_path = run / "run-receipt.json"
    receipt = DATA.load_json(receipt_path)
    original_receipt = json.loads(json.dumps(receipt))
    receipt["installed_skills"][0]["tree_sha256"] = "0" * 64
    write_json(receipt_path, receipt)
    with pytest.raises(SUMMARY.SummaryError, match="input bindings"):
        SUMMARY.summarize(campaign, "graphrag-papers-40")
    write_json(receipt_path, original_receipt)

    first = schedule["cells"][0]
    first_run = campaign / str(first["shard_path"])
    result_path = first_run / "q001__fixture/result.json"
    result = DATA.load_json(result_path)
    original_result = json.loads(json.dumps(result))
    result["verifier_result"] = {}
    write_json(result_path, result)
    invalid = SUMMARY.summarize(
        campaign,
        "graphrag-papers-40",
        allow_partial=True,
        allow_invalid=True,
    )
    assert invalid["evaluator_clean"] is False
    assert invalid["ranking_eligible"] is False
    assert invalid["evaluable_trials"] == 319
    write_json(result_path, original_result)

    result["task_name"] = "knowledge/wrong__consult-only__adaptive__q001"
    write_json(result_path, result)
    with pytest.raises(SUMMARY.SummaryError, match="task name"):
        SUMMARY.summarize(campaign, "graphrag-papers-40")
    write_json(result_path, original_result)

    outcome_path = campaign / "outcomes/0001.json"
    outcome = DATA.load_json(outcome_path)
    original_outcome = json.loads(json.dumps(outcome))
    outcome["outcome"] = "provider-quota"
    write_json(outcome_path, outcome)
    checkpoint_path = campaign / "checkpoints/completed.json"
    checkpoint = DATA.load_json(checkpoint_path)
    checkpoint["terminal_outcomes"] = {
        "answer-emitted": 319,
        "provider-quota": 1,
    }
    write_json(checkpoint_path, checkpoint)
    with pytest.raises(SUMMARY.SummaryError, match="contains aborting outcomes"):
        SUMMARY.summarize(campaign, "graphrag-papers-40")
    write_json(outcome_path, original_outcome)

    checkpoint["terminal_outcomes"] = {"answer-emitted": 320}
    checkpoint["completed_cell_count"] = 319
    write_json(checkpoint_path, checkpoint)
    with pytest.raises(SUMMARY.SummaryError, match="checkpoint drift"):
        SUMMARY.summarize(campaign, "graphrag-papers-40")


def test_forensic_summary_accepts_a_trace_wrapped_by_post_call_binding_drift(
    tmp_path: Path,
) -> None:
    campaign, _schedule = build_complete_scheduled_campaign(tmp_path)
    outcome_path = campaign / "outcomes/0001.json"
    outcome = DATA.load_json(outcome_path)
    outcome.update(
        {
            "binding_error_type": "CampaignRunError",
            "error_code": "input_binding_drift",
            "failure_domain": "runner",
            "outcome": "runner-error",
            "run_exit_code": 0,
            "underlying_trace_error_code": None,
            "underlying_trace_failure_domain": None,
            "underlying_trace_outcome": "answer-emitted",
        }
    )
    write_json(outcome_path, outcome)

    completed_path = campaign / "checkpoints/completed.json"
    completed = DATA.load_json(completed_path)
    completed["terminal_outcomes"] = {
        "answer-emitted": 319,
        "runner-error": 1,
    }
    write_json(completed_path, completed)
    with pytest.raises(SUMMARY.SummaryError, match="contains aborting outcomes"):
        SUMMARY.summarize(
            campaign,
            "graphrag-papers-40",
            allow_partial=True,
            allow_invalid=True,
        )

    completed_path.unlink()
    completed.update(
        {
            "status": "aborted",
            "terminal_outcomes": {
                "answer-emitted": 319,
                "runner-error": 1,
            },
            "trigger": CAMPAIGN.checkpoint_trigger(outcome),
        }
    )
    write_json(campaign / "checkpoints/aborted.json", completed)

    report = SUMMARY.summarize(
        campaign,
        "graphrag-papers-40",
        allow_partial=True,
        allow_invalid=True,
    )
    assert report["scheduled_execution_complete"] is False
    assert report["ranking_eligible"] is False
    assert report["evaluable_trials"] == 320

    aborted_path = campaign / "checkpoints/aborted.json"
    aborted = DATA.load_json(aborted_path)
    outcome.pop("binding_error_type")
    write_json(outcome_path, outcome)
    aborted["trigger"] = CAMPAIGN.checkpoint_trigger(outcome)
    write_json(aborted_path, aborted)
    with pytest.raises(SUMMARY.SummaryError, match="wrapper has an invalid shape"):
        SUMMARY.summarize(
            campaign,
            "graphrag-papers-40",
            allow_partial=True,
            allow_invalid=True,
        )

    outcome["error_code"] = "nonzero_runner_exit"
    outcome["run_exit_code"] = 0
    write_json(outcome_path, outcome)
    aborted["trigger"] = CAMPAIGN.checkpoint_trigger(outcome)
    write_json(aborted_path, aborted)
    with pytest.raises(SUMMARY.SummaryError, match="wrapper has an invalid shape"):
        SUMMARY.summarize(
            campaign,
            "graphrag-papers-40",
            allow_partial=True,
            allow_invalid=True,
        )

    outcome["run_exit_code"] = 7
    write_json(outcome_path, outcome)
    SUMMARY.summarize(
        campaign,
        "graphrag-papers-40",
        allow_partial=True,
        allow_invalid=True,
    )

    outcome["underlying_trace_outcome"] = "provider-error"
    write_json(outcome_path, outcome)
    with pytest.raises(SUMMARY.SummaryError, match="terminal trace"):
        SUMMARY.summarize(
            campaign,
            "graphrag-papers-40",
            allow_partial=True,
            allow_invalid=True,
        )
