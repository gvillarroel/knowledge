"""Tests for the markdown transform utilities."""

from __future__ import annotations

from pathlib import Path

import pytest

from knowledge.transform.markdown import (
    _slugify,
    build_frontmatter,
    html_to_markdown,
    write_markdown_page,
)


def test_slugify_basic():
    assert _slugify("Hello World") == "hello-world"


def test_slugify_special_chars():
    assert _slugify("Hello, World! & More") == "hello-world-more"


def test_slugify_empty():
    assert _slugify("") == "untitled"


def test_slugify_leading_trailing_dashes():
    assert _slugify("--hello--") == "hello"


def test_build_frontmatter():
    fm = build_frontmatter({"title": "My Page", "source": "https://example.com"})
    assert fm.startswith("---\n")
    assert fm.endswith("---\n")
    assert "title: My Page" in fm
    assert "source: https://example.com" in fm


def test_html_to_markdown_basic():
    html = "<h1>Title</h1><p>Some text.</p>"
    md = html_to_markdown(html)
    assert "Title" in md
    assert "Some text" in md


def test_write_markdown_page(tmp_path):
    out = write_markdown_page(
        output_dir=tmp_path,
        title="Test Page",
        body="Hello, world!",
        meta={"source": "https://example.com", "key": "test"},
    )
    assert out.exists()
    content = out.read_text()
    assert content.startswith("---\n")
    assert "title: Test Page" in content
    assert "Hello, world!" in content


def test_write_markdown_page_custom_filename(tmp_path):
    out = write_markdown_page(
        output_dir=tmp_path,
        title="Any Title",
        body="body",
        meta={},
        filename="my-custom-file",
    )
    assert out.name == "my-custom-file.md"


def test_write_markdown_page_creates_dirs(tmp_path):
    deep = tmp_path / "a" / "b" / "c"
    out = write_markdown_page(
        output_dir=deep,
        title="Deep",
        body="content",
        meta={},
    )
    assert out.exists()
