"""Tests for the registered dual-mode Semantic OKF evaluation datasets."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import shutil
import sys
from pathlib import Path
from types import ModuleType

import pytest

REPO = Path(__file__).resolve().parents[1]
ROOT = REPO / "evaluations/semantic-okf-datasets"
GRADER_ROOT = REPO / "evaluations/semantic-okf-harbor/grader"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(GRADER_ROOT))

import dataset_tool as DATA  # noqa: E402
import generate_harbor_tasks as GENERATOR  # noqa: E402
import run_harbor as RUNNER  # noqa: E402
import summarize_consult_campaign as SUMMARY  # noqa: E402


def module(name: str, path: Path) -> ModuleType:
    """Load a repository script without requiring a package path."""

    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


SCORE = module(
    "semantic_okf_dataset_score",
    REPO / "evaluations/semantic-okf-harbor/grader/score.py",
)


def write_json(path: Path, value: object) -> None:
    """Write one JSON test fixture."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value) + "\n", encoding="utf-8")


def test_tree_digest_uses_cross_platform_posix_order_and_exclusions(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "mixed-case-tree"
    files = {
        "Zoo.txt": b"upper-z",
        "apple.txt": b"lower-a",
        "nested/Beta.txt": b"upper-b",
        "nested/alpha.txt": b"lower-a-nested",
        "nested/ignored.txt": b"excluded",
        "__pycache__/cache.pyc": b"cache",
    }
    for relative, payload in files.items():
        path = root.joinpath(*relative.split("/"))
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)

    discovered = [root.joinpath(*relative.split("/")) for relative in files]
    discovery_orders = iter(
        (
            sorted(discovered, key=lambda path: path.as_posix().casefold()),
            list(reversed(discovered)),
        )
    )

    def simulated_rglob(path: Path, pattern: str) -> list[Path]:
        assert path == root
        assert pattern == "*"
        return next(discovery_orders)

    monkeypatch.setattr(type(root), "rglob", simulated_rglob)

    expected = hashlib.sha256()
    for relative in (
        "Zoo.txt",
        "apple.txt",
        "nested/Beta.txt",
        "nested/alpha.txt",
    ):
        expected.update(relative.encode("utf-8") + b"\0" + files[relative] + b"\0")

    expected_digest = expected.hexdigest()
    assert DATA.tree_digest(root, exclude={"nested/ignored.txt"}) == expected_digest
    assert DATA.tree_digest(root, exclude={"nested/ignored.txt"}) == expected_digest


def test_registry_validates_both_datasets_and_all_strategy_pairs() -> None:
    reports = {identifier: DATA.validate_dataset(identifier) for identifier in DATA.available_datasets()}
    assert set(reports) == {"astro-40", "graphrag-papers-40"}
    assert reports["astro-40"]["source_file_count"] == 416
    assert reports["graphrag-papers-40"]["source_file_count"] == 31
    assert all(report["question_count"] == 40 for report in reports.values())
    assert all(report["hard_question_count"] == 10 for report in reports.values())
    assert all(len(report["families"]) == 8 for report in reports.values())
    assert reports["graphrag-papers-40"]["reference_bundle_present"] is True
    assert reports["astro-40"]["reference_bundle_present"] is False
    assert reports["graphrag-papers-40"]["semantic_rubric_count"] == 30
    assert reports["astro-40"]["semantic_rubric_count"] == 0


def test_cohorts_partition_questions_exactly_once() -> None:
    for identifier in DATA.available_datasets():
        dataset = DATA.load_dataset(identifier)
        cohorts = DATA.dataset_cohorts(dataset)
        partition = [item for name in dataset["partition_cohorts"] for item in cohorts[name]]
        questions = [row["normalized_id"] for row in DATA.dataset_questions(dataset)]
        assert len(partition) == len(set(partition)) == 40
        assert set(partition) == set(questions)


def test_staged_paper_input_is_deterministic_and_evaluator_free(tmp_path: Path) -> None:
    stage = tmp_path / "stage"
    stage.mkdir()
    receipt = DATA.stage_dataset("graphrag-papers-40", "legacy", stage)
    assert receipt["evaluator_material_included"] is False
    assert receipt["payload_tree_sha256"] == DATA.tree_digest(stage, exclude={"input-manifest.json"})
    assert (stage / "manifest.json").is_file()
    assert len(receipt["source_files"]) == 31
    names = {path.name.casefold() for path in stage.rglob("*") if path.is_file()}
    assert "retrieval-questions.jsonl" not in names
    assert "hard-ground-truth.jsonl" not in names
    assert not any("qrel" in name or "ground-truth" in name for name in names)


def test_describe_exposes_non_overlapping_mode_contracts() -> None:
    report = DATA.describe("graphrag-papers-40", "legacy")
    build_consult = report["modes"]["build-consult"]
    consult_only = report["modes"]["consult-only"]
    assert build_consult["installed_skills"] == [
        "build-semantic-okf",
        "consult-semantic-okf",
    ]
    assert build_consult["read_only_mount"] == "/dataset"
    assert build_consult["prebuilt_knowledge_mounted"] is False
    assert consult_only["installed_skills"] == ["consult-semantic-okf"]
    assert consult_only["read_only_mount"] == "/knowledge"
    assert consult_only["raw_sources_mounted"] is False


def test_mode_instructions_keep_raw_and_processed_knowledge_separate() -> None:
    family = DATA.load_families()["legacy"]
    question = {
        "id": "q001",
        "question": "What is supported?",
        "question_type": "direct",
        "qrels": {"document_ids": ["secret-document"], "source_ids": ["secret-source"]},
    }
    consult = GENERATOR.instruction(question, "consult-only", "legacy", family)
    end_to_end = GENERATOR.instruction(question, "build-consult", "legacy", family)
    assert "/knowledge" in consult and "consult-semantic-okf" in consult
    assert "/dataset" not in consult and "build-semantic-okf" not in consult
    assert "/dataset/manifest.json" in end_to_end and "/workspace/knowledge" in end_to_end
    assert "build-semantic-okf" in end_to_end and "consult-semantic-okf" in end_to_end
    assert "secret-document" not in consult + end_to_end
    assert "secret-source" not in consult + end_to_end


def test_paper_rubric_restores_minimum_without_leaking_required_points() -> None:
    dataset = DATA.load_dataset("graphrag-papers-40")
    rubrics = DATA.dataset_semantic_rubrics(dataset)
    source = next(
        row
        for row in DATA.dataset_questions(dataset)
        if row["normalized_id"] == "q003"
    )
    question = GENERATOR.normalized_question(
        source, dataset["question_format"], rubrics["q003"]
    )
    instruction = GENERATOR.instruction(
        question, "consult-only", "legacy", DATA.load_families()["legacy"]
    )

    assert question["minimum_document_count"] == 6
    assert len(question["semantic_rubric"]["required_points"]) == 4
    assert "at least 6 independent relevant papers" in instruction
    assert all(
        point not in instruction
        for point in question["semantic_rubric"]["required_points"]
    )


def test_paper_truth_splits_reader_discarded_controls_into_exact_spans() -> None:
    dataset = DATA.load_dataset("graphrag-papers-40")
    source = next(
        row
        for row in DATA.load_jsonl(DATA.pinned_path(dataset["hard_ground_truth"], "truth"))
        if DATA.normalize_question_id(row["id"]) == "q037"
    )
    truth = GENERATOR.normalize_paper_truth(source)
    rows = [
        row
        for row in truth["authoritative_evidence"]
        if row["id"].startswith("claim-2508-19855v3-044-paper-3")
    ]
    assert len(rows) == 3
    assert [row["id"] for row in rows] == [
        "claim-2508-19855v3-044-paper-3-part-1",
        "claim-2508-19855v3-044-paper-3-part-2",
        "claim-2508-19855v3-044-paper-3-part-3",
    ]
    authority = DATA.repo_path(rows[0]["path"], "authority")
    normalized = GENERATOR.normalized_utf8_payload(authority).decode("utf-8")
    assert all(
        not any(ord(character) < 0x20 and character not in "\n\t\r" for character in normalized[row["start_char"] : row["end_char"]])
        for row in rows
    )


def test_paper_hard_oracle_passes_the_real_harbor_grader(tmp_path: Path) -> None:
    dataset = DATA.load_dataset("graphrag-papers-40")
    question = next(
        GENERATOR.normalized_question(row, dataset["question_format"])
        for row in DATA.dataset_questions(dataset)
        if DATA.normalize_question_id(row["id"]) == "q037"
    )
    truth = GENERATOR.normalized_truths(dataset)["q037"]
    bundle = DATA.repo_path(dataset["reference_bundle"], "reference bundle")
    ledger_path = bundle / "semantic/records.jsonl"
    ledger_rows, ledger = GENERATOR.ledger(ledger_path)
    crosswalk = GENERATOR.source_combination(dataset, ledger_rows)
    answer = GENERATOR.oracle_answer(question, truth, crosswalk, ledger)

    shutil.copyfile(ledger_path, tmp_path / "records.jsonl")
    write_json(tmp_path / "question.json", question)
    write_json(tmp_path / "truth.json", truth)
    write_json(tmp_path / "crosswalk.json", crosswalk)
    (tmp_path / "pi.jsonl").write_text(GENERATOR.pi_event(answer), encoding="utf-8")
    GENERATOR.copy_authority(truth, tmp_path / "authority")
    rewards, diagnostics = SCORE.score(
        argparse.Namespace(
            pi_log=tmp_path / "pi.jsonl",
            question=tmp_path / "question.json",
            ledger=tmp_path / "records.jsonl",
            crosswalk=tmp_path / "crosswalk.json",
            ground_truth=tmp_path / "truth.json",
            authority_root=tmp_path / "authority",
        )
    )
    assert rewards["evidence_contract_gate"] == 1.0
    assert rewards["mechanical_qualification_gate"] == 1.0
    assert rewards["authoritative_evidence_anchor_coverage"] == 1.0
    assert diagnostics["covered_hard_evidence_count"] == diagnostics["expected_hard_evidence_count"]


def test_runner_configs_install_only_mode_appropriate_skills(tmp_path: Path) -> None:
    task_path = tmp_path / "tasks"
    task_path.mkdir()
    resource = tmp_path / "resource"
    resource.mkdir()
    build = tmp_path / "build-skill"
    consult = tmp_path / "consult-skill"
    build.mkdir()
    consult.mkdir()
    common = {
        "output": tmp_path / "job",
        "tasks_path": task_path,
        "task_ids": ["q001"],
        "attempts": 1,
        "resource": resource,
        "auth_source": "<ephemeral-auth-directory>",
        "hf_cache": None,
    }
    consult_config = RUNNER.job_config(
        **common,
        skills=[consult],
        resource_target="/knowledge",
    )
    build_config = RUNNER.job_config(
        **common,
        skills=[build, consult],
        resource_target="/dataset",
    )
    assert consult_config["agents"][0]["skills"] == [str(consult)]
    assert build_config["agents"][0]["skills"] == [str(build), str(consult)]
    assert [mount["target"] for mount in consult_config["environment"]["mounts"]] == [
        "/knowledge",
        "/root/.pi/agent",
    ]
    assert [mount["target"] for mount in build_config["environment"]["mounts"]] == [
        "/dataset",
        "/root/.pi/agent",
    ]
    assert all(mount.get("read_only") for mount in (consult_config["environment"]["mounts"][0], build_config["environment"]["mounts"][0]))
    assert "secret" not in json.dumps(consult_config) + json.dumps(build_config)


def test_runner_requires_embedding_cache_only_for_declared_families() -> None:
    families = DATA.load_families()
    assert {name for name, row in families.items() if row["requires_hf_cache"]} == {
        "embeddings",
        "ensemble",
    }


def test_runner_receipt_status_rejects_provider_failure_even_when_harbor_exits_zero() -> None:
    provider = RUNNER.completion_status(0, {"provider-quota": 1})
    successful = RUNNER.completion_status(0, {"answer-emitted": 1})
    runner_failure = RUNNER.completion_status(7, {})
    signaled = RUNNER.completion_status(-9, {})

    assert provider == {
        "provider_failure_detected": True,
        "run_status": "provider-failure",
        "effective_exit_code": 2,
    }
    assert successful == {
        "provider_failure_detected": False,
        "run_status": "completed",
        "effective_exit_code": 0,
    }
    assert runner_failure == {
        "provider_failure_detected": False,
        "run_status": "runner-failure",
        "effective_exit_code": 7,
    }
    assert signaled == {
        "provider_failure_detected": False,
        "run_status": "runner-failure",
        "effective_exit_code": 137,
    }


def test_campaign_summary_binds_runtime_and_preserves_technical_failures(tmp_path: Path) -> None:
    campaign = tmp_path / "campaign"
    run = campaign / "runs/adaptive-discovery"
    trial = run / "q001__fixture"
    cohorts = DATA.dataset_cohorts(DATA.load_dataset("graphrag-papers-40"))
    write_json(
        run / "config.json",
        {
            "agents": [
                {
                    "name": "pi",
                    "model_name": SUMMARY.EXPECTED_MODEL,
                    "skills": [str(REPO / "skills/consult-semantic-okf-adaptive")],
                    "kwargs": {"version": SUMMARY.EXPECTED_PI_VERSION, "thinking": "high"},
                }
            ],
            "datasets": [{"task_names": cohorts["discovery"]}],
        },
    )
    write_json(
        run / "run-receipt.json",
        {
            "dataset_id": "graphrag-papers-40",
            "family": "adaptive",
            "mode": "consult-only",
            "cohort": "discovery",
            "task_ids": cohorts["discovery"],
            "attempts": 1,
            "model": SUMMARY.EXPECTED_MODEL,
            "pi_version": SUMMARY.EXPECTED_PI_VERSION,
            "public_mount_target": "/knowledge",
            "prebuilt_knowledge_mounted": True,
            "raw_sources_mounted": False,
            "installed_skills": [
                {"path": str(REPO / "skills/consult-semantic-okf-adaptive")}
            ],
            "resource_kind": "processed-knowledge",
            "records_sha256": "a" * 64,
        },
    )
    write_json(
        trial / "result.json",
        {
            "id": "trial-1",
            "task_name": "knowledge/graphrag-papers-40__consult-only__adaptive__q001",
            "started_at": "2026-07-17T00:00:00Z",
            "finished_at": "2026-07-17T00:10:00Z",
            "agent_result": {
                "n_input_tokens": 100,
                "n_cache_tokens": 50,
                "n_output_tokens": 20,
            },
            "verifier_result": {"rewards": {"reward": 0.0, "quality_gate": 0.0}},
            "exception_info": {
                "exception_type": "AgentTimeoutError",
                "exception_message": "timed out",
            },
        },
    )
    (trial / "artifacts").mkdir(parents=True)
    (trial / "artifacts/pi.jsonl").write_text(
        json.dumps(
            {
                "type": "message_end",
                "message": {
                    "role": "assistant",
                    "content": [{"type": "text", "text": "still working"}],
                    "stopReason": "toolUse",
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )
    report = SUMMARY.summarize(campaign, "graphrag-papers-40", allow_partial=True)
    adaptive = report["by_family"]["adaptive"]
    assert report["structurally_complete"] is False
    assert report["ranking_eligible"] is False
    assert report["result_trials"] == 1
    assert adaptive["agent_outcomes"] == {"agent-interrupted": 1}
    assert adaptive["secondary_anomalies"] == {"AgentTimeoutError": 1}
    assert adaptive["metrics"]["reward"] == {
        "mean": None,
        "observed": 0,
    }
    assert adaptive["metrics"]["response_contract"] == {
        "mean": None,
        "observed": 0,
    }
    assert adaptive["tokens"] == {"input": 100, "cache": 50, "output": 20}
    rendered = SUMMARY.markdown(report)
    assert "adaptive" in rendered
    assert "INVALID FOR COMPARISON" in rendered
    assert "## Cohort observability" in rendered


def test_campaign_summary_rejects_incomplete_strict_matrix(tmp_path: Path) -> None:
    with pytest.raises(SUMMARY.SummaryError, match="campaign is incomplete"):
        SUMMARY.summarize(tmp_path / "empty", "graphrag-papers-40")


def test_structurally_complete_quota_campaign_is_forensic_not_rankable(
    tmp_path: Path,
) -> None:
    campaign = tmp_path / "campaign"
    dataset = DATA.load_dataset("graphrag-papers-40")
    cohorts = DATA.dataset_cohorts(dataset)
    families = DATA.load_families()
    quota_written = False
    for family, metadata in families.items():
        for cohort in dataset["partition_cohorts"]:
            task_ids = cohorts[cohort]
            run = campaign / "runs" / f"{family}-{cohort}"
            write_json(
                run / "config.json",
                {
                    "agents": [
                        {
                            "name": "pi",
                            "model_name": SUMMARY.EXPECTED_MODEL,
                            "skills": [str(REPO / "skills" / metadata["consult_skill"])],
                            "kwargs": {
                                "version": SUMMARY.EXPECTED_PI_VERSION,
                                "thinking": "high",
                            },
                        }
                    ],
                    "datasets": [{"task_names": task_ids}],
                },
            )
            write_json(
                run / "run-receipt.json",
                {
                    "dataset_id": "graphrag-papers-40",
                    "family": family,
                    "mode": "consult-only",
                    "cohort": cohort,
                    "task_ids": task_ids,
                    "attempts": 1,
                    "model": SUMMARY.EXPECTED_MODEL,
                    "pi_version": SUMMARY.EXPECTED_PI_VERSION,
                    "public_mount_target": "/knowledge",
                    "prebuilt_knowledge_mounted": True,
                    "raw_sources_mounted": False,
                    "installed_skills": [
                        {"path": str(REPO / "skills" / metadata["consult_skill"])}
                    ],
                    "resource_kind": "processed-knowledge",
                    "records_sha256": "b" * 64,
                },
            )
            for identifier in task_ids:
                trial = run / f"{identifier}__fixture"
                write_json(
                    trial / "result.json",
                    {
                        "id": f"{family}-{identifier}",
                        "task_name": (
                            "knowledge/graphrag-papers-40__consult-only__"
                            f"{family}__{identifier}"
                        ),
                        "agent_result": {},
                        "verifier_result": {
                            "rewards": {
                                "reward": 1.0,
                                "evidence_contract_gate": 1.0,
                                "minimum_document_gate": 1.0,
                                "mechanical_qualification_gate": 1.0,
                            }
                        },
                    },
                )
                (trial / "artifacts").mkdir(parents=True)
                if not quota_written:
                    event = {
                        "type": "message_end",
                        "message": {
                            "role": "assistant",
                            "content": [],
                            "stopReason": "error",
                            "errorMessage": "usage_limit_reached",
                        },
                    }
                    quota_written = True
                else:
                    event = {
                        "type": "message_end",
                        "message": {
                            "role": "assistant",
                            "content": [{"type": "text", "text": "{}"}],
                            "stopReason": "stop",
                        },
                    }
                (trial / "artifacts/pi.jsonl").write_text(
                    json.dumps(event) + "\n", encoding="utf-8"
                )

    with pytest.raises(SUMMARY.SummaryError, match="not ranking-eligible"):
        SUMMARY.summarize(campaign, "graphrag-papers-40")
    report = SUMMARY.summarize(
        campaign, "graphrag-papers-40", allow_invalid=True
    )
    assert report["structurally_complete"] is True
    assert report["provider_clean"] is False
    assert report["evaluation_complete"] is False
    assert report["ranking_eligible"] is False
    assert report["evaluable_trials"] == 0
    assert report["evaluator_clean"] is False
    assert report["winner"] is None
    rendered = SUMMARY.markdown(report)
    assert "INVALID FOR COMPARISON" in rendered
    assert "## Mechanical ranking" not in rendered


def test_active_papers_campaign_has_durable_progress_checkpoints() -> None:
    reports = ROOT / "reports"
    log = reports / "20260717-papers-consult-gpt53-spark-01-test-log.md"
    checkpoints = DATA.load_json(
        reports / "20260717-papers-consult-gpt53-spark-01-checkpoints.json"
    )
    assert log.is_file()
    assert checkpoints["dataset_id"] == "graphrag-papers-40"
    assert checkpoints["model"] == SUMMARY.EXPECTED_MODEL
    assert checkpoints["pi_version"] == SUMMARY.EXPECTED_PI_VERSION
    assert checkpoints["expected_trials"] == 320
    assert checkpoints["validation"]["repository_tests_passed"] == 691
    assert checkpoints["validation"]["application_coverage_percent"] >= 80.0
    assert [row["id"] for row in checkpoints["checkpoints"]] == [
        "holdout-complete",
        "discovery-wave-1-complete",
        "live-progress-159",
        "discovery-complete",
        "final-complete",
        "evaluator-audit-invalidated",
    ]
    holdout = checkpoints["checkpoints"][0]
    assert holdout["result_trials"] == 48
    assert set(holdout["families"]) == set(DATA.load_families())
    final = DATA.load_json(
        reports / "20260717-papers-consult-gpt53-spark-01-final.json"
    )
    assert final["complete"] is True
    assert final["result_trials"] == final["expected_trials"] == 320
    assert final["records_sha256_values"] == [checkpoints["records_sha256"]]
    assert len(final["trials"]) == 320
    current = checkpoints["current_status"]
    assert current == {
        "checkpoint_id": "evaluator-audit-invalidated",
        "structurally_complete": True,
        "evaluation_complete": False,
        "ranking_eligible": False,
        "winner": None,
        "reason": "Provider quota and execution failures left only 32 complete final responses.",
    }
    audit = DATA.load_json(
        reports / "20260717-papers-consult-gpt53-spark-01-audit-v2.json"
    )
    assert audit["structurally_complete"] is True
    assert audit["evaluation_complete"] is False
    assert audit["ranking_eligible"] is False
    assert audit["winner"] is None
    assert audit["evaluable_trials"] == 32
    assert len(audit["trials"]) == 320
    audit_checkpoint = checkpoints["checkpoints"][-1]
    assert audit_checkpoint["validation"]["corrected_oracles_passed"] == 320
    assert audit_checkpoint["validation"]["repository_tests_passed"] == 1826
    assert audit_checkpoint["validation"]["application_coverage_percent"] >= 80.0
    manual = (
        reports / "20260717-papers-consult-gpt53-spark-01-manual-review.md"
    ).read_text(encoding="utf-8")
    assert "Semantic pass | 0" in manual
    assert "Hard-question responses available | 0" in manual
    assert "Current status: invalid for comparison" in log.read_text(encoding="utf-8")
    assert "do not rewrite prior observations" in (ROOT / "README.md").read_text(
        encoding="utf-8"
    )


@pytest.mark.parametrize("mode", GENERATOR.MODES)
def test_runner_dry_run_arguments_are_cross_platform(mode: str) -> None:
    arguments = [
        "--dataset",
        "graphrag-papers-40",
        "--family",
        "legacy",
        "--mode",
        mode,
        "--cohort",
        "holdout",
        "--dry-run",
    ]
    parsed = RUNNER.parse_args(arguments)
    assert parsed.mode == mode
    assert parsed.dry_run is True
