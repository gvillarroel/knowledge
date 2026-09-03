"""Adversarial tests for isolated replicated semantic answer review."""

from __future__ import annotations

import json
from pathlib import Path
import sys

import pytest


EVALUATION_ROOT = (
    Path(__file__).resolve().parents[1] / "evaluations" / "semantic-okf-datasets"
)
sys.path.insert(0, str(EVALUATION_ROOT))

import isolated_answer_quality_review as REVIEW  # noqa: E402


def _contract() -> dict:
    return {
        "schemaVersion": REVIEW.SCHEMA_VERSION,
        "contractBasis": "semantic-rubric-plus-hard-ground-truth",
        "contractStrength": "hard-ground-truth",
        "question": "Compare alpha and beta.",
        "requiredPoints": [
            {"criterionId": "rp-001", "criterion": "Explain alpha."},
            {"criterionId": "rp-002", "criterion": "Explain beta."},
        ],
        "referenceClaims": [
            {"claimId": "ref-001", "statement": "Alpha is a rate."},
            {"claimId": "ref-002", "statement": "Beta is a factor."},
        ],
        "importantNegatives": [
            {"negativeId": "neg-001", "statement": "Do not put them on one scale."}
        ],
        "expectedSources": [],
        "qrelScope": None,
    }


def _judgment(
    packet: dict,
    required: tuple[str, str] = ("satisfied", "satisfied"),
    negative: str = "respected",
    correctness: str = "correct",
) -> dict:
    contract = packet["qualityContract"]
    return {
        "schemaVersion": REVIEW.SCHEMA_VERSION,
        "packetSha256": REVIEW.sha256_bytes(REVIEW.canonical_json_bytes(packet)),
        "requiredPointJudgments": [
            {
                "criterionId": item["criterionId"],
                "status": status,
                "rationale": "The response is checked against this exact point.",
                "claimOrdinals": [1] if status in {"satisfied", "partial"} else [],
            }
            for item, status in zip(contract["requiredPoints"], required, strict=True)
        ],
        "importantNegativeJudgments": [
            {
                "negativeId": item["negativeId"],
                "status": negative,
                "rationale": "The forbidden conflation is checked directly.",
                "claimOrdinals": [],
            }
            for item in contract["importantNegatives"]
        ],
        "materialCorrectness": {
            "status": correctness,
            "rationale": "No material correctness defect is present.",
        },
    }


def _consensus(
    first: str,
    second: str,
    *,
    correctness: str = "correct",
) -> dict:
    return {
        "requiredPointJudgments": [
            {"criterionId": "rp-001", "status": first},
            {"criterionId": "rp-002", "status": second},
        ],
        "importantNegativeJudgments": [
            {"negativeId": "neg-001", "status": "respected"}
        ],
        "materialCorrectness": {"status": correctness},
        "unresolved": False,
    }


def test_projection_retains_visible_numeric_citations_and_hides_mechanics() -> None:
    response = {
        "answer": {
            "summary": "The measured values are [1, 2] and 43.7(1)% [3].",
            "claims": [
                {
                    "statement": "The interval [1, 2] is substantive text [3].",
                    "evidence_indices": [99],
                }
            ],
        },
        "evidence": [{"source_path": "private/original.md"}],
    }

    projected = REVIEW.project_answer(response)
    serialized = json.dumps(projected)

    assert "[1, 2]" in serialized
    assert "43.7(1)% [3]" in serialized
    assert "evidence_indices" not in serialized
    assert "private/original.md" not in serialized


def test_qrel_contract_uses_rubric_as_claims_and_sources_only_as_anchors(
    tmp_path: Path,
) -> None:
    tests = tmp_path / "q001" / "tests"
    tests.mkdir(parents=True)
    question = {
        "id": "q001",
        "question": "What does the paper establish?",
        "qrels": {"document_ids": ["2401.00001v1"]},
        "evaluation_policy": {"qrel_scope": "non-exhaustive-focus-set"},
        "semantic_rubric": {
            "required_points": ["Explain the measured result."],
        },
    }
    (tests / "question.json").write_text(json.dumps(question), encoding="utf-8")
    (tests / "records.jsonl").write_text(
        json.dumps(
            {
                "record_id": "record-1",
                "title": "A Frozen Paper Title",
                "attributes": {"paper_id": "2401.00001v1"},
            }
        )
        + "\n",
        encoding="utf-8",
    )

    contract, bindings = REVIEW.task_contract(tmp_path / "q001")

    assert contract["contractStrength"] == "qrel-grounded-rubric"
    assert contract["referenceClaims"] == [
        {"claimId": "ref-001", "statement": "Explain the measured result."}
    ]
    assert contract["expectedSources"][0]["title"] == "A Frozen Paper Title"
    assert "A Frozen Paper Title" not in contract["referenceClaims"][0]["statement"]
    assert bindings["groundTruthSha256"] is None


def test_three_orders_keep_stable_ids_and_require_order_matched_output() -> None:
    response = {"summary": "Alpha is a rate; beta is a factor.", "claims": [
        {"ordinal": 1, "statement": "Alpha is a rate; beta is a factor."}
    ]}
    forward = REVIEW.review_packet(_contract(), response, "forward")
    reverse = REVIEW.review_packet(_contract(), response, "reverse")
    rotate = REVIEW.review_packet(_contract(), response, "rotate")

    assert [item["criterionId"] for item in forward["qualityContract"]["requiredPoints"]] == [
        "rp-001", "rp-002"
    ]
    assert [item["criterionId"] for item in reverse["qualityContract"]["requiredPoints"]] == [
        "rp-002", "rp-001"
    ]
    assert [item["criterionId"] for item in rotate["qualityContract"]["requiredPoints"]] == [
        "rp-002", "rp-001"
    ]

    invalid = _judgment(reverse)
    invalid["requiredPointJudgments"].reverse()
    with pytest.raises(REVIEW.ReviewError, match="identifier or status"):
        REVIEW.validate_judgment(invalid, reverse)


def test_runner_normalizes_well_formed_model_digest_typo() -> None:
    response = {
        "summary": "Alpha and beta.",
        "claims": [{"ordinal": 1, "statement": "Alpha and beta."}],
    }
    packet = REVIEW.review_packet(_contract(), response, "forward")
    result = _judgment(packet)
    result["packetSha256"] = "0" * 64

    normalized = REVIEW.validate_judgment(result, packet)

    assert normalized["packetSha256"] == REVIEW.sha256_bytes(
        REVIEW.canonical_json_bytes(packet)
    )

    result["packetSha256"] = "not-a-digest"
    assert REVIEW.validate_judgment(result, packet)["packetSha256"] == REVIEW.sha256_bytes(
        REVIEW.canonical_json_bytes(packet)
    )


def test_majority_resolves_two_votes_but_not_three_distinct_votes() -> None:
    response = {"summary": "Alpha and beta.", "claims": [
        {"ordinal": 1, "statement": "Alpha and beta."}
    ]}
    packet = REVIEW.review_packet(_contract(), response, "forward")
    majority = REVIEW.majority_consensus(
        [
            REVIEW.validate_judgment(_judgment(packet, ("satisfied", "partial")), packet),
            REVIEW.validate_judgment(_judgment(packet, ("satisfied", "partial")), packet),
            REVIEW.validate_judgment(_judgment(packet, ("partial", "missing")), packet),
        ]
    )
    unresolved = REVIEW.majority_consensus(
        [
            REVIEW.validate_judgment(_judgment(packet, ("satisfied", "satisfied")), packet),
            REVIEW.validate_judgment(_judgment(packet, ("partial", "satisfied")), packet),
            REVIEW.validate_judgment(_judgment(packet, ("missing", "satisfied")), packet),
        ]
    )

    assert majority["requiredPointJudgments"][0]["status"] == "satisfied"
    assert majority["unresolved"] is False
    assert unresolved["requiredPointJudgments"][0]["status"] == "unresolved"
    assert unresolved["unresolved"] is True


def test_component_comparison_is_id_bound_and_detects_swapped_quality() -> None:
    baseline = _consensus("satisfied", "partial")
    candidate = _consensus("partial", "satisfied")
    candidate["requiredPointJudgments"].reverse()

    assert REVIEW.component_outcome(baseline, candidate) == "mixed"

    candidate["requiredPointJudgments"][0]["criterionId"] = "rp-999"
    with pytest.raises(REVIEW.ReviewError, match="identity drift"):
        REVIEW.component_outcome(baseline, candidate)


def test_controls_fail_closed_on_unresolved_or_partial_positive() -> None:
    negative = _consensus("missing", "contradicted", correctness="major-error")
    positive = _consensus("satisfied", "satisfied")
    positive["casePass"] = True
    negative["casePass"] = False

    assert REVIEW._control_pass("empty-answer-negative", negative) is True
    assert REVIEW._control_pass("contract-derived-positive", positive) is True

    positive["unresolved"] = True
    assert REVIEW._control_pass("contract-derived-positive", positive) is False


def test_positive_control_explicitly_covers_rubric_truth_and_negative() -> None:
    control = REVIEW.positive_control(_contract())
    statements = [item["statement"] for item in control["claims"]]

    assert "Explain alpha." in statements
    assert "Explain beta." in statements
    assert "Alpha is a rate." in statements
    assert "Beta is a factor." in statements
    assert "It is invalid to put them on one scale." in statements
