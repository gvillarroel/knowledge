#!/usr/bin/env python3
"""Verify and search an immutable expert with trace/classical hybrid fusion."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path, PurePosixPath
import re
import sys
from typing import Any, Iterable, Iterator, Mapping, Sequence


SKILL_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = SKILL_ROOT / "expert-manifest.json"
KNOWLEDGE_ROOT = SKILL_ROOT / "references" / "knowledge"
LEDGER_PATH = KNOWLEDGE_ROOT / "semantic" / "records.jsonl"
CLASSICAL_ROOT = KNOWLEDGE_ROOT / "classical"
TOKEN_RE = re.compile(r"[\w-]+")
CLASSICAL_TOKEN_RE = re.compile(r"[a-z0-9]+", re.IGNORECASE)
FIELD_WEIGHTS = {"claims": 0.5, "paper": 1.0}
BM25_K1 = 5.0
BM25_B = 0.75
HYBRID_RRF_K = 60
TRACE_RRF_WEIGHT = 1.0
CLASSICAL_RRF_WEIGHT = 2.0
CLASSICAL_STOPWORDS = frozenset(
    "a about above after again against all am an and any are as at be because "
    "been before being below between both but by can could did do does doing "
    "down during each few for from further had has have having he her here hers "
    "herself him himself his how i if in into is it its itself just me more "
    "most my myself no nor not now of off on once only or other our ours "
    "ourselves out over own same she should so some such than that the their "
    "theirs them themselves then there these they this those through to too "
    "under until up very was we were what when where which while who whom why "
    "will with you your yours yourself yourselves".split()
)


class ExpertQueryError(ValueError):
    """Raised when the expert binding or query is invalid."""


def retrieval_contract() -> dict[str, Any]:
    """Describe the frozen retrieval adapter used by this expert."""

    return {
        "id": "trace-classical-hybrid-rrf-v3",
        "route_name": "specialized_expert_trace_classical_hybrid",
        "query_adapter": (
            "The complete question remains the anchor. Unicode word-and-hyphen "
            "tokens retain each exact hyphenated facet and add its component "
            "terms. The trace-derived paper/claims BM25 ranking is combined with "
            "the snapshot's immutable passage BM25, PPMI-association, and MALLET "
            "topic fusion through weighted reciprocal ranks. One exact ledger "
            "record is then returned per authoritative paper identity."
        ),
        "parameters": {
            "bm25_b": BM25_B,
            "bm25_k1": BM25_K1,
            "classical_rrf_weight": CLASSICAL_RRF_WEIGHT,
            "claims_weight": FIELD_WEIGHTS["claims"],
            "hybrid_rrf_k": HYBRID_RRF_K,
            "paper_weight": FIELD_WEIGHTS["paper"],
            "hyphen_policy": "retain-and-expand-components",
            "paper_duplicate_policy": "highest-contribution-record",
            "trace_rrf_weight": TRACE_RRF_WEIGHT,
        },
    }


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _tree_binding(root: Path) -> tuple[str, int]:
    if not root.is_dir():
        raise ExpertQueryError(f"Embedded knowledge is absent: {root}")
    paths: list[Path] = []
    for path in root.rglob("*"):
        if path.is_symlink():
            raise ExpertQueryError(f"Embedded knowledge contains a symlink: {path}")
        if path.is_file():
            paths.append(path)
    digest = hashlib.sha256()
    for path in sorted(paths, key=lambda item: item.relative_to(root).as_posix()):
        relative = path.relative_to(root).as_posix().encode("utf-8")
        data = path.read_bytes()
        digest.update(relative)
        digest.update(b"\0")
        digest.update(str(len(data)).encode("ascii"))
        digest.update(b"\0")
        digest.update(data)
        digest.update(b"\0")
    return digest.hexdigest(), len(paths)


def _load_manifest() -> dict[str, Any]:
    try:
        payload = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ExpertQueryError(f"Cannot read expert manifest: {exc}") from exc
    if not isinstance(payload, dict):
        raise ExpertQueryError("Expert manifest must be a JSON object")
    return payload


def verify() -> dict[str, Any]:
    """Verify the complete embedded knowledge and bound expert artifacts."""

    manifest = _load_manifest()
    if manifest.get("schema_version") != "semantic-okf-expert-skill/1.0":
        raise ExpertQueryError("Unsupported expert manifest schema")
    knowledge = manifest.get("knowledge")
    artifacts = manifest.get("artifacts")
    if not isinstance(knowledge, dict) or not isinstance(artifacts, dict):
        raise ExpertQueryError("Expert manifest lacks required bindings")
    expected_tree = knowledge.get("tree")
    if not isinstance(expected_tree, dict):
        raise ExpertQueryError("Expert manifest lacks a tree binding")
    tree_sha256, file_count = _tree_binding(KNOWLEDGE_ROOT)
    if tree_sha256 != expected_tree.get("sha256"):
        raise ExpertQueryError("Embedded knowledge tree digest drift")
    if file_count != expected_tree.get("file_count"):
        raise ExpertQueryError("Embedded knowledge file count drift")

    for key, fallback in (
        ("skill_md", "SKILL.md"),
        ("guidance", "references/guidance.md"),
        ("query_script", "scripts/query_expert_knowledge.py"),
        ("agents_metadata", "agents/openai.yaml"),
    ):
        binding = artifacts.get(key)
        if not isinstance(binding, dict):
            raise ExpertQueryError(f"Missing artifact binding: {key}")
        raw_path = binding.get("path", fallback)
        if not isinstance(raw_path, str):
            raise ExpertQueryError(f"Invalid artifact path: {key}")
        relative = PurePosixPath(raw_path)
        if relative.is_absolute() or ".." in relative.parts or "\\" in raw_path:
            raise ExpertQueryError(f"Unsafe artifact path: {raw_path}")
        path = SKILL_ROOT.joinpath(*relative.parts)
        if not path.is_file() or _sha256_file(path) != binding.get("sha256"):
            raise ExpertQueryError(f"Artifact digest drift: {key}")
    return {
        "status": "pass",
        "skill_name": manifest.get("skill_name"),
        "knowledge_tree_sha256": tree_sha256,
        "knowledge_file_count": file_count,
        "record_count": knowledge.get("record_count"),
        "retrieval": retrieval_contract(),
    }


def _records() -> Iterator[dict[str, Any]]:
    try:
        lines = LEDGER_PATH.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        raise ExpertQueryError(f"Cannot read embedded record ledger: {exc}") from exc
    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ExpertQueryError(
                f"Invalid ledger JSON on line {line_number}: {exc}"
            ) from exc
        if not isinstance(record, dict):
            raise ExpertQueryError(f"Ledger line {line_number} is not an object")
        yield record


def _safe_concept_path(record: dict[str, Any]) -> str:
    raw = record.get("concept_path")
    if not isinstance(raw, str):
        raise ExpertQueryError("Ledger record lacks concept_path")
    relative = PurePosixPath(raw)
    if relative.is_absolute() or ".." in relative.parts or "\\" in raw:
        raise ExpertQueryError(f"Unsafe concept_path: {raw}")
    target = KNOWLEDGE_ROOT.joinpath(*relative.parts)
    if not target.is_file():
        raise ExpertQueryError(f"Concept is absent: {raw}")
    return raw


def _project(
    record: dict[str, Any],
    *,
    show_content: bool,
    score: float | None,
) -> dict[str, Any]:
    result = {
        "source_id": record.get("source_id"),
        "record_id": record.get("record_id"),
        "title": record.get("title"),
        "concept_type": record.get("concept_type"),
        "concept_id": record.get("concept_id"),
        "concept_path": _safe_concept_path(record),
        "record_sha256": record.get("record_sha256"),
        "source_path": record.get("source_path"),
    }
    if score is not None:
        result["score"] = score
    if show_content:
        body = record.get("body")
        result["body"] = body
        if isinstance(body, str):
            result["text"] = body
            result["text_sha256"] = hashlib.sha256(body.encode("utf-8")).hexdigest()
            result["locator"] = {"kind": "record"}
    return result


def _tokens(text: str) -> list[str]:
    tokens: list[str] = []
    for token in TOKEN_RE.findall(text.casefold()):
        tokens.append(token)
        if "-" in token:
            tokens.extend(part for part in token.split("-") if part)
    return tokens


def _record_text(record: dict[str, Any]) -> str:
    return " ".join(
        str(record.get(key, ""))
        for key in ("title", "body", "source_id", "record_id", "concept_type")
    )


def _field(record: dict[str, Any]) -> str:
    source_id = str(record.get("source_id", ""))
    if source_id.startswith("claims-"):
        return "claims"
    return "paper"


def _paper_group(record: dict[str, Any]) -> str:
    source_id = str(record.get("source_id", ""))
    for prefix in ("claims-", "paper-"):
        if source_id.startswith(prefix) and len(source_id) > len(prefix):
            return source_id[len(prefix) :]
    return f"{source_id}\0{record.get('record_id', '')}"


def _load_classical_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ExpertQueryError(f"Cannot read {label}: {exc}") from exc
    if not isinstance(value, dict):
        raise ExpertQueryError(f"{label} must be a JSON object")
    return value


def _load_classical_jsonl(path: Path, label: str) -> list[dict[str, Any]]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        raise ExpertQueryError(f"Cannot read {label}: {exc}") from exc
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(lines, start=1):
        if not line:
            raise ExpertQueryError(f"{label}:{line_number} is blank")
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ExpertQueryError(
                f"{label}:{line_number} is invalid JSON: {exc}"
            ) from exc
        if not isinstance(row, dict):
            raise ExpertQueryError(f"{label}:{line_number} must be an object")
        rows.append(row)
    return rows


def _classical_snapshot() -> tuple[
    dict[str, Any],
    list[dict[str, Any]],
    dict[str, Any],
    list[dict[str, Any]],
    dict[str, Any],
]:
    """Load the digest-bound classical projection used by the hybrid ranker."""

    index = _load_classical_json(CLASSICAL_ROOT / "index.json", "classical index")
    documents = _load_classical_jsonl(
        CLASSICAL_ROOT / "documents.jsonl",
        "classical documents",
    )
    lexicon = _load_classical_json(
        CLASSICAL_ROOT / "lexicon.json",
        "classical lexicon",
    )
    associations = _load_classical_jsonl(
        CLASSICAL_ROOT / "associations.jsonl",
        "classical associations",
    )
    topics = _load_classical_json(
        CLASSICAL_ROOT / "topics.json",
        "classical topics",
    )
    plan = index.get("plan")
    artifacts = index.get("artifacts")
    if not isinstance(plan, dict) or not isinstance(artifacts, dict):
        raise ExpertQueryError("Classical index lacks plan or artifact bindings")
    expected_counts = {
        "documents": len(documents),
        "associations": len(associations),
        "lexicon": len(lexicon.get("terms", [])),
        "topics": topics.get("topic_count"),
    }
    for name, count in expected_counts.items():
        binding = artifacts.get(name)
        if not isinstance(binding, dict) or binding.get("count") != count:
            raise ExpertQueryError(f"Classical artifact count drift: {name}")
    document_ids = [row.get("document_id") for row in documents]
    if (
        any(not isinstance(identifier, str) for identifier in document_ids)
        or len(document_ids) != len(set(document_ids))
    ):
        raise ExpertQueryError("Classical documents have invalid identities")
    return index, documents, lexicon, associations, topics


def _classical_unigrams(value: str, plan: Mapping[str, Any]) -> list[str]:
    minimum = int(plan["tokenization"]["min_token_length"])
    return [
        token
        for token in CLASSICAL_TOKEN_RE.findall(value.casefold())
        if len(token) >= minimum and token not in CLASSICAL_STOPWORDS
    ]


def _classical_tokens(value: str, plan: Mapping[str, Any]) -> list[str]:
    words = _classical_unigrams(value, plan)
    if plan["tokenization"]["ngram_range"] == [1, 1]:
        return words
    return [
        *words,
        *(f"{left} {right}" for left, right in zip(words, words[1:])),
    ]


def _classical_bm25_scores(
    documents: Sequence[dict[str, Any]],
    query_weights: Mapping[str, float],
    lexicon: Mapping[str, Any],
    plan: Mapping[str, Any],
) -> dict[str, float]:
    stats = {
        row["term"]: row
        for row in lexicon["terms"]
        if isinstance(row, dict) and isinstance(row.get("term"), str)
    }
    average = lexicon["average_field_lengths"]
    config = plan["bm25"]
    k1 = float(config["k1"])
    b = float(config["b"])
    result: dict[str, float] = {}
    for document in documents:
        score = 0.0
        for term, query_weight in query_weights.items():
            term_stats = stats.get(term)
            if term_stats is None or query_weight <= 0.0:
                continue
            inverse_document_frequency = float(term_stats["idf"])
            field_score = 0.0
            for field, weight in (
                ("title", config["title_weight"]),
                ("body", config["body_weight"]),
            ):
                frequency = document[f"{field}_terms"].get(term, 0)
                if not frequency or weight <= 0.0:
                    continue
                length = document[f"{field}_length"]
                denominator = frequency + k1 * (
                    1.0
                    - b
                    + b
                    * length
                    / max(float(average[field]), 1e-12)
                )
                field_score += (
                    float(weight)
                    * frequency
                    * (k1 + 1.0)
                    / denominator
                )
            score += float(query_weight) * inverse_document_frequency * field_score
        if score > 0.0:
            result[document["document_id"]] = score
    return result


def _classical_association_expansion(
    query: str,
    associations: Sequence[dict[str, Any]],
    plan: Mapping[str, Any],
) -> dict[str, float]:
    graph = {
        row["term"]: {
            neighbor["term"]: float(neighbor["ppmi"])
            for neighbor in row["neighbors"]
        }
        for row in associations
    }
    originals = set(_classical_unigrams(query, plan))
    frontier = {term: 1.0 for term in originals if term in graph}
    accumulated: defaultdict[str, float] = defaultdict(float)
    for depth in range(2):
        next_frontier: defaultdict[str, float] = defaultdict(float)
        damping = 0.6 ** (depth + 1)
        for term, value in frontier.items():
            neighbors = graph.get(term, {})
            total = sum(neighbors.values())
            if total <= 0.0:
                continue
            for neighbor, weight in neighbors.items():
                propagated = value * damping * weight / total
                next_frontier[neighbor] += propagated
                if neighbor not in originals:
                    accumulated[neighbor] += propagated
        frontier = dict(next_frontier)
    maximum = max(accumulated.values(), default=0.0)
    limit = int(plan["expansion"]["association_terms"])
    selected = sorted(
        accumulated.items(),
        key=lambda item: (-item[1], item[0]),
    )[:limit]
    return {
        term: value
        / maximum
        * float(plan["expansion"]["association_weight"])
        for term, value in selected
        if maximum > 0.0
    }


def _classical_topic_expansion(
    query: str,
    association_weights: Mapping[str, float],
    topics: Mapping[str, Any],
    plan: Mapping[str, Any],
) -> tuple[dict[str, float], dict[str, float]]:
    term_topic = {
        row["term"]: row["topic_id"]
        for row in topics["term_topics"]
    }
    activation: defaultdict[str, float] = defaultdict(float)
    originals = set(_classical_unigrams(query, plan))
    for term in originals:
        if term in term_topic:
            activation[term_topic[term]] += 1.0
    for term, weight in association_weights.items():
        if term in term_topic:
            activation[term_topic[term]] += weight
    total = sum(activation.values())
    query_topics = (
        {
            topic_id: weight / total
            for topic_id, weight in activation.items()
        }
        if total
        else {}
    )
    candidates: list[tuple[float, str, str]] = []
    for topic in topics["topics"]:
        topic_weight = query_topics.get(topic["topic_id"], 0.0)
        if topic_weight <= 0.0:
            continue
        maximum = max(
            (float(item["weight"]) for item in topic["terms"]),
            default=1.0,
        )
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
    selected = sorted(
        candidates,
        key=lambda item: (-item[0], item[1], item[2]),
    )[:limit]
    weights = {
        term: weight * float(plan["expansion"]["topic_weight"])
        for weight, term, _ in selected
    }
    return weights, query_topics


def _rank_scores(scores: Mapping[str, float]) -> list[str]:
    return [
        key
        for key, _ in sorted(
            scores.items(),
            key=lambda item: (-item[1], item[0]),
        )
    ]


def _reciprocal_rank_fusion(
    rankings: Sequence[Sequence[str]],
    *,
    k: int,
) -> dict[str, float]:
    result: defaultdict[str, float] = defaultdict(float)
    for ranking in rankings:
        for rank, identifier in enumerate(ranking, start=1):
            result[identifier] += 1.0 / (k + rank)
    return dict(result)


def _normalize_scores(scores: Mapping[str, float]) -> dict[str, float]:
    maximum = max(scores.values(), default=0.0)
    if maximum <= 0.0:
        return {}
    return {
        identifier: value / maximum
        for identifier, value in scores.items()
    }


def _topic_vector(weights: Iterable[Mapping[str, Any]]) -> dict[str, float]:
    return {
        str(item["topic_id"]): float(item["weight"])
        for item in weights
    }


def _cosine(
    left: Mapping[str, float],
    right: Mapping[str, float],
) -> float:
    if not left or not right:
        return 0.0
    numerator = sum(
        value * right.get(key, 0.0)
        for key, value in left.items()
    )
    left_norm = math.sqrt(sum(value * value for value in left.values()))
    right_norm = math.sqrt(sum(value * value for value in right.values()))
    if not left_norm or not right_norm:
        return 0.0
    return numerator / (left_norm * right_norm)


def _classical_paper_order(query: str) -> list[str]:
    """Return the snapshot's lexical, association, and topic fusion order."""

    index, documents, lexicon, associations, topics = _classical_snapshot()
    plan = index["plan"]
    original = Counter(_classical_tokens(query, plan))
    original_weights = {
        term: float(count)
        for term, count in original.items()
    }
    association_weights = _classical_association_expansion(
        query,
        associations,
        plan,
    )
    topic_weights, query_topics = _classical_topic_expansion(
        query,
        association_weights,
        topics,
        plan,
    )
    association_query = dict(original_weights)
    for term, weight in association_weights.items():
        association_query[term] = association_query.get(term, 0.0) + weight
    topic_query = dict(association_query)
    for term, weight in topic_weights.items():
        topic_query[term] = topic_query.get(term, 0.0) + weight

    lexical_scores = _classical_bm25_scores(
        documents,
        original_weights,
        lexicon,
        plan,
    )
    association_scores = _classical_bm25_scores(
        documents,
        association_query,
        lexicon,
        plan,
    )
    topic_lexical = _classical_bm25_scores(
        documents,
        topic_query,
        lexicon,
        plan,
    )
    normalized_topic_lexical = _normalize_scores(topic_lexical)
    topic_scores = {
        document["document_id"]: (
            0.8
            * normalized_topic_lexical.get(document["document_id"], 0.0)
            + 0.2
            * _cosine(
                query_topics,
                _topic_vector(document["topic_weights"]),
            )
        )
        for document in documents
    }
    topic_scores = {
        identifier: score
        for identifier, score in topic_scores.items()
        if score > 0.0
    }
    fusion_scores = _reciprocal_rank_fusion(
        (
            _rank_scores(lexical_scores),
            _rank_scores(association_scores),
            _rank_scores(topic_scores),
        ),
        k=int(plan["reranking"]["rrf_k"]),
    )

    normalized_fusion = _normalize_scores(fusion_scores)
    by_id = {
        document["document_id"]: document
        for document in documents
    }
    pool_ids = _rank_scores(fusion_scores)[
        : int(plan["reranking"]["candidate_pool"])
    ]
    selected: list[str] = []
    selected_sources: set[str] = set()
    selected_papers: set[str] = set()
    maximum_papers = len(
        {
            document.get("paper_id") or document["source_id"]
            for document in documents
        }
    )
    while pool_ids and len(selected) < maximum_papers:
        choices: list[tuple[float, str]] = []
        for identifier in pool_ids:
            document = by_id[identifier]
            paper_id = str(document.get("paper_id") or document["source_id"])
            if paper_id in selected_papers:
                continue
            vector = _topic_vector(document["topic_weights"])
            similarity = max(
                (
                    _cosine(
                        vector,
                        _topic_vector(by_id[chosen]["topic_weights"]),
                    )
                    for chosen in selected
                ),
                default=0.0,
            )
            source_novelty = float(
                document["source_id"] not in selected_sources
                and paper_id not in selected_papers
            )
            value = (
                float(plan["reranking"]["relevance_weight"])
                * normalized_fusion.get(identifier, 0.0)
                + float(plan["reranking"]["topic_novelty_weight"])
                * (1.0 - similarity)
                + float(plan["reranking"]["source_novelty_weight"])
                * source_novelty
            )
            choices.append((value, identifier))
        if not choices:
            break
        _, chosen = sorted(
            choices,
            key=lambda item: (-item[0], item[1]),
        )[0]
        pool_ids.remove(chosen)
        selected.append(chosen)
        selected_sources.add(by_id[chosen]["source_id"])
        selected_papers.add(
            str(by_id[chosen].get("paper_id") or by_id[chosen]["source_id"])
        )

    return [
        _paper_group({"source_id": by_id[identifier]["source_id"]})
        for identifier in selected
    ]


def _bm25_score(
    counter: Counter[str],
    *,
    document_length: int,
    average_length: float,
    document_frequency: Counter[str],
    document_count: int,
    query_tokens: Sequence[str],
) -> float:
    if average_length <= 0.0:
        return 0.0
    normalization = 1.0 - BM25_B + BM25_B * document_length / average_length
    score = 0.0
    for token in query_tokens:
        frequency = counter[token]
        if frequency == 0:
            continue
        frequency_in_documents = document_frequency[token]
        inverse_document_frequency = math.log(
            1.0
            + (
                document_count
                - frequency_in_documents
                + 0.5
            )
            / (frequency_in_documents + 0.5)
        )
        score += inverse_document_frequency * (
            frequency * (BM25_K1 + 1.0)
            / (frequency + BM25_K1 * normalization)
        )
    return score


def search(
    contains: str,
    *,
    source_id: str | None,
    concept_type: str | None,
    limit: int,
    show_content: bool,
) -> list[dict[str, Any]]:
    """Return trace/classical hybrid matches grouped by paper identity."""

    query_tokens = tuple(dict.fromkeys(_tokens(contains)))
    if not query_tokens:
        raise ExpertQueryError("--contains must include at least one search token")
    if limit < 1:
        raise ExpertQueryError("--limit must be positive")

    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in _records():
        if source_id is not None and record.get("source_id") != source_id:
            continue
        if concept_type is not None and record.get("concept_type") != concept_type:
            continue
        grouped[_paper_group(record)].append(record)
    if not grouped:
        return []

    counters: dict[str, dict[str, Counter[str]]] = {}
    records_by_field: dict[str, dict[str, list[tuple[dict[str, Any], Counter[str]]]]] = {}
    for identity, records in grouped.items():
        counters[identity] = {
            field: Counter()
            for field in FIELD_WEIGHTS
        }
        records_by_field[identity] = {
            field: []
            for field in FIELD_WEIGHTS
        }
        for record in records:
            field = _field(record)
            counter = Counter(_tokens(_record_text(record)))
            counters[identity][field].update(counter)
            records_by_field[identity][field].append((record, counter))

    document_count = len(grouped)
    document_frequency = {
        field: Counter()
        for field in FIELD_WEIGHTS
    }
    average_length: dict[str, float] = {}
    for field in FIELD_WEIGHTS:
        for field_counters in counters.values():
            document_frequency[field].update(field_counters[field].keys())
        average_length[field] = (
            sum(sum(field_counters[field].values()) for field_counters in counters.values())
            / document_count
        )

    ranked: list[tuple[float, str, dict[str, Any]]] = []
    for identity, field_counters in counters.items():
        field_scores: dict[str, float] = {}
        for field, weight in FIELD_WEIGHTS.items():
            counter = field_counters[field]
            field_scores[field] = weight * _bm25_score(
                counter,
                document_length=sum(counter.values()),
                average_length=average_length[field],
                document_frequency=document_frequency[field],
                document_count=document_count,
                query_tokens=query_tokens,
            )
        total_score = sum(field_scores.values())
        if total_score <= 0.0:
            continue

        representatives: list[tuple[float, str, str, dict[str, Any]]] = []
        for field, rows in records_by_field[identity].items():
            weight = FIELD_WEIGHTS[field]
            for record, counter in rows:
                contribution = weight * _bm25_score(
                    counter,
                    document_length=sum(counter.values()),
                    average_length=average_length[field],
                    document_frequency=document_frequency[field],
                    document_count=document_count,
                    query_tokens=query_tokens,
                )
                representatives.append(
                    (
                        -contribution,
                        str(record.get("source_id", "")),
                        str(record.get("record_id", "")),
                        record,
                    )
                )
        representatives.sort(key=lambda row: row[:3])
        ranked.append((total_score, identity, representatives[0][3]))

    trace_order = sorted(ranked, key=lambda row: (-row[0], row[1]))
    trace_ranks = {
        identity: rank
        for rank, (_, identity, _) in enumerate(trace_order, start=1)
    }
    classical_ranks = {
        identity: rank
        for rank, identity in enumerate(
            _classical_paper_order(contains),
            start=1,
        )
    }
    hybrid: list[tuple[float, float, str, dict[str, Any]]] = []
    for trace_score, identity, record in ranked:
        combined_score = TRACE_RRF_WEIGHT / (
            HYBRID_RRF_K + trace_ranks[identity]
        )
        if identity in classical_ranks:
            combined_score += CLASSICAL_RRF_WEIGHT / (
                HYBRID_RRF_K + classical_ranks[identity]
            )
        hybrid.append(
            (
                combined_score,
                trace_score,
                identity,
                record,
            )
        )
    hybrid.sort(key=lambda row: (-row[0], -row[1], row[2]))
    return [
        _project(
            record,
            show_content=show_content,
            score=round(score, 12),
        )
        for score, _, _, record in hybrid[:limit]
    ]


def get_record(
    source_id: str,
    record_id: str,
    *,
    show_content: bool,
) -> dict[str, Any]:
    """Return one exact authoritative record identity."""

    for record in _records():
        if record.get("source_id") == source_id and record.get("record_id") == record_id:
            return _project(record, show_content=show_content, score=None)
    raise ExpertQueryError(f"Record is absent: ({source_id!r}, {record_id!r})")


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser."""

    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("verify", help="Verify every manifest binding")

    search_parser = subparsers.add_parser("search", help="Search the embedded ledger")
    search_parser.add_argument("--contains", required=True)
    search_parser.add_argument("--source-id")
    search_parser.add_argument("--type", dest="concept_type")
    search_parser.add_argument("--limit", type=int, default=10)
    search_parser.add_argument("--show-content", action="store_true")

    get_parser = subparsers.add_parser("get", help="Get one exact ledger record")
    get_parser.add_argument("--source-id", required=True)
    get_parser.add_argument("--record-id", required=True)
    get_parser.add_argument("--show-content", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Verify the expert and run one read-only operation."""

    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(encoding="utf-8")
    args = build_parser().parse_args(argv)
    try:
        verification = verify()
        if args.command == "verify":
            payload: Any = verification
        elif args.command == "search":
            payload = {
                "verification": verification,
                "results": search(
                    args.contains,
                    source_id=args.source_id,
                    concept_type=args.concept_type,
                    limit=args.limit,
                    show_content=args.show_content,
                ),
            }
        else:
            payload = {
                "verification": verification,
                "result": get_record(
                    args.source_id,
                    args.record_id,
                    show_content=args.show_content,
                ),
            }
    except (OSError, ExpertQueryError) as exc:
        raise SystemExit(f"Expert query failed: {exc}") from exc
    print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
