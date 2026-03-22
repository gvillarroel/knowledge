"""Web source — uses crawl4ai to download a complete site."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from .base import BaseSource
from ..transform.markdown import write_markdown_page


class WebSource(BaseSource):
    """Crawl a website using crawl4ai and convert pages to Markdown.

    Configuration keys
    ------------------
    url : str
        The seed URL to crawl.
    max_pages : int, optional
        Maximum number of pages to fetch (default: 50).
    """

    source_type = "web"

    def __init__(self, key: str, config: dict[str, Any]) -> None:
        super().__init__(key, config)
        self.url: str = config["url"]
        self.max_pages: int = int(config.get("max_pages", 50))

    def fetch(self, output_dir: Path) -> list[Path]:
        """Crawl *self.url* and write one Markdown file per page."""
        return asyncio.run(self._async_fetch(output_dir))

    async def _async_fetch(self, output_dir: Path) -> list[Path]:
        try:
            from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode
            from crawl4ai.deep_scraping_strategy import DeepScrapingStrategy
        except ImportError as exc:
            raise RuntimeError(
                "crawl4ai is required for the 'web' source type. "
                "Install it with: pip install crawl4ai"
            ) from exc

        written: list[Path] = []
        config = CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            deep_crawl_strategy=DeepScrapingStrategy(
                max_depth=3,
                max_pages=self.max_pages,
            ),
        )
        async with AsyncWebCrawler() as crawler:
            results = await crawler.arun(self.url, config=config)
            if not isinstance(results, list):
                results = [results]
            for result in results:
                if not result.success:
                    continue
                title = result.metadata.get("title") or _url_to_title(result.url)
                body = result.markdown or ""
                meta = {
                    "source": result.url,
                    "key": self.key,
                    "type": self.source_type,
                }
                slug = _url_to_slug(result.url)
                path = write_markdown_page(
                    output_dir=output_dir,
                    title=title,
                    body=body,
                    meta=meta,
                    filename=slug,
                )
                written.append(path)
        return written


def _url_to_title(url: str) -> str:
    parsed = urlparse(url)
    parts = [p for p in parsed.path.strip("/").split("/") if p]
    return parts[-1].replace("-", " ").replace("_", " ").title() if parts else parsed.netloc


def _url_to_slug(url: str) -> str:
    parsed = urlparse(url)
    path = parsed.path.strip("/").replace("/", "--")
    return (parsed.netloc + ("--" + path if path else "")).replace(".", "-") or "index"
