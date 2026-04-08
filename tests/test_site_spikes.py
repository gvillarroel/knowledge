from __future__ import annotations

from pathlib import Path

from knowledge.site_spikes import (
    CapturedPage,
    SpikeReport,
    StrategyResult,
    _dedupe_captured_pages,
    _extract_html_title,
    _fetch_http_page,
    _http_bfs_capture,
    _normalize_browser_text,
    _rank_links,
    _result_sort_key,
    render_report_markdown,
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
