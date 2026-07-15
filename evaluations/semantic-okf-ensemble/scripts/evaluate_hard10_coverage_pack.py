#!/usr/bin/env python3
"""Evaluate the final ensemble coverage pack against the frozen hard ten."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import statistics
import sys
import time
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Mapping, Sequence

from _evaluation import (
    ENSEMBLE_PLAN,
    REPO_ROOT,
    EvaluationError,
    benchmark_rows,
    canonical_json,
    load_json,
    load_jsonl,
    mean,
    module_from_path,
    percentile,
    sha256,
    write_new,
)


SCHEMA_VERSION = "semantic-okf-ensemble-hard10-coverage-pack/2.0"
COVERAGE_ALGORITHM = "bounded-reviewed-claim-multisignal-expansion-v2"
ROUTES = ("adaptive", "graph", "embedding", "union")
OVERLAPS = (
    "adaptive_graph",
    "adaptive_embedding",
    "graph_embedding",
    "all_three",
)
GRAPH_LIMITS = (8, 80)
EMBEDDING_LIMITS = (20, 240)
FROZEN_MANIFEST_SHA256 = (
    "2f905bd9a7ad07991fe215e0b82b3c7bfdcccbff9431ee5bd20095d99b8f4414"
)
REVIEWED_GROUND_TRUTH = (
    REPO_ROOT
    / "evaluations/semantic-okf-ensemble/reviewed-benchmark/hard-ground-truth.jsonl"
)
REVIEWED_ANSWER_BENCHMARK = (
    REPO_ROOT
    / "evaluations/semantic-okf-ensemble/reviewed-benchmark/frozen-answer-benchmark.json"
)
REVIEWED_ANSWER_BENCHMARK_SCHEMA = (
    "semantic-okf-frozen-answer-benchmark/1.0"
)
EVIDENCE_RE = re.compile(r"(?P<path>[^#;]+)#PDF-page-(?P<page>[1-9]\d*)")
RUNTIME = REPO_ROOT / "skills/consult-semantic-okf-ensemble/scripts/_ensemble_snapshot.py"
INVENTORY = REPO_ROOT / "evaluations/semantic-okf-embeddings/input-inventory.json"
CORPUS_ROOT = REPO_ROOT / "evaluations/graphrag-cross-paper"


def _exact(value: Any, keys: set[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise EvaluationError(f"{label} must be an object")
    actual = set(value)
    if actual != keys:
        raise EvaluationError(
            f"{label} uses a closed schema; missing={sorted(keys - actual)}, "
            f"unknown={sorted(actual - keys)}"
        )
    return value


def _canonical_sha(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _repository_path(repo: Path, path: Path, label: str) -> str:
    try:
        return path.resolve(strict=True).relative_to(repo.resolve(strict=True)).as_posix()
    except ValueError as exc:
        raise EvaluationError(f"{label} must remain inside the repository") from exc


def _tree(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): sha256(path)
        for path in sorted(root.rglob("*"))
        if path.is_file()
        and path.suffix.lower() not in {".pyc", ".pyo"}
        and "__pycache__" not in path.parts
    }


def _tree_sha(root: Path) -> str:
    return _canonical_sha(
        [{"path": path, "sha256": digest} for path, digest in _tree(root).items()]
    )


def _safe_join(root: Path, relative: str, label: str) -> Path:
    if not isinstance(relative, str) or not relative:
        raise EvaluationError(f"{label} must be a nonempty relative path")
    logical = PurePosixPath(relative.replace("\\", "/"))
    if logical.is_absolute() or not logical.parts or any(part in {"", ".", ".."} for part in logical.parts):
        raise EvaluationError(f"{label} is not a safe relative path: {relative!r}")
    candidate = root.joinpath(*logical.parts).resolve(strict=True)
    try:
        candidate.relative_to(root.resolve(strict=True))
    except ValueError as exc:
        raise EvaluationError(f"{label} escapes its declared root") from exc
    if not candidate.is_file() or candidate.is_symlink():
        raise EvaluationError(f"{label} must resolve to one regular file")
    return candidate


def _source_inventory(inventory_path: Path, corpus_root: Path) -> dict[str, dict[str, Any]]:
    inventory = load_json(inventory_path)
    if inventory.get("schema_version") != "1.0" or not isinstance(inventory.get("files"), list):
        raise EvaluationError("input inventory has an unsupported schema")
    entries: dict[str, dict[str, Any]] = {}
    for row in inventory["files"]:
        _exact(row, {"paper_id", "role", "kind", "path", "bytes", "rows", "sha256"}, "inventory row")
        logical = row["path"]
        if not isinstance(logical, str) or logical in entries:
            raise EvaluationError("inventory source paths must be unique strings")
        source = _safe_join(corpus_root, logical, "inventory source")
        if source.stat().st_size != row["bytes"] or sha256(source) != row["sha256"]:
            raise EvaluationError(f"inventory source differs from its byte/hash binding: {logical}")
        entries[logical] = row
    if len(entries) != 30:
        raise EvaluationError("coverage evaluation requires the exact 30 paper/claim inventory")
    return entries


def _claim_sources(corpus_root: Path, inventory: Mapping[str, Mapping[str, Any]]) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    for logical, entry in sorted(inventory.items()):
        if entry["role"] != "reviewed-claims":
            continue
        source_rows = load_jsonl(_safe_join(corpus_root, logical, "reviewed claim source"))
        if len(source_rows) != entry["rows"]:
            raise EvaluationError(f"claim source row count differs: {logical}")
        for row in source_rows:
            claim_id = row.get("id")
            if not isinstance(claim_id, str) or not claim_id or claim_id in rows:
                raise EvaluationError(f"claim sources contain an invalid or duplicate id: {claim_id!r}")
            rows[claim_id] = row
    return rows


def _record_digest(record: Mapping[str, Any]) -> str:
    fields = (
        "source_id",
        "source_kind",
        "source_path",
        "record_id",
        "subject_iri",
        "ontology_class_iri",
        "concept_type",
        "title",
        "body",
        "attributes",
    )
    if any(field not in record for field in fields):
        raise EvaluationError(f"semantic record omits digest fields: {record.get('record_id')}")
    return _canonical_sha({field: record[field] for field in fields})


def _parsed_evidence(raw: Mapping[str, Any]) -> tuple[list[str], list[int], list[tuple[str, int]]]:
    locator = raw.get("evidence_locator")
    if not isinstance(locator, str) or not locator:
        raise EvaluationError(f"reviewed claim has no evidence locator: {raw.get('id')}")
    paths: set[str] = set()
    pages: set[int] = set()
    pairs: set[tuple[str, int]] = set()
    for fragment in locator.split(";"):
        match = EVIDENCE_RE.fullmatch(fragment)
        if match is None:
            raise EvaluationError(f"reviewed claim has an invalid evidence locator: {raw.get('id')}")
        evidence_path = match.group("path").replace("\\", "/")
        page = int(match.group("page"))
        paths.add(evidence_path)
        pages.add(page)
        pairs.add((evidence_path, page))
    return sorted(paths), sorted(pages), sorted(pairs)


def _validate_binding(
    binding: Mapping[str, Any],
    *,
    bundle: Path,
    corpus_root: Path,
    inventory: Mapping[str, Mapping[str, Any]],
    source_rows: Mapping[str, Mapping[str, Any]],
    semantic_records: Mapping[str, Mapping[str, Any]],
    semantic_sources: Mapping[str, Mapping[str, Any]],
) -> None:
    claim_id = binding.get("record_id")
    if not isinstance(claim_id, str) or claim_id not in source_rows or claim_id not in semantic_records:
        raise EvaluationError(f"coverage pack names an unknown authoritative claim: {claim_id!r}")
    raw = source_rows[claim_id]
    record = semantic_records[claim_id]
    for field in (
        "source_id",
        "record_id",
        "record_sha256",
        "concept_id",
        "concept_type",
        "concept_path",
        "source_path",
    ):
        if binding.get(field) != record.get(field):
            raise EvaluationError(f"binding {field} differs from semantic record: {claim_id}")
    if binding.get("review_state") != "reviewed" or raw.get("review_state") != "reviewed":
        raise EvaluationError(f"coverage binding is not independently reviewed: {claim_id}")
    if record.get("record_sha256") != _record_digest(record):
        raise EvaluationError(f"semantic record digest does not rederive: {claim_id}")
    expected_attributes = {key: value for key, value in raw.items() if key not in {"id", "title"}}
    if record.get("attributes") != expected_attributes or record.get("title") != raw.get("title"):
        raise EvaluationError(f"semantic record differs from the authoritative JSONL row: {claim_id}")
    if binding.get("authoritative_text") != raw.get("interpretation"):
        raise EvaluationError(f"binding text differs from reviewed interpretation: {claim_id}")
    text = binding.get("authoritative_text")
    if not isinstance(text, str) or hashlib.sha256(text.encode("utf-8")).hexdigest() != binding.get("authoritative_text_sha256"):
        raise EvaluationError(f"binding authoritative text hash differs: {claim_id}")
    expected_paths, expected_pages, expected_pairs = _parsed_evidence(raw)
    if binding.get("evidence_paths") != expected_paths:
        raise EvaluationError(f"binding evidence paths differ from reviewed locator: {claim_id}")
    if binding.get("citation_pages") != expected_pages:
        raise EvaluationError(f"binding citation pages differ from reviewed locator: {claim_id}")
    if binding.get("locator_tokens") != [f"PDF-page-{page}" for page in expected_pages]:
        raise EvaluationError(f"binding locator tokens differ from reviewed locator: {claim_id}")
    source_path = binding.get("source_path")
    if source_path not in inventory or inventory[source_path]["role"] != "reviewed-claims":
        raise EvaluationError(f"binding claim path is not in the pinned inventory: {claim_id}")
    source_manifest_row = semantic_sources.get(str(binding.get("source_id")))
    if (
        source_manifest_row is None
        or source_manifest_row.get("path") != source_path
        or record.get("source_content_sha256") != source_manifest_row.get("content_sha256")
    ):
        raise EvaluationError(f"binding source manifest linkage differs: {claim_id}")
    for evidence_path, page in expected_pairs:
        if evidence_path not in inventory or inventory[evidence_path]["role"] != "paper-markdown":
            raise EvaluationError(f"binding evidence path is not in the pinned inventory: {claim_id}")
        evidence = _safe_join(corpus_root, evidence_path, "binding evidence source")
        if re.search(rf"(?m)^## PDF page {page}\s*$", evidence.read_text(encoding="utf-8")) is None:
            raise EvaluationError(f"binding page locator does not resolve: {claim_id} PDF-page-{page}")
    concept = _safe_join(bundle, str(binding.get("concept_path")), "binding concept")
    concept_text = concept.read_text(encoding="utf-8")
    if record["body"] not in concept_text or record["record_sha256"] not in concept_text or text not in concept_text:
        raise EvaluationError(f"binding concept does not retain exact record/text identity: {claim_id}")


def _validate_expected_binding(binding: Mapping[str, Any], evidence: Mapping[str, Any]) -> None:
    expected_pages = sorted(int(row["locator"].removeprefix("PDF-page-")) for row in evidence["paper_evidence"])
    if (
        binding.get("record_id") != evidence.get("claim_id")
        or binding.get("paper_id") != evidence.get("paper_id")
        or binding.get("authoritative_text") != evidence.get("interpretation")
        or binding.get("authoritative_text_sha256") != evidence.get("interpretation_sha256")
        or binding.get("citation_pages") != expected_pages
        or binding.get("locator_tokens") != [f"PDF-page-{page}" for page in expected_pages]
    ):
        raise EvaluationError(f"returned binding differs from revalidated hard truth: {evidence.get('claim_id')}")


def _adaptive_ids(pack: Mapping[str, Any], bindings: Mapping[str, Mapping[str, Any]]) -> set[str]:
    adaptive = _exact(
        pack.get("adaptive"),
        {
            "schema_version", "status", "authoritative", "discovery_only", "query", "algorithm",
            "top_k", "per_facet", "maximum_facets", "facet_count", "unique_candidate_claims",
            "primary", "coverage_facets", "coverage_contract",
        },
        "adaptive coverage pack",
    )
    primary = adaptive.get("primary")
    facets = adaptive.get("coverage_facets")
    if not isinstance(primary, dict) or not isinstance(primary.get("ranked_bindings"), list) or not isinstance(facets, list):
        raise EvaluationError("adaptive coverage pack omits primary or facet candidates")
    identifiers: set[str] = set()
    for rank, row in enumerate(primary["ranked_bindings"], 1):
        claim_id = row.get("record_id") if isinstance(row, dict) else None
        binding = bindings.get(str(claim_id))
        if binding is None or row.get("rank") != rank:
            raise EvaluationError("adaptive primary contains an unknown or mis-ranked binding")
        for field in (
            "binding_id", "source_id", "record_id", "record_sha256", "concept_id", "concept_type",
            "concept_path", "source_path", "paper_id", "review_state", "locator_tokens",
            "citation_pages", "evidence_paths", "authoritative_text", "authoritative_text_sha256",
        ):
            if row.get(field) != binding.get(field):
                raise EvaluationError(f"adaptive primary binding field differs: {claim_id} {field}")
        identifiers.add(str(claim_id))
    for facet in facets:
        if not isinstance(facet, dict) or set(facet) != {"facet", "returned", "candidates"}:
            raise EvaluationError("adaptive facet row has an open or incomplete schema")
        candidates = facet["candidates"]
        if not isinstance(candidates, list) or facet["returned"] != len(candidates):
            raise EvaluationError("adaptive facet returned count differs")
        for rank, row in enumerate(candidates, 1):
            claim_id = row.get("claim_id") if isinstance(row, dict) else None
            binding = bindings.get(str(claim_id))
            expected = {
                "rank": rank,
                "claim_id": claim_id,
                "paper_id": binding.get("paper_id") if binding else None,
                "authoritative_text": binding.get("authoritative_text") if binding else None,
                "concept_path": binding.get("concept_path") if binding else None,
                "source_path": binding.get("source_path") if binding else None,
                "locators": sorted(set(binding.get("locator_tokens", []))) if binding else [],
                "citation_pages": sorted(set(binding.get("citation_pages", []))) if binding else [],
            }
            if row != expected:
                raise EvaluationError(f"adaptive facet candidate differs from exact binding: {claim_id}")
            identifiers.add(str(claim_id))
    if adaptive.get("unique_candidate_claims") != len(identifiers):
        raise EvaluationError("adaptive unique candidate count differs")
    return identifiers


def _discovery_route_ids(
    pack: Mapping[str, Any],
    bindings: Mapping[str, Mapping[str, Any]],
    reviewed_claim_ids: set[str],
    *,
    route: str,
    rows_key: str,
    per_facet_gate: str,
) -> set[str]:
    route_rows = pack.get(rows_key)
    if not isinstance(route_rows, list):
        raise EvaluationError(f"ensemble {route} queries must be an array")
    identifiers: set[str] = set()
    maximum_per_facet = pack["gates"][per_facet_gate]
    for row in route_rows:
        if not isinstance(row, dict) or set(row) != {"query_kind", "facet", "returned", "candidates"}:
            raise EvaluationError(f"{route} query row has an open or incomplete schema")
        candidates = row["candidates"]
        if not isinstance(candidates, list) or row["returned"] != len(candidates) or len(candidates) > maximum_per_facet:
            raise EvaluationError(f"{route} query count exceeds or differs from its gate")
        previous_rank = 0
        for rank, candidate in enumerate(candidates, 1):
            claim_id = candidate.get("claim_id") if isinstance(candidate, dict) else None
            binding = bindings.get(str(claim_id))
            if claim_id not in reviewed_claim_ids:
                raise EvaluationError(f"{route} candidate is not a reviewed bound claim: {claim_id}")
            retained_rank = candidate.get("rank") if isinstance(candidate, dict) else None
            if (
                isinstance(retained_rank, bool)
                or not isinstance(retained_rank, int)
                or retained_rank < rank
                or retained_rank <= previous_rank
            ):
                raise EvaluationError(f"{route} candidate has an invalid retained rank: {claim_id}")
            previous_rank = retained_rank
            score = candidate.get("score") if isinstance(candidate, dict) else None
            if (
                isinstance(score, bool)
                or not isinstance(score, (int, float))
                or not math.isfinite(float(score))
            ):
                raise EvaluationError(f"{route} candidate has a non-finite score: {claim_id}")
            expected = {
                "rank": retained_rank,
                "claim_id": claim_id,
                "paper_id": binding.get("paper_id") if binding else None,
                "score": score,
                "concept_path": binding.get("concept_path") if binding else None,
                "source_path": binding.get("source_path") if binding else None,
                "locators": sorted(set(binding.get("locator_tokens", []))) if binding else [],
                "citation_pages": sorted(set(binding.get("citation_pages", []))) if binding else [],
                "authoritative_text": binding.get("authoritative_text") if binding else None,
                "authoritative_text_sha256": binding.get("authoritative_text_sha256") if binding else None,
                "review_state": "reviewed",
            }
            if candidate != expected or claim_id in identifiers:
                raise EvaluationError(f"{route} candidate differs from exact unique binding: {claim_id}")
            identifiers.add(str(claim_id))
    return identifiers


def _graph_ids(
    pack: Mapping[str, Any],
    bindings: Mapping[str, Mapping[str, Any]],
    reviewed_claim_ids: set[str],
) -> set[str]:
    return _discovery_route_ids(
        pack,
        bindings,
        reviewed_claim_ids,
        route="graph",
        rows_key="graph_queries",
        per_facet_gate="maximum_graph_claims_per_facet",
    )


def _embedding_ids(
    pack: Mapping[str, Any],
    bindings: Mapping[str, Mapping[str, Any]],
    reviewed_claim_ids: set[str],
) -> set[str]:
    return _discovery_route_ids(
        pack,
        bindings,
        reviewed_claim_ids,
        route="embedding",
        rows_key="embedding_queries",
        per_facet_gate="maximum_embedding_claims_per_facet",
    )


def _route_overlaps(routes: Mapping[str, set[str]]) -> dict[str, int]:
    adaptive = routes["adaptive"]
    graph = routes["graph"]
    embedding = routes["embedding"]
    return {
        "adaptive_graph": len(adaptive & graph),
        "adaptive_embedding": len(adaptive & embedding),
        "graph_embedding": len(graph & embedding),
        "all_three": len(adaptive & graph & embedding),
    }


def _embedding_route_binding(
    snapshot: Any,
    ensemble_index: Mapping[str, Any],
    plan: Mapping[str, Any],
) -> dict[str, Any]:
    embedding_plan = plan.get("embedding")
    if not isinstance(embedding_plan, dict):
        raise EvaluationError("ensemble plan has no embedding component plan")
    embedding_index = snapshot.embedding.index
    embedding_hashes = snapshot.embedding.hashes
    plan_digest = _canonical_sha(embedding_plan)
    if embedding_index.get("retrieval_plan_sha256") != plan_digest:
        raise EvaluationError("embedding index differs from the exact component plan")
    component = ensemble_index.get("components", {}).get("embedding")
    component_index = component.get("index") if isinstance(component, dict) else None
    if (
        not isinstance(component_index, dict)
        or component_index.get("path") != "retrieval/index.json"
        or component_index.get("sha256") != embedding_hashes.get("index_sha256")
    ):
        raise EvaluationError("ensemble index does not bind the live embedding index")
    declared = embedding_plan.get("embedding")
    live = embedding_index.get("embedding")
    fields = ("provider", "model_id", "revision", "dimension", "normalize")
    if not isinstance(declared, dict) or not isinstance(live, Mapping) or any(
        declared.get(field) != live.get(field) for field in fields
    ):
        raise EvaluationError("embedding provider/model declaration differs from the live index")
    return {
        "provider": live["provider"],
        "model_id": live["model_id"],
        "revision": live["revision"],
        "dimension": live["dimension"],
        "normalize": live["normalize"],
        "retrieval_plan_sha256": plan_digest,
        "index_sha256": embedding_hashes["index_sha256"],
        "chunks_sha256": embedding_hashes["chunks_sha256"],
        "embeddings_sha256": embedding_hashes["embeddings_sha256"],
    }


def _group_rows(groups: Any, route_ids: Mapping[str, set[str]]) -> list[dict[str, Any]]:
    if not isinstance(groups, list):
        raise EvaluationError("ground-truth option groups must be an array")
    rows: list[dict[str, Any]] = []
    for group in groups:
        _exact(group, {"id", "statement", "evidence_claim_ids"}, "ground-truth option group")
        options = group["evidence_claim_ids"]
        if not isinstance(options, list) or not options or any(not isinstance(item, str) for item in options):
            raise EvaluationError("ground-truth option group has invalid claim IDs")
        option_set = set(options)
        rows.append(
            {
                "id": group["id"],
                "statement": group["statement"],
                "claim_options": options,
                **{
                    f"{route}_matches": sorted(route_ids[route] & option_set)
                    for route in ROUTES
                },
                **{
                    f"{route}_covered": bool(route_ids[route] & option_set)
                    for route in ROUTES
                },
            }
        )
    return rows


def _route_metrics(route_ids: set[str], groups: Sequence[Mapping[str, Any]], expected_ids: set[str]) -> dict[str, float]:
    return {
        "evidence_claim_recall": len(route_ids & expected_ids) / len(expected_ids) if expected_ids else 1.0,
        "option_group_coverage": mean(float(bool(route_ids & set(group["claim_options"]))) for group in groups),
    }


def _marginal_group_counts(groups: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    return {
        "graph_over_adaptive": sum(
            int(group["graph_covered"] and not group["adaptive_covered"])
            for group in groups
        ),
        "embedding_over_adaptive": sum(
            int(group["embedding_covered"] and not group["adaptive_covered"])
            for group in groups
        ),
        "embedding_over_adaptive_graph": sum(
            int(
                group["embedding_covered"]
                and not group["adaptive_covered"]
                and not group["graph_covered"]
            )
            for group in groups
        ),
    }


def _leaked_question_ids(skill_root: Path, identifiers: Iterable[str]) -> list[str]:
    needles = {identifier: identifier.encode("utf-8") for identifier in identifiers}
    leaked: set[str] = set()
    for path in sorted(skill_root.rglob("*")):
        if not path.is_file() or path.suffix.lower() in {".pyc", ".pyo"} or "__pycache__" in path.parts:
            continue
        content = path.read_bytes()
        leaked.update(identifier for identifier, needle in needles.items() if needle in content)
    return sorted(leaked)


def _stats(values: Sequence[float | int]) -> dict[str, float | int]:
    return {"mean": statistics.fmean(values), "minimum": min(values), "maximum": max(values)}


def _validate_reviewed_truth(
    frozen: Sequence[Mapping[str, Any]],
    reviewed: Sequence[Mapping[str, Any]],
) -> None:
    """Require a question-identical, option-superset answer correction."""

    if len(frozen) != 10 or len(reviewed) != len(frozen):
        raise EvaluationError("reviewed answer ground truth must contain the frozen hard ten")
    immutable_ground_truth_keys = {
        "required_paper_ids",
        "required_source_ids",
        "derivation",
        "acceptable_variants",
    }
    for parent, child in zip(frozen, reviewed, strict=True):
        if (
            child.get("id") != parent.get("id")
            or child.get("question") != parent.get("question")
            or child.get("schema_version") != parent.get("schema_version")
            or child.get("corpus_inventory") != parent.get("corpus_inventory")
        ):
            raise EvaluationError("reviewed answer ground truth changed frozen question content")
        parent_contract = parent.get("ground_truth")
        child_contract = child.get("ground_truth")
        if not isinstance(parent_contract, Mapping) or not isinstance(child_contract, Mapping):
            raise EvaluationError("reviewed answer ground truth has no closed contract")
        for key in immutable_ground_truth_keys:
            if child_contract.get(key) != parent_contract.get(key):
                raise EvaluationError(f"reviewed answer ground truth changed {key}")
        for section in ("answer_claims", "important_negatives"):
            parent_rows = parent_contract.get(section)
            child_rows = child_contract.get(section)
            if not isinstance(parent_rows, list) or not isinstance(child_rows, list):
                raise EvaluationError(f"reviewed answer ground truth has invalid {section}")
            if [(row.get("id"), row.get("statement")) for row in child_rows] != [
                (row.get("id"), row.get("statement")) for row in parent_rows
            ]:
                raise EvaluationError(f"reviewed answer ground truth changed {section} semantics")
            for parent_row, child_row in zip(parent_rows, child_rows, strict=True):
                parent_options = parent_row.get("evidence_claim_ids")
                child_options = child_row.get("evidence_claim_ids")
                if (
                    not isinstance(parent_options, list)
                    or not isinstance(child_options, list)
                    or len(child_options) != len(set(child_options))
                    or not set(parent_options).issubset(child_options)
                ):
                    raise EvaluationError(
                        f"reviewed answer ground truth is not an option superset: {child_row.get('id')}"
                    )
        parent_evidence = {
            row.get("claim_id"): row for row in parent.get("authoritative_evidence", [])
        }
        child_evidence = {
            row.get("claim_id"): row for row in child.get("authoritative_evidence", [])
        }
        if len(child_evidence) != len(child.get("authoritative_evidence", [])):
            raise EvaluationError("reviewed answer ground truth duplicates authoritative evidence")
        if any(child_evidence.get(claim_id) != row for claim_id, row in parent_evidence.items()):
            raise EvaluationError("reviewed answer ground truth changed parent evidence objects")


def _load_reviewed_answer_benchmark(
    *,
    repo: Path,
    manifest_path: Path,
    ground_truth_path: Path,
    parent_manifest: Mapping[str, Any],
    frozen_questions: Sequence[Mapping[str, Any]],
    frozen_truth: Sequence[Mapping[str, Any]],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Validate the closed reviewed-answer manifest and its exact ground truth."""

    manifest = load_json(manifest_path)
    _exact(
        manifest,
        {
            "schema_version", "benchmark_id", "status", "frozen_on",
            "mutation_policy", "parent_frozen_benchmark", "amendments",
            "generator", "cohorts", "invariants", "audit_summary",
        },
        "reviewed answer benchmark manifest",
    )
    if (
        manifest["schema_version"] != REVIEWED_ANSWER_BENCHMARK_SCHEMA
        or manifest["status"] != "frozen"
        or manifest["benchmark_id"]
        != "semantic-okf-ensemble-reviewed-answer-40-plus-hard10-v1"
        or not isinstance(manifest["frozen_on"], str)
        or not isinstance(manifest["mutation_policy"], str)
        or not manifest["mutation_policy"]
    ):
        raise EvaluationError("reviewed answer benchmark schema or status differs")
    parent = _exact(
        manifest["parent_frozen_benchmark"],
        {"path", "sha256", "benchmark_id"},
        "reviewed answer parent benchmark",
    )
    expected_parent = repo / "evaluations/semantic-okf-adaptive-evolution/frozen-benchmark.json"
    if (
        _safe_join(repo, parent["path"], "reviewed answer parent benchmark") != expected_parent
        or parent["sha256"] != FROZEN_MANIFEST_SHA256
        or parent["benchmark_id"] != parent_manifest.get("benchmark_id")
    ):
        raise EvaluationError("reviewed answer parent benchmark binding differs")
    for key in ("amendments", "generator"):
        binding = _exact(manifest[key], {"path", "sha256"}, f"reviewed answer {key}")
        path = _safe_join(repo, binding["path"], f"reviewed answer {key}")
        if sha256(path) != binding["sha256"]:
            raise EvaluationError(f"reviewed answer {key} hash differs")
    cohorts = _exact(
        manifest["cohorts"],
        {"hard_ground_truth", "hard_questions", "retrieval_questions"},
        "reviewed answer cohorts",
    )
    for key, expected_count in (
        ("hard_ground_truth", 10),
        ("hard_questions", 10),
        ("retrieval_questions", 40),
    ):
        binding = _exact(
            cohorts[key],
            {"path", "sha256", "count", "ordered_ids"},
            f"reviewed answer {key}",
        )
        path = _safe_join(repo, binding["path"], f"reviewed answer {key}")
        if binding["count"] != expected_count or sha256(path) != binding["sha256"]:
            raise EvaluationError(f"reviewed answer {key} binding differs")
    hard_rows = load_jsonl(
        _safe_join(repo, cohorts["hard_questions"]["path"], "reviewed hard questions")
    )
    retrieval_rows = load_jsonl(
        _safe_join(
            repo,
            cohorts["retrieval_questions"]["path"],
            "reviewed retrieval questions",
        )
    )
    if hard_rows != list(frozen_questions[-10:]) or retrieval_rows != list(frozen_questions):
        raise EvaluationError("reviewed answer benchmark changed question or qrel content")
    invariants = _exact(
        manifest["invariants"],
        {
            "parent_files_unchanged", "question_content_identity", "qrel_identity",
            "append_only_option_sets", "authoritative_evidence_derivation",
            "or_option_semantics",
        },
        "reviewed answer invariants",
    )
    if not all(isinstance(value, str) and value for value in invariants.values()):
        raise EvaluationError("reviewed answer invariants must be nonempty declarations")
    audit = _exact(
        manifest["audit_summary"],
        {
            "questions", "atomic_answer_claims", "important_negatives",
            "parent_expected_id_links", "appended_atomic_option_links",
            "appended_negative_option_links", "reviewed_expected_id_links",
            "parent_unique_expected_claim_ids", "added_unique_claim_ids",
            "reviewed_unique_expected_claim_ids",
            "parent_authoritative_evidence_objects",
            "added_authoritative_evidence_objects",
            "reviewed_authoritative_evidence_objects",
            "rejected_close_alternatives",
        },
        "reviewed answer audit summary",
    )
    if any(isinstance(value, bool) or not isinstance(value, int) or value < 0 for value in audit.values()):
        raise EvaluationError("reviewed answer audit summary counts must be nonnegative integers")
    if audit["questions"] != 10 or audit["atomic_answer_claims"] != 44 or audit["important_negatives"] != 13:
        raise EvaluationError("reviewed answer audit summary benchmark counts differ")
    truth_binding = cohorts["hard_ground_truth"]
    bound_truth_path = _safe_join(
        repo, truth_binding["path"], "reviewed answer hard ground truth"
    )
    if bound_truth_path != ground_truth_path or sha256(ground_truth_path) != truth_binding["sha256"]:
        raise EvaluationError("reviewed answer ground-truth path differs")
    truths = load_jsonl(ground_truth_path)
    if truth_binding["ordered_ids"] != [row.get("id") for row in truths]:
        raise EvaluationError("reviewed answer ground-truth order differs")
    _validate_reviewed_truth(frozen_truth, truths)
    return manifest, truths


def evaluate(args: argparse.Namespace) -> dict[str, Any]:
    repo = args.repo_root.resolve(strict=True)
    bundle = args.bundle.resolve(strict=True)
    runtime_path = args.runtime.resolve(strict=True)
    plan_path = args.plan.resolve(strict=True)
    inventory_path = args.inventory.resolve(strict=True)
    corpus_root = args.corpus_root.resolve(strict=True)
    evaluator_path = Path(__file__).resolve(strict=True)
    parent_manifest, questions, frozen_truths = benchmark_rows()
    if parent_manifest.get("manifest_sha256") not in {None, FROZEN_MANIFEST_SHA256}:
        raise EvaluationError("frozen benchmark validator returned a different identity")
    hard_questions = questions[-10:]
    answer_manifest_path = args.answer_benchmark_manifest.resolve(strict=True)
    ground_truth_path = args.ground_truth.resolve(strict=True)
    manifest, truths = _load_reviewed_answer_benchmark(
        repo=repo,
        manifest_path=answer_manifest_path,
        ground_truth_path=ground_truth_path,
        parent_manifest=parent_manifest,
        frozen_questions=questions,
        frozen_truth=frozen_truths,
    )
    if [row["id"] for row in hard_questions] != [row["id"] for row in truths]:
        raise EvaluationError("hard question and ground-truth IDs differ")

    truth_validator = module_from_path(
        "semantic_okf_ensemble_hard_truth_validator",
        repo / "evaluations/semantic-okf-classical/scripts/validate_hard_ground_truth.py",
    )
    for truth in truths:
        truth_validator.validate_ground_truth_record(repo, truth)

    plan = load_json(plan_path)
    inventory_payload = load_json(inventory_path)
    inventory = _source_inventory(inventory_path, corpus_root)
    source_rows = _claim_sources(corpus_root, inventory)
    skill_root = runtime_path.parent.parent
    leaked_ids = _leaked_question_ids(skill_root, [row["id"] for row in hard_questions])
    if leaked_ids:
        raise EvaluationError(f"consult skill contains frozen hard question IDs: {leaked_ids}")

    scripts = runtime_path.parent
    if str(scripts) not in sys.path:
        sys.path.insert(0, str(scripts))
    runtime = module_from_path("semantic_okf_ensemble_coverage_runtime", runtime_path)
    before = _tree(bundle)
    snapshot = runtime.load_snapshot(bundle, deep_validation=True)
    index = snapshot.index
    if index.get("plan") != plan or index.get("ensemble_plan_sha256") != _canonical_sha(plan):
        raise EvaluationError("published bundle is not bound to the requested final ensemble plan")
    if index.get("core", {}).get("tree_sha256") != inventory_payload.get("baseline", {}).get("bundle_tree_sha256"):
        raise EvaluationError("published bundle core differs from the frozen benchmark")

    bindings = {row["record_id"]: row for row in snapshot.adaptive.answer_bindings}
    if len(bindings) != len(snapshot.adaptive.answer_bindings):
        raise EvaluationError("answer bindings contain duplicate claim IDs")
    semantic_rows = load_jsonl(bundle / "semantic/records.jsonl")
    semantic_records = {
        row["record_id"]: row for row in semantic_rows if row.get("record_id") in bindings
    }
    source_manifest = load_json(bundle / "semantic/source-manifest.json")
    semantic_sources = {row["id"]: row for row in source_manifest["sources"]}
    reviewed_graph_claim_ids = {
        entity["authoritative_identity"]["record_id"]
        for entity in snapshot.graph.entities
        if entity.get("entity_type") == "claim"
        and entity.get("review_state") == "reviewed"
        and isinstance(entity.get("authoritative_identity"), dict)
        and isinstance(entity["authoritative_identity"].get("record_id"), str)
    }
    reviewed_binding_ids = {
        claim_id
        for claim_id, binding in bindings.items()
        if binding.get("review_state") == "reviewed"
    }
    if reviewed_binding_ids != set(bindings):
        raise EvaluationError("answer-binding set contains a non-reviewed claim")
    embedding_route_binding = _embedding_route_binding(snapshot, index, plan)

    quality_gates = plan.get("quality_gates")
    if not isinstance(quality_gates, dict):
        raise EvaluationError("ensemble plan has no quality-gate object")
    if (
        quality_gates.get("maximum_graph_claims_per_facet"),
        quality_gates.get("maximum_graph_claims_total"),
    ) != GRAPH_LIMITS:
        raise EvaluationError("published graph coverage limits differ from 8 per facet / 80 total")
    if (
        quality_gates.get("maximum_embedding_claims_per_facet"),
        quality_gates.get("maximum_embedding_claims_total"),
    ) != EMBEDDING_LIMITS:
        raise EvaluationError("published semantic coverage limits differ from 20 per facet / 240 total")

    validated_bindings: set[str] = set()
    per_question: list[dict[str, Any]] = []
    latencies: list[float] = []
    for question, truth in zip(hard_questions, truths, strict=True):
        packs: list[dict[str, Any]] = []
        for _ in range(args.repetitions):
            started = time.perf_counter()
            pack = runtime.build_coverage_pack(
                snapshot,
                question["question"],
                args.top_k,
                args.per_facet,
                args.maximum_facets,
            )
            latencies.append((time.perf_counter() - started) * 1000.0)
            packs.append(pack)
        hashes = [_canonical_sha(pack) for pack in packs]
        if len(set(hashes)) != 1 or any(pack != packs[0] for pack in packs[1:]):
            raise EvaluationError(f"coverage pack is nondeterministic: {question['id']}")
        pack = _exact(
            packs[0],
            {
                "schema_version", "status", "authoritative", "discovery_only", "query", "algorithm",
                "top_k", "per_facet", "maximum_facets", "adaptive", "graph_queries",
                "embedding_queries", "adaptive_candidate_claims", "graph_candidate_claims",
                "embedding_candidate_claims", "unique_candidate_claims", "union_claim_ids",
                "gates", "snapshot", "coverage_contract",
            },
            "ensemble coverage pack",
        )
        gates = _exact(
            pack["gates"],
            {
                "reviewed_graph_claims_only", "reviewed_embedding_claims_only",
                "candidate_edge_weight", "maximum_graph_claims_per_facet",
                "maximum_graph_claims_total", "maximum_embedding_claims_per_facet",
                "maximum_embedding_claims_total", "exact_answer_bindings", "limits_passed",
            },
            "ensemble coverage gates",
        )
        pack_snapshot = _exact(
            pack["snapshot"],
            {"core_tree_sha256", "ensemble_index_sha256"},
            "ensemble coverage snapshot binding",
        )
        coverage_contract = _exact(
            pack["coverage_contract"],
            {
                "graph_role", "embedding_role", "candidate_edges_establish_facts",
                "authoritative_verification_required", "facet_status_required_before_finalization",
                "finalizer",
            },
            "ensemble coverage contract",
        )
        if (
            pack["schema_version"] != runtime.SCHEMA_VERSION
            or pack["status"] != "pass"
            or pack["authoritative"] is not False
            or pack["discovery_only"] is not True
            or pack["algorithm"] != COVERAGE_ALGORITHM
            or pack["query"] != question["question"]
            or (pack["top_k"], pack["per_facet"], pack["maximum_facets"])
            != (args.top_k, args.per_facet, args.maximum_facets)
            or pack_snapshot["core_tree_sha256"] != index["core"]["tree_sha256"]
            or pack_snapshot["ensemble_index_sha256"] != snapshot.index_sha256
            or gates["reviewed_graph_claims_only"] is not True
            or gates["reviewed_embedding_claims_only"] is not True
            or gates["candidate_edge_weight"] != 0.0
            or gates["exact_answer_bindings"] is not True
            or coverage_contract["graph_role"] != "candidate discovery only"
            or coverage_contract["embedding_role"]
            != (
                "reviewed claim candidate discovery only; "
                "adaptive-paper-conditioned-claim-diversification-v1"
            )
            or coverage_contract["candidate_edges_establish_facts"] is not False
            or coverage_contract["authoritative_verification_required"] is not True
            or coverage_contract["facet_status_required_before_finalization"] is not True
            or coverage_contract["finalizer"] != runtime.ANSWER_GATE_ID
            or (
                gates["maximum_graph_claims_per_facet"],
                gates["maximum_graph_claims_total"],
            ) != GRAPH_LIMITS
            or (
                gates["maximum_embedding_claims_per_facet"],
                gates["maximum_embedding_claims_total"],
            ) != EMBEDDING_LIMITS
        ):
            raise EvaluationError(f"coverage pack contract differs: {question['id']}")
        adaptive_ids = _adaptive_ids(pack, bindings)
        graph_ids = _graph_ids(pack, bindings, reviewed_graph_claim_ids)
        embedding_ids = _embedding_ids(pack, bindings, reviewed_binding_ids)
        union_ids = set(pack["union_claim_ids"])
        route_ids = {
            "adaptive": adaptive_ids,
            "graph": graph_ids,
            "embedding": embedding_ids,
            "union": union_ids,
        }
        graph_signature = [
            (row["query_kind"], row["facet"])
            for row in pack["graph_queries"]
        ]
        embedding_signature = [
            (row["query_kind"], row["facet"])
            for row in pack["embedding_queries"]
        ]
        expected_facets = [question["question"]]
        expected_facets.extend(
            row["facet"]
            for row in pack["adaptive"]["coverage_facets"]
            if row["facet"] not in expected_facets
        )
        expected_signature = [
            ("full" if number == 0 else "facet", facet)
            for number, facet in enumerate(expected_facets)
        ]
        if (
            pack["union_claim_ids"] != sorted(union_ids)
            or union_ids != adaptive_ids | graph_ids | embedding_ids
            or pack["adaptive_candidate_claims"] != len(adaptive_ids)
            or pack["graph_candidate_claims"] != len(graph_ids)
            or pack["embedding_candidate_claims"] != len(embedding_ids)
            or pack["unique_candidate_claims"] != len(union_ids)
            or len(graph_ids) > gates["maximum_graph_claims_total"]
            or len(embedding_ids) > gates["maximum_embedding_claims_total"]
            or graph_signature != expected_signature
            or embedding_signature != expected_signature
            or gates["limits_passed"] is not True
        ):
            raise EvaluationError(f"coverage candidate-set gates differ: {question['id']}")
        for claim_id in sorted(union_ids):
            if claim_id not in validated_bindings:
                _validate_binding(
                    bindings[claim_id],
                    bundle=bundle,
                    corpus_root=corpus_root,
                    inventory=inventory,
                    source_rows=source_rows,
                    semantic_records=semantic_records,
                    semantic_sources=semantic_sources,
                )
                validated_bindings.add(claim_id)

        evidence_by_id = {row["claim_id"]: row for row in truth["authoritative_evidence"]}
        for claim_id in sorted(union_ids & set(evidence_by_id)):
            _validate_expected_binding(bindings[claim_id], evidence_by_id[claim_id])
        contract = truth["ground_truth"]
        answer_groups = _group_rows(contract["answer_claims"], route_ids)
        negative_groups = _group_rows(contract["important_negatives"], route_ids)
        answer_ids = {
            claim_id for group in answer_groups for claim_id in group["claim_options"]
        }
        negative_ids = {
            claim_id for group in negative_groups for claim_id in group["claim_options"]
        }
        required_papers = set(contract["required_paper_ids"])
        route_papers = {
            route: {bindings[claim_id]["paper_id"] for claim_id in identifiers}
            for route, identifiers in route_ids.items()
        }
        per_question.append(
            {
                "id": question["id"],
                "coverage_pack_sha256": hashes[0],
                "candidate_counts": {
                    route: len(route_ids[route]) for route in ROUTES
                },
                "candidate_overlaps": _route_overlaps(route_ids),
                "candidate_set_sha256": {
                    route: _canonical_sha(sorted(route_ids[route])) for route in ROUTES
                },
                "answer_claims": {
                    **{
                        route: _route_metrics(route_ids[route], answer_groups, answer_ids)
                        for route in ROUTES
                    },
                    "marginal_groups": _marginal_group_counts(answer_groups),
                    "groups": answer_groups,
                },
                "important_negatives": {
                    **{
                        route: _route_metrics(route_ids[route], negative_groups, negative_ids)
                        for route in ROUTES
                    },
                    "marginal_groups": _marginal_group_counts(negative_groups),
                    "groups": negative_groups,
                },
                "required_papers": {
                    "expected": sorted(required_papers),
                    **{
                        f"{route}_matches": sorted(route_papers[route] & required_papers)
                        for route in ROUTES
                    },
                    **{
                        f"{route}_coverage": len(route_papers[route] & required_papers)
                        / len(required_papers)
                        for route in ROUTES
                    },
                },
            }
        )
    after = _tree(bundle)
    read_only = before == after
    if not read_only:
        raise EvaluationError("coverage evaluation modified the published bundle")

    def macro(section: str, route: str, metric: str) -> float:
        return mean(float(row[section][route][metric]) for row in per_question)

    metrics = {
        "answer_claims": {
            route: {
                "evidence_claim_recall": macro("answer_claims", route, "evidence_claim_recall"),
                "option_group_coverage": macro("answer_claims", route, "option_group_coverage"),
            }
            for route in ROUTES
        },
        "important_negatives": {
            route: {
                "evidence_claim_recall": macro("important_negatives", route, "evidence_claim_recall"),
                "option_group_coverage": macro("important_negatives", route, "option_group_coverage"),
            }
            for route in ROUTES
        },
        "required_paper_coverage": {
            route: mean(float(row["required_papers"][f"{route}_coverage"]) for row in per_question)
            for route in ROUTES
        },
        "marginal_groups": {
            section: {
                name: sum(
                    row[section]["marginal_groups"][name] for row in per_question
                )
                for name in (
                    "graph_over_adaptive",
                    "embedding_over_adaptive",
                    "embedding_over_adaptive_graph",
                )
            }
            for section in ("answer_claims", "important_negatives")
        },
        "group_counts": {
            section: {
                "total": sum(len(row[section]["groups"]) for row in per_question),
                **{
                    f"{route}_covered": sum(
                        int(group[f"{route}_covered"])
                        for row in per_question
                        for group in row[section]["groups"]
                    )
                    for route in ROUTES
                },
            }
            for section in ("answer_claims", "important_negatives")
        },
        "candidate_claims": {
            route: _stats([row["candidate_counts"][route] for row in per_question])
            for route in ROUTES
        },
        "candidate_overlaps": {
            overlap: _stats(
                [row["candidate_overlaps"][overlap] for row in per_question]
            )
            for overlap in OVERLAPS
        },
        "latency_ms": {
            "mean": statistics.fmean(latencies),
            "median": statistics.median(latencies),
            "p95": percentile(latencies, 0.95),
            "maximum": max(latencies),
        },
        "evidence_validation": {
            "unique_returned_bindings": len(validated_bindings),
            "valid_unique_bindings": len(validated_bindings),
            "ratio": 1.0,
        },
    }
    hard_gates = {
        "frozen_benchmark_valid": True,
        "ground_truth_locators_and_hashes_valid": True,
        "exact_final_plan_binding": True,
        "deep_snapshot_validation": snapshot.deep_validation is True,
        "deterministic_three_repetitions": True,
        "read_only": read_only,
        "question_id_isolation": not leaked_ids,
        "closed_candidate_sets": True,
        "reviewed_graph_claims_only": True,
        "reviewed_embedding_claims_only": True,
        "candidate_edge_weight_zero": quality_gates["candidate_edge_weight"] == 0.0,
        "embedding_provider_plan_index_bound": True,
        "graph_limits_declared": (
            quality_gates["maximum_graph_claims_per_facet"],
            quality_gates["maximum_graph_claims_total"],
        ) == GRAPH_LIMITS,
        "graph_limits_passed": True,
        "semantic_limits_declared": (
            quality_gates["maximum_embedding_claims_per_facet"],
            quality_gates["maximum_embedding_claims_total"],
        ) == EMBEDDING_LIMITS,
        "semantic_limits_passed": True,
        "exact_binding_validation": True,
    }
    issues = sorted(name for name, passed in hard_gates.items() if passed is not True)
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "pass" if not issues else "fail",
        "candidate": args.candidate,
        "benchmark": {
            "id": manifest["benchmark_id"],
            "manifest_sha256": sha256(answer_manifest_path),
            "hard_questions": len(hard_questions),
        },
        "protocol": {
            "primary_top_k": args.top_k,
            "per_facet": args.per_facet,
            "maximum_facets": args.maximum_facets,
            "repetitions_per_question": args.repetitions,
            "coverage_algorithm": COVERAGE_ALGORITHM,
            "maximum_graph_claims_per_facet": GRAPH_LIMITS[0],
            "maximum_graph_claims_total": GRAPH_LIMITS[1],
            "maximum_embedding_claims_per_facet": EMBEDDING_LIMITS[0],
            "maximum_embedding_claims_total": EMBEDDING_LIMITS[1],
            "budget_warning": "The adaptive-plus-graph-plus-embedding union has a larger variable budget and is not Recall@30.",
            "option_group_rule": "A ground-truth answer or negative group is covered when any declared evidence claim is returned.",
            "aggregation_rule": "Reported coverage percentages are macro averages across the ten questions; group_counts retains unweighted totals.",
        },
        "inputs": {
            "bundle": _repository_path(repo, bundle, "bundle"),
            "bundle_tree_sha256": _tree_sha(bundle),
            "ensemble_index_sha256": snapshot.index_sha256,
            "core_tree_sha256": index["core"]["tree_sha256"],
            "plan": _repository_path(repo, plan_path, "plan"),
            "plan_sha256": sha256(plan_path),
            "plan_canonical_sha256": _canonical_sha(plan),
            "runtime": _repository_path(repo, runtime_path, "runtime"),
            "runtime_sha256": sha256(runtime_path),
            "runtime_tree_sha256": _tree_sha(skill_root),
            "embedding_route": embedding_route_binding,
            "evaluator": _repository_path(repo, evaluator_path, "evaluator"),
            "evaluator_sha256": sha256(evaluator_path),
            "inventory": _repository_path(repo, inventory_path, "inventory"),
            "inventory_sha256": sha256(inventory_path),
            "ground_truth_sha256": sha256(ground_truth_path),
            "answer_binding_count": len(bindings),
        },
        "hard_gates": hard_gates,
        "metrics": metrics,
        "questions": per_question,
        "issues": issues,
    }


def _percent(value: float) -> str:
    return f"{value:.1%}"


def validate_report(report: Any) -> None:
    """Recheck the compact report's closed machine-readable schema."""

    root = _exact(
        report,
        {
            "schema_version", "status", "candidate", "benchmark", "protocol", "inputs",
            "hard_gates", "metrics", "questions", "issues",
        },
        "coverage evaluation report",
    )
    if root["schema_version"] != SCHEMA_VERSION or root["status"] not in {"pass", "fail"}:
        raise EvaluationError("coverage evaluation report version or status differs")
    _exact(root["benchmark"], {"id", "manifest_sha256", "hard_questions"}, "report benchmark")
    _exact(
        root["protocol"],
        {
            "primary_top_k", "per_facet", "maximum_facets", "repetitions_per_question",
            "coverage_algorithm", "maximum_graph_claims_per_facet",
            "maximum_graph_claims_total", "maximum_embedding_claims_per_facet",
            "maximum_embedding_claims_total", "budget_warning", "option_group_rule",
            "aggregation_rule",
        },
        "report protocol",
    )
    if (
        root["protocol"]["coverage_algorithm"] != COVERAGE_ALGORITHM
        or (
            root["protocol"]["maximum_graph_claims_per_facet"],
            root["protocol"]["maximum_graph_claims_total"],
        ) != GRAPH_LIMITS
        or (
            root["protocol"]["maximum_embedding_claims_per_facet"],
            root["protocol"]["maximum_embedding_claims_total"],
        ) != EMBEDDING_LIMITS
    ):
        raise EvaluationError("report algorithm or route limits differ")
    _exact(
        root["inputs"],
        {
            "bundle", "bundle_tree_sha256", "ensemble_index_sha256", "core_tree_sha256",
            "plan", "plan_sha256", "plan_canonical_sha256", "runtime", "runtime_sha256",
            "runtime_tree_sha256", "embedding_route", "evaluator", "evaluator_sha256", "inventory",
            "inventory_sha256", "ground_truth_sha256", "answer_binding_count",
        },
        "report inputs",
    )
    embedding_binding = _exact(
        root["inputs"]["embedding_route"],
        {
            "provider", "model_id", "revision", "dimension", "normalize",
            "retrieval_plan_sha256", "index_sha256", "chunks_sha256", "embeddings_sha256",
        },
        "report embedding route binding",
    )
    if (
        any(
            not isinstance(embedding_binding[field], str)
            or not embedding_binding[field]
            for field in ("provider", "model_id", "revision")
        )
        or isinstance(embedding_binding["dimension"], bool)
        or not isinstance(embedding_binding["dimension"], int)
        or embedding_binding["dimension"] < 1
        or not isinstance(embedding_binding["normalize"], bool)
        or any(
            re.fullmatch(r"[0-9a-f]{64}", str(embedding_binding[field])) is None
            for field in (
                "retrieval_plan_sha256", "index_sha256", "chunks_sha256",
                "embeddings_sha256",
            )
        )
    ):
        raise EvaluationError("report embedding route binding has invalid identities")
    gate_keys = {
        "frozen_benchmark_valid", "ground_truth_locators_and_hashes_valid",
        "exact_final_plan_binding", "deep_snapshot_validation",
        "deterministic_three_repetitions", "read_only", "question_id_isolation",
        "closed_candidate_sets", "reviewed_graph_claims_only",
        "reviewed_embedding_claims_only", "candidate_edge_weight_zero",
        "embedding_provider_plan_index_bound", "graph_limits_declared", "graph_limits_passed",
        "semantic_limits_declared", "semantic_limits_passed", "exact_binding_validation",
    }
    gates = _exact(root["hard_gates"], gate_keys, "report hard gates")
    if any(not isinstance(value, bool) for value in gates.values()):
        raise EvaluationError("report hard gates must be booleans")
    _exact(
        root["metrics"],
        {
            "answer_claims", "important_negatives", "required_paper_coverage",
            "marginal_groups", "group_counts", "candidate_claims", "candidate_overlaps",
            "latency_ms", "evidence_validation",
        },
        "report metrics",
    )
    group_counts = _exact(
        root["metrics"]["group_counts"],
        {"answer_claims", "important_negatives"},
        "report group counts",
    )
    for section in group_counts.values():
        counts = _exact(
            section,
            {"total", *{f"{route}_covered" for route in ROUTES}},
            "report group-count section",
        )
        if any(isinstance(value, bool) or not isinstance(value, int) or value < 0 for value in counts.values()):
            raise EvaluationError("report group counts must be nonnegative integers")
        if any(counts[f"{route}_covered"] > counts["total"] for route in ROUTES):
            raise EvaluationError("report covered group count exceeds total")
    marginal = _exact(
        root["metrics"]["marginal_groups"],
        {"answer_claims", "important_negatives"},
        "report marginal groups",
    )
    marginal_keys = {
        "graph_over_adaptive", "embedding_over_adaptive",
        "embedding_over_adaptive_graph",
    }
    for section in marginal.values():
        values = _exact(section, marginal_keys, "report marginal-group section")
        if any(isinstance(value, bool) or not isinstance(value, int) or value < 0 for value in values.values()):
            raise EvaluationError("report marginal-group counts must be nonnegative integers")
    for metric_name in ("answer_claims", "important_negatives"):
        route_metrics = _exact(root["metrics"][metric_name], set(ROUTES), f"report {metric_name}")
        for route, values in route_metrics.items():
            closed = _exact(
                values,
                {"evidence_claim_recall", "option_group_coverage"},
                f"report {metric_name} {route}",
            )
            if any(
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not 0.0 <= float(value) <= 1.0
                for value in closed.values()
            ):
                raise EvaluationError("report coverage metrics must be in the closed unit interval")
    _exact(root["metrics"]["required_paper_coverage"], set(ROUTES), "report paper coverage")
    candidate_metrics = _exact(
        root["metrics"]["candidate_claims"], set(ROUTES), "report candidate claims"
    )
    overlap_metrics = _exact(
        root["metrics"]["candidate_overlaps"], set(OVERLAPS), "report candidate overlaps"
    )
    for label, stats in [*candidate_metrics.items(), *overlap_metrics.items()]:
        closed = _exact(stats, {"mean", "minimum", "maximum"}, f"report count stats {label}")
        if not 0 <= closed["minimum"] <= closed["mean"] <= closed["maximum"]:
            raise EvaluationError("report count statistics are unordered")
    _exact(root["metrics"]["latency_ms"], {"mean", "median", "p95", "maximum"}, "report latency")
    _exact(
        root["metrics"]["evidence_validation"],
        {"unique_returned_bindings", "valid_unique_bindings", "ratio"},
        "report evidence validation",
    )
    questions = root["questions"]
    if not isinstance(questions, list) or len(questions) != 10:
        raise EvaluationError("coverage evaluation report must contain ten question rows")
    for question in questions:
        row = _exact(
            question,
            {
                "id", "coverage_pack_sha256", "candidate_counts", "candidate_set_sha256",
                "candidate_overlaps", "answer_claims", "important_negatives", "required_papers",
            },
            "report question",
        )
        counts = _exact(row["candidate_counts"], set(ROUTES), "candidate counts")
        overlaps = _exact(row["candidate_overlaps"], set(OVERLAPS), "candidate overlaps")
        hashes = _exact(row["candidate_set_sha256"], set(ROUTES), "candidate set hashes")
        if any(isinstance(value, bool) or not isinstance(value, int) or value < 0 for value in counts.values()):
            raise EvaluationError("candidate counts must be nonnegative integers")
        if any(isinstance(value, bool) or not isinstance(value, int) or value < 0 for value in overlaps.values()):
            raise EvaluationError("candidate overlaps must be nonnegative integers")
        if counts["union"] < max(counts[route] for route in ROUTES[:-1]):
            raise EvaluationError("union candidate count is smaller than a component route")
        if any(re.fullmatch(r"[0-9a-f]{64}", str(value)) is None for value in hashes.values()):
            raise EvaluationError("candidate set hashes must be lowercase SHA-256 values")
        for section_name in ("answer_claims", "important_negatives"):
            section = _exact(
                row[section_name],
                {*ROUTES, "marginal_groups", "groups"},
                f"question {section_name}",
            )
            for route in ROUTES:
                _exact(section[route], {"evidence_claim_recall", "option_group_coverage"}, f"{section_name} {route}")
            _exact(section["marginal_groups"], marginal_keys, f"{section_name} marginal groups")
            if not isinstance(section["groups"], list):
                raise EvaluationError(f"question {section_name} groups must be an array")
            for group in section["groups"]:
                closed_group = _exact(
                    group,
                    {
                        "id", "statement", "claim_options",
                        *{f"{route}_matches" for route in ROUTES},
                        *{f"{route}_covered" for route in ROUTES},
                    },
                    f"question {section_name} group",
                )
                for route in ROUTES:
                    matches = closed_group[f"{route}_matches"]
                    covered = closed_group[f"{route}_covered"]
                    if (
                        not isinstance(matches, list)
                        or matches != sorted(set(matches))
                        or not set(matches).issubset(set(closed_group["claim_options"]))
                        or not isinstance(covered, bool)
                        or covered != bool(matches)
                    ):
                        raise EvaluationError("question group route matches/coverage differ")
        papers = _exact(
            row["required_papers"],
            {
                "expected", *{f"{route}_matches" for route in ROUTES},
                *{f"{route}_coverage" for route in ROUTES},
            },
            "question required papers",
        )
        for route in ROUTES:
            matches = papers[f"{route}_matches"]
            coverage = papers[f"{route}_coverage"]
            if (
                not isinstance(matches, list)
                or matches != sorted(set(matches))
                or isinstance(coverage, bool)
                or not isinstance(coverage, (int, float))
                or not 0.0 <= float(coverage) <= 1.0
            ):
                raise EvaluationError("question required-paper route values differ")
    expected_issues = sorted(name for name, passed in gates.items() if not passed)
    if root["issues"] != expected_issues or (root["status"] == "pass") != (not expected_issues):
        raise EvaluationError("report status/issues do not follow hard gates")


def render_markdown(report: Mapping[str, Any]) -> str:
    metrics = report["metrics"]
    answer_counts = metrics["group_counts"]["answer_claims"]
    negative_counts = metrics["group_counts"]["important_negatives"]
    marginal_answers = metrics["marginal_groups"]["answer_claims"]
    marginal_negatives = metrics["marginal_groups"]["important_negatives"]
    provider = report["inputs"]["embedding_route"]
    lines = [
        "# Definitive Multisignal Ensemble Hard-10 Coverage-Pack Evaluation",
        "",
        f"Status: **{report['status']}**. The report is bound to the frozen benchmark, exact published final plan, and pinned semantic index.",
        "",
        "This evaluates the adaptive, reviewed graph-claim, and pinned embedding-claim candidates available to answer synthesis. "
        "The gated union is variable-budget and therefore must not be labeled Recall@30.",
        "",
        "Coverage percentages below are macro averages across the ten questions, so every question has equal weight.",
        "",
        "## Route comparison",
        "",
        "| Route | Answer claim IDs | Answer groups | Negative claim IDs | Negative groups | Required papers | Mean candidates |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    labels = {
        "adaptive": "Adaptive facets",
        "graph": "Reviewed claim graph",
        "embedding": "Pinned semantic claims",
        "union": "Gated union",
    }
    for route in ROUTES:
        lines.append(
            f"| {labels[route]} | {_percent(metrics['answer_claims'][route]['evidence_claim_recall'])} | "
            f"{_percent(metrics['answer_claims'][route]['option_group_coverage'])} | "
            f"{_percent(metrics['important_negatives'][route]['evidence_claim_recall'])} | "
            f"{_percent(metrics['important_negatives'][route]['option_group_coverage'])} | "
            f"{_percent(metrics['required_paper_coverage'][route])} | "
            f"{metrics['candidate_claims'][route]['mean']:.1f} |"
        )
    overlaps = metrics["candidate_overlaps"]
    lines.extend(
        [
            "",
            "Mean candidate overlaps: "
            f"adaptive∩graph **{overlaps['adaptive_graph']['mean']:.1f}**, "
            f"adaptive∩embedding **{overlaps['adaptive_embedding']['mean']:.1f}**, "
            f"graph∩embedding **{overlaps['graph_embedding']['mean']:.1f}**, and "
            f"all three **{overlaps['all_three']['mean']:.1f}**.",
            "",
            "## Per question",
            "",
            "| Question | Adaptive/graph/embedding/union candidates | Answer groups A/G/E/U | Negative groups A/G/E/U | Papers A/G/E/U |",
            "| --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in report["questions"]:
        counts = row["candidate_counts"]
        answers = row["answer_claims"]
        negatives = row["important_negatives"]
        papers = row["required_papers"]
        lines.append(
            f"| `{row['id']}` | {counts['adaptive']}/{counts['graph']}/{counts['embedding']}/{counts['union']} | "
            f"{_percent(answers['adaptive']['option_group_coverage'])}/"
            f"{_percent(answers['graph']['option_group_coverage'])}/"
            f"{_percent(answers['embedding']['option_group_coverage'])}/"
            f"{_percent(answers['union']['option_group_coverage'])} | "
            f"{_percent(negatives['adaptive']['option_group_coverage'])}/"
            f"{_percent(negatives['graph']['option_group_coverage'])}/"
            f"{_percent(negatives['embedding']['option_group_coverage'])}/"
            f"{_percent(negatives['union']['option_group_coverage'])} | "
            f"{_percent(papers['adaptive_coverage'])}/{_percent(papers['graph_coverage'])}/"
            f"{_percent(papers['embedding_coverage'])}/"
            f"{_percent(papers['union_coverage'])} |"
        )
    missing_answers = [
        group
        for row in report["questions"]
        for group in row["answer_claims"]["groups"]
        if not group["union_covered"]
    ]
    missing_negatives = [
        group
        for row in report["questions"]
        for group in row["important_negatives"]["groups"]
        if not group["union_covered"]
    ]
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            f"Relative to adaptive facets, the graph route finds **{marginal_answers['graph_over_adaptive']}** additional answer groups and "
            f"the embedding route finds **{marginal_answers['embedding_over_adaptive']}**. Of the embedding additions, "
            f"**{marginal_answers['embedding_over_adaptive_graph']}** remain unique after adaptive and graph candidates are combined.",
            "",
            f"For important-negative groups, graph and embedding add **{marginal_negatives['graph_over_adaptive']}** and "
            f"**{marginal_negatives['embedding_over_adaptive']}** over adaptive respectively; "
            f"**{marginal_negatives['embedding_over_adaptive_graph']}** embedding additions remain unique beyond adaptive plus graph.",
            "",
            f"As raw totals, adaptive covers **{answer_counts['adaptive_covered']}/{answer_counts['total']}** answer groups, "
            f"graph covers **{answer_counts['graph_covered']}/{answer_counts['total']}**, embedding covers "
            f"**{answer_counts['embedding_covered']}/{answer_counts['total']}**, and the union covers "
            f"**{answer_counts['union_covered']}/{answer_counts['total']}**. The union covers "
            f"**{negative_counts['union_covered']}/{negative_counts['total']}** important-negative groups.",
            "",
            f"The semantic route used `{provider['provider']}` model `{provider['model_id']}` at immutable revision "
            f"`{provider['revision']}`. Its component plan, retrieval index, chunks, and embedding artifacts are hash-bound in the JSON report.",
            "",
            f"Every one of the **{metrics['evidence_validation']['unique_returned_bindings']}** distinct returned bindings passed independent "
            "record, source path, concept path, PDF-page locator, reviewed text, and SHA-256 checks. The bundle remained byte-identical.",
            "",
        ]
    )
    if missing_answers:
        lines.extend(["Uncovered answer groups:", "", *[f"- `{row['id']}`: {row['statement']}" for row in missing_answers], ""])
    else:
        lines.extend(["All answer groups are covered by the gated union.", ""])
    if missing_negatives:
        lines.extend(["Uncovered important failure conditions:", "", *[f"- `{row['id']}`: {row['statement']}" for row in missing_negatives], ""])
    else:
        lines.extend(["All important failure conditions are covered by the gated union.", ""])
    lines.extend(
        [
            "The JSON companion retains each ground-truth option group, its acceptable claim IDs, route-specific matches, "
            "candidate counts and overlaps, route-set hashes, semantic provider/index bindings, and all reproducibility gates.",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--runtime", type=Path, default=RUNTIME)
    parser.add_argument("--plan", type=Path, default=ENSEMBLE_PLAN)
    parser.add_argument("--inventory", type=Path, default=INVENTORY)
    parser.add_argument("--corpus-root", type=Path, default=CORPUS_ROOT)
    parser.add_argument("--ground-truth", type=Path, default=REVIEWED_GROUND_TRUTH)
    parser.add_argument(
        "--answer-benchmark-manifest",
        type=Path,
        default=REVIEWED_ANSWER_BENCHMARK,
    )
    parser.add_argument("--top-k", type=int, default=30)
    parser.add_argument("--per-facet", type=int, default=12)
    parser.add_argument("--maximum-facets", type=int, default=12)
    parser.add_argument("--repetitions", type=int, default=3)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-markdown", type=Path, required=True)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    if (args.top_k, args.per_facet, args.maximum_facets, args.repetitions) != (30, 12, 12, 3):
        print(json.dumps({"status": "fail", "error": "published protocol is fixed at 30/12/12/3"}), file=sys.stderr)
        return 2
    try:
        report = evaluate(args)
        validate_report(report)
        write_new(args.output_json, json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n")
        write_new(args.output_markdown, render_markdown(report))
    except (EvaluationError, OSError, UnicodeError, ValueError, TypeError, KeyError, IndexError) as exc:
        print(json.dumps({"status": "fail", "error": str(exc)}, sort_keys=True), file=sys.stderr)
        return 2
    print(
        json.dumps(
            {
                "status": report["status"],
                "candidate": report["candidate"],
                "embedding_answer_group_coverage": report["metrics"]["answer_claims"]["embedding"]["option_group_coverage"],
                "answer_group_coverage": report["metrics"]["answer_claims"]["union"]["option_group_coverage"],
                "negative_group_coverage": report["metrics"]["important_negatives"]["union"]["option_group_coverage"],
                "required_paper_coverage": report["metrics"]["required_paper_coverage"]["union"],
                "evidence_validity": report["metrics"]["evidence_validation"]["ratio"],
            },
            sort_keys=True,
        )
    )
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
