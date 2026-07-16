#!/usr/bin/env python3
"""Create and score deterministic grounded answer packs for the five hard questions."""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from _retrieval_eval import (
    AuthoritativeLedger,
    EvaluationError,
    load_json,
    load_jsonl,
    pretty_json,
    sha256_file,
)


SCRIPT = Path(__file__).resolve()
EVALUATION = SCRIPT.parents[1]
REPO = SCRIPT.parents[3]
REPORTS = EVALUATION / "reports"
SCHEMA_VERSION = "semantic-okf-endocrine-hygiene-hard-answer-comparison/1.1"
SHOWCASE_ID = "q030-causal-evidence-map"


def _atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(content, encoding="utf-8", newline="\n")
    temporary.replace(path)


def _selected_route(report: Mapping[str, Any], family: str) -> str | None:
    for row in report.get("families", []):
        if isinstance(row, dict) and row.get("family") == family:
            value = row.get("best_route")
            return value if isinstance(value, str) else None
    return None


def _route(report: Mapping[str, Any], family: str, route: str) -> dict[str, Any]:
    matches = [
        row
        for row in report.get("routes", [])
        if isinstance(row, dict) and row.get("family") == family and row.get("route") == route
    ]
    if len(matches) != 1:
        raise EvaluationError(f"expected one retrieval route for {family}/{route}")
    return matches[0]


def _query(route: Mapping[str, Any], identifier: str) -> dict[str, Any]:
    matches = [row for row in route.get("queries", []) if isinstance(row, dict) and row.get("question_id") == identifier]
    if len(matches) != 1:
        raise EvaluationError(f"expected one query row for {identifier}")
    return matches[0]


def _claim_candidates(
    query: Mapping[str, Any],
    ledger: AuthoritativeLedger,
    identity_by_source: Mapping[str, str],
) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    observed: set[tuple[str, str]] = set()
    for hit in query.get("hits", []):
        if not isinstance(hit, dict):
            continue
        source_id, record_id = hit.get("source_id"), hit.get("record_id")
        if not isinstance(source_id, str) or not source_id.startswith("claims-") or not isinstance(record_id, str):
            continue
        identity = (source_id, record_id)
        if identity in observed:
            continue
        observed.add(identity)
        record = ledger.by_identity.get(identity)
        if record is None:
            continue
        attributes = record.get("attributes")
        if not isinstance(attributes, dict):
            continue
        interpretation = attributes.get("interpretation")
        locator = attributes.get("evidence_locator")
        text_sha256 = attributes.get("evidence_text_sha256")
        if not all(isinstance(value, str) and value for value in (interpretation, locator, text_sha256)):
            continue
        candidates.append(
            {
                "rank": hit.get("rank"),
                "claim_id": record_id,
                "statement": interpretation,
                "paper_id": identity_by_source[source_id],
                "source_id": source_id,
                "concept_path": record["concept_path"],
                "source_path": record["source_path"],
                "record_sha256": record["record_sha256"],
                "evidence_locator": locator,
                "evidence_text_sha256": text_sha256,
            }
        )
    return candidates


def _diversify_claims(candidates: Sequence[dict[str, Any]], maximum: int) -> list[dict[str, Any]]:
    """Retain one claim per retrieved paper before filling remaining ranked slots."""

    selected: list[dict[str, Any]] = []
    selected_ids: set[str] = set()
    papers: set[str] = set()
    for candidate in candidates:
        if candidate["paper_id"] not in papers:
            selected.append(candidate)
            selected_ids.add(candidate["claim_id"])
            papers.add(candidate["paper_id"])
            if len(selected) == maximum:
                return selected
    for candidate in candidates:
        if candidate["claim_id"] not in selected_ids:
            selected.append(candidate)
            selected_ids.add(candidate["claim_id"])
            if len(selected) == maximum:
                break
    return selected


def _evidence_ids(truth: Mapping[str, Any], selected: Sequence[Mapping[str, Any]]) -> set[str]:
    signatures = {(item["paper_id"], item["evidence_text_sha256"]) for item in selected}
    return {
        item["id"]
        for item in truth["authoritative_evidence"]
        if (item["paper_id"], item["text_sha256"]) in signatures
    }


def _fraction(values: Iterable[bool]) -> float:
    items = list(values)
    return sum(items) / len(items) if items else 1.0


def _load_claim_requirements(
    path: Path,
    truths: Mapping[str, Mapping[str, Any]],
) -> dict[str, dict[str, list[dict[str, Any]]]]:
    """Load the independently reviewed exact-claim requirements and bind them to ground-truth atoms."""

    value = load_json(path)
    if set(value) != {"schema_version", "contract", "questions"}:
        raise EvaluationError("hard-claim requirements have unexpected or missing top-level members")
    if value.get("schema_version") != "semantic-okf-endocrine-hygiene-hard-claim-requirements/1.0":
        raise EvaluationError("hard-claim requirements have an unsupported schema_version")
    if not isinstance(value.get("contract"), str) or not value["contract"]:
        raise EvaluationError("hard-claim requirements have no non-empty contract")
    rows = value.get("questions")
    if not isinstance(rows, list) or not all(isinstance(row, dict) for row in rows):
        raise EvaluationError("hard-claim requirements questions must be an array of objects")
    identifiers = [row.get("id") for row in rows]
    if not all(isinstance(identifier, str) and identifier for identifier in identifiers):
        raise EvaluationError("hard-claim requirements contain an invalid question ID")
    if len(set(identifiers)) != len(identifiers):
        raise EvaluationError("hard-claim requirements contain duplicate question IDs")
    if set(identifiers) != set(truths):
        raise EvaluationError("hard-claim requirements and hard ground truth have different question IDs")
    result: dict[str, dict[str, list[dict[str, Any]]]] = {}
    for row in rows:
        identifier = row["id"]
        expected_truth = truths[identifier]["ground_truth"]
        checked_groups: dict[str, list[dict[str, Any]]] = {}
        for group_name in ("answer_claims", "important_negatives"):
            groups = row.get(group_name)
            if not isinstance(groups, list) or not all(isinstance(group, dict) for group in groups):
                raise EvaluationError(f"{identifier}.{group_name} must be an array of objects")
            expected_ids = [group.get("id") for group in expected_truth[group_name]]
            actual_ids = [group.get("id") for group in groups]
            if actual_ids != expected_ids:
                raise EvaluationError(
                    f"{identifier}.{group_name} IDs do not exactly match the ground-truth atoms"
                )
            checked: list[dict[str, Any]] = []
            for group in groups:
                if set(group) != {"id", "required_claim_ids"}:
                    raise EvaluationError(
                        f"{identifier}.{group_name}.{group.get('id')} has unexpected members"
                    )
                claim_ids = group.get("required_claim_ids")
                if (
                    not isinstance(claim_ids, list)
                    or not claim_ids
                    or not all(isinstance(claim_id, str) and claim_id for claim_id in claim_ids)
                    or len(set(claim_ids)) != len(claim_ids)
                    or claim_ids != sorted(claim_ids)
                ):
                    raise EvaluationError(
                        f"{identifier}.{group_name}.{group.get('id')} required_claim_ids "
                        "must be non-empty, sorted, and unique"
                    )
                checked.append({"id": group["id"], "required_claim_ids": claim_ids})
            checked_groups[group_name] = checked
        result[identifier] = checked_groups
    return result


def _score_answer(
    truth: Mapping[str, Any],
    requirements: Mapping[str, Sequence[Mapping[str, Any]]],
    claims: Sequence[dict[str, Any]],
) -> dict[str, Any]:
    ground_truth = truth["ground_truth"]
    covered = _evidence_ids(truth, claims)
    all_evidence = {item["id"] for item in truth["authoritative_evidence"]}
    required_papers = set(ground_truth["required_paper_ids"])
    present_papers = {item["paper_id"] for item in claims}
    selected_claim_ids = {item["claim_id"] for item in claims}
    atomic = requirements["answer_claims"]
    negatives = requirements["important_negatives"]
    exact_allowed_claim_ids = {
        claim_id
        for group_name in ("answer_claims", "important_negatives")
        for group in requirements[group_name]
        for claim_id in group["required_claim_ids"]
    }
    valid_claims = [
        bool(item["claim_id"])
        and bool(item["concept_path"])
        and bool(item["source_path"])
        and bool(item["record_sha256"])
        and bool(item["evidence_locator"])
        and bool(item["evidence_text_sha256"])
        for item in claims
    ]
    return {
        "response_contract": 1.0,
        "grounding": 1.0 if claims else 0.0,
        "ledger_evidence_validity": _fraction(valid_claims) if claims else 0.0,
        "required_paper_coverage": len(required_papers & present_papers) / len(required_papers),
        "authoritative_evidence_completeness": len(covered) / len(all_evidence),
        "atomic_reviewed_claim_fidelity": _fraction(
            set(item["required_claim_ids"]).issubset(selected_claim_ids) for item in atomic
        ),
        "important_negative_reviewed_claim_fidelity": _fraction(
            set(item["required_claim_ids"]).issubset(selected_claim_ids) for item in negatives
        ),
        "exact_required_claim_precision": (
            len(selected_claim_ids & exact_allowed_claim_ids) / len(selected_claim_ids)
            if selected_claim_ids
            else 0.0
        ),
        "covered_required_claim_ids": sorted(selected_claim_ids & exact_allowed_claim_ids),
        "missing_required_claim_ids": sorted(exact_allowed_claim_ids - selected_claim_ids),
        "covered_evidence_ids": sorted(covered),
        "covered_paper_ids": sorted(required_papers & present_papers),
    }


def _answer(question: str, claims: Sequence[dict[str, Any]]) -> dict[str, Any]:
    summary = " ".join(
        f"{item['statement'].rstrip('.')} ({item['paper_id']}, {item['evidence_locator']})."
        for item in claims
    )
    return {
        "question": question,
        "summary": summary or None,
        "claims": [
            {
                "claim_id": item["claim_id"],
                "statement": item["statement"],
                "paper_id": item["paper_id"],
                "evidence_locator": item["evidence_locator"],
            }
            for item in claims
        ],
        "evidence": [
            {
                key: item[key]
                for key in (
                    "claim_id",
                    "paper_id",
                    "source_id",
                    "concept_path",
                    "source_path",
                    "record_sha256",
                    "evidence_locator",
                    "evidence_text_sha256",
                )
            }
            for item in claims
        ],
    }


def _mean_metrics(outputs: Sequence[Mapping[str, Any]]) -> dict[str, float]:
    names = (
        "response_contract",
        "grounding",
        "ledger_evidence_validity",
        "required_paper_coverage",
        "authoritative_evidence_completeness",
        "atomic_reviewed_claim_fidelity",
        "important_negative_reviewed_claim_fidelity",
        "exact_required_claim_precision",
    )
    return {name: statistics.fmean(float(row["metrics"][name]) for row in outputs) for name in names}


def compare(args: argparse.Namespace) -> dict[str, Any]:
    retrieval = load_json(args.retrieval_report)
    truths = load_jsonl(args.ground_truth)
    questions = {row["id"]: row["question"] for row in load_jsonl(args.hard_questions)}
    truth_by_id = {row["id"]: row for row in truths}
    if set(questions) != set(truth_by_id):
        raise EvaluationError("hard question and ground-truth identities differ")
    requirements_by_id = _load_claim_requirements(args.claim_requirements, truth_by_id)
    combination = load_json(args.source_combination)
    identity = combination.get("identity_by_source")
    if not isinstance(identity, dict):
        raise EvaluationError("source combination has no identity map")
    families: list[dict[str, Any]] = []
    for family in ("legacy", "embeddings", "classical", "entity-graph", "adaptive", "ensemble"):
        retrieval_best_route = _selected_route(retrieval, family)
        bundle = args.run_dir / "bundles" / f"{family}-a"
        route_names = [
            row["route"]
            for row in retrieval.get("routes", [])
            if isinstance(row, dict)
            and row.get("family") == family
            and row.get("overall") is not None
            and isinstance(row.get("route"), str)
        ]
        if retrieval_best_route is None or not bundle.is_dir() or not route_names:
            family_row = next((row for row in retrieval["families"] if row["family"] == family), {})
            families.append(
                {
                    "family": family,
                    "status": "not-applicable",
                    "route": None,
                    "retrieval_best_route": None,
                    "reason": family_row.get("reason") or "no compatible search/answer route",
                    "metrics": None,
                    "answers": [],
                    "route_candidates": [],
                }
            )
            continue
        ledger = AuthoritativeLedger(bundle)
        ledger_claim_ids = {
            record_id
            for source_id, record_id in ledger.by_identity
            if source_id.startswith("claims-")
        }
        required_claim_ids = {
            claim_id
            for question_requirements in requirements_by_id.values()
            for group_name in ("answer_claims", "important_negatives")
            for group in question_requirements[group_name]
            for claim_id in group["required_claim_ids"]
        }
        missing_required_claims = sorted(required_claim_ids - ledger_claim_ids)
        if missing_required_claims:
            raise EvaluationError(
                f"{family} ledger is missing required reviewed claims: {missing_required_claims}"
            )
        candidates_by_route: list[dict[str, Any]] = []
        for route_name in route_names:
            route = _route(retrieval, family, route_name)
            outputs: list[dict[str, Any]] = []
            for identifier, truth in truth_by_id.items():
                query = _query(route, identifier)
                candidates = _claim_candidates(query, ledger, identity)
                selected = _diversify_claims(candidates, args.max_claims)
                outputs.append(
                    {
                        "question_id": identifier,
                        "answer": _answer(questions[identifier], selected),
                        "metrics": _score_answer(truth, requirements_by_id[identifier], selected),
                    }
                )
            candidates_by_route.append(
                {"route": route_name, "metrics": _mean_metrics(outputs), "answers": outputs}
            )
        winner = max(
            candidates_by_route,
            key=lambda row: (
                row["metrics"]["atomic_reviewed_claim_fidelity"],
                row["metrics"]["important_negative_reviewed_claim_fidelity"],
                row["metrics"]["authoritative_evidence_completeness"],
                row["metrics"]["required_paper_coverage"],
                row["metrics"]["exact_required_claim_precision"],
                row["route"],
            ),
        )
        families.append(
            {
                "family": family,
                "status": "pass",
                "route": winner["route"],
                "retrieval_best_route": retrieval_best_route,
                "reason": None,
                "metrics": winner["metrics"],
                "answers": winner["answers"],
                "route_candidates": [
                    {"route": row["route"], "metrics": row["metrics"]} for row in candidates_by_route
                ],
            }
        )
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "pass",
        "method": {
            "kind": "deterministic-extractive-answer-pack",
            "ground_truth_blind_generation": True,
            "selection": "top retrieved reviewed claims, diversified one per paper before rank fill",
            "maximum_claims": args.max_claims,
            "natural_language_model_used": False,
            "claim_requirements": {
                "path": args.claim_requirements.relative_to(REPO).as_posix(),
                "sha256": sha256_file(args.claim_requirements),
            },
            "route_selection_for_reporting": "best hard-answer metrics after every route was scored; generation within each route remains ground-truth blind",
            "scoring": "exact reviewed claim IDs per atomic answer and important negative; authoritative passage evidence completeness is reported separately",
            "interpretation": "This isolates consultation evidence selection. Reviewed-claim fidelity means exact inclusion of independently required ledger claim IDs; it is not a score of free-form semantic answer quality or prose fluency.",
        },
        "showcase_question_id": SHOWCASE_ID,
        "families": families,
    }


def _pct(value: Any) -> str:
    return "N/A" if value is None else f"{100 * float(value):.1f}%"


def _render_markdown(report: Mapping[str, Any]) -> str:
    lines = [
        "# Hard-Question Grounded Answer Comparison",
        "",
        "These are actual deterministic extractive answer packs from each compatible consultation route. Generation is ground-truth blind: the same post-retrieval rule selects top reviewed claims, diversifies once by paper, and copies their reviewed interpretations with exact evidence bindings. No MCP or language model participates. The answer metrics below are exact reviewed-claim fidelity and evidence-selection measures; they do not measure free-form semantic answer quality or prose fluency.",
        "",
        "| Family | Answer-best route | Retrieval-best route | Atomic claim fidelity | Required papers | Evidence completeness | Negative claim fidelity | Exact-claim precision | Grounding | Ledger evidence valid |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for family in report["families"]:
        metrics = family["metrics"]
        if metrics is None:
            lines.append(f"| {family['family']} | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |")
            continue
        lines.append(
            "| {family} | {route} | {retrieval_route} | {atomic} | {papers} | {evidence} | {negative} | {precision} | {grounding} | {valid} |".format(
                family=family["family"], route=family["route"],
                retrieval_route=family["retrieval_best_route"],
                atomic=_pct(metrics["atomic_reviewed_claim_fidelity"]),
                papers=_pct(metrics["required_paper_coverage"]),
                evidence=_pct(metrics["authoritative_evidence_completeness"]),
                negative=_pct(metrics["important_negative_reviewed_claim_fidelity"]),
                precision=_pct(metrics["exact_required_claim_precision"]),
                grounding=_pct(metrics["grounding"]), valid=_pct(metrics["ledger_evidence_validity"]),
            )
        )
    lines.extend(["", f"## Showcase: `{report['showcase_question_id']}`", ""])
    for family in report["families"]:
        lines.extend([f"### {family['family']}", ""])
        if family["metrics"] is None:
            lines.extend([f"N/A — {family['reason']}", ""])
            continue
        answer = next(item for item in family["answers"] if item["question_id"] == report["showcase_question_id"])
        lines.append(answer["answer"]["question"])
        lines.append("")
        for claim in answer["answer"]["claims"]:
            lines.append(
                f"- {claim['statement']} (`{claim['paper_id']}`, `{claim['claim_id']}`, `{claim['evidence_locator']}`)"
            )
        lines.append("")
    return "\n".join(lines)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument(
        "--retrieval-report",
        type=Path,
        required=True,
        help="Detailed retrieval report with per-query hits.",
    )
    parser.add_argument("--ground-truth", type=Path, default=EVALUATION / "benchmark/hard-ground-truth.jsonl")
    parser.add_argument("--hard-questions", type=Path, default=EVALUATION / "benchmark/hard-questions.jsonl")
    parser.add_argument(
        "--claim-requirements",
        type=Path,
        default=EVALUATION / "benchmark/hard-claim-requirements.json",
    )
    parser.add_argument("--source-combination", type=Path, default=EVALUATION / "corpus/source-combination.json")
    parser.add_argument("--output-json", type=Path, default=REPORTS / "hard-answer-comparison.json")
    parser.add_argument("--output-markdown", type=Path, default=REPORTS / "hard-answer-comparison.md")
    parser.add_argument("--max-claims", type=int, default=12)
    args = parser.parse_args(argv)
    for name in (
        "run_dir",
        "retrieval_report",
        "ground_truth",
        "hard_questions",
        "claim_requirements",
        "source_combination",
        "output_json",
        "output_markdown",
    ):
        setattr(args, name, getattr(args, name).resolve())
    if not 1 <= args.max_claims <= 50:
        parser.error("--max-claims must be from 1 through 50")
    return args


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        report = compare(args)
        _atomic_write(args.output_json, pretty_json(report))
        _atomic_write(args.output_markdown, _render_markdown(report))
    except EvaluationError as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1
    print(json.dumps({"status": "pass", "families": len(report["families"]), "showcase": SHOWCASE_ID}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
