#!/usr/bin/env python3
"""Validate a classical Semantic OKF bundle and search it with Tantivy."""

from __future__ import annotations

import hashlib
import json
import math
import re
from dataclasses import dataclass
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path, PurePosixPath
from typing import Any, Mapping, Sequence


SCHEMA_VERSION = "1.0"
TANTIVY_VERSION = "0.26.0"
ENGINE_ID = "tantivy-0.26.0-native-bm25-morphology-diversified-v3"
DOCUMENT_ID_RE = re.compile(r"document-[0-9a-f]{32}")
HEX_64 = re.compile(r"[0-9a-f]{64}")
TOKEN_RE = re.compile(r"[A-Za-z0-9]+")
EXPLICIT_QUERY_SYNTAX_RE = re.compile(r'["():]|\b(?:AND|OR|NOT)\b')
CLASSICAL_FILES = {
    "index.json",
    "documents.jsonl",
    "lexicon.json",
    "associations.jsonl",
    "topics.json",
    "build-report.json",
}
CLASSICAL_ALGORITHMS = {
    "bm25": "okapi-bm25f-v1",
    "associations": "windowed-positive-pmi-v1",
    "topics": "deterministic-seeded-weighted-label-propagation-v1",
    "topic_scoring": "normalized-bm25-plus-topic-cosine-v1",
    "association_scoring": "two-step-ppmi-query-propagation-v1",
    "fusion": "reciprocal-rank-fusion-v1",
    "reranking": "topic-and-source-mmr-v1",
}
INDEX_KEYS = {
    "schema_version",
    "authoritative",
    "core",
    "classical_plan_sha256",
    "plan",
    "selection",
    "algorithms",
    "artifacts",
    "summary",
}
DOCUMENT_KEYS = {
    "document_id",
    "source_id",
    "record_id",
    "record_sha256",
    "concept_id",
    "concept_type",
    "concept_path",
    "source_path",
    "paper_id",
    "ordinal",
    "locator",
    "title",
    "text",
    "text_sha256",
    "title_terms",
    "body_terms",
    "title_length",
    "body_length",
    "topic_weights",
}


class SnapshotError(RuntimeError):
    """Describe an invalid snapshot, runtime, filter, or query."""


@dataclass(frozen=True)
class TantivySnapshot:
    """Hold a structurally validated classical passage collection."""

    root: Path
    index: dict[str, Any]
    documents: tuple[dict[str, Any], ...]
    index_sha256: str
    query_unigrams: frozenset[str]


def canonical_json(value: Any) -> str:
    """Serialize JSON deterministically while rejecting non-finite values."""

    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def sha256_bytes(value: bytes) -> str:
    """Return a lowercase SHA-256 digest for bytes."""

    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    """Return a lowercase SHA-256 digest for one file."""

    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_canonical(value: Any) -> str:
    """Hash canonical UTF-8 JSON."""

    return sha256_bytes(canonical_json(value).encode("utf-8"))


def strict_json_loads(payload: str, *, label: str) -> Any:
    """Load JSON while rejecting duplicate members and non-standard numbers."""

    def reject_constant(value: str) -> Any:
        raise SnapshotError(f"{label} contains non-standard number {value!r}")

    def reject_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise SnapshotError(f"{label} contains duplicate member {key!r}")
            result[key] = value
        return result

    try:
        return json.loads(
            payload,
            object_pairs_hook=reject_duplicates,
            parse_constant=reject_constant,
        )
    except json.JSONDecodeError as exc:
        raise SnapshotError(f"{label} is invalid JSON: {exc}") from exc


def _load_json(path: Path, label: str) -> Any:
    try:
        return strict_json_loads(path.read_text(encoding="utf-8"), label=label)
    except (OSError, UnicodeError) as exc:
        raise SnapshotError(f"cannot read {label}: {exc}") from exc


def _read_jsonl(path: Path, label: str) -> list[dict[str, Any]]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        raise SnapshotError(f"cannot read {label}: {exc}") from exc
    rows: list[dict[str, Any]] = []
    for number, line in enumerate(lines, start=1):
        if not line:
            raise SnapshotError(f"{label}:{number} is blank")
        value = strict_json_loads(line, label=f"{label}:{number}")
        if not isinstance(value, dict):
            raise SnapshotError(f"{label}:{number} must be an object")
        rows.append(value)
    return rows


def _exact_keys(value: Mapping[str, Any], expected: set[str], label: str) -> None:
    actual = set(value)
    if actual != expected:
        raise SnapshotError(
            f"{label} has a closed schema; "
            f"missing={sorted(expected - actual)}, unknown={sorted(actual - expected)}"
        )


def _safe_relative(value: Any, label: str) -> PurePosixPath:
    if not isinstance(value, str) or not value or "\\" in value:
        raise SnapshotError(f"{label} is not a safe relative path: {value!r}")
    candidate = PurePosixPath(value)
    if (
        candidate.is_absolute()
        or not candidate.parts
        or any(part in {"", ".", ".."} for part in candidate.parts)
    ):
        raise SnapshotError(f"{label} is not a safe relative path: {value!r}")
    return candidate


def _core_inventory(root: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise SnapshotError(
                f"snapshot contains an unsafe symlink: {path.relative_to(root)}"
            )
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if relative.parts and relative.parts[0] == "classical":
            continue
        rows.append({"path": relative.as_posix(), "sha256": sha256_file(path)})
    return rows


def _artifact(path: Path, relative: str, count: int | None = None) -> dict[str, Any]:
    result: dict[str, Any] = {
        "path": relative,
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }
    if count is not None:
        result["count"] = count
    return result


def _require_tantivy() -> str:
    try:
        installed = version("tantivy")
    except PackageNotFoundError as exc:
        raise SnapshotError(
            "tantivy 0.26.0 is required; install scripts/requirements.txt"
        ) from exc
    if installed != TANTIVY_VERSION:
        raise SnapshotError(
            f"tantivy version mismatch: expected {TANTIVY_VERSION}, found {installed}"
        )
    return installed


def _validate_bm25_plan(index: Mapping[str, Any]) -> dict[str, float]:
    plan = index.get("plan")
    if not isinstance(plan, dict):
        raise SnapshotError("classical index plan must be an object")
    bm25 = plan.get("bm25")
    if not isinstance(bm25, dict):
        raise SnapshotError("classical plan must contain a bm25 object")
    _exact_keys(bm25, {"k1", "b", "title_weight", "body_weight"}, "plan.bm25")
    values: dict[str, float] = {}
    for name in ("k1", "b", "title_weight", "body_weight"):
        value = bm25[name]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise SnapshotError(f"plan.bm25.{name} must be numeric")
        values[name] = float(value)
        if not math.isfinite(values[name]):
            raise SnapshotError(f"plan.bm25.{name} must be finite")
    if values["k1"] != 1.2 or values["b"] != 0.75:
        raise SnapshotError(
            "Tantivy consultation requires the classical k1=1.2 and b=0.75 defaults"
        )
    if values["title_weight"] < 0 or values["body_weight"] < 0:
        raise SnapshotError("BM25 field weights must be nonnegative")
    if values["title_weight"] + values["body_weight"] <= 0:
        raise SnapshotError("at least one BM25 field weight must be positive")
    if index.get("classical_plan_sha256") != sha256_canonical(plan):
        raise SnapshotError("classical plan digest is invalid")
    return values


def _validate_document(
    root: Path,
    document: Mapping[str, Any],
    record_by_key: Mapping[tuple[Any, Any], Mapping[str, Any]],
    number: int,
) -> None:
    label = f"classical/documents.jsonl:{number}"
    _exact_keys(document, DOCUMENT_KEYS, label)
    document_id = document["document_id"]
    if not isinstance(document_id, str) or not DOCUMENT_ID_RE.fullmatch(document_id):
        raise SnapshotError(f"{label} has an invalid document ID")
    for name in (
        "source_id",
        "record_id",
        "record_sha256",
        "concept_id",
        "concept_type",
        "concept_path",
        "source_path",
        "title",
        "text",
        "text_sha256",
    ):
        if not isinstance(document[name], str) or not document[name]:
            raise SnapshotError(f"{label} has an invalid {name}")
    if not HEX_64.fullmatch(document["record_sha256"]) or not HEX_64.fullmatch(
        document["text_sha256"]
    ):
        raise SnapshotError(f"{label} has an invalid digest")
    record = record_by_key.get((document["source_id"], document["record_id"]))
    if record is None:
        raise SnapshotError(f"{label} is orphaned from the authoritative ledger")
    for name in (
        "record_sha256",
        "concept_id",
        "concept_type",
        "concept_path",
        "source_path",
        "title",
    ):
        if document[name] != record.get(name):
            raise SnapshotError(f"{label} {name} differs from its authoritative record")
    concept = _safe_relative(document["concept_path"], "document concept_path")
    if concept.parts[0] != "concepts" or concept.suffix.lower() != ".md":
        raise SnapshotError(f"{label} concept_path is outside concepts/")
    concept_file = root.joinpath(*concept.parts)
    if not concept_file.is_file() or concept_file.is_symlink():
        raise SnapshotError(f"{label} concept file is missing or unsafe")
    text = document["text"]
    if document["text_sha256"] != sha256_bytes(text.encode("utf-8")):
        raise SnapshotError(f"{label} text digest is invalid")
    body = record.get("body")
    locator = document["locator"]
    if locator == {"kind": "record"}:
        if text != body:
            raise SnapshotError(f"{label} record locator does not resolve")
    elif (
        isinstance(locator, dict)
        and set(locator) == {"kind", "start", "end"}
        and locator.get("kind") == "character-range"
    ):
        start, end = locator["start"], locator["end"]
        if (
            isinstance(start, bool)
            or isinstance(end, bool)
            or not isinstance(start, int)
            or not isinstance(end, int)
            or not isinstance(body, str)
            or not 0 <= start < end <= len(body)
            or body[start:end] != text
        ):
            raise SnapshotError(f"{label} character-range locator does not resolve")
    else:
        raise SnapshotError(f"{label} has an invalid locator")


def load_snapshot(root: Path) -> TantivySnapshot:
    """Load and structurally validate one classical snapshot without modifying it."""

    _require_tantivy()
    candidate = root.expanduser()
    if candidate.is_symlink() or not candidate.is_dir():
        raise SnapshotError(
            f"bundle does not exist or is not a real directory: {candidate}"
        )
    root = candidate.resolve()
    classical = root / "classical"
    if not classical.is_dir() or classical.is_symlink():
        raise SnapshotError("classical must be a real directory")
    actual_names = {path.name for path in classical.iterdir()}
    if actual_names != CLASSICAL_FILES:
        raise SnapshotError(
            "classical artifact set is closed; "
            f"missing={sorted(CLASSICAL_FILES - actual_names)}, "
            f"unknown={sorted(actual_names - CLASSICAL_FILES)}"
        )
    if any(path.is_symlink() or not path.is_file() for path in classical.iterdir()):
        raise SnapshotError("classical artifacts must be regular files")

    semantic_report = _load_json(
        root / "semantic" / "build-report.json", "semantic/build-report.json"
    )
    if (
        not isinstance(semantic_report, dict)
        or semantic_report.get("valid") is not True
        or semantic_report.get("status") != "pass"
    ):
        raise SnapshotError("authoritative Semantic OKF build report is not passing")
    index = _load_json(classical / "index.json", "classical/index.json")
    if not isinstance(index, dict):
        raise SnapshotError("classical/index.json root must be an object")
    _exact_keys(index, INDEX_KEYS, "classical index")
    if index["schema_version"] != SCHEMA_VERSION or index["authoritative"] is not False:
        raise SnapshotError("classical index version or authority marker is invalid")
    if index["algorithms"] != CLASSICAL_ALGORITHMS:
        raise SnapshotError("classical algorithm identities are invalid")
    _validate_bm25_plan(index)

    core = {
        "tree_sha256": sha256_canonical(_core_inventory(root)),
        "records_sha256": sha256_file(root / "semantic" / "records.jsonl"),
        "record_count": len(
            _read_jsonl(root / "semantic" / "records.jsonl", "semantic/records.jsonl")
        ),
    }
    if index["core"] != core:
        raise SnapshotError("classical index core binding is stale or invalid")

    records = _read_jsonl(root / "semantic" / "records.jsonl", "semantic/records.jsonl")
    record_by_key = {
        (row.get("source_id"), row.get("record_id")): row for row in records
    }
    if len(record_by_key) != len(records):
        raise SnapshotError(
            "authoritative ledger has duplicate source/record identities"
        )
    documents = _read_jsonl(classical / "documents.jsonl", "classical/documents.jsonl")
    identifiers: list[str] = []
    for number, document in enumerate(documents, start=1):
        _validate_document(root, document, record_by_key, number)
        identifiers.append(document["document_id"])
    if identifiers != sorted(identifiers) or len(identifiers) != len(set(identifiers)):
        raise SnapshotError(
            "classical documents must be uniquely ordered by document ID"
        )

    lexicon = _load_json(classical / "lexicon.json", "classical/lexicon.json")
    associations = _read_jsonl(
        classical / "associations.jsonl", "classical/associations.jsonl"
    )
    topics = _load_json(classical / "topics.json", "classical/topics.json")
    if not isinstance(lexicon, dict) or not isinstance(lexicon.get("terms"), list):
        raise SnapshotError("classical lexicon has an invalid term array")
    query_unigrams = frozenset(
        row["term"]
        for row in lexicon["terms"]
        if isinstance(row, dict)
        and isinstance(row.get("term"), str)
        and " " not in row["term"]
    )
    if not query_unigrams:
        raise SnapshotError("classical lexicon has no unigram query vocabulary")
    if not isinstance(topics, dict) or not isinstance(topics.get("topic_count"), int):
        raise SnapshotError("classical topics has an invalid topic count")
    artifacts = {
        "documents": _artifact(
            classical / "documents.jsonl", "classical/documents.jsonl", len(documents)
        ),
        "lexicon": _artifact(
            classical / "lexicon.json", "classical/lexicon.json", len(lexicon["terms"])
        ),
        "associations": _artifact(
            classical / "associations.jsonl",
            "classical/associations.jsonl",
            len(associations),
        ),
        "topics": _artifact(
            classical / "topics.json", "classical/topics.json", topics["topic_count"]
        ),
    }
    if index["artifacts"] != artifacts:
        raise SnapshotError("classical artifact hashes, sizes, or counts are invalid")
    report = _load_json(classical / "build-report.json", "classical/build-report.json")
    expected_report = {
        "schema_version": SCHEMA_VERSION,
        "valid": True,
        "status": "pass",
        "errors": [],
        "warnings": [],
        "classical_plan_sha256": index["classical_plan_sha256"],
        "core": core,
        "selection": index["selection"],
        "summary": index["summary"],
        "artifacts": {
            "index": _artifact(classical / "index.json", "classical/index.json"),
            **artifacts,
        },
    }
    if report != expected_report:
        raise SnapshotError("classical build report differs from live validation")
    return TantivySnapshot(
        root=root,
        index=index,
        documents=tuple(documents),
        index_sha256=sha256_file(classical / "index.json"),
        query_unigrams=query_unigrams,
    )


def inspect_snapshot(snapshot: TantivySnapshot) -> dict[str, Any]:
    """Return capabilities and authoritative paths for a validated snapshot."""

    installed = _require_tantivy()
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "pass",
        "authoritative": False,
        "discovery_only": True,
        "validation": {"structural": True, "locator_bindings": True},
        "engine": {
            "id": ENGINE_ID,
            "name": "Tantivy",
            "implementation": "Rust",
            "package_version": installed,
            "scoring": "BM25",
            "index_storage": "memory",
            "tokenizer": "default",
        },
        "core_tree_sha256": snapshot.index["core"]["tree_sha256"],
        "classical_index_sha256": snapshot.index_sha256,
        "classical_plan_sha256": snapshot.index["classical_plan_sha256"],
        "summary": snapshot.index["summary"],
        "capabilities": ["tantivy-bm25"],
        "authoritative_paths": {
            "records": "semantic/records.jsonl",
            "concepts": "concepts/",
            "data": "semantic/data.ttl",
            "ontology": "semantic/ontology.ttl",
            "provenance": "semantic/provenance.ttl",
            "shapes": "semantic/shapes.ttl",
            "validation": "semantic/validation-report.ttl",
        },
    }


def _filters(values: Sequence[str], label: str) -> list[str]:
    if any(not isinstance(value, str) or not value.strip() for value in values):
        raise SnapshotError(f"{label} filters must be nonempty strings")
    return sorted(set(values))


def _eligible_documents(
    snapshot: TantivySnapshot,
    source_ids: Sequence[str],
    concept_ids: Sequence[str],
    concept_types: Sequence[str],
) -> tuple[list[dict[str, Any]], dict[str, list[str]]]:
    filters = {
        "source_ids": _filters(source_ids, "source_id"),
        "concept_ids": _filters(concept_ids, "concept_id"),
        "concept_types": _filters(concept_types, "concept_type"),
    }
    selected = [
        document
        for document in snapshot.documents
        if (not filters["source_ids"] or document["source_id"] in filters["source_ids"])
        and (
            not filters["concept_ids"]
            or document["concept_id"] in filters["concept_ids"]
        )
        and (
            not filters["concept_types"]
            or document["concept_type"] in filters["concept_types"]
        )
    ]
    return selected, filters


def _tantivy_search(
    documents: Sequence[dict[str, Any]],
    query_text: str,
    top_k: int,
    boosts: Mapping[str, float],
) -> tuple[list[tuple[float, dict[str, Any]]], int]:
    import tantivy

    builder = tantivy.SchemaBuilder()
    builder.add_text_field("document_id", stored=True, tokenizer_name="raw")
    builder.add_text_field("title", stored=True, index_option="position")
    builder.add_text_field("body", stored=True, index_option="position")
    schema = builder.build()
    index = tantivy.Index(schema)
    with index.writer(num_threads=1) as writer:
        for document in documents:
            writer.add_document(
                tantivy.Document(
                    document_id=document["document_id"],
                    title=document["title"],
                    body=document["text"],
                )
            )
    index.reload()
    try:
        query = index.parse_query(
            query_text,
            ["title", "body"],
            field_boosts={
                "title": boosts["title_weight"],
                "body": boosts["body_weight"],
            },
            allow_regexes=False,
        )
    except ValueError as exc:
        raise SnapshotError(f"invalid Tantivy query: {exc}") from exc
    searcher = index.searcher()
    try:
        search_result = searcher.search(query, limit=len(documents), count=True)
    except ValueError as exc:
        raise SnapshotError(f"Tantivy search failed: {exc}") from exc
    by_id = {document["document_id"]: document for document in documents}
    hits: list[tuple[float, dict[str, Any]]] = []
    for score, address in search_result.hits:
        stored = searcher.doc(address)
        document_id = stored.get_first("document_id")
        document = by_id.get(document_id)
        if document is None:
            raise SnapshotError("Tantivy returned an unknown document identity")
        numeric_score = float(score)
        if not math.isfinite(numeric_score):
            raise SnapshotError("Tantivy returned a non-finite BM25 score")
        hits.append((numeric_score, document))
    hits.sort(key=lambda item: (-item[0], item[1]["document_id"]))
    return hits[:top_k], int(search_result.count)


def _evidence_identity(document: Mapping[str, Any]) -> str:
    """Return the plan-compatible identity used to cap repeated passages."""

    paper_id = document.get("paper_id")
    return paper_id if isinstance(paper_id, str) and paper_id else document["source_id"]


def _inflection_variants(
    vocabulary: frozenset[str],
    term: str,
) -> tuple[str, ...]:
    """Return at most two deterministic lexicon-backed English variants."""

    candidates: list[str] = []
    if term.endswith("ies") and len(term) > 4:
        candidates.append(f"{term[:-3]}y")
    if term.endswith("es") and len(term) > 3:
        candidates.extend((term[:-1], term[:-2]))
    elif term.endswith("s") and not term.endswith("ss") and len(term) > 3:
        candidates.append(term[:-1])
    else:
        candidates.extend((f"{term}s", f"{term}es"))
    if term.endswith("y") and len(term) > 3:
        candidates.append(f"{term[:-1]}ies")
    if term.endswith("ing") and len(term) > 5:
        candidates.extend((term[:-3], f"{term[:-3]}e"))
    if term.endswith("ed") and len(term) > 4:
        candidates.extend((term[:-2], term[:-1]))
    variants: list[str] = []
    for candidate in candidates:
        if (
            candidate != term
            and candidate in vocabulary
            and candidate not in variants
        ):
            variants.append(candidate)
    return tuple(variants[:2])


def _normalized_query(
    snapshot: TantivySnapshot,
    query_text: str,
) -> tuple[str, bool]:
    """Normalize and weakly expand syntax-free text against the unigram lexicon."""

    if EXPLICIT_QUERY_SYNTAX_RE.search(query_text):
        return query_text, False
    terms = [
        term
        for term in TOKEN_RE.findall(query_text.casefold())
        if term in snapshot.query_unigrams
    ]
    if not terms:
        return query_text, False
    clauses: list[str] = []
    for term in terms:
        clauses.append(f"{term}^3.0")
        clauses.extend(
            f"{variant}^0.35"
            for variant in _inflection_variants(snapshot.query_unigrams, term)
        )
    return " ".join(clauses), True


def _diversify_hits(
    hits: Sequence[tuple[float, dict[str, Any]]],
    top_k: int,
    identity_cap: int,
) -> list[tuple[float, dict[str, Any]]]:
    """Keep native score order while limiting passages per evidence identity."""

    selected: list[tuple[float, dict[str, Any]]] = []
    identity_counts: dict[str, int] = {}
    for hit in hits:
        identity = _evidence_identity(hit[1])
        count = identity_counts.get(identity, 0)
        if count >= identity_cap:
            continue
        selected.append(hit)
        identity_counts[identity] = count + 1
        if len(selected) == top_k:
            break
    return selected


def search_snapshot(
    snapshot: TantivySnapshot,
    query: str,
    top_k: int,
    *,
    source_ids: Sequence[str] = (),
    concept_ids: Sequence[str] = (),
    concept_types: Sequence[str] = (),
) -> dict[str, Any]:
    """Search filtered passages through an ephemeral in-memory Tantivy index."""

    _require_tantivy()
    query_text = query.strip()
    if not query_text:
        raise SnapshotError("query must be nonempty")
    if isinstance(top_k, bool) or not isinstance(top_k, int) or not 1 <= top_k <= 100:
        raise SnapshotError("top_k must be an integer from 1 through 100")
    documents, filters = _eligible_documents(
        snapshot, source_ids, concept_ids, concept_types
    )
    boosts = _validate_bm25_plan(snapshot.index)
    parsed_query, normalized = _normalized_query(snapshot, query_text)
    reranking = snapshot.index["plan"].get("reranking")
    if not isinstance(reranking, dict):
        raise SnapshotError("classical plan must contain a reranking object")
    candidate_pool = reranking.get("candidate_pool")
    identity_cap = reranking.get("max_per_evidence_identity")
    if (
        isinstance(candidate_pool, bool)
        or not isinstance(candidate_pool, int)
        or candidate_pool < 1
    ):
        raise SnapshotError(
            "plan.reranking.candidate_pool must be a positive integer"
        )
    if (
        isinstance(identity_cap, bool)
        or not isinstance(identity_cap, int)
        or identity_cap < 1
    ):
        raise SnapshotError(
            "plan.reranking.max_per_evidence_identity must be a positive integer"
        )
    hits: list[tuple[float, dict[str, Any]]] = []
    match_count = 0
    effective_candidate_pool = min(len(documents), max(top_k, candidate_pool))
    if documents:
        native_hits, match_count = _tantivy_search(
            documents,
            parsed_query,
            effective_candidate_pool,
            boosts,
        )
        hits = _diversify_hits(native_hits, top_k, identity_cap)
    results: list[dict[str, Any]] = []
    for rank, (score, document) in enumerate(hits, start=1):
        results.append(
            {
                "rank": rank,
                "score": score,
                **{
                    name: document[name]
                    for name in (
                        "document_id",
                        "source_id",
                        "record_id",
                        "record_sha256",
                        "concept_id",
                        "concept_type",
                        "concept_path",
                        "source_path",
                        "paper_id",
                        "ordinal",
                        "locator",
                        "text",
                        "text_sha256",
                    )
                },
            }
        )
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "pass",
        "authoritative": False,
        "discovery_only": True,
        "query": query_text,
        "parsed_query": parsed_query,
        "requested_mode": "tantivy-bm25",
        "effective_mode": "tantivy-bm25",
        "filters": filters,
        "top_k": top_k,
        "engine": {
            "id": ENGINE_ID,
            "name": "Tantivy",
            "implementation": "Rust",
            "package_version": TANTIVY_VERSION,
            "scoring": "BM25",
            "index_storage": "memory",
            "tokenizer": "default",
            "title_boost": boosts["title_weight"],
            "body_boost": boosts["body_weight"],
            "indexed_documents": len(documents),
            "matched_documents": match_count,
            "candidate_pool": effective_candidate_pool,
            "identity_cap": identity_cap,
            "identity_policy": "paper_id-or-source_id",
            "ranking": "native-score-order-with-identity-cap-v1",
            "returned_identities": len(
                {_evidence_identity(document) for _, document in hits}
            ),
            "query_normalization": (
                "classical-unigram-inflection-v2"
                if normalized
                else "preserved-syntax"
            ),
        },
        "snapshot": {
            "core_tree_sha256": snapshot.index["core"]["tree_sha256"],
            "classical_index_sha256": snapshot.index_sha256,
            "classical_plan_sha256": snapshot.index["classical_plan_sha256"],
        },
        "result_count": len(results),
        "results": results,
    }
