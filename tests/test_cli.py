from __future__ import annotations

import json
import tomllib
from pathlib import Path
from zipfile import ZipFile

import pytest
import yaml

from knowledge.cli import main


def test_init_creates_store(tmp_path: Path) -> None:
    assert main(["--store", str(tmp_path), "init"]) == 0
    assert (tmp_path / "config.yaml").exists()
    assert (tmp_path / "keys.yaml").exists()
    assert (tmp_path / "exports").exists()


def test_add_key_creates_metadata_and_directories(tmp_path: Path) -> None:
    assert main(["--store", str(tmp_path), "add", "key", "product-docs"]) == 0

    metadata = yaml.safe_load((tmp_path / "product-docs" / "metadata.yaml").read_text(encoding="utf-8"))
    assert metadata["name"] == "product-docs"
    assert metadata["commands"]["sync"] == "know sync --key product-docs"
    assert metadata["commands"]["export"] == "know export --key product-docs"
    assert (tmp_path / "product-docs" / "raw").exists()
    assert (tmp_path / "product-docs" / "library").exists()
    assert not (tmp_path / "product-docs" / "cache").exists()


def test_list_keys_returns_created_keys(tmp_path: Path, capsys) -> None:
    assert main(["--store", str(tmp_path), "add", "key", "alpha"]) == 0
    assert main(["--store", str(tmp_path), "add", "key", "beta"]) == 0

    assert main(["--store", str(tmp_path), "list", "keys"]) == 0
    output = capsys.readouterr().out
    assert '"alpha"' in output
    assert '"beta"' in output


def test_set_credential_and_list_credentials_use_verb_object_shape(tmp_path: Path, capsys) -> None:
    assert main(["--store", str(tmp_path), "set", "credential", "jira_token", "secret"]) == 0

    capsys.readouterr()
    assert main(["--store", str(tmp_path), "list", "credentials"]) == 0
    output = capsys.readouterr().out
    assert '"jira_token"' in output


def test_top_level_key_command_is_not_available(tmp_path: Path, capsys) -> None:
    with pytest.raises(SystemExit) as excinfo:
        main(["--store", str(tmp_path), "key", "list"])
    assert excinfo.value.code == 2
    error = capsys.readouterr().err
    assert "invalid choice" in error


def test_add_confluence_registers_source_under_key(tmp_path: Path) -> None:
    assert main(["--store", str(tmp_path), "add", "key", "research"]) == 0
    assert (
        main(
            [
                "--store",
                str(tmp_path),
                "add",
                "confluence",
                "--space",
                "ENG",
                "--key",
                "research",
            ]
        )
        == 0
    )

    metadata = yaml.safe_load((tmp_path / "research" / "metadata.yaml").read_text(encoding="utf-8"))
    assert metadata["sources"][0]["type"] == "confluence"
    assert metadata["sources"][0]["config"]["space"] == "ENG"
    assert metadata["sources"][0]["update_command"] == "know sync confluence --space ENG --key research"
    assert not (tmp_path / "research" / "confluence" / "confluence-eng.yaml").exists()


def test_add_arxiv_registers_url_under_key(tmp_path: Path) -> None:
    assert main(["--store", str(tmp_path), "add", "key", "papers"]) == 0
    assert (
        main(
            [
                "--store",
                str(tmp_path),
                "add",
                "arxiv",
                "https://arxiv.org/abs/1706.03762",
                "--key",
                "papers",
            ]
        )
        == 0
    )

    metadata = yaml.safe_load((tmp_path / "papers" / "metadata.yaml").read_text(encoding="utf-8"))
    assert metadata["sources"][0]["type"] == "arxiv"
    assert metadata["sources"][0]["config"]["url"] == "https://arxiv.org/abs/1706.03762"
    assert metadata["sources"][0]["id"] == "arxiv-1706.03762"


def test_add_site_registers_url_under_key(tmp_path: Path) -> None:
    assert main(["--store", str(tmp_path), "add", "key", "sites"]) == 0
    assert (
        main(
            [
                "--store",
                str(tmp_path),
                "add",
                "site",
                "https://openai.com/index/harness-engineering/",
                "--key",
                "sites",
                "--max-depth",
                "2",
                "--max-pages",
                "5",
            ]
        )
        == 0
    )

    metadata = yaml.safe_load((tmp_path / "sites" / "metadata.yaml").read_text(encoding="utf-8"))
    assert metadata["sources"][0]["type"] == "site"
    assert metadata["sources"][0]["config"]["url"] == "https://openai.com/index/harness-engineering/"
    assert metadata["sources"][0]["config"]["max_depth"] == 2
    assert metadata["sources"][0]["config"]["max_pages"] == 5
    assert metadata["sources"][0]["id"] == "site-harness-engineering"


def test_add_video_registers_url_under_key(tmp_path: Path) -> None:
    assert main(["--store", str(tmp_path), "add", "key", "media"]) == 0
    assert (
        main(
            [
                "--store",
                str(tmp_path),
                "add",
                "video",
                "https://www.youtube.com/watch?v=cxqRKt1GYNQ&t=1405s",
                "--key",
                "media",
                "--language",
                "en",
            ]
        )
        == 0
    )

    metadata = yaml.safe_load((tmp_path / "media" / "metadata.yaml").read_text(encoding="utf-8"))
    assert metadata["sources"][0]["type"] == "video"
    assert metadata["sources"][0]["config"]["url"] == "https://www.youtube.com/watch?v=cxqRKt1GYNQ&t=1405s"
    assert metadata["sources"][0]["config"]["languages"] == ["en"]
    assert metadata["sources"][0]["id"] == "video-cxqrkt1gynq"


def test_add_github_repo_uses_repeatable_branch_flags(tmp_path: Path) -> None:
    assert main(["--store", str(tmp_path), "add", "key", "code"]) == 0
    assert (
        main(
            [
                "--store",
                str(tmp_path),
                "add",
                "github-repo",
                "https://github.com/example/repo.git",
                "--key",
                "code",
                "--branch",
                "main",
                "--branch",
                "dev",
            ]
        )
        == 0
    )

    metadata = yaml.safe_load((tmp_path / "code" / "metadata.yaml").read_text(encoding="utf-8"))
    assert metadata["sources"][0]["type"] == "github"
    assert metadata["sources"][0]["config"]["branches"] == ["main", "dev"]


def test_list_sources_filters_by_key(tmp_path: Path, capsys) -> None:
    assert main(["--store", str(tmp_path), "add", "key", "alpha"]) == 0
    assert main(["--store", str(tmp_path), "add", "key", "beta"]) == 0
    assert main(["--store", str(tmp_path), "add", "confluence", "--space", "ENG", "--key", "alpha"]) == 0
    assert main(["--store", str(tmp_path), "add", "arxiv", "https://arxiv.org/abs/1234.5678", "--key", "beta"]) == 0

    capsys.readouterr()
    assert main(["--store", str(tmp_path), "list", "sources", "--key", "alpha"]) == 0
    output = capsys.readouterr().out
    assert '"key": "alpha"' in output
    assert '"confluence"' in output
    assert '"beta"' not in output


def test_search_confluence_lists_possible_sources(tmp_path: Path, capsys) -> None:
    assert main(["--store", str(tmp_path), "add", "key", "alpha"]) == 0
    assert main(["--store", str(tmp_path), "add", "key", "beta"]) == 0
    assert main(["--store", str(tmp_path), "add", "confluence", "--space", "ENG", "--key", "alpha"]) == 0
    assert main(["--store", str(tmp_path), "add", "confluence", "--space", "OPS", "--key", "beta"]) == 0

    assert main(["--store", str(tmp_path), "search", "confluence", "incident postmortem"]) == 0
    output = capsys.readouterr().out
    assert '"query": "incident postmortem"' in output
    assert '"space": "ENG"' in output
    assert '"space": "OPS"' in output


def test_search_confluence_honors_time_filters(tmp_path: Path, capsys) -> None:
    assert main(["--store", str(tmp_path), "add", "key", "alpha"]) == 0
    assert main(["--store", str(tmp_path), "add", "key", "beta"]) == 0
    assert main(["--store", str(tmp_path), "add", "confluence", "--space", "ENG", "--key", "alpha"]) == 0
    assert main(["--store", str(tmp_path), "add", "confluence", "--space", "OPS", "--key", "beta"]) == 0

    alpha_metadata = yaml.safe_load((tmp_path / "alpha" / "metadata.yaml").read_text(encoding="utf-8"))
    beta_metadata = yaml.safe_load((tmp_path / "beta" / "metadata.yaml").read_text(encoding="utf-8"))
    alpha_metadata["sources"][0]["updated_at"] = "2026-03-20T12:00:00+00:00"
    beta_metadata["sources"][0]["last_synced_at"] = "2026-03-23T09:30:00Z"
    (tmp_path / "alpha" / "metadata.yaml").write_text(yaml.safe_dump(alpha_metadata, sort_keys=False), encoding="utf-8")
    (tmp_path / "beta" / "metadata.yaml").write_text(yaml.safe_dump(beta_metadata, sort_keys=False), encoding="utf-8")

    capsys.readouterr()
    assert (
        main(
            [
                "--store",
                str(tmp_path),
                "search",
                "confluence",
                "incident postmortem",
                "--start-time",
                "2026-03-21T00:00:00+00:00",
                "--end-time",
                "2026-03-23T10:00:00+00:00",
            ]
        )
        == 0
    )
    output = capsys.readouterr().out
    assert '"start_time": "2026-03-21T00:00:00+00:00"' in output
    assert '"end_time": "2026-03-23T10:00:00+00:00"' in output
    assert '"space": "OPS"' in output
    assert '"space": "ENG"' not in output


def test_search_arxiv_queries_public_api(tmp_path: Path, capsys, monkeypatch) -> None:
    import requests

    atom_payload = """<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom"
      xmlns:opensearch="http://a9.com/-/spec/opensearch/1.1/">
  <opensearch:totalResults>1</opensearch:totalResults>
  <opensearch:startIndex>0</opensearch:startIndex>
  <opensearch:itemsPerPage>5</opensearch:itemsPerPage>
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
"""

    class StubResponse:
        text = atom_payload

        def raise_for_status(self) -> None:
            return None

    def fake_get(url: str, *, params: dict[str, object], headers: dict[str, str], timeout: int) -> StubResponse:
        assert url == "https://export.arxiv.org/api/query"
        assert params["search_query"] == 'all:"attention is all you need"'
        assert params["start"] == 0
        assert params["max_results"] == 5
        assert params["sortBy"] == "submittedDate"
        assert params["sortOrder"] == "descending"
        assert headers["Accept"] == "application/atom+xml"
        assert timeout == 60
        return StubResponse()

    monkeypatch.setattr(requests, "get", fake_get)

    assert (
        main(
            [
                "--store",
                str(tmp_path),
                "search",
                "arxiv",
                "attention is all you need",
                "--max-results",
                "5",
                "--sort-by",
                "submittedDate",
            ]
        )
        == 0
    )
    output = capsys.readouterr().out
    assert '"query": "attention is all you need"' in output
    assert '"total_results": 1' in output
    assert '"title": "Attention Is All You Need"' in output
    assert '"pdf_url": "http://arxiv.org/pdf/1706.03762v7"' in output


def test_sync_by_key_exports_matching_source_stats(tmp_path: Path, monkeypatch) -> None:
    assert main(["--store", str(tmp_path), "add", "key", "research"]) == 0
    assert main(["--store", str(tmp_path), "add", "arxiv", "https://arxiv.org/abs/1706.03762", "--key", "research"]) == 0

    import knowledge.registry as registry_module
    from knowledge.sources.arxiv import ArxivSource

    class StubArxivSource(ArxivSource):
        def sync(self) -> dict[str, object]:
            self.write_text(self.raw_dir / "paper.xml", "<feed/>")
            return self.finalize_sync({"paper_id": "1706.03762", "raw_dir": str(self.raw_dir)})

    monkeypatch.setitem(registry_module.SOURCE_TYPES, "arxiv", StubArxivSource)

    assert main(["--store", str(tmp_path), "sync", "--key", "research"]) == 0
    metadata = yaml.safe_load((tmp_path / "research" / "metadata.yaml").read_text(encoding="utf-8"))
    assert metadata["sources"][0]["last_synced_at"]
    assert (tmp_path / "research" / "raw" / "arxiv" / "arxiv-1706.03762" / "paper.xml").exists()


def test_sync_site_by_url_exports_matching_source_stats(tmp_path: Path, monkeypatch) -> None:
    assert main(["--store", str(tmp_path), "add", "key", "sites"]) == 0
    assert (
        main(
            [
                "--store",
                str(tmp_path),
                "add",
                "site",
                "https://openai.com/index/harness-engineering/",
                "--key",
                "sites",
            ]
        )
        == 0
    )

    import knowledge.registry as registry_module

    class StubSiteSource:
        def __init__(self, source: dict[str, object], _store) -> None:
            self.source = source
            self._store = _store
            self.raw_dir = _store.source_raw_dir(source)

        def sync(self) -> dict[str, object]:
            (self.raw_dir / "pages").mkdir(parents=True, exist_ok=True)
            (self.raw_dir / "pages" / "openai.com_index_harness-engineering.md").write_text(
                "# Harness Engineering\n", encoding="utf-8"
            )
            self.source["last_synced_at"] = "2026-03-22T00:00:00+00:00"
            self._store.update_collection_source(self.source)
            return {"key": "sites", "source": self.source["id"], "pages": 1}

    monkeypatch.setitem(registry_module.SOURCE_TYPES, "site", StubSiteSource)

    assert (
        main(
            [
                "--store",
                str(tmp_path),
                "sync",
                "site",
                "https://openai.com/index/harness-engineering/",
                "--key",
                "sites",
            ]
        )
        == 0
    )
    metadata = yaml.safe_load((tmp_path / "sites" / "metadata.yaml").read_text(encoding="utf-8"))
    assert metadata["sources"][0]["last_synced_at"]
    assert (
        tmp_path / "sites" / "raw" / "site" / "site-harness-engineering" / "pages" / "openai.com_index_harness-engineering.md"
    ).exists()


def test_sync_github_repo_honors_branch_override_without_rewriting_metadata(tmp_path: Path, monkeypatch) -> None:
    assert main(["--store", str(tmp_path), "add", "key", "code"]) == 0
    assert (
        main(
            [
                "--store",
                str(tmp_path),
                "add",
                "github-repo",
                "https://github.com/example/repo.git",
                "--key",
                "code",
                "--branch",
                "main",
            ]
        )
        == 0
    )

    import knowledge.registry as registry_module

    observed: dict[str, object] = {}

    class StubGitHubRepoSource:
        def __init__(self, source: dict[str, object], store) -> None:
            observed["source"] = source
            self.source = source
            self.store = store

        def sync(self) -> dict[str, object]:
            self.source["last_synced_at"] = "2026-03-23T00:00:00+00:00"
            persisted = {key: value for key, value in self.source.items() if not key.startswith("_")}
            self.store.update_collection_source(persisted)
            return {
                "key": "code",
                "source": self.source["id"],
                "branches": self.source.get("_sync_branches"),
            }

    monkeypatch.setitem(registry_module.SOURCE_TYPES, "github", StubGitHubRepoSource)

    assert (
        main(
            [
                "--store",
                str(tmp_path),
                "sync",
                "github-repo",
                "https://github.com/example/repo.git",
                "--key",
                "code",
                "--branch",
                "release",
            ]
        )
        == 0
    )

    metadata = yaml.safe_load((tmp_path / "code" / "metadata.yaml").read_text(encoding="utf-8"))
    source = metadata["sources"][0]
    assert observed["source"]["_sync_branches"] == ["release"]
    assert source["config"]["branches"] == ["main"]
    assert "_sync_branches" not in source


def test_export_generates_frontmatter_and_zip_archive(tmp_path: Path, capsys) -> None:
    assert main(["--store", str(tmp_path), "add", "key", "sample"]) == 0
    assert main(["--store", str(tmp_path), "add", "arxiv", "https://arxiv.org/abs/1706.03762", "--key", "sample"]) == 0

    raw_file = tmp_path / "sample" / "raw" / "arxiv" / "arxiv-1706.03762" / "paper.txt"
    raw_file.parent.mkdir(parents=True, exist_ok=True)
    raw_file.write_text("Attention Is All You Need\n", encoding="utf-8")

    capsys.readouterr()
    assert main(["--store", str(tmp_path), "export", "--key", "sample"]) == 0
    output = json.loads(capsys.readouterr().out)
    archive_path = Path(output["archive"])
    assert archive_path.exists()

    exported = (
        tmp_path / "sample" / "library" / "arxiv" / "arxiv-1706.03762" / "paper.md"
    ).read_text(encoding="utf-8")
    assert exported.startswith("---\n")
    assert "knowledge_key: sample" in exported
    assert "source_id: arxiv-1706.03762" in exported

    with ZipFile(archive_path) as archive:
        assert "sample/metadata.yaml" in archive.namelist()


def test_import_merges_metadata_from_archive(tmp_path: Path) -> None:
    source_store = tmp_path / "source-store"
    target_store = tmp_path / "target-store"

    assert main(["--store", str(source_store), "add", "key", "docs"]) == 0
    assert main(["--store", str(source_store), "add", "confluence", "--space", "ENG", "--key", "docs"]) == 0
    assert main(["--store", str(source_store), "export", "--key", "docs"]) == 0

    exports = sorted((source_store / "exports").glob("*.zip"))
    archive = exports[-1]

    assert main(["--store", str(target_store), "add", "key", "docs"]) == 0
    assert main(["--store", str(target_store), "add", "arxiv", "https://arxiv.org/abs/1706.03762", "--key", "docs"]) == 0
    assert main(["--store", str(target_store), "import", str(archive)]) == 0

    metadata = yaml.safe_load((target_store / "docs" / "metadata.yaml").read_text(encoding="utf-8"))
    source_ids = {source["id"] for source in metadata["sources"]}
    assert "confluence-eng" in source_ids
    assert "arxiv-1706.03762" in source_ids


def test_pyproject_exposes_know_console_script() -> None:
    pyproject = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
    scripts = pyproject["project"]["scripts"]
    assert scripts["know"] == "knowledge.cli:main"
