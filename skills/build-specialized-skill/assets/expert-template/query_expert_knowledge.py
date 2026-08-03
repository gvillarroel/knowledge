#!/usr/bin/env python3
"""Verify and search the immutable knowledge embedded in an expert skill."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sys
from typing import Any, Iterator, Sequence


SKILL_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = SKILL_ROOT / "expert-manifest.json"
KNOWLEDGE_ROOT = SKILL_ROOT / "references" / "knowledge"
LEDGER_PATH = KNOWLEDGE_ROOT / "semantic" / "records.jsonl"


class ExpertQueryError(ValueError):
    """Raised when the expert binding or query is invalid."""


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


def verify() -> dict[str, Any]:
    """Verify the complete embedded knowledge and bound expert artifacts."""

    manifest = _load_manifest()
    if manifest.get("schema_version") != "semantic-okf-expert-skill/1.0":
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

    for key, fallback in (
        ("skill_md", "SKILL.md"),
        ("guidance", "references/guidance.md"),
        ("query_script", "scripts/query_expert_knowledge.py"),
        ("agents_metadata", "agents/openai.yaml"),
    ):
        binding = artifacts.get(key)
        if not isinstance(binding, dict):
            raise ExpertQueryError(f"Missing artifact binding: {key}")
        raw_path = binding.get("path", fallback)
        if not isinstance(raw_path, str):
            raise ExpertQueryError(f"Invalid artifact path: {key}")
        relative = PurePosixPath(raw_path)
        if relative.is_absolute() or ".." in relative.parts or "\\" in raw_path:
            raise ExpertQueryError(f"Unsafe artifact path: {raw_path}")
        path = SKILL_ROOT.joinpath(*relative.parts)
        if not path.is_file() or _sha256_file(path) != binding.get("sha256"):
            raise ExpertQueryError(f"Artifact digest drift: {key}")
    return {
        "status": "pass",
        "skill_name": manifest.get("skill_name"),
        "knowledge_tree_sha256": tree_sha256,
        "knowledge_file_count": file_count,
        "record_count": knowledge.get("record_count"),
    }


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


def _project(record: dict[str, Any], *, show_content: bool, score: int | None) -> dict[str, Any]:
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
    if score is not None:
        result["score"] = score
    if show_content:
        body = record.get("body")
        result["body"] = body
        if isinstance(body, str):
            result["text"] = body
            result["text_sha256"] = hashlib.sha256(body.encode("utf-8")).hexdigest()
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
    """Return stable lexical matches from the authoritative record ledger."""

    tokens = tuple(dict.fromkeys(re.findall(r"[\w-]+", contains.casefold())))
    if not tokens:
        raise ExpertQueryError("--contains must include at least one search token")
    matches: list[tuple[int, str, str, dict[str, Any]]] = []
    for record in _records():
        if source_id is not None and record.get("source_id") != source_id:
            continue
        if concept_type is not None and record.get("concept_type") != concept_type:
            continue
        haystack = " ".join(
            str(record.get(key, ""))
            for key in ("title", "body", "source_id", "record_id", "concept_type")
        ).casefold()
        score = sum(haystack.count(token) for token in tokens)
        if score:
            matches.append(
                (
                    -score,
                    str(record.get("source_id", "")),
                    str(record.get("record_id", "")),
                    record,
                )
            )
    matches.sort(key=lambda item: item[:3])
    return [
        _project(record, show_content=show_content, score=-negative_score)
        for negative_score, _, _, record in matches[:limit]
    ]


def get_record(
    source_id: str,
    record_id: str,
    *,
    show_content: bool,
) -> dict[str, Any]:
    """Return one exact authoritative record identity."""

    for record in _records():
        if record.get("source_id") == source_id and record.get("record_id") == record_id:
            return _project(record, show_content=show_content, score=None)
    raise ExpertQueryError(f"Record is absent: ({source_id!r}, {record_id!r})")


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser."""

    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("verify", help="Verify every manifest binding")

    search_parser = subparsers.add_parser("search", help="Search the embedded ledger")
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
    """Verify the expert and run one read-only operation."""

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
            if args.limit < 1:
                raise ExpertQueryError("--limit must be positive")
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
    except (OSError, ExpertQueryError) as exc:
        raise SystemExit(f"Expert query failed: {exc}") from exc
    print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
