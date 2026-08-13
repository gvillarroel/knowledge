"""Closed registry for direct Semantic OKF expert generation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class FamilyProfile:
    """Describe one exact matched builder and consultation family."""

    family_id: str
    display_name: str
    build_skill: str
    consult_skill: str
    build_script: str
    validate_script: str
    query_script: str
    uses_plan: bool
    modes: tuple[str, ...]
    default_mode: str
    search_style: str
    target: str
    model_optional: bool = False

    def as_manifest(self) -> dict[str, Any]:
        """Return the public, path-independent family contract."""

        return {
            "id": self.family_id,
            "display_name": self.display_name,
            "build_skill": self.build_skill,
            "consult_skill": self.consult_skill,
            "build_script": self.build_script,
            "validate_script": self.validate_script,
            "query_script": self.query_script,
            "uses_plan": self.uses_plan,
            "modes": list(self.modes),
            "default_mode": self.default_mode,
            "search_style": self.search_style,
            "target": self.target,
            "model_optional": self.model_optional,
        }


PROFILES = {
    profile.family_id: profile
    for profile in (
        FamilyProfile(
            "legacy",
            "Legacy Semantic OKF",
            "build-semantic-okf",
            "consult-semantic-okf",
            "build_semantic_okf.py",
            "validate_semantic_okf.py",
            "query_semantic_okf.py",
            False,
            ("ledger",),
            "ledger",
            "legacy-ledger",
            "bundle",
        ),
        FamilyProfile(
            "embeddings",
            "Embedding Semantic OKF",
            "build-semantic-okf-embeddings",
            "consult-semantic-okf-embeddings",
            "build_semantic_okf_embeddings.py",
            "validate_semantic_okf_embeddings.py",
            "query_semantic_okf_embeddings.py",
            True,
            ("auto", "lexical", "vector", "hybrid"),
            "auto",
            "mode-option",
            "bundle",
            True,
        ),
        FamilyProfile(
            "classical",
            "Classical Semantic OKF",
            "build-semantic-okf-classical",
            "consult-semantic-okf-classical",
            "build_semantic_okf_classical.py",
            "validate_semantic_okf_classical.py",
            "query_semantic_okf_classical.py",
            True,
            ("bm25", "topic", "association", "fusion"),
            "fusion",
            "mode-option",
            "bundle",
        ),
        FamilyProfile(
            "adaptive",
            "Adaptive Semantic OKF",
            "build-semantic-okf-adaptive",
            "consult-semantic-okf-adaptive",
            "build_semantic_okf_adaptive.py",
            "validate_semantic_okf_adaptive.py",
            "query_semantic_okf_adaptive.py",
            True,
            ("bm25", "topic", "association", "fusion", "adaptive"),
            "adaptive",
            "mode-option",
            "bundle",
        ),
        FamilyProfile(
            "entity-graph",
            "Entity Graph Semantic OKF",
            "build-semantic-okf-entity-graph",
            "consult-semantic-okf-entity-graph",
            "build_semantic_okf_entity_graph.py",
            "validate_semantic_okf_entity_graph.py",
            "query_semantic_okf_entity_graph.py",
            True,
            ("lexical", "entity", "traversal", "fusion"),
            "fusion",
            "mode-option",
            "bundle",
        ),
        FamilyProfile(
            "ensemble",
            "Ensemble Semantic OKF",
            "build-semantic-okf-ensemble",
            "consult-semantic-okf-ensemble",
            "build_semantic_okf_ensemble.py",
            "validate_semantic_okf_ensemble.py",
            "query_semantic_okf_ensemble.py",
            True,
            ("default", "quality", "fast", "robust"),
            "default",
            "policy-option",
            "bundle",
            True,
        ),
        FamilyProfile(
            "graphify",
            "Graphify Semantic OKF",
            "build-semantic-okf-graphify",
            "consult-semantic-okf-graphify",
            "build_semantic_okf_graphify.py",
            "validate_semantic_okf_graphify.py",
            "query_semantic_okf_graphify.py",
            False,
            ("graphify",),
            "graphify",
            "graphify-positional",
            "bundle",
        ),
        FamilyProfile(
            "turso",
            "Turso Semantic OKF",
            "build-semantic-okf-turso",
            "consult-semantic-okf-turso",
            "build_semantic_okf.py",
            "validate_semantic_okf.py",
            "query_turso_knowledge.py",
            False,
            ("records",),
            "records",
            "turso-records",
            "semantic/knowledge.db",
        ),
    )
}


def profile(family_id: str) -> FamilyProfile:
    """Return one supported family or fail closed."""

    try:
        return PROFILES[family_id]
    except KeyError as exc:
        raise ValueError(
            f"Unsupported family {family_id!r}; choose one of {sorted(PROFILES)}"
        ) from exc


def vendor_root(skill_root: Path, family_id: str, role: str) -> Path:
    """Return one package-local vendor root."""

    if role not in {"builder", "consultant"}:
        raise ValueError(f"Unsupported vendor role: {role}")
    return skill_root / "assets" / "families" / family_id / role
