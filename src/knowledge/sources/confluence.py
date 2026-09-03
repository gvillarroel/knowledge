from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
from html import unescape
from html.parser import HTMLParser
import json
import logging
from pathlib import Path
import re
from typing import Any, Iterator
from urllib.parse import parse_qs, urljoin, urlsplit

import requests

from ..errors import KnowledgeError
from .base import SourceAdapter
from .confluence_http import ConfluenceClient, ConfluenceOptions, ConfluenceRequestError, normalize_confluence_base_url
from .confluence_snapshot import ConfluenceSnapshot, atomic_json, cache_page, cached_page

_LOG = logging.getLogger(__name__)


class ConfluenceSyncError(KnowledgeError):
    """An incomplete sync with a durable report and reusable page checkpoints."""

    def __init__(self, stats: dict[str, Any]) -> None:
        self.stats = stats
        super().__init__(
            f"Confluence sync incomplete: {stats['pages']} page(s) ready, "
            f"{len(stats['failures'])} error(s). Previous files preserved. "
            f"Retry the same command. Report: {stats['report']}"
        )


class ConfluenceSource(SourceAdapter):
    """Synchronize Confluence pages with bounded downloads and resumable checkpoints."""

    def sync(self) -> dict[str, object]:
        """Publish a complete snapshot, or retain the last successful corpus on failure."""
        config = {**self.config, **self.source.get("_confluence_sync_options", {})}
        options = ConfluenceOptions.from_config(config)
        auth = self._auth()
        base_url = normalize_confluence_base_url(config["base_url"])
        scope = json.dumps(
            [str(self.store.root.resolve()), base_url, auth[0], config.get("space_key") or config.get("space"), config.get("cql")],
            sort_keys=True,
        )
        checkpoint = self.cache_dir / "confluence-v1" / hashlib.sha256(scope.encode()).hexdigest()
        report = checkpoint / "sync-report.json"
        stats: dict[str, Any] = {
            "pages": 0, "discovered": 0, "downloaded": 0, "reused": 0,
            "failures": [], "complete": False, "snapshot_schema": 1,
            "space_key": config.get("space_key") or config.get("space"),
            "cql": config.get("cql"), "raw_dir": str(self.raw_dir),
            "report": str(report), "workers": options.workers, "page_size": options.page_size,
        }
        previous_source = dict(self.source)
        owns_snapshot = False
        with ConfluenceClient(base_url, auth, options) as client:
            try:
                with ConfluenceSnapshot(self.raw_dir, self.source) as snapshot:
                    owns_snapshot = True
                    assert snapshot.stage is not None
                    with ThreadPoolExecutor(max_workers=options.workers, thread_name_prefix="confluence") as executor:
                        try:
                            self._download_batches(client, executor, snapshot.stage, checkpoint, config, stats)
                        except BaseException:
                            client.cancel()
                            executor.shutdown(wait=True, cancel_futures=True)
                            raise
                    stats.update(requests=client.requests, retries=client.retries)
                    if stats["failures"]:
                        atomic_json(report, stats)
                        raise ConfluenceSyncError(stats)
                    stats["complete"] = True
                    result = snapshot.publish(lambda: self.finalize_sync(stats))
                    # Report bookkeeping must not turn an already published corpus into failure.
                    try:
                        atomic_json(report, stats)
                    except OSError:
                        _LOG.warning("Confluence snapshot saved, but its cache report could not be updated")
                    return result
            except ConfluenceSyncError:
                raise
            except (ConfluenceRequestError, OSError, ValueError, KeyboardInterrupt, KnowledgeError) as exc:
                if not owns_snapshot:
                    raise
                self.source.clear()
                self.source.update(previous_source)
                stats.update(complete=False, requests=client.requests, retries=client.retries)
                reason = str(exc) if isinstance(exc, KnowledgeError) else type(exc).__name__
                stats["failures"].append({"phase": "sync", "error": reason})
                atomic_json(report, stats)
                raise ConfluenceSyncError(stats) from None

    def _auth(self) -> tuple[str, str]:
        return (self.store.resolve_key(self.config["username"]), self.store.resolve_key(self.config["token"]))

    def _inventory(self, client: ConfluenceClient, config: dict[str, Any]) -> Iterator[list[dict[str, Any]]]:
        options = client.options
        if config.get("cql"):
            yield from client.iter_batches(
                "rest/api/search",
                {"cql": config["cql"], "limit": min(options.page_size, options.max_pages or options.page_size),
                 "expand": "content.version"},
            )
            return
        space_key = config.get("space_key") or config.get("space")
        if not space_key:
            raise ConfluenceRequestError("Confluence sync requires a space or CQL filter")
        spaces = client.get_json("api/v2/spaces", {"keys": space_key, "limit": 2}).get("results")
        if not isinstance(spaces, list) or any(not isinstance(row, dict) for row in spaces):
            raise ConfluenceRequestError("Confluence returned a malformed space lookup")
        matches = [space for space in spaces if space.get("key") == space_key]
        if len(matches) != 1:
            raise ConfluenceRequestError("Confluence space was not found or is not uniquely accessible")
        space_id = _valid_page_id(matches[0].get("id"))
        for batch in client.iter_batches(
            "api/v2/pages",
            {"space-id": space_id, "status": "current", "subtype": "page", "limit": options.page_size},
        ):
            for page in batch:
                if str(page.get("spaceId")) != space_id:
                    raise ConfluenceRequestError("Confluence inventory returned a page outside the requested space")
            yield batch

    def _download_batches(
        self, client: ConfluenceClient, executor: ThreadPoolExecutor, stage: Path,
        checkpoint: Path, config: dict[str, Any], stats: dict[str, Any],
    ) -> None:
        seen: set[str] = set()
        for batch in self._inventory(client, config):
            selected = []
            for row in batch:
                page = row.get("content", row) if config.get("cql") else row
                if not isinstance(page, dict):
                    raise ConfluenceRequestError("Confluence search returned malformed content")
                if page.get("type", "page") != "page":
                    continue
                page_id = _valid_page_id(page.get("id"))
                if page_id in seen:
                    continue
                seen.add(page_id)
                selected.append(page)
                if client.options.max_pages and len(seen) >= client.options.max_pages:
                    break
            if batch and not selected and all(
                (row.get("content", row) if config.get("cql") else row).get("type", "page") == "page"
                for row in batch
            ):
                raise ConfluenceRequestError("Confluence pagination made no progress")
            stats["discovered"] += len(selected)
            # Bound pending futures as well as active requests, even for a large page_size.
            for offset in range(0, len(selected), client.options.workers * 2):
                pending = {
                    executor.submit(self._download_page, client, page, checkpoint, bool(config.get("refresh"))): str(page["id"])
                    for page in selected[offset:offset + client.options.workers * 2]
                }
                for future in as_completed(pending):
                    page_id = pending[future]
                    try:
                        page, reused = future.result()
                        self._write_page(stage, client.base_url, page)
                    except ConfluenceRequestError as exc:
                        stats["failures"].append({"page_id": page_id, "status": exc.status, "error": str(exc)})
                        _LOG.warning("Confluence page %s could not be downloaded: %s", page_id, exc)
                        if exc.fatal:
                            raise
                        continue
                    stats["pages"] += 1
                    stats["reused" if reused else "downloaded"] += 1
                atomic_json(Path(stats["report"]), stats)
                _LOG.info(
                    "Confluence: %d ready (%d downloaded, %d reused), %d errors",
                    stats["pages"], stats["downloaded"], stats["reused"], len(stats["failures"]),
                )
            if client.options.max_pages and len(seen) >= client.options.max_pages:
                return

    def _download_page(
        self, client: ConfluenceClient, metadata: dict[str, Any], checkpoint: Path, refresh: bool
    ) -> tuple[dict[str, Any], bool]:
        page_id = _valid_page_id(metadata.get("id"))
        path = checkpoint / f"{page_id}.json"
        page = None if refresh else cached_page(path, metadata)
        if page is not None:
            return page, True
        page = client.get_json(f"api/v2/pages/{page_id}", {"body-format": "storage"})
        if _valid_page_id(page.get("id")) != page_id:
            raise ConfluenceRequestError("Confluence page response has the wrong identity")
        if metadata.get("spaceId") is not None and page.get("spaceId") != metadata["spaceId"]:
            raise ConfluenceRequestError("Confluence page moved out of the listed space")
        if page.get("status", "current") != "current" or page.get("subtype", "page") != "page":
            raise ConfluenceRequestError("Confluence page is no longer a current published page")
        body = page.get("body")
        storage = body.get("storage") if isinstance(body, dict) else None
        if not isinstance(storage, dict) or not isinstance(storage.get("value"), str):
            raise ConfluenceRequestError("Confluence page response is missing its storage body")
        cache_page(path, page)
        return page, False

    def _write_page(self, directory: Path, base_url: str, page: dict[str, Any]) -> None:
        page_id = _valid_page_id(page["id"])
        title = str(page.get("title") or f"Page {page_id}")
        version = page.get("version") or {}
        if not isinstance(version, dict):
            raise ConfluenceRequestError("Confluence page has malformed version metadata")
        frontmatter = {
            "title": title, "knowledge_key": self.source["key"],
            "source_id": self.source["id"], "source_type": self.source["type"],
            "document_id": page_id, "space_key": self.config.get("space_key") or self.config.get("space"),
            "space_id": page.get("spaceId"), "status": page.get("status"),
            "author_id": page.get("authorId"), "owner_id": page.get("ownerId"),
            "parent_id": page.get("parentId"), "parent_type": page.get("parentType"),
            "created_at": page.get("createdAt"), "updated_at": version.get("createdAt") or page.get("updatedAt"),
            "version_number": version.get("number"), "web_url": _page_url(base_url, page),
        }
        self.write_markdown(
            directory / f"{page_id}-{_slugify(title)[:80]}.md",
            frontmatter, confluence_storage_to_markdown(page["body"]["storage"]["value"]),
        )


def _valid_page_id(value: object) -> str:
    if not isinstance(value, (str, int)) or isinstance(value, bool) or not re.fullmatch(r"[0-9]+", str(value)):
        raise ConfluenceRequestError("Confluence returned an invalid page or space ID")
    return str(value)


def search_confluence(
    *,
    base_url: str, username: str, token: str,
    query: str | None = None, cql: str | None = None, space: str | None = None,
    content_type: str | None = None, labels: list[str] | None = None,
    title_contains: str | None = None, text_contains: str | None = None,
    created_after: str | None = None, created_before: str | None = None,
    updated_after: str | None = None, updated_before: str | None = None,
    limit: int = 25, cursor: str | None = None,
    options: ConfluenceOptions | None = None,
) -> dict[str, object]:
    """Search one CQL result page with safe retries and a decoded continuation cursor."""
    if type(limit) is not int or limit < 1:
        raise ValueError("Confluence search limit must be a positive integer")
    compiled_cql = cql or _build_cql(
        query=query, space=space, content_type=content_type, labels=labels,
        title_contains=title_contains, text_contains=text_contains,
        created_after=created_after, created_before=created_before,
        updated_after=updated_after, updated_before=updated_before,
    )
    params: dict[str, Any] = {"cql": compiled_cql, "limit": min(limit, 250)}
    if cursor:
        params["cursor"] = cursor
    with ConfluenceClient(base_url, (username, token), options) as client:
        payload = client.get_json("rest/api/search", params)
        results = payload.get("results")
        if not isinstance(results, list) or any(not isinstance(row, dict) for row in results):
            raise ConfluenceRequestError("Confluence search returned malformed results")
    return {
        "query": query, "cql": compiled_cql, "limit": limit, "cursor": cursor,
        "results": results, "next_cursor": _next_cursor(payload),
    }


def _limited_confluence_rows(
    client: ConfluenceClient, path: str, params: dict[str, Any], limit: int, identity: str
) -> Iterator[dict[str, Any]]:
    if type(limit) is not int or limit < 1:
        raise ValueError("Confluence browse limit must be a positive integer")
    seen: set[str] = set()
    for batch in client.iter_batches(path, params):
        before = len(seen)
        for row in batch:
            key = str(row.get(identity) or "")
            if not key:
                raise ConfluenceRequestError("Confluence listing returned an item without an identity")
            if key in seen:
                continue
            seen.add(key)
            yield row
            if len(seen) >= limit:
                return
        if batch and len(seen) == before:
            raise ConfluenceRequestError("Confluence pagination made no progress")


def list_confluence_spaces(
    *, base_url: str, username: str, token: str, limit: int = 250,
    options: ConfluenceOptions | None = None,
) -> list[dict[str, object]]:
    """Return up to limit visible spaces with bounded pagination and retries."""
    spaces = []
    with ConfluenceClient(base_url, (username, token), options) as client:
        rows = _limited_confluence_rows(
            client, "rest/api/space", {"limit": min(limit, client.options.page_size)}, limit, "key"
        )
        for space in rows:
            spaces.append({
                "key": space.get("key", ""), "name": space.get("name", ""), "type": space.get("type", ""),
                "description": (space.get("description", {}) or {}).get("plain", {}).get("value", ""),
                "web_url": urljoin(client.base_url, f"wiki/spaces/{space['key']}"),
            })
    return spaces


def list_confluence_pages(
    *, base_url: str, username: str, token: str, space: str, limit: int = 500,
    options: ConfluenceOptions | None = None,
) -> list[dict[str, object]]:
    """Return up to limit pages with ancestor paths, without downloading their bodies."""
    pages = []
    with ConfluenceClient(base_url, (username, token), options) as client:
        rows = _limited_confluence_rows(
            client, "rest/api/content",
            {"type": "page", "spaceKey": space, "expand": "ancestors",
             "limit": min(limit, client.options.page_size)}, limit, "id",
        )
        for page in rows:
            title = page.get("title", "Untitled")
            parts = [a.get("title", "") for a in (page.get("ancestors") or []) if a.get("title")]
            parts.append(title)
            pages.append({
                "title": title, "path": "/" + "/".join(parts),
                "web_url": _page_url(client.base_url, page) or "",
                "page_id": str(page["id"]), "space": space,
            })
    return pages


def _slugify(value: str) -> str:
    normalized = re.sub(r"[^A-Za-z0-9._-]+", "-", value).strip("-").lower()
    return normalized or "page"


def _page_url(base_url: str, page: dict[str, object]) -> str | None:
    links = page.get("_links", {}) if isinstance(page, dict) else {}
    webui = links.get("webui") if isinstance(links, dict) else None
    if isinstance(webui, str) and webui:
        if webui.startswith(("/spaces/", "spaces/")):
            return urljoin(normalize_confluence_base_url(base_url), "wiki/" + webui.lstrip("/"))
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
    return parse_qs(urlsplit(next_link).query).get("cursor", [None])[0]


def _search_result_page_id(result: dict[str, object]) -> str | None:
    if not isinstance(result, dict):
        return None
    content = result.get("content")
    if isinstance(content, dict):
        content_id = content.get("id")
        if content_id:
            return str(content_id)
    result_id = result.get("id")
    return str(result_id) if result_id else None


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
