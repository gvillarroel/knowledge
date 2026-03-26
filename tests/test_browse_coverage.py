"""Additional tests for ``browse_commands`` and ``browse_extended`` to raise coverage."""

from __future__ import annotations

import re
from argparse import Namespace
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from knowledge.browse_commands import (
    _add_local_confluence,
    _add_local_jira_issues,
    _config_value_or_env,
    _confluence_webui,
    _display_name,
    _field_name,
    _find_activity_item,
    _strip_yaml_frontmatter,
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
)
from knowledge.browse_extended import (
    _build_sync_cmd,
    _extract_fm,
    cmd_browse_by_key,
    cmd_browse_by_type,
    cmd_browse_commands,
    cmd_browse_crossref,
    cmd_browse_files,
    cmd_browse_key_sources,
    cmd_browse_papers,
    cmd_browse_recent,
    cmd_browse_repo_files,
    cmd_browse_repos,
    cmd_browse_source_files,
    cmd_browse_stale,
    cmd_browse_stats,
    cmd_browse_timeline,
    cmd_browse_unsynced,
)
from knowledge.store import KnowledgeStore


def _clean(text: str) -> str:
    return re.sub(r"\033\[[0-9;]*m", "", text)


def _args(**kwargs) -> Namespace:
    defaults = {"store": None, "json": False, "verbose": False, "quiet": False}
    defaults.update(kwargs)
    return Namespace(**defaults)


# ── browse_commands helpers ──────────────────────────────────────────────


class TestFieldName:
    def test_dict_with_name(self):
        assert _field_name({"name": "Bug"}) == "Bug"

    def test_dict_without_name(self):
        assert _field_name({}) == "unknown"

    def test_none(self):
        assert _field_name(None) == "unknown"

    def test_string(self):
        assert _field_name("plain") == "unknown"


class TestDisplayName:
    def test_display_name(self):
        assert _display_name({"displayName": "Alice"}) == "Alice"

    def test_email(self):
        assert _display_name({"emailAddress": "a@b.com"}) == "a@b.com"

    def test_account_id(self):
        assert _display_name({"accountId": "abc123"}) == "abc123"

    def test_empty_dict(self):
        assert _display_name({}) == "unassigned"

    def test_none(self):
        assert _display_name(None) == "unassigned"


class TestConfluenceWebui:
    def test_with_webui(self):
        content = {"_links": {"webui": "/pages/123"}}
        assert _confluence_webui("https://wiki.example.com", content) == "https://wiki.example.com/pages/123"

    def test_trailing_slash(self):
        content = {"_links": {"webui": "/pages/456"}}
        assert _confluence_webui("https://wiki.example.com/", content) == "https://wiki.example.com/pages/456"

    def test_no_links(self):
        assert _confluence_webui("https://wiki.example.com", {}) == ""

    def test_no_webui(self):
        assert _confluence_webui("https://wiki.example.com", {"_links": {}}) == ""


class TestConfigValueOrEnv:
    def test_explicit_value(self):
        assert _config_value_or_env("my-val", "MY_ENV") == "my-val"

    def test_env_value(self):
        with patch.dict("os.environ", {"MY_ENV": "from-env"}):
            assert _config_value_or_env(None, "MY_ENV") == "$env:MY_ENV"

    def test_no_value(self):
        import os
        old = os.environ.pop("XYZZY_NOT_SET", None)
        try:
            assert _config_value_or_env(None, "XYZZY_NOT_SET") is None
        finally:
            if old:
                os.environ["XYZZY_NOT_SET"] = old


class TestFindActivityItem:
    def test_empty(self):
        assert _find_activity_item([], None) is None

    def test_no_selected(self):
        items = [{"number": 1}, {"number": 2}]
        assert _find_activity_item(items, None) == items[0]

    def test_match_by_number(self):
        items = [{"number": 1}, {"number": 42}]
        assert _find_activity_item(items, "Issue #42 title") == items[1]

    def test_no_match_fallback(self):
        items = [{"number": 1}]
        assert _find_activity_item(items, "no hash here") == items[0]


class TestAddLocalJiraIssues:
    def test_adds_issues(self):
        store = MagicMock()
        source = {"id": "s1", "key": "k1", "config": {"project": "PROJ"}}
        issues: list = []
        _add_local_jira_issues(store, source, issues, {"PROJ-1", "PROJ-2"})
        assert len(issues) == 2
        keys = {i["key"] for i in issues}
        assert "PROJ-1" in keys
        assert "PROJ-2" in keys
        assert issues[0]["synced"] is True


class TestAddLocalConfluence:
    def test_adds_pages(self):
        source = {"config": {"space": "DEV"}}
        pages: list = []
        _add_local_confluence({"Page A", "Page B"}, {"Page A": "body a", "Page B": "body b"}, source, pages)
        assert len(pages) == 2
        titles = {p["title"] for p in pages}
        assert "Page A" in titles
        assert pages[0]["synced"] is True


class TestStripYamlFrontmatter:
    def test_no_end(self):
        assert _strip_yaml_frontmatter("---\ntitle: x\nno end") == "---\ntitle: x\nno end"


# ── browse_commands with populated data ──────────────────────────────────


def _add_src(store, key, stype, title, config=None, update_cmd="x", delete_cmd="y"):
    """Add source and return its actual source_dir path."""
    store.add_collection_source(
        key_name=key, source_type=stype, title=title,
        config=config or {},
        update_command=update_cmd, delete_command=delete_cmd,
    )
    sources = store.list_collection_sources(key_name=key, source_type=stype)
    src = [s for s in sources if s.get("title") == title][0]
    d = store.source_dir(src)
    d.mkdir(parents=True, exist_ok=True)
    return d, src


@pytest.fixture
def rich_store(tmp_path):
    s = KnowledgeStore(tmp_path)
    s.initialize()
    s.create_collection_key("demo")

    # Jira
    jira_dir, _ = _add_src(s, "demo", "jira", "DEMO",
        config={"project": "DEMO", "jql": "project=DEMO"},
        update_cmd="know sync jira-project DEMO --key demo",
        delete_cmd="know del --key demo jira-demo")
    (jira_dir / "DEMO-1.md").write_text("---\ntitle: Issue One\n---\nJira body", encoding="utf-8")

    # Confluence
    conf_dir, _ = _add_src(s, "demo", "confluence", "My Space",
        config={"space": "MS", "base_url": "https://wiki.example.com"},
        update_cmd="know sync confluence MS --key demo",
        delete_cmd="know del --key demo confluence-ms")
    (conf_dir / "page1.md").write_text("---\ntitle: Page One\n---\nConfluence body", encoding="utf-8")

    # ArXiv
    arxiv_dir, _ = _add_src(s, "demo", "arxiv", "Paper X",
        config={"url": "https://arxiv.org/abs/2401.12345"},
        update_cmd="know sync arxiv https://arxiv.org/abs/2401.12345 --key demo",
        delete_cmd="know del --key demo arxiv-paper-x")
    (arxiv_dir / "paper.md").write_text("---\ntitle: Paper X\n---\nAbstract text", encoding="utf-8")

    # Aha
    aha_dir, _ = _add_src(s, "demo", "aha", "FEAT-1",
        update_cmd="know sync aha --key demo",
        delete_cmd="know del --key demo aha-feat-1")
    (aha_dir / "feat.json").write_text("{}", encoding="utf-8")

    # Releases
    rel_dir, _ = _add_src(s, "demo", "google_releases", "GCP Releases",
        update_cmd="know sync google-releases --key demo",
        delete_cmd="know del --key demo google_releases-gcp-releases")
    entries_dir = rel_dir / "entries"
    entries_dir.mkdir(parents=True, exist_ok=True)
    (entries_dir / "release1.md").write_text(
        "---\ntitle: GKE Update\nentry_updated: 2026-03-01\nentry_url: https://example.com/rel\n---\nRelease body",
        encoding="utf-8")

    # Video
    vid_dir, _ = _add_src(s, "demo", "video", "My Video",
        config={"url": "https://youtube.com/watch?v=abc"},
        update_cmd="know sync video https://youtube.com/watch?v=abc --key demo",
        delete_cmd="know del --key demo video-my-video")
    (vid_dir / "transcript.md").write_text("---\ntitle: My Video\n---\nTranscript text", encoding="utf-8")

    # Site
    site_dir, _ = _add_src(s, "demo", "site", "Example Site",
        config={"url": "https://example.com"},
        update_cmd="know sync site https://example.com --key demo",
        delete_cmd="know del --key demo site-example-site")
    (site_dir / "index.md").write_text("---\ntitle: Example Site\n---\nSite content here", encoding="utf-8")

    # GitHub
    gh_dir, _ = _add_src(s, "demo", "github", "owner/myrepo",
        config={"repo_url": "https://github.com/owner/myrepo", "branches": ["main"]},
        update_cmd="know sync github-repo https://github.com/owner/myrepo --key demo --branch main",
        delete_cmd="know del --key demo github-owner-myrepo")
    (gh_dir / "README.md").write_text("---\ntitle: README\n---\n# Repo Readme", encoding="utf-8")
    (gh_dir / "main.py").write_text("print('hello')", encoding="utf-8")

    return s


class TestBrowseJiraPopulated:
    def test_television_with_local(self, rich_store):
        args = _args(store=rich_store.root, format="television", key=None, entry=None)
        result = cmd_browse_jira(args)
        clean = _clean(result)
        assert "DEMO-1" in clean

    def test_preview_with_local(self, rich_store):
        args = _args(store=rich_store.root, format="television-preview", key=None, entry="DEMO-1")
        result = cmd_browse_jira(args)
        assert "DEMO-1" in result


class TestBrowseConfluencePopulated:
    def test_television_local(self, rich_store):
        args = _args(store=rich_store.root, format="television", key=None, entry=None)
        result = cmd_browse_confluence(args)
        clean = _clean(result)
        assert "Page One" in clean

    def test_preview_local(self, rich_store):
        args = _args(store=rich_store.root, format="television-preview", key=None, entry="Page One")
        result = cmd_browse_confluence(args)
        assert "Page One" in result

    def test_json_local(self, rich_store):
        args = _args(store=rich_store.root, format="json", key=None, entry=None)
        result = cmd_browse_confluence(args)
        assert len(result["pages"]) >= 1
        assert result["pages"][0]["synced"] is True


class TestBrowseArxivPopulated:
    def test_television(self, rich_store):
        args = _args(store=rich_store.root, format="television", key=None, entry=None)
        result = cmd_browse_arxiv(args)
        clean = _clean(result)
        assert "Paper X" in clean

    def test_preview(self, rich_store):
        args = _args(store=rich_store.root, format="television-preview", key=None, entry="Paper X")
        result = cmd_browse_arxiv(args)
        assert "Paper X" in result

    def test_json(self, rich_store):
        args = _args(store=rich_store.root, format="json", key=None, entry=None)
        result = cmd_browse_arxiv(args)
        assert len(result["papers"]) >= 1
        assert result["papers"][0]["synced"] is True


class TestBrowseAhaPopulated:
    def test_television(self, rich_store):
        args = _args(store=rich_store.root, format="television", key=None, entry=None)
        result = cmd_browse_aha(args)
        clean = _clean(result)
        assert "FEAT-1" in clean

    def test_preview(self, rich_store):
        args = _args(store=rich_store.root, format="television-preview", key=None, entry="FEAT-1")
        result = cmd_browse_aha(args)
        assert "FEAT-1" in result

    def test_json_synced(self, rich_store):
        args = _args(store=rich_store.root, format="json", key=None, entry=None)
        result = cmd_browse_aha(args)
        assert result["features"][0]["synced"] is True


class TestBrowseReleasesPopulated:
    def test_television(self, rich_store):
        args = _args(store=rich_store.root, format="television", key=None, entry=None)
        result = cmd_browse_releases(args)
        clean = _clean(result)
        assert "GKE Update" in clean

    def test_preview(self, rich_store):
        args = _args(store=rich_store.root, format="television-preview", key=None, entry="GKE Update")
        result = cmd_browse_releases(args)
        assert "Release body" in result

    def test_json(self, rich_store):
        args = _args(store=rich_store.root, format="json", key=None, entry=None)
        result = cmd_browse_releases(args)
        assert len(result["entries"]) >= 1
        assert result["entries"][0]["synced"] is True


class TestBrowseVideosPopulated:
    def test_television(self, rich_store):
        args = _args(store=rich_store.root, format="television", key=None, entry=None)
        result = cmd_browse_videos(args)
        clean = _clean(result)
        assert "My Video" in clean

    def test_preview(self, rich_store):
        args = _args(store=rich_store.root, format="television-preview", key=None, entry="My Video")
        result = cmd_browse_videos(args)
        assert "My Video" in result

    def test_json_synced(self, rich_store):
        args = _args(store=rich_store.root, format="json", key=None, entry=None)
        result = cmd_browse_videos(args)
        assert result["videos"][0]["synced"] is True
        assert "Transcript text" in result["videos"][0]["body"]


class TestBrowseSitesPopulated:
    def test_television(self, rich_store):
        args = _args(store=rich_store.root, format="television", key=None, entry=None)
        result = cmd_browse_sites(args)
        clean = _clean(result)
        assert "Example Site" in clean

    def test_preview(self, rich_store):
        args = _args(store=rich_store.root, format="television-preview", key=None, entry="Example Site")
        result = cmd_browse_sites(args)
        assert "Example Site" in result

    def test_json_synced(self, rich_store):
        args = _args(store=rich_store.root, format="json", key=None, entry=None)
        result = cmd_browse_sites(args)
        assert result["sites"][0]["synced"] is True
        assert "Site content here" in result["sites"][0]["body"]


class TestBrowseLocalPopulated:
    def test_television(self, rich_store):
        args = _args(store=rich_store.root, format="television", key=None, entry=None, type=None)
        result = cmd_browse_local(args)
        clean = _clean(result)
        assert len(clean) > 0

    def test_preview(self, rich_store):
        args = _args(store=rich_store.root, format="television-preview", key=None, entry=None, type=None)
        result = cmd_browse_local(args)
        assert isinstance(result, str)

    def test_filter_by_type(self, rich_store):
        args = _args(store=rich_store.root, format="json", key=None, entry=None, type="video")
        result = cmd_browse_local(args)
        for item in result["items"]:
            assert item["source_type"] == "video"


class TestBrowseGitHubPopulated:
    def test_with_local_sources_no_token(self, rich_store):
        import os
        old = os.environ.pop("GITHUB_TOKEN", None)
        try:
            with patch("subprocess.run", side_effect=FileNotFoundError):
                args = _args(store=rich_store.root, format="json", key=None, entry=None)
                result = cmd_browse_github(args)
                assert len(result["repos"]) >= 1
                assert result["repos"][0]["synced"] is True
                assert "owner/myrepo" in result["repos"][0]["full_name"]
        finally:
            if old:
                os.environ["GITHUB_TOKEN"] = old

    def test_television_local_repos(self, rich_store):
        import os
        old = os.environ.pop("GITHUB_TOKEN", None)
        try:
            with patch("subprocess.run", side_effect=FileNotFoundError):
                args = _args(store=rich_store.root, format="television", key=None, entry=None)
                result = cmd_browse_github(args)
                clean = _clean(result)
                assert "owner/myrepo" in clean
        finally:
            if old:
                os.environ["GITHUB_TOKEN"] = old

    def test_preview_local_repos(self, rich_store):
        import os
        old = os.environ.pop("GITHUB_TOKEN", None)
        try:
            args = _args(store=rich_store.root, format="television-preview", key=None, entry="owner/myrepo")
            result = cmd_browse_github(args)
            assert "owner/myrepo" in result
        finally:
            if old:
                os.environ["GITHUB_TOKEN"] = old


class TestBrowseGitHubActivityWithToken:
    def test_json_with_mock_api(self, rich_store):
        mock_items = [
            {"kind": "issue", "number": 10, "title": "Test issue", "user": "alice",
             "comments_count": 2, "labels": ["bug"]},
        ]
        with patch.dict("os.environ", {"GITHUB_TOKEN": "fake-token"}):
            with patch("knowledge.sources.github_api.list_repo_activity", return_value=mock_items):
                args = _args(store=rich_store.root, format="json", repo="owner/myrepo", entry=None)
                result = cmd_browse_github_activity(args)
                assert result["items"] == mock_items

    def test_television_with_mock(self, rich_store):
        mock_items = [
            {"kind": "issue", "number": 10, "title": "Test", "user": "x",
             "comments_count": 0, "labels": []},
        ]
        with patch.dict("os.environ", {"GITHUB_TOKEN": "fake-token"}):
            with patch("knowledge.sources.github_api.list_repo_activity", return_value=mock_items):
                args = _args(store=rich_store.root, format="television", repo="owner/myrepo", entry=None)
                result = cmd_browse_github_activity(args)
                assert "#10" in _clean(result)

    def test_preview_with_thread(self, rich_store):
        mock_items = [
            {"kind": "issue", "number": 10, "title": "Test", "user": "x",
             "comments_count": 0, "labels": []},
        ]
        with patch.dict("os.environ", {"GITHUB_TOKEN": "fake-token"}):
            with patch("knowledge.sources.github_api.list_repo_activity", return_value=mock_items):
                with patch("knowledge.sources.github_api.render_issue_thread_markdown", return_value="# Thread\nDetails"):
                    args = _args(store=rich_store.root, format="television-preview", repo="owner/myrepo", entry="#10 Test")
                    result = cmd_browse_github_activity(args)
                    assert "Thread" in result


# ── browse_extended with populated data ──────────────────────────────────


class TestExtractFm:
    def test_no_frontmatter(self):
        assert _extract_fm("plain text", "title") == ""

    def test_no_end(self):
        assert _extract_fm("---\ntitle: x", "title") == ""

    def test_field_found(self):
        assert _extract_fm("---\ntitle: Hello\n---\nbody", "title") == "Hello"

    def test_field_not_found(self):
        assert _extract_fm("---\ntitle: Hello\n---\nbody", "author") == ""


class TestBuildSyncCmd:
    def test_basic(self):
        repo = {"repo_url": "https://github.com/a/b", "key": "k1", "branches": ["main"]}
        cmd = _build_sync_cmd(repo)
        assert "know sync github-repo" in cmd
        assert "--branch main" in cmd

    def test_multiple_branches(self):
        repo = {"repo_url": "https://github.com/a/b", "key": "k1", "branches": ["main", "dev"]}
        cmd = _build_sync_cmd(repo)
        assert "--branch main" in cmd
        assert "--branch dev" in cmd


class TestBrowseByTypePreview:
    def test_preview(self, rich_store):
        result = cmd_browse_by_type(_args(store=rich_store.root, format="television-preview", entry="arxiv"))
        assert "arxiv" in result
        assert "Actions" in result

    def test_preview_no_match(self, rich_store):
        result = cmd_browse_by_type(_args(store=rich_store.root, format="television-preview", entry="zzz_nope"))
        assert isinstance(result, str)


class TestBrowseByKeyPreviewNoMatch:
    def test_no_match(self, tmp_path):
        s = KnowledgeStore(tmp_path)
        s.initialize()
        result = cmd_browse_by_key(_args(store=s.root, format="television-preview", entry="nope"))
        assert "No key" in result


class TestBrowseReposPreview:
    def test_preview(self, rich_store):
        result = cmd_browse_repos(_args(store=rich_store.root, format="television-preview", entry="owner/myrepo"))
        assert "owner/myrepo" in result
        assert "Actions" in result

    def test_preview_no_match(self, rich_store):
        result = cmd_browse_repos(_args(store=rich_store.root, format="television-preview", entry="nonexistent"))
        assert isinstance(result, str)


class TestBrowseRepoFilesPopulated:
    def test_json(self, rich_store):
        result = cmd_browse_repo_files(_args(store=rich_store.root, format="json", repo="owner/myrepo", entry=None))
        assert "files" in result
        assert len(result["files"]) == 2
        paths = {f["path"] for f in result["files"]}
        assert "README.md" in paths
        assert "main.py" in paths

    def test_television(self, rich_store):
        result = cmd_browse_repo_files(_args(store=rich_store.root, format="television", repo="owner/myrepo", entry=None))
        clean = _clean(result)
        assert "README.md" in clean
        assert "main.py" in clean

    def test_preview_md_file(self, rich_store):
        result = cmd_browse_repo_files(
            _args(store=rich_store.root, format="television-preview", repo="owner/myrepo", entry="README.md")
        )
        assert "Repo Readme" in result

    def test_preview_non_md_file(self, rich_store):
        result = cmd_browse_repo_files(
            _args(store=rich_store.root, format="television-preview", repo="owner/myrepo", entry="main.py")
        )
        assert "print" in result

    def test_no_repo_filter(self, rich_store):
        result = cmd_browse_repo_files(_args(store=rich_store.root, format="json", repo=None, entry=None))
        assert len(result["files"]) >= 2


class TestBrowseRecentPreview:
    def test_preview(self, rich_store):
        result = cmd_browse_recent(_args(store=rich_store.root, format="television-preview", limit=50, entry=None))
        assert isinstance(result, str)
        assert "Type:" in result or "Key:" in result


class TestBrowseStalePreview:
    def test_preview(self, rich_store):
        result = cmd_browse_stale(_args(store=rich_store.root, format="television-preview", days=0, entry=None))
        assert isinstance(result, str)

    def test_json_never_synced(self, rich_store):
        result = cmd_browse_stale(_args(store=rich_store.root, format="json", days=0, entry=None))
        assert len(result["stale"]) > 0
        for s in result["stale"]:
            assert s["status"] == "never synced"


class TestBrowseUnsyncedPreview:
    def test_preview(self, rich_store):
        result = cmd_browse_unsynced(_args(store=rich_store.root, format="television-preview", entry=None))
        assert isinstance(result, str)
        assert "Sync command" in result or "No unsynced" in result


class TestBrowseTimelinePreview:
    def test_preview(self, rich_store):
        result = cmd_browse_timeline(_args(store=rich_store.root, format="television-preview", entry=None))
        assert isinstance(result, str)
        assert "Type:" in result or "Key:" in result

    def test_preview_with_config(self, rich_store):
        result = cmd_browse_timeline(_args(store=rich_store.root, format="television-preview", entry="Paper X"))
        assert isinstance(result, str)


class TestBrowseKeySourcesPreview:
    def test_preview(self, rich_store):
        result = cmd_browse_key_sources(_args(store=rich_store.root, format="television-preview", key="demo", entry=None))
        assert isinstance(result, str)
        assert "Type:" in result

    def test_preview_no_match(self, rich_store):
        result = cmd_browse_key_sources(
            _args(store=rich_store.root, format="television-preview", key="demo", entry="zzz_missing")
        )
        assert isinstance(result, str)


class TestBrowsePapersPreview:
    def test_preview_no_match(self, rich_store):
        result = cmd_browse_papers(_args(store=rich_store.root, format="television-preview", entry="zzz_missing"))
        assert isinstance(result, str)
        assert "arXiv" in result or "URL" in result


class TestBrowseSourceFilesNonMd:
    def test_source_not_found(self, rich_store):
        result = cmd_browse_source_files(
            _args(store=rich_store.root, format="json", key="demo", source_id="nonexistent", entry=None)
        )
        assert "not found" in str(result)

    def test_preview_non_md_file(self, rich_store):
        result = cmd_browse_source_files(
            _args(store=rich_store.root, format="json", key="demo", source_id="aha-feat-1", entry=None)
        )
        if "files" in result:
            assert any(f["ext"] == ".json" for f in result["files"])

    def test_preview_fallback_read(self, rich_store):
        result = cmd_browse_source_files(
            _args(store=rich_store.root, format="television-preview", key="demo", source_id="aha-feat-1", entry="feat.json")
        )
        assert isinstance(result, str)


class TestBrowseFilesPreviewNoMatch:
    def test_no_match(self, rich_store):
        result = cmd_browse_files(
            _args(store=rich_store.root, format="television-preview", query=None, key=None, entry="zzz_missing")
        )
        assert isinstance(result, str)


class TestBrowseCrossrefEmpty:
    def test_empty_crossref(self, tmp_path):
        s = KnowledgeStore(tmp_path)
        s.initialize()
        s.create_collection_key("solo")
        s.add_collection_source(
            key_name="solo", source_type="arxiv", title="Unique",
            config={"url": "https://arxiv.org/abs/9999.99999"},
            update_command="know sync arxiv",
            delete_command="know del arxiv",
        )
        result = cmd_browse_crossref(_args(store=s.root, format="json", entry=None))
        assert result["crossref"] == []

    def test_television_empty(self, tmp_path):
        s = KnowledgeStore(tmp_path)
        s.initialize()
        result = cmd_browse_crossref(_args(store=s.root, format="television", entry=None))
        assert result == ""

    def test_preview_no_match(self, rich_store):
        result = cmd_browse_crossref(_args(store=rich_store.root, format="television-preview", entry="zzz_nope"))
        assert isinstance(result, str)


class TestBrowseCommandsPreviewNoMatch:
    def test_empty_store(self, tmp_path):
        s = KnowledgeStore(tmp_path)
        s.initialize()
        result = cmd_browse_commands(_args(store=s.root, format="television", entry=None))
        assert result == ""

    def test_preview_no_match(self, tmp_path):
        s = KnowledgeStore(tmp_path)
        s.initialize()
        result = cmd_browse_commands(_args(store=s.root, format="television-preview", entry="zzz"))
        assert "No command" in result


class TestBrowseStatsEmpty:
    def test_empty_store(self, tmp_path):
        s = KnowledgeStore(tmp_path)
        s.initialize()
        result = cmd_browse_stats(_args(store=s.root, format="json", entry=None))
        stats = {s["label"]: s["value"] for s in result["stats"]}
        assert stats["Total keys"] == "0"
        assert stats["Total sources"] == "0"


# ── Additional edge cases for browse_extended ────────────────────────────


class TestBrowseByKeyWithData:
    def test_json_with_rich(self, rich_store):
        result = cmd_browse_by_key(_args(store=rich_store.root, format="json", entry=None))
        assert len(result["keys"]) == 1
        assert result["keys"][0]["name"] == "demo"
        assert result["keys"][0]["source_count"] == 8

    def test_television_with_rich(self, rich_store):
        result = cmd_browse_by_key(_args(store=rich_store.root, format="television", entry=None))
        clean = _clean(result)
        assert "demo" in clean
        assert "sources" in clean

    def test_preview_with_rich(self, rich_store):
        result = cmd_browse_by_key(_args(store=rich_store.root, format="television-preview", entry="demo"))
        assert "demo" in result
        assert "Commands" in result


class TestBrowseByTypeWithData:
    def test_json_with_rich(self, rich_store):
        result = cmd_browse_by_type(_args(store=rich_store.root, format="json", entry=None))
        types = [t["type"] for t in result["types"]]
        assert "jira" in types
        assert "github" in types

    def test_television_with_rich(self, rich_store):
        result = cmd_browse_by_type(_args(store=rich_store.root, format="television", entry=None))
        clean = _clean(result)
        assert "jira" in clean or "arxiv" in clean


class TestBrowseCommandsWithData:
    def test_json(self, rich_store):
        result = cmd_browse_commands(_args(store=rich_store.root, format="json", entry=None))
        assert len(result["commands"]) > 0
        types = {c["type"] for c in result["commands"]}
        assert "sync" in types
        assert "export" in types
        assert "delete" in types

    def test_television(self, rich_store):
        result = cmd_browse_commands(_args(store=rich_store.root, format="television", entry=None))
        clean = _clean(result)
        assert "sync" in clean.lower()

    def test_preview(self, rich_store):
        result = cmd_browse_commands(_args(store=rich_store.root, format="television-preview", entry=None))
        assert "Command" in result


class TestBrowseStatsWithData:
    def test_json(self, rich_store):
        result = cmd_browse_stats(_args(store=rich_store.root, format="json", entry=None))
        labels = [s["label"] for s in result["stats"]]
        assert "Total keys" in labels
        assert "Total sources" in labels

    def test_television(self, rich_store):
        result = cmd_browse_stats(_args(store=rich_store.root, format="television", entry=None))
        clean = _clean(result)
        assert "Total keys" in clean

    def test_preview(self, rich_store):
        result = cmd_browse_stats(_args(store=rich_store.root, format="television-preview", entry=None))
        assert "Knowledge Base Statistics" in result


class TestBrowseReposWithData:
    def test_json(self, rich_store):
        result = cmd_browse_repos(_args(store=rich_store.root, format="json", entry=None))
        assert len(result["repos"]) == 1
        assert result["repos"][0]["repo_name"] == "owner/myrepo"

    def test_television(self, rich_store):
        result = cmd_browse_repos(_args(store=rich_store.root, format="television", entry=None))
        clean = _clean(result)
        assert "owner/myrepo" in clean


class TestBrowsePapersWithData:
    def test_json(self, rich_store):
        result = cmd_browse_papers(_args(store=rich_store.root, format="json", entry=None))
        assert len(result["papers"]) >= 1

    def test_television(self, rich_store):
        result = cmd_browse_papers(_args(store=rich_store.root, format="television", entry=None))
        clean = _clean(result)
        assert "2401.12345" in clean

    def test_preview(self, rich_store):
        result = cmd_browse_papers(_args(store=rich_store.root, format="television-preview", entry="2401.12345"))
        assert "arXiv" in result


class TestBrowseTimelineWithData:
    def test_json(self, rich_store):
        result = cmd_browse_timeline(_args(store=rich_store.root, format="json", entry=None))
        assert "timeline" in result
        assert len(result["timeline"]) == 8

    def test_television(self, rich_store):
        result = cmd_browse_timeline(_args(store=rich_store.root, format="television", entry=None))
        assert isinstance(result, str)
        assert len(result) > 0


class TestBrowseUnsyncedWithData:
    def test_json(self, rich_store):
        result = cmd_browse_unsynced(_args(store=rich_store.root, format="json", entry=None))
        assert len(result["unsynced"]) > 0

    def test_television(self, rich_store):
        result = cmd_browse_unsynced(_args(store=rich_store.root, format="television", entry=None))
        clean = _clean(result)
        assert len(clean) > 0


class TestBrowseRecentWithData:
    def test_json(self, rich_store):
        result = cmd_browse_recent(_args(store=rich_store.root, format="json", limit=50, entry=None))
        assert len(result["sources"]) > 0

    def test_television(self, rich_store):
        result = cmd_browse_recent(_args(store=rich_store.root, format="television", limit=50, entry=None))
        assert isinstance(result, str)


class TestBrowseStaleWithData:
    def test_json(self, rich_store):
        result = cmd_browse_stale(_args(store=rich_store.root, format="json", days=0, entry=None))
        assert len(result["stale"]) > 0

    def test_television(self, rich_store):
        result = cmd_browse_stale(_args(store=rich_store.root, format="television", days=0, entry=None))
        assert isinstance(result, str)


class TestBrowseFilesWithData:
    def test_json(self, rich_store):
        result = cmd_browse_files(_args(store=rich_store.root, format="json", query=None, key=None, entry=None))
        assert len(result["files"]) >= 1

    def test_television(self, rich_store):
        result = cmd_browse_files(_args(store=rich_store.root, format="television", query=None, key=None, entry=None))
        clean = _clean(result)
        assert len(clean) > 0

    def test_with_key_filter(self, rich_store):
        result = cmd_browse_files(_args(store=rich_store.root, format="json", query=None, key="demo", entry=None))
        assert len(result["files"]) >= 1

    def test_with_query_match(self, rich_store):
        result = cmd_browse_files(_args(store=rich_store.root, format="json", query="Abstract", key=None, entry=None))
        assert len(result["files"]) >= 1

    def test_with_query_no_match(self, rich_store):
        result = cmd_browse_files(_args(store=rich_store.root, format="json", query="zzz_nonexistent", key=None, entry=None))
        assert len(result["files"]) == 0


class TestBrowseKeySourcesWithData:
    def test_json(self, rich_store):
        result = cmd_browse_key_sources(_args(store=rich_store.root, format="json", key="demo", entry=None))
        assert len(result["sources"]) == 8

    def test_television(self, rich_store):
        result = cmd_browse_key_sources(_args(store=rich_store.root, format="television", key="demo", entry=None))
        assert isinstance(result, str)
        assert len(result) > 0


class TestBrowseSourceFilesWithData:
    def test_json_arxiv(self, rich_store):
        result = cmd_browse_source_files(
            _args(store=rich_store.root, format="json", key="demo", source_id="arxiv-paper-x", entry=None)
        )
        assert "files" in result
        assert len(result["files"]) >= 1

    def test_television_arxiv(self, rich_store):
        result = cmd_browse_source_files(
            _args(store=rich_store.root, format="television", key="demo", source_id="arxiv-paper-x", entry=None)
        )
        clean = _clean(result)
        assert "paper.md" in clean

    def test_preview_md(self, rich_store):
        result = cmd_browse_source_files(
            _args(store=rich_store.root, format="television-preview", key="demo", source_id="arxiv-paper-x", entry="paper.md")
        )
        assert "Abstract text" in result or "Paper X" in result
