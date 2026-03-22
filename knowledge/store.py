"""Knowledge base store — manages the ~/.knowledge directory."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


KNOWLEDGE_DIR = Path(os.environ.get("KNOWLEDGE_HOME", Path.home() / ".knowledge"))
SOURCES_FILE = KNOWLEDGE_DIR / "sources.yaml"
DATA_DIR = KNOWLEDGE_DIR / "data"


def _ensure_dirs() -> None:
    KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def _load_sources() -> list[dict[str, Any]]:
    """Return the list of source entries from sources.yaml."""
    _ensure_dirs()
    if not SOURCES_FILE.exists():
        return []
    with SOURCES_FILE.open() as fh:
        data = yaml.safe_load(fh) or {}
    return data.get("sources", [])


def _save_sources(sources: list[dict[str, Any]]) -> None:
    """Persist source entries to sources.yaml."""
    _ensure_dirs()
    with SOURCES_FILE.open("w") as fh:
        yaml.dump({"sources": sources}, fh, default_flow_style=False, allow_unicode=True)


def get_source(key: str) -> dict[str, Any] | None:
    """Return the source entry for *key*, or None if not found."""
    for entry in _load_sources():
        if entry.get("key") == key:
            return entry
    return None


def list_sources() -> list[dict[str, Any]]:
    """Return all source entries."""
    return _load_sources()


def add_source(entry: dict[str, Any]) -> None:
    """Add or replace a source entry identified by *entry['key']*."""
    key = entry["key"]
    sources = _load_sources()
    sources = [s for s in sources if s.get("key") != key]
    entry.setdefault("added_at", datetime.now(timezone.utc).isoformat())
    sources.append(entry)
    _save_sources(sources)


def remove_source(key: str) -> bool:
    """Remove the source entry for *key*. Returns True if it existed."""
    sources = _load_sources()
    new = [s for s in sources if s.get("key") != key]
    if len(new) == len(sources):
        return False
    _save_sources(new)
    return True


def source_data_dir(key: str) -> Path:
    """Return (and create) the data directory for *key*."""
    d = DATA_DIR / key
    d.mkdir(parents=True, exist_ok=True)
    return d
