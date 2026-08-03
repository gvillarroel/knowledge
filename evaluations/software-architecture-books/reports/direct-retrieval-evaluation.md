# Software Architecture Books Retrieval Evaluation

This report compares deterministic discovery routes on 40 frozen questions. It evaluates retrieval, not generated-answer quality. Qrels are non-exhaustive focus sets.

| Rank | Route | Recall@10 | nDCG@10 | Full qrel coverage | Reviewed locator recall | P95 latency |
|---:|---|---:|---:|---:|---:|---:|
| 1 | fusion | 0.973 | 0.926 | 0.925 | 0.067 | 1863.9 ms |
| 2 | association | 0.973 | 0.926 | 0.925 | 0.067 | 1901.4 ms |
| 3 | topic | 0.973 | 0.926 | 0.925 | 0.067 | 1902.3 ms |
| 4 | bm25 | 0.838 | 0.814 | 0.650 | 0.167 | 1815.4 ms |

The JSON companion contains duplicate-safe per-question ranks, source identities, hashes, and exact locators, but excludes all private passage text.
