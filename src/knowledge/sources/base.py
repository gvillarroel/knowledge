from __future__ import annotations

import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from ..store import KnowledgeStore, utc_now


class SourceAdapter(ABC):
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

    def finalize_sync(self, stats: dict[str, Any]) -> dict[str, Any]:
        self.source["last_synced_at"] = utc_now()
        self.store.update_collection_source(self.source)
        return {"key": self.source["key"], "source": self.source["id"], **stats}
