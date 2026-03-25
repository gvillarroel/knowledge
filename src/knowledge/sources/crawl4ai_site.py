from __future__ import annotations

import asyncio
import json
import re
from html import unescape
from urllib.parse import urlparse

import requests

from .base import SourceAdapter


class SiteSource(SourceAdapter):
    """Adapter that crawls a website and stores pages as Markdown."""

    def sync(self) -> dict[str, object]:
        start_url = self.config["url"]
        max_depth = int(self.config.get("max_depth", 1))
        max_pages = int(self.config.get("max_pages", 1))

        pages = self._crawl_with_crawl4ai(start_url, max_depth, max_pages)
        if pages is None:
            pages = [self._fetch_single_page(start_url)]

        self.write_json(self.raw_dir / "pages.json", pages)
        for page in pages:
            slug = _slugify_url(page["url"])
            self.write_text(self.raw_dir / "pages" / f"{slug}.md", str(page["markdown"]))
            self.write_json(self.raw_dir / "pages" / f"{slug}.json", page)

        return self.finalize_sync(
            {
                "pages": len(pages),
                "entrypoint": start_url,
                "raw_dir": str(self.raw_dir),
            }
        )

    def _crawl_with_crawl4ai(
        self, start_url: str, max_depth: int, max_pages: int
    ) -> list[dict[str, object]] | None:
        try:
            from crawl4ai import AsyncWebCrawler
        except ImportError:
            return None

        async def run_crawl() -> list[dict[str, object]]:
            async with AsyncWebCrawler() as crawler:
                result = await crawler.arun(
                    url=start_url,
                    max_depth=max_depth,
                    word_count_threshold=1,
                    page_timeout=60000,
                    max_pages=max_pages,
                )
                if isinstance(result, list):
                    return [self._normalize_result(item) for item in result]
                return [self._normalize_result(result)]

        return asyncio.run(run_crawl())

    def _fetch_single_page(self, url: str) -> dict[str, object]:
        try:
            response = requests.get(
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
            response.raise_for_status()
            html = response.text
            title_match = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
            title = unescape(title_match.group(1).strip()) if title_match else url
            markdown = _html_to_text(html)
            return {
                "url": url,
                "title": title,
                "markdown": markdown,
                "metadata": {
                    "url": url,
                    "title": title,
                    "fetched_via": "requests",
                    "content_type": response.headers.get("Content-Type"),
                },
            }
        except requests.HTTPError as exc:
            if exc.response is None or exc.response.status_code not in {401, 403}:
                raise
            return self._fetch_readable_proxy(url)

    def _normalize_result(self, result: object) -> dict[str, object]:
        if isinstance(result, dict):
            payload = result
        else:
            payload = json.loads(result.model_dump_json())  # type: ignore[attr-defined]
        return {
            "url": payload.get("url"),
            "title": payload.get("title"),
            "markdown": payload.get("markdown") or payload.get("cleaned_html") or "",
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


def _html_to_text(html: str) -> str:
    without_scripts = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", html, flags=re.IGNORECASE | re.DOTALL)
    main = re.sub(r"</(p|div|section|article|h1|h2|h3|h4|h5|h6|li|br)>", "\n", without_scripts, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", main)
    text = unescape(text)
    lines = [" ".join(line.split()) for line in text.splitlines()]
    cleaned = "\n".join(line for line in lines if line)
    return cleaned.strip() + "\n"
