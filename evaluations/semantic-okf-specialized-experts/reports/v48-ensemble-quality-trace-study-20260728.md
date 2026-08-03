# V48 Ensemble Quality and Trace Specialized Expert Study

Date: 2026-07-28

## Evaluation boundary

This study packages the exact validated `Ensemble quality` knowledge snapshot as
a standalone expert and asks whether a bounded, trace-derived lexical signal can
improve its deterministic paper ranking. The snapshot contains 904 files and
874 authoritative semantic records. Its tree SHA-256 is
`2d611b958fdde78ad5563fb7d3f88705d850f25b697445194a418d226e452df0`.

All forty GraphRAG retrieval questions and their qrels had prior exposure.
Parameter selection is therefore retrospective and uses only q001-q024 as a
declared development prefix. The final all-40 result supports a comparable
experimental rank, not holdout-qualified promotion or a grounded answer-quality
claim.

The prior trace-derived fielded-BM25 helper supplies the complementary lexical
ranking. This study performs a closed deterministic operator search over frozen
rankings; it does not claim a new Harbor trial or an untouched Harbor gate.

## Exact Ensemble quality reproduction

`build-specialized-skill` was extended to bind a complete multi-file query
adapter. The pure reproduction packages the Ensemble adaptive, entity-graph,
BM25, and pinned offline embedding routes without changing their quality policy
or internal Top-10 budget.

The resulting `graphrag-ensemble-quality-expert-v46` reproduces the canonical
quality metrics exactly:

| Candidate | Recall@10 | MRR@10 | nDCG@10 | Hard Recall@10 | Hard nDCG@10 |
|---|---:|---:|---:|---:|---:|
| Ensemble `quality` baseline | 83.82% | 100.00% | 85.20% | 95.50% | 88.27% |
| Standalone quality expert v46 | 83.82% | 100.00% | 85.20% | 95.50% | 88.27% |

All 400 returned evidence rows validate. The expert uses the immutable
`sentence-transformers/all-MiniLM-L6-v2` revision
`1110a243fdf4706b3f48f1d95db1a4f5529b4d41` from an offline cache and fails
closed rather than substituting a model.

## Development search and protocol correction

The closed search evaluates 1,800 global operators across two candidate scopes,
nine RRF constants, ten quality weights, and ten trace weights. Every operator
uses the same frozen quality ranking, fielded-BM25 ranking, qrels, metric code,
and stable tie break.

The first selection receipt credited a quality candidate when the same paper
appeared below rank ten in the trace list. The executable adapter correctly
restricted trace contributions to its declared Top-10 candidate budget, so that
receipt and the resulting v47 package are excluded from final selection. A
regression test now proves that rank eleven cannot affect either the protected
set or the union.

Schema `semantic-okf-ensemble-quality-trace-selection/1.1` repeats the search
with the exact executable boundary. Its selected global operator is:

- union of quality Top-10 and trace Top-10;
- quality weight 9;
- trace weight 5;
- RRF constant 0; and
- fused score, quality rank, trace rank, and paper ID tie ordering.

The corrected receipt seal is
`sha256:025a8af788b8b21166fff53701b9c47e78fdfa4ec283643a28248cdae23c5404`.
The selected ranking SHA-256 is
`d8540e8ea185cf1fecbc7b02a0f54979daf53043672de33e72c5895192f8c828`.

| Development q001-q024 | Recall@10 | MRR@10 | nDCG@10 |
|---|---:|---:|---:|
| Pure quality expert | 79.96% | 100.00% | 83.65% |
| Selected 9:5 fusion | 82.11% | 100.00% | 85.19% |
| Change | +2.15 pp | 0.00 pp | +1.54 pp |

The materialized v48 execution reproduces all three selected development
metrics exactly.

## Materialized v48

The selected adapter is packaged as
`graphrag-ensemble-quality-trace-expert-v48`. Its retrieval contract is
`ensemble-quality-trace-union-rrf-v3`.

- query helper SHA-256:
  `017ba7b22d1becc89d9fda52d9462b0e18c7b89a11fe29256acc358e44219221`;
- expert manifest SHA-256:
  `aed263cc284c03c7b329b75a895e8fa2d05383cc2109986b75a9753016665ae3`;
- guidance SHA-256:
  `5535b14ad9f5879acfc767b46be585e6efc0b34296348fd0082f6480a4bd2c0c`;
- evaluation tree SHA-256:
  `c4bc9dca324e34d9f7c4857f0608500309374ed3e7ce65160c4bf7aec382de54`;
  and
- unchanged embedded knowledge tree SHA-256:
  `2d611b958fdde78ad5563fb7d3f88705d850f25b697445194a418d226e452df0`.

The package validator, general skill validator, byte-identical reproduction
check, manifest verification, offline runtime check, and exact evidence checks
all pass.

## All-40 evaluation and rank

The frozen package was evaluated independently at Top 10 and pool 100. The
adapter intentionally emits no more than ten paper identities, so every Top-10
ranking, hit, score, and evidence object is an exact prefix of the pool-100
request. All 400 evidence rows validate, all forty queries succeed, and both
runs bind identical expert, knowledge, builder, packager, question, and
selection inputs.

| Candidate | Recall@10 | MRR@10 | nDCG@10 | Hard Recall@10 | Hard nDCG@10 | P95 | Position |
|---|---:|---:|---:|---:|---:|---:|---:|
| Ensemble `quality` | 83.82% | 100.00% | 85.20% | 95.50% | 88.27% | 1461.92 ms | 1 of 24 |
| Specialized expert v48 | 85.39% | 100.00% | 86.02% | 95.50% | 86.56% | 2012.48 ms | 1 of 24 |
| Change | +1.57 pp | 0.00 pp | +0.82 pp | 0.00 pp | -1.71 pp | +550.56 ms | unchanged |

The checked
[improvement audit](ensemble-quality-trace-improved-retrieval-20260728.md)
replaces the evolved `quality` predecessor rather than counting both versions.
V48 is position **1 of 24** under the table's nDCG-first ordering. It also
matches the v45 expert's Recall@10 to displayed precision while improving
nDCG@10 by 2.27 percentage points.

The trade-off is explicit: v48 improves all-40 ordering and coverage but is
slower, and its hard-10 nDCG is lower than pure quality. The pure quality route
therefore remains the stronger hard-cohort choice, while v48 is the strongest
observed all-40 deterministic ranker.

## Promotion boundary

V48 remains an experimental specialized expert. A formal promotion requires a
newly registered cohort that was not inspected during policy construction,
selection, or reporting, followed by a frozen Harbor holdout gate. Grounded
answer behavior also requires a separate answer-generation and semantic-review
study; direct retrieval metrics do not establish answer correctness or
completeness.
