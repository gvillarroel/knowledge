# General GraphRAG strategy ranking on evaluation-only questions

## General evaluation-only direct comparison

| Pos. | Pair / strategy | Recall@10 | MRR@10 | nDCG@10 | Stable queries | P95 |
|---:|---|---:|---:|---:|---:|---:|
| 1 | Classical association | 100.00% | 100.00% | 99.60% | 100.00% | 664.65 ms |
| 2 | Classical fusion | 100.00% | 100.00% | 99.38% | 100.00% | 671.43 ms |
| 3 | Adaptive fusion | 100.00% | 100.00% | 99.38% | 100.00% | 2405.80 ms |
| 4 | Ensemble `robust` | 100.00% | 100.00% | 99.38% | 100.00% | 2486.93 ms |
| 5 | Classical topic | 100.00% | 100.00% | 99.31% | 100.00% | 665.76 ms |
| 6 | Specialized expert early confidence-gated hybrid | 100.00% | 99.17% | 99.03% | 100.00% | 989.63 ms |
| 7 | RustMallet association | 100.00% | 100.00% | 98.91% | 100.00% | 677.64 ms |
| 8 | RustMallet fusion | 100.00% | 100.00% | 98.85% | 100.00% | 684.80 ms |
| 9 | RustMallet topic | 100.00% | 100.00% | 98.68% | 100.00% | 682.38 ms |
| 10 | RustMallet BM25 | 98.33% | 100.00% | 98.11% | 100.00% | 650.81 ms |
| 11 | Classical BM25 | 98.33% | 100.00% | 98.11% | 100.00% | 665.72 ms |
| 12 | Ensemble `fast` | 100.00% | 96.67% | 97.58% | 100.00% | 2794.83 ms |
| 13 | Specialized expert Ensemble quality + trace v48 | 100.00% | 96.67% | 97.24% | 100.00% | 4855.90 ms |
| 14 | Tantivy BM25 | 100.00% | 96.25% | 96.25% | 100.00% | 128.27 ms |
| 15 | Entity Graph lexical | 98.89% | 92.55% | 92.70% | 100.00% | 485.78 ms |
| 16 | Embeddings lexical | 98.89% | 91.94% | 92.05% | 100.00% | 298.04 ms |
| 17 | Tika/MALLET fusion | 99.44% | 90.85% | 91.28% | 100.00% | 99.48 ms |
| 18 | Entity Graph fusion | 97.78% | 86.81% | 86.05% | 100.00% | 478.67 ms |
| 19 | Entity Graph entity | 95.83% | 82.39% | 81.77% | 100.00% | 471.66 ms |
| 20 | Entity Graph traversal | 93.89% | 75.22% | 75.89% | 100.00% | 478.05 ms |
| 21 | Tika/MALLET/Tantivy fusion | 93.06% | 61.30% | 66.38% | 100.00% | 2883.27 ms |
| 22 | Embeddings hybrid | 79.72% | 65.61% | 65.33% | 100.00% | 545.45 ms |
| 23 | Legacy lexical | 97.78% | 49.69% | 60.54% | 100.00% | 9.96 ms |
| 24 | Embeddings vector | 69.44% | 53.58% | 52.60% | 100.00% | 251.61 ms |
| 25 | Specialized expert supervised profiles v51 | 71.11% | 34.11% | 41.03% | 43.33% | 142.67 ms |

Scope: 60 evaluation-only questions, Top-10, authoritative-paper identity, three repetitions per strategy. Ranking uses nDCG@10, then MRR@10, Recall@10, latency, and stable strategy ID.

Graphify and Turso are omitted because neither exposes a compatible GraphRAG paper-level Top-10 route. This table measures retrieval and evidence validity, not generated-answer correctness.
