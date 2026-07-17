#!/usr/bin/env python3
"""Validate the closed q034 holdout semantic review and its bindings."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT = Path(__file__).resolve().parent / "reports/q034-semantic-review.json"
FAMILIES = {"legacy", "embeddings", "classical", "adaptive", "entity-graph", "ensemble"}
ITEM_IDS = ("q034-a1", "q034-a2", "q034-a3", "q034-a4", "q034-a5")
NEGATIVE_IDS = ("q034-n1", "q034-n2")
DERIVATION_IDS = ("processing_boundary", "authorization_before_inference")
ALLOWED_STATUS = {"valid_answer", "contract_invalid", "invalid_json", "timeout"}
ALLOWED_ITEM_SCORES = {0, 0.5, 1}
RESULT_PATH = re.compile(
    r"^evaluations/semantic-okf-harbor/results/"
    r"20260716-(baseline|evolved)-holdout-"
    r"(legacy|embeddings|classical|adaptive|entity-graph|ensemble)-q034/"
    r"q034__[^/]+/result\.json$"
)


def sha256(path: Path) -> str:
    """Return the lowercase SHA-256 of a file."""

    return hashlib.sha256(path.read_bytes()).hexdigest()


def final_answer_text(trace_path: Path) -> str | None:
    """Return the last non-empty assistant text block from a Pi JSONL trace."""

    final: str | None = None
    for raw_line in trace_path.read_text(encoding="utf-8").splitlines():
        try:
            event = json.loads(raw_line)
        except json.JSONDecodeError:
            continue
        message = event.get("message", {})
        if event.get("type") != "message_end" or message.get("role") != "assistant":
            continue
        for block in message.get("content", []):
            text = block.get("text") if block.get("type") == "text" else None
            if isinstance(text, str) and text:
                final = text
    return final


def _ground_truth_ids(path: Path) -> tuple[set[str], set[str]]:
    """Read q034 and return its atomic and negative identifiers."""

    for line in path.read_text(encoding="utf-8").splitlines():
        item = json.loads(line)
        if item.get("id") == "q034":
            truth = item["ground_truth"]
            return (
                {claim["id"] for claim in truth["answer_claims"]},
                {claim["id"] for claim in truth["important_negatives"]},
            )
    raise ValueError("q034 is absent from the bound hard ground truth")


def _actual_metric(result: dict, key: str) -> float:
    """Read a Harbor metric, mapping absent timeout metrics to zero."""

    value = result.get("verifier_result", {}).get("rewards", {}).get(key)
    if value is None and (result.get("exception_info") or {}).get("exception_type") == "AgentTimeoutError":
        return 0.0
    if value is None:
        raise ValueError(f"result is missing Harbor metric {key}")
    return float(value)


def _expected_status(result: dict, final_text: str | None) -> str:
    """Classify a result from the exception, final text, and contract metric."""

    if (result.get("exception_info") or {}).get("exception_type") == "AgentTimeoutError":
        return "timeout"
    if final_text is None:
        return "invalid_json"
    try:
        json.loads(final_text)
    except json.JSONDecodeError:
        return "invalid_json"
    return "valid_answer" if _actual_metric(result, "response_contract") == 1 else "contract_invalid"


def _verify_raw_artifact(review: dict) -> None:
    """Verify one exact holdout result, its metrics, and final assistant text."""

    binding = review["result_binding"]
    normalized_path = binding["path"].replace("\\", "/")
    match = RESULT_PATH.fullmatch(normalized_path)
    if match is None:
        raise ValueError("q034 review must bind only the definitive holdout result roots")
    if (match.group(1), match.group(2)) != (review["variant"], review["family"]):
        raise ValueError("result path does not match the declared variant and family")

    result_path = ROOT / binding["path"]
    if not result_path.is_file() or sha256(result_path) != binding["sha256"]:
        raise ValueError(f"raw result binding mismatch: {binding['path']}")
    result = json.loads(result_path.read_text(encoding="utf-8"))
    if result.get("source") != "holdout" or result.get("task_name", "").split("__")[-1] != "q034":
        raise ValueError(f"result is not the definitive q034 holdout trial: {binding['path']}")

    for report_key, result_key in (
        ("reward", "reward"),
        ("quality_gate", "quality_gate"),
        ("evidence_validity", "evidence_validity"),
        ("response_contract", "response_contract"),
    ):
        observed = float(review["harbor_metrics"][report_key])
        actual = _actual_metric(result, result_key)
        if not math.isclose(observed, actual, rel_tol=0, abs_tol=1e-15):
            raise ValueError(f"Harbor metric mismatch for {binding['path']}: {report_key}")

    trace_path = result_path.parent / "artifacts/pi.jsonl"
    if not trace_path.is_file():
        raise ValueError(f"Pi trace is absent for {binding['path']}")
    final_text = final_answer_text(trace_path)
    if review["status"] != _expected_status(result, final_text):
        raise ValueError(f"review status disagrees with the raw q034 result: {binding['path']}")
    expected_hash = review["final_answer_sha256"]
    if final_text is None:
        if expected_hash is not None:
            raise ValueError(f"final answer is absent but a hash is declared: {binding['path']}")
    else:
        actual_hash = hashlib.sha256(final_text.encode("utf-8")).hexdigest()
        if actual_hash != expected_hash:
            raise ValueError(f"final-answer hash mismatch: {binding['path']}")


def validate(path: Path = REPORT, *, verify_artifacts: bool = False) -> dict:
    """Validate IDs, pair coverage, arithmetic, and optional raw bindings."""

    report = json.loads(path.read_text(encoding="utf-8"))
    if report.get("schema_version") != "semantic-okf-harbor-semantic-review/1.0":
        raise ValueError("unexpected semantic review schema version")
    if report.get("question_id") != "q034":
        raise ValueError("semantic review must be bound to q034")

    binding = report["ground_truth_binding"]
    truth_path = ROOT / binding["path"]
    if not truth_path.is_file() or sha256(truth_path) != binding["sha256"]:
        raise ValueError("ground-truth binding does not match")
    truth_items, truth_negatives = _ground_truth_ids(truth_path)
    if truth_items != set(ITEM_IDS) or truth_negatives != set(NEGATIVE_IDS):
        raise ValueError("checked q034 identifiers differ from the bound ground truth")

    reviews = report.get("reviews", [])
    expected = {(family, variant) for family in FAMILIES for variant in ("baseline", "evolved")}
    observed = {(item.get("family"), item.get("variant")) for item in reviews}
    if len(reviews) != 12 or observed != expected:
        raise ValueError("review must contain exactly one baseline/evolved pair per family")

    for review in reviews:
        if review["status"] not in ALLOWED_STATUS:
            raise ValueError("unknown review status")
        if set(review["atomic_answer_claims"]) != set(ITEM_IDS):
            raise ValueError("atomic answer claim IDs differ from q034 ground truth")
        if set(review["important_negatives"]) != set(NEGATIVE_IDS):
            raise ValueError("important-negative IDs differ from q034 ground truth")
        if set(review["derivation_logic"]) != set(DERIVATION_IDS):
            raise ValueError("q034 review must score both declared derivations")
        scored = [review["atomic_answer_claims"][key]["score"] for key in ITEM_IDS]
        scored += [review["important_negatives"][key]["score"] for key in NEGATIVE_IDS]
        scored += [review["derivation_logic"][key]["score"] for key in DERIVATION_IDS]
        if not all(score in ALLOWED_ITEM_SCORES for score in scored):
            raise ValueError("item scores must be 0, 0.5, or 1")
        expected_completeness = round(sum(scored) / len(scored), 6)
        if review["summary_scores"]["completeness"] != expected_completeness:
            raise ValueError("completeness does not equal the declared nine-item mean")
        if review["summary_scores"]["response_contract"] != review["harbor_metrics"]["response_contract"]:
            raise ValueError("response-contract summaries disagree")
        final_hash = review["final_answer_sha256"]
        if review["status"] == "timeout" and final_hash is not None:
            raise ValueError("timeout must not claim a final-answer hash")
        if review["status"] != "timeout" and (not isinstance(final_hash, str) or len(final_hash) != 64):
            raise ValueError("non-timeout review must bind the final answer")
        if verify_artifacts:
            _verify_raw_artifact(review)

    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, default=REPORT)
    parser.add_argument("--verify-artifacts", action="store_true")
    args = parser.parse_args()
    validate(args.report, verify_artifacts=args.verify_artifacts)
    print("q034 semantic review is valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
