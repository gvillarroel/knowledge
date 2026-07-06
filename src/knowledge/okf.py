from __future__ import annotations

import re
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import yaml


OKF_VERSION = "0.1"

SOURCE_TYPE_CONCEPT_TYPES = {
    "aha": "Aha Feature",
    "arxiv": "arXiv Paper",
    "confluence": "Confluence Page",
    "github": "Repository File",
    "google_releases": "Google Cloud Release Note",
    "jira": "Jira Issue",
    "site": "Web Page",
    "television": "Television Channel",
    "video": "Video Transcript",
}

RESOURCE_FIELDS = (
    "resource",
    "source_url",
    "web_url",
    "url",
    "entry_url",
    "pdf_url",
    "feed_url",
)

TIMESTAMP_FIELDS = (
    "timestamp",
    "updated_at",
    "entry_updated",
    "updated",
    "created_at",
    "published",
    "last_synced_at",
)

TAG_FIELDS = (
    "tags",
    "labels",
    "products",
    "categories",
    "primary_category",
)

OKF_FIELD_ORDER = (
    "type",
    "title",
    "description",
    "resource",
    "tags",
    "timestamp",
)


def apply_okf_frontmatter(
    frontmatter: dict[str, Any],
    *,
    source: dict[str, Any] | None = None,
    body: str = "",
    fallback_title: str | None = None,
) -> dict[str, Any]:
    """Return frontmatter enriched with Open Knowledge Format v0.1 fields."""
    normalized = dict(frontmatter)
    source = source or {}

    if not _has_value(normalized.get("type")):
        normalized["type"] = _concept_type(source)
    if not _has_value(normalized.get("title")):
        title = source.get("title") or fallback_title
        if _has_value(title):
            normalized["title"] = str(title)
    if not _has_value(normalized.get("description")):
        description = _description_from_body(body)
        if description:
            normalized["description"] = description
    if not _has_value(normalized.get("resource")):
        resource = _resource_from(normalized, source)
        if resource:
            normalized["resource"] = resource
    if not _has_value(normalized.get("timestamp")):
        timestamp = _timestamp_from(normalized, source)
        if timestamp:
            normalized["timestamp"] = timestamp

    tags = _tags_from(normalized, source)
    if tags:
        normalized["tags"] = tags

    return _order_frontmatter(normalized)


def render_okf_markdown(
    frontmatter: dict[str, Any],
    body: str,
    *,
    source: dict[str, Any] | None = None,
    fallback_title: str | None = None,
) -> str:
    """Render a Markdown document with OKF-compatible YAML frontmatter."""
    normalized = apply_okf_frontmatter(
        frontmatter,
        source=source,
        body=body,
        fallback_title=fallback_title,
    )
    return (
        "---\n"
        + yaml.safe_dump(normalized, sort_keys=False, allow_unicode=False).strip()
        + "\n---\n\n"
        + body.rstrip()
        + "\n"
    )


def ensure_markdown_file_okf(
    path: Path,
    *,
    source: dict[str, Any] | None = None,
    fallback_title: str | None = None,
) -> bool:
    """Rewrite a Markdown file with OKF fields when they are missing."""
    text = path.read_text(encoding="utf-8", errors="replace")
    frontmatter, body, has_frontmatter = split_frontmatter(text)
    effective_body = body if has_frontmatter else text
    normalized = apply_okf_frontmatter(
        frontmatter,
        source=source,
        body=effective_body,
        fallback_title=fallback_title or path.stem,
    )
    if has_frontmatter and normalized == _order_frontmatter(frontmatter):
        return False
    path.write_text(render_okf_markdown(normalized, effective_body, source=source), encoding="utf-8")
    return True


def split_frontmatter(text: str) -> tuple[dict[str, Any], str, bool]:
    """Split a Markdown document into YAML frontmatter and body."""
    if not text.startswith("---\n"):
        return {}, text, False
    marker = "\n---\n"
    end_index = text.find(marker, 4)
    if end_index == -1:
        return {}, text, False
    raw_frontmatter = text[4:end_index]
    body = text[end_index + len(marker):]
    try:
        payload = yaml.safe_load(raw_frontmatter)
    except yaml.YAMLError:
        return {}, text, False
    if not isinstance(payload, dict):
        return {}, text, False
    return payload, body.lstrip("\n"), True


def _concept_type(source: dict[str, Any]) -> str:
    source_type = str(source.get("type") or "")
    return SOURCE_TYPE_CONCEPT_TYPES.get(source_type, "Reference")


def _resource_from(frontmatter: dict[str, Any], source: dict[str, Any]) -> str | None:
    for field in RESOURCE_FIELDS:
        value = frontmatter.get(field)
        if _is_uri(value):
            return str(value)
    config = source.get("config")
    if isinstance(config, dict):
        for field in ("url", "repo_url", "base_url", "feed_url"):
            value = config.get(field)
            if _is_uri(value):
                return str(value)
    title = source.get("title")
    if _is_uri(title):
        return str(title)
    return None


def _timestamp_from(frontmatter: dict[str, Any], source: dict[str, Any]) -> str | None:
    for field in TIMESTAMP_FIELDS:
        value = frontmatter.get(field)
        if _has_value(value):
            return str(value)
    for field in ("updated_at", "last_synced_at", "created_at"):
        value = source.get(field)
        if _has_value(value):
            return str(value)
    return None


def _tags_from(frontmatter: dict[str, Any], source: dict[str, Any]) -> list[str]:
    tags: list[str] = []
    for field in TAG_FIELDS:
        _extend_tags(tags, frontmatter.get(field))
    _extend_tags(tags, source.get("type"))
    _extend_tags(tags, source.get("key") or frontmatter.get("knowledge_key"))
    return _dedupe_tags(tags)


def _extend_tags(tags: list[str], value: Any) -> None:
    if value is None:
        return
    if isinstance(value, (list, tuple, set)):
        for item in value:
            _extend_tags(tags, item)
        return
    tag = _normalize_tag(str(value))
    if tag:
        tags.append(tag)


def _dedupe_tags(tags: list[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for tag in tags:
        if tag in seen:
            continue
        seen.add(tag)
        deduped.append(tag)
    return deduped


def _normalize_tag(value: str) -> str:
    normalized = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip().lower()).strip("-")
    return normalized


def _description_from_body(body: str) -> str | None:
    in_code = False
    for raw_line in body.splitlines():
        line = raw_line.strip()
        if line.startswith("```"):
            in_code = not in_code
            continue
        if in_code or not line or line.startswith("#"):
            continue
        if line.startswith(("-", "*", ">")):
            line = line.lstrip("-*> ").strip()
        line = re.sub(r"\s+", " ", line)
        if not line:
            continue
        return line[:180].rstrip()
    return None


def _order_frontmatter(frontmatter: dict[str, Any]) -> dict[str, Any]:
    ordered: dict[str, Any] = {}
    for field in OKF_FIELD_ORDER:
        if field in frontmatter and _has_value(frontmatter[field]):
            ordered[field] = frontmatter[field]
    for key, value in frontmatter.items():
        if key not in ordered:
            ordered[key] = value
    return ordered


def _has_value(value: Any) -> bool:
    return value is not None and value != "" and value != []


def _is_uri(value: Any) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    parsed = urlparse(value)
    return bool(parsed.scheme and parsed.netloc)
