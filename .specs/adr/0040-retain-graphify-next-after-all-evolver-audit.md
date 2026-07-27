---
adr: "0040"
title: "ADR 0040: Retain Graphify Next After the All-Evolver Audit"
summary: "Keep the capped reciprocal-reference candidate unchanged because every additional compatible mutation was neutral or regressive and the only label-enrichment candidate broke the unchanged consultation contract."
status: "Accepted"
date: "2026-07-20"
product: "knowledge"
owner: "Platform Architecture"
area: "Semantic Knowledge Retrieval"
tags: [knowledge, okf, graphify, harbor, evolution, pareto]
---

# ADR 0040: Retain Graphify Next After the All-Evolver Audit

## Status

Accepted. This extends ADR 0039 and keeps both official skills unchanged.

## Context

The frozen `build-semantic-okf-graphify-next` candidate improves retrospective
Astro retrieval with capped reciprocal documentation references, but those
references do not occur in the GraphRAG papers corpus. A second evolution pass
therefore applied every available Harbor evolution contract and searched for a
compatible cross-dataset mutation while preserving
`consult-semantic-okf-graphify` byte-for-byte.

## Decision

Retain the current next candidate without further mutation. Treat it as the
sole non-dominated candidate in this pass:

- It improves Astro Recall@10 and nDCG@10 over the official control.
- It emits exactly the official GraphRAG graph, establishing no regression but
  no improvement on that corpus.
- Sparse same-paper, cross-paper dimension, and reciprocal dimension edges are
  neutral on the 24-question GraphRAG discovery cohort.
- Root-label and semantic-anchor projections regress GraphRAG discovery.
- Projecting related-paper titles into temporary views is source-grounded, but
  changes view digests and is rejected by the unchanged consultant.

Do not merge neutral, regressive, or contract-incompatible mutations merely to
combine outputs from multiple evolution engines.

## Harbor evolution boundaries

The completed q032 Harbor job installs only the consultation skill and contains
one unique task. Its retrieval metrics pass, while response and evidence
contract gates fail. It cannot provide causal builder credit, satisfy the
two-task trace-distillation minimum, or justify retry as an external failure.

GEPA is limited to `SKILL.md` mutation and would optimize the wrong installed
skill for this builder-only request. Population search, reflective Pareto
search, and operator coevolution require one SHA-bound candidate skill per
native Harbor job, while the canonical build-consult mode installs a builder
and consultant together. Metaskill evolution requires a producer-published
append-only policy ledger that is absent here. Each engine therefore fails
closed at its declared boundary.

The candidate-realization engine did run end to end: it prepared, sealed,
validated, and verified the related-paper-title candidate. That seal records a
valid mutation realization, not a promotion; the unchanged consultant then
rejected the candidate's regenerated view digests.

## Consequences

`build-semantic-okf-graphify-next` remains the ADR 0039 implementation with
Astro logical graph SHA-256
`ab17730bb536da30c6c20c74bdc80c6c9d86e09a8171ace687ed92e97224587a`.
On GraphRAG it emits 10,797 nodes and 13,504 edges with logical SHA-256
`9d3574cee7b42825d9b72e1a1526c31ed24aa127f8041be86bb33d12ad9b632`,
identical to the official builder.

Future evolution needs either a fresh prospective dataset, a canonical
builder-only Harbor task with one installed candidate skill, or an explicitly
versioned consultation contract that permits additional view labels.
