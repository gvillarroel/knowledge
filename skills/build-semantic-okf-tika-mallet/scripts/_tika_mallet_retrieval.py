#!/usr/bin/env python3
"""Build and validate Java MALLET retrieval artifacts for Tika Semantic OKF."""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import subprocess
import tempfile
import zipfile
from collections import Counter
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Mapping, Sequence

from _semantic_okf import validate_semantic_bundle
from _safe_paths import (
    UnsafePathError,
    file_identity,
    require_identity,
    require_real_directory,
    require_regular_file,
    scan_regular_tree,
)


SCHEMA_VERSION = "1.0"
STOPWORDS_ID = "english-v1"
TOKENIZER_ID = "ascii-alphanumeric-v1"
TOKEN_RE = re.compile(r"[a-z0-9]+", re.ASCII | re.IGNORECASE)
PAGE_RE = re.compile(r"(?m)^## PDF page \d+\s*$")
PAPER_RE = re.compile(r"(?<!\d)(\d{4})[.-](\d{5}v\d+)(?!\d)", re.IGNORECASE)
HEX_64 = re.compile(r"[0-9a-f]{64}")
DOCUMENT_KEYS = {
    "document_id",
    "source_id",
    "record_id",
    "record_sha256",
    "concept_id",
    "concept_type",
    "concept_path",
    "source_path",
    "paper_id",
    "ordinal",
    "locator",
    "title",
    "text",
    "text_sha256",
    "title_terms",
    "body_terms",
    "title_length",
    "body_length",
    "topic_weights",
}
PLAN_KEYS = {
    "schema_version",
    "selection",
    "tokenization",
    "bm25",
    "associations",
    "topics",
    "expansion",
    "reranking",
}
ARTIFACT_NAMES = {
    "documents": "classical/documents.jsonl",
    "lexicon": "classical/lexicon.json",
    "associations": "classical/associations.jsonl",
    "topics": "classical/topics.json",
}
ALGORITHMS = {
    "bm25": "okapi-bm25f-v1",
    "associations": "windowed-positive-pmi-v1",
    "topics": "mallet-2.1.0-parallel-topic-model-v1",
    "topic_scoring": "normalized-bm25-plus-topic-cosine-v1",
    "association_scoring": "two-step-ppmi-query-propagation-v1",
    "fusion": "reciprocal-rank-fusion-v1",
    "reranking": "topic-and-source-mmr-v1",
}
STOPWORDS = frozenset(
    "a about above after again against all am an and any are as at be because been before being below "
    "between both but by can could did do does doing down during each few for from further had has have "
    "having he her here hers herself him himself his how i if in into is it its itself just me more most "
    "my myself no nor not now of off on once only or other our ours ourselves out over own same she should "
    "so some such than that the their theirs them themselves then there these they this those through to too "
    "under until up very was we were what when where which while who whom why will with you your yours "
    "yourself yourselves".split()
)


class ClassicalError(RuntimeError):
    """Describe an invalid plan, projection, or atomic classical build."""


@dataclass(frozen=True)
class ClassicalPlan:
    """Hold one validated closed classical-retrieval plan."""

    raw: dict[str, Any]
    sha256: str
    source_ids: tuple[str, ...]


@dataclass(frozen=True)
class MalletRuntime:
    """Describe the exact Java and MALLET runtime used for topic training."""

    java: Path
    java_version: str
    mallet_home: Path
    mallet_version: str
    jar_inventory: tuple[dict[str, str], ...]
    jar_tree_sha256: str
    java_identity: tuple[int, int] | None = None
    home_identity: tuple[int, int] | None = None

    def payload(self) -> dict[str, Any]:
        """Return the path-independent runtime binding stored in the projection."""

        return {
            "java_version": self.java_version,
            "mallet_jar_inventory": list(self.jar_inventory),
            "mallet_jar_tree_sha256": self.jar_tree_sha256,
            "mallet_version": self.mallet_version,
        }


def canonical_json(value: Any) -> str:
    """Serialize JSON deterministically and reject non-finite numbers."""

    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def sha256_bytes(value: bytes) -> str:
    """Return a lowercase SHA-256 digest for bytes."""

    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    """Return a lowercase SHA-256 digest for one file."""

    try:
        path = require_regular_file(path, label="file to hash")
    except UnsafePathError as exc:
        raise ClassicalError(str(exc)) from exc
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_canonical(value: Any) -> str:
    """Hash deterministic UTF-8 JSON."""

    return sha256_bytes(canonical_json(value).encode("utf-8"))


def _normalize_output(value: str) -> str:
    return value.replace("\r\n", "\n").replace("\r", "\n")


def _run_java(
    command: Sequence[str], *, cwd: Path, timeout: int, label: str
) -> tuple[str, str, int]:
    """Run Java without a shell and decode its output strictly as UTF-8."""

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
        raise ClassicalError(f"{label} failed to execute: {exc}") from exc
    try:
        stdout = _normalize_output(completed.stdout.decode("utf-8", errors="strict"))
        stderr = _normalize_output(completed.stderr.decode("utf-8", errors="strict"))
    except UnicodeDecodeError as exc:
        raise ClassicalError(f"{label} did not emit valid UTF-8") from exc
    return stdout, stderr, completed.returncode


def preflight_mallet(java: Path, mallet_home: Path) -> MalletRuntime:
    """Require Java 17+ and the exact MALLET 2.1.0 binary layout."""

    try:
        java_path = require_regular_file(java, label="Java executable")
        home = require_real_directory(mallet_home, label="MALLET home")
    except UnsafePathError as exc:
        raise ClassicalError(str(exc)) from exc
    library = home / "lib"
    main_jar = library / "mallet-2.1.0.jar"
    inventory, inventory_sha256 = _mallet_inventory(home)
    try:
        main_jar = require_regular_file(main_jar, label="MALLET main jar")
    except UnsafePathError as exc:
        raise ClassicalError(str(exc)) from exc
    stdout, stderr, returncode = _run_java(
        [str(java_path), "-version"], cwd=home, timeout=60, label="Java preflight"
    )
    if returncode != 0:
        raise ClassicalError("Java preflight failed")
    java_version = (stdout or stderr).strip()
    match = re.search(r'version "(\d+)(?:\.|\")', java_version)
    if not match or int(match.group(1)) < 17:
        raise ClassicalError("Java 17 or later is required")
    try:
        with zipfile.ZipFile(main_jar) as archive:
            names = set(archive.namelist())
    except (OSError, zipfile.BadZipFile) as exc:
        raise ClassicalError(f"MALLET main jar is unreadable: {exc}") from exc
    required_classes = {
        "cc/mallet/classify/tui/Csv2Vectors.class",
        "cc/mallet/topics/tui/TopicTrainer.class",
        "cc/mallet/topics/ParallelTopicModel.class",
    }
    if not required_classes.issubset(names):
        raise ClassicalError("MALLET main jar lacks required import or topic classes")
    return MalletRuntime(
        java=java_path,
        java_version=java_version,
        mallet_home=home,
        mallet_version="2.1.0",
        jar_inventory=inventory,
        jar_tree_sha256=inventory_sha256,
        java_identity=file_identity(java_path),
        home_identity=file_identity(home),
    )


def _mallet_inventory(home: Path) -> tuple[tuple[dict[str, str], ...], str]:
    """Bind exactly the closed, immediate MALLET lib jar classpath."""

    library = home / "lib"
    try:
        files, directories = scan_regular_tree(library, label="MALLET lib directory")
    except UnsafePathError as exc:
        raise ClassicalError(str(exc)) from exc
    if directories or any(path.parent != library for path in files):
        raise ClassicalError("MALLET lib must contain only immediate jar files")
    if any(path.suffix.casefold() != ".jar" for path in files):
        raise ClassicalError("MALLET lib contains a non-jar classpath entry")
    rows = tuple(
        {
            "path": path.relative_to(home).as_posix(),
            "sha256": sha256_file(path),
        }
        for path in files
    )
    if not rows or not any(row["path"] == "lib/mallet-2.1.0.jar" for row in rows):
        raise ClassicalError("MALLET jar inventory is incomplete")
    return rows, sha256_canonical(list(rows))


def _verify_mallet_runtime(runtime: MalletRuntime) -> None:
    """Reject runtime identity or classpath changes after preflight."""

    if runtime.java_identity is None or runtime.home_identity is None:
        return
    try:
        require_identity(runtime.java, runtime.java_identity, label="Java executable")
        require_identity(runtime.mallet_home, runtime.home_identity, label="MALLET home")
    except UnsafePathError as exc:
        raise ClassicalError(str(exc)) from exc
    inventory, tree_sha256 = _mallet_inventory(runtime.mallet_home)
    if inventory != runtime.jar_inventory or tree_sha256 != runtime.jar_tree_sha256:
        raise ClassicalError("MALLET jar classpath changed after preflight")


def strict_json_loads(payload: str, *, label: str) -> Any:
    """Load JSON while rejecting duplicate keys and non-standard numbers."""

    def reject_constant(value: str) -> Any:
        raise ClassicalError(f"{label} contains non-standard number {value!r}")

    def reject_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ClassicalError(f"{label} contains duplicate member {key!r}")
            result[key] = value
        return result

    try:
        return json.loads(
            payload,
            object_pairs_hook=reject_duplicates,
            parse_constant=reject_constant,
        )
    except json.JSONDecodeError as exc:
        raise ClassicalError(f"{label} is invalid JSON: {exc}") from exc


def _exact_keys(value: Mapping[str, Any], expected: set[str], label: str) -> None:
    actual = set(value)
    if actual != expected:
        raise ClassicalError(
            f"{label} has a closed schema; missing={sorted(expected - actual)}, "
            f"unknown={sorted(actual - expected)}"
        )


def _plain_int(value: Any, label: str, minimum: int, maximum: int) -> int:
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or not minimum <= value <= maximum
    ):
        raise ClassicalError(
            f"{label} must be an integer from {minimum} through {maximum}"
        )
    return value


def _finite(value: Any, label: str, minimum: float, maximum: float) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ClassicalError(f"{label} must be numeric")
    result = float(value)
    if not math.isfinite(result) or not minimum <= result <= maximum:
        raise ClassicalError(f"{label} must be finite from {minimum} through {maximum}")
    return result


def _parse_plan(value: Any) -> ClassicalPlan:
    if not isinstance(value, dict):
        raise ClassicalError("classical plan root must be an object")
    _exact_keys(value, PLAN_KEYS, "classical plan")
    if value["schema_version"] != SCHEMA_VERSION:
        raise ClassicalError(f"classical plan schema_version must be {SCHEMA_VERSION}")

    selection = value["selection"]
    if not isinstance(selection, dict):
        raise ClassicalError("plan.selection must be an object")
    _exact_keys(selection, {"source_ids"}, "plan.selection")
    source_ids = selection["source_ids"]
    if (
        not isinstance(source_ids, list)
        or not source_ids
        or any(not isinstance(item, str) or not item for item in source_ids)
        or source_ids != sorted(set(source_ids))
    ):
        raise ClassicalError(
            "plan.selection.source_ids must be a sorted unique non-empty string array"
        )

    tokenization = value["tokenization"]
    if not isinstance(tokenization, dict):
        raise ClassicalError("plan.tokenization must be an object")
    _exact_keys(
        tokenization,
        {"tokenizer", "stopwords", "min_token_length", "ngram_range"},
        "plan.tokenization",
    )
    if (
        tokenization["tokenizer"] != TOKENIZER_ID
        or tokenization["stopwords"] != STOPWORDS_ID
    ):
        raise ClassicalError(
            "the portable plan requires the bundled tokenizer and stopword identities"
        )
    _plain_int(tokenization["min_token_length"], "min_token_length", 1, 12)
    ngram_range = tokenization["ngram_range"]
    if ngram_range not in ([1, 1], [1, 2]):
        raise ClassicalError("plan.tokenization.ngram_range must be [1,1] or [1,2]")

    bm25 = value["bm25"]
    if not isinstance(bm25, dict):
        raise ClassicalError("plan.bm25 must be an object")
    _exact_keys(bm25, {"k1", "b", "title_weight", "body_weight"}, "plan.bm25")
    _finite(bm25["k1"], "plan.bm25.k1", 0.01, 10.0)
    _finite(bm25["b"], "plan.bm25.b", 0.0, 1.0)
    _finite(bm25["title_weight"], "plan.bm25.title_weight", 0.0, 100.0)
    _finite(bm25["body_weight"], "plan.bm25.body_weight", 0.0, 100.0)
    if float(bm25["title_weight"]) + float(bm25["body_weight"]) <= 0:
        raise ClassicalError("at least one BM25 field weight must be positive")

    associations = value["associations"]
    if not isinstance(associations, dict):
        raise ClassicalError("plan.associations must be an object")
    _exact_keys(
        associations,
        {
            "window_size",
            "min_document_frequency",
            "min_cooccurrence",
            "max_vocabulary",
            "max_neighbors",
            "minimum_ppmi",
        },
        "plan.associations",
    )
    _plain_int(associations["window_size"], "window_size", 2, 64)
    _plain_int(
        associations["min_document_frequency"], "min_document_frequency", 1, 1000000
    )
    _plain_int(associations["min_cooccurrence"], "min_cooccurrence", 1, 1000000)
    _plain_int(associations["max_vocabulary"], "max_vocabulary", 32, 50000)
    _plain_int(associations["max_neighbors"], "max_neighbors", 1, 128)
    _finite(associations["minimum_ppmi"], "minimum_ppmi", 0.0, 100.0)

    topics = value["topics"]
    if not isinstance(topics, dict):
        raise ClassicalError("plan.topics must be an object")
    _exact_keys(
        topics,
        {
            "topic_count",
            "num_iterations",
            "num_threads",
            "num_icm_iterations",
            "optimize_interval",
            "optimize_burn_in",
            "alpha_sum",
            "beta",
            "random_seed",
            "min_document_frequency",
            "max_document_fraction",
            "top_terms",
            "timeout_seconds",
        },
        "plan.topics",
    )
    _plain_int(topics["topic_count"], "topic_count", 2, 128)
    num_iterations = _plain_int(
        topics["num_iterations"], "num_iterations", 1, 10000
    )
    if topics["num_threads"] != 1:
        raise ClassicalError("plan.topics.num_threads must be 1 for reproducibility")
    _plain_int(topics["num_threads"], "num_threads", 1, 1)
    _plain_int(topics["num_icm_iterations"], "num_icm_iterations", 0, 10000)
    _plain_int(topics["optimize_interval"], "optimize_interval", 0, 10000)
    optimize_burn_in = _plain_int(
        topics["optimize_burn_in"], "optimize_burn_in", 0, 10000
    )
    if optimize_burn_in > num_iterations:
        raise ClassicalError(
            "plan.topics.optimize_burn_in cannot exceed num_iterations"
        )
    _finite(topics["alpha_sum"], "alpha_sum", 0.000000001, 10000.0)
    _finite(topics["beta"], "beta", 0.000000001, 100.0)
    _plain_int(topics["random_seed"], "random_seed", 1, 2147483647)
    _plain_int(
        topics["min_document_frequency"],
        "min_document_frequency",
        1,
        1000000,
    )
    _finite(topics["max_document_fraction"], "max_document_fraction", 0.000000001, 1.0)
    _plain_int(topics["top_terms"], "top_terms", 3, 100)
    _plain_int(topics["timeout_seconds"], "timeout_seconds", 1, 3600)

    expansion = value["expansion"]
    if not isinstance(expansion, dict):
        raise ClassicalError("plan.expansion must be an object")
    _exact_keys(
        expansion,
        {"association_terms", "topic_terms", "association_weight", "topic_weight"},
        "plan.expansion",
    )
    _plain_int(expansion["association_terms"], "association_terms", 0, 64)
    _plain_int(expansion["topic_terms"], "topic_terms", 0, 64)
    _finite(expansion["association_weight"], "association_weight", 0.0, 1.0)
    _finite(expansion["topic_weight"], "topic_weight", 0.0, 1.0)

    reranking = value["reranking"]
    if not isinstance(reranking, dict):
        raise ClassicalError("plan.reranking must be an object")
    _exact_keys(
        reranking,
        {
            "candidate_pool",
            "relevance_weight",
            "topic_novelty_weight",
            "source_novelty_weight",
            "max_per_evidence_identity",
            "rrf_k",
        },
        "plan.reranking",
    )
    _plain_int(reranking["candidate_pool"], "candidate_pool", 10, 10000)
    _plain_int(
        reranking["max_per_evidence_identity"], "max_per_evidence_identity", 1, 100
    )
    _plain_int(reranking["rrf_k"], "rrf_k", 1, 10000)
    weights = [
        _finite(reranking[name], f"plan.reranking.{name}", 0.0, 1.0)
        for name in (
            "relevance_weight",
            "topic_novelty_weight",
            "source_novelty_weight",
        )
    ]
    if not math.isclose(sum(weights), 1.0, rel_tol=0.0, abs_tol=1e-9):
        raise ClassicalError("reranking relevance/topic/source weights must sum to 1")
    raw = json.loads(canonical_json(value))
    return ClassicalPlan(
        raw=raw, sha256=sha256_canonical(raw), source_ids=tuple(source_ids)
    )


def load_plan(path: Path) -> ClassicalPlan:
    """Load and validate one closed classical-retrieval plan."""

    try:
        checked = require_regular_file(path, label="classical retrieval plan")
        value = strict_json_loads(checked.read_text(encoding="utf-8"), label=str(checked))
    except (OSError, UnicodeError, UnsafePathError) as exc:
        raise ClassicalError(f"cannot read classical plan at {path}: {exc}") from exc
    return _parse_plan(value)


def _safe_relative(value: str, label: str) -> PurePosixPath:
    candidate = PurePosixPath(value.replace("\\", "/"))
    if (
        candidate.is_absolute()
        or not candidate.parts
        or any(part in {"", ".", ".."} for part in candidate.parts)
    ):
        raise ClassicalError(f"{label} is not a safe relative path: {value!r}")
    return candidate


def _read_jsonl(path: Path, *, label: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        raise ClassicalError(f"cannot read {label}: {exc}") from exc
    for number, line in enumerate(lines, start=1):
        if not line:
            raise ClassicalError(f"{label}:{number} is blank")
        value = strict_json_loads(line, label=f"{label}:{number}")
        if not isinstance(value, dict):
            raise ClassicalError(f"{label}:{number} must be an object")
        rows.append(value)
    return rows


def _write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False)
        + "\n",
        encoding="utf-8",
    )


def _write_jsonl(path: Path, rows: Iterable[Mapping[str, Any]]) -> None:
    path.write_text(
        "".join(canonical_json(dict(row)) + "\n" for row in rows),
        encoding="utf-8",
    )


def _core_inventory(root: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    try:
        files, _ = scan_regular_tree(root, label="Semantic OKF bundle")
    except UnsafePathError as exc:
        raise ClassicalError(str(exc)) from exc
    for path in files:
        relative = path.relative_to(root)
        if relative.parts and relative.parts[0] == "classical":
            continue
        rows.append({"path": relative.as_posix(), "sha256": sha256_file(path)})
    return rows


def _core_tree_sha256(root: Path) -> str:
    return sha256_canonical(_core_inventory(root))


def _load_core(root: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    records = _read_jsonl(
        root / "semantic" / "records.jsonl", label="semantic/records.jsonl"
    )
    try:
        source_manifest = strict_json_loads(
            (root / "semantic" / "source-manifest.json").read_text(encoding="utf-8"),
            label="semantic/source-manifest.json",
        )
    except (OSError, UnicodeError) as exc:
        raise ClassicalError(
            f"cannot read semantic/source-manifest.json: {exc}"
        ) from exc
    sources = (
        source_manifest.get("sources") if isinstance(source_manifest, dict) else None
    )
    if not isinstance(sources, list) or any(
        not isinstance(item, dict) for item in sources
    ):
        raise ClassicalError(
            "semantic/source-manifest.json must contain an object source array"
        )
    return records, sources


def _selection(
    records: Sequence[dict[str, Any]],
    sources: Sequence[dict[str, Any]],
    plan: ClassicalPlan,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    source_by_id = {
        str(source["id"]): source
        for source in sources
        if isinstance(source.get("id"), str) and source["id"]
    }
    missing = sorted(set(plan.source_ids) - set(source_by_id))
    if missing:
        raise ClassicalError(f"classical plan selects unknown source IDs: {missing}")
    selected = [
        record for record in records if record.get("source_id") in set(plan.source_ids)
    ]
    eligible = sorted({str(record.get("source_id")) for record in selected})
    if eligible != list(plan.source_ids):
        absent = sorted(set(plan.source_ids) - set(eligible))
        raise ClassicalError(
            f"selected source IDs produced no eligible records: {absent}"
        )
    inventory = [
        {
            "source_id": source_id,
            "content_sha256": source_by_id[source_id].get("content_sha256"),
        }
        for source_id in eligible
    ]
    if any(not HEX_64.fullmatch(str(row["content_sha256"])) for row in inventory):
        raise ClassicalError(
            "selected source inventory contains an invalid content digest"
        )
    selection = {
        "requested_source_ids": list(plan.source_ids),
        "eligible_source_ids": eligible,
        "excluded_source_ids": sorted(set(source_by_id) - set(plan.source_ids)),
        "input_count": len(inventory),
        "input_sha256": sha256_canonical(inventory),
    }
    return sorted(
        selected, key=lambda row: (str(row.get("source_id")), str(row.get("record_id")))
    ), selection


def _unigrams(value: str, plan: ClassicalPlan) -> list[str]:
    minimum = int(plan.raw["tokenization"]["min_token_length"])
    return [
        token
        for token in TOKEN_RE.findall(value.casefold())
        if len(token) >= minimum and token not in STOPWORDS
    ]


def tokenize(value: str, plan: ClassicalPlan) -> list[str]:
    """Tokenize text into the plan's deterministic bag-of-words features."""

    words = _unigrams(value, plan)
    if plan.raw["tokenization"]["ngram_range"] == [1, 1]:
        return words
    return [*words, *(f"{left} {right}" for left, right in zip(words, words[1:]))]


def _paper_id(record: Mapping[str, Any]) -> str | None:
    for value in (
        record.get("source_id"),
        record.get("record_id"),
        record.get("source_path"),
        record.get("title"),
    ):
        if isinstance(value, str):
            match = PAPER_RE.search(value)
            if match:
                return f"{match.group(1)}.{match.group(2).lower()}"
    return None


def _trimmed_range(body: str, start: int, end: int) -> tuple[int, int] | None:
    while start < end and body[start].isspace():
        start += 1
    while end > start and body[end - 1].isspace():
        end -= 1
    return (start, end) if start < end else None


def _passage_ranges(record: Mapping[str, Any]) -> list[tuple[int, int]]:
    body = str(record.get("body") or "")
    matches = list(PAGE_RE.finditer(body))
    if not matches:
        trimmed = _trimmed_range(body, 0, len(body))
        return [trimmed] if trimmed is not None else []
    starts = [0, *(match.start() for match in matches[1:])]
    ends = [*(match.start() for match in matches[1:]), len(body)]
    return [
        item
        for pair in zip(starts, ends, strict=True)
        if (item := _trimmed_range(body, *pair))
    ]


def _document_id(row: Mapping[str, Any]) -> str:
    identity = {
        "source_id": row["source_id"],
        "record_id": row["record_id"],
        "record_sha256": row["record_sha256"],
        "ordinal": row["ordinal"],
        "text_sha256": row["text_sha256"],
    }
    return "document-" + sha256_canonical(identity)[:32]


def _counter_object(tokens: Sequence[str]) -> dict[str, int]:
    return dict(sorted(Counter(tokens).items()))


def _derive_documents(
    records: Sequence[dict[str, Any]], plan: ClassicalPlan
) -> list[dict[str, Any]]:
    documents: list[dict[str, Any]] = []
    for record in records:
        required = (
            "source_id",
            "record_id",
            "record_sha256",
            "concept_id",
            "concept_type",
            "concept_path",
            "source_path",
            "title",
            "body",
        )
        if any(
            not isinstance(record.get(name), str) or not record[name]
            for name in required
        ):
            raise ClassicalError(
                "selected authoritative record has an invalid required identity or body"
            )
        concept_path = str(record["concept_path"]).replace("\\", "/")
        safe = _safe_relative(concept_path, "record concept_path")
        if safe.parts[0] != "concepts":
            raise ClassicalError(
                f"record concept_path is outside concepts/: {concept_path}"
            )
        body = str(record["body"])
        ranges = _passage_ranges(record)
        if not ranges:
            raise ClassicalError(
                f"record {record['source_id']}/{record['record_id']} has no indexable text"
            )
        for ordinal, (start, end) in enumerate(ranges):
            text = body[start:end]
            locator: dict[str, Any]
            if start == 0 and end == len(body):
                locator = {"kind": "record"}
            else:
                locator = {"kind": "character-range", "start": start, "end": end}
            title = str(record["title"])
            title_tokens = tokenize(title, plan)
            body_tokens = tokenize(text, plan)
            row: dict[str, Any] = {
                "document_id": "",
                "source_id": str(record["source_id"]),
                "record_id": str(record["record_id"]),
                "record_sha256": str(record["record_sha256"]),
                "concept_id": str(record["concept_id"]),
                "concept_type": str(record["concept_type"]),
                "concept_path": concept_path,
                "source_path": str(record["source_path"]).replace("\\", "/"),
                "paper_id": _paper_id(record),
                "ordinal": ordinal,
                "locator": locator,
                "title": title,
                "text": text,
                "text_sha256": sha256_bytes(text.encode("utf-8")),
                "title_terms": _counter_object(title_tokens),
                "body_terms": _counter_object(body_tokens),
                "title_length": len(title_tokens),
                "body_length": len(body_tokens),
                "topic_weights": [],
            }
            row["document_id"] = _document_id(row)
            documents.append(row)
    return sorted(documents, key=lambda row: row["document_id"])


def _derive_lexicon(
    documents: Sequence[dict[str, Any]], plan: ClassicalPlan
) -> dict[str, Any]:
    document_frequency: Counter[str] = Counter()
    corpus_frequency: Counter[str] = Counter()
    for document in documents:
        combined = Counter(document["title_terms"]) + Counter(document["body_terms"])
        document_frequency.update(combined.keys())
        corpus_frequency.update(combined)
    count = len(documents)
    terms = []
    for term in sorted(document_frequency):
        df = document_frequency[term]
        idf = math.log(1.0 + (count - df + 0.5) / (df + 0.5))
        terms.append(
            {
                "term": term,
                "document_frequency": df,
                "corpus_frequency": corpus_frequency[term],
                "idf": round(idf, 10),
            }
        )
    return {
        "schema_version": SCHEMA_VERSION,
        "tokenization": plan.raw["tokenization"],
        "bm25": plan.raw["bm25"],
        "document_count": count,
        "average_field_lengths": {
            "title": round(sum(row["title_length"] for row in documents) / count, 10),
            "body": round(sum(row["body_length"] for row in documents) / count, 10),
        },
        "terms": terms,
    }


def _derive_associations(
    documents: Sequence[dict[str, Any]], lexicon: Mapping[str, Any], plan: ClassicalPlan
) -> list[dict[str, Any]]:
    config = plan.raw["associations"]
    candidates = [
        row
        for row in lexicon["terms"]
        if " " not in row["term"]
        and row["document_frequency"] >= config["min_document_frequency"]
    ]
    candidates.sort(
        key=lambda row: (
            -row["document_frequency"],
            -row["corpus_frequency"],
            row["term"],
        )
    )
    vocabulary = {row["term"] for row in candidates[: config["max_vocabulary"]]}
    statistics = {row["term"]: row for row in candidates if row["term"] in vocabulary}
    positions: Counter[str] = Counter()
    pairs: Counter[tuple[str, str]] = Counter()
    pair_total = 0
    position_total = 0
    window = config["window_size"]
    for document in documents:
        sequence = [
            token
            for token in _unigrams(f"{document['title']} {document['text']}", plan)
            if token in vocabulary
        ]
        positions.update(sequence)
        position_total += len(sequence)
        for left_index, left in enumerate(sequence):
            for right in sequence[left_index + 1 : left_index + window + 1]:
                if left == right:
                    continue
                pairs[tuple(sorted((left, right)))] += 1
                pair_total += 1
    neighbors: dict[str, list[dict[str, Any]]] = {term: [] for term in vocabulary}
    if pair_total and position_total:
        for (left, right), count in pairs.items():
            if count < config["min_cooccurrence"]:
                continue
            probability_pair = count / pair_total
            probability_left = positions[left] / position_total
            probability_right = positions[right] / position_total
            ppmi = max(
                0.0, math.log(probability_pair / (probability_left * probability_right))
            )
            if ppmi < config["minimum_ppmi"] or ppmi <= 0.0:
                continue
            weight = round(ppmi, 8)
            neighbors[left].append(
                {"term": right, "cooccurrence": count, "ppmi": weight}
            )
            neighbors[right].append(
                {"term": left, "cooccurrence": count, "ppmi": weight}
            )
    rows: list[dict[str, Any]] = []
    for term in sorted(vocabulary):
        ranked = sorted(
            neighbors[term],
            key=lambda row: (-row["ppmi"], -row["cooccurrence"], row["term"]),
        )[: config["max_neighbors"]]
        rows.append(
            {
                "term": term,
                "document_frequency": statistics[term]["document_frequency"],
                "corpus_frequency": statistics[term]["corpus_frequency"],
                "neighbors": ranked,
            }
        )
    return rows


def _association_graph(rows: Sequence[dict[str, Any]]) -> dict[str, dict[str, float]]:
    graph: dict[str, dict[str, float]] = {row["term"]: {} for row in rows}
    for row in rows:
        term = row["term"]
        for neighbor in row["neighbors"]:
            other = neighbor["term"]
            weight = float(neighbor["ppmi"])
            graph.setdefault(term, {})[other] = max(
                graph.get(term, {}).get(other, 0.0), weight
            )
            graph.setdefault(other, {})[term] = max(
                graph.get(other, {}).get(term, 0.0), weight
            )
    return graph


def _filtered_topic_corpus(
    documents: Sequence[Mapping[str, Any]], plan: ClassicalPlan
) -> tuple[list[list[str]], list[str]]:
    """Apply the closed vocabulary thresholds before invoking MALLET."""

    config = plan.raw["topics"]
    token_rows = [
        _unigrams(str(document["title"]), plan)
        + _unigrams(str(document["text"]), plan)
        for document in documents
    ]
    frequencies = Counter(term for row in token_rows for term in set(row))
    maximum_documents = len(documents) * float(config["max_document_fraction"])
    vocabulary = sorted(
        term
        for term, frequency in frequencies.items()
        if frequency >= config["min_document_frequency"]
        and frequency <= maximum_documents + 1e-12
    )
    allowed = set(vocabulary)
    filtered = [[term for term in row if term in allowed] for row in token_rows]
    if not vocabulary:
        raise ClassicalError("MALLET vocabulary filtering removed every term")
    if any(not row for row in filtered):
        raise ClassicalError(
            "MALLET vocabulary filtering removed every token from a document"
        )
    return filtered, vocabulary


def _mallet_command(runtime: MalletRuntime, class_name: str) -> list[str]:
    classpath: list[str] = []
    for row in runtime.jar_inventory:
        relative = _safe_relative(str(row["path"]), "MALLET jar inventory path")
        classpath.append(str(runtime.mallet_home.joinpath(*relative.parts)))
    if not classpath:
        raise ClassicalError("MALLET classpath is empty")
    return [
        str(runtime.java),
        "-Xmx1G",
        "-ea",
        "-Dfile.encoding=UTF-8",
        "-Duser.language=en",
        "-Duser.country=US",
        "-Duser.timezone=UTC",
        "-classpath",
        os.pathsep.join(classpath),
        class_name,
    ]


def _require_mallet_run(
    command: Sequence[str],
    *,
    runtime: MalletRuntime,
    timeout: int,
    label: str,
) -> tuple[str, str]:
    for attempt in range(2):
        _verify_mallet_runtime(runtime)
        stdout, stderr, returncode = _run_java(
            command,
            cwd=runtime.mallet_home,
            timeout=timeout,
            label=label,
        )
        combined = f"{stdout}\n{stderr}"
        transient_jshell = (
            returncode != 0
            and "Launching JShell execution engine threw" in combined
            and "TransportTimeoutException: timeout waiting for connection" in combined
        )
        if transient_jshell and attempt == 0:
            continue
        break
    _verify_mallet_runtime(runtime)
    if returncode != 0:
        raise ClassicalError(
            f"{label} exited {returncode}: {(stderr or stdout).strip()[:1000]}"
        )
    for marker in (
        "Missing argument for option",
        "Unrecognized option",
        "Exception in thread",
        "CommandOption$IllegalArgumentException",
    ):
        if marker in combined:
            raise ClassicalError(f"{label} reported an option or runtime error: {marker}")
    return stdout, stderr


def _require_output(path: Path, label: str) -> None:
    try:
        checked = require_regular_file(path, label=label)
    except UnsafePathError as exc:
        raise ClassicalError(str(exc)) from exc
    if checked.stat().st_size == 0:
        raise ClassicalError(f"MALLET did not create a non-empty {label}")


def _parse_document_topics(
    path: Path, document_ids: Sequence[str], topic_count: int
) -> list[list[float]]:
    rows: list[list[float]] = []
    lines = path.read_text(encoding="utf-8").splitlines()
    if len(lines) != len(document_ids):
        raise ClassicalError("MALLET document-topic row count is incomplete")
    for expected_index, (line, document_id) in enumerate(zip(lines, document_ids)):
        fields = line.split("\t")
        if len(fields) != topic_count + 2:
            raise ClassicalError("MALLET document-topic row has the wrong width")
        try:
            observed_index = int(fields[0])
            weights = [float(value) for value in fields[2:]]
        except ValueError as exc:
            raise ClassicalError("MALLET document-topic row is malformed") from exc
        if observed_index != expected_index or fields[1] != document_id:
            raise ClassicalError("MALLET document order or identity changed")
        if any(not math.isfinite(value) or value < 0.0 for value in weights):
            raise ClassicalError("MALLET emitted an invalid document-topic weight")
        if not math.isclose(sum(weights), 1.0, rel_tol=0.0, abs_tol=1e-7):
            raise ClassicalError("MALLET document-topic weights do not sum to one")
        rows.append(weights)
    return rows


def _parse_topic_keys(path: Path, topic_count: int) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    if len(lines) != topic_count:
        raise ClassicalError("MALLET topic-key output is incomplete")
    for expected, line in enumerate(lines):
        fields = line.split("\t")
        try:
            observed = int(fields[0])
            alpha = float(fields[1])
        except (IndexError, ValueError) as exc:
            raise ClassicalError("MALLET topic-key output is malformed") from exc
        if observed != expected or not math.isfinite(alpha) or alpha <= 0.0:
            raise ClassicalError("MALLET topic-key identity or alpha is invalid")


def _parse_word_topic_counts(
    path: Path, vocabulary: Sequence[str], topic_count: int
) -> dict[str, dict[str, int]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if len(lines) != len(vocabulary):
        raise ClassicalError("MALLET word-topic count vocabulary is incomplete")
    result: dict[str, dict[str, int]] = {}
    observed_terms: list[str] = []
    for expected_index, line in enumerate(lines):
        fields = line.split()
        if len(fields) < 2:
            raise ClassicalError("MALLET word-topic count row is malformed")
        try:
            observed_index = int(fields[0])
        except ValueError as exc:
            raise ClassicalError("MALLET word-topic term index is malformed") from exc
        if observed_index != expected_index:
            raise ClassicalError("MALLET word-topic term indices are not contiguous")
        term = fields[1]
        counts: dict[str, int] = {}
        for assignment in fields[2:]:
            try:
                topic_raw, count_raw = assignment.split(":", 1)
                topic = int(topic_raw)
                count = int(count_raw)
            except ValueError as exc:
                raise ClassicalError("MALLET word-topic assignment is malformed") from exc
            if not 0 <= topic < topic_count or count <= 0 or str(topic) in counts:
                raise ClassicalError("MALLET word-topic assignment is invalid")
            counts[str(topic)] = count
        observed_terms.append(term)
        result[term] = counts
    observed_set = set(observed_terms)
    expected_set = set(vocabulary)
    if observed_set != expected_set or len(observed_terms) != len(observed_set):
        duplicates = sorted(
            term for term, count in Counter(observed_terms).items() if count > 1
        )
        raise ClassicalError(
            "MALLET returned a foreign or duplicate vocabulary: "
            f"missing={sorted(expected_set - observed_set)[:10]}, "
            f"foreign={sorted(observed_set - expected_set)[:10]}, "
            f"duplicates={duplicates[:10]}"
        )
    return result


def _parse_topic_word_weights(
    path: Path,
    vocabulary: Sequence[str],
    topic_count: int,
    beta: float,
    sparse_counts: Mapping[str, Mapping[str, int]],
) -> list[list[float]]:
    expected = topic_count * len(vocabulary)
    lines = path.read_text(encoding="utf-8").splitlines()
    if len(lines) != expected:
        raise ClassicalError("MALLET topic-word output is incomplete")
    weights_by_topic = [dict() for _ in range(topic_count)]
    for line in lines:
        fields = line.split("\t")
        if len(fields) != 3:
            raise ClassicalError("MALLET topic-word row is malformed")
        try:
            topic = int(fields[0])
            weight = float(fields[2])
        except ValueError as exc:
            raise ClassicalError("MALLET topic-word value is malformed") from exc
        term = fields[1]
        if (
            not 0 <= topic < topic_count
            or term not in set(vocabulary)
            or term in weights_by_topic[topic]
            or not math.isfinite(weight)
            or weight <= 0.0
        ):
            raise ClassicalError("MALLET topic-word identity or weight is invalid")
        weights_by_topic[topic][term] = weight
    probabilities: list[list[float]] = []
    for topic, weights in enumerate(weights_by_topic):
        if set(weights) != set(vocabulary):
            raise ClassicalError("MALLET topic-word vocabulary coverage is incomplete")
        ordered_weights: list[float] = []
        for term in vocabulary:
            weight = weights[term]
            expected_weight = float(sparse_counts[term].get(str(topic), 0)) + beta
            if not math.isclose(weight, expected_weight, rel_tol=0.0, abs_tol=1e-9):
                raise ClassicalError("MALLET topic-word weight disagrees with token counts")
            ordered_weights.append(weight)
        total = sum(ordered_weights)
        probabilities.append([weight / total for weight in ordered_weights])
    return probabilities


def _derive_topics(
    documents: list[dict[str, Any]], plan: ClassicalPlan, runtime: MalletRuntime
) -> dict[str, Any]:
    """Train fixed-seed one-thread sparse-Gibbs LDA with Java MALLET."""

    config = plan.raw["topics"]
    corpus_rows, expected_vocabulary = _filtered_topic_corpus(documents, plan)
    document_ids = [document["document_id"] for document in documents]
    if any("\t" in value or "\n" in value or "\r" in value for value in document_ids):
        raise ClassicalError("document identifiers are unsafe for the MALLET corpus")
    timeout = config["timeout_seconds"]
    with tempfile.TemporaryDirectory(prefix="semantic-okf-mallet-") as temporary:
        work = Path(temporary)
        corpus_tsv = work / "corpus.tsv"
        corpus_tsv.write_text(
            "".join(
                f"{document_id}\tX\t{' '.join(tokens)}\n"
                for document_id, tokens in zip(document_ids, corpus_rows)
            ),
            encoding="utf-8",
            newline="\n",
        )
        corpus_mallet = work / "corpus.mallet"
        import_command = [
            *_mallet_command(runtime, "cc.mallet.classify.tui.Csv2Vectors"),
            "--input",
            str(corpus_tsv),
            "--output",
            str(corpus_mallet),
            "--keep-sequence",
            "TRUE",
            "--line-regex",
            r"^([^\t]+)\t([^\t]+)\t(.*)$",
            "--name",
            "1",
            "--label",
            "2",
            "--data",
            "3",
            "--token-regex",
            "[a-z0-9]+",
            "--preserve-case",
            "TRUE",
            "--remove-stopwords",
            "FALSE",
        ]
        _require_mallet_run(
            import_command,
            runtime=runtime,
            timeout=timeout,
            label="MALLET import-file",
        )
        _require_output(corpus_mallet, "serialized corpus")

        topic_keys = work / "topic-keys.txt"
        document_topics_path = work / "doc-topics.txt"
        topic_word_path = work / "topic-word-weights.txt"
        word_topic_path = work / "word-topic-counts.txt"
        train_command = [
            *_mallet_command(runtime, "cc.mallet.topics.tui.TopicTrainer"),
            "--input",
            str(corpus_mallet),
            "--num-topics",
            str(config["topic_count"]),
            "--num-threads",
            "1",
            "--num-iterations",
            str(config["num_iterations"]),
            "--num-icm-iterations",
            str(config["num_icm_iterations"]),
            "--random-seed",
            str(config["random_seed"]),
            "--optimize-interval",
            str(config["optimize_interval"]),
            "--optimize-burn-in",
            str(config["optimize_burn_in"]),
            "--alpha",
            str(config["alpha_sum"]),
            "--beta",
            str(config["beta"]),
            "--num-top-words",
            str(config["top_terms"]),
            "--show-topics-interval",
            "0",
            "--output-topic-keys",
            str(topic_keys),
            "--output-doc-topics",
            str(document_topics_path),
            "--doc-topics-threshold",
            "0.0",
            "--topic-word-weights-file",
            str(topic_word_path),
            "--word-topic-counts-file",
            str(word_topic_path),
        ]
        _require_mallet_run(
            train_command,
            runtime=runtime,
            timeout=timeout,
            label="MALLET train-topics",
        )
        for path, label in (
            (topic_keys, "topic keys"),
            (document_topics_path, "document topics"),
            (topic_word_path, "topic-word weights"),
            (word_topic_path, "word-topic counts"),
        ):
            _require_output(path, label)
        _parse_topic_keys(topic_keys, config["topic_count"])
        sparse_counts = _parse_word_topic_counts(
            word_topic_path, expected_vocabulary, config["topic_count"]
        )
        topic_word = _parse_topic_word_weights(
            topic_word_path,
            expected_vocabulary,
            config["topic_count"],
            float(config["beta"]),
            sparse_counts,
        )
        document_topics = _parse_document_topics(
            document_topics_path, document_ids, config["topic_count"]
        )

    labels = {
        term: max(
            range(len(topic_word)),
            key=lambda topic_index: (
                topic_word[topic_index][term_index],
                -topic_index,
            ),
        )
        for term_index, term in enumerate(expected_vocabulary)
    }
    topics: list[dict[str, Any]] = []
    for topic_index, probabilities in enumerate(topic_word):
        ranked = sorted(
            zip(probabilities, expected_vocabulary),
            key=lambda item: (-item[0], item[1]),
        )
        topics.append(
            {
                "topic_id": f"topic-{topic_index:02d}",
                "seed": ranked[0][1],
                "term_count": sum(
                    1 for assigned in labels.values() if assigned == topic_index
                ),
                "terms": [
                    {"term": term, "weight": round(probability, 8)}
                    for probability, term in ranked[: config["top_terms"]]
                    if probability > 0.0
                ],
            }
        )
    for document, weights in zip(documents, document_topics):
        document["topic_weights"] = [
            {
                "topic_id": f"topic-{topic_index:02d}",
                "weight": round(weight, 8),
            }
            for topic_index, weight in enumerate(weights)
            if weight > 0.0
        ]
    return {
        "schema_version": SCHEMA_VERSION,
        "algorithm": ALGORITHMS["topics"],
        "requested_topic_count": config["topic_count"],
        "topic_count": len(topics),
        "iterations": config["num_iterations"],
        "term_topics": [
            {"term": term, "topic_id": f"topic-{labels[term]:02d}"}
            for term in sorted(labels)
        ],
        "topics": topics,
    }


def _derive_all(
    records: Sequence[dict[str, Any]], plan: ClassicalPlan, runtime: MalletRuntime
) -> tuple[list[dict[str, Any]], dict[str, Any], list[dict[str, Any]], dict[str, Any]]:
    documents = _derive_documents(records, plan)
    lexicon = _derive_lexicon(documents, plan)
    associations = _derive_associations(documents, lexicon, plan)
    topics = _derive_topics(documents, plan, runtime)
    return documents, lexicon, associations, topics


def _artifact(root: Path, relative: str, count: int | None = None) -> dict[str, Any]:
    path = root / relative
    result: dict[str, Any] = {
        "path": relative,
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }
    if count is not None:
        result["count"] = count
    return result


def _summary(
    selection: Mapping[str, Any],
    records: Sequence[dict[str, Any]],
    documents: Sequence[dict[str, Any]],
    lexicon: Mapping[str, Any],
    associations: Sequence[dict[str, Any]],
    topics: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "inputs": selection["input_count"],
        "records": len(records),
        "documents": len(documents),
        "terms": len(lexicon["terms"]),
        "association_terms": len(associations),
        "topics": topics["topic_count"],
    }


def build_projection(
    root: Path, plan_path: Path, runtime: MalletRuntime
) -> dict[str, Any]:
    """Add a complete classical projection to an already validated core snapshot."""

    plan = load_plan(plan_path)
    records, sources = _load_core(root)
    selected, selection = _selection(records, sources, plan)
    documents, lexicon, associations, topics = _derive_all(selected, plan, runtime)
    classical = root / "classical"
    if classical.exists() or classical.is_symlink():
        raise ClassicalError("core candidate unexpectedly contains classical artifacts")
    classical.mkdir()
    _write_jsonl(classical / "documents.jsonl", documents)
    _write_json(classical / "lexicon.json", lexicon)
    _write_jsonl(classical / "associations.jsonl", associations)
    _write_json(classical / "topics.json", topics)
    core = {
        "tree_sha256": _core_tree_sha256(root),
        "records_sha256": sha256_file(root / "semantic" / "records.jsonl"),
        "record_count": len(records),
    }
    artifacts = {
        "documents": _artifact(root, ARTIFACT_NAMES["documents"], len(documents)),
        "lexicon": _artifact(root, ARTIFACT_NAMES["lexicon"], len(lexicon["terms"])),
        "associations": _artifact(
            root, ARTIFACT_NAMES["associations"], len(associations)
        ),
        "topics": _artifact(root, ARTIFACT_NAMES["topics"], topics["topic_count"]),
    }
    summary = _summary(selection, selected, documents, lexicon, associations, topics)
    index = {
        "schema_version": SCHEMA_VERSION,
        "authoritative": False,
        "core": core,
        "classical_plan_sha256": plan.sha256,
        "plan": plan.raw,
        "selection": selection,
        "algorithms": ALGORITHMS,
        "toolchain": runtime.payload(),
        "artifacts": artifacts,
        "summary": summary,
    }
    _write_json(classical / "index.json", index)
    initial = validate_classical_bundle(
        root, runtime, require_build_report=False
    )
    if not initial["valid"]:
        raise ClassicalError(initial["errors"][0]["message"])
    report = {
        "schema_version": SCHEMA_VERSION,
        "valid": True,
        "status": "pass",
        "errors": [],
        "warnings": [],
        "classical_plan_sha256": plan.sha256,
        "core": core,
        "selection": selection,
        "toolchain": runtime.payload(),
        "summary": summary,
        "artifacts": {"index": _artifact(root, "classical/index.json"), **artifacts},
    }
    _write_json(classical / "build-report.json", report)
    final = validate_classical_bundle(root, runtime)
    if not final["valid"]:
        raise ClassicalError(final["errors"][0]["message"])
    return report


def _load_json(path: Path, label: str) -> Any:
    try:
        return strict_json_loads(path.read_text(encoding="utf-8"), label=label)
    except (OSError, UnicodeError) as exc:
        raise ClassicalError(f"cannot read {label}: {exc}") from exc


def _validate_or_raise(
    root: Path, runtime: MalletRuntime, *, require_build_report: bool
) -> dict[str, Any]:
    try:
        root = require_real_directory(root, label="Semantic OKF bundle")
        scan_regular_tree(root, label="Semantic OKF bundle")
    except UnsafePathError as exc:
        raise ClassicalError(str(exc)) from exc
    core_result = validate_semantic_bundle(root)
    if not core_result.valid:
        detail = "; ".join(
            error.get("message", "core error") for error in core_result.errors[:3]
        )
        raise ClassicalError(f"authoritative Semantic OKF core is invalid: {detail}")
    classical = root / "classical"
    expected = {
        "index.json",
        "documents.jsonl",
        "lexicon.json",
        "associations.jsonl",
        "topics.json",
    }
    if require_build_report:
        expected.add("build-report.json")
    if not classical.is_dir() or classical.is_symlink():
        raise ClassicalError("classical must be a real directory")
    actual = {path.name for path in classical.iterdir()}
    if actual != expected:
        raise ClassicalError(
            f"classical artifact set is closed; missing={sorted(expected - actual)}, unknown={sorted(actual - expected)}"
        )
    if any(path.is_symlink() or not path.is_file() for path in classical.iterdir()):
        raise ClassicalError("classical artifacts must be regular files")
    index = _load_json(classical / "index.json", "classical/index.json")
    if not isinstance(index, dict):
        raise ClassicalError("classical/index.json root must be an object")
    _exact_keys(
        index,
        {
            "schema_version",
            "authoritative",
            "core",
            "classical_plan_sha256",
            "plan",
            "selection",
            "algorithms",
            "toolchain",
            "artifacts",
            "summary",
        },
        "classical index",
    )
    if index["schema_version"] != SCHEMA_VERSION or index["authoritative"] is not False:
        raise ClassicalError("classical index version or authority marker is invalid")
    if index["algorithms"] != ALGORITHMS:
        raise ClassicalError("classical index algorithm identities are invalid")
    if index["toolchain"] != runtime.payload():
        raise ClassicalError(
            "MALLET runtime differs from the projection's exact toolchain binding"
        )
    plan = _parse_plan(index["plan"])
    if index["classical_plan_sha256"] != plan.sha256:
        raise ClassicalError("classical plan digest is invalid")
    records, sources = _load_core(root)
    selected, selection = _selection(records, sources, plan)
    core = {
        "tree_sha256": _core_tree_sha256(root),
        "records_sha256": sha256_file(root / "semantic" / "records.jsonl"),
        "record_count": len(records),
    }
    if index["core"] != core:
        raise ClassicalError("classical index core binding is stale or invalid")
    if index["selection"] != selection:
        raise ClassicalError("classical index source selection binding is invalid")
    documents = _read_jsonl(
        classical / "documents.jsonl", label="classical/documents.jsonl"
    )
    lexicon = _load_json(classical / "lexicon.json", "classical/lexicon.json")
    associations = _read_jsonl(
        classical / "associations.jsonl", label="classical/associations.jsonl"
    )
    topics = _load_json(classical / "topics.json", "classical/topics.json")
    expected_documents, expected_lexicon, expected_associations, expected_topics = (
        _derive_all(selected, plan, runtime)
    )
    if documents != expected_documents:
        raise ClassicalError(
            "classical documents differ from deterministic authoritative derivation"
        )
    if lexicon != expected_lexicon:
        raise ClassicalError(
            "classical lexicon differs from deterministic document statistics"
        )
    if associations != expected_associations:
        raise ClassicalError(
            "classical associations differ from deterministic PPMI derivation"
        )
    if topics != expected_topics:
        raise ClassicalError(
            "MALLET topics differ from fixed-seed one-thread Java derivation"
        )
    for number, document in enumerate(documents, start=1):
        _exact_keys(document, DOCUMENT_KEYS, f"classical/documents.jsonl:{number}")
    artifacts = {
        "documents": _artifact(root, ARTIFACT_NAMES["documents"], len(documents)),
        "lexicon": _artifact(root, ARTIFACT_NAMES["lexicon"], len(lexicon["terms"])),
        "associations": _artifact(
            root, ARTIFACT_NAMES["associations"], len(associations)
        ),
        "topics": _artifact(root, ARTIFACT_NAMES["topics"], topics["topic_count"]),
    }
    if index["artifacts"] != artifacts:
        raise ClassicalError(
            "classical index artifact hashes, sizes, or counts are invalid"
        )
    summary = _summary(selection, selected, documents, lexicon, associations, topics)
    if index["summary"] != summary:
        raise ClassicalError("classical index summary is invalid")
    expected_report = {
        "schema_version": SCHEMA_VERSION,
        "valid": True,
        "status": "pass",
        "errors": [],
        "warnings": [],
        "classical_plan_sha256": plan.sha256,
        "core": core,
        "selection": selection,
        "toolchain": runtime.payload(),
        "summary": summary,
        "artifacts": {"index": _artifact(root, "classical/index.json"), **artifacts},
    }
    if require_build_report:
        report = _load_json(
            classical / "build-report.json", "classical/build-report.json"
        )
        if report != expected_report:
            raise ClassicalError("classical build report differs from live validation")
    return {
        "schema_version": SCHEMA_VERSION,
        "valid": True,
        "status": "pass",
        "errors": [],
        "warnings": [],
        "summary": summary,
    }


def validate_classical_bundle(
    root: Path, runtime: MalletRuntime, *, require_build_report: bool = True
) -> dict[str, Any]:
    """Validate the authoritative core plus every classical retrieval binding."""

    try:
        return _validate_or_raise(
            root, runtime, require_build_report=require_build_report
        )
    except (
        ClassicalError,
        OSError,
        UnicodeError,
        KeyError,
        IndexError,
        TypeError,
        ValueError,
        OverflowError,
    ) as exc:
        return {
            "schema_version": SCHEMA_VERSION,
            "valid": False,
            "status": "error",
            "errors": [
                {"code": "classical-error", "path": "classical", "message": str(exc)}
            ],
            "warnings": [],
            "summary": {},
        }
