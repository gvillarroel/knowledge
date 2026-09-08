# EnterpriseRAG-Bench 40-question reduced-corpus comparison

Direct deterministic retrieval over 40 frozen questions, Top-10, with 3 repetitions per route. This evaluates retrieval, not generated-answer quality.

| Pos. | Family | Route | Recall@10 | MRR@10 | nDCG@10 | Full coverage | Stable queries | P95 |
|---:|---|---|---:|---:|---:|---:|---:|---:|
| 1 | Entity Graph | Lexical | 63.73% | 60.78% | 59.40% | 55.00% | 100.00% | 83.17 ms |
| 2 | Embeddings | Lexical | 61.86% | 61.50% | 59.07% | 50.00% | 100.00% | 10.28 ms |
| 3 | Classical | BM25 | 64.56% | 60.56% | 58.90% | 55.00% | 100.00% | 38.79 ms |
| 4 | Legacy | Lexical | 61.92% | 59.86% | 57.50% | 52.50% | 100.00% | 3.57 ms |
| 5 | Ensemble | Quality | 59.00% | 60.36% | 55.38% | 47.50% | 100.00% | 1315.92 ms |
| 6 | Ensemble | Fast | 59.00% | 59.07% | 52.29% | 47.50% | 100.00% | 1224.41 ms |
| 7 | Embeddings | Hybrid | 59.91% | 53.97% | 51.47% | 50.00% | 100.00% | 47.66 ms |
| 8 | Adaptive | Adaptive fusion | 59.00% | 57.47% | 50.34% | 47.50% | 100.00% | 1190.77 ms |
| 9 | Ensemble | Robust | 59.00% | 57.47% | 50.34% | 47.50% | 100.00% | 1141.87 ms |
| 10 | Classical | Association | 45.86% | 56.25% | 47.21% | 37.50% | 100.00% | 43.36 ms |
| 11 | Entity Graph | Fusion | 58.04% | 47.33% | 46.73% | 50.00% | 100.00% | 92.52 ms |
| 12 | Classical | Topic | 45.86% | 55.00% | 46.47% | 37.50% | 100.00% | 39.68 ms |
| 13 | Entity Graph | Entity | 56.58% | 46.67% | 45.25% | 45.00% | 100.00% | 82.75 ms |
| 14 | Classical | Fusion | 42.46% | 56.25% | 43.42% | 32.50% | 100.00% | 41.14 ms |
| 15 | Entity Graph | Traversal | 50.33% | 46.04% | 43.27% | 37.50% | 100.00% | 82.57 ms |
| 16 | Turso | Lexical SQL comparator | 49.87% | 40.85% | 40.32% | 40.00% | 100.00% | 52.04 ms |
| 17 | Embeddings | Vector | 36.92% | 37.80% | 32.64% | 25.00% | 100.00% | 34.76 ms |
| 18 | Graphify | Graph search | 17.37% | 20.42% | 13.63% | 10.00% | 100.00% | 128.30 ms |

All returned identities and hashes passed exact authoritative-ledger validation. Qrels are reviewed, non-exhaustive focus sets.

The Turso row is a declared generic SQL token-overlap comparator over the validated Turso store; Turso does not otherwise expose a canonical natural-language ranking route.

This is a reference-enriched reduced corpus with 85 reference documents and 900 fixed distractors, not an official Onyx leaderboard run over all 511,962 documents. The 40 questions cover eight grounded categories; high-level and information-not-found questions require a separate answer-quality contract.

The embedding backend is deterministic 384-dimensional hashing. No model was called. Provider cost and LLM tokens are zero for retrieval; local compute cost and generated-answer correctness were not measured. Each route has a fresh process; initialization is excluded from P95, and three repetitions reuse that route's caches.
