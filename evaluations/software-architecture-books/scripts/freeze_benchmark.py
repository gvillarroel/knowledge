#!/usr/bin/env python3
"""Freeze hash-only hard evidence from the private page-addressable corpus."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
from typing import Any, Mapping, Sequence
import unicodedata


ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parents[1]
DATASET_ID = "software-architecture-books-40"
BLUEPRINT = ROOT / "benchmark" / "hard-ground-truth-blueprint.json"
QUESTIONS = ROOT / "benchmark" / "retrieval-questions.jsonl"
OUTPUT = ROOT / "benchmark" / "hard-ground-truth.jsonl"
SOURCES = ROOT / "processed" / "sources" / "markdown"
PAGE_RE = re.compile(r"(?m)^## PDF page (\d+)\s*$")


class FreezeError(ValueError):
    """Raised when reviewed benchmark evidence cannot be frozen exactly."""


def sha256_bytes(value: bytes) -> str:
    """Return a lowercase SHA-256 digest."""

    return hashlib.sha256(value).hexdigest()


def normalized_text(path: Path) -> str:
    """Read one prepared source under the same normalization used by the corpus."""

    return unicodedata.normalize(
        "NFC",
        path.read_text(encoding="utf-8")
        .replace("\r\n", "\n")
        .replace("\r", "\n"),
    )


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    """Load a sequence of JSON objects."""

    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(),
        start=1,
    ):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise FreezeError(f"{path} line {line_number} is not an object")
        rows.append(value)
    return rows


def page_span(text: str, page_number: int) -> tuple[int, int, str]:
    """Resolve one exact trimmed Markdown page passage."""

    matches = list(PAGE_RE.finditer(text))
    matching = [
        (index, match)
        for index, match in enumerate(matches)
        if int(match.group(1)) == page_number
    ]
    if len(matching) != 1:
        raise FreezeError(f"PDF page {page_number} is absent or duplicated")
    index, match = matching[0]
    start = match.start()
    end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
    while start < end and text[start].isspace():
        start += 1
    while end > start and text[end - 1].isspace():
        end -= 1
    passage = text[start:end]
    if not passage.startswith(f"## PDF page {page_number}"):
        raise FreezeError(f"PDF page {page_number} has an invalid passage boundary")
    return start, end, passage


def load_questions() -> dict[str, dict[str, Any]]:
    """Load the hard-question qrels keyed by full identifier."""

    result: dict[str, dict[str, Any]] = {}
    for index, row in enumerate(load_jsonl(QUESTIONS), start=1):
        identifier = row.get("id")
        if not isinstance(identifier, str) or not identifier.startswith(
            f"q{index:03d}-"
        ):
            raise FreezeError(f"Question order or identity drift at row {index}")
        if index >= 31:
            result[identifier] = row
    if len(result) != 10:
        raise FreezeError("The hard cohort must contain exactly ten questions")
    return result


def validate_claim_groups(
    identifier: str,
    groups: Any,
    evidence_ids: set[str],
    label: str,
) -> list[dict[str, Any]]:
    """Validate paraphrased claims and their evidence bindings."""

    if not isinstance(groups, list) or (label == "answer_claims" and not groups):
        raise FreezeError(f"{identifier}: invalid {label}")
    normalized: list[dict[str, Any]] = []
    seen: set[str] = set()
    for group in groups:
        if not isinstance(group, dict) or set(group) != {
            "id",
            "statement",
            "evidence_ids",
        }:
            raise FreezeError(f"{identifier}: invalid {label} row")
        claim_id = group["id"]
        statement = group["statement"]
        bound = group["evidence_ids"]
        if (
            not isinstance(claim_id, str)
            or claim_id in seen
            or not isinstance(statement, str)
            or not statement.strip()
            or not isinstance(bound, list)
            or not bound
            or any(item not in evidence_ids for item in bound)
        ):
            raise FreezeError(f"{identifier}: invalid {label} binding")
        seen.add(claim_id)
        normalized.append(
            {
                "id": claim_id,
                "statement": statement.strip(),
                "evidence_ids": list(bound),
            }
        )
    return normalized


def freeze() -> list[dict[str, Any]]:
    """Materialize the common Harbor hard-truth schema without source excerpts."""

    blueprint = json.loads(BLUEPRINT.read_text(encoding="utf-8"))
    rows = blueprint.get("rows") if isinstance(blueprint, dict) else None
    if (
        blueprint.get("schema_version")
        != "private-book-hard-ground-truth-blueprint/1.0"
        or blueprint.get("dataset_id") != DATASET_ID
        or not isinstance(rows, list)
        or len(rows) != 10
    ):
        raise FreezeError("Hard-ground-truth blueprint is invalid")
    questions = load_questions()
    result: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            raise FreezeError("Hard-ground-truth blueprint row is invalid")
        identifier = row.get("id")
        if not isinstance(identifier, str) or identifier not in questions:
            raise FreezeError(f"Unknown hard question: {identifier!r}")
        required = row.get("required_document_ids")
        question_qrels = questions[identifier].get("qrels")
        expected_documents = (
            question_qrels.get("document_ids")
            if isinstance(question_qrels, Mapping)
            else None
        )
        if (
            not isinstance(required, list)
            or required != sorted(set(required))
            or required != expected_documents
        ):
            raise FreezeError(f"{identifier}: required document drift")
        evidence_rows = row.get("evidence")
        if not isinstance(evidence_rows, list) or not evidence_rows:
            raise FreezeError(f"{identifier}: no reviewed evidence")
        authoritative: list[dict[str, Any]] = []
        evidence_ids: set[str] = set()
        covered_documents: set[str] = set()
        for evidence in evidence_rows:
            if not isinstance(evidence, dict) or set(evidence) != {
                "id",
                "document_id",
                "page_number",
                "interpretation",
            }:
                raise FreezeError(f"{identifier}: invalid evidence blueprint row")
            evidence_id = evidence["id"]
            document_id = evidence["document_id"]
            page_number = evidence["page_number"]
            interpretation = evidence["interpretation"]
            if (
                not isinstance(evidence_id, str)
                or evidence_id in evidence_ids
                or document_id not in required
                or not isinstance(page_number, int)
                or page_number <= 0
                or not isinstance(interpretation, str)
                or not interpretation.strip()
            ):
                raise FreezeError(f"{identifier}: invalid evidence identity")
            source_path = SOURCES / f"{document_id}.md"
            if not source_path.is_file() or source_path.is_symlink():
                raise FreezeError(f"{identifier}: private source is absent: {source_path}")
            text = normalized_text(source_path)
            start, end, passage = page_span(text, page_number)
            relative_path = source_path.relative_to(REPO_ROOT).as_posix()
            source_id = f"book-{document_id}"
            authoritative.append(
                {
                    "id": evidence_id,
                    "source_id": source_id,
                    "record_id": f"processed/sources/markdown/{document_id}",
                    "document_id": document_id,
                    "path": relative_path,
                    "locator": f"PDF-page-{page_number}",
                    "page_number": page_number,
                    "start_char": start,
                    "end_char": end,
                    "text_length": len(passage),
                    "file_sha256": sha256_bytes(text.encode("utf-8")),
                    "text_sha256": sha256_bytes(passage.encode("utf-8")),
                    "interpretation": interpretation.strip(),
                }
            )
            evidence_ids.add(evidence_id)
            covered_documents.add(document_id)
        if covered_documents != set(required):
            raise FreezeError(f"{identifier}: reviewed evidence misses a qrel document")
        answer_claims = validate_claim_groups(
            identifier,
            row.get("answer_claims"),
            evidence_ids,
            "answer_claims",
        )
        important_negatives = validate_claim_groups(
            identifier,
            row.get("important_negatives"),
            evidence_ids,
            "important_negatives",
        )
        derivation = row.get("derivation")
        acceptable = row.get("acceptable_variants")
        if not isinstance(derivation, list) or not isinstance(acceptable, list):
            raise FreezeError(f"{identifier}: invalid derivation or variants")
        result.append(
            {
                "schema_version": "semantic-okf-hard-ground-truth/1.0",
                "id": identifier,
                "question": questions[identifier]["question"],
                "authoritative_evidence": authoritative,
                "ground_truth": {
                    "required_document_ids": required,
                    "required_source_ids": [f"book-{item}" for item in required],
                    "answer_claims": answer_claims,
                    "important_negatives": important_negatives,
                    "derivation": derivation,
                    "acceptable_variants": acceptable,
                },
            }
        )
    if [row["id"] for row in result] != list(questions):
        raise FreezeError("Hard-ground-truth blueprint order drift")
    return result


def render(rows: Sequence[Mapping[str, Any]]) -> str:
    """Render canonical compact JSON Lines."""

    return "\n".join(
        json.dumps(
            row,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        for row in rows
    ) + "\n"


def build_parser() -> argparse.ArgumentParser:
    """Build the hard-truth freezing command line."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Verify that the accepted hash-only hard truth is reproducible.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Freeze or check the reviewed private benchmark evidence."""

    args = build_parser().parse_args(argv)
    try:
        payload = render(freeze())
        if args.check:
            if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != payload:
                raise FreezeError("Frozen hard ground truth is absent or has drifted")
            status = "pass"
        else:
            OUTPUT.parent.mkdir(parents=True, exist_ok=True)
            OUTPUT.write_text(payload, encoding="utf-8", newline="\n")
            status = "created"
        result = {
            "status": status,
            "dataset_id": DATASET_ID,
            "hard_question_count": 10,
            "output": OUTPUT.relative_to(REPO_ROOT).as_posix(),
            "output_sha256": sha256_bytes(payload.encode("utf-8")),
        }
    except (FreezeError, OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, sort_keys=True))
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
