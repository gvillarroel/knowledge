#!/usr/bin/env python3
"""Verify and query an embedded Semantic OKF ensemble with its quality policy."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import sys
from typing import Any, Iterator, Sequence


sys.dont_write_bytecode = True
SCRIPT_ROOT = Path(__file__).resolve().parent
if str(SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPT_ROOT))

from _ensemble_snapshot import (  # noqa: E402
    EnsembleSnapshot,
    SnapshotError,
    load_snapshot,
    search_snapshot,
)


SKILL_ROOT = SCRIPT_ROOT.parent
MANIFEST_PATH = SKILL_ROOT / "expert-manifest.json"
KNOWLEDGE_ROOT = SKILL_ROOT / "references" / "knowledge"
LEDGER_PATH = KNOWLEDGE_ROOT / "semantic" / "records.jsonl"
MANIFEST_SCHEMA = "semantic-okf-expert-skill/1.0"
ROUTE_NAME = "specialized_expert_ensemble_quality"
RETRIEVAL_CONTRACT_ID = "ensemble-quality-protected-multisignal-v1"
INTERNAL_CANDIDATE_BUDGET = 10
_SNAPSHOT: EnsembleSnapshot | None = None


class ExpertQueryError(ValueError):
    """Describe an invalid expert binding or query."""


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _tree_binding(root: Path) -> tuple[str, int]:
    if not root.is_dir():
        raise ExpertQueryError(f"Embedded knowledge is absent: {root}")
    paths: list[Path] = []
    for path in root.rglob("*"):
        if path.is_symlink():
            raise ExpertQueryError(f"Embedded knowledge contains a symlink: {path}")
        if path.is_file():
            paths.append(path)
    digest = hashlib.sha256()
    for path in sorted(paths, key=lambda item: item.relative_to(root).as_posix()):
        relative = path.relative_to(root).as_posix().encode("utf-8")
        data = path.read_bytes()
        digest.update(relative)
        digest.update(b"\0")
        digest.update(str(len(data)).encode("ascii"))
        digest.update(b"\0")
        digest.update(data)
        digest.update(b"\0")
    return digest.hexdigest(), len(paths)


def _load_manifest() -> dict[str, Any]:
    try:
        payload = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ExpertQueryError(f"Cannot read expert manifest: {exc}") from exc
    if not isinstance(payload, dict):
        raise ExpertQueryError("Expert manifest must be a JSON object")
    return payload


def _safe_artifact_path(raw: Any, *, label: str) -> Path:
    if not isinstance(raw, str):
        raise ExpertQueryError(f"Invalid artifact path: {label}")
    relative = PurePosixPath(raw)
    if (
        relative.is_absolute()
        or not relative.parts
        or ".." in relative.parts
        or "\\" in raw
    ):
        raise ExpertQueryError(f"Unsafe artifact path: {raw}")
    path = SKILL_ROOT.joinpath(*relative.parts)
    try:
        path.resolve().relative_to(SKILL_ROOT.resolve())
    except ValueError as exc:
        raise ExpertQueryError(f"Artifact escapes the skill: {raw}") from exc
    return path


def _verify_artifact(binding: Any, *, label: str) -> None:
    if not isinstance(binding, dict):
        raise ExpertQueryError(f"Missing artifact binding: {label}")
    path = _safe_artifact_path(binding.get("path"), label=label)
    if (
        not path.is_file()
        or path.is_symlink()
        or _sha256_file(path) != binding.get("sha256")
    ):
        raise ExpertQueryError(f"Artifact digest drift: {label}")


def verify() -> dict[str, Any]:
    """Verify the complete embedded knowledge and every bound adapter file."""

    manifest = _load_manifest()
    if manifest.get("schema_version") != MANIFEST_SCHEMA:
        raise ExpertQueryError("Unsupported expert manifest schema")
    knowledge = manifest.get("knowledge")
    artifacts = manifest.get("artifacts")
    if not isinstance(knowledge, dict) or not isinstance(artifacts, dict):
        raise ExpertQueryError("Expert manifest lacks required bindings")
    expected_tree = knowledge.get("tree")
    if not isinstance(expected_tree, dict):
        raise ExpertQueryError("Expert manifest lacks a tree binding")
    tree_sha256, file_count = _tree_binding(KNOWLEDGE_ROOT)
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
        _verify_artifact(artifacts.get(key), label=key)

    support = artifacts.get("query_support")
    if not isinstance(support, list) or not support:
        raise ExpertQueryError("Ensemble adapter support bindings are absent")
    support_paths: set[str] = set()
    for index, binding in enumerate(support):
        _verify_artifact(binding, label=f"query_support[{index}]")
        raw_path = binding["path"]
        if raw_path in support_paths:
            raise ExpertQueryError(f"Duplicate query support path: {raw_path}")
        support_paths.add(raw_path)
    required_support = {
        "scripts/_adaptive_snapshot.py",
        "scripts/_embedding_snapshot.py",
        "scripts/_ensemble_snapshot.py",
        "scripts/_entity_graph_model.py",
        "scripts/_entity_graph_snapshot.py",
        "scripts/requirements-embeddings.txt",
    }
    if support_paths != required_support:
        raise ExpertQueryError("Ensemble adapter support set drift")
    return {
        "status": "pass",
        "skill_name": manifest.get("skill_name"),
        "knowledge_tree_sha256": tree_sha256,
        "knowledge_file_count": file_count,
        "record_count": knowledge.get("record_count"),
        "retrieval": retrieval_contract(),
    }


def retrieval_contract() -> dict[str, Any]:
    """Describe the frozen expert retrieval contract."""

    return {
        "id": RETRIEVAL_CONTRACT_ID,
        "route_name": ROUTE_NAME,
        "query_adapter": (
            "Protect the adaptive paper set, then apply the bundled Ensemble "
            "quality policy over adaptive, entity-graph fusion, BM25, and the "
            "exact pinned embedding-hybrid route with its consensus promotion gate"
        ),
        "parameters": {
            "policy": "quality",
            "algorithm": "protected-multisignal-paper-rerank-v2",
            "routes": [
                "adaptive",
                "graph_fusion",
                "bm25",
                "embedding_hybrid",
            ],
            "weights": [4, 1, 5, 1],
            "rrf_k": 7,
            "candidate_budget": INTERNAL_CANDIDATE_BUDGET,
            "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
            "embedding_revision": (
                "1110a243fdf4706b3f48f1d95db1a4f5529b4d41"
            ),
        },
    }


def _snapshot() -> EnsembleSnapshot:
    global _SNAPSHOT
    if _SNAPSHOT is None:
        os.environ.setdefault("HF_HUB_OFFLINE", "1")
        os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
        _SNAPSHOT = load_snapshot(KNOWLEDGE_ROOT, deep_validation=False)
    return _SNAPSHOT


def _records() -> Iterator[dict[str, Any]]:
    try:
        lines = LEDGER_PATH.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        raise ExpertQueryError(f"Cannot read embedded record ledger: {exc}") from exc
    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ExpertQueryError(
                f"Invalid ledger JSON on line {line_number}: {exc}"
            ) from exc
        if not isinstance(record, dict):
            raise ExpertQueryError(f"Ledger line {line_number} is not an object")
        yield record


def _safe_concept_path(record: dict[str, Any]) -> str:
    raw = record.get("concept_path")
    if not isinstance(raw, str):
        raise ExpertQueryError("Ledger record lacks concept_path")
    relative = PurePosixPath(raw)
    if relative.is_absolute() or ".." in relative.parts or "\\" in raw:
        raise ExpertQueryError(f"Unsafe concept_path: {raw}")
    target = KNOWLEDGE_ROOT.joinpath(*relative.parts)
    if not target.is_file():
        raise ExpertQueryError(f"Concept is absent: {raw}")
    return raw


def _project_record(
    record: dict[str, Any],
    *,
    show_content: bool,
) -> dict[str, Any]:
    result = {
        "source_id": record.get("source_id"),
        "record_id": record.get("record_id"),
        "title": record.get("title"),
        "concept_type": record.get("concept_type"),
        "concept_id": record.get("concept_id"),
        "concept_path": _safe_concept_path(record),
        "record_sha256": record.get("record_sha256"),
        "source_path": record.get("source_path"),
    }
    if show_content:
        body = record.get("body")
        result["body"] = body
        if isinstance(body, str):
            result["text"] = body
            result["text_sha256"] = hashlib.sha256(
                body.encode("utf-8")
            ).hexdigest()
            result["locator"] = {"kind": "record"}
    return result


def search(
    contains: str,
    *,
    source_id: str | None,
    concept_type: str | None,
    limit: int,
    show_content: bool,
) -> list[dict[str, Any]]:
    """Return the quality-policy ordering over exact protected evidence."""

    if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 1000:
        raise ExpertQueryError("--limit must be from 1 through 1000")
    payload = search_snapshot(
        _snapshot(),
        contains,
        "quality",
        INTERNAL_CANDIDATE_BUDGET,
        source_ids=([source_id] if source_id is not None else ()),
        concept_types=([concept_type] if concept_type is not None else ()),
    )
    raw_results = payload.get("results")
    if not isinstance(raw_results, list):
        raise ExpertQueryError("Ensemble quality search returned no results array")
    results: list[dict[str, Any]] = []
    for raw in raw_results[:limit]:
        if not isinstance(raw, dict):
            raise ExpertQueryError("Ensemble quality search returned a non-object hit")
        row = dict(raw)
        if not show_content:
            row.pop("text", None)
            row.pop("text_sha256", None)
        results.append(row)
    return results


def get_record(
    source_id: str,
    record_id: str,
    *,
    show_content: bool,
) -> dict[str, Any]:
    """Return one exact authoritative record identity."""

    for record in _records():
        if record.get("source_id") == source_id and record.get("record_id") == record_id:
            return _project_record(record, show_content=show_content)
    raise ExpertQueryError(f"Record is absent: ({source_id!r}, {record_id!r})")


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser."""

    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("verify", help="Verify every manifest binding")

    search_parser = subparsers.add_parser(
        "search",
        help="Search with the embedded Ensemble quality policy",
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
