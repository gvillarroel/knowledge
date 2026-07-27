#!/usr/bin/env python3
"""Compile one bounded extractive answer from a Tika/MALLET Semantic OKF snapshot."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

from _tika_mallet_snapshot import SnapshotError, load_snapshot, search_snapshot


EVIDENCE_FIELDS = (
    "source_id",
    "record_id",
    "concept_path",
    "source_path",
    "record_sha256",
    "locator",
    "text_sha256",
)
TOKEN_RE = re.compile(r"[a-z0-9]+", re.ASCII | re.IGNORECASE)
SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")
SPACE_RE = re.compile(r"\s+")
CLAIM_CHAR_LIMIT = 420
SUMMARY_WORD_LIMIT = 440


def configure_utf8() -> None:
    """Make the closed JSON stream portable across host defaults."""

    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(encoding="utf-8")


def strict_positive_int(value: str) -> int:
    """Parse a positive command-line integer without accepting booleans."""

    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("value must be positive")
    return parsed


def build_parser() -> argparse.ArgumentParser:
    """Return the intentionally narrow command contract."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle", type=Path)
    parser.add_argument("--question-id", required=True)
    parser.add_argument("--question", required=True)
    parser.add_argument("--query", action="append", required=True)
    parser.add_argument(
        "--mode",
        choices=("bm25", "topic", "association", "fusion"),
        default="fusion",
    )
    parser.add_argument("--top-k", type=strict_positive_int, default=6)
    parser.add_argument("--minimum-sources", type=strict_positive_int, required=True)
    parser.add_argument("--max-sources", type=strict_positive_int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser


def canonical_json(value: object) -> str:
    """Serialize closed output without non-standard numeric values."""

    return json.dumps(
        value,
        ensure_ascii=False,
        indent=2,
        sort_keys=False,
        allow_nan=False,
    ) + "\n"


def evidence_identity(row: dict[str, Any]) -> dict[str, Any]:
    """Copy the exact closed evidence identity from one validated result."""

    evidence: dict[str, Any] = {}
    for field in EVIDENCE_FIELDS:
        value = row.get(field)
        if field == "locator":
            if not isinstance(value, dict) or not value:
                raise SnapshotError("retrieval result has invalid locator")
        elif not isinstance(value, str) or not value:
            raise SnapshotError(f"retrieval result has invalid {field}")
        evidence[field] = value
    return evidence


def serialized_evidence(row: dict[str, Any]) -> str:
    """Return a stable identity key for a validated result."""

    return json.dumps(
        evidence_identity(row),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def fuse_results(searches: list[dict[str, Any]], max_sources: int) -> list[dict[str, Any]]:
    """Fuse query rankings and retain one strongest passage per source."""

    candidates: dict[str, dict[str, Any]] = {}
    for query_index, search in enumerate(searches):
        query = search.get("query")
        rows = search.get("results")
        if not isinstance(query, str) or not isinstance(rows, list):
            raise SnapshotError("search output is malformed")
        for row in rows:
            if not isinstance(row, dict):
                raise SnapshotError("search result row is malformed")
            rank = row.get("rank")
            if isinstance(rank, bool) or not isinstance(rank, int) or rank < 1:
                raise SnapshotError("search result rank is invalid")
            key = serialized_evidence(row)
            candidate = candidates.setdefault(
                key,
                {
                    "row": row,
                    "queries": [],
                    "rrf": 0.0,
                    "best_rank": rank,
                    "best_query": query_index,
                },
            )
            matched = candidate["queries"]
            if query not in matched:
                matched.append(query)
                candidate["rrf"] += 1.0 / (60.0 + rank)
            if (rank, query_index, key) < (
                candidate["best_rank"],
                candidate["best_query"],
                key,
            ):
                candidate["row"] = row
                candidate["best_rank"] = rank
                candidate["best_query"] = query_index

    by_source: dict[str, list[tuple[str, dict[str, Any]]]] = {}
    for key, candidate in candidates.items():
        source_id = candidate["row"].get("source_id")
        if not isinstance(source_id, str) or not source_id:
            raise SnapshotError("search result source_id is invalid")
        by_source.setdefault(source_id, []).append((key, candidate))

    selected: list[tuple[str, dict[str, Any]]] = []
    for rows in by_source.values():
        selected.append(
            min(
                rows,
                key=lambda item: (
                    -len(item[1]["queries"]),
                    -item[1]["rrf"],
                    item[1]["best_rank"],
                    item[1]["best_query"],
                    item[0],
                ),
            )
        )
    selected.sort(
        key=lambda item: (
            -len(item[1]["queries"]),
            -item[1]["rrf"],
            item[1]["best_rank"],
            item[1]["best_query"],
            item[0],
        )
    )
    return [candidate for _key, candidate in selected[:max_sources]]


def query_tokens(queries: list[str]) -> set[str]:
    """Return informative ASCII tokens for deterministic sentence selection."""

    return {
        token.casefold()
        for query in queries
        for token in TOKEN_RE.findall(query)
        if len(token) >= 4
    }


def trim_words(text: str, char_limit: int) -> str:
    """Trim normalized prose at a word boundary."""

    if len(text) <= char_limit:
        return text
    prefix = text[: char_limit + 1]
    boundary = prefix.rfind(" ")
    if boundary >= char_limit // 2:
        prefix = prefix[:boundary]
    return prefix.rstrip(" ,;:-") + "."


def extract_claim(text: str, queries: list[str]) -> str:
    """Select a compact query-dense sentence span from one exact passage."""

    normalized = SPACE_RE.sub(" ", text).strip()
    if not normalized:
        raise SnapshotError("retrieval result text is empty")
    sentences = [item.strip() for item in SENTENCE_RE.split(normalized) if item.strip()]
    if not sentences:
        sentences = [normalized]
    tokens = query_tokens(queries)

    def score(item: tuple[int, str]) -> tuple[int, int, int]:
        index, sentence = item
        folded = sentence.casefold()
        coverage = sum(token in folded for token in tokens)
        informative = int(45 <= len(sentence) <= CLAIM_CHAR_LIMIT)
        return (-coverage, -informative, index)

    index, first = min(enumerate(sentences), key=score)
    claim = first
    if len(claim) < 90 and index + 1 < len(sentences):
        claim = f"{claim} {sentences[index + 1]}"
    return trim_words(claim, CLAIM_CHAR_LIMIT)


def bounded_summary(question: str, claims: list[dict[str, Any]]) -> str:
    """Create a substantive summary from the same grounded extractive claims."""

    lead = (
        f"For the question “{SPACE_RE.sub(' ', question).strip()}”, "
        "the retrieved sources provide the following source-specific evidence: "
    )
    body = " ".join(str(claim["statement"]) for claim in claims)
    words = (lead + body).split()
    if len(words) > SUMMARY_WORD_LIMIT:
        words = words[:SUMMARY_WORD_LIMIT]
        return " ".join(words).rstrip(" ,;:-") + "."
    return " ".join(words)


def build_answer(
    *,
    question_id: str,
    question: str,
    selected: list[dict[str, Any]],
    minimum_sources: int,
) -> dict[str, Any]:
    """Build a closed answer or the declared null response."""

    if len(selected) < minimum_sources:
        return {"question_id": question_id, "answer": None, "evidence": []}
    claims: list[dict[str, Any]] = []
    evidence: list[dict[str, Any]] = []
    for index, candidate in enumerate(selected):
        row = candidate["row"]
        text = row.get("text")
        if not isinstance(text, str):
            raise SnapshotError("retrieval result text is invalid")
        claims.append(
            {
                "statement": extract_claim(text, list(candidate["queries"])),
                "evidence_indices": [index],
            }
        )
        evidence.append(evidence_identity(row))
    return {
        "question_id": question_id,
        "answer": {
            "summary": bounded_summary(question, claims),
            "claims": claims,
        },
        "evidence": evidence,
    }


def validate_answer(answer: dict[str, Any], selected: list[dict[str, Any]]) -> None:
    """Reject any drift in the generated answer and evidence order."""

    if tuple(answer) != ("question_id", "answer", "evidence"):
        raise SnapshotError("answer top-level order drifted")
    evidence = answer["evidence"]
    if answer["answer"] is None:
        if evidence != []:
            raise SnapshotError("null answer has evidence")
        return
    if (
        not isinstance(answer["answer"], dict)
        or tuple(answer["answer"]) != ("summary", "claims")
        or not isinstance(evidence, list)
    ):
        raise SnapshotError("answer contract drifted")
    claims = answer["answer"]["claims"]
    if not isinstance(claims, list) or len(claims) != len(evidence):
        raise SnapshotError("claim/evidence cardinality drifted")
    expected = [evidence_identity(candidate["row"]) for candidate in selected]
    if evidence != expected or len({serialized_evidence(row) for row in evidence}) != len(
        evidence
    ):
        raise SnapshotError("evidence identity or uniqueness drifted")
    for index, claim in enumerate(claims):
        if (
            not isinstance(claim, dict)
            or tuple(claim) != ("statement", "evidence_indices")
            or not isinstance(claim["statement"], str)
            or not claim["statement"].strip()
            or claim["evidence_indices"] != [index]
        ):
            raise SnapshotError("claim contract or first-use order drifted")


def checked_output(bundle: Path, output: Path) -> Path:
    """Resolve a new regular output outside the immutable snapshot."""

    if output.exists() or output.is_symlink():
        raise SnapshotError(f"refusing to overwrite output: {output}")
    parent = output.parent.resolve()
    if not parent.is_dir() or parent.is_symlink():
        raise SnapshotError(f"output parent is absent or linked: {output.parent}")
    checked = parent / output.name
    try:
        checked.relative_to(bundle.resolve(strict=True))
    except ValueError:
        return checked
    raise SnapshotError("output cannot be written inside the snapshot")


def write_new(path: Path, payload: str) -> None:
    """Publish one durable no-replace answer."""

    try:
        with path.open("x", encoding="utf-8", newline="\n") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
    except FileExistsError as exc:
        raise SnapshotError(f"refusing to overwrite output: {path}") from exc


def main(argv: list[str] | None = None) -> int:
    """Execute the sealed consultation operation."""

    configure_utf8()
    args = build_parser().parse_args(argv)
    try:
        queries = args.query
        if (
            not isinstance(queries, list)
            or not 3 <= len(queries) <= 5
            or len(set(queries)) != len(queries)
            or any(not query.strip() for query in queries)
        ):
            raise SnapshotError("supply three through five distinct non-empty queries")
        if not args.question_id.strip() or not args.question.strip():
            raise SnapshotError("question identity and text must be non-empty")
        if (
            not 1 <= args.top_k <= 8
            or not 1 <= args.minimum_sources <= args.max_sources <= 12
            or args.max_sources > args.minimum_sources + 2
        ):
            raise SnapshotError(
                "require top-k 1..8 and minimum <= maximum <= minimum+2 <= 12"
            )
        checked = checked_output(args.bundle, args.output)
        snapshot = load_snapshot(args.bundle)
        searches = [
            search_snapshot(
                snapshot,
                query,
                args.mode,
                args.top_k,
                source_ids=[],
                concept_ids=[],
                concept_types=[],
            )
            for query in queries
        ]
        selected = fuse_results(searches, args.max_sources)
        answer = build_answer(
            question_id=args.question_id,
            question=args.question,
            selected=selected,
            minimum_sources=args.minimum_sources,
        )
        validate_answer(answer, selected if answer["answer"] is not None else [])
        payload = canonical_json(answer)
        write_new(checked, payload)
        sys.stdout.write(payload)
        return 0
    except (
        SnapshotError,
        OSError,
        UnicodeError,
        ValueError,
        TypeError,
        KeyError,
        IndexError,
        OverflowError,
    ) as exc:
        print(
            json.dumps(
                {"status": "error", "code": "bounded-answer-error", "error": str(exc)},
                ensure_ascii=False,
                sort_keys=True,
                allow_nan=False,
            ),
            file=sys.stderr,
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
