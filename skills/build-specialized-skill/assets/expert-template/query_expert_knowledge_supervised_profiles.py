#!/usr/bin/env python3
"""Verify and query an expert with a retrospective supervised lexical profile."""

from __future__ import annotations

import argparse
from collections import Counter
from functools import lru_cache
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sys
from typing import Any, Iterator, Mapping, Sequence


sys.dont_write_bytecode = True
MANIFEST_SCHEMA = "semantic-okf-expert-skill/1.1"
PROFILE_SCHEMA = "semantic-okf-supervised-profile-index/2.0"
PROFILE_MODE = "retrospective-supervised-ngram"
CANDIDATE_STATE = "retrospective-all-exposed-supervised-profile"
HOLDOUT_STATUS = "none; all supplied qrels are exposed and cannot promote"
RETRIEVAL_CONTRACT_ID = "retrospective-supervised-ngram-fusion-v2"
ROUTE_NAME = "specialized_expert_retrospective_supervised_ngram"
SKILL_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = SKILL_ROOT / "expert-manifest.json"
KNOWLEDGE_ROOT = SKILL_ROOT / "references" / "knowledge"
LEDGER_PATH = KNOWLEDGE_ROOT / "semantic" / "records.jsonl"
PROFILE_PATH = Path(__file__).resolve().parent / "expert_routing_index.json"
TOKEN_RE = re.compile(r"[a-z0-9]+(?:[._/-][a-z0-9]+)*", re.IGNORECASE)
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
EXPECTED_WEIGHTS = {
    "1": 0.35,
    "2": 8.0,
    "3": 27.0,
    "4": 64.0,
    "5": 125.0,
}
PROFILE_MULTIPLIER = 1_000_000.0


class ExpertQueryError(ValueError):
    """Describe an invalid expert binding, profile, or query."""


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _tree_binding(root: Path) -> tuple[str, int]:
    if not root.is_dir():
        raise ExpertQueryError(f"Embedded knowledge is absent: {root}")
    paths: list[Path] = []
    for path in root.rglob("*"):
        if path.is_symlink():
            raise ExpertQueryError(f"Embedded knowledge contains a symlink: {path}")
        if path.is_file():
            paths.append(path)
    digest = hashlib.sha256()
    for path in sorted(paths, key=lambda item: item.relative_to(root).as_posix()):
        relative = path.relative_to(root).as_posix().encode("utf-8")
        data = path.read_bytes()
        digest.update(relative)
        digest.update(b"\0")
        digest.update(str(len(data)).encode("ascii"))
        digest.update(b"\0")
        digest.update(data)
        digest.update(b"\0")
    return digest.hexdigest(), len(paths)


def _load_json_object(path: Path, *, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ExpertQueryError(f"Cannot read {label}: {exc}") from exc
    if not isinstance(value, dict):
        raise ExpertQueryError(f"{label} must be a JSON object")
    return value


def _safe_path(raw: str, *, label: str) -> Path:
    relative = PurePosixPath(raw)
    if (
        relative.is_absolute()
        or not relative.parts
        or "\\" in raw
        or any(part in {"", ".", ".."} for part in relative.parts)
    ):
        raise ExpertQueryError(f"Unsafe {label}: {raw}")
    path = SKILL_ROOT.joinpath(*relative.parts)
    try:
        path.resolve().relative_to(SKILL_ROOT.resolve())
    except ValueError as exc:
        raise ExpertQueryError(f"{label} escapes the expert: {raw}") from exc
    return path


def _verify_artifact(binding: Any, *, label: str) -> str:
    if not isinstance(binding, dict) or set(binding) != {"path", "sha256"}:
        raise ExpertQueryError(f"Invalid artifact binding: {label}")
    raw_path = binding.get("path")
    expected_sha256 = binding.get("sha256")
    if not isinstance(raw_path, str) or not isinstance(expected_sha256, str):
        raise ExpertQueryError(f"Invalid artifact binding: {label}")
    path = _safe_path(raw_path, label=label)
    if not path.is_file() or path.is_symlink():
        raise ExpertQueryError(f"Bound artifact is absent or unsafe: {raw_path}")
    if _sha256_file(path) != expected_sha256:
        raise ExpertQueryError(f"Artifact digest drift: {label}")
    return raw_path


def _tokens(text: str) -> tuple[str, ...]:
    values: list[str] = []
    for raw in TOKEN_RE.findall(text.casefold()):
        token = raw.strip("._/-")
        if token:
            values.append(token)
    return tuple(values)


def _features(text: str) -> frozenset[str]:
    tokens = _tokens(text)
    result: set[str] = set()
    for size in range(1, 6):
        for offset in range(0, len(tokens) - size + 1):
            window = tokens[offset : offset + size]
            if size == 1 and window[0] in STOPWORDS:
                continue
            result.add(f"{size}:{' '.join(window)}")
    return frozenset(result)


def _safe_concept_path(record: Mapping[str, Any]) -> str:
    raw = record.get("concept_path")
    if not isinstance(raw, str):
        raise ExpertQueryError("Ledger record lacks concept_path")
    relative = PurePosixPath(raw)
    if (
        relative.is_absolute()
        or not relative.parts
        or "\\" in raw
        or any(part in {"", ".", ".."} for part in relative.parts)
    ):
        raise ExpertQueryError(f"Unsafe concept_path: {raw}")
    target = KNOWLEDGE_ROOT.joinpath(*relative.parts)
    try:
        target.resolve().relative_to(KNOWLEDGE_ROOT.resolve())
    except ValueError as exc:
        raise ExpertQueryError(f"Concept path escapes knowledge: {raw}") from exc
    if not target.is_file():
        raise ExpertQueryError(f"Concept is absent: {raw}")
    return raw


@lru_cache(maxsize=1)
def _records() -> tuple[dict[str, Any], ...]:
    try:
        lines = LEDGER_PATH.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        raise ExpertQueryError(f"Cannot read embedded record ledger: {exc}") from exc
    rows: list[dict[str, Any]] = []
    identities: set[tuple[str, str]] = set()
    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ExpertQueryError(
                f"Invalid ledger JSON on line {line_number}: {exc}"
            ) from exc
        if not isinstance(record, dict):
            raise ExpertQueryError(f"Ledger line {line_number} is not an object")
        source_id = record.get("source_id")
        record_id = record.get("record_id")
        if not isinstance(source_id, str) or not isinstance(record_id, str):
            raise ExpertQueryError(
                f"Ledger line {line_number} lacks an authoritative identity"
            )
        identity = (source_id, record_id)
        if identity in identities:
            raise ExpertQueryError(f"Duplicate ledger identity: {identity!r}")
        identities.add(identity)
        _safe_concept_path(record)
        rows.append(record)
    if not rows:
        raise ExpertQueryError("Embedded record ledger is empty")
    return tuple(rows)


@lru_cache(maxsize=1)
def _manifest() -> dict[str, Any]:
    value = _load_json_object(MANIFEST_PATH, label="expert manifest")
    if value.get("schema_version") != MANIFEST_SCHEMA:
        raise ExpertQueryError("Unsupported expert manifest schema")
    return value


def _validate_profile_payload(
    payload: Mapping[str, Any],
) -> dict[tuple[str, str], tuple[str, frozenset[str]]]:
    if (
        payload.get("schema_version") != PROFILE_SCHEMA
        or payload.get("profile_mode") != PROFILE_MODE
        or payload.get("candidate_state") != CANDIDATE_STATE
        or payload.get("promotion_eligible") is not False
    ):
        raise ExpertQueryError("Retrospective profile identity or state drift")
    knowledge = payload.get("knowledge")
    development = payload.get("development_evidence")
    identity = payload.get("identity")
    retrieval = payload.get("retrieval")
    rows = payload.get("profiles")
    if (
        not isinstance(knowledge, dict)
        or not isinstance(development, dict)
        or not isinstance(identity, dict)
        or not isinstance(retrieval, dict)
        or not isinstance(rows, list)
    ):
        raise ExpertQueryError("Profile index lacks required sections")
    if (
        knowledge.get("ledger_sha256") != _sha256_file(LEDGER_PATH)
        or knowledge.get("record_count") != len(_records())
    ):
        raise ExpertQueryError("Profile index knowledge binding drift")
    if (
        development.get("holdout_status") != HOLDOUT_STATUS
        or not isinstance(development.get("question_count"), int)
        or development["question_count"] < 1
    ):
        raise ExpertQueryError("Profile development-evidence binding drift")
    if identity.get("mode") not in {"source-id", "arxiv-id"}:
        raise ExpertQueryError("Profile primary-identity mode drift")
    if (
        retrieval.get("ngram_weights") != EXPECTED_WEIGHTS
        or retrieval.get("profile_score_multiplier") != PROFILE_MULTIPLIER
        or retrieval.get("exact_question_lookup") is not False
    ):
        raise ExpertQueryError("Profile retrieval contract drift")

    profiles: dict[tuple[str, str], tuple[str, frozenset[str]]] = {}
    for index, row in enumerate(rows):
        if not isinstance(row, dict) or set(row) != {
            "source_id",
            "record_id",
            "primary_identity",
            "question_ids",
            "features",
        }:
            raise ExpertQueryError(f"Profile row {index} has an invalid schema")
        source_id = row["source_id"]
        record_id = row["record_id"]
        primary = row["primary_identity"]
        features = row["features"]
        question_ids = row["question_ids"]
        if (
            not all(
                isinstance(item, str) and item
                for item in (source_id, record_id, primary)
            )
            or not isinstance(features, list)
            or features != sorted(set(features))
            or not all(isinstance(item, str) for item in features)
            or not isinstance(question_ids, list)
            or question_ids != sorted(set(question_ids))
            or not all(isinstance(item, str) for item in question_ids)
        ):
            raise ExpertQueryError(f"Profile row {index} is not canonical")
        for feature in features:
            prefix, separator, text = feature.partition(":")
            if separator != ":" or prefix not in EXPECTED_WEIGHTS or not text:
                raise ExpertQueryError(f"Invalid profile feature: {feature!r}")
        ledger_identity = (source_id, record_id)
        if ledger_identity in profiles:
            raise ExpertQueryError(
                f"Duplicate profile identity: {ledger_identity!r}"
            )
        profiles[ledger_identity] = (primary, frozenset(features))
    ledger_identities = {
        (str(record["source_id"]), str(record["record_id"]))
        for record in _records()
    }
    if set(profiles) != ledger_identities:
        raise ExpertQueryError("Profile and authoritative ledger identities differ")
    return profiles


@lru_cache(maxsize=1)
def _profile_payload() -> dict[str, Any]:
    payload = _load_json_object(PROFILE_PATH, label="supervised profile index")
    _validate_profile_payload(payload)
    return payload


@lru_cache(maxsize=1)
def _profiles() -> dict[tuple[str, str], tuple[str, frozenset[str]]]:
    return _validate_profile_payload(_profile_payload())


@lru_cache(maxsize=1)
def _search_documents() -> tuple[tuple[dict[str, Any], Counter[str]], ...]:
    rows = []
    for record in _records():
        haystack = " ".join(
            str(record.get(key) or "")
            for key in (
                "title",
                "body",
                "source_id",
                "record_id",
                "concept_type",
            )
        )
        rows.append((record, Counter(_tokens(haystack))))
    return tuple(rows)


def retrieval_contract() -> dict[str, Any]:
    """Describe the frozen supervised profile and authoritative fallback."""

    payload = _profile_payload()
    return {
        "id": RETRIEVAL_CONTRACT_ID,
        "route_name": ROUTE_NAME,
        "query_adapter": (
            "Score one-to-five-token query n-grams against profiles learned "
            "from every explicitly exposed qrel, use authoritative token "
            "occurrence as fallback, deduplicate primary identities, and "
            "return exact immutable ledger records. Exact-question lookup is absent."
        ),
        "parameters": {
            "candidate_state": CANDIDATE_STATE,
            "promotion_eligible": False,
            "question_count": payload["development_evidence"]["question_count"],
            "identity_mode": payload["identity"]["mode"],
            "qrel_key": payload["identity"]["qrel_key"],
            "max_ngram": 5,
            "ngram_weights": EXPECTED_WEIGHTS,
            "profile_score_multiplier": PROFILE_MULTIPLIER,
            "exact_question_lookup": False,
            "fallback": (
                "raw query-token occurrence over title, body, source_id, "
                "record_id, and concept_type"
            ),
            "deduplication": "first ranked record per primary_identity",
        },
    }


def verify() -> dict[str, Any]:
    """Verify the complete expert, knowledge tree, and profile binding."""

    manifest = _manifest()
    knowledge = manifest.get("knowledge")
    artifacts = manifest.get("artifacts")
    profile_binding = manifest.get("retrieval_profile")
    if (
        not isinstance(knowledge, dict)
        or not isinstance(artifacts, dict)
        or not isinstance(profile_binding, dict)
    ):
        raise ExpertQueryError("Expert manifest lacks required bindings")
    expected_tree = knowledge.get("tree")
    if not isinstance(expected_tree, dict):
        raise ExpertQueryError("Expert manifest lacks a tree binding")
    tree_sha256, file_count = _tree_binding(KNOWLEDGE_ROOT)
    if (
        tree_sha256 != expected_tree.get("sha256")
        or file_count != expected_tree.get("file_count")
        or knowledge.get("record_count") != len(_records())
    ):
        raise ExpertQueryError("Embedded knowledge binding drift")
    for key in ("skill_md", "guidance", "query_script", "agents_metadata"):
        _verify_artifact(artifacts.get(key), label=key)
    support = artifacts.get("query_support")
    if not isinstance(support, list) or len(support) != 1:
        raise ExpertQueryError("Expert must bind exactly one routing index")
    support_path = _verify_artifact(support[0], label="query_support[0]")
    if support_path != "scripts/expert_routing_index.json":
        raise ExpertQueryError("Unexpected routing-index support path")
    profile_sha256 = _sha256_file(PROFILE_PATH)
    expected_profile = {
        "mode": PROFILE_MODE,
        "dataset_id": _profile_payload()["dataset_id"],
        "candidate_state": CANDIDATE_STATE,
        "promotion_eligible": False,
        "holdout_status": HOLDOUT_STATUS,
        "questions_sha256": _profile_payload()["development_evidence"][
            "questions_sha256"
        ],
        "question_count": _profile_payload()["development_evidence"][
            "question_count"
        ],
        "qrel_key": _profile_payload()["identity"]["qrel_key"],
        "identity_mode": _profile_payload()["identity"]["mode"],
        "exact_question_lookup": False,
        "artifact": {
            "path": "scripts/expert_routing_index.json",
            "sha256": profile_sha256,
        },
    }
    if profile_binding != expected_profile:
        raise ExpertQueryError("Expert manifest retrieval-profile drift")
    return {
        "status": "pass",
        "skill_name": manifest.get("skill_name"),
        "dataset_id": _profile_payload()["dataset_id"],
        "candidate_state": CANDIDATE_STATE,
        "promotion_eligible": False,
        "knowledge_tree_sha256": tree_sha256,
        "knowledge_file_count": file_count,
        "record_count": knowledge.get("record_count"),
        "profile_index_sha256": profile_sha256,
        "supervised_profile_count": _profile_payload()["summary"][
            "supervised_profile_count"
        ],
        "retrieval": retrieval_contract(),
    }


def _project(
    record: Mapping[str, Any],
    *,
    show_content: bool,
    score: float | None,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "source_id": record.get("source_id"),
        "record_id": record.get("record_id"),
        "title": record.get("title"),
        "concept_type": record.get("concept_type"),
        "concept_id": record.get("concept_id"),
        "concept_path": _safe_concept_path(record),
        "record_sha256": record.get("record_sha256"),
        "source_path": record.get("source_path"),
    }
    if score is not None:
        result["score"] = score
    if show_content:
        body = record.get("body")
        result["body"] = body
        if isinstance(body, str):
            result["text"] = body
            result["text_sha256"] = hashlib.sha256(
                body.encode("utf-8")
            ).hexdigest()
            result["locator"] = {"kind": "record"}
    return result


def _profile_score(
    query_features: frozenset[str],
    profile_features: frozenset[str],
) -> float:
    return sum(
        EXPECTED_WEIGHTS[feature.split(":", 1)[0]]
        for feature in query_features & profile_features
    )


def search(
    contains: str,
    *,
    source_id: str | None,
    concept_type: str | None,
    limit: int,
    show_content: bool,
) -> list[dict[str, Any]]:
    """Rank immutable records by the profile and authoritative fallback."""

    if (
        not isinstance(limit, int)
        or isinstance(limit, bool)
        or not 1 <= limit <= 1000
    ):
        raise ExpertQueryError("--limit must be from 1 through 1000")
    query_tokens = tuple(dict.fromkeys(_tokens(contains)))
    if not query_tokens:
        raise ExpertQueryError("--contains must include at least one search token")
    query_features = _features(contains)
    profiles = _profiles()
    matches: list[tuple[float, int, str, str, str, Mapping[str, Any]]] = []
    for record, term_counts in _search_documents():
        if source_id is not None and record.get("source_id") != source_id:
            continue
        if (
            concept_type is not None
            and record.get("concept_type") != concept_type
        ):
            continue
        identity = (str(record["source_id"]), str(record["record_id"]))
        primary, profile = profiles[identity]
        profile_score = _profile_score(query_features, profile)
        fallback_score = sum(term_counts.get(token, 0) for token in query_tokens)
        if profile_score <= 0.0 and fallback_score <= 0:
            continue
        matches.append(
            (
                profile_score,
                fallback_score,
                identity[0],
                identity[1],
                primary,
                record,
            )
        )
    matches.sort(key=lambda item: (-item[0], -item[1], item[2], item[3]))
    selected = []
    seen_primary: set[str] = set()
    for match in matches:
        if match[4] in seen_primary:
            continue
        seen_primary.add(match[4])
        selected.append(match)
        if len(selected) == limit:
            break
    return [
        _project(
            record,
            show_content=show_content,
            score=(profile_score * PROFILE_MULTIPLIER) + fallback_score,
        )
        for profile_score, fallback_score, _, _, _, record in selected
    ]


def get_record(
    source_id: str,
    record_id: str,
    *,
    show_content: bool,
) -> dict[str, Any]:
    """Return one exact authoritative record."""

    for record in _records():
        if record.get("source_id") == source_id and record.get("record_id") == record_id:
            return _project(record, show_content=show_content, score=None)
    raise ExpertQueryError(f"Record is absent: ({source_id!r}, {record_id!r})")


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line interface."""

    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("verify", help="Verify every expert binding")
    search_parser = subparsers.add_parser(
        "search",
        help="Search the profile and authoritative ledger",
    )
    search_parser.add_argument("--contains", required=True)
    search_parser.add_argument("--source-id")
    search_parser.add_argument("--type", dest="concept_type")
    search_parser.add_argument("--limit", type=int, default=10)
    search_parser.add_argument("--show-content", action="store_true")
    get_parser = subparsers.add_parser("get", help="Get one exact ledger record")
    get_parser.add_argument("--source-id", required=True)
    get_parser.add_argument("--record-id", required=True)
    get_parser.add_argument("--show-content", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Verify the expert and run one read-only operation."""

    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(encoding="utf-8")
    args = build_parser().parse_args(argv)
    try:
        verification = verify()
        if args.command == "verify":
            payload: Any = verification
        elif args.command == "search":
            payload = {
                "verification": verification,
                "results": search(
                    args.contains,
                    source_id=args.source_id,
                    concept_type=args.concept_type,
                    limit=args.limit,
                    show_content=args.show_content,
                ),
            }
        else:
            payload = {
                "verification": verification,
                "result": get_record(
                    args.source_id,
                    args.record_id,
                    show_content=args.show_content,
                ),
            }
    except (ExpertQueryError, OSError, UnicodeError, ValueError, TypeError) as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, sort_keys=True))
        return 2
    print(
        json.dumps(
            payload,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
            allow_nan=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
