# Latest Evaluation Report

Cutoff: 2026-07-27.

Newest scored evidence: 2026-07-24.

## Executive result

There is no valid full-dataset grounded Harbor winner across the eight
registered Semantic OKF families. The latest GraphRAG inventory contains 516
rescored trial artifacts, but provider failures and uneven response coverage
leave eleven of forty questions without an empirical response. That inventory
is diagnostic and must not be used as a family ranking.

The strongest current cross-pair evidence is the deterministic GraphRAG
40-question direct-retrieval comparison. Under its fixed direct Top-10
contract:

- definitive Ensemble `quality` has the best observed ordering, with 85.20%
  nDCG@10 and 100.00% MRR@10;
- Adaptive and Ensemble tie for the best all-40 Recall@10 at 83.82%;
- Classical fusion is the simpler practical default: it is only 0.36
  percentage points behind Adaptive on Recall@10 and 0.20 points behind on
  nDCG@10, while its recorded P95 is materially lower;
- Tantivy is the strongest experimental speed/quality tradeoff in the direct
  table, but it remains outside the registered Harbor comparison; and
- every ranked route has 100% exact evidence validity, which establishes
  traceability but not semantic answer correctness.

## Evaluation in brief

The portfolio has two independent evaluation layers.

1. **Deterministic retrieval.** Each route receives the same forty questions
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
| 1 | GraphRAG 40-question direct retrieval | Comparable and rankable within this scope | [`semantic-okf-ensemble/EVALUATION-CONCLUSIONS.md`](semantic-okf-ensemble/EVALUATION-CONCLUSIONS.md) |
| 2 | GraphRAG artifact-wide current-metrics rescore | Current diagnostic; not ranking-eligible | [`semantic-okf-datasets/reports/20260724-graphrag-papers-40-current-metrics-table.md`](semantic-okf-datasets/reports/20260724-graphrag-papers-40-current-metrics-table.md) |
| 3 | Astro live Harbor baseline-to-evolved pilot | Valid but limited to three selected questions per family | [`semantic-okf-harbor/RESULTS.md`](semantic-okf-harbor/RESULTS.md) |
| 4 | Graphify builder evolution | Retrieval promotion only; different benchmark and scope | [`semantic-okf-harbor/reports/graphify-builder-evolution.md`](semantic-okf-harbor/reports/graphify-builder-evolution.md) |
| 5 | File, embeddings, Turso, and Graphify storage capabilities | Capability comparison; not a retrieval leaderboard | [`semantic-okf-storage-versions/comparison-report.md`](semantic-okf-storage-versions/comparison-report.md) |
| 6 | GraphRAG campaign history and readiness | Operational provenance; no valid eight-family winner | [`semantic-okf-datasets/reports/graphrag-papers-consult-campaign-evolution.md`](semantic-okf-datasets/reports/graphrag-papers-consult-campaign-evolution.md) |

Older `last_report.md`, historical campaign summaries, forensic reports, and
superseded aggregations remain evidence at their original paths. They do not
override the sources above.

## Comparable direct-retrieval pairs

This descriptive table selects the highest all-40 nDCG@10 route within each
evaluated pair or experimental workflow, then orders rows by nDCG@10. The
selection rule makes the table compact; it is not a promotion rule or a
universal composite score. All rows use the same frozen forty questions,
canonical paper identities, direct Top-10 budget, and exact evidence contract.

| Rank | Build / consult pair or workflow | Selected route | Status | Recall@10 | Hard Recall@10 | MRR@10 | nDCG@10 | P95 ms |
| ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| 1 | `build-semantic-okf-ensemble` + `consult-semantic-okf-ensemble` | `quality` | Accepted | 83.82% | 95.50% | 100.00% | 85.20% | 1,461.92 |
| 2 | `build-semantic-okf-adaptive` + `consult-semantic-okf-adaptive` | `adaptive_fusion` | Accepted | 83.82% | 95.50% | 95.83% | 83.43% | 407.56 |
| 3 | `build-semantic-okf-classical` + `consult-semantic-okf-classical` | `classical_fusion` | Accepted | 83.46% | 95.50% | 95.83% | 83.23% | 106.76 |
| 4 | Reference-aware RustMallet build/consult workflow | `rust_mallet_topic` | Experimental | 80.80% | 88.50% | 95.00% | 81.86% | 238.70 |
| 5 | `build-semantic-okf-entity-graph` + `consult-semantic-okf-entity-graph` | `entity_graph_lexical` | Accepted | 79.76% | 84.67% | 96.67% | 81.14% | 241.63 |
| 6 | `build-semantic-okf-tantivy` + `consult-semantic-okf-tantivy` | `tantivy_bm25` | Experimental | 80.74% | 92.17% | 93.75% | 81.05% | 90.92 |
| 7 | `build-semantic-okf-tika-mallet` + `consult-semantic-okf-tika-mallet` | `tika_mallet_fusion` | Experimental | 74.82% | 71.83% | 87.50% | 75.44% | 86.36 |
| 8 | `build-semantic-okf` + `consult-semantic-okf` | `legacy_lexical` | Accepted baseline | 79.31% | 80.67% | 78.96% | 74.22% | 4.79 |
| 9 | `build-semantic-okf-embeddings` + `consult-semantic-okf-embeddings` | `new_lexical` | Accepted | 54.75% | 73.50% | 88.83% | 60.92% | 76.20 |

### Interpretation

- Ensemble `quality` improves ordering, not coverage, over Adaptive. It has the
  highest recorded P95 in the table, so it is appropriate when evidence
  ordering and synthesis readiness matter more than latency.
- Adaptive's observed lead over Classical comes from one of forty questions;
  the other thirty-nine tie on Recall@10, MRR@10, and nDCG@10, and the hard ten
  tie exactly. Classical remains the simpler broad default.
- Entity-graph lexical retrieval is strong at placing one relevant result
  early. Entity-graph fusion is preferable when the workflow values broader
  multi-paper graph coverage, even though its nDCG is lower than the lexical
  route selected above.
- Tantivy provides 80.74% Recall@10 and 81.05% nDCG@10 at a measured 90.92 ms
  P95. Its complete replay and pool-100 prefix checks passed, but grounded
  Harbor admission remains a separate gate.
- The Tika/MALLET row is valid for deterministic direct retrieval and exact
  extraction evidence. It does not establish broad format support or grounded
  answer quality.
- The embedding result is sensitive to candidate budget because multiple
  chunks from one paper can occupy the direct Top-10. At a pool of 100 before
  paper deduplication, hard Recall@10 rises to 93.00% for lexical, 78.00% for
  vector, and 90.50% for hybrid. Those different-budget values are correctly
  excluded from the direct leaderboard.
- Latency scopes and setup costs differ. The P95 column supports operational
  tradeoff analysis, not a portable engine benchmark.

## Registered pairs without a comparable row

Graphify and Turso are registered Semantic OKF families, but their latest
accepted evidence answers different questions and is not inserted into the
GraphRAG direct-retrieval leaderboard.

| Pair | Latest measured result | Interpretation |
| --- | --- | --- |
| `build-semantic-okf-graphify` + `consult-semantic-okf-graphify` | On the separate Astro 40-question builder benchmark, the promoted builder reached 77.3% Recall@10, 57.5% hard Recall@10, 0.579 MRR@10, and 0.578 nDCG@10 with 301/301 valid evidence rows. | Promoted for deterministic retrieval only. The paired q032 Harbor answers both failed the unchanged locator contract, so this is not a strict answer-quality win. |
| `build-semantic-okf-turso` + `consult-semantic-okf-turso` | On the 31-source, 874-record storage study, Turso used 4.81 times the file-backed storage and built 21.6% more slowly; exact lookup was 71.1% slower, while grouped aggregation was 21.6% faster. | Prefer Turso for bounded SQL joins, grouping, and batched structured work. The study does not provide a same-contract forty-question retrieval row. |

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

For deterministic GraphRAG retrieval, use Classical fusion as the practical
default, Ensemble `quality` when ranking quality is worth the latency, Adaptive
for complex multi-aspect queries where its extra cost is acceptable, and
Entity graph when auditable entity-to-claim navigation is important. Tantivy
is the most promising experimental low-latency comparator. Keep Legacy for
portability and compatibility, Embeddings for candidate discovery with a
paper-aware larger pool, Graphify for graph navigation, and Turso for batched
relational work.

No pair should be declared the grounded GraphRAG winner until one frozen,
balanced campaign produces forty scorer-observable answers per registered
family with no provider or evaluator failures and receives separate semantic
review.
