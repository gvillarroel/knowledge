# Semantic OKF Graphify Storage Comparison

Status: **pass**. Corpus: 874 records from 31 sources; retrieval set: 30 questions.

## Build and artifact cost

| Version | Files | Bytes | Mean build (ms) | Deterministic |
|---|---:|---:|---:|---|
| file-backed | 884 | 10888503 | 16253.3 | pass |
| embedding-backed | 888 | 21808060 | 176755.2 | pass |
| turso-backed | 885 | 52405559 | 19765.4 | pass |
| graphify-backed | 886 | 31704281 | 50755.4 | pass |

Graphify build time includes the unchanged Semantic OKF build, deterministic temporary-view generation, structural extraction, canonical serialization, and full validation. Historical embedding timing uses its append-only offline model run.

## Authoritative operations

| Operation | File median (ms) | Turso median (ms) | Graphify median (ms) |
|---|---:|---:|---:|
| Exact record | 276.1 | 472.5 | 1442.2 |
| Group by source/type | 617.9 | 484.3 | 1554.3 |

Graphify exact lookup and aggregation intentionally use `records.jsonl`; their extra time is the fail-closed validation of the core and derived graph in each fresh process.

## Retrieval on the identical 30 questions

| Route | Recall@10 | MRR@10 | nDCG@10 | Evidence validity | Mean (ms) |
|---|---:|---:|---:|---:|---:|
| legacy_lexical | 0.7886 | 0.8611 | 0.8002 | 1.0000 | 2.6 |
| new_lexical | 0.4850 | 0.9167 | 0.5931 | 1.0000 | 1240.2 |
| vector | 0.4687 | 0.8278 | 0.5534 | 1.0000 | 6100.0 |
| hybrid | 0.4273 | 0.8889 | 0.5381 | 1.0000 | 6254.7 |
| graphify_structural | 0.4950 | 0.8306 | 0.5794 | 1.0000 | 2877.1 |

Latency scopes differ: legacy lexical reuses an in-process index, while Graphify, new lexical, vector, and hybrid figures include fresh validated subprocess boundaries. Quality metrics use the same paper-level qrels and first-rank deduplication.

## Integrity findings

- Authoritative core parity with file-backed: **pass**.
- Independent graph rebuild: **pass** (`e996aec29ca6d0f629edd218574d4bb99b09ac87bca9f536a057c02bfdf6ca95`).
- Exact and aggregate result parity: **pass**.
- Full ledger, record-digest, paper-ID, locator, and concept-body evidence binding: **pass**.
- Snapshot unchanged by all consultation calls: **pass**.
- Graph: 10797 nodes, 13289 edges, 0 orphans.

## Decision

Keep file-backed as the default minimum-footprint release. Choose Turso for repeated structured SQL-style aggregation. Choose embeddings when tuned paraphrase retrieval is required. Choose Graphify when linked-heading orientation and bounded Markdown-neighborhood traversal are useful and the additional graph size, build time, and validation latency are acceptable. Graphify did not become a factual authority: every returned record was hydrated from unchanged OKF concepts.
