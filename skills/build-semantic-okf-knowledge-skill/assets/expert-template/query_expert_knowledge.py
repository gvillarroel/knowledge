#!/usr/bin/env python3
"""Verify and query one immutable, family-bound Semantic OKF expert."""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
from typing import Any, Iterator, Mapping, Sequence

sys.dont_write_bytecode = True


SCHEMA_VERSION = "semantic-okf-family-knowledge-skill/1.0"
SKILL_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = SKILL_ROOT / "expert-manifest.json"
KNOWLEDGE_ROOT = SKILL_ROOT / "references" / "knowledge"
LEDGER_PATH = KNOWLEDGE_ROOT / "semantic" / "records.jsonl"
NATIVE_ROOT = SKILL_ROOT / "scripts" / "native"
HEX_64_RE = re.compile(r"^[0-9a-f]{64}$")
STRUCTURED_SOURCE_KINDS = {"csv", "json", "rdf"}
SOURCE_PACKED_LAYOUT = "source-packed-v1"


FAMILY_CONTRACTS: dict[str, dict[str, Any]] = {
    "legacy": {
        "id": "legacy", "display_name": "Legacy Semantic OKF",
        "build_skill": "build-semantic-okf", "consult_skill": "consult-semantic-okf",
        "build_script": "build_semantic_okf.py", "validate_script": "validate_semantic_okf.py",
        "query_script": "query_semantic_okf.py", "uses_plan": False,
        "modes": ["ledger"], "default_mode": "ledger",
        "search_style": "legacy-ledger", "target": "bundle", "model_optional": False,
    },
    "embeddings": {
        "id": "embeddings", "display_name": "Embedding Semantic OKF",
        "build_skill": "build-semantic-okf-embeddings",
        "consult_skill": "consult-semantic-okf-embeddings",
        "build_script": "build_semantic_okf_embeddings.py",
        "validate_script": "validate_semantic_okf_embeddings.py",
        "query_script": "query_semantic_okf_embeddings.py", "uses_plan": True,
        "modes": ["auto", "lexical", "vector", "hybrid"], "default_mode": "auto",
        "search_style": "mode-option", "target": "bundle", "model_optional": True,
    },
    "classical": {
        "id": "classical", "display_name": "Classical Semantic OKF",
        "build_skill": "build-semantic-okf-classical",
        "consult_skill": "consult-semantic-okf-classical",
        "build_script": "build_semantic_okf_classical.py",
        "validate_script": "validate_semantic_okf_classical.py",
        "query_script": "query_semantic_okf_classical.py", "uses_plan": True,
        "modes": ["bm25", "topic", "association", "fusion"], "default_mode": "fusion",
        "search_style": "mode-option", "target": "bundle", "model_optional": False,
    },
    "adaptive": {
        "id": "adaptive", "display_name": "Adaptive Semantic OKF",
        "build_skill": "build-semantic-okf-adaptive",
        "consult_skill": "consult-semantic-okf-adaptive",
        "build_script": "build_semantic_okf_adaptive.py",
        "validate_script": "validate_semantic_okf_adaptive.py",
        "query_script": "query_semantic_okf_adaptive.py", "uses_plan": True,
        "modes": ["bm25", "topic", "association", "fusion", "adaptive"],
        "default_mode": "adaptive", "search_style": "mode-option",
        "target": "bundle", "model_optional": False,
    },
    "entity-graph": {
        "id": "entity-graph", "display_name": "Entity Graph Semantic OKF",
        "build_skill": "build-semantic-okf-entity-graph",
        "consult_skill": "consult-semantic-okf-entity-graph",
        "build_script": "build_semantic_okf_entity_graph.py",
        "validate_script": "validate_semantic_okf_entity_graph.py",
        "query_script": "query_semantic_okf_entity_graph.py", "uses_plan": True,
        "modes": ["lexical", "entity", "traversal", "fusion"], "default_mode": "fusion",
        "search_style": "mode-option", "target": "bundle", "model_optional": False,
    },
    "ensemble": {
        "id": "ensemble", "display_name": "Ensemble Semantic OKF",
        "build_skill": "build-semantic-okf-ensemble",
        "consult_skill": "consult-semantic-okf-ensemble",
        "build_script": "build_semantic_okf_ensemble.py",
        "validate_script": "validate_semantic_okf_ensemble.py",
        "query_script": "query_semantic_okf_ensemble.py", "uses_plan": True,
        "modes": ["default", "quality", "fast", "robust"], "default_mode": "default",
        "search_style": "policy-option", "target": "bundle", "model_optional": True,
    },
    "graphify": {
        "id": "graphify", "display_name": "Graphify Semantic OKF",
        "build_skill": "build-semantic-okf-graphify",
        "consult_skill": "consult-semantic-okf-graphify",
        "build_script": "build_semantic_okf_graphify.py",
        "validate_script": "validate_semantic_okf_graphify.py",
        "query_script": "query_semantic_okf_graphify.py", "uses_plan": False,
        "modes": ["graphify"], "default_mode": "graphify",
        "search_style": "graphify-positional", "target": "bundle", "model_optional": False,
    },
    "turso": {
        "id": "turso", "display_name": "Turso Semantic OKF",
        "build_skill": "build-semantic-okf-turso", "consult_skill": "consult-semantic-okf-turso",
        "build_script": "build_semantic_okf.py", "validate_script": "validate_semantic_okf.py",
        "query_script": "query_turso_knowledge.py", "uses_plan": False,
        "modes": ["records"], "default_mode": "records",
        "search_style": "turso-records", "target": "semantic/knowledge.db",
        "model_optional": False,
    },
}


class ExpertQueryError(ValueError):
    """Describe an invalid expert or native consultation failure."""


def _configure_utf8() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(encoding="utf-8", errors="strict")


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _regular_files(root: Path) -> Iterator[Path]:
    if not root.is_dir() or root.is_symlink():
        raise ExpertQueryError(f"Directory is absent or unsafe: {root}")
    files: list[Path] = []
    for path in root.rglob("*"):
        if path.is_symlink():
            raise ExpertQueryError(f"Symlink is not allowed: {path}")
        if path.is_file():
            files.append(path)
        elif not path.is_dir():
            raise ExpertQueryError(f"Special file is not allowed: {path}")
    yield from sorted(files, key=lambda item: item.relative_to(root).as_posix())


def _tree_binding(root: Path) -> tuple[str, int]:
    digest = hashlib.sha256()
    count = 0
    for path in _regular_files(root):
        relative = path.relative_to(root).as_posix().encode("utf-8")
        data = path.read_bytes()
        digest.update(relative)
        digest.update(b"\0")
        digest.update(str(len(data)).encode("ascii"))
        digest.update(b"\0")
        digest.update(data)
        digest.update(b"\0")
        count += 1
    return digest.hexdigest(), count


def _safe_relative(raw: str, *, label: str) -> PurePosixPath:
    value = PurePosixPath(raw)
    if (
        not raw or value.is_absolute() or "\\" in raw
        or any(part in {"", ".", ".."} for part in value.parts)
    ):
        raise ExpertQueryError(f"Unsafe {label}: {raw!r}")
    return value


def _load_json(path: Path, *, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ExpertQueryError(f"Invalid {label}: {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ExpertQueryError(f"{label} must be a JSON object: {path}")
    return value


def _records() -> list[dict[str, Any]]:
    try:
        lines = LEDGER_PATH.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        raise ExpertQueryError(f"Cannot read authoritative ledger: {exc}") from exc
    rows: list[dict[str, Any]] = []
    identities: set[tuple[str, str]] = set()
    for number, line in enumerate(lines, 1):
        if not line.strip():
            raise ExpertQueryError(f"Blank authoritative ledger line: {number}")
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ExpertQueryError(f"Invalid ledger JSON on line {number}: {exc}") from exc
        if not isinstance(row, dict):
            raise ExpertQueryError(f"Ledger line {number} is not an object")
        required = ("source_id", "record_id", "record_sha256", "concept_path", "source_kind", "body")
        if any(not isinstance(row.get(key), str) for key in required):
            raise ExpertQueryError(f"Ledger line {number} lacks required string fields")
        identity = (row["source_id"], row["record_id"])
        if identity in identities:
            raise ExpertQueryError(f"Duplicate authoritative identity: {identity!r}")
        if not HEX_64_RE.fullmatch(row["record_sha256"]):
            raise ExpertQueryError(f"Invalid authoritative record digest: {identity!r}")
        identities.add(identity)
        rows.append(row)
    if not rows:
        raise ExpertQueryError("Authoritative ledger is empty")
    return rows


def _concept_layout() -> str:
    report = _load_json(KNOWLEDGE_ROOT / "semantic" / "build-report.json", label="build report")
    if report.get("status") != "pass":
        raise ExpertQueryError("Semantic OKF build report is not passing")
    processor = report.get("processor")
    if not isinstance(processor, dict):
        raise ExpertQueryError("Semantic OKF processor report is invalid")
    value = processor.get("concept_layout", "record-per-file-v1")
    if value not in {"record-per-file-v1", SOURCE_PACKED_LAYOUT}:
        raise ExpertQueryError(f"Unsupported concept layout: {value!r}")
    return value


def _evidence_location(
    record: Mapping[str, Any], *, layout: str, source_counts: Mapping[str, int]
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
        layout == SOURCE_PACKED_LAYOUT
        and record.get("source_kind") in STRUCTURED_SOURCE_KINDS
        and source_counts.get(str(record.get("source_id")), 0) > 1
    ):
        physical = _safe_relative(
            f"concepts/{record.get('source_id')}.md", label="packed concept path"
        )
        anchor = f"record-{record['record_sha256'][:16]}"
    else:
        raise ExpertQueryError(f"Logical concept has no physical document: {logical_raw}")
    target = KNOWLEDGE_ROOT.joinpath(*physical.parts)
    if not target.is_file() or target.is_symlink():
        raise ExpertQueryError(f"Physical evidence is absent or unsafe: {physical}")
    try:
        target.resolve().relative_to(KNOWLEDGE_ROOT.resolve())
    except ValueError as exc:
        raise ExpertQueryError(f"Physical evidence escapes knowledge: {physical}") from exc
    text = target.read_text(encoding="utf-8")
    if record["body"] not in text:
        raise ExpertQueryError(f"Physical evidence lacks exact body: {logical_raw}")
    if anchor is not None:
        marker = f'<a id="{anchor}"></a>'
        marker_offset = text.find(marker)
        if marker_offset < 0 or text.find(marker, marker_offset + len(marker)) >= 0:
            raise ExpertQueryError(f"Packed evidence anchor is absent or duplicated: {anchor}")
        body_offset = text.find(record["body"], marker_offset + len(marker))
        next_marker = text.find('\n<a id="record-', marker_offset + len(marker))
        if body_offset < 0 or (next_marker >= 0 and body_offset >= next_marker):
            raise ExpertQueryError(f"Packed body is not bound to exact anchor: {anchor}")
    physical_raw = physical.as_posix()
    evidence_path = f"references/knowledge/{physical_raw}"
    return {
        "logical_concept_path": logical.as_posix(),
        "physical_concept_path": physical_raw,
        "evidence_path": evidence_path,
        "evidence_anchor": anchor,
        "citation": evidence_path + (f"#{anchor}" if anchor else ""),
    }


def _verify_static() -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]], dict[str, Any]]:
    if SKILL_ROOT.is_symlink():
        raise ExpertQueryError("Expert skill root cannot be a symlink")
    manifest = _load_json(MANIFEST_PATH, label="expert manifest")
    if set(manifest) != {
        "schema_version", "skill_name", "description", "family", "generation", "knowledge", "artifacts"
    }:
        raise ExpertQueryError("Expert manifest is not closed")
    if manifest.get("schema_version") != SCHEMA_VERSION:
        raise ExpertQueryError("Unsupported expert manifest schema")
    if manifest.get("skill_name") != SKILL_ROOT.name:
        raise ExpertQueryError("Expert manifest skill identity drift")
    family = manifest.get("family")
    family_id = family.get("id") if isinstance(family, dict) else None
    if family_id not in FAMILY_CONTRACTS or family != FAMILY_CONTRACTS[family_id]:
        raise ExpertQueryError("Expert family contract drift")

    generation = manifest.get("generation")
    if not isinstance(generation, dict) or set(generation) != {
        "builder", "concept_layout", "source_manifest_sha256", "plan_input_sha256",
        "deep_validation", "active_requirements",
    }:
        raise ExpertQueryError("Expert generation binding is invalid")
    if generation.get("builder") != "build-semantic-okf-knowledge-skill":
        raise ExpertQueryError("Expert builder identity drift")
    if generation.get("deep_validation") is not True:
        raise ExpertQueryError("Expert was not deeply validated at generation")
    if not isinstance(generation.get("source_manifest_sha256"), str) or not HEX_64_RE.fullmatch(
        generation["source_manifest_sha256"]
    ):
        raise ExpertQueryError("Source manifest digest binding is invalid")
    plan_hash = generation.get("plan_input_sha256")
    if family["uses_plan"]:
        if not isinstance(plan_hash, str) or not HEX_64_RE.fullmatch(plan_hash):
            raise ExpertQueryError("Plan digest binding is invalid")
    elif plan_hash is not None:
        raise ExpertQueryError("Planless family unexpectedly binds a plan")

    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        raise ExpertQueryError("Expert artifact bindings are invalid")
    expected_paths: set[str] = set()
    for index, binding in enumerate(artifacts):
        if not isinstance(binding, dict) or set(binding) != {"path", "bytes", "sha256"}:
            raise ExpertQueryError(f"Invalid artifact binding at index {index}")
        raw = binding.get("path")
        if not isinstance(raw, str):
            raise ExpertQueryError(f"Invalid artifact path at index {index}")
        relative = _safe_relative(raw, label="artifact path")
        if raw.startswith("references/knowledge/") or raw == "expert-manifest.json":
            raise ExpertQueryError(f"Reserved artifact binding: {raw}")
        if raw in expected_paths:
            raise ExpertQueryError(f"Duplicate artifact binding: {raw}")
        expected_paths.add(raw)
        path = SKILL_ROOT.joinpath(*relative.parts)
        if not path.is_file() or path.is_symlink():
            raise ExpertQueryError(f"Bound artifact is absent or unsafe: {raw}")
        if binding.get("bytes") != path.stat().st_size or binding.get("sha256") != _sha256_file(path):
            raise ExpertQueryError(f"Artifact binding drift: {raw}")
    actual_paths = {
        path.relative_to(SKILL_ROOT).as_posix()
        for path in _regular_files(SKILL_ROOT)
        if not path.relative_to(SKILL_ROOT).as_posix().startswith("references/knowledge/")
        and path.name != "expert-manifest.json"
    }
    if actual_paths != expected_paths:
        raise ExpertQueryError(
            "Expert artifact surface is not closed; "
            f"missing={sorted(expected_paths - actual_paths)}, unknown={sorted(actual_paths - expected_paths)}"
        )
    active = generation.get("active_requirements")
    if not isinstance(active, str) or active not in expected_paths:
        raise ExpertQueryError("Active requirements are absent or unbound")

    knowledge = manifest.get("knowledge")
    if not isinstance(knowledge, dict) or set(knowledge) != {
        "format", "path", "tree", "record_count", "build_report_sha256"
    }:
        raise ExpertQueryError("Expert knowledge binding is invalid")
    if knowledge.get("format") != "semantic-okf" or knowledge.get("path") != "references/knowledge":
        raise ExpertQueryError("Expert knowledge format/path drift")
    expected_tree = knowledge.get("tree")
    if not isinstance(expected_tree, dict) or set(expected_tree) != {"sha256", "file_count"}:
        raise ExpertQueryError("Expert knowledge tree binding is invalid")
    tree_sha256, file_count = _tree_binding(KNOWLEDGE_ROOT)
    if expected_tree != {"sha256": tree_sha256, "file_count": file_count}:
        raise ExpertQueryError("Embedded knowledge tree binding drift")
    rows = _records()
    if knowledge.get("record_count") != len(rows):
        raise ExpertQueryError("Embedded knowledge record-count drift")
    if knowledge.get("build_report_sha256") != _sha256_file(
        KNOWLEDGE_ROOT / "semantic" / "build-report.json"
    ):
        raise ExpertQueryError("Embedded build-report digest drift")
    layout = _concept_layout()
    if generation.get("concept_layout") != layout:
        raise ExpertQueryError("Expert concept-layout binding drift")
    query_script = NATIVE_ROOT / family["query_script"]
    if not query_script.is_file() or query_script.is_symlink():
        raise ExpertQueryError("Matched native consultant is absent or unsafe")
    verification = {
        "schema_version": SCHEMA_VERSION,
        "status": "pass",
        "read_only": True,
        "skill_name": manifest["skill_name"],
        "family": family_id,
        "knowledge_tree_sha256": tree_sha256,
        "knowledge_file_count": file_count,
        "record_count": len(rows),
        "concept_layout": layout,
        "default_query_mode": family["default_mode"],
    }
    return manifest, family, rows, verification


def _native_target(family: Mapping[str, Any]) -> Path:
    if family["target"] == "bundle":
        return KNOWLEDGE_ROOT
    return KNOWLEDGE_ROOT.joinpath(*PurePosixPath(family["target"]).parts)


def _run_native(family: Mapping[str, Any], arguments: Sequence[str]) -> dict[str, Any]:
    script = NATIVE_ROOT / str(family["query_script"])
    env = os.environ.copy()
    env.update({
        "PYTHONDONTWRITEBYTECODE": "1",
        "HF_HUB_OFFLINE": "1",
        "TRANSFORMERS_OFFLINE": "1",
        "TOKENIZERS_PARALLELISM": "false",
    })
    completed = subprocess.run(
        [sys.executable, "-B", str(script), *arguments],
        cwd=NATIVE_ROOT,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="strict",
        check=False,
    )
    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout).strip()
        raise ExpertQueryError(
            f"Native {family['id']} consultation failed ({completed.returncode}): {detail[-2000:]}"
        )
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise ExpertQueryError(
            f"Native {family['id']} consultant emitted invalid JSON: {completed.stdout[-1000:]!r}"
        ) from exc
    if not isinstance(payload, dict) or payload.get("status") == "error":
        raise ExpertQueryError(f"Native {family['id']} consultant returned an invalid payload")
    return payload


def _native_inspect_arguments(family: Mapping[str, Any], deep_validation: bool) -> list[str]:
    target = str(_native_target(family))
    family_id = family["id"]
    if family_id == "legacy":
        return [target, "ledger", "--limit", "1", "--validate", "--format", "json"]
    if family_id == "embeddings":
        return [target, "inspect"]
    if family_id in {"classical", "adaptive", "entity-graph"}:
        return [target, "inspect", *(["--deep-validation"] if deep_validation else [])]
    if family_id == "ensemble":
        return [*(["--deep-validation"] if deep_validation else []), target, "inspect"]
    if family_id == "graphify":
        return ["--format", "json", target, "verify"]
    if family_id == "turso":
        return [*(["--validate"] if deep_validation else []), target, "verify", "--format", "json"]
    raise ExpertQueryError(f"Unsupported family: {family_id!r}")


def _native_search_arguments(
    family: Mapping[str, Any], query: str, mode: str, top_k: int,
    *, source_ids: Sequence[str], concept_ids: Sequence[str],
    concept_types: Sequence[str], allow_fallback: bool,
) -> list[str]:
    family_id = family["id"]
    if mode not in family["modes"]:
        raise ExpertQueryError(f"Mode {mode!r} is not available for family {family_id!r}")
    target = str(_native_target(family))
    if family_id == "legacy":
        args = [target, "ledger", "--contains", query, "--limit", str(top_k), "--validate", "--format", "json"]
        for value in source_ids: args.extend(("--source-id", value))
        for value in concept_ids: args.extend(("--concept-id", value))
        for value in concept_types: args.extend(("--type", value))
        return args
    if family_id in {"embeddings", "classical", "adaptive"}:
        args = [target, "search", "--query", query, "--mode", mode, "--top-k", str(top_k)]
        for value in source_ids: args.extend(("--source-id", value))
        for value in concept_ids: args.extend(("--concept-id", value))
        for value in concept_types: args.extend(("--concept-type", value))
        if family_id == "embeddings" and allow_fallback: args.append("--allow-fallback")
        return args
    if family_id == "entity-graph":
        if concept_ids or concept_types or allow_fallback:
            raise ExpertQueryError("Entity-graph search does not support concept filters or fallback")
        args = [target, "search", "--query", query, "--mode", mode, "--top-k", str(top_k)]
        for value in source_ids: args.extend(("--source-id", value))
        return args
    if family_id == "ensemble":
        if allow_fallback:
            raise ExpertQueryError("Ensemble search does not expose embedding fallback")
        args = [target, "search", "--query", query, "--policy", mode, "--top-k", str(top_k)]
        for value in source_ids: args.extend(("--source-id", value))
        for value in concept_ids: args.extend(("--concept-id", value))
        for value in concept_types: args.extend(("--concept-type", value))
        return args
    if family_id == "graphify":
        if source_ids or concept_ids or concept_types or allow_fallback:
            raise ExpertQueryError("Graphify search does not support façade filters or fallback")
        return ["--format", "json", target, "search", query, "--top-k", str(top_k), "--show-content"]
    if family_id == "turso":
        if allow_fallback:
            raise ExpertQueryError("Turso records search does not expose fallback")
        args = [target, "records", "--contains", query, "--show-body", "--limit", str(top_k), "--format", "json"]
        for value in source_ids: args.extend(("--source-id", value))
        for value in concept_ids: args.extend(("--concept-id", value))
        for value in concept_types: args.extend(("--type", value))
        return args
    raise ExpertQueryError(f"Unsupported family: {family_id!r}")


def _enrich_payload(payload: Any, rows: Sequence[Mapping[str, Any]]) -> Any:
    by_identity = {(row["source_id"], row["record_id"]): row for row in rows}
    concept_groups: dict[str, list[Mapping[str, Any]]] = {}
    for row in rows:
        concept_id = row.get("concept_id")
        if isinstance(concept_id, str):
            concept_groups.setdefault(concept_id, []).append(row)
    unique_concepts = {key: values[0] for key, values in concept_groups.items() if len(values) == 1}
    layout = _concept_layout()
    counts = Counter(str(row["source_id"]) for row in rows)

    def visit(value: Any) -> Any:
        if isinstance(value, list):
            return [visit(item) for item in value]
        if not isinstance(value, dict):
            return value
        enriched = {key: visit(item) for key, item in value.items()}
        record = None
        source_id, record_id = value.get("source_id"), value.get("record_id")
        if isinstance(source_id, str) and isinstance(record_id, str):
            record = by_identity.get((source_id, record_id))
        if record is None and isinstance(value.get("concept_id"), str):
            record = unique_concepts.get(value["concept_id"])
        if record is not None:
            location = _evidence_location(record, layout=layout, source_counts=counts)
            for key, item in location.items():
                if key in enriched and enriched[key] != item:
                    raise ExpertQueryError(f"Native evidence field conflicts with authoritative {key}")
                enriched[key] = item
        return enriched

    return visit(payload)


def _require_search_citations(payload: Mapping[str, Any]) -> int:
    candidates = payload.get("results")
    if candidates is None:
        candidates = payload.get("hits")
    if candidates is None:
        candidates = payload.get("records")
    if not isinstance(candidates, list):
        raise ExpertQueryError("Native search payload lacks a result list")
    for index, row in enumerate(candidates):
        if not isinstance(row, dict) or not isinstance(row.get("citation"), str):
            raise ExpertQueryError(f"Native result {index} is not bound to physical evidence")
    return len(candidates)


def verify(*, deep_validation: bool) -> dict[str, Any]:
    """Verify the complete expert, native family, and every citation."""

    _, family, rows, result = _verify_static()
    before = _tree_binding(KNOWLEDGE_ROOT)
    native = _run_native(family, _native_inspect_arguments(family, deep_validation))
    counts = Counter(str(row["source_id"]) for row in rows)
    layout = result["concept_layout"]
    for row in rows:
        _evidence_location(row, layout=layout, source_counts=counts)
    after = _tree_binding(KNOWLEDGE_ROOT)
    if before != after:
        raise ExpertQueryError("Embedded knowledge changed during native verification")
    result.update({
        "deep_validation": deep_validation,
        "evidence_records_verified": len(rows),
        "native_verification": native,
    })
    return result


def inspect(*, deep_validation: bool) -> dict[str, Any]:
    """Return matched native capabilities under the verified expert binding."""

    _, family, _, verification = _verify_static()
    before = _tree_binding(KNOWLEDGE_ROOT)
    native = _run_native(family, _native_inspect_arguments(family, deep_validation))
    if before != _tree_binding(KNOWLEDGE_ROOT):
        raise ExpertQueryError("Embedded knowledge changed during native inspection")
    return {"status": "pass", "mode": "inspect", "expert": verification, "native": native}


def search(
    query: str, mode: str | None, top_k: int, *, source_ids: Sequence[str],
    concept_ids: Sequence[str], concept_types: Sequence[str], allow_fallback: bool,
) -> dict[str, Any]:
    """Run the matched native search and add exact physical citations."""

    if not query.strip():
        raise ExpertQueryError("Search query cannot be empty")
    if top_k < 1:
        raise ExpertQueryError("--top-k must be at least 1")
    _, family, rows, verification = _verify_static()
    selected_mode = mode or str(family["default_mode"])
    arguments = _native_search_arguments(
        family, query, selected_mode, top_k,
        source_ids=source_ids, concept_ids=concept_ids,
        concept_types=concept_types, allow_fallback=allow_fallback,
    )
    before = _tree_binding(KNOWLEDGE_ROOT)
    native = _run_native(family, arguments)
    enriched = _enrich_payload(native, rows)
    cited = _require_search_citations(enriched)
    if before != _tree_binding(KNOWLEDGE_ROOT):
        raise ExpertQueryError("Embedded knowledge changed during native search")
    enriched["expert"] = {
        "skill_name": verification["skill_name"],
        "family": verification["family"],
        "knowledge_tree_sha256": verification["knowledge_tree_sha256"],
        "read_only": True,
        "citation_contract": "physical-path-and-optional-record-anchor",
        "cited_results": cited,
    }
    return enriched


def get_record(source_id: str, record_id: str, *, show_content: bool) -> dict[str, Any]:
    """Hydrate one exact ledger record with its portable physical citation."""

    _, _, rows, verification = _verify_static()
    matches = [row for row in rows if row["source_id"] == source_id and row["record_id"] == record_id]
    if len(matches) != 1:
        raise ExpertQueryError(
            f"Expected one record for ({source_id!r}, {record_id!r}); found {len(matches)}"
        )
    record = matches[0]
    counts = Counter(str(row["source_id"]) for row in rows)
    location = _evidence_location(record, layout=_concept_layout(), source_counts=counts)
    projected = {
        key: record.get(key)
        for key in (
            "source_id", "record_id", "record_sha256", "concept_id", "concept_type",
            "concept_path", "source_path", "title", "source_refs",
        )
    }
    projected.update(location)
    if show_content:
        projected["body"] = record["body"]
    return {
        "schema_version": SCHEMA_VERSION, "status": "pass", "authoritative": True,
        "expert": verification, "record": projected,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    verify_parser = commands.add_parser("verify", help="Verify every expert and native binding")
    verify_parser.add_argument("--deep-validation", action="store_true")
    inspect_parser = commands.add_parser("inspect", help="Inspect matched native capabilities")
    inspect_parser.add_argument("--deep-validation", action="store_true")
    search_parser = commands.add_parser("search", help="Search through the matched native family")
    search_parser.add_argument("--query", "--contains", dest="query", required=True)
    search_parser.add_argument("--mode", help="Family mode or ensemble policy; defaults to the bound family default")
    search_parser.add_argument("--top-k", "--limit", dest="top_k", type=int, default=10)
    search_parser.add_argument("--source-id", action="append", default=[])
    search_parser.add_argument("--concept-id", action="append", default=[])
    search_parser.add_argument("--concept-type", "--type", dest="concept_type", action="append", default=[])
    search_parser.add_argument("--allow-fallback", action="store_true")
    get_parser = commands.add_parser("get", help="Hydrate one exact authoritative record")
    get_parser.add_argument("--source-id", required=True)
    get_parser.add_argument("--record-id", required=True)
    get_parser.add_argument("--show-content", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    _configure_utf8()
    args = build_parser().parse_args(argv)
    try:
        if args.command == "verify":
            result = verify(deep_validation=args.deep_validation)
        elif args.command == "inspect":
            result = inspect(deep_validation=args.deep_validation)
        elif args.command == "search":
            result = search(
                args.query, args.mode, args.top_k, source_ids=args.source_id,
                concept_ids=args.concept_id, concept_types=args.concept_type,
                allow_fallback=args.allow_fallback,
            )
        else:
            result = get_record(args.source_id, args.record_id, show_content=args.show_content)
    except (
        ExpertQueryError, OSError, UnicodeError, ValueError, TypeError,
        KeyError, IndexError, subprocess.SubprocessError,
    ) as exc:
        print(json.dumps({
            "schema_version": SCHEMA_VERSION, "status": "error",
            "code": "expert-query-error", "error": str(exc),
        }, ensure_ascii=False, sort_keys=True))
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
