# Semantic OKF Alternatives: Results and Conclusions

## Executive conclusion

There is no single winner for every layer of the task.

- **Classical fusion remains the recommended broad retrieval default.** Adaptive fusion has the
  highest observed all-40 Recall@10 and nDCG@10, but its lead over classical fusion is only 0.36 and
  0.20 percentage points, comes from one of forty questions, disappears on the hard ten, and costs
  about 3.13 times as much query time in the recorded diagnostic.
- **Entity graph is the best navigation and first-hit alternative.** Its lexical route has the highest
  all-40 MRR@10, 96.67%, and its explicit entity-to-claim-to-paper-section edges make evidence paths
  easier to inspect. Its fusion route is broad, but still trails classical and adaptive fusion on
  hard-question recall and nDCG.
- **Embedding consultation was the strongest original isolated consult treatment.** Among the five
  first-generation treatments, it had the highest answer correctness, completeness, evidence
  validity, grounding, paper coverage, and source coverage.
- **The evolved adaptive generation 2 is now the strongest adaptive end-to-end policy.** It achieved
  100% response-contract compliance, 98.0% correctness, 94.4% evidence validity, 93.7% grounding,
  84.8% completeness, 93.0% required-paper coverage, and 100% important-negative coverage. In its
  isolated paired run, adding the skill improved validity by 20.9 points and grounding by 21.1 points,
  while reducing completeness by 4.2 points and correctness by 0.8 points.
- **Adaptive generation 0 remains a complementary high-grounding survivor.** Its treatment reached
  97.6% evidence validity, 97.7% grounding, and 58.5% exact atomic-ID coverage, all higher than
  generation 2 in separate runs. Generation 2 is preferable as the default because it reliably emits
  the required response contract, avoids unsupported full abstention, and has higher correctness,
  paper/source coverage, and negative coverage. Cross-run differences are descriptive, not causal.

The frozen expected-ID audit found all 44 atomic mappings sensible, with zero structural or config
mismatches. Exact-ID coverage remains deliberately stricter than semantic correctness; it should be
read as an evidence-identity diagnostic, not as the sole answer-quality score.

## How to read the retrieval numbers

- **Recall@10** is the average fraction of required papers found in the first ten paper-level results.
  It measures breadth. If four of five required papers are found, that question contributes 80%.
- **MRR@10** rewards putting the first relevant paper early. Rank 1 contributes 1.0, rank 2 contributes
  0.5, and rank 3 contributes about 0.333. It does not measure complete multi-paper coverage.
- **nDCG@10** rewards retrieving several required papers and placing them near the top. It combines
  breadth and order, but still does not measure answer correctness.
- **Evidence validity** checks that a returned record, path, locator, hash, concept, and authoritative
  binding really exist and agree. Every direct route achieved 100%.
- **Mean milliseconds** is a diagnostic from this machine and execution method, not a portable service
  latency benchmark.

## Direct retrieval comparison over the frozen forty questions

All rows use the same 15 Markdown papers, 15 reviewed-claim ledgers, original 30 questions, new 10 hard
questions, direct top-10 paper budget, and evidence-valid schema 1.2 evaluator.

| Builder / consultant | Route | All Recall@10 | All MRR@10 | All nDCG@10 | Hard Recall@10 | Hard MRR@10 | Hard nDCG@10 | Valid evidence | Mean ms |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Legacy | lexical | 79.31% | 78.96% | 74.22% | 80.67% | 57.50% | 56.81% | 100% | **3.02** |
| Embedding | lexical | 54.75% | 88.83% | 60.92% | 73.50% | 80.33% | 65.78% | 100% | 70.94 |
| Embedding | vector | 50.40% | 78.75% | 54.77% | 61.00% | 66.67% | 53.05% | 100% | 110.60 |
| Embedding | hybrid | 48.34% | 88.54% | 56.51% | 65.17% | 87.50% | 64.60% | 100% | 202.46 |
| Entity graph | lexical | 79.76% | **96.67%** | 81.14% | 84.67% | 86.67% | 74.47% | 100% | 116.94 |
| Entity graph | entity | 79.58% | 86.04% | 76.72% | 85.00% | 71.67% | 66.08% | 100% | 120.73 |
| Entity graph | traversal | 78.49% | 80.21% | 74.03% | 86.67% | 75.00% | 69.65% | 100% | 117.54 |
| Entity graph | fusion | 80.84% | 93.12% | 79.86% | 91.67% | 90.00% | 76.32% | 100% | 110.71 |
| Classical | BM25 | 49.72% | 95.83% | 60.94% | 63.17% | **95.00%** | 69.31% | 100% | 86.43 |
| Classical | topic | 82.42% | 93.33% | 82.25% | 93.00% | **95.00%** | 83.75% | 100% | 94.62 |
| Classical | association | 82.56% | 94.58% | 82.58% | 93.00% | **95.00%** | 84.76% | 100% | 94.64 |
| Classical | fusion | 83.46% | 95.83% | 83.23% | **95.50%** | **95.00%** | **84.98%** | 100% | 94.63 |
| Adaptive | fusion | **83.82%** | 95.83% | **83.43%** | **95.50%** | **95.00%** | **84.98%** | 100% | 296.45 |

The bold adaptive lead is an observed score, not evidence of general superiority. Adaptive and
classical fusion tie on every hard-ten metric, and 39 of 40 paired questions are identical. The only
change is one extra required paper at rank ten for `q011-vector-graph-hybrid`.

The direct embedding rows look weaker partly because ten chunk results can contain repeated papers.
In the prior pool-100 sensitivity analysis, paper-aware deduplication increased hard Recall@10 to
93.0% for embedding lexical, 78.0% for vector, and 90.5% for hybrid. Those larger-pool numbers are not
directly comparable with the fixed top-10 table above.

## Actual grounded-answer comparison on the hard ten

This table evaluates generated answers, not retrieval lists. Correctness, completeness, and negatives
come from blinded fixed-rubric review. Evidence validity and grounding are independently recomputed
from authoritative claim bindings, paths, papers, and integer PDF pages.

| Consult treatment | Contract | Evidence validity | Grounding | Correctness | Completeness | Exact atomic IDs | Papers | Sources | Negatives |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Legacy | 10.0% | 84.3% | 83.5% | 88.8% | 75.0% | 50.5% | 75.0% | 74.0% | 90.0% |
| Embedding | 40.0% | 83.6% | 83.4% | 96.2% | 82.8% | 48.5% | 89.2% | 85.4% | **100.0%** |
| Classical | 30.0% | 80.4% | 79.7% | 91.5% | 82.2% | 37.0% | 86.7% | 79.2% | 95.0% |
| Entity graph | 40.0% | 60.0% | 60.0% | 78.8% | 70.2% | 31.5% | 67.7% | 57.6% | 90.0% |
| Adaptive, historical | 20.0% | 59.3% | 60.0% | 93.6% | 57.2% | 19.5% | 69.7% | 56.9% | **100.0%** |
| Adaptive, generation 0 | 40.0% | **97.6%** | **97.7%** | 91.3% | **84.8%** | **58.5%** | 90.5% | 90.5% | 97.5% |
| Adaptive, generation 1 | 90.0% | 85.8% | 86.7% | 87.1% | 80.8% | 49.5% | 87.5% | 87.5% | 90.0% |
| Adaptive, generation 2 | **100.0%** | 94.4% | 93.7% | **98.0%** | **84.8%** | 53.5% | **93.0%** | **91.3%** | **100.0%** |

The first five rows and each adaptive generation come from separate stochastic runs. Their absolute
treatment scores are useful descriptions, but differences between rows are not causal estimates.
Only control-versus-treatment differences within the same isolated Skill Arena run support a causal
statement about adding that version of the consult skill.

Generation 1 is rejected despite solving most output-format problems: unrestricted facet evidence
retention reduced correctness, validity, grounding, and negative coverage, and one answer fully
abstained when the corpus supported a substantive response. Its deterministic finalizer and facet
candidate generator were retained as components.

Generation 2 adds a minimal-direct-support policy: expand for discovery, then retain only records that
directly entail a stated answer claim; remove unused or merely topical evidence; split broad claims;
and qualify an unresolved facet rather than nulling a partially supportable answer.

### Causal generation-2 result

| Metric | Same-bundle control | Generation-2 treatment | Treatment minus control |
| --- | ---: | ---: | ---: |
| Response contract | 10.0% | 100.0% | **+90.0 points** |
| Evidence validity | 73.5% | 94.4% | **+20.9** |
| Grounding | 72.6% | 93.7% | **+21.1** |
| Correctness | 98.8% | 98.0% | -0.8 |
| Completeness | 89.0% | 84.8% | -4.2 |
| Exact atomic IDs | 49.5% | 53.5% | +4.0 |
| Required papers | 89.2% | 93.0% | +3.8 |
| Required sources | 79.2% | 91.3% | **+12.2** |
| Important negatives | 100.0% | 100.0% | 0.0 |

The important trade-off is visible: the skill substantially improves evidence mechanics and response
conformance while slightly narrowing semantic coverage. That is why generation 0 remains a Pareto
survivor rather than being erased.

## Evidence discovery beyond one top-30 list

Generation 2 can issue query-derived facet searches and return a paper-diverse candidate set. This is
useful for answer construction, but its larger budget must not be mislabeled as Recall@30.

| Candidate metric | Primary top-30 | Facet union |
| --- | ---: | ---: |
| Exact answer-claim coverage | 60.0% | 76.5% |
| Important-negative coverage | 75.0% | 88.3% |
| Required-paper coverage | 98.0% | 100.0% |
| Mean unique candidate claims | 30 | 81 |

The facet union averages 7.1 facets and 81 unique candidates. It is a candidate-generation tool, not
a fair replacement for the fixed-budget retrieval row.

## Why exact expected IDs make sense—and what they do not prove

The independent audit verified 44 atomic claims, 13 negatives, 42 unique reviewed records, every
claim-line and page hash, and all four Skill Arena configs. It classified 40 atomic mappings as direct
record paraphrases, three as bounded derivations, and one as a page-supported detail. No benchmark
file was changed.

The exact-ID metric is useful because it detects when a response finds the right topic but loses the
canonical evidence identity. It is not a synonym for correctness. A semantically correct answer may
cite another valid record and lose exact-ID points; conversely, citing an expected ID does not prove
the prose made the correct inference.

Negative assertions are even narrower: each accepts at least one declared anchor, so they measure
evidence presence rather than whether the response actually states the exclusion. The blinded review
provides the semantic negative score.

## Why every generation still has zero strict passes

A strict pass requires every assertion simultaneously: exact JSON structure and key order, word
limit, complete canonical ID set, only allowed evidence, valid paths and locators, citation agreement,
all required papers, and all negative anchors. One failed component makes the whole cell fail.

Generation 2 therefore has zero strict conjunctive passes even with 98.0% correctness, 94.4% evidence
validity, and 100% contract compliance. The strict score remains useful as a conformance stress test;
the component table is the meaningful diagnosis.

## Recommended route by need

| Need | Recommended alternative | Reason |
| --- | --- | --- |
| Default broad multi-paper retrieval | Classical fusion | Near-identical best retrieval, hard-ten tie with adaptive, and much lower recorded query cost |
| Long, multi-facet evidence discovery | Adaptive fusion plus coverage pack | Preserves full-query breadth and exposes missing facets before final evidence minimization |
| Current adaptive answer construction | Adaptive generation 2 | Best response contract and correctness with strong independently validated grounding |
| Maximum observed adaptive grounding/exact identity | Adaptive generation 0 | Highest separate-run evidence validity, grounding, and exact-ID coverage |
| Auditable entity/relation navigation | Entity-graph fusion or traversal | Explicit entity-to-claim-to-paper-section paths |
| First precise relevant paper | Entity-graph lexical | Highest all-40 MRR@10 |
| Semantic paraphrases with a larger candidate budget | Embedding hybrid with paper-aware pooling | Semantic matching helps after duplicate-paper chunks are controlled |
| Frozen speed/regression reference | Legacy lexical | Simplest and fastest historical baseline; leave it unchanged |

## Boundaries of the conclusion

- The same ten hard questions were reused for diagnosis and three adaptive generations. They are a
  frozen regression target, not a fresh post-selection holdout.
- The answer runs contain ten treatment answers each and one model route; they do not estimate broad
  population performance.
- Control answers varied materially across runs. Report within-run deltas for causal claims and use
  absolute cross-run rows only descriptively.
- The facet union has a larger variable candidate budget than top-30 retrieval.
- English lexical tokenization, topics, term associations, entity edges, embeddings, rankings, answer
  bindings, and evidence packs are all derived and non-authoritative.
- The authoritative Semantic OKF core remains unchanged, and consultation remains read-only.

## Reproducibility evidence

- [Frozen benchmark manifest](frozen-benchmark.json)
- [Expected-ID audit](EXPECTED-ID-AUDIT.md) and [machine-readable details](expected-id-audit.json)
- [Generation 0 population](GENERATION-000.md) and [summary](generation-000-summary.json)
- [Generation 1 result](GENERATION-001.md) and [summary](generation-001-summary.json)
- [Generation 2 result](GENERATION-002.md) and [summary](generation-002-summary.json)
- [Facet coverage report](COVERAGE-PACK.md) and [summary](coverage-pack-summary.json)
- [Final implementation validation](final-validation-summary.json)
- [Original adaptive retrieval and answer report](../semantic-okf-adaptive/EVALUATION-CONCLUSIONS.md)
- [Entity-graph evaluation](../semantic-okf-entity-graph/README.md)
- [Architecture decision](../../.specs/adr/0022-frozen-adaptive-semantic-okf-evolution.md)
