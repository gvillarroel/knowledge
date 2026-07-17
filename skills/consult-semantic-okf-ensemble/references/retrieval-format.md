# Retrieval Snapshot Contract

## Contents

1. Authority boundary
2. Root artifacts
3. Index contract
4. Chunk and embedding rows
5. Digest bindings
6. Failure policy

## 1. Authority boundary

The `retrieval/` tree is a derived, non-authoritative discovery projection. The accepted Semantic OKF truth remains in the ledger, concept Markdown, and purpose-selected RDF graphs. Rebuilding retrieval artifacts must not change record identity or ontology meaning.

## 2. Root artifacts

An embedding-enabled snapshot contains:

```text
BUNDLE/
  concepts/
  semantic/
    build-report.json
    semantic-plan.json
    source-manifest.json
    records.jsonl
    data.ttl
    ontology.ttl
    provenance.ttl
    shapes.ttl
    validation-report.ttl
  retrieval/
    index.json
    chunks.jsonl
    embeddings.jsonl
    build-report.json
```

The four files shown under `retrieval/` are the exact closed artifact set. Every entry must be a regular non-symlink file. The retrieval report must equal a live reconstruction of the index/core/selection bindings, selected-record and vector counts, dimension, and raw index/chunk/embedding hashes. The baseline refuses unknown files, symlinks, path traversal, missing required artifacts, duplicate JSON keys, non-finite JSON numbers, and blank JSONL rows.

## 3. Index contract

`retrieval/index.json` is a closed schema with these top-level members:

- `schema_version`: `"1.0"`;
- `authoritative`: `false`;
- `core`: pre-retrieval tree digest, raw ledger digest, and record count;
- `retrieval_plan_sha256`: reviewed plan digest;
- `selection`: requested, eligible, and excluded source IDs plus selected physical-source count and digest;
- `chunking`: implementation, strategy, buffer size, and breakpoint percentile;
- `embedding`: allowlisted provider, exact model and revision, dimension, normalization, vector precision, cosine metric, and document/query encoding routes;
- `artifacts`: fixed chunk and embedding paths, raw hashes, and counts;
- `chunk_count` and `embedding_count`.

Hashing v1 is exactly `provider=hashing`, `model_id=knowledge-hashing-embedding`, and `revision=1`. The other allowlisted provider is `sentence-transformers`, which requires a valid Hugging Face `namespace/repository` ID, an immutable hexadecimal revision, and a locally available snapshot at that exact commit.

## 4. Chunk and embedding rows

Every `chunks.jsonl` row contains exactly:

```text
chunk_id, source_id, record_id, concept_id, concept_path,
record_sha256, source_path, locator, ordinal, text, text_sha256
```

Rows are strictly ordered by unique `chunk_id`. Record chunking requires exactly `{"kind":"record"}` and exact equality with a nonempty authoritative ledger body. Semantic chunking requires exactly `{"kind":"character-range","start":N,"end":N}` and an exact substring match. Every eligible record has at least one chunk, and no ineligible or unknown record may have one. Buffer size is bounded to 1-16.

`chunk_id` is `chunk-` plus the first 32 hexadecimal characters of the canonical SHA-256 over `source_id`, `record_id`, `record_sha256`, `ordinal`, and `text_sha256`.

Every `embeddings.jsonl` row contains exactly `chunk_id` and `vector`. Its ordered chunk IDs equal the chunk file exactly. Vectors have the declared dimension, finite numeric values, nonzero norm, and—when requested—unit norm within the tolerance implied by declared decimal precision.

## 5. Digest bindings

- Artifact hashes cover raw file bytes.
- `core.records_sha256` covers raw `semantic/records.jsonl` bytes.
- `core.tree_sha256` hashes canonical JSON rows `{path, sha256}` for every core file before `retrieval/` is added.
- `selection.input_sha256` hashes sorted canonical rows `{source_id, content_sha256}` from the eligible entries in `semantic/source-manifest.json`.
- Every chunk repeats the authoritative record digest and exact concept path.

In ensemble schema `2.0`, consultation also exposes the chunk's persisted
`record_sha256` in every route hit and resolves it only through the ensemble identity
crosswalk. A shared record ID or source path is never sufficient for a join.

This graph is acyclic: the retrieval index binds the already complete core, while the core digest excludes `retrieval/`.

## 6. Failure policy

Missing optional model code or weights is a provider-availability condition and can produce an explicitly authorized lexical fallback. A malformed or stale declared retrieval artifact is a bundle-integrity failure and always stops consultation. Never hide corruption by searching the ledger instead.
