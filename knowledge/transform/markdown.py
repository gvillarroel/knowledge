"""Markdown transformation utilities."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _slugify(text: str) -> str:
    """Convert *text* to a filesystem-safe slug."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    text = re.sub(r"^-+|-+$", "", text)
    return text or "untitled"


def build_frontmatter(meta: dict[str, Any]) -> str:
    """Render a YAML frontmatter block from *meta*."""
    import yaml  # local import keeps transform module lightweight

    return "---\n" + yaml.dump(meta, default_flow_style=False, allow_unicode=True) + "---\n"


def html_to_markdown(html: str) -> str:
    """Convert HTML to Markdown using markdownify."""
    try:
        import markdownify

        return markdownify.markdownify(html, heading_style="ATX")
    except ImportError:
        # Fallback: strip tags crudely
        text = re.sub(r"<[^>]+>", "", html)
        return text


def write_markdown_page(
    *,
    output_dir: Path,
    title: str,
    body: str,
    meta: dict[str, Any],
    filename: str | None = None,
) -> Path:
    """Write a single markdown page with YAML frontmatter.

    Returns the path of the written file.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    slug = filename or _slugify(title)
    if not slug.endswith(".md"):
        slug += ".md"
    filepath = output_dir / slug
    meta.setdefault("title", title)
    meta.setdefault("fetched_at", datetime.now(timezone.utc).isoformat())
    content = build_frontmatter(meta) + "\n" + body.strip() + "\n"
    filepath.write_text(content, encoding="utf-8")
    return filepath
