from __future__ import annotations

from urllib.parse import urljoin

import requests

from .base import SourceAdapter


class AhaSource(SourceAdapter):
    def sync(self) -> dict[str, object]:
        base_url = self.config["base_url"].rstrip("/") + "/"
        token = self.store.resolve_key(self.config["token"])
        product = self.config["product"]
        limit = int(self.config.get("limit", 100))

        response = requests.get(
            urljoin(base_url, f"api/v1/products/{product}/features"),
            headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
            params={"per_page": limit},
            timeout=60,
        )
        response.raise_for_status()
        data = response.json()
        features = data.get("features", [])
        self.write_json(self.raw_dir / "features.json", data)
        for feature in features:
            reference = feature.get("reference_num", feature["id"])
            self.write_json(self.raw_dir / "features" / f"{reference}.json", feature)

        return self.finalize_sync(
            {
                "features": len(features),
                "product": product,
                "raw_dir": str(self.raw_dir),
            }
        )
