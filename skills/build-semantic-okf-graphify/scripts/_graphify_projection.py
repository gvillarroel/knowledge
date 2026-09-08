"""Build and validate a deterministic Graphify projection over Semantic OKF.

The Semantic OKF ledger and concept Markdown remain authoritative.  Graphify is
used only to extract a structural, read-only discovery graph from deterministic
temporary Markdown views whose headings expose reviewed record attributes.
"""

from __future__ import annotations

import hashlib
import importlib
import importlib.metadata
import json
import math
import os
import posixpath
import re
import shutil
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Mapping

import yaml


CONTRACT = "semantic-okf-graphify/1.0"
GRAPHIFY_DISTRIBUTION = "graphifyy"
GRAPHIFY_VERSION = "0.9.17"
LEXICAL_NEIGHBORS = 1
LEXICAL_ROOT_ROLE = "record-root"
LEXICAL_SIMILARITY_PROJECTION = "harbor-lexical-similarity"
LEXICAL_TOKEN_RE = re.compile(r"\w+", re.UNICODE)
ENGINE_MODE = "markdown-structural-no-llm"
PROJECTION_RELATIVE_PATH = PurePosixPath("retrieval/graphify")
GRAPH_RELATIVE_PATH = PROJECTION_RELATIVE_PATH / "graph.json"
INDEX_RELATIVE_PATH = PROJECTION_RELATIVE_PATH / "index.json"
RECORDS_RELATIVE_PATH = PurePosixPath("semantic/records.jsonl")
VIEW_ROOT_NAME = ".graphify-views"
HEX_RE = re.compile(r"^[0-9a-f]{64}$")
CONCEPT_LAYOUT_SOURCE_PACKED = "source-packed-v1"
CONCEPT_LAYOUT_RECORD_PER_FILE = "record-per-file-v1"
STRUCTURED_SOURCE_KINDS = {"csv", "json", "rdf"}
OKF_VERSION = "0.2"
RECORD_IDENTITY_FIELDS = (
    "concept_id",
    "concept_path",
    "concept_type",
    "paper_id",
    "record_id",
    "record_sha256",
    "source_id",
)
RECORD_INDEX_FIELDS = (*RECORD_IDENTITY_FIELDS, "view_path", "view_sha256")


class GraphifyProjectionError(RuntimeError):
    """A stable, user-facing Graphify projection failure."""


def canonical_json(value: Any) -> str:
    """Return deterministic UTF-8-safe JSON text."""

    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
    )


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def sha256_json(value: Any) -> str:
    return sha256_bytes(canonical_json(value).encode("utf-8"))


def _remove_tree_verified(path: Path, label: str) -> None:
    """Remove an ephemeral tree and fail rather than publish after partial cleanup."""

    if not path.exists():
        return
    try:
        shutil.rmtree(path)
    except OSError as exc:
        raise GraphifyProjectionError(f"cannot remove {label}: {exc}") from exc
    if path.exists():
        raise GraphifyProjectionError(f"cannot remove {label}: path still exists")


def _relative(path: Path, root: Path) -> str:
    try:
        relative = path.resolve().relative_to(root.resolve()).as_posix()
    except (OSError, ValueError) as exc:
        raise GraphifyProjectionError(f"path escapes the bundle: {path}") from exc
    if not relative or relative.startswith("../"):
        raise GraphifyProjectionError(f"path escapes the bundle: {path}")
    return relative


def _projection_path(relative: str) -> bool:
    path = PurePosixPath(relative)
    return path == PROJECTION_RELATIVE_PATH or PROJECTION_RELATIVE_PATH in path.parents


def core_artifacts(root: Path) -> list[dict[str, Any]]:
    """Fingerprint the complete authoritative bundle outside this projection."""

    artifacts: list[dict[str, Any]] = []
    for path in sorted(
        (candidate for candidate in root.rglob("*") if candidate.is_file()),
        key=lambda item: item.relative_to(root).as_posix(),
    ):
        relative = path.relative_to(root).as_posix()
        if _projection_path(relative) or PurePosixPath(relative).parts[0] == VIEW_ROOT_NAME:
            continue
        if path.is_symlink():
            raise GraphifyProjectionError(f"symlink is not allowed in a release: {relative}")
        artifacts.append(
            {"path": relative, "bytes": path.stat().st_size, "sha256": sha256_file(path)}
        )
    return artifacts


def core_tree_sha256(artifacts: Iterable[Mapping[str, Any]]) -> str:
    return sha256_json(
        [
            {
                "path": str(item["path"]),
                "bytes": int(item["bytes"]),
                "sha256": str(item["sha256"]),
            }
            for item in artifacts
        ]
    )


def load_records(root: Path) -> list[dict[str, Any]]:
    path = root / RECORDS_RELATIVE_PATH
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        raise GraphifyProjectionError(f"cannot read {RECORDS_RELATIVE_PATH}: {exc}") from exc
    records: list[dict[str, Any]] = []
    for number, line in enumerate(lines, 1):
        if not line.strip():
            raise GraphifyProjectionError(f"blank record at {RECORDS_RELATIVE_PATH}:{number}")
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise GraphifyProjectionError(
                f"invalid JSON at {RECORDS_RELATIVE_PATH}:{number}: {exc}"
            ) from exc
        if not isinstance(value, dict):
            raise GraphifyProjectionError(
                f"record at {RECORDS_RELATIVE_PATH}:{number} must be an object"
            )
        records.append(value)
    if not records:
        raise GraphifyProjectionError("record ledger is empty")
    return records


def _concept_document_paths(
    root: Path, records: list[dict[str, Any]]
) -> dict[str, str]:
    """Map stable logical concept locators to physical Markdown documents."""

    report = _load_json_object(root / "semantic" / "build-report.json", "build report")
    processor = report.get("processor")
    layout = processor.get("concept_layout") if isinstance(processor, Mapping) else None
    source_counts: dict[str, int] = {}
    for record in records:
        source_id = record.get("source_id")
        if isinstance(source_id, str):
            source_counts[source_id] = source_counts.get(source_id, 0) + 1
    result: dict[str, str] = {}
    for record in records:
        logical = str(record.get("concept_path", ""))
        source_id = record.get("source_id")
        packed = (
            layout == CONCEPT_LAYOUT_SOURCE_PACKED
            and record.get("source_kind") in STRUCTURED_SOURCE_KINDS
            and isinstance(source_id, str)
            and source_counts.get(source_id, 0) > 1
        )
        result[logical] = f"concepts/{source_id}.md" if packed else logical
    return result


def _safe_text(value: Any) -> str:
    text = " ".join(str(value).replace("\x00", " ").split())
    return text.translate(
        str.maketrans(
            {
                "#": "＃",
                "[": "［",
                "]": "］",
                "(": "（",
                ")": "）",
                "<": "＜",
                ">": "＞",
            }
        )
    ).strip()


def _yaml_scalar(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def _view_name(record: Mapping[str, Any]) -> str:
    identity = f"{record.get('source_id', '')}\0{record.get('record_id', '')}"
    return f"{sha256_bytes(identity.encode('utf-8'))[:24]}.md"


def _iter_scalars(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, (bool, int)):
        yield str(value)
    elif isinstance(value, float) and math.isfinite(value):
        yield str(value)
    elif isinstance(value, list):
        for item in value:
            yield from _iter_scalars(item)


def _paper_id(
    record: Mapping[str, Any], subject_records: Mapping[str, Mapping[str, Any]]
) -> str | None:
    attributes = record.get("attributes")
    if isinstance(attributes, dict):
        direct = attributes.get("paper_id")
        if isinstance(direct, str) and direct:
            return direct
        for value in attributes.values():
            for scalar in _iter_scalars(value):
                target = subject_records.get(scalar)
                target_attributes = target.get("attributes") if target else None
                candidate = (
                    target_attributes.get("paper_id")
                    if isinstance(target_attributes, dict)
                    else None
                )
                if isinstance(candidate, str) and candidate:
                    return candidate
    match = re.search(
        r"(?:^|[-/])(\d{4})[.-](\d{4,5}v\d+)(?:$|[-/])",
        str(record.get("source_id", "")),
        re.IGNORECASE,
    )
    return f"{match.group(1)}.{match.group(2)}" if match else None


def _heading_values(record: Mapping[str, Any]) -> list[tuple[str, str]]:
    values: list[tuple[str, str]] = []
    attributes = record.get("attributes")
    if not isinstance(attributes, dict):
        attributes = {}
    preferred = (
        "interpretation",
        "definition",
        "description",
        "label",
        "claim_kind",
        "term_kind",
        "selection_dimension",
        "selectionDimension",
    )
    ordered_names = [name for name in preferred if name in attributes]
    ordered_names.extend(sorted(set(attributes) - set(ordered_names)))
    for name in ordered_names:
        for scalar in _iter_scalars(attributes[name]):
            text = _safe_text(scalar)
            if (
                not text
                or text.startswith(("http://", "https://"))
                or HEX_RE.fullmatch(text.lower())
                or len(text) > 1200
            ):
                continue
            values.append((_safe_text(name.replace("_", " ")), text))
    return values


def _record_maps(
    records: Iterable[Mapping[str, Any]],
) -> tuple[dict[str, Mapping[str, Any]], dict[str, str]]:
    subject_records = {
        str(record.get("subject_iri")): record
        for record in records
        if isinstance(record.get("subject_iri"), str) and record.get("subject_iri")
    }
    subject_views = {
        subject: f"records/{_view_name(record)}" for subject, record in subject_records.items()
    }
    return subject_records, subject_views


def _record_tokens(record: Mapping[str, Any]) -> set[str]:
    """Return deterministic lexical features from authoritative record text."""

    text = "\n".join(
        str(value)
        for value in (
            record.get("title", ""),
            record.get("record_id", ""),
            record.get("concept_type", ""),
            record.get("body", ""),
        )
        if value
    )
    return {token for token in LEXICAL_TOKEN_RE.findall(text.casefold()) if len(token) >= 2}


def _lexical_similarity_pairs(
    records: Iterable[Mapping[str, Any]],
) -> list[tuple[str, str, float]]:
    """Select a symmetric deterministic cross-partition TF-IDF neighbor graph."""

    values = list(records)
    identity_parts = [PurePosixPath(str(record.get("record_id", ""))).parts for record in values]
    common = 0
    for parts in zip(*identity_parts):
        if len(set(parts)) != 1:
            break
        common += 1
    rows = sorted(
        (
            (
                str(record.get("concept_path", "")),
                _record_tokens(record),
                parts[common] if common < len(parts) else "",
            )
            for record, parts in zip(values, identity_parts)
        ),
        key=lambda row: row[0],
    )
    document_frequency: dict[str, int] = {}
    for _path, tokens, _partition in rows:
        for token in tokens:
            document_frequency[token] = document_frequency.get(token, 0) + 1
    total = len(rows)
    weights = {
        token: math.log((total + 1) / (frequency + 1)) + 1.0
        for token, frequency in document_frequency.items()
    }
    norms = [
        math.sqrt(sum(weights[token] ** 2 for token in tokens))
        for _path, tokens, _partition in rows
    ]
    scores: dict[tuple[int, int], float] = {}
    for left in range(total):
        for right in range(left + 1, total):
            common = rows[left][1] & rows[right][1]
            if not common or not norms[left] or not norms[right]:
                continue
            score = sum(weights[token] ** 2 for token in common) / (norms[left] * norms[right])
            if score > 0:
                scores[(left, right)] = score

    directed: set[tuple[int, int]] = set()
    bridge_partitions = len({row[2] for row in rows}) > 1
    for index in range(total):
        candidates = [
            (score, right if left == index else left)
            for (left, right), score in scores.items()
            if left == index or right == index
            if not bridge_partitions or rows[left][2] != rows[right][2]
        ]
        candidates.sort(key=lambda item: (-item[0], rows[item[1]][0]))
        for _score, neighbor in candidates[:LEXICAL_NEIGHBORS]:
            directed.add((index, neighbor))
    selected = {
        tuple(sorted((left, right)))
        for left, right in directed
        if (right, left) in directed
    }
    return [
        (rows[left][0], rows[right][0], round(scores[(left, right)], 12))
        for left, right in sorted(selected, key=lambda pair: (rows[pair[0]][0], rows[pair[1]][0]))
    ]


def _record_identity(
    record: Mapping[str, Any], subject_records: Mapping[str, Mapping[str, Any]]
) -> dict[str, Any]:
    return {
        "concept_id": str(record.get("concept_id", "")),
        "concept_path": str(record.get("concept_path", "")),
        "concept_type": str(record.get("concept_type", "")),
        "paper_id": _paper_id(record, subject_records),
        "record_id": str(record.get("record_id", "")),
        "record_sha256": str(record.get("record_sha256", "")),
        "source_id": str(record.get("source_id", "")),
    }


def _render_view(
    record: Mapping[str, Any],
    subject_records: Mapping[str, Mapping[str, Any]],
    subject_views: Mapping[str, str],
) -> tuple[str, str]:
    """Render the exact ephemeral Markdown input from authoritative ledger fields."""

    concept_path = str(record.get("concept_path", ""))
    view_relative = f"{VIEW_ROOT_NAME}/records/{_view_name(record)}"
    view_parent = PurePosixPath(view_relative).parent.as_posix()
    title = _safe_text(record.get("title") or record.get("record_id") or "Untitled record")
    lines = [
        "---",
        'type: "Graphify Projection View"',
        f"concept_path: {_yaml_scalar(concept_path)}",
        f"record_sha256: {_yaml_scalar(str(record.get('record_sha256', '')))}",
        "---",
        "",
        f"# {title}",
        "",
        f"## Type: {_safe_text(record.get('concept_type', 'Record'))}",
        "",
        f"## Record ID: {_safe_text(record.get('record_id', ''))}",
        "",
    ]
    for name, value in _heading_values(record):
        lines.extend((f"## {name}: {value}", ""))
    own_target = posixpath.relpath(concept_path, start=view_parent)
    lines.extend((f"- [Authoritative concept]({own_target})", ""))
    attributes = record.get("attributes")
    relations: list[tuple[str, str]] = []
    if isinstance(attributes, dict):
        for name in sorted(attributes):
            for scalar in _iter_scalars(attributes[name]):
                target_view = subject_views.get(scalar)
                if target_view:
                    target = f"{VIEW_ROOT_NAME}/{target_view}"
                    relations.append(
                        (_safe_text(name.replace("_", " ")), posixpath.relpath(target, start=view_parent))
                    )
    for name, target in sorted(set(relations)):
        lines.append(f"- [{name}]({target})")
    return view_relative, "\n".join(lines).rstrip() + "\n"


def _expected_index_entry(
    record: Mapping[str, Any],
    subject_records: Mapping[str, Mapping[str, Any]],
    subject_views: Mapping[str, str],
) -> dict[str, Any]:
    view_relative, text = _render_view(record, subject_records, subject_views)
    return {
        **_record_identity(record, subject_records),
        "view_path": view_relative,
        "view_sha256": sha256_bytes(text.encode("utf-8")),
    }


def _write_views(root: Path, records: list[dict[str, Any]]) -> tuple[Path, list[dict[str, Any]]]:
    view_root = root / VIEW_ROOT_NAME
    if view_root.exists():
        raise GraphifyProjectionError(f"reserved temporary path already exists: {view_root}")
    record_root = view_root / "records"
    record_root.mkdir(parents=True)
    subject_records, subject_views = _record_maps(records)
    concept_documents = _concept_document_paths(root, records)
    entries: list[dict[str, Any]] = []
    for record in records:
        concept_path = str(record.get("concept_path", ""))
        concept = root / PurePosixPath(concept_documents.get(concept_path, ""))
        if not concept_path or not concept.is_file() or concept.is_symlink():
            raise GraphifyProjectionError(f"record has an invalid concept_path: {concept_path!r}")
        view_relative, text = _render_view(record, subject_records, subject_views)
        view_path = root / PurePosixPath(view_relative)
        view_path.write_text(text, encoding="utf-8", newline="\n")
        entries.append(_expected_index_entry(record, subject_records, subject_views))
    entries.sort(key=lambda item: (item["source_id"], item["record_id"], item["concept_path"]))
    return view_root, entries


def _canonical_graph(data: dict[str, Any]) -> dict[str, Any]:
    data = dict(data)
    data.pop("built_at_commit", None)
    nodes = data.get("nodes")
    links = data.get("links", data.get("edges"))
    hyperedges = data.get("hyperedges", [])
    if not isinstance(nodes, list) or not isinstance(links, list) or not isinstance(hyperedges, list):
        raise GraphifyProjectionError("Graphify emitted an invalid node-link graph")
    for label, values in (("node", nodes), ("link", links), ("hyperedge", hyperedges)):
        if any(not isinstance(item, dict) for item in values):
            raise GraphifyProjectionError(f"Graphify emitted a non-object {label}")
    data.pop("edges", None)
    data["nodes"] = sorted(nodes, key=lambda item: str(item.get("id", "")))
    data["links"] = sorted(
        links,
        key=lambda item: (
            str(item.get("source", "")),
            str(item.get("target", "")),
            str(item.get("relation", "")),
            str(item.get("source_file", "")),
            str(item.get("source_location", "")),
        ),
    )
    data["hyperedges"] = sorted(hyperedges, key=lambda item: str(item.get("id", "")))
    return data


class _VirtualMarkdownPath:
    """Expose deterministic Markdown text to Graphify without materializing a file."""

    def __init__(self, path: Path, text: str) -> None:
        self._path = path
        self._text = text

    @property
    def name(self) -> str:
        return self._path.name

    @property
    def parent(self) -> Path:
        return self._path.parent

    def read_text(self, *_args: Any, **_kwargs: Any) -> str:
        return self._text

    def with_suffix(self, suffix: str) -> Path:
        return self._path.with_suffix(suffix)

    def __fspath__(self) -> str:
        return os.fspath(self._path)

    def __str__(self) -> str:
        return str(self._path)


def _record_per_file_text(
    record: Mapping[str, Any], manifest: Mapping[str, Any]
) -> str:
    """Reconstruct the exact legacy concept Markdown used by Graphify discovery."""

    body = record.get("body")
    title = record.get("title")
    bundle = manifest.get("bundle")
    if not isinstance(body, str) or not isinstance(title, str) or not isinstance(bundle, Mapping):
        raise GraphifyProjectionError("cannot reconstruct a record-per-file Graphify view")
    description = next(
        (line.strip() for line in body.splitlines() if line.strip() and not line.startswith("#")),
        title,
    )
    payload = {
        "type": record.get("concept_type"),
        "title": title,
        "description": description[:240],
        "resource": record.get("subject_iri"),
        "tags": [
            record.get("source_id"),
            record.get("source_kind"),
            str(bundle.get("owl_profile", "")).lower(),
        ],
        "sources": [
            {
                "id": record.get("source_id"),
                "resource": record.get("source_path"),
                "title": record.get("source_id"),
            }
        ],
        "generated": {"by": "process:semantic-okf-python"},
        "concept_id": record.get("concept_id"),
        "concept_path": record.get("concept_path"),
        "subject_iri": record.get("subject_iri"),
        "ontology_class_iri": record.get("ontology_class_iri"),
        "ontology_version_iri": bundle.get("version_iri"),
        "source_id": record.get("source_id"),
        "source_kind": record.get("source_kind"),
        "source_path": record.get("source_path"),
        "source_content_sha256": record.get("source_content_sha256"),
        "record_sha256": record.get("record_sha256"),
        "source_refs": record.get("source_refs"),
        "record_id": record.get("record_id"),
    }
    frontmatter = yaml.safe_dump(
        payload,
        allow_unicode=True,
        sort_keys=False,
        default_flow_style=False,
    ).rstrip()
    rendered_body = body.rstrip() or f"# {title}"
    return f"---\n{frontmatter}\n---\n\n{rendered_body}\n"


def _record_per_file_index_text(
    records: Iterable[Mapping[str, Any]], manifest: Mapping[str, Any]
) -> str:
    bundle = manifest.get("bundle")
    if not isinstance(bundle, Mapping) or not isinstance(bundle.get("title"), str):
        raise GraphifyProjectionError("semantic plan has invalid bundle metadata")
    lines = ["---", f'okf_version: "{OKF_VERSION}"', "---", "", f"# {bundle['title']}", ""]
    for record in sorted(records, key=lambda item: str(item.get("concept_id", ""))):
        lines.append(
            f"* [{record.get('title')}]({record.get('concept_path')}) - "
            f"{record.get('concept_type')} from {record.get('source_id')}."
        )
    return "\n".join(lines) + "\n"


def _declared_concept_layout(root: Path) -> str:
    report = _load_json_object(root / "semantic" / "build-report.json", "build report")
    processor = report.get("processor")
    if not isinstance(processor, Mapping):
        raise GraphifyProjectionError("build report processor metadata is missing")
    layout = processor.get("concept_layout", CONCEPT_LAYOUT_RECORD_PER_FILE)
    if layout not in {CONCEPT_LAYOUT_RECORD_PER_FILE, CONCEPT_LAYOUT_SOURCE_PACKED}:
        raise GraphifyProjectionError(f"unsupported concept layout in build report: {layout!r}")
    return str(layout)


def _legacy_graphify_documents(
    root: Path,
    records: list[dict[str, Any]],
    view_entries: list[dict[str, Any]],
) -> list[tuple[str, str]]:
    """Return legacy-equivalent Markdown inputs without expanding the packed bundle."""

    manifest = _load_json_object(root / "semantic" / "semantic-plan.json", "semantic plan")
    documents: dict[str, str] = {"index.md": _record_per_file_index_text(records, manifest)}
    for record in records:
        relative = record.get("concept_path")
        if not isinstance(relative, str):
            raise GraphifyProjectionError("record has an invalid logical concept path")
        logical = PurePosixPath(relative)
        if logical.is_absolute() or ".." in logical.parts or "\\" in relative:
            raise GraphifyProjectionError(f"record has an unsafe logical concept path: {relative}")
        if relative in documents:
            raise GraphifyProjectionError(f"duplicate virtual Graphify document: {relative}")
        documents[relative] = _record_per_file_text(record, manifest)
    for entry in view_entries:
        relative = entry.get("view_path")
        view = _safe_bundle_path(root, relative, "record view path")
        assert isinstance(relative, str)
        if relative in documents:
            raise GraphifyProjectionError(f"duplicate virtual Graphify document: {relative}")
        try:
            documents[relative] = view.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            raise GraphifyProjectionError(f"cannot read record view: {relative}") from exc
    return sorted(documents.items())


def _extract_virtual_markdown(
    root: Path, documents: list[tuple[str, str]]
) -> dict[str, Any]:
    """Run the pinned Markdown extractor in memory with Graphify's canonical IDs."""

    extract_module = importlib.import_module("graphify.extract")
    markdown_module = importlib.import_module("graphify.extractors.markdown")
    base_module = importlib.import_module("graphify.extractors.base")
    extract_markdown = getattr(markdown_module, "extract_markdown", None)
    file_node_id = getattr(extract_module, "_file_node_id", None)
    disambiguate = getattr(extract_module, "_disambiguate_colliding_node_ids", None)
    rewire = getattr(extract_module, "_rewire_unique_stub_nodes", None)
    make_id = getattr(base_module, "_make_id", None)
    if not all(
        callable(item)
        for item in (extract_markdown, file_node_id, disambiguate, rewire, make_id)
    ):
        raise GraphifyProjectionError("pinned Graphify Markdown extraction API is unavailable")

    root = root.resolve()
    paths: list[tuple[Path, Path, str]] = []
    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    for relative, content in documents:
        posix = PurePosixPath(relative)
        path = root.joinpath(*posix.parts)
        result = extract_markdown(_VirtualMarkdownPath(path, content))
        if not isinstance(result, dict) or result.get("error"):
            detail = result.get("error") if isinstance(result, dict) else "invalid result"
            raise GraphifyProjectionError(
                f"Graphify could not extract virtual Markdown {relative}: {detail}"
            )
        nodes.extend(result.get("nodes", []))
        edges.extend(result.get("edges", []))
        paths.append((path, Path(*posix.parts), relative))

    id_remap: dict[str, str] = {}
    prefix_remap: dict[Path, tuple[str, str]] = {}
    for path, relative_path, _relative in paths:
        new_id = file_node_id(relative_path)
        old_file_id = make_id(str(path))
        old_prefix = file_node_id(path)
        if old_file_id != new_id:
            id_remap[old_file_id] = new_id
        if old_prefix != new_id:
            prefix_remap[path.resolve()] = (old_prefix, new_id)
    for node in nodes:
        if node.get("id") in id_remap:
            node["id"] = id_remap[node["id"]]
    for edge in edges:
        if edge.get("source") in id_remap:
            edge["source"] = id_remap[edge["source"]]
        if edge.get("target") in id_remap:
            edge["target"] = id_remap[edge["target"]]

    symbol_remap: dict[str, str] = {}
    for node in nodes:
        source_file = node.get("source_file")
        remap = prefix_remap.get(Path(source_file).resolve()) if source_file else None
        node_id = node.get("id")
        if remap and isinstance(node_id, str) and node_id.startswith(remap[0] + "_"):
            symbol_remap[node_id] = remap[1] + node_id[len(remap[0]) :]
    for node in nodes:
        if node.get("id") in symbol_remap:
            node["id"] = symbol_remap[node["id"]]
    for edge in edges:
        if edge.get("source") in symbol_remap:
            edge["source"] = symbol_remap[edge["source"]]
        if edge.get("target") in symbol_remap:
            edge["target"] = symbol_remap[edge["target"]]

    disambiguate(nodes, edges, [], root)
    rewire(nodes, edges)
    for item in [*nodes, *edges]:
        source_file = item.get("source_file")
        if source_file and Path(source_file).is_absolute():
            try:
                item["source_file"] = Path(source_file).relative_to(root).as_posix()
            except ValueError as exc:
                raise GraphifyProjectionError("virtual Graphify source escaped the bundle") from exc
    for node in nodes:
        node.pop("origin_file", None)
        node.pop("_callable", None)
        node["_origin"] = "ast"
    for edge in edges:
        edge["_origin"] = "ast"
    return {"nodes": nodes, "edges": edges, "input_tokens": 0, "output_tokens": 0}


def _normalize_local_heading_ids(root: Path, data: dict[str, Any]) -> None:
    """Remove the pinned extractor's absolute-path ID for an empty heading.

    Graphify relativizes symbols only when an underscore follows the file stem.
    An empty heading has the bare stem, which otherwise leaks the temporary
    build directory into published graph bytes. Keep it distinct from the file
    root and preserve labels, source locations, and every relationship.
    """

    file_node_id = importlib.import_module("graphify.extract")._file_node_id
    root = root.resolve()
    occupied = {node.get("id") for node in data.get("nodes", [])}
    remap: dict[str, str] = {}
    for node in data.get("nodes", []):
        source = node.get("source_file")
        if not isinstance(source, str) or not source:
            continue
        source_path = Path(source)
        absolute = (source_path if source_path.is_absolute() else root / source_path).resolve()
        try:
            relative = absolute.relative_to(root)
        except ValueError:
            continue
        absolute_id = file_node_id(absolute)
        if node.get("id") != absolute_id or absolute_id == file_node_id(relative):
            continue
        location = node.get("source_location")
        if not isinstance(location, str) or not location:
            raise GraphifyProjectionError("bare-stem Graphify heading has no source location")
        # A colon cannot occur in Graphify's normalized IDs. Bind the full
        # digest to the local document and location, and reject any collision.
        binding = canonical_json([relative.as_posix(), location]).encode("utf-8")
        replacement = "semantic-okf:heading:" + sha256_bytes(binding)
        if replacement in occupied:
            raise GraphifyProjectionError("normalized Graphify heading identity collides")
        if absolute_id in remap and remap[absolute_id] != replacement:
            raise GraphifyProjectionError("Graphify heading identity is ambiguous")
        occupied.add(replacement)
        remap[absolute_id] = replacement
    for node in data.get("nodes", []):
        if node.get("id") in remap:
            node["id"] = remap[node["id"]]
    for edge in data.get("links", data.get("edges", [])):
        for endpoint in ("source", "target"):
            if edge.get(endpoint) in remap:
                edge[endpoint] = remap[edge[endpoint]]


def _run_graphify(root: Path, view_entries: list[dict[str, Any]], output: Path) -> dict[str, Any]:
    installed = importlib.metadata.version(GRAPHIFY_DISTRIBUTION)
    if installed != GRAPHIFY_VERSION:
        raise GraphifyProjectionError(
            f"{GRAPHIFY_DISTRIBUTION} {GRAPHIFY_VERSION} is required; found {installed}"
        )
    cache_root = Path(tempfile.mkdtemp(prefix="semantic-okf-graphify-cache-"))
    previous_out = os.environ.get("GRAPHIFY_OUT")
    os.environ["GRAPHIFY_OUT"] = str(cache_root / "graphify-out")
    try:
        graphify = importlib.import_module("graphify")
        export = importlib.import_module("graphify.export")
        graphify_extract = graphify.extract
        if _declared_concept_layout(root) == CONCEPT_LAYOUT_SOURCE_PACKED:
            extraction = _extract_virtual_markdown(
                root, _legacy_graphify_documents(root, load_records(root), view_entries)
            )
        else:
            markdown_paths = sorted(
                (
                    path
                    for path in root.rglob("*.md")
                    if path.is_file()
                    and not _projection_path(path.relative_to(root).as_posix())
                ),
                key=lambda path: path.relative_to(root).as_posix(),
            )
            extraction = graphify_extract(markdown_paths, cache_root=root, parallel=False)
        graph = graphify.build_from_json(extraction, directed=False, root=root)
        output.parent.mkdir(parents=True, exist_ok=True)
        if not export.to_json(graph, {}, str(output), force=True, built_at_commit=""):
            raise GraphifyProjectionError("Graphify refused to serialize the graph")
        data = json.loads(output.read_text(encoding="utf-8"))
        _normalize_local_heading_ids(root, data)
    except GraphifyProjectionError:
        raise
    except Exception as exc:
        raise GraphifyProjectionError(f"Graphify extraction failed: {exc}") from exc
    finally:
        if previous_out is None:
            os.environ.pop("GRAPHIFY_OUT", None)
        else:
            os.environ["GRAPHIFY_OUT"] = previous_out
        _remove_tree_verified(cache_root, "temporary Graphify cache")

    by_view = {entry["view_path"]: entry for entry in view_entries}
    records = load_records(root)
    root_by_path: dict[str, str] = {}
    for node in data.get("nodes", []):
        source = str(node.get("source_file", "")).replace("\\", "/")
        source = source.removeprefix("./")
        entry = by_view.get(source)
        if entry:
            node["projection_source_file"] = source
            node["projection_source_location"] = node.get("source_location")
            node["source_file"] = entry["concept_path"]
            node["source_location"] = None
            for field in (
                "concept_id",
                "concept_path",
                "concept_type",
                "paper_id",
                "record_id",
                "record_sha256",
                "source_id",
            ):
                node[field] = entry[field]
            node["projection"] = "graphify-view"
            if str(node.get("label", "")) == PurePosixPath(source).name:
                concept_path = str(entry["concept_path"])
                node["projection_role"] = LEXICAL_ROOT_ROLE
                root_by_path[concept_path] = str(node["id"])
    missing_roots = sorted({str(record.get("concept_path", "")) for record in records} - set(root_by_path))
    if missing_roots:
        raise GraphifyProjectionError(
            f"Graphify emitted no record root for {len(missing_roots)} records"
        )
    for link in data.get("links", data.get("edges", [])):
        source = str(link.get("source_file", "")).replace("\\", "/")
        source = source.removeprefix("./")
        entry = by_view.get(source)
        if entry:
            link["projection_source_file"] = source
            link["projection_source_location"] = link.get("source_location")
            link["source_file"] = entry["concept_path"]
            link["source_location"] = None
            link["concept_path"] = entry["concept_path"]
            link["record_sha256"] = entry["record_sha256"]
            link["projection"] = "graphify-view"
    links = data.get("links", data.get("edges", []))
    for left, right, similarity in _lexical_similarity_pairs(records):
        source, target = sorted((root_by_path[left], root_by_path[right]))
        links.append(
            {
                "projection": LEXICAL_SIMILARITY_PROJECTION,
                "relation": "lexical-similarity",
                "similarity": similarity,
                "source": source,
                "target": target,
            }
        )
    data = _canonical_graph(data)
    output.write_text(
        json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return data


def graph_logical_sha256(data: Mapping[str, Any]) -> str:
    return sha256_json(_canonical_graph(dict(data)))


def _record_index_digest(entries: Iterable[Mapping[str, Any]]) -> str:
    canonical: list[dict[str, Any]] = []
    for number, item in enumerate(entries):
        if not isinstance(item, Mapping):
            raise GraphifyProjectionError(f"record index entry {number} must be an object")
        if set(item) != set(RECORD_INDEX_FIELDS):
            raise GraphifyProjectionError(
                f"record index entry {number} does not match the closed schema"
            )
        if not all(isinstance(item[field], str) for field in RECORD_INDEX_FIELDS if field != "paper_id"):
            raise GraphifyProjectionError(f"record index entry {number} has a non-string field")
        if item["paper_id"] is not None and not isinstance(item["paper_id"], str):
            raise GraphifyProjectionError(f"record index entry {number} has an invalid paper_id")
        canonical.append({field: item[field] for field in RECORD_INDEX_FIELDS})
    return sha256_json(canonical)


def materialize_graphify_projection(root: Path) -> dict[str, Any]:
    """Create one hash-bound projection without overwriting an existing one."""

    root = root.expanduser().resolve()
    if not root.is_dir():
        raise GraphifyProjectionError(f"bundle directory does not exist: {root}")
    final = root / PROJECTION_RELATIVE_PATH
    if final.exists():
        raise GraphifyProjectionError(f"projection already exists: {final}")
    records = load_records(root)
    core = core_artifacts(root)
    records_path = root / RECORDS_RELATIVE_PATH
    retrieval_root = final.parent
    retrieval_root.mkdir(parents=True, exist_ok=True)
    candidate = Path(tempfile.mkdtemp(prefix=".graphify-candidate-", dir=retrieval_root))
    view_root: Path | None = None
    try:
        view_root, entries = _write_views(root, records)
        graph_path = candidate / "graph.json"
        data = _run_graphify(root, entries, graph_path)
        logical_sha256 = graph_logical_sha256(data)
        index = {
            "authoritative": False,
            "contract": CONTRACT,
            "core": {
                "artifacts": core,
                "records": len(records),
                "records_sha256": sha256_file(records_path),
                "tree_sha256": core_tree_sha256(core),
            },
            "engine": {
                "distribution": GRAPHIFY_DISTRIBUTION,
                "mode": ENGINE_MODE,
                "semantic_llm": False,
                "version": GRAPHIFY_VERSION,
            },
            "graph": {
                "edges": len(data["links"]),
                "logical_sha256": logical_sha256,
                "nodes": len(data["nodes"]),
                "path": "graph.json",
                "sha256": sha256_file(graph_path),
            },
            "record_index_sha256": _record_index_digest(entries),
            "records": entries,
            "schema_version": "1.0",
        }
        (candidate / "index.json").write_text(
            json.dumps(index, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        if view_root is not None:
            _remove_tree_verified(view_root, "temporary Graphify views")
            view_root = None
        if (root / VIEW_ROOT_NAME).exists():
            raise GraphifyProjectionError("temporary Graphify views remain before publication")
        if final.exists():
            raise GraphifyProjectionError(f"projection appeared during build: {final}")
        candidate.replace(final)
        report = validate_graphify_projection(root, require_runtime=True)
        if not report["valid"]:
            raise GraphifyProjectionError("; ".join(report["errors"]))
        return report
    except Exception:
        shutil.rmtree(candidate, ignore_errors=True)
        if final.exists():
            shutil.rmtree(final, ignore_errors=True)
        raise
    finally:
        if view_root is not None:
            _remove_tree_verified(view_root, "temporary Graphify views")


def _load_json_object(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise GraphifyProjectionError(f"cannot read {label}: {exc}") from exc
    if not isinstance(value, dict):
        raise GraphifyProjectionError(f"{label} must contain a JSON object")
    return value


def _safe_bundle_path(root: Path, value: Any, label: str) -> Path:
    if not isinstance(value, str) or not value:
        raise GraphifyProjectionError(f"{label} must be a non-empty relative path")
    pure = PurePosixPath(value)
    if pure.is_absolute() or ".." in pure.parts or "\\" in value:
        raise GraphifyProjectionError(f"{label} is not a safe bundle-relative path")
    path = root / pure
    if not path.is_file() or path.is_symlink():
        raise GraphifyProjectionError(f"{label} does not resolve to a regular file: {value}")
    return path


def validate_graphify_projection(root: Path, *, require_runtime: bool = True) -> dict[str, Any]:
    """Validate runtime pin, closed hashes, graph structure, and record bindings."""

    root = root.expanduser().resolve()
    errors: list[str] = []
    try:
        index = _load_json_object(root / INDEX_RELATIVE_PATH, str(INDEX_RELATIVE_PATH))
        graph = _load_json_object(root / GRAPH_RELATIVE_PATH, str(GRAPH_RELATIVE_PATH))
        records = load_records(root)
        if (root / VIEW_ROOT_NAME).exists():
            errors.append("published bundle contains reserved temporary Graphify views")
        ledger_by_path = {str(record.get("concept_path")): record for record in records}
        concept_documents = _concept_document_paths(root, records)
        if len(ledger_by_path) != len(records):
            errors.append("authoritative ledger contains duplicate concept paths")
        subject_records, subject_views = _record_maps(records)
        expected_by_path = {
            path: _expected_index_entry(record, subject_records, subject_views)
            for path, record in ledger_by_path.items()
        }
        if require_runtime:
            installed = importlib.metadata.version(GRAPHIFY_DISTRIBUTION)
            if installed != GRAPHIFY_VERSION:
                errors.append(
                    f"runtime version mismatch: expected {GRAPHIFY_VERSION}, found {installed}"
                )
        if index.get("contract") != CONTRACT:
            errors.append("unsupported projection contract")
        if index.get("authoritative") is not False:
            errors.append("projection must declare authoritative=false")
        engine = index.get("engine")
        if not isinstance(engine, dict) or engine != {
            "distribution": GRAPHIFY_DISTRIBUTION,
            "mode": ENGINE_MODE,
            "semantic_llm": False,
            "version": GRAPHIFY_VERSION,
        }:
            errors.append("engine metadata does not match the pinned no-LLM contract")
        expected_core = index.get("core")
        actual_core = core_artifacts(root)
        if not isinstance(expected_core, dict):
            errors.append("core metadata is missing")
        else:
            if expected_core.get("artifacts") != actual_core:
                errors.append("authoritative core artifact hashes changed")
            if expected_core.get("tree_sha256") != core_tree_sha256(actual_core):
                errors.append("authoritative core tree digest changed")
            if expected_core.get("records_sha256") != sha256_file(root / RECORDS_RELATIVE_PATH):
                errors.append("record ledger digest changed")
            if expected_core.get("records") != len(records):
                errors.append("record ledger count changed")
        graph_meta = index.get("graph")
        if not isinstance(graph_meta, dict):
            errors.append("graph metadata is missing")
        else:
            if graph_meta.get("sha256") != sha256_file(root / GRAPH_RELATIVE_PATH):
                errors.append("graph file digest changed")
            if graph_meta.get("logical_sha256") != graph_logical_sha256(graph):
                errors.append("graph logical digest changed")
        nodes = graph.get("nodes")
        links = graph.get("links")
        if not isinstance(nodes, list) or not isinstance(links, list):
            raise GraphifyProjectionError("graph must contain nodes and links arrays")
        node_ids: set[str] = set()
        projected_paths: set[str] = set()
        lexical_roots: dict[str, list[str]] = {}
        for number, node in enumerate(nodes):
            if not isinstance(node, dict) or not isinstance(node.get("id"), str) or not node["id"]:
                errors.append(f"node {number} has an invalid id")
                continue
            if node["id"] in node_ids:
                errors.append(f"duplicate node id: {node['id']}")
            node_ids.add(node["id"])
            source = node.get("source_file")
            try:
                _safe_bundle_path(
                    root,
                    concept_documents.get(str(source), source),
                    f"node {node['id']} source_file",
                )
            except GraphifyProjectionError as exc:
                errors.append(str(exc))
            if node.get("projection") == "graphify-view":
                concept_path = str(node.get("concept_path", ""))
                expected = expected_by_path.get(concept_path)
                if expected is None:
                    errors.append(f"projected node references an unknown concept: {concept_path}")
                else:
                    projected_paths.add(concept_path)
                    for field in RECORD_IDENTITY_FIELDS:
                        if node.get(field) != expected[field]:
                            errors.append(
                                f"projected node identity mismatch for {concept_path}: {field}"
                            )
                    if node.get("source_file") != concept_path:
                        errors.append(f"projected node source mismatch for {concept_path}")
                    if node.get("projection_source_file") != expected["view_path"]:
                        errors.append(f"projected node view mismatch for {concept_path}")
                    if node.get("projection_role") == LEXICAL_ROOT_ROLE:
                        lexical_roots.setdefault(concept_path, []).append(node["id"])
                        if node.get("label") != PurePosixPath(expected["view_path"]).name:
                            errors.append(f"record root label mismatch for {concept_path}")
        for concept_path in sorted(ledger_by_path):
            if len(lexical_roots.get(concept_path, [])) != 1:
                errors.append(
                    f"expected exactly one record root for {concept_path}; "
                    f"found {len(lexical_roots.get(concept_path, []))}"
                )
        for number, link in enumerate(links):
            if not isinstance(link, dict):
                errors.append(f"link {number} must be an object")
                continue
            if link.get("source") not in node_ids or link.get("target") not in node_ids:
                errors.append(f"link {number} has a dangling endpoint")
            source_file = link.get("source_file")
            if source_file:
                try:
                    _safe_bundle_path(
                        root,
                        concept_documents.get(str(source_file), source_file),
                        f"link {number} source_file",
                    )
                except GraphifyProjectionError as exc:
                    errors.append(str(exc))
            if link.get("projection") == "graphify-view":
                concept_path = str(link.get("concept_path", ""))
                expected = expected_by_path.get(concept_path)
                if expected is None:
                    errors.append(f"projected link references an unknown concept: {concept_path}")
                else:
                    if link.get("record_sha256") != expected["record_sha256"]:
                        errors.append(f"projected link record mismatch for {concept_path}")
                    if link.get("source_file") != concept_path:
                        errors.append(f"projected link source mismatch for {concept_path}")
                    if link.get("projection_source_file") != expected["view_path"]:
                        errors.append(f"projected link view mismatch for {concept_path}")
        if all(len(lexical_roots.get(path, [])) == 1 for path in ledger_by_path):
            expected_similarity = [
                {
                    "projection": LEXICAL_SIMILARITY_PROJECTION,
                    "relation": "lexical-similarity",
                    "similarity": similarity,
                    "source": min(lexical_roots[left][0], lexical_roots[right][0]),
                    "target": max(lexical_roots[left][0], lexical_roots[right][0]),
                }
                for left, right, similarity in _lexical_similarity_pairs(records)
            ]
            actual_similarity = [
                link for link in links
                if isinstance(link, dict)
                and link.get("projection") == LEXICAL_SIMILARITY_PROJECTION
            ]
            expected_similarity.sort(key=lambda link: (link["source"], link["target"]))
            actual_similarity.sort(key=lambda link: (str(link.get("source")), str(link.get("target"))))
            if actual_similarity != expected_similarity:
                errors.append("lexical similarity projection differs from the ledger")
        if isinstance(graph_meta, dict):
            if graph_meta.get("nodes") != len(nodes) or graph_meta.get("edges") != len(links):
                errors.append("stored graph counts changed")
        indexed = index.get("records")
        if not isinstance(indexed, list):
            errors.append("record index is missing")
            indexed = []
        if index.get("record_index_sha256") != _record_index_digest(indexed):
            errors.append("record index digest changed")
        seen_paths: set[str] = set()
        for entry in indexed:
            if not isinstance(entry, dict):
                errors.append("record index entry must be an object")
                continue
            concept_path = str(entry.get("concept_path", ""))
            ledger = ledger_by_path.get(concept_path)
            if not ledger:
                errors.append(f"record index references an unknown concept: {concept_path}")
                continue
            if concept_path in seen_paths:
                errors.append(f"record index duplicates a concept: {concept_path}")
            seen_paths.add(concept_path)
            expected = expected_by_path[concept_path]
            if entry != expected:
                errors.append(f"record index identity or view digest mismatch for {concept_path}")
            if concept_path not in projected_paths:
                errors.append(f"Graphify has no projected node for {concept_path}")
        if seen_paths != set(ledger_by_path):
            errors.append("Graphify record coverage differs from the authoritative ledger")
        degrees = {node_id: 0 for node_id in node_ids}
        for link in links:
            if isinstance(link, dict) and link.get("source") in degrees and link.get("target") in degrees:
                degrees[str(link["source"])] += 1
                degrees[str(link["target"])] += 1
        orphans = sorted(node_id for node_id, degree in degrees.items() if degree == 0)
        if orphans:
            errors.append(f"graph contains {len(orphans)} orphan nodes")
        return {
            "contract": CONTRACT,
            "errors": sorted(set(errors)),
            "graph": str(root / GRAPH_RELATIVE_PATH),
            "index": str(root / INDEX_RELATIVE_PATH),
            "logical_sha256": graph_logical_sha256(graph),
            "status": "pass" if not errors else "fail",
            "summary": {
                "edges": len(links),
                "nodes": len(nodes),
                "orphans": len(orphans),
                "records": len(records),
            },
            "valid": not errors,
        }
    except (GraphifyProjectionError, importlib.metadata.PackageNotFoundError, OSError, ValueError) as exc:
        errors.append(str(exc))
        return {
            "contract": CONTRACT,
            "errors": sorted(set(errors)),
            "status": "fail",
            "summary": {},
            "valid": False,
        }
