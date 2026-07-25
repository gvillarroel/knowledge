#!/usr/bin/env python3
"""Inventory GraphRAG evaluation responses without confusing trials with questions."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
GRADER = REPO / "evaluations/semantic-okf-harbor/grader"
for import_root in (HERE, GRADER):
    if str(import_root) not in sys.path:
        sys.path.insert(0, str(import_root))

import dataset_tool as data  # noqa: E402
import score as grader  # noqa: E402
from trace_status import classify_pi_trace  # noqa: E402

QUESTION_PREFIX = re.compile(r"^(q[0-9]{3})")


class AuditError(ValueError):
    """Raised when response evidence or adjudication coverage is inconsistent."""


def load_json(path: Path) -> dict[str, Any]:
    """Load one JSON object."""

    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AuditError(f"expected a JSON object: {path}")
    return value


def optional_json(path: Path) -> dict[str, Any]:
    """Load one optional JSON object."""

    return load_json(path) if path.is_file() else {}


def response_identity_digest(rows: Sequence[Mapping[str, Any]]) -> str:
    """Hash the stable raw-response identity and payload-hash pairs."""

    payload = [
        [str(row["response_id"]), str(row["response_sha256"])]
        for row in sorted(rows, key=lambda item: str(item["response_id"]))
    ]
    encoded = json.dumps(payload, ensure_ascii=True, separators=(",", ":")).encode(
        "ascii"
    )
    return hashlib.sha256(encoded).hexdigest()


def raw_responses(results_root: Path, question_ids: set[str]) -> tuple[list[dict[str, Any]], int]:
    """Read every local Harbor Pi trace and retain complete JSON responses."""

    responses: list[dict[str, Any]] = []
    trial_count = 0
    for pi_log in sorted(results_root.glob("*/q*__*/agent/pi.txt")):
        trial_count += 1
        trial = pi_log.parents[1]
        job = trial.parent
        match = QUESTION_PREFIX.match(trial.name)
        if match is None or match.group(1) not in question_ids:
            continue
        question_id = match.group(1)
        trace = classify_pi_trace(pi_log)
        output_text = trace.get("answer_text")
        if trace.get("outcome") != "answer-emitted" or not isinstance(
            output_text, str
        ):
            continue
        try:
            output = grader.strict_json(output_text)
        except (json.JSONDecodeError, grader.ScoreError):
            continue
        if not isinstance(output, Mapping) or set(output) != {
            "question_id",
            "answer",
            "evidence",
        }:
            continue
        contract, non_null, contract_errors = grader.validate_contract(
            output, question_id
        )
        evidence = output.get("evidence")
        evidence_count = len(evidence) if isinstance(evidence, list) else 0
        reward = optional_json(trial / "verifier/reward.json")
        diagnostics = optional_json(trial / "verifier/diagnostics.json")
        responses.append(
            {
                "response_id": f"raw/{job.name}/{trial.name}",
                "source": "raw-harbor-result",
                "job": job.name,
                "trial": trial.name,
                "trial_id": optional_json(trial / "result.json").get("id"),
                "question_id": question_id,
                "response_sha256": hashlib.sha256(
                    output_text.encode("utf-8")
                ).hexdigest(),
                "raw_response_available": True,
                "answer_state": "non-null" if non_null else "null",
                "response_contract": contract,
                "contract_errors": contract_errors,
                "evidence_count": evidence_count,
                "reward": reward.get("reward"),
                "mechanical_qualification_gate": reward.get(
                    "mechanical_qualification_gate"
                ),
                "cited_document_count": diagnostics.get(
                    "cited_document_count"
                ),
                "valid_independent_document_count": diagnostics.get(
                    "valid_independent_document_count"
                ),
                "covered_focus_document_count": diagnostics.get(
                    "covered_qrel_count"
                ),
            }
        )
    return responses, trial_count


def manual_review_rows(path: Path) -> dict[tuple[str, str], dict[str, str]]:
    """Parse the existing append-only manual-review table."""

    result: dict[tuple[str, str], dict[str, str]] = {}
    in_results = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line == "## Results":
            in_results = True
            continue
        if in_results and line.startswith("## "):
            break
        if not in_results or not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != 7 or cells[0] in {"Family", "---"}:
            continue
        family = cells[0].casefold().replace(" ", "-")
        question_id = cells[1]
        result[(family, question_id)] = {
            "document_coverage": cells[2],
            "point_coverage": cells[3],
            "rationale": cells[4],
            "protocol_observation": cells[5],
            "semantic_verdict": cells[6].casefold(),
        }
    return result


def historical_responses(
    campaign_report: Path,
    manual_review: Path,
    question_ids: set[str],
) -> tuple[list[dict[str, Any]], int]:
    """Load response identities from a historical report whose raw traces are absent."""

    report = load_json(campaign_report)
    reviews = manual_review_rows(manual_review)
    rows: list[dict[str, Any]] = []
    trials = report.get("trials")
    if not isinstance(trials, list):
        raise AuditError(f"campaign report has no trials: {campaign_report}")
    for trial in trials:
        if not isinstance(trial, Mapping) or not trial.get(
            "complete_response_observed"
        ):
            continue
        question_id = str(trial.get("question_id"))
        family = str(trial.get("family"))
        if question_id not in question_ids:
            continue
        review = reviews.get((family, question_id))
        if review is None:
            raise AuditError(
                f"manual review is missing {family}/{question_id}"
            )
        metrics = trial.get("metrics")
        metrics = metrics if isinstance(metrics, Mapping) else {}
        diagnostics = trial.get("diagnostics")
        diagnostics = diagnostics if isinstance(diagnostics, Mapping) else {}
        rows.append(
            {
                "response_id": (
                    "historical/"
                    f"{report.get('campaign')}/{trial.get('trial_id')}"
                ),
                "source": "historical-manual-review",
                "job": trial.get("run"),
                "trial": None,
                "trial_id": trial.get("trial_id"),
                "family": family,
                "question_id": question_id,
                "response_sha256": None,
                "raw_response_available": False,
                "answer_state": "non-null",
                "response_contract": metrics.get("response_contract") == 1.0,
                "contract_errors": diagnostics.get("contract_errors", []),
                "evidence_count": diagnostics.get("evidence_count"),
                "reward": metrics.get("reward"),
                "mechanical_qualification_gate": metrics.get(
                    "mechanical_qualification_gate"
                ),
                "cited_document_count": None,
                "valid_independent_document_count": None,
                "covered_focus_document_count": diagnostics.get(
                    "covered_qrel_count"
                ),
                **review,
            }
        )
    return rows, len(trials)


def apply_raw_adjudications(
    rows: list[dict[str, Any]], adjudication_path: Path
) -> str:
    """Apply one digest-bound manual adjudication policy to raw responses."""

    adjudication = load_json(adjudication_path)
    digest = response_identity_digest(rows)
    if adjudication.get("response_identity_sha256") != digest:
        raise AuditError(
            "raw-response adjudication does not match the current response inventory"
        )
    rationales = adjudication.get("partial_rationale_by_question")
    pass_cells = adjudication.get("semantic_pass_cells")
    overrides = adjudication.get("overrides", {})
    if not isinstance(rationales, Mapping) or not isinstance(pass_cells, list):
        raise AuditError("invalid raw-response adjudication policy")
    pass_keys = {
        (str(cell.get("job")), str(cell.get("question_id")))
        for cell in pass_cells
        if isinstance(cell, Mapping)
    }
    if not isinstance(overrides, Mapping):
        raise AuditError("invalid adjudication overrides")
    observed_pass_keys: set[tuple[str, str]] = set()
    for row in rows:
        override = overrides.get(row["response_id"])
        if override is not None:
            if not isinstance(override, Mapping):
                raise AuditError(f"invalid override: {row['response_id']}")
            row["semantic_verdict"] = str(override["semantic_verdict"])
            row["rationale"] = str(override["rationale"])
            continue
        if row["answer_state"] == "null":
            row["semantic_verdict"] = "fail"
            row["rationale"] = (
                "The response abstained even though the checked corpus supports "
                "a non-null answer."
            )
            continue
        key = (str(row["job"]), str(row["question_id"]))
        if key in pass_keys:
            observed_pass_keys.add(key)
            row["semantic_verdict"] = "pass"
            row["rationale"] = (
                "Manual review found every authored semantic requirement "
                "materially addressed."
            )
            continue
        rationale = rationales.get(row["question_id"])
        if not isinstance(rationale, str) or not rationale:
            raise AuditError(
                f"no partial rationale for {row['question_id']}"
            )
        row["semantic_verdict"] = "partial"
        row["rationale"] = rationale
    if observed_pass_keys != pass_keys:
        missing = sorted(pass_keys - observed_pass_keys)
        raise AuditError(f"semantic pass cells are absent: {missing}")
    return digest


def semantic_target_counts(
    dataset: Mapping[str, Any],
) -> dict[str, int]:
    """Count authored semantic review targets for every question."""

    result = {
        identifier: len(row["required_points"])
        for identifier, row in data.dataset_semantic_rubrics(dataset).items()
    }
    for row in data.load_jsonl(
        data.pinned_path(dataset["hard_ground_truth"], "hard ground truth")
    ):
        identifier = data.normalize_question_id(row.get("id"))
        ground = row.get("ground_truth")
        if not isinstance(ground, Mapping):
            raise AuditError(f"{identifier}: hard question has no ground truth")
        result[identifier] = sum(
            len(ground.get(key, []))
            for key in ("answer_claims", "derivation", "important_negatives")
        )
    return result


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    """Build the complete question and response inventory."""

    dataset = data.load_dataset(args.dataset)
    validation = data.validate_dataset(args.dataset)
    questions = data.dataset_questions(dataset)
    question_ids = {row["normalized_id"] for row in questions}
    cohorts = data.dataset_cohorts(dataset)
    question_cohort = {
        question_id: cohort
        for cohort in dataset["partition_cohorts"]
        for question_id in cohorts[cohort]
    }
    rubrics = data.dataset_semantic_rubrics(dataset)
    targets = semantic_target_counts(dataset)
    raw, raw_trial_count = raw_responses(args.results, question_ids)
    raw_digest = apply_raw_adjudications(raw, args.raw_adjudications)
    historical, historical_trial_count = historical_responses(
        args.historical_campaign, args.historical_manual_review, question_ids
    )
    responses = sorted(
        [*raw, *historical], key=lambda row: str(row["response_id"])
    )
    response_counts = Counter(row["question_id"] for row in responses)
    raw_counts = Counter(row["question_id"] for row in raw)
    historical_counts = Counter(row["question_id"] for row in historical)
    verdicts = Counter(str(row["semantic_verdict"]) for row in responses)
    covered_questions = {question_id for question_id, count in response_counts.items() if count}
    missing_questions = sorted(question_ids - covered_questions)
    policy = dataset.get("evaluation_policy")
    full_coverage_required = bool(
        isinstance(policy, Mapping)
        and policy.get("full_dataset_coverage_required")
    )
    rubric_by_id = rubrics
    question_rows = []
    for source in sorted(questions, key=lambda row: row["normalized_id"]):
        identifier = source["normalized_id"]
        qrels = source.get("qrels")
        qrels = qrels if isinstance(qrels, Mapping) else {}
        rubric = rubric_by_id.get(identifier)
        question_rows.append(
            {
                "question_id": identifier,
                "source_question_id": source.get("id"),
                "cohort": question_cohort[identifier],
                "question": source.get("question"),
                "focus_document_count": len(qrels.get("paper_ids", [])),
                "minimum_document_count": (
                    rubric.get("min_papers")
                    if isinstance(rubric, Mapping)
                    else None
                ),
                "semantic_target_count": targets[identifier],
                "raw_response_count": raw_counts[identifier],
                "historical_response_count": historical_counts[identifier],
                "reviewable_response_count": response_counts[identifier],
                "empirical_coverage": (
                    "covered" if response_counts[identifier] else "missing"
                ),
                "question_specification_review": (
                    "reviewed-no-content-defect-found"
                ),
            }
        )
    summary_only = load_json(args.summary_only_cells)
    summary_cells = summary_only.get("cells")
    summary_cell_count = len(summary_cells) if isinstance(summary_cells, list) else 0
    concentrated = sum(raw_counts[key] for key in ("q002", "q003", "q004"))
    return {
        "schema_version": "graphrag-response-coverage-audit/1.0",
        "dataset_id": args.dataset,
        "dataset_validation": validation,
        "dataset_question_count": len(question_ids),
        "raw_harbor_trial_count": raw_trial_count,
        "historical_campaign_trial_count": historical_trial_count,
        "summary_only_cell_count": summary_cell_count,
        "summary_only_cells_reviewable": False,
        "raw_complete_response_count": len(raw),
        "historical_manually_reviewed_response_count": len(historical),
        "reviewable_response_count": len(responses),
        "unique_raw_response_count": len(
            {row["response_sha256"] for row in raw}
        ),
        "empirically_covered_question_count": len(covered_questions),
        "missing_question_ids": missing_questions,
        "raw_q002_q004_response_count": concentrated,
        "raw_q002_q004_share": (
            concentrated / len(raw) if raw else 0.0
        ),
        "semantic_verdict_counts": dict(sorted(verdicts.items())),
        "full_dataset_coverage_required": full_coverage_required,
        "full_dataset_claim_eligible": (
            not full_coverage_required or len(covered_questions) == len(question_ids)
        ),
        "raw_response_identity_sha256": raw_digest,
        "questions": question_rows,
        "responses": responses,
    }


def markdown(report: Mapping[str, Any]) -> str:
    """Render one audit with every question and response on its own row."""

    verdicts = report["semantic_verdict_counts"]
    lines = [
        "# GraphRAG 40-question response and coverage audit",
        "",
        "## Scope correction",
        "",
        (
            f"The canonical dataset contains **{report['dataset_question_count']} "
            "questions**. The earlier 18-response report was a v36 evidence "
            "slice, not the complete dataset."
        ),
        "",
        (
            f"This audit inventories {report['raw_complete_response_count']} "
            "complete raw Harbor responses and "
            f"{report['historical_manually_reviewed_response_count']} additional "
            "historical responses with preserved manual adjudications: "
            f"**{report['reviewable_response_count']} reviewable responses**."
        ),
        "",
        (
            f"Only **{report['empirically_covered_question_count']}/"
            f"{report['dataset_question_count']} questions** have a complete "
            "response. Missing: "
            + ", ".join(f"`{item}`" for item in report["missing_question_ids"])
            + "."
        ),
        "",
        (
            f"`q002`-`q004` account for "
            f"{report['raw_q002_q004_response_count']}/"
            f"{report['raw_complete_response_count']} raw responses "
            f"({100 * report['raw_q002_q004_share']:.1f}%), so the archive is "
            "iteration-heavy rather than question-balanced."
        ),
        "",
        (
            f"Semantic adjudications: {verdicts.get('pass', 0)} pass, "
            f"{verdicts.get('partial', 0)} partial, and "
            f"{verdicts.get('fail', 0)} fail. Mechanical reward is not used "
            "as semantic correctness."
        ),
        "",
        (
            "**Full-dataset claim eligible:** "
            f"`{str(report['full_dataset_claim_eligible']).lower()}`."
        ),
        "",
        "The 60 older comparison cells are retained as summary-only evidence; "
        "their response bodies are absent, so they are not silently counted as "
        "individually reviewable responses.",
        "",
        "## Every question",
        "",
        "| Question | Cohort | Focus docs | Minimum | Semantic targets | Raw | Historical | Total | Coverage |",
        "|---|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in report["questions"]:
        minimum = (
            "—"
            if row["minimum_document_count"] is None
            else str(row["minimum_document_count"])
        )
        lines.append(
            "| "
            + " | ".join(
                [
                    str(row["question_id"]),
                    str(row["cohort"]),
                    str(row["focus_document_count"]),
                    minimum,
                    str(row["semantic_target_count"]),
                    str(row["raw_response_count"]),
                    str(row["historical_response_count"]),
                    str(row["reviewable_response_count"]),
                    str(row["empirical_coverage"]),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "All 40 question specifications were reviewed against their authored "
            "rubric or hard ground truth. No question-content defect was found. "
            "The defects were in coverage and evaluator semantics.",
            "",
            "## Every reviewable response",
            "",
            "| Response | Question | Semantic | Answer | Contract | Evidence | Valid docs | Focus docs | Reward |",
            "|---|---|---|---|---:|---:|---:|---:|---:|",
        ]
    )
    for row in report["responses"]:
        values = []
        for key in (
            "evidence_count",
            "valid_independent_document_count",
            "covered_focus_document_count",
            "reward",
        ):
            value = row.get(key)
            if value is None:
                values.append("—")
            elif key == "reward":
                values.append(f"{float(value):.6f}")
            else:
                values.append(str(value))
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{row['response_id']}`",
                    str(row["question_id"]),
                    str(row["semantic_verdict"]),
                    str(row["answer_state"]),
                    "1" if row["response_contract"] else "0",
                    *values,
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "Each response row has a separate semantic verdict and retains its "
            "mechanical observations. Detailed rationales are in the companion "
            "JSON report. Historical rows do not invent unavailable raw payloads.",
            "",
        ]
    )
    return "\n".join(lines)


def write_text(path: Path, value: str) -> None:
    """Write an LF-normalized UTF-8 artifact."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        value.replace("\r\n", "\n") + ("" if value.endswith("\n") else "\n"),
        encoding="utf-8",
        newline="\n",
    )


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse response-audit inputs and outputs."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", default="graphrag-papers-40")
    parser.add_argument(
        "--results",
        type=Path,
        default=HERE / "results",
    )
    parser.add_argument(
        "--historical-campaign",
        type=Path,
        default=(
            HERE
            / "reports/20260717-papers-consult-gpt53-spark-01-audit-v2.json"
        ),
    )
    parser.add_argument(
        "--historical-manual-review",
        type=Path,
        default=(
            HERE
            / "reports/20260717-papers-consult-gpt53-spark-01-manual-review.md"
        ),
    )
    parser.add_argument(
        "--summary-only-cells",
        type=Path,
        default=(
            REPO
            / "evaluations/graphrag-cross-paper/analysis/full-baseline-cells.json"
        ),
    )
    parser.add_argument("--raw-adjudications", type=Path, required=True)
    parser.add_argument("--output-json", type=Path)
    parser.add_argument("--output-markdown", type=Path)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    """Run the response inventory and emit requested artifacts."""

    args = parse_args(argv)
    try:
        report = build_report(args)
    except (
        AuditError,
        data.DatasetError,
        OSError,
        UnicodeError,
        json.JSONDecodeError,
    ) as exc:
        raise SystemExit(str(exc)) from exc
    rendered_json = json.dumps(
        report, ensure_ascii=False, indent=2, sort_keys=True
    )
    rendered_markdown = markdown(report)
    if args.output_json:
        write_text(args.output_json, rendered_json)
    if args.output_markdown:
        write_text(args.output_markdown, rendered_markdown)
    if not args.output_json and not args.output_markdown:
        print(rendered_json)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
