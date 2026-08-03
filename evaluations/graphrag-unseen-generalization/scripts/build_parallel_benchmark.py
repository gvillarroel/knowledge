#!/usr/bin/env python3
"""Build a large evaluation-only extension from reviewed GraphRAG claims."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
from typing import Any, Mapping, Sequence


SCHEMA_VERSION = "graphrag-evaluation-only-question-extension/1.0"
POLICY_SCHEMA_VERSION = "evaluation-only-dataset-policy/1.0"
DATASET_ID = "graphrag-papers-parallel-eval-60-v1"
QUESTION_COUNT = 60
REPO_ROOT = Path(__file__).resolve().parents[3]
ANALYSIS_ROOT = REPO_ROOT / "evaluations" / "graphrag-cross-paper" / "analysis"
MARKDOWN_ROOT = (
    REPO_ROOT / "evaluations" / "graphrag-cross-paper" / "sources" / "markdown"
)
CANONICAL_QUESTIONS = (
    REPO_ROOT / "evaluations" / "semantic-okf-adaptive" / "retrieval-questions.jsonl"
)
GROUP_FILES = ("group-a.json", "group-b.json", "group-c.json")
TOKEN_RE = re.compile(r"[a-z0-9]+(?:[._/-][a-z0-9]+)*", re.IGNORECASE)
PAGE_CITATION_RE = re.compile(
    r"\s*[\[(]PDF\s+pp?\.[^\])]*[\])]\.?",
    re.IGNORECASE,
)
OUTPUT_FILES = (
    "retrieval-questions.jsonl",
    "ground-truth.jsonl",
    "harbor-questions.jsonl",
    "manifest.json",
    "EVALUATION_ONLY.json",
)


class ParallelBenchmarkError(ValueError):
    """Describe invalid or drifting evaluation-only benchmark input."""


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
        for offset in range(len(tokens) - size + 1)
    }


def _jaccard(left: set[Any], right: set[Any]) -> float:
    union = left | right
    return len(left & right) / len(union) if union else 0.0


def _load_object(path: Path, *, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ParallelBenchmarkError(f"Cannot read {label} at {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ParallelBenchmarkError(f"{label} must be a JSON object")
    return value


def _load_jsonl(path: Path, *, label: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        raise ParallelBenchmarkError(f"Cannot read {label} at {path}: {exc}") from exc
    for number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ParallelBenchmarkError(
                f"Invalid {label} JSON on line {number}: {exc}"
            ) from exc
        if not isinstance(value, dict):
            raise ParallelBenchmarkError(f"{label} line {number} is not an object")
        rows.append(value)
    if not rows:
        raise ParallelBenchmarkError(f"{label} must not be empty")
    return rows


def _load_papers() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    papers: dict[str, dict[str, Any]] = {}
    inputs = []
    for name in GROUP_FILES:
        path = ANALYSIS_ROOT / name
        payload = _load_object(path, label=name)
        rows = payload.get("papers")
        if not isinstance(rows, list):
            raise ParallelBenchmarkError(f"{name} has no papers array")
        for row in rows:
            if not isinstance(row, dict):
                raise ParallelBenchmarkError(f"{name} contains a non-object paper")
            paper_id = row.get("paper_id")
            claims = row.get("claims")
            if (
                not isinstance(paper_id, str)
                or not paper_id
                or paper_id in papers
                or not isinstance(claims, list)
                or len(claims) < 10
            ):
                raise ParallelBenchmarkError(f"{name} contains an invalid paper")
            papers[paper_id] = row
        inputs.append(
            {
                "path": path.relative_to(REPO_ROOT).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": _sha256_file(path),
            }
        )
    if len(papers) != 15:
        raise ParallelBenchmarkError(f"Expected 15 papers, found {len(papers)}")
    return [papers[key] for key in sorted(papers)], inputs


def _scenario(paper: Mapping[str, Any]) -> str:
    value = str(paper.get("problem_statement", "")).strip()
    if not value:
        raise ParallelBenchmarkError(f"{paper.get('paper_id')} has no problem statement")
    value = PAGE_CITATION_RE.sub("", value).strip()
    for explicit in (paper.get("method_name"), paper.get("title")):
        if isinstance(explicit, str) and explicit:
            value = re.sub(
                re.escape(explicit),
                "the proposed approach",
                value,
                flags=re.IGNORECASE,
            )
    value = re.sub(r"\s+", " ", value).strip()
    return value if value.endswith((".", "?", "!")) else value + "."


def _select_claims(
    paper: Mapping[str, Any],
    preference_groups: Sequence[Sequence[str]],
) -> list[int]:
    claims = paper["claims"]
    used: set[int] = set()
    selected: list[int] = []
    for preferences in preference_groups:
        match = next(
            (
                index
                for kind in preferences
                for index, claim in enumerate(claims)
                if index not in used and claim.get("kind") == kind
            ),
            None,
        )
        if match is None:
            match = next(
                (index for index in range(len(claims)) if index not in used),
                None,
            )
        if match is None:
            raise ParallelBenchmarkError(
                f"{paper.get('paper_id')} lacks enough independent claims"
            )
        used.add(match)
        selected.append(match)
    return selected


PIPELINE_CLAIMS = (
    ("graph-construction", "graph-representation", "methodology"),
    ("retrieval-strategy", "retrieval-unit", "organization-synthesis"),
    ("organization-synthesis", "methodology", "graph-representation"),
    ("efficiency-update", "comparison", "evaluation"),
    ("limitation",),
)
EVIDENCE_CLAIMS = (
    ("task", "methodology", "graph-construction"),
    ("evaluation", "strength", "comparison"),
    ("strength", "evaluation", "comparison"),
    ("safety-grounding", "comparison", "retrieval-strategy"),
    ("limitation",),
)
COMPARISON_CLAIMS = (
    ("graph-construction", "graph-representation", "methodology"),
    ("retrieval-strategy", "retrieval-unit", "organization-synthesis"),
    ("efficiency-update", "evaluation", "strength"),
    ("limitation",),
)


def _question_specs(papers: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    specs: list[dict[str, Any]] = []
    number = 201
    for index, paper in enumerate(papers, start=1):
        scenario = _scenario(paper)
        specs.append(
            {
                "id": f"q{number:03d}-pipeline-audit-{index:02d}",
                "difficulty": "hard-single-paper",
                "question": (
                    f"A research team faces this scenario: {scenario} "
                    "Reconstruct the proposed solution across five linked decisions: "
                    "graph or knowledge construction, retrieval unit and ranking "
                    "behavior, organization or synthesis, the efficiency or update "
                    "trade-off, and the limitation that blocks a stronger "
                    "generalization claim. Separate measured behavior from proposals "
                    "and identify the method."
                ),
                "papers": [(paper, _select_claims(paper, PIPELINE_CLAIMS))],
            }
        )
        number += 1
    for index, paper in enumerate(papers, start=1):
        scenario = _scenario(paper)
        specs.append(
            {
                "id": f"q{number:03d}-evidence-boundary-{index:02d}",
                "difficulty": "hard-single-paper",
                "question": (
                    f"An audit must decide whether research for this scenario supports "
                    f"deployment: {scenario} Identify the method, state its intended "
                    "task, explain the evaluation design and strongest reported "
                    "outcome, and reconcile that outcome with an important negative "
                    "or safety boundary and one limitation. State both the conclusion "
                    "that is supported and the broader conclusion that is not."
                ),
                "papers": [(paper, _select_claims(paper, EVIDENCE_CLAIMS))],
            }
        )
        number += 1

    pair_indices = [
        *((index, (index + 5) % 15) for index in range(15)),
        *((index, (index + 7) % 15) for index in range(5)),
    ]
    for index, (left_index, right_index) in enumerate(pair_indices, start=1):
        left = papers[left_index]
        right = papers[right_index]
        specs.append(
            {
                "id": f"q{number:03d}-paired-boundary-{index:02d}",
                "difficulty": "hard-two-paper-comparison",
                "question": (
                    "Compare two papers motivated by these distinct scenarios. "
                    f"Scenario A: {_scenario(left)} Scenario B: {_scenario(right)} "
                    "For each paper, identify the method, graph construction or "
                    "representation, retrieval or synthesis mechanism, efficiency or "
                    "evaluation boundary, and one limitation. Finish by explaining "
                    "why a reported strength from either paper cannot be transferred "
                    "to the other without new evidence."
                ),
                "papers": [
                    (left, _select_claims(left, COMPARISON_CLAIMS)),
                    (right, _select_claims(right, COMPARISON_CLAIMS)),
                ],
            }
        )
        number += 1

    triple_indices = [
        *((index, index + 5, index + 10) for index in range(5)),
        *((index, (index + 3) % 15, (index + 8) % 15) for index in range(5)),
    ]
    for index, indices in enumerate(triple_indices, start=1):
        selected = [papers[value] for value in indices]
        scenarios = " ".join(
            f"Scenario {label}: {_scenario(paper)}"
            for label, paper in zip(("A", "B", "C"), selected, strict=True)
        )
        specs.append(
            {
                "id": f"q{number:03d}-three-way-decision-{index:02d}",
                "difficulty": "very-hard-three-paper-synthesis",
                "question": (
                    f"A system architect is choosing among three research directions. "
                    f"{scenarios} Build an evidence-bounded decision matrix: identify "
                    "each method, trace construction or representation into retrieval "
                    "and synthesis, state the relevant measured strength or efficiency "
                    "boundary, and give one limitation. Make a conditional "
                    "recommendation without treating an unmeasured capability in one "
                    "paper as a result established by another."
                ),
                "papers": [
                    (paper, _select_claims(paper, COMPARISON_CLAIMS))
                    for paper in selected
                ],
            }
        )
        number += 1
    if len(specs) != QUESTION_COUNT or number != 261:
        raise ParallelBenchmarkError("Internal question plan is incomplete")
    return specs


def _validate_pages(paper_id: str, pages: Sequence[int]) -> str:
    path = MARKDOWN_ROOT / f"{paper_id}.md"
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise ParallelBenchmarkError(f"Cannot read paper Markdown {path}: {exc}") from exc
    for page in pages:
        if f"## PDF page {page}" not in text:
            raise ParallelBenchmarkError(f"{paper_id} lacks PDF page {page}")
    return path.relative_to(REPO_ROOT).as_posix()


def _source_ids(paper_ids: Sequence[str]) -> list[str]:
    values = []
    for paper_id in paper_ids:
        slug = paper_id.replace(".", "-")
        values.extend((f"claims-{slug}", f"paper-{slug}"))
    return sorted(values)


def _materialize(
    specs: Sequence[Mapping[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    retrieval_rows = []
    truth_rows = []
    difficulty_rows = []
    for spec in specs:
        evidence = []
        answer_sections = []
        paper_ids = []
        for paper, claim_indices in spec["papers"]:
            paper_id = paper["paper_id"]
            paper_ids.append(paper_id)
            statements = []
            for claim_index in claim_indices:
                claim = paper["claims"][claim_index]
                pages = claim.get("evidence_pages")
                if (
                    not isinstance(pages, list)
                    or not pages
                    or any(
                        isinstance(page, bool) or not isinstance(page, int) or page < 1
                        for page in pages
                    )
                ):
                    raise ParallelBenchmarkError(
                        f"{spec['id']} references invalid evidence pages"
                    )
                statement = claim.get("statement")
                kind = claim.get("kind")
                if not isinstance(statement, str) or not isinstance(kind, str):
                    raise ParallelBenchmarkError(
                        f"{spec['id']} references an incomplete claim"
                    )
                statements.append(statement)
                evidence.append(
                    {
                        "paper_id": paper_id,
                        "paper_title": paper["title"],
                        "method_name": paper["method_name"],
                        "claim_index": claim_index,
                        "claim_kind": kind,
                        "statement": statement,
                        "evidence_pages": pages,
                        "source_markdown": _validate_pages(paper_id, pages),
                    }
                )
            answer_sections.append(
                f"{paper['method_name']} ({paper_id}): " + " ".join(statements)
            )
        paper_ids = sorted(set(paper_ids))
        question = str(spec["question"])
        if len(_tokens(question)) < 55:
            raise ParallelBenchmarkError(f"{spec['id']} is not sufficiently complex")
        retrieval_rows.append(
            {
                "id": spec["id"],
                "question": question,
                "qrels": {
                    "paper_ids": paper_ids,
                    "source_ids": _source_ids(paper_ids),
                },
            }
        )
        truth_rows.append(
            {
                "id": spec["id"],
                "question": question,
                "expected_answer": "\n\n".join(answer_sections),
                "paper_ids": paper_ids,
                "difficulty": spec["difficulty"],
                "evidence": evidence,
                "review": {
                    "status": "source-derived-reviewed-claim-binding",
                    "independent_human_adjudication": False,
                    "answer_scope": "all selected claims must remain attributable",
                },
            }
        )
        difficulty_rows.append(
            {
                "id": spec["id"],
                "difficulty": spec["difficulty"],
                "paper_count": len(paper_ids),
                "claim_anchor_count": len(evidence),
                "question_token_count": len(_tokens(question)),
            }
        )
    return retrieval_rows, truth_rows, difficulty_rows


def build(parent_questions: Path) -> dict[str, str]:
    """Build all evaluation-only artifacts in memory."""

    parent_rows = _load_jsonl(parent_questions, label="parent unseen questions")
    if len(parent_rows) != 20:
        raise ParallelBenchmarkError(
            f"Parent extension must contain 20 questions, found {len(parent_rows)}"
        )
    canonical_rows = _load_jsonl(
        CANONICAL_QUESTIONS,
        label="canonical GraphRAG questions",
    )
    papers, claim_inputs = _load_papers()
    specs = _question_specs(papers)
    retrieval, truth, difficulty = _materialize(specs)

    historical = canonical_rows + parent_rows
    historical_texts = [str(row.get("question", "")) for row in historical]
    novelty = []
    seen_questions: set[str] = set()
    for row in retrieval:
        normalized = " ".join(_tokens(row["question"]))
        if normalized in seen_questions:
            raise ParallelBenchmarkError(f"Duplicate generated question: {row['id']}")
        seen_questions.add(normalized)
        token_set = set(_tokens(row["question"]))
        five_grams = _ngrams(row["question"], 5)
        novelty.append(
            {
                "id": row["id"],
                "max_historical_token_jaccard": max(
                    _jaccard(token_set, set(_tokens(text)))
                    for text in historical_texts
                ),
                "max_historical_5gram_jaccard": max(
                    _jaccard(five_grams, _ngrams(text, 5))
                    for text in historical_texts
                ),
            }
        )
    max_five_gram = max(row["max_historical_5gram_jaccard"] for row in novelty)
    if max_five_gram >= 0.35:
        raise ParallelBenchmarkError(
            f"Generated question is too close to prior evidence: {max_five_gram}"
        )

    retrieval_text = "\n".join(_json_line(row) for row in retrieval) + "\n"
    truth_text = "\n".join(_json_line(row) for row in truth) + "\n"
    harbor_text = _json_line(canonical_rows[0]) + "\n" + retrieval_text
    retrieval_sha = _sha256_bytes(retrieval_text.encode("utf-8"))
    truth_sha = _sha256_bytes(truth_text.encode("utf-8"))
    policy = {
        "schema_version": POLICY_SCHEMA_VERSION,
        "dataset_id": DATASET_ID,
        "classification": "evaluation-only",
        "allowed_uses": [
            "sealed final evaluation",
            "aggregate comparison reporting",
        ],
        "forbidden_uses": [
            "knowledge construction",
            "retrieval-profile construction",
            "skill or query-adapter evolution",
            "trace distillation",
            "candidate realization or selection",
            "discovery, development, or validation fitness",
        ],
        "questions_sha256": retrieval_sha,
        "ground_truth_sha256": truth_sha,
        "copying_or_reformatting_does_not_change_policy": True,
    }
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "dataset_id": DATASET_ID,
        "classification": "evaluation-only",
        "parent_extension": {
            "dataset_id": "graphrag-post-v51-unseen-20-v1",
            "path": str(parent_questions.resolve()),
            "bytes": parent_questions.stat().st_size,
            "sha256": _sha256_file(parent_questions),
        },
        "canonical_questions": {
            "path": CANONICAL_QUESTIONS.relative_to(REPO_ROOT).as_posix(),
            "bytes": CANONICAL_QUESTIONS.stat().st_size,
            "sha256": _sha256_file(CANONICAL_QUESTIONS),
        },
        "claim_inputs": claim_inputs,
        "policy": policy,
        "summary": {
            "question_count": len(retrieval),
            "hard_single_paper_questions": sum(
                row["paper_count"] == 1 for row in difficulty
            ),
            "hard_two_paper_questions": sum(
                row["paper_count"] == 2 for row in difficulty
            ),
            "very_hard_three_paper_questions": sum(
                row["paper_count"] == 3 for row in difficulty
            ),
            "paper_coverage": len(
                {
                    paper_id
                    for row in retrieval
                    for paper_id in row["qrels"]["paper_ids"]
                }
            ),
            "minimum_claim_anchors": min(
                row["claim_anchor_count"] for row in difficulty
            ),
            "mean_claim_anchors": sum(
                row["claim_anchor_count"] for row in difficulty
            )
            / len(difficulty),
            "minimum_question_tokens": min(
                row["question_token_count"] for row in difficulty
            ),
            "mean_question_tokens": sum(
                row["question_token_count"] for row in difficulty
            )
            / len(difficulty),
            "max_historical_token_jaccard": max(
                row["max_historical_token_jaccard"] for row in novelty
            ),
            "max_historical_5gram_jaccard": max_five_gram,
        },
        "difficulty": difficulty,
        "novelty": novelty,
        "artifacts": {
            "retrieval-questions.jsonl": {
                "bytes": len(retrieval_text.encode("utf-8")),
                "sha256": retrieval_sha,
            },
            "ground-truth.jsonl": {
                "bytes": len(truth_text.encode("utf-8")),
                "sha256": truth_sha,
            },
            "harbor-questions.jsonl": {
                "bytes": len(harbor_text.encode("utf-8")),
                "sha256": _sha256_bytes(harbor_text.encode("utf-8")),
                "note": "One calibration question followed by sixty evaluation-only questions",
            },
        },
        "review_boundary": {
            "authority": "previously reviewed claim ledger and pinned PDF pages",
            "independent_human_adjudication": False,
            "retrieval_metrics_are_not_semantic_answer_correctness": True,
        },
    }
    return {
        "retrieval-questions.jsonl": retrieval_text,
        "ground-truth.jsonl": truth_text,
        "harbor-questions.jsonl": harbor_text,
        "manifest.json": _canonical_json(manifest),
        "EVALUATION_ONLY.json": _canonical_json(policy),
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
                raise ParallelBenchmarkError(f"Generated benchmark drifted: {path}")
        return
    output_dir.mkdir(parents=True, exist_ok=True)
    for name in OUTPUT_FILES:
        path = output_dir / name
        if path.exists():
            raise ParallelBenchmarkError(f"Refusing to replace artifact: {path}")
        path.write_text(artifacts[name], encoding="utf-8", newline="\n")


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--parent-questions", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Build or verify the evaluation-only benchmark."""

    args = build_parser().parse_args(argv)
    try:
        artifacts = build(args.parent_questions.resolve())
        _write_or_check(artifacts, args.output_dir.resolve(), check=args.check)
    except (ParallelBenchmarkError, OSError, UnicodeError) as exc:
        print(_canonical_json({"status": "error", "error": str(exc)}), end="")
        return 2
    print(
        _canonical_json(
            {
                "status": "pass" if args.check else "created",
                "dataset_id": DATASET_ID,
                "question_count": QUESTION_COUNT,
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
