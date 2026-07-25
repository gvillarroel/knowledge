---
adr: "0059"
title: "ADR 0059: Pin Curated Reference Answers for All GraphRAG Questions"
summary: "Version the GraphRAG dataset contract to 1.2 and pin forty independently reviewed, evidence-valid reference answers without treating them as live evaluation trials."
status: "Accepted"
date: "2026-07-24"
product: "knowledge"
owner: "Platform Architecture"
area: "Semantic Knowledge Evaluation"
tags: [knowledge, okf, graphrag, harbor, evaluation, reference-answers]
---

# ADR 0059: Pin Curated Reference Answers for All GraphRAG Questions

## Status

Accepted. This extends the semantic-review and full-dataset-coverage separation
established by ADR 0058.

## Context

The `graphrag-papers-40` dataset had authored semantic rubrics for q001-q030
and hard ground truth for q031-q040, but it did not contain a complete
human-readable reference answer collection. The preserved evaluation archive
contained 175 individually reviewable responses covering only 29 questions.
Most were partial, q028 had no complete response, and q031-q040 had no live
complete response.

A question-level review assigned all forty questions to agents with the exact
question, full rubric or hard ground truth, every available historical
response, and the frozen evidence ledger. The collaboration runtime allowed 34
producing agent threads; after its thread cap was reached, two active agents
performed the final six assignments sequentially with separate contexts,
outputs, checklists, and validations.

The resulting collection covers 200 authored semantic targets with 243
supported claims and 408 exact evidence rows. The ten hard answers cover all 94
authoritative evidence anchors.

## Decision

Version the GraphRAG dataset descriptor as
`semantic-okf-evaluation-dataset/1.2` and require a hash-pinned
`reference_answers` artifact.

The pinned collection must:

1. contain exactly one non-null reference answer for every q001-q040 question;
2. preserve question order and identity;
3. account for each available historical response exactly once within its
   question-level review;
4. include a complete semantic checklist for every required point, hard answer
   claim, derivation, and important negative;
5. pass exact response-contract, evidence-identity, first-use-order, document
   minimum, and hard-anchor validation; and
6. state that it is curated evaluator material rather than live model
   evidence.

Schema 1.0 continues to forbid evaluation policy and reference answers. Schema
1.1 requires the evaluation policy but forbids reference answers. Schema 1.2
requires both.

## Consequences

Evaluators and maintainers now have a complete, evidence-backed expected-answer
surface for all forty questions. Missing live responses can no longer be
mistaken for missing expected answers.

The collection does not repair historical campaign coverage, create model
trials, or make a partial campaign rankable. Full-dataset empirical claims
still require complete live responses for all forty questions under ADR 0058.

Any change to a pinned reference answer requires regeneration, full collection
validation, a new SHA-256 binding in the dataset descriptor, and review of the
affected semantic target.
