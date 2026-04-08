from __future__ import annotations

from html import unescape
from html.parser import HTMLParser
import re
from typing import Any
from xml.etree import ElementTree

import requests

from .base import SourceAdapter


ATOM_NAMESPACE = {"atom": "http://www.w3.org/2005/Atom"}


class GoogleReleasesSource(SourceAdapter):
    """Adapter that synchronizes Google Cloud release note Atom feeds."""

    def sync(self) -> dict[str, object]:
        feed_url = self.config["url"]
        response = requests.get(
            feed_url,
            headers={"Accept": "application/atom+xml, application/xml;q=0.9, text/xml;q=0.8"},
            timeout=60,
        )
        response.raise_for_status()

        entries = parse_google_releases_feed(response.text)
        self.clear_source_dir()

        for entry in entries:
            document_path = self.raw_dir / "entries" / f"{entry['slug']}.md"
            frontmatter = {
                "title": entry["title"],
                "knowledge_key": self.source["key"],
                "source_id": self.source["id"],
                "source_type": self.source["type"],
                "entry_id": entry["entry_id"],
                "entry_updated": entry["updated"],
                "entry_url": entry["url"],
                "feed_url": feed_url,
                "products": entry["products"],
                "product_count": len(entry["products"]),
            }
            self.write_markdown(document_path, frontmatter, _render_entry_markdown(entry))

        return self.finalize_sync(
            {
                "entries": len(entries),
                "feed_url": feed_url,
                "documents": len(entries),
                "library_dir": str(self.raw_dir),
            }
        )


def parse_google_releases_feed(payload: str) -> list[dict[str, object]]:
    """Parse the Google Cloud release notes Atom feed into normalized entries."""
    root = ElementTree.fromstring(payload)
    entries: list[dict[str, object]] = []
    for entry in root.findall("atom:entry", ATOM_NAMESPACE):
        title = _text(entry, "atom:title") or "Untitled release"
        entry_id = _text(entry, "atom:id") or title
        updated = _text(entry, "atom:updated")
        content = entry.find("atom:content", ATOM_NAMESPACE)
        html = content.text if content is not None and content.text is not None else ""
        entry_url = None
        for link in entry.findall("atom:link", ATOM_NAMESPACE):
            if link.get("rel") == "alternate" and link.get("href"):
                entry_url = link.get("href")
                break
        products = _extract_release_products(html)
        entries.append(
            {
                "title": title,
                "entry_id": entry_id,
                "updated": updated,
                "url": entry_url,
                "html": html,
                "products": products,
                "slug": _slugify_release_entry(title, entry_id),
            }
        )
    return entries


def _render_entry_markdown(entry: dict[str, object]) -> str:
    title = str(entry.get("title") or "Untitled release")
    products = [str(product) for product in entry.get("products", []) if product]
    lines = [f"# {title}"]
    if entry.get("updated"):
        lines.extend(["", f"- Updated: {entry['updated']}"])
    if entry.get("url"):
        lines.append(f"- Source: {entry['url']}")
    if products:
        lines.append(f"- Products: {', '.join(products)}")

    content = _google_release_html_to_markdown(str(entry.get("html") or ""))
    if content:
        lines.extend(["", content])
    return "\n".join(lines).rstrip() + "\n"


def _extract_release_products(html: str) -> list[str]:
    parser = _ProductTitleParser()
    parser.feed(html)
    parser.close()
    return parser.products


class _ProductTitleParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.products: list[str] = []
        self._capture_product = False
        self._buffer: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = dict(attrs)
        class_name = attrs_dict.get("class") or ""
        if tag == "h2" and "release-note-product-title" in class_name.split():
            self._capture_product = True
            self._buffer = []

    def handle_endtag(self, tag: str) -> None:
        if tag == "h2" and self._capture_product:
            value = " ".join("".join(self._buffer).split())
            if value:
                self.products.append(value)
            self._capture_product = False
            self._buffer = []

    def handle_data(self, data: str) -> None:
        if self._capture_product and data:
            self._buffer.append(unescape(data))


class _GoogleReleaseHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.list_stack: list[str] = []
        self.link_stack: list[str | None] = []
        self.code_stack: list[bool] = []
        self.table_state: list[dict[str, object]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        handler = self._START_HANDLERS.get(tag)
        if handler is not None:
            handler(self, attrs)

    def handle_endtag(self, tag: str) -> None:
        handler = self._END_HANDLERS.get(tag)
        if handler is not None:
            handler(self)

    def handle_data(self, data: str) -> None:
        if not data:
            return
        text = re.sub(r"\s+", " ", unescape(data))
        if not text.strip():
            return
        if self.table_state and self.table_state[-1].get("current_cell") is not None:
            current_cell = self.table_state[-1]["current_cell"]
            if isinstance(current_cell, list):
                current_cell.append(text)
            return
        self.parts.append(text)

    # -- Start-tag handlers ------------------------------------------------

    def _start_block(self, _attrs: list[tuple[str, str | None]]) -> None:
        self._ensure_block_break()

    def _start_br(self, _attrs: list[tuple[str, str | None]]) -> None:
        self.parts.append("\n")

    def _start_bold(self, _attrs: list[tuple[str, str | None]]) -> None:
        self.parts.append("**")

    def _start_italic(self, _attrs: list[tuple[str, str | None]]) -> None:
        self.parts.append("*")

    def _start_code(self, _attrs: list[tuple[str, str | None]]) -> None:
        self.code_stack.append(True)
        self.parts.append("`")

    def _start_heading(self, attrs: list[tuple[str, str | None]], tag: str = "h1") -> None:
        self._ensure_block_break()
        attrs_dict = dict(attrs)
        prefix = "#" * int(tag[1])
        if tag == "h2" and "release-note-product-title" in (attrs_dict.get("class") or "").split():
            prefix = "##"
        self.parts.append(f"{prefix} ")

    def _start_list(self, attrs: list[tuple[str, str | None]], tag: str = "ul") -> None:
        self._ensure_block_break()
        self.list_stack.append(tag)

    def _start_li(self, _attrs: list[tuple[str, str | None]]) -> None:
        indent = "  " * max(len(self.list_stack) - 1, 0)
        marker = "- " if (self.list_stack[-1:] and self.list_stack[-1] == "ul") else "1. "
        self.parts.append(f"{indent}{marker}")

    def _start_a(self, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = dict(attrs)
        self.link_stack.append(attrs_dict.get("href"))
        self.parts.append("[")

    def _start_table(self, _attrs: list[tuple[str, str | None]]) -> None:
        self._ensure_block_break()
        self.table_state.append({"rows": [], "current_row": None, "current_cell": None})

    def _start_tr(self, _attrs: list[tuple[str, str | None]]) -> None:
        if self.table_state:
            self.table_state[-1]["current_row"] = []

    def _start_cell(self, _attrs: list[tuple[str, str | None]]) -> None:
        if self.table_state:
            self.table_state[-1]["current_cell"] = []

    _START_HANDLERS: dict[str, Any] = {}

    # -- End-tag handlers --------------------------------------------------

    def _end_block(self) -> None:
        self._ensure_block_break()

    def _end_bold(self) -> None:
        self.parts.append("**")

    def _end_italic(self) -> None:
        self.parts.append("*")

    def _end_code(self) -> None:
        if self.code_stack:
            self.code_stack.pop()
        self.parts.append("`")

    def _end_heading(self) -> None:
        self._ensure_block_break()

    def _end_list(self) -> None:
        if self.list_stack:
            self.list_stack.pop()
        self._ensure_block_break()

    def _end_li(self) -> None:
        self.parts.append("\n")

    def _end_a(self) -> None:
        href = self.link_stack.pop() if self.link_stack else None
        self.parts.append(f"]({href})" if href else "]")

    def _end_cell(self) -> None:
        if not self.table_state:
            return
        table = self.table_state[-1]
        current_row = table.get("current_row")
        current_cell = table.get("current_cell")
        if isinstance(current_row, list):
            current_row.append(" ".join("".join(current_cell or []).split()))
        table["current_cell"] = None

    def _end_tr(self) -> None:
        if not self.table_state:
            return
        table = self.table_state[-1]
        current_row = table.get("current_row")
        if isinstance(current_row, list) and current_row:
            rows = table.get("rows")
            if isinstance(rows, list):
                rows.append(current_row)
        table["current_row"] = None

    def _end_table(self) -> None:
        if not self.table_state:
            return
        table = self.table_state.pop()
        rows = table.get("rows")
        if isinstance(rows, list) and rows:
            self.parts.append(_markdown_table(rows))
            self._ensure_block_break()

    _END_HANDLERS: dict[str, Any] = {}

    def render(self) -> str:
        """Join parts and normalize whitespace into final Markdown output."""
        text = "".join(self.parts)
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r"[ \t]+\n", "\n", text)
        return text.strip()

    def _ensure_block_break(self) -> None:
        current = "".join(self.parts[-2:])
        if not current.endswith("\n\n"):
            if current.endswith("\n"):
                self.parts.append("\n")
            else:
                self.parts.append("\n\n")


# Populate dispatch tables after class definition so methods are bound.
def _make_heading_start(t: str):  # noqa: ANN202
    def handler(self: _GoogleReleaseHTMLParser, attrs: list[tuple[str, str | None]]) -> None:
        self._start_heading(attrs, tag=t)
    return handler

def _make_list_start(t: str):  # noqa: ANN202
    def handler(self: _GoogleReleaseHTMLParser, attrs: list[tuple[str, str | None]]) -> None:
        self._start_list(attrs, tag=t)
    return handler

_GoogleReleaseHTMLParser._START_HANDLERS = {
    "p": _GoogleReleaseHTMLParser._start_block,
    "div": _GoogleReleaseHTMLParser._start_block,
    "br": _GoogleReleaseHTMLParser._start_br,
    "strong": _GoogleReleaseHTMLParser._start_bold,
    "b": _GoogleReleaseHTMLParser._start_bold,
    "em": _GoogleReleaseHTMLParser._start_italic,
    "i": _GoogleReleaseHTMLParser._start_italic,
    "code": _GoogleReleaseHTMLParser._start_code,
    "li": _GoogleReleaseHTMLParser._start_li,
    "a": _GoogleReleaseHTMLParser._start_a,
    "table": _GoogleReleaseHTMLParser._start_table,
    "tr": _GoogleReleaseHTMLParser._start_tr,
    "th": _GoogleReleaseHTMLParser._start_cell,
    "td": _GoogleReleaseHTMLParser._start_cell,
    **{f"h{i}": _make_heading_start(f"h{i}") for i in range(1, 7)},
    "ul": _make_list_start("ul"),
    "ol": _make_list_start("ol"),
}

_GoogleReleaseHTMLParser._END_HANDLERS = {
    "p": _GoogleReleaseHTMLParser._end_block,
    "div": _GoogleReleaseHTMLParser._end_block,
    "strong": _GoogleReleaseHTMLParser._end_bold,
    "b": _GoogleReleaseHTMLParser._end_bold,
    "em": _GoogleReleaseHTMLParser._end_italic,
    "i": _GoogleReleaseHTMLParser._end_italic,
    "code": _GoogleReleaseHTMLParser._end_code,
    "li": _GoogleReleaseHTMLParser._end_li,
    "a": _GoogleReleaseHTMLParser._end_a,
    "th": _GoogleReleaseHTMLParser._end_cell,
    "td": _GoogleReleaseHTMLParser._end_cell,
    "tr": _GoogleReleaseHTMLParser._end_tr,
    "table": _GoogleReleaseHTMLParser._end_table,
    "ul": _GoogleReleaseHTMLParser._end_list,
    "ol": _GoogleReleaseHTMLParser._end_list,
    **{f"h{i}": _GoogleReleaseHTMLParser._end_heading for i in range(1, 7)},
}


def _google_release_html_to_markdown(html: str) -> str:
    parser = _GoogleReleaseHTMLParser()
    parser.feed(html)
    parser.close()
    return parser.render()


def _markdown_table(rows: list[object]) -> str:
    normalized_rows = [[str(cell).strip() for cell in row] for row in rows if isinstance(row, list) and row]
    if not normalized_rows:
        return ""
    width = max(len(row) for row in normalized_rows)
    padded = [row + [""] * (width - len(row)) for row in normalized_rows]
    header = padded[0]
    lines = [
        "| " + " | ".join(header) + " |",
        "| " + " | ".join("---" for _ in header) + " |",
    ]
    for row in padded[1:]:
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def _slugify_release_entry(title: str, entry_id: str) -> str:
    raw_value = title or entry_id.rsplit("#", 1)[-1]
    normalized = re.sub(r"[^A-Za-z0-9._-]+", "-", raw_value).strip("-").lower()
    return normalized or "release"


def _text(element: ElementTree.Element, selector: str) -> str | None:
    node = element.find(selector, ATOM_NAMESPACE)
    if node is None or node.text is None:
        return None
    return " ".join(node.text.split())
