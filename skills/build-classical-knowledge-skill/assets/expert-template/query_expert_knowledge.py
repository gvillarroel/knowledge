#!/usr/bin/env python3
"""Verify and query the immutable classical knowledge embedded in this skill."""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sys
from typing import Any, Iterator, Mapping, Sequence

sys.dont_write_bytecode = True

from _classical_snapshot import (  # noqa: E402
    CONCEPT_LAYOUT_SOURCE_PACKED,
    STRUCTURED_SOURCE_KINDS,
    SnapshotError,
    inspect_snapshot,
    load_snapshot,
    search_snapshot,
)


SCHEMA_VERSION = "classical-knowledge-skill/1.0"
SKILL_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = SKILL_ROOT / "expert-manifest.json"
KNOWLEDGE_ROOT = SKILL_ROOT / "references" / "knowledge"
LEDGER_PATH = KNOWLEDGE_ROOT / "semantic" / "records.jsonl"
EXPECTED_ARTIFACT_PATHS = {
    "skill_md": "SKILL.md",
    "guidance": "references/guidance.md",
    "query_script": "scripts/query_expert_knowledge.py",
    "snapshot_runtime": "scripts/_classical_snapshot.py",
    "runtime_smoke": "scripts/runtime_smoke.py",
    "requirements": "scripts/requirements.txt",
    "agents_metadata": "agents/openai.yaml",
}
EXPECTED_NON_KNOWLEDGE_PATHS = {
    "expert-manifest.json",
    *EXPECTED_ARTIFACT_PATHS.values(),
}
HEX_64_RE = re.compile(r"^[0-9a-f]{64}$")


class ExpertQueryError(ValueError):
    """Describe an invalid expert artifact or unsupported query."""


def _configure_utf8() -> None:
    """Configure deterministic UTF-8 console output when supported."""

    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(encoding="utf-8")


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _tree_binding(root: Path) -> tuple[str, int]:
    if not root.is_dir() or root.is_symlink():
        raise ExpertQueryError(f"Embedded knowledge is absent or unsafe: {root}")
    files: list[Path] = []
    for path in root.rglob("*"):
        if path.is_symlink():
            raise ExpertQueryError(f"Embedded knowledge contains a symlink: {path}")
        if path.is_file():
            files.append(path)
        elif not path.is_dir():
            raise ExpertQueryError(f"Embedded knowledge contains a special file: {path}")
    digest = hashlib.sha256()
    for path in sorted(files, key=lambda item: item.relative_to(root).as_posix()):
        relative = path.relative_to(root).as_posix().encode("utf-8")
        data = path.read_bytes()
        digest.update(relative)
        digest.update(b"\0")
        digest.update(str(len(data)).encode("ascii"))
        digest.update(b"\0")
        digest.update(data)
        digest.update(b"\0")
    return digest.hexdigest(), len(files)


def _verify_closed_skill_surface() -> None:
    """Reject unbound files, links, and special files outside embedded knowledge."""

    actual: set[str] = set()
    for path in SKILL_ROOT.rglob("*"):
        if path.is_symlink():
            raise ExpertQueryError(f"Generated skill contains a symlink: {path}")
        if path.is_file():
            relative = path.relative_to(SKILL_ROOT).as_posix()
            if not relative.startswith("references/knowledge/"):
                actual.add(relative)
        elif not path.is_dir():
            raise ExpertQueryError(f"Generated skill contains a special file: {path}")
    if actual != EXPECTED_NON_KNOWLEDGE_PATHS:
        missing = sorted(EXPECTED_NON_KNOWLEDGE_PATHS - actual)
        unknown = sorted(actual - EXPECTED_NON_KNOWLEDGE_PATHS)
        raise ExpertQueryError(
            f"Generated skill surface is not closed; missing={missing}, unknown={unknown}"
        )


def _safe_relative(raw: str, *, label: str) -> PurePosixPath:
    candidate = PurePosixPath(raw)
    if (
        not raw
        or candidate.is_absolute()
        or "\\" in raw
        or any(part in {"", ".", ".."} for part in candidate.parts)
    ):
        raise ExpertQueryError(f"Unsafe {label}: {raw!r}")
    return candidate


def _load_json(path: Path, *, label: str) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ExpertQueryError(f"Invalid {label}: {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ExpertQueryError(f"{label} must be a JSON object: {path}")
    return payload


def _load_manifest() -> dict[str, Any]:
    manifest = _load_json(MANIFEST_PATH, label="expert manifest")
    if set(manifest) != {
        "schema_version",
        "skill_name",
        "description",
        "generation",
        "knowledge",
        "artifacts",
    }:
        raise ExpertQueryError("Expert manifest is not closed")
    if manifest.get("schema_version") != SCHEMA_VERSION:
        raise ExpertQueryError("Unsupported expert manifest schema")
    if manifest.get("skill_name") != SKILL_ROOT.name:
        raise ExpertQueryError("Expert manifest skill identity drift")
    return manifest


def _verify_artifacts(manifest: Mapping[str, Any]) -> None:
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, dict) or set(artifacts) != set(EXPECTED_ARTIFACT_PATHS):
        raise ExpertQueryError("Expert artifact binding set is not closed")
    for key, relative in EXPECTED_ARTIFACT_PATHS.items():
        binding = artifacts.get(key)
        if not isinstance(binding, dict) or set(binding) != {"path", "bytes", "sha256"}:
            raise ExpertQueryError(f"Invalid expert artifact binding: {key}")
        if binding.get("path") != relative:
            raise ExpertQueryError(f"Expert artifact path drift: {key}")
        path = SKILL_ROOT.joinpath(*PurePosixPath(relative).parts)
        if not path.is_file() or path.is_symlink():
            raise ExpertQueryError(f"Expert artifact is absent or unsafe: {relative}")
        if binding.get("bytes") != path.stat().st_size:
            raise ExpertQueryError(f"Expert artifact byte-count drift: {key}")
        if binding.get("sha256") != _sha256_file(path):
            raise ExpertQueryError(f"Expert artifact digest drift: {key}")
    actual_scripts = {
        path.relative_to(SKILL_ROOT).as_posix()
        for path in (SKILL_ROOT / "scripts").iterdir()
        if path.is_file()
    }
    expected_scripts = {
        relative
        for relative in EXPECTED_ARTIFACT_PATHS.values()
        if relative.startswith("scripts/")
    }
    if actual_scripts != expected_scripts:
        raise ExpertQueryError("Expert scripts are missing or unbound")


def _records() -> Iterator[dict[str, Any]]:
    try:
        lines = LEDGER_PATH.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        raise ExpertQueryError(f"Cannot read authoritative ledger: {exc}") from exc
    identities: set[tuple[str, str]] = set()
    for number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ExpertQueryError(
                f"Invalid authoritative ledger JSON on line {number}: {exc}"
            ) from exc
        if not isinstance(row, dict):
            raise ExpertQueryError(f"Authoritative ledger line {number} is not an object")
        required = (
            "source_id",
            "record_id",
            "record_sha256",
            "concept_path",
            "source_kind",
            "body",
        )
        if any(not isinstance(row.get(key), str) for key in required):
            raise ExpertQueryError(
                f"Authoritative ledger line {number} lacks required string fields"
            )
        identity = (row["source_id"], row["record_id"])
        if identity in identities:
            raise ExpertQueryError(f"Duplicate authoritative identity: {identity!r}")
        identities.add(identity)
        if not HEX_64_RE.fullmatch(row["record_sha256"]):
            raise ExpertQueryError(f"Invalid authoritative record digest: {identity!r}")
        yield row


def _concept_layout() -> str:
    report = _load_json(
        KNOWLEDGE_ROOT / "semantic" / "build-report.json",
        label="Semantic OKF build report",
    )
    processor = report.get("processor")
    if not isinstance(processor, Mapping):
        return "record-per-file-v1"
    value = processor.get("concept_layout", "record-per-file-v1")
    if not isinstance(value, str):
        raise ExpertQueryError("Semantic OKF concept layout must be a string")
    return value


def _evidence_location(
    record: Mapping[str, Any],
    *,
    layout: str,
    source_counts: Mapping[str, int],
) -> dict[str, Any]:
    logical_raw = record.get("concept_path")
    if not isinstance(logical_raw, str):
        raise ExpertQueryError("Record concept_path must be a string")
    logical = _safe_relative(logical_raw, label="concept_path")
    if not logical.parts or logical.parts[0] != "concepts" or logical.suffix != ".md":
        raise ExpertQueryError(f"Concept path is outside concepts/: {logical_raw}")
    logical_file = KNOWLEDGE_ROOT.joinpath(*logical.parts)
    anchor: str | None = None
    if logical_file.is_file() and not logical_file.is_symlink():
        physical = logical
    elif (
        layout == CONCEPT_LAYOUT_SOURCE_PACKED
        and record.get("source_kind") in STRUCTURED_SOURCE_KINDS
        and source_counts.get(str(record.get("source_id")), 0) > 1
    ):
        physical = _safe_relative(
            f"concepts/{record.get('source_id')}.md",
            label="packed concept path",
        )
        anchor = f"record-{record.get('record_sha256', '')[:16]}"
    else:
        raise ExpertQueryError(f"Logical concept has no physical document: {logical_raw}")
    target = KNOWLEDGE_ROOT.joinpath(*physical.parts)
    if not target.is_file() or target.is_symlink():
        raise ExpertQueryError(
            f"Physical evidence is absent or unsafe: {physical.as_posix()}"
        )
    try:
        target.resolve().relative_to(KNOWLEDGE_ROOT.resolve())
    except ValueError as exc:
        raise ExpertQueryError(
            f"Physical evidence escapes the knowledge root: {physical.as_posix()}"
        ) from exc
    try:
        text = target.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise ExpertQueryError(
            f"Cannot read physical evidence {physical.as_posix()}: {exc}"
        ) from exc
    body = record.get("body")
    if not isinstance(body, str) or body not in text:
        raise ExpertQueryError(
            f"Physical evidence does not contain the exact record body: {logical_raw}"
        )
    if anchor is not None:
        marker = f'<a id="{anchor}"></a>'
        marker_offset = text.find(marker)
        if marker_offset < 0 or text.find(marker, marker_offset + len(marker)) >= 0:
            raise ExpertQueryError(
                f"Packed evidence lacks its exact anchor or body: {logical_raw}"
            )
        body_offset = text.find(body, marker_offset + len(marker))
        next_marker = text.find('\n<a id="record-', marker_offset + len(marker))
        if body_offset < 0 or (next_marker >= 0 and body_offset >= next_marker):
            raise ExpertQueryError(
                f"Packed evidence body is not bound to its exact anchor: {logical_raw}"
            )
    physical_raw = physical.as_posix()
    evidence_path = f"references/knowledge/{physical_raw}"
    citation = evidence_path + (f"#{anchor}" if anchor else "")
    return {
        "logical_concept_path": logical.as_posix(),
        "physical_concept_path": physical_raw,
        "evidence_path": evidence_path,
        "evidence_anchor": anchor,
        "citation": citation,
    }


def _verify(
    *,
    deep_validation: bool,
) -> tuple[dict[str, Any], Any, list[dict[str, Any]], dict[str, Any]]:
    _verify_closed_skill_surface()
    manifest = _load_manifest()
    _verify_artifacts(manifest)
    knowledge = manifest.get("knowledge")
    if not isinstance(knowledge, dict) or set(knowledge) != {
        "format",
        "path",
        "tree",
        "record_count",
        "core_tree_sha256",
        "classical_index_sha256",
        "classical_plan_sha256",
    }:
        raise ExpertQueryError("Expert knowledge binding is invalid")
    if knowledge.get("format") != "semantic-okf-classical":
        raise ExpertQueryError("Expert knowledge format drift")
    if knowledge.get("path") != "references/knowledge":
        raise ExpertQueryError("Expert knowledge path drift")
    expected_tree = knowledge.get("tree")
    if not isinstance(expected_tree, dict) or set(expected_tree) != {"sha256", "file_count"}:
        raise ExpertQueryError("Expert knowledge tree binding is invalid")
    tree_sha256, file_count = _tree_binding(KNOWLEDGE_ROOT)
    if expected_tree.get("sha256") != tree_sha256:
        raise ExpertQueryError("Embedded knowledge tree digest drift")
    if expected_tree.get("file_count") != file_count:
        raise ExpertQueryError("Embedded knowledge file-count drift")
    snapshot = load_snapshot(KNOWLEDGE_ROOT, deep_validation=deep_validation)
    rows = list(_records())
    if knowledge.get("record_count") != len(rows):
        raise ExpertQueryError("Embedded knowledge record-count drift")
    if knowledge.get("core_tree_sha256") != snapshot.index["core"]["tree_sha256"]:
        raise ExpertQueryError("Embedded authoritative core digest drift")
    if knowledge.get("classical_index_sha256") != snapshot.index_sha256:
        raise ExpertQueryError("Embedded classical index digest drift")
    if knowledge.get("classical_plan_sha256") != snapshot.index["classical_plan_sha256"]:
        raise ExpertQueryError("Embedded classical plan digest drift")
    generation = manifest.get("generation")
    if not isinstance(generation, dict) or generation.get("deep_validation") is not True:
        raise ExpertQueryError("Expert generation validation binding is invalid")
    if generation.get("concept_layout") != _concept_layout():
        raise ExpertQueryError("Expert concept-layout binding drift")
    if generation.get("default_query_mode") != "fusion":
        raise ExpertQueryError("Expert default query mode drift")
    result = {
        "schema_version": SCHEMA_VERSION,
        "status": "pass",
        "read_only": True,
        "skill_name": manifest["skill_name"],
        "knowledge_tree_sha256": tree_sha256,
        "knowledge_file_count": file_count,
        "record_count": len(rows),
        "core_tree_sha256": snapshot.index["core"]["tree_sha256"],
        "classical_index_sha256": snapshot.index_sha256,
        "classical_plan_sha256": snapshot.index["classical_plan_sha256"],
        "concept_layout": generation["concept_layout"],
        "deep_validation": deep_validation,
        "default_query_mode": "fusion",
    }
    return manifest, snapshot, rows, result


def verify(*, deep_validation: bool) -> dict[str, Any]:
    """Verify the complete expert and every physical evidence locator."""

    _, _, rows, result = _verify(deep_validation=deep_validation)
    layout = _concept_layout()
    counts = Counter(str(row["source_id"]) for row in rows)
    for row in rows:
        _evidence_location(row, layout=layout, source_counts=counts)
    result["evidence_records_verified"] = len(rows)
    return result


def inspect(*, deep_validation: bool) -> dict[str, Any]:
    """Inspect the expert and classical capabilities without changing files."""

    _, snapshot, rows, verification = _verify(deep_validation=deep_validation)
    result = inspect_snapshot(snapshot)
    result["expert"] = verification
    result["evidence_records"] = len(rows)
    return result


def search(
    query: str,
    mode: str,
    top_k: int,
    *,
    source_ids: Sequence[str],
    concept_ids: Sequence[str],
    concept_types: Sequence[str],
) -> dict[str, Any]:
    """Search the classical projection and add exact physical citations."""

    _, snapshot, rows, verification = _verify(deep_validation=False)
    payload = search_snapshot(
        snapshot,
        query,
        mode,
        top_k,
        source_ids=source_ids,
        concept_ids=concept_ids,
        concept_types=concept_types,
    )
    by_identity = {(row["source_id"], row["record_id"]): row for row in rows}
    layout = _concept_layout()
    counts = Counter(str(row["source_id"]) for row in rows)
    augmented: list[dict[str, Any]] = []
    for result in payload["results"]:
        record = by_identity.get((result.get("source_id"), result.get("record_id")))
        if record is None:
            raise ExpertQueryError("Classical result is orphaned from the ledger")
        location = _evidence_location(record, layout=layout, source_counts=counts)
        augmented.append({**result, **location})
    payload["results"] = augmented
    payload["expert"] = {
        "skill_name": verification["skill_name"],
        "knowledge_tree_sha256": verification["knowledge_tree_sha256"],
        "read_only": True,
        "citation_contract": "physical-path-and-optional-record-anchor",
    }
    return payload


def get_record(
    source_id: str,
    record_id: str,
    *,
    show_content: bool,
) -> dict[str, Any]:
    """Return one exact authoritative record with its physical citation."""

    _, _, rows, verification = _verify(deep_validation=False)
    matches = [
        row
        for row in rows
        if row["source_id"] == source_id and row["record_id"] == record_id
    ]
    if len(matches) != 1:
        raise ExpertQueryError(
            f"Expected one record for ({source_id!r}, {record_id!r}); found {len(matches)}"
        )
    record = matches[0]
    counts = Counter(str(row["source_id"]) for row in rows)
    location = _evidence_location(
        record,
        layout=_concept_layout(),
        source_counts=counts,
    )
    keys = (
        "source_id",
        "record_id",
        "record_sha256",
        "concept_id",
        "concept_type",
        "concept_path",
        "source_path",
        "title",
        "source_refs",
    )
    projected = {key: record.get(key) for key in keys}
    projected.update(location)
    if show_content:
        projected["body"] = record["body"]
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "pass",
        "authoritative": True,
        "expert": {
            "skill_name": verification["skill_name"],
            "knowledge_tree_sha256": verification["knowledge_tree_sha256"],
            "read_only": True,
        },
        "record": projected,
    }


def build_parser() -> argparse.ArgumentParser:
    """Build the read-only expert query parser."""

    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    verify_parser = commands.add_parser("verify", help="Verify every expert binding")
    verify_parser.add_argument("--deep-validation", action="store_true")
    inspect_parser = commands.add_parser("inspect", help="Inspect retrieval capabilities")
    inspect_parser.add_argument("--deep-validation", action="store_true")
    search_parser = commands.add_parser("search", help="Search exact evidence passages")
    search_parser.add_argument("--query", "--contains", dest="query", required=True)
    search_parser.add_argument(
        "--mode",
        choices=("bm25", "topic", "association", "fusion"),
        default="fusion",
    )
    search_parser.add_argument("--top-k", "--limit", dest="top_k", type=int, default=10)
    search_parser.add_argument("--source-id", action="append", default=[])
    search_parser.add_argument("--concept-id", action="append", default=[])
    search_parser.add_argument("--concept-type", "--type", dest="concept_type", action="append", default=[])
    get_parser = commands.add_parser("get", help="Hydrate one exact ledger record")
    get_parser.add_argument("--source-id", required=True)
    get_parser.add_argument("--record-id", required=True)
    get_parser.add_argument("--show-content", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Execute one verified, read-only expert operation."""

    _configure_utf8()
    args = build_parser().parse_args(argv)
    try:
        if args.command == "verify":
            result = verify(deep_validation=args.deep_validation)
        elif args.command == "inspect":
            result = inspect(deep_validation=args.deep_validation)
        elif args.command == "search":
            result = search(
                args.query,
                args.mode,
                args.top_k,
                source_ids=args.source_id,
                concept_ids=args.concept_id,
                concept_types=args.concept_type,
            )
        else:
            result = get_record(
                args.source_id,
                args.record_id,
                show_content=args.show_content,
            )
    except (
        ExpertQueryError,
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
                {
                    "schema_version": SCHEMA_VERSION,
                    "status": "error",
                    "code": "expert-query-error",
                    "error": str(exc),
                },
                ensure_ascii=False,
                sort_keys=True,
            )
        )
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
