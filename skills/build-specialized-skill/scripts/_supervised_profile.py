"""Deterministic retrospective supervised-profile construction."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
from typing import Any, Mapping, Sequence


PROFILE_SCHEMA_VERSION = "semantic-okf-supervised-profile-index/2.0"
PROFILE_MODE = "retrospective-supervised-ngram"
CANDIDATE_STATE = "retrospective-all-exposed-supervised-profile"
HOLDOUT_STATUS = "none; all supplied qrels are exposed and cannot promote"
IDENTITY_MODES = ("source-id", "arxiv-id")
TOKEN_RE = re.compile(r"[a-z0-9]+(?:[._/-][a-z0-9]+)*", re.IGNORECASE)
ARXIV_ID_RE = re.compile(
    r"(?<!\d)(\d{4})[.-](\d{4,5})(v\d+)(?!\w)",
    re.IGNORECASE,
)
STOPWORDS = frozenset(
    {
        "a",
        "about",
        "across",
        "an",
        "and",
        "are",
        "as",
        "be",
        "by",
        "can",
        "do",
        "does",
        "for",
        "from",
        "how",
        "in",
        "into",
        "is",
        "its",
        "of",
        "on",
        "or",
        "should",
        "than",
        "that",
        "the",
        "their",
        "then",
        "this",
        "to",
        "use",
        "using",
        "what",
        "when",
        "where",
        "which",
        "why",
        "with",
        "would",
    }
)
NGRAM_WEIGHTS = {
    "1": 0.35,
    "2": 8.0,
    "3": 27.0,
    "4": 64.0,
    "5": 125.0,
}
PROFILE_SCORE_MULTIPLIER = 1_000_000.0


class SupervisedProfileError(ValueError):
    """Raised when exposed development evidence cannot form a safe profile."""


def sha256_file(path: Path) -> str:
    """Return the lowercase SHA-256 digest of one file."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_json(value: Any) -> str:
    """Render deterministic finite JSON with one trailing newline."""

    return (
        json.dumps(
            value,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
            allow_nan=False,
        )
        + "\n"
    )


def _read_jsonl(path: Path, *, label: str) -> list[dict[str, Any]]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        raise SupervisedProfileError(f"Cannot read {label}: {path}: {exc}") from exc
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise SupervisedProfileError(
                f"Invalid {label} JSON on line {line_number}: {exc}"
            ) from exc
        if not isinstance(value, dict):
            raise SupervisedProfileError(
                f"{label} line {line_number} must be a JSON object"
            )
        rows.append(value)
    if not rows:
        raise SupervisedProfileError(f"{label} is empty: {path}")
    return rows


def _tokens(text: str) -> list[str]:
    values: list[str] = []
    for raw in TOKEN_RE.findall(text.casefold()):
        token = raw.strip("._/-")
        if token:
            values.append(token)
    return values


def _features(text: str) -> set[str]:
    tokens = _tokens(text)
    result: set[str] = set()
    for size in range(1, 6):
        for offset in range(0, len(tokens) - size + 1):
            window = tokens[offset : offset + size]
            if size == 1 and window[0] in STOPWORDS:
                continue
            result.add(f"{size}:{' '.join(window)}")
    return result


def normalize_arxiv_id(value: str) -> str:
    """Extract one versioned arXiv identity from a reviewed string."""

    matches = {
        f"{match.group(1)}.{match.group(2)}{match.group(3).lower()}"
        for match in ARXIV_ID_RE.finditer(value)
    }
    if len(matches) != 1:
        raise SupervisedProfileError(
            f"Expected exactly one versioned arXiv identity in {value!r}"
        )
    return next(iter(matches))


def _record_identity(record: Mapping[str, Any], mode: str) -> str:
    source_id = record.get("source_id")
    if not isinstance(source_id, str) or not source_id:
        raise SupervisedProfileError("Knowledge record lacks source_id")
    if mode == "source-id":
        return source_id
    candidates: set[str] = set()
    for key in ("source_id", "record_id", "source_path", "title"):
        value = record.get(key)
        if not isinstance(value, str):
            continue
        for match in ARXIV_ID_RE.finditer(value):
            candidates.add(
                f"{match.group(1)}.{match.group(2)}{match.group(3).lower()}"
            )
    if len(candidates) != 1:
        raise SupervisedProfileError(
            "Each record in arxiv-id mode must expose exactly one consistent "
            f"versioned arXiv identity; found {sorted(candidates)!r} for {source_id!r}"
        )
    return next(iter(candidates))


def _normalize_qrel(value: str, mode: str) -> str:
    return value if mode == "source-id" else normalize_arxiv_id(value)


def _validate_questions(
    path: Path,
    *,
    qrel_key: str,
    identity_mode: str,
) -> list[dict[str, Any]]:
    questions = _read_jsonl(path, label="retrieval questions")
    identifiers: set[str] = set()
    for number, row in enumerate(questions, start=1):
        identifier = row.get("id")
        question = row.get("question")
        qrels = row.get("qrels")
        if (
            not isinstance(identifier, str)
            or not identifier
            or not isinstance(question, str)
            or not question.strip()
            or not isinstance(qrels, dict)
        ):
            raise SupervisedProfileError(f"Question row {number} is incomplete")
        if identifier in identifiers:
            raise SupervisedProfileError(
                f"Duplicate question identifier: {identifier}"
            )
        identifiers.add(identifier)
        identities = qrels.get(qrel_key)
        if (
            not isinstance(identities, list)
            or not identities
            or not all(isinstance(item, str) and item for item in identities)
        ):
            raise SupervisedProfileError(
                f"Question {identifier} has invalid {qrel_key} qrels"
            )
        normalized = [_normalize_qrel(item, identity_mode) for item in identities]
        if normalized != sorted(set(normalized)):
            raise SupervisedProfileError(
                f"Question {identifier} {qrel_key} qrels are not sorted and unique"
            )
        if not _features(question):
            raise SupervisedProfileError(
                f"Question {identifier} has no lexical profile features"
            )
    return questions


def build_supervised_profile(
    *,
    dataset_id: str,
    knowledge: Path,
    questions_path: Path,
    qrel_key: str,
    identity_mode: str,
) -> dict[str, Any]:
    """Build one generic all-exposed-cohort n-gram routing profile."""

    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", dataset_id):
        raise SupervisedProfileError(
            "Profile dataset ID must use lowercase letters, digits, and hyphens"
        )
    if not re.fullmatch(r"[a-z][a-z0-9_]*", qrel_key):
        raise SupervisedProfileError(
            "Profile qrel key must be a lowercase JSON member name"
        )
    if identity_mode not in IDENTITY_MODES:
        raise SupervisedProfileError(
            f"Unsupported profile identity mode: {identity_mode}"
        )

    ledger_path = knowledge / "semantic" / "records.jsonl"
    records = _read_jsonl(ledger_path, label="knowledge ledger")
    questions = _validate_questions(
        questions_path,
        qrel_key=qrel_key,
        identity_mode=identity_mode,
    )

    records_by_primary: dict[str, list[dict[str, Any]]] = {}
    ledger_identities: set[tuple[str, str]] = set()
    for row_number, record in enumerate(records, start=1):
        source_id = record.get("source_id")
        record_id = record.get("record_id")
        if not isinstance(source_id, str) or not isinstance(record_id, str):
            raise SupervisedProfileError(
                f"Knowledge ledger row {row_number} lacks source_id or record_id"
            )
        identity = (source_id, record_id)
        if identity in ledger_identities:
            raise SupervisedProfileError(
                f"Duplicate knowledge identity: {identity!r}"
            )
        ledger_identities.add(identity)
        primary = _record_identity(record, identity_mode)
        records_by_primary.setdefault(primary, []).append(record)

    features_by_record = {identity: set() for identity in ledger_identities}
    question_ids_by_record = {identity: set() for identity in ledger_identities}
    for question in questions:
        question_features = _features(str(question["question"]))
        qrels = question["qrels"][qrel_key]
        for raw_primary in qrels:
            primary = _normalize_qrel(raw_primary, identity_mode)
            matched = records_by_primary.get(primary)
            if matched is None:
                raise SupervisedProfileError(
                    f"Question {question['id']} references absent identity: {primary}"
                )
            for record in matched:
                identity = (str(record["source_id"]), str(record["record_id"]))
                features_by_record[identity].update(question_features)
                question_ids_by_record[identity].add(str(question["id"]))

    profile_rows: list[dict[str, Any]] = []
    for record in sorted(
        records,
        key=lambda item: (str(item["source_id"]), str(item["record_id"])),
    ):
        identity = (str(record["source_id"]), str(record["record_id"]))
        profile_rows.append(
            {
                "source_id": identity[0],
                "record_id": identity[1],
                "primary_identity": _record_identity(record, identity_mode),
                "question_ids": sorted(question_ids_by_record[identity]),
                "features": sorted(features_by_record[identity]),
            }
        )

    supervised = [row for row in profile_rows if row["features"]]
    return {
        "schema_version": PROFILE_SCHEMA_VERSION,
        "dataset_id": dataset_id,
        "profile_mode": PROFILE_MODE,
        "candidate_state": CANDIDATE_STATE,
        "promotion_eligible": False,
        "knowledge": {
            "ledger_path": "references/knowledge/semantic/records.jsonl",
            "ledger_sha256": sha256_file(ledger_path),
            "record_count": len(records),
        },
        "development_evidence": {
            "questions_filename": questions_path.name,
            "questions_sha256": sha256_file(questions_path),
            "question_count": len(questions),
            "scope": (
                f"all {len(questions)} supplied questions and their exposed "
                "reviewed qrels"
            ),
            "holdout_status": HOLDOUT_STATUS,
        },
        "identity": {
            "mode": identity_mode,
            "qrel_key": qrel_key,
            "deduplication": "first ranked record per primary_identity",
        },
        "retrieval": {
            "max_ngram": 5,
            "ngram_weights": NGRAM_WEIGHTS,
            "profile_score_multiplier": PROFILE_SCORE_MULTIPLIER,
            "fallback": (
                "stable raw token occurrence over authoritative ledger fields"
            ),
            "tie_break": [
                "profile_score_desc",
                "fallback_score_desc",
                "source_id_asc",
                "record_id_asc",
            ],
            "exact_question_lookup": False,
        },
        "summary": {
            "profile_count": len(profile_rows),
            "primary_identity_count": len(records_by_primary),
            "supervised_profile_count": len(supervised),
            "feature_assignment_count": sum(
                len(row["features"]) for row in profile_rows
            ),
            "question_assignment_count": sum(
                len(row["question_ids"]) for row in profile_rows
            ),
        },
        "profiles": profile_rows,
    }


def manifest_profile_binding(payload: Mapping[str, Any], sha256: str) -> dict[str, Any]:
    """Project the non-authoritative profile contract into the expert manifest."""

    development = payload["development_evidence"]
    identity = payload["identity"]
    return {
        "mode": PROFILE_MODE,
        "dataset_id": payload["dataset_id"],
        "candidate_state": CANDIDATE_STATE,
        "promotion_eligible": False,
        "holdout_status": HOLDOUT_STATUS,
        "questions_sha256": development["questions_sha256"],
        "question_count": development["question_count"],
        "qrel_key": identity["qrel_key"],
        "identity_mode": identity["mode"],
        "exact_question_lookup": False,
        "artifact": {
            "path": "scripts/expert_routing_index.json",
            "sha256": sha256,
        },
    }


def validate_profile_against_manifest(
    payload: Mapping[str, Any],
    binding: Mapping[str, Any],
    *,
    ledger_sha256: str,
    record_count: int,
) -> None:
    """Validate the closed governance and identity surface of a profile."""

    if payload.get("schema_version") != PROFILE_SCHEMA_VERSION:
        raise SupervisedProfileError("Unsupported supervised profile schema")
    if payload.get("profile_mode") != PROFILE_MODE:
        raise SupervisedProfileError("Supervised profile mode drift")
    if payload.get("candidate_state") != CANDIDATE_STATE:
        raise SupervisedProfileError("Supervised profile candidate state drift")
    if payload.get("promotion_eligible") is not False:
        raise SupervisedProfileError("Retrospective profile cannot be promotable")

    knowledge = payload.get("knowledge")
    development = payload.get("development_evidence")
    identity = payload.get("identity")
    retrieval = payload.get("retrieval")
    rows = payload.get("profiles")
    if not all(
        isinstance(value, dict)
        for value in (knowledge, development, identity, retrieval)
    ) or not isinstance(rows, list):
        raise SupervisedProfileError("Supervised profile lacks required sections")
    if (
        knowledge.get("ledger_path")
        != "references/knowledge/semantic/records.jsonl"
        or knowledge.get("ledger_sha256") != ledger_sha256
        or knowledge.get("record_count") != record_count
    ):
        raise SupervisedProfileError("Supervised profile knowledge binding drift")
    if (
        development.get("holdout_status") != HOLDOUT_STATUS
        or not isinstance(development.get("question_count"), int)
        or development["question_count"] < 1
    ):
        raise SupervisedProfileError("Supervised profile development evidence drift")
    if (
        identity.get("mode") not in IDENTITY_MODES
        or not isinstance(identity.get("qrel_key"), str)
    ):
        raise SupervisedProfileError("Supervised profile identity contract drift")
    if (
        retrieval.get("ngram_weights") != NGRAM_WEIGHTS
        or retrieval.get("profile_score_multiplier")
        != PROFILE_SCORE_MULTIPLIER
        or retrieval.get("exact_question_lookup") is not False
    ):
        raise SupervisedProfileError("Supervised profile retrieval contract drift")

    expected_binding = manifest_profile_binding(
        payload,
        str(binding.get("artifact", {}).get("sha256", "")),
    )
    if dict(binding) != expected_binding:
        raise SupervisedProfileError("Expert manifest retrieval-profile drift")

    observed: set[tuple[str, str]] = set()
    for index, row in enumerate(rows):
        if not isinstance(row, dict) or set(row) != {
            "source_id",
            "record_id",
            "primary_identity",
            "question_ids",
            "features",
        }:
            raise SupervisedProfileError(f"Invalid profile row at index {index}")
        source_id = row["source_id"]
        record_id = row["record_id"]
        primary = row["primary_identity"]
        features = row["features"]
        question_ids = row["question_ids"]
        if (
            not all(isinstance(item, str) and item for item in (source_id, record_id, primary))
            or not isinstance(features, list)
            or features != sorted(set(features))
            or not all(isinstance(item, str) for item in features)
            or not isinstance(question_ids, list)
            or question_ids != sorted(set(question_ids))
            or not all(isinstance(item, str) for item in question_ids)
        ):
            raise SupervisedProfileError(f"Non-canonical profile row at index {index}")
        for feature in features:
            prefix, separator, text = feature.partition(":")
            if separator != ":" or prefix not in NGRAM_WEIGHTS or not text:
                raise SupervisedProfileError(
                    f"Invalid profile feature at index {index}: {feature!r}"
                )
        ledger_identity = (source_id, record_id)
        if ledger_identity in observed:
            raise SupervisedProfileError(
                f"Duplicate profile ledger identity: {ledger_identity!r}"
            )
        observed.add(ledger_identity)
    if len(observed) != record_count:
        raise SupervisedProfileError("Profile and ledger record counts differ")

