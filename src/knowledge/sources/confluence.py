from __future__ import annotations

from html import unescape
from html.parser import HTMLParser
import re
from typing import Any
from urllib.parse import urljoin

import requests

from .base import SourceAdapter


class ConfluenceSource(SourceAdapter):
    """Adapter that synchronizes pages from a Confluence space."""

    def sync(self) -> dict[str, object]:
        base_url = self.config["base_url"].rstrip("/") + "/"
        auth = self._auth()
        space_key = self.config["space_key"]
        limit = int(self.config.get("limit", 100))

        pages: list[dict[str, object]] = []
        next_url = urljoin(base_url, "wiki/api/v2/pages")
        params: dict[str, object] | None = {
            "space-key": space_key,
            "limit": limit,
            "body-format": "storage",
        }
        while next_url:
            response = requests.get(
                next_url,
                headers={"Accept": "application/json"},
                params=params,
                auth=auth,
                timeout=60,
            )
            response.raise_for_status()
            data = response.json()
            pages.extend(data.get("results", []))

            next_path = data.get("_links", {}).get("next")
            next_url = urljoin(base_url, next_path) if next_path else ""
            params = None

        self.clear_source_dir()
        for page in pages:
            page_id = page["id"]
            storage_body = page.get("body", {}).get("storage", {}).get("value", "")
            body = confluence_storage_to_markdown(storage_body)
            title = str(page.get("title") or f"Page {page_id}")
            frontmatter = {
                "title": title,
                "knowledge_key": self.source["key"],
                "source_id": self.source["id"],
                "source_type": self.source["type"],
                "document_id": str(page_id),
                "space_key": space_key,
                "space_id": page.get("spaceId"),
                "status": page.get("status"),
                "author_id": page.get("authorId"),
                "owner_id": page.get("ownerId"),
                "parent_id": page.get("parentId"),
                "parent_type": page.get("parentType"),
                "created_at": page.get("createdAt"),
                "updated_at": page.get("version", {}).get("createdAt") or page.get("updatedAt"),
                "version_number": (page.get("version", {}) or {}).get("number"),
                "web_url": _page_url(base_url, page),
            }
            self.write_markdown(self.raw_dir / f"{page_id}-{_slugify(title)}.md", frontmatter, body)

        return self.finalize_sync(
            {
                "pages": len(pages),
                "space_key": space_key,
                "raw_dir": str(self.raw_dir),
            }
        )

    def _auth(self) -> tuple[str, str]:
        username = self.store.resolve_key(self.config["username"])
        token = self.store.resolve_key(self.config["token"])
        return (username, token)


def search_confluence(
    *,
    base_url: str,
    username: str,
    token: str,
    query: str | None = None,
    cql: str | None = None,
    space: str | None = None,
    content_type: str | None = None,
    labels: list[str] | None = None,
    title_contains: str | None = None,
    text_contains: str | None = None,
    created_after: str | None = None,
    created_before: str | None = None,
    updated_after: str | None = None,
    updated_before: str | None = None,
    limit: int = 25,
    cursor: str | None = None,
) -> dict[str, object]:
    compiled_cql = cql or _build_cql(
        query=query,
        space=space,
        content_type=content_type,
        labels=labels,
        title_contains=title_contains,
        text_contains=text_contains,
        created_after=created_after,
        created_before=created_before,
        updated_after=updated_after,
        updated_before=updated_before,
    )
    params: dict[str, object] = {
        "cql": compiled_cql,
        "limit": limit,
    }
    if cursor:
        params["cursor"] = cursor

    response = requests.get(
        urljoin(base_url.rstrip("/") + "/", "wiki/rest/api/search"),
        headers={"Accept": "application/json"},
        params=params,
        auth=(username, token),
        timeout=60,
    )
    response.raise_for_status()
    payload = response.json()
    return {
        "query": query,
        "cql": compiled_cql,
        "limit": limit,
        "cursor": cursor,
        "results": payload.get("results", []),
        "next_cursor": _next_cursor(payload),
    }


def _slugify(value: str) -> str:
    normalized = re.sub(r"[^A-Za-z0-9._-]+", "-", value).strip("-").lower()
    return normalized or "page"


def _page_url(base_url: str, page: dict[str, object]) -> str | None:
    links = page.get("_links", {}) if isinstance(page, dict) else {}
    webui = links.get("webui") if isinstance(links, dict) else None
    if isinstance(webui, str) and webui:
        return urljoin(base_url, webui)
    return None


def _quote_cql(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def _build_cql(
    *,
    query: str | None,
    space: str | None,
    content_type: str | None,
    labels: list[str] | None,
    title_contains: str | None,
    text_contains: str | None,
    created_after: str | None,
    created_before: str | None,
    updated_after: str | None,
    updated_before: str | None,
) -> str:
    clauses: list[str] = []
    effective_text = text_contains or query
    if effective_text:
        clauses.append(f"text ~ {_quote_cql(effective_text)}")
    if title_contains:
        clauses.append(f"title ~ {_quote_cql(title_contains)}")
    if space:
        clauses.append(f"space = {_quote_cql(space)}")
    if content_type:
        clauses.append(f"type = {_quote_cql(content_type)}")
    for label in labels or []:
        clauses.append(f"label = {_quote_cql(label)}")
    if created_after:
        clauses.append(f'created >= {_quote_cql(created_after)}')
    if created_before:
        clauses.append(f'created <= {_quote_cql(created_before)}')
    if updated_after:
        clauses.append(f'lastmodified >= {_quote_cql(updated_after)}')
    if updated_before:
        clauses.append(f'lastmodified <= {_quote_cql(updated_before)}')
    if not clauses:
        raise ValueError("confluence search requires a query, --text-contains, --title-contains, or --cql")
    return " AND ".join(clauses)


def _next_cursor(payload: dict[str, object]) -> str | None:
    links = payload.get("_links", {}) if isinstance(payload, dict) else {}
    next_link = links.get("next") if isinstance(links, dict) else None
    if not isinstance(next_link, str) or "cursor=" not in next_link:
        return None
    return next_link.rsplit("cursor=", 1)[-1].split("&", 1)[0]


def confluence_storage_to_markdown(payload: str) -> str:
    parser = _ConfluenceStorageParser()
    parser.feed(payload)
    parser.close()
    return parser.render()


class _ConfluenceStorageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.list_stack: list[str] = []
        self.link_stack: list[str | None] = []
        self.blockquote_depth = 0
        self.preformatted = False
        self.code_block = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        handler = _CONFLUENCE_START.get(tag)
        if handler is not None:
            handler(self, attrs)

    def handle_endtag(self, tag: str) -> None:
        handler = _CONFLUENCE_END.get(tag)
        if handler is not None:
            handler(self)

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
        if self.preformatted:
            return
        self.parts.append("`")

    def _start_pre(self, _attrs: list[tuple[str, str | None]]) -> None:
        self._ensure_block_break()
        self.preformatted = True
        self.code_block = True
        self.parts.append("```\n")

    def _start_heading(self, _attrs: list[tuple[str, str | None]], tag: str = "h1") -> None:
        self._ensure_block_break()
        self.parts.append("#" * int(tag[1]) + " ")

    def _start_list(self, _attrs: list[tuple[str, str | None]], tag: str = "ul") -> None:
        self._ensure_block_break()
        self.list_stack.append(tag)

    def _start_li(self, _attrs: list[tuple[str, str | None]]) -> None:
        indent = "  " * max(len(self.list_stack) - 1, 0)
        marker = "- " if (self.list_stack[-1:] and self.list_stack[-1] == "ul") else "1. "
        self.parts.append(f"{indent}{marker}")

    def _start_blockquote(self, _attrs: list[tuple[str, str | None]]) -> None:
        self._ensure_block_break()
        self.blockquote_depth += 1
        self.parts.append("> " * self.blockquote_depth)

    def _start_a(self, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = dict(attrs)
        self.link_stack.append(attrs_dict.get("href"))
        self.parts.append("[")

    def _start_hr(self, _attrs: list[tuple[str, str | None]]) -> None:
        self._ensure_block_break()
        self.parts.append("---\n\n")

    def _start_structured_macro(self, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = dict(attrs)
        if attrs_dict.get("ac:name") in {"code", "noformat"}:
            self._ensure_block_break()
            self.preformatted = True
            self.code_block = True
            self.parts.append("```\n")

    # -- End-tag handlers --------------------------------------------------

    def _end_block(self) -> None:
        self._ensure_block_break()

    def _end_bold(self) -> None:
        self.parts.append("**")

    def _end_italic(self) -> None:
        self.parts.append("*")

    def _end_code(self) -> None:
        if self.preformatted:
            return
        self.parts.append("`")

    def _end_pre(self) -> None:
        self.parts.append("\n```")
        self.preformatted = False
        self.code_block = False
        self._ensure_block_break()

    def _end_heading(self) -> None:
        self._ensure_block_break()

    def _end_list(self) -> None:
        if self.list_stack:
            self.list_stack.pop()
        self._ensure_block_break()

    def _end_li(self) -> None:
        self.parts.append("\n")

    def _end_blockquote(self) -> None:
        self.blockquote_depth = max(self.blockquote_depth - 1, 0)
        self._ensure_block_break()

    def _end_a(self) -> None:
        href = self.link_stack.pop() if self.link_stack else None
        self.parts.append(f"]({href})" if href else "]")

    def _end_structured_macro(self) -> None:
        if self.code_block:
            self.parts.append("\n```")
            self.preformatted = False
            self.code_block = False
            self._ensure_block_break()

    def handle_data(self, data: str) -> None:
        if not data:
            return
        text = unescape(data)
        if self.preformatted:
            self.parts.append(text)
            return
        collapsed = re.sub(r"\s+", " ", text)
        if collapsed.strip():
            self.parts.append(collapsed)

    def render(self) -> str:
        text = "".join(self.parts)
        text = text.replace("\\n", "\n")
        text = re.sub(r">\s*\n\n", "> ", text)
        text = _normalize_task_artifacts(text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r"[ \t]+\n", "\n", text)
        return text.strip() or "No content."

    def _ensure_block_break(self) -> None:
        current = "".join(self.parts[-2:])
        if not current.endswith("\n\n"):
            if current.endswith("\n"):
                self.parts.append("\n")
            else:
                self.parts.append("\n\n")


def _normalize_task_artifacts(text: str) -> str:
    """Normalize Confluence task list artifacts into Markdown checkboxes."""
    text = re.sub(
        r"\n\s*\d+\s*\n(incomplete|complete)\s*\n([^\n]+?)(?:\n\s*\n|\Z)",
        lambda match: "\n- [{}] {}\n\n".format(" " if match.group(1) == "incomplete" else "x", match.group(2).strip()),
        text,
        flags=re.IGNORECASE,
    )
    return text


# -- Confluence parser dispatch tables -----------------------------------

def _make_confluence_heading_start(t: str):  # noqa: ANN202
    """Create a start-tag handler for heading ``t`` (e.g. ``h1``)."""
    def handler(self: _ConfluenceStorageParser, _attrs: list[tuple[str, str | None]]) -> None:
        self._start_heading(_attrs, tag=t)
    return handler


def _make_confluence_list_start(t: str):  # noqa: ANN202
    """Create a start-tag handler for list type ``t`` (``ul`` or ``ol``)."""
    def handler(self: _ConfluenceStorageParser, _attrs: list[tuple[str, str | None]]) -> None:
        self._start_list(_attrs, tag=t)
    return handler


_CONFLUENCE_START: dict[str, Any] = {
    "p": _ConfluenceStorageParser._start_block,
    "div": _ConfluenceStorageParser._start_block,
    "br": _ConfluenceStorageParser._start_br,
    "strong": _ConfluenceStorageParser._start_bold,
    "b": _ConfluenceStorageParser._start_bold,
    "em": _ConfluenceStorageParser._start_italic,
    "i": _ConfluenceStorageParser._start_italic,
    "code": _ConfluenceStorageParser._start_code,
    "pre": _ConfluenceStorageParser._start_pre,
    "li": _ConfluenceStorageParser._start_li,
    "blockquote": _ConfluenceStorageParser._start_blockquote,
    "a": _ConfluenceStorageParser._start_a,
    "hr": _ConfluenceStorageParser._start_hr,
    "ac:structured-macro": _ConfluenceStorageParser._start_structured_macro,
    **{f"h{i}": _make_confluence_heading_start(f"h{i}") for i in range(1, 7)},
    "ul": _make_confluence_list_start("ul"),
    "ol": _make_confluence_list_start("ol"),
}

_CONFLUENCE_END: dict[str, Any] = {
    "p": _ConfluenceStorageParser._end_block,
    "div": _ConfluenceStorageParser._end_block,
    "strong": _ConfluenceStorageParser._end_bold,
    "b": _ConfluenceStorageParser._end_bold,
    "em": _ConfluenceStorageParser._end_italic,
    "i": _ConfluenceStorageParser._end_italic,
    "code": _ConfluenceStorageParser._end_code,
    "pre": _ConfluenceStorageParser._end_pre,
    "li": _ConfluenceStorageParser._end_li,
    "blockquote": _ConfluenceStorageParser._end_blockquote,
    "a": _ConfluenceStorageParser._end_a,
    "ac:structured-macro": _ConfluenceStorageParser._end_structured_macro,
    "ul": _ConfluenceStorageParser._end_list,
    "ol": _ConfluenceStorageParser._end_list,
    **{f"h{i}": _ConfluenceStorageParser._end_heading for i in range(1, 7)},
}
