#!/usr/bin/env python3
"""Generate trace-backed native one-command builder proposals."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-skill", type=Path, required=True)
    parser.add_argument("--native-assets", type=Path, required=True)
    parser.add_argument("--protocol-assets", type=Path, required=True)
    parser.add_argument("--evidence-id", action="append", required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _proposal(
    *,
    identifier: str,
    diagnosis: str,
    conflict_group: str,
    target: str,
    operation: str,
    content: str,
    evidence_ids: list[str],
    old: str | None = None,
) -> dict[str, object]:
    proposal: dict[str, object] = {
        "id": identifier,
        "diagnosis": diagnosis,
        "domain": "build-correctness/execution-efficiency",
        "evidenceIds": evidence_ids,
        "conflictGroup": conflict_group,
        "target": target,
        "operation": operation,
        "content": content,
    }
    if old is not None:
        proposal["old"] = old
    return proposal


def proposal_document(
    baseline: Path,
    native_assets: Path,
    protocol_assets: Path,
    evidence_ids: list[str],
) -> dict[str, object]:
    unique_evidence = list(dict.fromkeys(evidence_ids))
    if len(unique_evidence) < 2:
        raise ValueError("at least two unique discovery evidence IDs are required")
    diagnosis = (
        "Qualified discovery traces had to build, validate, then manually derive, "
        "index, bind, and revalidate the reference dictionary. Native derivation "
        "closes that correctness gap, while one public build-and-validate command "
        "removes compensating inspection and repair calls before consultation."
    )
    replacements = (
        (
            "native-reference-dictionary-module",
            "reference-dictionary-module",
            "scripts/_reference_dictionary.py",
            native_assets / "_reference_dictionary.py",
            "create",
        ),
        (
            "native-reference-dictionary-pipeline",
            "classical-build-pipeline",
            "scripts/_rust_mallet_retrieval.py",
            native_assets / "_rust_mallet_retrieval.py",
            "replace",
        ),
        (
            "one-command-builder-protocol",
            "builder-instructions",
            "SKILL.md",
            protocol_assets / "SKILL.md",
            "replace",
        ),
        (
            "document-reference-artifact-format",
            "projection-format",
            "references/rust-mallet-format.md",
            native_assets / "rust-mallet-format.md",
            "replace",
        ),
        (
            "build-and-validate-wrapper",
            "builder-entrypoint",
            "scripts/build_validate_semantic_okf_rust_mallet.py",
            protocol_assets / "build_validate_semantic_okf_rust_mallet.py",
            "create",
        ),
    )
    proposals: list[dict[str, object]] = []
    for identifier, group, target, asset, operation in replacements:
        old = _read(baseline / target) if operation == "replace" else None
        content = _read(asset)
        if old == content:
            raise ValueError(f"candidate asset does not mutate {target}")
        proposals.append(
            _proposal(
                identifier=identifier,
                diagnosis=diagnosis,
                conflict_group=group,
                target=target,
                operation=operation,
                content=content,
                evidence_ids=unique_evidence,
                old=old,
            )
        )
    return {"proposals": proposals}


def main() -> int:
    args = parse_args()
    payload = proposal_document(
        args.baseline_skill.resolve(),
        args.native_assets.resolve(),
        args.protocol_assets.resolve(),
        args.evidence_id,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        json.dumps(
            {
                "output": str(args.output),
                "proposal_count": len(payload["proposals"]),
                "status": "pass",
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
