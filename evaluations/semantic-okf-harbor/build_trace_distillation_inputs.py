#!/usr/bin/env python3
"""Normalize reviewed Harbor consult trajectories for trace distillation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


DISCOVERY = ("q031", "q032")
HOLDOUT = ("q034",)


def normalize(question: str, review: dict) -> dict:
    """Convert one reviewed evolved trajectory into the skill trace schema."""
    metrics = review["harbor_metrics"]
    scores = review["summary_scores"]
    success = (
        metrics["quality_gate"] == 1
        and metrics["response_contract"] == 1
        and scores["semantic_correctness"] >= 0.9
        and scores["grounding"] >= 0.95
    )
    issues: list[str] = []
    strengths: list[str] = []
    if metrics["response_contract"] != 1:
        issues.extend(("missing-output-contract", "missing-hard-gates"))
    else:
        strengths.append("strong-output-contract")
    if scores["semantic_correctness"] < 0.9:
        issues.append("semantic-correctness-regression")
    if scores["completeness"] < 0.8:
        issues.append("incomplete-semantic-coverage")
    if scores["grounding"] < 0.95:
        issues.append("weak-evidence-grounding")
    else:
        strengths.append("strong-evidence-grounding")
    if not review.get("material_errors"):
        strengths.append("strong-scope-discipline")
    composite = (
        metrics["reward"] * 0.4
        + scores["semantic_correctness"] * 0.25
        + scores["completeness"] * 0.2
        + scores["grounding"] * 0.15
    )
    return {
        "traceId": f'{review["family"]}-{question}-evolved',
        "benchmarkId": "semantic-okf-harbor-reviewed-v1",
        "promptId": question,
        "outcome": "success" if success else "failure",
        "issues": issues,
        "strengths": strengths,
        "score": round(composite, 6),
        "notes": json.dumps(
            {"metrics": metrics, "scores": scores, "material_errors": review.get("material_errors", [])},
            sort_keys=True,
        ),
        "filesTouched": [],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reports", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    for cohort, questions in (("discovery", DISCOVERY), ("holdout", HOLDOUT)):
        for question in questions:
            payload = json.loads((args.reports / f"{question}-semantic-review.json").read_text(encoding="utf-8"))
            for review in payload["reviews"]:
                if review["variant"] != "evolved":
                    continue
                target = args.output / review["family"] / cohort
                target.mkdir(parents=True, exist_ok=True)
                (target / f"{question}.json").write_text(
                    json.dumps(normalize(question, review), indent=2) + "\n", encoding="utf-8"
                )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
