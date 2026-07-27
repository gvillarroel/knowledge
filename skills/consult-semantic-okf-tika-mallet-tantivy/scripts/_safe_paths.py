#!/usr/bin/env python3
"""Provide lexical, lstat-based path checks for the standalone consultant."""

from __future__ import annotations

import os
import stat
from pathlib import Path
from typing import Iterable


REPARSE_POINT = 0x0400


class UnsafePathError(RuntimeError):
    """Report a symbolic link, reparse point, or unsafe path overlap."""


def lexical_absolute(path: Path) -> Path:
    """Return an absolute path without resolving links or requiring existence."""

    return Path(os.path.abspath(os.fspath(path.expanduser())))


def is_link_or_reparse_stat(value: os.stat_result) -> bool:
    return stat.S_ISLNK(value.st_mode) or bool(
        getattr(value, "st_file_attributes", 0) & REPARSE_POINT
    )


def assert_no_links(
    path: Path,
    *,
    label: str,
    allow_missing_tail: bool = False,
) -> Path:
    """Reject links/reparse points in every existing path component."""

    absolute = lexical_absolute(path)
    current = Path(absolute.anchor)
    relative_parts = absolute.parts[1:] if absolute.anchor else absolute.parts
    missing = False
    for part in relative_parts:
        current = current / part
        if missing or not os.path.lexists(current):
            if not allow_missing_tail:
                raise UnsafePathError(f"{label} does not exist: {current}")
            missing = True
            continue
        try:
            value = os.lstat(current)
        except OSError as exc:
            raise UnsafePathError(f"cannot inspect {label}: {current}: {exc}") from exc
        if is_link_or_reparse_stat(value):
            raise UnsafePathError(
                f"{label} contains a symbolic link or reparse point: {current}"
            )
    return absolute


def require_regular_file(path: Path, *, label: str) -> Path:
    """Require a link-free regular file and return its lexical absolute path."""

    absolute = assert_no_links(path, label=label)
    value = os.lstat(absolute)
    if not stat.S_ISREG(value.st_mode):
        raise UnsafePathError(f"{label} is not a regular file: {absolute}")
    return absolute


def require_real_directory(path: Path, *, label: str) -> Path:
    """Require a link-free real directory and return its lexical absolute path."""

    absolute = assert_no_links(path, label=label)
    value = os.lstat(absolute)
    if not stat.S_ISDIR(value.st_mode):
        raise UnsafePathError(f"{label} is not a real directory: {absolute}")
    return absolute


def file_identity(path: Path) -> tuple[int, int]:
    """Return stable device/inode identity for a checked directory or file."""

    value = os.stat(path, follow_symlinks=False)
    if is_link_or_reparse_stat(value):
        raise UnsafePathError(f"unsafe path identity: {path}")
    return int(value.st_dev), int(value.st_ino)


def require_identity(path: Path, expected: tuple[int, int], *, label: str) -> None:
    """Fail when a path was swapped after its initial check."""

    assert_no_links(path, label=label)
    if file_identity(path) != expected:
        raise UnsafePathError(f"{label} identity changed during the operation")


def scan_regular_tree(
    root: Path, *, label: str
) -> tuple[list[Path], list[Path]]:
    """Walk without following links and reject every non-file/non-directory entry."""

    absolute = require_real_directory(root, label=label)
    files: list[Path] = []
    directories: list[Path] = []
    pending = [absolute]
    while pending:
        current = pending.pop()
        try:
            entries = list(os.scandir(current))
        except OSError as exc:
            raise UnsafePathError(f"cannot scan {label}: {current}: {exc}") from exc
        for entry in entries:
            path = Path(entry.path)
            try:
                value = entry.stat(follow_symlinks=False)
            except OSError as exc:
                raise UnsafePathError(f"cannot inspect {label}: {path}: {exc}") from exc
            if is_link_or_reparse_stat(value):
                raise UnsafePathError(
                    f"{label} contains a symbolic link or reparse point: {path}"
                )
            if stat.S_ISDIR(value.st_mode):
                directories.append(path)
                pending.append(path)
            elif stat.S_ISREG(value.st_mode):
                files.append(path)
            else:
                raise UnsafePathError(f"{label} contains an unsupported entry: {path}")
    key = lambda item: item.relative_to(absolute).as_posix()
    return sorted(files, key=key), sorted(directories, key=key)


def paths_overlap(left: Path, right: Path) -> bool:
    """Return true when either absolute lexical path contains the other."""

    left_absolute = lexical_absolute(left)
    right_absolute = lexical_absolute(right)
    try:
        left_absolute.relative_to(right_absolute)
        return True
    except ValueError:
        pass
    try:
        right_absolute.relative_to(left_absolute)
        return True
    except ValueError:
        return False


def reject_overlaps(path: Path, forbidden: Iterable[Path], *, label: str) -> None:
    """Reject a path equal to, inside, or containing any forbidden root."""

    for root in forbidden:
        if paths_overlap(path, root):
            raise UnsafePathError(f"{label} overlaps forbidden root: {root}")
