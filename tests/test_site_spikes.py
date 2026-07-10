from __future__ import annotations

import json
import sys
import types
from pathlib import Path

import pytest

import knowledge.site_spikes as site_spikes
from knowledge.site_spikes import (
    BrowserBFSSiteStrategy,
    BrowserSeededRequestsStrategy,
    CapturedPage,
    Crawl4AIStrategy,
    RequestsBFSSiteStrategy,
    SiteSpikeStrategy,
    SpikeReport,
    StrategyResult,
    _browser_bfs_capture,
    _dedupe_captured_pages,
    _extract_html_title,
    _fetch_http_page,
    _http_bfs_capture,
    _normalize_browser_text,
    _rank_links,
    _result_sort_key,
    build_arg_parser,
    main,
    render_report_markdown,
    run_spikes,
    write_spike_outputs,
)


def test_captured_page_useful_threshold() -> None:
    short = CapturedPage(
        url="https://example.com/docs/a",
        title="A",
        markdown="short",
        links=[],
        fetch_mode="http",
    )
    useful = CapturedPage(
        url="https://example.com/docs/b",
        title="B",
        markdown="x" * 650,
        links=[],
        fetch_mode="http",
    )

    assert short.useful is False
    assert useful.useful is True


def test_normalize_browser_text_collapses_whitespace() -> None:
    text = " Heading  \n\n   First   line \nSecond\tline "

    assert _normalize_browser_text(text) == "Heading\nFirst line\nSecond line\n"


def test_rank_links_prefers_docs_paths() -> None:
    current_url = "https://docs.cloud.google.com/bigquery/docs"
    links = [
        "https://docs.cloud.google.com/bigquery/docs/reference",
        "https://docs.cloud.google.com/bigquery/docs/quickstarts",
        "https://docs.cloud.google.com/bigquery/docs/tutorials",
        "https://docs.cloud.google.com/contact",
    ]

    ranked = _rank_links(current_url, links)

    assert ranked[0] == "https://docs.cloud.google.com/bigquery/docs/quickstarts"
    assert "https://docs.cloud.google.com/contact" in ranked


def test_result_sort_key_prefers_successful_useful_fast_strategies() -> None:
    winner = StrategyResult(
        name="winner",
        status="ok",
        elapsed_seconds=2.0,
        pages_requested=10,
        pages_captured=10,
        useful_pages=9,
        blocked_pages=0,
        avg_markdown_chars=1200,
    )
    loser = StrategyResult(
        name="loser",
        status="failed",
        elapsed_seconds=1.0,
        pages_requested=10,
        pages_captured=0,
        useful_pages=0,
        blocked_pages=0,
        avg_markdown_chars=0,
    )

    assert _result_sort_key(winner) < _result_sort_key(loser)


def test_render_report_markdown_contains_recommendation() -> None:
    report = SpikeReport(
        url="https://docs.cloud.google.com/bigquery/docs",
        generated_at="2026-04-07T00:00:00Z",
        max_pages=12,
        max_depth=1,
        cdp_url="http://127.0.0.1:9222",
        python_version="3.14.3",
        platform="Windows",
        strategies=[
            StrategyResult(
                name="browser_seeded_http_cdp",
                status="ok",
                elapsed_seconds=3.5,
                pages_requested=12,
                pages_captured=12,
                useful_pages=11,
                blocked_pages=0,
                avg_markdown_chars=1800,
            )
        ],
    )

    rendered = render_report_markdown(report)

    assert "Site Capture Spike Report" in rendered
    assert "browser_seeded_http_cdp" in rendered
    assert "Recommendation" in rendered


def test_extract_html_title_returns_title_text() -> None:
    html = "<html><head><title> BigQuery Docs </title></head></html>"

    assert _extract_html_title(html) == "BigQuery Docs"


def test_dedupe_captured_pages_normalizes_urls() -> None:
    pages = [
        CapturedPage(
            url="https://example.com/docs/page",
            title="One",
            markdown="x" * 700,
            links=[],
            fetch_mode="http",
        ),
        CapturedPage(
            url="https://example.com/docs/page#section",
            title="Two",
            markdown="x" * 700,
            links=[],
            fetch_mode="http",
        ),
    ]

    deduped = _dedupe_captured_pages(pages)

    assert len(deduped) == 1
    assert deduped[0].url == "https://example.com/docs/page"


class _FakeResponse:
    def __init__(self, text: str, status_code: int = 200) -> None:
        self.text = text
        self.status_code = status_code


class _FakeSession:
    def __init__(self, pages: dict[str, str]) -> None:
        self.pages = pages

    def get(self, url: str, headers: dict[str, str], timeout: int) -> _FakeResponse:
        del headers, timeout
        return _FakeResponse(self.pages[url])


def test_fetch_http_page_resolves_relative_links() -> None:
    session = _FakeSession(
        {
            "https://example.com/docs/start": """
            <html>
              <head><title>Start</title></head>
              <body>
                <main>
                  <p>Hello docs</p>
                  <a href="/docs/next">Next</a>
                </main>
              </body>
            </html>
            """
        }
    )

    page = _fetch_http_page(session, "https://example.com/docs/start", fetch_mode="http")  # type: ignore[arg-type]

    assert page.title == "Start"
    assert page.links == ["https://example.com/docs/next"]
    assert "Hello docs" in page.markdown


def test_http_bfs_capture_follows_in_subtree_links() -> None:
    session = _FakeSession(
        {
            "https://example.com/docs/start": """
            <html><head><title>Start</title></head><body>
            <a href="/docs/next">Next</a>
            <a href="/outside">Outside</a>
            <p>Root</p>
            </body></html>
            """,
            "https://example.com/docs/next": """
            <html><head><title>Next</title></head><body><p>Child</p></body></html>
            """,
        }
    )

    pages = _http_bfs_capture(
        "https://example.com/docs/start",
        max_pages=5,
        max_depth=1,
        session=session,  # type: ignore[arg-type]
        fetch_mode="http",
    )

    assert [page.url for page in pages] == [
        "https://example.com/docs/start",
        "https://example.com/docs/next",
    ]


def test_write_spike_outputs_writes_report_and_pages(tmp_path: Path) -> None:
    report = SpikeReport(
        url="https://example.com/docs",
        generated_at="2026-04-07T00:00:00Z",
        max_pages=2,
        max_depth=1,
        cdp_url=None,
        python_version="3.14.3",
        platform="Windows",
        strategies=[
            StrategyResult(
                name="http_cdp_bfs",
                status="ok",
                elapsed_seconds=1.2,
                pages_requested=2,
                pages_captured=1,
                useful_pages=1,
                blocked_pages=0,
                avg_markdown_chars=900,
                sample_pages=[
                    CapturedPage(
                        url="https://example.com/docs/start",
                        title="Start",
                        markdown="content",
                        links=[],
                        fetch_mode="http_cdp_bfs",
                    )
                ],
            )
        ],
    )

    json_path, markdown_path = write_spike_outputs(report, tmp_path)

    assert json_path.exists()
    assert markdown_path.exists()
    page_file = tmp_path / "http_cdp_bfs" / "pages" / "01-example.com_docs_start.md"
    assert page_file.exists()
    assert "content" in page_file.read_text(encoding="utf-8")


class _ControlledStrategy(SiteSpikeStrategy):
    name = "controlled"

    def __init__(self, outcome: object) -> None:
        self.outcome = outcome

    def _capture(self, url: str, *, max_pages: int, max_depth: int, cdp_url: str | None) -> list[CapturedPage]:
        del url, max_pages, max_depth, cdp_url
        if isinstance(self.outcome, BaseException):
            raise self.outcome
        return self.outcome  # type: ignore[return-value]

    def _notes(self, url: str, pages: list[CapturedPage], *, cdp_url: str | None) -> list[str]:
        return [f"{url}|{len(pages)}|{cdp_url}"]


@pytest.mark.parametrize(
    ("outcome", "status"),
    [
        (ModuleNotFoundError("optional dependency"), "unavailable"),
        (RuntimeError("capture failed"), "failed"),
    ],
)
def test_site_spike_strategy_run_reports_failures(outcome: BaseException, status: str) -> None:
    result = _ControlledStrategy(outcome).run(
        "https://example.com/docs",
        max_pages=3,
        max_depth=1,
        cdp_url=None,
    )

    assert result.status == status
    assert result.pages_captured == 0
    assert result.error
    assert result.notes == ["https://example.com/docs|0|None"]


def test_site_spike_strategy_run_calculates_page_metrics() -> None:
    pages = [
        CapturedPage("https://example.com/a", "A", "x" * 700, [], "test"),
        CapturedPage("https://example.com/b", "B", "blocked", [], "test", blocked_reason="captcha"),
    ]

    result = _ControlledStrategy(pages).run(
        "https://example.com/docs",
        max_pages=3,
        max_depth=1,
        cdp_url="http://127.0.0.1:9222",
    )

    assert result.status == "ok"
    assert result.pages_captured == 2
    assert result.useful_pages == 1
    assert result.blocked_pages == 1
    assert result.avg_markdown_chars == 353


def test_base_strategy_methods_are_explicit() -> None:
    strategy = SiteSpikeStrategy()

    with pytest.raises(NotImplementedError):
        strategy._capture("https://example.com", max_pages=1, max_depth=0, cdp_url=None)
    assert strategy._notes("https://example.com", [], cdp_url=None) == []


def test_strategy_notes_cover_empty_and_configured_variants() -> None:
    crawl = Crawl4AIStrategy()
    assert "live Chrome" in " ".join(crawl._notes("https://example.com", [], cdp_url="cdp"))
    assert "No pages" in " ".join(crawl._notes("https://example.com", [], cdp_url=None))

    plain = RequestsBFSSiteStrategy(use_cdp_cookies=False)
    cookies = RequestsBFSSiteStrategy(use_cdp_cookies=True)
    page = CapturedPage("https://example.com", "Example", "x" * 700, [], "http")
    assert plain.name == "http_plain_bfs"
    assert "anti-bot" in " ".join(plain._notes("https://example.com", [page], cdp_url=None))
    assert "skipped" in " ".join(cookies._notes("https://example.com", [], cdp_url=None))

    browser = BrowserBFSSiteStrategy()
    assert "No pages" in " ".join(browser._notes("https://example.com", [], cdp_url="cdp"))
    assert "highest-fidelity" in " ".join(browser._notes("https://example.com", [page], cdp_url="cdp"))
    seeded = BrowserSeededRequestsStrategy()
    assert "No pages" in " ".join(seeded._notes("https://example.com", [], cdp_url="cdp"))


def test_requests_strategy_injects_cookies_and_runs_bfs(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: dict[str, object] = {}

    class Cookies:
        def set(self, name: str, value: str, **kwargs: object) -> None:
            calls["cookie"] = (name, value, kwargs)

    class Session:
        def __init__(self) -> None:
            self.cookies = Cookies()

    monkeypatch.setattr(site_spikes.requests, "Session", Session)
    monkeypatch.setattr(site_spikes, "_load_cookies_from_cdp", lambda _url: [{"name": "sid", "value": "1"}])
    monkeypatch.setattr(
        site_spikes,
        "_http_bfs_capture",
        lambda url, **kwargs: calls.update(url=url, kwargs=kwargs) or [],
    )

    result = RequestsBFSSiteStrategy(use_cdp_cookies=True)._capture(
        "https://example.com/docs",
        max_pages=2,
        max_depth=1,
        cdp_url="http://127.0.0.1:9222",
    )

    assert result == []
    assert calls["cookie"] == ("sid", "1", {"domain": None, "path": "/"})
    assert calls["url"] == "https://example.com/docs"


def test_browser_strategies_require_cdp() -> None:
    with pytest.raises(RuntimeError, match="CDP URL is required"):
        BrowserBFSSiteStrategy()._capture("https://example.com", max_pages=1, max_depth=0, cdp_url=None)
    with pytest.raises(RuntimeError, match="CDP URL is required"):
        BrowserSeededRequestsStrategy()._capture("https://example.com", max_pages=1, max_depth=0, cdp_url=None)


def test_browser_strategy_runs_async_capture(monkeypatch: pytest.MonkeyPatch) -> None:
    page = CapturedPage("https://example.com", "Example", "body", [], "browser")

    async def capture(*args: object, **kwargs: object) -> list[CapturedPage]:
        del args, kwargs
        return [page]

    monkeypatch.setattr(site_spikes, "_browser_bfs_capture", capture)

    result = BrowserBFSSiteStrategy()._capture(
        "https://example.com",
        max_pages=1,
        max_depth=0,
        cdp_url="http://127.0.0.1:9222",
    )

    assert result == [page]


def test_browser_seeded_strategy_handles_empty_seed(monkeypatch: pytest.MonkeyPatch) -> None:
    async def capture(*args: object, **kwargs: object) -> list[CapturedPage]:
        del args, kwargs
        return []

    monkeypatch.setattr(site_spikes, "_browser_bfs_capture", capture)

    assert BrowserSeededRequestsStrategy()._capture(
        "https://example.com/docs",
        max_pages=2,
        max_depth=1,
        cdp_url="http://127.0.0.1:9222",
    ) == []


def test_browser_seeded_strategy_fetches_ranked_pages(monkeypatch: pytest.MonkeyPatch) -> None:
    seed = CapturedPage(
        "https://example.com/docs",
        "Docs",
        "seed",
        ["https://example.com/docs/a", "https://example.com/docs/b", "https://outside.example/a"],
        "browser",
    )

    async def capture(*args: object, **kwargs: object) -> list[CapturedPage]:
        del args, kwargs
        return [seed]

    class Cookies:
        def set(self, *args: object, **kwargs: object) -> None:
            del args, kwargs

    class Session:
        def __init__(self) -> None:
            self.cookies = Cookies()

    def fetch(_session: object, url: str, *, fetch_mode: str) -> CapturedPage:
        if url.endswith("/b"):
            raise site_spikes.requests.RequestException("blocked")
        return CapturedPage(url, url.rsplit("/", 1)[-1], "body", [], fetch_mode)

    monkeypatch.setattr(site_spikes, "_browser_bfs_capture", capture)
    monkeypatch.setattr(site_spikes.requests, "Session", Session)
    monkeypatch.setattr(site_spikes, "_load_cookies_from_cdp", lambda _url: [{"name": "sid", "value": "1"}])
    monkeypatch.setattr(site_spikes, "_fetch_http_page", fetch)

    pages = BrowserSeededRequestsStrategy()._capture(
        "https://example.com/docs",
        max_pages=3,
        max_depth=1,
        cdp_url="http://127.0.0.1:9222",
    )

    assert [page.url for page in pages] == ["https://example.com/docs", "https://example.com/docs/a"]


def test_run_spikes_builds_and_sorts_report(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_run(self: SiteSpikeStrategy, url: str, **kwargs: object) -> StrategyResult:
        del url, kwargs
        useful = 2 if self.name == "http_plain_bfs" else 1
        return StrategyResult(self.name, "ok", 1.0, 2, 2, useful, 0, 700)

    monkeypatch.setattr(SiteSpikeStrategy, "run", fake_run)

    report = run_spikes("https://example.com/docs", max_pages=2, max_depth=1, cdp_url=None)

    assert len(report.strategies) == 5
    assert report.strategies[0].name == "http_plain_bfs"
    assert report.generated_at.endswith("Z")


def test_cli_parser_and_main_write_report(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    parser = build_arg_parser()
    parsed = parser.parse_args(["https://example.com", "--max-pages", "0", "--max-depth", "-2"])
    assert parsed.url == "https://example.com"

    captured: dict[str, object] = {}
    report = SpikeReport("https://example.com", "now", 1, 0, None, "3", "test", [])
    monkeypatch.setattr(
        site_spikes,
        "run_spikes",
        lambda url, **kwargs: captured.update(url=url, kwargs=kwargs) or report,
    )
    monkeypatch.setattr(
        site_spikes,
        "write_spike_outputs",
        lambda _report, output: (output / "report.json", output / "report.md"),
    )

    result = main(["https://example.com", "--max-pages", "0", "--max-depth", "-2", "--output-dir", str(tmp_path)])

    assert result == 0
    assert captured["kwargs"] == {"max_pages": 1, "max_depth": 0, "cdp_url": None}
    assert json.loads(capsys.readouterr().out)["json"].endswith("report.json")


def test_crawl4ai_strategy_capture_with_fake_optional_dependency(monkeypatch: pytest.MonkeyPatch) -> None:
    class Value:
        def __init__(self, *args: object, **kwargs: object) -> None:
            self.args = args
            self.kwargs = kwargs

    class ModelItem:
        def model_dump_json(self) -> str:
            return json.dumps({"url": "https://example.com/docs/b", "title": "B", "cleaned_html": "B body"})

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
                {"url": "https://example.com/docs/a", "title": "A", "markdown": "A body"},
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

    pages = Crawl4AIStrategy()._capture(
        "https://example.com/docs",
        max_pages=2,
        max_depth=1,
        cdp_url="http://127.0.0.1:9222",
    )

    assert [page.title for page in pages] == ["A", "B"]


def test_browser_bfs_capture_with_fake_playwright(monkeypatch: pytest.MonkeyPatch) -> None:
    payloads = [
        {
            "url": "https://example.com/docs",
            "title": "Docs",
            "markdown": "Root body",
            "links": [{"href": "https://example.com/docs/child"}],
        },
        {
            "url": "https://example.com/docs/child",
            "title": "Child",
            "markdown": "Child body",
            "links": [],
        },
    ]

    class Response:
        status = 200

    class Page:
        async def goto(self, *args: object, **kwargs: object) -> Response:
            del args, kwargs
            return Response()

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
    async_api.async_playwright = lambda: Manager()
    monkeypatch.setitem(sys.modules, "playwright.async_api", async_api)

    pages = site_spikes.asyncio.run(
        _browser_bfs_capture(
            "https://example.com/docs",
            max_pages=2,
            max_depth=1,
            cdp_url="http://127.0.0.1:9222",
        )
    )

    assert [page.title for page in pages] == ["Docs", "Child"]


@pytest.mark.parametrize(
    ("html", "expected"),
    [
        ("<html></html>", None),
        ("<title without-close", None),
    ],
)
def test_extract_html_title_handles_missing_markup(html: str, expected: None) -> None:
    assert _extract_html_title(html) is expected
