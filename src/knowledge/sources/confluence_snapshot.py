"""Private checkpoint and publication helpers for Confluence synchronization."""

from __future__ import annotations

from contextlib import contextmanager
import hashlib
import json
import logging
import os
from pathlib import Path
import shutil
import tempfile
from typing import Any, Callable, Iterator
from uuid import uuid4

import yaml

from ..errors import KnowledgeError

_LOG = logging.getLogger(__name__)


def atomic_json(path: Path, payload: Any) -> None:
    """Replace one checkpoint only after its complete JSON has been written."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, delete=False) as handle:
        temporary = Path(handle.name)
        try:
            json.dump(payload, handle, sort_keys=True, ensure_ascii=False)
            handle.flush()
        except BaseException:
            handle.close()
            temporary.unlink(missing_ok=True)
            raise
    try:
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def cache_page(path: Path, page: dict[str, Any]) -> None:
    """Store a page with a digest so corrupt checkpoints are never reused."""
    digest = hashlib.sha256(json.dumps(page, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    atomic_json(path, {"schema": 1, "sha256": digest, "page": page})


def cached_page(path: Path, current: dict[str, Any]) -> dict[str, Any] | None:
    """Reuse only a complete, digest-valid page matching freshly listed metadata."""
    current_version = current.get("version")
    version = current_version.get("number") if isinstance(current_version, dict) else None
    if type(version) is not int or version < 1:
        return None
    try:
        cached = json.loads(path.read_text(encoding="utf-8"))
        page = cached["page"]
        if cached["schema"] != 1 or not isinstance(page, dict):
            return None
        digest = hashlib.sha256(json.dumps(page, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
        if digest != cached["sha256"] or (page.get("version") or {}).get("number") != version:
            return None
        for key in ("id", "title", "spaceId", "parentId", "parentType", "status", "authorId", "ownerId", "createdAt"):
            if key in current and current[key] != page.get(key):
                return None
        if not isinstance(page.get("body", {}).get("storage", {}).get("value"), str):
            return None
        return page
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        return None


@contextmanager
def _source_lock(path: Path) -> Iterator[None]:
    if path.is_symlink():
        raise KnowledgeError("Confluence sync lock must not be a symbolic link")
    with path.open("a+b") as handle:
        handle.seek(0, os.SEEK_END)
        if handle.tell() == 0:
            handle.write(b"\0")
            handle.flush()
        handle.seek(0)
        try:
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            raise KnowledgeError("Another Confluence sync is already using this source") from None
        try:
            yield
        finally:
            handle.seek(0)
            if os.name == "nt":
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def _frontmatter(path: Path) -> dict[str, Any]:
    try:
        with path.open(encoding="utf-8") as handle:
            if handle.readline().strip() != "---":
                return {}
            lines = []
            size = 0
            for line in handle:
                if line.strip() == "---":
                    result = yaml.safe_load("".join(lines))
                    return result if isinstance(result, dict) else {}
                size += len(line)
                if size > 65536:
                    return {}
                lines.append(line)
    except (OSError, UnicodeError, yaml.YAMLError):
        pass
    return {}


class ConfluenceSnapshot:
    """Stage a complete corpus, preserving authored files and rolling back failed publication."""

    def __init__(self, raw_dir: Path, source: dict[str, Any]) -> None:
        self.raw_dir = raw_dir
        self.source = source
        store_root = raw_dir.parents[2]
        scope = hashlib.sha256(str(raw_dir.resolve()).encode()).hexdigest()
        self.work_dir = store_root / ".confluence-sync" / scope
        if not self.work_dir.resolve().is_relative_to(store_root.resolve()):
            raise KnowledgeError("Confluence staging directory escapes the store")
        self.work_dir.mkdir(parents=True, exist_ok=True)
        self.backup = self.work_dir / "previous"
        self.stage: Path | None = None
        self._lock_context = _source_lock(self.work_dir / "sync.lock")

    def __enter__(self) -> ConfluenceSnapshot:
        self._lock_context.__enter__()
        try:
            if self.raw_dir.is_symlink() or self.backup.is_symlink():
                raise KnowledgeError("Confluence snapshot directories must not be symbolic links")
            self._recover()
            self.stage = Path(tempfile.mkdtemp(prefix="candidate-", dir=self.work_dir))
            return self
        except BaseException:
            self._lock_context.__exit__(None, None, None)
            raise

    def __exit__(self, *_exc: object) -> None:
        try:
            if self.stage is not None and self.stage.exists():
                shutil.rmtree(self.stage)
        finally:
            self._lock_context.__exit__(None, None, None)

    def _recover(self) -> None:
        if not self.backup.exists():
            return
        metadata_path = self.raw_dir / "source-metadata.yaml"
        try:
            metadata = yaml.safe_load(metadata_path.read_text(encoding="utf-8")) or {}
            complete = (
                metadata.get("source_id") == self.source["id"]
                and metadata.get("stats", {}).get("snapshot_schema") == 1
                and metadata.get("stats", {}).get("complete") is True
            )
        except (OSError, ValueError, AttributeError, yaml.YAMLError):
            complete = False
        if complete:
            shutil.rmtree(self.backup)
            return
        # A process may have died between the two directory renames. Keep any
        # uncertain candidate instead of deleting files that might be authored.
        if self.raw_dir.exists():
            if any(self.raw_dir.iterdir()):
                self.raw_dir.rename(self.work_dir / f"interrupted-{uuid4().hex}")
            else:
                self.raw_dir.rmdir()
        self.backup.rename(self.raw_dir)
        _LOG.warning("Recovered the previous Confluence snapshot after interrupted publication")

    def _preserve_authored_files(self) -> None:
        assert self.stage is not None
        for path in self.raw_dir.iterdir():
            if path.is_symlink() or (path.is_dir() and any(item.is_symlink() for item in path.rglob("*"))):
                raise KnowledgeError("Confluence source contains a symbolic link; publication stopped")
            if path.name == "source-metadata.yaml":
                continue
            metadata = _frontmatter(path) if path.suffix == ".md" and path.is_file() else {}
            if (
                metadata.get("source_id") == self.source["id"]
                and metadata.get("source_type") == "confluence"
                and metadata.get("document_id") is not None
            ):
                continue
            target = self.stage / path.name
            if target.exists():
                raise KnowledgeError(f"Confluence output would overwrite an authored file: {path.name}")
            if path.is_dir():
                shutil.copytree(path, target)
            else:
                shutil.copy2(path, target)

    def publish(self, finalize: Callable[[], dict[str, Any]]) -> dict[str, Any]:
        """Swap the staged corpus and roll it back if source metadata cannot be saved."""
        assert self.stage is not None
        self._preserve_authored_files()
        self.raw_dir.rename(self.backup)
        try:
            self.stage.rename(self.raw_dir)
            result = finalize()
        except BaseException:
            if self.raw_dir.exists():
                self.raw_dir.rename(self.stage)
            self.backup.rename(self.raw_dir)
            raise
        try:
            shutil.rmtree(self.backup)
        except OSError:
            _LOG.warning("Confluence sync completed; the previous snapshot is retained for later cleanup")
        return result
