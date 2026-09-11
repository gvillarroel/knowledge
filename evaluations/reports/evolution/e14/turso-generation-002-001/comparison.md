# EnterpriseRAG E14: updated retained profiles across six qualified families

This snapshot updates Turso to its qualified generation-two incumbent and preserves the other five previously published profiles. Entity Graph and Ensemble remain unqualified. Highest subgroup values describe this fixed comparison; no router, significance test or new optimizer selection was executed.

## All

| Group | Legacy | Turso | Adaptive | Embeddings | Classical | Graphify | Highest retained nDCG |
| --- | --- | --- | --- | --- | --- | --- | --- |
| all | 72.38 | 72.13 | 66.21 | 63.51 | 62.10 | 8.12 | legacy |

## Application

| Group | Legacy | Turso | Adaptive | Embeddings | Classical | Graphify | Highest retained nDCG |
| --- | --- | --- | --- | --- | --- | --- | --- |
| confluence | 69.99 | 69.87 | 68.09 | 70.99 | 60.05 | 9.82 | embeddings |
| fireflies | 77.65 | 77.65 | 69.60 | 56.10 | 78.91 | 4.75 | classical |
| github | 64.76 | 61.99 | 62.71 | 67.29 | 57.63 | 11.03 | embeddings |
| gmail | 72.19 | 72.70 | 71.15 | 49.64 | 50.07 | 16.88 | turso |
| google_drive | 76.29 | 74.96 | 68.73 | 66.33 | 62.33 | 17.72 | legacy |
| hubspot | 74.14 | 74.14 | 59.97 | 63.68 | 56.90 | 0.00 | legacy, turso |
| jira | 79.77 | 80.47 | 69.16 | 65.37 | 65.61 | 5.45 | turso |
| linear | 83.06 | 82.91 | 81.33 | 69.72 | 83.23 | 12.83 | classical |
| slack | 56.20 | 56.52 | 50.16 | 62.80 | 46.68 | 2.82 | embeddings |

## Category

| Group | Legacy | Turso | Adaptive | Embeddings | Classical | Graphify | Highest retained nDCG |
| --- | --- | --- | --- | --- | --- | --- | --- |
| basic | 84.80 | 84.67 | 84.72 | 71.54 | 79.17 | 10.13 | legacy |
| completeness | 55.71 | 58.41 | 62.90 | 52.20 | 31.00 | 16.69 | adaptive |
| conflicting_info | 100.00 | 97.99 | 96.26 | 78.30 | 90.33 | 18.72 | legacy |
| constrained | 87.84 | 88.18 | 80.70 | 86.92 | 71.46 | 6.05 | turso |
| high_level | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable |
| info_not_found | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable |
| intra_document_reasoning | 100.00 | 100.00 | 100.00 | 82.89 | 100.00 | 6.10 | adaptive, classical, legacy, turso |
| miscellaneous | 92.88 | 92.88 | 87.50 | 90.77 | 87.50 | 18.11 | legacy, turso |
| project_related | 63.62 | 63.93 | 60.27 | 71.66 | 54.96 | 9.44 | embeddings |
| semantic | 40.20 | 39.16 | 20.22 | 32.90 | 22.53 | 1.35 | legacy |

All values are nDCG@10 x100 on the same development workload. Application cohorts can overlap. Subgroups without retrieval references have unavailable scores. Full recall, MRR, coverage, weights and exact native rows are in [aggregate.json](aggregate.json).

[Turso gain and limits](README.md) · [Turso paired groups](groups.md) · [CTA](cta.md)
