from __future__ import annotations

from typing import Any
from urllib.parse import urljoin

import requests

from .base import SourceAdapter


class JiraSource(SourceAdapter):
    """Adapter that synchronizes issues from a Jira project."""

    def sync(self) -> dict[str, object]:
        base_url = self.config["base_url"].rstrip("/") + "/"
        auth = self._auth()
        jql = self.config["jql"]
        limit = int(self.config.get("limit", 100))

        fields = self.config.get(
            "fields",
            [
                "summary",
                "description",
                "status",
                "issuetype",
                "labels",
                "priority",
                "assignee",
                "reporter",
                "created",
                "updated",
            ],
        )
        issues: list[dict[str, object]] = []
        next_page_token: str | None = None

        while True:
            params = {
                "jql": jql,
                "maxResults": limit,
                "fields": ",".join(fields),
            }
            if next_page_token:
                params["nextPageToken"] = next_page_token

            response = requests.get(
                urljoin(base_url, "rest/api/3/search/jql"),
                headers={"Accept": "application/json"},
                params=params,
                auth=auth,
                timeout=60,
            )
            response.raise_for_status()
            data = response.json()
            issues.extend(data.get("issues", []))

            next_page_token = data.get("nextPageToken")
            if not next_page_token:
                break

        self.clear_source_dir()
        for issue in issues:
            key = issue["key"]
            fields_payload = issue.get("fields", {})
            frontmatter = {
                "title": fields_payload.get("summary") or key,
                "knowledge_key": self.source["key"],
                "source_id": self.source["id"],
                "source_type": self.source["type"],
                "issue_key": key,
                "issue_id": issue.get("id"),
                "issue_type": _field_name(fields_payload.get("issuetype")),
                "status": _field_name(fields_payload.get("status")),
                "status_category": _status_category_name(fields_payload.get("status")),
                "priority": _field_name(fields_payload.get("priority")),
                "labels": fields_payload.get("labels") or [],
                "assignee": _display_name(fields_payload.get("assignee")),
                "reporter": _display_name(fields_payload.get("reporter")),
                "created_at": fields_payload.get("created"),
                "updated_at": fields_payload.get("updated"),
                "jql": jql,
                "web_url": urljoin(base_url, f"browse/{key}"),
            }
            body = _issue_markdown_body(key, fields_payload)
            self.write_markdown(self.raw_dir / f"{key}.md", frontmatter, body)

        return self.finalize_sync(
            {
                "issues": len(issues),
                "jql": jql,
                "raw_dir": str(self.raw_dir),
            }
        )

    def _auth(self) -> tuple[str, str]:
        username = self.store.resolve_key(self.config["username"])
        token = self.store.resolve_key(self.config["token"])
        return (username, token)


def search_jira(
    *,
    base_url: str,
    username: str,
    token: str,
    query: str | None = None,
    project: str | None = None,
    jql: str | None = None,
    statuses: list[str] | None = None,
    issue_types: list[str] | None = None,
    assignee: str | None = None,
    reporter: str | None = None,
    created_after: str | None = None,
    created_before: str | None = None,
    updated_after: str | None = None,
    updated_before: str | None = None,
    order_by: list[str] | None = None,
    fields: list[str] | None = None,
    properties: list[str] | None = None,
    limit: int = 25,
    next_page_token: str | None = None,
    expand: list[str] | None = None,
    fields_by_keys: bool = False,
) -> dict[str, object]:
    compiled_jql = jql or _build_jql(
        query=query,
        project=project,
        statuses=statuses,
        issue_types=issue_types,
        assignee=assignee,
        reporter=reporter,
        created_after=created_after,
        created_before=created_before,
        updated_after=updated_after,
        updated_before=updated_before,
        order_by=order_by,
    )
    params: dict[str, object] = {
        "jql": compiled_jql,
        "maxResults": limit,
        "fieldsByKeys": str(fields_by_keys).lower(),
    }
    if fields:
        params["fields"] = ",".join(fields)
    if properties:
        params["properties"] = ",".join(properties)
    if expand:
        params["expand"] = ",".join(expand)
    if next_page_token:
        params["nextPageToken"] = next_page_token

    response = requests.get(
        urljoin(base_url.rstrip("/") + "/", "rest/api/3/search/jql"),
        headers={"Accept": "application/json"},
        params=params,
        auth=(username, token),
        timeout=60,
    )
    response.raise_for_status()
    payload = response.json()
    return {
        "query": query,
        "jql": compiled_jql,
        "limit": limit,
        "fields": fields or [],
        "properties": properties or [],
        "expand": expand or [],
        "fields_by_keys": fields_by_keys,
        "next_page_token": payload.get("nextPageToken"),
        "issues": payload.get("issues", []),
    }


def _issue_markdown_body(key: str, fields_payload: dict[str, Any]) -> str:
    """Build Markdown body for a Jira issue from its fields."""
    summary = str(fields_payload.get("summary") or key)
    labels = [str(label) for label in fields_payload.get("labels", []) if label]
    description = _adf_to_markdown(fields_payload.get("description"))

    lines = [f"# {summary}", "", f"- Issue: {key}"]
    _append_field(lines, "Type", _field_name(fields_payload.get("issuetype")))
    _append_field(lines, "Status", _field_name(fields_payload.get("status")))
    _append_field(lines, "Priority", _field_name(fields_payload.get("priority")))
    _append_field(lines, "Assignee", _display_name(fields_payload.get("assignee")))
    _append_field(lines, "Reporter", _display_name(fields_payload.get("reporter")))
    if labels:
        lines.append(f"- Labels: {', '.join(labels)}")
    if description:
        lines.extend(["", "## Description", "", description.strip()])
    return "\n".join(lines).rstrip()


def _append_field(lines: list[str], label: str, value: str | None) -> None:
    """Append a Markdown list item only when *value* is truthy."""
    if value:
        lines.append(f"- {label}: {value}")


def _adf_to_markdown(node: Any, *, list_depth: int = 0) -> str:
    """Convert an Atlassian Document Format node tree into Markdown."""
    if isinstance(node, str):
        return node
    if isinstance(node, list):
        parts = [_adf_to_markdown(item, list_depth=list_depth) for item in node]
        return "\n".join(part for part in parts if part).strip()
    if not isinstance(node, dict):
        return ""

    node_type = node.get("type")
    handler = _ADF_HANDLERS.get(node_type)
    if handler is not None:
        return handler(node, list_depth)
    # Fallback: recursively render child content joined by newlines.
    content = node.get("content", [])
    return "\n".join(
        part for part in (_adf_to_markdown(item, list_depth=list_depth) for item in content) if part
    ).strip()


# -- ADF node handlers (one small function per node type) ----------------

def _adf_text(node: dict[str, Any], _depth: int) -> str:
    return _apply_marks(str(node.get("text") or ""), node.get("marks", []))


def _adf_hard_break(_node: dict[str, Any], _depth: int) -> str:
    return "\n"


def _adf_paragraph(node: dict[str, Any], depth: int) -> str:
    return "".join(_adf_to_markdown(item, list_depth=depth) for item in node.get("content", [])).strip()


def _adf_heading(node: dict[str, Any], depth: int) -> str:
    level = int(node.get("attrs", {}).get("level", 1))
    text = "".join(_adf_to_markdown(item, list_depth=depth) for item in node.get("content", [])).strip()
    return f'{"#" * max(1, min(level, 6))} {text}'.strip()


def _adf_blockquote(node: dict[str, Any], depth: int) -> str:
    text = "\n".join(
        _adf_to_markdown(item, list_depth=depth)
        for item in node.get("content", [])
        if _adf_to_markdown(item, list_depth=depth)
    )
    return "\n".join(f"> {line}" if line else ">" for line in text.splitlines())


def _adf_code_block(node: dict[str, Any], depth: int) -> str:
    text = "\n".join(_adf_to_markdown(item, list_depth=depth) for item in node.get("content", [])).strip("\n")
    language = node.get("attrs", {}).get("language")
    fence = f"```{language}" if language else "```"
    return f"{fence}\n{text}\n```".strip()


def _adf_rule(_node: dict[str, Any], _depth: int) -> str:
    return "---"


def _adf_panel(node: dict[str, Any], depth: int) -> str:
    text = "\n".join(
        _adf_to_markdown(item, list_depth=depth)
        for item in node.get("content", [])
        if _adf_to_markdown(item, list_depth=depth)
    )
    return f"> {text}".strip()


def _adf_doc(node: dict[str, Any], depth: int) -> str:
    parts = [_adf_to_markdown(item, list_depth=depth) for item in node.get("content", [])]
    return "\n\n".join(part for part in parts if part).strip()


def _adf_list(node: dict[str, Any], depth: int) -> str:
    parts = [_adf_to_markdown(item, list_depth=depth + 1) for item in node.get("content", [])]
    return "\n".join(part for part in parts if part).strip()


def _adf_list_item(node: dict[str, Any], depth: int) -> str:
    blocks = [_adf_to_markdown(item, list_depth=depth) for item in node.get("content", [])]
    lines = [line for block in blocks if block for line in block.splitlines()]
    if not lines:
        return ""
    indent = "  " * max(depth - 1, 0)
    rendered = [f"{indent}- {lines[0]}"]
    rendered.extend(f"{indent}  {line}" for line in lines[1:])
    return "\n".join(rendered)


def _adf_table(node: dict[str, Any], _depth: int) -> str:
    rows = [_table_row(item) for item in node.get("content", []) if item.get("type") == "tableRow"]
    rows = [row for row in rows if row]
    if not rows:
        return ""
    max_cells = max(len(row) for row in rows)
    normalized = [row + [""] * (max_cells - len(row)) for row in rows]
    header = normalized[0]
    body_rows = normalized[1:] or [[""] * max_cells]
    lines = [
        "| " + " | ".join(header) + " |",
        "| " + " | ".join(["---"] * max_cells) + " |",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in body_rows)
    return "\n".join(lines)


def _adf_mention(node: dict[str, Any], _depth: int) -> str:
    attrs = node.get("attrs", {})
    return "@" + str(attrs.get("text") or attrs.get("id") or "mention")


def _adf_emoji(node: dict[str, Any], _depth: int) -> str:
    attrs = node.get("attrs", {})
    return str(attrs.get("text") or attrs.get("shortName") or "")


def _adf_card(node: dict[str, Any], _depth: int) -> str:
    return str(node.get("attrs", {}).get("url") or "")


_ADF_HANDLERS: dict[str, Any] = {
    "text": _adf_text,
    "hardBreak": _adf_hard_break,
    "paragraph": _adf_paragraph,
    "heading": _adf_heading,
    "blockquote": _adf_blockquote,
    "codeBlock": _adf_code_block,
    "rule": _adf_rule,
    "panel": _adf_panel,
    "doc": _adf_doc,
    "bulletList": _adf_list,
    "orderedList": _adf_list,
    "listItem": _adf_list_item,
    "table": _adf_table,
    "mention": _adf_mention,
    "emoji": _adf_emoji,
    "inlineCard": _adf_card,
    "blockCard": _adf_card,
}


def _table_row(node: dict[str, Any]) -> list[str]:
    cells: list[str] = []
    for cell in node.get("content", []):
        if cell.get("type") not in {"tableCell", "tableHeader"}:
            continue
        value = "\n".join(_adf_to_markdown(item) for item in cell.get("content", []) if _adf_to_markdown(item))
        cells.append(value.replace("\n", "<br>").strip())
    return cells


def _apply_marks(text: str, marks: list[dict[str, Any]] | None) -> str:
    rendered = text
    for mark in marks or []:
        mark_type = mark.get("type")
        if mark_type == "strong":
            rendered = f"**{rendered}**"
        elif mark_type == "em":
            rendered = f"*{rendered}*"
        elif mark_type == "code":
            rendered = f"`{rendered}`"
        elif mark_type == "strike":
            rendered = f"~~{rendered}~~"
        elif mark_type == "link":
            href = ((mark.get("attrs") or {}).get("href"))
            rendered = f"[{rendered}]({href})" if href else rendered
    return rendered


def _quote_jql(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def _build_jql(
    *,
    query: str | None,
    project: str | None,
    statuses: list[str] | None,
    issue_types: list[str] | None,
    assignee: str | None,
    reporter: str | None,
    created_after: str | None,
    created_before: str | None,
    updated_after: str | None,
    updated_before: str | None,
    order_by: list[str] | None,
) -> str:
    clauses: list[str] = []
    if project:
        clauses.append(f"project = {project}")
    if query:
        clauses.append(f"(summary ~ {_quote_jql(query)} OR description ~ {_quote_jql(query)})")
    if statuses:
        clauses.append(_in_clause("status", statuses))
    if issue_types:
        clauses.append(_in_clause("issuetype", issue_types))
    if assignee:
        clauses.append(f"assignee = {_quote_jql(assignee)}")
    if reporter:
        clauses.append(f"reporter = {_quote_jql(reporter)}")
    if created_after:
        clauses.append(f"created >= {_quote_jql(created_after)}")
    if created_before:
        clauses.append(f"created <= {_quote_jql(created_before)}")
    if updated_after:
        clauses.append(f"updated >= {_quote_jql(updated_after)}")
    if updated_before:
        clauses.append(f"updated <= {_quote_jql(updated_before)}")
    if not clauses:
        raise ValueError("jira search requires either a query or an explicit --jql")
    jql = " AND ".join(clauses)
    if order_by:
        jql = f"{jql} ORDER BY {', '.join(order_by)}"
    return jql


def _in_clause(field_name: str, values: list[str]) -> str:
    quoted = ", ".join(_quote_jql(value) for value in values)
    return f"{field_name} in ({quoted})"


def _field_name(value: Any) -> str | None:
    if isinstance(value, dict):
        name = value.get("name")
        return str(name) if name else None
    return None


def _display_name(value: Any) -> str | None:
    if isinstance(value, dict):
        display_name = value.get("displayName") or value.get("emailAddress") or value.get("accountId")
        return str(display_name) if display_name else None
    return None


def _status_category_name(value: Any) -> str | None:
    if not isinstance(value, dict):
        return None
    status_category = value.get("statusCategory")
    if not isinstance(status_category, dict):
        return None
    name = status_category.get("name")
    return str(name) if name else None
