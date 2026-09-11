# Entity Graph: reuse snapshot evidence indexes

The isolated candidate passed all **nine software checks** and returned all
**48 retained public runtime responses exactly**. Its observed profiled query
time was **6.579 seconds**, compared with the retained
parent's **7.785 seconds**. One evidence index and one
traversal index served the full route-major query sequence. This software
observation does not establish a native EnterpriseRAG speedup or quality gain.
The candidate's first native measurement remains **unassigned**.

## Retained EnterpriseRAG comparison

| Family | Retained nDCG@10 x100 | Proposals / cap | Search state |
| --- | ---: | ---: | --- |
| legacy | 72.38 | 16 / 55 | Recorded catalog stop |
| turso | 72.08 | 2 / 55 | Open |
| adaptive | 66.21 | 20 / 100 | Open |
| embeddings | 63.51 | 6 / 40 | Recorded catalog stop |
| classical | 62.10 | 37 / 85 | Recorded catalog stop |
| graphify | 8.12 | 0 / 65 | Open |
| ensemble | Unavailable | 2 / 105 | Open |
| entity-graph | Unavailable | 8 / 80 | Open |

These six scores retain the exact [previous native comparison](../entity-traversal-adjacency-reuse-native-001/README.md):
120 stratified questions, 112 retrieval-eligible questions and 6,000 complete
documents, with frozen-category-weighted nDCG@10 multiplied by 100. They measure
internal retrieval quality. The final all-500 comparison, generated-answer
Overall, public ranking and independent whole-bundle acceptance remain unfinished.
No score is assigned to Entity Graph or Ensemble from a software fixture.

## Exact treatment

Only the Entity consultant's `_entity_graph_snapshot.py` changes. It reuses
source-derived record, section, claim-evidence and edge-evidence lookups for
one immutable snapshot. The existing reentrant query lock guards a single
weak-owner entry bound to snapshot identity, root, index, core and plan digests.
Replacement drops the old entry before allocation; owner collection releases it.
The builder and the other 251 package files remain byte-identical.

The mutation preserves scoring arithmetic, tokenization, traversal, route order,
filters, rank and evidence ordering, duplicates, validation and public errors.
It does not enlarge the preceding-query cache or reuse validation. Returned
claim evidence remains isolated from the internal cache.

Candidate: `sha256:c4d3c66cb4567ac4bbb6236e183c17bccaad9f4cccac77f67a382cfdbc735faf`.
Parent: `sha256:37015e173891f7a267b9cd8ffd88567a8f8200dccdea7827180df4e375770f66`.
The complete diff, validation and original tool outcomes are bound in the
[aggregate](aggregate.json). [ADR 0149](../../../../../.specs/adr/0149-reuse-entity-snapshot-evidence-indexes.md)
records the implementation decision.

## Software and runtime evidence

- Exact recipe and single-file scope, plus skill-format validation.
- 96 lookup comparisons, binding invalidation, duplicate/order checks, weak
  ownership and failed-replacement cleanup.
- 192 concurrent comparisons across four snapshots.
- Four complete schema/layout cells with repeat builds, independent validation,
  complete artifact and query parity, corruption rejection and overwrite checks.
- 96 additional warm response pairs across all four routes and source filters,
  plus 16 matched public rejection pairs and returned-evidence mutation checks.
- One pinned, network-free consultation-only replay on 1,024 synthetic records,
  2,048 entities and 76,419 edges. All 48 reference responses matched, with zero
  complete-query cache hits and one construction of each reusable index.

The parent runtime was not re-executed. Sequential profiled times include
instrumentation overhead and do not establish a causal speedup or native peak
memory. The synthetic fixture does not identify the previous native timeout
function. See [CTA](cta.md) for timing and resource scope.

## Opportunity accounting and next gate

This nonrefundable proposal increases the total to **91 of 585**, including
**8 of Entity Graph's 80**. All nine earlier construction first measurements
remain consumed. This candidate has one unassigned first-measurement identity,
zero dispatched native attempts and zero evaluable quality misses.

Five searches remain open with 373 family-bound maximum opportunities. The
recorded Legacy, Classical and Embeddings stops, nontransferable unused capacity,
Adaptive `b=0.25` and Turso `k1=0.6` pending measurements, and permanently unavailable
originals stay unchanged. Execution failures are not quality zeroes or misses.

Exact native qualification under the unchanged full workload and resource limits
is required next. Current admission, common-reference reproduction, remaining
family searches, joint replay, the paired all-500 comparison and sealed whole-bundle
acceptance are still required. No canonical skill has been promoted.

[E11 overview](../README.md) · [Family index](../../../../../docs/enterprise-family-report-index.md)
