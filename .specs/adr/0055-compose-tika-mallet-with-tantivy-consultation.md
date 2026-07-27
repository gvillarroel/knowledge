---
adr: "0055"
title: "ADR 0055: Compose Tika and MALLET Snapshots with Tantivy Consultation"
summary: "Add one standalone read-only skill that validates Tika/MALLET snapshots and combines native Tantivy BM25 with MALLET topic and PPMI discovery signals."
status: "Accepted"
date: "2026-07-23"
product: "knowledge"
owner: "Platform Architecture"
area: "Semantic Knowledge Retrieval"
tags: [knowledge, okf, tika, mallet, tantivy, bm25, retrieval]
---

# ADR 0055: Compose Tika and MALLET Snapshots with Tantivy Consultation

## Status

Accepted. This extends ADRs 0044, 0050, and 0054 without changing either
existing skill pair, their evaluation results, or their experimental registry
status.

## Context

The Tika/MALLET experiment provides hash-bound heterogeneous extraction,
fixed-seed Java MALLET topics, PPMI associations, and exact Semantic OKF
evidence. The promoted Tantivy consultant provides native Rust BM25, syntax-aware
natural-query normalization, pre-index filtering, pathless in-memory indexes,
and bounded evidence-identity diversity.

A single new skill was requested that uses Tika, MALLET, and Tantivy. The
repository's durable lifecycle boundary prohibits combining write-capable
extraction with read-only answering in one skill. Reusing a sibling consultant
at runtime would also violate the standalone package contract.

## Decision

Ship `consult-semantic-okf-tika-mallet-tantivy` as an independent read-only
skill. Copy the required validation and query implementation into its package;
do not import or execute either existing sibling skill.

Require a validated Tika `4.0.0-beta-1` receipt and Java MALLET `2.1.0`
projection. Pin the official `tantivy==0.26.0` Python binding and require the
snapshot's `k1=1.2` and `b=0.75` plan. Apply filters before building one
pathless in-memory index and pass title and body weights as Tantivy field
boosts.

Expose four explicit modes:

- `tantivy` for native lexical BM25;
- `association` for Tantivy queries expanded by persisted PPMI neighbors;
- `topic` for Tantivy queries expanded by persisted MALLET vocabulary and
  blended with document-topic cosine; and
- `fusion` for reciprocal-rank fusion of those three rankings.

Preserve explicit Tantivy syntax, disable regex queries, normalize syntax-free
text against persisted unigrams, disclose each parsed component query, and
retain exact evidence identities and locators. Treat every retrieval signal as
non-authoritative and require factual verification in Semantic OKF authority
layers.

Do not persist Tantivy state, re-extract sources, retrain during ordinary
consultation, repair a bundle, or claim retrieval-quality promotion. Optional
deep validation may retrain the exact bound MALLET model only in temporary
storage outside the snapshot.

## Consequences

Positive:

- heterogeneous Tika ingestion, probabilistic MALLET topics, and native Tantivy
  ranking can be exercised through one portable skill;
- filters, engine identity, expansions, scores, evidence, and read-only behavior
  remain inspectable;
- the existing builder and consultants remain unchanged; and
- the authoritative OKF evidence boundary is preserved.

Negative:

- the package duplicates validation code to remain standalone;
- ordinary consultation now requires both PyYAML and the pinned native Tantivy
  wheel;
- native BM25 defaults constrain eligible Tika/MALLET retrieval plans; and
- retrieval and grounded-answer quality remain unknown until a separate
  prospective evaluation is completed.
