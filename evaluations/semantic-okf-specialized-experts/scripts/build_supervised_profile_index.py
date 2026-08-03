#!/usr/bin/env python3
"""Build a deterministic retrospective lexical-profile index for one expert."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
from typing import Any, Iterable, Mapping, Sequence


SCHEMA_VERSION = "semantic-okf-supervised-profile-index/1.0"
SUPPORTED_DATASETS = ("astro-40", "graphrag-papers-40")
TOKEN_RE = re.compile(r"[a-z0-9]+(?:[._/-][a-z0-9]+)*", re.IGNORECASE)
PAPER_ID_RE = re.compile(
    r"(?<!\d)(\d{4})[.-](\d{5})(v\d+)(?!\w)",
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


class ProfileIndexError(ValueError):
    """Describe an invalid input or a non-reproducible profile index."""


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
        allow_nan=False,
    ) + "\n"


def _read_json_object(path: Path, *, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ProfileIndexError(f"Cannot read {label} at {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ProfileIndexError(f"{label} must be a JSON object: {path}")
    return value


def _read_jsonl(path: Path, *, label: str) -> list[dict[str, Any]]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        raise ProfileIndexError(f"Cannot read {label} at {path}: {exc}") from exc
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ProfileIndexError(
                f"Invalid {label} JSON on line {line_number}: {exc}"
            ) from exc
        if not isinstance(value, dict):
            raise ProfileIndexError(
                f"{label} line {line_number} must be a JSON object"
            )
        rows.append(value)
    if not rows:
        raise ProfileIndexError(f"{label} is empty: {path}")
    return rows


def _tokens(text: str) -> list[str]:
    tokens: list[str] = []
    for raw in TOKEN_RE.findall(text.casefold()):
        token = raw.strip("._/-")
        if token:
            tokens.append(token)
    return tokens


def _features(text: str) -> set[str]:
    tokens = _tokens(text)
    features: set[str] = set()
    for size in range(1, 6):
        for offset in range(0, len(tokens) - size + 1):
            window = tokens[offset : offset + size]
            if size == 1 and window[0] in STOPWORDS:
                continue
            features.add(f"{size}:{' '.join(window)}")
    return features


def _paper_id(value: str) -> str | None:
    match = PAPER_ID_RE.search(value)
    if match is None:
        return None
    return f"{match.group(1)}.{match.group(2)}{match.group(3).lower()}"


def _validate_knowledge(knowledge: Path) -> tuple[Path, list[dict[str, Any]]]:
    report_path = knowledge / "semantic" / "build-report.json"
    ledger_path = knowledge / "semantic" / "records.jsonl"
    index_path = knowledge / "index.md"
    for path in (report_path, ledger_path, index_path):
        if not path.is_file():
            raise ProfileIndexError(f"Required knowledge file is absent: {path}")
    report = _read_json_object(report_path, label="knowledge build report")
    if report.get("status") != "pass" or report.get("valid") is not True:
        raise ProfileIndexError("Knowledge build report is not valid and passing")
    records = _read_jsonl(ledger_path, label="knowledge ledger")
    identities: set[tuple[str, str]] = set()
    for number, record in enumerate(records, start=1):
        source_id = record.get("source_id")
        record_id = record.get("record_id")
        if not isinstance(source_id, str) or not isinstance(record_id, str):
            raise ProfileIndexError(
                f"Knowledge ledger row {number} lacks source_id or record_id"
            )
        identity = (source_id, record_id)
        if identity in identities:
            raise ProfileIndexError(f"Duplicate knowledge identity: {identity!r}")
        identities.add(identity)
    summary = report.get("summary")
    if isinstance(summary, dict) and summary.get("records") != len(records):
        raise ProfileIndexError("Knowledge report and ledger record counts differ")
    return ledger_path, records


def _validate_questions(
    path: Path,
    dataset_id: str,
) -> list[dict[str, Any]]:
    questions = _read_jsonl(path, label="retrieval questions")
    if len(questions) != 40:
        raise ProfileIndexError(
            f"The canonical dataset requires 40 questions, found {len(questions)}"
        )
    identifiers: set[str] = set()
    qrel_key = "paper_ids" if dataset_id == "graphrag-papers-40" else "source_ids"
    for number, row in enumerate(questions, start=1):
        identifier = row.get("id")
        question = row.get("question")
        qrels = row.get("qrels")
        if (
            not isinstance(identifier, str)
            or not identifier
            or not isinstance(question, str)
            or not question
            or not isinstance(qrels, dict)
        ):
            raise ProfileIndexError(f"Question row {number} is incomplete")
        if identifier in identifiers:
            raise ProfileIndexError(f"Duplicate question identifier: {identifier}")
        identifiers.add(identifier)
        identities = qrels.get(qrel_key)
        if (
            not isinstance(identities, list)
            or not identities
            or not all(isinstance(item, str) and item for item in identities)
        ):
            raise ProfileIndexError(
                f"Question {identifier} has invalid {qrel_key} qrels"
            )
        if identities != sorted(set(identities)):
            raise ProfileIndexError(
                f"Question {identifier} {qrel_key} qrels are not sorted and unique"
            )
    return questions


def _profile_targets(
    dataset_id: str,
    records: Sequence[Mapping[str, Any]],
) -> dict[str, tuple[str, ...]]:
    if dataset_id == "astro-40":
        result: dict[str, tuple[str, ...]] = {}
        for record in records:
            source_id = str(record["source_id"])
            if source_id in result:
                raise ProfileIndexError(
                    f"Astro knowledge contains duplicate source_id: {source_id}"
                )
            result[source_id] = (source_id,)
        return result

    by_paper: dict[str, list[str]] = {}
    for record in records:
        source_id = str(record["source_id"])
        paper_id = _paper_id(source_id)
        if paper_id is None:
            raise ProfileIndexError(
                f"GraphRAG source lacks a paper identity: {source_id}"
            )
        by_paper.setdefault(paper_id, []).append(source_id)
    result = {
        paper_id: tuple(sorted(set(source_ids)))
        for paper_id, source_ids in sorted(by_paper.items())
    }
    if any(len(source_ids) < 1 for source_ids in result.values()):
        raise ProfileIndexError("GraphRAG paper target has no source records")
    return result


def build_index(
    *,
    dataset_id: str,
    knowledge: Path,
    questions_path: Path,
) -> dict[str, Any]:
    """Build one deterministic all-exposed-cohort profile index."""

    if dataset_id not in SUPPORTED_DATASETS:
        raise ProfileIndexError(f"Unsupported dataset: {dataset_id}")
    knowledge = knowledge.resolve()
    questions_path = questions_path.resolve()
    ledger_path, records = _validate_knowledge(knowledge)
    questions = _validate_questions(questions_path, dataset_id)
    targets = _profile_targets(dataset_id, records)
    profiles: dict[str, set[str]] = {
        str(record["source_id"]): set()
        for record in records
    }
    source_question_ids: dict[str, set[str]] = {
        source_id: set()
        for source_id in profiles
    }

    qrel_key = "paper_ids" if dataset_id == "graphrag-papers-40" else "source_ids"
    for row in questions:
        features = _features(str(row["question"]))
        if not features:
            raise ProfileIndexError(f"Question has no lexical features: {row['id']}")
        for identity in row["qrels"][qrel_key]:
            source_ids = targets.get(identity)
            if source_ids is None:
                raise ProfileIndexError(
                    f"Question {row['id']} references absent identity: {identity}"
                )
            for source_id in source_ids:
                profiles[source_id].update(features)
                source_question_ids[source_id].add(str(row["id"]))

    profile_rows = []
    for record in sorted(
        records,
        key=lambda item: (str(item["source_id"]), str(item["record_id"])),
    ):
        source_id = str(record["source_id"])
        profile_rows.append(
            {
                "source_id": source_id,
                "record_id": str(record["record_id"]),
                "question_ids": sorted(source_question_ids[source_id]),
                "features": sorted(profiles[source_id]),
            }
        )

    supervised = [row for row in profile_rows if row["features"]]
    return {
        "schema_version": SCHEMA_VERSION,
        "dataset_id": dataset_id,
        "candidate_state": "retrospective-all-exposed-supervised-profile",
        "promotion_eligible": False,
        "knowledge": {
            "ledger_path": "references/knowledge/semantic/records.jsonl",
            "ledger_sha256": _sha256_file(ledger_path),
            "record_count": len(records),
        },
        "development_evidence": {
            "questions_path": questions_path.name,
            "questions_sha256": _sha256_file(questions_path),
            "question_count": len(questions),
            "scope": "all 40 exposed canonical questions and their reviewed qrels",
            "holdout_status": "none; this index is retrospective and cannot promote",
        },
        "retrieval": {
            "max_ngram": 5,
            "ngram_weights": NGRAM_WEIGHTS,
            "profile_score_multiplier": 1_000_000.0,
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
            "supervised_profile_count": len(supervised),
            "feature_assignment_count": sum(
                len(row["features"])
                for row in profile_rows
            ),
            "question_assignment_count": sum(
                len(row["question_ids"])
                for row in profile_rows
            ),
        },
        "profiles": profile_rows,
    }


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line interface."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-id", choices=SUPPORTED_DATASETS, required=True)
    parser.add_argument("--knowledge", type=Path, required=True)
    parser.add_argument("--questions", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Rebuild in memory and compare with the existing output",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Build or check a supervised profile index."""

    args = build_parser().parse_args(argv)
    try:
        payload = build_index(
            dataset_id=args.dataset_id,
            knowledge=args.knowledge,
            questions_path=args.questions,
        )
        rendered = _canonical_json(payload)
        if args.check:
            if not args.output.is_file():
                raise ProfileIndexError("--check requires an existing output file")
            existing = args.output.read_text(encoding="utf-8")
            if existing != rendered:
                raise ProfileIndexError("Profile index is not reproducible")
            status = "pass"
        else:
            if args.output.exists() or args.output.is_symlink():
                raise ProfileIndexError(f"Output already exists: {args.output}")
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(
                rendered,
                encoding="utf-8",
                newline="\n",
            )
            status = "created"
    except (ProfileIndexError, OSError, UnicodeError) as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, sort_keys=True))
        return 2
    print(
        json.dumps(
            {
                "status": status,
                "dataset_id": args.dataset_id,
                "output": str(args.output),
                "sha256": _sha256_file(args.output),
                "profile_count": payload["summary"]["profile_count"],
                "supervised_profile_count": payload["summary"][
                    "supervised_profile_count"
                ],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
