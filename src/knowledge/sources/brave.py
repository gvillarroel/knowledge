"""Brave Search API integration."""

from __future__ import annotations

from typing import Any
from urllib.parse import urlparse

import requests

from ..errors import KnowledgeError


_BRAVE_WEB_SEARCH_URL = "https://api.search.brave.com/res/v1/web/search"
_RESULT_SECTION_KEYS = ("web", "news", "videos", "locations", "discussions", "faq", "infobox", "rich")
_RESULT_LIST_KEYS = ("results", "items", "entities", "places")
_RESULT_QUERY_KEYS = (
    "country",
    "search_lang",
    "ui_lang",
    "safesearch",
    "spellcheck",
    "freshness",
    "text_decorations",
    "result_filter",
    "units",
    "goggles",
    "extra_snippets",
    "summary",
    "enable_rich_callback",
    "include_fetch_metadata",
    "operators",
)
_RESULT_HEADER_KEYS = (
    "loc_lat",
    "loc_long",
    "loc_timezone",
    "loc_city",
    "loc_state",
    "loc_state_name",
    "loc_country",
    "loc_postal_code",
    "api_version",
    "accept",
    "cache_control",
    "user_agent",
)
_HEADER_NAME_MAP = {
    "loc_lat": "X-Loc-Lat",
    "loc_long": "X-Loc-Long",
    "loc_timezone": "X-Loc-Timezone",
    "loc_city": "X-Loc-City",
    "loc_state": "X-Loc-State",
    "loc_state_name": "X-Loc-State-Name",
    "loc_country": "X-Loc-Country",
    "loc_postal_code": "X-Loc-Postal-Code",
    "api_version": "Api-Version",
    "accept": "Accept",
    "cache_control": "Cache-Control",
    "user_agent": "User-Agent",
}


def search_brave(
    query: str,
    *,
    api_key: str,
    options: dict[str, object] | None = None,
) -> dict[str, object]:
    """Query the official Brave Web Search API and normalize the response."""
    if not api_key.strip():
        raise KnowledgeError("Brave Search API key is empty")

    normalized_options = options or {}
    params = _build_params(query, normalized_options)
    headers = _build_headers(api_key, normalized_options)

    try:
        response = requests.get(
            _BRAVE_WEB_SEARCH_URL,
            params=params,
            headers=headers,
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
        "count": params["count"],
        "offset": params["offset"],
        "results": results,
        "more_results_available": bool(query_info.get("more_results_available", False)),
    }


def _build_params(query: str, options: dict[str, object]) -> dict[str, object]:
    """Build Brave query parameters from CLI options."""
    params: dict[str, object] = {
        "q": query,
        "count": min(max(int(options.get("count", 10) or 10), 1), 20),
        "offset": min(max(int(options.get("offset", 0) or 0), 0), 9),
    }
    for key in _RESULT_QUERY_KEYS:
        value = options.get(key)
        if value is None:
            continue
        params[key] = _serialize_param_value(key, value)
    return params


def _build_headers(api_key: str, options: dict[str, object]) -> dict[str, str]:
    """Build Brave request headers from CLI options."""
    headers = {
        "Accept": str(options.get("accept") or "application/json"),
        "X-Subscription-Token": api_key,
    }
    for key in _RESULT_HEADER_KEYS:
        if key == "accept":
            continue
        value = options.get(key)
        if value is None:
            continue
        headers[_HEADER_NAME_MAP[key]] = _serialize_header_value(value)
    return headers


def _serialize_param_value(key: str, value: object) -> object:
    """Convert CLI option values into request-safe Brave parameter values."""
    if isinstance(value, bool):
        return "true" if value else "false"
    if key == "result_filter" and isinstance(value, list):
        return ",".join(str(item) for item in value)
    if key == "goggles" and isinstance(value, list):
        return [str(item) for item in value]
    return value


def _serialize_header_value(value: object) -> str:
    """Convert header values to the string form expected by requests."""
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def _normalize_results(payload: object) -> list[dict[str, str]]:
    """Convert Brave API payload into a flat result list."""
    normalized: list[dict[str, str]] = []
    for result_type, item in _extract_items(payload):
        if not isinstance(item, dict):
            continue
        title = _normalize_title(item)
        url = _normalize_url(item)
        description = _normalize_description(item)
        source = _normalize_source(item, url, result_type)
        if not title and not url and not description:
            continue
        normalized.append(
            {
                "title": title or description or url or result_type,
                "url": url,
                "description": description,
                "source": source,
                "result_type": result_type,
            }
        )
    return normalized


def _extract_items(payload: object) -> list[tuple[str, object]]:
    """Pull result items from the Brave Search API envelope."""
    if not isinstance(payload, dict):
        return []

    items: list[tuple[str, object]] = []
    for section_name in _RESULT_SECTION_KEYS:
        section = payload.get(section_name)
        if not isinstance(section, dict):
            continue
        section_items = _extract_section_items(section_name, section)
        if section_items:
            items.extend(section_items)
            continue
        if _looks_like_result(section):
            items.append((section_name, section))
    results = payload.get("results")
    if isinstance(results, list):
        items.extend(("web", item) for item in results)
    return items


def _extract_section_items(section_name: str, section: dict[str, Any]) -> list[tuple[str, object]]:
    """Extract result items from one Brave response section."""
    for key in _RESULT_LIST_KEYS:
        value = section.get(key)
        if isinstance(value, list):
            return [(section_name, item) for item in value]
    return []


def _looks_like_result(item: dict[str, Any]) -> bool:
    """Return True when the section itself resembles a displayable result."""
    return any(item.get(field) for field in ("title", "name", "url", "link", "description", "snippet"))


def _normalize_title(item: dict[str, Any]) -> str:
    """Choose the most useful result title."""
    return str(
        item.get("title")
        or item.get("name")
        or item.get("question")
        or item.get("label")
        or item.get("city")
        or ""
    ).strip()


def _normalize_url(item: dict[str, Any]) -> str:
    """Choose the best URL-like field for the result."""
    for key in ("url", "link"):
        value = item.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    profile = item.get("profile")
    if isinstance(profile, dict):
        for key in ("url", "long_url"):
            value = profile.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    return ""


def _normalize_description(item: dict[str, Any]) -> str:
    """Choose a readable result description."""
    for key in ("description", "snippet", "summary", "article", "answer"):
        value = item.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    address = item.get("address")
    if isinstance(address, dict):
        parts = [address.get(part) for part in ("street_address", "locality", "region", "country")]
        rendered = ", ".join(str(part).strip() for part in parts if isinstance(part, str) and part.strip())
        if rendered:
            return rendered
    return ""


def _normalize_source(item: dict[str, Any], url: str, result_type: str) -> str:
    """Choose a short source label for a result."""
    meta_url = item.get("meta_url")
    if isinstance(meta_url, dict):
        hostname = meta_url.get("hostname")
        if isinstance(hostname, str) and hostname.strip():
            return hostname.strip()
    for key in ("source", "provider", "type"):
        value = item.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    host = _hostname(url)
    return host or result_type


def _hostname(url: str) -> str:
    """Return a host label for display."""
    parsed = urlparse(url)
    return parsed.netloc
