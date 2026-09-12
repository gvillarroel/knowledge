# EnterpriseRAG E14: Graphify generation 19 paired groups

Compare `versioned-019` with `versioned-016`. Values use a 0–100 scale and full-precision differences. Applications overlap; groups without retrieval references have unavailable quality. No application router is selected or tested.

## Application

| Group | Eligible | Retained nDCG | Candidate nDCG | Delta points | Candidate recall | Candidate MRR | Improved / regressed / tied |
| --- | --- | --- | --- | --- | --- | --- | --- |
| confluence | 39 | 62.87 | 36.70 | -26.17 | 36.52 | 48.43 | 2 / 30 / 7 |
| fireflies | 9 | 70.91 | 54.19 | -16.73 | 53.42 | 56.43 | 0 / 5 / 4 |
| github | 12 | 68.16 | 35.64 | -32.52 | 35.34 | 54.32 | 1 / 9 / 2 |
| gmail | 10 | 68.59 | 35.27 | -33.32 | 52.53 | 35.24 | 0 / 8 / 2 |
| google_drive | 14 | 82.74 | 61.95 | -20.80 | 63.92 | 72.93 | 0 / 9 / 5 |
| hubspot | 9 | 70.96 | 32.18 | -38.77 | 32.18 | 32.18 | 0 / 5 / 4 |
| jira | 26 | 68.97 | 38.07 | -30.90 | 36.99 | 47.92 | 2 / 19 / 5 |
| linear | 15 | 65.23 | 32.64 | -32.58 | 41.69 | 36.49 | 0 / 11 / 4 |
| slack | 24 | 47.11 | 13.33 | -33.78 | 12.90 | 24.00 | 1 / 19 / 4 |

## Category

| Group | Eligible | Retained nDCG | Candidate nDCG | Delta points | Candidate recall | Candidate MRR | Improved / regressed / tied |
| --- | --- | --- | --- | --- | --- | --- | --- |
| basic | 24 | 75.65 | 47.47 | -28.18 | 54.17 | 45.14 | 1 / 13 / 10 |
| completeness | 12 | 52.02 | 32.64 | -19.38 | 29.17 | 47.22 | 3 / 9 / 0 |
| conflicting_info | 4 | 87.53 | 50.00 | -37.53 | 50.00 | 50.00 | 0 / 2 / 2 |
| constrained | 8 | 70.15 | 25.00 | -45.15 | 25.00 | 31.25 | 0 / 7 / 1 |
| high_level | 0 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | 0 / 0 / 0 |
| info_not_found | 0 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | 0 / 0 / 0 |
| intra_document_reasoning | 12 | 88.01 | 45.83 | -42.18 | 50.00 | 44.44 | 0 / 7 / 5 |
| miscellaneous | 8 | 73.97 | 45.39 | -28.59 | 62.50 | 39.58 | 0 / 6 / 2 |
| project_related | 12 | 67.96 | 44.63 | -23.33 | 40.51 | 79.17 | 0 / 12 / 0 |
| semantic | 32 | 32.77 | 6.25 | -26.52 | 9.38 | 5.21 | 0 / 17 / 15 |

[Family result](README.md) · [CTA](cta.md) · [Full metrics](aggregate.json)
