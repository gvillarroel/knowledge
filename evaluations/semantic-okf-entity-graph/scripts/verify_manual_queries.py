#!/usr/bin/env python3
"""Run four independent read-only spot checks against an entity-graph bundle."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "semantic-okf-entity-graph-manual-query-verification/1.0"
CASES = [
    ("lexical", "Prize-Collecting Steiner Tree path retrieval exact mechanism"),
    ("entity", "community summaries global sensemaking hierarchical organization"),
    ("traversal", "corrupted graph irrelevant paths edge deletion robust retrieval"),
    ("fusion", "simple fact retrieval graph expansion noise complex interconnected reasoning"),
]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


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
    section_rows = {
        row["section_id"]: row
        for row in _load_jsonl(bundle / "entity-graph" / "sections.jsonl")
    }
    exact_sections = []
    for hit in hits:
        canonical = section_rows.get(hit["section_id"], {})
        canonical_locator = {
            key: value for key, value in canonical.get("locator", {}).items() if key != "fragment"
        }
        exact_sections.append(
            hit.get("source_path") == canonical.get("source_path")
            and hit.get("locator") == canonical_locator
            and hit.get("text") == canonical.get("text")
            and hit.get("text_sha256") == canonical.get("text_sha256")
            and hashlib.sha256(hit["text"].encode("utf-8")).hexdigest() == hit["text_sha256"]
        )
    resolved_claim_ids = sorted(
        entity["record_id"]
        for entity in value.get("resolved_entities", [])
        if entity.get("entity_type") == "claim"
        and entity.get("review_state") == "reviewed"
        and isinstance(entity.get("record_id"), str)
    )
    result = {
        "mode": mode,
        "query_sha256": hashlib.sha256(query.encode()).hexdigest(),
        "status": value.get("status"),
        "requested_mode": value.get("requested_mode"),
        "effective_mode": value.get("effective_mode"),
        "returned": value.get("returned"),
        "paper_ids": [hit.get("paper_id") for hit in hits],
        "section_ids": [hit.get("section_id") for hit in hits],
        "ordinals": [hit.get("ordinal") for hit in hits],
        "unique_paper_count": len({hit.get("paper_id") for hit in hits}),
        "all_concept_paths_exist": all((bundle / Path(hit["concept_path"])).is_file() for hit in hits),
        "all_sections_exact": all(exact_sections),
        "reviewed_claim_ids": resolved_claim_ids,
        "reviewed_claim_count": len(resolved_claim_ids),
        "snapshot": value.get("snapshot"),
        "discovery_only": value.get("discovery_only"),
    }
    if result["status"] != "pass" or result["effective_mode"] != mode or result["returned"] != 5:
        raise ValueError(f"{mode} query violated its response contract")
    if not result["all_concept_paths_exist"] or not result["all_sections_exact"]:
        raise ValueError(f"{mode} query returned an invalid exact section")
    if result["discovery_only"] is not True or not result["snapshot"].get("entity_graph_index_sha256"):
        raise ValueError(f"{mode} query did not expose the derived-snapshot boundary")
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
    expected_top_papers = {
        "lexical": "2402.07630v3",
        "entity": "2404.16130v2",
        "traversal": "2502.14902v2",
        "fusion": "2506.05690v3",
    }
    for mode, paper_id in expected_top_papers.items():
        if by_mode[mode]["paper_ids"][0] != paper_id:
            raise ValueError(f"{mode} check did not return expected leading paper {paper_id}")
    if any(by_mode[mode]["unique_paper_count"] != 5 for mode, _ in CASES):
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
