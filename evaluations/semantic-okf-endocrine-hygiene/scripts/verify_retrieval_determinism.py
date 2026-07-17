#!/usr/bin/env python3
"""Compare two append-only retrieval runs after removing runtime-only timing and scores."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence


SCHEMA_VERSION = "semantic-okf-endocrine-hygiene-retrieval-determinism/1.0"


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict) or value.get("status") != "pass":
        raise ValueError(f"retrieval report did not pass: {path}")
    return value


def _summary_without_timing(value: Mapping[str, Any] | None) -> dict[str, Any] | None:
    return None if value is None else {key: item for key, item in value.items() if key != "timing_ms"}


def projection(report: Mapping[str, Any]) -> list[dict[str, Any]]:
    result = []
    for route in report["routes"]:
        result.append(
            {
                "family": route["family"],
                "route": route["route"],
                "status": route["status"],
                "overall": _summary_without_timing(route.get("overall")),
                "hard": _summary_without_timing(route.get("hard")),
                "queries": [
                    {
                        "question_id": query["question_id"],
                        "error": query["error"],
                        "paper_ids": query["paper_ids"],
                        "source_ids": query["source_ids"],
                        "paper_metrics": query["paper_metrics"],
                        "source_metrics": query["source_metrics"],
                        "evidence_validity": query["evidence_validity"],
                        "hits": [
                            {key: item for key, item in hit.items() if key != "score"}
                            for hit in query["hits"]
                        ],
                    }
                    for query in route["queries"]
                ],
            }
        )
    return result


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(content, encoding="utf-8", newline="\n")
    temporary.replace(path)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("first", type=Path)
    parser.add_argument("second", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    first = projection(load(args.first.resolve()))
    second = projection(load(args.second.resolve()))
    first_digest, second_digest = digest(first), digest(second)
    report = {
        "schema_version": SCHEMA_VERSION,
        "status": "pass" if first == second else "fail",
        "comparison_scope": "routes, rankings, evidence bindings, errors, and metrics; timing and floating runtime scores excluded",
        "first": {"path": args.first.as_posix(), "projection_sha256": first_digest},
        "second": {"path": args.second.as_posix(), "projection_sha256": second_digest},
        "equal": first == second,
    }
    atomic_write(args.output.resolve(), json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n")
    print(canonical_json(report))
    return 0 if report["equal"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
