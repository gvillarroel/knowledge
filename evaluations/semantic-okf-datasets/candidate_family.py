#!/usr/bin/env python3
"""Validate a hash-bound candidate family without activating it in families.json."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any, Mapping

import dataset_tool as data


SCHEMA_VERSION = "semantic-okf-evaluation-candidate-family/1.0"
FAMILY_ID = re.compile(r"\A[a-z0-9]+(?:-[a-z0-9]+)*\Z")
FAMILY_FIELDS = {
    "build_script",
    "build_skill",
    "consult_skill",
    "requires_hf_cache",
    "uses_plan",
    "validate_script",
}
ALLOWED_MODES = {"build-consult", "consult-only"}
REPO = Path(__file__).resolve().parents[2]


class CandidateFamilyError(ValueError):
    """Raised when a candidate-family binding is absent, stale, or unsafe."""


def _sha256_json(value: Any) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _relative_regular_file(path: Path, label: str) -> Path:
    resolved = path.resolve()
    try:
        relative = resolved.relative_to(REPO)
    except ValueError as exc:
        raise CandidateFamilyError(f"{label} must be inside the repository") from exc
    if not resolved.is_file() or resolved.is_symlink():
        raise CandidateFamilyError(f"{label} is absent or not a regular file: {path}")
    if any(parent.is_symlink() for parent in resolved.parents if parent != REPO.parent):
        raise CandidateFamilyError(f"{label} cannot traverse a symlink: {path}")
    if not relative.parts:
        raise CandidateFamilyError(f"{label} cannot be the repository root")
    return resolved


def load(
    path: Path,
    *,
    family_id: str,
    mode: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Load one inactive candidate and return its family plus immutable binding."""

    candidate_path = _relative_regular_file(path, "candidate family specification")
    value = data.load_json(candidate_path)
    if set(value) != {
        "schema_version",
        "candidate_id",
        "allowed_modes",
        "family",
    }:
        raise CandidateFamilyError("candidate family specification has invalid fields")
    if value.get("schema_version") != SCHEMA_VERSION:
        raise CandidateFamilyError("unsupported candidate family schema")
    candidate_id = value.get("candidate_id")
    if (
        not isinstance(candidate_id, str)
        or FAMILY_ID.fullmatch(candidate_id) is None
        or candidate_id != family_id
    ):
        raise CandidateFamilyError("candidate family identity mismatch")
    if candidate_id in data.load_families():
        raise CandidateFamilyError(
            f"{candidate_id} is already active; omit --candidate-family-spec"
        )
    modes = value.get("allowed_modes")
    if (
        not isinstance(modes, list)
        or not modes
        or len(modes) != len(set(modes))
        or any(item not in ALLOWED_MODES for item in modes)
        or mode not in modes
    ):
        raise CandidateFamilyError(
            f"candidate family does not permit execution mode {mode!r}"
        )
    family = value.get("family")
    if not isinstance(family, dict) or set(family) != FAMILY_FIELDS:
        raise CandidateFamilyError("candidate family contract has invalid fields")
    for name in ("build_script", "build_skill", "consult_skill", "validate_script"):
        item = family.get(name)
        if not isinstance(item, str) or not item or "/" in item or "\\" in item:
            raise CandidateFamilyError(f"candidate family field is invalid: {name}")
    for name in ("requires_hf_cache", "uses_plan"):
        if not isinstance(family.get(name), bool):
            raise CandidateFamilyError(f"candidate family field is invalid: {name}")

    build_skill = REPO / "skills" / family["build_skill"]
    consult_skill = REPO / "skills" / family["consult_skill"]
    for skill, label in (
        (build_skill, "candidate build skill"),
        (consult_skill, "candidate consult skill"),
    ):
        if not skill.is_dir() or skill.is_symlink() or not (skill / "SKILL.md").is_file():
            raise CandidateFamilyError(f"{label} is absent or invalid: {skill}")
    for name in ("build_script", "validate_script"):
        script = build_skill / "scripts" / family[name]
        if not script.is_file() or script.is_symlink():
            raise CandidateFamilyError(f"candidate {name} is absent: {script}")
    binding = {
        "schema_version": SCHEMA_VERSION,
        "candidate_id": candidate_id,
        "allowed_modes": modes,
        "specification_path": candidate_path.relative_to(REPO).as_posix(),
        "specification_sha256": data.sha256_file(candidate_path),
        "family_contract_sha256": _sha256_json(family),
    }
    return dict(family), binding


def resolve(
    dataset_id: str,
    family_id: str,
    mode: str,
    candidate_spec: Path | None,
) -> tuple[dict[str, Any], dict[str, Any] | None]:
    """Resolve either an active family or an explicitly bound inactive candidate."""

    if candidate_spec is None:
        data.validate_dataset(dataset_id, family_id)
        families = data.load_families()
        if family_id not in families:
            raise CandidateFamilyError(f"unknown active family: {family_id}")
        return dict(families[family_id]), None
    data.validate_dataset(dataset_id)
    return load(candidate_spec, family_id=family_id, mode=mode)


def verify_manifest(
    manifest: Mapping[str, Any],
    binding: Mapping[str, Any] | None,
) -> None:
    """Require generated tasks to carry the exact candidate-family binding."""

    actual = manifest.get("candidate_family")
    if binding is None:
        if actual is not None:
            raise CandidateFamilyError(
                "active-family execution cannot use candidate-bound tasks"
            )
        return
    if actual != dict(binding):
        raise CandidateFamilyError("generated task candidate-family binding drift")
