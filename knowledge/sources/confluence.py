"""Confluence source — downloads spaces or pages via Atlassian Python API."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .base import BaseSource
from ..transform.markdown import html_to_markdown, write_markdown_page, _slugify


class ConfluenceSource(BaseSource):
    """Fetch pages from a Confluence space and convert them to Markdown.

    Configuration keys
    ------------------
    url : str
        Base URL of the Confluence instance (e.g. ``https://myco.atlassian.net/wiki``).
    username : str
        Confluence username (email for Cloud).
    token : str
        API token or password.
    space : str
        Space key to fetch (e.g. ``DOCS``).
    max_pages : int, optional
        Maximum pages to fetch per space (default: 200).
    """

    source_type = "confluence"

    def __init__(self, key: str, config: dict[str, Any]) -> None:
        super().__init__(key, config)
        self.url: str = config["url"]
        self.username: str = config["username"]
        self.token: str = config["token"]
        self.space: str = config["space"]
        self.max_pages: int = int(config.get("max_pages", 200))

    def fetch(self, output_dir: Path) -> list[Path]:
        try:
            from atlassian import Confluence
        except ImportError as exc:
            raise RuntimeError(
                "atlassian-python-api is required for the 'confluence' source. "
                "Install it with: pip install atlassian-python-api"
            ) from exc

        client = Confluence(
            url=self.url,
            username=self.username,
            password=self.token,
            cloud=True,
        )

        written: list[Path] = []
        start = 0
        limit = min(50, self.max_pages)
        fetched = 0

        while fetched < self.max_pages:
            pages = client.get_all_pages_from_space(
                self.space,
                start=start,
                limit=limit,
                expand="body.storage,ancestors",
            )
            if not pages:
                break
            for page in pages:
                if fetched >= self.max_pages:
                    break
                path = self._write_page(client, page, output_dir)
                if path:
                    written.append(path)
                fetched += 1
            if len(pages) < limit:
                break
            start += limit

        return written

    def _write_page(
        self, client: Any, page: dict[str, Any], output_dir: Path
    ) -> Path | None:
        title = page.get("title", "Untitled")
        html = page.get("body", {}).get("storage", {}).get("value", "")
        body = html_to_markdown(html)
        page_id = page.get("id", "")
        page_url = self.url.rstrip("/") + "/pages/" + page_id

        # Build sub-directory from ancestor titles
        ancestors = page.get("ancestors", [])
        sub_parts = [_slugify(a["title"]) for a in ancestors if a.get("title")]
        sub_dir = output_dir
        for part in sub_parts:
            sub_dir = sub_dir / part

        meta = {
            "source": page_url,
            "key": self.key,
            "type": self.source_type,
            "space": self.space,
            "page_id": page_id,
        }
        return write_markdown_page(
            output_dir=sub_dir,
            title=title,
            body=body,
            meta=meta,
        )

