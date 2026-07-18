#!/usr/bin/env python3
"""Run a fair, append-only 320-cell consult-only Harbor campaign."""

from __future__ import annotations

import _thread
import argparse
import base64
import concurrent.futures
import contextlib
import ctypes
import errno
import functools
import hashlib
import json
import ntpath
import os
import platform
import queue
import re
import shutil
import socket
import stat
import subprocess
import sys
import threading
from collections import Counter, defaultdict
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
GRADER = HERE.parent / "semantic-okf-harbor" / "grader"
RUNTIME = HERE.parent / "semantic-okf-harbor" / "runtime"
RUNTIME_BUILD_RECEIPT = RUNTIME / "build/runtime-build.json"
PINNED_RUNTIME = RUNTIME / "pinned"
PINNED_RUNTIME_BUILD_RECEIPT = PINNED_RUNTIME / "build/runtime-build.json"

sys.path.insert(0, str(HERE))
sys.path.insert(0, str(GRADER))

import campaign_binding as frozen  # noqa: E402
import dataset_tool as data  # noqa: E402
import run_harbor as harbor_runner  # noqa: E402
from trace_status import classify_pi_trace, sanitize_provider_reset  # noqa: E402

DATASET = "graphrag-papers-40"
MODE = "consult-only"
INPUT_BINDING_SCHEMA_V1 = "semantic-okf-consult-campaign-input-bindings/1.0"
INPUT_BINDING_SCHEMA_V2 = "semantic-okf-consult-campaign-input-bindings/2.0"
QUESTION_IDS = tuple(f"q{number:03d}" for number in range(1, 41))
PROVIDER_ABORT_OUTCOMES = frozenset(
    {"provider-quota", "provider-rate-limit", "provider-error"}
)
INFRASTRUCTURE_ABORT_OUTCOMES = frozenset({"runner-error"})
ABORT_OUTCOMES = PROVIDER_ABORT_OUTCOMES | INFRASTRUCTURE_ABORT_OUTCOMES
PERSISTED_OUTCOME_FIELDS = (
    "binding_error_type",
    "error_code",
    "failure_domain",
    "outcome",
    "parsed_events",
    "run_exit_code",
    "stop_reason",
    "trace_path",
    "underlying_trace_error_code",
    "underlying_trace_failure_domain",
    "underlying_trace_outcome",
    "underlying_trace_provider_reset",
)
CHECKPOINT_TRIGGER_FIELDS = (
    "cohort",
    "error_code",
    "family",
    "outcome",
    "question_id",
    "sequence",
)


class CampaignRunError(ValueError):
    """Raised when a campaign cannot be run without breaking its contract."""


_LOCAL_OPERATION_LEASES: dict[str, int] = {}
_LOCAL_OPERATION_LEASES_GUARD = threading.Lock()


def _canonical_campaign_lock_identity(campaign: Path) -> str:
    """Return one Windows/WSL-stable campaign identity for global locking."""

    resolved = campaign.resolve()
    raw = str(resolved)
    if os.name == "nt":
        normalized = ntpath.normcase(ntpath.normpath(raw))
    else:
        match = re.fullmatch(r"/mnt/([A-Za-z])(?:/(.*))?", raw)
        if match:
            converted = subprocess.run(
                ["wslpath", "-w", raw],
                capture_output=True,
                text=True,
                check=False,
            )
            if converted.returncode != 0 or not converted.stdout.strip():
                raise CampaignRunError(
                    "cannot canonicalize the WSL campaign path for global locking"
                )
            normalized = ntpath.normcase(ntpath.normpath(converted.stdout.strip()))
        else:
            normalized = raw
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _operation_mutex_name(campaign: Path) -> str:
    return f"Global\\SemanticOKF-CampaignOperation-{_canonical_campaign_lock_identity(campaign)}"


@contextlib.contextmanager
def _native_windows_operation_mutex(name: str):
    """Hold one process-owned Windows kernel mutex without a filesystem path."""

    from ctypes import wintypes

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.CreateMutexW.argtypes = (wintypes.LPVOID, wintypes.BOOL, wintypes.LPCWSTR)
    kernel32.CreateMutexW.restype = wintypes.HANDLE
    kernel32.WaitForSingleObject.argtypes = (wintypes.HANDLE, wintypes.DWORD)
    kernel32.WaitForSingleObject.restype = wintypes.DWORD
    kernel32.ReleaseMutex.argtypes = (wintypes.HANDLE,)
    kernel32.ReleaseMutex.restype = wintypes.BOOL
    kernel32.CloseHandle.argtypes = (wintypes.HANDLE,)
    kernel32.CloseHandle.restype = wintypes.BOOL

    handle = kernel32.CreateMutexW(None, False, name)
    if not handle:
        raise CampaignRunError("cannot create the global campaign operation mutex")
    acquired = False
    try:
        status = kernel32.WaitForSingleObject(handle, 0)
        if status == 0x00000102:
            raise CampaignRunError("campaign operation lock is already held")
        if status not in {0x00000000, 0x00000080}:
            raise CampaignRunError(
                f"global campaign operation mutex wait failed: 0x{status:08x}"
            )
        acquired = True
        yield
    finally:
        if acquired and not kernel32.ReleaseMutex(handle):
            kernel32.CloseHandle(handle)
            raise CampaignRunError("cannot release the global campaign operation mutex")
        kernel32.CloseHandle(handle)


POWERSHELL_MUTEX_HELPER = r"""
$ErrorActionPreference = 'Stop'
$name = [Environment]::GetEnvironmentVariable('SEMANTIC_OKF_OPERATION_MUTEX')
$mutex = [Threading.Mutex]::new($false, $name)
$acquired = $false
try {
    try {
        $acquired = $mutex.WaitOne(0)
    } catch [Threading.AbandonedMutexException] {
        $acquired = $true
    }
    if (-not $acquired) {
        [Console]::Out.WriteLine('busy')
        [Console]::Out.Flush()
        exit 73
    }
    [Console]::Out.WriteLine('acquired')
    [Console]::Out.Flush()
    [Console]::In.ReadToEnd() | Out-Null
} finally {
    if ($acquired) {
        $mutex.ReleaseMutex()
    }
    $mutex.Dispose()
}
""".strip()


@contextlib.contextmanager
def _wsl_windows_operation_mutex(name: str):
    """Hold the shared Windows mutex through one stdin-bound helper process."""

    executable = shutil.which("powershell.exe")
    if executable is None:
        raise CampaignRunError("WSL cannot access powershell.exe for the global mutex")
    encoded = base64.b64encode(
        POWERSHELL_MUTEX_HELPER.encode("utf-16-le")
    ).decode("ascii")
    environment = dict(os.environ)
    environment["SEMANTIC_OKF_OPERATION_MUTEX"] = name
    inherited = [item for item in environment.get("WSLENV", "").split(":") if item]
    inherited.append("SEMANTIC_OKF_OPERATION_MUTEX")
    environment["WSLENV"] = ":".join(dict.fromkeys(inherited))
    process = subprocess.Popen(
        [
            executable,
            "-NoLogo",
            "-NoProfile",
            "-NonInteractive",
            "-EncodedCommand",
            encoded,
        ],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=environment,
    )
    assert process.stdout is not None
    handshake: queue.Queue[str] = queue.Queue(maxsize=1)
    reader = threading.Thread(
        target=lambda: handshake.put(process.stdout.readline()), daemon=True
    )
    reader.start()
    intentional_release = threading.Event()
    unexpected_exit = threading.Event()
    monitor: threading.Thread | None = None
    try:
        try:
            state = handshake.get(timeout=15).strip()
        except queue.Empty as exc:
            process.kill()
            process.wait(timeout=10)
            raise CampaignRunError("global campaign mutex helper did not become ready") from exc
        if state == "busy":
            process.wait(timeout=10)
            raise CampaignRunError("campaign operation lock is already held")
        if state != "acquired" or process.poll() is not None:
            process.kill()
            process.wait(timeout=10)
            raise CampaignRunError("global campaign mutex helper failed to acquire")
        def monitor_helper() -> None:
            process.wait()
            if not intentional_release.is_set():
                unexpected_exit.set()
                _thread.interrupt_main()

        monitor = threading.Thread(target=monitor_helper, daemon=True)
        monitor.start()
        try:
            yield
        except KeyboardInterrupt as exc:
            if unexpected_exit.is_set():
                raise CampaignRunError(
                    "global campaign mutex helper exited while held"
                ) from exc
            raise
        if unexpected_exit.is_set():
            raise CampaignRunError("global campaign mutex helper exited while held")
        if process.poll() is not None:
            raise CampaignRunError("global campaign mutex helper exited while held")
    finally:
        intentional_release.set()
        if process.poll() is None:
            assert process.stdin is not None
            process.stdin.close()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired as exc:
                process.kill()
                process.wait(timeout=10)
                raise CampaignRunError(
                    "global campaign mutex helper did not release"
                ) from exc
        if monitor is not None:
            monitor.join(timeout=1)
        if process.returncode not in {0, 73}:
            assert process.stderr is not None
            detail = process.stderr.read().strip()
            raise CampaignRunError(
                "global campaign mutex helper failed"
                + (f": {detail}" if detail else "")
            )


@contextlib.contextmanager
def _campaign_operation_lease(campaign: Path):
    """Hold a path-independent, crash-releasing campaign operation lease."""

    name = _operation_mutex_name(campaign)
    pid = os.getpid()
    with _LOCAL_OPERATION_LEASES_GUARD:
        if _LOCAL_OPERATION_LEASES.get(name) == pid:
            raise CampaignRunError("campaign operation lock is already held")
        _LOCAL_OPERATION_LEASES[name] = pid
    try:
        if os.name == "nt":
            with _native_windows_operation_mutex(name):
                yield
            return
        if not sys.platform.startswith("linux"):
            raise CampaignRunError("campaign operation locking is unsupported")

        address = b"\0semantic-okf-operation-" + _canonical_campaign_lock_identity(
            campaign
        ).encode("ascii")
        lease = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        lease.set_inheritable(False)
        try:
            try:
                lease.bind(address)
            except OSError as exc:
                if exc.errno == errno.EADDRINUSE:
                    raise CampaignRunError("campaign operation lock is already held") from exc
                raise CampaignRunError(
                    "cannot acquire the Linux campaign operation lease"
                ) from exc
            if re.fullmatch(r"/mnt/[A-Za-z](?:/.*)?", str(campaign.resolve())):
                with _wsl_windows_operation_mutex(name):
                    yield
            else:
                yield
        finally:
            lease.close()
    finally:
        with _LOCAL_OPERATION_LEASES_GUARD:
            if _LOCAL_OPERATION_LEASES.get(name) == pid:
                del _LOCAL_OPERATION_LEASES[name]


@contextlib.contextmanager
def campaign_operation_lock(campaign: Path, owner: str):
    """Hold one crash-releasing cross-process lease for execution or migration."""

    campaign = campaign.resolve()
    campaign.mkdir(parents=True, exist_ok=True)
    lock_path = campaign / ".campaign-operation.lock"
    if lock_path.is_symlink() or (lock_path.exists() and not lock_path.is_file()):
        raise CampaignRunError(f"campaign operation lock path is unsafe: {lock_path}")
    with _campaign_operation_lease(campaign):
        payload = canonical_json_bytes(
            {
                "acquired_at": datetime.now(timezone.utc).isoformat(),
                "lease": "path-independent-os-lease",
                "mutex_name_sha256": hashlib.sha256(
                    _operation_mutex_name(campaign).encode("utf-8")
                ).hexdigest(),
                "owner": owner,
                "pid": os.getpid(),
                "schema_version": "semantic-okf-campaign-operation-lock/2.0",
            }
        )
        flags = os.O_RDWR | os.O_CREAT | getattr(os, "O_BINARY", 0)
        if os.name == "posix":
            flags |= os.O_NOFOLLOW | getattr(os, "O_CLOEXEC", 0)
        try:
            descriptor = os.open(lock_path, flags, 0o600)
        except OSError as exc:
            raise CampaignRunError(
                f"cannot open campaign operation record: {lock_path}"
            ) from exc
        try:
            metadata = os.fstat(descriptor)
            if not stat.S_ISREG(metadata.st_mode) or metadata.st_nlink != 1:
                raise CampaignRunError(
                    f"campaign operation record path is unsafe: {lock_path}"
                )
            with os.fdopen(descriptor, "r+b", closefd=False) as stream:
                stream.seek(0)
                stream.truncate()
                stream.write(payload)
                stream.flush()
                os.fsync(descriptor)
                yield
                stream.seek(0)
                if stream.read() != payload:
                    raise CampaignRunError("campaign operation record identity changed")
                try:
                    current = lock_path.lstat()
                except OSError as exc:
                    raise CampaignRunError(
                        "campaign operation record became unreadable"
                    ) from exc
                if (
                    not stat.S_ISREG(current.st_mode)
                    or current.st_nlink != 1
                    or (current.st_dev, current.st_ino)
                    != (metadata.st_dev, metadata.st_ino)
                ):
                    raise CampaignRunError(
                        "campaign operation record path identity changed"
                    )
        finally:
            os.close(descriptor)


def _campaign_locked(function):
    """Decorate a campaign execution entrypoint with the shared operation lease."""

    @functools.wraps(function)
    def guarded(schedule, campaign, settings, *args, **kwargs):
        with campaign_operation_lock(Path(campaign), "execute"):
            return function(schedule, campaign, settings, *args, **kwargs)

    return guarded


@dataclass(frozen=True)
class RunSettings:
    """Immutable settings passed to each one-task Harbor shard."""

    auth_file: Path
    hf_cache: Path | None
    harbor: str = "harbor"
    docker: str = "docker"
    max_concurrency: int = 4


ShardExecutor = Callable[[Mapping[str, Any], Path, RunSettings], dict[str, Any]]
BindingVerifier = Callable[[Mapping[str, Any], Path, Sequence[str] | None], str]


def canonical_json_bytes(value: Mapping[str, Any]) -> bytes:
    """Serialize a mapping as stable, human-readable UTF-8 JSON bytes."""

    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def schedule_digest(schedule: Mapping[str, Any]) -> str:
    """Return the SHA-256 digest of the exact canonical schedule bytes."""

    return hashlib.sha256(canonical_json_bytes(schedule)).hexdigest()


def build_schedule(
    dataset_id: str = DATASET,
    *,
    cohorts: Mapping[str, Sequence[str]] | None = None,
    families: Sequence[str] | None = None,
) -> dict[str, Any]:
    """Build the deterministic, position-balanced 40-by-8 campaign schedule."""

    if cohorts is None:
        dataset = data.load_dataset(dataset_id)
        cohorts = data.dataset_cohorts(dataset)
    if families is None:
        families = sorted(data.load_families())

    ordered_families = sorted(families)
    if len(ordered_families) != 8 or len(set(ordered_families)) != 8:
        raise CampaignRunError("a consult campaign requires exactly eight unique families")

    question_cohorts: dict[str, str] = {}
    for cohort, identifiers in cohorts.items():
        for identifier in identifiers:
            if identifier in question_cohorts:
                raise CampaignRunError(f"question appears in multiple cohorts: {identifier}")
            question_cohorts[identifier] = cohort
    if tuple(sorted(question_cohorts)) != QUESTION_IDS:
        raise CampaignRunError("the campaign requires exactly q001 through q040")

    cells: list[dict[str, Any]] = []
    sequence = 0
    for question_index, question_id in enumerate(QUESTION_IDS):
        rotation = question_index % len(ordered_families)
        rotated = ordered_families[rotation:] + ordered_families[:rotation]
        for family_index, family in enumerate(rotated):
            sequence += 1
            question_wave = family_index // 4 + 1
            cells.append(
                {
                    "cohort": question_cohorts[question_id],
                    "family": family,
                    "family_position": family_index + 1,
                    "position_in_wave": family_index % 4 + 1,
                    "question_id": question_id,
                    "question_wave": question_wave,
                    "rotation": rotation,
                    "sequence": sequence,
                    "shard_path": (
                        f"runs/{sequence:04d}-{question_id}-{family}"
                    ),
                    "wave_index": question_index * 2 + question_wave,
                }
            )

    schedule: dict[str, Any] = {
        "cell_count": len(cells),
        "cells": cells,
        "dataset_id": dataset_id,
        "families": ordered_families,
        "family_count": len(ordered_families),
        "mode": MODE,
        "question_count": len(QUESTION_IDS),
        "rotation_policy": "left-rotate-one-family-per-question",
        "schema_version": "semantic-okf-consult-campaign-schedule/1.0",
        "wave_size": 4,
    }
    validate_schedule(schedule)
    return schedule


def validate_schedule(schedule: Mapping[str, Any]) -> None:
    """Validate coverage, uniqueness, order, and positional balance of a schedule."""

    cells = schedule.get("cells")
    families = schedule.get("families")
    if not isinstance(cells, list) or not isinstance(families, list):
        raise CampaignRunError("schedule cells and families must be lists")
    if len(cells) != 320 or len(families) != 8:
        raise CampaignRunError("schedule must contain 320 cells across eight families")
    if families != sorted(families) or len(set(families)) != 8:
        raise CampaignRunError("schedule families must be unique and sorted")
    if (
        type(schedule.get("cell_count")) is not int
        or type(schedule.get("question_count")) is not int
        or schedule.get("cell_count") != 320
        or schedule.get("question_count") != 40
    ):
        raise CampaignRunError("schedule summary counts do not match its fixed matrix")

    observed_pairs: set[tuple[str, str]] = set()
    positions: Counter[tuple[str, int]] = Counter()
    waves: Counter[tuple[str, int]] = Counter()
    question_cohorts: dict[str, str] = {}
    expected_sequence = 1
    for cell in cells:
        if not isinstance(cell, Mapping):
            raise CampaignRunError("each schedule cell must be an object")
        integer_fields = (
            "family_position",
            "position_in_wave",
            "question_wave",
            "rotation",
            "sequence",
            "wave_index",
        )
        if any(type(cell.get(field)) is not int for field in integer_fields):
            raise CampaignRunError("schedule cell numeric fields must be integers")
        if cell.get("sequence") != expected_sequence:
            raise CampaignRunError("schedule sequence must be contiguous and ordered")
        expected_sequence += 1
        question = cell.get("question_id")
        family = cell.get("family")
        position = cell.get("family_position")
        question_wave = cell.get("question_wave")
        if question not in QUESTION_IDS or family not in families:
            raise CampaignRunError("schedule cell has an unknown question or family")
        question_index = (expected_sequence - 2) // 8
        family_index = (expected_sequence - 2) % 8
        rotation = question_index % 8
        expected_family_order = families[rotation:] + families[:rotation]
        expected_shape = {
            "family": expected_family_order[family_index],
            "family_position": family_index + 1,
            "position_in_wave": family_index % 4 + 1,
            "question_id": QUESTION_IDS[question_index],
            "question_wave": family_index // 4 + 1,
            "rotation": rotation,
            "shard_path": (
                f"runs/{int(cell['sequence']):04d}-{QUESTION_IDS[question_index]}-"
                f"{expected_family_order[family_index]}"
            ),
            "wave_index": question_index * 2 + family_index // 4 + 1,
        }
        if any(cell.get(key) != value for key, value in expected_shape.items()):
            raise CampaignRunError("schedule cell violates its deterministic rotation policy")
        prior_cohort = question_cohorts.setdefault(str(question), str(cell.get("cohort")))
        if prior_cohort != cell.get("cohort"):
            raise CampaignRunError(f"question changes cohort within its family cells: {question}")
        pair = (question, family)
        if pair in observed_pairs:
            raise CampaignRunError(f"duplicate schedule cell: {question}/{family}")
        observed_pairs.add(pair)
        positions[(family, position)] += 1
        waves[(family, question_wave)] += 1

    expected_pairs = {(question, family) for question in QUESTION_IDS for family in families}
    if observed_pairs != expected_pairs:
        raise CampaignRunError("schedule does not cover the complete question-family matrix")
    if any(positions[(family, position)] != 5 for family in families for position in range(1, 9)):
        raise CampaignRunError("each family must occupy every position exactly five times")
    if any(waves[(family, wave)] != 20 for family in families for wave in (1, 2)):
        raise CampaignRunError("each family must appear in each four-task wave twenty times")


def persist_schedule(campaign: Path, schedule: Mapping[str, Any]) -> str:
    """Persist or verify an immutable schedule and its sidecar SHA before execution."""

    validate_schedule(schedule)
    campaign.mkdir(parents=True, exist_ok=True)
    schedule_path = campaign / "schedule.json"
    digest_path = campaign / "schedule.sha256"
    payload = canonical_json_bytes(schedule)
    digest = hashlib.sha256(payload).hexdigest()

    if schedule_path.exists() or digest_path.exists():
        if not schedule_path.is_file() or not digest_path.is_file():
            raise CampaignRunError("campaign has an incomplete persisted schedule binding")
        if schedule_path.read_bytes() != payload:
            raise CampaignRunError(
                "persisted campaign schedule differs from the requested schedule"
            )
        recorded = digest_path.read_text(encoding="utf-8").strip().split()[0]
        if recorded != digest or hashlib.sha256(schedule_path.read_bytes()).hexdigest() != digest:
            raise CampaignRunError("persisted campaign schedule SHA-256 does not verify")
        return digest

    _write_bytes_exclusive(schedule_path, payload)
    _write_bytes_exclusive(digest_path, f"{digest}  schedule.json\n".encode("ascii"))
    return digest


def runtime_build_binding(expected_tag: str) -> dict[str, Any]:
    """Validate and bind the checked local Harbor runtime build receipt."""

    if not RUNTIME_BUILD_RECEIPT.is_file():
        raise CampaignRunError(
            f"runtime build receipt is absent: {RUNTIME_BUILD_RECEIPT}"
        )
    receipt = data.load_json(RUNTIME_BUILD_RECEIPT)
    expected = {
        "schema_version": "semantic-okf-harbor-runtime-build/1.0",
        "image_tag": expected_tag,
        "dockerfile_sha256": data.sha256_file(RUNTIME / "Dockerfile"),
        "requirements_sha256": data.sha256_file(RUNTIME / "requirements.txt"),
        "model_weights_in_image": False,
    }
    if any(receipt.get(key) != value for key, value in expected.items()):
        raise CampaignRunError("runtime build receipt or build inputs drifted")
    image_id = receipt.get("image_id")
    if (
        not isinstance(image_id, str)
        or not image_id.startswith("sha256:")
        or len(image_id) != 71
        or any(character not in "0123456789abcdef" for character in image_id[7:])
    ):
        raise CampaignRunError("runtime build receipt has an invalid image ID")
    return {
        "runtime_build_receipt_sha256": data.sha256_file(RUNTIME_BUILD_RECEIPT),
        "runtime_image_id": image_id,
        "runtime_dockerfile_sha256": str(receipt["dockerfile_sha256"]),
        "runtime_requirements_sha256": str(receipt["requirements_sha256"]),
    }


def pinned_runtime_build_binding(expected_image_id: str) -> dict[str, Any]:
    """Validate the exact Node/Pi-preinstalled runtime used by frozen campaigns."""

    if not PINNED_RUNTIME_BUILD_RECEIPT.is_file():
        raise CampaignRunError(
            f"pinned runtime build receipt is absent: {PINNED_RUNTIME_BUILD_RECEIPT}"
        )
    receipt = data.load_json(PINNED_RUNTIME_BUILD_RECEIPT)
    expected_top = {
        "schema_version": "semantic-okf-harbor-pinned-runtime-build/2.0",
        "image_tag": "semantic-okf-harbor-runtime:2.0",
        "image_id": expected_image_id,
        "model_weights_in_image": False,
    }
    if any(receipt.get(key) != value for key, value in expected_top.items()):
        raise CampaignRunError("pinned runtime build receipt identity drift")
    if (
        not expected_image_id.startswith("sha256:")
        or not frozen.SHA256.fullmatch(expected_image_id[7:])
    ):
        raise CampaignRunError("pinned runtime build receipt has an invalid image ID")
    input_files = receipt.get("input_files")
    expected_names = {
        "dockerfile",
        "requirements",
        "package_json",
        "package_lock",
        "receipt_schema",
    }
    if not isinstance(input_files, Mapping) or set(input_files) != expected_names:
        raise CampaignRunError("pinned runtime input-file receipt is incomplete")
    verified_inputs: dict[str, dict[str, str]] = {}
    for name in sorted(expected_names):
        row = input_files[name]
        if not isinstance(row, Mapping):
            raise CampaignRunError("pinned runtime input-file receipt is malformed")
        relative = row.get("path")
        if not isinstance(relative, str):
            raise CampaignRunError("pinned runtime input-file path is malformed")
        pure = Path(*frozen._safe_relative(relative, "pinned runtime input").parts)
        path = (RUNTIME / pure).resolve()
        if RUNTIME.resolve() not in path.parents or not path.is_file():
            raise CampaignRunError("pinned runtime input-file path escapes its root")
        digest = data.sha256_file(path)
        if row.get("sha256") != digest:
            raise CampaignRunError(f"pinned runtime input drift: {relative}")
        verified_inputs[name] = {"path": relative, "sha256": digest}
    node = receipt.get("node")
    pi = receipt.get("pi_coding_agent")
    python = receipt.get("python")
    if not isinstance(node, Mapping) or not isinstance(pi, Mapping) or not isinstance(python, Mapping):
        raise CampaignRunError("pinned runtime language identities are incomplete")
    if (
        f"v{node.get('version')}" != frozen.NODE_VERSION
        or node.get("archive_sha256")
        != "9749e988f437343b7fa832c69ded82a312e41a03116d766797ac14f6f9eee578"
        or pi.get("package") != frozen.PI_PACKAGE
        or pi.get("version") != frozen.PI_VERSION
        or pi.get("integrity") != frozen.PI_NPM_INTEGRITY
        or python.get("version") != "3.12.13"
    ):
        raise CampaignRunError("pinned runtime Node, Pi, or Python identity drift")
    return {
        "runtime_build_receipt_sha256": data.sha256_file(
            PINNED_RUNTIME_BUILD_RECEIPT
        ),
        "runtime_image_id": expected_image_id,
        "runtime_image_tag": str(receipt["image_tag"]),
        "runtime_input_files": verified_inputs,
        "runtime_node": dict(node),
        "runtime_pi_coding_agent": dict(pi),
        "runtime_python": dict(python),
    }


def _resolved_executable(command: str, label: str) -> Path:
    candidate = shutil.which(command)
    path = Path(candidate or command).expanduser().resolve()
    if not path.is_file():
        raise CampaignRunError(f"{label} executable is absent: {command}")
    return path


def _checked_command_output(command: Sequence[str], label: str) -> str:
    completed = subprocess.run(
        list(command),
        cwd=REPO,
        capture_output=True,
        text=True,
        check=False,
    )
    value = completed.stdout.strip()
    if completed.returncode != 0 or not value:
        raise CampaignRunError(f"cannot identify the selected {label}")
    return value


def _harbor_dependency_inventory(interpreter: Path) -> dict[str, Any]:
    script = (
        "import importlib.metadata as m,json;"
        "rows=sorted((d.metadata.get('Name','').lower().replace('_','-'),d.version) "
        "for d in m.distributions());"
        "print(json.dumps(rows,separators=(',',':')))"
    )
    raw = _checked_command_output([str(interpreter), "-c", script], "Harbor dependencies")
    try:
        rows = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise CampaignRunError("Harbor dependency inventory is not JSON") from exc
    if (
        not isinstance(rows, list)
        or not rows
        or any(
            not isinstance(row, list)
            or len(row) != 2
            or not all(isinstance(value, str) and value for value in row)
            for row in rows
        )
        or rows != sorted(rows)
    ):
        raise CampaignRunError("Harbor dependency inventory is malformed")
    payload = json.dumps(rows, ensure_ascii=True, separators=(",", ":")).encode("ascii")
    return {
        "count": len(rows),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "packages": rows,
    }


def host_runtime_binding(settings: RunSettings) -> dict[str, Any]:
    """Bind the host executables and dependency inventory that submit each shard."""

    campaign_python = Path(sys.executable).resolve()
    harbor = _resolved_executable(settings.harbor, "Harbor")
    docker = _resolved_executable(settings.docker, "Docker")
    vendor = REPO / "vendor/harbor"
    expected_entrypoint = REPO / "vendor/harbor-cli"
    if not vendor.is_dir() or harbor != expected_entrypoint:
        raise CampaignRunError("frozen campaigns must use their campaign-local Harbor adapter")
    try:
        shebang = harbor.read_text(encoding="utf-8").splitlines()[0]
    except (OSError, UnicodeError, IndexError) as exc:
        raise CampaignRunError("campaign Harbor adapter has no Python shebang") from exc
    if not shebang.startswith("#!/"):
        raise CampaignRunError("campaign Harbor adapter has no absolute Python shebang")
    harbor_python = Path(shebang[2:]).expanduser()
    if not harbor_python.is_absolute() or not harbor_python.is_file():
        raise CampaignRunError("campaign Harbor adapter interpreter is absent")
    harbor_version = _checked_command_output([str(harbor), "--version"], "Harbor")
    if harbor_version != frozen.HARBOR_VERSION:
        raise CampaignRunError("campaign Harbor adapter version drift")
    return {
        "campaign_python": {
            "implementation": platform.python_implementation(),
            "version": platform.python_version(),
            "executable_sha256": data.sha256_file(campaign_python),
        },
        "harbor": {
            "version": harbor_version,
            "entrypoint": "frozen/repo/vendor/harbor-cli",
            "entrypoint_sha256": data.sha256_file(harbor),
            "interpreter_sha256": data.sha256_file(harbor_python),
            "distribution_tree_sha256": data.tree_digest(vendor),
            "dependencies": _harbor_dependency_inventory(harbor_python),
        },
        "docker": {
            "version": _checked_command_output([str(docker), "--version"], "Docker"),
            "executable_sha256": data.sha256_file(docker),
        },
    }


def pipeline_source_binding() -> dict[str, str]:
    """Hash the exact frozen Python pipeline used by the campaign."""

    result: dict[str, str] = {}
    for relative in frozen.PIPELINE_SOURCE_PATHS:
        path = REPO / Path(*Path(relative).parts)
        if not path.is_file():
            raise CampaignRunError(f"frozen pipeline source is absent: {relative}")
        result[relative] = data.sha256_file(path)
    return result


def execution_contract(settings: RunSettings) -> dict[str, Any]:
    """Return the closed, redacted Harbor orchestration policy."""

    return {
        "campaign_max_concurrency": settings.max_concurrency,
        "shard_attempts": 1,
        "shard_concurrency": 1,
        "harbor_retries": 0,
        "agent": {
            "name": "pi",
            "model": harbor_runner.MODEL,
            "pi_version": harbor_runner.PI_VERSION,
            "thinking": "high",
        },
        "mounts": {
            "knowledge": {"target": "/knowledge", "read_only": True},
            "hf_cache": {
                "source": "frozen/model-cache/hub",
                "target": "/models/huggingface/hub",
                "read_only": True,
                "families": ["embeddings", "ensemble"],
            },
            "authentication": {
                "target": "/root/.pi/agent",
                "serialized": False,
                "continuity": "binding-scoped-shared-session",
                "credential_slot": "openai-codex",
            },
        },
        "task_root": "frozen/repo/evaluations/semantic-okf-datasets/generated/tasks",
        "skills_root": "frozen/repo/skills",
        "runtime_image_reference": "content-addressed-local-tag",
        "runtime_image_identity_check": "before-and-after-each-wave",
    }


def verify_local_runtime_image(
    docker: str, expected_reference: str, expected_image_id: str | None = None
) -> str:
    """Require the live Docker reference to resolve to its bound immutable image ID."""

    if expected_image_id is not None:
        if frozen.runtime_image_reference(expected_image_id) != expected_reference:
            raise CampaignRunError("runtime image reference does not encode its bound ID")
        pinned_runtime_build_binding(expected_image_id)
    elif expected_reference.startswith("sha256:"):
        pinned_runtime_build_binding(expected_reference)
        expected_image_id = expected_reference
    else:
        binding = runtime_build_binding(expected_reference)
        expected_image_id = str(binding["runtime_image_id"])
    completed = subprocess.run(
        [docker, "image", "inspect", "--format", "{{.Id}}", expected_reference],
        cwd=REPO,
        capture_output=True,
        text=True,
        check=False,
    )
    image_id = completed.stdout.strip() if completed.returncode == 0 else ""
    if image_id != expected_image_id:
        raise CampaignRunError(
            "local Harbor runtime image does not match runtime-build.json"
        )
    return image_id


def family_input_binding(
    schedule: Mapping[str, Any], campaign: Path, family: str
) -> dict[str, Any]:
    """Hash one family's exact generated tasks, bundle, and consultation skill."""

    metadata = data.load_families().get(family)
    if not isinstance(metadata, Mapping):
        raise CampaignRunError(f"unknown campaign family: {family}")
    task_root = (
        HERE
        / "generated/tasks"
        / str(schedule["dataset_id"])
        / MODE
        / family
    )
    task_manifest_path = task_root / "manifest.json"
    if not task_manifest_path.is_file():
        raise CampaignRunError(f"generated task manifest is absent: {task_manifest_path}")
    task_manifest = data.load_json(task_manifest_path)
    expected_identity = {
        "dataset_id": schedule["dataset_id"],
        "family": family,
        "mode": MODE,
    }
    if any(task_manifest.get(key) != value for key, value in expected_identity.items()):
        raise CampaignRunError(f"generated task manifest identity drift: {task_manifest_path}")

    bundle = campaign / "bundles" / family
    ledger = bundle / "semantic/records.jsonl"
    if not ledger.is_file():
        raise CampaignRunError(f"family-specific bundle is incomplete: {bundle}")
    bundle_hash = data.tree_digest(bundle)
    records_hash = data.sha256_file(ledger)
    if (
        bundle_hash != task_manifest.get("reference_bundle_tree_sha256")
        or records_hash != task_manifest.get("reference_records_sha256")
    ):
        raise CampaignRunError(f"{family} bundle differs from its corrected task manifest")

    skill_name = str(metadata["consult_skill"])
    skill = REPO / "skills" / skill_name
    if not (skill / "SKILL.md").is_file():
        raise CampaignRunError(f"consultation skill is incomplete: {skill}")
    runtime_image = task_manifest.get("runtime_image")
    if not isinstance(runtime_image, str) or not runtime_image:
        raise CampaignRunError(f"generated task manifest has no runtime image: {task_manifest_path}")
    return {
        "consult_skill": skill_name,
        "consult_skill_tree_sha256": data.tree_digest(skill),
        "generated_tasks_tree_sha256": data.tree_digest(task_root),
        "reference_bundle_tree_sha256": bundle_hash,
        "reference_records_sha256": records_hash,
        "runtime_image": runtime_image,
        "task_manifest_sha256": data.sha256_file(task_manifest_path),
    }


def _v1_input_bindings(
    schedule: Mapping[str, Any], campaign: Path
) -> dict[str, Any]:
    """Build the legacy binding retained only for forensic compatibility."""

    family_bindings = {
        family: family_input_binding(schedule, campaign, family)
        for family in schedule["families"]
    }
    runtime_images = {row["runtime_image"] for row in family_bindings.values()}
    if len(runtime_images) != 1:
        raise CampaignRunError("campaign task manifests do not share one runtime image")
    runtime_image = next(iter(runtime_images))
    return {
        "schema_version": INPUT_BINDING_SCHEMA_V1,
        "dataset_id": schedule["dataset_id"],
        "mode": MODE,
        "schedule_sha256": schedule_digest(schedule),
        "model": harbor_runner.MODEL,
        "pi_version": harbor_runner.PI_VERSION,
        "thinking": "high",
        "runtime_image": runtime_image,
        **runtime_build_binding(runtime_image),
        "grader_tree_sha256": data.tree_digest(GRADER),
        "families_registry_sha256": data.sha256_file(data.FAMILIES_PATH),
        "families": family_bindings,
    }


def _offline_model_key(model: Mapping[str, Any]) -> str:
    return f"{model['model_id']}@{model['revision']}"


def _v2_family_binding(
    schedule: Mapping[str, Any],
    campaign: Path,
    family: str,
    model_key: str,
) -> dict[str, Any]:
    result = family_input_binding(schedule, campaign, family)
    result["offline_model_snapshot"] = (
        model_key if family in {"embeddings", "ensemble"} else None
    )
    return result


def _v2_top_binding(
    schedule: Mapping[str, Any],
    campaign: Path,
    settings: RunSettings,
    *,
    verify_model: bool,
) -> tuple[dict[str, Any], str]:
    manifest = frozen.verify_frozen_inputs(campaign, verify_model=verify_model)
    model = manifest["offline_model"]
    if not isinstance(model, Mapping):
        raise CampaignRunError("frozen campaign model descriptor is malformed")
    model_key = _offline_model_key(model)
    runtime = manifest["task_runtime"]
    if not isinstance(runtime, Mapping):
        raise CampaignRunError("frozen campaign task runtime binding is malformed")
    runtime_image = runtime.get("runtime_image_reference")
    runtime_image_id = runtime.get("runtime_image_id")
    if not isinstance(runtime_image, str) or not isinstance(runtime_image_id, str):
        raise CampaignRunError("frozen campaign has no complete runtime image identity")
    descriptor = REPO / "evaluations/semantic-okf-datasets/datasets" / f"{DATASET}.json"
    summarizer = REPO / "evaluations/semantic-okf-datasets/summarize_consult_campaign.py"
    frozen_manifest_path = campaign / "frozen-inputs.json"
    top = {
        "schema_version": INPUT_BINDING_SCHEMA_V2,
        "dataset_id": schedule["dataset_id"],
        "mode": MODE,
        "schedule_sha256": schedule_digest(schedule),
        "model": harbor_runner.MODEL,
        "pi_version": harbor_runner.PI_VERSION,
        "thinking": "high",
        "runtime_image": runtime_image,
        "runtime_image_id": runtime_image_id,
        "runtime_build": pinned_runtime_build_binding(runtime_image_id),
        "grader_tree_sha256": data.tree_digest(GRADER),
        "families_registry_sha256": data.sha256_file(data.FAMILIES_PATH),
        "dataset_descriptor_sha256": data.sha256_file(descriptor),
        "pipeline_sources_sha256": pipeline_source_binding(),
        "host_runtime": host_runtime_binding(settings),
        "execution_contract": execution_contract(settings),
        "frozen_inputs": {
            "manifest_sha256": data.sha256_file(frozen_manifest_path),
            "source_campaign": manifest["source_campaign"],
            "frozen_repo": manifest["frozen_repo"],
            "task_runtime": manifest["task_runtime"],
            "harbor_adapter": manifest["harbor_adapter"],
        },
        "offline_model_snapshots": {model_key: dict(model)},
        "auditor": {
            "summarizer_sha256": data.sha256_file(summarizer),
            "grader_tree_sha256": data.tree_digest(GRADER),
        },
    }
    return top, model_key


def _v2_input_bindings(
    schedule: Mapping[str, Any], campaign: Path, settings: RunSettings
) -> dict[str, Any]:
    top, model_key = _v2_top_binding(
        schedule, campaign, settings, verify_model=True
    )
    family_bindings = {
        family: _v2_family_binding(schedule, campaign, family, model_key)
        for family in schedule["families"]
    }
    runtime_images = {row["runtime_image"] for row in family_bindings.values()}
    if runtime_images != {top["runtime_image"]}:
        raise CampaignRunError("frozen campaign task manifests changed runtime image")
    return {**top, "families": family_bindings}


def build_input_bindings(
    schedule: Mapping[str, Any],
    campaign: Path,
    settings: RunSettings | None = None,
) -> dict[str, Any]:
    """Build the immutable pre-call binding for every campaign treatment input."""

    validate_schedule(schedule)
    if (campaign / "frozen-inputs.json").exists():
        if settings is None:
            raise CampaignRunError("input-binding v2 requires explicit run settings")
        return _v2_input_bindings(schedule, campaign, settings)
    return _v1_input_bindings(schedule, campaign)


def persist_input_bindings(
    schedule: Mapping[str, Any],
    campaign: Path,
    settings: RunSettings | None = None,
) -> str:
    """Persist or verify the exact immutable campaign input-binding manifest."""

    bindings = build_input_bindings(schedule, campaign, settings)
    payload = canonical_json_bytes(bindings)
    digest = hashlib.sha256(payload).hexdigest()
    path = campaign / "input-bindings.json"
    digest_path = campaign / "input-bindings.sha256"
    if path.exists() or digest_path.exists():
        if not path.is_file() or not digest_path.is_file():
            raise CampaignRunError("campaign has an incomplete input-binding manifest")
        if path.read_bytes() != payload:
            raise CampaignRunError("campaign inputs differ from their immutable binding manifest")
        recorded = digest_path.read_text(encoding="ascii").strip().split()[0]
        if recorded != digest or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise CampaignRunError("campaign input-binding SHA-256 does not verify")
        return digest
    _write_bytes_exclusive(path, payload)
    _write_bytes_exclusive(
        digest_path, f"{digest}  input-bindings.json\n".encode("ascii")
    )
    return digest


def verify_input_bindings(
    schedule: Mapping[str, Any],
    campaign: Path,
    families: Sequence[str] | None = None,
    *,
    settings: RunSettings | None = None,
) -> str:
    """Recheck persisted bindings globally or for the families in one live wave."""

    path = campaign / "input-bindings.json"
    digest_path = campaign / "input-bindings.sha256"
    if not path.is_file() or not digest_path.is_file():
        raise CampaignRunError("campaign input bindings must be persisted before execution")
    recorded = data.load_json(path)
    payload = canonical_json_bytes(recorded)
    actual_digest = hashlib.sha256(path.read_bytes()).hexdigest()
    canonical_digest = hashlib.sha256(payload).hexdigest()
    try:
        sidecar_digest = digest_path.read_text(encoding="ascii").strip().split()[0]
    except (OSError, UnicodeError, IndexError) as exc:
        raise CampaignRunError("campaign input-binding sidecar is unreadable") from exc
    if actual_digest != canonical_digest or sidecar_digest != actual_digest:
        raise CampaignRunError("campaign input-binding SHA-256 does not verify")
    runtime_image = recorded.get("runtime_image")
    if not isinstance(runtime_image, str) or not runtime_image:
        raise CampaignRunError("campaign input binding has no runtime image")
    recorded_families = recorded.get("families")
    if not isinstance(recorded_families, Mapping) or set(recorded_families) != set(
        schedule["families"]
    ):
        raise CampaignRunError("campaign input-binding family matrix drift")
    selected = list(families) if families is not None else list(schedule["families"])
    if len(selected) != len(set(selected)) or any(
        family not in schedule["families"] for family in selected
    ):
        raise CampaignRunError("input-binding verification requested unknown families")
    schema = recorded.get("schema_version")
    if schema == INPUT_BINDING_SCHEMA_V2:
        if settings is None:
            raise CampaignRunError("input-binding v2 verification requires run settings")
        verify_model = families is None or bool(
            {"embeddings", "ensemble"}.intersection(selected)
        )
        expected_top, model_key = _v2_top_binding(
            schedule, campaign, settings, verify_model=verify_model
        )
        expected_keys = set(expected_top) | {"families"}
        if set(recorded) != expected_keys or any(
            recorded.get(key) != value for key, value in expected_top.items()
        ):
            raise CampaignRunError("campaign input-binding v2 global identity drift")
        for family in selected:
            if _v2_family_binding(schedule, campaign, family, model_key) != recorded_families.get(family):
                raise CampaignRunError(f"campaign input binding drift for {family}")
    elif schema == INPUT_BINDING_SCHEMA_V1:
        expected_top = {
            "schema_version": INPUT_BINDING_SCHEMA_V1,
            "dataset_id": schedule["dataset_id"],
            "mode": MODE,
            "schedule_sha256": schedule_digest(schedule),
            "model": harbor_runner.MODEL,
            "pi_version": harbor_runner.PI_VERSION,
            "thinking": "high",
            "grader_tree_sha256": data.tree_digest(GRADER),
            "families_registry_sha256": data.sha256_file(data.FAMILIES_PATH),
            "runtime_image": runtime_image,
            **runtime_build_binding(runtime_image),
        }
        if any(recorded.get(key) != value for key, value in expected_top.items()):
            raise CampaignRunError("campaign input-binding runtime identity drift")
        for family in selected:
            if family_input_binding(schedule, campaign, family) != recorded_families.get(family):
                raise CampaignRunError(f"campaign input binding drift for {family}")
    else:
        raise CampaignRunError("campaign input-binding schema is unsupported")
    runtime_images = {
        row.get("runtime_image")
        for row in recorded_families.values()
        if isinstance(row, Mapping)
    }
    if runtime_images != {recorded.get("runtime_image")}:
        raise CampaignRunError("campaign input-binding runtime image drift")
    return actual_digest


def build_shard_command(
    cell: Mapping[str, Any], campaign: Path, settings: RunSettings
) -> list[str]:
    """Build the existing runner invocation for one append-only task shard."""

    family = str(cell["family"])
    bindings = data.load_json(campaign / "input-bindings.json")
    frozen_execution = bindings.get("schema_version") == INPUT_BINDING_SCHEMA_V2
    command = [
        sys.executable,
        str(HERE / "run_harbor.py"),
        "--dataset",
        DATASET,
        "--family",
        family,
        "--mode",
        MODE,
        "--cohort",
        str(cell["cohort"]),
        "--task-id",
        str(cell["question_id"]),
        "--bundle",
        str((campaign / "bundles" / family).resolve()),
        "--auth-file",
        str(settings.auth_file.expanduser().resolve()),
        "--attempts",
        "1",
        "--output",
        str((campaign / str(cell["shard_path"])).resolve()),
        "--harbor",
        settings.harbor,
    ]
    if frozen_execution:
        command.extend(
            [
                "--frozen-campaign",
                "--input-bindings",
                str((campaign / "input-bindings.json").resolve()),
                "--consult-skill",
                str((REPO / "skills" / data.load_families()[family]["consult_skill"]).resolve()),
            ]
        )
    family_metadata = data.load_families()[family]
    if family_metadata["requires_hf_cache"]:
        if settings.hf_cache is None:
            raise CampaignRunError(f"{family} requires --hf-cache")
        command.extend(["--hf-cache", str(settings.hf_cache.expanduser().resolve())])
    return command


def classify_shard_output(
    shard: Path,
    returncode: int | None,
    question_id: str | None = None,
) -> dict[str, Any]:
    """Classify the one Pi trace in a shard without persisting answer content."""

    all_traces = sorted(shard.glob("**/artifacts/pi.jsonl")) if shard.is_dir() else []
    traces = (
        sorted(shard.glob(f"{question_id}__*/artifacts/pi.jsonl"))
        if shard.is_dir() and question_id is not None
        else all_traces
    )
    if all_traces != traces:
        return {
            "error_code": "off_contract_pi_trace",
            "failure_domain": "runner",
            "outcome": "runner-error",
            "run_exit_code": returncode,
            "trace_path": None,
        }
    if any(
        trace.is_symlink()
        or trace.parent.is_symlink()
        or trace.parent.parent.is_symlink()
        for trace in traces
    ):
        return {
            "error_code": "symlinked_pi_trace",
            "failure_domain": "runner",
            "outcome": "runner-error",
            "run_exit_code": returncode,
            "trace_path": None,
        }
    if len(traces) != 1:
        return {
            "error_code": "missing_pi_trace" if not traces else "multiple_pi_traces",
            "failure_domain": "runner",
            "outcome": "runner-error",
            "run_exit_code": returncode,
            "trace_path": None,
        }
    classified = dict(classify_pi_trace(traces[0]))
    classified.pop("answer_text", None)
    if (
        returncode not in (None, 0)
        and classified.get("outcome")
        not in {
            "provider-quota",
            "provider-rate-limit",
            "provider-context-limit",
            "provider-error",
        }
    ):
        classified["underlying_trace_outcome"] = classified.get("outcome")
        classified["underlying_trace_failure_domain"] = classified.get(
            "failure_domain"
        )
        classified["underlying_trace_error_code"] = classified.get("error_code")
        reset = classified.get("provider_reset")
        if isinstance(reset, Mapping):
            classified["underlying_trace_provider_reset"] = reset
        classified["outcome"] = "runner-error"
        classified["failure_domain"] = "runner"
        classified["error_code"] = "nonzero_runner_exit"
    classified["run_exit_code"] = returncode
    classified["trace_path"] = traces[0].relative_to(shard).as_posix()
    return classified


def run_shard(
    cell: Mapping[str, Any], campaign: Path, settings: RunSettings
) -> dict[str, Any]:
    """Invoke one live one-task shard, or recover its existing trace without duplication."""

    shard = campaign / str(cell["shard_path"])
    log_path = campaign / "launcher-logs" / f"{int(cell['sequence']):04d}.log"
    if shard.exists():
        return classify_shard_output(
            shard,
            _recovered_shard_exit_code(cell, campaign, shard),
            str(cell["question_id"]),
        )
    if log_path.exists():
        return {
            "error_code": "prior_launch_without_shard",
            "failure_domain": "runner",
            "outcome": "runner-error",
            "run_exit_code": None,
            "trace_path": None,
        }

    command = build_shard_command(cell, campaign, settings)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("x", encoding="utf-8", newline="\n") as log:
        completed = subprocess.run(
            command,
            cwd=REPO,
            stdout=log,
            stderr=subprocess.STDOUT,
            check=False,
            text=True,
        )
    return classify_shard_output(
        shard, completed.returncode, str(cell["question_id"])
    )


def _validate_recovered_shard_identity(
    cell: Mapping[str, Any], campaign: Path, shard: Path
) -> dict[str, Any]:
    """Apply the complete frozen audit contract before reusing an existing shard."""

    import summarize_consult_campaign as auditor

    family = str(cell["family"])
    cohort = str(cell["cohort"])
    question_id = str(cell["question_id"])
    if shard.is_symlink() or not shard.is_dir():
        raise CampaignRunError("existing shard path is unsafe")
    relative_shard = Path(str(cell["shard_path"]))
    cursor = campaign
    for part in relative_shard.parts:
        cursor = cursor / part
        if cursor.is_symlink():
            raise CampaignRunError("existing shard path contains a symlink")
    expected_shard = (campaign / str(cell["shard_path"])).resolve()
    if shard.resolve() != expected_shard:
        raise CampaignRunError("existing shard path differs from its scheduled cell")
    for identity_name in ("config.json", "job-config.redacted.json", "run-receipt.json"):
        identity_path = shard / identity_name
        if identity_path.is_symlink():
            raise CampaignRunError(
                f"existing shard identity path is a symlink: {identity_path}"
            )
    bindings_path = campaign / "input-bindings.json"
    if not bindings_path.is_file():
        raise CampaignRunError("existing shard campaign has no input binding manifest")
    bindings = data.load_json(bindings_path)
    family_bindings = bindings.get("families")
    input_binding = (
        family_bindings.get(family)
        if isinstance(family_bindings, Mapping)
        else None
    )
    if not isinstance(input_binding, Mapping):
        raise CampaignRunError(
            f"existing shard campaign has no input binding for {family}"
        )
    tasks_root = HERE / "generated/tasks" / DATASET / MODE
    try:
        task_manifest = auditor.scheduled_task_manifests(
            tasks_root, DATASET, [family]
        )[family]
        receipt = auditor.validate_run_identity(
            shard,
            dataset_id=DATASET,
            family=family,
            cohort=cohort,
            task_ids=[question_id],
            allow_partial=False,
        )
        if receipt is None:  # pragma: no cover - fail-closed type narrowing
            raise CampaignRunError("existing shard identity is incomplete")
        expected_skill = data.load_families()[family]["consult_skill"]
        auditor.validate_scheduled_receipt(
            shard,
            receipt,
            expected_skill=expected_skill,
            task_manifest=task_manifest,
            input_binding=input_binding,
            input_bindings_sha256=data.sha256_file(bindings_path),
            runtime_image_id=bindings.get("runtime_image_id"),
        )
    except auditor.SummaryError as exc:
        raise CampaignRunError(
            f"existing shard fails its frozen identity contract: {shard}"
        ) from exc
    return receipt


def _recovered_shard_exit_code(
    cell: Mapping[str, Any], campaign: Path, shard: Path
) -> int:
    """Recover the effective wrapper exit from a fully audited shard receipt."""

    receipt_path = shard / "run-receipt.json"
    if not receipt_path.is_file():
        raise CampaignRunError(f"existing shard has no run receipt: {shard}")
    receipt = _validate_recovered_shard_identity(cell, campaign, shard)
    harbor_exit_code = receipt.get("harbor_exit_code")
    terminal_outcomes = receipt.get("terminal_outcomes")
    if (
        not isinstance(harbor_exit_code, int)
        or isinstance(harbor_exit_code, bool)
        or not isinstance(terminal_outcomes, Mapping)
        or any(
            not isinstance(name, str)
            or not isinstance(count, int)
            or isinstance(count, bool)
            or count <= 0
            for name, count in terminal_outcomes.items()
        )
    ):
        raise CampaignRunError(f"existing shard has invalid completion metadata: {shard}")
    observed_outcomes = harbor_runner.completed_trace_outcomes(shard)
    question_id = str(cell["question_id"])
    all_traces = sorted(shard.glob("**/artifacts/pi.jsonl"))
    scheduled_traces = sorted(shard.glob(f"{question_id}__*/artifacts/pi.jsonl"))
    if all_traces != scheduled_traces:
        raise CampaignRunError(f"existing shard has an off-contract Pi trace: {shard}")
    if any(
        trace.is_symlink()
        or trace.parent.is_symlink()
        or trace.parent.parent.is_symlink()
        for trace in scheduled_traces
    ):
        raise CampaignRunError(f"existing shard has a symlinked Pi trace: {shard}")
    if dict(terminal_outcomes) != observed_outcomes:
        raise CampaignRunError(f"existing shard receipt differs from its traces: {shard}")
    completion = harbor_runner.completion_status(harbor_exit_code, observed_outcomes)
    if (
        receipt.get("provider_failure_detected")
        is not completion["provider_failure_detected"]
        or receipt.get("run_status") != completion["run_status"]
    ):
        raise CampaignRunError(f"existing shard completion status is inconsistent: {shard}")
    return int(completion["effective_exit_code"])


def _validate_recovered_outcome(
    cell: Mapping[str, Any], campaign: Path, outcome: Mapping[str, Any]
) -> None:
    """Re-audit a persisted outcome before it can skip its scheduled live cell."""

    shard = campaign / str(cell["shard_path"])
    if shard.exists() and (shard.is_symlink() or not shard.is_dir()):
        raise CampaignRunError(f"persisted outcome shard path is unsafe: {shard}")
    if not shard.is_dir():
        if (
            outcome.get("outcome") != "runner-error"
            or outcome.get("failure_domain") != "runner"
            or not isinstance(outcome.get("error_code"), str)
            or not outcome.get("error_code")
            or outcome.get("trace_path") is not None
            or outcome.get("run_exit_code") is not None
            or any(key.startswith("underlying_trace_") for key in outcome)
        ):
            raise CampaignRunError(
                f"persisted outcome has no auditable scheduled shard: {shard}"
            )
        return
    _recovered_shard_exit_code(cell, campaign, shard)
    receipt = data.load_json(shard / "run-receipt.json")
    import summarize_consult_campaign as auditor

    try:
        auditor._validate_v3_scheduled_completion(shard, outcome, receipt)
    except auditor.SummaryError as exc:
        raise CampaignRunError(
            f"persisted outcome fails its recovered shard audit: {shard}"
        ) from exc


@_campaign_locked
def execute_campaign(
    schedule: Mapping[str, Any],
    campaign: Path,
    settings: RunSettings,
    *,
    shard_executor: ShardExecutor | None = None,
    binding_verifier: BindingVerifier | None = None,
    prepared_bindings_digest: str | None = None,
) -> dict[str, Any]:
    """Execute a persisted schedule with a synchronous preflight and bounded waves."""

    validate_schedule(schedule)
    if not 1 <= settings.max_concurrency <= 4:
        raise CampaignRunError("max concurrency must be between one and four")
    digest = persist_schedule(campaign, schedule)
    if binding_verifier is None:
        if prepared_bindings_digest is None:
            input_bindings_digest = persist_input_bindings(
                schedule, campaign, settings
            )
        else:
            bindings_path = campaign / "input-bindings.json"
            sidecar_path = campaign / "input-bindings.sha256"
            if not bindings_path.is_file() or not sidecar_path.is_file():
                raise CampaignRunError("prepared campaign input binding is incomplete")
            actual_digest = data.sha256_file(bindings_path)
            try:
                sidecar_digest = (
                    sidecar_path.read_text(encoding="ascii").strip().split()[0]
                )
            except (OSError, UnicodeError, IndexError) as exc:
                raise CampaignRunError(
                    "prepared campaign input-binding sidecar is unreadable"
                ) from exc
            if actual_digest != prepared_bindings_digest or sidecar_digest != actual_digest:
                raise CampaignRunError("prepared campaign input-binding digest drift")
            input_bindings_digest = prepared_bindings_digest

        def verify_bindings(
            checked_schedule: Mapping[str, Any],
            checked_campaign: Path,
            checked_families: Sequence[str] | None,
        ) -> str:
            return verify_input_bindings(
                checked_schedule,
                checked_campaign,
                checked_families,
                settings=settings,
            )

        persisted_bindings = data.load_json(campaign / "input-bindings.json")
        bound_runtime_image = str(persisted_bindings["runtime_image"])
        bound_runtime_image_id = (
            str(persisted_bindings["runtime_image_id"])
            if persisted_bindings.get("schema_version") == INPUT_BINDING_SCHEMA_V2
            else None
        )
    else:
        verify_bindings = binding_verifier
        input_bindings_digest = verify_bindings(schedule, campaign, None)
        bound_runtime_image = None
        bound_runtime_image_id = None

    def verify_wave_bindings(families: Sequence[str]) -> None:
        verify_bindings(schedule, campaign, families)
        if bound_runtime_image is not None:
            verify_local_runtime_image(
                settings.docker, bound_runtime_image, bound_runtime_image_id
            )

    executor = shard_executor or run_shard
    cells = list(schedule["cells"])
    outcomes = _load_outcomes(campaign, cells)
    if shard_executor is None:
        for cell in cells:
            outcome = outcomes.get(int(cell["sequence"]))
            if outcome is not None:
                _validate_recovered_outcome(cell, campaign, outcome)
    completed_path = campaign / "checkpoints/completed.json"
    aborted_path = campaign / "checkpoints/aborted.json"
    checkpoints_root = campaign / "checkpoints"
    if checkpoints_root.exists():
        if checkpoints_root.is_symlink() or not checkpoints_root.is_dir():
            raise CampaignRunError("terminal checkpoint root is unsafe")
        for entry in checkpoints_root.iterdir():
            if (
                entry.name not in {"aborted.json", "completed.json"}
                or entry.is_symlink()
                or not entry.is_file()
            ):
                raise CampaignRunError(f"unexpected terminal checkpoint artifact: {entry}")
    for checkpoint_path in (completed_path, aborted_path):
        if checkpoint_path.exists() and not checkpoint_path.is_file():
            raise CampaignRunError(
                f"terminal checkpoint path is not a file: {checkpoint_path}"
            )
    if completed_path.exists() and aborted_path.exists():
        raise CampaignRunError("campaign has conflicting terminal checkpoints")

    prior_abort = _first_abort(outcomes.values())
    if prior_abort is not None:
        if completed_path.exists():
            raise CampaignRunError(
                "completed checkpoint conflicts with an aborting outcome"
            )
        return _persist_terminal_checkpoint(
            campaign,
            "aborted",
            digest,
            outcomes,
            trigger=prior_abort,
            input_bindings_digest=input_bindings_digest,
        )
    if aborted_path.exists():
        raise CampaignRunError("aborted checkpoint exists without an aborting outcome")
    if completed_path.is_file():
        if len(outcomes) != len(cells):
            raise CampaignRunError("completed checkpoint exists without all task outcomes")
        return _persist_terminal_checkpoint(
            campaign,
            "completed",
            digest,
            outcomes,
            input_bindings_digest=input_bindings_digest,
        )

    first = cells[0]
    first_sequence = int(first["sequence"])
    if first_sequence not in outcomes:
        # The first real model call is intentionally synchronous and is also cell 1.
        try:
            verify_wave_bindings([str(first["family"])])
        except Exception as exc:  # noqa: BLE001 - persist a stable pre-call abort
            outcome = _binding_failure_outcome(exc)
            outcomes[first_sequence] = _persist_outcome(campaign, first, outcome)
            return _persist_terminal_checkpoint(
                campaign,
                "aborted",
                digest,
                outcomes,
                trigger=outcomes[first_sequence],
                input_bindings_digest=input_bindings_digest,
            )
        outcome = _execute_safely(executor, first, campaign, settings)
        try:
            verify_wave_bindings([str(first["family"])])
        except Exception as exc:  # noqa: BLE001 - reject a mid-call input mutation
            outcome = _binding_failure_outcome(exc, underlying=outcome)
        outcomes[first_sequence] = _persist_outcome(campaign, first, outcome)
    trigger = _first_abort(outcomes.values())
    if trigger is not None:
        return _persist_terminal_checkpoint(
            campaign,
            "aborted",
            digest,
            outcomes,
            trigger=trigger,
            input_bindings_digest=input_bindings_digest,
        )

    cells_by_wave: dict[int, list[Mapping[str, Any]]] = defaultdict(list)
    for cell in cells[1:]:
        if int(cell["sequence"]) not in outcomes:
            cells_by_wave[int(cell["wave_index"])].append(cell)

    for wave_index in sorted(cells_by_wave):
        wave_cells = cells_by_wave[wave_index]
        try:
            verify_wave_bindings(
                [str(cell["family"]) for cell in wave_cells]
            )
        except Exception as exc:  # noqa: BLE001 - persist a stable pre-call abort
            cell = wave_cells[0]
            sequence = int(cell["sequence"])
            outcomes[sequence] = _persist_outcome(
                campaign, cell, _binding_failure_outcome(exc)
            )
            return _persist_terminal_checkpoint(
                campaign,
                "aborted",
                digest,
                outcomes,
                trigger=outcomes[sequence],
                input_bindings_digest=input_bindings_digest,
            )
        new_outcomes, trigger = _execute_wave(
            wave_cells,
            campaign,
            settings,
            executor,
        )
        try:
            verify_wave_bindings([str(cell["family"]) for cell in wave_cells])
        except Exception as exc:  # noqa: BLE001 - reject a mid-wave input mutation
            new_outcomes = [
                (cell, _binding_failure_outcome(exc, underlying=outcome))
                for cell, outcome in new_outcomes
            ]
            trigger = _bind_outcome(new_outcomes[0][0], new_outcomes[0][1])
        for cell, outcome in new_outcomes:
            sequence = int(cell["sequence"])
            outcomes[sequence] = _persist_outcome(campaign, cell, outcome)
        if trigger is not None:
            return _persist_terminal_checkpoint(
                campaign,
                "aborted",
                digest,
                outcomes,
                trigger=trigger,
                input_bindings_digest=input_bindings_digest,
            )

    if len(outcomes) != len(cells):
        raise CampaignRunError("campaign stopped without a terminal outcome for every cell")
    return _persist_terminal_checkpoint(
        campaign,
        "completed",
        digest,
        outcomes,
        input_bindings_digest=input_bindings_digest,
    )


def validate_live_inputs(
    schedule: Mapping[str, Any],
    campaign: Path,
    settings: RunSettings,
    *,
    auth: bool,
    verify_frozen: bool = True,
) -> None:
    """Check all local task, bundle, cache, and optional authentication inputs up front."""

    for family in schedule["families"]:
        bundle = campaign / "bundles" / family
        if not (bundle / "semantic/records.jsonl").is_file():
            raise CampaignRunError(f"family-specific bundle is incomplete: {bundle}")
    if settings.hf_cache is None or not settings.hf_cache.expanduser().is_dir():
        raise CampaignRunError("--hf-cache must name an existing cache for embeddings and ensemble")
    frozen_manifest = campaign / "frozen-inputs.json"
    if frozen_manifest.is_file():
        expected_repo = (campaign / "frozen/repo").resolve()
        expected_hf = (campaign / "frozen/model-cache/hub").resolve()
        expected_harbor = (expected_repo / "vendor/harbor-cli").resolve()
        if REPO.resolve() != expected_repo:
            raise CampaignRunError("frozen campaign must run its campaign-local pipeline")
        if settings.hf_cache.expanduser().resolve() != expected_hf:
            raise CampaignRunError("frozen campaign must mount only its campaign-local HF closure")
        if _resolved_executable(settings.harbor, "Harbor") != expected_harbor:
            raise CampaignRunError("frozen campaign must use its campaign-local Harbor adapter")
        manifest = (
            frozen.verify_frozen_inputs(campaign)
            if verify_frozen
            else frozen.load_frozen_inputs(campaign)
        )
        runtime = manifest.get("task_runtime")
        runtime_image = runtime.get("runtime_image_reference") if isinstance(runtime, Mapping) else None
        runtime_image_id = runtime.get("runtime_image_id") if isinstance(runtime, Mapping) else None
        if not isinstance(runtime_image, str) or not isinstance(runtime_image_id, str):
            raise CampaignRunError("frozen campaign task runtime identity is incomplete")
        verify_local_runtime_image(settings.docker, runtime_image, runtime_image_id)
    if auth and not settings.auth_file.expanduser().is_file():
        raise CampaignRunError(f"Pi authentication file is absent: {settings.auth_file}")
    for cell in schedule["cells"]:
        task = (
            HERE
            / "generated/tasks"
            / str(schedule["dataset_id"])
            / MODE
            / str(cell["family"])
            / str(cell["cohort"])
            / str(cell["question_id"])
            / "task.toml"
        )
        if not task.is_file():
            raise CampaignRunError(f"generated campaign task is absent: {task}")
    if auth and not frozen_manifest.is_file():
        first_family = str(schedule["families"][0])
        manifest = data.load_json(
            HERE
            / "generated/tasks"
            / str(schedule["dataset_id"])
            / MODE
            / first_family
            / "manifest.json"
        )
        runtime_image = manifest.get("runtime_image")
        if not isinstance(runtime_image, str):
            raise CampaignRunError("generated tasks have no runtime image")
        verify_local_runtime_image(settings.docker, runtime_image)


def _validate_auth_file(path: Path) -> None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise CampaignRunError("Pi authentication file is not valid UTF-8 JSON") from exc
    if not isinstance(value, Mapping) or not value.get("openai-codex"):
        raise CampaignRunError("Pi authentication file has no openai-codex credential")


def prepare_binding_scoped_auth(
    source: Path,
    binding_digest: str,
    *,
    session_root: Path | None = None,
) -> Path:
    """Create or reuse one private non-artifact auth copy for the whole campaign."""

    if not frozen.SHA256.fullmatch(binding_digest):
        raise CampaignRunError("cannot scope authentication to an invalid binding digest")
    source = source.expanduser().resolve()
    _validate_auth_file(source)
    root = session_root or harbor_runner.FROZEN_AUTH_SESSION_ROOT
    root = root.resolve()
    session = root / binding_digest
    target = session / "auth.json"
    root.mkdir(parents=True, exist_ok=True)
    root.chmod(stat.S_IRWXU)
    session.mkdir(mode=stat.S_IRWXU, exist_ok=True)
    session.chmod(stat.S_IRWXU)
    if target.exists():
        if target.is_symlink() or not target.is_file():
            raise CampaignRunError("binding-scoped authentication path is unsafe")
        _validate_auth_file(target)
        target.chmod(stat.S_IRUSR | stat.S_IWUSR)
        return target
    payload = source.read_bytes()
    with target.open("xb") as stream:
        stream.write(payload)
    target.chmod(stat.S_IRUSR | stat.S_IWUSR)
    _validate_auth_file(target)
    return target


def remove_binding_scoped_auth(path: Path, *, session_root: Path | None = None) -> None:
    """Remove a terminal campaign's private auth session without touching artifacts."""

    root = (
        session_root or harbor_runner.FROZEN_AUTH_SESSION_ROOT
    ).resolve()
    session = path.resolve().parent
    if session.parent != root or not frozen.SHA256.fullmatch(session.name):
        raise CampaignRunError("refusing to remove an unexpected authentication path")
    shutil.rmtree(session)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse fair consult campaign orchestration arguments."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--campaign", type=Path, required=True)
    parser.add_argument("--dataset", choices=[DATASET], default=DATASET)
    parser.add_argument("--auth-file", type=Path, default=Path.home() / ".pi/agent/auth.json")
    parser.add_argument("--hf-cache", type=Path)
    parser.add_argument("--harbor", default="harbor")
    parser.add_argument("--docker", default="docker")
    parser.add_argument("--max-concurrency", type=int, default=1)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--schedule-only", action="store_true")
    args = parser.parse_args(argv)
    if not 1 <= args.max_concurrency <= 4:
        parser.error("--max-concurrency must be between 1 and 4")
    return args


def main(argv: Sequence[str] | None = None) -> int:
    """Persist a fair schedule, optionally validate it, and run live shards."""

    args = parse_args(argv)
    campaign = args.campaign.expanduser().resolve()
    try:
        schedule = build_schedule(args.dataset)
        digest = persist_schedule(campaign, schedule)
        settings = RunSettings(
            auth_file=args.auth_file,
            hf_cache=args.hf_cache,
            harbor=args.harbor,
            docker=args.docker,
            max_concurrency=args.max_concurrency,
        )
        if args.schedule_only:
            result = {"schedule_sha256": digest, "status": "schedule-only"}
            print(json.dumps(result, sort_keys=True))
            return 0
        if args.dry_run:
            validate_live_inputs(
                schedule, campaign, settings, auth=False, verify_frozen=False
            )
            bindings_digest = persist_input_bindings(schedule, campaign, settings)
            verify_input_bindings(schedule, campaign, None, settings=settings)
            print(
                json.dumps(
                    {
                        "input_bindings_sha256": bindings_digest,
                        "schedule_sha256": digest,
                        "status": "dry-run",
                    },
                    sort_keys=True,
                )
            )
            return 0
        if os.name != "posix":
            raise CampaignRunError("live Harbor execution must run inside Linux or WSL")
        if not (campaign / "frozen-inputs.json").is_file():
            raise CampaignRunError(
                "live consult campaigns require frozen input-binding schema v2"
            )
        if settings.max_concurrency != 1:
            raise CampaignRunError(
                "frozen live campaigns require sequential shards for auth continuity"
            )
        validate_live_inputs(
            schedule, campaign, settings, auth=True, verify_frozen=False
        )
        bindings_digest = persist_input_bindings(schedule, campaign, settings)
        session_auth = prepare_binding_scoped_auth(settings.auth_file, bindings_digest)
        session_settings = replace(settings, auth_file=session_auth)
        checkpoint = execute_campaign(
            schedule,
            campaign,
            session_settings,
            prepared_bindings_digest=bindings_digest,
        )
        remove_binding_scoped_auth(session_auth)
        print(json.dumps(checkpoint, sort_keys=True))
        return 0 if checkpoint["status"] == "completed" else 2
    except (CampaignRunError, data.DatasetError, frozen.BindingError, OSError) as exc:
        raise SystemExit(str(exc)) from exc


def _write_bytes_exclusive(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(payload)


def _outcome_path(campaign: Path, sequence: int) -> Path:
    return campaign / "outcomes" / f"{sequence:04d}.json"


def _load_outcomes(
    campaign: Path, cells: Sequence[Mapping[str, Any]]
) -> dict[int, dict[str, Any]]:
    outcomes: dict[int, dict[str, Any]] = {}
    outcomes_root = campaign / "outcomes"
    expected_names = {f"{int(cell['sequence']):04d}.json" for cell in cells}
    if outcomes_root.exists():
        if outcomes_root.is_symlink() or not outcomes_root.is_dir():
            raise CampaignRunError("persisted outcomes root is unsafe")
        for entry in outcomes_root.iterdir():
            if (
                entry.name not in expected_names
                or entry.is_symlink()
                or not entry.is_file()
            ):
                raise CampaignRunError(f"unexpected persisted outcome artifact: {entry}")
    for cell in cells:
        sequence = int(cell["sequence"])
        path = _outcome_path(campaign, sequence)
        if not path.exists():
            continue
        outcome = data.load_json(path)
        identity = {
            "cohort": cell["cohort"],
            "family": cell["family"],
            "question_id": cell["question_id"],
            "sequence": sequence,
        }
        if (
            type(outcome.get("sequence")) is not int
            or any(outcome.get(key) != value for key, value in identity.items())
        ):
            raise CampaignRunError(f"persisted outcome identity mismatch: {path}")
        if (
            not {
                "error_code",
                "failure_domain",
                "outcome",
                "run_exit_code",
                "trace_path",
            }.issubset(outcome)
            or _bind_outcome(cell, outcome) != outcome
            or canonical_json_bytes(outcome) != path.read_bytes()
        ):
            raise CampaignRunError(f"persisted outcome has an invalid closed shape: {path}")
        outcomes[sequence] = outcome
    return outcomes


def _execute_safely(
    executor: ShardExecutor,
    cell: Mapping[str, Any],
    campaign: Path,
    settings: RunSettings,
) -> dict[str, Any]:
    try:
        return executor(cell, campaign, settings)
    except Exception as exc:  # noqa: BLE001 - worker failures become durable outcomes
        return {
            "error_code": type(exc).__name__,
            "failure_domain": "runner",
            "outcome": "runner-error",
            "run_exit_code": None,
            "trace_path": None,
        }


def _binding_failure_outcome(
    exc: BaseException, *, underlying: Mapping[str, Any] | None = None
) -> dict[str, Any]:
    """Return one redacted runner outcome for immutable input-binding drift."""

    result = {
        "error_code": "input_binding_drift",
        "failure_domain": "runner",
        "outcome": "runner-error",
        "run_exit_code": None,
        "trace_path": None,
        "binding_error_type": type(exc).__name__,
    }
    if underlying is not None:
        result.update(
            {
                key: underlying[key]
                for key in ("parsed_events", "run_exit_code", "stop_reason", "trace_path")
                if key in underlying
            }
        )
        trace_outcome = underlying.get(
            "underlying_trace_outcome", underlying.get("outcome")
        )
        if isinstance(trace_outcome, str):
            result["underlying_trace_outcome"] = trace_outcome
            result["underlying_trace_failure_domain"] = underlying.get(
                "underlying_trace_failure_domain", underlying.get("failure_domain")
            )
            result["underlying_trace_error_code"] = underlying.get(
                "underlying_trace_error_code", underlying.get("error_code")
            )
            reset = underlying.get(
                "underlying_trace_provider_reset", underlying.get("provider_reset")
            )
            if (
                trace_outcome == "provider-quota"
                and result["underlying_trace_error_code"] == "usage_limit_reached"
                and isinstance(reset, Mapping)
            ):
                sanitized = sanitize_provider_reset(
                    reset.get("at"), reset.get("remaining_seconds")
                )
                if sanitized is not None:
                    result["underlying_trace_provider_reset"] = sanitized
    return result


def _execute_wave(
    cells: Sequence[Mapping[str, Any]],
    campaign: Path,
    settings: RunSettings,
    executor: ShardExecutor,
) -> tuple[list[tuple[Mapping[str, Any], dict[str, Any]]], dict[str, Any] | None]:
    pending = iter(cells)
    results: list[tuple[Mapping[str, Any], dict[str, Any]]] = []
    trigger: dict[str, Any] | None = None
    with concurrent.futures.ThreadPoolExecutor(
        max_workers=settings.max_concurrency
    ) as pool:
        active: dict[concurrent.futures.Future[dict[str, Any]], Mapping[str, Any]] = {}
        for _ in range(min(settings.max_concurrency, len(cells))):
            cell = next(pending)
            active[pool.submit(_execute_safely, executor, cell, campaign, settings)] = cell

        while active:
            done, _ = concurrent.futures.wait(
                active, return_when=concurrent.futures.FIRST_COMPLETED
            )
            batch: list[tuple[Mapping[str, Any], dict[str, Any]]] = []
            for future in done:
                cell = active.pop(future)
                batch.append((cell, future.result()))
            batch.sort(key=lambda item: int(item[0]["sequence"]))
            results.extend(batch)
            aborts = [
                _bind_outcome(cell, outcome)
                for cell, outcome in batch
                if outcome.get("outcome") in ABORT_OUTCOMES
            ]
            if aborts and trigger is None:
                trigger = min(aborts, key=lambda item: int(item["sequence"]))
            if trigger is None:
                for _ in range(len(batch)):
                    try:
                        cell = next(pending)
                    except StopIteration:
                        break
                    active[pool.submit(_execute_safely, executor, cell, campaign, settings)] = cell
    results.sort(key=lambda item: int(item[0]["sequence"]))
    return results, trigger


def _bind_outcome(
    cell: Mapping[str, Any], outcome: Mapping[str, Any]
) -> dict[str, Any]:
    result = {
        key: outcome.get(key)
        for key in PERSISTED_OUTCOME_FIELDS
        if key in outcome
    }
    reset = outcome.get("provider_reset")
    if (
        outcome.get("outcome") == "provider-quota"
        and outcome.get("error_code") == "usage_limit_reached"
        and isinstance(reset, Mapping)
    ):
        sanitized = sanitize_provider_reset(
            reset.get("at"), reset.get("remaining_seconds")
        )
        if sanitized is not None:
            result["provider_reset"] = sanitized
    result.update(
        {
            "cohort": cell["cohort"],
            "family": cell["family"],
            "question_id": cell["question_id"],
            "schema_version": "semantic-okf-consult-campaign-outcome/1.0",
            "sequence": int(cell["sequence"]),
        }
    )
    return result


def checkpoint_trigger(outcome: Mapping[str, Any]) -> dict[str, Any]:
    """Return the redacted abort identity and optional sanitized provider reset."""

    result = {key: outcome.get(key) for key in CHECKPOINT_TRIGGER_FIELDS}
    reset = outcome.get("provider_reset")
    if (
        outcome.get("outcome") == "provider-quota"
        and outcome.get("error_code") == "usage_limit_reached"
        and isinstance(reset, Mapping)
    ):
        sanitized = sanitize_provider_reset(
            reset.get("at"), reset.get("remaining_seconds")
        )
        if sanitized is not None:
            result["provider_reset"] = sanitized
    return result


def _persist_outcome(
    campaign: Path, cell: Mapping[str, Any], outcome: Mapping[str, Any]
) -> dict[str, Any]:
    result = _bind_outcome(cell, outcome)
    path = _outcome_path(campaign, int(cell["sequence"]))
    _write_bytes_exclusive(path, canonical_json_bytes(result))
    return result


def _first_abort(outcomes: Sequence[Mapping[str, Any]]) -> dict[str, Any] | None:
    aborts = [outcome for outcome in outcomes if outcome.get("outcome") in ABORT_OUTCOMES]
    return min(aborts, key=lambda item: int(item["sequence"])) if aborts else None


def _persist_terminal_checkpoint(
    campaign: Path,
    status: str,
    digest: str,
    outcomes: Mapping[int, Mapping[str, Any]],
    *,
    trigger: Mapping[str, Any] | None = None,
    input_bindings_digest: str | None = None,
) -> dict[str, Any]:
    path = campaign / "checkpoints" / f"{status}.json"
    if path.is_file():
        return _validate_terminal_checkpoint(
            data.load_json(path),
            status=status,
            digest=digest,
            outcomes=outcomes,
            trigger=trigger,
            input_bindings_digest=input_bindings_digest,
        )
    if path.exists():
        raise CampaignRunError(f"terminal checkpoint path is not a file: {path}")
    counts = Counter(str(outcome.get("outcome", "unknown")) for outcome in outcomes.values())
    checkpoint: dict[str, Any] = {
        "completed_cell_count": len(outcomes),
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "schedule_sha256": digest,
        "schema_version": "semantic-okf-consult-campaign-checkpoint/1.0",
        "status": status,
        "terminal_outcomes": dict(sorted(counts.items())),
    }
    if input_bindings_digest is not None:
        checkpoint["input_bindings_sha256"] = input_bindings_digest
    if trigger is not None:
        checkpoint["trigger"] = checkpoint_trigger(trigger)
    _write_bytes_exclusive(path, canonical_json_bytes(checkpoint))
    return checkpoint


def _validate_terminal_checkpoint(
    checkpoint: Mapping[str, Any],
    *,
    status: str,
    digest: str,
    outcomes: Mapping[int, Mapping[str, Any]],
    trigger: Mapping[str, Any] | None,
    input_bindings_digest: str | None,
) -> dict[str, Any]:
    """Validate an existing terminal checkpoint against its derived state."""

    counts = Counter(str(outcome.get("outcome", "unknown")) for outcome in outcomes.values())
    expected: dict[str, Any] = {
        "completed_cell_count": len(outcomes),
        "schedule_sha256": digest,
        "schema_version": "semantic-okf-consult-campaign-checkpoint/1.0",
        "status": status,
        "terminal_outcomes": dict(sorted(counts.items())),
    }
    if input_bindings_digest is not None:
        expected["input_bindings_sha256"] = input_bindings_digest
    if trigger is not None:
        expected["trigger"] = checkpoint_trigger(trigger)
    expected_keys = set(expected) | {"recorded_at"}
    if set(checkpoint) != expected_keys or any(
        checkpoint.get(key) != value for key, value in expected.items()
    ):
        raise CampaignRunError(f"existing {status} checkpoint does not match campaign state")
    recorded_at = checkpoint.get("recorded_at")
    try:
        timestamp = datetime.fromisoformat(
            str(recorded_at).replace("Z", "+00:00")
        )
    except ValueError as exc:
        raise CampaignRunError(
            f"existing {status} checkpoint has an invalid recorded_at"
        ) from exc
    if (
        not isinstance(recorded_at, str)
        or timestamp.tzinfo is None
        or timestamp.utcoffset() is None
    ):
        raise CampaignRunError(
            f"existing {status} checkpoint has an invalid recorded_at"
        )
    return dict(checkpoint)


if __name__ == "__main__":
    raise SystemExit(main())
