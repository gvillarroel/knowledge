#!/usr/bin/env python3
"""Create and score actual no-MCP extractive answers for all Astro alternatives."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import statistics
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


SCRIPT = Path(__file__).resolve()
EVALUATION = SCRIPT.parents[1]
REPO = SCRIPT.parents[3]
REPORTS = EVALUATION / "reports"
SCHEMA = "semantic-okf-astro-hard-answer-comparison/1.0"
SHOWCASE_ID = "q040"
TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9._/-]*", re.IGNORECASE)
SENTENCE_RE = re.compile(r"(?<=[.!?])\s+|\n{2,}")
STOPWORDS = frozenset(
    "a about all also an and are as at be but by can compare describe do does explain for from how if in "
    "into is it its of on or should than that the their these they this to using was were what when where which why with"
    .split()
)


class AnswerError(RuntimeError):
    """Describe malformed retrieval or ground-truth answer inputs."""


def strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    """Reject duplicate JSON members."""

    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise AnswerError(f"duplicate JSON member: {key}")
        result[key] = value
    return result


def load_json(path: Path) -> dict[str, Any]:
    """Load one strict JSON object."""

    try:
        value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=strict_object)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise AnswerError(f"cannot load JSON object {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise AnswerError(f"expected JSON object: {path}")
    return value


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    """Load strict nonblank JSONL rows."""

    rows: list[dict[str, Any]] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        raise AnswerError(f"cannot load JSONL {path}: {exc}") from exc
    for number, line in enumerate(lines, 1):
        if not line.strip():
            raise AnswerError(f"blank JSONL row at {path}:{number}")
        try:
            value = json.loads(line, object_pairs_hook=strict_object)
        except json.JSONDecodeError as exc:
            raise AnswerError(f"invalid JSONL at {path}:{number}: {exc}") from exc
        if not isinstance(value, dict):
            raise AnswerError(f"expected object at {path}:{number}")
        rows.append(value)
    if not rows:
        raise AnswerError(f"empty JSONL: {path}")
    return rows


def pretty_json(value: Any) -> str:
    """Serialize deterministic report JSON."""

    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n"


def sha256_file(path: Path) -> str:
    """Hash one file."""

    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_write(path: Path, content: str) -> None:
    """Publish a compact report atomically."""

    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(content, encoding="utf-8", newline="\n")
    os.replace(temporary, path)


def tokens(value: str) -> set[str]:
    """Return nontrivial lower-case answer-selection tokens."""

    return {
        token for token in TOKEN_RE.findall(value.casefold())
        if len(token) >= 2 and token not in STOPWORDS
    }


def concise_extract(text: str, query: str, *, maximum: int = 420) -> str:
    """Select a ground-truth-blind query-overlapping sentence from one hit."""

    query_terms = tokens(query)
    candidates = [segment.strip() for segment in SENTENCE_RE.split(text) if segment.strip()]
    if not candidates:
        return text.strip()[:maximum]
    ranked = sorted(
        enumerate(candidates),
        key=lambda row: (-len(tokens(row[1]) & query_terms), row[0]),
    )
    selected = ranked[0][1]
    return selected if len(selected) <= maximum else selected[: maximum - 1].rstrip() + "…"


def diversify(hits: Sequence[Mapping[str, Any]], maximum: int) -> list[dict[str, Any]]:
    """Retain one valid passage per document before filling remaining ranks."""

    valid = [
        dict(hit) for hit in hits
        if isinstance(hit, Mapping)
        and isinstance(hit.get("evidence_validation"), Mapping)
        and hit["evidence_validation"].get("valid") is True
    ]
    result: list[dict[str, Any]] = []
    selected: set[tuple[Any, Any]] = set()
    documents: set[str] = set()
    for hit in valid:
        document = hit.get("document_id")
        key = (hit.get("source_id"), hit.get("retrieval_id"))
        if isinstance(document, str) and document not in documents:
            result.append(hit)
            selected.add(key)
            documents.add(document)
            if len(result) == maximum:
                return result
    for hit in valid:
        key = (hit.get("source_id"), hit.get("retrieval_id"))
        if key not in selected:
            result.append(hit)
            selected.add(key)
            if len(result) == maximum:
                break
    return result


def evidence_row(hit: Mapping[str, Any]) -> dict[str, Any]:
    """Project one independently valid consultation hit into answer evidence."""

    return {
        "document_id": hit.get("document_id"),
        "source_id": hit.get("source_id"),
        "record_id": hit.get("record_id"),
        "concept_path": hit.get("concept_path"),
        "source_path": hit.get("source_path"),
        "record_sha256": hit.get("record_sha256"),
        "locator": hit.get("locator"),
        "text_sha256": hit.get("text_sha256"),
    }


def make_answer(question_id: str, question: str, hits: Sequence[Mapping[str, Any]], maximum: int) -> dict[str, Any]:
    """Create one actual structured extractive answer without reading ground truth."""

    selected = diversify(hits, maximum)
    claims = []
    for number, hit in enumerate(selected, 1):
        text = hit.get("text")
        if not isinstance(text, str) or not text.strip():
            continue
        claims.append(
            {
                "id": f"extract-{number:02d}",
                "statement": concise_extract(text, question),
                "document_id": hit.get("document_id"),
                "evidence_rank": int(hit.get("rank", number)),
            }
        )
    evidence = [evidence_row(hit) for hit in selected]
    summary = " ".join(
        f"[{claim['document_id']}] {claim['statement']}" for claim in claims
    ) or None
    return {
        "question_id": question_id,
        "question": question,
        "answer": {
            "summary": summary,
            "claims": claims,
            "document_ids": sorted({
                str(claim["document_id"]) for claim in claims if isinstance(claim.get("document_id"), str)
            }),
        } if claims else None,
        "evidence": evidence if claims else [],
    }


def hit_range(hit: Mapping[str, Any], document_body_lengths: Mapping[str, int]) -> tuple[int, int] | None:
    """Return an authoritative body range for one validated hit."""

    document = hit.get("document_id")
    locator = hit.get("locator")
    if not isinstance(document, str) or not isinstance(locator, Mapping):
        return None
    if locator.get("kind") == "record":
        length = document_body_lengths.get(document)
        return (0, length) if isinstance(length, int) and length > 0 else None
    if locator.get("kind") != "character-range":
        return None
    start, end = locator.get("start"), locator.get("end")
    if isinstance(start, bool) or isinstance(end, bool) or not isinstance(start, int) or not isinstance(end, int):
        return None
    return (start, end)


def truth_groups(value: Any, label: str) -> list[dict[str, Any]]:
    """Validate atomic truth groups used for mechanical sufficiency scoring."""

    if not isinstance(value, list) or not all(isinstance(row, dict) for row in value):
        raise AnswerError(f"{label} must be an array of objects")
    result: list[dict[str, Any]] = []
    for row in value:
        identifier = row.get("id")
        evidence_ids = row.get("evidence_ids")
        if not isinstance(identifier, str) or not identifier:
            raise AnswerError(f"{label} contains an invalid id")
        if (
            not isinstance(evidence_ids, list) or not evidence_ids
            or any(not isinstance(item, str) or not item for item in evidence_ids)
        ):
            raise AnswerError(f"{label}.{identifier} has invalid evidence_ids")
        result.append({"id": identifier, "evidence_ids": list(evidence_ids)})
    return result


def fraction(values: Iterable[bool]) -> float:
    """Return a total-safe boolean mean."""

    rows = list(values)
    return sum(rows) / len(rows) if rows else 1.0


def score_answer(
    truth: Mapping[str, Any],
    selected_hits: Sequence[Mapping[str, Any]],
    document_body_lengths: Mapping[str, int],
) -> dict[str, Any]:
    """Score retrieval-grounded evidence sufficiency separately from prose fluency."""

    evidence_rows = truth.get("authoritative_evidence")
    ground_truth = truth.get("ground_truth")
    if not isinstance(evidence_rows, list) or not isinstance(ground_truth, Mapping):
        raise AnswerError(f"ground truth {truth.get('id')} has invalid evidence/ground_truth")
    evidence: dict[str, Mapping[str, Any]] = {}
    for row in evidence_rows:
        if not isinstance(row, Mapping) or not isinstance(row.get("id"), str):
            raise AnswerError(f"ground truth {truth.get('id')} contains invalid evidence")
        evidence[row["id"]] = row
    claims = truth_groups(ground_truth.get("answer_claims"), f"{truth.get('id')}.answer_claims")
    negatives = truth_groups(
        ground_truth.get("important_negatives"), f"{truth.get('id')}.important_negatives"
    )
    covered: set[str] = set()
    for identifier, row in evidence.items():
        document = row.get("document_id")
        start, end = row.get("start_char"), row.get("end_char")
        if not isinstance(document, str) or not isinstance(start, int) or not isinstance(end, int):
            raise AnswerError(f"ground truth evidence {identifier} lacks document/range")
        for hit in selected_hits:
            if hit.get("document_id") != document:
                continue
            interval = hit_range(hit, document_body_lengths)
            if interval is not None and interval[0] <= start and interval[1] >= end:
                covered.add(identifier)
                break
    required_documents = ground_truth.get("required_document_ids")
    if not isinstance(required_documents, list) or not required_documents:
        raise AnswerError(f"ground truth {truth.get('id')} lacks required_document_ids")
    selected_documents = {
        hit.get("document_id") for hit in selected_hits if isinstance(hit.get("document_id"), str)
    }
    valid = [
        isinstance(hit.get("evidence_validation"), Mapping)
        and hit["evidence_validation"].get("valid") is True
        for hit in selected_hits
    ]
    return {
        "response_contract": 1.0,
        "grounding": 1.0 if selected_hits and all(valid) else 0.0,
        "evidence_validity": fraction(valid) if selected_hits else 0.0,
        "required_document_coverage": len(set(required_documents) & selected_documents) / len(set(required_documents)),
        "authoritative_evidence_completeness": len(covered) / len(evidence) if evidence else 1.0,
        "atomic_claim_evidence_completeness": fraction(
            set(row["evidence_ids"]).issubset(covered) for row in claims
        ),
        "important_negative_evidence_completeness": fraction(
            set(row["evidence_ids"]).issubset(covered) for row in negatives
        ),
        "covered_evidence_ids": sorted(covered),
        "missing_evidence_ids": sorted(set(evidence) - covered),
        "covered_document_ids": sorted(set(required_documents) & selected_documents),
    }


def mean_metrics(outputs: Sequence[Mapping[str, Any]]) -> dict[str, float]:
    """Average hard-question answer metrics."""

    names = (
        "response_contract", "grounding", "evidence_validity", "required_document_coverage",
        "authoritative_evidence_completeness", "atomic_claim_evidence_completeness",
        "important_negative_evidence_completeness",
    )
    return {
        name: statistics.fmean(float(row["metrics"][name]) for row in outputs)
        for name in names
    }


def route_queries(retrieval: Mapping[str, Any], family: str, route: str) -> Mapping[str, Mapping[str, Any]]:
    """Index one detailed route by question ID."""

    row = next(
        (
            candidate for candidate in retrieval.get("routes", [])
            if isinstance(candidate, Mapping)
            and candidate.get("family") == family
            and candidate.get("route") == route
        ),
        None,
    )
    if not isinstance(row, Mapping) or row.get("status") != "pass":
        raise AnswerError(f"missing successful retrieval route {family}/{route}")
    queries = row.get("queries")
    if not isinstance(queries, list):
        raise AnswerError(f"retrieval route {family}/{route} has no detailed queries")
    result = {
        query["question_id"]: query
        for query in queries
        if isinstance(query, Mapping) and isinstance(query.get("question_id"), str)
    }
    if len(result) != len(queries):
        raise AnswerError(f"retrieval route {family}/{route} has duplicate/invalid query IDs")
    return result


def body_lengths(run_dir: Path) -> dict[str, int]:
    """Load document body lengths from the authoritative legacy ledger and explicit crosswalk."""

    combination = load_json(EVALUATION / "corpus/source-combination.json")
    records = combination.get("records")
    if not isinstance(records, list):
        raise AnswerError("source-combination has no records")
    identity = {
        (row["source_id"], row["record_id"]): row["document_id"]
        for row in records if isinstance(row, dict)
    }
    ledger = load_jsonl(run_dir / "bundles/legacy-a/semantic/records.jsonl")
    result = {}
    for record in ledger:
        key = (record.get("source_id"), record.get("record_id"))
        document = identity.get(key)
        body = record.get("body")
        if isinstance(document, str) and isinstance(body, str):
            result[document] = len(body)
    if len(result) != len(identity):
        raise AnswerError("authoritative ledger/body-length crosswalk is not total")
    return result


def compare(args: argparse.Namespace) -> dict[str, Any]:
    """Score every route, choose one answer route per family, and retain all answers."""

    retrieval = load_json(args.retrieval_report)
    truths = load_jsonl(args.ground_truth)
    if len(truths) != 10:
        raise AnswerError("hard ground truth must contain exactly 10 questions")
    truth_by_id = {row.get("id"): row for row in truths}
    if len(truth_by_id) != 10 or any(not isinstance(key, str) for key in truth_by_id):
        raise AnswerError("hard ground truth has invalid/duplicate IDs")
    if args.showcase_id not in truth_by_id:
        raise AnswerError(f"showcase question is absent: {args.showcase_id}")
    lengths = body_lengths(args.run_dir)
    families: list[dict[str, Any]] = []
    retrieval_best = {
        row["family"]: row.get("best_route")
        for row in retrieval.get("families", []) if isinstance(row, dict)
    }
    route_names: dict[str, list[str]] = {}
    for row in retrieval.get("routes", []):
        if isinstance(row, dict) and row.get("status") == "pass":
            route_names.setdefault(str(row.get("family")), []).append(str(row.get("route")))
    for family in ("legacy", "embeddings", "classical", "adaptive", "entity-graph", "ensemble"):
        candidates: list[dict[str, Any]] = []
        for route in route_names.get(family, []):
            queries = route_queries(retrieval, family, route)
            outputs: list[dict[str, Any]] = []
            for identifier, truth in truth_by_id.items():
                query = queries.get(identifier)
                if not isinstance(query, Mapping) or not isinstance(query.get("hits"), list):
                    raise AnswerError(f"{family}/{route} lacks hard query {identifier}")
                selected = diversify(query["hits"], args.max_passages)
                answer = make_answer(identifier, str(truth.get("question")), query["hits"], args.max_passages)
                outputs.append(
                    {
                        "question_id": identifier,
                        "answer": answer,
                        "metrics": score_answer(truth, selected, lengths),
                    }
                )
            candidates.append({"route": route, "metrics": mean_metrics(outputs), "answers": outputs})
        if not candidates:
            raise AnswerError(f"no successful answer route for family {family}")
        winner = max(
            candidates,
            key=lambda row: (
                row["metrics"]["atomic_claim_evidence_completeness"],
                row["metrics"]["important_negative_evidence_completeness"],
                row["metrics"]["authoritative_evidence_completeness"],
                row["metrics"]["required_document_coverage"],
                row["route"],
            ),
        )
        families.append(
            {
                "family": family,
                "status": "pass",
                "route": winner["route"],
                "retrieval_best_route": retrieval_best.get(family),
                "metrics": winner["metrics"],
                "answers": winner["answers"],
                "route_candidates": [
                    {"route": row["route"], "metrics": row["metrics"]} for row in candidates
                ],
            }
        )
    return {
        "schema_version": SCHEMA,
        "status": "pass",
        "method": {
            "kind": "deterministic-query-overlap extractive answer pack",
            "ground_truth_blind_generation": True,
            "maximum_passages": args.max_passages,
            "selection": "top valid passages, one per document before rank fill; one query-overlapping extract per passage",
            "route_selection_for_reporting": "every route scored; family answer route selected by frozen hard-evidence sufficiency order",
            "semantic_model_used": False,
            "mcp_used": False,
            "interpretation": "Atomic and negative metrics measure whether selected exact passages contain every curated evidence span. They are mechanical evidence-sufficiency proxies, not model-judged prose correctness or fluency.",
            "ground_truth": {
                "path": args.ground_truth.relative_to(REPO).as_posix(),
                "sha256": sha256_file(args.ground_truth),
            },
        },
        "showcase_question_id": args.showcase_id,
        "families": families,
    }


def pct(value: Any) -> str:
    """Render one ratio as a percentage."""

    return f"{100.0 * float(value):.1f}%"


def render_markdown(report: Mapping[str, Any]) -> str:
    """Render metrics plus the requested all-alternative hard answer showcase."""

    lines = [
        "# Astro Hard-Question Answer Comparison",
        "",
        "These are actual deterministic extractive answers produced from each alternative's own ranked, independently valid passages. Generation does not read ground truth and uses no language model or MCP. The mechanical completeness metrics indicate evidence sufficiency, not prose fluency or a semantic judge score.",
        "",
        "| Family | Answer-best route | Retrieval-best route | Atomic evidence | Required documents | Evidence completeness | Negative evidence | Grounding | Evidence valid |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in report["families"]:
        metrics = row["metrics"]
        lines.append(
            f"| {row['family']} | {row['route']} | {row['retrieval_best_route']} | "
            f"{pct(metrics['atomic_claim_evidence_completeness'])} | {pct(metrics['required_document_coverage'])} | "
            f"{pct(metrics['authoritative_evidence_completeness'])} | "
            f"{pct(metrics['important_negative_evidence_completeness'])} | {pct(metrics['grounding'])} | "
            f"{pct(metrics['evidence_validity'])} |"
        )
    lines.extend(["", f"## One difficult question: `{report['showcase_question_id']}`", ""])
    for row in report["families"]:
        answer_row = next(
            item for item in row["answers"] if item["question_id"] == report["showcase_question_id"]
        )
        answer = answer_row["answer"]
        lines.extend([f"### {row['family']} — `{row['route']}`", "", answer["question"], ""])
        if answer["answer"] is None:
            lines.extend(["No supported extractive answer was returned.", ""])
            continue
        lines.extend([answer["answer"]["summary"], "", "Evidence:", ""])
        for evidence in answer["evidence"]:
            locator = json.dumps(evidence["locator"], ensure_ascii=False, sort_keys=True, separators=(",", ":"))
            lines.append(
                f"- `{evidence['document_id']}` — `{evidence['concept_path']}` — `{locator}` — `{evidence['text_sha256']}`"
            )
        metrics = answer_row["metrics"]
        lines.extend(
            [
                "",
                f"Mechanical score for this answer: atomic evidence {pct(metrics['atomic_claim_evidence_completeness'])}; required documents {pct(metrics['required_document_coverage'])}; important negatives {pct(metrics['important_negative_evidence_completeness'])}.",
                "",
            ]
        )
    rendered = "\n".join(lines)
    return "\n".join(line.rstrip() for line in rendered.split("\n"))


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse comparison inputs."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--retrieval-report", type=Path, required=True)
    parser.add_argument("--ground-truth", type=Path, default=EVALUATION / "benchmark/hard-ground-truth.jsonl")
    parser.add_argument("--showcase-id", default=SHOWCASE_ID)
    parser.add_argument("--max-passages", type=int, default=12)
    parser.add_argument("--output-json", type=Path, default=REPORTS / "hard-answer-comparison.json")
    parser.add_argument("--output-markdown", type=Path, default=REPORTS / "hard-answer-comparison.md")
    args = parser.parse_args(argv)
    for name in ("run_dir", "retrieval_report", "ground_truth", "output_json", "output_markdown"):
        setattr(args, name, getattr(args, name).resolve())
    if not 1 <= args.max_passages <= 50:
        parser.error("--max-passages must be from 1 through 50")
    return args


def main(argv: Sequence[str] | None = None) -> int:
    """Publish the all-alternative hard answer comparison."""

    args = parse_args(argv)
    try:
        report = compare(args)
        atomic_write(args.output_json, pretty_json(report))
        atomic_write(args.output_markdown, render_markdown(report))
    except (AnswerError, OSError, UnicodeError, ValueError, TypeError, KeyError) as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1
    print(json.dumps({"status": "pass", "families": len(report["families"]), "showcase": args.showcase_id}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
