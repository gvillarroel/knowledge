"""Tests for the fair append-only Semantic OKF consult campaign runner."""

from __future__ import annotations

import json
import sys
import threading
from collections import Counter
from pathlib import Path
from types import SimpleNamespace

import pytest

EVALUATION_ROOT = (
    Path(__file__).resolve().parents[1] / "evaluations" / "semantic-okf-datasets"
)
sys.path.insert(0, str(EVALUATION_ROOT))

import run_consult_campaign as CAMPAIGN  # noqa: E402


FAMILIES = [
    "adaptive",
    "classical",
    "embeddings",
    "ensemble",
    "entity-graph",
    "graphify",
    "legacy",
    "turso",
]


def cohorts() -> dict[str, list[str]]:
    """Return a deliberately non-sorted complete synthetic cohort mapping."""

    return {
        "hard": [f"q{number:03d}" for number in range(31, 41)],
        "holdout": [f"q{number:03d}" for number in range(25, 31)],
        "discovery": [f"q{number:03d}" for number in range(1, 25)],
    }


def test_schedule_covers_each_question_family_cell_once_in_question_order() -> None:
    schedule = CAMPAIGN.build_schedule(cohorts=cohorts(), families=reversed(FAMILIES))
    cells = schedule["cells"]

    assert len(cells) == 320
    assert [cell["sequence"] for cell in cells] == list(range(1, 321))
    assert [cell["question_id"] for cell in cells] == [
        f"q{number:03d}" for number in range(1, 41) for _ in range(8)
    ]
    assert {
        (cell["question_id"], cell["family"]) for cell in cells
    } == {
        (f"q{number:03d}", family)
        for number in range(1, 41)
        for family in FAMILIES
    }
    assert len({cell["shard_path"] for cell in cells}) == 320


def test_rotated_family_order_balances_positions_and_four_task_waves() -> None:
    cells = CAMPAIGN.build_schedule(cohorts=cohorts(), families=FAMILIES)["cells"]
    position_counts = Counter(
        (cell["family"], cell["family_position"]) for cell in cells
    )
    wave_counts = Counter((cell["family"], cell["question_wave"]) for cell in cells)

    assert all(
        position_counts[(family, position)] == 5
        for family in FAMILIES
        for position in range(1, 9)
    )
    assert all(
        wave_counts[(family, wave)] == 20
        for family in FAMILIES
        for wave in (1, 2)
    )
    assert [cell["family"] for cell in cells[:8]] == FAMILIES
    assert [cell["family"] for cell in cells[8:16]] == FAMILIES[1:] + FAMILIES[:1]


def test_schedule_hash_is_deterministic_and_binds_content() -> None:
    first = CAMPAIGN.build_schedule(cohorts=cohorts(), families=FAMILIES)
    second = CAMPAIGN.build_schedule(
        cohorts=dict(reversed(list(cohorts().items()))), families=reversed(FAMILIES)
    )

    assert first == second
    assert CAMPAIGN.schedule_digest(first) == CAMPAIGN.schedule_digest(second)
    modified = json.loads(json.dumps(first))
    modified["rotation_policy"] = "different"
    assert CAMPAIGN.schedule_digest(modified) != CAMPAIGN.schedule_digest(first)


def test_provider_abort_stops_after_preflight_wave_and_persists_checkpoint(
    tmp_path: Path,
) -> None:
    schedule = CAMPAIGN.build_schedule(cohorts=cohorts(), families=FAMILIES)
    campaign = tmp_path / "campaign"
    CAMPAIGN.persist_schedule(campaign, schedule)
    calls: list[int] = []
    lock = threading.Lock()

    def fake_shard(cell, _campaign, _settings):
        with lock:
            calls.append(cell["sequence"])
        if cell["sequence"] == 2:
            return {
                "error_code": "usage_limit_reached",
                "failure_domain": "provider",
                "outcome": "provider-quota",
            }
        return {
            "error_code": None,
            "failure_domain": None,
            "outcome": "answer-emitted",
        }

    checkpoint = CAMPAIGN.execute_campaign(
        schedule,
        campaign,
        CAMPAIGN.RunSettings(
            auth_file=tmp_path / "unused-auth.json",
            hf_cache=tmp_path / "unused-cache",
            max_concurrency=4,
        ),
        shard_executor=fake_shard,
        binding_verifier=lambda *_args: "a" * 64,
    )

    assert checkpoint["status"] == "aborted"
    assert checkpoint["trigger"]["outcome"] == "provider-quota"
    assert set(calls) == {1, 2, 3, 4}
    assert calls.count(1) == 1
    assert not any(sequence > 4 for sequence in calls)
    assert len(list((campaign / "outcomes").glob("*.json"))) == 4
    persisted = json.loads(
        (campaign / "checkpoints/aborted.json").read_text(encoding="utf-8")
    )
    assert persisted == checkpoint


def test_execute_campaign_rejects_a_forged_completed_checkpoint(
    tmp_path: Path,
) -> None:
    schedule = CAMPAIGN.build_schedule(cohorts=cohorts(), families=FAMILIES)
    campaign = tmp_path / "campaign"
    CAMPAIGN.persist_schedule(campaign, schedule)
    for cell in schedule["cells"]:
        CAMPAIGN._persist_outcome(
            campaign,
            cell,
            {
                "error_code": None,
                "failure_domain": None,
                "outcome": "answer-emitted",
                "run_exit_code": 0,
                "trace_path": "q001__fixture/artifacts/pi.jsonl",
            },
        )
    checkpoint_path = campaign / "checkpoints/completed.json"
    checkpoint_path.parent.mkdir(parents=True)
    checkpoint_path.write_text(
        json.dumps(
            {
                "completed_cell_count": 1,
                "input_bindings_sha256": "1" * 64,
                "recorded_at": "2026-07-18T00:00:00+00:00",
                "schedule_sha256": "0" * 64,
                "schema_version": "wrong",
                "status": "completed",
                "terminal_outcomes": {"runner-error": 999},
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(CAMPAIGN.CampaignRunError, match="existing completed checkpoint"):
        CAMPAIGN.execute_campaign(
            schedule,
            campaign,
            CAMPAIGN.RunSettings(
                auth_file=tmp_path / "unused-auth.json",
                hf_cache=tmp_path / "unused-cache",
            ),
            shard_executor=lambda *_args: pytest.fail("no shard may be submitted"),
            binding_verifier=lambda *_args: "1" * 64,
        )


def test_execute_campaign_rejects_invalid_or_conflicting_abort_checkpoints(
    tmp_path: Path,
) -> None:
    schedule = CAMPAIGN.build_schedule(cohorts=cohorts(), families=FAMILIES)
    campaign = tmp_path / "campaign"
    CAMPAIGN.persist_schedule(campaign, schedule)
    first = schedule["cells"][0]
    CAMPAIGN._persist_outcome(
        campaign,
        first,
        {
            "error_code": "fixture",
            "failure_domain": "runner",
            "outcome": "runner-error",
            "run_exit_code": None,
            "trace_path": None,
        },
    )
    aborted_path = campaign / "checkpoints/aborted.json"
    aborted_path.parent.mkdir(parents=True)
    aborted_path.write_text("{}", encoding="utf-8")
    settings = CAMPAIGN.RunSettings(
        auth_file=tmp_path / "unused-auth.json",
        hf_cache=tmp_path / "unused-cache",
    )

    with pytest.raises(CAMPAIGN.CampaignRunError, match="existing aborted checkpoint"):
        CAMPAIGN.execute_campaign(
            schedule,
            campaign,
            settings,
            shard_executor=lambda *_args: pytest.fail("no shard may be submitted"),
            binding_verifier=lambda *_args: "1" * 64,
        )

    completed_path = campaign / "checkpoints/completed.json"
    completed_path.write_text("{}", encoding="utf-8")
    with pytest.raises(CAMPAIGN.CampaignRunError, match="conflicting terminal checkpoints"):
        CAMPAIGN.execute_campaign(
            schedule,
            campaign,
            settings,
            shard_executor=lambda *_args: pytest.fail("no shard may be submitted"),
            binding_verifier=lambda *_args: "1" * 64,
        )
    assert (campaign / "schedule.sha256").read_text(encoding="ascii").startswith(
        CAMPAIGN.schedule_digest(schedule)
    )


def test_schedule_only_and_dry_run_never_invoke_a_shard(
    tmp_path: Path, monkeypatch
) -> None:
    def forbidden_call(*_args, **_kwargs):
        raise AssertionError("dry modes must not start a subprocess")

    monkeypatch.setattr(CAMPAIGN.subprocess, "run", forbidden_call)
    monkeypatch.setattr(CAMPAIGN, "validate_live_inputs", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(CAMPAIGN, "persist_input_bindings", lambda *_args: "b" * 64)
    monkeypatch.setattr(CAMPAIGN, "verify_input_bindings", lambda *_args, **_kwargs: "b" * 64)

    assert CAMPAIGN.main(
        ["--campaign", str(tmp_path / "schedule-only"), "--schedule-only"]
    ) == 0
    assert CAMPAIGN.main(
        ["--campaign", str(tmp_path / "dry-run"), "--dry-run"]
    ) == 0


def test_input_binding_manifest_is_immutable_and_family_drift_is_rejected(
    tmp_path: Path, monkeypatch
) -> None:
    schedule = CAMPAIGN.build_schedule(cohorts=cohorts(), families=FAMILIES)
    campaign = tmp_path / "campaign"
    CAMPAIGN.persist_schedule(campaign, schedule)

    def binding(family: str, marker: str = "c") -> dict[str, str]:
        return {
            "consult_skill": f"consult-{family}",
            "consult_skill_tree_sha256": marker * 64,
            "generated_tasks_tree_sha256": "2" * 64,
            "reference_bundle_tree_sha256": "d" * 64,
            "reference_records_sha256": "e" * 64,
            "runtime_image": "runtime:1",
            "task_manifest_sha256": "f" * 64,
        }

    current = {family: binding(family) for family in FAMILIES}
    monkeypatch.setattr(
        CAMPAIGN,
        "family_input_binding",
        lambda _schedule, _campaign, family: dict(current[family]),
    )
    monkeypatch.setattr(
        CAMPAIGN,
        "runtime_build_binding",
        lambda _tag: {
            "runtime_build_receipt_sha256": "3" * 64,
            "runtime_image_id": "sha256:" + "4" * 64,
            "runtime_dockerfile_sha256": "5" * 64,
            "runtime_requirements_sha256": "6" * 64,
        },
    )

    digest = CAMPAIGN.persist_input_bindings(schedule, campaign)
    assert len(digest) == 64
    assert CAMPAIGN.verify_input_bindings(schedule, campaign, ["adaptive"]) == digest
    current["adaptive"] = binding("adaptive", "0")
    try:
        CAMPAIGN.verify_input_bindings(schedule, campaign, ["adaptive"])
    except CAMPAIGN.CampaignRunError as exc:
        assert "drift for adaptive" in str(exc)
    else:
        raise AssertionError("a changed family binding must abort before another shard")


def test_family_binding_detects_non_manifest_generated_task_drift(
    tmp_path: Path, monkeypatch
) -> None:
    repo = tmp_path / "repo"
    evaluation_root = repo / "evaluations/semantic-okf-datasets"
    campaign = evaluation_root / "campaign"
    family = "adaptive"
    task_root = (
        evaluation_root
        / "generated/tasks/graphrag-papers-40/consult-only"
        / family
    )
    bundle = campaign / "bundles" / family
    ledger = bundle / "semantic/records.jsonl"
    ledger.parent.mkdir(parents=True)
    ledger.write_text('{"record_id":"r","source_id":"s"}\n', encoding="utf-8")
    instruction = task_root / "discovery/q001/instruction.md"
    instruction.parent.mkdir(parents=True)
    instruction.write_text("original\n", encoding="utf-8")
    manifest = {
        "dataset_id": "graphrag-papers-40",
        "family": family,
        "mode": "consult-only",
        "runtime_image": "runtime:1",
        "reference_bundle_tree_sha256": CAMPAIGN.data.tree_digest(bundle),
        "reference_records_sha256": CAMPAIGN.data.sha256_file(ledger),
    }
    (task_root / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    skill = repo / "skills/consult-semantic-okf-adaptive"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text("---\nname: fixture\n---\n", encoding="utf-8")
    monkeypatch.setattr(CAMPAIGN, "HERE", evaluation_root)
    monkeypatch.setattr(CAMPAIGN, "REPO", repo)

    schedule = {"dataset_id": "graphrag-papers-40"}
    before = CAMPAIGN.family_input_binding(schedule, campaign, family)
    manifest_hash = before["task_manifest_sha256"]
    instruction.write_text("mutated without manifest edit\n", encoding="utf-8")
    after = CAMPAIGN.family_input_binding(schedule, campaign, family)

    assert after["task_manifest_sha256"] == manifest_hash
    assert (
        after["generated_tasks_tree_sha256"]
        != before["generated_tasks_tree_sha256"]
    )


def test_runtime_build_receipt_and_live_docker_image_are_bound(monkeypatch) -> None:
    binding = CAMPAIGN.runtime_build_binding("semantic-okf-harbor-runtime:1.0")
    assert binding["runtime_build_receipt_sha256"]
    assert binding["runtime_image_id"].startswith("sha256:")

    monkeypatch.setattr(
        CAMPAIGN.subprocess,
        "run",
        lambda *_args, **_kwargs: SimpleNamespace(
            returncode=0, stdout=binding["runtime_image_id"] + "\n"
        ),
    )
    assert (
        CAMPAIGN.verify_local_runtime_image(
            "docker", "semantic-okf-harbor-runtime:1.0"
        )
        == binding["runtime_image_id"]
    )
    monkeypatch.setattr(
        CAMPAIGN.subprocess,
        "run",
        lambda *_args, **_kwargs: SimpleNamespace(
            returncode=0, stdout="sha256:" + "0" * 64 + "\n"
        ),
    )
    with pytest.raises(CAMPAIGN.CampaignRunError, match="does not match"):
        CAMPAIGN.verify_local_runtime_image(
            "docker", "semantic-okf-harbor-runtime:1.0"
        )


def test_binding_drift_aborts_before_submitting_the_next_wave(tmp_path: Path) -> None:
    schedule = CAMPAIGN.build_schedule(cohorts=cohorts(), families=FAMILIES)
    campaign = tmp_path / "campaign"
    CAMPAIGN.persist_schedule(campaign, schedule)
    calls: list[int] = []
    verification_calls: list[tuple[str, ...] | None] = []

    def verify(_schedule, _campaign, families):
        selected = tuple(families) if families is not None else None
        verification_calls.append(selected)
        if selected is not None and "classical" in selected:
            raise CAMPAIGN.CampaignRunError("fixture drift")
        return "1" * 64

    def shard(cell, _campaign, _settings):
        calls.append(int(cell["sequence"]))
        return {
            "error_code": None,
            "failure_domain": None,
            "outcome": "answer-emitted",
        }

    checkpoint = CAMPAIGN.execute_campaign(
        schedule,
        campaign,
        CAMPAIGN.RunSettings(
            auth_file=tmp_path / "unused-auth.json",
            hf_cache=tmp_path / "unused-cache",
        ),
        shard_executor=shard,
        binding_verifier=verify,
    )

    assert calls == [1]
    assert verification_calls[:4] == [
        None,
        ("adaptive",),
        ("adaptive",),
        ("classical", "embeddings", "ensemble"),
    ]
    assert checkpoint["status"] == "aborted"
    assert checkpoint["trigger"]["sequence"] == 2
    assert checkpoint["trigger"]["error_code"] == "input_binding_drift"
    persisted = json.loads((campaign / "outcomes/0002.json").read_text(encoding="utf-8"))
    assert persisted["outcome"] == "runner-error"
    assert not (campaign / str(schedule["cells"][1]["shard_path"])).exists()


def test_binding_drift_after_a_call_rejects_its_result(tmp_path: Path) -> None:
    schedule = CAMPAIGN.build_schedule(cohorts=cohorts(), families=FAMILIES)
    campaign = tmp_path / "campaign"
    CAMPAIGN.persist_schedule(campaign, schedule)
    verification_count = 0
    calls: list[int] = []

    def verify(_schedule, _campaign, _families):
        nonlocal verification_count
        verification_count += 1
        if verification_count == 3:
            raise CAMPAIGN.CampaignRunError("fixture changed during the first call")
        return "1" * 64

    def shard(cell, _campaign, _settings):
        calls.append(int(cell["sequence"]))
        return {
            "error_code": None,
            "failure_domain": None,
            "outcome": "answer-emitted",
            "run_exit_code": 0,
            "trace_path": "q001__fixture/artifacts/pi.jsonl",
        }

    checkpoint = CAMPAIGN.execute_campaign(
        schedule,
        campaign,
        CAMPAIGN.RunSettings(
            auth_file=tmp_path / "unused-auth.json",
            hf_cache=tmp_path / "unused-cache",
        ),
        shard_executor=shard,
        binding_verifier=verify,
    )

    assert calls == [1]
    assert checkpoint["status"] == "aborted"
    assert checkpoint["trigger"]["error_code"] == "input_binding_drift"
    outcome = json.loads((campaign / "outcomes/0001.json").read_text(encoding="utf-8"))
    assert outcome["outcome"] == "runner-error"
    assert outcome["binding_error_type"] == "CampaignRunError"
    assert outcome["underlying_trace_outcome"] == "answer-emitted"
    assert outcome["underlying_trace_failure_domain"] is None
    assert outcome["underlying_trace_error_code"] is None
    assert outcome["run_exit_code"] == 0
    assert outcome["trace_path"] == "q001__fixture/artifacts/pi.jsonl"


def test_post_wave_binding_drift_records_every_completed_call(tmp_path: Path) -> None:
    schedule = CAMPAIGN.build_schedule(cohorts=cohorts(), families=FAMILIES)
    campaign = tmp_path / "campaign"
    CAMPAIGN.persist_schedule(campaign, schedule)
    verification_count = 0
    calls: list[int] = []

    def verify(_schedule, _campaign, _families):
        nonlocal verification_count
        verification_count += 1
        if verification_count == 5:
            raise CAMPAIGN.CampaignRunError("fixture changed during a wave")
        return "1" * 64

    def shard(cell, _campaign, _settings):
        sequence = int(cell["sequence"])
        calls.append(sequence)
        return {
            "error_code": None,
            "failure_domain": None,
            "outcome": "answer-emitted",
            "run_exit_code": 0,
            "trace_path": f"trace-{sequence}.jsonl",
        }

    checkpoint = CAMPAIGN.execute_campaign(
        schedule,
        campaign,
        CAMPAIGN.RunSettings(
            auth_file=tmp_path / "unused-auth.json",
            hf_cache=tmp_path / "unused-cache",
        ),
        shard_executor=shard,
        binding_verifier=verify,
    )

    assert calls == [1, 2, 3, 4]
    assert checkpoint["status"] == "aborted"
    assert checkpoint["trigger"]["sequence"] == 2
    for sequence in (2, 3, 4):
        outcome = json.loads(
            (campaign / f"outcomes/{sequence:04d}.json").read_text(encoding="utf-8")
        )
        assert outcome["outcome"] == "runner-error"
        assert outcome["underlying_trace_outcome"] == "answer-emitted"
        assert outcome["trace_path"] == f"trace-{sequence}.jsonl"


def test_binding_scoped_auth_reuses_private_copy_when_source_changes(
    tmp_path: Path, monkeypatch
) -> None:
    source = tmp_path / "source-auth.json"
    source.write_text(
        json.dumps({"openai-codex": {"access": "first-secret"}}),
        encoding="utf-8",
    )
    sessions = tmp_path / "sessions"
    digest = "a" * 64

    first = CAMPAIGN.prepare_binding_scoped_auth(
        source, digest, session_root=sessions
    )
    first_bytes = first.read_bytes()
    source.write_text(
        json.dumps({"openai-codex": {"access": "replacement-secret"}}),
        encoding="utf-8",
    )
    second = CAMPAIGN.prepare_binding_scoped_auth(
        source, digest, session_root=sessions
    )

    assert second == first
    assert second.read_bytes() == first_bytes
    assert b"replacement-secret" not in second.read_bytes()
    monkeypatch.setattr(
        CAMPAIGN.harbor_runner, "FROZEN_AUTH_SESSION_ROOT", sessions
    )
    mounted_directory, owned = CAMPAIGN.harbor_runner.execution_auth_directory(
        second, digest
    )
    assert mounted_directory == second.parent
    assert owned is False
    second.write_text(
        json.dumps({"openai-codex": {"access": "refreshed-secret"}}),
        encoding="utf-8",
    )
    reused = CAMPAIGN.prepare_binding_scoped_auth(
        source, digest, session_root=sessions
    )
    assert b"refreshed-secret" in reused.read_bytes()
    CAMPAIGN.remove_binding_scoped_auth(second, session_root=sessions)
    assert not second.parent.exists()


def test_existing_shard_recovery_uses_and_validates_its_live_receipt(
    tmp_path: Path, monkeypatch
) -> None:
    campaign = tmp_path / "campaign"
    shard = campaign / "runs/0001-q001-adaptive"
    trace = shard / "q001__fixture/artifacts/pi.jsonl"
    trace.parent.mkdir(parents=True)
    trace.write_text(
        json.dumps(
            {
                "type": "message_end",
                "message": {
                    "role": "assistant",
                    "content": [{"type": "text", "text": "{}"}],
                    "stopReason": "stop",
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )
    receipt_path = shard / "run-receipt.json"
    receipt = {
        "harbor_exit_code": 0,
        "provider_failure_detected": False,
        "run_status": "completed",
        "terminal_outcomes": {"answer-emitted": 1},
    }
    receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
    cell = {
        "cohort": "discovery",
        "family": "adaptive",
        "question_id": "q001",
        "sequence": 1,
        "shard_path": "runs/0001-q001-adaptive",
    }
    settings = CAMPAIGN.RunSettings(
        auth_file=tmp_path / "unused-auth.json",
        hf_cache=tmp_path / "unused-cache",
    )

    monkeypatch.setattr(
        CAMPAIGN,
        "_validate_recovered_shard_identity",
        lambda _cell, _campaign, _shard: json.loads(
            receipt_path.read_text(encoding="utf-8")
        ),
    )

    recovered = CAMPAIGN.run_shard(cell, campaign, settings)
    assert recovered["outcome"] == "answer-emitted"
    assert recovered["run_exit_code"] == 0

    receipt["terminal_outcomes"] = {"provider-error": 1}
    receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
    with pytest.raises(CAMPAIGN.CampaignRunError, match="differs from its traces"):
        CAMPAIGN.run_shard(cell, campaign, settings)

    receipt["terminal_outcomes"] = {}
    receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
    unexpected = shard / "unexpected/artifacts/pi.jsonl"
    unexpected.parent.mkdir(parents=True)
    trace.replace(unexpected)
    with pytest.raises(CAMPAIGN.CampaignRunError, match="off-contract Pi trace"):
        CAMPAIGN.run_shard(cell, campaign, settings)


def test_recovered_shard_identity_invokes_the_complete_frozen_audit(
    tmp_path: Path, monkeypatch
) -> None:
    campaign = tmp_path / "campaign"
    shard = campaign / "runs/0001-q001-adaptive"
    shard.mkdir(parents=True)
    bindings = {
        "families": {
            "adaptive": {
                "consult_skill": "consult-semantic-okf-adaptive",
                "offline_model_snapshot": None,
            }
        },
        "runtime_image_id": "sha256:" + "a" * 64,
    }
    (campaign / "input-bindings.json").write_text(
        json.dumps(bindings), encoding="utf-8"
    )
    receipt = {"identity": "audited"}
    calls: list[str] = []

    class FixtureSummaryError(ValueError):
        pass

    def scheduled_task_manifests(tasks_root, dataset_id, families):
        assert tasks_root == CAMPAIGN.HERE / "generated/tasks/graphrag-papers-40/consult-only"
        assert dataset_id == "graphrag-papers-40"
        assert families == ["adaptive"]
        calls.append("manifest")
        return {"adaptive": {"manifest": "bound"}}

    def validate_run_identity(run, **kwargs):
        assert run == shard
        assert kwargs == {
            "allow_partial": False,
            "cohort": "discovery",
            "dataset_id": "graphrag-papers-40",
            "family": "adaptive",
            "task_ids": ["q001"],
        }
        calls.append("identity")
        return receipt

    def validate_scheduled_receipt(run, observed, **kwargs):
        assert run == shard
        assert observed is receipt
        assert kwargs["expected_skill"] == "consult-semantic-okf-adaptive"
        assert kwargs["task_manifest"] == {"manifest": "bound"}
        assert kwargs["input_binding"] == bindings["families"]["adaptive"]
        assert kwargs["runtime_image_id"] == bindings["runtime_image_id"]
        assert len(kwargs["input_bindings_sha256"]) == 64
        calls.append("scheduled")

    fake_auditor = SimpleNamespace(
        SummaryError=FixtureSummaryError,
        scheduled_task_manifests=scheduled_task_manifests,
        validate_run_identity=validate_run_identity,
        validate_scheduled_receipt=validate_scheduled_receipt,
    )
    monkeypatch.setitem(sys.modules, "summarize_consult_campaign", fake_auditor)
    cell = {
        "cohort": "discovery",
        "family": "adaptive",
        "question_id": "q001",
        "sequence": 1,
        "shard_path": "runs/0001-q001-adaptive",
    }

    assert CAMPAIGN._validate_recovered_shard_identity(cell, campaign, shard) is receipt
    assert calls == ["manifest", "identity", "scheduled"]

    fake_auditor.validate_run_identity = lambda *_args, **_kwargs: (_ for _ in ()).throw(
        FixtureSummaryError("forged identity")
    )
    with pytest.raises(CAMPAIGN.CampaignRunError, match="frozen identity contract"):
        CAMPAIGN._validate_recovered_shard_identity(cell, campaign, shard)


def test_campaign_operation_lock_is_exclusive_and_crash_reusable(tmp_path: Path) -> None:
    campaign = tmp_path / "campaign"
    lock_path = campaign / ".campaign-operation.lock"

    with CAMPAIGN.campaign_operation_lock(campaign, "outer"):
        assert lock_path.is_file()
        with pytest.raises(CAMPAIGN.CampaignRunError, match="already held"):
            with CAMPAIGN.campaign_operation_lock(campaign, "nested"):
                pytest.fail("a second campaign operation may not acquire the lease")

    retained = json.loads(lock_path.read_text(encoding="utf-8"))
    assert retained["owner"] == "outer"
    with CAMPAIGN.campaign_operation_lock(campaign, "recovered"):
        assert lock_path.is_file()
    current = json.loads(lock_path.read_text(encoding="utf-8"))
    assert current["owner"] == "recovered"


def test_campaign_operation_lock_survives_local_record_and_directory_replacement(
    tmp_path: Path,
) -> None:
    if os.name != "posix":
        pytest.skip("path-replacement regression requires the Linux lease")
    campaign = tmp_path / "campaign"
    moved = tmp_path / "moved-campaign"
    contender_was_blocked = False

    with pytest.raises(CAMPAIGN.CampaignRunError, match="operation record"):
        with CAMPAIGN.campaign_operation_lock(campaign, "outer"):
            (campaign / ".campaign-operation.lock").unlink()
            campaign.rename(moved)
            campaign.mkdir()
            with pytest.raises(CAMPAIGN.CampaignRunError, match="already held"):
                with CAMPAIGN.campaign_operation_lock(campaign, "contender"):
                    pytest.fail("path replacement must not create a second lease")
            contender_was_blocked = True

    assert contender_was_blocked


def test_existing_outcomes_are_reaudited_before_they_can_skip_a_cell(
    tmp_path: Path, monkeypatch
) -> None:
    schedule = CAMPAIGN.build_schedule(cohorts=cohorts(), families=FAMILIES)
    campaign = tmp_path / "campaign"
    first = schedule["cells"][0]
    persisted = CAMPAIGN._persist_outcome(
        campaign,
        first,
        {
            "error_code": "fixture",
            "failure_domain": "runner",
            "outcome": "runner-error",
            "run_exit_code": None,
            "trace_path": None,
        },
    )
    audited: list[int] = []

    def audit(cell, checked_campaign, outcome):
        assert checked_campaign == campaign
        assert outcome == persisted
        audited.append(int(cell["sequence"]))

    monkeypatch.setattr(CAMPAIGN, "_validate_recovered_outcome", audit)
    checkpoint = CAMPAIGN.execute_campaign(
        schedule,
        campaign,
        CAMPAIGN.RunSettings(
            auth_file=tmp_path / "unused-auth.json",
            hf_cache=tmp_path / "unused-cache",
        ),
        binding_verifier=lambda *_args: "a" * 64,
    )

    assert audited == [1]
    assert checkpoint["status"] == "aborted"


def test_recovered_non_runner_outcome_requires_its_scheduled_shard(
    tmp_path: Path,
) -> None:
    cell = {
        "question_id": "q001",
        "sequence": 1,
        "shard_path": "runs/0001-q001-adaptive",
    }

    with pytest.raises(CAMPAIGN.CampaignRunError, match="no auditable scheduled shard"):
        CAMPAIGN._validate_recovered_outcome(
            cell,
            tmp_path / "campaign",
            {
                "error_code": None,
                "failure_domain": None,
                "outcome": "answer-emitted",
                "run_exit_code": 0,
                "trace_path": "q001__fixture/artifacts/pi.jsonl",
            },
        )
