"""Bind the additive Enterprise title-only ingestion correction to existing evidence."""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
from urllib.parse import quote

REPO = Path(__file__).resolve().parents[2]


def write_json(path: Path, value: dict) -> None:
    """Write a portable audit without dependencies on the retired experiment."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False,
                               allow_nan=False) + "\n", encoding="utf-8", newline="\n")


def audit(prototype: Path, historical: Path, historical_manifest: Path, output: Path) -> dict:
    """Compare normalized record digests without changing historical native jobs."""
    source = prototype / "inputs/enterprise-all"
    ledger_path = prototype / "skills/unified/enterprise-all/references/knowledge/semantic/records.jsonl"
    ledger = [json.loads(line) for line in ledger_path.read_text(encoding="utf-8").splitlines()]
    source_rows = [json.loads(line) for path in (source / "documents").glob("*.jsonl") for line in path.read_text(encoding="utf-8").splitlines()]
    original = {row["id"]: row for row in source_rows}
    identities = {row["record_id"]: row["record_sha256"] for row in ledger}
    if len(identities) != len(original) or set(identities) != set(original):
        raise ValueError("Historical projection and original inventory differ")
    manifest = json.loads((source / "manifest.json").read_text(encoding="utf-8"))
    if any("body" in row.get("fields", {}) for row in manifest["sources"]):
        raise ValueError("Expected the preserved original unmapped manifest")
    if any(row.get("attributes", {}).get("body") for row in ledger):
        raise ValueError("Historical projection includes some body content")
    neutral = json.loads(historical_manifest.read_text(encoding="utf-8"))
    if {k: v for k, v in manifest.items() if k != "bundle"} != {k: v for k, v in neutral.items() if k != "bundle"}:
        raise ValueError("The historical manifest differs beyond neutral bundle metadata")
    # The e6 authoring adapter neutralized dataset-specific bundle metadata.
    # Recreate only the two identity fields affected by that known transformation.
    # Equality to all native record digests then binds the complete normalized
    # payload, including its title-only body and empty mapped attributes.
    fields = ("source_id", "source_kind", "source_path", "record_id", "subject_iri", "ontology_class_iri", "concept_type", "title", "body", "attributes")
    ontology = neutral["bundle"]["ontology_iri"].rstrip("#/") + "#"
    for row in ledger:
        payload = {key: row[key] for key in fields}
        payload["subject_iri"] = neutral["bundle"]["base_iri"] + "resource/" + quote(row["source_id"], safe="") + "/" + quote(row["record_id"], safe="")
        payload["ontology_class_iri"] = ontology + "EnterpriseDocument"
        identities[row["record_id"]] = hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()
    results = []
    for path in sorted((historical / "search").glob("*/development/generation-*/harbor-jobs/*/*/artifacts/response.json")):
        value = json.loads(path.read_text(encoding="utf-8"))
        records = value["record_identities"]
        match = {row["record_id"]: row["record_sha256"] for row in records.values()} == identities
        results.append({"family": value["family"], "response_sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "record_digests_match_title_projection": match})
    if not results or not all(row["record_digests_match_title_projection"] for row in results):
        raise ValueError("Historical record projections are not all identical; scope must be narrowed")
    result = {"schema_version": "enterprise-ingestion-scope-correction/1.0", "date": "2026-09-07",
        "records": len(ledger), "raw_body_characters": sum(len(row["body"]) for row in original.values()),
        "historical_rendered_body_characters": sum(len(row["body"]) for row in ledger),
        "historical_records_with_mapped_source_body": 0,
        "historical_ledger_sha256": hashlib.sha256(ledger_path.read_bytes()).hexdigest(),
        "original_manifest_sha256": hashlib.sha256((source / "manifest.json").read_bytes()).hexdigest(),
        "neutralized_historical_manifest_sha256": hashlib.sha256(historical_manifest.read_bytes()).hexdigest(),
        "identity_transform": "Only subject_iri and ontology_class_iri are rebased to the e6 manifest; all other normalized fields, including body and attributes, remain identical.",
        "verified_e6_trials": len(results), "trials_by_family": dict(sorted(Counter(row["family"] for row in results).items())),
        "all_record_digests_match": True, "historical_results_modified": False, "native_response_bindings": results,
        "interpretation": "The verified e6 records are identical to the title-only projection. Existing scores describe that projection and do not establish full-body retrieval or answer quality."}
    if output.exists():
        raise FileExistsError(output)
    write_json(output, result)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prototype", type=Path, default=REPO / "tmp/enterprise-source-skills-s1")
    parser.add_argument("--historical", type=Path, default=REPO / "tmp/e6")
    parser.add_argument("--historical-manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.prototype, args.historical, args.historical_manifest, args.output)
    print(json.dumps({key: value for key, value in result.items() if key != "native_response_bindings"}))
