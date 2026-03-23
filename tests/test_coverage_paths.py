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
from knowledge.sources.confluence import ConfluenceSource
from knowledge.sources.crawl4ai_site import SiteSource
from knowledge.sources.github_repo import GitHubRepoSource
from knowledge.sources.jira import JiraSource
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
    assert not (tmp_path / "docs" / "raw" / "confluence" / "confluence-eng").exists()
    assert not (tmp_path / "docs" / "library" / "confluence" / "confluence-eng").exists()


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


def test_filter_confluence_sources_by_time_bounds_uses_sync_or_update_timestamps() -> None:
    older = {
        "id": "confluence-eng",
        "updated_at": "2026-03-20T12:00:00+00:00",
    }
    newer = {
        "id": "confluence-ops",
        "last_synced_at": "2026-03-23T09:30:00+00:00",
        "updated_at": "2026-03-22T12:00:00+00:00",
    }

    filtered = commands._filter_confluence_sources_by_time_bounds(
        [older, newer],
        start_time="2026-03-21T00:00:00+00:00",
        end_time="2026-03-23T10:00:00+00:00",
    )

    assert [source["id"] for source in filtered] == ["confluence-ops"]


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
            "url": "https://arxiv.org/abs/1",
            "repo_url": "https://github.com/example/repo.git",
            "project": "PROD",
            "workspace": "ROADMAP",
            "product": "ROADMAP",
        },
    }
    assert commands._matches_source(source, "jira-prod")
    assert commands._matches_source(source, "ENG")
    assert commands._matches_source(source, "https://github.com/example/repo.git")
    assert commands._matches_source(source, "https://arxiv.org/abs/1")
    assert not commands._matches_source(source, "missing")


def test_parse_iso8601_supports_z_suffix() -> None:
    parsed = commands._parse_iso8601("2026-03-23T10:15:00Z")
    assert parsed is not None
    assert parsed.isoformat() == "2026-03-23T10:15:00+00:00"


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

    with pytest.raises(FileExistsError):
        store.create_collection_key("docs")
    with pytest.raises(FileNotFoundError):
        store.get_collection_metadata("missing")
    with pytest.raises(FileNotFoundError):
        store.delete_collection_source("docs", "missing")
    with pytest.raises(FileNotFoundError):
        store.import_archive(tmp_path / "missing.zip")

    store.set_key("token", "secret")
    assert store.resolve_key("$token") == "secret"
    assert store.resolve_key("plain") == "plain"
    with pytest.raises(KeyError):
        store.resolve_key("$missing")

    assert store._read_yaml(tmp_path / "absent.yaml", default={"fallback": True}) == {"fallback": True}
    assert store._source_id("jira", "!!!") == "jira-source"


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

    assert str(cache_dir).startswith(str(Path("/tmp").resolve()))
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
        archive.writestr("imported/raw/arxiv/arxiv-1234/paper.txt", "hello\n")

    payload = store.import_archive(archive_path)
    assert payload["imported_keys"] == ["imported"]
    assert payload["merged_sources"] == 1
    assert (tmp_path / "imported" / "raw" / "arxiv" / "arxiv-1234" / "paper.txt").exists()


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


def test_store_cleanup_orphan_source_dirs_removes_unregistered_raw_and_library(tmp_path: Path) -> None:
    store = make_store(tmp_path)
    store.create_collection_key("docs")
    orphan_raw = tmp_path / "docs" / "raw" / "site" / "site-old"
    orphan_library = tmp_path / "docs" / "library" / "site" / "site-old"
    orphan_raw.mkdir(parents=True, exist_ok=True)
    orphan_library.mkdir(parents=True, exist_ok=True)
    (orphan_raw / "pages.json").write_text("[]\n", encoding="utf-8")
    (orphan_library / "page.md").write_text("---\n---\n", encoding="utf-8")

    payload = store.cleanup_orphan_source_dirs("docs")

    assert payload == {"keys": 1, "removed": 2}
    assert not orphan_raw.exists()
    assert not orphan_library.exists()


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
    assert (store.source_raw_dir(source) / "pages" / "1.html").exists()


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
    issue_file = store.source_raw_dir(source) / "issues" / "PROD-1.json"
    assert json.loads(issue_file.read_text(encoding="utf-8"))["key"] == "PROD-1"


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
    transcript_md = (store.source_raw_dir(source) / "transcript.md").read_text(encoding="utf-8")
    raw_files = [path.name for path in store.source_raw_dir(source).iterdir() if path.is_file()]
    frontmatter = yaml.safe_load(transcript_md.split("---\n", 2)[1])
    assert raw_files == ["transcript.md"]
    assert transcript_md.startswith("---\n")
    assert frontmatter["video_id"] == "cxqRKt1GYNQ"
    assert frontmatter["author_name"] == "OpenAI"
    assert frontmatter["segment_count"] == 2
    assert "\n# Agent video\n" in transcript_md
    assert "[00:00] Hello world" in transcript_md


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

    assert sorted(path.name for path in raw_dir.iterdir()) == ["transcript.md"]


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
    (raw_dir / "transcript.md").write_text("# Markdown transcript\n", encoding="utf-8")
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
    raw_dir.joinpath("transcript.md").write_text(
        "---\n"
        "title: Agent video\n"
        "video_id: cxqRKt1GYNQ\n"
        "author_name: OpenAI\n"
        "---\n\n"
        "# Agent video\n",
        encoding="utf-8",
    )

    export_source(store, source)

    exported = (store.source_library_dir(source) / "transcript.md").read_text(encoding="utf-8")
    assert exported.startswith("---\n")
    assert "knowledge_key: media" in exported
    assert "video_id: cxqRKt1GYNQ" in exported
    assert "author_name: OpenAI" in exported
    assert "# Agent video" in exported
    assert exported.count("---\n") == 2


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
    (raw_dir / "transcript.md").write_text("# Markdown transcript\n", encoding="utf-8")
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
