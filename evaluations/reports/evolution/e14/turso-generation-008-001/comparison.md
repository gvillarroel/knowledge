# EnterpriseRAG E14: retained profiles across six qualified families

This snapshot updates Turso to its qualified generation-8 incumbent and preserves the other five previously published profiles. Entity Graph and Ensemble remain unqualified. Highest subgroup values describe this fixed comparison; no router, significance test or new optimizer selection was executed.

## All

Legacy and Turso tie at full precision in the overall metric and in all four retrieval metrics across the 18 groups with references. The remaining two groups have unavailable metrics for both. This snapshot preserves their separate native observations and CTA measurements.

| Group | Legacy | Turso | Adaptive | Embeddings | Classical | Graphify | Highest retained nDCG |
| --- | --- | --- | --- | --- | --- | --- | --- |
| all | 72.38 | 72.38 | 66.21 | 63.51 | 62.10 | 27.90 | Legacy, Turso |

## Application

| Group | Legacy | Turso | Adaptive | Embeddings | Classical | Graphify | Highest retained nDCG |
| --- | --- | --- | --- | --- | --- | --- | --- |
| confluence | 69.99 | 69.99 | 68.09 | 70.99 | 60.05 | 28.07 | Embeddings |
| fireflies | 77.65 | 77.65 | 69.60 | 56.10 | 78.91 | 49.35 | Classical |
| github | 64.76 | 64.76 | 62.71 | 67.29 | 57.63 | 24.03 | Embeddings |
| gmail | 72.19 | 72.19 | 71.15 | 49.64 | 50.07 | 21.69 | Legacy, Turso |
| google_drive | 76.29 | 76.29 | 68.73 | 66.33 | 62.33 | 57.01 | Legacy, Turso |
| hubspot | 74.14 | 74.14 | 59.97 | 63.68 | 56.90 | 32.18 | Legacy, Turso |
| jira | 79.77 | 79.77 | 69.16 | 65.37 | 65.61 | 30.72 | Legacy, Turso |
| linear | 83.06 | 83.06 | 81.33 | 69.72 | 83.23 | 23.85 | Classical |
| slack | 56.20 | 56.20 | 50.16 | 62.80 | 46.68 | 8.92 | Embeddings |

## Category

| Group | Legacy | Turso | Adaptive | Embeddings | Classical | Graphify | Highest retained nDCG |
| --- | --- | --- | --- | --- | --- | --- | --- |
| basic | 84.80 | 84.80 | 84.72 | 71.54 | 79.17 | 42.18 | Legacy, Turso |
| completeness | 55.71 | 55.71 | 62.90 | 52.20 | 31.00 | 26.69 | Adaptive |
| conflicting_info | 100.00 | 100.00 | 96.26 | 78.30 | 90.33 | 50.00 | Legacy, Turso |
| constrained | 87.84 | 87.84 | 80.70 | 86.92 | 71.46 | 17.45 | Legacy, Turso |
| high_level | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable |
| info_not_found | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable |
| intra_document_reasoning | 100.00 | 100.00 | 100.00 | 82.89 | 100.00 | 39.33 | Adaptive, Classical, Legacy, Turso |
| miscellaneous | 92.88 | 92.88 | 87.50 | 90.77 | 87.50 | 27.66 | Legacy, Turso |
| project_related | 63.62 | 63.62 | 60.27 | 71.66 | 54.96 | 30.75 | Embeddings |
| semantic | 40.20 | 40.20 | 20.22 | 32.90 | 22.53 | 2.55 | Legacy, Turso |

All values are nDCG@10 x100 on the same 120-question development workload. Application cohorts overlap. Subgroups without retrieval references have unavailable scores. Full recall, MRR, coverage, weights and exact native records are in [aggregate.json](aggregate.json).

[Gain and limits](README.md) · [Paired groups](groups.md) · [CTA](cta.md)
