"""Tests for Brave Search API integration."""

from __future__ import annotations

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


class _Resp:
    def __init__(self, payload: dict[str, object]) -> None:
        self._payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict[str, object]:
        return self._payload


def test_search_brave_normalizes_web_results(monkeypatch: pytest.MonkeyPatch) -> None:
    payload = {
        "web": {
            "results": [
                {
                    "title": "OpenAI Codex",
                    "url": "https://openai.com/index/openai-codex/",
                    "description": "Agentic coding in the terminal.",
                    "meta_url": {"hostname": "openai.com"},
                }
            ]
        },
        "query": {"more_results_available": True},
    }

    captured: dict[str, object] = {}

    def fake_get(url: str, *, params: dict[str, object], headers: dict[str, str], timeout: int) -> _Resp:
        captured["url"] = url
        captured["params"] = params
        captured["headers"] = headers
        captured["timeout"] = timeout
        return _Resp(payload)

    monkeypatch.setattr(brave_module.requests, "get", fake_get)

    results = brave_module.search_brave("openai codex", api_key="secret", count=5)

    assert results["query"] == "openai codex"
    assert results["count"] == 5
    assert results["more_results_available"] is True
    assert results["results"][0]["title"] == "OpenAI Codex"
    assert results["results"][0]["source"] == "openai.com"
    assert captured["url"] == brave_module._BRAVE_WEB_SEARCH_URL
    assert captured["params"] == {"q": "openai codex", "count": 5}
    assert captured["headers"]["X-Subscription-Token"] == "secret"


def test_search_brave_reports_api_failures(monkeypatch: pytest.MonkeyPatch) -> None:
    class _BadResp:
        def raise_for_status(self) -> None:
            raise brave_module.requests.HTTPError("boom")

    monkeypatch.setattr(brave_module.requests, "get", lambda *args, **kwargs: _BadResp())

    with pytest.raises(Exception, match="Brave Search API request failed"):
        brave_module.search_brave("openai", api_key="secret")


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
        "web": {
            "results": [
                {
                    "title": "OpenAI Codex",
                    "url": "https://openai.com/index/openai-codex/",
                    "description": "Agentic coding in the terminal.",
                    "meta_url": {"hostname": "openai.com"},
                }
            ]
        },
        "query": {"more_results_available": False},
    }

    monkeypatch.setenv("BRAVE_SEARCH_API_KEY", "secret")
    monkeypatch.setattr(brave_module.requests, "get", lambda *args, **kwargs: _Resp(payload))

    assert main(["--store", str(tmp_path), "search", "brave", "openai codex", "--count", "1"]) == 0
    output = capsys.readouterr().out
    assert '"query": "openai codex"' in output
    assert '"title": "OpenAI Codex"' in output
    assert '"more_results_available": false' in output


def test_search_brave_main_supports_television(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys) -> None:
    payload = {
        "web": {
            "results": [
                {
                    "title": "OpenAI Codex",
                    "url": "https://openai.com/index/openai-codex/",
                    "description": "Agentic coding in the terminal.",
                    "meta_url": {"hostname": "openai.com"},
                }
            ]
        }
    }

    monkeypatch.setenv("BRAVE_SEARCH_API_KEY", "secret")
    monkeypatch.setattr(brave_module.requests, "get", lambda *args, **kwargs: _Resp(payload))

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
                    "meta_url": {"hostname": "openai.com"},
                }
            ]
        }
    }

    monkeypatch.setenv("BRAVE_SEARCH_API_KEY", "secret")
    monkeypatch.setattr(brave_module.requests, "get", lambda *args, **kwargs: _Resp(payload))

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


def test_search_brave_uses_stored_credential_when_env_missing(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys) -> None:
    payload = {
        "web": {
            "results": [
                {
                    "title": "OpenAI Codex",
                    "url": "https://openai.com/index/openai-codex/",
                    "description": "Agentic coding in the terminal.",
                    "meta_url": {"hostname": "openai.com"},
                }
            ]
        }
    }

    monkeypatch.delenv("BRAVE_SEARCH_API_KEY", raising=False)
    monkeypatch.setattr(brave_module.requests, "get", lambda *args, **kwargs: _Resp(payload))

    assert main(["--store", str(tmp_path), "set", "credential", "brave_search_api_key", "secret"]) == 0
    capsys.readouterr()
    assert main(["--store", str(tmp_path), "search", "brave", "openai codex"]) == 0
    output = capsys.readouterr().out
    assert '"title": "OpenAI Codex"' in output


def test_search_brave_fails_when_api_key_missing(tmp_path: Path, capsys, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("BRAVE_SEARCH_API_KEY", raising=False)
    rc = main(["--store", str(tmp_path), "search", "brave", "openai codex"])
    assert rc == 1
    assert "Brave Search API key not configured" in capsys.readouterr().err
