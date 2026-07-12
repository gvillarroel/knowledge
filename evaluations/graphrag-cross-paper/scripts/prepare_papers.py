"""Download, verify, and extract the pinned GraphRAG paper collection."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
import re
import tempfile
import time
from pathlib import Path
from typing import Any

import requests
from pypdf import PdfReader, __version__ as PYPDF_VERSION


DEFAULT_ROOT = Path(__file__).resolve().parents[1]
MIN_EXTRACTED_CHARACTERS = 4_000
USER_AGENT = "knowledge-graphrag-study/1.0 (reproducible academic corpus preparation)"


class PreparationError(RuntimeError):
    """Raised when a pinned source cannot be prepared without data loss."""


def load_catalog(path: Path) -> dict[str, Any]:
    """Load and validate a pinned paper catalog."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    papers = payload.get("papers")
    if not isinstance(papers, list) or len(papers) < 11:
        raise PreparationError("The paper catalog must contain more than ten papers.")

    versioned_ids: set[str] = set()
    for paper in papers:
        if not isinstance(paper, dict):
            raise PreparationError("Every paper entry must be an object.")
        required = {"arxiv_id", "version", "title", "authors", "year", "abs_url", "pdf_url", "pdf_sha256"}
        missing = sorted(required - paper.keys())
        if missing:
            raise PreparationError(f"Paper entry is missing fields: {', '.join(missing)}")
        versioned_id = paper["arxiv_id"] + paper["version"]
        if versioned_id in versioned_ids:
            raise PreparationError(f"Duplicate pinned paper: {versioned_id}")
        if not paper["pdf_url"].endswith(versioned_id):
            raise PreparationError(f"PDF URL is not version-pinned for {versioned_id}")
        if not re.fullmatch(r"[0-9a-f]{64}", str(paper["pdf_sha256"])):
            raise PreparationError(f"PDF SHA-256 is invalid for {versioned_id}")
        versioned_ids.add(versioned_id)
    return payload


def sha256_file(path: Path) -> str:
    """Return the hexadecimal SHA-256 digest of a file."""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def download_pdf(
    session: requests.Session,
    paper: dict[str, Any],
    destination: Path,
    *,
    force: bool = False,
    attempts: int = 4,
) -> None:
    """Download one pinned PDF atomically with bounded retries."""
    if destination.exists() and not force:
        if destination.read_bytes()[:5] == b"%PDF-":
            return
        raise PreparationError(f"Existing file is not a PDF: {destination}")

    destination.parent.mkdir(parents=True, exist_ok=True)
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        temporary_path: Path | None = None
        try:
            with session.get(paper["pdf_url"], stream=True, timeout=(30, 180)) as response:
                response.raise_for_status()
                with tempfile.NamedTemporaryFile(
                    mode="wb", prefix=destination.stem + ".", suffix=".tmp", dir=destination.parent, delete=False
                ) as temporary:
                    temporary_path = Path(temporary.name)
                    for chunk in response.iter_content(chunk_size=1024 * 1024):
                        if chunk:
                            temporary.write(chunk)
            if temporary_path.read_bytes()[:5] != b"%PDF-":
                raise PreparationError(f"Downloaded response is not a PDF: {paper['pdf_url']}")
            os.replace(temporary_path, destination)
            return
        except (OSError, requests.RequestException, PreparationError) as error:
            last_error = error
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)
            if attempt < attempts:
                time.sleep(attempt * 2)
    raise PreparationError(f"Failed to download {paper['pdf_url']}: {last_error}")


def normalize_page_text(text: str) -> str:
    """Normalize extractor whitespace while preserving paragraph boundaries."""
    text = text.replace("\x00", "").replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def yaml_string(value: object) -> str:
    """Serialize a scalar as a JSON string, which is also valid YAML."""
    return json.dumps(str(value), ensure_ascii=False)


def display_path(path: Path, root: Path) -> str:
    """Return a stable root-relative path when possible."""
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def extract_pdf(
    paper: dict[str, Any], pdf_path: Path, markdown_path: Path, *, inventory_root: Path
) -> dict[str, Any]:
    """Extract a PDF into one page-addressable Markdown source document."""
    try:
        reader = PdfReader(pdf_path)
    except Exception as error:  # pypdf exposes several parser-specific exceptions
        raise PreparationError(f"Cannot parse {pdf_path}: {error}") from error

    pages: list[str] = []
    for index, page in enumerate(reader.pages, start=1):
        try:
            extracted = normalize_page_text(page.extract_text() or "")
        except Exception as error:
            raise PreparationError(f"Cannot extract page {index} from {pdf_path}: {error}") from error
        pages.append(f"## PDF page {index}\n\n{extracted or '[No extractable text on this page.]'}")

    extracted_characters = sum(len(page) for page in pages)
    if extracted_characters < MIN_EXTRACTED_CHARACTERS:
        raise PreparationError(
            f"Extraction from {pdf_path} produced only {extracted_characters} characters; expected at least "
            f"{MIN_EXTRACTED_CHARACTERS}."
        )

    versioned_id = paper["arxiv_id"] + paper["version"]
    digest = sha256_file(pdf_path)
    frontmatter = [
        "---",
        f"title: {yaml_string(paper['title'])}",
        f"description: {yaml_string(paper['selection_dimension'])}",
        'type: "Paper"',
        f"resource: {yaml_string(paper['abs_url'])}",
        'tags: "graphrag; research-paper; cross-paper-study"',
        f"paper_id: {yaml_string(versioned_id)}",
        f"arxiv_id: {yaml_string(paper['arxiv_id'])}",
        f"arxiv_version: {yaml_string(paper['version'])}",
        f"publication_year: {paper['year']}",
        f"authors: {yaml_string('; '.join(paper['authors']))}",
        f"source_url: {yaml_string(paper['abs_url'])}",
        f"pdf_url: {yaml_string(paper['pdf_url'])}",
        f"pdf_sha256: {yaml_string(digest)}",
        f"page_count: {len(reader.pages)}",
        f"extracted_characters: {extracted_characters}",
        "---",
        "",
        f"# {paper['title']}",
        "",
        "## Source citation",
        "",
        f"- Pinned arXiv record: [{versioned_id}]({paper['abs_url']})",
        f"- Authors: {'; '.join(paper['authors'])}",
        f"- PDF: [{paper['pdf_url']}]({paper['pdf_url']})",
        f"- PDF SHA-256: `{digest}`",
        f"- Extracted pages: {len(reader.pages)}",
        "",
        "The following text was extracted page by page from the pinned PDF. Page headings are stable evidence locators.",
        "",
    ]
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.write_text("\n".join(frontmatter + pages).rstrip() + "\n", encoding="utf-8")
    return {
        "paper_id": versioned_id,
        "title": paper["title"],
        "pdf_path": display_path(pdf_path, inventory_root),
        "markdown_path": display_path(markdown_path, inventory_root),
        "pdf_sha256": digest,
        "markdown_sha256": sha256_file(markdown_path),
        "pdf_bytes": pdf_path.stat().st_size,
        "page_count": len(reader.pages),
        "extracted_characters": extracted_characters,
        "retrieved_at": datetime.fromtimestamp(pdf_path.stat().st_mtime, timezone.utc).isoformat(),
        "extractor": {"name": "pypdf", "version": PYPDF_VERSION},
    }


def prepare_collection(
    catalog_path: Path,
    pdf_dir: Path,
    markdown_dir: Path,
    inventory_path: Path,
    *,
    force_download: bool = False,
) -> dict[str, Any]:
    """Download and extract every paper in a catalog, then write a stable inventory."""
    catalog = load_catalog(catalog_path)
    inventory_root = catalog_path.parent
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT, "Accept": "application/pdf"})
    inventory: list[dict[str, Any]] = []
    for paper in catalog["papers"]:
        versioned_id = paper["arxiv_id"] + paper["version"]
        pdf_path = pdf_dir / f"{versioned_id}.pdf"
        markdown_path = markdown_dir / f"{versioned_id}.md"
        download_pdf(session, paper, pdf_path, force=force_download)
        actual_digest = sha256_file(pdf_path)
        if actual_digest != paper["pdf_sha256"]:
            raise PreparationError(
                f"Pinned PDF digest mismatch for {versioned_id}: expected {paper['pdf_sha256']}, got {actual_digest}."
            )
        inventory.append(extract_pdf(paper, pdf_path, markdown_path, inventory_root=inventory_root))

    payload = {
        "collection_id": catalog["collection_id"],
        "catalog_sha256": sha256_file(catalog_path),
        "paper_count": len(inventory),
        "total_pdf_bytes": sum(item["pdf_bytes"] for item in inventory),
        "total_pages": sum(item["page_count"] for item in inventory),
        "total_extracted_characters": sum(item["extracted_characters"] for item in inventory),
        "papers": inventory,
    }
    inventory_path.parent.mkdir(parents=True, exist_ok=True)
    inventory_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload


def check_collection(catalog_path: Path, pdf_dir: Path, markdown_dir: Path, inventory_path: Path) -> dict[str, Any]:
    """Re-extract every pinned PDF in isolation and verify all recorded digests."""
    catalog = load_catalog(catalog_path)
    if not inventory_path.is_file():
        raise PreparationError(f"Inventory does not exist: {inventory_path}")
    recorded = json.loads(inventory_path.read_text(encoding="utf-8"))
    recorded_by_id = {item["paper_id"]: item for item in recorded.get("papers", [])}
    if recorded.get("paper_count") != len(catalog["papers"]):
        raise PreparationError("Inventory paper count does not match the catalog.")

    verified: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="graphrag-paper-check-") as temporary:
        temporary_root = Path(temporary)
        for paper in catalog["papers"]:
            versioned_id = paper["arxiv_id"] + paper["version"]
            pdf_path = pdf_dir / f"{versioned_id}.pdf"
            markdown_path = markdown_dir / f"{versioned_id}.md"
            if not pdf_path.is_file() or not markdown_path.is_file():
                raise PreparationError(f"Prepared artifacts are missing for {versioned_id}.")
            if sha256_file(pdf_path) != paper["pdf_sha256"]:
                raise PreparationError(f"Pinned PDF digest mismatch for {versioned_id}.")
            item = recorded_by_id.get(versioned_id)
            if item is None:
                raise PreparationError(f"Inventory record is missing for {versioned_id}.")
            if sha256_file(markdown_path) != item.get("markdown_sha256"):
                raise PreparationError(f"Markdown digest mismatch for {versioned_id}.")
            regenerated_path = temporary_root / f"{versioned_id}.md"
            regenerated = extract_pdf(paper, pdf_path, regenerated_path, inventory_root=catalog_path.parent)
            if regenerated["markdown_sha256"] != item.get("markdown_sha256"):
                raise PreparationError(f"Re-extraction drift detected for {versioned_id}.")
            verified.append({"paper_id": versioned_id, "status": "pass"})
    return {"collection_id": catalog["collection_id"], "paper_count": len(verified), "status": "pass"}


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_ROOT / "papers.json")
    parser.add_argument("--pdf-dir", type=Path, default=DEFAULT_ROOT / "sources" / "pdfs")
    parser.add_argument("--markdown-dir", type=Path, default=DEFAULT_ROOT / "sources" / "markdown")
    parser.add_argument("--inventory", type=Path, default=DEFAULT_ROOT / "sources" / "inventory.json")
    parser.add_argument("--force-download", action="store_true")
    parser.add_argument("--check", action="store_true", help="Verify pinned PDFs and deterministic re-extraction.")
    return parser


def main() -> int:
    """Run collection preparation and print a compact machine-readable summary."""
    args = build_parser().parse_args()
    if args.check:
        payload = check_collection(
            args.catalog.resolve(), args.pdf_dir.resolve(), args.markdown_dir.resolve(), args.inventory.resolve()
        )
        print(json.dumps(payload, sort_keys=True))
        return 0
    payload = prepare_collection(
        args.catalog.resolve(), args.pdf_dir.resolve(), args.markdown_dir.resolve(), args.inventory.resolve(),
        force_download=args.force_download,
    )
    print(
        json.dumps(
            {
                "collection_id": payload["collection_id"],
                "paper_count": payload["paper_count"],
                "total_pages": payload["total_pages"],
                "total_extracted_characters": payload["total_extracted_characters"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
