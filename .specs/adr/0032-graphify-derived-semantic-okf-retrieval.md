---
adr: "0032"
title: "ADR 0032: Add a Derived Graphify Retrieval Projection to Semantic OKF"
summary: "Preserve Semantic OKF authority while adding a deterministic, hash-bound Graphify Markdown graph for read-only discovery and traversal."
status: "Accepted"
date: 2026-07-16
product: "knowledge"
owner: "Platform Architecture"
area: "Semantic Knowledge Retrieval"
tags:
  - knowledge
  - okf
  - graphify
  - graph
  - retrieval
  - skills
---

# ADR 0032: Add a Derived Graphify Retrieval Projection to Semantic OKF

## Status

Accepted.

This decision extends ADR 0004, ADR 0010, ADR 0012, ADR 0014, and ADR 0017 without replacing the file-backed, embedding-backed, or Turso-backed variants.

## Context

Semantic OKF already provides a deterministic ledger, readable concept Markdown, explicit RDF graphs, provenance, constraints, and validation evidence. Graphify 0.9.17 can extract headings and local Markdown links into a native node-link graph and run lexical scoring plus bounded graph traversal. That is useful for orientation and linked-neighborhood discovery, but its structural Markdown extractor does not index ordinary paragraph or bullet text.

The frozen GraphRAG corpus puts the most useful reviewed claim interpretation in normalized attributes and concept bullets. Directly scanning those concepts would therefore underrepresent the available evidence. Rewriting authoritative concepts to improve Graphify recall would break byte parity and make a retrieval-engine concern alter the knowledge contract. Running Graphify semantic extraction would introduce an LLM-dependent, non-deterministic authority ambiguity.

## Decision

Ship two additional standalone skills:

1. `build-semantic-okf-graphify` builds and validates the unchanged Semantic OKF core, creates deterministic temporary Markdown views from the ledger, runs Graphify structural extraction, publishes a canonical graph and closed index, and owns all lifecycle mutation.
2. `consult-semantic-okf-graphify` verifies the complete core/projection binding, performs read-only Graphify scoring and BFS discovery, then hydrates authoritative concepts before returning evidence.

The builder pins the `graphifyy` distribution to version 0.9.17. Temporary views place reviewed titles, types, identifiers, and scalar attributes in headings. It neutralizes Markdown structural punctuation in scalar values so those values cannot inject links; only reviewed attribute IRIs that match another record subject become local links. The builder runs no semantic LLM extraction and no clustering, rewrites temporary source metadata onto the corresponding authoritative concept identity, and verifies removal of all views and caches before publication.

The published projection is exactly `retrieval/graphify/graph.json` plus `retrieval/graphify/index.json`. The index records:

- the complete non-projection core artifact list and logical tree digest;
- the ledger digest and record count;
- Graphify distribution, version, and no-LLM mode;
- per-record source, identity, concept path, record digest, optional paper identity, and deterministic view digest;
- graph physical and logical digests plus node and edge counts.

Graphify remains non-authoritative. Exact identity and grouped aggregation use `semantic/records.jsonl`; full reading and citations use concept Markdown; semantic joins and provenance remain RDF responsibilities. Graphify labels, scores, and structural `references` edges are discovery evidence only.

Validation regenerates every temporary view in memory from the authoritative ledger and checks its digest, complete record and paper identity, and the corresponding projected node and link fields. Consultation rejects malformed closed schemas, unsafe paths, duplicate nodes, dangling endpoints, missing record coverage, orphans, and any hash drift, then hashes the complete published snapshot before and after every command. Search exposes deterministic structured seeds, scores, context nodes, traversal counts, and exact concept-file evidence locators; it omits Graphify's non-deterministically ordered native display text. The pinned private Graphify scoring and BFS primitives are a reviewed compatibility surface; runtime smoke fails when an upgrade removes or changes them.

## Alternatives considered

- **Rewrite authoritative concept Markdown for Graphify.** Rejected because it breaks core parity and lets a retrieval engine reshape factual artifacts.
- **Run Graphify semantic LLM extraction.** Rejected for the baseline because it adds network/model configuration, non-determinism, cost, and unclear evidence authority. It may be evaluated later as a separate ablation.
- **Parse Graphify CLI text.** Rejected in favor of pinned in-process scoring and traversal primitives plus structured concept hydration.
- **Treat Graphify as a replacement for RDF.** Rejected because Markdown references do not preserve reviewed predicate, graph, provenance, or SHACL semantics.
- **Publish temporary graph-ready views.** Rejected because they duplicate authoritative content and expand the immutable release surface without adding evidence authority.

## Consequences

The variant adds one sizeable graph artifact and a Graphify runtime dependency, and its build performs a second deterministic Markdown scan. It gains a bounded structural discovery path that can expose reviewed attributes and cross-record links without modifying the Semantic OKF core. Every result carries an authoritative concept path and digest, and corrupt or stale projections fail closed.

The comparison under `evaluations/semantic-okf-storage-versions/` must use the same frozen 31-source, 874-record corpus and existing 30 retrieval questions as the other versions, and it must freeze the historical baseline report by digest. Reports must distinguish fresh-process latency, authoritative ledger operations, and Graphify structural discovery quality. Evidence validity requires full ledger identity, recomputed normalized-record digest, ledger-derived paper identity, a safe exact concept-file locator, byte-identical returned content, and the exact authoritative ledger body.
