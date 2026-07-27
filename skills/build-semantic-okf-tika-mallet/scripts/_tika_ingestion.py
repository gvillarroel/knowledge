#!/usr/bin/env python3
"""Extract local documents with Tika and bind them to Semantic OKF inputs."""

from __future__ import annotations

import glob
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import tempfile
import unicodedata
from dataclasses import dataclass
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any, Iterable, Mapping, Sequence
from urllib.parse import urlsplit

import yaml

from _semantic_okf import canonical_json, sha256_json, validate_manifest
from _safe_paths import (
    UnsafePathError,
    assert_no_links,
    file_identity,
    lexical_absolute,
    require_identity,
    require_real_directory,
    require_regular_file,
    scan_regular_tree,
)


SCHEMA_VERSION = "1.0"
TIKA_VERSION = "4.0.0-beta-1"
TIKA_ALGORITHM = "apache-tika-4.0.0-beta-1-default-markdown-verified-v1"
TIKA_VERBATIM_ALGORITHM = (
    "apache-tika-4.0.0-beta-1-hybrid-markdown-or-utf8-verbatim-verified-v1"
)
DEFAULT_BODY_MODE = "tika-markdown"
VERBATIM_BODY_MODE = "utf8-verbatim-tika-verified"
DEFAULT_HANDLER = "markdown-default-verified-v1"
VERBATIM_HANDLER = "utf8-verbatim-tika-metadata-verified-v1"
VERBATIM_SUFFIXES = frozenset({".csv", ".json", ".jsonl", ".md", ".markdown", ".txt"})
TIKA_DIRECTORY = "tika"
TIKA_INDEX = "tika/index.json"
TIKA_DOCUMENTS = "tika/documents.jsonl"
PLAN_KEYS = frozenset({"schema_version", "bundle", "sources", "tika"})
BUNDLE_KEYS = frozenset(
    {
        "title",
        "description",
        "base_iri",
        "ontology_iri",
        "version_iri",
        "prefix",
        "owl_profile",
    }
)
SOURCE_KEYS = frozenset({"id", "path", "concept_type"})
SOURCE_OPTIONAL_KEYS = frozenset({"body_mode"})
TIKA_KEYS = frozenset(
    {"version", "verify_default_markdown", "timeout_seconds", "max_input_bytes"}
)
SOURCE_ID_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$")
WINDOWS_RESERVED = {
    "con",
    "prn",
    "aux",
    "nul",
    *(f"com{index}" for index in range(1, 10)),
    *(f"lpt{index}" for index in range(1, 10)),
}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class TikaIngestionError(RuntimeError):
    """Report a closed-plan, runtime, extraction, or receipt failure."""


def _body_mode(source: Mapping[str, Any]) -> str:
    value = source.get("body_mode", DEFAULT_BODY_MODE)
    if value not in {DEFAULT_BODY_MODE, VERBATIM_BODY_MODE}:
        raise TikaIngestionError(f"unsupported source body_mode: {value!r}")
    return str(value)


def _handler(source: Mapping[str, Any]) -> str:
    return (
        VERBATIM_HANDLER
        if _body_mode(source) == VERBATIM_BODY_MODE
        else DEFAULT_HANDLER
    )


def _plan_algorithm(plan: Mapping[str, Any]) -> str:
    return (
        TIKA_VERBATIM_ALGORITHM
        if any(
            _body_mode(source) == VERBATIM_BODY_MODE
            for source in plan["sources"]
        )
        else TIKA_ALGORITHM
    )


def _handler_pattern(plan: Mapping[str, Any]) -> str:
    handlers = sorted({_handler(source) for source in plan["sources"]})
    if len(handlers) == 1:
        return f"^{re.escape(handlers[0])}$"
    return "^(?:" + "|".join(re.escape(value) for value in handlers) + ")$"


@dataclass(frozen=True)
class TikaRuntime:
    """Describe the exact Java and Tika runtime used for extraction."""

    java: Path
    java_version: str
    tika_home: Path
    tika_jar: Path
    tika_version: str
    jar_inventory: tuple[dict[str, str], ...]
    jar_tree_sha256: str
    java_identity: tuple[int, int] | None = None
    home_identity: tuple[int, int] | None = None


@dataclass(frozen=True)
class IngestionPlan:
    """Hold a validated, closed Tika ingestion plan and its origin."""

    raw: dict[str, Any]
    root: Path
    sha256: str


def sha256_bytes(value: bytes) -> str:
    """Return a lowercase SHA-256 digest for *value*."""

    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    """Hash one regular file without following a symbolic link."""

    try:
        path = require_regular_file(path, label="file to hash")
    except UnsafePathError as exc:
        raise TikaIngestionError(str(exc)) from exc
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _exact_keys(value: Mapping[str, Any], expected: Iterable[str], label: str) -> None:
    actual = set(value)
    required = set(expected)
    if actual != required:
        missing = sorted(required - actual)
        extra = sorted(actual - required)
        details: list[str] = []
        if missing:
            details.append(f"missing {', '.join(missing)}")
        if extra:
            details.append(f"unsupported {', '.join(extra)}")
        raise TikaIngestionError(f"{label} has invalid fields: {'; '.join(details)}")


def _plain_int(value: Any, label: str, minimum: int, maximum: int) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or not minimum <= value <= maximum:
        raise TikaIngestionError(
            f"{label} must be an integer between {minimum} and {maximum}"
        )
    return value


def _safe_plan_path(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TikaIngestionError(f"{label} must be a non-empty string")
    if (
        "\\" in value
        or "://" in value
        or value.startswith(("/", "//"))
        or Path(value).is_absolute()
        or PureWindowsPath(value).drive
        or ".." in PurePosixPath(value).parts
    ):
        raise TikaIngestionError(f"{label} must be a portable plan-relative path")
    return value


def _parse_plan(value: Any, root: Path) -> IngestionPlan:
    if not isinstance(value, dict):
        raise TikaIngestionError("ingestion plan root must be an object")
    _exact_keys(value, PLAN_KEYS, "ingestion plan")
    if value["schema_version"] != SCHEMA_VERSION:
        raise TikaIngestionError(f"schema_version must be {SCHEMA_VERSION!r}")

    bundle = value["bundle"]
    if not isinstance(bundle, dict):
        raise TikaIngestionError("plan.bundle must be an object")
    _exact_keys(bundle, BUNDLE_KEYS, "plan.bundle")
    for field in BUNDLE_KEYS:
        if not isinstance(bundle[field], str) or not bundle[field].strip():
            raise TikaIngestionError(f"plan.bundle.{field} must be non-empty")

    sources = value["sources"]
    if not isinstance(sources, list) or not sources:
        raise TikaIngestionError("plan.sources must be a non-empty list")
    source_ids: set[str] = set()
    for index, source in enumerate(sources):
        if not isinstance(source, dict):
            raise TikaIngestionError(f"plan.sources[{index}] must be an object")
        if not SOURCE_KEYS <= set(source) <= SOURCE_KEYS | SOURCE_OPTIONAL_KEYS:
            raise TikaIngestionError(
                f"plan.sources[{index}] has invalid fields"
            )
        source_id = source["id"]
        if not isinstance(source_id, str) or not SOURCE_ID_RE.fullmatch(source_id):
            raise TikaIngestionError(f"plan.sources[{index}].id is invalid")
        if source_id in WINDOWS_RESERVED:
            raise TikaIngestionError(f"source id is reserved on Windows: {source_id}")
        if source_id in source_ids:
            raise TikaIngestionError(f"duplicate source id: {source_id}")
        source_ids.add(source_id)
        _safe_plan_path(source["path"], f"plan.sources[{index}].path")
        if not isinstance(source["concept_type"], str) or not source[
            "concept_type"
        ].strip():
            raise TikaIngestionError(
                f"plan.sources[{index}].concept_type must be non-empty"
            )
        body_mode = _body_mode(source)
        if (
            body_mode == VERBATIM_BODY_MODE
            and PurePosixPath(source["path"]).suffix.casefold()
            not in VERBATIM_SUFFIXES
        ):
            raise TikaIngestionError(
                f"plan.sources[{index}].body_mode requires a supported textual suffix"
            )

    tika = value["tika"]
    if not isinstance(tika, dict):
        raise TikaIngestionError("plan.tika must be an object")
    _exact_keys(tika, TIKA_KEYS, "plan.tika")
    if tika["version"] != TIKA_VERSION:
        raise TikaIngestionError(f"plan.tika.version must be {TIKA_VERSION!r}")
    if tika["verify_default_markdown"] is not True:
        raise TikaIngestionError("plan.tika.verify_default_markdown must be true")
    _plain_int(tika["timeout_seconds"], "timeout_seconds", 1, 3600)
    _plain_int(tika["max_input_bytes"], "max_input_bytes", 1, 2**63 - 1)

    normalized = json.loads(canonical_json(value))
    manifest_errors = validate_manifest(generate_semantic_manifest(normalized))
    if manifest_errors:
        raise TikaIngestionError(
            "plan cannot generate a valid Semantic OKF manifest: "
            + "; ".join(manifest_errors)
        )
    try:
        checked_root = require_real_directory(root, label="ingestion plan directory")
    except UnsafePathError as exc:
        raise TikaIngestionError(str(exc)) from exc
    return IngestionPlan(normalized, checked_root, sha256_json(normalized))


def load_ingestion_plan(path: Path) -> IngestionPlan:
    """Load and validate one Tika ingestion plan."""

    try:
        resolved = require_regular_file(path, label="ingestion plan")
    except UnsafePathError as exc:
        raise TikaIngestionError(str(exc)) from exc
    try:
        value = json.loads(resolved.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise TikaIngestionError(f"cannot read ingestion plan {resolved}: {exc}") from exc
    return _parse_plan(value, resolved.parent)


def generate_semantic_manifest(plan: Mapping[str, Any]) -> dict[str, Any]:
    """Generate the fixed extraction-provenance Semantic OKF manifest."""

    properties = [
        ("documentTitle", "xsd:string", "document title"),
        ("sourceLocator", "xsd:string", "source locator"),
        ("rawSha256", "xsd:string", "raw input SHA-256"),
        ("rawBytes", "xsd:long", "raw input bytes"),
        ("mediaType", "xsd:string", "detected media type"),
        ("tikaVersion", "xsd:string", "Apache Tika version"),
        ("tikaMetadataSha256", "xsd:string", "canonical Tika metadata SHA-256"),
        ("extractedBodySha256", "xsd:string", "extracted Markdown body SHA-256"),
        ("tikaHandler", "xsd:string", "Tika handler verification contract"),
    ]
    fields = {
        "title": "documentTitle",
        "source_locator": "sourceLocator",
        "raw_sha256": "rawSha256",
        "raw_bytes": "rawBytes",
        "media_type": "mediaType",
        "tika_version": "tikaVersion",
        "tika_metadata_sha256": "tikaMetadataSha256",
        "extracted_body_sha256": "extractedBodySha256",
        "tika_handler": "tikaHandler",
    }
    patterns = {
        "rawSha256": "^[0-9a-f]{64}$",
        "tikaMetadataSha256": "^[0-9a-f]{64}$",
        "extractedBodySha256": "^[0-9a-f]{64}$",
        "tikaVersion": f"^{re.escape(TIKA_VERSION)}$",
        "tikaHandler": _handler_pattern(plan),
    }
    rules: list[dict[str, Any]] = []
    for name, datatype, label in properties:
        rule: dict[str, Any] = {
            "name": f"Required{name[0].upper()}{name[1:]}",
            "target_class": "ExtractedDocument",
            "path": name,
            "min_count": 1,
            "max_count": 1,
            "datatype": datatype,
            "message": f"Every extracted document must retain its {label}.",
            "basis": {
                "kind": "operational-policy",
                "references": ["TIKA-MALLET-INGESTION-1"],
            },
        }
        if name in patterns:
            rule["pattern"] = patterns[name]
        rules.append(rule)
    return {
        "schema_version": SCHEMA_VERSION,
        "bundle": dict(plan["bundle"]),
        "ontology": {
            "classes": [
                {
                    "name": "ExtractedDocument",
                    "label": "Tika-extracted document",
                    "description": (
                        "A local source document whose text and metadata were extracted "
                        "with a hash-bound Apache Tika runtime."
                    ),
                }
            ],
            "properties": [
                {
                    "name": name,
                    "kind": "datatype",
                    "domain": "ExtractedDocument",
                    "range": datatype,
                    "label": label,
                }
                for name, datatype, label in properties
            ],
        },
        "rules": rules,
        "sources": [
            {
                "id": source["id"],
                "kind": "markdown",
                "path": f"tika/extracted/{source['id']}/*.md",
                "concept_type": source["concept_type"],
                "ontology_class": "ExtractedDocument",
                "fields": fields,
                **(
                    {"body_normalization": "line-endings-only"}
                    if _body_mode(source) == VERBATIM_BODY_MODE
                    else {}
                ),
            }
            for source in plan["sources"]
        ],
    }


def _run(
    command: Sequence[str], *, cwd: Path, timeout: int, label: str
) -> tuple[str, str]:
    try:
        completed = subprocess.run(
            list(command),
            cwd=cwd,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=timeout,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise TikaIngestionError(f"{label} failed to execute: {exc}") from exc
    try:
        stdout = completed.stdout.decode("utf-8", errors="strict")
        stderr = completed.stderr.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise TikaIngestionError(f"{label} did not emit valid UTF-8") from exc
    if completed.returncode != 0:
        diagnostic = stderr.strip() or stdout.strip() or "no diagnostic"
        raise TikaIngestionError(
            f"{label} exited {completed.returncode}: {diagnostic[:1000]}"
        )
    return stdout, stderr


def _normalize_output(value: str) -> str:
    return unicodedata.normalize("NFC", value.replace("\r\n", "\n").replace("\r", "\n"))


def _jar_inventory(root: Path) -> tuple[tuple[dict[str, str], ...], str]:
    rows: list[dict[str, str]] = []
    try:
        files, _ = scan_regular_tree(root, label="Tika home")
    except UnsafePathError as exc:
        raise TikaIngestionError(str(exc)) from exc
    for path in (item for item in files if item.suffix.casefold() == ".jar"):
        rows.append(
            {
                "path": path.relative_to(root).as_posix(),
                "sha256": sha256_file(path),
            }
        )
    if not rows:
        raise TikaIngestionError(f"no jars found under Tika home: {root}")
    frozen = tuple(rows)
    return frozen, sha256_json(rows)


def preflight_tika(java: Path, tika_home: Path, timeout: int = 60) -> TikaRuntime:
    """Validate Java 17+ and the exact unpacked Tika beta distribution."""

    try:
        java_path = require_regular_file(java, label="Java executable")
        home = require_real_directory(tika_home, label="Tika home")
    except UnsafePathError as exc:
        raise TikaIngestionError(str(exc)) from exc
    jar = home / f"tika-app-{TIKA_VERSION}.jar"
    try:
        jar = require_regular_file(jar, label="Tika launcher")
    except UnsafePathError as exc:
        raise TikaIngestionError(str(exc)) from exc

    java_stdout, java_stderr = _run(
        [str(java_path), "-version"], cwd=home, timeout=timeout, label="Java preflight"
    )
    java_version = _normalize_output(java_stdout or java_stderr).strip()
    match = re.search(r'version "(\d+)(?:\.|\")', java_version)
    if not match or int(match.group(1)) < 17:
        raise TikaIngestionError("Java 17 or later is required")
    tika_stdout, _ = _run(
        [
            str(java_path),
            "-Dfile.encoding=UTF-8",
            "-Duser.language=en",
            "-Duser.country=US",
            "-Duser.timezone=UTC",
            "-jar",
            str(jar),
            "--version",
        ],
        cwd=home,
        timeout=timeout,
        label="Tika version preflight",
    )
    observed = _normalize_output(tika_stdout).strip()
    if observed != f"Apache Tika {TIKA_VERSION}":
        raise TikaIngestionError(
            f"expected Apache Tika {TIKA_VERSION}, observed {observed!r}"
        )
    inventory, tree_sha256 = _jar_inventory(home)
    return TikaRuntime(
        java=java_path,
        java_version=java_version,
        tika_home=home,
        tika_jar=jar,
        tika_version=TIKA_VERSION,
        jar_inventory=inventory,
        jar_tree_sha256=tree_sha256,
        java_identity=file_identity(java_path),
        home_identity=file_identity(home),
    )


def _verify_tika_runtime(runtime: TikaRuntime) -> None:
    """Re-bind the executable and complete jar tree immediately around execution."""

    if runtime.java_identity is None or runtime.home_identity is None:
        return
    try:
        require_identity(runtime.java, runtime.java_identity, label="Java executable")
        require_identity(runtime.tika_home, runtime.home_identity, label="Tika home")
    except UnsafePathError as exc:
        raise TikaIngestionError(str(exc)) from exc
    inventory, tree_sha256 = _jar_inventory(runtime.tika_home)
    if inventory != runtime.jar_inventory or tree_sha256 != runtime.jar_tree_sha256:
        raise TikaIngestionError("Tika jar inventory changed after preflight")


def _discover(plan: IngestionPlan) -> list[tuple[dict[str, Any], Path, str]]:
    rows: list[tuple[dict[str, Any], Path, str]] = []
    maximum = plan.raw["tika"]["max_input_bytes"]
    try:
        root = require_real_directory(plan.root, label="ingestion plan directory")
    except UnsafePathError as exc:
        raise TikaIngestionError(str(exc)) from exc
    for source in plan.raw["sources"]:
        pattern = str(root / source["path"])
        matches = [lexical_absolute(Path(item)) for item in glob.glob(pattern, recursive=True)]
        files: list[Path] = []
        for path in sorted(set(matches), key=lambda item: item.as_posix()):
            try:
                relative = path.relative_to(root).as_posix()
            except ValueError as exc:
                raise TikaIngestionError(
                    f"source {source['id']!r} escapes the plan directory: {path}"
                ) from exc
            try:
                checked = require_regular_file(
                    path, label=f"source {source['id']!r} input"
                )
            except UnsafePathError as exc:
                raise TikaIngestionError(
                    f"source {source['id']!r} matched an unsafe input {relative}: {exc}"
                ) from exc
            size = os.lstat(checked).st_size
            if size > maximum:
                raise TikaIngestionError(
                    f"source {source['id']!r} input exceeds max_input_bytes: {relative}"
                )
            files.append(checked)
        if not files:
            raise TikaIngestionError(
                f"source {source['id']!r} path matched no regular files"
            )
        rows.extend((source, path, path.relative_to(root).as_posix()) for path in files)
    return rows


def _safe_segment(locator: str) -> str:
    normalized = unicodedata.normalize("NFKD", PurePosixPath(locator).stem)
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", ascii_value).strip(".-_").lower()
    slug = slug[:64] or "document"
    return f"{slug}-{sha256_bytes(locator.encode('utf-8'))[:12]}"


def _yaml_markdown(metadata: Mapping[str, Any], body: str) -> str:
    frontmatter = yaml.safe_dump(
        dict(metadata),
        allow_unicode=True,
        default_flow_style=False,
        sort_keys=True,
    ).rstrip("\n")
    return f"---\n{frontmatter}\n---\n\n{body.rstrip()}\n"


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _write_jsonl(path: Path, rows: Iterable[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(canonical_json(row) + "\n" for row in rows),
        encoding="utf-8",
        newline="\n",
    )


def _tree_inventory(root: Path, relative_root: str) -> tuple[list[dict[str, str]], str]:
    base = root / relative_root
    rows: list[dict[str, str]] = []
    try:
        files, _ = scan_regular_tree(base, label=relative_root)
    except UnsafePathError as exc:
        raise TikaIngestionError(str(exc)) from exc
    for path in files:
        rows.append(
            {
                "path": path.relative_to(root).as_posix(),
                "sha256": sha256_file(path),
            }
        )
    return rows, sha256_json(rows)


def _extract_one(
    runtime: TikaRuntime,
    input_path: Path,
    *,
    timeout: int,
) -> tuple[str, dict[str, Any]]:
    prefix = [
        str(runtime.java),
        "-Dfile.encoding=UTF-8",
        "-Duser.language=en",
        "-Duser.country=US",
        "-Duser.timezone=UTC",
        "-jar",
        str(runtime.tika_jar),
    ]
    _verify_tika_runtime(runtime)
    default_stdout, _ = _run(
        [*prefix, str(input_path)],
        cwd=runtime.tika_home,
        timeout=timeout,
        label=f"Tika default extraction for {input_path.name}",
    )
    _verify_tika_runtime(runtime)
    explicit_stdout, _ = _run(
        [*prefix, "--md", str(input_path)],
        cwd=runtime.tika_home,
        timeout=timeout,
        label=f"Tika Markdown extraction for {input_path.name}",
    )
    default_markdown = _normalize_output(default_stdout)
    explicit_markdown = _normalize_output(explicit_stdout)
    if default_markdown != explicit_markdown:
        raise TikaIngestionError(
            f"Tika default output differs from explicit Markdown for {input_path.name}"
        )
    body = default_markdown.strip()
    if not body:
        raise TikaIngestionError(f"Tika extracted no Markdown text from {input_path.name}")
    _verify_tika_runtime(runtime)
    metadata_stdout, _ = _run(
        [*prefix, "--json", str(input_path)],
        cwd=runtime.tika_home,
        timeout=timeout,
        label=f"Tika metadata extraction for {input_path.name}",
    )
    try:
        metadata = json.loads(_normalize_output(metadata_stdout))
    except json.JSONDecodeError as exc:
        raise TikaIngestionError(
            f"Tika metadata is not valid JSON for {input_path.name}: {exc}"
        ) from exc
    if not isinstance(metadata, dict):
        raise TikaIngestionError(f"Tika metadata must be an object for {input_path.name}")
    _verify_tika_runtime(runtime)
    canonical_metadata = json.loads(canonical_json(metadata))
    return body, canonical_metadata


def _verified_utf8_body(
    snapshot: Path,
    metadata: Mapping[str, Any],
) -> str:
    """Return exact LF UTF-8 text after Tika has independently typed the source."""

    media_type = metadata.get("Content-Type") or metadata.get(
        "Content-Type-Magic-Detected"
    )
    base_type = str(media_type).split(";", 1)[0].strip().casefold()
    if not (
        base_type.startswith("text/")
        or base_type
        in {"application/json", "application/ld+json", "application/x-ndjson"}
    ):
        raise TikaIngestionError(
            f"verbatim UTF-8 mode requires a Tika-detected textual media type: {media_type!r}"
        )
    payload = snapshot.read_bytes()
    if payload.startswith(b"\xef\xbb\xbf"):
        raise TikaIngestionError("verbatim UTF-8 input cannot contain a byte-order mark")
    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise TikaIngestionError("verbatim input is not strict UTF-8") from exc
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    body = text.rstrip("\n")
    if not body or body != body.strip():
        raise TikaIngestionError(
            "verbatim UTF-8 input must have no leading or trailing whitespace"
        )
    return body


def _snapshot_input(source: Path, destination: Path, maximum: int) -> tuple[str, int]:
    """Read a source once into private storage while hashing that exact byte stream."""

    try:
        source = require_regular_file(source, label="Tika source input")
    except UnsafePathError as exc:
        raise TikaIngestionError(str(exc)) from exc
    before = os.lstat(source)
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(source, flags)
    except OSError as exc:
        raise TikaIngestionError(f"cannot open Tika source input {source}: {exc}") from exc
    digest = hashlib.sha256()
    copied = 0
    try:
        opened = os.fstat(descriptor)
        if (
            not stat.S_ISREG(opened.st_mode)
            or (opened.st_dev, opened.st_ino) != (before.st_dev, before.st_ino)
        ):
            raise TikaIngestionError("Tika source identity changed while it was opened")
        if opened.st_size > maximum:
            raise TikaIngestionError(f"Tika source exceeds max_input_bytes: {source}")
        destination.parent.mkdir(parents=True, exist_ok=False)
        with os.fdopen(descriptor, "rb", closefd=False) as input_stream, destination.open(
            "xb"
        ) as output_stream:
            for block in iter(lambda: input_stream.read(1024 * 1024), b""):
                copied += len(block)
                if copied > maximum:
                    raise TikaIngestionError(
                        f"Tika source exceeds max_input_bytes while snapshotting: {source}"
                    )
                digest.update(block)
                output_stream.write(block)
        after = os.fstat(descriptor)
    finally:
        os.close(descriptor)
    stable_fields = ("st_dev", "st_ino", "st_size", "st_mtime_ns", "st_ctime_ns")
    if any(getattr(opened, name) != getattr(after, name) for name in stable_fields):
        destination.unlink(missing_ok=True)
        raise TikaIngestionError("Tika source changed while its private snapshot was created")
    try:
        current = os.lstat(assert_no_links(source, label="Tika source input"))
    except (OSError, UnsafePathError) as exc:
        destination.unlink(missing_ok=True)
        raise TikaIngestionError(f"Tika source identity changed after snapshot: {exc}") from exc
    if (current.st_dev, current.st_ino) != (before.st_dev, before.st_ino):
        destination.unlink(missing_ok=True)
        raise TikaIngestionError("Tika source identity changed after snapshot")
    if copied != after.st_size:
        destination.unlink(missing_ok=True)
        raise TikaIngestionError("Tika private snapshot is incomplete")
    return digest.hexdigest(), copied


def extract_tika_sources(
    plan: IngestionPlan,
    runtime: TikaRuntime,
    output: Path,
    *,
    _precreated_private_output: bool = False,
) -> dict[str, Any]:
    """Create a new closed Tika source tree at *output*."""

    destination = lexical_absolute(output)
    try:
        assert_no_links(destination, label="Tika output", allow_missing_tail=True)
    except UnsafePathError as exc:
        raise TikaIngestionError(str(exc)) from exc
    if _precreated_private_output:
        try:
            require_real_directory(destination, label="private Tika output")
        except UnsafePathError as exc:
            raise TikaIngestionError(str(exc)) from exc
        if any(destination.iterdir()):
            raise TikaIngestionError("private Tika output must start empty")
    else:
        if os.path.lexists(destination):
            raise TikaIngestionError(f"Tika output already exists: {destination}")
        destination.mkdir(parents=True)
    timeout = plan.raw["tika"]["timeout_seconds"]
    rows: list[dict[str, Any]] = []
    seen_outputs: set[str] = set()
    try:
        discovered = _discover(plan)
        with tempfile.TemporaryDirectory(prefix="semantic-okf-tika-raw-") as temporary:
            snapshot_root = Path(temporary)
            for ordinal, (source, input_path, locator) in enumerate(discovered):
                segment = _safe_segment(locator)
                markdown_relative = f"tika/extracted/{source['id']}/{segment}.md"
                metadata_relative = f"tika/metadata/{source['id']}/{segment}.json"
                if markdown_relative.casefold() in seen_outputs:
                    raise TikaIngestionError(
                        f"case-insensitive extracted-path collision: {markdown_relative}"
                    )
                seen_outputs.add(markdown_relative.casefold())
                snapshot_path = snapshot_root / f"{ordinal:08d}" / input_path.name
                raw_sha256, raw_bytes = _snapshot_input(
                    input_path, snapshot_path, plan.raw["tika"]["max_input_bytes"]
                )
                tika_body, tika_metadata = _extract_one(
                    runtime, snapshot_path, timeout=timeout
                )
                body = (
                    _verified_utf8_body(snapshot_path, tika_metadata)
                    if _body_mode(source) == VERBATIM_BODY_MODE
                    else tika_body
                )
                handler = _handler(source)
                metadata_sha256 = sha256_json(tika_metadata)
                body_sha256 = sha256_bytes(body.encode("utf-8"))
                media_type = tika_metadata.get("Content-Type") or tika_metadata.get(
                    "Content-Type-Magic-Detected"
                )
                if not isinstance(media_type, str) or not media_type.strip():
                    raise TikaIngestionError(
                        f"Tika emitted no detected media type for {locator}"
                    )
                title_value = tika_metadata.get("dc:title") or tika_metadata.get(
                    "X-TIKA:resourceName"
                )
                title = str(title_value).strip() if title_value is not None else ""
                if not title or title.lower() == "untitled":
                    title = input_path.name
                frontmatter = {
                    "extracted_body_sha256": body_sha256,
                    "media_type": media_type.strip(),
                    "raw_bytes": raw_bytes,
                    "raw_sha256": raw_sha256,
                    "source_locator": locator,
                    "tika_handler": handler,
                    "tika_metadata_sha256": metadata_sha256,
                    "tika_version": runtime.tika_version,
                    "title": title,
                }
                markdown = _yaml_markdown(frontmatter, body)
                markdown_path = destination / markdown_relative
                markdown_path.parent.mkdir(parents=True, exist_ok=True)
                markdown_path.write_text(markdown, encoding="utf-8", newline="\n")
                metadata_path = destination / metadata_relative
                _write_json(metadata_path, tika_metadata)
                rows.append(
                    {
                        "body_sha256": body_sha256,
                        "concept_type": source["concept_type"],
                        "markdown_path": markdown_relative,
                        "markdown_sha256": sha256_file(markdown_path),
                        "media_type": media_type.strip(),
                        "metadata_path": metadata_relative,
                        "metadata_sha256": metadata_sha256,
                        "raw_bytes": raw_bytes,
                        "raw_sha256": raw_sha256,
                        "source_id": source["id"],
                        "source_locator": locator,
                        "title": title,
                    }
                )
        rows.sort(key=lambda row: (row["source_id"], row["source_locator"]))
        documents_path = destination / TIKA_DOCUMENTS
        _write_jsonl(documents_path, rows)
        extracted_inventory, extracted_sha = _tree_inventory(
            destination, "tika/extracted"
        )
        metadata_inventory, metadata_sha = _tree_inventory(
            destination, "tika/metadata"
        )
        index = {
            "algorithm": _plan_algorithm(plan.raw),
            "artifacts": {
                "documents": {
                    "bytes": documents_path.stat().st_size,
                    "count": len(rows),
                    "path": TIKA_DOCUMENTS,
                    "sha256": sha256_file(documents_path),
                },
                "extracted": {
                    "count": len(extracted_inventory),
                    "inventory_sha256": extracted_sha,
                    "path": "tika/extracted",
                },
                "metadata": {
                    "count": len(metadata_inventory),
                    "inventory_sha256": metadata_sha,
                    "path": "tika/metadata",
                },
            },
            "plan": plan.raw,
            "plan_sha256": plan.sha256,
            "schema_version": SCHEMA_VERSION,
            "summary": {
                "documents": len(rows),
                "sources": len(plan.raw["sources"]),
            },
            "toolchain": {
                "java_version": runtime.java_version,
                "tika_jar_inventory": list(runtime.jar_inventory),
                "tika_jar_tree_sha256": runtime.jar_tree_sha256,
                "tika_version": runtime.tika_version,
            },
        }
        _write_json(destination / TIKA_INDEX, index)
        validate_tika_tree(destination)
        return index
    except Exception:
        shutil.rmtree(destination, ignore_errors=True)
        raise


def _read_json(path: Path, label: str) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise TikaIngestionError(f"cannot read {label}: {exc}") from exc


def _read_jsonl(path: Path, label: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        raise TikaIngestionError(f"cannot read {label}: {exc}") from exc
    for index, line in enumerate(lines, start=1):
        if not line.strip():
            raise TikaIngestionError(f"{label}:{index} is blank")
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise TikaIngestionError(f"{label}:{index} is invalid JSON: {exc}") from exc
        if not isinstance(row, dict):
            raise TikaIngestionError(f"{label}:{index} must be an object")
        rows.append(row)
    return rows


def _safe_artifact(root: Path, value: Any, label: str, suffix: str) -> Path:
    relative = _safe_plan_path(value, label)
    if not relative.endswith(suffix):
        raise TikaIngestionError(f"{label} must end with {suffix}")
    path = lexical_absolute(root / relative)
    try:
        path.relative_to(lexical_absolute(root))
    except ValueError as exc:
        raise TikaIngestionError(f"{label} escapes the bundle") from exc
    try:
        return require_regular_file(path, label=label)
    except UnsafePathError as exc:
        raise TikaIngestionError(f"{label} is missing or unsafe: {relative}: {exc}") from exc


def _split_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = normalized.split("\n")
    if not lines or lines[0] != "---":
        raise TikaIngestionError("extracted Markdown lacks YAML frontmatter")
    try:
        end = lines.index("---", 1)
    except ValueError as exc:
        raise TikaIngestionError("extracted Markdown frontmatter is unterminated") from exc
    try:
        metadata = yaml.safe_load("\n".join(lines[1:end]))
    except yaml.YAMLError as exc:
        raise TikaIngestionError(f"extracted Markdown frontmatter is invalid: {exc}") from exc
    if not isinstance(metadata, dict):
        raise TikaIngestionError("extracted Markdown frontmatter must be an object")
    return metadata, "\n".join(lines[end + 1 :]).strip()


def validate_tika_tree(root: Path) -> dict[str, Any]:
    """Validate the closed Tika receipt and every persisted extraction binding."""

    try:
        bundle = require_real_directory(root, label="Semantic OKF bundle")
    except UnsafePathError as exc:
        raise TikaIngestionError(str(exc)) from exc
    tika_root = bundle / TIKA_DIRECTORY
    try:
        _, _ = scan_regular_tree(tika_root, label="Tika tree")
    except UnsafePathError as exc:
        raise TikaIngestionError(str(exc)) from exc
    allowed_roots = {"index.json", "documents.jsonl", "extracted", "metadata"}
    actual_roots = {path.name for path in tika_root.iterdir()}
    if actual_roots != allowed_roots:
        raise TikaIngestionError(
            "tika directory has an invalid closed tree: "
            f"expected {sorted(allowed_roots)}, observed {sorted(actual_roots)}"
        )
    index_path = bundle / TIKA_INDEX
    documents_path = bundle / TIKA_DOCUMENTS
    index = _read_json(index_path, TIKA_INDEX)
    if not isinstance(index, dict):
        raise TikaIngestionError("tika/index.json root must be an object")
    _exact_keys(
        index,
        {
            "algorithm",
            "artifacts",
            "plan",
            "plan_sha256",
            "schema_version",
            "summary",
            "toolchain",
        },
        "tika index",
    )
    if index["schema_version"] != SCHEMA_VERSION:
        raise TikaIngestionError("Tika index schema or algorithm is unsupported")
    plan = _parse_plan(index["plan"], bundle)
    if index["algorithm"] != _plan_algorithm(plan.raw):
        raise TikaIngestionError("Tika index algorithm disagrees with its plan")
    if index["plan_sha256"] != plan.sha256:
        raise TikaIngestionError("Tika plan digest is stale")
    toolchain = index["toolchain"]
    if not isinstance(toolchain, dict):
        raise TikaIngestionError("Tika toolchain must be an object")
    _exact_keys(
        toolchain,
        {"java_version", "tika_jar_inventory", "tika_jar_tree_sha256", "tika_version"},
        "Tika toolchain",
    )
    if toolchain["tika_version"] != TIKA_VERSION:
        raise TikaIngestionError("Tika toolchain version is unsupported")
    if (
        not isinstance(toolchain["java_version"], str)
        or not (match := re.search(r'version "(\d+)', toolchain["java_version"]))
        or int(match.group(1)) < 17
    ):
        raise TikaIngestionError("Tika Java version binding is invalid")
    jars = toolchain["tika_jar_inventory"]
    if (
        not isinstance(jars, list)
        or not jars
        or any(
            not isinstance(row, dict)
            or set(row) != {"path", "sha256"}
            or not isinstance(row["path"], str)
            or _safe_plan_path(row["path"], "Tika jar path") != row["path"]
            or not isinstance(row["sha256"], str)
            or not SHA256_RE.fullmatch(row["sha256"])
            for row in jars
        )
    ):
        raise TikaIngestionError("Tika jar inventory is malformed")
    if (
        jars != sorted(jars, key=lambda row: row["path"])
        or len({row["path"].casefold() for row in jars}) != len(jars)
    ):
        raise TikaIngestionError("Tika jar inventory must be sorted and unique")
    if not any(row["path"] == "tika-app-4.0.0-beta-1.jar" for row in jars):
        raise TikaIngestionError("Tika jar inventory lacks the beta application jar")
    if toolchain["tika_jar_tree_sha256"] != sha256_json(jars):
        raise TikaIngestionError("Tika jar inventory digest is stale")

    rows = _read_jsonl(documents_path, TIKA_DOCUMENTS)
    expected_row_keys = {
        "body_sha256",
        "concept_type",
        "markdown_path",
        "markdown_sha256",
        "media_type",
        "metadata_path",
        "metadata_sha256",
        "raw_bytes",
        "raw_sha256",
        "source_id",
        "source_locator",
        "title",
    }
    source_by_id = {source["id"]: source for source in plan.raw["sources"]}
    seen_markdown: set[str] = set()
    seen_metadata: set[str] = set()
    seen_inputs: set[tuple[str, str]] = set()
    for index_number, row in enumerate(rows, start=1):
        _exact_keys(row, expected_row_keys, f"Tika document {index_number}")
        source_id = row["source_id"]
        if source_id not in source_by_id:
            raise TikaIngestionError(f"Tika document has unknown source_id: {source_id}")
        if row["concept_type"] != source_by_id[source_id]["concept_type"]:
            raise TikaIngestionError("Tika document concept_type differs from its plan")
        locator = _safe_plan_path(row["source_locator"], "Tika source_locator")
        identity = (source_id, locator)
        if identity in seen_inputs:
            raise TikaIngestionError(f"duplicate Tika input identity: {identity}")
        seen_inputs.add(identity)
        for field in ("body_sha256", "markdown_sha256", "metadata_sha256", "raw_sha256"):
            if not isinstance(row[field], str) or not SHA256_RE.fullmatch(row[field]):
                raise TikaIngestionError(f"Tika document {field} is invalid")
        raw_bytes = _plain_int(row["raw_bytes"], "Tika raw_bytes", 0, 2**63 - 1)
        if raw_bytes > plan.raw["tika"]["max_input_bytes"]:
            raise TikaIngestionError("Tika raw_bytes exceeds the plan limit")
        if (
            not isinstance(row["title"], str)
            or not row["title"]
            or not isinstance(row["media_type"], str)
            or not row["media_type"]
        ):
            raise TikaIngestionError("Tika document title or media type is invalid")
        markdown_path = _safe_artifact(bundle, row["markdown_path"], "markdown_path", ".md")
        metadata_path = _safe_artifact(bundle, row["metadata_path"], "metadata_path", ".json")
        relative_markdown = markdown_path.relative_to(bundle).as_posix()
        relative_metadata = metadata_path.relative_to(bundle).as_posix()
        if not relative_markdown.startswith(f"tika/extracted/{source_id}/"):
            raise TikaIngestionError("Tika markdown path is outside its source partition")
        if relative_markdown.casefold() in seen_markdown:
            raise TikaIngestionError("duplicate case-insensitive Tika markdown path")
        seen_markdown.add(relative_markdown.casefold())
        if not relative_metadata.startswith(f"tika/metadata/{source_id}/"):
            raise TikaIngestionError("Tika metadata path is outside its source partition")
        if relative_metadata.casefold() in seen_metadata:
            raise TikaIngestionError("duplicate case-insensitive Tika metadata path")
        seen_metadata.add(relative_metadata.casefold())
        if sha256_file(markdown_path) != row["markdown_sha256"]:
            raise TikaIngestionError("Tika Markdown hash is stale")
        metadata = _read_json(metadata_path, str(row["metadata_path"]))
        if not isinstance(metadata, dict) or sha256_json(metadata) != row["metadata_sha256"]:
            raise TikaIngestionError("Tika metadata hash is stale")
        frontmatter, body = _split_frontmatter(markdown_path.read_text(encoding="utf-8"))
        expected_frontmatter = {
            "extracted_body_sha256": row["body_sha256"],
            "media_type": row["media_type"],
            "raw_bytes": row["raw_bytes"],
            "raw_sha256": row["raw_sha256"],
            "source_locator": row["source_locator"],
            "tika_handler": _handler(source_by_id[source_id]),
            "tika_metadata_sha256": row["metadata_sha256"],
            "tika_version": TIKA_VERSION,
            "title": row["title"],
        }
        if frontmatter != expected_frontmatter:
            raise TikaIngestionError("Tika Markdown frontmatter differs from its receipt")
        if sha256_bytes(body.encode("utf-8")) != row["body_sha256"]:
            raise TikaIngestionError("Tika extracted body hash is stale")

    if rows != sorted(rows, key=lambda row: (row["source_id"], row["source_locator"])):
        raise TikaIngestionError("Tika document rows are not deterministically ordered")
    if {row["source_id"] for row in rows} != set(source_by_id):
        raise TikaIngestionError("Tika document rows do not cover every planned source")

    artifacts = index["artifacts"]
    if not isinstance(artifacts, dict):
        raise TikaIngestionError("Tika artifacts must be an object")
    _exact_keys(artifacts, {"documents", "extracted", "metadata"}, "Tika artifacts")
    documents_artifact = artifacts["documents"]
    if documents_artifact != {
        "bytes": documents_path.stat().st_size,
        "count": len(rows),
        "path": TIKA_DOCUMENTS,
        "sha256": sha256_file(documents_path),
    }:
        raise TikaIngestionError("Tika documents artifact binding is stale")
    extracted_inventory, extracted_sha = _tree_inventory(bundle, "tika/extracted")
    metadata_inventory, metadata_sha = _tree_inventory(bundle, "tika/metadata")
    if {row["path"].casefold() for row in extracted_inventory} != seen_markdown:
        raise TikaIngestionError("Tika extracted tree and document receipt lack parity")
    if {row["path"].casefold() for row in metadata_inventory} != seen_metadata:
        raise TikaIngestionError("Tika metadata tree and document receipt lack parity")
    if artifacts["extracted"] != {
        "count": len(extracted_inventory),
        "inventory_sha256": extracted_sha,
        "path": "tika/extracted",
    }:
        raise TikaIngestionError("Tika extracted inventory is stale")
    if artifacts["metadata"] != {
        "count": len(metadata_inventory),
        "inventory_sha256": metadata_sha,
        "path": "tika/metadata",
    }:
        raise TikaIngestionError("Tika metadata inventory is stale")
    if index["summary"] != {
        "documents": len(rows),
        "sources": len(plan.raw["sources"]),
    }:
        raise TikaIngestionError("Tika summary is stale")
    return {
        "algorithm": index["algorithm"],
        "documents": len(rows),
        "plan_sha256": plan.sha256,
        "sources": len(plan.raw["sources"]),
        "tika_jar_tree_sha256": toolchain["tika_jar_tree_sha256"],
        "tika_version": TIKA_VERSION,
    }


def validate_tika_semantic_bindings(root: Path) -> dict[str, Any]:
    """Require one exact Semantic OKF ledger record per Tika extraction."""

    try:
        bundle = require_real_directory(root, label="Semantic OKF bundle")
    except UnsafePathError as exc:
        raise TikaIngestionError(str(exc)) from exc
    report = validate_tika_tree(bundle)
    index = _read_json(bundle / TIKA_INDEX, TIKA_INDEX)
    expected_manifest = generate_semantic_manifest(index["plan"])
    semantic_plan = _read_json(
        bundle / "semantic/semantic-plan.json", "semantic/semantic-plan.json"
    )
    if semantic_plan != expected_manifest:
        raise TikaIngestionError("Semantic plan differs from the Tika-generated manifest")
    documents = _read_jsonl(bundle / TIKA_DOCUMENTS, TIKA_DOCUMENTS)
    records = _read_jsonl(
        bundle / "semantic/records.jsonl", "semantic/records.jsonl"
    )
    document_by_path = {row["markdown_path"]: row for row in documents}
    source_by_id = {
        source["id"]: source for source in index["plan"]["sources"]
    }
    record_by_path = {row.get("source_path"): row for row in records}
    if len(record_by_path) != len(records) or set(document_by_path) != set(record_by_path):
        raise TikaIngestionError("Tika documents and Semantic OKF records lack parity")
    for path, document in document_by_path.items():
        record = record_by_path[path]
        if record.get("source_id") != document["source_id"]:
            raise TikaIngestionError("Tika source identity differs from the ledger")
        if record.get("title") != document["title"]:
            raise TikaIngestionError("Tika title differs from the ledger")
        if sha256_bytes(str(record.get("body", "")).encode("utf-8")) != document[
            "body_sha256"
        ]:
            raise TikaIngestionError("Tika body differs from the authoritative ledger")
        attributes = record.get("attributes")
        expected_attributes = {
            "extracted_body_sha256": document["body_sha256"],
            "media_type": document["media_type"],
            "raw_bytes": document["raw_bytes"],
            "raw_sha256": document["raw_sha256"],
            "source_locator": document["source_locator"],
            "tika_handler": _handler(source_by_id[document["source_id"]]),
            "tika_metadata_sha256": document["metadata_sha256"],
            "tika_version": TIKA_VERSION,
            "title": document["title"],
        }
        if attributes != expected_attributes:
            raise TikaIngestionError("Tika provenance attributes differ from the ledger")
    return report


def stage_tika_inputs(
    plan_path: Path,
    *,
    java: Path,
    tika_home: Path,
) -> tuple[Path, Path, TikaRuntime, dict[str, Any]]:
    """Create a disposable manifest root containing Tika sources and a manifest."""

    plan = load_ingestion_plan(plan_path)
    runtime = preflight_tika(java, tika_home, plan.raw["tika"]["timeout_seconds"])
    stage = Path(tempfile.mkdtemp(prefix="semantic-okf-tika-inputs-"))
    try:
        extract_tika_sources(
            plan, runtime, stage, _precreated_private_output=True
        )
        manifest_path = stage / "semantic-manifest.json"
        _write_json(manifest_path, generate_semantic_manifest(plan.raw))
        return stage, manifest_path, runtime, plan.raw
    except Exception:
        shutil.rmtree(stage, ignore_errors=True)
        raise


def copy_tika_tree(stage: Path, bundle: Path) -> None:
    """Copy the validated Tika tree into an unpublished bundle candidate."""

    validate_tika_tree(stage)
    destination = bundle / TIKA_DIRECTORY
    if os.path.lexists(destination):
        raise TikaIngestionError(f"bundle candidate already contains {TIKA_DIRECTORY}")
    shutil.copytree(stage / TIKA_DIRECTORY, destination, copy_function=shutil.copy2)
    validate_tika_tree(bundle)
