---
adr: "0042"
title: "ADR 0042: Retain RustMallet as an Experimental Topic Candidate"
summary: "Keep the standalone RustMallet skill pair for reproducible experimentation without replacing the stronger classical topic-community default or expanding the canonical eight-family Harbor registry."
status: "Accepted"
date: "2026-07-22"
product: "knowledge"
owner: "Platform Architecture"
area: "Semantic Knowledge Retrieval"
tags:
  - knowledge
  - okf
  - rust-mallet
  - lda
  - retrieval
  - evaluation
---

# ADR 0042: Retain RustMallet as an Experimental Topic Candidate

## Status

Accepted.

This decision extends ADR 0019 and does not modify the accepted classical skill pair, the canonical eight-family dataset registry, or historical evaluation artifacts.

## Context

The classical Semantic OKF strategy uses deterministic weighted label propagation over a PPMI term graph. RustMallet provides a materially different topic signal: sparse Gibbs-sampled latent Dirichlet allocation with local Python bindings and no hosted model dependency. A direct candidate was needed to determine whether probabilistic topics improve cross-paper retrieval while preserving exact evidence traceability.

Changing the existing classical skills in place would destroy the frozen comparison. Adding the untested candidate to the canonical dual-mode Harbor registry would also expand every dataset descriptor, campaign matrix, scheduler invariant, and historical eight-family interpretation before retrieval merit had been established.

## Decision

Keep two additional standalone skills:

1. `build-semantic-okf-rust-mallet` duplicates the classical builder boundary and replaces only topic derivation with `pyrmallet==0.1.1` sparse-Gibbs LDA.
2. `consult-semantic-okf-rust-mallet` validates and searches the candidate read-only, including independent fixed-seed retraining for deep validation.

Retain the existing `classical/` artifact boundary so the candidate preserves the established exact-passage, lexicon, association, and evidence contracts. Bind the changed topic algorithm through the index identity `pyrmallet-0.1.1-sparse-gibbs-lda-v1` and a closed plan containing every sampler and vocabulary parameter. Invoke the native Rust API with an explicit ASCII-alphanumeric token regex; reject any vocabulary term that did not originate in the auditable pretokenized corpus and reject any document removed by vocabulary filtering.

Evaluate the candidate outside the canonical Harbor family registry against the frozen GraphRAG classical report. Require two byte-identical builds, independent deep validation, authoritative-core parity, shared-baseline parity, zero route errors, and exact evidence validity before comparing retrieval metrics.

Do not promote RustMallet to the canonical registry on the current evidence. The top-10 fusion route reduced all-40 paper recall@10 from 83.46% to 80.28% and hard-10 recall@10 from 95.50% to 86.00%. Pool-100 evaluation produced the same deltas. BM25 remained identical, showing that the regression is isolated to the changed topic-dependent ranking rather than the authoritative core or lexical statistics.

## Consequences

Positive:

- RustMallet can be studied through an independently installable, hash-bound skill pair;
- the experiment exercises the upstream Rust implementation rather than a substitute LDA library;
- fixed parameters and two-build equality make the observed candidate reproducible on the evaluated platform;
- exact evidence identity and authoritative source parity remain unchanged; and
- the canonical eight-family Harbor campaign remains comparable with its historical evidence.

Negative:

- the candidate adds a native wheel and NumPy dependency;
- deep validation retrains LDA and is slower than validating deterministic topic communities;
- fixed-seed reproducibility has been established on the evaluated Windows CPython 3.12 runtime, not across every platform; and
- the current topic, association, and fusion routes recover fewer relevant papers than the accepted classical baseline, especially on the hard cohort.
