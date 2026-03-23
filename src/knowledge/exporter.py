from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from .sources.arxiv import _parse_arxiv_feed
from .store import KnowledgeStore


def _dump_frontmatter(payload: dict[str, Any]) -> str:
    return yaml.safe_dump(payload, sort_keys=False, allow_unicode=False).strip()


def _markdown_document(frontmatter: dict[str, Any], body: str) -> str:
    return f"---\n{_dump_frontmatter(frontmatter)}\n---\n\n{body.rstrip()}\n"


def _render_json_payload(payload: Any) -> str:
    return "```json\n" + json.dumps(payload, indent=2, sort_keys=True) + "\n```"


def export_source(store: KnowledgeStore, source: dict[str, Any]) -> dict[str, Any]:
    raw_dir = store.source_raw_dir(source)
    library_dir = store.source_library_dir(source)
    _clear_library_dir(library_dir)
    exported_files: list[str] = []

    for path in _iter_export_paths(source, raw_dir):
        rel = path.relative_to(raw_dir)
        content = _build_markdown_for_raw_file(source, path, rel)
        output_path = library_dir / _export_relative_path(source, rel)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding="utf-8")
        exported_files.append(str(output_path))

    source["last_exported_at"] = source.get("updated_at")
    store.update_collection_source(source)
    return {
        "key": source["key"],
        "source": source["id"],
        "files": len(exported_files),
        "library_dir": str(library_dir),
    }


def _build_markdown_for_raw_file(source: dict[str, Any], path: Path, rel: Path) -> str:
    frontmatter = {
        "title": source.get("title") or rel.stem,
        "knowledge_key": source["key"],
        "source_id": source["id"],
        "source_type": source["type"],
        "original_path": str(rel).replace("\\", "/"),
        "generated_from": str(path),
    }

    if source.get("type") == "arxiv" and path.name == "paper.xml":
        arxiv_frontmatter, body = _render_arxiv_document(source, path)
        frontmatter.update(arxiv_frontmatter)
        return _markdown_document(frontmatter, body)
    if source.get("type") == "video" and path.name == "transcript.json":
        video_frontmatter, body = _render_video_document(source, path)
        frontmatter.update(video_frontmatter)
        return _markdown_document(frontmatter, body)

    sidecar_metadata = _load_sidecar_metadata(path)
    frontmatter.update(_frontmatter_from_sidecar(sidecar_metadata))

    suffix = path.suffix.lower()
    if suffix in {".md", ".markdown"}:
        raw_text = path.read_text(encoding="utf-8", errors="replace")
        embedded_frontmatter, body = _extract_frontmatter(raw_text)
        frontmatter.update(embedded_frontmatter)
    elif suffix in {".html", ".htm"}:
        body = path.read_text(encoding="utf-8", errors="replace")
    elif suffix in {".txt", ".json", ".yaml", ".yml", ".xml"}:
        body = f"```{suffix.lstrip('.')}\n{path.read_text(encoding='utf-8', errors='replace')}\n```"
    else:
        body = _render_json_payload(
            {
                "note": "Binary or unsupported file type retained in raw store.",
                "path": str(path),
            }
        )
    return _markdown_document(frontmatter, body)


def _extract_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---\n"):
        return {}, text
    marker = "\n---\n"
    end_index = text.find(marker, 4)
    if end_index == -1:
        return {}, text
    raw_frontmatter = text[4:end_index]
    body = text[end_index + len(marker):]
    try:
        payload = yaml.safe_load(raw_frontmatter)
    except yaml.YAMLError:
        return {}, text
    if not isinstance(payload, dict):
        return {}, text
    return payload, body.lstrip("\n")

def _iter_export_paths(source: dict[str, Any], raw_dir: Path) -> list[Path]:
    if source.get("type") == "video":
        preferred = raw_dir / "transcript.json"
        if preferred.exists():
            return [preferred]
        legacy_markdown = raw_dir / "transcript.md"
        if legacy_markdown.exists():
            return [legacy_markdown]
        fallback = raw_dir / "transcript.txt"
        if fallback.exists():
            return [fallback]
    if source.get("type") == "arxiv":
        for filename in ("paper.xml", "paper.html", "paper.txt"):
            preferred = raw_dir / filename
            if preferred.exists():
                return [preferred]
    if source.get("type") == "site":
        pages_dir = raw_dir / "pages"
        if pages_dir.exists():
            page_files = [path for path in sorted(pages_dir.rglob("*.md")) if path.is_file()]
            if page_files:
                return page_files
    if source.get("type") == "confluence":
        pages_dir = raw_dir / "pages"
        if pages_dir.exists():
            page_files = [path for path in sorted(pages_dir.rglob("*.html")) if path.is_file()]
            if page_files:
                return page_files
    return [path for path in sorted(raw_dir.rglob("*")) if path.is_file()]


def _export_relative_path(source: dict[str, Any], rel: Path) -> Path:
    if source.get("type") == "video":
        return Path("transcript.md")
    if source.get("type") == "arxiv" and rel.name.startswith("paper."):
        return Path("paper.md")
    if rel.suffix.lower() in {".md", ".markdown"}:
        return rel.with_suffix(".md")
    if rel.suffix.lower() in {".html", ".htm"}:
        return rel.with_suffix(".md")
    return rel.with_name(f"{rel.name}.md")


def _clear_library_dir(library_dir: Path) -> None:
    for path in sorted(library_dir.rglob("*"), reverse=True):
        if path.is_file():
            path.unlink()
        elif path.is_dir():
            path.rmdir()


def _load_sidecar_metadata(path: Path) -> dict[str, Any]:
    if path.suffix.lower() not in {".md", ".markdown", ".html", ".htm"}:
        return {}
    sidecar_path = path.with_suffix(".json")
    if not sidecar_path.exists():
        return {}
    try:
        payload = json.loads(sidecar_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def _frontmatter_from_sidecar(payload: dict[str, Any]) -> dict[str, Any]:
    if not payload:
        return {}
    frontmatter: dict[str, Any] = {}
    if payload.get("title"):
        frontmatter["title"] = payload["title"]
    if payload.get("url"):
        frontmatter["url"] = payload["url"]
    if payload.get("id"):
        frontmatter["document_id"] = str(payload["id"])
    if payload.get("metadata"):
        frontmatter["source_metadata"] = payload["metadata"]
    return frontmatter


def _render_arxiv_document(source: dict[str, Any], path: Path) -> tuple[dict[str, Any], str]:
    payload = _parse_arxiv_feed(path.read_text(encoding="utf-8", errors="replace"))
    entry = next(iter(payload.get("entries", [])), {})
    title = entry.get("title") or source.get("title") or source["id"]
    summary = str(entry.get("summary") or "").strip()
    authors = [author for author in entry.get("authors", []) if author]
    categories = [category for category in entry.get("categories", []) if category]
    links = entry.get("links", {})
    frontmatter = {
        "title": title,
        "paper_id": _arxiv_paper_id(source),
        "source_url": source.get("config", {}).get("url"),
        "authors": authors,
        "published": entry.get("published"),
        "updated": entry.get("updated"),
        "categories": categories,
        "primary_category": entry.get("primary_category"),
        "pdf_url": entry.get("pdf_url"),
        "links": links,
    }
    body_lines = [f"# {title}"]
    if authors:
        body_lines.append("")
        body_lines.append("Authors: " + ", ".join(str(author) for author in authors))
    if summary:
        body_lines.append("")
        body_lines.append("## Summary")
        body_lines.append("")
        body_lines.append(summary)
    return frontmatter, "\n".join(body_lines).strip()


def _arxiv_paper_id(source: dict[str, Any]) -> str:
    source_url = str(source.get("config", {}).get("url") or "")
    if "/abs/" in source_url:
        return source_url.rsplit("/abs/", 1)[-1]
    if "/pdf/" in source_url:
        return source_url.rsplit("/pdf/", 1)[-1].removesuffix(".pdf")
    return source["id"].removeprefix("arxiv-")


def _render_video_document(source: dict[str, Any], path: Path) -> tuple[dict[str, Any], str]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    metadata_path = path.with_name("metadata.json")
    metadata = {}
    if metadata_path.exists():
        try:
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            metadata = {}
    title = payload.get("title") or payload.get("video_id") or source["id"]
    author_name = payload.get("author_name") or "Unknown"
    segments = payload.get("segments", [])
    frontmatter = {
        "title": title,
        "video_id": payload.get("video_id"),
        "url": payload.get("url"),
        "author_name": author_name,
        "language": payload.get("language"),
        "language_code": payload.get("language_code"),
        "is_generated": payload.get("is_generated"),
        "segment_count": len(segments) if isinstance(segments, list) else 0,
        "source_metadata": metadata,
    }
    lines = [
        f"# {title}",
        "",
        f"- Author: {author_name}",
        f"- Language: {payload.get('language')} ({payload.get('language_code')})",
        f"- Auto-generated: {payload.get('is_generated')}",
        "",
        "## Transcript",
        "",
    ]
    for segment in segments if isinstance(segments, list) else []:
        if not isinstance(segment, dict):
            continue
        text = str(segment.get("text", "")).strip()
        if not text:
            continue
        lines.append(f"[{_format_timestamp(float(segment.get('start', 0.0)))}] {text}")
    return frontmatter, "\n".join(lines).rstrip()


def _format_timestamp(seconds: float) -> str:
    whole = int(seconds)
    hours, remainder = divmod(whole, 3600)
    minutes, secs = divmod(remainder, 60)
    if hours:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"
