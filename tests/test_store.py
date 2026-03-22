"""Tests for the knowledge store module."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

import knowledge.store as store_mod


@pytest.fixture(autouse=True)
def isolated_store(tmp_path, monkeypatch):
    """Redirect the store to a temporary directory for each test."""
    monkeypatch.setattr(store_mod, "KNOWLEDGE_DIR", tmp_path / ".knowledge")
    monkeypatch.setattr(store_mod, "SOURCES_FILE", tmp_path / ".knowledge" / "sources.yaml")
    monkeypatch.setattr(store_mod, "DATA_DIR", tmp_path / ".knowledge" / "data")
    yield


def test_empty_store():
    assert store_mod.list_sources() == []


def test_add_and_get_source():
    entry = {"key": "mysite", "type": "web", "url": "https://example.com"}
    store_mod.add_source(entry)
    result = store_mod.get_source("mysite")
    assert result is not None
    assert result["key"] == "mysite"
    assert result["url"] == "https://example.com"


def test_add_source_sets_added_at():
    entry = {"key": "ts", "type": "web", "url": "https://example.com"}
    store_mod.add_source(entry)
    saved = store_mod.get_source("ts")
    assert "added_at" in saved


def test_add_source_upserts():
    store_mod.add_source({"key": "k", "type": "web", "url": "https://a.com"})
    store_mod.add_source({"key": "k", "type": "web", "url": "https://b.com"})
    sources = store_mod.list_sources()
    assert len(sources) == 1
    assert sources[0]["url"] == "https://b.com"


def test_remove_source():
    store_mod.add_source({"key": "k", "type": "web", "url": "https://x.com"})
    removed = store_mod.remove_source("k")
    assert removed is True
    assert store_mod.get_source("k") is None


def test_remove_nonexistent_returns_false():
    assert store_mod.remove_source("ghost") is False


def test_list_sources_multiple():
    for i in range(3):
        store_mod.add_source({"key": f"s{i}", "type": "web", "url": f"https://site{i}.com"})
    assert len(store_mod.list_sources()) == 3


def test_source_data_dir_created(tmp_path, monkeypatch):
    data_dir = tmp_path / ".knowledge" / "data"
    monkeypatch.setattr(store_mod, "DATA_DIR", data_dir)
    result = store_mod.source_data_dir("mykey")
    assert result.exists()
    assert result == data_dir / "mykey"
