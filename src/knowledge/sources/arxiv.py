from __future__ import annotations

from xml.etree import ElementTree
from urllib.parse import quote

import requests

from .base import SourceAdapter


ARXIV_API_URL = "https://export.arxiv.org/api/query"
ATOM_NAMESPACE = {"atom": "http://www.w3.org/2005/Atom", "opensearch": "http://a9.com/-/spec/opensearch/1.1/"}


class ArxivSource(SourceAdapter):
    def sync(self) -> dict[str, object]:
        url = self.config["url"]
        paper_id = self._extract_paper_id(url)
        api_url = f"{ARXIV_API_URL}?id_list={quote(paper_id)}"

        response = requests.get(
            api_url,
            headers={"Accept": "application/atom+xml"},
            timeout=60,
        )
        response.raise_for_status()

        feed = _parse_arxiv_feed(response.text)
        entry = next(iter(feed.get("entries", [])), {})
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

        self.clear_source_dir()
        self.write_markdown(self.raw_dir / "paper.md", frontmatter, "\n".join(lines).strip())
        return self.finalize_sync(
            {
                "paper_id": paper_id,
                "documents": 1,
                "library_dir": str(self.raw_dir),
            }
        )

    def _extract_paper_id(self, url: str) -> str:
        trimmed = url.rstrip("/")
        if "/abs/" in trimmed:
            return trimmed.rsplit("/abs/", 1)[-1]
        if "/pdf/" in trimmed:
            return trimmed.rsplit("/pdf/", 1)[-1].removesuffix(".pdf")
        return trimmed.rsplit("/", 1)[-1]


def search_arxiv(
    query: str,
    *,
    start: int = 0,
    max_results: int = 10,
    sort_by: str = "relevance",
    sort_order: str = "descending",
) -> dict[str, object]:
    search_query = _normalize_search_query(query)
    response = requests.get(
        ARXIV_API_URL,
        params={
            "search_query": search_query,
            "start": start,
            "max_results": max_results,
            "sortBy": sort_by,
            "sortOrder": sort_order,
        },
        headers={"Accept": "application/atom+xml"},
        timeout=60,
    )
    response.raise_for_status()
    return {
        "search_query": search_query,
        **_parse_arxiv_feed(response.text),
    }


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
