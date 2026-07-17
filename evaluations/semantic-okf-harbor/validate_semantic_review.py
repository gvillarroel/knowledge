#!/usr/bin/env python3
"""Validate the closed q031 semantic review and its reproducible bindings."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT = Path(__file__).resolve().parent / "reports/q031-semantic-review.json"
FAMILIES = {"legacy", "embeddings", "classical", "adaptive", "entity-graph", "ensemble"}
ITEM_IDS = ("q031-a1", "q031-a2", "q031-a3", "q031-a4", "q031-a5")
NEGATIVE_IDS = ("q031-n1", "q031-n2")
ALLOWED_STATUS = {"valid_answer", "contract_invalid", "invalid_json", "timeout"}
ALLOWED_ITEM_SCORES = {0, 0.5, 1}


def sha256(path: Path) -> str:
    """Return the lowercase SHA-256 of a file."""

    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(path: Path = REPORT, *, verify_artifacts: bool = False) -> dict:
    """Validate structure, pair coverage, arithmetic, and optional raw bindings."""

    report = json.loads(path.read_text(encoding="utf-8"))
    if report.get("schema_version") != "semantic-okf-harbor-semantic-review/1.0":
        raise ValueError("unexpected semantic review schema version")
    if report.get("question_id") != "q031":
        raise ValueError("semantic review must be bound to q031")

    binding = report["ground_truth_binding"]
    truth_path = ROOT / binding["path"]
    if not truth_path.is_file() or sha256(truth_path) != binding["sha256"]:
        raise ValueError("ground-truth binding does not match")

    reviews = report.get("reviews", [])
    expected = {(family, variant) for family in FAMILIES for variant in ("baseline", "evolved")}
    observed = {(item.get("family"), item.get("variant")) for item in reviews}
    if len(reviews) != 12 or observed != expected:
        raise ValueError("review must contain exactly one baseline/evolved pair per family")

    for review in reviews:
        if review["status"] not in ALLOWED_STATUS:
            raise ValueError("unknown review status")
        if set(review["atomic_answer_claims"]) != set(ITEM_IDS):
            raise ValueError("atomic answer claim IDs differ from q031 ground truth")
        if set(review["important_negatives"]) != set(NEGATIVE_IDS):
            raise ValueError("important-negative IDs differ from q031 ground truth")
        scored = [review["atomic_answer_claims"][key]["score"] for key in ITEM_IDS]
        scored += [review["important_negatives"][key]["score"] for key in NEGATIVE_IDS]
        scored += [review["derivation_logic"][key]["score"] for key in ("join", "conditional")]
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

        result_binding = review["result_binding"]
        if verify_artifacts:
            result_path = ROOT / result_binding["path"]
            if not result_path.is_file() or sha256(result_path) != result_binding["sha256"]:
                raise ValueError(f"raw result binding mismatch: {result_binding['path']}")

    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, default=REPORT)
    parser.add_argument("--verify-artifacts", action="store_true")
    args = parser.parse_args()
    validate(args.report, verify_artifacts=args.verify_artifacts)
    print("q031 semantic review is valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
