# EnterpriseRAG E14: retained profiles across six qualified families

This snapshot updates Graphify to its qualified generation-10 incumbent and preserves the other five previously published profiles. Entity Graph and Ensemble remain unqualified. Highest subgroup values describe this fixed comparison; no router, significance test or new optimizer selection was executed.

## All

| Group | Legacy | Turso | Adaptive | Embeddings | Classical | Graphify | Highest retained nDCG |
| --- | --- | --- | --- | --- | --- | --- | --- |
| all | 72.38 | 72.38 | 66.21 | 63.51 | 62.10 | 63.46 | Legacy, Turso |

## Application

| Group | Legacy | Turso | Adaptive | Embeddings | Classical | Graphify | Highest retained nDCG |
| --- | --- | --- | --- | --- | --- | --- | --- |
| confluence | 69.99 | 69.99 | 68.09 | 70.99 | 60.05 | 62.75 | Embeddings |
| fireflies | 77.65 | 77.65 | 69.60 | 56.10 | 78.91 | 70.91 | Classical |
| github | 64.76 | 64.76 | 62.71 | 67.29 | 57.63 | 68.25 | Graphify |
| gmail | 72.19 | 72.19 | 71.15 | 49.64 | 50.07 | 68.59 | Legacy, Turso |
| google_drive | 76.29 | 76.29 | 68.73 | 66.33 | 62.33 | 82.82 | Graphify |
| hubspot | 74.14 | 74.14 | 59.97 | 63.68 | 56.90 | 70.96 | Legacy, Turso |
| jira | 79.77 | 79.77 | 69.16 | 65.37 | 65.61 | 67.92 | Legacy, Turso |
| linear | 83.06 | 83.06 | 81.33 | 69.72 | 83.23 | 65.23 | Classical |
| slack | 56.20 | 56.20 | 50.16 | 62.80 | 46.68 | 46.88 | Embeddings |

## Category

| Group | Legacy | Turso | Adaptive | Embeddings | Classical | Graphify | Highest retained nDCG |
| --- | --- | --- | --- | --- | --- | --- | --- |
| basic | 84.80 | 84.80 | 84.72 | 71.54 | 79.17 | 75.65 | Legacy, Turso |
| completeness | 55.71 | 55.71 | 62.90 | 52.20 | 31.00 | 52.02 | Adaptive |
| conflicting_info | 100.00 | 100.00 | 96.26 | 78.30 | 90.33 | 87.53 | Legacy, Turso |
| constrained | 87.84 | 87.84 | 80.70 | 86.92 | 71.46 | 66.53 | Legacy, Turso |
| high_level | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable |
| info_not_found | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable |
| intra_document_reasoning | 100.00 | 100.00 | 100.00 | 82.89 | 100.00 | 88.01 | Adaptive, Classical, Legacy, Turso |
| miscellaneous | 92.88 | 92.88 | 87.50 | 90.77 | 87.50 | 73.97 | Legacy, Turso |
| project_related | 63.62 | 63.62 | 60.27 | 71.66 | 54.96 | 67.55 | Embeddings |
| semantic | 40.20 | 40.20 | 20.22 | 32.90 | 22.53 | 32.77 | Legacy, Turso |

All values are nDCG@10 x100 on the same 120-question development workload. Application cohorts overlap. Subgroups without retrieval references have unavailable scores. Full recall, MRR, coverage, weights and exact native records are in [aggregate.json](aggregate.json).

[Gain and limits](README.md) · [Paired groups](groups.md) · [CTA](cta.md)
