#!/usr/bin/env python3
"""Prepare and finalize compact, parent-record-bound Semantic OKF answers.

The command is intentionally read-only. ``prepare`` runs the package's exact
hybrid chunk search once per bounded question facet, resolves every hit to its
authoritative ledger parent, and emits opaque support IDs plus short excerpts.
``finalize`` rebuilds that support pack and expands a strict draft into the
public Harbor answer contract.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from _embedding_snapshot import (  # noqa: E402
    ProviderUnavailable,
    SnapshotError,
    load_snapshot,
    search_snapshot,
)


SCHEMA_VERSION = "semantic-okf-harbor-support-pack/1.0"
STRATEGY = "hybrid-parent-facet-round-robin-v1"
TOKEN_RE = re.compile(r"[^\W_]+", re.UNICODE)
SPLIT_RE = re.compile(
    r"[?!;.,]+|\b(?:and|but|while|whereas|versus|vs\.?|however|although)\b",
    re.IGNORECASE,
)
HEX64_RE = re.compile(r"[0-9a-f]{64}")
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
PARAMETER_KEYS = {
    "facet_limit",
    "per_facet",
    "max_supports",
    "excerpt_chars",
    "mode",
    "strategy",
}
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
        result.append(token)
    return result


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
        "mode": args.mode,
        "strategy": STRATEGY,
    }


def build_support_pack(bundle: Path, question_id: str, question: str, parameters: Mapping[str, Any]) -> dict[str, Any]:
    try:
        snapshot = load_snapshot(bundle)
        facets = decompose_facets(question, int(parameters["facet_limit"]))
        searches = [
            search_snapshot(
                snapshot,
                facet,
                requested_mode=str(parameters["mode"]),
                top_k=int(parameters["per_facet"]),
                allow_fallback=True,
            )
            for facet in facets
        ]
    except (SnapshotError, ProviderUnavailable, ValueError) as exc:
        raise AnswerError(f"retrieval snapshot is unavailable: {exc}") from exc
    support_rows: list[dict[str, Any]] = []
    by_identity: dict[tuple[str, str], dict[str, Any]] = {}
    for rank_offset in range(int(parameters["per_facet"])):
        for facet_index, search in enumerate(searches):
            hits = search["hits"]
            if rank_offset >= len(hits):
                continue
            hit = hits[rank_offset]
            record = snapshot.records[str(hit["concept_id"])]
            component_scores = hit.get("scores") if isinstance(hit.get("scores"), Mapping) else {}
            score = next(
                (
                    float(component_scores[key])
                    for key in ("hybrid", "vector", "lexical")
                    if isinstance(component_scores.get(key), (int, float))
                ),
                0.0,
            )
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
            locator = hit.get("locator")
            preferred = None
            if (
                isinstance(locator, Mapping)
                and locator.get("kind") == "character-range"
                and isinstance(locator.get("start"), int)
                and isinstance(locator.get("end"), int)
            ):
                preferred = (int(locator["start"]), int(locator["end"]))
            excerpt, start, end = _best_excerpt(
                str(record["body"]),
                facets[facet_index],
                int(parameters["excerpt_chars"]),
                preferred,
            )
            row = {
                "support_id": _support_id(evidence),
                "facet_ids": [facet_id],
                "rank": len(support_rows) + 1,
                "score": round(score, 12),
                "chunk_id": hit["chunk_id"],
                "requested_mode": search["requested_mode"],
                "effective_mode": search["effective_mode"],
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
    parser.add_argument("--mode", choices=("auto", "hybrid", "vector", "lexical"), default="auto")


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
