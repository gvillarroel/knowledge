# ADR 0077: Package retrospective supervised-profile experts

## Status

Accepted on 2026-07-28.

## Context

The strongest recorded GraphRAG direct retriever was the retrospective v48
quality-plus-trace expert. The strongest Astro nDCG route was classical
association. Both left material ranking quality and latency headroom.

Every canonical question and qrel in both datasets has already been exposed.
That makes an all-40 profile useful for a frozen benchmark and fixed FAQ-like
workload, but it also makes a holdout-qualified promotion impossible.

## Decision

Package one separate standalone expert per dataset:

- `graphrag-papers-definitive-expert-v51`; and
- `astro-docs-definitive-expert-v3`.

Use an explicitly retrospective supervised lexical profile as the discovery
projection. Learn one-to-five-token features from all exposed question/qrel
pairs, keep an authoritative lexical fallback, deduplicate canonical
identities before Top 10, and return only exact immutable ledger evidence.
Forbid exact-question lookup and bind the routing index as a hashed direct
query-support child.

Retain the complete selected knowledge snapshots. Verify the manifest,
knowledge tree, guidance, helper, and routing index before every query.

Require a candidate to preserve or improve Recall@10, MRR@10, and nDCG@10,
strictly improve at least one quality metric, strictly reduce P95, and retain
100% exact evidence. Report the result as retrospective and
`promotion_eligible: false`.

## Consequences

- Both fixed datasets now have a separate portable expert with first-place
  in-sample retrieval and much lower P95 than the strongest prior quality
  route.
- The helper output satisfies the existing native Harbor retrieval grader
  without adapter-specific fields or duplicate primary identities.
- The routing projection is optimized for the exposed questions. Its ranking
  cannot establish behavior on unseen requests.
- A future promotion requires newly registered untouched questions and a
  one-way holdout release. These artifacts may be baselines in that study, but
  their present results cannot be relabeled as holdout evidence.
