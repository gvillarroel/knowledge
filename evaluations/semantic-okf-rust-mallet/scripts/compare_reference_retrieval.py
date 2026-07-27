#!/usr/bin/env python3
"""Compare original and reference-aware RustMallet retrieval exhaustively."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType
from typing import Any


SCHEMA_VERSION = "semantic-okf-rust-mallet-reference-parity/1.0"
MODES = ("bm25", "topic", "association", "fusion")


class ParityError(RuntimeError):
    """Describe an invalid input or a retrieval parity failure."""


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _load_runtime(name: str, path: Path) -> ModuleType:
    scripts = path.parent.resolve()
    sys.path.insert(0, str(scripts))
    try:
        specification = importlib.util.spec_from_file_location(name, path)
        if specification is None or specification.loader is None:
            raise ParityError(f"cannot load runtime: {path}")
        module = importlib.util.module_from_spec(specification)
        sys.modules[name] = module
        specification.loader.exec_module(module)
        return module
    finally:
        sys.path.remove(str(scripts))


def _questions(path: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ParityError(f"question row {number} is not an object")
        question_id = value.get("id")
        question = value.get("question")
        if not isinstance(question_id, str) or not isinstance(question, str):
            raise ParityError(f"question row {number} lacks id or question")
        rows.append({"question_id": question_id, "question": question})
    if not rows or len({row["question_id"] for row in rows}) != len(rows):
        raise ParityError("questions must be non-empty with unique IDs")
    return rows


def _normalized(payload: dict[str, Any]) -> dict[str, Any]:
    value = dict(payload)
    value.pop("snapshot", None)
    value["results"] = [
        {key: item[key] for key in item if key != "reference_id"}
        for item in payload.get("results", [])
    ]
    return value


def _tree_sha256(root: Path) -> str:
    rows = [
        (path.relative_to(root).as_posix(), _sha256_file(path))
        for path in sorted(root.rglob("*"))
        if path.is_file()
    ]
    encoded = json.dumps(
        rows, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def compare(args: argparse.Namespace) -> dict[str, Any]:
    original_runtime = _load_runtime(
        "rust_mallet_original_parity_runtime", args.original_runtime.resolve()
    )
    evolved_runtime = _load_runtime(
        "rust_mallet_evolved_parity_runtime", args.evolved_runtime.resolve()
    )
    original_bundle = args.original_bundle.resolve()
    evolved_bundle = args.evolved_bundle.resolve()
    original = original_runtime.load_snapshot(
        original_bundle, deep_validation=args.deep_validation
    )
    evolved = evolved_runtime.load_snapshot(
        evolved_bundle, deep_validation=args.deep_validation
    )
    references = getattr(evolved, "references_by_document", None)
    if not isinstance(references, dict) or len(references) != len(evolved.documents):
        raise ParityError("evolved snapshot has no complete reference dictionary")

    mismatches: list[dict[str, Any]] = []
    checked_references = 0
    reference_ids: set[str] = set()
    questions = _questions(args.questions.resolve())
    for row in questions:
        for top_k in args.top_k:
            for mode in MODES:
                old = original_runtime.search_snapshot(
                    original, row["question"], mode, top_k
                )
                new = evolved_runtime.search_snapshot(
                    evolved, row["question"], mode, top_k
                )
                for item in new.get("results", []):
                    document_id = item.get("document_id")
                    binding = references.get(document_id)
                    reference_id = item.get("reference_id")
                    if not isinstance(binding, dict) or reference_id != binding.get(
                        "reference_id"
                    ):
                        raise ParityError(
                            f"invalid reference binding for {row['question_id']} "
                            f"{mode}@{top_k}: {document_id}"
                        )
                    checked_references += 1
                    reference_ids.add(reference_id)
                if _normalized(old) != _normalized(new):
                    mismatches.append(
                        {
                            "question_id": row["question_id"],
                            "mode": mode,
                            "top_k": top_k,
                            "original_document_ids": [
                                item.get("document_id") for item in old.get("results", [])
                            ],
                            "evolved_document_ids": [
                                item.get("document_id") for item in new.get("results", [])
                            ],
                        }
                    )
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "pass" if not mismatches else "fail",
        "question_count": len(questions),
        "modes": list(MODES),
        "top_k": args.top_k,
        "comparison_count": len(questions) * len(MODES) * len(args.top_k),
        "mismatch_count": len(mismatches),
        "mismatches": mismatches,
        "reference_rows_checked": checked_references,
        "unique_reference_ids_returned": len(reference_ids),
        "reference_dictionary_count": len(references),
        "deep_validation": args.deep_validation,
        "original_bundle": {
            "path": str(original_bundle),
            "tree_sha256": _tree_sha256(original_bundle),
        },
        "evolved_bundle": {
            "path": str(evolved_bundle),
            "tree_sha256": _tree_sha256(evolved_bundle),
            "references_sha256": _sha256_file(
                evolved_bundle / "classical" / "references.json"
            ),
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--questions", type=Path, required=True)
    parser.add_argument("--original-bundle", type=Path, required=True)
    parser.add_argument("--evolved-bundle", type=Path, required=True)
    parser.add_argument("--original-runtime", type=Path, required=True)
    parser.add_argument("--evolved-runtime", type=Path, required=True)
    parser.add_argument("--top-k", type=int, action="append", required=True)
    parser.add_argument("--deep-validation", action="store_true")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if any(value < 1 or value > 1000 for value in args.top_k):
        parser.error("--top-k must be from 1 through 1000")
    if len(set(args.top_k)) != len(args.top_k):
        parser.error("--top-k values must be unique")
    return args


def main() -> int:
    args = parse_args()
    if args.output.exists() or args.output.is_symlink():
        raise SystemExit(f"output already exists: {args.output}")
    try:
        report = compare(args)
    except (ParityError, OSError, UnicodeError, ValueError, TypeError) as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, sort_keys=True))
        return 2
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
