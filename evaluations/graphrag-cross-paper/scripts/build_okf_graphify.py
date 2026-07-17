#!/usr/bin/env python3
"""Build the deterministic OKF v0.1 input bundle for the Graphify benchmark."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
import re
import shutil
import sys
import tempfile
from collections import defaultdict, deque
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Mapping, Sequence
from urllib.parse import unquote, urlsplit

import yaml


BENCHMARK_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PAPERS_PATH = BENCHMARK_ROOT / "papers.json"
DEFAULT_MARKDOWN_DIR = BENCHMARK_ROOT / "sources" / "markdown"
DEFAULT_CLAIMS_DIR = BENCHMARK_ROOT / "sources" / "claims"
DEFAULT_VOCABULARY_PATH = (
    BENCHMARK_ROOT / "sources" / "semantic" / "analysis-vocabulary.jsonl"
)
DEFAULT_OUTPUT = (
    BENCHMARK_ROOT
    / "fixtures"
    / "workspaces"
    / "okf-graphify-overlay"
    / "knowledge"
)

OKF_VERSION = "0.1"
GRAPHIFY_PACKAGE = "graphifyy"
GRAPHIFY_VERSION = "0.9.17"
GRAPHIFY_REQUIREMENT = f"{GRAPHIFY_PACKAGE}=={GRAPHIFY_VERSION}"
QUERY_TOKEN_BUDGET = 1500
QUERY_DEPTH = 2

EXPECTED_DEFAULT = {
    "papers_catalog_sha256": "20870e8021deb2064214c6c63537ce733c3593c608e40ce651b9e901d08ce1a5",
    "vocabulary_sha256": "7436dc26e79ce7f50b4e92db47ff829405e966199cb1f9420c1c3af53bfd2997",
    "core_tree_sha256": "25945882b73ca659230c8b8c66a58fa8418313f8a0233f57e85b0e48445f4328",
    "dataset_tree_sha256": "ab14c14f6471086a320f75350def889ba91f2bbd3b040f81fa4797814ce689ab",
    "papers": 15,
    "claims": 831,
    "dimensions": 13,
    "methods": 15,
    "records": 874,
    "dataset_sources": 31,
}

_SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_PAGE_HEADING = re.compile(r"^## PDF page ([1-9][0-9]*)\s*$", re.MULTILINE)
_EVIDENCE = re.compile(
    r"^sources/markdown/(?P<paper>[A-Za-z0-9._-]+)\.md#PDF-page-(?P<page>[1-9][0-9]*)$"
)
_MARKDOWN_LINK = re.compile(r"(?<!!)\[[^\]\n]+\]\(([^)\n]+)\)")
_HEADING = re.compile(r"^#{1,6}\s+(.+?)\s*#*\s*$", re.MULTILINE)
_FRONTMATTER_PRIORITY = (
    "okf_version",
    "type",
    "title",
    "description",
    "resource",
    "tags",
    "timestamp",
)


class BuildError(RuntimeError):
    """Report invalid inputs, output drift, or a broken generated bundle."""


@dataclass(frozen=True)
class SourceDigest:
    """Describe one immutable source file used by the builder."""

    path: Path
    relative_path: str
    role: str
    records: int
    byte_count: int
    sha256: str
    logical_sha256: str
    paper_id: str | None = None

    def manifest_value(self) -> dict[str, Any]:
        """Return the stable, path-portable manifest representation."""

        value: dict[str, Any] = {
            "bytes": self.byte_count,
            "logical_sha256": self.logical_sha256,
            "path": self.relative_path,
            "records": self.records,
            "role": self.role,
            "sha256": self.sha256,
        }
        if self.paper_id is not None:
            value["paper_id"] = self.paper_id
        return value


@dataclass(frozen=True)
class PaperInput:
    """Represent one catalog entry and its complete page-addressed Markdown source."""

    paper_id: str
    catalog: Mapping[str, Any]
    frontmatter: Mapping[str, Any]
    frontmatter_text: str
    body: str
    source: SourceDigest
    page_count: int


@dataclass(frozen=True)
class TermInput:
    """Represent one reviewed analysis dimension or paper-specific method."""

    identifier: str
    label: str
    definition: str
    term_kind: str
    resource: str
    source: SourceDigest
    source_line: int
    record: Mapping[str, Any]


@dataclass(frozen=True)
class ClaimInput:
    """Represent one reviewed, page-grounded claim and its graph endpoints."""

    identifier: str
    paper_id: str
    dimension_id: str
    method_id: str
    interpretation: str
    evidence: tuple[tuple[int, str], ...]
    resource: str
    source: SourceDigest
    source_line: int
    record: Mapping[str, Any]


@dataclass(frozen=True)
class InputModel:
    """Hold validated immutable inputs for one deterministic bundle build."""

    collection_id: str
    selection_policy: str
    catalog_source: SourceDigest
    papers: tuple[PaperInput, ...]
    claims: tuple[ClaimInput, ...]
    dimensions: tuple[TermInput, ...]
    methods: tuple[TermInput, ...]
    dataset_sources: tuple[SourceDigest, ...]
    core_tree_sha256: str
    dataset_tree_sha256: str


@dataclass(frozen=True)
class _SourceBlob:
    path: Path
    relative_path: str
    role: str
    data: bytes
    paper_id: str | None = None

    @property
    def sha256(self) -> str:
        return _sha256_bytes(self.data)

    @property
    def logical_sha256(self) -> str:
        return _sha256_bytes(_logical_bytes(self.data))

    def digest(self, records: int) -> SourceDigest:
        return SourceDigest(
            path=self.path,
            relative_path=self.relative_path,
            role=self.role,
            records=records,
            byte_count=len(self.data),
            sha256=self.sha256,
            logical_sha256=self.logical_sha256,
            paper_id=self.paper_id,
        )


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _logical_bytes(value: bytes) -> bytes:
    if b"\x00" in value:
        return value
    return value.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _pretty_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode(
        "utf-8"
    )


def _tree_digest(entries: Iterable[SourceDigest]) -> str:
    members = [
        {"path": entry.relative_path, "sha256": entry.logical_sha256}
        for entry in sorted(entries, key=lambda item: item.relative_path)
    ]
    return _sha256_bytes(_canonical_json(members).encode("utf-8"))


def _artifact_tree_digest(artifacts: Mapping[str, bytes]) -> str:
    members = [
        {"path": path, "sha256": _sha256_bytes(_logical_bytes(data))}
        for path, data in sorted(artifacts.items())
    ]
    return _sha256_bytes(_canonical_json(members).encode("utf-8"))


def _decode(blob: _SourceBlob, label: str) -> str:
    try:
        return _logical_bytes(blob.data).decode("utf-8")
    except UnicodeDecodeError as exc:
        raise BuildError(f"{label} is not valid UTF-8: {blob.relative_path}: {exc}") from exc


def _json_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise BuildError(f"Duplicate JSON key: {key!r}")
        result[key] = value
    return result


def _parse_json_object(blob: _SourceBlob, label: str) -> dict[str, Any]:
    try:
        value = json.loads(_decode(blob, label), object_pairs_hook=_json_pairs)
    except json.JSONDecodeError as exc:
        raise BuildError(f"Invalid {label} JSON at {blob.relative_path}: {exc}") from exc
    if not isinstance(value, dict):
        raise BuildError(f"{label} must be a JSON object: {blob.relative_path}")
    return value


def _parse_jsonl(blob: _SourceBlob, label: str) -> list[tuple[int, dict[str, Any]]]:
    records: list[tuple[int, dict[str, Any]]] = []
    for number, line in enumerate(_decode(blob, label).splitlines(), start=1):
        if not line.strip():
            continue
        try:
            value = json.loads(line, object_pairs_hook=_json_pairs)
        except json.JSONDecodeError as exc:
            raise BuildError(
                f"Invalid {label} JSON on line {number} of {blob.relative_path}: {exc}"
            ) from exc
        if not isinstance(value, dict):
            raise BuildError(
                f"{label} line {number} of {blob.relative_path} must be a JSON object."
            )
        records.append((number, value))
    if not records:
        raise BuildError(f"{label} contains no records: {blob.relative_path}")
    return records


def _required_string(record: Mapping[str, Any], key: str, label: str) -> str:
    value = record.get(key)
    if not isinstance(value, str) or not value.strip():
        raise BuildError(f"{label} requires a non-empty string field {key!r}.")
    return value.strip()


def _safe_identifier(value: str, label: str) -> str:
    if not _SAFE_ID.fullmatch(value):
        raise BuildError(f"{label} has an unsafe identifier: {value!r}")
    return value


def _read_blob(path: Path, relative_path: str, role: str, paper_id: str | None = None) -> _SourceBlob:
    try:
        data = path.read_bytes()
    except OSError as exc:
        raise BuildError(f"Cannot read required input {path}: {exc}") from exc
    return _SourceBlob(path.resolve(), relative_path, role, data, paper_id)


def _split_frontmatter(text: str, label: str) -> tuple[dict[str, Any], str, str]:
    if not text.startswith("---\n"):
        raise BuildError(f"{label} must begin with YAML frontmatter.")
    end = text.find("\n---\n", 4)
    if end < 0:
        raise BuildError(f"{label} has unterminated YAML frontmatter.")
    raw_frontmatter = text[4:end]
    try:
        frontmatter = yaml.safe_load(raw_frontmatter)
    except yaml.YAMLError as exc:
        raise BuildError(f"{label} has invalid YAML frontmatter: {exc}") from exc
    if not isinstance(frontmatter, dict):
        raise BuildError(f"{label} frontmatter must be a mapping.")
    body = text[end + len("\n---\n") :]
    if body.startswith("\n"):
        body = body[1:]
    return frontmatter, raw_frontmatter, body


def _term_id_from_iri(value: str, label: str) -> str:
    parsed = urlsplit(value)
    if parsed.scheme not in {"http", "https"} or not parsed.path:
        raise BuildError(f"{label} must be an absolute HTTP(S) IRI: {value!r}")
    identifier = unquote(parsed.path.rsplit("/", 1)[-1])
    return _safe_identifier(identifier, label)


def _claim_resource(paper_iri: str, claim_id: str) -> str:
    prefix, marker, _ = paper_iri.partition("/resource/")
    if not marker or not prefix:
        raise BuildError(f"Claim paper_iri does not expose a resource namespace: {paper_iri!r}")
    return f"{prefix}/resource/{claim_id}"


def _graph_paper_id(paper_id: str) -> str:
    return paper_id.replace(".", "-")


def _method_id(paper_id: str) -> str:
    return f"method-{_graph_paper_id(paper_id)}"


def _default_inputs_selected(
    papers_path: Path,
    markdown_dir: Path,
    claims_dir: Path,
    vocabulary_path: Path,
) -> bool:
    return all(
        actual.resolve() == expected.resolve()
        for actual, expected in (
            (papers_path, DEFAULT_PAPERS_PATH),
            (markdown_dir, DEFAULT_MARKDOWN_DIR),
            (claims_dir, DEFAULT_CLAIMS_DIR),
            (vocabulary_path, DEFAULT_VOCABULARY_PATH),
        )
    )


def _load_catalog(blob: _SourceBlob) -> tuple[str, str, dict[str, dict[str, Any]]]:
    catalog = _parse_json_object(blob, "papers catalog")
    collection_id = _required_string(catalog, "collection_id", "papers catalog")
    selection_policy = _required_string(catalog, "selection_policy", "papers catalog")
    rows = catalog.get("papers")
    if not isinstance(rows, list) or not rows:
        raise BuildError("papers catalog requires a non-empty papers array.")
    papers: dict[str, dict[str, Any]] = {}
    for index, value in enumerate(rows, start=1):
        label = f"papers catalog row {index}"
        if not isinstance(value, dict):
            raise BuildError(f"{label} must be an object.")
        arxiv_id = _required_string(value, "arxiv_id", label)
        version = _required_string(value, "version", label)
        paper_id = _safe_identifier(f"{arxiv_id}{version}", label)
        if not re.fullmatch(r"[0-9]{4}\.[0-9]{5}", arxiv_id) or not re.fullmatch(
            r"v[1-9][0-9]*", version
        ):
            raise BuildError(f"{label} has invalid arXiv identity fields.")
        if paper_id in papers:
            raise BuildError(f"Duplicate paper id in catalog: {paper_id}")
        for key in ("title", "abs_url", "pdf_url", "selection_dimension"):
            _required_string(value, key, label)
        authors = value.get("authors")
        if not isinstance(authors, list) or not authors or any(
            not isinstance(author, str) or not author.strip() for author in authors
        ):
            raise BuildError(f"{label} requires a non-empty authors string array.")
        year = value.get("year")
        if isinstance(year, bool) or not isinstance(year, int) or year < 1900:
            raise BuildError(f"{label} has an invalid publication year.")
        pdf_sha256 = _required_string(value, "pdf_sha256", label)
        if not _SHA256.fullmatch(pdf_sha256):
            raise BuildError(f"{label} has an invalid pdf_sha256.")
        if value["abs_url"] != f"https://arxiv.org/abs/{paper_id}":
            raise BuildError(f"{label} abs_url does not match the pinned paper id.")
        if value["pdf_url"] != f"https://arxiv.org/pdf/{paper_id}":
            raise BuildError(f"{label} pdf_url does not match the pinned paper id.")
        papers[paper_id] = dict(value)
    return collection_id, selection_policy, papers


def _load_terms(blob: _SourceBlob) -> tuple[dict[str, dict[str, Any]], dict[str, int]]:
    terms: dict[str, dict[str, Any]] = {}
    lines: dict[str, int] = {}
    for line, record in _parse_jsonl(blob, "analysis vocabulary"):
        label = f"analysis vocabulary line {line}"
        identifier = _safe_identifier(_required_string(record, "id", label), label)
        if identifier in terms:
            raise BuildError(f"Duplicate analysis vocabulary id: {identifier}")
        for key in ("label", "definition", "term_kind"):
            _required_string(record, key, label)
        if record["term_kind"] not in {"analysis-dimension", "paper-specific-method"}:
            raise BuildError(f"{label} has an unsupported term_kind: {record['term_kind']!r}")
        terms[identifier] = dict(record)
        lines[identifier] = line
    return terms, lines


def _load_paper_source(
    blob: _SourceBlob,
    catalog: Mapping[str, Any],
) -> PaperInput:
    paper_id = blob.paper_id or ""
    text = _decode(blob, f"paper Markdown {paper_id}")
    frontmatter, raw_frontmatter, body = _split_frontmatter(text, f"paper Markdown {paper_id}")
    label = f"paper Markdown {paper_id}"
    if _required_string(frontmatter, "paper_id", label) != paper_id:
        raise BuildError(f"{label} paper_id does not match its filename.")
    if _required_string(frontmatter, "type", label) != "Paper":
        raise BuildError(f"{label} must have type 'Paper'.")
    expected_fields = {
        "title": catalog["title"],
        "resource": catalog["abs_url"],
        "source_url": catalog["abs_url"],
        "pdf_url": catalog["pdf_url"],
        "pdf_sha256": catalog["pdf_sha256"],
    }
    for key, expected in expected_fields.items():
        if frontmatter.get(key) != expected:
            raise BuildError(f"{label} field {key!r} does not match papers.json.")
    tags = frontmatter.get("tags")
    if not isinstance(tags, (str, list)) or not tags:
        raise BuildError(f"{label} requires non-empty tags.")
    page_count = frontmatter.get("page_count")
    if isinstance(page_count, bool) or not isinstance(page_count, int) or page_count < 1:
        raise BuildError(f"{label} requires a positive integer page_count.")
    pages = [int(value) for value in _PAGE_HEADING.findall(body)]
    if pages != list(range(1, page_count + 1)):
        raise BuildError(
            f"{label} must preserve one ordered page heading for every page; "
            f"expected 1..{page_count}, observed {pages[:5]}{'...' if len(pages) > 5 else ''}."
        )
    if f"# {catalog['title']}" not in body.splitlines():
        raise BuildError(f"{label} does not preserve the catalog title as its H1 heading.")
    digest = blob.digest(records=1)
    return PaperInput(
        paper_id=paper_id,
        catalog=dict(catalog),
        frontmatter=dict(frontmatter),
        frontmatter_text=raw_frontmatter,
        body=body,
        source=digest,
        page_count=page_count,
    )


def _load_claims(
    blobs: Sequence[_SourceBlob],
    papers: Mapping[str, PaperInput],
    terms: Mapping[str, Mapping[str, Any]],
) -> tuple[tuple[ClaimInput, ...], dict[str, set[str]], dict[str, int]]:
    claims: list[ClaimInput] = []
    identifiers: set[str] = set()
    term_resources: dict[str, set[str]] = defaultdict(set)
    record_counts: dict[str, int] = {}
    for blob in blobs:
        paper_id = blob.paper_id or ""
        paper = papers[paper_id]
        parsed = _parse_jsonl(blob, f"claims for {paper_id}")
        record_counts[blob.relative_path] = len(parsed)
        source = blob.digest(records=len(parsed))
        for line, record in parsed:
            label = f"claim line {line} of {blob.relative_path}"
            for key in (
                "id",
                "title",
                "interpretation",
                "claim_kind",
                "claim_origin",
                "confidence",
                "evidence_locator",
                "paper_iri",
                "pdf_sha256",
                "review_state",
                "subject_term_iri",
                "object_term_iri",
            ):
                _required_string(record, key, label)
            identifier = _safe_identifier(str(record["id"]), label)
            claim_paper_id = _graph_paper_id(paper_id)
            if not identifier.startswith(f"claim-{claim_paper_id}-"):
                raise BuildError(f"{label} id does not match its paper source.")
            if identifier in identifiers:
                raise BuildError(f"Duplicate claim id: {identifier}")
            identifiers.add(identifier)
            if record["pdf_sha256"] != paper.catalog["pdf_sha256"]:
                raise BuildError(f"{label} pdf_sha256 does not match the paper catalog.")
            if _graph_paper_id(paper_id) not in record["paper_iri"]:
                raise BuildError(f"{label} paper_iri does not identify {paper_id}.")
            dimension_id = _term_id_from_iri(str(record["object_term_iri"]), label)
            method_id = _term_id_from_iri(str(record["subject_term_iri"]), label)
            if dimension_id not in terms or terms[dimension_id].get("term_kind") != "analysis-dimension":
                raise BuildError(f"{label} references unknown analysis dimension {dimension_id!r}.")
            if method_id not in terms or terms[method_id].get("term_kind") != "paper-specific-method":
                raise BuildError(f"{label} references unknown paper method {method_id!r}.")
            if method_id != _method_id(paper_id):
                raise BuildError(f"{label} method does not match the claim paper.")
            term_resources[dimension_id].add(str(record["object_term_iri"]))
            term_resources[method_id].add(str(record["subject_term_iri"]))
            evidence: list[tuple[int, str]] = []
            for locator in str(record["evidence_locator"]).split(";"):
                match = _EVIDENCE.fullmatch(locator)
                if match is None or match.group("paper") != paper_id:
                    raise BuildError(f"{label} has an invalid evidence locator: {locator!r}")
                page = int(match.group("page"))
                if page > paper.page_count:
                    raise BuildError(f"{label} evidence page {page} exceeds the paper page count.")
                evidence.append((page, locator))
            if not evidence or len(evidence) != len(set(evidence)):
                raise BuildError(f"{label} requires unique page evidence locators.")
            claims.append(
                ClaimInput(
                    identifier=identifier,
                    paper_id=paper_id,
                    dimension_id=dimension_id,
                    method_id=method_id,
                    interpretation=str(record["interpretation"]),
                    evidence=tuple(evidence),
                    resource=_claim_resource(str(record["paper_iri"]), identifier),
                    source=source,
                    source_line=line,
                    record=dict(record),
                )
            )
    return tuple(sorted(claims, key=lambda item: item.identifier)), term_resources, record_counts


def _make_terms(
    records: Mapping[str, Mapping[str, Any]],
    lines: Mapping[str, int],
    resources: Mapping[str, set[str]],
    source: SourceDigest,
    paper_ids: set[str],
) -> tuple[tuple[TermInput, ...], tuple[TermInput, ...]]:
    dimensions: list[TermInput] = []
    methods: list[TermInput] = []
    for identifier in sorted(records):
        record = records[identifier]
        resource_values = resources.get(identifier, set())
        if len(resource_values) != 1:
            raise BuildError(
                f"Analysis term {identifier!r} must have exactly one claim-derived resource IRI; "
                f"observed {sorted(resource_values)}."
            )
        term = TermInput(
            identifier=identifier,
            label=str(record["label"]),
            definition=str(record["definition"]),
            term_kind=str(record["term_kind"]),
            resource=next(iter(resource_values)),
            source=source,
            source_line=lines[identifier],
            record=dict(record),
        )
        if term.term_kind == "analysis-dimension":
            dimensions.append(term)
        else:
            methods.append(term)
    expected_method_ids = {_method_id(paper_id) for paper_id in paper_ids}
    observed_method_ids = {item.identifier for item in methods}
    if observed_method_ids != expected_method_ids:
        raise BuildError(
            "Paper-specific methods must have a one-to-one mapping with papers; "
            f"missing={sorted(expected_method_ids - observed_method_ids)}, "
            f"extra={sorted(observed_method_ids - expected_method_ids)}."
        )
    if not dimensions:
        raise BuildError("Analysis vocabulary must define at least one analysis dimension.")
    return tuple(dimensions), tuple(methods)


def _validate_default_pins(model: InputModel) -> None:
    actual = {
        "papers_catalog_sha256": model.catalog_source.logical_sha256,
        "vocabulary_sha256": next(
            item.logical_sha256 for item in model.dataset_sources if item.role == "analysis-vocabulary"
        ),
        "core_tree_sha256": model.core_tree_sha256,
        "dataset_tree_sha256": model.dataset_tree_sha256,
        "papers": len(model.papers),
        "claims": len(model.claims),
        "dimensions": len(model.dimensions),
        "methods": len(model.methods),
        "records": len(model.papers) + len(model.claims) + len(model.dimensions) + len(model.methods),
        "dataset_sources": len(model.dataset_sources),
    }
    mismatches = [
        f"{key}: expected {expected!r}, observed {actual.get(key)!r}"
        for key, expected in EXPECTED_DEFAULT.items()
        if actual.get(key) != expected
    ]
    if mismatches:
        raise BuildError("Pinned GraphRAG inputs drifted:\n- " + "\n- ".join(mismatches))


def load_inputs(
    papers_path: Path = DEFAULT_PAPERS_PATH,
    markdown_dir: Path = DEFAULT_MARKDOWN_DIR,
    claims_dir: Path = DEFAULT_CLAIMS_DIR,
    vocabulary_path: Path = DEFAULT_VOCABULARY_PATH,
    *,
    enforce_default_pins: bool = False,
) -> InputModel:
    """Load and validate the catalog, papers, claims, vocabulary, counts, and digests."""

    papers_path = Path(papers_path)
    markdown_dir = Path(markdown_dir)
    claims_dir = Path(claims_dir)
    vocabulary_path = Path(vocabulary_path)
    if not markdown_dir.is_dir() or not claims_dir.is_dir():
        raise BuildError("Markdown and claims inputs must be existing directories.")
    markdown_paths = sorted(markdown_dir.glob("*.md"), key=lambda path: path.name)
    claims_paths = sorted(claims_dir.glob("*.jsonl"), key=lambda path: path.name)
    if not markdown_paths or not claims_paths:
        raise BuildError("Markdown and claims directories must both contain input files.")

    catalog_blob = _read_blob(papers_path, "papers.json", "papers-catalog")
    vocabulary_blob = _read_blob(
        vocabulary_path,
        "sources/semantic/analysis-vocabulary.jsonl",
        "analysis-vocabulary",
    )
    markdown_blobs = [
        _read_blob(
            path,
            f"sources/markdown/{path.name}",
            "paper-markdown",
            path.stem,
        )
        for path in markdown_paths
    ]
    claim_blobs = [
        _read_blob(
            path,
            f"sources/claims/{path.name}",
            "reviewed-claims",
            path.stem,
        )
        for path in claims_paths
    ]

    collection_id, selection_policy, catalog = _load_catalog(catalog_blob)
    paper_ids = set(catalog)
    markdown_ids = {blob.paper_id for blob in markdown_blobs}
    claim_ids = {blob.paper_id for blob in claim_blobs}
    if len(markdown_ids) != len(markdown_blobs) or len(claim_ids) != len(claim_blobs):
        raise BuildError("Input filenames must map to unique paper ids.")
    if markdown_ids != paper_ids or claim_ids != paper_ids:
        raise BuildError(
            "Catalog, Markdown, and claim files must cover the same paper ids; "
            f"missing_markdown={sorted(paper_ids - markdown_ids)}, "
            f"extra_markdown={sorted(markdown_ids - paper_ids)}, "
            f"missing_claims={sorted(paper_ids - claim_ids)}, "
            f"extra_claims={sorted(claim_ids - paper_ids)}."
        )

    paper_map = {
        blob.paper_id or "": _load_paper_source(blob, catalog[blob.paper_id or ""])
        for blob in markdown_blobs
    }
    term_records, term_lines = _load_terms(vocabulary_blob)
    claims, term_resources, claim_record_counts = _load_claims(
        claim_blobs, paper_map, term_records
    )
    vocabulary_source = vocabulary_blob.digest(records=len(term_records))
    dimensions, methods = _make_terms(
        term_records,
        term_lines,
        term_resources,
        vocabulary_source,
        paper_ids,
    )

    markdown_sources = tuple(paper_map[paper_id].source for paper_id in sorted(paper_map))
    claim_sources = tuple(
        blob.digest(records=claim_record_counts[blob.relative_path]) for blob in claim_blobs
    )
    dataset_sources = tuple(
        sorted((*markdown_sources, *claim_sources, vocabulary_source), key=lambda item: item.relative_path)
    )
    core_sources = tuple(item for item in dataset_sources if item.role != "analysis-vocabulary")
    model = InputModel(
        collection_id=collection_id,
        selection_policy=selection_policy,
        catalog_source=catalog_blob.digest(records=len(catalog)),
        papers=tuple(paper_map[paper_id] for paper_id in sorted(paper_map)),
        claims=claims,
        dimensions=dimensions,
        methods=methods,
        dataset_sources=dataset_sources,
        core_tree_sha256=_tree_digest(core_sources),
        dataset_tree_sha256=_tree_digest(dataset_sources),
    )
    if enforce_default_pins:
        _validate_default_pins(model)
    return model


def _normalize_yaml_value(value: Any, label: str) -> Any:
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise BuildError(f"{label} contains a non-finite YAML number.")
        return value
    if isinstance(value, (dt.date, dt.datetime)):
        return value.isoformat()
    if isinstance(value, (list, tuple)):
        return [_normalize_yaml_value(item, label) for item in value]
    if isinstance(value, dict):
        normalized: dict[str, Any] = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise BuildError(f"{label} contains a non-string mapping key.")
            normalized[key] = _normalize_yaml_value(item, label)
        return normalized
    raise BuildError(f"{label} contains an unsupported YAML value: {type(value).__name__}")


def _render_frontmatter(frontmatter: Mapping[str, Any]) -> str:
    normalized = _normalize_yaml_value(dict(frontmatter), "generated frontmatter")
    keys = [key for key in _FRONTMATTER_PRIORITY if key in normalized]
    keys.extend(sorted(set(normalized) - set(keys)))
    lines = [
        f"{key}: {json.dumps(normalized[key], ensure_ascii=False, sort_keys=True, separators=(',', ':'))}"
        for key in keys
    ]
    return "---\n" + "\n".join(lines) + "\n---\n"


def _render_document(frontmatter: Mapping[str, Any], body: str) -> bytes:
    if not body.endswith("\n"):
        body += "\n"
    return (_render_frontmatter(frontmatter) + "\n" + body).encode("utf-8")


def _single_line(value: str) -> str:
    return " ".join(value.split())


def _link_label(value: str) -> str:
    return _single_line(value).replace("[", "(").replace("]", ")")


def _render_index(model: InputModel, claims_by_paper: Mapping[str, list[ClaimInput]]) -> bytes:
    frontmatter = {
        "okf_version": OKF_VERSION,
        "title": "GraphRAG Cross-Paper OKF and Graphify Knowledge",
        "description": (
            "A deterministic OKF v0.1 projection of fifteen page-addressed papers, "
            "reviewed claims, analysis dimensions, and paper-specific methods."
        ),
    }
    lines = [
        "# GraphRAG Cross-Paper OKF and Graphify Knowledge",
        "",
        "This bundle is the deterministic Markdown input to the separately orchestrated Graphify update. "
        "No semantic LLM was used to build it.",
        "",
        "## Papers",
        "",
    ]
    for paper in model.papers:
        lines.append(
            f"- [{_link_label(str(paper.catalog['title']))}](papers/{paper.paper_id}.md) "
            f"— {len(claims_by_paper[paper.paper_id])} reviewed claims"
        )
    lines.extend(["", "## Analysis dimensions", ""])
    for term in model.dimensions:
        lines.append(f"- [{_link_label(term.label)}](dimensions/{term.identifier}.md)")
    lines.extend(["", "## Paper-specific methods", ""])
    for term in model.methods:
        lines.append(f"- [{_link_label(term.label)}](methods/{term.identifier}.md)")
    return _render_document(frontmatter, "\n".join(lines))


def _render_paper(
    model: InputModel,
    paper: PaperInput,
    method: TermInput,
    claims: Sequence[ClaimInput],
) -> bytes:
    original_frontmatter = _normalize_yaml_value(dict(paper.frontmatter), "paper frontmatter")
    frontmatter = dict(original_frontmatter)
    frontmatter.update(
        {
            "collection_id": model.collection_id,
            "source_path": paper.source.relative_path,
            "source_sha256": paper.source.sha256,
            "source_logical_sha256": paper.source.logical_sha256,
            "source_frontmatter_sha256": _sha256_bytes(
                paper.frontmatter_text.encode("utf-8")
            ),
            "source_frontmatter": original_frontmatter,
        }
    )
    relationships = [
        "## Knowledge graph relationships",
        "",
        f"- Paper-specific method: [{_link_label(method.label)}](../methods/{method.identifier}.md)",
        f"- Reviewed claims: {len(claims)}",
        "",
        "### Reviewed claims",
        "",
    ]
    relationships.extend(
        f"- [{claim.identifier}](../claims/{paper.paper_id}/{claim.identifier}.md)"
        for claim in claims
    )
    body = paper.body
    if not body.endswith("\n"):
        body += "\n"
    body += "\n" + "\n".join(relationships) + "\n"
    return _render_document(frontmatter, body)


def _render_claim(
    claim: ClaimInput,
    paper: PaperInput,
    dimension: TermInput,
    method: TermInput,
) -> bytes:
    original_record = _normalize_yaml_value(dict(claim.record), "claim record")
    frontmatter = dict(original_record)
    frontmatter.update(
        {
            "type": "PaperSemanticClaim",
            "description": claim.interpretation,
            "resource": claim.resource,
            "tags": ["graphrag", "reviewed-claim", str(claim.record["claim_kind"]), claim.paper_id],
            "claim_id": claim.identifier,
            "paper_id": claim.paper_id,
            "dimension_id": claim.dimension_id,
            "method_id": claim.method_id,
            "source_path": claim.source.relative_path,
            "source_line": claim.source_line,
            "source_sha256": claim.source.sha256,
            "source_record": original_record,
        }
    )
    lines = [
        f"# {claim.identifier}: {_single_line(claim.interpretation)}",
        "",
        "## Interpretation",
        "",
        claim.interpretation,
        "",
        "## Relationships",
        "",
        f"- Paper: [{_link_label(str(paper.catalog['title']))}](../../papers/{paper.paper_id}.md)",
        f"- Analysis dimension: [{_link_label(dimension.label)}](../../dimensions/{dimension.identifier}.md)",
        f"- Paper-specific method: [{_link_label(method.label)}](../../methods/{method.identifier}.md)",
        "",
        "## Page-grounded evidence",
        "",
    ]
    lines.extend(
        f"- [PDF page {page}](../../papers/{paper.paper_id}.md#PDF-page-{page}) — `{locator}`"
        for page, locator in claim.evidence
    )
    lines.extend(
        [
            "",
            "## Provenance",
            "",
            f"- Review state: `{claim.record['review_state']}`",
            f"- Confidence: `{claim.record['confidence']}`",
            f"- Claim origin: `{claim.record['claim_origin']}`",
            f"- Source record: `{claim.source.relative_path}:{claim.source_line}`",
        ]
    )
    return _render_document(frontmatter, "\n".join(lines))


def _render_dimension(
    term: TermInput,
    claims: Sequence[ClaimInput],
    methods: Mapping[str, TermInput],
) -> bytes:
    original_record = _normalize_yaml_value(dict(term.record), "dimension record")
    frontmatter = {
        **original_record,
        "type": "AnalysisDimension",
        "title": term.label,
        "description": term.definition,
        "resource": term.resource,
        "tags": ["graphrag", "analysis-dimension", term.identifier],
        "term_id": term.identifier,
        "source_path": term.source.relative_path,
        "source_line": term.source_line,
        "source_sha256": term.source.sha256,
        "source_record": original_record,
    }
    lines = [
        f"# {term.label}",
        "",
        term.definition,
        "",
        "## Reviewed claims",
        "",
    ]
    lines.extend(
        f"- [{claim.identifier}](../claims/{claim.paper_id}/{claim.identifier}.md) — "
        f"[{_link_label(methods[claim.method_id].label)}](../methods/{claim.method_id}.md)"
        for claim in claims
    )
    return _render_document(frontmatter, "\n".join(lines))


def _render_method(
    term: TermInput,
    paper: PaperInput,
    claims: Sequence[ClaimInput],
    dimensions: Mapping[str, TermInput],
) -> bytes:
    original_record = _normalize_yaml_value(dict(term.record), "method record")
    frontmatter = {
        **original_record,
        "type": "PaperSpecificMethod",
        "title": term.label,
        "description": term.definition,
        "resource": term.resource,
        "tags": ["graphrag", "paper-specific-method", paper.paper_id],
        "term_id": term.identifier,
        "paper_id": paper.paper_id,
        "source_path": term.source.relative_path,
        "source_line": term.source_line,
        "source_sha256": term.source.sha256,
        "source_record": original_record,
    }
    lines = [
        f"# {term.label}",
        "",
        term.definition,
        "",
        "## Paper",
        "",
        f"- [{_link_label(str(paper.catalog['title']))}](../papers/{paper.paper_id}.md)",
        "",
        "## Reviewed claims",
        "",
    ]
    lines.extend(
        f"- [{claim.identifier}](../claims/{claim.paper_id}/{claim.identifier}.md) — "
        f"[{_link_label(dimensions[claim.dimension_id].label)}](../dimensions/{claim.dimension_id}.md)"
        for claim in claims
    )
    return _render_document(frontmatter, "\n".join(lines))


def build_artifacts(model: InputModel) -> dict[str, bytes]:
    """Render every OKF Markdown concept deterministically in memory."""

    papers = {item.paper_id: item for item in model.papers}
    dimensions = {item.identifier: item for item in model.dimensions}
    methods = {item.identifier: item for item in model.methods}
    claims_by_paper: dict[str, list[ClaimInput]] = defaultdict(list)
    claims_by_dimension: dict[str, list[ClaimInput]] = defaultdict(list)
    claims_by_method: dict[str, list[ClaimInput]] = defaultdict(list)
    for claim in model.claims:
        claims_by_paper[claim.paper_id].append(claim)
        claims_by_dimension[claim.dimension_id].append(claim)
        claims_by_method[claim.method_id].append(claim)
    for collection in (*claims_by_paper.values(), *claims_by_dimension.values(), *claims_by_method.values()):
        collection.sort(key=lambda item: item.identifier)

    artifacts: dict[str, bytes] = {"index.md": _render_index(model, claims_by_paper)}
    for paper in model.papers:
        method = methods[_method_id(paper.paper_id)]
        artifacts[f"papers/{paper.paper_id}.md"] = _render_paper(
            model, paper, method, claims_by_paper[paper.paper_id]
        )
    for claim in model.claims:
        artifacts[f"claims/{claim.paper_id}/{claim.identifier}.md"] = _render_claim(
            claim,
            papers[claim.paper_id],
            dimensions[claim.dimension_id],
            methods[claim.method_id],
        )
    for term in model.dimensions:
        artifacts[f"dimensions/{term.identifier}.md"] = _render_dimension(
            term, claims_by_dimension[term.identifier], methods
        )
    for term in model.methods:
        paper_id = next(
            paper.paper_id for paper in model.papers if _method_id(paper.paper_id) == term.identifier
        )
        artifacts[f"methods/{term.identifier}.md"] = _render_method(
            term, papers[paper_id], claims_by_method[term.identifier], dimensions
        )
    return dict(sorted(artifacts.items()))


def _tags_present(value: Any) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, list):
        return bool(value) and all(isinstance(item, str) and item.strip() for item in value)
    return False


def _heading_slugs(text: str) -> set[str]:
    slugs: set[str] = set()
    for heading in _HEADING.findall(text):
        slug = re.sub(r"[^\w\- ]", "", heading, flags=re.UNICODE).strip().replace(" ", "-")
        if slug:
            slugs.add(slug.casefold())
    return slugs


def _local_target(source_path: str, href: str) -> tuple[str, str | None] | None:
    href = href.strip()
    if href.startswith("<") and href.endswith(">"):
        href = href[1:-1]
    parsed = urlsplit(href)
    if parsed.scheme or parsed.netloc or (not parsed.path and parsed.fragment):
        return None
    raw_path = unquote(parsed.path)
    if not raw_path:
        return None
    parts: list[str] = []
    initial = PurePosixPath(raw_path.lstrip("/")) if raw_path.startswith("/") else PurePosixPath(source_path).parent / raw_path
    for part in initial.parts:
        if part in {"", "."}:
            continue
        if part == "..":
            if not parts:
                raise BuildError(f"Local link escapes the bundle: {source_path} -> {href}")
            parts.pop()
        else:
            parts.append(part)
    if not parts:
        raise BuildError(f"Local link has no target: {source_path} -> {href}")
    return PurePosixPath(*parts).as_posix(), unquote(parsed.fragment) or None


def validate_artifacts(artifacts: Mapping[str, bytes]) -> dict[str, Any]:
    """Validate OKF frontmatter, local links, fragments, reachability, and orphans."""

    if "index.md" not in artifacts:
        raise BuildError("Generated bundle is missing index.md.")
    if any(not path.endswith(".md") for path in artifacts):
        raise BuildError("Concept artifact validation accepts Markdown files only.")
    texts: dict[str, str] = {}
    frontmatters: dict[str, dict[str, Any]] = {}
    bodies: dict[str, str] = {}
    expected_types = {
        "papers": "Paper",
        "claims": "PaperSemanticClaim",
        "dimensions": "AnalysisDimension",
        "methods": "PaperSpecificMethod",
    }
    for path, data in artifacts.items():
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise BuildError(f"Generated artifact is not UTF-8: {path}") from exc
        frontmatter, _, body = _split_frontmatter(text, path)
        texts[path] = text
        frontmatters[path] = frontmatter
        bodies[path] = body
        if path == "index.md":
            if frontmatter.get("okf_version") != OKF_VERSION:
                raise BuildError("index.md must declare okf_version '0.1'.")
            continue
        top = PurePosixPath(path).parts[0]
        expected_type = expected_types.get(top)
        if expected_type is None or frontmatter.get("type") != expected_type:
            raise BuildError(f"{path} has an invalid or unexpected OKF type.")
        for key in ("title", "description", "resource"):
            if not isinstance(frontmatter.get(key), str) or not str(frontmatter[key]).strip():
                raise BuildError(f"{path} requires non-empty {key!r} frontmatter.")
        if not _tags_present(frontmatter.get("tags")):
            raise BuildError(f"{path} requires non-empty tags frontmatter.")
        if top == "claims":
            first_heading = next(iter(_HEADING.findall(body)), "")
            description = _single_line(str(frontmatter["description"]))
            if description not in _single_line(first_heading):
                raise BuildError(f"{path} H1 label must include its claim interpretation.")

    edges: dict[str, set[str]] = {path: set() for path in artifacts}
    incoming: dict[str, set[str]] = {path: set() for path in artifacts}
    link_count = 0
    for source_path, text in texts.items():
        for href in _MARKDOWN_LINK.findall(text):
            target_value = _local_target(source_path, href)
            if target_value is None:
                continue
            target_path, fragment = target_value
            if target_path not in artifacts:
                raise BuildError(f"Broken local link: {source_path} -> {href}")
            if fragment and fragment.casefold() not in _heading_slugs(texts[target_path]):
                raise BuildError(f"Broken local fragment: {source_path} -> {href}")
            edges[source_path].add(target_path)
            incoming[target_path].add(source_path)
            link_count += 1

    orphaned = sorted(
        path
        for path in artifacts
        if path != "index.md" and not edges[path] and not incoming[path]
    )
    if orphaned:
        raise BuildError(f"Generated concepts are orphaned: {orphaned[:10]}")
    reachable = {"index.md"}
    queue: deque[str] = deque(["index.md"])
    while queue:
        source = queue.popleft()
        for target in sorted(edges[source]):
            if target not in reachable:
                reachable.add(target)
                queue.append(target)
    missing = sorted(set(artifacts) - reachable)
    if missing:
        raise BuildError(f"Generated concepts are not reachable from index.md: {missing[:10]}")
    return {
        "broken_local_links": 0,
        "concepts_reachable_from_index": len(reachable) - 1,
        "local_links": link_count,
        "markdown_files": len(artifacts),
        "orphans": 0,
        "status": "pass",
    }


def _build_manifest(
    model: InputModel,
    artifacts: Mapping[str, bytes],
    validation: Mapping[str, Any],
) -> dict[str, Any]:
    concept_count = len(model.papers) + len(model.claims) + len(model.dimensions) + len(model.methods)
    sources = [entry.manifest_value() for entry in model.dataset_sources]
    return {
        "schema_version": "1.0",
        "builder": {
            "deterministic": True,
            "name": "graphrag-okf-graphify",
            "semantic_llm": False,
            "version": "1.0",
        },
        "okf": {"version": OKF_VERSION},
        "graphify": {
            "builder_invoked": False,
            "orchestration_command": "graphify update . --no-cluster",
            "package": GRAPHIFY_PACKAGE,
            "requirement": GRAPHIFY_REQUIREMENT,
            "semantic_llm": False,
            "version": GRAPHIFY_VERSION,
            "query": {
                "depth": QUERY_DEPTH,
                "token_budget": QUERY_TOKEN_BUDGET,
                "traversal": "bfs",
            },
        },
        "inputs": {
            "catalog": model.catalog_source.manifest_value(),
            "core_source_count": len([item for item in model.dataset_sources if item.role != "analysis-vocabulary"]),
            "core_tree_sha256": model.core_tree_sha256,
            "dataset_record_count": concept_count,
            "dataset_source_count": len(model.dataset_sources),
            "dataset_tree_sha256": model.dataset_tree_sha256,
            "hash_contract": (
                "sha256(canonical JSON array of path and LF-normalized logical-file sha256 "
                "objects sorted by path)"
            ),
            "sources": sources,
        },
        "counts": {
            "claims": len(model.claims),
            "concepts": concept_count,
            "dimensions": len(model.dimensions),
            "index_files": 1,
            "markdown_files": len(artifacts),
            "methods": len(model.methods),
            "papers": len(model.papers),
        },
        "bundle": {
            "build_manifest_excluded_from_tree_digest": True,
            "bundle_tree_sha256": _artifact_tree_digest(artifacts),
            "file_count": len(artifacts),
            "total_bytes": sum(len(value) for value in artifacts.values()),
            "tree_contract": (
                "All generated Markdown files; build-manifest.json is excluded to avoid "
                "a self-referential digest."
            ),
        },
        "validation": {
            **dict(validation),
            "deterministic_rebuild": "pass",
            "input_counts_and_digests": "pass",
        },
    }


def _ensure_inputs_unchanged(model: InputModel) -> None:
    for source in (model.catalog_source, *model.dataset_sources):
        try:
            data = source.path.read_bytes()
        except OSError as exc:
            raise BuildError(f"Input disappeared during build: {source.path}: {exc}") from exc
        observed = (len(data), _sha256_bytes(data), _sha256_bytes(_logical_bytes(data)))
        expected = (source.byte_count, source.sha256, source.logical_sha256)
        if observed != expected:
            raise BuildError(f"Input changed during build: {source.relative_path}")


def _safe_artifact_path(root: Path, relative: str) -> Path:
    candidate = PurePosixPath(relative)
    if candidate.is_absolute() or not candidate.parts or any(
        part in {"", ".", ".."} for part in candidate.parts
    ):
        raise BuildError(f"Unsafe generated artifact path: {relative!r}")
    return root.joinpath(*candidate.parts)


def write_or_check(artifacts: Mapping[str, bytes], output: Path, *, check: bool) -> None:
    """Write a complete replacement tree or verify byte-for-byte output drift."""

    output = Path(output).resolve()
    if output == output.parent:
        raise BuildError("Refusing to use a filesystem root as the generated output.")
    expected_paths = set(artifacts)
    if check:
        if not output.is_dir():
            raise BuildError(f"Generated output is missing: {output}")
        actual_paths = {
            path.relative_to(output).as_posix() for path in output.rglob("*") if path.is_file()
        }
        missing = sorted(expected_paths - actual_paths)
        extra = sorted(actual_paths - expected_paths)
        changed = sorted(
            relative
            for relative in expected_paths & actual_paths
            if _safe_artifact_path(output, relative).read_bytes() != artifacts[relative]
        )
        if missing or extra or changed:
            raise BuildError(
                "Generated OKF Graphify bundle drifted: "
                f"missing={missing[:5]}, extra={extra[:5]}, changed={changed[:5]}"
            )
        return

    output.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=f".{output.name}-", dir=output.parent))
    try:
        for relative, data in sorted(artifacts.items()):
            target = _safe_artifact_path(stage, relative)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        if output.is_symlink() or output.is_file():
            output.unlink()
        elif output.exists():
            shutil.rmtree(output)
        stage.replace(output)
    except Exception:
        if stage.exists():
            shutil.rmtree(stage, ignore_errors=True)
        raise


def build_bundle(
    output: Path = DEFAULT_OUTPUT,
    *,
    papers_path: Path = DEFAULT_PAPERS_PATH,
    markdown_dir: Path = DEFAULT_MARKDOWN_DIR,
    claims_dir: Path = DEFAULT_CLAIMS_DIR,
    vocabulary_path: Path = DEFAULT_VOCABULARY_PATH,
    check: bool = False,
    enforce_default_pins: bool | None = None,
) -> dict[str, Any]:
    """Build or check the graph-ready OKF bundle and return its stable manifest."""

    if enforce_default_pins is None:
        enforce_default_pins = _default_inputs_selected(
            Path(papers_path), Path(markdown_dir), Path(claims_dir), Path(vocabulary_path)
        )
    model = load_inputs(
        Path(papers_path),
        Path(markdown_dir),
        Path(claims_dir),
        Path(vocabulary_path),
        enforce_default_pins=enforce_default_pins,
    )
    first = build_artifacts(model)
    second = build_artifacts(model)
    if first != second:
        raise BuildError("The in-memory bundle rebuild was not deterministic.")
    validation = validate_artifacts(first)
    manifest = _build_manifest(model, first, validation)
    manifest_bytes = _pretty_json(manifest)
    if manifest_bytes != _pretty_json(_build_manifest(model, second, validation)):
        raise BuildError("The build manifest was not deterministic.")
    _ensure_inputs_unchanged(model)
    complete = dict(first)
    complete["build-manifest.json"] = manifest_bytes
    write_or_check(complete, Path(output), check=check)
    return manifest


def _argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Build a deterministic OKF v0.1 bundle for the GraphRAG Graphify benchmark. "
            "Graphify itself is intentionally not invoked."
        )
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Generated knowledge directory (default: {DEFAULT_OUTPUT}).",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Verify the generated tree byte-for-byte without writing files.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the command-line builder and return a conventional process status."""

    args = _argument_parser().parse_args(argv)
    try:
        manifest = build_bundle(args.output, check=args.check)
    except (BuildError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    result = {
        "bundle_tree_sha256": manifest["bundle"]["bundle_tree_sha256"],
        "counts": manifest["counts"],
        "output": str(args.output.resolve()),
        "status": "checked" if args.check else "written",
    }
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
