---
adr: "0017"
title: "ADR 0017: Add Embedding-Derived Retrieval to Semantic OKF"
summary: "Keep Semantic OKF records and graphs authoritative while adding a hash-bound, optional embedding retrieval projection through a separate build and consultation skill pair."
status: "Accepted"
date: "2026-07-13"
product: "knowledge"
owner: "Platform Architecture"
area: "Semantic Knowledge Retrieval"
tags:
  - knowledge
  - okf
  - embeddings
  - llamaindex
  - retrieval
---

# ADR 0017: Add Embedding-Derived Retrieval to Semantic OKF

## Status

Accepted.

This decision extends ADR 0008, ADR 0010, ADR 0012, and ADR 0014 without changing the
existing deterministic Semantic OKF build or consultation contracts.

## Context

The existing Semantic OKF snapshot exposes exact records, concept Markdown, RDF graphs,
provenance, and validation evidence. These layers preserve reviewed semantic identity and are
appropriate for exact filters, reading, joins, aggregation, and lineage. They do not provide a
general semantic-discovery surface for paraphrases or conceptually related passages.

Embedding models and libraries such as LlamaIndex can create useful retrieval units and rank
them by similarity. Their output is model-, revision-, and threshold-dependent. Treating each
chunk as a new OKF record or RDF entity would therefore make semantic identity change whenever
the retrieval configuration changes. Implicit model downloads or LlamaIndex defaults would also
make an otherwise local build depend on mutable network state; in particular, a semantic
splitter without an explicit embedding model may select a hosted default.

The prior GraphRAG corpus provides a pinned comparison surface. Its requested corpus contains
fifteen paper Markdown files and fifteen reviewed-claim JSONL files. Its complete Semantic OKF
manifest also contains one required shared vocabulary file, so a parity build processes thirty
requested files through thirty declarations plus the same auxiliary declaration.

## Decision

Ship two additional standalone skills:

1. `build-semantic-okf-embeddings` owns creation and validation of an embedding-enabled
   snapshot.
2. `consult-semantic-okf-embeddings` owns read-only inspection and lexical, vector, or hybrid
   discovery over that snapshot.

The existing `build-semantic-okf` and `consult-semantic-okf` packages remain the deterministic
baseline and historical comparison surface. The new packages do not import or execute their
siblings; they contain every required baseline script, validator, reference, and dependency
declaration inside their own directories.

An embedding-enabled build first materializes the unchanged authoritative Semantic OKF core:
concepts, `records.jsonl`, data, ontology, provenance, shapes, and validation results. It then
adds a derived retrieval projection under `retrieval/`:

- `chunks.jsonl` contains deterministic retrieval units bound to the source record digest,
  concept path, source path, ordinal, and locator;
- `embeddings.jsonl` contains one finite, normalized vector per chunk in the same canonical
  order;
- `index.json` fixes the provider, model identifier, immutable revision, dimensionality,
  metric, query/document encoding contract, chunking implementation and thresholds, eligible
  and excluded records, input inventory, core record digest, and artifact hashes; and
- `build-report.json` records validation and summary metrics without becoming domain evidence.

Chunks remain derived retrieval units. They are not automatically added to `records.jsonl`,
the OKF concept tree, or RDF graphs. A future workflow that wants chunk entities must declare
and review their domain meaning separately.

The portable baseline uses a deterministic local hashing embedder and native splitter. Optional
Sentence Transformers and LlamaIndex backends are permitted only through package-local optional
requirements and a closed provider/implementation allowlist. Model selection is explicit. A
Sentence Transformers plan requires a Hugging Face repository ID and immutable revision. The
provider resolves that exact revision from the preloaded local cache in offline mode, verifies the
resolved snapshot directory has the requested revision leaf, and passes only that local directory
to the CPU model loader. No builder or consultant may select a hosted provider, download weights,
trust remote code, accept an arbitrary local model path, or create a cache implicitly. Model
weights and caches are explicit user-supplied inputs.

Consultation treats the retrieval projection as discovery only:

- use the record ledger for exact identifiers, attributes, filters, and counts;
- use lexical, vector, or hybrid retrieval for candidate discovery;
- open the exact concept Markdown and locator before using a hit as evidence; and
- use explicitly selected RDF graphs for joins, aggregation, schema, or lineage.

Vector search uses an exact local cosine scan for the portable contract. Hybrid search combines
independent lexical and vector ranks with deterministic reciprocal-rank fusion; it does not add
incommensurate raw scores. Filters apply before ranking and ties resolve by chunk ID. Optional
ANN indexes are disposable accelerators outside the authoritative snapshot and must bind to the
published index digest.

An explicit vector request fails when the exact provider or model is unavailable unless the
caller opts into a declared lexical fallback. Automatic mode may fall back and must report the
reason. A declared but corrupt, stale, non-finite, dimensionally invalid, or hash-mismatched
index is a bundle error and never falls back silently. Consultation must not modify the bundle,
download a model, or write cache state.

The implementation comparison uses the same thirty requested GraphRAG files and the required
auxiliary vocabulary. It records both input-set digests and compares four retrieval paths:
legacy lexical discovery, new lexical discovery, vector discovery, and hybrid discovery. The
report includes core semantic parity, input coverage, artifact size and timing, Recall at fixed
cutoffs, MRR, nDCG, and evidence validity against the authoritative ledger, identities, text hash,
concept path, and exact locator. Reproducible runs create append-only local directories with
runtime, tool, model, command, timing, log, deterministic-tree, and report fingerprints.

## Consequences

Positive:

- paraphrase and conceptual discovery become available without changing reviewed semantic
  identity;
- model, revision, chunking, source coverage, and every retrieval artifact are auditable;
- the deterministic Semantic OKF baseline and all historical results remain reproducible;
- the new build and consultation authorities remain separated and independently installable;
- exact scans and JSONL artifacts avoid database locks, journals, pickle, and platform-specific
  index formats for the supported baseline; and
- the four-path comparison can distinguish chunking gains from embedding and fusion gains.

Negative:

- an embedding-enabled snapshot stores duplicated passage text and vectors;
- high-quality local models add installation, model-weight, memory, and runtime costs;
- exact vector scans do not scale indefinitely and may require a separately governed
  accelerator for large releases;
- duplicated baseline Semantic OKF code must be kept compatible across standalone packages; and
- retrieval scores are discovery signals, so agents must still open authoritative concepts and
  verify locators before answering.
