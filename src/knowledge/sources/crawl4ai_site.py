from __future__ import annotations

import asyncio
import json
import os
import random
import re
import time
from functools import lru_cache
from html import unescape
from html.parser import HTMLParser
from urllib.parse import urldefrag, urljoin, urlparse

import requests
from ..errors import SyncError
from .base import SourceAdapter


class _LinkExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "a":
            return
        for name, value in attrs:
            if name.lower() == "href" and value:
                self.links.append(value)
                return


class _BlockedPageError(RuntimeError):
    def __init__(self, url: str, reason: str) -> None:
        self.url = url
        self.reason = reason
        super().__init__(f"{reason}: {url}")


class _SkippablePageError(RuntimeError):
    def __init__(self, url: str, reason: str) -> None:
        self.url = url
        self.reason = reason
        super().__init__(f"{reason}: {url}")


class SiteSource(SourceAdapter):
    """Adapter that crawls a website and stores pages as Markdown."""

    def sync(self) -> dict[str, object]:
        start_url = self.config["url"]
        max_depth = int(self.config.get("max_depth", 1))
        max_pages = int(self.config.get("max_pages", 1))
        crawl_page_limit = _effective_max_pages(max_pages)

        pages: list[dict[str, object]] | None = None
        if _prefer_cdp_bfs(start_url):
            pages = self._crawl_with_http_bfs(start_url, max_depth, crawl_page_limit)
        elif _prefer_crawl4ai(start_url):
            pages = self._crawl_with_crawl4ai(start_url, max_depth, crawl_page_limit)
        if pages is None:
            pages = self._crawl_with_http_bfs(start_url, max_depth, crawl_page_limit)
        anti_bot_reason = _find_anti_bot_reason(pages)
        if anti_bot_reason:
            raise SyncError(
                self.source["key"],
                self.source["id"],
                f"site returned anti-bot content for {start_url}: {anti_bot_reason}",
            )

        self.clear_source_dir()
        self._write_compact_pages(start_url, pages)

        return self.finalize_sync(
            {
                "pages": len(pages),
                "entrypoint": start_url,
                "raw_dir": str(self.raw_dir),
            }
        )

    def _write_compact_pages(
        self,
        start_url: str,
        pages: list[dict[str, object]],
    ) -> None:
        for page in pages:
            slug = _slugify_url(str(page.get("url") or "page"))
            page_path = self.raw_dir / "pages" / f"{slug}.md"
            metadata = page.get("metadata") if isinstance(page.get("metadata"), dict) else {}
            frontmatter = {
                "title": page.get("title") or page.get("url"),
                "url": page.get("url"),
                "knowledge_key": self.source["key"],
                "source_id": self.source["id"],
                "source_type": self.source["type"],
                "entrypoint": start_url,
                "source_metadata": metadata,
            }
            self.write_markdown(page_path, frontmatter, str(page.get("markdown") or ""))

    def _crawl_with_crawl4ai(
        self, start_url: str, max_depth: int, max_pages: int
    ) -> list[dict[str, object]] | None:
        try:
            from crawl4ai import AsyncWebCrawler, BFSDeepCrawlStrategy, BrowserConfig, CrawlerRunConfig
            from crawl4ai.async_logger import AsyncLogger
            from crawl4ai.deep_crawling import FilterChain, URLPatternFilter
        except ImportError:
            return None

        async def run_crawl() -> list[dict[str, object]]:
            browser_config = None
            cdp_url = _cdp_url()
            if cdp_url:
                browser_config = BrowserConfig(
                    browser_mode="custom",
                    cdp_url=cdp_url,
                    # Reuse the user's live browser session without taking
                    # ownership of its lifecycle.
                    use_managed_browser=False,
                    cache_cdp_connection=False,
                    headless=False,
                    verbose=False,
                )
            allowed_patterns = [
                f"{urlparse(start_url).scheme}://{urlparse(start_url).netloc}{prefix}*"
                for prefix in _allowed_path_prefixes(_normalize_url(start_url))
            ]
            crawl_config = CrawlerRunConfig(
                word_count_threshold=1,
                page_timeout=60000,
                cache_mode="bypass",
                mean_delay=_env_float("KNOW_SITE_CRAWL_MEAN_DELAY_SECONDS", 2.0),
                max_range=_env_float("KNOW_SITE_CRAWL_JITTER_SECONDS", 1.0),
                semaphore_count=_env_int("KNOW_SITE_CRAWL_CONCURRENCY", 1),
                delay_before_return_html=_env_float("KNOW_SITE_CRAWL_RENDER_DELAY_SECONDS", 1.0),
                wait_for_images=False,
                deep_crawl_strategy=BFSDeepCrawlStrategy(
                    max_depth=max_depth,
                    max_pages=max_pages,
                    filter_chain=FilterChain(
                        [URLPatternFilter(patterns=allowed_patterns)]
                    ),
                ),
                verbose=False,
                log_console=False,
            )
            # Silence crawl4ai's Rich logger so Windows cp1252 consoles do not
            # fail before the crawl starts.
            async with AsyncWebCrawler(config=browser_config, logger=AsyncLogger(verbose=False)) as crawler:
                result = await crawler.arun(url=start_url, config=crawl_config)
                if isinstance(result, list):
                    return _dedupe_pages_by_url(self._normalize_result(item) for item in result)
                return _dedupe_pages_by_url([self._normalize_result(result)])

        try:
            return asyncio.run(run_crawl())
        except Exception:
            return None

    def _crawl_with_http_bfs(self, start_url: str, max_depth: int, max_pages: int) -> list[dict[str, object]]:
        start_url = _normalize_url(start_url)
        allowed_prefixes = _allowed_path_prefixes(start_url)
        queue: list[tuple[str, int]] = [(start_url, 0)]
        queued = {start_url}
        visited: set[str] = set()
        pages: list[dict[str, object]] = []

        while queue and len(pages) < max_pages:
            current_url, depth = queue.pop(0)
            if current_url in visited:
                continue
            visited.add(current_url)

            if pages:
                time.sleep(_fallback_delay_seconds())
            try:
                page, links = self._fetch_page_with_links(current_url)
            except (_BlockedPageError, _SkippablePageError):
                if not pages and current_url == start_url:
                    raise
                continue
            pages.append(page)

            if depth >= max_depth:
                continue

            for link in _rank_candidate_links(links, start_url):
                normalized = _normalize_url(urljoin(current_url, link))
                if not _should_follow_link(normalized, start_url, allowed_prefixes):
                    continue
                if normalized in visited or normalized in queued:
                    continue
                queue.append((normalized, depth + 1))
                queued.add(normalized)
                if len(queue) + len(pages) >= max_pages:
                    break

        return pages or [self._fetch_single_page(start_url)]

    def _fetch_page_with_links(self, url: str) -> tuple[dict[str, object], list[str]]:
        response = _http_get_with_backoff(url)
        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            if exc.response is not None and exc.response.status_code == 404:
                raise _SkippablePageError(url, "not_found") from exc
            if exc.response is None or exc.response.status_code not in {401, 403}:
                raise
            return self._fetch_readable_proxy(url), []

        html = response.text
        title = _extract_html_title(html) or url
        markdown = _html_to_primary_text(html)
        parser = _LinkExtractor()
        parser.feed(html)
        return (
            {
                "url": url,
                "title": title,
                "markdown": markdown,
                "metadata": {
                    "url": url,
                    "title": title,
                    "fetched_via": _active_http_fetch_mode(),
                    "content_scope": _content_scope(html),
                    "content_type": response.headers.get("Content-Type"),
                    "status_code": getattr(response, "status_code", 200),
                },
            },
            parser.links,
        )

    def _fetch_single_page(self, url: str) -> dict[str, object]:
        page, _ = self._fetch_page_with_links(url)
        return page

    def _normalize_result(self, result: object) -> dict[str, object]:
        if isinstance(result, dict):
            payload = result
            markdown = payload.get("markdown") or payload.get("cleaned_html") or payload.get("html") or ""
        else:
            payload = json.loads(result.model_dump_json())  # type: ignore[attr-defined]
            markdown_result = getattr(result, "markdown", None)
            markdown = ""
            if markdown_result is not None:
                markdown = getattr(markdown_result, "raw_markdown", "") or str(markdown_result)
            if not markdown:
                markdown = payload.get("cleaned_html") or payload.get("html") or ""
        return {
            "url": payload.get("url"),
            "title": payload.get("title"),
            "markdown": markdown,
            "metadata": payload,
        }

    def _fetch_readable_proxy(self, url: str) -> dict[str, object]:
        proxy_url = f"https://r.jina.ai/http://{url.removeprefix('https://').removeprefix('http://')}"
        response = requests.get(proxy_url, timeout=60)
        response.raise_for_status()
        markdown = response.text.strip() + "\n"
        title_match = re.search(r"^Title:\s*(.+)$", markdown, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else url
        return {
            "url": url,
            "title": title,
            "markdown": markdown,
            "metadata": {
                "url": url,
                "title": title,
                "fetched_via": "r.jina.ai",
                "proxy_url": proxy_url,
                "content_type": response.headers.get("Content-Type"),
            },
        }


def _slugify_url(value: str | None) -> str:
    if not value:
        return "page"
    parsed = urlparse(value)
    base = f"{parsed.netloc}{parsed.path}".strip("/") or "page"
    safe = re.sub(r"[^A-Za-z0-9._-]+", "_", base)
    return safe[:200]


def _normalize_url(value: str) -> str:
    parsed = urlparse(value)
    cleaned = parsed._replace(fragment="", query="")
    return urldefrag(cleaned.geturl().rstrip("/"))[0]


def _allowed_path_prefixes(start_url: str) -> list[str]:
    parsed = urlparse(start_url)
    segments = [segment for segment in parsed.path.split("/") if segment]
    if len(segments) >= 5 and segments[0] in {"python", "java"} and segments[1:4] == ["docs", "reference", segments[3]]:
        return ["/" + "/".join(segments[:5])]
    if len(segments) >= 4 and segments[0] in {"python", "java"} and segments[1:3] == ["docs", "reference"]:
        return ["/" + "/".join(segments[:5])]
    if len(segments) >= 2 and segments[1] == "docs":
        return [f"/{segments[0]}/docs"]
    if segments:
        return ["/" + "/".join(segments[:-1] or segments)]
    return ["/"]


def _should_follow_link(candidate_url: str, start_url: str, allowed_prefixes: list[str]) -> bool:
    parsed_candidate = urlparse(candidate_url)
    parsed_start = urlparse(start_url)
    if parsed_candidate.scheme not in {"http", "https"}:
        return False
    if parsed_candidate.netloc != parsed_start.netloc:
        return False
    if not parsed_candidate.path:
        return False
    if any(parsed_candidate.path.startswith(prefix) for prefix in allowed_prefixes):
        return True
    return candidate_url == start_url


def _html_to_text(html: str) -> str:
    without_scripts = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", html, flags=re.IGNORECASE | re.DOTALL)
    main = re.sub(r"</(p|div|section|article|h1|h2|h3|h4|h5|h6|li|br)>", "\n", without_scripts, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", main)
    text = unescape(text)
    lines = [" ".join(line.split()) for line in text.splitlines()]
    cleaned = "\n".join(line for line in lines if line)
    return cleaned.strip() + "\n"


def _extract_html_title(html: str) -> str | None:
    title_match = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
    if not title_match:
        return None
    return unescape(" ".join(title_match.group(1).split()))


def _extract_primary_html(html: str) -> str | None:
    patterns = [
        r"<main\b[^>]*>(?P<content>.*?)</main>",
        r"<article\b[^>]*>(?P<content>.*?)</article>",
        r"<div\b[^>]*role=[\"']main[\"'][^>]*>(?P<content>.*?)</div>",
    ]
    for pattern in patterns:
        match = re.search(pattern, html, re.IGNORECASE | re.DOTALL)
        if match:
            content = match.group("content").strip()
            if content:
                return content
    return None


def _content_scope(html: str) -> str:
    return "primary" if _extract_primary_html(html) else "document"


def _html_to_primary_text(html: str) -> str:
    primary_html = _extract_primary_html(html)
    if primary_html:
        primary_text = _html_to_text(primary_html)
        if len(primary_text.strip()) >= 200:
            return primary_text
    return _html_to_text(html)


def _active_http_fetch_mode() -> str:
    return "http_cdp_bfs" if _cdp_url() else "http_bfs"


def _rank_candidate_links(links: list[str], start_url: str) -> list[str]:
    start = _normalize_url(start_url)
    ranked: list[tuple[int, str]] = []
    for link in links:
        normalized = _normalize_url(urljoin(start, link))
        if not normalized or normalized == start:
            continue
        parsed = urlparse(normalized)
        score = 0
        score += 40 if "/docs/" in parsed.path or parsed.path.endswith("/docs") else 0
        score += 20 if any(token in parsed.path for token in ("guide", "guides", "tutorial", "quickstart")) else 0
        score -= 20 if any(token in parsed.path for token in ("reference", "release-notes")) else 0
        score -= 10 if parsed.query else 0
        ranked.append((score, link))
    deduped: list[str] = []
    seen: set[str] = set()
    for _, link in sorted(ranked, key=lambda item: (-item[0], item[1])):
        normalized = _normalize_url(urljoin(start, link))
        if normalized in seen:
            continue
        seen.add(normalized)
        deduped.append(link)
    return deduped


def _dedupe_pages_by_url(pages: list[dict[str, object]] | object) -> list[dict[str, object]]:
    seen: set[str] = set()
    deduped: list[dict[str, object]] = []
    for page in pages:
        normalized = _normalize_url(str(page.get("url") or ""))
        if normalized in seen:
            continue
        seen.add(normalized)
        deduped.append(page)
    return deduped


def _env_float(name: str, default: float) -> float:
    raw = os.getenv(name)
    if raw is None or raw == "":
        return default
    try:
        return float(raw)
    except ValueError:
        return default


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or raw == "":
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def _effective_max_pages(max_pages: int) -> int:
    if max_pages <= 0:
        return max(_env_int("KNOW_SITE_UNLIMITED_MAX_PAGES_CAP", 100000), 1)
    return max_pages


def _fallback_delay_seconds() -> float:
    base = _env_float("KNOW_SITE_FALLBACK_DELAY_SECONDS", 2.0)
    jitter = max(_env_float("KNOW_SITE_FALLBACK_JITTER_SECONDS", 1.0), 0.0)
    return max(base, 0.0) + (random.random() * jitter)


def _prefer_http_crawl(start_url: str) -> bool:
    host = urlparse(start_url).netloc.lower()
    host_override = os.getenv("KNOW_SITE_PREFER_HTTP_HOSTS", "")
    override_hosts = [item.strip().lower() for item in host_override.split(",") if item.strip()]
    if override_hosts:
        return any(host == candidate or host.endswith(f".{candidate}") for candidate in override_hosts)
    return host == "docs.cloud.google.com"


def _prefer_cdp_bfs(start_url: str) -> bool:
    if not _prefer_http_crawl(start_url):
        return False
    return _cdp_url() is not None


def _cdp_url() -> str | None:
    raw = os.getenv("KNOW_SITE_CDP_URL", "").strip()
    return raw or None


def _prefer_crawl4ai(start_url: str) -> bool:
    if _prefer_http_crawl(start_url) and os.getenv("KNOW_SITE_FORCE_CRAWL4AI", "").strip() != "1":
        return False
    if _cdp_url():
        return True
    return not _prefer_http_crawl(start_url)


def _http_get_with_backoff(url: str) -> requests.Response:
    attempts = max(_env_int("KNOW_SITE_HTTP_MAX_ATTEMPTS", 4), 1)
    base_delay = max(_env_float("KNOW_SITE_HTTP_RETRY_BASE_SECONDS", 15.0), 0.0)
    last_response: requests.Response | None = None
    get = _http_session().get if _cdp_url() else requests.get

    for attempt in range(attempts):
        try:
            response = get(
                url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.9",
                    "Upgrade-Insecure-Requests": "1",
                },
                timeout=60,
            )
        except requests.RequestException as exc:
            if attempt < attempts - 1:
                time.sleep(base_delay * (attempt + 1))
                continue
            raise _BlockedPageError(url, "network_or_rate_limited") from exc
        last_response = response
        status_code = getattr(response, "status_code", 200)
        text = response.text.lower()
        blocked = status_code == 429 or "unusual traffic" in text or "/sorry/index" in text
        if not blocked:
            return response
        if attempt < attempts - 1:
            time.sleep(base_delay * (attempt + 1))

    assert last_response is not None
    raise _BlockedPageError(url, "anti_bot_or_rate_limited")


def _find_anti_bot_reason(pages: list[dict[str, object]]) -> str | None:
    for page in pages:
        reason = _page_anti_bot_reason(page)
        if reason:
            return reason
    return None


@lru_cache(maxsize=1)
def _http_session() -> requests.Session:
    session = requests.Session()
    cdp_url = _cdp_url()
    if cdp_url:
        try:
            for cookie in _load_cookies_from_cdp(cdp_url):
                session.cookies.set(
                    cookie["name"],
                    cookie["value"],
                    domain=cookie.get("domain"),
                    path=cookie.get("path", "/"),
                )
        except RuntimeError:
            raise
        except Exception:
            pass
    return session


def _load_cookies_from_cdp(cdp_url: str) -> list[dict[str, object]]:
    try:
        from playwright.async_api import async_playwright
    except ImportError as exc:
        raise RuntimeError(
            "CDP-assisted site crawling requires the `playwright` Python package. "
            "Install it before using KNOW_SITE_CDP_URL."
        ) from exc

    async def read_cookies() -> list[dict[str, object]]:
        async with async_playwright() as playwright:
            browser = await playwright.chromium.connect_over_cdp(cdp_url)
            cookies: list[dict[str, object]] = []
            for context in browser.contexts:
                cookies.extend(await context.cookies())
            return cookies

    try:
        return asyncio.run(read_cookies())
    except Exception as exc:
        raise RuntimeError(f"Unable to load cookies from CDP endpoint {cdp_url}") from exc


def _page_anti_bot_reason(page: dict[str, object]) -> str | None:
    metadata = page.get("metadata") if isinstance(page.get("metadata"), dict) else {}
    haystacks = [
        str(page.get("url") or ""),
        str(page.get("title") or ""),
        str(page.get("markdown") or ""),
        str(metadata.get("redirected_url") or ""),
        str(metadata.get("cleaned_html") or ""),
        str(metadata.get("html") or ""),
    ]
    combined = "\n".join(haystacks).lower()
    indicators = [
        ("google_sorry", "our systems have detected unusual traffic"),
        ("captcha_prompt", "to continue, please type the characters below"),
        ("sorry_index", "/sorry/index"),
        ("robot_check", "this page checks to see if it's really you sending the requests"),
        ("verify_human", "verify you are human"),
    ]
    for label, needle in indicators:
        if needle in combined:
            return label
    return None
