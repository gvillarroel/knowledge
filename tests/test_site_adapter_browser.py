from __future__ import annotations

import json
import sys
import types
from pathlib import Path

import pytest

import knowledge.sources.crawl4ai_site as site_module
from knowledge.sources.crawl4ai_site import SiteSource, _browser_bfs_capture, _load_cookies_from_cdp
from knowledge.store import KnowledgeStore


def make_adapter(tmp_path: Path) -> SiteSource:
    store = KnowledgeStore(tmp_path)
    store.initialize()
    store.create_collection_key("sites")
    source = store.add_collection_source(
        "sites",
        "site",
        title="https://example.com/docs",
        config={"url": "https://example.com/docs", "max_depth": 1, "max_pages": 3},
        update_command="sync",
        delete_command="del",
    )
    return SiteSource(source, store)


def test_crawl4ai_capture_uses_optional_dependency(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    adapter = make_adapter(tmp_path)

    class Value:
        def __init__(self, *args: object, **kwargs: object) -> None:
            self.args = args
            self.kwargs = kwargs

    class ModelItem:
        markdown = types.SimpleNamespace(raw_markdown="model markdown")

        def model_dump_json(self) -> str:
            return json.dumps({"url": "https://example.com/docs/b", "title": "B"})

    class AsyncCrawler:
        def __init__(self, *args: object, **kwargs: object) -> None:
            del args, kwargs

        async def __aenter__(self) -> "AsyncCrawler":
            return self

        async def __aexit__(self, *args: object) -> None:
            del args

        async def arun(self, **kwargs: object) -> list[object]:
            del kwargs
            return [
                {"url": "https://example.com/docs/a", "title": "A", "markdown": "dict markdown"},
                ModelItem(),
            ]

    crawl4ai = types.ModuleType("crawl4ai")
    crawl4ai.AsyncWebCrawler = AsyncCrawler
    crawl4ai.BFSDeepCrawlStrategy = Value
    crawl4ai.BrowserConfig = Value
    crawl4ai.CrawlerRunConfig = Value
    logger = types.ModuleType("crawl4ai.async_logger")
    logger.AsyncLogger = Value
    deep = types.ModuleType("crawl4ai.deep_crawling")
    deep.FilterChain = Value
    deep.URLPatternFilter = Value
    monkeypatch.setitem(sys.modules, "crawl4ai", crawl4ai)
    monkeypatch.setitem(sys.modules, "crawl4ai.async_logger", logger)
    monkeypatch.setitem(sys.modules, "crawl4ai.deep_crawling", deep)
    monkeypatch.setenv("KNOW_SITE_CDP_URL", "http://127.0.0.1:9222")

    pages = adapter._crawl_with_crawl4ai("https://example.com/docs", 1, 3)

    assert pages is not None
    assert [page["title"] for page in pages] == ["A", "B"]
    assert pages[1]["markdown"] == "model markdown"


def test_crawl4ai_capture_returns_none_when_runner_fails(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    adapter = make_adapter(tmp_path)

    class Value:
        def __init__(self, *args: object, **kwargs: object) -> None:
            del args, kwargs

    class AsyncCrawler:
        def __init__(self, *args: object, **kwargs: object) -> None:
            del args, kwargs

        async def __aenter__(self) -> "AsyncCrawler":
            raise RuntimeError("browser unavailable")

        async def __aexit__(self, *args: object) -> None:
            del args

    crawl4ai = types.ModuleType("crawl4ai")
    crawl4ai.AsyncWebCrawler = AsyncCrawler
    crawl4ai.BFSDeepCrawlStrategy = Value
    crawl4ai.BrowserConfig = Value
    crawl4ai.CrawlerRunConfig = Value
    logger = types.ModuleType("crawl4ai.async_logger")
    logger.AsyncLogger = Value
    deep = types.ModuleType("crawl4ai.deep_crawling")
    deep.FilterChain = Value
    deep.URLPatternFilter = Value
    monkeypatch.setitem(sys.modules, "crawl4ai", crawl4ai)
    monkeypatch.setitem(sys.modules, "crawl4ai.async_logger", logger)
    monkeypatch.setitem(sys.modules, "crawl4ai.deep_crawling", deep)

    assert adapter._crawl_with_crawl4ai("https://example.com/docs", 1, 3) is None


def test_browser_seeded_http_handles_fallback_blocked_and_fetch_errors(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    adapter = make_adapter(tmp_path)
    fallback = [{"url": "https://example.com/docs", "title": "Fallback", "markdown": "body"}]
    monkeypatch.setattr(adapter, "_crawl_with_browser_bfs", lambda *_args: [])
    monkeypatch.setattr(adapter, "_crawl_with_http_bfs", lambda *_args: fallback)
    assert adapter._crawl_with_browser_seeded_http_bfs("https://example.com/docs", 1, 3) == fallback

    blocked = {
        "url": "https://example.com/docs",
        "title": "Human check",
        "markdown": "Please verify you are human",
        "links": ["https://example.com/docs/a"],
    }
    monkeypatch.setattr(adapter, "_crawl_with_browser_bfs", lambda *_args: [blocked])
    assert adapter._crawl_with_browser_seeded_http_bfs("https://example.com/docs", 1, 3) == [blocked]

    seed = {
        "url": "https://example.com/docs",
        "title": "Docs",
        "markdown": "body",
        "links": [
            "https://example.com/docs/a",
            "https://example.com/docs/b",
            "https://example.com/outside",
        ],
    }
    monkeypatch.setattr(adapter, "_crawl_with_browser_bfs", lambda *_args: [seed])

    def fetch(url: str) -> tuple[dict[str, object], list[str]]:
        if url.endswith("/a"):
            raise site_module._BlockedPageError(url, "blocked")
        return ({"url": url, "title": "B", "markdown": "body", "metadata": {}}, [])

    monkeypatch.setattr(adapter, "_fetch_page_with_links", fetch)
    pages = adapter._crawl_with_browser_seeded_http_bfs("https://example.com/docs", 1, 4)
    assert [page["url"] for page in pages] == ["https://example.com/docs", "https://example.com/docs/b"]
    assert pages[1]["metadata"] == {
        "seeded_from_browser": True,
        "seed_url": "https://example.com/docs",
    }


def test_fetch_page_with_browser_uses_shared_or_created_context(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    adapter = make_adapter(tmp_path)
    events: list[str] = []

    class PlaywrightError(Exception):
        pass

    class Page:
        def goto(self, *args: object, **kwargs: object) -> None:
            del args, kwargs

        def wait_for_load_state(self, *args: object, **kwargs: object) -> None:
            del args, kwargs
            raise PlaywrightError("network stays busy")

        def content(self) -> str:
            return '<html><title>Docs</title><main>Browser body</main><a href="/docs/a">A</a></html>'

        def title(self) -> str:
            return "Docs"

        def eval_on_selector_all(self, *_args: object) -> list[str]:
            return ["https://example.com/docs/a"]

        def close(self) -> None:
            events.append("page")

    class Context:
        def new_page(self) -> Page:
            return Page()

        def close(self) -> None:
            events.append("context")

    class Browser:
        contexts: list[Context] = []

        def new_context(self) -> Context:
            return Context()

        def close(self) -> None:
            events.append("browser")

    class Chromium:
        def connect_over_cdp(self, _url: str) -> Browser:
            return Browser()

    class Playwright:
        chromium = Chromium()

    class Manager:
        def __enter__(self) -> Playwright:
            return Playwright()

        def __exit__(self, *args: object) -> None:
            del args

    sync_api = types.ModuleType("playwright.sync_api")
    sync_api.Error = PlaywrightError
    sync_api.sync_playwright = lambda: Manager()
    monkeypatch.setitem(sys.modules, "playwright.sync_api", sync_api)
    monkeypatch.setenv("KNOW_SITE_CDP_URL", "http://127.0.0.1:9222")

    result = adapter._fetch_page_with_browser("https://example.com/docs")

    assert result is not None
    assert result[0]["metadata"]["fetched_via"] == "browser_cdp"
    assert result[1] == ["https://example.com/docs/a", "/docs/a"]
    assert events == ["page", "context", "browser"]


def test_browser_bfs_capture_with_fake_async_playwright(monkeypatch: pytest.MonkeyPatch) -> None:
    payloads = [
        {
            "url": "https://example.com/docs",
            "title": "Docs",
            "markdown": "Root body",
            "links": ["https://example.com/docs/child"],
        },
        {
            "url": "https://example.com/docs/child",
            "title": "Child",
            "markdown": "Child body",
            "links": [],
        },
    ]

    class PlaywrightError(Exception):
        pass

    class Response:
        status = 200

    class Page:
        async def goto(self, *args: object, **kwargs: object) -> Response:
            del args, kwargs
            return Response()

        async def wait_for_load_state(self, *args: object, **kwargs: object) -> None:
            del args, kwargs
            raise PlaywrightError("network busy")

        async def evaluate(self, _script: str) -> dict[str, object]:
            return payloads.pop(0)

        async def close(self) -> None:
            return None

    class Context:
        async def new_page(self) -> Page:
            return Page()

    class Browser:
        contexts = [Context()]

    class Chromium:
        async def connect_over_cdp(self, _url: str) -> Browser:
            return Browser()

    class Playwright:
        chromium = Chromium()

    class Manager:
        async def __aenter__(self) -> Playwright:
            return Playwright()

        async def __aexit__(self, *args: object) -> None:
            del args

    async_api = types.ModuleType("playwright.async_api")
    async_api.Error = PlaywrightError
    async_api.async_playwright = lambda: Manager()
    monkeypatch.setitem(sys.modules, "playwright.async_api", async_api)

    pages = site_module.asyncio.run(
        _browser_bfs_capture(
            "https://example.com/docs",
            max_pages=2,
            max_depth=1,
            cdp_url="http://127.0.0.1:9222",
        )
    )

    assert [page["title"] for page in pages] == ["Docs", "Child"]
    assert pages[0]["metadata"]["status_code"] == 200


def test_load_cookies_reports_missing_playwright(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setitem(sys.modules, "playwright.async_api", None)

    with pytest.raises(RuntimeError, match="requires the `playwright` Python package"):
        _load_cookies_from_cdp("http://127.0.0.1:9222")
