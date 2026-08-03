# ADR 0086: Recommend quality-first and balanced retrieval skill groups

## Status

Accepted as provisional operational guidance on 2026-07-30.

## Context

ADR 0085 ranked twenty-five frozen direct-retrieval strategies on sixty
evaluation-only questions. The result identifies a quality winner, but an
operational choice must also account for P95 latency, evidence validity, and
ranking stability. Selecting one strategy solely by latency would choose
legacy lexical retrieval and sacrifice ranking quality; selecting solely by
nDCG would ignore a useful fivefold speed difference.

Builder and consultation skills must remain matched treatments. The evaluation
did not test a query-level cascade, cross-family fusion, or one shared bundle
served by multiple consultants.

## Decision

Document two recommended operational profiles:

- **Quality-first, fully measured:** `build-semantic-okf-classical` plus
  `consult-semantic-okf-classical` in `association` mode.
- **Balanced runtime, measured:** `consult-semantic-okf-tantivy` over the
  frozen validated classical projection used by the evaluation.

For new construction, use `build-semantic-okf-tantivy` as the intended matched
builder candidate, but do not attribute the measured holdout result to that
builder. The holdout evaluated the Tantivy consultant against a pre-existing
classical-builder-lineage bundle and did not rebuild the Tantivy-specific
builder.

The quality-first rule maximizes nDCG@10, then MRR@10, Recall@10, and lower
P95. The balanced rule minimizes P95 after requiring:

- 100% exact evidence validity;
- 100% query-ranking stability;
- at least 95% nDCG@10; and
- at least 95% Recall@10.

Under those rules, classical association reaches 99.60% nDCG@10, 100% MRR and
Recall, and 664.65 ms P95. Tantivy reaches 96.25% nDCG, 96.25% MRR, 100%
Recall, and 128.27 ms P95. Tantivy is 5.18 times faster and reduces P95 by
80.70% for a 3.35-point nDCG trade-off.

Retain the Tika/MALLET matched pair in `fusion` mode only as an experimental
ultra-fast option under a 90% nDCG and 95% Recall floor. Do not recommend it as
the general default because it loses a further 4.97 nDCG points relative to
Tantivy and depends on preview Tika software.

This is a post-evaluation operational recommendation, not a formal promotion.
Do not use the evaluation-only questions, qrels, rankings, or diagnostics to
tune, fuse, cascade, repair, or evolve any candidate.

## Consequences

- Latency-sensitive workloads have a clear provisional runtime default in the
  measured Tantivy consultation route.
- A fresh Tantivy matched pair remains a candidate requiring validation on a
  different sealed cohort.
- Quality-constrained workloads have a clear matched classical association
  pair.
- A deployment may expose both profiles as workload-level choices, but no
  measured claim is made for automatic per-query routing between them.
- Classical fusion, adaptive fusion, ensemble robust, and classical topic are
  dominated by classical association on the measured nDCG/P95 plane.
- v51 is excluded from operational recommendation because its evaluation-only
  nDCG is 41.03% and its ranking stability is 43.33%.
- A production default change requires a new sealed cohort and the
  `harbor-organize-evaluations` plus `harbor-run-results` governance path.
- The recommendation covers direct retrieval only, not generated-answer
  correctness, unseen-corpus transfer, build time, storage, or token cost.
