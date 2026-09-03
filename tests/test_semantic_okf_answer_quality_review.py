"""Tests for solution-agnostic Semantic OKF answer-quality review."""

from __future__ import annotations

import json
from pathlib import Path
import sys

import pytest


EVALUATION_ROOT = (
    Path(__file__).resolve().parents[1] / "evaluations" / "semantic-okf-datasets"
)
sys.path.insert(0, str(EVALUATION_ROOT))

import answer_quality_review as REVIEW  # noqa: E402


def question() -> dict:
    """Return a valid frozen semantic-rubric fixture."""

    return {
        "id": "q001",
        "question": "What differs, and what must not be conflated?",
        "semantic_rubric": {
            "required_points": [
                "Explain the first mechanism.",
                "Explain the second mechanism.",
            ]
        },
    }


def truth() -> dict:
    """Return a valid hard-ground-truth fixture with mechanical metadata."""

    return {
        "id": "q001",
        "authoritative_evidence": [
            {
                "path": "secret/original.md",
                "file_sha256": "a" * 64,
                "start_char": 10,
                "end_char": 99,
            }
        ],
        "ground_truth": {
            "answer_claims": [
                {"id": "a1", "statement": "The first mechanism measures alpha."},
                {"id": "a2", "statement": "The second mechanism measures beta."},
            ],
            "important_negatives": [
                {"id": "n1", "statement": "Alpha and beta are not one scale."}
            ],
        },
    }


def response(summary: str = "Alpha and beta measure different things.") -> dict:
    """Return a valid response containing solution-specific fields."""

    return {
        "question_id": "q001",
        "answer": {
            "summary": summary + " [0]",
            "claims": [
                {
                    "statement": "The first mechanism measures alpha. [3]",
                    "evidence_indices": [0],
                },
                {
                    "statement": "The second mechanism measures beta.",
                    "evidence_indices": [1],
                },
            ],
        },
        "evidence": [
            {
                "source_path": "original/file.md",
                "record_sha256": "b" * 64,
                "locator": {"kind": "record", "target": "record.body"},
            }
        ],
    }


def judgment(
    packet: dict,
    *,
    required: list[str] | None = None,
    negative: str = "respected",
    correctness: str = "correct",
) -> dict:
    """Return a valid two-answer reviewer result."""

    statuses = required or ["satisfied", "satisfied"]
    return {
        "schemaVersion": REVIEW.SCHEMA_VERSION,
        "packetSha256": REVIEW.sha256_bytes(REVIEW.canonical_json_bytes(packet)),
        "judgments": [
            {
                "answerLabel": label,
                "requiredPointStatuses": list(statuses),
                "importantNegativeStatuses": [negative],
                "materialCorrectness": correctness,
                "defectCodes": [],
            }
            for label in ("answer-a", "answer-b")
        ],
    }


def write_task(root: Path) -> None:
    """Write one frozen task fixture."""

    tests = root / "q001" / "tests"
    tests.mkdir(parents=True)
    (tests / "question.json").write_text(json.dumps(question()), encoding="utf-8")
    (tests / "hard-ground-truth.json").write_text(json.dumps(truth()), encoding="utf-8")


def write_job(root: Path, answer: dict) -> None:
    """Write one minimal completed Harbor/Pi job fixture."""

    root.mkdir(parents=True)
    (root / "lock.json").write_text(json.dumps({"trials": [{}]}), encoding="utf-8")
    trial = root / "q001__abc123"
    (trial / "artifacts").mkdir(parents=True)
    (trial / "result.json").write_text(
        json.dumps({"exception_info": None, "task_checksum": "c" * 64}),
        encoding="utf-8",
    )
    final_text = json.dumps(answer)
    events = [
        {"type": "session", "version": 3},
        {
            "type": "message_end",
            "message": {
                "role": "assistant",
                "content": [{"type": "text", "text": final_text}],
            },
        },
    ]
    (trial / "artifacts" / "pi.jsonl").write_text(
        "".join(json.dumps(event) + "\n" for event in events), encoding="utf-8"
    )


def test_task_contract_exposes_quality_truth_but_no_file_mechanics() -> None:
    contract = REVIEW.task_quality_contract(question(), truth())
    serialized = json.dumps(contract, sort_keys=True)

    assert contract["question"] == question()["question"]
    assert len(contract["requiredPoints"]) == 2
    assert len(contract["referenceClaims"]) == 2
    assert "secret/original.md" not in serialized
    assert "file_sha256" not in serialized
    assert "start_char" not in serialized
    assert "q001" not in serialized


def test_task_contract_fails_closed_without_semantic_quality_fields() -> None:
    broken = question()
    broken["semantic_rubric"]["required_points"] = []
    with pytest.raises(REVIEW.ReviewError, match="required_points"):
        REVIEW.task_quality_contract(broken, truth())

    broken_truth = truth()
    broken_truth["ground_truth"]["important_negatives"] = []
    with pytest.raises(REVIEW.ReviewError, match="important_negatives"):
        REVIEW.task_quality_contract(question(), broken_truth)


def test_rubric_only_contract_is_explicit_and_does_not_invent_negatives() -> None:
    contract = REVIEW.task_quality_contract(question())

    assert contract["contractBasis"] == "semantic-rubric-only"
    assert [item["statement"] for item in contract["referenceClaims"]] == [
        "Explain the first mechanism.",
        "Explain the second mechanism.",
    ]
    assert contract["importantNegatives"] == []


def test_answer_projection_is_invariant_to_evidence_and_locator_storage() -> None:
    first = response()
    second = response()
    second["question_id"] = "different"
    second["answer"]["claims"][0]["evidence_indices"] = [99, 100]
    second["evidence"] = [
        {
            "source_path": "rewritten/storage/location.md",
            "record_sha256": "f" * 64,
            "locator": {"kind": "character-range", "start": 1, "end": 2},
        }
    ]

    assert REVIEW.normalized_answer(first) == REVIEW.normalized_answer(second)
    assert "[0]" not in REVIEW.normalized_answer(first)["summary"]
    assert "[3]" not in REVIEW.normalized_answer(first)["claims"][0]["statement"]


def test_answer_projection_retains_invalid_complete_responses_as_quality_failures() -> None:
    projected = REVIEW.normalized_answer(
        {"question_id": "q001", "answer": None, "evidence": []}
    )

    assert projected == {
        "summary": "No semantic answer content was emitted.",
        "claims": [
            {"ordinal": 1, "statement": "No semantic answer content was emitted."}
        ],
    }


def test_review_packet_digest_changes_with_prose_not_solution_metadata() -> None:
    contract = REVIEW.task_quality_contract(question(), truth())
    first = REVIEW.normalized_answer(response())
    mechanically_different = response()
    mechanically_different["evidence"][0]["source_path"] = "other.md"
    second = REVIEW.normalized_answer(mechanically_different)

    packet_a = REVIEW.review_packet(contract, [first, second])
    packet_b = REVIEW.review_packet(contract, [first, REVIEW.normalized_answer(response())])
    assert REVIEW.canonical_json_bytes(packet_a) == REVIEW.canonical_json_bytes(packet_b)

    changed = REVIEW.normalized_answer(response("This answer contradicts the contract."))
    packet_c = REVIEW.review_packet(contract, [first, changed])
    assert REVIEW.canonical_json_bytes(packet_a) != REVIEW.canonical_json_bytes(packet_c)


def test_prompt_contains_no_known_solution_mechanics() -> None:
    contract = REVIEW.task_quality_contract(question(), truth())
    normalized = REVIEW.normalized_answer(response())
    prompt = REVIEW.render_prompt(REVIEW.review_packet(contract, [normalized, normalized]))

    for forbidden in (
        "original/file.md",
        "record_sha256",
        "record.body",
        "evidence_indices",
        "mechanical reward",
        "q001",
    ):
        assert forbidden not in prompt
    assert "true but adjacent result" in prompt
    assert "does not substitute" in prompt


def test_result_validation_rejects_model_authored_shape_or_count_drift() -> None:
    contract = REVIEW.task_quality_contract(question(), truth())
    normalized = REVIEW.normalized_answer(response())
    packet = REVIEW.review_packet(contract, [normalized, normalized])
    valid = judgment(packet)
    assert REVIEW.validate_judgment(valid, packet)["judgments"][0][
        "materialCorrectness"
    ] == "correct"

    invalid = json.loads(json.dumps(valid))
    invalid["judgments"][0]["requiredPointStatuses"] = ["satisfied"]
    with pytest.raises(REVIEW.ReviewError, match="required-point"):
        REVIEW.validate_judgment(invalid, packet)

    invalid = json.loads(json.dumps(valid))
    invalid["score"] = 100
    with pytest.raises(REVIEW.ReviewError, match="top-level"):
        REVIEW.validate_judgment(invalid, packet)


def test_conservative_consensus_uses_worst_status_and_reports_agreement() -> None:
    first = judgment(
        REVIEW.review_packet(
            REVIEW.task_quality_contract(question(), truth()),
            [REVIEW.normalized_answer(response()), REVIEW.normalized_answer(response())],
        )
    )["judgments"][0]
    second = json.loads(json.dumps(first))
    second["requiredPointStatuses"] = ["partial", "satisfied"]
    second["importantNegativeStatuses"] = ["violated"]
    second["materialCorrectness"] = "minor-error"
    second["defectCodes"] = ["scope-imprecision"]

    consensus = REVIEW.conservative_consensus([first, second])
    assert consensus["requiredPointStatuses"] == ["partial", "satisfied"]
    assert consensus["requiredPointCoverage"] == 0.75
    assert consensus["importantNegativeStatuses"] == ["violated"]
    assert consensus["materialCorrectness"] == "minor-error"
    assert consensus["casePass"] is False
    assert consensus["orientationAgreement"] == 0.25


def test_pareto_comparison_does_not_hide_mixed_quality_movement() -> None:
    baseline = {
        "requiredPointCoverage": 0.75,
        "importantNegativeStatuses": ["respected"],
        "materialCorrectness": "correct",
        "casePass": False,
    }
    candidate = {
        "requiredPointCoverage": 1.0,
        "importantNegativeStatuses": ["respected"],
        "materialCorrectness": "major-error",
        "casePass": False,
    }
    assert REVIEW._comparison_outcome(baseline, candidate) == "mixed"
    candidate["requiredPointCoverage"] = 0.5
    assert REVIEW._comparison_outcome(baseline, candidate) == "regressed"


def test_prepare_is_counterbalanced_append_only_and_digest_validated(tmp_path: Path) -> None:
    task_root = tmp_path / "tasks"
    write_task(task_root)
    first_job = tmp_path / "first-job"
    second_job = tmp_path / "second-job"
    write_job(first_job, response("First answer."))
    write_job(second_job, response("Second answer."))
    output = tmp_path / "review"

    result = REVIEW.prepare_review(
        task_root,
        [("canonical", first_job), ("candidate", second_job)],
        output,
    )
    manifest = REVIEW.validate_manifest(Path(result["manifestPath"]))
    assert result["caseCount"] == 1
    assert result["reviewCallCount"] == 2
    assert [item["orientation"] for item in manifest["prompts"]] == [
        "forward",
        "reverse",
    ]
    assert manifest["prompts"][0]["labelMap"] == {
        "answer-a": "canonical",
        "answer-b": "candidate",
    }
    assert manifest["prompts"][1]["labelMap"] == {
        "answer-a": "candidate",
        "answer-b": "canonical",
    }
    with pytest.raises(REVIEW.ReviewError, match="overwrite"):
        REVIEW.prepare_review(
            task_root,
            [("canonical", first_job), ("candidate", second_job)],
            output,
        )


def test_report_derives_scores_from_statuses_and_writes_aggregate_table(
    tmp_path: Path,
) -> None:
    task_root = tmp_path / "tasks"
    write_task(task_root)
    first_job = tmp_path / "first-job"
    second_job = tmp_path / "second-job"
    write_job(first_job, response("First answer."))
    write_job(second_job, response("Second answer."))
    output = tmp_path / "review"
    prepared = REVIEW.prepare_review(
        task_root,
        [("canonical", first_job), ("candidate", second_job)],
        output,
    )
    manifest_path = Path(prepared["manifestPath"])
    manifest = REVIEW.validate_manifest(manifest_path)
    for item in manifest["prompts"]:
        packet = REVIEW.load_json(output / item["packetPath"])
        result = judgment(packet)
        if item["orientation"] == "forward":
            result["judgments"][1]["requiredPointStatuses"] = [
                "missing",
                "satisfied",
            ]
            result["judgments"][1]["materialCorrectness"] = "major-error"
        else:
            result["judgments"][0]["requiredPointStatuses"] = [
                "missing",
                "satisfied",
            ]
            result["judgments"][0]["materialCorrectness"] = "major-error"
        path = output / item["resultPath"]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(REVIEW.canonical_json_bytes(result))

    report = REVIEW.build_report(manifest_path)
    assert report["aggregates"]["canonical"]["casePassCount"] == 1
    assert report["aggregates"]["candidate"]["meanRequiredPointCoverage"] == 0.5
    assert report["pairedSecondArmOutcomes"] == {"regressed": 1}

    written = REVIEW.write_report(
        manifest_path, output / "report.json", output / "report.table.md"
    )
    table = Path(written["tablePath"]).read_text(encoding="utf-8")
    assert "solution-agnostic" in table.lower()
    assert "Full-quality cases | 1/1 | 0/1" in table
    assert "native mechanical reward" in table


def test_population_review_counterbalances_all_arms_and_renders_rows(
    tmp_path: Path,
) -> None:
    task_root = tmp_path / "tasks"
    write_task(task_root)
    jobs = []
    for ordinal, name in enumerate(("canonical", "strategy-one", "strategy-two"), 1):
        path = tmp_path / name
        write_job(path, response(f"Answer {ordinal}."))
        jobs.append((name, path))
    output = tmp_path / "population"
    prepared = REVIEW.prepare_review(task_root, jobs, output)
    manifest_path = Path(prepared["manifestPath"])
    manifest = REVIEW.validate_manifest(manifest_path)

    assert manifest["prompts"][0]["labelMap"] == {
        "answer-001": "canonical",
        "answer-002": "strategy-one",
        "answer-003": "strategy-two",
    }
    assert manifest["prompts"][1]["labelMap"] == {
        "answer-001": "strategy-two",
        "answer-002": "strategy-one",
        "answer-003": "canonical",
    }
    for item in manifest["prompts"]:
        packet = REVIEW.load_json(output / item["packetPath"])
        result = {
            "schemaVersion": REVIEW.SCHEMA_VERSION,
            "packetSha256": REVIEW.sha256_bytes(REVIEW.canonical_json_bytes(packet)),
            "judgments": [
                {
                    "answerLabel": answer["answerLabel"],
                    "requiredPointStatuses": ["satisfied", "satisfied"],
                    "importantNegativeStatuses": ["respected"],
                    "materialCorrectness": "correct",
                    "defectCodes": [],
                }
                for answer in packet["answers"]
            ],
        }
        path = output / item["resultPath"]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(REVIEW.canonical_json_bytes(result))

    report = REVIEW.build_report(manifest_path)
    assert report["armOrder"] == ["canonical", "strategy-one", "strategy-two"]
    assert report["pairedOutcomesByArm"] == {
        "strategy-one": {"tie": 1},
        "strategy-two": {"tie": 1},
    }
    table = REVIEW.render_report_table(report)
    assert "Solution-agnostic population" in table
    assert "| strategy-one |" in table
    assert "tie=1" in table

    consolidated = REVIEW.build_consolidated_report([("q001-q001", manifest_path)])
    assert consolidated["cohortCount"] == 1
    assert consolidated["strategyRowCount"] == 3
    assert consolidated["rows"][1]["semanticGate"] == "non-regressed"
    consolidated_table = REVIEW.render_consolidated_table(consolidated)
    assert "q001-q001" in consolidated_table
    assert "No cross-cohort winner is declared" in consolidated_table
