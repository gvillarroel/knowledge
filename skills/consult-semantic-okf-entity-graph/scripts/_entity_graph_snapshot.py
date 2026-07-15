#!/usr/bin/env python3
"""Validate and query a Semantic OKF entity-section graph without mutation."""

from __future__ import annotations

import math
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from _entity_graph_model import (
    ALGORITHMS,
    SCHEMA_VERSION,
    EntityGraphError,
    EntityGraphPlan,
    content_tokens,
    core_tree_sha256,
    derive_projection,
    load_core,
    parse_plan,
    read_json,
    read_jsonl,
    select_records,
    sha256_file,
    tokens,
    validate_rows,
)


EXPECTED_FILES = {"index.json", "build-report.json", "entities.jsonl", "sections.jsonl", "mentions.jsonl", "edges.jsonl", "lexicon.json"}
INDEX_KEYS = {
    "schema_version",
    "authoritative",
    "discovery_only",
    "core",
    "entity_graph_plan_sha256",
    "plan",
    "selection",
    "algorithms",
    "artifacts",
    "summary",
}
ARTIFACT_PATHS = {
    "entities": "entity-graph/entities.jsonl",
    "sections": "entity-graph/sections.jsonl",
    "mentions": "entity-graph/mentions.jsonl",
    "edges": "entity-graph/edges.jsonl",
    "lexicon": "entity-graph/lexicon.json",
}


class SnapshotError(RuntimeError):
    """Describe an invalid or unsafe entity-graph consultation request."""


@dataclass(frozen=True)
class EntityGraphSnapshot:
    """Hold a fully validated read-only snapshot in memory."""

    root: Path
    index: dict[str, Any]
    index_sha256: str
    plan: EntityGraphPlan
    records: list[dict[str, Any]]
    entities: list[dict[str, Any]]
    sections: list[dict[str, Any]]
    mentions: list[dict[str, Any]]
    edges: list[dict[str, Any]]
    lexicon: dict[str, Any]
    deep_validation: bool


def _artifact(root: Path, relative: str, count: int | None = None) -> dict[str, Any]:
    path = root / relative
    result: dict[str, Any] = {"path": relative, "bytes": path.stat().st_size, "sha256": sha256_file(path)}
    if count is not None:
        result["count"] = count
    return result


def _core_binding(root: Path) -> dict[str, Any]:
    records, _ = load_core(root)
    return {
        "tree_sha256": core_tree_sha256(root),
        "records_sha256": sha256_file(root / "semantic" / "records.jsonl"),
        "record_count": len(records),
    }


def _artifacts(root: Path, values: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "entities": _artifact(root, ARTIFACT_PATHS["entities"], len(values["entities"])),
        "sections": _artifact(root, ARTIFACT_PATHS["sections"], len(values["sections"])),
        "mentions": _artifact(root, ARTIFACT_PATHS["mentions"], len(values["mentions"])),
        "edges": _artifact(root, ARTIFACT_PATHS["edges"], len(values["edges"])),
        "lexicon": _artifact(root, ARTIFACT_PATHS["lexicon"], len(values["lexicon"]["terms"])),
    }


def _summary(index: Mapping[str, Any], values: Mapping[str, Any]) -> dict[str, Any]:
    entities = values["entities"]
    edges = values["edges"]
    return {
        "inputs": index["selection"]["input_count"],
        "selected_records": index["summary"]["selected_records"],
        "sections": len(values["sections"]),
        "entities": len(entities),
        "reviewed_entities": sum(entity["review_state"] == "reviewed" for entity in entities),
        "candidate_entities": sum(entity["review_state"] == "candidate" for entity in entities),
        "mentions": len(values["mentions"]),
        "edges": len(edges),
        "reviewed_edges": sum(edge["review_state"] == "reviewed" for edge in edges),
        "candidate_edges": sum(edge["review_state"] == "candidate" for edge in edges),
        "lexicon_terms": len(values["lexicon"]["terms"]),
    }


def _verify_authoritative_bindings(
    records: Sequence[dict[str, Any]], entities: Sequence[dict[str, Any]], sections: Sequence[dict[str, Any]]
) -> None:
    record_by_identity = {(record.get("source_id"), record.get("record_id")): record for record in records}
    for entity in entities:
        identity = entity["authoritative_identity"]
        if identity is None:
            continue
        record = record_by_identity.get((identity["source_id"], identity["record_id"]))
        if record is None:
            raise SnapshotError("reviewed entity identity is absent from the authoritative ledger")
        expected = {
            "source_id": record.get("source_id"),
            "record_id": record.get("record_id"),
            "record_sha256": record.get("record_sha256"),
            "concept_id": record.get("concept_id"),
            "concept_path": record.get("concept_path"),
            "subject_iri": record.get("subject_iri"),
        }
        if identity != expected:
            raise SnapshotError("reviewed entity identity differs from its authoritative ledger record")
    for section in sections:
        record = record_by_identity.get((section["source_id"], section["record_id"]))
        if record is None or record.get("record_sha256") != section["record_sha256"]:
            raise SnapshotError("section record binding is absent or stale")
        body = record.get("body")
        locator = section["locator"]
        if not isinstance(body, str) or body[locator["start"] : locator["end"]] != section["text"]:
            raise SnapshotError("section character locator does not reconstruct exact authoritative text")
        concept = section["concept_path"]
        path = (Path(record.get("concept_path", "")))
        if concept != path.as_posix():
            raise SnapshotError("section concept path differs from the authoritative record")


def load_snapshot(root: Path, *, deep_validation: bool = False) -> EntityGraphSnapshot:
    """Load and validate a graph snapshot without writing any files."""

    try:
        root = root.resolve(strict=True)
        graph = root / "entity-graph"
        if not graph.is_dir() or graph.is_symlink():
            raise SnapshotError("entity-graph must be a real directory")
        actual = {path.name for path in graph.iterdir()}
        if actual != EXPECTED_FILES:
            raise SnapshotError(
                f"entity-graph artifact set is closed; missing={sorted(EXPECTED_FILES - actual)}, unknown={sorted(actual - EXPECTED_FILES)}"
            )
        if any(path.is_symlink() or not path.is_file() for path in graph.iterdir()):
            raise SnapshotError("entity-graph artifacts must be regular files")
        index = read_json(graph / "index.json", "entity-graph/index.json")
        if not isinstance(index, dict) or set(index) != INDEX_KEYS:
            raise SnapshotError("entity-graph index has an invalid closed schema")
        if index["schema_version"] != SCHEMA_VERSION or index["authoritative"] is not False or index["discovery_only"] is not True:
            raise SnapshotError("entity-graph index version or authority markers are invalid")
        if index["algorithms"] != ALGORITHMS:
            raise SnapshotError("entity-graph algorithm identities are invalid")
        plan = parse_plan(index["plan"])
        if index["entity_graph_plan_sha256"] != plan.sha256:
            raise SnapshotError("entity-graph plan digest is invalid")
        records, sources = load_core(root)
        selected, selection = select_records(records, sources, plan)
        if index["selection"] != selection or index["core"] != _core_binding(root):
            raise SnapshotError("entity-graph core or source selection binding is stale")
        values = {
            "entities": read_jsonl(graph / "entities.jsonl", label="entity-graph/entities.jsonl"),
            "sections": read_jsonl(graph / "sections.jsonl", label="entity-graph/sections.jsonl"),
            "mentions": read_jsonl(graph / "mentions.jsonl", label="entity-graph/mentions.jsonl"),
            "edges": read_jsonl(graph / "edges.jsonl", label="entity-graph/edges.jsonl"),
            "lexicon": read_json(graph / "lexicon.json", "entity-graph/lexicon.json"),
        }
        validate_rows(values["entities"], values["sections"], values["mentions"], values["edges"], values["lexicon"])
        if index["artifacts"] != _artifacts(root, values):
            raise SnapshotError("entity-graph artifact hashes, sizes, or counts are invalid")
        if index["summary"] != _summary(index, values):
            raise SnapshotError("entity-graph summary is inconsistent with persisted rows")
        _verify_authoritative_bindings(selected, values["entities"], values["sections"])
        if deep_validation:
            expected = derive_projection(root, plan)
            for name in ("entities", "sections", "mentions", "edges", "lexicon"):
                if values[name] != expected[name]:
                    raise SnapshotError(f"entity-graph {name} differ from independent deterministic rederivation")
            if index["selection"] != expected["selection"] or index["summary"] != expected["summary"]:
                raise SnapshotError("entity-graph index differs from independent deterministic rederivation")
        report = read_json(graph / "build-report.json", "entity-graph/build-report.json")
        expected_report = {
            "schema_version": SCHEMA_VERSION,
            "valid": True,
            "status": "pass",
            "errors": [],
            "warnings": [
                {
                    "code": "derived-discovery-only",
                    "message": "Entity mentions, candidate phrases, co-mentions, and retrieval scores are non-authoritative discovery signals.",
                }
            ],
            "entity_graph_plan_sha256": plan.sha256,
            "core": index["core"],
            "selection": index["selection"],
            "summary": index["summary"],
            "artifacts": {"index": _artifact(root, "entity-graph/index.json"), **index["artifacts"]},
        }
        if report != expected_report:
            raise SnapshotError("entity-graph build report differs from current validated artifacts")
        return EntityGraphSnapshot(
            root=root,
            index=index,
            index_sha256=sha256_file(graph / "index.json"),
            plan=plan,
            records=selected,
            entities=values["entities"],
            sections=values["sections"],
            mentions=values["mentions"],
            edges=values["edges"],
            lexicon=values["lexicon"],
            deep_validation=deep_validation,
        )
    except EntityGraphError as exc:
        raise SnapshotError(str(exc)) from exc


def inspect_snapshot(snapshot: EntityGraphSnapshot) -> dict[str, Any]:
    """Describe one validated snapshot and its authority boundary."""

    return {
        "schema_version": SCHEMA_VERSION,
        "status": "pass",
        "authoritative": False,
        "discovery_only": True,
        "read_only": True,
        "deep_validation": snapshot.deep_validation,
        "summary": snapshot.index["summary"],
        "core": snapshot.index["core"],
        "entity_graph_index_sha256": snapshot.index_sha256,
        "entity_graph_plan_sha256": snapshot.plan.sha256,
        "algorithms": ALGORITHMS,
    }


def _bm25_scores(snapshot: EntityGraphSnapshot, query_weights: Mapping[str, float]) -> dict[str, float]:
    plan = snapshot.plan.raw
    k1 = float(plan["bm25"]["k1"])
    b = float(plan["bm25"]["b"])
    average = float(snapshot.lexicon["average_length"])
    scores: dict[str, float] = {}
    for section in snapshot.sections:
        score = 0.0
        length = float(section["length"])
        for term, query_weight in query_weights.items():
            frequency = float(section["terms"].get(term, 0))
            term_row = snapshot.lexicon["terms"].get(term)
            if frequency <= 0 or not isinstance(term_row, dict):
                continue
            denominator = frequency + k1 * (1.0 - b + b * length / average)
            score += float(query_weight) * float(term_row["idf"]) * frequency * (k1 + 1.0) / denominator
        if score > 0:
            scores[section["section_id"]] = score
    return scores


def _contains_phrase(sequence: Sequence[str], phrase: Sequence[str]) -> bool:
    return bool(phrase) and any(tuple(sequence[index : index + len(phrase)]) == tuple(phrase) for index in range(len(sequence) - len(phrase) + 1))


def _resolve_entities(snapshot: EntityGraphSnapshot, query: str) -> list[dict[str, Any]]:
    query_tokens = content_tokens(query, snapshot.plan)
    if not query_tokens:
        return []
    query_set = set(query_tokens)
    lexicon = snapshot.lexicon["terms"]
    result = []
    record_by_identity = {(record["source_id"], record["record_id"]): record for record in snapshot.records}
    section_by_id = {section["section_id"]: section for section in snapshot.sections}
    claim_evidence: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for edge in snapshot.edges:
        if edge["predicate"] != "supportedBySection":
            continue
        section = section_by_id[edge["target_node"]]
        claim_evidence[edge["source_node"]].append(
            {
                "section_id": section["section_id"],
                "paper_id": section["paper_id"],
                "source_path": section["source_path"],
                "locator": section["locator"]["fragment"],
                "text_sha256": section["text_sha256"],
            }
        )
    for entity in snapshot.entities:
        alias_values = [entity["canonical_label"], *entity["aliases"]]
        best_score = 0.0
        matched: set[str] = set()
        for alias in alias_values:
            alias_tokens = content_tokens(alias, snapshot.plan)
            if not alias_tokens:
                continue
            overlap = query_set & set(alias_tokens)
            if not overlap:
                continue
            weighted_overlap = sum(float(lexicon.get(term, {"idf": 1.0})["idf"]) for term in overlap)
            weighted_alias = sum(float(lexicon.get(term, {"idf": 1.0})["idf"]) for term in set(alias_tokens))
            score = weighted_overlap / max(weighted_alias, 1e-12)
            if _contains_phrase(query_tokens, alias_tokens):
                score += 1.0
            if entity["entity_type"] == "claim":
                score *= 1.15
            elif entity["review_state"] == "reviewed":
                score *= 1.1
            else:
                score *= 0.9
            if score > best_score:
                best_score = score
            matched.update(overlap)
        if best_score > 0:
            identity = entity["authoritative_identity"]
            record = None if identity is None else record_by_identity.get((identity["source_id"], identity["record_id"]))
            result.append(
                {
                    "entity_id": entity["entity_id"],
                    "entity_type": entity["entity_type"],
                    "canonical_label": entity["canonical_label"],
                    "review_state": entity["review_state"],
                    "matched_terms": sorted(matched),
                    "score": round(best_score, 12),
                    "record_id": None if identity is None else identity["record_id"],
                    "concept_path": None if identity is None else identity["concept_path"],
                    "record_source_path": None if record is None else record["source_path"],
                    "claim_evidence": sorted(
                        claim_evidence.get(entity["entity_id"], []),
                        key=lambda item: (item["paper_id"], item["locator"], item["section_id"]),
                    ),
                }
            )
    result.sort(key=lambda row: (-row["score"], row["review_state"] != "reviewed", row["entity_id"]))
    return result[: int(snapshot.plan.raw["query"]["resolved_entities"])]


def _normalize_scores(scores: Mapping[str, float]) -> dict[str, float]:
    maximum = max(scores.values(), default=0.0)
    return {key: value / maximum for key, value in scores.items()} if maximum > 0 else {}


def _direct_entity_scores(snapshot: EntityGraphSnapshot, resolved: Sequence[dict[str, Any]]) -> dict[str, float]:
    start = {row["entity_id"]: float(row["score"]) for row in resolved}
    scores: defaultdict[str, float] = defaultdict(float)
    mention_weight = float(snapshot.plan.raw["query"]["mention_weight"])
    for mention in snapshot.mentions:
        if mention["entity_id"] in start:
            scores[mention["section_id"]] += start[mention["entity_id"]] * mention_weight * (1.0 + math.log1p(mention["count"]))
    for edge in snapshot.edges:
        if edge["source_node"] not in start:
            continue
        if edge["predicate"] == "supportedBySection":
            scores[edge["target_node"]] += start[edge["source_node"]] * 2.0
        elif edge["predicate"] == "mentionedInSection":
            scores[edge["target_node"]] += start[edge["source_node"]] * mention_weight
    return dict(scores)


def _traversal_scores(snapshot: EntityGraphSnapshot, resolved: Sequence[dict[str, Any]]) -> tuple[dict[str, float], dict[str, set[str]]]:
    query = snapshot.plan.raw["query"]
    reviewed_weight = float(query["reviewed_edge_weight"])
    candidate_weight = float(query["candidate_edge_weight"])
    decay = float(query["hop_decay"])
    max_hops = int(query["max_hops"])
    adjacency: dict[str, list[tuple[str, dict[str, Any]]]] = defaultdict(list)
    for edge in snapshot.edges:
        adjacency[edge["source_node"]].append((edge["target_node"], edge))
        adjacency[edge["target_node"]].append((edge["source_node"], edge))
    frontier = {row["entity_id"]: float(row["score"]) for row in resolved}
    best = dict(frontier)
    section_scores: defaultdict[str, float] = defaultdict(float)
    section_edges: dict[str, set[str]] = defaultdict(set)
    section_ids = {section["section_id"] for section in snapshot.sections}
    for hop in range(1, max_hops + 1):
        following: dict[str, float] = {}
        for node, node_score in sorted(frontier.items()):
            for neighbor, edge in adjacency.get(node, []):
                authority_weight = reviewed_weight if edge["review_state"] == "reviewed" else candidate_weight
                bounded_edge = float(edge["weight"]) / (1.0 + float(edge["weight"]))
                propagated = node_score * authority_weight * bounded_edge * (decay ** hop)
                if propagated <= 0:
                    continue
                if neighbor in section_ids:
                    section_scores[neighbor] += propagated
                    section_edges[neighbor].add(edge["edge_id"])
                if propagated > best.get(neighbor, 0.0):
                    best[neighbor] = propagated
                    following[neighbor] = max(following.get(neighbor, 0.0), propagated)
        frontier = following
        if not frontier:
            break
    for mention in snapshot.mentions:
        entity_score = best.get(mention["entity_id"], 0.0)
        if entity_score > 0:
            section_scores[mention["section_id"]] += entity_score * 0.25 * (1.0 + math.log1p(mention["count"]))
    return dict(section_scores), section_edges


def _rank(scores: Mapping[str, float]) -> list[str]:
    return sorted(scores, key=lambda identifier: (-scores[identifier], identifier))


def _rrf(rankings: Sequence[Sequence[str]], k: int) -> dict[str, float]:
    scores: defaultdict[str, float] = defaultdict(float)
    for ranking in rankings:
        for rank, identifier in enumerate(ranking, start=1):
            scores[identifier] += 1.0 / (k + rank)
    return dict(scores)


def _diversify(snapshot: EntityGraphSnapshot, scores: Mapping[str, float], top_k: int) -> list[dict[str, Any]]:
    by_id = {section["section_id"]: section for section in snapshot.sections}
    pool = _rank(scores)[: int(snapshot.plan.raw["query"]["candidate_pool"])]
    selected: list[dict[str, Any]] = []
    paper_counts: Counter[str] = Counter()
    maximum = int(snapshot.plan.raw["query"]["max_per_paper"])
    for identifier in pool:
        section = by_id[identifier]
        if paper_counts[section["paper_id"]] >= maximum:
            continue
        selected.append(section)
        paper_counts[section["paper_id"]] += 1
        if len(selected) >= top_k:
            break
    return selected


def search_snapshot(
    snapshot: EntityGraphSnapshot,
    query: str,
    mode: str,
    top_k: int,
    *,
    source_ids: Sequence[str] = (),
    paper_ids: Sequence[str] = (),
) -> dict[str, Any]:
    """Search exact sections by lexical, entity, traversal, or fused graph ranking."""

    if mode not in {"lexical", "entity", "traversal", "fusion"}:
        raise SnapshotError("mode must be lexical, entity, traversal, or fusion")
    if not isinstance(query, str) or not query.strip():
        raise SnapshotError("query must be nonempty")
    if isinstance(top_k, bool) or not isinstance(top_k, int) or not 1 <= top_k <= 1000:
        raise SnapshotError("top-k must be an integer from 1 through 1000")
    source_filter, paper_filter = set(source_ids), set(paper_ids)
    eligible = {
        section["section_id"]
        for section in snapshot.sections
        if (not source_filter or section["source_id"] in source_filter)
        and (not paper_filter or section["paper_id"] in paper_filter)
    }
    query_weights = Counter(content_tokens(query, snapshot.plan))
    lexical = {key: value for key, value in _bm25_scores(snapshot, query_weights).items() if key in eligible}
    resolved = _resolve_entities(snapshot, query)
    entity = {key: value for key, value in _direct_entity_scores(snapshot, resolved).items() if key in eligible}
    traversal, path_edges = _traversal_scores(snapshot, resolved)
    traversal = {key: value for key, value in traversal.items() if key in eligible}
    fusion = _rrf([_rank(lexical), _rank(entity), _rank(traversal)], int(snapshot.plan.raw["query"]["rrf_k"]))
    route_scores = {"lexical": lexical, "entity": entity, "traversal": traversal, "fusion": fusion}
    scores = route_scores[mode]
    selected = _diversify(snapshot, scores, top_k)
    component_ranks = {
        name: {identifier: rank for rank, identifier in enumerate(_rank(values), start=1)}
        for name, values in route_scores.items()
    }
    edges_by_section: dict[str, list[str]] = defaultdict(list)
    for edge in snapshot.edges:
        for section_id in edge["evidence_section_ids"]:
            edges_by_section[section_id].append(edge["edge_id"])
    results = []
    for rank, section in enumerate(selected, start=1):
        identifier = section["section_id"]
        supporting = sorted(set(edges_by_section.get(identifier, [])) | path_edges.get(identifier, set()))[:20]
        results.append(
            {
                "rank": rank,
                "section_id": identifier,
                "document_id": identifier,
                "source_id": section["source_id"],
                "paper_id": section["paper_id"],
                "record_id": section["record_id"],
                "record_sha256": section["record_sha256"],
                "concept_id": section["concept_id"],
                "concept_type": "Research Paper Section",
                "concept_path": section["concept_path"],
                "source_path": section["source_path"],
                "ordinal": section["ordinal"],
                "heading": section["heading"],
                "locator": {
                    "kind": section["locator"]["kind"],
                    "start": section["locator"]["start"],
                    "end": section["locator"]["end"],
                },
                "text": section["text"],
                "text_sha256": section["text_sha256"],
                "score": scores.get(identifier, 0.0),
                "scores": {name: values.get(identifier) for name, values in route_scores.items()},
                "ranks": {name: ranks.get(identifier) for name, ranks in component_ranks.items()},
                "supporting_edge_ids": supporting,
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
        "filters": {"source_ids": sorted(source_filter), "paper_ids": sorted(paper_filter)},
        "resolved_entities": resolved,
        "snapshot": {
            "core_tree_sha256": snapshot.index["core"]["tree_sha256"],
            "entity_graph_index_sha256": snapshot.index_sha256,
            "entity_graph_plan_sha256": snapshot.plan.sha256,
            "deep_validation": snapshot.deep_validation,
        },
        "results": results,
    }
