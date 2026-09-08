# Endocrine hygiene

## Direct comparison

| Pos. | Pair / strategy | nDCG@10 | Recall@10 | MRR@10 | P95 (ms) |
|---:|---|---:|---:|---:|---:|
| 1 | adaptive / bm25 | 95.30% | 98.90% | 95.00% | 26.30 ms |
| 2 | classical / bm25 | 95.30% | 98.90% | 95.00% | 20.60 ms |
| 3 | legacy / legacy_lexical | 94.70% | 98.90% | 96.70% | 0.80 ms |
| 4 | embeddings / lexical | 92.80% | 98.70% | 93.30% | 36.00 ms |

Omitted because this historical contract has no comparable measurements: ensemble, entity-graph. These are unavailable, not zero-score results.

Published best route per family; entity-graph and ensemble are unavailable on this historical contract, not zero-score rows.

[Original report](../../../evaluations/semantic-okf-endocrine-hygiene/reports/retrieval-comparison.md) · [Report hub](../README.md) · [CTA](../cta/README.md)

Primary comparison: **nDCG@10**. N/A is an unavailable or unmeasured value. This table does not score generated-answer correctness.

Publication source SHA-256: `bb02f571b8ed753815ef0b28e1de8275ca6df856d8f344a9ae9996594e6711f2`.
