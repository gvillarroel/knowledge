"""Tests for television output formatting across all commands."""
from __future__ import annotations

import pytest

from knowledge.television import (
    TV_FORMAT_CHOICES,
    format_arxiv_preview,
    format_arxiv_television,
    format_confluence_preview,
    format_confluence_television,
    format_jira_preview,
    format_jira_television,
    format_keys_preview,
    format_keys_television,
    format_sources_preview,
    format_sources_television,
    _find_arxiv_entry,
    _find_source,
    _find_confluence_result,
    _find_jira_issue,
    _resolve_selection,
    _strip_html_tags,
)


# ── TV_FORMAT_CHOICES ────────────────────────────────────────────────────

class TestTVFormatChoices:
    def test_choices_tuple(self):
        assert TV_FORMAT_CHOICES == ("json", "television", "television-preview")


# ── Keys ─────────────────────────────────────────────────────────────────

class TestKeysTelevision:
    def test_format_keys_television_basic(self):
        result = format_keys_television(["research", "work"])
        assert result == "research\nwork"

    def test_format_keys_television_empty(self):
        assert format_keys_television([]) == ""

    def test_format_keys_preview_basic(self):
        result = format_keys_preview(["research", "work"], "research")
        assert "# research" in result
        assert "know list sources --key research" in result
        assert "know sync --key research" in result
        assert "know export --key research" in result

    def test_format_keys_preview_no_selection(self):
        result = format_keys_preview(["research"], None)
        assert "# research" in result

    def test_format_keys_preview_empty(self):
        result = format_keys_preview([], None)
        assert "No key matched" in result

    def test_format_keys_preview_nonexistent_falls_back(self):
        result = format_keys_preview(["alpha"], "nonexistent")
        assert "# alpha" in result


# ── Sources ──────────────────────────────────────────────────────────────

class TestSourcesTelevision:
    SAMPLE_SOURCES = [
        {
            "id": "confluence-eng",
            "type": "confluence",
            "key": "research",
            "title": "ENG",
            "created_at": "2026-01-01T00:00:00+00:00",
            "updated_at": "2026-03-01T00:00:00+00:00",
            "config": {"space": "ENG", "base_url": "https://wiki.example.com"},
            "update_command": "know sync confluence --space ENG --key research",
            "delete_command": "know del --key research confluence-eng",
        },
        {
            "id": "jira-kan",
            "type": "jira",
            "key": "work",
            "title": "KAN",
            "config": {"project": "KAN"},
        },
    ]

    def test_format_sources_television_basic(self):
        result = format_sources_television(self.SAMPLE_SOURCES)
        lines = result.split("\n")
        assert len(lines) == 2
        assert "confluence-eng | confluence | research | ENG" in lines[0]
        assert "jira-kan | jira | work | KAN" in lines[1]

    def test_format_sources_television_empty(self):
        assert format_sources_television([]) == ""

    def test_format_sources_preview_by_id(self):
        result = format_sources_preview(
            self.SAMPLE_SOURCES, "confluence-eng | confluence | research | ENG"
        )
        assert "# ENG" in result
        assert "confluence-eng" in result
        assert "know sync confluence" in result
        assert "space: ENG" in result

    def test_format_sources_preview_no_selection(self):
        result = format_sources_preview(self.SAMPLE_SOURCES, None)
        assert "# ENG" in result

    def test_format_sources_preview_empty(self):
        result = format_sources_preview([], None)
        assert "No source matched" in result

    def test_find_source_by_id(self):
        found = _find_source(self.SAMPLE_SOURCES, "jira-kan | jira | work | KAN")
        assert found is not None
        assert found["id"] == "jira-kan"

    def test_find_source_fallback(self):
        found = _find_source(self.SAMPLE_SOURCES, "nonexistent")
        assert found is not None
        assert found["id"] == "confluence-eng"

    def test_find_source_empty(self):
        assert _find_source([], "anything") is None

    def test_format_sources_preview_with_markdown_body(self):
        body = "# Introduction\n\nSome content here."
        result = format_sources_preview(
            self.SAMPLE_SOURCES,
            "confluence-eng | confluence | research | ENG",
            markdown_body=body,
        )
        assert "# ENG" in result
        assert "# Introduction" in result
        assert "Some content here." in result
        # Should NOT contain metadata fields when body is present
        assert "Source id:" not in result
        assert "Type:" not in result

    def test_format_sources_preview_none_body_falls_back(self):
        result = format_sources_preview(
            self.SAMPLE_SOURCES,
            "confluence-eng | confluence | research | ENG",
            markdown_body=None,
        )
        # Falls back to metadata view
        assert "Source id:" in result
        assert "confluence-eng" in result

    def test_format_sources_preview_empty_body_falls_back(self):
        result = format_sources_preview(
            self.SAMPLE_SOURCES,
            "confluence-eng | confluence | research | ENG",
            markdown_body="",
        )
        # Empty string is falsy, falls back to metadata
        assert "Source id:" in result


# ── Confluence ───────────────────────────────────────────────────────────

class TestConfluenceTelevision:
    SAMPLE_MATCHES = [
        {
            "source_id": "confluence-eng",
            "key": "research",
            "space": "ENG",
            "base_url": "https://wiki.example.com",
            "cql": 'text ~ "incident"',
            "results": [
                {
                    "content": {
                        "title": "Incident Postmortem Q1",
                        "type": "page",
                        "_links": {"webui": "/wiki/spaces/ENG/pages/123"},
                        "history": {
                            "lastUpdated": {"when": "2026-02-15T10:00:00Z"}
                        },
                    },
                    "excerpt": "This was an <b>incident</b> report.",
                },
                {
                    "content": {
                        "title": "Runbook: Database",
                        "type": "page",
                        "_links": {"webui": "/wiki/spaces/ENG/pages/456"},
                    },
                    "excerpt": "Steps to recover database.",
                },
            ],
            "next_cursor": None,
        }
    ]

    def test_format_confluence_television_basic(self):
        result = format_confluence_television(self.SAMPLE_MATCHES)
        lines = result.split("\n")
        assert len(lines) == 2
        assert "Incident Postmortem Q1" in lines[0]
        assert "ENG" in lines[0]
        assert "Runbook: Database" in lines[1]

    def test_format_confluence_television_empty(self):
        assert format_confluence_television([]) == ""

    def test_format_confluence_preview_basic(self):
        result = format_confluence_preview(
            self.SAMPLE_MATCHES, "Incident Postmortem Q1 | ENG | research | url"
        )
        assert "# Incident Postmortem Q1" in result
        assert "Space: ENG" in result
        assert "incident" in result
        assert "Updated: 2026-02-15T10:00:00Z" in result

    def test_format_confluence_preview_no_selection(self):
        result = format_confluence_preview(self.SAMPLE_MATCHES, None)
        assert "# Incident Postmortem Q1" in result

    def test_format_confluence_preview_empty_matches(self):
        result = format_confluence_preview([], None)
        assert "No Confluence result matched" in result

    def test_format_confluence_preview_url(self):
        result = format_confluence_preview(
            self.SAMPLE_MATCHES, "Incident Postmortem Q1 | ENG | research | url"
        )
        assert "wiki.example.com" in result

    def test_find_confluence_result_empty(self):
        r, ctx = _find_confluence_result([], "anything")
        assert r is None
        assert ctx is None


# ── Jira ─────────────────────────────────────────────────────────────────

class TestJiraTelevision:
    SAMPLE_MATCHES = [
        {
            "source_id": "jira-kan",
            "key": "work",
            "project": "KAN",
            "base_url": "https://jira.example.com",
            "jql": "project = KAN",
            "issues": [
                {
                    "key": "KAN-101",
                    "id": "10101",
                    "fields": {
                        "summary": "Fix login bug",
                        "status": {"name": "In Progress"},
                        "issuetype": {"name": "Bug"},
                        "priority": {"name": "High"},
                        "assignee": {"displayName": "Alice"},
                        "reporter": {"displayName": "Bob"},
                        "labels": ["backend", "auth"],
                        "created": "2026-03-01T08:00:00Z",
                        "updated": "2026-03-20T14:00:00Z",
                    },
                },
                {
                    "key": "KAN-102",
                    "id": "10102",
                    "fields": {
                        "summary": "Add caching layer",
                        "status": {"name": "To Do"},
                        "issuetype": {"name": "Story"},
                        "priority": {"name": "Medium"},
                        "assignee": None,
                        "reporter": {"displayName": "Charlie"},
                        "labels": [],
                        "created": "2026-03-15T09:00:00Z",
                        "updated": "2026-03-15T09:00:00Z",
                    },
                },
            ],
            "next_page_token": None,
        }
    ]

    def test_format_jira_television_basic(self):
        result = format_jira_television(self.SAMPLE_MATCHES)
        lines = result.split("\n")
        assert len(lines) == 2
        assert "KAN-101" in lines[0]
        assert "Fix login bug" in lines[0]
        assert "In Progress" in lines[0]
        assert "Alice" in lines[0]
        assert "KAN-102" in lines[1]
        assert "unassigned" in lines[1]

    def test_format_jira_television_empty(self):
        assert format_jira_television([]) == ""

    def test_format_jira_preview_basic(self):
        result = format_jira_preview(
            self.SAMPLE_MATCHES, "KAN-101 | Fix login bug | In Progress | KAN | Alice"
        )
        assert "# KAN-101: Fix login bug" in result
        assert "Bug" in result
        assert "In Progress" in result
        assert "High" in result
        assert "Alice" in result
        assert "Bob" in result
        assert "backend" in result
        assert "jira.example.com" in result

    def test_format_jira_preview_no_selection(self):
        result = format_jira_preview(self.SAMPLE_MATCHES, None)
        assert "KAN-101" in result

    def test_format_jira_preview_empty(self):
        result = format_jira_preview([], None)
        assert "No Jira issue matched" in result

    def test_format_jira_preview_with_description(self):
        matches = [
            {
                "source_id": "jira-x",
                "key": "k",
                "project": "X",
                "base_url": "https://jira.example.com",
                "issues": [
                    {
                        "key": "X-1",
                        "fields": {
                            "summary": "Test",
                            "status": {"name": "Open"},
                            "issuetype": {"name": "Task"},
                            "priority": None,
                            "assignee": None,
                            "reporter": None,
                            "description": "Detailed description here.",
                            "created": "2026-01-01",
                            "updated": "2026-01-01",
                        },
                    }
                ],
            }
        ]
        result = format_jira_preview(matches, None)
        assert "Detailed description here." in result

    def test_find_jira_issue_empty(self):
        r, ctx = _find_jira_issue([], "anything")
        assert r is None
        assert ctx is None

    def test_find_jira_issue_by_key(self):
        flat = [
            ({"key": "KAN-101"}, {"project": "KAN"}),
            ({"key": "KAN-102"}, {"project": "KAN"}),
        ]
        issue, ctx = _find_jira_issue(flat, "KAN-102 | summary")
        assert issue["key"] == "KAN-102"


# ── arXiv ────────────────────────────────────────────────────────────────

class TestArxivTelevision:
    SAMPLE_ENTRIES = [
        {
            "title": "Attention Is All You Need",
            "primary_category": "cs.CL",
            "published": "2017-06-12T17:57:25Z",
            "updated": "2023-08-02T17:54:18Z",
            "authors": ["Ashish Vaswani", "Noam Shazeer"],
            "summary": "The dominant sequence transduction models...",
            "pdf_url": "http://arxiv.org/pdf/1706.03762v7",
            "id": "http://arxiv.org/abs/1706.03762v7",
        },
        {
            "title": "BERT: Pre-training",
            "primary_category": "cs.CL",
            "published": "2018-10-11T00:00:00Z",
        },
    ]

    def test_format_arxiv_television_basic(self):
        result = format_arxiv_television(self.SAMPLE_ENTRIES)
        lines = result.split("\n")
        assert len(lines) == 2
        assert "Attention Is All You Need | cs.CL | 2017-06-12" in lines[0]

    def test_format_arxiv_television_empty(self):
        assert format_arxiv_television([]) == ""

    def test_format_arxiv_television_skips_no_title(self):
        entries = [{"primary_category": "cs.CL"}]
        assert format_arxiv_television(entries) == ""

    def test_format_arxiv_preview_basic(self):
        result = format_arxiv_preview(
            self.SAMPLE_ENTRIES,
            "Attention Is All You Need | cs.CL | 2017-06-12T17:57:25Z",
        )
        assert "# Attention Is All You Need" in result
        assert "Ashish Vaswani" in result
        assert "dominant sequence" in result
        assert "PDF:" in result

    def test_format_arxiv_preview_no_selection(self):
        result = format_arxiv_preview(self.SAMPLE_ENTRIES, None)
        assert "Attention Is All You Need" in result

    def test_format_arxiv_preview_empty(self):
        result = format_arxiv_preview([], None)
        assert "No arXiv entry matched" in result

    def test_find_arxiv_entry_by_title(self):
        entry = _find_arxiv_entry(
            self.SAMPLE_ENTRIES,
            "BERT: Pre-training | cs.CL | 2018",
        )
        assert entry["title"] == "BERT: Pre-training"

    def test_find_arxiv_entry_fallback(self):
        entry = _find_arxiv_entry(self.SAMPLE_ENTRIES, "nonexistent")
        assert entry["title"] == "Attention Is All You Need"

    def test_find_arxiv_entry_empty(self):
        assert _find_arxiv_entry([], None) == {}

    def test_find_arxiv_entry_not_a_list(self):
        assert _find_arxiv_entry("not a list", None) == {}


# ── Helpers ──────────────────────────────────────────────────────────────

class TestHelpers:
    def test_resolve_selection_empty(self):
        assert _resolve_selection([], "x") is None

    def test_resolve_selection_none(self):
        assert _resolve_selection(["a", "b"], None) == "a"

    def test_resolve_selection_match(self):
        assert _resolve_selection(["a", "b"], "b") == "b"

    def test_resolve_selection_no_match_fallback(self):
        assert _resolve_selection(["a", "b"], "c") == "a"

    def test_strip_html_tags(self):
        assert _strip_html_tags("<b>bold</b> text") == "bold text"
        assert _strip_html_tags("no tags") == "no tags"
        assert _strip_html_tags("") == ""


# ── CLI integration with --format television ─────────────────────────────

class TestCLITelevisionIntegration:
    """Test that commands accept --format television flags via the parser."""

    def test_list_keys_television(self, tmp_path):
        from knowledge.cli import main
        store = tmp_path / "store"
        # Create a key
        main(["--store", str(store), "add", "key", "mykey"])
        # List keys in television format
        rc = main(["--store", str(store), "list", "keys", "--format", "television"])
        assert rc == 0

    def test_list_keys_television_preview(self, tmp_path):
        from knowledge.cli import main
        store = tmp_path / "store"
        main(["--store", str(store), "add", "key", "mykey"])
        rc = main(["--store", str(store), "list", "keys", "--format", "television-preview", "--entry", "mykey"])
        assert rc == 0

    def test_list_sources_television(self, tmp_path):
        from knowledge.cli import main
        store = tmp_path / "store"
        main(["--store", str(store), "add", "key", "k1"])
        rc = main(["--store", str(store), "list", "sources", "--format", "television"])
        assert rc == 0

    def test_list_sources_television_preview(self, tmp_path):
        from knowledge.cli import main
        store = tmp_path / "store"
        main(["--store", str(store), "add", "key", "k1"])
        main(["--store", str(store), "add", "arxiv", "https://arxiv.org/abs/1706.03762", "--key", "k1"])
        rc = main(["--store", str(store), "list", "sources", "--format", "television-preview"])
        assert rc == 0

    def test_list_credentials_does_not_accept_television_flags(self, tmp_path):
        from knowledge.cli import main
        store = tmp_path / "store"
        main(["--store", str(store), "init"])
        main(["--store", str(store), "set", "credential", "tok", "val"])
        with pytest.raises(SystemExit) as excinfo:
            main(["--store", str(store), "list", "credentials", "--format", "television"])
        assert excinfo.value.code == 2
