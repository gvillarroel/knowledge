"""Exact public artifact bindings and exclusive, repository-scoped writes."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import sys

from .authority import safe_path
from .planner import ProtocolError

REPO = Path(__file__).resolve().parents[2]
PROFILE = "assets/retrieval-profile.json"
SKILL_NAME = "build-semantic-okf-knowledge-skill"


def parse_json(text: str | bytes):
    """Reject duplicate keys and nonfinite values in a protocol artifact."""
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ProtocolError("Duplicate JSON key")
            result[key] = value
        return result
    def invalid(_):
        raise ProtocolError("Nonfinite JSON")
    return json.loads(text, object_pairs_hook=unique, parse_constant=invalid)


def read(path: Path):
    """Read one regular JSON artifact with strict protocol parsing."""
    if path.is_symlink() or not path.is_file():
        raise ProtocolError("Missing or linked JSON artifact")
    return parse_json(path.read_text(encoding="utf-8"))


def write(path: Path, value) -> None:
    """Create one artifact exclusively inside the writable repository."""
    path = safe_path(path, REPO)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, sort_keys=True, indent=2, allow_nan=False)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())


def sha(path: Path) -> str:
    """Hash a regular file without following the final link."""
    if path.is_symlink() or not path.is_file():
        raise ProtocolError("Missing or linked source")
    result = hashlib.sha256()
    with path.open("rb") as stream:
        while block := stream.read(1024 * 1024):
            result.update(block)
    return result.hexdigest()


def inventory(root: Path) -> tuple[str, dict[str, str]]:
    """Use the official realizer's tree encoding, rejecting unsafe nodes."""
    safe_path(root, REPO)
    if not root.is_dir():
        raise ProtocolError("Missing bound tree")
    pending, entries = [root], []
    while pending:
        for node in os.scandir(pending.pop()):
            path, info = Path(node.path), node.stat(follow_symlinks=False)
            if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
                raise ProtocolError("Bound tree contains a link or reparse point")
            kind = "directory" if stat.S_ISDIR(info.st_mode) else "file" if stat.S_ISREG(info.st_mode) else None
            if kind is None:
                raise ProtocolError("Bound tree contains a special node")
            entries.append((path.relative_to(root).as_posix(), kind, path))
            if kind == "directory":
                pending.append(path)
    result, files = hashlib.sha256(), {}
    for relative, kind, path in sorted(entries, key=lambda item: (item[0].encode("utf-8"), item[1])):
        result.update((b"D\0" if kind == "directory" else b"F\0") + relative.encode("utf-8") + b"\0")
        if kind == "file":
            with path.open("rb") as stream:
                file_digest = hashlib.sha256()
                while block := stream.read(1024 * 1024):
                    result.update(block)
                    file_digest.update(block)
            result.update(b"\0")
            files[relative] = file_digest.hexdigest()
    return result.hexdigest(), files


def host(value: str | Path) -> Path:
    """Resolve the declared C-drive shared Windows/WSL path convention."""
    value = str(value)
    if os.name == "nt" and value.startswith("/mnt/c/"):
        return Path("C:/" + value[7:])
    if os.name != "nt" and value[:3].lower() in ("c:/", "c:\\"):
        return Path("/mnt/c/" + value[3:].replace("\\", "/"))
    return Path(value)


def posix(path: Path) -> str:
    """Return a shared WSL path without shell interpolation."""
    value = path.absolute().as_posix()
    return "/mnt/c/" + value[3:] if value[:3].lower() == "c:/" else value


def load(name: str, path: Path):
    """Load one precommitted implementation by its exact source path."""
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ProtocolError("Cannot load the declared authority")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module
