#!/usr/bin/env python3
"""Validate private PDFs and build a deterministic page-addressable corpus."""

from __future__ import annotations

import argparse
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


ROOT = Path(__file__).resolve().parents[1]
SELECTION_PATH = ROOT / "book-selection.json"
DEFAULT_INPUT = ROOT / "raw" / "pdfs"
DEFAULT_OUTPUT = ROOT / "processed" / "sources"
DATASET_ID = "software-architecture-books-40"
WATERMARK_RE = re.compile(
    r"(?m)^[ \t]*Humble Bundle Pearson Software Development[ \t]*"
    r"[–-][ \t]*© Pearson\.[ \t]*Do Not Distribute\.[ \t]*$"
)


class CorpusError(ValueError):
    """Raised when the private corpus does not match its frozen contract."""


def sha256_bytes(value: bytes) -> str:
    """Return a lowercase SHA-256 for bytes."""

    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    """Return a lowercase SHA-256 for one regular file."""

    return sha256_bytes(path.read_bytes())


def canonical_json(value: Any) -> str:
    """Serialize one stable, human-readable JSON document."""

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


def write_text(path: Path, text: str) -> None:
    """Write UTF-8 text with LF line endings."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def normalized_words(value: str) -> str:
    """Normalize metadata for conservative prefix and equality checks."""

    return " ".join(unicodedata.normalize("NFC", value).split()).casefold()


def normalize_page_text(value: str) -> str:
    """Normalize extracted text and remove only the known distribution watermark."""

    normalized = unicodedata.normalize(
        "NFC",
        value.replace("\x00", "")
        .replace("\r\n", "\n")
        .replace("\r", "\n"),
    )
    return WATERMARK_RE.sub("", normalized).strip()


def load_selection(path: Path = SELECTION_PATH) -> dict[str, Any]:
    """Load and validate the closed private-book selection contract."""

    value = json.loads(path.read_text(encoding="utf-8"))
    books = value.get("books") if isinstance(value, dict) else None
    if (
        value.get("schema_version") != "private-book-selection/1.0"
        or value.get("dataset_id") != DATASET_ID
        or value.get("corpus_policy") != "local-private-do-not-redistribute"
        or value.get("document_count") != 18
        or not isinstance(books, list)
        or len(books) != 18
    ):
        raise CorpusError("Book selection contract is invalid")
    expected_keys = {
        "author",
        "expected_bytes",
        "expected_pages",
        "expected_title",
        "filename",
        "pdf_sha256",
        "selection_dimension",
        "slug",
    }
    slugs: list[str] = []
    filenames: list[str] = []
    for index, book in enumerate(books):
        if not isinstance(book, dict) or set(book) != expected_keys:
            raise CorpusError(f"Book selection row {index} has invalid fields")
        text_fields = (
            "author",
            "expected_title",
            "filename",
            "selection_dimension",
            "slug",
        )
        if any(
            not isinstance(book.get(field), str) or not book[field].strip()
            for field in text_fields
        ):
            raise CorpusError(f"Book selection row {index} has an empty field")
        if (
            not isinstance(book["expected_bytes"], int)
            or book["expected_bytes"] <= 0
            or not isinstance(book["expected_pages"], int)
            or book["expected_pages"] <= 0
            or not re.fullmatch(r"[0-9a-f]{64}", book["pdf_sha256"])
            or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", book["slug"])
            or Path(book["filename"]).name != book["filename"]
            or not book["filename"].casefold().endswith(".pdf")
        ):
            raise CorpusError(f"Book selection row {index} is incomplete")
        slugs.append(book["slug"])
        filenames.append(book["filename"])
    if slugs != sorted(set(slugs)):
        raise CorpusError("Book slugs must be sorted and unique")
    if len(filenames) != len(set(filenames)):
        raise CorpusError("Book filenames must be unique")
    return value


def validate_local_path(path: Path, label: str) -> Path:
    """Resolve one local path while keeping private artifacts inside this study."""

    resolved = path.resolve()
    if not resolved.is_relative_to(ROOT):
        raise CorpusError(f"{label} must stay inside {ROOT}")
    return resolved


def pdf_metadata(reader: pypdf.PdfReader) -> tuple[str, str]:
    """Return normalized title and author metadata."""

    metadata = reader.metadata
    title = metadata.title if metadata and isinstance(metadata.title, str) else ""
    author = metadata.author if metadata and isinstance(metadata.author, str) else ""
    return " ".join(title.split()), " ".join(author.split())


def render_markdown(
    book: Mapping[str, Any],
    pdf_bytes: bytes,
) -> tuple[str, dict[str, Any]]:
    """Validate one PDF and render deterministic per-page Markdown."""

    if not pdf_bytes.startswith(b"%PDF"):
        raise CorpusError(f"{book['filename']}: missing PDF signature")
    if len(pdf_bytes) != book["expected_bytes"]:
        raise CorpusError(
            f"{book['filename']}: byte count drift "
            f"({len(pdf_bytes)} != {book['expected_bytes']})"
        )
    pdf_sha256 = sha256_bytes(pdf_bytes)
    if pdf_sha256 != book["pdf_sha256"]:
        raise CorpusError(f"{book['filename']}: PDF SHA-256 drift")
    try:
        reader = pypdf.PdfReader(BytesIO(pdf_bytes))
        encrypted = bool(reader.is_encrypted)
        decryption_result = reader.decrypt("") if encrypted else 0
        if encrypted and decryption_result == 0:
            raise CorpusError(f"{book['filename']}: empty-password decryption failed")
    except CorpusError:
        raise
    except Exception as exc:
        raise CorpusError(f"{book['filename']}: cannot parse PDF: {exc}") from exc
    if len(reader.pages) != book["expected_pages"]:
        raise CorpusError(
            f"{book['filename']}: page count drift "
            f"({len(reader.pages)} != {book['expected_pages']})"
        )
    metadata_title, metadata_author = pdf_metadata(reader)
    if not normalized_words(metadata_title).startswith(
        normalized_words(book["expected_title"])
    ):
        raise CorpusError(
            f"{book['filename']}: title metadata drift ({metadata_title!r})"
        )
    if normalized_words(metadata_author) != normalized_words(book["author"]):
        raise CorpusError(
            f"{book['filename']}: author metadata drift ({metadata_author!r})"
        )

    pages: list[str] = []
    blank_pages: list[int] = []
    extracted_characters = 0
    for page_number, page in enumerate(reader.pages, start=1):
        try:
            text = normalize_page_text(page.extract_text() or "")
        except Exception as exc:
            raise CorpusError(
                f"{book['filename']}: cannot extract page {page_number}: {exc}"
            ) from exc
        if not text:
            blank_pages.append(page_number)
        extracted_characters += len(text)
        pages.append(f"## PDF page {page_number}\n\n{text}\n")
    if extracted_characters < 100_000:
        raise CorpusError(
            f"{book['filename']}: suspiciously short extraction "
            f"({extracted_characters} characters)"
        )
    if len(blank_pages) > max(5, len(pages) // 20):
        raise CorpusError(
            f"{book['filename']}: too many blank extracted pages ({blank_pages!r})"
        )

    frontmatter = {
        "title": book["expected_title"],
        "description": book["selection_dimension"],
        "type": "Software Architecture Book",
        "tags": "software-architecture; software-engineering; private-corpus",
        "document_id": book["slug"],
        "author": book["author"],
        "page_count": len(pages),
        "pdf_sha256": pdf_sha256,
        "extracted_characters": extracted_characters,
        "source_policy": "local-private-do-not-redistribute",
    }
    yaml_lines = ["---"]
    for key, value in frontmatter.items():
        rendered = str(value) if isinstance(value, int) else json.dumps(
            value,
            ensure_ascii=False,
        )
        yaml_lines.append(f"{key}: {rendered}")
    yaml_lines.extend(
        [
            "---",
            "",
            f"# {book['expected_title']}",
            "",
            "## Corpus provenance",
            "",
            f"- Author: {book['author']}",
            f"- Stable document ID: `{book['slug']}`",
            f"- PDF SHA-256: `{pdf_sha256}`",
            f"- Extracted pages: {len(pages)}",
            (
                "- Processing: page-order text extraction with NFC and LF "
                "normalization; the repeated distribution watermark is removed."
            ),
            "",
            (
                "The following private text was extracted page by page. PDF page "
                "headings are stable evidence locators."
            ),
            "",
            "\n".join(pages).rstrip(),
            "",
        ]
    )
    details = {
        "author": book["author"],
        "blank_pages_after_watermark_removal": blank_pages,
        "document_id": book["slug"],
        "encrypted": encrypted,
        "extracted_characters": extracted_characters,
        "filename": book["filename"],
        "metadata_author": metadata_author,
        "metadata_title": metadata_title,
        "page_count": len(pages),
        "pdf_bytes": len(pdf_bytes),
        "pdf_sha256": pdf_sha256,
        "title": book["expected_title"],
    }
    return "\n".join(yaml_lines), details


def regular_tree(root: Path) -> dict[str, str]:
    """Hash every regular file in a derived corpus tree."""

    if root.is_symlink():
        raise CorpusError(f"Derived tree must not be a symlink: {root}")
    tree: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise CorpusError(f"Derived tree contains a symlink: {path}")
        if path.is_file():
            tree[path.relative_to(root).as_posix()] = sha256_file(path)
    return tree


def materialize(
    candidate: Path,
    selection: Mapping[str, Any],
    input_dir: Path,
) -> dict[str, Any]:
    """Build one candidate corpus from the exact frozen local PDFs."""

    if not input_dir.is_dir() or input_dir.is_symlink():
        raise CorpusError(f"Private PDF directory is absent or unsafe: {input_dir}")
    observed = sorted(
        path.name
        for path in input_dir.iterdir()
        if path.is_file() and not path.is_symlink()
    )
    expected = sorted(book["filename"] for book in selection["books"])
    if observed != expected:
        raise CorpusError(
            "Private PDF inventory drift: "
            f"missing={sorted(set(expected) - set(observed))!r}, "
            f"extra={sorted(set(observed) - set(expected))!r}"
        )

    inventory_rows: list[dict[str, Any]] = []
    for book in selection["books"]:
        pdf_path = input_dir / book["filename"]
        if not pdf_path.is_file() or pdf_path.is_symlink():
            raise CorpusError(f"Private PDF is absent or unsafe: {pdf_path}")
        markdown, details = render_markdown(book, pdf_path.read_bytes())
        markdown_path = candidate / "markdown" / f"{book['slug']}.md"
        write_text(markdown_path, markdown)
        details["markdown_path"] = markdown_path.relative_to(candidate).as_posix()
        details["markdown_sha256"] = sha256_file(markdown_path)
        details["raw_pdf_path"] = (
            Path("raw") / "pdfs" / book["filename"]
        ).as_posix()
        inventory_rows.append(details)

    inventory = {
        "schema_version": "private-book-corpus-inventory/1.0",
        "dataset_id": DATASET_ID,
        "corpus_policy": selection["corpus_policy"],
        "selection_sha256": sha256_file(SELECTION_PATH),
        "extractor": {
            "implementation": "pypdf",
            "version": pypdf.__version__,
            "page_locator": "PDF page N",
            "normalization": "NFC-LF-and-known-watermark-removal-v1",
        },
        "document_count": len(inventory_rows),
        "page_count": sum(row["page_count"] for row in inventory_rows),
        "extracted_characters": sum(
            row["extracted_characters"] for row in inventory_rows
        ),
        "documents": inventory_rows,
    }
    write_text(candidate / "inventory.json", canonical_json(inventory))
    write_text(
        candidate / "metadata.json",
        canonical_json(
            {
                "schema_version": "private-book-metadata/1.0",
                "dataset_id": DATASET_ID,
                "documents": [
                    {
                        key: row[key]
                        for key in (
                            "author",
                            "document_id",
                            "metadata_author",
                            "metadata_title",
                            "page_count",
                            "title",
                        )
                    }
                    for row in inventory_rows
                ],
            }
        ),
    )
    return inventory


def build_parser() -> argparse.ArgumentParser:
    """Build the deterministic corpus preparation command line."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=DEFAULT_INPUT,
        help="Private input directory containing exactly the frozen PDFs.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Derived corpus directory; it must remain inside this study.",
    )
    operation = parser.add_mutually_exclusive_group()
    operation.add_argument(
        "--check",
        action="store_true",
        help="Regenerate and byte-compare without changing the accepted corpus.",
    )
    operation.add_argument(
        "--refresh",
        action="store_true",
        help="Atomically replace an existing derived corpus from the frozen PDFs.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Prepare or verify the private book corpus."""

    args = build_parser().parse_args(argv)
    try:
        input_dir = validate_local_path(args.input_dir, "input directory")
        output_dir = validate_local_path(args.output_dir, "output directory")
        output_dir.parent.mkdir(parents=True, exist_ok=True)
        temporary = Path(
            tempfile.mkdtemp(prefix=".software-books-", dir=output_dir.parent)
        )
        candidate = temporary / "sources"
        candidate.mkdir()
        try:
            selection = load_selection()
            inventory = materialize(candidate, selection, input_dir)
            if args.check:
                if not output_dir.is_dir():
                    raise CorpusError("--check requires an existing derived corpus")
                expected_tree = regular_tree(output_dir)
                actual_tree = regular_tree(candidate)
                if expected_tree != actual_tree:
                    changed = sorted(
                        path
                        for path in set(expected_tree) | set(actual_tree)
                        if expected_tree.get(path) != actual_tree.get(path)
                    )
                    raise CorpusError(
                        f"Derived corpus is not reproducible: {changed!r}"
                    )
                status = "pass"
            elif args.refresh:
                if not output_dir.is_dir() or output_dir.is_symlink():
                    raise CorpusError(
                        "--refresh requires an existing regular derived corpus"
                    )
                previous = temporary / "previous-sources"
                os.replace(output_dir, previous)
                try:
                    os.replace(candidate, output_dir)
                except OSError:
                    os.replace(previous, output_dir)
                    raise
                status = "refreshed"
            else:
                if output_dir.exists() or output_dir.is_symlink():
                    raise CorpusError(
                        f"Derived corpus already exists: {output_dir}"
                    )
                os.replace(candidate, output_dir)
                status = "created"
            result = {
                "status": status,
                "dataset_id": DATASET_ID,
                "document_count": inventory["document_count"],
                "page_count": inventory["page_count"],
                "extracted_characters": inventory["extracted_characters"],
                "selection_sha256": inventory["selection_sha256"],
                "source_tree": regular_tree(output_dir),
            }
        finally:
            shutil.rmtree(temporary, ignore_errors=True)
    except (CorpusError, OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(
            json.dumps(
                {"status": "error", "error": str(exc)},
                ensure_ascii=False,
                sort_keys=True,
            )
        )
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
