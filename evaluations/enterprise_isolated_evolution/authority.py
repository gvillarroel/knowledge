"""Exclusive campaign authority and durable native identity consumption.

The authority lock is held through admission, allocation, dispatch, native
qualification and finalization. A second launcher cannot acquire that lease.
An interrupted allocation stays consumed; no timeout or PID check frees it.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import stat
from typing import Any

from .planner import ProtocolError, digest


def safe_path(path: Path, root: Path) -> Path:
    """Reject path escape, symlinks and Windows reparse points before use."""
    root = root.absolute()
    path = path.absolute()
    try:
        path.relative_to(root)
    except ValueError as error:
        raise ProtocolError("Path escapes the declared authority root") from error
    current = path
    while True:
        if current.exists() or current.is_symlink():
            info = current.lstat()
            if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
                raise ProtocolError("Authority paths cannot contain links or reparse points")
        if current == root:
            break
        current = current.parent
    if not path.resolve().is_relative_to(root.resolve()):
        raise ProtocolError("Resolved authority path escaped")
    return path


class ExclusiveAuthority:
    """Hold one OS-backed lease across all campaign operations."""

    def __init__(self, path: Path, *, root: Path):
        self.path = safe_path(path, root)
        self.stream = None

    def __enter__(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.stream = self.path.open("a+b")
        try:
            if os.name == "nt":
                import msvcrt
                if self.path.stat().st_size == 0:
                    self.stream.write(b"\0")
                    self.stream.flush()
                self.stream.seek(0)
                msvcrt.locking(self.stream.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(self.stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as error:
            self.stream.close()
            self.stream = None
            raise ProtocolError("Another campaign authority holds the lease") from error
        return self

    def __exit__(self, *_):
        if self.stream is not None:
            self.stream.close()
            self.stream = None

    def require(self) -> None:
        """Reject dispatch after the authority lease was released."""
        if self.stream is None or self.stream.closed:
            raise ProtocolError("No active campaign authority lease")


class Journal:
    """Append hash-chained events and consume each native request once."""

    def __init__(self, path: Path, authority: ExclusiveAuthority, *, root: Path):
        authority.require()
        self.path = safe_path(path, root)
        self.authority = authority
        self.sequence = 0
        self.head = "0" * 64
        self.consumed: set[tuple[str, str, str]] = set()
        self.terminal = False
        self.path.parent.mkdir(parents=True, exist_ok=True)
        # Existing journals require a separately audited artifact recovery;
        # launching the same campaign never repeats pending native work.
        self.stream = self.path.open("x", encoding="utf-8", newline="\n")

    def append(self, kind: str, payload: dict[str, Any]) -> dict:
        """Persist an event before its corresponding side effect."""
        self.authority.require()
        if self.terminal:
            raise ProtocolError("Journal is terminal")
        event = {"sequence": self.sequence, "previous_sha256": self.head,
                 "kind": kind, "payload": payload}
        event["sha256"] = digest(event)
        self.stream.write(json.dumps(event, sort_keys=True, allow_nan=False) + "\n")
        self.stream.flush()
        os.fsync(self.stream.fileno())
        self.head = event["sha256"]
        self.sequence += 1
        self.terminal = kind == "terminal"
        return event

    def consume(self, request: dict) -> None:
        """Durably reserve one phase/family/candidate identity before dispatch."""
        key = (request["phase"], request.get("family", "joint"), request["candidate_id"])
        if key in self.consumed:
            raise ProtocolError("Native request identity already consumed")
        self.append("allocated", {"identity": list(key), "request_sha256": digest(request),
                                   "attempts": 1, "automatic_retries": 0})
        self.consumed.add(key)

    def close(self) -> None:
        """Close the append stream while retaining every event."""
        self.stream.close()


def verify_journal(path: Path) -> list[dict]:
    """Read an existing chain without repairing or reissuing its allocations."""
    head = "0" * 64
    events = []
    identities = set()
    terminal = False
    def unique(pairs):
        value = {}
        for key, item in pairs:
            if key in value:
                raise ProtocolError("Duplicate journal field")
            value[key] = item
        return value
    for line in path.read_text(encoding="utf-8").splitlines():
        event = json.loads(line, object_pairs_hook=unique)
        if terminal or set(event) != {"sequence", "previous_sha256", "kind", "payload", "sha256"}:
            raise ProtocolError("Invalid or post-terminal journal event")
        expected = event.pop("sha256")
        if type(event["sequence"]) is not int or event["sequence"] != len(events) or event["previous_sha256"] != head or digest(event) != expected:
            raise ProtocolError("Journal chain drift")
        event["sha256"] = head = expected
        if event["kind"] == "allocated":
            key = tuple(event["payload"]["identity"])
            if key in identities:
                raise ProtocolError("Duplicate native allocation")
            identities.add(key)
        terminal = event["kind"] == "terminal"
        events.append(event)
    return events
