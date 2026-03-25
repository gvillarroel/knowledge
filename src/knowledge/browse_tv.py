"""Television formatters for the ``know browse`` family of commands.

These formatters produce ANSI-colored output suitable for ``tv --ansi``
and provide sync-status visual cues (green = downloaded, yellow = remote).
"""

from __future__ import annotations

from typing import Any


# ANSI color codes
_GREEN = "\033[32m"
_YELLOW = "\033[33m"
_CYAN = "\033[36m"
_DIM = "\033[2m"
_RESET = "\033[0m"
_BOLD = "\033[1m"
_BLUE = "\033[34m"
_MAGENTA = "\033[35m"

_KIND_ICONS = {
    "issue": "🔵",
    "pull_request": "🟢",
    "discussion": "💬",
}

_KIND_COLORS = {
    "issue": _CYAN,
    "pull_request": _GREEN,
    "discussion": _MAGENTA,
}


# ── Jira sync browse ────────────────────────────────────────────────────

def format_jira_browse_television(issues: list[dict[str, Any]]) -> str:
    """Colored list of Jira issues: green=synced, yellow=remote only."""
    lines: list[str] = []
    for issue in issues:
        key = issue.get("key", "")
        summary = issue.get("summary", "")
        status = issue.get("status", "")
        synced = issue.get("synced", False)
        color = _GREEN if synced else _YELLOW
        marker = "●" if synced else "○"
        line = f"{color}{marker} {key}{_RESET} | {summary} | {_DIM}{status}{_RESET}"
        lines.append(line)
    return "\n".join(lines)


def format_jira_browse_preview(issues: list[dict[str, Any]], selected: str | None) -> str:
    """Preview pane for a selected Jira browse row."""
    issue = _find_jira_browse_issue(issues, selected)
    if not issue:
        return "No issue matched.\n"
    key = issue.get("key", "unknown")
    summary = issue.get("summary", key)
    synced = issue.get("synced", False)
    lines = [
        f"# {key}: {summary}",
        "",
        f"- Status: {issue.get('status', 'unknown')}",
        f"- Type: {issue.get('issue_type', 'unknown')}",
        f"- Priority: {issue.get('priority', 'unknown')}",
        f"- Assignee: {issue.get('assignee', 'unassigned')}",
        f"- Reporter: {issue.get('reporter', 'unknown')}",
        f"- Synced locally: {'✅ Yes' if synced else '❌ No'}",
    ]
    if issue.get("labels"):
        lines.append(f"- Labels: {', '.join(issue['labels'])}")
    if issue.get("web_url"):
        lines.append(f"- URL: {issue['web_url']}")
    description = issue.get("description", "")
    if description:
        lines.extend(["", "## Description", "", description])
    if synced and issue.get("local_path"):
        lines.extend(["", f"📁 Local: `{issue['local_path']}`"])
    return "\n".join(lines) + "\n"


def _find_jira_browse_issue(
    issues: list[dict[str, Any]], selected: str | None
) -> dict[str, Any] | None:
    if not issues:
        return None
    if not selected:
        return issues[0]
    for issue in issues:
        key = issue.get("key", "")
        if key and key in selected:
            return issue
    return issues[0]


# ── Confluence sync browse ───────────────────────────────────────────────

def format_confluence_browse_television(pages: list[dict[str, Any]]) -> str:
    """Colored list of Confluence pages: green=synced, yellow=remote."""
    lines: list[str] = []
    for page in pages:
        title = page.get("title", "Untitled")
        space = page.get("space", "")
        synced = page.get("synced", False)
        color = _GREEN if synced else _YELLOW
        marker = "●" if synced else "○"
        line = f"{color}{marker}{_RESET} {title} | {_DIM}{space}{_RESET}"
        lines.append(line)
    return "\n".join(lines)


def format_confluence_browse_preview(pages: list[dict[str, Any]], selected: str | None) -> str:
    page = _find_browse_item_by_title(pages, selected)
    if not page:
        return "No page matched.\n"
    title = page.get("title", "Untitled")
    synced = page.get("synced", False)
    lines = [
        f"# {title}",
        "",
        f"- Space: {page.get('space', 'unknown')}",
        f"- Synced locally: {'✅ Yes' if synced else '❌ No'}",
    ]
    if page.get("web_url"):
        lines.append(f"- URL: {page['web_url']}")
    if page.get("excerpt"):
        lines.extend(["", "## Excerpt", "", page["excerpt"]])
    if synced and page.get("body"):
        lines.extend(["", "## Content", "", page["body"]])
    return "\n".join(lines) + "\n"


# ── GitHub repos browse ─────────────────────────────────────────────────

def format_github_repos_television(repos: list[dict[str, Any]]) -> str:
    """List of GitHub repos with activity indicators."""
    lines: list[str] = []
    for repo in repos:
        full_name = repo.get("full_name", "")
        description = repo.get("description") or ""
        language = repo.get("language") or ""
        stars = repo.get("stargazers_count", 0)
        synced = repo.get("synced", False)
        color = _GREEN if synced else _CYAN
        marker = "●" if synced else "○"
        desc_short = (description[:60] + "…") if len(description) > 60 else description
        line = f"{color}{marker}{_RESET} {full_name} | {desc_short} | {_DIM}★{stars} {language}{_RESET}"
        lines.append(line)
    return "\n".join(lines)


def format_github_repos_preview(repos: list[dict[str, Any]], selected: str | None) -> str:
    repo = _find_browse_item_by_field(repos, "full_name", selected)
    if not repo:
        return "No repository matched.\n"
    name = repo.get("full_name", "unknown")
    lines = [
        f"# {name}",
        "",
        f"- Description: {repo.get('description') or 'No description'}",
        f"- Language: {repo.get('language') or 'unknown'}",
        f"- Stars: {repo.get('stargazers_count', 0)}",
        f"- Forks: {repo.get('forks_count', 0)}",
        f"- Open Issues: {repo.get('open_issues_count', 0)}",
        f"- Synced locally: {'✅ Yes' if repo.get('synced') else '❌ No'}",
        f"- URL: {repo.get('html_url', '')}",
        f"- Updated: {repo.get('updated_at', 'unknown')}",
    ]
    if repo.get("topics"):
        lines.append(f"- Topics: {', '.join(repo['topics'])}")
    lines.extend([
        "",
        "## Actions",
        "",
        f"- Press **Enter** to browse issues, PRs & discussions",
        f"- Sync: `know sync github-repo {repo.get('clone_url', '')} --key <KEY>`",
    ])
    return "\n".join(lines) + "\n"


# ── GitHub activity (issues/PRs/discussions) ─────────────────────────────

def format_github_activity_television(items: list[dict[str, Any]]) -> str:
    """Unified list of issues, PRs, discussions for a repo."""
    lines: list[str] = []
    for item in items:
        kind = item.get("kind", "issue")
        number = item.get("number", 0)
        title = item.get("title", "")
        user = item.get("user", "")
        comments = item.get("comments_count", 0)
        icon = _KIND_ICONS.get(kind, "●")
        color = _KIND_COLORS.get(kind, _CYAN)
        labels_str = ""
        if item.get("labels"):
            labels_str = f" [{', '.join(item['labels'][:3])}]"
        line = (
            f"{color}{icon} #{number}{_RESET} | {title}{labels_str} | "
            f"{_DIM}@{user} 💬{comments}{_RESET}"
        )
        lines.append(line)
    return "\n".join(lines)


def format_github_activity_preview(items: list[dict[str, Any]], selected: str | None, *, thread_md: str | None = None) -> str:
    """Preview with full thread markdown."""
    if thread_md:
        return thread_md
    item = _find_github_activity_item(items, selected)
    if not item:
        return "No item matched.\n"
    kind_label = {"issue": "Issue", "pull_request": "Pull Request", "discussion": "Discussion"}.get(item.get("kind", ""), "Item")
    lines = [
        f"# [{kind_label} #{item.get('number', 0)}] {item.get('title', '')}",
        "",
        f"- Author: @{item.get('user', 'unknown')}",
        f"- State: {item.get('state', 'open')}",
        f"- Created: {item.get('created_at', '')}",
        f"- Comments: {item.get('comments_count', 0)}",
    ]
    if item.get("labels"):
        lines.append(f"- Labels: {', '.join(item['labels'])}")
    if item.get("url"):
        lines.append(f"- URL: {item['url']}")
    body = item.get("body") or ""
    if body.strip():
        lines.extend(["", "## Description", "", body.strip()])
    return "\n".join(lines) + "\n"


def _find_github_activity_item(
    items: list[dict[str, Any]], selected: str | None
) -> dict[str, Any] | None:
    if not items:
        return None
    if not selected:
        return items[0]
    # Extract #number from selection
    import re
    match = re.search(r"#(\d+)", selected)
    if match:
        num = int(match.group(1))
        for item in items:
            if item.get("number") == num:
                return item
    return items[0]


# ── arXiv browse ─────────────────────────────────────────────────────────

def format_arxiv_browse_television(papers: list[dict[str, Any]]) -> str:
    """Colored list of arXiv papers: green=synced, yellow=remote."""
    lines: list[str] = []
    for paper in papers:
        title = paper.get("title", "Untitled")
        category = paper.get("primary_category", "")
        synced = paper.get("synced", False)
        color = _GREEN if synced else _YELLOW
        marker = "●" if synced else "○"
        line = f"{color}{marker}{_RESET} {title} | {_DIM}{category}{_RESET}"
        lines.append(line)
    return "\n".join(lines)


def format_arxiv_browse_preview(papers: list[dict[str, Any]], selected: str | None) -> str:
    paper = _find_browse_item_by_title(papers, selected)
    if not paper:
        return "No paper matched.\n"
    title = paper.get("title", "Untitled")
    synced = paper.get("synced", False)
    lines = [
        f"# {title}",
        "",
        f"- Authors: {', '.join(paper.get('authors', []))}",
        f"- Published: {paper.get('published', 'unknown')}",
        f"- Category: {paper.get('primary_category', 'unknown')}",
        f"- Synced locally: {'✅ Yes' if synced else '❌ No'}",
    ]
    if paper.get("pdf_url"):
        lines.append(f"- PDF: {paper['pdf_url']}")
    summary = paper.get("summary", "")
    if summary:
        lines.extend(["", "## Abstract", "", summary.strip()])
    return "\n".join(lines) + "\n"


# ── Aha browse ───────────────────────────────────────────────────────────

def format_aha_browse_television(features: list[dict[str, Any]]) -> str:
    """Colored list of Aha features: green=synced, yellow=remote."""
    lines: list[str] = []
    for feature in features:
        ref = feature.get("reference_num", "")
        name = feature.get("name", "Untitled")
        status = feature.get("status", "")
        synced = feature.get("synced", False)
        color = _GREEN if synced else _YELLOW
        marker = "●" if synced else "○"
        line = f"{color}{marker} {ref}{_RESET} | {name} | {_DIM}{status}{_RESET}"
        lines.append(line)
    return "\n".join(lines)


def format_aha_browse_preview(features: list[dict[str, Any]], selected: str | None) -> str:
    feature = _find_browse_item_by_field(features, "reference_num", selected)
    if not feature:
        return "No feature matched.\n"
    name = feature.get("name", "Untitled")
    lines = [
        f"# {feature.get('reference_num', '')}: {name}",
        "",
        f"- Status: {feature.get('status', 'unknown')}",
        f"- Synced locally: {'✅ Yes' if feature.get('synced') else '❌ No'}",
    ]
    if feature.get("description"):
        lines.extend(["", "## Description", "", feature["description"]])
    return "\n".join(lines) + "\n"


# ── Google Releases browse ──────────────────────────────────────────────

def format_releases_browse_television(entries: list[dict[str, Any]]) -> str:
    """Colored list of release notes: green=synced, yellow=remote."""
    lines: list[str] = []
    for entry in entries:
        title = entry.get("title", "Untitled")
        updated = entry.get("updated", "")
        synced = entry.get("synced", False)
        color = _GREEN if synced else _YELLOW
        marker = "●" if synced else "○"
        products = ", ".join(entry.get("products", [])[:3])
        line = f"{color}{marker}{_RESET} {title} | {_DIM}{products} {updated}{_RESET}"
        lines.append(line)
    return "\n".join(lines)


def format_releases_browse_preview(entries: list[dict[str, Any]], selected: str | None) -> str:
    entry = _find_browse_item_by_title(entries, selected)
    if not entry:
        return "No entry matched.\n"
    title = entry.get("title", "Untitled")
    lines = [
        f"# {title}",
        "",
        f"- Updated: {entry.get('updated', 'unknown')}",
        f"- Products: {', '.join(entry.get('products', []))}",
        f"- Synced locally: {'✅ Yes' if entry.get('synced') else '❌ No'}",
    ]
    if entry.get("url"):
        lines.append(f"- URL: {entry['url']}")
    if entry.get("body"):
        lines.extend(["", entry["body"]])
    return "\n".join(lines) + "\n"


# ── Videos browse ────────────────────────────────────────────────────────

def format_videos_browse_television(videos: list[dict[str, Any]]) -> str:
    """Colored list of video sources: green=synced, yellow=not."""
    lines: list[str] = []
    for video in videos:
        title = video.get("title", video.get("url", "Unknown"))
        synced = video.get("synced", False)
        color = _GREEN if synced else _YELLOW
        marker = "●" if synced else "○"
        line = f"{color}{marker}{_RESET} {title}"
        lines.append(line)
    return "\n".join(lines)


def format_videos_browse_preview(videos: list[dict[str, Any]], selected: str | None) -> str:
    video = _find_browse_item_by_title(videos, selected)
    if not video:
        return "No video matched.\n"
    title = video.get("title", "Unknown")
    lines = [
        f"# {title}",
        "",
        f"- URL: {video.get('url', 'unknown')}",
        f"- Synced locally: {'✅ Yes' if video.get('synced') else '❌ No'}",
    ]
    if video.get("body"):
        lines.extend(["", "## Transcription", "", video["body"]])
    return "\n".join(lines) + "\n"


# ── Sites browse ────────────────────────────────────────────────────────

def format_sites_browse_television(sites: list[dict[str, Any]]) -> str:
    """Colored list of crawled sites: green=synced, yellow=not."""
    lines: list[str] = []
    for site in sites:
        title = site.get("title", site.get("url", "Unknown"))
        synced = site.get("synced", False)
        color = _GREEN if synced else _YELLOW
        marker = "●" if synced else "○"
        line = f"{color}{marker}{_RESET} {title} | {_DIM}{site.get('url', '')}{_RESET}"
        lines.append(line)
    return "\n".join(lines)


def format_sites_browse_preview(sites: list[dict[str, Any]], selected: str | None) -> str:
    site = _find_browse_item_by_title(sites, selected)
    if not site:
        return "No site matched.\n"
    title = site.get("title", "Unknown")
    lines = [
        f"# {title}",
        "",
        f"- URL: {site.get('url', 'unknown')}",
        f"- Synced locally: {'✅ Yes' if site.get('synced') else '❌ No'}",
    ]
    if site.get("body"):
        lines.extend(["", "## Content", "", site["body"]])
    return "\n".join(lines) + "\n"


# ── Local knowledge browse ──────────────────────────────────────────────

def format_local_browse_television(items: list[dict[str, Any]]) -> str:
    """Browse all locally downloaded knowledge files."""
    lines: list[str] = []
    for item in items:
        title = item.get("title", "Untitled")
        source_type = item.get("source_type", "")
        key = item.get("key", "")
        color = {
            "jira": _CYAN,
            "confluence": _BLUE,
            "github": _GREEN,
            "arxiv": _MAGENTA,
            "video": _YELLOW,
        }.get(source_type, _DIM)
        line = f"{color}[{source_type}]{_RESET} {title} | {_DIM}{key}{_RESET}"
        lines.append(line)
    return "\n".join(lines)


def format_local_browse_preview(items: list[dict[str, Any]], selected: str | None) -> str:
    item = _find_browse_item_by_title(items, selected)
    if not item:
        return "No item matched.\n"
    lines = [
        f"# {item.get('title', 'Untitled')}",
        "",
        f"- Type: {item.get('source_type', 'unknown')}",
        f"- Key: {item.get('key', 'unknown')}",
        f"- Path: {item.get('path', 'unknown')}",
    ]
    if item.get("body"):
        lines.extend(["", item["body"]])
    return "\n".join(lines) + "\n"


# ── Helpers ──────────────────────────────────────────────────────────────

def _find_browse_item_by_title(
    items: list[dict[str, Any]], selected: str | None
) -> dict[str, Any] | None:
    if not items:
        return None
    if not selected:
        return items[0]
    # Strip ANSI codes for matching
    clean = _strip_ansi(selected).split(" | ", 1)[0].strip()
    # Remove sync markers
    clean = clean.lstrip("●○ ").strip()
    for item in items:
        title = item.get("title", item.get("key", ""))
        if title and title in clean:
            return item
        # Match by key field
        key = item.get("key", "")
        if key and key in clean:
            return item
        ref = item.get("reference_num", "")
        if ref and ref in clean:
            return item
        full_name = item.get("full_name", "")
        if full_name and full_name in clean:
            return item
    return items[0]


def _find_browse_item_by_field(
    items: list[dict[str, Any]], field: str, selected: str | None
) -> dict[str, Any] | None:
    if not items:
        return None
    if not selected:
        return items[0]
    clean = _strip_ansi(selected)
    for item in items:
        val = str(item.get(field, ""))
        if val and val in clean:
            return item
    return items[0]


def _strip_ansi(text: str) -> str:
    """Remove ANSI escape sequences from text."""
    import re
    return re.sub(r"\033\[[0-9;]*m", "", text)
