"""Jira source — downloads issues from a project via Atlassian Python API."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .base import BaseSource
from ..transform.markdown import html_to_markdown, write_markdown_page, _slugify


class JiraSource(BaseSource):
    """Fetch issues from a Jira project and convert them to Markdown.

    Configuration keys
    ------------------
    url : str
        Base URL of the Jira instance (e.g. ``https://myco.atlassian.net``).
    username : str
        Jira username (email for Cloud).
    token : str
        API token.
    project : str
        Jira project key (e.g. ``PROJ``).
    jql : str, optional
        Custom JQL query (overrides *project* filter when provided).
    max_issues : int, optional
        Maximum number of issues to fetch (default: 500).
    """

    source_type = "jira"

    def __init__(self, key: str, config: dict[str, Any]) -> None:
        super().__init__(key, config)
        self.url: str = config["url"]
        self.username: str = config["username"]
        self.token: str = config["token"]
        self.project: str = config.get("project", "")
        self.jql: str = config.get("jql", f"project = {self.project} ORDER BY updated DESC")
        self.max_issues: int = int(config.get("max_issues", 500))

    def fetch(self, output_dir: Path) -> list[Path]:
        try:
            from atlassian import Jira
        except ImportError as exc:
            raise RuntimeError(
                "atlassian-python-api is required for the 'jira' source. "
                "Install it with: pip install atlassian-python-api"
            ) from exc

        client = Jira(
            url=self.url,
            username=self.username,
            password=self.token,
            cloud=True,
        )

        written: list[Path] = []
        start = 0
        limit = 50

        while len(written) < self.max_issues:
            response = client.jql(
                self.jql,
                start=start,
                limit=min(limit, self.max_issues - len(written)),
                fields="summary,description,status,assignee,reporter,issuetype,labels,created,updated",
            )
            issues = response.get("issues", [])
            if not issues:
                break
            for issue in issues:
                path = self._write_issue(issue, output_dir)
                if path:
                    written.append(path)
            if len(issues) < limit:
                break
            start += limit

        return written

    def _write_issue(self, issue: dict[str, Any], output_dir: Path) -> Path | None:
        fields = issue.get("fields", {})
        issue_key = issue.get("key", "UNKNOWN")
        title = f"{issue_key}: {fields.get('summary', 'Untitled')}"

        description_raw = fields.get("description") or ""
        # Jira Cloud returns Atlassian Document Format; fall back to plain text
        if isinstance(description_raw, dict):
            body = _adf_to_text(description_raw)
        else:
            body = html_to_markdown(str(description_raw))

        issue_type = fields.get("issuetype", {}).get("name", "issue")
        status = fields.get("status", {}).get("name", "")
        sub_dir = output_dir / _slugify(issue_type)

        meta = {
            "source": self.url.rstrip("/") + "/browse/" + issue_key,
            "key": self.key,
            "type": self.source_type,
            "issue_key": issue_key,
            "status": status,
            "issue_type": issue_type,
            "labels": fields.get("labels", []),
        }
        return write_markdown_page(
            output_dir=sub_dir,
            title=title,
            body=body,
            meta=meta,
            filename=_slugify(issue_key),
        )


def _adf_to_text(node: dict[str, Any], depth: int = 0) -> str:
    """Recursively extract plain text from an Atlassian Document Format node."""
    node_type = node.get("type", "")
    content = node.get("content", [])
    text = node.get("text", "")

    if node_type == "text":
        return text
    if node_type in ("paragraph", "blockquote"):
        return "".join(_adf_to_text(c) for c in content) + "\n\n"
    if node_type == "heading":
        level = node.get("attrs", {}).get("level", 1)
        return "#" * level + " " + "".join(_adf_to_text(c) for c in content) + "\n\n"
    if node_type == "bulletList":
        return "".join("- " + _adf_to_text(c) for c in content)
    if node_type == "orderedList":
        return "".join(f"{i + 1}. " + _adf_to_text(c) for i, c in enumerate(content))
    if node_type == "listItem":
        return "".join(_adf_to_text(c) for c in content)
    if node_type == "codeBlock":
        lang = node.get("attrs", {}).get("language", "")
        code = "".join(_adf_to_text(c) for c in content)
        return f"```{lang}\n{code}\n```\n\n"
    if node_type == "hardBreak":
        return "\n"
    return "".join(_adf_to_text(c) for c in content)

