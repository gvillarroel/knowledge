#!/usr/bin/env python3
"""Validate, inventory, and deterministically prepare the private EPUB corpus."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import posixpath
import re
import shutil
import sys
import tempfile
import unicodedata
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath
from typing import Any, Mapping, Sequence
from urllib.parse import unquote, urlsplit
from zipfile import ZIP_STORED, BadZipFile, ZipFile


DATASET_ID = "data-science-ai-ml-books-38"
CATALOG_SCHEMA = "google-drive-epub-source/1.0"
INVENTORY_SCHEMA = "epub-corpus-inventory/1.0"
DESCRIPTOR_SCHEMA = "private-knowledge-corpus/1.0"
RECEIPT_SCHEMA = "epub-corpus-preparation/1.0"
EXTRACTOR_ID = "stdlib-epub-xhtml-to-markdown/1.0"
EPUB_MIME_TYPE = "application/epub+zip"
MAX_CONTROL_FILE_BYTES = 5 * 1024 * 1024
MAX_SPINE_MEMBER_BYTES = 8 * 1024 * 1024
MAX_TOTAL_SPINE_BYTES = 64 * 1024 * 1024
DEFAULT_ROOT = Path(__file__).resolve().parents[1]
PORTABLE_NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*\.epub$")
PARTITION_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
DRIVE_ID_RE = re.compile(r"^[A-Za-z0-9_-]{10,}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
IGNORED_XHTML_TAGS = frozenset({"head", "script", "style", "noscript", "template"})
BLOCK_XHTML_TAGS = frozenset(
    {
        "address",
        "article",
        "aside",
        "dd",
        "div",
        "dl",
        "dt",
        "figcaption",
        "figure",
        "footer",
        "header",
        "main",
        "nav",
        "p",
        "section",
    }
)


class DatasetError(RuntimeError):
    """Report a closed-contract dataset validation or preparation failure."""


@dataclass(frozen=True)
class EpubPackage:
    """Describe verified EPUB metadata and the ordered readable spine."""

    title: str
    authors: str
    publisher: str
    language: str
    publication_date: str
    isbn: str
    spine_members: tuple[str, ...]
    sections: tuple[tuple[str, str], ...] = ()


class _XhtmlToMarkdown(HTMLParser):
    """Render bounded XHTML body markup into stable, readable Markdown."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.ignored_depth = 0
        self.pre_buffer: list[str] | None = None
        self.list_stack: list[list[Any]] = []
        self.table_cell_index: int | None = None

    @staticmethod
    def _tag(value: str) -> str:
        return value.rsplit(":", 1)[-1].lower()

    def _block(self) -> None:
        self.parts.append("\n\n")

    def _append_inline(self, value: str) -> None:
        value = unicodedata.normalize("NFC", re.sub(r"\s+", " ", value))
        if not value:
            return
        previous = self.parts[-1][-1:] if self.parts and self.parts[-1] else ""
        if previous.isspace() and value.startswith(" "):
            value = value.lstrip(" ")
        elif previous == "\n":
            value = value.lstrip(" ")
        self.parts.append(value)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = self._tag(tag)
        attributes = {self._tag(key): value or "" for key, value in attrs}
        if self.ignored_depth:
            self.ignored_depth += 1
            return
        if tag in IGNORED_XHTML_TAGS:
            self.ignored_depth = 1
            return
        if self.pre_buffer is not None:
            if tag == "br":
                self.pre_buffer.append("\n")
            return
        if tag == "pre":
            self.pre_buffer = []
            return
        if tag in BLOCK_XHTML_TAGS:
            self._block()
        elif tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            self._block()
            level = min(6, int(tag[1]) + 1)
            self.parts.append(f"{'#' * level} ")
        elif tag == "br":
            self.parts.append("\n")
        elif tag == "hr":
            self.parts.append("\n\n---\n\n")
        elif tag in {"ul", "ol"}:
            self._block()
            self.list_stack.append([tag, 0])
        elif tag == "li":
            self.parts.append("\n")
            depth = max(0, len(self.list_stack) - 1)
            prefix = "- "
            if self.list_stack and self.list_stack[-1][0] == "ol":
                self.list_stack[-1][1] += 1
                prefix = f"{self.list_stack[-1][1]}. "
            self.parts.append(f"{'  ' * depth}{prefix}")
        elif tag == "blockquote":
            self._block()
        elif tag == "table":
            self._block()
        elif tag == "tr":
            self.parts.append("\n")
            self.table_cell_index = 0
        elif tag in {"th", "td"}:
            if self.table_cell_index is None:
                self.table_cell_index = 0
            if self.table_cell_index:
                self.parts.append(" | ")
            self.table_cell_index += 1
        elif tag == "img":
            alt = _normalize_space(attributes.get("alt", ""))
            if alt:
                self.parts.append(f"[Image: {alt}]")

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_endtag(self, tag: str) -> None:
        tag = self._tag(tag)
        if self.ignored_depth:
            self.ignored_depth -= 1
            return
        if self.pre_buffer is not None:
            if tag == "pre":
                value = unicodedata.normalize(
                    "NFC", "".join(self.pre_buffer).replace("\r\n", "\n").replace("\r", "\n")
                ).strip("\n")
                longest = max((len(item) for item in re.findall(r"`+", value)), default=0)
                fence = "`" * max(3, longest + 1)
                self.parts.append(f"\n\n{fence}text\n{value}\n{fence}\n\n")
                self.pre_buffer = None
            return
        if tag in BLOCK_XHTML_TAGS or tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            self._block()
        elif tag in {"ul", "ol"}:
            if self.list_stack:
                self.list_stack.pop()
            self._block()
        elif tag == "li":
            self.parts.append("\n")
        elif tag == "blockquote":
            self._block()
        elif tag == "tr":
            self.parts.append("\n")
            self.table_cell_index = None

    def handle_data(self, data: str) -> None:
        if self.ignored_depth:
            return
        if self.pre_buffer is not None:
            self.pre_buffer.append(data)
            return
        self._append_inline(data)

    def markdown(self) -> str:
        """Return normalized Markdown after the complete XHTML body was fed."""

        if self.pre_buffer is not None:
            raise DatasetError("XHTML contains an unclosed preformatted block")
        value = "".join(self.parts).replace("\r\n", "\n").replace("\r", "\n")
        value = re.sub(r"[ \t]+\n", "\n", value)
        value = re.sub(r"\n{3,}", "\n\n", value)
        return value.strip()


def _normalize_space(value: str) -> str:
    return unicodedata.normalize("NFC", re.sub(r"\s+", " ", value).strip())


def _local_name(value: str) -> str:
    return value.rsplit("}", 1)[-1].rsplit(":", 1)[-1]


def _exact_keys(value: Mapping[str, Any], expected: set[str], label: str) -> None:
    missing = sorted(expected - set(value))
    extra = sorted(set(value) - expected)
    if missing or extra:
        details: list[str] = []
        if missing:
            details.append(f"missing {missing}")
        if extra:
            details.append(f"unexpected {extra}")
        raise DatasetError(f"{label} has invalid fields: {'; '.join(details)}")


def _require_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise DatasetError(f"{label} must be a non-empty string")
    return value


def _require_timestamp(value: Any, label: str) -> str:
    text = _require_string(value, label)
    try:
        normalized = text.removesuffix("Z") + ("+00:00" if text.endswith("Z") else "")
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise DatasetError(f"{label} must be an ISO-8601 timestamp") from exc
    if parsed.tzinfo is None:
        raise DatasetError(f"{label} must include a timezone")
    return text


def _canonical_json(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True).encode("utf-8") + b"\n"
    )


def sha256_file(path: Path) -> str:
    """Return the SHA-256 digest of one regular file without loading it whole."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _safe_archive_name(value: str, label: str) -> str:
    if "\\" in value or "\x00" in value:
        raise DatasetError(f"{label} is not a portable EPUB member path")
    path = PurePosixPath(value)
    if path.is_absolute() or not path.parts or ".." in path.parts:
        raise DatasetError(f"{label} is not a safe EPUB member path")
    return path.as_posix()


def _resolve_archive_href(base: str, href: str, label: str) -> str:
    parsed = urlsplit(href)
    if parsed.scheme or parsed.netloc:
        raise DatasetError(f"{label} must be an archive-local reference")
    decoded = unquote(parsed.path)
    if not decoded:
        raise DatasetError(f"{label} has an empty archive path")
    _safe_archive_name(decoded, label)
    combined = posixpath.normpath(posixpath.join(base, decoded))
    return _safe_archive_name(combined, label)


def _read_bounded(zf: ZipFile, name: str, maximum: int, label: str) -> bytes:
    try:
        info = zf.getinfo(name)
    except KeyError as exc:
        raise DatasetError(f"{label} is missing from the EPUB: {name}") from exc
    if info.is_dir() or info.file_size > maximum:
        raise DatasetError(f"{label} has an invalid size: {info.file_size}")
    try:
        return zf.read(info)
    except (BadZipFile, RuntimeError) as exc:
        raise DatasetError(f"{label} failed CRC or encryption validation") from exc


def _metadata_values(metadata: ET.Element, name: str) -> list[str]:
    return [
        text
        for child in list(metadata)
        if _local_name(child.tag) == name and (text := _normalize_space(child.text or ""))
    ]


def _single_metadata(metadata: ET.Element, name: str, label: str) -> str:
    values = _metadata_values(metadata, name)
    if not values:
        raise DatasetError(f"EPUB metadata is missing {label}")
    return values[0]


def _validate_zip_members(zf: ZipFile) -> None:
    infos = zf.infolist()
    if not infos:
        raise DatasetError("EPUB archive is empty")
    names = [item.filename for item in infos]
    if len(names) != len(set(names)):
        raise DatasetError("EPUB archive contains duplicate member names")
    for info in infos:
        _safe_archive_name(info.filename.rstrip("/"), "EPUB member")
        if info.flag_bits & 0x1:
            raise DatasetError(f"EPUB member is encrypted: {info.filename}")
    first = infos[0]
    if (
        first.filename != "mimetype"
        or first.compress_type != ZIP_STORED
        or _read_bounded(zf, "mimetype", 128, "EPUB mimetype") != EPUB_MIME_TYPE.encode()
    ):
        raise DatasetError("EPUB mimetype must be the first uncompressed archive member")


def _xhtml_to_markdown(value: bytes, member_name: str) -> str:
    try:
        root = ET.fromstring(value)
    except ET.ParseError as exc:
        raise DatasetError(f"spine document is not well-formed XHTML: {member_name}") from exc
    body = next((node for node in root.iter() if _local_name(node.tag) == "body"), None)
    if body is None:
        raise DatasetError(f"spine document has no XHTML body: {member_name}")
    parser = _XhtmlToMarkdown()
    parser.feed(ET.tostring(body, encoding="unicode", method="html"))
    parser.close()
    return parser.markdown()


def inspect_epub(path: Path, *, extract_sections: bool = False) -> EpubPackage:
    """Validate one EPUB and return exact OPF metadata and ordered spine members."""

    try:
        with ZipFile(path) as zf:
            _validate_zip_members(zf)
            container_bytes = _read_bounded(
                zf, "META-INF/container.xml", MAX_CONTROL_FILE_BYTES, "EPUB container"
            )
            try:
                container = ET.fromstring(container_bytes)
            except ET.ParseError as exc:
                raise DatasetError("EPUB container is not well-formed XML") from exc
            rootfiles = [
                node for node in container.iter() if _local_name(node.tag) == "rootfile"
            ]
            if len(rootfiles) != 1:
                raise DatasetError("EPUB container must declare exactly one rootfile")
            opf_name = _safe_archive_name(
                _require_string(rootfiles[0].attrib.get("full-path"), "EPUB rootfile path"),
                "EPUB rootfile path",
            )
            opf_bytes = _read_bounded(zf, opf_name, MAX_CONTROL_FILE_BYTES, "EPUB package")
            try:
                package = ET.fromstring(opf_bytes)
            except ET.ParseError as exc:
                raise DatasetError("EPUB package is not well-formed XML") from exc
            metadata = next(
                (node for node in package.iter() if _local_name(node.tag) == "metadata"), None
            )
            manifest = next(
                (node for node in package.iter() if _local_name(node.tag) == "manifest"), None
            )
            spine = next(
                (node for node in package.iter() if _local_name(node.tag) == "spine"), None
            )
            if metadata is None or manifest is None or spine is None:
                raise DatasetError("EPUB package must contain metadata, manifest, and spine")
            title = _single_metadata(metadata, "title", "title")
            creators = _metadata_values(metadata, "creator")
            if not creators:
                raise DatasetError("EPUB metadata is missing creator")
            authors = "; ".join(creators)
            publisher = _single_metadata(metadata, "publisher", "publisher")
            language = _single_metadata(metadata, "language", "language").lower()
            if language != "en" and not language.startswith("en-"):
                raise DatasetError(f"EPUB language is outside the English-only corpus: {language}")
            publication_date = _single_metadata(metadata, "date", "publication date")
            if not DATE_RE.fullmatch(publication_date):
                raise DatasetError(f"EPUB publication date is not YYYY-MM-DD: {publication_date}")
            isbn = _single_metadata(metadata, "identifier", "identifier")
            items: dict[str, tuple[str, str]] = {}
            package_base = posixpath.dirname(opf_name)
            for node in list(manifest):
                if _local_name(node.tag) != "item":
                    continue
                item_id = _require_string(node.attrib.get("id"), "EPUB manifest item id")
                if item_id in items:
                    raise DatasetError(f"duplicate EPUB manifest item id: {item_id}")
                media_type = _require_string(
                    node.attrib.get("media-type"), f"EPUB manifest item {item_id} media type"
                )
                member = _resolve_archive_href(
                    package_base,
                    _require_string(
                        node.attrib.get("href"), f"EPUB manifest item {item_id} href"
                    ),
                    f"EPUB manifest item {item_id}",
                )
                items[item_id] = (member, media_type)
            spine_members: list[str] = []
            for node in list(spine):
                if _local_name(node.tag) != "itemref":
                    continue
                item_id = _require_string(node.attrib.get("idref"), "EPUB spine itemref")
                if item_id not in items:
                    raise DatasetError(f"EPUB spine references unknown manifest item: {item_id}")
                member, media_type = items[item_id]
                if media_type not in {"application/xhtml+xml", "text/html"}:
                    raise DatasetError(
                        f"EPUB spine item {item_id} has unsupported media type: {media_type}"
                    )
                spine_members.append(member)
            if not spine_members or len(spine_members) != len(set(spine_members)):
                raise DatasetError("EPUB spine must be non-empty and contain unique documents")
            total_spine_bytes = 0
            sections: list[tuple[str, str]] = []
            for member in spine_members:
                try:
                    info = zf.getinfo(member)
                except KeyError as exc:
                    raise DatasetError(f"EPUB spine member is missing: {member}") from exc
                total_spine_bytes += info.file_size
                if info.file_size > MAX_SPINE_MEMBER_BYTES:
                    raise DatasetError(f"EPUB spine member is too large: {member}")
                if total_spine_bytes > MAX_TOTAL_SPINE_BYTES:
                    raise DatasetError("EPUB readable spine exceeds the extraction limit")
                if extract_sections:
                    rendered = _xhtml_to_markdown(
                        _read_bounded(zf, member, MAX_SPINE_MEMBER_BYTES, "EPUB spine member"),
                        member,
                    )
                    if rendered:
                        sections.append((member, rendered))
            return EpubPackage(
                title=title,
                authors=authors,
                publisher=publisher,
                language=language,
                publication_date=publication_date,
                isbn=isbn,
                spine_members=tuple(spine_members),
                sections=tuple(sections),
            )
    except (BadZipFile, OSError) as exc:
        raise DatasetError(f"cannot read EPUB {path}: {exc}") from exc


def _book_id(partition: str, filename: str) -> str:
    stem = unicodedata.normalize("NFKD", Path(filename).stem)
    ascii_value = stem.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_value.lower()).strip("-")
    if not slug:
        raise DatasetError(f"cannot derive a stable book id from {filename}")
    return f"{partition}-{slug}"


def load_source_catalog(dataset_root: Path) -> dict[str, Any]:
    """Load and validate the closed Google Drive folder and file catalog."""

    path = dataset_root / "sources" / "drive-files.json"
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise DatasetError(f"cannot read source catalog {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise DatasetError("source catalog root must be an object")
    _exact_keys(value, {"schema_version", "dataset_id", "folders", "files"}, "source catalog")
    if value["schema_version"] != CATALOG_SCHEMA or value["dataset_id"] != DATASET_ID:
        raise DatasetError("source catalog identity is invalid")
    if not isinstance(value["folders"], list) or not value["folders"]:
        raise DatasetError("source catalog folders must be a non-empty list")
    partitions: set[str] = set()
    folder_ids: set[str] = set()
    for index, folder in enumerate(value["folders"]):
        if not isinstance(folder, dict):
            raise DatasetError(f"source catalog folder {index} must be an object")
        _exact_keys(
            folder,
            {
                "partition",
                "folder_id",
                "folder_name",
                "url",
                "created_time",
                "modified_time",
            },
            f"source catalog folder {index}",
        )
        partition = _require_string(folder["partition"], f"folder {index} partition")
        folder_id = _require_string(folder["folder_id"], f"folder {index} id")
        if not PARTITION_RE.fullmatch(partition) or not DRIVE_ID_RE.fullmatch(folder_id):
            raise DatasetError(f"source catalog folder {index} has invalid identity")
        if partition in partitions or folder_id in folder_ids:
            raise DatasetError("source catalog contains duplicate folder identity")
        partitions.add(partition)
        folder_ids.add(folder_id)
        if folder["url"] != f"https://drive.google.com/drive/folders/{folder_id}":
            raise DatasetError(f"source catalog folder {partition} has a noncanonical URL")
        _require_string(folder["folder_name"], f"folder {partition} name")
        _require_timestamp(folder["created_time"], f"folder {partition} created_time")
        _require_timestamp(folder["modified_time"], f"folder {partition} modified_time")
    if not isinstance(value["files"], list) or not value["files"]:
        raise DatasetError("source catalog files must be a non-empty list")
    file_ids: set[str] = set()
    file_keys: set[tuple[str, str]] = set()
    for index, item in enumerate(value["files"]):
        if not isinstance(item, dict):
            raise DatasetError(f"source catalog file {index} must be an object")
        _exact_keys(
            item,
            {
                "partition",
                "drive_file_id",
                "filename",
                "mime_type",
                "size_bytes",
                "created_time",
                "modified_time",
                "url",
            },
            f"source catalog file {index}",
        )
        partition = _require_string(item["partition"], f"file {index} partition")
        file_id = _require_string(item["drive_file_id"], f"file {index} id")
        filename = _require_string(item["filename"], f"file {index} filename")
        if partition not in partitions or not DRIVE_ID_RE.fullmatch(file_id):
            raise DatasetError(f"source catalog file {index} has invalid identity")
        if not PORTABLE_NAME_RE.fullmatch(filename):
            raise DatasetError(f"source catalog file {index} has a nonportable EPUB filename")
        if item["mime_type"] != EPUB_MIME_TYPE:
            raise DatasetError(f"source catalog file {index} has an invalid MIME type")
        if (
            isinstance(item["size_bytes"], bool)
            or not isinstance(item["size_bytes"], int)
            or item["size_bytes"] <= 0
        ):
            raise DatasetError(f"source catalog file {index} has an invalid byte size")
        if item["url"] != f"https://drive.google.com/file/d/{file_id}/view?usp=drivesdk":
            raise DatasetError(f"source catalog file {index} has a noncanonical URL")
        _require_timestamp(item["created_time"], f"file {index} created_time")
        _require_timestamp(item["modified_time"], f"file {index} modified_time")
        key = (partition, filename)
        if file_id in file_ids or key in file_keys:
            raise DatasetError("source catalog contains duplicate file identity")
        file_ids.add(file_id)
        file_keys.add(key)
    expected_order = sorted(
        value["files"], key=lambda item: (item["partition"], item["filename"])
    )
    if value["files"] != expected_order:
        raise DatasetError("source catalog files must be sorted by partition and filename")
    return value


def build_inventory(dataset_root: Path, catalog: Mapping[str, Any]) -> dict[str, Any]:
    """Verify the complete raw EPUB tree and return its content-bound inventory."""

    raw_root = dataset_root / "raw" / "epub"
    expected = {
        (item["partition"], item["filename"]): item for item in catalog["files"]
    }
    actual: dict[tuple[str, str], Path] = {}
    if raw_root.is_dir():
        for path in sorted(raw_root.rglob("*")):
            if path.is_symlink():
                raise DatasetError(f"raw EPUB tree contains a symlink: {path}")
            if not path.is_file():
                continue
            relative = path.relative_to(raw_root)
            if len(relative.parts) != 2:
                raise DatasetError(f"raw EPUB path must be partition/filename: {relative}")
            actual[(relative.parts[0], relative.parts[1])] = path
    if set(actual) != set(expected):
        missing = sorted(set(expected) - set(actual))
        extra = sorted(set(actual) - set(expected))
        raise DatasetError(f"raw EPUB membership drift: missing={missing}; extra={extra}")
    books: list[dict[str, Any]] = []
    book_ids: set[str] = set()
    summary: dict[str, dict[str, int]] = {
        folder["partition"]: {"files": 0, "bytes": 0} for folder in catalog["folders"]
    }
    for key in sorted(expected):
        source = expected[key]
        path = actual[key]
        observed_size = path.stat().st_size
        if observed_size != source["size_bytes"]:
            raise DatasetError(
                f"raw EPUB size drift for {source['filename']}: "
                f"expected {source['size_bytes']}, observed {observed_size}"
            )
        package = inspect_epub(path)
        book_id = _book_id(source["partition"], source["filename"])
        if book_id in book_ids:
            raise DatasetError(f"duplicate derived book id: {book_id}")
        book_ids.add(book_id)
        books.append(
            {
                "book_id": book_id,
                "partition": source["partition"],
                "filename": source["filename"],
                "media_type": source["mime_type"],
                "size_bytes": observed_size,
                "sha256": sha256_file(path),
                "drive_file_id": source["drive_file_id"],
                "drive_url": source["url"],
                "drive_created_time": source["created_time"],
                "drive_modified_time": source["modified_time"],
                "title": package.title,
                "authors": package.authors,
                "publisher": package.publisher,
                "language": package.language,
                "publication_date": package.publication_date,
                "isbn": package.isbn,
                "spine_documents": len(package.spine_members),
            }
        )
        summary[source["partition"]]["files"] += 1
        summary[source["partition"]]["bytes"] += observed_size
    catalog_path = dataset_root / "sources" / "drive-files.json"
    return {
        "schema_version": INVENTORY_SCHEMA,
        "dataset_id": DATASET_ID,
        "source_catalog": {
            "path": "sources/drive-files.json",
            "sha256": sha256_file(catalog_path),
        },
        "summary": {
            "files": len(books),
            "bytes": sum(item["size_bytes"] for item in books),
            "partitions": dict(sorted(summary.items())),
        },
        "books": books,
    }


def load_inventory(dataset_root: Path) -> dict[str, Any]:
    """Load the tracked raw-content inventory after basic closed-shape checks."""

    path = dataset_root / "sources" / "inventory.json"
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise DatasetError(f"cannot read inventory {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise DatasetError("inventory root must be an object")
    _exact_keys(
        value,
        {"schema_version", "dataset_id", "source_catalog", "summary", "books"},
        "inventory",
    )
    if value["schema_version"] != INVENTORY_SCHEMA or value["dataset_id"] != DATASET_ID:
        raise DatasetError("inventory identity is invalid")
    if not isinstance(value["books"], list) or not value["books"]:
        raise DatasetError("inventory books must be a non-empty list")
    for index, book in enumerate(value["books"]):
        if not isinstance(book, dict):
            raise DatasetError(f"inventory book {index} must be an object")
        digest = book.get("sha256")
        if not isinstance(digest, str) or not SHA256_RE.fullmatch(digest):
            raise DatasetError(f"inventory book {index} has an invalid SHA-256")
    return value


def check_inventory(dataset_root: Path) -> dict[str, Any]:
    """Rebuild the inventory from raw bytes and reject any tracked drift."""

    catalog = load_source_catalog(dataset_root)
    expected = load_inventory(dataset_root)
    observed = build_inventory(dataset_root, catalog)
    if observed != expected:
        raise DatasetError("tracked EPUB inventory differs from the verified raw corpus")
    return observed


def check_descriptor(dataset_root: Path) -> dict[str, Any]:
    """Validate the corpus descriptor and every hash-pinned tracked artifact."""

    path = dataset_root / "dataset.json"
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise DatasetError(f"cannot read dataset descriptor {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise DatasetError("dataset descriptor root must be an object")
    _exact_keys(
        value,
        {
            "schema_version",
            "dataset_id",
            "title",
            "description",
            "language",
            "source_format",
            "source_folders",
            "summary",
            "artifacts",
            "evaluation_status",
        },
        "dataset descriptor",
    )
    if value["schema_version"] != DESCRIPTOR_SCHEMA or value["dataset_id"] != DATASET_ID:
        raise DatasetError("dataset descriptor identity is invalid")
    if value["language"] != "en" or value["source_format"] != "EPUB":
        raise DatasetError("dataset descriptor language or source format is invalid")
    if value["evaluation_status"] != "corpus-only-not-registered":
        raise DatasetError("dataset descriptor evaluation status is invalid")
    _require_string(value["title"], "dataset title")
    _require_string(value["description"], "dataset description")
    catalog = load_source_catalog(dataset_root)
    inventory = load_inventory(dataset_root)
    expected_folders = [
        {
            "partition": folder["partition"],
            "folder_id": folder["folder_id"],
            "url": folder["url"],
        }
        for folder in catalog["folders"]
    ]
    if value["source_folders"] != expected_folders:
        raise DatasetError("dataset descriptor source folder binding drift")
    if value["summary"] != inventory["summary"]:
        raise DatasetError("dataset descriptor summary drift")
    artifacts = value["artifacts"]
    if not isinstance(artifacts, list) or not artifacts:
        raise DatasetError("dataset descriptor artifacts must be a non-empty list")
    expected_roles = {
        "source-catalog",
        "source-inventory",
        "semantic-manifest",
        "source-combination",
        "scope",
    }
    observed_roles: set[str] = set()
    for index, artifact in enumerate(artifacts):
        if not isinstance(artifact, dict):
            raise DatasetError(f"dataset artifact {index} must be an object")
        _exact_keys(artifact, {"role", "path", "sha256"}, f"dataset artifact {index}")
        role = _require_string(artifact["role"], f"dataset artifact {index} role")
        relative = _require_string(artifact["path"], f"dataset artifact {index} path")
        digest = _require_string(artifact["sha256"], f"dataset artifact {index} sha256")
        if role in observed_roles or role not in expected_roles:
            raise DatasetError(f"dataset artifact {index} has an invalid role")
        observed_roles.add(role)
        if "\\" in relative:
            raise DatasetError(f"dataset artifact {index} path is not portable")
        portable = PurePosixPath(relative)
        if portable.is_absolute() or ".." in portable.parts:
            raise DatasetError(f"dataset artifact {index} path is unsafe")
        artifact_path = (dataset_root / Path(*portable.parts)).resolve()
        try:
            artifact_path.relative_to(dataset_root.resolve())
        except ValueError as exc:
            raise DatasetError(f"dataset artifact {index} escapes the dataset root") from exc
        if not artifact_path.is_file() or not SHA256_RE.fullmatch(digest):
            raise DatasetError(f"dataset artifact {index} is missing or has an invalid digest")
        if sha256_file(artifact_path) != digest:
            raise DatasetError(f"dataset artifact digest drift: {relative}")
    if observed_roles != expected_roles:
        raise DatasetError("dataset descriptor is missing required artifact roles")
    return value


def write_inventory(dataset_root: Path, *, replace: bool = False) -> dict[str, Any]:
    """Write a freshly verified tracked inventory from the current raw corpus."""

    value = build_inventory(dataset_root, load_source_catalog(dataset_root))
    path = dataset_root / "sources" / "inventory.json"
    if path.exists() and not replace:
        raise DatasetError(f"inventory already exists; use --replace explicitly: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(_canonical_json(value))
    return value


def _yaml_scalar(value: str | int) -> str:
    if isinstance(value, int):
        return str(value)
    return json.dumps(value, ensure_ascii=False)


def _book_markdown(book: Mapping[str, Any], package: EpubPackage) -> str:
    body_parts = [f"# {package.title}"]
    for index, (member, content) in enumerate(package.sections, start=1):
        body_parts.extend([f"## EPUB spine document {index}: `{member}`", content])
    body = "\n\n".join(body_parts).strip() + "\n"
    frontmatter: dict[str, str | int] = {
        "title": package.title,
        "book_id": str(book["book_id"]),
        "authors": package.authors,
        "publisher": package.publisher,
        "language": package.language,
        "publication_date": package.publication_date,
        "isbn": package.isbn,
        "collection": str(book["partition"]),
        "source_format": "EPUB",
        "drive_file_id": str(book["drive_file_id"]),
        "drive_url": str(book["drive_url"]),
        "epub_sha256": str(book["sha256"]),
        "epub_size_bytes": int(book["size_bytes"]),
        "spine_documents": len(package.spine_members),
        "extracted_characters": len(body),
    }
    lines = ["---"]
    lines.extend(f"{key}: {_yaml_scalar(frontmatter[key])}" for key in frontmatter)
    lines.extend(["---", "", body.rstrip(), ""])
    return "\n".join(lines)


def _tree_hashes(
    root: Path,
    *,
    excluded_top_levels: frozenset[str] = frozenset(),
) -> dict[str, str]:
    if not root.is_dir():
        raise DatasetError(f"processed dataset directory does not exist: {root}")
    hashes: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise DatasetError(f"processed dataset contains a symlink: {path}")
        if path.is_file():
            relative = path.relative_to(root)
            if relative.parts[0] in excluded_top_levels:
                continue
            hashes[relative.as_posix()] = sha256_file(path)
    return hashes


def _build_processed_tree(dataset_root: Path, destination: Path) -> dict[str, Any]:
    inventory = check_inventory(dataset_root)
    destination.mkdir(parents=True, exist_ok=False)
    outputs: list[dict[str, Any]] = []
    inventory_books = {
        (book["partition"], book["filename"]): book for book in inventory["books"]
    }
    for key in sorted(inventory_books):
        book = inventory_books[key]
        raw_path = dataset_root / "raw" / "epub" / book["partition"] / book["filename"]
        package = inspect_epub(raw_path, extract_sections=True)
        for field in ("title", "authors", "publisher", "language", "publication_date", "isbn"):
            if getattr(package, field) != book[field]:
                raise DatasetError(f"EPUB metadata drift for {book['filename']}: {field}")
        output_stem = book["book_id"].removeprefix(book["partition"] + "-")
        output_relative = Path("markdown") / book["partition"] / f"{output_stem}.md"
        output_path = destination / output_relative
        output_path.parent.mkdir(parents=True, exist_ok=True)
        markdown = _book_markdown(book, package).encode("utf-8")
        output_path.write_bytes(markdown)
        outputs.append(
            {
                "book_id": book["book_id"],
                "source_sha256": book["sha256"],
                "path": output_relative.as_posix(),
                "sha256": _sha256_bytes(markdown),
                "spine_documents": len(package.spine_members),
                "extracted_characters": len(markdown.decode("utf-8")),
            }
        )
    receipt = {
        "schema_version": RECEIPT_SCHEMA,
        "dataset_id": DATASET_ID,
        "extractor": EXTRACTOR_ID,
        "source_inventory": {
            "path": "sources/inventory.json",
            "sha256": sha256_file(dataset_root / "sources" / "inventory.json"),
        },
        "summary": {
            "books": len(outputs),
            "source_bytes": inventory["summary"]["bytes"],
            "extracted_characters": sum(item["extracted_characters"] for item in outputs),
        },
        "outputs": outputs,
    }
    (destination / "receipt.json").write_bytes(_canonical_json(receipt))
    return receipt


def prepare_dataset(
    dataset_root: Path,
    destination: Path,
    *,
    replace: bool = False,
) -> dict[str, Any]:
    """Build the complete processed Markdown corpus and publish it atomically."""

    dataset_root = dataset_root.resolve()
    check_descriptor(dataset_root)
    if destination.is_symlink():
        raise DatasetError(f"processed destination must not be a symlink: {destination}")
    destination = destination.resolve()
    processed_root = (dataset_root / "processed").resolve()
    try:
        destination.relative_to(processed_root)
    except ValueError as exc:
        raise DatasetError(
            f"processed destination must be {processed_root} or one of its descendants"
        ) from exc
    if destination.exists() and not destination.is_dir():
        raise DatasetError(f"processed destination is not a directory: {destination}")
    if destination.exists() and not replace:
        raise DatasetError(
            f"processed destination already exists; use --replace explicitly: {destination}"
        )
    destination.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(
        tempfile.mkdtemp(prefix=f".{destination.name}.transaction-", dir=destination.parent)
    )
    candidate = staging / "candidate"
    previous = staging / "previous"
    try:
        receipt = _build_processed_tree(dataset_root, candidate)
        if destination.exists():
            os.replace(destination, previous)
        try:
            os.replace(candidate, destination)
        except BaseException:
            if previous.exists() and not destination.exists():
                try:
                    os.replace(previous, destination)
                except BaseException as restore_error:
                    raise DatasetError(
                        "processed publication failed and the previous output could not be "
                        f"restored; it remains preserved at {previous}"
                    ) from restore_error
            raise
        shutil.rmtree(staging, ignore_errors=True)
        return receipt
    except BaseException:
        if not previous.exists():
            shutil.rmtree(staging, ignore_errors=True)
        raise


def check_processed(dataset_root: Path, destination: Path) -> dict[str, Any]:
    """Rebuild in temporary storage and require byte-identical processed output."""

    check_descriptor(dataset_root)
    destination = destination.resolve()
    observed_hashes = _tree_hashes(
        destination,
        excluded_top_levels=frozenset({"semantic-okf"}),
    )
    with tempfile.TemporaryDirectory(prefix="epub-corpus-check-") as temporary:
        candidate = Path(temporary) / "processed"
        receipt = _build_processed_tree(dataset_root.resolve(), candidate)
        expected_hashes = _tree_hashes(candidate)
    if observed_hashes != expected_hashes:
        missing = sorted(set(expected_hashes) - set(observed_hashes))
        extra = sorted(set(observed_hashes) - set(expected_hashes))
        changed = sorted(
            path
            for path in set(expected_hashes) & set(observed_hashes)
            if expected_hashes[path] != observed_hashes[path]
        )
        raise DatasetError(
            f"processed dataset drift: missing={missing}; extra={extra}; changed={changed}"
        )
    return receipt


def _summary(value: Mapping[str, Any], operation: str) -> dict[str, Any]:
    source = value.get("summary", {})
    return {
        "status": "passed",
        "operation": operation,
        "dataset_id": DATASET_ID,
        "summary": source,
    }


def build_parser() -> argparse.ArgumentParser:
    """Create the dataset preparation command-line parser."""

    parser = argparse.ArgumentParser(
        description="Validate and deterministically prepare the private Google Drive EPUB corpus."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=DEFAULT_ROOT,
        help="Dataset root containing sources/, raw/, and processed/.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    inventory = subparsers.add_parser("inventory", help="Create or check the raw inventory.")
    inventory_mode = inventory.add_mutually_exclusive_group(required=True)
    inventory_mode.add_argument("--write", action="store_true", help="Write a new inventory.")
    inventory_mode.add_argument(
        "--check",
        action="store_true",
        help="Check the tracked inventory.",
    )
    inventory.add_argument(
        "--replace", action="store_true", help="Replace an existing tracked inventory."
    )
    prepare = subparsers.add_parser("prepare", help="Build the processed Markdown corpus.")
    prepare.add_argument(
        "--output",
        type=Path,
        help="Output within ROOT/processed; defaults to ROOT/processed.",
    )
    prepare.add_argument(
        "--replace",
        action="store_true",
        help="Atomically replace an existing processed output after rebuilding it.",
    )
    check = subparsers.add_parser("check", help="Check raw inventory and processed bytes.")
    check.add_argument(
        "--output",
        type=Path,
        help="Processed output directory; defaults to ROOT/processed.",
    )
    subparsers.add_parser("describe", help="Print the verified raw corpus summary.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the requested dataset inventory, preparation, or check operation."""

    args = build_parser().parse_args(argv)
    root = args.root.resolve()
    if args.command == "inventory":
        value = (
            write_inventory(root, replace=args.replace)
            if args.write
            else check_inventory(root)
        )
        result = _summary(value, "inventory-write" if args.write else "inventory-check")
    elif args.command == "prepare":
        output = (args.output or (root / "processed")).resolve()
        result = _summary(
            prepare_dataset(root, output, replace=args.replace),
            "prepare",
        )
    elif args.command == "check":
        output = (args.output or (root / "processed")).resolve()
        result = _summary(check_processed(root, output), "check")
    else:
        check_descriptor(root)
        result = _summary(check_inventory(root), "describe")
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except DatasetError as exc:
        print(
            json.dumps(
                {"status": "failed", "code": "epub-dataset-error", "message": str(exc)},
                ensure_ascii=False,
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        raise SystemExit(1) from exc
