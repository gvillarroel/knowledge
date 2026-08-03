# ADR 0085: Rank the exhaustive frozen strategy table on evaluation-only questions

## Status

Accepted on 2026-07-30.

## Context

ADR 0084 reserved sixty new questions for evaluation-only ranking, but its
first execution compared seven specialized-expert strategies. The repository's
general historical comparison contains twenty-five direct-retrieval
alternatives across lexical, vector, topic, association, entity-graph,
adaptive, ensemble, Tantivy, Tika/MALLET, Rust/MALLET, and specialized-expert
families. A general table needs to compare that complete pre-existing
population under one untouched question contract without using the outcome to
change any candidate.

Graphify and Turso artifacts do not expose a compatible authoritative-paper
Top-10 retrieval route. Including either by inventing a projection after
holdout release would change the frozen population and the metric contract.

## Decision

Freeze all twenty-five rows from the pre-existing general comparison before
running `graphrag-papers-parallel-eval-60-v1`.

- Evaluate the same sixty questions at Top 10 with authoritative-paper
  identity, reviewed binary qrels, exact evidence validation, and three
  independent repetitions.
- Rank by nDCG@10, then MRR@10, Recall@10, representative P95 latency, and
  stable strategy ID.
- Require complete queries, zero route errors, valid evidence, and identical
  paper-ranking stability to be measured and disclosed across repetitions.
- Retain non-deterministic frozen strategies in the exhaustive table using
  median retrieval metrics rather than hiding their instability.
- Publish one aggregate twenty-five-row table and retain query-level evidence
  in the private study area.
- Keep Graphify and Turso outside the ranked table until a compatible route is
  designed and frozen against a different evaluation-only dataset version.
- Treat latency as diagnostic because setup and runtime boundaries differ by
  strategy family.

The evaluation-only questions, qrels, rankings, and diagnostics remain
forbidden inputs to construction, evolution, trace distillation, candidate
repair, or subsequent selection.

## Consequences

- The general table compares every previously published compatible
  direct-retrieval strategy under one unseen-question boundary.
- No strategy may be altered in response to this result and then reevaluated
  on the same dataset as a promotion candidate.
- Historical runtime projections may be assembled from frozen artifacts when
  their route-local ledgers validate; any core-parity exception must be
  disclosed in the private evidence and publication limitations.
- The ranking estimates same-corpus unseen-question retrieval generalization.
  It does not measure generated-answer quality or unseen-corpus transfer.
