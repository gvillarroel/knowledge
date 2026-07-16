"""Validate and consult a read-only, quality-gated Semantic OKF ensemble."""

from __future__ import annotations

import hashlib
import importlib
import importlib.metadata
import json
import math
import re
import threading
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

import _adaptive_snapshot as adaptive_runtime
import _embedding_snapshot as embedding_runtime
import _entity_graph_snapshot as graph_runtime


SCHEMA_VERSION = "1.0"
GENERIC_SCHEMA_VERSION = "2.0"
SUPPORTED_SCHEMA_VERSIONS = frozenset({SCHEMA_VERSION, GENERIC_SCHEMA_VERSION})
ALGORITHM_ID = "protected-multisignal-paper-rerank-v2"
GENERIC_ALGORITHM_ID = "protected-multisignal-group-rerank-v1"
COVERAGE_ALGORITHM_ID = "bounded-reviewed-claim-multisignal-expansion-v2"
COVERAGE_BRIEF_SCHEMA_VERSION = "semantic-okf-ensemble-coverage-brief/1.0"
COVERAGE_BRIEF_ALGORITHM_ID = "reviewed-claim-priority-coverage-brief-v2"
COVERAGE_BRIEF_ORDER_ID = "persisted-idf-facet-consensus-priority-v1"
COVERAGE_BRIEF_RRF_K = 7
COVERAGE_BRIEF_ROUTE_WEIGHTS = {
    "adaptive_primary": 4.0,
    "adaptive_facet": 3.0,
    "entity_graph": 2.0,
    "embedding_hybrid": 2.0,
}
ANSWER_GATE_ID = "facet-status-exact-binding-finalizer-v1"
GENERIC_ANSWER_GATE_ID = "exact-evidence-id-verbatim-support-finalizer-v1"
GENERIC_ANSWER_BRIEF_SCHEMA_VERSION = "semantic-okf-source-answer-brief/1.0"
GENERIC_ANSWER_BRIEF_ALGORITHM_ID = "idf-facet-bounded-verbatim-support-v1"
IDENTITY_ALGORITHM_ID = "source-record-explicit-override-crosswalk-v1"
EVIDENCE_ALGORITHM_ID = "exact-record-body-evidence-v1"
EXPECTED_FILES = {"index.json", "build-report.json"}
GENERIC_EXPECTED_FILES = EXPECTED_FILES | {"identity-crosswalk.jsonl"}
PLAN_KEYS = {
    "schema_version",
    "adaptive",
    "entity_graph",
    "embedding",
    "policies",
    "quality_gates",
}
GENERIC_PLAN_KEYS = PLAN_KEYS | {"identity"}
IDENTITY_KEYS = {"default_grouping", "overrides"}
IDENTITY_OVERRIDE_KEYS = {"source_id", "record_id", "namespace", "value"}
POLICIES_KEYS = {"default", "quality", "fast", "robust"}
POLICY_KEYS = {"routes", "weights", "rrf_k", "protected_route", "promotion"}
PROMOTION_KEYS = {
    "route",
    "confirmation_routes",
    "confirmation_depth",
    "minimum_confirmations",
    "maximum_protected_rank",
}
QUALITY_GATE_KEYS = {
    "required_components",
    "protect_candidate_set",
    "require_core_parity",
    "reviewed_graph_claims_only",
    "reviewed_embedding_claims_only",
    "candidate_edge_weight",
    "maximum_graph_claims_per_facet",
    "maximum_graph_claims_total",
    "maximum_embedding_claims_per_facet",
    "maximum_embedding_claims_total",
    "require_facet_status",
    "require_exact_answer_bindings",
}
GENERIC_QUALITY_GATE_KEYS = QUALITY_GATE_KEYS | {
    "require_child_plan_parity",
    "require_total_identity_crosswalk",
    "require_component_group_parity",
    "require_exact_passage_evidence",
    "claim_only_coverage_requires_bindings",
}
ALLOWED_ROUTES = frozenset(
    {
        "adaptive",
        "graph_lexical",
        "graph_fusion",
        "bm25",
        "association",
        "embedding_hybrid",
    }
)
REQUIRED_COMPONENTS = ["adaptive", "entity_graph", "embedding"]
QUESTION_ID_RE = re.compile(
    r"(?<![a-z0-9])q\d{3}(?:[-_][a-z0-9-]+)?(?![a-z0-9])", re.IGNORECASE
)
IDENTITY_NAMESPACE_RE = re.compile(r"[a-z][a-z0-9.-]{0,63}")
HEX_64_RE = re.compile(r"[0-9a-f]{64}")
CROSSWALK_KEYS = {
    "source_id",
    "record_id",
    "record_sha256",
    "concept_id",
    "concept_type",
    "concept_path",
    "source_path",
    "group_namespace",
    "group_key",
    "group_id",
    "evidence_id",
    "locator",
    "text_sha256",
}
_EMBEDDER_CACHE: dict[str, embedding_runtime.QueryEmbedder] = {}
EMBEDDING_CLAIM_RERANK_ID = "adaptive-paper-conditioned-claim-diversification-v1"
EMBEDDING_GLOBAL_PREFIX = 6
EMBEDDING_PREFERRED_PAPERS = 3
EMBEDDING_CLAIMS_PER_PREFERRED_PAPER = 6
EMBEDDING_CANDIDATE_POOL_MULTIPLIER = 10


class SnapshotError(RuntimeError):
    """Describe an invalid ensemble snapshot or gated consultation request."""


@dataclass(frozen=True)
class EnsembleSnapshot:
    """Hold one validated ensemble and its independently loaded components."""

    root: Path
    index: dict[str, Any]
    index_sha256: str
    adaptive: adaptive_runtime.AdaptiveSnapshot
    graph: graph_runtime.EntityGraphSnapshot
    embedding: embedding_runtime.LoadedSnapshot
    identity_crosswalk: tuple[dict[str, Any], ...]
    deep_validation: bool


@dataclass
class _RoutePayloadCache:
    """Bound one query context to internal component payloads only."""

    snapshot: Any
    key: tuple[Any, ...]
    payloads: dict[str, Mapping[str, Any]]


_ROUTE_PAYLOAD_CACHE_LOCK = threading.RLock()
_LAST_ROUTE_PAYLOAD_CACHE: _RoutePayloadCache | None = None


def canonical_json(value: Any) -> str:
    """Serialize one JSON value with the builder's canonical encoding."""

    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def sha256_file(path: Path) -> str:
    """Hash one regular file without mutating the snapshot."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_canonical(value: Any) -> str:
    """Hash one canonical JSON value."""

    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _exact_keys(value: Mapping[str, Any], expected: set[str], label: str) -> None:
    actual = set(value)
    if actual != expected:
        raise SnapshotError(
            f"{label} uses a closed schema; missing={sorted(expected - actual)}, "
            f"unknown={sorted(actual - expected)}"
        )


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


def _string_list(value: Any, label: str) -> list[str]:
    if not isinstance(value, list) or not value or any(not isinstance(item, str) for item in value):
        raise SnapshotError(f"{label} must be a nonempty string array")
    if len(set(value)) != len(value):
        raise SnapshotError(f"{label} must not contain duplicates")
    unknown = sorted(set(value) - ALLOWED_ROUTES)
    if unknown:
        raise SnapshotError(f"{label} contains unknown routes: {unknown}")
    return list(value)


def _schema_version(value: Mapping[str, Any]) -> str:
    version = value.get("schema_version")
    if version not in SUPPORTED_SCHEMA_VERSIONS:
        raise SnapshotError(
            "ensemble schema_version must be one of "
            f"{sorted(SUPPORTED_SCHEMA_VERSIONS)}"
        )
    return str(version)


def _validate_identity_plan(value: Any, selected_sources: set[str]) -> None:
    if not isinstance(value, dict):
        raise SnapshotError("ensemble identity plan must be an object")
    _exact_keys(value, IDENTITY_KEYS, "ensemble identity plan")
    if value["default_grouping"] != "source-record-v1":
        raise SnapshotError("ensemble identity default_grouping must be source-record-v1")
    overrides = value["overrides"]
    if not isinstance(overrides, list):
        raise SnapshotError("ensemble identity overrides must be an array")
    previous: tuple[str, str] | None = None
    for number, row in enumerate(overrides, start=1):
        if not isinstance(row, dict):
            raise SnapshotError(f"ensemble identity override {number} must be an object")
        _exact_keys(row, IDENTITY_OVERRIDE_KEYS, f"ensemble identity override {number}")
        source_id, record_id = row["source_id"], row["record_id"]
        namespace, group_value = row["namespace"], row["value"]
        if not isinstance(source_id, str) or source_id not in selected_sources:
            raise SnapshotError(
                f"ensemble identity override {number} names an unselected source"
            )
        if not isinstance(record_id, str) or not record_id:
            raise SnapshotError(
                f"ensemble identity override {number} record_id must be nonempty"
            )
        if (
            not isinstance(namespace, str)
            or IDENTITY_NAMESPACE_RE.fullmatch(namespace) is None
        ):
            raise SnapshotError(f"ensemble identity override {number} namespace is invalid")
        if (
            not isinstance(group_value, str)
            or not group_value
            or len(group_value.encode("utf-8")) > 4096
            or any(ord(character) < 32 for character in group_value)
        ):
            raise SnapshotError(f"ensemble identity override {number} value is invalid")
        identity = (source_id, record_id)
        if previous is not None and identity <= previous:
            raise SnapshotError(
                "ensemble identity overrides must be uniquely ordered by source_id and record_id"
            )
        previous = identity


def _validate_plan(value: Any) -> dict[str, Any]:
    """Independently validate the closed ensemble plan persisted in the snapshot."""

    if not isinstance(value, dict):
        raise SnapshotError("ensemble plan root must be an object")
    version = _schema_version(value)
    _exact_keys(
        value,
        PLAN_KEYS if version == SCHEMA_VERSION else GENERIC_PLAN_KEYS,
        "ensemble plan",
    )
    for child in ("adaptive", "entity_graph", "embedding"):
        if not isinstance(value[child], dict):
            raise SnapshotError(f"ensemble plan {child} must be an object")
    leaked = QUESTION_ID_RE.search(canonical_json(value))
    if leaked:
        raise SnapshotError(
            f"ensemble plans must not contain evaluation question IDs: {leaked.group(0)}"
        )
    if version == GENERIC_SCHEMA_VERSION:
        adaptive_sources = value["adaptive"].get("selection", {}).get("source_ids")
        embedding_sources = value["embedding"].get("selection", {}).get("source_ids")
        if (
            not isinstance(adaptive_sources, list)
            or not adaptive_sources
            or any(not isinstance(item, str) or not item for item in adaptive_sources)
        ):
            raise SnapshotError("adaptive child selection.source_ids must be nonempty strings")
        if adaptive_sources != sorted(set(adaptive_sources)):
            raise SnapshotError("adaptive child selection.source_ids must be sorted and unique")
        if embedding_sources != adaptive_sources:
            raise SnapshotError("adaptive and embedding selections must be identical")
        graph_sources = value["entity_graph"].get("selection", {}).get("source_ids")
        if graph_sources != adaptive_sources:
            raise SnapshotError(
                "adaptive, entity-graph, and embedding selections must be identical"
            )
        if value["entity_graph"].get("schema_version") != GENERIC_SCHEMA_VERSION:
            raise SnapshotError("ensemble v2 requires entity-graph plan schema_version 2.0")
        page_sources = value["adaptive"].get("passages", {}).get(
            "markdown_pdf_page_source_ids"
        )
        if page_sources != []:
            raise SnapshotError("ensemble v2 adaptive passages must use exact full records")
        _validate_identity_plan(value["identity"], set(adaptive_sources))
    policies = value["policies"]
    if not isinstance(policies, dict):
        raise SnapshotError("ensemble plan policies must be an object")
    _exact_keys(policies, POLICIES_KEYS, "ensemble plan policies")
    if policies["default"] not in {"quality", "fast", "robust"}:
        raise SnapshotError("ensemble default policy must be quality, fast, or robust")
    for name in ("quality", "fast", "robust"):
        policy = policies[name]
        if not isinstance(policy, dict):
            raise SnapshotError(f"ensemble policy {name} must be an object")
        _exact_keys(policy, POLICY_KEYS, f"ensemble policy {name}")
        routes = _string_list(policy["routes"], f"ensemble policy {name}.routes")
        weights = policy["weights"]
        if not isinstance(weights, list) or len(weights) != len(routes):
            raise SnapshotError(f"ensemble policy {name}.weights must align with routes")
        for number, weight in enumerate(weights, start=1):
            _finite(weight, f"ensemble policy {name}.weights[{number}]", 0.01, 100.0)
        _plain_int(policy["rrf_k"], f"ensemble policy {name}.rrf_k", 0, 10_000)
        if policy["protected_route"] != "adaptive":
            raise SnapshotError(f"ensemble policy {name} must protect the adaptive candidate set")
        if "adaptive" not in routes:
            raise SnapshotError(f"ensemble policy {name} must include the adaptive route")
        promotion = policy["promotion"]
        if not isinstance(promotion, dict):
            raise SnapshotError(f"ensemble policy {name}.promotion must be an object")
        _exact_keys(promotion, PROMOTION_KEYS, f"ensemble policy {name}.promotion")
        if promotion["route"] not in ALLOWED_ROUTES:
            raise SnapshotError(f"ensemble policy {name}.promotion.route is unknown")
        confirmations = _string_list(
            promotion["confirmation_routes"],
            f"ensemble policy {name}.promotion.confirmation_routes",
        )
        _plain_int(promotion["confirmation_depth"], "promotion confirmation_depth", 1, 100)
        _plain_int(
            promotion["minimum_confirmations"],
            "promotion minimum_confirmations",
            1,
            len(confirmations),
        )
        _plain_int(
            promotion["maximum_protected_rank"],
            "promotion maximum_protected_rank",
            1,
            1000,
        )
    gates = value["quality_gates"]
    if not isinstance(gates, dict):
        raise SnapshotError("ensemble quality_gates must be an object")
    _exact_keys(
        gates,
        QUALITY_GATE_KEYS if version == SCHEMA_VERSION else GENERIC_QUALITY_GATE_KEYS,
        "ensemble quality_gates",
    )
    if gates["required_components"] != REQUIRED_COMPONENTS:
        raise SnapshotError(f"required_components must be exactly {REQUIRED_COMPONENTS}")
    for name in (
        "protect_candidate_set",
        "require_core_parity",
        "reviewed_graph_claims_only",
        "reviewed_embedding_claims_only",
        "require_facet_status",
        "require_exact_answer_bindings",
    ):
        if gates[name] is not True:
            raise SnapshotError(f"quality gate {name} must be true")
    if version == GENERIC_SCHEMA_VERSION:
        for name in sorted(GENERIC_QUALITY_GATE_KEYS - QUALITY_GATE_KEYS):
            if gates[name] is not True:
                raise SnapshotError(f"quality gate {name} must be true")
    if _finite(gates["candidate_edge_weight"], "candidate_edge_weight", 0.0, 1.0) != 0.0:
        raise SnapshotError("candidate_edge_weight must be zero for answer-evidence expansion")
    _plain_int(
        gates["maximum_graph_claims_per_facet"],
        "maximum_graph_claims_per_facet",
        1,
        32,
    )
    _plain_int(
        gates["maximum_graph_claims_total"],
        "maximum_graph_claims_total",
        1,
        500,
    )
    _plain_int(
        gates["maximum_embedding_claims_per_facet"],
        "maximum_embedding_claims_per_facet",
        1,
        100,
    )
    _plain_int(
        gates["maximum_embedding_claims_total"],
        "maximum_embedding_claims_total",
        1,
        1000,
    )
    return value


def _load_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = adaptive_runtime.strict_json_loads(path.read_text(encoding="utf-8"), label=label)
    except (OSError, UnicodeError) as exc:
        raise SnapshotError(f"cannot read {label}: {exc}") from exc
    if not isinstance(value, dict):
        raise SnapshotError(f"{label} root must be an object")
    return value


def _load_jsonl(path: Path, label: str) -> list[dict[str, Any]]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        raise SnapshotError(f"cannot read {label}: {exc}") from exc
    rows: list[dict[str, Any]] = []
    for number, line in enumerate(lines, start=1):
        if not line.strip():
            raise SnapshotError(f"{label}:{number} is blank")
        try:
            row = adaptive_runtime.strict_json_loads(line, label=f"{label}:{number}")
        except adaptive_runtime.SnapshotError as exc:
            raise SnapshotError(str(exc)) from exc
        if not isinstance(row, dict):
            raise SnapshotError(f"{label}:{number} must contain an object")
        rows.append(row)
    return rows


def _jsonl_payload(rows: Sequence[Mapping[str, Any]]) -> str:
    return "".join(canonical_json(row) + "\n" for row in rows)


def _artifact(root: Path, relative: str) -> dict[str, Any]:
    path = root / relative
    return {"path": relative, "bytes": path.stat().st_size, "sha256": sha256_file(path)}


def _counted_artifact(root: Path, relative: str, count: int) -> dict[str, Any]:
    return {**_artifact(root, relative), "count": count}


def _group_id(namespace: str, value: str) -> str:
    return "group-" + sha256_canonical({"namespace": namespace, "value": value})[:32]


def _record_locator(body: str) -> dict[str, Any]:
    return {
        "target": "record-body",
        "kind": "character-range",
        "start": 0,
        "end": len(body),
        "fragment": None,
    }


def _evidence_id(record: Mapping[str, Any], text_sha256: str) -> str:
    identity = {
        "source_id": record["source_id"],
        "record_id": record["record_id"],
        "record_sha256": record["record_sha256"],
        "locator": _record_locator(str(record["body"])),
        "text_sha256": text_sha256,
    }
    return "evidence-" + sha256_canonical(identity)[:32]


def _derive_identity_crosswalk(
    root: Path, plan: Mapping[str, Any]
) -> list[dict[str, Any]]:
    selected_sources = set(plan["adaptive"]["selection"]["source_ids"])
    overrides = {
        (row["source_id"], row["record_id"]): (row["namespace"], row["value"])
        for row in plan["identity"]["overrides"]
    }
    records = [
        row
        for row in _load_jsonl(root / "semantic" / "records.jsonl", "semantic/records.jsonl")
        if row.get("source_id") in selected_sources
    ]
    identities = [(row.get("source_id"), row.get("record_id")) for row in records]
    if len(set(identities)) != len(identities):
        raise SnapshotError("authoritative ledger repeats a selected source/record identity")
    if {str(row.get("source_id")) for row in records} != selected_sources:
        raise SnapshotError("identity crosswalk selection contains a source with no records")
    record_keys = {(str(source), str(record)) for source, record in identities}
    unknown_overrides = sorted(set(overrides) - record_keys)
    if unknown_overrides:
        raise SnapshotError(
            f"identity overrides name unknown selected records: {unknown_overrides}"
        )
    rows: list[dict[str, Any]] = []
    required = (
        "source_id",
        "record_id",
        "record_sha256",
        "concept_id",
        "concept_type",
        "concept_path",
        "source_path",
        "body",
    )
    for record in records:
        if any(not isinstance(record.get(key), str) or not record[key] for key in required):
            raise SnapshotError("identity crosswalk record lacks required authoritative fields")
        if HEX_64_RE.fullmatch(str(record["record_sha256"])) is None:
            raise SnapshotError("identity crosswalk record digest is invalid")
        source_id, record_id = str(record["source_id"]), str(record["record_id"])
        namespace, group_key = overrides.get(
            (source_id, record_id),
            (
                "semantic-okf-record",
                canonical_json({"source_id": source_id, "record_id": record_id}),
            ),
        )
        body = str(record["body"])
        text_sha256 = hashlib.sha256(body.encode("utf-8")).hexdigest()
        row = {
            "source_id": source_id,
            "record_id": record_id,
            "record_sha256": record["record_sha256"],
            "concept_id": record["concept_id"],
            "concept_type": record["concept_type"],
            "concept_path": str(record["concept_path"]).replace("\\", "/"),
            "source_path": str(record["source_path"]).replace("\\", "/"),
            "group_namespace": namespace,
            "group_key": group_key,
            "group_id": _group_id(namespace, group_key),
            "evidence_id": _evidence_id(record, text_sha256),
            "locator": _record_locator(body),
            "text_sha256": text_sha256,
        }
        _exact_keys(row, CROSSWALK_KEYS, "identity crosswalk row")
        rows.append(row)
    rows.sort(key=lambda row: (row["source_id"], row["record_id"]))
    groups: dict[str, tuple[str, str]] = {}
    for row in rows:
        identity = (row["group_namespace"], row["group_key"])
        previous = groups.setdefault(row["group_id"], identity)
        if previous != identity:
            raise SnapshotError("identity crosswalk group ID collision")
    if len({row["evidence_id"] for row in rows}) != len(rows):
        raise SnapshotError("identity crosswalk evidence IDs are not unique")
    return rows


def _component_record_sets(
    adaptive: adaptive_runtime.AdaptiveSnapshot,
    graph: graph_runtime.EntityGraphSnapshot,
    embedding: embedding_runtime.LoadedSnapshot,
) -> dict[str, set[tuple[str, str, str]]]:
    values: dict[str, Sequence[Mapping[str, Any]]] = {
        "adaptive": adaptive.documents,
        "entity_graph": graph.sections,
        "embedding": embedding.chunks,
    }
    result: dict[str, set[tuple[str, str, str]]] = {}
    for name, rows in values.items():
        identities: set[tuple[str, str, str]] = set()
        for number, row in enumerate(rows, start=1):
            exact = tuple(row.get(key) for key in ("source_id", "record_id", "record_sha256"))
            if any(not isinstance(item, str) or not item for item in exact):
                raise SnapshotError(
                    f"{name} component row {number} lacks an exact record identity"
                )
            identities.add(exact)  # type: ignore[arg-type]
        result[name] = identities
    return result


def _verify_component_group_parity(
    crosswalk: Sequence[Mapping[str, Any]],
    adaptive: adaptive_runtime.AdaptiveSnapshot,
    graph: graph_runtime.EntityGraphSnapshot,
    embedding: embedding_runtime.LoadedSnapshot,
) -> None:
    expected = {
        (row["source_id"], row["record_id"], row["record_sha256"])
        for row in crosswalk
    }
    for name, identities in _component_record_sets(adaptive, graph, embedding).items():
        if identities != expected:
            raise SnapshotError(
                f"ensemble {name} component group parity failed; "
                f"missing={len(expected - identities)}, unexpected={len(identities - expected)}"
            )


def _component(root: Path, name: str, relative: str) -> dict[str, Any]:
    payload = _load_json(root / relative, relative)
    return {
        "name": name,
        "index": _artifact(root, relative),
        "schema_version": payload.get("schema_version"),
        "authoritative": payload.get("authoritative"),
        "core": payload.get("core"),
    }


def _expected_child_plan_digests(plan: Mapping[str, Any]) -> dict[str, str]:
    return {
        name: sha256_canonical(plan[name])
        for name in ("adaptive", "entity_graph", "embedding")
    }


def _verify_child_plan_parity(
    plan: Mapping[str, Any],
    adaptive: adaptive_runtime.AdaptiveSnapshot,
    graph: graph_runtime.EntityGraphSnapshot,
    embedding: embedding_runtime.LoadedSnapshot,
) -> dict[str, str]:
    expected = _expected_child_plan_digests(plan)
    observed = {
        "adaptive": adaptive.index.get("adaptive_plan_sha256"),
        "entity_graph": graph.index.get("entity_graph_plan_sha256"),
        "embedding": embedding.index.get("retrieval_plan_sha256"),
    }
    if observed != expected:
        raise SnapshotError("ensemble child-plan digest parity failed")
    if adaptive.index.get("plan") != plan["adaptive"]:
        raise SnapshotError("adaptive persisted child plan differs from ensemble parent")
    if graph.index.get("plan") != plan["entity_graph"]:
        raise SnapshotError("entity-graph persisted child plan differs from ensemble parent")
    return expected


def _verify_claim_binding_parity(
    adaptive: adaptive_runtime.AdaptiveSnapshot,
    graph: graph_runtime.EntityGraphSnapshot,
) -> None:
    adaptive_claims = {
        str(binding["record_id"])
        for binding in adaptive.answer_bindings
        if "claim" in str(binding["concept_type"]).casefold()
    }
    graph_claims: set[str] = set()
    for entity in graph.entities:
        if entity["entity_type"] != "claim" or entity["review_state"] != "reviewed":
            continue
        identity = entity["authoritative_identity"]
        if not isinstance(identity, dict) or not isinstance(identity.get("record_id"), str):
            raise SnapshotError("reviewed graph claim lacks an exact authoritative identity")
        graph_claims.add(identity["record_id"])
    if graph_claims != adaptive_claims:
        raise SnapshotError(
            "reviewed graph claims and exact adaptive answer bindings differ; "
            f"missing={len(adaptive_claims - graph_claims)}, "
            f"unexpected={len(graph_claims - adaptive_claims)}"
        )


def load_snapshot(root: Path, *, deep_validation: bool = False) -> EnsembleSnapshot:
    """Load the closed ensemble and validate all child projections read-only."""

    try:
        root = root.expanduser().resolve(strict=True)
        if not root.is_dir():
            raise SnapshotError(f"bundle is not a directory: {root}")
        ensemble = root / "ensemble"
        if not ensemble.is_dir() or ensemble.is_symlink():
            raise SnapshotError("ensemble must be a real directory")
        actual = {path.name for path in ensemble.iterdir()}
        if "index.json" not in actual:
            raise SnapshotError("ensemble artifact set is missing index.json")
        if any(path.is_symlink() or not path.is_file() for path in ensemble.iterdir()):
            raise SnapshotError("ensemble artifacts must be regular files")
        index = _load_json(ensemble / "index.json", "ensemble/index.json")
        version = _schema_version(index)
        expected_files = (
            EXPECTED_FILES if version == SCHEMA_VERSION else GENERIC_EXPECTED_FILES
        )
        if actual != expected_files:
            raise SnapshotError(
                f"ensemble artifact set is closed; missing={sorted(expected_files - actual)}, "
                f"unknown={sorted(actual - expected_files)}"
            )
        base_index_keys = {
            "schema_version",
            "authoritative",
            "discovery_only",
            "ensemble_plan_sha256",
            "plan",
            "core",
            "components",
            "algorithms",
            "summary",
        }
        _exact_keys(
            index,
            base_index_keys
            if version == SCHEMA_VERSION
            else base_index_keys | {"child_plan_sha256s", "identity_crosswalk"},
            "ensemble index",
        )
        if (
            index["authoritative"] is not False
            or index["discovery_only"] is not True
        ):
            raise SnapshotError("ensemble index authority marker is invalid")
        plan = _validate_plan(index["plan"])
        if plan["schema_version"] != version:
            raise SnapshotError("ensemble index and plan schema versions differ")
        if index["ensemble_plan_sha256"] != sha256_canonical(plan):
            raise SnapshotError("ensemble plan digest is invalid")
        expected_algorithms = {
            "direct_search": ALGORITHM_ID,
            "coverage": COVERAGE_ALGORITHM_ID,
            "answer_gate": ANSWER_GATE_ID,
        }
        if version == GENERIC_SCHEMA_VERSION:
            expected_algorithms = {
                "direct_search": GENERIC_ALGORITHM_ID,
                "coverage": COVERAGE_ALGORITHM_ID,
                "answer_gate": ANSWER_GATE_ID,
                "identity_crosswalk": IDENTITY_ALGORITHM_ID,
                "passage_evidence": EVIDENCE_ALGORITHM_ID,
            }
        if index["algorithms"] != expected_algorithms:
            raise SnapshotError("ensemble algorithm identities are invalid")
        expected_components = {
            "adaptive": _component(root, "adaptive", "adaptive/index.json"),
            "entity_graph": _component(root, "entity_graph", "entity-graph/index.json"),
            "embedding": _component(root, "embedding", "retrieval/index.json"),
        }
        if index["components"] != expected_components:
            raise SnapshotError("ensemble component bindings are stale")
        cores = [component["core"] for component in expected_components.values()]
        if any(core != cores[0] for core in cores[1:]) or index["core"] != cores[0]:
            raise SnapshotError("ensemble authoritative core parity gate failed")
        expected_summary = {
            "policies": 3,
            "required_components": len(REQUIRED_COMPONENTS),
            "default_policy": plan["policies"]["default"],
        }
        identity_crosswalk: list[dict[str, Any]] = []
        crosswalk_artifact: dict[str, Any] | None = None
        if version == GENERIC_SCHEMA_VERSION:
            expected_child_digests = _expected_child_plan_digests(plan)
            if index["child_plan_sha256s"] != expected_child_digests:
                raise SnapshotError("ensemble child-plan digest binding is invalid")
            identity_crosswalk = _load_jsonl(
                ensemble / "identity-crosswalk.jsonl",
                "ensemble/identity-crosswalk.jsonl",
            )
            for number, row in enumerate(identity_crosswalk, start=1):
                _exact_keys(row, CROSSWALK_KEYS, f"identity crosswalk row {number}")
            expected_crosswalk = _derive_identity_crosswalk(root, plan)
            if identity_crosswalk != expected_crosswalk:
                raise SnapshotError(
                    "ensemble identity crosswalk differs from authoritative derivation"
                )
            try:
                crosswalk_payload = (ensemble / "identity-crosswalk.jsonl").read_text(
                    encoding="utf-8"
                )
            except (OSError, UnicodeError) as exc:
                raise SnapshotError(f"cannot read identity crosswalk bytes: {exc}") from exc
            if crosswalk_payload != _jsonl_payload(expected_crosswalk):
                raise SnapshotError("ensemble identity crosswalk is not canonical JSONL")
            crosswalk_artifact = _counted_artifact(
                root, "ensemble/identity-crosswalk.jsonl", len(identity_crosswalk)
            )
            if index["identity_crosswalk"] != crosswalk_artifact:
                raise SnapshotError("ensemble identity crosswalk artifact binding is stale")
            expected_summary = {
                **expected_summary,
                "identity_records": len(identity_crosswalk),
                "identity_groups": len(
                    {row["group_id"] for row in identity_crosswalk}
                ),
                "passage_evidence": len(identity_crosswalk),
            }
        if index["summary"] != expected_summary:
            raise SnapshotError("ensemble summary is invalid")
        expected_report = {
            "schema_version": version,
            "valid": True,
            "status": "pass",
            "authoritative": False,
            "discovery_only": True,
            "errors": [],
            "warnings": [],
            "ensemble_plan_sha256": index["ensemble_plan_sha256"],
            "core": index["core"],
            "components": {
                name: component["index"] for name, component in expected_components.items()
            },
            "artifacts": {"index": _artifact(root, "ensemble/index.json")},
            "summary": expected_summary,
        }
        if crosswalk_artifact is not None:
            expected_report["artifacts"]["identity_crosswalk"] = crosswalk_artifact
        if _load_json(ensemble / "build-report.json", "ensemble/build-report.json") != expected_report:
            raise SnapshotError("ensemble build report differs from live validation")

        adaptive = adaptive_runtime.load_snapshot(root, deep_validation=deep_validation)
        graph = graph_runtime.load_snapshot(root, deep_validation=deep_validation)
        embedding = embedding_runtime.load_snapshot(root)
        live_cores = [adaptive.index["core"], graph.index["core"], embedding.index["core"]]
        if any(core != index["core"] for core in live_cores):
            raise SnapshotError("loaded components do not preserve authoritative core parity")
        if version == GENERIC_SCHEMA_VERSION:
            child_digests = _verify_child_plan_parity(plan, adaptive, graph, embedding)
            if index["child_plan_sha256s"] != child_digests:
                raise SnapshotError("loaded child-plan digests differ from ensemble binding")
            _verify_component_group_parity(
                identity_crosswalk, adaptive, graph, embedding
            )
        else:
            _verify_claim_binding_parity(adaptive, graph)
        return EnsembleSnapshot(
            root=root,
            index=index,
            index_sha256=sha256_file(ensemble / "index.json"),
            adaptive=adaptive,
            graph=graph,
            embedding=embedding,
            identity_crosswalk=tuple(identity_crosswalk),
            deep_validation=deep_validation,
        )
    except (adaptive_runtime.SnapshotError, graph_runtime.SnapshotError, embedding_runtime.SnapshotError) as exc:
        raise SnapshotError(str(exc)) from exc


def inspect_snapshot(snapshot: EnsembleSnapshot) -> dict[str, Any]:
    """Describe validated capabilities, component bindings, and mandatory gates."""

    version = str(snapshot.index["schema_version"])
    component_plan_names = {
        "adaptive": "adaptive",
        "entity_graph": "entity_graph",
        "embedding": "embedding",
    }
    components: dict[str, dict[str, Any]] = {}
    for name, binding in snapshot.index["components"].items():
        child_plan = snapshot.index["plan"].get(component_plan_names[name])
        child_plan_schema = (
            child_plan.get("schema_version") if isinstance(child_plan, dict) else None
        )
        components[name] = {
            **binding,
            "artifact_schema_version": binding["schema_version"],
            "child_plan_schema_version": child_plan_schema,
        }
    capabilities: Any
    if version == GENERIC_SCHEMA_VERSION:
        has_claim_bindings = bool(snapshot.adaptive.answer_bindings)
        capabilities = {
            "search": {"available": True, "evidence": "exact-authoritative-passages"},
            "evidence-pack": {
                "available": True,
                "evidence": "exact-authoritative-passages",
            },
            "answer-brief": {
                "available": not has_claim_bindings,
                "algorithm": GENERIC_ANSWER_BRIEF_ALGORITHM_ID,
                "evidence": "bounded-verbatim-support-identifiers",
            },
            "coverage-pack": {
                "available": has_claim_bindings,
                "requires": "reviewed exact answer bindings",
            },
            "coverage-brief": {
                "available": has_claim_bindings,
                "requires": "reviewed exact answer bindings",
            },
            "finalize-answer": {
                "available": True,
                "algorithm": (
                    ANSWER_GATE_ID if has_claim_bindings else GENERIC_ANSWER_GATE_ID
                ),
                "mode": (
                    "reviewed-exact-answer-bindings"
                    if has_claim_bindings
                    else "exact-evidence-id-and-verbatim-support"
                ),
                "requires": (
                    "reviewed exact answer bindings"
                    if has_claim_bindings
                    else "source-generic evidence pack with exact quoted support"
                ),
            },
        }
    else:
        capabilities = [
            "search",
            "evidence-pack",
            "coverage-pack",
            "coverage-brief",
            "finalize-answer",
        ]
    result = {
        "schema_version": version,
        "status": "pass",
        "authoritative": False,
        "discovery_only": True,
        "read_only": True,
        "deep_validation": snapshot.deep_validation,
        "core": snapshot.index["core"],
        "ensemble_index_sha256": snapshot.index_sha256,
        "ensemble_plan_sha256": snapshot.index["ensemble_plan_sha256"],
        "components": components,
        "algorithms": snapshot.index["algorithms"],
        "policies": {
            "default": snapshot.index["plan"]["policies"]["default"],
            "available": ["quality", "fast", "robust"],
        },
        "quality_gates": snapshot.index["plan"]["quality_gates"],
        "capabilities": capabilities,
    }
    if version == GENERIC_SCHEMA_VERSION:
        result["identity"] = {
            "algorithm": IDENTITY_ALGORITHM_ID,
            "records": len(snapshot.identity_crosswalk),
            "groups": len({row["group_id"] for row in snapshot.identity_crosswalk}),
            "crosswalk_sha256": snapshot.index["identity_crosswalk"]["sha256"],
        }
    return result


def _paper_id(row: Mapping[str, Any]) -> str | None:
    value = row.get("paper_id")
    if isinstance(value, str) and value:
        return value
    source_id = row.get("source_id")
    if isinstance(source_id, str) and source_id.startswith("paper-"):
        candidate = source_id[len("paper-") :]
        match = re.fullmatch(r"(\d{4})-(\d{5}v\d+)", candidate, re.IGNORECASE)
        return f"{match.group(1)}.{match.group(2)}" if match else candidate
    record_id = row.get("record_id")
    if isinstance(record_id, str) and record_id.startswith("sources/markdown/"):
        return record_id.rsplit("/", 1)[-1]
    return None


def _paper_ranking(payload: Mapping[str, Any]) -> tuple[list[str], dict[str, Mapping[str, Any]]]:
    rows: Any = payload.get("results")
    if not isinstance(rows, list):
        rows = payload.get("hits")
    if not isinstance(rows, list):
        raise SnapshotError("component search output lacks a result array")
    ranking: list[str] = []
    representatives: dict[str, Mapping[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict):
            raise SnapshotError("component search emitted a non-object result")
        paper_id = _paper_id(row)
        if paper_id is None:
            continue
        if paper_id not in representatives:
            representatives[paper_id] = row
            ranking.append(paper_id)
    return ranking, representatives


def _exact_record_identity(row: Mapping[str, Any]) -> tuple[str, str, str]:
    values = tuple(row.get(key) for key in ("source_id", "record_id", "record_sha256"))
    if any(not isinstance(value, str) or not value for value in values):
        raise SnapshotError(
            "generic component result lacks source_id, record_id, or record_sha256"
        )
    return values  # type: ignore[return-value]


def _crosswalk_by_record(
    snapshot: EnsembleSnapshot,
) -> dict[tuple[str, str, str], Mapping[str, Any]]:
    result = {
        (row["source_id"], row["record_id"], row["record_sha256"]): row
        for row in snapshot.identity_crosswalk
    }
    if len(result) != len(snapshot.identity_crosswalk):
        raise SnapshotError("identity crosswalk record keys are not unique")
    return result


def _crosswalk_by_group(
    snapshot: EnsembleSnapshot,
) -> dict[str, Mapping[str, Any]]:
    result: dict[str, Mapping[str, Any]] = {}
    for row in snapshot.identity_crosswalk:
        existing = result.setdefault(str(row["group_id"]), row)
        if (
            existing["group_namespace"] != row["group_namespace"]
            or existing["group_key"] != row["group_key"]
        ):
            raise SnapshotError("identity crosswalk group ID collision")
    return result


def _group_ranking(
    snapshot: EnsembleSnapshot, payload: Mapping[str, Any]
) -> tuple[list[str], dict[str, Mapping[str, Any]]]:
    """Join component hits only through the persisted exact identity crosswalk."""

    rows: Any = payload.get("results")
    if not isinstance(rows, list):
        rows = payload.get("hits")
    if not isinstance(rows, list):
        raise SnapshotError("component search output lacks a result array")
    crosswalk = _crosswalk_by_record(snapshot)
    ranking: list[str] = []
    representatives: dict[str, Mapping[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict):
            raise SnapshotError("component search emitted a non-object result")
        exact = _exact_record_identity(row)
        identity = crosswalk.get(exact)
        if identity is None:
            raise SnapshotError(
                "component search result is absent from the exact identity crosswalk"
            )
        group_id = str(identity["group_id"])
        if group_id not in representatives:
            representatives[group_id] = row
            ranking.append(group_id)
    return ranking, representatives


def _normalized_record_body_locator(
    locator: Any, crosswalk: Mapping[str, Any]
) -> dict[str, Any]:
    full = crosswalk["locator"]
    if locator == {"kind": "record"}:
        return dict(full)
    if (
        isinstance(locator, dict)
        and set(locator) == {"kind", "start", "end"}
        and locator.get("kind") == "character-range"
        and isinstance(locator.get("start"), int)
        and not isinstance(locator.get("start"), bool)
        and isinstance(locator.get("end"), int)
        and not isinstance(locator.get("end"), bool)
        and 0 <= locator["start"] < locator["end"] <= full["end"]
    ):
        return {
            "target": "record-body",
            "kind": "character-range",
            "start": locator["start"],
            "end": locator["end"],
            "fragment": None,
        }
    raise SnapshotError("adaptive passage result has an invalid record-body locator")


def _passage_evidence_id(
    exact: tuple[str, str, str], locator: Mapping[str, Any], text_sha256: str
) -> str:
    value = {
        "source_id": exact[0],
        "record_id": exact[1],
        "record_sha256": exact[2],
        "locator": locator,
        "text_sha256": text_sha256,
    }
    return "evidence-" + sha256_canonical(value)[:32]


def _generic_evidence_row(
    snapshot: EnsembleSnapshot,
    row: Mapping[str, Any],
    rank: int,
) -> dict[str, Any]:
    exact = _exact_record_identity(row)
    crosswalk = _crosswalk_by_record(snapshot).get(exact)
    if crosswalk is None:
        raise SnapshotError("adaptive evidence row is absent from the identity crosswalk")
    for key in ("concept_id", "concept_type", "concept_path", "source_path"):
        if row.get(key) != crosswalk[key]:
            raise SnapshotError(
                f"adaptive evidence row {key} differs from the authoritative crosswalk"
            )
    text = row.get("text")
    text_sha256 = row.get("text_sha256")
    if (
        not isinstance(text, str)
        or not isinstance(text_sha256, str)
        or hashlib.sha256(text.encode("utf-8")).hexdigest() != text_sha256
    ):
        raise SnapshotError("adaptive evidence row has invalid text or text hash")
    locator = _normalized_record_body_locator(row.get("locator"), crosswalk)
    evidence_id = _passage_evidence_id(exact, locator, text_sha256)
    if locator == crosswalk["locator"] and evidence_id != crosswalk["evidence_id"]:
        raise SnapshotError("full-record passage evidence ID differs from the crosswalk")
    return {
        "rank": rank,
        "evidence_id": evidence_id,
        "group_id": crosswalk["group_id"],
        "group_namespace": crosswalk["group_namespace"],
        "group_key": crosswalk["group_key"],
        "source_id": exact[0],
        "record_id": exact[1],
        "record_sha256": exact[2],
        "concept_id": crosswalk["concept_id"],
        "concept_type": crosswalk["concept_type"],
        "concept_path": crosswalk["concept_path"],
        "source_path": crosswalk["source_path"],
        "locator": locator,
        "text": text,
        "text_sha256": text_sha256,
        "adaptive_index_sha256": snapshot.adaptive.index_sha256,
        "core_tree_sha256": snapshot.index["core"]["tree_sha256"],
    }


def _cached_embedding_provider(
    snapshot: embedding_runtime.LoadedSnapshot,
) -> embedding_runtime.QueryEmbedder | None:
    """Load one exact offline semantic model once per process and plan digest."""

    config = snapshot.index["embedding"]
    if config["provider"] != "sentence-transformers":
        return None
    key = sha256_canonical(config)
    if key in _EMBEDDER_CACHE:
        return _EMBEDDER_CACHE[key]
    try:
        version = importlib.metadata.version("sentence-transformers")
        if version != embedding_runtime.SENTENCE_TRANSFORMERS_VERSION:
            raise embedding_runtime.ProviderUnavailable(
                "sentence-transformers "
                f"{embedding_runtime.SENTENCE_TRANSFORMERS_VERSION} is required, found {version}"
            )
        module = importlib.import_module("sentence_transformers")
        model_class = getattr(module, "SentenceTransformer")
        model_path = embedding_runtime._resolve_sentence_transformer_snapshot(config)
        with embedding_runtime._offline_model_environment():
            model = model_class(
                str(model_path),
                device="cpu",
                local_files_only=True,
                trust_remote_code=False,
            )
    except embedding_runtime.ProviderUnavailable:
        raise
    except Exception as exc:
        raise embedding_runtime.ProviderUnavailable(
            "the exact pinned sentence-transformers model cannot be initialized offline"
        ) from exc

    def encode(text: str, active_config: Mapping[str, Any]) -> Sequence[float]:
        kwargs = {
            "normalize_embeddings": bool(active_config["normalize"]),
            "show_progress_bar": False,
            "convert_to_numpy": True,
        }
        with embedding_runtime._offline_model_environment():
            if active_config["encoding"]["query"] == "query" and callable(
                getattr(model, "encode_query", None)
            ):
                value = model.encode_query([text], **kwargs)
            else:
                value = model.encode([text], **kwargs)
        return embedding_runtime._sequence_from_model(value)

    _EMBEDDER_CACHE[key] = encode
    return encode


def _run_route(
    snapshot: EnsembleSnapshot,
    route: str,
    query: str,
    top_k: int,
    *,
    source_ids: Sequence[str],
    concept_ids: Sequence[str],
    concept_types: Sequence[str],
) -> Mapping[str, Any]:
    if route == "adaptive":
        return adaptive_runtime.search_snapshot(
            snapshot.adaptive,
            query,
            "adaptive",
            top_k,
            source_ids=source_ids,
            concept_ids=concept_ids,
            concept_types=concept_types,
        )
    if route in {"bm25", "association"}:
        return adaptive_runtime.search_snapshot(
            snapshot.adaptive,
            query,
            route,
            top_k,
            source_ids=source_ids,
            concept_ids=concept_ids,
            concept_types=concept_types,
        )
    if route in {"graph_lexical", "graph_fusion"}:
        return graph_runtime.search_snapshot(
            snapshot.graph,
            query,
            route.removeprefix("graph_"),
            top_k,
            source_ids=source_ids,
        )
    if route == "embedding_hybrid":
        return embedding_runtime.search_snapshot(
            snapshot.embedding,
            query,
            requested_mode="hybrid",
            top_k=top_k,
            source_ids=source_ids,
            concept_ids=concept_ids,
            concept_types=concept_types,
            allow_fallback=False,
            embedder=_cached_embedding_provider(snapshot.embedding),
        )
    raise SnapshotError(f"unsupported ensemble route: {route}")


def _route_payload_cache_key(
    snapshot: EnsembleSnapshot,
    query: str,
    top_k: int,
    source_ids: Sequence[str],
    concept_ids: Sequence[str],
    concept_types: Sequence[str],
) -> tuple[Any, ...]:
    """Bind reusable route payloads to one exact generic query context."""

    return (
        id(snapshot),
        snapshot.root.as_posix(),
        snapshot.index_sha256,
        snapshot.index["core"]["tree_sha256"],
        snapshot.index["ensemble_plan_sha256"],
        query,
        top_k,
        tuple(sorted(set(source_ids))),
        tuple(sorted(set(concept_ids))),
        tuple(sorted(set(concept_types))),
    )


def _cached_route_payload(
    snapshot: EnsembleSnapshot,
    route: str,
    query: str,
    top_k: int,
    *,
    source_ids: Sequence[str],
    concept_ids: Sequence[str],
    concept_types: Sequence[str],
) -> Mapping[str, Any]:
    """Reuse one component route result without exposing it to public callers."""

    global _LAST_ROUTE_PAYLOAD_CACHE
    key = _route_payload_cache_key(
        snapshot,
        query,
        top_k,
        source_ids,
        concept_ids,
        concept_types,
    )
    with _ROUTE_PAYLOAD_CACHE_LOCK:
        if (
            _LAST_ROUTE_PAYLOAD_CACHE is None
            or _LAST_ROUTE_PAYLOAD_CACHE.snapshot is not snapshot
            or _LAST_ROUTE_PAYLOAD_CACHE.key != key
        ):
            _LAST_ROUTE_PAYLOAD_CACHE = _RoutePayloadCache(
                snapshot=snapshot,
                key=key,
                payloads={},
            )
        payload = _LAST_ROUTE_PAYLOAD_CACHE.payloads.get(route)
        if payload is None:
            payload = _run_route(
                snapshot,
                route,
                query,
                top_k,
                source_ids=source_ids,
                concept_ids=concept_ids,
                concept_types=concept_types,
            )
            _LAST_ROUTE_PAYLOAD_CACHE.payloads[route] = payload
        return payload


def _search_generic_snapshot(
    snapshot: EnsembleSnapshot,
    query: str,
    policy_name: str,
    top_k: int,
    *,
    source_ids: Sequence[str],
    concept_ids: Sequence[str],
    concept_types: Sequence[str],
) -> dict[str, Any]:
    """Fuse v2 routes by explicit persisted identity groups without path inference."""

    policies = snapshot.index["plan"]["policies"]
    effective_policy = policies["default"] if policy_name == "default" else policy_name
    if effective_policy not in {"quality", "fast", "robust"}:
        raise SnapshotError("policy must be default, quality, fast, or robust")
    policy = policies[effective_policy]
    promotion = policy["promotion"]
    required_routes = set(policy["routes"])
    required_routes.add(promotion["route"])
    required_routes.update(promotion["confirmation_routes"])
    disabled_routes: dict[str, str] = {}
    if concept_ids or concept_types:
        for route in sorted(required_routes & {"graph_lexical", "graph_fusion"}):
            disabled_routes[route] = "graph routes do not expose concept filters"
    payloads: dict[str, Mapping[str, Any]] = {}
    rankings: dict[str, list[str]] = {}
    representatives: dict[str, dict[str, Mapping[str, Any]]] = {}
    for route in sorted(required_routes - set(disabled_routes)):
        try:
            payload = _cached_route_payload(
                snapshot,
                route,
                query,
                top_k,
                source_ids=source_ids,
                concept_ids=concept_ids,
                concept_types=concept_types,
            )
        except embedding_runtime.ProviderUnavailable as exc:
            raise SnapshotError(
                "quality policy requires the exact pinned embedding provider; "
                "choose fast or robust explicitly when it is unavailable"
            ) from exc
        payloads[route] = payload
        ranking, by_group = _group_ranking(snapshot, payload)
        rankings[route] = ranking
        representatives[route] = by_group
    if "adaptive" not in rankings:
        raise SnapshotError("every ensemble policy must execute the protected adaptive route")
    protected = rankings["adaptive"]
    adaptive_by_group = representatives["adaptive"]
    adaptive_ranks = {
        group_id: rank for rank, group_id in enumerate(protected, start=1)
    }
    component_ranks = {
        route: {group_id: rank for rank, group_id in enumerate(ranking, start=1)}
        for route, ranking in rankings.items()
    }
    scores: dict[str, float] = {group_id: 0.0 for group_id in protected}
    effective_scoring_routes: list[str] = []
    for route, weight in zip(policy["routes"], policy["weights"]):
        if route not in component_ranks:
            continue
        effective_scoring_routes.append(route)
        for group_id in protected:
            rank = component_ranks[route].get(group_id)
            if rank is not None:
                scores[group_id] += float(weight) / (int(policy["rrf_k"]) + rank)
    if not effective_scoring_routes:
        raise SnapshotError("no policy scoring route remained after filter capability gates")
    selected = sorted(
        protected,
        key=lambda group_id: (
            -scores[group_id],
            min(
                component_ranks[route].get(group_id, top_k + 1)
                for route in effective_scoring_routes
            ),
            sum(
                component_ranks[route].get(group_id, top_k + 1)
                for route in effective_scoring_routes
            ),
            -sum(
                group_id in component_ranks[route]
                for route in effective_scoring_routes
            ),
            group_id,
        ),
    )
    promotion_route = promotion["route"]
    promotion_candidate = (
        rankings.get(promotion_route, [None])[0]
        if rankings.get(promotion_route)
        else None
    )
    confirmations: list[str] = []
    if promotion_candidate is not None:
        confirmations = [
            route
            for route in promotion["confirmation_routes"]
            if component_ranks.get(route, {}).get(promotion_candidate, top_k + 1)
            <= int(promotion["confirmation_depth"])
        ]
    eligible = (
        promotion_candidate in adaptive_ranks
        and adaptive_ranks.get(str(promotion_candidate), top_k + 1)
        <= int(promotion["maximum_protected_rank"])
        and len(confirmations) >= int(promotion["minimum_confirmations"])
    )
    if eligible and promotion_candidate is not None:
        selected = [
            promotion_candidate,
            *(group for group in selected if group != promotion_candidate),
        ]
    if set(selected) != set(protected) or len(selected) != len(protected):
        raise SnapshotError("protected adaptive candidate-set gate failed")

    crosswalk_by_group = _crosswalk_by_group(snapshot)
    crosswalk_by_record = _crosswalk_by_record(snapshot)
    adaptive_payload = payloads["adaptive"]
    adaptive_evidence: dict[str, Mapping[str, Any]] = {}
    for row in adaptive_payload.get("evidence_rows", []):
        if not isinstance(row, dict):
            raise SnapshotError("adaptive evidence output contains a non-object row")
        exact = _exact_record_identity(row)
        crosswalk = crosswalk_by_record.get(exact)
        if crosswalk is None:
            raise SnapshotError("adaptive evidence row is absent from the crosswalk")
        adaptive_evidence.setdefault(str(crosswalk["group_id"]), row)
    adaptive_answer: dict[str, Mapping[str, Any]] = {}
    for row in adaptive_payload.get("answer_evidence_rows", []):
        if not isinstance(row, dict):
            raise SnapshotError("adaptive answer evidence contains a non-object row")
        exact = _exact_record_identity(row)
        crosswalk = crosswalk_by_record.get(exact)
        if crosswalk is None:
            raise SnapshotError("adaptive answer evidence is absent from the crosswalk")
        adaptive_answer.setdefault(str(crosswalk["group_id"]), row)

    results: list[dict[str, Any]] = []
    evidence_rows: list[dict[str, Any]] = []
    answer_evidence_rows: list[dict[str, Any]] = []
    for rank, group_id in enumerate(selected, start=1):
        identity = crosswalk_by_group.get(group_id)
        if identity is None:
            raise SnapshotError("selected group is absent from the identity crosswalk")
        hit = dict(adaptive_by_group[group_id])
        hit["rank"] = rank
        hit["chunk_id"] = hit.get("chunk_id") or hit.get("document_id")
        hit["group_id"] = group_id
        hit["identity_group"] = {
            "namespace": identity["group_namespace"],
            "key": identity["group_key"],
        }
        hit["score"] = round(scores[group_id], 12)
        hit["scores"] = {
            **dict(hit.get("scores", {})),
            "ensemble": round(scores[group_id], 12),
        }
        hit["ranks"] = {
            route: ranks.get(group_id)
            for route, ranks in sorted(component_ranks.items())
        }
        hit["ensemble"] = {
            "policy": effective_policy,
            "protected_adaptive_rank": adaptive_ranks[group_id],
            "promoted": eligible and group_id == promotion_candidate,
        }
        evidence = adaptive_evidence.get(group_id)
        if evidence is None:
            raise SnapshotError(
                "protected adaptive group lacks exact authoritative passage evidence"
            )
        if _exact_record_identity(hit) != _exact_record_identity(evidence):
            raise SnapshotError(
                "adaptive representative and evidence row record identities differ"
            )
        normalized_evidence = _generic_evidence_row(snapshot, evidence, rank)
        hit["evidence_id"] = normalized_evidence["evidence_id"]
        hit["locator"] = normalized_evidence["locator"]
        hit["source_path"] = normalized_evidence["source_path"]
        hit["concept_path"] = normalized_evidence["concept_path"]
        hit["text_sha256"] = normalized_evidence["text_sha256"]
        results.append(hit)
        evidence_rows.append(normalized_evidence)
        answer = adaptive_answer.get(group_id)
        if answer is not None:
            answer_evidence_rows.append(
                {
                    **dict(answer),
                    "rank": rank,
                    "group_id": group_id,
                    "identity_group": hit["identity_group"],
                }
            )
    result = {
        "schema_version": GENERIC_SCHEMA_VERSION,
        "status": "pass",
        "authoritative": False,
        "discovery_only": True,
        "query": query,
        "requested_policy": policy_name,
        "effective_policy": effective_policy,
        "top_k": top_k,
        "returned": len(results),
        "filters": {
            "source_ids": sorted(set(source_ids)),
            "concept_ids": sorted(set(concept_ids)),
            "concept_types": sorted(set(concept_types)),
        },
        "snapshot": {
            "core_tree_sha256": snapshot.index["core"]["tree_sha256"],
            "ensemble_index_sha256": snapshot.index_sha256,
            "ensemble_plan_sha256": snapshot.index["ensemble_plan_sha256"],
            "identity_crosswalk_sha256": snapshot.index["identity_crosswalk"]["sha256"],
            "deep_validation": snapshot.deep_validation,
        },
        "policy": {
            "algorithm": GENERIC_ALGORITHM_ID,
            "routes": list(policy["routes"]),
            "weights": list(policy["weights"]),
            "rrf_k": policy["rrf_k"],
            "effective_scoring_routes": effective_scoring_routes,
            "disabled_routes": disabled_routes,
        },
        "promotion_gate": {
            "candidate_group_id": promotion_candidate,
            "confirmations": confirmations,
            "required_confirmations": promotion["minimum_confirmations"],
            "confirmation_depth": promotion["confirmation_depth"],
            "protected_rank": adaptive_ranks.get(str(promotion_candidate)),
            "maximum_protected_rank": promotion["maximum_protected_rank"],
            "passed": eligible,
        },
        "candidate_set_gate": {
            "protected_route": "adaptive",
            "protected_group_ids": protected,
            "selected_group_ids": selected,
            "preserved_exactly": set(selected) == set(protected),
        },
        "route_rankings": {
            route: {"returned": len(ranking), "group_ids": ranking}
            for route, ranking in sorted(rankings.items())
        },
        "results": results,
        "evidence_rows": evidence_rows,
        "answer_evidence_rows": answer_evidence_rows,
        "evidence_contract": {
            "adapter": EVIDENCE_ALGORITHM_ID,
            "copy_fields_only": True,
            "authoritative_verification_required": True,
            "identity_join": "source_id+record_id+record_sha256 via identity-crosswalk.jsonl",
            "locator_basis": "semantic/records.jsonl record.body character range",
        },
    }
    if snapshot.adaptive.answer_bindings:
        result["answer_evidence_contract"] = adaptive_payload[
            "answer_evidence_contract"
        ]
    return result


def search_snapshot(
    snapshot: EnsembleSnapshot,
    query: str,
    policy_name: str,
    top_k: int,
    *,
    source_ids: Sequence[str] = (),
    concept_ids: Sequence[str] = (),
    concept_types: Sequence[str] = (),
) -> dict[str, Any]:
    """Rerank only protected adaptive papers with independently persisted signals."""

    if not isinstance(query, str) or not query.strip():
        raise SnapshotError("query must be nonempty")
    if isinstance(top_k, bool) or not isinstance(top_k, int) or not 1 <= top_k <= 1000:
        raise SnapshotError("top-k must be an integer from 1 through 1000")
    if snapshot.index.get("schema_version") == GENERIC_SCHEMA_VERSION:
        return _search_generic_snapshot(
            snapshot,
            query,
            policy_name,
            top_k,
            source_ids=source_ids,
            concept_ids=concept_ids,
            concept_types=concept_types,
        )
    policies = snapshot.index["plan"]["policies"]
    effective_policy = policies["default"] if policy_name == "default" else policy_name
    if effective_policy not in {"quality", "fast", "robust"}:
        raise SnapshotError("policy must be default, quality, fast, or robust")
    policy = policies[effective_policy]
    promotion = policy["promotion"]
    required_routes = set(policy["routes"])
    required_routes.add(promotion["route"])
    required_routes.update(promotion["confirmation_routes"])
    disabled_routes: dict[str, str] = {}
    if concept_ids or concept_types:
        for route in sorted(required_routes & {"graph_lexical", "graph_fusion"}):
            disabled_routes[route] = "graph routes do not expose concept filters"
    payloads: dict[str, Mapping[str, Any]] = {}
    rankings: dict[str, list[str]] = {}
    representatives: dict[str, dict[str, Mapping[str, Any]]] = {}
    for route in sorted(required_routes - set(disabled_routes)):
        try:
            payload = _run_route(
                snapshot,
                route,
                query,
                top_k,
                source_ids=source_ids,
                concept_ids=concept_ids,
                concept_types=concept_types,
            )
        except embedding_runtime.ProviderUnavailable as exc:
            raise SnapshotError(
                "quality policy requires the exact pinned embedding provider; "
                "choose fast or robust explicitly when it is unavailable"
            ) from exc
        payloads[route] = payload
        ranking, by_paper = _paper_ranking(payload)
        rankings[route] = ranking
        representatives[route] = by_paper
    if "adaptive" not in rankings:
        raise SnapshotError("every ensemble policy must execute the protected adaptive route")
    protected = rankings["adaptive"]
    adaptive_by_paper = representatives["adaptive"]
    adaptive_ranks = {paper_id: rank for rank, paper_id in enumerate(protected, start=1)}
    component_ranks = {
        route: {paper_id: rank for rank, paper_id in enumerate(ranking, start=1)}
        for route, ranking in rankings.items()
    }
    scores: dict[str, float] = {paper_id: 0.0 for paper_id in protected}
    effective_scoring_routes: list[str] = []
    for route, weight in zip(policy["routes"], policy["weights"]):
        if route not in component_ranks:
            continue
        effective_scoring_routes.append(route)
        for paper_id in protected:
            rank = component_ranks[route].get(paper_id)
            if rank is not None:
                scores[paper_id] += float(weight) / (int(policy["rrf_k"]) + rank)
    if not effective_scoring_routes:
        raise SnapshotError("no policy scoring route remained after filter capability gates")
    selected = sorted(
        protected,
        key=lambda paper_id: (
            -scores[paper_id],
            min(
                component_ranks[route].get(paper_id, top_k + 1)
                for route in effective_scoring_routes
            ),
            sum(
                component_ranks[route].get(paper_id, top_k + 1)
                for route in effective_scoring_routes
            ),
            -sum(
                paper_id in component_ranks[route]
                for route in effective_scoring_routes
            ),
            paper_id,
        ),
    )

    promotion_route = promotion["route"]
    promotion_candidate = rankings.get(promotion_route, [None])[0] if rankings.get(promotion_route) else None
    confirmations: list[str] = []
    if promotion_candidate is not None:
        confirmations = [
            route
            for route in promotion["confirmation_routes"]
            if component_ranks.get(route, {}).get(promotion_candidate, top_k + 1)
            <= int(promotion["confirmation_depth"])
        ]
    eligible = (
        promotion_candidate in adaptive_ranks
        and adaptive_ranks.get(str(promotion_candidate), top_k + 1)
        <= int(promotion["maximum_protected_rank"])
        and len(confirmations) >= int(promotion["minimum_confirmations"])
    )
    if eligible and promotion_candidate is not None:
        selected = [promotion_candidate, *(paper for paper in selected if paper != promotion_candidate)]
    if set(selected) != set(protected) or len(selected) != len(protected):
        raise SnapshotError("protected adaptive candidate-set gate failed")

    results: list[dict[str, Any]] = []
    evidence_rows: list[dict[str, Any]] = []
    answer_evidence_rows: list[dict[str, Any]] = []
    adaptive_payload = payloads["adaptive"]
    adaptive_evidence_by_paper: dict[str, Mapping[str, Any]] = {}
    for row in adaptive_payload.get("evidence_rows", []):
        if isinstance(row, dict) and isinstance(row.get("paper_id"), str):
            adaptive_evidence_by_paper.setdefault(row["paper_id"], row)
    adaptive_answer_by_paper: dict[str, Mapping[str, Any]] = {}
    for row in adaptive_payload.get("answer_evidence_rows", []):
        if isinstance(row, dict) and isinstance(row.get("paper_id"), str):
            adaptive_answer_by_paper.setdefault(row["paper_id"], row)
    for rank, paper_id in enumerate(selected, start=1):
        hit = dict(adaptive_by_paper[paper_id])
        hit["rank"] = rank
        hit["chunk_id"] = hit.get("chunk_id") or hit.get("document_id")
        hit["score"] = round(scores[paper_id], 12)
        hit["scores"] = {
            **dict(hit.get("scores", {})),
            "ensemble": round(scores[paper_id], 12),
        }
        hit["ranks"] = {
            route: ranks.get(paper_id) for route, ranks in sorted(component_ranks.items())
        }
        hit["ensemble"] = {
            "policy": effective_policy,
            "protected_adaptive_rank": adaptive_ranks[paper_id],
            "promoted": eligible and paper_id == promotion_candidate,
        }
        results.append(hit)
        evidence = adaptive_evidence_by_paper.get(paper_id)
        if evidence is not None:
            evidence_rows.append({**dict(evidence), "rank": rank})
        answer_evidence = adaptive_answer_by_paper.get(paper_id)
        if answer_evidence is not None:
            answer_evidence_rows.append({**dict(answer_evidence), "rank": rank})
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "pass",
        "authoritative": False,
        "discovery_only": True,
        "query": query,
        "requested_policy": policy_name,
        "effective_policy": effective_policy,
        "top_k": top_k,
        "returned": len(results),
        "filters": {
            "source_ids": sorted(set(source_ids)),
            "concept_ids": sorted(set(concept_ids)),
            "concept_types": sorted(set(concept_types)),
        },
        "snapshot": {
            "core_tree_sha256": snapshot.index["core"]["tree_sha256"],
            "ensemble_index_sha256": snapshot.index_sha256,
            "ensemble_plan_sha256": snapshot.index["ensemble_plan_sha256"],
            "deep_validation": snapshot.deep_validation,
        },
        "policy": {
            "algorithm": ALGORITHM_ID,
            "routes": list(policy["routes"]),
            "weights": list(policy["weights"]),
            "rrf_k": policy["rrf_k"],
            "effective_scoring_routes": effective_scoring_routes,
            "disabled_routes": disabled_routes,
        },
        "promotion_gate": {
            "candidate": promotion_candidate,
            "confirmations": confirmations,
            "required_confirmations": promotion["minimum_confirmations"],
            "confirmation_depth": promotion["confirmation_depth"],
            "protected_rank": adaptive_ranks.get(str(promotion_candidate)),
            "maximum_protected_rank": promotion["maximum_protected_rank"],
            "passed": eligible,
        },
        "candidate_set_gate": {
            "protected_route": "adaptive",
            "protected_paper_ids": protected,
            "selected_paper_ids": selected,
            "preserved_exactly": set(selected) == set(protected),
        },
        "route_rankings": {
            route: {"returned": len(ranking), "paper_ids": ranking}
            for route, ranking in sorted(rankings.items())
        },
        "results": results,
        "evidence_rows": evidence_rows,
        "answer_evidence_rows": answer_evidence_rows,
        "evidence_contract": adaptive_payload["evidence_contract"],
        "answer_evidence_contract": adaptive_payload["answer_evidence_contract"],
    }


def build_evidence_pack(
    snapshot: EnsembleSnapshot,
    query: str,
    top_k: int,
) -> dict[str, Any]:
    """Delegate answer-record ranking to the validated adaptive evidence route."""

    if (
        snapshot.index.get("schema_version") == GENERIC_SCHEMA_VERSION
        and not snapshot.adaptive.answer_bindings
    ):
        search = search_snapshot(snapshot, query, "fast", top_k)
        return {
            "schema_version": GENERIC_SCHEMA_VERSION,
            "status": "pass",
            "authoritative": False,
            "discovery_only": True,
            "query": query,
            "top_k": top_k,
            "returned": len(search["evidence_rows"]),
            "evidence_kind": "authoritative-record-body-passages",
            "claim_binding_gate": {
                "available": False,
                "reason": "the selected authoritative records have no reviewed exact answer bindings",
                "claim_only_commands": [
                    "coverage-pack",
                    "coverage-brief",
                    "finalize-answer",
                ],
            },
            "evidence_rows": search["evidence_rows"],
            "results": search["results"],
            "evidence_contract": search["evidence_contract"],
            "ensemble": {
                "ensemble_index_sha256": snapshot.index_sha256,
                "identity_crosswalk_sha256": snapshot.index["identity_crosswalk"]["sha256"],
                "core_tree_sha256": snapshot.index["core"]["tree_sha256"],
                "quality_gates": snapshot.index["plan"]["quality_gates"],
            },
        }
    result = adaptive_runtime.build_evidence_pack(snapshot.adaptive, query, top_k)
    result["ensemble"] = {
        "ensemble_index_sha256": snapshot.index_sha256,
        "core_tree_sha256": snapshot.index["core"]["tree_sha256"],
        "quality_gates": snapshot.index["plan"]["quality_gates"],
    }
    return result


def _bounded_quote_spans(text: str, maximum_characters: int = 900) -> list[tuple[int, int, str]]:
    """Split authoritative text into deterministic, exact, reviewable quote spans."""

    spans: list[tuple[int, int, str]] = []
    for match in re.finditer(r"\S[\s\S]*?(?=\r?\n[ \t]*\r?\n|\Z)", text):
        raw_start, raw_end = match.span()
        raw = text[raw_start:raw_end]
        leading = len(raw) - len(raw.lstrip())
        trailing = len(raw) - len(raw.rstrip())
        start = raw_start + leading
        end = raw_end - trailing
        if end - start < 16:
            continue
        if end - start <= maximum_characters:
            spans.append((start, end, text[start:end]))
            continue
        cursor = start
        while cursor < end:
            ceiling = min(end, cursor + maximum_characters)
            boundary = ceiling
            if ceiling < end:
                candidates = [
                    text.rfind("\n", cursor + 160, ceiling),
                    text.rfind(". ", cursor + 160, ceiling),
                    text.rfind(" ", cursor + 160, ceiling),
                ]
                usable = [candidate for candidate in candidates if candidate >= cursor + 160]
                if usable:
                    boundary = max(usable) + (2 if text[max(usable): max(usable) + 2] == ". " else 1)
            quote_start = cursor
            while quote_start < boundary and text[quote_start].isspace():
                quote_start += 1
            quote_end = boundary
            while quote_end > quote_start and text[quote_end - 1].isspace():
                quote_end -= 1
            if quote_end - quote_start >= 16:
                spans.append((quote_start, quote_end, text[quote_start:quote_end]))
            cursor = max(boundary, cursor + 1)
    return spans


def _answer_brief_facets(
    snapshot: EnsembleSnapshot,
    query: str,
    maximum_facets: int,
) -> list[str]:
    full = query.strip()
    if maximum_facets == 1:
        return [full]
    facets = adaptive_runtime.decompose_coverage_facets(
        query,
        snapshot.adaptive.index["plan"],
        maximum_facets - 1,
    )
    return [full, *(facet for facet in facets if facet != full)][:maximum_facets]


def _support_id(evidence_id: str, start: int, end: int, quote: str) -> str:
    return "support-" + sha256_canonical(
        {
            "evidence_id": evidence_id,
            "start": start,
            "end": end,
            "quote_sha256": hashlib.sha256(quote.encode("utf-8")).hexdigest(),
        }
    )[:32]


def build_source_answer_brief(
    snapshot: EnsembleSnapshot,
    query: str,
    top_k: int,
    per_facet: int,
    maximum_facets: int,
    *,
    evidence_pack: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Expose compact exact support handles for claimless answer finalization."""

    if snapshot.index.get("schema_version") != GENERIC_SCHEMA_VERSION:
        raise SnapshotError("answer-brief is available only for source-generic schema 2.0")
    if snapshot.adaptive.answer_bindings:
        raise SnapshotError("answer-brief is unavailable when reviewed claim bindings exist")
    if not isinstance(query, str) or not query.strip():
        raise SnapshotError("query must be nonempty")
    maximum_evidence = _plain_int(top_k, "top-k", 1, 100)
    per_facet_limit = _plain_int(per_facet, "per-facet", 1, 12)
    facet_limit = _plain_int(maximum_facets, "maximum facets", 1, 32)
    pack = (
        evidence_pack
        if evidence_pack is not None
        else build_evidence_pack(snapshot, query.strip(), maximum_evidence)
    )
    facets = _answer_brief_facets(snapshot, query.strip(), facet_limit)
    plan = snapshot.adaptive.index["plan"]
    idf = {
        row["term"]: float(row["idf"])
        for row in snapshot.adaptive.lexicon["terms"]
    }
    full_tokens = set(adaptive_runtime.tokenize(query, plan))
    candidates: list[dict[str, Any]] = []
    for evidence in pack["evidence_rows"]:
        text = evidence["text"]
        for start, end, quote in _bounded_quote_spans(text):
            quote_tokens = set(adaptive_runtime.tokenize(quote, plan))
            if not quote_tokens:
                continue
            candidates.append(
                {
                    "evidence": evidence,
                    "start": start,
                    "end": end,
                    "quote": quote,
                    "quote_tokens": quote_tokens,
                    "full_overlap": sum(
                        idf.get(token, 1.0) for token in full_tokens & quote_tokens
                    ),
                }
            )

    facet_rows: list[dict[str, Any]] = []
    all_supports: dict[str, dict[str, Any]] = {}
    preferred_evidence_ids = [
        row["evidence_id"] for row in pack["evidence_rows"][:2]
    ]
    for facet in facets:
        facet_tokens = set(adaptive_runtime.tokenize(facet, plan))
        denominator = sum(idf.get(token, 1.0) for token in facet_tokens) or 1.0
        association_weights, _ = adaptive_runtime._association_expansion(
            facet,
            snapshot.adaptive,
        )
        topic_weights, _, _ = adaptive_runtime._topic_expansion(
            facet,
            association_weights,
            snapshot.adaptive,
        )
        expanded_weights = dict(association_weights)
        for term, weight in topic_weights.items():
            expanded_weights[term] = max(expanded_weights.get(term, 0.0), float(weight))
        ranked: list[tuple[tuple[Any, ...], dict[str, Any]]] = []
        for candidate in candidates:
            overlap = facet_tokens & candidate["quote_tokens"]
            expanded_overlap = set(expanded_weights) & candidate["quote_tokens"]
            if not overlap and not expanded_overlap:
                continue
            weighted = sum(idf.get(token, 1.0) for token in overlap)
            coverage = weighted / denominator
            density = weighted / math.sqrt(max(1, len(candidate["quote_tokens"])))
            expansion = sum(expanded_weights[token] for token in expanded_overlap)
            evidence = candidate["evidence"]
            score = round(
                10.0 * coverage
                + density
                + 2.0 * expansion
                + 0.01 * candidate["full_overlap"],
                12,
            )
            ranked.append(
                (
                    (
                        -score,
                        int(evidence["rank"]),
                        evidence["evidence_id"],
                        candidate["start"],
                    ),
                    candidate,
                )
            )
        selected: list[dict[str, Any]] = []
        seen_evidence: set[str] = set()
        ranked_candidates = sorted(ranked, key=lambda item: item[0])
        protected_candidates: list[dict[str, Any]] = []
        for evidence_id in preferred_evidence_ids:
            match = next(
                (
                    candidate
                    for _, candidate in ranked_candidates
                    if candidate["evidence"]["evidence_id"] == evidence_id
                ),
                None,
            )
            if match is not None:
                protected_candidates.append(match)
        ordered_candidates = [
            *protected_candidates,
            *(candidate for _, candidate in ranked_candidates),
        ]
        for candidate in ordered_candidates:
            evidence = candidate["evidence"]
            evidence_id = evidence["evidence_id"]
            if evidence_id in seen_evidence:
                continue
            seen_evidence.add(evidence_id)
            support_id = _support_id(
                evidence_id,
                candidate["start"],
                candidate["end"],
                candidate["quote"],
            )
            support = {
                "support_id": support_id,
                "evidence_id": evidence_id,
                "source_id": evidence["source_id"],
                "record_id": evidence["record_id"],
                "concept_path": evidence["concept_path"],
                "source_path": evidence["source_path"],
                "record_sha256": evidence["record_sha256"],
                "quote_locator": {
                    "target": "record-body",
                    "kind": "character-range",
                    "start": candidate["start"],
                    "end": candidate["end"],
                    "fragment": None,
                },
                "quote": candidate["quote"],
                "quote_sha256": hashlib.sha256(
                    candidate["quote"].encode("utf-8")
                ).hexdigest(),
            }
            all_supports[support_id] = support
            selected.append(support)
            if len(selected) == per_facet_limit:
                break
        facet_rows.append({"facet": facet, "supports": selected})

    return {
        "schema_version": GENERIC_ANSWER_BRIEF_SCHEMA_VERSION,
        "status": "pass",
        "authoritative": False,
        "discovery_only": True,
        "algorithm": GENERIC_ANSWER_BRIEF_ALGORITHM_ID,
        "query": query.strip(),
        "top_k": maximum_evidence,
        "per_facet": per_facet_limit,
        "maximum_facets": facet_limit,
        "facets": facet_rows,
        "support_count": len(all_supports),
        "evidence_pack": {
            "returned": pack["returned"],
            "ensemble_index_sha256": pack["ensemble"]["ensemble_index_sha256"],
            "core_tree_sha256": pack["ensemble"]["core_tree_sha256"],
        },
        "contract": {
            "support_ids_recomputed_by_finalizer": True,
            "quotes_are_exact_authoritative_substrings": True,
            "support_is_not_a_reviewed_claim": True,
        },
    }


def _require_claim_bindings(snapshot: EnsembleSnapshot, operation: str) -> None:
    if (
        snapshot.index.get("schema_version") == GENERIC_SCHEMA_VERSION
        and not snapshot.adaptive.answer_bindings
    ):
        raise SnapshotError(
            f"{operation} is claim-only and requires reviewed exact answer bindings; "
            "this v2 snapshot is claimless, so use search or evidence-pack for exact "
            "authoritative passage evidence"
        )


def _graph_claim_candidates(
    snapshot: EnsembleSnapshot,
    query: str,
    maximum: int,
) -> list[dict[str, Any]]:
    resolved = graph_runtime._resolve_entities(snapshot.graph, query)
    entity_by_id = {entity["entity_id"]: entity for entity in snapshot.graph.entities}
    adjacency: dict[str, list[tuple[str, Mapping[str, Any]]]] = defaultdict(list)
    for edge in snapshot.graph.edges:
        if edge["review_state"] != "reviewed":
            continue
        adjacency[edge["source_node"]].append((edge["target_node"], edge))
        adjacency[edge["target_node"]].append((edge["source_node"], edge))
    best: dict[str, float] = {}
    frontier: dict[str, float] = {}
    for row in resolved:
        entity = entity_by_id.get(row["entity_id"])
        multiplier = (
            2.0
            if entity is not None
            and entity["entity_type"] == "claim"
            and entity["review_state"] == "reviewed"
            else 1.0
        )
        score = float(row["score"]) * multiplier
        best[row["entity_id"]] = max(best.get(row["entity_id"], 0.0), score)
        frontier[row["entity_id"]] = max(frontier.get(row["entity_id"], 0.0), score)
    for hop in range(1, 3):
        following: dict[str, float] = {}
        for node, node_score in sorted(frontier.items()):
            for neighbor, edge in adjacency.get(node, []):
                bounded = float(edge["weight"]) / (1.0 + float(edge["weight"]))
                propagated = node_score * bounded * (0.65**hop)
                if propagated <= best.get(neighbor, 0.0):
                    continue
                best[neighbor] = propagated
                following[neighbor] = max(following.get(neighbor, 0.0), propagated)
        frontier = following
        if not frontier:
            break
    bindings = {
        str(binding["record_id"]): binding for binding in snapshot.adaptive.answer_bindings
    }
    rows: list[dict[str, Any]] = []
    for entity_id in sorted(best, key=lambda value: (-best[value], value)):
        entity = entity_by_id.get(entity_id)
        if (
            entity is None
            or entity["entity_type"] != "claim"
            or entity["review_state"] != "reviewed"
            or not isinstance(entity["authoritative_identity"], dict)
        ):
            continue
        claim_id = entity["authoritative_identity"]["record_id"]
        binding = bindings.get(claim_id)
        if binding is None:
            continue
        rows.append(
            {
                "rank": len(rows) + 1,
                "claim_id": claim_id,
                "paper_id": binding["paper_id"],
                "score": round(best[entity_id], 12),
                "concept_path": binding["concept_path"],
                "source_path": binding["source_path"],
                "locators": sorted(set(binding["locator_tokens"])),
                "citation_pages": sorted(set(binding["citation_pages"])),
                "authoritative_text": binding["authoritative_text"],
                "authoritative_text_sha256": binding["authoritative_text_sha256"],
                "review_state": "reviewed",
            }
        )
        if len(rows) == maximum:
            break
    return rows


def _embedding_claim_candidates(
    snapshot: EnsembleSnapshot,
    query: str,
    maximum: int,
    preferred_paper_ids: Sequence[str] = (),
) -> list[dict[str, Any]]:
    """Retrieve reviewed claims and deterministically diversify over leading papers."""

    bindings = {
        str(binding["record_id"]): binding
        for binding in snapshot.adaptive.answer_bindings
        if binding.get("review_state") == "reviewed"
    }
    claim_sources = tuple(sorted({str(binding["source_id"]) for binding in bindings.values()}))
    result = _run_route(
        snapshot,
        "embedding_hybrid",
        query,
        max(maximum, min(len(bindings), maximum * EMBEDDING_CANDIDATE_POOL_MULTIPLIER)),
        source_ids=claim_sources,
        concept_ids=(),
        concept_types=(),
    )
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for hit in result.get("hits", []):
        if not isinstance(hit, Mapping):
            continue
        claim_id = str(hit.get("record_id", ""))
        binding = bindings.get(claim_id)
        if binding is None or claim_id in seen:
            continue
        if any(
            hit.get(key) != binding[key]
            for key in ("source_id", "source_path", "concept_path")
        ):
            raise SnapshotError(
                f"embedding claim candidate {claim_id} differs from its exact answer binding"
            )
        scores = hit.get("scores")
        if not isinstance(scores, Mapping) or not isinstance(scores.get("hybrid"), (int, float)):
            raise SnapshotError(f"embedding claim candidate {claim_id} has no finite hybrid score")
        score = float(scores["hybrid"])
        if not math.isfinite(score):
            raise SnapshotError(f"embedding claim candidate {claim_id} has no finite hybrid score")
        seen.add(claim_id)
        rows.append(
            {
                "rank": len(rows) + 1,
                "claim_id": claim_id,
                "paper_id": binding["paper_id"],
                "score": round(score, 12),
                "concept_path": binding["concept_path"],
                "source_path": binding["source_path"],
                "locators": sorted(set(binding["locator_tokens"])),
                "citation_pages": sorted(set(binding["citation_pages"])),
                "authoritative_text": binding["authoritative_text"],
                "authoritative_text_sha256": binding["authoritative_text_sha256"],
                "review_state": "reviewed",
            }
        )
    selected: list[dict[str, Any]] = []
    selected_ids: set[str] = set()

    def retain(row: dict[str, Any]) -> None:
        claim_id = str(row["claim_id"])
        if claim_id not in selected_ids and len(selected) < maximum:
            selected_ids.add(claim_id)
            selected.append(row)

    for row in rows[: min(EMBEDDING_GLOBAL_PREFIX, maximum)]:
        retain(row)
    preferred: list[str] = []
    for paper_id in preferred_paper_ids:
        if isinstance(paper_id, str) and paper_id and paper_id not in preferred:
            preferred.append(paper_id)
        if len(preferred) == EMBEDDING_PREFERRED_PAPERS:
            break
    for paper_id in preferred:
        paper_rank = 0
        for row in rows:
            if row["paper_id"] != paper_id:
                continue
            paper_rank += 1
            retain(row)
            if paper_rank == EMBEDDING_CLAIMS_PER_PREFERRED_PAPER:
                break
    for row in rows:
        retain(row)
        if len(selected) == maximum:
            break
    return [dict(row, rank=rank) for rank, row in enumerate(selected, 1)]


def build_coverage_pack(
    snapshot: EnsembleSnapshot,
    query: str,
    top_k: int,
    per_facet: int,
    maximum_facets: int,
) -> dict[str, Any]:
    """Union adaptive facets with bounded reviewed graph and semantic claim routes."""

    _require_claim_bindings(snapshot, "coverage-pack")
    adaptive = adaptive_runtime.build_coverage_pack(
        snapshot.adaptive,
        query,
        top_k,
        per_facet,
        maximum_facets,
    )
    gates = snapshot.index["plan"]["quality_gates"]
    maximum_per_facet = int(gates["maximum_graph_claims_per_facet"])
    maximum_total = int(gates["maximum_graph_claims_total"])
    maximum_embedding_per_facet = int(gates["maximum_embedding_claims_per_facet"])
    maximum_embedding_total = int(gates["maximum_embedding_claims_total"])
    graph_queries = [query]
    graph_queries.extend(
        row["facet"]
        for row in adaptive["coverage_facets"]
        if row["facet"] != query and row["facet"] not in graph_queries
    )
    selected_graph_ids: set[str] = set()
    graph_rows: list[dict[str, Any]] = []
    for number, facet in enumerate(graph_queries):
        candidates = _graph_claim_candidates(snapshot, facet, maximum_per_facet)
        bounded: list[dict[str, Any]] = []
        for candidate in candidates:
            claim_id = candidate["claim_id"]
            if claim_id in selected_graph_ids:
                continue
            if len(selected_graph_ids) >= maximum_total:
                continue
            selected_graph_ids.add(claim_id)
            bounded.append(candidate)
        graph_rows.append(
            {
                "query_kind": "full" if number == 0 else "facet",
                "facet": facet,
                "returned": len(bounded),
                "candidates": bounded,
            }
        )
    selected_embedding_ids: set[str] = set()
    embedding_rows: list[dict[str, Any]] = []
    preferred_embedding_papers: list[str] = []
    for binding in adaptive["primary"]["ranked_bindings"]:
        paper_id = binding.get("paper_id")
        if (
            isinstance(paper_id, str)
            and paper_id
            and paper_id not in preferred_embedding_papers
        ):
            preferred_embedding_papers.append(paper_id)
        if len(preferred_embedding_papers) == EMBEDDING_PREFERRED_PAPERS:
            break
    for number, facet in enumerate(graph_queries):
        candidates = _embedding_claim_candidates(
            snapshot,
            facet,
            maximum_embedding_per_facet,
            preferred_embedding_papers,
        )
        bounded: list[dict[str, Any]] = []
        for candidate in candidates:
            claim_id = candidate["claim_id"]
            if claim_id in selected_embedding_ids:
                continue
            if len(selected_embedding_ids) >= maximum_embedding_total:
                continue
            selected_embedding_ids.add(claim_id)
            bounded.append(candidate)
        embedding_rows.append(
            {
                "query_kind": "full" if number == 0 else "facet",
                "facet": facet,
                "returned": len(bounded),
                "candidates": bounded,
            }
        )
    adaptive_ids = {
        row["record_id"] for row in adaptive["primary"]["ranked_bindings"]
    }
    for row in adaptive["coverage_facets"]:
        adaptive_ids.update(candidate["claim_id"] for candidate in row["candidates"])
    union = sorted(adaptive_ids | selected_graph_ids | selected_embedding_ids)
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "pass",
        "authoritative": False,
        "discovery_only": True,
        "query": query,
        "algorithm": COVERAGE_ALGORITHM_ID,
        "top_k": top_k,
        "per_facet": per_facet,
        "maximum_facets": maximum_facets,
        "adaptive": adaptive,
        "graph_queries": graph_rows,
        "embedding_queries": embedding_rows,
        "adaptive_candidate_claims": len(adaptive_ids),
        "graph_candidate_claims": len(selected_graph_ids),
        "embedding_candidate_claims": len(selected_embedding_ids),
        "unique_candidate_claims": len(union),
        "union_claim_ids": union,
        "gates": {
            "reviewed_graph_claims_only": True,
            "reviewed_embedding_claims_only": True,
            "candidate_edge_weight": 0.0,
            "maximum_graph_claims_per_facet": maximum_per_facet,
            "maximum_graph_claims_total": maximum_total,
            "maximum_embedding_claims_per_facet": maximum_embedding_per_facet,
            "maximum_embedding_claims_total": maximum_embedding_total,
            "exact_answer_bindings": True,
            "limits_passed": all(row["returned"] <= maximum_per_facet for row in graph_rows)
            and len(selected_graph_ids) <= maximum_total
            and all(
                row["returned"] <= maximum_embedding_per_facet
                for row in embedding_rows
            )
            and len(selected_embedding_ids) <= maximum_embedding_total,
        },
        "snapshot": {
            "core_tree_sha256": snapshot.index["core"]["tree_sha256"],
            "ensemble_index_sha256": snapshot.index_sha256,
        },
        "coverage_contract": {
            "graph_role": "candidate discovery only",
            "embedding_role": (
                "reviewed claim candidate discovery only; "
                f"{EMBEDDING_CLAIM_RERANK_ID}"
            ),
            "candidate_edges_establish_facts": False,
            "authoritative_verification_required": True,
            "facet_status_required_before_finalization": True,
            "finalizer": ANSWER_GATE_ID,
        },
    }


def _coverage_brief_bindings(snapshot: EnsembleSnapshot) -> dict[str, Mapping[str, Any]]:
    """Index reviewed answer bindings by authoritative claim ID."""

    bindings: dict[str, Mapping[str, Any]] = {}
    for binding in snapshot.adaptive.answer_bindings:
        if binding.get("review_state") != "reviewed":
            continue
        claim_id = str(binding.get("record_id", ""))
        if not claim_id:
            raise SnapshotError("reviewed answer binding has no claim ID")
        if claim_id in bindings:
            raise SnapshotError(f"reviewed answer binding claim ID is not unique: {claim_id}")
        bindings[claim_id] = binding
    return bindings


def _coverage_brief_claim_id(candidate: Mapping[str, Any], route: str) -> str:
    """Resolve one route candidate to its exact reviewed claim ID."""

    key = "record_id" if route == "adaptive_primary" else "claim_id"
    claim_id = candidate.get(key)
    if not isinstance(claim_id, str) or not claim_id:
        raise SnapshotError(f"coverage brief {route} candidate has no claim ID")
    return claim_id


def _validate_coverage_brief_candidate(
    candidate: Mapping[str, Any],
    binding: Mapping[str, Any],
    claim_id: str,
) -> None:
    """Fail when a projected route row differs from its exact answer binding."""

    if candidate.get("review_state", "reviewed") != "reviewed":
        raise SnapshotError(f"coverage brief candidate is not reviewed: {claim_id}")
    for key in ("paper_id", "authoritative_text", "authoritative_text_sha256"):
        if key in candidate and candidate[key] != binding[key]:
            raise SnapshotError(
                f"coverage brief candidate {claim_id} differs from its answer binding: {key}"
            )
    if "citation_pages" in candidate and sorted(set(candidate["citation_pages"])) != sorted(
        set(binding["citation_pages"])
    ):
        raise SnapshotError(
            f"coverage brief candidate {claim_id} differs from its answer binding: citation_pages"
        )


def _idf_cosine(
    left: set[str], right: set[str], idf: Mapping[str, float]
) -> float:
    """Return deterministic persisted-IDF cosine similarity for two token sets."""

    left_norm = math.sqrt(sum(idf.get(token, 0.0) ** 2 for token in left))
    right_norm = math.sqrt(sum(idf.get(token, 0.0) ** 2 for token in right))
    if left_norm == 0.0 or right_norm == 0.0:
        return 0.0
    numerator = sum(idf.get(token, 0.0) ** 2 for token in left & right)
    return numerator / (left_norm * right_norm)


def _coverage_brief_priority_order(
    snapshot: EnsembleSnapshot,
    claims: Mapping[str, Mapping[str, Any]],
    query: str,
    facets: Sequence[str],
) -> list[str]:
    """Order the complete claim union by reproducible relevance and consensus signals."""

    lexicon = snapshot.adaptive.lexicon
    if not isinstance(lexicon, dict):
        raise SnapshotError("coverage brief requires the persisted adaptive lexicon")
    tokenization = lexicon.get("tokenization")
    terms = lexicon.get("terms")
    if not isinstance(tokenization, dict) or not isinstance(terms, list):
        raise SnapshotError("coverage brief adaptive lexicon is malformed")
    idf: dict[str, float] = {}
    for number, row in enumerate(terms, start=1):
        if not isinstance(row, dict):
            raise SnapshotError(f"coverage brief lexicon term {number} is malformed")
        term = row.get("term")
        value = row.get("idf")
        if (
            not isinstance(term, str)
            or not term
            or isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(float(value))
            or float(value) < 0.0
        ):
            raise SnapshotError(f"coverage brief lexicon term {number} is invalid")
        if term in idf:
            raise SnapshotError(f"coverage brief lexicon repeats term {term!r}")
        idf[term] = float(value)

    token_plan = {"tokenization": tokenization}
    query_values = [query, *(facet for facet in facets if facet != query)]
    query_tokens = [
        set(adaptive_runtime.tokenize(value, token_plan)) for value in query_values
    ]

    def priority(claim_id: str) -> tuple[Any, ...]:
        claim = claims[claim_id]
        claim_tokens = set(
            adaptive_runtime.tokenize(str(claim["authoritative_text"]), token_plan)
        )
        lexical = max(
            (_idf_cosine(tokens, claim_tokens, idf) for tokens in query_tokens),
            default=0.0,
        )
        provenance = claim.get("provenance")
        if not isinstance(provenance, list) or not provenance:
            raise SnapshotError(f"coverage brief claim has no provenance: {claim_id}")
        routes: set[str] = set()
        facet_keys: set[tuple[str, int | None]] = set()
        full_routes = 0
        weighted_rrf = 0.0
        for row in provenance:
            if not isinstance(row, dict):
                raise SnapshotError(f"coverage brief provenance is malformed: {claim_id}")
            route = row.get("route")
            rank = row.get("rank")
            query_kind = row.get("query_kind")
            facet_index = row.get("facet_index")
            if route not in COVERAGE_BRIEF_ROUTE_WEIGHTS:
                raise SnapshotError(f"coverage brief route is unsupported: {route!r}")
            if isinstance(rank, bool) or not isinstance(rank, int) or rank < 1:
                raise SnapshotError(f"coverage brief rank is invalid: {claim_id}")
            if query_kind not in {"full", "facet"}:
                raise SnapshotError(f"coverage brief query kind is invalid: {claim_id}")
            if facet_index is not None and (
                isinstance(facet_index, bool)
                or not isinstance(facet_index, int)
                or facet_index < 1
            ):
                raise SnapshotError(f"coverage brief facet index is invalid: {claim_id}")
            routes.add(route)
            facet_keys.add((query_kind, facet_index))
            full_routes += int(query_kind == "full")
            weighted_rrf += COVERAGE_BRIEF_ROUTE_WEIGHTS[route] / (
                COVERAGE_BRIEF_RRF_K + rank
            )
        return (
            -round(lexical, 12),
            -len(routes),
            -len(facet_keys),
            -full_routes,
            -round(weighted_rrf, 12),
            str(claim["paper_id"]),
            claim_id,
        )

    return sorted(claims, key=priority)


def build_coverage_brief(
    snapshot: EnsembleSnapshot,
    query: str,
    top_k: int,
    per_facet: int,
    maximum_facets: int,
    page: int,
    page_size: int,
) -> dict[str, Any]:
    """Page every full-pack claim through a compact reviewed discovery view."""

    _require_claim_bindings(snapshot, "coverage-brief")
    requested_page = _plain_int(page, "coverage brief page", 1, 1_000_000)
    requested_page_size = _plain_int(page_size, "coverage brief page size", 1, 48)
    coverage = build_coverage_pack(snapshot, query, top_k, per_facet, maximum_facets)
    adaptive = coverage["adaptive"]
    facet_rows = adaptive["coverage_facets"]
    required_facets = [str(row["facet"]) for row in facet_rows]
    if not required_facets:
        required_facets = [query.strip()]
    if len(set(required_facets)) != len(required_facets):
        raise SnapshotError("coverage brief requires unique derived facets")
    facet_indexes = {facet: number for number, facet in enumerate(required_facets, start=1)}
    facets = [
        {"facet_index": number, "facet": facet}
        for number, facet in enumerate(required_facets, start=1)
    ]

    adaptive_by_facet = {str(row["facet"]): row for row in facet_rows}
    if len(adaptive_by_facet) != len(facet_rows):
        raise SnapshotError("coverage brief adaptive facets are not unique")
    graph_by_query = {
        (str(row["query_kind"]), str(row["facet"])): row
        for row in coverage["graph_queries"]
    }
    embedding_by_query = {
        (str(row["query_kind"]), str(row["facet"])): row
        for row in coverage["embedding_queries"]
    }
    if len(graph_by_query) != len(coverage["graph_queries"]):
        raise SnapshotError("coverage brief graph route rows are not unique")
    if len(embedding_by_query) != len(coverage["embedding_queries"]):
        raise SnapshotError("coverage brief embedding route rows are not unique")

    gates = coverage["gates"]
    route_specs: list[
        tuple[str, str, int | None, str, int, Sequence[Mapping[str, Any]]]
    ] = []
    full_facet_index = facet_indexes.get(query)
    route_specs.append(
        (
            "adaptive_primary",
            "full",
            full_facet_index,
            query,
            top_k,
            adaptive["primary"]["ranked_bindings"],
        )
    )
    if query in adaptive_by_facet:
        route_specs.append(
            (
                "adaptive_facet",
                "facet",
                facet_indexes[query],
                query,
                per_facet,
                adaptive_by_facet[query]["candidates"],
            )
        )
    for route, rows, route_limit in (
        (
            "entity_graph",
            graph_by_query,
            int(gates["maximum_graph_claims_per_facet"]),
        ),
        (
            "embedding_hybrid",
            embedding_by_query,
            int(gates["maximum_embedding_claims_per_facet"]),
        ),
    ):
        row = rows.get(("full", query))
        if row is None:
            raise SnapshotError(f"coverage brief is missing the full {route} route")
        route_specs.append(
            (route, "full", full_facet_index, query, route_limit, row["candidates"])
        )
    for facet in required_facets:
        if facet != query:
            adaptive_row = adaptive_by_facet.get(facet)
            if adaptive_row is None:
                raise SnapshotError(f"coverage brief is missing adaptive facet: {facet}")
            route_specs.append(
                (
                    "adaptive_facet",
                    "facet",
                    facet_indexes[facet],
                    facet,
                    per_facet,
                    adaptive_row["candidates"],
                )
            )
        for route, rows, route_limit in (
            (
                "entity_graph",
                graph_by_query,
                int(gates["maximum_graph_claims_per_facet"]),
            ),
            (
                "embedding_hybrid",
                embedding_by_query,
                int(gates["maximum_embedding_claims_per_facet"]),
            ),
        ):
            row = rows.get(("facet", facet))
            if row is None:
                if facet == query:
                    continue
                raise SnapshotError(f"coverage brief is missing {route} facet: {facet}")
            route_specs.append(
                (
                    route,
                    "facet",
                    facet_indexes[facet],
                    facet,
                    route_limit,
                    row["candidates"],
                )
            )

    bindings = _coverage_brief_bindings(snapshot)
    claims: dict[str, dict[str, Any]] = {}
    full_routes: list[dict[str, Any]] = []
    full_candidate_references = 0
    full_union = set(coverage["union_claim_ids"])
    for route, query_kind, facet_index, facet, route_limit, candidates in route_specs:
        if len(candidates) > route_limit:
            raise SnapshotError(f"coverage brief {route} route exceeds its full-pack bound")
        claim_ids: list[str] = []
        for position, candidate in enumerate(candidates, start=1):
            claim_id = _coverage_brief_claim_id(candidate, route)
            if claim_id in claim_ids:
                raise SnapshotError(
                    f"coverage brief {route} route repeats claim ID {claim_id}"
                )
            binding = bindings.get(claim_id)
            if binding is None:
                raise SnapshotError(
                    f"coverage brief candidate has no reviewed answer binding: {claim_id}"
                )
            if claim_id not in full_union:
                raise SnapshotError(
                    f"coverage brief candidate falls outside full coverage: {claim_id}"
                )
            _validate_coverage_brief_candidate(candidate, binding, claim_id)
            rank = candidate.get("rank", position)
            if isinstance(rank, bool) or not isinstance(rank, int) or rank < 1:
                raise SnapshotError(f"coverage brief candidate {claim_id} has an invalid rank")
            claim_ids.append(claim_id)
            full_candidate_references += 1
            claim = claims.setdefault(
                claim_id,
                {
                    "claim_id": claim_id,
                    "paper_id": binding["paper_id"],
                    "authoritative_text": binding["authoritative_text"],
                    "authoritative_text_sha256": binding["authoritative_text_sha256"],
                    "citation_pages": sorted(set(binding["citation_pages"])),
                    "review_state": "reviewed",
                    "provenance": [],
                },
            )
            claim["provenance"].append(
                {
                    "query_kind": query_kind,
                    "facet_index": facet_index,
                    "route": route,
                    "rank": rank,
                }
            )
        full_routes.append(
            {
                "query_kind": query_kind,
                "facet_index": facet_index,
                "facet": facet,
                "route": route,
                "candidate_limit": route_limit,
                "total_candidates": len(claim_ids),
                "candidate_claim_ids": claim_ids,
            }
        )

    if set(claims) != full_union:
        missing = sorted(full_union - set(claims))
        unexpected = sorted(set(claims) - full_union)
        raise SnapshotError(
            "coverage brief must page the entire full coverage union; "
            f"missing={missing}, unexpected={unexpected}"
        )
    ordered_claim_ids = _coverage_brief_priority_order(
        snapshot,
        claims,
        query,
        required_facets,
    )
    priority_order_sha256 = sha256_canonical(ordered_claim_ids)
    total_pages = max(1, math.ceil(len(ordered_claim_ids) / requested_page_size))
    if requested_page > total_pages:
        raise SnapshotError(
            f"coverage brief page {requested_page} exceeds total pages {total_pages}"
        )
    start = (requested_page - 1) * requested_page_size
    page_claim_ids = ordered_claim_ids[start : start + requested_page_size]
    page_claim_id_set = set(page_claim_ids)
    ordered_claims = [claims[claim_id] for claim_id in page_claim_ids]
    routes = [
        {
            "query_kind": row["query_kind"],
            "facet_index": row["facet_index"],
            "facet": row["facet"],
            "route": row["route"],
            "candidate_limit": row["candidate_limit"],
            "total_candidates": row["total_candidates"],
            "page_candidates": len(
                [
                    claim_id
                    for claim_id in row["candidate_claim_ids"]
                    if claim_id in page_claim_id_set
                ]
            ),
            "candidate_claim_ids": [
                claim_id
                for claim_id in row["candidate_claim_ids"]
                if claim_id in page_claim_id_set
            ],
        }
        for row in full_routes
    ]
    page_candidate_references = sum(row["page_candidates"] for row in routes)
    return {
        "schema_version": COVERAGE_BRIEF_SCHEMA_VERSION,
        "status": "pass",
        "authoritative": False,
        "discovery_only": True,
        "query": query,
        "algorithm": COVERAGE_BRIEF_ALGORITHM_ID,
        "parameters": {
            "top_k": top_k,
            "per_facet": per_facet,
            "maximum_facets": maximum_facets,
            "page": requested_page,
            "page_size": requested_page_size,
        },
        "pagination": {
            "page": requested_page,
            "page_size": requested_page_size,
            "total_pages": total_pages,
            "total_claims": len(ordered_claim_ids),
            "has_more": requested_page < total_pages,
            "next_page": requested_page + 1 if requested_page < total_pages else None,
        },
        "facets": facets,
        "routes": routes,
        "claims": ordered_claims,
        "counts": {
            "facets": len(facets),
            "route_rows": len(routes),
            "page_candidate_references": page_candidate_references,
            "full_candidate_references": full_candidate_references,
            "page_unique_claims": len(ordered_claims),
            "full_unique_claims": int(coverage["unique_candidate_claims"]),
        },
        "full_coverage": {
            "algorithm": coverage["algorithm"],
            "sha256": sha256_canonical(coverage),
            "priority_order": COVERAGE_BRIEF_ORDER_ID,
            "priority_order_sha256": priority_order_sha256,
            "unique_claims": len(ordered_claim_ids),
            "recomputed": True,
            "emitted": False,
        },
        "snapshot": dict(coverage["snapshot"]),
        "brief_contract": {
            "closed_schema": True,
            "reviewed_claims_only": all(
                claim["review_state"] == "reviewed" for claim in ordered_claims
            ),
            "page_claims_within_full_coverage": page_claim_id_set <= full_union,
            "all_full_claims_paged": set(claims) == full_union,
            "read_every_page_before_drafting": True,
            "candidate_role": "draft discovery only",
            "stable_ordering": (
                "facets in finalizer order; routes in fixed full/facet route order; "
                f"pages and claims by {COVERAGE_BRIEF_ORDER_ID}; provenance in route order"
            ),
            "finalizer_recomputes_full_coverage": True,
            "finalizer": ANSWER_GATE_ID,
        },
    }


def _draft_payload(
    snapshot: EnsembleSnapshot,
    raw_payload: str,
    query: str,
    coverage: Mapping[str, Any],
) -> str:
    draft = adaptive_runtime.strict_json_loads(raw_payload, label="ensemble answer draft")
    if not isinstance(draft, dict):
        raise SnapshotError("ensemble answer draft root must be an object")
    _exact_keys(draft, {"summary", "facets"}, "ensemble answer draft")
    summary = draft["summary"]
    if not isinstance(summary, str) or not summary.strip():
        raise SnapshotError("ensemble answer draft summary must be nonempty")
    facets = draft["facets"]
    if not isinstance(facets, list) or not facets:
        raise SnapshotError("ensemble answer draft facets must be a nonempty array")
    expected_facets = adaptive_runtime.decompose_coverage_facets(
        query,
        snapshot.adaptive.index["plan"],
        int(coverage["maximum_facets"]),
    )
    if not expected_facets:
        expected_facets = [query.strip()]
    if len(facets) != len(expected_facets):
        raise SnapshotError("ensemble answer draft must account for every derived facet exactly once")
    allowed = set(coverage["union_claim_ids"])
    claims: list[dict[str, Any]] = []
    supported = 0
    for number, (raw, expected) in enumerate(zip(facets, expected_facets), start=1):
        if not isinstance(raw, dict):
            raise SnapshotError(f"ensemble answer draft facet {number} must be an object")
        _exact_keys(
            raw,
            {"facet", "status", "statement", "supporting_claim_ids"},
            f"ensemble answer draft facet {number}",
        )
        if raw["facet"] != expected:
            raise SnapshotError(
                f"ensemble answer draft facet {number} must equal the derived facet {expected!r}"
            )
        status = raw["status"]
        if status not in {"supported", "partial", "unresolved"}:
            raise SnapshotError(
                f"ensemble answer draft facet {number} status must be supported, partial, or unresolved"
            )
        statement = raw["statement"]
        identifiers = raw["supporting_claim_ids"]
        if not isinstance(statement, str) or not statement.strip():
            raise SnapshotError(f"ensemble answer draft facet {number} statement must be nonempty")
        if not isinstance(identifiers, list) or any(
            not isinstance(identifier, str) for identifier in identifiers
        ):
            raise SnapshotError(
                f"ensemble answer draft facet {number} supporting IDs must be a string array"
            )
        ordered = sorted(set(identifiers))
        if status == "unresolved" and ordered:
            raise SnapshotError(
                f"ensemble answer draft facet {number} unresolved status must not cite claims"
            )
        if status != "unresolved" and not ordered:
            raise SnapshotError(
                f"ensemble answer draft facet {number} {status} status requires supporting claims"
            )
        unknown = sorted(set(ordered) - allowed)
        if unknown:
            raise SnapshotError(
                f"ensemble answer draft facet {number} cites claims outside the gated coverage pack: {unknown}"
            )
        if status != "unresolved":
            supported += 1
            claims.append(
                {"statement": statement.strip(), "supporting_claim_ids": ordered}
            )
    if supported == 0:
        raise SnapshotError("ensemble answer draft cannot mark every facet unresolved")
    return canonical_json({"summary": summary.strip(), "claims": claims})


def finalize_answer(
    snapshot: EnsembleSnapshot,
    draft_path: Path | None,
    question_id: str,
    query: str,
    minimum_summary_words: int,
    maximum_summary_words: int,
    *,
    top_k: int = 30,
    per_facet: int = 12,
    maximum_facets: int = 12,
    draft_payload: str | None = None,
) -> dict[str, Any]:
    """Enforce facet status and candidate gates, then rebuild exact evidence."""

    if (
        snapshot.index.get("schema_version") == GENERIC_SCHEMA_VERSION
        and not snapshot.adaptive.answer_bindings
    ):
        return _finalize_source_answer(
            snapshot,
            draft_path,
            question_id,
            query,
            minimum_summary_words,
            maximum_summary_words,
            top_k=top_k,
            per_facet=per_facet,
            maximum_facets=maximum_facets,
            draft_payload=draft_payload,
        )
    _require_claim_bindings(snapshot, "finalize-answer")
    if not isinstance(query, str) or not query.strip():
        raise SnapshotError("query must be nonempty")
    if (draft_path is None) == (draft_payload is None):
        raise SnapshotError("provide exactly one answer draft path or standard-input payload")
    if draft_payload is None:
        assert draft_path is not None
        try:
            resolved = draft_path.expanduser().resolve(strict=True)
            resolved.relative_to(snapshot.root)
        except ValueError:
            pass
        except OSError as exc:
            raise SnapshotError(f"cannot read answer draft: {exc}") from exc
        else:
            raise SnapshotError("answer draft must remain outside the immutable bundle")
        draft_payload = resolved.read_text(encoding="utf-8")
    coverage = build_coverage_pack(
        snapshot,
        query,
        top_k,
        per_facet,
        maximum_facets,
    )
    adaptive_payload = _draft_payload(snapshot, draft_payload, query, coverage)
    return adaptive_runtime.finalize_answer(
        snapshot.adaptive,
        None,
        question_id,
        minimum_summary_words,
        maximum_summary_words,
        draft_payload=adaptive_payload,
    )


def _generic_answer_draft(
    snapshot: EnsembleSnapshot,
    draft_path: Path | None,
    draft_payload: str | None,
) -> dict[str, Any]:
    """Load one closed-schema draft without permitting writes inside the snapshot."""

    if (draft_path is None) == (draft_payload is None):
        raise SnapshotError("provide exactly one answer draft path or standard-input payload")
    if draft_payload is None:
        assert draft_path is not None
        try:
            resolved = draft_path.expanduser().resolve(strict=True)
            resolved.relative_to(snapshot.root)
        except ValueError:
            pass
        except OSError as exc:
            raise SnapshotError(f"cannot read answer draft: {exc}") from exc
        else:
            raise SnapshotError("answer draft must remain outside the immutable bundle")
        if not resolved.is_file():
            raise SnapshotError("answer draft must be a regular file")
        draft_payload = resolved.read_text(encoding="utf-8")
    draft = adaptive_runtime.strict_json_loads(
        draft_payload,
        label="source-generic answer draft",
    )
    if not isinstance(draft, dict):
        raise SnapshotError("source-generic answer draft root must be an object")
    _exact_keys(draft, {"summary", "claims"}, "source-generic answer draft")
    return draft


def _generic_answer_evidence(row: Mapping[str, Any]) -> dict[str, Any]:
    """Project an already validated passage into the public answer contract."""

    return {
        "source_id": row["source_id"],
        "record_id": row["record_id"],
        "concept_path": row["concept_path"],
        "source_path": row["source_path"],
        "record_sha256": row["record_sha256"],
        "locator": dict(row["locator"]),
        "text_sha256": row["text_sha256"],
    }


def _finalize_source_answer(
    snapshot: EnsembleSnapshot,
    draft_path: Path | None,
    question_id: str,
    query: str,
    minimum_summary_words: int,
    maximum_summary_words: int,
    *,
    top_k: int,
    per_facet: int,
    maximum_facets: int,
    draft_payload: str | None,
) -> dict[str, Any]:
    """Finalize claimless answers from gated evidence IDs and exact support quotes."""

    if not isinstance(question_id, str) or not question_id.strip():
        raise SnapshotError("question ID must be nonempty")
    if not isinstance(query, str) or not query.strip():
        raise SnapshotError("query must be nonempty")
    minimum = _plain_int(minimum_summary_words, "minimum summary words", 1, 5000)
    maximum = _plain_int(maximum_summary_words, "maximum summary words", 1, 5000)
    if minimum > maximum:
        raise SnapshotError("minimum summary words cannot exceed maximum summary words")
    maximum_evidence = _plain_int(top_k, "top-k", 1, 100)
    draft = _generic_answer_draft(snapshot, draft_path, draft_payload)
    summary = draft["summary"]
    if not isinstance(summary, str) or not summary.strip():
        raise SnapshotError("source-generic answer draft summary must be nonempty")
    word_count = len(summary.strip().split())
    if not minimum <= word_count <= maximum:
        raise SnapshotError(
            "source-generic answer draft summary must contain "
            f"{minimum} through {maximum} words; got {word_count}"
        )
    raw_claims = draft["claims"]
    if not isinstance(raw_claims, list) or not raw_claims:
        raise SnapshotError("source-generic answer draft claims must be a nonempty array")

    pack = build_evidence_pack(snapshot, query.strip(), maximum_evidence)
    brief = build_source_answer_brief(
        snapshot,
        query.strip(),
        maximum_evidence,
        per_facet,
        maximum_facets,
        evidence_pack=pack,
    )
    evidence_by_id = {
        row["evidence_id"]: row
        for row in pack["evidence_rows"]
        if isinstance(row, dict) and isinstance(row.get("evidence_id"), str)
    }
    if not evidence_by_id:
        raise SnapshotError("source-generic evidence pack returned no finalizable evidence")
    support_by_id = {
        support["support_id"]: support
        for facet in brief["facets"]
        for support in facet["supports"]
    }

    evidence: list[dict[str, Any]] = []
    evidence_indices: dict[str, int] = {}
    claims: list[dict[str, Any]] = []
    for claim_number, raw_claim in enumerate(raw_claims, start=1):
        if not isinstance(raw_claim, dict):
            raise SnapshotError(f"source-generic answer draft claim {claim_number} must be an object")
        _exact_keys(
            raw_claim,
            {"statement", "supporting_evidence"},
            f"source-generic answer draft claim {claim_number}",
        )
        statement = raw_claim["statement"]
        supports = raw_claim["supporting_evidence"]
        if not isinstance(statement, str) or not statement.strip():
            raise SnapshotError(
                f"source-generic answer draft claim {claim_number} statement must be nonempty"
            )
        if not isinstance(supports, list) or not supports:
            raise SnapshotError(
                f"source-generic answer draft claim {claim_number} supporting evidence "
                "must be a nonempty array"
            )
        claim_indices: list[int] = []
        seen_support_references: set[str] = set()
        for support_number, support in enumerate(supports, start=1):
            label = (
                f"source-generic answer draft claim {claim_number} "
                f"support {support_number}"
            )
            if not isinstance(support, dict):
                raise SnapshotError(f"{label} must be an object")
            support_keys = set(support)
            if support_keys == {"support_id"}:
                support_id = support["support_id"]
                if not isinstance(support_id, str) or not support_id:
                    raise SnapshotError(f"{label} support_id must be nonempty")
                governed_support = support_by_id.get(support_id)
                if governed_support is None:
                    raise SnapshotError(
                        f"{label} names support outside the gated answer brief: {support_id!r}"
                    )
                evidence_id = governed_support["evidence_id"]
                quote = governed_support["quote"]
                reference_key = support_id
            elif support_keys == {"evidence_id", "quote"}:
                evidence_id = support["evidence_id"]
                quote = support["quote"]
                reference_key = canonical_json(
                    {"evidence_id": evidence_id, "quote": quote}
                )
            else:
                raise SnapshotError(
                    f"{label} uses a closed schema; expected either ['support_id'] or "
                    "['evidence_id', 'quote']"
                )
            if not isinstance(evidence_id, str) or not evidence_id:
                raise SnapshotError(f"{label} evidence_id must be nonempty")
            if reference_key in seen_support_references:
                raise SnapshotError(f"{label} duplicates one support reference")
            seen_support_references.add(reference_key)
            selected = evidence_by_id.get(evidence_id)
            if selected is None:
                raise SnapshotError(
                    f"{label} names evidence outside the gated evidence pack: {evidence_id!r}"
                )
            if not isinstance(quote, str) or len(quote.strip()) < 16:
                raise SnapshotError(f"{label} quote must contain at least 16 characters")
            exact_quote = quote.strip()
            text = selected.get("text")
            if not isinstance(text, str) or exact_quote not in text:
                raise SnapshotError(f"{label} quote is not an exact substring of its evidence")
            if evidence_id not in evidence_indices:
                evidence_indices[evidence_id] = len(evidence)
                evidence.append(_generic_answer_evidence(selected))
            evidence_index = evidence_indices[evidence_id]
            if evidence_index not in claim_indices:
                claim_indices.append(evidence_index)
        claims.append(
            {
                "statement": statement.strip(),
                "evidence_indices": claim_indices,
            }
        )

    return {
        "question_id": question_id.strip(),
        "answer": {"summary": summary.strip(), "claims": claims},
        "evidence": evidence,
    }
