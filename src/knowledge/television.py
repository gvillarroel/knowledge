"""Television output formatting for all ``know`` commands.

Each command that supports ``--format television`` emits one line per result
to be consumed by ``tv`` as a source command.  The ``television-preview``
variant renders a detail pane for the currently selected row.
"""

from __future__ import annotations

from typing import Any


# ── Keys ─────────────────────────────────────────────────────────────────

def format_keys_television(keys: list[str]) -> str:
    """One line per key name."""
    return "\n".join(keys)


def format_keys_preview(keys: list[str], selected: str | None) -> str:
    """Render detail pane for a selected key name."""
    name = _resolve_selection(keys, selected)
    if not name:
        return "No key matched the selected row.\n"
    lines = [
        f"# {name}",
        "",
        f"- Key: {name}",
        "",
        "## Commands",
        "",
        f"- List sources: `know list sources --key {name}`",
        f"- Sync: `know sync --key {name}`",
        f"- Export: `know export --key {name}`",
    ]
    return "\n".join(lines) + "\n"


# ── Credentials ──────────────────────────────────────────────────────────

def format_credentials_television(names: list[str]) -> str:
    """One line per credential name."""
    return "\n".join(sorted(names))


def format_credentials_preview(names: list[str], selected: str | None) -> str:
    name = _resolve_selection(sorted(names), selected)
    if not name:
        return "No credential matched the selected row.\n"
    return f"# Credential: {name}\n\nStored in `keys.yaml`.\n"


# ── Sources ──────────────────────────────────────────────────────────────

def format_sources_television(sources: list[dict[str, Any]]) -> str:
    """``source_id | type | key | title``"""
    lines: list[str] = []
    for s in sources:
        sid = s.get("id", "")
        stype = s.get("type", "")
        key = s.get("key", "")
        title = s.get("title", "")
        lines.append(f"{sid} | {stype} | {key} | {title}")
    return "\n".join(lines)


def format_sources_preview(sources: list[dict[str, Any]], selected: str | None, *, markdown_body: str | None = None) -> str:
    source = _find_source(sources, selected)
    if not source:
        return "No source matched the selected row.\n"
    sid = source.get("id", "unknown")
    title = source.get("title", sid)

    # When markdown body is available, show content without metadata.
    if markdown_body:
        lines = [f"# {title}", ""]
        lines.append(markdown_body)
        return "\n".join(lines) + "\n"

    lines = [
        f"# {title}",
        "",
        f"- Source id: {sid}",
        f"- Type: {source.get('type')}",
        f"- Key: {source.get('key')}",
        f"- Created: {source.get('created_at', 'unknown')}",
        f"- Updated: {source.get('updated_at', 'unknown')}",
    ]
    config = source.get("config", {})
    if config:
        lines.extend(["", "## Config", ""])
        for k, v in config.items():
            lines.append(f"- {k}: {v}")
    update_cmd = source.get("update_command")
    delete_cmd = source.get("delete_command")
    if update_cmd or delete_cmd:
        lines.extend(["", "## Commands", ""])
        if update_cmd:
            lines.append(f"- Sync: `{update_cmd}`")
        if delete_cmd:
            lines.append(f"- Delete: `{delete_cmd}`")
    return "\n".join(lines) + "\n"


def _find_source(sources: list[dict[str, Any]], selected: str | None) -> dict[str, Any] | None:
    if not sources:
        return None
    if not selected:
        return sources[0]
    sel_id = selected.split(" | ", 1)[0].strip()
    for s in sources:
        if s.get("id") == sel_id:
            return s
    return sources[0]


# ── Confluence search ────────────────────────────────────────────────────

def format_confluence_television(matches: list[dict[str, Any]]) -> str:
    """``title | space | key | url``"""
    lines: list[str] = []
    for match in matches:
        for result in match.get("results", []):
            title = _confluence_result_title(result)
            space = match.get("space", "")
            key = match.get("key", "")
            url = _confluence_result_url(result, match.get("base_url", ""))
            lines.append(f"{title} | {space} | {key} | {url}")
    return "\n".join(lines)


def format_confluence_preview(matches: list[dict[str, Any]], selected: str | None) -> str:
    all_results = _flatten_confluence_results(matches)
    result, match_ctx = _find_confluence_result(all_results, selected)
    if not result:
        return "No Confluence result matched the selected row.\n"
    title = _confluence_result_title(result)
    content = result.get("content", {}) if isinstance(result, dict) else {}
    excerpt = str(result.get("excerpt") or "").strip()
    base_url = match_ctx.get("base_url", "") if match_ctx else ""
    url = _confluence_result_url(result, base_url)
    lines = [
        f"# {title}",
        "",
        f"- Space: {match_ctx.get('space', 'unknown') if match_ctx else 'unknown'}",
        f"- Key: {match_ctx.get('key', 'unknown') if match_ctx else 'unknown'}",
        f"- Type: {content.get('type', 'unknown')}",
    ]
    if url:
        lines.append(f"- URL: {url}")
    last_modified = (content.get("history", {}) or {}).get("lastUpdated", {})
    if isinstance(last_modified, dict) and last_modified.get("when"):
        lines.append(f"- Updated: {last_modified['when']}")
    if excerpt:
        lines.extend(["", "## Excerpt", "", _strip_html_tags(excerpt)])
    return "\n".join(lines) + "\n"


def _confluence_result_title(result: dict[str, Any]) -> str:
    content = result.get("content", {}) if isinstance(result, dict) else {}
    if isinstance(content, dict) and content.get("title"):
        return str(content["title"]).strip()
    return str(result.get("title", "Untitled")).strip()


def _confluence_result_url(result: dict[str, Any], base_url: str) -> str:
    content = result.get("content", {}) if isinstance(result, dict) else {}
    if isinstance(content, dict):
        links = content.get("_links", {})
        if isinstance(links, dict) and links.get("webui"):
            return f"{base_url.rstrip('/')}{links['webui']}"
    return ""


def _flatten_confluence_results(
    matches: list[dict[str, Any]],
) -> list[tuple[dict[str, Any], dict[str, Any]]]:
    flat: list[tuple[dict[str, Any], dict[str, Any]]] = []
    for match in matches:
        for result in match.get("results", []):
            flat.append((result, match))
    return flat


def _find_confluence_result(
    flat: list[tuple[dict[str, Any], dict[str, Any]]], selected: str | None
) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    if not flat:
        return None, None
    if not selected:
        return flat[0]
    sel_title = selected.split(" | ", 1)[0].strip()
    for result, ctx in flat:
        if _confluence_result_title(result) == sel_title:
            return result, ctx
    return flat[0]


# ── Jira search ──────────────────────────────────────────────────────────

def format_jira_television(matches: list[dict[str, Any]]) -> str:
    """``issue_key | summary | status | project | assignee``"""
    lines: list[str] = []
    for match in matches:
        for issue in match.get("issues", []):
            key = issue.get("key", "")
            fields = issue.get("fields", {}) or {}
            summary = str(fields.get("summary") or "").strip()
            status = _jira_field_name(fields.get("status"))
            project_name = match.get("project", "")
            assignee = _jira_display_name(fields.get("assignee"))
            lines.append(f"{key} | {summary} | {status} | {project_name} | {assignee}")
    return "\n".join(lines)


def format_jira_preview(matches: list[dict[str, Any]], selected: str | None) -> str:
    all_issues = _flatten_jira_issues(matches)
    issue, match_ctx = _find_jira_issue(all_issues, selected)
    if not issue:
        return "No Jira issue matched the selected row.\n"
    fields = issue.get("fields", {}) or {}
    key = issue.get("key", "unknown")
    summary = str(fields.get("summary") or key)
    lines = [
        f"# {key}: {summary}",
        "",
        f"- Type: {_jira_field_name(fields.get('issuetype'))}",
        f"- Status: {_jira_field_name(fields.get('status'))}",
        f"- Priority: {_jira_field_name(fields.get('priority'))}",
        f"- Assignee: {_jira_display_name(fields.get('assignee'))}",
        f"- Reporter: {_jira_display_name(fields.get('reporter'))}",
        f"- Created: {fields.get('created', 'unknown')}",
        f"- Updated: {fields.get('updated', 'unknown')}",
    ]
    labels = fields.get("labels")
    if labels:
        lines.append(f"- Labels: {', '.join(str(l) for l in labels)}")
    base_url = match_ctx.get("base_url", "") if match_ctx else ""
    if base_url:
        lines.append(f"- URL: {base_url.rstrip('/')}/browse/{key}")
    description = fields.get("description")
    if description:
        desc_text = str(description) if isinstance(description, str) else "(structured ADF content)"
        lines.extend(["", "## Description", "", desc_text])
    return "\n".join(lines) + "\n"


def _flatten_jira_issues(
    matches: list[dict[str, Any]],
) -> list[tuple[dict[str, Any], dict[str, Any]]]:
    flat: list[tuple[dict[str, Any], dict[str, Any]]] = []
    for match in matches:
        for issue in match.get("issues", []):
            flat.append((issue, match))
    return flat


def _find_jira_issue(
    flat: list[tuple[dict[str, Any], dict[str, Any]]], selected: str | None
) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    if not flat:
        return None, None
    if not selected:
        return flat[0]
    sel_key = selected.split(" | ", 1)[0].strip()
    for issue, ctx in flat:
        if issue.get("key") == sel_key:
            return issue, ctx
    return flat[0]


def _jira_field_name(value: Any) -> str:
    if isinstance(value, dict):
        return str(value.get("name") or "unknown")
    return "unknown"


def _jira_display_name(value: Any) -> str:
    if isinstance(value, dict):
        return str(
            value.get("displayName")
            or value.get("emailAddress")
            or value.get("accountId")
            or "unassigned"
        )
    return "unassigned"


# ── arXiv search ─────────────────────────────────────────────────────────

def format_arxiv_television(entries: list[dict[str, Any]]) -> str:
    """``title | primary_category | published``"""
    lines: list[str] = []
    for entry in entries if isinstance(entries, list) else []:
        if not isinstance(entry, dict):
            continue
        title = str(entry.get("title") or "").strip()
        if not title:
            continue
        primary_category = str(entry.get("primary_category") or "uncategorized").strip()
        published = str(entry.get("published") or "unknown-date").strip()
        lines.append(f"{title} | {primary_category} | {published}")
    return "\n".join(lines)


def format_arxiv_preview(entries: list[dict[str, Any]], selected: str | None) -> str:
    entry = _find_arxiv_entry(entries, selected)
    if not entry:
        return "No arXiv entry matched the selected television row.\n"
    title = str(entry.get("title") or "Untitled")
    authors = [str(a) for a in entry.get("authors", []) if a]
    summary = str(entry.get("summary") or "").strip()
    lines = [
        f"# {title}",
        "",
        f"- Published: {entry.get('published') or 'unknown'}",
        f"- Updated: {entry.get('updated') or 'unknown'}",
        f"- Primary category: {entry.get('primary_category') or 'unknown'}",
    ]
    if entry.get("pdf_url"):
        lines.append(f"- PDF: {entry['pdf_url']}")
    if entry.get("id"):
        lines.append(f"- Abs: {entry['id']}")
    if authors:
        lines.extend(["", "## Authors", "", ", ".join(authors)])
    if summary:
        lines.extend(["", "## Summary", "", summary])
    return "\n".join(lines).rstrip() + "\n"


def _find_arxiv_entry(entries: list[dict[str, Any]], selected: str | None) -> dict[str, Any]:
    if not isinstance(entries, list) or not entries:
        return {}
    if not selected:
        return entries[0] if isinstance(entries[0], dict) else {}
    sel_title = selected.split(" | ", 1)[0].strip()
    for entry in entries:
        if isinstance(entry, dict) and str(entry.get("title") or "").strip() == sel_title:
            return entry
    return entries[0] if isinstance(entries[0], dict) else {}


# ── Helpers ──────────────────────────────────────────────────────────────

def _resolve_selection(items: list[str], selected: str | None) -> str | None:
    if not items:
        return None
    if not selected:
        return items[0]
    sel = selected.split(" | ", 1)[0].strip()
    if sel in items:
        return sel
    return items[0]


def _strip_html_tags(text: str) -> str:
    import re
    clean = re.sub(r"<[^>]+>", "", text)
    return clean.strip()


# ── Format constants ─────────────────────────────────────────────────────

TV_FORMAT_CHOICES = ("json", "television", "television-preview")
