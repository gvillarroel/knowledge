# ADR 0073: Evolve v43 with retrospective Harbor Pareto search

## Status

Accepted on 2026-07-28 for a deterministic retrieval candidate and retrospective
ranking. This is not a holdout-qualified promotion or a grounded answer-quality
claim.

## Context

ADR 0072 froze `graphrag-trace-expert-v43` after selecting its fielded BM25
adapter on a 24-question discovery cohort and confirming it on q031-q040. On the
canonical all-40 retrieval contract, v43 reached 82.88% Recall@10, 87.65%
MRR@10, and 81.76% nDCG@10, placing it 10 of 24.

The q031-q040 confirmation cases exposed two complementary weaknesses. Generic
field scoring under-ranked questions about non-monotonic context budgets and
lossless-enough evidence organization. At the same time, the qualified v46
knowledge snapshot already contained immutable classical passage-BM25,
PPMI-association, and MALLET-topic artifacts that v43 did not use.

All registered GraphRAG retrieval cohorts, including the six canonical holdout
questions, had already been exposed by prior studies. No remaining cohort could
serve as an untouched promotion gate for another v43 mutation.

## Decision

Use native Harbor 0.18.0 jobs and the reflective Pareto protocol to run a
retrospective search on q031-q040. Preserve the frozen v43 expert as the
generation-zero baseline. Require every trial to pass manifest binding, exact
evidence, and mechanical qualification gates.

The task protocol reads the helper's raw `/logs/agent/retrieval.json` artifact.
Two earlier diagnostic schemas are excluded: the first normalized arXiv
identities incorrectly, and the second allowed an otherwise valid retrieval to
be confounded by model transcription of the result artifact.

Evaluate two generation-one mutations:

- a facet-balanced trace rank; and
- a classical hybrid that combines v43's trace rank with the snapshot's
  passage-BM25, PPMI-association, and MALLET-topic rank through weighted
  reciprocal-rank fusion.

The hybrid uses RRF constant 60, trace weight 1.0, and classical weight 2.0. It
raises q031-q040 nDCG@10 from 70.40% to 80.79%, Recall@10 from 85.50% to
95.50%, and MRR@10 from 67.26% to 83.33%.

Retain a generation-two agreement-gated alternative in the Pareto archive. It
has no q031-q040 case regression against v43 and reaches 80.68% nDCG@10, but
the original hybrid remains the aggregate winner at 80.79%.

Materialize the exact winning query helper as the reusable
`query_expert_knowledge_trace_classical_hybrid.py` packaging template and
package `graphrag-trace-expert-v44`. The helper SHA-256 is
`25adc3196b0bc21769f3115a4c5889a5369f5ae211418ddbfdece5e447e44ead`;
the embedded 108-file knowledge tree remains
`e787e3ef4a2c2a3a624be0803a3536ab24c2dcdd66e4b894c2d0ec10634f1d9e`.

Evaluate the frozen v44 package at Top 10 and pool 100 on all 40 questions.
Require exact Top-10 prefixes, identical input bindings, zero query errors,
byte-identical artifacts, and 100% exact evidence. Replace the v43 row rather
than counting two versions of the same expert.

## Consequences

- V44 reaches 84.97% Recall@10, 92.08% MRR@10, and 83.47% nDCG@10 on all 40
  questions, moving the expert from position 10 to position 3 of 24.
- The all-40 nDCG@10 gain over v43 is 1.70 percentage points; the q031-q040
  gain is 10.39 points.
- Selected P95 latency rises from 229.86 ms to 568.22 ms because the helper
  executes the additional immutable classical rankers.
- The agreement-gated archive member remains useful when a no-development-case-
  regression objective is more important than the final 0.10 nDCG point.
- The ranking is retrospective because both search and final evaluation use
  previously exposed questions. A newly registered, untouched cohort is
  required for formal promotion.
- This decision evaluates deterministic retrieval only. It does not assign a
  grounded answer-quality rank to the expert guidance.
