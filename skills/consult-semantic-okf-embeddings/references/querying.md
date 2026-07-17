# Querying an Embedding-Enabled Snapshot

## Contents

1. Mode selection
2. Deterministic ranking
3. Filters and evidence
4. Fallback rules
5. Optional local models

## 1. Mode selection

| Need | Mode or layer | Reason |
|---|---|---|
| Exact ID, type, attribute, count, or literal path | Ledger | No ranking ambiguity |
| Rare token, code, name, or quoted phrase | Lexical | Exact term evidence dominates |
| Paraphrase or concept with little word overlap | Vector | Same-model cosine neighborhood |
| General natural-language discovery | Auto/hybrid | Combines lexical precision and semantic recall |
| Join, aggregate, traverse, or trace lineage | Selected RDF graph | Retrieval chunks do not encode query semantics |

`auto` requests hybrid search and degrades to lexical only when an allowlisted provider is unavailable. Explicit `vector` and `hybrid` requests fail unless `--allow-fallback` is present.

## 2. Deterministic ranking

Lexical ranking uses a Unicode case-folded `\w+` tokenizer and dependency-free BM25. Zero-score chunks are not lexical hits.

Vector ranking embeds the query with the exact declared provider and scans every filtered vector with cosine similarity. It does not use an approximate index. Equal scores sort by `chunk_id`.

Hybrid ranking uses reciprocal-rank fusion with constant 60:

```text
score = 1 / (60 + lexical_rank) + 1 / (60 + vector_rank)
```

A missing component contributes zero. Final ties sort by `chunk_id`. Component scores remain visible, but they are discovery diagnostics rather than evidence.

## 3. Filters and evidence

Source, concept ID, and concept type filters are applied before document frequency, cosine ranking, and reciprocal-rank fusion are calculated. Repeat a flag to allow several values of one kind. Filter kinds combine with logical AND.

After ranking:

1. copy the exact `concept_path` and locator from the hit;
2. verify the file exists beneath the bundle;
3. read the authoritative concept or ledger record;
4. use RDF only when the operation actually requires it;
5. cite the authoritative file, not `retrieval/index.json` or a similarity score.

## 4. Fallback rules

Permitted fallback:

- SentenceTransformers package is absent;
- the exact model ID and revision are not present in the local cache;
- a deliberately injected provider reports unavailability.

Forbidden fallback:

- core, ledger, source, chunk, or embedding digest mismatch;
- unknown provider or mutable model revision;
- malformed JSON/JSONL, duplicate key, NaN, infinity, zero vector, wrong dimension, or invalid normalization;
- orphan or missing chunk, concept-path escape, locator mismatch, count mismatch, or unordered identity.

Always surface the fallback object in a successful degraded response.

## 5. Optional local models

Consultation calls `huggingface_hub.snapshot_download` lazily with the declared namespace/repository, immutable revision, `local_files_only=True`, and Hugging Face/Transformers offline flags. It requires the resolved directory leaf to equal the declared commit, then gives that resolved local path—not the model ID—to SentenceTransformers on CPU with `local_files_only=True` and `trust_remote_code=False`. Model weights are an explicit external input and are never fetched by consultation. Hashing v1 remains the portable standard-library provider and uses the same frozen symmetric encoder for documents and queries.
