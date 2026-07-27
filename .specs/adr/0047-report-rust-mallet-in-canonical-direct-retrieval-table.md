---
adr: "0047"
title: "ADR 0047: Report RustMallet in the Canonical Direct-Retrieval Table"
summary: "Include the fully evaluated reference-aware RustMallet routes in the general 40-question direct-retrieval table with measured latency while retaining experimental, non-registry status."
status: "Accepted"
date: "2026-07-23"
product: "knowledge"
owner: "Platform Architecture"
area: "Semantic Knowledge Retrieval"
tags:
  - knowledge
  - okf
  - rust-mallet
  - evaluation
  - latency
  - references
---

# ADR 0047: Report RustMallet in the Canonical Direct-Retrieval Table

## Status

Accepted.

This decision extends ADR 0042 and ADR 0045. It changes comparative reporting,
not the canonical eight-family Harbor registry or RustMallet's promotion state.

## Context

ADR 0042 retained RustMallet as an experimental topic candidate after a complete
40-question retrieval comparison found lower recall than the accepted classical
projection. ADR 0045 then retained compact snapshot-owned references for
consultation while rejecting native builder integration on sealed Harbor
holdout.

The general direct-retrieval table continued to omit RustMallet even though its
quality results were comparable to the other deterministic routes. It also did
not expose a reference-aware latency measurement. This made the candidate harder
to interpret alongside legacy, embedding, entity-graph, classical, adaptive,
and definitive ensemble routes.

## Decision

Report all four reference-aware RustMallet routes in
`evaluations/semantic-okf-ensemble/EVALUATION-CONCLUSIONS.md`. Label every row
experimental and explicitly state that the rows do not add a ninth family to
the Harbor registry.

Use the same frozen 40 questions, canonical paper identity, binary reviewed
qrels, Top-10 metrics, hard-10 cohort, and exact evidence-validity contract as
the existing table. Measure each route through one reused read-only snapshot
after a separately reported independent deep-validation setup. Report mean and
P95 query latency in the candidate summary; retain P95 in the general table.

The 2026-07-23 execution passed all required gates:

- 40 questions and four routes at both Top 10 and pool 100;
- zero query errors and 100% exact evidence validity;
- authoritative-core and raw-input inventory parity;
- 1,135 validated compact references;
- 320 original/reference-aware ranking comparisons with zero mismatches;
- 7,267 returned reference rows checked; and
- 728 distinct compact reference IDs exercised.

The Top-10 run used 12,150.39 ms of shared deep-validation setup and
44,746.75 ms of total evaluator wall time. Route P95 latencies were 226.69 ms
for BM25, 238.70 ms for topic, 224.30 ms for association, and 232.25 ms for
fusion. The separate pool-100 evaluator took 48,463.00 ms.

Keep RustMallet experimental. Its strongest all-40 recall is 80.80% on the
topic route, below classical fusion at 83.46% and adaptive and definitive
ensemble retrieval at 83.82%. Reporting a valid comparator is not a promotion
decision.

## Consequences

Positive:

- the general table now shows RustMallet quality and measured latency using the
  same direct-retrieval contract as the other rows;
- compact-reference transport is represented by fresh end-to-end evidence
  rather than inferred from the pre-reference run;
- the append-only Top-10, pool-100, and parity artifacts are digest-bound by a
  tracked summary; and
- registry cardinality and historical eight-family Harbor comparisons remain
  unchanged.

Negative:

- the general table contains experimental rows in addition to registered
  families, so status labels and the registry boundary must remain explicit;
- P95 values are operational diagnostics because initialization and runtime
  dependencies differ across families; and
- the candidate remains available for comparison despite failing to improve
  the accepted recall floor.
