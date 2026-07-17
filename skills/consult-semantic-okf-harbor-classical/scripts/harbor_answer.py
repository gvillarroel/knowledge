#!/usr/bin/env python3
"""Build compact Harbor support packs and compile strict grounded answers."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence


from _classical_snapshot import SnapshotError, load_snapshot, search_snapshot


FAMILY = "classical"
RETRIEVAL_MODE = "fusion"


SCHEMA_VERSION = "semantic-okf-harbor-support-pack/1.0"
ALGORITHM = "bounded-facet-deficit-parent-projection-v1"
QUESTION_ID = re.compile(r"^q[0-9]{3}$")
TOKEN = re.compile(r"[a-z0-9][a-z0-9._/-]*", re.IGNORECASE)
SPLIT_FACET = re.compile(
    r"\s*(?:[,;]|\b(?:and|or|versus|vs\.?|while|but|then)\b)\s*",
    re.IGNORECASE,
)
STOPWORDS = frozenset(
    "a an and are as at be been by can could did do does for from had has have how i if in into is it "
    "its may must of on or our should so than that the their them then there these this those through to "
    "under use using was were what when where which while who why will with would you your".split()
)
PACK_KEYS = ["schema_version", "parameters", "parameters_sha256", "facets", "supports"]
PARAMETER_KEYS = ["algorithm", "family", "question_id", "question", "retrieval", "snapshot"]
RETRIEVAL_KEYS = [
    "mode",
    "full_top_k",
    "per_facet_top_k",
    "max_facets",
    "max_supports",
    "protected_full",
    "snippet_chars",
    "snippets_per_support",
]
SUPPORT_KEYS = [
    "support_id",
    "source_id",
    "record_id",
    "concept_path",
    "source_path",
    "record_sha256",
    "locator",
    "text_sha256",
    "full_rank",
    "facet_ranks",
    "snippets",
]
SNIPPET_KEYS = ["start", "end", "text", "text_sha256"]
DRAFT_KEYS = ["question_id", "parameters_sha256", "summary", "claims"]
CLAIM_KEYS = ["statement", "support_ids"]
EVIDENCE_KEYS = [
    "source_id",
    "record_id",
    "concept_path",
    "source_path",
    "record_sha256",
    "locator",
    "text_sha256",
]


def _configure_utf8() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(encoding="utf-8")


def _canonical(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise SnapshotError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def strict_json(payload: str, *, label: str) -> Any:
    """Parse one strict JSON value, rejecting duplicate keys and non-finite numbers."""

    def reject_constant(value: str) -> None:
        raise SnapshotError(f"{label} contains a non-finite number: {value}")

    try:
        return json.loads(
            payload,
            object_pairs_hook=_strict_object,
            parse_constant=reject_constant,
        )
    except json.JSONDecodeError as exc:
        raise SnapshotError(f"{label} is not strict JSON: {exc.msg}") from exc


def _read_json(path: Path, *, label: str) -> Any:
    if not path.is_file() or path.is_symlink():
        raise SnapshotError(f"{label} must be a regular non-symlink file")
    return strict_json(path.read_text(encoding="utf-8"), label=label)


def _closed(mapping: Any, keys: Sequence[str], *, label: str) -> Mapping[str, Any]:
    if not isinstance(mapping, Mapping) or list(mapping.keys()) != list(keys):
        raise SnapshotError(f"{label} must contain exactly these ordered keys: {', '.join(keys)}")
    return mapping


def _bounded_int(value: Any, *, label: str, minimum: int, maximum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not minimum <= value <= maximum:
        raise SnapshotError(f"{label} must be an integer from {minimum} through {maximum}")
    return value


def _terms(value: str) -> list[str]:
    result: list[str] = []
    for term in TOKEN.findall(value.casefold()):
        if len(term) >= 3 and term not in STOPWORDS and term not in result:
            result.append(term)
    return result


def derive_facets(question: str, maximum: int) -> list[str]:
    """Derive a deterministic, bounded set of lexical coverage facets."""

    normalized = " ".join(question.split())
    pieces: list[str] = []
    for sentence in re.split(r"(?<=[.!?])\s+", normalized):
        for piece in SPLIT_FACET.split(sentence):
            clean = piece.strip(" .:!?()[]{}\"'")
            if _terms(clean) and clean.casefold() not in {item.casefold() for item in pieces}:
                pieces.append(clean)
            if len(pieces) >= maximum:
                return pieces
    return pieces or [normalized]


def _ledger(snapshot: Any) -> dict[tuple[str, str], Mapping[str, Any]]:
    path = snapshot.root / "semantic" / "records.jsonl"
    records: dict[tuple[str, str], Mapping[str, Any]] = {}
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            raise SnapshotError(f"semantic ledger contains a blank line at {number}")
        row = strict_json(line, label=f"semantic ledger line {number}")
        if not isinstance(row, Mapping):
            raise SnapshotError(f"semantic ledger line {number} is not an object")
        key = (str(row.get("source_id")), str(row.get("record_id")))
        if key in records:
            raise SnapshotError(f"duplicate authoritative record identity: {key[0]} / {key[1]}")
        records[key] = row
    return records


def _parent_projection(
    result: Mapping[str, Any],
    records: Mapping[tuple[str, str], Mapping[str, Any]],
) -> tuple[dict[str, Any], str]:
    key = (str(result.get("source_id")), str(result.get("record_id")))
    record = records.get(key)
    if record is None:
        raise SnapshotError(f"retrieval returned an unknown authoritative record: {key[0]} / {key[1]}")
    for field in ("record_sha256", "concept_path", "source_path"):
        if result.get(field) != record.get(field):
            raise SnapshotError(f"retrieval-to-ledger mismatch for {key[0]} / {key[1]}: {field}")
    body = record.get("body")
    if not isinstance(body, str) or not body:
        raise SnapshotError(f"authoritative record body is empty: {key[0]} / {key[1]}")
    locator = result.get("locator")
    text = result.get("text")
    if not isinstance(locator, Mapping) or not isinstance(text, str):
        raise SnapshotError("retrieval result is missing its exact locator or text")
    if locator.get("kind") == "record":
        selected = body
    elif locator.get("kind") == "character-range":
        start, end = locator.get("start"), locator.get("end")
        if (
            isinstance(start, bool)
            or isinstance(end, bool)
            or not isinstance(start, int)
            or not isinstance(end, int)
            or not 0 <= start < end <= len(body)
        ):
            raise SnapshotError("retrieval result contains an invalid character range")
        selected = body[start:end]
    else:
        raise SnapshotError("retrieval result contains an unsupported locator")
    if text != selected or result.get("text_sha256") != _sha256_text(selected):
        raise SnapshotError("retrieval result text does not match the authoritative locator")
    evidence = {
        "source_id": key[0],
        "record_id": key[1],
        "concept_path": str(record["concept_path"]),
        "source_path": str(record["source_path"]),
        "record_sha256": str(record["record_sha256"]),
        "locator": {"kind": "record"},
        "text_sha256": _sha256_text(body),
    }
    return evidence, body


def _snippet_windows(body: str, query: str, limit: int, count: int) -> list[dict[str, Any]]:
    terms = _terms(query)
    lowered = body.casefold()
    centers: list[int] = []
    for term in terms:
        start = 0
        for _ in range(12):
            position = lowered.find(term, start)
            if position < 0:
                break
            centers.append(position + len(term) // 2)
            start = position + len(term)
    if not centers:
        centers = [0]
    candidates: dict[tuple[int, int], tuple[int, int, int]] = {}
    for center in centers:
        start = max(0, center - limit // 2)
        end = min(len(body), start + limit)
        start = max(0, end - limit)
        left_break = body.rfind("\n", max(0, start - 160), start)
        if left_break >= 0:
            start = left_break + 1
        right_break = body.find("\n", end, min(len(body), end + 160))
        if right_break >= 0:
            end = right_break
        fragment = lowered[start:end]
        distinct = sum(term in fragment for term in terms)
        occurrences = sum(min(fragment.count(term), 3) for term in terms)
        candidates[(start, end)] = (distinct, occurrences, -start)
    selected: list[tuple[int, int]] = []
    for (start, end), _score in sorted(
        candidates.items(),
        key=lambda item: (-item[1][0], -item[1][1], item[0][0]),
    ):
        if any(max(start, old_start) < min(end, old_end) for old_start, old_end in selected):
            continue
        selected.append((start, end))
        if len(selected) >= count:
            break
    snippets = []
    for start, end in sorted(selected):
        text = body[start:end]
        snippets.append(
            {"start": start, "end": end, "text": text, "text_sha256": _sha256_text(text)}
        )
    return snippets


def _snapshot_parameters(snapshot: Any) -> dict[str, str]:
    core = snapshot.index.get("core")
    tree = core.get("tree_sha256") if isinstance(core, Mapping) else None
    if not isinstance(tree, str) or not re.fullmatch(r"[0-9a-f]{64}", tree):
        raise SnapshotError("snapshot is missing its validated core tree hash")
    if not isinstance(snapshot.index_sha256, str):
        raise SnapshotError("snapshot is missing its validated retrieval index hash")
    return {"core_tree_sha256": tree, "index_sha256": snapshot.index_sha256}


def _validate_retrieval_parameters(value: Any) -> dict[str, Any]:
    row = _closed(value, RETRIEVAL_KEYS, label="retrieval parameters")
    if row["mode"] != RETRIEVAL_MODE:
        raise SnapshotError(f"retrieval mode must be {RETRIEVAL_MODE}")
    return {
        "mode": RETRIEVAL_MODE,
        "full_top_k": _bounded_int(row["full_top_k"], label="full-top-k", minimum=1, maximum=50),
        "per_facet_top_k": _bounded_int(
            row["per_facet_top_k"], label="per-facet-top-k", minimum=1, maximum=20
        ),
        "max_facets": _bounded_int(row["max_facets"], label="max-facets", minimum=1, maximum=12),
        "max_supports": _bounded_int(
            row["max_supports"], label="max-supports", minimum=1, maximum=24
        ),
        "protected_full": _bounded_int(
            row["protected_full"], label="protected-full", minimum=0, maximum=12
        ),
        "snippet_chars": _bounded_int(
            row["snippet_chars"], label="snippet-chars", minimum=300, maximum=2400
        ),
        "snippets_per_support": _bounded_int(
            row["snippets_per_support"], label="snippets-per-support", minimum=1, maximum=4
        ),
    }


def build_pack(
    snapshot: Any,
    *,
    question_id: str,
    question: str,
    retrieval: Mapping[str, Any],
    search: Callable[..., dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Run unchanged family retrieval and construct one compact, hash-bound support pack."""

    if not isinstance(question_id, str) or not QUESTION_ID.fullmatch(question_id):
        raise SnapshotError("question-id must match qNNN")
    if not isinstance(question, str) or not question.strip():
        raise SnapshotError("question must be nonempty")
    question = " ".join(question.split())
    settings = _validate_retrieval_parameters(retrieval)
    search = search_snapshot if search is None else search
    facets = derive_facets(question, settings["max_facets"])
    snapshot_parameters = _snapshot_parameters(snapshot)
    parameters = {
        "algorithm": ALGORITHM,
        "family": FAMILY,
        "question_id": question_id,
        "question": question,
        "retrieval": settings,
        "snapshot": snapshot_parameters,
    }
    parameters_sha256 = _sha256_text(_canonical(parameters))
    records = _ledger(snapshot)
    candidates: dict[tuple[str, str], dict[str, Any]] = {}

    def add_results(query: str, top_k: int, facet_index: int | None) -> None:
        response = search(snapshot, query, RETRIEVAL_MODE, top_k)
        if response.get("status") != "pass" or response.get("effective_mode") != RETRIEVAL_MODE:
            raise SnapshotError("family retrieval did not return the requested passing mode")
        results = response.get("results")
        if not isinstance(results, list):
            raise SnapshotError("family retrieval returned an invalid result list")
        for ordinal, raw in enumerate(results, start=1):
            if not isinstance(raw, Mapping) or raw.get("rank") != ordinal:
                raise SnapshotError("family retrieval returned unstable result ranks")
            evidence, body = _parent_projection(raw, records)
            identity = (evidence["source_id"], evidence["record_id"])
            candidate = candidates.get(identity)
            if candidate is None:
                candidate = {
                    "evidence": evidence,
                    "body": body,
                    "full_rank": None,
                    "facet_ranks": {},
                }
                candidates[identity] = candidate
            elif candidate["evidence"] != evidence or candidate["body"] != body:
                raise SnapshotError("one source-record identity resolved inconsistently")
            if facet_index is None:
                candidate["full_rank"] = ordinal
            else:
                candidate["facet_ranks"][facet_index] = ordinal

    add_results(question, settings["full_top_k"], None)
    for facet_index, facet in enumerate(facets):
        add_results(facet, settings["per_facet_top_k"], facet_index)

    selected: list[tuple[str, str]] = []
    full_order = sorted(
        (
            (candidate["full_rank"], identity)
            for identity, candidate in candidates.items()
            if candidate["full_rank"] is not None
        ),
        key=lambda item: (item[0], item[1]),
    )
    for _rank, identity in full_order[: min(settings["protected_full"], settings["max_supports"])]:
        selected.append(identity)
    for facet_index in range(len(facets)):
        narrow_facet = len(_terms(facets[facet_index])) == 1

        def facet_priority(item: tuple[int, tuple[str, str]]) -> tuple[Any, ...]:
            rank, identity = item
            source_path = str(candidates[identity]["evidence"]["source_path"]).casefold()
            canonical_tier = 0
            if narrow_facet:
                if "/guides/" in source_path:
                    canonical_tier = 0
                elif "/reference/errors/" in source_path:
                    canonical_tier = 2
                else:
                    canonical_tier = 1
            return canonical_tier, rank, identity

        choices = sorted(
            (
                (candidate["facet_ranks"][facet_index], identity)
                for identity, candidate in candidates.items()
                if facet_index in candidate["facet_ranks"] and identity not in selected
            ),
            key=facet_priority,
        )
        if choices and len(selected) < settings["max_supports"]:
            selected.append(choices[0][1])
    if len(selected) < settings["max_supports"]:
        remaining = []
        for identity, candidate in candidates.items():
            if identity in selected:
                continue
            score = 0.0
            if candidate["full_rank"] is not None:
                score += 2.0 / (60 + candidate["full_rank"])
            score += sum(1.0 / (60 + rank) for rank in candidate["facet_ranks"].values())
            remaining.append((-score, identity))
        for _negative_score, identity in sorted(remaining):
            if len(selected) >= settings["max_supports"]:
                break
            selected.append(identity)

    supports: list[dict[str, Any]] = []
    for identity in selected:
        candidate = candidates[identity]
        matched_facets = sorted(candidate["facet_ranks"])
        snippet_query = " ".join([question, *(facets[index] for index in matched_facets)])
        snippets = _snippet_windows(
            candidate["body"],
            snippet_query,
            settings["snippet_chars"],
            settings["snippets_per_support"],
        )
        support_seed = {
            "parameters_sha256": parameters_sha256,
            "evidence": candidate["evidence"],
            "snippets": [row["text_sha256"] for row in snippets],
        }
        support_id = "support-" + _sha256_text(_canonical(support_seed))[:24]
        evidence = candidate["evidence"]
        supports.append(
            {
                "support_id": support_id,
                "source_id": evidence["source_id"],
                "record_id": evidence["record_id"],
                "concept_path": evidence["concept_path"],
                "source_path": evidence["source_path"],
                "record_sha256": evidence["record_sha256"],
                "locator": evidence["locator"],
                "text_sha256": evidence["text_sha256"],
                "full_rank": candidate["full_rank"],
                "facet_ranks": [
                    {"facet": index, "rank": candidate["facet_ranks"][index]}
                    for index in matched_facets
                ],
                "snippets": snippets,
            }
        )
    return {
        "schema_version": SCHEMA_VERSION,
        "parameters": parameters,
        "parameters_sha256": parameters_sha256,
        "facets": facets,
        "supports": supports,
    }


def _validate_pack_shape(value: Any) -> Mapping[str, Any]:
    pack = _closed(value, PACK_KEYS, label="support pack")
    if pack["schema_version"] != SCHEMA_VERSION:
        raise SnapshotError("support pack schema version is unsupported")
    parameters = _closed(pack["parameters"], PARAMETER_KEYS, label="support pack parameters")
    if parameters["algorithm"] != ALGORITHM or parameters["family"] != FAMILY:
        raise SnapshotError("support pack algorithm or family does not match this skill")
    if not isinstance(pack["parameters_sha256"], str):
        raise SnapshotError("support pack parameter hash is invalid")
    if _sha256_text(_canonical(parameters)) != pack["parameters_sha256"]:
        raise SnapshotError("support pack parameter hash mismatch")
    _validate_retrieval_parameters(parameters["retrieval"])
    if not isinstance(pack["facets"], list) or not all(isinstance(row, str) for row in pack["facets"]):
        raise SnapshotError("support pack facets are invalid")
    if not isinstance(pack["supports"], list):
        raise SnapshotError("support pack supports are invalid")
    seen: set[str] = set()
    identities: set[tuple[str, str]] = set()
    for index, raw in enumerate(pack["supports"]):
        support = _closed(raw, SUPPORT_KEYS, label=f"support {index}")
        support_id = support["support_id"]
        if not isinstance(support_id, str) or support_id in seen:
            raise SnapshotError("support IDs must be unique strings")
        seen.add(support_id)
        identity = (str(support["source_id"]), str(support["record_id"]))
        if identity in identities:
            raise SnapshotError("support identities must be exact source-record unique")
        identities.add(identity)
        if not isinstance(support["snippets"], list) or not support["snippets"]:
            raise SnapshotError("each support must contain compact snippets")
        for snippet in support["snippets"]:
            _closed(snippet, SNIPPET_KEYS, label=f"support {index} snippet")
    return pack


def _rederive_pack(snapshot: Any, supplied: Mapping[str, Any]) -> dict[str, Any]:
    parameters = supplied["parameters"]
    if parameters["snapshot"] != _snapshot_parameters(snapshot):
        raise SnapshotError("support pack snapshot parameter mismatch")
    expected = build_pack(
        snapshot,
        question_id=parameters["question_id"],
        question=parameters["question"],
        retrieval=parameters["retrieval"],
    )
    if _canonical(expected) != _canonical(supplied):
        raise SnapshotError("support pack is unknown, stale, or tampered")
    return expected


def compile_answer(pack: Mapping[str, Any], draft_value: Any) -> dict[str, Any]:
    """Compile selected hash-bound supports into strict first-use evidence order."""

    draft = _closed(draft_value, DRAFT_KEYS, label="answer draft")
    parameters = pack["parameters"]
    if draft["question_id"] != parameters["question_id"]:
        raise SnapshotError("answer draft question-id parameter mismatch")
    if draft["parameters_sha256"] != pack["parameters_sha256"]:
        raise SnapshotError("answer draft support-pack parameter mismatch")
    summary = draft["summary"]
    if not isinstance(summary, str) or not summary.strip() or len(summary.split()) > 450:
        raise SnapshotError("answer summary must contain 1 through 450 words")
    claims = draft["claims"]
    if not isinstance(claims, list) or not 1 <= len(claims) <= 64:
        raise SnapshotError("answer draft must contain 1 through 64 claims")
    supports = {row["support_id"]: row for row in pack["supports"]}
    first_use: list[str] = []
    compiled_claims: list[dict[str, Any]] = []
    for index, raw in enumerate(claims):
        claim = _closed(raw, CLAIM_KEYS, label=f"answer claim {index}")
        statement, support_ids = claim["statement"], claim["support_ids"]
        if not isinstance(statement, str) or not statement.strip():
            raise SnapshotError(f"answer claim {index} has an empty statement")
        if (
            not isinstance(support_ids, list)
            or not support_ids
            or not all(isinstance(item, str) for item in support_ids)
            or len(support_ids) != len(set(support_ids))
        ):
            raise SnapshotError(f"answer claim {index} support IDs must be a nonempty unique list")
        for support_id in support_ids:
            if support_id not in supports:
                raise SnapshotError(f"answer claim {index} references an unknown support ID")
            if support_id not in first_use:
                first_use.append(support_id)
        compiled_claims.append(
            {
                "statement": statement.strip(),
                "evidence_indices": [first_use.index(support_id) for support_id in support_ids],
            }
        )
    evidence = [
        {key: supports[support_id][key] for key in EVIDENCE_KEYS}
        for support_id in first_use
    ]
    referenced = {
        evidence_index
        for claim in compiled_claims
        for evidence_index in claim["evidence_indices"]
    }
    if referenced != set(range(len(evidence))):
        raise SnapshotError("compiled answer contains unused evidence")
    return {
        "question_id": parameters["question_id"],
        "answer": {"summary": summary.strip(), "claims": compiled_claims},
        "evidence": evidence,
    }


def _default_retrieval(args: argparse.Namespace) -> dict[str, Any]:
    return {
        "mode": RETRIEVAL_MODE,
        "full_top_k": args.full_top_k,
        "per_facet_top_k": args.per_facet_top_k,
        "max_facets": args.max_facets,
        "max_supports": args.max_supports,
        "protected_full": args.protected_full,
        "snippet_chars": args.snippet_chars,
        "snippets_per_support": args.snippets_per_support,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle", type=Path, help="Published Semantic OKF bundle")
    commands = parser.add_subparsers(dest="command", required=True)
    prepare = commands.add_parser("prepare", help="emit a compact, bounded support pack")
    prepare.add_argument("--question-id", required=True)
    prepare.add_argument("--question", required=True)
    prepare.add_argument("--full-top-k", type=int, default=12)
    prepare.add_argument("--per-facet-top-k", type=int, default=10)
    prepare.add_argument("--max-facets", type=int, default=8)
    prepare.add_argument("--max-supports", type=int, default=10)
    prepare.add_argument("--protected-full", type=int, default=3)
    prepare.add_argument("--snippet-chars", type=int, default=1200)
    prepare.add_argument("--snippets-per-support", type=int, default=2)
    finalize = commands.add_parser(
        "finalize", help="rederive a support pack and emit contract-ready JSON"
    )
    finalize.add_argument("--pack", required=True, type=Path)
    finalize.add_argument("--draft", required=True, help="external JSON path, or - for standard input")
    return parser


def main(argv: list[str] | None = None) -> int:
    _configure_utf8()
    args = build_parser().parse_args(argv)
    try:
        snapshot = load_snapshot(args.bundle)
        if args.command == "prepare":
            output = build_pack(
                snapshot,
                question_id=args.question_id,
                question=args.question,
                retrieval=_default_retrieval(args),
            )
        else:
            supplied = _validate_pack_shape(_read_json(args.pack, label="support pack"))
            pack = _rederive_pack(snapshot, supplied)
            draft_payload = (
                sys.stdin.read()
                if args.draft == "-"
                else Path(args.draft).read_text(encoding="utf-8")
            )
            draft = strict_json(draft_payload, label="answer draft")
            output = compile_answer(pack, draft)
    except (SnapshotError, OSError, UnicodeError, ValueError, TypeError, KeyError, IndexError) as exc:
        print(
            json.dumps(
                {"status": "error", "code": f"harbor-{FAMILY}-answer-error", "error": str(exc)},
                ensure_ascii=False,
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 2
    print(json.dumps(output, ensure_ascii=False, separators=(",", ":"), allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
