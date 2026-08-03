# Latest Evaluation Report

Cutoff: 2026-07-30.

Newest scored evidence: 2026-07-30.

## Executive result

This report presents three separate comparisons. The newest study evaluates
all twenty-five compatible retrieval strategies on forty new cross-source
contradiction audits over the existing fifteen-paper corpus. The established
sixty-question direct-retrieval table follows it, then the revised 2026-07-24
GraphRAG grounded-answer table. The contradiction and generalization studies
use one shared Top-10 paper-identity contract and repeated process
measurements. The grounded-answer report uses dataset schema `1.2`,
diagnostics schema `3.0`, the current grader, each trial's native ledger and
source-combination crosswalk, and the independently reviewed reference-answer
collection.

The revised evaluation does not establish a winner across the eight registered
Semantic OKF families. It rescored 516 trial artifacts, but provider failures
and uneven response coverage leave eleven of forty questions without an
empirical response. Of 175 semantically reviewed responses, 3 passed, 168 were
partial, and 4 failed. The family and candidate tables below are therefore
coverage and outcome diagnostics, not leaderboards.

The evaluation-only comparison reverses the exposed-benchmark result.
Classical association ranks first at 99.60% nDCG@10. The retrospective v51
supervised profile falls to 41.03% nDCG@10 and reproduces only 43.33% of
query rankings across three executions. Retrieval values remain supplemental
to grounded-answer evaluation and are not substituted into its table.

On contradiction search, the v45 early confidence-gated specialized expert
ranks first by the primary Full evidence@10 metric at 92.50%. RustMallet
association follows at 90.00%, and classical association is third at 87.50%.
The v51 supervised-profile expert reaches only 52.50%, ranks twenty-first, and
reproduces the same Top-10 papers for only 50.00% of questions. These values
measure retrieval of all sources needed to adjudicate a contradiction, not
the correctness of a generated answer.

## Evaluation in brief

The portfolio has two independent evaluation layers.

1. **Replicated retrieval.** Each route receives the same sixty evaluation-only questions
   and returns ranked paper-level evidence. Recall@10 measures how much required
   evidence appears in the first ten distinct papers. MRR@10 rewards placing
   the first relevant paper early. nDCG@10 rewards ordering the full relevant
   set well. Exact evidence validation checks record identity, safe paths,
   locators, hashes, and authoritative-core parity. P95 latency is an
   operational diagnostic, not a service-level benchmark.
2. **Grounded Harbor answers.** An agent uses a frozen consultation skill to
   answer a question under a strict JSON and evidence contract. The mechanical
   verifier checks response shape, exact evidence identity, locator and hash
   validity, document coverage, focus coverage, and ranking diagnostics.
   Separate semantic adjudication evaluates correctness, completeness,
   important negatives, and grounding. Mechanical reward and semantic quality
   are intentionally not collapsed into one score.

The dataset registry also supports two isolated execution modes:
`build-consult`, which builds knowledge from read-only raw input during the
trial, and `consult-only`, which mounts only an exact processed snapshot. Raw
sources, processed knowledge, questions, qrels, and evaluator material are kept
on their declared sides of the boundary.

## Evidence order

| Priority | Scope | Status | Current source |
| ---: | --- | --- | --- |
| 1 | GraphRAG 40-question contradiction-search retrieval | Complete comparable twenty-five-strategy table; primary metric requires all contradiction sides | [`graphrag-unseen-generalization/study-v5-contradictions/publication/tables/contradiction-strategy-ranking.table.md`](graphrag-unseen-generalization/study-v5-contradictions/publication/tables/contradiction-strategy-ranking.table.md) |
| 2 | GraphRAG 60-question evaluation-only direct retrieval | Complete comparable twenty-five-strategy table; ranking applies only to this scope | [`graphrag-unseen-generalization/study-v4-general-organized/publication/tables/general-strategy-ranking.table.md`](graphrag-unseen-generalization/study-v4-general-organized/publication/tables/general-strategy-ranking.table.md) |
| 3 | GraphRAG artifact-wide revised current-metrics rescore | Current grounded-answer diagnostic; not ranking-eligible | [`semantic-okf-datasets/reports/20260724-graphrag-papers-40-current-metrics-table.md`](semantic-okf-datasets/reports/20260724-graphrag-papers-40-current-metrics-table.md) |
| 4 | Astro live Harbor baseline-to-evolved pilot | Valid but limited to three selected questions per family | [`semantic-okf-harbor/RESULTS.md`](semantic-okf-harbor/RESULTS.md) |
| 5 | Graphify builder evolution | Retrieval promotion only; different benchmark and scope | [`semantic-okf-harbor/reports/graphify-builder-evolution.md`](semantic-okf-harbor/reports/graphify-builder-evolution.md) |
| 6 | File, embeddings, Turso, and Graphify storage capabilities | Capability comparison; not a retrieval leaderboard | [`semantic-okf-storage-versions/comparison-report.md`](semantic-okf-storage-versions/comparison-report.md) |
| 7 | GraphRAG campaign history and readiness | Operational provenance; no valid eight-family winner | [`semantic-okf-datasets/reports/graphrag-papers-consult-campaign-evolution.md`](semantic-okf-datasets/reports/graphrag-papers-consult-campaign-evolution.md) |
| 8 | Two-stage token efficiency | Artifact-only construction and consultation diagnostics with separate denominators | [`semantic-okf-datasets/reports/20260730-semantic-okf-token-usage.md`](semantic-okf-datasets/reports/20260730-semantic-okf-token-usage.md) |
| 9 | Classical bounded-section token study | Six-question development and disjoint holdout; semantic quality preserved, promotion rejected on token consistency | [`semantic-okf-classical-token-efficiency-study-v4/publication/tables/classical-token-efficiency-v34.table.md`](semantic-okf-classical-token-efficiency-study-v4/publication/tables/classical-token-efficiency-v34.table.md) |

Older `last_report.md`, historical campaign summaries, forensic reports, and
superseded aggregations remain evidence at their original paths. They do not
override the sources above.

## Contradiction-search comparison

The contradiction-search dataset adds no papers. It contains forty new,
evaluation-only questions over the same fifteen papers: fifteen require two
papers, twenty require three, and five require four. Each asks the retriever to
surface every source needed to distinguish a direct contradiction from a
scope-conditioned tension, an incommensurable result, or a compatible
trade-off.

Full evidence@10 is the primary metric because finding only one side cannot
support contradiction adjudication. The complete metric-only
[twenty-five-strategy table](graphrag-unseen-generalization/study-v5-contradictions/publication/tables/contradiction-strategy-ranking.table.md)
also reports Recall@10, MRR@10, nDCG@10, query stability, and P95 latency. All
returned evidence passed exact identity validation and the aggregate table
passed both final-report validators.

This new evidence supports v45 as the best contradiction-source retriever in
this frozen population. It does not support replacing the broader operational
default without a separate decision, and it does not measure generated-answer
correctness. The contradiction questions, qrels, adjudications, and rankings
remain forbidden inputs to construction, profile forging, evolution, trace
distillation, candidate repair, or optimizer-visible selection.

## Direct comparison

The table includes one current representative for each evaluated candidate
lineage under the GraphRAG sixty-question evaluation-only Top-10 contract and
orders rows by nDCG@10, MRR@10, Recall@10, P95, and stable strategy ID. When a frozen
specialized expert evolves an existing row, it replaces that predecessor here;
the complete route and predecessor history remains in the linked study reports.

| Pos. | Pair / strategy | Recall@10 | MRR@10 | nDCG@10 | Stable queries | P95 |
|---:|---|---:|---:|---:|---:|---:|
| 1 | Classical association | 100.00% | 100.00% | 99.60% | 100.00% | 664.65 ms |
| 2 | Classical fusion | 100.00% | 100.00% | 99.38% | 100.00% | 671.43 ms |
| 3 | Adaptive fusion | 100.00% | 100.00% | 99.38% | 100.00% | 2405.80 ms |
| 4 | Ensemble `robust` | 100.00% | 100.00% | 99.38% | 100.00% | 2486.93 ms |
| 5 | Classical topic | 100.00% | 100.00% | 99.31% | 100.00% | 665.76 ms |
| 6 | Specialized expert early confidence-gated hybrid | 100.00% | 99.17% | 99.03% | 100.00% | 989.63 ms |
| 7 | RustMallet association | 100.00% | 100.00% | 98.91% | 100.00% | 677.64 ms |
| 8 | RustMallet fusion | 100.00% | 100.00% | 98.85% | 100.00% | 684.80 ms |
| 9 | RustMallet topic | 100.00% | 100.00% | 98.68% | 100.00% | 682.38 ms |
| 10 | RustMallet BM25 | 98.33% | 100.00% | 98.11% | 100.00% | 650.81 ms |
| 11 | Classical BM25 | 98.33% | 100.00% | 98.11% | 100.00% | 665.72 ms |
| 12 | Ensemble `fast` | 100.00% | 96.67% | 97.58% | 100.00% | 2794.83 ms |
| 13 | Specialized expert Ensemble quality + trace v48 | 100.00% | 96.67% | 97.24% | 100.00% | 4855.90 ms |
| 14 | Tantivy BM25 | 100.00% | 96.25% | 96.25% | 100.00% | 128.27 ms |
| 15 | Entity Graph lexical | 98.89% | 92.55% | 92.70% | 100.00% | 485.78 ms |
| 16 | Embeddings lexical | 98.89% | 91.94% | 92.05% | 100.00% | 298.04 ms |
| 17 | Tika/MALLET fusion | 99.44% | 90.85% | 91.28% | 100.00% | 99.48 ms |
| 18 | Entity Graph fusion | 97.78% | 86.81% | 86.05% | 100.00% | 478.67 ms |
| 19 | Entity Graph entity | 95.83% | 82.39% | 81.77% | 100.00% | 471.66 ms |
| 20 | Entity Graph traversal | 93.89% | 75.22% | 75.89% | 100.00% | 478.05 ms |
| 21 | Tika/MALLET/Tantivy fusion | 93.06% | 61.30% | 66.38% | 100.00% | 2883.27 ms |
| 22 | Embeddings hybrid | 79.72% | 65.61% | 65.33% | 100.00% | 545.45 ms |
| 23 | Legacy lexical | 97.78% | 49.69% | 60.54% | 100.00% | 9.96 ms |
| 24 | Embeddings vector | 69.44% | 53.58% | 52.60% | 100.00% | 251.61 ms |
| 25 | Specialized expert supervised profiles v51 | 71.11% | 34.11% | 41.03% | 43.33% | 142.67 ms |

### Operational recommendation

Use the matched classical pair
`build-semantic-okf-classical` plus `consult-semantic-okf-classical` in
`association` mode when retrieval quality is the primary constraint. Use the
measured `consult-semantic-okf-tantivy` route over its frozen validated
classical projection as the provisional quality/latency runtime default.
Tantivy is 5.18 times faster at P95, preserves 100% Recall@10, and gives up
3.35 nDCG percentage points relative to classical association. A fresh
`build-semantic-okf-tantivy` plus `consult-semantic-okf-tantivy` pair still
requires validation on a new sealed cohort.

The [skill-group recommendation](graphrag-unseen-generalization/STRATEGY-RECOMMENDATION.md)
and [Pareto frontier](graphrag-unseen-generalization/study-v4-general-organized/publication/tables/quality-latency-frontier.table.md)
document the decision rules and limitations. This is operational guidance, not
formal promotion; a default change requires a newly sealed validation cohort.

The remaining registered or evaluated strategies are retained below instead
of being mixed into the ranking with unavailable metrics.

| Pair / strategy without a comparable direct measurement |
|---|
| Graphify |
| Turso |

Graphify's accepted retrieval result uses a separate Astro benchmark, Turso's
accepted evidence evaluates storage and bounded SQL capabilities.

The twenty-five strategy definitions were frozen before evaluation-only
release. Every row completed three process repetitions against the registered
question digest, with zero query errors and exact evidence validity. The full
[aggregate table](graphrag-unseen-generalization/study-v4-general-organized/publication/tables/general-strategy-ranking.table.md)
is sealed by the study ledger. Graphify and Turso remain outside the ranking
because neither exposes the same paper-level Top-10 route.

The evaluation-only question bytes, qrels, rankings, and diagnostics are
forbidden inputs to construction, profile forging, evolution, trace
distillation, candidate repair, or later selection. V51 remains a valid
fixed-workload experiment, but this result shows that its exposed supervised
profile does not generalize reliably to new questions over the same corpus.

## Revised-evaluation table: registered pairs

Every value in this table comes from the revised current-metrics report.
`Qualified rate` and the two means use emitted answers only. `P/Pt/F` means
semantic pass, partial, and fail. The table follows registry order and has no
rank column because the response coverage is not comparable.

| Build / consult pair | Trials / Q | Emitted | Reviewed | Contract | Qualified | Qualified rate | Mean utility | Mean reward | Semantic P/Pt/F |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `build-semantic-okf` + `consult-semantic-okf` | 40 / 40 | 7 | 7 | 0/7 | 0/7 | 0.0% | 0.000 | 0.000 | 0/7/0 |
| `build-semantic-okf-embeddings` + `consult-semantic-okf-embeddings` | 40 / 40 | 4 | 4 | 3/4 | 1/4 | 25.0% | 0.665 | 0.210 | 0/4/0 |
| `build-semantic-okf-classical` + `consult-semantic-okf-classical` | 40 / 40 | 6 | 6 | 6/6 | 1/6 | 16.7% | 0.568 | 0.124 | 0/6/0 |
| `build-semantic-okf-adaptive` + `consult-semantic-okf-adaptive` | 41 / 40 | 5 | 5 | 3/5 | 2/5 | 40.0% | 0.313 | 0.172 | 0/5/0 |
| `build-semantic-okf-entity-graph` + `consult-semantic-okf-entity-graph` | 40 / 40 | 4 | 4 | 1/4 | 0/4 | 0.0% | 0.145 | 0.000 | 0/3/1 |
| `build-semantic-okf-ensemble` + `consult-semantic-okf-ensemble` | 40 / 40 | 0 | 0 | 0/0 | 0/0 | — | — | — | 0/0/0 |
| `build-semantic-okf-graphify` + `consult-semantic-okf-graphify` | 40 / 40 | 0 | 0 | 0/0 | 0/0 | — | — | — | 0/0/0 |
| `build-semantic-okf-turso` + `consult-semantic-okf-turso` | 40 / 40 | 6 | 6 | 0/6 | 0/6 | 0.0% | 0.000 | 0.000 | 0/6/0 |

### What the revised table supports

- Adaptive has the highest observed mechanical qualification rate among its
  emitted answers, 2/5 or 40.0%, but all five reviewed answers are semantically
  partial and thirty-six trials emitted no answer. This is not a winner claim.
- Embeddings has the highest mean mechanical utility and reward among the
  registered families that emitted answers, but only four of forty trials
  emitted an answer and all four are semantically partial.
- Classical is the only registered family whose six emitted answers all pass
  the response contract. Only one is mechanically qualified, and all six are
  semantically partial.
- Ensemble and Graphify have no emitted response in the revised inventory.
  Their numeric absence is preserved rather than converted to zero quality.
- Entity graph has the only semantic failure among the registered-family rows.
  Legacy and Turso emitted reviewed answers, but none passed the current
  response or mechanical qualification contracts.

## Revised-evaluation table: experimental strategies

These rows also come from the revised evaluator, but they represent different
candidate revisions, question counts, and repeated development work. They must
not be ranked against the eight registered pairs or against one another as if
they were one balanced campaign.

| Strategy identity | Trials / Q | Emitted | Reviewed | Contract | Qualified | Qualified rate | Mean utility | Mean reward | Semantic P/Pt/F |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `tika-mallet-bounded-v4` | 1 / 1 | 0 | 0 | 0/0 | 0/0 | — | — | — | 0/0/0 |
| `tika-mallet-canonical-text` | 4 / 1 | 2 | 2 | 2/2 | 1/2 | 50.0% | 0.662 | 0.359 | 0/2/0 |
| `tika-mallet-canonical-text-v2` | 6 / 6 | 5 | 5 | 5/5 | 5/5 | 100.0% | 0.604 | 0.604 | 0/5/0 |
| `tika-mallet-canonical-text-v3` | 30 / 30 | 29 | 29 | 27/29 | 17/29 | 58.6% | 0.655 | 0.402 | 3/26/0 |
| `tika-mallet-tantivy-canonical-text` | 154 / 15 | 141 | 107 | 115/141 | 88/141 | 62.4% | 0.566 | 0.454 | 0/104/3 |

## Token efficiency

All eight registered strategy families now have comparable construction and
consultation measurements. Construction used 16 newly submitted, qualified
one-folder builder calls (two independent replicas per family); every pair
produced a byte-identical knowledge tree. Consultation reuses 48 existing
common-cohort traces (the same six held-out questions per family).

Construction and consultation remain separate leaderboards because one unit is
a generated knowledge folder and the other is a submitted query.

| Construction rank | Strategy | Qualified folders | Mean total tokens per folder |
|---:|---|---:|---:|
| 1 | Classical | 2 | 5,734.50 |
| 2 | Entity Graph | 2 | 6,299.00 |
| 3 | Embeddings | 2 | 6,543.00 |
| 4 | Adaptive | 2 | 6,882.00 |
| 5 | Legacy | 2 | 7,003.50 |
| 6 | Ensemble | 2 | 7,291.00 |
| 7 | Turso | 2 | 8,557.00 |
| 8 | Graphify | 2 | 9,836.00 |

| Submitted-query rank | Strategy | Queries | Runtime errors | Complete responses | Mean total tokens per submitted query |
|---:|---|---:|---:|---:|---:|
| 1 | Graphify | 6 | 6 | 0 | 325,279.00 |
| 2 | Ensemble | 6 | 6 | 0 | 1,099,499.50 |
| 3 | Embeddings | 6 | 1 | 5 | 1,397,144.33 |
| 4 | Classical | 6 | 1 | 5 | 1,539,005.33 |
| 5 | Legacy | 6 | 0 | 6 | 1,585,536.83 |
| 6 | Adaptive | 6 | 2 | 4 | 1,871,644.67 |
| 7 | Turso | 6 | 0 | 6 | 2,109,545.83 |
| 8 | Entity Graph | 6 | 3 | 3 | 2,433,148.67 |

The construction mean across all strategies is 7,268.25 total tokens per
folder. The submitted-query mean is 1,545,100.52 across 48 queries, including
19 runtime errors. Graphify and Ensemble appear cheapest only because all of
their consultation trials failed before producing complete responses. Among
the zero-error strategies, Legacy is the lower-cost option and Turso the
higher-cost option.

Harbor input already includes cached input, so total is input plus output;
cache is reported separately and never added twice. All 25 deterministic
direct-retrieval helpers consume zero LLM tokens during retrieval; later answer
generation is outside that unit. See the full
[methodology, input/output, cache, and failure tables](semantic-okf-datasets/reports/20260730-semantic-okf-token-usage.md).

A separate bounded-section Classical study preserved all six holdout answers
and lowered mean consultation usage by 8.96%, but reduced tokens in only four
of six cases against a frozen five-case requirement. It was not promoted; see
the [aggregate development and holdout table](semantic-okf-classical-token-efficiency-study-v4/publication/tables/classical-token-efficiency-v34.table.md).

## Grounded Harbor status

### GraphRAG

The 2026-07-24 artifact-only recalculation is the newest scored report:

| Measure | Result |
| --- | ---: |
| Raw trial artifacts rescored | 516 / 516 |
| Trials that emitted an answer | 209 |
| Semantically reviewed responses | 175 |
| Current mechanical qualification passes | 115 / 516 |
| Questions with empirical response coverage | 29 / 40 |
| Provider-quota outcomes | 257 |
| Full-dataset empirical claim eligible | No |

The family response counts are too uneven for a fair ranking: some registered
families emitted no answer, while later candidate workflows contributed many
repeated development responses. Mechanical qualification rates in that report
use emitted answers only and must not be interpreted as family win rates.

Campaign 01 has all 320 result artifacts but only 32 complete final responses
and 254 provider-quota outcomes. Campaign 02 stopped after its first counted
preflight hit provider quota. Campaign 03 was abandoned before a model call
because of a cross-platform digest-ordering defect. Campaign 04 corrected that
defect but was superseded before execution because its closure did not bind all
runtime inputs. Campaign 05 is the closed version-2 successor; its tracked
state has zero model calls and no evaluable ranking.

### Latest valid live comparison

The latest complete baseline-to-evolved Harbor comparison remains the limited
Astro pilot: six families, two generations, and three prospectively selected
questions, for 36 accepted trials.

| Family | Current conclusion |
| --- | --- |
| Classical | Strongest mechanical primary candidate; concise answers still need semantic-completeness checks. |
| Embeddings | Most consistently positive evolution across the three live questions and strongest selected hard-recall route in that study. |
| Entity graph | Valuable complementary strategy with strong development semantics but weaker holdout evidence coverage. |
| Legacy | Mechanical promotion, retained primarily as a compatibility baseline. |
| Adaptive | Rejected because development evidence validity, quality, reward, and completeness gates regressed. |
| Ensemble | Pending because a baseline timeout made one declared non-regression gate unobservable. |

This pilot is real model evidence, but three selected questions per family do
not establish a full-dataset or cross-domain winner.

## Bottom line

For direct deterministic retrieval, the retrospective v48 specialized expert
has the strongest observed all-40 ordering at 86.02% nDCG@10 and is position
1 of 24. It also reaches 85.39% Recall@10 and 100.00% MRR@10, at a higher
2012.48 ms P95. Within the accepted Ensemble family, `quality` remains the
strongest canonical policy and the stronger hard-10 ordering choice. The v48
rank measures its deterministic helper, not grounded-answer behavior, and does
not qualify the candidate for promotion without a new untouched cohort.

The revised grounded evaluation still does not support a GraphRAG winner.
Adaptive's 40.0% and Embeddings' 25.0% qualification rates describe only five
and four emitted answers, respectively; they are not full-family win rates.
The three semantic passes in the complete inventory belong to an experimental
Tika/MALLET revision, not to a balanced registered family campaign.

A grounded pair may be ranked only after one frozen, balanced campaign produces
forty scorer-observable answers per registered family with no provider or
evaluator failures and receives separate semantic review. Until then, use the
supplemental retrieval and capability reports only for their explicitly
declared operational scopes.
