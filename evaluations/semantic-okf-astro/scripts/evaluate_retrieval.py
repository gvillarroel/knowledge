#!/usr/bin/env python3
"""Evaluate every local Semantic OKF consultation route on 40 Astro questions."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import importlib.util
import json
import math
import os
import re
import statistics
import subprocess
import sys
import time
from collections import Counter
from dataclasses import dataclass, replace
from pathlib import Path, PurePosixPath
from types import ModuleType
from typing import Any, Callable, Iterable, Mapping, Sequence


SCRIPT = Path(__file__).resolve()
EVALUATION = SCRIPT.parents[1]
REPO = SCRIPT.parents[3]
REPORTS = EVALUATION / "reports"
SCHEMA = "semantic-okf-astro-retrieval-comparison/1.0"
RAW_POOL = 100
METRIC_CUTOFFS = (1, 3, 5, 10, 20)
TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9._/-]*", re.IGNORECASE)
STOPWORDS = frozenset(
    "a about after all also an and are as at be because before between but by can compare could "
    "describe did do does each explain for from had has have how if in into is it its most not of "
    "on or should than that the their these they this to using was were what when where which why with without"
    .split()
)
FAMILY_ROUTES: dict[str, tuple[str, ...]] = {
    "legacy": ("legacy_tfidf",),
    "embeddings": ("lexical", "vector", "hybrid"),
    "classical": ("bm25", "topic", "association", "fusion"),
    "adaptive": ("bm25", "topic", "association", "fusion", "adaptive"),
    "entity-graph": ("lexical", "entity", "traversal", "fusion"),
    "ensemble": ("quality", "fast", "robust"),
}
CONSULT_SCRIPTS = {
    "embeddings": "skills/consult-semantic-okf-embeddings/scripts/query_semantic_okf_embeddings.py",
    "classical": "skills/consult-semantic-okf-classical/scripts/query_semantic_okf_classical.py",
    "adaptive": "skills/consult-semantic-okf-adaptive/scripts/query_semantic_okf_adaptive.py",
    "entity-graph": "skills/consult-semantic-okf-entity-graph/scripts/query_semantic_okf_entity_graph.py",
    "ensemble": "skills/consult-semantic-okf-ensemble/scripts/query_semantic_okf_ensemble.py",
}
RUNTIME_MODULES = {
    "embeddings": "_embedding_snapshot.py",
    "classical": "_classical_snapshot.py",
    "adaptive": "_adaptive_snapshot.py",
    "entity-graph": "_entity_graph_snapshot.py",
    "ensemble": "_ensemble_snapshot.py",
}
_MISSING_MODULE = object()
EMBEDDING_WARMUP_QUERY = "Semantic OKF offline retrieval runtime warmup"


class EvaluationError(RuntimeError):
    """Describe malformed benchmark data, consultation output, or evidence."""


def canonical_json(value: Any) -> str:
    """Serialize JSON deterministically for identity bindings."""

    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def pretty_json(value: Any) -> str:
    """Serialize a stable report."""

    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n"


def sha256_bytes(value: bytes) -> str:
    """Return a lowercase SHA-256 digest."""

    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    """Hash one regular file."""

    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    """Reject duplicate JSON members."""

    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise EvaluationError(f"duplicate JSON member: {key}")
        result[key] = value
    return result


def load_json(path: Path) -> dict[str, Any]:
    """Load one strict JSON object."""

    try:
        value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=strict_object)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise EvaluationError(f"cannot load JSON object {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise EvaluationError(f"expected JSON object at {path}")
    return value


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    """Load nonblank strict JSONL objects."""

    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        raise EvaluationError(f"cannot load JSONL {path}: {exc}") from exc
    rows: list[dict[str, Any]] = []
    for number, line in enumerate(lines, 1):
        if not line.strip():
            raise EvaluationError(f"blank JSONL row at {path}:{number}")
        try:
            value = json.loads(line, object_pairs_hook=strict_object)
        except json.JSONDecodeError as exc:
            raise EvaluationError(f"invalid JSONL at {path}:{number}: {exc}") from exc
        if not isinstance(value, dict):
            raise EvaluationError(f"expected object at {path}:{number}")
        rows.append(value)
    if not rows:
        raise EvaluationError(f"empty JSONL file: {path}")
    return rows


def atomic_write(path: Path, content: str) -> None:
    """Atomically replace a compact checked report."""

    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(content, encoding="utf-8", newline="\n")
    os.replace(temporary, path)


def append_only_write(path: Path, content: str) -> None:
    """Write one raw result exactly once."""

    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise EvaluationError(f"refusing to replace append-only raw report: {path}")
    path.write_text(content, encoding="utf-8", newline="\n")


def bundle_identity(root: Path) -> dict[str, Any]:
    """Hash an immutable bundle tree before or after consultation."""

    rows = []
    total = 0
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        relative = path.relative_to(root).as_posix()
        size = path.stat().st_size
        total += size
        rows.append({"path": relative, "bytes": size, "sha256": sha256_file(path)})
    return {
        "file_count": len(rows),
        "total_bytes": total,
        "tree_sha256": sha256_bytes(canonical_json(rows).encode("utf-8")),
    }


@dataclass(frozen=True)
class Question:
    """Represent one closed retrieval question and document qrels."""

    identifier: str
    cohort: str
    text: str
    document_ids: tuple[str, ...]
    source_ids: tuple[str, ...]


@dataclass(frozen=True)
class Hit:
    """Normalize one alternative-specific result for independent validation."""

    source_id: str | None
    record_id: str | None
    document_id: str | None
    record_sha256: str | None
    concept_id: str | None
    concept_path: str | None
    source_path: str | None
    locator: dict[str, Any] | None
    text: str | None
    text_sha256: str | None
    score: float | None
    retrieval_id: str | None
    record_sha256_provenance: str | None = None


def sorted_strings(value: Any, label: str, *, allow_empty: bool = False) -> tuple[str, ...]:
    """Validate a sorted unique string array."""

    if not isinstance(value, list) or (not value and not allow_empty) or any(
        not isinstance(item, str) or not item for item in value
    ):
        raise EvaluationError(f"{label} must be a {'possibly empty ' if allow_empty else 'nonempty '}string array")
    if value != sorted(set(value)):
        raise EvaluationError(f"{label} must be sorted and unique")
    return tuple(value)


def load_identity_map(path: Path) -> tuple[dict[tuple[str, str], str], dict[str, dict[str, Any]]]:
    """Load the sole explicit source-record-to-document crosswalk."""

    payload = load_json(path)
    if payload.get("schema_version") != "semantic-okf-astro-source-identity/1.1":
        raise EvaluationError("source-combination schema_version differs")
    records = payload.get("records")
    if not isinstance(records, list) or len(records) != 416:
        raise EvaluationError("source-combination must contain exactly 416 records")
    by_identity: dict[tuple[str, str], str] = {}
    by_document: dict[str, dict[str, Any]] = {}
    expected_keys = {"source_id", "record_id", "document_id", "path", "upstream_path", "canonical_url"}
    for number, row in enumerate(records, 1):
        if not isinstance(row, dict) or set(row) != expected_keys:
            raise EvaluationError(f"source-combination row {number} violates its closed schema")
        if any(not isinstance(row[key], str) or not row[key] for key in expected_keys):
            raise EvaluationError(f"source-combination row {number} contains an empty identity")
        key = (row["source_id"], row["record_id"])
        if key in by_identity or row["document_id"] in by_document:
            raise EvaluationError("source-combination contains duplicate identity/document IDs")
        by_identity[key] = row["document_id"]
        by_document[row["document_id"]] = row
    encoded = payload.get("source_record_to_document_ids")
    if not isinstance(encoded, dict) or len(encoded) != len(by_identity):
        raise EvaluationError("source_record_to_document_ids is not total")
    expected = {canonical_json([*key]): value for key, value in by_identity.items()}
    if encoded != dict(sorted(expected.items())):
        raise EvaluationError("source_record_to_document_ids differs from records")
    return by_identity, by_document


def load_questions(path: Path, documents: Mapping[str, Any]) -> list[Question]:
    """Load the exact 40-question benchmark."""

    rows = load_jsonl(path)
    if len(rows) != 40:
        raise EvaluationError("retrieval benchmark must contain exactly 40 questions")
    result: list[Question] = []
    observed: set[str] = set()
    for number, row in enumerate(rows, 1):
        if set(row) != {"id", "question", "question_type", "qrels"}:
            raise EvaluationError(f"question row {number} violates its closed schema")
        identifier, question, cohort, qrels = row["id"], row["question"], row["question_type"], row["qrels"]
        if not isinstance(identifier, str) or not identifier or identifier in observed:
            raise EvaluationError(f"question row {number} has invalid/duplicate id")
        observed.add(identifier)
        if not isinstance(question, str) or not question.strip():
            raise EvaluationError(f"question {identifier} is empty")
        if cohort not in {"direct", "cross-document", "hard"}:
            raise EvaluationError(f"question {identifier} has invalid question_type")
        if not isinstance(qrels, dict) or set(qrels) != {"document_ids", "source_ids"}:
            raise EvaluationError(f"question {identifier} qrels violates its closed schema")
        document_ids = sorted_strings(qrels["document_ids"], f"{identifier}.document_ids")
        source_ids = sorted_strings(qrels["source_ids"], f"{identifier}.source_ids")
        unknown = sorted(set(document_ids) - set(documents))
        if unknown:
            raise EvaluationError(f"question {identifier} has unknown document IDs: {unknown}")
        result.append(Question(identifier, cohort, question, document_ids, source_ids))
    if sum(row.cohort == "hard" for row in result) != 10:
        raise EvaluationError("retrieval benchmark must contain exactly 10 hard questions")
    return result


class Ledger:
    """Validate discovery passages against exact authoritative records."""

    def __init__(self, bundle: Path, identity: Mapping[tuple[str, str], str]) -> None:
        self.bundle = bundle.resolve()
        self.path = self.bundle / "semantic" / "records.jsonl"
        self.records = load_jsonl(self.path)
        self.by_identity: dict[tuple[str, str], dict[str, Any]] = {}
        self.document_by_identity = dict(identity)
        for number, record in enumerate(self.records, 1):
            required = (
                "source_id", "record_id", "record_sha256", "concept_id", "concept_path",
                "source_path", "body", "title",
            )
            if any(not isinstance(record.get(key), str) or not record[key] for key in required):
                raise EvaluationError(f"ledger row {number} lacks required fields")
            key = (record["source_id"], record["record_id"])
            if key in self.by_identity:
                raise EvaluationError(f"duplicate ledger identity {key}")
            if key not in self.document_by_identity:
                raise EvaluationError(f"ledger identity absent from explicit document crosswalk: {key}")
            self.by_identity[key] = record
        if set(self.by_identity) != set(self.document_by_identity):
            missing = set(self.document_by_identity) - set(self.by_identity)
            raise EvaluationError(f"explicit document crosswalk is not total over ledger: {len(missing)} missing")

    def bind(self, hit: Hit) -> Hit:
        """Attach only an omitted record hash/document ID through exact ledger identity."""

        if hit.source_id is None or hit.record_id is None:
            return hit
        key = (hit.source_id, hit.record_id)
        record = self.by_identity.get(key)
        if record is None:
            return hit
        return replace(
            hit,
            document_id=self.document_by_identity[key],
            record_sha256=hit.record_sha256 or record["record_sha256"],
            record_sha256_provenance=(
                hit.record_sha256_provenance or "authoritative-ledger-identity-join"
            ),
        )

    def validate(self, hit: Hit) -> dict[str, Any]:
        """Independently reconstruct a returned evidence passage."""

        issues: list[str] = []
        if hit.source_id is None or hit.record_id is None:
            return {"valid": False, "issues": ["missing source_id or record_id"]}
        key = (hit.source_id, hit.record_id)
        record = self.by_identity.get(key)
        if record is None:
            return {"valid": False, "issues": ["unknown source-record identity"]}
        if hit.document_id != self.document_by_identity[key]:
            issues.append("document ID differs from the explicit identity crosswalk")
        for field in ("record_sha256", "concept_id", "concept_path", "source_path"):
            value = getattr(hit, field)
            if value is not None and value != record[field]:
                issues.append(f"{field} differs from authoritative ledger")
        if hit.record_sha256 != record["record_sha256"]:
            issues.append("record_sha256 is missing or invalid")
        if not isinstance(hit.text, str) or not isinstance(hit.text_sha256, str):
            issues.append("retained text or text_sha256 is missing")
        elif sha256_bytes(hit.text.encode("utf-8")) != hit.text_sha256:
            issues.append("text_sha256 does not hash retained text")
        body = record["body"]
        locator = hit.locator
        if not isinstance(locator, dict):
            issues.append("locator is missing")
        else:
            kind = locator.get("kind")
            if kind == "record":
                if hit.text != body:
                    issues.append("record locator does not retain the complete body")
            elif kind == "character-range":
                start, end = locator.get("start"), locator.get("end")
                if (
                    isinstance(start, bool) or isinstance(end, bool)
                    or not isinstance(start, int) or not isinstance(end, int)
                    or not 0 <= start < end <= len(body)
                ):
                    issues.append("character-range locator is out of bounds")
                elif hit.text != body[start:end]:
                    issues.append("retained text differs from authoritative body slice")
                target = locator.get("target")
                if target is not None and target not in {"record-body", "record.body", "source-body"}:
                    issues.append("locator target is not an authoritative record body")
            else:
                issues.append("unsupported locator kind")
        return {"valid": not issues, "issues": issues}


def numeric_score(raw: Mapping[str, Any]) -> float | None:
    """Select a finite scalar score from heterogeneous route output."""

    value = raw.get("score")
    if isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value)):
        return float(value)
    scores = raw.get("scores")
    if isinstance(scores, dict):
        values = [
            float(item) for item in scores.values()
            if isinstance(item, (int, float)) and not isinstance(item, bool) and math.isfinite(float(item))
        ]
        if values:
            return max(values)
    return None


def normalize_hits(payload: Mapping[str, Any], ledger: Ledger) -> list[Hit]:
    """Normalize one successful consult payload without trusting its derived identity."""

    if payload.get("status") != "pass":
        raise EvaluationError(f"consultation payload did not pass: {payload.get('error') or payload}")
    values = payload.get("hits") if isinstance(payload.get("hits"), list) else payload.get("results")
    if not isinstance(values, list):
        raise EvaluationError("consultation payload has no hits/results array")
    hits: list[Hit] = []
    for number, raw in enumerate(values, 1):
        if not isinstance(raw, dict):
            raise EvaluationError(f"consultation hit {number} is not an object")
        text = raw.get("text")
        if not isinstance(text, str):
            text = raw.get("authoritative_text") if isinstance(raw.get("authoritative_text"), str) else None
        text_sha = raw.get("text_sha256")
        if not isinstance(text_sha, str):
            text_sha = raw.get("authoritative_text_sha256") if isinstance(raw.get("authoritative_text_sha256"), str) else None
        hit = Hit(
            source_id=raw.get("source_id") if isinstance(raw.get("source_id"), str) else None,
            record_id=raw.get("record_id") if isinstance(raw.get("record_id"), str) else None,
            document_id=None,
            record_sha256=raw.get("record_sha256") if isinstance(raw.get("record_sha256"), str) else None,
            concept_id=raw.get("concept_id") if isinstance(raw.get("concept_id"), str) else None,
            concept_path=(raw.get("concept_path").replace("\\", "/") if isinstance(raw.get("concept_path"), str) else None),
            source_path=(raw.get("source_path").replace("\\", "/") if isinstance(raw.get("source_path"), str) else None),
            locator=raw.get("locator") if isinstance(raw.get("locator"), dict) else None,
            text=text,
            text_sha256=text_sha,
            score=numeric_score(raw),
            retrieval_id=str(raw.get("chunk_id") or raw.get("section_id") or raw.get("document_id") or number),
            record_sha256_provenance="consult-output" if isinstance(raw.get("record_sha256"), str) else None,
        )
        hits.append(ledger.bind(hit))
    return hits


def tokenize(value: str) -> list[str]:
    """Tokenize a lexical baseline query/document deterministically."""

    return [token for token in TOKEN_RE.findall(value.casefold()) if len(token) >= 2 and token not in STOPWORDS]


class LegacyIndex:
    """Evaluator-side deterministic TF-IDF baseline over authoritative records."""

    def __init__(self, ledger: Ledger) -> None:
        documents: list[tuple[Hit, Counter[str]]] = []
        document_frequency: Counter[str] = Counter()
        for record in ledger.records:
            key = (record["source_id"], record["record_id"])
            body = record["body"]
            terms = Counter(tokenize(f"{record['title']}\n{body}"))
            document_frequency.update(terms)
            documents.append(
                (
                    Hit(
                        source_id=key[0], record_id=key[1], document_id=ledger.document_by_identity[key],
                        record_sha256=record["record_sha256"], concept_id=record["concept_id"],
                        concept_path=record["concept_path"], source_path=record["source_path"],
                        locator={"kind": "record"}, text=body,
                        text_sha256=sha256_bytes(body.encode("utf-8")), score=None,
                        retrieval_id=record["concept_id"], record_sha256_provenance="authoritative-ledger",
                    ),
                    terms,
                )
            )
        count = len(documents)
        self.documents = documents
        self.idf = {
            term: math.log((count + 1) / (frequency + 1)) + 1.0
            for term, frequency in document_frequency.items()
        }

    def search(self, query: str, top_k: int) -> list[Hit]:
        """Return positive-scoring whole records in deterministic score/path order."""

        terms = set(tokenize(query))
        ranked: list[tuple[float, str, Hit]] = []
        for hit, frequencies in self.documents:
            score = sum(
                (1.0 + math.log(frequencies[term])) * self.idf.get(term, 0.0)
                for term in terms if frequencies[term]
            )
            if score > 0:
                ranked.append((score, hit.concept_path or "", replace(hit, score=score)))
        ranked.sort(key=lambda row: (-row[0], row[1]))
        return [row[2] for row in ranked[:top_k]]


def run_json(command: Sequence[str], *, timeout: float, env: Mapping[str, str]) -> dict[str, Any]:
    """Run one bounded local CLI command and parse strict JSON stdout."""

    try:
        completed = subprocess.run(
            list(command), cwd=REPO, env=dict(env), capture_output=True, text=True,
            encoding="utf-8", errors="strict", timeout=timeout, check=False,
        )
    except (OSError, UnicodeError, subprocess.TimeoutExpired) as exc:
        raise EvaluationError(f"consultation command could not run: {exc}") from exc
    if completed.returncode != 0:
        diagnostic = completed.stderr.strip() or completed.stdout.strip() or f"exit {completed.returncode}"
        raise EvaluationError(f"consultation command failed: {diagnostic[-3000:]}")
    try:
        value = json.loads(completed.stdout, object_pairs_hook=strict_object)
    except json.JSONDecodeError as exc:
        raise EvaluationError(f"consultation command emitted invalid JSON: {exc}") from exc
    if not isinstance(value, dict) or value.get("status") != "pass":
        raise EvaluationError(f"consultation command did not return status=pass: {value}")
    return value


def search_command(python: str, family: str, bundle: Path, route: str, query: str) -> list[str]:
    """Build one route-specific, no-fallback local CLI command."""

    script = REPO / CONSULT_SCRIPTS[family]
    command = [python, str(script), str(bundle), "search", "--query", query]
    if family == "ensemble":
        command.extend(["--policy", route])
    else:
        command.extend(["--mode", route])
    command.extend(["--top-k", str(RAW_POOL)])
    return command


def inspect_command(python: str, family: str, bundle: Path) -> list[str]:
    """Build one independent deep inspection command."""

    command = [python, str(REPO / CONSULT_SCRIPTS[family]), str(bundle)]
    if family in {"classical", "adaptive", "entity-graph", "ensemble"}:
        command.append("--deep-validation") if family == "ensemble" else None
    command.append("inspect")
    if family in {"classical", "adaptive", "entity-graph"}:
        command.append("--deep-validation")
    return command


def legacy_inspect_command(python: str, bundle: Path) -> list[str]:
    """Build the legacy package's complete validated-ledger inspection command."""

    return [
        python,
        str(REPO / "skills/consult-semantic-okf/scripts/query_semantic_okf.py"),
        str(bundle),
        "ledger",
        "--all",
        "--validate",
        "--format",
        "json",
    ]


def _load_module(
    name: str,
    path: Path,
    *,
    aliases: Mapping[str, ModuleType] | None = None,
) -> ModuleType:
    """Load one runtime by exact path while containing its private import aliases."""

    specification = importlib.util.spec_from_file_location(name, path)
    if specification is None or specification.loader is None:
        raise EvaluationError(f"cannot import consultation runtime: {path}")
    module = importlib.util.module_from_spec(specification)
    previous_name = sys.modules.get(name, _MISSING_MODULE)
    previous_aliases = {
        alias: sys.modules.get(alias, _MISSING_MODULE)
        for alias in (aliases or {})
    }
    sys.modules[name] = module
    for alias, dependency in (aliases or {}).items():
        sys.modules[alias] = dependency
    try:
        specification.loader.exec_module(module)
    except Exception as exc:
        if previous_name is _MISSING_MODULE:
            sys.modules.pop(name, None)
        else:
            sys.modules[name] = previous_name  # type: ignore[assignment]
        raise EvaluationError(f"cannot initialize consultation runtime {path}: {exc}") from exc
    finally:
        for alias, previous in previous_aliases.items():
            if previous is _MISSING_MODULE:
                sys.modules.pop(alias, None)
            else:
                sys.modules[alias] = previous  # type: ignore[assignment]
    return module


def _entity_runtime(scripts: Path, prefix: str) -> ModuleType:
    """Load the graph runtime with its matching model implementation."""

    model = _load_module(f"{prefix}_entity_graph_model", scripts / "_entity_graph_model.py")
    return _load_module(
        f"{prefix}_entity_graph_snapshot",
        scripts / "_entity_graph_snapshot.py",
        aliases={"_entity_graph_model": model},
    )


def _ensemble_runtime(scripts: Path) -> ModuleType:
    """Load the ensemble and its exact colocated child runtime copies."""

    adaptive = _load_module(
        "astro_ensemble_adaptive_snapshot", scripts / "_adaptive_snapshot.py"
    )
    embedding = _load_module(
        "astro_ensemble_embedding_snapshot", scripts / "_embedding_snapshot.py"
    )
    graph_model = _load_module(
        "astro_ensemble_entity_graph_model", scripts / "_entity_graph_model.py"
    )
    graph = _load_module(
        "astro_ensemble_entity_graph_snapshot",
        scripts / "_entity_graph_snapshot.py",
        aliases={"_entity_graph_model": graph_model},
    )
    return _load_module(
        "astro_ensemble_snapshot",
        scripts / "_ensemble_snapshot.py",
        aliases={
            "_adaptive_snapshot": adaptive,
            "_embedding_snapshot": embedding,
            "_entity_graph_snapshot": graph,
        },
    )


def _cached_embedding_provider(
    runtime: ModuleType, snapshot: Any
) -> Callable[[str, Mapping[str, Any]], Any] | None:
    """Eagerly load one exact offline embedding model for all family queries."""

    config = snapshot.index["embedding"]
    if config["provider"] != "sentence-transformers":
        return None
    try:
        version = importlib.metadata.version("sentence-transformers")
        required = runtime.SENTENCE_TRANSFORMERS_VERSION
        if version != required:
            raise EvaluationError(
                f"sentence-transformers {required} is required, found {version}"
            )
        model_module = __import__("sentence_transformers")
        model_class = getattr(model_module, "SentenceTransformer")
        model_path = runtime._resolve_sentence_transformer_snapshot(config)
        with runtime._offline_model_environment():
            model = model_class(
                str(model_path),
                device="cpu",
                local_files_only=True,
                trust_remote_code=False,
            )
    except EvaluationError:
        raise
    except Exception as exc:
        raise EvaluationError(
            "cannot initialize the exact pinned offline embedding model"
        ) from exc

    def encode(text: str, active: Mapping[str, Any]) -> Any:
        kwargs = {
            "normalize_embeddings": bool(active["normalize"]),
            "show_progress_bar": False,
            "convert_to_numpy": True,
        }
        with runtime._offline_model_environment():
            if active["encoding"]["query"] == "query" and callable(
                getattr(model, "encode_query", None)
            ):
                value = model.encode_query([text], **kwargs)
            else:
                value = model.encode([text], **kwargs)
        return runtime._sequence_from_model(value)

    return encode


def _load_warm_payload_searcher(
    family: str, bundle: Path
) -> Callable[[str, str], Mapping[str, Any]]:
    """Load one validated snapshot/model and return a route-aware query adapter."""

    scripts = (REPO / CONSULT_SCRIPTS[family]).parent
    if family == "embeddings":
        runtime = _load_module(
            "astro_embedding_snapshot", scripts / RUNTIME_MODULES[family]
        )
        snapshot = runtime.load_snapshot(bundle)
        embedder = _cached_embedding_provider(runtime, snapshot)
        if embedder is not None:
            embedder(EMBEDDING_WARMUP_QUERY, snapshot.index["embedding"])
        return lambda route, query: runtime.search_snapshot(
            snapshot,
            query,
            requested_mode=route,
            top_k=RAW_POOL,
            allow_fallback=False,
            embedder=embedder,
        )
    if family in {"classical", "adaptive"}:
        runtime = _load_module(
            f"astro_{family.replace('-', '_')}_snapshot",
            scripts / RUNTIME_MODULES[family],
        )
        snapshot = runtime.load_snapshot(bundle, deep_validation=True)
        return lambda route, query: runtime.search_snapshot(
            snapshot, query, route, RAW_POOL
        )
    if family == "entity-graph":
        runtime = _entity_runtime(scripts, "astro_standalone")
        snapshot = runtime.load_snapshot(bundle, deep_validation=True)
        return lambda route, query: runtime.search_snapshot(
            snapshot, query, route, RAW_POOL
        )
    if family == "ensemble":
        runtime = _ensemble_runtime(scripts)
        snapshot = runtime.load_snapshot(bundle, deep_validation=True)
        # The ensemble owns a process cache. Populate it before the query timer so
        # the same model-setup boundary applies to standalone embeddings.
        embedder = runtime._cached_embedding_provider(snapshot.embedding)
        if embedder is not None:
            embedder(
                EMBEDDING_WARMUP_QUERY,
                snapshot.embedding.index["embedding"],
            )
        return lambda route, query: runtime.search_snapshot(
            snapshot, query, route, RAW_POOL
        )
    raise EvaluationError(f"no warm runtime adapter for {family}")


def validate_route_payload(
    payload: Mapping[str, Any], family: str, route: str
) -> None:
    """Require the requested route and prohibit every declared fallback."""

    effective_key = "effective_policy" if family == "ensemble" else "effective_mode"
    if payload.get(effective_key) != route:
        raise EvaluationError(
            f"{family}/{route} changed {effective_key} to {payload.get(effective_key)!r}"
        )
    if payload.get("fallback") is not None:
        raise EvaluationError(f"{family}/{route} used a fallback")


def warm_searchers(
    family: str, bundle: Path, ledger: Ledger
) -> dict[str, Callable[[str], list[Hit]]]:
    """Expose every family route over one already-loaded, read-only runtime."""

    payload_search = _load_warm_payload_searcher(family, bundle)

    def search(route: str, query: str) -> list[Hit]:
        payload = payload_search(route, query)
        validate_route_payload(payload, family, route)
        return normalize_hits(payload, ledger)

    return {
        route: (lambda query, active=route: search(active, query))
        for route in FAMILY_ROUTES[family]
    }


def deduplicate(values: Iterable[str | None]) -> list[str]:
    """Keep the first occurrence of every nonempty identity."""

    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        if isinstance(value, str) and value and value not in seen:
            result.append(value)
            seen.add(value)
    return result


def ranking_metrics(ranked: Sequence[str], relevant: set[str]) -> dict[str, float]:
    """Compute binary recall, reciprocal rank, and normalized DCG."""

    if not relevant:
        raise EvaluationError("qrels cannot be empty")
    result = {
        f"recall_at_{cutoff}": len(set(ranked[:cutoff]) & relevant) / len(relevant)
        for cutoff in METRIC_CUTOFFS
    }
    result["mrr_at_10"] = next(
        (1.0 / rank for rank, value in enumerate(ranked[:10], 1) if value in relevant), 0.0
    )
    dcg = sum(
        1.0 / math.log2(rank + 1)
        for rank, value in enumerate(ranked[:10], 1) if value in relevant
    )
    ideal = sum(1.0 / math.log2(rank + 1) for rank in range(1, min(10, len(relevant)) + 1))
    result["ndcg_at_10"] = dcg / ideal if ideal else 0.0
    return result


def compact_hit(hit: Hit, validation: Mapping[str, Any], rank: int) -> dict[str, Any]:
    """Retain enough exact evidence for later answer-output evaluation."""

    return {
        "rank": rank,
        "source_id": hit.source_id,
        "record_id": hit.record_id,
        "document_id": hit.document_id,
        "record_sha256": hit.record_sha256,
        "record_sha256_provenance": hit.record_sha256_provenance,
        "concept_id": hit.concept_id,
        "concept_path": hit.concept_path,
        "source_path": hit.source_path,
        "locator": hit.locator,
        "text": hit.text,
        "text_sha256": hit.text_sha256,
        "score": hit.score,
        "retrieval_id": hit.retrieval_id,
        "evidence_validation": dict(validation),
    }


def evaluate_hits(question: Question, hits: Sequence[Hit], ledger: Ledger, elapsed_ms: float, error: str | None) -> dict[str, Any]:
    """Score one ranked result with evidence validity kept independent."""

    validations = [ledger.validate(hit) for hit in hits]
    documents = deduplicate(hit.document_id for hit in hits)
    sources = deduplicate(hit.source_id for hit in hits)
    return {
        "question_id": question.identifier,
        "cohort": question.cohort,
        "question": question.text,
        "qrels": {"document_ids": list(question.document_ids), "source_ids": list(question.source_ids)},
        "elapsed_ms": round(elapsed_ms, 3),
        "error": error,
        "document_metrics": ranking_metrics(documents, set(question.document_ids)),
        "source_metrics": ranking_metrics(sources, set(question.source_ids)),
        "evidence_validity": {
            "returned": len(hits),
            "valid": sum(bool(row["valid"]) for row in validations),
            "invalid": sum(not bool(row["valid"]) for row in validations),
        },
        "hits": [compact_hit(hit, validation, rank) for rank, (hit, validation) in enumerate(zip(hits, validations), 1)],
    }


def percentile(values: Sequence[float], fraction: float) -> float | None:
    """Return a linearly interpolated percentile."""

    if not values:
        return None
    ordered = sorted(values)
    position = (len(ordered) - 1) * fraction
    lower, upper = math.floor(position), math.ceil(position)
    if lower == upper:
        return float(ordered[lower])
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)


def route_summary(rows: Sequence[Mapping[str, Any]], cohort: str | None = None) -> dict[str, Any]:
    """Aggregate one route over all or one question cohort."""

    selected = [row for row in rows if cohort is None or row["cohort"] == cohort]
    names = [*(f"recall_at_{cutoff}" for cutoff in METRIC_CUTOFFS), "mrr_at_10", "ndcg_at_10"]

    def means(key: str) -> dict[str, float]:
        return {name: statistics.fmean(float(row[key][name]) for row in selected) for name in names}

    returned = sum(int(row["evidence_validity"]["returned"]) for row in selected)
    valid = sum(int(row["evidence_validity"]["valid"]) for row in selected)
    timings = [float(row["elapsed_ms"]) for row in selected]
    return {
        "query_count": len(selected),
        "error_count": sum(row["error"] is not None for row in selected),
        "document_metrics": means("document_metrics"),
        "source_metrics": means("source_metrics"),
        "evidence_validity": {
            "returned": returned, "valid": valid, "invalid": returned - valid,
            "ratio": valid / returned if returned else None,
        },
        "timing_ms": {
            "total": sum(timings),
            "mean": statistics.fmean(timings) if timings else None,
            "median": statistics.median(timings) if timings else None,
            "p95": percentile(timings, 0.95),
        },
    }


def evaluate_route(
    family: str,
    route: str,
    questions: Sequence[Question],
    ledger: Ledger,
    search: Any,
    execution: str,
) -> dict[str, Any]:
    """Run all questions through one route while retaining per-query failures."""

    rows: list[dict[str, Any]] = []
    for question in questions:
        started = time.perf_counter()
        error: str | None = None
        try:
            hits = search(question.text)
        except Exception as exc:
            if isinstance(exc, (KeyboardInterrupt, SystemExit)):
                raise
            hits = []
            error = f"{type(exc).__name__}: {exc}"
        elapsed = (time.perf_counter() - started) * 1000.0
        rows.append(evaluate_hits(question, hits, ledger, elapsed, error))
    overall, hard = route_summary(rows), route_summary(rows, "hard")
    status = "pass" if overall["error_count"] == 0 and overall["evidence_validity"]["invalid"] == 0 else "fail"
    return {
        "family": family,
        "route": route,
        "status": status,
        "execution": execution,
        "candidate_pool": RAW_POOL,
        "overall": overall,
        "hard": hard,
        "queries": rows,
    }


def evaluate_family_routes(
    family: str,
    route_names: Sequence[str],
    questions: Sequence[Question],
    ledger: Ledger,
    searchers: Mapping[str, Callable[[str], list[Hit]]],
    execution: str,
    *,
    progress: bool = False,
) -> list[dict[str, Any]]:
    """Run routes query-major so one query's bounded runtime cache remains hot."""

    rows_by_route: dict[str, list[dict[str, Any]]] = {
        route: [] for route in route_names
    }
    for question_number, question in enumerate(questions, start=1):
        for route in route_names:
            started = time.perf_counter()
            error: str | None = None
            try:
                hits = searchers[route](question.text)
            except Exception as exc:
                if isinstance(exc, (KeyboardInterrupt, SystemExit)):
                    raise
                hits = []
                error = f"{type(exc).__name__}: {exc}"
            elapsed = (time.perf_counter() - started) * 1000.0
            rows_by_route[route].append(
                evaluate_hits(question, hits, ledger, elapsed, error)
            )
        if progress and (
            question_number % 10 == 0 or question_number == len(questions)
        ):
            print(
                f"[astro-eval] {family}: {question_number}/{len(questions)} questions",
                file=sys.stderr,
                flush=True,
            )
    results: list[dict[str, Any]] = []
    for route in route_names:
        rows = rows_by_route[route]
        overall, hard = route_summary(rows), route_summary(rows, "hard")
        status = (
            "pass"
            if overall["error_count"] == 0
            and overall["evidence_validity"]["invalid"] == 0
            else "fail"
        )
        results.append(
            {
                "family": family,
                "route": route,
                "status": status,
                "execution": execution,
                "candidate_pool": RAW_POOL,
                "overall": overall,
                "hard": hard,
                "queries": rows,
            }
        )
    return results


def _route_selection_key(row: Mapping[str, Any]) -> tuple[Any, ...]:
    """Apply the frozen best-route rule consistently within and across families."""

    return (
        row["hard"]["document_metrics"]["recall_at_10"],
        row["overall"]["document_metrics"]["ndcg_at_10"],
        row["overall"]["document_metrics"]["mrr_at_10"],
        row["overall"]["evidence_validity"]["ratio"] or 0.0,
        row["route"],
    )


def standalone_route_timing(
    family: str,
    route: str,
    questions: Sequence[Question],
    search: Callable[[str], list[Hit]],
    *,
    progress: bool = False,
) -> dict[str, Any]:
    """Time the selected route alone, with no preceding sibling route per query."""

    timings: list[float] = []
    errors: list[dict[str, str]] = []
    for question_number, question in enumerate(questions, start=1):
        started = time.perf_counter()
        try:
            search(question.text)
        except Exception as exc:
            if isinstance(exc, (KeyboardInterrupt, SystemExit)):
                raise
            errors.append(
                {
                    "question_id": question.identifier,
                    "error": f"{type(exc).__name__}: {exc}",
                }
            )
        timings.append((time.perf_counter() - started) * 1000.0)
        if progress and (
            question_number % 10 == 0 or question_number == len(questions)
        ):
            print(
                f"[astro-eval] {family}/{route} standalone timing: "
                f"{question_number}/{len(questions)} questions",
                file=sys.stderr,
                flush=True,
            )
    return {
        "family": family,
        "route": route,
        "status": "pass" if not errors else "fail",
        "query_count": len(questions),
        "error_count": len(errors),
        "errors": errors,
        "execution": (
            "warm in-process selected route alone; one query at a time; "
            "no sibling-route cache priming"
        ),
        "timing_ms": {
            "total": sum(timings),
            "mean": statistics.fmean(timings) if timings else None,
            "median": statistics.median(timings) if timings else None,
            "p95": percentile(timings, 0.95),
        },
    }


def best_families(routes: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Select each family's best route under one frozen lexicographic rule."""

    result: list[dict[str, Any]] = []
    for family in FAMILY_ROUTES:
        candidates = [row for row in routes if row["family"] == family and row["status"] == "pass"]
        if not candidates:
            result.append({"family": family, "status": "fail", "best_route": None, "overall": None, "hard": None})
            continue
        winner = max(candidates, key=_route_selection_key)
        result.append(
            {
                "family": family,
                "status": winner["status"],
                "best_route": winner["route"],
                "overall": winner["overall"],
                "hard": winner["hard"],
            }
        )
    return result


def pct(value: Any) -> str:
    """Render one optional ratio as a percentage."""

    return "N/A" if value is None else f"{100.0 * float(value):.1f}%"


def number(value: Any, digits: int = 3) -> str:
    """Render one optional number."""

    return "N/A" if value is None else f"{float(value):.{digits}f}"


def render_markdown(report: Mapping[str, Any]) -> str:
    """Render family and route tables with interpretation boundaries."""

    lines = [
        "# Astro Documentation Retrieval Comparison",
        "",
        "All routes use the same 40 questions, the same explicit source-record-to-document crosswalk, a raw pool of 100, first-occurrence document deduplication, and independent validation against `semantic/records.jsonl`. Ranking and evidence validity are separate gates.",
        "",
        "## Best route by knowledge builder/consult alternative",
        "",
        "| Family | Best route | Recall@10 | Hard Recall@10 | MRR@10 | nDCG@10 | Evidence valid | Mean ms | p95 ms |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in report["families"]:
        if row["best_route"] is None:
            lines.append(f"| {row['family']} | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |")
            continue
        overall = row["overall"]
        metrics = overall["document_metrics"]
        timing = report["standalone_best_route_timing"][row["family"]]["timing_ms"]
        lines.append(
            f"| {row['family']} | {row['best_route']} | {pct(metrics['recall_at_10'])} | "
            f"{pct(row['hard']['document_metrics']['recall_at_10'])} | {number(metrics['mrr_at_10'])} | "
            f"{number(metrics['ndcg_at_10'])} | {pct(overall['evidence_validity']['ratio'])} | "
            f"{number(timing['mean'], 1)} | {number(timing['p95'], 1)} |"
        )
    lines.extend(
        [
            "",
            "## Every consultation route",
            "",
            "| Family | Route | Status | R@1 | R@3 | R@5 | R@10 | R@20 | Hard R@10 | MRR@10 | nDCG@10 | Evidence valid | Marginal mean ms |",
            "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in report["routes"]:
        metrics, overall = row["overall"]["document_metrics"], row["overall"]
        lines.append(
            f"| {row['family']} | {row['route']} | {row['status']} | {pct(metrics['recall_at_1'])} | "
            f"{pct(metrics['recall_at_3'])} | {pct(metrics['recall_at_5'])} | {pct(metrics['recall_at_10'])} | "
            f"{pct(metrics['recall_at_20'])} | {pct(row['hard']['document_metrics']['recall_at_10'])} | "
            f"{number(metrics['mrr_at_10'])} | {number(metrics['ndcg_at_10'])} | "
            f"{pct(overall['evidence_validity']['ratio'])} | {number(overall['timing_ms']['mean'], 1)} |"
        )
    lines.extend(
        [
            "",
            "The legacy row is an evaluator-side deterministic TF-IDF baseline because the legacy consult skill exposes ledger/SPARQL reads but no ranked natural-language-search command. It does not invoke `grep` or `rg`.",
            "",
            "The best-family table uses a second pass that times only the selected route, one query at a time, without sibling-route cache priming. Those standalone numbers are comparable. The every-route table retains query-major marginal timings used during metric collection; because later sibling routes can reuse bounded computation from the same query, those marginal timings are diagnostic and are not comparable as standalone route latency. Deep CLI inspection and one-time setup are excluded and reported separately.",
            "",
            "All derived indexes are discovery-only. A high ranking score does not make a passage authoritative; only the separately checked ledger locator and hash establish evidence validity. No MCP participates.",
            "",
        ]
    )
    return "\n".join(lines)


def evaluate(args: argparse.Namespace) -> dict[str, Any]:
    """Execute every compatible route and enforce read-only bundle identity."""

    identity, documents = load_identity_map(args.source_combination)
    questions = load_questions(args.questions, documents)
    routes: list[dict[str, Any]] = []
    inspections: dict[str, Any] = {}
    read_only: dict[str, Any] = {}
    runtime_setup: dict[str, Any] = {}
    standalone_best_route_timing: dict[str, dict[str, Any]] = {}
    env = dict(os.environ)
    env.update({"PYTHONDONTWRITEBYTECODE": "1", "HF_HUB_OFFLINE": "1", "TRANSFORMERS_OFFLINE": "1"})
    for family, route_names in FAMILY_ROUTES.items():
        print(
            f"[astro-eval] {family}: validating and loading one warm runtime",
            file=sys.stderr,
            flush=True,
        )
        bundle = args.run_dir / "bundles" / f"{family}-a"
        if not bundle.is_dir():
            raise EvaluationError(f"missing compatible bundle for {family}: {bundle}")
        ledger = Ledger(bundle, identity)
        before = bundle_identity(bundle)
        if family == "legacy":
            inspected = run_json(
                legacy_inspect_command(args.python, bundle), timeout=args.timeout, env=env
            )
            setup_started = time.perf_counter()
            index = LegacyIndex(ledger)
            setup_ms = (time.perf_counter() - setup_started) * 1000.0
            inspections[family] = {
                "status": "pass",
                "kind": "complete validated authoritative ledger CLI read",
                "record_count": len(inspected.get("records", [])),
            }
            runtime_setup[family] = {
                "elapsed_ms": round(setup_ms, 3),
                "snapshot_loads": 1,
                "model_loads": 0,
                "model_inference_warmup": False,
                "included_in_query_timings": False,
            }
            family_routes = evaluate_family_routes(
                    family,
                    route_names,
                    questions,
                    ledger,
                    {route_names[0]: lambda query: index.search(query, RAW_POOL)},
                    "warm in-process evaluator-side TF-IDF; one prebuilt index; query-major execution",
                    progress=True,
                )
            routes.extend(family_routes)
            only_route = family_routes[0]
            standalone_best_route_timing[family] = {
                "family": family,
                "route": only_route["route"],
                "status": only_route["status"],
                "query_count": only_route["overall"]["query_count"],
                "error_count": only_route["overall"]["error_count"],
                "errors": [],
                "execution": "same sole-route pass; no sibling route exists",
                "timing_ms": only_route["overall"]["timing_ms"],
            }
        else:
            inspections[family] = run_json(
                inspect_command(args.python, family, bundle), timeout=args.timeout, env=env
            )
            setup_started = time.perf_counter()
            searchers = warm_searchers(family, bundle, ledger)
            setup_ms = (time.perf_counter() - setup_started) * 1000.0
            runtime_setup[family] = {
                "elapsed_ms": round(setup_ms, 3),
                "snapshot_loads": 1,
                "model_loads": 1 if family in {"embeddings", "ensemble"} else 0,
                "model_inference_warmup": family in {"embeddings", "ensemble"},
                "included_in_query_timings": False,
            }
            family_routes = evaluate_family_routes(
                    family,
                    route_names,
                    questions,
                    ledger,
                    searchers,
                    "warm in-process; one deep-validated snapshot/model per family; query-major bounded-cache execution; no fallback",
                    progress=True,
                )
            routes.extend(family_routes)
            passing = [row for row in family_routes if row["status"] == "pass"]
            if passing:
                winner = max(passing, key=_route_selection_key)
                print(
                    f"[astro-eval] {family}: timing selected route {winner['route']} alone",
                    file=sys.stderr,
                    flush=True,
                )
                standalone_best_route_timing[family] = standalone_route_timing(
                    family,
                    winner["route"],
                    questions,
                    searchers[winner["route"]],
                    progress=True,
                )
            else:
                standalone_best_route_timing[family] = {
                    "family": family,
                    "route": None,
                    "status": "fail",
                    "query_count": 0,
                    "error_count": 1,
                    "errors": [{"question_id": "*", "error": "no passing route"}],
                    "execution": "not run",
                    "timing_ms": {"total": 0.0, "mean": None, "median": None, "p95": None},
                }
        after = bundle_identity(bundle)
        read_only[family] = {"before": before, "after": after, "unchanged": before == after}
        if before != after:
            raise EvaluationError(f"{family} consultation modified its published bundle")
        print(
            f"[astro-eval] {family}: complete ({len(route_names)} routes)",
            file=sys.stderr,
            flush=True,
        )
    families = best_families(routes)
    status = "pass" if (
        all(row["status"] == "pass" for row in routes)
        and all(row["best_route"] is not None for row in families)
        and all(
            row["status"] == "pass"
            for row in standalone_best_route_timing.values()
        )
    ) else "fail"
    return {
        "schema_version": SCHEMA,
        "status": status,
        "benchmark": {
            "questions_path": args.questions.relative_to(REPO).as_posix(),
            "questions_sha256": sha256_file(args.questions),
            "question_count": len(questions),
            "hard_question_count": sum(row.cohort == "hard" for row in questions),
            "candidate_pool": RAW_POOL,
            "primary_identity": "explicit document_id joined only through source-combination.json",
            "deduplication": "first occurrence before metric cutoff",
        },
        "run_dir": args.run_dir.relative_to(REPO).as_posix(),
        "source_combination": {
            "path": args.source_combination.relative_to(REPO).as_posix(),
            "sha256": sha256_file(args.source_combination),
            "record_count": len(identity),
        },
        "timing_interpretation": {
            "all_routes": "query-major marginal latency after one family setup; later sibling routes may reuse an exact bounded computation and are not standalone-latency comparable",
            "standalone_best_route": "second pass over the selected route alone, warm in-process, with no sibling-route cache priming; used for the family comparison table",
            "comparability": "only standalone_best_route_timing values are compared as route latency; one-time setup latency is reported separately",
        },
        "inspections": inspections,
        "runtime_setup": runtime_setup,
        "standalone_best_route_timing": standalone_best_route_timing,
        "read_only": read_only,
        "routes": routes,
        "families": families,
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse evaluation arguments."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--questions", type=Path, default=EVALUATION / "benchmark/retrieval-questions.jsonl")
    parser.add_argument("--source-combination", type=Path, default=EVALUATION / "corpus/source-combination.json")
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--timeout", type=float, default=240.0)
    parser.add_argument("--raw-output", type=Path)
    parser.add_argument("--compact-json", type=Path, default=REPORTS / "retrieval-comparison.json")
    parser.add_argument("--compact-markdown", type=Path, default=REPORTS / "retrieval-comparison.md")
    args = parser.parse_args(argv)
    for name in ("run_dir", "questions", "source_combination", "compact_json", "compact_markdown"):
        setattr(args, name, getattr(args, name).resolve())
    args.raw_output = (
        args.raw_output.resolve() if args.raw_output is not None
        else args.run_dir / "retrieval" / "detailed-report.json"
    )
    if not args.run_dir.is_dir():
        parser.error(f"run directory does not exist: {args.run_dir}")
    if args.timeout <= 0:
        parser.error("--timeout must be positive")
    return args


def main(argv: Sequence[str] | None = None) -> int:
    """Run the comparison and publish raw/compact reports."""

    args = parse_args(argv)
    try:
        report = evaluate(args)
        append_only_write(args.raw_output, pretty_json(report))
        compact = dict(report)
        compact["routes"] = [
            {key: value for key, value in row.items() if key != "queries"}
            for row in report["routes"]
        ]
        atomic_write(args.compact_json, pretty_json(compact))
        atomic_write(args.compact_markdown, render_markdown(compact))
    except (EvaluationError, OSError, UnicodeError, ValueError, TypeError, KeyError) as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1
    print(json.dumps({"status": report["status"], "routes": len(report["routes"]), "raw": str(args.raw_output)}))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
