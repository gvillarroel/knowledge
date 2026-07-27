#!/usr/bin/env python3
"""Generate the trace-backed preserving-prepare consult mutation contract."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parents[1]
REPO = HERE.parents[1]
ASSETS = HERE / "evolution-assets" / "consult-preserving-prepare"
BASELINE = REPO / "skills" / "consult-semantic-okf-rust-mallet-evolved"
EVIDENCE_IDS = (
    "rust-mallet-reference-contract-consult-c-trace-discovery:"
    "0d335fa1-6b67-42a8-aa18-7d3a32fe734f",
    "rust-mallet-reference-contract-consult-c-trace-discovery:"
    "6ba14aad-9bd7-4538-8339-9ff11e1a9000",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument(
        "--evidence-id",
        action="append",
        dest="evidence_ids",
        help=(
            "Eligible discovery evidence ID. Repeat for at least two unique "
            "trials and tasks. Defaults to the checked Spark discovery cohort."
        ),
    )
    return parser.parse_args()


def proposal_document(
    evidence_ids: tuple[str, ...] = EVIDENCE_IDS,
) -> dict[str, list[dict[str, Any]]]:
    if len(evidence_ids) < 2 or len(set(evidence_ids)) != len(evidence_ids):
        raise ValueError("at least two unique evidence IDs are required")
    diagnosis = (
        "Both qualified discovery traces reached strong semantic rewards only "
        "after separate search and show calls, while also spending calls on help "
        "or source inspection. A single public preparation operation can remove "
        "that repeated orchestration without discarding the successful search "
        "interpretations, selected full text, or bounded breadth buffer."
    )
    return {
        "proposals": [
            {
                "id": "preserve-search-guidance-and-selected-text",
                "diagnosis": diagnosis,
                "domain": "execution-efficiency/context-budget",
                "evidenceIds": list(evidence_ids),
                "conflictGroup": "preserving-prepare-helper",
                "target": "scripts/prepare_reference_consult.py",
                "operation": "create",
                "content": (
                    ASSETS / "prepare_reference_consult.py"
                ).read_text(encoding="utf-8"),
            },
            {
                "id": "document-preserving-prepare-protocol",
                "diagnosis": diagnosis,
                "domain": "execution-efficiency/context-budget",
                "evidenceIds": list(evidence_ids),
                "conflictGroup": "preserving-prepare-protocol",
                "target": "SKILL.md",
                "operation": "replace",
                "old": (BASELINE / "SKILL.md").read_text(encoding="utf-8"),
                "content": (ASSETS / "SKILL.md").read_text(encoding="utf-8"),
            },
        ]
    }


def main() -> int:
    args = parse_args()
    evidence_ids = tuple(args.evidence_ids or EVIDENCE_IDS)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(
            proposal_document(evidence_ids),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        json.dumps(
            {"status": "pass", "output": str(args.output), "proposal_count": 2},
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
