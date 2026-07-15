#!/usr/bin/env python3
"""Atomically build and independently validate the entity-graph projection."""

from __future__ import annotations

import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any, Iterable, Mapping

from _entity_graph_model import (
    ALGORITHMS,
    SCHEMA_VERSION,
    EntityGraphError,
    canonical_json,
    core_tree_sha256,
    derive_projection,
    load_core,
    load_plan,
    parse_plan,
    read_json,
    read_jsonl,
    sha256_file,
    validate_rows,
)
from _semantic_okf import validate_semantic_bundle


ARTIFACT_PATHS = {
    "entities": "entity-graph/entities.jsonl",
    "sections": "entity-graph/sections.jsonl",
    "mentions": "entity-graph/mentions.jsonl",
    "edges": "entity-graph/edges.jsonl",
    "lexicon": "entity-graph/lexicon.json",
}
EXPECTED_FILES = {"index.json", "build-report.json", "entities.jsonl", "sections.jsonl", "mentions.jsonl", "edges.jsonl", "lexicon.json"}


def _write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def _write_jsonl(path: Path, rows: Iterable[Mapping[str, Any]]) -> None:
    path.write_text("".join(canonical_json(dict(row)) + "\n" for row in rows), encoding="utf-8")


def _artifact(root: Path, relative: str, count: int | None = None) -> dict[str, Any]:
    path = root / relative
    result: dict[str, Any] = {"path": relative, "bytes": path.stat().st_size, "sha256": sha256_file(path)}
    if count is not None:
        result["count"] = count
    return result


def _core_binding(root: Path) -> dict[str, Any]:
    records, _ = load_core(root)
    return {
        "tree_sha256": core_tree_sha256(root),
        "records_sha256": sha256_file(root / "semantic" / "records.jsonl"),
        "record_count": len(records),
    }


def _artifact_manifest(root: Path, derived: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "entities": _artifact(root, ARTIFACT_PATHS["entities"], len(derived["entities"])),
        "sections": _artifact(root, ARTIFACT_PATHS["sections"], len(derived["sections"])),
        "mentions": _artifact(root, ARTIFACT_PATHS["mentions"], len(derived["mentions"])),
        "edges": _artifact(root, ARTIFACT_PATHS["edges"], len(derived["edges"])),
        "lexicon": _artifact(root, ARTIFACT_PATHS["lexicon"], len(derived["lexicon"]["terms"])),
    }


def build_projection(root: Path, plan_path: Path) -> dict[str, Any]:
    """Add the closed graph projection to an already validated core candidate."""

    plan = load_plan(plan_path)
    derived = derive_projection(root, plan)
    graph = root / "entity-graph"
    if graph.exists() or graph.is_symlink():
        raise EntityGraphError("core candidate unexpectedly contains entity-graph artifacts")
    graph.mkdir()
    _write_jsonl(graph / "entities.jsonl", derived["entities"])
    _write_jsonl(graph / "sections.jsonl", derived["sections"])
    _write_jsonl(graph / "mentions.jsonl", derived["mentions"])
    _write_jsonl(graph / "edges.jsonl", derived["edges"])
    _write_json(graph / "lexicon.json", derived["lexicon"])
    core = _core_binding(root)
    artifacts = _artifact_manifest(root, derived)
    index = {
        "schema_version": SCHEMA_VERSION,
        "authoritative": False,
        "discovery_only": True,
        "core": core,
        "entity_graph_plan_sha256": plan.sha256,
        "plan": plan.raw,
        "selection": derived["selection"],
        "algorithms": ALGORITHMS,
        "artifacts": artifacts,
        "summary": derived["summary"],
    }
    _write_json(graph / "index.json", index)
    initial = validate_entity_graph_bundle(root, require_build_report=False)
    if not initial["valid"]:
        raise EntityGraphError(initial["errors"][0]["message"])
    report = {
        "schema_version": SCHEMA_VERSION,
        "valid": True,
        "status": "pass",
        "errors": [],
        "warnings": [
            {
                "code": "derived-discovery-only",
                "message": "Entity mentions, candidate phrases, co-mentions, and retrieval scores are non-authoritative discovery signals.",
            }
        ],
        "entity_graph_plan_sha256": plan.sha256,
        "core": core,
        "selection": derived["selection"],
        "summary": derived["summary"],
        "artifacts": {"index": _artifact(root, "entity-graph/index.json"), **artifacts},
    }
    _write_json(graph / "build-report.json", report)
    final = validate_entity_graph_bundle(root)
    if not final["valid"]:
        raise EntityGraphError(final["errors"][0]["message"])
    return report


def _validate_or_raise(root: Path, *, require_build_report: bool) -> dict[str, Any]:
    if not root.is_dir():
        raise EntityGraphError(f"bundle does not exist or is not a directory: {root}")
    core_result = validate_semantic_bundle(root)
    if not core_result.valid:
        detail = "; ".join(error.get("message", "core error") for error in core_result.errors[:3])
        raise EntityGraphError(f"authoritative Semantic OKF core is invalid: {detail}")
    graph = root / "entity-graph"
    expected = EXPECTED_FILES if require_build_report else EXPECTED_FILES - {"build-report.json"}
    if not graph.is_dir() or graph.is_symlink():
        raise EntityGraphError("entity-graph must be a real directory")
    actual = {path.name for path in graph.iterdir()}
    if actual != expected:
        raise EntityGraphError(
            f"entity-graph artifact set is closed; missing={sorted(expected - actual)}, unknown={sorted(actual - expected)}"
        )
    if any(path.is_symlink() or not path.is_file() for path in graph.iterdir()):
        raise EntityGraphError("entity-graph artifacts must be regular files")
    index = read_json(graph / "index.json", "entity-graph/index.json")
    expected_index_keys = {
        "schema_version",
        "authoritative",
        "discovery_only",
        "core",
        "entity_graph_plan_sha256",
        "plan",
        "selection",
        "algorithms",
        "artifacts",
        "summary",
    }
    if not isinstance(index, dict) or set(index) != expected_index_keys:
        raise EntityGraphError("entity-graph index has an invalid closed schema")
    if index["schema_version"] != SCHEMA_VERSION or index["authoritative"] is not False or index["discovery_only"] is not True:
        raise EntityGraphError("entity-graph index version or authority markers are invalid")
    if index["algorithms"] != ALGORITHMS:
        raise EntityGraphError("entity-graph algorithm identities are invalid")
    plan = parse_plan(index["plan"])
    if index["entity_graph_plan_sha256"] != plan.sha256:
        raise EntityGraphError("entity-graph plan digest is invalid")
    derived = derive_projection(root, plan)
    persisted = {
        "entities": read_jsonl(graph / "entities.jsonl", label="entity-graph/entities.jsonl"),
        "sections": read_jsonl(graph / "sections.jsonl", label="entity-graph/sections.jsonl"),
        "mentions": read_jsonl(graph / "mentions.jsonl", label="entity-graph/mentions.jsonl"),
        "edges": read_jsonl(graph / "edges.jsonl", label="entity-graph/edges.jsonl"),
        "lexicon": read_json(graph / "lexicon.json", "entity-graph/lexicon.json"),
    }
    validate_rows(persisted["entities"], persisted["sections"], persisted["mentions"], persisted["edges"], persisted["lexicon"])
    for name in ("entities", "sections", "mentions", "edges", "lexicon"):
        if persisted[name] != derived[name]:
            raise EntityGraphError(f"entity-graph {name} differ from deterministic authoritative derivation")
    core = _core_binding(root)
    artifacts = _artifact_manifest(root, derived)
    if index["core"] != core:
        raise EntityGraphError("entity-graph authoritative core binding is stale")
    if index["selection"] != derived["selection"]:
        raise EntityGraphError("entity-graph source selection binding is invalid")
    if index["artifacts"] != artifacts:
        raise EntityGraphError("entity-graph artifact hashes, sizes, or counts are invalid")
    if index["summary"] != derived["summary"]:
        raise EntityGraphError("entity-graph summary is invalid")
    expected_report = {
        "schema_version": SCHEMA_VERSION,
        "valid": True,
        "status": "pass",
        "errors": [],
        "warnings": [
            {
                "code": "derived-discovery-only",
                "message": "Entity mentions, candidate phrases, co-mentions, and retrieval scores are non-authoritative discovery signals.",
            }
        ],
        "entity_graph_plan_sha256": plan.sha256,
        "core": core,
        "selection": derived["selection"],
        "summary": derived["summary"],
        "artifacts": {"index": _artifact(root, "entity-graph/index.json"), **artifacts},
    }
    if require_build_report:
        report = read_json(graph / "build-report.json", "entity-graph/build-report.json")
        if report != expected_report:
            raise EntityGraphError("entity-graph build report differs from live validation")
    return {
        "schema_version": SCHEMA_VERSION,
        "valid": True,
        "status": "pass",
        "errors": [],
        "warnings": expected_report["warnings"],
        "summary": derived["summary"],
    }


def validate_entity_graph_bundle(root: Path, *, require_build_report: bool = True) -> dict[str, Any]:
    """Independently rederive and validate the core-bound entity graph."""

    try:
        return _validate_or_raise(root.resolve(), require_build_report=require_build_report)
    except (EntityGraphError, OSError, UnicodeError, KeyError, IndexError, TypeError, ValueError, OverflowError) as exc:
        return {
            "schema_version": SCHEMA_VERSION,
            "valid": False,
            "status": "error",
            "errors": [{"code": "entity-graph-error", "path": "entity-graph", "message": str(exc)}],
            "warnings": [],
            "summary": {},
        }


def atomic_build(manifest_path: Path, plan_path: Path, output: Path, core_builder: Any) -> dict[str, Any]:
    """Build core and graph layers in a private sibling, then publish once."""

    output = output.resolve()
    if output.exists() or output.is_symlink():
        raise EntityGraphError(f"output already exists: {output}")
    load_plan(plan_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    candidate = Path(tempfile.mkdtemp(prefix=f".{output.name}.entity-graph-candidate-", dir=output.parent))
    candidate.rmdir()
    try:
        core_builder(manifest_path, candidate)
        build_projection(candidate, plan_path)
        os.replace(candidate, output)
    except Exception:
        if candidate.exists():
            shutil.rmtree(candidate, ignore_errors=True)
        raise
    return read_json(output / "entity-graph" / "build-report.json", "entity-graph/build-report.json")
