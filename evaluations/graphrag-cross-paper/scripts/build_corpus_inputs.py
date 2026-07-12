"""Build reviewed Semantic OKF inputs for the GraphRAG cross-paper study."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any
from urllib.parse import quote


ROOT = Path(__file__).resolve().parents[1]
BASE_IRI = "https://example.org/graphrag-cross-paper/"
ONTOLOGY_IRI = "https://example.org/ontology/graphrag-cross-paper"
CLAIM_KINDS = (
    "methodology",
    "graph-representation",
    "graph-construction",
    "retrieval-unit",
    "retrieval-strategy",
    "organization-synthesis",
    "task",
    "evaluation",
    "strength",
    "limitation",
    "efficiency-update",
    "safety-grounding",
    "comparison",
)
REVIEW_FIELDS = {
    "graph_representations": "graph-representation",
    "construction_methods": "graph-construction",
    "retrieval_units": "retrieval-unit",
    "retrieval_strategies": "retrieval-strategy",
    "organization_and_synthesis": "organization-synthesis",
    "query_and_task_types": "task",
    "evaluation_tasks": "evaluation",
    "reported_strengths": "strength",
    "reported_limitations": "limitation",
    "efficiency_and_updates": "efficiency-update",
}


class CorpusInputError(RuntimeError):
    """Raised when reviewed analysis cannot be converted without ambiguity."""


def canonical_json(value: Any) -> str:
    """Return stable compact JSON for hashes and JSONL rows."""
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_file(path: Path) -> str:
    """Return the hexadecimal SHA-256 digest of a file."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_id_for_paper(versioned_id: str, prefix: str) -> str:
    """Return a stable source ID for a version-pinned paper."""
    normalized = versioned_id.replace(".", "-").lower()
    return f"{prefix}-{normalized}"


def resource_iri(source_id: str, record_id: str) -> str:
    """Construct the same source-scoped resource IRI as the Semantic OKF builder."""
    return f"{BASE_IRI}resource/{quote(source_id, safe='')}/{quote(record_id, safe='')}"


def load_json(path: Path) -> dict[str, Any]:
    """Load one JSON object with a useful error for non-object roots."""
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise CorpusInputError(f"Expected a JSON object: {path}")
    return value


def load_reviewed_papers(analysis_dir: Path) -> tuple[list[dict[str, Any]], list[Path]]:
    """Load and validate the three independently reviewed paper groups."""
    paths = [analysis_dir / name for name in ("group-a.json", "group-b.json", "group-c.json")]
    papers: list[dict[str, Any]] = []
    for path in paths:
        if not path.is_file():
            raise CorpusInputError(f"Reviewed analysis is missing: {path}")
        value = load_json(path)
        group = value.get("papers")
        if not isinstance(group, list) or len(group) != 5:
            raise CorpusInputError(f"Each reviewed group must contain exactly five papers: {path}")
        papers.extend(group)

    ids = [paper.get("paper_id") for paper in papers]
    if len(set(ids)) != 15 or any(not isinstance(item, str) for item in ids):
        raise CorpusInputError("Reviewed analysis must contain fifteen unique paper IDs.")
    for paper in papers:
        claims = paper.get("claims")
        if not isinstance(claims, list) or len(claims) < 12:
            raise CorpusInputError(f"Paper {paper['paper_id']} must contain at least twelve reviewed claims.")
        for claim in claims:
            kind = claim.get("kind")
            statement = claim.get("statement")
            pages = claim.get("evidence_pages")
            if kind not in CLAIM_KINDS:
                raise CorpusInputError(f"Unsupported claim kind {kind!r} in {paper['paper_id']}.")
            if not isinstance(statement, str) or not statement.strip():
                raise CorpusInputError(f"Claim statement is empty in {paper['paper_id']}.")
            if not isinstance(pages, list) or not pages or any(not isinstance(page, int) or page < 1 for page in pages):
                raise CorpusInputError(f"Claim pages are invalid in {paper['paper_id']}.")
        for field in REVIEW_FIELDS:
            items = paper.get(field)
            if not isinstance(items, list) or not items or any(not isinstance(item, str) for item in items):
                raise CorpusInputError(f"Reviewed field {field} is invalid in {paper['paper_id']}.")
            for item in items:
                parse_review_item(item, paper["paper_id"])
    return sorted(papers, key=lambda paper: paper["paper_id"]), paths


def paper_subject(versioned_id: str) -> str:
    """Return the generated Paper subject for one Markdown declaration."""
    source_id = source_id_for_paper(versioned_id, "paper")
    record_id = f"sources/markdown/{versioned_id}"
    return resource_iri(source_id, record_id)


def term_subject(term_id: str) -> str:
    """Return the generated AnalysisTerm subject for a vocabulary row."""
    return resource_iri("analysis-vocabulary", term_id)


def build_terms(reviewed_papers: list[dict[str, Any]]) -> list[dict[str, str]]:
    """Build common dimension terms and paper-specific method terms."""
    terms = [
        {
            "id": f"dimension-{kind}",
            "label": kind.replace("-", " ").title(),
            "term_kind": "analysis-dimension",
            "definition": f"Reviewed source-specific claims about {kind.replace('-', ' ')}.",
        }
        for kind in CLAIM_KINDS
    ]
    for paper in reviewed_papers:
        method_name = str(paper.get("method_name") or paper["title"]).strip()
        terms.append(
            {
                "id": f"method-{paper['paper_id'].replace('.', '-').lower()}",
                "label": method_name,
                "term_kind": "paper-specific-method",
                "definition": (
                    f"Method name used for paper {paper['paper_id']}. It is source-scoped and does not assert "
                    "equivalence with any other paper's method."
                ),
            }
        )
    return sorted(terms, key=lambda item: item["id"])


def evidence_locator(versioned_id: str, pages: list[int]) -> str:
    """Serialize stable input Markdown page anchors for one reviewed claim."""
    unique_pages = sorted(set(pages))
    return ";".join(f"sources/markdown/{versioned_id}.md#PDF-page-{page}" for page in unique_pages)


def parse_review_item(item: str, paper_id: str) -> tuple[str, list[int]]:
    """Split one reviewed list item from its mandatory trailing PDF page citation."""
    match = re.search(r"\s*(?:\(|\[)PDF pp?\.\s*([^\]\)]+)(?:\)|\])\.?\s*$", item)
    if match is None:
        raise CorpusInputError(f"Reviewed item lacks a trailing PDF page citation in {paper_id}: {item!r}")
    page_expression = match.group(1)
    pages: set[int] = set()
    for token in re.split(r"\s*,\s*|\s+and\s+", page_expression):
        token = token.strip()
        if not token:
            continue
        range_match = re.fullmatch(r"(\d+)\s*[-–]\s*(\d+)", token)
        if range_match:
            start, end = (int(value) for value in range_match.groups())
            if end < start:
                raise CorpusInputError(f"Descending page range in {paper_id}: {item!r}")
            pages.update(range(start, end + 1))
        elif token.isdigit():
            pages.add(int(token))
        else:
            raise CorpusInputError(f"Unrecognized page citation in {paper_id}: {item!r}")
    statement = item[: match.start()].strip().rstrip(".") + "."
    if not pages or not statement.strip(". "):
        raise CorpusInputError(f"Reviewed item is empty or ungrounded in {paper_id}: {item!r}")
    return statement, sorted(pages)


def build_claim_rows(
    paper: dict[str, Any], inventory_item: dict[str, Any]
) -> list[dict[str, str]]:
    """Convert one paper review into source-scoped semantic claim rows."""
    versioned_id = paper["paper_id"]
    method_term_id = f"method-{versioned_id.replace('.', '-').lower()}"
    claim_inputs: list[tuple[str, str, list[int], str]] = []
    for field, kind in REVIEW_FIELDS.items():
        for item in paper[field]:
            statement, pages = parse_review_item(item, versioned_id)
            claim_inputs.append((kind, statement, pages, f"review-list:{field}"))
    for claim in paper["claims"]:
        claim_inputs.append(
            (
                claim["kind"],
                " ".join(claim["statement"].split()),
                sorted(set(claim["evidence_pages"])),
                "explicit-review-claim",
            )
        )

    rows: list[dict[str, str]] = []
    seen: set[tuple[str, str, tuple[int, ...]]] = set()
    for kind, statement, pages, origin in claim_inputs:
        identity = (kind, statement.casefold(), tuple(pages))
        if identity in seen:
            continue
        seen.add(identity)
        index = len(rows) + 1
        confidence = "medium" if re.search(r"\b(may|might|suggest|appears|uncertain)\b", statement, re.I) else "high"
        rows.append(
            {
                "id": f"claim-{versioned_id.replace('.', '-').lower()}-{index:03d}",
                "title": f"{versioned_id} {claim['kind']} claim {index:03d}",
                "paper_iri": paper_subject(versioned_id),
                "subject_term_iri": term_subject(method_term_id),
                "object_term_iri": term_subject(f"dimension-{kind}"),
                "claim_kind": kind,
                "claim_origin": origin,
                "evidence_locator": evidence_locator(versioned_id, pages),
                "interpretation": statement,
                "confidence": confidence,
                "review_state": "reviewed",
                "pdf_sha256": inventory_item["pdf_sha256"],
            }
        )
    return rows


def paper_source(paper: dict[str, Any]) -> dict[str, Any]:
    """Build one Markdown source declaration for a paper."""
    versioned_id = paper["paper_id"]
    return {
        "id": source_id_for_paper(versioned_id, "paper"),
        "kind": "markdown",
        "path": f"sources/markdown/{versioned_id}.md",
        "concept_type": "Research Paper",
        "ontology_class": "Paper",
        "fields": {
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
        },
    }


def claim_source(versioned_id: str) -> dict[str, Any]:
    """Build one JSON source declaration for a paper's reviewed claims."""
    return {
        "id": source_id_for_paper(versioned_id, "claims"),
        "kind": "json",
        "path": f"sources/claims/{versioned_id}.jsonl",
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
            "pdf_sha256": "string",
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
            "pdf_sha256": "claimPdfSha256",
        },
    }


def vocabulary_source() -> dict[str, Any]:
    """Build the common analysis-vocabulary source declaration."""
    return {
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


def ontology() -> dict[str, Any]:
    """Return the reviewed ontology declaration for papers, terms, and claims."""
    properties = [
        ("paperTitle", "datatype", "Paper", "xsd:string"),
        ("selectionDimension", "datatype", "Paper", "xsd:string"),
        ("paperId", "datatype", "Paper", "xsd:string"),
        ("arxivId", "datatype", "Paper", "xsd:string"),
        ("arxivVersion", "datatype", "Paper", "xsd:string"),
        ("publicationYear", "datatype", "Paper", "xsd:integer"),
        ("authors", "datatype", "Paper", "xsd:string"),
        ("sourceUrl", "datatype", "Paper", "xsd:string"),
        ("pdfUrl", "datatype", "Paper", "xsd:string"),
        ("pdfSha256", "datatype", "Paper", "xsd:string"),
        ("pageCount", "datatype", "Paper", "xsd:integer"),
        ("extractedCharacters", "datatype", "Paper", "xsd:integer"),
        ("termLabel", "datatype", "AnalysisTerm", "xsd:string"),
        ("termKind", "datatype", "AnalysisTerm", "xsd:string"),
        ("termDefinition", "datatype", "AnalysisTerm", "xsd:string"),
        ("aboutPaper", "object", "PaperSemanticClaim", "Paper"),
        ("subjectTerm", "object", "PaperSemanticClaim", "AnalysisTerm"),
        ("objectTerm", "object", "PaperSemanticClaim", "AnalysisTerm"),
        ("claimKind", "datatype", "PaperSemanticClaim", "xsd:string"),
        ("claimOrigin", "datatype", "PaperSemanticClaim", "xsd:string"),
        ("evidenceLocator", "datatype", "PaperSemanticClaim", "xsd:string"),
        ("interpretation", "datatype", "PaperSemanticClaim", "xsd:string"),
        ("confidence", "datatype", "PaperSemanticClaim", "xsd:string"),
        ("reviewState", "datatype", "PaperSemanticClaim", "xsd:string"),
        ("claimPdfSha256", "datatype", "PaperSemanticClaim", "xsd:string"),
    ]
    return {
        "classes": [
            {"name": "Paper", "label": "research paper"},
            {"name": "AnalysisTerm", "label": "analysis term"},
            {"name": "PaperSemanticClaim", "label": "paper semantic claim"},
        ],
        "properties": [
            {"name": name, "kind": kind, "domain": domain, "range": range_value}
            for name, kind, domain, range_value in properties
        ],
    }


def rule(
    name: str,
    target_class: str,
    path: str,
    message: str,
    *,
    datatype: str | None = None,
    class_name: str | None = None,
    pattern: str | None = None,
) -> dict[str, Any]:
    """Build one required single-valued SHACL rule."""
    value: dict[str, Any] = {
        "name": name,
        "target_class": target_class,
        "path": path,
        "min_count": 1,
        "max_count": 1,
        "message": message,
        "basis": {"kind": "evidence", "references": ["GRAPHRAG-STUDY-1"]},
    }
    if datatype is not None:
        value["datatype"] = datatype
    if class_name is not None:
        value["class"] = class_name
        value["node_kind"] = "IRI"
    if pattern is not None:
        value["pattern"] = pattern
    return value


def rules() -> list[dict[str, Any]]:
    """Return the minimal accepted-data contract for the study."""
    return [
        rule("PaperIdentifierRule", "Paper", "paperId", "Every paper must retain its pinned arXiv version.", datatype="xsd:string", pattern=r"^[0-9]{4}\.[0-9]{5}v[0-9]+$"),
        rule("PaperDigestRule", "Paper", "pdfSha256", "Every paper must retain its accepted PDF digest.", datatype="xsd:string", pattern=r"^[0-9a-f]{64}$"),
        rule("TermLabelRule", "AnalysisTerm", "termLabel", "Every analysis term must have a label.", datatype="xsd:string", pattern=r".+"),
        rule("ClaimPaperRule", "PaperSemanticClaim", "aboutPaper", "Every claim must identify its source paper.", class_name="Paper"),
        rule("ClaimSubjectRule", "PaperSemanticClaim", "subjectTerm", "Every claim must identify its paper-specific method.", class_name="AnalysisTerm"),
        rule("ClaimDimensionRule", "PaperSemanticClaim", "objectTerm", "Every claim must identify one analysis dimension.", class_name="AnalysisTerm"),
        rule("ClaimKindRule", "PaperSemanticClaim", "claimKind", "Every claim must use one reviewed claim kind.", datatype="xsd:string", pattern="^(" + "|".join(CLAIM_KINDS) + ")$"),
        rule("ClaimEvidenceRule", "PaperSemanticClaim", "evidenceLocator", "Every claim must cite one or more PDF pages.", datatype="xsd:string", pattern=r"^sources/markdown/.+#PDF-page-[0-9]+"),
        rule("ClaimInterpretationRule", "PaperSemanticClaim", "interpretation", "Every claim must retain its source-specific interpretation.", datatype="xsd:string", pattern=r".+"),
        rule("ClaimReviewRule", "PaperSemanticClaim", "reviewState", "Every accepted claim must be reviewed.", datatype="xsd:string", pattern=r"^reviewed$"),
    ]


def manifest(reviewed_papers: list[dict[str, Any]]) -> dict[str, Any]:
    """Build the complete closed-schema Semantic OKF manifest."""
    sources: list[dict[str, Any]] = []
    for paper in reviewed_papers:
        sources.append(paper_source(paper))
    sources.append(vocabulary_source())
    for paper in reviewed_papers:
        sources.append(claim_source(paper["paper_id"]))
    return {
        "schema_version": "1.0",
        "bundle": {
            "title": "GraphRAG Cross-Paper Semantic Corpus",
            "description": "Fifteen source-separated GraphRAG papers with reviewed, page-grounded analysis claims.",
            "base_iri": BASE_IRI,
            "ontology_iri": ONTOLOGY_IRI,
            "version_iri": f"{ONTOLOGY_IRI}/1.0.0",
            "prefix": "graphrag",
            "owl_profile": "rl",
        },
        "ontology": ontology(),
        "rules": rules(),
        "sources": sources,
    }


def write_json(path: Path, value: Any) -> None:
    """Write one stable, UTF-8 JSON document."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    """Write stable JSONL rows in caller-provided order."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(canonical_json(row) + "\n" for row in rows), encoding="utf-8")


def build_inputs(root: Path) -> dict[str, Any]:
    """Generate vocabulary, claims, manifest, and the external review ledger."""
    catalog = load_json(root / "papers.json")
    inventory = load_json(root / "sources" / "inventory.json")
    reviewed_papers, review_paths = load_reviewed_papers(root / "analysis")
    catalog_ids = {paper["arxiv_id"] + paper["version"] for paper in catalog["papers"]}
    reviewed_ids = {paper["paper_id"] for paper in reviewed_papers}
    if reviewed_ids != catalog_ids:
        raise CorpusInputError(f"Reviewed IDs differ from catalog IDs: {sorted(catalog_ids ^ reviewed_ids)}")
    inventory_by_id = {item["paper_id"]: item for item in inventory["papers"]}
    if set(inventory_by_id) != catalog_ids:
        raise CorpusInputError("Inventory IDs differ from the pinned catalog.")

    terms = build_terms(reviewed_papers)
    write_jsonl(root / "sources" / "semantic" / "analysis-vocabulary.jsonl", terms)
    claim_counts: Counter[str] = Counter()
    total_claims = 0
    for paper in reviewed_papers:
        rows = build_claim_rows(paper, inventory_by_id[paper["paper_id"]])
        write_jsonl(root / "sources" / "claims" / f"{paper['paper_id']}.jsonl", rows)
        claim_counts.update(row["claim_kind"] for row in rows)
        total_claims += len(rows)

    manifest_value = manifest(reviewed_papers)
    write_json(root / "manifest.json", manifest_value)
    review_ledger = {
        "collection_id": catalog["collection_id"],
        "review_mode": "three-independent-five-paper-groups-with-root-consolidation",
        "paper_count": len(reviewed_papers),
        "claim_count": total_claims,
        "claim_counts_by_kind": dict(sorted(claim_counts.items())),
        "review_inputs": [
            {"path": path.relative_to(root).as_posix(), "sha256": sha256_file(path)} for path in review_paths
        ],
        "catalog_sha256": sha256_file(root / "papers.json"),
        "inventory_sha256": sha256_file(root / "sources" / "inventory.json"),
        "manifest_sha256": sha256_file(root / "manifest.json"),
        "record_fusion": False,
        "automatic_equivalence": False,
    }
    write_json(root / "analysis" / "review-ledger.json", review_ledger)
    return review_ledger


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    return parser


def main() -> int:
    """Generate corpus inputs and print a compact summary."""
    args = build_parser().parse_args()
    ledger = build_inputs(args.root.resolve())
    print(canonical_json({key: ledger[key] for key in ("paper_count", "claim_count", "claim_counts_by_kind")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
