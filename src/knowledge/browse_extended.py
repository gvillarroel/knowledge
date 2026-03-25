"""Extended browse commands for deep knowledge navigation.

Adds cross-key, cross-type, timeline, stale, unsynced, file-level,
repo-file, stats, and command browsers.
"""

from __future__ import annotations

import os
import re
from argparse import Namespace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .store import KnowledgeStore


def _store_from_args(args: Namespace) -> KnowledgeStore:
    return KnowledgeStore(args.store)


def _strip_yaml_frontmatter(text: str) -> str:
    if not text.startswith("---"):
        return text
    end = text.find("\n---", 3)
    if end == -1:
        return text
    return text[end + 4:].lstrip("\n")


def _extract_fm(text: str, field: str) -> str:
    if not text.startswith("---"):
        return ""
    end = text.find("\n---", 3)
    if end == -1:
        return ""
    fm = text[4:end]
    for line in fm.splitlines():
        if line.startswith(f"{field}:"):
            return line.split(":", 1)[1].strip().strip("'\"")
    return ""


# ── ANSI helpers ─────────────────────────────────────────────────────────

_GREEN = "\033[32m"
_YELLOW = "\033[33m"
_CYAN = "\033[36m"
_BLUE = "\033[34m"
_MAGENTA = "\033[35m"
_RED = "\033[31m"
_DIM = "\033[2m"
_BOLD = "\033[1m"
_RESET = "\033[0m"

_TYPE_COLORS = {
    "arxiv": _MAGENTA,
    "github": _GREEN,
    "confluence": _BLUE,
    "jira": _CYAN,
    "video": _YELLOW,
    "site": _BLUE,
    "aha": _MAGENTA,
    "google_releases": _YELLOW,
    "television": _DIM,
}

_TYPE_ICONS = {
    "arxiv": "📄",
    "github": "🔗",
    "confluence": "📝",
    "jira": "🎫",
    "video": "🎬",
    "site": "🌐",
    "aha": "💡",
    "google_releases": "📢",
    "television": "📺",
}


# ── know browse by-key ───────────────────────────────────────────────────

def cmd_browse_by_key(args: Namespace) -> object:
    """List keys with source count and type summary for drill-down."""
    store = _store_from_args(args)
    store.initialize()
    fmt = getattr(args, "format", "json")
    entry = getattr(args, "entry", None)
    keys_data: list[dict[str, Any]] = []

    for key_name in store.list_collection_keys():
        meta = store.get_collection_metadata(key_name)
        sources = meta.get("sources", [])
        type_counts: dict[str, int] = {}
        file_count = 0
        for s in sources:
            t = s.get("type", "unknown")
            type_counts[t] = type_counts.get(t, 0) + 1
        key_dir = store.key_dir(key_name)
        for md in key_dir.rglob("*.md"):
            if md.name != "metadata.yaml":
                file_count += 1
        types_summary = ", ".join(f"{v} {k}" for k, v in sorted(type_counts.items()))
        keys_data.append({
            "name": key_name,
            "source_count": len(sources),
            "file_count": file_count,
            "types_summary": types_summary,
            "created_at": meta.get("created_at", ""),
            "updated_at": meta.get("updated_at", ""),
        })

    if fmt == "television":
        lines = []
        for k in keys_data:
            lines.append(
                f"{_BOLD}{k['name']}{_RESET} | "
                f"{_CYAN}{k['source_count']} sources{_RESET} | "
                f"{_DIM}{k['file_count']} files | {k['types_summary']}{_RESET}"
            )
        return "\n".join(lines)
    if fmt == "television-preview":
        item = _find_by_name(keys_data, entry)
        if not item:
            return "No key matched.\n"
        lines = [
            f"# {item['name']}",
            "",
            f"- Sources: {item['source_count']}",
            f"- Local files: {item['file_count']}",
            f"- Types: {item['types_summary']}",
            f"- Created: {item['created_at']}",
            f"- Updated: {item['updated_at']}",
            "",
            "## Commands",
            "",
            f"- List sources: `know list sources --key {item['name']}`",
            f"- Sync: `know sync --key {item['name']}`",
            f"- Export: `know export --key {item['name']}`",
            f"- Browse sources: Enter to drill into this key's sources",
        ]
        return "\n".join(lines) + "\n"
    return {"keys": keys_data}


# ── know browse by-type ──────────────────────────────────────────────────

def cmd_browse_by_type(args: Namespace) -> object:
    """List source types with count and key distribution."""
    store = _store_from_args(args)
    store.initialize()
    fmt = getattr(args, "format", "json")
    entry = getattr(args, "entry", None)

    type_data: dict[str, dict[str, Any]] = {}
    for source in store.list_collection_sources():
        t = source.get("type", "unknown")
        if t not in type_data:
            type_data[t] = {"type": t, "count": 0, "keys": set(), "synced": 0, "unsynced": 0}
        type_data[t]["count"] += 1
        type_data[t]["keys"].add(source.get("key", ""))
        if source.get("last_synced_at"):
            type_data[t]["synced"] += 1
        else:
            type_data[t]["unsynced"] += 1

    items = []
    for t, d in sorted(type_data.items(), key=lambda x: -x[1]["count"]):
        items.append({
            "type": t,
            "count": d["count"],
            "keys": sorted(d["keys"]),
            "key_count": len(d["keys"]),
            "synced": d["synced"],
            "unsynced": d["unsynced"],
        })

    if fmt == "television":
        lines = []
        for i in items:
            icon = _TYPE_ICONS.get(i["type"], "●")
            color = _TYPE_COLORS.get(i["type"], _DIM)
            lines.append(
                f"{color}{icon} {i['type']}{_RESET} | "
                f"{i['count']} sources | "
                f"{_GREEN}{i['synced']} synced{_RESET} "
                f"{_YELLOW}{i['unsynced']} pending{_RESET} | "
                f"{_DIM}{i['key_count']} keys{_RESET}"
            )
        return "\n".join(lines)
    if fmt == "television-preview":
        item = _find_by_field(items, "type", entry)
        if not item:
            return "No type matched.\n"
        lines = [
            f"# Source type: {item['type']}",
            "",
            f"- Total sources: {item['count']}",
            f"- Synced: {item['synced']}",
            f"- Pending: {item['unsynced']}",
            f"- Keys using this type: {', '.join(item['keys'])}",
            "",
            "## Actions",
            "",
            "- Press **Enter** to browse all sources of this type",
            f"- `know browse local --type {item['type']}`",
        ]
        return "\n".join(lines) + "\n"
    return {"types": items}


# ── know browse papers ───────────────────────────────────────────────────

def cmd_browse_papers(args: Namespace) -> object:
    """Unified arXiv paper browser across ALL keys."""
    store = _store_from_args(args)
    store.initialize()
    fmt = getattr(args, "format", "json")
    entry = getattr(args, "entry", None)

    sources = store.list_collection_sources(source_type="arxiv")
    papers: list[dict[str, Any]] = []

    for source in sources:
        config = source.get("config", {})
        url = config.get("url", "")
        arxiv_id = _extract_arxiv_id(url)
        has_files = False
        body = ""
        try:
            source_dir = store.source_dir(source)
            md_files = list(source_dir.glob("**/*.md"))
            has_files = len(md_files) > 0
            if has_files and md_files:
                text = md_files[0].read_text(encoding="utf-8")
                body = _strip_yaml_frontmatter(text)
        except Exception:
            pass

        papers.append({
            "arxiv_id": arxiv_id,
            "url": url,
            "key": source.get("key", ""),
            "synced": has_files,
            "last_synced_at": source.get("last_synced_at", ""),
            "body": body[:500] if body else "",
            "title": source.get("title", url),
        })

    if fmt == "television":
        lines = []
        for p in papers:
            color = _GREEN if p["synced"] else _YELLOW
            marker = "●" if p["synced"] else "○"
            lines.append(
                f"{color}{marker}{_RESET} {p['arxiv_id']} | "
                f"{_DIM}{p['key']}{_RESET}"
            )
        return "\n".join(lines)
    if fmt == "television-preview":
        item = _find_by_field(papers, "arxiv_id", entry)
        if not item:
            return "No paper matched.\n"
        lines = [
            f"# arXiv: {item['arxiv_id']}",
            "",
            f"- URL: {item['url']}",
            f"- Key: {item['key']}",
            f"- Synced: {'✅ Yes' if item['synced'] else '❌ No'}",
        ]
        if item.get("last_synced_at"):
            lines.append(f"- Last synced: {item['last_synced_at']}")
        if item["body"]:
            lines.extend(["", "## Content preview", "", item["body"]])
        lines.extend([
            "",
            "## Commands",
            "",
            f"- Sync: `know sync arxiv {item['url']} --key {item['key']}`",
        ])
        return "\n".join(lines) + "\n"
    return {"papers": papers}


# ── know browse repos ────────────────────────────────────────────────────

def cmd_browse_repos(args: Namespace) -> object:
    """All GitHub repos across all keys with file counts."""
    store = _store_from_args(args)
    store.initialize()
    fmt = getattr(args, "format", "json")
    entry = getattr(args, "entry", None)

    sources = store.list_collection_sources(source_type="github")
    repos: list[dict[str, Any]] = []

    for source in sources:
        config = source.get("config", {})
        repo_url = config.get("repo_url", "")
        branches = config.get("branches", ["HEAD"])
        file_count = 0
        try:
            source_dir = store.source_dir(source)
            file_count = sum(1 for _ in source_dir.rglob("*") if _.is_file())
        except Exception:
            pass

        repos.append({
            "repo_url": repo_url,
            "repo_name": _repo_short_name(repo_url),
            "key": source.get("key", ""),
            "source_id": source.get("id", ""),
            "branches": branches,
            "file_count": file_count,
            "synced": file_count > 0,
            "last_synced_at": source.get("last_synced_at", ""),
        })

    if fmt == "television":
        lines = []
        for r in repos:
            color = _GREEN if r["synced"] else _YELLOW
            marker = "●" if r["synced"] else "○"
            lines.append(
                f"{color}{marker}{_RESET} {r['repo_name']} | "
                f"{_DIM}{r['key']} | {r['file_count']} files | "
                f"{', '.join(r['branches'])}{_RESET}"
            )
        return "\n".join(lines)
    if fmt == "television-preview":
        item = _find_by_field(repos, "repo_name", entry)
        if not item:
            return "No repo matched.\n"
        lines = [
            f"# {item['repo_name']}",
            "",
            f"- URL: {item['repo_url']}",
            f"- Key: {item['key']}",
            f"- Branches: {', '.join(item['branches'])}",
            f"- Local files: {item['file_count']}",
            f"- Synced: {'✅ Yes' if item['synced'] else '❌ No'}",
            "",
            "## Actions",
            "",
            "- Press **Enter** to browse files inside this repo",
            f"- Sync: `{_build_sync_cmd(item)}`",
        ]
        return "\n".join(lines) + "\n"
    return {"repos": repos}


# ── know browse repo-files ──────────────────────────────────────────────

def cmd_browse_repo_files(args: Namespace) -> object:
    """Browse files inside a synced GitHub repo."""
    store = _store_from_args(args)
    store.initialize()
    fmt = getattr(args, "format", "json")
    entry = getattr(args, "entry", None)
    repo_filter = getattr(args, "repo", None)

    sources = store.list_collection_sources(source_type="github")
    files: list[dict[str, Any]] = []

    for source in sources:
        config = source.get("config", {})
        repo_name = _repo_short_name(config.get("repo_url", ""))
        if repo_filter and repo_filter not in repo_name:
            continue
        try:
            source_dir = store.source_dir(source)
            for f in sorted(source_dir.rglob("*")):
                if not f.is_file():
                    continue
                rel = f.relative_to(source_dir)
                body = ""
                if f.suffix == ".md":
                    try:
                        text = f.read_text(encoding="utf-8", errors="replace")
                        body = _strip_yaml_frontmatter(text)
                    except Exception:
                        pass
                files.append({
                    "path": str(rel).replace("\\", "/"),
                    "repo": repo_name,
                    "key": source.get("key", ""),
                    "size": f.stat().st_size,
                    "ext": f.suffix,
                    "full_path": str(f),
                    "body": body[:2000] if body else "",
                })
        except Exception:
            pass

    if fmt == "television":
        lines = []
        for f in files:
            ext_color = _GREEN if f["ext"] in {".py", ".rs", ".go", ".ts", ".js"} else \
                        _BLUE if f["ext"] in {".md", ".txt"} else \
                        _YELLOW if f["ext"] in {".toml", ".yaml", ".yml", ".json"} else _DIM
            lines.append(
                f"{ext_color}{f['path']}{_RESET} | "
                f"{_DIM}{f['repo']} | {f['size']}b{_RESET}"
            )
        return "\n".join(lines)
    if fmt == "television-preview":
        item = _find_by_field(files, "path", entry)
        if not item:
            return "No file matched.\n"
        lines = [
            f"# {item['path']}",
            "",
            f"- Repo: {item['repo']}",
            f"- Key: {item['key']}",
            f"- Size: {item['size']} bytes",
        ]
        if item["body"]:
            lines.extend(["", "---", "", item["body"]])
        else:
            try:
                text = Path(item["full_path"]).read_text(encoding="utf-8", errors="replace")[:3000]
                lines.extend(["", "---", "", text])
            except Exception:
                lines.append("\n_Could not read file._")
        return "\n".join(lines) + "\n"
    return {"files": files}


# ── know browse files ────────────────────────────────────────────────────

def cmd_browse_files(args: Namespace) -> object:
    """Full-text searchable file browser across all local markdown."""
    store = _store_from_args(args)
    store.initialize()
    fmt = getattr(args, "format", "json")
    entry = getattr(args, "entry", None)
    query = getattr(args, "query", None)
    key_filter = getattr(args, "key", None)

    sources = store.list_collection_sources(key_name=key_filter)
    items: list[dict[str, Any]] = []

    for source in sources:
        try:
            source_dir = store.source_dir(source)
            for md_file in sorted(source_dir.rglob("*.md")):
                text = md_file.read_text(encoding="utf-8", errors="replace")
                title = _extract_fm(text, "title") or md_file.stem
                body = _strip_yaml_frontmatter(text)
                if query and query.lower() not in text.lower():
                    continue
                items.append({
                    "title": title,
                    "source_type": source.get("type", ""),
                    "key": source.get("key", ""),
                    "source_id": source.get("id", ""),
                    "path": str(md_file),
                    "body": body,
                })
        except Exception:
            pass

    if fmt == "television":
        lines = []
        for i in items:
            color = _TYPE_COLORS.get(i["source_type"], _DIM)
            icon = _TYPE_ICONS.get(i["source_type"], "●")
            lines.append(
                f"{color}{icon}{_RESET} {i['title']} | "
                f"{_DIM}{i['source_type']} | {i['key']}{_RESET}"
            )
        return "\n".join(lines)
    if fmt == "television-preview":
        item = _find_by_title(items, entry)
        if not item:
            return "No file matched.\n"
        return f"# {item['title']}\n\n{item.get('body', '')}\n"
    return {"files": items}


# ── know browse recent ──────────────────────────────────────────────────

def cmd_browse_recent(args: Namespace) -> object:
    """Sources ordered by last sync date (most recent first)."""
    store = _store_from_args(args)
    store.initialize()
    fmt = getattr(args, "format", "json")
    entry = getattr(args, "entry", None)
    limit = getattr(args, "limit", 50)

    sources = store.list_collection_sources()
    with_date = []
    for s in sources:
        synced_at = s.get("last_synced_at") or s.get("updated_at") or ""
        with_date.append({**s, "_sort_date": synced_at})
    with_date.sort(key=lambda x: x["_sort_date"], reverse=True)
    items = with_date[:limit]

    if fmt == "television":
        lines = []
        for s in items:
            color = _TYPE_COLORS.get(s.get("type", ""), _DIM)
            icon = _TYPE_ICONS.get(s.get("type", ""), "●")
            date = s.get("last_synced_at", "never")[:19]
            lines.append(
                f"{color}{icon} {s.get('title', s.get('id', ''))}{_RESET} | "
                f"{_DIM}{s.get('key', '')} | {date}{_RESET}"
            )
        return "\n".join(lines)
    if fmt == "television-preview":
        item = _find_by_title(items, entry)
        if not item:
            return "No source matched.\n"
        lines = [
            f"# {item.get('title', item.get('id', ''))}",
            "",
            f"- Type: {item.get('type', '')}",
            f"- Key: {item.get('key', '')}",
            f"- Last synced: {item.get('last_synced_at', 'never')}",
            f"- Updated: {item.get('updated_at', '')}",
        ]
        if item.get("update_command"):
            lines.append(f"- Sync: `{item['update_command']}`")
        return "\n".join(lines) + "\n"
    return {"sources": items}


# ── know browse stale ───────────────────────────────────────────────────

def cmd_browse_stale(args: Namespace) -> object:
    """Sources that haven't been synced in a long time or never."""
    store = _store_from_args(args)
    store.initialize()
    fmt = getattr(args, "format", "json")
    entry = getattr(args, "entry", None)
    days = getattr(args, "days", 7)

    sources = store.list_collection_sources()
    now = datetime.now(timezone.utc)
    stale: list[dict[str, Any]] = []

    for s in sources:
        synced_at = s.get("last_synced_at")
        if not synced_at:
            stale.append({**s, "age_days": -1, "status": "never synced"})
            continue
        try:
            dt = datetime.fromisoformat(synced_at)
            age = (now - dt).days
            if age >= days:
                stale.append({**s, "age_days": age, "status": f"{age} days ago"})
        except Exception:
            stale.append({**s, "age_days": -1, "status": "unknown"})

    stale.sort(key=lambda x: x.get("age_days", 9999), reverse=True)

    if fmt == "television":
        lines = []
        for s in stale:
            color = _RED if s["age_days"] < 0 else _YELLOW
            icon = "⚠️" if s["age_days"] < 0 else "🕐"
            lines.append(
                f"{color}{icon} {s.get('title', s.get('id', ''))}{_RESET} | "
                f"{s['status']} | "
                f"{_DIM}{s.get('type', '')} | {s.get('key', '')}{_RESET}"
            )
        return "\n".join(lines)
    if fmt == "television-preview":
        item = _find_by_title(stale, entry)
        if not item:
            return "No stale source matched.\n"
        lines = [
            f"# {item.get('title', item.get('id', ''))}",
            "",
            f"- Status: {item.get('status', '')}",
            f"- Type: {item.get('type', '')}",
            f"- Key: {item.get('key', '')}",
        ]
        if item.get("update_command"):
            lines.extend([
                "",
                "## Re-sync command",
                "",
                f"```\n{item['update_command']}\n```",
            ])
        return "\n".join(lines) + "\n"
    return {"stale": stale}


# ── know browse unsynced ────────────────────────────────────────────────

def cmd_browse_unsynced(args: Namespace) -> object:
    """Sources registered but never synced."""
    store = _store_from_args(args)
    store.initialize()
    fmt = getattr(args, "format", "json")
    entry = getattr(args, "entry", None)

    sources = store.list_collection_sources()
    unsynced = [s for s in sources if not s.get("last_synced_at")]

    if fmt == "television":
        lines = []
        for s in unsynced:
            color = _TYPE_COLORS.get(s.get("type", ""), _RED)
            icon = _TYPE_ICONS.get(s.get("type", ""), "○")
            lines.append(
                f"{color}{icon} {s.get('title', s.get('id', ''))}{_RESET} | "
                f"{_DIM}{s.get('type', '')} | {s.get('key', '')}{_RESET}"
            )
        return "\n".join(lines)
    if fmt == "television-preview":
        item = _find_by_title(unsynced, entry)
        if not item:
            return "No unsynced source.\n"
        lines = [
            f"# {item.get('title', item.get('id', ''))}",
            "",
            f"- Type: {item.get('type', '')}",
            f"- Key: {item.get('key', '')}",
            f"- Created: {item.get('created_at', '')}",
            "",
            "## Sync command",
            "",
            f"```\n{item.get('update_command', 'N/A')}\n```",
            "",
            "Press **Enter** to sync this source.",
        ]
        return "\n".join(lines) + "\n"
    return {"unsynced": unsynced}


# ── know browse timeline ────────────────────────────────────────────────

def cmd_browse_timeline(args: Namespace) -> object:
    """All sources ordered chronologically by creation date."""
    store = _store_from_args(args)
    store.initialize()
    fmt = getattr(args, "format", "json")
    entry = getattr(args, "entry", None)

    sources = store.list_collection_sources()
    sources.sort(key=lambda x: x.get("created_at", ""), reverse=True)

    if fmt == "television":
        lines = []
        for s in sources:
            color = _TYPE_COLORS.get(s.get("type", ""), _DIM)
            icon = _TYPE_ICONS.get(s.get("type", ""), "●")
            date = (s.get("created_at") or "")[:10]
            synced = "●" if s.get("last_synced_at") else "○"
            lines.append(
                f"{color}{icon}{_RESET} {date} | {synced} {s.get('title', s.get('id', ''))} | "
                f"{_DIM}{s.get('key', '')}{_RESET}"
            )
        return "\n".join(lines)
    if fmt == "television-preview":
        item = _find_by_title(sources, entry)
        if not item:
            return "No source matched.\n"
        lines = [
            f"# {item.get('title', item.get('id', ''))}",
            "",
            f"- Type: {item.get('type', '')}",
            f"- Key: {item.get('key', '')}",
            f"- Created: {item.get('created_at', '')}",
            f"- Last synced: {item.get('last_synced_at', 'never')}",
        ]
        if item.get("config"):
            lines.extend(["", "## Config"])
            for k, v in item["config"].items():
                lines.append(f"- {k}: {v}")
        return "\n".join(lines) + "\n"
    return {"timeline": sources}


# ── know browse commands ─────────────────────────────────────────────────

def cmd_browse_commands(args: Namespace) -> object:
    """Browse all available sync/delete/export commands."""
    store = _store_from_args(args)
    store.initialize()
    fmt = getattr(args, "format", "json")
    entry = getattr(args, "entry", None)

    cmds: list[dict[str, Any]] = []

    # Key-level commands
    for key_name in store.list_collection_keys():
        cmds.append({
            "command": f"know sync --key {key_name}",
            "type": "sync",
            "scope": "key",
            "target": key_name,
            "description": f"Sync all sources in key '{key_name}'",
        })
        cmds.append({
            "command": f"know export --key {key_name}",
            "type": "export",
            "scope": "key",
            "target": key_name,
            "description": f"Export key '{key_name}'",
        })

    # Source-level commands
    for source in store.list_collection_sources():
        if source.get("update_command"):
            cmds.append({
                "command": source["update_command"],
                "type": "sync",
                "scope": "source",
                "target": source.get("title", source.get("id", "")),
                "key": source.get("key", ""),
                "description": f"Sync {source.get('type', '')} source: {source.get('title', '')}",
            })
        if source.get("delete_command"):
            cmds.append({
                "command": source["delete_command"],
                "type": "delete",
                "scope": "source",
                "target": source.get("title", source.get("id", "")),
                "key": source.get("key", ""),
                "description": f"Delete {source.get('type', '')} source: {source.get('title', '')}",
            })

    if fmt == "television":
        lines = []
        for c in cmds:
            color = _GREEN if c["type"] == "sync" else _YELLOW if c["type"] == "export" else _RED
            icon = "🔄" if c["type"] == "sync" else "📦" if c["type"] == "export" else "🗑️"
            lines.append(
                f"{color}{icon} [{c['type']}]{_RESET} {c['command']}"
            )
        return "\n".join(lines)
    if fmt == "television-preview":
        item = _find_cmd(cmds, entry)
        if not item:
            return "No command matched.\n"
        lines = [
            f"# {item['description']}",
            "",
            f"- Type: {item['type']}",
            f"- Scope: {item['scope']}",
            f"- Target: {item['target']}",
            "",
            "## Command",
            "",
            f"```\n{item['command']}\n```",
            "",
            "Press **Enter** to execute this command.",
        ]
        return "\n".join(lines) + "\n"
    return {"commands": cmds}


# ── know browse stats ───────────────────────────────────────────────────

def cmd_browse_stats(args: Namespace) -> object:
    """Knowledge base statistics overview."""
    store = _store_from_args(args)
    store.initialize()
    fmt = getattr(args, "format", "json")
    entry = getattr(args, "entry", None)

    keys = store.list_collection_keys()
    all_sources = store.list_collection_sources()
    type_counts: dict[str, int] = {}
    synced_count = 0
    for s in all_sources:
        t = s.get("type", "unknown")
        type_counts[t] = type_counts.get(t, 0) + 1
        if s.get("last_synced_at"):
            synced_count += 1

    total_files = 0
    for key_name in keys:
        kdir = store.key_dir(key_name)
        total_files += sum(1 for _ in kdir.rglob("*.md") if _.is_file())

    stats = [
        {"label": "Total keys", "value": str(len(keys)), "detail": ", ".join(keys)},
        {"label": "Total sources", "value": str(len(all_sources)), "detail": ""},
        {"label": "Synced sources", "value": str(synced_count), "detail": f"{len(all_sources) - synced_count} pending"},
        {"label": "Total local files", "value": str(total_files), "detail": ".md files"},
    ]
    for t, c in sorted(type_counts.items(), key=lambda x: -x[1]):
        icon = _TYPE_ICONS.get(t, "●")
        stats.append({"label": f"{icon} {t}", "value": str(c), "detail": "sources"})

    if fmt == "television":
        lines = []
        for s in stats:
            lines.append(f"{_BOLD}{s['label']}{_RESET} | {_CYAN}{s['value']}{_RESET} | {_DIM}{s['detail']}{_RESET}")
        return "\n".join(lines)
    if fmt == "television-preview":
        lines = ["# Knowledge Base Statistics", ""]
        for s in stats:
            lines.append(f"- **{s['label']}**: {s['value']} {s['detail']}")
        lines.extend([
            "",
            "## Keys",
            "",
        ])
        for key_name in keys:
            meta = store.get_collection_metadata(key_name)
            sc = len(meta.get("sources", []))
            lines.append(f"- `{key_name}` — {sc} sources")
        return "\n".join(lines) + "\n"
    return {"stats": stats}


# ── know browse crossref ────────────────────────────────────────────────

def cmd_browse_crossref(args: Namespace) -> object:
    """Find sources that appear in multiple keys (shared URLs, etc.)."""
    store = _store_from_args(args)
    store.initialize()
    fmt = getattr(args, "format", "json")
    entry = getattr(args, "entry", None)

    url_map: dict[str, list[str]] = {}
    for source in store.list_collection_sources():
        config = source.get("config", {})
        url = config.get("url") or config.get("repo_url") or ""
        if url:
            url_map.setdefault(url, []).append(source.get("key", ""))

    shared = []
    for url, ks in sorted(url_map.items()):
        if len(ks) > 1:
            shared.append({"url": url, "keys": ks, "key_count": len(ks)})

    if fmt == "television":
        lines = []
        for s in shared:
            lines.append(
                f"{_MAGENTA}🔗{_RESET} {s['url']} | "
                f"{_CYAN}{s['key_count']} keys{_RESET} | "
                f"{_DIM}{', '.join(s['keys'])}{_RESET}"
            )
        return "\n".join(lines)
    if fmt == "television-preview":
        item = _find_by_field(shared, "url", entry)
        if not item:
            return "No cross-reference found.\n"
        lines = [
            f"# Shared source: {item['url']}",
            "",
            f"- Present in {item['key_count']} keys:",
        ]
        for k in item["keys"]:
            lines.append(f"  - `{k}`")
        return "\n".join(lines) + "\n"
    return {"crossref": shared}


# ── know browse key-sources (for fork from by-key) ──────────────────────

def cmd_browse_key_sources(args: Namespace) -> object:
    """Browse sources for a specific key (used in fork chain)."""
    store = _store_from_args(args)
    store.initialize()
    fmt = getattr(args, "format", "json")
    entry = getattr(args, "entry", None)
    key_name = getattr(args, "key", None)

    if not key_name:
        return "No key specified.\n"

    sources = store.list_collection_sources(key_name=key_name)
    items: list[dict[str, Any]] = []
    for s in sources:
        file_count = 0
        try:
            sd = store.source_dir(s)
            file_count = sum(1 for _ in sd.rglob("*.md") if _.is_file())
        except Exception:
            pass
        items.append({
            **s,
            "file_count": file_count,
            "synced": file_count > 0 or bool(s.get("last_synced_at")),
        })

    if fmt == "television":
        lines = []
        for i in items:
            color = _TYPE_COLORS.get(i.get("type", ""), _DIM)
            icon = _TYPE_ICONS.get(i.get("type", ""), "●")
            marker = f"{_GREEN}●{_RESET}" if i["synced"] else f"{_YELLOW}○{_RESET}"
            lines.append(
                f"{marker} {color}{icon} {i.get('title', i.get('id', ''))}{_RESET} | "
                f"{_DIM}{i.get('type', '')} | {i['file_count']} files{_RESET}"
            )
        return "\n".join(lines)
    if fmt == "television-preview":
        item = _find_by_title(items, entry)
        if not item:
            return "No source matched.\n"
        lines = [
            f"# {item.get('title', item.get('id', ''))}",
            "",
            f"- Type: {item.get('type', '')}",
            f"- Key: {item.get('key', '')}",
            f"- Files: {item['file_count']}",
            f"- Synced: {'✅ Yes' if item['synced'] else '❌ No'}",
            f"- Created: {item.get('created_at', '')}",
            f"- Last synced: {item.get('last_synced_at', 'never')}",
        ]
        if item.get("update_command"):
            lines.extend(["", f"- Sync: `{item['update_command']}`"])
        if item.get("delete_command"):
            lines.append(f"- Delete: `{item['delete_command']}`")
        return "\n".join(lines) + "\n"
    return {"sources": items}


# ── know browse source-files (for fork chain) ──────────────────────────

def cmd_browse_source_files(args: Namespace) -> object:
    """Browse markdown files inside a specific source."""
    store = _store_from_args(args)
    store.initialize()
    fmt = getattr(args, "format", "json")
    entry = getattr(args, "entry", None)
    key_name = getattr(args, "key", None)
    source_id = getattr(args, "source_id", None)

    if not key_name or not source_id:
        return "Need --key and --source-id.\n"

    sources = store.list_collection_sources(key_name=key_name)
    source = next((s for s in sources if s.get("id") == source_id), None)
    if not source:
        return f"Source '{source_id}' not found in key '{key_name}'.\n"

    items: list[dict[str, Any]] = []
    try:
        source_dir = store.source_dir(source)
        for f in sorted(source_dir.rglob("*")):
            if not f.is_file():
                continue
            rel = str(f.relative_to(source_dir)).replace("\\", "/")
            body = ""
            if f.suffix == ".md":
                try:
                    text = f.read_text(encoding="utf-8", errors="replace")
                    title = _extract_fm(text, "title") or f.stem
                    body = _strip_yaml_frontmatter(text)
                except Exception:
                    title = f.stem
            else:
                title = f.name
            items.append({
                "title": title,
                "path": rel,
                "full_path": str(f),
                "ext": f.suffix,
                "size": f.stat().st_size,
                "body": body,
            })
    except Exception:
        pass

    if fmt == "television":
        lines = []
        for i in items:
            ext_color = _GREEN if i["ext"] in {".py", ".rs", ".go"} else \
                        _BLUE if i["ext"] == ".md" else _DIM
            lines.append(f"{ext_color}{i['path']}{_RESET} | {_DIM}{i['size']}b{_RESET}")
        return "\n".join(lines)
    if fmt == "television-preview":
        item = _find_by_field(items, "path", entry)
        if not item:
            item = _find_by_title(items, entry)
        if not item:
            return "No file matched.\n"
        if item["body"]:
            return f"# {item['title']}\n\n{item['body']}\n"
        try:
            text = Path(item["full_path"]).read_text(encoding="utf-8", errors="replace")[:5000]
            return f"# {item['title']}\n\n```\n{text}\n```\n"
        except Exception:
            return f"# {item['title']}\n\n_Could not read file._\n"
    return {"files": items}


# ── Helpers ──────────────────────────────────────────────────────────────

def _find_by_name(items: list[dict], entry: str | None) -> dict | None:
    if not items:
        return None
    if not entry:
        return items[0]
    clean = re.sub(r"\033\[[0-9;]*m", "", entry or "")
    for i in items:
        if i.get("name", "") in clean:
            return i
    return items[0]


def _find_by_field(items: list[dict], field: str, entry: str | None) -> dict | None:
    if not items:
        return None
    if not entry:
        return items[0]
    clean = re.sub(r"\033\[[0-9;]*m", "", entry or "")
    for i in items:
        val = str(i.get(field, ""))
        if val and val in clean:
            return i
    return items[0]


def _find_by_title(items: list[dict], entry: str | None) -> dict | None:
    if not items:
        return None
    if not entry:
        return items[0]
    clean = re.sub(r"\033\[[0-9;]*m", "", entry or "")
    for i in items:
        t = i.get("title") or i.get("id") or i.get("name") or ""
        if t and t in clean:
            return i
    return items[0]


def _find_cmd(cmds: list[dict], entry: str | None) -> dict | None:
    if not cmds:
        return None
    if not entry:
        return cmds[0]
    clean = re.sub(r"\033\[[0-9;]*m", "", entry or "")
    for c in cmds:
        if c["command"] in clean:
            return c
    return cmds[0]


def _extract_arxiv_id(url: str) -> str:
    match = re.search(r"(\d{4}\.\d{4,5}(?:v\d+)?)", url)
    return match.group(1) if match else url.split("/")[-1]


def _repo_short_name(url: str) -> str:
    from urllib.parse import urlparse
    path = urlparse(url).path.rstrip("/")
    if path.endswith(".git"):
        path = path[:-4]
    parts = path.strip("/").split("/")
    if len(parts) >= 2:
        return f"{parts[-2]}/{parts[-1]}"
    return url


def _build_sync_cmd(repo: dict) -> str:
    branches = " ".join(f"--branch {b}" for b in repo.get("branches", ["HEAD"]))
    return f"know sync github-repo {repo['repo_url']} --key {repo['key']} {branches}".strip()
