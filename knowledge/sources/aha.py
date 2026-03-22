"""Aha! source — downloads features/ideas from an Aha! account via REST API."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import httpx

from .base import BaseSource
from ..transform.markdown import html_to_markdown, write_markdown_page, _slugify


_AHA_API = "https://{subdomain}.aha.io/api/v1"


class AhaSource(BaseSource):
    """Fetch features from an Aha! product and convert them to Markdown.

    Configuration keys
    ------------------
    subdomain : str
        The Aha! account subdomain (e.g. ``mycompany`` for
        ``mycompany.aha.io``).
    token : str
        Aha! API token.
    product_id : str
        Product reference prefix (e.g. ``PROJ``).
    resource : str, optional
        Resource type to fetch: ``features`` (default) or ``ideas``.
    max_items : int, optional
        Maximum number of items to fetch (default: 200).
    """

    source_type = "aha"

    def __init__(self, key: str, config: dict[str, Any]) -> None:
        super().__init__(key, config)
        self.subdomain: str = config["subdomain"]
        self.token: str = config["token"]
        self.product_id: str = config["product_id"]
        self.resource: str = config.get("resource", "features")
        self.max_items: int = int(config.get("max_items", 200))
        self._base_url = _AHA_API.format(subdomain=self.subdomain)

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    def fetch(self, output_dir: Path) -> list[Path]:
        written: list[Path] = []
        page = 1
        per_page = 50

        with httpx.Client(headers=self._headers(), timeout=30) as client:
            while len(written) < self.max_items:
                resp = client.get(
                    f"{self._base_url}/products/{self.product_id}/{self.resource}",
                    params={"page": page, "per_page": per_page},
                )
                resp.raise_for_status()
                data = resp.json()
                items = data.get(self.resource, [])
                if not items:
                    break
                for item in items:
                    if len(written) >= self.max_items:
                        break
                    path = self._write_item(item, output_dir)
                    if path:
                        written.append(path)
                if len(items) < per_page:
                    break
                page += 1

        return written

    def _write_item(self, item: dict[str, Any], output_dir: Path) -> Path | None:
        ref = item.get("reference_num", item.get("id", ""))
        name = item.get("name", "Untitled")
        title = f"{ref}: {name}" if ref else name
        html = item.get("description", {}).get("body", "") or ""
        body = html_to_markdown(html)
        item_url = item.get("url", "")
        workflow_status = item.get("workflow_status", {}).get("name", "")

        meta = {
            "source": item_url,
            "key": self.key,
            "type": self.source_type,
            "reference_num": ref,
            "workflow_status": workflow_status,
            "resource": self.resource,
        }
        return write_markdown_page(
            output_dir=output_dir,
            title=title,
            body=body,
            meta=meta,
            filename=_slugify(str(ref) or name),
        )

