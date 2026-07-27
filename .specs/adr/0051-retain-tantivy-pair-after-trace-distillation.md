---
adr: "0051"
title: "ADR 0051: Retain the Tantivy Pair After Trace-Distillation Holdout Regressions"
summary: "Reject the IDF query and forward-four builder candidates after non-regressing Harbor holdout gates, retain the previously frozen pair, and confirm its canonical row by a complete replay."
status: "Accepted"
date: "2026-07-23"
product: "knowledge"
owner: "Platform Architecture"
area: "Semantic Knowledge Retrieval"
tags: [knowledge, okf, tantivy, harbor, trace-distillation, holdout]
---

# ADR 0051: Retain the Tantivy Pair After Trace-Distillation Holdout Regressions

## Status

Accepted. This extends ADR 0050 without changing its promoted consultation
candidate, retained builder, or experimental non-registry status.

## Context

ADR 0050 promoted the `identity-natural` Tantivy consultant and retained the
stable dedicated builder after a development-winning builder mutation
regressed holdout. A later trace-distillation round sought another improvement
in the same required order: query first, then builder with the accepted query
frozen.

Both stages used Harbor 0.18.0 schema-2 gates, one attempt per task, zero
retries, six independent development tasks, and four disjoint holdout tasks.
Every trial had to satisfy exact-evidence and mechanical-qualification rewards.
Promotion additionally required non-negative mean holdout gain, zero candidate
errors, and no task regression.

## Decision

Do not promote the IDF-weighted query candidate. It preserved every normalized
term, boosted at most twelve lowest-document-frequency terms from the immutable
lexicon, and left explicit Tantivy syntax unchanged. Development mean reward
improved from 0.851161 to 0.864072. Holdout mean improved from 0.852793 to
0.883546, but part 04 fell from 0.954375 to 0.952761. The non-compensating
no-regression gate therefore returned `keep-baseline`.

Keep the previously promoted query frozen at realizer digest
`sha256:8c3666ede3281b96a8630321d9c2fb91d015da96469003ecf22643e041b6f7e7`
for the builder stage.

Do not promote the `forward-four` builder candidate. It retained all paper and
semantic-claim records while replacing single-page paper passages with exact
overlapping forward windows of up to four page regions. Its sealed Harbor skill
digest was
`sha256:0fccf4555edea1fadbe0530262030b15f183f6e696acd6e32dba17225b848a5d`.
It improved all six development tasks and raised their mean reward from
0.851161 to 0.866492. On holdout, parts 01 and 02 improved, but part 03 fell by
0.222829 and part 04 fell by 0.006287. Mean reward fell from 0.852793 to
0.831703, so the gate returned `keep-baseline`.

Retain the stable checked `build-semantic-okf-tantivy` implementation and the
existing canonical direct-retrieval row. Two new 890-file builds of the retained
builder were byte-identical to each other and to the frozen bundle. A complete
40-question Top-10 run, exact replay, and pool-100 run reproduced 80.74%
Recall@10, 93.75% MRR@10, and 81.05% nDCG@10 across all questions; 92.17%,
90.00%, and 80.54% on the hard cohort; 100% exact evidence validity; identical
ranked Top-10 results; and an identical pool-100 Top-10 prefix.

## Consequences

The live query and builder remain the best candidates that satisfy the strict
non-regression contract. Positive aggregate gains cannot hide a task-specific
loss, and a development-wide improvement cannot justify promotion after an
untouched holdout decline.

The query and builder candidates remain append-only experimental evidence. A
future mutation may use their development traces, but it must not tune against
these now-observed holdout tasks. Another promotion attempt requires a new
prospective holdout cohort.

The canonical comparison table remains unchanged because the published pair
did not change and its complete replay reproduced the checked metrics exactly.
