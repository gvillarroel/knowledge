"""Regression tests for provider-aware Semantic OKF Harbor scoring."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import OrderedDict
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
GRADER_ROOT = REPO / "evaluations/semantic-okf-harbor/grader"
sys.path.insert(0, str(GRADER_ROOT))

import score as SCORE  # noqa: E402
from trace_status import classify_pi_trace  # noqa: E402


def assistant_event(
    text: str | None,
    *,
    stop_reason: str,
    error: str | None = None,
) -> str:
    """Render one minimal Pi assistant message-end event."""

    message: dict[str, object] = {
        "role": "assistant",
        "content": [] if text is None else [{"type": "text", "text": text}],
        "stopReason": stop_reason,
    }
    if error is not None:
        message["errorMessage"] = error
    return json.dumps({"type": "message_end", "message": message}) + "\n"


def evidence_row(record: dict[str, object], *, shuffled: bool = False) -> OrderedDict[str, object]:
    """Build one exact evidence row, optionally in a non-canonical member order."""

    body = str(record["body"])
    values = {
        "source_id": record["source_id"],
        "record_id": record["record_id"],
        "concept_path": record["concept_path"],
        "source_path": record["source_path"],
        "record_sha256": record["record_sha256"],
        "locator": OrderedDict([("kind", "record"), ("target", "record.body")]),
        "text_sha256": hashlib.sha256(body.encode("utf-8")).hexdigest(),
    }
    order = (
        [
            "source_id",
            "record_id",
            "record_sha256",
            "concept_path",
            "source_path",
            "locator",
            "text_sha256",
        ]
        if shuffled
        else SCORE.EVIDENCE_KEYS
    )
    return OrderedDict((key, values[key]) for key in order)


def scoring_fixture(tmp_path: Path, *, cited_documents: int, stop_reason: str = "stop") -> argparse.Namespace:
    """Create a six-document scoring fixture with a configurable cited subset."""

    tmp_path.mkdir(parents=True, exist_ok=True)
    records = [
        {
            "source_id": f"paper-{index}",
            "record_id": f"record-{index}",
            "concept_path": f"concepts/paper-{index}.md",
            "source_path": f"papers/{index}.md",
            "record_sha256": f"{index:064x}",
            "body": f"Evidence body {index}",
        }
        for index in range(1, 7)
    ]
    question = {
        "id": "q003",
        "question": "Compare six papers.",
        "qrels": {"document_ids": [f"doc-{index}" for index in range(1, 7)]},
        "minimum_document_count": 6,
        "semantic_rubric": {"required_points": ["Compare origins."]},
    }
    crosswalk = {
        "records": [
            {
                "source_id": row["source_id"],
                "record_id": row["record_id"],
                "document_id": f"doc-{index}",
            }
            for index, row in enumerate(records, 1)
        ]
    }
    evidence = [
        evidence_row(row, shuffled=index == 0)
        for index, row in enumerate(records[:cited_documents])
    ]
    answer = OrderedDict(
        [
            ("question_id", "q003"),
            (
                "answer",
                OrderedDict(
                    [
                        ("summary", "A grounded comparison."),
                        (
                            "claims",
                            [
                                OrderedDict(
                                    [
                                        ("statement", "The papers differ."),
                                        ("evidence_indices", list(range(cited_documents))),
                                    ]
                                )
                            ],
                        ),
                    ]
                ),
            ),
            ("evidence", evidence),
        ]
    )
    (tmp_path / "question.json").write_text(json.dumps(question), encoding="utf-8")
    (tmp_path / "records.jsonl").write_text(
        "".join(json.dumps(row) + "\n" for row in records), encoding="utf-8"
    )
    (tmp_path / "crosswalk.json").write_text(json.dumps(crosswalk), encoding="utf-8")
    (tmp_path / "pi.jsonl").write_text(
        assistant_event(json.dumps(answer), stop_reason=stop_reason), encoding="utf-8"
    )
    return argparse.Namespace(
        pi_log=tmp_path / "pi.jsonl",
        question=tmp_path / "question.json",
        ledger=tmp_path / "records.jsonl",
        crosswalk=tmp_path / "crosswalk.json",
        ground_truth=None,
        authority_root=tmp_path / "authority",
    )


def test_evidence_object_member_order_is_not_an_undeclared_contract() -> None:
    record = {
        "source_id": "source",
        "record_id": "record",
        "concept_path": "concept.md",
        "source_path": "source.md",
        "record_sha256": "a" * 64,
        "body": "body",
    }
    answer = OrderedDict(
        [
            ("question_id", "q003"),
            (
                "answer",
                OrderedDict(
                    [
                        ("summary", "Summary"),
                        (
                            "claims",
                            [
                                OrderedDict(
                                    [("statement", "Claim"), ("evidence_indices", [0])]
                                )
                            ],
                        ),
                    ]
                ),
            ),
            ("evidence", [evidence_row(record, shuffled=True)]),
        ]
    )

    assert SCORE.validate_contract(answer, "q003") == (True, True, [])
    del answer["evidence"][0]["source_path"]
    assert "evidence-contract" in SCORE.validate_contract(answer, "q003")[2]


def test_minimum_document_gate_is_separate_and_non_compensating(tmp_path: Path) -> None:
    two_rewards, two_diagnostics = SCORE.score(scoring_fixture(tmp_path / "two", cited_documents=2))
    six_rewards, _ = SCORE.score(scoring_fixture(tmp_path / "six", cited_documents=6))

    assert two_rewards["evidence_contract_gate"] == 1.0
    assert two_rewards["minimum_document_gate"] == 0.0
    assert two_rewards["mechanical_qualification_gate"] == 0.0
    assert two_rewards["reward"] == 0.0
    assert two_diagnostics["semantic_correctness"] == "manual-review-required"
    assert six_rewards["evidence_contract_gate"] == 1.0
    assert six_rewards["minimum_document_gate"] == 1.0
    assert six_rewards["mechanical_qualification_gate"] == 1.0
    assert six_rewards["reward"] == 1.0


def test_terminal_classifier_distinguishes_provider_and_agent_outcomes(tmp_path: Path) -> None:
    fixtures = {
        "quota": (assistant_event(None, stop_reason="error", error="usage_limit_reached status_code\":429"), "provider-quota"),
        "context": (assistant_event(None, stop_reason="error", error="context_length_exceeded"), "provider-context-limit"),
        "length": (assistant_event("{", stop_reason="length"), "output-limit"),
        "tool": (assistant_event("working", stop_reason="toolUse"), "agent-interrupted"),
        "answer": (assistant_event('{"ok":true}', stop_reason="stop"), "answer-emitted"),
    }
    for name, (payload, expected) in fixtures.items():
        path = tmp_path / f"{name}.jsonl"
        path.write_text(payload, encoding="utf-8")
        result = classify_pi_trace(path)
        assert result["outcome"] == expected
        assert "usage limit" not in json.dumps({key: value for key, value in result.items() if key != "answer_text"})


def test_provider_failure_is_not_a_verifier_error_and_keeps_metric_vector(tmp_path: Path) -> None:
    args = scoring_fixture(tmp_path, cited_documents=6)
    args.pi_log.write_text(
        assistant_event(None, stop_reason="error", error="usage_limit_reached private headers"),
        encoding="utf-8",
    )

    rewards, diagnostics = SCORE.score(args)

    assert diagnostics["status"] == "provider-failure"
    assert diagnostics["terminal_outcome"] == "provider-quota"
    assert diagnostics["error_code"] == "usage_limit_reached"
    assert diagnostics["parse_error"] == "assistant-output-absent"
    assert rewards["response_contract"] == 0.0
    assert rewards["reward"] == 0.0
    assert "private headers" not in json.dumps(diagnostics)


def test_output_limit_cannot_pass_even_when_partial_text_is_valid_json(tmp_path: Path) -> None:
    rewards, diagnostics = SCORE.score(
        scoring_fixture(tmp_path, cited_documents=6, stop_reason="length")
    )

    assert rewards["response_contract"] == 1.0
    assert rewards["minimum_document_gate"] == 1.0
    assert rewards["evidence_contract_gate"] == 0.0
    assert rewards["mechanical_qualification_gate"] == 0.0
    assert diagnostics["status"] == "agent-failure"
    assert diagnostics["terminal_outcome"] == "output-limit"
