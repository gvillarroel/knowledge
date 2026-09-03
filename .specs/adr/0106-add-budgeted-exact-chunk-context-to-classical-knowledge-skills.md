---
adr: "0106"
title: "ADR 0106: Add Budgeted Exact-Chunk Context to Classical Knowledge Skills"
summary: "Create an additive classical generator that retains the complete immutable knowledge tree while answering through budgeted, linked, exact ledger chunks."
status: "Accepted"
date: "2026-08-14"
product: "knowledge"
owner: "Platform Architecture"
area: "Semantic OKF Expert Skills"
tags: [knowledge, semantic-okf, classical-retrieval, chunking, token-efficiency, skills]
---

# ADR 0106: Add Budgeted Exact-Chunk Context to Classical Knowledge Skills

## Status

Accepted as an additive generator and deterministic context projection. This
decision does not promote the candidate on semantic answer quality.

## Context

The integrated classical expert preserves exact evidence and strong retrieval,
but its normal search payload can place large passage texts, topic vectors,
scores, expansions, and repeated metadata into model context. This is especially
expensive for research papers and large source files. Removing the authoritative
knowledge, replacing it with summaries, or changing classical retrieval would
repeat strategies that previously reduced tokens while failing semantic quality.

Chunking alone is not sufficient. Fixed-width chunks can sever headings and
local arguments; embedding-dependent chunkers add models and nondeterminism;
and novelty-only selection can prefer irrelevant vocabulary. Published evidence
also cautions that more complex semantic chunking does not automatically beat
simpler structure-aware methods. MMR provides the useful relevance-versus-
redundancy pattern, while recent retrieval work supports bounded adaptive
expansion instead of loading whole documents.

## Decision

- Add `skills/build-classical-chunked-knowledge-skill/`. Do not modify or
  overwrite `skills/build-classical-knowledge-skill/`.
- Build the complete authoritative Semantic OKF core and unchanged classical
  projection under `references/knowledge/`. Require byte equality with the
  separately generated classical knowledge tree and runtime parity with the
  accepted classical consultant.
- Add a derived metadata-only projection under `references/context/`. Store no
  copied evidence text there. Each chunk binds one document and ledger record,
  exact record-relative character bounds, SHA-256 digests, heading ancestry,
  term counts, a conservative token estimate, and previous/next chunk links.
- Split deterministically at Markdown structural boundaries. Split an oversized
  structural unit safely without overlap. Target 360 estimated tokens, cap one
  chunk at 720, and preserve every exact character exactly once within its
  structural unit.
- Hydrate each chosen chunk from the authoritative ledger at query time and
  recheck its digest. Emit its physical citation, packed-record anchor when
  applicable, and exact character locator.
- Keep the original `bm25`, `topic`, `association`, and `fusion` routes. Run the
  unchanged classical route internally to obtain candidate documents, but do
  not send that complete discovery payload into model context.
- Select under a closed 6,000-token default budget and 12,000-token maximum.
  First reserve distinct evidence identities, then repair uncovered retrievable
  query facets by weighted coverage per token, and finally apply a cost-aware
  MMR pass using relevance, parent rank, evidence diversity, linked continuity,
  and a bounded Jensen-Shannon redundancy penalty. Return no more than 48
  chunks.
- Use Jensen-Shannon similarity rather than raw cross-entropy. Cross-entropy is
  directional, unbounded, and smoothing-sensitive; Jensen-Shannon similarity is
  symmetric and bounded. Treat it only as a redundancy signal, never as a
  relevance score.
- Report an explicit quality guard for retrievable-query coverage and distinct
  evidence identities. On failure, allow one maximum-budget retry, targeted
  linked-neighbor hydration, and finally the original full search or exact
  record lookup as a fail-closed diagnostic path.
- Measure output with the larger of lexical token count and UTF-8 bytes divided
  by four. Label this as a deterministic proxy, never as provider-native or
  billed tokens.

## Deterministic validation evidence

The frozen candidate was compared retrospectively with the unchanged integrated
classical experts on all 120 disclosed questions from `graphrag-papers-40`,
`astro-40`, and `quantum-error-correction-papers-40`, using the normal `fusion`
route.

| Gate | Result |
|---|---:|
| Full classical retrieval parity | 120/120 |
| Default quality-guard pass | 120/120 |
| Exact chunks reconstructed and rehashed | 1,951/1,951 |
| Provider-visible UTF-8 byte reduction | 80.42% |
| Deterministic estimated-token reduction | 83.34% |

Per-dataset estimated-token reductions were 60.19% for GraphRAG, 91.85% for
Astro, and 65.52% for quantum error correction. The complete machine-readable
result and interpretation boundary are retained in
[`20260814-classical-chunked-context-efficiency.md`](../../evaluations/semantic-okf-datasets/reports/20260814-classical-chunked-context-efficiency.md)
and its adjacent JSON report.

This regression proves unchanged retrieval, exact evidence reconstruction,
guard behavior, and payload reduction. Because the questions are disclosed and
the token estimator is not a provider tokenizer, it does not prove semantic
answer equivalence or native token billing. Any promotion claim still requires a
new digest-locked development/validation study and a one-way independent
semantic gate.

## Alternatives considered

### Replace full knowledge with summaries

Rejected. Summaries are lossy derived claims and can hallucinate or omit the
exact evidence needed for difficult synthesis. The full immutable tree remains
the authority.

### Use fixed-size overlapping chunks

Rejected as the default. Overlap repeats tokens and can inflate apparent
evidence diversity. Structural non-overlapping chunks plus explicit neighbor
links preserve continuity without duplicating every boundary.

### Use embeddings or model-based semantic breakpoints

Deferred. They add model, dependency, and reproducibility requirements, and
current evidence does not justify making them mandatory for this deterministic
classical path.

### Use raw cross-entropy to select non-overlapping information

Rejected. Vocabulary difference is not evidence relevance, and raw
cross-entropy has unsuitable directionality, range, and unseen-term behavior.

### Modify the existing classical generator in place

Rejected. The accepted baseline is retained for compatibility, exact comparison,
and fail-closed fallback. The new behavior is opt-in through a separate skill.

## Consequences

Positive:

- model context normally contains only exact question-relevant spans and compact
  citation metadata;
- authoritative knowledge and classical retrieval remain byte- and rank-stable;
- local context can expand through verified links without overlapping every
  chunk;
- deterministic guards expose insufficient coverage instead of silently
  presenting a small payload as complete;
- the generated expert remains portable, read-only, and model-independent.

Negative:

- generated skills carry an additional metadata index and selector runtime;
- chunk selection adds local CPU work before consultation;
- a difficult guard failure can deliberately fall back to a larger payload;
- deterministic regression cannot replace independent semantic answer review.

## Research basis

- Carbonell and Goldstein, [The Use of MMR, Diversity-Based Reranking for
  Reordering Documents and Producing Summaries](https://aclanthology.org/X98-1025/).
- Weeratunga et al., [Late Chunking: Contextual Chunk Embeddings Using Long-
  Context Embedding Models](https://arxiv.org/abs/2409.04701).
- [SCAR: Selective Context-Aware Retrieval for Long-Document Question
  Answering](https://arxiv.org/abs/2606.16661).
- [Evaluating Chunking Strategies for Retrieval](https://arxiv.org/abs/2607.01852).
