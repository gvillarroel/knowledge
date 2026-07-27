#!/usr/bin/env python3
"""Derive and validate compact exact-evidence reference dictionaries."""

from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Mapping, Sequence


SCHEMA_VERSION = "1.0"
ALGORITHM = "exact-evidence-reference-dictionary-v1"
REFERENCE_ID_RE = re.compile(r"ref-[0-9a-f]{24}")
EVIDENCE_KEYS = (
    "source_id",
    "record_id",
    "concept_path",
    "source_path",
    "record_sha256",
    "locator",
    "text_sha256",
)
ROOT_KEYS = {"schema_version", "algorithm", "reference_count", "references"}
ENTRY_KEYS = {"document_id", "evidence"}


class ReferenceDictionaryError(RuntimeError):
    """Describe an invalid or inconsistent reference dictionary."""


def canonical_json(value: Any) -> str:
    """Serialize JSON deterministically and reject non-finite values."""

    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def _reference_id(evidence: Mapping[str, Any]) -> str:
    digest = hashlib.sha256(canonical_json(evidence).encode("utf-8")).hexdigest()
    return f"ref-{digest[:24]}"


def derive_reference_dictionary(
    documents: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Map stable compact IDs to exact evidence identities for every document."""

    references: dict[str, dict[str, Any]] = {}
    document_ids: set[str] = set()
    for number, document in enumerate(documents, start=1):
        document_id = document.get("document_id")
        if not isinstance(document_id, str) or not document_id:
            raise ReferenceDictionaryError(
                f"document {number} has no valid document_id"
            )
        if document_id in document_ids:
            raise ReferenceDictionaryError(f"duplicate document_id: {document_id}")
        document_ids.add(document_id)
        evidence = {key: document.get(key) for key in EVIDENCE_KEYS}
        if any(value is None for value in evidence.values()):
            raise ReferenceDictionaryError(
                f"document {document_id} lacks an exact evidence field"
            )
        reference_id = _reference_id(evidence)
        entry = {"document_id": document_id, "evidence": evidence}
        existing = references.get(reference_id)
        if existing is not None and existing != entry:
            raise ReferenceDictionaryError(
                f"reference ID collision for {reference_id}"
            )
        if existing is not None:
            raise ReferenceDictionaryError(
                f"duplicate exact evidence identity for {reference_id}"
            )
        references[reference_id] = entry
    ordered = {key: references[key] for key in sorted(references)}
    return {
        "schema_version": SCHEMA_VERSION,
        "algorithm": ALGORITHM,
        "reference_count": len(ordered),
        "references": ordered,
    }


def validate_reference_dictionary(
    value: Any, documents: Sequence[Mapping[str, Any]]
) -> dict[str, dict[str, Any]]:
    """Require exact closed-schema equality with deterministic derivation."""

    if not isinstance(value, dict) or set(value) != ROOT_KEYS:
        raise ReferenceDictionaryError("reference dictionary root schema is invalid")
    if value.get("schema_version") != SCHEMA_VERSION:
        raise ReferenceDictionaryError("reference dictionary schema version is invalid")
    if value.get("algorithm") != ALGORITHM:
        raise ReferenceDictionaryError("reference dictionary algorithm is invalid")
    references = value.get("references")
    if not isinstance(references, dict):
        raise ReferenceDictionaryError("references must be a JSON object")
    if value.get("reference_count") != len(references):
        raise ReferenceDictionaryError("reference dictionary count is invalid")
    if list(references) != sorted(references):
        raise ReferenceDictionaryError("reference IDs must be sorted")
    for reference_id, entry in references.items():
        if not isinstance(reference_id, str) or not REFERENCE_ID_RE.fullmatch(
            reference_id
        ):
            raise ReferenceDictionaryError(f"invalid reference ID: {reference_id!r}")
        if not isinstance(entry, dict) or set(entry) != ENTRY_KEYS:
            raise ReferenceDictionaryError(
                f"reference entry {reference_id} has an invalid schema"
            )
        evidence = entry.get("evidence")
        if not isinstance(evidence, dict) or set(evidence) != set(EVIDENCE_KEYS):
            raise ReferenceDictionaryError(
                f"reference entry {reference_id} has invalid evidence fields"
            )
        if _reference_id(evidence) != reference_id:
            raise ReferenceDictionaryError(
                f"reference entry {reference_id} has a stale ID"
            )
    expected = derive_reference_dictionary(documents)
    if value != expected:
        raise ReferenceDictionaryError(
            "reference dictionary differs from deterministic document derivation"
        )
    by_document = {
        entry["document_id"]: {"reference_id": reference_id, **entry}
        for reference_id, entry in references.items()
    }
    if len(by_document) != len(references):
        raise ReferenceDictionaryError(
            "reference dictionary contains duplicate document bindings"
        )
    return by_document
