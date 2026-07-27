# Tantivy Runtime

## Pin and installation

Install `scripts/requirements.txt` into an isolated CPython 3.12 environment. The
skill requires the official `tantivy==0.26.0` Python package and fails on a missing
or different version. Do not substitute a Python BM25 implementation, search
service, command-line binary, or another Tantivy binding.

Run:

```bash
python -B scripts/runtime_smoke.py
```

The report must identify package version `0.26.0`, the Rust implementation, native
BM25 scoring, and in-memory index storage.

## Index behavior

The query helper creates a fresh schema with:

- a raw stored `document_id`;
- positional indexed and stored `title`; and
- positional indexed and stored `body`.

It applies filters first, builds `tantivy.Index(schema)` without a filesystem
directory, indexes through one writer thread, and discards the index at process
exit. Never create a Tantivy directory, cache, or sidecar in the snapshot.

The persisted plan must use `k1=1.2` and `b=0.75`. Tantivy supplies those native
defaults; the plan's title and body weights are passed as query-parser field
boosts. Output must disclose the package version, tokenizer, boosts, indexed
passage count, parsed component queries, native scores, and storage mode.

## Diagnostics

Stop on:

- a missing package or version mismatch;
- unsupported BM25 parameters;
- invalid or regex query syntax;
- a non-finite native score;
- an unknown document identity returned by the index; or
- any snapshot validation failure before indexing.

An empty result set is valid when no filtered passage matches. Do not fall back to
another engine or broaden filters implicitly.
