"""Audit declared source selection without claiming raw-source text fidelity."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any

from _direct_skill import DirectSkillError, load_json, load_records, sha256_file


def source_declarations(manifest_path: Path) -> tuple[list[dict[str, Any]], str]:
    """Require a deliberate structured selection before calling a family builder."""
    digest = sha256_file(manifest_path)
    manifest = load_json(manifest_path, label="source manifest")
    sources = manifest.get("sources")
    if not isinstance(sources, list) or not sources or any(not isinstance(s, dict) for s in sources):
        raise DirectSkillError("Source manifest requires a non-empty array of source objects")
    for source in sources:
        if source.get("kind") not in {"json", "csv"}:
            continue
        schema = source.get("schema")
        if not isinstance(schema, dict):
            raise DirectSkillError(f"Source {source.get('id')!r} requires an explicit schema object")
        identity = {value for key in ("id_field", "title_field")
                    if isinstance(value := source.get(key), str)}
        if "fields" not in source and set(schema) - identity:
            raise DirectSkillError(
                f"Source {source.get('id')!r} declares fields beyond identity/title. "
                "Add an explicit fields object mapping the content to retain; "
                "use fields: {} only for intentional title-only knowledge. "
                "A schema declaration alone does not retain content."
            )
        if "fields" in source and not isinstance(source["fields"], dict):
            raise DirectSkillError(f"Source {source.get('id')!r} fields must be an object")
    return sources, digest


def source_coverage(
    sources: list[dict[str, Any]], manifest_sha256: str, knowledge: Path,
) -> dict[str, Any]:
    """Summarize the validated ledger against raw declaration intent.

    Values and character counts describe normalized records. The canonical
    adapter owns parsing, typing and rendering; this audit does not reimplement it.
    """
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in load_records(knowledge):
        grouped[record["source_id"]].append(record)
    declared = {source["id"]: source for source in sources}
    rows = []
    for source_id in sorted(set(declared) | set(grouped)):
        source = declared.get(source_id)
        records = grouped[source_id]
        mapped = sorted(source.get("fields", {})) if source else []
        schema = sorted(source.get("schema", {})) if source else []
        identity = sorted({value for key in ("id_field", "title_field")
                           if source and isinstance(value := source.get(key), str)})
        kind = source["kind"] if source else "derived"
        structured = kind in {"json", "csv"}
        non_null = null = characters = 0
        for record in records:
            attributes, body = record.get("attributes"), record.get("body")
            if not isinstance(attributes, dict) or not isinstance(body, str):
                raise DirectSkillError(f"Source {source_id!r} has an invalid normalized record")
            if structured and not set(mapped).issubset(attributes):
                raise DirectSkillError(f"Source {source_id!r} lost declared fields in normalized attributes")
            values = [attributes[key] for key in mapped if key in attributes]
            non_null += sum(value is not None for value in values)
            null += sum(value is None for value in values)
            characters += len(body)
        scope = ("derived" if source is None else "native" if not structured
                 else "mapped-fields" if mapped else "title-only")
        rows.append({
            "source_id": source_id, "kind": kind, "declared_fields": schema,
            "identity_fields": identity, "mapped_fields": mapped,
            "omitted_fields": sorted(set(schema) - set(mapped) - set(identity)),
            "mapping_explicit": source is not None and "fields" in source,
            "scope": scope, "record_count": len(records),
            "mapped_value_count": non_null, "null_mapped_value_count": null,
            "text_characters": characters,
        })
    return {
        "schema_version": "semantic-okf-source-coverage/1.0",
        "source_manifest_sha256": manifest_sha256,
        "scope": "declared-structured-fields-and-normalized-records",
        "raw_source_fidelity_verified": False,
        "sources": rows,
    }
