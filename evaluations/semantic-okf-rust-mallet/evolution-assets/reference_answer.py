#!/usr/bin/env python3
"""Prepare and finalize bounded answers through a snapshot reference dictionary."""

from __future__ import annotations

import argparse
import json
import os
import sys
import uuid
from collections import defaultdict
from pathlib import Path
from typing import Any

from _rust_mallet_snapshot import SnapshotError, load_snapshot, search_snapshot


PACK_SCHEMA = "semantic-okf-reference-answer-pack/1.0"
EVIDENCE_KEYS = (
    "source_id",
    "record_id",
    "concept_path",
    "source_path",
    "record_sha256",
    "locator",
    "text_sha256",
)


class AnswerWorkflowError(RuntimeError):
    """Describe an invalid bounded reference-answer operation."""


def _configure_utf8() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(encoding="utf-8")


def _strict_load(path: Path, label: str) -> dict[str, Any]:
    def reject_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise AnswerWorkflowError(f"{label} contains duplicate key {key!r}")
            result[key] = value
        return result

    try:
        value = json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=reject_duplicates,
            parse_constant=lambda raw: (_ for _ in ()).throw(
                AnswerWorkflowError(f"{label} contains non-standard number {raw}")
            ),
        )
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise AnswerWorkflowError(f"cannot read {label}: {exc}") from exc
    if not isinstance(value, dict):
        raise AnswerWorkflowError(f"{label} must be a JSON object")
    return value


def _atomic_write(path: Path, value: Any, *, forbidden_root: Path | None = None) -> None:
    target = path.expanduser().resolve()
    if forbidden_root is not None and target.is_relative_to(forbidden_root.resolve()):
        raise AnswerWorkflowError("temporary answer artifacts cannot be written in the snapshot")
    if target.exists() and (target.is_symlink() or not target.is_file()):
        raise AnswerWorkflowError(f"unsafe output path: {target}")
    target.parent.mkdir(parents=True, exist_ok=True)
    candidate = target.parent / f".{target.name}.candidate-{uuid.uuid4().hex}"
    try:
        candidate.write_text(
            json.dumps(
                value,
                ensure_ascii=False,
                indent=2,
                sort_keys=False,
                allow_nan=False,
            )
            + "\n",
            encoding="utf-8",
            newline="\n",
        )
        os.replace(candidate, target)
    finally:
        if candidate.exists():
            candidate.unlink()


def _bounded_int(value: str, minimum: int, maximum: int) -> int:
    parsed = int(value)
    if not minimum <= parsed <= maximum:
        raise argparse.ArgumentTypeError(
            f"expected an integer from {minimum} through {maximum}"
        )
    return parsed


def _queries(query: str, focuses: list[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for raw in [query, *focuses]:
        normalized = " ".join(raw.split())
        key = normalized.casefold()
        if normalized and key not in seen:
            result.append(normalized)
            seen.add(key)
    if not result:
        raise AnswerWorkflowError("query must be nonempty")
    if len(result) > 5:
        raise AnswerWorkflowError("use at most four distinct focus queries")
    return result


def _preview(pack: dict[str, Any], preview_chars: int) -> dict[str, Any]:
    if not 80 <= preview_chars <= 1000:
        raise AnswerWorkflowError("preview-chars must be from 80 through 1000")
    rows = []
    for row in pack["results"]:
        text = " ".join(row["text"].split())
        rows.append(
            {
                "pack_index": row["pack_index"],
                "reference_id": row["reference_id"],
                "source_identity": row["source_identity"],
                "matched_queries": row["matched_queries"],
                "preview": text[:preview_chars],
            }
        )
    return {
        "status": "pass",
        "source_coverage_met": pack["source_coverage_met"],
        "returned": len(rows),
        "results": rows,
    }


def _prepare(args: argparse.Namespace) -> dict[str, Any]:
    queries = _queries(args.query, args.focus)
    snapshot = load_snapshot(args.bundle, deep_validation=False)
    accumulated: dict[str, dict[str, Any]] = {}
    for query_index, query in enumerate(queries):
        response = search_snapshot(
            snapshot,
            query,
            "fusion",
            args.top_k_per_query,
            concept_types=("Paper Semantic Claim",),
        )
        weight = 3.0 if query_index == 0 else 1.0
        for hit in response["results"]:
            reference_id = hit["reference_id"]
            row = accumulated.setdefault(
                reference_id,
                {
                    "hit": hit,
                    "score": 0.0,
                    "matched_queries": [],
                    "best_rank": hit["rank"],
                },
            )
            row["score"] += weight / (20.0 + hit["rank"])
            row["matched_queries"].append(query_index)
            row["best_rank"] = min(row["best_rank"], hit["rank"])
    ranked = sorted(
        accumulated.values(),
        key=lambda row: (
            -row["score"],
            -len(row["matched_queries"]),
            row["best_rank"],
            row["hit"]["reference_id"],
        ),
    )
    by_identity: dict[str, list[dict[str, Any]]] = defaultdict(list)
    identity_order: list[str] = []
    for row in ranked:
        hit = row["hit"]
        identity = hit.get("paper_id") or hit["source_id"]
        if identity not in by_identity:
            identity_order.append(identity)
        by_identity[identity].append(row)
    selected = [by_identity[identity][0] for identity in identity_order]
    selected = selected[: args.max_results]
    if len(selected) < args.minimum_sources:
        raise AnswerWorkflowError(
            f"retrieval found {len(selected)} independent sources; "
            f"{args.minimum_sources} required"
        )
    selected.sort(
        key=lambda row: (
            -row["score"],
            row["best_rank"],
            row["hit"]["reference_id"],
        )
    )
    results = [
        {
            "pack_index": index,
            "reference_id": row["hit"]["reference_id"],
            "source_identity": row["hit"].get("paper_id")
            or row["hit"]["source_id"],
            "matched_queries": row["matched_queries"],
            "text": row["hit"]["text"],
        }
        for index, row in enumerate(selected)
    ]
    pack = {
        "schema_version": PACK_SCHEMA,
        "status": "pass",
        "read_only_snapshot": True,
        "reference_dictionary_sha256": snapshot.index["artifacts"]["references"][
            "sha256"
        ],
        "queries": [
            {"index": index, "text": query}
            for index, query in enumerate(queries)
        ],
        "minimum_sources": args.minimum_sources,
        "distinct_source_count": len(results),
        "source_coverage_met": len(results) >= args.minimum_sources,
        "results": results,
    }
    _atomic_write(args.output, pack, forbidden_root=snapshot.root)
    return _preview(pack, args.preview_chars)


def _load_pack(path: Path) -> dict[str, Any]:
    pack = _strict_load(path, "reference pack")
    if set(pack) != {
        "schema_version",
        "status",
        "read_only_snapshot",
        "reference_dictionary_sha256",
        "queries",
        "minimum_sources",
        "distinct_source_count",
        "source_coverage_met",
        "results",
    }:
        raise AnswerWorkflowError("reference pack root schema is invalid")
    if pack["schema_version"] != PACK_SCHEMA or pack["status"] != "pass":
        raise AnswerWorkflowError("reference pack version or status is invalid")
    results = pack["results"]
    if not isinstance(results, list) or not results:
        raise AnswerWorkflowError("reference pack results must be nonempty")
    if any(not isinstance(row, dict) for row in results):
        raise AnswerWorkflowError("reference pack results must be JSON objects")
    expected_indices = list(range(len(results)))
    if [row.get("pack_index") for row in results] != expected_indices:
        raise AnswerWorkflowError("reference pack indices are invalid")
    if any(
        set(row)
        != {"pack_index", "reference_id", "source_identity", "matched_queries", "text"}
        or not isinstance(row["reference_id"], str)
        or not isinstance(row["source_identity"], str)
        or not isinstance(row["text"], str)
        or not row["text"]
        for row in results
    ):
        raise AnswerWorkflowError("reference pack contains an invalid result")
    if len({row["reference_id"] for row in results}) != len(results):
        raise AnswerWorkflowError("reference pack contains duplicate references")
    return pack


def _selected_indices(values: list[int], results: list[dict[str, Any]]) -> list[int]:
    if not values:
        raise AnswerWorkflowError("at least one pack index is required")
    unique = list(dict.fromkeys(values))
    if any(index < 0 or index >= len(results) for index in unique):
        raise AnswerWorkflowError("pack index is out of range")
    return unique


def _show(pack: dict[str, Any], indices: list[int]) -> dict[str, Any]:
    results = pack["results"]
    return {
        "status": "pass",
        "selected": [
            {
                "pack_index": index,
                "reference_id": results[index]["reference_id"],
                "source_identity": results[index]["source_identity"],
                "text": results[index]["text"],
            }
            for index in _selected_indices(indices, results)
        ],
    }


def _finalize(args: argparse.Namespace) -> dict[str, Any]:
    pack = _load_pack(args.pack)
    draft = _strict_load(args.draft, "answer draft")
    snapshot = load_snapshot(args.bundle, deep_validation=False)
    dictionary_sha256 = snapshot.index["artifacts"]["references"]["sha256"]
    if pack["reference_dictionary_sha256"] != dictionary_sha256:
        raise AnswerWorkflowError("reference pack is stale for this snapshot")
    if set(draft) != {"question_id", "summary", "claims"}:
        raise AnswerWorkflowError(
            "draft must contain exactly question_id, summary, and claims"
        )
    question_id, summary, claims = (
        draft["question_id"],
        draft["summary"],
        draft["claims"],
    )
    if not isinstance(question_id, str) or not question_id:
        raise AnswerWorkflowError("question_id must be nonempty")
    if not isinstance(summary, str) or not summary.strip():
        raise AnswerWorkflowError("summary must be nonempty")
    if len(summary.split()) > 450:
        raise AnswerWorkflowError("summary exceeds 450 words")
    if not isinstance(claims, list) or not claims:
        raise AnswerWorkflowError("claims must be a nonempty array")
    results = pack["results"]
    first_use: list[int] = []
    normalized_claims: list[tuple[str, list[int]]] = []
    for claim_number, claim in enumerate(claims):
        if not isinstance(claim, dict) or set(claim) != {
            "statement",
            "pack_indices",
        }:
            raise AnswerWorkflowError(
                f"claim {claim_number} must contain exactly statement and pack_indices"
            )
        statement, raw_indices = claim["statement"], claim["pack_indices"]
        if not isinstance(statement, str) or not statement.strip():
            raise AnswerWorkflowError(f"claim {claim_number} statement is empty")
        if not isinstance(raw_indices, list) or any(
            isinstance(index, bool) or not isinstance(index, int)
            for index in raw_indices
        ):
            raise AnswerWorkflowError(
                f"claim {claim_number} pack_indices must be integers"
            )
        selected = _selected_indices(raw_indices, results)
        for index in selected:
            if index not in first_use:
                first_use.append(index)
        normalized_claims.append((statement, selected))
    identities = {results[index]["source_identity"] for index in first_use}
    if len(first_use) != args.minimum_sources or len(identities) != args.minimum_sources:
        raise AnswerWorkflowError(
            f"answer must use exactly {args.minimum_sources} references from "
            f"{args.minimum_sources} independent sources"
        )
    by_reference = {
        entry["reference_id"]: entry
        for entry in snapshot.references_by_document.values()
    }
    for row in results:
        entry = by_reference.get(row["reference_id"])
        if entry is None:
            raise AnswerWorkflowError(
                f"pack contains unknown reference {row['reference_id']}"
            )
    positions = {index: position for position, index in enumerate(first_use)}
    answer = {
        "question_id": question_id,
        "answer": {
            "summary": summary,
            "claims": [
                {
                    "statement": statement,
                    "evidence_indices": [positions[index] for index in indices],
                }
                for statement, indices in normalized_claims
            ],
        },
        "evidence": [
            {
                key: by_reference[results[index]["reference_id"]]["evidence"][key]
                for key in EVIDENCE_KEYS
            }
            for index in first_use
        ],
    }
    if args.output is not None:
        _atomic_write(args.output, answer, forbidden_root=snapshot.root)
    return answer


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    prepare = commands.add_parser("prepare")
    prepare.add_argument("bundle", type=Path)
    prepare.add_argument("--query", required=True)
    prepare.add_argument("--focus", action="append", default=[])
    prepare.add_argument(
        "--minimum-sources",
        type=lambda value: _bounded_int(value, 1, 20),
        required=True,
    )
    prepare.add_argument(
        "--top-k-per-query",
        type=lambda value: _bounded_int(value, 5, 100),
        default=30,
    )
    prepare.add_argument(
        "--max-results",
        type=lambda value: _bounded_int(value, 1, 24),
        default=12,
    )
    prepare.add_argument(
        "--preview-chars",
        type=lambda value: _bounded_int(value, 80, 1000),
        default=360,
    )
    prepare.add_argument("--output", type=Path, required=True)
    review = commands.add_parser("review")
    review.add_argument("pack", type=Path)
    review.add_argument(
        "--preview-chars",
        type=lambda value: _bounded_int(value, 80, 1000),
        default=360,
    )
    show = commands.add_parser("show")
    show.add_argument("pack", type=Path)
    show.add_argument("--index", action="append", type=int, required=True)
    finalize = commands.add_parser("finalize")
    finalize.add_argument("bundle", type=Path)
    finalize.add_argument("pack", type=Path)
    finalize.add_argument("draft", type=Path)
    finalize.add_argument(
        "--minimum-sources",
        type=lambda value: _bounded_int(value, 1, 20),
        required=True,
    )
    finalize.add_argument("--output", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    _configure_utf8()
    args = build_parser().parse_args(argv)
    try:
        if args.command == "prepare":
            result = _prepare(args)
        elif args.command == "review":
            result = _preview(_load_pack(args.pack), args.preview_chars)
        elif args.command == "show":
            result = _show(_load_pack(args.pack), args.index)
        else:
            result = _finalize(args)
    except (
        AnswerWorkflowError,
        SnapshotError,
        OSError,
        UnicodeError,
        ValueError,
        TypeError,
        KeyError,
        IndexError,
        json.JSONDecodeError,
    ) as exc:
        print(
            json.dumps(
                {"status": "error", "code": "reference-answer-error", "error": str(exc)},
                ensure_ascii=False,
                sort_keys=True,
            )
        )
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=False, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
