"""Tests for the CLI commands."""

from __future__ import annotations

from click.testing import CliRunner

import knowledge.store as store_mod
from knowledge.cli import main


def _setup_store(tmp_path, monkeypatch):
    monkeypatch.setattr(store_mod, "KNOWLEDGE_DIR", tmp_path / ".knowledge")
    monkeypatch.setattr(store_mod, "SOURCES_FILE", tmp_path / ".knowledge" / "sources.yaml")
    monkeypatch.setattr(store_mod, "DATA_DIR", tmp_path / ".knowledge" / "data")


def test_add_web_source(tmp_path, monkeypatch):
    _setup_store(tmp_path, monkeypatch)
    runner = CliRunner()
    result = runner.invoke(main, ["add", "mysite", "https://example.com", "--type", "web"])
    assert result.exit_code == 0, result.output
    assert "mysite" in result.output
    entry = store_mod.get_source("mysite")
    assert entry is not None
    assert entry["type"] == "web"


def test_add_github_source(tmp_path, monkeypatch):
    _setup_store(tmp_path, monkeypatch)
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["add", "myrepo", "https://github.com/org/repo", "--type", "github", "--branches", "main,dev"],
    )
    assert result.exit_code == 0, result.output
    entry = store_mod.get_source("myrepo")
    assert entry["branches"] == ["main", "dev"]


def test_list_empty(tmp_path, monkeypatch):
    _setup_store(tmp_path, monkeypatch)
    runner = CliRunner()
    result = runner.invoke(main, ["list"])
    assert result.exit_code == 0
    assert "No sources" in result.output


def test_list_sources(tmp_path, monkeypatch):
    _setup_store(tmp_path, monkeypatch)
    store_mod.add_source({"key": "s1", "type": "web", "url": "https://a.com"})
    store_mod.add_source({"key": "s2", "type": "github", "url": "https://github.com/o/r"})
    runner = CliRunner()
    result = runner.invoke(main, ["list"])
    assert result.exit_code == 0
    assert "s1" in result.output
    assert "s2" in result.output


def test_list_json(tmp_path, monkeypatch):
    _setup_store(tmp_path, monkeypatch)
    store_mod.add_source({"key": "j1", "type": "web", "url": "https://x.com"})
    runner = CliRunner()
    result = runner.invoke(main, ["list", "--json"])
    assert result.exit_code == 0
    import json
    data = json.loads(result.output)
    assert isinstance(data, list)
    assert data[0]["key"] == "j1"


def test_show_source(tmp_path, monkeypatch):
    _setup_store(tmp_path, monkeypatch)
    store_mod.add_source({"key": "show-me", "type": "web", "url": "https://example.com"})
    runner = CliRunner()
    result = runner.invoke(main, ["show", "show-me"])
    assert result.exit_code == 0
    assert "show-me" in result.output


def test_show_missing(tmp_path, monkeypatch):
    _setup_store(tmp_path, monkeypatch)
    runner = CliRunner()
    result = runner.invoke(main, ["show", "nope"])
    assert result.exit_code != 0


def test_remove_source(tmp_path, monkeypatch):
    _setup_store(tmp_path, monkeypatch)
    store_mod.add_source({"key": "bye", "type": "web", "url": "https://bye.com"})
    runner = CliRunner()
    result = runner.invoke(main, ["remove", "bye", "--yes"])
    assert result.exit_code == 0
    assert store_mod.get_source("bye") is None


def test_remove_missing(tmp_path, monkeypatch):
    _setup_store(tmp_path, monkeypatch)
    runner = CliRunner()
    result = runner.invoke(main, ["remove", "ghost", "--yes"])
    assert result.exit_code != 0


def test_export_no_data(tmp_path, monkeypatch):
    _setup_store(tmp_path, monkeypatch)
    store_mod.add_source({"key": "k", "type": "web", "url": "https://x.com"})
    runner = CliRunner()
    out_dir = tmp_path / "out"
    result = runner.invoke(main, ["export", "k", "--output", str(out_dir)])
    assert result.exit_code == 0
    assert "run 'knowledge update" in result.output


def test_export_with_data(tmp_path, monkeypatch):
    _setup_store(tmp_path, monkeypatch)
    store_mod.add_source({"key": "k", "type": "web", "url": "https://x.com"})
    # Manually create data
    data_dir = tmp_path / ".knowledge" / "data" / "k"
    data_dir.mkdir(parents=True)
    (data_dir / "page.md").write_text("---\ntitle: Page\n---\n\nContent\n")
    runner = CliRunner()
    out_dir = tmp_path / "out"
    result = runner.invoke(main, ["export", "k", "--output", str(out_dir)])
    assert result.exit_code == 0
    assert (out_dir / "k" / "page.md").exists()


def test_add_confluence_missing_params(tmp_path, monkeypatch):
    _setup_store(tmp_path, monkeypatch)
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["add", "cf", "https://x.atlassian.net/wiki", "--type", "confluence"],
    )
    assert result.exit_code != 0


def test_add_aha_source(tmp_path, monkeypatch):
    _setup_store(tmp_path, monkeypatch)
    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "add", "myaha", "https://myco.aha.io",
            "--type", "aha",
            "--subdomain", "myco",
            "--product-id", "PROD",
            "--token", "tok",
        ],
    )
    assert result.exit_code == 0, result.output
    entry = store_mod.get_source("myaha")
    assert entry["subdomain"] == "myco"
