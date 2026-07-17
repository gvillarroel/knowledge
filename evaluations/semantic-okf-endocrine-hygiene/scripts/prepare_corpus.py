#!/usr/bin/env python3
"""Normalize the lossless Know BioC acquisition into a pinned Semantic OKF corpus."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any, Iterable, Mapping
from urllib.parse import quote

import yaml


EVALUATION = Path(__file__).resolve().parents[1]
CORPUS = EVALUATION / "corpus"
SELECTION_PATH = CORPUS / "acquisition-selection.json"
CLAIMS_SEED_PATH = CORPUS / "claims-seed.json"
BASE_IRI = "https://example.org/endocrine-hygiene/"
SCHEMA_VERSION = "semantic-okf-endocrine-hygiene-corpus/1.0"
BIOC_URL = "https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/BioC_json/{pmcid}/unicode"
HEX_64 = re.compile(r"[0-9a-f]{64}")
PMCID_RE = re.compile(r"PMC[1-9][0-9]*")
GENERATED_ROOTS = (
    Path("sources/markdown"),
    Path("sources/claims"),
    Path("sources/semantic"),
)


class PreparationError(RuntimeError):
    """Describe an invalid acquisition, seed, or generated corpus."""


class _PromotionRecoveryError(PreparationError):
    """Report a failed rollback whose transaction directory must be retained."""


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def pretty_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n"


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def strict_json(text: str, label: str) -> Any:
    def reject_constant(value: str) -> Any:
        raise PreparationError(f"{label} contains non-standard number {value!r}")

    def reject_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise PreparationError(f"{label} contains duplicate member {key!r}")
            result[key] = value
        return result

    try:
        return json.loads(text, object_pairs_hook=reject_duplicates, parse_constant=reject_constant)
    except json.JSONDecodeError as exc:
        raise PreparationError(f"{label} is invalid JSON: {exc}") from exc


def load_json(path: Path) -> Any:
    try:
        return strict_json(path.read_text(encoding="utf-8"), path.as_posix())
    except OSError as exc:
        raise PreparationError(f"cannot read {path.as_posix()}: {exc}") from exc


def exact_keys(value: Mapping[str, Any], expected: set[str], label: str) -> None:
    actual = set(value)
    if actual != expected:
        raise PreparationError(
            f"{label} has a closed schema; missing={sorted(expected - actual)}, unknown={sorted(actual - expected)}"
        )


def normalize_pmcid(value: Any, label: str) -> str:
    raw = str(value)
    result = raw if raw.startswith("PMC") else f"PMC{raw}"
    if PMCID_RE.fullmatch(result) is None:
        raise PreparationError(f"{label} is not a canonical PMCID: {value!r}")
    return result


def split_okf_markdown(path: Path) -> tuple[dict[str, Any], str, bytes]:
    raw = path.read_bytes()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise PreparationError(f"{path.as_posix()} is not UTF-8") from exc
    match = re.match(r"\A---\r?\n(?P<frontmatter>.*?)\r?\n---\r?\n", text, flags=re.DOTALL)
    if match is None:
        raise PreparationError(f"{path.as_posix()} lacks closed YAML frontmatter")
    frontmatter_text = match.group("frontmatter")
    body = text[match.end() :]
    frontmatter = yaml.safe_load(frontmatter_text)
    if not isinstance(frontmatter, dict):
        raise PreparationError(f"{path.as_posix()} frontmatter is not an object")
    return frontmatter, body.strip(), raw


def _name_order(key: str) -> int:
    match = re.fullmatch(r"name_(\d+)", key)
    return int(match.group(1)) if match else 10**9


def authors_from_infons(infons: Mapping[str, Any]) -> list[str]:
    result: list[str] = []
    for key in sorted((item for item in infons if re.fullmatch(r"name_\d+", item)), key=_name_order):
        parts: dict[str, str] = {}
        for component in str(infons[key]).split(";"):
            name, separator, value = component.partition(":")
            if separator:
                parts[name] = value
        author = " ".join(part for part in (parts.get("given-names"), parts.get("surname")) if part)
        if author:
            result.append(author)
    return result


def first_infon(passages: Iterable[Mapping[str, Any]], key: str) -> str | None:
    for passage in passages:
        infons = passage.get("infons")
        if isinstance(infons, dict) and isinstance(infons.get(key), str) and infons[key].strip():
            return infons[key].strip()
    return None


def is_json_content_type(value: Any) -> bool:
    """Return whether an HTTP media type carries JSON content."""

    media_type = str(value or "").partition(";")[0].strip().casefold()
    return media_type == "application/json" or media_type.endswith("+json")


def paper_record(selection: Mapping[str, Any], know_root: Path, know_key: str) -> dict[str, Any]:
    pmcid = normalize_pmcid(selection.get("pmcid"), "selection.pmcid")
    source_id = pmcid.casefold()
    pages_dir = know_root / know_key / "site" / source_id / "pages"
    paths = sorted(pages_dir.glob("*.md"))
    if len(paths) != 1:
        raise PreparationError(f"Know source {source_id} must contain exactly one Markdown page; observed {len(paths)}")
    frontmatter, body, know_bytes = split_okf_markdown(paths[0])
    expected_url = BIOC_URL.format(pmcid=pmcid)
    if frontmatter.get("knowledge_key") != know_key or frontmatter.get("source_id") != source_id:
        raise PreparationError(f"Know identity mismatch for {pmcid}")
    if frontmatter.get("url") != expected_url:
        raise PreparationError(f"Know URL mismatch for {pmcid}")
    metadata = frontmatter.get("source_metadata")
    if not isinstance(metadata, dict):
        raise PreparationError(f"Know source metadata is missing for {pmcid}")
    if metadata.get("content_format") != "json" or not is_json_content_type(metadata.get("content_type")):
        raise PreparationError(f"Know source {pmcid} was not captured through lossless JSON mode")
    raw_sha256 = sha256_bytes(body.encode("utf-8"))
    if metadata.get("raw_content_sha256") != raw_sha256 or metadata.get("raw_content_bytes") != len(
        body.encode("utf-8")
    ):
        raise PreparationError(f"Know raw-content hash or byte count does not bind the stored JSON for {pmcid}")
    payload = strict_json(body, f"Know BioC body for {pmcid}")
    if not isinstance(payload, list) or len(payload) != 1 or not isinstance(payload[0], dict):
        raise PreparationError(f"BioC root for {pmcid} must contain one collection")
    documents = payload[0].get("documents")
    if not isinstance(documents, list) or len(documents) != 1 or not isinstance(documents[0], dict):
        raise PreparationError(f"BioC collection for {pmcid} must contain one document")
    document = documents[0]
    if normalize_pmcid(document.get("id"), "BioC document.id") != pmcid:
        raise PreparationError(f"BioC document identity mismatch for {pmcid}")
    passages = document.get("passages")
    if not isinstance(passages, list) or not passages or any(not isinstance(item, dict) for item in passages):
        raise PreparationError(f"BioC document {pmcid} has no passage array")
    normalized_passages: list[dict[str, Any]] = []
    for index, passage in enumerate(passages, start=1):
        text = passage.get("text")
        offset = passage.get("offset")
        infons = passage.get("infons")
        if not isinstance(text, str) or isinstance(offset, bool) or not isinstance(offset, int) or not isinstance(infons, dict):
            raise PreparationError(f"BioC {pmcid} passage {index} has an invalid text, offset, or infons value")
        normalized_passages.append(
            {
                "index": index,
                "offset": offset,
                "section_type": str(infons.get("section_type") or "UNKNOWN"),
                "passage_type": str(infons.get("type") or "unknown"),
                "text": text,
                "text_sha256": sha256_bytes(text.encode("utf-8")),
            }
        )
    title = next(
        (item["text"] for item in normalized_passages if item["section_type"] == "TITLE" and item["text"].strip()),
        None,
    )
    if not title:
        raise PreparationError(f"BioC document {pmcid} lacks a title passage")
    first_infons = passages[0]["infons"]
    authors = authors_from_infons(first_infons)
    doi = first_infon(passages, "article-id_doi")
    pmid = first_infon(passages, "article-id_pmid")
    year_text = first_infon(passages, "year")
    if doi is None or year_text is None or not year_text.isdigit():
        raise PreparationError(f"BioC document {pmcid} lacks DOI or year metadata")
    license_value = str(document.get("infons", {}).get("license") or first_infons.get("license") or "unspecified")
    return {
        "pmcid": pmcid,
        "pmid": pmid,
        "doi": doi,
        "year": int(year_text),
        "title": title,
        "authors": authors,
        "license": license_value,
        "role": selection["role"],
        "relevance": selection["relevance"],
        "caution": selection["caution"],
        "bioc_url": expected_url,
        "article_url": f"https://pmc.ncbi.nlm.nih.gov/articles/{pmcid}/",
        "raw_bioc_sha256": raw_sha256,
        "raw_bioc_bytes": len(body.encode("utf-8")),
        "know_page_sha256": sha256_bytes(know_bytes),
        "passages": normalized_passages,
    }


def yaml_scalar(value: Any) -> str:
    rendered = yaml.safe_dump(value, allow_unicode=True, default_flow_style=True, width=10_000).strip()
    return re.sub(r"\n\.\.\.\s*\Z", "", rendered).strip()


def render_paper(paper: Mapping[str, Any]) -> str:
    frontmatter = {
        "title": paper["title"],
        "description": paper["relevance"],
        "type": "Paper",
        "resource": paper["article_url"],
        "tags": "endocrine-disruption; hygiene-products; personal-care-products; research-paper",
        "paper_id": paper["pmcid"],
        "pmcid": paper["pmcid"],
        "doi": paper["doi"],
        "publication_year": paper["year"],
        "authors": "; ".join(paper["authors"]),
        "source_url": paper["article_url"],
        "bioc_url": paper["bioc_url"],
        "raw_bioc_sha256": paper["raw_bioc_sha256"],
        "raw_bioc_bytes": paper["raw_bioc_bytes"],
        "passage_count": len(paper["passages"]),
        "nonempty_passage_count": sum(bool(item["text"].strip()) for item in paper["passages"]),
        "extracted_characters": sum(len(item["text"]) for item in paper["passages"]),
        "license": paper["license"],
        "corpus_role": paper["role"],
        "evidence_caution": paper["caution"],
    }
    if paper["pmid"] is not None:
        frontmatter["pmid"] = paper["pmid"]
    lines = ["---"]
    for key, value in frontmatter.items():
        lines.append(f"{key}: {yaml_scalar(value)}")
    lines.extend(
        [
            "---",
            "",
            f"# {paper['title']}",
            "",
            "## Source citation",
            "",
            f"- PMCID: [{paper['pmcid']}]({paper['article_url']})",
            f"- DOI: `{paper['doi']}`",
            f"- NCBI BioC source: [{paper['bioc_url']}]({paper['bioc_url']})",
            f"- Raw BioC SHA-256: `{paper['raw_bioc_sha256']}`",
            f"- Evidence caveat: {paper['caution']}",
            "",
            "The following sections preserve NCBI BioC passage boundaries. They are not PDF pages. Each heading is a stable corpus locator bound to the original passage offset and text hash.",
            "",
        ]
    )
    for passage in paper["passages"]:
        if not passage["text"].strip():
            continue
        lines.extend(
            [
                f"## BioC passage {passage['index']:04d}",
                "",
                (
                    f"Locator metadata: offset={passage['offset']}; section_type={passage['section_type']}; "
                    f"passage_type={passage['passage_type']}; text_sha256={passage['text_sha256']}"
                ),
                "",
                passage["text"],
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def resource_iri(source_id: str, record_id: str) -> str:
    return f"{BASE_IRI}resource/{source_id}/{quote(record_id, safe='')}"


def render_jsonl(rows: Iterable[Mapping[str, Any]]) -> str:
    return "".join(canonical_json(row) + "\n" for row in rows)


def vocabulary_rows(papers: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    dimensions = [
        ("dimension-disparity", "population disparity", "Differences in product use, exposure, or risk across populations."),
        ("dimension-exposure-biomarker", "exposure biomarker", "Measured internal biomarker associated with product use."),
        ("dimension-health-outcome", "health outcome", "Observed or hypothesized health or pregnancy outcome."),
        ("dimension-hormonal-mechanism", "hormonal mechanism", "Hormone concentration, receptor activity, or endocrine pathway evidence."),
        ("dimension-intervention-effect", "intervention effect", "Change observed after a product substitution or exposure intervention."),
        ("dimension-limitation", "limitation", "Design, measurement, generalizability, or causal-inference boundary."),
        ("dimension-methodology", "methodology", "Population, assay, sampling matrix, or analytical design."),
        ("dimension-null-contrary", "null or contrary result", "Null, inconsistent, unexpected, or directionally contrary result."),
        ("dimension-product-content", "product content", "Chemical content measured directly in a consumer or occupational product."),
        ("dimension-risk-assessment", "risk assessment", "Modeled exposure, hazard, or risk estimate."),
    ]
    rows = [
        {"id": identifier, "label": label, "term_kind": "analysis-dimension", "definition": definition}
        for identifier, label, definition in dimensions
    ]
    for paper in papers:
        rows.append(
            {
                "id": f"method-{str(paper['pmcid']).casefold()}",
                "label": f"{paper['pmcid']} study design",
                "term_kind": "paper-specific-method",
                "definition": f"The population, exposure, assay, and analysis design reported in {paper['title']}.",
            }
        )
    return sorted(rows, key=lambda row: row["id"])


def claim_rows(seed: Any, papers: Mapping[str, Mapping[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    if not isinstance(seed, dict):
        raise PreparationError("claims seed root must be an object")
    exact_keys(seed, {"schema_version", "claims"}, "claims seed")
    if seed["schema_version"] != "semantic-okf-endocrine-hygiene-claims-seed/1.0":
        raise PreparationError("claims seed schema version is unsupported")
    claims = seed["claims"]
    if not isinstance(claims, list) or not claims or any(not isinstance(item, dict) for item in claims):
        raise PreparationError("claims seed must contain a nonempty object array")
    grouped: dict[str, list[dict[str, Any]]] = {pmcid: [] for pmcid in papers}
    observed_ids: set[str] = set()
    expected = {
        "id",
        "paper_id",
        "passage",
        "passage_sha256",
        "claim_kind",
        "dimension_id",
        "interpretation",
        "claim_origin",
        "confidence",
    }
    for number, raw in enumerate(claims, start=1):
        exact_keys(raw, expected, f"claims seed row {number}")
        claim_id = raw["id"]
        pmcid = normalize_pmcid(raw["paper_id"], f"claims seed row {number}.paper_id")
        if not isinstance(claim_id, str) or not claim_id.startswith(f"claim-{pmcid.casefold()}-") or claim_id in observed_ids:
            raise PreparationError(f"claims seed row {number} has an invalid or duplicate ID")
        observed_ids.add(claim_id)
        if pmcid not in papers:
            raise PreparationError(f"claims seed row {number} names an unselected paper")
        passage_number = raw["passage"]
        if isinstance(passage_number, bool) or not isinstance(passage_number, int):
            raise PreparationError(f"claims seed row {number}.passage must be an integer")
        passages = papers[pmcid]["passages"]
        if not 1 <= passage_number <= len(passages):
            raise PreparationError(f"claims seed row {number} passage is out of range")
        passage = passages[passage_number - 1]
        if passage["text_sha256"] != raw["passage_sha256"] or not passage["text"].strip():
            raise PreparationError(f"claims seed row {number} does not bind the declared passage hash")
        dimension_id = raw["dimension_id"]
        if not isinstance(dimension_id, str) or not dimension_id.startswith("dimension-"):
            raise PreparationError(f"claims seed row {number} has an invalid dimension")
        if not all(isinstance(raw[key], str) and raw[key].strip() for key in expected - {"passage"}):
            raise PreparationError(f"claims seed row {number} contains an empty string")
        record_id = f"sources/markdown/{pmcid}"
        source_id = f"paper-{pmcid.casefold()}"
        locator = f"sources/markdown/{pmcid}.md#BioC-passage-{passage_number:04d}"
        grouped[pmcid].append(
            {
                "id": claim_id,
                "title": f"{pmcid} {raw['claim_kind']} claim {len(grouped[pmcid]) + 1:03d}",
                "paper_iri": resource_iri(source_id, record_id),
                "subject_term_iri": resource_iri("analysis-vocabulary", f"method-{pmcid.casefold()}"),
                "object_term_iri": resource_iri("analysis-vocabulary", dimension_id),
                "claim_kind": raw["claim_kind"],
                "claim_origin": raw["claim_origin"],
                "evidence_locator": locator,
                "interpretation": raw["interpretation"],
                "confidence": raw["confidence"],
                "review_state": "reviewed",
                "bioc_sha256": papers[pmcid]["raw_bioc_sha256"],
                "evidence_text_sha256": passage["text_sha256"],
            }
        )
    missing = sorted(pmcid for pmcid, rows in grouped.items() if not rows)
    if missing:
        raise PreparationError(f"every selected paper needs at least one reviewed claim: {missing}")
    for rows in grouped.values():
        rows.sort(key=lambda row: row["id"])
    return grouped


def manifest(papers: list[Mapping[str, Any]]) -> dict[str, Any]:
    properties = [
        {"name": "paperTitle", "kind": "datatype", "domain": "Paper", "range": "xsd:string"},
        {"name": "selectionDimension", "kind": "datatype", "domain": "Paper", "range": "xsd:string"},
        {"name": "paperId", "kind": "datatype", "domain": "Paper", "range": "xsd:string"},
        {"name": "pmcid", "kind": "datatype", "domain": "Paper", "range": "xsd:string"},
        {"name": "pmid", "kind": "datatype", "domain": "Paper", "range": "xsd:string"},
        {"name": "doi", "kind": "datatype", "domain": "Paper", "range": "xsd:string"},
        {"name": "publicationYear", "kind": "datatype", "domain": "Paper", "range": "xsd:integer"},
        {"name": "authors", "kind": "datatype", "domain": "Paper", "range": "xsd:string"},
        {"name": "sourceUrl", "kind": "datatype", "domain": "Paper", "range": "xsd:string"},
        {"name": "biocUrl", "kind": "datatype", "domain": "Paper", "range": "xsd:string"},
        {"name": "rawBiocSha256", "kind": "datatype", "domain": "Paper", "range": "xsd:string"},
        {"name": "rawBiocBytes", "kind": "datatype", "domain": "Paper", "range": "xsd:integer"},
        {"name": "passageCount", "kind": "datatype", "domain": "Paper", "range": "xsd:integer"},
        {"name": "extractedCharacters", "kind": "datatype", "domain": "Paper", "range": "xsd:integer"},
        {"name": "license", "kind": "datatype", "domain": "Paper", "range": "xsd:string"},
        {"name": "corpusRole", "kind": "datatype", "domain": "Paper", "range": "xsd:string"},
        {"name": "evidenceCaution", "kind": "datatype", "domain": "Paper", "range": "xsd:string"},
        {"name": "termLabel", "kind": "datatype", "domain": "AnalysisTerm", "range": "xsd:string"},
        {"name": "termKind", "kind": "datatype", "domain": "AnalysisTerm", "range": "xsd:string"},
        {"name": "termDefinition", "kind": "datatype", "domain": "AnalysisTerm", "range": "xsd:string"},
        {"name": "aboutPaper", "kind": "object", "domain": "PaperSemanticClaim", "range": "Paper"},
        {"name": "subjectTerm", "kind": "object", "domain": "PaperSemanticClaim", "range": "AnalysisTerm"},
        {"name": "objectTerm", "kind": "object", "domain": "PaperSemanticClaim", "range": "AnalysisTerm"},
        {"name": "claimKind", "kind": "datatype", "domain": "PaperSemanticClaim", "range": "xsd:string"},
        {"name": "claimOrigin", "kind": "datatype", "domain": "PaperSemanticClaim", "range": "xsd:string"},
        {"name": "evidenceLocator", "kind": "datatype", "domain": "PaperSemanticClaim", "range": "xsd:string"},
        {"name": "interpretation", "kind": "datatype", "domain": "PaperSemanticClaim", "range": "xsd:string"},
        {"name": "confidence", "kind": "datatype", "domain": "PaperSemanticClaim", "range": "xsd:string"},
        {"name": "reviewState", "kind": "datatype", "domain": "PaperSemanticClaim", "range": "xsd:string"},
        {"name": "claimBiocSha256", "kind": "datatype", "domain": "PaperSemanticClaim", "range": "xsd:string"},
        {"name": "evidenceTextSha256", "kind": "datatype", "domain": "PaperSemanticClaim", "range": "xsd:string"},
    ]
    rules = [
        {
            "name": "PaperIdentifierRule",
            "target_class": "Paper",
            "path": "paperId",
            "min_count": 1,
            "max_count": 1,
            "message": "Every paper must retain its canonical PMCID.",
            "basis": {"kind": "evidence", "references": ["END-HYG-STUDY-1"]},
            "datatype": "xsd:string",
            "pattern": "^PMC[1-9][0-9]*$",
        },
        {
            "name": "PaperDigestRule",
            "target_class": "Paper",
            "path": "rawBiocSha256",
            "min_count": 1,
            "max_count": 1,
            "message": "Every paper must retain its accepted raw BioC digest.",
            "basis": {"kind": "evidence", "references": ["END-HYG-STUDY-1"]},
            "datatype": "xsd:string",
            "pattern": "^[0-9a-f]{64}$",
        },
        {
            "name": "TermLabelRule",
            "target_class": "AnalysisTerm",
            "path": "termLabel",
            "min_count": 1,
            "max_count": 1,
            "message": "Every analysis term must have a label.",
            "basis": {"kind": "evidence", "references": ["END-HYG-STUDY-1"]},
            "datatype": "xsd:string",
            "pattern": ".+",
        },
        {
            "name": "ClaimPaperRule",
            "target_class": "PaperSemanticClaim",
            "path": "aboutPaper",
            "min_count": 1,
            "max_count": 1,
            "message": "Every claim must identify its source paper.",
            "basis": {"kind": "evidence", "references": ["END-HYG-STUDY-1"]},
            "class": "Paper",
            "node_kind": "IRI",
        },
        {
            "name": "ClaimSubjectRule",
            "target_class": "PaperSemanticClaim",
            "path": "subjectTerm",
            "min_count": 1,
            "max_count": 1,
            "message": "Every claim must identify its paper-specific study design.",
            "basis": {"kind": "evidence", "references": ["END-HYG-STUDY-1"]},
            "class": "AnalysisTerm",
            "node_kind": "IRI",
        },
        {
            "name": "ClaimDimensionRule",
            "target_class": "PaperSemanticClaim",
            "path": "objectTerm",
            "min_count": 1,
            "max_count": 1,
            "message": "Every claim must identify one analysis dimension.",
            "basis": {"kind": "evidence", "references": ["END-HYG-STUDY-1"]},
            "class": "AnalysisTerm",
            "node_kind": "IRI",
        },
        {
            "name": "ClaimKindRule",
            "target_class": "PaperSemanticClaim",
            "path": "claimKind",
            "min_count": 1,
            "max_count": 1,
            "message": "Every claim must use one reviewed claim kind.",
            "basis": {"kind": "evidence", "references": ["END-HYG-STUDY-1"]},
            "datatype": "xsd:string",
            "pattern": "^(methodology|exposure-association|intervention-effect|hormonal-mechanism|health-outcome|product-content|risk-assessment|disparity|limitation|null-result|comparison)$",
        },
        {
            "name": "ClaimEvidenceRule",
            "target_class": "PaperSemanticClaim",
            "path": "evidenceLocator",
            "min_count": 1,
            "max_count": 1,
            "message": "Every claim must cite one exact BioC passage.",
            "basis": {"kind": "evidence", "references": ["END-HYG-STUDY-1"]},
            "datatype": "xsd:string",
            "pattern": "^sources/markdown/PMC[1-9][0-9]*\\.md#BioC-passage-[0-9]{4}$",
        },
        {
            "name": "ClaimReviewRule",
            "target_class": "PaperSemanticClaim",
            "path": "reviewState",
            "min_count": 1,
            "max_count": 1,
            "message": "Every accepted claim must be reviewed.",
            "basis": {"kind": "evidence", "references": ["END-HYG-STUDY-1"]},
            "datatype": "xsd:string",
            "pattern": "^reviewed$",
        },
    ]
    paper_sources = []
    claim_sources = []
    for paper in papers:
        pmcid = paper["pmcid"]
        paper_sources.append(
            {
                "id": f"paper-{pmcid.casefold()}",
                "kind": "markdown",
                "path": f"sources/markdown/{pmcid}.md",
                "concept_type": "Research Paper",
                "ontology_class": "Paper",
                "fields": {
                    "title": "paperTitle",
                    "description": "selectionDimension",
                    "paper_id": "paperId",
                    "pmcid": "pmcid",
                    "pmid": "pmid",
                    "doi": "doi",
                    "publication_year": "publicationYear",
                    "authors": "authors",
                    "source_url": "sourceUrl",
                    "bioc_url": "biocUrl",
                    "raw_bioc_sha256": "rawBiocSha256",
                    "raw_bioc_bytes": "rawBiocBytes",
                    "passage_count": "passageCount",
                    "extracted_characters": "extractedCharacters",
                    "license": "license",
                    "corpus_role": "corpusRole",
                    "evidence_caution": "evidenceCaution",
                },
            }
        )
        claim_sources.append(
            {
                "id": f"claims-{pmcid.casefold()}",
                "kind": "json",
                "path": f"sources/claims/{pmcid}.jsonl",
                "concept_type": "Paper Semantic Claim",
                "ontology_class": "PaperSemanticClaim",
                "id_field": "id",
                "title_field": "title",
                "schema": {
                    "id": "string",
                    "title": "string",
                    "paper_iri": "string",
                    "subject_term_iri": "string",
                    "object_term_iri": "string",
                    "claim_kind": "string",
                    "claim_origin": "string",
                    "evidence_locator": "string",
                    "interpretation": "string",
                    "confidence": "string",
                    "review_state": "string",
                    "bioc_sha256": "string",
                    "evidence_text_sha256": "string",
                },
                "fields": {
                    "paper_iri": "aboutPaper",
                    "subject_term_iri": "subjectTerm",
                    "object_term_iri": "objectTerm",
                    "claim_kind": "claimKind",
                    "claim_origin": "claimOrigin",
                    "evidence_locator": "evidenceLocator",
                    "interpretation": "interpretation",
                    "confidence": "confidence",
                    "review_state": "reviewState",
                    "bioc_sha256": "claimBiocSha256",
                    "evidence_text_sha256": "evidenceTextSha256",
                },
            }
        )
    vocabulary_source = {
        "id": "analysis-vocabulary",
        "kind": "json",
        "path": "sources/semantic/analysis-vocabulary.jsonl",
        "concept_type": "Analysis Term",
        "ontology_class": "AnalysisTerm",
        "id_field": "id",
        "title_field": "label",
        "schema": {"id": "string", "label": "string", "term_kind": "string", "definition": "string"},
        "fields": {"label": "termLabel", "term_kind": "termKind", "definition": "termDefinition"},
    }
    return {
        "schema_version": "1.0",
        "bundle": {
            "title": "Endocrine Disruption and Hygiene Products Semantic Corpus",
            "description": "Fifteen source-separated PMC papers with reviewed BioC-passage-grounded claims.",
            "base_iri": BASE_IRI,
            "ontology_iri": f"{BASE_IRI}ontology",
            "version_iri": f"{BASE_IRI}ontology/1.0.0",
            "prefix": "endhyg",
            "owl_profile": "rl",
        },
        "ontology": {
            "classes": [
                {"name": "Paper", "label": "research paper"},
                {"name": "AnalysisTerm", "label": "analysis term"},
                {"name": "PaperSemanticClaim", "label": "paper semantic claim"},
            ],
            "properties": properties,
        },
        "rules": rules,
        "sources": [*paper_sources, vocabulary_source, *claim_sources],
    }


def checked_file_inventory(files: Mapping[Path, bytes]) -> list[dict[str, Any]]:
    rows = []
    for path, payload in sorted(files.items(), key=lambda item: item[0].as_posix()):
        suffix = path.suffix
        row_count = None
        if suffix == ".jsonl":
            row_count = sum(bool(line) for line in payload.decode("utf-8").splitlines())
        rows.append(
            {
                "path": path.relative_to(CORPUS).as_posix(),
                "bytes": len(payload),
                "sha256": sha256_bytes(payload),
                "row_count": row_count,
            }
        )
    return rows


def build_outputs(know_store: Path) -> dict[Path, bytes]:
    selection = load_json(SELECTION_PATH)
    if not isinstance(selection, dict):
        raise PreparationError("acquisition selection root must be an object")
    exact_keys(
        selection,
        {"schema_version", "know_key", "source_kind", "accepted_export", "papers"},
        "acquisition selection",
    )
    if selection["schema_version"] != "semantic-okf-endocrine-hygiene-acquisition-selection/1.0":
        raise PreparationError("acquisition selection schema version is unsupported")
    if selection["source_kind"] != "site" or not isinstance(selection["know_key"], str):
        raise PreparationError("acquisition selection must identify one Know site key")
    accepted_export = selection["accepted_export"]
    if not isinstance(accepted_export, dict):
        raise PreparationError("acquisition selection accepted_export must be an object")
    exact_keys(accepted_export, {"filename", "bytes", "sha256"}, "accepted export")
    export_path = know_store / "exports" / str(accepted_export["filename"])
    if (
        not export_path.is_file()
        or export_path.stat().st_size != accepted_export["bytes"]
        or sha256_bytes(export_path.read_bytes()) != accepted_export["sha256"]
    ):
        raise PreparationError("accepted Know export is missing or differs from its pinned size/digest")
    paper_selections = selection["papers"]
    if not isinstance(paper_selections, list) or len(paper_selections) != 15:
        raise PreparationError("acquisition selection must contain exactly 15 papers")
    for number, item in enumerate(paper_selections, start=1):
        if not isinstance(item, dict):
            raise PreparationError(f"acquisition paper {number} must be an object")
        exact_keys(item, {"pmcid", "role", "relevance", "caution"}, f"acquisition paper {number}")
    if [item["pmcid"] for item in paper_selections] != sorted(item["pmcid"] for item in paper_selections):
        raise PreparationError("acquisition papers must be sorted by PMCID")
    papers = [paper_record(item, know_store, selection["know_key"]) for item in paper_selections]
    by_pmcid = {paper["pmcid"]: paper for paper in papers}
    if len(by_pmcid) != 15:
        raise PreparationError("acquisition contains duplicate PMCIDs")
    grouped_claims = claim_rows(load_json(CLAIMS_SEED_PATH), by_pmcid)
    outputs: dict[Path, bytes] = {}
    for paper in papers:
        outputs[CORPUS / "sources" / "markdown" / f"{paper['pmcid']}.md"] = render_paper(paper).encode("utf-8")
        outputs[CORPUS / "sources" / "claims" / f"{paper['pmcid']}.jsonl"] = render_jsonl(
            grouped_claims[paper["pmcid"]]
        ).encode("utf-8")
    outputs[CORPUS / "sources" / "semantic" / "analysis-vocabulary.jsonl"] = render_jsonl(
        vocabulary_rows(papers)
    ).encode("utf-8")
    outputs[CORPUS / "manifest.json"] = pretty_json(manifest(papers)).encode("utf-8")
    acquisition_rows = []
    for paper in papers:
        normalized_path = CORPUS / "sources" / "markdown" / f"{paper['pmcid']}.md"
        acquisition_rows.append(
            {
                "pmcid": paper["pmcid"],
                "pmid": paper["pmid"],
                "doi": paper["doi"],
                "year": paper["year"],
                "title": paper["title"],
                "license": paper["license"],
                "role": paper["role"],
                "bioc_url": paper["bioc_url"],
                "know_source_id": paper["pmcid"].casefold(),
                "know_page_sha256": paper["know_page_sha256"],
                "raw_bioc_sha256": paper["raw_bioc_sha256"],
                "raw_bioc_bytes": paper["raw_bioc_bytes"],
                "passage_count": len(paper["passages"]),
                "passage_text_characters": sum(len(item["text"]) for item in paper["passages"]),
                "normalized_path": normalized_path.relative_to(EVALUATION).as_posix(),
                "normalized_sha256": sha256_bytes(outputs[normalized_path]),
                "claim_count": len(grouped_claims[paper["pmcid"]]),
            }
        )
    acquisition = {
        "schema_version": "semantic-okf-endocrine-hygiene-acquisition/1.0",
        "know": {
            "key": selection["know_key"],
            "source_type": "site",
            "lossless_json_required": True,
            "export_is_append_only_and_ignored": True,
            "accepted_export": {
                "path": f"exports/{accepted_export['filename']}",
                "bytes": accepted_export["bytes"],
                "sha256": accepted_export["sha256"],
            },
        },
        "paper_count": len(papers),
        "total_passages": sum(len(paper["passages"]) for paper in papers),
        "total_passage_text_characters": sum(
            len(item["text"]) for paper in papers for item in paper["passages"]
        ),
        "papers": acquisition_rows,
    }
    outputs[CORPUS / "acquisition-manifest.json"] = pretty_json(acquisition).encode("utf-8")
    inventory_files = checked_file_inventory(outputs)
    inventory = {
        "schema_version": "semantic-okf-endocrine-hygiene-input-inventory/1.0",
        "paper_count": 15,
        "claim_source_count": 15,
        "auxiliary_source_count": 1,
        "authoritative_core_source_count": 30,
        "files": inventory_files,
        "inventory_sha256": sha256_bytes(canonical_json(inventory_files).encode("utf-8")),
    }
    outputs[CORPUS / "input-inventory.json"] = pretty_json(inventory).encode("utf-8")
    combination = {
        "schema_version": "semantic-okf-source-combination/1.0",
        "authoritative_sources": sorted(
            [f"paper-{paper['pmcid'].casefold()}" for paper in papers]
            + [f"claims-{paper['pmcid'].casefold()}" for paper in papers]
        ),
        "auxiliary_sources": ["analysis-vocabulary"],
        "retrieval_selection": sorted(
            [f"paper-{paper['pmcid'].casefold()}" for paper in papers]
            + [f"claims-{paper['pmcid'].casefold()}" for paper in papers]
        ),
        "identity_by_source": {
            source_id: paper["pmcid"]
            for paper in papers
            for source_id in (
                f"paper-{paper['pmcid'].casefold()}",
                f"claims-{paper['pmcid'].casefold()}",
            )
        },
        "authority_boundary": "BioC paper passages and reviewed claim records are authoritative; every retrieval projection is derived and non-authoritative.",
    }
    outputs[CORPUS / "source-combination.json"] = pretty_json(combination).encode("utf-8")
    return outputs


def _relative_outputs(outputs: Mapping[Path, bytes]) -> dict[Path, bytes]:
    relative_outputs: dict[Path, bytes] = {}
    for path, payload in outputs.items():
        try:
            relative = path.relative_to(CORPUS)
        except ValueError as exc:
            raise PreparationError(f"generated output escapes the corpus: {path.as_posix()}") from exc
        if relative == Path(".") or relative in relative_outputs:
            raise PreparationError(f"generated output path is invalid or duplicated: {path.as_posix()}")
        relative_outputs[relative] = payload
    return relative_outputs


def _is_managed_path(relative: Path, expected_paths: set[Path]) -> bool:
    return relative in expected_paths or any(root == relative or root in relative.parents for root in GENERATED_ROOTS)


def _candidate_mismatches(root: Path, outputs: Mapping[Path, bytes]) -> list[str]:
    mismatches: list[str] = []
    expected_generated = {
        relative
        for relative in outputs
        if any(generated_root == relative or generated_root in relative.parents for generated_root in GENERATED_ROOTS)
    }
    actual_generated = {
        path.relative_to(root)
        for generated_root in GENERATED_ROOTS
        if (root / generated_root).exists()
        for path in (root / generated_root).rglob("*")
        if path.is_file()
    }
    for stale in sorted(actual_generated - expected_generated, key=Path.as_posix):
        mismatches.append(f"unexpected generated file: {(CORPUS / stale).relative_to(EVALUATION).as_posix()}")
    for relative, payload in sorted(outputs.items(), key=lambda item: item[0].as_posix()):
        path = root / relative
        if not path.is_file() or path.read_bytes() != payload:
            mismatches.append(f"stale or missing: {(CORPUS / relative).relative_to(EVALUATION).as_posix()}")
    return mismatches


def _copy_unmanaged_files(source: Path, candidate: Path, expected_paths: set[Path]) -> None:
    if not source.exists():
        return
    for path in sorted(source.rglob("*"), key=lambda item: item.as_posix()):
        relative = path.relative_to(source)
        if _is_managed_path(relative, expected_paths):
            continue
        destination = candidate / relative
        if path.is_symlink():
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, destination, follow_symlinks=False)
        elif path.is_dir():
            destination.mkdir(parents=True, exist_ok=True)
        elif path.is_file():
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, destination)


def _write_staged_outputs(candidate: Path, outputs: Mapping[Path, bytes]) -> None:
    for relative, payload in sorted(outputs.items(), key=lambda item: item[0].as_posix()):
        path = candidate / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)


def _atomic_rename(source: Path, target: Path) -> None:
    """Rename one directory to an absent sibling path on the same filesystem."""

    source.rename(target)


def _promote_candidate(candidate: Path, transaction_root: Path) -> None:
    backup = transaction_root / "previous-corpus"
    previous_moved = False
    try:
        if CORPUS.exists():
            _atomic_rename(CORPUS, backup)
            previous_moved = True
        _atomic_rename(candidate, CORPUS)
    except Exception as exc:
        if previous_moved and not CORPUS.exists():
            try:
                _atomic_rename(backup, CORPUS)
            except Exception as rollback_exc:
                raise _PromotionRecoveryError(
                    "corpus publication and rollback failed; the previous complete corpus remains at "
                    f"{backup.as_posix()}: publication={exc}; rollback={rollback_exc}"
                ) from rollback_exc
        raise PreparationError(f"corpus publication failed; the previous corpus was restored: {exc}") from exc


def publish(outputs: Mapping[Path, bytes], check: bool) -> None:
    relative_outputs = _relative_outputs(outputs)
    if check:
        mismatches = _candidate_mismatches(CORPUS, relative_outputs)
        if mismatches:
            raise PreparationError("corpus check failed:\n- " + "\n- ".join(mismatches))
        return

    EVALUATION.mkdir(parents=True, exist_ok=True)
    transaction_root = Path(tempfile.mkdtemp(prefix=f".{CORPUS.name}-publication-", dir=EVALUATION))
    candidate = transaction_root / "candidate-corpus"
    candidate.mkdir()
    retain_transaction = False
    try:
        _copy_unmanaged_files(CORPUS, candidate, set(relative_outputs))
        _write_staged_outputs(candidate, relative_outputs)
        mismatches = _candidate_mismatches(candidate, relative_outputs)
        if mismatches:
            raise PreparationError("staged corpus validation failed:\n- " + "\n- ".join(mismatches))
        _promote_candidate(candidate, transaction_root)
    except _PromotionRecoveryError:
        retain_transaction = True
        raise
    except PreparationError:
        raise
    except Exception as exc:
        raise PreparationError(f"corpus staging failed before publication: {exc}") from exc
    finally:
        if not retain_transaction:
            shutil.rmtree(transaction_root, ignore_errors=True)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--know-store",
        type=Path,
        default=Path("tmp/endocrine-hygiene-know"),
        help="Root of the isolated Know store containing the synchronized BioC key.",
    )
    parser.add_argument("--check", action="store_true", help="Verify checked artifacts without writing.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        outputs = build_outputs(args.know_store.resolve())
        publish(outputs, args.check)
    except PreparationError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(
        canonical_json(
            {
                "status": "pass",
                "mode": "check" if args.check else "write",
                "output_files": len(outputs),
                "know_store": str(args.know_store),
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
