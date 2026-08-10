from __future__ import annotations

from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from html.parser import HTMLParser
import re
import time
from xml.etree import ElementTree
from urllib.parse import quote, urlparse

import requests

from .base import SourceAdapter
from ..store import KnowledgeStore


ARXIV_API_URL = "https://export.arxiv.org/api/query"
ATOM_NAMESPACE = {"atom": "http://www.w3.org/2005/Atom", "opensearch": "http://a9.com/-/spec/opensearch/1.1/"}
ARXIV_USER_AGENT = "knowledge-cli/0.1.0"
ARXIV_RETRY_STATUSES = {429, 500, 502, 503, 504}
ARXIV_MAX_ATTEMPTS = 3
ARXIV_ID_RE = re.compile(
    r"^(?:arxiv:)?(?P<identifier>(?:\d{4}\.\d{4,5}|[a-z0-9.-]+/\d{7})(?:v\d+)?)$",
    re.IGNORECASE,
)
ARXIV_HOSTS = {"arxiv.org", "export.arxiv.org", "www.arxiv.org"}
ALPHAXIV_HOSTS = {"alphaxiv.org", "www.alphaxiv.org"}
HTML_VOID_TAGS = {
    "area",
    "base",
    "br",
    "col",
    "embed",
    "hr",
    "img",
    "input",
    "link",
    "meta",
    "param",
    "source",
    "track",
    "wbr",
}


class ArxivSource(SourceAdapter):
    def sync(self) -> dict[str, object]:
        url = canonical_arxiv_url(str(self.config["url"]))
        paper_id = extract_arxiv_id(url)
        api_url = f"{ARXIV_API_URL}?id_list={quote(paper_id)}"

        try:
            response = _request_arxiv(api_url)
            feed = _parse_arxiv_feed(response.text)
            entry = next(iter(feed.get("entries", [])), {})
        except requests.RequestException:
            entry = _fetch_arxiv_html_entry(paper_id)
        return self.sync_from_entry(entry)

    def sync_from_entry(self, entry: dict[str, object]) -> dict[str, object]:
        """Persist one already-fetched arXiv entry for this registered source."""
        url = canonical_arxiv_url(str(self.config["url"]))
        paper_id = extract_arxiv_id(url)
        title = entry.get("title") or self.source.get("title") or self.source["id"]
        summary = str(entry.get("summary") or "").strip()
        authors = [author for author in entry.get("authors", []) if author]
        categories = [category for category in entry.get("categories", []) if category]
        links = entry.get("links", {})
        frontmatter = {
            "title": title,
            "knowledge_key": self.source["key"],
            "source_id": self.source["id"],
            "source_type": self.source["type"],
            "paper_id": paper_id,
            "source_url": url,
            "authors": authors,
            "published": entry.get("published"),
            "updated": entry.get("updated"),
            "categories": categories,
            "primary_category": entry.get("primary_category"),
            "pdf_url": entry.get("pdf_url"),
            "links": links,
        }
        lines = [f"# {title}"]
        if authors:
            lines.extend(["", "Authors: " + ", ".join(str(author) for author in authors)])
        if summary:
            lines.extend(["", "## Summary", "", summary])

        self.config["url"] = url
        self.source.update(
            {
                "title": title,
                "paper_id": paper_id,
                "authors": authors,
                "categories": categories,
                "published": entry.get("published"),
                "updated": entry.get("updated"),
                "pdf_url": entry.get("pdf_url"),
            }
        )
        self.clear_source_dir()
        self.write_markdown(self.raw_dir / "paper.md", frontmatter, "\n".join(lines).strip())
        return self.finalize_sync(
            {
                "paper_id": paper_id,
                "documents": 1,
                "library_dir": str(self.raw_dir),
                "metadata_source": entry.get("_metadata_source", "arxiv-api"),
            }
        )

    def _extract_paper_id(self, url: str) -> str:
        """Extract the stable arXiv identifier from a supported URL."""
        return extract_arxiv_id(url)


def extract_arxiv_id(value: str) -> str:
    """Return a validated arXiv identifier from an arXiv or alphaXiv URL."""
    candidate = value.strip()
    parsed = urlparse(candidate)
    if parsed.scheme or parsed.netloc:
        host = (parsed.hostname or "").lower()
        parts = [part for part in parsed.path.split("/") if part]
        if host in ARXIV_HOSTS:
            if not parts or parts[0].lower() not in {"abs", "html", "pdf"}:
                raise ValueError(f"unsupported arXiv URL: {value}")
            candidate = "/".join(parts[1:])
        elif host in ALPHAXIV_HOSTS:
            if len(parts) < 2 or parts[0].lower() != "overview":
                raise ValueError(f"unsupported alphaXiv URL: {value}")
            candidate = "/".join(parts[1:])
        else:
            raise ValueError(f"unsupported arXiv host: {host or value}")
    candidate = candidate.removesuffix(".pdf").strip("/")
    match = ARXIV_ID_RE.fullmatch(candidate)
    if match is None:
        raise ValueError(f"invalid arXiv identifier: {value}")
    return match.group("identifier")


def canonical_arxiv_url(value: str) -> str:
    """Normalize supported arXiv and alphaXiv links to an official abstract URL."""
    return f"https://arxiv.org/abs/{extract_arxiv_id(value)}"


def versionless_arxiv_id(value: str) -> str:
    """Return an arXiv identifier without its optional version suffix."""
    return re.sub(r"v\d+$", "", extract_arxiv_id(value), flags=re.IGNORECASE)


def search_arxiv(
    query: str,
    *,
    start: int = 0,
    max_results: int = 10,
    sort_by: str = "relevance",
    sort_order: str = "descending",
) -> dict[str, object]:
    search_query = _normalize_search_query(query)
    response = _request_arxiv(
        ARXIV_API_URL,
        params={
            "search_query": search_query,
            "start": start,
            "max_results": max_results,
            "sortBy": sort_by,
            "sortOrder": sort_order,
        },
    )
    return {
        "search_query": search_query,
        **_parse_arxiv_feed(response.text),
    }


def search_arxiv_many(
    queries: list[str],
    *,
    start: int = 0,
    max_results: int = 10,
    sort_by: str = "relevance",
    sort_order: str = "descending",
    request_delay: float = 3.0,
    published_after: datetime | None = None,
) -> dict[str, object]:
    """Search several query lanes sequentially and deduplicate exact paper versions."""
    cleaned_queries = list(dict.fromkeys(query.strip() for query in queries if query.strip()))
    if not cleaned_queries:
        raise ValueError("at least one arXiv query is required")
    if request_delay < 0:
        raise ValueError("arXiv request delay must be non-negative")

    entries_by_id: dict[str, dict[str, object]] = {}
    query_results: list[dict[str, object]] = []
    for index, query in enumerate(cleaned_queries):
        if index:
            time.sleep(request_delay)
        effective_query = arxiv_submitted_after_query(query, published_after) if published_after else query
        result = search_arxiv(
            effective_query,
            start=start,
            max_results=max_results,
            sort_by=sort_by,
            sort_order=sort_order,
        )
        query_results.append(
            {
                "query": query,
                "search_query": result["search_query"],
                "total_results": result["total_results"],
                "returned_results": len(result.get("entries", [])),
                "truncated": int(result["total_results"]) > len(result.get("entries", [])),
            }
        )
        for entry in result.get("entries", []):
            if not isinstance(entry, dict) or not entry.get("id"):
                continue
            paper_id = extract_arxiv_id(str(entry["id"]))
            existing = entries_by_id.get(paper_id)
            if existing is None:
                existing = {**entry, "arxiv_id": paper_id, "matched_queries": []}
                entries_by_id[paper_id] = existing
            matched_queries = existing.setdefault("matched_queries", [])
            if isinstance(matched_queries, list) and query not in matched_queries:
                matched_queries.append(query)

    entries = list(entries_by_id.values())
    sort_field = {
        "submittedDate": "published",
        "lastUpdatedDate": "updated",
    }.get(sort_by)
    if sort_field:
        entries.sort(
            key=lambda entry: (
                str(entry.get(sort_field) or ""),
                str(entry.get("arxiv_id") or ""),
            ),
            reverse=sort_order == "descending",
        )
    return {
        "queries": cleaned_queries,
        "query_results": query_results,
        "truncated_queries": [
            result["query"] for result in query_results if result["truncated"]
        ],
        "total_results": len(entries),
        "entries": entries,
    }


def sync_arxiv_batch(
    sources: list[dict[str, object]],
    store: KnowledgeStore,
    *,
    request_delay: float = 3.0,
    batch_size: int = 50,
) -> list[dict[str, object]]:
    """Synchronize arXiv sources through compact, politely paced ID batches."""
    if request_delay < 0:
        raise ValueError("arXiv request delay must be non-negative")
    if batch_size < 1 or batch_size > 200:
        raise ValueError("arXiv batch size must be between 1 and 200")

    synced: list[dict[str, object]] = []
    for offset in range(0, len(sources), batch_size):
        if offset:
            time.sleep(request_delay)
        batch = sources[offset : offset + batch_size]
        paper_ids = [extract_arxiv_id(str(source["config"]["url"])) for source in batch]
        try:
            response = _request_arxiv(
                ARXIV_API_URL,
                params={"id_list": ",".join(paper_ids), "max_results": len(paper_ids)},
            )
            entries = {
                extract_arxiv_id(str(entry["id"])): entry
                for entry in _parse_arxiv_feed(response.text).get("entries", [])
                if isinstance(entry, dict) and entry.get("id")
            }
        except requests.RequestException:
            entries = {}
        missing = [paper_id for paper_id in paper_ids if paper_id not in entries]
        for index, paper_id in enumerate(missing):
            if index:
                time.sleep(request_delay)
            entries[paper_id] = _fetch_arxiv_html_entry(paper_id)
        for source, paper_id in zip(batch, paper_ids, strict=True):
            synced.append(ArxivSource(source, store).sync_from_entry(entries[paper_id]))
    return synced


def arxiv_submitted_after_query(query: str, boundary: datetime) -> str:
    """Constrain an arXiv query to submissions at or after a UTC boundary."""
    normalized = boundary
    if normalized.tzinfo is None:
        normalized = normalized.replace(tzinfo=timezone.utc)
    normalized = normalized.astimezone(timezone.utc)
    timestamp = normalized.strftime("%Y%m%d%H%M")
    return f"({_normalize_search_query(query)}) AND submittedDate:[{timestamp} TO 999912312359]"


def _request_arxiv(url: str, *, params: dict[str, object] | None = None) -> requests.Response:
    """Issue an arXiv request with bounded Retry-After-aware retries."""
    last_error: requests.RequestException | None = None
    for attempt in range(ARXIV_MAX_ATTEMPTS):
        try:
            response = requests.get(
                url,
                params=params,
                headers={
                    "Accept": "application/atom+xml",
                    "User-Agent": ARXIV_USER_AGENT,
                },
                timeout=60,
            )
        except requests.RequestException as exc:
            last_error = exc
            if attempt + 1 == ARXIV_MAX_ATTEMPTS:
                raise
            time.sleep(3.0 * (2**attempt))
            continue

        status_code = int(getattr(response, "status_code", 200))
        if status_code not in ARXIV_RETRY_STATUSES or attempt + 1 == ARXIV_MAX_ATTEMPTS:
            response.raise_for_status()
            return response
        time.sleep(_retry_delay(response, attempt))

    if last_error is not None:  # pragma: no cover - defensive exhaustion guard
        raise last_error
    raise RuntimeError("arXiv request retry loop exhausted")  # pragma: no cover


def _retry_delay(response: requests.Response, attempt: int) -> float:
    """Return the server-requested delay or a bounded exponential fallback."""
    headers = getattr(response, "headers", {}) or {}
    value = str(headers.get("Retry-After", "")).strip()
    if value.isdigit():
        return min(60.0, max(0.0, float(value)))
    return min(60.0, 3.0 * (2**attempt))


def _fetch_arxiv_html_entry(paper_id: str) -> dict[str, object]:
    """Fetch an exact paper from the official abstract page as an API fallback."""
    url = canonical_arxiv_url(paper_id)
    response = _request_arxiv_html(url)
    parser = _ArxivHTMLParser()
    parser.feed(response.text)
    return parser.as_entry(paper_id, url)


def _request_arxiv_html(url: str) -> requests.Response:
    """Issue an official abstract-page request with bounded retries."""
    for attempt in range(ARXIV_MAX_ATTEMPTS):
        try:
            response = requests.get(
                url,
                headers={"Accept": "text/html", "User-Agent": ARXIV_USER_AGENT},
                timeout=60,
            )
        except requests.RequestException:
            if attempt + 1 == ARXIV_MAX_ATTEMPTS:
                raise
            time.sleep(3.0 * (2**attempt))
            continue
        status_code = int(getattr(response, "status_code", 200))
        if status_code not in ARXIV_RETRY_STATUSES or attempt + 1 == ARXIV_MAX_ATTEMPTS:
            response.raise_for_status()
            return response
        time.sleep(_retry_delay(response, attempt))
    raise RuntimeError("arXiv HTML request retry loop exhausted")  # pragma: no cover


class _ArxivHTMLParser(HTMLParser):
    """Extract authoritative citation and subject metadata from an arXiv page."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.meta: dict[str, list[str]] = {}
        self.subject_parts: list[str] = []
        self.submission_parts: list[str] = []
        self._subjects_depth = 0
        self._submission_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key: value or "" for key, value in attrs}
        if tag == "meta" and values.get("name", "").startswith("citation_"):
            self.meta.setdefault(values["name"], []).append(values.get("content", ""))
        classes = set(values.get("class", "").split())
        if tag == "td" and {"tablecell", "subjects"}.issubset(classes):
            self._subjects_depth = 1
        elif self._subjects_depth and tag not in HTML_VOID_TAGS:
            self._subjects_depth += 1
        if tag == "div" and "submission-history" in classes:
            self._submission_depth = 1
        elif self._submission_depth and tag not in HTML_VOID_TAGS:
            self._submission_depth += 1

    def handle_endtag(self, _tag: str) -> None:
        if self._subjects_depth:
            self._subjects_depth -= 1
        if self._submission_depth:
            self._submission_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._subjects_depth and data.strip():
            self.subject_parts.append(data.strip())
        if self._submission_depth and data.strip():
            self.submission_parts.append(data.strip())

    def as_entry(self, paper_id: str, url: str) -> dict[str, object]:
        """Build an API-shaped entry from collected HTML metadata."""
        title = _first(self.meta, "citation_title")
        summary = _first(self.meta, "citation_abstract")
        if not title or not summary:
            raise ValueError(f"arXiv abstract page omitted citation metadata for {paper_id}")
        authors = [_display_author(author) for author in self.meta.get("citation_author", [])]
        categories = re.findall(r"\(([a-z-]+\.[A-Za-z-]+)\)", " ".join(self.subject_parts))
        versions = _submission_versions(" ".join(self.submission_parts))
        requested_version = re.search(r"v(\d+)$", paper_id, flags=re.IGNORECASE)
        requested_number = int(requested_version.group(1)) if requested_version else max(versions, default=1)
        citation_date = _citation_date(_first(self.meta, "citation_date"))
        published = versions.get(1) or citation_date
        updated = versions.get(requested_number) or published
        pdf_url = f"https://arxiv.org/pdf/{paper_id}"
        return {
            "id": url,
            "title": title,
            "summary": summary,
            "published": published,
            "updated": updated,
            "authors": authors,
            "categories": categories,
            "primary_category": categories[0] if categories else None,
            "links": {"alternate": url, "pdf": pdf_url},
            "pdf_url": pdf_url,
            "_metadata_source": "arxiv-abs-html",
        }


def _first(values: dict[str, list[str]], key: str) -> str | None:
    items = values.get(key, [])
    return items[0].strip() if items and items[0].strip() else None


def _display_author(value: str) -> str:
    if "," not in value:
        return value.strip()
    family, given = value.split(",", 1)
    return f"{given.strip()} {family.strip()}".strip()


def _submission_versions(value: str) -> dict[int, str]:
    versions: dict[int, str] = {}
    for number, raw_date in re.findall(r"\[v(\d+)\]\s*([^([]+?)\s*\(", value):
        try:
            parsed = parsedate_to_datetime(raw_date.strip())
        except (TypeError, ValueError):
            continue
        versions[int(number)] = parsed.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    return versions


def _citation_date(value: str | None) -> str | None:
    if not value:
        return None
    try:
        parsed = datetime.strptime(value, "%Y/%m/%d").replace(tzinfo=timezone.utc)
    except ValueError:
        return None
    return parsed.isoformat().replace("+00:00", "Z")


def _normalize_search_query(query: str) -> str:
    trimmed = query.strip()
    if ":" in trimmed:
        return trimmed
    if any(ch.isspace() for ch in trimmed):
        escaped = trimmed.replace('"', '\\"')
        return f'all:"{escaped}"'
    return f"all:{trimmed}"


def _parse_arxiv_feed(payload: str) -> dict[str, object]:
    root = ElementTree.fromstring(payload)
    entries: list[dict[str, object]] = []
    for entry in root.findall("atom:entry", ATOM_NAMESPACE):
        links = {
            link.get("title") or link.get("rel") or "related": link.get("href")
            for link in entry.findall("atom:link", ATOM_NAMESPACE)
            if link.get("href")
        }
        entries.append(
            {
                "id": _text(entry, "atom:id"),
                "title": _text(entry, "atom:title"),
                "summary": _text(entry, "atom:summary"),
                "published": _text(entry, "atom:published"),
                "updated": _text(entry, "atom:updated"),
                "authors": [_text(author, "atom:name") for author in entry.findall("atom:author", ATOM_NAMESPACE)],
                "categories": [category.get("term") for category in entry.findall("atom:category", ATOM_NAMESPACE)],
                "primary_category": next(
                    (category.get("term") for category in entry.findall("atom:category", ATOM_NAMESPACE)),
                    None,
                ),
                "links": links,
                "pdf_url": links.get("pdf"),
            }
        )

    return {
        "total_results": _int_text(root, "opensearch:totalResults"),
        "start_index": _int_text(root, "opensearch:startIndex"),
        "items_per_page": _int_text(root, "opensearch:itemsPerPage"),
        "entries": entries,
    }


def _text(element: ElementTree.Element, selector: str) -> str | None:
    node = element.find(selector, ATOM_NAMESPACE)
    if node is None or node.text is None:
        return None
    return " ".join(node.text.split())


def _int_text(element: ElementTree.Element, selector: str) -> int:
    value = _text(element, selector)
    return int(value) if value is not None else 0
