from __future__ import annotations

from urllib.parse import urljoin

import requests

from .base import SourceAdapter


class JiraSource(SourceAdapter):
    def sync(self) -> dict[str, object]:
        base_url = self.config["base_url"].rstrip("/") + "/"
        auth = self._auth()
        jql = self.config["jql"]
        limit = int(self.config.get("limit", 100))

        response = requests.get(
            urljoin(base_url, "rest/api/3/search/jql"),
            headers={"Accept": "application/json"},
            params={
                "jql": jql,
                "maxResults": limit,
                "fields": ",".join(self.config.get("fields", ["summary", "description", "status"])),
            },
            auth=auth,
            timeout=60,
        )
        response.raise_for_status()
        data = response.json()
        issues = data.get("issues", [])
        self.write_json(self.raw_dir / "issues.json", data)
        for issue in issues:
            key = issue["key"]
            self.write_json(self.raw_dir / "issues" / f"{key}.json", issue)

        return self.finalize_sync(
            {
                "issues": len(issues),
                "jql": jql,
                "raw_dir": str(self.raw_dir),
            }
        )

    def _auth(self) -> tuple[str, str]:
        username = self.store.resolve_key(self.config["username"])
        token = self.store.resolve_key(self.config["token"])
        return (username, token)
