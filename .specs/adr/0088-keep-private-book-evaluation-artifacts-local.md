# ADR 0088: Keep private book evaluation artifacts local

- Status: Accepted
- Date: 2026-07-30

## Context

The user supplied a private Google Drive folder containing eighteen commercial
software-engineering books. Each PDF carries a distribution restriction. A
useful evaluation needs exact source bytes, page-level text, a processed
Semantic OKF snapshot, questions, and evidence locators, but committing the
source or extracted prose would redistribute protected material. Registering a
descriptor that requires ignored files in the canonical public dataset
registry would also make clean-checkout validation fail.

## Decision

Create `software-architecture-books-40` as a local-private evaluation study
under `evaluations/software-architecture-books/`.

- Keep `raw/`, `processed/`, `generated/`, and `results/` ignored.
- Version only the selection contract with source hashes, deterministic
  preparation and evaluation scripts, the Semantic OKF manifest and plans,
  paraphrased questions and adjudications, exact hash-only evidence locators,
  aggregate reports, and documentation.
- Represent every book as a separate logical source in one bundle. This
  preserves book authority and evidence identity while accepting one atomic
  local release boundary.
- Build exact PDF-page passages with the classical Semantic OKF projection and
  deep-validate the snapshot before evaluation.
- Compare the frozen `bm25`, `topic`, `association`, and `fusion` routes at
  Top-10 using duplicate-safe book identities. Report Recall, MRR, nDCG, full
  qrel coverage, reviewed-locator recall, and P95 latency.
- Treat qrels as non-exhaustive focus sets and keep the benchmark out of
  supervised profile construction. The study evaluates retrieval, not answer
  synthesis.
- Generate any Semantic OKF dataset descriptor and Harbor task trees only
  under ignored local paths. Do not add this private corpus to the canonical
  checked descriptor registry.

## Consequences

A permitted local user can reproduce the corpus by staging the exact PDFs and
running the checked scripts. A clean public checkout retains the evaluation
contract but cannot reconstruct protected source text without separately
authorized access.

Aggregate metrics and hash-only evidence remain reviewable without exposing
book passages. Harbor task generation can be rehearsed locally, but raw task
trees, model responses, and full evidence stay private. Any future public
release requires a separate licensing review and a new decision record.
