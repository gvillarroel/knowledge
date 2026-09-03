"""Extra unit tests for Confluence and Jira helper paths."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta
from email.utils import format_datetime
import json
from pathlib import Path
import threading
import time
from typing import Any
from urllib.parse import urlsplit

import pytest
import requests
import yaml

from knowledge.errors import KnowledgeError
from knowledge.sources import confluence as confluence_module
from knowledge.sources import confluence_http as conf_http
from knowledge.sources import confluence_snapshot as conf_snapshot
from knowledge.sources import jira as jira_module
from knowledge.sources.confluence import ConfluenceSource, ConfluenceSyncError
from knowledge.store import KnowledgeStore


class _FakeResponse:
    def __init__(self, payload: Any, status: int = 200, headers: dict[str, str] | None = None) -> None:
        self._payload = payload
        self.status_code = status
        self.headers = headers or {}
        self.closed = False
        self.links = {
            item["rel"]: item
            for item in confluence_module.requests.utils.parse_header_links(self.headers.get("Link", ""))
            if "rel" in item
        }

    def close(self) -> None:
        self.closed = True

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict[str, Any]:
        if isinstance(self._payload, Exception):
            raise self._payload
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

    monkeypatch.setattr(confluence_module.requests.Session, "get", lambda _session, url, **kwargs: fake_get(url, **{key: value for key, value in kwargs.items() if key != "allow_redirects"}))

    spaces = confluence_module.list_confluence_spaces(
        base_url="https://wiki.example.com",
        username="user",
        token="token",
        limit=2,
    )

    assert [space["key"] for space in spaces] == ["ENG", "OPS"]
    assert calls[0][1] == {"limit": 2}
    assert calls[1][1] == {"limit": 2, "cursor": "next"}


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

    monkeypatch.setattr(confluence_module.requests.Session, "get", lambda _session, url, **kwargs: fake_get(url, **{key: value for key, value in kwargs.items() if key != "allow_redirects"}))

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


# Confluence resilience: transport failures, pagination, and checkpointed sync.

class _Clock:
    def __init__(self) -> None:
        self.now = 0.0
        self.waits: list[float] = []

    def wait(self, seconds: float) -> None:
        self.waits.append(seconds)
        self.now += seconds


def _confluence_transport(monkeypatch, outcomes):
    calls = []
    remaining = iter(outcomes)

    def get(session, url, **kwargs):
        calls.append((id(session), url, kwargs))
        result = next(remaining)
        if isinstance(result, Exception):
            raise result
        return result

    monkeypatch.setattr(requests.Session, "get", get)
    return calls


def _confluence_clock(monkeypatch):
    clock = _Clock()
    monkeypatch.setattr(conf_http.time, "monotonic", lambda: clock.now)
    monkeypatch.setattr(conf_http.ConfluenceClient, "_wait", lambda _client, seconds: clock.wait(seconds))
    monkeypatch.setattr(conf_http.random, "uniform", lambda _a, _b: 1.0)
    return clock


@pytest.mark.parametrize("failure", [
    requests.Timeout("private-token"),
    requests.ConnectionError("private-token"),
    requests.exceptions.ChunkedEncodingError("private-token"),
    *[_FakeResponse({}, status) for status in (408, 429, 500, 502, 503, 504)],
])
def test_confluence_transport_retries_transient_reads(monkeypatch, failure):
    clock = _confluence_clock(monkeypatch)
    response = _FakeResponse({"ok": True})
    calls = _confluence_transport(monkeypatch, [failure, response])
    with conf_http.ConfluenceClient("https://example.com/wiki/", ("u", "private-token")) as client:
        assert client.get_json("api/v2/pages") == {"ok": True}
        assert client.retries == 1
        assert client.requests == 2
    assert len({call[0] for call in calls}) == 1
    assert clock.waits == [1.0]
    assert calls[0][1] == "https://example.com/wiki/api/v2/pages"
    assert calls[0][2]["allow_redirects"] is False
    assert calls[0][2]["timeout"] == (10.0, 60.0)
    assert response.closed


@pytest.mark.parametrize("status", [301, 302, 400, 401, 403, 404, 409, 422])
def test_confluence_transport_does_not_retry_permanent_errors(monkeypatch, status):
    response = _FakeResponse({"error": "private-token"}, status)
    calls = _confluence_transport(monkeypatch, [response])
    with conf_http.ConfluenceClient("https://example.com", ("u", "private-token")) as client:
        with pytest.raises(conf_http.ConfluenceRequestError) as error:
            client.get_json("api/v2/pages")
    assert len(calls) == 1
    assert "private-token" not in str(error.value)
    assert error.value.status == status
    assert response.closed


def test_confluence_inactive_subscription_fails_fast_with_sanitized_error(monkeypatch):
    response = _FakeResponse(
        {"errorCode": "SUSPENDED_INACTIVITY", "errorMessage": "private-token"},
        503,
    )
    calls = _confluence_transport(monkeypatch, [response])
    with conf_http.ConfluenceClient("https://example.com", ("u", "private-token")) as client:
        with pytest.raises(conf_http.ConfluenceRequestError, match="SUSPENDED_INACTIVITY") as error:
            client.get_json("api/v2/spaces")
        assert client.requests == 1
        assert client.retries == 0
    assert len(calls) == 1
    assert error.value.status == 503
    assert error.value.fatal is True
    assert "private-token" not in str(error.value)
    assert response.closed


def test_confluence_missing_app_access_fails_fast_with_actionable_error(monkeypatch):
    response = _FakeResponse(
        {
            "message": (
                "com.atlassian.confluence.SomeException: 403 FORBIDDEN "
                '"Request rejected because caller cannot access Confluence" private-token'
            ),
            "statusCode": 403,
        },
        403,
    )
    calls = _confluence_transport(monkeypatch, [response])
    with conf_http.ConfluenceClient("https://example.com", ("u", "private-token")) as client:
        with pytest.raises(conf_http.ConfluenceRequestError, match="grant Confluence app access") as error:
            client.get_json("rest/api/user/current")
        assert client.requests == 1
        assert client.retries == 0
    assert len(calls) == 1
    assert error.value.status == 403
    assert error.value.fatal is True
    assert "private-token" not in str(error.value)
    assert response.closed


def test_confluence_transport_retry_exhaustion_is_bounded(monkeypatch):
    clock = _confluence_clock(monkeypatch)
    calls = _confluence_transport(monkeypatch, [requests.Timeout("private-token")] * 3)
    with conf_http.ConfluenceClient("https://example.com", ("u", "private-token"),
                                   conf_http.ConfluenceOptions(max_retries=2)) as client:
        with pytest.raises(conf_http.ConfluenceRequestError, match="after 3 attempt") as error:
            client.get_json("api/v2/pages")
    assert len(calls) == 3
    assert clock.waits == [1.0, 2.0]
    assert "private-token" not in str(error.value)


def test_confluence_transport_tls_errors_are_not_retried(monkeypatch):
    calls = _confluence_transport(monkeypatch, [requests.exceptions.SSLError("private-token")])
    with conf_http.ConfluenceClient("https://example.com", ("u", "private-token")) as client:
        with pytest.raises(conf_http.ConfluenceRequestError, match="TLS"):
            client.get_json("api/v2/pages")
    assert len(calls) == 1


@pytest.mark.parametrize("value, expected", [
    ("3", 3), ("0", 0), ("1.5", 1.5), ("-1", None),
    ("nan", None), ("inf", None), ("garbage", None), ("", None), (None, None),
    ("Wed, 21 Oct 2015 07:28:00 GMT", 0),
])
def test_confluence_retry_after_values(value, expected):
    assert conf_http.retry_after_seconds(value) == expected


def test_confluence_retry_after_http_date():
    header = format_datetime(datetime.now(UTC) + timedelta(seconds=20), usegmt=True)
    assert 18 <= conf_http.retry_after_seconds(header) <= 20


@pytest.mark.parametrize("status", [429, 503])
def test_confluence_retry_after_is_a_minimum_delay(monkeypatch, status):
    clock = _confluence_clock(monkeypatch)
    _confluence_transport(monkeypatch, [_FakeResponse({}, status, {"Retry-After": "3"}), _FakeResponse({})])
    with conf_http.ConfluenceClient("https://example.com", ("u", "t")) as client:
        client.get_json("api/v2/pages")
    assert sum(clock.waits) == 3


def test_confluence_long_retry_after_stops_without_retrying_early(monkeypatch):
    clock = _confluence_clock(monkeypatch)
    calls = _confluence_transport(monkeypatch, [_FakeResponse({}, 429, {"Retry-After": "3600"})])
    with conf_http.ConfluenceClient("https://example.com", ("u", "t")) as client:
        with pytest.raises(conf_http.ConfluenceRequestError, match="max_retry_wait") as error:
            client.get_json("api/v2/pages")
        assert error.value.fatal
    assert len(calls) == 1
    assert not clock.waits


def test_confluence_cooldown_is_shared_between_workers(monkeypatch):
    cooldown_started = threading.Event()
    sent = []
    lock = threading.Lock()
    original_wait = conf_http.ConfluenceClient._wait
    monkeypatch.setattr(conf_http.random, "uniform", lambda _a, _b: 0)

    def waiting(client, seconds):
        cooldown_started.set()
        original_wait(client, seconds)

    def get(session, url, **kwargs):
        with lock:
            sent.append((url, time.monotonic(), id(session)))
            first = len(sent) == 1
        return _FakeResponse({}, 429, {"Retry-After": "0.2"}) if first else _FakeResponse({})

    monkeypatch.setattr(conf_http.ConfluenceClient, "_wait", waiting)
    monkeypatch.setattr(requests.Session, "get", get)
    with conf_http.ConfluenceClient("https://example.com", ("u", "t")) as client:
        with ThreadPoolExecutor(max_workers=2) as executor:
            first = executor.submit(client.get_json, "api/v2/pages/1")
            assert cooldown_started.wait(3)
            second = executor.submit(client.get_json, "api/v2/pages/2")
            first.result(timeout=3)
            second.result(timeout=3)
        assert len(client._sessions) == 2
    assert len(sent) == 3
    assert all(moment - sent[0][1] >= 0.17 for _, moment, _ in sent[1:])
    assert not client._sessions


@pytest.mark.parametrize("payload", [[], None, ValueError("private-token"), {"_links": ["bad"]}])
def test_confluence_transport_rejects_invalid_json_shapes(monkeypatch, payload):
    response = _FakeResponse(payload)
    _confluence_transport(monkeypatch, [response])
    with conf_http.ConfluenceClient("https://example.com", ("u", "t"),
                                   conf_http.ConfluenceOptions(max_retries=0)) as client:
        with pytest.raises(conf_http.ConfluenceRequestError) as error:
            client.get_json("api/v2/pages")
    assert "private-token" not in str(error.value)
    assert response.closed


@pytest.mark.parametrize("config", [
    {"workers": 0}, {"workers": 17}, {"workers": True}, {"page_size": 0}, {"page_size": 251},
    {"max_retries": -1}, {"max_retries": 11}, {"max_pages": -1}, {"limit": 0},
    {"timeout": float("nan")}, {"timeout": float("inf")}, {"timeout": 0},
    {"connect_timeout": -1}, {"max_retry_wait": 0},
])
def test_confluence_options_reject_invalid_limits(config):
    with pytest.raises(ValueError):
        conf_http.ConfluenceOptions.from_config(config)


def test_confluence_legacy_limits_remain_compatible():
    assert conf_http.ConfluenceOptions.from_config({"limit": 500}).page_size == 250
    assert conf_http.ConfluenceOptions.from_config({"limit": 10}).max_pages == 0
    assert conf_http.ConfluenceOptions.from_config({"cql": "type=page", "limit": 10}).max_pages == 10
    assert conf_http.ConfluenceOptions.from_config({"cql": "type=page"}).max_pages == 0
    assert conf_http.ConfluenceOptions.from_config({"limit": 10, "page_size": 2}).page_size == 2


@pytest.mark.parametrize("url", [
    "ftp://example.com", "https://u:secret@example.com", "https://example.com?secret=1",
    "https://example.com#fragment", "https://example.com:invalid",
])
def test_confluence_base_url_rejects_unsafe_values(url):
    with pytest.raises(ValueError):
        conf_http.normalize_confluence_base_url(url)


def test_confluence_pagination_preserves_filters_and_decodes_cursor(monkeypatch):
    calls = _confluence_transport(monkeypatch, [
        _FakeResponse({"results": [{"id": "1"}], "_links": {"next": "/wiki/api/v2/pages?cursor=a%2Bb%2Fc%3D"}}),
        _FakeResponse({"results": [{"id": "2"}]}),
    ])
    params = {"space-id": "10", "status": "current", "subtype": "page", "limit": 2}
    with conf_http.ConfluenceClient("https://example.com/wiki", ("u", "t")) as client:
        batches = list(client.iter_batches("api/v2/pages", params))
    assert len(batches) == 2
    assert calls[1][2]["params"] == {**params, "cursor": "a+b/c="}
    assert confluence_module._next_cursor({"_links": {"next": "?cursor=a%2Bb%2Fc%3D"}}) == "a+b/c="


def test_confluence_pagination_supports_link_header(monkeypatch):
    calls = _confluence_transport(monkeypatch, [
        _FakeResponse({"results": [{"id": "1"}]}, headers={
            "Link": '<https://example.com/wiki/api/v2/pages?cursor=next>; rel="next"'
        }),
        _FakeResponse({"results": [{"id": "2"}]}),
    ])
    with conf_http.ConfluenceClient("https://example.com", ("u", "t")) as client:
        assert len(list(client.iter_batches("api/v2/pages", {"limit": 2}))) == 2
    assert calls[1][2]["params"]["cursor"] == "next"


@pytest.mark.parametrize("link", [
    "https://other.example/wiki/api/v2/pages?cursor=x",
    "//other.example/wiki/api/v2/pages?cursor=x",
    "https://user:secret@example.com/wiki/api/v2/pages?cursor=x",
    "/wiki/api/v2/spaces?cursor=x",
    "/wiki/api/v2/pages?cursor=x&space-id=20",
    "/wiki/api/v2/pages?cursor=x&status=draft",
    "/wiki/api/v2/pages?cursor=x&unexpected=1",
    "/wiki/api/v2/pages?cursor=x&cursor=y",
    "/wiki/api/v2/pages?cursor=",
    "/wiki/api/v2/pages?start=-1",
    "/wiki/api/v2/pages?start=invalid",
    "/wiki/api/v2/pages?cursor=x&limit=251",
    "/wiki/api/v2/pages?cursor=x#fragment",
    "/wiki/api/v2/pages?limit=2",
])
def test_confluence_pagination_rejects_unsafe_continuations(monkeypatch, link):
    calls = _confluence_transport(monkeypatch, [
        _FakeResponse({"results": [{"id": "1"}], "_links": {"next": link}}),
    ])
    with conf_http.ConfluenceClient("https://example.com", ("u", "secret")) as client:
        with pytest.raises(conf_http.ConfluenceRequestError):
            list(client.iter_batches("api/v2/pages", {"space-id": "10", "status": "current", "limit": 2}))
    assert len(calls) == 1


@pytest.mark.parametrize("payload", [
    {}, {"results": {}}, {"results": [None]}, {"results": [], "_links": {"next": "?cursor=x"}},
    {"results": [{"id": "1"}], "_links": {"next": 123}},
])
def test_confluence_pagination_rejects_incomplete_results(monkeypatch, payload):
    _confluence_transport(monkeypatch, [_FakeResponse(payload)])
    with conf_http.ConfluenceClient("https://example.com", ("u", "t")) as client:
        with pytest.raises(conf_http.ConfluenceRequestError):
            list(client.iter_batches("api/v2/pages", {"limit": 2}))


def test_confluence_pagination_repeated_cursor_cannot_loop(monkeypatch):
    calls = _confluence_transport(monkeypatch, [
        _FakeResponse({"results": [{"id": "1"}], "_links": {"next": "?cursor=repeat"}}),
        _FakeResponse({"results": [{"id": "2"}], "_links": {"next": "?cursor=repeat"}}),
    ])
    with conf_http.ConfluenceClient("https://example.com", ("u", "t")) as client:
        with pytest.raises(conf_http.ConfluenceRequestError, match="repeated"):
            list(client.iter_batches("api/v2/pages", {"limit": 2}))
    assert len(calls) == 2


def _confluence_adapter(tmp_path, **overrides):
    store = KnowledgeStore(tmp_path / "store")
    store.temp_root = tmp_path / "cache"
    store.initialize()
    store.create_collection_key("docs")
    source = store.add_collection_source(
        "docs", "confluence", title="ENG",
        config={"base_url": "https://example.com/wiki", "space_key": "ENG", "username": "fixture-user",
                "token": "fixture-token", "workers": 3, "page_size": 5, "max_retries": 0, **overrides},
        update_command="know sync confluence --key docs", delete_command="del",
    )
    return ConfluenceSource(source, store)


class _ConfluenceAPI:
    def __init__(self, count=20, delay=0.0):
        self.pages = {
            str(index): {"id": str(index), "title": f"Page {index}", "spaceId": "10", "status": "current",
                         "version": {"number": 1}, "body": {"storage": {"value": f"<p>Body {index}</p>"}}}
            for index in range(1, count + 1)
        }
        self.delay = delay
        self.fail_pages = {}
        self.fail_cursor = None
        self.calls = []
        self.active = 0
        self.peak = 0
        self.lock = threading.Lock()

    def get(self, session, url, **kwargs):
        path = urlsplit(url).path
        params = kwargs["params"]
        with self.lock:
            self.calls.append((path, dict(params)))
        if path.endswith("/spaces"):
            assert params["keys"] == "ENG"
            return _FakeResponse({"results": [{"id": "10", "key": "ENG"}]})
        if path.endswith("/pages") or path.endswith("/search"):
            if self.fail_cursor is not None and params.get("cursor") == self.fail_cursor:
                return _FakeResponse({}, 503)
            if path.endswith("/pages"):
                assert params["space-id"] == "10"
                assert "body-format" not in params
            else:
                assert params["expand"] == "content.version"
            start = int(params.get("cursor", 0))
            rows = [{key: value for key, value in page.items() if key != "body"}
                    for page in list(self.pages.values())[start:start + params["limit"]]]
            if path.endswith("/search"):
                rows = [{"content": {**row, "type": "page"}} for row in rows]
            next_start = start + len(rows)
            links = {"next": f"{path}?cursor={next_start}"} if next_start < len(self.pages) else {}
            return _FakeResponse({"results": rows, "_links": links})
        page_id = path.rsplit("/", 1)[-1]
        with self.lock:
            self.active += 1
            self.peak = max(self.peak, self.active)
        try:
            if self.delay:
                time.sleep(self.delay)
            if page_id in self.fail_pages:
                return _FakeResponse({"error": "fixture-token"}, self.fail_pages[page_id])
            return _FakeResponse(self.pages[page_id])
        finally:
            with self.lock:
                self.active -= 1

    def install(self, monkeypatch):
        monkeypatch.setattr(requests.Session, "get", lambda session, url, **kwargs: self.get(session, url, **kwargs))


def test_confluence_sync_is_parallel_and_reuses_current_versions(tmp_path, monkeypatch):
    api = _ConfluenceAPI(delay=0.005)
    api.install(monkeypatch)
    adapter = _confluence_adapter(tmp_path)
    (adapter.raw_dir / "authored.md").write_text("# Keep my notes\n", encoding="utf-8")
    first = adapter.sync()
    assert first["pages"] == first["downloaded"] == 20
    assert 1 < api.peak <= 3
    assert first["requests"] == 25
    assert (adapter.raw_dir / "authored.md").read_text() == "# Keep my notes\n"
    second = adapter.sync()
    assert second["reused"] == 20
    assert second["downloaded"] == 0
    assert second["requests"] == 5
    api.pages["2"]["title"] = "Renamed"
    api.pages["2"]["version"] = {"number": 2}
    third = adapter.sync()
    assert third["downloaded"] == 1
    assert third["reused"] == 19
    assert not (adapter.raw_dir / "2-page-2.md").exists()
    assert (adapter.raw_dir / "2-renamed.md").exists()
    del api.pages["3"]
    fourth = adapter.sync()
    assert fourth["pages"] == 19
    assert not (adapter.raw_dir / "3-page-3.md").exists()
    assert (adapter.raw_dir / "authored.md").exists()


def test_confluence_partial_download_preserves_snapshot_and_resumes(tmp_path, monkeypatch):
    api = _ConfluenceAPI()
    api.install(monkeypatch)
    adapter = _confluence_adapter(tmp_path)
    adapter.sync()
    original = {path.name: path.read_bytes() for path in adapter.raw_dir.iterdir()}
    last_synced = adapter.source["last_synced_at"]
    for page in api.pages.values():
        page["version"] = {"number": 2}
        page["body"]["storage"]["value"] = "<p>Updated</p>"
    api.fail_pages["3"] = 503
    with pytest.raises(ConfluenceSyncError) as error:
        adapter.sync()
    assert error.value.stats["pages"] == 19
    assert error.value.stats["failures"][0]["page_id"] == "3"
    assert original == {path.name: path.read_bytes() for path in adapter.raw_dir.iterdir()}
    assert adapter.source["last_synced_at"] == last_synced
    persisted = adapter.store.list_collection_sources(key_name="docs")[0]
    assert persisted["last_synced_at"] == last_synced
    report = Path(error.value.stats["report"]).read_text(encoding="utf-8")
    assert "fixture-token" not in report
    assert "fixture-user" not in report
    api.fail_pages.clear()
    result = adapter.sync()
    assert result["downloaded"] == 1
    assert result["reused"] == 19
    assert result["complete"]
    assert "Updated" in (adapter.raw_dir / "3-page-3.md").read_text(encoding="utf-8")


def test_confluence_inventory_failure_keeps_downloaded_checkpoints(tmp_path, monkeypatch):
    api = _ConfluenceAPI(12)
    api.fail_cursor = "5"
    api.install(monkeypatch)
    adapter = _confluence_adapter(tmp_path)
    (adapter.raw_dir / "original.txt").write_text("keep", encoding="utf-8")
    with pytest.raises(ConfluenceSyncError) as error:
        adapter.sync()
    assert error.value.stats["pages"] == 5
    assert not list(adapter.raw_dir.glob("*.md"))
    api.fail_cursor = None
    result = adapter.sync()
    assert result["reused"] == 5
    assert result["downloaded"] == 7
    assert (adapter.raw_dir / "original.txt").read_text() == "keep"


def test_confluence_cql_sync_is_not_silently_limited_to_100_pages(tmp_path, monkeypatch):
    api = _ConfluenceAPI(125)
    api.install(monkeypatch)
    adapter = _confluence_adapter(tmp_path, cql='type = "page"', page_size=25)
    result = adapter.sync()
    assert result["pages"] == 125
    assert result["downloaded"] == 125
    assert not any(path.endswith("/spaces") for path, _ in api.calls)
    assert adapter.sync()["reused"] == 125


@pytest.mark.parametrize("config", [{"max_pages": 3}, {"cql": "type=page", "limit": 3}])
def test_confluence_sync_respects_explicit_total_caps(tmp_path, monkeypatch, config):
    api = _ConfluenceAPI()
    api.install(monkeypatch)
    adapter = _confluence_adapter(tmp_path, **config)
    assert adapter.sync()["pages"] == 3
    body_calls = [path for path, _ in api.calls if "/pages/" in path]
    assert len(body_calls) == 3


def test_confluence_refresh_and_corrupt_cache_force_body_downloads(tmp_path, monkeypatch):
    api = _ConfluenceAPI(3)
    api.install(monkeypatch)
    adapter = _confluence_adapter(tmp_path)
    first = adapter.sync()
    checkpoint = Path(first["report"]).parent
    (checkpoint / "2.json").write_text("{broken", encoding="utf-8")
    assert adapter.sync()["downloaded"] == 1
    adapter.source["_confluence_sync_options"] = {"refresh": True}
    assert adapter.sync()["downloaded"] == 3
    assert "_confluence_sync_options" not in adapter.store.list_collection_sources()[0]


def test_confluence_cache_is_scoped_to_store_and_account(tmp_path, monkeypatch):
    api = _ConfluenceAPI(2)
    api.install(monkeypatch)
    first = _confluence_adapter(tmp_path / "a")
    second = _confluence_adapter(tmp_path / "b")
    second.cache_dir = first.cache_dir
    first_result = first.sync()
    second_result = second.sync()
    assert first_result["report"] != second_result["report"]
    assert second_result["downloaded"] == 2
    second.config["username"] = "another-user"
    assert second.sync()["downloaded"] == 2


@pytest.mark.parametrize("bad_page", [
    {"id": "../outside"}, {"id": "999"}, {"spaceId": "20"}, {"status": "draft"},
    {"subtype": "live"}, {"body": {}}, {"body": {"storage": {}}}, {"version": "invalid"},
])
def test_confluence_invalid_page_never_replaces_healthy_files(tmp_path, monkeypatch, bad_page):
    api = _ConfluenceAPI(1)
    api.install(monkeypatch)
    adapter = _confluence_adapter(tmp_path)
    original = adapter.raw_dir / "original.txt"
    original.write_text("keep", encoding="utf-8")
    actual_get = api.get

    def malformed(session, url, **kwargs):
        if url.endswith("/pages/1"):
            return _FakeResponse({**api.pages["1"], **bad_page})
        return actual_get(session, url, **kwargs)

    monkeypatch.setattr(requests.Session, "get", malformed)
    with pytest.raises(ConfluenceSyncError):
        adapter.sync()
    assert original.read_text() == "keep"
    assert not list(adapter.raw_dir.glob("*.md"))
    assert "last_synced_at" not in adapter.source


def test_confluence_cross_space_inventory_fails_closed(tmp_path, monkeypatch):
    api = _ConfluenceAPI(1)
    api.pages["1"]["spaceId"] = "20"
    api.install(monkeypatch)
    adapter = _confluence_adapter(tmp_path)
    with pytest.raises(ConfluenceSyncError) as error:
        adapter.sync()
    assert "outside the requested space" in error.value.stats["failures"][0]["error"]
    assert not any("/pages/" in path for path, _ in api.calls)


def test_confluence_publication_rolls_back_metadata_write_failure(tmp_path, monkeypatch):
    api = _ConfluenceAPI(2)
    api.install(monkeypatch)
    adapter = _confluence_adapter(tmp_path)
    adapter.sync()
    original = {p.name: p.read_bytes() for p in adapter.raw_dir.iterdir()}
    old_source = dict(adapter.source)

    def broken_update(_source):
        raise OSError("disk full")

    monkeypatch.setattr(adapter.store, "update_collection_source", broken_update)
    with pytest.raises(ConfluenceSyncError):
        adapter.sync()
    assert original == {p.name: p.read_bytes() for p in adapter.raw_dir.iterdir()}
    assert adapter.source == old_source


def test_confluence_authored_file_collision_is_not_overwritten(tmp_path, monkeypatch):
    api = _ConfluenceAPI(1)
    api.install(monkeypatch)
    adapter = _confluence_adapter(tmp_path)
    authored = adapter.raw_dir / "1-page-1.md"
    authored.write_text("Handwritten notes", encoding="utf-8")
    with pytest.raises(ConfluenceSyncError):
        adapter.sync()
    assert authored.read_text() == "Handwritten notes"


def test_confluence_source_lock_blocks_a_concurrent_writer(tmp_path, monkeypatch):
    api = _ConfluenceAPI(1)
    api.install(monkeypatch)
    adapter = _confluence_adapter(tmp_path)
    with conf_snapshot.ConfluenceSnapshot(adapter.raw_dir, adapter.source):
        with pytest.raises(KnowledgeError, match="already using"):
            adapter.sync()
    assert not api.calls
    assert adapter.sync()["complete"]


def test_confluence_recovers_after_interrupted_directory_swap(tmp_path):
    adapter = _confluence_adapter(tmp_path)
    (adapter.raw_dir / "authored.txt").write_text("keep", encoding="utf-8")
    backup = conf_snapshot.ConfluenceSnapshot(adapter.raw_dir, adapter.source).backup
    adapter.raw_dir.rename(backup)
    adapter.raw_dir.mkdir()
    with conf_snapshot.ConfluenceSnapshot(adapter.raw_dir, adapter.source):
        assert (adapter.raw_dir / "authored.txt").read_text() == "keep"
    assert not backup.exists()


@pytest.mark.parametrize("change", [
    {"version": {"number": 2}}, {"version": {}}, {"version": None},
    {"title": "new title"}, {"parentId": "200"}, {"status": "draft"},
])
def test_confluence_cache_requires_fresh_metadata_match(tmp_path, change):
    page = _ConfluenceAPI(1).pages["1"]
    path = tmp_path / "1.json"
    conf_snapshot.cache_page(path, page)
    current = {**page, **change}
    assert conf_snapshot.cached_page(path, current) is None


def test_confluence_cache_digest_detects_modified_payload(tmp_path):
    page = _ConfluenceAPI(1).pages["1"]
    path = tmp_path / "1.json"
    conf_snapshot.cache_page(path, page)
    payload = json.loads(path.read_text())
    payload["page"]["body"]["storage"]["value"] = "tampered"
    path.write_text(json.dumps(payload), encoding="utf-8")
    assert conf_snapshot.cached_page(path, page) is None


def test_confluence_large_space_over_real_http_recovers_and_resumes(tmp_path):
    """Exercise real keep-alive connections, truncated transfers, throttling, and resume."""
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
    from urllib.parse import parse_qs

    state = {
        "counts": {}, "active": 0, "peak": 0, "hard_failure": True,
        "client_ports": set(), "body_requests": 0,
    }
    guard = threading.Lock()
    count = 128
    body = "<p>" + ("Reliable page content. " * 1600) + "</p>"
    pages = {
        str(index): {"id": str(index), "spaceId": "10", "title": f"Page {index}", "status": "current",
                     "subtype": "page", "version": {"number": 1}, "body": {"storage": {"value": body}}}
        for index in range(1, count + 1)
    }

    class Handler(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def log_message(self, *_args):
            pass

        def respond(self, payload, status=200, retry=None, truncate=False, next_link=None):
            data = json.dumps(payload).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            if retry is not None:
                self.send_header("Retry-After", retry)
            if next_link:
                self.send_header("Link", f'<{next_link}>; rel="next"')
            self.end_headers()
            try:
                self.wfile.write(data[:len(data) // 2] if truncate else data)
            except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
                pass
            if truncate:
                self.close_connection = True

        def do_GET(self):
            parsed = urlsplit(self.path)
            query = parse_qs(parsed.query)
            if parsed.path.endswith("/spaces"):
                self.respond({"results": [{"id": "10", "key": "ENG"}]})
                return
            if parsed.path.endswith("/pages"):
                if query.get("space-id") != ["10"] or "body-format" in query:
                    self.respond({}, 400)
                    return
                start = int(query.get("cursor", ["0"])[0])
                limit = int(query["limit"][0])
                rows = [{key: value for key, value in page.items() if key != "body"}
                        for page in list(pages.values())[start:start + limit]]
                next_link = f"/wiki/api/v2/pages?cursor={start + len(rows)}" if start + len(rows) < count else None
                self.respond({"results": rows}, next_link=next_link)
                return
            page_id = parsed.path.rsplit("/", 1)[-1]
            with guard:
                state["counts"][page_id] = state["counts"].get(page_id, 0) + 1
                attempt = state["counts"][page_id]
                state["active"] += 1
                state["peak"] = max(state["peak"], state["active"])
                state["client_ports"].add(self.client_address[1])
                state["body_requests"] += 1
            try:
                time.sleep(0.005)
                if page_id == "50" and state["hard_failure"]:
                    self.respond({}, 403)
                elif page_id in {"7", "13"} and attempt == 1:
                    self.respond({}, 503 if page_id == "7" else 429, retry="0.01")
                else:
                    self.respond(pages[page_id], truncate=page_id == "19" and attempt == 1)
            finally:
                with guard:
                    state["active"] -= 1

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    server.daemon_threads = True
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    adapter = _confluence_adapter(
        tmp_path, base_url=f"http://127.0.0.1:{server.server_port}/wiki",
        workers=4, page_size=11, timeout=5, max_retries=2,
    )
    (adapter.raw_dir / "authored.txt").write_text("Preserve this note.", encoding="utf-8")
    started = time.perf_counter()
    try:
        with pytest.raises(ConfluenceSyncError) as error:
            adapter.sync()
        assert error.value.stats["pages"] == count - 1
        assert error.value.stats["retries"] == 3
        assert not list(adapter.raw_dir.glob("*.md"))
        with guard:
            state["hard_failure"] = False
            requests_before_resume = state["body_requests"]
        result = adapter.sync()
        assert result["pages"] == count
        assert result["reused"] == count - 1
        assert result["downloaded"] == 1
        assert state["body_requests"] - requests_before_resume == 1
        assert 1 < state["peak"] <= 4
        assert len(state["client_ports"]) < count // 2
        assert len(list(adapter.raw_dir.glob("*.md"))) == count
        assert (adapter.raw_dir / "authored.txt").read_text() == "Preserve this note."
        summary = {
            "pages": count, "body_bytes_per_page": len(body.encode()), "peak_concurrency": state["peak"],
            "transient_failures_recovered": error.value.stats["retries"],
            "partial_pages_retained": error.value.stats["pages"],
            "resume_downloaded": result["downloaded"], "resume_reused": result["reused"],
            "elapsed_seconds": round(time.perf_counter() - started, 3),
        }
        (tmp_path / "confluence-stress-summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    finally:
        server.shutdown()
        server.server_close()
        server_thread.join(timeout=5)


def test_confluence_web_urls_retain_the_wiki_prefix():
    assert confluence_module._page_url("https://example.com/wiki", {"_links": {"webui": "/spaces/ENG/pages/1"}}) == (
        "https://example.com/wiki/spaces/ENG/pages/1"
    )


def test_confluence_malformed_fresh_version_is_a_cache_miss(tmp_path):
    assert conf_snapshot.cached_page(tmp_path / "missing.json", {"version": "invalid"}) is None


def test_confluence_staging_and_locks_are_not_exported(tmp_path):
    from zipfile import ZipFile

    adapter = _confluence_adapter(tmp_path)
    (adapter.raw_dir / "authored.md").write_text("# Published notes", encoding="utf-8")
    with conf_snapshot.ConfluenceSnapshot(adapter.raw_dir, adapter.source) as snapshot:
        (snapshot.stage / "pending.md").write_text("Uncommitted page", encoding="utf-8")
        archive = adapter.store.archive_keys(["docs"])
        with ZipFile(archive) as handle:
            assert set(handle.namelist()) == {"docs/metadata.yaml", "docs/confluence/confluence-eng/authored.md"}


def test_confluence_recovers_unknown_interrupted_candidate_without_deleting_it(tmp_path):
    adapter = _confluence_adapter(tmp_path)
    (adapter.raw_dir / "original.txt").write_text("previous", encoding="utf-8")
    backup = conf_snapshot.ConfluenceSnapshot(adapter.raw_dir, adapter.source).backup
    adapter.raw_dir.rename(backup)
    adapter.raw_dir.mkdir()
    (adapter.raw_dir / "uncertain.txt").write_text("keep for inspection", encoding="utf-8")
    with conf_snapshot.ConfluenceSnapshot(adapter.raw_dir, adapter.source) as snapshot:
        assert (adapter.raw_dir / "original.txt").read_text() == "previous"
        parked = list(snapshot.work_dir.glob("interrupted-*"))
        assert len(parked) == 1
        assert (parked[0] / "uncertain.txt").read_text() == "keep for inspection"


def test_confluence_completed_swap_cleans_retained_backup(tmp_path, monkeypatch):
    api = _ConfluenceAPI(1)
    api.install(monkeypatch)
    adapter = _confluence_adapter(tmp_path)
    adapter.sync()
    snapshot = conf_snapshot.ConfluenceSnapshot(adapter.raw_dir, adapter.source)
    snapshot.backup.mkdir()
    (snapshot.backup / "old.txt").write_text("old", encoding="utf-8")
    with snapshot:
        assert not snapshot.backup.exists()
        assert (adapter.raw_dir / "1-page-1.md").exists()


def test_confluence_snapshot_preserves_authored_subdirectories(tmp_path, monkeypatch):
    api = _ConfluenceAPI(1)
    api.install(monkeypatch)
    adapter = _confluence_adapter(tmp_path)
    notes = adapter.raw_dir / "notes"
    notes.mkdir()
    (notes / "manual.txt").write_text("keep", encoding="utf-8")
    adapter.sync()
    assert (notes / "manual.txt").read_text() == "keep"


def test_confluence_failed_stage_rename_restores_previous_snapshot(tmp_path, monkeypatch):
    api = _ConfluenceAPI(1)
    api.install(monkeypatch)
    adapter = _confluence_adapter(tmp_path)
    (adapter.raw_dir / "original.txt").write_text("keep", encoding="utf-8")
    original_rename = Path.rename

    def fail_stage(path, target):
        if path.name.startswith("candidate-"):
            raise PermissionError("busy file")
        return original_rename(path, target)

    monkeypatch.setattr(Path, "rename", fail_stage)
    with pytest.raises(ConfluenceSyncError):
        adapter.sync()
    assert (adapter.raw_dir / "original.txt").read_text() == "keep"


def test_confluence_atomic_checkpoint_write_failure_keeps_previous_json(tmp_path):
    path = tmp_path / "checkpoint.json"
    conf_snapshot.atomic_json(path, {"good": True})
    with pytest.raises(TypeError):
        conf_snapshot.atomic_json(path, {"invalid": object()})
    assert json.loads(path.read_text()) == {"good": True}
    assert list(tmp_path.iterdir()) == [path]


@pytest.mark.parametrize("payload", [
    {"schema": 0, "page": {}}, {"schema": 1, "page": []}, {"schema": 1},
    [], "invalid", {"schema": 1, "page": {"version": None}, "sha256": "invalid"},
])
def test_confluence_malformed_checkpoint_is_a_cache_miss(tmp_path, payload):
    path = tmp_path / "1.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    assert conf_snapshot.cached_page(path, _ConfluenceAPI(1).pages["1"]) is None


@pytest.mark.parametrize("content", ["plain notes", "---\n[invalid: yaml\n---\n", "---\n- list\n---\n",
                                     "---\n" + ("x" * 65537), "---\nno closing delimiter"],
                         ids=["plain", "invalid-yaml", "list", "oversized", "unclosed"])
def test_confluence_unrecognized_frontmatter_remains_authored(tmp_path, content):
    path = tmp_path / "note.md"
    path.write_text(content, encoding="utf-8")
    assert conf_snapshot._frontmatter(path) == {}


def test_confluence_cancel_stops_new_requests_and_waits(monkeypatch):
    calls = _confluence_transport(monkeypatch, [])
    with conf_http.ConfluenceClient("https://example.com", ("u", "t")) as client:
        client.cancel()
        with pytest.raises(conf_http.ConfluenceRequestError, match="stopped"):
            client.get_json("api/v2/pages")
        with pytest.raises(conf_http.ConfluenceRequestError, match="stopped"):
            client._wait(0)
    assert not calls


def test_confluence_shared_cooldown_budget_exhaustion(monkeypatch):
    _confluence_clock(monkeypatch)
    with conf_http.ConfluenceClient("https://example.com", ("u", "t")) as client:
        client._cooldown_until = 200
        with pytest.raises(conf_http.ConfluenceRequestError, match="cooldown exceeds"):
            client.get_json("api/v2/pages")


def test_confluence_429_exhaustion_stops_request_group(monkeypatch):
    _confluence_transport(monkeypatch, [_FakeResponse({}, 429)])
    with conf_http.ConfluenceClient("https://example.com", ("u", "t"),
                                   conf_http.ConfluenceOptions(max_retries=0)) as client:
        with pytest.raises(conf_http.ConfluenceRequestError) as error:
            client.get_json("api/v2/pages")
        assert error.value.fatal
        assert client._cancelled.is_set()


@pytest.mark.parametrize("spaces", [None, {}, [None], [], [{"id": "10", "key": "OTHER"}]])
def test_confluence_missing_or_malformed_space_is_not_an_empty_success(tmp_path, monkeypatch, spaces):
    _confluence_transport(monkeypatch, [_FakeResponse({"results": spaces})])
    adapter = _confluence_adapter(tmp_path)
    with pytest.raises(ConfluenceSyncError):
        adapter.sync()
    assert not (adapter.raw_dir / "source-metadata.yaml").exists()


def test_confluence_incomplete_json_read_is_retried(monkeypatch):
    _confluence_clock(monkeypatch)
    calls = _confluence_transport(monkeypatch, [_FakeResponse(ValueError("truncated")), _FakeResponse({"ok": True})])
    with conf_http.ConfluenceClient("https://example.com", ("u", "t")) as client:
        assert client.get_json("api/v2/pages") == {"ok": True}
        assert client.retries == 1
    assert len(calls) == 2


@pytest.mark.parametrize(("payload", "expected_calls"), [
    ({}, 3),
    ({"errorCode": "SUSPENDED_INACTIVITY", "errorMessage": "fixture-token"}, 1),
])
def test_confluence_live_smoke_preflight_failure_prevents_all_writes(
    tmp_path, monkeypatch, capsys, payload, expected_calls
):
    import importlib.util

    path = Path(__file__).resolve().parents[1] / "scripts" / "confluence_sync_smoke.py"
    spec = importlib.util.spec_from_file_location("confluence_live_smoke", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setattr(module, "ROOT", tmp_path)
    monkeypatch.setenv("CONFLUENCE_BASE_URL", "https://example.com")
    monkeypatch.setenv("CONFLUENCE_USERNAME", "fixture-user")
    monkeypatch.setenv("CONFLUENCE_TOKEN", "fixture-token")
    # main changes these variables; registering them makes fixture teardown restore them.
    monkeypatch.setenv("TMP", str(tmp_path))
    monkeypatch.setenv("TEMP", str(tmp_path))
    _confluence_clock(monkeypatch)
    calls = _confluence_transport(monkeypatch, [_FakeResponse(payload, 503)] * expected_calls)
    posts = []
    monkeypatch.setattr(requests.Session, "post", lambda *args, **kwargs: posts.append(args))
    output = tmp_path / "smoke"
    assert module.main(["--create-fixture", "--output", str(output)]) == 1
    report = json.loads((output / "live-report.json").read_text())
    assert report["phase"] == "preflight"
    assert report["writes"] == []
    assert report["complete"] is False
    assert len(calls) == expected_calls
    assert not posts
    assert "fixture-token" not in capsys.readouterr().out
    if expected_calls == 1:
        assert "SUSPENDED_INACTIVITY" in report["error"]


def test_confluence_live_smoke_requires_explicit_site_visible_fixture(tmp_path, monkeypatch, capsys):
    import importlib.util

    path = Path(__file__).resolve().parents[1] / "scripts" / "confluence_sync_smoke.py"
    spec = importlib.util.spec_from_file_location("confluence_live_smoke_site_visible", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setattr(module, "ROOT", tmp_path)
    monkeypatch.setenv("CONFLUENCE_BASE_URL", "https://example.com")
    monkeypatch.setenv("CONFLUENCE_USERNAME", "fixture-user")
    monkeypatch.setenv("CONFLUENCE_TOKEN", "fixture-token")
    monkeypatch.setenv("TMP", str(tmp_path))
    monkeypatch.setenv("TEMP", str(tmp_path))
    calls = _confluence_transport(
        monkeypatch,
        [_FakeResponse({"accountId": "user-1"}), _FakeResponse({"results": []})],
    )
    posts = []

    def reject_space(_session, _url, **kwargs):
        posts.append(kwargs["json"])
        return _FakeResponse({"message": "fixture-token"}, 403)

    monkeypatch.setattr(requests.Session, "post", reject_space)
    output = tmp_path / "site-visible-smoke"
    assert module.main([
        "--create-fixture", "--site-visible-fixture", "--output", str(output)
    ]) == 1
    report = json.loads((output / "live-report.json").read_text())
    assert len(calls) == 2
    assert len(posts) == 1
    assert posts[0]["createPrivateSpace"] is False
    assert posts[0]["name"].startswith("Know synthetic sync test ")
    assert report["fixture_visibility"] == "site"
    assert report["writes"][0]["state"] == "unverified"
    assert "fixture-token" not in capsys.readouterr().out


def test_confluence_nonprogressing_page_inventory_fails_after_checkpointing(tmp_path, monkeypatch):
    api = _ConfluenceAPI(2)
    adapter = _confluence_adapter(tmp_path)
    original_get = api.get

    def repeated(session, url, **kwargs):
        if url.endswith("/pages"):
            rows = [{key: value for key, value in page.items() if key != "body"} for page in api.pages.values()]
            cursor = "second" if not kwargs["params"].get("cursor") else "third"
            return _FakeResponse({"results": rows, "_links": {"next": f"?cursor={cursor}"}})
        return original_get(session, url, **kwargs)

    monkeypatch.setattr(requests.Session, "get", repeated)
    with pytest.raises(ConfluenceSyncError) as error:
        adapter.sync()
    assert error.value.stats["pages"] == 2
    assert "no progress" in error.value.stats["failures"][0]["error"]
    assert not list(adapter.raw_dir.glob("*.md"))


def test_confluence_cql_ignores_nonpages_and_deduplicates_page_ids(tmp_path, monkeypatch):
    api = _ConfluenceAPI(1)
    adapter = _confluence_adapter(tmp_path, cql="type=page")
    original_get = api.get

    def mixed(session, url, **kwargs):
        if url.endswith("/search"):
            metadata = {key: value for key, value in api.pages["1"].items() if key != "body"}
            return _FakeResponse({"results": [
                {"content": {"id": "2", "type": "blogpost"}},
                {"content": metadata}, {"content": metadata},
            ]})
        return original_get(session, url, **kwargs)

    monkeypatch.setattr(requests.Session, "get", mixed)
    result = adapter.sync()
    assert result["pages"] == 1
    assert result["discovered"] == 1


def test_confluence_fatal_page_auth_failure_is_reported(tmp_path, monkeypatch):
    api = _ConfluenceAPI(3)
    api.fail_pages["1"] = 401
    api.install(monkeypatch)
    adapter = _confluence_adapter(tmp_path, workers=1)
    with pytest.raises(ConfluenceSyncError) as error:
        adapter.sync()
    assert error.value.stats["failures"][0]["status"] == 401
    assert not list(adapter.raw_dir.glob("*.md"))


def test_confluence_success_is_not_reversed_by_cache_report_failure(tmp_path, monkeypatch):
    api = _ConfluenceAPI(1)
    api.install(monkeypatch)
    adapter = _confluence_adapter(tmp_path)
    original_json = confluence_module.atomic_json

    def write_report(path, payload):
        if payload["complete"]:
            raise OSError("unavailable cache")
        original_json(path, payload)

    monkeypatch.setattr(confluence_module, "atomic_json", write_report)
    assert adapter.sync()["complete"]
    assert (adapter.raw_dir / "1-page-1.md").exists()
    assert adapter.source["last_synced_at"]


def test_confluence_success_retains_busy_backup_for_later_cleanup(tmp_path, monkeypatch):
    api = _ConfluenceAPI(1)
    api.install(monkeypatch)
    adapter = _confluence_adapter(tmp_path)
    backup = conf_snapshot.ConfluenceSnapshot(adapter.raw_dir, adapter.source).backup
    original_remove = conf_snapshot.shutil.rmtree

    def remove(path, *args, **kwargs):
        if path == backup:
            raise PermissionError("backup is in use")
        original_remove(path, *args, **kwargs)

    monkeypatch.setattr(conf_snapshot.shutil, "rmtree", remove)
    assert adapter.sync()["complete"]
    assert backup.is_dir()
    assert (adapter.raw_dir / "1-page-1.md").exists()


@pytest.mark.parametrize("function,kwargs", [
    (confluence_module.search_confluence, {"cql": "type=page"}),
    (confluence_module.list_confluence_spaces, {}),
    (confluence_module.list_confluence_pages, {"space": "ENG"}),
])
def test_confluence_read_helpers_reject_nonpositive_limits(monkeypatch, function, kwargs):
    calls = _confluence_transport(monkeypatch, [])
    with pytest.raises(ValueError):
        function(base_url="https://example.com", username="u", token="t", limit=0, **kwargs)
    assert not calls


def test_confluence_search_rejects_malformed_result_schema(monkeypatch):
    _confluence_transport(monkeypatch, [_FakeResponse({"results": {}})])
    with pytest.raises(conf_http.ConfluenceRequestError, match="malformed results"):
        confluence_module.search_confluence(base_url="https://example.com", username="u", token="t", cql="type=page")


def test_confluence_browse_deduplicates_rows_and_detects_no_progress(monkeypatch):
    _confluence_transport(monkeypatch, [
        _FakeResponse({"results": [{"key": "ENG"}, {"key": "ENG"}], "_links": {"next": "?start=2"}}),
        _FakeResponse({"results": [{"key": "ENG"}]}),
    ])
    with pytest.raises(conf_http.ConfluenceRequestError, match="no progress"):
        confluence_module.list_confluence_spaces(base_url="https://example.com", username="u", token="t")


def test_confluence_browse_rejects_missing_identity(monkeypatch):
    _confluence_transport(monkeypatch, [_FakeResponse({"results": [{}]})])
    with pytest.raises(conf_http.ConfluenceRequestError, match="without an identity"):
        confluence_module.list_confluence_spaces(base_url="https://example.com", username="u", token="t")
