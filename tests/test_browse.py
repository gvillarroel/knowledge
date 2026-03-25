"""Tests for ``know browse`` commands and their television formatters."""

from __future__ import annotations

import json
import re
from argparse import Namespace
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from knowledge.browse_commands import (
    cmd_browse_aha,
    cmd_browse_arxiv,
    cmd_browse_confluence,
    cmd_browse_github,
    cmd_browse_github_activity,
    cmd_browse_jira,
    cmd_browse_local,
    cmd_browse_releases,
    cmd_browse_sites,
    cmd_browse_videos,
    _extract_frontmatter_field,
    _parse_owner_repo,
    _repo_name_from_url,
    _strip_yaml_frontmatter,
)
from knowledge.browse_tv import (
    _strip_ansi,
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
from knowledge.store import KnowledgeStore


# ── Helper ───────────────────────────────────────────────────────────────

def _make_args(**kwargs) -> Namespace:
    defaults = {"store": None, "json": False, "verbose": False, "quiet": False}
    defaults.update(kwargs)
    return Namespace(**defaults)


def _clean(text: str) -> str:
    """Strip ANSI codes for easier assertion."""
    return re.sub(r"\033\[[0-9;]*m", "", text)


# ── browse_tv formatters ────────────────────────────────────────────────

class TestJiraBrowseFormatters:
    def test_television_synced(self):
        issues = [
            {"key": "PROJ-1", "summary": "First", "status": "Done", "synced": True},
            {"key": "PROJ-2", "summary": "Second", "status": "Open", "synced": False},
        ]
        out = format_jira_browse_television(issues)
        clean = _clean(out)
        assert "● PROJ-1" in clean
        assert "○ PROJ-2" in clean
        assert "First" in clean
        assert "Second" in clean

    def test_television_empty(self):
        assert format_jira_browse_television([]) == ""

    def test_preview_synced(self):
        issues = [{"key": "X-1", "summary": "Bug", "synced": True, "status": "Done"}]
        out = format_jira_browse_preview(issues, None)
        assert "✅ Yes" in out
        assert "X-1" in out

    def test_preview_not_synced(self):
        issues = [{"key": "X-2", "summary": "Task", "synced": False, "status": "Open"}]
        out = format_jira_browse_preview(issues, None)
        assert "❌ No" in out

    def test_preview_no_match(self):
        out = format_jira_browse_preview([], "something")
        assert "No issue" in out

    def test_preview_select_by_key(self):
        issues = [
            {"key": "A-1", "summary": "First", "synced": True},
            {"key": "A-2", "summary": "Second", "synced": False},
        ]
        out = format_jira_browse_preview(issues, "○ A-2 | Second | Open")
        assert "A-2" in out


class TestConfluenceBrowseFormatters:
    def test_television_output(self):
        pages = [
            {"title": "Page One", "space": "DEV", "synced": True},
            {"title": "Page Two", "space": "DEV", "synced": False},
        ]
        out = format_confluence_browse_television(pages)
        clean = _clean(out)
        assert "●" in clean
        assert "○" in clean
        assert "Page One" in clean

    def test_preview(self):
        pages = [{"title": "Page", "space": "SP", "synced": True, "body": "Content here"}]
        out = format_confluence_browse_preview(pages, None)
        assert "Page" in out
        assert "Content here" in out


class TestGitHubBrowseFormatters:
    def test_repos_television(self):
        repos = [
            {"full_name": "user/repo1", "description": "A test repo", "language": "Python",
             "stargazers_count": 5, "synced": True},
            {"full_name": "user/repo2", "description": "Another", "language": "Go",
             "stargazers_count": 0, "synced": False},
        ]
        out = format_github_repos_television(repos)
        clean = _clean(out)
        assert "user/repo1" in clean
        assert "user/repo2" in clean
        assert "●" in clean
        assert "○" in clean

    def test_repos_preview(self):
        repos = [{"full_name": "user/repo", "description": "Test", "language": "Rust",
                  "stargazers_count": 10, "forks_count": 2, "open_issues_count": 3,
                  "html_url": "https://github.com/user/repo", "synced": True,
                  "updated_at": "2026-01-01"}]
        out = format_github_repos_preview(repos, None)
        assert "user/repo" in out
        assert "✅ Yes" in out

    def test_activity_television(self):
        items = [
            {"kind": "issue", "number": 1, "title": "Bug", "user": "alice",
             "comments_count": 3, "labels": ["bug"]},
            {"kind": "pull_request", "number": 2, "title": "Fix", "user": "bob",
             "comments_count": 1, "labels": []},
            {"kind": "discussion", "number": 3, "title": "Q&A", "user": "carol",
             "comments_count": 0, "labels": []},
        ]
        out = format_github_activity_television(items)
        clean = _clean(out)
        assert "#1" in clean
        assert "#2" in clean
        assert "#3" in clean
        assert "Bug" in clean

    def test_activity_preview_with_thread(self):
        items = [{"kind": "issue", "number": 1, "title": "Bug"}]
        out = format_github_activity_preview(items, None, thread_md="# Full thread\nDetails")
        assert "Full thread" in out

    def test_activity_preview_without_thread(self):
        items = [{"kind": "issue", "number": 1, "title": "Bug", "state": "open",
                  "user": "alice", "created_at": "2026-01-01", "comments_count": 0,
                  "labels": ["bug"], "url": "https://github.com/x/y/issues/1",
                  "body": "Description text"}]
        out = format_github_activity_preview(items, None)
        assert "Bug" in out
        assert "Description text" in out


class TestArxivBrowseFormatters:
    def test_television(self):
        papers = [{"title": "Paper A", "primary_category": "cs.AI", "synced": True}]
        out = format_arxiv_browse_television(papers)
        clean = _clean(out)
        assert "Paper A" in clean
        assert "●" in clean

    def test_preview(self):
        papers = [{"title": "Paper A", "primary_category": "cs.AI", "synced": False,
                   "authors": ["Alice", "Bob"], "published": "2026-01-01",
                   "summary": "An abstract.", "pdf_url": "https://arxiv.org/pdf/123"}]
        out = format_arxiv_browse_preview(papers, None)
        assert "Paper A" in out
        assert "❌ No" in out
        assert "An abstract." in out


class TestAhaBrowseFormatters:
    def test_television(self):
        features = [{"reference_num": "FEAT-1", "name": "Feature X", "status": "In Progress", "synced": True}]
        out = format_aha_browse_television(features)
        clean = _clean(out)
        assert "FEAT-1" in clean

    def test_preview(self):
        features = [{"reference_num": "FEAT-1", "name": "Feature X", "synced": False}]
        out = format_aha_browse_preview(features, None)
        assert "❌ No" in out


class TestReleasesBrowseFormatters:
    def test_television(self):
        entries = [{"title": "Release v1", "updated": "2026-01-01", "products": ["GKE"], "synced": True}]
        out = format_releases_browse_television(entries)
        clean = _clean(out)
        assert "Release v1" in clean

    def test_preview(self):
        entries = [{"title": "Release v1", "updated": "2026-01-01", "products": ["GKE"], "synced": True}]
        out = format_releases_browse_preview(entries, None)
        assert "Release v1" in out


class TestVideosBrowseFormatters:
    def test_television(self):
        videos = [{"title": "Video A", "synced": True}]
        out = format_videos_browse_television(videos)
        clean = _clean(out)
        assert "Video A" in clean

    def test_preview(self):
        videos = [{"title": "Video A", "synced": True, "url": "https://youtube.com/watch?v=x"}]
        out = format_videos_browse_preview(videos, None)
        assert "Video A" in out


class TestSitesBrowseFormatters:
    def test_television(self):
        sites = [{"title": "Example", "url": "https://example.com", "synced": True}]
        out = format_sites_browse_television(sites)
        clean = _clean(out)
        assert "Example" in clean

    def test_preview(self):
        sites = [{"title": "Example", "url": "https://example.com", "synced": True}]
        out = format_sites_browse_preview(sites, None)
        assert "Example" in out


class TestLocalBrowseFormatters:
    def test_television(self):
        items = [{"title": "Doc", "source_type": "jira", "key": "mykey"}]
        out = format_local_browse_television(items)
        clean = _clean(out)
        assert "[jira]" in clean
        assert "Doc" in clean

    def test_preview(self):
        items = [{"title": "Doc", "source_type": "jira", "key": "k", "path": "/a/b.md", "body": "Body text"}]
        out = format_local_browse_preview(items, None)
        assert "Body text" in out


# ── Helpers ──────────────────────────────────────────────────────────────

class TestHelpers:
    def test_strip_ansi(self):
        assert _strip_ansi("\033[32mhello\033[0m") == "hello"

    def test_repo_name_from_url(self):
        assert _repo_name_from_url("https://github.com/owner/repo.git") == "owner/repo"
        assert _repo_name_from_url("https://github.com/owner/repo") == "owner/repo"
        assert _repo_name_from_url("not-a-url") is None

    def test_parse_owner_repo(self):
        assert _parse_owner_repo("owner/repo") == ("owner", "repo")
        assert _parse_owner_repo("https://github.com/owner/repo") == ("owner", "repo")
        assert _parse_owner_repo("invalid") == ("", "")

    def test_strip_yaml_frontmatter(self):
        text = "---\ntitle: Hello\n---\n\nBody content"
        assert "Body content" in _strip_yaml_frontmatter(text)
        assert "title" not in _strip_yaml_frontmatter(text)

    def test_strip_yaml_frontmatter_no_frontmatter(self):
        text = "Just plain text"
        assert _strip_yaml_frontmatter(text) == text

    def test_extract_frontmatter_field(self):
        text = "---\ntitle: My Title\nauthor: Alice\n---\nBody"
        assert _extract_frontmatter_field(text, "title") == "My Title"
        assert _extract_frontmatter_field(text, "author") == "Alice"
        assert _extract_frontmatter_field(text, "missing") is None

    def test_extract_frontmatter_field_no_frontmatter(self):
        assert _extract_frontmatter_field("No frontmatter", "title") is None


# ── Browse commands (mocked store) ──────────────────────────────────────

@pytest.fixture
def tmp_store(tmp_path):
    store = KnowledgeStore(tmp_path)
    store.initialize()
    return store


class TestBrowseJiraCommand:
    def test_json_format_empty(self, tmp_store):
        args = _make_args(store=tmp_store.root, format="json", key=None, entry=None)
        result = cmd_browse_jira(args)
        assert isinstance(result, dict)
        assert "issues" in result

    def test_television_format_empty(self, tmp_store):
        args = _make_args(store=tmp_store.root, format="television", key=None, entry=None)
        result = cmd_browse_jira(args)
        assert isinstance(result, str)

    def test_television_preview_empty(self, tmp_store):
        args = _make_args(store=tmp_store.root, format="television-preview", key=None, entry=None)
        result = cmd_browse_jira(args)
        assert isinstance(result, str)


class TestBrowseConfluenceCommand:
    def test_json_format_empty(self, tmp_store):
        args = _make_args(store=tmp_store.root, format="json", key=None, entry=None)
        result = cmd_browse_confluence(args)
        assert isinstance(result, dict)
        assert "pages" in result


class TestBrowseGitHubCommand:
    def test_json_format_no_token(self, tmp_store):
        with patch.dict("os.environ", {}, clear=False):
            # Remove GITHUB_TOKEN if present
            import os
            old = os.environ.pop("GITHUB_TOKEN", None)
            try:
                args = _make_args(store=tmp_store.root, format="json", key=None, entry=None)
                result = cmd_browse_github(args)
                assert isinstance(result, dict)
                assert "repos" in result
            finally:
                if old:
                    os.environ["GITHUB_TOKEN"] = old

    def test_television_format_no_token(self, tmp_store):
        import os
        old = os.environ.pop("GITHUB_TOKEN", None)
        try:
            args = _make_args(store=tmp_store.root, format="television", key=None, entry=None)
            result = cmd_browse_github(args)
            assert isinstance(result, str)
        finally:
            if old:
                os.environ["GITHUB_TOKEN"] = old


class TestBrowseGitHubActivityCommand:
    def test_invalid_repo(self, tmp_store):
        args = _make_args(store=tmp_store.root, format="json", repo="invalid", entry=None)
        result = cmd_browse_github_activity(args)
        assert "Invalid repo" in str(result)

    def test_no_token(self, tmp_store):
        import os
        old = os.environ.pop("GITHUB_TOKEN", None)
        try:
            args = _make_args(store=tmp_store.root, format="json", repo="owner/repo", entry=None)
            result = cmd_browse_github_activity(args)
            assert "token" in str(result).lower()
        finally:
            if old:
                os.environ["GITHUB_TOKEN"] = old


class TestBrowseArxivCommand:
    def test_json_format_empty(self, tmp_store):
        args = _make_args(store=tmp_store.root, format="json", key=None, entry=None)
        result = cmd_browse_arxiv(args)
        assert isinstance(result, dict)
        assert "papers" in result


class TestBrowseAhaCommand:
    def test_json_format_empty(self, tmp_store):
        args = _make_args(store=tmp_store.root, format="json", key=None, entry=None)
        result = cmd_browse_aha(args)
        assert isinstance(result, dict)
        assert "features" in result


class TestBrowseReleasesCommand:
    def test_json_format_empty(self, tmp_store):
        args = _make_args(store=tmp_store.root, format="json", key=None, entry=None)
        result = cmd_browse_releases(args)
        assert isinstance(result, dict)
        assert "entries" in result


class TestBrowseVideosCommand:
    def test_json_format_empty(self, tmp_store):
        args = _make_args(store=tmp_store.root, format="json", key=None, entry=None)
        result = cmd_browse_videos(args)
        assert isinstance(result, dict)
        assert "videos" in result


class TestBrowseSitesCommand:
    def test_json_format_empty(self, tmp_store):
        args = _make_args(store=tmp_store.root, format="json", key=None, entry=None)
        result = cmd_browse_sites(args)
        assert isinstance(result, dict)
        assert "sites" in result


class TestBrowseLocalCommand:
    def test_json_format_empty(self, tmp_store):
        args = _make_args(store=tmp_store.root, format="json", key=None, entry=None, type=None)
        result = cmd_browse_local(args)
        assert isinstance(result, dict)
        assert "items" in result

    def test_with_local_files(self, tmp_store):
        # Create a key with a source and a local file
        tmp_store.create_collection_key("test-key")
        tmp_store.add_collection_source(
            key_name="test-key",
            source_type="jira",
            title="PROJ",
            config={"project": "PROJ", "jql": "project=PROJ", "base_url": "https://jira.example.com"},
            update_command="know sync jira-project PROJ --key test-key",
            delete_command="know del --key test-key jira-proj",
        )
        # Write a markdown file
        source_dir = tmp_store.root / "test-key" / "jira" / "jira-proj"
        source_dir.mkdir(parents=True, exist_ok=True)
        md = source_dir / "PROJ-1.md"
        md.write_text("---\ntitle: Test Issue\n---\n\n# Test Issue\nBody here", encoding="utf-8")

        args = _make_args(store=tmp_store.root, format="television", key=None, entry=None, type=None)
        result = cmd_browse_local(args)
        assert isinstance(result, str)
        clean = _clean(result)
        assert "Test Issue" in clean

    def test_preview_with_local_files(self, tmp_store):
        tmp_store.create_collection_key("pkey")
        tmp_store.add_collection_source(
            key_name="pkey",
            source_type="jira",
            title="P",
            config={"project": "P", "jql": "project=P", "base_url": "https://jira.example.com"},
            update_command="know sync jira-project P --key pkey",
            delete_command="know del --key pkey jira-p",
        )
        source_dir = tmp_store.root / "pkey" / "jira" / "jira-p"
        source_dir.mkdir(parents=True, exist_ok=True)
        md = source_dir / "P-1.md"
        md.write_text("---\ntitle: My Issue\n---\n\n# My Issue\nBody content", encoding="utf-8")

        args = _make_args(store=tmp_store.root, format="television-preview", key=None, entry=None, type=None)
        result = cmd_browse_local(args)
        assert isinstance(result, str)
        assert "Body content" in result


class TestBrowseJiraWithSources:
    def test_local_only_jira(self, tmp_store):
        tmp_store.create_collection_key("jk")
        tmp_store.add_collection_source(
            key_name="jk",
            source_type="jira",
            title="JP",
            config={"project": "JP", "jql": "project=JP"},
            update_command="know sync jira-project JP --key jk",
            delete_command="know del --key jk jira-jp",
        )
        source_dir = tmp_store.root / "jk" / "jira" / "jira-jp"
        source_dir.mkdir(parents=True, exist_ok=True)
        (source_dir / "JP-1.md").write_text("---\ntitle: Issue 1\n---\n\nBody", encoding="utf-8")

        args = _make_args(store=tmp_store.root, format="television", key=None, entry=None)
        result = cmd_browse_jira(args)
        assert isinstance(result, str)
        clean = _clean(result)
        assert "JP-1" in clean
        assert "●" in clean  # synced marker


# ── CLI integration ─────────────────────────────────────────────────────

class TestCLIBrowseIntegration:
    def test_browse_help(self):
        from knowledge.cli import build_parser
        parser = build_parser()
        # Verify browse subcommands are registered
        with pytest.raises(SystemExit):
            parser.parse_args(["browse", "--help"])

    def test_browse_jira_parse(self):
        from knowledge.cli import build_parser
        parser = build_parser()
        args = parser.parse_args(["browse", "jira", "--format", "television"])
        assert args.format == "television"
        assert args.handler == cmd_browse_jira

    def test_browse_github_parse(self):
        from knowledge.cli import build_parser
        parser = build_parser()
        args = parser.parse_args(["browse", "github", "--format", "television"])
        assert args.handler == cmd_browse_github

    def test_browse_github_activity_parse(self):
        from knowledge.cli import build_parser
        parser = build_parser()
        args = parser.parse_args(["browse", "github-activity", "owner/repo", "--format", "television-preview"])
        assert args.repo == "owner/repo"
        assert args.format == "television-preview"

    def test_browse_local_parse(self):
        from knowledge.cli import build_parser
        parser = build_parser()
        args = parser.parse_args(["browse", "local", "--key", "k", "--type", "jira", "--format", "television"])
        assert args.key == "k"
        assert args.type == "jira"
