from __future__ import annotations

import json
from abc import ABC, abstractmethod
from pathlib import Path
import shutil
from typing import Any

import yaml

from ..store import KnowledgeStore, utc_now


class SourceAdapter(ABC):
    """Abstract base for all source synchronization adapters.

    Each concrete adapter implements :meth:`sync` which fetches content from
    the external system and writes raw files into the store.
    """

    def __init__(self, source: dict[str, Any], store: KnowledgeStore) -> None:
        self.source = source
        self.store = store
        self.config = source["config"]
        self.raw_dir = store.source_raw_dir(source)
        self.cache_dir = store.source_cache_dir(source)

    @abstractmethod
    def sync(self) -> dict[str, Any]:
        raise NotImplementedError

    def write_json(self, path: Path, payload: Any) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    def write_text(self, path: Path, payload: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(payload, encoding="utf-8")

    def write_markdown(self, path: Path, frontmatter: dict[str, Any], body: str) -> None:
        document = (
            "---\n"
            + yaml.safe_dump(frontmatter, sort_keys=False, allow_unicode=False).strip()
            + "\n---\n\n"
            + body.rstrip()
            + "\n"
        )
        self.write_text(path, document)

    def write_source_metadata(self, synced_at: str, stats: dict[str, Any]) -> None:
        payload = {
            "knowledge_key": self.source["key"],
            "source_id": self.source["id"],
            "source_type": self.source["type"],
            "title": self.source.get("title"),
            "last_synced_at": synced_at,
            "update_command": self.source.get("update_command"),
            "delete_command": self.source.get("delete_command"),
            "config": self.source.get("config", {}),
            "stats": stats,
        }
        self.write_text(
            self.raw_dir / "source-metadata.yaml",
            yaml.safe_dump(payload, sort_keys=False, allow_unicode=False),
        )

    def clear_source_dir(self) -> None:
        if not self.raw_dir.exists():
            self.raw_dir.mkdir(parents=True, exist_ok=True)
            return
        for path in sorted(self.raw_dir.iterdir(), reverse=True):
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()

    def finalize_sync(self, stats: dict[str, Any]) -> dict[str, Any]:
        synced_at = utc_now()
        self.source["last_synced_at"] = synced_at
        persisted_source = {
            key: value for key, value in self.source.items() if not key.startswith("_")
        }
        self.write_source_metadata(synced_at, stats)
        self.store.update_collection_source(persisted_source)
        return {"key": self.source["key"], "source": self.source["id"], **stats}
