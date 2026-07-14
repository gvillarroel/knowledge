# Semantic OKF Storage Version Comparison

Status: **pass**. Corpus: 874 records from 31 sources.

## Outcome

No version dominates every workload. The file-backed release remains the smallest and most portable baseline. The embedding-backed release uniquely exposes vector and hybrid discovery, but its measured routes did not beat the legacy lexical baseline on recall or nDCG in this corpus. The Turso-backed release adds bounded SQL and indexed relational rows while preserving byte-identical authoritative Semantic OKF files.

## Build and storage

| Version | Files | Bytes | Mean build ms | Deterministic rebuild | Authoritative core parity |
| --- | ---: | ---: | ---: | ---: | ---: |
| file-backed | 884 | 10888503 | 16253.3 | pass | baseline |
| embedding-backed | 888 | 21808060 | 176755.2 | pass | pass |
| turso-backed | 885 | 52405559 | 19765.4 | pass | pass |

Build timings are fresh CLI subprocess measurements for file-backed and Turso-backed releases. Embedding build timings come from its append-only, offline SentenceTransformers run manifest because that model-backed evaluation already performed two verified builds on the same manifest.

Relative to the file-backed baseline, Turso used 4.81x the storage and its build was 21.6% slower in this run.

## Exact and aggregate consultation

| Operation | File-backed median ms | Turso-backed median ms | Result parity |
| --- | ---: | ---: | ---: |
| Exact `(source_id, record_id)` lookup | 276.1 | 472.5 | pass |
| Group by source and type | 617.9 | 484.3 | pass |

Each latency is a fresh end-to-end CLI subprocess, including startup and the version's integrity checks. It is not an in-process engine microbenchmark.

For this corpus, Turso's single exact lookup was 71.1% slower, while its grouped aggregation was 21.6% faster. Batch related structured work into one bounded SQL query instead of paying the verification boundary for many small CLI calls.

## Embedding retrieval evidence

| Route | Recall@10 | MRR@10 | nDCG@10 | Evidence validity | Mean ms |
| --- | ---: | ---: | ---: | ---: | ---: |
| legacy_lexical | 0.7886 | 0.8611 | 0.8002 | 1.0000 | 2.6 |
| new_lexical | 0.4850 | 0.9167 | 0.5931 | 1.0000 | 1240.2 |
| vector | 0.4687 | 0.8278 | 0.5534 | 1.0000 | 6100.0 |
| hybrid | 0.4273 | 0.8889 | 0.5381 | 1.0000 | 6254.7 |

Timing caveat: reported latency is operational end-to-end latency, not an isolated algorithm-speed comparison; legacy and new route timings have intentionally different execution scopes.

## Capability decision matrix

| Need | Preferred version | Reason |
| --- | --- | --- |
| Lowest dependency and storage overhead | file-backed | JSONL, Markdown, and RDF remain directly inspectable and require no additional index engine. |
| Single exact record lookup on this corpus | file-backed | Its end-to-end CLI median was lower while returning the same authoritative record. |
| Paraphrase-oriented candidate discovery | embedding-backed, after quality tuning | It uniquely offers vector and hybrid retrieval, but the measured vector and hybrid routes trailed legacy lexical recall and nDCG. |
| Joins, grouping, and batched structured queries | Turso-backed | Prepared filters and one bounded SQL statement operate over indexed relational rows; grouping was faster in this run. |
| Direct standards-based graph queries | file-backed or embedding-backed | Their consultation path exposes local SPARQL over the authoritative RDF graphs. |
| SQL-oriented agent tooling with preserved evidence | Turso-backed | Records, attributes, concepts, artifacts, and selected RDF statements are queryable while original files remain authoritative. |
| Smallest distributable artifact | file-backed | It avoids both vectors and the duplicated relational projection. |

## Integrity findings

- File/Turso record-ledger parity: **pass**.
- File/Turso authoritative core byte parity: **pass**.
- Query result parity: **pass**.
- Published release bytes unchanged by consultation: **pass**.
- Turso logical database digest: `f0f6d96b3c31d2dfa3d71c302f7044e980979241bf843ef3574b82b493be565a`.

## Interpretation

Keep file-backed as the default portability and minimum-footprint release. Choose Turso when the workload can benefit from batched relational joins, grouping, or agent-authored bounded SQL; it is not automatically faster for one exact lookup because every CLI call preserves a full verification boundary. Choose embeddings only when paraphrase-oriented candidate discovery is required, and retune or re-evaluate its retrieval plan before assuming the additional model, build time, and storage improve quality.
