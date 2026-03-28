"""Tests for Brave Search CLI integration."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from knowledge.cli import build_parser, main
from knowledge.commands import cmd_search_brave
from knowledge.sources import brave as brave_module
from knowledge.television import format_brave_preview, format_brave_television


def test_search_brave_parser() -> None:
    parser = build_parser()
    args = parser.parse_args(["search", "brave", "openai codex", "--count", "3", "--format", "television"])
    assert args.query == "openai codex"
    assert args.count == 3
    assert args.format == "television"
    assert args.handler == cmd_search_brave


def test_search_brave_normalizes_web_results(monkeypatch: pytest.MonkeyPatch) -> None:
    payload = {
        "web": {
            "results": [
                {
                    "title": "OpenAI Codex",
                    "url": "https://openai.com/index/openai-codex/",
                    "description": "Agentic coding in the terminal.",
                }
            ]
        }
    }

    def fake_run(*args, **kwargs) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(args[0], 0, stdout=json.dumps(payload), stderr="")

    monkeypatch.setattr(brave_module.subprocess, "run", fake_run)

    results = brave_module.search_brave("openai codex", count=5)

    assert results["query"] == "openai codex"
    assert results["count"] == 5
    assert results["results"][0]["title"] == "OpenAI Codex"
    assert results["results"][0]["source"] == "openai.com"


def test_search_brave_reports_missing_bx(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_run(*args, **kwargs):
        raise FileNotFoundError("bx not found")

    monkeypatch.setattr(brave_module.subprocess, "run", fake_run)

    with pytest.raises(Exception, match="Brave Search CLI `bx` is not installed"):
        brave_module.search_brave("openai")


def test_format_brave_television_and_preview() -> None:
    results = [
        {
            "title": "OpenAI Codex",
            "source": "openai.com",
            "url": "https://openai.com/index/openai-codex/",
            "description": "Agentic coding in the terminal.",
        }
    ]

    tv = format_brave_television(results)
    preview = format_brave_preview(results, "OpenAI Codex | openai.com | https://openai.com/index/openai-codex/")

    assert "OpenAI Codex | openai.com | https://openai.com/index/openai-codex/" in tv
    assert "# OpenAI Codex" in preview
    assert "Agentic coding in the terminal." in preview


def test_search_brave_main_json_output(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys) -> None:
    payload = {
        "results": [
            {
                "title": "OpenAI Codex",
                "link": "https://openai.com/index/openai-codex/",
                "snippet": "Agentic coding in the terminal.",
            }
        ]
    }

    def fake_run(*args, **kwargs) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(args[0], 0, stdout=json.dumps(payload), stderr="")

    monkeypatch.setattr(brave_module.subprocess, "run", fake_run)

    assert main(["--store", str(tmp_path), "search", "brave", "openai codex", "--count", "1"]) == 0
    output = capsys.readouterr().out
    assert '"query": "openai codex"' in output
    assert '"title": "OpenAI Codex"' in output


def test_search_brave_main_supports_television(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys) -> None:
    payload = {
        "web": {
            "results": [
                {
                    "title": "OpenAI Codex",
                    "url": "https://openai.com/index/openai-codex/",
                    "description": "Agentic coding in the terminal.",
                }
            ]
        }
    }

    def fake_run(*args, **kwargs) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(args[0], 0, stdout=json.dumps(payload), stderr="")

    monkeypatch.setattr(brave_module.subprocess, "run", fake_run)

    assert main(["--store", str(tmp_path), "search", "brave", "openai codex", "--format", "television"]) == 0
    output = capsys.readouterr().out
    assert "OpenAI Codex | openai.com | https://openai.com/index/openai-codex/" in output


def test_search_brave_main_supports_preview(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys) -> None:
    payload = {
        "web": {
            "results": [
                {
                    "title": "OpenAI Codex",
                    "url": "https://openai.com/index/openai-codex/",
                    "description": "Agentic coding in the terminal.",
                }
            ]
        }
    }

    def fake_run(*args, **kwargs) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(args[0], 0, stdout=json.dumps(payload), stderr="")

    monkeypatch.setattr(brave_module.subprocess, "run", fake_run)

    assert (
        main(
            [
                "--store",
                str(tmp_path),
                "search",
                "brave",
                "openai codex",
                "--format",
                "television-preview",
                "--entry",
                "OpenAI Codex | openai.com | https://openai.com/index/openai-codex/",
            ]
        )
        == 0
    )
    output = capsys.readouterr().out
    assert "# OpenAI Codex" in output
    assert "## Summary" in output
