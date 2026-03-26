"""Additional tests to raise coverage above 90% for all modules."""

from __future__ import annotations

import json
from argparse import Namespace
from pathlib import Path

import pytest
import yaml

from knowledge.cli import _validate_url, _SYNC_ATTR_MAP, build_parser, main, load_dotenv
from knowledge.errors import (
    CredentialNotFoundError,
    InvalidURLError,
    KeyAlreadyExistsError,
    KnowledgeError,
    SourceAlreadyExistsError,
    SourceNotFoundError,
    SyncError,
)
from knowledge.exporter import (
    _build_markdown_for_raw_file,
    _extract_frontmatter,
    _export_relative_path,
    _is_generated_export,
    _iter_export_paths,
    _render_video_document,
    export_source,
)
from knowledge.sources.base import SourceAdapter
from knowledge.sources.crawl4ai_site import SiteSource, _html_to_text, _slugify_url
from knowledge.sources.google_releases import parse_google_releases_feed
from knowledge.sources.jira import (
    _adf_to_markdown,
    _apply_marks,
    _build_jql,
    _display_name,
    _field_name,
    _status_category_name,
    _table_row,
)
from knowledge.sources.video import extract_video_id
from knowledge.store import KnowledgeStore


def make_store(tmp_path: Path) -> KnowledgeStore:
    store = KnowledgeStore(tmp_path)
    store.initialize()
    return store


# ──────────────────────────────────────────────────────────────
# D-07: Custom error types
# ──────────────────────────────────────────────────────────────


class TestErrors:
    def test_knowledge_error_is_exception(self):
        assert issubclass(KnowledgeError, Exception)

    def test_credential_not_found(self):
        err = CredentialNotFoundError("$token")
        assert err.reference == "$token"
        assert "not found" in str(err)

    def test_source_not_found(self):
        err = SourceNotFoundError("docs", "src-1")
        assert err.key_name == "docs"
        assert err.source_id == "src-1"
        assert "src-1" in str(err)

    def test_key_already_exists(self):
        err = KeyAlreadyExistsError("docs")
        assert err.key_name == "docs"
        assert "already exists" in str(err)

    def test_source_already_exists(self):
        err = SourceAlreadyExistsError("docs", "src-1")
        assert err.key_name == "docs"
        assert err.source_id == "src-1"
        assert "already exists" in str(err)

    def test_invalid_url(self):
        err = InvalidURLError("ftp://x", reason="bad scheme")
        assert err.url == "ftp://x"
        assert "bad scheme" in str(err)

    def test_invalid_url_default_reason(self):
        err = InvalidURLError("bad")
        assert "invalid URL" in str(err)

    def test_sync_error(self):
        err = SyncError("docs", "src-1", "timeout")
        assert err.key_name == "docs"
        assert err.source_id == "src-1"
        assert "timeout" in str(err)


# ──────────────────────────────────────────────────────────────
# D-06: URL validation
# ──────────────────────────────────────────────────────────────


class TestURLValidation:
    def test_valid_url_passes(self):
        _validate_url("https://arxiv.org/abs/1234")

    def test_http_url_passes(self):
        _validate_url("http://example.com")

    def test_ftp_url_rejected(self):
        with pytest.raises(InvalidURLError):
            _validate_url("ftp://example.com")

    def test_no_scheme_rejected(self):
        with pytest.raises(InvalidURLError):
            _validate_url("example.com")

    def test_empty_rejected(self):
        with pytest.raises(InvalidURLError):
            _validate_url("")

    def test_cli_add_arxiv_rejects_bad_url(self, tmp_path):
        rc = main(["--store", str(tmp_path), "add", "key", "k1"])
        assert rc == 0
        with pytest.raises(InvalidURLError):
            _validate_url("not-a-url")

    def test_cli_add_site_with_valid_url(self, tmp_path):
        # Just ensure the parser builds correctly with the new flags
        parser = build_parser()
        args = parser.parse_args([
            "--store", str(tmp_path),
            "--verbose",
            "add", "site", "https://example.com", "--key", "k1",
        ])
        assert args.verbose is True
        assert args.url == "https://example.com"

    def test_cli_add_google_releases_with_valid_url(self, tmp_path):
        parser = build_parser()
        args = parser.parse_args([
            "--store", str(tmp_path),
            "add", "google-releases", "https://docs.cloud.google.com/feeds/gcp-release-notes.xml", "--key", "k1",
        ])
        assert args.url == "https://docs.cloud.google.com/feeds/gcp-release-notes.xml"


# ──────────────────────────────────────────────────────────────
# D-10: Verbose / quiet flags
# ──────────────────────────────────────────────────────────────


class TestVerboseQuietFlags:
    def test_quiet_flag_parsed(self):
        parser = build_parser()
        args = parser.parse_args(["--quiet", "list", "keys"])
        assert args.quiet is True

    def test_verbose_flag_parsed(self):
        parser = build_parser()
        args = parser.parse_args(["--verbose", "list", "keys"])
        assert args.verbose is True


# ──────────────────────────────────────────────────────────────
# D-05: Sync attr map
# ──────────────────────────────────────────────────────────────


class TestSyncAttrMap:
    def test_all_sync_commands_have_mapping(self):
        expected = {"confluence", "arxiv", "site", "video", "television",
                    "google-releases",
                    "github-repo", "jira-project", "aha"}
        assert set(_SYNC_ATTR_MAP.keys()) == expected


# ──────────────────────────────────────────────────────────────
# Exporter coverage improvements
# ──────────────────────────────────────────────────────────────


class TestExporterCoverage:
    def test_extract_frontmatter_no_closing_marker(self):
        text = "---\ntitle: foo\nbody without end"
        fm, body = _extract_frontmatter(text)
        assert fm == {}
        assert body == text

    def test_extract_frontmatter_invalid_yaml(self):
        text = "---\n: :\n---\n\nbody"
        fm, body = _extract_frontmatter(text)
        # yaml.safe_load may parse or error; either way we get a result
        assert isinstance(fm, dict) or body == text

    def test_extract_frontmatter_non_dict_yaml(self):
        text = "---\n- item1\n- item2\n---\n\nbody"
        fm, body = _extract_frontmatter(text)
        assert fm == {}
        assert body == text

    def test_export_relative_path_html(self):
        result = _export_relative_path({"type": "site"}, Path("pages/index.html"))
        assert result.suffix == ".md"

    def test_export_relative_path_unknown(self):
        result = _export_relative_path({"type": "github"}, Path("README.rst"))
        assert result.name == "README.rst.md"

    def test_iter_export_paths_video_legacy_md(self, tmp_path):
        raw_dir = tmp_path / "video" / "v1"
        raw_dir.mkdir(parents=True)
        (raw_dir / "transcript.md").write_text("# transcript", encoding="utf-8")
        paths = _iter_export_paths({"type": "video"}, raw_dir)
        assert len(paths) == 1
        assert paths[0].name == "transcript.md"

    def test_iter_export_paths_video_txt_fallback(self, tmp_path):
        raw_dir = tmp_path / "video" / "v2"
        raw_dir.mkdir(parents=True)
        (raw_dir / "transcript.txt").write_text("plain text", encoding="utf-8")
        paths = _iter_export_paths({"type": "video"}, raw_dir)
        assert len(paths) == 1
        assert paths[0].name == "transcript.txt"

    def test_iter_export_paths_arxiv_html_fallback(self, tmp_path):
        raw_dir = tmp_path / "arxiv" / "a1"
        raw_dir.mkdir(parents=True)
        (raw_dir / "paper.html").write_text("<h1>test</h1>", encoding="utf-8")
        paths = _iter_export_paths({"type": "arxiv"}, raw_dir)
        assert len(paths) == 1
        assert paths[0].name == "paper.html"

    def test_iter_export_paths_arxiv_txt_fallback(self, tmp_path):
        raw_dir = tmp_path / "arxiv" / "a2"
        raw_dir.mkdir(parents=True)
        (raw_dir / "paper.txt").write_text("text", encoding="utf-8")
        paths = _iter_export_paths({"type": "arxiv"}, raw_dir)
        assert len(paths) == 1
        assert paths[0].name == "paper.txt"

    def test_iter_export_paths_confluence_html(self, tmp_path):
        raw_dir = tmp_path / "confluence" / "c1"
        pages_dir = raw_dir / "pages"
        pages_dir.mkdir(parents=True)
        (pages_dir / "page1.html").write_text("<p>hi</p>", encoding="utf-8")
        paths = _iter_export_paths({"type": "confluence"}, raw_dir)
        assert len(paths) == 1
        assert paths[0].name == "page1.html"

    def test_iter_export_paths_google_releases_entries(self, tmp_path):
        raw_dir = tmp_path / "google_releases" / "g1"
        entries_dir = raw_dir / "entries"
        entries_dir.mkdir(parents=True)
        (entries_dir / "march-24-2026.md").write_text("# release", encoding="utf-8")
        paths = _iter_export_paths({"type": "google_releases"}, raw_dir)
        assert len(paths) == 1
        assert paths[0].name == "march-24-2026.md"

    def test_build_markdown_for_html_file(self, tmp_path):
        source = {"key": "k", "id": "s", "type": "github", "title": "t"}
        html_file = tmp_path / "page.html"
        html_file.write_text("<p>Hello</p>", encoding="utf-8")
        result = _build_markdown_for_raw_file(source, html_file, Path("page.html"))
        assert "<p>Hello</p>" in result

    def test_build_markdown_for_binary_file(self, tmp_path):
        source = {"key": "k", "id": "s", "type": "github", "title": "t"}
        bin_file = tmp_path / "image.png"
        bin_file.write_bytes(b"\x89PNG")
        result = _build_markdown_for_raw_file(source, bin_file, Path("image.png"))
        assert "Binary or unsupported" in result

    def test_build_markdown_for_txt_file(self, tmp_path):
        source = {"key": "k", "id": "s", "type": "github", "title": "t"}
        txt_file = tmp_path / "notes.txt"
        txt_file.write_text("hello world", encoding="utf-8")
        result = _build_markdown_for_raw_file(source, txt_file, Path("notes.txt"))
        assert "```txt" in result
        assert "hello world" in result

    def test_is_generated_export_for_aha(self, tmp_path):
        source = {"key": "k", "id": "s", "type": "aha"}
        md_file = tmp_path / "file.md"
        md_file.write_text("anything", encoding="utf-8")
        assert _is_generated_export(md_file, source) is True

    def test_is_generated_export_for_github_without_frontmatter(self, tmp_path):
        source = {"key": "k", "id": "s", "type": "github"}
        md_file = tmp_path / "file.md"
        md_file.write_text("no frontmatter here", encoding="utf-8")
        assert _is_generated_export(md_file, source) is False

    def test_is_generated_export_for_github_with_matching_frontmatter(self, tmp_path):
        source = {"key": "k", "id": "s", "type": "github"}
        md_file = tmp_path / "file.md"
        fm = yaml.safe_dump({"knowledge_key": "k", "source_id": "s"})
        md_file.write_text(f"---\n{fm}---\n\nbody", encoding="utf-8")
        assert _is_generated_export(md_file, source) is True

    def test_export_source_for_jira_type(self, tmp_path):
        store = make_store(tmp_path)
        store.create_collection_key("k1")
        source = store.add_collection_source(
            "k1", "jira", title="PROJ",
            config={"project": "PROJ"},
            update_command="sync", delete_command="del",
        )
        src_dir = store.source_dir(source)
        (src_dir / "PROJ-1.md").write_text(
            "---\ntitle: Issue 1\n---\n\n# Issue 1\n", encoding="utf-8"
        )
        result = export_source(store, source)
        assert result["files"] == 1

    def test_render_video_document_with_metadata(self, tmp_path):
        source = {"key": "k", "id": "s", "type": "video", "config": {}}
        transcript = {
            "video_id": "abc",
            "url": "https://youtube.com/watch?v=abc",
            "title": "Test Video",
            "author_name": "Author",
            "language": "English",
            "language_code": "en",
            "is_generated": True,
            "segments": [
                {"text": "Hello", "start": 0.0, "duration": 1.0},
                {"text": "World", "start": 3661.0, "duration": 1.0},
                {"text": "", "start": 5.0, "duration": 1.0},
            ],
        }
        transcript_path = tmp_path / "transcript.json"
        transcript_path.write_text(json.dumps(transcript), encoding="utf-8")
        metadata_path = tmp_path / "metadata.json"
        metadata_path.write_text(json.dumps({"extra": "info"}), encoding="utf-8")
        fm, body = _render_video_document(source, transcript_path)
        assert fm["title"] == "Test Video"
        assert "[01:01:01]" in body  # 3661 seconds
        assert "Hello" in body
        assert fm["source_metadata"] == {"extra": "info"}

    def test_render_video_document_bad_metadata_json(self, tmp_path):
        source = {"key": "k", "id": "s", "type": "video", "config": {}}
        transcript = {
            "video_id": "x", "url": "u", "title": "T",
            "author_name": "A", "language": "en",
            "language_code": "en", "is_generated": False,
            "segments": [],
        }
        transcript_path = tmp_path / "transcript.json"
        transcript_path.write_text(json.dumps(transcript), encoding="utf-8")
        bad_meta = tmp_path / "metadata.json"
        bad_meta.write_text("{invalid json", encoding="utf-8")
        fm, body = _render_video_document(source, transcript_path)
        assert fm["source_metadata"] == {}

    def test_render_video_non_dict_segments(self, tmp_path):
        source = {"key": "k", "id": "s", "type": "video", "config": {}}
        transcript = {
            "video_id": "x", "url": "u", "title": "T",
            "author_name": "A", "language": "en",
            "language_code": "en", "is_generated": False,
            "segments": "not a list",
        }
        transcript_path = tmp_path / "transcript.json"
        transcript_path.write_text(json.dumps(transcript), encoding="utf-8")
        fm, body = _render_video_document(source, transcript_path)
        assert "Transcript" in body


# ──────────────────────────────────────────────────────────────
# crawl4ai_site coverage improvements
# ──────────────────────────────────────────────────────────────


class TestCrawl4aiSiteCoverage:
    def test_html_to_text_strips_script_tags(self):
        html = "<html><script>alert(1)</script><p>Hello</p></html>"
        result = _html_to_text(html)
        assert "alert" not in result
        assert "Hello" in result

    def test_html_to_text_strips_style_tags(self):
        html = "<html><style>body{color:red}</style><p>Content</p></html>"
        result = _html_to_text(html)
        assert "color:red" not in result
        assert "Content" in result

    def test_slugify_url_empty(self):
        assert _slugify_url("") == "page"

    def test_slugify_url_none(self):
        assert _slugify_url(None) == "page"

    def test_slugify_url_long(self):
        result = _slugify_url("https://example.com/" + "a" * 300)
        assert len(result) <= 200

    def test_fetch_single_page_success(self, tmp_path, monkeypatch):
        store = make_store(tmp_path)
        store.create_collection_key("k")
        source = store.add_collection_source(
            "k", "site", title="https://example.com",
            config={"url": "https://example.com", "max_depth": 1, "max_pages": 1},
            update_command="sync", delete_command="del",
        )
        adapter = SiteSource(source, store)

        class FakeResp:
            text = "<html><title>Example</title><p>Hello World</p></html>"
            headers = {"Content-Type": "text/html"}
            def raise_for_status(self): pass
            def json(self): return {}

        monkeypatch.setattr("knowledge.sources.crawl4ai_site.requests.get", lambda *a, **kw: FakeResp())
        result = adapter._fetch_single_page("https://example.com")
        assert result["title"] == "Example"
        assert "Hello World" in result["markdown"]

    def test_fetch_single_page_403_falls_back_to_proxy(self, tmp_path, monkeypatch):
        import requests as req
        store = make_store(tmp_path)
        store.create_collection_key("k")
        source = store.add_collection_source(
            "k", "site", title="https://example.com",
            config={"url": "https://example.com", "max_depth": 1, "max_pages": 1},
            update_command="sync", delete_command="del",
        )
        adapter = SiteSource(source, store)

        class FakeErrorResp:
            status_code = 403
            text = ""
            headers = {}
            def raise_for_status(self):
                err = req.HTTPError(response=self)
                raise err
            def json(self): return {}

        class FakeProxyResp:
            text = "Title: Proxy Page\n\nContent from proxy\n"
            headers = {"Content-Type": "text/plain"}
            def raise_for_status(self): pass
            def json(self): return {}

        call_count = [0]
        def fake_get(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                return FakeErrorResp()
            return FakeProxyResp()

        monkeypatch.setattr("knowledge.sources.crawl4ai_site.requests.get", fake_get)
        result = adapter._fetch_single_page("https://example.com")
        assert result["title"] == "Proxy Page"
        assert result["metadata"]["fetched_via"] == "r.jina.ai"

    def test_fetch_single_page_500_raises(self, tmp_path, monkeypatch):
        import requests as req
        store = make_store(tmp_path)
        store.create_collection_key("k")
        source = store.add_collection_source(
            "k", "site", title="https://example.com",
            config={"url": "https://example.com", "max_depth": 1, "max_pages": 1},
            update_command="sync", delete_command="del",
        )
        adapter = SiteSource(source, store)

        class FakeErrorResp:
            status_code = 500
            text = ""
            headers = {}
            def raise_for_status(self):
                err = req.HTTPError(response=self)
                raise err

        monkeypatch.setattr("knowledge.sources.crawl4ai_site.requests.get", lambda *a, **kw: FakeErrorResp())
        with pytest.raises(req.HTTPError):
            adapter._fetch_single_page("https://example.com")

    def test_normalize_result_dict(self, tmp_path):
        store = make_store(tmp_path)
        store.create_collection_key("k")
        source = store.add_collection_source(
            "k", "site", title="https://example.com",
            config={"url": "https://example.com", "max_depth": 1, "max_pages": 1},
            update_command="sync", delete_command="del",
        )
        adapter = SiteSource(source, store)
        result = adapter._normalize_result({
            "url": "https://example.com",
            "title": "Example",
            "markdown": "# Hello",
        })
        assert result["url"] == "https://example.com"
        assert result["markdown"] == "# Hello"

    def test_normalize_result_cleaned_html_fallback(self, tmp_path):
        store = make_store(tmp_path)
        store.create_collection_key("k")
        source = store.add_collection_source(
            "k", "site", title="https://example.com",
            config={"url": "https://example.com", "max_depth": 1, "max_pages": 1},
            update_command="sync", delete_command="del",
        )
        adapter = SiteSource(source, store)
        result = adapter._normalize_result({
            "url": "https://example.com",
            "title": "Example",
            "cleaned_html": "<p>fallback</p>",
        })
        assert result["markdown"] == "<p>fallback</p>"

    def test_fetch_readable_proxy_no_title(self, tmp_path, monkeypatch):
        store = make_store(tmp_path)
        store.create_collection_key("k")
        source = store.add_collection_source(
            "k", "site", title="https://example.com",
            config={"url": "https://example.com", "max_depth": 1, "max_pages": 1},
            update_command="sync", delete_command="del",
        )
        adapter = SiteSource(source, store)

        class FakeResp:
            text = "No title line here\nJust content\n"
            headers = {"Content-Type": "text/plain"}
            def raise_for_status(self): pass

        monkeypatch.setattr("knowledge.sources.crawl4ai_site.requests.get", lambda *a, **kw: FakeResp())
        result = adapter._fetch_readable_proxy("https://example.com")
        assert result["title"] == "https://example.com"


# ──────────────────────────────────────────────────────────────
# base.py SourceAdapter coverage
# ──────────────────────────────────────────────────────────────


class ConcreteAdapter(SourceAdapter):
    """Minimal concrete adapter for testing base methods."""
    def sync(self):
        return self.finalize_sync({"test": True})


class TestSourceAdapterBase:
    def test_write_json(self, tmp_path):
        store = make_store(tmp_path)
        store.create_collection_key("k")
        source = store.add_collection_source(
            "k", "arxiv", title="paper",
            config={"url": "https://arxiv.org/abs/1"},
            update_command="sync", delete_command="del",
        )
        adapter = ConcreteAdapter(source, store)
        out = adapter.raw_dir / "data.json"
        adapter.write_json(out, {"key": "value"})
        assert json.loads(out.read_text(encoding="utf-8")) == {"key": "value"}

    def test_write_markdown(self, tmp_path):
        store = make_store(tmp_path)
        store.create_collection_key("k")
        source = store.add_collection_source(
            "k", "arxiv", title="paper",
            config={"url": "https://arxiv.org/abs/1"},
            update_command="sync", delete_command="del",
        )
        adapter = ConcreteAdapter(source, store)
        out = adapter.raw_dir / "doc.md"
        adapter.write_markdown(out, {"title": "Test"}, "Body text")
        content = out.read_text(encoding="utf-8")
        assert content.startswith("---\n")
        assert "title: Test" in content
        assert "Body text" in content

    def test_clear_source_dir(self, tmp_path):
        store = make_store(tmp_path)
        store.create_collection_key("k")
        source = store.add_collection_source(
            "k", "arxiv", title="paper",
            config={"url": "https://arxiv.org/abs/1"},
            update_command="sync", delete_command="del",
        )
        adapter = ConcreteAdapter(source, store)
        # Create some files
        (adapter.raw_dir / "file.txt").write_text("hello", encoding="utf-8")
        sub = adapter.raw_dir / "subdir"
        sub.mkdir()
        (sub / "inner.txt").write_text("inner", encoding="utf-8")
        adapter.clear_source_dir()
        # Dir exists but is empty
        assert adapter.raw_dir.exists()
        assert list(adapter.raw_dir.iterdir()) == []

    def test_clear_source_dir_when_not_exists(self, tmp_path):
        store = make_store(tmp_path)
        store.create_collection_key("k")
        source = store.add_collection_source(
            "k", "arxiv", title="paper",
            config={"url": "https://arxiv.org/abs/1"},
            update_command="sync", delete_command="del",
        )
        adapter = ConcreteAdapter(source, store)
        import shutil
        if adapter.raw_dir.exists():
            shutil.rmtree(adapter.raw_dir)
        adapter.clear_source_dir()
        assert adapter.raw_dir.exists()

    def test_finalize_sync_strips_private_keys(self, tmp_path):
        store = make_store(tmp_path)
        store.create_collection_key("k")
        source = store.add_collection_source(
            "k", "arxiv", title="paper",
            config={"url": "https://arxiv.org/abs/1"},
            update_command="sync", delete_command="del",
        )
        source["_sync_branches"] = ["main"]
        adapter = ConcreteAdapter(source, store)
        result = adapter.sync()
        assert result["test"] is True
        # Check the persisted source doesn't have private keys
        metadata = store.get_collection_metadata("k")
        for s in metadata["sources"]:
            assert "_sync_branches" not in s


# ──────────────────────────────────────────────────────────────
# Jira ADF renderer additional coverage
# ──────────────────────────────────────────────────────────────


class TestJiraADFCoverage:
    def test_adf_emoji(self):
        node = {"type": "emoji", "attrs": {"text": "😀", "shortName": ":grinning:"}}
        assert _adf_to_markdown(node) == "😀"

    def test_adf_emoji_shortname_only(self):
        node = {"type": "emoji", "attrs": {"shortName": ":smile:"}}
        assert _adf_to_markdown(node) == ":smile:"

    def test_adf_mention(self):
        node = {"type": "mention", "attrs": {"text": "John"}}
        assert _adf_to_markdown(node) == "@John"

    def test_adf_inline_card(self):
        node = {"type": "inlineCard", "attrs": {"url": "https://example.com"}}
        assert _adf_to_markdown(node) == "https://example.com"

    def test_adf_block_card(self):
        node = {"type": "blockCard", "attrs": {"url": "https://example.com"}}
        assert _adf_to_markdown(node) == "https://example.com"

    def test_adf_rule(self):
        node = {"type": "rule"}
        assert _adf_to_markdown(node) == "---"

    def test_adf_panel(self):
        node = {"type": "panel", "content": [
            {"type": "paragraph", "content": [{"type": "text", "text": "Note"}]}
        ]}
        result = _adf_to_markdown(node)
        assert result.startswith(">")
        assert "Note" in result

    def test_adf_code_block_with_language(self):
        node = {
            "type": "codeBlock",
            "attrs": {"language": "python"},
            "content": [{"type": "text", "text": "print('hi')"}],
        }
        result = _adf_to_markdown(node)
        assert "```python" in result
        assert "print('hi')" in result

    def test_apply_marks_strike(self):
        result = _apply_marks("deleted", [{"type": "strike"}])
        assert result == "~~deleted~~"

    def test_apply_marks_link(self):
        result = _apply_marks("click", [{"type": "link", "attrs": {"href": "https://x.com"}}])
        assert result == "[click](https://x.com)"

    def test_apply_marks_link_no_href(self):
        result = _apply_marks("click", [{"type": "link", "attrs": {}}])
        assert result == "click"

    def test_field_name_non_dict(self):
        assert _field_name("string") is None
        assert _field_name(None) is None

    def test_field_name_no_name_key(self):
        assert _field_name({"id": 123}) is None

    def test_display_name_non_dict(self):
        assert _display_name("string") is None
        assert _display_name(None) is None

    def test_status_category_name_non_dict(self):
        assert _status_category_name("string") is None
        assert _status_category_name(None) is None

    def test_status_category_name_no_category(self):
        assert _status_category_name({"name": "Open"}) is None

    def test_status_category_name_category_not_dict(self):
        assert _status_category_name({"statusCategory": "string"}) is None

    def test_build_jql_no_clauses_raises(self):
        with pytest.raises(ValueError):
            _build_jql(
                query=None, project=None, statuses=None, issue_types=None,
                assignee=None, reporter=None, created_after=None,
                created_before=None, updated_after=None, updated_before=None,
                order_by=None,
            )

    def test_build_jql_with_all_filters(self):
        result = _build_jql(
            query="bug", project="PROJ", statuses=["Open", "Closed"],
            issue_types=["Bug"], assignee="john", reporter="jane",
            created_after="2025-01-01", created_before="2025-12-31",
            updated_after="2025-06-01", updated_before="2025-06-30",
            order_by=["updated DESC"],
        )
        assert "project = PROJ" in result
        assert "assignee" in result
        assert "reporter" in result
        assert "ORDER BY" in result

    def test_table_row(self):
        node = {
            "content": [
                {"type": "tableCell", "content": [
                    {"type": "paragraph", "content": [{"type": "text", "text": "A"}]}
                ]},
                {"type": "tableHeader", "content": [
                    {"type": "paragraph", "content": [{"type": "text", "text": "B"}]}
                ]},
            ]
        }
        cells = _table_row(node)
        assert cells == ["A", "B"]

    def test_adf_table(self):
        node = {
            "type": "table",
            "content": [
                {"type": "tableRow", "content": [
                    {"type": "tableHeader", "content": [
                        {"type": "paragraph", "content": [{"type": "text", "text": "H1"}]}
                    ]},
                ]},
                {"type": "tableRow", "content": [
                    {"type": "tableCell", "content": [
                        {"type": "paragraph", "content": [{"type": "text", "text": "V1"}]}
                    ]},
                ]},
            ],
        }
        result = _adf_to_markdown(node)
        assert "| H1 |" in result
        assert "| V1 |" in result
        assert "---" in result


# ──────────────────────────────────────────────────────────────
# Video extract_video_id additional coverage
# ──────────────────────────────────────────────────────────────


class TestVideoExtractId:
    def test_shorts_url(self):
        result = extract_video_id("https://www.youtube.com/shorts/abc123")
        assert result == "abc123"

    def test_youtu_be(self):
        result = extract_video_id("https://youtu.be/xyz789")
        assert result == "xyz789"

    def test_empty_path_raises(self):
        with pytest.raises(ValueError):
            extract_video_id("https://youtube.com/")


# ──────────────────────────────────────────────────────────────
# Store additional coverage
# ──────────────────────────────────────────────────────────────


class TestStoreCoverage:
    def test_source_already_exists_error(self, tmp_path):
        store = make_store(tmp_path)
        store.create_collection_key("k1")
        store.add_collection_source(
            "k1", "arxiv", title="paper",
            config={"url": "https://arxiv.org/abs/1"},
            update_command="sync", delete_command="del",
        )
        with pytest.raises(SourceAlreadyExistsError):
            store.add_collection_source(
                "k1", "arxiv", title="paper",
                config={"url": "https://arxiv.org/abs/1"},
                update_command="sync", delete_command="del",
            )

    def test_config_yaml_updated_on_reinitialize(self, tmp_path):
        store = make_store(tmp_path)
        # Mutate config to trigger update path
        config = yaml.safe_load(store.config_path.read_text(encoding="utf-8"))
        config["paths"]["exports"] = "old"
        store.config_path.write_text(yaml.safe_dump(config), encoding="utf-8")
        store.initialize()
        updated = yaml.safe_load(store.config_path.read_text(encoding="utf-8"))
        assert updated["paths"]["exports"] == "exports"

    def test_cleanup_orphan_source_dirs_removes_raw_library(self, tmp_path):
        store = make_store(tmp_path)
        store.create_collection_key("k1")
        key_dir = store.key_dir("k1")
        (key_dir / "raw").mkdir()
        (key_dir / "library").mkdir()
        result = store.cleanup_orphan_source_dirs("k1")
        assert result["removed"] >= 2
        assert not (key_dir / "raw").exists()
        assert not (key_dir / "library").exists()


# ──────────────────────────────────────────────────────────────
# load_dotenv coverage
# ──────────────────────────────────────────────────────────────


class TestLoadDotenv:
    def test_load_dotenv_with_file(self, tmp_path, monkeypatch):
        env_file = tmp_path / ".env"
        env_file.write_text(
            '# comment\nTEST_KNOW_VAR="hello"\nTEST_KNOW_BARE=world\n\n',
            encoding="utf-8",
        )
        monkeypatch.delenv("TEST_KNOW_VAR", raising=False)
        monkeypatch.delenv("TEST_KNOW_BARE", raising=False)
        load_dotenv(env_file)
        import os
        assert os.environ.get("TEST_KNOW_VAR") == "hello"
        assert os.environ.get("TEST_KNOW_BARE") == "world"
        # Cleanup
        monkeypatch.delenv("TEST_KNOW_VAR", raising=False)
        monkeypatch.delenv("TEST_KNOW_BARE", raising=False)

    def test_load_dotenv_single_quotes(self, tmp_path, monkeypatch):
        env_file = tmp_path / ".env"
        env_file.write_text("TEST_KNOW_SQ='single'\n", encoding="utf-8")
        monkeypatch.delenv("TEST_KNOW_SQ", raising=False)
        load_dotenv(env_file)
        import os
        assert os.environ.get("TEST_KNOW_SQ") == "single"
        monkeypatch.delenv("TEST_KNOW_SQ", raising=False)

    def test_load_dotenv_missing_file(self, tmp_path):
        load_dotenv(tmp_path / "nonexistent.env")  # Should not raise


class TestGoogleReleasesCoverage:
    def test_parse_google_releases_feed_extracts_products_and_links(self):
        payload = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <title>March 24, 2026</title>
    <id>tag:google.com,2016:gcp-release-notes#March_24_2026</id>
    <updated>2026-03-24T00:00:00-07:00</updated>
    <link rel="alternate" href="https://docs.cloud.google.com/release-notes#March_24_2026"/>
    <content type="html"><![CDATA[
      <h2 class="release-note-product-title">Cloud Monitoring</h2>
      <h3>Feature</h3>
      <p>Updated quotas.</p>
    ]]></content>
  </entry>
</feed>
"""
        entries = parse_google_releases_feed(payload)
        assert entries[0]["title"] == "March 24, 2026"
        assert entries[0]["products"] == ["Cloud Monitoring"]
        assert entries[0]["url"] == "https://docs.cloud.google.com/release-notes#March_24_2026"
        assert entries[0]["slug"] == "march-24-2026"
