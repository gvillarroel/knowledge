#!/usr/bin/env python3
"""Query an embedded Ensemble quality snapshot with a trace-BM25 union."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
import sys
from typing import Any, Sequence


sys.dont_write_bytecode = True
SCRIPT_ROOT = Path(__file__).resolve().parent
if str(SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPT_ROOT))

import query_expert_knowledge_ensemble_quality as quality_runtime  # noqa: E402
import query_expert_knowledge_trace_bm25 as trace_runtime  # noqa: E402
from _ensemble_snapshot import SnapshotError  # noqa: E402


ROUTE_NAME = "specialized_expert_ensemble_quality_trace"
RETRIEVAL_CONTRACT_ID = "ensemble-quality-trace-union-rrf-v3"
QUALITY_WEIGHT = 9.0
TRACE_WEIGHT = 5.0
RRF_K = 0
CANDIDATE_BUDGET = 10
PAPER_ID_RE = re.compile(r"(?<!\d)(\d{4}\.\d{4,5})(v\d+)(?!\w)", re.IGNORECASE)


class ExpertQueryError(ValueError):
    """Describe an invalid expert binding or fusion request."""


def _paper_id(row: dict[str, Any]) -> str:
    direct = row.get("paper_id")
    if isinstance(direct, str) and direct:
        return direct
    for key in (
        "source_id",
        "record_id",
        "concept_id",
        "concept_path",
        "source_path",
        "title",
    ):
        value = row.get(key)
        if not isinstance(value, str):
            continue
        match = PAPER_ID_RE.search(value)
        if match:
            return f"{match.group(1)}{match.group(2).lower()}"
    raise ExpertQueryError("Retrieved evidence lacks an authoritative paper identity")


def _support_paths(artifacts: dict[str, Any]) -> set[str]:
    support = artifacts.get("query_support")
    if not isinstance(support, list) or not support:
        raise ExpertQueryError("Fusion adapter support bindings are absent")
    paths: set[str] = set()
    for index, binding in enumerate(support):
        quality_runtime._verify_artifact(  # noqa: SLF001
            binding,
            label=f"query_support[{index}]",
        )
        raw_path = binding.get("path")
        if not isinstance(raw_path, str) or raw_path in paths:
            raise ExpertQueryError("Invalid or duplicate query-support path")
        paths.add(raw_path)
    return paths


def verify() -> dict[str, Any]:
    """Verify embedded knowledge and the complete two-route adapter."""

    manifest = quality_runtime._load_manifest()  # noqa: SLF001
    if manifest.get("schema_version") != quality_runtime.MANIFEST_SCHEMA:
        raise ExpertQueryError("Unsupported expert manifest schema")
    knowledge = manifest.get("knowledge")
    artifacts = manifest.get("artifacts")
    if not isinstance(knowledge, dict) or not isinstance(artifacts, dict):
        raise ExpertQueryError("Expert manifest lacks required bindings")
    expected_tree = knowledge.get("tree")
    if not isinstance(expected_tree, dict):
        raise ExpertQueryError("Expert manifest lacks a tree binding")
    tree_sha256, file_count = quality_runtime._tree_binding(  # noqa: SLF001
        quality_runtime.KNOWLEDGE_ROOT
    )
    if tree_sha256 != expected_tree.get("sha256"):
        raise ExpertQueryError("Embedded knowledge tree digest drift")
    if file_count != expected_tree.get("file_count"):
        raise ExpertQueryError("Embedded knowledge file count drift")

    for key in (
        "skill_md",
        "guidance",
        "query_script",
        "agents_metadata",
    ):
        quality_runtime._verify_artifact(artifacts.get(key), label=key)  # noqa: SLF001

    expected_support = {
        "scripts/_adaptive_snapshot.py",
        "scripts/_embedding_snapshot.py",
        "scripts/_ensemble_snapshot.py",
        "scripts/_entity_graph_model.py",
        "scripts/_entity_graph_snapshot.py",
        "scripts/query_expert_knowledge_ensemble_quality.py",
        "scripts/query_expert_knowledge_trace_bm25.py",
        "scripts/requirements-embeddings.txt",
    }
    if _support_paths(artifacts) != expected_support:
        raise ExpertQueryError("Fusion adapter support set drift")
    return {
        "status": "pass",
        "skill_name": manifest.get("skill_name"),
        "knowledge_tree_sha256": tree_sha256,
        "knowledge_file_count": file_count,
        "record_count": knowledge.get("record_count"),
        "retrieval": retrieval_contract(),
    }


def retrieval_contract() -> dict[str, Any]:
    """Describe the frozen quality-plus-trace fusion."""

    return {
        "id": RETRIEVAL_CONTRACT_ID,
        "route_name": ROUTE_NAME,
        "query_adapter": (
            "Form the union of the bundled Ensemble quality Top-10 and a "
            "full-question fielded-BM25 Top-10 over the same authoritative "
            "snapshot, then rerank the union with global 9:5 reciprocal-rank "
            "fusion and stable quality-first ties"
        ),
        "parameters": {
            "candidate_budget": CANDIDATE_BUDGET,
            "candidate_scope": "quality-top10-union-trace-top10",
            "quality_contract": quality_runtime.RETRIEVAL_CONTRACT_ID,
            "quality_weight": QUALITY_WEIGHT,
            "trace_contract": "trace-bm25-field-fusion-v1",
            "trace_weight": TRACE_WEIGHT,
            "rrf_k": RRF_K,
            "tie_break": [
                "fused_score_desc",
                "quality_rank_asc",
                "trace_rank_asc",
                "paper_id_asc",
            ],
        },
    }


def search(
    contains: str,
    *,
    source_id: str | None,
    concept_type: str | None,
    limit: int,
    show_content: bool,
) -> list[dict[str, Any]]:
    """Return the frozen quality/trace union ordering."""

    if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 1000:
        raise ExpertQueryError("--limit must be from 1 through 1000")
    quality_rows = quality_runtime.search(
        contains,
        source_id=source_id,
        concept_type=concept_type,
        limit=CANDIDATE_BUDGET,
        show_content=show_content,
    )
    trace_rows = trace_runtime.search(
        contains,
        source_id=source_id,
        concept_type=concept_type,
        limit=1000,
        show_content=show_content,
    )

    quality_by_paper: dict[str, dict[str, Any]] = {}
    quality_order: list[str] = []
    for row in quality_rows:
        paper_id = _paper_id(row)
        if paper_id not in quality_by_paper:
            quality_by_paper[paper_id] = row
            quality_order.append(paper_id)
        if len(quality_order) == CANDIDATE_BUDGET:
            break

    trace_by_paper: dict[str, dict[str, Any]] = {}
    trace_order: list[str] = []
    for row in trace_rows:
        paper_id = _paper_id(row)
        if paper_id not in trace_by_paper:
            trace_by_paper[paper_id] = row
            trace_order.append(paper_id)
        if len(trace_order) == CANDIDATE_BUDGET:
            break

    quality_ranks = {
        paper_id: rank
        for rank, paper_id in enumerate(quality_order, start=1)
    }
    trace_ranks = {
        paper_id: rank
        for rank, paper_id in enumerate(trace_order, start=1)
    }
    candidates = list(dict.fromkeys([*quality_order, *trace_order]))
    scores = {
        paper_id: (
            (
                QUALITY_WEIGHT / (RRF_K + quality_ranks[paper_id])
                if paper_id in quality_ranks
                else 0.0
            )
            + (
                TRACE_WEIGHT / (RRF_K + trace_ranks[paper_id])
                if paper_id in trace_ranks
                else 0.0
            )
        )
        for paper_id in candidates
    }
    selected = sorted(
        candidates,
        key=lambda paper_id: (
            -scores[paper_id],
            quality_ranks.get(paper_id, 1001),
            trace_ranks.get(paper_id, 1001),
            paper_id,
        ),
    )[:CANDIDATE_BUDGET]

    results: list[dict[str, Any]] = []
    for rank, paper_id in enumerate(selected, start=1):
        row = dict(
            quality_by_paper.get(paper_id)
            or trace_by_paper[paper_id]
        )
        row["paper_id"] = paper_id
        row["rank"] = rank
        row["score"] = round(scores[paper_id], 12)
        row["ensemble_quality_trace"] = {
            "quality_rank": quality_ranks.get(paper_id),
            "trace_rank": trace_ranks.get(paper_id),
            "quality_weight": QUALITY_WEIGHT,
            "trace_weight": TRACE_WEIGHT,
            "rrf_k": RRF_K,
        }
        results.append(row)
    return results[:limit]


def get_record(
    source_id: str,
    record_id: str,
    *,
    show_content: bool,
) -> dict[str, Any]:
    """Return one exact authoritative record identity."""

    return quality_runtime.get_record(
        source_id,
        record_id,
        show_content=show_content,
    )


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser."""

    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("verify", help="Verify every manifest binding")

    search_parser = subparsers.add_parser(
        "search",
        help="Search the quality/trace union",
    )
    search_parser.add_argument("--contains", required=True)
    search_parser.add_argument("--source-id")
    search_parser.add_argument("--type", dest="concept_type")
    search_parser.add_argument("--limit", type=int, default=10)
    search_parser.add_argument("--show-content", action="store_true")

    get_parser = subparsers.add_parser("get", help="Get one exact ledger record")
    get_parser.add_argument("--source-id", required=True)
    get_parser.add_argument("--record-id", required=True)
    get_parser.add_argument("--show-content", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Verify the expert and execute one read-only operation."""

    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(encoding="utf-8")
    args = build_parser().parse_args(argv)
    try:
        verification = verify()
        if args.command == "verify":
            payload: Any = verification
        elif args.command == "search":
            payload = {
                "verification": verification,
                "results": search(
                    args.contains,
                    source_id=args.source_id,
                    concept_type=args.concept_type,
                    limit=args.limit,
                    show_content=args.show_content,
                ),
            }
        else:
            payload = {
                "verification": verification,
                "result": get_record(
                    args.source_id,
                    args.record_id,
                    show_content=args.show_content,
                ),
            }
    except (
        OSError,
        ExpertQueryError,
        quality_runtime.ExpertQueryError,
        trace_runtime.ExpertQueryError,
        SnapshotError,
        UnicodeError,
        ValueError,
        TypeError,
        KeyError,
        IndexError,
    ) as exc:
        raise SystemExit(f"Expert query failed: {exc}") from exc
    print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
