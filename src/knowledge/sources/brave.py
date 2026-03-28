"""Brave Search integration via the ``bx`` CLI."""

from __future__ import annotations

import json
import subprocess
from urllib.parse import urlparse

from ..errors import KnowledgeError


def search_brave(
    query: str,
    *,
    count: int = 10,
) -> dict[str, object]:
    """Run ``bx web`` and normalize the JSON response for the CLI."""
    command = [
        "bx",
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
        raise KnowledgeError("Brave Search CLI `bx` is not installed or not on PATH") from exc
    except subprocess.TimeoutExpired as exc:
        raise KnowledgeError("Brave Search request timed out") from exc

    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip() or f"bx exited with status {result.returncode}"
        raise KnowledgeError(f"Brave Search failed: {detail}")

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
