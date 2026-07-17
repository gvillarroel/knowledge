---
type: Agent Skill
title: Consult Semantic OKF Harbor Entity Graph
description: Consult a published Semantic OKF entity-section graph with bounded full-question
  and focused-facet fusion, compact authoritative parent-record excerpts, and a strict
  recomputed JSON finalizer. Use for read-only, evidence-grounded multi-document questions—especially
  Harbor evaluations—where exact source-record identities, locators, and hashes must
  be preserved without exposing graph edges as factual support.
tags:
- codex
- skill
skill_name: consult-semantic-okf-harbor-entity-graph
source_path: skills/consult-semantic-okf-harbor-entity-graph/SKILL.md
---

# Consult Semantic OKF Harbor Entity Graph

Use the unchanged graph fusion ranker for discovery, then close the answer through the packaged
parent-record compiler. Never hand-author evidence metadata.

## Standalone and read-only boundary

- Use only this package and the supplied bundle.
- Treat `semantic/` and `concepts/` as authoritative and `entity-graph/` as derived discovery data.
- Do not import sibling skills, evaluator code, fixtures, expected answers, or web evidence.
- Never build, repair, cache, or write inside the bundle.
- Treat graph entities, mention edges, co-mentions, traversal paths, and scores only as discovery.
- Stop on a validation, identity, locator, hash, parameter, or finalization failure.

## Required workflow

1. Preserve the exact question ID and question text.
2. Run `harbor_answer.py prepare` once with the final parameters.
3. Review the bounded excerpts by facet. Open a listed authoritative concept only when more context
   is needed; do not run broad filesystem scans.
4. Copy `draft_template`. Replace the summary, add atomic claims, and list only emitted `support_id`
   values in `evidence`, in first-use order.
5. Point every claim to one or more zero-based draft evidence indices. Use every listed support.
6. Run `harbor_answer.py finalize` with the identical question and parameters.
7. Return the finalizer JSON verbatim with no prose wrapper or reserialization.

The compiler uses only graph `fusion` searches. It keeps the unchanged full question, derives at
most eight bounded clauses, round-robins their section rankings, and deduplicates exact
`(source_id, record_id)` parents. It validates every selected section against `record.body`, emits a
short hash-bound excerpt, and projects public evidence to the authoritative full record. Graph edge
IDs are never support IDs and never appear in the public answer.

## Prepare support

```bash
python -B scripts/harbor_answer.py /knowledge prepare \
  --question-id QUESTION_ID \
  --question "EXACT QUESTION" > /tmp/support-pack.json
```

Read [harbor-answer-contract.md](../../skills/consult-semantic-okf-harbor-entity-graph/references/harbor-answer-contract.md) before drafting. Read
[querying.md](../../skills/consult-semantic-okf-harbor-entity-graph/references/querying.md) only when diagnosing graph ranking or opening additional
authoritative context. Read [entity-graph-format.md](../../skills/consult-semantic-okf-harbor-entity-graph/references/entity-graph-format.md) when
checking the discovery projection's authority boundary.

## Finalize the answer

Use this exact draft shape:

```json
{
  "question_id": "q000",
  "question_sha256": "COPY_FROM_PACK",
  "parameters": {"COPY": "FROM_PACK"},
  "support_pack_sha256": "COPY_FROM_PACK",
  "answer": {
    "summary": "A bounded synthesis.",
    "claims": [
      {"statement": "One atomic claim.", "evidence_indices": [0]}
    ]
  },
  "evidence": ["support-..."]
}
```

```bash
python -B scripts/harbor_answer.py /knowledge finalize \
  --question-id QUESTION_ID \
  --question "EXACT QUESTION" \
  --draft /tmp/answer-draft.json
```

Repeat `--facet-limit`, `--per-facet`, `--max-supports`, and `--excerpt-chars` identically when
overriding defaults. The finalizer recomputes retrieval and rejects duplicate JSON members, changed
parameters, changed questions, stale packs, unknown or tampered supports, duplicate supports,
out-of-range indices, unused evidence, and evidence not ordered by first use.

## Existing graph CLI

The copied graph query scripts remain byte-identical to `consult-semantic-okf-entity-graph`. Use
`query_semantic_okf_entity_graph.py` for read-only inspection or exploratory `lexical`, `entity`,
`traversal`, and `fusion` searches, then still emit any contracted answer through
`harbor_answer.py finalize`.

## Completion gate

- Confirm the bundle tree remained unchanged.
- Confirm every claim is directly supported by the selected authoritative parent excerpt.
- Preserve conditions, exclusions, and important negatives when evidence establishes them.
- Never cite a section ID, entity ID, graph edge, score, or model memory as factual evidence.
- Return only the successful finalizer object. If authoritative support is insufficient, return the
  task's exact null-answer contract instead of guessing.
