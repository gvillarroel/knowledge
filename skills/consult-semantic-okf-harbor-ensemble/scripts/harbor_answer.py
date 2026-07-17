#!/usr/bin/env python3
"""Prepare and finalize compact ensemble Semantic OKF answers.

The unchanged ensemble runtime executes its declared quality or fast policy for
the full question and bounded focused facets. This read-only adapter unions
those independently ranked candidates, projects them to exact authoritative
ledger parents, and recomputes the support pack before finalization.
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

from _ensemble_snapshot import (  # noqa: E402
    SnapshotError,
    load_snapshot,
    search_snapshot,
)


SCHEMA_VERSION = "semantic-okf-harbor-support-pack/1.0"
STRATEGY = "ensemble-full-focused-parent-union-v1"
TOKEN_RE = re.compile(r"[^\W_]+", re.UNICODE)
SPLIT_RE = re.compile(
    r"[?!;.,]+|\b(?:and|but|while|whereas|versus|vs\.?|however|although)\b",
    re.IGNORECASE,
)
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
    "policy",
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


def _reject_constant(value: str) -> None:
    raise AnswerError(f"non-standard JSON number: {value!r}")


def _loads_json(text: str, label: str) -> Any:
    try:
        return json.loads(
            text,
            object_pairs_hook=_strict_object,
            parse_constant=_reject_constant,
        )
    except (json.JSONDecodeError, UnicodeError) as exc:
        raise AnswerError(f"invalid {label}: {exc}") from exc


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _sha256_json(value: Any) -> str:
    return _sha256_text(_canonical_json(value))


def _exact_keys(value: Mapping[str, Any], expected: set[str], label: str) -> None:
    actual = set(value)
    if actual != expected:
        raise AnswerError(
            f"{label} keys differ (missing={sorted(expected - actual)}, "
            f"unknown={sorted(actual - expected)})"
        )


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
    """Return the unchanged full question plus bounded focused clauses."""

    normalized = " ".join(question.split())
    candidates = [normalized]
    candidates.extend(" ".join(part.split()) for part in SPLIT_RE.split(normalized))
    result: list[str] = []
    seen: set[str] = set()
    for candidate in candidates:
        candidate = candidate.strip(" ,:-")
        key = candidate.casefold()
        tokens = _tokens(candidate)
        too_short = len(tokens) < 2 and not (len(tokens) == 1 and len(tokens[0]) >= 5)
        if not candidate or key in seen or (candidate != normalized and too_short):
            continue
        seen.add(key)
        result.append(candidate)
        if len(result) == limit:
            break
    return result


def _record_index(records: Sequence[Mapping[str, Any]]) -> dict[tuple[str, str], Mapping[str, Any]]:
    result: dict[tuple[str, str], Mapping[str, Any]] = {}
    for record in records:
        source_id, record_id = record.get("source_id"), record.get("record_id")
        if not isinstance(source_id, str) or not isinstance(record_id, str):
            raise AnswerError("authoritative ledger record has an invalid identity")
        identity = (source_id, record_id)
        if identity in result:
            raise AnswerError(f"duplicate authoritative identity: {identity!r}")
        result[identity] = record
    return result


def _best_excerpt(
    body: str,
    query: str,
    maximum: int,
    preferred: tuple[int, int] | None = None,
) -> tuple[str, int, int]:
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
        score = 10 * len(query_terms & set(window_tokens))
        score += sum(token in query_terms for token in window_tokens)
        if preferred is not None and start <= preferred[0] < end:
            score += 3
        ranked.append((-score, start, end))
    _, start, end = min(ranked)
    return body[start:end], start, end


def _parent_evidence(record: Mapping[str, Any]) -> dict[str, Any]:
    required = ("source_id", "record_id", "concept_path", "source_path", "record_sha256", "body")
    if any(not isinstance(record.get(key), str) or not record[key] for key in required):
        raise AnswerError("authoritative ledger parent has incomplete evidence fields")
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


def _validate_hit(
    hit: Mapping[str, Any],
    passage: Mapping[str, Any],
    record: Mapping[str, Any],
) -> tuple[int, int] | None:
    for row_name, row in (("ensemble hit", hit), ("ensemble passage", passage)):
        for key in ("source_id", "record_id", "record_sha256", "concept_path", "source_path"):
            if row.get(key) != record.get(key):
                raise AnswerError(f"{row_name} {key} differs from its authoritative parent")
    body = record.get("body")
    locator = passage.get("locator")
    text = passage.get("text")
    text_sha256 = passage.get("text_sha256")
    if not isinstance(body, str) or not isinstance(locator, Mapping):
        raise AnswerError("ensemble passage has no valid authoritative locator")
    if locator.get("kind") != "character-range" or locator.get("target") != "record-body":
        raise AnswerError("ensemble support must be a record-body character range")
    start, end = locator.get("start"), locator.get("end")
    if (
        isinstance(start, bool)
        or isinstance(end, bool)
        or not isinstance(start, int)
        or not isinstance(end, int)
        or not 0 <= start < end <= len(body)
    ):
        raise AnswerError("ensemble passage has an invalid record-body range")
    selected = body[start:end]
    if selected != text or _sha256_text(selected) != text_sha256:
        raise AnswerError("ensemble passage text or hash differs from its authoritative range")
    return start, end


def _support_id(
    evidence: Mapping[str, Any],
    excerpt_start: int,
    excerpt_end: int,
    excerpt_sha256: str,
) -> str:
    binding = {
        "evidence": dict(evidence),
        "excerpt_start": excerpt_start,
        "excerpt_end": excerpt_end,
        "excerpt_sha256": excerpt_sha256,
    }
    return "support-" + _sha256_json(binding)[:20]


def _parameters(args: argparse.Namespace) -> dict[str, Any]:
    return {
        "facet_limit": args.facet_limit,
        "per_facet": args.per_facet,
        "max_supports": args.max_supports,
        "excerpt_chars": args.excerpt_chars,
        "policy": args.policy,
        "strategy": STRATEGY,
    }


def _passages_by_identity(search: Mapping[str, Any]) -> dict[tuple[str, str, str], Mapping[str, Any]]:
    rows = search.get("evidence_rows")
    if not isinstance(rows, list):
        raise AnswerError("ensemble search has no exact evidence rows")
    result: dict[tuple[str, str, str], Mapping[str, Any]] = {}
    for row in rows:
        if not isinstance(row, Mapping):
            raise AnswerError("ensemble evidence contains a non-object row")
        exact = (str(row.get("source_id")), str(row.get("record_id")), str(row.get("record_sha256")))
        if exact in result:
            raise AnswerError("ensemble search repeats an exact evidence identity")
        result[exact] = row
    return result


def build_support_pack(
    bundle: Path,
    question_id: str,
    question: str,
    parameters: Mapping[str, Any],
) -> dict[str, Any]:
    _exact_keys(parameters, PARAMETER_KEYS, "parameters")
    if parameters.get("policy") not in {"quality", "fast"} or parameters.get("strategy") != STRATEGY:
        raise AnswerError("parameters do not select a closed ensemble strategy")
    try:
        snapshot = load_snapshot(bundle)
        facets = decompose_facets(question, int(parameters["facet_limit"]))
        searches = [
            search_snapshot(
                snapshot,
                facet,
                str(parameters["policy"]),
                int(parameters["per_facet"]),
            )
            for facet in facets
        ]
    except (SnapshotError, OSError, ValueError) as exc:
        raise AnswerError(f"ensemble snapshot is unavailable: {exc}") from exc
    records = _record_index(snapshot.graph.records)
    passages = [_passages_by_identity(search) for search in searches]
    supports: list[dict[str, Any]] = []
    by_identity: dict[tuple[str, str], dict[str, Any]] = {}
    for offset in range(int(parameters["per_facet"])):
        for facet_index, search in enumerate(searches):
            hits = search.get("results")
            if not isinstance(hits, list) or offset >= len(hits):
                continue
            hit = hits[offset]
            if not isinstance(hit, Mapping):
                raise AnswerError("ensemble search returned a non-object hit")
            identity = (str(hit.get("source_id")), str(hit.get("record_id")))
            record = records.get(identity)
            if record is None:
                raise AnswerError("ensemble hit is absent from the authoritative ledger")
            exact = (identity[0], identity[1], str(hit.get("record_sha256")))
            passage = passages[facet_index].get(exact)
            if passage is None:
                raise AnswerError("ensemble hit lacks exact passage evidence")
            preferred = _validate_hit(hit, passage, record)
            facet_id = f"facet-{facet_index + 1:02d}"
            existing = by_identity.get(identity)
            if existing is not None:
                if facet_id not in existing["facet_ids"]:
                    existing["facet_ids"].append(facet_id)
                continue
            if len(supports) >= int(parameters["max_supports"]):
                continue
            body = str(record["body"])
            excerpt, start, end = _best_excerpt(
                body,
                facets[facet_index],
                int(parameters["excerpt_chars"]),
                preferred,
            )
            evidence = _parent_evidence(record)
            excerpt_sha256 = _sha256_text(excerpt)
            row = {
                "support_id": _support_id(evidence, start, end, excerpt_sha256),
                "facet_ids": [facet_id],
                "rank": len(supports) + 1,
                "policy": parameters["policy"],
                "group_id": hit.get("group_id"),
                "source_id": evidence["source_id"],
                "record_id": evidence["record_id"],
                "concept_path": evidence["concept_path"],
                "source_path": evidence["source_path"],
                "record_sha256": evidence["record_sha256"],
                "locator": evidence["locator"],
                "text_sha256": evidence["text_sha256"],
                "excerpt": excerpt,
                "excerpt_start": start,
                "excerpt_end": end,
                "excerpt_sha256": excerpt_sha256,
            }
            supports.append(row)
            by_identity[identity] = row
    if not supports:
        raise AnswerError("ensemble candidate union produced no authoritative support")
    digest_input = {
        "schema_version": SCHEMA_VERSION,
        "question_id": question_id,
        "question_sha256": _sha256_text(question),
        "parameters": dict(parameters),
        "facets": facets,
        "supports": supports,
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
        "candidate_union": {
            "full_query": True,
            "focused_query_count": max(0, len(facets) - 1),
            "selected_parent_count": len(supports),
        },
        "facets": [
            {"facet_id": f"facet-{index + 1:02d}", "text": facet}
            for index, facet in enumerate(facets)
        ],
        "supports": supports,
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


def _load_draft(path: str, bundle: Path) -> Mapping[str, Any]:
    try:
        if path == "-":
            text = sys.stdin.read()
        else:
            draft_path = Path(path).resolve(strict=True)
            bundle_root = bundle.resolve(strict=True)
            if draft_path == bundle_root or bundle_root in draft_path.parents:
                raise AnswerError("answer draft must not be read from inside the bundle")
            text = draft_path.read_text(encoding="utf-8")
    except AnswerError:
        raise
    except (OSError, UnicodeError) as exc:
        raise AnswerError(f"cannot read answer draft: {exc}") from exc
    draft = _loads_json(text, "answer draft")
    if not isinstance(draft, Mapping):
        raise AnswerError("answer draft must be an object")
    return draft


def finalize(pack: Mapping[str, Any], draft: Mapping[str, Any]) -> dict[str, Any]:
    """Validate a closed draft and emit exact evidence in first-use order."""

    _exact_keys(draft, PACK_KEYS, "answer draft")
    for key in ("question_id", "question_sha256", "parameters", "support_pack_sha256"):
        if draft[key] != pack[key]:
            raise AnswerError(f"draft {key} does not match the recomputed support pack")
    answer = draft["answer"]
    if not isinstance(answer, Mapping):
        raise AnswerError("draft answer must be an object")
    _exact_keys(answer, ANSWER_KEYS, "draft answer")
    summary = _text(answer["summary"], "answer.summary")
    if len(summary.split()) > 450:
        raise AnswerError("answer.summary exceeds 450 words")
    claims = answer["claims"]
    if not isinstance(claims, list) or not claims:
        raise AnswerError("answer.claims must be a non-empty array")
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
        raise AnswerError(f"draft references unknown or tampered supports: {unknown}")
    normalized_claims: list[dict[str, Any]] = []
    first_use: list[int] = []
    seen: set[int] = set()
    for number, claim in enumerate(claims, start=1):
        if not isinstance(claim, Mapping):
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
        normalized_claims.append({"statement": statement, "evidence_indices": list(indices)})
    expected = list(range(len(support_ids)))
    if first_use != expected:
        if set(first_use) != set(expected):
            raise AnswerError("draft contains unused evidence")
        raise AnswerError("draft evidence is not ordered by first use")
    public_evidence = [
        {key: available[support_id][key] for key in EVIDENCE_KEYS}
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
    parser.add_argument("--per-facet", type=int, default=10)
    parser.add_argument("--max-supports", type=int, default=32)
    parser.add_argument("--excerpt-chars", type=int, default=700)
    parser.add_argument("--policy", choices=("quality", "fast"), default="quality")


def _validate_args(args: argparse.Namespace) -> tuple[str, str]:
    question_id = _text(args.question_id, "question_id", maximum=256)
    question = _text(args.question, "question")
    bounds = {
        "facet_limit": (1, 8),
        "per_facet": (1, 10),
        "max_supports": (1, 32),
        "excerpt_chars": (240, 1200),
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
    prepare = commands.add_parser("prepare", help="Retrieve a compact ensemble support pack.")
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
        payload = (
            pack
            if args.command == "prepare"
            else finalize(pack, _load_draft(args.draft, args.bundle))
        )
    except AnswerError as exc:
        error = {"status": "error", "code": "answer-invalid", "error": str(exc), "read_only": True}
        print(_canonical_json(error), file=sys.stderr)
        return 2
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
