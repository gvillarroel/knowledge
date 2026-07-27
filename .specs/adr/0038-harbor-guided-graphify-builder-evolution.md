---
adr: "0038"
title: "ADR 0038: Add Reciprocal Cross-Partition Similarity to the Graphify Builder"
summary: "Keep Graphify consultation frozen while adding a deterministic ledger-derived bridge graph to a standalone builder."
status: "Accepted"
date: "2026-07-20"
product: "knowledge"
owner: "Platform Architecture"
area: "Semantic Knowledge Retrieval"
tags: [knowledge, okf, graphify, harbor, builder, skills]
---

# ADR 0038: Add Reciprocal Cross-Partition Similarity to the Graphify Builder

## Status

Accepted. This extends ADRs 0030 and 0037 without changing the consultation package selected by ADR 0037.

## Context

The original Graphify projection produces one disconnected structural subgraph per record when the source ledger has no reviewed object relationships. The unchanged consultation runtime can score those subgraphs, but its bounded BFS cannot discover complementary records across them.

Harbor-style discovery trials rejected two lexical-label variants and three unrestricted nearest-neighbor variants. Long labels did not improve recall and increased latency. Unrestricted similarity links improved some aggregate metrics but displaced hard-question evidence through dense hubs.

## Decision

Add `build-semantic-okf-harbor-graphify` as an independently named builder. Preserve the authoritative Semantic OKF core, Graphify temporary-view contract, original node labels, index schema, runtime pin, and `consult-semantic-okf-graphify` package.

After structural extraction, identify exactly one generated record root per ledger record. Derive binary TF-IDF vectors from authoritative title, record ID, concept type, and body. Derive record-ID partitions from the first segment after the corpus-wide common prefix. Publish a similarity edge only when two roots are reciprocal nearest neighbors in different partitions; use unrestricted reciprocal neighbors only for a single-partition corpus.

Treat every similarity edge as non-authoritative discovery state. Regenerate roots, partitions, TF-IDF scores, and the complete similarity edge set from `records.jsonl` during validation. Reject missing, extra, or changed edges.

Freeze the builder after 32 discovery questions and open the eight-question holdout once. Promote the builder for Graphify retrieval only when the unchanged consult validates the bundle, evidence validity remains perfect, discovery hard metrics do not regress, and sealed holdout ranking improves. Do not claim that this makes the original consultation package Harbor-contract-ready.

## Consequences

The final projection adds 30 reciprocal bridge edges to the 6,389 original edges while preserving all 6,390 nodes and the exact authoritative core. On the full 40-question benchmark, Recall@10 improves from 68.5% to 77.3% and hard Recall@10 from 45.8% to 57.5%, with 301/301 evidence rows valid.

The paired q032 Harbor trace does not pass the response contract for either bundle because the frozen consult does not expose the grader's required locator and retained-text hash shape. Builder promotion therefore applies to deterministic retrieval quality, not to strict Harbor answer compilation.
