from __future__ import annotations

import argparse
import asyncio
import json
import platform
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse

import requests
import yaml

from .sources.crawl4ai_site import (
    _LinkExtractor,
    _allowed_path_prefixes,
    _html_to_text,
    _load_cookies_from_cdp,
    _normalize_url,
    _page_anti_bot_reason,
    _should_follow_link,
)


@dataclass
class CapturedPage:
    """One captured documentation page used in a spike comparison."""

    url: str
    title: str
    markdown: str
    links: list[str]
    fetch_mode: str
    status_code: int | None = None
    blocked_reason: str | None = None

    @property
    def markdown_chars(self) -> int:
        """Return the rendered content size in characters."""

        return len(self.markdown.strip())

    @property
    def useful(self) -> bool:
        """Report whether the capture produced meaningful documentation text."""

        return self.blocked_reason is None and self.markdown_chars >= 600


@dataclass
class StrategyResult:
    """Machine-readable result for a single spike strategy."""

    name: str
    status: str
    elapsed_seconds: float
    pages_requested: int
    pages_captured: int
    useful_pages: int
    blocked_pages: int
    avg_markdown_chars: int
    notes: list[str] = field(default_factory=list)
    error: str | None = None
    sample_pages: list[CapturedPage] = field(default_factory=list)


@dataclass
class SpikeReport:
    """Full report for one benchmark execution."""

    url: str
    generated_at: str
    max_pages: int
    max_depth: int
    cdp_url: str | None
    python_version: str
    platform: str
    strategies: list[StrategyResult]


class SiteSpikeStrategy:
    """Base class for benchmarkable site capture strategies."""

    name = "base"

    def run(self, url: str, *, max_pages: int, max_depth: int, cdp_url: str | None) -> StrategyResult:
        """Execute the strategy and return a structured result."""

        started = time.perf_counter()
        try:
            pages = self._capture(url, max_pages=max_pages, max_depth=max_depth, cdp_url=cdp_url)
            blocked_pages = sum(1 for page in pages if page.blocked_reason)
            useful_pages = sum(1 for page in pages if page.useful)
            average_chars = int(sum(page.markdown_chars for page in pages) / len(pages)) if pages else 0
            return StrategyResult(
                name=self.name,
                status="ok",
                elapsed_seconds=round(time.perf_counter() - started, 2),
                pages_requested=max_pages,
                pages_captured=len(pages),
                useful_pages=useful_pages,
                blocked_pages=blocked_pages,
                avg_markdown_chars=average_chars,
                notes=self._notes(url, pages, cdp_url=cdp_url),
                sample_pages=pages,
            )
        except ModuleNotFoundError as exc:
            return StrategyResult(
                name=self.name,
                status="unavailable",
                elapsed_seconds=round(time.perf_counter() - started, 2),
                pages_requested=max_pages,
                pages_captured=0,
                useful_pages=0,
                blocked_pages=0,
                avg_markdown_chars=0,
                error=str(exc),
                notes=self._notes(url, [], cdp_url=cdp_url),
            )
        except Exception as exc:  # pragma: no cover - exercised by live runs
            return StrategyResult(
                name=self.name,
                status="failed",
                elapsed_seconds=round(time.perf_counter() - started, 2),
                pages_requested=max_pages,
                pages_captured=0,
                useful_pages=0,
                blocked_pages=0,
                avg_markdown_chars=0,
                error=f"{type(exc).__name__}: {exc}",
                notes=self._notes(url, [], cdp_url=cdp_url),
            )

    def _capture(
        self,
        url: str,
        *,
        max_pages: int,
        max_depth: int,
        cdp_url: str | None,
    ) -> list[CapturedPage]:
        raise NotImplementedError

    def _notes(self, url: str, pages: list[CapturedPage], *, cdp_url: str | None) -> list[str]:
        """Return strategy-specific notes for the report."""

        del url, pages, cdp_url
        return []


class Crawl4AIStrategy(SiteSpikeStrategy):
    """Current deep-crawl baseline using crawl4ai when available."""

    name = "crawl4ai_deep"

    def _capture(
        self,
        url: str,
        *,
        max_pages: int,
        max_depth: int,
        cdp_url: str | None,
    ) -> list[CapturedPage]:
        from crawl4ai import AsyncWebCrawler, BFSDeepCrawlStrategy, BrowserConfig, CrawlerRunConfig
        from crawl4ai.async_logger import AsyncLogger
        from crawl4ai.deep_crawling import FilterChain, URLPatternFilter

        async def run_crawl() -> list[CapturedPage]:
            browser_config = None
            if cdp_url:
                browser_config = BrowserConfig(
                    browser_mode="custom",
                    cdp_url=cdp_url,
                    use_managed_browser=False,
                    cache_cdp_connection=False,
                    headless=False,
                    verbose=False,
                )
            normalized = _normalize_url(url)
            parsed = urlparse(normalized)
            allowed_patterns = [
                f"{parsed.scheme}://{parsed.netloc}{prefix}*"
                for prefix in _allowed_path_prefixes(normalized)
            ]
            crawl_config = CrawlerRunConfig(
                cache_mode="bypass",
                word_count_threshold=1,
                page_timeout=60000,
                wait_for_images=False,
                verbose=False,
                log_console=False,
                deep_crawl_strategy=BFSDeepCrawlStrategy(
                    max_depth=max_depth,
                    max_pages=max_pages,
                    filter_chain=FilterChain([URLPatternFilter(patterns=allowed_patterns)]),
                ),
            )
            async with AsyncWebCrawler(config=browser_config, logger=AsyncLogger(verbose=False)) as crawler:
                result = await crawler.arun(url=url, config=crawl_config)
            items = result if isinstance(result, list) else [result]
            pages: list[CapturedPage] = []
            for item in items:
                payload = json.loads(item.model_dump_json()) if not isinstance(item, dict) else item
                markdown = payload.get("markdown") or payload.get("cleaned_html") or payload.get("html") or ""
                blocked_reason = _page_anti_bot_reason(
                    {
                        "url": payload.get("url"),
                        "title": payload.get("title"),
                        "markdown": markdown,
                        "metadata": payload,
                    }
                )
                pages.append(
                    CapturedPage(
                        url=str(payload.get("url") or ""),
                        title=str(payload.get("title") or payload.get("url") or ""),
                        markdown=str(markdown),
                        links=[],
                        fetch_mode="crawl4ai",
                        blocked_reason=blocked_reason,
                    )
                )
            return _dedupe_captured_pages(pages)[:max_pages]

        return asyncio.run(run_crawl())

    def _notes(self, url: str, pages: list[CapturedPage], *, cdp_url: str | None) -> list[str]:
        notes = ["Deep crawl baseline used by the current site adapter."]
        if cdp_url:
            notes.append("Connected to the live Chrome session through CDP.")
        if not pages:
            notes.append(f"No pages were captured for {url}.")
        return notes


class RequestsBFSSiteStrategy(SiteSpikeStrategy):
    """Breadth-first HTTP crawler with optional Chrome cookies."""

    def __init__(self, *, use_cdp_cookies: bool) -> None:
        self.use_cdp_cookies = use_cdp_cookies
        self.name = "http_cdp_bfs" if use_cdp_cookies else "http_plain_bfs"

    def _capture(
        self,
        url: str,
        *,
        max_pages: int,
        max_depth: int,
        cdp_url: str | None,
    ) -> list[CapturedPage]:
        session = requests.Session()
        if self.use_cdp_cookies and cdp_url:
            for cookie in _load_cookies_from_cdp(cdp_url):
                session.cookies.set(
                    cookie["name"],
                    cookie["value"],
                    domain=cookie.get("domain"),
                    path=cookie.get("path", "/"),
                )
        return _http_bfs_capture(
            url,
            max_pages=max_pages,
            max_depth=max_depth,
            session=session,
            fetch_mode=self.name,
        )

    def _notes(self, url: str, pages: list[CapturedPage], *, cdp_url: str | None) -> list[str]:
        notes = ["Requests-based breadth-first crawl."]
        if self.use_cdp_cookies:
            notes.append("Chrome cookies are loaded through CDP before issuing HTTP requests.")
            if not cdp_url:
                notes.append("No CDP endpoint was configured, so cookie injection was skipped.")
        else:
            notes.append("No browser state is used, so anti-bot pages are expected on Google-hosted docs.")
        if pages:
            notes.append(f"Start URL: {url}")
        return notes


class BrowserBFSSiteStrategy(SiteSpikeStrategy):
    """Breadth-first crawl executed in the live browser through CDP."""

    name = "browser_cdp_bfs"

    def _capture(
        self,
        url: str,
        *,
        max_pages: int,
        max_depth: int,
        cdp_url: str | None,
    ) -> list[CapturedPage]:
        if not cdp_url:
            raise RuntimeError("CDP URL is required for browser_cdp_bfs")
        return asyncio.run(_browser_bfs_capture(url, max_pages=max_pages, max_depth=max_depth, cdp_url=cdp_url))

    def _notes(self, url: str, pages: list[CapturedPage], *, cdp_url: str | None) -> list[str]:
        notes = ["Every page is navigated inside the live Chrome session."]
        if pages:
            notes.append("This is the highest-fidelity browser simulation in the benchmark.")
        else:
            notes.append(f"No pages were captured for {url}.")
        return notes


class BrowserSeededRequestsStrategy(SiteSpikeStrategy):
    """Hybrid strategy: seed links in the browser, then fetch content over HTTP with cookies."""

    name = "browser_seeded_http_cdp"

    def _capture(
        self,
        url: str,
        *,
        max_pages: int,
        max_depth: int,
        cdp_url: str | None,
    ) -> list[CapturedPage]:
        if not cdp_url:
            raise RuntimeError("CDP URL is required for browser_seeded_http_cdp")
        seed_pages = asyncio.run(_browser_bfs_capture(url, max_pages=1, max_depth=0, cdp_url=cdp_url))
        if not seed_pages:
            return []
        session = requests.Session()
        allowed_prefixes = _allowed_path_prefixes(_normalize_url(url))
        for cookie in _load_cookies_from_cdp(cdp_url):
            session.cookies.set(
                cookie["name"],
                cookie["value"],
                domain=cookie.get("domain"),
                path=cookie.get("path", "/"),
            )
        seed = seed_pages[0]
        candidate_urls = _rank_links(seed.url, seed.links)[: max_pages * 3]
        pages = [seed]
        for candidate in candidate_urls:
            if len(pages) >= max_pages:
                break
            if not _should_follow_link(candidate, _normalize_url(url), allowed_prefixes):
                continue
            try:
                page = _fetch_http_page(session, candidate, fetch_mode=self.name)
            except requests.RequestException:
                continue
            if any(existing.url == page.url for existing in pages):
                continue
            pages.append(page)
        return pages[:max_pages]

    def _notes(self, url: str, pages: list[CapturedPage], *, cdp_url: str | None) -> list[str]:
        notes = [
            "The browser seeds high-signal documentation links, then requests + Chrome cookies download pages faster.",
            "This is the main candidate if you want a production replacement for full browser crawling.",
        ]
        if not pages:
            notes.append(f"No pages were captured for {url}.")
        return notes


def run_spikes(
    url: str,
    *,
    max_pages: int,
    max_depth: int,
    cdp_url: str | None,
) -> SpikeReport:
    """Execute all site-capture spikes for the target URL."""

    strategies: list[SiteSpikeStrategy] = [
        Crawl4AIStrategy(),
        RequestsBFSSiteStrategy(use_cdp_cookies=False),
        RequestsBFSSiteStrategy(use_cdp_cookies=True),
        BrowserBFSSiteStrategy(),
        BrowserSeededRequestsStrategy(),
    ]
    results = [strategy.run(url, max_pages=max_pages, max_depth=max_depth, cdp_url=cdp_url) for strategy in strategies]
    results.sort(key=_result_sort_key)
    return SpikeReport(
        url=url,
        generated_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        max_pages=max_pages,
        max_depth=max_depth,
        cdp_url=cdp_url,
        python_version=platform.python_version(),
        platform=platform.platform(),
        strategies=results,
    )


def write_spike_outputs(report: SpikeReport, output_dir: Path) -> tuple[Path, Path]:
    """Persist the benchmark report as JSON and Markdown."""

    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "report.json"
    markdown_path = output_dir / "report.md"
    json_path.write_text(json.dumps(_report_to_dict(report), indent=2), encoding="utf-8")
    markdown_path.write_text(render_report_markdown(report), encoding="utf-8")
    for strategy in report.strategies:
        strategy_dir = output_dir / strategy.name / "pages"
        strategy_dir.mkdir(parents=True, exist_ok=True)
        for index, page in enumerate(strategy.sample_pages, start=1):
            slug = _safe_slug(page.url) or f"page-{index}"
            target = strategy_dir / f"{index:02d}-{slug}.md"
            payload = {
                "title": page.title,
                "url": page.url,
                "fetch_mode": page.fetch_mode,
                "status_code": page.status_code,
                "blocked_reason": page.blocked_reason,
            }
            body = page.markdown.strip() or "_empty_"
            target.write_text(
                "---\n"
                + yaml.safe_dump(payload, sort_keys=False, allow_unicode=False).strip()
                + "\n---\n\n"
                + body
                + "\n",
                encoding="utf-8",
            )
    return json_path, markdown_path


def render_report_markdown(report: SpikeReport) -> str:
    """Render a concise Markdown summary for humans."""

    lines = [
        "# Site Capture Spike Report",
        "",
        f"- Target URL: `{report.url}`",
        f"- Generated at: `{report.generated_at}`",
        f"- Max pages: `{report.max_pages}`",
        f"- Max depth: `{report.max_depth}`",
        f"- CDP URL: `{report.cdp_url or 'not set'}`",
        f"- Python: `{report.python_version}`",
        f"- Platform: `{report.platform}`",
        "",
        "## Ranking",
        "",
        "| Rank | Strategy | Status | Pages | Useful | Blocked | Avg chars | Seconds |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for rank, strategy in enumerate(report.strategies, start=1):
        lines.append(
            "| "
            + " | ".join(
                [
                    str(rank),
                    strategy.name,
                    strategy.status,
                    str(strategy.pages_captured),
                    str(strategy.useful_pages),
                    str(strategy.blocked_pages),
                    str(strategy.avg_markdown_chars),
                    f"{strategy.elapsed_seconds:.2f}",
                ]
            )
            + " |"
        )
    lines.extend(["", "## Notes", ""])
    for strategy in report.strategies:
        lines.append(f"### {strategy.name}")
        lines.append("")
        lines.append(f"- Status: `{strategy.status}`")
        if strategy.error:
            lines.append(f"- Error: `{strategy.error}`")
        if strategy.notes:
            for note in strategy.notes:
                lines.append(f"- {note}")
        if strategy.sample_pages:
            lines.append(f"- Sample capture count stored on disk: `{len(strategy.sample_pages)}`")
        lines.append("")
    best = report.strategies[0] if report.strategies else None
    if best:
        lines.extend(
            [
                "## Recommendation",
                "",
                f"`{best.name}` ranked first in this run. Prefer it when you need the highest mix of useful page count, low block rate, and runtime efficiency.",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def build_arg_parser() -> argparse.ArgumentParser:
    """Create the CLI parser for the site spike runner."""

    parser = argparse.ArgumentParser(description="Run site capture spikes against one documentation subtree.")
    parser.add_argument("url", help="Target documentation URL")
    parser.add_argument("--max-pages", type=int, default=12, help="Maximum pages to capture per strategy")
    parser.add_argument("--max-depth", type=int, default=1, help="Maximum crawl depth for BFS strategies")
    parser.add_argument("--cdp-url", default=None, help="Chrome DevTools URL used by browser-based strategies")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("evaluation") / "site_spikes",
        help="Directory where reports and sampled markdown files will be written",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Entry point for the standalone site spike runner."""

    parser = build_arg_parser()
    args = parser.parse_args(argv)
    report = run_spikes(
        args.url,
        max_pages=max(args.max_pages, 1),
        max_depth=max(args.max_depth, 0),
        cdp_url=args.cdp_url,
    )
    json_path, markdown_path = write_spike_outputs(report, args.output_dir)
    print(json.dumps({"json": str(json_path), "markdown": str(markdown_path)}, indent=2))
    return 0


def _result_sort_key(result: StrategyResult) -> tuple[int, int, int, float, int]:
    status_rank = {"ok": 0, "failed": 1, "unavailable": 2}.get(result.status, 3)
    return (
        status_rank,
        -result.useful_pages,
        result.blocked_pages,
        result.elapsed_seconds,
        -result.avg_markdown_chars,
    )


def _report_to_dict(report: SpikeReport) -> dict[str, Any]:
    payload = asdict(report)
    payload["strategies"] = [_strategy_to_dict(strategy) for strategy in report.strategies]
    return payload


def _strategy_to_dict(strategy: StrategyResult) -> dict[str, Any]:
    payload = asdict(strategy)
    payload["sample_pages"] = [asdict(page) for page in strategy.sample_pages]
    return payload


def _dedupe_captured_pages(pages: list[CapturedPage]) -> list[CapturedPage]:
    seen: set[str] = set()
    deduped: list[CapturedPage] = []
    for page in pages:
        normalized = _normalize_url(page.url)
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        page.url = normalized
        deduped.append(page)
    return deduped


def _http_bfs_capture(
    start_url: str,
    *,
    max_pages: int,
    max_depth: int,
    session: requests.Session,
    fetch_mode: str,
) -> list[CapturedPage]:
    start_url = _normalize_url(start_url)
    allowed_prefixes = _allowed_path_prefixes(start_url)
    queue: list[tuple[str, int]] = [(start_url, 0)]
    queued = {start_url}
    visited: set[str] = set()
    pages: list[CapturedPage] = []

    while queue and len(pages) < max_pages:
        current_url, depth = queue.pop(0)
        if current_url in visited:
            continue
        visited.add(current_url)
        page = _fetch_http_page(session, current_url, fetch_mode=fetch_mode)
        pages.append(page)
        if depth >= max_depth:
            continue
        for link in _rank_links(current_url, page.links):
            normalized = _normalize_url(link)
            if normalized in visited or normalized in queued:
                continue
            if not _should_follow_link(normalized, start_url, allowed_prefixes):
                continue
            queue.append((normalized, depth + 1))
            queued.add(normalized)
            if len(queue) + len(pages) >= max_pages:
                break
    return _dedupe_captured_pages(pages)[:max_pages]


def _fetch_http_page(session: requests.Session, url: str, *, fetch_mode: str) -> CapturedPage:
    response = session.get(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        },
        timeout=60,
    )
    html = response.text
    title = _extract_html_title(html) or url
    parser = _LinkExtractor()
    parser.feed(html)
    markdown = _html_to_text(html)
    blocked_reason = _page_anti_bot_reason(
        {"url": url, "title": title, "markdown": markdown, "metadata": {"html": html}}
    )
    return CapturedPage(
        url=_normalize_url(url),
        title=title,
        markdown=markdown,
        links=[_normalize_url(urljoin(url, link)) for link in parser.links if link],
        fetch_mode=fetch_mode,
        status_code=response.status_code,
        blocked_reason=blocked_reason,
    )


async def _browser_bfs_capture(
    start_url: str,
    *,
    max_pages: int,
    max_depth: int,
    cdp_url: str,
) -> list[CapturedPage]:
    from playwright.async_api import async_playwright

    start_url = _normalize_url(start_url)
    allowed_prefixes = _allowed_path_prefixes(start_url)
    queue: list[tuple[str, int]] = [(start_url, 0)]
    queued = {start_url}
    visited: set[str] = set()
    pages: list[CapturedPage] = []

    async with async_playwright() as playwright:
        browser = await playwright.chromium.connect_over_cdp(cdp_url)
        context = browser.contexts[0] if browser.contexts else await browser.new_context()
        while queue and len(pages) < max_pages:
            current_url, depth = queue.pop(0)
            if current_url in visited:
                continue
            visited.add(current_url)
            page = await context.new_page()
            try:
                response = await page.goto(current_url, wait_until="domcontentloaded", timeout=60000)
                payload = await page.evaluate(
                    """() => {
                        const root = document.querySelector('main') || document.querySelector('article') || document.body;
                        const nodes = Array.from(document.querySelectorAll('a[href]'));
                        return {
                            title: document.title || location.href,
                            url: location.href,
                            markdown: (root ? root.innerText : document.body.innerText || '').trim(),
                            links: nodes.map((node) => ({
                                href: node.href,
                                text: (node.innerText || node.textContent || '').trim(),
                            })),
                        };
                    }"""
                )
            finally:
                await page.close()
            markdown = _normalize_browser_text(str(payload.get("markdown") or ""))
            normalized_url = _normalize_url(str(payload.get("url") or current_url))
            links = [
                _normalize_url(str(item.get("href") or ""))
                for item in payload.get("links", [])
                if isinstance(item, dict) and item.get("href")
            ]
            blocked_reason = _page_anti_bot_reason(
                {
                    "url": normalized_url,
                    "title": payload.get("title") or normalized_url,
                    "markdown": markdown,
                    "metadata": {},
                }
            )
            pages.append(
                CapturedPage(
                    url=normalized_url,
                    title=str(payload.get("title") or normalized_url),
                    markdown=markdown,
                    links=links,
                    fetch_mode="browser_cdp_bfs",
                    status_code=None if response is None else response.status,
                    blocked_reason=blocked_reason,
                )
            )
            if depth >= max_depth:
                continue
            for link in _rank_links(current_url, links):
                if link in visited or link in queued:
                    continue
                if not _should_follow_link(link, start_url, allowed_prefixes):
                    continue
                queue.append((link, depth + 1))
                queued.add(link)
                if len(queue) + len(pages) >= max_pages:
                    break
    return _dedupe_captured_pages(pages)[:max_pages]


def _normalize_browser_text(text: str) -> str:
    lines = [" ".join(line.split()) for line in text.splitlines()]
    cleaned = "\n".join(line for line in lines if line)
    return cleaned.strip() + ("\n" if cleaned else "")


def _extract_html_title(html: str) -> str | None:
    start = html.lower().find("<title")
    if start == -1:
        return None
    start = html.find(">", start)
    end = html.lower().find("</title>", start)
    if start == -1 or end == -1:
        return None
    return " ".join(html[start + 1 : end].split())


def _rank_links(current_url: str, links: list[str]) -> list[str]:
    scored: list[tuple[int, str]] = []
    current = _normalize_url(current_url)
    for link in links:
        if not link:
            continue
        normalized = _normalize_url(link)
        if not normalized or normalized == current:
            continue
        parsed = urlparse(normalized)
        score = 0
        score += 50 if "/docs" in parsed.path else 0
        score += 15 if parsed.path.count("/") <= 4 else 0
        score += 10 if any(token in parsed.path for token in ("guide", "docs", "quickstart", "tutorial")) else 0
        score -= 20 if any(token in parsed.path for token in ("reference", "release-notes")) else 0
        score -= 30 if parsed.query else 0
        scored.append((score, normalized))
    deduped: list[str] = []
    seen: set[str] = set()
    for _, link in sorted(scored, key=lambda item: (-item[0], item[1])):
        if link in seen:
            continue
        seen.add(link)
        deduped.append(link)
    return deduped


def _safe_slug(url: str) -> str:
    parsed = urlparse(url)
    value = f"{parsed.netloc}{parsed.path}".strip("/")
    safe = "".join(char if char.isalnum() or char in "._-" else "_" for char in value)
    return safe[:120]


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
