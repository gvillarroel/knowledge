# ADR 0078: Integrate profile forging and freeze a QEC transfer benchmark

## Status

Accepted on 2026-07-28.

## Context

ADR 0077 established that supervised lexical profiles could make the
GraphRAG and Astro experts highly effective on fixed, fully exposed workloads.
That implementation lived in evaluation-specific scripts and custom adapter
files. Reproducing the technique for a new domain therefore required copying
evaluation machinery instead of invoking the expert builder through one
explicit contract.

The prior datasets could not show whether the technique transferred to new
source bytes. A separate domain, corpus, question set, and immutable knowledge
snapshot were required. Because every new question would be used to construct
the profile, the transfer result would still be retrospective and could not
support promotion.

## Decision

Extend `build-specialized-skill` with one builder-owned
`retrospective-supervised-ngram` mode.

- Preserve manifest schema `semantic-okf-expert-skill/1.0` for default and
  custom-adapter experts.
- Use `semantic-okf-expert-skill/1.1` only when the integrated profile is
  selected.
- Require a frozen dataset ID, exact question JSONL, qrel key, identity mode,
  and `--acknowledge-exposed-qrels`.
- Support exact ledger `source-id` and exact versioned `arxiv-id` identity
  modes.
- Learn one-to-five-token features without storing question text, answers, or
  an exact-question lookup.
- Bind the question bytes, complete ledger, profile artifact, identity
  contract, and no-holdout disclosure by SHA-256.
- Keep an authoritative lexical fallback, deduplicate the declared primary
  identity, return only exact immutable ledger records, and set
  `promotion_eligible: false`.
- Reject attempts to combine the integrated mode with a custom query template
  or support files.

Freeze `quantum-error-correction-papers-40` as the cross-domain transfer
benchmark:

- fifteen exact arXiv versions and PDF digests;
- deterministic page-by-page Markdown extraction normalized to NFC;
- one independently validated fifteen-record Semantic OKF snapshot;
- thirty development and ten evidence-first hard questions;
- non-exhaustive focus qrels and reviewed semantic targets;
- separate `build-consult` and `consult-only` task trees; and
- verifier network disabled in the generated task contract.

Compare a default lexical expert and the integrated profile expert over all
forty questions for three replicates. Gate the profile on perfect Recall@10,
MRR@10, nDCG@10, and exact evidence; strict quality improvement over the
same-snapshot baseline; stable rankings; and a 250 ms maximum replicate P95.

## Consequences

- The high-performing fixed-workload technique is now reproducible through one
  public builder command instead of evaluation-local adapter assembly.
- Existing expert packages and their version-1 manifest contract remain
  unchanged.
- The QEC source acquisition, benchmark generation, snapshot build, and expert
  packaging are deterministic and digest-bound.
- Both Harbor modes pass all eighty mechanical qualification oracles and
  leakage checks. Redacted dry runs were inspected; no live Windows Harbor run
  was attempted.
- The candidate also passes the native Harbor retrieval grader on one
  development case and one hard case. The grader now accepts both four- and
  five-digit modern arXiv numbers after the dot, so older identifiers such as
  `1208.0928v2` remain canonical and evidence-valid.
- The integrated QEC candidate ranks first of two treatments with 100%
  Recall@10, MRR@10, nDCG@10, and exact evidence in all three replicates. Its
  representative P95 is 34.006 ms; the default baseline records 74.5833%,
  27.4018%, 36.6713%, and 123.550 ms respectively.
- These metrics establish fixed-workload retrieval transfer only. They do not
  establish semantic answer correctness, unseen-query behavior, or eligibility
  for promotion.
- A future promotion attempt must register new untouched questions, preserve a
  one-way holdout release, and evaluate the exact selected artifact without
  exposing those qrels during construction.
