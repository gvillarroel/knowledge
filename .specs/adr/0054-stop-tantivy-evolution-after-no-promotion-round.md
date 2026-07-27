---
adr: "0054"
title: "ADR 0054: Stop Tantivy Evolution After a No-Promotion Round"
summary: "Reject an endocrine query candidate on a holdout cell regression and an interpretation-passage builder on canonical GraphRAG regression, retaining both live skills."
status: "Accepted"
date: "2026-07-23"
product: "knowledge"
owner: "Platform Architecture"
area: "Semantic Knowledge Retrieval"
tags: [knowledge, okf, tantivy, harbor, trace-distillation, holdout]
---

# ADR 0054: Stop Tantivy Evolution After a No-Promotion Round

## Status

Accepted. This extends ADR 0053 and records the requested stopping condition.

## Context

A third prospective round used the previously unused endocrine-hygiene
benchmark. Twenty questions formed discovery and candidate development, five
cross-paper questions formed the query holdout, and five hard questions formed
the builder holdout. All three cohorts were disjoint.

Harbor 0.18.0 schema-2 jobs used one attempt, zero retries, exact evidence and
mechanical qualification gates, canonical skill locks, and a frozen consultant
inside every builder task. One host-interrupted query discovery job was
preserved but excluded; a new complete job supplied all accepted discovery
evidence.

## Decision

Reject the bounded concept-type query seed. It improved development reward from
`0.788357` to `0.862557` and holdout mean from `0.681789` to `0.697527`, but one
holdout cell regressed by `0.011854`. Retain consultant digest
`sha256:896d038b16dd974411ef50bf91e5efead5e2589262058114b4bed4d8993f0c84`.

Reject the exact structured-interpretation builder despite its endocrine
development and hard-holdout gains. Its two canonical GraphRAG builds were
byte-identical and its complete deterministic evaluation had no errors or
invalid evidence, but hard-10 Recall@10 regressed from 92.17% to 83.17%, MRR
from 90.00% to 88.33%, and nDCG from 80.54% to 77.43%. Retain builder digest
`sha256:8a5024734f62d4b53fe55b6b6f569d831513429460c0de8783ae1b47584de40a`.

Because this complete query-then-builder round promoted neither candidate, stop
the repeated evolution loop. Do not change the live skills or the canonical
comparison table.

## Consequences

The retained experimental Tantivy row remains 80.74% Recall@10, 93.75% MRR@10,
and 81.05% nDCG@10 overall; 92.17%, 90.00%, and 80.54% on hard-10.

The endocrine cohorts and all GraphRAG canonical results from this round are
observed evidence and cannot be reused as untouched holdout in future work.
Further evolution requires a new explicit request and a new prospective
holdout.
