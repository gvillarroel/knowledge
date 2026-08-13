#!/usr/bin/env python3
"""Validate Tika/MALLET Semantic OKF and query it with in-memory Tantivy."""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Mapping, Sequence

from _mallet_topics import (
    MalletRuntime,
    MalletRuntimeError,
    derive_topics,
    preflight_mallet,
    validate_toolchain,
)
from _tika_snapshot import TikaSnapshotError, validate_tika_snapshot
from _safe_paths import (
    UnsafePathError,
    paths_overlap,
    require_real_directory,
    require_regular_file,
    scan_regular_tree,
)


SCHEMA_VERSION = "1.0"
CONCEPT_LAYOUT_SOURCE_PACKED = "source-packed-v1"
STRUCTURED_SOURCE_KINDS = {"csv", "json", "rdf"}
TANTIVY_VERSION = "0.26.0"
ENGINE_ID = "tika-mallet-tantivy-0.26.0-fusion-v1"
TOKENIZER_ID = "ascii-alphanumeric-v1"
STOPWORDS_ID = "english-v1"
TOKEN_RE = re.compile(r"[a-z0-9]+", re.ASCII | re.IGNORECASE)
EXPLICIT_QUERY_SYNTAX_RE = re.compile(r'["():]|\b(?:AND|OR|NOT)\b')
PAGE_RE = re.compile(r"(?m)^## PDF page \d+\s*$")
PAPER_RE = re.compile(r"(?<!\d)(\d{4})[.-](\d{5}v\d+)(?!\d)", re.IGNORECASE)
HEX_64 = re.compile(r"[0-9a-f]{64}")
DOCUMENT_ID_RE = re.compile(r"document-[0-9a-f]{32}")
ALGORITHMS = {
    "bm25": "okapi-bm25f-v1",
    "associations": "windowed-positive-pmi-v1",
    "topics": "mallet-2.1.0-parallel-topic-model-v1",
    "topic_scoring": "normalized-bm25-plus-topic-cosine-v1",
    "association_scoring": "two-step-ppmi-query-propagation-v1",
    "fusion": "reciprocal-rank-fusion-v1",
    "reranking": "topic-and-source-mmr-v1",
}
PLAN_KEYS = {
    "schema_version",
    "selection",
    "tokenization",
    "bm25",
    "associations",
    "topics",
    "expansion",
    "reranking",
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
STOPWORDS = frozenset(
    "a about above after again against all am an and any are as at be because been before being below "
    "between both but by can could did do does doing down during each few for from further had has have "
    "having he her here hers herself him himself his how i if in into is it its itself just me more most "
    "my myself no nor not now of off on once only or other our ours ourselves out over own same she should "
    "so some such than that the their theirs them themselves then there these they this those through to too "
    "under until up very was we were what when where which while who whom why will with you your yours "
    "yourself yourselves".split()
)


class SnapshotError(RuntimeError):
    """Describe an invalid snapshot, runtime, filter, or hybrid search request."""


@dataclass(frozen=True)
class ClassicalSnapshot:
    """Hold one fully validated in-memory classical retrieval snapshot."""

    root: Path
    tika: dict[str, Any]
    index: dict[str, Any]
    documents: tuple[dict[str, Any], ...]
    lexicon: dict[str, Any]
    associations: tuple[dict[str, Any], ...]
    topics: dict[str, Any]
    index_sha256: str
    deep_validation: bool


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
    """Return a lowercase SHA-256 digest for bytes."""

    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    """Return a lowercase SHA-256 digest for one file."""

    try:
        path = require_regular_file(path, label="file to hash")
    except UnsafePathError as exc:
        raise SnapshotError(str(exc)) from exc
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_canonical(value: Any) -> str:
    """Hash canonical UTF-8 JSON."""

    return sha256_bytes(canonical_json(value).encode("utf-8"))


def strict_json_loads(payload: str, *, label: str) -> Any:
    """Load JSON while rejecting duplicate keys and non-standard numbers."""

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
            payload, object_pairs_hook=reject_duplicates, parse_constant=reject_constant
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
            f"{label} has a closed schema; missing={sorted(expected - actual)}, unknown={sorted(actual - expected)}"
        )


def _safe_relative(value: str, label: str) -> PurePosixPath:
    candidate = PurePosixPath(value.replace("\\", "/"))
    if (
        candidate.is_absolute()
        or not candidate.parts
        or any(part in {"", ".", ".."} for part in candidate.parts)
    ):
        raise SnapshotError(f"{label} is not a safe relative path: {value!r}")
    return candidate


def _core_inventory(root: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    try:
        files, _ = scan_regular_tree(root, label="Semantic OKF bundle")
    except UnsafePathError as exc:
        raise SnapshotError(str(exc)) from exc
    for path in files:
        relative = path.relative_to(root)
        if relative.parts and relative.parts[0] == "classical":
            continue
        rows.append({"path": relative.as_posix(), "sha256": sha256_file(path)})
    return rows


SEMANTIC_FILES = {
    "build-report.json",
    "data.ttl",
    "ontology.ttl",
    "provenance.ttl",
    "records.jsonl",
    "semantic-plan.json",
    "shapes.ttl",
    "source-manifest.json",
    "validation-report.ttl",
}


def _validate_closed_layout(root: Path) -> None:
    """Reject links, device files, and unknown authoritative root/semantic entries."""

    try:
        files, directories = scan_regular_tree(root, label="Semantic OKF bundle")
    except UnsafePathError as exc:
        raise SnapshotError(str(exc)) from exc
    root_files = {path.name for path in files if path.parent == root}
    root_directories = {path.name for path in directories if path.parent == root}
    expected_directories = {"classical", "concepts", "semantic", "tika"}
    if root_files != {"index.md"} or root_directories != expected_directories:
        raise SnapshotError(
            "bundle root is closed; "
            f"files={sorted(root_files)}, directories={sorted(root_directories)}"
        )
    semantic = root / "semantic"
    semantic_files = {path.name for path in files if path.parent == semantic}
    semantic_directories = [path for path in directories if semantic in path.parents]
    if semantic_files != SEMANTIC_FILES or semantic_directories:
        raise SnapshotError(
            "semantic artifact set is closed; "
            f"missing={sorted(SEMANTIC_FILES - semantic_files)}, "
            f"unknown={sorted(semantic_files - SEMANTIC_FILES)}"
        )


def _validate_concept_tree(root: Path, records: Sequence[Mapping[str, Any]]) -> None:
    """Require exactly the concept files and directories named by the ledger."""

    expected_files: set[str] = set()
    expected_directories: set[str] = set()
    for number, record in enumerate(records, start=1):
        raw = record.get("concept_path")
        if not isinstance(raw, str):
            raise SnapshotError(f"semantic record {number} has no concept_path")
        relative = _safe_relative(raw.replace("\\", "/"), "record concept_path")
        if relative.parts[0] != "concepts" or relative.suffix.casefold() != ".md":
            raise SnapshotError("record concept_path must name a Markdown file under concepts/")
        value = relative.as_posix()
        if value in expected_files:
            raise SnapshotError(f"duplicate record concept_path: {value}")
        expected_files.add(value)
        parents = relative.parts[:-1]
        while len(parents) > 1:
            expected_directories.add(PurePosixPath(*parents).as_posix())
            parents = parents[:-1]
    try:
        files, directories = scan_regular_tree(root / "concepts", label="concept tree")
    except UnsafePathError as exc:
        raise SnapshotError(str(exc)) from exc
    actual_files = {path.relative_to(root).as_posix() for path in files}
    actual_directories = {path.relative_to(root).as_posix() for path in directories}
    if actual_files != expected_files or actual_directories != expected_directories:
        raise SnapshotError(
            "concept tree differs from the authoritative ledger; "
            f"missing_files={sorted(expected_files - actual_files)}, "
            f"unknown_files={sorted(actual_files - expected_files)}, "
            f"unknown_directories={sorted(actual_directories - expected_directories)}"
        )


def _plain_int(value: Any, label: str, minimum: int, maximum: int) -> int:
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or not minimum <= value <= maximum
    ):
        raise SnapshotError(
            f"{label} must be an integer from {minimum} through {maximum}"
        )
    return value


def _finite(value: Any, label: str, minimum: float, maximum: float) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise SnapshotError(f"{label} must be numeric")
    result = float(value)
    if not math.isfinite(result) or not minimum <= result <= maximum:
        raise SnapshotError(f"{label} must be finite from {minimum} through {maximum}")
    return result


def _validate_plan(plan: Any) -> dict[str, Any]:
    if not isinstance(plan, dict):
        raise SnapshotError("classical index plan must be an object")
    _exact_keys(plan, PLAN_KEYS, "classical index plan")
    if plan["schema_version"] != SCHEMA_VERSION:
        raise SnapshotError("classical plan schema version is invalid")
    selection = plan["selection"]
    if not isinstance(selection, dict):
        raise SnapshotError("plan.selection must be an object")
    _exact_keys(selection, {"source_ids"}, "plan.selection")
    source_ids = selection["source_ids"]
    if (
        not isinstance(source_ids, list)
        or not source_ids
        or any(not isinstance(item, str) or not item for item in source_ids)
        or source_ids != sorted(set(source_ids))
    ):
        raise SnapshotError(
            "plan.selection.source_ids must be sorted, unique, and nonempty"
        )
    tokenization = plan["tokenization"]
    if not isinstance(tokenization, dict):
        raise SnapshotError("plan.tokenization must be an object")
    _exact_keys(
        tokenization,
        {"tokenizer", "stopwords", "min_token_length", "ngram_range"},
        "plan.tokenization",
    )
    if (
        tokenization["tokenizer"] != TOKENIZER_ID
        or tokenization["stopwords"] != STOPWORDS_ID
    ):
        raise SnapshotError("unsupported tokenizer or stopword identity")
    _plain_int(tokenization["min_token_length"], "min_token_length", 1, 12)
    if tokenization["ngram_range"] not in ([1, 1], [1, 2]):
        raise SnapshotError("unsupported ngram range")

    bm25 = plan["bm25"]
    if not isinstance(bm25, dict):
        raise SnapshotError("plan.bm25 must be an object")
    _exact_keys(bm25, {"k1", "b", "title_weight", "body_weight"}, "plan.bm25")
    _finite(bm25["k1"], "plan.bm25.k1", 0.01, 10.0)
    _finite(bm25["b"], "plan.bm25.b", 0.0, 1.0)
    _finite(bm25["title_weight"], "plan.bm25.title_weight", 0.0, 100.0)
    _finite(bm25["body_weight"], "plan.bm25.body_weight", 0.0, 100.0)
    if float(bm25["title_weight"]) + float(bm25["body_weight"]) <= 0:
        raise SnapshotError("at least one BM25 field weight must be positive")

    associations = plan["associations"]
    if not isinstance(associations, dict):
        raise SnapshotError("plan.associations must be an object")
    _exact_keys(
        associations,
        {
            "window_size",
            "min_document_frequency",
            "min_cooccurrence",
            "max_vocabulary",
            "max_neighbors",
            "minimum_ppmi",
        },
        "plan.associations",
    )
    _plain_int(associations["window_size"], "window_size", 2, 64)
    _plain_int(
        associations["min_document_frequency"], "min_document_frequency", 1, 1_000_000
    )
    _plain_int(associations["min_cooccurrence"], "min_cooccurrence", 1, 1_000_000)
    _plain_int(associations["max_vocabulary"], "max_vocabulary", 32, 50_000)
    _plain_int(associations["max_neighbors"], "max_neighbors", 1, 128)
    _finite(associations["minimum_ppmi"], "minimum_ppmi", 0.0, 100.0)

    topics = plan["topics"]
    if not isinstance(topics, dict):
        raise SnapshotError("plan.topics must be an object")
    _exact_keys(
        topics,
        {
            "topic_count",
            "num_iterations",
            "num_threads",
            "num_icm_iterations",
            "optimize_interval",
            "optimize_burn_in",
            "alpha_sum",
            "beta",
            "random_seed",
            "min_document_frequency",
            "max_document_fraction",
            "top_terms",
            "timeout_seconds",
        },
        "plan.topics",
    )
    _plain_int(topics["topic_count"], "topic_count", 2, 128)
    num_iterations = _plain_int(
        topics["num_iterations"], "num_iterations", 1, 10000
    )
    if topics["num_threads"] != 1:
        raise SnapshotError("plan.topics.num_threads must be 1 for reproducibility")
    _plain_int(topics["num_threads"], "num_threads", 1, 1)
    _plain_int(topics["num_icm_iterations"], "num_icm_iterations", 0, 10000)
    _plain_int(topics["optimize_interval"], "optimize_interval", 0, 10000)
    optimize_burn_in = _plain_int(
        topics["optimize_burn_in"], "optimize_burn_in", 0, 10000
    )
    if optimize_burn_in > num_iterations:
        raise SnapshotError(
            "plan.topics.optimize_burn_in cannot exceed num_iterations"
        )
    _finite(topics["alpha_sum"], "alpha_sum", 0.000000001, 10000.0)
    _finite(topics["beta"], "beta", 0.000000001, 100.0)
    _plain_int(topics["random_seed"], "random_seed", 1, 2147483647)
    _plain_int(
        topics["min_document_frequency"],
        "min_document_frequency",
        1,
        1000000,
    )
    _finite(topics["max_document_fraction"], "max_document_fraction", 0.000000001, 1.0)
    _plain_int(topics["top_terms"], "top_terms", 3, 100)
    _plain_int(topics["timeout_seconds"], "timeout_seconds", 1, 3600)

    expansion = plan["expansion"]
    if not isinstance(expansion, dict):
        raise SnapshotError("plan.expansion must be an object")
    _exact_keys(
        expansion,
        {"association_terms", "topic_terms", "association_weight", "topic_weight"},
        "plan.expansion",
    )
    _plain_int(expansion["association_terms"], "association_terms", 0, 64)
    _plain_int(expansion["topic_terms"], "topic_terms", 0, 64)
    _finite(expansion["association_weight"], "association_weight", 0.0, 1.0)
    _finite(expansion["topic_weight"], "topic_weight", 0.0, 1.0)

    reranking = plan["reranking"]
    if not isinstance(reranking, dict):
        raise SnapshotError("plan.reranking must be an object")
    _exact_keys(
        reranking,
        {
            "candidate_pool",
            "relevance_weight",
            "topic_novelty_weight",
            "source_novelty_weight",
            "max_per_evidence_identity",
            "rrf_k",
        },
        "plan.reranking",
    )
    _plain_int(reranking["candidate_pool"], "candidate_pool", 10, 10_000)
    _plain_int(
        reranking["max_per_evidence_identity"], "max_per_evidence_identity", 1, 100
    )
    _plain_int(reranking["rrf_k"], "rrf_k", 1, 10_000)
    weights = [
        _finite(reranking[name], f"plan.reranking.{name}", 0.0, 1.0)
        for name in (
            "relevance_weight",
            "topic_novelty_weight",
            "source_novelty_weight",
        )
    ]
    if not math.isclose(
        sum(weights),
        1.0,
        rel_tol=0.0,
        abs_tol=1e-9,
    ):
        raise SnapshotError("reranking weights must sum to one")
    return json.loads(canonical_json(plan))


def _unigrams(value: str, plan: Mapping[str, Any]) -> list[str]:
    minimum = int(plan["tokenization"]["min_token_length"])
    return [
        token
        for token in TOKEN_RE.findall(value.casefold())
        if len(token) >= minimum and token not in STOPWORDS
    ]


def tokenize(value: str, plan: Mapping[str, Any]) -> list[str]:
    """Tokenize a query or evidence passage with the persisted contract."""

    words = _unigrams(value, plan)
    if plan["tokenization"]["ngram_range"] == [1, 1]:
        return words
    return [*words, *(f"{left} {right}" for left, right in zip(words, words[1:]))]


def _counter_object(tokens: Sequence[str]) -> dict[str, int]:
    return dict(sorted(Counter(tokens).items()))


def _select_records(
    records: Sequence[dict[str, Any]],
    sources: Sequence[dict[str, Any]],
    plan: Mapping[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    source_by_id = {
        str(source["id"]): source
        for source in sources
        if isinstance(source.get("id"), str) and source["id"]
    }
    requested = plan["selection"]["source_ids"]
    missing = sorted(set(requested) - set(source_by_id))
    if missing:
        raise SnapshotError(f"classical plan selects unknown source IDs: {missing}")
    requested_set = set(requested)
    selected = [
        record for record in records if record.get("source_id") in requested_set
    ]
    eligible = sorted({str(record.get("source_id")) for record in selected})
    if eligible != requested:
        raise SnapshotError(
            f"selected source IDs produced no eligible records: {sorted(set(requested) - set(eligible))}"
        )
    inventory = [
        {
            "source_id": source_id,
            "content_sha256": source_by_id[source_id].get("content_sha256"),
        }
        for source_id in eligible
    ]
    if any(not HEX_64.fullmatch(str(row["content_sha256"])) for row in inventory):
        raise SnapshotError(
            "selected source inventory contains an invalid content digest"
        )
    selection = {
        "requested_source_ids": list(requested),
        "eligible_source_ids": eligible,
        "excluded_source_ids": sorted(set(source_by_id) - set(requested)),
        "input_count": len(inventory),
        "input_sha256": sha256_canonical(inventory),
    }
    return sorted(
        selected, key=lambda row: (str(row.get("source_id")), str(row.get("record_id")))
    ), selection


def _paper_id(record: Mapping[str, Any]) -> str | None:
    for value in (
        record.get("source_id"),
        record.get("record_id"),
        record.get("source_path"),
        record.get("title"),
    ):
        if isinstance(value, str):
            match = PAPER_RE.search(value)
            if match:
                return f"{match.group(1)}.{match.group(2).lower()}"
    return None


def _trimmed_range(body: str, start: int, end: int) -> tuple[int, int] | None:
    while start < end and body[start].isspace():
        start += 1
    while end > start and body[end - 1].isspace():
        end -= 1
    return (start, end) if start < end else None


def _passage_ranges(record: Mapping[str, Any]) -> list[tuple[int, int]]:
    body = str(record.get("body") or "")
    matches = list(PAGE_RE.finditer(body))
    if not matches:
        trimmed = _trimmed_range(body, 0, len(body))
        return [trimmed] if trimmed is not None else []
    starts = [0, *(match.start() for match in matches[1:])]
    ends = [*(match.start() for match in matches[1:]), len(body)]
    return [
        item
        for pair in zip(starts, ends, strict=True)
        if (item := _trimmed_range(body, *pair))
    ]


def _document_id(row: Mapping[str, Any]) -> str:
    identity = {
        "source_id": row["source_id"],
        "record_id": row["record_id"],
        "record_sha256": row["record_sha256"],
        "ordinal": row["ordinal"],
        "text_sha256": row["text_sha256"],
    }
    return "document-" + sha256_canonical(identity)[:32]


def _derive_documents(
    records: Sequence[dict[str, Any]], plan: Mapping[str, Any]
) -> list[dict[str, Any]]:
    documents: list[dict[str, Any]] = []
    for record in records:
        required = (
            "source_id",
            "record_id",
            "record_sha256",
            "concept_id",
            "concept_type",
            "concept_path",
            "source_path",
            "title",
            "body",
        )
        if any(
            not isinstance(record.get(name), str) or not record[name]
            for name in required
        ):
            raise SnapshotError(
                "selected authoritative record has an invalid required identity or body"
            )
        concept_path = str(record["concept_path"]).replace("\\", "/")
        safe = _safe_relative(concept_path, "record concept_path")
        if safe.parts[0] != "concepts":
            raise SnapshotError(
                f"record concept_path is outside concepts/: {concept_path}"
            )
        body = str(record["body"])
        ranges = _passage_ranges(record)
        if not ranges:
            raise SnapshotError(
                f"record {record['source_id']}/{record['record_id']} has no indexable text"
            )
        for ordinal, (start, end) in enumerate(ranges):
            text = body[start:end]
            locator: dict[str, Any]
            if start == 0 and end == len(body):
                locator = {"kind": "record"}
            else:
                locator = {"kind": "character-range", "start": start, "end": end}
            title = str(record["title"])
            title_tokens = tokenize(title, plan)
            body_tokens = tokenize(text, plan)
            row: dict[str, Any] = {
                "document_id": "",
                "source_id": str(record["source_id"]),
                "record_id": str(record["record_id"]),
                "record_sha256": str(record["record_sha256"]),
                "concept_id": str(record["concept_id"]),
                "concept_type": str(record["concept_type"]),
                "concept_path": concept_path,
                "source_path": str(record["source_path"]).replace("\\", "/"),
                "paper_id": _paper_id(record),
                "ordinal": ordinal,
                "locator": locator,
                "title": title,
                "text": text,
                "text_sha256": sha256_bytes(text.encode("utf-8")),
                "title_terms": _counter_object(title_tokens),
                "body_terms": _counter_object(body_tokens),
                "title_length": len(title_tokens),
                "body_length": len(body_tokens),
                "topic_weights": [],
            }
            row["document_id"] = _document_id(row)
            documents.append(row)
    return sorted(documents, key=lambda row: row["document_id"])


def _derive_lexicon(
    documents: Sequence[dict[str, Any]], plan: Mapping[str, Any]
) -> dict[str, Any]:
    document_frequency: Counter[str] = Counter()
    corpus_frequency: Counter[str] = Counter()
    for document in documents:
        combined = Counter(document["title_terms"]) + Counter(document["body_terms"])
        document_frequency.update(combined.keys())
        corpus_frequency.update(combined)
    count = len(documents)
    terms = []
    for term in sorted(document_frequency):
        df = document_frequency[term]
        terms.append(
            {
                "term": term,
                "document_frequency": df,
                "corpus_frequency": corpus_frequency[term],
                "idf": round(math.log(1.0 + (count - df + 0.5) / (df + 0.5)), 10),
            }
        )
    return {
        "schema_version": SCHEMA_VERSION,
        "tokenization": plan["tokenization"],
        "bm25": plan["bm25"],
        "document_count": count,
        "average_field_lengths": {
            "title": round(sum(row["title_length"] for row in documents) / count, 10),
            "body": round(sum(row["body_length"] for row in documents) / count, 10),
        },
        "terms": terms,
    }


def _derive_associations(
    documents: Sequence[dict[str, Any]],
    lexicon: Mapping[str, Any],
    plan: Mapping[str, Any],
) -> list[dict[str, Any]]:
    config = plan["associations"]
    candidates = [
        row
        for row in lexicon["terms"]
        if " " not in row["term"]
        and row["document_frequency"] >= config["min_document_frequency"]
    ]
    candidates.sort(
        key=lambda row: (
            -row["document_frequency"],
            -row["corpus_frequency"],
            row["term"],
        )
    )
    vocabulary = {row["term"] for row in candidates[: config["max_vocabulary"]]}
    statistics = {row["term"]: row for row in candidates if row["term"] in vocabulary}
    positions: Counter[str] = Counter()
    pairs: Counter[tuple[str, str]] = Counter()
    pair_total = 0
    position_total = 0
    window = config["window_size"]
    for document in documents:
        sequence = [
            token
            for token in _unigrams(f"{document['title']} {document['text']}", plan)
            if token in vocabulary
        ]
        positions.update(sequence)
        position_total += len(sequence)
        for left_index, left in enumerate(sequence):
            for right in sequence[left_index + 1 : left_index + window + 1]:
                if left == right:
                    continue
                pairs[tuple(sorted((left, right)))] += 1
                pair_total += 1
    neighbors: dict[str, list[dict[str, Any]]] = {term: [] for term in vocabulary}
    if pair_total and position_total:
        for (left, right), count in pairs.items():
            if count < config["min_cooccurrence"]:
                continue
            probability_pair = count / pair_total
            probability_left = positions[left] / position_total
            probability_right = positions[right] / position_total
            ppmi = max(
                0.0, math.log(probability_pair / (probability_left * probability_right))
            )
            if ppmi < config["minimum_ppmi"] or ppmi <= 0.0:
                continue
            weight = round(ppmi, 8)
            neighbors[left].append(
                {"term": right, "cooccurrence": count, "ppmi": weight}
            )
            neighbors[right].append(
                {"term": left, "cooccurrence": count, "ppmi": weight}
            )
    rows: list[dict[str, Any]] = []
    for term in sorted(vocabulary):
        ranked = sorted(
            neighbors[term],
            key=lambda row: (-row["ppmi"], -row["cooccurrence"], row["term"]),
        )[: config["max_neighbors"]]
        rows.append(
            {
                "term": term,
                "document_frequency": statistics[term]["document_frequency"],
                "corpus_frequency": statistics[term]["corpus_frequency"],
                "neighbors": ranked,
            }
        )
    return rows


def _association_graph(rows: Sequence[dict[str, Any]]) -> dict[str, dict[str, float]]:
    graph: dict[str, dict[str, float]] = {row["term"]: {} for row in rows}
    for row in rows:
        term = row["term"]
        for neighbor in row["neighbors"]:
            other = neighbor["term"]
            weight = float(neighbor["ppmi"])
            graph.setdefault(term, {})[other] = max(
                graph.get(term, {}).get(other, 0.0), weight
            )
            graph.setdefault(other, {})[term] = max(
                graph.get(other, {}).get(term, 0.0), weight
            )
    return graph


def _derive_topics(
    documents: list[dict[str, Any]],
    plan: Mapping[str, Any],
    runtime: MalletRuntime,
    *,
    forbidden_roots: Sequence[Path] = (),
) -> dict[str, Any]:
    """Retrain the fixed-seed one-thread Java MALLET topic projection."""

    try:
        return derive_topics(
            documents,
            plan,
            runtime,
            _unigrams,
            forbidden_roots=forbidden_roots,
        )
    except MalletRuntimeError as exc:
        raise SnapshotError(str(exc)) from exc


def _derive_all(
    records: Sequence[dict[str, Any]],
    plan: Mapping[str, Any],
    runtime: MalletRuntime,
    *,
    forbidden_roots: Sequence[Path] = (),
) -> tuple[list[dict[str, Any]], dict[str, Any], list[dict[str, Any]], dict[str, Any]]:
    documents = _derive_documents(records, plan)
    lexicon = _derive_lexicon(documents, plan)
    associations = _derive_associations(documents, lexicon, plan)
    topics = _derive_topics(
        documents, plan, runtime, forbidden_roots=forbidden_roots
    )
    return documents, lexicon, associations, topics


def _artifact(path: Path, relative: str, count: int | None = None) -> dict[str, Any]:
    result: dict[str, Any] = {
        "path": relative,
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }
    if count is not None:
        result["count"] = count
    return result


def _validate_packed_record(
    concept_file: Path, record: Mapping[str, Any], label: str
) -> None:
    """Verify one packed anchor and its complete authoritative record body."""

    digest = record.get("record_sha256")
    body = record.get("body")
    title = record.get("title")
    if not isinstance(digest, str) or not isinstance(body, str):
        raise SnapshotError(f"{label} has invalid packed record identity")
    marker = f'<a id="record-{digest[:16]}"></a>\n\n'
    try:
        text = concept_file.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise SnapshotError(f"{label} packed concept is unreadable") from exc
    if text.count(marker) != 1:
        raise SnapshotError(f"{label} packed concept anchor is missing or duplicated")
    remainder = text.split(marker, 1)[1]
    expected = body.rstrip() or f"# {title}"
    if not remainder.startswith(expected):
        raise SnapshotError(f"{label} packed concept body differs from the ledger")
    boundary = remainder[len(expected) :]
    if boundary != "\n" and not boundary.startswith("\n\n---\n\n<a id=\""):
        raise SnapshotError(f"{label} packed concept record boundary is invalid")


def _validate_documents(
    root: Path,
    documents: Sequence[dict[str, Any]],
    records: Sequence[dict[str, Any]],
    plan: Mapping[str, Any],
    topics: Mapping[str, Any],
    semantic_report: Mapping[str, Any],
) -> None:
    record_by_key = {
        (row.get("source_id"), row.get("record_id")): row for row in records
    }
    if len(record_by_key) != len(records):
        raise SnapshotError(
            "authoritative ledger contains duplicate source/record identities"
        )
    term_topics = {row["term"]: row["topic_id"] for row in topics["term_topics"]}
    topic_ids = {row["topic_id"] for row in topics["topics"]}
    source_counts = Counter(str(record.get("source_id")) for record in records)
    processor = semantic_report.get("processor")
    concept_layout = (
        processor.get("concept_layout") if isinstance(processor, Mapping) else None
    )
    ids: list[str] = []
    for number, document in enumerate(documents, start=1):
        _exact_keys(document, DOCUMENT_KEYS, f"classical/documents.jsonl:{number}")
        if not isinstance(document["document_id"], str) or not DOCUMENT_ID_RE.fullmatch(
            document["document_id"]
        ):
            raise SnapshotError(
                f"classical/documents.jsonl:{number} has an invalid document ID"
            )
        if document["document_id"] != _document_id(document):
            raise SnapshotError(
                f"classical/documents.jsonl:{number} has a stale document ID"
            )
        ids.append(document["document_id"])
        record = record_by_key.get((document["source_id"], document["record_id"]))
        if record is None:
            raise SnapshotError(
                f"classical/documents.jsonl:{number} is orphaned from the ledger"
            )
        for field in (
            "record_sha256",
            "concept_id",
            "concept_type",
            "concept_path",
            "source_path",
            "title",
        ):
            if document[field] != record.get(field):
                raise SnapshotError(
                    f"classical/documents.jsonl:{number} {field} differs from its record"
                )
        if document["paper_id"] != _paper_id(record):
            raise SnapshotError(
                f"classical/documents.jsonl:{number} paper identity differs from its record"
            )
        if (
            isinstance(document["ordinal"], bool)
            or not isinstance(document["ordinal"], int)
            or document["ordinal"] < 0
        ):
            raise SnapshotError(
                f"classical/documents.jsonl:{number} has an invalid ordinal"
            )
        concept = _safe_relative(document["concept_path"], "document concept_path")
        if concept.parts[0] != "concepts":
            raise SnapshotError("document concept path is outside concepts/")
        packed = (
            concept_layout == CONCEPT_LAYOUT_SOURCE_PACKED
            and record.get("source_kind") in STRUCTURED_SOURCE_KINDS
            and source_counts[str(record.get("source_id"))] > 1
        )
        if packed:
            collection = _safe_relative(
                f"concepts/{record.get('source_id')}.md",
                "packed concept collection",
            )
            concept_file = root.joinpath(*collection.parts)
        else:
            concept_file = root.joinpath(*concept.parts)
        if not concept_file.is_file() or concept_file.is_symlink():
            raise SnapshotError(
                f"document concept file is missing or unsafe: {document['concept_path']}"
            )
        if packed:
            _validate_packed_record(concept_file, record, f"document {number}")
        text = document["text"]
        if (
            not isinstance(text, str)
            or not text
            or document["text_sha256"] != sha256_bytes(text.encode("utf-8"))
        ):
            raise SnapshotError(
                f"classical/documents.jsonl:{number} has invalid text or text hash"
            )
        body = record.get("body")
        locator = document["locator"]
        if locator == {"kind": "record"}:
            if text != body:
                raise SnapshotError(
                    f"classical/documents.jsonl:{number} record locator does not resolve"
                )
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
                raise SnapshotError(
                    f"classical/documents.jsonl:{number} character locator does not resolve"
                )
        else:
            raise SnapshotError(
                f"classical/documents.jsonl:{number} has an invalid locator"
            )
        expected_title = _counter_object(tokenize(document["title"], plan))
        expected_body = _counter_object(tokenize(text, plan))
        if (
            document["title_terms"] != expected_title
            or document["body_terms"] != expected_body
        ):
            raise SnapshotError(
                f"classical/documents.jsonl:{number} token counts do not match text"
            )
        if document["title_length"] != sum(expected_title.values()) or document[
            "body_length"
        ] != sum(expected_body.values()):
            raise SnapshotError(
                f"classical/documents.jsonl:{number} field lengths are invalid"
            )
        seen_topics: set[str] = set()
        for item in document["topic_weights"]:
            if not isinstance(item, dict) or set(item) != {"topic_id", "weight"}:
                raise SnapshotError(
                    f"classical/documents.jsonl:{number} has invalid topic weights"
                )
            if item["topic_id"] not in topic_ids or item["topic_id"] in seen_topics:
                raise SnapshotError(
                    f"classical/documents.jsonl:{number} has an unknown or duplicate topic"
                )
            if (
                isinstance(item["weight"], bool)
                or not isinstance(item["weight"], (int, float))
                or not 0 < float(item["weight"]) <= 1
            ):
                raise SnapshotError(
                    f"classical/documents.jsonl:{number} has an invalid topic weight"
                )
            seen_topics.add(item["topic_id"])
        if document["topic_weights"] != sorted(
            document["topic_weights"], key=lambda item: item["topic_id"]
        ):
            raise SnapshotError(
                f"classical/documents.jsonl:{number} topic weights are not ordered"
            )
        if seen_topics != topic_ids or not math.isclose(
            sum(float(item["weight"]) for item in document["topic_weights"]),
            1.0,
            rel_tol=0.0,
            abs_tol=0.000001,
        ):
            raise SnapshotError(
                f"classical/documents.jsonl:{number} MALLET topic distribution is incomplete"
            )
        combined = Counter(expected_title) + Counter(expected_body)
        expected_topics = {
            term_topics[term] for term in combined if term in term_topics
        }
        if expected_topics and not seen_topics:
            raise SnapshotError(
                f"classical/documents.jsonl:{number} is missing derived topic weights"
            )
    if ids != sorted(ids) or len(ids) != len(set(ids)):
        raise SnapshotError(
            "classical documents must be uniquely ordered by document ID"
        )


def _validate_associations(
    associations: Sequence[dict[str, Any]],
    lexicon: Mapping[str, Any],
    plan: Mapping[str, Any],
) -> None:
    term_stats = {row["term"]: row for row in lexicon["terms"]}
    terms: list[str] = []
    maximum = int(plan["associations"]["max_neighbors"])
    for number, row in enumerate(associations, start=1):
        if not isinstance(row, dict) or set(row) != {
            "term",
            "document_frequency",
            "corpus_frequency",
            "neighbors",
        }:
            raise SnapshotError(
                f"classical/associations.jsonl:{number} has an invalid shape"
            )
        term = row["term"]
        if term not in term_stats or " " in term:
            raise SnapshotError(
                f"classical/associations.jsonl:{number} has an unknown term"
            )
        if (
            row["document_frequency"] != term_stats[term]["document_frequency"]
            or row["corpus_frequency"] != term_stats[term]["corpus_frequency"]
        ):
            raise SnapshotError(
                f"classical/associations.jsonl:{number} statistics differ from the lexicon"
            )
        if not isinstance(row["neighbors"], list) or len(row["neighbors"]) > maximum:
            raise SnapshotError(
                f"classical/associations.jsonl:{number} has an invalid neighbor array"
            )
        previous: tuple[float, int, str] | None = None
        neighbor_terms: set[str] = set()
        for neighbor in row["neighbors"]:
            if not isinstance(neighbor, dict) or set(neighbor) != {
                "term",
                "cooccurrence",
                "ppmi",
            }:
                raise SnapshotError(
                    f"classical/associations.jsonl:{number} has an invalid neighbor"
                )
            if (
                neighbor["term"] not in term_stats
                or neighbor["term"] == term
                or neighbor["term"] in neighbor_terms
            ):
                raise SnapshotError(
                    f"classical/associations.jsonl:{number} has an unknown or duplicate neighbor"
                )
            if (
                isinstance(neighbor["cooccurrence"], bool)
                or not isinstance(neighbor["cooccurrence"], int)
                or neighbor["cooccurrence"] < 1
            ):
                raise SnapshotError(
                    f"classical/associations.jsonl:{number} has an invalid cooccurrence"
                )
            if (
                isinstance(neighbor["ppmi"], bool)
                or not isinstance(neighbor["ppmi"], (int, float))
                or not math.isfinite(float(neighbor["ppmi"]))
                or float(neighbor["ppmi"]) <= 0
            ):
                raise SnapshotError(
                    f"classical/associations.jsonl:{number} has an invalid PPMI"
                )
            ordering = (
                -float(neighbor["ppmi"]),
                -neighbor["cooccurrence"],
                neighbor["term"],
            )
            if previous is not None and ordering < previous:
                raise SnapshotError(
                    f"classical/associations.jsonl:{number} neighbors are not ordered"
                )
            previous = ordering
            neighbor_terms.add(neighbor["term"])
        terms.append(term)
    if terms != sorted(terms) or len(terms) != len(set(terms)):
        raise SnapshotError("association terms must be uniquely ordered")


def _validate_topics(
    topics: Any, lexicon: Mapping[str, Any], plan: Mapping[str, Any]
) -> None:
    if not isinstance(topics, dict):
        raise SnapshotError("classical/topics.json root must be an object")
    _exact_keys(
        topics,
        {
            "schema_version",
            "algorithm",
            "requested_topic_count",
            "topic_count",
            "iterations",
            "term_topics",
            "topics",
        },
        "MALLET topics",
    )
    if (
        topics["schema_version"] != SCHEMA_VERSION
        or topics["algorithm"] != ALGORITHMS["topics"]
    ):
        raise SnapshotError("MALLET topic algorithm identity is invalid")
    if topics["requested_topic_count"] != plan["topics"]["topic_count"]:
        raise SnapshotError("requested topic count differs from the plan")
    if topics["iterations"] != plan["topics"]["num_iterations"]:
        raise SnapshotError("MALLET topic iterations differ from the plan")
    if not isinstance(topics["topics"], list) or topics["topic_count"] != len(
        topics["topics"]
    ):
        raise SnapshotError("topic count is invalid")
    if topics["topic_count"] != topics["requested_topic_count"]:
        raise SnapshotError("MALLET did not return the requested topic count")
    topic_ids = [
        row.get("topic_id") for row in topics["topics"] if isinstance(row, dict)
    ]
    if len(topic_ids) != len(topics["topics"]) or topic_ids != [
        f"topic-{index:02d}" for index in range(len(topic_ids))
    ]:
        raise SnapshotError("topic IDs are invalid or unordered")
    if not isinstance(topics["term_topics"], list) or any(
        not isinstance(row, dict) or set(row) != {"term", "topic_id"}
        for row in topics["term_topics"]
    ):
        raise SnapshotError("MALLET topic term mapping has an invalid shape")
    mapped_terms = [row["term"] for row in topics["term_topics"]]
    lexical_terms = {row["term"] for row in lexicon["terms"]}
    if not mapped_terms or mapped_terms != sorted(set(mapped_terms)):
        raise SnapshotError(
            "MALLET topic term mapping must be nonempty, unique, and ordered"
        )
    if any(term not in lexical_terms or " " in term for term in mapped_terms):
        raise SnapshotError(
            "MALLET topic term mapping names an unknown lexical unigram"
        )
    if any(row.get("topic_id") not in set(topic_ids) for row in topics["term_topics"]):
        raise SnapshotError("topic term mapping names an unknown topic")
    assigned_counts = Counter(row["topic_id"] for row in topics["term_topics"])
    for row in topics["topics"]:
        if (
            set(row) != {"topic_id", "seed", "term_count", "terms"}
            or row["seed"] not in lexical_terms
        ):
            raise SnapshotError("topic row has an invalid shape or seed")
        if row["term_count"] != assigned_counts[row["topic_id"]]:
            raise SnapshotError(
                "topic row term count differs from the MALLET argmax mapping"
            )
        if (
            not isinstance(row["terms"], list)
            or len(row["terms"]) > plan["topics"]["top_terms"]
        ):
            raise SnapshotError("topic top-term array is invalid")
        if any(
            not isinstance(item, dict)
            or set(item) != {"term", "weight"}
            or item["term"] not in lexical_terms
            or isinstance(item["weight"], bool)
            or not isinstance(item["weight"], (int, float))
            or not math.isfinite(float(item["weight"]))
            or not 0.0 < float(item["weight"]) <= 1.0
            for item in row["terms"]
        ):
            raise SnapshotError("topic contains an invalid top term")
        if not row["terms"] or row["seed"] != row["terms"][0]["term"]:
            raise SnapshotError("topic seed must be its strongest MALLET term")
        if len({item["term"] for item in row["terms"]}) != len(row["terms"]):
            raise SnapshotError("MALLET topic contains duplicate top terms")
        ordering = [(-float(item["weight"]), item["term"]) for item in row["terms"]]
        if ordering != sorted(ordering):
            raise SnapshotError("MALLET topic terms are not ordered by probability")
    if sum(row["term_count"] for row in topics["topics"]) != len(mapped_terms):
        raise SnapshotError(
            "MALLET topic assignment counts do not cover the vocabulary"
        )


def load_snapshot(
    root: Path,
    *,
    deep_validation: bool = False,
    java: Path | None = None,
    mallet_home: Path | None = None,
) -> ClassicalSnapshot:
    """Load read-only and optionally retrain with the bound Java MALLET runtime."""

    _require_tantivy()
    try:
        root = require_real_directory(root, label="Semantic OKF bundle")
    except UnsafePathError as exc:
        raise SnapshotError(str(exc)) from exc
    _validate_closed_layout(root)
    try:
        tika_report = validate_tika_snapshot(root)
    except TikaSnapshotError as exc:
        raise SnapshotError(str(exc)) from exc
    classical = root / "classical"
    expected_names = {
        "index.json",
        "documents.jsonl",
        "lexicon.json",
        "associations.jsonl",
        "topics.json",
        "build-report.json",
    }
    if not classical.is_dir() or classical.is_symlink():
        raise SnapshotError("classical must be a real directory")
    actual_names = {path.name for path in classical.iterdir()}
    if actual_names != expected_names:
        raise SnapshotError(
            f"classical artifact set is closed; missing={sorted(expected_names - actual_names)}, unknown={sorted(actual_names - expected_names)}"
        )
    if any(path.is_symlink() or not path.is_file() for path in classical.iterdir()):
        raise SnapshotError("classical artifacts must be regular files")
    semantic_report = _load_json(
        root / "semantic" / "build-report.json", "semantic/build-report.json"
    )
    if not isinstance(semantic_report, dict) or semantic_report.get("status") != "pass":
        raise SnapshotError("authoritative Semantic OKF build report is not passing")
    index = _load_json(classical / "index.json", "classical/index.json")
    if not isinstance(index, dict):
        raise SnapshotError("classical/index.json root must be an object")
    _exact_keys(
        index,
        {
            "schema_version",
            "authoritative",
            "core",
            "classical_plan_sha256",
            "plan",
            "selection",
            "algorithms",
            "toolchain",
            "artifacts",
            "summary",
        },
        "classical index",
    )
    if index["schema_version"] != SCHEMA_VERSION or index["authoritative"] is not False:
        raise SnapshotError("classical index version or authority marker is invalid")
    if index["algorithms"] != ALGORITHMS:
        raise SnapshotError("classical algorithm identities are invalid")
    try:
        toolchain = validate_toolchain(index["toolchain"])
    except MalletRuntimeError as exc:
        raise SnapshotError(str(exc)) from exc
    plan = _validate_plan(index["plan"])
    _validate_tantivy_bm25(plan)
    if index["classical_plan_sha256"] != sha256_canonical(plan):
        raise SnapshotError("classical plan digest is invalid")
    records = _read_jsonl(root / "semantic" / "records.jsonl", "semantic/records.jsonl")
    _validate_concept_tree(root, records)
    source_manifest = _load_json(
        root / "semantic" / "source-manifest.json", "semantic/source-manifest.json"
    )
    sources = (
        source_manifest.get("sources") if isinstance(source_manifest, dict) else None
    )
    if not isinstance(sources, list) or any(
        not isinstance(item, dict) for item in sources
    ):
        raise SnapshotError(
            "semantic/source-manifest.json must contain an object source array"
        )
    selected_records, expected_selection = _select_records(records, sources, plan)
    if index["selection"] != expected_selection:
        raise SnapshotError("classical source selection binding is invalid")
    core = {
        "tree_sha256": sha256_canonical(_core_inventory(root)),
        "records_sha256": sha256_file(root / "semantic" / "records.jsonl"),
        "record_count": len(records),
    }
    if index["core"] != core:
        raise SnapshotError("classical index core binding is stale or invalid")
    documents = _read_jsonl(classical / "documents.jsonl", "classical/documents.jsonl")
    lexicon = _load_json(classical / "lexicon.json", "classical/lexicon.json")
    associations = _read_jsonl(
        classical / "associations.jsonl", "classical/associations.jsonl"
    )
    topics = _load_json(classical / "topics.json", "classical/topics.json")
    _validate_topics(topics, lexicon, plan)
    _validate_documents(root, documents, records, plan, topics, semantic_report)
    if lexicon != _derive_lexicon(documents, plan):
        raise SnapshotError("classical lexicon differs from live document statistics")
    _validate_associations(associations, lexicon, plan)
    if deep_validation:
        if java is None or mallet_home is None:
            raise SnapshotError(
                "deep validation requires both --java and --mallet-home"
            )
        try:
            runtime = preflight_mallet(java, mallet_home)
        except MalletRuntimeError as exc:
            raise SnapshotError(str(exc)) from exc
        if runtime.payload() != toolchain:
            raise SnapshotError(
                "MALLET runtime differs from the projection's exact toolchain binding"
            )
        if paths_overlap(root, runtime.mallet_home) or paths_overlap(root, runtime.java):
            raise SnapshotError("deep-validation runtime overlaps the read-only bundle")
        expected_documents, expected_lexicon, expected_associations, expected_topics = (
            _derive_all(
                selected_records,
                plan,
                runtime,
                forbidden_roots=(root, runtime.mallet_home),
            )
        )
        if documents != expected_documents:
            raise SnapshotError(
                "classical documents differ from authoritative deterministic derivation"
            )
        if lexicon != expected_lexicon:
            raise SnapshotError(
                "classical lexicon differs from authoritative deterministic derivation"
            )
        if associations != expected_associations:
            raise SnapshotError(
                "classical associations differ from independent deterministic PPMI derivation"
            )
        if topics != expected_topics:
            raise SnapshotError(
                "MALLET topics differ from independent fixed-seed Java MALLET derivation"
            )
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
    summary = {
        "inputs": index["selection"]["input_count"],
        "records": len(selected_records),
        "documents": len(documents),
        "terms": len(lexicon["terms"]),
        "association_terms": len(associations),
        "topics": topics["topic_count"],
    }
    if index["summary"] != summary:
        raise SnapshotError("classical index summary is invalid")
    expected_report = {
        "schema_version": SCHEMA_VERSION,
        "valid": True,
        "status": "pass",
        "errors": [],
        "warnings": [],
        "classical_plan_sha256": index["classical_plan_sha256"],
        "core": core,
        "selection": index["selection"],
        "toolchain": toolchain,
        "summary": summary,
        "artifacts": {
            "index": _artifact(classical / "index.json", "classical/index.json"),
            **artifacts,
        },
    }
    if (
        _load_json(classical / "build-report.json", "classical/build-report.json")
        != expected_report
    ):
        raise SnapshotError("classical build report differs from live validation")
    return ClassicalSnapshot(
        root=root,
        tika=tika_report,
        index=index,
        documents=tuple(documents),
        lexicon=lexicon,
        associations=tuple(associations),
        topics=topics,
        index_sha256=sha256_file(classical / "index.json"),
        deep_validation=deep_validation,
    )


def inspect_snapshot(snapshot: ClassicalSnapshot) -> dict[str, Any]:
    """Return capabilities and authoritative paths for a validated snapshot."""

    installed = _require_tantivy()
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "pass",
        "authoritative": False,
        "discovery_only": True,
        "validation": {
            "structural": True,
            "independent_rederivation": snapshot.deep_validation,
        },
        "core_tree_sha256": snapshot.index["core"]["tree_sha256"],
        "classical_index_sha256": snapshot.index_sha256,
        "classical_plan_sha256": snapshot.index["classical_plan_sha256"],
        "tika": snapshot.tika,
        "mallet": {
            "algorithm": snapshot.index["algorithms"]["topics"],
            "jar_tree_sha256": snapshot.index["toolchain"]["mallet_jar_tree_sha256"],
            "version": snapshot.index["toolchain"]["mallet_version"],
        },
        "engine": {
            "id": ENGINE_ID,
            "name": "Tantivy",
            "implementation": "Rust",
            "package_version": installed,
            "scoring": "BM25",
            "index_storage": "memory",
            "tokenizer": "default",
        },
        "summary": snapshot.index["summary"],
        "capabilities": ["tantivy", "topic", "association", "fusion"],
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


def _require_tantivy() -> str:
    """Require the official pinned Python binding instead of a substitute."""

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


def _validate_tantivy_bm25(plan: Mapping[str, Any]) -> dict[str, float]:
    """Validate the BM25 settings supported by the pinned native engine."""

    config = plan["bm25"]
    values = {
        name: float(config[name])
        for name in ("k1", "b", "title_weight", "body_weight")
    }
    if values["k1"] != 1.2 or values["b"] != 0.75:
        raise SnapshotError(
            "Tantivy consultation requires the classical k1=1.2 and b=0.75 defaults"
        )
    return values


def _query_unigrams(snapshot: ClassicalSnapshot) -> frozenset[str]:
    """Return the validated persisted unigram vocabulary."""

    terms = frozenset(
        row["term"]
        for row in snapshot.lexicon["terms"]
        if isinstance(row, dict)
        and isinstance(row.get("term"), str)
        and " " not in row["term"]
    )
    if not terms:
        raise SnapshotError("classical lexicon has no unigram query vocabulary")
    return terms


def _normalized_query(
    snapshot: ClassicalSnapshot,
    query_text: str,
) -> tuple[str, bool]:
    """Normalize syntax-free natural text against the persisted vocabulary."""

    if EXPLICIT_QUERY_SYNTAX_RE.search(query_text):
        return query_text, False
    raw_terms = TOKEN_RE.findall(query_text.casefold())
    known_terms = [term for term in raw_terms if term in _query_unigrams(snapshot)]
    return (" ".join(known_terms or raw_terms), True)


def _expanded_query(
    base_query: str,
    expansion_terms: Iterable[str],
    *,
    explicit_syntax: bool,
) -> str:
    """Add only safe persisted expansion terms to one Tantivy query."""

    additions = sorted(
        {
            term.casefold()
            for term in expansion_terms
            if isinstance(term, str) and TOKEN_RE.fullmatch(term)
        }
    )
    if not additions:
        return base_query
    if explicit_syntax:
        return f"({base_query}) OR " + " OR ".join(additions)
    base_terms = TOKEN_RE.findall(base_query.casefold())
    return " ".join(dict.fromkeys([*base_terms, *additions]))


def _build_tantivy_index(
    documents: Sequence[dict[str, Any]],
) -> tuple[Any, dict[str, dict[str, Any]]]:
    """Build one pathless in-memory index after filters have been applied."""

    import tantivy

    builder = tantivy.SchemaBuilder()
    builder.add_text_field("document_id", stored=True, tokenizer_name="raw")
    builder.add_text_field("title", stored=True, index_option="position")
    builder.add_text_field("body", stored=True, index_option="position")
    index = tantivy.Index(builder.build())
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
    return index, {document["document_id"]: document for document in documents}


def _tantivy_scores(
    index: Any,
    documents: Mapping[str, dict[str, Any]],
    query_text: str,
    boosts: Mapping[str, float],
) -> tuple[dict[str, float], int]:
    """Run one native BM25 query against an already built memory index."""

    if not query_text.strip():
        return {}, 0
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
        response = searcher.search(query, limit=len(documents), count=True)
    except ValueError as exc:
        raise SnapshotError(f"Tantivy search failed: {exc}") from exc
    scores: dict[str, float] = {}
    for score, address in response.hits:
        stored = searcher.doc(address)
        document_id = stored.get_first("document_id")
        if not isinstance(document_id, str) or document_id not in documents:
            raise SnapshotError("Tantivy returned an unknown document identity")
        numeric_score = float(score)
        if not math.isfinite(numeric_score):
            raise SnapshotError("Tantivy returned a non-finite BM25 score")
        scores[document_id] = numeric_score
    return scores, int(response.count)


def _native_routes(
    documents: Sequence[dict[str, Any]],
    queries: Mapping[str, str],
    boosts: Mapping[str, float],
) -> tuple[dict[str, dict[str, float]], dict[str, int]]:
    """Build once and execute every lexical route through native Tantivy."""

    if not documents:
        return ({name: {} for name in queries}, {name: 0 for name in queries})
    index, by_id = _build_tantivy_index(documents)
    routes: dict[str, dict[str, float]] = {}
    matches: dict[str, int] = {}
    for name, query in queries.items():
        routes[name], matches[name] = _tantivy_scores(index, by_id, query, boosts)
    return routes, matches


def _normalize_scores(scores: Mapping[str, float]) -> dict[str, float]:
    maximum = max(scores.values(), default=0.0)
    return (
        {key: value / maximum for key, value in scores.items()} if maximum > 0 else {}
    )


def _topic_vector(weights: Iterable[Mapping[str, Any]]) -> dict[str, float]:
    return {str(item["topic_id"]): float(item["weight"]) for item in weights}


def _cosine(left: Mapping[str, float], right: Mapping[str, float]) -> float:
    if not left or not right:
        return 0.0
    numerator = sum(value * right.get(key, 0.0) for key, value in left.items())
    left_norm = math.sqrt(sum(value * value for value in left.values()))
    right_norm = math.sqrt(sum(value * value for value in right.values()))
    return numerator / (left_norm * right_norm) if left_norm and right_norm else 0.0


def _association_expansion(
    query: str, snapshot: ClassicalSnapshot
) -> tuple[dict[str, float], list[dict[str, Any]]]:
    plan = snapshot.index["plan"]
    graph = {
        row["term"]: {
            neighbor["term"]: float(neighbor["ppmi"]) for neighbor in row["neighbors"]
        }
        for row in snapshot.associations
    }
    originals = set(_unigrams(query, plan))
    frontier = {term: 1.0 for term in originals if term in graph}
    accumulated: defaultdict[str, float] = defaultdict(float)
    for depth in range(2):
        next_frontier: defaultdict[str, float] = defaultdict(float)
        damping = 0.6 ** (depth + 1)
        for term, value in frontier.items():
            neighbors = graph.get(term, {})
            total = sum(neighbors.values())
            if total <= 0:
                continue
            for neighbor, weight in neighbors.items():
                propagated = value * damping * weight / total
                next_frontier[neighbor] += propagated
                if neighbor not in originals:
                    accumulated[neighbor] += propagated
        frontier = dict(next_frontier)
    maximum = max(accumulated.values(), default=0.0)
    limit = int(plan["expansion"]["association_terms"])
    selected = sorted(accumulated.items(), key=lambda item: (-item[1], item[0]))[:limit]
    rows = [
        {"term": term, "weight": round(value / maximum, 8), "source": "ppmi-two-step"}
        for term, value in selected
        if maximum > 0
    ]
    weights = {
        row["term"]: float(row["weight"])
        * float(plan["expansion"]["association_weight"])
        for row in rows
    }
    return weights, rows


def _topic_expansion(
    query: str,
    association_weights: Mapping[str, float],
    snapshot: ClassicalSnapshot,
) -> tuple[dict[str, float], list[dict[str, Any]], dict[str, float]]:
    plan = snapshot.index["plan"]
    term_topic = {
        row["term"]: row["topic_id"] for row in snapshot.topics["term_topics"]
    }
    activation: defaultdict[str, float] = defaultdict(float)
    originals = set(_unigrams(query, plan))
    for term in originals:
        if term in term_topic:
            activation[term_topic[term]] += 1.0
    for term, weight in association_weights.items():
        if term in term_topic:
            activation[term_topic[term]] += weight
    total = sum(activation.values())
    query_topics = (
        {key: value / total for key, value in activation.items()} if total else {}
    )
    candidates: list[tuple[float, str, str]] = []
    for topic in snapshot.topics["topics"]:
        topic_weight = query_topics.get(topic["topic_id"], 0.0)
        if topic_weight <= 0:
            continue
        maximum = max((float(item["weight"]) for item in topic["terms"]), default=1.0)
        for item in topic["terms"]:
            term = item["term"]
            if term in originals or term in association_weights:
                continue
            candidates.append(
                (
                    topic_weight * float(item["weight"]) / maximum,
                    term,
                    topic["topic_id"],
                )
            )
    limit = int(plan["expansion"]["topic_terms"])
    selected = sorted(candidates, key=lambda item: (-item[0], item[1], item[2]))[:limit]
    rows = [
        {
            "term": term,
            "weight": round(weight, 8),
            "topic_id": topic_id,
            "source": "java-mallet-2.1.0-lda",
        }
        for weight, term, topic_id in selected
    ]
    weights = {
        row["term"]: float(row["weight"]) * float(plan["expansion"]["topic_weight"])
        for row in rows
    }
    return weights, rows, query_topics


def _rank(scores: Mapping[str, float]) -> list[str]:
    return [
        key for key, _ in sorted(scores.items(), key=lambda item: (-item[1], item[0]))
    ]


def _rrf(rankings: Sequence[Sequence[str]], k: int) -> dict[str, float]:
    result: defaultdict[str, float] = defaultdict(float)
    for ranking in rankings:
        for rank, identifier in enumerate(ranking, start=1):
            result[identifier] += 1.0 / (k + rank)
    return dict(result)


def _diversify(
    candidates: Sequence[dict[str, Any]],
    scores: Mapping[str, float],
    top_k: int,
    plan: Mapping[str, Any],
) -> list[dict[str, Any]]:
    normalized = _normalize_scores(scores)
    by_id = {row["document_id"]: row for row in candidates}
    pool_ids = _rank(scores)[: int(plan["reranking"]["candidate_pool"])]
    selected: list[str] = []
    selected_sources: set[str] = set()
    selected_papers: set[str] = set()
    identity_counts: Counter[str] = Counter()
    identity_cap = int(plan["reranking"]["max_per_evidence_identity"])
    while pool_ids and len(selected) < top_k:
        choices: list[tuple[float, str]] = []
        for identifier in pool_ids:
            document = by_id[identifier]
            evidence_identity = document.get("paper_id") or document["source_id"]
            if identity_counts[evidence_identity] >= identity_cap:
                continue
            vector = _topic_vector(document["topic_weights"])
            similarity = max(
                (
                    _cosine(vector, _topic_vector(by_id[item]["topic_weights"]))
                    for item in selected
                ),
                default=0.0,
            )
            source_novelty = (
                1.0
                if (
                    document["source_id"] not in selected_sources
                    and evidence_identity not in selected_papers
                )
                else 0.0
            )
            value = (
                float(plan["reranking"]["relevance_weight"])
                * normalized.get(identifier, 0.0)
                + float(plan["reranking"]["topic_novelty_weight"]) * (1.0 - similarity)
                + float(plan["reranking"]["source_novelty_weight"]) * source_novelty
            )
            choices.append((value, identifier))
        if not choices:
            break
        _, chosen = sorted(choices, key=lambda item: (-item[0], item[1]))[0]
        pool_ids.remove(chosen)
        selected.append(chosen)
        selected_sources.add(by_id[chosen]["source_id"])
        evidence_identity = by_id[chosen].get("paper_id") or by_id[chosen]["source_id"]
        selected_papers.add(evidence_identity)
        identity_counts[evidence_identity] += 1
    return [by_id[identifier] for identifier in selected]


def _native_identity_cap(
    candidates: Sequence[dict[str, Any]],
    scores: Mapping[str, float],
    top_k: int,
    plan: Mapping[str, Any],
) -> list[dict[str, Any]]:
    """Retain native score order while limiting repeated evidence identities."""

    by_id = {row["document_id"]: row for row in candidates}
    counts: Counter[str] = Counter()
    selected: list[dict[str, Any]] = []
    identity_cap = int(plan["reranking"]["max_per_evidence_identity"])
    candidate_pool = int(plan["reranking"]["candidate_pool"])
    for identifier in _rank(scores)[: max(top_k, candidate_pool)]:
        document = by_id[identifier]
        identity = document.get("paper_id") or document["source_id"]
        if counts[identity] >= identity_cap:
            continue
        selected.append(document)
        counts[identity] += 1
        if len(selected) == top_k:
            break
    return selected


def search_snapshot(
    snapshot: ClassicalSnapshot,
    query: str,
    mode: str,
    top_k: int,
    *,
    source_ids: Sequence[str] = (),
    concept_ids: Sequence[str] = (),
    concept_types: Sequence[str] = (),
) -> dict[str, Any]:
    """Search Tika/MALLET evidence with Tantivy, topics, PPMI, or fusion."""

    _require_tantivy()
    if mode not in {"tantivy", "topic", "association", "fusion"}:
        raise SnapshotError("mode must be tantivy, topic, association, or fusion")
    if not isinstance(query, str) or not query.strip():
        raise SnapshotError("query must be nonempty")
    if isinstance(top_k, bool) or not isinstance(top_k, int) or not 1 <= top_k <= 1000:
        raise SnapshotError("top-k must be an integer from 1 through 1000")
    source_filter, concept_filter, type_filter = (
        set(source_ids),
        set(concept_ids),
        set(concept_types),
    )
    documents = [
        row
        for row in snapshot.documents
        if (not source_filter or row["source_id"] in source_filter)
        and (not concept_filter or row["concept_id"] in concept_filter)
        and (not type_filter or row["concept_type"] in type_filter)
    ]
    plan = snapshot.index["plan"]
    boosts = _validate_tantivy_bm25(plan)
    query_text = query.strip()
    parsed_query, normalized = _normalized_query(snapshot, query_text)
    explicit_syntax = not normalized
    association_weights, association_rows = _association_expansion(query, snapshot)
    topic_weights, topic_rows, query_topics = _topic_expansion(
        query, association_weights, snapshot
    )
    association_query = _expanded_query(
        parsed_query,
        association_weights,
        explicit_syntax=explicit_syntax,
    )
    topic_query = _expanded_query(
        association_query,
        topic_weights,
        explicit_syntax=explicit_syntax,
    )
    native, matched = _native_routes(
        documents,
        {
            "tantivy": parsed_query,
            "association": association_query,
            "topic": topic_query,
        },
        boosts,
    )
    tantivy_scores = native["tantivy"]
    association = native["association"]
    topic_lexical = native["topic"]
    normalized_topic_lexical = _normalize_scores(topic_lexical)
    topic_scores = {
        row["document_id"]: 0.8 * normalized_topic_lexical.get(row["document_id"], 0.0)
        + 0.2 * _cosine(query_topics, _topic_vector(row["topic_weights"]))
        for row in documents
    }
    topic_scores = {key: value for key, value in topic_scores.items() if value > 0}
    fusion = _rrf(
        [_rank(tantivy_scores), _rank(association), _rank(topic_scores)],
        int(plan["reranking"]["rrf_k"]),
    )
    route_scores = {
        "tantivy": tantivy_scores,
        "association": association,
        "topic": topic_scores,
        "fusion": fusion,
    }
    scores = route_scores[mode]
    if mode == "tantivy":
        selected = _native_identity_cap(documents, scores, top_k, plan)
    else:
        selected = _diversify(documents, scores, top_k, plan)
    component_ranks = {
        name: {
            identifier: rank for rank, identifier in enumerate(_rank(values), start=1)
        }
        for name, values in route_scores.items()
    }
    results = []
    for rank, document in enumerate(selected, start=1):
        identifier = document["document_id"]
        results.append(
            {
                "rank": rank,
                "document_id": identifier,
                "source_id": document["source_id"],
                "paper_id": document["paper_id"],
                "record_id": document["record_id"],
                "record_sha256": document["record_sha256"],
                "concept_id": document["concept_id"],
                "concept_type": document["concept_type"],
                "concept_path": document["concept_path"],
                "source_path": document["source_path"],
                "ordinal": document["ordinal"],
                "locator": document["locator"],
                "text": document["text"],
                "text_sha256": document["text_sha256"],
                "score": scores.get(identifier, 0.0),
                "scores": {
                    name: values.get(identifier)
                    for name, values in route_scores.items()
                },
                "ranks": {
                    name: ranks.get(identifier)
                    for name, ranks in component_ranks.items()
                },
                "topic_weights": document["topic_weights"],
            }
        )
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "pass",
        "authoritative": False,
        "discovery_only": True,
        "query": query_text,
        "parsed_query": parsed_query,
        "requested_mode": mode,
        "effective_mode": mode,
        "top_k": top_k,
        "returned": len(results),
        "filters": {
            "source_ids": sorted(source_filter),
            "concept_ids": sorted(concept_filter),
            "concept_types": sorted(type_filter),
        },
        "expansion": {
            "association_terms": association_rows,
            "topic_terms": topic_rows,
            "query_topics": [
                {"topic_id": topic_id, "weight": round(weight, 8)}
                for topic_id, weight in sorted(query_topics.items())
            ],
        },
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
            "matched_documents": matched,
            "lexical_queries": {
                "tantivy": parsed_query,
                "association": association_query,
                "topic": topic_query,
            },
            "query_normalization": (
                "classical-unigram-lexicon-v1"
                if normalized
                else "preserved-syntax"
            ),
            "identity_cap": int(
                plan["reranking"]["max_per_evidence_identity"]
            ),
            "identity_policy": "paper_id-or-source_id",
        },
        "snapshot": {
            "core_tree_sha256": snapshot.index["core"]["tree_sha256"],
            "classical_index_sha256": snapshot.index_sha256,
            "classical_plan_sha256": snapshot.index["classical_plan_sha256"],
            "deep_validation": snapshot.deep_validation,
        },
        "results": results,
    }
