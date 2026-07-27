---
adr: "0061"
title: "ADR 0061: Reaudit Every GraphRAG Reference Answer Independently"
summary: "Run a second independent question-level audit over the complete historical response archive and replace fourteen reference answers with more precisely grounded versions."
status: "Accepted"
date: "2026-07-24"
product: "knowledge"
owner: "Platform Architecture"
area: "Semantic Knowledge Evaluation"
tags: [knowledge, okf, graphrag, harbor, evaluation, reference-answers, audit]
---

# ADR 0061: Reaudit Every GraphRAG Reference Answer Independently

## Status

Accepted. This refines the curated reference-answer decision in ADR 0059
without changing the empirical-coverage boundary in ADRs 0058 and 0060.

## Context

The first complete collection satisfied the strict response, evidence,
document-minimum, semantic-checklist, and hard-anchor contracts. Those
mechanical gates do not establish that every phrase is the narrowest claim
supported by its cited records or that every material statement cites the
specific record that supports it.

A second independent assignment reviewed each q001-q040 question using its
complete context: every one of the 175 locally reviewable historical
responses, the current curated answer, all authored semantic targets, the
native evidence ledger and source-combination crosswalk, and the frozen source
corpus when needed. Questions q028 and q031-q040 had no historical complete
response and were reviewed directly against their full rubric or hard ground
truth.

## Decision

Retain 26 reference answers and replace the following 14:

- q009, q010, q012, q015, q021;
- q026, q027, q028, q029, q030, q031;
- q036, q037, q040.

The replacements correct unsupported or overly broad statements, exact metric
attribution, inference-versus-measurement boundaries, and claim-level evidence
indices. They preserve all 200 semantic targets and all 94 hard evidence
anchors. The q030 replacement adds one exact evidence row; the other
replacements retain their prior evidence cardinality.

Pin the regenerated forty-answer collection in dataset contract 1.2 and
preserve the full audit in:

- `reports/20260724-graphrag-papers-40-second-pass-review.json`;
- `reports/20260724-graphrag-papers-40-second-pass-review.md`.

Recalculate the current metrics table against the new reference collection
without changing any immutable historical trial or making a new evaluation
model call.

## Consequences

Every final answer has two independent question-level judgments. The final
collection still covers 175 historical responses, 200 semantic targets, and 94
hard anchors, and all forty answers pass exact response, evidence identity,
first-use order, document-minimum, and hard-anchor validation.

The second pass is curated evaluator work, not a live Harbor campaign. It does
not repair the eleven questions missing empirical responses, change the 29 of
40 empirical coverage result, or make the historical campaign rankable.
