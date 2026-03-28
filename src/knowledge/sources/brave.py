"""Brave Search integration via the ``bx`` CLI."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from html import unescape
from urllib.parse import urlparse

import requests

from ..errors import KnowledgeError


def search_brave(
    query: str,
    *,
    count: int = 10,
) -> dict[str, object]:
    """Run ``bx web`` and normalize the JSON response for the CLI."""
    command = [
        shutil.which("bx") or "bx",
        "web",
        "-q",
        query,
        "--count",
        str(count),
        "--format",
        "json",
    ]
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
            timeout=60,
        )
    except FileNotFoundError as exc:
        return _search_brave_html(query, count=count)
    except subprocess.TimeoutExpired as exc:
        raise KnowledgeError("Brave Search request timed out") from exc

    if result.returncode != 0:
        return _search_brave_html(query, count=count)

    try:
        payload = json.loads(result.stdout or "{}")
    except json.JSONDecodeError as exc:
        raise KnowledgeError("Brave Search returned invalid JSON") from exc

    results = _normalize_results(payload)
    return {
        "query": query,
        "count": count,
        "results": results,
    }


def _normalize_results(payload: object) -> list[dict[str, str]]:
    """Convert different Brave JSON payload shapes into a flat result list."""
    items = _extract_items(payload)
    normalized: list[dict[str, str]] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        title = str(item.get("title") or item.get("name") or "").strip()
        url = str(item.get("url") or item.get("link") or "").strip()
        if not title and not url:
            continue
        description = str(item.get("description") or item.get("snippet") or item.get("summary") or "").strip()
        source = str(item.get("source") or item.get("hostname") or _hostname(url)).strip()
        normalized.append(
            {
                "title": title or url,
                "url": url,
                "description": description,
                "source": source,
            }
        )
    return normalized


def _extract_items(payload: object) -> list[object]:
    """Pull result items from the common ``bx web`` JSON envelopes."""
    if isinstance(payload, list):
        return payload
    if not isinstance(payload, dict):
        return []

    candidates = [
        payload.get("results"),
        payload.get("items"),
        (payload.get("web") or {}).get("results") if isinstance(payload.get("web"), dict) else None,
        (payload.get("web") or {}).get("items") if isinstance(payload.get("web"), dict) else None,
    ]
    for candidate in candidates:
        if isinstance(candidate, list):
            return candidate
    return []


def _hostname(url: str) -> str:
    """Return a host label for display."""
    parsed = urlparse(url)
    return parsed.netloc


def _search_brave_html(query: str, *, count: int) -> dict[str, object]:
    """Fallback search against Brave Search HTML when ``bx`` is unavailable."""
    try:
        response = requests.get(
            "https://search.brave.com/search",
            params={"q": query},
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=30,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise KnowledgeError("Brave Search fallback request failed") from exc

    results = _parse_brave_html(response.text, limit=count)
    return {
        "query": query,
        "count": count,
        "results": results,
    }


def _parse_brave_html(html: str, *, limit: int) -> list[dict[str, str]]:
    """Extract top web results from Brave Search HTML."""
    results: list[dict[str, str]] = []
    seen_urls: set[str] = set()
    pattern = re.compile(
        r'<a href="(?P<url>https?://[^"]+)"[^>]*class="[^"]*\bl1\b[^"]*"[^>]*>.*?'
        r'<div class="desktop-small-semibold[^"]*">(?P<source>.*?)</div>.*?'
        r'<div class="title [^"]*"[^>]*title="(?P<title_attr>[^"]+)">(?P<title_inner>.*?)</div>'
        r'.*?</a>',
        flags=re.DOTALL,
    )
    for match in pattern.finditer(html):
        if not match:
            continue
        url = unescape(match.group("url")).strip()
        if not url or url in seen_urls:
            continue
        seen_urls.add(url)
        title = _strip_tags(match.group("title_attr") or match.group("title_inner") or "").strip()
        tail = html[match.end() : match.end() + 1500]
        desc_match = re.search(r'<div class="content [^"]*">(?P<desc>.*?)</div>', tail, flags=re.DOTALL)
        description = _strip_tags(desc_match.group("desc") if desc_match else "").strip()
        source = _strip_tags(match.group("source") or "").strip() or _hostname(url)
        results.append(
            {
                "title": title or url,
                "url": url,
                "description": description,
                "source": source,
            }
        )
        if len(results) >= limit:
            break
    return results


def _strip_tags(text: str) -> str:
    """Remove HTML tags and collapse whitespace."""
    clean = re.sub(r"<[^>]+>", "", text)
    clean = unescape(clean)
    return re.sub(r"\s+", " ", clean).strip()
