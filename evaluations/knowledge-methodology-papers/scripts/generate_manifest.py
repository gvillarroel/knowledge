#!/usr/bin/env python3
"""Generate the deterministic Semantic OKF manifest for the paper corpus."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Sequence


ROOT = Path(__file__).resolve().parents[1]
INVENTORY_PATH = ROOT / "sources" / "inventory.json"
MANIFEST_PATH = ROOT / "manifest.json"


class ManifestError(ValueError):
    """Raised when the corpus cannot produce the expected manifest."""


PAPER_FIELDS = {
    "title": "paperTitle",
    "description": "selectionDimension",
    "paper_id": "paperId",
    "arxiv_id": "arxivId",
    "arxiv_version": "arxivVersion",
    "publication_year": "publicationYear",
    "authors": "authors",
    "source_url": "sourceUrl",
    "pdf_url": "pdfUrl",
    "pdf_sha256": "pdfSha256",
    "page_count": "pageCount",
    "extracted_characters": "extractedCharacters",
}


def _canonical_json(value: Any) -> str:
    return (
        json.dumps(
            value,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
            allow_nan=False,
        )
        + "\n"
    )


def _property(name: str, field_range: str) -> dict[str, str]:
    return {
        "domain": "Paper",
        "kind": "datatype",
        "name": name,
        "range": field_range,
    }


def _manifest() -> dict[str, Any]:
    if not INVENTORY_PATH.is_file():
        raise ManifestError("Acquire the paper corpus before generating a manifest")
    inventory = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    rows = inventory.get("papers") if isinstance(inventory, dict) else None
    if (
        inventory.get("schema_version")
        != "knowledge-methodology-corpus-inventory/1.0"
        or inventory.get("dataset_id") != "knowledge-methodology-papers-47"
        or not isinstance(rows, list)
        or len(rows) != 47
    ):
        raise ManifestError("Corpus inventory is invalid")
    identifiers = [row.get("arxiv_id") for row in rows]
    if identifiers != sorted(set(identifiers)):
        raise ManifestError("Inventory identities must be sorted and unique")
    sources: list[dict[str, Any]] = []
    for row in rows:
        markdown_path = row.get("markdown_path")
        identity = row.get("arxiv_id")
        if not isinstance(markdown_path, str) or not isinstance(identity, str):
            raise ManifestError("Inventory row is incomplete")
        path = ROOT / "sources" / markdown_path
        if not path.is_file():
            raise ManifestError(f"Inventory Markdown is absent: {markdown_path}")
        sources.append(
            {
                "concept_type": "Research Paper",
                "fields": PAPER_FIELDS,
                "id": "paper-" + identity.replace(".", "-").casefold(),
                "kind": "markdown",
                "ontology_class": "Paper",
                "path": f"sources/{markdown_path}",
            }
        )
    return {
        "bundle": {
            "base_iri": "https://example.org/knowledge-methodology-papers/",
            "description": (
                "Forty-seven version-pinned papers covering knowledge "
                "construction, representation, retrieval, validation, "
                "evaluation, and skill evolution."
            ),
            "ontology_iri": (
                "https://example.org/ontology/knowledge-methodology-papers"
            ),
            "owl_profile": "rl",
            "prefix": "kmp",
            "title": "Knowledge Methodology Research Paper Corpus",
            "version_iri": (
                "https://example.org/ontology/"
                "knowledge-methodology-papers/1.0.0"
            ),
        },
        "ontology": {
            "classes": [{"label": "research paper", "name": "Paper"}],
            "properties": [
                _property("paperTitle", "xsd:string"),
                _property("selectionDimension", "xsd:string"),
                _property("paperId", "xsd:string"),
                _property("arxivId", "xsd:string"),
                _property("arxivVersion", "xsd:string"),
                _property("publicationYear", "xsd:integer"),
                _property("authors", "xsd:string"),
                _property("sourceUrl", "xsd:string"),
                _property("pdfUrl", "xsd:string"),
                _property("pdfSha256", "xsd:string"),
                _property("pageCount", "xsd:integer"),
                _property("extractedCharacters", "xsd:integer"),
            ],
        },
        "rules": [
            {
                "basis": {
                    "kind": "evidence",
                    "references": ["KNOWLEDGE-METHODOLOGY-SELECTION-1"],
                },
                "datatype": "xsd:string",
                "max_count": 1,
                "message": "Every paper must retain one exact versioned arXiv ID.",
                "min_count": 1,
                "name": "PaperIdentifierRule",
                "path": "paperId",
                "pattern": "^[0-9]{4}\\.[0-9]{4,5}v[0-9]+$",
                "target_class": "Paper",
            },
            {
                "basis": {
                    "kind": "evidence",
                    "references": ["KNOWLEDGE-METHODOLOGY-INVENTORY-1"],
                },
                "datatype": "xsd:string",
                "max_count": 1,
                "message": "Every paper must retain its pinned PDF digest.",
                "min_count": 1,
                "name": "PaperDigestRule",
                "path": "pdfSha256",
                "pattern": "^[0-9a-f]{64}$",
                "target_class": "Paper",
            },
            {
                "basis": {
                    "kind": "evidence",
                    "references": ["KNOWLEDGE-METHODOLOGY-METADATA-1"],
                },
                "datatype": "xsd:string",
                "max_count": 1,
                "message": "Every paper must retain its official title.",
                "min_count": 1,
                "name": "PaperTitleRule",
                "path": "paperTitle",
                "pattern": ".+",
                "target_class": "Paper",
            },
        ],
        "schema_version": "1.0",
        "sources": sources,
    }


def build_parser() -> argparse.ArgumentParser:
    """Build the manifest generator command line."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Compare generated bytes with the accepted manifest",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Generate or check the paper-corpus manifest."""

    args = build_parser().parse_args(argv)
    try:
        rendered = _canonical_json(_manifest())
        if args.check:
            if not MANIFEST_PATH.is_file():
                raise ManifestError("Accepted manifest is absent")
            if MANIFEST_PATH.read_text(encoding="utf-8") != rendered:
                raise ManifestError("Accepted manifest has deterministic drift")
            status = "pass"
        else:
            MANIFEST_PATH.write_text(rendered, encoding="utf-8", newline="\n")
            status = "created"
    except (ManifestError, OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, sort_keys=True))
        return 2
    print(
        json.dumps(
            {
                "status": status,
                "manifest": str(MANIFEST_PATH),
                "source_count": 47,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
