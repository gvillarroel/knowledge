from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from .sources.arxiv import _parse_arxiv_feed
from .store import KnowledgeStore


_FINAL_LAYOUT_SOURCE_TYPES = {
    "aha",
    "arxiv",
    "confluence",
    "google_releases",
    "jira",
    "site",
    "television",
    "video",
}


def _dump_frontmatter(payload: dict[str, Any]) -> str:
    return yaml.safe_dump(payload, sort_keys=False, allow_unicode=False).strip()


def _markdown_document(frontmatter: dict[str, Any], body: str) -> str:
    return f"---\n{_dump_frontmatter(frontmatter)}\n---\n\n{body.rstrip()}\n"


def _render_json_payload(payload: Any) -> str:
    return "```json\n" + json.dumps(payload, indent=2, sort_keys=True) + "\n```"


def export_source(store: KnowledgeStore, source: dict[str, Any]) -> dict[str, Any]:
    """Export a single source into Markdown with YAML frontmatter."""
    source_dir = store.source_dir(source)
    if source.get("type") in _FINAL_LAYOUT_SOURCE_TYPES and (source_dir / "source-metadata.yaml").exists():
        exported_files = [
            str(path)
            for path in sorted(source_dir.rglob("*"))
            if path.is_file() and path.name != "source-metadata.yaml"
        ]
        source["last_exported_at"] = source.get("updated_at")
        store.update_collection_source(source)
        return {
            "key": source["key"],
            "source": source["id"],
            "files": len(exported_files),
            "library_dir": str(source_dir),
        }

    exported_files: list[str] = []
    export_targets: list[Path] = []

    for path in _iter_export_paths(source, source_dir):
        rel = path.relative_to(source_dir)
        content = _build_markdown_for_raw_file(source, path, rel)
        output_path = source_dir / _export_relative_path(source, rel)
        export_targets.append(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding="utf-8")
        exported_files.append(str(output_path))

    _clear_stale_export_outputs(source, source_dir, export_targets)
    source["last_exported_at"] = source.get("updated_at")
    store.update_collection_source(source)
    return {
        "key": source["key"],
        "source": source["id"],
        "files": len(exported_files),
        "library_dir": str(source_dir),
    }


def _build_markdown_for_raw_file(source: dict[str, Any], path: Path, rel: Path) -> str:
    """Build a Markdown document from a raw source file."""
    frontmatter = {
        "title": source.get("title") or rel.stem,
        "knowledge_key": source["key"],
        "source_id": source["id"],
        "source_type": source["type"],
        "original_path": str(rel).replace("\\", "/"),
        "generated_from": str(path),
    }

    special_renderer = _SPECIAL_RENDERERS.get((source.get("type"), path.name))
    if special_renderer is not None:
        extra_fm, body = special_renderer(source, path)
        frontmatter.update(extra_fm)
        return _markdown_document(frontmatter, body)

    sidecar_metadata = _load_sidecar_metadata(path)
    frontmatter.update(_frontmatter_from_sidecar(sidecar_metadata))

    body = _render_body_by_extension(path)
    if path.suffix.lower() in {".md", ".markdown"}:
        raw_text = path.read_text(encoding="utf-8", errors="replace")
        embedded_frontmatter, body = _extract_frontmatter(raw_text)
        frontmatter.update(embedded_frontmatter)

    return _markdown_document(frontmatter, body)


def _render_body_by_extension(path: Path) -> str:
    """Render the body text for a file based on its extension."""
    suffix = path.suffix.lower()
    if suffix in {".md", ".markdown"}:
        return path.read_text(encoding="utf-8", errors="replace")
    if suffix in {".html", ".htm"}:
        return path.read_text(encoding="utf-8", errors="replace")
    if suffix in {".txt", ".json", ".yaml", ".yml", ".xml"}:
        return f"```{suffix.lstrip('.')}\n{path.read_text(encoding='utf-8', errors='replace')}\n```"
    return _render_json_payload(
        {
            "note": "Binary or unsupported file type retained in raw store.",
            "path": str(path),
        }
    )


_SPECIAL_RENDERERS: dict[tuple[str | None, str], Any] = {
    ("arxiv", "paper.xml"): lambda source, path: _render_arxiv_document(source, path),
    ("video", "transcript.json"): lambda source, path: _render_video_document(source, path),
}


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
    """Return the list of raw files to export for a source."""
    source_type = source.get("type")
    resolver = _EXPORT_PATH_RESOLVERS.get(source_type)
    if resolver is not None:
        result = resolver(raw_dir)
        if result is not None:
            return result
    return [path for path in sorted(raw_dir.rglob("*")) if path.is_file()]


def _resolve_video_paths(raw_dir: Path) -> list[Path] | None:
    for name in ("transcript.json", "transcript.md", "transcript.txt"):
        candidate = raw_dir / name
        if candidate.exists():
            return [candidate]
    return None


def _resolve_arxiv_paths(raw_dir: Path) -> list[Path] | None:
    for name in ("paper.xml", "paper.html", "paper.txt"):
        candidate = raw_dir / name
        if candidate.exists():
            return [candidate]
    return None


def _resolve_glob_paths(raw_dir: Path, subdir: str, pattern: str) -> list[Path] | None:
    target = raw_dir / subdir
    if target.exists():
        files = [p for p in sorted(target.rglob(pattern)) if p.is_file()]
        if files:
            return files
    return None


def _resolve_site_paths(raw_dir: Path) -> list[Path] | None:
    return _resolve_glob_paths(raw_dir, "pages", "*.md")


def _resolve_google_releases_paths(raw_dir: Path) -> list[Path] | None:
    return _resolve_glob_paths(raw_dir, "entries", "*.md")


def _resolve_confluence_paths(raw_dir: Path) -> list[Path] | None:
    return _resolve_glob_paths(raw_dir, "pages", "*.html")


_EXPORT_PATH_RESOLVERS: dict[str, Any] = {
    "video": _resolve_video_paths,
    "arxiv": _resolve_arxiv_paths,
    "site": _resolve_site_paths,
    "google_releases": _resolve_google_releases_paths,
    "confluence": _resolve_confluence_paths,
}


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


def _clear_stale_export_outputs(source: dict[str, Any], source_dir: Path, keep_paths: list[Path]) -> None:
    keep = {path.resolve() for path in keep_paths}
    for path in sorted(source_dir.rglob("*.md"), reverse=True):
        if path.resolve() in keep:
            continue
        if _is_generated_export(path, source):
            path.unlink()
    for path in sorted(source_dir.rglob("*"), reverse=True):
        if path.is_dir() and path != source_dir and not any(path.iterdir()):
            path.rmdir()


def _is_generated_export(path: Path, source: dict[str, Any]) -> bool:
    if source.get("type") in {"arxiv", "video", "confluence", "jira", "aha"}:
        return True
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False
    if not text.startswith("---\n"):
        return False
    frontmatter, _ = _extract_frontmatter(text)
    return (
        frontmatter.get("knowledge_key") == source["key"]
        and frontmatter.get("source_id") == source["id"]
    )


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
