from __future__ import annotations

import json
import re
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
        for feature in features:
            reference = feature.get("reference_num", feature["id"])
            name = _feature_name(feature, str(reference))
            frontmatter = {
                "title": name,
                "knowledge_key": self.source["key"],
                "source_id": self.source["id"],
                "source_type": self.source["type"],
                "feature_id": feature.get("id"),
                "reference_num": reference,
                "url": feature.get("url"),
                "workflow_status": _feature_status(feature),
            }
            self.write_markdown(
                self.raw_dir / "features" / f"{reference}.md",
                frontmatter,
                _render_feature_markdown(feature),
            )

        return self.finalize_sync(
            {
                "features": len(features),
                "workspace": workspace,
                "product": workspace,
                "documents": len(features),
                "library_dir": str(self.raw_dir),
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


def _feature_name(feature: dict[str, Any], fallback: str) -> str:
    return str(
        feature.get("name")
        or feature.get("title")
        or feature.get("reference_num")
        or fallback
    )


def _feature_status(feature: dict[str, Any]) -> str | None:
    status = feature.get("workflow_status")
    if isinstance(status, dict):
        name = status.get("name")
        return str(name) if name else None
    return None


def _feature_description(feature: dict[str, Any]) -> str:
    description = feature.get("description")
    if isinstance(description, dict):
        for key in ("body", "html_body", "text"):
            value = description.get(key)
            if isinstance(value, str) and value.strip():
                return _strip_html(value)
    if isinstance(description, str) and description.strip():
        return _strip_html(description)
    return ""


def _strip_html(value: str) -> str:
    text = re.sub(r"<[^>]+>", " ", value)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _render_feature_markdown(feature: dict[str, Any]) -> str:
    reference = str(feature.get("reference_num") or feature.get("id") or "feature")
    name = _feature_name(feature, reference)
    lines = [f"# {name}", "", f"- Reference: {reference}"]
    status = _feature_status(feature)
    if status:
        lines.append(f"- Status: {status}")
    url = feature.get("url")
    if url:
        lines.append(f"- URL: {url}")
    description = _feature_description(feature)
    if description:
        lines.extend(["", "## Description", "", description])
    lines.extend(
        [
            "",
            "## Source Data",
            "",
            "```json",
            json.dumps(feature, indent=2, sort_keys=True),
            "```",
        ]
    )
    return "\n".join(lines).rstrip()
