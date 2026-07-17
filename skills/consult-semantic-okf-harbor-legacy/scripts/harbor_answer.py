#!/usr/bin/env python3
"""Prepare and finalize compact, ledger-bound Semantic OKF answers.

The command is intentionally read-only. ``prepare`` runs deterministic TF-IDF
over the authoritative record ledger and emits opaque support IDs plus bounded
excerpts. ``finalize`` rebuilds that support pack and expands a strict draft
into the public Harbor answer contract.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
from collections import Counter
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Mapping, Sequence


SCHEMA_VERSION = "semantic-okf-harbor-support-pack/1.0"
STRATEGY = "ledger-tfidf-facet-round-robin-v1"
TOKEN_RE = re.compile(r"[^\W_]+", re.UNICODE)
SPLIT_RE = re.compile(
    r"[?!;.,]+|\b(?:and|but|while|whereas|versus|vs\.?|however|although)\b",
    re.IGNORECASE,
)
HEX64_RE = re.compile(r"[0-9a-f]{64}")
STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "been",
    "by",
    "for",
    "from",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "this",
    "to",
    "was",
    "were",
    "with",
}
PACK_KEYS = {
    "question_id",
    "question_sha256",
    "parameters",
    "support_pack_sha256",
    "answer",
    "evidence",
}
ANSWER_KEYS = {"summary", "claims"}
CLAIM_KEYS = {"statement", "evidence_indices"}
PARAMETER_KEYS = {"facet_limit", "per_facet", "max_supports", "excerpt_chars", "strategy"}
EVIDENCE_KEYS = (
    "source_id",
    "record_id",
    "concept_path",
    "source_path",
    "record_sha256",
    "locator",
    "text_sha256",
)


class AnswerError(RuntimeError):
    """Describe an invalid bundle, support pack, or answer draft."""


def _configure_utf8() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            try:
                reconfigure(encoding="utf-8")
            except (AttributeError, OSError, ValueError):
                pass


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise AnswerError(f"duplicate JSON key: {key!r}")
        result[key] = value
    return result


def _loads_json(text: str, label: str) -> Any:
    try:
        return json.loads(text, object_pairs_hook=_strict_object)
    except (json.JSONDecodeError, UnicodeError) as exc:
        raise AnswerError(f"invalid {label}: {exc}") from exc


def _read_json(path: Path, label: str) -> Any:
    try:
        return _loads_json(path.read_text(encoding="utf-8"), label)
    except OSError as exc:
        raise AnswerError(f"cannot read {label}: {exc}") from exc


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _sha256_json(value: Any) -> str:
    return _sha256_text(_canonical_json(value))


def _exact_keys(value: Mapping[str, Any], expected: set[str], label: str) -> None:
    actual = set(value)
    if actual != expected:
        missing = sorted(expected - actual)
        unknown = sorted(actual - expected)
        raise AnswerError(f"{label} keys differ (missing={missing}, unknown={unknown})")


def _text(value: Any, label: str, *, maximum: int = 64 * 1024) -> str:
    if not isinstance(value, str) or not value.strip():
        raise AnswerError(f"{label} must be non-empty text")
    if len(value.encode("utf-8")) > maximum:
        raise AnswerError(f"{label} exceeds {maximum} UTF-8 bytes")
    return value.strip()


def _tokens(value: str) -> list[str]:
    result: list[str] = []
    for raw in TOKEN_RE.findall(value):
        token = raw.casefold()
        if len(token) > 5 and token.endswith("ies"):
            token = token[:-3] + "y"
        elif len(token) > 4 and token.endswith("s") and not token.endswith("ss"):
            token = token[:-1]
        if token not in STOPWORDS:
            result.append(token)
    return result


def _safe_concept(root: Path, value: Any) -> None:
    if not isinstance(value, str) or "\\" in value:
        raise AnswerError("record contains an unsafe concept_path")
    pure = PurePosixPath(value)
    if pure.is_absolute() or ".." in pure.parts or not pure.parts or pure.parts[0] != "concepts":
        raise AnswerError(f"unsafe concept_path: {value!r}")
    target = root.joinpath(*pure.parts)
    try:
        resolved = target.resolve(strict=True)
        resolved.relative_to(root.resolve(strict=True))
    except (OSError, ValueError) as exc:
        raise AnswerError(f"concept_path escapes or is missing: {value!r}") from exc
    if target.is_symlink() or not resolved.is_file():
        raise AnswerError(f"concept_path is not a regular local file: {value!r}")


def _load_records(bundle: Path) -> list[dict[str, Any]]:
    if not bundle.is_dir() or bundle.is_symlink():
        raise AnswerError("bundle must be an existing non-symlink directory")
    report = _read_json(bundle / "semantic" / "build-report.json", "build report")
    if not isinstance(report, dict) or report.get("valid") is not True or report.get("status") != "pass":
        raise AnswerError("build report does not identify a passing snapshot")
    ledger = bundle / "semantic" / "records.jsonl"
    try:
        lines = ledger.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        raise AnswerError(f"cannot read record ledger: {exc}") from exc
    if not lines:
        raise AnswerError("record ledger must not be empty")
    records: list[dict[str, Any]] = []
    identities: set[tuple[str, str]] = set()
    for number, line in enumerate(lines, start=1):
        row = _loads_json(line, f"record ledger line {number}")
        if not isinstance(row, dict):
            raise AnswerError(f"record ledger line {number} must be an object")
        required = ("source_id", "record_id", "concept_path", "source_path", "record_sha256", "body")
        for field in required:
            if not isinstance(row.get(field), str) or not row[field]:
                raise AnswerError(f"record ledger line {number}.{field} must be non-empty text")
        if not HEX64_RE.fullmatch(row["record_sha256"]):
            raise AnswerError(f"record ledger line {number}.record_sha256 must be lowercase SHA-256")
        identity = (row["source_id"], row["record_id"])
        if identity in identities:
            raise AnswerError(f"duplicate source-record identity: {identity!r}")
        identities.add(identity)
        _safe_concept(bundle, row["concept_path"])
        records.append(row)
    return records


def decompose_facets(question: str, limit: int) -> list[str]:
    """Return the full request and bounded, order-preserving clauses."""

    normalized = " ".join(question.split())
    candidates = [normalized]
    candidates.extend(" ".join(part.split()) for part in SPLIT_RE.split(normalized))
    result: list[str] = []
    seen: set[str] = set()
    for candidate in candidates:
        candidate = candidate.strip(" ,:-")
        key = candidate.casefold()
        candidate_tokens = _tokens(candidate)
        too_short = len(candidate_tokens) < 2 and not (
            len(candidate_tokens) == 1 and len(candidate_tokens[0]) >= 5
        )
        if not candidate or key in seen or (candidate != normalized and too_short):
            continue
        seen.add(key)
        result.append(candidate)
        if len(result) == limit:
            break
    return result


def _document_text(record: Mapping[str, Any]) -> str:
    attributes = record.get("attributes")
    attribute_text = _canonical_json(attributes) if isinstance(attributes, dict) else ""
    return "\n".join(
        (
            str(record.get("title") or ""),
            str(record.get("record_id") or ""),
            attribute_text,
            str(record.get("body") or ""),
        )
    )


def _tfidf_rank(records: Sequence[Mapping[str, Any]], query: str, limit: int) -> list[tuple[int, float]]:
    document_counts = [Counter(_tokens(_document_text(record))) for record in records]
    heading_counts = [
        Counter(_tokens(f"{record.get('title') or ''}\n{record.get('record_id') or ''}"))
        for record in records
    ]
    document_frequency: Counter[str] = Counter()
    for counts in document_counts:
        document_frequency.update(counts.keys())
    size = len(records)
    idf = {token: math.log((size + 1.0) / (frequency + 1.0)) + 1.0 for token, frequency in document_frequency.items()}
    query_counts = Counter(_tokens(query))
    query_weights = {
        token: (1.0 + math.log(count)) * idf.get(token, math.log(size + 1.0) + 1.0)
        for token, count in query_counts.items()
    }
    query_norm = math.sqrt(math.fsum(weight * weight for weight in query_weights.values()))
    scored: list[tuple[int, float]] = []
    if not query_norm:
        return scored
    for index, counts in enumerate(document_counts):
        shared = set(query_weights) & set(counts)
        if not shared:
            continue
        body_score = math.fsum(
            query_weights[token] * (1.0 + 0.25 * math.log(counts[token])) * idf[token]
            for token in shared
        )
        headings = heading_counts[index]
        heading_score = math.fsum(
            query_weights[token] * (1.0 + 0.25 * math.log(headings[token])) * idf[token]
            for token in set(query_weights) & set(headings)
        )
        score = (body_score + 2.5 * heading_score) / query_norm
        if score > 0.0:
            scored.append((index, score))
    scored.sort(
        key=lambda item: (
            -item[1],
            str(records[item[0]].get("source_id")),
            str(records[item[0]].get("record_id")),
        )
    )
    return scored[:limit]


def _best_excerpt(body: str, query: str, maximum: int, preferred: tuple[int, int] | None = None) -> tuple[str, int, int]:
    if len(body) <= maximum:
        return body, 0, len(body)
    query_terms = set(_tokens(query))
    starts = {0, max(0, len(body) - maximum)}
    if preferred is not None:
        middle = (preferred[0] + preferred[1]) // 2
        starts.add(max(0, min(len(body) - maximum, middle - maximum // 2)))
    casefolded = body.casefold()
    for term in query_terms:
        position = casefolded.find(term)
        while position >= 0:
            starts.add(max(0, min(len(body) - maximum, position - maximum // 3)))
            position = casefolded.find(term, position + 1)
    ranked: list[tuple[int, int, int]] = []
    for start in starts:
        end = min(len(body), start + maximum)
        window_tokens = _tokens(body[start:end])
        score = 10 * len(query_terms & set(window_tokens)) + sum(token in query_terms for token in window_tokens)
        if preferred is not None and start <= preferred[0] < end:
            score += 3
        ranked.append((-score, start, end))
    _, start, end = min(ranked)
    return body[start:end], start, end


def _evidence(record: Mapping[str, Any]) -> dict[str, Any]:
    body = str(record["body"])
    return {
        "source_id": record["source_id"],
        "record_id": record["record_id"],
        "concept_path": record["concept_path"],
        "source_path": record["source_path"],
        "record_sha256": record["record_sha256"],
        "locator": {"kind": "record", "target": "record.body"},
        "text_sha256": _sha256_text(body),
    }


def _support_id(evidence: Mapping[str, Any]) -> str:
    return "support-" + _sha256_json(evidence)[:20]


def _parameters(args: argparse.Namespace) -> dict[str, Any]:
    return {
        "facet_limit": args.facet_limit,
        "per_facet": args.per_facet,
        "max_supports": args.max_supports,
        "excerpt_chars": args.excerpt_chars,
        "strategy": STRATEGY,
    }


def build_support_pack(bundle: Path, question_id: str, question: str, parameters: Mapping[str, Any]) -> dict[str, Any]:
    records = _load_records(bundle)
    facets = decompose_facets(question, int(parameters["facet_limit"]))
    ranked_by_facet = [_tfidf_rank(records, facet, int(parameters["per_facet"])) for facet in facets]
    support_rows: list[dict[str, Any]] = []
    by_identity: dict[tuple[str, str], dict[str, Any]] = {}
    for rank_offset in range(int(parameters["per_facet"])):
        for facet_index, ranked in enumerate(ranked_by_facet):
            if rank_offset >= len(ranked):
                continue
            record_index, score = ranked[rank_offset]
            record = records[record_index]
            identity = (str(record["source_id"]), str(record["record_id"]))
            facet_id = f"facet-{facet_index + 1:02d}"
            existing = by_identity.get(identity)
            if existing is not None:
                if facet_id not in existing["facet_ids"]:
                    existing["facet_ids"].append(facet_id)
                existing["score"] = max(float(existing["score"]), round(score, 12))
                continue
            if len(support_rows) >= int(parameters["max_supports"]):
                continue
            evidence = _evidence(record)
            excerpt, start, end = _best_excerpt(
                str(record["body"]), facets[facet_index], int(parameters["excerpt_chars"])
            )
            row = {
                "support_id": _support_id(evidence),
                "facet_ids": [facet_id],
                "rank": len(support_rows) + 1,
                "score": round(score, 12),
                "source_id": evidence["source_id"],
                "record_id": evidence["record_id"],
                "concept_path": evidence["concept_path"],
                "source_path": evidence["source_path"],
                "record_sha256": evidence["record_sha256"],
                "text_sha256": evidence["text_sha256"],
                "excerpt": excerpt,
                "excerpt_sha256": _sha256_text(excerpt),
                "excerpt_start": start,
                "excerpt_end": end,
            }
            support_rows.append(row)
            by_identity[identity] = row
    if not support_rows:
        raise AnswerError("retrieval produced no support")
    digest_input = {
        "schema_version": SCHEMA_VERSION,
        "question_id": question_id,
        "question_sha256": _sha256_text(question),
        "parameters": dict(parameters),
        "facets": facets,
        "supports": support_rows,
    }
    pack_sha256 = _sha256_json(digest_input)
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "pass",
        "read_only": True,
        "authoritative": False,
        "question_id": question_id,
        "question_sha256": _sha256_text(question),
        "parameters": dict(parameters),
        "facets": [
            {"facet_id": f"facet-{index + 1:02d}", "text": facet}
            for index, facet in enumerate(facets)
        ],
        "supports": support_rows,
        "support_pack_sha256": pack_sha256,
        "draft_template": {
            "question_id": question_id,
            "question_sha256": _sha256_text(question),
            "parameters": dict(parameters),
            "support_pack_sha256": pack_sha256,
            "answer": {"summary": "REPLACE", "claims": []},
            "evidence": [],
        },
    }


def _load_draft(path: str) -> Mapping[str, Any]:
    try:
        text = sys.stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise AnswerError(f"cannot read draft: {exc}") from exc
    draft = _loads_json(text, "answer draft")
    if not isinstance(draft, dict):
        raise AnswerError("answer draft must be an object")
    return draft


def finalize(pack: Mapping[str, Any], draft: Mapping[str, Any]) -> dict[str, Any]:
    _exact_keys(draft, PACK_KEYS, "answer draft")
    if draft["question_id"] != pack["question_id"]:
        raise AnswerError("draft question_id does not match the recomputed pack")
    if draft["question_sha256"] != pack["question_sha256"]:
        raise AnswerError("draft question_sha256 does not match the recomputed pack")
    if draft["parameters"] != pack["parameters"]:
        raise AnswerError("draft parameters do not match the recomputed pack")
    if draft["support_pack_sha256"] != pack["support_pack_sha256"]:
        raise AnswerError("draft support_pack_sha256 does not match the recomputed pack")
    answer = draft["answer"]
    if not isinstance(answer, dict):
        raise AnswerError("draft answer must be an object")
    _exact_keys(answer, ANSWER_KEYS, "draft answer")
    summary = _text(answer["summary"], "answer.summary")
    if len(summary.split()) > 450:
        raise AnswerError("answer.summary must contain at most 450 words")
    claims = answer["claims"]
    if not isinstance(claims, list) or not claims:
        raise AnswerError("answer.claims must be a non-empty array")
    if len(claims) > 64:
        raise AnswerError("answer.claims must contain at most 64 items")
    support_ids = draft["evidence"]
    if not isinstance(support_ids, list) or not support_ids:
        raise AnswerError("draft evidence must be a non-empty support-ID array")
    if any(not isinstance(value, str) or not value for value in support_ids):
        raise AnswerError("every draft evidence item must be a support ID")
    if len(support_ids) != len(set(support_ids)):
        raise AnswerError("draft evidence contains duplicate support IDs")
    available = {row["support_id"]: row for row in pack["supports"]}
    unknown = sorted(set(support_ids) - set(available))
    if unknown:
        raise AnswerError(f"draft references unknown supports: {unknown}")
    normalized_claims: list[dict[str, Any]] = []
    first_use: list[int] = []
    seen: set[int] = set()
    for number, claim in enumerate(claims, start=1):
        if not isinstance(claim, dict):
            raise AnswerError(f"answer.claims[{number}] must be an object")
        _exact_keys(claim, CLAIM_KEYS, f"answer.claims[{number}]")
        statement = _text(claim["statement"], f"answer.claims[{number}].statement")
        indices = claim["evidence_indices"]
        if not isinstance(indices, list) or not indices:
            raise AnswerError(f"answer.claims[{number}].evidence_indices must be non-empty")
        if len(indices) != len(set(indices)):
            raise AnswerError(f"answer.claims[{number}] repeats an evidence index")
        for index in indices:
            if isinstance(index, bool) or not isinstance(index, int) or not 0 <= index < len(support_ids):
                raise AnswerError(f"answer.claims[{number}] has an out-of-range evidence index")
            if index not in seen:
                seen.add(index)
                first_use.append(index)
        normalized_claims.append({"statement": statement, "evidence_indices": indices})
    expected_order = list(range(len(support_ids)))
    if first_use != expected_order:
        if set(first_use) != set(expected_order):
            raise AnswerError("draft contains unused evidence")
        raise AnswerError("draft evidence is not ordered by first use")
    public_evidence = [
        {key: available[support_id][key] if key != "locator" else {"kind": "record", "target": "record.body"} for key in EVIDENCE_KEYS}
        for support_id in support_ids
    ]
    return {
        "question_id": pack["question_id"],
        "answer": {"summary": summary, "claims": normalized_claims},
        "evidence": public_evidence,
    }


def _add_common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--question-id", required=True)
    parser.add_argument("--question", required=True)
    parser.add_argument("--facet-limit", type=int, default=8)
    parser.add_argument("--per-facet", type=int, default=4)
    parser.add_argument("--max-supports", type=int, default=16)
    parser.add_argument("--excerpt-chars", type=int, default=700)


def _validate_args(args: argparse.Namespace) -> tuple[str, str]:
    question_id = _text(args.question_id, "question_id", maximum=256)
    question = _text(args.question, "question")
    bounds = {
        "facet_limit": (1, 8),
        "per_facet": (1, 10),
        "max_supports": (1, 32),
        "excerpt_chars": (160, 1200),
    }
    for field, (minimum, maximum) in bounds.items():
        value = getattr(args, field)
        if isinstance(value, bool) or not isinstance(value, int) or not minimum <= value <= maximum:
            raise AnswerError(f"--{field.replace('_', '-')} must be within {minimum}-{maximum}")
    return question_id, question


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle", type=Path)
    commands = parser.add_subparsers(dest="command", required=True)
    prepare = commands.add_parser("prepare", help="Retrieve a compact support pack.")
    _add_common(prepare)
    complete = commands.add_parser("finalize", help="Recompute support and close a strict answer draft.")
    _add_common(complete)
    complete.add_argument("--draft", default="-", help="Draft JSON path, or '-' for stdin.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    _configure_utf8()
    args = build_parser().parse_args(argv)
    try:
        question_id, question = _validate_args(args)
        parameters = _parameters(args)
        pack = build_support_pack(args.bundle, question_id, question, parameters)
        payload = pack if args.command == "prepare" else finalize(pack, _load_draft(args.draft))
    except AnswerError as exc:
        print(_canonical_json({"status": "error", "code": "answer-invalid", "error": str(exc), "read_only": True}), file=sys.stderr)
        return 2
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
