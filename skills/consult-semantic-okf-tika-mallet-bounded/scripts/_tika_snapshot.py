#!/usr/bin/env python3
"""Validate persisted Tika extraction receipts and Semantic OKF bindings read-only."""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any, Iterable, Mapping

import yaml

from _safe_paths import (
    UnsafePathError,
    require_real_directory,
    require_regular_file,
    scan_regular_tree,
)


SCHEMA_VERSION = "1.0"
TIKA_VERSION = "4.0.0-beta-1"
TIKA_ALGORITHM = "apache-tika-4.0.0-beta-1-default-markdown-verified-v1"
TIKA_VERBATIM_ALGORITHM = (
    "apache-tika-4.0.0-beta-1-hybrid-markdown-or-utf8-verbatim-verified-v1"
)
DEFAULT_BODY_MODE = "tika-markdown"
VERBATIM_BODY_MODE = "utf8-verbatim-tika-verified"
DEFAULT_HANDLER = "markdown-default-verified-v1"
VERBATIM_HANDLER = "utf8-verbatim-tika-metadata-verified-v1"
VERBATIM_SUFFIXES = frozenset({".csv", ".json", ".jsonl", ".md", ".markdown", ".txt"})
TIKA_INDEX = "tika/index.json"
TIKA_DOCUMENTS = "tika/documents.jsonl"
PLAN_KEYS = frozenset({"schema_version", "bundle", "sources", "tika"})
BUNDLE_KEYS = frozenset(
    {
        "title",
        "description",
        "base_iri",
        "ontology_iri",
        "version_iri",
        "prefix",
        "owl_profile",
    }
)
SOURCE_KEYS = frozenset({"id", "path", "concept_type"})
SOURCE_OPTIONAL_KEYS = frozenset({"body_mode"})
TIKA_KEYS = frozenset(
    {"version", "verify_default_markdown", "timeout_seconds", "max_input_bytes"}
)
SOURCE_ID_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
WINDOWS_RESERVED = {
    "con",
    "prn",
    "aux",
    "nul",
    *(f"com{index}" for index in range(1, 10)),
    *(f"lpt{index}" for index in range(1, 10)),
}


class TikaSnapshotError(RuntimeError):
    """Report a malformed, stale, or unsafe persisted Tika receipt."""


def _body_mode(source: Mapping[str, Any]) -> str:
    value = source.get("body_mode", DEFAULT_BODY_MODE)
    if value not in {DEFAULT_BODY_MODE, VERBATIM_BODY_MODE}:
        raise TikaSnapshotError(f"unsupported source body_mode: {value!r}")
    return str(value)


def _handler(source: Mapping[str, Any]) -> str:
    return (
        VERBATIM_HANDLER
        if _body_mode(source) == VERBATIM_BODY_MODE
        else DEFAULT_HANDLER
    )


def _plan_algorithm(plan: Mapping[str, Any]) -> str:
    return (
        TIKA_VERBATIM_ALGORITHM
        if any(
            _body_mode(source) == VERBATIM_BODY_MODE
            for source in plan["sources"]
        )
        else TIKA_ALGORITHM
    )


def _handler_pattern(plan: Mapping[str, Any]) -> str:
    handlers = sorted({_handler(source) for source in plan["sources"]})
    if len(handlers) == 1:
        return f"^{re.escape(handlers[0])}$"
    return "^(?:" + "|".join(re.escape(value) for value in handlers) + ")$"


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_json(value: Any) -> str:
    return _sha256_bytes(_canonical_json(value).encode("utf-8"))


def _sha256_file(path: Path) -> str:
    try:
        path = require_regular_file(path, label="Tika artifact")
    except UnsafePathError as exc:
        raise TikaSnapshotError(str(exc)) from exc
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _strict_json_loads(payload: str, label: str) -> Any:
    def reject_constant(value: str) -> Any:
        raise TikaSnapshotError(f"{label} contains non-standard number {value!r}")

    def reject_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise TikaSnapshotError(f"{label} contains duplicate member {key!r}")
            result[key] = value
        return result

    try:
        return json.loads(
            payload,
            object_pairs_hook=reject_duplicates,
            parse_constant=reject_constant,
        )
    except json.JSONDecodeError as exc:
        raise TikaSnapshotError(f"{label} is invalid JSON: {exc}") from exc


def _read_json(path: Path, label: str) -> Any:
    try:
        return _strict_json_loads(path.read_text(encoding="utf-8"), label)
    except (OSError, UnicodeError) as exc:
        raise TikaSnapshotError(f"cannot read {label}: {exc}") from exc


def _read_jsonl(path: Path, label: str) -> list[dict[str, Any]]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        raise TikaSnapshotError(f"cannot read {label}: {exc}") from exc
    rows: list[dict[str, Any]] = []
    for number, line in enumerate(lines, start=1):
        if not line:
            raise TikaSnapshotError(f"{label}:{number} is blank")
        value = _strict_json_loads(line, f"{label}:{number}")
        if not isinstance(value, dict):
            raise TikaSnapshotError(f"{label}:{number} must be an object")
        rows.append(value)
    return rows


def _exact_keys(value: Mapping[str, Any], expected: Iterable[str], label: str) -> None:
    actual = set(value)
    required = set(expected)
    if actual != required:
        raise TikaSnapshotError(
            f"{label} has a closed schema; missing={sorted(required - actual)}, "
            f"unknown={sorted(actual - required)}"
        )


def _plain_int(value: Any, label: str, minimum: int, maximum: int) -> int:
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or not minimum <= value <= maximum
    ):
        raise TikaSnapshotError(
            f"{label} must be an integer from {minimum} through {maximum}"
        )
    return value


def _safe_relative(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TikaSnapshotError(f"{label} must be a non-empty string")
    candidate = PurePosixPath(value.replace("\\", "/"))
    if (
        "\\" in value
        or "://" in value
        or candidate.is_absolute()
        or not candidate.parts
        or any(part in {"", ".", ".."} for part in candidate.parts)
        or PureWindowsPath(value).drive
    ):
        raise TikaSnapshotError(f"{label} must be a portable relative path")
    return candidate.as_posix()


def _validate_plan(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise TikaSnapshotError("Tika plan root must be an object")
    _exact_keys(value, PLAN_KEYS, "Tika plan")
    if value["schema_version"] != SCHEMA_VERSION:
        raise TikaSnapshotError("Tika plan schema version is unsupported")
    bundle = value["bundle"]
    if not isinstance(bundle, dict):
        raise TikaSnapshotError("Tika plan.bundle must be an object")
    _exact_keys(bundle, BUNDLE_KEYS, "Tika plan.bundle")
    if any(not isinstance(bundle[key], str) or not bundle[key].strip() for key in bundle):
        raise TikaSnapshotError("every Tika plan.bundle value must be non-empty")
    sources = value["sources"]
    if not isinstance(sources, list) or not sources:
        raise TikaSnapshotError("Tika plan.sources must be non-empty")
    ids: list[str] = []
    for number, source in enumerate(sources):
        if not isinstance(source, dict):
            raise TikaSnapshotError(f"Tika plan.sources[{number}] must be an object")
        if not SOURCE_KEYS <= set(source) <= SOURCE_KEYS | SOURCE_OPTIONAL_KEYS:
            raise TikaSnapshotError(
                f"Tika plan.sources[{number}] has invalid fields"
            )
        source_id = source["id"]
        if (
            not isinstance(source_id, str)
            or not SOURCE_ID_RE.fullmatch(source_id)
            or source_id in WINDOWS_RESERVED
        ):
            raise TikaSnapshotError(f"Tika plan.sources[{number}].id is invalid")
        ids.append(source_id)
        _safe_relative(source["path"], f"Tika plan.sources[{number}].path")
        if not isinstance(source["concept_type"], str) or not source["concept_type"].strip():
            raise TikaSnapshotError(
                f"Tika plan.sources[{number}].concept_type must be non-empty"
            )
        body_mode = _body_mode(source)
        if (
            body_mode == VERBATIM_BODY_MODE
            and PurePosixPath(source["path"]).suffix.casefold()
            not in VERBATIM_SUFFIXES
        ):
            raise TikaSnapshotError(
                "Tika verbatim source has an unsupported textual suffix"
            )
    if len(ids) != len(set(ids)):
        raise TikaSnapshotError("Tika plan source IDs must be unique")
    tika = value["tika"]
    if not isinstance(tika, dict):
        raise TikaSnapshotError("Tika plan.tika must be an object")
    _exact_keys(tika, TIKA_KEYS, "Tika plan.tika")
    if tika["version"] != TIKA_VERSION or tika["verify_default_markdown"] is not True:
        raise TikaSnapshotError("Tika plan must bind the verified 4.0.0-beta-1 default Markdown contract")
    _plain_int(tika["timeout_seconds"], "Tika timeout_seconds", 1, 3600)
    _plain_int(tika["max_input_bytes"], "Tika max_input_bytes", 1, 2**63 - 1)
    return json.loads(_canonical_json(value))


def _semantic_manifest(plan: Mapping[str, Any]) -> dict[str, Any]:
    properties = [
        ("documentTitle", "xsd:string", "document title"),
        ("sourceLocator", "xsd:string", "source locator"),
        ("rawSha256", "xsd:string", "raw input SHA-256"),
        ("rawBytes", "xsd:long", "raw input bytes"),
        ("mediaType", "xsd:string", "detected media type"),
        ("tikaVersion", "xsd:string", "Apache Tika version"),
        ("tikaMetadataSha256", "xsd:string", "canonical Tika metadata SHA-256"),
        ("extractedBodySha256", "xsd:string", "extracted Markdown body SHA-256"),
        ("tikaHandler", "xsd:string", "Tika handler verification contract"),
    ]
    fields = {
        "title": "documentTitle",
        "source_locator": "sourceLocator",
        "raw_sha256": "rawSha256",
        "raw_bytes": "rawBytes",
        "media_type": "mediaType",
        "tika_version": "tikaVersion",
        "tika_metadata_sha256": "tikaMetadataSha256",
        "extracted_body_sha256": "extractedBodySha256",
        "tika_handler": "tikaHandler",
    }
    patterns = {
        "rawSha256": "^[0-9a-f]{64}$",
        "tikaMetadataSha256": "^[0-9a-f]{64}$",
        "extractedBodySha256": "^[0-9a-f]{64}$",
        "tikaVersion": f"^{re.escape(TIKA_VERSION)}$",
        "tikaHandler": _handler_pattern(plan),
    }
    rules: list[dict[str, Any]] = []
    for name, datatype, label in properties:
        rule: dict[str, Any] = {
            "name": f"Required{name[0].upper()}{name[1:]}",
            "target_class": "ExtractedDocument",
            "path": name,
            "min_count": 1,
            "max_count": 1,
            "datatype": datatype,
            "message": f"Every extracted document must retain its {label}.",
            "basis": {
                "kind": "operational-policy",
                "references": ["TIKA-MALLET-INGESTION-1"],
            },
        }
        if name in patterns:
            rule["pattern"] = patterns[name]
        rules.append(rule)
    return {
        "schema_version": SCHEMA_VERSION,
        "bundle": dict(plan["bundle"]),
        "ontology": {
            "classes": [
                {
                    "name": "ExtractedDocument",
                    "label": "Tika-extracted document",
                    "description": (
                        "A local source document whose text and metadata were extracted "
                        "with a hash-bound Apache Tika runtime."
                    ),
                }
            ],
            "properties": [
                {
                    "name": name,
                    "kind": "datatype",
                    "domain": "ExtractedDocument",
                    "range": datatype,
                    "label": label,
                }
                for name, datatype, label in properties
            ],
        },
        "rules": rules,
        "sources": [
            {
                "id": source["id"],
                "kind": "markdown",
                "path": f"tika/extracted/{source['id']}/*.md",
                "concept_type": source["concept_type"],
                "ontology_class": "ExtractedDocument",
                "fields": fields,
                **(
                    {"body_normalization": "line-endings-only"}
                    if _body_mode(source) == VERBATIM_BODY_MODE
                    else {}
                ),
            }
            for source in plan["sources"]
        ],
    }


def _safe_file(root: Path, relative: Any, label: str, suffix: str) -> Path:
    normalized = _safe_relative(relative, label)
    if not normalized.endswith(suffix):
        raise TikaSnapshotError(f"{label} must end with {suffix}")
    candidate = root.joinpath(*PurePosixPath(normalized).parts)
    try:
        return require_regular_file(candidate, label=label)
    except UnsafePathError as exc:
        raise TikaSnapshotError(f"{label} is missing or unsafe: {normalized}: {exc}") from exc


def _tree_inventory(root: Path, relative: str) -> tuple[list[dict[str, str]], str]:
    directory = root.joinpath(*PurePosixPath(relative).parts)
    rows: list[dict[str, str]] = []
    try:
        files, _ = scan_regular_tree(directory, label=relative)
    except UnsafePathError as exc:
        raise TikaSnapshotError(str(exc)) from exc
    for path in files:
        rows.append(
            {"path": path.relative_to(root).as_posix(), "sha256": _sha256_file(path)}
        )
    return rows, _sha256_json(rows)


def _split_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = normalized.split("\n")
    if not lines or lines[0] != "---":
        raise TikaSnapshotError("extracted Markdown lacks YAML frontmatter")
    try:
        end = lines.index("---", 1)
    except ValueError as exc:
        raise TikaSnapshotError("extracted Markdown frontmatter is unterminated") from exc
    try:
        metadata = yaml.safe_load("\n".join(lines[1:end]))
    except yaml.YAMLError as exc:
        raise TikaSnapshotError(f"extracted Markdown frontmatter is invalid: {exc}") from exc
    if not isinstance(metadata, dict):
        raise TikaSnapshotError("extracted Markdown frontmatter must be an object")
    return metadata, "\n".join(lines[end + 1 :]).strip()


def validate_tika_snapshot(root: Path) -> dict[str, Any]:
    """Validate a closed Tika receipt and its authoritative Semantic OKF parity."""

    try:
        bundle = require_real_directory(root, label="Semantic OKF bundle")
    except UnsafePathError as exc:
        raise TikaSnapshotError(str(exc)) from exc
    tika_root = bundle / "tika"
    try:
        scan_regular_tree(tika_root, label="Tika tree")
    except UnsafePathError as exc:
        raise TikaSnapshotError(str(exc)) from exc
    expected_roots = {"index.json", "documents.jsonl", "extracted", "metadata"}
    actual_roots = {path.name for path in tika_root.iterdir()}
    if actual_roots != expected_roots:
        raise TikaSnapshotError(
            f"tika tree is closed; missing={sorted(expected_roots - actual_roots)}, "
            f"unknown={sorted(actual_roots - expected_roots)}"
        )
    index_path = bundle / TIKA_INDEX
    documents_path = bundle / TIKA_DOCUMENTS
    index = _read_json(index_path, TIKA_INDEX)
    if not isinstance(index, dict):
        raise TikaSnapshotError("tika/index.json root must be an object")
    _exact_keys(
        index,
        {"algorithm", "artifacts", "plan", "plan_sha256", "schema_version", "summary", "toolchain"},
        "Tika index",
    )
    if index["schema_version"] != SCHEMA_VERSION:
        raise TikaSnapshotError("Tika index schema or algorithm is unsupported")
    plan = _validate_plan(index["plan"])
    if index["algorithm"] != _plan_algorithm(plan):
        raise TikaSnapshotError("Tika index algorithm disagrees with its plan")
    if index["plan_sha256"] != _sha256_json(plan):
        raise TikaSnapshotError("Tika plan digest is stale")

    toolchain = index["toolchain"]
    if not isinstance(toolchain, dict):
        raise TikaSnapshotError("Tika toolchain must be an object")
    _exact_keys(
        toolchain,
        {"java_version", "tika_jar_inventory", "tika_jar_tree_sha256", "tika_version"},
        "Tika toolchain",
    )
    if toolchain["tika_version"] != TIKA_VERSION:
        raise TikaSnapshotError("Tika toolchain version is unsupported")
    if (
        not isinstance(toolchain["java_version"], str)
        or not (match := re.search(r'version "(\d+)', toolchain["java_version"]))
        or int(match.group(1)) < 17
    ):
        raise TikaSnapshotError("Tika Java version binding is invalid")
    jars = toolchain["tika_jar_inventory"]
    if (
        not isinstance(jars, list)
        or not jars
        or any(
            not isinstance(row, dict)
            or set(row) != {"path", "sha256"}
            or not isinstance(row["path"], str)
            or _safe_relative(row["path"], "Tika jar path") != row["path"]
            or not isinstance(row["sha256"], str)
            or not SHA256_RE.fullmatch(row["sha256"])
            for row in jars
        )
    ):
        raise TikaSnapshotError("Tika jar inventory is malformed")
    if (
        jars != sorted(jars, key=lambda row: row["path"])
        or len({row["path"].casefold() for row in jars}) != len(jars)
    ):
        raise TikaSnapshotError("Tika jar inventory must be sorted and unique")
    if not any(row["path"] == "tika-app-4.0.0-beta-1.jar" for row in jars):
        raise TikaSnapshotError("Tika jar inventory lacks the beta application jar")
    if toolchain["tika_jar_tree_sha256"] != _sha256_json(jars):
        raise TikaSnapshotError("Tika jar inventory digest is stale")

    rows = _read_jsonl(documents_path, TIKA_DOCUMENTS)
    row_keys = {
        "body_sha256", "concept_type", "markdown_path", "markdown_sha256",
        "media_type", "metadata_path", "metadata_sha256", "raw_bytes", "raw_sha256",
        "source_id", "source_locator", "title",
    }
    sources = {source["id"]: source for source in plan["sources"]}
    seen_inputs: set[tuple[str, str]] = set()
    seen_markdown: set[str] = set()
    seen_metadata: set[str] = set()
    for number, row in enumerate(rows, start=1):
        _exact_keys(row, row_keys, f"Tika document {number}")
        source_id = row["source_id"]
        if source_id not in sources or row["concept_type"] != sources[source_id]["concept_type"]:
            raise TikaSnapshotError("Tika document source identity differs from the plan")
        locator = _safe_relative(row["source_locator"], "Tika source_locator")
        identity = (source_id, locator)
        if identity in seen_inputs:
            raise TikaSnapshotError("Tika input identity is duplicated")
        seen_inputs.add(identity)
        for field in ("body_sha256", "markdown_sha256", "metadata_sha256", "raw_sha256"):
            if not isinstance(row[field], str) or not SHA256_RE.fullmatch(row[field]):
                raise TikaSnapshotError(f"Tika document {field} is invalid")
        raw_bytes = _plain_int(row["raw_bytes"], "Tika raw_bytes", 0, 2**63 - 1)
        if raw_bytes > plan["tika"]["max_input_bytes"]:
            raise TikaSnapshotError("Tika raw_bytes exceeds the plan limit")
        if (
            not isinstance(row["title"], str)
            or not row["title"]
            or not isinstance(row["media_type"], str)
            or not row["media_type"]
        ):
            raise TikaSnapshotError("Tika document title or media type is invalid")
        markdown = _safe_file(bundle, row["markdown_path"], "Tika markdown_path", ".md")
        metadata_path = _safe_file(bundle, row["metadata_path"], "Tika metadata_path", ".json")
        relative_markdown = markdown.relative_to(bundle).as_posix()
        relative_metadata = metadata_path.relative_to(bundle).as_posix()
        if not relative_markdown.startswith(f"tika/extracted/{source_id}/"):
            raise TikaSnapshotError("Tika Markdown is outside its source partition")
        if relative_markdown.casefold() in seen_markdown:
            raise TikaSnapshotError("Tika Markdown path is duplicated case-insensitively")
        seen_markdown.add(relative_markdown.casefold())
        if not relative_metadata.startswith(f"tika/metadata/{source_id}/"):
            raise TikaSnapshotError("Tika metadata is outside its source partition")
        if relative_metadata.casefold() in seen_metadata:
            raise TikaSnapshotError("Tika metadata path is duplicated case-insensitively")
        seen_metadata.add(relative_metadata.casefold())
        if _sha256_file(markdown) != row["markdown_sha256"]:
            raise TikaSnapshotError("Tika Markdown hash is stale")
        metadata = _read_json(metadata_path, str(row["metadata_path"]))
        if not isinstance(metadata, dict) or _sha256_json(metadata) != row["metadata_sha256"]:
            raise TikaSnapshotError("Tika metadata hash is stale")
        frontmatter, body = _split_frontmatter(markdown.read_text(encoding="utf-8"))
        expected_frontmatter = {
            "extracted_body_sha256": row["body_sha256"],
            "media_type": row["media_type"],
            "raw_bytes": row["raw_bytes"],
            "raw_sha256": row["raw_sha256"],
            "source_locator": row["source_locator"],
            "tika_handler": _handler(sources[source_id]),
            "tika_metadata_sha256": row["metadata_sha256"],
            "tika_version": TIKA_VERSION,
            "title": row["title"],
        }
        if frontmatter != expected_frontmatter:
            raise TikaSnapshotError("Tika Markdown frontmatter differs from its receipt")
        if _sha256_bytes(body.encode("utf-8")) != row["body_sha256"]:
            raise TikaSnapshotError("Tika extracted body hash is stale")

    if rows != sorted(rows, key=lambda row: (row["source_id"], row["source_locator"])):
        raise TikaSnapshotError("Tika document rows are not deterministically ordered")
    if {row["source_id"] for row in rows} != set(sources):
        raise TikaSnapshotError("Tika document rows do not cover every planned source")

    artifacts = index["artifacts"]
    if not isinstance(artifacts, dict):
        raise TikaSnapshotError("Tika artifacts must be an object")
    _exact_keys(artifacts, {"documents", "extracted", "metadata"}, "Tika artifacts")
    if artifacts["documents"] != {
        "bytes": documents_path.stat().st_size,
        "count": len(rows),
        "path": TIKA_DOCUMENTS,
        "sha256": _sha256_file(documents_path),
    }:
        raise TikaSnapshotError("Tika document artifact binding is stale")
    extracted_rows, extracted_sha = _tree_inventory(bundle, "tika/extracted")
    metadata_rows, metadata_sha = _tree_inventory(bundle, "tika/metadata")
    if {row["path"].casefold() for row in extracted_rows} != seen_markdown:
        raise TikaSnapshotError("Tika extracted tree and document receipt lack parity")
    if {row["path"].casefold() for row in metadata_rows} != seen_metadata:
        raise TikaSnapshotError("Tika metadata tree and document receipt lack parity")
    if artifacts["extracted"] != {
        "count": len(extracted_rows),
        "inventory_sha256": extracted_sha,
        "path": "tika/extracted",
    }:
        raise TikaSnapshotError("Tika extracted inventory is stale")
    if artifacts["metadata"] != {
        "count": len(metadata_rows),
        "inventory_sha256": metadata_sha,
        "path": "tika/metadata",
    }:
        raise TikaSnapshotError("Tika metadata inventory is stale")
    if index["summary"] != {"documents": len(rows), "sources": len(sources)}:
        raise TikaSnapshotError("Tika summary is stale")

    semantic_plan = _read_json(
        bundle / "semantic" / "semantic-plan.json", "semantic/semantic-plan.json"
    )
    if semantic_plan != _semantic_manifest(plan):
        raise TikaSnapshotError("Semantic plan differs from the Tika-generated manifest")
    records = _read_jsonl(bundle / "semantic" / "records.jsonl", "semantic/records.jsonl")
    document_by_path = {row["markdown_path"]: row for row in rows}
    record_by_path = {row.get("source_path"): row for row in records}
    if len(record_by_path) != len(records) or set(document_by_path) != set(record_by_path):
        raise TikaSnapshotError("Tika documents and Semantic OKF records lack parity")
    for path, document in document_by_path.items():
        record = record_by_path[path]
        if record.get("source_id") != document["source_id"] or record.get("title") != document["title"]:
            raise TikaSnapshotError("Tika identity differs from the authoritative ledger")
        if _sha256_bytes(str(record.get("body", "")).encode("utf-8")) != document["body_sha256"]:
            raise TikaSnapshotError("Tika body differs from the authoritative ledger")
        expected_attributes = {
            "extracted_body_sha256": document["body_sha256"],
            "media_type": document["media_type"],
            "raw_bytes": document["raw_bytes"],
            "raw_sha256": document["raw_sha256"],
            "source_locator": document["source_locator"],
            "tika_handler": _handler(sources[document["source_id"]]),
            "tika_metadata_sha256": document["metadata_sha256"],
            "tika_version": TIKA_VERSION,
            "title": document["title"],
        }
        if record.get("attributes") != expected_attributes:
            raise TikaSnapshotError("Tika provenance differs from the authoritative ledger")
    return {
        "algorithm": index["algorithm"],
        "documents": len(rows),
        "plan_sha256": index["plan_sha256"],
        "sources": len(sources),
        "tika_jar_tree_sha256": toolchain["tika_jar_tree_sha256"],
        "tika_version": TIKA_VERSION,
    }
