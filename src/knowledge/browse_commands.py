"""Implementation of ``know browse`` commands.

Each command retrieves data from both local store and remote APIs,
annotates items with sync status, and emits television-formatted output.
"""

from __future__ import annotations

import asyncio
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
    format_follow_preview,
    format_follow_television,
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


_FOLLOW_MAX_CONCURRENT_REQUESTS = 8


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
    repo_arg = getattr(args, "repo", None) or _repo_name_from_selected_row(getattr(args, "selected_row", None))

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
    """Resolve GitHub token from env, store credentials, or ``gh`` CLI."""
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
    # Fall back to the ``gh`` CLI auth token
    try:
        import subprocess

        result = subprocess.run(
            ["gh", "auth", "token"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
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


def _repo_name_from_selected_row(selected_row: str | None) -> str:
    """Extract ``owner/repo`` from a Television row emitted by GitHub repo browse."""
    if not selected_row:
        return ""
    import re

    clean = re.sub(r"\033\[[0-9;]*m", "", selected_row)
    first_segment = clean.split(" | ", 1)[0].strip()
    first_segment = first_segment.lstrip("●○ ").strip()
    return first_segment


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


# ── Confluence spaces browse ─────────────────────────────────────────────

def cmd_browse_confluence_spaces(args: Namespace) -> object:
    """List Confluence spaces from all registered Confluence sources."""
    from .browse_tv import (
        format_confluence_spaces_preview,
        format_confluence_spaces_television,
    )

    store = _store_from_args(args)
    store.initialize()
    sources = store.list_collection_sources(source_type="confluence")
    fmt = getattr(args, "format", "json")
    entry = getattr(args, "entry", None)

    seen: set[str] = set()
    all_spaces: list[dict[str, Any]] = []

    for source in sources:
        config = source.get("config", {})
        base_url = config.get("base_url")
        if not base_url or not config.get("username") or not config.get("token"):
            continue
        try:
            from .sources.confluence import list_confluence_spaces

            spaces = list_confluence_spaces(
                base_url=base_url,
                username=store.resolve_key(config["username"]),
                token=store.resolve_key(config["token"]),
            )
            for space in spaces:
                key = str(space.get("key", ""))
                if key and key not in seen:
                    seen.add(key)
                    all_spaces.append(space)
        except Exception:
            pass

    if fmt == "television":
        return format_confluence_spaces_television(all_spaces)
    if fmt == "television-preview":
        return format_confluence_spaces_preview(all_spaces, entry)
    return {"spaces": all_spaces}


# ── Confluence pages (path-style) browse ─────────────────────────────────

def cmd_browse_confluence_pages(args: Namespace) -> object:
    """List Confluence pages as ``/path/title`` for a given space."""
    from .browse_tv import (
        format_confluence_pages_preview,
        format_confluence_pages_television,
    )

    store = _store_from_args(args)
    store.initialize()
    fmt = getattr(args, "format", "json")
    entry = getattr(args, "entry", None)
    space_filter = getattr(args, "space", None)

    # Derive space from --selected-row when drilling in from cspaces
    if not space_filter:
        selected_row = getattr(args, "selected_row", None)
        if selected_row:
            import re
            clean = re.sub(r"\033\[[0-9;]*m", "", selected_row)
            first = clean.split("|")[0].strip()
            if first:
                space_filter = first

    sources = store.list_collection_sources(source_type="confluence")

    all_pages: list[dict[str, Any]] = []

    for source in sources:
        config = source.get("config", {})
        base_url = config.get("base_url")
        if not base_url or not config.get("username") or not config.get("token"):
            continue
        source_space = config.get("space") or config.get("space_key")
        if space_filter and source_space != space_filter:
            continue
        try:
            from .sources.confluence import list_confluence_pages

            pages = list_confluence_pages(
                base_url=base_url,
                username=store.resolve_key(config["username"]),
                token=store.resolve_key(config["token"]),
                space=space_filter or source_space or "",
            )
            all_pages.extend(pages)
        except Exception:
            pass

    if fmt == "television":
        return format_confluence_pages_television(all_pages)
    if fmt == "television-preview":
        return format_confluence_pages_preview(all_pages, entry)
    return {"pages": all_pages}


# ── Jira projects browse ────────────────────────────────────────────────

def cmd_browse_jira_projects(args: Namespace) -> object:
    """List Jira projects from all registered Jira sources."""
    from .browse_tv import (
        format_jira_projects_preview,
        format_jira_projects_television,
    )

    store = _store_from_args(args)
    store.initialize()
    sources = store.list_collection_sources(source_type="jira")
    fmt = getattr(args, "format", "json")
    entry = getattr(args, "entry", None)

    seen: set[str] = set()
    all_projects: list[dict[str, Any]] = []

    for source in sources:
        config = source.get("config", {})
        base_url = config.get("base_url")
        if not base_url or not config.get("username") or not config.get("token"):
            continue
        try:
            from .sources.jira import list_jira_projects

            projects = list_jira_projects(
                base_url=base_url,
                username=store.resolve_key(config["username"]),
                token=store.resolve_key(config["token"]),
            )
            for proj in projects:
                key = str(proj.get("key", ""))
                if key and key not in seen:
                    seen.add(key)
                    all_projects.append(proj)
        except Exception:
            pass

    if fmt == "television":
        return format_jira_projects_television(all_projects)
    if fmt == "television-preview":
        return format_jira_projects_preview(all_projects, entry)
    return {"projects": all_projects}


# ── Follow browse ────────────────────────────────────────────────────────

def cmd_browse_follow(args: Namespace) -> object:
    """List open items from GitHub repos and Jira projects interacted with in the last 6 months.

    Each item is presented as a path:
    ``github/<repo>/<element_type>/<id>`` or
    ``jira/<project>/<issue_type>/<key>``.

    Only open items are included (not closed, done, or merged).
    """
    from datetime import datetime, timedelta, timezone

    store = _store_from_args(args)
    store.initialize()
    fmt = getattr(args, "format", "json")
    entry = getattr(args, "entry", None)

    # ── Fast-path for preview: resolve directly from path ────────────
    if fmt == "television-preview" and entry:
        return _follow_preview_fast(entry, store)

    six_months_ago = datetime.now(timezone.utc) - timedelta(days=180)
    six_months_iso = six_months_ago.strftime("%Y-%m-%dT%H:%M:%S%z")

    items = asyncio.run(_collect_follow_items(store, six_months_iso))

    if fmt == "television":
        return format_follow_television(items)
    if fmt == "television-preview":
        return format_follow_preview(items, entry, store)
    return {"items": items}


async def _collect_follow_items(
    store: KnowledgeStore,
    six_months_iso: str,
) -> list[dict[str, Any]]:
    """Collect follow items from GitHub and Jira concurrently."""
    token = _resolve_github_token(store)
    jira_sources = store.list_collection_sources(source_type="jira")

    github_items, jira_items = await asyncio.gather(
        _fetch_github_follow_items(token, six_months_iso),
        _fetch_jira_follow_items(store, jira_sources),
    )
    return [*github_items, *jira_items]


async def _fetch_github_follow_items(
    token: str | None,
    six_months_iso: str,
) -> list[dict[str, Any]]:
    """Fetch follow items from recent GitHub repositories."""
    if not token:
        return []

    try:
        from .sources.github_api import list_user_repos

        repos = await asyncio.to_thread(list_user_repos, token, per_page=100)
    except Exception:
        return []

    semaphore = asyncio.Semaphore(_FOLLOW_MAX_CONCURRENT_REQUESTS)
    tasks: list[asyncio.Future[list[dict[str, Any]]] | asyncio.Task[list[dict[str, Any]]]] = []
    for repo in repos:
        updated = repo.get("updated_at") or repo.get("pushed_at") or ""
        if updated and updated < six_months_iso:
            continue
        full_name = repo.get("full_name", "")
        if not full_name or "/" not in full_name:
            continue
        owner, repo_name = full_name.split("/", 1)
        tasks.append(
            asyncio.create_task(
                _fetch_github_repo_follow_items(
                    token,
                    full_name,
                    owner,
                    repo_name,
                    semaphore,
                )
            )
        )
    if not tasks:
        return []

    results = await asyncio.gather(*tasks)
    return [item for batch in results for item in batch]


async def _fetch_github_repo_follow_items(
    token: str,
    full_name: str,
    owner: str,
    repo_name: str,
    semaphore: asyncio.Semaphore,
) -> list[dict[str, Any]]:
    """Fetch follow items for one GitHub repository."""
    try:
        from .sources.github_api import list_repo_activity

        async with semaphore:
            activity = await asyncio.to_thread(
                list_repo_activity,
                token,
                owner,
                repo_name,
                state="open",
                per_page=50,
            )
    except Exception:
        return []

    items: list[dict[str, Any]] = []
    for act in activity:
        kind = act.get("kind", "issue")
        number = act.get("number", 0)
        title = act.get("title", "")
        items.append({
            "source": "github",
            "repo": full_name,
            "element_type": kind,
            "id": str(number),
            "title": title,
            "url": act.get("url", ""),
            "user": act.get("user", ""),
            "created_at": act.get("created_at", ""),
            "updated_at": act.get("updated_at", ""),
            "body": act.get("body") or "",
            "labels": act.get("labels", []),
            "comments_count": act.get("comments_count", 0),
            "state": act.get("state", "open"),
            "path": f"github/{full_name}/{kind}/{number}",
        })
    return items


async def _fetch_jira_follow_items(
    store: KnowledgeStore,
    jira_sources: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Fetch follow items from Jira sources concurrently."""
    semaphore = asyncio.Semaphore(_FOLLOW_MAX_CONCURRENT_REQUESTS)
    tasks: list[asyncio.Future[list[dict[str, Any]]] | asyncio.Task[list[dict[str, Any]]]] = []
    for source in jira_sources:
        tasks.append(asyncio.create_task(_fetch_jira_source_follow_items(store, source, semaphore)))
    if not tasks:
        return []

    results = await asyncio.gather(*tasks)
    return [item for batch in results for item in batch]


async def _fetch_jira_source_follow_items(
    store: KnowledgeStore,
    source: dict[str, Any],
    semaphore: asyncio.Semaphore,
) -> list[dict[str, Any]]:
    """Fetch follow items for one Jira source."""
    config = source.get("config", {})
    base_url = config.get("base_url")
    username_ref = config.get("username")
    token_ref = config.get("token")
    if not (base_url and username_ref and token_ref):
        return []

    try:
        from .sources.jira import search_jira

        username = store.resolve_key(username_ref)
        jira_token = store.resolve_key(token_ref)
        project = config.get("project", "")
        jql = (
            f"project = {project} AND statusCategory != Done "
            f"AND updated >= '-26w' ORDER BY updated DESC"
        )
        async with semaphore:
            results = await asyncio.to_thread(
                search_jira,
                base_url=base_url,
                username=username,
                token=jira_token,
                jql=jql,
                limit=int(config.get("limit", 50)),
                fields=[
                    "summary", "status", "issuetype", "priority",
                    "assignee", "reporter", "labels", "created", "updated",
                    "description",
                ],
            )
    except Exception:
        return []

    done_categories = {"done", "complete", "completed", "closed", "resolved"}
    items: list[dict[str, Any]] = []
    for issue in results.get("issues", []):
        key = issue.get("key", "")
        fields = issue.get("fields", {}) or {}
        status_name = _field_name(fields.get("status"))
        status_cat = ""
        status_obj = fields.get("status")
        if isinstance(status_obj, dict):
            cat_obj = status_obj.get("statusCategory") or {}
            status_cat = (cat_obj.get("name") or "").lower()
        if status_cat in done_categories:
            continue
        summary = str(fields.get("summary") or key)
        issue_type = _field_name(fields.get("issuetype")) or "task"
        description_body = ""
        raw_desc = fields.get("description")
        if raw_desc:
            try:
                from .sources.jira import _adf_to_markdown

                description_body = _adf_to_markdown(raw_desc)
            except Exception:
                description_body = str(raw_desc) if not isinstance(raw_desc, dict) else ""
        normalized_issue_type = issue_type.lower().replace(" ", "_")
        items.append({
            "source": "jira",
            "project": project,
            "element_type": normalized_issue_type,
            "id": key,
            "title": summary,
            "url": f"{base_url.rstrip('/')}/browse/{key}",
            "status": status_name,
            "priority": _field_name(fields.get("priority")),
            "assignee": _display_name(fields.get("assignee")),
            "reporter": _display_name(fields.get("reporter")),
            "labels": fields.get("labels") or [],
            "created_at": fields.get("created") or "",
            "updated_at": fields.get("updated") or "",
            "body": description_body,
            "state": "open",
            "path": f"jira/{project}/{normalized_issue_type}/{key}",
        })
    return items


def _follow_preview_fast(entry: str, store: KnowledgeStore) -> str:
    """Render a preview for a follow entry without re-querying all APIs.

    Parses the path (``github/owner/repo/kind/number`` or
    ``jira/PROJECT/type/KEY``) and fetches only the single item needed.
    """
    import re

    clean = re.sub(r"\033\[[0-9;]*m", "", entry).strip()
    for icon in ("🔵", "🟢", "💬", "🔷", "●"):
        clean = clean.lstrip(icon).strip()
    parts = clean.split()
    path = parts[0] if parts else clean
    segments = [s for s in path.split("/") if s]

    if not segments:
        return "No item matched.\n"

    source = segments[0]

    if source == "github" and len(segments) >= 5:
        owner, repo_name, kind, number = segments[1], segments[2], segments[3], segments[4]
        token = _resolve_github_token(store)
        if not token:
            return "GitHub token not configured.\n"
        try:
            from .sources.github_api import list_repo_issues, list_repo_pulls, list_repo_discussions

            item_data: dict[str, Any] | None = None
            num = int(number)
            if kind == "pull_request":
                from .sources.github_api import get_pr_detail
                pr = get_pr_detail(token, owner, repo_name, num)
                item_data = {
                    "kind": "pull_request", "number": num,
                    "title": pr.get("title", ""),
                    "body": pr.get("body") or "",
                    "user": (pr.get("user") or {}).get("login", ""),
                    "created_at": pr.get("created_at", ""),
                    "updated_at": pr.get("updated_at", ""),
                    "state": pr.get("state", "open"),
                    "labels": [l.get("name", "") for l in pr.get("labels", [])],
                    "url": pr.get("html_url", ""),
                }
            elif kind == "discussion":
                discussions = list_repo_discussions(token, owner, repo_name, per_page=50)
                for d in discussions:
                    if d.get("number") == num:
                        item_data = {
                            "kind": "discussion", "number": num,
                            "title": d.get("title", ""),
                            "body": d.get("body") or "",
                            "user": (d.get("author") or {}).get("login", ""),
                            "created_at": d.get("createdAt", ""),
                            "updated_at": d.get("updatedAt", ""),
                            "state": "open",
                            "labels": [],
                            "url": d.get("url", ""),
                        }
                        break
            else:
                # Issue
                import requests
                resp = requests.get(
                    f"https://api.github.com/repos/{owner}/{repo_name}/issues/{num}",
                    headers={
                        "Accept": "application/vnd.github+json",
                        "Authorization": f"Bearer {token}",
                        "X-GitHub-Api-Version": "2022-11-28",
                    },
                    timeout=10,
                )
                resp.raise_for_status()
                issue = resp.json()
                item_data = {
                    "kind": "issue", "number": num,
                    "title": issue.get("title", ""),
                    "body": issue.get("body") or "",
                    "user": (issue.get("user") or {}).get("login", ""),
                    "created_at": issue.get("created_at", ""),
                    "updated_at": issue.get("updated_at", ""),
                    "state": issue.get("state", "open"),
                    "labels": [l.get("name", "") for l in issue.get("labels", [])],
                    "url": issue.get("html_url", ""),
                }

            if item_data:
                kind_label = {
                    "issue": "Issue", "pull_request": "Pull Request",
                    "discussion": "Discussion",
                }.get(item_data["kind"], "Item")
                lines = [
                    f"# [{kind_label} #{num}] {item_data['title']}",
                    "",
                    f"- Repo: {owner}/{repo_name}",
                    f"- Author: @{item_data['user']}",
                    f"- Created: {item_data['created_at']}",
                    f"- Updated: {item_data.get('updated_at', '')}",
                    f"- State: {item_data['state']}",
                ]
                if item_data.get("labels"):
                    lines.append(f"- Labels: {', '.join(item_data['labels'])}")
                if item_data.get("url"):
                    lines.append(f"- URL: {item_data['url']}")
                body = item_data.get("body") or ""
                if body.strip():
                    lines.extend(["", "## Description", "", body.strip()])
                return "\n".join(lines) + "\n"
        except Exception:
            pass
        return f"Could not load GitHub {kind} #{number}.\n"

    elif source == "jira" and len(segments) >= 4:
        issue_key = segments[3]
        project = segments[1]
        issue_type = segments[2]
        # Find Jira credentials from registered sources
        jira_sources = store.list_collection_sources(source_type="jira")
        for src in jira_sources:
            config = src.get("config", {})
            base_url = config.get("base_url")
            if not (base_url and config.get("username") and config.get("token")):
                continue
            try:
                from .sources.jira import search_jira, _adf_to_markdown

                username = store.resolve_key(config["username"])
                jira_token = store.resolve_key(config["token"])
                results = search_jira(
                    base_url=base_url, username=username, token=jira_token,
                    jql=f"key = {issue_key}",
                    fields=[
                        "summary", "status", "issuetype", "priority",
                        "assignee", "reporter", "labels", "created",
                        "updated", "description",
                    ],
                    limit=1,
                )
                issues = results.get("issues", [])
                if issues:
                    issue = issues[0]
                    fields = issue.get("fields", {}) or {}
                    summary = str(fields.get("summary") or issue_key)
                    desc = ""
                    if fields.get("description"):
                        try:
                            desc = _adf_to_markdown(fields["description"])
                        except Exception:
                            pass
                    lines = [
                        f"# {issue_key}: {summary}",
                        "",
                        f"- Project: {project}",
                        f"- Type: {issue_type}",
                        f"- Status: {_field_name(fields.get('status'))}",
                        f"- Priority: {_field_name(fields.get('priority'))}",
                        f"- Assignee: {_display_name(fields.get('assignee'))}",
                        f"- Reporter: {_display_name(fields.get('reporter'))}",
                    ]
                    labels = fields.get("labels") or []
                    if labels:
                        lines.append(f"- Labels: {', '.join(labels)}")
                    lines.append(f"- URL: {base_url.rstrip('/')}/browse/{issue_key}")
                    if desc.strip():
                        lines.extend(["", "## Description", "", desc.strip()])
                    return "\n".join(lines) + "\n"
            except Exception:
                pass
        return f"Could not load Jira issue {issue_key}.\n"

    return "No item matched.\n"


def cmd_browse_follow_open(args: Namespace) -> object:
    """Resolve the URL from a follow television row and print it to stdout.

    The cable TOML is responsible for piping this URL to the OS-specific
    open command (``start``, ``open``, ``xdg-open``, etc.), which makes
    the solution portable without changing Python code.
    """
    import re

    selected = getattr(args, "selected_row", "") or ""
    clean = re.sub(r"\033\[[0-9;]*m", "", selected).strip()

    # Take only the path part (first space-separated token)
    parts = clean.split()
    clean = parts[0] if parts else clean

    # Remove leading icon characters
    for icon in ("🔵", "🟢", "💬", "🔷", "●"):
        clean = clean.lstrip(icon).strip()

    url = _resolve_follow_url(clean, args)
    if url:
        return url
    return ""


def _resolve_follow_url(path: str, args: Namespace) -> str | None:
    """Resolve a web URL from a follow path string.

    Paths look like:
    - ``github/owner/repo/issue/123/title``
    - ``github/owner/repo/pull_request/45/title``
    - ``github/owner/repo/discussion/67``
    - ``jira/PROJECT/type/KEY-123``
    """
    parts = [p for p in path.split("/") if p]
    if len(parts) < 4:
        return None

    source = parts[0]

    if source == "github":
        if len(parts) < 5:
            return None
        owner = parts[1]
        repo = parts[2]
        kind = parts[3]
        number = parts[4]
        if kind == "pull_request":
            return f"https://github.com/{owner}/{repo}/pull/{number}"
        elif kind == "discussion":
            return f"https://github.com/{owner}/{repo}/discussions/{number}"
        else:
            return f"https://github.com/{owner}/{repo}/issues/{number}"

    elif source == "jira":
        # jira/PROJECT/type/KEY-123
        issue_key = parts[3]
        # Try to find the base_url from registered sources
        store = _store_from_args(args)
        store.initialize()
        jira_sources = store.list_collection_sources(source_type="jira")
        for src in jira_sources:
            config = src.get("config", {})
            base_url = config.get("base_url")
            if base_url:
                return f"{base_url.rstrip('/')}/browse/{issue_key}"
        return None

    return None
