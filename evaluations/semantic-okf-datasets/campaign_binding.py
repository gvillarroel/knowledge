#!/usr/bin/env python3
"""Freeze and verify the non-secret inputs consumed by consult campaigns."""

from __future__ import annotations

import contextlib
import hashlib
import json
import os
import re
import shutil
import stat
import tomllib
from pathlib import Path, PurePosixPath
from typing import Any, Iterator, Mapping


FROZEN_INPUTS_SCHEMA = "semantic-okf-consult-campaign-frozen-inputs/1.0"
HF_CLOSURE_SCHEMA = "semantic-okf-hf-runtime-closure/1.0"
HF_MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"
HF_REVISION = "1110a243fdf4706b3f48f1d95db1a4f5529b4d41"
HF_PROVIDER = "sentence-transformers"
HF_REPOSITORY_DIRECTORY = "models--sentence-transformers--all-MiniLM-L6-v2"
HF_EXPECTED_FILES = {
    "1_Pooling/config.json": (
        190,
        "4be450dde3b0273bb9787637cfbd28fe04a7ba6ab9d36ac48e92b11e350ffc23",
    ),
    "config_sentence_transformers.json": (
        116,
        "061ca9d39661d6c6d6de5ba27f79a1cd5770ea247f8d46412a68a498dc5ac9f3",
    ),
    "config.json": (
        612,
        "953f9c0d463486b10a6871cc2fd59f223b2c70184f49815e7efbcab5d8908b41",
    ),
    "data_config.json": (
        39265,
        "32edcb108fc2516b920734a862ae0692bcae1c5d45d5f8d972cb0d53434a4c54",
    ),
    "model.safetensors": (
        90868376,
        "53aa51172d142c89d9012cce15ae4d6cc0ca6895895114379cacb4fab128d9db",
    ),
    "modules.json": (
        349,
        "84e40c8e006c9b1d6c122e02cba9b02458120b5fb0c87b746c41e0207cf642cf",
    ),
    "sentence_bert_config.json": (
        53,
        "fc1993fde0a95c24ec6c022539d41cf6e2f7c9721e5415d6fb6897472a9cd4b7",
    ),
    "special_tokens_map.json": (
        112,
        "303df45a03609e4ead04bc3dc1536d0ab19b5358db685b6f3da123d05ec200e3",
    ),
    "tokenizer.json": (
        466247,
        "be50c3628f2bf5bb5e3a7f17b1f74611b2561a3a27eeab05e5aa30f411572037",
    ),
    "tokenizer_config.json": (
        350,
        "acb92769e8195aabd29b7b2137a9e6d6e25c476a4f15aa4355c233426c61576b",
    ),
    "vocab.txt": (
        231508,
        "07eced375cec144d27c900241f3e339478dec958f92fddbc551f295c992038a3",
    ),
}
PI_PACKAGE = "@mariozechner/pi-coding-agent"
PI_VERSION = "0.73.1"
PI_NPM_INTEGRITY = (
    "sha512-gXQh3SaZmWTfVMc4Ao5+LGbVeKvzyO7tolok0nLsZgq9nGjZx/"
    "EEU3NM8C+qUnB4Nvs2rswG5qOVgLzQkq0fHQ=="
)
NODE_VERSION = "v22.23.1"
HARBOR_VERSION = "0.18.0"
RUNTIME_IMAGE_REPOSITORY = "semantic-okf-harbor-runtime"
RUNTIME_IMAGE_TAG_PREFIX = f"{RUNTIME_IMAGE_REPOSITORY}:sha256-"
HARBOR_PI_SOURCE_SHA256 = (
    "ae621461cf4e76837c21a70b1b28103a0b37acaf0d554bec4c3f627512e89168"
)
PIPELINE_SOURCE_PATHS = (
    "evaluations/semantic-okf-datasets/campaign_binding.py",
    "evaluations/semantic-okf-datasets/dataset_tool.py",
    "evaluations/semantic-okf-datasets/freeze_consult_campaign.py",
    "evaluations/semantic-okf-datasets/generate_harbor_tasks.py",
    "evaluations/semantic-okf-datasets/run_consult_campaign.py",
    "evaluations/semantic-okf-datasets/run_harbor.py",
    "evaluations/semantic-okf-datasets/summarize_consult_campaign.py",
)
SHA256 = re.compile(r"[0-9a-f]{64}")
REVISION = re.compile(r"[0-9a-f]{40}")


class BindingError(ValueError):
    """Raised when a frozen input is unsafe, incomplete, or drifted."""


def runtime_image_reference(image_id: str) -> str:
    """Return the content-addressed local tag used by frozen Dockerfiles."""

    if not image_id.startswith("sha256:") or not SHA256.fullmatch(image_id[7:]):
        raise BindingError("runtime image ID is not a canonical SHA-256 identity")
    return f"{RUNTIME_IMAGE_TAG_PREFIX}{image_id[7:]}"


def runtime_image_id_from_reference(reference: str) -> str:
    """Recover and validate the image ID encoded in a frozen local tag."""

    if not reference.startswith(RUNTIME_IMAGE_TAG_PREFIX):
        raise BindingError("frozen runtime reference is not content-addressed")
    digest = reference[len(RUNTIME_IMAGE_TAG_PREFIX) :]
    if not SHA256.fullmatch(digest):
        raise BindingError("frozen runtime reference has an invalid SHA-256 suffix")
    return f"sha256:{digest}"


def canonical_json_bytes(value: Mapping[str, Any]) -> bytes:
    """Return canonical human-readable JSON bytes."""

    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def sha256_file(path: Path) -> str:
    """Return the SHA-256 digest of one regular file."""

    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _safe_relative(value: str, label: str) -> PurePosixPath:
    pure = PurePosixPath(value)
    if (
        not value
        or pure.is_absolute()
        or ".." in pure.parts
        or "\\" in value
        or pure.as_posix() != value
    ):
        raise BindingError(f"{label} is not a safe canonical relative path: {value!r}")
    return pure


def _is_link_like(path: Path) -> bool:
    """Return whether a path is a symbolic link or Windows junction."""

    junction = getattr(path, "is_junction", None)
    return path.is_symlink() or (junction is not None and junction())


def _regular_inventory(
    root: Path,
    *,
    reject_links: bool,
    reject_hardlinks: bool,
) -> tuple[list[dict[str, Any]], list[str]]:
    """Inventory a closed regular-file tree in canonical byte order."""

    if not root.is_dir():
        raise BindingError(f"bound tree is absent: {root}")
    rows: list[tuple[bytes, dict[str, Any]]] = []
    directories: list[tuple[bytes, str]] = []
    casefolded: dict[str, str] = {}
    for path in root.rglob("*"):
        relative = path.relative_to(root).as_posix()
        _safe_relative(relative, "bound tree entry")
        prior = casefolded.setdefault(relative.casefold(), relative)
        if prior != relative:
            raise BindingError(
                f"bound tree has a case-fold collision: {prior!r}, {relative!r}"
            )
        if _is_link_like(path):
            if reject_links:
                raise BindingError(f"bound tree contains a link-like entry: {relative}")
            continue
        if path.is_dir():
            directories.append((relative.encode("utf-8"), relative))
            continue
        if not path.is_file():
            raise BindingError(f"bound tree contains a non-regular entry: {relative}")
        metadata = path.stat()
        if reject_hardlinks and metadata.st_nlink != 1:
            raise BindingError(f"bound tree contains a shared hardlink: {relative}")
        rows.append(
            (
                relative.encode("utf-8"),
                {
                    "path": relative,
                    "sha256": sha256_file(path),
                    "size": metadata.st_size,
                },
            )
        )
    return (
        [row for _key, row in sorted(rows, key=lambda item: item[0])],
        [relative for _key, relative in sorted(directories, key=lambda item: item[0])],
    )


def tree_identity(root: Path, *, reject_links: bool = True) -> dict[str, Any]:
    """Return a compact content identity for a closed regular-file tree."""

    files, _directories = _regular_inventory(
        root, reject_links=reject_links, reject_hardlinks=True
    )
    digest = hashlib.sha256()
    total = 0
    for row in files:
        relative = str(row["path"])
        path = root / Path(*PurePosixPath(relative).parts)
        digest.update(relative.encode("utf-8") + b"\0")
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
        digest.update(b"\0")
        total += int(row["size"])
    return {
        "file_count": len(files),
        "total_bytes": total,
        "tree_sha256": digest.hexdigest(),
    }


def model_identity_from_bundles(campaign: Path) -> dict[str, Any]:
    """Require Embeddings and Ensemble to declare one identical model identity."""

    observed: list[dict[str, Any]] = []
    for family in ("embeddings", "ensemble"):
        path = campaign / "bundles" / family / "retrieval" / "index.json"
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise BindingError(f"cannot load {family} retrieval index: {path}") from exc
        embedding = value.get("embedding") if isinstance(value, Mapping) else None
        if not isinstance(embedding, Mapping):
            raise BindingError(f"{family} retrieval index has no embedding identity")
        observed.append(
            {
                "dimension": embedding.get("dimension"),
                "model_id": embedding.get("model_id"),
                "normalize": embedding.get("normalize"),
                "provider": embedding.get("provider"),
                "revision": embedding.get("revision"),
            }
        )
    expected = {
        "dimension": 384,
        "model_id": HF_MODEL_ID,
        "normalize": True,
        "provider": HF_PROVIDER,
        "revision": HF_REVISION,
    }
    if observed != [expected, expected]:
        raise BindingError("embedding-backed bundles do not share the pinned model identity")
    return expected


def _snapshot_path(hub: Path) -> Path:
    return hub / HF_REPOSITORY_DIRECTORY / "snapshots" / HF_REVISION


def _require_plain_directory(path: Path, label: str) -> None:
    """Require one directory path component without following a link."""

    if _is_link_like(path):
        raise BindingError(f"{label} is not a plain directory: {path}")
    try:
        metadata = path.lstat()
    except OSError as exc:
        raise BindingError(f"{label} is absent: {path}") from exc
    if not stat.S_ISDIR(metadata.st_mode):
        raise BindingError(f"{label} is not a plain directory: {path}")


def _require_exact_children(path: Path, expected: set[str], label: str) -> None:
    """Require the complete immediate inventory of one closed directory."""

    try:
        actual = {child.name for child in path.iterdir()}
    except OSError as exc:
        raise BindingError(f"cannot inspect {label}: {path}") from exc
    if actual != expected:
        raise BindingError(f"{label} contains unexpected or missing entries")


def _require_closed_hf_hub_layout(hub: Path) -> Path:
    """Require the exact directory envelope of a materialized HF closure."""

    repository = hub / HF_REPOSITORY_DIRECTORY
    snapshots = repository / "snapshots"
    snapshot = snapshots / HF_REVISION
    for path, label in (
        (hub, "HF closure hub"),
        (repository, "HF closure repository"),
        (snapshots, "HF closure snapshots directory"),
        (snapshot, "HF closure revision"),
    ):
        _require_plain_directory(path, label)
    _require_exact_children(hub, {HF_REPOSITORY_DIRECTORY}, "HF closure hub")
    _require_exact_children(repository, {"snapshots"}, "HF closure repository")
    _require_exact_children(snapshots, {HF_REVISION}, "HF closure snapshots directory")
    return snapshot


def materialize_hf_runtime_closure(source_hub: Path, destination_hub: Path) -> dict[str, Any]:
    """Copy the exact pinned raw HF cache snapshot as independent files."""

    source_repository = source_hub / HF_REPOSITORY_DIRECTORY
    source_snapshots = source_repository / "snapshots"
    source_blobs_path = source_repository / "blobs"
    source_snapshot = _snapshot_path(source_hub)
    destination_snapshot = _snapshot_path(destination_hub)
    if destination_hub.exists() or destination_hub.is_symlink():
        raise BindingError(f"HF closure destination already exists: {destination_hub}")
    for path, label in (
        (source_hub, "HF source hub"),
        (source_repository, "HF source repository"),
        (source_snapshots, "HF source snapshots directory"),
        (source_snapshot, "pinned HF source snapshot"),
        (source_blobs_path, "pinned HF source blob store"),
    ):
        _require_plain_directory(path, label)
    source_blobs = source_blobs_path.resolve(strict=True)

    source_rows: list[tuple[bytes, str, Path]] = []
    for path in source_snapshot.rglob("*"):
        relative = path.relative_to(source_snapshot).as_posix()
        _safe_relative(relative, "HF snapshot entry")
        if path.is_dir() and not _is_link_like(path):
            continue
        if _is_link_like(path):
            resolved = path.resolve(strict=True)
            if resolved.parent != source_blobs:
                raise BindingError(f"HF snapshot link escapes its blob store: {relative}")
        elif path.is_file():
            resolved = path.resolve(strict=True)
            if source_snapshot.resolve() not in resolved.parents:
                raise BindingError(f"HF snapshot file escapes its snapshot: {relative}")
        else:
            raise BindingError(f"HF snapshot contains a non-regular entry: {relative}")
        if not resolved.is_file():
            raise BindingError(f"HF snapshot target is not a regular file: {relative}")
        source_rows.append((relative.encode("utf-8"), relative, resolved))

    destination_snapshot.mkdir(parents=True)
    for _key, relative, source in sorted(source_rows, key=lambda row: row[0]):
        target = destination_snapshot / Path(*PurePosixPath(relative).parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target, follow_symlinks=True)
        if target.is_symlink() or not target.is_file():
            raise BindingError(f"HF closure did not materialize a regular file: {relative}")

    return describe_hf_runtime_closure(destination_hub)


def _sha256_descriptor(descriptor: int) -> str:
    """Hash one open file descriptor and restore its offset."""

    digest = hashlib.sha256()
    os.lseek(descriptor, 0, os.SEEK_SET)
    with os.fdopen(os.dup(descriptor), "rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    os.lseek(descriptor, 0, os.SEEK_SET)
    return digest.hexdigest()


def _open_directory_descriptor(
    name: str | os.PathLike[str], *, parent: int | None = None
) -> int:
    """Open and pin one directory without following its final component."""

    flags = (
        os.O_RDONLY
        | os.O_DIRECTORY
        | os.O_NOFOLLOW
        | getattr(os, "O_CLOEXEC", 0)
    )
    try:
        if parent is None:
            return os.open(name, flags)
        return os.open(name, flags, dir_fd=parent)
    except OSError as exc:
        raise BindingError(
            f"cannot pin plain HF source directory component: {name}"
        ) from exc


@contextlib.contextmanager
def _open_attested_hf_source_files(
    source_hub: Path, expected: Mapping[str, Any]
) -> Iterator[dict[str, int]]:
    """Pin the complete source path and every qualified model file by fd."""

    if (
        os.name != "posix"
        or not hasattr(os, "O_DIRECTORY")
        or not hasattr(os, "O_NOFOLLOW")
        or os.open not in os.supports_dir_fd
    ):
        raise BindingError(
            "closed HF campaign migration requires POSIX no-follow directory descriptors"
        )
    if not source_hub.is_absolute():
        raise BindingError("closed HF campaign source must be an absolute path")

    expected_rows = expected.get("files")
    if not isinstance(expected_rows, list):
        raise BindingError("source HF closure manifest has no file inventory")
    expected_files: dict[str, Mapping[str, Any]] = {}
    children: dict[str, set[str]] = {"": set()}
    for row in expected_rows:
        if not isinstance(row, Mapping):
            raise BindingError("source HF closure manifest has an invalid file inventory")
        relative = str(row.get("path", ""))
        pure = _safe_relative(relative, "source HF closure manifest file")
        if relative in expected_files:
            raise BindingError("source HF closure manifest repeats a file")
        expected_files[relative] = row
        parent = PurePosixPath(".")
        for part in pure.parts[:-1]:
            parent_key = "" if parent.as_posix() == "." else parent.as_posix()
            children.setdefault(parent_key, set()).add(part)
            parent = parent / part
            children.setdefault(parent.as_posix(), set())
        parent_key = "" if parent.as_posix() == "." else parent.as_posix()
        children.setdefault(parent_key, set()).add(pure.name)

    with contextlib.ExitStack() as stack:
        parts = source_hub.parts
        root = Path(source_hub.anchor)
        current = _open_directory_descriptor(root)
        stack.callback(os.close, current)
        for part in parts[1:]:
            current = _open_directory_descriptor(part, parent=current)
            stack.callback(os.close, current)
        hub_descriptor = current

        if set(os.listdir(hub_descriptor)) != {HF_REPOSITORY_DIRECTORY}:
            raise BindingError("pinned HF closure hub inventory changed")
        repository = _open_directory_descriptor(
            HF_REPOSITORY_DIRECTORY, parent=hub_descriptor
        )
        stack.callback(os.close, repository)
        if set(os.listdir(repository)) != {"snapshots"}:
            raise BindingError("pinned HF closure repository inventory changed")
        snapshots = _open_directory_descriptor("snapshots", parent=repository)
        stack.callback(os.close, snapshots)
        if set(os.listdir(snapshots)) != {HF_REVISION}:
            raise BindingError("pinned HF closure snapshots inventory changed")
        revision = _open_directory_descriptor(HF_REVISION, parent=snapshots)
        stack.callback(os.close, revision)

        directory_descriptors: dict[str, int] = {"": revision}
        for relative in sorted(
            (value for value in children if value),
            key=lambda value: (len(PurePosixPath(value).parts), value.encode("utf-8")),
        ):
            pure = PurePosixPath(relative)
            parent = pure.parent.as_posix()
            if parent == ".":
                parent = ""
            descriptor = _open_directory_descriptor(
                pure.name, parent=directory_descriptors[parent]
            )
            stack.callback(os.close, descriptor)
            directory_descriptors[relative] = descriptor
        for relative, descriptor in directory_descriptors.items():
            if set(os.listdir(descriptor)) != children[relative]:
                label = relative or "."
                raise BindingError(
                    f"pinned HF closure directory inventory changed: {label}"
                )

        file_descriptors: dict[str, int] = {}
        file_flags = (
            os.O_RDONLY
            | os.O_NOFOLLOW
            | getattr(os, "O_NONBLOCK", 0)
            | getattr(os, "O_CLOEXEC", 0)
            | getattr(os, "O_BINARY", 0)
        )
        for relative, row in sorted(
            expected_files.items(), key=lambda item: item[0].encode("utf-8")
        ):
            pure = PurePosixPath(relative)
            parent = pure.parent.as_posix()
            if parent == ".":
                parent = ""
            try:
                descriptor = os.open(
                    pure.name, file_flags, dir_fd=directory_descriptors[parent]
                )
            except OSError as exc:
                raise BindingError(
                    f"cannot pin materialized HF source file: {relative}"
                ) from exc
            stack.callback(os.close, descriptor)
            metadata = os.fstat(descriptor)
            if (
                not stat.S_ISREG(metadata.st_mode)
                or metadata.st_nlink != 1
                or metadata.st_size != row.get("size")
                or _sha256_descriptor(descriptor) != row.get("sha256")
            ):
                raise BindingError(
                    f"pinned HF source file differs from its manifest: {relative}"
                )
            file_descriptors[relative] = descriptor
        yield file_descriptors


def rematerialize_hf_runtime_closure(
    source_hub: Path,
    destination_hub: Path,
    expected: Mapping[str, Any],
) -> dict[str, Any]:
    """Copy an attested campaign-local HF closure without following links."""

    if destination_hub.exists() or destination_hub.is_symlink():
        raise BindingError(f"HF closure destination already exists: {destination_hub}")
    before = describe_hf_runtime_closure(source_hub)
    if before != dict(expected):
        raise BindingError("source HF closure differs from its frozen manifest")

    destination_snapshot = _snapshot_path(destination_hub)
    destination_snapshot.mkdir(parents=True)
    with _open_attested_hf_source_files(source_hub, before) as source_files:
        for relative, descriptor in source_files.items():
            pure = _safe_relative(relative, "materialized HF source file")
            target = destination_snapshot / Path(*pure.parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            os.lseek(descriptor, 0, os.SEEK_SET)
            with os.fdopen(os.dup(descriptor), "rb") as source_stream:
                with target.open("xb") as target_stream:
                    shutil.copyfileobj(source_stream, target_stream, 1024 * 1024)
            opened = os.fstat(descriptor)
            if not stat.S_ISREG(opened.st_mode) or opened.st_nlink != 1:
                raise BindingError(
                    f"pinned HF source file changed while copying: {relative}"
                )

    try:
        after = describe_hf_runtime_closure(source_hub)
    except BindingError as exc:
        raise BindingError("source HF closure changed while it was copied") from exc
    destination = describe_hf_runtime_closure(destination_hub)
    if after != before:
        raise BindingError("source HF closure changed while it was copied")
    if destination != before:
        raise BindingError("rematerialized HF closure differs from its source")
    return destination


def describe_hf_runtime_closure(hub: Path) -> dict[str, Any]:
    """Describe and validate a materialized, closed HF runtime snapshot."""

    snapshot = _require_closed_hf_hub_layout(hub)
    files, directories = _regular_inventory(
        snapshot, reject_links=True, reject_hardlinks=True
    )
    expected_directories = sorted(
        {
            PurePosixPath(str(row["path"])).parent.as_posix()
            for row in files
            if PurePosixPath(str(row["path"])).parent.as_posix() != "."
        },
        key=lambda value: value.encode("utf-8"),
    )
    if directories != expected_directories:
        raise BindingError("HF closure contains unexpected or missing directories")
    expected_files = [
        {"path": path, "size": size, "sha256": digest}
        for path, (size, digest) in sorted(
            HF_EXPECTED_FILES.items(), key=lambda item: item[0].encode("utf-8")
        )
    ]
    if files != expected_files:
        raise BindingError("HF closure does not match the qualified model file inventory")
    identity = tree_identity(snapshot)
    return {
        "schema_version": HF_CLOSURE_SCHEMA,
        "materialization": "dereferenced-independent-regular-files",
        "provider": HF_PROVIDER,
        "model_id": HF_MODEL_ID,
        "revision": HF_REVISION,
        "hub_repository_path": HF_REPOSITORY_DIRECTORY,
        "snapshot_path": (
            f"{HF_REPOSITORY_DIRECTORY}/snapshots/{HF_REVISION}"
        ),
        "directories": directories,
        "files": files,
        **identity,
    }


def verify_hf_runtime_closure(hub: Path, expected: Mapping[str, Any]) -> dict[str, Any]:
    """Require an HF closure to match its closed canonical descriptor exactly."""

    actual = describe_hf_runtime_closure(hub)
    if actual != expected:
        raise BindingError("campaign HF runtime closure differs from its binding")
    return actual


def patch_harbor_pi_for_pinned_runtime(vendor_root: Path) -> dict[str, str]:
    """Patch the pinned Harbor Pi adapter to use the image-provided Node and Pi."""

    path = vendor_root / "harbor" / "agents" / "installed" / "pi.py"
    if sha256_file(path) != HARBOR_PI_SOURCE_SHA256:
        raise BindingError("Harbor Pi adapter source differs from the qualified 0.18.0 file")
    source = path.read_text(encoding="utf-8")
    source = source.replace(
        'return ". ~/.nvm/nvm.sh; pi --version"',
        'return "pi --version"',
        1,
    )
    old_install = '''        await self.exec_as_root(
            environment,
            command="apt-get update && apt-get install -y curl",
            env={"DEBIAN_FRONTEND": "noninteractive"},
        )
        version_spec = f"@{self._version}" if self._version else "@latest"
        await self.exec_as_agent(
            environment,
            command=(
                "set -euo pipefail; "
                f"{nvm_node_install_snippet()} && "
                f"npm install -g @mariozechner/pi-coding-agent{version_spec} && "
                "pi --version"
            ),
        )'''
    new_install = f'''        if self._version != "{PI_VERSION}":
            raise ValueError("the frozen Semantic OKF runtime requires Pi {PI_VERSION}")
        await self.exec_as_agent(
            environment,
            command=(
                "set -euo pipefail; "
                'test "$(node --version)" = "{NODE_VERSION}"; '
                'test "$(pi --version | tail -n 1)" = "{PI_VERSION}"; '
                "node --version; pi --version"
            ),
        )'''
    if old_install not in source:
        raise BindingError("qualified Harbor Pi install block was not found exactly once")
    source = source.replace(old_install, new_install, 1)
    run_prefix = 'f". ~/.nvm/nvm.sh; "'
    if source.count(run_prefix) != 1:
        raise BindingError("qualified Harbor Pi run prefix was not found exactly once")
    source = source.replace(run_prefix, 'f""', 1)
    path.write_text(source, encoding="utf-8", newline="\n")
    return {
        "source_sha256": HARBOR_PI_SOURCE_SHA256,
        "patched_sha256": sha256_file(path),
    }


def task_runtime_references(repo: Path, dataset_id: str) -> dict[str, int | str]:
    """Validate every staged task and verifier use one content-addressed tag."""

    root = repo / "evaluations" / "semantic-okf-datasets" / "generated" / "tasks"
    root = root / dataset_id / "consult-only"
    manifests = sorted(root.glob("*/manifest.json"))
    task_files = sorted(root.glob("*/*/q*/task.toml"))
    verifier_files = sorted(root.glob("*/*/q*/tests/Dockerfile"))
    if len(manifests) != 8 or len(task_files) != 320 or len(verifier_files) != 320:
        raise BindingError("frozen task matrix is incomplete")
    images: set[str] = set()
    for path in manifests:
        value = json.loads(path.read_text(encoding="utf-8"))
        image = value.get("runtime_image") if isinstance(value, Mapping) else None
        if not isinstance(image, str):
            raise BindingError(f"frozen task manifest has no runtime image: {path}")
        images.add(image)
    for path in task_files:
        value = tomllib.loads(path.read_text(encoding="utf-8"))
        image = value.get("environment", {}).get("docker_image")
        if not isinstance(image, str):
            raise BindingError(f"frozen task has no runtime image: {path}")
        images.add(image)
    for path in verifier_files:
        lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines()]
        from_lines = [line for line in lines if line.startswith("FROM ")]
        if len(from_lines) != 1:
            raise BindingError(f"frozen verifier Dockerfile has no single FROM: {path}")
        images.add(from_lines[0][5:].strip())
    if len(images) != 1:
        raise BindingError("frozen tasks do not share one runtime image reference")
    image = next(iter(images))
    image_id = runtime_image_id_from_reference(image)
    return {
        "manifest_count": len(manifests),
        "task_count": len(task_files),
        "verifier_dockerfile_count": len(verifier_files),
        "runtime_image_reference": image,
        "runtime_image_id": image_id,
    }


def load_frozen_inputs(campaign: Path) -> dict[str, Any]:
    """Load and cryptographically verify a campaign frozen-input manifest."""

    path = campaign / "frozen-inputs.json"
    sidecar = campaign / "frozen-inputs.sha256"
    if not path.is_file() or not sidecar.is_file():
        raise BindingError("campaign has no complete frozen-input manifest")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        recorded = sidecar.read_text(encoding="ascii").strip().split()[0]
    except (OSError, UnicodeError, json.JSONDecodeError, IndexError) as exc:
        raise BindingError("campaign frozen-input manifest is unreadable") from exc
    if not isinstance(value, dict) or canonical_json_bytes(value) != path.read_bytes():
        raise BindingError("campaign frozen-input manifest is not canonical JSON")
    actual = sha256_file(path)
    if recorded != actual:
        raise BindingError("campaign frozen-input manifest SHA-256 does not verify")
    return value


def verify_frozen_inputs(
    campaign: Path, *, verify_model: bool = True
) -> dict[str, Any]:
    """Rehash every campaign-local execution input against its trusted manifest."""

    manifest = load_frozen_inputs(campaign)
    expected_keys = {
        "schema_version",
        "source_campaign",
        "dataset_id",
        "mode",
        "frozen_repo",
        "offline_model",
        "task_runtime",
        "harbor_adapter",
        "pi_distribution",
    }
    if set(manifest) != expected_keys or manifest.get("schema_version") != FROZEN_INPUTS_SCHEMA:
        raise BindingError("campaign frozen-input manifest has an unsupported shape")
    if manifest.get("dataset_id") != "graphrag-papers-40" or manifest.get("mode") != "consult-only":
        raise BindingError("campaign frozen-input identity drift")
    repo = campaign / "frozen" / "repo"
    hub = campaign / "frozen" / "model-cache" / "hub"
    expected_repo = manifest.get("frozen_repo")
    if not isinstance(expected_repo, Mapping) or expected_repo.get("path") != "frozen/repo":
        raise BindingError("campaign frozen repository binding is invalid")
    actual_repo = {"path": "frozen/repo", **tree_identity(repo)}
    if actual_repo != expected_repo:
        raise BindingError("campaign frozen repository tree drift")
    expected_model = manifest.get("offline_model")
    if not isinstance(expected_model, Mapping):
        raise BindingError("campaign frozen model binding is invalid")
    if verify_model:
        verify_hf_runtime_closure(hub, expected_model)
    task_runtime = task_runtime_references(repo, "graphrag-papers-40")
    if task_runtime != manifest.get("task_runtime"):
        raise BindingError("campaign frozen task runtime references drift")
    pi_distribution = manifest.get("pi_distribution")
    if pi_distribution != {
        "name": PI_PACKAGE,
        "version": PI_VERSION,
        "npm_integrity": PI_NPM_INTEGRITY,
        "node_version": NODE_VERSION,
    }:
        raise BindingError("campaign frozen Pi distribution identity drift")
    adapter = manifest.get("harbor_adapter")
    pi_path = repo / "vendor" / "harbor" / "agents" / "installed" / "pi.py"
    if (
        not isinstance(adapter, Mapping)
        or adapter.get("harbor_version") != HARBOR_VERSION
        or adapter.get("source_sha256") != HARBOR_PI_SOURCE_SHA256
        or adapter.get("patched_sha256") != sha256_file(pi_path)
    ):
        raise BindingError("campaign frozen Harbor Pi adapter drift")
    return manifest


def write_canonical_exclusive(path: Path, value: Mapping[str, Any]) -> str:
    """Write one canonical JSON document and sidecar without overwriting."""

    payload = canonical_json_bytes(value)
    digest = hashlib.sha256(payload).hexdigest()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(payload)
    sidecar = path.with_suffix(".sha256")
    with sidecar.open("xb") as stream:
        stream.write(f"{digest}  {path.name}\n".encode("ascii"))
    return digest


def make_executable(path: Path) -> None:
    """Ensure a generated launcher is executable for its owner."""

    path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
