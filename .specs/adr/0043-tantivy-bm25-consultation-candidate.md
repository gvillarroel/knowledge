---
adr: "0043"
title: "ADR 0043: Add a Tantivy BM25 Consultation Candidate"
summary: "Clone the classical read-only consultation boundary into a standalone candidate that rebuilds a filtered in-memory Tantivy index and preserves exact Semantic OKF evidence bindings."
status: "Accepted"
date: "2026-07-22"
product: "knowledge"
owner: "Platform Architecture"
area: "Semantic Knowledge Retrieval"
tags:
  - knowledge
  - okf
  - tantivy
  - rust
  - bm25
  - retrieval
  - skills
---

# ADR 0043: Add a Tantivy BM25 Consultation Candidate

## Status

Accepted.

This decision extends ADR 0019 without modifying the accepted classical build and consultation skills, the canonical eight-family Harbor registry, or historical evaluation artifacts.

## Context

The classical consultant computes field-aware Okapi BM25 in Python from the persisted `classical/lexicon.json` statistics. Tantivy is a Rust full-text search engine with native BM25 ranking, a mature query parser, phrase queries, and small startup overhead suitable for command-line use. A separate candidate is needed to exercise that engine directly without changing the frozen classical implementation or claiming metric equivalence before evaluation.

The request is limited to consultation. Persisting a Tantivy index would introduce a new build artifact, schema, refresh lifecycle, atomic publication boundary, and builder authority. Those concerns are unnecessary for an initial read-only candidate because the validated classical projection already contains exact title and passage text with authoritative ledger locators.

## Decision

Ship `consult-semantic-okf-tantivy` as a standalone read-only skill.

Pin the official `tantivy==0.26.0` Python binding, which executes the Rust Tantivy engine. Fail with an explicit diagnostic when that exact package version is unavailable; do not substitute a Python BM25 implementation, a search server, or another binding.

Consume an existing validated classical Semantic OKF snapshot. Validate the closed classical artifact set, authoritative core binding, plan digest, artifact hashes and counts, passing build report, document identities, safe concept paths, exact record or character-range locators, and text hashes before search. Keep the classical projection and Semantic OKF core immutable.

For each request:

1. apply source, concept, and concept-type filters to the validated passage set;
2. create a pathless in-memory Tantivy index containing only the filtered passages;
3. index `title` and `body` with Tantivy's default analyzer and positional term frequencies;
4. parse the bounded query over those two fields with regular expressions disabled;
5. use Tantivy's native BM25 scorer with classical title/body weights as field boosts; and
6. return stable ranking metadata plus every authoritative evidence identity and locator.

Require the classical plan's `k1=1.2` and `b=0.75` values because they match the Tantivy/Lucene defaults exposed by the pinned binding. Reject other values instead of claiming a parameter setting that the binding does not expose. Tantivy tokenization and scoring remain a distinct candidate and need not reproduce the Python classical ordering.

Do not create a persistent Tantivy index, cache, sidecar, or builder skill in this decision. Do not add the candidate to the canonical Harbor family registry until separate retrieval, evidence-validity, determinism, latency, and grounded-answer evaluation supports promotion.

## Consequences

Positive:

- consultation exercises Tantivy's native Rust BM25 implementation directly;
- phrase and Boolean queries are available without a hosted service or model;
- pre-ranking filters reduce the in-memory corpus and make the authority boundary visible;
- no derived file is written into or beside the published snapshot; and
- exact record, concept, locator, and text-hash evidence remains available for grounded answers.

Negative:

- the native index is rebuilt for every process invocation;
- installation needs a compatible wheel or a Rust/native compiler toolchain;
- Tantivy's analyzer differs from the persisted classical tokenizer, so ranking parity is not implied;
- the Python binding does not expose arbitrary BM25 `k1` and `b` configuration for this path; and
- promotion claims require a fresh isolated evaluation rather than reuse of classical metrics.
