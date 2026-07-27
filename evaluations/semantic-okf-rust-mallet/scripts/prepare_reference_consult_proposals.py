#!/usr/bin/env python3
"""Generate trace-grounded proposals for the reference-aware consultant."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


DISCOVERY_EVIDENCE_IDS = (
    "rust-mallet-reference-consult-trace-discovery:"
    "e89f2318-483f-472d-a908-a7e70812bae1",
    "rust-mallet-reference-consult-trace-discovery:"
    "b3226e61-bcbf-4f70-85c1-362f56cb60c4",
)

OLD_WORKFLOW = """## Workflow

1. Inspect the snapshot; require a passing core and RustMallet projection. For a newly received or evaluation-critical snapshot, add `--deep-validation` once to independently retrain fixed-seed LDA and rederive every document, lexical statistic, PPMI edge, topic, and document-topic weight.
2. Select the cheapest authoritative or discovery layer.
3. Apply source, concept, and type filters before ranking.
4. Use `bm25`, `topic`, `association`, or `fusion` for candidate discovery.
5. Preserve each returned compact `reference_id`, requested/effective mode, query expansions, topic activations, index hashes, and component ranks.
6. Open the exact returned `concept_path`; resolve its locator to authoritative record text.
7. Use the ledger for exact metadata or selected RDF graphs for joins, aggregation, schema, lineage, shapes, or validation.
8. Cite authoritative paths and page locators. Never cite a retrieval score as factual support.

## Environment and inspection

Install the pinned `pyrmallet==0.1.1` runtime before inspection or search:

```bash
python scripts/runtime_smoke.py
python scripts/query_semantic_okf_rust_mallet.py BUNDLE inspect
python scripts/query_semantic_okf_rust_mallet.py BUNDLE inspect --deep-validation
```

Resolve selected compact IDs through the snapshot-owned dictionary instead of
copying identity fields from search output or rebuilding them manually:

```bash
python scripts/query_semantic_okf_rust_mallet.py BUNDLE resolve \\
  --reference-id ref-0123456789abcdef01234567
```

`classical/references.json` is processed snapshot data. The consultant validates
its complete one-to-one document coverage, deterministic IDs, exact evidence
rows, artifact digest, and build-report binding before any search or resolve.

Use `python -B` or set `PYTHONDONTWRITEBYTECODE=1` when the copied skill directory itself must remain byte-for-byte unchanged. The helper does not write inside the bundle.
"""

NEW_WORKFLOW = """## Bounded reference-answer workflow

For an answer that requires exact evidence JSON, use the snapshot reference
dictionary through this bounded path:

1. Read the required references. Do not list the bundle tree, read helper source,
   reinstall dependencies, open concept files, reconstruct evidence paths, or
   run manual searches. `reference_answer.py prepare` loads and validates the
   snapshot once. Deep validation is a publication audit and is allowed only
   when the user explicitly requests one.
2. Translate the full question into its original wording plus two to four short
   focus queries that cover every named mechanism, contrast, risk, or constraint.
   Never invent target paper IDs.
3. Run one `prepare` command with the task's required independent-source count.
   Write the pack outside the snapshot. The displayed pack contains only compact
   `reference_id` values, source identities, matched-query indices, and text.
4. From the previews, select exactly the required number of relevant independent
   sources. Run one `show` command with all selected indices to read their full
   texts. A second `prepare` is allowed only if source coverage is false or the
   first pack lacks a required question dimension.
5. Draft a temporary JSON object with exactly `question_id`, `summary`, and
   `claims`. Each claim has exactly `statement` and `pack_indices`; ground every
   claim in selected text. Use every selected index and no unselected index.
6. Run `finalize` with the exact required source count. It revalidates the pack's
   dictionary digest and resolves each compact ID to the snapshot-owned seven-field
   evidence object. Return the finalized JSON unchanged, with no surrounding text.

Example for a task requiring five independent sources:

```bash
python -B scripts/reference_answer.py prepare BUNDLE \\
  --query "FULL QUESTION" \\
  --focus "FIRST MECHANISM AND SIGNAL" \\
  --focus "SECOND MECHANISM AND TRADEOFF" \\
  --minimum-sources 5 \\
  --output /tmp/reference-pack.json
python -B scripts/reference_answer.py show /tmp/reference-pack.json \\
  --index 0 --index 2 --index 4 --index 6 --index 8
python -B scripts/reference_answer.py finalize BUNDLE \\
  /tmp/reference-pack.json /tmp/reference-draft.json \\
  --minimum-sources 5 --output /tmp/final-answer.json
```

The runtime is pinned by `scripts/requirements.txt`. Run `runtime_smoke.py` only
after an actual import error. Use `python -B` or set
`PYTHONDONTWRITEBYTECODE=1` when the copied skill directory itself must remain
byte-for-byte unchanged. No helper writes inside the bundle.
"""

OLD_GATE = """- inspection passed, evaluation-critical snapshots passed independent deep rederivation, and the bundle tree remained unchanged;
- filters were applied before ranking;
- requested and effective mode are identical and disclosed;
- every selected hit was resolved by its returned `reference_id` through the
  validated snapshot dictionary;
- expansion terms and activated topics are visible rather than hidden;
- every cited concept path exists and binds to the returned record;
- every locator resolves to the returned text and text hash;
- factual claims were checked in an authoritative layer; and
- no topic label, association edge, retrieval score, web result, or model memory is presented as ground truth."""

NEW_GATE = """- `prepare` passed against an unchanged snapshot and its validated dictionary;
- the pack covers every required question dimension and the exact required count
  of independent sources was selected;
- every claim is grounded only in a selected full text;
- `finalize` passed with the current dictionary digest and produced every evidence
  row by exact `reference_id` resolution rather than transcription;
- every locator resolves to the returned text and text hash; and
- no topic label, association edge, retrieval score, web result, or model memory is presented as ground truth."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-skill", type=Path, required=True)
    parser.add_argument("--helper-source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def proposal(
    *,
    identifier: str,
    diagnosis: str,
    conflict_group: str,
    target: str,
    operation: str,
    content: str,
    old: str | None = None,
) -> dict[str, object]:
    result: dict[str, object] = {
        "id": identifier,
        "diagnosis": diagnosis,
        "domain": "execution-efficiency/context-budget",
        "evidenceIds": list(DISCOVERY_EVIDENCE_IDS),
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
    skill_text = (args.baseline_skill / "SKILL.md").read_text(encoding="utf-8")
    if skill_text.count(OLD_WORKFLOW) != 1:
        raise SystemExit("baseline workflow does not match the frozen proposal target")
    if skill_text.count(OLD_GATE) != 1:
        raise SystemExit("baseline completion gate does not match the proposal target")
    helper = args.helper_source.read_text(encoding="utf-8")
    payload = {
        "proposals": [
            proposal(
                identifier="compact-reference-answer-helper",
                diagnosis=(
                    "Two independent discovery traces used 34 and 32 calls while "
                    "manually inspecting search results and evidence. One trace "
                    "failed exact evidence validity. A compact reference-only pack "
                    "plus deterministic dictionary resolution removes manual identity "
                    "transcription and bounds context use."
                ),
                conflict_group="reference-answer-helper",
                target="scripts/reference_answer.py",
                operation="create",
                content=helper,
            ),
            proposal(
                identifier="bounded-reference-answer-workflow",
                diagnosis=(
                    "The two discovery traces repeatedly validated runtime and source "
                    "state, issued many searches, and opened authoritative pages even "
                    "though the processed snapshot now owns exact compact references. "
                    "The normal answer path should select IDs and defer all identity "
                    "materialization to the dictionary."
                ),
                conflict_group="consultation-workflow",
                target="SKILL.md",
                operation="replace",
                old=OLD_WORKFLOW,
                content=NEW_WORKFLOW,
            ),
            proposal(
                identifier="reference-resolution-completion-gate",
                diagnosis=(
                    "Exact evidence passed in only one of the two discovery cases. "
                    "The completion gate must require current-digest resolution and "
                    "forbid transcribed identity fields while preserving source breadth."
                ),
                conflict_group="completion-gate",
                target="SKILL.md",
                operation="replace",
                old=OLD_GATE,
                content=NEW_GATE,
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
