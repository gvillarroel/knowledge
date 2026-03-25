"""Tests for ``know browse`` extended commands (browse_extended.py)."""

from __future__ import annotations

import re
from argparse import Namespace

import pytest

from knowledge.browse_extended import (
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
    _extract_arxiv_id,
    _find_by_field,
    _find_by_name,
    _find_by_title,
    _find_cmd,
    _repo_short_name,
)
from knowledge.store import KnowledgeStore


def _clean(text: str) -> str:
    return re.sub(r"\033\[[0-9;]*m", "", text)


def _args(**kwargs) -> Namespace:
    defaults = {"store": None, "json": False, "verbose": False, "quiet": False}
    defaults.update(kwargs)
    return Namespace(**defaults)


@pytest.fixture
def store(tmp_path):
    s = KnowledgeStore(tmp_path)
    s.initialize()
    return s


@pytest.fixture
def populated_store(store):
    """Store with multiple keys and sources."""
    store.create_collection_key("alpha")
    store.add_collection_source(
        key_name="alpha", source_type="arxiv", title="https://arxiv.org/abs/2301.00001",
        config={"url": "https://arxiv.org/abs/2301.00001"},
        update_command="know sync arxiv https://arxiv.org/abs/2301.00001 --key alpha",
        delete_command="know del --key alpha arxiv-2301.00001",
    )
    store.add_collection_source(
        key_name="alpha", source_type="github", title="https://github.com/test/repo",
        config={"repo_url": "https://github.com/test/repo", "branches": ["main"]},
        update_command="know sync github-repo https://github.com/test/repo --key alpha --branch main",
        delete_command="know del --key alpha github-repo",
    )
    store.create_collection_key("beta")
    store.add_collection_source(
        key_name="beta", source_type="arxiv", title="https://arxiv.org/abs/2301.00001",
        config={"url": "https://arxiv.org/abs/2301.00001"},
        update_command="know sync arxiv https://arxiv.org/abs/2301.00001 --key beta",
        delete_command="know del --key beta arxiv-2301.00001",
    )
    store.add_collection_source(
        key_name="beta", source_type="jira", title="PROJ",
        config={"project": "PROJ", "jql": "project=PROJ", "base_url": "https://jira.example.com"},
        update_command="know sync jira-project PROJ --key beta",
        delete_command="know del --key beta jira-proj",
    )
    # Add a local markdown file
    sd = store.root / "alpha" / "arxiv" / "arxiv-2301.00001"
    sd.mkdir(parents=True, exist_ok=True)
    (sd / "paper.md").write_text("---\ntitle: Test Paper\n---\n\n# Test Paper\nAbstract here.", encoding="utf-8")
    return store


# ── by-key ──────────────────────────────────────────────────────────────

class TestBrowseByKey:
    def test_json(self, populated_store):
        result = cmd_browse_by_key(_args(store=populated_store.root, format="json", entry=None))
        assert "keys" in result
        assert len(result["keys"]) == 2
        assert result["keys"][0]["name"] == "alpha"

    def test_television(self, populated_store):
        result = cmd_browse_by_key(_args(store=populated_store.root, format="television", entry=None))
        clean = _clean(result)
        assert "alpha" in clean
        assert "beta" in clean
        assert "sources" in clean

    def test_preview(self, populated_store):
        result = cmd_browse_by_key(_args(store=populated_store.root, format="television-preview", entry="alpha"))
        assert "alpha" in result
        assert "Commands" in result


# ── by-type ──────────────────────────────────────────────────────────────

class TestBrowseByType:
    def test_json(self, populated_store):
        result = cmd_browse_by_type(_args(store=populated_store.root, format="json", entry=None))
        assert "types" in result
        types = [t["type"] for t in result["types"]]
        assert "arxiv" in types

    def test_television(self, populated_store):
        result = cmd_browse_by_type(_args(store=populated_store.root, format="television", entry=None))
        clean = _clean(result)
        assert "arxiv" in clean
        assert "synced" in clean


# ── papers ──────────────────────────────────────────────────────────────

class TestBrowsePapers:
    def test_json(self, populated_store):
        result = cmd_browse_papers(_args(store=populated_store.root, format="json", entry=None))
        assert "papers" in result
        assert len(result["papers"]) == 2

    def test_television(self, populated_store):
        result = cmd_browse_papers(_args(store=populated_store.root, format="television", entry=None))
        clean = _clean(result)
        assert "2301.00001" in clean

    def test_preview(self, populated_store):
        result = cmd_browse_papers(_args(store=populated_store.root, format="television-preview", entry="2301.00001"))
        assert "2301.00001" in result


# ── repos ────────────────────────────────────────────────────────────────

class TestBrowseRepos:
    def test_json(self, populated_store):
        result = cmd_browse_repos(_args(store=populated_store.root, format="json", entry=None))
        assert "repos" in result
        assert len(result["repos"]) == 1

    def test_television(self, populated_store):
        result = cmd_browse_repos(_args(store=populated_store.root, format="television", entry=None))
        clean = _clean(result)
        assert "test/repo" in clean


# ── repo-files ──────────────────────────────────────────────────────────

class TestBrowseRepoFiles:
    def test_empty(self, populated_store):
        result = cmd_browse_repo_files(_args(store=populated_store.root, format="json", repo="test/repo", entry=None))
        assert "files" in result

    def test_television_empty(self, populated_store):
        result = cmd_browse_repo_files(_args(store=populated_store.root, format="television", repo="nonexistent", entry=None))
        assert isinstance(result, str)


# ── files ────────────────────────────────────────────────────────────────

class TestBrowseFiles:
    def test_json(self, populated_store):
        result = cmd_browse_files(_args(store=populated_store.root, format="json", query=None, key=None, entry=None))
        assert "files" in result
        assert len(result["files"]) >= 1

    def test_with_query(self, populated_store):
        result = cmd_browse_files(_args(store=populated_store.root, format="json", query="Abstract", key=None, entry=None))
        assert len(result["files"]) >= 1

    def test_query_no_match(self, populated_store):
        result = cmd_browse_files(_args(store=populated_store.root, format="json", query="zzz_nonexistent_zzz", key=None, entry=None))
        assert len(result["files"]) == 0

    def test_television(self, populated_store):
        result = cmd_browse_files(_args(store=populated_store.root, format="television", query=None, key=None, entry=None))
        clean = _clean(result)
        assert "Test Paper" in clean

    def test_preview(self, populated_store):
        result = cmd_browse_files(_args(store=populated_store.root, format="television-preview", query=None, key=None, entry=None))
        assert "Abstract here" in result


# ── recent ──────────────────────────────────────────────────────────────

class TestBrowseRecent:
    def test_json(self, populated_store):
        result = cmd_browse_recent(_args(store=populated_store.root, format="json", limit=50, entry=None))
        assert "sources" in result

    def test_television(self, populated_store):
        result = cmd_browse_recent(_args(store=populated_store.root, format="television", limit=50, entry=None))
        assert isinstance(result, str)


# ── stale ────────────────────────────────────────────────────────────────

class TestBrowseStale:
    def test_json(self, populated_store):
        result = cmd_browse_stale(_args(store=populated_store.root, format="json", days=0, entry=None))
        assert "stale" in result

    def test_television(self, populated_store):
        result = cmd_browse_stale(_args(store=populated_store.root, format="television", days=0, entry=None))
        assert isinstance(result, str)


# ── unsynced ─────────────────────────────────────────────────────────────

class TestBrowseUnsynced:
    def test_json(self, populated_store):
        result = cmd_browse_unsynced(_args(store=populated_store.root, format="json", entry=None))
        assert "unsynced" in result
        # All sources are unsynced in this fixture (no sync has been run)
        assert len(result["unsynced"]) >= 1

    def test_television(self, populated_store):
        result = cmd_browse_unsynced(_args(store=populated_store.root, format="television", entry=None))
        clean = _clean(result)
        assert len(clean) > 0


# ── timeline ─────────────────────────────────────────────────────────────

class TestBrowseTimeline:
    def test_json(self, populated_store):
        result = cmd_browse_timeline(_args(store=populated_store.root, format="json", entry=None))
        assert "timeline" in result

    def test_television(self, populated_store):
        result = cmd_browse_timeline(_args(store=populated_store.root, format="television", entry=None))
        assert isinstance(result, str)


# ── commands ─────────────────────────────────────────────────────────────

class TestBrowseCommands:
    def test_json(self, populated_store):
        result = cmd_browse_commands(_args(store=populated_store.root, format="json", entry=None))
        assert "commands" in result
        types = {c["type"] for c in result["commands"]}
        assert "sync" in types
        assert "export" in types
        assert "delete" in types

    def test_television(self, populated_store):
        result = cmd_browse_commands(_args(store=populated_store.root, format="television", entry=None))
        clean = _clean(result)
        assert "sync" in clean.lower()

    def test_preview(self, populated_store):
        result = cmd_browse_commands(_args(store=populated_store.root, format="television-preview", entry=None))
        assert "Command" in result


# ── stats ────────────────────────────────────────────────────────────────

class TestBrowseStats:
    def test_json(self, populated_store):
        result = cmd_browse_stats(_args(store=populated_store.root, format="json", entry=None))
        assert "stats" in result
        labels = [s["label"] for s in result["stats"]]
        assert "Total keys" in labels
        assert "Total sources" in labels

    def test_television(self, populated_store):
        result = cmd_browse_stats(_args(store=populated_store.root, format="television", entry=None))
        clean = _clean(result)
        assert "Total keys" in clean

    def test_preview(self, populated_store):
        result = cmd_browse_stats(_args(store=populated_store.root, format="television-preview", entry=None))
        assert "Knowledge Base Statistics" in result


# ── crossref ─────────────────────────────────────────────────────────────

class TestBrowseCrossref:
    def test_json(self, populated_store):
        result = cmd_browse_crossref(_args(store=populated_store.root, format="json", entry=None))
        assert "crossref" in result
        # arxiv 2301.00001 is in both alpha and beta
        assert len(result["crossref"]) == 1
        assert result["crossref"][0]["key_count"] == 2

    def test_television(self, populated_store):
        result = cmd_browse_crossref(_args(store=populated_store.root, format="television", entry=None))
        clean = _clean(result)
        assert "2301.00001" in clean
        assert "2 keys" in clean

    def test_preview(self, populated_store):
        result = cmd_browse_crossref(_args(store=populated_store.root, format="television-preview", entry="2301.00001"))
        assert "alpha" in result
        assert "beta" in result


# ── key-sources ──────────────────────────────────────────────────────────

class TestBrowseKeySources:
    def test_json(self, populated_store):
        result = cmd_browse_key_sources(_args(store=populated_store.root, format="json", key="alpha", entry=None))
        assert "sources" in result
        assert len(result["sources"]) == 2

    def test_television(self, populated_store):
        result = cmd_browse_key_sources(_args(store=populated_store.root, format="television", key="alpha", entry=None))
        clean = _clean(result)
        assert "arxiv" in clean or "github" in clean

    def test_no_key(self, populated_store):
        result = cmd_browse_key_sources(_args(store=populated_store.root, format="json", key=None, entry=None))
        assert "No key" in str(result)


# ── source-files ─────────────────────────────────────────────────────────

class TestBrowseSourceFiles:
    def test_json(self, populated_store):
        result = cmd_browse_source_files(
            _args(store=populated_store.root, format="json", key="alpha", source_id="arxiv-2301.00001", entry=None)
        )
        assert "files" in result
        assert len(result["files"]) >= 1

    def test_television(self, populated_store):
        result = cmd_browse_source_files(
            _args(store=populated_store.root, format="television", key="alpha", source_id="arxiv-2301.00001", entry=None)
        )
        clean = _clean(result)
        assert "paper.md" in clean

    def test_preview(self, populated_store):
        result = cmd_browse_source_files(
            _args(store=populated_store.root, format="television-preview", key="alpha", source_id="arxiv-2301.00001", entry=None)
        )
        assert "Abstract here" in result or "Test Paper" in result

    def test_missing_args(self, populated_store):
        result = cmd_browse_source_files(
            _args(store=populated_store.root, format="json", key=None, source_id=None, entry=None)
        )
        assert "Need" in str(result)


# ── Helpers ──────────────────────────────────────────────────────────────

class TestExtendedHelpers:
    def test_extract_arxiv_id(self):
        assert _extract_arxiv_id("https://arxiv.org/abs/2301.00001") == "2301.00001"
        assert _extract_arxiv_id("https://arxiv.org/pdf/2301.00001v2") == "2301.00001v2"
        assert _extract_arxiv_id("not-an-id") == "not-an-id"

    def test_repo_short_name(self):
        assert _repo_short_name("https://github.com/owner/repo.git") == "owner/repo"
        assert _repo_short_name("https://github.com/owner/repo") == "owner/repo"

    def test_find_by_name(self):
        items = [{"name": "alpha"}, {"name": "beta"}]
        assert _find_by_name(items, None) == items[0]
        assert _find_by_name(items, "beta")["name"] == "beta"
        assert _find_by_name([], "x") is None

    def test_find_by_field(self):
        items = [{"type": "arxiv"}, {"type": "jira"}]
        assert _find_by_field(items, "type", "jira")["type"] == "jira"
        assert _find_by_field(items, "type", None) == items[0]
        assert _find_by_field([], "type", "x") is None

    def test_find_by_title(self):
        items = [{"title": "Paper A"}, {"title": "Paper B"}]
        assert _find_by_title(items, "Paper B")["title"] == "Paper B"
        assert _find_by_title(items, None) == items[0]

    def test_find_cmd(self):
        cmds = [{"command": "know sync --key a"}, {"command": "know export --key b"}]
        assert _find_cmd(cmds, "know export --key b")["command"] == "know export --key b"
        assert _find_cmd(cmds, None) == cmds[0]
        assert _find_cmd([], "x") is None


# ── CLI parser integration ──────────────────────────────────────────────

class TestExtendedCLIParsing:
    def test_all_extended_browse_subcommands(self):
        from knowledge.cli import build_parser
        parser = build_parser()
        for cmd in [
            "by-key", "by-type", "papers", "repos", "repo-files",
            "files", "recent", "stale", "unsynced", "timeline",
            "commands", "stats", "crossref",
        ]:
            args = parser.parse_args(["browse", cmd, "--format", "television"])
            assert args.format == "television"

    def test_key_sources_parse(self):
        from knowledge.cli import build_parser
        parser = build_parser()
        args = parser.parse_args(["browse", "key-sources", "--key", "alpha", "--format", "television"])
        assert args.key == "alpha"

    def test_source_files_parse(self):
        from knowledge.cli import build_parser
        parser = build_parser()
        args = parser.parse_args(["browse", "source-files", "--key", "a", "--source-id", "arxiv-x"])
        assert args.key == "a"
        assert args.source_id == "arxiv-x"

    def test_files_with_query(self):
        from knowledge.cli import build_parser
        parser = build_parser()
        args = parser.parse_args(["browse", "files", "--query", "test", "--key", "k"])
        assert args.query == "test"
        assert args.key == "k"
