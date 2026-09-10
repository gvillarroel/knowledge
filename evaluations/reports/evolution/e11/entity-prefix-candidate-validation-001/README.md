# Entity Graph candidate: exact mention matching with fewer irrelevant lookups

The complete `entity-prefix-matching-001` candidate passed all seven declared
software validation commands and the maintained realizer's final verification.
Its [source-bound aggregate](aggregate.json) records the actual checks. The
6,000-document native EnterpriseRAG measurement remains pending; this report
establishes no new retrieval score or full-workload speedup.

The correction changes one function in one standalone Entity Graph builder
file. It groups possible alias lengths by their first normalized token, avoiding
tuple lookups for aliases that cannot begin at a section position. Complete
matching, duplicate and overlapping occurrence counts, result ordering, all
consultants and the other 251 package files remain unchanged. Ensemble's
separate internal matcher is also unchanged.

## Completed correctness evidence

All **1,120 ordered parent/candidate comparisons** matched across generic and
scientific schemas, four minimum token lengths and 140 deterministic cases per
stratum. Of these comparisons, 1,066 produced nonempty results. A separate
count oracle checks duplicate and overlapping aliases independently of the
parent implementation.

| Schema | Storage layout | Identical artifact files | Complete builds | Independent validations | Exact nonempty query pairs |
| --- | --- | ---: | ---: | ---: | ---: |
| Generic | Record per file | 21 | 4 | 4 | 8 |
| Generic | Source packed | 21 | 4 | 4 | 8 |
| Scientific | Record per file | 105 | 4 | 4 | 8 |
| Scientific | Source packed | 20 | 4 | 4 | 8 |

These four integration cells executed 152 Python commands: 16 complete builds,
16 independent validations, 32 paired queries across all four routes, eight
deep validations by the unchanged consultation implementation, 40 corruption
rejections and eight refusals to overwrite existing output. Package inventories
and fixture inputs remained unchanged. Detailed command arguments and outputs
are preserved in ignored local evidence.

The fixture contains four neutral generic records and one existing public
scientific source with its semantic and claim records. It contains no benchmark
questions, relevance labels or private evaluation inputs. An earlier validator
mistakenly expected a `valid` field in the CLI's overwrite error. Its failed
self-checks were preserved, and the corrected response-shape assertion passed
before the candidate was realized.

## Construction hypothesis and accounting

The instrumented neutral stress fixture returned exactly 32 mentions in both
versions. It counted **4,001,920 tuple constructions for the parent and 160 for
the candidate**. This verifies elimination of irrelevant lookups in that fixture;
it is not a measured native duration, memory reduction or retrieval gain.

The [original timeout](../entity-graph-timeout-001/README.md) and
[matching diagnosis](../entity-graph-matching-diagnosis-001/README.md) remain
unchanged. The new construction proposal consumes one existing Entity Graph
claim, leaving 79 in that family's cap. At this checkpoint, 81 historical
claims plus the Ensemble and Entity Graph proposals total **83**, within the
unchanged global cap of 585. All inherited search state and stopping rules
remain intact.

| Resource or outcome | Observed value |
| --- | --- |
| New construction proposal claims | 1 |
| Native Harbor trials | 0 |
| Benchmark questions evaluated | 0 |
| Model calls | 0 |
| Host compute cost | Unavailable |
| Full-workload peak memory and duration | Unmeasured |
| EnterpriseRAG nDCG@10 | Unmeasured |
| Private validation releases | 0 |
| Canonical skill installation | None |

The candidate tree is
`sha256:886840868c7e47d2d7f35d5ecdf677100dfffc49d8750f8a890c273efc0c1f9d`;
the parent tree is
`sha256:b352ebab48148260e16ab43fd6ad0781e38ad39b1f11ff8be833a4ed7e61b8f8`.
The reservation binds one exclusive prospective first-measurement identity but
assigns no native allocation. Full-corpus qualification and the remaining
all-family, final-comparison and independent-acceptance gates are still required.

[Decision record](../../../../../.specs/adr/0138-index-exact-entity-mentions-by-first-token.md) ·
[E11 overview](../README.md) ·
[Results by family](../../../../../docs/enterprise-family-report-index.md) ·
[Evolution index](../../README.md)
