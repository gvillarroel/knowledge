#!/usr/bin/env python3
"""Build and validate the non-authoritative retrieval projection.

The authoritative OKF/RDF snapshot is produced by the package-local core builder.
This module only derives hash-bound chunks and vectors from its record ledger.
"""

from __future__ import annotations

import hashlib
import importlib
import json
import math
import os
import re
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Protocol, Sequence

from _semantic_okf import canonical_json, validate_semantic_bundle


SCHEMA_VERSION = "1.0"
HASHING_MODEL_ID = "knowledge-hashing-embedding"
HASHING_REVISION = "1"
VECTOR_PRECISION = 8
DERIVED_ROOTS = frozenset({"adaptive", "entity-graph", "retrieval", "ensemble"})
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
HEX_64 = re.compile(r"^[0-9a-f]{64}$")
IMMUTABLE_REVISION = re.compile(r"^[0-9a-fA-F]{7,64}$")
HF_MODEL_ID_RE = re.compile(
    r"[A-Za-z0-9](?:[A-Za-z0-9._-]{0,94}[A-Za-z0-9])?/"
    r"[A-Za-z0-9](?:[A-Za-z0-9._-]{0,94}[A-Za-z0-9])?"
)
TOKEN = re.compile(r"\w+", flags=re.UNICODE)
SENTENCE_BOUNDARY = re.compile(r"(?<=[.!?])\s+|\n{2,}")


class RetrievalError(RuntimeError):
    """Describe a closed-plan, embedding, or retrieval-integrity failure."""


class Embedder(Protocol):
    """Minimal provider contract shared by native and LlamaIndex splitters."""

    dimension: int

    def encode(self, texts: Sequence[str]) -> list[list[float]]:
        """Encode texts in order without network or cache writes."""


@dataclass(frozen=True)
class RetrievalPlan:
    """Validated closed retrieval plan."""

    raw: dict[str, Any]
    source_ids: tuple[str, ...]
    implementation: str
    strategy: str
    buffer_size: int
    percentile: float
    provider: str
    model_id: str
    revision: str
    dimension: int
    normalize: bool

    @property
    def sha256(self) -> str:
        return sha256_canonical(self.raw)


def sha256_bytes(value: bytes) -> str:
    """Return a lowercase SHA-256 digest."""

    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    """Hash one file without normalizing its bytes."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_canonical(value: Any) -> str:
    """Hash canonical UTF-8 JSON."""

    return sha256_bytes(canonical_json(value).encode("utf-8"))


def strict_json_loads(payload: str, *, label: str) -> Any:
    """Parse JSON while rejecting duplicate keys and non-finite constants."""

    def reject_constant(value: str) -> None:
        raise RetrievalError(f"{label} contains non-finite JSON constant {value!r}")

    def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise RetrievalError(f"{label} contains duplicate object key {key!r}")
            result[key] = value
        return result

    try:
        return json.loads(
            payload,
            parse_constant=reject_constant,
            object_pairs_hook=reject_duplicate_keys,
        )
    except RetrievalError:
        raise
    except json.JSONDecodeError as exc:
        raise RetrievalError(f"cannot parse {label}: {exc}") from exc


def _require_exact_keys(value: Mapping[str, Any], expected: set[str], label: str) -> None:
    actual = set(value)
    if actual != expected:
        missing = sorted(expected - actual)
        unknown = sorted(actual - expected)
        raise RetrievalError(f"{label} keys are closed; missing={missing}, unknown={unknown}")


def _require_plain_int(value: Any, label: str, *, minimum: int, maximum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not minimum <= value <= maximum:
        raise RetrievalError(f"{label} must be an integer in [{minimum}, {maximum}]")
    return value


def _is_hugging_face_model_id(value: Any) -> bool:
    """Return whether a value is a closed Hugging Face namespace/repository ID."""

    return (
        isinstance(value, str)
        and HF_MODEL_ID_RE.fullmatch(value) is not None
        and ".." not in value
        and "--" not in value
    )


def load_plan(path: Path) -> RetrievalPlan:
    """Load and validate the closed retrieval-plan schema."""

    try:
        payload = strict_json_loads(path.read_text(encoding="utf-8"), label=str(path))
    except OSError as exc:
        raise RetrievalError(f"cannot read retrieval plan {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise RetrievalError("retrieval plan root must be an object")
    _require_exact_keys(payload, {"schema_version", "selection", "chunking", "embedding"}, "plan")
    if payload["schema_version"] != SCHEMA_VERSION:
        raise RetrievalError(f"plan.schema_version must be {SCHEMA_VERSION!r}")

    selection = payload["selection"]
    if not isinstance(selection, dict):
        raise RetrievalError("plan.selection must be an object")
    _require_exact_keys(selection, {"source_ids"}, "plan.selection")
    source_ids = selection["source_ids"]
    if (
        not isinstance(source_ids, list)
        or not source_ids
        or any(not isinstance(item, str) or not item for item in source_ids)
    ):
        raise RetrievalError("plan.selection.source_ids must be a non-empty string array")
    if source_ids != sorted(set(source_ids)):
        raise RetrievalError("plan.selection.source_ids must be sorted and unique")

    chunking = payload["chunking"]
    if not isinstance(chunking, dict):
        raise RetrievalError("plan.chunking must be an object")
    _require_exact_keys(
        chunking,
        {"implementation", "strategy", "buffer_size", "breakpoint_percentile_threshold"},
        "plan.chunking",
    )
    implementation = chunking["implementation"]
    strategy = chunking["strategy"]
    if implementation not in {"native", "llamaindex"}:
        raise RetrievalError("plan.chunking.implementation must be native or llamaindex")
    if strategy not in {"record", "semantic"}:
        raise RetrievalError("plan.chunking.strategy must be record or semantic")
    if implementation == "llamaindex" and strategy != "semantic":
        raise RetrievalError("llamaindex implementation is only valid with semantic strategy")
    buffer_size = _require_plain_int(
        chunking["buffer_size"], "plan.chunking.buffer_size", minimum=1, maximum=16
    )
    percentile = chunking["breakpoint_percentile_threshold"]
    if isinstance(percentile, bool) or not isinstance(percentile, (int, float)):
        raise RetrievalError("breakpoint percentile must be a finite number in [0, 100]")
    percentile = float(percentile)
    if not math.isfinite(percentile) or not 0.0 <= percentile <= 100.0:
        raise RetrievalError("breakpoint percentile must be a finite number in [0, 100]")

    embedding = payload["embedding"]
    if not isinstance(embedding, dict):
        raise RetrievalError("plan.embedding must be an object")
    _require_exact_keys(
        embedding,
        {"provider", "model_id", "revision", "dimension", "normalize"},
        "plan.embedding",
    )
    provider = embedding["provider"]
    model_id = embedding["model_id"]
    revision = embedding["revision"]
    if provider not in {"hashing", "sentence-transformers"}:
        raise RetrievalError("plan.embedding.provider must be hashing or sentence-transformers")
    if not isinstance(model_id, str) or not model_id:
        raise RetrievalError("plan.embedding.model_id must be a non-empty string")
    if not isinstance(revision, str) or not revision:
        raise RetrievalError("plan.embedding.revision must be a non-empty string")
    if provider == "hashing":
        if (model_id, revision) != (HASHING_MODEL_ID, HASHING_REVISION):
            raise RetrievalError(
                f"hashing provider requires model_id={HASHING_MODEL_ID!r} and revision={HASHING_REVISION!r}"
            )
    else:
        if not _is_hugging_face_model_id(model_id):
            raise RetrievalError(
                "sentence-transformers model_id must be a Hugging Face namespace/repository ID"
            )
        if not IMMUTABLE_REVISION.fullmatch(revision):
            raise RetrievalError(
                "sentence-transformers revision must be an immutable 7-64 digit hex commit"
            )
    dimension = _require_plain_int(
        embedding["dimension"], "plan.embedding.dimension", minimum=1, maximum=4096
    )
    normalize = embedding["normalize"]
    if not isinstance(normalize, bool):
        raise RetrievalError("plan.embedding.normalize must be boolean")

    return RetrievalPlan(
        raw=payload,
        source_ids=tuple(source_ids),
        implementation=implementation,
        strategy=strategy,
        buffer_size=buffer_size,
        percentile=percentile,
        provider=provider,
        model_id=model_id,
        revision=revision,
        dimension=dimension,
        normalize=normalize,
    )


class HashingEmbedder:
    """Portable symmetric signed-token hashing embedder."""

    def __init__(self, dimension: int, normalize: bool) -> None:
        self.dimension = dimension
        self.normalize = normalize

    def encode(self, texts: Sequence[str]) -> list[list[float]]:
        rows: list[list[float]] = []
        for text in texts:
            vector = [0.0] * self.dimension
            tokens = TOKEN.findall(text.casefold())
            for token in tokens:
                digest = hashlib.sha256(token.encode("utf-8")).digest()
                index = int.from_bytes(digest[:8], "big") % self.dimension
                vector[index] += 1.0 if digest[8] & 1 else -1.0
            norm = math.sqrt(sum(value * value for value in vector))
            if not tokens or norm == 0.0:
                digest = hashlib.sha256(b"fallback\0" + text.encode("utf-8")).digest()
                vector[int.from_bytes(digest[:8], "big") % self.dimension] = 1.0
                norm = 1.0
            if self.normalize:
                vector = [value / norm for value in vector]
            rows.append(vector)
        return rows


class SentenceTransformersEmbedder:
    """Explicit offline SentenceTransformers provider loaded only when selected."""

    def __init__(self, plan: RetrievalPlan) -> None:
        os.environ["HF_HUB_OFFLINE"] = "1"
        os.environ["TRANSFORMERS_OFFLINE"] = "1"
        try:
            hub_module = importlib.import_module("huggingface_hub")
        except ImportError as exc:
            raise RetrievalError(
                "sentence-transformers provider is unavailable; install scripts/requirements-sentence-transformers.txt"
            ) from exc
        try:
            snapshot = hub_module.snapshot_download(
                repo_id=plan.model_id,
                revision=plan.revision,
                local_files_only=True,
            )
        except Exception as exc:
            raise RetrievalError(
                "cannot resolve the pinned Hugging Face snapshot offline; pre-populate the explicit model cache"
            ) from exc
        try:
            snapshot_path = Path(snapshot).resolve(strict=True)
        except (OSError, TypeError) as exc:
            raise RetrievalError("the resolved Hugging Face snapshot path is unavailable") from exc
        if not snapshot_path.is_dir():
            raise RetrievalError("the resolved Hugging Face snapshot path is not a directory")
        if snapshot_path.name.lower() != plan.revision.lower():
            raise RetrievalError(
                "the resolved Hugging Face snapshot does not match the requested revision"
            )

        try:
            module = importlib.import_module("sentence_transformers")
        except ImportError as exc:
            raise RetrievalError(
                "sentence-transformers provider is unavailable; install scripts/requirements-sentence-transformers.txt"
            ) from exc
        try:
            self._model = module.SentenceTransformer(
                str(snapshot_path),
                local_files_only=True,
                trust_remote_code=False,
                device="cpu",
            )
        except Exception as exc:
            raise RetrievalError(
                "cannot open the pinned SentenceTransformers snapshot offline; pre-populate the explicit model cache"
            ) from exc
        self.dimension = plan.dimension
        self.normalize = plan.normalize

    def encode(self, texts: Sequence[str]) -> list[list[float]]:
        try:
            result = self._model.encode(
                list(texts),
                normalize_embeddings=self.normalize,
                convert_to_numpy=True,
                show_progress_bar=False,
            )
        except Exception as exc:
            raise RetrievalError(f"SentenceTransformers encoding failed: {exc}") from exc
        rows = [[float(value) for value in row] for row in result]
        _validate_vectors(rows, self.dimension, self.normalize, "provider output")
        return rows


def make_embedder(plan: RetrievalPlan) -> Embedder:
    """Instantiate only the explicitly selected local provider."""

    if plan.provider == "hashing":
        return HashingEmbedder(plan.dimension, plan.normalize)
    return SentenceTransformersEmbedder(plan)


def _validate_vectors(
    vectors: Sequence[Sequence[Any]], dimension: int, normalize: bool, label: str
) -> None:
    """Reject non-finite, zero, dimensionally invalid, or wrongly normalized vectors."""

    for ordinal, vector in enumerate(vectors):
        if len(vector) != dimension:
            raise RetrievalError(f"{label} vector {ordinal} has dimension {len(vector)}, expected {dimension}")
        if any(isinstance(value, bool) or not isinstance(value, (int, float)) for value in vector):
            raise RetrievalError(f"{label} vector {ordinal} contains a non-numeric value")
        values = [float(value) for value in vector]
        if any(not math.isfinite(value) for value in values):
            raise RetrievalError(f"{label} vector {ordinal} contains a non-finite value")
        norm = math.sqrt(sum(value * value for value in values))
        if norm == 0.0:
            raise RetrievalError(f"{label} vector {ordinal} is zero")
        if normalize and not math.isclose(norm, 1.0, rel_tol=1e-6, abs_tol=1e-6):
            raise RetrievalError(f"{label} vector {ordinal} is not L2 normalized")


def _cosine_distance(left: Sequence[float], right: Sequence[float]) -> float:
    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    if left_norm == 0.0 or right_norm == 0.0:
        raise RetrievalError("semantic splitter received a zero vector")
    similarity = sum(a * b for a, b in zip(left, right)) / (left_norm * right_norm)
    return 1.0 - max(-1.0, min(1.0, similarity))


def _percentile(values: Sequence[float], percentile: float) -> float:
    if not values:
        return math.inf
    ordered = sorted(values)
    position = (len(ordered) - 1) * percentile / 100.0
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    fraction = position - lower
    return ordered[lower] * (1.0 - fraction) + ordered[upper] * fraction


def _sentence_spans(text: str) -> list[tuple[int, int]]:
    spans: list[tuple[int, int]] = []
    cursor = 0
    for match in SENTENCE_BOUNDARY.finditer(text):
        start, end = cursor, match.start()
        while start < end and text[start].isspace():
            start += 1
        while end > start and text[end - 1].isspace():
            end -= 1
        if start < end:
            spans.append((start, end))
        cursor = match.end()
    start, end = cursor, len(text)
    while start < end and text[start].isspace():
        start += 1
    while end > start and text[end - 1].isspace():
        end -= 1
    if start < end:
        spans.append((start, end))
    return spans


def _native_semantic_ranges(text: str, plan: RetrievalPlan, embedder: Embedder) -> list[tuple[int, int]]:
    spans = _sentence_spans(text)
    if len(spans) <= 1:
        return spans or [(0, len(text))]
    windows: list[str] = []
    for index in range(len(spans)):
        first = max(0, index - plan.buffer_size)
        last = min(len(spans), index + plan.buffer_size + 1)
        windows.append(text[spans[first][0] : spans[last - 1][1]])
    vectors = embedder.encode(windows)
    _validate_vectors(vectors, plan.dimension, plan.normalize, "splitter")
    distances = [_cosine_distance(vectors[index], vectors[index + 1]) for index in range(len(vectors) - 1)]
    threshold = _percentile(distances, plan.percentile)
    breaks = {index for index, value in enumerate(distances) if value > threshold}
    ranges: list[tuple[int, int]] = []
    first = 0
    for index in range(len(spans) - 1):
        if index in breaks:
            ranges.append((spans[first][0], spans[index][1]))
            first = index + 1
    ranges.append((spans[first][0], spans[-1][1]))
    return ranges


def _llamaindex_semantic_ranges(
    text: str, plan: RetrievalPlan, embedder: Embedder
) -> list[tuple[int, int]]:
    """Split with LlamaIndex while supplying the selected offline embedder explicitly."""

    try:
        schema_module = importlib.import_module("llama_index.core.schema")
        parser_module = importlib.import_module("llama_index.core.node_parser")
        embeddings_module = importlib.import_module("llama_index.core.base.embeddings.base")
    except ImportError as exc:
        raise RetrievalError(
            "llamaindex implementation is unavailable; install scripts/requirements-llamaindex.txt"
        ) from exc

    base_embedding = embeddings_module.BaseEmbedding

    class ExplicitEmbedding(base_embedding):  # type: ignore[misc, valid-type]
        """Bridge the closed provider contract into LlamaIndex."""

        model_name: str = plan.model_id

        def _get_query_embedding(self, query: str) -> list[float]:
            return embedder.encode([query])[0]

        async def _aget_query_embedding(self, query: str) -> list[float]:
            return self._get_query_embedding(query)

        def _get_text_embedding(self, value: str) -> list[float]:
            return embedder.encode([value])[0]

        def _get_text_embeddings(self, values: list[str]) -> list[list[float]]:
            return embedder.encode(values)

    try:
        parser = parser_module.SemanticSplitterNodeParser(
            embed_model=ExplicitEmbedding(),
            buffer_size=plan.buffer_size,
            breakpoint_percentile_threshold=plan.percentile,
        )
        document = schema_module.Document(text=text)
        nodes = parser.get_nodes_from_documents([document], show_progress=False)
    except Exception as exc:
        raise RetrievalError(f"LlamaIndex semantic splitting failed: {exc}") from exc
    ranges: list[tuple[int, int]] = []
    cursor = 0
    for node in nodes:
        value = str(node.get_content()).strip()
        if not value:
            continue
        start = text.find(value, cursor)
        if start < 0:
            raise RetrievalError("LlamaIndex returned text that cannot be located in its source record")
        end = start + len(value)
        ranges.append((start, end))
        cursor = end
    if not ranges:
        raise RetrievalError("LlamaIndex returned no chunks for a non-empty record")
    return ranges


def _canonicalize_vectors(vectors: Sequence[Sequence[float]], normalize: bool) -> list[list[float]]:
    """Quantize provider output to a hardware-stable JSON precision."""

    result: list[list[float]] = []
    for vector in vectors:
        values = [round(float(value), VECTOR_PRECISION) for value in vector]
        if normalize:
            norm = math.sqrt(sum(value * value for value in values))
            if norm == 0.0:
                raise RetrievalError("quantization produced a zero vector")
            values = [round(value / norm, VECTOR_PRECISION) for value in values]
        result.append(values)
    return result


def _chunk_id(row: Mapping[str, Any]) -> str:
    identity = {
        "source_id": row["source_id"],
        "record_id": row["record_id"],
        "record_sha256": row["record_sha256"],
        "ordinal": row["ordinal"],
        "text_sha256": row["text_sha256"],
    }
    return "chunk-" + sha256_canonical(identity)[:32]


def _chunk_rows(
    records: Sequence[dict[str, Any]], plan: RetrievalPlan, embedder: Embedder
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for record in records:
        body = record.get("body")
        if not isinstance(body, str) or not body:
            raise RetrievalError(
                f"selected record {record.get('source_id')!r}/{record.get('record_id')!r} has no text"
            )
        if plan.strategy == "record":
            ranges = [(0, len(body))]
        elif plan.implementation == "native":
            ranges = _native_semantic_ranges(body, plan, embedder)
        else:
            ranges = _llamaindex_semantic_ranges(body, plan, embedder)
        for ordinal, (start, end) in enumerate(ranges):
            text = body[start:end]
            locator: dict[str, Any]
            if plan.strategy == "record":
                locator = {"kind": "record"}
            else:
                locator = {"kind": "character-range", "start": start, "end": end}
            row = {
                "chunk_id": "",
                "source_id": record["source_id"],
                "record_id": record["record_id"],
                "concept_id": record["concept_id"],
                "concept_path": record["concept_path"],
                "record_sha256": record["record_sha256"],
                "source_path": record["source_path"],
                "locator": locator,
                "ordinal": ordinal,
                "text": text,
                "text_sha256": sha256_bytes(text.encode("utf-8")),
            }
            row["chunk_id"] = _chunk_id(row)
            rows.append(row)
    rows.sort(key=lambda row: row["chunk_id"])
    if len({row["chunk_id"] for row in rows}) != len(rows):
        raise RetrievalError("derived chunk IDs are not unique")
    return rows


def _read_jsonl(path: Path, *, label: str) -> list[dict[str, Any]]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise RetrievalError(f"cannot read {label}: {exc}") from exc
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(lines, start=1):
        if not line:
            raise RetrievalError(f"{label}:{line_number} is blank")
        value = strict_json_loads(line, label=f"{label}:{line_number}")
        if not isinstance(value, dict):
            raise RetrievalError(f"{label}:{line_number} must be an object")
        if line != canonical_json(value):
            raise RetrievalError(f"{label}:{line_number} is not canonical JSON")
        rows.append(value)
    return rows


def _write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _write_jsonl(path: Path, rows: Iterable[Mapping[str, Any]]) -> None:
    path.write_text(
        "".join(canonical_json(row) + "\n" for row in rows),
        encoding="utf-8",
        newline="\n",
    )


def _core_inventory(root: Path) -> list[dict[str, str]]:
    files = [
        path
        for path in root.rglob("*")
        if path.is_file() and path.relative_to(root).parts[0] not in DERIVED_ROOTS
    ]
    return [
        {"path": path.relative_to(root).as_posix(), "sha256": sha256_file(path)}
        for path in sorted(files, key=lambda item: item.relative_to(root).as_posix())
    ]


def _core_tree_sha256(root: Path) -> str:
    return sha256_canonical(_core_inventory(root))


def _artifact(path: str, root: Path, count: int | None = None) -> dict[str, Any]:
    result: dict[str, Any] = {"path": path, "sha256": sha256_file(root / path)}
    if count is not None:
        result["count"] = count
    return result


def _load_core(root: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    records = _read_jsonl(root / "semantic" / "records.jsonl", label="semantic/records.jsonl")
    try:
        manifest = strict_json_loads(
            (root / "semantic" / "source-manifest.json").read_text(encoding="utf-8"),
            label="semantic/source-manifest.json",
        )
    except OSError as exc:
        raise RetrievalError(f"cannot read semantic/source-manifest.json: {exc}") from exc
    if not isinstance(manifest, dict) or not isinstance(manifest.get("sources"), list):
        raise RetrievalError("semantic/source-manifest.json has no sources array")
    sources = manifest["sources"]
    if any(not isinstance(source, dict) for source in sources):
        raise RetrievalError("semantic/source-manifest.json contains a non-object source")
    return records, sources


def _selection(
    records: Sequence[dict[str, Any]], sources: Sequence[dict[str, Any]], plan: RetrievalPlan
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    source_by_id = {source.get("id"): source for source in sources if isinstance(source.get("id"), str)}
    unknown = sorted(set(plan.source_ids) - set(source_by_id))
    if unknown:
        raise RetrievalError(f"retrieval plan selects unknown source IDs: {unknown}")
    selected = [record for record in records if record.get("source_id") in plan.source_ids]
    eligible = sorted({str(record["source_id"]) for record in selected})
    missing = sorted(set(plan.source_ids) - set(eligible))
    if missing:
        raise RetrievalError(f"selected source IDs produced no eligible records: {missing}")
    excluded = sorted(set(source_by_id) - set(plan.source_ids))
    inventory = [
        {"source_id": source_id, "content_sha256": source_by_id[source_id].get("content_sha256")}
        for source_id in eligible
    ]
    if any(not HEX_64.fullmatch(str(row["content_sha256"])) for row in inventory):
        raise RetrievalError("selected source inventory contains an invalid content digest")
    selection = {
        "requested_source_ids": list(plan.source_ids),
        "eligible_source_ids": eligible,
        "excluded_source_ids": excluded,
        "input_count": len(inventory),
        "input_sha256": sha256_canonical(inventory),
    }
    selected.sort(key=lambda row: (str(row.get("source_id")), str(row.get("record_id"))))
    return selected, selection


def build_projection(root: Path, plan_path: Path) -> dict[str, Any]:
    """Add a complete retrieval projection to an already validated core snapshot."""

    plan = load_plan(plan_path)
    records, sources = _load_core(root)
    selected_records, selection = _selection(records, sources, plan)
    embedder = make_embedder(plan)
    chunks = _chunk_rows(selected_records, plan, embedder)
    vectors = _canonicalize_vectors(embedder.encode([row["text"] for row in chunks]), plan.normalize)
    _validate_vectors(vectors, plan.dimension, plan.normalize, "serialized")
    embeddings = [
        {"chunk_id": chunk["chunk_id"], "vector": vector}
        for chunk, vector in zip(chunks, vectors)
    ]

    retrieval = root / "retrieval"
    if retrieval.exists():
        raise RetrievalError("core candidate unexpectedly contains retrieval artifacts")
    retrieval.mkdir()
    _write_jsonl(retrieval / "chunks.jsonl", chunks)
    _write_jsonl(retrieval / "embeddings.jsonl", embeddings)

    core = {
        "tree_sha256": _core_tree_sha256(root),
        "records_sha256": sha256_file(root / "semantic" / "records.jsonl"),
        "record_count": len(records),
    }
    chunking = {
        "implementation": plan.implementation,
        "strategy": plan.strategy,
        "buffer_size": plan.buffer_size,
        "breakpoint_percentile_threshold": plan.percentile,
    }
    embedding = {
        "provider": plan.provider,
        "model_id": plan.model_id,
        "revision": plan.revision,
        "dimension": plan.dimension,
        "normalize": plan.normalize,
        "metric": "cosine",
        "encoding": {"document": "symmetric", "query": "symmetric"},
        "vector_precision": VECTOR_PRECISION,
    }
    index = {
        "schema_version": SCHEMA_VERSION,
        "authoritative": False,
        "core": core,
        "retrieval_plan_sha256": plan.sha256,
        "selection": selection,
        "chunking": chunking,
        "embedding": embedding,
        "artifacts": {
            "chunks": _artifact("retrieval/chunks.jsonl", root, len(chunks)),
            "embeddings": _artifact("retrieval/embeddings.jsonl", root, len(embeddings)),
        },
        "chunk_count": len(chunks),
        "embedding_count": len(embeddings),
    }
    _write_json(retrieval / "index.json", index)
    initial = validate_retrieval_bundle(root, require_build_report=False)
    if not initial["valid"]:
        messages = "; ".join(error["message"] for error in initial["errors"])
        raise RetrievalError("retrieval projection failed validation: " + messages)
    report = {
        "schema_version": SCHEMA_VERSION,
        "valid": True,
        "status": "pass",
        "errors": [],
        "warnings": [],
        "retrieval_plan_sha256": plan.sha256,
        "core": core,
        "selection": selection,
        "summary": {
            "inputs": selection["input_count"],
            "records": len(selected_records),
            "chunks": len(chunks),
            "embeddings": len(embeddings),
            "dimension": plan.dimension,
        },
        "artifacts": {
            "index": _artifact("retrieval/index.json", root),
            "chunks": index["artifacts"]["chunks"],
            "embeddings": index["artifacts"]["embeddings"],
        },
    }
    _write_json(retrieval / "build-report.json", report)
    final = validate_retrieval_bundle(root)
    if not final["valid"]:
        messages = "; ".join(error["message"] for error in final["errors"])
        raise RetrievalError("completed retrieval bundle failed validation: " + messages)
    return report


def _expect_digest(value: Any, label: str) -> str:
    if not isinstance(value, str) or not HEX_64.fullmatch(value):
        raise RetrievalError(f"{label} must be a lowercase SHA-256 digest")
    return value


def _validate_index_shape(index: Any) -> dict[str, Any]:
    if not isinstance(index, dict):
        raise RetrievalError("retrieval/index.json root must be an object")
    _require_exact_keys(index, INDEX_KEYS, "retrieval index")
    if index["schema_version"] != SCHEMA_VERSION or index["authoritative"] is not False:
        raise RetrievalError("retrieval index version/authority marker is invalid")
    core = index["core"]
    if not isinstance(core, dict):
        raise RetrievalError("retrieval index core must be an object")
    _require_exact_keys(core, {"tree_sha256", "records_sha256", "record_count"}, "index.core")
    _expect_digest(core["tree_sha256"], "index.core.tree_sha256")
    _expect_digest(core["records_sha256"], "index.core.records_sha256")
    _require_plain_int(core["record_count"], "index.core.record_count", minimum=0, maximum=2**63 - 1)
    _expect_digest(index["retrieval_plan_sha256"], "index.retrieval_plan_sha256")

    selection = index["selection"]
    if not isinstance(selection, dict):
        raise RetrievalError("retrieval index selection must be an object")
    _require_exact_keys(
        selection,
        {
            "requested_source_ids",
            "eligible_source_ids",
            "excluded_source_ids",
            "input_count",
            "input_sha256",
        },
        "index.selection",
    )
    for key in ("requested_source_ids", "eligible_source_ids", "excluded_source_ids"):
        values = selection[key]
        if (
            not isinstance(values, list)
            or any(not isinstance(value, str) or not value for value in values)
            or values != sorted(set(values))
        ):
            raise RetrievalError(f"index.selection.{key} must be a sorted unique string array")
    if set(selection["eligible_source_ids"]) & set(selection["excluded_source_ids"]):
        raise RetrievalError("eligible and excluded source IDs overlap")
    _require_plain_int(selection["input_count"], "index.selection.input_count", minimum=1, maximum=2**31 - 1)
    _expect_digest(selection["input_sha256"], "index.selection.input_sha256")

    chunking = index["chunking"]
    if not isinstance(chunking, dict):
        raise RetrievalError("retrieval index chunking must be an object")
    _require_exact_keys(
        chunking,
        {"implementation", "strategy", "buffer_size", "breakpoint_percentile_threshold"},
        "index.chunking",
    )
    if chunking["implementation"] not in {"native", "llamaindex"}:
        raise RetrievalError("index chunking implementation is invalid")
    if chunking["strategy"] not in {"record", "semantic"}:
        raise RetrievalError("index chunking strategy is invalid")
    if chunking["implementation"] == "llamaindex" and chunking["strategy"] != "semantic":
        raise RetrievalError("llamaindex index requires semantic strategy")
    _require_plain_int(chunking["buffer_size"], "index.chunking.buffer_size", minimum=1, maximum=16)
    percentile = chunking["breakpoint_percentile_threshold"]
    if (
        isinstance(percentile, bool)
        or not isinstance(percentile, (int, float))
        or not math.isfinite(float(percentile))
        or not 0.0 <= float(percentile) <= 100.0
    ):
        raise RetrievalError("index chunking percentile is invalid")

    embedding = index["embedding"]
    if not isinstance(embedding, dict):
        raise RetrievalError("retrieval index embedding must be an object")
    _require_exact_keys(
        embedding,
        {
            "provider",
            "model_id",
            "revision",
            "dimension",
            "normalize",
            "metric",
            "encoding",
            "vector_precision",
        },
        "index.embedding",
    )
    if embedding["provider"] not in {"hashing", "sentence-transformers"}:
        raise RetrievalError("index embedding provider is invalid")
    if not isinstance(embedding["model_id"], str) or not embedding["model_id"]:
        raise RetrievalError("index embedding model_id is invalid")
    if not isinstance(embedding["revision"], str) or not embedding["revision"]:
        raise RetrievalError("index embedding revision is invalid")
    if embedding["provider"] == "hashing" and (
        embedding["model_id"], embedding["revision"]
    ) != (HASHING_MODEL_ID, HASHING_REVISION):
        raise RetrievalError("index hashing model identity is invalid")
    if embedding["provider"] == "sentence-transformers":
        if not _is_hugging_face_model_id(embedding["model_id"]):
            raise RetrievalError("index SentenceTransformers model_id is invalid")
        if not IMMUTABLE_REVISION.fullmatch(embedding["revision"]):
            raise RetrievalError("index SentenceTransformers revision is not immutable")
    _require_plain_int(embedding["dimension"], "index.embedding.dimension", minimum=1, maximum=4096)
    if not isinstance(embedding["normalize"], bool):
        raise RetrievalError("index embedding normalize marker must be boolean")
    if embedding["metric"] != "cosine":
        raise RetrievalError("index embedding metric must be cosine")
    if embedding["encoding"] != {"document": "symmetric", "query": "symmetric"}:
        raise RetrievalError("index embedding encoding contract is invalid")
    if embedding["vector_precision"] != VECTOR_PRECISION:
        raise RetrievalError(f"index vector_precision must be {VECTOR_PRECISION}")

    artifacts = index["artifacts"]
    if not isinstance(artifacts, dict):
        raise RetrievalError("retrieval index artifacts must be an object")
    _require_exact_keys(artifacts, {"chunks", "embeddings"}, "index.artifacts")
    for key in ("chunks", "embeddings"):
        value = artifacts[key]
        if not isinstance(value, dict):
            raise RetrievalError(f"index artifact {key} must be an object")
        _require_exact_keys(value, {"path", "sha256", "count"}, f"index.artifacts.{key}")
        expected_path = f"retrieval/{key}.jsonl"
        if value["path"] != expected_path:
            raise RetrievalError(f"index artifact {key} path must be {expected_path}")
        _expect_digest(value["sha256"], f"index.artifacts.{key}.sha256")
        _require_plain_int(value["count"], f"index.artifacts.{key}.count", minimum=0, maximum=2**63 - 1)
    _require_plain_int(index["chunk_count"], "index.chunk_count", minimum=0, maximum=2**63 - 1)
    _require_plain_int(index["embedding_count"], "index.embedding_count", minimum=0, maximum=2**63 - 1)
    return index


def _validate_chunk_rows(
    rows: Sequence[dict[str, Any]], records: Sequence[dict[str, Any]], index: Mapping[str, Any]
) -> None:
    record_by_key = {
        (record.get("source_id"), record.get("record_id")): record for record in records
    }
    eligible = set(index["selection"]["eligible_source_ids"])
    chunk_ids: list[str] = []
    ordinals: dict[tuple[Any, Any], list[int]] = {}
    for number, row in enumerate(rows, start=1):
        _require_exact_keys(row, CHUNK_KEYS, f"retrieval/chunks.jsonl:{number}")
        chunk_id = row["chunk_id"]
        if not isinstance(chunk_id, str) or not re.fullmatch(r"chunk-[0-9a-f]{32}", chunk_id):
            raise RetrievalError(f"retrieval/chunks.jsonl:{number} has an invalid chunk_id")
        if row["source_id"] not in eligible:
            raise RetrievalError(f"retrieval/chunks.jsonl:{number} belongs to an ineligible source")
        key = (row["source_id"], row["record_id"])
        record = record_by_key.get(key)
        if record is None:
            raise RetrievalError(f"retrieval/chunks.jsonl:{number} is orphaned from the record ledger")
        for field in (
            "concept_id",
            "concept_path",
            "record_sha256",
            "source_path",
        ):
            if row[field] != record.get(field):
                raise RetrievalError(f"retrieval/chunks.jsonl:{number} {field} differs from its record")
        ordinal = row["ordinal"]
        _require_plain_int(ordinal, f"retrieval/chunks.jsonl:{number}.ordinal", minimum=0, maximum=2**31 - 1)
        text = row["text"]
        if not isinstance(text, str) or not text:
            raise RetrievalError(f"retrieval/chunks.jsonl:{number}.text must be non-empty")
        if row["text_sha256"] != sha256_bytes(text.encode("utf-8")):
            raise RetrievalError(f"retrieval/chunks.jsonl:{number} text digest mismatch")
        if row["chunk_id"] != _chunk_id(row):
            raise RetrievalError(f"retrieval/chunks.jsonl:{number} chunk ID mismatch")
        locator = row["locator"]
        if not isinstance(locator, dict):
            raise RetrievalError(f"retrieval/chunks.jsonl:{number}.locator must be an object")
        body = record.get("body")
        strategy = index["chunking"]["strategy"]
        if locator == {"kind": "record"}:
            if strategy != "record":
                raise RetrievalError(
                    f"retrieval/chunks.jsonl:{number} uses a record locator for semantic chunking"
                )
            if text != body:
                raise RetrievalError(f"retrieval/chunks.jsonl:{number} record locator text mismatch")
        else:
            if strategy != "semantic":
                raise RetrievalError(
                    f"retrieval/chunks.jsonl:{number} uses a character locator for record chunking"
                )
            _require_exact_keys(locator, {"kind", "start", "end"}, f"retrieval/chunks.jsonl:{number}.locator")
            if locator["kind"] != "character-range":
                raise RetrievalError(f"retrieval/chunks.jsonl:{number} locator kind is invalid")
            start = _require_plain_int(locator["start"], "locator.start", minimum=0, maximum=2**63 - 1)
            end = _require_plain_int(locator["end"], "locator.end", minimum=1, maximum=2**63 - 1)
            if not isinstance(body, str) or not start < end <= len(body) or body[start:end] != text:
                raise RetrievalError(f"retrieval/chunks.jsonl:{number} character locator text mismatch")
        chunk_ids.append(chunk_id)
        ordinals.setdefault(key, []).append(ordinal)
    if chunk_ids != sorted(chunk_ids) or len(set(chunk_ids)) != len(chunk_ids):
        raise RetrievalError("retrieval/chunks.jsonl must be uniquely ordered by chunk_id")
    for key, values in ordinals.items():
        if sorted(values) != list(range(len(values))):
            raise RetrievalError(f"chunk ordinals for {key!r} are not contiguous from zero")
    selected_record_keys = {
        (record.get("source_id"), record.get("record_id"))
        for record in records
        if record.get("source_id") in eligible
    }
    if set(ordinals) != selected_record_keys:
        raise RetrievalError("eligible records and chunked records differ")


def _validate_embedding_rows(
    rows: Sequence[dict[str, Any]], chunks: Sequence[dict[str, Any]], index: Mapping[str, Any]
) -> None:
    if len(rows) != len(chunks):
        raise RetrievalError("embedding and chunk row counts differ")
    vectors: list[list[Any]] = []
    for number, (row, chunk) in enumerate(zip(rows, chunks), start=1):
        _require_exact_keys(row, {"chunk_id", "vector"}, f"retrieval/embeddings.jsonl:{number}")
        if row["chunk_id"] != chunk["chunk_id"]:
            raise RetrievalError(f"retrieval/embeddings.jsonl:{number} is orphaned or out of order")
        vector = row["vector"]
        if not isinstance(vector, list):
            raise RetrievalError(f"retrieval/embeddings.jsonl:{number}.vector must be an array")
        if any(
            isinstance(value, float) and round(value, VECTOR_PRECISION) != value for value in vector
        ):
            raise RetrievalError(f"retrieval/embeddings.jsonl:{number} exceeds vector precision")
        vectors.append(vector)
    embedding = index["embedding"]
    _validate_vectors(vectors, embedding["dimension"], embedding["normalize"], "stored")


def _validate_retrieval_or_raise(root: Path, *, require_build_report: bool) -> dict[str, Any]:
    if not root.is_dir():
        raise RetrievalError(f"bundle does not exist or is not a directory: {root}")
    core_result = validate_semantic_bundle(root)
    if not core_result.valid:
        details = "; ".join(error.get("message", "core error") for error in core_result.errors[:3])
        raise RetrievalError(f"authoritative Semantic OKF core is invalid: {details}")
    retrieval = root / "retrieval"
    expected_names = {"index.json", "chunks.jsonl", "embeddings.jsonl"}
    if require_build_report:
        expected_names.add("build-report.json")
    if not retrieval.is_dir() or retrieval.is_symlink():
        raise RetrievalError("retrieval must be a real directory")
    actual_names = {path.name for path in retrieval.iterdir()}
    if actual_names != expected_names:
        raise RetrievalError(
            f"retrieval artifact set is closed; missing={sorted(expected_names - actual_names)}, "
            f"unknown={sorted(actual_names - expected_names)}"
        )
    if any(path.is_symlink() or not path.is_file() for path in retrieval.iterdir()):
        raise RetrievalError("retrieval artifacts must be regular files")
    index_value = strict_json_loads(
        (retrieval / "index.json").read_text(encoding="utf-8"),
        label="retrieval/index.json",
    )
    index = _validate_index_shape(index_value)
    records, sources = _load_core(root)
    if index["core"] != {
        "tree_sha256": _core_tree_sha256(root),
        "records_sha256": sha256_file(root / "semantic" / "records.jsonl"),
        "record_count": len(records),
    }:
        raise RetrievalError("retrieval index core binding is stale or invalid")

    source_by_id = {source.get("id"): source for source in sources if isinstance(source.get("id"), str)}
    requested = index["selection"]["requested_source_ids"]
    if requested != index["selection"]["eligible_source_ids"]:
        raise RetrievalError("every requested source must be eligible in a completed projection")
    if set(requested) - set(source_by_id):
        raise RetrievalError("retrieval index selects unknown source IDs")
    if index["selection"]["excluded_source_ids"] != sorted(set(source_by_id) - set(requested)):
        raise RetrievalError("retrieval index excluded source set is invalid")
    inventory = [
        {"source_id": source_id, "content_sha256": source_by_id[source_id].get("content_sha256")}
        for source_id in requested
    ]
    if index["selection"]["input_count"] != len(inventory):
        raise RetrievalError("retrieval index input count mismatch")
    if index["selection"]["input_sha256"] != sha256_canonical(inventory):
        raise RetrievalError("retrieval index input digest mismatch")

    chunks_path = retrieval / "chunks.jsonl"
    embeddings_path = retrieval / "embeddings.jsonl"
    chunks = _read_jsonl(chunks_path, label="retrieval/chunks.jsonl")
    embeddings = _read_jsonl(embeddings_path, label="retrieval/embeddings.jsonl")
    _validate_chunk_rows(chunks, records, index)
    _validate_embedding_rows(embeddings, chunks, index)
    expected_artifacts = {
        "chunks": _artifact("retrieval/chunks.jsonl", root, len(chunks)),
        "embeddings": _artifact("retrieval/embeddings.jsonl", root, len(embeddings)),
    }
    if index["artifacts"] != expected_artifacts:
        raise RetrievalError("retrieval index artifact hashes or counts are invalid")
    if index["chunk_count"] != len(chunks) or index["embedding_count"] != len(embeddings):
        raise RetrievalError("retrieval index summary counts are invalid")

    selected_record_count = sum(1 for row in records if row.get("source_id") in set(requested))
    expected_report = {
        "schema_version": SCHEMA_VERSION,
        "valid": True,
        "status": "pass",
        "errors": [],
        "warnings": [],
        "retrieval_plan_sha256": index["retrieval_plan_sha256"],
        "core": index["core"],
        "selection": index["selection"],
        "summary": {
            "inputs": len(inventory),
            "records": selected_record_count,
            "chunks": len(chunks),
            "embeddings": len(embeddings),
            "dimension": index["embedding"]["dimension"],
        },
        "artifacts": {
            "index": _artifact("retrieval/index.json", root),
            "chunks": expected_artifacts["chunks"],
            "embeddings": expected_artifacts["embeddings"],
        },
    }
    if require_build_report:
        report = strict_json_loads(
            (retrieval / "build-report.json").read_text(encoding="utf-8"),
            label="retrieval/build-report.json",
        )
        if report != expected_report:
            raise RetrievalError("retrieval build report differs from live validation")
    return {
        "schema_version": SCHEMA_VERSION,
        "valid": True,
        "status": "pass",
        "errors": [],
        "warnings": [],
        "summary": expected_report["summary"],
    }


def validate_retrieval_bundle(root: Path, *, require_build_report: bool = True) -> dict[str, Any]:
    """Validate the authoritative core plus every retrieval binding."""

    try:
        return _validate_retrieval_or_raise(root, require_build_report=require_build_report)
    except (
        RetrievalError,
        OSError,
        UnicodeError,
        KeyError,
        IndexError,
        TypeError,
        ValueError,
        OverflowError,
    ) as exc:
        return {
            "schema_version": SCHEMA_VERSION,
            "valid": False,
            "status": "error",
            "errors": [{"code": "retrieval-error", "path": "retrieval", "message": str(exc)}],
            "warnings": [],
            "summary": {},
        }


def atomic_build(
    manifest_path: Path,
    plan_path: Path,
    output: Path,
    core_builder: Any,
) -> dict[str, Any]:
    """Build core and retrieval layers in a sibling candidate, then publish once."""

    output = output.resolve()
    if output.exists() or output.is_symlink():
        raise RetrievalError(f"output already exists: {output}")
    # Fail a malformed or unsafe retrieval plan before spending work on the core.
    load_plan(plan_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    candidate = Path(
        tempfile.mkdtemp(prefix=f".{output.name}.embedding-candidate-", dir=output.parent)
    )
    # The core builder requires a nonexistent target and publishes atomically to it.
    candidate.rmdir()
    try:
        core_builder(manifest_path, candidate)
        build_projection(candidate, plan_path)
        os.replace(candidate, output)
    except Exception:
        if candidate.exists():
            shutil.rmtree(candidate, ignore_errors=True)
        raise
    report = strict_json_loads(
        (output / "retrieval" / "build-report.json").read_text(encoding="utf-8"),
        label="retrieval/build-report.json",
    )
    return report
