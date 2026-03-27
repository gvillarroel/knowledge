"""Tests for follow browse commands."""

from __future__ import annotations

import re
import threading
from argparse import Namespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from knowledge.browse_commands import (
    cmd_browse_follow,
    cmd_browse_follow_launch,
    cmd_browse_follow_open,
    _resolve_follow_url,
)
from knowledge.browse_tv import (
    format_follow_preview,
    format_follow_television,
    _find_follow_item,
)


def _make_args(**kwargs) -> Namespace:
    defaults = {"store": None, "json": False, "verbose": False, "quiet": False}
    defaults.update(kwargs)
    return Namespace(**defaults)


def _clean(text: str) -> str:
    return re.sub(r"\033\[[0-9;]*m", "", text)


# ── Sample data ──────────────────────────────────────────────────────────

GITHUB_ITEMS = [
    {
        "source": "github",
        "repo": "owner/repo",
        "element_type": "issue",
        "id": "42",
        "title": "Fix bug",
        "url": "https://github.com/owner/repo/issues/42",
        "user": "alice",
        "created_at": "2026-01-01T00:00:00Z",
        "updated_at": "2026-03-01T00:00:00Z",
        "body": "Something is broken",
        "labels": ["bug"],
        "comments_count": 3,
        "state": "open",
        "path": "github/owner/repo/issue/42",
    },
    {
        "source": "github",
        "repo": "owner/repo",
        "element_type": "pull_request",
        "id": "55",
        "title": "Add feature",
        "url": "https://github.com/owner/repo/pull/55",
        "user": "bob",
        "created_at": "2026-02-01T00:00:00Z",
        "updated_at": "2026-03-10T00:00:00Z",
        "body": "New feature PR",
        "labels": ["enhancement"],
        "comments_count": 1,
        "state": "open",
        "path": "github/owner/repo/pull_request/55",
    },
    {
        "source": "github",
        "repo": "owner/repo",
        "element_type": "discussion",
        "id": "7",
        "title": "Roadmap ideas",
        "url": "https://github.com/owner/repo/discussions/7",
        "user": "carol",
        "created_at": "2026-02-15T00:00:00Z",
        "updated_at": "2026-03-20T00:00:00Z",
        "body": "Let's discuss the roadmap",
        "labels": [],
        "comments_count": 5,
        "state": "open",
        "path": "github/owner/repo/discussion/7",
    },
]

JIRA_ITEMS = [
    {
        "source": "jira",
        "project": "KAN",
        "element_type": "task",
        "id": "KAN-123",
        "title": "Implement login",
        "url": "https://myco.atlassian.net/browse/KAN-123",
        "status": "In Progress",
        "priority": "High",
        "assignee": "dave",
        "reporter": "eve",
        "labels": ["backend"],
        "created_at": "2026-01-10T00:00:00Z",
        "updated_at": "2026-03-05T00:00:00Z",
        "body": "",
        "state": "open",
        "path": "jira/KAN/task/KAN-123",
    },
]

ALL_ITEMS = GITHUB_ITEMS + JIRA_ITEMS


# ── format_follow_television ─────────────────────────────────────────────

class TestFormatFollowTelevision:
    def test_renders_github_paths(self):
        out = format_follow_television(GITHUB_ITEMS)
        clean = _clean(out)
        assert "github/owner/repo/issue/42" in clean
        assert "github/owner/repo/pull_request/55" in clean
        assert "github/owner/repo/discussion/7" in clean

    def test_renders_jira_paths(self):
        out = format_follow_television(JIRA_ITEMS)
        clean = _clean(out)
        assert "jira/KAN/task/KAN-123" in clean

    def test_empty_list(self):
        out = format_follow_television([])
        assert out == ""

    def test_mixed_sources(self):
        out = format_follow_television(ALL_ITEMS)
        lines = out.strip().split("\n")
        assert len(lines) == 4


# ── format_follow_preview ────────────────────────────────────────────────

class TestFormatFollowPreview:
    def test_github_issue_preview(self):
        out = format_follow_preview(GITHUB_ITEMS, "github/owner/repo/issue/42")
        assert "Fix bug" in out
        assert "Issue #42" in out
        assert "@alice" in out

    def test_github_pr_preview(self):
        out = format_follow_preview(
            GITHUB_ITEMS, "github/owner/repo/pull_request/55/Add feature"
        )
        assert "Pull Request #55" in out
        assert "Add feature" in out

    def test_github_discussion_preview(self):
        out = format_follow_preview(
            GITHUB_ITEMS, "github/owner/repo/discussion/7/Roadmap ideas"
        )
        assert "Discussion #7" in out

    def test_jira_preview(self):
        out = format_follow_preview(JIRA_ITEMS, "jira/KAN/task/KAN-123")
        assert "KAN-123" in out
        assert "Implement login" in out
        assert "In Progress" in out

    def test_no_match_returns_fallback(self):
        out = format_follow_preview([], "nonexistent")
        assert "No item matched" in out

    def test_no_selection_returns_first(self):
        out = format_follow_preview(JIRA_ITEMS, None)
        assert "KAN-123" in out

    def test_github_with_labels(self):
        out = format_follow_preview(GITHUB_ITEMS, "github/owner/repo/issue/42")
        assert "bug" in out

    def test_jira_with_labels(self):
        out = format_follow_preview(JIRA_ITEMS, "jira/KAN/task/KAN-123")
        assert "backend" in out


# ── _find_follow_item ────────────────────────────────────────────────────

class TestFindFollowItem:
    def test_exact_path_match(self):
        item = _find_follow_item(ALL_ITEMS, "github/owner/repo/issue/42")
        assert item is not None
        assert item["id"] == "42"

    def test_id_match(self):
        item = _find_follow_item(ALL_ITEMS, "something/42/else")
        assert item is not None
        assert item["id"] == "42"

    def test_no_items(self):
        assert _find_follow_item([], "anything") is None

    def test_no_selection(self):
        item = _find_follow_item(ALL_ITEMS, None)
        assert item == ALL_ITEMS[0]

    def test_fallback_to_first(self):
        item = _find_follow_item(ALL_ITEMS, "completely-unrelated")
        assert item == ALL_ITEMS[0]


# ── _resolve_follow_url ─────────────────────────────────────────────────

class TestResolveFollowUrl:
    def test_github_issue(self):
        args = _make_args()
        url = _resolve_follow_url("github/owner/repo/issue/42", args)
        assert url == "https://github.com/owner/repo/issues/42"

    def test_github_pull_request(self):
        args = _make_args()
        url = _resolve_follow_url("github/owner/repo/pull_request/55", args)
        assert url == "https://github.com/owner/repo/pull/55"

    def test_github_discussion(self):
        args = _make_args()
        url = _resolve_follow_url("github/owner/repo/discussion/7", args)
        assert url == "https://github.com/owner/repo/discussions/7"

    def test_jira_with_store(self):
        mock_store = MagicMock()
        mock_store.list_collection_sources.return_value = [
            {"config": {"base_url": "https://myco.atlassian.net"}},
        ]
        with patch(
            "knowledge.browse_commands._store_from_args",
            return_value=mock_store,
        ):
            args = _make_args()
            url = _resolve_follow_url("jira/KAN/task/KAN-123", args)
            assert url == "https://myco.atlassian.net/browse/KAN-123"

    def test_jira_no_sources(self):
        mock_store = MagicMock()
        mock_store.list_collection_sources.return_value = []
        with patch(
            "knowledge.browse_commands._store_from_args",
            return_value=mock_store,
        ):
            args = _make_args()
            url = _resolve_follow_url("jira/KAN/task/KAN-123", args)
            assert url is None

    def test_short_path(self):
        args = _make_args()
        url = _resolve_follow_url("too/short", args)
        assert url is None

    def test_unknown_source(self):
        args = _make_args()
        url = _resolve_follow_url("unknown/a/b/c/d", args)
        assert url is None


# ── cmd_browse_follow ────────────────────────────────────────────────────

class TestCmdBrowseFollow:
    def test_json_format_no_data(self):
        mock_store = MagicMock()
        mock_store.list_collection_sources.return_value = []
        with patch(
            "knowledge.browse_commands._store_from_args",
            return_value=mock_store,
        ), patch(
            "knowledge.browse_commands._resolve_github_token",
            return_value=None,
        ):
            args = _make_args(format="json", entry=None)
            result = cmd_browse_follow(args)
            assert isinstance(result, dict)
            assert result["items"] == []

    def test_television_format_with_github(self):
        mock_store = MagicMock()
        mock_store.list_collection_sources.return_value = []
        fake_repos = [
            {
                "full_name": "owner/repo",
                "updated_at": "2026-03-01T00:00:00Z",
                "pushed_at": "2026-03-01T00:00:00Z",
            }
        ]
        fake_activity = [
            {
                "kind": "issue",
                "number": 1,
                "title": "Open issue",
                "state": "open",
                "user": "user1",
                "created_at": "2026-02-01T00:00:00Z",
                "updated_at": "2026-03-01T00:00:00Z",
                "body": "body text",
                "labels": [],
                "url": "https://github.com/owner/repo/issues/1",
                "comments_count": 0,
            }
        ]
        with patch(
            "knowledge.browse_commands._store_from_args",
            return_value=mock_store,
        ), patch(
            "knowledge.browse_commands._resolve_github_token",
            return_value="fake-token",
        ), patch(
            "knowledge.sources.github_api.list_user_repos",
            return_value=fake_repos,
        ), patch(
            "knowledge.sources.github_api.list_starred_repos",
            return_value=[],
        ), patch(
            "knowledge.sources.github_api.list_repo_activity",
            return_value=fake_activity,
        ):
            args = _make_args(format="television", entry=None)
            result = cmd_browse_follow(args)
            assert isinstance(result, str)
            clean = _clean(result)
            assert "github/owner/repo/issue/1" in clean

    def test_television_preview_format(self):
        mock_store = MagicMock()
        mock_store.list_collection_sources.return_value = []
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {
            "title": "Preview this",
            "body": "Preview body",
            "state": "open",
            "user": {"login": "alice"},
            "created_at": "2026-02-01T00:00:00Z",
            "updated_at": "2026-03-01T00:00:00Z",
            "labels": [],
            "html_url": "https://github.com/owner/repo/issues/10",
        }
        with patch(
            "knowledge.browse_commands._store_from_args",
            return_value=mock_store,
        ), patch(
            "knowledge.browse_commands._resolve_github_token",
            return_value="fake-token",
        ), patch(
            "requests.get",
            return_value=mock_response,
        ):
            args = _make_args(
                format="television-preview",
                entry="github/owner/repo/issue/10",
            )
            result = cmd_browse_follow(args)
            assert isinstance(result, str)
            assert "Preview this" in result

    def test_jira_items_included(self):
        mock_store = MagicMock()
        mock_store.list_collection_sources.return_value = [
            {
                "type": "jira",
                "id": "src1",
                "config": {
                    "base_url": "https://co.atlassian.net",
                    "username": "$jira_user",
                    "token": "$jira_token",
                    "project": "KAN",
                    "limit": 10,
                },
            }
        ]
        mock_store.resolve_key.side_effect = lambda k: "resolved"
        fake_issues = {
            "issues": [
                {
                    "key": "KAN-1",
                    "fields": {
                        "summary": "Open task",
                        "status": {
                            "name": "To Do",
                            "statusCategory": {"name": "To Do"},
                        },
                        "issuetype": {"name": "Task"},
                        "priority": {"name": "Medium"},
                        "assignee": {"displayName": "Dave"},
                        "reporter": {"displayName": "Eve"},
                        "labels": [],
                        "created": "2026-01-01T00:00:00Z",
                        "updated": "2026-03-01T00:00:00Z",
                    },
                },
            ],
        }
        with patch(
            "knowledge.browse_commands._store_from_args",
            return_value=mock_store,
        ), patch(
            "knowledge.browse_commands._resolve_github_token",
            return_value=None,
        ), patch(
            "knowledge.sources.jira.search_jira",
            return_value=fake_issues,
        ):
            args = _make_args(format="json", entry=None)
            result = cmd_browse_follow(args)
            assert len(result["items"]) == 1
            item = result["items"][0]
            assert item["source"] == "jira"
            assert item["path"] == "jira/KAN/task/KAN-1"

    def test_jira_done_items_excluded(self):
        mock_store = MagicMock()
        mock_store.list_collection_sources.return_value = [
            {
                "type": "jira",
                "id": "src1",
                "config": {
                    "base_url": "https://co.atlassian.net",
                    "username": "$jira_user",
                    "token": "$jira_token",
                    "project": "KAN",
                    "limit": 10,
                },
            }
        ]
        mock_store.resolve_key.side_effect = lambda k: "resolved"
        fake_issues = {
            "issues": [
                {
                    "key": "KAN-99",
                    "fields": {
                        "summary": "Done task",
                        "status": {
                            "name": "Done",
                            "statusCategory": {"name": "Done"},
                        },
                        "issuetype": {"name": "Task"},
                        "priority": {"name": "Low"},
                        "assignee": None,
                        "reporter": None,
                        "labels": [],
                        "created": "2026-01-01T00:00:00Z",
                        "updated": "2026-03-01T00:00:00Z",
                    },
                },
            ],
        }
        with patch(
            "knowledge.browse_commands._store_from_args",
            return_value=mock_store,
        ), patch(
            "knowledge.browse_commands._resolve_github_token",
            return_value=None,
        ), patch(
            "knowledge.sources.jira.search_jira",
            return_value=fake_issues,
        ):
            args = _make_args(format="json", entry=None)
            result = cmd_browse_follow(args)
            assert len(result["items"]) == 0

    def test_old_github_repos_excluded(self):
        """Repos not updated in last 6 months should be skipped."""
        mock_store = MagicMock()
        mock_store.list_collection_sources.return_value = []
        fake_repos = [
            {
                "full_name": "old/repo",
                "updated_at": "2020-01-01T00:00:00Z",
                "pushed_at": "2020-01-01T00:00:00Z",
            }
        ]
        with patch(
            "knowledge.browse_commands._store_from_args",
            return_value=mock_store,
        ), patch(
            "knowledge.browse_commands._resolve_github_token",
            return_value="fake-token",
        ), patch(
            "knowledge.sources.github_api.list_user_repos",
            return_value=fake_repos,
        ), patch(
            "knowledge.sources.github_api.list_starred_repos",
            return_value=[],
        ):
            args = _make_args(format="json", entry=None)
            result = cmd_browse_follow(args)
            assert len(result["items"]) == 0

    def test_starred_github_repos_are_included(self):
        mock_store = MagicMock()
        mock_store.list_collection_sources.return_value = []
        fake_activity = [
            {
                "kind": "issue",
                "number": 9,
                "title": "Starred repo issue",
                "state": "open",
                "user": "user1",
                "created_at": "2026-02-01T00:00:00Z",
                "updated_at": "2026-03-01T00:00:00Z",
                "body": "body text",
                "labels": [],
                "url": "https://github.com/starred/repo/issues/9",
                "comments_count": 0,
            }
        ]
        fake_starred_repos = [
            {
                "full_name": "starred/repo",
                "updated_at": "2026-03-01T00:00:00Z",
                "pushed_at": "2026-03-01T00:00:00Z",
            }
        ]
        with patch(
            "knowledge.browse_commands._store_from_args",
            return_value=mock_store,
        ), patch(
            "knowledge.browse_commands._resolve_github_token",
            return_value="fake-token",
        ), patch(
            "knowledge.sources.github_api.list_user_repos",
            return_value=[],
        ), patch(
            "knowledge.sources.github_api.list_starred_repos",
            return_value=fake_starred_repos,
        ), patch(
            "knowledge.sources.github_api.list_repo_activity",
            return_value=fake_activity,
        ):
            args = _make_args(format="json", entry=None)
            result = cmd_browse_follow(args)
            assert len(result["items"]) == 1
            assert result["items"][0]["repo"] == "starred/repo"

    def test_starred_and_owned_github_repos_are_deduplicated(self):
        mock_store = MagicMock()
        mock_store.list_collection_sources.return_value = []
        fake_repo = {
            "full_name": "owner/repo",
            "updated_at": "2026-03-01T00:00:00Z",
            "pushed_at": "2026-03-01T00:00:00Z",
        }
        with patch(
            "knowledge.browse_commands._store_from_args",
            return_value=mock_store,
        ), patch(
            "knowledge.browse_commands._resolve_github_token",
            return_value="fake-token",
        ), patch(
            "knowledge.sources.github_api.list_user_repos",
            return_value=[fake_repo],
        ), patch(
            "knowledge.sources.github_api.list_starred_repos",
            return_value=[fake_repo],
        ), patch(
            "knowledge.sources.github_api.list_repo_activity",
            return_value=[],
        ) as activity_mock:
            args = _make_args(format="json", entry=None)
            result = cmd_browse_follow(args)
            assert result["items"] == []
            activity_mock.assert_called_once_with(
                "fake-token",
                "owner",
                "repo",
                state="open",
                per_page=50,
            )

    def test_github_repo_activity_requests_run_concurrently(self):
        mock_store = MagicMock()
        mock_store.list_collection_sources.return_value = []
        fake_repos = [
            {
                "full_name": "owner/repo-one",
                "updated_at": "2026-03-01T00:00:00Z",
                "pushed_at": "2026-03-01T00:00:00Z",
            },
            {
                "full_name": "owner/repo-two",
                "updated_at": "2026-03-02T00:00:00Z",
                "pushed_at": "2026-03-02T00:00:00Z",
            },
        ]
        gate = threading.Event()
        started = 0
        started_lock = threading.Lock()
        all_started = threading.Event()

        def fake_activity(token, owner, repo_name, **kwargs):
            nonlocal started
            with started_lock:
                started += 1
                if started == 2:
                    all_started.set()
            assert all_started.wait(timeout=1), "repo activity calls did not overlap"
            gate.wait(timeout=1)
            return [{
                "kind": "issue",
                "number": 1,
                "title": f"{repo_name} issue",
                "state": "open",
                "user": "user1",
                "created_at": "2026-02-01T00:00:00Z",
                "updated_at": "2026-03-01T00:00:00Z",
                "body": "body text",
                "labels": [],
                "url": f"https://github.com/owner/{repo_name}/issues/1",
                "comments_count": 0,
            }]

        with patch(
            "knowledge.browse_commands._store_from_args",
            return_value=mock_store,
        ), patch(
            "knowledge.browse_commands._resolve_github_token",
            return_value="fake-token",
        ), patch(
            "knowledge.sources.github_api.list_user_repos",
            return_value=fake_repos,
        ), patch(
            "knowledge.sources.github_api.list_starred_repos",
            return_value=[],
        ), patch(
            "knowledge.sources.github_api.list_repo_activity",
            side_effect=fake_activity,
        ):
            gate.set()
            args = _make_args(format="json", entry=None)
            result = cmd_browse_follow(args)
            assert len(result["items"]) == 2

    def test_jira_source_requests_run_concurrently(self):
        mock_store = MagicMock()
        mock_store.list_collection_sources.return_value = [
            {
                "type": "jira",
                "id": "src1",
                "config": {
                    "base_url": "https://co.atlassian.net",
                    "username": "$jira_user",
                    "token": "$jira_token",
                    "project": "KAN",
                    "limit": 10,
                },
            },
            {
                "type": "jira",
                "id": "src2",
                "config": {
                    "base_url": "https://co.atlassian.net",
                    "username": "$jira_user",
                    "token": "$jira_token",
                    "project": "OPS",
                    "limit": 10,
                },
            },
        ]
        mock_store.resolve_key.side_effect = lambda k: "resolved"
        gate = threading.Event()
        started = 0
        started_lock = threading.Lock()
        all_started = threading.Event()

        def fake_search_jira(*, jql, **kwargs):
            nonlocal started
            with started_lock:
                started += 1
                if started == 2:
                    all_started.set()
            assert all_started.wait(timeout=1), "jira search calls did not overlap"
            gate.wait(timeout=1)
            project = "KAN" if "project = KAN" in jql else "OPS"
            return {
                "issues": [
                    {
                        "key": f"{project}-1",
                        "fields": {
                            "summary": f"{project} open task",
                            "status": {
                                "name": "To Do",
                                "statusCategory": {"name": "To Do"},
                            },
                            "issuetype": {"name": "Task"},
                            "priority": {"name": "Medium"},
                            "assignee": {"displayName": "Dave"},
                            "reporter": {"displayName": "Eve"},
                            "labels": [],
                            "created": "2026-01-01T00:00:00Z",
                            "updated": "2026-03-01T00:00:00Z",
                        },
                    },
                ],
            }

        with patch(
            "knowledge.browse_commands._store_from_args",
            return_value=mock_store,
        ), patch(
            "knowledge.browse_commands._resolve_github_token",
            return_value=None,
        ), patch(
            "knowledge.sources.jira.search_jira",
            side_effect=fake_search_jira,
        ):
            gate.set()
            args = _make_args(format="json", entry=None)
            result = cmd_browse_follow(args)
            assert len(result["items"]) == 2

    def test_uses_cached_follow_items_when_available(self):
        mock_store = MagicMock()
        mock_store.initialize.return_value = None
        cached_items = [{"path": "github/owner/repo/issue/1", "source": "github"}]
        with patch(
            "knowledge.browse_commands._store_from_args",
            return_value=mock_store,
        ), patch(
            "knowledge.browse_commands._load_follow_cache",
            return_value=cached_items,
        ), patch(
            "knowledge.browse_commands._collect_follow_items",
            new_callable=AsyncMock,
        ) as collect_mock:
            args = _make_args(format="json", entry=None)
            result = cmd_browse_follow(args)
            assert result == {"items": cached_items}
            collect_mock.assert_not_called()

    def test_saves_follow_items_after_cache_miss(self):
        mock_store = MagicMock()
        mock_store.initialize.return_value = None
        fetched_items = [{"path": "jira/KAN/task/KAN-1", "source": "jira"}]
        with patch(
            "knowledge.browse_commands._store_from_args",
            return_value=mock_store,
        ), patch(
            "knowledge.browse_commands._load_follow_cache",
            return_value=None,
        ), patch(
            "knowledge.browse_commands._collect_follow_items",
            new_callable=AsyncMock,
            return_value=fetched_items,
        ) as collect_mock, patch(
            "knowledge.browse_commands._save_follow_cache",
        ) as save_mock:
            args = _make_args(format="json", entry=None)
            result = cmd_browse_follow(args)
            assert result == {"items": fetched_items}
            collect_mock.assert_called_once()
            save_mock.assert_called_once_with(mock_store, fetched_items)


# ── cmd_browse_follow_open (now follow-url: returns URL only) ────────────

class TestCmdBrowseFollowOpen:
    def test_github_issue_url(self):
        args = _make_args(selected_row="🔵github/owner/repo/issue/42 Fix bug")
        result = cmd_browse_follow_open(args)
        assert result == "https://github.com/owner/repo/issues/42"

    def test_github_pr_url(self):
        args = _make_args(selected_row="🟢github/owner/repo/pull_request/55 Add feature")
        result = cmd_browse_follow_open(args)
        assert result == "https://github.com/owner/repo/pull/55"

    def test_github_discussion_url(self):
        args = _make_args(selected_row="💬github/owner/repo/discussion/7 Ideas")
        result = cmd_browse_follow_open(args)
        assert result == "https://github.com/owner/repo/discussions/7"

    def test_jira_url(self):
        mock_store = MagicMock()
        mock_store.list_collection_sources.return_value = [
            {"config": {"base_url": "https://myco.atlassian.net"}},
        ]
        with patch(
            "knowledge.browse_commands._store_from_args",
            return_value=mock_store,
        ):
            args = _make_args(selected_row="🔷jira/KAN/task/KAN-123 Implement login")
            result = cmd_browse_follow_open(args)
            assert result == "https://myco.atlassian.net/browse/KAN-123"

    def test_unresolvable_row(self):
        args = _make_args(selected_row="garbage")
        result = cmd_browse_follow_open(args)
        assert result == ""

    def test_with_ansi_codes(self):
        ansi_row = "\033[36m🔵\033[0mgithub/owner/repo/issue/42 Fix bug"
        args = _make_args(selected_row=ansi_row)
        result = cmd_browse_follow_open(args)
        assert result == "https://github.com/owner/repo/issues/42"


class TestCmdBrowseFollowLaunch:
    def test_opens_resolved_url(self):
        args = _make_args(selected_row="🔵github/owner/repo/issue/42 Fix bug")
        with patch("webbrowser.open", return_value=True) as open_mock:
            result = cmd_browse_follow_launch(args)
            assert result == ""
            open_mock.assert_called_once_with(
                "https://github.com/owner/repo/issues/42",
                new=2,
            )

    def test_returns_url_when_browser_open_fails(self):
        args = _make_args(selected_row="🔵github/owner/repo/issue/42 Fix bug")
        with patch("webbrowser.open", return_value=False):
            result = cmd_browse_follow_launch(args)
            assert result == "https://github.com/owner/repo/issues/42"

    def test_returns_empty_for_unresolvable_row(self):
        args = _make_args(selected_row="garbage")
        with patch("webbrowser.open") as open_mock:
            result = cmd_browse_follow_launch(args)
            assert result == ""
            open_mock.assert_not_called()
