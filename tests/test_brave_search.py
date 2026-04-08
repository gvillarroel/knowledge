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
    args = parser.parse_args(
        [
            "search",
            "brave",
            "openai codex",
            "--count",
            "3",
            "--offset",
            "2",
            "--country",
            "US",
            "--search-lang",
            "en",
            "--ui-lang",
            "en-US",
            "--spellcheck",
            "--result-filter",
            "web",
            "--result-filter",
            "news",
            "--goggles",
            "https://example.com/test.goggle",
            "--loc-lat",
            "40.7",
            "--loc-long",
            "-74.0",
            "--api-version",
            "2025-10-01",
            "--user-agent",
            "pytest",
            "--format",
            "television",
        ]
    )
    assert args.query == "openai codex"
    assert args.count == 3
    assert args.offset == 2
    assert args.country == "US"
    assert args.search_lang == "en"
    assert args.ui_lang == "en-US"
    assert args.spellcheck is True
    assert args.result_filter == ["web", "news"]
    assert args.goggles == ["https://example.com/test.goggle"]
    assert args.loc_lat == pytest.approx(40.7)
    assert args.loc_long == pytest.approx(-74.0)
    assert args.api_version == "2025-10-01"
    assert args.user_agent == "pytest"
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

    results = brave_module.search_brave(
        "openai codex",
        api_key="secret",
        options={
            "count": 5,
            "offset": 2,
            "country": "US",
            "search_lang": "en",
            "ui_lang": "en-US",
            "spellcheck": True,
            "text_decorations": False,
            "result_filter": ["web", "news"],
            "goggles": ["https://example.com/test.goggle"],
            "loc_lat": 40.7,
            "loc_long": -74.0,
            "api_version": "2025-10-01",
            "cache_control": "no-cache",
            "user_agent": "pytest",
        },
    )

    assert results["query"] == "openai codex"
    assert results["count"] == 5
    assert results["offset"] == 2
    assert results["more_results_available"] is True
    assert results["results"][0]["title"] == "OpenAI Codex"
    assert results["results"][0]["source"] == "openai.com"
    assert captured["url"] == brave_module._BRAVE_WEB_SEARCH_URL
    assert captured["params"] == {
        "q": "openai codex",
        "count": 5,
        "offset": 2,
        "country": "US",
        "search_lang": "en",
        "ui_lang": "en-US",
        "spellcheck": "true",
        "text_decorations": "false",
        "result_filter": "web,news",
        "goggles": ["https://example.com/test.goggle"],
    }
    assert captured["headers"]["Accept"] == "application/json"
    assert captured["headers"]["Api-Version"] == "2025-10-01"
    assert captured["headers"]["Cache-Control"] == "no-cache"
    assert captured["headers"]["User-Agent"] == "pytest"
    assert captured["headers"]["X-Loc-Lat"] == "40.7"
    assert captured["headers"]["X-Loc-Long"] == "-74.0"
    assert captured["headers"]["X-Subscription-Token"] == "secret"


def test_search_brave_reports_api_failures(monkeypatch: pytest.MonkeyPatch) -> None:
    class _BadResp:
        def raise_for_status(self) -> None:
            raise brave_module.requests.HTTPError("boom")

    monkeypatch.setattr(brave_module.requests, "get", lambda *args, **kwargs: _BadResp())

    with pytest.raises(Exception, match="Brave Search API request failed"):
        brave_module.search_brave("openai", api_key="secret")


def test_search_brave_normalizes_non_web_sections() -> None:
    payload = {
        "news": {
            "results": [
                {
                    "title": "Launch update",
                    "url": "https://example.com/news/launch",
                    "description": "Latest product launch details.",
                    "meta_url": {"hostname": "example.com"},
                }
            ]
        },
        "locations": {
            "results": [
                {
                    "name": "OpenAI HQ",
                    "address": {
                        "street_address": "1 Market St",
                        "locality": "San Francisco",
                        "region": "CA",
                        "country": "US",
                    },
                }
            ]
        },
    }

    results = brave_module._normalize_results(payload)

    assert results[0]["result_type"] == "news"
    assert results[0]["title"] == "Launch update"
    assert results[1]["result_type"] == "locations"
    assert results[1]["title"] == "OpenAI HQ"
    assert "San Francisco" in results[1]["description"]


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


def test_search_brave_main_passes_extended_options(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys) -> None:
    payload = {"web": {"results": []}, "query": {"more_results_available": False}}
    captured: dict[str, object] = {}

    def fake_get(url: str, *, params: dict[str, object], headers: dict[str, str], timeout: int) -> _Resp:
        captured["url"] = url
        captured["params"] = params
        captured["headers"] = headers
        captured["timeout"] = timeout
        return _Resp(payload)

    monkeypatch.setenv("BRAVE_SEARCH_API_KEY", "secret")
    monkeypatch.setattr(brave_module.requests, "get", fake_get)

    assert (
        main(
            [
                "--store",
                str(tmp_path),
                "search",
                "brave",
                "openai codex",
                "--country",
                "US",
                "--search-lang",
                "en",
                "--ui-lang",
                "en-US",
                "--count",
                "7",
                "--offset",
                "3",
                "--safesearch",
                "strict",
                "--spellcheck",
                "--freshness",
                "pw",
                "--no-text-decorations",
                "--result-filter",
                "web",
                "--result-filter",
                "news",
                "--units",
                "metric",
                "--goggles",
                "https://example.com/test.goggle",
                "--extra-snippets",
                "--summary",
                "--enable-rich-callback",
                "--include-fetch-metadata",
                "--operators",
                "--loc-lat",
                "40.7",
                "--loc-long",
                "-74.0",
                "--loc-timezone",
                "America/New_York",
                "--loc-city",
                "New York",
                "--loc-state",
                "NY",
                "--loc-state-name",
                "New York",
                "--loc-country",
                "US",
                "--loc-postal-code",
                "10001",
                "--api-version",
                "2025-10-01",
                "--cache-control",
                "no-cache",
                "--user-agent",
                "pytest",
            ]
        )
        == 0
    )
    capsys.readouterr()
    assert captured["url"] == brave_module._BRAVE_WEB_SEARCH_URL
    assert captured["params"] == {
        "q": "openai codex",
        "country": "US",
        "search_lang": "en",
        "ui_lang": "en-US",
        "count": 7,
        "offset": 3,
        "safesearch": "strict",
        "spellcheck": "true",
        "freshness": "pw",
        "text_decorations": "false",
        "result_filter": "web,news",
        "units": "metric",
        "goggles": ["https://example.com/test.goggle"],
        "extra_snippets": "true",
        "summary": "true",
        "enable_rich_callback": "true",
        "include_fetch_metadata": "true",
        "operators": "true",
    }
    assert captured["headers"]["X-Subscription-Token"] == "secret"
    assert captured["headers"]["Accept"] == "application/json"
    assert captured["headers"]["X-Loc-Timezone"] == "America/New_York"
    assert captured["headers"]["X-Loc-City"] == "New York"
    assert captured["headers"]["X-Loc-State"] == "NY"
    assert captured["headers"]["X-Loc-State-Name"] == "New York"
    assert captured["headers"]["X-Loc-Country"] == "US"
    assert captured["headers"]["X-Loc-Postal-Code"] == "10001"
