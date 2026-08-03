# Specialized Expert Canonical Retrieval Audit

## Direct comparison

| Pos. | Pair / strategy | Recall@10 | nDCG@10 | P95 |
|---:|---|---:|---:|---:|
| 1 | Ensemble `quality` | 83.82% | 85.20% | 1461.92 ms |
| 2 | Ensemble `fast` | 83.82% | 84.30% | 766.57 ms |
| 3 | Adaptive fusion | 83.82% | 83.43% | 407.56 ms |
| 4 | Ensemble `robust` | 83.82% | 83.43% | 568.20 ms |
| 5 | Classical fusion | 83.46% | 83.23% | 106.76 ms |
| 6 | Classical association | 82.56% | 82.58% | 111.94 ms |
| 7 | Classical topic | 82.42% | 82.25% | 107.79 ms |
| 8 | RustMallet topic | 80.80% | 81.86% | 238.70 ms |
| 9 | RustMallet fusion | 80.28% | 81.84% | 232.25 ms |
| 10 | Entity Graph lexical | 79.76% | 81.14% | 241.63 ms |
| 11 | Tantivy BM25 | 80.74% | 81.05% | 90.92 ms |
| 12 | RustMallet association | 79.49% | 80.84% | 224.30 ms |
| 13 | Entity Graph fusion | 80.84% | 79.86% | 237.15 ms |
| 14 | Entity Graph entity | 79.58% | 76.72% | 237.23 ms |
| 15 | Tika/MALLET fusion | 74.82% | 75.44% | 86.36 ms |
| 16 | Legacy lexical | 79.31% | 74.22% | 4.79 ms |
| 17 | Entity Graph traversal | 78.49% | 74.03% | 235.99 ms |
| 18 | Tika/MALLET/Tantivy fusion | 73.50% | 71.75% | 470.74 ms |
| 19 | Specialized expert lexical | 72.20% | 66.57% | 170.78 ms |
| 20 | Classical BM25 | 49.72% | 60.94% | 99.46 ms |
| 21 | RustMallet BM25 | 49.72% | 60.94% | 226.69 ms |
| 22 | Embeddings lexical | 54.75% | 60.92% | 76.20 ms |
| 23 | Embeddings hybrid | 48.34% | 56.51% | 228.52 ms |
| 24 | Embeddings vector | 50.40% | 54.77% | 122.82 ms |

## Audit result

The specialized expert lexical route is position **19 of 24** under the shared all-40 Top-10 contract.

Both independently packaged guidance variants produced identical Top-10 rankings and metrics, identical pool-100 rankings, exact Top-10 prefixes, and 100% exact evidence validity. Their guidance does not participate in this deterministic retrieval score; grounded answer quality remains a separate Harbor evaluation.
