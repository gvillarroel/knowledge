# Data Science, AI, and Machine Learning Books: All Registered Retrieval Routes

Direct deterministic retrieval over 40 frozen questions, Top-10, with 3 repetitions per route. This evaluates retrieval, not generated-answer quality.

| Pos. | Family | Route | Recall@10 | MRR@10 | nDCG@10 | Full coverage | Stable queries | P95 |
|---:|---|---|---:|---:|---:|---:|---:|---:|
| 1 | Ensemble | Fast | 99.17% | 96.75% | 94.44% | 97.50% | 100.00% | 16155.87 ms |
| 2 | Classical | BM25 | 98.33% | 94.06% | 93.08% | 95.00% | 100.00% | 1766.70 ms |
| 3 | Ensemble | Quality | 99.17% | 94.11% | 92.78% | 97.50% | 100.00% | 22566.20 ms |
| 4 | Adaptive | Adaptive fusion | 99.17% | 93.23% | 91.78% | 97.50% | 100.00% | 5359.04 ms |
| 5 | Ensemble | Robust | 99.17% | 93.23% | 91.78% | 97.50% | 100.00% | 5403.21 ms |
| 6 | Entity Graph | Lexical | 99.17% | 88.75% | 90.31% | 97.50% | 100.00% | 14174.95 ms |
| 7 | Entity Graph | Fusion | 97.50% | 86.88% | 85.83% | 92.50% | 100.00% | 14003.99 ms |
| 8 | Legacy | Lexical | 95.00% | 81.75% | 83.22% | 90.00% | 100.00% | 0.91 ms |
| 9 | Classical | Association | 78.54% | 91.25% | 80.54% | 70.00% | 100.00% | 1594.91 ms |
| 10 | Classical | Topic | 78.54% | 91.25% | 80.54% | 70.00% | 100.00% | 1727.19 ms |
| 11 | Classical | Fusion | 78.54% | 91.25% | 80.54% | 70.00% | 100.00% | 1735.27 ms |
| 12 | Entity Graph | Entity | 96.67% | 78.42% | 80.29% | 90.00% | 100.00% | 13957.18 ms |
| 13 | Embeddings | Lexical | 83.33% | 58.19% | 63.24% | 75.00% | 100.00% | 2387.46 ms |
| 14 | Embeddings | Hybrid | 88.96% | 53.25% | 60.97% | 80.00% | 100.00% | 2393.27 ms |
| 15 | Graphify | Graph search | 53.96% | 62.50% | 54.41% | 47.50% | 100.00% | 737.82 ms |
| 16 | Entity Graph | Traversal | 79.58% | 43.55% | 51.20% | 72.50% | 100.00% | 11329.79 ms |
| 17 | Turso | Lexical SQL comparator | 74.38% | 31.79% | 40.16% | 65.00% | 100.00% | 2269.25 ms |
| 18 | Embeddings | Vector | 70.42% | 29.13% | 39.38% | 67.50% | 100.00% | 5.09 ms |

All returned identities and hashes passed exact authoritative-ledger validation. Qrels are reviewed, non-exhaustive focus sets.

The Turso row is a declared generic SQL token-overlap comparator over the validated Turso store; Turso does not otherwise expose a canonical natural-language ranking route.
