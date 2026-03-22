"""Tests for source classes (using mocks to avoid real network calls)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch, AsyncMock

import pytest

from knowledge.sources.base import BaseSource
from knowledge.sources import web, confluence, jira, aha, github


# ---------------------------------------------------------------------------
# BaseSource registry
# ---------------------------------------------------------------------------


def test_base_registry_contains_all_types():
    assert "web" in BaseSource._registry
    assert "confluence" in BaseSource._registry
    assert "jira" in BaseSource._registry
    assert "aha" in BaseSource._registry
    assert "github" in BaseSource._registry


def test_from_entry_web():
    entry = {"key": "test", "type": "web", "url": "https://example.com"}
    src = BaseSource.from_entry(entry)
    assert isinstance(src, web.WebSource)
    assert src.url == "https://example.com"


def test_from_entry_unknown_type():
    with pytest.raises(ValueError, match="Unknown source type"):
        BaseSource.from_entry({"key": "k", "type": "unknown"})


def test_to_store_entry():
    src = web.WebSource("mykey", {"url": "https://x.com", "max_pages": 10})
    entry = src.to_store_entry()
    assert entry["key"] == "mykey"
    assert entry["type"] == "web"
    assert entry["url"] == "https://x.com"


# ---------------------------------------------------------------------------
# WebSource
# ---------------------------------------------------------------------------


def test_web_source_missing_crawl4ai(tmp_path):
    """When crawl4ai is not importable, fetch() should raise RuntimeError."""
    src = web.WebSource("test", {"url": "https://example.com"})
    with patch.dict("sys.modules", {"crawl4ai": None}):
        with pytest.raises((RuntimeError, ImportError)):
            src.fetch(tmp_path)


# ---------------------------------------------------------------------------
# ConfluenceSource
# ---------------------------------------------------------------------------


def test_confluence_source_fetch(tmp_path):
    src = confluence.ConfluenceSource(
        "cf",
        {
            "url": "https://myco.atlassian.net/wiki",
            "username": "user@example.com",
            "token": "secret",
            "space": "DOCS",
        },
    )

    mock_page = {
        "id": "12345",
        "title": "My Page",
        "body": {"storage": {"value": "<p>Content here.</p>"}},
        "ancestors": [],
    }

    mock_client = MagicMock()
    mock_client.get_all_pages_from_space.side_effect = [[mock_page], []]

    with patch("atlassian.Confluence", return_value=mock_client):
        paths = src.fetch(tmp_path)

    assert len(paths) == 1
    content = paths[0].read_text()
    assert "My Page" in content
    assert "Content here" in content


# ---------------------------------------------------------------------------
# JiraSource
# ---------------------------------------------------------------------------


def test_jira_source_fetch(tmp_path):
    src = jira.JiraSource(
        "jira-proj",
        {
            "url": "https://myco.atlassian.net",
            "username": "user@example.com",
            "token": "secret",
            "project": "PROJ",
        },
    )

    mock_issue = {
        "key": "PROJ-1",
        "fields": {
            "summary": "Fix the bug",
            "description": "<p>Details about the bug.</p>",
            "status": {"name": "Open"},
            "issuetype": {"name": "Bug"},
            "labels": [],
        },
    }

    mock_client = MagicMock()
    mock_client.jql.side_effect = [
        {"issues": [mock_issue]},
        {"issues": []},
    ]

    with patch("atlassian.Jira", return_value=mock_client):
        paths = src.fetch(tmp_path)

    assert len(paths) == 1
    content = paths[0].read_text()
    assert "PROJ-1" in content


# ---------------------------------------------------------------------------
# AhaSource
# ---------------------------------------------------------------------------


def test_aha_source_fetch(tmp_path):
    src = aha.AhaSource(
        "aha-prod",
        {
            "subdomain": "myco",
            "token": "secret",
            "product_id": "PROD",
        },
    )

    mock_item = {
        "reference_num": "PROD-1",
        "name": "New Feature",
        "description": {"body": "<p>Feature description.</p>"},
        "url": "https://myco.aha.io/features/PROD-1",
        "workflow_status": {"name": "Under consideration"},
    }

    mock_response = MagicMock()
    mock_response.json.return_value = {"features": [mock_item]}
    mock_response.raise_for_status = MagicMock()

    mock_client = MagicMock()
    mock_client.get.side_effect = [mock_response, MagicMock(json=lambda: {"features": []}, raise_for_status=MagicMock())]
    mock_client.__enter__ = lambda s: s
    mock_client.__exit__ = MagicMock(return_value=False)

    with patch("knowledge.sources.aha.httpx.Client", return_value=mock_client):
        paths = src.fetch(tmp_path)

    assert len(paths) == 1
    content = paths[0].read_text()
    assert "PROD-1" in content


# ---------------------------------------------------------------------------
# GitHubSource
# ---------------------------------------------------------------------------


def _make_mock_repo(tmp_path: Path, branch: str = "main") -> MagicMock:
    # Create a fake repo directory with a README
    (tmp_path / "README.md").write_text("# Hello\n\nThis is a readme.", encoding="utf-8")
    (tmp_path / "main.py").write_text('print("hello")\n', encoding="utf-8")

    mock_ref = MagicMock()
    mock_ref.remote_head = branch
    mock_remote = MagicMock()
    mock_remote.refs = [mock_ref]
    mock_remote.__getitem__ = lambda s, k: mock_remote

    mock_repo = MagicMock()
    mock_repo.remotes = {"origin": mock_remote}
    mock_repo.git = MagicMock()
    return mock_repo


def test_github_source_fetch(tmp_path):
    src = github.GitHubSource(
        "myrepo",
        {"url": "https://github.com/org/repo", "branches": ["main"]},
    )

    repo_dir = tmp_path / "fake_repo"
    repo_dir.mkdir()
    (repo_dir / "README.md").write_text("# Title\n\nContent.", encoding="utf-8")
    (repo_dir / "app.py").write_text('x = 1\n', encoding="utf-8")

    mock_repo = _make_mock_repo(repo_dir)

    import tempfile

    def fake_clone(url, dest, **kwargs):
        import shutil
        shutil.copytree(str(repo_dir), dest)
        return mock_repo

    with patch("git.Repo.clone_from", side_effect=fake_clone):
        with patch("tempfile.TemporaryDirectory") as mock_td:
            real_tmpdir = tmp_path / "work"
            real_tmpdir.mkdir()
            mock_td.return_value.__enter__ = lambda s: str(real_tmpdir)
            mock_td.return_value.__exit__ = MagicMock(return_value=False)
            paths = src.fetch(tmp_path / "out")

    assert any(p.suffix == ".md" for p in paths)
