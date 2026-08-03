# Software Architecture Books: All Registered Retrieval Routes

Direct deterministic retrieval over 40 frozen questions, Top-10, with 3 repetitions per route. This evaluates retrieval, not generated-answer quality.

| Pos. | Family | Route | Recall@10 | MRR@10 | nDCG@10 | Full coverage | Stable queries | P95 |
|---:|---|---|---:|---:|---:|---:|---:|---:|
| 1 | Classical | Fusion | 97.29% | 97.50% | 92.58% | 92.50% | 100.00% | 1832.07 ms |
| 2 | Classical | Association | 97.29% | 97.50% | 92.56% | 92.50% | 100.00% | 1799.42 ms |
| 3 | Classical | Topic | 97.29% | 97.50% | 92.56% | 92.50% | 100.00% | 1882.90 ms |
| 4 | Entity Graph | Lexical | 98.33% | 89.25% | 88.98% | 95.00% | 100.00% | 5473.10 ms |
| 5 | Ensemble | Fast | 95.21% | 89.38% | 86.04% | 87.50% | 100.00% | 7820.74 ms |
| 6 | Ensemble | Robust | 95.21% | 90.50% | 85.61% | 87.50% | 100.00% | 3901.24 ms |
| 7 | Adaptive | Adaptive fusion | 95.21% | 90.50% | 85.61% | 87.50% | 100.00% | 4206.12 ms |
| 8 | Ensemble | Quality | 95.21% | 88.00% | 85.01% | 87.50% | 100.00% | 9788.55 ms |
| 9 | Classical | BM25 | 83.75% | 95.00% | 84.18% | 65.00% | 100.00% | 1858.98 ms |
| 10 | Entity Graph | Fusion | 97.50% | 81.33% | 83.50% | 92.50% | 100.00% | 5612.20 ms |
| 11 | Entity Graph | Entity | 93.54% | 81.15% | 81.76% | 82.50% | 100.00% | 4262.95 ms |
| 12 | Legacy | Lexical | 95.00% | 80.62% | 81.55% | 90.00% | 100.00% | 0.56 ms |
| 13 | Entity Graph | Traversal | 92.92% | 80.92% | 80.30% | 85.00% | 100.00% | 4336.46 ms |
| 14 | Embeddings | Hybrid | 92.08% | 72.92% | 73.39% | 80.00% | 100.00% | 1182.23 ms |
| 15 | Embeddings | Lexical | 92.92% | 71.57% | 72.13% | 82.50% | 100.00% | 1154.39 ms |
| 16 | Embeddings | Vector | 84.38% | 65.99% | 65.56% | 65.00% | 100.00% | 2.98 ms |
| 17 | Turso | Lexical SQL comparator | 86.25% | 52.72% | 58.40% | 72.50% | 100.00% | 1372.74 ms |
| 18 | Graphify | Graph search | 59.58% | 67.92% | 57.10% | 42.50% | 100.00% | 211.65 ms |

All returned identities and hashes passed exact authoritative-ledger validation. Qrels are reviewed, non-exhaustive focus sets.

The Turso row is a declared generic SQL token-overlap comparator over the validated Turso store; Turso does not otherwise expose a canonical natural-language ranking route.
