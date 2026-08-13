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
import candidate_family as CANDIDATES  # noqa: E402
import generate_harbor_tasks as GENERATOR  # noqa: E402
import run_harbor as RUNNER  # noqa: E402
import summarize_consult_campaign as SUMMARY  # noqa: E402
import validate_harbor_tasks as VALIDATOR  # noqa: E402


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


def test_registry_validates_all_datasets_and_strategy_pairs() -> None:
    reports = {identifier: DATA.validate_dataset(identifier) for identifier in DATA.available_datasets()}
    assert set(reports) == {
        "astro-40",
        "graphrag-papers-40",
        "quantum-error-correction-papers-40",
    }
    assert reports["astro-40"]["source_file_count"] == 416
    assert reports["graphrag-papers-40"]["source_file_count"] == 31
    assert reports["quantum-error-correction-papers-40"][
        "source_file_count"
    ] == 15
    assert all(report["question_count"] == 40 for report in reports.values())
    assert all(report["hard_question_count"] == 10 for report in reports.values())
    assert all(len(report["families"]) == 8 for report in reports.values())
    assert reports["graphrag-papers-40"]["reference_bundle_present"] is True
    assert reports["quantum-error-correction-papers-40"][
        "reference_bundle_present"
    ] is True
    assert reports["astro-40"]["reference_bundle_present"] is False
    assert reports["graphrag-papers-40"]["semantic_rubric_count"] == 30
    assert reports["quantum-error-correction-papers-40"][
        "semantic_rubric_count"
    ] == 40
    assert reports["astro-40"]["semantic_rubric_count"] == 0
    assert reports["graphrag-papers-40"]["reference_answer_count"] == 40
    assert reports["quantum-error-correction-papers-40"][
        "reference_answer_count"
    ] == 0
    assert reports["astro-40"]["reference_answer_count"] == 0


def test_harbor_generation_normalizes_both_arxiv_identifier_widths() -> None:
    assert GENERATOR.paper_document_id("paper-1208-0928v2") == "1208.0928v2"
    assert GENERATOR.paper_document_id("paper-2508-05095v3") == "2508.05095v3"


def test_dataset_schema_versions_policy_and_reference_answers() -> None:
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads((ROOT / "dataset.schema.json").read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)

    legacy = DATA.load_dataset("astro-40")
    current = DATA.load_dataset("graphrag-papers-40")
    qec = DATA.load_dataset("quantum-error-correction-papers-40")
    validator.validate(legacy)
    validator.validate(current)
    validator.validate(qec)

    missing_policy = json.loads(json.dumps(current))
    missing_policy.pop("evaluation_policy")
    with pytest.raises(jsonschema.ValidationError):
        validator.validate(missing_policy)

    missing_answers = json.loads(json.dumps(current))
    missing_answers.pop("reference_answers")
    with pytest.raises(jsonschema.ValidationError):
        validator.validate(missing_answers)

    version_1_1 = json.loads(json.dumps(current))
    version_1_1["schema_version"] = "semantic-okf-evaluation-dataset/1.1"
    version_1_1.pop("reference_answers")
    validator.validate(version_1_1)

    answers_on_version_1_1 = json.loads(json.dumps(version_1_1))
    answers_on_version_1_1["reference_answers"] = current[
        "reference_answers"
    ]
    with pytest.raises(jsonschema.ValidationError):
        validator.validate(answers_on_version_1_1)

    policy_on_legacy = json.loads(json.dumps(legacy))
    policy_on_legacy["evaluation_policy"] = current["evaluation_policy"]
    with pytest.raises(jsonschema.ValidationError):
        validator.validate(policy_on_legacy)


def test_reference_answers_cover_every_question_and_historical_response_once() -> None:
    dataset = DATA.load_dataset("graphrag-papers-40")
    collection = DATA.load_json(
        DATA.pinned_path(
            dataset["reference_answers"],
            "graphrag-papers-40 reference answers",
        )
    )
    expected_ids = [f"q{index:03d}" for index in range(1, 41)]
    reviews = collection["reviews"]
    validations = collection["validations"]

    assert [row["question_id"] for row in reviews] == expected_ids
    assert [row["question_id"] for row in validations] == expected_ids
    assert all(row["status"] == "pass" for row in validations)
    assert all(
        row["proposed_response"]["question_id"] == row["question_id"]
        and row["proposed_response"]["answer"] is not None
        and SCORE.validate_contract(
            row["proposed_response"],
            row["question_id"],
        )[0]
        and SCORE.reference_validity(row["proposed_response"])
        for row in reviews
    )

    historical_ids = [
        response_id
        for row in reviews
        for response_id in row["historical_review"][
            "reviewed_response_ids"
        ]
    ]
    assert len(historical_ids) == len(set(historical_ids)) == 175
    assert collection["historical_response_count"] == 175
    assert collection["semantic_target_count"] == 200
    assert collection["proposed_claim_count"] == 243
    assert collection["evidence_row_count"] == 409
    assert collection["hard_anchor_count"] == 94
    assert collection["second_pass_review_count"] == 40
    assert collection["second_pass_producing_agent_count"] == 40
    assert collection["second_pass_keep_count"] == 26
    assert collection["second_pass_revise_count"] == 14
    assert collection["second_pass_validation_status"] == "pass"
    assert all(
        row["second_pass_review_agent"]
        == f"/root/{row['question_id']}_second_pass"
        and row["second_pass_verdict"] in {"keep", "revise"}
        and len(row["second_pass_verdict_sha256"]) == 64
        and row["final_answer_source"]
        == (
            "second-pass-replacement"
            if row["second_pass_verdict"] == "revise"
            else "first-pass-confirmed"
        )
        for row in reviews
    )

    no_history = {"q028", *(f"q{index:03d}" for index in range(31, 41))}
    assert all(
        row["historical_review"]["response_count"] == 0
        for row in reviews
        if row["question_id"] in no_history
    )


def test_reference_answer_second_pass_report_covers_every_assignment() -> None:
    report = DATA.load_json(
        ROOT
        / "reports/"
        "20260724-graphrag-papers-40-second-pass-review.json"
    )
    collection = DATA.load_json(
        ROOT / "reports/20260724-graphrag-papers-40-best-answers.json"
    )
    expected_ids = [f"q{index:03d}" for index in range(1, 41)]
    revised = {
        "q009",
        "q010",
        "q012",
        "q015",
        "q021",
        "q026",
        "q027",
        "q028",
        "q029",
        "q030",
        "q031",
        "q036",
        "q037",
        "q040",
    }

    assert report["schema_version"] == (
        "graphrag-best-answer-second-pass-report/1.0"
    )
    assert report["report_kind"] == (
        "curated-reference-answer-audit-not-live-trials"
    )
    assert report["question_count"] == report["agent_assignment_count"] == 40
    assert report["historical_response_count"] == 175
    assert report["semantic_target_count"] == 200
    assert report["hard_anchor_count"] == 94
    assert report["keep_count"] == 26
    assert report["revise_count"] == len(revised) == 14
    assert report["confidence_counts"] == {"high": 40}
    assert report["validation_status"] == "pass"
    assert set(report["revised_question_ids"]) == revised
    assert [row["question_id"] for row in report["reviews"]] == expected_ids
    assert len(
        {row["agent_assignment"] for row in report["reviews"]}
    ) == 40

    final_reviews = {
        row["question_id"]: row for row in collection["reviews"]
    }
    for row in report["reviews"]:
        question_id = row["question_id"]
        response = final_reviews[question_id]["proposed_response"]
        response_sha256 = hashlib.sha256(
            json.dumps(
                response,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
                allow_nan=False,
            ).encode("utf-8")
        ).hexdigest()
        assert row["verdict"] == (
            "revise" if question_id in revised else "keep"
        )
        assert row["confidence"] == "high"
        assert row["final_answer_source"] == (
            "second-pass-replacement"
            if question_id in revised
            else "first-pass-confirmed"
        )
        assert row["final_response_sha256"] == response_sha256
        assert row["final_evidence_count"] == len(response["evidence"])
        assert row["validation_status"] == "pass"


def test_current_metrics_report_recalculates_every_raw_trial_without_answer_leakage() -> None:
    report_path = (
        ROOT
        / "reports/"
        "20260724-graphrag-papers-40-current-metrics-table.json"
    )
    report_text = report_path.read_text(encoding="utf-8")
    report = json.loads(report_text)
    summary = report["summary"]
    trials = report["raw_trials"]
    references = report["reference_calibrations"]

    assert report["schema_version"] == (
        "graphrag-current-metrics-evaluation-table/1.1"
    )
    assert report["new_model_calls"] == 0
    assert summary["raw_harbor_trial_count"] == len(trials) == 516
    assert summary["raw_trials_rescored_with_current_metrics"] == 516
    assert summary["primary_raw_harbor_trial_count"] == 180
    assert summary["additional_raw_harbor_trial_count"] == 336
    assert summary["complete_parent_job_trial_count"] == 503
    assert summary["incomplete_parent_job_trial_count"] == 13
    assert summary["incomplete_parent_job_count"] == 4
    assert summary["reviewable_raw_response_count"] == 175
    assert summary["primary_reviewable_raw_response_count"] == 143
    assert summary["resolved_historical_raw_response_count"] == 32
    assert summary["unreviewed_answer_emitted_count"] == 34
    assert summary["legacy_reviewable_response_count"] == 0
    assert summary["reviewable_response_count"] == 175
    assert summary["current_mechanical_qualification_count"] == 115
    assert summary["empirically_covered_question_count"] == 29
    assert summary["reference_mechanical_qualification_count"] == 40
    assert len({row["response_id"] for row in trials}) == 516
    assert report["metric_contract"]["trial_source_roots"] == [
        "evaluations/semantic-okf-datasets/results",
        (
            "evaluations/semantic-okf-tika-mallet-tantivy/generated/"
            "trace-distillation"
        ),
        (
            "evaluations/semantic-okf-datasets/generated/campaigns/"
            "20260717-papers-consult-gpt53-spark-01/runs"
        ),
        (
            "evaluations/semantic-okf-datasets/generated/campaigns/"
            "20260717-papers-consult-gpt53-spark-02/runs"
        ),
    ]
    distillation = [
        row
        for row in trials
        if row["artifact_root"].endswith("trace-distillation")
    ]
    assert len(distillation) == 15
    assert {
        row["question_id"] for row in distillation
    } == {"q002", "q003", "q004"}
    assert sum(
        row["current_metrics"]["mechanical_qualification_gate"] == 1.0
        for row in distillation
    ) == 12
    assert sum(
        row["artifact_root"].endswith(
            "20260717-papers-consult-gpt53-spark-01/runs"
        )
        for row in trials
    ) == 320
    assert sum(
        row["artifact_root"].endswith(
            "20260717-papers-consult-gpt53-spark-02/runs"
        )
        for row in trials
    ) == 1
    assert report["legacy_historical_responses"] == []
    strategies = {
        row["strategy"]: row for row in report["strategies"]
    }
    assert set(strategies) == {
        "adaptive",
        "classical",
        "embeddings",
        "ensemble",
        "entity-graph",
        "graphify",
        "legacy",
        "tika-mallet-bounded-v4",
        "tika-mallet-canonical-text",
        "tika-mallet-canonical-text-v2",
        "tika-mallet-canonical-text-v3",
        "tika-mallet-tantivy-canonical-text",
        "turso",
    }
    assert strategies["adaptive"]["trial_count"] == 41
    assert strategies["ensemble"]["answer_emitted_count"] == 0
    assert strategies["graphify"]["answer_emitted_count"] == 0
    tantivy = strategies["tika-mallet-tantivy-canonical-text"]
    assert tantivy["trial_count"] == 154
    assert tantivy["answer_emitted_count"] == 141
    assert tantivy["mechanical_qualification_count"] == 88
    assert tantivy["semantically_reviewed_response_count"] == 107
    assert [row["question_id"] for row in report["questions"]] == [
        f"q{index:03d}" for index in range(1, 41)
    ]
    assert [row["question_id"] for row in references] == [
        f"q{index:03d}" for index in range(1, 41)
    ]
    assert all(
        row["current_diagnostics"]["schema_version"]
        == "semantic-okf-harbor-redacted-diagnostics/3.0"
        and row["current_metrics"]["reward"]
        == pytest.approx(
            row["current_metrics"]["mechanical_qualification_gate"]
            * row["current_metrics"]["mechanical_utility"]
        )
        for row in trials
    )
    assert all(
        row["semantic_verdict"] == "pass"
        and row["current_metrics"]["mechanical_qualification_gate"] == 1.0
        for row in references
    )
    assert '"answer_text"' not in report_text


def test_response_coverage_audit_separates_reviewed_and_unreviewed_traces() -> None:
    report = json.loads(
        (
            ROOT
            / "reports/"
            "20260724-graphrag-papers-40-response-coverage-audit.json"
        ).read_text(encoding="utf-8")
    )

    assert report["schema_version"] == (
        "graphrag-response-coverage-audit/1.1"
    )
    assert report["raw_harbor_trial_count"] == 516
    assert report["primary_raw_harbor_trial_count"] == 180
    assert report["additional_raw_harbor_trial_count"] == 336
    assert report["raw_complete_response_count"] == 189
    assert report["semantically_reviewed_raw_response_count"] == 174
    assert report["semantically_unreviewed_raw_response_count"] == 15
    assert report["historical_manually_reviewed_response_count"] == 32
    assert report["resolved_historical_raw_response_count"] == 31
    assert report["legacy_historical_response_count"] == 1
    assert report["reviewable_response_count"] == 190
    assert report["semantically_reviewed_response_count"] == 175
    assert report["semantic_verdict_counts"] == {
        "fail": 4,
        "not-reviewed": 15,
        "partial": 168,
        "pass": 3,
    }
    assert report["empirically_covered_question_count"] == 29
    assert report["full_dataset_claim_eligible"] is False


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
        source,
        dataset["question_format"],
        rubrics["q003"],
        dataset["evaluation_policy"],
    )
    instruction = GENERATOR.instruction(
        question, "consult-only", "legacy", DATA.load_families()["legacy"]
    )

    assert question["minimum_document_count"] == 6
    assert len(question["semantic_rubric"]["required_points"]) == 4
    assert question["evaluation_policy"] == {
        "qrel_scope": "non-exhaustive-focus-set",
        "minimum_document_gate_basis": "valid-evidence-document-count",
        "semantic_ranking_gate": "manual-review-required",
        "full_dataset_coverage_required": True,
    }
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
        GENERATOR.normalized_question(
            row,
            dataset["question_format"],
            evaluation_policy=dataset["evaluation_policy"],
        )
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
    assert diagnostics["semantic_correctness"] == "manual-review-required"
    assert diagnostics["semantic_ranking_eligible"] is False


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


def test_runner_binds_bounded_concurrency_to_trials_and_agent() -> None:
    config = RUNNER.job_config(
        output=Path("/tmp/results/job"),
        tasks_path=Path("/tmp/tasks/holdout"),
        task_ids=["q005", "q010", "q015"],
        attempts=1,
        skills=[Path("/tmp/skills/consult")],
        resource=Path("/tmp/knowledge"),
        resource_target="/knowledge",
        auth_source="/tmp/auth",
        hf_cache=None,
        concurrency=3,
    )

    assert config["n_concurrent_trials"] == 3
    assert config["agents"][0]["n_concurrent"] == 3


def test_inactive_candidate_family_is_hash_bound_and_consult_only() -> None:
    specification = (
        REPO
        / "evaluations/semantic-okf-tika-mallet/canonical/graphrag-papers-40"
        / "harbor-candidate.json"
    )
    family, binding = CANDIDATES.resolve(
        "graphrag-papers-40",
        "tika-mallet",
        "consult-only",
        specification,
    )

    assert "tika-mallet" not in DATA.load_families()
    assert family == {
        "build_script": "build_semantic_okf_tika_mallet.py",
        "build_skill": "build-semantic-okf-tika-mallet",
        "consult_skill": "consult-semantic-okf-tika-mallet",
        "requires_hf_cache": False,
        "uses_plan": True,
        "validate_script": "validate_semantic_okf_tika_mallet.py",
    }
    assert binding is not None
    assert binding["candidate_id"] == "tika-mallet"
    assert binding["allowed_modes"] == ["consult-only"]
    assert binding["specification_sha256"] == DATA.sha256_file(specification)
    assert len(binding["family_contract_sha256"]) == 64
    CANDIDATES.verify_manifest({"candidate_family": binding}, binding)

    drifted = json.loads(json.dumps(binding))
    drifted["specification_sha256"] = "0" * 64
    with pytest.raises(
        CANDIDATES.CandidateFamilyError,
        match="binding drift",
    ):
        CANDIDATES.verify_manifest({"candidate_family": drifted}, binding)
    with pytest.raises(
        CANDIDATES.CandidateFamilyError,
        match="does not permit execution mode",
    ):
        CANDIDATES.resolve(
            "graphrag-papers-40",
            "tika-mallet",
            "build-consult",
            specification,
        )


def test_consult_only_instruction_requires_skill_first_bounded_access() -> None:
    row = {
        "id": "q999",
        "question": "What does the snapshot support?",
        "minimum_document_count": 4,
    }
    family = {
        "consult_skill": "consult-semantic-okf-tika-mallet",
    }

    rendered = GENERATOR.instruction(row, "consult-only", "tika-mallet", family)

    assert "Before accessing `/knowledge`, read that skill" in rendered
    assert "`answer-pack` then `finalize-answer` workflow exactly" in rendered
    assert "Do not use `search`, `batch-search`, ad hoc snapshot reads" in rendered
    assert "Use evidence from at least 4 independent relevant papers." in rendered
    assert "prefer up to two additional independently relevant papers" in rendered


def test_tika_mallet_build_instruction_names_both_closed_plans() -> None:
    row = {
        "id": "q999",
        "question": "What does the new snapshot support?",
    }
    family = {
        "build_skill": "build-semantic-okf-tika-mallet",
        "consult_skill": "consult-semantic-okf-tika-mallet-tantivy",
        "uses_plan": True,
        "validate_script": "validate_semantic_okf_tika_mallet.py",
    }

    rendered = GENERATOR.instruction(
        row,
        "build-consult",
        "tika-mallet-tantivy",
        family,
    )

    assert "/dataset/ingestion-plan.json" in rendered
    assert "/dataset/retrieval-plan.json" in rendered
    assert "/dataset/manifest.json" not in rendered
    assert "/dataset/plan.json" not in rendered
    VALIDATOR.mode_boundaries(rendered, "build-consult", family, "q999")


def test_bounded_candidate_is_separately_hash_bound_and_uses_one_compiler() -> None:
    specification = (
        REPO
        / "evaluations/semantic-okf-tika-mallet/canonical/graphrag-papers-40"
        / "harbor-candidate-bounded-v4.json"
    )
    family, binding = CANDIDATES.resolve(
        "graphrag-papers-40",
        "tika-mallet",
        "consult-only",
        specification,
    )
    row = {
        "id": "q999",
        "question": "What does the snapshot support?",
        "minimum_document_count": 4,
    }
    rendered = GENERATOR.instruction(
        row,
        "consult-only",
        "tika-mallet",
        family,
    )

    assert family["consult_skill"] == (
        "consult-semantic-okf-tika-mallet-bounded"
    )
    assert binding is not None
    assert binding["specification_path"].endswith(
        "harbor-candidate-bounded-v4.json"
    )
    assert "run exactly one `scripts/bounded_answer.py` invocation" in rendered
    assert "`--minimum-sources 4`" in rendered
    assert "`--max-sources 6`" in rendered
    assert "Do not list, grep, search, or read the snapshot" in rendered
    assert "do not run a second compiler command" in rendered


def test_runner_accepts_an_explicit_candidate_task_root(tmp_path: Path) -> None:
    root = tmp_path / "candidate-tasks"
    task = root / "holdout/q005/task.toml"
    task.parent.mkdir(parents=True)
    task.write_text('version = "1.0"\n', encoding="utf-8")
    manifest = {
        "dataset_id": "graphrag-papers-40",
        "family": "tika-mallet",
        "mode": "consult-only",
    }
    write_json(root / "manifest.json", manifest)

    tasks_path, identifiers, observed_manifest = RUNNER.checked_tasks(
        "graphrag-papers-40",
        "tika-mallet",
        "consult-only",
        "holdout",
        ["q005"],
        root,
    )

    assert tasks_path == root.resolve() / "holdout"
    assert identifiers == ["q005"]
    assert observed_manifest == manifest


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
    assert adaptive["token_usage"]["result_trials"] == {
        "observed_trials": 1,
        "cache_observed_trials": 1,
        "input_tokens_including_cache": {
            "total": 100,
            "mean": 100.0,
        },
        "cache_tokens_reported_separately": {
            "total": 50,
            "mean": 50.0,
        },
        "output_tokens": {"total": 20, "mean": 20.0},
        "total_tokens": {"total": 120, "mean": 120.0},
    }
    assert adaptive["token_usage"]["complete_response_trials"][
        "observed_trials"
    ] == 0
    rendered = SUMMARY.markdown(report)
    assert "adaptive" in rendered
    assert "INVALID FOR COMPARISON" in rendered
    assert "## Consultation token use" in rendered
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
