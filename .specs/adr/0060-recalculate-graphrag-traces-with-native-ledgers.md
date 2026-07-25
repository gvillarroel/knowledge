---
adr: "0060"
title: "ADR 0060: Recalculate GraphRAG Traces with Native Ledgers"
summary: "Apply the current evaluation policy to immutable traces while validating exact evidence against each trial's native ledger and reporting curated references only as calibration."
status: "Accepted"
date: "2026-07-24"
product: "knowledge"
owner: "Platform Architecture"
area: "Semantic Knowledge Evaluation"
tags: [knowledge, okf, graphrag, harbor, evaluation, rescore, metrics]
---

# ADR 0060: Recalculate GraphRAG Traces with Native Ledgers

## Status

Accepted. This operationalizes the evaluator corrections in ADR 0058 and the
reference-answer boundary in ADR 0059.

## Context

The preserved local GraphRAG archive contains 180 raw Harbor trials produced by
several Semantic OKF families and candidate revisions. Those families represent
the same authoritative papers with different exact record identities, source
paths, and locators. Rescoring every response against the legacy reference
ledger therefore invalidates otherwise exact candidate evidence.

The current evaluation contract also differs from the stored historical
metrics. Contract 1.2 treats qrels as non-exhaustive focus sets, gates the public
document minimum on exact valid evidence documents, and keeps semantic review
separate from mechanical reward.

The pinned reference-answer collection exposed an additional strict-contract
issue during calibration: recursively sorting JSON keys changed the required
top-level response member order even though the answer content remained intact.

## Decision

Recalculate preserved raw trials without changing their append-only result
artifacts.

For each trial:

1. use the current question, qrels, public minimum, evaluation policy, semantic
   rubric, and hard ground truth;
2. validate evidence against the exact native ledger and source-combination
   crosswalk bound to that trial;
3. emit diagnostics schema 3.0 and retain the original metrics beside the
   recalculated metrics;
4. preserve provider, agent, response-contract, mechanical, and semantic states
   as separate fields; and
5. exclude historical rows from recalculation when their raw response bodies
   are absent.

Score the forty curated reference answers through the same current grader as a
calibration check, but never count them as live trials or empirical coverage.

Preserve strict JSON member order when serializing a reference response and
make dataset validation reject a pinned collection that loses that order.

## Consequences

All 180 locally preserved raw trials can be evaluated under one current policy
without falsely rejecting family-specific evidence identities. The resulting
table reports 99 current mechanical qualification passes. Among 174 trials with
comparable stored rewards, 46 increase, none decrease, and 128 remain
unchanged.

The recalculation does not repair empirical coverage. Only 29 of 40 questions
have an individually reviewable live response, and the full-dataset empirical
claim remains ineligible.

All forty curated references now pass the exact current response and mechanical
qualification contracts. Their scores validate the evaluator surface only;
they remain separate from model-performance evidence.
