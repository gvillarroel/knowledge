"""Extra unit tests for Confluence and Jira helper paths."""

from __future__ import annotations

from typing import Any

import pytest

from knowledge.sources import confluence as confluence_module
from knowledge.sources import jira as jira_module


class _FakeResponse:
    def __init__(self, payload: dict[str, Any]) -> None:
        self._payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict[str, Any]:
        return self._payload


def test_list_confluence_spaces_paginates_and_stops_at_limit(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[tuple[str, dict[str, object] | None]] = []
    payloads = iter(
        [
            {
                "results": [
                    {"key": "ENG", "name": "Engineering", "type": "global", "description": {"plain": {"value": "Docs"}}},
                ],
                "_links": {"next": "/wiki/rest/api/space?cursor=next"},
            },
            {
                "results": [
                    {"key": "OPS", "name": "Operations", "type": "global", "description": {"plain": {"value": "Runbooks"}}},
                ],
                "_links": {},
            },
        ]
    )

    def fake_get(
        url: str,
        *,
        headers: dict[str, str],
        params: dict[str, object] | None,
        auth: tuple[str, str],
        timeout: int,
    ) -> _FakeResponse:
        calls.append((url, params))
        return _FakeResponse(next(payloads))

    monkeypatch.setattr(confluence_module.requests, "get", fake_get)

    spaces = confluence_module.list_confluence_spaces(
        base_url="https://wiki.example.com",
        username="user",
        token="token",
        limit=2,
    )

    assert [space["key"] for space in spaces] == ["ENG", "OPS"]
    assert calls[0][1] == {"limit": 2}
    assert calls[1][1] is None


def test_list_confluence_pages_builds_paths_and_follows_next(monkeypatch: pytest.MonkeyPatch) -> None:
    payloads = iter(
        [
            {
                "results": [
                    {
                        "id": "1",
                        "title": "Guide",
                        "ancestors": [{"title": "Home"}],
                        "_links": {"webui": "/wiki/spaces/DEV/pages/1"},
                    }
                ],
                "_links": {"next": "/wiki/rest/api/content?cursor=next"},
            },
            {
                "results": [
                    {
                        "id": "2",
                        "title": "API",
                        "ancestors": [{"title": "Home"}, {"title": "Guide"}],
                        "_links": {"webui": "/wiki/spaces/DEV/pages/2"},
                    }
                ],
                "_links": {},
            },
        ]
    )

    def fake_get(
        url: str,
        *,
        headers: dict[str, str],
        params: dict[str, object] | None,
        auth: tuple[str, str],
        timeout: int,
    ) -> _FakeResponse:
        return _FakeResponse(next(payloads))

    monkeypatch.setattr(confluence_module.requests, "get", fake_get)

    pages = confluence_module.list_confluence_pages(
        base_url="https://wiki.example.com",
        username="user",
        token="token",
        space="DEV",
        limit=10,
    )

    assert pages[0]["path"] == "/Home/Guide"
    assert pages[1]["path"] == "/Home/Guide/API"
    assert pages[1]["web_url"] == "https://wiki.example.com/wiki/spaces/DEV/pages/2"


def test_confluence_helpers_cover_edge_cases() -> None:
    assert confluence_module._slugify("Hello, World!") == "hello-world"
    assert confluence_module._slugify("???") == "page"
    assert (
        confluence_module._page_url("https://wiki.example.com/", {"_links": {"webui": "/pages/1"}})
        == "https://wiki.example.com/pages/1"
    )
    assert confluence_module._page_url("https://wiki.example.com/", {"_links": {"webui": ""}}) is None
    assert confluence_module._quote_cql('a"b\\c') == '"a\\"b\\\\c"'
    assert confluence_module._next_cursor({"_links": {"next": "/wiki/rest/api/search?cursor=abc&limit=25"}}) == "abc"
    assert confluence_module._next_cursor({"_links": {"next": "/wiki/rest/api/search?limit=25"}}) is None
    assert confluence_module._search_result_page_id({"content": {"id": 42}}) == "42"
    assert confluence_module._search_result_page_id({"id": "99"}) == "99"
    assert confluence_module._search_result_page_id("bad") is None


def test_confluence_storage_to_markdown_covers_links_lists_and_macros() -> None:
    payload = """
    <h2>Heading</h2>
    <p><a href="https://example.com">Link</a> and <strong>bold</strong></p>
    <ol><li>First</li><li>Second</li></ol>
    <blockquote><p>Quoted</p></blockquote>
    <ac:structured-macro ac:name="code">print('x')</ac:structured-macro>
    """

    rendered = confluence_module.confluence_storage_to_markdown(payload)

    assert "## Heading" in rendered
    assert "[Link](https://example.com)" in rendered
    assert "1. First" in rendered
    assert "> Quoted" in rendered
    assert "```" in rendered


def test_list_jira_projects_paginates_until_last_page(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[dict[str, object]] = []
    payloads = iter(
        [
            {
                "values": [
                    {"key": "KAN", "name": "Kanban", "projectTypeKey": "software", "lead": {"displayName": "Alice"}},
                ],
                "isLast": False,
            },
            {
                "values": [
                    {"key": "OPS", "name": "Operations", "projectTypeKey": "business", "lead": {"displayName": "Bob"}},
                ],
                "isLast": True,
            },
        ]
    )

    def fake_get(
        url: str,
        *,
        headers: dict[str, str],
        params: dict[str, object],
        auth: tuple[str, str],
        timeout: int,
    ) -> _FakeResponse:
        calls.append(params)
        return _FakeResponse(next(payloads))

    monkeypatch.setattr(jira_module.requests, "get", fake_get)

    projects = jira_module.list_jira_projects(
        base_url="https://jira.example.com",
        username="user",
        token="token",
        limit=2,
    )

    assert [project["key"] for project in projects] == ["KAN", "OPS"]
    assert calls[0]["startAt"] == 0
    assert calls[1]["startAt"] == 1


def test_jira_helper_functions_cover_branches() -> None:
    assert jira_module._quote_jql('a"b\\c') == '"a\\"b\\\\c"'
    assert jira_module._in_clause("status", ["In Progress", "Done"]) == 'status in ("In Progress", "Done")'
    assert jira_module._field_name({"name": "Bug"}) == "Bug"
    assert jira_module._field_name(None) is None
    assert jira_module._display_name({"displayName": "Alice"}) == "Alice"
    assert jira_module._display_name({}) is None
    assert jira_module._status_category_name({"statusCategory": {"name": "Done"}}) == "Done"
    assert jira_module._status_category_name({"statusCategory": "bad"}) is None


def test_issue_markdown_body_renders_metadata_and_description() -> None:
    body = jira_module._issue_markdown_body(
        "KAN-1",
        {
            "summary": "Fix login",
            "issuetype": {"name": "Bug"},
            "status": {"name": "In Progress"},
            "priority": {"name": "High"},
            "assignee": {"displayName": "Alice"},
            "reporter": {"displayName": "Bob"},
            "labels": ["auth", "urgent"],
            "description": {
                "type": "doc",
                "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Investigate"}]}],
            },
        },
    )

    assert "# Fix login" in body
    assert "- Type: Bug" in body
    assert "- Labels: auth, urgent" in body
    assert "## Description" in body
    assert "Investigate" in body


def test_jira_adf_helpers_cover_tables_cards_and_marks() -> None:
    node = {
        "type": "table",
        "content": [
            {
                "type": "tableRow",
                "content": [
                    {"type": "tableHeader", "content": [{"type": "text", "text": "Name"}]},
                    {"type": "tableHeader", "content": [{"type": "text", "text": "Value"}]},
                ],
            },
            {
                "type": "tableRow",
                "content": [
                    {"type": "tableCell", "content": [{"type": "text", "text": "A"}]},
                    {"type": "tableCell", "content": [{"type": "text", "text": "B"}]},
                ],
            },
        ],
    }

    assert "| Name | Value |" in jira_module._adf_to_markdown(node)
    assert (
        jira_module._apply_marks("x", [{"type": "strong"}, {"type": "em"}, {"type": "code"}, {"type": "strike"}])
        == "~~`***x***`~~"
    )
    assert jira_module._apply_marks("docs", [{"type": "link", "attrs": {"href": "https://example.com"}}]) == "[docs](https://example.com)"
    assert jira_module._table_row({"type": "tableRow", "content": [{"type": "ignored"}]}) == []
    lines = ["x"]
    jira_module._append_field(lines, "Ignored", None)
    assert lines == ["x"]
