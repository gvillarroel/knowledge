# EnterpriseRAG reduced corpus (40)

## Direct comparison

| Pos. | Pair / strategy | nDCG@10 | Recall@10 | MRR@10 | P95 (ms) |
|---:|---|---:|---:|---:|---:|
| 1 | entity-graph / Lexical | 59.40% | 63.73% | 60.78% | 83.17 ms |
| 2 | embeddings / Lexical | 59.07% | 61.86% | 61.50% | 10.28 ms |
| 3 | classical / BM25 | 58.90% | 64.56% | 60.56% | 38.79 ms |
| 4 | legacy / Lexical | 57.50% | 61.92% | 59.86% | 3.57 ms |
| 5 | ensemble / Quality | 55.38% | 59.00% | 60.36% | 1315.92 ms |
| 6 | ensemble / Fast | 52.29% | 59.00% | 59.07% | 1224.41 ms |
| 7 | embeddings / Hybrid | 51.47% | 59.91% | 53.97% | 47.66 ms |
| 8 | adaptive / Adaptive fusion | 50.34% | 59.00% | 57.47% | 1190.77 ms |
| 9 | ensemble / Robust | 50.34% | 59.00% | 57.47% | 1141.87 ms |
| 10 | classical / Association | 47.21% | 45.86% | 56.25% | 43.36 ms |
| 11 | entity-graph / Fusion | 46.73% | 58.04% | 47.33% | 92.52 ms |
| 12 | classical / Topic | 46.47% | 45.86% | 55.00% | 39.68 ms |
| 13 | entity-graph / Entity | 45.25% | 56.58% | 46.67% | 82.75 ms |
| 14 | classical / Fusion | 43.42% | 42.46% | 56.25% | 41.14 ms |
| 15 | entity-graph / Traversal | 43.27% | 50.33% | 46.04% | 82.57 ms |
| 16 | turso / Lexical SQL comparator | 40.32% | 49.87% | 40.85% | 52.04 ms |
| 17 | embeddings / Vector | 32.64% | 36.92% | 37.80% | 34.76 ms |
| 18 | graphify / Graph search | 13.63% | 17.37% | 20.42% | 128.30 ms |

Pinned Onyx v1.0.0; 40 stratified questions, 985 documents including 900 distractors. Retrieval only; not the full official benchmark.

[Original report](../../../evaluations/enterprise-rag-bench/reports/20260906-v2/final-report.md) · [Report hub](../README.md) · [CTA](../cta/README.md)

Primary comparison: **nDCG@10**. N/A is an unavailable or unmeasured value. This table does not score generated-answer correctness.

Publication source SHA-256: `23c451906b6195575eb716f9d86a387874d5a90af97ee3ab7303a65b8745b6ab`.

**Scope correction:** these historical Enterprise records contain titles without mapped document bodies. See the [ingestion audit](../enterprise-source-skills/ingestion-scope-20260907.md). Their original scores are preserved and are not full-text retrieval measurements.

[Enterprise evolution sweep and its separate development contract](../evolution/e6/README.md)
