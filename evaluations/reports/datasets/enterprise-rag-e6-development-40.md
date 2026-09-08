# EnterpriseRAG e6 development (40)

## Direct comparison

| Pos. | Pair / strategy | nDCG@10 | Recall@10 | MRR@10 | P95 (ms) |
|---:|---|---:|---:|---:|---:|
| 1 | embeddings / baseline / hybrid | 63.19% | 68.38% | 64.38% | 171.35 ms |
| 2 | ensemble / candidate-018 / quality | 61.37% | 62.76% | 63.12% | 1518.88 ms |
| 3 | graphify / candidate-010 / search | 60.36% | 63.24% | 62.50% | 140.04 ms |
| 4 | legacy / candidate-003 / lexical | 59.62% | 62.48% | 61.50% | 9.63 ms |
| 5 | turso / candidate-003 / lexical-sql | 59.62% | 62.48% | 61.50% | 8.66 ms |
| 6 | adaptive / candidate-013 / adaptive | 58.62% | 62.20% | 60.36% | 1305.60 ms |
| 7 | classical / candidate-014 / fusion | 48.21% | 45.86% | 57.50% | 39.30 ms |
| 8 | entity-graph / candidate-010 / fusion | 48.19% | 58.59% | 48.34% | 39.53 ms |

Forty exposed development queries on a reference-enriched 985-document corpus. Eight retained primary routes from frozen experimental profiles: five construction and three consultation treatments. Eighteen retained-profile routes are available separately as diagnostics. These maxima do not describe installed defaults, unseen-query quality or official generated-answer accuracy; the terminal decision is separate.

[Original report](../../../evaluations/reports/evolution/e6/catalog-001/comparison.md) · [Report hub](../README.md) · [CTA](../cta/README.md)

Primary comparison: **nDCG@10**. N/A is an unavailable or unmeasured value. This table does not score generated-answer correctness.

Publication source SHA-256: `0c604264261f00d6e084fcb43bf6b3224786c3a96a611ee1ddaf6e2f0e5e360a`.

**Scope correction:** these historical Enterprise records contain titles without mapped document bodies. See the [ingestion audit](../enterprise-source-skills/ingestion-scope-20260907.md). Their original scores are preserved and are not full-text retrieval measurements.

[Enterprise evolution sweep and its separate development contract](../evolution/e6/README.md)
