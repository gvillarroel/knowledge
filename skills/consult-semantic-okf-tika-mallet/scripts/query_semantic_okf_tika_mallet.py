#!/usr/bin/env python3
"""Inspect or search a Tika/MALLET Semantic OKF snapshot read-only."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
from pathlib import Path

from _tika_mallet_snapshot import (
    SCHEMA_VERSION,
    SnapshotError,
    inspect_snapshot,
    load_snapshot,
    search_snapshot,
)

EVIDENCE_IDENTITY_FIELDS = (
    "source_id",
    "record_id",
    "concept_path",
    "source_path",
    "record_sha256",
    "locator",
    "text_sha256",
)
EXCERPT_TOKEN_RE = re.compile(r"[a-z0-9]+", re.ASCII | re.IGNORECASE)
DEFAULT_EXCERPT_CHARS = 1800
ANSWER_PACK_EXCERPT_CHARS = 1200
ANSWER_PACK_SCHEMA_VERSION = "semantic-okf-tika-mallet-answer-pack/1.0"
DRAFT_TOP_LEVEL_KEYS = ("question_id", "summary", "claims")
DRAFT_CLAIM_KEYS = ("statement", "support_ids")
ANSWER_TOP_LEVEL_KEYS = ("question_id", "answer", "evidence")
ANSWER_KEYS = ("summary", "claims")
CLAIM_KEYS = ("statement", "evidence_indices")


def _configure_utf8() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(encoding="utf-8")


def _add_search_arguments(
    parser: argparse.ArgumentParser,
    *,
    repeated_queries: bool,
) -> None:
    """Add the shared closed search arguments to one subcommand."""

    parser.add_argument(
        "--query",
        action="append" if repeated_queries else None,
        required=True,
        help=(
            "Query text; repeat this option for batch-search"
            if repeated_queries
            else "Query text"
        ),
    )
    parser.add_argument(
        "--mode", choices=("bm25", "topic", "association", "fusion"), default="fusion"
    )
    parser.add_argument("--top-k", type=int, default=10)
    parser.add_argument("--source-id", action="append", default=[])
    parser.add_argument("--concept-id", action="append", default=[])
    parser.add_argument("--concept-type", action="append", default=[])
    parser.add_argument(
        "--evidence-only",
        action="store_true",
        help=(
            "omit diagnostic expansions and scores while retaining a query-focused "
            "exact text excerpt plus identities, hashes, paths, and locators"
        ),
    )
    parser.add_argument(
        "--excerpt-chars",
        type=int,
        default=DEFAULT_EXCERPT_CHARS,
        help=(
            "maximum exact excerpt characters per hit with --evidence-only "
            f"(default: {DEFAULT_EXCERPT_CHARS})"
        ),
    )


def _excerpt(text: str, query: str, limit: int) -> tuple[str, int, int]:
    """Select one deterministic query-dense exact substring."""

    if len(text) <= limit:
        return text, 0, len(text)
    folded = text.casefold()
    terms = sorted(
        {
            token.casefold()
            for token in EXCERPT_TOKEN_RE.findall(query)
            if len(token) >= 3
        },
        key=lambda token: (-len(token), token),
    )
    anchors = {0}
    for term in terms:
        offset = 0
        for _ in range(20):
            found = folded.find(term, offset)
            if found < 0:
                break
            anchors.add(found)
            offset = found + max(1, len(term))
    candidates: list[tuple[int, int, int]] = []
    for anchor in anchors:
        start = max(0, anchor - limit // 3)
        end = min(len(text), start + limit)
        start = max(0, end - limit)
        window = folded[start:end]
        coverage = sum(term in window for term in terms)
        candidates.append((-coverage, start, end))
    _, start, end = min(candidates)
    return text[start:end], start, end


def _evidence_view(
    result: dict[str, object],
    excerpt_chars: int,
) -> dict[str, object]:
    """Return a compact lossless-for-grounding view of one search result."""

    rows = result["results"]
    if not isinstance(rows, list):
        raise SnapshotError("search result rows are malformed")
    compact_rows = []
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("text"), str):
            raise SnapshotError("search result evidence text is malformed")
        excerpt, start, end = _excerpt(
            row["text"],
            str(result["query"]),
            excerpt_chars,
        )
        compact_rows.append(
            {
                "rank": row["rank"],
                "evidence": {
                    field: row[field]
                    for field in EVIDENCE_IDENTITY_FIELDS
                },
                "text_chars": len(row["text"]),
                "text_excerpt_start": start,
                "text_excerpt_end": end,
                "text_excerpt": excerpt,
            }
        )
    return {
        "schema_version": result["schema_version"],
        "status": result["status"],
        "authoritative": result["authoritative"],
        "discovery_only": result["discovery_only"],
        "query": result["query"],
        "requested_mode": result["requested_mode"],
        "effective_mode": result["effective_mode"],
        "top_k": result["top_k"],
        "returned": result["returned"],
        "filters": result["filters"],
        "snapshot": result["snapshot"],
        "result_view": "exact-evidence-excerpt",
        "excerpt_chars": excerpt_chars,
        "results": compact_rows,
    }


def _reject_duplicate_members(pairs: list[tuple[str, object]]) -> dict[str, object]:
    """Build one JSON object while rejecting duplicate member names."""

    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate member {key!r}")
        result[key] = value
    return result


def _validate_answer(snapshot: object, answer_path: Path) -> dict[str, object]:
    """Validate one response contract and every exact retrieval identity."""

    try:
        value = json.loads(
            answer_path.read_text(encoding="utf-8"),
            object_pairs_hook=_reject_duplicate_members,
            parse_constant=lambda token: (_ for _ in ()).throw(
                ValueError(f"non-standard number {token!r}")
            ),
        )
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        raise SnapshotError(f"answer JSON is invalid: {exc}") from exc
    if not isinstance(value, dict) or tuple(value) != ANSWER_TOP_LEVEL_KEYS:
        raise SnapshotError(
            "answer must contain question_id, answer, and evidence in that order"
        )
    question_id = value["question_id"]
    evidence = value["evidence"]
    answer = value["answer"]
    if not isinstance(question_id, str) or not question_id.strip():
        raise SnapshotError("answer question_id must be a nonempty string")
    if not isinstance(evidence, list):
        raise SnapshotError("answer evidence must be an array")
    if answer is None:
        if evidence:
            raise SnapshotError("a null answer must use an empty evidence array")
        return {
            "schema_version": SCHEMA_VERSION,
            "status": "pass",
            "question_id": question_id,
            "non_null_answer": False,
            "evidence_count": 0,
            "distinct_source_count": 0,
        }
    if not isinstance(answer, dict) or tuple(answer) != ANSWER_KEYS:
        raise SnapshotError("non-null answer must contain summary and claims in order")
    summary, claims = answer["summary"], answer["claims"]
    if (
        not isinstance(summary, str)
        or not summary.strip()
        or not 1 <= len(summary.split()) <= 450
    ):
        raise SnapshotError("answer summary must contain 1 through 450 words")
    if not isinstance(claims, list) or not claims:
        raise SnapshotError("answer claims must be a nonempty array")
    first_use: list[int] = []
    seen_indices: set[int] = set()
    for claim in claims:
        if not isinstance(claim, dict) or tuple(claim) != CLAIM_KEYS:
            raise SnapshotError(
                "each claim must contain statement and evidence_indices in order"
            )
        statement, indices = claim["statement"], claim["evidence_indices"]
        if not isinstance(statement, str) or not statement.strip():
            raise SnapshotError("each claim statement must be nonempty")
        if (
            not isinstance(indices, list)
            or not indices
            or any(
                isinstance(index, bool)
                or not isinstance(index, int)
                or not 0 <= index < len(evidence)
                for index in indices
            )
        ):
            raise SnapshotError("claim evidence indices are invalid")
        for index in indices:
            if index not in seen_indices:
                seen_indices.add(index)
                first_use.append(index)
    if first_use != list(range(len(evidence))):
        raise SnapshotError(
            "evidence rows are not in complete first-use order"
        )
    documents = getattr(snapshot, "documents", ())
    valid_evidence = {
        json.dumps(
            {
                field: document[field]
                for field in EVIDENCE_IDENTITY_FIELDS
            },
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        for document in documents
    }
    serialized_rows: list[str] = []
    for index, row in enumerate(evidence):
        if not isinstance(row, dict) or set(row) != set(EVIDENCE_IDENTITY_FIELDS):
            raise SnapshotError(
                f"evidence row {index} does not have the exact grounding fields"
            )
        serialized = json.dumps(
            row,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        if serialized not in valid_evidence:
            raise SnapshotError(
                f"evidence row {index} is not an exact validated consultation hit"
            )
        serialized_rows.append(serialized)
    if len(serialized_rows) != len(set(serialized_rows)):
        raise SnapshotError("answer evidence rows must be distinct")
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "pass",
        "question_id": question_id,
        "non_null_answer": True,
        "claim_count": len(claims),
        "evidence_count": len(evidence),
        "distinct_source_count": len(
            {str(row["source_id"]) for row in evidence}
        ),
        "first_use_order": True,
        "exact_evidence": True,
    }


def _answer_pack(
    searches: list[dict[str, object]],
    *,
    excerpt_chars: int,
    max_sources: int,
) -> dict[str, object]:
    """Fuse several compact searches into one bounded source-diverse support pack."""

    candidates: dict[str, dict[str, object]] = {}
    for query_index, search in enumerate(searches):
        compact = _evidence_view(search, excerpt_chars)
        query = compact["query"]
        rows = compact["results"]
        if not isinstance(query, str) or not isinstance(rows, list):
            raise SnapshotError("compact search result is malformed")
        for row in rows:
            if not isinstance(row, dict) or not isinstance(row.get("evidence"), dict):
                raise SnapshotError("compact evidence row is malformed")
            serialized = json.dumps(
                row["evidence"],
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
                allow_nan=False,
            )
            rank = row.get("rank")
            if isinstance(rank, bool) or not isinstance(rank, int) or rank < 1:
                raise SnapshotError("compact evidence rank is invalid")
            candidate = candidates.setdefault(
                serialized,
                {
                    "row": row,
                    "queries": [],
                    "reciprocal_rank": 0.0,
                    "best_rank": rank,
                    "best_query_index": query_index,
                },
            )
            queries = candidate["queries"]
            if not isinstance(queries, list):
                raise SnapshotError("answer-pack query accumulator is malformed")
            if query not in queries:
                queries.append(query)
                candidate["reciprocal_rank"] = float(
                    candidate["reciprocal_rank"]
                ) + 1.0 / (60.0 + rank)
            if (rank, query_index) < (
                int(candidate["best_rank"]),
                int(candidate["best_query_index"]),
            ):
                candidate["row"] = row
                candidate["best_rank"] = rank
                candidate["best_query_index"] = query_index

    by_source: dict[str, list[tuple[str, dict[str, object]]]] = {}
    for serialized, candidate in candidates.items():
        row = candidate["row"]
        if not isinstance(row, dict) or not isinstance(row.get("evidence"), dict):
            raise SnapshotError("answer-pack candidate is malformed")
        source_id = row["evidence"].get("source_id")
        if not isinstance(source_id, str) or not source_id:
            raise SnapshotError("answer-pack source identity is malformed")
        by_source.setdefault(source_id, []).append((serialized, candidate))

    selected: list[tuple[str, dict[str, object]]] = []
    for rows in by_source.values():
        selected.append(
            min(
                rows,
                key=lambda item: (
                    -len(item[1]["queries"]),
                    -float(item[1]["reciprocal_rank"]),
                    int(item[1]["best_rank"]),
                    int(item[1]["best_query_index"]),
                    item[0],
                ),
            )
        )
    selected.sort(
        key=lambda item: (
            -len(item[1]["queries"]),
            -float(item[1]["reciprocal_rank"]),
            int(item[1]["best_rank"]),
            int(item[1]["best_query_index"]),
            item[0],
        )
    )
    selected = selected[:max_sources]
    results: list[dict[str, object]] = []
    for index, (_serialized, candidate) in enumerate(selected, start=1):
        row = candidate["row"]
        if not isinstance(row, dict):
            raise SnapshotError("answer-pack selected row is malformed")
        results.append(
            {
                "support_id": f"s{index:02d}",
                "matched_queries": candidate["queries"],
                "best_rank": candidate["best_rank"],
                "evidence": row["evidence"],
                "text_chars": row["text_chars"],
                "text_excerpt_start": row["text_excerpt_start"],
                "text_excerpt_end": row["text_excerpt_end"],
                "text_excerpt": row["text_excerpt"],
            }
        )
    return {
        "schema_version": ANSWER_PACK_SCHEMA_VERSION,
        "status": "pass",
        "authoritative": False,
        "discovery_only": True,
        "query_count": len(searches),
        "source_count": len(results),
        "max_sources": max_sources,
        "excerpt_chars": excerpt_chars,
        "results": results,
    }


def _load_strict_json(path: Path, label: str) -> dict[str, object]:
    """Load one closed JSON object while rejecting duplicate members."""

    try:
        value = json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=_reject_duplicate_members,
            parse_constant=lambda token: (_ for _ in ()).throw(
                ValueError(f"non-standard number {token!r}")
            ),
        )
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        raise SnapshotError(f"{label} JSON is invalid: {exc}") from exc
    if not isinstance(value, dict):
        raise SnapshotError(f"{label} must contain one JSON object")
    return value


def _checked_external_output(bundle: Path, output: Path) -> Path:
    """Require a new regular output outside the immutable snapshot."""

    if output.exists() or output.is_symlink():
        raise SnapshotError(f"refusing to overwrite output: {output}")
    parent = output.parent.resolve()
    if not parent.is_dir() or parent.is_symlink():
        raise SnapshotError(f"output parent is absent or linked: {output.parent}")
    resolved = parent / output.name
    try:
        resolved.relative_to(bundle.resolve())
    except ValueError:
        pass
    else:
        raise SnapshotError("derived output cannot be written inside the bundle")
    return resolved


def _write_new_json(bundle: Path, output: Path, value: dict[str, object]) -> None:
    """Publish one deterministic JSON artifact with no-replace semantics."""

    checked = _checked_external_output(bundle, output)
    payload = (
        json.dumps(
            value,
            ensure_ascii=False,
            indent=2,
            sort_keys=False,
            allow_nan=False,
        )
        + "\n"
    )
    try:
        with checked.open("x", encoding="utf-8", newline="\n") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
    except FileExistsError as exc:
        raise SnapshotError(f"refusing to overwrite output: {output}") from exc


def _finalize_answer(
    snapshot: object,
    *,
    bundle: Path,
    pack_path: Path,
    draft_path: Path,
    output_path: Path,
) -> dict[str, object]:
    """Compile support IDs into exact evidence rows and validate the final answer."""

    pack = _load_strict_json(pack_path, "answer pack")
    if (
        pack.get("schema_version") != ANSWER_PACK_SCHEMA_VERSION
        or pack.get("status") != "pass"
        or not isinstance(pack.get("results"), list)
    ):
        raise SnapshotError("answer pack contract is invalid")
    supports: dict[str, dict[str, object]] = {}
    for row in pack["results"]:
        if (
            not isinstance(row, dict)
            or not isinstance(row.get("support_id"), str)
            or not isinstance(row.get("evidence"), dict)
            or row["support_id"] in supports
        ):
            raise SnapshotError("answer pack contains an invalid support row")
        supports[row["support_id"]] = row
    if not supports:
        raise SnapshotError("answer pack contains no supports")

    draft = _load_strict_json(draft_path, "answer draft")
    if tuple(draft) != DRAFT_TOP_LEVEL_KEYS:
        raise SnapshotError(
            "answer draft must contain question_id, summary, and claims in order"
        )
    question_id, summary, draft_claims = (
        draft["question_id"],
        draft["summary"],
        draft["claims"],
    )
    if (
        not isinstance(question_id, str)
        or not question_id.strip()
        or not isinstance(summary, str)
        or not isinstance(draft_claims, list)
        or not draft_claims
    ):
        raise SnapshotError("answer draft identity, summary, or claims are invalid")

    evidence: list[dict[str, object]] = []
    evidence_indices: dict[str, int] = {}
    claims: list[dict[str, object]] = []
    for claim in draft_claims:
        if not isinstance(claim, dict) or tuple(claim) != DRAFT_CLAIM_KEYS:
            raise SnapshotError(
                "each draft claim must contain statement and support_ids in order"
            )
        statement, support_ids = claim["statement"], claim["support_ids"]
        if (
            not isinstance(statement, str)
            or not statement.strip()
            or not isinstance(support_ids, list)
            or not support_ids
            or len(support_ids) != len(set(support_ids))
            or any(
                not isinstance(support_id, str) or support_id not in supports
                for support_id in support_ids
            )
        ):
            raise SnapshotError("draft claim statement or support IDs are invalid")
        indices: list[int] = []
        for support_id in support_ids:
            if support_id not in evidence_indices:
                evidence_indices[support_id] = len(evidence)
                support = supports[support_id]
                evidence.append(dict(support["evidence"]))
            indices.append(evidence_indices[support_id])
        claims.append({"statement": statement, "evidence_indices": indices})
    answer = {
        "question_id": question_id,
        "answer": {"summary": summary, "claims": claims},
        "evidence": evidence,
    }

    checked_output = _checked_external_output(bundle, output_path)
    checked_output.parent.mkdir(parents=False, exist_ok=True)
    temporary_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="\n",
            prefix=f".{checked_output.name}.",
            suffix=".tmp",
            dir=checked_output.parent,
            delete=False,
        ) as handle:
            json.dump(
                answer,
                handle,
                ensure_ascii=False,
                indent=2,
                sort_keys=False,
                allow_nan=False,
            )
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
            temporary_name = handle.name
        validation = _validate_answer(snapshot, Path(temporary_name))
        _write_new_json(bundle, checked_output, answer)
    finally:
        if temporary_name is not None:
            Path(temporary_name).unlink(missing_ok=True)
    return {
        **validation,
        "output": str(checked_output),
        "support_count": len(evidence),
    }


def build_parser() -> argparse.ArgumentParser:
    """Build the read-only Tika/MALLET consultation parser."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "bundle", type=Path, help="Published Tika/MALLET Semantic OKF bundle"
    )
    commands = parser.add_subparsers(dest="command", required=True)
    inspect = commands.add_parser(
        "inspect", help="Validate and describe the Tika/MALLET projection"
    )
    inspect.add_argument(
        "--deep-validation",
        action="store_true",
        help=(
            "independently rederive BM25 and PPMI artifacts and retrain the "
            "fixed-seed one-thread Java MALLET model"
        ),
    )
    inspect.add_argument(
        "--java",
        type=Path,
        help="Java 17+ executable required with --deep-validation",
    )
    inspect.add_argument(
        "--mallet-home",
        type=Path,
        help="MALLET 2.1.0 binary directory required with --deep-validation",
    )
    search = commands.add_parser("search", help="Retrieve exact evidence passages")
    _add_search_arguments(search, repeated_queries=False)
    batch = commands.add_parser(
        "batch-search",
        help="Run several exact-evidence searches after validating the snapshot once",
    )
    _add_search_arguments(batch, repeated_queries=True)
    answer_pack = commands.add_parser(
        "answer-pack",
        help=(
            "Fuse several searches into one small source-diverse support pack "
            "for bounded answer drafting"
        ),
    )
    _add_search_arguments(answer_pack, repeated_queries=True)
    answer_pack.set_defaults(
        evidence_only=True,
        excerpt_chars=ANSWER_PACK_EXCERPT_CHARS,
        top_k=6,
    )
    answer_pack.add_argument(
        "--max-sources",
        type=int,
        default=10,
        help="maximum distinct source IDs in the support pack (default: 10)",
    )
    answer_pack.add_argument(
        "--output",
        type=Path,
        required=True,
        help="new answer-pack JSON path outside the immutable bundle",
    )
    validate_answer = commands.add_parser(
        "validate-answer",
        help="Validate a final JSON response and every copied evidence identity",
    )
    validate_answer.add_argument(
        "--answer",
        type=Path,
        required=True,
        help="Candidate response JSON outside the immutable bundle",
    )
    finalize_answer = commands.add_parser(
        "finalize-answer",
        help=(
            "Compile a small support-ID draft into exact first-use evidence and "
            "validate the final response"
        ),
    )
    finalize_answer.add_argument("--pack", type=Path, required=True)
    finalize_answer.add_argument("--draft", type=Path, required=True)
    finalize_answer.add_argument("--output", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    """Validate the supplied snapshot and execute one read-only operation."""

    _configure_utf8()
    args = build_parser().parse_args(argv)
    try:
        deep = bool(getattr(args, "deep_validation", False))
        java = getattr(args, "java", None)
        mallet_home = getattr(args, "mallet_home", None)
        if deep and (java is None or mallet_home is None):
            raise SnapshotError(
                "--deep-validation requires both --java and --mallet-home"
            )
        if not deep and (java is not None or mallet_home is not None):
            raise SnapshotError(
                "--java and --mallet-home are only accepted with --deep-validation"
            )
        if (
            getattr(args, "evidence_only", False)
            and (
                isinstance(args.excerpt_chars, bool)
                or not 256 <= args.excerpt_chars <= 8000
            )
        ):
            raise SnapshotError(
                "--excerpt-chars must be an integer from 256 through 8000"
            )
        snapshot = load_snapshot(
            args.bundle,
            deep_validation=deep,
            java=java,
            mallet_home=mallet_home,
        )
        if args.command == "inspect":
            result = inspect_snapshot(snapshot)
        elif args.command == "validate-answer":
            result = _validate_answer(snapshot, args.answer)
        elif args.command == "finalize-answer":
            result = _finalize_answer(
                snapshot,
                bundle=args.bundle,
                pack_path=args.pack,
                draft_path=args.draft,
                output_path=args.output,
            )
        elif args.command == "search":
            search_result = search_snapshot(
                snapshot,
                args.query,
                args.mode,
                args.top_k,
                source_ids=args.source_id,
                concept_ids=args.concept_id,
                concept_types=args.concept_type,
            )
            result = (
                _evidence_view(search_result, args.excerpt_chars)
                if args.evidence_only
                else search_result
            )
        else:
            queries = args.query
            if (
                not isinstance(queries, list)
                or not queries
                or len(queries) > 32
                or len(set(queries)) != len(queries)
            ):
                raise SnapshotError(
                    "batch-search requires 1 through 32 distinct --query values"
                )
            if args.command == "answer-pack" and not 2 <= len(queries) <= 6:
                raise SnapshotError(
                    "answer-pack requires 2 through 6 distinct --query values"
                )
            if (
                args.command == "answer-pack"
                and (
                    isinstance(args.max_sources, bool)
                    or not 4 <= args.max_sources <= 16
                    or isinstance(args.top_k, bool)
                    or not 1 <= args.top_k <= 8
                )
            ):
                raise SnapshotError(
                    "answer-pack requires --max-sources from 4 through 16 "
                    "and --top-k from 1 through 8"
                )
            searches = [
                search_snapshot(
                    snapshot,
                    query,
                    args.mode,
                    args.top_k,
                    source_ids=args.source_id,
                    concept_ids=args.concept_id,
                    concept_types=args.concept_type,
                )
                for query in queries
            ]
            if args.command == "answer-pack":
                result = _answer_pack(
                    searches,
                    excerpt_chars=args.excerpt_chars,
                    max_sources=args.max_sources,
                )
                _write_new_json(args.bundle, args.output, result)
                print(
                    json.dumps(
                        result,
                        ensure_ascii=False,
                        sort_keys=True,
                        allow_nan=False,
                    )
                )
                return 0
            if args.evidence_only:
                searches = [
                    _evidence_view(item, args.excerpt_chars)
                    for item in searches
                ]
            result = {
                "schema_version": SCHEMA_VERSION,
                "status": "pass",
                "authoritative": False,
                "discovery_only": True,
                "query_count": len(searches),
                "result_view": (
                    "exact-evidence-excerpt"
                    if args.evidence_only
                    else "diagnostic"
                ),
                "searches": searches,
            }
    except (
        SnapshotError,
        OSError,
        UnicodeError,
        ValueError,
        TypeError,
        KeyError,
        IndexError,
    ) as exc:
        print(
            json.dumps(
                {"status": "error", "code": "tika-mallet-error", "error": str(exc)},
                ensure_ascii=False,
                sort_keys=True,
            )
        )
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
