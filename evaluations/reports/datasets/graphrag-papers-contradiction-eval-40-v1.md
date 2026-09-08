# GraphRAG contradictions (40)

## Direct comparison

| Pos. | Pair / strategy | Full evidence@10 | Recall@10 | MRR@10 | nDCG@10 | P95 (ms) |
|---:|---|---:|---:|---:|---:|---:|
| 1 | specialized-expert / Specialized expert early confidence-gated hybrid | 92.50% | 97.71% | 88.33% | 85.11% | 941.60 ms |
| 2 | rust-mallet / RustMallet association | 90.00% | 97.08% | 88.33% | 87.09% | 492.97 ms |
| 3 | adaptive / Adaptive fusion | 87.50% | 96.25% | 88.33% | 86.22% | 1995.64 ms |
| 4 | classical / Classical association | 87.50% | 96.25% | 88.33% | 86.83% | 454.25 ms |
| 5 | classical / Classical fusion | 87.50% | 96.25% | 88.33% | 86.22% | 455.04 ms |
| 6 | classical / Classical topic | 87.50% | 96.25% | 85.83% | 84.63% | 450.19 ms |
| 7 | ensemble / Ensemble fast | 87.50% | 96.25% | 84.58% | 84.06% | 2308.88 ms |
| 8 | ensemble / Ensemble robust | 87.50% | 96.25% | 88.33% | 86.22% | 2017.18 ms |
| 9 | rust-mallet / RustMallet fusion | 87.50% | 96.25% | 88.33% | 85.86% | 496.45 ms |
| 10 | rust-mallet / RustMallet topic | 87.50% | 96.25% | 84.17% | 83.49% | 497.68 ms |
| 11 | specialized-expert / Specialized expert Ensemble quality + trace v48 | 87.50% | 96.25% | 78.96% | 81.35% | 4088.78 ms |
| 12 | tantivy / Tantivy BM25 | 82.50% | 93.75% | 87.50% | 81.28% | 122.69 ms |
| 13 | entity-graph / Entity Graph lexical | 67.50% | 88.12% | 70.44% | 68.19% | 497.28 ms |
| 14 | classical / Classical BM25 | 65.00% | 86.25% | 90.00% | 81.93% | 435.86 ms |
| 15 | entity-graph / Entity Graph fusion | 65.00% | 87.92% | 66.46% | 65.27% | 505.72 ms |
| 16 | rust-mallet / RustMallet BM25 | 65.00% | 86.25% | 90.00% | 81.93% | 470.43 ms |
| 17 | entity-graph / Entity Graph traversal | 62.50% | 86.88% | 63.47% | 63.48% | 501.14 ms |
| 18 | entity-graph / Entity Graph entity | 60.00% | 86.25% | 66.42% | 64.93% | 493.58 ms |
| 19 | legacy / Legacy lexical | 60.00% | 83.96% | 51.28% | 54.46% | 7.78 ms |
| 20 | tika-mallet / Tika/MALLET fusion | 55.00% | 83.33% | 60.80% | 59.90% | 104.40 ms |
| 21 | specialized-expert / Specialized expert supervised profiles v51 | 52.50% | 77.92% | 41.30% | 48.08% | 47.04 ms |
| 22 | embeddings / Embeddings lexical | 47.50% | 77.92% | 62.96% | 61.23% | 259.01 ms |
| 23 | tika-mallet-tantivy / Tika/MALLET/Tantivy fusion | 45.00% | 78.33% | 56.38% | 56.06% | 1990.39 ms |
| 24 | embeddings / Embeddings hybrid | 37.50% | 70.00% | 81.75% | 66.96% | 472.63 ms |
| 25 | embeddings / Embeddings vector | 32.50% | 65.83% | 71.50% | 57.74% | 222.01 ms |

Released evaluation-only contradiction cohort; complete evidence is the primary metric; 25 compatible routes.

[Original report](../../../evaluations/graphrag-unseen-generalization/study-v5-contradictions/publication/tables/contradiction-strategy-ranking.table.md) · [Report hub](../README.md) · [CTA](../cta/README.md)

Primary comparison: **Full evidence@10**. N/A is an unavailable or unmeasured value. This table does not score generated-answer correctness.

Publication source SHA-256: `ba810f756d83a0673730c5ef7f68eb24f1e4448d34898c63188590fcecffa1c6`.
