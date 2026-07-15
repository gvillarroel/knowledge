# How to Read the Semantic OKF Adaptive Evaluation

This document explains the comparison numbers, the conclusion they support, and the conclusion they
do not support. The benchmark uses the same authoritative corpus and forty questions for every route.

> **Historical result:** this file documents the first adaptive generation. The frozen-benchmark
> evolution retained the retrieval result, repaired answer evidence and serialization, and selected a
> new generation-2 default consult policy. Read the
> [current cross-generation conclusion](../semantic-okf-adaptive-evolution/EVALUATION-CONCLUSIONS.md)
> for the latest recommendation; this report remains unchanged evidence for the historical run.

## Executive conclusion

Adaptive fusion has the best observed overall paper coverage in this direct top-10 run:

- **83.82% recall@10**, compared with 83.46% for classical fusion;
- **83.43% nDCG@10**, compared with 83.23% for classical fusion; and
- **95.83% MRR@10**, tied with classical fusion but below entity-graph lexical at 96.67%.

The numerical lead is real in this run but weak as evidence of general superiority. The entire
adaptive/classical difference comes from one question, `q011-vector-graph-hybrid`; the other 39
questions have identical recall@10, MRR@10, and nDCG@10. On the ten hard questions, adaptive and
classical fusion tie on every reported retrieval metric. The paired descriptive bootstrap intervals
include zero. Adaptive is also about 3.13 times slower than classical fusion in the recorded
in-process diagnostic.

The practical conclusion is therefore:

- use **classical fusion** as the simpler broad default;
- use **adaptive fusion** when a long question contains multiple mechanisms, exclusions, contrasts,
  or failure boundaries and the extra query cost is acceptable;
- use the **entity graph** for auditable entity-to-claim-to-section navigation or a fast first precise
  hit; and
- do not claim that adaptive is universally best until a new untouched benchmark shows a distributed
  gain across more questions and source domains.

The answer-level conclusion is less favorable to the adaptive consult skill. The adaptive bundle by
itself produced the strongest knowledge-only control in the ten-question answer run: 97.50%
correctness, 90.25% completeness, 93.23% evidence validity, and 93.32% grounding. Adding the adaptive
consult skill reduced those values to 93.58%, 57.25%, 59.33%, and 60.00%, respectively. The retriever
is therefore a useful candidate generator, but the current consult instructions are **not** the best
end-to-end answer treatment. Among the five isolated consult treatments, embedding consultation is the
only one with positive paired deltas across correctness, completeness, evidence validity, grounding,
required-paper coverage, and important-negative coverage.

## What each number means

### Recall@10: breadth of required evidence

Recall@10 is the fraction of required paper identities found among the first ten paper-level results,
averaged across questions. If a question requires five papers and the route finds four, that question
contributes 80% recall.

Recall is the most important retrieval metric for multi-paper synthesis because a missing paper may
remove one side of a contrast, an exclusion, or an important failure condition. It does **not** mean
that the final generated answer is correct.

### MRR@10: how early the first relevant paper appears

Mean Reciprocal Rank rewards placing at least one relevant paper near the top. A first relevant result
at rank 1 contributes 1.0, rank 2 contributes 0.5, rank 3 contributes about 0.333, and no relevant
result in the first ten contributes zero.

Entity-graph lexical has the highest overall MRR, 96.67%. That makes it excellent for reaching one
precise relevant section quickly, but MRR alone does not measure whether all required papers were
found.

### nDCG@10: quality of the complete ordering

Normalized Discounted Cumulative Gain rewards placing multiple required papers near the top and
discounts relevant papers that appear later. It combines breadth and ordering, but it still evaluates
paper relevance rather than answer correctness.

### Evidence validity: whether a hit is real and traceable

Evidence validity independently checks the returned source and record identities, safe paths, exact
locator, text hash, concept binding, and authoritative-core parity. Every route achieved 100% validity
with zero query errors. This means score differences are not caused by fabricated paths or stale
bundles.

### Mean milliseconds: diagnostic query cost

Mean milliseconds is the average measured query time for the route. It is useful for comparing this
specific run, but it is not a portable hardware benchmark because route execution scopes and
dependencies differ.

### Percentage points versus percent change

Adaptive recall is 83.82% and classical recall is 83.46%. The absolute difference is **0.36 percentage
points**. It is not a 0.36% relative improvement; relative to 83.46%, it is approximately 0.43%.

## Direct top-10 retrieval table

| Builder / consultant | Route | All recall@10 | All MRR@10 | All nDCG@10 | Hard recall@10 | Hard MRR@10 | Hard nDCG@10 | Valid evidence | Mean ms |
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

## The important comparisons

### Adaptive versus classical fusion

| Cohort | Recall delta | MRR delta | nDCG delta | Interpretation |
| --- | ---: | ---: | ---: | --- |
| All 40 | +0.36 points | 0.00 | +0.20 points | Small observed adaptive lead |
| Original 30 | +0.48 points | 0.00 | +0.26 points | The only aggregate gain is in the development cohort |
| Hard 10 | 0.00 | 0.00 | 0.00 | Exact tie; no hard-cohort regression or gain |

Only one question changed the paired metrics. On `q011-vector-graph-hybrid`, adaptive added one of the
seven required papers at rank 10, increasing that question's recall by 14.29 points and nDCG by 7.95
points. Averaged across forty questions, those become the much smaller 0.36- and 0.20-point gains.

The deterministic 10,000-sample paired-question percentile bootstrap produced:

- recall delta: mean +0.36 points, 95% interval 0.00 to +1.07 points;
- nDCG delta: mean +0.20 points, 95% interval 0.00 to +0.60 points; and
- MRR delta: 0.00 points, interval 0.00 to 0.00.

These are descriptive intervals over this fixed benchmark, not population guarantees. Their zero
lower bounds make the correct claim “highest observed score,” not “proven generally better.”

### Adaptive versus entity graph

Adaptive fusion has 2.97 points more overall recall and 3.57 points more overall nDCG than
entity-graph fusion. Entity-graph lexical nevertheless has 0.83 points more overall MRR than adaptive,
so the graph remains the best route for the first precise relevant result and for explicit relation
navigation.

### Why the direct embedding numbers look low

This table gives every route ten raw results and then evaluates distinct paper identities. Embedding
routes can spend several results on chunks from the same paper, reducing paper coverage. The existing
pool-100 sensitivity experiment raises embedding hard recall substantially before paper deduplication:

| Embedding route | Direct hard recall@10 | Pool-100 hard recall@10 |
| --- | ---: | ---: |
| Lexical | 73.50% | 93.00% |
| Vector | 61.00% | 78.00% |
| Hybrid | 65.17% | 90.50% |

The adaptive final run did not repeat pool-100. Those values come from the prior entity-graph
evaluation and should be treated as a candidate-budget sensitivity result, not as part of the direct
adaptive table.

## Recommended use by need

| Need | Recommended route | Reason |
| --- | --- | --- |
| Default broad multi-paper retrieval | Classical fusion | Nearly identical top score, hard-ten tie, and about one-third the adaptive query time |
| Long multi-aspect question | Adaptive fusion | Preserves the full query while allowing a top aspect result to add evidence |
| Auditable entity or relation navigation | Entity-graph fusion or traversal | Explicit paths from entities and reviewed claims to exact sections |
| First precise relevant hit | Entity-graph lexical | Highest overall MRR@10 |
| Semantic paraphrase retrieval | Embedding hybrid with a larger paper-aware candidate pool | Semantic matching helps, but direct chunk budgets suppress paper coverage |
| Frozen regression baseline | Legacy lexical | Fast, simple historical reference |
| Current isolated answer treatment | Embedding consult | Only treatment with consistently positive paired answer deltas on the hard ten |

## Actual grounded-answer comparison

The retrieval table asks whether a route found relevant papers. This table instead summarizes ten
actual answers from each isolated consult treatment. Correctness, completeness, and important
negatives come from a blinded fixed-rubric review. Evidence validity and grounding are recomputed
deterministically against the authoritative ledger, concept paths, paper identities, and integer PDF
pages.

| Consult treatment | Contract | Evidence validity | Grounding | Correctness | Completeness | Exact atomic IDs | Papers | Sources | Negatives |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Legacy | 10.0% | 84.3% | 83.5% | 88.8% | 75.0% | **50.5%** | 75.0% | 74.0% | 90.0% |
| Embedding | **40.0%** | **83.6%** | **83.4%** | **96.2%** | **82.8%** | 48.5% | **89.2%** | **85.4%** | **100.0%** |
| Classical | 30.0% | 80.4% | 79.7% | 91.5% | 82.2% | 37.0% | 86.7% | 79.2% | 95.0% |
| Entity graph | **40.0%** | 60.0% | 60.0% | 78.8% | 70.2% | 31.5% | 67.7% | 57.6% | 90.0% |
| Adaptive | 20.0% | 59.3% | 60.0% | 93.6% | 57.2% | 19.5% | 69.7% | 56.9% | **100.0%** |

These are absolute treatment scores, not causal deltas. The embedding treatment is strongest overall:
it has the highest correctness, completeness, evidence validity, grounding, paper coverage, and source
coverage among the five treatment rows. Adaptive preserves high claim correctness and all important
negatives, but it omits many required answer facets and often fails to carry exact evidence identities
through to the response.

### Adaptive control versus treatment

The isolated Skill Arena comparison keeps the bundle, model, prompts, restrictions, and execution
settings fixed. The only declared capability difference is the adaptive consult skill. Positive
deltas would favor adding the skill.

| Metric | Knowledge-only control | Adaptive treatment | Treatment minus control |
| --- | ---: | ---: | ---: |
| Response contract | 40.00% | 20.00% | -20.00 points |
| Evidence validity | 93.23% | 59.33% | -33.90 points |
| Grounding | 93.32% | 60.00% | -33.32 points |
| Claim correctness | 97.50% | 93.58% | -3.92 points |
| Semantic completeness | 90.25% | 57.25% | -33.00 points |
| Exact atomic evidence IDs | 73.50% | 19.50% | -54.00 points |
| Required papers | 88.33% | 69.67% | -18.67 points |
| Required sources | 88.33% | 56.92% | -31.42 points |
| Important negatives | 100.00% | 100.00% | 0.00 points |

The treatment's stated claims were usually faithful to the records it cited, which explains its high
93.58% correctness. That is different from completeness: several answers missed entire required
mechanisms, baselines, exclusions, or stage distinctions. Four of ten treatment answers also emitted
full `sources/...#PDF-page-N` locator strings where the response contract required integer page
numbers. Those rows could contain real retrieved evidence while still scoring zero for independently
valid answer evidence and grounding.

An earlier diagnostic run exposed the same serialization family and prompted a stricter output
adapter instruction. In the accepted final run, evidence validity rose from 41.39% in that diagnostic
to 59.33%, but completeness fell from 75.25% to 57.25%. Because these were separate stochastic answer
runs over the same questions, this is not a causal before/after estimate. The correct conclusion is
that the instruction-only repair did not establish a reliable end-to-end fix. A deterministic
serializer outside the answer model is still needed.

### Why zero strict passes does not mean zero correct answers

Every profile has a 0% strict all-contract pass rate. A strict cell requires every condition to pass
simultaneously: JSON key order, word limits, exact identities, valid paths, integer pages, citation
agreement, atomic claim coverage, and important negatives. One failed condition makes the complete
cell fail. The strict score is retained as a conformance stress test; the component metrics above are
the useful diagnosis. For example, adaptive treatment has 0% strict success but 93.58% claim
correctness.

## Evaluation boundaries

- Retrieval metrics do not establish answer correctness, completeness, grounding, or response-contract
  compliance. The separate actual-answer evaluation measures those properties on only the ten hard
  questions.
- Adaptive parameters were selected on the original thirty questions. The hard ten were a
  no-regression cohort, not a pristine post-selection holdout.
- The hard questions were reused for paired answer evaluation and for one diagnostic instruction
  repair. A new question set is needed for a fresh generalization or repair-effect claim.
- The answer comparison contains one model route and ten answers per profile; it has no
  confidence-bounded population estimate.
- The tokenizer and stopword list are English-oriented.
- All topics, associations, query aspects, graph edges, embeddings, and rankings remain derived
  discovery signals. The authoritative Semantic OKF core is unchanged.

## Reproducibility evidence

- [Compact retrieval report](retrieval-summary.md)
- [Machine-readable retrieval summary](retrieval-summary.json)
- [Grounded-answer component and paired tables](grounded-answer-summary.md)
- [Machine-readable grounded-answer summary](grounded-answer-summary.json)
- [Accepted Skill Arena run binding](skill-arena/final-run-summary.json)
- [Superseded diagnostic run binding](skill-arena/diagnostic-run-summary.json)
- [Architecture and reproduction commands](README.md)
- [Evaluation runtime](evaluation-environment.json)
- [Determinism report](determinism-report.json)
- [Manual read-only query verification](manual-query-verification.json)
- [Adaptive architecture decision](../../.specs/adr/0021-adaptive-evidence-fusion-semantic-okf-retrieval.md)
- [Legacy `rg` and evaluator investigation](../semantic-okf-classical/legacy-grep-investigation.md)
