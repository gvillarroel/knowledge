---
adr: "0050"
title: "ADR 0050: Promote the Tantivy Consultant and Retain the Dedicated Builder Baseline"
summary: "Promote the identity-diversified Tantivy consultant after disjoint holdout, freeze it, and reject the development-winning builder mutation after its holdout regression."
status: "Accepted"
date: "2026-07-23"
product: "knowledge"
owner: "Platform Architecture"
area: "Semantic Knowledge Retrieval"
tags: [knowledge, okf, tantivy, harbor, evolution, holdout]
---

# ADR 0050: Promote the Tantivy Consultant and Retain the Dedicated Builder Baseline

## Status

Accepted. This supersedes the implementation and measurement conclusions in
ADRs 0043, 0046, and 0048 without changing their historical evidence. Tantivy
remains an experimental comparator outside the canonical eight-family Harbor
registry.

## Context

The earlier Tantivy candidate used a validated Classical snapshot but repeated
passages from the same paper in its first ten results. Its complete direct row
reached only 34.64% all-40 Recall@10. The requested evolution had two ordered
stages: improve consultation first, freeze it, and only then optimize a
dedicated builder against that exact consumer.

The evaluation therefore used deterministic development and untouched holdout
cohorts. Candidate rewards combined Recall@10, MRR@10, and nDCG@10 under exact
evidence and mechanical-qualification gates. Promotion required complete
evaluation, no errors, non-negative mean gain, and no holdout task regression.

## Decision

Promote the `identity-natural` consultation candidate. It caps results by
paper-or-source identity and normalizes syntax-free natural questions against
the persisted unigram lexicon while preserving explicit Tantivy syntax.
Development mean reward improved from 0.548310 to 0.851161. On the disjoint
holdout it improved from 0.558400 to 0.852793 with zero regressed tasks. Freeze
the promoted consultation tree at realizer digest
`sha256:8c3666ede3281b96a8630321d9c2fb91d015da96469003ecf22643e041b6f7e7`.

Ship `build-semantic-okf-tantivy` as a standalone dedicated builder. It owns
its entry points, implementation modules, dependency locks, references,
validation, and atomic publication. Its stable construction semantics reproduce
the accepted Classical GraphRAG authoritative core across all 884 files.
Preserve the builder's explicit UTF-8 LF serialization so clean builds remain
byte-identical across supported hosts. The six derived `classical/` files
differ bytewise from the local CRLF campaign snapshot: four data artifacts are
equal after newline normalization, while the index and build report bind the
regenerated LF hashes.

Do not promote the development-winning `papers-forward-3` builder mutation.
With the consultation tree frozen, it improved development mean reward from
0.851161 to 0.868570, and both population and Pareto selection chose it. Its
holdout reward then fell from the stable builder's 0.852793 to 0.812123. The
single aggregate holdout task regressed, so the promotion gate correctly
returned `retain-stable-dedicated-baseline`.

Report the resulting dedicated pair in the canonical direct-retrieval table:
80.74% all-40 Recall@10, 93.75% MRR@10, 81.05% nDCG@10, 92.17% hard-10
Recall@10, 90.00% hard-10 MRR@10, 80.54% hard-10 nDCG@10, 100% exact evidence
validity, and 96.73 ms P95 query time. Exact replay and the pool-100 Top-10
prefix gate pass.

## Evolution-engine audit

Every applicable evolution contract was evaluated:

- candidate realization sealed the baseline and four builder candidates;
- native population search ranked five complete development jobs;
- reflective Pareto search independently retained `papers-forward-3`;
- trace distillation emitted no proposal because the evidence did not support a
  further mutation;
- operator coevolution failed closed when the aggregate task identifier could
  not bind to its local task contract;
- external-failure resume rejected the interrupted pre-terminal job rather than
  fabricating a terminal result;
- GEPA was not run because its `SKILL.md`-only mutation surface cannot change
  the runtime script directly invoked by this Oracle task; and
- metaskill evolution was not run because this evaluation has no
  producer-published typed policy ledger to replay.

Engine participation does not override promotion gates. Unsupported,
non-causal, incomplete, or holdout-regressive outputs receive no promotion
credit.

## Consequences

The promoted consultant materially improves direct retrieval coverage and
nDCG while retaining native Tantivy execution, exact evidence identities, and
read-only behavior. The dedicated builder makes ownership and future evolution
explicit without changing accepted bundle bytes.

The builder search also demonstrates development overfitting: its best local
mutation regressed the disjoint holdout. Future builder work must start from
the retained stable baseline, preserve the frozen-consumer protocol, and use a
new prospective cohort before reconsidering that mutation family. Grounded
answer behavior and registry admission remain separate decisions.
