#!/usr/bin/env python3
"""Validate and search an immutable embedding-enabled Semantic OKF snapshot."""

from __future__ import annotations

import hashlib
import importlib
import importlib.metadata
import importlib.util
import json
import math
import os
import re
from collections import Counter
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Callable, Iterable, Iterator, Mapping, Sequence


INDEX_RELATIVE = "retrieval/index.json"
CHUNKS_RELATIVE = "retrieval/chunks.jsonl"
EMBEDDINGS_RELATIVE = "retrieval/embeddings.jsonl"
RETRIEVAL_BUILD_REPORT_RELATIVE = "retrieval/build-report.json"
RECORDS_RELATIVE = "semantic/records.jsonl"
SOURCE_MANIFEST_RELATIVE = "semantic/source-manifest.json"
BUILD_REPORT_RELATIVE = "semantic/build-report.json"
AUTHORITATIVE_READ_FILES = (
    "semantic/semantic-plan.json",
    "semantic/data.ttl",
    "semantic/ontology.ttl",
    "semantic/provenance.ttl",
    "semantic/shapes.ttl",
    "semantic/validation-report.ttl",
)

HEX_RE = re.compile(r"[0-9a-f]{64}")
TOKEN_RE = re.compile(r"\w+", flags=re.UNICODE)
MAX_DIMENSION = 4_096
NORMALIZED_TOLERANCE = 1e-6
VECTOR_PRECISION = 8
DERIVED_ROOTS = frozenset({"adaptive", "entity-graph", "retrieval", "ensemble"})
HASHING_MODEL_ID = "knowledge-hashing-embedding"
HASHING_REVISION = "1"
SENTENCE_TRANSFORMERS_VERSION = "5.6.0"
HUGGINGFACE_HUB_VERSION = "1.23.0"
ALLOWED_PROVIDERS = frozenset({"hashing", "sentence-transformers"})
IMMUTABLE_REVISION_RE = re.compile(r"[0-9a-fA-F]{7,64}")
HF_MODEL_ID_RE = re.compile(
    r"[A-Za-z0-9](?:[A-Za-z0-9._-]{0,94}[A-Za-z0-9])?/"
    r"[A-Za-z0-9](?:[A-Za-z0-9._-]{0,94}[A-Za-z0-9])?"
)
RETRIEVAL_ARTIFACT_NAMES = frozenset(
    {"index.json", "chunks.jsonl", "embeddings.jsonl", "build-report.json"}
)

INDEX_KEYS = {
    "schema_version",
    "authoritative",
    "core",
    "retrieval_plan_sha256",
    "selection",
    "chunking",
    "embedding",
    "artifacts",
    "chunk_count",
    "embedding_count",
}
CORE_KEYS = {"tree_sha256", "records_sha256", "record_count"}
SELECTION_KEYS = {
    "requested_source_ids",
    "eligible_source_ids",
    "excluded_source_ids",
    "input_count",
    "input_sha256",
}
CHUNKING_KEYS = {
    "implementation",
    "strategy",
    "buffer_size",
    "breakpoint_percentile_threshold",
}
EMBEDDING_KEYS = {
    "provider",
    "model_id",
    "revision",
    "dimension",
    "normalize",
    "vector_precision",
    "metric",
    "encoding",
}
ENCODING_KEYS = {"document", "query"}
ARTIFACT_KEYS = {"chunks", "embeddings"}
ARTIFACT_ENTRY_KEYS = {"path", "sha256", "count"}
CHUNK_KEYS = {
    "chunk_id",
    "source_id",
    "record_id",
    "concept_id",
    "concept_path",
    "record_sha256",
    "source_path",
    "locator",
    "ordinal",
    "text",
    "text_sha256",
}
EMBEDDING_ROW_KEYS = {"chunk_id", "vector"}


class SnapshotError(RuntimeError):
    """Describe a malformed, stale, or unsafe retrieval snapshot."""


class ProviderUnavailable(RuntimeError):
    """Describe an embedding provider that cannot run exactly as declared."""


@dataclass(frozen=True)
class LoadedSnapshot:
    """Validated in-memory retrieval view of one immutable snapshot."""

    root: Path
    index: Mapping[str, Any]
    records: Mapping[str, Mapping[str, Any]]
    chunks: tuple[Mapping[str, Any], ...]
    embeddings: Mapping[str, tuple[float, ...]]
    hashes: Mapping[str, str]


QueryEmbedder = Callable[[str, Mapping[str, Any]], Sequence[float]]


def canonical_json(value: Any) -> str:
    """Return the canonical JSON representation used by the builder contract."""

    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_bytes(value: bytes) -> str:
    """Return a lowercase SHA-256 digest."""

    return hashlib.sha256(value).hexdigest()


def sha256_json(value: Any) -> str:
    """Hash one canonical JSON value as UTF-8."""

    return sha256_bytes(canonical_json(value).encode("utf-8"))


def file_sha256(path: Path) -> str:
    """Hash one local file without changing it."""

    try:
        return sha256_bytes(path.read_bytes())
    except OSError as exc:
        raise SnapshotError(f"cannot hash {path}: {exc}") from exc


def _reject_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON number is forbidden: {value}")


def _object_without_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON object key: {key!r}")
        result[key] = value
    return result


def strict_json_loads(value: str) -> Any:
    """Parse strict JSON while rejecting duplicate keys and non-finite numbers."""

    return json.loads(
        value,
        object_pairs_hook=_object_without_duplicates,
        parse_constant=_reject_constant,
    )


def _json_object(path: Path, label: str) -> dict[str, Any]:
    try:
        value = strict_json_loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        raise SnapshotError(f"cannot read {label} at {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise SnapshotError(f"{label} at {path} must be a JSON object")
    return value


def _jsonl_objects(path: Path, label: str) -> list[dict[str, Any]]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        raise SnapshotError(f"cannot read {label} at {path}: {exc}") from exc
    if not lines:
        raise SnapshotError(f"{label} must not be empty")
    result: list[dict[str, Any]] = []
    for number, line in enumerate(lines, start=1):
        if not line.strip():
            raise SnapshotError(f"{label} line {number} must not be blank")
        try:
            value = strict_json_loads(line)
        except (json.JSONDecodeError, ValueError) as exc:
            raise SnapshotError(f"invalid {label} line {number}: {exc}") from exc
        if not isinstance(value, dict):
            raise SnapshotError(f"{label} line {number} must be an object")
        result.append(value)
    return result


def _require_keys(value: Mapping[str, Any], expected: set[str], label: str) -> None:
    actual = set(value)
    if actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        raise SnapshotError(f"{label} keys differ; missing={missing!r}, extra={extra!r}")


def _require_digest(value: Any, label: str) -> str:
    if not isinstance(value, str) or HEX_RE.fullmatch(value) is None:
        raise SnapshotError(f"{label} must be a lowercase SHA-256 digest")
    return value


def _require_nonempty_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise SnapshotError(f"{label} must be a nonempty string")
    return value


def _require_integer(value: Any, label: str, *, minimum: int = 0) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < minimum:
        raise SnapshotError(f"{label} must be an integer >= {minimum}")
    return value


def _sorted_unique_strings(value: Any, label: str) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) and item for item in value):
        raise SnapshotError(f"{label} must be an array of nonempty strings")
    if value != sorted(set(value)):
        raise SnapshotError(f"{label} must be sorted and unique")
    return value


def resolve_bundle_root(value: Path) -> Path:
    """Resolve a real directory without accepting a symlink at the public boundary."""

    expanded = value.expanduser()
    if expanded.is_symlink():
        raise SnapshotError(f"bundle root cannot be a symlink: {expanded}")
    try:
        resolved = expanded.resolve(strict=True)
    except OSError as exc:
        raise SnapshotError(f"bundle root does not exist: {expanded}") from exc
    if not resolved.is_dir():
        raise SnapshotError(f"bundle root must be a directory: {resolved}")
    return resolved


def _validate_retrieval_artifact_set(root: Path) -> None:
    """Require the published retrieval directory to contain only its four files."""

    retrieval = root / "retrieval"
    if retrieval.is_symlink() or not retrieval.is_dir():
        raise SnapshotError("retrieval must be a real directory")
    try:
        entries = list(retrieval.iterdir())
    except OSError as exc:
        raise SnapshotError(f"cannot inspect retrieval directory: {exc}") from exc
    actual = {entry.name for entry in entries}
    if actual != RETRIEVAL_ARTIFACT_NAMES:
        missing = sorted(RETRIEVAL_ARTIFACT_NAMES - actual)
        unknown = sorted(actual - RETRIEVAL_ARTIFACT_NAMES)
        raise SnapshotError(
            f"retrieval artifact set is closed; missing={missing!r}, unknown={unknown!r}"
        )
    if any(entry.is_symlink() or not entry.is_file() for entry in entries):
        raise SnapshotError("retrieval artifacts must be regular non-symlink files")


def snapshot_file(root: Path, relative: str) -> Path:
    """Resolve one regular file without following a bundle symlink."""

    if not isinstance(relative, str) or "\\" in relative:
        raise SnapshotError(f"unsafe snapshot path: {relative!r}")
    pure = PurePosixPath(relative)
    if pure.is_absolute() or not pure.parts or ".." in pure.parts:
        raise SnapshotError(f"unsafe snapshot path: {relative!r}")
    current = root
    for part in pure.parts:
        current = current / part
        if current.is_symlink():
            raise SnapshotError(f"snapshot path uses a symlink: {relative!r}")
    try:
        resolved = current.resolve(strict=True)
        resolved.relative_to(root)
    except (OSError, ValueError) as exc:
        raise SnapshotError(f"snapshot file escapes or is missing: {relative!r}") from exc
    if not resolved.is_file():
        raise SnapshotError(f"snapshot path is not a regular file: {relative!r}")
    return resolved


def concept_file(root: Path, relative: Any) -> Path:
    """Resolve one exact Markdown concept path from the record ledger."""

    if not isinstance(relative, str):
        raise SnapshotError("concept_path must be a string")
    pure = PurePosixPath(relative)
    if not pure.parts or pure.parts[0] != "concepts" or pure.suffix.lower() != ".md":
        raise SnapshotError(f"unsafe concept_path: {relative!r}")
    return snapshot_file(root, relative)


def core_tree_members(root: Path) -> list[dict[str, str]]:
    """Describe every non-retrieval core file by exact relative path and raw digest."""

    members: list[dict[str, str]] = []
    for path in sorted(root.rglob("*"), key=lambda item: item.relative_to(root).as_posix()):
        relative = path.relative_to(root)
        if relative.parts[0] in DERIVED_ROOTS:
            continue
        if path.is_symlink():
            raise SnapshotError(f"core tree contains a symlink: {relative.as_posix()}")
        if path.is_file():
            members.append({"path": relative.as_posix(), "sha256": file_sha256(path)})
    if not members:
        raise SnapshotError("core tree contains no files")
    return members


def core_tree_sha256(root: Path) -> str:
    """Hash the canonical pre-retrieval core-tree inventory."""

    return sha256_json(core_tree_members(root))


def _validate_build_report(root: Path) -> None:
    report = _json_object(snapshot_file(root, BUILD_REPORT_RELATIVE), "build report")
    if report.get("valid") is not True or report.get("status") != "pass":
        raise SnapshotError("build report does not identify a passing snapshot")


def _load_records(root: Path) -> dict[str, Mapping[str, Any]]:
    rows = _jsonl_objects(snapshot_file(root, RECORDS_RELATIVE), "record ledger")
    records: dict[str, Mapping[str, Any]] = {}
    for number, row in enumerate(rows, start=1):
        label = f"record ledger line {number}"
        concept_id = _require_nonempty_string(row.get("concept_id"), f"{label}.concept_id")
        if concept_id in records:
            raise SnapshotError(f"duplicate concept_id in record ledger: {concept_id!r}")
        _require_nonempty_string(row.get("source_id"), f"{label}.source_id")
        _require_nonempty_string(row.get("record_id"), f"{label}.record_id")
        _require_nonempty_string(row.get("source_path"), f"{label}.source_path")
        _require_nonempty_string(row.get("concept_type"), f"{label}.concept_type")
        _require_nonempty_string(row.get("body"), f"{label}.body")
        _require_digest(row.get("record_sha256"), f"{label}.record_sha256")
        concept_file(root, row.get("concept_path"))
        records[concept_id] = row
    return records


def _source_entries(root: Path) -> dict[str, Mapping[str, Any]]:
    manifest = _json_object(snapshot_file(root, SOURCE_MANIFEST_RELATIVE), "source manifest")
    sources = manifest.get("sources")
    if not isinstance(sources, list):
        raise SnapshotError("source manifest sources must be an array")
    result: dict[str, Mapping[str, Any]] = {}
    for number, entry in enumerate(sources, start=1):
        if not isinstance(entry, dict):
            raise SnapshotError(f"source manifest entry {number} must be an object")
        source_id = _require_nonempty_string(entry.get("id"), f"source entry {number}.id")
        content_sha256 = _require_digest(
            entry.get("content_sha256"), f"source entry {number}.content_sha256"
        )
        if source_id in result:
            raise SnapshotError(f"duplicate source manifest id: {source_id!r}")
        result[source_id] = {"id": source_id, "content_sha256": content_sha256}
    return result


def _validate_index_shape(index: Mapping[str, Any]) -> None:
    _require_keys(index, INDEX_KEYS, "retrieval index")
    if index.get("schema_version") != "1.0":
        raise SnapshotError("retrieval index schema_version must be '1.0'")
    if index.get("authoritative") is not False:
        raise SnapshotError("retrieval index must declare authoritative=false")
    _require_digest(index.get("retrieval_plan_sha256"), "retrieval_plan_sha256")

    core = index.get("core")
    if not isinstance(core, dict):
        raise SnapshotError("retrieval index core must be an object")
    _require_keys(core, CORE_KEYS, "retrieval index core")
    _require_digest(core.get("tree_sha256"), "core.tree_sha256")
    _require_digest(core.get("records_sha256"), "core.records_sha256")
    _require_integer(core.get("record_count"), "core.record_count", minimum=1)

    selection = index.get("selection")
    if not isinstance(selection, dict):
        raise SnapshotError("retrieval index selection must be an object")
    _require_keys(selection, SELECTION_KEYS, "retrieval index selection")
    requested = _sorted_unique_strings(
        selection.get("requested_source_ids"), "selection.requested_source_ids"
    )
    eligible = _sorted_unique_strings(
        selection.get("eligible_source_ids"), "selection.eligible_source_ids"
    )
    excluded = _sorted_unique_strings(
        selection.get("excluded_source_ids"), "selection.excluded_source_ids"
    )
    if set(eligible) & set(excluded):
        raise SnapshotError("eligible and excluded source IDs must be disjoint")
    if requested != eligible:
        raise SnapshotError("every requested source must be eligible in a completed projection")
    _require_integer(selection.get("input_count"), "selection.input_count", minimum=1)
    _require_digest(selection.get("input_sha256"), "selection.input_sha256")

    chunking = index.get("chunking")
    if not isinstance(chunking, dict):
        raise SnapshotError("retrieval index chunking must be an object")
    _require_keys(chunking, CHUNKING_KEYS, "retrieval index chunking")
    implementation = _require_nonempty_string(
        chunking.get("implementation"), "chunking.implementation"
    )
    if implementation not in {"native", "llamaindex"}:
        raise SnapshotError("chunking.implementation must be 'native' or 'llamaindex'")
    strategy = _require_nonempty_string(chunking.get("strategy"), "chunking.strategy")
    if strategy not in {"record", "semantic"}:
        raise SnapshotError("chunking.strategy must be 'record' or 'semantic'")
    if implementation == "llamaindex" and strategy != "semantic":
        raise SnapshotError("llamaindex chunking requires semantic strategy")
    buffer_size = _require_integer(
        chunking.get("buffer_size"), "chunking.buffer_size", minimum=1
    )
    if buffer_size > 16:
        raise SnapshotError("chunking.buffer_size must be an integer within 1-16")
    threshold_value = chunking.get("breakpoint_percentile_threshold")
    if (
        isinstance(threshold_value, bool)
        or not isinstance(threshold_value, (int, float))
        or not math.isfinite(float(threshold_value))
        or not 0.0 <= float(threshold_value) <= 100.0
    ):
        raise SnapshotError("chunking.breakpoint_percentile_threshold must be finite within 0-100")

    embedding = index.get("embedding")
    if not isinstance(embedding, dict):
        raise SnapshotError("retrieval index embedding must be an object")
    _require_keys(embedding, EMBEDDING_KEYS, "retrieval index embedding")
    provider = _require_nonempty_string(embedding.get("provider"), "embedding.provider")
    if provider not in ALLOWED_PROVIDERS:
        raise SnapshotError(f"embedding.provider is not allowlisted: {provider!r}")
    model_id = _require_nonempty_string(embedding.get("model_id"), "embedding.model_id")
    revision = _require_nonempty_string(embedding.get("revision"), "embedding.revision")
    if provider == "hashing" and (model_id, revision) != (HASHING_MODEL_ID, HASHING_REVISION):
        raise SnapshotError("hashing provider model_id/revision does not match hashing v1")
    if provider == "sentence-transformers":
        if (
            HF_MODEL_ID_RE.fullmatch(model_id) is None
            or ".." in model_id
            or "--" in model_id
        ):
            raise SnapshotError(
                "sentence-transformers model_id must be a valid namespace/repository ID"
            )
        if IMMUTABLE_REVISION_RE.fullmatch(revision) is None:
            raise SnapshotError(
                "sentence-transformers revision must be an immutable hexadecimal commit"
            )
    dimension = _require_integer(embedding.get("dimension"), "embedding.dimension", minimum=1)
    if dimension > MAX_DIMENSION:
        raise SnapshotError(f"embedding.dimension cannot exceed {MAX_DIMENSION}")
    if not isinstance(embedding.get("normalize"), bool):
        raise SnapshotError("embedding.normalize must be boolean")
    if embedding.get("vector_precision") != VECTOR_PRECISION:
        raise SnapshotError(f"embedding.vector_precision must be {VECTOR_PRECISION}")
    if embedding.get("metric") != "cosine":
        raise SnapshotError("embedding.metric must be 'cosine'")
    encoding = embedding.get("encoding")
    if not isinstance(encoding, dict):
        raise SnapshotError("embedding.encoding must be an object")
    _require_keys(encoding, ENCODING_KEYS, "embedding.encoding")
    if encoding != {"document": "symmetric", "query": "symmetric"}:
        raise SnapshotError("embedding encoding must declare symmetric document/query routes")

    artifacts = index.get("artifacts")
    if not isinstance(artifacts, dict):
        raise SnapshotError("retrieval index artifacts must be an object")
    _require_keys(artifacts, ARTIFACT_KEYS, "retrieval index artifacts")
    expected_paths = {"chunks": CHUNKS_RELATIVE, "embeddings": EMBEDDINGS_RELATIVE}
    for name, expected_path in expected_paths.items():
        entry = artifacts.get(name)
        if not isinstance(entry, dict):
            raise SnapshotError(f"artifacts.{name} must be an object")
        _require_keys(entry, ARTIFACT_ENTRY_KEYS, f"artifacts.{name}")
        if entry.get("path") != expected_path:
            raise SnapshotError(f"artifacts.{name}.path must be {expected_path!r}")
        _require_digest(entry.get("sha256"), f"artifacts.{name}.sha256")
        _require_integer(entry.get("count"), f"artifacts.{name}.count", minimum=1)

    _require_integer(index.get("chunk_count"), "chunk_count", minimum=1)
    _require_integer(index.get("embedding_count"), "embedding_count", minimum=1)


def _validate_locator(value: Any, label: str, strategy: str) -> Mapping[str, Any]:
    if not isinstance(value, dict):
        raise SnapshotError(f"{label} must be an object")
    if strategy == "record":
        if value.get("kind") != "record":
            raise SnapshotError(f"{label}.kind must be 'record' for record chunking")
        _require_keys(value, {"kind"}, label)
    elif strategy == "semantic":
        if value.get("kind") != "character-range":
            raise SnapshotError(
                f"{label}.kind must be 'character-range' for semantic chunking"
            )
        _require_keys(value, {"kind", "start", "end"}, label)
        start = _require_integer(value.get("start"), f"{label}.start")
        end = _require_integer(value.get("end"), f"{label}.end", minimum=1)
        if end <= start:
            raise SnapshotError(f"{label}.end must be greater than start")
    else:  # The closed index validator makes this unreachable.
        raise SnapshotError(f"unsupported chunking strategy: {strategy!r}")
    return value


def expected_chunk_id(row: Mapping[str, Any]) -> str:
    """Recompute the deterministic chunk identity declared by the builder contract."""

    identity = {
        "source_id": row["source_id"],
        "record_id": row["record_id"],
        "record_sha256": row["record_sha256"],
        "ordinal": row["ordinal"],
        "text_sha256": row["text_sha256"],
    }
    return "chunk-" + sha256_json(identity)[:32]


def _validate_chunks(
    root: Path,
    rows: list[dict[str, Any]],
    records: Mapping[str, Mapping[str, Any]],
    eligible_sources: set[str],
    strategy: str,
) -> tuple[Mapping[str, Any], ...]:
    previous = ""
    ordinals: dict[tuple[str, str], list[int]] = {}
    linked_records: set[tuple[str, str]] = set()
    for number, row in enumerate(rows, start=1):
        label = f"chunks line {number}"
        _require_keys(row, CHUNK_KEYS, label)
        chunk_id = _require_nonempty_string(row.get("chunk_id"), f"{label}.chunk_id")
        if re.fullmatch(r"chunk-[0-9a-f]{32}", chunk_id) is None:
            raise SnapshotError(f"{label}.chunk_id is invalid")
        if previous and chunk_id <= previous:
            raise SnapshotError("chunks.jsonl must be strictly ordered by unique chunk_id")
        previous = chunk_id
        source_id = _require_nonempty_string(row.get("source_id"), f"{label}.source_id")
        if source_id not in eligible_sources:
            raise SnapshotError(f"chunk belongs to an ineligible source: {source_id!r}")
        concept_id = _require_nonempty_string(row.get("concept_id"), f"{label}.concept_id")
        record = records.get(concept_id)
        if record is None:
            raise SnapshotError(f"orphan chunk references unknown concept_id: {concept_id!r}")
        for field in ("source_id", "record_id", "concept_path", "record_sha256", "source_path"):
            if row.get(field) != record.get(field):
                raise SnapshotError(f"{label}.{field} does not match the authoritative record")
        _require_digest(row.get("record_sha256"), f"{label}.record_sha256")
        concept_file(root, row.get("concept_path"))
        ordinal = _require_integer(row.get("ordinal"), f"{label}.ordinal")
        record_key = (source_id, str(row["record_id"]))
        ordinals.setdefault(record_key, []).append(ordinal)
        locator = _validate_locator(row.get("locator"), f"{label}.locator", strategy)
        text = _require_nonempty_string(row.get("text"), f"{label}.text")
        expected_text_hash = sha256_bytes(text.encode("utf-8"))
        if row.get("text_sha256") != expected_text_hash:
            raise SnapshotError(f"{label}.text_sha256 does not match text")
        body = record.get("body")
        if not isinstance(body, str) or not body:
            raise SnapshotError(f"{label} authoritative record body must be nonempty")
        if strategy == "semantic":
            start = int(locator["start"])
            end = int(locator["end"])
            if end > len(body) or body[start:end] != text:
                raise SnapshotError(f"{label}.locator does not identify the exact record text")
        elif text != body:
            raise SnapshotError(f"{label}.record locator text does not match the record body")
        if chunk_id != expected_chunk_id(row):
            raise SnapshotError(f"{label}.chunk_id does not match its deterministic identity")
        linked_records.add(record_key)

    for record_key, values in ordinals.items():
        if sorted(values) != list(range(len(values))):
            raise SnapshotError(f"chunk ordinals are not contiguous from zero for {record_key!r}")

    expected_records = {
        (str(record.get("source_id")), str(record.get("record_id")))
        for record in records.values()
        if record.get("source_id") in eligible_sources
    }
    if linked_records != expected_records:
        missing = sorted(expected_records - linked_records)
        extra = sorted(linked_records - expected_records)
        raise SnapshotError(f"chunk coverage differs from eligible records; missing={missing!r}, extra={extra!r}")
    return tuple(rows)


def _vector(
    value: Any,
    dimension: int,
    normalize: bool,
    label: str,
    *,
    enforce_precision: bool = True,
) -> tuple[float, ...]:
    if not isinstance(value, list) or len(value) != dimension:
        raise SnapshotError(f"{label} must contain exactly {dimension} values")
    result: list[float] = []
    for index, item in enumerate(value):
        if isinstance(item, bool) or not isinstance(item, (int, float)):
            raise SnapshotError(f"{label}[{index}] must be numeric")
        number = float(item)
        if not math.isfinite(number):
            raise SnapshotError(f"{label}[{index}] must be finite")
        if enforce_precision and isinstance(item, float) and round(item, VECTOR_PRECISION) != item:
            raise SnapshotError(f"{label}[{index}] exceeds vector_precision={VECTOR_PRECISION}")
        result.append(number)
    norm = math.sqrt(math.fsum(item * item for item in result))
    if norm == 0.0:
        raise SnapshotError(f"{label} cannot be a zero vector")
    if normalize and not math.isclose(
        norm, 1.0, rel_tol=NORMALIZED_TOLERANCE, abs_tol=NORMALIZED_TOLERANCE
    ):
        raise SnapshotError(f"{label} must be L2-normalized")
    return tuple(result)


def _canonicalize_query_vector(
    value: Sequence[float], dimension: int, normalize: bool
) -> tuple[float, ...]:
    """Apply the builder's frozen precision rules to ephemeral query vectors."""

    raw = _vector(
        list(value),
        dimension,
        normalize,
        "query vector",
        enforce_precision=False,
    )
    rounded = [round(item, VECTOR_PRECISION) for item in raw]
    if normalize:
        norm = math.sqrt(math.fsum(item * item for item in rounded))
        if norm == 0.0:
            raise SnapshotError("query vector quantization produced a zero vector")
        rounded = [round(item / norm, VECTOR_PRECISION) for item in rounded]
    return _vector(rounded, dimension, normalize, "query vector")


def _validate_embeddings(
    rows: list[dict[str, Any]],
    chunk_ids: Sequence[str],
    dimension: int,
    normalize: bool,
) -> dict[str, tuple[float, ...]]:
    result: dict[str, tuple[float, ...]] = {}
    previous = ""
    for number, row in enumerate(rows, start=1):
        label = f"embeddings line {number}"
        _require_keys(row, EMBEDDING_ROW_KEYS, label)
        chunk_id = _require_nonempty_string(row.get("chunk_id"), f"{label}.chunk_id")
        if previous and chunk_id <= previous:
            raise SnapshotError("embeddings.jsonl must be strictly ordered by unique chunk_id")
        previous = chunk_id
        result[chunk_id] = _vector(row.get("vector"), dimension, normalize, f"{label}.vector")
    if list(result) != list(chunk_ids):
        raise SnapshotError("embedding chunk IDs must exactly match chunks.jsonl order")
    return result


def load_snapshot(bundle: Path) -> LoadedSnapshot:
    """Validate every retrieval binding before exposing any search result."""

    root = resolve_bundle_root(bundle)
    _validate_retrieval_artifact_set(root)
    _validate_build_report(root)
    for relative in AUTHORITATIVE_READ_FILES:
        snapshot_file(root, relative)
    records_path = snapshot_file(root, RECORDS_RELATIVE)
    source_manifest_path = snapshot_file(root, SOURCE_MANIFEST_RELATIVE)
    index_path = snapshot_file(root, INDEX_RELATIVE)
    retrieval_report_path = snapshot_file(root, RETRIEVAL_BUILD_REPORT_RELATIVE)
    index = _json_object(index_path, "retrieval index")
    _validate_index_shape(index)

    core = index["core"]
    actual_records_hash = file_sha256(records_path)
    if core["records_sha256"] != actual_records_hash:
        raise SnapshotError("core.records_sha256 does not match semantic/records.jsonl")
    actual_tree_hash = core_tree_sha256(root)
    if core["tree_sha256"] != actual_tree_hash:
        raise SnapshotError("core.tree_sha256 does not match the immutable core tree")

    records = _load_records(root)
    if core["record_count"] != len(records):
        raise SnapshotError("core.record_count does not match semantic/records.jsonl")
    source_entries = _source_entries(root)

    selection = index["selection"]
    eligible = selection["eligible_source_ids"]
    eligible_set = set(eligible)
    missing_sources = sorted(set(eligible) - set(source_entries))
    if missing_sources:
        raise SnapshotError(f"eligible sources are absent from source manifest: {missing_sources!r}")
    excluded = selection["excluded_source_ids"]
    if excluded != sorted(set(source_entries) - set(eligible)):
        raise SnapshotError("selection.excluded_source_ids does not match the unselected sources")
    selected_inputs = [
        {
            "source_id": source_id,
            "content_sha256": source_entries[source_id]["content_sha256"],
        }
        for source_id in eligible
    ]
    if selection["input_count"] != len(selected_inputs):
        raise SnapshotError("selection.input_count does not match eligible source declarations")
    if selection["input_sha256"] != sha256_json(selected_inputs):
        raise SnapshotError("selection.input_sha256 does not match selected source declarations")

    artifacts = index["artifacts"]
    chunks_path = snapshot_file(root, artifacts["chunks"]["path"])
    embeddings_path = snapshot_file(root, artifacts["embeddings"]["path"])
    if artifacts["chunks"]["sha256"] != file_sha256(chunks_path):
        raise SnapshotError("declared chunks artifact hash does not match")
    if artifacts["embeddings"]["sha256"] != file_sha256(embeddings_path):
        raise SnapshotError("declared embeddings artifact hash does not match")

    chunk_rows = _jsonl_objects(chunks_path, "chunks.jsonl")
    embedding_rows = _jsonl_objects(embeddings_path, "embeddings.jsonl")
    if index["chunk_count"] != len(chunk_rows) or artifacts["chunks"]["count"] != len(chunk_rows):
        raise SnapshotError("chunk counts do not match chunks.jsonl")
    if (
        index["embedding_count"] != len(embedding_rows)
        or artifacts["embeddings"]["count"] != len(embedding_rows)
    ):
        raise SnapshotError("embedding counts do not match embeddings.jsonl")
    if len(chunk_rows) != len(embedding_rows):
        raise SnapshotError("every chunk must have exactly one embedding")

    chunks = _validate_chunks(
        root,
        chunk_rows,
        records,
        eligible_set,
        str(index["chunking"]["strategy"]),
    )
    embedding_config = index["embedding"]
    embeddings = _validate_embeddings(
        embedding_rows,
        [str(row["chunk_id"]) for row in chunks],
        int(embedding_config["dimension"]),
        bool(embedding_config["normalize"]),
    )
    selected_record_count = sum(
        1 for record in records.values() if record.get("source_id") in eligible_set
    )
    expected_report = {
        "schema_version": "1.0",
        "valid": True,
        "status": "pass",
        "errors": [],
        "warnings": [],
        "retrieval_plan_sha256": index["retrieval_plan_sha256"],
        "core": index["core"],
        "selection": index["selection"],
        "summary": {
            "inputs": len(selected_inputs),
            "records": selected_record_count,
            "chunks": len(chunk_rows),
            "embeddings": len(embedding_rows),
            "dimension": embedding_config["dimension"],
        },
        "artifacts": {
            "index": {
                "path": INDEX_RELATIVE,
                "sha256": file_sha256(index_path),
            },
            "chunks": {
                "path": CHUNKS_RELATIVE,
                "sha256": file_sha256(chunks_path),
                "count": len(chunk_rows),
            },
            "embeddings": {
                "path": EMBEDDINGS_RELATIVE,
                "sha256": file_sha256(embeddings_path),
                "count": len(embedding_rows),
            },
        },
    }
    if _json_object(retrieval_report_path, "retrieval build report") != expected_report:
        raise SnapshotError("retrieval build report differs from live validation")
    hashes = {
        "index_sha256": file_sha256(index_path),
        "core_tree_sha256": actual_tree_hash,
        "records_sha256": actual_records_hash,
        "source_manifest_sha256": file_sha256(source_manifest_path),
        "chunks_sha256": file_sha256(chunks_path),
        "embeddings_sha256": file_sha256(embeddings_path),
        "retrieval_build_report_sha256": file_sha256(retrieval_report_path),
        "retrieval_plan_sha256": str(index["retrieval_plan_sha256"]),
        "input_sha256": str(selection["input_sha256"]),
    }
    return LoadedSnapshot(root, index, records, chunks, embeddings, hashes)


def hashing_embedding(text: str, dimension: int, normalize: bool) -> tuple[float, ...]:
    """Encode text with the frozen, dependency-free knowledge hashing v1 contract."""

    values = [0.0] * dimension
    for token in TOKEN_RE.findall(text.casefold()):
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        bucket = int.from_bytes(digest[:8], "big") % dimension
        values[bucket] += 1.0 if digest[8] & 1 else -1.0
    norm = math.sqrt(math.fsum(item * item for item in values))
    if norm == 0.0:
        digest = hashlib.sha256(b"fallback\0" + text.encode("utf-8")).digest()
        values[int.from_bytes(digest[:8], "big") % dimension] = 1.0
        norm = 1.0
    if normalize:
        values = [item / norm for item in values]
    return tuple(values)


@contextmanager
def _offline_model_environment() -> Iterator[None]:
    names = ("HF_HUB_OFFLINE", "TRANSFORMERS_OFFLINE")
    previous = {name: os.environ.get(name) for name in names}
    try:
        for name in names:
            os.environ[name] = "1"
        yield
    finally:
        for name, value in previous.items():
            if value is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = value


def _sequence_from_model(value: Any) -> Sequence[float]:
    if hasattr(value, "tolist"):
        value = value.tolist()
    if isinstance(value, list) and len(value) == 1 and isinstance(value[0], list):
        value = value[0]
    if not isinstance(value, (list, tuple)):
        raise ProviderUnavailable("sentence-transformers returned an unsupported vector value")
    return value


def _resolve_sentence_transformer_snapshot(config: Mapping[str, Any]) -> Path:
    """Resolve only an already-cached Hugging Face snapshot at the declared commit."""

    model_id = str(config.get("model_id", ""))
    revision = str(config.get("revision", ""))
    if (
        HF_MODEL_ID_RE.fullmatch(model_id) is None
        or ".." in model_id
        or "--" in model_id
        or IMMUTABLE_REVISION_RE.fullmatch(revision) is None
    ):
        raise ProviderUnavailable("the declared Hugging Face model identity is invalid")
    try:
        version = importlib.metadata.version("huggingface-hub")
        if version != HUGGINGFACE_HUB_VERSION:
            raise ProviderUnavailable(
                f"huggingface-hub {HUGGINGFACE_HUB_VERSION} is required, found {version}"
            )
        module = importlib.import_module("huggingface_hub")
        snapshot_download = getattr(module, "snapshot_download")
    except importlib.metadata.PackageNotFoundError as exc:
        raise ProviderUnavailable(
            f"huggingface-hub {HUGGINGFACE_HUB_VERSION} is not installed "
            "in the active environment"
        ) from exc
    except (ImportError, AttributeError) as exc:
        raise ProviderUnavailable("huggingface-hub cannot be imported") from exc
    try:
        with _offline_model_environment():
            value = snapshot_download(
                repo_id=model_id,
                revision=revision,
                local_files_only=True,
            )
        if not isinstance(value, (str, os.PathLike)):
            raise TypeError("snapshot_download returned a non-path value")
        resolved = Path(value).expanduser().resolve(strict=True)
        if not resolved.is_dir():
            raise OSError("resolved snapshot is not a directory")
    except Exception as exc:
        raise ProviderUnavailable(
            "the exact Hugging Face model snapshot is unavailable locally"
        ) from exc
    if resolved.name.lower() != revision.lower():
        raise ProviderUnavailable(
            "the cached Hugging Face snapshot does not match the declared revision"
        )
    return resolved


def sentence_transformer_embedding(text: str, config: Mapping[str, Any]) -> Sequence[float]:
    """Load the exact local model revision with network and remote code disabled."""

    try:
        version = importlib.metadata.version("sentence-transformers")
        if version != SENTENCE_TRANSFORMERS_VERSION:
            raise ProviderUnavailable(
                "sentence-transformers "
                f"{SENTENCE_TRANSFORMERS_VERSION} is required, found {version}"
            )
        module = importlib.import_module("sentence_transformers")
        model_class = getattr(module, "SentenceTransformer")
    except importlib.metadata.PackageNotFoundError as exc:
        raise ProviderUnavailable(
            f"sentence-transformers {SENTENCE_TRANSFORMERS_VERSION} is not installed "
            "in the active environment"
        ) from exc
    except (ImportError, AttributeError) as exc:
        raise ProviderUnavailable("sentence-transformers cannot be imported") from exc
    try:
        snapshot = _resolve_sentence_transformer_snapshot(config)
        with _offline_model_environment():
            model = model_class(
                str(snapshot),
                device="cpu",
                local_files_only=True,
                trust_remote_code=False,
            )
            encoding = config["encoding"]["query"]
            kwargs = {
                "normalize_embeddings": bool(config["normalize"]),
                "show_progress_bar": False,
                "convert_to_numpy": True,
            }
            if encoding == "query" and callable(getattr(model, "encode_query", None)):
                value = model.encode_query([text], **kwargs)
            else:
                value = model.encode([text], **kwargs)
    except Exception as exc:
        raise ProviderUnavailable(
            "the exact sentence-transformers model revision is unavailable locally"
        ) from exc
    return _sequence_from_model(value)


def query_embedding(
    text: str,
    config: Mapping[str, Any],
    *,
    embedder: QueryEmbedder | None = None,
) -> tuple[float, ...]:
    """Encode a query through an injected test adapter or an allowlisted provider."""

    if embedder is not None:
        try:
            value = embedder(text, config)
        except ProviderUnavailable:
            raise
        except Exception as exc:
            raise ProviderUnavailable(f"injected embedding provider failed: {exc}") from exc
    elif config["provider"] == "hashing":
        value = hashing_embedding(text, int(config["dimension"]), bool(config["normalize"]))
    elif config["provider"] == "sentence-transformers":
        value = sentence_transformer_embedding(text, config)
    else:  # The index validator makes this unreachable.
        raise ProviderUnavailable(f"unsupported embedding provider: {config['provider']!r}")
    try:
        return _canonicalize_query_vector(
            value,
            int(config["dimension"]),
            bool(config["normalize"]),
        )
    except SnapshotError as exc:
        raise ProviderUnavailable(f"embedding provider returned an invalid query vector: {exc}") from exc


def _tokens(value: str) -> tuple[str, ...]:
    return tuple(TOKEN_RE.findall(value.casefold()))


def _eligible_chunks(
    snapshot: LoadedSnapshot,
    *,
    source_ids: Iterable[str] = (),
    concept_ids: Iterable[str] = (),
    concept_types: Iterable[str] = (),
) -> list[Mapping[str, Any]]:
    source_filter = set(source_ids)
    concept_filter = set(concept_ids)
    type_filter = set(concept_types)
    result: list[Mapping[str, Any]] = []
    for chunk in snapshot.chunks:
        record = snapshot.records[str(chunk["concept_id"])]
        if source_filter and chunk["source_id"] not in source_filter:
            continue
        if concept_filter and chunk["concept_id"] not in concept_filter:
            continue
        if type_filter and record.get("concept_type") not in type_filter:
            continue
        result.append(chunk)
    return result


def lexical_ranking(
    chunks: Sequence[Mapping[str, Any]], query: str
) -> tuple[dict[str, float], dict[str, int]]:
    """Rank arbitrary Unicode chunk text with deterministic dependency-free BM25."""

    query_tokens = tuple(dict.fromkeys(_tokens(query)))
    if not query_tokens or not chunks:
        return {}, {}
    documents = {str(chunk["chunk_id"]): _tokens(str(chunk["text"])) for chunk in chunks}
    lengths = {chunk_id: len(tokens) for chunk_id, tokens in documents.items()}
    average = math.fsum(lengths.values()) / len(lengths) or 1.0
    frequencies = {chunk_id: Counter(tokens) for chunk_id, tokens in documents.items()}
    document_frequency = {
        token: sum(token in frequencies[chunk_id] for chunk_id in documents)
        for token in query_tokens
    }
    k1 = 1.5
    b = 0.75
    scores: dict[str, float] = {}
    for chunk_id in documents:
        score = 0.0
        for token in query_tokens:
            tf = frequencies[chunk_id][token]
            df = document_frequency[token]
            if not tf or not df:
                continue
            inverse = math.log(1.0 + (len(documents) - df + 0.5) / (df + 0.5))
            denominator = tf + k1 * (1.0 - b + b * lengths[chunk_id] / average)
            score += inverse * (tf * (k1 + 1.0)) / denominator
        if score > 0.0:
            scores[chunk_id] = round(score, 12)
    ordered = sorted(scores, key=lambda chunk_id: (-scores[chunk_id], chunk_id))
    return scores, {chunk_id: rank for rank, chunk_id in enumerate(ordered, start=1)}


def _cosine(left: Sequence[float], right: Sequence[float]) -> float:
    numerator = math.fsum(a * b for a, b in zip(left, right, strict=True))
    left_norm = math.sqrt(math.fsum(item * item for item in left))
    right_norm = math.sqrt(math.fsum(item * item for item in right))
    if left_norm == 0.0 or right_norm == 0.0:
        raise SnapshotError("cosine similarity cannot use a zero vector")
    return numerator / (left_norm * right_norm)


def vector_ranking(
    snapshot: LoadedSnapshot,
    chunks: Sequence[Mapping[str, Any]],
    query_vector: Sequence[float],
) -> tuple[dict[str, float], dict[str, int]]:
    """Run an exact cosine scan with a stable chunk-ID tie break."""

    scores = {
        str(chunk["chunk_id"]): round(
            _cosine(query_vector, snapshot.embeddings[str(chunk["chunk_id"])]), 12
        )
        for chunk in chunks
    }
    ordered = sorted(scores, key=lambda chunk_id: (-scores[chunk_id], chunk_id))
    return scores, {chunk_id: rank for rank, chunk_id in enumerate(ordered, start=1)}


def hybrid_ranking(
    lexical_ranks: Mapping[str, int],
    vector_ranks: Mapping[str, int],
    *,
    constant: int = 60,
) -> tuple[dict[str, float], dict[str, int]]:
    """Fuse lexical and vector ranks with deterministic reciprocal-rank fusion."""

    identifiers = set(lexical_ranks) | set(vector_ranks)
    scores = {
        chunk_id: round(
            (1.0 / (constant + lexical_ranks[chunk_id]) if chunk_id in lexical_ranks else 0.0)
            + (1.0 / (constant + vector_ranks[chunk_id]) if chunk_id in vector_ranks else 0.0),
            12,
        )
        for chunk_id in identifiers
    }
    ordered = sorted(scores, key=lambda chunk_id: (-scores[chunk_id], chunk_id))
    return scores, {chunk_id: rank for rank, chunk_id in enumerate(ordered, start=1)}


def _hit(
    snapshot: LoadedSnapshot,
    chunk: Mapping[str, Any],
    rank: int,
    lexical_scores: Mapping[str, float],
    lexical_ranks: Mapping[str, int],
    vector_scores: Mapping[str, float],
    vector_ranks: Mapping[str, int],
    hybrid_scores: Mapping[str, float],
) -> dict[str, Any]:
    chunk_id = str(chunk["chunk_id"])
    record = snapshot.records[str(chunk["concept_id"])]
    return {
        "rank": rank,
        "chunk_id": chunk_id,
        "source_id": chunk["source_id"],
        "record_id": chunk["record_id"],
        "record_sha256": chunk["record_sha256"],
        "concept_id": chunk["concept_id"],
        "concept_type": record.get("concept_type"),
        "concept_path": chunk["concept_path"],
        "source_path": chunk["source_path"],
        "locator": chunk["locator"],
        "ordinal": chunk["ordinal"],
        "text": chunk["text"],
        "text_sha256": chunk["text_sha256"],
        "scores": {
            "lexical": lexical_scores.get(chunk_id),
            "vector": vector_scores.get(chunk_id),
            "hybrid": hybrid_scores.get(chunk_id),
        },
        "ranks": {
            "lexical": lexical_ranks.get(chunk_id),
            "vector": vector_ranks.get(chunk_id),
        },
    }


def inspect_snapshot(snapshot: LoadedSnapshot) -> dict[str, Any]:
    """Return deterministic capabilities and immutable snapshot bindings."""

    embedding = snapshot.index["embedding"]
    provider = str(embedding["provider"])
    if provider == "hashing":
        provider_runtime = "available"
    elif importlib.util.find_spec("sentence_transformers") is None:
        provider_runtime = "optional-package-missing"
    else:
        provider_runtime = "local-model-required"
    return {
        "status": "pass",
        "mode": "inspect",
        "read_only": True,
        "discovery_only": True,
        "schema_version": snapshot.index["schema_version"],
        "authoritative": False,
        "counts": {
            "sources": snapshot.index["selection"]["input_count"],
            "records": snapshot.index["core"]["record_count"],
            "chunks": snapshot.index["chunk_count"],
            "embeddings": snapshot.index["embedding_count"],
        },
        "embedding": {
            **dict(embedding),
            "runtime": provider_runtime,
        },
        "chunking": dict(snapshot.index["chunking"]),
        "selection": dict(snapshot.index["selection"]),
        "hashes": dict(snapshot.hashes),
        "authoritative_layers": {
            "ledger": RECORDS_RELATIVE,
            "concepts": "concepts/",
            "data": "semantic/data.ttl",
            "ontology": "semantic/ontology.ttl",
            "provenance": "semantic/provenance.ttl",
            "shapes": "semantic/shapes.ttl",
            "validation": "semantic/validation-report.ttl",
        },
    }


def search_snapshot(
    snapshot: LoadedSnapshot,
    query: str,
    *,
    requested_mode: str,
    top_k: int,
    source_ids: Iterable[str] = (),
    concept_ids: Iterable[str] = (),
    concept_types: Iterable[str] = (),
    allow_fallback: bool = False,
    embedder: QueryEmbedder | None = None,
) -> dict[str, Any]:
    """Search validated chunks without treating retrieval scores as evidence."""

    if requested_mode not in {"auto", "lexical", "vector", "hybrid"}:
        raise ValueError(f"unsupported search mode: {requested_mode!r}")
    if not isinstance(query, str) or not query.strip():
        raise ValueError("--query must contain non-whitespace text")
    if len(query.encode("utf-8")) > 16 * 1024:
        raise ValueError("--query exceeds the 16 KiB limit")
    if not isinstance(top_k, int) or isinstance(top_k, bool) or not 1 <= top_k <= 1000:
        raise ValueError("--top-k must be between 1 and 1000")

    source_values = tuple(sorted(set(source_ids)))
    concept_values = tuple(sorted(set(concept_ids)))
    type_values = tuple(sorted(set(concept_types)))
    chunks = _eligible_chunks(
        snapshot,
        source_ids=source_values,
        concept_ids=concept_values,
        concept_types=type_values,
    )
    lexical_scores: dict[str, float] = {}
    lexical_ranks: dict[str, int] = {}
    vector_scores: dict[str, float] = {}
    vector_ranks: dict[str, int] = {}
    hybrid_scores: dict[str, float] = {}
    effective_mode = "hybrid" if requested_mode == "auto" else requested_mode
    fallback: dict[str, str] | None = None

    if effective_mode in {"lexical", "hybrid"}:
        lexical_scores, lexical_ranks = lexical_ranking(chunks, query)
    if effective_mode in {"vector", "hybrid"}:
        try:
            vector = query_embedding(query, snapshot.index["embedding"], embedder=embedder)
            vector_scores, vector_ranks = vector_ranking(snapshot, chunks, vector)
        except ProviderUnavailable as exc:
            if requested_mode == "auto" or allow_fallback:
                if not lexical_ranks:
                    lexical_scores, lexical_ranks = lexical_ranking(chunks, query)
                fallback = {
                    "code": "embedding-provider-unavailable",
                    "from": effective_mode,
                    "to": "lexical",
                    "reason": str(exc),
                }
                effective_mode = "lexical"
                vector_scores = {}
                vector_ranks = {}
            else:
                raise

    if effective_mode == "hybrid":
        hybrid_scores, final_ranks = hybrid_ranking(lexical_ranks, vector_ranks)
    elif effective_mode == "vector":
        final_ranks = vector_ranks
    else:
        final_ranks = lexical_ranks

    chunk_by_id = {str(chunk["chunk_id"]): chunk for chunk in chunks}
    ordered_ids = sorted(final_ranks, key=lambda chunk_id: (final_ranks[chunk_id], chunk_id))[:top_k]
    hits = [
        _hit(
            snapshot,
            chunk_by_id[chunk_id],
            rank,
            lexical_scores,
            lexical_ranks,
            vector_scores,
            vector_ranks,
            hybrid_scores,
        )
        for rank, chunk_id in enumerate(ordered_ids, start=1)
    ]
    return {
        "status": "pass",
        "mode": "search",
        "requested_mode": requested_mode,
        "effective_mode": effective_mode,
        "fallback": fallback,
        "read_only": True,
        "discovery_only": True,
        "query": {
            "text": query,
            "top_k": top_k,
            "filters": {
                "source_ids": list(source_values),
                "concept_ids": list(concept_values),
                "concept_types": list(type_values),
            },
        },
        "hashes": dict(snapshot.hashes),
        "embedding": {
            "provider": snapshot.index["embedding"]["provider"],
            "model_id": snapshot.index["embedding"]["model_id"],
            "revision": snapshot.index["embedding"]["revision"],
            "dimension": snapshot.index["embedding"]["dimension"],
            "metric": snapshot.index["embedding"]["metric"],
        },
        "candidate_count": len(chunks),
        "returned": len(hits),
        "hits": hits,
    }
