from __future__ import annotations

from urllib.parse import urljoin

import requests

from .base import SourceAdapter


class ConfluenceSource(SourceAdapter):
    def sync(self) -> dict[str, object]:
        base_url = self.config["base_url"].rstrip("/") + "/"
        auth = self._auth()
        space_key = self.config["space_key"]
        limit = int(self.config.get("limit", 100))

        response = requests.get(
            urljoin(base_url, "wiki/api/v2/pages"),
            headers={"Accept": "application/json"},
            params={"space-key": space_key, "limit": limit, "body-format": "storage"},
            auth=auth,
            timeout=60,
        )
        response.raise_for_status()
        data = response.json()
        results = data.get("results", [])

        self.write_json(self.raw_dir / "pages.json", data)
        for page in results:
            page_id = page["id"]
            body = page.get("body", {}).get("storage", {}).get("value", "")
            self.write_text(self.raw_dir / "pages" / f"{page_id}.html", body)
            self.write_json(self.raw_dir / "pages" / f"{page_id}.json", page)

        return self.finalize_sync(
            {
                "pages": len(results),
                "space_key": space_key,
                "raw_dir": str(self.raw_dir),
            }
        )

    def _auth(self) -> tuple[str, str]:
        username = self.store.resolve_key(self.config["username"])
        token = self.store.resolve_key(self.config["token"])
        return (username, token)
