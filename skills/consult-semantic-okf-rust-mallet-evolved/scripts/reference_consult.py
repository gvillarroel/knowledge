#!/usr/bin/env python3
"""Search compact references and finalize exact Semantic OKF answers."""

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


class ReferenceConsultError(RuntimeError):
    """Describe an invalid compact consultation operation."""


def _configure_utf8() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(encoding="utf-8")


def _bounded_int(value: str, minimum: int, maximum: int) -> int:
    parsed = int(value)
    if not minimum <= parsed <= maximum:
        raise argparse.ArgumentTypeError(
            f"expected an integer from {minimum} through {maximum}"
        )
    return parsed


def _automatic_queries(query: str) -> list[str]:
    lowered = query.casefold()
    expansions: list[str] = []
    if any(term in lowered for term in ("diffusion", "pagerank", "ranking")):
        expansions.append(
            "personalized pagerank spreading activation query-linked seeds "
            "node specificity"
        )
    if "path" in lowered:
        expansions.append(
            "relational paths flow-based pruning reliability resource propagation"
        )
    if "subgraph" in lowered:
        expansions.append(
            "prize-collecting steiner connected subgraph query relevance prizes "
            "edge cost"
        )
    if any(term in lowered for term in ("adaptive", "traversal", "agentic")):
        expansions.append(
            "adaptive graph traversal bfs meta-path shortest paths query "
            "decomposition iterative reflection"
        )
    if any(
        term in lowered
        for term in ("parametric", "intrinsic", "external knowledge")
    ):
        expansions.extend(
            [
                "external parametric complementary reasoning filtering logits "
                "integration relevance",
                "fresh domain-specific structured relational evidence external memory",
                "irrelevant noisy retrieval suppress useful intrinsic reasoning filtering",
                "graph quality evidence sufficiency domain risk grounding",
            ]
        )
    return expansions


def _queries(query: str, focuses: list[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for raw in [query, *_automatic_queries(query), *focuses]:
        normalized = " ".join(raw.split())
        key = normalized.casefold()
        if normalized and key not in seen and len(result) < 5:
            result.append(normalized)
            seen.add(key)
    if not result:
        raise ReferenceConsultError("query must be nonempty")
    return result


def _interpretation(text: str, preview_chars: int) -> str:
    marker = "- **interpretation**:"
    for line in text.splitlines():
        if line.casefold().startswith(marker):
            value = line[len(marker) :].strip()
            if value:
                return value[:preview_chars]
    return " ".join(text.split())[:preview_chars]


def _search(args: argparse.Namespace) -> dict[str, Any]:
    queries = _queries(args.query, args.focus)
    snapshot = load_snapshot(args.bundle, deep_validation=False)
    accumulated: dict[str, dict[str, Any]] = {}
    for query_index, query in enumerate(queries):
        response = search_snapshot(
            snapshot,
            query,
            "bm25",
            args.depth,
            concept_types=("Paper Semantic Claim",),
        )
        weight = 2.0 if query_index == 0 else 1.0
        for hit in response["results"]:
            reference_id = hit["reference_id"]
            row = accumulated.setdefault(
                reference_id,
                {
                    "hit": hit,
                    "score": 0.0,
                    "matched_queries": set(),
                    "query_ranks": {},
                    "best_rank": hit["rank"],
                },
            )
            row["score"] += weight / (20.0 + hit["rank"])
            row["matched_queries"].add(query_index)
            row["query_ranks"].setdefault(query_index, hit["rank"])
            row["best_rank"] = min(row["best_rank"], hit["rank"])
    ranked = sorted(
        accumulated.values(),
        key=lambda row: (
            -len(row["matched_queries"]),
            -row["score"],
            row["best_rank"],
            row["hit"]["reference_id"],
        ),
    )
    by_source: dict[str, list[dict[str, Any]]] = defaultdict(list)
    source_order: list[str] = []
    for row in ranked:
        hit = row["hit"]
        identity = hit.get("paper_id") or hit["source_id"]
        if identity not in by_source:
            source_order.append(identity)
        by_source[identity].append(row)
    source_order = source_order[: args.max_sources]
    selected: list[dict[str, Any]] = []
    depth = 0
    while len(selected) < args.max_results:
        added = False
        for identity in source_order:
            rows = by_source[identity]
            if depth < min(len(rows), args.per_source):
                selected.append(rows[depth])
                added = True
                if len(selected) >= args.max_results:
                    break
        if not added:
            break
        depth += 1
    def source_identity(row: dict[str, Any]) -> str:
        hit = row["hit"]
        return hit.get("paper_id") or hit["source_id"]

    def compact_row(row: dict[str, Any], index: int) -> dict[str, Any]:
        hit = row["hit"]
        return {
            "result_index": index,
            "reference_id": hit["reference_id"],
            "source_identity": source_identity(row),
            "matched_queries": sorted(row["matched_queries"]),
            "interpretation": _interpretation(hit["text"], args.preview_chars),
        }

    recommended_rows: list[dict[str, Any]] = []
    recommended_sources: set[str] = set()
    recommendation_target = min(args.minimum_sources + 2, args.max_sources)

    def recommend(candidates: list[dict[str, Any]]) -> None:
        for candidate in candidates:
            identity = source_identity(candidate)
            if identity in recommended_sources:
                continue
            recommended_rows.append(candidate)
            recommended_sources.add(identity)
            return

    structural = any(
        term in args.query.casefold()
        for term in ("diffusion", "path", "subgraph", "adaptive", "traversal")
    )
    if structural:
        for query_index in range(1, len(queries)):
            candidates = sorted(
                (
                    row
                    for row in accumulated.values()
                    if query_index in row["query_ranks"]
                ),
                key=lambda row: (
                    row["query_ranks"][query_index],
                    -row["score"],
                    row["hit"]["reference_id"],
                ),
            )
            recommend(candidates)
            if len(recommended_rows) >= recommendation_target:
                break
    else:
        for row in ranked:
            if 0 in row["matched_queries"]:
                recommend([row])
            if len(recommended_rows) >= recommendation_target:
                break
    for row in ranked:
        if len(recommended_rows) >= recommendation_target:
            break
        recommend([row])
    if len(recommended_rows) < args.minimum_sources:
        raise ReferenceConsultError(
            f"retrieval found {len(recommended_rows)} recommended sources; "
            f"{args.minimum_sources} required"
        )
    results = [compact_row(row, index) for index, row in enumerate(selected)]
    recommended = [
        {
            "reference_id": row["hit"]["reference_id"],
            "source_identity": source_identity(row),
            "matched_queries": sorted(row["matched_queries"]),
            "interpretation": _interpretation(
                row["hit"]["text"], args.preview_chars
            ),
        }
        for row in recommended_rows
    ]
    return {
        "status": "pass",
        "read_only_snapshot": True,
        "minimum_sources": args.minimum_sources,
        "recommended": recommended,
        "queries": [
            {"index": index, "text": query}
            for index, query in enumerate(queries)
        ],
        "returned": len(results),
        "distinct_sources": len({row["source_identity"] for row in results}),
        "results": results,
    }


def _reference_map(snapshot: Any) -> dict[str, dict[str, Any]]:
    return {
        entry["reference_id"]: entry
        for entry in snapshot.references_by_document.values()
    }


def _unique_references(values: list[str]) -> list[str]:
    if not values:
        raise ReferenceConsultError("at least one reference ID is required")
    if any(not isinstance(value, str) or not value for value in values):
        raise ReferenceConsultError("reference IDs must be nonempty strings")
    return list(dict.fromkeys(values))


def _show(args: argparse.Namespace) -> dict[str, Any]:
    snapshot = load_snapshot(args.bundle, deep_validation=False)
    by_reference = _reference_map(snapshot)
    documents = {row["document_id"]: row for row in snapshot.documents}
    references = _unique_references(args.reference_id)
    unknown = [value for value in references if value not in by_reference]
    if unknown:
        raise ReferenceConsultError(f"unknown reference IDs: {unknown}")
    return {
        "status": "pass",
        "selected": [
            {
                "reference_id": reference_id,
                "source_identity": documents[
                    by_reference[reference_id]["document_id"]
                ].get("paper_id")
                or documents[by_reference[reference_id]["document_id"]][
                    "source_id"
                ],
                "text": documents[by_reference[reference_id]["document_id"]]["text"],
            }
            for reference_id in references
        ],
    }


def _strict_load(path: Path, label: str) -> dict[str, Any]:
    def reject_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ReferenceConsultError(f"{label} contains duplicate key {key!r}")
            result[key] = value
        return result

    try:
        value = json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=reject_duplicates,
            parse_constant=lambda raw: (_ for _ in ()).throw(
                ReferenceConsultError(f"{label} contains non-standard number {raw}")
            ),
        )
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ReferenceConsultError(f"cannot read {label}: {exc}") from exc
    if not isinstance(value, dict):
        raise ReferenceConsultError(f"{label} must be a JSON object")
    return value


def _atomic_write(path: Path, value: Any, snapshot_root: Path) -> None:
    target = path.expanduser().resolve()
    if target.is_relative_to(snapshot_root.resolve()):
        raise ReferenceConsultError("answer output cannot be written in the snapshot")
    if target.exists() and (target.is_symlink() or not target.is_file()):
        raise ReferenceConsultError(f"unsafe output path: {target}")
    target.parent.mkdir(parents=True, exist_ok=True)
    candidate = target.parent / f".{target.name}.candidate-{uuid.uuid4().hex}"
    try:
        candidate.write_text(
            json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        os.replace(candidate, target)
    finally:
        if candidate.exists():
            candidate.unlink()


def _finalize(args: argparse.Namespace) -> dict[str, Any]:
    draft = _strict_load(args.draft, "answer draft")
    snapshot = load_snapshot(args.bundle, deep_validation=False)
    by_reference = _reference_map(snapshot)
    if set(draft) != {"question_id", "summary", "claims"}:
        raise ReferenceConsultError(
            "draft must contain exactly question_id, summary, and claims"
        )
    question_id = draft["question_id"]
    summary = draft["summary"]
    claims = draft["claims"]
    if not isinstance(question_id, str) or not question_id:
        raise ReferenceConsultError("question_id must be nonempty")
    if not isinstance(summary, str) or not summary.strip():
        raise ReferenceConsultError("summary must be nonempty")
    if len(summary.split()) > 450:
        raise ReferenceConsultError("summary exceeds 450 words")
    if not isinstance(claims, list) or not claims:
        raise ReferenceConsultError("claims must be a nonempty array")
    first_use: list[str] = []
    normalized_claims: list[tuple[str, list[str]]] = []
    for claim_number, claim in enumerate(claims):
        if not isinstance(claim, dict) or set(claim) != {
            "statement",
            "reference_ids",
        }:
            raise ReferenceConsultError(
                f"claim {claim_number} must contain statement and reference_ids"
            )
        statement = claim["statement"]
        raw_references = claim["reference_ids"]
        if not isinstance(statement, str) or not statement.strip():
            raise ReferenceConsultError(f"claim {claim_number} statement is empty")
        if not isinstance(raw_references, list):
            raise ReferenceConsultError(
                f"claim {claim_number} reference_ids must be an array"
            )
        references = _unique_references(raw_references)
        for reference_id in references:
            if reference_id not in by_reference:
                raise ReferenceConsultError(f"unknown reference ID {reference_id}")
            if reference_id not in first_use:
                first_use.append(reference_id)
        normalized_claims.append((statement, references))
    identities = {
        by_reference[reference_id]["document_id"] for reference_id in first_use
    }
    if (
        len(first_use) < args.minimum_sources
        or len(first_use) > args.minimum_sources + 2
        or len(identities) != len(first_use)
    ):
        raise ReferenceConsultError(
            f"answer must use {args.minimum_sources} through "
            f"{args.minimum_sources + 2} references from the same count of "
            "independent sources"
        )
    positions = {
        reference_id: index for index, reference_id in enumerate(first_use)
    }
    answer = {
        "question_id": question_id,
        "answer": {
            "summary": summary,
            "claims": [
                {
                    "statement": statement,
                    "evidence_indices": [
                        positions[reference_id] for reference_id in references
                    ],
                }
                for statement, references in normalized_claims
            ],
        },
        # Keep exact identity materialization outside the model boundary. The
        # verifier resolves these immutable IDs through the snapshot dictionary
        # before applying the legacy seven-field evidence checks.
        "evidence": [
            {"reference_id": reference_id} for reference_id in first_use
        ],
    }
    if args.output is not None:
        _atomic_write(args.output, answer, snapshot.root)
    return answer


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    search = commands.add_parser("search")
    search.add_argument("bundle", type=Path)
    search.add_argument("--query", required=True)
    search.add_argument("--focus", action="append", default=[])
    search.add_argument(
        "--minimum-sources",
        type=lambda value: _bounded_int(value, 1, 20),
        required=True,
    )
    search.add_argument(
        "--depth", type=lambda value: _bounded_int(value, 20, 100), default=60
    )
    search.add_argument(
        "--max-results", type=lambda value: _bounded_int(value, 4, 30), default=18
    )
    search.add_argument(
        "--max-sources", type=lambda value: _bounded_int(value, 4, 20), default=10
    )
    search.add_argument(
        "--per-source", type=lambda value: _bounded_int(value, 1, 3), default=2
    )
    search.add_argument(
        "--preview-chars",
        type=lambda value: _bounded_int(value, 120, 800),
        default=360,
    )
    show = commands.add_parser("show")
    show.add_argument("bundle", type=Path)
    show.add_argument("--reference-id", action="append", required=True)
    finalize = commands.add_parser("finalize")
    finalize.add_argument("bundle", type=Path)
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
        if args.command == "search":
            result = _search(args)
        elif args.command == "show":
            result = _show(args)
        else:
            result = _finalize(args)
    except (
        ReferenceConsultError,
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
                {"status": "error", "code": "reference-consult-error", "error": str(exc)},
                ensure_ascii=False,
                sort_keys=True,
            )
        )
        return 2
    if args.command == "finalize":
        print(
            json.dumps(
                result,
                ensure_ascii=False,
                separators=(",", ":"),
                allow_nan=False,
            )
        )
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
