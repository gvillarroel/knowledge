"""Tests for the GitHub API client module."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from knowledge.sources.github_api import (
    list_user_repos,
    list_starred_repos,
    list_repo_issues,
    list_repo_pulls,
    list_repo_discussions,
    list_repo_activity,
    get_issue_comments,
    get_pr_detail,
    render_issue_thread_markdown,
    _headers,
)


class TestHeaders:
    def test_bearer_token(self):
        h = _headers("test-token")
        assert h["Authorization"] == "Bearer test-token"
        assert "application/vnd.github" in h["Accept"]


class TestListUserRepos:
    @patch("knowledge.sources.github_api.requests.get")
    def test_returns_repos(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.json.return_value = [{"full_name": "user/repo1"}, {"full_name": "user/repo2"}]
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        repos = list_user_repos("tok")
        assert len(repos) == 2
        assert repos[0]["full_name"] == "user/repo1"


class TestListStarredRepos:
    @patch("knowledge.sources.github_api.requests.get")
    def test_returns_starred_repos(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.json.return_value = [{"full_name": "user/starred"}]
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        repos = list_starred_repos("tok")
        assert repos == [{"full_name": "user/starred"}]


class TestListRepoIssues:
    @patch("knowledge.sources.github_api.requests.get")
    def test_returns_issues(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.json.return_value = [
            {"number": 1, "title": "Bug", "state": "open"},
        ]
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        issues = list_repo_issues("tok", "owner", "repo")
        assert len(issues) == 1
        assert issues[0]["number"] == 1


class TestListRepoPulls:
    @patch("knowledge.sources.github_api.requests.get")
    def test_returns_pulls(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.json.return_value = [{"number": 10, "title": "Fix"}]
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        pulls = list_repo_pulls("tok", "owner", "repo")
        assert len(pulls) == 1


class TestListRepoDiscussions:
    @patch("knowledge.sources.github_api.requests.post")
    def test_returns_discussions(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            "data": {
                "repository": {
                    "discussions": {
                        "nodes": [
                            {"number": 1, "title": "Q&A", "body": "Question",
                             "url": "https://github.com/o/r/discussions/1",
                             "author": {"login": "alice"},
                             "category": {"name": "Q&A"},
                             "comments": {"nodes": []}}
                        ]
                    }
                }
            }
        }
        mock_resp.raise_for_status = MagicMock()
        mock_post.return_value = mock_resp

        discussions = list_repo_discussions("tok", "owner", "repo")
        assert len(discussions) == 1
        assert discussions[0]["title"] == "Q&A"

    @patch("knowledge.sources.github_api.requests.post")
    def test_handles_empty_response(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"data": {"repository": None}}
        mock_resp.raise_for_status = MagicMock()
        mock_post.return_value = mock_resp

        discussions = list_repo_discussions("tok", "owner", "repo")
        assert discussions == []


class TestGetIssueComments:
    @patch("knowledge.sources.github_api.requests.get")
    def test_returns_comments(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.json.return_value = [
            {"body": "comment 1", "user": {"login": "alice"}},
        ]
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        comments = get_issue_comments("tok", "owner", "repo", 1)
        assert len(comments) == 1


class TestGetPrDetail:
    @patch("knowledge.sources.github_api.requests.get")
    def test_returns_detail(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"number": 10, "title": "PR", "mergeable": True}
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        detail = get_pr_detail("tok", "owner", "repo", 10)
        assert detail["number"] == 10


class TestListRepoActivity:
    @patch("knowledge.sources.github_api.list_repo_discussions")
    @patch("knowledge.sources.github_api.list_repo_issues")
    def test_unified_activity(self, mock_issues, mock_discussions):
        mock_issues.return_value = [
            {"number": 1, "title": "Bug", "state": "open", "user": {"login": "a"},
             "created_at": "", "updated_at": "", "body": "", "labels": [],
             "html_url": "", "comments": 0},
            {"number": 2, "title": "PR Fix", "state": "open", "user": {"login": "b"},
             "created_at": "", "updated_at": "", "body": "", "labels": [],
             "html_url": "", "comments": 1, "pull_request": {"url": "..."}},
        ]
        mock_discussions.return_value = [
            {"number": 3, "title": "Q", "body": "", "url": "",
             "createdAt": "", "updatedAt": "", "author": {"login": "c"},
             "category": {"name": "Q&A"},
             "comments": {"nodes": []}},
        ]

        items = list_repo_activity("tok", "owner", "repo")
        assert len(items) == 3
        kinds = [i["kind"] for i in items]
        assert "issue" in kinds
        assert "pull_request" in kinds
        assert "discussion" in kinds

    @patch("knowledge.sources.github_api.list_repo_discussions", side_effect=Exception("no discussions"))
    @patch("knowledge.sources.github_api.list_repo_issues")
    def test_graceful_discussion_failure(self, mock_issues, mock_disc):
        mock_issues.return_value = [
            {"number": 1, "title": "Bug", "state": "open", "user": {"login": "a"},
             "created_at": "", "updated_at": "", "body": "", "labels": [],
             "html_url": "", "comments": 0},
        ]
        items = list_repo_activity("tok", "owner", "repo")
        assert len(items) == 1

    @patch("knowledge.sources.github_api.list_repo_discussions")
    @patch("knowledge.sources.github_api.list_repo_issues")
    def test_skips_discussions_when_disabled(self, mock_issues, mock_discussions):
        mock_issues.return_value = []
        items = list_repo_activity("tok", "owner", "repo", include_discussions=False)
        assert items == []
        mock_discussions.assert_not_called()


class TestRenderIssueThread:
    @patch("knowledge.sources.github_api.get_issue_comments")
    def test_render_issue(self, mock_comments):
        mock_comments.return_value = [
            {"body": "Looks good", "user": {"login": "bob"}, "created_at": "2026-01-01"},
        ]
        item = {
            "kind": "issue", "number": 42, "title": "A Bug",
            "body": "Steps to reproduce...", "user": "alice",
            "created_at": "2026-01-01", "state": "open",
            "labels": ["bug"], "url": "https://github.com/x/y/issues/42",
        }
        md = render_issue_thread_markdown("tok", "owner", "repo", item)
        assert "A Bug" in md
        assert "#42" in md
        assert "Steps to reproduce" in md
        assert "Looks good" in md
        assert "@bob" in md

    def test_render_discussion(self):
        item = {
            "kind": "discussion", "number": 5, "title": "Question",
            "body": "How do I...", "user": "carol",
            "created_at": "2026-01-01", "state": "open",
            "labels": [], "url": "https://github.com/x/y/discussions/5",
            "_discussion_comments": [
                {"body": "Answer here", "author": {"login": "dave"}, "createdAt": "2026-01-02"},
            ],
        }
        md = render_issue_thread_markdown("tok", "owner", "repo", item)
        assert "Discussion #5" in md
        assert "Answer here" in md
        assert "@dave" in md

    @patch("knowledge.sources.github_api.get_issue_comments", side_effect=Exception("fail"))
    def test_render_with_comment_failure(self, mock_comments):
        item = {
            "kind": "issue", "number": 1, "title": "Bug",
            "body": "Desc", "user": "u", "created_at": "",
            "state": "open", "labels": [], "url": "",
        }
        md = render_issue_thread_markdown("tok", "o", "r", item)
        assert "Could not load comments" in md
