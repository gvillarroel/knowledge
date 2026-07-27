---
adr: "0053"
title: "ADR 0053: Promote the Tantivy Long-Record Overview Builder"
summary: "Reject a query mutation on the canonical hard cohort, freeze the retained consultant, and promote an exact long-record overview builder after prospective Astro and canonical gates."
status: "Accepted"
date: "2026-07-23"
product: "knowledge"
owner: "Platform Architecture"
area: "Semantic Knowledge Retrieval"
tags: [knowledge, okf, tantivy, harbor, trace-distillation, holdout]
---

# ADR 0053: Promote the Tantivy Long-Record Overview Builder

## Status

Accepted. This extends ADR 0051. The consultant and experimental non-registry
status remain unchanged; the dedicated builder changes.

## Context

A second prospective round used the untouched Astro registry rather than the
previously observed GraphRAG evolution holdout. Query development used the 24
`train` questions and query holdout used the eight `dev` questions. Builder
development used `train`; builder holdout used the eight `holdout` questions.

Every Harbor 0.18.0 schema-2 job used one attempt, zero retries, exact evidence
and mechanical qualification gates, lock-verified skill identity, and disjoint
holdout tasks. The builder tasks embedded the exact frozen consultant.

## Decision

Reject the lexicon-backed inflection query candidate despite its Astro holdout
gain from `0.787847` to `0.807445`. Its complete GraphRAG replay regressed the
hard cohort from 92.17% to 90.17% Recall@10, from 90.00% to 85.00% MRR@10,
and from 80.54% to 78.03% nDCG@10. Restore and freeze consultant digest
`sha256:896d038b16dd974411ef50bf91e5efead5e2589262058114b4bed4d8993f0c84`.

Promote the builder candidate with digest
`sha256:5223046d8c1fcc4d4d7cc4cf138e9182a67ac92f970d4bf05bcf39ba50c9e1a8`.
It retains the complete non-paper record and adds at most one exact overview
from the body start to the first level-two heading when the record has at least
10,000 characters. PDF-page passage behavior is unchanged.

The builder passed 6/6 candidate-development trials and raised reward from
`0.832638` to `0.853740`. On the disjoint holdout it raised reward from
`0.927071` to `0.927305`; one task was unchanged, one improved, and no cell
regressed.

Two canonical builds were byte-identical. The complete Top-10, replay, and
pool-100 evaluation reproduced the existing quality row: 80.74% Recall@10,
93.75% MRR@10, and 81.05% nDCG@10 overall; 92.17%, 90.00%, and 80.54% on the
hard cohort; 100% evidence validity and deterministic rankings.

## Consequences

The builder gains a deterministic exact-overview passage for long non-paper
records while preserving the authoritative ledger, full records, plan, frozen
consumer, and exact locator contract.

The general canonical quality table is stable. Its P95 diagnostic is refreshed
to 90.92 ms from the latest replay, but timing remains operational rather than
an SLA comparison.

Future query work must use a new prospective cohort and must retain the
GraphRAG hard-cohort regression gate. The observed Astro and GraphRAG tasks from
this round are no longer eligible as untouched holdout evidence.
