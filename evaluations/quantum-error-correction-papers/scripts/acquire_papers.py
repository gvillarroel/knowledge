#!/usr/bin/env python3
"""Acquire and deterministically verify the pinned arXiv QEC paper corpus."""

from __future__ import annotations

import argparse
from html.parser import HTMLParser
from io import BytesIO
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import tempfile
from typing import Any, Mapping, Sequence
import unicodedata

import pypdf
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


ROOT = Path(__file__).resolve().parents[1]
SELECTION_PATH = ROOT / "paper-selection.json"
SOURCES_PATH = ROOT / "sources"
ABS_URL = "https://arxiv.org/abs/{paper_id}"
USER_AGENT = "knowledge-semantic-okf-evaluation/1.0"
ARXIV_ID_RE = re.compile(r"^(\d{4})\.(\d{4,5})(v\d+)$")


class AcquisitionError(ValueError):
    """Raised when the pinned corpus cannot be reproduced exactly."""


class _CitationMetadataParser(HTMLParser):
    """Collect scholarly citation metadata from an official arXiv abstract page."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.values: dict[str, list[str]] = {}

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        if tag != "meta":
            return
        attributes = dict(attrs)
        name = attributes.get("name")
        content = attributes.get("content")
        if (
            isinstance(name, str)
            and name.startswith("citation_")
            and isinstance(content, str)
        ):
            self.values.setdefault(name, []).append(" ".join(content.split()))


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


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


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _load_selection() -> dict[str, Any]:
    value = json.loads(SELECTION_PATH.read_text(encoding="utf-8"))
    papers = value.get("papers") if isinstance(value, dict) else None
    if (
        value.get("schema_version") != "arxiv-paper-selection/1.0"
        or value.get("dataset_id") != "quantum-error-correction-papers-40"
        or not isinstance(papers, list)
        or len(papers) != 15
    ):
        raise AcquisitionError("Paper selection contract is invalid")
    ids: list[str] = []
    for index, paper in enumerate(papers):
        if not isinstance(paper, dict) or set(paper) != {
            "arxiv_id",
            "expected_title",
            "selection_dimension",
        }:
            raise AcquisitionError(f"Paper selection row {index} is invalid")
        paper_id = paper["arxiv_id"]
        if (
            not isinstance(paper_id, str)
            or ARXIV_ID_RE.fullmatch(paper_id) is None
            or not isinstance(paper["expected_title"], str)
            or not isinstance(paper["selection_dimension"], str)
        ):
            raise AcquisitionError(f"Paper selection row {index} is incomplete")
        ids.append(paper_id)
    if ids != sorted(set(ids)):
        raise AcquisitionError("Paper selection IDs must be sorted and unique")
    return value


def _fetch_metadata(
    session: requests.Session,
    selection: Mapping[str, Any],
) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for row in selection["papers"]:
        identity = row["arxiv_id"]
        abs_url = ABS_URL.format(paper_id=identity)
        response = session.get(abs_url, timeout=(15, 90))
        response.raise_for_status()
        parser = _CitationMetadataParser()
        parser.feed(response.text)
        values = parser.values

        def one(name: str) -> str:
            candidates = values.get(name, [])
            if len(candidates) != 1 or not candidates[0]:
                raise AcquisitionError(
                    f"arXiv page {identity} has invalid {name!r} metadata"
                )
            return candidates[0]

        unversioned = identity.split("v", 1)[0]
        if one("citation_arxiv_id") != unversioned:
            raise AcquisitionError(f"arXiv abstract identity drift: {identity}")
        title = one("citation_title")
        if title.casefold() != row["expected_title"].casefold():
            raise AcquisitionError(f"Title drift for {identity}: {title!r}")
        publication_date = one("citation_date").replace("/", "-")
        online_date = one("citation_online_date").replace("/", "-")
        primary_match = re.search(
            r'class="primary-subject"[^>]*>[^<]*\(([^()]+)\)',
            response.text,
        )
        primary_category = primary_match.group(1) if primary_match else "quant-ph"
        result[identity] = {
            "arxiv_id": identity,
            "title": title,
            "abstract": one("citation_abstract"),
            "authors": values.get("citation_author", []),
            "published": f"{publication_date}T00:00:00Z",
            "updated": f"{online_date}T00:00:00Z",
            "primary_category": primary_category,
            "categories": [primary_category],
            "abs_url": abs_url,
            "pdf_url": f"https://arxiv.org/pdf/{identity}",
        }
    return result


def _normalize_page_text(value: str) -> str:
    return unicodedata.normalize(
        "NFC",
        value.replace("\x00", "")
        .replace("\r\n", "\n")
        .replace("\r", "\n"),
    ).rstrip()


def _render_markdown(
    metadata: Mapping[str, Any],
    selection: Mapping[str, Any],
    pdf_bytes: bytes,
) -> tuple[str, int, int]:
    try:
        reader = pypdf.PdfReader(BytesIO(pdf_bytes))
    except Exception as exc:
        raise AcquisitionError(
            f"Cannot parse {metadata['arxiv_id']} PDF: {exc}"
        ) from exc
    pages: list[str] = []
    for page_number, page in enumerate(reader.pages, start=1):
        try:
            text = _normalize_page_text(page.extract_text() or "")
        except Exception as exc:
            raise AcquisitionError(
                f"Cannot extract {metadata['arxiv_id']} page {page_number}: {exc}"
            ) from exc
        pages.append(f"## PDF page {page_number}\n\n{text}\n")
    extracted = "\n".join(pages)
    pdf_sha256 = _sha256_bytes(pdf_bytes)
    paper_id = metadata["arxiv_id"]
    match = ARXIV_ID_RE.fullmatch(paper_id)
    if match is None:
        raise AcquisitionError(f"Invalid versioned arXiv identity: {paper_id}")
    publication_year = int(metadata["published"][:4])
    authors = "; ".join(metadata["authors"])
    tags = "quantum-error-correction; research-paper; arxiv"
    frontmatter = {
        "title": metadata["title"],
        "description": selection["selection_dimension"],
        "type": "Paper",
        "resource": metadata["abs_url"],
        "tags": tags,
        "paper_id": paper_id,
        "arxiv_id": f"{match.group(1)}.{match.group(2)}",
        "arxiv_version": match.group(3),
        "publication_year": publication_year,
        "authors": authors,
        "primary_category": metadata["primary_category"],
        "abstract": metadata["abstract"],
        "source_url": metadata["abs_url"],
        "pdf_url": metadata["pdf_url"],
        "pdf_sha256": pdf_sha256,
        "page_count": len(pages),
        "extracted_characters": len(extracted),
    }
    yaml_lines = ["---"]
    for key, value in frontmatter.items():
        if isinstance(value, int):
            rendered = str(value)
        else:
            rendered = json.dumps(value, ensure_ascii=False)
        yaml_lines.append(f"{key}: {rendered}")
    yaml_lines.extend(
        [
            "---",
            "",
            f"# {metadata['title']}",
            "",
            "## Source citation",
            "",
            f"- Pinned arXiv record: [{paper_id}]({metadata['abs_url']})",
            f"- Authors: {authors}",
            f"- PDF: [{metadata['pdf_url']}]({metadata['pdf_url']})",
            f"- PDF SHA-256: `{pdf_sha256}`",
            f"- Extracted pages: {len(pages)}",
            "",
            (
                "The following text was extracted page by page from the pinned "
                "PDF. Page headings are stable evidence locators."
            ),
            "",
            extracted.rstrip(),
            "",
        ]
    )
    return "\n".join(yaml_lines), len(pages), len(extracted)


def _regular_tree(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): _sha256_file(path)
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def _materialize(
    candidate: Path,
    selection: Mapping[str, Any],
    *,
    reuse_pdfs: Path | None,
) -> dict[str, Any]:
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})
    session.mount(
        "https://",
        HTTPAdapter(
            max_retries=Retry(
                total=5,
                connect=5,
                read=5,
                status=5,
                backoff_factor=1.0,
                status_forcelist=(429, 500, 502, 503, 504),
                allowed_methods=frozenset({"GET"}),
                respect_retry_after_header=True,
            )
        ),
    )
    metadata = _fetch_metadata(session, selection)
    inventory_rows: list[dict[str, Any]] = []
    normalized_metadata: list[dict[str, Any]] = []
    for selected in selection["papers"]:
        paper_id = selected["arxiv_id"]
        entry = metadata[paper_id]
        if reuse_pdfs is None:
            response = session.get(entry["pdf_url"], timeout=(15, 240))
            response.raise_for_status()
            pdf_bytes = response.content
            if not pdf_bytes.startswith(b"%PDF"):
                raise AcquisitionError(f"arXiv PDF response is invalid: {paper_id}")
        else:
            local_pdf = reuse_pdfs / "pdfs" / f"{paper_id}.pdf"
            if not local_pdf.is_file():
                raise AcquisitionError(f"Pinned local PDF is absent: {local_pdf}")
            pdf_bytes = local_pdf.read_bytes()
        markdown, page_count, character_count = _render_markdown(
            entry,
            selected,
            pdf_bytes,
        )
        pdf_path = candidate / "pdfs" / f"{paper_id}.pdf"
        markdown_path = candidate / "markdown" / f"{paper_id}.md"
        pdf_path.parent.mkdir(parents=True, exist_ok=True)
        pdf_path.write_bytes(pdf_bytes)
        _write_text(markdown_path, markdown)
        inventory_rows.append(
            {
                "arxiv_id": paper_id,
                "pdf_path": pdf_path.relative_to(candidate).as_posix(),
                "pdf_sha256": _sha256_file(pdf_path),
                "markdown_path": markdown_path.relative_to(candidate).as_posix(),
                "markdown_sha256": _sha256_file(markdown_path),
                "page_count": page_count,
                "extracted_characters": character_count,
            }
        )
        normalized_metadata.append(entry)
    _write_text(
        candidate / "metadata.json",
        _canonical_json(
            {
                "schema_version": "arxiv-normalized-metadata/1.0",
                "dataset_id": selection["dataset_id"],
                "papers": normalized_metadata,
            }
        ),
    )
    inventory = {
        "schema_version": "arxiv-pdf-corpus-inventory/1.0",
        "dataset_id": selection["dataset_id"],
        "selection_sha256": _sha256_file(SELECTION_PATH),
        "metadata_endpoint": "https://arxiv.org/abs/{versioned-arxiv-id}",
        "extractor": {
            "implementation": "pypdf",
            "version": pypdf.__version__,
            "page_locator": "PDF page N",
        },
        "paper_count": len(inventory_rows),
        "papers": inventory_rows,
    }
    _write_text(candidate / "inventory.json", _canonical_json(inventory))
    return inventory


def build_parser() -> argparse.ArgumentParser:
    """Build the corpus acquisition command line."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help=(
            "Verify API metadata, local PDF hashes, and deterministic Markdown "
            "regeneration without changing the accepted corpus"
        ),
    )
    parser.add_argument(
        "--refresh",
        action="store_true",
        help=(
            "Rebuild deterministic metadata and Markdown from the accepted "
            "local PDFs, then atomically replace the source tree"
        ),
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Acquire or check the pinned QEC paper corpus."""

    args = build_parser().parse_args(argv)
    if args.check and args.refresh:
        raise SystemExit("--check and --refresh are mutually exclusive")
    temporary = Path(
        tempfile.mkdtemp(prefix=".qec-sources-", dir=ROOT)
    )
    candidate = temporary / "sources"
    candidate.mkdir()
    try:
        selection = _load_selection()
        if args.check:
            if not SOURCES_PATH.is_dir():
                raise AcquisitionError("--check requires an acquired sources tree")
            inventory = _materialize(
                candidate,
                selection,
                reuse_pdfs=SOURCES_PATH,
            )
            expected = _regular_tree(SOURCES_PATH)
            actual = _regular_tree(candidate)
            if expected != actual:
                changed = sorted(
                    path
                    for path in set(expected) | set(actual)
                    if expected.get(path) != actual.get(path)
                )
                raise AcquisitionError(
                    f"Acquired source tree is not reproducible: {changed!r}"
                )
            status = "pass"
        elif args.refresh:
            if not SOURCES_PATH.is_dir():
                raise AcquisitionError("--refresh requires an acquired sources tree")
            inventory = _materialize(
                candidate,
                selection,
                reuse_pdfs=SOURCES_PATH,
            )
            previous = temporary / "previous-sources"
            os.replace(SOURCES_PATH, previous)
            try:
                os.replace(candidate, SOURCES_PATH)
            except OSError:
                os.replace(previous, SOURCES_PATH)
                raise
            status = "refreshed"
        else:
            if SOURCES_PATH.exists() or SOURCES_PATH.is_symlink():
                raise AcquisitionError(f"Sources already exist: {SOURCES_PATH}")
            inventory = _materialize(candidate, selection, reuse_pdfs=None)
            os.replace(candidate, SOURCES_PATH)
            status = "created"
        result = {
            "status": status,
            "dataset_id": selection["dataset_id"],
            "paper_count": inventory["paper_count"],
            "selection_sha256": inventory["selection_sha256"],
            "source_file_count": len(_regular_tree(SOURCES_PATH)),
            "source_tree": _regular_tree(SOURCES_PATH),
        }
    except (
        AcquisitionError,
        OSError,
        UnicodeError,
        json.JSONDecodeError,
        requests.RequestException,
    ) as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, sort_keys=True))
        return 2
    finally:
        shutil.rmtree(temporary, ignore_errors=True)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
