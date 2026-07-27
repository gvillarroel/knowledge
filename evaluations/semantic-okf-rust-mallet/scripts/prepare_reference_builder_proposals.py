#!/usr/bin/env python3
"""Generate trace-grounded proposals for native reference-dictionary builds."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-skill", type=Path, required=True)
    parser.add_argument("--asset-directory", type=Path, required=True)
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
    result: dict[str, object] = {
        "id": identifier,
        "diagnosis": diagnosis,
        "domain": "build-correctness/reference-integrity",
        "evidenceIds": evidence_ids,
        "conflictGroup": conflict_group,
        "target": target,
        "operation": operation,
        "content": content,
    }
    if old is not None:
        result["old"] = old
    return result


def main() -> int:
    args = parse_args()
    if len(set(args.evidence_id)) < 2:
        raise SystemExit("at least two unique discovery evidence IDs are required")
    baseline = args.baseline_skill.resolve()
    assets = args.asset_directory.resolve()
    replacements = (
        ("scripts/_rust_mallet_retrieval.py", "_rust_mallet_retrieval.py"),
        ("SKILL.md", "SKILL.md"),
        ("references/rust-mallet-format.md", "rust-mallet-format.md"),
    )
    for target, asset in replacements:
        if _read(baseline / target) == _read(assets / asset):
            raise SystemExit(f"candidate asset does not mutate {target}")

    shared_diagnosis = (
        "Both qualified discovery traces completed only after the agent manually "
        "derived, wrote, indexed, and validated a reference dictionary after the "
        "builder had published its six-file projection (57 calls for q007 and 41 "
        "calls for q019). Native atomic derivation removes that compensating repair "
        "and makes exact reference coverage part of the builder's closed validator."
    )
    evidence_ids = list(dict.fromkeys(args.evidence_id))
    payload = {
        "proposals": [
            _proposal(
                identifier="native-reference-dictionary-module",
                diagnosis=shared_diagnosis,
                conflict_group="reference-dictionary-module",
                target="scripts/_reference_dictionary.py",
                operation="create",
                content=_read(assets / "_reference_dictionary.py"),
                evidence_ids=evidence_ids,
            ),
            _proposal(
                identifier="atomic-reference-dictionary-build-and-validation",
                diagnosis=shared_diagnosis,
                conflict_group="classical-build-pipeline",
                target="scripts/_rust_mallet_retrieval.py",
                operation="replace",
                old=_read(baseline / "scripts/_rust_mallet_retrieval.py"),
                content=_read(assets / "_rust_mallet_retrieval.py"),
                evidence_ids=evidence_ids,
            ),
            _proposal(
                identifier="document-native-reference-build-contract",
                diagnosis=(
                    shared_diagnosis
                    + " The operational contract must name the seventh artifact and "
                    "require its deterministic one-to-one coverage before delivery."
                ),
                conflict_group="builder-instructions",
                target="SKILL.md",
                operation="replace",
                old=_read(baseline / "SKILL.md"),
                content=_read(assets / "SKILL.md"),
                evidence_ids=evidence_ids,
            ),
            _proposal(
                identifier="document-reference-artifact-format",
                diagnosis=(
                    shared_diagnosis
                    + " The format reference must close the schema, ID derivation, "
                    "and stale-or-colliding binding failure rules."
                ),
                conflict_group="projection-format",
                target="references/rust-mallet-format.md",
                operation="replace",
                old=_read(baseline / "references/rust-mallet-format.md"),
                content=_read(assets / "rust-mallet-format.md"),
                evidence_ids=evidence_ids,
            ),
        ]
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
