---
type: Agent Skill
title: Consult Semantic OKF Harbor Adaptive
description: Consult an immutable adaptive Semantic OKF snapshot with its unchanged
  adaptive full-query and per-facet retrieval, then build a bounded deficit-aware
  support union and compile strict source-generic Harbor answers. Use for hard multi-source
  questions that require compact authoritative support, exact hashes and locators,
  deterministic first-use evidence ordering, or lower-context evaluation. This standalone
  skill is read-only and never builds, repairs, or modifies knowledge.
tags:
- codex
- skill
skill_name: consult-semantic-okf-harbor-adaptive
source_path: skills/consult-semantic-okf-harbor-adaptive/SKILL.md
---

# Consult Semantic OKF Harbor Adaptive

Retrieve with the published adaptive algorithm, close explicit facet deficits, and compile the final answer only from a compact hash-bound support pack.

## Standalone read-only boundary

- Use only this directory's instructions, references, scripts, and requirements.
- Treat the bundle as an explicit external input mounted read-only.
- Do not import a sibling skill, repository helper, evaluator, fixture, or answer key.
- Never write a cache, draft, answer, lock, repair, or derived artifact into the bundle.
- Treat adaptive ranks, topics, aspects, and expansions as discovery signals, not domain evidence.
- Stop on a stale hash, schema violation, symlink, unsafe path, invalid locator, unknown support, parameter mismatch, tampered support, or failing build report.

## Required references

- Read [adaptive-format.md](../../skills/consult-semantic-okf-harbor-adaptive/references/adaptive-format.md) when inspecting snapshot integrity.
- Read [querying.md](../../skills/consult-semantic-okf-harbor-adaptive/references/querying.md) before preparing or selecting supports.

## Harbor answer workflow

1. Run ordinary inspection. Add `--deep-validation` once for a new, evaluation-critical, or release-candidate snapshot.
2. Turn the question into atomic answer facets: named subjects, requested mechanisms, conditions, contrasts, exclusions, and important negatives.
3. Run `harbor_answer.py prepare`. It runs the original `adaptive` route for the full question and every bounded lexical facet, protects the leading full-query evidence, fills uncovered facets, deduplicates exact source-record identities, projects hits to authoritative parent records, and emits only bounded snippets plus exact hashes.
4. Inspect every selected snippet. Use its `support_id` only when the authoritative excerpt directly supports an atomic statement. Qualify unsupported facets; do not fill gaps from memory.
5. Create an external draft with exactly `question_id`, `parameters_sha256`, `summary`, and `claims`. Each claim must contain exactly `statement` and `support_ids`.
6. Run `harbor_answer.py finalize`. Return its JSON unchanged. The finalizer independently reruns retrieval, rejects stale or altered packs, resolves support IDs to authoritative records, deduplicates exact identities, and emits evidence in deterministic first-use order with no unused row.
7. If finalization fails, fix the external draft or regenerate the pack. Never edit the bundle or manually reconstruct identities.

```bash
python scripts/runtime_smoke.py
python scripts/query_semantic_okf_adaptive.py /knowledge inspect --deep-validation
python scripts/harbor_answer.py /knowledge prepare \
  --question-id q031 \
  --question "A hard multi-part question" > /tmp/support-pack.json
python scripts/harbor_answer.py /knowledge finalize \
  --pack /tmp/support-pack.json \
  --draft /tmp/answer-draft.json
```

Use `/tmp` or another path outside the snapshot for ephemeral files. Use `--draft -` to read the draft from standard input. The scripts never write to the bundle.

## Draft contract

```json
{
  "question_id": "q031",
  "parameters_sha256": "copy from the support pack",
  "summary": "A concise synthesis grounded only in selected supports.",
  "claims": [
    {
      "statement": "One atomic statement.",
      "support_ids": ["support-copy-exactly"]
    }
  ]
}
```

Keep claims atomic. Use two supports only for a real join or contrast. Preserve explicit negatives. It is valid to leave a candidate support unused; it is not valid to cite an unknown support or manually add an evidence row. The compiler includes only selected supports and proves every emitted evidence row is used.

## Diagnostic retrieval

Use the copied original CLI only to diagnose ranking behavior:

```bash
python scripts/query_semantic_okf_adaptive.py /knowledge search \
  --query "exact identifier or mechanism" --mode adaptive --top-k 10
```

Do not stream its unbounded full-record result into the answer context when the compact Harbor pack suffices. The original `_adaptive_snapshot.py` and `query_semantic_okf_adaptive.py` behavior is retained unchanged in this package.

## Completion gate

Before returning an answer, confirm that inspection passed; the snapshot remained unchanged; full-query and per-facet retrieval used `adaptive`; every factual statement maps to a directly supporting selected snippet; the pack and draft parameter hashes agree; finalization succeeded; top-level and nested keys are exact; evidence hashes and paths came from authoritative parent records; evidence is in first-use order; every emitted evidence row is referenced; unsupported facets are qualified; and no retrieval score, web result, or model memory is presented as ground truth.
