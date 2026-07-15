#!/usr/bin/env python3
"""Validate and query a classical Semantic OKF projection without writing it."""

from __future__ import annotations

import hashlib
import json
import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Mapping, Sequence


SCHEMA_VERSION = "1.0"
TOKENIZER_ID = "ascii-alphanumeric-v1"
STOPWORDS_ID = "english-v1"
TOKEN_RE = re.compile(r"[a-z0-9]+", re.IGNORECASE)
PAGE_RE = re.compile(r"(?m)^## PDF page \d+\s*$")
PAPER_RE = re.compile(r"(?<!\d)(\d{4})[.-](\d{5}v\d+)(?!\d)", re.IGNORECASE)
HEX_64 = re.compile(r"[0-9a-f]{64}")
DOCUMENT_ID_RE = re.compile(r"document-[0-9a-f]{32}")
ALGORITHMS = {
    "bm25": "okapi-bm25f-v1",
    "associations": "windowed-positive-pmi-v1",
    "topics": "deterministic-seeded-weighted-label-propagation-v1",
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
    """Describe an invalid snapshot, filter, or classical search request."""


@dataclass(frozen=True)
class ClassicalSnapshot:
    """Hold one fully validated in-memory classical retrieval snapshot."""

    root: Path
    index: dict[str, Any]
    documents: tuple[dict[str, Any], ...]
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
        if relative.parts and relative.parts[0] == "classical":
            continue
        rows.append({"path": relative.as_posix(), "sha256": sha256_file(path)})
    return rows


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
        raise SnapshotError("plan.selection.source_ids must be sorted, unique, and nonempty")
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
        ranges = _passage_ranges(record)
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
        _exact_keys(document, DOCUMENT_KEYS, f"classical/documents.jsonl:{number}")
        if not isinstance(document["document_id"], str) or not DOCUMENT_ID_RE.fullmatch(document["document_id"]):
            raise SnapshotError(f"classical/documents.jsonl:{number} has an invalid document ID")
        if document["document_id"] != _document_id(document):
            raise SnapshotError(f"classical/documents.jsonl:{number} has a stale document ID")
        ids.append(document["document_id"])
        record = record_by_key.get((document["source_id"], document["record_id"]))
        if record is None:
            raise SnapshotError(f"classical/documents.jsonl:{number} is orphaned from the ledger")
        for field in (
            "record_sha256",
            "concept_id",
            "concept_type",
            "concept_path",
            "source_path",
            "title",
        ):
            if document[field] != record.get(field):
                raise SnapshotError(f"classical/documents.jsonl:{number} {field} differs from its record")
        if document["paper_id"] != _paper_id(record):
            raise SnapshotError(f"classical/documents.jsonl:{number} paper identity differs from its record")
        if isinstance(document["ordinal"], bool) or not isinstance(document["ordinal"], int) or document["ordinal"] < 0:
            raise SnapshotError(f"classical/documents.jsonl:{number} has an invalid ordinal")
        concept = _safe_relative(document["concept_path"], "document concept_path")
        if concept.parts[0] != "concepts":
            raise SnapshotError("document concept path is outside concepts/")
        concept_file = root.joinpath(*concept.parts)
        if not concept_file.is_file() or concept_file.is_symlink():
            raise SnapshotError(f"document concept file is missing or unsafe: {document['concept_path']}")
        text = document["text"]
        if not isinstance(text, str) or not text or document["text_sha256"] != sha256_bytes(text.encode("utf-8")):
            raise SnapshotError(f"classical/documents.jsonl:{number} has invalid text or text hash")
        body = record.get("body")
        locator = document["locator"]
        if locator == {"kind": "record"}:
            if text != body:
                raise SnapshotError(f"classical/documents.jsonl:{number} record locator does not resolve")
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
                raise SnapshotError(f"classical/documents.jsonl:{number} character locator does not resolve")
        else:
            raise SnapshotError(f"classical/documents.jsonl:{number} has an invalid locator")
        expected_title = _counter_object(tokenize(document["title"], plan))
        expected_body = _counter_object(tokenize(text, plan))
        if document["title_terms"] != expected_title or document["body_terms"] != expected_body:
            raise SnapshotError(f"classical/documents.jsonl:{number} token counts do not match text")
        if document["title_length"] != sum(expected_title.values()) or document["body_length"] != sum(expected_body.values()):
            raise SnapshotError(f"classical/documents.jsonl:{number} field lengths are invalid")
        seen_topics: set[str] = set()
        for item in document["topic_weights"]:
            if not isinstance(item, dict) or set(item) != {"topic_id", "weight"}:
                raise SnapshotError(f"classical/documents.jsonl:{number} has invalid topic weights")
            if item["topic_id"] not in topic_ids or item["topic_id"] in seen_topics:
                raise SnapshotError(f"classical/documents.jsonl:{number} has an unknown or duplicate topic")
            if isinstance(item["weight"], bool) or not isinstance(item["weight"], (int, float)) or not 0 < float(item["weight"]) <= 1:
                raise SnapshotError(f"classical/documents.jsonl:{number} has an invalid topic weight")
            seen_topics.add(item["topic_id"])
        if document["topic_weights"] != sorted(document["topic_weights"], key=lambda item: item["topic_id"]):
            raise SnapshotError(f"classical/documents.jsonl:{number} topic weights are not ordered")
        combined = Counter(expected_title) + Counter(expected_body)
        expected_topics = {term_topics[term] for term in combined if term in term_topics}
        if expected_topics and not seen_topics:
            raise SnapshotError(f"classical/documents.jsonl:{number} is missing derived topic weights")
    if ids != sorted(ids) or len(ids) != len(set(ids)):
        raise SnapshotError("classical documents must be uniquely ordered by document ID")


def _validate_associations(
    associations: Sequence[dict[str, Any]], lexicon: Mapping[str, Any], plan: Mapping[str, Any]
) -> None:
    term_stats = {row["term"]: row for row in lexicon["terms"]}
    terms: list[str] = []
    maximum = int(plan["associations"]["max_neighbors"])
    for number, row in enumerate(associations, start=1):
        if not isinstance(row, dict) or set(row) != {"term", "document_frequency", "corpus_frequency", "neighbors"}:
            raise SnapshotError(f"classical/associations.jsonl:{number} has an invalid shape")
        term = row["term"]
        if term not in term_stats or " " in term:
            raise SnapshotError(f"classical/associations.jsonl:{number} has an unknown term")
        if row["document_frequency"] != term_stats[term]["document_frequency"] or row["corpus_frequency"] != term_stats[term]["corpus_frequency"]:
            raise SnapshotError(f"classical/associations.jsonl:{number} statistics differ from the lexicon")
        if not isinstance(row["neighbors"], list) or len(row["neighbors"]) > maximum:
            raise SnapshotError(f"classical/associations.jsonl:{number} has an invalid neighbor array")
        previous: tuple[float, int, str] | None = None
        neighbor_terms: set[str] = set()
        for neighbor in row["neighbors"]:
            if not isinstance(neighbor, dict) or set(neighbor) != {"term", "cooccurrence", "ppmi"}:
                raise SnapshotError(f"classical/associations.jsonl:{number} has an invalid neighbor")
            if neighbor["term"] not in term_stats or neighbor["term"] == term or neighbor["term"] in neighbor_terms:
                raise SnapshotError(f"classical/associations.jsonl:{number} has an unknown or duplicate neighbor")
            if isinstance(neighbor["cooccurrence"], bool) or not isinstance(neighbor["cooccurrence"], int) or neighbor["cooccurrence"] < 1:
                raise SnapshotError(f"classical/associations.jsonl:{number} has an invalid cooccurrence")
            if isinstance(neighbor["ppmi"], bool) or not isinstance(neighbor["ppmi"], (int, float)) or not math.isfinite(float(neighbor["ppmi"])) or float(neighbor["ppmi"]) <= 0:
                raise SnapshotError(f"classical/associations.jsonl:{number} has an invalid PPMI")
            ordering = (-float(neighbor["ppmi"]), -neighbor["cooccurrence"], neighbor["term"])
            if previous is not None and ordering < previous:
                raise SnapshotError(f"classical/associations.jsonl:{number} neighbors are not ordered")
            previous = ordering
            neighbor_terms.add(neighbor["term"])
        terms.append(term)
    if terms != sorted(terms) or len(terms) != len(set(terms)):
        raise SnapshotError("association terms must be uniquely ordered")


def _validate_topics(topics: Any, associations: Sequence[dict[str, Any]], plan: Mapping[str, Any]) -> None:
    if not isinstance(topics, dict):
        raise SnapshotError("classical/topics.json root must be an object")
    _exact_keys(
        topics,
        {"schema_version", "algorithm", "requested_topic_count", "topic_count", "iterations", "term_topics", "topics"},
        "classical topics",
    )
    if topics["schema_version"] != SCHEMA_VERSION or topics["algorithm"] != ALGORITHMS["topics"]:
        raise SnapshotError("classical topic algorithm identity is invalid")
    if topics["requested_topic_count"] != plan["topics"]["topic_count"]:
        raise SnapshotError("requested topic count differs from the plan")
    if not isinstance(topics["topics"], list) or topics["topic_count"] != len(topics["topics"]):
        raise SnapshotError("topic count is invalid")
    topic_ids = [row.get("topic_id") for row in topics["topics"] if isinstance(row, dict)]
    if len(topic_ids) != len(topics["topics"]) or topic_ids != [f"topic-{index:02d}" for index in range(len(topic_ids))]:
        raise SnapshotError("topic IDs are invalid or unordered")
    association_terms = {row["term"] for row in associations}
    mapped_terms = [row.get("term") for row in topics["term_topics"] if isinstance(row, dict)]
    if mapped_terms != sorted(association_terms):
        raise SnapshotError("topic term mapping does not cover the association vocabulary exactly")
    if any(row.get("topic_id") not in set(topic_ids) for row in topics["term_topics"]):
        raise SnapshotError("topic term mapping names an unknown topic")
    for row in topics["topics"]:
        if set(row) != {"topic_id", "seed", "term_count", "terms"} or row["seed"] not in association_terms:
            raise SnapshotError("topic row has an invalid shape or seed")
        if not isinstance(row["terms"], list) or len(row["terms"]) > plan["topics"]["top_terms"]:
            raise SnapshotError("topic top-term array is invalid")
        if any(not isinstance(item, dict) or set(item) != {"term", "weight"} or item["term"] not in association_terms for item in row["terms"]):
            raise SnapshotError("topic contains an invalid top term")


def load_snapshot(root: Path, *, deep_validation: bool = False) -> ClassicalSnapshot:
    """Load one snapshot read-only, optionally rederiving every classical artifact."""

    root = root.expanduser().resolve()
    if not root.is_dir():
        raise SnapshotError(f"bundle does not exist or is not a directory: {root}")
    classical = root / "classical"
    expected_names = {"index.json", "documents.jsonl", "lexicon.json", "associations.jsonl", "topics.json", "build-report.json"}
    if not classical.is_dir() or classical.is_symlink():
        raise SnapshotError("classical must be a real directory")
    actual_names = {path.name for path in classical.iterdir()}
    if actual_names != expected_names:
        raise SnapshotError(
            f"classical artifact set is closed; missing={sorted(expected_names - actual_names)}, unknown={sorted(actual_names - expected_names)}"
        )
    if any(path.is_symlink() or not path.is_file() for path in classical.iterdir()):
        raise SnapshotError("classical artifacts must be regular files")
    semantic_report = _load_json(root / "semantic" / "build-report.json", "semantic/build-report.json")
    if not isinstance(semantic_report, dict) or semantic_report.get("status") != "pass":
        raise SnapshotError("authoritative Semantic OKF build report is not passing")
    index = _load_json(classical / "index.json", "classical/index.json")
    if not isinstance(index, dict):
        raise SnapshotError("classical/index.json root must be an object")
    _exact_keys(
        index,
        {"schema_version", "authoritative", "core", "classical_plan_sha256", "plan", "selection", "algorithms", "artifacts", "summary"},
        "classical index",
    )
    if index["schema_version"] != SCHEMA_VERSION or index["authoritative"] is not False:
        raise SnapshotError("classical index version or authority marker is invalid")
    if index["algorithms"] != ALGORITHMS:
        raise SnapshotError("classical algorithm identities are invalid")
    plan = _validate_plan(index["plan"])
    if index["classical_plan_sha256"] != sha256_canonical(plan):
        raise SnapshotError("classical plan digest is invalid")
    records = _read_jsonl(root / "semantic" / "records.jsonl", "semantic/records.jsonl")
    source_manifest = _load_json(
        root / "semantic" / "source-manifest.json", "semantic/source-manifest.json"
    )
    sources = source_manifest.get("sources") if isinstance(source_manifest, dict) else None
    if not isinstance(sources, list) or any(not isinstance(item, dict) for item in sources):
        raise SnapshotError("semantic/source-manifest.json must contain an object source array")
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
    associations = _read_jsonl(classical / "associations.jsonl", "classical/associations.jsonl")
    topics = _load_json(classical / "topics.json", "classical/topics.json")
    _validate_topics(topics, associations, plan)
    _validate_documents(root, documents, records, plan, topics)
    if lexicon != _derive_lexicon(documents, plan):
        raise SnapshotError("classical lexicon differs from live document statistics")
    _validate_associations(associations, lexicon, plan)
    if deep_validation:
        expected_documents, expected_lexicon, expected_associations, expected_topics = _derive_all(
            selected_records, plan
        )
        if documents != expected_documents:
            raise SnapshotError("classical documents differ from authoritative deterministic derivation")
        if lexicon != expected_lexicon:
            raise SnapshotError("classical lexicon differs from authoritative deterministic derivation")
        if associations != expected_associations:
            raise SnapshotError("classical associations differ from independent deterministic PPMI derivation")
        if topics != expected_topics:
            raise SnapshotError("classical topics differ from independent deterministic topic derivation")
    artifacts = {
        "documents": _artifact(classical / "documents.jsonl", "classical/documents.jsonl", len(documents)),
        "lexicon": _artifact(classical / "lexicon.json", "classical/lexicon.json", len(lexicon["terms"])),
        "associations": _artifact(classical / "associations.jsonl", "classical/associations.jsonl", len(associations)),
        "topics": _artifact(classical / "topics.json", "classical/topics.json", topics["topic_count"]),
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
        "summary": summary,
        "artifacts": {"index": _artifact(classical / "index.json", "classical/index.json"), **artifacts},
    }
    if _load_json(classical / "build-report.json", "classical/build-report.json") != expected_report:
        raise SnapshotError("classical build report differs from live validation")
    return ClassicalSnapshot(
        root=root,
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
        "summary": snapshot.index["summary"],
        "capabilities": ["bm25", "topic", "association", "fusion"],
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
    query: str, snapshot: ClassicalSnapshot
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
    snapshot: ClassicalSnapshot,
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
                (_cosine(vector, _topic_vector(by_id[item]["topic_weights"])) for item in selected),
                default=0.0,
            )
            source_novelty = 1.0 if (
                document["source_id"] not in selected_sources and evidence_identity not in selected_papers
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
        evidence_identity = by_id[chosen].get("paper_id") or by_id[chosen]["source_id"]
        selected_papers.add(evidence_identity)
        identity_counts[evidence_identity] += 1
    return [by_id[identifier] for identifier in selected]


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
    """Search one validated snapshot with BM25, topic, association, or fusion ranking."""

    if mode not in {"bm25", "topic", "association", "fusion"}:
        raise SnapshotError("mode must be bm25, topic, association, or fusion")
    if not isinstance(query, str) or not query.strip():
        raise SnapshotError("query must be nonempty")
    if isinstance(top_k, bool) or not isinstance(top_k, int) or not 1 <= top_k <= 1000:
        raise SnapshotError("top-k must be an integer from 1 through 1000")
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
            "classical_index_sha256": snapshot.index_sha256,
            "classical_plan_sha256": snapshot.index["classical_plan_sha256"],
            "deep_validation": snapshot.deep_validation,
        },
        "results": results,
    }
