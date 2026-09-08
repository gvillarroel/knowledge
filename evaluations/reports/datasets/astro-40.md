# Astro documentation (40)

## Direct comparison

| Pos. | Pair / strategy | nDCG@10 | Recall@10 | MRR@10 | P95 (ms) |
|---:|---|---:|---:|---:|---:|
| 1 | adaptive / association | 83.50% | 88.80% | 91.50% | 1443.60 ms |
| 2 | classical / association | 83.50% | 88.80% | 91.50% | 1430.10 ms |
| 3 | ensemble / quality | 81.90% | 89.60% | 89.00% | 10938.40 ms |
| 4 | embeddings / lexical | 78.30% | 89.80% | 81.20% | 107.80 ms |
| 5 | entity-graph / entity | 70.60% | 88.10% | 72.90% | 1626.60 ms |
| 6 | legacy / legacy_tfidf | 68.50% | 82.30% | 70.60% | 3.60 ms |

Published best route for six families; raw pool 100, document deduplication; standalone selected-route P95.

[Original report](../../../evaluations/semantic-okf-astro/reports/retrieval-comparison.md) · [Report hub](../README.md) · [CTA](../cta/README.md)

Primary comparison: **nDCG@10**. N/A is an unavailable or unmeasured value. This table does not score generated-answer correctness.

Publication source SHA-256: `0ed19c2429ef691cf94633359d13a9f2ad181f56da6e16b5e5bca333f8ed9e8a`.
