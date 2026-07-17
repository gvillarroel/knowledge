#!/usr/bin/env python3
"""Validate and summarize actual grounded answers for the ten hard questions."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path, PurePosixPath
from statistics import mean
from typing import Any


SCHEMA_VERSION = "semantic-okf-grounded-answer-comparison/1.0"
PAPER_RE = re.compile(r"(\d{4})[.-](\d{5})v(\d+)", re.IGNORECASE)
METRICS = (
    "response_contract",
    "evidence_validity",
    "grounding",
    "claim_correctness",
    "semantic_completeness",
    "exact_atomic_evidence_coverage",
    "required_paper_coverage",
    "required_source_coverage",
    "important_negative_coverage",
)


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _paper_id(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    match = PAPER_RE.search(value)
    return f"{match.group(1)}.{match.group(2)}v{match.group(3).lower()}" if match else None


def _normalize_path(value: Any) -> str | None:
    if not isinstance(value, str) or not value:
        return None
    normalized = value.replace("\\", "/")
    while normalized.startswith("./"):
        normalized = normalized[2:]
    if normalized.startswith("knowledge/"):
        normalized = normalized[len("knowledge/") :]
    path = PurePosixPath(normalized)
    if path.is_absolute() or ".." in path.parts or not path.parts:
        return None
    return path.as_posix()


def _page(value: Any) -> int | None:
    if isinstance(value, int) and not isinstance(value, bool) and value > 0:
        return value
    if isinstance(value, str):
        match = re.fullmatch(r"(?:PDF-page-)?(\d+)", value)
        if match and int(match.group(1)) > 0:
            return int(match.group(1))
    return None


def _record_pages(record: dict[str, Any]) -> set[int]:
    locator = record.get("attributes", {}).get("evidence_locator")
    if not isinstance(locator, str):
        return set()
    return {
        page
        for fragment in locator.split(";")
        if (page := _page(fragment.rsplit("#", 1)[-1])) is not None
    }


def _records(bundle: Path) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    by_id = {}
    paper_records = {}
    for record in _load_jsonl(bundle / "semantic" / "records.jsonl"):
        record_id = record.get("record_id")
        if isinstance(record_id, str):
            by_id[record_id] = record
        paper = _paper_id(record.get("source_id")) or _paper_id(record_id)
        if paper and str(record.get("source_id", "")).startswith("paper-"):
            paper_records[paper] = record
    return by_id, paper_records


def _rows(path: Path) -> list[dict[str, Any]]:
    value = json.loads(path.read_text(encoding="utf-8"))
    rows = value.get("results", {}).get("results")
    if not isinstance(rows, list):
        raise ValueError(f"Missing Promptfoo results: {path}")
    return rows


def _safe_mean(values: list[float]) -> float:
    return mean(values) if values else 0.0


def _score_evidence_item(
    item: Any,
    bundle: Path,
    records: dict[str, dict[str, Any]],
    paper_records: dict[str, dict[str, Any]],
    cited_pages: dict[str, set[int]],
) -> tuple[bool, str | None, set[int]]:
    if not isinstance(item, dict):
        return False, None, set()
    claim_id = item.get("claim_id")
    record = records.get(claim_id) if isinstance(claim_id, str) else None
    if record is None or not str(record.get("source_id", "")).startswith("claims-"):
        return False, claim_id if isinstance(claim_id, str) else None, set()
    paper = _paper_id(record.get("source_id"))
    if paper is None or item.get("paper_id") != paper:
        return False, claim_id, set()
    concept_path = _normalize_path(item.get("concept_path"))
    expected_concept = _normalize_path(record.get("concept_path"))
    if concept_path != expected_concept or concept_path is None or not (bundle / Path(concept_path)).is_file():
        return False, claim_id, set()

    paper_record = paper_records.get(paper)
    source_path = _normalize_path(item.get("source_path"))
    allowed_sources = {
        _normalize_path(record.get("source_path")),
        _normalize_path(paper_record.get("source_path")) if paper_record else None,
        _normalize_path(paper_record.get("concept_path")) if paper_record else None,
    }
    if source_path is None or source_path not in allowed_sources:
        return False, claim_id, set()
    locators = item.get("locators")
    if not isinstance(locators, list) or not locators:
        return False, claim_id, set()
    pages = {_page(locator) for locator in locators}
    if None in pages or len(pages) != len(locators):
        return False, claim_id, set()
    normalized_pages = {int(page) for page in pages if page is not None}
    expected_pages = _record_pages(record)
    if not normalized_pages.issubset(expected_pages):
        return False, claim_id, normalized_pages
    if not normalized_pages.issubset(cited_pages.get(paper, set())):
        return False, claim_id, normalized_pages
    if record.get("attributes", {}).get("review_state") != "reviewed":
        return False, claim_id, normalized_pages
    return True, claim_id, normalized_pages


def _review_scores(review: dict[str, Any]) -> tuple[float, float, float]:
    fidelity = [float(item["score"]) for item in review["claim_fidelity"]]
    atomic = [float(value) for value in review["atomic_scores"].values()]
    negatives = [float(value) for value in review["negative_scores"].values()]
    return _safe_mean(fidelity), _safe_mean(atomic), _safe_mean(negatives)


def _score_answer(
    method: str,
    row: dict[str, Any],
    ground_truth: dict[str, dict[str, Any]],
    bundle: Path,
    records: dict[str, dict[str, Any]],
    paper_records: dict[str, dict[str, Any]],
    reviews: dict[str, dict[str, Any]],
    result_path: Path,
) -> dict[str, Any]:
    output_text = row.get("response", {}).get("output")
    if not isinstance(output_text, str):
        raise ValueError("Promptfoo answer has no output")
    output_sha256 = _sha256(output_text.encode("utf-8"))
    try:
        output = json.loads(output_text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Promptfoo output is not JSON: {exc}") from exc
    question_id = output.get("question_id")
    if question_id not in ground_truth:
        raise ValueError(f"Unexpected answer question id: {question_id}")
    provider = row.get("provider", {})
    profile = provider.get("id") if isinstance(provider, dict) else provider
    if not isinstance(profile, str):
        raise ValueError("Promptfoo answer has no profile id")
    answer_id = _sha256(f"{method}\0{profile}\0{question_id}\0{output_sha256}".encode())[:24]
    review = reviews.get(answer_id)
    if review is None:
        raise ValueError(f"Missing blinded review for {answer_id}")
    claim_correctness, semantic_completeness, negative_coverage = _review_scores(review)

    named_scores = row.get("namedScores", {})
    response_contract = float(named_scores.get("response-contract", 0))
    full_strict_score = float(row.get("score", 0))
    answer = output.get("answer") if isinstance(output, dict) else None
    if not isinstance(answer, dict):
        return {
            "answer_id": answer_id,
            "method": method,
            "profile": profile,
            "question_id": question_id,
            "output_sha256": output_sha256,
            "result_path": result_path.as_posix(),
            "strict_skill_arena_score": full_strict_score,
            "metrics": {name: 0.0 for name in METRICS},
            "counts": {},
            "review_note": review["note"],
        }

    citations = answer.get("citations", []) if isinstance(answer.get("citations"), list) else []
    cited_pages: dict[str, set[int]] = defaultdict(set)
    for citation in citations:
        if not isinstance(citation, dict) or not isinstance(citation.get("paper_id"), str):
            continue
        for value in citation.get("pages", []):
            if (page := _page(value)) is not None:
                cited_pages[citation["paper_id"]].add(page)

    evidence = output.get("evidence", []) if isinstance(output.get("evidence"), list) else []
    valid_items = 0
    evidence_claim_ids = set()
    evidence_papers = set()
    for item in evidence:
        valid, claim_id, _ = _score_evidence_item(item, bundle, records, paper_records, cited_pages)
        valid_items += int(valid)
        if valid and claim_id:
            evidence_claim_ids.add(claim_id)
            paper = _paper_id(records[claim_id].get("source_id"))
            if paper:
                evidence_papers.add(paper)
    evidence_validity = valid_items / len(evidence) if evidence else 0.0

    claims = answer.get("claims", []) if isinstance(answer.get("claims"), list) else []
    support_ids = [
        claim_id
        for claim in claims
        if isinstance(claim, dict)
        for claim_id in claim.get("supporting_claim_ids", [])
        if isinstance(claim_id, str)
    ]
    valid_support_ids = {claim_id for claim_id in support_ids if claim_id in records}
    grounding = (
        sum(claim_id in evidence_claim_ids for claim_id in support_ids) / len(support_ids)
        if support_ids
        else 0.0
    )

    truth = ground_truth[question_id]["ground_truth"]
    atomic_scores = []
    for atomic in truth["answer_claims"]:
        options = set(atomic["evidence_claim_ids"])
        atomic_scores.append(float(bool(options & valid_support_ids & evidence_claim_ids)))
    exact_atomic = _safe_mean(atomic_scores)
    paper_ids = set(answer.get("paper_ids", [])) if isinstance(answer.get("paper_ids"), list) else set()
    required_papers = set(truth["required_paper_ids"])
    paper_coverage = len(required_papers & paper_ids & set(cited_pages)) / len(required_papers)
    observed_sources = {
        str(records[claim_id]["source_id"])
        for claim_id in evidence_claim_ids
        if claim_id in records
    }
    observed_sources.update(
        f"paper-{paper.replace('.', '-', 1)}" for paper in paper_ids & set(cited_pages)
    )
    required_sources = set(truth["required_source_ids"])
    source_coverage = len(required_sources & observed_sources) / len(required_sources)

    return {
        "answer_id": answer_id,
        "method": method,
        "profile": profile,
        "question_id": question_id,
        "output_sha256": output_sha256,
        "result_path": result_path.as_posix(),
        "strict_skill_arena_score": round(full_strict_score, 8),
        "metrics": {
            "response_contract": round(response_contract, 8),
            "evidence_validity": round(evidence_validity, 8),
            "grounding": round(grounding, 8),
            "claim_correctness": round(claim_correctness, 8),
            "semantic_completeness": round(semantic_completeness, 8),
            "exact_atomic_evidence_coverage": round(exact_atomic, 8),
            "required_paper_coverage": round(paper_coverage, 8),
            "required_source_coverage": round(source_coverage, 8),
            "important_negative_coverage": round(negative_coverage, 8),
        },
        "counts": {
            "answer_claims": len(claims),
            "supporting_claim_references": len(support_ids),
            "valid_supporting_claim_identities": len(valid_support_ids),
            "evidence_items": len(evidence),
            "valid_evidence_items": valid_items,
            "required_atomic_claims": len(truth["answer_claims"]),
            "required_papers": len(required_papers),
            "required_sources": len(required_sources),
        },
        "review_note": review["note"],
    }


def _aggregate(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "answer_count": len(rows),
        "metrics": {
            metric: round(_safe_mean([row["metrics"][metric] for row in rows]), 8)
            for metric in METRICS
        },
        "strict_full_pass_rate": round(
            _safe_mean([float(row["strict_skill_arena_score"] == 1.0) for row in rows]), 8
        ),
        "output_hashes": sorted(row["output_sha256"] for row in rows),
    }


def _markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# Grounded Answer Comparison on the Ten Hard Questions",
        "",
        "All values are means across ten actual answers. Semantic correctness, completeness, and important-negative coverage come from a blinded fixed-rubric review; evidence validity and grounding are independently recomputed against the authoritative ledger and concept files. The strict Skill Arena full-pass rate is reported separately because one failed sub-contract fails a whole cell.",
        "",
        "| Method / profile | Strict all-contract | Contract | Evidence validity | Grounding | Correctness | Completeness | Exact atomic IDs | Papers | Sources | Negatives |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for method in ("legacy", "embedding", "classical"):
        profiles = summary["aggregates"][method]
        for profile in sorted(profiles, key=lambda value: ("control" not in value, value)):
            metrics = profiles[profile]["metrics"]
            lines.append(
                f"| `{method}` / `{profile}` | {profiles[profile]['strict_full_pass_rate']:.1%} | "
                f"{metrics['response_contract']:.1%} | {metrics['evidence_validity']:.1%} | "
                f"{metrics['grounding']:.1%} | {metrics['claim_correctness']:.1%} | {metrics['semantic_completeness']:.1%} | "
                f"{metrics['exact_atomic_evidence_coverage']:.1%} | {metrics['required_paper_coverage']:.1%} | "
                f"{metrics['required_source_coverage']:.1%} | {metrics['important_negative_coverage']:.1%} |"
            )
    lines.extend(["", "## Paired treatment deltas", "", "Positive values favor the single-skill treatment over its same-bundle knowledge-only control.", ""])
    lines.append("| Method | Correctness | Completeness | Evidence validity | Grounding | Papers | Negatives |")
    lines.append("| --- | ---: | ---: | ---: | ---: | ---: | ---: |")
    for method in ("legacy", "embedding", "classical"):
        delta = summary["paired_deltas"][method]
        lines.append(
            f"| `{method}` | {delta['claim_correctness']:+.1%} | {delta['semantic_completeness']:+.1%} | "
            f"{delta['evidence_validity']:+.1%} | {delta['grounding']:+.1%} | "
            f"{delta['required_paper_coverage']:+.1%} | {delta['important_negative_coverage']:+.1%} |"
        )
    lines.extend(
        [
            "",
            "## Reading the metrics",
            "",
            "- **Correctness** asks whether each stated candidate claim is faithful to its cited reviewed claim records.",
            "- **Completeness** asks whether the answer conveys every atomic ground-truth claim, allowing reviewed paraphrases and equivalent supporting records.",
            "- **Exact atomic IDs** is deliberately stricter: it requires the particular reviewed claim identities chosen during evidence-first question construction.",
            "- **Grounding** requires every cited supporting claim ID to appear in the answer's evidence list.",
            "- **Evidence validity** accepts normalized `knowledge/` prefixes and integer page locators, but still requires an exact ledger/concept/paper/page binding.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ground-truth", type=Path, required=True)
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--result", action="append", required=True)
    parser.add_argument("--reviews", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-markdown", type=Path, required=True)
    args = parser.parse_args()

    ground_truth = {item["id"]: item for item in _load_jsonl(args.ground_truth)}
    if len(ground_truth) != 10:
        raise ValueError("Expected ten hard ground-truth rows")
    records, paper_records = _records(args.bundle)
    review_report = json.loads(args.reviews.read_text(encoding="utf-8"))
    if review_report.get("schema_version") != "semantic-okf-grounded-answer-review/1.0":
        raise ValueError("Unexpected review schema")
    reviews = {item["answer_id"]: item for item in review_report.get("reviews", [])}

    scored = []
    input_reports = []
    for item in args.result:
        method, separator, raw_path = item.partition("=")
        if not separator:
            raise ValueError("Each --result must be METHOD=PATH")
        path = Path(raw_path)
        rows = _rows(path)
        if len(rows) != 20:
            raise ValueError(f"Expected 20 answers for {method}, found {len(rows)}")
        input_reports.append({"method": method, "path": path.as_posix(), "sha256": _sha256(path.read_bytes())})
        scored.extend(
            _score_answer(method, row, ground_truth, args.bundle, records, paper_records, reviews, path)
            for row in rows
        )
    if len(scored) != 60 or len({row["answer_id"] for row in scored}) != 60:
        raise ValueError("Expected 60 unique grounded answers")

    grouped: dict[str, dict[str, list[dict[str, Any]]]] = defaultdict(lambda: defaultdict(list))
    for row in scored:
        grouped[row["method"]][row["profile"]].append(row)
    aggregates = {
        method: {profile: _aggregate(rows) for profile, rows in profiles.items()}
        for method, profiles in grouped.items()
    }
    paired_deltas = {}
    for method, profiles in aggregates.items():
        control_id = next(profile for profile in profiles if profile == "knowledge-only-control")
        treatment_id = next(profile for profile in profiles if profile != control_id)
        paired_deltas[method] = {
            metric: round(
                profiles[treatment_id]["metrics"][metric] - profiles[control_id]["metrics"][metric], 8
            )
            for metric in METRICS
        }

    summary = {
        "schema_version": SCHEMA_VERSION,
        "question_count": 10,
        "answer_count": 60,
        "method_count": 3,
        "profiles_per_method": 2,
        "review": {
            "model": review_report.get("model"),
            "blinded": review_report.get("blinded"),
            "review_count": review_report.get("review_count"),
            "sha256": _sha256(args.reviews.read_bytes()),
        },
        "inputs": input_reports,
        "metric_contract": {
            "response_contract": "Skill Arena strict response-contract assertion",
            "evidence_validity": "independent exact ledger/concept/source/paper/page validation",
            "grounding": "supporting claim IDs represented by independently valid evidence items",
            "claim_correctness": "blinded reviewer fidelity of candidate claims to cited reviewed records",
            "semantic_completeness": "blinded reviewer coverage of atomic ground-truth claims",
            "exact_atomic_evidence_coverage": "exact curated evidence-claim identity coverage",
            "required_paper_coverage": "required paper IDs present in answer and citations",
            "required_source_coverage": "required claim and paper source IDs represented",
            "important_negative_coverage": "blinded reviewer coverage of important failure conditions",
        },
        "aggregates": aggregates,
        "paired_deltas": paired_deltas,
        "answers": sorted(scored, key=lambda row: (row["method"], row["profile"], row["question_id"])),
    }
    args.output_json.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    args.output_markdown.write_text(_markdown(summary), encoding="utf-8", newline="\n")
    print(json.dumps({"status": "pass", "answers": 60, "reviews": len(reviews)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
