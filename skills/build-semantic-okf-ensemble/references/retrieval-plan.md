# Retrieval Plan and Projection Contract

## Authority boundary

The core Semantic OKF snapshot is authoritative. Retrieval chunks and embeddings are derived discovery aids. Never add a chunk to `semantic/records.jsonl`, concept Markdown, or RDF merely because a splitter emitted it.

## Closed plan

The plan root has exactly `schema_version`, `selection`, `chunking`, and `embedding`.

- `schema_version` is `"1.0"`.
- `selection.source_ids` is a non-empty, sorted, unique array of source IDs from the Semantic OKF manifest.
- `chunking.implementation` is `native` or `llamaindex`.
- `chunking.strategy` is `record` or `semantic`. LlamaIndex is valid only for semantic splitting.
- `chunking.buffer_size` is an integer from 1 through 16.
- `chunking.breakpoint_percentile_threshold` is finite and from 0 through 100.
- `embedding.provider` is `hashing` or `sentence-transformers`.
- `embedding.model_id`, `revision`, `dimension`, and `normalize` are mandatory.

The hashing identity is fixed to model ID `knowledge-hashing-embedding`, revision `1`. A SentenceTransformers model ID must be a Hugging Face `namespace/repository` identifier, not a local path, and its revision must be an immutable hexadecimal commit with 7 through 64 digits. Dimensions range from 1 through 4096. Normalization is an explicit boolean.

Unknown fields fail. Defaults are never inferred.

## Selected-input digest

The builder resolves selected IDs against `semantic/source-manifest.json`. It sorts eligible IDs and hashes canonical JSON for this array:

```json
[
  {"source_id": "claims-a", "content_sha256": "..."},
  {"source_id": "paper-a", "content_sha256": "..."}
]
```

Canonical JSON uses UTF-8, sorted object keys, no insignificant spaces, Unicode characters rather than ASCII escapes, and no non-finite values. `input_count` counts selected physical source declarations, not normalized records or chunks.

## Hashing embedding v1

Document and query encoding are symmetric:

1. Unicode-casefold the text and extract Python Unicode `\w+` tokens.
2. SHA-256 each token's UTF-8 bytes.
3. Select `int.from_bytes(digest[0:8], "big") % dimension`.
4. Add `+1` when `digest[8] & 1`, otherwise add `-1`.
5. If the text has no tokens or cancellation produces zero norm, hash `b"fallback\0" + text.encode("utf-8")`, select the same way, and set that bucket to `+1`.
6. Apply L2 normalization exactly when requested.
7. Round each component to eight decimal places; for normalized vectors, renormalize the rounded vector and round once more.

The index declares cosine similarity, symmetric query/document encoding, and `vector_precision: 8`. Unit norm is validated with relative and absolute tolerance `1e-6`.

## Native semantic splitting

The native splitter finds sentence boundaries after `.`, `!`, or `?`, and at blank lines. It creates an embedding window around each unit using the declared buffer size, computes cosine distance between adjacent windows, and breaks where distance is greater than the declared percentile. Source character ranges remain exact, and the final chunks preserve all interior source text.

Thresholds are corpus-dependent. Compare chunk counts and manually open representative locators before accepting a plan. A record with one unit remains one chunk.

## Retrieval rows

`chunks.jsonl` is sorted by `chunk_id`. Every row has exactly:

```text
chunk_id, source_id, record_id, concept_id, concept_path,
record_sha256, source_path, locator, ordinal, text, text_sha256
```

A record chunk locator is `{"kind":"record"}`. A semantic locator is `{"kind":"character-range","start":N,"end":M}` and must resolve to `record.body[N:M]` exactly.

`embeddings.jsonl` has exactly `chunk_id` and `vector`, in the same order and cardinality as chunks. JSON non-finite constants, booleans as numeric components, zero vectors, dimension drift, excessive precision, and orphan IDs fail validation.

## Atomicity and offline behavior

The builder creates the core and retrieval layers in a private sibling candidate. It independently validates the complete candidate and performs one final rename to a nonexistent output. Ordinary failures remove the candidate.

The builder resolves SentenceTransformers through `huggingface_hub.snapshot_download` with the exact repository ID, revision, and `local_files_only=True` while both Hugging Face and Transformers offline modes are forced. It verifies the returned snapshot directory name against the requested revision and passes only that resolved local path to SentenceTransformers with remote code disabled and CPU execution. LlamaIndex receives the same explicit local embedding adapter. Neither backend may select OpenAI, contact a hosted API, download a model, or create an undeclared cache.
