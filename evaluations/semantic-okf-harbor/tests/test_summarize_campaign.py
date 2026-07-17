"""Tests for explicit, hash-bound Harbor campaign aggregation."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).resolve().parents[1]


def module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


SUMMARY = module("semantic_okf_harbor_campaign_summary", ROOT / "summarize_campaign.py")


def dump(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True) + "\n", encoding="utf-8")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def campaign(path: Path, cohorts: dict[str, list[str]] | None = None) -> Path:
    target = path / "campaign.json"
    dump(target, {
        "campaign_id": "campaign-a",
        "families": ["classical"],
        "live_cases": cohorts or {"train": [], "dev": ["q032"], "holdout": []},
        "runtime": {
            "agent": "pi", "pi_version": "0.73.1",
            "model": "openai-codex/gpt-5.3-codex-spark", "mcp_used": False,
        },
    })
    return target


def trial(
    root: Path,
    generation: str,
    *,
    question: str = "q032",
    cohort: str = "dev",
    rewards: dict[str, float] | None = None,
    exception_type: str | None = None,
) -> dict[str, object]:
    trial_name = f"{question}__fixed"
    trial_dir = root / trial_name
    lock = {
        "task": {"name": question, "source": cohort, "digest": "sha256:task"},
        "agent": {"name": "pi", "model_name": "openai-codex/gpt-5.3-codex-spark", "mcp_servers": []},
        "skills": [{
            "name": f"consult-{generation}",
            "source": f"/repo/evaluations/semantic-okf-harbor/snapshots/content/{generation}/classical/consult-{generation}",
            "digest": f"sha256:{generation}",
        }],
    }
    job_id = f"job-{generation}"
    values = {name: 1.0 for name in SUMMARY.REWARD_DIMENSIONS}
    if rewards:
        values.update(rewards)
    result = {
        "task_name": f"knowledge/semantic-okf-harbor__{question}",
        "trial_name": trial_name,
        "source": cohort,
        "task_checksum": "same-task-checksum",
        "config": {"job_id": job_id},
        "agent_info": {
            "name": "pi", "version": "0.73.1",
            "model_info": {"provider": "openai-codex", "name": "gpt-5.3-codex-spark"},
        },
        "agent_result": {"n_input_tokens": 100, "n_cache_tokens": 70, "n_output_tokens": 20},
        "verifier_result": {"rewards": values},
        "exception_info": {"exception_type": exception_type} if exception_type else None,
        "agent_execution": {"started_at": "2026-07-16T10:00:00Z", "finished_at": "2026-07-16T10:00:03Z"},
    }
    dump(root / "result.json", {"id": job_id})
    dump(root / "lock.json", {"trials": [lock]})
    dump(trial_dir / "result.json", result)
    dump(trial_dir / "lock.json", lock)
    return {
        "family": "classical", "generation": generation, "cohort": cohort,
        "question_id": question, "result_root": root.relative_to(root.parents[1]).as_posix(),
        "job_result_sha256": digest(root / "result.json"),
        "job_lock_sha256": digest(root / "lock.json"),
        "trial_relative_dir": trial_name,
        "trial_result_sha256": digest(trial_dir / "result.json"),
        "trial_lock_sha256": digest(trial_dir / "lock.json"),
    }


def ledger(tmp_path: Path, entries: list[dict[str, object]], external: bool | None = True) -> Path:
    target = tmp_path / "bindings.json"
    dump(target, {
        "schema_version": SUMMARY.SCHEMA,
        "campaign_id": "campaign-a",
        "external_gates": {"classical": {"deterministic_retrieval_no_regression": external}},
        "excluded_runs": [],
        "entries": entries,
    })
    return target


def paired(tmp_path: Path, **evolved: object) -> tuple[Path, Path]:
    base = trial(tmp_path / "runs/baseline", "baseline")
    candidate = trial(tmp_path / "runs/evolved", "evolved", **evolved)
    return ledger(tmp_path, [base, candidate]), campaign(tmp_path)


def test_complete_pair_reports_all_dimensions_resources_and_promotion(tmp_path: Path) -> None:
    bindings, campaign_path = paired(tmp_path, rewards={"reward": 0.9})
    report = SUMMARY.summarize(bindings, campaign_path)
    assert report["status"] == "complete"
    assert report["paired_cases"] == 1
    assert report["reward_dimensions"] == list(SUMMARY.REWARD_DIMENSIONS)
    evolved = report["aggregates"]["dev"]["classical"]["evolved"]
    assert len(evolved["metrics"]) == 16
    assert evolved["metrics"]["reward"] == {"mean": 0.9, "observed_trials": 1, "total_trials": 1}
    assert evolved["resources"]["latency_seconds"]["mean"] == 3.0
    assert evolved["resources"]["input_tokens"]["total"] == 100.0
    assert report["promotion"]["classical"]["decision"] == "rejected"  # reward regressed from 1.0


def test_promotion_passes_only_when_internal_and_external_gates_pass(tmp_path: Path) -> None:
    bindings, campaign_path = paired(tmp_path)
    report = SUMMARY.summarize(bindings, campaign_path)
    assert report["promotion"]["classical"]["decision"] == "promoted"
    pending_bindings = ledger(tmp_path, load_json(bindings)["entries"], external=None)
    pending = SUMMARY.summarize(pending_bindings, campaign_path)
    assert pending["promotion"]["classical"]["decision"] == "pending"
    assert "| classical | pending | pass | pass |" in SUMMARY.markdown(pending)
    assert SUMMARY._gate(None) == "pending"


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def test_hash_mismatch_is_rejected_before_aggregation(tmp_path: Path) -> None:
    bindings, campaign_path = paired(tmp_path)
    data = load_json(bindings)
    data["entries"][0]["trial_result_sha256"] = "0" * 64
    dump(bindings, data)
    with pytest.raises(SUMMARY.CampaignSummaryError, match="trial_result_sha256 mismatch"):
        SUMMARY.summarize(bindings, campaign_path)


def test_job_and_trial_lock_must_be_the_same_bound_configuration(tmp_path: Path) -> None:
    bindings, campaign_path = paired(tmp_path)
    data = load_json(bindings)
    entry = data["entries"][0]
    lock_path = tmp_path / entry["result_root"] / entry["trial_relative_dir"] / "lock.json"
    broken = load_json(lock_path)
    broken["task"]["digest"] = "sha256:changed"
    dump(lock_path, broken)
    entry["trial_lock_sha256"] = digest(lock_path)
    dump(bindings, data)
    with pytest.raises(SUMMARY.CampaignSummaryError, match="exactly the bound trial lock"):
        SUMMARY.summarize(bindings, campaign_path)


def test_duplicate_or_unpaired_bindings_are_rejected(tmp_path: Path) -> None:
    bindings, campaign_path = paired(tmp_path)
    data = load_json(bindings)
    data["entries"].append(dict(data["entries"][0]))
    dump(bindings, data)
    with pytest.raises(SUMMARY.CampaignSummaryError, match="duplicate campaign binding"):
        SUMMARY.summarize(bindings, campaign_path)
    data["entries"] = data["entries"][:1]
    dump(bindings, data)
    with pytest.raises(SUMMARY.CampaignSummaryError, match="matrix is incomplete"):
        SUMMARY.summarize(bindings, campaign_path)


def test_runtime_failure_keeps_missing_metrics_null_and_rejects_promotion(tmp_path: Path) -> None:
    bindings, campaign_path = paired(tmp_path, exception_type="AgentTimeoutError")
    data = load_json(bindings)
    entry = data["entries"][1]
    result_path = tmp_path / entry["result_root"] / entry["trial_relative_dir"] / "result.json"
    result = load_json(result_path)
    result["verifier_result"]["rewards"] = {"quality_gate": 0.0, "reward": 0.0}
    dump(result_path, result)
    entry["trial_result_sha256"] = digest(result_path)
    dump(bindings, data)
    report = SUMMARY.summarize(bindings, campaign_path)
    evolved = report["aggregates"]["dev"]["classical"]["evolved"]
    assert evolved["runtime_errors_by_type"] == {"AgentTimeoutError": 1}
    assert evolved["metrics"]["response_contract"]["mean"] is None
    assert report["promotion"]["classical"]["decision"] == "rejected"


def test_missing_baseline_completeness_keeps_non_regression_gate_pending(tmp_path: Path) -> None:
    bindings, campaign_path = paired(tmp_path)
    data = load_json(bindings)
    entry = data["entries"][0]
    result_path = tmp_path / entry["result_root"] / entry["trial_relative_dir"] / "result.json"
    result = load_json(result_path)
    for name in SUMMARY.HARD_COMPLETENESS:
        result["verifier_result"]["rewards"].pop(name)
    dump(result_path, result)
    entry["trial_result_sha256"] = digest(result_path)
    dump(bindings, data)
    report = SUMMARY.summarize(bindings, campaign_path)
    promotion = report["promotion"]["classical"]
    assert promotion["decision"] == "pending"
    assert promotion["checks"]["dev_hard_completeness_no_regression"] is None


def test_allow_incomplete_reports_missing_matrix_and_semantic_limit(tmp_path: Path) -> None:
    base = trial(tmp_path / "runs/baseline", "baseline")
    bindings = ledger(tmp_path, [base])
    report = SUMMARY.summarize(bindings, campaign(tmp_path), allow_incomplete=True)
    rendered = SUMMARY.markdown(report)
    assert report["status"] == "incomplete"
    assert report["missing_bindings"] == [{
        "family": "classical", "cohort": "dev", "question_id": "q032", "generation": "evolved",
    }]
    assert "All sixteen Harbor reward dimensions" in rendered
    assert "do **not** establish semantic answer correctness" in rendered
    assert "## Train" in rendered and "## Dev" in rendered and "## Holdout" in rendered


def test_rejects_path_escape_unknown_rewards_and_wrong_snapshot_generation(tmp_path: Path) -> None:
    bindings, campaign_path = paired(tmp_path)
    data = load_json(bindings)
    data["entries"][0]["result_root"] = "../elsewhere"
    dump(bindings, data)
    with pytest.raises(SUMMARY.CampaignSummaryError, match="stay within"):
        SUMMARY.summarize(bindings, campaign_path)


def test_rejects_out_of_range_rewards_and_unknown_external_gate(tmp_path: Path) -> None:
    bindings, campaign_path = paired(tmp_path)
    data = load_json(bindings)
    entry = data["entries"][1]
    result_path = tmp_path / entry["result_root"] / entry["trial_relative_dir"] / "result.json"
    result = load_json(result_path)
    result["verifier_result"]["rewards"]["reward"] = 1.1
    dump(result_path, result)
    entry["trial_result_sha256"] = digest(result_path)
    dump(bindings, data)
    with pytest.raises(SUMMARY.CampaignSummaryError, match=r"within \[0, 1\]"):
        SUMMARY.summarize(bindings, campaign_path)

    result["verifier_result"]["rewards"]["reward"] = 1.0
    dump(result_path, result)
    entry["trial_result_sha256"] = digest(result_path)
    data["external_gates"]["classical"]["semantic_judgment"] = True
    dump(bindings, data)
    with pytest.raises(SUMMARY.CampaignSummaryError, match="unknown fields"):
        SUMMARY.summarize(bindings, campaign_path)


def test_excluded_runs_are_documented_but_never_aggregated(tmp_path: Path) -> None:
    bindings, campaign_path = paired(tmp_path)
    excluded_root = tmp_path / "runs/pre-fix"
    excluded_root.mkdir(parents=True)
    data = load_json(bindings)
    data["excluded_runs"] = [{
        "result_root": "runs/pre-fix",
        "category": "pre_fix_grader",
        "reason": "Superseded by the repaired grader run.",
    }]
    dump(bindings, data)
    report = SUMMARY.summarize(bindings, campaign_path)
    assert report["paired_cases"] == 1
    assert report["excluded_runs"] == data["excluded_runs"]
    assert "never participate in any aggregate" in SUMMARY.markdown(report)


def test_result_root_cannot_be_bound_and_excluded(tmp_path: Path) -> None:
    bindings, campaign_path = paired(tmp_path)
    data = load_json(bindings)
    data["excluded_runs"] = [{
        "result_root": data["entries"][0]["result_root"],
        "category": "pre_fix_grader",
        "reason": "This intentionally contradicts the binding.",
    }]
    dump(bindings, data)
    with pytest.raises(SUMMARY.CampaignSummaryError, match="both bound and excluded"):
        SUMMARY.summarize(bindings, campaign_path)
