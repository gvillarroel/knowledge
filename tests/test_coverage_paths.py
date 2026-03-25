from __future__ import annotations

import json
import subprocess
from argparse import Namespace
from pathlib import Path
from types import SimpleNamespace
from zipfile import ZipFile

import pytest
import yaml

from knowledge import commands
from knowledge.exporter import export_source
from knowledge.registry import create_source_adapter
from knowledge.sources.aha import AhaSource
from knowledge.sources.arxiv import ArxivSource
from knowledge.sources.confluence import ConfluenceSource, confluence_storage_to_markdown, search_confluence
from knowledge.sources.crawl4ai_site import SiteSource
from knowledge.sources.github_repo import GitHubRepoSource
from knowledge.sources.google_releases import GoogleReleasesSource
from knowledge.sources.jira import JiraSource, search_jira
from knowledge.sources.television import TelevisionSource
from knowledge.sources.video import VideoSource, extract_video_id
from knowledge.store import KnowledgeStore


class DummyResponse:
    def __init__(self, payload: dict | None = None, text: str = "") -> None:
        self._payload = payload or {}
        self.text = text

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict:
        return self._payload


def make_store(tmp_path: Path) -> KnowledgeStore:
    store = KnowledgeStore(tmp_path)
    store.initialize()
    return store


def test_key_set_and_key_list_command_roundtrip(tmp_path: Path) -> None:
    args = Namespace(store=tmp_path, name="jira_token", value="secret")
    assert commands.cmd_key_set(args) == {"stored": "jira_token"}
    assert commands.cmd_key_list(Namespace(store=tmp_path)) == {"keys": ["jira_token"]}


def test_delete_source_command_removes_record(tmp_path: Path) -> None:
    store = make_store(tmp_path)
    store.create_collection_key("docs")
    source = store.add_collection_source(
        "docs",
        "confluence",
        title="ENG",
        config={"space": "ENG"},
        update_command="know sync confluence --space ENG --key docs",
        delete_command="know del --key docs confluence-eng",
    )

    payload = commands.cmd_delete_source(Namespace(store=tmp_path, key="docs", source_id=source["id"]))
    assert payload == {"key": "docs", "id": "confluence-eng", "type": "confluence"}
    metadata = store.get_collection_metadata("docs")
    assert metadata["sources"] == []
    assert not (tmp_path / "docs" / "confluence" / "confluence-eng.yaml").exists()
    assert not (tmp_path / "docs" / "confluence" / "confluence-eng").exists()


def test_sync_filters_to_matching_source_value(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    store = make_store(tmp_path)
    store.create_collection_key("docs")
    store.add_collection_source(
        "docs",
        "confluence",
        title="ENG",
        config={"space": "ENG"},
        update_command="sync eng",
        delete_command="del eng",
    )
    store.add_collection_source(
        "docs",
        "confluence",
        title="OPS",
        config={"space": "OPS"},
        update_command="sync ops",
        delete_command="del ops",
    )

    synced_ids: list[str] = []

    class StubAdapter:
        def __init__(self, source: dict, _store: KnowledgeStore) -> None:
            self.source = source

        def sync(self) -> dict[str, str]:
            synced_ids.append(self.source["id"])
            return {"source": self.source["id"]}

    monkeypatch.setattr(commands, "create_source_adapter", lambda source, _store: StubAdapter(source, store))

    payload = commands.cmd_sync(
        Namespace(store=tmp_path, key="docs", source_type="confluence", match_value="OPS")
    )
    assert payload == {"synced": [{"source": "confluence-ops"}]}
    assert synced_ids == ["confluence-ops"]


def test_prepare_source_for_sync_adds_ephemeral_github_branch_override() -> None:
    source = {
        "key": "code",
        "type": "github",
        "id": "github-repo",
        "config": {"repo_url": "https://github.com/example/repo.git", "branches": ["main"]},
    }

    prepared = commands._prepare_source_for_sync(source, Namespace(branch=["release"]))

    assert prepared["_sync_branches"] == ["release"]
    assert prepared["config"]["branches"] == ["main"]
    assert "_sync_branches" not in source


def test_search_confluence_command_marks_sources_missing_credentials(tmp_path: Path) -> None:
    store = make_store(tmp_path)
    store.create_collection_key("docs")
    store.add_collection_source(
        "docs",
        "confluence",
        title="ENG",
        config={"space": "ENG"},
        update_command="sync",
        delete_command="del",
    )

    payload = commands.cmd_search_confluence(
        Namespace(
            store=tmp_path,
            query="incident postmortem",
            knowledge_key=None,
            space=None,
            cql=None,
            limit=25,
            cursor=None,
        )
    )

    assert payload["matches"][0]["error"] == "missing credentials or base_url"


def test_add_jira_and_aha_commands_store_metadata(tmp_path: Path) -> None:
    store = make_store(tmp_path)
    store.create_collection_key("work")

    jira_payload = commands.cmd_add_jira_project(
        Namespace(
            store=tmp_path,
            key="work",
            project="PROD",
            jql=None,
            base_url="https://jira.example.com",
            username="$jira_user",
            token="$jira_token",
            field=["summary"],
            limit=25,
        )
    )
    aha_payload = commands.cmd_add_aha_workspace(
        Namespace(
            store=tmp_path,
            key="work",
            workspace="ROADMAP",
            base_url="https://aha.example.com",
            token="$aha_token",
            limit=20,
        )
    )

    assert jira_payload["source"]["type"] == "jira"
    assert aha_payload["source"]["type"] == "aha"
    metadata = store.get_collection_metadata("work")
    assert {source["type"] for source in metadata["sources"]} == {"jira", "aha"}


def test_add_video_command_stores_normalized_id(tmp_path: Path) -> None:
    store = make_store(tmp_path)
    store.create_collection_key("media")

    payload = commands.cmd_add_video(
        Namespace(
            store=tmp_path,
            key="media",
            url="https://www.youtube.com/watch?v=cxqRKt1GYNQ&t=1405s",
            language=["en"],
        )
    )

    assert payload["source"]["id"] == "video-cxqrkt1gynq"
    assert payload["source"]["config"]["languages"] == ["en"]


def test_add_television_command_stores_channel_commands(tmp_path: Path) -> None:
    store = make_store(tmp_path)
    store.create_collection_key("automation")

    payload = commands.cmd_add_television(
        Namespace(
            store=tmp_path,
            key="automation",
            name="knowledge-sources",
            description="Browse registered sources",
            source_command="know list sources --key automation --json",
            source_display=None,
            preview_command="know export --key automation",
            action_command="know sync --key automation",
        )
    )

    assert payload["source"]["id"] == "television-knowledge-sources"
    assert payload["source"]["config"]["channel"] == "knowledge-sources"
    assert payload["source"]["config"]["source_command"] == "know list sources --key automation --json"


def test_add_collection_source_does_not_write_legacy_yaml_record(tmp_path: Path) -> None:
    store = make_store(tmp_path)
    store.create_collection_key("docs")

    store.add_collection_source(
        "docs",
        "confluence",
        title="ENG",
        config={"space": "ENG"},
        update_command="sync",
        delete_command="del",
    )

    assert not (tmp_path / "docs" / "confluence" / "confluence-eng.yaml").exists()


def test_update_collection_source_removes_legacy_yaml_record(tmp_path: Path) -> None:
    store = make_store(tmp_path)
    store.create_collection_key("docs")
    legacy_dir = tmp_path / "docs" / "confluence"
    legacy_dir.mkdir(parents=True, exist_ok=True)
    legacy_record = legacy_dir / "confluence-eng.yaml"
    legacy_record.write_text("type: confluence\n", encoding="utf-8")
    source = {
        "key": "docs",
        "type": "confluence",
        "id": "confluence-eng",
        "title": "ENG",
        "config": {"space": "ENG"},
        "created_at": "2026-03-22T00:00:00+00:00",
        "updated_at": "2026-03-22T00:00:00+00:00",
        "update_command": "sync",
        "delete_command": "del",
    }
    store.save_collection_metadata(
        "docs",
        {
            **store.get_collection_metadata("docs"),
            "sources": [{k: v for k, v in source.items() if k != "key"}],
        },
    )

    store.update_collection_source(source)

    assert not legacy_record.exists()
    assert not legacy_dir.exists()


def test_add_site_command_stores_url_and_limits(tmp_path: Path) -> None:
    store = make_store(tmp_path)
    store.create_collection_key("sites")

    payload = commands.cmd_add_site(
        Namespace(
            store=tmp_path,
            key="sites",
            url="https://openai.com/index/harness-engineering/",
            max_depth=2,
            max_pages=5,
        )
    )

    assert payload["source"]["id"] == "site-harness-engineering"
    assert payload["source"]["config"]["max_depth"] == 2
    assert payload["source"]["config"]["max_pages"] == 5


def test_matches_source_helper_covers_supported_fields() -> None:
    source = {
        "id": "jira-prod",
        "title": "PROD",
        "config": {
            "space": "ENG",
            "space_key": "ENG",
            "channel": "knowledge-sources",
            "url": "https://arxiv.org/abs/1",
            "repo_url": "https://github.com/example/repo.git",
            "project": "PROD",
            "workspace": "ROADMAP",
            "product": "ROADMAP",
        },
    }
    assert commands._matches_source(source, "jira-prod")
    assert commands._matches_source(source, "ENG")
    assert commands._matches_source(source, "knowledge-sources")
    assert commands._matches_source(source, "https://github.com/example/repo.git")
    assert commands._matches_source(source, "https://arxiv.org/abs/1")
    assert not commands._matches_source(source, "missing")


def test_search_jira_requires_query_or_jql() -> None:
    with pytest.raises(ValueError, match="requires either a query or an explicit --jql"):
        search_jira(
            base_url="https://jira.example.com",
            username="user@example.com",
            token="token",
        )


def test_arxiv_television_helpers_render_list_and_preview() -> None:
    entries = [
        {
            "title": "Attention Is All You Need",
            "primary_category": "cs.CL",
            "published": "2017-06-12T17:57:25Z",
            "updated": "2023-08-02T17:54:18Z",
            "authors": ["Ashish Vaswani"],
            "summary": "Transformer paper summary.",
            "pdf_url": "http://arxiv.org/pdf/1706.03762v7",
            "id": "http://arxiv.org/abs/1706.03762v7",
        }
    ]

    from knowledge.television import format_arxiv_television, format_arxiv_preview, _find_arxiv_entry

    tv_output = format_arxiv_television(entries)
    lines = tv_output.split("\n")
    selected = _find_arxiv_entry(entries, lines[0])
    preview = format_arxiv_preview(entries, lines[0])

    assert lines == ["Attention Is All You Need | cs.CL | 2017-06-12T17:57:25Z"]
    assert selected["title"] == "Attention Is All You Need"
    assert "# Attention Is All You Need" in preview
    assert "Transformer paper summary." in preview


def test_extract_video_id_supports_common_youtube_formats() -> None:
    assert extract_video_id("https://www.youtube.com/watch?v=cxqRKt1GYNQ&t=1405s") == "cxqRKt1GYNQ"
    assert extract_video_id("https://youtu.be/cxqRKt1GYNQ") == "cxqRKt1GYNQ"
    assert extract_video_id("https://www.youtube.com/shorts/cxqRKt1GYNQ") == "cxqRKt1GYNQ"


def test_export_source_wraps_binary_payload(tmp_path: Path) -> None:
    store = make_store(tmp_path)
    store.create_collection_key("docs")
    source = store.add_collection_source(
        "docs",
        "arxiv",
        title="https://arxiv.org/abs/1706.03762",
        config={"url": "https://arxiv.org/abs/1706.03762"},
        update_command="sync",
        delete_command="del",
    )
    binary_file = store.source_raw_dir(source) / "paper.bin"
    binary_file.write_bytes(b"\x00\x01")

    result = export_source(store, source)
    exported = (store.source_library_dir(source) / "paper.md").read_text(encoding="utf-8")

    assert result["files"] == 1
    assert "Binary or unsupported file type retained in raw store." in exported


def test_registry_rejects_unknown_source(tmp_path: Path) -> None:
    store = make_store(tmp_path)
    with pytest.raises(ValueError):
        create_source_adapter({"type": "unknown", "config": {}}, store)


def test_store_error_and_helper_paths(tmp_path: Path) -> None:
    store = make_store(tmp_path)
    store.create_collection_key("docs")

    with pytest.raises(Exception, match="already exists"):
        store.create_collection_key("docs")
    with pytest.raises(FileNotFoundError):
        store.get_collection_metadata("missing")
    with pytest.raises(Exception, match="not found"):
        store.delete_collection_source("docs", "missing")
    with pytest.raises(FileNotFoundError):
        store.import_archive(tmp_path / "missing.zip")

    store.set_key("token", "secret")
    assert store.resolve_key("$token") == "secret"
    assert store.resolve_key("plain") == "plain"
    with pytest.raises(Exception, match="not found"):
        store.resolve_key("$missing")

    assert store._read_yaml(tmp_path / "absent.yaml", default={"fallback": True}) == {"fallback": True}
    assert store._source_id("jira", "!!!") == "jira-source"


def test_store_resolve_key_supports_env_references(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    store = make_store(tmp_path)

    monkeypatch.setenv("JIRA_TOKEN", "secret-from-env")
    assert store.resolve_key("$env:JIRA_TOKEN") == "secret-from-env"

    monkeypatch.delenv("JIRA_TOKEN", raising=False)
    with pytest.raises(Exception, match="not found"):
        store.resolve_key("$env:JIRA_TOKEN")


def test_source_cache_dir_uses_system_temp_outside_store(tmp_path: Path) -> None:
    store = make_store(tmp_path)
    store.create_collection_key("docs")
    source = store.add_collection_source(
        "docs",
        "github",
        title="https://github.com/example/repo.git",
        config={"repo_url": "https://github.com/example/repo.git"},
        update_command="sync",
        delete_command="del",
    )

    cache_dir = store.source_cache_dir(source)

    import tempfile
    assert str(cache_dir).startswith(str(Path(tempfile.gettempdir()).resolve()))
    assert str(cache_dir).find(str(tmp_path.resolve())) == -1


def test_store_import_archive_creates_new_key_from_archive(tmp_path: Path) -> None:
    store = make_store(tmp_path)
    archive_path = tmp_path / "seed.zip"
    with ZipFile(archive_path, "w") as archive:
        archive.writestr(
            "imported/metadata.yaml",
            yaml.safe_dump(
                {
                    "version": 1,
                    "name": "imported",
                    "created_at": "2026-03-22T00:00:00+00:00",
                    "updated_at": "2026-03-22T00:00:00+00:00",
                    "sources": [{"id": "arxiv-1234", "type": "arxiv"}],
                    "commands": {"sync": "know sync --key imported"},
                },
                sort_keys=False,
            ),
        )
        archive.writestr("imported/arxiv/arxiv-1234/paper.txt", "hello\n")

    payload = store.import_archive(archive_path)
    assert payload["imported_keys"] == ["imported"]
    assert payload["merged_sources"] == 1
    assert (tmp_path / "imported" / "arxiv" / "arxiv-1234" / "paper.txt").exists()


def test_store_cleanup_legacy_source_records_removes_imported_yaml_records(tmp_path: Path) -> None:
    store = make_store(tmp_path)
    store.create_collection_key("docs")
    store.save_collection_metadata(
        "docs",
        {
            **store.get_collection_metadata("docs"),
            "sources": [
                {
                    "type": "confluence",
                    "id": "confluence-eng",
                    "title": "ENG",
                    "created_at": "2026-03-22T00:00:00+00:00",
                    "updated_at": "2026-03-22T00:00:00+00:00",
                    "update_command": "sync",
                    "delete_command": "del",
                    "config": {"space": "ENG"},
                }
            ],
        },
    )
    legacy_dir = tmp_path / "docs" / "confluence"
    legacy_dir.mkdir(parents=True, exist_ok=True)
    legacy_file = legacy_dir / "confluence-eng.yaml"
    legacy_file.write_text("type: confluence\n", encoding="utf-8")

    payload = store.cleanup_legacy_source_records("docs")

    assert payload == {"keys": 1, "removed": 1}
    assert not legacy_file.exists()
    assert not legacy_dir.exists()


def test_store_cleanup_orphan_source_dirs_removes_unregistered_source_and_legacy_dirs(tmp_path: Path) -> None:
    store = make_store(tmp_path)
    store.create_collection_key("docs")
    orphan_source = tmp_path / "docs" / "site" / "site-old"
    legacy_raw = tmp_path / "docs" / "raw" / "site" / "site-legacy"
    orphan_source.mkdir(parents=True, exist_ok=True)
    legacy_raw.mkdir(parents=True, exist_ok=True)
    (orphan_source / "pages.json").write_text("[]\n", encoding="utf-8")
    (legacy_raw / "pages.json").write_text("[]\n", encoding="utf-8")

    payload = store.cleanup_orphan_source_dirs("docs")

    assert payload == {"keys": 1, "removed": 2}
    assert not orphan_source.exists()
    assert not (tmp_path / "docs" / "raw").exists()


def test_confluence_sync_writes_pages_and_resolves_auth(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    store = make_store(tmp_path)
    store.create_collection_key("docs")
    store.set_key("confluence_user", "user@example.com")
    store.set_key("confluence_token", "token")
    source = store.add_collection_source(
        "docs",
        "confluence",
        title="ENG",
        config={
            "base_url": "https://conf.example.com",
            "space_key": "ENG",
            "username": "$confluence_user",
            "token": "$confluence_token",
            "limit": 5,
        },
        update_command="sync",
        delete_command="del",
    )

    captured: dict[str, object] = {}

    def fake_get(url: str, **kwargs: object) -> DummyResponse:
        captured["url"] = url
        captured["kwargs"] = kwargs
        return DummyResponse(
            payload={
                "results": [
                    {
                        "id": "1",
                        "body": {"storage": {"value": "<p>Hello</p>"}},
                    }
                ]
            }
        )

    monkeypatch.setattr("knowledge.sources.confluence.requests.get", fake_get)
    payload = ConfluenceSource(source, store).sync()

    assert payload["pages"] == 1
    assert captured["url"] == "https://conf.example.com/wiki/api/v2/pages"
    assert captured["kwargs"]["auth"] == ("user@example.com", "token")
    markdown_files = list(store.source_raw_dir(source).glob("*.md"))
    assert len(markdown_files) == 1
    contents = markdown_files[0].read_text(encoding="utf-8")
    assert "Hello" in contents
    assert "knowledge_key: docs" in contents
    assert "source_metadata:" not in contents


def test_confluence_sync_follows_pagination_links(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    store = make_store(tmp_path)
    store.create_collection_key("docs")
    source = store.add_collection_source(
        "docs",
        "confluence",
        title="ENG",
        config={
            "base_url": "https://conf.example.com",
            "space_key": "ENG",
            "username": "user@example.com",
            "token": "token",
            "limit": 1,
        },
        update_command="sync",
        delete_command="del",
    )

    calls: list[tuple[str, object | None]] = []

    def fake_get(url: str, **kwargs: object) -> DummyResponse:
        calls.append((url, kwargs.get("params")))
        if url == "https://conf.example.com/wiki/api/v2/pages":
            return DummyResponse(
                payload={
                    "results": [{"id": "1", "body": {"storage": {"value": "<p>One</p>"}}}],
                    "_links": {"next": "/wiki/api/v2/pages?cursor=abc"},
                }
            )
        if url == "https://conf.example.com/wiki/api/v2/pages?cursor=abc":
            return DummyResponse(
                payload={
                    "results": [{"id": "2", "body": {"storage": {"value": "<p>Two</p>"}}}],
                    "_links": {},
                }
            )
        raise AssertionError(url)

    monkeypatch.setattr("knowledge.sources.confluence.requests.get", fake_get)

    payload = ConfluenceSource(source, store).sync()

    assert payload["pages"] == 2
    assert calls == [
        (
            "https://conf.example.com/wiki/api/v2/pages",
            {"space-key": "ENG", "limit": 1, "body-format": "storage"},
        ),
        ("https://conf.example.com/wiki/api/v2/pages?cursor=abc", None),
    ]
    assert len(list(store.source_raw_dir(source).glob("*.md"))) == 2


def test_search_confluence_uses_search_endpoint_and_returns_cursor(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    def fake_get(url: str, **kwargs: object) -> DummyResponse:
        captured["url"] = url
        captured["kwargs"] = kwargs
        return DummyResponse(
            payload={
                "results": [{"title": "Runbook", "content": {"id": "42"}}],
                "_links": {"next": "/wiki/rest/api/search?cursor=next-1"},
            }
        )

    monkeypatch.setattr("knowledge.sources.confluence.requests.get", fake_get)

    payload = search_confluence(
        base_url="https://conf.example.com",
        username="user@example.com",
        token="token",
        query="runbook",
        space="ENG",
        limit=5,
    )

    assert payload["cql"] == 'text ~ "runbook" AND space = "ENG"'
    assert payload["next_cursor"] == "next-1"
    assert payload["results"] == [{"title": "Runbook", "content": {"id": "42"}}]
    assert captured["url"] == "https://conf.example.com/wiki/rest/api/search"
    assert captured["kwargs"]["params"] == {
        "cql": 'text ~ "runbook" AND space = "ENG"',
        "limit": 5,
    }
    assert captured["kwargs"]["auth"] == ("user@example.com", "token")


def test_search_confluence_builds_cql_with_extended_filters(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    def fake_get(url: str, **kwargs: object) -> DummyResponse:
        captured["url"] = url
        captured["kwargs"] = kwargs
        return DummyResponse(payload={"results": [], "_links": {}})

    monkeypatch.setattr("knowledge.sources.confluence.requests.get", fake_get)

    payload = search_confluence(
        base_url="https://conf.example.com",
        username="user@example.com",
        token="token",
        space="ENG",
        content_type="page",
        labels=["runbook", "prod"],
        title_contains="incident",
        created_after="2026-03-20T00:00:00+00:00",
        updated_before="2026-03-25T00:00:00+00:00",
        limit=10,
    )

    assert payload["cql"] == (
        'title ~ "incident" AND space = "ENG" AND type = "page" AND label = "runbook" '
        'AND label = "prod" AND created >= "2026-03-20T00:00:00+00:00" '
        'AND lastmodified <= "2026-03-25T00:00:00+00:00"'
    )
    assert captured["kwargs"]["params"]["limit"] == 10


def test_search_confluence_passes_cursor_and_allows_text_contains(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    def fake_get(_url: str, **kwargs: object) -> DummyResponse:
        captured["kwargs"] = kwargs
        return DummyResponse(payload={"results": [], "_links": {"next": "/wiki/rest/api/search?cursor=next-2&limit=5"}})

    monkeypatch.setattr("knowledge.sources.confluence.requests.get", fake_get)

    payload = search_confluence(
        base_url="https://conf.example.com",
        username="user@example.com",
        token="token",
        text_contains="deployment",
        created_before="2026-03-25T00:00:00+00:00",
        updated_after="2026-03-20T00:00:00+00:00",
        cursor="abc",
    )

    assert payload["next_cursor"] == "next-2"
    assert captured["kwargs"]["params"] == {
        "cql": 'text ~ "deployment" AND created <= "2026-03-25T00:00:00+00:00" AND lastmodified >= "2026-03-20T00:00:00+00:00"',
        "limit": 25,
        "cursor": "abc",
    }


def test_search_confluence_requires_search_input() -> None:
    with pytest.raises(ValueError, match="confluence search requires"):
        search_confluence(
            base_url="https://conf.example.com",
            username="user@example.com",
            token="token",
        )


def test_confluence_storage_to_markdown_renders_basic_blocks() -> None:
    payload = (
        "<h1>Overview</h1>"
        "<p>Hello <strong>world</strong> and <a href=\"https://example.com\">link</a>.</p>"
        "<ul><li>First</li><li>Second</li></ul>"
        "<pre><code>print('x')</code></pre>"
    )

    rendered = confluence_storage_to_markdown(payload)

    assert "# Overview" in rendered
    assert "Hello **world** and [link](https://example.com)." in rendered
    assert "- First" in rendered
    assert "- Second" in rendered
    assert "```" in rendered
    assert "print('x')" in rendered


def test_confluence_storage_to_markdown_covers_misc_blocks() -> None:
    payload = (
        "<blockquote><p>Quoted</p></blockquote>"
        "<p><em>soft</em><br/><code>x</code></p>"
        "<hr/>"
        "<ac:structured-macro ac:name=\"code\"><ac:plain-text-body>const x = 1;</ac:plain-text-body></ac:structured-macro>"
    )

    rendered = confluence_storage_to_markdown(payload)

    assert "> Quoted" in rendered
    assert "*soft*" in rendered
    assert "`x`" in rendered
    assert "---" in rendered
    assert "const x = 1;" in rendered


def test_confluence_storage_to_markdown_normalizes_task_artifacts() -> None:
    payload = "<p>Tasks</p><ac:task-list>\\n<ac:task>\\n<ac:task-id>1</ac:task-id>\\n<ac:task-status>incomplete</ac:task-status>\\nEscribe tu tarea aquí.\\n\\n</ac:task></ac:task-list>"

    rendered = confluence_storage_to_markdown(payload)

    assert "1\nincomplete" not in rendered
    assert "- [ ] Escribe tu tarea aquí." in rendered


def test_jira_sync_writes_issues_and_resolves_auth(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    store = make_store(tmp_path)
    store.create_collection_key("work")
    store.set_key("jira_user", "user@example.com")
    store.set_key("jira_token", "token")
    source = store.add_collection_source(
        "work",
        "jira",
        title="PROD",
        config={
            "base_url": "https://jira.example.com",
            "username": "$jira_user",
            "token": "$jira_token",
            "jql": "project = PROD",
            "fields": ["summary"],
            "limit": 10,
        },
        update_command="sync",
        delete_command="del",
    )

    def fake_get(_url: str, **_kwargs: object) -> DummyResponse:
        return DummyResponse(payload={"issues": [{"key": "PROD-1", "fields": {"summary": "Hello"}}]})

    monkeypatch.setattr("knowledge.sources.jira.requests.get", fake_get)
    payload = JiraSource(source, store).sync()

    assert payload["issues"] == 1
    issue_file = store.source_raw_dir(source) / "PROD-1.md"
    contents = issue_file.read_text(encoding="utf-8")
    assert "# Hello" in contents
    assert "issue_key: PROD-1" in contents
    assert "source_metadata:" not in contents


def test_search_jira_uses_v3_endpoint(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    def fake_get(url: str, **kwargs: object) -> DummyResponse:
        captured["url"] = url
        captured["kwargs"] = kwargs
        return DummyResponse(payload={"issues": [{"key": "PROD-7"}], "nextPageToken": "page-2"})

    monkeypatch.setattr("knowledge.sources.jira.requests.get", fake_get)

    payload = search_jira(
        base_url="https://jira.example.com",
        username="user@example.com",
        token="token",
        query="release bug",
        project="PROD",
        fields=["summary", "status"],
        limit=20,
        expand=["names"],
        fields_by_keys=True,
    )

    assert payload["jql"] == 'project = PROD AND (summary ~ "release bug" OR description ~ "release bug")'
    assert payload["issues"] == [{"key": "PROD-7"}]
    assert payload["next_page_token"] == "page-2"
    assert captured["url"] == "https://jira.example.com/rest/api/3/search/jql"
    assert captured["kwargs"]["params"] == {
        "jql": 'project = PROD AND (summary ~ "release bug" OR description ~ "release bug")',
        "maxResults": 20,
        "fieldsByKeys": "true",
        "fields": "summary,status",
        "expand": "names",
    }
    assert captured["kwargs"]["auth"] == ("user@example.com", "token")


def test_search_jira_supports_extended_jql_filters(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    def fake_get(url: str, **kwargs: object) -> DummyResponse:
        captured["url"] = url
        captured["kwargs"] = kwargs
        return DummyResponse(payload={"issues": [], "nextPageToken": None})

    monkeypatch.setattr("knowledge.sources.jira.requests.get", fake_get)

    payload = search_jira(
        base_url="https://jira.example.com",
        username="user@example.com",
        token="token",
        project="PROD",
        statuses=["To Do", "In Progress"],
        issue_types=["Task"],
        assignee="alice@example.com",
        updated_after="2026-03-20T00:00:00+00:00",
        order_by=["updated DESC", "created ASC"],
        properties=["foo", "bar"],
        limit=15,
    )

    assert payload["jql"] == (
        'project = PROD AND status in ("To Do", "In Progress") AND issuetype in ("Task") '
        'AND assignee = "alice@example.com" AND updated >= "2026-03-20T00:00:00+00:00" '
        'ORDER BY updated DESC, created ASC'
    )
    assert captured["kwargs"]["params"]["properties"] == "foo,bar"


def test_search_jira_passes_next_page_token_and_jql_override(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    def fake_get(_url: str, **kwargs: object) -> DummyResponse:
        captured["kwargs"] = kwargs
        return DummyResponse(payload={"issues": [], "nextPageToken": "page-3"})

    monkeypatch.setattr("knowledge.sources.jira.requests.get", fake_get)

    payload = search_jira(
        base_url="https://jira.example.com",
        username="user@example.com",
        token="token",
        jql="project = PROD ORDER BY updated DESC",
        next_page_token="page-2",
    )

    assert payload["jql"] == "project = PROD ORDER BY updated DESC"
    assert payload["next_page_token"] == "page-3"
    assert captured["kwargs"]["params"] == {
        "jql": "project = PROD ORDER BY updated DESC",
        "maxResults": 25,
        "fieldsByKeys": "false",
        "nextPageToken": "page-2",
    }


def test_jira_markdown_body_renders_richer_adf(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    store = make_store(tmp_path)
    store.create_collection_key("work")
    source = store.add_collection_source(
        "work",
        "jira",
        title="PROD",
        config={
            "base_url": "https://jira.example.com",
            "username": "user@example.com",
            "token": "token",
            "jql": "project = PROD",
            "fields": ["summary", "description", "status", "issuetype", "labels", "priority"],
            "limit": 10,
        },
        update_command="sync",
        delete_command="del",
    )

    def fake_get(_url: str, **_kwargs: object) -> DummyResponse:
        return DummyResponse(
            payload={
                "issues": [
                    {
                        "key": "PROD-1",
                        "id": "1",
                        "fields": {
                            "summary": "Hello",
                            "status": {"name": "In Progress"},
                            "issuetype": {"name": "Task"},
                            "priority": {"name": "High"},
                            "labels": ["ops"],
                            "description": {
                                "type": "doc",
                                "content": [
                                    {"type": "heading", "attrs": {"level": 2}, "content": [{"type": "text", "text": "Details"}]},
                                    {"type": "paragraph", "content": [{"type": "text", "text": "Need "}, {"type": "text", "text": "fix", "marks": [{"type": "strong"}]}]},
                                    {
                                        "type": "bulletList",
                                        "content": [
                                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "First"}]}]},
                                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Second"}]}]},
                                        ],
                                    },
                                    {"type": "codeBlock", "attrs": {"language": "python"}, "content": [{"type": "text", "text": "print('x')"}]},
                                ],
                            },
                        },
                    }
                ]
            }
        )

    monkeypatch.setattr("knowledge.sources.jira.requests.get", fake_get)
    JiraSource(source, store).sync()

    contents = (store.source_raw_dir(source) / "PROD-1.md").read_text(encoding="utf-8")
    assert "- Type: Task" in contents
    assert "- Priority: High" in contents
    assert "- Labels: ops" in contents
    assert "## Details" in contents
    assert "Need **fix**" in contents
    assert "- First" in contents
    assert "```python" in contents
    assert "source_metadata:" not in contents


def test_jira_markdown_body_covers_more_adf_nodes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    store = make_store(tmp_path)
    store.create_collection_key("work")
    source = store.add_collection_source(
        "work",
        "jira",
        title="PROD",
        config={
            "base_url": "https://jira.example.com",
            "username": "user@example.com",
            "token": "token",
            "jql": "project = PROD",
            "fields": ["summary", "description", "status", "assignee", "reporter", "created", "updated"],
            "limit": 10,
        },
        update_command="sync",
        delete_command="del",
    )

    def fake_get(_url: str, **_kwargs: object) -> DummyResponse:
        return DummyResponse(
            payload={
                "issues": [
                    {
                        "key": "PROD-2",
                        "id": "2",
                        "fields": {
                            "summary": "More nodes",
                            "status": {"name": "Done"},
                            "assignee": {"displayName": "Alice"},
                            "reporter": {"emailAddress": "bob@example.com"},
                            "created": "2026-03-20T00:00:00+00:00",
                            "updated": "2026-03-21T00:00:00+00:00",
                            "description": {
                                "type": "doc",
                                "content": [
                                    {"type": "paragraph", "content": [{"type": "text", "text": "line 1"}, {"type": "hardBreak"}, {"type": "text", "text": "line 2"}]},
                                    {"type": "blockquote", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Quoted"}]}]},
                                    {"type": "rule"},
                                    {"type": "panel", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Panel body"}]}]},
                                    {
                                        "type": "table",
                                        "content": [
                                            {"type": "tableRow", "content": [{"type": "tableHeader", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "H"}]}]}]},
                                            {"type": "tableRow", "content": [{"type": "tableCell", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "V"}]}]}]},
                                        ],
                                    },
                                    {"type": "paragraph", "content": [{"type": "mention", "attrs": {"text": "alice"}}, {"type": "text", "text": " "}, {"type": "emoji", "attrs": {"text": ":rocket:"}}]},
                                    {"type": "paragraph", "content": [{"type": "text", "text": "Docs", "marks": [{"type": "link", "attrs": {"href": "https://example.com"}}]}]},
                                    {"type": "blockCard", "attrs": {"url": "https://card.example.com"}},
                                ],
                            },
                        },
                    }
                ]
            }
        )

    monkeypatch.setattr("knowledge.sources.jira.requests.get", fake_get)
    JiraSource(source, store).sync()

    contents = (store.source_raw_dir(source) / "PROD-2.md").read_text(encoding="utf-8")
    assert "- Assignee: Alice" in contents
    assert "- Reporter: bob@example.com" in contents
    assert "line 1" in contents and "line 2" in contents
    assert "> Quoted" in contents
    assert "---" in contents
    assert "| H |" in contents
    assert "@alice" in contents
    assert ":rocket:" in contents
    assert "[Docs](https://example.com)" in contents
    assert "https://card.example.com" in contents
    assert "source_metadata:" not in contents


def test_jira_sync_follows_next_page_token(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    store = make_store(tmp_path)
    store.create_collection_key("work")
    source = store.add_collection_source(
        "work",
        "jira",
        title="PROD",
        config={
            "base_url": "https://jira.example.com",
            "username": "user@example.com",
            "token": "token",
            "jql": "project = PROD",
            "fields": ["summary"],
            "limit": 1,
        },
        update_command="sync",
        delete_command="del",
    )

    calls: list[dict[str, object]] = []

    def fake_get(_url: str, **kwargs: object) -> DummyResponse:
        calls.append(kwargs["params"])
        if "nextPageToken" not in kwargs["params"]:
            return DummyResponse(
                payload={
                    "issues": [{"key": "PROD-1", "fields": {"summary": "One"}}],
                    "nextPageToken": "token-2",
                }
            )
        return DummyResponse(payload={"issues": [{"key": "PROD-2", "fields": {"summary": "Two"}}]})

    monkeypatch.setattr("knowledge.sources.jira.requests.get", fake_get)

    payload = JiraSource(source, store).sync()

    assert payload["issues"] == 2
    assert calls == [
        {"jql": "project = PROD", "maxResults": 1, "fields": "summary"},
        {"jql": "project = PROD", "maxResults": 1, "fields": "summary", "nextPageToken": "token-2"},
    ]
    issue_file = store.source_raw_dir(source) / "PROD-2.md"
    assert "# Two" in issue_file.read_text(encoding="utf-8")


def test_aha_sync_writes_features(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    store = make_store(tmp_path)
    store.create_collection_key("roadmap")
    store.set_key("aha_token", "token")
    source = store.add_collection_source(
        "roadmap",
        "aha",
        title="PROD",
        config={
            "base_url": "https://aha.example.com",
            "product": "PROD",
            "token": "$aha_token",
            "limit": 10,
        },
        update_command="sync",
        delete_command="del",
    )

    def fake_get(_url: str, **_kwargs: object) -> DummyResponse:
        return DummyResponse(payload={"features": [{"id": "1", "reference_num": "PROD-1"}]})

    monkeypatch.setattr("knowledge.sources.aha.requests.get", fake_get)
    payload = AhaSource(source, store).sync()

    assert payload["features"] == 1
    assert (store.source_raw_dir(source) / "features" / "PROD-1.json").exists()


def test_arxiv_sync_fetches_feed_and_extracts_pdf_id(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    store = make_store(tmp_path)
    store.create_collection_key("papers")
    source = store.add_collection_source(
        "papers",
        "arxiv",
        title="https://arxiv.org/pdf/1706.03762.pdf",
        config={"url": "https://arxiv.org/pdf/1706.03762.pdf"},
        update_command="sync",
        delete_command="del",
    )

    captured: dict[str, str] = {}

    def fake_get(url: str, **_kwargs: object) -> DummyResponse:
        captured["url"] = url
        return DummyResponse(text="<feed/>")

    monkeypatch.setattr("knowledge.sources.arxiv.requests.get", fake_get)
    payload = ArxivSource(source, store).sync()

    assert payload["paper_id"] == "1706.03762"
    assert "1706.03762" in captured["url"]
    assert (store.source_raw_dir(source) / "paper.xml").read_text(encoding="utf-8") == "<feed/>"


def test_github_sync_clones_and_exports_text_files(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    store = make_store(tmp_path)
    store.create_collection_key("code")
    source = store.add_collection_source(
        "code",
        "github",
        title="https://github.com/example/repo.git",
        config={"repo_url": "https://github.com/example/repo.git", "branches": ["main"]},
        update_command="sync",
        delete_command="del",
    )

    calls: list[list[str]] = []
    cache_dir = store.source_cache_dir(source)
    if cache_dir.exists():
        for path in sorted(cache_dir.rglob("*"), reverse=True):
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                path.rmdir()
        cache_dir.rmdir()

    def fake_run(
        args: list[str],
        cwd: Path,
        check: bool,
        capture_output: bool,
        text: bool,
        encoding: str | None = None,
        errors: str | None = None,
    ) -> SimpleNamespace:
        del check, capture_output, text, encoding, errors
        calls.append(args)
        if args[:3] == ["git", "clone", "--mirror"]:
            Path(args[-1]).mkdir(parents=True, exist_ok=True)
            return SimpleNamespace(stdout="")
        if args[:4] == ["git", "ls-tree", "-r", "--name-only"]:
            return SimpleNamespace(stdout="README.md\nimage.png\nsrc/app.py\n")
        if args[:2] == ["git", "show"]:
            return SimpleNamespace(stdout="content\n")
        if args[:3] == ["git", "fetch", "--all"]:
            return SimpleNamespace(stdout="")
        raise AssertionError(f"Unexpected git invocation: {args} cwd={cwd}")

    monkeypatch.setattr(subprocess, "run", fake_run)
    payload = GitHubRepoSource(source, store).sync()

    assert payload["files"] == 2
    assert any(args[:3] == ["git", "clone", "--mirror"] for args in calls)
    assert (store.source_raw_dir(source) / "main" / "README.md").exists()
    assert not (store.source_raw_dir(source) / "main" / "image.png").exists()


def test_github_sync_uses_ephemeral_branch_override_without_persisting_it(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    store = make_store(tmp_path)
    store.create_collection_key("code")
    source = store.add_collection_source(
        "code",
        "github",
        title="https://github.com/example/repo.git",
        config={"repo_url": "https://github.com/example/repo.git", "branches": ["main"]},
        update_command="sync",
        delete_command="del",
    )
    source["_sync_branches"] = ["release"]

    observed_refs: list[str] = []
    cache_dir = store.source_cache_dir(source)
    if cache_dir.exists():
        for path in sorted(cache_dir.rglob("*"), reverse=True):
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                path.rmdir()
        cache_dir.rmdir()

    def fake_run(
        args: list[str],
        cwd: Path,
        check: bool,
        capture_output: bool,
        text: bool,
        encoding: str | None = None,
        errors: str | None = None,
    ) -> SimpleNamespace:
        del cwd, check, capture_output, text, encoding, errors
        if args[:3] == ["git", "clone", "--mirror"]:
            Path(args[-1]).mkdir(parents=True, exist_ok=True)
            return SimpleNamespace(stdout="")
        if args[:4] == ["git", "ls-tree", "-r", "--name-only"]:
            observed_refs.append(args[-1])
            return SimpleNamespace(stdout="README.md\n")
        if args[:2] == ["git", "show"]:
            observed_refs.append(args[2].split(":", 1)[0])
            return SimpleNamespace(stdout="content\n")
        raise AssertionError(f"Unexpected git invocation: {args}")

    monkeypatch.setattr(subprocess, "run", fake_run)

    payload = GitHubRepoSource(source, store).sync()

    metadata = store.get_collection_metadata("code")
    persisted = metadata["sources"][0]
    assert payload["branches"] == ["release"]
    assert observed_refs == ["release", "release"]
    assert persisted["config"]["branches"] == ["main"]
    assert "_sync_branches" not in persisted


def test_video_sync_writes_transcript_and_markdown(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    store = make_store(tmp_path)
    store.create_collection_key("media")
    source = store.add_collection_source(
        "media",
        "video",
        source_id="video-cxqrkt1gynq",
        title="https://www.youtube.com/watch?v=cxqRKt1GYNQ&t=1405s",
        config={"url": "https://www.youtube.com/watch?v=cxqRKt1GYNQ&t=1405s", "languages": ["en"]},
        update_command="sync",
        delete_command="del",
    )

    class Snippet:
        def __init__(self, text: str, start: float, duration: float) -> None:
            self.text = text
            self.start = start
            self.duration = duration

    class Transcript:
        language = "English"
        language_code = "en"
        is_generated = True

        def __iter__(self):
            return iter(
                [
                    Snippet("Hello world", 0.32, 4.0),
                    Snippet("Second line", 5.1, 3.0),
                ]
            )

    class FakeApi:
        def fetch(self, video_id: str, languages: list[str]):
            assert video_id == "cxqRKt1GYNQ"
            assert languages == ["en"]
            return Transcript()

    def fake_get(_url: str, **_kwargs: object) -> DummyResponse:
        return DummyResponse(payload={"title": "Agent video", "author_name": "OpenAI"})

    monkeypatch.setattr("knowledge.sources.video.YouTubeTranscriptApi", FakeApi)
    monkeypatch.setattr("knowledge.sources.video.requests.get", fake_get)

    payload = VideoSource(source, store).sync()

    assert payload["segments"] == 2
    transcript_payload = json.loads((store.source_raw_dir(source) / "transcript.json").read_text(encoding="utf-8"))
    metadata_payload = json.loads((store.source_raw_dir(source) / "metadata.json").read_text(encoding="utf-8"))
    raw_files = [path.name for path in store.source_raw_dir(source).iterdir() if path.is_file()]
    assert sorted(raw_files) == ["metadata.json", "transcript.json"]
    assert transcript_payload["video_id"] == "cxqRKt1GYNQ"
    assert transcript_payload["author_name"] == "OpenAI"
    assert len(transcript_payload["segments"]) == 2
    assert transcript_payload["segments"][0]["text"] == "Hello world"
    assert metadata_payload["title"] == "Agent video"


def test_video_sync_removes_stale_raw_video_files(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    store = make_store(tmp_path)
    store.create_collection_key("media")
    source = store.add_collection_source(
        "media",
        "video",
        source_id="video-cxqrkt1gynq",
        title="https://www.youtube.com/watch?v=cxqRKt1GYNQ&t=1405s",
        config={"url": "https://www.youtube.com/watch?v=cxqRKt1GYNQ&t=1405s", "languages": ["en"]},
        update_command="sync",
        delete_command="del",
    )
    raw_dir = store.source_raw_dir(source)
    (raw_dir / "transcript.json").write_text("{}", encoding="utf-8")
    (raw_dir / "metadata.json").write_text("{}", encoding="utf-8")
    (raw_dir / "transcript.txt").write_text("old", encoding="utf-8")

    class Snippet:
        def __init__(self, text: str, start: float, duration: float) -> None:
            self.text = text
            self.start = start
            self.duration = duration

    class Transcript:
        language = "English"
        language_code = "en"
        is_generated = True

        def __iter__(self):
            return iter([Snippet("Hello world", 0.0, 4.0)])

    class FakeApi:
        def fetch(self, _video_id: str, languages: list[str]):
            assert languages == ["en"]
            return Transcript()

    def fake_get(_url: str, **_kwargs: object) -> DummyResponse:
        return DummyResponse(payload={"title": "Agent video", "author_name": "OpenAI"})

    monkeypatch.setattr("knowledge.sources.video.YouTubeTranscriptApi", FakeApi)
    monkeypatch.setattr("knowledge.sources.video.requests.get", fake_get)

    VideoSource(source, store).sync()

    assert sorted(path.name for path in raw_dir.iterdir()) == ["metadata.json", "transcript.json"]


def test_television_sync_writes_channel_bundle(tmp_path: Path) -> None:
    store = make_store(tmp_path)
    store.create_collection_key("automation")
    source = store.add_collection_source(
        "automation",
        "television",
        source_id="television-knowledge-sources",
        title="knowledge-sources",
        config={
            "channel": "knowledge-sources",
            "description": "Browse registered sources",
            "source_command": "know list sources --key automation --json",
            "preview_command": "know export --key automation",
            "action_command": "know sync --key automation",
        },
        update_command="know sync television knowledge-sources --key automation",
        delete_command="know del --key automation television-knowledge-sources",
    )

    payload = TelevisionSource(source, store).sync()

    channel_file = store.source_raw_dir(source) / "knowledge-sources.toml"
    manifest_file = store.source_raw_dir(source) / "commands.json"
    readme_file = store.source_raw_dir(source) / "README.md"
    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))

    assert payload["files"] == 3
    assert channel_file.exists()
    assert manifest_file.exists()
    assert readme_file.exists()
    channel_text = channel_file.read_text(encoding="utf-8")
    assert 'name = "knowledge-sources"' in channel_text
    assert 'command = "know list sources --key automation --json"' in channel_text
    assert 'ctrl-o = "actions:open"' in channel_text
    assert manifest["commands"]["run_after_install"] == "tv knowledge-sources"
    assert "install_unix" in manifest["commands"]


def test_site_sync_fetches_single_page_without_crawl4ai(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    store = make_store(tmp_path)
    store.create_collection_key("sites")
    source = store.add_collection_source(
        "sites",
        "site",
        title="https://openai.com/index/harness-engineering/",
        config={"url": "https://openai.com/index/harness-engineering/", "max_depth": 1, "max_pages": 1},
        update_command="sync",
        delete_command="del",
    )

    class Response:
        text = (
            "<html><head><title>Harness Engineering</title></head>"
            "<body><article><h1>Harness Engineering</h1><p>Evaluation systems for AI.</p></article></body></html>"
        )
        headers = {"Content-Type": "text/html; charset=utf-8"}

        def raise_for_status(self) -> None:
            return None

    def fake_get(url: str, **kwargs: object) -> Response:
        assert url == "https://openai.com/index/harness-engineering/"
        assert kwargs["timeout"] == 60
        return Response()

    monkeypatch.setattr("knowledge.sources.crawl4ai_site.requests.get", fake_get)
    payload = SiteSource(source, store).sync()

    assert payload["pages"] == 1
    page_md = (
        store.source_raw_dir(source) / "pages" / "openai.com_index_harness-engineering.md"
    ).read_text(encoding="utf-8")
    page_json = json.loads((store.source_raw_dir(source) / "pages.json").read_text(encoding="utf-8"))
    assert "Harness Engineering" in page_md
    assert "Evaluation systems for AI." in page_md
    assert page_json[0]["title"] == "Harness Engineering"


def test_site_sync_falls_back_to_readable_proxy_after_403(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import requests

    store = make_store(tmp_path)
    store.create_collection_key("sites")
    source = store.add_collection_source(
        "sites",
        "site",
        title="https://openai.com/index/harness-engineering/",
        config={"url": "https://openai.com/index/harness-engineering/"},
        update_command="sync",
        delete_command="del",
    )

    class ForbiddenResponse:
        status_code = 403
        headers = {"Content-Type": "text/html; charset=utf-8"}
        text = ""

        def raise_for_status(self) -> None:
            raise requests.HTTPError("403 Client Error", response=self)

    class ProxyResponse:
        headers = {"Content-Type": "text/plain; charset=utf-8"}
        text = (
            "Title: Harness engineering: leveraging Codex in an agent-first world\n\n"
            "URL Source: http://openai.com/index/harness-engineering/\n\n"
            "Markdown Content:\n"
            "# Harness engineering\n\n"
            "Agent-first workflows.\n"
        )

        def raise_for_status(self) -> None:
            return None

    calls: list[str] = []

    def fake_get(url: str, **_kwargs: object):
        calls.append(url)
        if url == "https://openai.com/index/harness-engineering/":
            return ForbiddenResponse()
        if url == "https://r.jina.ai/http://openai.com/index/harness-engineering/":
            return ProxyResponse()
        raise AssertionError(url)

    monkeypatch.setattr("knowledge.sources.crawl4ai_site.requests.get", fake_get)
    payload = SiteSource(source, store).sync()

    assert payload["pages"] == 1
    assert calls == [
        "https://openai.com/index/harness-engineering/",
        "https://r.jina.ai/http://openai.com/index/harness-engineering/",
    ]
    page_md = (
        store.source_raw_dir(source) / "pages" / "openai.com_index_harness-engineering.md"
    ).read_text(encoding="utf-8")
    assert "Title: Harness engineering: leveraging Codex in an agent-first world" in page_md


def test_google_releases_sync_writes_feed_manifest_and_entry_markdown(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    store = make_store(tmp_path)
    store.create_collection_key("cloud")
    source = store.add_collection_source(
        "cloud",
        "google_releases",
        title="https://docs.cloud.google.com/feeds/gcp-release-notes.xml",
        config={"url": "https://docs.cloud.google.com/feeds/gcp-release-notes.xml"},
        update_command="sync",
        delete_command="del",
    )

    feed_payload = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <title>March 24, 2026</title>
    <id>tag:google.com,2016:gcp-release-notes#March_24_2026</id>
    <updated>2026-03-24T00:00:00-07:00</updated>
    <link rel="alternate" href="https://docs.cloud.google.com/release-notes#March_24_2026"/>
    <content type="html"><![CDATA[
      <h2 class="release-note-product-title">Cloud Monitoring</h2>
      <h3>Feature</h3>
      <p>Telemetry API quotas were updated.</p>
      <table>
        <tr><th>Old</th><th>New</th></tr>
        <tr><td>30k</td><td>60k</td></tr>
      </table>
    ]]></content>
  </entry>
</feed>
"""

    def fake_get(_url: str, **kwargs: object) -> DummyResponse:
        assert kwargs["timeout"] == 60
        return DummyResponse(text=feed_payload)

    monkeypatch.setattr("knowledge.sources.google_releases.requests.get", fake_get)
    payload = GoogleReleasesSource(source, store).sync()

    assert payload["entries"] == 1
    raw_dir = store.source_raw_dir(source)
    assert (raw_dir / "feed.xml").exists()
    manifest = json.loads((raw_dir / "entries.json").read_text(encoding="utf-8"))
    entry_file = raw_dir / "entries" / "march-24-2026.md"
    contents = entry_file.read_text(encoding="utf-8")
    assert manifest[0]["products"] == ["Cloud Monitoring"]
    assert "# March 24, 2026" in contents
    assert "## Cloud Monitoring" in contents
    assert "| Old | New |" in contents


def test_export_google_releases_only_writes_entry_documents(tmp_path: Path) -> None:
    store = make_store(tmp_path)
    store.create_collection_key("cloud")
    source = store.add_collection_source(
        "cloud",
        "google_releases",
        title="https://docs.cloud.google.com/feeds/gcp-release-notes.xml",
        config={"url": "https://docs.cloud.google.com/feeds/gcp-release-notes.xml"},
        update_command="sync",
        delete_command="del",
    )
    raw_dir = store.source_raw_dir(source)
    raw_dir.joinpath("feed.xml").write_text("<feed/>\n", encoding="utf-8")
    raw_dir.joinpath("entries.json").write_text("[]\n", encoding="utf-8")
    entries_dir = raw_dir / "entries"
    entries_dir.mkdir(parents=True, exist_ok=True)
    entries_dir.joinpath("march-24-2026.md").write_text(
        "---\n"
        "title: March 24, 2026\n"
        "products:\n"
        "  - Cloud Monitoring\n"
        "---\n\n"
        "# March 24, 2026\n",
        encoding="utf-8",
    )

    result = export_source(store, source)

    assert result["files"] == 1
    assert (store.source_library_dir(source) / "entries" / "march-24-2026.md").exists()
    assert not (store.source_library_dir(source) / "feed.xml.md").exists()
    assert not (store.source_library_dir(source) / "entries.json.md").exists()


def test_export_preserves_distinct_outputs_for_same_stem(tmp_path: Path) -> None:
    store = make_store(tmp_path)
    store.create_collection_key("media")
    source = store.add_collection_source(
        "media",
        "video",
        source_id="video-cxqrkt1gynq",
        title="https://www.youtube.com/watch?v=cxqRKt1GYNQ&t=1405s",
        config={"url": "https://www.youtube.com/watch?v=cxqRKt1GYNQ&t=1405s"},
        update_command="sync",
        delete_command="del",
    )
    raw_dir = store.source_raw_dir(source)
    (raw_dir / "transcript.json").write_text(
        json.dumps(
            {
                "video_id": "cxqRKt1GYNQ",
                "url": "https://www.youtube.com/watch?v=cxqRKt1GYNQ&t=1405s",
                "title": "Markdown transcript",
                "author_name": "OpenAI",
                "language": "English",
                "language_code": "en",
                "is_generated": True,
                "segments": [{"text": "Hello", "start": 0.0, "duration": 1.0}],
            }
        ),
        encoding="utf-8",
    )
    (raw_dir / "metadata.json").write_text(json.dumps({"title": "Markdown transcript"}), encoding="utf-8")
    (raw_dir / "transcript.txt").write_text("plain transcript\n", encoding="utf-8")

    result = export_source(store, source)

    assert result["files"] == 1
    assert (store.source_library_dir(source) / "transcript.md").exists()
    assert not (store.source_library_dir(source) / "transcript.txt.md").exists()


def test_export_merges_markdown_frontmatter_metadata(tmp_path: Path) -> None:
    store = make_store(tmp_path)
    store.create_collection_key("media")
    source = store.add_collection_source(
        "media",
        "video",
        source_id="video-cxqrkt1gynq",
        title="https://www.youtube.com/watch?v=cxqRKt1GYNQ&t=1405s",
        config={"url": "https://www.youtube.com/watch?v=cxqRKt1GYNQ&t=1405s"},
        update_command="sync",
        delete_command="del",
    )
    raw_dir = store.source_raw_dir(source)
    raw_dir.joinpath("transcript.json").write_text(
        json.dumps(
            {
                "title": "Agent video",
                "video_id": "cxqRKt1GYNQ",
                "url": "https://www.youtube.com/watch?v=cxqRKt1GYNQ&t=1405s",
                "author_name": "OpenAI",
                "language": "English",
                "language_code": "en",
                "is_generated": True,
                "segments": [{"text": "Hello world", "start": 0.0, "duration": 4.0}],
            }
        ),
        encoding="utf-8",
    )
    raw_dir.joinpath("metadata.json").write_text(
        json.dumps({"title": "Agent video", "channel": "OpenAI"}),
        encoding="utf-8",
    )

    export_source(store, source)

    exported = (store.source_library_dir(source) / "transcript.md").read_text(encoding="utf-8")
    assert exported.startswith("---\n")
    assert "knowledge_key: media" in exported
    assert "video_id: cxqRKt1GYNQ" in exported
    assert "author_name: OpenAI" in exported
    assert "# Agent video" in exported
    assert "source_metadata:" in exported


def test_export_ignores_invalid_embedded_frontmatter(tmp_path: Path) -> None:
    store = make_store(tmp_path)
    store.create_collection_key("docs")
    source = store.add_collection_source(
        "docs",
        "github",
        title="https://github.com/example/repo.git",
        config={"repo_url": "https://github.com/example/repo.git", "branches": ["main"]},
        update_command="sync",
        delete_command="del",
    )
    raw_file = store.source_raw_dir(source) / "main" / "bad.md"
    raw_file.parent.mkdir(parents=True, exist_ok=True)
    raw_file.write_text(
        "---\n"
        "title: [Component Name] - Technical Documentation\n"
        "---\n\n"
        "# Template\n",
        encoding="utf-8",
    )

    result = export_source(store, source)
    exported = (store.source_library_dir(source) / "main" / "bad.md").read_text(encoding="utf-8")

    assert result["files"] == 1
    assert "source_id:" in exported
    assert "title: https://github.com/example/repo.git" in exported
    assert "title: [Component Name] - Technical Documentation" in exported
    assert "knowledge_key: docs" in exported


def test_export_clears_stale_video_library_files(tmp_path: Path) -> None:
    store = make_store(tmp_path)
    store.create_collection_key("media")
    source = store.add_collection_source(
        "media",
        "video",
        source_id="video-cxqrkt1gynq",
        title="https://www.youtube.com/watch?v=cxqRKt1GYNQ&t=1405s",
        config={"url": "https://www.youtube.com/watch?v=cxqRKt1GYNQ&t=1405s"},
        update_command="sync",
        delete_command="del",
    )
    raw_dir = store.source_raw_dir(source)
    library_dir = store.source_library_dir(source)
    (raw_dir / "transcript.json").write_text(
        json.dumps(
            {
                "video_id": "cxqRKt1GYNQ",
                "url": "https://www.youtube.com/watch?v=cxqRKt1GYNQ&t=1405s",
                "title": "Markdown transcript",
                "author_name": "OpenAI",
                "language": "English",
                "language_code": "en",
                "is_generated": True,
                "segments": [{"text": "Hello", "start": 0.0, "duration": 1.0}],
            }
        ),
        encoding="utf-8",
    )
    (raw_dir / "metadata.json").write_text(json.dumps({"title": "Markdown transcript"}), encoding="utf-8")
    (library_dir / "transcript.txt.md").write_text("stale\n", encoding="utf-8")
    (library_dir / "metadata.json.md").write_text("stale\n", encoding="utf-8")

    result = export_source(store, source)

    assert result["files"] == 1
    assert (library_dir / "transcript.md").exists()
    assert not (library_dir / "transcript.txt.md").exists()
    assert not (library_dir / "metadata.json.md").exists()


def test_export_arxiv_only_writes_single_paper_document(tmp_path: Path) -> None:
    store = make_store(tmp_path)
    store.create_collection_key("papers")
    source = store.add_collection_source(
        "papers",
        "arxiv",
        title="https://arxiv.org/abs/1706.03762",
        config={"url": "https://arxiv.org/abs/1706.03762"},
        update_command="sync",
        delete_command="del",
    )
    raw_dir = store.source_raw_dir(source)
    raw_dir.joinpath("paper.xml").write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <id>http://arxiv.org/abs/1706.03762v7</id>
    <updated>2023-08-02T17:54:18Z</updated>
    <published>2017-06-12T17:57:25Z</published>
    <title>Attention Is All You Need</title>
    <summary>Transformer paper summary.</summary>
    <author><name>Ashish Vaswani</name></author>
    <category term="cs.CL" />
    <link rel="alternate" href="http://arxiv.org/abs/1706.03762v7" />
    <link title="pdf" href="http://arxiv.org/pdf/1706.03762v7" />
  </entry>
</feed>
""",
        encoding="utf-8",
    )
    raw_dir.joinpath("source-url.txt").write_text("https://arxiv.org/abs/1706.03762\n", encoding="utf-8")

    result = export_source(store, source)

    exported = (store.source_library_dir(source) / "paper.md").read_text(encoding="utf-8")
    assert result["files"] == 1
    assert (store.source_library_dir(source) / "paper.md").exists()
    assert not (store.source_library_dir(source) / "source-url.txt.md").exists()
    assert "paper_id: '1706.03762'" in exported or "paper_id: 1706.03762" in exported
    assert "source_url: https://arxiv.org/abs/1706.03762" in exported
    assert "# Attention Is All You Need" in exported
    assert "## Summary" in exported


def test_export_site_only_writes_page_documents_with_sidecar_metadata(tmp_path: Path) -> None:
    store = make_store(tmp_path)
    store.create_collection_key("sites")
    source = store.add_collection_source(
        "sites",
        "site",
        title="https://openai.com/index/harness-engineering/",
        config={"url": "https://openai.com/index/harness-engineering/"},
        update_command="sync",
        delete_command="del",
    )
    raw_dir = store.source_raw_dir(source)
    pages_dir = raw_dir / "pages"
    pages_dir.mkdir(parents=True, exist_ok=True)
    page_path = pages_dir / "openai.com_index_harness-engineering.md"
    page_path.write_text("# Harness Engineering\n", encoding="utf-8")
    page_path.with_suffix(".json").write_text(
        json.dumps(
            {
                "url": "https://openai.com/index/harness-engineering/",
                "title": "Harness engineering: leveraging Codex in an agent-first world",
                "metadata": {"fetched_via": "r.jina.ai"},
            }
        ),
        encoding="utf-8",
    )
    raw_dir.joinpath("pages.json").write_text("[]\n", encoding="utf-8")

    result = export_source(store, source)

    exported = (store.source_library_dir(source) / "pages" / "openai.com_index_harness-engineering.md").read_text(
        encoding="utf-8"
    )
    assert result["files"] == 1
    assert "title: 'Harness engineering: leveraging Codex in an agent-first world'" in exported
    assert "url: https://openai.com/index/harness-engineering/" in exported
    assert "source_metadata:" in exported
    assert not (store.source_library_dir(source) / "pages.json.md").exists()


# ── Strip YAML frontmatter and source markdown body ─────────────────────


def test_strip_yaml_frontmatter_removes_header():
    from knowledge.commands import _strip_yaml_frontmatter

    text = "---\ntitle: Hello\ndate: 2026-01-01\n---\n\n# Content\n\nBody text."
    result = _strip_yaml_frontmatter(text)
    assert result.startswith("# Content")
    assert "title:" not in result


def test_strip_yaml_frontmatter_no_frontmatter():
    from knowledge.commands import _strip_yaml_frontmatter

    text = "# Just markdown\n\nNo frontmatter."
    result = _strip_yaml_frontmatter(text)
    assert result == text


def test_strip_yaml_frontmatter_incomplete():
    from knowledge.commands import _strip_yaml_frontmatter

    text = "---\ntitle: Hello\nno closing delimiter"
    result = _strip_yaml_frontmatter(text)
    assert result == text


def test_read_source_markdown_body(tmp_path: Path):
    from knowledge.commands import _read_source_markdown_body
    from knowledge.store import KnowledgeStore

    store = KnowledgeStore(tmp_path)
    store.initialize()
    store.create_collection_key("mykey")
    source = {
        "id": "src-1",
        "type": "confluence",
        "key": "mykey",
        "title": "Test",
    }
    src_dir = store.source_dir(source)
    (src_dir / "page1.md").write_text(
        "---\ntitle: Page One\n---\n\n# Page One\n\nContent A.\n",
        encoding="utf-8",
    )
    (src_dir / "page2.md").write_text(
        "# Page Two\n\nContent B.\n",
        encoding="utf-8",
    )
    result = _read_source_markdown_body(store, source)
    assert "# Page One" in result
    assert "Content A." in result
    assert "# Page Two" in result
    assert "Content B." in result
    assert "title: Page One" not in result


def test_read_source_markdown_body_no_md_files(tmp_path: Path):
    from knowledge.commands import _read_source_markdown_body
    from knowledge.store import KnowledgeStore

    store = KnowledgeStore(tmp_path)
    store.initialize()
    store.create_collection_key("mykey")
    source = {
        "id": "src-2",
        "type": "confluence",
        "key": "mykey",
        "title": "Empty",
    }
    src_dir = store.source_dir(source)
    (src_dir / "data.json").write_text("{}", encoding="utf-8")
    result = _read_source_markdown_body(store, source)
    assert result is None


def test_find_selected_source():
    from knowledge.commands import _find_selected_source

    sources = [
        {"id": "a", "type": "confluence"},
        {"id": "b", "type": "jira"},
    ]
    assert _find_selected_source(sources, "b | jira")["id"] == "b"
    assert _find_selected_source(sources, None)["id"] == "a"
    assert _find_selected_source(sources, "nonexistent")["id"] == "a"
    assert _find_selected_source([], "anything") is None
