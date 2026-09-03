# Budgeted Context Projection

## Contents

- [Purpose](#purpose)
- [Chunk contract](#chunk-contract)
- [Selection contract](#selection-contract)
- [Why not raw cross-entropy](#why-not-raw-cross-entropy)
- [Quality and fallback](#quality-and-fallback)

## Purpose

The context projection reduces provider-visible evidence without changing the
authoritative Semantic OKF ledger or the accepted classical ranking. The
runtime may scan the complete local projection, but it emits only a bounded set
of exact evidence spans to the model.

## Chunk contract

`references/context/chunks.jsonl` contains metadata only. It never duplicates
the authoritative body text. Each row binds one exact non-overlapping range by:

- classical `document_id` and authoritative `(source_id, record_id)`;
- authoritative `record_sha256`;
- exact record-relative start and end characters;
- SHA-256 of the exact range;
- deterministic token estimate and lexical counts;
- Markdown heading ancestry; and
- explicit previous and next chunk identities inside the same passage.

Chunking prefers Markdown headings, paragraphs, lists, tables, and fenced code
boundaries. An indivisible oversize block is split at the latest safe newline,
sentence, or whitespace boundary that fits. Chunks never overlap; continuity is
recovered through verified neighbor links instead of paying for duplicated
context on every query.

The built-in plan targets 360 estimated tokens and caps ordinary chunks at 720.
The estimator is the larger of lexical-token count and UTF-8 bytes divided by
four. It is a deterministic conservative proxy, not a claim about a provider's
private tokenizer.

## Selection contract

The `context` operation first runs the unchanged classical route internally.
The complete retrieval payload does not enter model context. It then selects
chunks from those ranked passages under a closed token budget.

Selection combines:

- normalized query and expansion relevance;
- new coverage of retrievable query terms;
- the unchanged parent-passage rank;
- new evidence-identity coverage;
- continuity for a sufficiently relevant linked neighbor; and
- a redundancy penalty based on bounded Jensen-Shannon similarity.

Utility is divided by a configurable token-cost exponent. Before the general
greedy pass, the selector reserves one best-fitting chunk from each of the
highest-ranked distinct evidence identities up to the declared minimum. This
prevents a short-document cluster from winning only because it is cheap.

It then repairs uncovered retrievable query facets by selecting the strongest
new weighted coverage per token, with relevance and parent rank as stable
tie-breakers. Only after the coverage threshold is reachable does the general
MMR pass optimize the remaining budget. Redundancy maxima are maintained
incrementally, so selection scales linearly with the number of chosen chunks
rather than recomputing every chosen-pair comparison on every pass.

The default emitted budget is 6,000 estimated tokens, including conservative
bundle and per-chunk metadata allowances. The hard supported maximum is 12,000,
and no more than 48 chunks may be returned even when structural units are small.

## Why not raw cross-entropy

Raw cross-entropy is directional, unbounded, and can reward a chunk merely for
using a different vocabulary even when it is irrelevant. It also needs an
arbitrary smoothing rule for unseen terms. The projection instead uses
query-conditioned relevance and coverage for usefulness, then applies
Jensen-Shannon similarity only as a symmetric bounded redundancy signal. This
keeps novelty subordinate to evidence relevance.

## Quality and fallback

The selector reports weighted retrievable-query coverage and distinct evidence
identity coverage. A bundle is complete only when both frozen thresholds pass.
When it is incomplete, rerun once with the reported maximum budget or hydrate a
named linked neighbor. Use the original full `search` or exact-record `get`
only as a diagnostic fallback. Never infer that a small bundle proves the
absence of evidence outside the selected spans.

Every emitted chunk is rehydrated from `semantic/records.jsonl` and rehashed at
query time. The generated skill remains read-only and creates no cache or
sidecar.
