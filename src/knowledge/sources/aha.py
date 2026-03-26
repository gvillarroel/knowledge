from __future__ import annotations

from typing import Any
from urllib.parse import urljoin

import requests

from .base import SourceAdapter


class AhaSource(SourceAdapter):
    """Adapter that synchronizes features from an Aha workspace."""

    def sync(self) -> dict[str, object]:
        base_url = self.config["base_url"].rstrip("/") + "/"
        token = self.store.resolve_key(self.config["token"])
        workspace = self.config.get("workspace") or self.config["product"]
        limit_value = self.config.get("limit")
        remaining = int(limit_value) if limit_value is not None else None
        page = 1
        features: list[dict[str, Any]] = []
        last_page_payload: dict[str, Any] = {}

        self.clear_source_dir()

        while True:
            per_page = 200 if remaining is None else max(1, min(remaining, 200))
            response = requests.get(
                urljoin(base_url, f"api/v1/products/{workspace}/features"),
                headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
                params={"page": page, "per_page": per_page},
                timeout=60,
            )
            response.raise_for_status()
            data = response.json()
            last_page_payload = data
            page_features = data.get("features", [])
            if remaining is not None:
                page_features = page_features[:remaining]
                remaining -= len(page_features)
            features.extend(page_features)

            if not self._has_next_page(data, page_features, page) or remaining == 0:
                break
            page += 1

        payload = dict(last_page_payload)
        payload["features"] = features
        self.write_json(self.raw_dir / "features.json", payload)
        for feature in features:
            reference = feature.get("reference_num", feature["id"])
            self.write_json(self.raw_dir / "features" / f"{reference}.json", feature)

        return self.finalize_sync(
            {
                "features": len(features),
                "workspace": workspace,
                "product": workspace,
                "raw_dir": str(self.raw_dir),
            }
        )

    def _has_next_page(
        self,
        payload: dict[str, Any],
        page_features: list[dict[str, Any]],
        current_page: int,
    ) -> bool:
        pagination = payload.get("pagination") or []
        if isinstance(pagination, list) and pagination:
            page_info = pagination[0] if isinstance(pagination[0], dict) else {}
        elif isinstance(pagination, dict):
            page_info = pagination
        else:
            page_info = {}
        total_pages = page_info.get("total_pages")
        if isinstance(total_pages, int):
            return current_page < total_pages
        return False
