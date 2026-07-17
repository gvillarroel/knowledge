#!/usr/bin/env python3
"""Validate and query a adaptive Semantic OKF projection without writing it."""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Mapping, Sequence


SCHEMA_VERSION = "1.2"
PLAN_SCHEMA_VERSION = "1.1"
TOKENIZER_ID = "ascii-alphanumeric-v1"
STOPWORDS_ID = "english-v1"
TOKEN_RE = re.compile(r"[a-z0-9]+", re.IGNORECASE)
ASPECT_SPLIT_RE = re.compile(
    r"(?:[?;:]|\.(?:\s|$)|(?=\b(?:and|while|whereas|versus|but|however)\b)|"
    r",(?=\s+(?:and\s+)?(?:why|which|what|when|where|how|or\b)))",
    re.IGNORECASE,
)
FACET_SPLIT_RE = re.compile(
    r"[?,;:]|\.(?:\s|$)|\b(?:and|or|versus|while|whereas|but|however)\b",
    re.IGNORECASE,
)
PAGE_RE = re.compile(r"(?m)^## PDF page \d+\s*$")
PAPER_ID_RE = re.compile(r"\d{4}\.\d{5}v\d+", re.IGNORECASE)
EVIDENCE_FRAGMENT_RE = re.compile(r"(?P<path>[^#]+)#PDF-page-(?P<page>[1-9]\d*)")
HEX_64 = re.compile(r"[0-9a-f]{64}")
DOCUMENT_ID_RE = re.compile(r"document-[0-9a-f]{32}")
ANSWER_FULL_RECORD_WEIGHT = 2.0
ANSWER_INTERPRETATION_WEIGHT = 1.0
ANSWER_INITIAL_PAPER_CAP = 3
COVERAGE_ALGORITHM = "enumeration-facet-separated-claim-ranking-v1"
ANSWER_FINALIZER_ALGORITHM = "authoritative-binding-response-finalizer-v1"
ALGORITHMS = {
    "bm25": "okapi-bm25f-v1",
    "associations": "windowed-positive-pmi-v1",
    "topics": "deterministic-seeded-weighted-label-propagation-v1",
    "topic_scoring": "normalized-bm25-plus-topic-cosine-v1",
    "association_scoring": "two-step-ppmi-query-propagation-v1",
    "fusion": "reciprocal-rank-fusion-v1",
    "reranking": "topic-and-source-mmr-v1",
    "adaptive": "protected-full-query-plus-aspect-rrf-v2",
    "evidence_adapter": "exact-authoritative-fields-v2",
    "answer_evidence_adapter": "verified-pdf-page-bindings-v1",
    "answer_evidence_ranking": "dual-view-record-interpretation-fusion-v2",
}
PLAN_KEYS = {
    "schema_version",
    "selection",
    "passages",
    "evidence_identity",
    "tokenization",
    "bm25",
    "associations",
    "topics",
    "expansion",
    "reranking",
    "adaptive",
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
ANSWER_BINDING_KEYS = {
    "binding_id",
    "source_id",
    "record_id",
    "record_sha256",
    "concept_id",
    "concept_type",
    "concept_path",
    "source_path",
    "paper_id",
    "review_state",
    "locator_tokens",
    "citation_pages",
    "evidence_paths",
    "authoritative_text",
    "authoritative_text_sha256",
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
    """Describe an invalid snapshot, filter, or adaptive search request."""


@dataclass(frozen=True)
class AdaptiveSnapshot:
    """Hold one fully validated in-memory adaptive retrieval snapshot."""

    root: Path
    index: dict[str, Any]
    documents: tuple[dict[str, Any], ...]
    answer_bindings: tuple[dict[str, Any], ...]
    answer_documents: tuple[dict[str, Any], ...]
    lexicon: dict[str, Any]
    associations: tuple[dict[str, Any], ...]
    topics: dict[str, Any]
    index_sha256: str
    deep_validation: bool


def canonical_json(value: Any) -> str:
    """Serialize JSON deterministically and reject non-finite values."""

    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


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
        return json.loads(payload, object_pairs_hook=reject_duplicates, parse_constant=reject_constant)
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
    if candidate.is_absolute() or not candidate.parts or any(part in {"", ".", ".."} for part in candidate.parts):
        raise SnapshotError(f"{label} is not a safe relative path: {value!r}")
    return candidate


def _core_inventory(root: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        relative = path.relative_to(root)
        if relative.parts and relative.parts[0] == "adaptive":
            continue
        rows.append({"path": relative.as_posix(), "sha256": sha256_file(path)})
    return rows


def _is_link_or_junction(path: Path) -> bool:
    """Reject filesystem indirection instead of following it during validation."""

    is_junction = getattr(path, "is_junction", None)
    return path.is_symlink() or bool(is_junction and is_junction())


def _reject_bundle_links(root: Path) -> None:
    if _is_link_or_junction(root):
        raise SnapshotError("bundle root must be a real directory")
    for current, directory_names, file_names in os.walk(root, topdown=True, followlinks=False):
        current_path = Path(current)
        for name in [*directory_names, *file_names]:
            candidate = current_path / name
            if _is_link_or_junction(candidate):
                relative = candidate.relative_to(root).as_posix()
                raise SnapshotError(f"bundle contains a symlink or junction: {relative}")


def _plain_int(value: Any, label: str, minimum: int, maximum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not minimum <= value <= maximum:
        raise SnapshotError(f"{label} must be an integer from {minimum} through {maximum}")
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
        raise SnapshotError("adaptive index plan must be an object")
    _exact_keys(plan, PLAN_KEYS, "adaptive index plan")
    if plan["schema_version"] != PLAN_SCHEMA_VERSION:
        raise SnapshotError("adaptive plan schema version is invalid")
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
        raise SnapshotError("plan.selection.source_ids must be sorted, unique, and nonempty")

    passages = plan["passages"]
    if not isinstance(passages, dict):
        raise SnapshotError("plan.passages must be an object")
    _exact_keys(passages, {"default_mode", "markdown_pdf_page_source_ids"}, "plan.passages")
    if passages["default_mode"] != "full-record":
        raise SnapshotError("plan.passages.default_mode must be full-record")
    page_source_ids = passages["markdown_pdf_page_source_ids"]
    if (
        not isinstance(page_source_ids, list)
        or any(not isinstance(item, str) or not item for item in page_source_ids)
        or page_source_ids != sorted(set(page_source_ids))
        or not set(page_source_ids).issubset(source_ids)
    ):
        raise SnapshotError(
            "plan.passages.markdown_pdf_page_source_ids must be a sorted unique subset of selected sources"
        )

    evidence_identity = plan["evidence_identity"]
    if not isinstance(evidence_identity, dict):
        raise SnapshotError("plan.evidence_identity must be an object")
    _exact_keys(evidence_identity, {"default_mode", "paper_ids_by_source"}, "plan.evidence_identity")
    if evidence_identity["default_mode"] != "source-record":
        raise SnapshotError("plan.evidence_identity.default_mode must be source-record")
    paper_ids_by_source = evidence_identity["paper_ids_by_source"]
    if not isinstance(paper_ids_by_source, dict):
        raise SnapshotError("plan.evidence_identity.paper_ids_by_source must be an object")
    if not set(paper_ids_by_source).issubset(source_ids):
        raise SnapshotError("paper identity mappings must name only selected sources")
    if any(
        not isinstance(source_id, str)
        or not source_id
        or not isinstance(paper_id, str)
        or PAPER_ID_RE.fullmatch(paper_id) is None
        or paper_id != paper_id.lower()
        for source_id, paper_id in paper_ids_by_source.items()
    ):
        raise SnapshotError("paper identity mappings must contain canonical versioned arXiv IDs")
    tokenization = plan["tokenization"]
    if not isinstance(tokenization, dict):
        raise SnapshotError("plan.tokenization must be an object")
    _exact_keys(tokenization, {"tokenizer", "stopwords", "min_token_length", "ngram_range"}, "plan.tokenization")
    if tokenization["tokenizer"] != TOKENIZER_ID or tokenization["stopwords"] != STOPWORDS_ID:
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
    _plain_int(associations["min_document_frequency"], "min_document_frequency", 1, 1_000_000)
    _plain_int(associations["min_cooccurrence"], "min_cooccurrence", 1, 1_000_000)
    _plain_int(associations["max_vocabulary"], "max_vocabulary", 32, 50_000)
    _plain_int(associations["max_neighbors"], "max_neighbors", 1, 128)
    _finite(associations["minimum_ppmi"], "minimum_ppmi", 0.0, 100.0)

    topics = plan["topics"]
    if not isinstance(topics, dict):
        raise SnapshotError("plan.topics must be an object")
    _exact_keys(topics, {"topic_count", "max_iterations", "top_terms"}, "plan.topics")
    _plain_int(topics["topic_count"], "topic_count", 2, 128)
    _plain_int(topics["max_iterations"], "max_iterations", 1, 100)
    _plain_int(topics["top_terms"], "top_terms", 3, 100)

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
    _plain_int(reranking["max_per_evidence_identity"], "max_per_evidence_identity", 1, 100)
    _plain_int(reranking["rrf_k"], "rrf_k", 1, 10_000)
    weights = [
        _finite(reranking[name], f"plan.reranking.{name}", 0.0, 1.0)
        for name in ("relevance_weight", "topic_novelty_weight", "source_novelty_weight")
    ]
    if not math.isclose(
        sum(weights),
        1.0,
        rel_tol=0.0,
        abs_tol=1e-9,
    ):
        raise SnapshotError("reranking weights must sum to one")

    adaptive = plan["adaptive"]
    if not isinstance(adaptive, dict):
        raise SnapshotError("plan.adaptive must be an object")
    _exact_keys(
        adaptive,
        {
            "maximum_aspects",
            "minimum_aspect_tokens",
            "full_query_weight",
            "aspect_weight",
            "best_aspect_weight",
            "rrf_k",
            "protected_full_results",
            "maximum_novel_aspect_rank",
        },
        "plan.adaptive",
    )
    _plain_int(adaptive["maximum_aspects"], "maximum_aspects", 0, 32)
    _plain_int(adaptive["minimum_aspect_tokens"], "minimum_aspect_tokens", 2, 32)
    _finite(adaptive["full_query_weight"], "full_query_weight", 0.01, 100.0)
    _finite(adaptive["aspect_weight"], "aspect_weight", 0.0, 100.0)
    _finite(adaptive["best_aspect_weight"], "best_aspect_weight", 0.0, 100.0)
    _plain_int(adaptive["rrf_k"], "adaptive.rrf_k", 0, 10_000)
    _plain_int(adaptive["protected_full_results"], "protected_full_results", 0, 1000)
    _plain_int(adaptive["maximum_novel_aspect_rank"], "maximum_novel_aspect_rank", 1, 1000)
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
        raise SnapshotError(f"adaptive plan selects unknown source IDs: {missing}")
    invalid_page_sources = sorted(
        source_id
        for source_id in plan["passages"]["markdown_pdf_page_source_ids"]
        if source_by_id[source_id].get("kind") != "markdown"
    )
    if invalid_page_sources:
        raise SnapshotError(
            "markdown PDF-page passage sources must declare kind=markdown: "
            f"{invalid_page_sources}"
        )
    requested_set = set(requested)
    selected = [record for record in records if record.get("source_id") in requested_set]
    eligible = sorted({str(record.get("source_id")) for record in selected})
    if eligible != requested:
        raise SnapshotError(
            f"selected source IDs produced no eligible records: {sorted(set(requested) - set(eligible))}"
        )
    inventory = [
        {"source_id": source_id, "content_sha256": source_by_id[source_id].get("content_sha256")}
        for source_id in eligible
    ]
    if any(not HEX_64.fullmatch(str(row["content_sha256"])) for row in inventory):
        raise SnapshotError("selected source inventory contains an invalid content digest")
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


def _paper_id(record: Mapping[str, Any], plan: Mapping[str, Any]) -> str | None:
    """Return only the paper identity explicitly reviewed in the closed plan."""

    return plan["evidence_identity"]["paper_ids_by_source"].get(record.get("source_id"))


def _trimmed_range(body: str, start: int, end: int) -> tuple[int, int] | None:
    while start < end and body[start].isspace():
        start += 1
    while end > start and body[end - 1].isspace():
        end -= 1
    return (start, end) if start < end else None


def _passage_ranges(record: Mapping[str, Any], plan: Mapping[str, Any]) -> list[tuple[int, int]]:
    body = str(record.get("body") or "")
    if record.get("source_id") not in set(plan["passages"]["markdown_pdf_page_source_ids"]):
        trimmed = _trimmed_range(body, 0, len(body))
        return [trimmed] if trimmed is not None else []
    matches = list(PAGE_RE.finditer(body))
    if not matches:
        trimmed = _trimmed_range(body, 0, len(body))
        return [trimmed] if trimmed is not None else []
    starts = [0, *(match.start() for match in matches[1:])]
    ends = [*(match.start() for match in matches[1:]), len(body)]
    return [item for pair in zip(starts, ends, strict=True) if (item := _trimmed_range(body, *pair))]


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
        if any(not isinstance(record.get(name), str) or not record[name] for name in required):
            raise SnapshotError("selected authoritative record has an invalid required identity or body")
        concept_path = str(record["concept_path"]).replace("\\", "/")
        safe = _safe_relative(concept_path, "record concept_path")
        if safe.parts[0] != "concepts":
            raise SnapshotError(f"record concept_path is outside concepts/: {concept_path}")
        body = str(record["body"])
        ranges = _passage_ranges(record, plan)
        if not ranges:
            raise SnapshotError(f"record {record['source_id']}/{record['record_id']} has no indexable text")
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
                "paper_id": _paper_id(record, plan),
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


def _derive_lexicon(documents: Sequence[dict[str, Any]], plan: Mapping[str, Any]) -> dict[str, Any]:
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
        key=lambda row: (-row["document_frequency"], -row["corpus_frequency"], row["term"])
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
            ppmi = max(0.0, math.log(probability_pair / (probability_left * probability_right)))
            if ppmi < config["minimum_ppmi"] or ppmi <= 0.0:
                continue
            weight = round(ppmi, 8)
            neighbors[left].append({"term": right, "cooccurrence": count, "ppmi": weight})
            neighbors[right].append({"term": left, "cooccurrence": count, "ppmi": weight})
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
            graph.setdefault(term, {})[other] = max(graph.get(term, {}).get(other, 0.0), weight)
            graph.setdefault(other, {})[term] = max(graph.get(other, {}).get(term, 0.0), weight)
    return graph


def _derive_topics(
    associations: Sequence[dict[str, Any]],
    lexicon: Mapping[str, Any],
    plan: Mapping[str, Any],
) -> dict[str, Any]:
    graph = _association_graph(associations)
    stats = {row["term"]: row for row in lexicon["terms"]}
    terms = sorted(graph)
    requested = min(plan["topics"]["topic_count"], len(terms))
    if requested < 2:
        raise SnapshotError("association vocabulary is too small to derive at least two topics")
    centrality = {term: sum(graph[term].values()) for term in terms}
    seeds: list[str] = []
    while len(seeds) < requested:
        ranked: list[tuple[float, str]] = []
        for term in terms:
            if term in seeds:
                continue
            maximum = max(
                (
                    graph[term].get(seed, 0.0)
                    / max(centrality[term], centrality.get(seed, 0.0), 1e-12)
                    for seed in seeds
                ),
                default=0.0,
            )
            score = (centrality[term] + math.log1p(stats[term]["corpus_frequency"])) / (
                1.0 + 8.0 * maximum
            )
            ranked.append((score, term))
        seeds.append(sorted(ranked, key=lambda item: (-item[0], item[1]))[0][1])

    labels: dict[str, int] = {}
    seed_index = {term: index for index, term in enumerate(seeds)}
    for term in terms:
        if term in seed_index:
            labels[term] = seed_index[term]
            continue
        direct = [(graph[term].get(seed, 0.0), index) for index, seed in enumerate(seeds)]
        best_weight, best_index = sorted(direct, key=lambda item: (-item[0], item[1]))[0]
        if best_weight <= 0.0:
            best_index = int(sha256_bytes(term.encode("utf-8"))[:8], 16) % requested
        labels[term] = best_index

    iterations = 0
    for iterations in range(1, plan["topics"]["max_iterations"] + 1):
        changed = 0
        for term in sorted(terms, key=lambda item: (-centrality[item], item)):
            if term in seed_index:
                continue
            scores: defaultdict[int, float] = defaultdict(float)
            for neighbor, weight in graph[term].items():
                scores[labels[neighbor]] += weight
            if not scores:
                continue
            best_score = max(scores.values())
            best_labels = sorted(
                label for label, score in scores.items() if math.isclose(score, best_score, abs_tol=1e-12)
            )
            selected = labels[term] if labels[term] in best_labels else best_labels[0]
            if selected != labels[term]:
                labels[term] = selected
                changed += 1
        if changed == 0:
            break

    topics: list[dict[str, Any]] = []
    top_terms = plan["topics"]["top_terms"]
    for index, seed in enumerate(seeds):
        members = [term for term in terms if labels[term] == index]
        ranked_members = sorted(
            members,
            key=lambda term: (
                -(math.log1p(stats[term]["corpus_frequency"]) * (1.0 + centrality[term])),
                term,
            ),
        )
        topics.append(
            {
                "topic_id": f"topic-{index:02d}",
                "seed": seed,
                "term_count": len(members),
                "terms": [
                    {
                        "term": term,
                        "weight": round(
                            math.log1p(stats[term]["corpus_frequency"])
                            * (1.0 + centrality[term]),
                            8,
                        ),
                    }
                    for term in ranked_members[:top_terms]
                ],
            }
        )
    return {
        "schema_version": SCHEMA_VERSION,
        "algorithm": ALGORITHMS["topics"],
        "requested_topic_count": plan["topics"]["topic_count"],
        "topic_count": len(topics),
        "iterations": iterations,
        "term_topics": [
            {"term": term, "topic_id": f"topic-{labels[term]:02d}"} for term in sorted(labels)
        ],
        "topics": topics,
    }


def _add_topic_weights(
    documents: list[dict[str, Any]],
    lexicon: Mapping[str, Any],
    topics: Mapping[str, Any],
) -> None:
    idf = {row["term"]: float(row["idf"]) for row in lexicon["terms"]}
    term_topics = {row["term"]: row["topic_id"] for row in topics["term_topics"]}
    for document in documents:
        combined = Counter(document["title_terms"]) + Counter(document["body_terms"])
        weights: defaultdict[str, float] = defaultdict(float)
        for term, count in combined.items():
            topic_id = term_topics.get(term)
            if topic_id is not None:
                weights[topic_id] += count * idf.get(term, 0.0)
        total = sum(weights.values())
        document["topic_weights"] = [
            {"topic_id": topic_id, "weight": round(weight / total, 8)}
            for topic_id, weight in sorted(weights.items())
            if total > 0.0 and weight > 0.0
        ]


def _derive_all(
    records: Sequence[dict[str, Any]], plan: Mapping[str, Any]
) -> tuple[list[dict[str, Any]], dict[str, Any], list[dict[str, Any]], dict[str, Any]]:
    documents = _derive_documents(records, plan)
    lexicon = _derive_lexicon(documents, plan)
    associations = _derive_associations(documents, lexicon, plan)
    topics = _derive_topics(associations, lexicon, plan)
    _add_topic_weights(documents, lexicon, topics)
    return documents, lexicon, associations, topics


def _derive_answer_bindings(
    records: Sequence[dict[str, Any]], plan: Mapping[str, Any]
) -> list[dict[str, Any]]:
    """Rederive reviewed PDF-page evidence bindings without package writes."""

    records_by_source_path: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        source_path = record.get("source_path")
        if isinstance(source_path, str) and source_path:
            records_by_source_path[source_path.replace("\\", "/")].append(record)
    bindings: list[dict[str, Any]] = []
    for record in records:
        attributes = record.get("attributes")
        if not isinstance(attributes, dict) or attributes.get("review_state") != "reviewed":
            continue
        raw_locator = attributes.get("evidence_locator")
        paper_id = _paper_id(record, plan)
        if not isinstance(raw_locator, str) or not raw_locator or paper_id is None:
            continue
        parsed: list[tuple[str, int]] = []
        valid = True
        for fragment in raw_locator.split(";"):
            match = EVIDENCE_FRAGMENT_RE.fullmatch(fragment)
            if match is None:
                valid = False
                break
            evidence_path = match.group("path").replace("\\", "/")
            _safe_relative(evidence_path, "reviewed evidence path")
            page = int(match.group("page"))
            targets = records_by_source_path.get(evidence_path, [])
            heading = f"## PDF page {page}"
            if not any(
                _paper_id(target, plan) == paper_id
                and isinstance(target.get("body"), str)
                and re.search(rf"(?m)^{re.escape(heading)}\s*$", target["body"])
                for target in targets
            ):
                valid = False
                break
            parsed.append((evidence_path, page))
        if not valid or not parsed:
            continue
        required = (
            "source_id",
            "record_id",
            "record_sha256",
            "concept_id",
            "concept_type",
            "concept_path",
            "source_path",
        )
        if any(not isinstance(record.get(field), str) or not record[field] for field in required):
            raise SnapshotError("reviewed evidence record has an invalid authoritative identity")
        concept_path = str(record["concept_path"]).replace("\\", "/")
        source_path = str(record["source_path"]).replace("\\", "/")
        _safe_relative(concept_path, "reviewed evidence concept path")
        _safe_relative(source_path, "reviewed evidence source path")
        pages = sorted({page for _, page in parsed})
        evidence_paths = sorted({path for path, _ in parsed})
        authoritative_text = attributes.get("interpretation")
        if not isinstance(authoritative_text, str) or not authoritative_text.strip():
            authoritative_text = str(record.get("body") or "")
        if not authoritative_text:
            raise SnapshotError("reviewed evidence record has no authoritative text")
        identity = {
            "source_id": record["source_id"],
            "record_id": record["record_id"],
            "record_sha256": record["record_sha256"],
            "paper_id": paper_id,
            "locator_tokens": [f"PDF-page-{page}" for page in pages],
        }
        row = {
            "binding_id": "answer-binding-" + sha256_canonical(identity)[:32],
            "source_id": record["source_id"],
            "record_id": record["record_id"],
            "record_sha256": record["record_sha256"],
            "concept_id": record["concept_id"],
            "concept_type": record["concept_type"],
            "concept_path": concept_path,
            "source_path": source_path,
            "paper_id": paper_id,
            "review_state": "reviewed",
            "locator_tokens": identity["locator_tokens"],
            "citation_pages": pages,
            "evidence_paths": evidence_paths,
            "authoritative_text": authoritative_text,
            "authoritative_text_sha256": sha256_bytes(authoritative_text.encode("utf-8")),
        }
        _exact_keys(row, ANSWER_BINDING_KEYS, f"answer binding {record['record_id']}")
        bindings.append(row)
    return sorted(bindings, key=lambda row: (row["source_id"], row["record_id"]))


def _derive_answer_documents(
    documents: Sequence[dict[str, Any]],
    answer_bindings: Sequence[dict[str, Any]],
    plan: Mapping[str, Any],
    lexicon: Mapping[str, Any],
    topics: Mapping[str, Any],
) -> list[dict[str, Any]]:
    """Derive a low-noise interpretation view while retaining claim-title signals."""

    binding_by_record = {
        (binding["source_id"], binding["record_id"]): binding
        for binding in answer_bindings
    }
    result: list[dict[str, Any]] = []
    for document in documents:
        binding = binding_by_record.get((document["source_id"], document["record_id"]))
        if binding is None:
            continue
        body_terms = Counter(tokenize(binding["authoritative_text"], plan))
        result.append(
            {
                "document_id": document["document_id"],
                "source_id": document["source_id"],
                "record_id": document["record_id"],
                "title_terms": dict(sorted(document["title_terms"].items())),
                "body_terms": dict(sorted(body_terms.items())),
                "title_length": int(document["title_length"]),
                "body_length": sum(body_terms.values()),
                "topic_weights": [],
            }
        )
    _add_topic_weights(result, lexicon, topics)
    return sorted(result, key=lambda row: row["document_id"])


def _artifact(path: Path, relative: str, count: int | None = None) -> dict[str, Any]:
    result: dict[str, Any] = {
        "path": relative,
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }
    if count is not None:
        result["count"] = count
    return result


def _validate_documents(
    root: Path,
    documents: Sequence[dict[str, Any]],
    records: Sequence[dict[str, Any]],
    plan: Mapping[str, Any],
    topics: Mapping[str, Any],
) -> None:
    record_by_key = {(row.get("source_id"), row.get("record_id")): row for row in records}
    if len(record_by_key) != len(records):
        raise SnapshotError("authoritative ledger contains duplicate source/record identities")
    term_topics = {row["term"]: row["topic_id"] for row in topics["term_topics"]}
    topic_ids = {row["topic_id"] for row in topics["topics"]}
    ids: list[str] = []
    for number, document in enumerate(documents, start=1):
        _exact_keys(document, DOCUMENT_KEYS, f"adaptive/documents.jsonl:{number}")
        if not isinstance(document["document_id"], str) or not DOCUMENT_ID_RE.fullmatch(document["document_id"]):
            raise SnapshotError(f"adaptive/documents.jsonl:{number} has an invalid document ID")
        if document["document_id"] != _document_id(document):
            raise SnapshotError(f"adaptive/documents.jsonl:{number} has a stale document ID")
        ids.append(document["document_id"])
        record = record_by_key.get((document["source_id"], document["record_id"]))
        if record is None:
            raise SnapshotError(f"adaptive/documents.jsonl:{number} is orphaned from the ledger")
        for field in (
            "record_sha256",
            "concept_id",
            "concept_type",
            "concept_path",
            "source_path",
            "title",
        ):
            if document[field] != record.get(field):
                raise SnapshotError(f"adaptive/documents.jsonl:{number} {field} differs from its record")
        if document["paper_id"] != _paper_id(record, plan):
            raise SnapshotError(f"adaptive/documents.jsonl:{number} paper identity differs from its record")
        if isinstance(document["ordinal"], bool) or not isinstance(document["ordinal"], int) or document["ordinal"] < 0:
            raise SnapshotError(f"adaptive/documents.jsonl:{number} has an invalid ordinal")
        concept = _safe_relative(document["concept_path"], "document concept_path")
        if concept.parts[0] != "concepts":
            raise SnapshotError("document concept path is outside concepts/")
        concept_file = root.joinpath(*concept.parts)
        if not concept_file.is_file() or concept_file.is_symlink():
            raise SnapshotError(f"document concept file is missing or unsafe: {document['concept_path']}")
        text = document["text"]
        if not isinstance(text, str) or not text or document["text_sha256"] != sha256_bytes(text.encode("utf-8")):
            raise SnapshotError(f"adaptive/documents.jsonl:{number} has invalid text or text hash")
        body = record.get("body")
        locator = document["locator"]
        if locator == {"kind": "record"}:
            if text != body:
                raise SnapshotError(f"adaptive/documents.jsonl:{number} record locator does not resolve")
        elif isinstance(locator, dict) and set(locator) == {"kind", "start", "end"} and locator.get("kind") == "character-range":
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
                raise SnapshotError(f"adaptive/documents.jsonl:{number} character locator does not resolve")
        else:
            raise SnapshotError(f"adaptive/documents.jsonl:{number} has an invalid locator")
        expected_title = _counter_object(tokenize(document["title"], plan))
        expected_body = _counter_object(tokenize(text, plan))
        if document["title_terms"] != expected_title or document["body_terms"] != expected_body:
            raise SnapshotError(f"adaptive/documents.jsonl:{number} token counts do not match text")
        if document["title_length"] != sum(expected_title.values()) or document["body_length"] != sum(expected_body.values()):
            raise SnapshotError(f"adaptive/documents.jsonl:{number} field lengths are invalid")
        seen_topics: set[str] = set()
        for item in document["topic_weights"]:
            if not isinstance(item, dict) or set(item) != {"topic_id", "weight"}:
                raise SnapshotError(f"adaptive/documents.jsonl:{number} has invalid topic weights")
            if item["topic_id"] not in topic_ids or item["topic_id"] in seen_topics:
                raise SnapshotError(f"adaptive/documents.jsonl:{number} has an unknown or duplicate topic")
            if isinstance(item["weight"], bool) or not isinstance(item["weight"], (int, float)) or not 0 < float(item["weight"]) <= 1:
                raise SnapshotError(f"adaptive/documents.jsonl:{number} has an invalid topic weight")
            seen_topics.add(item["topic_id"])
        if document["topic_weights"] != sorted(document["topic_weights"], key=lambda item: item["topic_id"]):
            raise SnapshotError(f"adaptive/documents.jsonl:{number} topic weights are not ordered")
        combined = Counter(expected_title) + Counter(expected_body)
        expected_topics = {term_topics[term] for term in combined if term in term_topics}
        if expected_topics and not seen_topics:
            raise SnapshotError(f"adaptive/documents.jsonl:{number} is missing derived topic weights")
    if ids != sorted(ids) or len(ids) != len(set(ids)):
        raise SnapshotError("adaptive documents must be uniquely ordered by document ID")


def _validate_associations(
    associations: Sequence[dict[str, Any]], lexicon: Mapping[str, Any], plan: Mapping[str, Any]
) -> None:
    term_stats = {row["term"]: row for row in lexicon["terms"]}
    terms: list[str] = []
    maximum = int(plan["associations"]["max_neighbors"])
    for number, row in enumerate(associations, start=1):
        if not isinstance(row, dict) or set(row) != {"term", "document_frequency", "corpus_frequency", "neighbors"}:
            raise SnapshotError(f"adaptive/associations.jsonl:{number} has an invalid shape")
        term = row["term"]
        if term not in term_stats or " " in term:
            raise SnapshotError(f"adaptive/associations.jsonl:{number} has an unknown term")
        if row["document_frequency"] != term_stats[term]["document_frequency"] or row["corpus_frequency"] != term_stats[term]["corpus_frequency"]:
            raise SnapshotError(f"adaptive/associations.jsonl:{number} statistics differ from the lexicon")
        if not isinstance(row["neighbors"], list) or len(row["neighbors"]) > maximum:
            raise SnapshotError(f"adaptive/associations.jsonl:{number} has an invalid neighbor array")
        previous: tuple[float, int, str] | None = None
        neighbor_terms: set[str] = set()
        for neighbor in row["neighbors"]:
            if not isinstance(neighbor, dict) or set(neighbor) != {"term", "cooccurrence", "ppmi"}:
                raise SnapshotError(f"adaptive/associations.jsonl:{number} has an invalid neighbor")
            if neighbor["term"] not in term_stats or neighbor["term"] == term or neighbor["term"] in neighbor_terms:
                raise SnapshotError(f"adaptive/associations.jsonl:{number} has an unknown or duplicate neighbor")
            if isinstance(neighbor["cooccurrence"], bool) or not isinstance(neighbor["cooccurrence"], int) or neighbor["cooccurrence"] < 1:
                raise SnapshotError(f"adaptive/associations.jsonl:{number} has an invalid cooccurrence")
            if isinstance(neighbor["ppmi"], bool) or not isinstance(neighbor["ppmi"], (int, float)) or not math.isfinite(float(neighbor["ppmi"])) or float(neighbor["ppmi"]) <= 0:
                raise SnapshotError(f"adaptive/associations.jsonl:{number} has an invalid PPMI")
            ordering = (-float(neighbor["ppmi"]), -neighbor["cooccurrence"], neighbor["term"])
            if previous is not None and ordering < previous:
                raise SnapshotError(f"adaptive/associations.jsonl:{number} neighbors are not ordered")
            previous = ordering
            neighbor_terms.add(neighbor["term"])
        terms.append(term)
    if terms != sorted(terms) or len(terms) != len(set(terms)):
        raise SnapshotError("association terms must be uniquely ordered")


def _validate_topics(topics: Any, associations: Sequence[dict[str, Any]], plan: Mapping[str, Any]) -> None:
    if not isinstance(topics, dict):
        raise SnapshotError("adaptive/topics.json root must be an object")
    _exact_keys(
        topics,
        {"schema_version", "algorithm", "requested_topic_count", "topic_count", "iterations", "term_topics", "topics"},
        "adaptive topics",
    )
    if topics["schema_version"] != SCHEMA_VERSION or topics["algorithm"] != ALGORITHMS["topics"]:
        raise SnapshotError("adaptive topic algorithm identity is invalid")
    if topics["requested_topic_count"] != plan["topics"]["topic_count"]:
        raise SnapshotError("requested topic count differs from the plan")
    _plain_int(topics["iterations"], "adaptive topics iterations", 1, int(plan["topics"]["max_iterations"]))
    if isinstance(topics["topic_count"], bool) or not isinstance(topics["topic_count"], int):
        raise SnapshotError("topic count must be an integer")
    if not isinstance(topics["topics"], list) or topics["topic_count"] != len(topics["topics"]):
        raise SnapshotError("topic count is invalid")
    topic_ids = [row.get("topic_id") for row in topics["topics"] if isinstance(row, dict)]
    if len(topic_ids) != len(topics["topics"]) or topic_ids != [f"topic-{index:02d}" for index in range(len(topic_ids))]:
        raise SnapshotError("topic IDs are invalid or unordered")
    association_terms = {row["term"] for row in associations}
    if not isinstance(topics["term_topics"], list) or any(
        not isinstance(row, dict) or set(row) != {"term", "topic_id"}
        for row in topics["term_topics"]
    ):
        raise SnapshotError("topic term mapping has an invalid shape")
    mapped_terms = [row["term"] for row in topics["term_topics"]]
    if mapped_terms != sorted(association_terms):
        raise SnapshotError("topic term mapping does not cover the association vocabulary exactly")
    if any(row["topic_id"] not in set(topic_ids) for row in topics["term_topics"]):
        raise SnapshotError("topic term mapping names an unknown topic")
    assigned_topic = {row["term"]: row["topic_id"] for row in topics["term_topics"]}
    topic_member_counts = Counter(assigned_topic.values())
    for row in topics["topics"]:
        if set(row) != {"topic_id", "seed", "term_count", "terms"} or row["seed"] not in association_terms:
            raise SnapshotError("topic row has an invalid shape or seed")
        if not isinstance(row["terms"], list) or not row["terms"] or len(row["terms"]) > plan["topics"]["top_terms"]:
            raise SnapshotError("topic top-term array is invalid")
        if (
            isinstance(row["term_count"], bool)
            or not isinstance(row["term_count"], int)
            or row["term_count"] != topic_member_counts[row["topic_id"]]
            or assigned_topic.get(row["seed"]) != row["topic_id"]
        ):
            raise SnapshotError("topic row has an invalid term count")
        previous: tuple[float, str] | None = None
        seen_terms: set[str] = set()
        for item in row["terms"]:
            if (
                not isinstance(item, dict)
                or set(item) != {"term", "weight"}
                or item["term"] not in association_terms
                or item["term"] in seen_terms
                or assigned_topic.get(item["term"]) != row["topic_id"]
                or isinstance(item["weight"], bool)
                or not isinstance(item["weight"], (int, float))
                or not math.isfinite(float(item["weight"]))
                or float(item["weight"]) <= 0
            ):
                raise SnapshotError("topic contains an invalid top term")
            ordering = (-float(item["weight"]), item["term"])
            if previous is not None and ordering < previous:
                raise SnapshotError("topic terms are not ordered")
            previous = ordering
            seen_terms.add(item["term"])


def load_snapshot(root: Path, *, deep_validation: bool = False) -> AdaptiveSnapshot:
    """Load one snapshot read-only, optionally rederiving every adaptive artifact."""

    root = root.expanduser()
    _reject_bundle_links(root)
    root = root.resolve()
    if not root.is_dir():
        raise SnapshotError(f"bundle does not exist or is not a directory: {root}")
    adaptive = root / "adaptive"
    expected_names = {
        "index.json",
        "documents.jsonl",
        "answer-bindings.jsonl",
        "lexicon.json",
        "associations.jsonl",
        "topics.json",
        "build-report.json",
    }
    if not adaptive.is_dir() or adaptive.is_symlink():
        raise SnapshotError("adaptive must be a real directory")
    actual_names = {path.name for path in adaptive.iterdir()}
    if actual_names != expected_names:
        raise SnapshotError(
            f"adaptive artifact set is closed; missing={sorted(expected_names - actual_names)}, unknown={sorted(actual_names - expected_names)}"
        )
    if any(path.is_symlink() or not path.is_file() for path in adaptive.iterdir()):
        raise SnapshotError("adaptive artifacts must be regular files")
    semantic_report = _load_json(root / "semantic" / "build-report.json", "semantic/build-report.json")
    if not isinstance(semantic_report, dict) or semantic_report.get("status") != "pass":
        raise SnapshotError("authoritative Semantic OKF build report is not passing")
    index = _load_json(adaptive / "index.json", "adaptive/index.json")
    if not isinstance(index, dict):
        raise SnapshotError("adaptive/index.json root must be an object")
    _exact_keys(
        index,
        {"schema_version", "authoritative", "core", "adaptive_plan_sha256", "plan", "selection", "algorithms", "artifacts", "summary"},
        "adaptive index",
    )
    if index["schema_version"] != SCHEMA_VERSION or index["authoritative"] is not False:
        raise SnapshotError("adaptive index version or authority marker is invalid")
    if index["algorithms"] != ALGORITHMS:
        raise SnapshotError("adaptive algorithm identities are invalid")
    plan = _validate_plan(index["plan"])
    if index["adaptive_plan_sha256"] != sha256_canonical(plan):
        raise SnapshotError("adaptive plan digest is invalid")
    records = _read_jsonl(root / "semantic" / "records.jsonl", "semantic/records.jsonl")
    source_manifest = _load_json(
        root / "semantic" / "source-manifest.json", "semantic/source-manifest.json"
    )
    sources = source_manifest.get("sources") if isinstance(source_manifest, dict) else None
    if not isinstance(sources, list) or any(not isinstance(item, dict) for item in sources):
        raise SnapshotError("semantic/source-manifest.json must contain an object source array")
    selected_records, expected_selection = _select_records(records, sources, plan)
    if index["selection"] != expected_selection:
        raise SnapshotError("adaptive source selection binding is invalid")
    core = {
        "tree_sha256": sha256_canonical(_core_inventory(root)),
        "records_sha256": sha256_file(root / "semantic" / "records.jsonl"),
        "record_count": len(records),
    }
    if index["core"] != core:
        raise SnapshotError("adaptive index core binding is stale or invalid")
    documents = _read_jsonl(adaptive / "documents.jsonl", "adaptive/documents.jsonl")
    answer_bindings = _read_jsonl(
        adaptive / "answer-bindings.jsonl", "adaptive/answer-bindings.jsonl"
    )
    lexicon = _load_json(adaptive / "lexicon.json", "adaptive/lexicon.json")
    associations = _read_jsonl(adaptive / "associations.jsonl", "adaptive/associations.jsonl")
    topics = _load_json(adaptive / "topics.json", "adaptive/topics.json")
    _validate_topics(topics, associations, plan)
    _validate_documents(root, documents, records, plan, topics)
    expected_answer_bindings = _derive_answer_bindings(selected_records, plan)
    if answer_bindings != expected_answer_bindings:
        raise SnapshotError(
            "adaptive answer bindings differ from deterministic authoritative derivation"
        )
    for number, binding in enumerate(answer_bindings, start=1):
        _exact_keys(binding, ANSWER_BINDING_KEYS, f"adaptive/answer-bindings.jsonl:{number}")
    if lexicon != _derive_lexicon(documents, plan):
        raise SnapshotError("adaptive lexicon differs from live document statistics")
    _validate_associations(associations, lexicon, plan)
    if deep_validation:
        expected_documents, expected_lexicon, expected_associations, expected_topics = _derive_all(
            selected_records, plan
        )
        if documents != expected_documents:
            raise SnapshotError("adaptive documents differ from authoritative deterministic derivation")
        if lexicon != expected_lexicon:
            raise SnapshotError("adaptive lexicon differs from authoritative deterministic derivation")
        if associations != expected_associations:
            raise SnapshotError("adaptive associations differ from independent deterministic PPMI derivation")
        if topics != expected_topics:
            raise SnapshotError("adaptive topics differ from independent deterministic topic derivation")
    artifacts = {
        "documents": _artifact(adaptive / "documents.jsonl", "adaptive/documents.jsonl", len(documents)),
        "answer_bindings": _artifact(
            adaptive / "answer-bindings.jsonl",
            "adaptive/answer-bindings.jsonl",
            len(answer_bindings),
        ),
        "lexicon": _artifact(adaptive / "lexicon.json", "adaptive/lexicon.json", len(lexicon["terms"])),
        "associations": _artifact(adaptive / "associations.jsonl", "adaptive/associations.jsonl", len(associations)),
        "topics": _artifact(adaptive / "topics.json", "adaptive/topics.json", topics["topic_count"]),
    }
    if index["artifacts"] != artifacts:
        raise SnapshotError("adaptive artifact hashes, sizes, or counts are invalid")
    summary = {
        "inputs": index["selection"]["input_count"],
        "records": len(selected_records),
        "documents": len(documents),
        "terms": len(lexicon["terms"]),
        "association_terms": len(associations),
        "topics": topics["topic_count"],
        "answer_bindings": len(answer_bindings),
    }
    if index["summary"] != summary:
        raise SnapshotError("adaptive index summary is invalid")
    expected_report = {
        "schema_version": SCHEMA_VERSION,
        "valid": True,
        "status": "pass",
        "errors": [],
        "warnings": [],
        "adaptive_plan_sha256": index["adaptive_plan_sha256"],
        "core": core,
        "selection": index["selection"],
        "summary": summary,
        "artifacts": {"index": _artifact(adaptive / "index.json", "adaptive/index.json"), **artifacts},
    }
    if _load_json(adaptive / "build-report.json", "adaptive/build-report.json") != expected_report:
        raise SnapshotError("adaptive build report differs from live validation")
    return AdaptiveSnapshot(
        root=root,
        index=index,
        documents=tuple(documents),
        answer_bindings=tuple(answer_bindings),
        answer_documents=tuple(
            _derive_answer_documents(documents, answer_bindings, plan, lexicon, topics)
        ),
        lexicon=lexicon,
        associations=tuple(associations),
        topics=topics,
        index_sha256=sha256_file(adaptive / "index.json"),
        deep_validation=deep_validation,
    )


def inspect_snapshot(snapshot: AdaptiveSnapshot) -> dict[str, Any]:
    """Return capabilities and authoritative paths for a validated snapshot."""

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
        "adaptive_index_sha256": snapshot.index_sha256,
        "adaptive_plan_sha256": snapshot.index["adaptive_plan_sha256"],
        "summary": snapshot.index["summary"],
        "capabilities": [
            "bm25",
            "topic",
            "association",
            "fusion",
            "adaptive",
            "evidence_rows",
            "answer_evidence_pack",
            "facet_coverage_pack",
            "authoritative_answer_finalizer",
        ],
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


def _bm25_scores(
    documents: Sequence[dict[str, Any]],
    query_weights: Mapping[str, float],
    lexicon: Mapping[str, Any],
    plan: Mapping[str, Any],
) -> dict[str, float]:
    stats = {row["term"]: row for row in lexicon["terms"]}
    average = lexicon["average_field_lengths"]
    config = plan["bm25"]
    k1, b = float(config["k1"]), float(config["b"])
    result: dict[str, float] = {}
    for document in documents:
        score = 0.0
        for term, query_weight in query_weights.items():
            term_stats = stats.get(term)
            if term_stats is None or query_weight <= 0:
                continue
            idf = float(term_stats["idf"])
            field_score = 0.0
            for field, weight in (("title", config["title_weight"]), ("body", config["body_weight"])):
                tf = document[f"{field}_terms"].get(term, 0)
                if not tf or weight <= 0:
                    continue
                length = document[f"{field}_length"]
                denominator = tf + k1 * (1.0 - b + b * length / max(float(average[field]), 1e-12))
                field_score += float(weight) * tf * (k1 + 1.0) / denominator
            score += float(query_weight) * idf * field_score
        if score > 0.0:
            result[document["document_id"]] = score
    return result


def _normalize_scores(scores: Mapping[str, float]) -> dict[str, float]:
    maximum = max(scores.values(), default=0.0)
    return {key: value / maximum for key, value in scores.items()} if maximum > 0 else {}


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
    query: str, snapshot: AdaptiveSnapshot
) -> tuple[dict[str, float], list[dict[str, Any]]]:
    plan = snapshot.index["plan"]
    graph = {
        row["term"]: {neighbor["term"]: float(neighbor["ppmi"]) for neighbor in row["neighbors"]}
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
    weights = {row["term"]: float(row["weight"]) * float(plan["expansion"]["association_weight"]) for row in rows}
    return weights, rows


def _topic_expansion(
    query: str,
    association_weights: Mapping[str, float],
    snapshot: AdaptiveSnapshot,
) -> tuple[dict[str, float], list[dict[str, Any]], dict[str, float]]:
    plan = snapshot.index["plan"]
    term_topic = {row["term"]: row["topic_id"] for row in snapshot.topics["term_topics"]}
    activation: defaultdict[str, float] = defaultdict(float)
    originals = set(_unigrams(query, plan))
    for term in originals:
        if term in term_topic:
            activation[term_topic[term]] += 1.0
    for term, weight in association_weights.items():
        if term in term_topic:
            activation[term_topic[term]] += weight
    total = sum(activation.values())
    query_topics = {key: value / total for key, value in activation.items()} if total else {}
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
            candidates.append((topic_weight * float(item["weight"]) / maximum, term, topic["topic_id"]))
    limit = int(plan["expansion"]["topic_terms"])
    selected = sorted(candidates, key=lambda item: (-item[0], item[1], item[2]))[:limit]
    rows = [
        {"term": term, "weight": round(weight, 8), "topic_id": topic_id, "source": "topic-community"}
        for weight, term, topic_id in selected
    ]
    weights = {row["term"]: float(row["weight"]) * float(plan["expansion"]["topic_weight"]) for row in rows}
    return weights, rows, query_topics


def _rank(scores: Mapping[str, float]) -> list[str]:
    return [key for key, _ in sorted(scores.items(), key=lambda item: (-item[1], item[0]))]


def _evidence_identity(hit: Mapping[str, Any]) -> str:
    """Return a collision-safe identity explicitly bound by the plan and ledger."""

    paper_id = hit.get("paper_id")
    if paper_id:
        return f"paper:{paper_id}"
    return canonical_json(["source-record", str(hit["source_id"]), str(hit["record_id"])])


def _rrf(
    rankings: Sequence[Sequence[str]],
    k: int,
    *,
    weights: Sequence[float] | None = None,
) -> dict[str, float]:
    result: defaultdict[str, float] = defaultdict(float)
    active_weights = tuple(weights) if weights is not None else (1.0,) * len(rankings)
    if len(active_weights) != len(rankings):
        raise SnapshotError("RRF weights must align with rankings")
    for ranking, weight in zip(rankings, active_weights, strict=True):
        for rank, identifier in enumerate(ranking, start=1):
            result[identifier] += float(weight) / (k + rank)
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
    selected_identities: set[str] = set()
    identity_counts: Counter[str] = Counter()
    identity_cap = int(plan["reranking"]["max_per_evidence_identity"])
    while pool_ids and len(selected) < top_k:
        choices: list[tuple[float, str]] = []
        for identifier in pool_ids:
            document = by_id[identifier]
            evidence_identity = _evidence_identity(document)
            if identity_counts[evidence_identity] >= identity_cap:
                continue
            vector = _topic_vector(document["topic_weights"])
            similarity = max(
                (_cosine(vector, _topic_vector(by_id[item]["topic_weights"])) for item in selected),
                default=0.0,
            )
            source_novelty = 1.0 if (
                document["source_id"] not in selected_sources and evidence_identity not in selected_identities
            ) else 0.0
            value = (
                float(plan["reranking"]["relevance_weight"]) * normalized.get(identifier, 0.0)
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
        evidence_identity = _evidence_identity(by_id[chosen])
        selected_identities.add(evidence_identity)
        identity_counts[evidence_identity] += 1
    return [by_id[identifier] for identifier in selected]


def decompose_query(query: str, plan: Mapping[str, Any]) -> list[str]:
    """Split a synthesis query without dropping short operands or duplicating the full query."""

    adaptive = plan["adaptive"]
    minimum = int(adaptive["minimum_aspect_tokens"])
    maximum = int(adaptive["maximum_aspects"])
    if maximum == 0:
        return []
    fragments = [
        candidate.strip(" ,.?;:-")
        for candidate in ASPECT_SPLIT_RE.split(query)
        if candidate.strip(" ,.?;:-")
    ]
    if len(fragments) <= 1:
        return []

    aspects: list[str] = []
    for fragment in fragments:
        if aspects and len(_unigrams(fragment, plan)) < minimum:
            aspects[-1] = f"{aspects[-1]} {fragment}"
        else:
            aspects.append(fragment)
    if len(aspects) > 1 and len(_unigrams(aspects[0], plan)) < minimum:
        aspects[1] = f"{aspects[0]} {aspects[1]}"
        aspects.pop(0)
    while len(aspects) > maximum:
        aspects[-2] = f"{aspects[-2]} {aspects[-1]}"
        aspects.pop()

    full_tokens = _unigrams(query, plan)
    result: list[str] = []
    for aspect in aspects:
        tokens = tuple(_unigrams(aspect, plan))
        if not tokens or list(tokens) == full_tokens:
            continue
        result.append(aspect)
    return result


def decompose_coverage_facets(
    query: str,
    plan: Mapping[str, Any],
    maximum_facets: int,
) -> list[str]:
    """Expose comma- and conjunction-delimited coverage units without answer hints."""

    if not isinstance(query, str) or not query.strip():
        raise SnapshotError("query must be nonempty")
    if (
        isinstance(maximum_facets, bool)
        or not isinstance(maximum_facets, int)
        or not 1 <= maximum_facets <= 32
    ):
        raise SnapshotError("maximum facets must be an integer from 1 through 32")
    result: list[str] = []
    for raw_fragment in FACET_SPLIT_RE.split(query):
        fragment = raw_fragment.strip(" ,.?;:-")
        terms = _unigrams(fragment, plan)
        named_singleton = len(terms) == 1 and any(character.isupper() for character in fragment)
        if (len(terms) >= 2 or named_singleton) and fragment not in result:
            result.append(fragment)
        if len(result) == maximum_facets:
            break
    return result


def _identity_ranking(results: Sequence[Mapping[str, Any]]) -> list[str]:
    ranking: list[str] = []
    for hit in results:
        identity = _evidence_identity(hit)
        if identity not in ranking:
            ranking.append(identity)
    return ranking


def _eligible_adaptive_identity(
    identity: str,
    full_top_k: set[str],
    aspect_ranks: Sequence[Mapping[str, int]],
    maximum_novel_aspect_rank: int,
) -> bool:
    """Gate novel evidence while always retaining full-query top-k eligibility."""

    return identity in full_top_k or any(
        ranks.get(identity) is not None
        and int(ranks[identity]) <= maximum_novel_aspect_rank
        for ranks in aspect_ranks
    )


def _evidence_row(
    hit: Mapping[str, Any],
    *,
    index_sha256: str,
    core_tree_sha256: str,
) -> dict[str, Any]:
    """Copy contract-ready evidence fields without model reconstruction."""

    return {
        "rank": hit["rank"],
        "evidence_identity": _evidence_identity(hit),
        "source_id": hit["source_id"],
        "paper_id": hit["paper_id"],
        "record_id": hit["record_id"],
        "record_sha256": hit["record_sha256"],
        "concept_id": hit["concept_id"],
        "concept_type": hit["concept_type"],
        "concept_path": hit["concept_path"],
        "source_path": hit["source_path"],
        "ordinal": hit["ordinal"],
        "locator": hit["locator"],
        "text": hit["text"],
        "text_sha256": hit["text_sha256"],
        "adaptive_index_sha256": index_sha256,
        "core_tree_sha256": core_tree_sha256,
    }


def _answer_evidence_row(
    binding: Mapping[str, Any],
    *,
    rank: int,
    index_sha256: str,
    core_tree_sha256: str,
) -> dict[str, Any]:
    """Expose distinct locator tokens and integer citation pages losslessly."""

    return {
        "rank": rank,
        "binding_id": binding["binding_id"],
        "source_id": binding["source_id"],
        "record_id": binding["record_id"],
        "record_sha256": binding["record_sha256"],
        "concept_id": binding["concept_id"],
        "concept_type": binding["concept_type"],
        "concept_path": binding["concept_path"],
        "source_path": binding["source_path"],
        "paper_id": binding["paper_id"],
        "review_state": binding["review_state"],
        "locator_tokens": list(binding["locator_tokens"]),
        "citation_pages": list(binding["citation_pages"]),
        "evidence_paths": list(binding["evidence_paths"]),
        "authoritative_text": binding["authoritative_text"],
        "authoritative_text_sha256": binding["authoritative_text_sha256"],
        "adaptive_index_sha256": index_sha256,
        "core_tree_sha256": core_tree_sha256,
    }


def _matching_answer_evidence_rows(
    snapshot: AdaptiveSnapshot, results: Sequence[Mapping[str, Any]]
) -> list[dict[str, Any]]:
    by_record = {
        (binding["source_id"], binding["record_id"]): binding
        for binding in snapshot.answer_bindings
    }
    return [
        _answer_evidence_row(
            binding,
            rank=int(hit["rank"]),
            index_sha256=snapshot.index_sha256,
            core_tree_sha256=snapshot.index["core"]["tree_sha256"],
        )
        for hit in results
        if (
            binding := by_record.get((hit.get("source_id"), hit.get("record_id")))
        )
        is not None
    ]


def _search_adaptive(
    snapshot: AdaptiveSnapshot,
    query: str,
    top_k: int,
    *,
    source_ids: Sequence[str],
    concept_ids: Sequence[str],
    concept_types: Sequence[str],
) -> dict[str, Any]:
    """Fuse a protected full-query ranking with deterministic aspect rankings."""

    plan = snapshot.index["plan"]
    adaptive = plan["adaptive"]
    pool = min(1000, max(top_k, int(plan["reranking"]["candidate_pool"])))
    common = {
        "source_ids": source_ids,
        "concept_ids": concept_ids,
        "concept_types": concept_types,
    }
    full = search_snapshot(snapshot, query, "fusion", pool, **common)
    aspects = decompose_query(query, plan)
    aspect_runs = [search_snapshot(snapshot, aspect, "fusion", pool, **common) for aspect in aspects]
    full_ranking = _identity_ranking(full["results"])
    aspect_rankings = [_identity_ranking(run["results"]) for run in aspect_runs]
    rrf_k = int(adaptive["rrf_k"])
    scores: defaultdict[str, float] = defaultdict(float)
    full_ranks = {identity: rank for rank, identity in enumerate(full_ranking, start=1)}
    aspect_ranks: list[dict[str, int]] = [
        {identity: rank for rank, identity in enumerate(ranking, start=1)}
        for ranking in aspect_rankings
    ]
    for identity, rank in full_ranks.items():
        scores[identity] += float(adaptive["full_query_weight"]) / (rrf_k + rank)
    if aspect_rankings:
        divisor = float(len(aspect_rankings))
        for ranks in aspect_ranks:
            for identity, rank in ranks.items():
                scores[identity] += float(adaptive["aspect_weight"]) / divisor / (rrf_k + rank)
        if float(adaptive["best_aspect_weight"]) > 0:
            for identity in set().union(*(set(ranks) for ranks in aspect_ranks)):
                best_rank = min(ranks[identity] for ranks in aspect_ranks if identity in ranks)
                scores[identity] += float(adaptive["best_aspect_weight"]) / (rrf_k + best_rank)

    candidates: defaultdict[str, list[tuple[int, int, str, Mapping[str, Any]]]] = defaultdict(list)
    for hit in full["results"]:
        candidates[_evidence_identity(hit)].append((int(hit["rank"]), 0, query, hit))
    for aspect_number, (aspect, run) in enumerate(zip(aspects, aspect_runs), start=1):
        for hit in run["results"]:
            candidates[_evidence_identity(hit)].append((int(hit["rank"]), aspect_number, aspect, hit))

    protected = min(int(adaptive["protected_full_results"]), top_k)
    selected_identities = full_ranking[:protected]
    full_top_k = set(full_ranking[:top_k])
    maximum_novel_aspect_rank = int(adaptive["maximum_novel_aspect_rank"])
    selected_identities.extend(
        identity
        for identity in sorted(scores, key=lambda item: (-scores[item], item))
        if identity not in selected_identities
        and _eligible_adaptive_identity(
            identity,
            full_top_k,
            aspect_ranks,
            maximum_novel_aspect_rank,
        )
    )
    selected_identities = selected_identities[:top_k]
    results: list[dict[str, Any]] = []
    for rank, identity in enumerate(selected_identities, start=1):
        _, aspect_number, selected_query, source_hit = sorted(candidates[identity], key=lambda row: (row[0], row[1]))[0]
        hit = dict(source_hit)
        component_scores = dict(hit["scores"])
        component_scores["adaptive"] = scores[identity]
        hit.update(
            {
                "rank": rank,
                "score": scores[identity],
                "scores": component_scores,
                "adaptive": {
                    "evidence_identity": identity,
                    "selected_query": selected_query,
                    "selected_query_kind": "full" if aspect_number == 0 else "aspect",
                    "full_query_rank": full_ranks.get(identity),
                    "aspect_ranks": [ranks.get(identity) for ranks in aspect_ranks],
                },
            }
        )
        results.append(hit)

    core_tree_sha256 = snapshot.index["core"]["tree_sha256"]
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "pass",
        "authoritative": False,
        "discovery_only": True,
        "query": query,
        "requested_mode": "adaptive",
        "effective_mode": "adaptive",
        "top_k": top_k,
        "returned": len(results),
        "filters": full["filters"],
        "expansion": full["expansion"],
        "adaptive": {
            "algorithm": ALGORITHMS["adaptive"],
            "aspects": aspects,
            "full_query_weight": adaptive["full_query_weight"],
            "aspect_weight": adaptive["aspect_weight"],
            "best_aspect_weight": adaptive["best_aspect_weight"],
            "rrf_k": adaptive["rrf_k"],
            "protected_full_results": protected,
            "maximum_novel_aspect_rank": maximum_novel_aspect_rank,
            "candidate_pool": pool,
        },
        "snapshot": full["snapshot"],
        "results": results,
        "evidence_rows": [
            _evidence_row(
                hit,
                index_sha256=snapshot.index_sha256,
                core_tree_sha256=core_tree_sha256,
            )
            for hit in results
        ],
        "answer_evidence_rows": _matching_answer_evidence_rows(snapshot, results),
        "answer_evidence_contract": {
            "adapter": ALGORITHMS["answer_evidence_adapter"],
            "record_id_role": "copy as claim_id only when the authoritative record is a claim",
            "locator_tokens_role": "copy as string evidence locators such as PDF-page-7",
            "citation_pages_role": "copy as integer citation pages such as 7",
        },
        "evidence_contract": {
            "adapter": ALGORITHMS["evidence_adapter"],
            "copy_fields_only": True,
            "authoritative_verification_required": True,
            "locator_basis": "semantic/records.jsonl record.body",
        },
    }


def search_snapshot(
    snapshot: AdaptiveSnapshot,
    query: str,
    mode: str,
    top_k: int,
    *,
    source_ids: Sequence[str] = (),
    concept_ids: Sequence[str] = (),
    concept_types: Sequence[str] = (),
) -> dict[str, Any]:
    """Search one validated snapshot with BM25, topic, association, or fusion ranking."""

    if mode not in {"bm25", "topic", "association", "fusion", "adaptive"}:
        raise SnapshotError("mode must be bm25, topic, association, fusion, or adaptive")
    if not isinstance(query, str) or not query.strip():
        raise SnapshotError("query must be nonempty")
    if isinstance(top_k, bool) or not isinstance(top_k, int) or not 1 <= top_k <= 1000:
        raise SnapshotError("top-k must be an integer from 1 through 1000")
    if mode == "adaptive":
        return _search_adaptive(
            snapshot,
            query,
            top_k,
            source_ids=source_ids,
            concept_ids=concept_ids,
            concept_types=concept_types,
        )
    source_filter, concept_filter, type_filter = set(source_ids), set(concept_ids), set(concept_types)
    documents = [
        row
        for row in snapshot.documents
        if (not source_filter or row["source_id"] in source_filter)
        and (not concept_filter or row["concept_id"] in concept_filter)
        and (not type_filter or row["concept_type"] in type_filter)
    ]
    plan = snapshot.index["plan"]
    original = Counter(tokenize(query, plan))
    original_weights = {term: float(count) for term, count in original.items()}
    association_weights, association_rows = _association_expansion(query, snapshot)
    topic_weights, topic_rows, query_topics = _topic_expansion(query, association_weights, snapshot)
    association_query = dict(original_weights)
    for term, weight in association_weights.items():
        association_query[term] = association_query.get(term, 0.0) + weight
    topic_query = dict(association_query)
    for term, weight in topic_weights.items():
        topic_query[term] = topic_query.get(term, 0.0) + weight
    bm25 = _bm25_scores(documents, original_weights, snapshot.lexicon, plan)
    association = _bm25_scores(documents, association_query, snapshot.lexicon, plan)
    topic_lexical = _bm25_scores(documents, topic_query, snapshot.lexicon, plan)
    normalized_topic_lexical = _normalize_scores(topic_lexical)
    topic_scores = {
        row["document_id"]: 0.8 * normalized_topic_lexical.get(row["document_id"], 0.0)
        + 0.2 * _cosine(query_topics, _topic_vector(row["topic_weights"]))
        for row in documents
    }
    topic_scores = {key: value for key, value in topic_scores.items() if value > 0}
    fusion = _rrf(
        [_rank(bm25), _rank(association), _rank(topic_scores)],
        int(plan["reranking"]["rrf_k"]),
    )
    route_scores = {"bm25": bm25, "association": association, "topic": topic_scores, "fusion": fusion}
    scores = route_scores[mode]
    if mode == "bm25":
        selected_ids = _rank(scores)[:top_k]
        by_id = {row["document_id"]: row for row in documents}
        selected = [by_id[identifier] for identifier in selected_ids]
    else:
        selected = _diversify(documents, scores, top_k, plan)
    component_ranks = {
        name: {identifier: rank for rank, identifier in enumerate(_rank(values), start=1)}
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
                "scores": {name: values.get(identifier) for name, values in route_scores.items()},
                "ranks": {name: ranks.get(identifier) for name, ranks in component_ranks.items()},
                "topic_weights": document["topic_weights"],
            }
        )
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "pass",
        "authoritative": False,
        "discovery_only": True,
        "query": query,
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
        "snapshot": {
            "core_tree_sha256": snapshot.index["core"]["tree_sha256"],
            "adaptive_index_sha256": snapshot.index_sha256,
            "adaptive_plan_sha256": snapshot.index["adaptive_plan_sha256"],
            "deep_validation": snapshot.deep_validation,
        },
        "results": results,
        "evidence_rows": [
            _evidence_row(
                hit,
                index_sha256=snapshot.index_sha256,
                core_tree_sha256=snapshot.index["core"]["tree_sha256"],
            )
            for hit in results
        ],
        "answer_evidence_rows": _matching_answer_evidence_rows(snapshot, results),
        "answer_evidence_contract": {
            "adapter": ALGORITHMS["answer_evidence_adapter"],
            "record_id_role": "copy as claim_id only when the authoritative record is a claim",
            "locator_tokens_role": "copy as string evidence locators such as PDF-page-7",
            "citation_pages_role": "copy as integer citation pages such as 7",
        },
        "evidence_contract": {
            "adapter": ALGORITHMS["evidence_adapter"],
            "copy_fields_only": True,
            "authoritative_verification_required": True,
            "locator_basis": "semantic/records.jsonl record.body",
        },
    }


def _rank_answer_documents(
    snapshot: AdaptiveSnapshot,
    documents: Sequence[dict[str, Any]],
    original_weights: Mapping[str, float],
    association_query: Mapping[str, float],
    topic_query: Mapping[str, float],
    query_topics: Mapping[str, float],
) -> list[str]:
    """Rank one deterministic answer-document view with shared query signals."""

    plan = snapshot.index["plan"]
    bm25 = _bm25_scores(documents, original_weights, snapshot.lexicon, plan)
    association = _bm25_scores(documents, association_query, snapshot.lexicon, plan)
    topic_lexical = _bm25_scores(documents, topic_query, snapshot.lexicon, plan)
    normalized_topic_lexical = _normalize_scores(topic_lexical)
    topic_scores = {
        row["document_id"]: 0.8 * normalized_topic_lexical.get(row["document_id"], 0.0)
        + 0.2 * _cosine(query_topics, _topic_vector(row["topic_weights"]))
        for row in documents
    }
    topic_scores = {key: value for key, value in topic_scores.items() if value > 0}
    return _rank(
        _rrf(
            [_rank(bm25), _rank(association), _rank(topic_scores)],
            int(plan["reranking"]["rrf_k"]),
        )
    )


def _binding_ranking(
    snapshot: AdaptiveSnapshot,
    query: str,
    documents: Sequence[dict[str, Any]],
    binding_by_record: Mapping[tuple[str, str], Mapping[str, Any]],
) -> tuple[list[str], dict[str, Any]]:
    """Fuse full-record and reviewed-interpretation views without paper deduplication."""

    plan = snapshot.index["plan"]
    original = Counter(tokenize(query, plan))
    original_weights = {term: float(count) for term, count in original.items()}
    association_weights, association_rows = _association_expansion(query, snapshot)
    topic_weights, topic_rows, query_topics = _topic_expansion(
        query, association_weights, snapshot
    )
    association_query = dict(original_weights)
    for term, weight in association_weights.items():
        association_query[term] = association_query.get(term, 0.0) + weight
    topic_query = dict(association_query)
    for term, weight in topic_weights.items():
        topic_query[term] = topic_query.get(term, 0.0) + weight
    eligible_ids = {document["document_id"] for document in documents}
    interpretation_documents = [
        document
        for document in snapshot.answer_documents
        if document["document_id"] in eligible_ids
    ]
    by_document = {row["document_id"]: row for row in documents}
    binding_rankings: list[list[str]] = []
    view_specs = [
        ("full-authoritative-record", ANSWER_FULL_RECORD_WEIGHT, documents),
        (
            "reviewed-interpretation",
            ANSWER_INTERPRETATION_WEIGHT,
            interpretation_documents,
        ),
    ]
    active_views = [view for view in view_specs if view[1] > 0.0]
    for _, _, view_documents in active_views:
        document_ranking = _rank_answer_documents(
            snapshot,
            view_documents,
            original_weights,
            association_query,
            topic_query,
            query_topics,
        )
        binding_ranking: list[str] = []
        for document_id in document_ranking:
            document = by_document[document_id]
            binding = binding_by_record[(document["source_id"], document["record_id"])]
            if binding["binding_id"] not in binding_ranking:
                binding_ranking.append(binding["binding_id"])
        binding_rankings.append(binding_ranking)
    fused = _rrf(
        binding_rankings,
        int(plan["reranking"]["rrf_k"]),
        weights=tuple(view[1] for view in active_views),
    )
    ranking: list[str] = []
    for binding_id in _rank(fused):
        if binding_id not in ranking:
            ranking.append(binding_id)
    return ranking, {
        "record_views": [
            {"view": name, "weight": weight}
            for name, weight, _ in active_views
        ],
        "maximum_initial_claims_per_paper": ANSWER_INITIAL_PAPER_CAP,
        "association_terms": association_rows,
        "topic_terms": topic_rows,
        "query_topics": [
            {"topic_id": topic_id, "weight": round(weight, 8)}
            for topic_id, weight in sorted(query_topics.items())
        ],
    }


def _diversify_answer_bindings(
    ordered: Sequence[str],
    binding_by_id: Mapping[str, Mapping[str, Any]],
    top_k: int,
) -> list[str]:
    """Fill an initial paper-diverse pass, then backfill without losing evidence."""

    selected: list[str] = []
    counts: Counter[str] = Counter()
    for binding_id in ordered:
        paper_id = str(binding_by_id[binding_id]["paper_id"])
        if counts[paper_id] < ANSWER_INITIAL_PAPER_CAP:
            selected.append(binding_id)
            counts[paper_id] += 1
        if len(selected) == top_k:
            return selected
    for binding_id in ordered:
        if binding_id not in selected:
            selected.append(binding_id)
        if len(selected) == top_k:
            break
    return selected


def build_evidence_pack(
    snapshot: AdaptiveSnapshot,
    query: str,
    top_k: int,
) -> dict[str, Any]:
    """Build a read-only, contract-ready evidence pack for answer synthesis."""

    if not isinstance(query, str) or not query.strip():
        raise SnapshotError("query must be nonempty")
    if isinstance(top_k, bool) or not isinstance(top_k, int) or not 1 <= top_k <= 1000:
        raise SnapshotError("top-k must be an integer from 1 through 1000")
    binding_by_record = {
        (binding["source_id"], binding["record_id"]): binding
        for binding in snapshot.answer_bindings
    }
    binding_by_id = {binding["binding_id"]: binding for binding in snapshot.answer_bindings}
    documents = [
        document
        for document in snapshot.documents
        if (document["source_id"], document["record_id"]) in binding_by_record
    ]
    if not documents:
        raise SnapshotError("snapshot has no verified answer-evidence bindings")
    full_ranking, expansion = _binding_ranking(
        snapshot, query, documents, binding_by_record
    )
    aspects = decompose_query(query, snapshot.index["plan"])
    aspect_rankings = [
        _binding_ranking(snapshot, aspect, documents, binding_by_record)[0]
        for aspect in aspects
    ]
    adaptive = snapshot.index["plan"]["adaptive"]
    rrf_k = int(adaptive["rrf_k"])
    scores: defaultdict[str, float] = defaultdict(float)
    for rank, binding_id in enumerate(full_ranking, start=1):
        scores[binding_id] += float(adaptive["full_query_weight"]) / (rrf_k + rank)
    if aspect_rankings:
        divisor = float(len(aspect_rankings))
        for ranking in aspect_rankings:
            for rank, binding_id in enumerate(ranking, start=1):
                scores[binding_id] += (
                    float(adaptive["aspect_weight"]) / divisor / (rrf_k + rank)
                )
    protected = min(int(adaptive["protected_full_results"]), top_k)
    selected = full_ranking[:protected]
    selected.extend(
        binding_id
        for binding_id in sorted(scores, key=lambda item: (-scores[item], item))
        if binding_id not in selected
    )
    selected = _diversify_answer_bindings(selected, binding_by_id, top_k)
    ranked_bindings = [
        _answer_evidence_row(
            binding_by_id[binding_id],
            rank=rank,
            index_sha256=snapshot.index_sha256,
            core_tree_sha256=snapshot.index["core"]["tree_sha256"],
        )
        for rank, binding_id in enumerate(selected, start=1)
    ]
    claim_evidence = sorted(
        (
            {
                "claim_id": row["record_id"],
                "concept_path": row["concept_path"],
                "paper_id": row["paper_id"],
                "source_path": row["source_path"],
                "locators": row["locator_tokens"],
            }
            for row in ranked_bindings
            if "claim" in row["concept_type"].casefold()
        ),
        key=lambda row: row["claim_id"],
    )
    citation_pages: defaultdict[str, set[int]] = defaultdict(set)
    for row in ranked_bindings:
        citation_pages[row["paper_id"]].update(row["citation_pages"])
    citations = [
        {"paper_id": paper_id, "pages": sorted(pages)}
        for paper_id, pages in sorted(citation_pages.items())
    ]
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "pass",
        "authoritative": False,
        "discovery_only": True,
        "query": query,
        "algorithm": ALGORITHMS["answer_evidence_ranking"],
        "aspects": aspects,
        "top_k": top_k,
        "returned": len(ranked_bindings),
        "expansion": expansion,
        "snapshot": {
            "core_tree_sha256": snapshot.index["core"]["tree_sha256"],
            "adaptive_index_sha256": snapshot.index_sha256,
            "adaptive_plan_sha256": snapshot.index["adaptive_plan_sha256"],
            "deep_validation": snapshot.deep_validation,
        },
        "ranked_bindings": ranked_bindings,
        "claim_evidence": claim_evidence,
        "citations": citations,
        "response_mapping": {
            "claim_id": "copy claim_evidence.claim_id from authoritative record_id",
            "evidence_locators": "copy claim_evidence.locators as canonical PDF-page-N strings",
            "citation_pages": "copy citations.pages as integers",
            "sorting": "claim_evidence is sorted by claim_id; citations is sorted by paper_id",
        },
    }


def _coverage_candidate(
    binding: Mapping[str, Any],
    *,
    rank: int,
) -> dict[str, Any]:
    """Return one compact claim candidate with response-ready locator ordering."""

    return {
        "rank": rank,
        "claim_id": binding["record_id"],
        "paper_id": binding["paper_id"],
        "authoritative_text": binding["authoritative_text"],
        "concept_path": binding["concept_path"],
        "source_path": binding["source_path"],
        "locators": sorted(set(binding["locator_tokens"])),
        "citation_pages": sorted(set(binding["citation_pages"])),
    }


def build_coverage_pack(
    snapshot: AdaptiveSnapshot,
    query: str,
    top_k: int,
    per_facet: int,
    maximum_facets: int,
) -> dict[str, Any]:
    """Keep enumeration facets separate so one strong clause cannot hide another."""

    if not isinstance(query, str) or not query.strip():
        raise SnapshotError("query must be nonempty")
    if isinstance(top_k, bool) or not isinstance(top_k, int) or not 1 <= top_k <= 1000:
        raise SnapshotError("top-k must be an integer from 1 through 1000")
    if (
        isinstance(per_facet, bool)
        or not isinstance(per_facet, int)
        or not 1 <= per_facet <= 30
    ):
        raise SnapshotError("per-facet must be an integer from 1 through 30")
    facets = decompose_coverage_facets(query, snapshot.index["plan"], maximum_facets)
    primary = build_evidence_pack(snapshot, query, top_k)
    binding_by_record = {
        (binding["source_id"], binding["record_id"]): binding
        for binding in snapshot.answer_bindings
    }
    binding_by_id = {binding["binding_id"]: binding for binding in snapshot.answer_bindings}
    documents = [
        document
        for document in snapshot.documents
        if (document["source_id"], document["record_id"]) in binding_by_record
    ]
    facet_rows: list[dict[str, Any]] = []
    union: set[str] = set()
    for facet in facets:
        ranking, _ = _binding_ranking(snapshot, facet, documents, binding_by_record)
        selected = _diversify_answer_bindings(ranking, binding_by_id, per_facet)
        candidates = [
            _coverage_candidate(binding_by_id[binding_id], rank=rank)
            for rank, binding_id in enumerate(selected, start=1)
        ]
        union.update(row["claim_id"] for row in candidates)
        facet_rows.append(
            {
                "facet": facet,
                "returned": len(candidates),
                "candidates": candidates,
            }
        )
    union.update(row["record_id"] for row in primary["ranked_bindings"])
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "pass",
        "authoritative": False,
        "discovery_only": True,
        "query": query,
        "algorithm": COVERAGE_ALGORITHM,
        "top_k": top_k,
        "per_facet": per_facet,
        "maximum_facets": maximum_facets,
        "facet_count": len(facet_rows),
        "unique_candidate_claims": len(union),
        "primary": primary,
        "coverage_facets": facet_rows,
        "coverage_contract": {
            "facet_derivation": "query punctuation and conjunctions only",
            "ground_truth_inputs": False,
            "candidate_role": "inspect each facet independently before drafting",
            "authoritative_verification_required": True,
            "finalizer": ANSWER_FINALIZER_ALGORITHM,
        },
    }


def _resolved_external_file(snapshot: AdaptiveSnapshot, path: Path, label: str) -> Path:
    """Resolve a readable file and reject drafts placed inside the immutable bundle."""

    try:
        resolved = path.expanduser().resolve(strict=True)
    except OSError as exc:
        raise SnapshotError(f"cannot read {label}: {exc}") from exc
    if not resolved.is_file():
        raise SnapshotError(f"{label} must be a regular file")
    try:
        resolved.relative_to(snapshot.root)
    except ValueError:
        return resolved
    raise SnapshotError(f"{label} must remain outside the immutable bundle")


def finalize_answer(
    snapshot: AdaptiveSnapshot,
    draft_path: Path | None,
    question_id: str,
    minimum_summary_words: int,
    maximum_summary_words: int,
    *,
    draft_payload: str | None = None,
) -> dict[str, Any]:
    """Rebuild response evidence from authoritative bindings and enforce its contract."""

    if not isinstance(question_id, str) or not question_id.strip():
        raise SnapshotError("question ID must be nonempty")
    for value, label in (
        (minimum_summary_words, "minimum summary words"),
        (maximum_summary_words, "maximum summary words"),
    ):
        if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= 5000:
            raise SnapshotError(f"{label} must be an integer from 1 through 5000")
    if minimum_summary_words > maximum_summary_words:
        raise SnapshotError("minimum summary words cannot exceed maximum summary words")
    if (draft_path is None) == (draft_payload is None):
        raise SnapshotError("provide exactly one answer draft path or standard-input payload")
    if draft_payload is not None:
        draft = strict_json_loads(draft_payload, label="answer draft")
    else:
        assert draft_path is not None
        draft = _load_json(
            _resolved_external_file(snapshot, draft_path, "answer draft"),
            "answer draft",
        )
    if not isinstance(draft, dict):
        raise SnapshotError("answer draft root must be an object")
    _exact_keys(draft, {"summary", "claims"}, "answer draft")
    summary = draft["summary"]
    if not isinstance(summary, str) or not summary.strip():
        raise SnapshotError("answer draft summary must be nonempty")
    word_count = len(summary.strip().split())
    if not minimum_summary_words <= word_count <= maximum_summary_words:
        raise SnapshotError(
            "answer draft summary must contain "
            f"{minimum_summary_words} through {maximum_summary_words} words; got {word_count}"
        )
    raw_claims = draft["claims"]
    if not isinstance(raw_claims, list) or not raw_claims:
        raise SnapshotError("answer draft claims must be a nonempty array")
    binding_by_claim = {
        binding["record_id"]: binding
        for binding in snapshot.answer_bindings
        if "claim" in binding["concept_type"].casefold()
    }
    claims: list[dict[str, Any]] = []
    selected_claim_ids: set[str] = set()
    for number, raw_claim in enumerate(raw_claims, start=1):
        if not isinstance(raw_claim, dict):
            raise SnapshotError(f"answer draft claim {number} must be an object")
        _exact_keys(
            raw_claim,
            {"statement", "supporting_claim_ids"},
            f"answer draft claim {number}",
        )
        statement = raw_claim["statement"]
        identifiers = raw_claim["supporting_claim_ids"]
        if not isinstance(statement, str) or not statement.strip():
            raise SnapshotError(f"answer draft claim {number} statement must be nonempty")
        if (
            not isinstance(identifiers, list)
            or not identifiers
            or any(not isinstance(identifier, str) for identifier in identifiers)
        ):
            raise SnapshotError(
                f"answer draft claim {number} supporting IDs must be a nonempty string array"
            )
        ordered_identifiers = sorted(set(identifiers))
        unknown = sorted(set(ordered_identifiers) - set(binding_by_claim))
        if unknown:
            raise SnapshotError(
                f"answer draft claim {number} names unknown claim IDs: {unknown}"
            )
        selected_claim_ids.update(ordered_identifiers)
        claims.append(
            {
                "statement": statement.strip(),
                "supporting_claim_ids": ordered_identifiers,
            }
        )
    selected = [binding_by_claim[identifier] for identifier in sorted(selected_claim_ids)]
    paper_ids = sorted({binding["paper_id"] for binding in selected})
    pages_by_paper: defaultdict[str, set[int]] = defaultdict(set)
    for binding in selected:
        pages_by_paper[binding["paper_id"]].update(binding["citation_pages"])
    citations = [
        {"paper_id": paper_id, "pages": sorted(pages_by_paper[paper_id])}
        for paper_id in paper_ids
    ]
    evidence = [
        {
            "claim_id": binding["record_id"],
            "concept_path": binding["concept_path"],
            "paper_id": binding["paper_id"],
            "source_path": binding["source_path"],
            "locators": sorted(set(binding["locator_tokens"])),
        }
        for binding in selected
    ]
    return {
        "question_id": question_id.strip(),
        "answer": {
            "summary": summary.strip(),
            "claims": claims,
            "paper_ids": paper_ids,
            "citations": citations,
        },
        "evidence": evidence,
    }
