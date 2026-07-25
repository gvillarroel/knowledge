---
adr: "0058"
title: "ADR 0058: Separate Focus Coverage from Semantic Relevance"
summary: "Treat GraphRAG focus-paper sets as non-exhaustive, gate the public document minimum on exact valid evidence, and require complete question coverage plus semantic review for semantic ranking."
status: "Accepted"
date: "2026-07-24"
product: "knowledge"
owner: "Platform Architecture"
area: "Semantic Knowledge Evaluation"
tags: [knowledge, okf, graphrag, harbor, evaluation, qrels, semantic-review]
---

# ADR 0058: Separate Focus Coverage from Semantic Relevance

## Status

Accepted. This refines ADR 0034, ADR 0035, and the interpretation of the
mechanical evidence used by ADR 0057.

## Context

The `graphrag-papers-40` benchmark contains 40 questions, but the v36
trace-distillation decision cited only 18 responses. A full archive inventory
found 175 individually reviewable responses across recent raw Harbor results
and a preserved historical manual review. Those responses cover only 29 of 40
questions, and 97 of 143 recent raw responses are repetitions of q002-q004.

Manual semantic review also found that the existing paper qrels act as curated
focus sets rather than exhaustive relevance judgments. Valid, on-topic evidence
from papers outside a focus list was common. The grader nevertheless used only
focus-set overlap to satisfy the public instruction's minimum number of
independent relevant papers. This forced mechanically valid q005 and q020
answers to zero despite six and seven exact independent evidence documents,
respectively.

The deterministic grader can establish evidence identity and focus coverage,
but it cannot establish claim entailment, required-point coverage, or semantic
relevance merely from document identity.

## Decision

Version the GraphRAG dataset evaluation contract as 1.1 and declare its qrels
to be `non-exhaustive-focus-set`.

For newly generated tasks:

1. Count only documents backed by exact valid evidence toward the public
   minimum-document gate.
2. Report focus-document coverage and its threshold diagnostic separately.
3. Keep focus coverage in the mechanical retrieval utility, but label the
   reward as mechanical contract and focus coverage only.
4. Mark every non-null cross-document or hard-question answer as requiring
   semantic review before semantic ranking.
5. Require at least one complete response for every q001-q040 question before
   describing an evaluation as full-dataset coverage.
6. Preserve strict response, evidence, and first-use-order qualification as
   non-compensating release checks.

## Consequences

Valid off-focus evidence no longer causes a minimum-document false negative.
On the corrected contract, the cited q005 baseline changes from reward
`0.000000` to `0.701818`, and q020 changes from `0.000000` to `0.590008`.
Both remain semantically partial and ineligible for semantic ranking until
review.

Malformed outputs do not gain eligibility: the q004 first-use-order failure and
the q025 locator-contract failure remain zero.

Historical result artifacts and their original scores remain immutable. A
rescore must state that it uses the version 1.1 policy. Future promotion reports
must distinguish trials, complete responses, unique payloads, covered questions,
focus coverage, release qualification, and semantic adjudication.
