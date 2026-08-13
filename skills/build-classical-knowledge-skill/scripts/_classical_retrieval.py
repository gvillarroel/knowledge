#!/usr/bin/env python3
"""Build and validate deterministic classical retrieval artifacts for Semantic OKF."""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import shutil
import tempfile
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Mapping, Sequence

from _semantic_okf import validate_semantic_bundle


SCHEMA_VERSION = "1.0"
STOPWORDS_ID = "english-v1"
TOKENIZER_ID = "ascii-alphanumeric-v1"
TOKEN_RE = re.compile(r"[a-z0-9]+", re.IGNORECASE)
PAGE_RE = re.compile(r"(?m)^## PDF page \d+\s*$")
PAPER_RE = re.compile(r"(?<!\d)(\d{4})[.-](\d{5}v\d+)(?!\d)", re.IGNORECASE)
HEX_64 = re.compile(r"[0-9a-f]{64}")
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
ARTIFACT_NAMES = {
    "documents": "classical/documents.jsonl",
    "lexicon": "classical/lexicon.json",
    "associations": "classical/associations.jsonl",
    "topics": "classical/topics.json",
}
ALGORITHMS = {
    "bm25": "okapi-bm25f-v1",
    "associations": "windowed-positive-pmi-v1",
    "topics": "deterministic-seeded-weighted-label-propagation-v1",
    "topic_scoring": "normalized-bm25-plus-topic-cosine-v1",
    "association_scoring": "two-step-ppmi-query-propagation-v1",
    "fusion": "reciprocal-rank-fusion-v1",
    "reranking": "topic-and-source-mmr-v1",
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


class ClassicalError(RuntimeError):
    """Describe an invalid plan, projection, or atomic classical build."""


@dataclass(frozen=True)
class ClassicalPlan:
    """Hold one validated closed classical-retrieval plan."""

    raw: dict[str, Any]
    sha256: str
    source_ids: tuple[str, ...]


def canonical_json(value: Any) -> str:
    """Serialize JSON deterministically and reject non-finite numbers."""

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
    """Hash deterministic UTF-8 JSON."""

    return sha256_bytes(canonical_json(value).encode("utf-8"))


def strict_json_loads(payload: str, *, label: str) -> Any:
    """Load JSON while rejecting duplicate keys and non-standard numbers."""

    def reject_constant(value: str) -> Any:
        raise ClassicalError(f"{label} contains non-standard number {value!r}")

    def reject_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ClassicalError(f"{label} contains duplicate member {key!r}")
            result[key] = value
        return result

    try:
        return json.loads(
            payload,
            object_pairs_hook=reject_duplicates,
            parse_constant=reject_constant,
        )
    except json.JSONDecodeError as exc:
        raise ClassicalError(f"{label} is invalid JSON: {exc}") from exc


def _exact_keys(value: Mapping[str, Any], expected: set[str], label: str) -> None:
    actual = set(value)
    if actual != expected:
        raise ClassicalError(
            f"{label} has a closed schema; missing={sorted(expected - actual)}, "
            f"unknown={sorted(actual - expected)}"
        )


def _plain_int(value: Any, label: str, minimum: int, maximum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not minimum <= value <= maximum:
        raise ClassicalError(f"{label} must be an integer from {minimum} through {maximum}")
    return value


def _finite(value: Any, label: str, minimum: float, maximum: float) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ClassicalError(f"{label} must be numeric")
    result = float(value)
    if not math.isfinite(result) or not minimum <= result <= maximum:
        raise ClassicalError(f"{label} must be finite from {minimum} through {maximum}")
    return result


def _parse_plan(value: Any) -> ClassicalPlan:
    if not isinstance(value, dict):
        raise ClassicalError("classical plan root must be an object")
    _exact_keys(value, PLAN_KEYS, "classical plan")
    if value["schema_version"] != SCHEMA_VERSION:
        raise ClassicalError(f"classical plan schema_version must be {SCHEMA_VERSION}")

    selection = value["selection"]
    if not isinstance(selection, dict):
        raise ClassicalError("plan.selection must be an object")
    _exact_keys(selection, {"source_ids"}, "plan.selection")
    source_ids = selection["source_ids"]
    if (
        not isinstance(source_ids, list)
        or not source_ids
        or any(not isinstance(item, str) or not item for item in source_ids)
        or source_ids != sorted(set(source_ids))
    ):
        raise ClassicalError("plan.selection.source_ids must be a sorted unique non-empty string array")

    tokenization = value["tokenization"]
    if not isinstance(tokenization, dict):
        raise ClassicalError("plan.tokenization must be an object")
    _exact_keys(
        tokenization,
        {"tokenizer", "stopwords", "min_token_length", "ngram_range"},
        "plan.tokenization",
    )
    if tokenization["tokenizer"] != TOKENIZER_ID or tokenization["stopwords"] != STOPWORDS_ID:
        raise ClassicalError("the portable plan requires the bundled tokenizer and stopword identities")
    _plain_int(tokenization["min_token_length"], "min_token_length", 1, 12)
    ngram_range = tokenization["ngram_range"]
    if ngram_range not in ([1, 1], [1, 2]):
        raise ClassicalError("plan.tokenization.ngram_range must be [1,1] or [1,2]")

    bm25 = value["bm25"]
    if not isinstance(bm25, dict):
        raise ClassicalError("plan.bm25 must be an object")
    _exact_keys(bm25, {"k1", "b", "title_weight", "body_weight"}, "plan.bm25")
    _finite(bm25["k1"], "plan.bm25.k1", 0.01, 10.0)
    _finite(bm25["b"], "plan.bm25.b", 0.0, 1.0)
    _finite(bm25["title_weight"], "plan.bm25.title_weight", 0.0, 100.0)
    _finite(bm25["body_weight"], "plan.bm25.body_weight", 0.0, 100.0)
    if float(bm25["title_weight"]) + float(bm25["body_weight"]) <= 0:
        raise ClassicalError("at least one BM25 field weight must be positive")

    associations = value["associations"]
    if not isinstance(associations, dict):
        raise ClassicalError("plan.associations must be an object")
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
    _plain_int(associations["min_document_frequency"], "min_document_frequency", 1, 1000000)
    _plain_int(associations["min_cooccurrence"], "min_cooccurrence", 1, 1000000)
    _plain_int(associations["max_vocabulary"], "max_vocabulary", 32, 50000)
    _plain_int(associations["max_neighbors"], "max_neighbors", 1, 128)
    _finite(associations["minimum_ppmi"], "minimum_ppmi", 0.0, 100.0)

    topics = value["topics"]
    if not isinstance(topics, dict):
        raise ClassicalError("plan.topics must be an object")
    _exact_keys(topics, {"topic_count", "max_iterations", "top_terms"}, "plan.topics")
    _plain_int(topics["topic_count"], "topic_count", 2, 128)
    _plain_int(topics["max_iterations"], "max_iterations", 1, 100)
    _plain_int(topics["top_terms"], "top_terms", 3, 100)

    expansion = value["expansion"]
    if not isinstance(expansion, dict):
        raise ClassicalError("plan.expansion must be an object")
    _exact_keys(
        expansion,
        {"association_terms", "topic_terms", "association_weight", "topic_weight"},
        "plan.expansion",
    )
    _plain_int(expansion["association_terms"], "association_terms", 0, 64)
    _plain_int(expansion["topic_terms"], "topic_terms", 0, 64)
    _finite(expansion["association_weight"], "association_weight", 0.0, 1.0)
    _finite(expansion["topic_weight"], "topic_weight", 0.0, 1.0)

    reranking = value["reranking"]
    if not isinstance(reranking, dict):
        raise ClassicalError("plan.reranking must be an object")
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
    _plain_int(reranking["candidate_pool"], "candidate_pool", 10, 10000)
    _plain_int(reranking["max_per_evidence_identity"], "max_per_evidence_identity", 1, 100)
    _plain_int(reranking["rrf_k"], "rrf_k", 1, 10000)
    weights = [
        _finite(reranking[name], f"plan.reranking.{name}", 0.0, 1.0)
        for name in ("relevance_weight", "topic_novelty_weight", "source_novelty_weight")
    ]
    if not math.isclose(sum(weights), 1.0, rel_tol=0.0, abs_tol=1e-9):
        raise ClassicalError("reranking relevance/topic/source weights must sum to 1")
    raw = json.loads(canonical_json(value))
    return ClassicalPlan(raw=raw, sha256=sha256_canonical(raw), source_ids=tuple(source_ids))


def load_plan(path: Path) -> ClassicalPlan:
    """Load and validate one closed classical-retrieval plan."""

    try:
        value = strict_json_loads(path.read_text(encoding="utf-8"), label=str(path))
    except (OSError, UnicodeError) as exc:
        raise ClassicalError(f"cannot read classical plan at {path}: {exc}") from exc
    return _parse_plan(value)


def _safe_relative(value: str, label: str) -> PurePosixPath:
    candidate = PurePosixPath(value.replace("\\", "/"))
    if candidate.is_absolute() or not candidate.parts or any(part in {"", ".", ".."} for part in candidate.parts):
        raise ClassicalError(f"{label} is not a safe relative path: {value!r}")
    return candidate


def _read_jsonl(path: Path, *, label: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        raise ClassicalError(f"cannot read {label}: {exc}") from exc
    for number, line in enumerate(lines, start=1):
        if not line:
            raise ClassicalError(f"{label}:{number} is blank")
        value = strict_json_loads(line, label=f"{label}:{number}")
        if not isinstance(value, dict):
            raise ClassicalError(f"{label}:{number} must be an object")
        rows.append(value)
    return rows


def _write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def _write_jsonl(path: Path, rows: Iterable[Mapping[str, Any]]) -> None:
    path.write_text(
        "".join(canonical_json(dict(row)) + "\n" for row in rows),
        encoding="utf-8",
    )


def _core_inventory(root: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        relative = path.relative_to(root)
        if relative.parts and relative.parts[0] == "classical":
            continue
        rows.append({"path": relative.as_posix(), "sha256": sha256_file(path)})
    return rows


def _core_tree_sha256(root: Path) -> str:
    return sha256_canonical(_core_inventory(root))


def _load_core(root: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    records = _read_jsonl(root / "semantic" / "records.jsonl", label="semantic/records.jsonl")
    try:
        source_manifest = strict_json_loads(
            (root / "semantic" / "source-manifest.json").read_text(encoding="utf-8"),
            label="semantic/source-manifest.json",
        )
    except (OSError, UnicodeError) as exc:
        raise ClassicalError(f"cannot read semantic/source-manifest.json: {exc}") from exc
    sources = source_manifest.get("sources") if isinstance(source_manifest, dict) else None
    if not isinstance(sources, list) or any(not isinstance(item, dict) for item in sources):
        raise ClassicalError("semantic/source-manifest.json must contain an object source array")
    return records, sources


def _selection(
    records: Sequence[dict[str, Any]], sources: Sequence[dict[str, Any]], plan: ClassicalPlan
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    source_by_id = {
        str(source["id"]): source
        for source in sources
        if isinstance(source.get("id"), str) and source["id"]
    }
    missing = sorted(set(plan.source_ids) - set(source_by_id))
    if missing:
        raise ClassicalError(f"classical plan selects unknown source IDs: {missing}")
    selected = [record for record in records if record.get("source_id") in set(plan.source_ids)]
    eligible = sorted({str(record.get("source_id")) for record in selected})
    if eligible != list(plan.source_ids):
        absent = sorted(set(plan.source_ids) - set(eligible))
        raise ClassicalError(f"selected source IDs produced no eligible records: {absent}")
    inventory = [
        {"source_id": source_id, "content_sha256": source_by_id[source_id].get("content_sha256")}
        for source_id in eligible
    ]
    if any(not HEX_64.fullmatch(str(row["content_sha256"])) for row in inventory):
        raise ClassicalError("selected source inventory contains an invalid content digest")
    selection = {
        "requested_source_ids": list(plan.source_ids),
        "eligible_source_ids": eligible,
        "excluded_source_ids": sorted(set(source_by_id) - set(plan.source_ids)),
        "input_count": len(inventory),
        "input_sha256": sha256_canonical(inventory),
    }
    return sorted(selected, key=lambda row: (str(row.get("source_id")), str(row.get("record_id")))), selection


def _unigrams(value: str, plan: ClassicalPlan) -> list[str]:
    minimum = int(plan.raw["tokenization"]["min_token_length"])
    return [
        token
        for token in TOKEN_RE.findall(value.casefold())
        if len(token) >= minimum and token not in STOPWORDS
    ]


def tokenize(value: str, plan: ClassicalPlan) -> list[str]:
    """Tokenize text into the plan's deterministic bag-of-words features."""

    words = _unigrams(value, plan)
    if plan.raw["tokenization"]["ngram_range"] == [1, 1]:
        return words
    return [*words, *(f"{left} {right}" for left, right in zip(words, words[1:]))]


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


def _counter_object(tokens: Sequence[str]) -> dict[str, int]:
    return dict(sorted(Counter(tokens).items()))


def _derive_documents(records: Sequence[dict[str, Any]], plan: ClassicalPlan) -> list[dict[str, Any]]:
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
            raise ClassicalError("selected authoritative record has an invalid required identity or body")
        concept_path = str(record["concept_path"]).replace("\\", "/")
        safe = _safe_relative(concept_path, "record concept_path")
        if safe.parts[0] != "concepts":
            raise ClassicalError(f"record concept_path is outside concepts/: {concept_path}")
        body = str(record["body"])
        ranges = _passage_ranges(record)
        if not ranges:
            raise ClassicalError(f"record {record['source_id']}/{record['record_id']} has no indexable text")
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


def _derive_lexicon(documents: Sequence[dict[str, Any]], plan: ClassicalPlan) -> dict[str, Any]:
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
        idf = math.log(1.0 + (count - df + 0.5) / (df + 0.5))
        terms.append(
            {
                "term": term,
                "document_frequency": df,
                "corpus_frequency": corpus_frequency[term],
                "idf": round(idf, 10),
            }
        )
    return {
        "schema_version": SCHEMA_VERSION,
        "tokenization": plan.raw["tokenization"],
        "bm25": plan.raw["bm25"],
        "document_count": count,
        "average_field_lengths": {
            "title": round(sum(row["title_length"] for row in documents) / count, 10),
            "body": round(sum(row["body_length"] for row in documents) / count, 10),
        },
        "terms": terms,
    }


def _derive_associations(
    documents: Sequence[dict[str, Any]], lexicon: Mapping[str, Any], plan: ClassicalPlan
) -> list[dict[str, Any]]:
    config = plan.raw["associations"]
    candidates = [
        row
        for row in lexicon["terms"]
        if " " not in row["term"] and row["document_frequency"] >= config["min_document_frequency"]
    ]
    candidates.sort(key=lambda row: (-row["document_frequency"], -row["corpus_frequency"], row["term"]))
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
    associations: Sequence[dict[str, Any]], lexicon: Mapping[str, Any], plan: ClassicalPlan
) -> dict[str, Any]:
    graph = _association_graph(associations)
    stats = {row["term"]: row for row in lexicon["terms"]}
    terms = sorted(graph)
    requested = min(plan.raw["topics"]["topic_count"], len(terms))
    if requested < 2:
        raise ClassicalError("association vocabulary is too small to derive at least two topics")
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
            score = (centrality[term] + math.log1p(stats[term]["corpus_frequency"])) / (1.0 + 8.0 * maximum)
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
    for iterations in range(1, plan.raw["topics"]["max_iterations"] + 1):
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
            best_labels = sorted(label for label, score in scores.items() if math.isclose(score, best_score, abs_tol=1e-12))
            selected = labels[term] if labels[term] in best_labels else best_labels[0]
            if selected != labels[term]:
                labels[term] = selected
                changed += 1
        if changed == 0:
            break

    topics: list[dict[str, Any]] = []
    top_terms = plan.raw["topics"]["top_terms"]
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
                            math.log1p(stats[term]["corpus_frequency"]) * (1.0 + centrality[term]),
                            8,
                        ),
                    }
                    for term in ranked_members[:top_terms]
                ],
            }
        )
    return {
        "schema_version": SCHEMA_VERSION,
        "algorithm": "deterministic-seeded-weighted-label-propagation-v1",
        "requested_topic_count": plan.raw["topics"]["topic_count"],
        "topic_count": len(topics),
        "iterations": iterations,
        "term_topics": [
            {"term": term, "topic_id": f"topic-{labels[term]:02d}"}
            for term in sorted(labels)
        ],
        "topics": topics,
    }


def _add_topic_weights(
    documents: list[dict[str, Any]], lexicon: Mapping[str, Any], topics: Mapping[str, Any]
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
    records: Sequence[dict[str, Any]], plan: ClassicalPlan
) -> tuple[list[dict[str, Any]], dict[str, Any], list[dict[str, Any]], dict[str, Any]]:
    documents = _derive_documents(records, plan)
    lexicon = _derive_lexicon(documents, plan)
    associations = _derive_associations(documents, lexicon, plan)
    topics = _derive_topics(associations, lexicon, plan)
    _add_topic_weights(documents, lexicon, topics)
    return documents, lexicon, associations, topics


def _artifact(root: Path, relative: str, count: int | None = None) -> dict[str, Any]:
    path = root / relative
    result: dict[str, Any] = {
        "path": relative,
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }
    if count is not None:
        result["count"] = count
    return result


def _summary(
    selection: Mapping[str, Any], records: Sequence[dict[str, Any]], documents: Sequence[dict[str, Any]],
    lexicon: Mapping[str, Any], associations: Sequence[dict[str, Any]], topics: Mapping[str, Any]
) -> dict[str, Any]:
    return {
        "inputs": selection["input_count"],
        "records": len(records),
        "documents": len(documents),
        "terms": len(lexicon["terms"]),
        "association_terms": len(associations),
        "topics": topics["topic_count"],
    }


def build_projection(root: Path, plan_path: Path) -> dict[str, Any]:
    """Add a complete classical projection to an already validated core snapshot."""

    plan = load_plan(plan_path)
    records, sources = _load_core(root)
    selected, selection = _selection(records, sources, plan)
    documents, lexicon, associations, topics = _derive_all(selected, plan)
    classical = root / "classical"
    if classical.exists() or classical.is_symlink():
        raise ClassicalError("core candidate unexpectedly contains classical artifacts")
    classical.mkdir()
    _write_jsonl(classical / "documents.jsonl", documents)
    _write_json(classical / "lexicon.json", lexicon)
    _write_jsonl(classical / "associations.jsonl", associations)
    _write_json(classical / "topics.json", topics)
    core = {
        "tree_sha256": _core_tree_sha256(root),
        "records_sha256": sha256_file(root / "semantic" / "records.jsonl"),
        "record_count": len(records),
    }
    artifacts = {
        "documents": _artifact(root, ARTIFACT_NAMES["documents"], len(documents)),
        "lexicon": _artifact(root, ARTIFACT_NAMES["lexicon"], len(lexicon["terms"])),
        "associations": _artifact(root, ARTIFACT_NAMES["associations"], len(associations)),
        "topics": _artifact(root, ARTIFACT_NAMES["topics"], topics["topic_count"]),
    }
    summary = _summary(selection, selected, documents, lexicon, associations, topics)
    index = {
        "schema_version": SCHEMA_VERSION,
        "authoritative": False,
        "core": core,
        "classical_plan_sha256": plan.sha256,
        "plan": plan.raw,
        "selection": selection,
        "algorithms": ALGORITHMS,
        "artifacts": artifacts,
        "summary": summary,
    }
    _write_json(classical / "index.json", index)
    initial = validate_classical_bundle(root, require_build_report=False)
    if not initial["valid"]:
        raise ClassicalError(initial["errors"][0]["message"])
    report = {
        "schema_version": SCHEMA_VERSION,
        "valid": True,
        "status": "pass",
        "errors": [],
        "warnings": [],
        "classical_plan_sha256": plan.sha256,
        "core": core,
        "selection": selection,
        "summary": summary,
        "artifacts": {"index": _artifact(root, "classical/index.json"), **artifacts},
    }
    _write_json(classical / "build-report.json", report)
    final = validate_classical_bundle(root)
    if not final["valid"]:
        raise ClassicalError(final["errors"][0]["message"])
    return report


def _load_json(path: Path, label: str) -> Any:
    try:
        return strict_json_loads(path.read_text(encoding="utf-8"), label=label)
    except (OSError, UnicodeError) as exc:
        raise ClassicalError(f"cannot read {label}: {exc}") from exc


def _validate_or_raise(root: Path, *, require_build_report: bool) -> dict[str, Any]:
    if not root.is_dir():
        raise ClassicalError(f"bundle does not exist or is not a directory: {root}")
    core_result = validate_semantic_bundle(root)
    if not core_result.valid:
        detail = "; ".join(error.get("message", "core error") for error in core_result.errors[:3])
        raise ClassicalError(f"authoritative Semantic OKF core is invalid: {detail}")
    classical = root / "classical"
    expected = {"index.json", "documents.jsonl", "lexicon.json", "associations.jsonl", "topics.json"}
    if require_build_report:
        expected.add("build-report.json")
    if not classical.is_dir() or classical.is_symlink():
        raise ClassicalError("classical must be a real directory")
    actual = {path.name for path in classical.iterdir()}
    if actual != expected:
        raise ClassicalError(
            f"classical artifact set is closed; missing={sorted(expected - actual)}, unknown={sorted(actual - expected)}"
        )
    if any(path.is_symlink() or not path.is_file() for path in classical.iterdir()):
        raise ClassicalError("classical artifacts must be regular files")
    index = _load_json(classical / "index.json", "classical/index.json")
    if not isinstance(index, dict):
        raise ClassicalError("classical/index.json root must be an object")
    _exact_keys(
        index,
        {"schema_version", "authoritative", "core", "classical_plan_sha256", "plan", "selection", "algorithms", "artifacts", "summary"},
        "classical index",
    )
    if index["schema_version"] != SCHEMA_VERSION or index["authoritative"] is not False:
        raise ClassicalError("classical index version or authority marker is invalid")
    if index["algorithms"] != ALGORITHMS:
        raise ClassicalError("classical index algorithm identities are invalid")
    plan = _parse_plan(index["plan"])
    if index["classical_plan_sha256"] != plan.sha256:
        raise ClassicalError("classical plan digest is invalid")
    records, sources = _load_core(root)
    selected, selection = _selection(records, sources, plan)
    core = {
        "tree_sha256": _core_tree_sha256(root),
        "records_sha256": sha256_file(root / "semantic" / "records.jsonl"),
        "record_count": len(records),
    }
    if index["core"] != core:
        raise ClassicalError("classical index core binding is stale or invalid")
    if index["selection"] != selection:
        raise ClassicalError("classical index source selection binding is invalid")
    documents = _read_jsonl(classical / "documents.jsonl", label="classical/documents.jsonl")
    lexicon = _load_json(classical / "lexicon.json", "classical/lexicon.json")
    associations = _read_jsonl(classical / "associations.jsonl", label="classical/associations.jsonl")
    topics = _load_json(classical / "topics.json", "classical/topics.json")
    expected_documents, expected_lexicon, expected_associations, expected_topics = _derive_all(selected, plan)
    if documents != expected_documents:
        raise ClassicalError("classical documents differ from deterministic authoritative derivation")
    if lexicon != expected_lexicon:
        raise ClassicalError("classical lexicon differs from deterministic document statistics")
    if associations != expected_associations:
        raise ClassicalError("classical associations differ from deterministic PPMI derivation")
    if topics != expected_topics:
        raise ClassicalError("classical topics differ from deterministic term-community derivation")
    for number, document in enumerate(documents, start=1):
        _exact_keys(document, DOCUMENT_KEYS, f"classical/documents.jsonl:{number}")
    artifacts = {
        "documents": _artifact(root, ARTIFACT_NAMES["documents"], len(documents)),
        "lexicon": _artifact(root, ARTIFACT_NAMES["lexicon"], len(lexicon["terms"])),
        "associations": _artifact(root, ARTIFACT_NAMES["associations"], len(associations)),
        "topics": _artifact(root, ARTIFACT_NAMES["topics"], topics["topic_count"]),
    }
    if index["artifacts"] != artifacts:
        raise ClassicalError("classical index artifact hashes, sizes, or counts are invalid")
    summary = _summary(selection, selected, documents, lexicon, associations, topics)
    if index["summary"] != summary:
        raise ClassicalError("classical index summary is invalid")
    expected_report = {
        "schema_version": SCHEMA_VERSION,
        "valid": True,
        "status": "pass",
        "errors": [],
        "warnings": [],
        "classical_plan_sha256": plan.sha256,
        "core": core,
        "selection": selection,
        "summary": summary,
        "artifacts": {"index": _artifact(root, "classical/index.json"), **artifacts},
    }
    if require_build_report:
        report = _load_json(classical / "build-report.json", "classical/build-report.json")
        if report != expected_report:
            raise ClassicalError("classical build report differs from live validation")
    return {
        "schema_version": SCHEMA_VERSION,
        "valid": True,
        "status": "pass",
        "errors": [],
        "warnings": [],
        "summary": summary,
    }


def validate_classical_bundle(root: Path, *, require_build_report: bool = True) -> dict[str, Any]:
    """Validate the authoritative core plus every classical retrieval binding."""

    try:
        return _validate_or_raise(root.resolve(), require_build_report=require_build_report)
    except (
        ClassicalError,
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
            "errors": [{"code": "classical-error", "path": "classical", "message": str(exc)}],
            "warnings": [],
            "summary": {},
        }


def atomic_build(
    manifest_path: Path,
    plan_path: Path,
    output: Path,
    core_builder: Any,
) -> dict[str, Any]:
    """Build core and classical layers in a sibling candidate, then publish once."""

    output = output.resolve()
    if output.exists() or output.is_symlink():
        raise ClassicalError(f"output already exists: {output}")
    load_plan(plan_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    candidate = Path(tempfile.mkdtemp(prefix=f".{output.name}.classical-candidate-", dir=output.parent))
    candidate.rmdir()
    try:
        core_builder(manifest_path, candidate)
        build_projection(candidate, plan_path)
        os.replace(candidate, output)
    except Exception:
        if candidate.exists():
            shutil.rmtree(candidate, ignore_errors=True)
        raise
    return _load_json(output / "classical" / "build-report.json", "classical/build-report.json")
