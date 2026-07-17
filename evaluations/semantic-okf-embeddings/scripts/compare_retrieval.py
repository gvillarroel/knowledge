#!/usr/bin/env python3
"""Compare legacy lexical retrieval with embedding-aware Semantic OKF routes."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import statistics
import subprocess
import sys
import time
from collections import Counter
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Callable, Iterable, Sequence


METRIC_CUTOFFS = (1, 3, 5, 10)
CORE_KEY_ARTIFACTS = (
    "semantic/records.jsonl",
    "semantic/source-manifest.json",
    "semantic/ontology.ttl",
    "semantic/data.ttl",
    "semantic/shapes.ttl",
    "semantic/provenance.ttl",
    "semantic/validation-report.ttl",
)
BUNDLE_KEY_ARTIFACTS = (
    "semantic/build-report.json",
    "semantic/source-manifest.json",
    "semantic/records.jsonl",
    "semantic/data.ttl",
    "semantic/ontology.ttl",
    "semantic/provenance.ttl",
    "semantic/shapes.ttl",
    "semantic/validation-report.ttl",
    "retrieval/index.json",
    "retrieval/chunks.jsonl",
    "retrieval/embeddings.jsonl",
    "retrieval/build-report.json",
)
TOKEN_RE = re.compile(r"[a-z0-9]+", re.IGNORECASE)
PAPER_ID_RE = re.compile(r"(?<!\d)(\d{4})[.-](\d{5}v\d+)(?!\d)", re.IGNORECASE)
STOPWORDS = {
    "about",
    "across",
    "after",
    "also",
    "among",
    "and",
    "are",
    "before",
    "between",
    "compare",
    "does",
    "each",
    "explain",
    "for",
    "from",
    "graph",
    "graphrag",
    "how",
    "into",
    "methods",
    "papers",
    "retrieval",
    "system",
    "systems",
    "that",
    "the",
    "their",
    "these",
    "they",
    "this",
    "what",
    "when",
    "which",
    "with",
}


class ComparisonError(RuntimeError):
    """Describe an invalid fixture, bundle, query response, or comparison run."""


@dataclass(frozen=True)
class RetrievalQuestion:
    """One retrieval query and its reviewed paper- and source-level qrels."""

    identifier: str
    question: str
    paper_ids: tuple[str, ...]
    source_ids: tuple[str, ...]


@dataclass(frozen=True)
class RetrievalHit:
    """One normalized ranked hit returned by either retrieval implementation."""

    source_id: str | None
    paper_id: str | None
    chunk_id: str | None
    ordinal: int | None
    concept_path: str | None
    concept_id: str | None
    record_id: str | None
    record_sha256: str | None
    source_path: str | None
    locator: dict[str, Any] | None
    text: str | None
    text_sha256: str | None
    score: float | None


def canonical_json(value: Any) -> str:
    """Serialize JSON deterministically for logical-tree hashing."""

    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_bytes(value: bytes) -> str:
    """Return a lowercase SHA-256 digest for bytes."""

    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    """Return a lowercase SHA-256 digest for one physical file."""

    return sha256_bytes(path.read_bytes())


def logical_file_sha256(path: Path) -> str:
    """Hash a file after normalizing text line endings in the repository convention."""

    content = path.read_bytes()
    if b"\x00" not in content:
        content = content.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return sha256_bytes(content)


def _safe_relative_path(value: str) -> PurePosixPath:
    candidate = PurePosixPath(value.replace("\\", "/"))
    if candidate.is_absolute() or not candidate.parts or any(part in {"", ".", ".."} for part in candidate.parts):
        raise ComparisonError(f"Unsafe relative path: {value!r}")
    return candidate


def _local_file(root: Path, relative: str) -> Path:
    candidate = _safe_relative_path(relative)
    resolved_root = root.resolve()
    resolved = resolved_root.joinpath(*candidate.parts).resolve()
    try:
        resolved.relative_to(resolved_root)
    except ValueError as exc:
        raise ComparisonError(f"Path escapes its declared root: {relative!r}") from exc
    return resolved


def logical_tree_sha256(root: Path, relative_paths: Iterable[str] | None = None) -> str:
    """Hash a logical file tree by sorted relative path and LF-normalized file digest."""

    root = root.resolve()
    if relative_paths is None:
        members = [path for path in root.rglob("*") if path.is_file()]
        pairs = [(path.relative_to(root).as_posix(), path) for path in members]
    else:
        pairs = [(str(_safe_relative_path(relative)), _local_file(root, relative)) for relative in relative_paths]
    entries: list[dict[str, str]] = []
    for relative, path in sorted(pairs, key=lambda item: item[0]):
        if not path.is_file():
            raise ComparisonError(f"Tree member is missing or not a file: {relative}")
        entries.append({"path": relative, "sha256": logical_file_sha256(path)})
    return sha256_bytes(canonical_json(entries).encode("utf-8"))


def _load_json_object(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ComparisonError(f"Cannot read {label} at {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ComparisonError(f"{label} must be a JSON object: {path}")
    return value


def load_inventory(path: Path) -> dict[str, Any]:
    """Load and minimally validate the immutable 30-file input inventory."""

    value = _load_json_object(path, "input inventory")
    files = value.get("files")
    if not isinstance(files, list) or not files:
        raise ComparisonError("Input inventory must contain a non-empty files array.")
    paths = [item.get("path") for item in files if isinstance(item, dict)]
    if len(paths) != len(files) or any(not isinstance(path, str) for path in paths):
        raise ComparisonError("Every inventory entry must contain a string path.")
    if len(set(paths)) != len(paths):
        raise ComparisonError("Input inventory contains duplicate paths.")
    return value


def load_questions(path: Path) -> list[RetrievalQuestion]:
    """Load retrieval questions and reject incomplete, duplicate, or unsorted qrels."""

    questions: list[RetrievalQuestion] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        raise ComparisonError(f"Cannot read retrieval questions at {path}: {exc}") from exc
    for number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ComparisonError(f"Invalid questions JSONL line {number}: {exc}") from exc
        if not isinstance(value, dict) or not isinstance(value.get("qrels"), dict):
            raise ComparisonError(f"Question line {number} must contain an object qrels field.")
        identifier = value.get("id")
        question = value.get("question")
        papers = value["qrels"].get("paper_ids")
        sources = value["qrels"].get("source_ids")
        if not isinstance(identifier, str) or not identifier or not isinstance(question, str) or not question:
            raise ComparisonError(f"Question line {number} has an invalid id or question.")
        if not isinstance(papers, list) or not papers or not all(isinstance(item, str) for item in papers):
            raise ComparisonError(f"Question line {number} has invalid paper qrels.")
        if not isinstance(sources, list) or not sources or not all(isinstance(item, str) for item in sources):
            raise ComparisonError(f"Question line {number} has invalid source qrels.")
        if papers != sorted(set(papers)) or sources != sorted(set(sources)):
            raise ComparisonError(f"Question line {number} qrels must be sorted and unique.")
        questions.append(RetrievalQuestion(identifier, question, tuple(papers), tuple(sources)))
    if not questions or len({item.identifier for item in questions}) != len(questions):
        raise ComparisonError("Retrieval questions must be non-empty and have unique ids.")
    return questions


def _logical_rows(path: Path, kind: str) -> int:
    if kind == "markdown":
        return 1
    if kind == "jsonl":
        return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())
    raise ComparisonError(f"Unsupported inventory kind: {kind!r}")


def _verify_inventory_entry(root: Path, entry: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    relative = entry.get("path")
    if not isinstance(relative, str):
        return ["inventory entry has no string path"]
    try:
        path = _local_file(root, relative)
    except ComparisonError as exc:
        return [str(exc)]
    if not path.is_file():
        return [f"missing file: {relative}"]
    if path.stat().st_size != entry.get("bytes"):
        errors.append(f"byte count mismatch: {relative}")
    if sha256_file(path) != entry.get("sha256"):
        errors.append(f"sha256 mismatch: {relative}")
    if "kind" in entry or "rows" in entry:
        try:
            rows = _logical_rows(path, str(entry.get("kind")))
        except (OSError, UnicodeError, ComparisonError) as exc:
            errors.append(f"row check failed for {relative}: {exc}")
        else:
            if rows != entry.get("rows"):
                errors.append(f"row count mismatch: {relative}")
    return errors


def verify_input_inventory(root: Path, inventory: dict[str, Any]) -> dict[str, Any]:
    """Verify all 30 core inputs, the required vocabulary, manifest, and tree digests."""

    root = root.resolve()
    files = inventory["files"]
    errors: list[str] = []
    verified_core_files = 0
    for entry in files:
        if not isinstance(entry, dict):
            errors.append("inventory contains a non-object file entry")
            continue
        entry_errors = _verify_inventory_entry(root, entry)
        errors.extend(entry_errors)
        if not entry_errors:
            verified_core_files += 1
    paths = [str(entry["path"]) for entry in files if isinstance(entry, dict) and isinstance(entry.get("path"), str)]
    actual_tree: str | None = None
    try:
        actual_tree = logical_tree_sha256(root, paths)
    except ComparisonError as exc:
        errors.append(str(exc))
    if actual_tree != inventory.get("core_tree_sha256"):
        errors.append("core logical-tree sha256 mismatch")
    if len(files) != inventory.get("core_file_count"):
        errors.append("inventory core_file_count is internally inconsistent")
    if sum(int(entry.get("bytes", 0)) for entry in files if isinstance(entry, dict)) != inventory.get("core_total_bytes"):
        errors.append("inventory core_total_bytes is internally inconsistent")
    if sum(int(entry.get("rows", 0)) for entry in files if isinstance(entry, dict)) != inventory.get("core_record_count"):
        errors.append("inventory core_record_count is internally inconsistent")

    auxiliary = inventory.get("required_auxiliary")
    auxiliary_entry = auxiliary.get("file") if isinstance(auxiliary, dict) else None
    manifest_entry = auxiliary.get("manifest") if isinstance(auxiliary, dict) else None
    if not isinstance(auxiliary_entry, dict) or not isinstance(manifest_entry, dict):
        errors.append("required_auxiliary must declare file and manifest objects")
    else:
        errors.extend(_verify_inventory_entry(root, auxiliary_entry))
        errors.extend(_verify_inventory_entry(root, manifest_entry))
        if auxiliary.get("real_build_input_count") != len(files) + 1:
            errors.append("required_auxiliary real_build_input_count is internally inconsistent")
        expected_records = inventory.get("core_record_count", 0) + auxiliary_entry.get("rows", 0)
        if auxiliary.get("real_build_record_count") != expected_records:
            errors.append("required_auxiliary real_build_record_count is internally inconsistent")
        try:
            all_paths = [*paths, str(auxiliary_entry["path"])]
            real_tree = logical_tree_sha256(root, all_paths)
        except (ComparisonError, KeyError) as exc:
            real_tree = None
            errors.append(f"cannot hash real build inputs: {exc}")
        if real_tree != auxiliary.get("real_build_inputs_tree_sha256"):
            errors.append("real 31-input logical-tree sha256 mismatch")
    return {
        "status": "pass" if not errors else "fail",
        "expected_core_files": inventory.get("core_file_count"),
        "verified_core_files": verified_core_files,
        "expected_core_tree_sha256": inventory.get("core_tree_sha256"),
        "actual_core_tree_sha256": actual_tree,
        "errors": errors,
    }


def _deduplicate(values: Iterable[str | None]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value is not None and value not in seen:
            seen.add(value)
            result.append(value)
    return result


def recall_at_k(ranked_ids: Sequence[str], relevant_ids: set[str], k: int) -> float:
    """Return binary macro recall among the first ``k`` unique ranked ids."""

    if not relevant_ids:
        return 0.0
    ranked = _deduplicate(ranked_ids)
    return len(set(ranked[:k]) & relevant_ids) / len(relevant_ids)


def reciprocal_rank_at_k(ranked_ids: Sequence[str], relevant_ids: set[str], k: int) -> float:
    """Return reciprocal rank of the first relevant unique result through ``k``."""

    for rank, identifier in enumerate(_deduplicate(ranked_ids)[:k], start=1):
        if identifier in relevant_ids:
            return 1.0 / rank
    return 0.0


def ndcg_at_k(ranked_ids: Sequence[str], relevant_ids: set[str], k: int) -> float:
    """Return binary nDCG through ``k`` over a unique identifier ranking."""

    if not relevant_ids:
        return 0.0
    ranked = _deduplicate(ranked_ids)[:k]
    dcg = sum(1.0 / math.log2(rank + 1) for rank, identifier in enumerate(ranked, start=1) if identifier in relevant_ids)
    ideal_count = min(k, len(relevant_ids))
    ideal = sum(1.0 / math.log2(rank + 1) for rank in range(1, ideal_count + 1))
    return dcg / ideal if ideal else 0.0


def evaluate_ranking(ranked_ids: Sequence[str], relevant_ids: set[str]) -> dict[str, float]:
    """Calculate the required recall, MRR, and nDCG measures for one query."""

    metrics = {f"recall_at_{cutoff}": recall_at_k(ranked_ids, relevant_ids, cutoff) for cutoff in METRIC_CUTOFFS}
    metrics["mrr_at_10"] = reciprocal_rank_at_k(ranked_ids, relevant_ids, 10)
    metrics["ndcg_at_10"] = ndcg_at_k(ranked_ids, relevant_ids, 10)
    return metrics


def _tokenize(value: str) -> list[str]:
    return [token for token in TOKEN_RE.findall(value.casefold()) if len(token) > 2 and token not in STOPWORDS]


def _record_text(record: dict[str, Any]) -> str:
    parts = [str(record.get(name) or "") for name in ("title", "body", "concept_type", "source_id", "record_id")]
    attributes = record.get("attributes")
    if isinstance(attributes, dict):
        parts.append(canonical_json(attributes))
    return " ".join(parts)


def _paper_id_from_strings(values: Iterable[str | None]) -> str | None:
    for value in values:
        if not value:
            continue
        match = PAPER_ID_RE.search(value)
        if match:
            return f"{match.group(1)}.{match.group(2).lower()}"
    return None


def _paper_id_from_mapping(value: dict[str, Any]) -> str | None:
    containers = [value]
    for name in ("metadata", "attributes", "record", "document"):
        nested = value.get(name)
        if isinstance(nested, dict):
            containers.append(nested)
    candidates: list[str | None] = []
    for container in containers:
        for name in ("paper_id", "paperId", "source_id", "sourceId", "record_id", "recordId", "concept_path", "path", "title"):
            item = container.get(name)
            candidates.append(item if isinstance(item, str) else None)
    return _paper_id_from_strings(candidates)


def _first_string(value: dict[str, Any], names: Sequence[str]) -> str | None:
    containers = [value]
    for key in ("metadata", "attributes", "record", "document"):
        nested = value.get(key)
        if isinstance(nested, dict):
            containers.append(nested)
    for container in containers:
        for name in names:
            item = container.get(name)
            if isinstance(item, str) and item:
                return item
    return None


def parse_search_output(payload: Any, top_k: int) -> list[RetrievalHit]:
    """Normalize supported JSON result envelopes from the embedding consultation CLI."""

    if isinstance(payload, dict):
        if payload.get("status") == "error":
            raise ComparisonError(f"Consult CLI reported an error: {payload.get('error') or payload.get('message')}")
        raw_hits = next((payload.get(name) for name in ("results", "hits", "records", "items") if isinstance(payload.get(name), list)), None)
        if raw_hits is None:
            raise ComparisonError("Consult CLI JSON must contain a results, hits, records, or items array.")
    elif isinstance(payload, list):
        raw_hits = payload
    else:
        raise ComparisonError("Consult CLI JSON must be an object or array.")
    hits: list[RetrievalHit] = []
    for rank, item in enumerate(raw_hits[:top_k], start=1):
        if not isinstance(item, dict):
            raise ComparisonError(f"Consult CLI hit {rank} is not an object.")
        source_id = _first_string(item, ("source_id", "sourceId"))
        chunk_id = _first_string(item, ("chunk_id", "chunkId"))
        ordinal_value = item.get("ordinal")
        ordinal = ordinal_value if isinstance(ordinal_value, int) and not isinstance(ordinal_value, bool) else None
        concept_path = _first_string(item, ("concept_path", "conceptPath", "artifact_path", "path"))
        concept_id = _first_string(item, ("concept_id", "conceptId"))
        record_id = _first_string(item, ("record_id", "recordId"))
        record_sha256 = _first_string(item, ("record_sha256", "recordSha256"))
        source_path = _first_string(item, ("source_path", "sourcePath"))
        text = _first_string(item, ("text", "chunk_text", "chunkText"))
        text_sha256 = _first_string(item, ("text_sha256", "textSha256"))
        locator_value = item.get("locator")
        locator = dict(locator_value) if isinstance(locator_value, dict) else None
        paper_id = _paper_id_from_mapping(item)
        score_value: Any = None
        for name in ("score", "similarity", "rrf_score", "rank_score"):
            if name in item:
                score_value = item[name]
                break
        if score_value is None and isinstance(item.get("scores"), dict):
            for name in ("hybrid", "vector", "lexical"):
                candidate = item["scores"].get(name)
                if candidate is not None:
                    score_value = candidate
                    break
        try:
            score = float(score_value) if score_value is not None else None
        except (TypeError, ValueError) as exc:
            raise ComparisonError(f"Consult CLI hit {rank} has a non-numeric score.") from exc
        hits.append(
            RetrievalHit(
                source_id=source_id,
                paper_id=paper_id,
                chunk_id=chunk_id,
                ordinal=ordinal,
                concept_path=concept_path.replace("\\", "/") if concept_path else None,
                concept_id=concept_id,
                record_id=record_id,
                record_sha256=record_sha256,
                source_path=source_path.replace("\\", "/") if source_path else None,
                locator=locator,
                text=text,
                text_sha256=text_sha256,
                score=score,
            )
        )
    return hits


class AuthoritativeLedger:
    """Load authoritative records once and bind every discovery hit back to them."""

    def __init__(self, bundle: Path, records: list[dict[str, Any]]) -> None:
        self.bundle = bundle.resolve()
        self.records = records
        self.by_identity: dict[tuple[str, str], dict[str, Any]] = {}
        for record in records:
            identity = (str(record["source_id"]), str(record["record_id"]))
            if identity in self.by_identity:
                raise ComparisonError(f"Duplicate authoritative ledger identity: {identity[0]}/{identity[1]}")
            self.by_identity[identity] = record

    @classmethod
    def from_bundle(cls, bundle: Path) -> "AuthoritativeLedger":
        """Read and structurally validate one bundle's authoritative JSONL ledger."""

        ledger_path = bundle / "semantic" / "records.jsonl"
        try:
            lines = ledger_path.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeError) as exc:
            raise ComparisonError(f"Cannot read authoritative ledger at {ledger_path}: {exc}") from exc
        records: list[dict[str, Any]] = []
        required = ("source_id", "record_id", "concept_id", "concept_path", "source_path", "body")
        for number, line in enumerate(lines, start=1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ComparisonError(f"Invalid authoritative ledger JSON line {number}: {exc}") from exc
            if not isinstance(record, dict):
                raise ComparisonError(f"Authoritative ledger line {number} is not an object.")
            missing = [name for name in required if not isinstance(record.get(name), str) or not record[name]]
            if missing:
                raise ComparisonError(
                    f"Authoritative ledger line {number} has invalid required fields: {', '.join(missing)}"
                )
            concept_path = str(record["concept_path"]).replace("\\", "/")
            safe_path = _safe_relative_path(concept_path)
            if not safe_path.parts or safe_path.parts[0] != "concepts":
                raise ComparisonError(f"Ledger concept path is outside concepts/: {concept_path!r}")
            record["concept_path"] = concept_path
            record["source_path"] = str(record["source_path"]).replace("\\", "/")
            records.append(record)
        if not records:
            raise ComparisonError(f"Authoritative ledger contains no records: {ledger_path}")
        return cls(bundle, records)

    def fingerprint(self) -> dict[str, Any]:
        """Describe the single ledger load used to validate a route."""

        path = self.bundle / "semantic" / "records.jsonl"
        return {
            "record_count": len(self.records),
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        }

    def lookup(self, hit: RetrievalHit) -> dict[str, Any] | None:
        """Return the exact ledger record named by a hit, if both identity fields exist."""

        if hit.source_id is None or hit.record_id is None:
            return None
        return self.by_identity.get((hit.source_id, hit.record_id))


class LegacyLexicalIndex:
    """Small deterministic TF-IDF-like index over a legacy Semantic OKF ledger."""

    def __init__(self, documents: list[tuple[RetrievalHit, Counter[str]]], idf: dict[str, float]) -> None:
        self.documents = documents
        self.idf = idf

    @classmethod
    def from_ledger(cls, ledger: AuthoritativeLedger) -> "LegacyLexicalIndex":
        """Index records from the route's already-loaded authoritative ledger."""

        documents: list[tuple[RetrievalHit, Counter[str]]] = []
        frequency: Counter[str] = Counter()
        for record in ledger.records:
            source_id = str(record["source_id"])
            concept_path = str(record["concept_path"])
            body = str(record["body"])
            paper_id = _paper_id_from_mapping(record)
            tokens = Counter(_tokenize(_record_text(record)))
            frequency.update(tokens.keys())
            documents.append(
                (
                    RetrievalHit(
                        source_id=source_id,
                        paper_id=paper_id,
                        chunk_id=None,
                        ordinal=None,
                        concept_path=concept_path,
                        concept_id=str(record["concept_id"]),
                        record_id=str(record["record_id"]),
                        record_sha256=(
                            str(record["record_sha256"])
                            if isinstance(record.get("record_sha256"), str)
                            else None
                        ),
                        source_path=str(record["source_path"]),
                        locator={"kind": "record"},
                        text=body,
                        text_sha256=sha256_bytes(body.encode("utf-8")),
                        score=None,
                    ),
                    tokens,
                )
            )
        if not documents:
            raise ComparisonError("Legacy ledger contains no records.")
        count = len(documents)
        idf = {token: math.log((count + 1) / (seen + 1)) + 1.0 for token, seen in frequency.items()}
        return cls(documents, idf)

    def search(self, query: str, top_k: int) -> list[RetrievalHit]:
        """Rank legacy records by deterministic query-token overlap."""

        query_tokens = set(_tokenize(query))
        ranked: list[tuple[float, str, RetrievalHit]] = []
        for hit, tokens in self.documents:
            score = sum((1.0 + math.log(tokens[token])) * self.idf.get(token, 0.0) for token in query_tokens if tokens[token])
            if score <= 0.0:
                continue
            path = hit.concept_path or ""
            ranked.append(
                (
                    score,
                    path,
                    RetrievalHit(
                        source_id=hit.source_id,
                        paper_id=hit.paper_id,
                        chunk_id=hit.chunk_id,
                        ordinal=hit.ordinal,
                        concept_path=hit.concept_path,
                        concept_id=hit.concept_id,
                        record_id=hit.record_id,
                        record_sha256=hit.record_sha256,
                        source_path=hit.source_path,
                        locator=hit.locator,
                        text=hit.text,
                        text_sha256=hit.text_sha256,
                        score=score,
                    ),
                )
            )
        ranked.sort(key=lambda item: (-item[0], item[1]))
        return [item[2] for item in ranked[:top_k]]


def run_consult_search(
    python_executable: str,
    consult_script: Path,
    bundle: Path,
    query: str,
    mode: str,
    top_k: int,
    timeout_seconds: float,
) -> list[RetrievalHit]:
    """Call the stable embedding consultation CLI contract and normalize its JSON hits."""

    command = [
        python_executable,
        str(consult_script),
        str(bundle),
        "search",
        "--query",
        query,
        "--mode",
        mode,
        "--top-k",
        str(top_k),
    ]
    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="strict",
            timeout=timeout_seconds,
            check=False,
        )
    except (OSError, UnicodeError, subprocess.TimeoutExpired) as exc:
        raise ComparisonError(f"Consult CLI {mode} search failed to execute: {exc}") from exc
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip() or f"exit {completed.returncode}"
        raise ComparisonError(f"Consult CLI {mode} search failed: {detail}")
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise ComparisonError(f"Consult CLI {mode} emitted invalid JSON: {exc}") from exc
    return parse_search_output(payload, top_k)


def _validate_hit_evidence(
    bundle: Path,
    ledger: AuthoritativeLedger,
    hit: RetrievalHit,
) -> dict[str, Any]:
    """Validate one discovery hit against its exact authoritative record and text locator."""

    issues: list[dict[str, str]] = []

    def issue(code: str, message: str) -> None:
        issues.append({"code": code, "message": message})

    concept_file: Path | None = None
    if hit.concept_path is None:
        issue("missing-concept-path", "The hit has no concept_path.")
    else:
        try:
            safe = _safe_relative_path(hit.concept_path)
            if not safe.parts or safe.parts[0] != "concepts":
                issue("concept-path-scope", "The concept path is outside concepts/.")
            else:
                concept_file = _local_file(bundle, hit.concept_path)
        except ComparisonError as exc:
            issue("unsafe-concept-path", str(exc))
        if concept_file is not None and not concept_file.is_file():
            issue("missing-concept-file", f"The bound concept file does not exist: {hit.concept_path}")

    record = ledger.lookup(hit)
    if record is None:
        issue("ledger-binding", "No authoritative record matches the hit source_id and record_id.")
    else:
        identity_fields = {
            "source_id": hit.source_id,
            "record_id": hit.record_id,
            "concept_id": hit.concept_id,
            "concept_path": hit.concept_path,
            "source_path": hit.source_path,
        }
        for field, actual in identity_fields.items():
            expected = record.get(field)
            if actual is None:
                issue(f"missing-{field.replace('_', '-')}", f"The hit has no {field}.")
            elif actual != expected:
                issue(
                    f"{field.replace('_', '-')}-binding",
                    f"Hit {field} {actual!r} does not match ledger value {expected!r}.",
                )
        expected_record_hash = record.get("record_sha256")
        if hit.record_sha256 is not None and hit.record_sha256 != expected_record_hash:
            issue("record-sha256-binding", "The hit record_sha256 does not match the ledger.")

        if hit.text is None:
            issue("missing-text", "The hit has no evidence text.")
        if hit.text_sha256 is None:
            issue("missing-text-sha256", "The hit has no text_sha256.")
        elif hit.text is not None:
            actual_text_hash = sha256_bytes(hit.text.encode("utf-8"))
            if hit.text_sha256 != actual_text_hash:
                issue("text-sha256", "The hit text_sha256 does not hash its retained text.")

        locator = hit.locator
        body = str(record.get("body") or "")
        if not isinstance(locator, dict):
            issue("missing-locator", "The hit has no object locator.")
        elif locator.get("kind") == "record":
            if set(locator) != {"kind"}:
                issue("record-locator-shape", "A record locator may contain only kind=record.")
            if hit.text is not None and hit.text != body:
                issue("record-locator-text", "The retained text is not the complete authoritative record body.")
        elif locator.get("kind") == "character-range":
            if set(locator) != {"kind", "start", "end"}:
                issue("character-range-shape", "A character-range locator requires only kind, start, and end.")
            start = locator.get("start")
            end = locator.get("end")
            integers = (
                isinstance(start, int)
                and not isinstance(start, bool)
                and isinstance(end, int)
                and not isinstance(end, bool)
            )
            if not integers or not (0 <= start <= end <= len(body)):
                issue("character-range-bounds", "The character-range bounds are not valid for the record body.")
            elif hit.text is not None and body[start:end] != hit.text:
                issue("character-range-text", "The retained text is not the exact authoritative body slice.")
        else:
            issue("locator-kind", "The locator kind must be record or character-range.")

    return {
        "valid": not issues,
        "issues": issues,
    }


def _hit_report(hit: RetrievalHit, validation: dict[str, Any], rank: int) -> dict[str, Any]:
    """Serialize a compact hit after validating its in-memory evidence text."""

    text_bytes = len(hit.text.encode("utf-8")) if hit.text is not None else None
    text_characters = len(hit.text) if hit.text is not None else None

    return {
        "rank": rank,
        "source_id": hit.source_id,
        "paper_id": hit.paper_id,
        "chunk_id": hit.chunk_id,
        "ordinal": hit.ordinal,
        "concept_id": hit.concept_id,
        "concept_path": hit.concept_path,
        "record_id": hit.record_id,
        "record_sha256": hit.record_sha256,
        "source_path": hit.source_path,
        "locator": hit.locator,
        "text_sha256": hit.text_sha256,
        "text_bytes": text_bytes,
        "text_characters": text_characters,
        "score": hit.score,
        "evidence_validation": validation,
    }


def _evidence_validity(
    bundle: Path,
    ledger: AuthoritativeLedger,
    hits: Sequence[RetrievalHit],
) -> dict[str, Any]:
    validations = [_validate_hit_evidence(bundle, ledger, hit) for hit in hits]
    valid = sum(bool(item["valid"]) for item in validations)
    return {
        "returned": len(hits),
        "valid": valid,
        "invalid": len(hits) - valid,
        "ratio": valid / len(hits) if hits else None,
        "hits": [
            _hit_report(hit, validation, rank)
            for rank, (hit, validation) in enumerate(
                zip(hits, validations, strict=True),
                start=1,
            )
        ],
    }


def _percentile(values: Sequence[float], percentile: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    position = (len(ordered) - 1) * percentile
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    weight = position - lower
    return ordered[lower] * (1.0 - weight) + ordered[upper] * weight


def _mean_metrics(rows: Sequence[dict[str, Any]], key: str) -> dict[str, float]:
    names = [*(f"recall_at_{cutoff}" for cutoff in METRIC_CUTOFFS), "mrr_at_10", "ndcg_at_10"]
    return {name: statistics.fmean(float(row[key][name]) for row in rows) for name in names}


def evaluate_route(
    name: str,
    bundle: Path,
    ledger: AuthoritativeLedger,
    questions: Sequence[RetrievalQuestion],
    search: Callable[[str], list[RetrievalHit]],
    *,
    continue_on_error: bool,
) -> dict[str, Any]:
    """Evaluate one retrieval route across every query and aggregate quality and timing."""

    rows: list[dict[str, Any]] = []
    timings: list[float] = []
    errors: list[dict[str, str]] = []
    for question in questions:
        started = time.perf_counter()
        error: str | None = None
        try:
            hits = search(question.question)
        except ComparisonError as exc:
            if not continue_on_error:
                raise
            hits = []
            error = str(exc)
            errors.append({"question_id": question.identifier, "error": error})
        elapsed_ms = (time.perf_counter() - started) * 1000.0
        timings.append(elapsed_ms)
        paper_ranking = _deduplicate(hit.paper_id for hit in hits)
        source_ranking = _deduplicate(hit.source_id for hit in hits)
        evidence_validity = _evidence_validity(bundle, ledger, hits)
        rows.append(
            {
                "question_id": question.identifier,
                "elapsed_ms": elapsed_ms,
                "error": error,
                "hit_count": len(hits),
                "paper_ids": paper_ranking,
                "source_ids": source_ranking,
                "hits": evidence_validity.pop("hits"),
                "paper_metrics": evaluate_ranking(paper_ranking, set(question.paper_ids)),
                "source_metrics": evaluate_ranking(source_ranking, set(question.source_ids)),
                "evidence_validity": evidence_validity,
            }
        )
    total_hits = sum(int(row["evidence_validity"]["returned"]) for row in rows)
    valid_evidence = sum(int(row["evidence_validity"]["valid"]) for row in rows)
    return {
        "name": name,
        "query_count": len(rows),
        "error_count": len(errors),
        "errors": errors,
        "paper_metrics": _mean_metrics(rows, "paper_metrics"),
        "source_metrics": _mean_metrics(rows, "source_metrics"),
        "evidence_validity": {
            "contract": (
                "Each retained hit must have a safe concepts/ path and existing concept file; bind to one "
                "authoritative ledger record by source_id and record_id; match source, record, concept, path, "
                "and source-path identity; hash its retained text; and resolve an exact record or character-range "
                "locator against the authoritative record body."
            ),
            "ledger": ledger.fingerprint(),
            "returned": total_hits,
            "valid": valid_evidence,
            "invalid": total_hits - valid_evidence,
            "ratio": valid_evidence / total_hits if total_hits else None,
        },
        "timing_ms": {
            "total": sum(timings),
            "mean": statistics.fmean(timings),
            "median": statistics.median(timings),
            "p95": _percentile(timings, 0.95),
        },
        "queries": rows,
    }


def _bundle_source_paths(bundle: Path) -> set[str]:
    manifest = _load_json_object(bundle / "semantic" / "source-manifest.json", "bundle source manifest")
    sources = manifest.get("sources")
    if not isinstance(sources, list):
        raise ComparisonError(f"Bundle source manifest has no sources array: {bundle}")
    paths: set[str] = set()
    for source in sources:
        if not isinstance(source, dict):
            continue
        path = source.get("path")
        if isinstance(path, str):
            paths.add(path.replace("\\", "/"))
        members = source.get("members")
        if isinstance(members, list):
            for member in members:
                if isinstance(member, dict) and isinstance(member.get("path"), str):
                    paths.add(member["path"].replace("\\", "/"))
    return paths


def bundle_input_coverage(bundle: Path, inventory: dict[str, Any]) -> dict[str, Any]:
    """Compare declared bundle source paths with the exact 30-file inventory."""

    expected = {str(entry["path"]) for entry in inventory["files"]}
    declared = _bundle_source_paths(bundle)
    covered = sorted(expected & declared)
    missing = sorted(expected - declared)
    auxiliary = inventory.get("required_auxiliary", {})
    auxiliary_path = auxiliary.get("file", {}).get("path") if isinstance(auxiliary, dict) else None
    return {
        "expected": len(expected),
        "covered": len(covered),
        "ratio": len(covered) / len(expected) if expected else 0.0,
        "covered_paths": covered,
        "missing_paths": missing,
        "required_auxiliary_path": auxiliary_path,
        "required_auxiliary_declared": isinstance(auxiliary_path, str) and auxiliary_path in declared,
        "declared_source_path_count": len(declared),
    }


def _artifact_fingerprint(path: Path) -> dict[str, Any]:
    return {"bytes": path.stat().st_size, "sha256": sha256_file(path)}


def _authoritative_relative_files(bundle: Path) -> list[str]:
    """List the complete bundle core while excluding only derived retrieval data."""

    result: list[str] = []
    for path in bundle.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(bundle)
        if relative.parts and relative.parts[0] == "retrieval":
            continue
        result.append(relative.as_posix())
    return sorted(result)


def authoritative_core_fingerprint(bundle: Path) -> dict[str, Any]:
    """Fingerprint every non-retrieval file and the required semantic key artifacts."""

    relative_files = _authoritative_relative_files(bundle)
    key_artifacts: dict[str, dict[str, Any] | None] = {}
    for relative in CORE_KEY_ARTIFACTS:
        path = bundle / relative
        key_artifacts[relative] = _artifact_fingerprint(path) if path.is_file() else None
    return {
        "scope": "all bundle files except retrieval/",
        "file_count": len(relative_files),
        "total_bytes": sum((bundle / relative).stat().st_size for relative in relative_files),
        "logical_tree_sha256": logical_tree_sha256(bundle, relative_files),
        "key_artifacts": key_artifacts,
    }


def compare_authoritative_cores(legacy_bundle: Path, new_bundle: Path) -> dict[str, Any]:
    """Prove whether retrieval derivation preserved the authoritative Semantic OKF core."""

    legacy_files = set(_authoritative_relative_files(legacy_bundle))
    new_files = set(_authoritative_relative_files(new_bundle))
    legacy = authoritative_core_fingerprint(legacy_bundle)
    new = authoritative_core_fingerprint(new_bundle)
    artifact_parity: dict[str, dict[str, Any]] = {}
    for relative in CORE_KEY_ARTIFACTS:
        legacy_artifact = legacy["key_artifacts"][relative]
        new_artifact = new["key_artifacts"][relative]
        artifact_parity[relative] = {
            "equal": legacy_artifact is not None
            and new_artifact is not None
            and legacy_artifact["sha256"] == new_artifact["sha256"],
            "legacy": legacy_artifact,
            "new": new_artifact,
        }
    file_set_equal = legacy_files == new_files
    tree_equal = legacy["logical_tree_sha256"] == new["logical_tree_sha256"]
    artifacts_equal = all(item["equal"] for item in artifact_parity.values())
    return {
        "status": "pass" if file_set_equal and tree_equal and artifacts_equal else "fail",
        "contract": (
            "The complete non-retrieval file set and LF-normalized logical tree must match, and every "
            "required semantic key artifact must have an identical byte SHA-256."
        ),
        "authoritative_file_set": {
            "equal": file_set_equal,
            "legacy_count": len(legacy_files),
            "new_count": len(new_files),
            "missing_from_new": sorted(legacy_files - new_files),
            "unexpected_in_new": sorted(new_files - legacy_files),
        },
        "logical_core_tree_equal": tree_equal,
        "key_artifacts_equal": artifacts_equal,
        "key_artifacts": artifact_parity,
        "legacy": legacy,
        "new": new,
    }


def bundle_fingerprint(bundle: Path) -> dict[str, Any]:
    """Report a portable logical tree hash, byte size, file count, and key artifact hashes."""

    files = sorted(path for path in bundle.rglob("*") if path.is_file())
    key_artifacts: dict[str, dict[str, Any]] = {}
    for relative in BUNDLE_KEY_ARTIFACTS:
        path = bundle / relative
        if path.is_file():
            key_artifacts[relative] = _artifact_fingerprint(path)
    return {
        "file_count": len(files),
        "total_bytes": sum(path.stat().st_size for path in files),
        "logical_tree_sha256": logical_tree_sha256(bundle),
        "key_artifacts": key_artifacts,
    }


def _file_fingerprint(path: Path) -> dict[str, Any]:
    return {"path": _report_path(path), "bytes": path.stat().st_size, "sha256": sha256_file(path)}


def _report_path(path: Path) -> str:
    """Return a portable path without leaking a workstation-specific absolute prefix."""

    resolved = path.resolve()
    try:
        return resolved.relative_to(Path.cwd().resolve()).as_posix()
    except ValueError:
        return f"external/{resolved.name}"


def run_comparison(args: argparse.Namespace) -> dict[str, Any]:
    """Run all four routes and return the complete machine-readable comparison."""

    if args.top_k < 10:
        raise ComparisonError("--top-k must be at least 10 for the declared metrics.")
    inventory = load_inventory(args.inventory)
    questions = load_questions(args.questions)
    legacy_bundle = args.legacy_bundle.resolve()
    new_bundle = args.new_bundle.resolve()
    consult_script = args.consult_script.resolve()
    for label, path in (("legacy bundle", legacy_bundle), ("new bundle", new_bundle)):
        if not path.is_dir():
            raise ComparisonError(f"{label} is not a directory: {path}")
    if not consult_script.is_file():
        raise ComparisonError(f"Embedding consult script is missing: {consult_script}")

    raw_input_verification: dict[str, Any] | None = None
    if args.input_root is not None:
        raw_input_verification = verify_input_inventory(args.input_root, inventory)
        if raw_input_verification["status"] != "pass" and not args.allow_input_drift:
            raise ComparisonError("Raw input inventory verification failed; use --allow-input-drift only for diagnostics.")

    legacy_ledger = AuthoritativeLedger.from_bundle(legacy_bundle)
    new_ledger = AuthoritativeLedger.from_bundle(new_bundle)
    setup_started = time.perf_counter()
    legacy_index = LegacyLexicalIndex.from_ledger(legacy_ledger)
    legacy_setup_ms = (time.perf_counter() - setup_started) * 1000.0
    routes = [
        evaluate_route(
            "legacy_lexical",
            legacy_bundle,
            legacy_ledger,
            questions,
            lambda query: legacy_index.search(query, args.top_k),
            continue_on_error=args.continue_on_error,
        )
    ]
    routes[0]["setup_ms"] = legacy_setup_ms
    routes[0]["timing_scope"] = (
        "In-process search after one ledger load and index setup; setup_ms is reported separately."
    )
    for route_name, mode in (("new_lexical", "lexical"), ("vector", "vector"), ("hybrid", "hybrid")):
        route = evaluate_route(
            route_name,
            new_bundle,
            new_ledger,
            questions,
            lambda query, selected=mode: run_consult_search(
                args.python_executable,
                consult_script,
                new_bundle,
                query,
                selected,
                args.top_k,
                args.timeout_seconds,
            ),
            continue_on_error=args.continue_on_error,
        )
        route["timing_scope"] = (
            "End-to-end per-query CLI subprocess, including process startup, snapshot validation, "
            "provider/model loading, retrieval, JSON serialization, and parent-side parsing."
        )
        routes.append(route)

    return {
        "schema_version": "1.2",
        "comparison": "semantic-okf-legacy-versus-embedding-retrieval",
        "query_count": len(questions),
        "top_k": args.top_k,
        "metric_contract": {
            "primary_identity": "paper_id",
            "duplicate_policy": "keep first rank per identity",
            "recall_cutoffs": list(METRIC_CUTOFFS),
            "mrr_cutoff": 10,
            "ndcg_cutoff": 10,
            "relevance": "binary",
        },
        "evidence_contract": (
            "Discovery quality is scored independently from evidence validity. Exact hit text is retained in "
            "memory through validation against one route-local authoritative ledger load. Compact reported "
            "hits omit raw text and retain record and concept identities, source path, exact locator, text "
            "SHA-256, UTF-8 byte count, and character count so evidence can be reconstructed and rehashed."
        ),
        "consult_command_contract": "PYTHON SCRIPT BUNDLE search --query QUERY --mode MODE --top-k K",
        "timing_methodology": {
            "legacy_lexical": {
                "execution_model": "single in-process index reused across queries",
                "setup": "Ledger loading and index construction occur once and are reported as setup_ms.",
                "per_query": "only LegacyLexicalIndex.search is timed.",
            },
            "new_routes": {
                "routes": ["new_lexical", "vector", "hybrid"],
                "execution_model": "one fresh CLI subprocess per query",
                "per_query": (
                    "timing includes process startup, full snapshot validation, provider/model loading, "
                    "retrieval, JSON serialization, and parent-side parsing."
                ),
            },
            "interpretation": (
                "reported latency is operational end-to-end latency, not an isolated algorithm-speed "
                "comparison; legacy and new route timings have intentionally different execution scopes."
            ),
        },
        "inputs": {
            "path_contract": (
                "Paths are POSIX-relative to the invocation directory when possible; external inputs use only "
                "an external/<basename> label and remain uniquely identified by byte count and SHA-256."
            ),
            "inventory": _file_fingerprint(args.inventory),
            "questions": _file_fingerprint(args.questions),
            "consult_script": _file_fingerprint(consult_script),
            "comparator_script": _file_fingerprint(Path(__file__).resolve()),
            "raw_input_verification": raw_input_verification,
        },
        "bundles": {
            "legacy": {
                "path": _report_path(legacy_bundle),
                "fingerprint": bundle_fingerprint(legacy_bundle),
                "input_coverage": bundle_input_coverage(legacy_bundle, inventory),
            },
            "new": {
                "path": _report_path(new_bundle),
                "fingerprint": bundle_fingerprint(new_bundle),
                "input_coverage": bundle_input_coverage(new_bundle, inventory),
            },
        },
        "core_semantic_parity": compare_authoritative_cores(legacy_bundle, new_bundle),
        "routes": routes,
    }


def _format_metric(value: Any) -> str:
    return "n/a" if value is None else f"{float(value):.4f}"


def render_markdown(report: dict[str, Any]) -> str:
    """Render a concise human-readable comparison from the JSON report."""

    lines = [
        "# Semantic OKF Embedding Retrieval Comparison",
        "",
        f"Queries: {report['query_count']}; top-k: {report['top_k']}; primary relevance identity: paper ID.",
        "",
        "## Retrieval quality",
        "",
        "| Route | Recall@1 | Recall@3 | Recall@5 | Recall@10 | MRR@10 | nDCG@10 | Source Recall@10 | Evidence validity | Mean ms | p95 ms | Errors |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for route in report["routes"]:
        paper = route["paper_metrics"]
        source = route["source_metrics"]
        timing = route["timing_ms"]
        lines.append(
            "| {name} | {r1} | {r3} | {r5} | {r10} | {mrr} | {ndcg} | {sr10} | {paths} | {mean} | {p95} | {errors} |".format(
                name=route["name"],
                r1=_format_metric(paper["recall_at_1"]),
                r3=_format_metric(paper["recall_at_3"]),
                r5=_format_metric(paper["recall_at_5"]),
                r10=_format_metric(paper["recall_at_10"]),
                mrr=_format_metric(paper["mrr_at_10"]),
                ndcg=_format_metric(paper["ndcg_at_10"]),
                sr10=_format_metric(source["recall_at_10"]),
                paths=_format_metric(route["evidence_validity"]["ratio"]),
                mean=_format_metric(timing["mean"]),
                p95=_format_metric(timing["p95"]),
                errors=route["error_count"],
            )
        )

    timing = report["timing_methodology"]
    lines.extend(
        [
            "",
            "## Timing methodology",
            "",
            f"- Legacy lexical: {timing['legacy_lexical']['execution_model']}; "
            f"{timing['legacy_lexical']['per_query']}",
            f"- New lexical, vector, and hybrid: {timing['new_routes']['execution_model']}; "
            f"{timing['new_routes']['per_query']}",
            f"- Interpretation: {timing['interpretation']}",
        ]
    )

    lines.extend(
        [
            "",
            "## Corpus coverage and bundle size",
            "",
            "| Bundle | 30-input coverage | Auxiliary vocabulary | Files | Bytes | Logical tree SHA-256 |",
            "| --- | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for name in ("legacy", "new"):
        bundle = report["bundles"][name]
        coverage = bundle["input_coverage"]
        fingerprint = bundle["fingerprint"]
        lines.append(
            f"| {name} | {coverage['covered']}/{coverage['expected']} ({coverage['ratio']:.1%}) | "
            f"{'yes' if coverage['required_auxiliary_declared'] else 'no'} | {fingerprint['file_count']} | "
            f"{fingerprint['total_bytes']} | `{fingerprint['logical_tree_sha256']}` |"
        )

    parity = report["core_semantic_parity"]
    file_set = parity["authoritative_file_set"]
    lines.extend(
        [
            "",
            "## Core semantic parity",
            "",
            f"Status: **{parity['status']}**. Authoritative file sets equal: "
            f"**{'yes' if file_set['equal'] else 'no'}** "
            f"({file_set['legacy_count']} legacy, {file_set['new_count']} new).",
            "",
            f"Logical core trees equal: **{'yes' if parity['logical_core_tree_equal'] else 'no'}**. "
            f"Legacy: `{parity['legacy']['logical_tree_sha256']}`; "
            f"new: `{parity['new']['logical_tree_sha256']}`.",
            "",
            "| Required artifact | Equal | Legacy SHA-256 | New SHA-256 |",
            "| --- | ---: | --- | --- |",
        ]
    )
    for relative, comparison in parity["key_artifacts"].items():
        legacy_hash = comparison["legacy"]["sha256"] if comparison["legacy"] else "missing"
        new_hash = comparison["new"]["sha256"] if comparison["new"] else "missing"
        lines.append(
            f"| `{relative}` | {'yes' if comparison['equal'] else 'no'} | "
            f"`{legacy_hash}` | `{new_hash}` |"
        )
    if file_set["missing_from_new"] or file_set["unexpected_in_new"]:
        lines.extend(
            [
                "",
                f"Missing from new: {', '.join(file_set['missing_from_new']) or 'none'}.",
                f"Unexpected in new: {', '.join(file_set['unexpected_in_new']) or 'none'}.",
            ]
        )

    raw = report["inputs"].get("raw_input_verification")
    if raw is not None:
        lines.extend(["", "## Raw input verification", "", f"Status: **{raw['status']}**. Verified core files: {raw['verified_core_files']}/{raw['expected_core_files']}."])
        if raw["errors"]:
            lines.extend(["", *[f"- {error}" for error in raw["errors"]]])
    route_errors = [(route["name"], error) for route in report["routes"] for error in route["errors"]]
    if route_errors:
        lines.extend(["", "## Route errors", ""])
        lines.extend(f"- `{route}` / `{error['question_id']}`: {error['error']}" for route, error in route_errors)
    lines.append("")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    """Build the portable comparison command-line parser."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inventory", type=Path, required=True)
    parser.add_argument("--questions", type=Path, required=True)
    parser.add_argument("--legacy-bundle", type=Path, required=True)
    parser.add_argument("--new-bundle", type=Path, required=True)
    parser.add_argument("--consult-script", type=Path, required=True)
    parser.add_argument("--python-executable", default=sys.executable)
    parser.add_argument("--input-root", type=Path, help="Optional root used to verify all inventoried raw inputs.")
    parser.add_argument("--top-k", type=int, default=10)
    parser.add_argument("--timeout-seconds", type=float, default=120.0)
    parser.add_argument("--continue-on-error", action="store_true")
    parser.add_argument("--allow-input-drift", action="store_true")
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-markdown", type=Path, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the comparison and write JSON plus Markdown reports."""

    args = build_parser().parse_args(argv)
    try:
        report = run_comparison(args)
    except ComparisonError as exc:
        print(f"comparison error: {exc}", file=sys.stderr)
        return 2
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_markdown.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.output_markdown.write_text(render_markdown(report), encoding="utf-8")
    print(canonical_json({"query_count": report["query_count"], "routes": [route["name"] for route in report["routes"]]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
