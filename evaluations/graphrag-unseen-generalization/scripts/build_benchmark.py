#!/usr/bin/env python3
"""Build an evidence-bound unseen-question GraphRAG retrieval benchmark."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
from typing import Any, Mapping, Sequence


SCHEMA_VERSION = "graphrag-unseen-question-benchmark/1.0"
TOKEN_RE = re.compile(r"[a-z0-9]+(?:[._/-][a-z0-9]+)*", re.IGNORECASE)
QUESTION_ID_RE = re.compile(r"^q1[0-9]{2}-[a-z0-9-]+$")
REPO_ROOT = Path(__file__).resolve().parents[3]
ANALYSIS_ROOT = REPO_ROOT / "evaluations" / "graphrag-cross-paper" / "analysis"
MARKDOWN_ROOT = (
    REPO_ROOT / "evaluations" / "graphrag-cross-paper" / "sources" / "markdown"
)
OLD_QUESTIONS = (
    REPO_ROOT / "evaluations" / "semantic-okf-adaptive" / "retrieval-questions.jsonl"
)
GROUP_FILES = ("group-a.json", "group-b.json", "group-c.json")
OUTPUT_FILES = (
    "retrieval-questions.jsonl",
    "ground-truth.jsonl",
    "harbor-questions.jsonl",
    "manifest.json",
)


class BenchmarkError(ValueError):
    """Describe invalid or non-reproducible benchmark input."""


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
        allow_nan=False,
    ) + "\n"


def _json_line(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _load_object(path: Path, *, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise BenchmarkError(f"Cannot read {label} at {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise BenchmarkError(f"{label} must be a JSON object")
    return value


def _load_jsonl(path: Path, *, label: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        raise BenchmarkError(f"Cannot read {label} at {path}: {exc}") from exc
    for number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise BenchmarkError(
                f"Invalid {label} JSON on line {number}: {exc}"
            ) from exc
        if not isinstance(value, dict):
            raise BenchmarkError(f"{label} line {number} is not an object")
        rows.append(value)
    return rows


def _tokens(text: str) -> tuple[str, ...]:
    return tuple(
        token.strip("._/-")
        for token in TOKEN_RE.findall(text.casefold())
        if token.strip("._/-")
    )


def _ngrams(text: str, size: int) -> set[tuple[str, ...]]:
    tokens = _tokens(text)
    return {
        tokens[offset : offset + size]
        for offset in range(0, len(tokens) - size + 1)
    }


def _jaccard(left: set[Any], right: set[Any]) -> float:
    union = left | right
    return len(left & right) / len(union) if union else 0.0


def _source_ids(paper_ids: Sequence[str]) -> list[str]:
    values = []
    for paper_id in paper_ids:
        slug = paper_id.replace(".", "-")
        values.extend((f"claims-{slug}", f"paper-{slug}"))
    return sorted(values)


def _load_reviewed_papers() -> tuple[dict[str, dict[str, Any]], list[dict[str, Any]]]:
    papers: dict[str, dict[str, Any]] = {}
    inputs = []
    for name in GROUP_FILES:
        path = ANALYSIS_ROOT / name
        payload = _load_object(path, label=name)
        rows = payload.get("papers")
        if not isinstance(rows, list):
            raise BenchmarkError(f"{name} has no papers array")
        for row in rows:
            if not isinstance(row, dict):
                raise BenchmarkError(f"{name} contains a non-object paper")
            paper_id = row.get("paper_id")
            claims = row.get("claims")
            if (
                not isinstance(paper_id, str)
                or not paper_id
                or paper_id in papers
                or not isinstance(claims, list)
                or not claims
            ):
                raise BenchmarkError(f"{name} has an invalid paper")
            papers[paper_id] = row
        inputs.append(
            {
                "path": path.relative_to(REPO_ROOT).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": _sha256_file(path),
            }
        )
    if len(papers) != 15:
        raise BenchmarkError(f"Expected 15 reviewed papers, found {len(papers)}")
    return papers, inputs


def _validate_evidence_page(paper_id: str, pages: Sequence[int]) -> str:
    path = MARKDOWN_ROOT / f"{paper_id}.md"
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise BenchmarkError(f"Cannot read paper Markdown {path}: {exc}") from exc
    for page in pages:
        if f"## PDF page {page}" not in text:
            raise BenchmarkError(f"{paper_id} lacks reviewed PDF page {page}")
    return path.relative_to(REPO_ROOT).as_posix()


def _build_rows(
    blueprint: Mapping[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    if blueprint.get("schema_version") != SCHEMA_VERSION:
        raise BenchmarkError("Blueprint schema version is unsupported")
    questions = blueprint.get("questions")
    if not isinstance(questions, list) or len(questions) != 20:
        raise BenchmarkError("Blueprint must contain exactly 20 questions")
    papers, claim_inputs = _load_reviewed_papers()
    old_rows = _load_jsonl(OLD_QUESTIONS, label="canonical GraphRAG questions")
    old_texts = [str(row.get("question", "")) for row in old_rows]
    old_normalized = {" ".join(_tokens(text)) for text in old_texts}

    retrieval_rows = []
    truth_rows = []
    novelty_rows = []
    seen_ids: set[str] = set()
    seen_questions: set[str] = set()
    covered_papers: set[str] = set()
    for position, row in enumerate(questions, start=1):
        if not isinstance(row, dict):
            raise BenchmarkError(f"Question {position} is not an object")
        identifier = row.get("id")
        question = row.get("question")
        answer = row.get("answer")
        evidence_specs = row.get("evidence")
        if (
            not isinstance(identifier, str)
            or QUESTION_ID_RE.fullmatch(identifier) is None
            or identifier in seen_ids
            or not isinstance(question, str)
            or len(_tokens(question)) < 8
            or not isinstance(answer, str)
            or len(_tokens(answer)) < 12
            or not isinstance(evidence_specs, list)
            or not evidence_specs
        ):
            raise BenchmarkError(f"Question {position} is incomplete or invalid")
        normalized = " ".join(_tokens(question))
        if normalized in old_normalized or normalized in seen_questions:
            raise BenchmarkError(f"Question {identifier} duplicates another question")
        seen_ids.add(identifier)
        seen_questions.add(normalized)

        evidence = []
        paper_ids = []
        for spec in evidence_specs:
            if not isinstance(spec, dict):
                raise BenchmarkError(f"{identifier} has invalid evidence")
            paper_id = spec.get("paper_id")
            claim_indices = spec.get("claim_indices")
            if (
                not isinstance(paper_id, str)
                or paper_id not in papers
                or not isinstance(claim_indices, list)
                or not claim_indices
                or any(
                    isinstance(index, bool) or not isinstance(index, int)
                    for index in claim_indices
                )
                or claim_indices != sorted(set(claim_indices))
            ):
                raise BenchmarkError(f"{identifier} has invalid claim references")
            paper = papers[paper_id]
            claims = paper["claims"]
            paper_ids.append(paper_id)
            covered_papers.add(paper_id)
            for claim_index in claim_indices:
                if not 0 <= claim_index < len(claims):
                    raise BenchmarkError(
                        f"{identifier} claim index {claim_index} is out of range"
                    )
                claim = claims[claim_index]
                if not isinstance(claim, dict):
                    raise BenchmarkError(f"{identifier} references an invalid claim")
                statement = claim.get("statement")
                kind = claim.get("kind")
                pages = claim.get("evidence_pages")
                if (
                    not isinstance(statement, str)
                    or not statement
                    or not isinstance(kind, str)
                    or not kind
                    or not isinstance(pages, list)
                    or not pages
                    or any(
                        isinstance(page, bool) or not isinstance(page, int) or page < 1
                        for page in pages
                    )
                ):
                    raise BenchmarkError(f"{identifier} references incomplete claim data")
                markdown_path = _validate_evidence_page(paper_id, pages)
                evidence.append(
                    {
                        "paper_id": paper_id,
                        "paper_title": paper["title"],
                        "method_name": paper["method_name"],
                        "claim_index": claim_index,
                        "claim_kind": kind,
                        "statement": statement,
                        "evidence_pages": pages,
                        "source_markdown": markdown_path,
                    }
                )
        paper_ids = sorted(set(paper_ids))
        retrieval_rows.append(
            {
                "id": identifier,
                "question": question,
                "qrels": {
                    "paper_ids": paper_ids,
                    "source_ids": _source_ids(paper_ids),
                },
            }
        )
        truth_rows.append(
            {
                "id": identifier,
                "question": question,
                "expected_answer": answer,
                "paper_ids": paper_ids,
                "evidence": evidence,
                "review": {
                    "status": "source-derived-reviewed-claim-binding",
                    "independent_human_adjudication": False,
                },
            }
        )

        token_set = set(_tokens(question))
        five_grams = _ngrams(question, 5)
        token_scores = [_jaccard(token_set, set(_tokens(text))) for text in old_texts]
        ngram_scores = [_jaccard(five_grams, _ngrams(text, 5)) for text in old_texts]
        novelty_rows.append(
            {
                "id": identifier,
                "max_old_token_jaccard": max(token_scores, default=0.0),
                "max_old_5gram_jaccard": max(ngram_scores, default=0.0),
            }
        )

    if covered_papers != set(papers):
        missing = sorted(set(papers) - covered_papers)
        raise BenchmarkError(f"Benchmark does not cover every paper: {missing}")
    if max(row["max_old_5gram_jaccard"] for row in novelty_rows) >= 0.5:
        raise BenchmarkError("A new question is too close to a canonical question")

    summary = {
        "question_count": len(retrieval_rows),
        "single_paper_questions": sum(
            len(row["qrels"]["paper_ids"]) == 1 for row in retrieval_rows
        ),
        "multi_paper_questions": sum(
            len(row["qrels"]["paper_ids"]) > 1 for row in retrieval_rows
        ),
        "paper_coverage": len(covered_papers),
        "max_old_token_jaccard": max(
            row["max_old_token_jaccard"] for row in novelty_rows
        ),
        "max_old_5gram_jaccard": max(
            row["max_old_5gram_jaccard"] for row in novelty_rows
        ),
    }
    metadata = {
        "claim_inputs": claim_inputs,
        "old_questions": {
            "path": OLD_QUESTIONS.relative_to(REPO_ROOT).as_posix(),
            "bytes": OLD_QUESTIONS.stat().st_size,
            "sha256": _sha256_file(OLD_QUESTIONS),
        },
        "novelty": novelty_rows,
        "summary": summary,
    }
    return retrieval_rows, truth_rows, metadata


def build(blueprint_path: Path) -> dict[str, str]:
    """Build all benchmark files in memory and return their exact text."""

    blueprint = _load_object(blueprint_path, label="benchmark blueprint")
    retrieval, truth, metadata = _build_rows(blueprint)
    retrieval_text = "\n".join(_json_line(row) for row in retrieval) + "\n"
    truth_text = "\n".join(_json_line(row) for row in truth) + "\n"
    old_rows = _load_jsonl(OLD_QUESTIONS, label="canonical GraphRAG questions")
    harbor_text = _json_line(old_rows[0]) + "\n" + retrieval_text
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "benchmark_id": blueprint.get("benchmark_id"),
        "candidate_boundary": {
            "candidate_state": "all candidates frozen before holdout release",
            "profile_update_allowed": False,
            "promotion_eligible": False,
        },
        "review_boundary": {
            "authority": "previously reviewed repository claim ledger and pinned PDF pages",
            "independent_human_adjudication": False,
            "answer_use": "correctness reference; retrieval metrics use paper qrels",
        },
        **metadata,
        "artifacts": {
            "retrieval-questions.jsonl": {
                "bytes": len(retrieval_text.encode("utf-8")),
                "sha256": _sha256_bytes(retrieval_text.encode("utf-8")),
            },
            "ground-truth.jsonl": {
                "bytes": len(truth_text.encode("utf-8")),
                "sha256": _sha256_bytes(truth_text.encode("utf-8")),
            },
            "harbor-questions.jsonl": {
                "bytes": len(harbor_text.encode("utf-8")),
                "sha256": _sha256_bytes(harbor_text.encode("utf-8")),
                "note": "One canonical calibration task followed by the twenty unseen holdout tasks",
            },
        },
        "blueprint": {
            "bytes": blueprint_path.stat().st_size,
            "sha256": _sha256_file(blueprint_path),
        },
    }
    return {
        "retrieval-questions.jsonl": retrieval_text,
        "ground-truth.jsonl": truth_text,
        "harbor-questions.jsonl": harbor_text,
        "manifest.json": _canonical_json(manifest),
    }


def _write_or_check(
    artifacts: Mapping[str, str],
    output_dir: Path,
    *,
    check: bool,
) -> None:
    if check:
        for name in OUTPUT_FILES:
            path = output_dir / name
            if not path.is_file() or path.read_text(encoding="utf-8") != artifacts[name]:
                raise BenchmarkError(f"Generated benchmark drifted: {path}")
        return
    output_dir.mkdir(parents=True, exist_ok=True)
    for name in OUTPUT_FILES:
        path = output_dir / name
        if path.exists():
            raise BenchmarkError(f"Refusing to replace benchmark artifact: {path}")
        path.write_text(artifacts[name], encoding="utf-8", newline="\n")


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--blueprint", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Build or check the benchmark."""

    args = build_parser().parse_args(argv)
    try:
        artifacts = build(args.blueprint.resolve())
        _write_or_check(artifacts, args.output_dir.resolve(), check=args.check)
    except (BenchmarkError, OSError, UnicodeError) as exc:
        print(_canonical_json({"status": "error", "error": str(exc)}), end="")
        return 2
    print(
        _canonical_json(
            {
                "status": "pass" if args.check else "created",
                "output_dir": str(args.output_dir.resolve()),
                "artifacts": {
                    name: _sha256_bytes(text.encode("utf-8"))
                    for name, text in artifacts.items()
                },
            }
        ),
        end="",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
