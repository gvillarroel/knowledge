#!/usr/bin/env python3
"""Count-agnostic, PMCID-aware helpers for the endocrine-hygiene benchmark."""

from __future__ import annotations

import hashlib
import json
import math
import re
import statistics
from collections import Counter
from dataclasses import dataclass, replace
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Mapping, Sequence


METRIC_CUTOFFS = (1, 3, 5, 10)
TOKEN_RE = re.compile(r"[a-z0-9]+", re.IGNORECASE)
HEX_64_RE = re.compile(r"[0-9a-f]{64}")
PMCID_RE = re.compile(r"PMC[1-9][0-9]*")
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
STOPWORDS = {
    "a", "about", "across", "after", "all", "also", "among", "an", "and", "are", "as", "at",
    "be", "because", "before", "between", "both", "but", "by", "can", "compare", "contrast", "did",
    "do", "does", "each", "explain", "for", "from", "had", "has", "have", "how", "in", "into", "is",
    "it", "its", "most", "not", "of", "on", "or", "other", "paper", "papers", "should", "study",
    "than", "that", "the", "their", "these", "they", "this", "to", "using", "was", "were", "what",
    "when", "where", "which", "why", "with", "without",
}


class EvaluationError(RuntimeError):
    """Describe a malformed benchmark, bundle, hit, or report."""


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def pretty_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n"


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise EvaluationError(f"duplicate JSON member: {key}")
        result[key] = value
    return result


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_strict_object)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise EvaluationError(f"cannot read JSON object {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise EvaluationError(f"expected a JSON object: {path}")
    return value


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        raise EvaluationError(f"cannot read JSONL {path}: {exc}") from exc
    rows: list[dict[str, Any]] = []
    for number, line in enumerate(lines, 1):
        if not line.strip():
            raise EvaluationError(f"blank JSONL row at {path}:{number}")
        try:
            value = json.loads(line, object_pairs_hook=_strict_object)
        except json.JSONDecodeError as exc:
            raise EvaluationError(f"invalid JSONL at {path}:{number}: {exc}") from exc
        if not isinstance(value, dict):
            raise EvaluationError(f"expected a JSON object at {path}:{number}")
        rows.append(value)
    if not rows:
        raise EvaluationError(f"JSONL contains no rows: {path}")
    return rows


def safe_relative_path(value: str) -> PurePosixPath:
    candidate = PurePosixPath(value.replace("\\", "/"))
    if candidate.is_absolute() or not candidate.parts or any(part in {"", ".", ".."} for part in candidate.parts):
        raise EvaluationError(f"unsafe relative path: {value!r}")
    return candidate


def local_file(root: Path, relative: str) -> Path:
    candidate = safe_relative_path(relative)
    resolved_root = root.resolve()
    resolved = resolved_root.joinpath(*candidate.parts).resolve()
    try:
        resolved.relative_to(resolved_root)
    except ValueError as exc:
        raise EvaluationError(f"path escapes bundle root: {relative!r}") from exc
    return resolved


@dataclass(frozen=True)
class RetrievalQuestion:
    identifier: str
    cohort: str
    question: str
    paper_ids: tuple[str, ...]
    source_ids: tuple[str, ...]


def _sorted_unique_strings(value: Any, label: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not value or any(not isinstance(item, str) or not item for item in value):
        raise EvaluationError(f"{label} must be a nonempty string array")
    if value != sorted(set(value)):
        raise EvaluationError(f"{label} must be sorted and unique")
    return tuple(value)


def load_questions(path: Path, identity_by_source: Mapping[str, str]) -> list[RetrievalQuestion]:
    rows = load_jsonl(path)
    questions: list[RetrievalQuestion] = []
    observed: set[str] = set()
    for number, row in enumerate(rows, 1):
        required = {"id", "question", "question_type", "qrels"}
        if set(row) != required:
            raise EvaluationError(
                f"question row {number} uses a closed schema; missing={sorted(required - set(row))}, "
                f"unknown={sorted(set(row) - required)}"
            )
        identifier = row["id"]
        cohort = row["question_type"]
        question = row["question"]
        qrels = row["qrels"]
        if not isinstance(identifier, str) or not identifier or identifier in observed:
            raise EvaluationError(f"question row {number} has an invalid or duplicate ID")
        observed.add(identifier)
        if cohort not in {"direct", "cross-paper", "hard"}:
            raise EvaluationError(f"question {identifier} has unsupported cohort {cohort!r}")
        if not isinstance(question, str) or not question.strip():
            raise EvaluationError(f"question {identifier} is empty")
        if not isinstance(qrels, dict) or set(qrels) != {"paper_ids", "source_ids"}:
            raise EvaluationError(f"question {identifier}.qrels must contain only paper_ids and source_ids")
        paper_ids = _sorted_unique_strings(qrels["paper_ids"], f"question {identifier}.paper_ids")
        source_ids = _sorted_unique_strings(qrels["source_ids"], f"question {identifier}.source_ids")
        if any(PMCID_RE.fullmatch(item) is None for item in paper_ids):
            raise EvaluationError(f"question {identifier} contains a noncanonical PMCID")
        unknown = sorted(set(source_ids) - set(identity_by_source))
        if unknown:
            raise EvaluationError(f"question {identifier} names unknown sources: {unknown}")
        mapped = {identity_by_source[source_id] for source_id in source_ids}
        if not mapped.issubset(set(paper_ids)):
            raise EvaluationError(f"question {identifier} source qrels map outside its paper qrels")
        questions.append(RetrievalQuestion(identifier, cohort, question, paper_ids, source_ids))
    if not any(question.cohort == "hard" for question in questions):
        raise EvaluationError("benchmark has no hard cohort")
    return questions


@dataclass(frozen=True)
class RetrievalHit:
    source_id: str | None
    paper_id: str | None
    record_id: str | None
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


class AuthoritativeLedger:
    """Load a bundle ledger once and validate discovery hits against exact records."""

    def __init__(self, bundle: Path) -> None:
        self.bundle = bundle.resolve()
        self.path = self.bundle / "semantic" / "records.jsonl"
        self.records = load_jsonl(self.path)
        self.by_identity: dict[tuple[str, str], dict[str, Any]] = {}
        required = {"source_id", "record_id", "record_sha256", "concept_id", "concept_path", "source_path", "body"}
        for number, record in enumerate(self.records, 1):
            missing = [key for key in required if not isinstance(record.get(key), str) or not record[key]]
            if missing:
                raise EvaluationError(f"ledger row {number} has invalid fields: {missing}")
            identity = (record["source_id"], record["record_id"])
            if identity in self.by_identity:
                raise EvaluationError(f"duplicate ledger identity: {identity}")
            concept_path = record["concept_path"].replace("\\", "/")
            source_path = record["source_path"].replace("\\", "/")
            if safe_relative_path(concept_path).parts[0] != "concepts":
                raise EvaluationError(f"ledger concept path is outside concepts/: {concept_path}")
            record["concept_path"] = concept_path
            record["source_path"] = source_path
            missing_digest_fields = [field for field in RECORD_DIGEST_FIELDS if field not in record]
            if missing_digest_fields:
                raise EvaluationError(
                    f"ledger row {number} lacks canonical digest fields: {missing_digest_fields}"
                )
            if not isinstance(record["attributes"], dict):
                raise EvaluationError(f"ledger row {number} attributes must be an object")
            digest_payload = {field: record[field] for field in RECORD_DIGEST_FIELDS}
            expected_record_sha256 = sha256_bytes(canonical_json(digest_payload).encode("utf-8"))
            if record["record_sha256"] != expected_record_sha256:
                raise EvaluationError(
                    f"ledger row {number} record_sha256 does not match its canonical source-derived fields"
                )
            self.by_identity[identity] = record

    def fingerprint(self) -> dict[str, Any]:
        return {"records": len(self.records), "bytes": self.path.stat().st_size, "sha256": sha256_file(self.path)}

    def bind_missing_record_sha256(self, hit: RetrievalHit) -> RetrievalHit:
        """Join a hash-less discovery hit to one exact authoritative ledger row.

        Some unchanged consultation baselines return a record identity, exact
        locator, and retained text but predate the record digest field.  The
        evaluator may attach the digest only through the closed two-column
        ledger identity.  Supplied digests are never repaired, so a mismatched
        consult output still fails independent validation.
        """

        if hit.record_sha256 is not None:
            return hit
        if hit.source_id is None or hit.record_id is None:
            return hit
        record = self.by_identity.get((hit.source_id, hit.record_id))
        if record is None:
            return hit
        return replace(
            hit,
            record_sha256=record["record_sha256"],
            record_sha256_provenance="authoritative-ledger-identity-join",
        )

    def validate_hit(self, hit: RetrievalHit) -> dict[str, Any]:
        issues: list[str] = []
        if hit.source_id is None or hit.record_id is None:
            record = None
            issues.append("missing source_id or record_id")
        else:
            record = self.by_identity.get((hit.source_id, hit.record_id))
            if record is None:
                issues.append("source_id and record_id do not bind a ledger record")
        if hit.record_sha256 is None:
            issues.append("missing record_sha256")
        if hit.concept_path is None:
            issues.append("missing concept_path")
        else:
            try:
                concept = local_file(self.bundle, hit.concept_path)
                if safe_relative_path(hit.concept_path).parts[0] != "concepts":
                    issues.append("concept_path is outside concepts/")
                elif not concept.is_file():
                    issues.append("concept_path does not exist")
            except EvaluationError as exc:
                issues.append(str(exc))
        if record is not None:
            for name in ("source_id", "record_id", "concept_id", "concept_path", "source_path"):
                value = getattr(hit, name)
                if value != record[name]:
                    issues.append(f"{name} does not match the ledger")
            if hit.record_sha256 is not None and hit.record_sha256 != record["record_sha256"]:
                issues.append("record_sha256 does not match the ledger")
            body = record["body"]
            if hit.text is None or hit.text_sha256 is None:
                issues.append("missing retained text or text_sha256")
            elif sha256_bytes(hit.text.encode("utf-8")) != hit.text_sha256:
                issues.append("text_sha256 does not hash retained text")
            locator = hit.locator
            if not isinstance(locator, dict):
                issues.append("missing locator")
            elif locator.get("kind") == "record":
                if set(locator) != {"kind"} or hit.text != body:
                    issues.append("record locator does not bind the complete ledger body")
            elif locator.get("kind") == "character-range":
                if set(locator) != {"kind", "start", "end"}:
                    issues.append("character-range locator has invalid members")
                else:
                    start, end = locator.get("start"), locator.get("end")
                    if (
                        isinstance(start, bool)
                        or isinstance(end, bool)
                        or not isinstance(start, int)
                        or not isinstance(end, int)
                        or not 0 <= start <= end <= len(body)
                    ):
                        issues.append("character-range locator is out of bounds")
                    elif hit.text != body[start:end]:
                        issues.append("character-range text differs from the ledger slice")
            else:
                issues.append("locator kind is neither record nor character-range")
        return {"valid": not issues, "issues": issues}


def parse_search_payload(payload: Mapping[str, Any], identity_by_source: Mapping[str, str]) -> list[RetrievalHit]:
    if payload.get("status") != "pass":
        raise EvaluationError(f"consult search did not pass: {payload.get('error') or payload}")
    raw_hits = payload.get("hits") if isinstance(payload.get("hits"), list) else payload.get("results")
    if not isinstance(raw_hits, list):
        raise EvaluationError("consult search payload has no hits/results array")
    hits: list[RetrievalHit] = []
    for number, raw in enumerate(raw_hits, 1):
        if not isinstance(raw, dict):
            raise EvaluationError(f"consult hit {number} is not an object")
        source_id = raw.get("source_id") if isinstance(raw.get("source_id"), str) else None
        score_value = raw.get("score")
        if score_value is None and isinstance(raw.get("scores"), dict):
            numeric = [value for value in raw["scores"].values() if isinstance(value, (int, float)) and not isinstance(value, bool)]
            score_value = max(numeric) if numeric else None
        score = float(score_value) if isinstance(score_value, (int, float)) and not isinstance(score_value, bool) else None
        retrieval_id = raw.get("chunk_id") or raw.get("document_id") or raw.get("section_id")
        hits.append(
            RetrievalHit(
                source_id=source_id,
                paper_id=identity_by_source.get(source_id) if source_id is not None else None,
                record_id=raw.get("record_id") if isinstance(raw.get("record_id"), str) else None,
                record_sha256=raw.get("record_sha256") if isinstance(raw.get("record_sha256"), str) else None,
                concept_id=raw.get("concept_id") if isinstance(raw.get("concept_id"), str) else None,
                concept_path=(raw.get("concept_path").replace("\\", "/") if isinstance(raw.get("concept_path"), str) else None),
                source_path=(raw.get("source_path").replace("\\", "/") if isinstance(raw.get("source_path"), str) else None),
                locator=raw.get("locator") if isinstance(raw.get("locator"), dict) else None,
                text=raw.get("text") if isinstance(raw.get("text"), str) else None,
                text_sha256=raw.get("text_sha256") if isinstance(raw.get("text_sha256"), str) else None,
                score=score,
                retrieval_id=str(retrieval_id) if retrieval_id is not None else None,
                record_sha256_provenance=(
                    "consult-output" if isinstance(raw.get("record_sha256"), str) else None
                ),
            )
        )
    return hits


def tokenize(text: str) -> list[str]:
    return [token for token in TOKEN_RE.findall(text.casefold()) if len(token) >= 2 and token not in STOPWORDS]


class LegacyLexicalIndex:
    """Deterministic TF-IDF-like evaluator baseline over selected ledger records."""

    def __init__(self, ledger: AuthoritativeLedger, identity_by_source: Mapping[str, str]) -> None:
        documents: list[tuple[RetrievalHit, Counter[str]]] = []
        document_frequency: Counter[str] = Counter()
        for record in ledger.records:
            source_id = record["source_id"]
            if source_id not in identity_by_source:
                continue
            body = record["body"]
            text = "\n".join(
                [
                    str(record.get("title") or ""),
                    body,
                    canonical_json(record.get("attributes") or {}),
                ]
            )
            tokens = Counter(tokenize(text))
            document_frequency.update(tokens.keys())
            documents.append(
                (
                    RetrievalHit(
                        source_id=source_id,
                        paper_id=identity_by_source[source_id],
                        record_id=record["record_id"],
                        record_sha256=record["record_sha256"],
                        concept_id=record["concept_id"],
                        concept_path=record["concept_path"],
                        source_path=record["source_path"],
                        locator={"kind": "record"},
                        text=body,
                        text_sha256=sha256_bytes(body.encode("utf-8")),
                        score=None,
                        retrieval_id=None,
                        record_sha256_provenance="authoritative-ledger",
                    ),
                    tokens,
                )
            )
        if not documents:
            raise EvaluationError("legacy ledger has no selected records")
        count = len(documents)
        self.documents = documents
        self.idf = {token: math.log((count + 1) / (seen + 1)) + 1.0 for token, seen in document_frequency.items()}

    def search(self, query: str, top_k: int) -> list[RetrievalHit]:
        query_tokens = set(tokenize(query))
        ranked: list[tuple[float, str, RetrievalHit]] = []
        for hit, tokens in self.documents:
            score = sum((1.0 + math.log(tokens[token])) * self.idf.get(token, 0.0) for token in query_tokens if tokens[token])
            if score > 0:
                ranked.append((score, hit.concept_path or "", replace(hit, score=score)))
        ranked.sort(key=lambda item: (-item[0], item[1]))
        return [item[2] for item in ranked[:top_k]]


def deduplicate(values: Iterable[str | None]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        if isinstance(value, str) and value and value not in seen:
            seen.add(value)
            result.append(value)
    return result


def ranking_metrics(ranked: Sequence[str], relevant: set[str]) -> dict[str, float]:
    if not relevant:
        raise EvaluationError("qrels cannot be empty")
    result = {
        f"recall_at_{cutoff}": len(set(ranked[:cutoff]) & relevant) / len(relevant)
        for cutoff in METRIC_CUTOFFS
    }
    reciprocal = 0.0
    for index, value in enumerate(ranked[:10], 1):
        if value in relevant:
            reciprocal = 1.0 / index
            break
    dcg = sum(1.0 / math.log2(index + 1) for index, value in enumerate(ranked[:10], 1) if value in relevant)
    ideal = sum(1.0 / math.log2(index + 1) for index in range(1, min(10, len(relevant)) + 1))
    result["mrr_at_10"] = reciprocal
    result["ndcg_at_10"] = dcg / ideal if ideal else 0.0
    return result


def mean_metrics(rows: Sequence[Mapping[str, Any]], key: str) -> dict[str, float] | None:
    if not rows:
        return None
    names = [*(f"recall_at_{cutoff}" for cutoff in METRIC_CUTOFFS), "mrr_at_10", "ndcg_at_10"]
    return {name: statistics.fmean(float(row[key][name]) for row in rows) for name in names}


def percentile(values: Sequence[float], fraction: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    position = (len(ordered) - 1) * fraction
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return float(ordered[lower])
    return float(ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower))


def route_summary(rows: Sequence[dict[str, Any]], cohort: str | None = None) -> dict[str, Any]:
    selected = [row for row in rows if cohort is None or row["cohort"] == cohort]
    returned = sum(row["evidence_validity"]["returned"] for row in selected)
    valid = sum(row["evidence_validity"]["valid"] for row in selected)
    timings = [float(row["elapsed_ms"]) for row in selected]
    return {
        "query_count": len(selected),
        "error_count": sum(row["error"] is not None for row in selected),
        "paper_metrics": mean_metrics(selected, "paper_metrics"),
        "source_metrics": mean_metrics(selected, "source_metrics"),
        "evidence_validity": {
            "returned": returned,
            "valid": valid,
            "invalid": returned - valid,
            "ratio": valid / returned if returned else None,
        },
        "timing_ms": {
            "total": sum(timings),
            "mean": statistics.fmean(timings) if timings else None,
            "median": statistics.median(timings) if timings else None,
            "p95": percentile(timings, 0.95),
        },
    }


def compact_hit(hit: RetrievalHit, validation: Mapping[str, Any], rank: int) -> dict[str, Any]:
    return {
        "rank": rank,
        "source_id": hit.source_id,
        "paper_id": hit.paper_id,
        "record_id": hit.record_id,
        "record_sha256": hit.record_sha256,
        "record_sha256_provenance": hit.record_sha256_provenance,
        "concept_id": hit.concept_id,
        "concept_path": hit.concept_path,
        "source_path": hit.source_path,
        "locator": hit.locator,
        "text_sha256": hit.text_sha256,
        "score": hit.score,
        "retrieval_id": hit.retrieval_id,
        "evidence_validation": dict(validation),
    }


def evaluate_hits(
    question: RetrievalQuestion,
    hits: Sequence[RetrievalHit],
    ledger: AuthoritativeLedger,
    elapsed_ms: float,
    error: str | None,
) -> dict[str, Any]:
    validations = [ledger.validate_hit(hit) for hit in hits]
    valid = sum(item["valid"] for item in validations)
    paper_ids = deduplicate(hit.paper_id for hit in hits)
    source_ids = deduplicate(hit.source_id for hit in hits)
    return {
        "question_id": question.identifier,
        "cohort": question.cohort,
        "elapsed_ms": elapsed_ms,
        "error": error,
        "paper_ids": paper_ids,
        "source_ids": source_ids,
        "paper_metrics": ranking_metrics(paper_ids, set(question.paper_ids)),
        "source_metrics": ranking_metrics(source_ids, set(question.source_ids)),
        "evidence_validity": {"returned": len(hits), "valid": valid, "invalid": len(hits) - valid},
        "hits": [compact_hit(hit, validation, rank) for rank, (hit, validation) in enumerate(zip(hits, validations, strict=True), 1)],
    }
