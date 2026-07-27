#!/usr/bin/env python3
"""Resolve compact evidence references for the source-generic Harbor scorer."""

from __future__ import annotations

import hashlib
import json
import re
from collections import OrderedDict
from pathlib import Path
from typing import Any, Mapping


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


def _pairs(rows: list[tuple[str, Any]]) -> OrderedDict[str, Any]:
    result: OrderedDict[str, Any] = OrderedDict()
    for key, value in rows:
        if key in result:
            raise ValueError("duplicate-reference-dictionary-member")
        result[key] = value
    return result


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def _reference_id(evidence: Mapping[str, Any]) -> str:
    digest = hashlib.sha256(_canonical_json(evidence).encode("utf-8")).hexdigest()
    return f"ref-{digest[:24]}"


def _load_dictionary(path: Path) -> Mapping[str, Any]:
    value = json.loads(
        path.read_text(encoding="utf-8"),
        object_pairs_hook=_pairs,
        parse_constant=lambda raw: (_ for _ in ()).throw(
            ValueError(f"non-standard-reference-number:{raw}")
        ),
    )
    if not isinstance(value, Mapping) or set(value) != ROOT_KEYS:
        raise ValueError("reference-dictionary-root")
    if value.get("schema_version") != "1.0":
        raise ValueError("reference-dictionary-version")
    if value.get("algorithm") != "exact-evidence-reference-dictionary-v1":
        raise ValueError("reference-dictionary-algorithm")
    references = value.get("references")
    if not isinstance(references, Mapping):
        raise ValueError("reference-dictionary-references")
    if value.get("reference_count") != len(references):
        raise ValueError("reference-dictionary-count")
    if list(references) != sorted(references):
        raise ValueError("reference-dictionary-order")
    for reference_id, entry in references.items():
        if not isinstance(reference_id, str) or not REFERENCE_ID_RE.fullmatch(
            reference_id
        ):
            raise ValueError("reference-dictionary-id")
        if not isinstance(entry, Mapping) or set(entry) != ENTRY_KEYS:
            raise ValueError("reference-dictionary-entry")
        evidence = entry.get("evidence")
        if not isinstance(evidence, Mapping) or set(evidence) != set(EVIDENCE_KEYS):
            raise ValueError("reference-dictionary-evidence")
        if _reference_id(evidence) != reference_id:
            raise ValueError("reference-dictionary-stale-id")
    return references


def materialize_reference_evidence(
    output: Any, dictionary_path: Path
) -> tuple[Any, int]:
    """Expand an all-reference evidence array; preserve the legacy exact form."""

    if not isinstance(output, Mapping):
        return output, 0
    evidence = output.get("evidence")
    if not isinstance(evidence, list) or not evidence:
        return output, 0
    reference_form = [
        isinstance(row, Mapping) and set(row) == {"reference_id"}
        for row in evidence
    ]
    legacy_form = [
        isinstance(row, Mapping) and set(row) == set(EVIDENCE_KEYS)
        for row in evidence
    ]
    if all(legacy_form):
        return output, 0
    if not all(reference_form):
        raise ValueError("mixed-or-invalid-evidence-contract")
    references = _load_dictionary(dictionary_path)
    identifiers = [row["reference_id"] for row in evidence]
    if any(
        not isinstance(identifier, str) or identifier not in references
        for identifier in identifiers
    ):
        raise ValueError("unknown-reference-id")
    if len(set(identifiers)) != len(identifiers):
        raise ValueError("duplicate-reference-id")
    materialized = OrderedDict(output)
    materialized["evidence"] = [
        OrderedDict(
            (key, references[identifier]["evidence"][key])
            for key in EVIDENCE_KEYS
        )
        for identifier in identifiers
    ]
    return materialized, len(identifiers)
