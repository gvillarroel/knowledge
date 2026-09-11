# Entity Graph traversal adjacency reuse

The isolated consultant candidate passed **eight software checks** and a
**48-query pinned-runtime replay with exact reference responses**. It builds
the snapshot's adjacency index once and reuses it across all four routes.
Its original native EnterpriseRAG measurement is **unassigned**; no retrieval
score or quality gain is attributed to this candidate.

## Exact change and evidence

Only `assets/families/entity-graph/consultant/scripts/_entity_graph_snapshot.py`
changes. The builder and all 251 other package files remain identical to the
parent. A one-entry cache uses the existing lock, weak snapshot identity and
root/index/core/plan digests. It releases the old graph before replacement and
clears its references when the snapshot dies. The original edge order, parallel
edges, both self-loop insertions, traversal arithmetic, evidence, routes and
query-cache behavior are preserved. Deep validation remains unchanged.

The sealed candidate is `sha256:37015e173891f7a267b9cd8ffd88567a8f8200dccdea7827180df4e375770f66` and its parent is
`sha256:cdbcc0e33b9ba6235f0ae6d7505826c0ed71768e1497c468bf63a9b0810ed591`. The [aggregate](aggregate.json) binds
the complete package manifest, original seal/verification observations,
checks, pinned runtime and retained reference responses.

The software checks include 192 exact traversal comparisons over 24 seeded
public topologies in both schema versions, with 144 nonempty results;
hand-counted propagation and edge-order checks; snapshot binding, weak lifetime
and failed-replacement release checks; and 96 concurrent comparisons across
four snapshot identities sharing the same path and digest fields. Four complete
schema/layout cells executed 192 child commands for exact construction,
independent validation, query parity, corrupt-input rejection and overwrite
rejection. These are software checks, not independent EnterpriseRAG cases.

## Pinned-runtime replay

The retained public synthetic snapshot contains 1,024 records, 1,024 sections,
2,048 entities and 76,419 edges. The same 12 synthetic queries ran in the same
route-major order across lexical, entity, traversal and fusion. All 48 responses
matched the retained parent exactly. The 10 consultant files, 19 snapshot files
and all reference-response files stayed unchanged.

Observed profiled query time decreased from **15.727 seconds**
to **7.785 seconds** (2.02x ratio). The candidate
built adjacency **once** while still performing 48 query computations with zero
full-query-cache hits. One deep load preceded the queries. The parent profile
was preserved and was not rerun. These are two sequential public software
observations with cProfile overhead, not a replicated native speedup, an
estimate for the 6,000-document task, or a peak-memory result. The previous
native timeout phase remains unidentified. See [CTA](cta.md).

## Retained EnterpriseRAG comparison

This table preserves the six qualified development scores from the
[previous native checkpoint](../entity-consultant-ngram-eligibility-native-001/README.md).
Scope: 120 stratified questions, 112 retrieval-eligible questions and 6,000
complete documents; frozen-category-weighted nDCG@10 multiplied by 100.
The synthetic runtime above supplies no new row in this retrieval ranking.

| Family | Retained nDCG@10 x100 | Search | Proposals / cap |
| --- | ---: | --- | ---: |
| Legacy | 72.38 | Closed | 16 / 55 |
| Turso | 72.08 | Open | 2 / 55 |
| Adaptive | 66.21 | Open | 20 / 100 |
| Embeddings | 63.51 | Closed | 6 / 40 |
| Classical | 62.10 | Closed | 37 / 85 |
| Graphify | 8.12 | Open | 0 / 65 |
| Ensemble | Unavailable | Open | 2 / 105 |
| Entity Graph | Unavailable | Open | 7 / 80 |

See [application/category availability](groups.md) and the
[family report index](../../../../../docs/enterprise-family-report-index.md).
These are retrieval measurements, not generated-answer quality, official
Overall, public leaderboard ranks or the final all-500 comparison.

## Opportunity accounting and remaining work

One nonrefundable proposal brings accounting to **90 of 585**, including
**7 of Entity's 80** and 2 of Ensemble's 105. All eight prior construction first
measurements remain consumed. The new
`entity-traversal-adjacency-reuse-001-first-measurement` is unassigned, with
cardinality one and zero retries. Software checks and this runtime replay add
no native trial or evaluable quality miss.

Five family searches remain open, with 374 family-bound claims available. Closed
unused allowances are not transferable. The five-round limit and three
consecutive unique evaluable misses per mechanism remain fixed. Preserve the
pending Adaptive/Turso measurements and unavailable originals.

The next step is exact native construction qualification under the unchanged
resource/task contract. The common reference, five open catalogs, joint replay,
exact bundle freeze, paired all-500 comparison and independent whole-bundle
acceptance remain unfinished. No private gate was released and no canonical
skill was promoted.

[E11 overview](../README.md) · [Aggregate](aggregate.json)
