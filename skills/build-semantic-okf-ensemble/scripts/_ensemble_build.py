"""Build and independently validate a multi-signal Semantic OKF ensemble."""

from __future__ import annotations

import json
import math
import os
import re
import shutil
import tempfile
from pathlib import Path
from typing import Any, Mapping

from _adaptive_retrieval import (
    AdaptiveError,
    _is_link_or_junction,
    build_projection as build_adaptive_projection,
    canonical_json,
    load_plan as load_adaptive_plan,
    sha256_canonical,
    sha256_file,
    strict_json_loads,
    validate_adaptive_bundle,
)
from _embedding_retrieval import (
    RetrievalError,
    build_projection as build_embedding_projection,
    load_plan as load_embedding_plan,
    validate_retrieval_bundle,
)
from _entity_graph_build import (
    build_projection as build_graph_projection,
    validate_entity_graph_bundle,
)
from _entity_graph_model import EntityGraphError, load_plan as load_graph_plan


SCHEMA_VERSION = "1.0"
ALGORITHM_ID = "protected-multisignal-paper-rerank-v2"
COVERAGE_ALGORITHM_ID = "bounded-reviewed-claim-multisignal-expansion-v2"
ANSWER_GATE_ID = "facet-status-exact-binding-finalizer-v1"
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
DERIVED_ROOTS = frozenset({"adaptive", "entity-graph", "retrieval", "ensemble"})
QUESTION_ID_RE = re.compile(r"(?<![a-z0-9])q\d{3}(?:[-_][a-z0-9-]+)?(?![a-z0-9])", re.IGNORECASE)


class EnsembleError(RuntimeError):
    """Describe an invalid plan, component, projection, or atomic build."""


def _exact_keys(value: Mapping[str, Any], expected: set[str], label: str) -> None:
    actual = set(value)
    if actual != expected:
        raise EnsembleError(
            f"{label} uses a closed schema; missing={sorted(expected - actual)}, "
            f"unknown={sorted(actual - expected)}"
        )


def _plain_int(value: Any, label: str, minimum: int, maximum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not minimum <= value <= maximum:
        raise EnsembleError(f"{label} must be an integer from {minimum} through {maximum}")
    return value


def _finite(value: Any, label: str, minimum: float, maximum: float) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise EnsembleError(f"{label} must be numeric")
    number = float(value)
    if not math.isfinite(number) or not minimum <= number <= maximum:
        raise EnsembleError(f"{label} must be finite from {minimum} through {maximum}")
    return number


def _string_list(value: Any, label: str, *, allowed: frozenset[str]) -> list[str]:
    if not isinstance(value, list) or not value or any(not isinstance(item, str) for item in value):
        raise EnsembleError(f"{label} must be a nonempty string array")
    if len(set(value)) != len(value):
        raise EnsembleError(f"{label} must not contain duplicates")
    unknown = sorted(set(value) - allowed)
    if unknown:
        raise EnsembleError(f"{label} contains unknown values: {unknown}")
    return list(value)


def _strict_json(payload: str, *, label: str) -> Any:
    """Parse strict JSON while translating component errors to this package contract."""

    try:
        return strict_json_loads(payload, label=label)
    except AdaptiveError as exc:
        raise EnsembleError(str(exc)) from exc


def _validated_component_plans(
    value: Mapping[str, Any],
) -> tuple[Any, Any, Any]:
    """Validate all nested component plans before building the authoritative core."""

    loaders = {
        "adaptive": load_adaptive_plan,
        "entity_graph": load_graph_plan,
        "embedding": load_embedding_plan,
    }
    parsed: dict[str, Any] = {}
    with tempfile.TemporaryDirectory(prefix="semantic-okf-ensemble-plan-validation-") as temp:
        root = Path(temp)
        for name, loader in loaders.items():
            path = root / f"{name}.json"
            path.write_text(canonical_json(value[name]) + "\n", encoding="utf-8", newline="\n")
            try:
                parsed[name] = loader(path)
            except (AdaptiveError, EntityGraphError, RetrievalError) as exc:
                raise EnsembleError(f"ensemble component plan {name} is invalid: {exc}") from exc
    return parsed["adaptive"], parsed["entity_graph"], parsed["embedding"]


def validate_plan(value: Any) -> dict[str, Any]:
    """Validate and return one closed, leakage-resistant ensemble plan."""

    if not isinstance(value, dict):
        raise EnsembleError("ensemble plan root must be an object")
    _exact_keys(value, PLAN_KEYS, "ensemble plan")
    if value["schema_version"] != SCHEMA_VERSION:
        raise EnsembleError(f"ensemble plan schema_version must be {SCHEMA_VERSION}")
    for child in ("adaptive", "entity_graph", "embedding"):
        if not isinstance(value[child], dict):
            raise EnsembleError(f"ensemble plan {child} must be an object")
    encoded = canonical_json(value)
    leaked = QUESTION_ID_RE.search(encoded)
    if leaked:
        raise EnsembleError(f"ensemble plans must not contain evaluation question IDs: {leaked.group(0)}")

    adaptive_plan, graph_plan, embedding_plan = _validated_component_plans(value)
    graph_retrieval_sources = tuple(sorted((*graph_plan.paper_source_ids, *graph_plan.claim_source_ids)))
    if adaptive_plan.source_ids != embedding_plan.source_ids:
        raise EnsembleError("adaptive and embedding components must select the same source IDs")
    if adaptive_plan.source_ids != graph_retrieval_sources:
        raise EnsembleError(
            "adaptive and embedding selections must equal the graph paper and claim selections"
        )
    paper_identity_sources = set(value["adaptive"]["evidence_identity"]["paper_ids_by_source"])
    if paper_identity_sources != set(adaptive_plan.source_ids):
        raise EnsembleError(
            "adaptive paper identity mappings must cover every selected paper and claim source"
        )
    page_sources = set(value["adaptive"]["passages"]["markdown_pdf_page_source_ids"])
    if page_sources != set(graph_plan.paper_source_ids):
        raise EnsembleError(
            "adaptive PDF-page passage sources must equal the graph paper-source selection"
        )

    policies = value["policies"]
    if not isinstance(policies, dict):
        raise EnsembleError("ensemble plan policies must be an object")
    _exact_keys(policies, POLICIES_KEYS, "ensemble plan policies")
    if policies["default"] not in {"quality", "fast", "robust"}:
        raise EnsembleError("ensemble default policy must be quality, fast, or robust")
    for name in ("quality", "fast", "robust"):
        policy = policies[name]
        if not isinstance(policy, dict):
            raise EnsembleError(f"ensemble policy {name} must be an object")
        _exact_keys(policy, POLICY_KEYS, f"ensemble policy {name}")
        routes = _string_list(policy["routes"], f"ensemble policy {name}.routes", allowed=ALLOWED_ROUTES)
        weights = policy["weights"]
        if not isinstance(weights, list) or len(weights) != len(routes):
            raise EnsembleError(f"ensemble policy {name}.weights must align with routes")
        for number, weight in enumerate(weights, start=1):
            _finite(weight, f"ensemble policy {name}.weights[{number}]", 0.01, 100.0)
        _plain_int(policy["rrf_k"], f"ensemble policy {name}.rrf_k", 0, 10_000)
        if policy["protected_route"] != "adaptive":
            raise EnsembleError(f"ensemble policy {name} must protect the adaptive candidate set")
        if "adaptive" not in routes:
            raise EnsembleError(f"ensemble policy {name} must include the adaptive route")
        promotion = policy["promotion"]
        if not isinstance(promotion, dict):
            raise EnsembleError(f"ensemble policy {name}.promotion must be an object")
        _exact_keys(promotion, PROMOTION_KEYS, f"ensemble policy {name}.promotion")
        if promotion["route"] not in ALLOWED_ROUTES:
            raise EnsembleError(f"ensemble policy {name}.promotion.route is unknown")
        _string_list(
            promotion["confirmation_routes"],
            f"ensemble policy {name}.promotion.confirmation_routes",
            allowed=ALLOWED_ROUTES,
        )
        _plain_int(promotion["confirmation_depth"], "promotion confirmation_depth", 1, 100)
        _plain_int(
            promotion["minimum_confirmations"],
            "promotion minimum_confirmations",
            1,
            len(promotion["confirmation_routes"]),
        )
        _plain_int(promotion["maximum_protected_rank"], "promotion maximum_protected_rank", 1, 1000)

    gates = value["quality_gates"]
    if not isinstance(gates, dict):
        raise EnsembleError("ensemble quality_gates must be an object")
    _exact_keys(gates, QUALITY_GATE_KEYS, "ensemble quality_gates")
    if gates["required_components"] != REQUIRED_COMPONENTS:
        raise EnsembleError(f"required_components must be exactly {REQUIRED_COMPONENTS}")
    for key in (
        "protect_candidate_set",
        "require_core_parity",
        "reviewed_graph_claims_only",
        "reviewed_embedding_claims_only",
        "require_facet_status",
        "require_exact_answer_bindings",
    ):
        if gates[key] is not True:
            raise EnsembleError(f"quality gate {key} must be true")
    if _finite(gates["candidate_edge_weight"], "candidate_edge_weight", 0.0, 1.0) != 0.0:
        raise EnsembleError("candidate_edge_weight must be zero for answer-evidence expansion")
    _plain_int(gates["maximum_graph_claims_per_facet"], "maximum_graph_claims_per_facet", 1, 32)
    _plain_int(gates["maximum_graph_claims_total"], "maximum_graph_claims_total", 1, 500)
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


def load_plan(path: Path) -> dict[str, Any]:
    """Load one ensemble plan with duplicate-key and non-finite rejection."""

    try:
        value = _strict_json(path.read_text(encoding="utf-8"), label="ensemble plan")
    except (OSError, UnicodeError) as exc:
        raise EnsembleError(f"cannot read ensemble plan at {path}: {exc}") from exc
    return validate_plan(value)


def _write_json(path: Path, value: Any) -> None:
    path.write_text(canonical_json(value) + "\n", encoding="utf-8", newline="\n")


def _artifact(root: Path, relative: str) -> dict[str, Any]:
    path = root / relative
    return {"path": relative, "bytes": path.stat().st_size, "sha256": sha256_file(path)}


def _component(root: Path, name: str, relative: str) -> dict[str, Any]:
    payload = _strict_json((root / relative).read_text(encoding="utf-8"), label=relative)
    if not isinstance(payload, dict):
        raise EnsembleError(f"{relative} must contain an object")
    if payload.get("authoritative") is not False or not isinstance(payload.get("core"), dict):
        raise EnsembleError(f"{relative} has an invalid authority or core binding")
    return {
        "name": name,
        "index": _artifact(root, relative),
        "schema_version": payload.get("schema_version"),
        "authoritative": payload.get("authoritative"),
        "core": payload.get("core"),
    }


def _component_results(root: Path) -> dict[str, dict[str, Any]]:
    results = {
        "adaptive": validate_adaptive_bundle(root),
        "entity_graph": validate_entity_graph_bundle(root),
        "embedding": validate_retrieval_bundle(root),
    }
    failed = [
        name
        for name, result in results.items()
        if result.get("status") != "pass" or result.get("valid") is not True
    ]
    if failed:
        details = []
        for name in failed:
            details.extend(str(item.get("message", item)) for item in results[name].get("errors", [])[:2])
        raise EnsembleError(f"ensemble component validation failed for {failed}: {'; '.join(details)}")
    return results


def build_projection(root: Path, plan_path: Path) -> dict[str, Any]:
    """Build all derived components and the closed ensemble binding in one candidate."""

    plan = load_plan(plan_path)
    for name in DERIVED_ROOTS:
        path = root / name
        if path.exists() or path.is_symlink():
            raise EnsembleError(f"core candidate unexpectedly contains derived artifacts: {name}")
    with tempfile.TemporaryDirectory(prefix="semantic-okf-ensemble-plans-") as temp:
        temp_root = Path(temp)
        child_paths: dict[str, Path] = {}
        for name in ("adaptive", "entity_graph", "embedding"):
            child = temp_root / f"{name}.json"
            _write_json(child, plan[name])
            child_paths[name] = child
        build_adaptive_projection(root, child_paths["adaptive"])
        build_graph_projection(root, child_paths["entity_graph"])
        build_embedding_projection(root, child_paths["embedding"])

    _component_results(root)
    ensemble = root / "ensemble"
    if ensemble.exists() or ensemble.is_symlink():
        raise EnsembleError("core candidate unexpectedly contains ensemble artifacts")
    ensemble.mkdir()
    components = {
        "adaptive": _component(root, "adaptive", "adaptive/index.json"),
        "entity_graph": _component(root, "entity_graph", "entity-graph/index.json"),
        "embedding": _component(root, "embedding", "retrieval/index.json"),
    }
    cores = [component["core"] for component in components.values()]
    if any(core != cores[0] for core in cores[1:]):
        raise EnsembleError("derived components do not bind to the same authoritative core")
    index = {
        "schema_version": SCHEMA_VERSION,
        "authoritative": False,
        "discovery_only": True,
        "ensemble_plan_sha256": sha256_canonical(plan),
        "plan": plan,
        "core": cores[0],
        "components": components,
        "algorithms": {
            "direct_search": ALGORITHM_ID,
            "coverage": COVERAGE_ALGORITHM_ID,
            "answer_gate": ANSWER_GATE_ID,
        },
        "summary": {
            "policies": 3,
            "required_components": len(REQUIRED_COMPONENTS),
            "default_policy": plan["policies"]["default"],
        },
    }
    _write_json(ensemble / "index.json", index)
    initial = validate_ensemble_bundle(root, require_build_report=False)
    if initial.get("status") != "pass":
        raise EnsembleError("ensemble index failed independent validation")
    report = {
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
            name: component["index"] for name, component in components.items()
        },
        "artifacts": {"index": _artifact(root, "ensemble/index.json")},
        "summary": index["summary"],
    }
    _write_json(ensemble / "build-report.json", report)
    final = validate_ensemble_bundle(root)
    if final.get("status") != "pass":
        raise EnsembleError("completed ensemble failed independent validation")
    return report


def _validate_or_raise(root: Path, *, require_build_report: bool) -> dict[str, Any]:
    root = root.expanduser().resolve(strict=True)
    ensemble = root / "ensemble"
    if not ensemble.is_dir() or ensemble.is_symlink():
        raise EnsembleError("ensemble must be a real directory")
    expected = {"index.json"}
    if require_build_report:
        expected.add("build-report.json")
    actual = {path.name for path in ensemble.iterdir()}
    if actual != expected:
        raise EnsembleError(
            f"ensemble artifact set is closed; missing={sorted(expected - actual)}, "
            f"unknown={sorted(actual - expected)}"
        )
    if any(path.is_symlink() or not path.is_file() for path in ensemble.iterdir()):
        raise EnsembleError("ensemble artifacts must be regular files")
    _component_results(root)
    index = _strict_json(
        (ensemble / "index.json").read_text(encoding="utf-8"),
        label="ensemble/index.json",
    )
    if not isinstance(index, dict):
        raise EnsembleError("ensemble/index.json root must be an object")
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
        raise EnsembleError("ensemble index version or authority marker is invalid")
    plan = validate_plan(index["plan"])
    if index["ensemble_plan_sha256"] != sha256_canonical(plan):
        raise EnsembleError("ensemble plan digest is invalid")
    if index["algorithms"] != {
        "direct_search": ALGORITHM_ID,
        "coverage": COVERAGE_ALGORITHM_ID,
        "answer_gate": ANSWER_GATE_ID,
    }:
        raise EnsembleError("ensemble algorithm identities are invalid")
    expected_components = {
        "adaptive": _component(root, "adaptive", "adaptive/index.json"),
        "entity_graph": _component(root, "entity_graph", "entity-graph/index.json"),
        "embedding": _component(root, "embedding", "retrieval/index.json"),
    }
    if index["components"] != expected_components:
        raise EnsembleError("ensemble component bindings are stale")
    cores = [component["core"] for component in expected_components.values()]
    if any(core != cores[0] for core in cores[1:]) or index["core"] != cores[0]:
        raise EnsembleError("ensemble authoritative core parity gate failed")
    expected_summary = {
        "policies": 3,
        "required_components": len(REQUIRED_COMPONENTS),
        "default_policy": plan["policies"]["default"],
    }
    if index["summary"] != expected_summary:
        raise EnsembleError("ensemble summary is invalid")
    report = {
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
    if require_build_report:
        observed = _strict_json(
            (ensemble / "build-report.json").read_text(encoding="utf-8"),
            label="ensemble/build-report.json",
        )
        if observed != report:
            raise EnsembleError("ensemble build report differs from live validation")
    return report


def validate_ensemble_bundle(root: Path, *, require_build_report: bool = True) -> dict[str, Any]:
    """Return a stable validation report for the complete ensemble bundle."""

    try:
        return _validate_or_raise(root, require_build_report=require_build_report)
    except (
        EnsembleError,
        AdaptiveError,
        EntityGraphError,
        RetrievalError,
        OSError,
        UnicodeError,
        json.JSONDecodeError,
        KeyError,
        IndexError,
        TypeError,
        ValueError,
        OverflowError,
    ) as exc:
        return {
            "schema_version": SCHEMA_VERSION,
            "status": "error",
            "valid": False,
            "errors": [{"code": "ensemble-error", "path": "ensemble", "message": str(exc)}],
            "warnings": [],
            "summary": {},
        }


def atomic_build(manifest_path: Path, plan_path: Path, output: Path, core_builder: Any) -> dict[str, Any]:
    """Build every layer in one private sibling and publish it once."""

    output = output.expanduser().absolute()
    for component in (output, *output.parents):
        if _is_link_or_junction(component):
            raise EnsembleError(f"output path contains a symlink or junction: {component}")
    if output.exists():
        raise EnsembleError(f"output already exists: {output}")
    load_plan(plan_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    for component in (output.parent, *output.parent.parents):
        if _is_link_or_junction(component):
            raise EnsembleError(f"output path contains a symlink or junction: {component}")
    container = Path(tempfile.mkdtemp(prefix=f".{output.name}.ensemble-candidate-", dir=output.parent))
    candidate = container / "payload"
    try:
        core_builder(manifest_path, candidate)
        report = build_projection(candidate, plan_path)
        os.replace(candidate, output)
    except Exception as exc:
        try:
            if candidate.is_symlink():
                candidate.unlink()
            elif candidate.is_dir():
                shutil.rmtree(candidate)
            elif candidate.exists():
                candidate.unlink()
            container.rmdir()
        except OSError as cleanup_exc:
            raise EnsembleError(
                f"atomic build failed and private candidate cleanup failed: {cleanup_exc}"
            ) from exc
        raise
    container.rmdir()
    return report
