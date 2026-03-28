"""Brave Search API integration."""

from __future__ import annotations

from urllib.parse import urlparse

import requests

from ..errors import KnowledgeError


_BRAVE_WEB_SEARCH_URL = "https://api.search.brave.com/res/v1/web/search"


def search_brave(
    query: str,
    *,
    api_key: str,
    count: int = 10,
) -> dict[str, object]:
    """Query the official Brave Web Search API and normalize the response."""
    if not api_key.strip():
        raise KnowledgeError("Brave Search API key is empty")

    try:
        response = requests.get(
            _BRAVE_WEB_SEARCH_URL,
            params={"q": query, "count": min(max(count, 1), 20)},
            headers={
                "Accept": "application/json",
                "X-Subscription-Token": api_key,
            },
            timeout=60,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise KnowledgeError("Brave Search API request failed") from exc

    payload = response.json()
    results = _normalize_results(payload)
    query_info = payload.get("query", {}) if isinstance(payload, dict) else {}
    return {
        "query": query,
        "count": min(max(count, 1), 20),
        "results": results,
        "more_results_available": bool(query_info.get("more_results_available", False)),
    }


def _normalize_results(payload: object) -> list[dict[str, str]]:
    """Convert Brave API payload into a flat result list."""
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
        source = str(item.get("meta_url", {}).get("hostname") if isinstance(item.get("meta_url"), dict) else "" or _hostname(url)).strip()
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
    """Pull result items from the Brave Search API envelope."""
    if not isinstance(payload, dict):
        return []
    web_payload = payload.get("web")
    if isinstance(web_payload, dict):
        results = web_payload.get("results")
        if isinstance(results, list):
            return results
    results = payload.get("results")
    return results if isinstance(results, list) else []


def _hostname(url: str) -> str:
    """Return a host label for display."""
    parsed = urlparse(url)
    return parsed.netloc
