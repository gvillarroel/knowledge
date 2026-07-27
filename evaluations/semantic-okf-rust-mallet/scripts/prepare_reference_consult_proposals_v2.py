#!/usr/bin/env python3
"""Generate the operational-expansion reference-consultant proposal set."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


NEW_SKILL = """---
name: consult-semantic-okf-rust-mallet-evolved
description: Consult an immutable reference-dictionary RustMallet Semantic OKF snapshot through one bounded preparation and reference-ID evidence. Use for multi-paper synthesis, probabilistic-topic discovery, and evidence JSON whose identities must remain byte-exact. This standalone skill is read-only and never builds, repairs, refreshes, or modifies knowledge.
---

# Consult Semantic OKF RustMallet Evolved

Prepare one bounded evidence set, synthesize only from that text, and return the
snapshot-owned IDs without copying long identity fields through model text.

## Read-only contract

- Use only this skill and the supplied external bundle.
- Never write a cache, query, draft, answer, lock, or derived file inside the bundle.
- Treat retrieval scores as discovery signals, never as factual support.
- Stop on any snapshot validation, dictionary, digest, locator, or path error.
- Never reconstruct or copy `source_id`, paths, locators, or hashes manually.

## Exact answer protocol

When the request requires evidence JSON, follow only this bounded protocol:

1. Copy `MINIMUM` exactly from the request's required independent-paper count.
   Do not use a number from this skill or increase it for extra breadth.
2. Do not list the skill or bundle, invoke `-h`, read helper source, inspect
   reference documents, run deep validation, install packages, open concept
   pages, or invoke the legacy query helper. The commands below are complete.
3. Run exactly one `prepare` call with the complete question and `MINIMUM`.
   The helper performs compact BM25 retrieval, deterministic operational query
   expansion, independent-source recommendation, and selected-text loading in
   one operation. Use its `selected` array unchanged and do not search again.
4. Draft outside the bundle with exactly `question_id`, `summary`, and `claims`.
   Each claim contains exactly `statement` and `reference_ids`. Ground every claim
   in shown text, use every selected reference, and introduce no unshown fact.
5. Run `finalize` once with the same `MINIMUM` and without
   `--output`. Its stdout is one canonical JSON line whose evidence rows contain
   exactly `reference_id`. Use that exact line as the terminal response: do not
   expand IDs, open a file, pretty-print, retype, normalize, or reconstruct any
   character. The task verifier resolves the IDs from the mounted snapshot before
   applying the legacy exact-evidence checks. If finalization rejects the draft,
   correct only the draft; do not resume discovery.

Use the installed skill path and keep temporary files outside the snapshot:

```bash
SKILL_DIR="$HOME/.agents/skills/consult-semantic-okf-rust-mallet-evolved"
MINIMUM="<integer copied from the request>"
python -B "$SKILL_DIR/scripts/reference_consult.py" prepare BUNDLE \\
  --query "FULL QUESTION" --minimum-sources "$MINIMUM"
python -B "$SKILL_DIR/scripts/reference_consult.py" finalize BUNDLE \\
  /tmp/reference-draft.json --minimum-sources "$MINIMUM"
```

`prepare` returns only the selected IDs, source identities, and authoritative
text. `finalize` validates every ID against the current
`classical/references.json`, enforces independent-source breadth and first-use
order, and emits only those IDs. The verifier, not the model, resolves the seven
exact evidence fields from the same dictionary.

## Other consultation

Use `scripts/query_semantic_okf_rust_mallet.py` for ordinary read-only discovery
or when the user explicitly asks for index diagnostics, topic activations,
associations, or an integrity audit. Deep validation is restricted to an
explicitly requested integrity audit.

## Completion gate

Before returning evidence JSON, confirm that:

- exactly one `prepare` call was used and no inspection/help call was used;
- the minimum count passed to both commands exactly matches the request;
- every selected reference appears in at least one grounded claim;
- `finalize` succeeded against the current dictionary; and
- the one-line finalized stdout is the unchanged terminal response.
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-skill", type=Path, required=True)
    parser.add_argument("--helper-source", type=Path, required=True)
    parser.add_argument(
        "--evidence-id",
        action="append",
        required=True,
        help="eligible discovery evidence ID; pass exactly twice",
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if len(args.evidence_id) != 2 or len(set(args.evidence_id)) != 2:
        parser.error("--evidence-id must provide exactly two unique IDs")
    return args


def proposal(
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
        "domain": "execution-efficiency/context-budget",
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
    baseline = (args.baseline_skill / "SKILL.md").read_text(encoding="utf-8")
    if baseline == NEW_SKILL:
        raise SystemExit("the baseline already contains the proposed protocol")
    helper = args.helper_source.read_text(encoding="utf-8")
    baseline_helper_path = (
        args.baseline_skill / "scripts" / "reference_consult.py"
    )
    if baseline_helper_path.is_file():
        helper_operation = "replace"
        helper_old = baseline_helper_path.read_text(encoding="utf-8")
    else:
        helper_operation = "create"
        helper_old = None
    payload = {
        "proposals": [
            proposal(
                identifier="single-prepare-reference-answer-contract",
                diagnosis=(
                    "Both qualified discovery traces resolved every compact reference "
                    "but used eight and ten tool calls. Each separately searched and "
                    "loaded evidence and also spent calls on listings, help, or helper "
                    "source. A single prepare operation can retain the same deterministic "
                    "recommendation while loading only its selected text."
                ),
                conflict_group="reference-consult-helper",
                target="scripts/reference_consult.py",
                operation=helper_operation,
                content=helper,
                evidence_ids=args.evidence_id,
                old=helper_old,
            ),
            proposal(
                identifier="exact-minimum-two-command-protocol",
                diagnosis=(
                    "The q007 trace used minimum five and cited seven papers even though "
                    "its request required four; q019 used five as requested. Both traces "
                    "also performed redundant inspection before successful finalization. "
                    "The protocol should copy the request minimum exactly and expose only "
                    "prepare, one external draft write, and finalize."
                ),
                conflict_group="consultation-workflow",
                target="SKILL.md",
                operation="replace",
                old=baseline,
                content=NEW_SKILL,
                evidence_ids=args.evidence_id,
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
