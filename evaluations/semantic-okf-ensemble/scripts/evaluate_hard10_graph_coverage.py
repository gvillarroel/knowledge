#!/usr/bin/env python3
"""Measure hard-ten paper and exact-page coverage from one graph-aware route."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from _evaluation import (
    ENSEMBLE_PLAN,
    EvaluationError,
    benchmark_rows,
    display_path,
    deduplicate,
    find_route,
    load_json,
    load_jsonl,
    mean,
    sha256,
    write_new,
)


SCHEMA_VERSION = "semantic-okf-ensemble-hard10-graph-coverage/1.0"


def _section_map(path: Path) -> dict[str, tuple[str, str]]:
    result: dict[str, tuple[str, str]] = {}
    for row in load_jsonl(path):
        section_id = row.get("section_id")
        paper_id = row.get("paper_id")
        locator = row.get("locator")
        fragment = locator.get("fragment") if isinstance(locator, dict) else None
        if not all(isinstance(value, str) and value for value in (section_id, paper_id, fragment)):
            raise EvaluationError("section rows require section_id, paper_id, and locator.fragment")
        if section_id in result:
            raise EvaluationError(f"duplicate section id: {section_id}")
        result[section_id] = (paper_id, fragment)
    if not result:
        raise EvaluationError("section map is empty")
    return result


def _claim_anchors(truth: dict[str, Any]) -> dict[str, set[tuple[str, str]]]:
    result: dict[str, set[tuple[str, str]]] = {}
    evidence = truth.get("authoritative_evidence")
    if not isinstance(evidence, list):
        raise EvaluationError(f"{truth.get('id')}: authoritative_evidence must be an array")
    for item in evidence:
        if not isinstance(item, dict):
            raise EvaluationError(f"{truth.get('id')}: invalid authoritative evidence row")
        claim_id = item.get("claim_id")
        paper_id = item.get("paper_id")
        pages = item.get("paper_evidence")
        if not isinstance(claim_id, str) or not isinstance(paper_id, str) or not isinstance(pages, list):
            raise EvaluationError(f"{truth.get('id')}: invalid claim evidence identity")
        anchors = {
            (paper_id, page["locator"])
            for page in pages
            if isinstance(page, dict) and isinstance(page.get("locator"), str)
        }
        if not anchors:
            raise EvaluationError(f"{truth.get('id')}: claim {claim_id} has no page anchors")
        if claim_id in result:
            raise EvaluationError(f"{truth.get('id')}: duplicate authoritative claim {claim_id}")
        result[claim_id] = anchors
    return result


def _group_coverage(
    groups: Any,
    anchors_by_claim: dict[str, set[tuple[str, str]]],
    returned: set[tuple[str, str]],
) -> tuple[float, float, list[dict[str, Any]]]:
    if not isinstance(groups, list):
        raise EvaluationError("ground-truth claim groups must be an array")
    any_scores: list[float] = []
    all_scores: list[float] = []
    details: list[dict[str, Any]] = []
    for group in groups:
        if not isinstance(group, dict) or not isinstance(group.get("evidence_claim_ids"), list):
            raise EvaluationError("invalid ground-truth claim group")
        options = group["evidence_claim_ids"]
        option_anchors = [anchors_by_claim[claim_id] for claim_id in options]
        any_covered = any(bool(anchors & returned) for anchors in option_anchors)
        all_covered = any(anchors <= returned for anchors in option_anchors)
        any_scores.append(float(any_covered))
        all_scores.append(float(all_covered))
        details.append(
            {
                "id": group.get("id"),
                "claim_options": options,
                "any_locator_covered": any_covered,
                "all_locators_covered": all_covered,
            }
        )
    return mean(any_scores), mean(all_scores), details


def _evaluate(
    report_path: Path,
    route_name: str,
    sections_path: Path,
    candidate_label: str,
    plan_path: Path,
) -> dict[str, Any]:
    manifest, questions, truth_rows = benchmark_rows()
    report = load_json(report_path)
    if str(report.get("extends_evidence_schema")) != "1.2":
        raise EvaluationError("candidate report must extend evidence-valid schema 1.2")
    if report.get("top_k") != 10:
        raise EvaluationError("graph coverage replay requires a direct top-k 10 report")
    route = find_route(report, route_name)
    rows = route.get("queries")
    if not isinstance(rows, list):
        raise EvaluationError("route queries must be an array")
    by_id = {row.get("question_id"): row for row in rows if isinstance(row, dict)}
    hard_questions = questions[-10:]
    if set(by_id) != {question["id"] for question in questions}:
        raise EvaluationError("candidate report must contain every frozen retrieval question exactly once")
    truth_by_id = {row["id"]: row for row in truth_rows}
    sections = _section_map(sections_path)
    per_question: list[dict[str, Any]] = []
    issues: list[str] = []
    total_hits = 0
    valid_hits = 0
    mapped_hits = 0
    for question in hard_questions:
        identifier = question["id"]
        row = by_id[identifier]
        truth = truth_by_id[identifier]
        hits = row.get("hits")
        if not isinstance(hits, list):
            raise EvaluationError(f"{identifier}: hits must be an array")
        returned_anchors: set[tuple[str, str]] = set()
        returned_papers: list[str | None] = []
        returned_sources: list[str | None] = []
        row_valid = 0
        row_mapped = 0
        for rank, hit in enumerate(hits, 1):
            if not isinstance(hit, dict) or hit.get("rank") != rank:
                issues.append(f"{identifier}: invalid hit rank {rank}")
                continue
            paper_id = hit.get("paper_id")
            returned_papers.append(paper_id)
            returned_sources.append(hit.get("source_id"))
            validation = hit.get("evidence_validation")
            valid = (
                isinstance(validation, dict)
                and validation.get("valid") is True
                and validation.get("issues") == []
            )
            row_valid += int(valid)
            if not valid:
                issues.append(f"{identifier}: hit {rank} failed retained evidence validation")
            fragment = None
            locator = hit.get("locator")
            if isinstance(locator, dict) and isinstance(locator.get("fragment"), str):
                fragment = locator["fragment"]
            chunk_id = hit.get("chunk_id")
            if fragment is None and isinstance(chunk_id, str) and chunk_id in sections:
                mapped_paper, fragment = sections[chunk_id]
                if mapped_paper != paper_id:
                    issues.append(f"{identifier}: hit {rank} section paper differs from hit paper")
                    fragment = None
            if isinstance(paper_id, str) and isinstance(fragment, str):
                returned_anchors.add((paper_id, fragment))
                row_mapped += 1
            else:
                issues.append(f"{identifier}: hit {rank} has no exact PDF-page locator")

        qrels = question["qrels"]
        required_papers = set(qrels["paper_ids"])
        required_sources = set(qrels["source_ids"])
        required_paper_sources = {source for source in required_sources if source.startswith("paper-")}
        papers = set(deduplicate(returned_papers))
        sources = set(deduplicate(returned_sources))
        anchors_by_claim = _claim_anchors(truth)
        expected_anchors = set().union(*anchors_by_claim.values())
        answer_any, answer_all, answer_details = _group_coverage(
            truth["ground_truth"]["answer_claims"], anchors_by_claim, returned_anchors
        )
        negative_any, negative_all, negative_details = _group_coverage(
            truth["ground_truth"]["important_negatives"], anchors_by_claim, returned_anchors
        )
        per_question.append(
            {
                "id": identifier,
                "returned_hits": len(hits),
                "valid_hits": row_valid,
                "mapped_page_hits": row_mapped,
                "required_paper_coverage": len(papers & required_papers) / len(required_papers),
                "required_paper_source_coverage": (
                    len(sources & required_paper_sources) / len(required_paper_sources)
                    if required_paper_sources
                    else 1.0
                ),
                "required_all_source_coverage": len(sources & required_sources) / len(required_sources),
                "exact_locator_recall": len(returned_anchors & expected_anchors) / len(expected_anchors),
                "answer_claim_any_locator_coverage": answer_any,
                "answer_claim_all_locator_coverage": answer_all,
                "important_negative_any_locator_coverage": negative_any,
                "important_negative_all_locator_coverage": negative_all,
                "expected_locator_count": len(expected_anchors),
                "returned_expected_locator_count": len(returned_anchors & expected_anchors),
                "answer_claims": answer_details,
                "important_negatives": negative_details,
            }
        )
        total_hits += len(hits)
        valid_hits += row_valid
        mapped_hits += row_mapped

    metrics = {
        name: mean(float(row[name]) for row in per_question)
        for name in (
            "required_paper_coverage",
            "required_paper_source_coverage",
            "required_all_source_coverage",
            "exact_locator_recall",
            "answer_claim_any_locator_coverage",
            "answer_claim_all_locator_coverage",
            "important_negative_any_locator_coverage",
            "important_negative_all_locator_coverage",
        )
    }
    evidence_ratio = valid_hits / total_hits if total_hits else 0.0
    page_mapping_ratio = mapped_hits / total_hits if total_hits else 0.0
    status = "pass" if not issues and evidence_ratio == 1.0 and page_mapping_ratio == 1.0 else "fail"
    return {
        "schema_version": SCHEMA_VERSION,
        "status": status,
        "candidate_label": candidate_label,
        "route": route_name,
        "benchmark": {
            "id": manifest["benchmark_id"],
            "manifest_sha256": "2f905bd9a7ad07991fe215e0b82b3c7bfdcccbff9431ee5bd20095d99b8f4414",
            "hard_question_count": len(hard_questions),
        },
        "inputs": {
            "candidate_report": display_path(report_path),
            "candidate_report_sha256": sha256(report_path),
            "sections": display_path(sections_path),
            "sections_sha256": sha256(sections_path),
            "ensemble_plan": display_path(plan_path),
            "ensemble_plan_sha256": sha256(plan_path),
        },
        "metric_contract": {
            "exact_locator_identity": "paper_id plus PDF-page-N fragment",
            "claim_any": "at least one declared locator for one acceptable evidence claim",
            "claim_all": "every declared locator for one acceptable evidence claim",
            "all_source_note": "graph section routes can cover paper sources without directly returning claim-source records",
        },
        "evidence_validity": {
            "returned": total_hits,
            "valid": valid_hits,
            "invalid": total_hits - valid_hits,
            "ratio": evidence_ratio,
        },
        "page_locator_mapping": {
            "mapped": mapped_hits,
            "unmapped": total_hits - mapped_hits,
            "ratio": page_mapping_ratio,
        },
        "metrics": metrics,
        "issues": issues,
        "questions": per_question,
    }


def _markdown(result: dict[str, Any]) -> str:
    metrics = result["metrics"]
    lines = [
        f"# Hard-10 Graph Coverage: {result['candidate_label']}",
        "",
        f"Status: **{result['status']}**. Route: `{result['route']}`. This is a named graph-route reference unless the input report was produced by a real ensemble candidate.",
        "",
        "| Metric | Macro value |",
        "| --- | ---: |",
        f"| Required papers | {metrics['required_paper_coverage']:.2%} |",
        f"| Required paper sources | {metrics['required_paper_source_coverage']:.2%} |",
        f"| Required claim + paper sources | {metrics['required_all_source_coverage']:.2%} |",
        f"| Exact authoritative page locators | {metrics['exact_locator_recall']:.2%} |",
        f"| Atomic claims with any locator | {metrics['answer_claim_any_locator_coverage']:.2%} |",
        f"| Atomic claims with all locators | {metrics['answer_claim_all_locator_coverage']:.2%} |",
        f"| Important negatives with any locator | {metrics['important_negative_any_locator_coverage']:.2%} |",
        f"| Important negatives with all locators | {metrics['important_negative_all_locator_coverage']:.2%} |",
        "",
        f"Evidence validity: **{result['evidence_validity']['ratio']:.2%}**. Exact page mapping: **{result['page_locator_mapping']['ratio']:.2%}**.",
        "",
        "## Per question",
        "",
        "| Question | Papers | Paper sources | All sources | Locators | Answer any/all | Negative any/all |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in result["questions"]:
        lines.append(
            f"| `{row['id']}` | {row['required_paper_coverage']:.1%} | "
            f"{row['required_paper_source_coverage']:.1%} | {row['required_all_source_coverage']:.1%} | "
            f"{row['exact_locator_recall']:.1%} | "
            f"{row['answer_claim_any_locator_coverage']:.1%}/{row['answer_claim_all_locator_coverage']:.1%} | "
            f"{row['important_negative_any_locator_coverage']:.1%}/{row['important_negative_all_locator_coverage']:.1%} |"
        )
    if result["issues"]:
        lines.extend(["", "## Issues", "", *[f"- {issue}" for issue in result["issues"]]])
    return "\n".join(lines) + "\n"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--route", required=True)
    parser.add_argument("--sections", type=Path, required=True)
    parser.add_argument("--candidate-label", required=True)
    parser.add_argument("--plan", type=Path, default=ENSEMBLE_PLAN)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-markdown", type=Path, required=True)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        result = _evaluate(
            args.report.resolve(strict=True),
            args.route,
            args.sections.resolve(strict=True),
            args.candidate_label,
            args.plan.resolve(strict=True),
        )
        write_new(args.output_json, json.dumps(result, indent=2, ensure_ascii=False) + "\n")
        write_new(args.output_markdown, _markdown(result))
    except (EvaluationError, OSError, UnicodeError, KeyError, TypeError) as exc:
        print(json.dumps({"status": "fail", "error": str(exc)}, sort_keys=True), file=sys.stderr)
        return 2
    print(
        json.dumps(
            {
                "status": result["status"],
                "route": result["route"],
                "required_paper_coverage": result["metrics"]["required_paper_coverage"],
                "exact_locator_recall": result["metrics"]["exact_locator_recall"],
                "evidence_validity": result["evidence_validity"]["ratio"],
            },
            sort_keys=True,
        )
    )
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
