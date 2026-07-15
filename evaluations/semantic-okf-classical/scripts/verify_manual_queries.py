#!/usr/bin/env python3
"""Run four independent read-only spot checks against a classical bundle."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "semantic-okf-classical-manual-query-verification/1.0"
CASES = [
    ("bm25", "Prize-Collecting Steiner Tree path retrieval exact mechanism"),
    ("topic", "community summaries global sensemaking hierarchical organization"),
    ("association", "corrupted graph irrelevant paths edge deletion robust retrieval"),
    ("fusion", "simple fact retrieval graph expansion noise complex interconnected reasoning"),
]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _tree(bundle: Path) -> str:
    entries = [
        {"path": path.relative_to(bundle).as_posix(), "sha256": _sha256(path)}
        for path in sorted(candidate for candidate in bundle.rglob("*") if candidate.is_file())
    ]
    encoded = json.dumps(entries, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _run(bundle: Path, script: Path, mode: str, query: str) -> dict[str, Any]:
    completed = subprocess.run(
        [sys.executable, str(script), str(bundle), "search", "--query", query, "--mode", mode, "--top-k", "5"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="strict",
        timeout=60,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(f"{mode} query failed: {completed.stderr.strip()}")
    value = json.loads(completed.stdout)
    hits = value.get("results", [])
    result = {
        "mode": mode,
        "query_sha256": hashlib.sha256(query.encode()).hexdigest(),
        "status": value.get("status"),
        "requested_mode": value.get("requested_mode"),
        "effective_mode": value.get("effective_mode"),
        "returned": value.get("returned"),
        "paper_ids": [hit.get("paper_id") for hit in hits],
        "record_ids": [hit.get("record_id") for hit in hits],
        "unique_paper_count": len({hit.get("paper_id") for hit in hits}),
        "all_evidence_paths_exist": all((bundle / Path(hit["concept_path"])).is_file() for hit in hits),
        "expansion": {
            "query_topics": len(value.get("expansion", {}).get("query_topics", [])),
            "topic_terms": len(value.get("expansion", {}).get("topic_terms", [])),
            "association_terms": len(value.get("expansion", {}).get("association_terms", [])),
        },
    }
    if result["status"] != "pass" or result["effective_mode"] != mode or result["returned"] != 5:
        raise ValueError(f"{mode} query violated its response contract")
    if not result["all_evidence_paths_exist"]:
        raise ValueError(f"{mode} query returned a missing concept path")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--consult-script", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(f"Refusing to replace verification output: {args.output}")
    before = _tree(args.bundle)
    results = [_run(args.bundle, args.consult_script, mode, query) for mode, query in CASES]
    after = _tree(args.bundle)
    if before != after:
        raise ValueError("Read-only query verification changed the bundle tree")
    by_mode = {item["mode"]: item for item in results}
    if by_mode["bm25"]["record_ids"][0] != "claim-2402-07630v3-007":
        raise ValueError("BM25 exact-mechanism check did not return the expected leading claim")
    if by_mode["fusion"]["record_ids"][0] != "claim-2506-05690v3-043":
        raise ValueError("Fusion routing check did not return the expected leading claim")
    if any(by_mode[mode]["unique_paper_count"] != 5 for mode in ("topic", "association", "fusion")):
        raise ValueError("Diversified modes did not return five distinct papers")
    report = {
        "schema_version": SCHEMA_VERSION,
        "status": "pass",
        "bundle_tree_before": before,
        "bundle_tree_after": after,
        "bundle_unchanged": True,
        "case_count": len(results),
        "results": results,
    }
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"status": "pass", "cases": len(results), "bundle_unchanged": True}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
