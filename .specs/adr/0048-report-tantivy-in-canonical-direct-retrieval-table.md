---
adr: "0048"
title: "ADR 0048: Report Tantivy in the Canonical Direct-Retrieval Table"
summary: "Include the fully evaluated native Tantivy BM25 route in the general 40-question direct-retrieval table while retaining experimental, non-registry status."
status: "Accepted"
date: "2026-07-23"
product: "knowledge"
owner: "Platform Architecture"
area: "Semantic Knowledge Retrieval"
tags:
  - knowledge
  - okf
  - tantivy
  - bm25
  - evaluation
  - latency
---

# ADR 0048: Report Tantivy in the Canonical Direct-Retrieval Table

## Status

Accepted.

This decision extends ADR 0043, ADR 0046, and ADR 0047. It changes comparative
reporting, not the canonical eight-family Harbor registry or Tantivy's
promotion state.

## Context

ADR 0043 introduced `consult-semantic-okf-tantivy` as a standalone read-only
candidate over validated Classical snapshots. ADR 0046 retained that checked-in
candidate unchanged after a later answer-construction variant failed its sealed
Harbor promotion holdout.

The candidate still lacked the complete direct-retrieval measurement required
for the general table. The prior tests established native execution, snapshot
validation, exact evidence transport, and small fixtures, but not quality,
determinism, or latency over the same 40 questions used by the accepted and
experimental comparator routes.

## Decision

Report `tantivy_bm25` in
`evaluations/semantic-okf-ensemble/EVALUATION-CONCLUSIONS.md` as an experimental
route over the validated Classical snapshot.

Use the same frozen 40 questions, canonical paper identity, binary reviewed
qrels, direct Top-10 metrics, hard-10 cohort, and exact schema 1.2 evidence
contract as the existing table. Adapt natural-language questions to safe
alphanumeric Tantivy whitespace terms without qrel-aware expansion. This is a
generic parser boundary, not a question-specific retrieval intervention.

The 2026-07-23 evaluation passed all execution gates:

- 40 Top-10 questions, 40 exact-replay questions, and 40 pool-100 questions;
- zero route errors;
- 400/400 valid Top-10 evidence rows and 4,000/4,000 valid pool-100 rows;
- byte-equivalent ranked Top-10 outputs across the complete replay; and
- identical ranked Top-10 prefixes in the pool-100 run.

The direct Top-10 row measured 34.64% all-40 Recall@10, 86.25% MRR@10,
44.81% nDCG@10, 45.17% hard-10 Recall@10, 76.67% hard-10 MRR@10, and
48.91% hard-10 nDCG@10. P95 query latency was 108.26 ms after a separately
reported 1,452.44 ms closed-snapshot validation.

Retain Classical BM25 as the accepted route. Tantivy regressed Classical by
15.08 percentage points on all-40 Recall@10 and 18.00 points on hard-10
Recall@10. Pool-100 raised recall over the first ten distinct paper identities
to 77.29%, showing that repeated passages from the same paper are the main
Top-10 coverage cost, but that different candidate budget is not substituted
into the canonical direct row.

Keep Tantivy experimental. Reporting a complete comparator does not register a
ninth Harbor family or override the rejected trace-distillation promotion.

## Consequences

Positive:

- the general table now answers how native Tantivy compares under the same
  direct-retrieval contract;
- exact replay and pool-prefix checks establish deterministic ranking;
- the measured row preserves exact evidence identities and reports operational
  latency; and
- the larger-pool diagnostic isolates paper-level duplication without changing
  the canonical Top-10 result.

Negative:

- the general table includes another experimental route, so its status and the
  registry boundary must remain explicit;
- default Tantivy analysis and passage-level scoring produce materially lower
  paper coverage than Classical BM25 on this corpus; and
- P95 latency remains an operational diagnostic because setup and runtime
  boundaries differ across families.
