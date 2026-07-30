#!/usr/bin/env python3
"""Validate the tracked knowledge-methodology dataset and its bindings."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
from typing import Any, Sequence

import yaml


ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = ROOT.parents[1]
SELECTION_PATH = ROOT / "paper-selection.json"
INVENTORY_PATH = ROOT / "sources" / "inventory.json"
MANIFEST_PATH = ROOT / "manifest.json"
SOURCE_COMBINATION_PATH = ROOT / "source-combination.json"
BUNDLE_PATH = ROOT / "bundle"
AUDIT_PATH = (
    ROOT
    / "reports"
    / "repository-methodology-audit-20260729.json"
)
EXPERT_KNOWLEDGE_PATH = (
    REPOSITORY_ROOT
    / "skills"
    / "review-knowledge-methodology"
    / "references"
    / "knowledge"
)
ARXIV_ID_RE = re.compile(r"^[0-9]{4}\.[0-9]{4,5}v[0-9]+$")


class DatasetValidationError(ValueError):
    """Raised when a dataset binding or semantic contract is invalid."""


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _frontmatter(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise DatasetValidationError(f"Missing frontmatter: {path}")
    try:
        raw = text.split("---\n", 2)[1]
        value = yaml.safe_load(raw)
    except (IndexError, yaml.YAMLError) as exc:
        raise DatasetValidationError(f"Invalid frontmatter: {path}") from exc
    if not isinstance(value, dict):
        raise DatasetValidationError(f"Frontmatter is not a mapping: {path}")
    return value


def _validate_selection(selection: dict[str, Any]) -> set[str]:
    papers = selection.get("papers")
    reused = selection.get("reused_corpora")
    if (
        selection.get("schema_version")
        != "knowledge-methodology-paper-selection/1.0"
        or selection.get("dataset_id") != "knowledge-methodology-papers-47"
        or not isinstance(papers, list)
        or len(papers) != 32
        or not isinstance(reused, list)
        or len(reused) != 1
    ):
        raise DatasetValidationError("Selection envelope is invalid")
    lanes = set(selection["selection_policy"]["coverage_lanes"])
    selected_lanes = {
        lane for paper in papers for lane in paper.get("coverage_lanes", [])
    }
    if selected_lanes != lanes:
        raise DatasetValidationError(
            f"Coverage lane mismatch: {sorted(lanes ^ selected_lanes)}"
        )
    identifiers = [paper.get("arxiv_id") for paper in papers]
    if (
        any(not isinstance(item, str) or not ARXIV_ID_RE.fullmatch(item)
            for item in identifiers)
        or identifiers != sorted(set(identifiers))
    ):
        raise DatasetValidationError("Selected paper identities are invalid")
    return set(identifiers)


def _validate_inventory(
    inventory: dict[str, Any],
    selection_ids: set[str],
) -> set[str]:
    rows = inventory.get("papers")
    if (
        inventory.get("schema_version")
        != "knowledge-methodology-corpus-inventory/1.0"
        or inventory.get("paper_count") != 47
        or inventory.get("new_paper_count") != 32
        or inventory.get("reused_paper_count") != 15
        or not isinstance(rows, list)
        or len(rows) != 47
    ):
        raise DatasetValidationError("Inventory envelope is invalid")
    if inventory.get("selection_sha256") != _sha256(SELECTION_PATH):
        raise DatasetValidationError("Inventory selection digest is stale")
    identities = [row.get("arxiv_id") for row in rows]
    if identities != sorted(set(identities)):
        raise DatasetValidationError("Inventory identities are not sorted unique")
    new_rows = {
        row["arxiv_id"]
        for row in rows
        if row.get("source_group") == "new-methodology-papers"
    }
    reused_rows = {
        row["arxiv_id"]
        for row in rows
        if row.get("source_group") == "reused-graphrag-papers"
    }
    if new_rows != selection_ids or len(reused_rows) != 15:
        raise DatasetValidationError("Inventory source-group membership is invalid")
    for row in rows:
        markdown = ROOT / "sources" / row["markdown_path"]
        if not markdown.is_file() or _sha256(markdown) != row["markdown_sha256"]:
            raise DatasetValidationError(
                f"Markdown binding failed: {row['arxiv_id']}"
            )
        metadata = _frontmatter(markdown)
        if metadata.get("paper_id") != row["arxiv_id"]:
            raise DatasetValidationError(
                f"Markdown identity failed: {row['arxiv_id']}"
            )
        if metadata.get("pdf_sha256") != row["pdf_sha256"]:
            raise DatasetValidationError(
                f"Markdown PDF digest failed: {row['arxiv_id']}"
            )
        pdf_path = Path(row["pdf_path"])
        if row["source_group"] == "new-methodology-papers":
            pdf = ROOT / "sources" / pdf_path
        else:
            pdf = REPOSITORY_ROOT / pdf_path
        if not pdf.is_file() or _sha256(pdf) != row["pdf_sha256"]:
            raise DatasetValidationError(
                f"PDF binding failed: {row['arxiv_id']}"
            )
    return set(identities)


def _validate_manifest(manifest: dict[str, Any], identities: set[str]) -> None:
    sources = manifest.get("sources")
    if (
        manifest.get("schema_version") != "1.0"
        or not isinstance(sources, list)
        or len(sources) != 47
    ):
        raise DatasetValidationError("Semantic manifest envelope is invalid")
    expected_ids = {
        identity.replace(".", "-", 1)
        for identity in identities
    }
    actual_ids = {
        source.get("id", "").removeprefix("paper-")
        for source in sources
    }
    if actual_ids != expected_ids:
        raise DatasetValidationError("Semantic manifest identity coverage failed")
    for source in sources:
        path = ROOT / source["path"]
        if not path.is_file():
            raise DatasetValidationError(
                f"Semantic manifest source is absent: {source['path']}"
            )
    if len(actual_ids) != 47:
        raise DatasetValidationError("Semantic manifest has duplicate sources")


def _validate_source_combination(
    value: dict[str, Any],
    manifest: dict[str, Any],
) -> None:
    members = value.get("members")
    partitions = value.get("physical_partitions")
    expected_members = sorted(source["id"] for source in manifest["sources"])
    if (
        value.get("protocol_version") != "1.0"
        or value.get("decision_id")
        != "knowledge-methodology-paper-combination-001"
        or value.get("dataset_id") != "knowledge-methodology-papers-47"
        or value.get("mode") != "separate-in-bundle"
        or value.get("logical_source_id") is not None
        or value.get("identity_scope") != "source-and-record-id"
        or value.get("duplicate_policy")
        != "reject-within-identity-scope"
        or value.get("record_fusion") is not False
        or members != expected_members
        or not isinstance(partitions, list)
        or [row.get("paper_count") for row in partitions] != [32, 15]
    ):
        raise DatasetValidationError("Source-combination decision is invalid")
    for partition in partitions:
        path = ROOT / partition["path"]
        if not path.is_dir():
            raise DatasetValidationError(
                f"Source-combination partition is absent: {partition['path']}"
            )


def _validate_bundle_and_audit(
    audit: dict[str, Any],
    identities: set[str],
) -> int:
    report = _load_json(BUNDLE_PATH / "semantic" / "build-report.json")
    ledger_path = BUNDLE_PATH / "semantic" / "records.jsonl"
    if (
        not isinstance(report, dict)
        or report.get("status") != "pass"
        or report.get("valid") is not True
        or not ledger_path.is_file()
    ):
        raise DatasetValidationError("Semantic OKF snapshot is not passing")
    records = [
        json.loads(line)
        for line in ledger_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    if len(records) != 47:
        raise DatasetValidationError("Semantic OKF ledger count is invalid")

    recommendations = audit.get("recommendations")
    if (
        audit.get("schema_version") != "knowledge-methodology-audit/1.0"
        or audit.get("dataset_id") != "knowledge-methodology-papers-47"
        or audit.get("status") != "complete"
        or not isinstance(recommendations, list)
        or len(recommendations) < 10
    ):
        raise DatasetValidationError("Methodology audit envelope is invalid")
    recommendation_ids = [row.get("id") for row in recommendations]
    if len(recommendation_ids) != len(set(recommendation_ids)):
        raise DatasetValidationError("Methodology audit IDs are not unique")
    for recommendation in recommendations:
        evidence = recommendation.get("evidence")
        if not isinstance(evidence, list):
            raise DatasetValidationError("Audit evidence must be an array")
        for citation in evidence:
            paper_id = citation.get("paper_id")
            concept_path = citation.get("concept_path")
            pages = citation.get("pdf_pages")
            if (
                paper_id not in identities
                or not isinstance(concept_path, str)
                or not isinstance(pages, list)
                or not pages
                or any(not isinstance(page, int) or page < 1 for page in pages)
            ):
                raise DatasetValidationError(
                    f"Audit citation is invalid: {citation!r}"
                )
            concept = EXPERT_KNOWLEDGE_PATH / concept_path
            if not concept.is_file():
                raise DatasetValidationError(
                    f"Audit concept is absent: {concept_path}"
                )
            text = concept.read_text(encoding="utf-8")
            for page in pages:
                if f"## PDF page {page}\n" not in text:
                    raise DatasetValidationError(
                        f"Audit page is absent: {concept_path} page {page}"
                    )
    return len(recommendations)


def main(argv: Sequence[str] | None = None) -> int:
    """Validate the complete dataset contract."""

    del argv
    try:
        for path in (
            SELECTION_PATH,
            INVENTORY_PATH,
            MANIFEST_PATH,
            SOURCE_COMBINATION_PATH,
            AUDIT_PATH,
        ):
            if not path.is_file():
                raise DatasetValidationError(f"Required file is absent: {path}")
        selection = _load_json(SELECTION_PATH)
        inventory = _load_json(INVENTORY_PATH)
        manifest = _load_json(MANIFEST_PATH)
        source_combination = _load_json(SOURCE_COMBINATION_PATH)
        audit = _load_json(AUDIT_PATH)
        if not all(
            isinstance(value, dict)
            for value in (
                selection,
                inventory,
                manifest,
                source_combination,
                audit,
            )
        ):
            raise DatasetValidationError("A required JSON root is not an object")
        selection_ids = _validate_selection(selection)
        identities = _validate_inventory(inventory, selection_ids)
        _validate_manifest(manifest, identities)
        _validate_source_combination(source_combination, manifest)
        recommendation_count = _validate_bundle_and_audit(audit, identities)
        result = {
            "status": "pass",
            "dataset_id": "knowledge-methodology-papers-47",
            "paper_count": len(identities),
            "coverage_lane_count": len(
                selection["selection_policy"]["coverage_lanes"]
            ),
            "manifest_source_count": len(manifest["sources"]),
            "audit_recommendation_count": recommendation_count,
        }
    except (
        DatasetValidationError,
        KeyError,
        OSError,
        UnicodeError,
        json.JSONDecodeError,
    ) as exc:
        result = {"status": "error", "error": str(exc)}
        print(json.dumps(result, sort_keys=True))
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
