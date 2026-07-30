---
adr: "0080"
title: "ADR 0080: Establish a Paper-Grounded Knowledge Methodology Review"
summary: "Adopt a version-pinned research corpus, a snapshot-bound expert skill, and a read-only restricted agent for evidence-backed reviews of repository knowledge methodology."
status: "Accepted"
date: "2026-07-29"
product: "knowledge"
owner: "Platform Architecture"
area: "Knowledge Methodology"
tags: [knowledge, research, papers, evaluation, skills, agents, reproducibility]
---

# ADR 0080: Establish a Paper-Grounded Knowledge Methodology Review

## Status

Accepted.

## Context

The repository has mature controls for Semantic OKF construction, consultation,
evaluation isolation, skill evolution, artifact sealing, and holdout release.
It also contains many retrieval and graph variants whose design choices are
informed by research but were not previously reviewed against one shared,
version-pinned cross-methodology paper corpus.

General model memory or ad hoc web searches cannot provide a repeatable
evidence boundary. A reviewer that can also mutate the implementation risks
mixing diagnosis, selection, and implementation authority.

## Decision

Adopt `knowledge-methodology-papers-47` as the first immutable research
snapshot for methodology review.

- Pin every paper to an exact arXiv version and preserve PDF and derived
  Markdown SHA-256 bindings.
- Reuse the fifteen canonical GraphRAG paper extractions rather than create a
  second independent copy.
- Organize the 47 papers into eight declared coverage lanes and preserve the
  curated selection limitations.
- Build and validate one Semantic OKF snapshot with a deterministic manifest,
  source-combination decision, ledger, RDF, ontology, SHACL, and provenance.
- Package the snapshot with reviewed application guidance as the standalone
  `review-knowledge-methodology` expert skill.
- Define `knowledge-methodology-reviewer` as a read-only project agent whose
  default and allowed skill lists contain only that standalone expert.
- Keep research acquisition, methodology review, and implementation as
  separate authority stages.
- Publish audits with exact concept paths, versioned paper identities, PDF
  pages, claim labels, limitations, priorities, and falsifiable validation
  plans.
- Refresh by publishing a new immutable corpus version and superseding audit;
  never silently replace paper versions or rewrite old review evidence.

The local agent manifest is a repository contract, not a claim that a hosted
Workspace Agent has been provisioned.

## Consequences

Positive:

- methodology recommendations are reproducible and page-grounded;
- the reviewer cannot silently rely on unrelated skills or external sources;
- repository practices can be recognized as supported, challenged, or left as
  open questions without conflating those outcomes;
- future paper updates and audit changes have an explicit provenance boundary.

Negative:

- the corpus is curated and arXiv-centered rather than exhaustive;
- complete paper text increases repository artifact size;
- PDF text extraction preserves page identity but may degrade layout;
- a useful recommendation still requires repository-specific experiments
  before implementation or promotion.

## Evaluation

Acceptance requires:

1. 47 unique exact paper versions and all eight coverage lanes;
2. complete inventory, PDF, Markdown, manifest, and concept bindings;
3. passing OKF, RDF, SHACL, provenance, and coherence validation;
4. an identical independent rebuild of the snapshot;
5. a validated and deterministic standalone expert skill;
6. an agent allowlist containing only the expert skill;
7. a human-readable and machine-readable paper-grounded audit; and
8. repository tests plus the standard application coverage gate.
