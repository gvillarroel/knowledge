---
name: consult-semantic-okf-harbor-ensemble
description: Consult a published definitive Semantic OKF ensemble with unchanged quality or fast retrieval, a bounded full-question plus focused-facet candidate union, compact authoritative parent-record excerpts, and a strict recomputed JSON finalizer. Use for read-only, evidence-grounded multi-document synthesis—especially Harbor evaluations—where exact source-record identities, locators, hashes, exclusions, and response-contract compliance matter.
---

# Consult Semantic OKF Harbor Ensemble

Use the ensemble's unchanged retrieval policies for discovery, then close the answer through the
packaged parent-record compiler. Never hand-author evidence metadata.

## Standalone and read-only boundary

- Use only this package, the supplied bundle, and the explicitly governed offline model cache.
- Treat `semantic/`, `concepts/`, and accepted RDF as authoritative. Treat `adaptive/`,
  `entity-graph/`, `retrieval/`, and `ensemble/` as derived discovery projections.
- Do not import sibling skills, evaluator code, fixtures, expected answers, web evidence, or MCP.
- Never build, repair, cache, or write inside the bundle.
- Stop on any snapshot, component-parity, identity, locator, hash, provider, parameter, or
  finalization failure.

## Required workflow

1. Preserve the exact question ID and question text.
2. Run `harbor_answer.py prepare` once with the final parameters. Use `quality` when the pinned
   offline embedding runtime is available; choose `fast` explicitly when its latency/provider
   tradeoff is required.
3. Review the bounded excerpts for the full question and each focused facet. Open listed
   authoritative concepts only when more context is necessary.
4. Copy `draft_template`. Replace the summary, add atomic claims, and list only emitted `support_id`
   values in `evidence`, in first-use order.
5. Point every claim to one or more zero-based draft evidence indices. Use every listed support.
6. Run `harbor_answer.py finalize` with the identical question, policy, and numeric parameters.
7. Return the finalizer JSON verbatim with no prose wrapper or reserialization.

The compiler preserves each underlying search policy. It searches the unchanged full question and
at most seven bounded clauses, then forms a capped round-robin union across those independently
ranked sets. This deliberately allows a focused facet to add an exact source-record candidate that
the full-query protected set omitted. Every hit is checked against its exact crosswalk identity and
authoritative `record.body`, deduplicated by `(source_id, record_id)`, and projected to a full-record
public locator.

## Prepare support

```bash
python -B scripts/harbor_answer.py /knowledge prepare \
  --question-id QUESTION_ID \
  --question "EXACT QUESTION" \
  --policy quality > /tmp/support-pack.json
```

Read [harbor-answer-contract.md](references/harbor-answer-contract.md) before drafting. Read
[querying.md](references/querying.md) when interpreting policy availability or lower-level output.
Read [adaptive-format.md](references/adaptive-format.md),
[entity-graph-format.md](references/entity-graph-format.md), or
[retrieval-format.md](references/retrieval-format.md) only when diagnosing that projection.

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
  --policy quality \
  --draft /tmp/answer-draft.json
```

Repeat `--facet-limit`, `--per-facet`, `--max-supports`, and `--excerpt-chars` identically when
overriding defaults. The finalizer recomputes the same candidate union and rejects duplicate JSON
members, changed parameters, changed questions, stale packs, unknown or tampered supports, duplicate
supports, out-of-range indices, unused evidence, and evidence not ordered by first use.

## Existing ensemble CLI

The copied ensemble scripts remain byte-identical to `consult-semantic-okf-ensemble`. Use
`query_semantic_okf_ensemble.py` for read-only inspection, direct `quality` or `fast` search, or
legacy reviewed-claim operations, then still emit a source-generic contracted answer through
`harbor_answer.py finalize`.

## Completion gate

- Confirm the bundle tree remained unchanged and the declared policy completed without fallback.
- Confirm every claim is directly supported by the selected authoritative parent excerpt.
- Preserve requested conditions, exclusions, joins, contrasts, and important negatives.
- Never cite a group ID, graph edge, candidate phrase, route score, or model memory as factual
  evidence.
- Return only the successful finalizer object. If authoritative support is insufficient, return the
  task's exact null-answer contract instead of guessing.
