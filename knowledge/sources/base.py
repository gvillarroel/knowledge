"""Base class for all knowledge sources."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class BaseSource(ABC):
    """Abstract base for a knowledge source.

    Subclasses must implement :meth:`fetch` which downloads content and
    writes Markdown files under *output_dir*.
    """

    source_type: str = "base"

    def __init__(self, key: str, config: dict[str, Any]) -> None:
        self.key = key
        self.config = config

    @abstractmethod
    def fetch(self, output_dir: Path) -> list[Path]:
        """Download / refresh content and write Markdown files.

        Returns a list of paths that were written.
        """

    def to_store_entry(self) -> dict[str, Any]:
        """Return a dict suitable for persisting in sources.yaml."""
        return {"key": self.key, "type": self.source_type, **self.config}

    # ------------------------------------------------------------------
    # Registry helpers
    # ------------------------------------------------------------------

    _registry: dict[str, type["BaseSource"]] = {}

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        if cls.source_type != "base":
            BaseSource._registry[cls.source_type] = cls

    @classmethod
    def from_entry(cls, entry: dict[str, Any]) -> "BaseSource":
        """Reconstruct a source object from a *sources.yaml* entry."""
        source_type = entry.get("type", "web")
        klass = cls._registry.get(source_type)
        if klass is None:
            raise ValueError(f"Unknown source type: {source_type!r}")
        key = entry["key"]
        config = {k: v for k, v in entry.items() if k not in ("key", "type", "added_at")}
        return klass(key, config)
