"""Implementation of ``know browse`` commands.

Each command retrieves data from both local store and remote APIs,
annotates items with sync status, and emits television-formatted output.
"""

from __future__ import annotations

import os
from argparse import Namespace
from pathlib import Path
from typing import Any

from .browse_tv import (
    format_aha_browse_preview,
    format_aha_browse_television,
    format_arxiv_browse_preview,
    format_arxiv_browse_television,
    format_confluence_browse_preview,
    format_confluence_browse_television,
    format_github_activity_preview,
    format_github_activity_television,
    format_github_repos_preview,
    format_github_repos_television,
    format_jira_browse_preview,
    format_jira_browse_television,
    format_local_browse_preview,
    format_local_browse_television,
    format_releases_browse_preview,
    format_releases_browse_television,
    format_sites_browse_preview,
    format_sites_browse_television,
    format_videos_browse_preview,
    format_videos_browse_television,
)
from .store import KnowledgeStore


def _store_from_args(args: Namespace) -> KnowledgeStore:
    """Create a ``KnowledgeStore`` from parsed CLI arguments."""
    return KnowledgeStore(args.store)


def _config_value_or_env(explicit: str | None, env_name: str) -> str | None:
    """Return explicit value, ``$env:`` reference, or ``None``."""
    if explicit is not None:
        return explicit
    if os.getenv(env_name):
        return f"$env:{env_name}"
    return None


def _strip_yaml_frontmatter(text: str) -> str:
    """Remove leading ``---`` delimited YAML frontmatter."""
    if not text.startswith("---"):
        return text
    end = text.find("\n---", 3)
    if end == -1:
        return text
    return text[end + 4:].lstrip("\n")


# ── Jira browse ──────────────────────────────────────────────────────────

def cmd_browse_jira(args: Namespace) -> object:
    """List Jira issues across registered projects with sync status."""
    store = _store_from_args(args)
    store.initialize()
    sources = store.list_collection_sources(
        key_name=getattr(args, "key", None),
        source_type="jira",
    )
    fmt = getattr(args, "format", "json")
    entry = getattr(args, "entry", None)

    all_issues: list[dict[str, Any]] = []

    for source in sources:
        config = source.get("config", {})
        base_url = config.get("base_url")
        username_ref = config.get("username")
        token_ref = config.get("token")

        # Get local synced files
        local_keys: set[str] = set()
        try:
            source_dir = store.source_dir(source)
            for md_file in source_dir.glob("**/*.md"):
                stem = md_file.stem
                local_keys.add(stem)
        except Exception:
            pass

        # Try fetching from API
        if base_url and username_ref and token_ref:
            try:
                from .sources.jira import search_jira

                username = store.resolve_key(username_ref)
                token = store.resolve_key(token_ref)
                project = config.get("project")
                jql = config.get("jql") or f"project = {project} ORDER BY updated DESC"
                results = search_jira(
                    base_url=base_url,
                    username=username,
                    token=token,
                    jql=jql,
                    limit=int(config.get("limit", 50)),
                )
                for issue in results.get("issues", []):
                    key = issue.get("key", "")
                    fields = issue.get("fields", {}) or {}
                    all_issues.append({
                        "key": key,
                        "summary": str(fields.get("summary") or key),
                        "status": _field_name(fields.get("status")),
                        "issue_type": _field_name(fields.get("issuetype")),
                        "priority": _field_name(fields.get("priority")),
                        "assignee": _display_name(fields.get("assignee")),
                        "reporter": _display_name(fields.get("reporter")),
                        "labels": fields.get("labels") or [],
                        "description": str(fields.get("description") or ""),
                        "web_url": f"{base_url.rstrip('/')}/browse/{key}",
                        "synced": key in local_keys,
                        "local_path": str(store.source_dir(source) / f"{key}.md") if key in local_keys else None,
                        "source_id": source.get("id"),
                        "knowledge_key": source.get("key"),
                        "project": project,
                    })
            except Exception:
                # Fall back to local-only
                _add_local_jira_issues(store, source, all_issues, local_keys)
        else:
            _add_local_jira_issues(store, source, all_issues, local_keys)

    if fmt == "television":
        return format_jira_browse_television(all_issues)
    if fmt == "television-preview":
        return format_jira_browse_preview(all_issues, entry)
    return {"issues": all_issues}


def _add_local_jira_issues(
    store: KnowledgeStore,
    source: dict[str, Any],
    all_issues: list[dict[str, Any]],
    local_keys: set[str],
) -> None:
    """Add locally synced Jira issues to the list."""
    for key in sorted(local_keys):
        all_issues.append({
            "key": key,
            "summary": key,
            "status": "unknown",
            "issue_type": "unknown",
            "priority": "unknown",
            "assignee": "unknown",
            "reporter": "unknown",
            "labels": [],
            "description": "",
            "synced": True,
            "source_id": source.get("id"),
            "knowledge_key": source.get("key"),
            "project": source.get("config", {}).get("project"),
        })


# ── Confluence browse ────────────────────────────────────────────────────

def cmd_browse_confluence(args: Namespace) -> object:
    """List Confluence pages with sync status."""
    store = _store_from_args(args)
    store.initialize()
    sources = store.list_collection_sources(
        key_name=getattr(args, "key", None),
        source_type="confluence",
    )
    fmt = getattr(args, "format", "json")
    entry = getattr(args, "entry", None)

    all_pages: list[dict[str, Any]] = []

    for source in sources:
        config = source.get("config", {})
        local_titles: set[str] = set()
        local_bodies: dict[str, str] = {}

        try:
            source_dir = store.source_dir(source)
            for md_file in source_dir.glob("**/*.md"):
                text = md_file.read_text(encoding="utf-8")
                title = _extract_frontmatter_field(text, "title") or md_file.stem
                local_titles.add(title)
                local_bodies[title] = _strip_yaml_frontmatter(text)
        except Exception:
            pass

        # Try fetching from API
        base_url = config.get("base_url")
        if base_url and config.get("username") and config.get("token"):
            try:
                from .sources.confluence import search_confluence

                space = config.get("space") or config.get("space_key")
                results = search_confluence(
                    base_url=base_url,
                    username=store.resolve_key(config["username"]),
                    token=store.resolve_key(config["token"]),
                    query=" ",
                    space=space,
                    limit=50,
                )
                for result in results.get("results", []):
                    content = result.get("content", {}) or {}
                    title = str(content.get("title") or "Untitled")
                    excerpt = str(result.get("excerpt") or "")
                    synced = title in local_titles
                    all_pages.append({
                        "title": title,
                        "space": space or "",
                        "synced": synced,
                        "web_url": _confluence_webui(base_url, content),
                        "excerpt": excerpt,
                        "body": local_bodies.get(title, ""),
                    })
            except Exception:
                _add_local_confluence(local_titles, local_bodies, source, all_pages)
        else:
            _add_local_confluence(local_titles, local_bodies, source, all_pages)

    if fmt == "television":
        return format_confluence_browse_television(all_pages)
    if fmt == "television-preview":
        return format_confluence_browse_preview(all_pages, entry)
    return {"pages": all_pages}


def _add_local_confluence(
    local_titles: set[str],
    local_bodies: dict[str, str],
    source: dict[str, Any],
    all_pages: list[dict[str, Any]],
) -> None:
    config = source.get("config", {})
    for title in sorted(local_titles):
        all_pages.append({
            "title": title,
            "space": config.get("space") or config.get("space_key") or "",
            "synced": True,
            "body": local_bodies.get(title, ""),
        })


# ── GitHub browse ────────────────────────────────────────────────────────

def cmd_browse_github(args: Namespace) -> object:
    """List GitHub repos the user has interacted with."""
    store = _store_from_args(args)
    store.initialize()
    fmt = getattr(args, "format", "json")
    entry = getattr(args, "entry", None)

    token = _resolve_github_token(store)

    # Get locally registered repos
    local_repos: set[str] = set()
    sources = store.list_collection_sources(source_type="github")
    for source in sources:
        url = source.get("config", {}).get("repo_url", "")
        repo_name = _repo_name_from_url(url)
        if repo_name:
            local_repos.add(repo_name.lower())

    repos: list[dict[str, Any]] = []
    if token:
        try:
            from .sources.github_api import list_user_repos

            raw_repos = list_user_repos(token, per_page=50)
            for repo in raw_repos:
                full_name = repo.get("full_name", "")
                repos.append({
                    **repo,
                    "synced": full_name.lower() in local_repos,
                })
        except Exception:
            pass

    # Add local-only repos not in API response
    api_names = {r.get("full_name", "").lower() for r in repos}
    for source in sources:
        url = source.get("config", {}).get("repo_url", "")
        name = _repo_name_from_url(url)
        if name and name.lower() not in api_names:
            repos.append({
                "full_name": name,
                "description": f"Local source: {source.get('id', '')}",
                "language": "",
                "stargazers_count": 0,
                "forks_count": 0,
                "open_issues_count": 0,
                "html_url": url,
                "synced": True,
                "updated_at": source.get("updated_at", ""),
            })

    if fmt == "television":
        return format_github_repos_television(repos)
    if fmt == "television-preview":
        return format_github_repos_preview(repos, entry)
    return {"repos": repos}


def cmd_browse_github_activity(args: Namespace) -> object:
    """List issues, PRs, and discussions for a specific GitHub repo."""
    store = _store_from_args(args)
    store.initialize()
    fmt = getattr(args, "format", "json")
    entry = getattr(args, "entry", None)
    repo_arg = getattr(args, "repo", "")

    # Parse owner/repo
    owner, repo = _parse_owner_repo(repo_arg)
    if not owner or not repo:
        return "Invalid repo format. Use owner/repo.\n"

    token = _resolve_github_token(store)
    if not token:
        return "GitHub token not configured. Set GITHUB_TOKEN or use `know set credential github_token <TOKEN>`.\n"

    from .sources.github_api import list_repo_activity, render_issue_thread_markdown

    items = list_repo_activity(token, owner, repo, per_page=30)

    if fmt == "television":
        return format_github_activity_television(items)
    if fmt == "television-preview":
        # Find the selected item and render full thread
        item = _find_activity_item(items, entry)
        if item:
            thread_md = render_issue_thread_markdown(token, owner, repo, item)
            return format_github_activity_preview(items, entry, thread_md=thread_md)
        return format_github_activity_preview(items, entry)
    return {"repo": f"{owner}/{repo}", "items": items}


# ── arXiv browse ─────────────────────────────────────────────────────────

def cmd_browse_arxiv(args: Namespace) -> object:
    """List arXiv papers with sync status."""
    store = _store_from_args(args)
    store.initialize()
    sources = store.list_collection_sources(
        key_name=getattr(args, "key", None),
        source_type="arxiv",
    )
    fmt = getattr(args, "format", "json")
    entry = getattr(args, "entry", None)

    papers: list[dict[str, Any]] = []
    for source in sources:
        has_files = False
        try:
            source_dir = store.source_dir(source)
            has_files = any(source_dir.glob("**/*.md"))
        except Exception:
            pass

        config = source.get("config", {})
        papers.append({
            "title": source.get("title", config.get("url", "Unknown")),
            "primary_category": "",
            "published": source.get("created_at", ""),
            "synced": has_files,
            "url": config.get("url", ""),
            "pdf_url": config.get("url", "").replace("/abs/", "/pdf/") if "/abs/" in config.get("url", "") else "",
            "authors": [],
            "summary": "",
        })

    if fmt == "television":
        return format_arxiv_browse_television(papers)
    if fmt == "television-preview":
        return format_arxiv_browse_preview(papers, entry)
    return {"papers": papers}


# ── Aha browse ───────────────────────────────────────────────────────────

def cmd_browse_aha(args: Namespace) -> object:
    """List Aha features with sync status."""
    store = _store_from_args(args)
    store.initialize()
    sources = store.list_collection_sources(
        key_name=getattr(args, "key", None),
        source_type="aha",
    )
    fmt = getattr(args, "format", "json")
    entry = getattr(args, "entry", None)

    features: list[dict[str, Any]] = []
    for source in sources:
        has_files = False
        try:
            source_dir = store.source_dir(source)
            has_files = any(source_dir.glob("**/*.json"))
        except Exception:
            pass

        features.append({
            "reference_num": source.get("title", ""),
            "name": source.get("title", "Unknown"),
            "status": "",
            "synced": has_files,
        })

    if fmt == "television":
        return format_aha_browse_television(features)
    if fmt == "television-preview":
        return format_aha_browse_preview(features, entry)
    return {"features": features}


# ── Google Releases browse ──────────────────────────────────────────────

def cmd_browse_releases(args: Namespace) -> object:
    """List Google Cloud release notes with sync status."""
    store = _store_from_args(args)
    store.initialize()
    sources = store.list_collection_sources(
        key_name=getattr(args, "key", None),
        source_type="google_releases",
    )
    fmt = getattr(args, "format", "json")
    entry = getattr(args, "entry", None)

    entries: list[dict[str, Any]] = []
    for source in sources:
        try:
            source_dir = store.source_dir(source)
            for md_file in sorted(source_dir.glob("entries/*.md")):
                text = md_file.read_text(encoding="utf-8")
                title = _extract_frontmatter_field(text, "title") or md_file.stem
                body = _strip_yaml_frontmatter(text)
                entries.append({
                    "title": title,
                    "updated": _extract_frontmatter_field(text, "entry_updated") or "",
                    "products": [],
                    "url": _extract_frontmatter_field(text, "entry_url") or "",
                    "synced": True,
                    "body": body,
                })
        except Exception:
            pass

    if fmt == "television":
        return format_releases_browse_television(entries)
    if fmt == "television-preview":
        return format_releases_browse_preview(entries, entry)
    return {"entries": entries}


# ── Videos browse ────────────────────────────────────────────────────────

def cmd_browse_videos(args: Namespace) -> object:
    """List video sources with sync status."""
    store = _store_from_args(args)
    store.initialize()
    sources = store.list_collection_sources(
        key_name=getattr(args, "key", None),
        source_type="video",
    )
    fmt = getattr(args, "format", "json")
    entry = getattr(args, "entry", None)

    videos: list[dict[str, Any]] = []
    for source in sources:
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

        config = source.get("config", {})
        videos.append({
            "title": source.get("title", config.get("url", "Unknown")),
            "url": config.get("url", ""),
            "synced": has_files,
            "body": body,
        })

    if fmt == "television":
        return format_videos_browse_television(videos)
    if fmt == "television-preview":
        return format_videos_browse_preview(videos, entry)
    return {"videos": videos}


# ── Sites browse ─────────────────────────────────────────────────────────

def cmd_browse_sites(args: Namespace) -> object:
    """List crawled site sources with sync status."""
    store = _store_from_args(args)
    store.initialize()
    sources = store.list_collection_sources(
        key_name=getattr(args, "key", None),
        source_type="site",
    )
    fmt = getattr(args, "format", "json")
    entry = getattr(args, "entry", None)

    sites: list[dict[str, Any]] = []
    for source in sources:
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

        config = source.get("config", {})
        sites.append({
            "title": source.get("title", config.get("url", "Unknown")),
            "url": config.get("url", ""),
            "synced": has_files,
            "body": body,
        })

    if fmt == "television":
        return format_sites_browse_television(sites)
    if fmt == "television-preview":
        return format_sites_browse_preview(sites, entry)
    return {"sites": sites}


# ── Local knowledge browse ──────────────────────────────────────────────

def cmd_browse_local(args: Namespace) -> object:
    """Browse all locally downloaded knowledge files."""
    store = _store_from_args(args)
    store.initialize()
    fmt = getattr(args, "format", "json")
    entry = getattr(args, "entry", None)
    key_filter = getattr(args, "key", None)
    type_filter = getattr(args, "type", None)

    sources = store.list_collection_sources(
        key_name=key_filter,
        source_type=type_filter,
    )

    items: list[dict[str, Any]] = []
    for source in sources:
        try:
            source_dir = store.source_dir(source)
            for md_file in sorted(source_dir.glob("**/*.md")):
                text = md_file.read_text(encoding="utf-8")
                title = _extract_frontmatter_field(text, "title") or md_file.stem
                body = _strip_yaml_frontmatter(text)
                items.append({
                    "title": title,
                    "source_type": source.get("type", ""),
                    "key": source.get("key", ""),
                    "path": str(md_file),
                    "body": body.strip(),
                })
        except Exception:
            pass

    if fmt == "television":
        return format_local_browse_television(items)
    if fmt == "television-preview":
        return format_local_browse_preview(items, entry)
    return {"items": items}


# ── Helpers ──────────────────────────────────────────────────────────────

def _resolve_github_token(store: KnowledgeStore) -> str | None:
    """Resolve GitHub token from env or store credentials."""
    token = os.getenv("GITHUB_TOKEN")
    if token:
        return token
    try:
        return store.resolve_key("$github_token")
    except Exception:
        pass
    try:
        return store.resolve_key("$GITHUB_TOKEN")
    except Exception:
        pass
    return None


def _repo_name_from_url(url: str) -> str | None:
    """Extract owner/repo from a Git URL."""
    from urllib.parse import urlparse

    parsed = urlparse(url)
    path = parsed.path.rstrip("/")
    if path.endswith(".git"):
        path = path[:-4]
    parts = path.strip("/").split("/")
    if len(parts) >= 2:
        return f"{parts[-2]}/{parts[-1]}"
    return None


def _parse_owner_repo(value: str) -> tuple[str, str]:
    """Parse 'owner/repo' or a full URL into (owner, repo)."""
    if "/" in value and not value.startswith("http"):
        parts = value.split("/")
        return parts[0], parts[1]
    name = _repo_name_from_url(value)
    if name:
        parts = name.split("/")
        return parts[0], parts[1]
    return "", ""


def _find_activity_item(
    items: list[dict[str, Any]], selected: str | None
) -> dict[str, Any] | None:
    """Find a GitHub activity item by number from selected text."""
    if not items:
        return None
    if not selected:
        return items[0]
    import re

    match = re.search(r"#(\d+)", selected)
    if match:
        num = int(match.group(1))
        for item in items:
            if item.get("number") == num:
                return item
    return items[0]


def _field_name(value: Any) -> str:
    if isinstance(value, dict):
        return str(value.get("name") or "unknown")
    return "unknown"


def _display_name(value: Any) -> str:
    if isinstance(value, dict):
        return str(
            value.get("displayName")
            or value.get("emailAddress")
            or value.get("accountId")
            or "unassigned"
        )
    return "unassigned"


def _extract_frontmatter_field(text: str, field: str) -> str | None:
    """Extract a field value from YAML frontmatter."""
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    fm = text[4:end]
    for line in fm.splitlines():
        if line.startswith(f"{field}:"):
            return line.split(":", 1)[1].strip().strip("'\"")
    return None


def _confluence_webui(base_url: str, content: dict[str, Any]) -> str:
    """Build a Confluence web URL from content _links."""
    links = content.get("_links", {})
    if isinstance(links, dict) and links.get("webui"):
        return f"{base_url.rstrip('/')}{links['webui']}"
    return ""
