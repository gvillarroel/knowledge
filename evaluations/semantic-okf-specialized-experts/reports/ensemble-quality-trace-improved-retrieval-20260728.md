# Trace-Improved Specialized Expert Retrieval Audit

## Direct comparison

| Pos. | Pair / strategy | Recall@10 | nDCG@10 | P95 |
|---:|---|---:|---:|---:|
| 1 | Specialized expert Ensemble quality + trace v48 | 85.39% | 86.02% | 2012.48 ms |
| 2 | Ensemble `fast` | 83.82% | 84.30% | 766.57 ms |
| 3 | Specialized expert early confidence-gated hybrid | 85.39% | 83.75% | 573.53 ms |
| 4 | Adaptive fusion | 83.82% | 83.43% | 407.56 ms |
| 5 | Ensemble `robust` | 83.82% | 83.43% | 568.20 ms |
| 6 | Classical fusion | 83.46% | 83.23% | 106.76 ms |
| 7 | Classical association | 82.56% | 82.58% | 111.94 ms |
| 8 | Classical topic | 82.42% | 82.25% | 107.79 ms |
| 9 | RustMallet topic | 80.80% | 81.86% | 238.70 ms |
| 10 | RustMallet fusion | 80.28% | 81.84% | 232.25 ms |
| 11 | Entity Graph lexical | 79.76% | 81.14% | 241.63 ms |
| 12 | Tantivy BM25 | 80.74% | 81.05% | 90.92 ms |
| 13 | RustMallet association | 79.49% | 80.84% | 224.30 ms |
| 14 | Entity Graph fusion | 80.84% | 79.86% | 237.15 ms |
| 15 | Entity Graph entity | 79.58% | 76.72% | 237.23 ms |
| 16 | Tika/MALLET fusion | 74.82% | 75.44% | 86.36 ms |
| 17 | Legacy lexical | 79.31% | 74.22% | 4.79 ms |
| 18 | Entity Graph traversal | 78.49% | 74.03% | 235.99 ms |
| 19 | Tika/MALLET/Tantivy fusion | 73.50% | 71.75% | 470.74 ms |
| 20 | Classical BM25 | 49.72% | 60.94% | 99.46 ms |
| 21 | RustMallet BM25 | 49.72% | 60.94% | 226.69 ms |
| 22 | Embeddings lexical | 54.75% | 60.92% | 76.20 ms |
| 23 | Embeddings hybrid | 48.34% | 56.51% | 228.52 ms |
| 24 | Embeddings vector | 50.40% | 54.77% | 122.82 ms |

## Improvement result

The frozen `graphrag-ensemble-quality-trace-expert-v48` candidate is position **1 of 24**, replacing its predecessor at position 1.

Recall@10 changed from 83.82% to 85.39%; nDCG@10 changed from 85.20% to 86.02%. The Top-10 result is an exact prefix of the pool-100 run, every query completed without error, all returned evidence was exact, and the expert remained byte-identical.
