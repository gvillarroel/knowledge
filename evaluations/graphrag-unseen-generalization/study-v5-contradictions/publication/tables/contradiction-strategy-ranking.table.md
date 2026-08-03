# GraphRAG contradiction-search retrieval ranking

## Cross-source contradiction retrieval comparison

| Pos. | Pair / strategy | Full evidence@10 | Recall@10 | MRR@10 | nDCG@10 | Stable queries | P95 |
|---:|---|---:|---:|---:|---:|---:|---:|
| 1 | Specialized expert early confidence-gated hybrid | 92.50% | 97.71% | 88.33% | 85.11% | 100.00% | 941.60 ms |
| 2 | RustMallet association | 90.00% | 97.08% | 88.33% | 87.09% | 100.00% | 492.97 ms |
| 3 | Classical association | 87.50% | 96.25% | 88.33% | 86.83% | 100.00% | 454.25 ms |
| 4 | Classical fusion | 87.50% | 96.25% | 88.33% | 86.22% | 100.00% | 455.04 ms |
| 5 | Adaptive fusion | 87.50% | 96.25% | 88.33% | 86.22% | 100.00% | 1995.64 ms |
| 6 | Ensemble `robust` | 87.50% | 96.25% | 88.33% | 86.22% | 100.00% | 2017.18 ms |
| 7 | RustMallet fusion | 87.50% | 96.25% | 88.33% | 85.86% | 100.00% | 496.45 ms |
| 8 | Classical topic | 87.50% | 96.25% | 85.83% | 84.63% | 100.00% | 450.19 ms |
| 9 | Ensemble `fast` | 87.50% | 96.25% | 84.58% | 84.06% | 100.00% | 2308.88 ms |
| 10 | RustMallet topic | 87.50% | 96.25% | 84.17% | 83.49% | 100.00% | 497.68 ms |
| 11 | Specialized expert Ensemble quality + trace v48 | 87.50% | 96.25% | 78.96% | 81.35% | 100.00% | 4088.78 ms |
| 12 | Tantivy BM25 | 82.50% | 93.75% | 87.50% | 81.28% | 100.00% | 122.69 ms |
| 13 | Entity Graph lexical | 67.50% | 88.12% | 70.44% | 68.19% | 100.00% | 497.28 ms |
| 14 | Classical BM25 | 65.00% | 86.25% | 90.00% | 81.93% | 100.00% | 435.86 ms |
| 15 | RustMallet BM25 | 65.00% | 86.25% | 90.00% | 81.93% | 100.00% | 470.43 ms |
| 16 | Entity Graph fusion | 65.00% | 87.92% | 66.46% | 65.27% | 100.00% | 505.72 ms |
| 17 | Entity Graph traversal | 62.50% | 86.88% | 63.47% | 63.48% | 100.00% | 501.14 ms |
| 18 | Entity Graph entity | 60.00% | 86.25% | 66.42% | 64.93% | 100.00% | 493.58 ms |
| 19 | Legacy lexical | 60.00% | 83.96% | 51.28% | 54.46% | 100.00% | 7.78 ms |
| 20 | Tika/MALLET fusion | 55.00% | 83.33% | 60.80% | 59.90% | 100.00% | 104.40 ms |
| 21 | Specialized expert supervised profiles v51 | 52.50% | 77.92% | 41.30% | 48.08% | 50.00% | 47.04 ms |
| 22 | Embeddings lexical | 47.50% | 77.92% | 62.96% | 61.23% | 100.00% | 259.01 ms |
| 23 | Tika/MALLET/Tantivy fusion | 45.00% | 78.33% | 56.38% | 56.06% | 100.00% | 1990.39 ms |
| 24 | Embeddings hybrid | 37.50% | 70.00% | 81.75% | 66.96% | 100.00% | 472.63 ms |
| 25 | Embeddings vector | 32.50% | 65.83% | 71.50% | 57.74% | 100.00% | 222.01 ms |

Scope: 40 evaluation-only contradiction audits over the existing fifteen-paper corpus; 15 questions require two papers, 20 require three, and 5 require four. Full evidence@10 is the primary metric because a contradiction cannot be adjudicated when any required side is absent.

This table measures direct retrieval and exact evidence validity, not generated-answer correctness. Graphify and Turso are omitted because neither exposes the same paper-level Top-10 contract.
