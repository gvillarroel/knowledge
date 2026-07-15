"""Validate and consult a read-only, quality-gated Semantic OKF ensemble."""

from __future__ import annotations

import hashlib
import importlib
import importlib.metadata
import json
import math
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

import _adaptive_snapshot as adaptive_runtime
import _embedding_snapshot as embedding_runtime
import _entity_graph_snapshot as graph_runtime


SCHEMA_VERSION = "1.0"
ALGORITHM_ID = "protected-multisignal-paper-rerank-v2"
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
EXPECTED_FILES = {"index.json", "build-report.json"}
PLAN_KEYS = {
    "schema_version",
    "adaptive",
    "entity_graph",
    "embedding",
    "policies",
    "quality_gates",
}
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
    deep_validation: bool


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


def _validate_plan(value: Any) -> dict[str, Any]:
    """Independently validate the closed ensemble plan persisted in the snapshot."""

    if not isinstance(value, dict):
        raise SnapshotError("ensemble plan root must be an object")
    _exact_keys(value, PLAN_KEYS, "ensemble plan")
    if value["schema_version"] != SCHEMA_VERSION:
        raise SnapshotError(f"ensemble plan schema_version must be {SCHEMA_VERSION}")
    for child in ("adaptive", "entity_graph", "embedding"):
        if not isinstance(value[child], dict):
            raise SnapshotError(f"ensemble plan {child} must be an object")
    leaked = QUESTION_ID_RE.search(canonical_json(value))
    if leaked:
        raise SnapshotError(
            f"ensemble plans must not contain evaluation question IDs: {leaked.group(0)}"
        )
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
    _exact_keys(gates, QUALITY_GATE_KEYS, "ensemble quality_gates")
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
    except OSError as exc:
        raise SnapshotError(f"cannot read {label}: {exc}") from exc
    if not isinstance(value, dict):
        raise SnapshotError(f"{label} root must be an object")
    return value


def _artifact(root: Path, relative: str) -> dict[str, Any]:
    path = root / relative
    return {"path": relative, "bytes": path.stat().st_size, "sha256": sha256_file(path)}


def _component(root: Path, name: str, relative: str) -> dict[str, Any]:
    payload = _load_json(root / relative, relative)
    return {
        "name": name,
        "index": _artifact(root, relative),
        "schema_version": payload.get("schema_version"),
        "authoritative": payload.get("authoritative"),
        "core": payload.get("core"),
    }


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
        if actual != EXPECTED_FILES:
            raise SnapshotError(
                f"ensemble artifact set is closed; missing={sorted(EXPECTED_FILES - actual)}, "
                f"unknown={sorted(actual - EXPECTED_FILES)}"
            )
        if any(path.is_symlink() or not path.is_file() for path in ensemble.iterdir()):
            raise SnapshotError("ensemble artifacts must be regular files")
        index = _load_json(ensemble / "index.json", "ensemble/index.json")
        _exact_keys(
            index,
            {
                "schema_version",
                "authoritative",
                "discovery_only",
                "ensemble_plan_sha256",
                "plan",
                "core",
                "components",
                "algorithms",
                "summary",
            },
            "ensemble index",
        )
        if (
            index["schema_version"] != SCHEMA_VERSION
            or index["authoritative"] is not False
            or index["discovery_only"] is not True
        ):
            raise SnapshotError("ensemble index version or authority marker is invalid")
        plan = _validate_plan(index["plan"])
        if index["ensemble_plan_sha256"] != sha256_canonical(plan):
            raise SnapshotError("ensemble plan digest is invalid")
        if index["algorithms"] != {
            "direct_search": ALGORITHM_ID,
            "coverage": COVERAGE_ALGORITHM_ID,
            "answer_gate": ANSWER_GATE_ID,
        }:
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
        if index["summary"] != expected_summary:
            raise SnapshotError("ensemble summary is invalid")
        expected_report = {
            "schema_version": SCHEMA_VERSION,
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
        if _load_json(ensemble / "build-report.json", "ensemble/build-report.json") != expected_report:
            raise SnapshotError("ensemble build report differs from live validation")

        adaptive = adaptive_runtime.load_snapshot(root, deep_validation=deep_validation)
        graph = graph_runtime.load_snapshot(root, deep_validation=deep_validation)
        embedding = embedding_runtime.load_snapshot(root)
        live_cores = [adaptive.index["core"], graph.index["core"], embedding.index["core"]]
        if any(core != index["core"] for core in live_cores):
            raise SnapshotError("loaded components do not preserve authoritative core parity")
        _verify_claim_binding_parity(adaptive, graph)
        return EnsembleSnapshot(
            root=root,
            index=index,
            index_sha256=sha256_file(ensemble / "index.json"),
            adaptive=adaptive,
            graph=graph,
            embedding=embedding,
            deep_validation=deep_validation,
        )
    except (adaptive_runtime.SnapshotError, graph_runtime.SnapshotError, embedding_runtime.SnapshotError) as exc:
        raise SnapshotError(str(exc)) from exc


def inspect_snapshot(snapshot: EnsembleSnapshot) -> dict[str, Any]:
    """Describe validated capabilities, component bindings, and mandatory gates."""

    return {
        "schema_version": SCHEMA_VERSION,
        "status": "pass",
        "authoritative": False,
        "discovery_only": True,
        "read_only": True,
        "deep_validation": snapshot.deep_validation,
        "core": snapshot.index["core"],
        "ensemble_index_sha256": snapshot.index_sha256,
        "ensemble_plan_sha256": snapshot.index["ensemble_plan_sha256"],
        "components": snapshot.index["components"],
        "algorithms": snapshot.index["algorithms"],
        "policies": {
            "default": snapshot.index["plan"]["policies"]["default"],
            "available": ["quality", "fast", "robust"],
        },
        "quality_gates": snapshot.index["plan"]["quality_gates"],
        "capabilities": [
            "search",
            "evidence-pack",
            "coverage-pack",
            "coverage-brief",
            "finalize-answer",
        ],
    }


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

    result = adaptive_runtime.build_evidence_pack(snapshot.adaptive, query, top_k)
    result["ensemble"] = {
        "ensemble_index_sha256": snapshot.index_sha256,
        "core_tree_sha256": snapshot.index["core"]["tree_sha256"],
        "quality_gates": snapshot.index["plan"]["quality_gates"],
    }
    return result


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
