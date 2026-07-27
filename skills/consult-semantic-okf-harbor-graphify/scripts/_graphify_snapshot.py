"""Read-only validation and querying for a Semantic OKF Graphify snapshot."""

from __future__ import annotations

import hashlib
import importlib
import importlib.metadata
import json
import math
import posixpath
import re
from collections import Counter
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Mapping


CONTRACT = "semantic-okf-graphify/1.0"
GRAPHIFY_VERSION = "0.9.17"
PROJECTION = PurePosixPath("retrieval/graphify")
INDEX_PATH = PROJECTION / "index.json"
GRAPH_PATH = PROJECTION / "graph.json"
RECORDS_PATH = PurePosixPath("semantic/records.jsonl")
VIEW_ROOT_NAME = ".graphify-views"
HEX_RE = re.compile(r"^[0-9a-f]{64}$")
RECORD_DIGEST_FIELDS = (
    "source_id",
    "source_kind",
    "source_path",
    "record_id",
    "subject_iri",
    "ontology_class_iri",
    "concept_type",
    "title",
    "body",
    "attributes",
)
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


class SnapshotError(RuntimeError):
    """A classified invalid-snapshot or read-only query failure."""


def canonical_json(value: Any) -> str:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
    )


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _is_projection(relative: str) -> bool:
    path = PurePosixPath(relative)
    return path == PROJECTION or PROJECTION in path.parents


def _artifacts(root: Path, *, include_projection: bool) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for path in sorted(
        (candidate for candidate in root.rglob("*") if candidate.is_file()),
        key=lambda candidate: candidate.relative_to(root).as_posix(),
    ):
        relative = path.relative_to(root).as_posix()
        if not include_projection and _is_projection(relative):
            continue
        if path.is_symlink():
            raise SnapshotError(f"symlink is not allowed in a published snapshot: {relative}")
        result.append(
            {"path": relative, "bytes": path.stat().st_size, "sha256": sha256_file(path)}
        )
    return result


def snapshot_sha256(root: Path) -> str:
    return sha256_json(_artifacts(root, include_projection=True))


def _load_object(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise SnapshotError(f"cannot read {label}: {exc}") from exc
    if not isinstance(value, dict):
        raise SnapshotError(f"{label} must contain a JSON object")
    return value


def _load_records(root: Path) -> list[dict[str, Any]]:
    try:
        lines = (root / RECORDS_PATH).read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        raise SnapshotError(f"cannot read {RECORDS_PATH}: {exc}") from exc
    records: list[dict[str, Any]] = []
    for number, line in enumerate(lines, 1):
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise SnapshotError(f"invalid JSON at {RECORDS_PATH}:{number}: {exc}") from exc
        if not isinstance(value, dict):
            raise SnapshotError(f"record at {RECORDS_PATH}:{number} must be an object")
        records.append(value)
    if not records:
        raise SnapshotError("record ledger is empty")
    return records


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
    return f"{hashlib.sha256(identity.encode('utf-8')).hexdigest()[:24]}.md"


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
    match = re.search(r"(?:^|[-/])(\d{4}\.\d{5}v\d+)(?:$|[-/])", str(record.get("source_id", "")))
    return match.group(1) if match else None


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
    lines.extend((f"- [Authoritative concept]({posixpath.relpath(concept_path, start=view_parent)})", ""))
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
        "view_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
    }


def _record_digest(record: Mapping[str, Any]) -> str:
    try:
        payload = {field: record[field] for field in RECORD_DIGEST_FIELDS}
    except KeyError as exc:
        raise SnapshotError(f"authoritative record omits digest field: {exc.args[0]}") from exc
    return sha256_json(payload)


def _canonical_graph(data: Mapping[str, Any]) -> dict[str, Any]:
    graph = dict(data)
    graph.pop("built_at_commit", None)
    nodes = graph.get("nodes")
    links = graph.get("links", graph.get("edges"))
    hyperedges = graph.get("hyperedges", [])
    if not isinstance(nodes, list) or not isinstance(links, list) or not isinstance(hyperedges, list):
        raise SnapshotError("graph must contain nodes, links, and hyperedges arrays")
    for label, values in (("node", nodes), ("link", links), ("hyperedge", hyperedges)):
        if any(not isinstance(item, dict) for item in values):
            raise SnapshotError(f"graph contains a non-object {label}")
    graph.pop("edges", None)
    graph["nodes"] = sorted(nodes, key=lambda item: str(item.get("id", "")))
    graph["links"] = sorted(
        links,
        key=lambda item: (
            str(item.get("source", "")),
            str(item.get("target", "")),
            str(item.get("relation", "")),
            str(item.get("source_file", "")),
            str(item.get("source_location", "")),
        ),
    )
    graph["hyperedges"] = sorted(hyperedges, key=lambda item: str(item.get("id", "")))
    return graph


def _record_index_digest(entries: Iterable[Mapping[str, Any]]) -> str:
    canonical: list[dict[str, Any]] = []
    for number, item in enumerate(entries):
        if not isinstance(item, Mapping):
            raise SnapshotError(f"record index entry {number} must be an object")
        if set(item) != set(RECORD_INDEX_FIELDS):
            raise SnapshotError(f"record index entry {number} does not match the closed schema")
        if not all(isinstance(item[field], str) for field in RECORD_INDEX_FIELDS if field != "paper_id"):
            raise SnapshotError(f"record index entry {number} has a non-string field")
        if item["paper_id"] is not None and not isinstance(item["paper_id"], str):
            raise SnapshotError(f"record index entry {number} has an invalid paper_id")
        canonical.append({field: item[field] for field in RECORD_INDEX_FIELDS})
    return sha256_json(canonical)


def _safe_file(root: Path, relative: Any, label: str) -> Path:
    if not isinstance(relative, str) or not relative:
        raise SnapshotError(f"{label} must be a non-empty path")
    path = PurePosixPath(relative)
    if path.is_absolute() or ".." in path.parts or "\\" in relative:
        raise SnapshotError(f"{label} must be a safe bundle-relative path")
    candidate = root / path
    if not candidate.is_file() or candidate.is_symlink():
        raise SnapshotError(f"{label} is not a regular bundle file: {relative}")
    return candidate


class Snapshot:
    """One fully verified immutable Semantic OKF + Graphify release."""

    def __init__(self, root: Path) -> None:
        self.root = root.expanduser().resolve()
        if not self.root.is_dir():
            raise SnapshotError(f"snapshot directory does not exist: {self.root}")
        self.index = _load_object(self.root / INDEX_PATH, str(INDEX_PATH))
        self.graph_data = _load_object(self.root / GRAPH_PATH, str(GRAPH_PATH))
        self.records = _load_records(self.root)
        self.records_by_path = {
            str(record.get("concept_path")): record for record in self.records
        }
        self.subject_records, self.subject_views = _record_maps(self.records)
        self.expected_by_path = {
            path: _expected_index_entry(record, self.subject_records, self.subject_views)
            for path, record in self.records_by_path.items()
        }
        self._validate()

    def _validate(self) -> None:
        errors: list[str] = []
        try:
            found = importlib.metadata.version("graphifyy")
        except importlib.metadata.PackageNotFoundError as exc:
            raise SnapshotError("graphifyy is not installed") from exc
        if found != GRAPHIFY_VERSION:
            errors.append(f"runtime version mismatch: expected {GRAPHIFY_VERSION}, found {found}")
        if (self.root / VIEW_ROOT_NAME).exists():
            errors.append("published snapshot contains reserved temporary Graphify views")
        if len(self.records_by_path) != len(self.records):
            errors.append("authoritative ledger contains duplicate concept paths")
        for path, record in self.records_by_path.items():
            try:
                if record.get("record_sha256") != _record_digest(record):
                    errors.append(f"authoritative record digest mismatch for {path}")
            except SnapshotError as exc:
                errors.append(str(exc))
        if self.index.get("contract") != CONTRACT:
            errors.append("unsupported projection contract")
        if self.index.get("authoritative") is not False:
            errors.append("projection must declare authoritative=false")
        if self.index.get("engine") != {
            "distribution": "graphifyy",
            "mode": "markdown-structural-no-llm",
            "semantic_llm": False,
            "version": GRAPHIFY_VERSION,
        }:
            errors.append("engine metadata differs from the pinned no-LLM contract")
        core = self.index.get("core")
        actual_core = _artifacts(self.root, include_projection=False)
        if not isinstance(core, dict):
            errors.append("core metadata is missing")
        else:
            if core.get("artifacts") != actual_core:
                errors.append("authoritative core artifact hashes changed")
            if core.get("tree_sha256") != sha256_json(actual_core):
                errors.append("authoritative core tree digest changed")
            if core.get("records_sha256") != sha256_file(self.root / RECORDS_PATH):
                errors.append("record ledger digest changed")
            if core.get("records") != len(self.records):
                errors.append("record ledger count changed")
        graph_meta = self.index.get("graph")
        canonical_graph = _canonical_graph(self.graph_data)
        if not isinstance(graph_meta, dict):
            errors.append("graph metadata is missing")
        else:
            if graph_meta.get("sha256") != sha256_file(self.root / GRAPH_PATH):
                errors.append("graph file digest changed")
            if graph_meta.get("logical_sha256") != sha256_json(canonical_graph):
                errors.append("graph logical digest changed")
        nodes = canonical_graph["nodes"]
        links = canonical_graph["links"]
        node_ids: set[str] = set()
        projected_paths: set[str] = set()
        for number, node in enumerate(nodes):
            if not isinstance(node, dict) or not isinstance(node.get("id"), str) or not node["id"]:
                errors.append(f"node {number} has an invalid id")
                continue
            if node["id"] in node_ids:
                errors.append(f"duplicate node id: {node['id']}")
            node_ids.add(node["id"])
            try:
                _safe_file(self.root, node.get("source_file"), f"node {node['id']} source_file")
            except SnapshotError as exc:
                errors.append(str(exc))
            if node.get("projection") == "graphify-view":
                concept_path = str(node.get("concept_path", ""))
                expected = self.expected_by_path.get(concept_path)
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
        degree = Counter({node_id: 0 for node_id in node_ids})
        for number, link in enumerate(links):
            if not isinstance(link, dict):
                errors.append(f"link {number} must be an object")
                continue
            if link.get("source") not in node_ids or link.get("target") not in node_ids:
                errors.append(f"link {number} has a dangling endpoint")
                continue
            degree[str(link["source"])] += 1
            degree[str(link["target"])] += 1
            if link.get("source_file"):
                try:
                    _safe_file(self.root, link["source_file"], f"link {number} source_file")
                except SnapshotError as exc:
                    errors.append(str(exc))
            if link.get("projection") == "graphify-view":
                concept_path = str(link.get("concept_path", ""))
                expected = self.expected_by_path.get(concept_path)
                if expected is None:
                    errors.append(f"projected link references an unknown concept: {concept_path}")
                else:
                    if link.get("record_sha256") != expected["record_sha256"]:
                        errors.append(f"projected link record mismatch for {concept_path}")
                    if link.get("source_file") != concept_path:
                        errors.append(f"projected link source mismatch for {concept_path}")
                    if link.get("projection_source_file") != expected["view_path"]:
                        errors.append(f"projected link view mismatch for {concept_path}")
        if any(value == 0 for value in degree.values()):
            errors.append("graph contains orphan nodes")
        if isinstance(graph_meta, dict) and (
            graph_meta.get("nodes") != len(nodes) or graph_meta.get("edges") != len(links)
        ):
            errors.append("stored graph counts changed")
        entries = self.index.get("records")
        if not isinstance(entries, list):
            errors.append("record index is missing")
            entries = []
        if self.index.get("record_index_sha256") != _record_index_digest(entries):
            errors.append("record index digest changed")
        seen: set[str] = set()
        for entry in entries:
            if not isinstance(entry, dict):
                errors.append("record index entry must be an object")
                continue
            path = str(entry.get("concept_path", ""))
            ledger = self.records_by_path.get(path)
            if not ledger:
                errors.append(f"record index references an unknown concept: {path}")
                continue
            if path in seen:
                errors.append(f"record index duplicates a concept: {path}")
            seen.add(path)
            if entry != self.expected_by_path[path]:
                errors.append(f"record index identity or view digest mismatch for {path}")
            if path not in projected_paths:
                errors.append(f"Graphify has no projected node for {path}")
        if seen != set(self.records_by_path):
            errors.append("Graphify record coverage differs from the ledger")
        if errors:
            raise SnapshotError("; ".join(sorted(set(errors))))

    def verify(self) -> dict[str, Any]:
        return {
            "authoritative": False,
            "contract": CONTRACT,
            "core_tree_sha256": self.index["core"]["tree_sha256"],
            "graph_logical_sha256": self.index["graph"]["logical_sha256"],
            "records": len(self.records),
            "status": "pass",
            "summary": {
                "edges": self.index["graph"]["edges"],
                "nodes": self.index["graph"]["nodes"],
                "records": len(self.records),
                "sources": len({str(record.get("source_id")) for record in self.records}),
            },
        }

    def _concept_payload(self, record: Mapping[str, Any], *, show_content: bool) -> dict[str, Any]:
        concept_path = str(record["concept_path"])
        concept = _safe_file(self.root, concept_path, "concept_path")
        concept_sha256 = sha256_file(concept)
        payload = {
            "attributes": record.get("attributes", {}),
            "concept_id": record.get("concept_id"),
            "concept_path": concept_path,
            "concept_sha256": concept_sha256,
            "concept_type": record.get("concept_type"),
            "evidence": {
                "kind": "concept-file",
                "path": concept_path,
                "sha256": concept_sha256,
            },
            "paper_id": _paper_id(record, self.subject_records),
            "record_id": record.get("record_id"),
            "record_sha256": record.get("record_sha256"),
            "source_id": record.get("source_id"),
            "source_path": record.get("source_path"),
            "title": record.get("title"),
        }
        if show_content:
            payload["content"] = concept.read_text(encoding="utf-8")
        return payload

    def exact(
        self, source_id: str, record_id: str, *, show_content: bool = False
    ) -> dict[str, Any]:
        matches = [
            record
            for record in self.records
            if record.get("source_id") == source_id and record.get("record_id") == record_id
        ]
        return {
            "authority": str(RECORDS_PATH),
            "records": [self._concept_payload(record, show_content=show_content) for record in matches],
            "returned": len(matches),
        }

    def aggregate(self) -> dict[str, Any]:
        counts = Counter(
            (str(record.get("source_id")), str(record.get("concept_type")))
            for record in self.records
        )
        return {
            "authority": str(RECORDS_PATH),
            "groups": [
                {"source_id": source, "concept_type": kind, "records": count}
                for (source, kind), count in sorted(counts.items())
            ],
        }

    def read(self, concept_path: str) -> dict[str, Any]:
        record = self.records_by_path.get(concept_path)
        if not record:
            raise SnapshotError(f"concept_path is not in the ledger: {concept_path}")
        return self._concept_payload(record, show_content=True)

    def search(
        self,
        question: str,
        *,
        depth: int = 2,
        top_k: int = 10,
        show_content: bool = False,
    ) -> dict[str, Any]:
        if not question.strip():
            raise SnapshotError("question must not be blank")
        if not 0 <= depth <= 6:
            raise SnapshotError("depth must be between 0 and 6")
        if not 1 <= top_k <= 100:
            raise SnapshotError("top_k must be between 1 and 100")
        json_graph = importlib.import_module("networkx.readwrite.json_graph")
        serve = importlib.import_module("graphify.serve")
        try:
            graph = json_graph.node_link_graph(self.graph_data, edges="links")
        except TypeError:
            graph = json_graph.node_link_graph(self.graph_data)
        terms = serve._query_terms(question)
        scores = serve._score_query(graph, terms, collect_per_term_seeds=True)
        seeds = serve._pick_seeds(
            scores.ranked,
            G=graph,
            best_seed_by_term=scores.best_seed_by_term,
        )
        visited, traversed_edges = serve._bfs(graph, seeds, depth) if seeds else (set(), [])
        score_by_node = {node_id: score for score, node_id in scores.ranked}
        distance = {node_id: 0 for node_id in seeds}
        frontier = set(seeds)
        for level in range(1, depth + 1):
            next_frontier: set[str] = set()
            for node_id in sorted(frontier, key=str):
                for neighbor in sorted(graph.neighbors(node_id), key=str):
                    if neighbor not in distance:
                        distance[neighbor] = level
                        next_frontier.add(neighbor)
            frontier = next_frontier
        candidates = sorted(
            (
                node_id
                for node_id in visited
                if graph.nodes[node_id].get("concept_path") in self.records_by_path
            ),
            key=lambda node_id: (
                -float(score_by_node.get(node_id, 0.0)),
                int(distance.get(node_id, depth + 1)),
                str(graph.nodes[node_id].get("label", "")),
                str(node_id),
            ),
        )
        results: list[dict[str, Any]] = []
        seen_paths: set[str] = set()
        for node_id in candidates:
            node = graph.nodes[node_id]
            path = str(node["concept_path"])
            if path in seen_paths:
                continue
            seen_paths.add(path)
            record = self.records_by_path[path]
            item = self._concept_payload(record, show_content=show_content)
            item.update(
                {
                    "distance": int(distance.get(node_id, depth + 1)),
                    "graphify_label": node.get("label"),
                    "graphify_node_id": node_id,
                    "graphify_score": float(score_by_node.get(node_id, 0.0)),
                }
            )
            results.append(item)
            if len(results) >= top_k:
                break
        context_nodes = [
            {
                "distance": int(distance.get(node_id, depth + 1)),
                "label": str(graph.nodes[node_id].get("label", "")),
                "node_id": str(node_id),
                "score": float(score_by_node.get(node_id, 0.0)),
            }
            for node_id in sorted(
                visited,
                key=lambda item: (
                    int(distance.get(item, depth + 1)),
                    str(graph.nodes[item].get("label", "")),
                    str(item),
                ),
            )[:100]
        ]
        return {
            "authority": "authoritative concept Markdown hydrated after Graphify discovery",
            "context_nodes": context_nodes,
            "depth": depth,
            "engine": {"distribution": "graphifyy", "version": GRAPHIFY_VERSION},
            "fallback": None,
            "question": question,
            "records": results,
            "returned": len(results),
            "seeds": seeds,
            "traversed_edges": len(traversed_edges),
            "visited_nodes": len(visited),
        }
