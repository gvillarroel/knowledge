#!/usr/bin/env python3
"""Publish a contract-validated final view of an already completed EnterpriseRAG run."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import build_report_catalog as catalog


def main() -> int:
    """Render a final publication without changing any raw measurements."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    specs = json.loads((catalog.REPO / "evaluations/report-sources.json").read_text(encoding="utf-8"))["datasets"]
    spec = next(spec for spec in specs if spec["format"] == "enterprise-json")
    group = catalog.load_dataset(spec)
    original = json.loads((catalog.REPO / spec["path"]).read_text(encoding="utf-8"))
    contract, primary = catalog.comparison_projection(group)
    contract["report"] = "final-report.md"
    lines = ["# EnterpriseRAG-Bench reduced-corpus evaluation", "", *primary, "", group["scope"], "",
             "All eight unchanged build/consult families passed two builds and independent validation. "
             "All 18 routes completed 40 questions in three repetitions: 2,160 query executions. "
             "Authoritative record identities and hashes were checked before scoring.", "",
             "## Category diagnostics", "",
             "Each category contains five selected questions. Highest observed nDCG@10 is descriptive at this small denominator; "
             "ties are retained and categories are not independent organization-level samples.", "",
             "| Category | Questions | Highest observed route(s) | nDCG@10 |", "|---|---:|---|---:|"]
    for category in sorted(original["ranking"][0]["categories"]):
        best = max(row["categories"][category]["ndcg_at_10"] for row in original["ranking"])
        routes = [row["strategy_id"] for row in original["ranking"] if row["categories"][category]["ndcg_at_10"] == best]
        lines.append(f"| {category.replace('_', ' ')} | 5 | {'; '.join(sorted(routes))} | {100 * best:.2f}% |")
    lines.extend(["", "## Cost, time, and integrity", "",
                  "Provider cost: **USD 0.00**. Model calls: **0**. LLM tokens: **0**. "
                  "Local machine cost and generated-answer correctness were not measured. "
                  "Embeddings use deterministic 384-dimensional hashing; Turso uses the actual pinned Turso engine.", "",
                  "P95 excludes process initialization and uses repeated-query caches within a fresh process per route. "
                  "The shared workstation also ran repository validation during part of this measurement. "
                  "Treat latency as local diagnostic evidence, not a controlled hardware comparison or a speed winner.", "",
                  "Every family rebuilt byte-identically, including the Turso database. The independent Turso validator "
                  "also checked its logical database contents. Input and executable hashes were checked before and after scoring.", "",
                  "## Dataset and interpretation", "",
                  "The pinned archive contains 511,962 document files. This derived dataset contains 985 documents: "
                  "85 reference documents and 900 deterministic distractors. Forty questions cover eight grounded categories. "
                  "The full 500-question bank and complete archive remain local. Four colliding document IDs are quarantined; "
                  "one repeated upstream qrel entry has set semantics. No ambiguous ID was required by the selected questions.", "",
                  "The reference-enriched corpus is not the official full-corpus Onyx benchmark. "
                  "High-level and information-not-found categories require separate answer/abstention evaluation. "
                  "No skill was evolved, no gold answer entered the builder input, and no promotion is claimed.", "",
                  "[Aggregate run details](comparison.json) · [Validated table contract](final-report.comparison.json) · "
                  "[Dataset guide](../../../../docs/evaluation-datasets-and-reports.md) · "
                  "[Cross-dataset hub](../../../reports/README.md)", ""])
    root = (catalog.REPO / spec["path"]).parent
    files = {"final-report.md": "\n".join(lines),
             "final-report.comparison.json": json.dumps(contract, indent=2, sort_keys=True, allow_nan=False) + "\n"}
    for name, text in files.items():
        path = root / name
        if args.check:
            if not path.exists() or path.read_text(encoding="utf-8") != text:
                raise ValueError("final publication drift")
        else:
            if path.exists():
                raise ValueError("final publication exists; use --check")
            path.write_text(text, encoding="utf-8", newline="\n")
    print(json.dumps({"status": "pass", "alternatives": len(contract["alternatives"])}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
