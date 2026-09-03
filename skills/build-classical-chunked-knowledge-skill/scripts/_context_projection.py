"""Build, validate, and query a deterministic budgeted context projection."""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
import hashlib
import json
import math
from pathlib import Path
import re
from typing import Any, Iterable, Mapping, Sequence

from _classical_snapshot import ClassicalSnapshot, search_snapshot, tokenize


SCHEMA_VERSION = "classical-context-projection/1.0"
PLAN_SCHEMA_VERSION = "classical-context-plan/1.0"
CHUNKS_PATH = "chunks.jsonl"
INDEX_PATH = "index.json"
HEX_64_RE = re.compile(r"^[0-9a-f]{64}$")
HEADING_RE = re.compile(r"^(#{1,6})[ \t]+(.+?)[ \t]*#*[ \t]*$")
LEXICAL_TOKEN_RE = re.compile(r"\w+|[^\w\s]", re.UNICODE)


class ContextProjectionError(ValueError):
    """Describe an invalid context plan, projection, or selection request."""


@dataclass(frozen=True)
class ContextProjection:
    """Hold a validated context index and its chunk rows."""

    index: dict[str, Any]
    chunks: tuple[dict[str, Any], ...]

    @property
    def by_id(self) -> dict[str, dict[str, Any]]:
        """Return chunks keyed by immutable chunk identity."""

        return {str(row["chunk_id"]): row for row in self.chunks}

    @property
    def by_document(self) -> dict[str, tuple[dict[str, Any], ...]]:
        """Return chunks grouped in natural order by classical document."""

        grouped: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in self.chunks:
            grouped[str(row["document_id"])].append(row)
        return {
            key: tuple(sorted(value, key=lambda item: int(item["chunk_ordinal"])))
            for key, value in grouped.items()
        }


def canonical_json(value: Any) -> str:
    """Serialize JSON deterministically and reject non-finite values."""

    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def sha256_bytes(value: bytes) -> str:
    """Return one lowercase SHA-256 digest."""

    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    """Hash one regular file."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_canonical(value: Any) -> str:
    """Hash one canonical JSON value."""

    return sha256_bytes(canonical_json(value).encode("utf-8"))


def _plain_int(value: Any, label: str, minimum: int, maximum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ContextProjectionError(f"{label} must be an integer")
    if not minimum <= value <= maximum:
        raise ContextProjectionError(f"{label} must be from {minimum} through {maximum}")
    return value


def _finite(value: Any, label: str, minimum: float, maximum: float) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ContextProjectionError(f"{label} must be numeric")
    result = float(value)
    if not math.isfinite(result) or not minimum <= result <= maximum:
        raise ContextProjectionError(f"{label} must be finite from {minimum} through {maximum}")
    return result


def validate_plan(raw: Mapping[str, Any]) -> dict[str, Any]:
    """Validate and normalize one closed context-projection plan."""

    if set(raw) != {"schema_version", "chunking", "selection"}:
        raise ContextProjectionError("Context plan root is not closed")
    if raw.get("schema_version") != PLAN_SCHEMA_VERSION:
        raise ContextProjectionError("Unsupported context plan schema")
    chunking = raw.get("chunking")
    if not isinstance(chunking, Mapping) or set(chunking) != {
        "boundary_policy",
        "token_estimator",
        "minimum_tokens",
        "target_tokens",
        "maximum_tokens",
    }:
        raise ContextProjectionError("Context plan chunking section is not closed")
    if chunking.get("boundary_policy") != "markdown-structure-v1":
        raise ContextProjectionError("Unsupported context boundary policy")
    if chunking.get("token_estimator") != "utf8-bytes-or-lexical-v1":
        raise ContextProjectionError("Unsupported context token estimator")
    minimum_tokens = _plain_int(chunking.get("minimum_tokens"), "minimum_tokens", 16, 2048)
    target_tokens = _plain_int(chunking.get("target_tokens"), "target_tokens", 32, 4096)
    maximum_tokens = _plain_int(chunking.get("maximum_tokens"), "maximum_tokens", 64, 8192)
    if not minimum_tokens <= target_tokens <= maximum_tokens:
        raise ContextProjectionError("Chunk token limits must be ordered")

    selection = raw.get("selection")
    if not isinstance(selection, Mapping) or set(selection) != {
        "default_budget_tokens",
        "maximum_budget_tokens",
        "candidate_documents",
        "maximum_chunks",
        "minimum_evidence_identities",
        "minimum_query_coverage",
        "metadata_tokens_per_chunk",
        "bundle_overhead_tokens",
        "cost_power",
        "neighbor_relative_relevance",
        "redundancy_penalty",
        "weights",
    }:
        raise ContextProjectionError("Context plan selection section is not closed")
    default_budget = _plain_int(
        selection.get("default_budget_tokens"), "default_budget_tokens", 256, 100_000
    )
    maximum_budget = _plain_int(
        selection.get("maximum_budget_tokens"), "maximum_budget_tokens", 256, 200_000
    )
    if default_budget > maximum_budget:
        raise ContextProjectionError("Default context budget exceeds its maximum")
    _plain_int(selection.get("candidate_documents"), "candidate_documents", 1, 1000)
    _plain_int(selection.get("maximum_chunks"), "maximum_chunks", 1, 1000)
    _plain_int(
        selection.get("minimum_evidence_identities"),
        "minimum_evidence_identities",
        1,
        100,
    )
    _plain_int(selection.get("metadata_tokens_per_chunk"), "metadata_tokens_per_chunk", 0, 1000)
    _plain_int(selection.get("bundle_overhead_tokens"), "bundle_overhead_tokens", 0, 5000)
    _finite(selection.get("minimum_query_coverage"), "minimum_query_coverage", 0.0, 1.0)
    _finite(selection.get("cost_power"), "cost_power", 0.0, 2.0)
    _finite(
        selection.get("neighbor_relative_relevance"),
        "neighbor_relative_relevance",
        0.0,
        1.0,
    )
    _finite(selection.get("redundancy_penalty"), "redundancy_penalty", 0.0, 1.0)
    weights = selection.get("weights")
    weight_names = {"relevance", "coverage", "rank", "source_novelty", "continuity"}
    if not isinstance(weights, Mapping) or set(weights) != weight_names:
        raise ContextProjectionError("Context selection weights are not closed")
    values = [_finite(weights.get(name), f"weights.{name}", 0.0, 1.0) for name in weight_names]
    if not math.isclose(sum(values), 1.0, rel_tol=0.0, abs_tol=1e-9):
        raise ContextProjectionError("Context selection weights must sum to one")
    return json.loads(canonical_json(raw))


def load_plan(path: Path) -> dict[str, Any]:
    """Load one UTF-8 context plan."""

    if path.is_symlink() or not path.is_file():
        raise ContextProjectionError(f"Context plan is absent or unsafe: {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ContextProjectionError(f"Invalid context plan: {exc}") from exc
    if not isinstance(value, Mapping):
        raise ContextProjectionError("Context plan must be a JSON object")
    return validate_plan(value)


def estimate_tokens(text: str) -> int:
    """Return a deterministic conservative token-count proxy."""

    if not text:
        return 0
    lexical = len(LEXICAL_TOKEN_RE.findall(text))
    byte_estimate = math.ceil(len(text.encode("utf-8")) / 4)
    return max(1, lexical, byte_estimate)


def _trimmed_range(text: str, start: int, end: int) -> tuple[int, int] | None:
    while start < end and text[start].isspace():
        start += 1
    while end > start and text[end - 1].isspace():
        end -= 1
    return (start, end) if start < end else None


def _heading_path(stack: list[str | None]) -> tuple[str, ...]:
    return tuple(value for value in stack if value is not None)


def _structural_units(text: str) -> list[tuple[int, int, tuple[str, ...]]]:
    """Split Markdown into exact heading-aware paragraph or fenced-code units."""

    lines = text.splitlines(keepends=True)
    if not lines and text:
        lines = [text]
    units: list[tuple[int, int, tuple[str, ...]]] = []
    headings: list[str | None] = [None] * 6
    offset = 0
    start: int | None = None
    pending_heading: int | None = None
    unit_heading: tuple[str, ...] = ()
    in_fence = False

    def close(end: int) -> None:
        nonlocal start, pending_heading, unit_heading
        effective = start if start is not None else pending_heading
        if effective is not None:
            trimmed = _trimmed_range(text, effective, end)
            if trimmed is not None:
                units.append((*trimmed, unit_heading))
        start = None
        pending_heading = None

    for line in lines:
        line_start = offset
        offset += len(line)
        stripped = line.rstrip("\r\n")
        heading = HEADING_RE.match(stripped)
        if heading and not in_fence:
            close(line_start)
            level = len(heading.group(1))
            headings[level - 1] = heading.group(2).strip()
            for index in range(level, len(headings)):
                headings[index] = None
            pending_heading = line_start
            unit_heading = _heading_path(headings)
            continue
        if stripped.lstrip().startswith("```") or stripped.lstrip().startswith("~~~"):
            if start is None:
                start = pending_heading if pending_heading is not None else line_start
                pending_heading = None
                unit_heading = _heading_path(headings)
            in_fence = not in_fence
            continue
        if not stripped.strip() and not in_fence:
            close(line_start)
            continue
        if start is None:
            start = pending_heading if pending_heading is not None else line_start
            pending_heading = None
            unit_heading = _heading_path(headings)
    close(len(text))
    if not units and text.strip():
        trimmed = _trimmed_range(text, 0, len(text))
        if trimmed is not None:
            units.append((*trimmed, ()))
    return units


def _largest_fitting_end(text: str, start: int, end: int, budget: int) -> int:
    low, high = start + 1, end
    best = start + 1
    while low <= high:
        middle = (low + high) // 2
        if estimate_tokens(text[start:middle]) <= budget:
            best = middle
            low = middle + 1
        else:
            high = middle - 1
    if best >= end:
        return end
    floor = start + max(1, int((best - start) * 0.6))
    window = text[floor:best]
    boundaries = [
        floor + match.end()
        for match in re.finditer(r"(?:\n|(?<=[.!?])\s+|[ \t]+)", window)
    ]
    return boundaries[-1] if boundaries else best


def _split_oversize(
    text: str,
    unit: tuple[int, int, tuple[str, ...]],
    maximum_tokens: int,
) -> list[tuple[int, int, tuple[str, ...]]]:
    start, end, headings = unit
    result: list[tuple[int, int, tuple[str, ...]]] = []
    cursor = start
    while cursor < end:
        next_end = _largest_fitting_end(text, cursor, end, maximum_tokens)
        trimmed = _trimmed_range(text, cursor, next_end)
        if trimmed is not None:
            result.append((*trimmed, headings))
        cursor = max(next_end, cursor + 1)
        while cursor < end and text[cursor].isspace():
            cursor += 1
    return result


def _chunk_ranges(text: str, plan: Mapping[str, Any]) -> list[tuple[int, int, tuple[str, ...]]]:
    chunking = plan["chunking"]
    minimum = int(chunking["minimum_tokens"])
    target = int(chunking["target_tokens"])
    maximum = int(chunking["maximum_tokens"])
    atoms: list[tuple[int, int, tuple[str, ...]]] = []
    for unit in _structural_units(text):
        if estimate_tokens(text[unit[0] : unit[1]]) > maximum:
            atoms.extend(_split_oversize(text, unit, maximum))
        else:
            atoms.append(unit)
    chunks: list[tuple[int, int, tuple[str, ...]]] = []
    current: tuple[int, int, tuple[str, ...]] | None = None
    for atom in atoms:
        if current is None:
            current = atom
            continue
        current_tokens = estimate_tokens(text[current[0] : current[1]])
        combined_tokens = estimate_tokens(text[current[0] : atom[1]])
        heading_changed = atom[2] != current[2]
        should_merge = combined_tokens <= target and (
            not heading_changed or current_tokens < minimum
        )
        if should_merge:
            current = (current[0], atom[1], atom[2] or current[2])
        else:
            chunks.append(current)
            current = atom
    if current is not None:
        chunks.append(current)
    return chunks


def _read_records(knowledge_root: Path) -> list[dict[str, Any]]:
    path = knowledge_root / "semantic" / "records.jsonl"
    try:
        rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ContextProjectionError(f"Cannot read authoritative records: {exc}") from exc
    if not rows or any(not isinstance(row, dict) for row in rows):
        raise ContextProjectionError("Authoritative record ledger is empty or malformed")
    return rows


def _record_base(document: Mapping[str, Any], body: str) -> int:
    locator = document.get("locator")
    if locator == {"kind": "record"}:
        base = 0
    elif (
        isinstance(locator, Mapping)
        and set(locator) == {"kind", "start", "end"}
        and locator.get("kind") == "character-range"
        and isinstance(locator.get("start"), int)
        and isinstance(locator.get("end"), int)
    ):
        base = int(locator["start"])
    else:
        raise ContextProjectionError("Classical document has an invalid locator")
    text = document.get("text")
    if not isinstance(text, str) or body[base : base + len(text)] != text:
        raise ContextProjectionError("Classical document text is not an exact ledger slice")
    return base


def derive_chunks(
    snapshot: ClassicalSnapshot,
    records: Sequence[Mapping[str, Any]],
    plan: Mapping[str, Any],
) -> list[dict[str, Any]]:
    """Derive all exact non-overlapping context chunks from classical passages."""

    normalized = validate_plan(plan)
    by_record = {
        (str(row.get("source_id")), str(row.get("record_id"))): row for row in records
    }
    chunks: list[dict[str, Any]] = []
    for document in sorted(snapshot.documents, key=lambda row: str(row["document_id"])):
        key = (str(document["source_id"]), str(document["record_id"]))
        record = by_record.get(key)
        if record is None or not isinstance(record.get("body"), str):
            raise ContextProjectionError(f"Classical document is orphaned: {key!r}")
        body = str(record["body"])
        text = str(document["text"])
        base = _record_base(document, body)
        document_rows: list[dict[str, Any]] = []
        for ordinal, (start, end, headings) in enumerate(_chunk_ranges(text, normalized)):
            chunk_text = text[start:end]
            record_start, record_end = base + start, base + end
            digest = sha256_bytes(chunk_text.encode("utf-8"))
            identity = {
                "document_id": document["document_id"],
                "record_sha256": document["record_sha256"],
                "start": record_start,
                "end": record_end,
                "text_sha256": digest,
            }
            row = {
                "chunk_id": "chunk-" + sha256_canonical(identity)[:32],
                "document_id": document["document_id"],
                "source_id": document["source_id"],
                "record_id": document["record_id"],
                "record_sha256": document["record_sha256"],
                "document_ordinal": document["ordinal"],
                "chunk_ordinal": ordinal,
                "record_char_start": record_start,
                "record_char_end": record_end,
                "text_sha256": digest,
                "estimated_tokens": estimate_tokens(chunk_text),
                "heading_path": list(headings),
                "terms": dict(sorted(Counter(tokenize(chunk_text, snapshot.index["plan"])).items())),
                "previous_chunk_id": None,
                "next_chunk_id": None,
            }
            document_rows.append(row)
        for index, row in enumerate(document_rows):
            row["previous_chunk_id"] = document_rows[index - 1]["chunk_id"] if index else None
            row["next_chunk_id"] = (
                document_rows[index + 1]["chunk_id"] if index + 1 < len(document_rows) else None
            )
        chunks.extend(document_rows)
    if not chunks:
        raise ContextProjectionError("Context projection produced no chunks")
    return chunks


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def build_projection(
    knowledge_root: Path,
    context_root: Path,
    snapshot: ClassicalSnapshot,
    plan: Mapping[str, Any],
) -> dict[str, Any]:
    """Build one closed context projection beside immutable knowledge."""

    if context_root.exists() or context_root.is_symlink():
        raise ContextProjectionError(f"Context projection already exists: {context_root}")
    normalized = validate_plan(plan)
    records = _read_records(knowledge_root)
    chunks = derive_chunks(snapshot, records, normalized)
    context_root.mkdir(parents=True)
    chunks_path = context_root / CHUNKS_PATH
    _write_text(chunks_path, "".join(canonical_json(row) + "\n" for row in chunks))
    index = {
        "schema_version": SCHEMA_VERSION,
        "algorithm": {
            "chunking": "markdown-structure-v1",
            "selection": "budgeted-query-coverage-mmr-v1",
            "redundancy": "jensen-shannon-similarity-v1",
            "neighbor_expansion": "relative-relevance-linked-v1",
        },
        "plan": normalized,
        "plan_sha256": sha256_canonical(normalized),
        "bindings": {
            "classical_index_sha256": snapshot.index_sha256,
            "records_sha256": sha256_file(knowledge_root / "semantic" / "records.jsonl"),
        },
        "counts": {
            "records": len(records),
            "documents": len(snapshot.documents),
            "chunks": len(chunks),
        },
        "artifacts": {
            CHUNKS_PATH: {
                "bytes": chunks_path.stat().st_size,
                "sha256": sha256_file(chunks_path),
            }
        },
    }
    _write_text(context_root / INDEX_PATH, json.dumps(index, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    return index


def _load_json_object(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ContextProjectionError(f"Invalid {label}: {exc}") from exc
    if not isinstance(value, dict):
        raise ContextProjectionError(f"{label} must be an object")
    return value


def load_projection(context_root: Path) -> ContextProjection:
    """Load and structurally validate one closed context projection."""

    if not context_root.is_dir() or context_root.is_symlink():
        raise ContextProjectionError("Context projection directory is absent or unsafe")
    files = {path.name for path in context_root.iterdir() if path.is_file() and not path.is_symlink()}
    if files != {INDEX_PATH, CHUNKS_PATH} or any(path.is_symlink() for path in context_root.iterdir()):
        raise ContextProjectionError("Context projection file set is not closed")
    index = _load_json_object(context_root / INDEX_PATH, "context index")
    if set(index) != {
        "schema_version", "algorithm", "plan", "plan_sha256", "bindings", "counts", "artifacts"
    } or index.get("schema_version") != SCHEMA_VERSION:
        raise ContextProjectionError("Context index schema or root is invalid")
    plan = validate_plan(index.get("plan") if isinstance(index.get("plan"), Mapping) else {})
    if index.get("plan_sha256") != sha256_canonical(plan):
        raise ContextProjectionError("Context plan digest drift")
    binding = index.get("artifacts", {}).get(CHUNKS_PATH) if isinstance(index.get("artifacts"), Mapping) else None
    chunks_path = context_root / CHUNKS_PATH
    if not isinstance(binding, Mapping) or set(binding) != {"bytes", "sha256"}:
        raise ContextProjectionError("Context chunks binding is invalid")
    if binding.get("bytes") != chunks_path.stat().st_size or binding.get("sha256") != sha256_file(chunks_path):
        raise ContextProjectionError("Context chunks artifact drift")
    try:
        chunks = tuple(
            json.loads(line) for line in chunks_path.read_text(encoding="utf-8").splitlines() if line.strip()
        )
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ContextProjectionError(f"Invalid context chunks: {exc}") from exc
    if not chunks or any(not isinstance(row, dict) for row in chunks):
        raise ContextProjectionError("Context chunks are empty or malformed")
    identities = [row.get("chunk_id") for row in chunks]
    if any(not isinstance(value, str) for value in identities) or len(set(identities)) != len(identities):
        raise ContextProjectionError("Context chunk identities are invalid or duplicated")
    if index.get("counts", {}).get("chunks") != len(chunks):
        raise ContextProjectionError("Context chunk count drift")
    return ContextProjection(index=index, chunks=chunks)


def validate_projection(
    knowledge_root: Path,
    context_root: Path,
    snapshot: ClassicalSnapshot,
    *,
    rederive: bool,
) -> ContextProjection:
    """Validate projection bindings and optionally rederive every chunk."""

    projection = load_projection(context_root)
    bindings = projection.index.get("bindings")
    if not isinstance(bindings, Mapping) or set(bindings) != {
        "classical_index_sha256", "records_sha256"
    }:
        raise ContextProjectionError("Context knowledge bindings are invalid")
    if bindings.get("classical_index_sha256") != snapshot.index_sha256:
        raise ContextProjectionError("Context classical-index binding drift")
    if bindings.get("records_sha256") != sha256_file(knowledge_root / "semantic" / "records.jsonl"):
        raise ContextProjectionError("Context ledger binding drift")
    counts = projection.index.get("counts")
    records = _read_records(knowledge_root)
    if not isinstance(counts, Mapping) or counts.get("records") != len(records) or counts.get("documents") != len(snapshot.documents):
        raise ContextProjectionError("Context source counts drift")
    by_record = {(str(row["source_id"]), str(row["record_id"])): row for row in records}
    for row in projection.chunks:
        record = by_record.get((str(row.get("source_id")), str(row.get("record_id"))))
        if record is None:
            raise ContextProjectionError("Context chunk is orphaned from the ledger")
        hydrate_chunk(row, by_record)
    if rederive:
        expected = derive_chunks(snapshot, records, projection.index["plan"])
        if [canonical_json(row) for row in expected] != [canonical_json(row) for row in projection.chunks]:
            raise ContextProjectionError("Context chunks differ from deterministic rederivation")
    return projection


def hydrate_chunk(
    chunk: Mapping[str, Any],
    records: Mapping[tuple[str, str], Mapping[str, Any]],
) -> str:
    """Return and verify one exact authoritative chunk body."""

    record = records.get((str(chunk.get("source_id")), str(chunk.get("record_id"))))
    if record is None or not isinstance(record.get("body"), str):
        raise ContextProjectionError("Context chunk is orphaned from authoritative evidence")
    start, end = chunk.get("record_char_start"), chunk.get("record_char_end")
    if (
        isinstance(start, bool)
        or isinstance(end, bool)
        or not isinstance(start, int)
        or not isinstance(end, int)
        or not 0 <= start < end <= len(record["body"])
    ):
        raise ContextProjectionError("Context chunk has an invalid authoritative range")
    text = str(record["body"])[start:end]
    if chunk.get("text_sha256") != sha256_bytes(text.encode("utf-8")):
        raise ContextProjectionError("Context chunk text digest drift")
    if chunk.get("estimated_tokens") != estimate_tokens(text):
        raise ContextProjectionError("Context chunk token estimate drift")
    return text


def _idf(snapshot: ClassicalSnapshot) -> dict[str, float]:
    terms = snapshot.lexicon.get("terms")
    if not isinstance(terms, list):
        return {}
    return {
        str(row["term"]): float(row["idf"])
        for row in terms
        if isinstance(row, Mapping) and isinstance(row.get("term"), str) and isinstance(row.get("idf"), (int, float))
    }


def _jensen_shannon_similarity(left: Mapping[str, int], right: Mapping[str, int]) -> float:
    left_total, right_total = sum(left.values()), sum(right.values())
    if left_total <= 0 or right_total <= 0:
        return 0.0
    keys = set(left) | set(right)
    divergence = 0.0
    for key in keys:
        p = float(left.get(key, 0)) / left_total
        q = float(right.get(key, 0)) / right_total
        mixture = (p + q) / 2.0
        if p > 0:
            divergence += 0.5 * p * math.log2(p / mixture)
        if q > 0:
            divergence += 0.5 * q * math.log2(q / mixture)
    return max(0.0, min(1.0, 1.0 - divergence))


def select_context(
    snapshot: ClassicalSnapshot,
    projection: ContextProjection,
    records: Sequence[Mapping[str, Any]],
    query: str,
    mode: str,
    *,
    budget_tokens: int | None,
    maximum_chunks: int | None,
    source_ids: Sequence[str] = (),
    concept_ids: Sequence[str] = (),
    concept_types: Sequence[str] = (),
) -> dict[str, Any]:
    """Select a compact, diverse, exact evidence bundle under a token budget."""

    plan = projection.index["plan"]
    selection = plan["selection"]
    budget = selection["default_budget_tokens"] if budget_tokens is None else budget_tokens
    if isinstance(budget, bool) or not isinstance(budget, int) or not 256 <= budget <= int(selection["maximum_budget_tokens"]):
        raise ContextProjectionError(
            f"budget_tokens must be from 256 through {selection['maximum_budget_tokens']}"
        )
    chunk_limit = selection["maximum_chunks"] if maximum_chunks is None else maximum_chunks
    if isinstance(chunk_limit, bool) or not isinstance(chunk_limit, int) or not 1 <= chunk_limit <= int(selection["maximum_chunks"]):
        raise ContextProjectionError(
            f"maximum_chunks must be from 1 through {selection['maximum_chunks']}"
        )
    candidate_documents = int(selection["candidate_documents"])
    discovery = search_snapshot(
        snapshot,
        query,
        mode,
        candidate_documents,
        source_ids=source_ids,
        concept_ids=concept_ids,
        concept_types=concept_types,
    )
    by_document = projection.by_document
    parent_rank = {
        str(row["document_id"]): int(row["rank"]) for row in discovery["results"]
    }
    candidates = [
        row
        for document_id in parent_rank
        for row in by_document.get(document_id, ())
    ]
    if not candidates:
        raise ContextProjectionError("Classical retrieval produced no context candidates")
    record_map = {
        (str(row.get("source_id")), str(row.get("record_id"))): row for row in records
    }
    idf = _idf(snapshot)
    original = Counter(tokenize(query, snapshot.index["plan"]))
    expansions = {
        str(row["term"]): float(row["weight"])
        for group in ("association_terms", "topic_terms")
        for row in discovery["expansion"][group]
    }
    query_weights: dict[str, float] = {
        term: float(count) for term, count in original.items()
    }
    for term, weight in expansions.items():
        query_weights[term] = query_weights.get(term, 0.0) + weight
    facet_weights = {
        term: float(count) * max(0.05, idf.get(term, 1.0))
        for term, count in original.items()
        if any(int(row.get("terms", {}).get(term, 0)) > 0 for row in candidates)
    }
    facet_total = sum(facet_weights.values())

    raw_relevance: dict[str, float] = {}
    for row in candidates:
        terms = row.get("terms") if isinstance(row.get("terms"), Mapping) else {}
        score = sum(
            weight * max(0.05, idf.get(term, 1.0)) * math.log1p(float(terms.get(term, 0)))
            for term, weight in query_weights.items()
        )
        raw_relevance[str(row["chunk_id"])] = score / math.sqrt(max(1, int(row["estimated_tokens"])))
    maximum_relevance = max(raw_relevance.values(), default=0.0)
    normalized_relevance = {
        key: (value / maximum_relevance if maximum_relevance > 0 else 0.0)
        for key, value in raw_relevance.items()
    }
    available_evidence = []
    for result in discovery["results"]:
        identity = str(result.get("paper_id") or result.get("source_id"))
        if identity not in available_evidence:
            available_evidence.append(identity)
    evidence_by_document = {
        str(result["document_id"]): str(result.get("paper_id") or result.get("source_id"))
        for result in discovery["results"]
    }
    evidence_by_chunk = {
        str(row["chunk_id"]): evidence_by_document[str(row["document_id"])]
        for row in candidates
    }
    required_evidence = min(
        int(selection["minimum_evidence_identities"]), len(available_evidence), chunk_limit
    )
    selected: list[dict[str, Any]] = []
    selected_ids: set[str] = set()
    selected_terms: Counter[str] = Counter()
    selected_evidence: set[str] = set()
    used_tokens = int(selection["bundle_overhead_tokens"])
    maximum_redundancy = {str(row["chunk_id"]): 0.0 for row in candidates}

    def evidence_identity(row: Mapping[str, Any]) -> str:
        return evidence_by_chunk[str(row["chunk_id"])]

    def cost(row: Mapping[str, Any]) -> int:
        return int(row["estimated_tokens"]) + int(selection["metadata_tokens_per_chunk"])

    def add(row: dict[str, Any]) -> bool:
        nonlocal used_tokens
        identifier = str(row["chunk_id"])
        if identifier in selected_ids or used_tokens + cost(row) > budget:
            return False
        hydrate_chunk(row, record_map)
        selected.append(row)
        selected_ids.add(identifier)
        selected_terms.update({str(key): int(value) for key, value in row["terms"].items()})
        selected_evidence.add(evidence_identity(row))
        used_tokens += cost(row)
        chosen_terms = row["terms"]
        for candidate in candidates:
            candidate_id = str(candidate["chunk_id"])
            if candidate_id in selected_ids:
                continue
            similarity = _jensen_shannon_similarity(candidate["terms"], chosen_terms)
            if similarity > maximum_redundancy[candidate_id]:
                maximum_redundancy[candidate_id] = similarity
        return True

    for identity in available_evidence[:required_evidence]:
        rows = [row for row in candidates if evidence_identity(row) == identity]
        rows.sort(
            key=lambda row: (
                -normalized_relevance[str(row["chunk_id"])],
                parent_rank[str(row["document_id"])],
                int(row["chunk_ordinal"]),
                str(row["chunk_id"]),
            )
        )
        for row in rows:
            if add(row):
                break

    minimum_coverage = float(selection["minimum_query_coverage"])
    cost_power = float(selection["cost_power"])

    def current_coverage() -> float:
        covered = sum(
            weight
            for term, weight in facet_weights.items()
            if selected_terms.get(term, 0) > 0
        )
        return covered / facet_total if facet_total > 0 else 0.0

    # Repair uncovered query facets before general MMR optimization. This makes
    # the declared completeness guard actionable instead of merely diagnostic.
    while len(selected) < chunk_limit and current_coverage() < minimum_coverage:
        coverage_choices: list[tuple[float, float, int, str, dict[str, Any]]] = []
        for row in candidates:
            identifier = str(row["chunk_id"])
            if identifier in selected_ids or used_tokens + cost(row) > budget:
                continue
            gain = sum(
                weight
                for term, weight in facet_weights.items()
                if selected_terms.get(term, 0) == 0 and int(row["terms"].get(term, 0)) > 0
            )
            if gain <= 0:
                continue
            adjusted_gain = gain / (max(1, cost(row)) ** cost_power)
            coverage_choices.append(
                (
                    adjusted_gain,
                    normalized_relevance[identifier],
                    -parent_rank[str(row["document_id"])],
                    identifier,
                    row,
                )
            )
        if not coverage_choices:
            break
        *_, chosen = sorted(
            coverage_choices,
            key=lambda item: (-item[0], -item[1], -item[2], item[3]),
        )[0]
        if not add(chosen):
            break

    weights = selection["weights"]
    while len(selected) < chunk_limit:
        choices: list[tuple[float, str, dict[str, Any]]] = []
        for row in candidates:
            identifier = str(row["chunk_id"])
            if identifier in selected_ids or used_tokens + cost(row) > budget:
                continue
            terms = row["terms"]
            new_coverage = sum(
                weight
                for term, weight in facet_weights.items()
                if int(terms.get(term, 0)) > 0 and selected_terms.get(term, 0) == 0
            )
            coverage_gain = new_coverage / facet_total if facet_total > 0 else 0.0
            rank_gain = 1.0 / float(parent_rank[str(row["document_id"])])
            novelty = 1.0 if evidence_identity(row) not in selected_evidence else 0.0
            neighbor_ids = {row.get("previous_chunk_id"), row.get("next_chunk_id")}
            adjacent = any(value in selected_ids for value in neighbor_ids if value)
            neighbor_relevance = max(
                (normalized_relevance.get(str(value), 0.0) for value in neighbor_ids if value),
                default=0.0,
            )
            continuity = 1.0 if adjacent and normalized_relevance[identifier] >= (
                float(selection["neighbor_relative_relevance"]) * neighbor_relevance
            ) else 0.0
            redundancy = maximum_redundancy[identifier]
            utility = (
                float(weights["relevance"]) * normalized_relevance[identifier]
                + float(weights["coverage"]) * coverage_gain
                + float(weights["rank"]) * rank_gain
                + float(weights["source_novelty"]) * novelty
                + float(weights["continuity"]) * continuity
                - float(selection["redundancy_penalty"]) * redundancy
            )
            adjusted = utility / (max(1, cost(row)) ** cost_power)
            choices.append((adjusted, identifier, row))
        if not choices:
            break
        _, _, chosen = sorted(choices, key=lambda item: (-item[0], item[1]))[0]
        if not add(chosen):
            break

    covered_weight = sum(
        weight for term, weight in facet_weights.items() if selected_terms.get(term, 0) > 0
    )
    coverage = covered_weight / facet_total if facet_total > 0 else 0.0
    complete = (
        facet_total > 0
        and coverage >= float(selection["minimum_query_coverage"])
        and len(selected_evidence) >= required_evidence
    )
    rows = []
    for rank, row in enumerate(selected, start=1):
        text = hydrate_chunk(row, record_map)
        rows.append(
            {
                "selection_rank": rank,
                "chunk_id": row["chunk_id"],
                "document_id": row["document_id"],
                "source_id": row["source_id"],
                "record_id": row["record_id"],
                "record_sha256": row["record_sha256"],
                "record_char_start": row["record_char_start"],
                "record_char_end": row["record_char_end"],
                "text_sha256": row["text_sha256"],
                "estimated_tokens": row["estimated_tokens"],
                "heading_path": row["heading_path"],
                "previous_chunk_id": row["previous_chunk_id"],
                "next_chunk_id": row["next_chunk_id"],
                "parent_rank": parent_rank[str(row["document_id"])],
                "text": text,
            }
        )
    uncovered = sorted(
        term for term in facet_weights if selected_terms.get(term, 0) == 0
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "pass",
        "authoritative": False,
        "discovery_only": True,
        "query": query,
        "requested_mode": mode,
        "effective_mode": mode,
        "budget": {
            "estimator": plan["chunking"]["token_estimator"],
            "maximum_tokens": budget,
            "used_tokens": used_tokens,
            "chunk_text_tokens": sum(int(row["estimated_tokens"]) for row in selected),
            "returned_chunks": len(rows),
        },
        "quality_guard": {
            "complete": complete,
            "query_coverage": round(coverage, 8),
            "minimum_query_coverage": selection["minimum_query_coverage"],
            "evidence_identities": len(selected_evidence),
            "minimum_evidence_identities": required_evidence,
            "uncovered_retrievable_terms": uncovered,
            "maximum_budget_tokens": selection["maximum_budget_tokens"],
        },
        "selection": {
                "algorithm": "budgeted-query-coverage-mmr-v1",
            "redundancy": "jensen-shannon-similarity-v1",
            "candidate_documents": len(discovery["results"]),
            "candidate_chunks": len(candidates),
        },
        "chunks": rows,
    }
