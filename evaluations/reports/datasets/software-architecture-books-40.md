# Software architecture books (40)

## Direct comparison

| Pos. | Pair / strategy | nDCG@10 | Recall@10 | MRR@10 | P95 (ms) |
|---:|---|---:|---:|---:|---:|
| 1 | classical / Fusion | 92.58% | 97.29% | 97.50% | 1832.07 ms |
| 2 | classical / Association | 92.56% | 97.29% | 97.50% | 1799.42 ms |
| 3 | classical / Topic | 92.56% | 97.29% | 97.50% | 1882.90 ms |
| 4 | entity-graph / Lexical | 88.98% | 98.33% | 89.25% | 5473.10 ms |
| 5 | ensemble / Fast | 86.04% | 95.21% | 89.38% | 7820.74 ms |
| 6 | adaptive / Adaptive fusion | 85.61% | 95.21% | 90.50% | 4206.12 ms |
| 7 | ensemble / Robust | 85.61% | 95.21% | 90.50% | 3901.24 ms |
| 8 | ensemble / Quality | 85.01% | 95.21% | 88.00% | 9788.55 ms |
| 9 | classical / BM25 | 84.18% | 83.75% | 95.00% | 1858.98 ms |
| 10 | entity-graph / Fusion | 83.50% | 97.50% | 81.33% | 5612.20 ms |
| 11 | entity-graph / Entity | 81.76% | 93.54% | 81.15% | 4262.95 ms |
| 12 | legacy / Lexical | 81.55% | 95.00% | 80.62% | 0.56 ms |
| 13 | entity-graph / Traversal | 80.30% | 92.92% | 80.92% | 4336.46 ms |
| 14 | embeddings / Hybrid | 73.39% | 92.08% | 72.92% | 1182.23 ms |
| 15 | embeddings / Lexical | 72.13% | 92.92% | 71.57% | 1154.39 ms |
| 16 | embeddings / Vector | 65.56% | 84.38% | 65.99% | 2.98 ms |
| 17 | turso / Lexical SQL comparator | 58.40% | 86.25% | 52.72% | 1372.74 ms |
| 18 | graphify / Graph search | 57.10% | 59.58% | 67.92% | 211.65 ms |

Private book corpus; 18 direct routes, Top-10, three repetitions; published rounded aggregates.

[Original report](../../../evaluations/software-architecture-books/reports/all-route-comparison.md) · [Report hub](../README.md) · [CTA](../cta/README.md)

Primary comparison: **nDCG@10**. N/A is an unavailable or unmeasured value. This table does not score generated-answer correctness.

Publication source SHA-256: `7f1d160e8831ef8f953b6b8839b7ff8ad1d774493a37f992724a0bc8b28648b6`.
