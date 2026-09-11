# EnterpriseRAG E14: Turso generation 4 paired groups

Compare `versioned-003` with `versioned-001`. Values use a 0–100 scale and full-precision differences. Applications overlap; groups without retrieval references have unavailable quality. No application router is selected or tested.

## Application

| Group | Eligible | Retained nDCG | Candidate nDCG | Delta points | Candidate recall | Candidate MRR | Improved / regressed / tied |
| --- | --- | --- | --- | --- | --- | --- | --- |
| confluence | 39 | 69.87 | 65.82 | -4.05 | 75.13 | 69.59 | 5 / 16 / 18 |
| fireflies | 9 | 77.65 | 80.43 | +2.78 | 80.47 | 84.48 | 2 / 2 / 5 |
| github | 12 | 61.99 | 48.20 | -13.79 | 57.21 | 54.87 | 1 / 9 / 2 |
| gmail | 10 | 72.70 | 65.36 | -7.34 | 80.54 | 61.38 | 1 / 5 / 4 |
| google_drive | 14 | 74.96 | 67.63 | -7.33 | 70.24 | 70.67 | 2 / 4 / 8 |
| hubspot | 9 | 74.14 | 62.05 | -12.09 | 82.76 | 55.32 | 0 / 3 / 6 |
| jira | 26 | 80.47 | 71.65 | -8.83 | 77.17 | 75.46 | 2 / 12 / 12 |
| linear | 15 | 82.91 | 80.73 | -2.19 | 85.24 | 82.54 | 0 / 4 / 11 |
| slack | 24 | 56.52 | 52.59 | -3.93 | 66.71 | 51.15 | 4 / 9 / 11 |

## Category

| Group | Eligible | Retained nDCG | Candidate nDCG | Delta points | Candidate recall | Candidate MRR | Improved / regressed / tied |
| --- | --- | --- | --- | --- | --- | --- | --- |
| basic | 24 | 84.67 | 81.51 | -3.16 | 87.50 | 79.63 | 0 / 3 / 21 |
| completeness | 12 | 58.41 | 35.02 | -23.40 | 34.31 | 55.98 | 1 / 11 / 0 |
| conflicting_info | 4 | 97.99 | 97.99 | +0.00 | 100.00 | 100.00 | 1 / 1 / 2 |
| constrained | 8 | 88.18 | 86.51 | -1.67 | 93.75 | 93.75 | 1 / 1 / 6 |
| high_level | 0 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | 0 / 0 / 0 |
| info_not_found | 0 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | 0 / 0 / 0 |
| intra_document_reasoning | 12 | 100.00 | 100.00 | +0.00 | 100.00 | 100.00 | 0 / 0 / 12 |
| miscellaneous | 8 | 92.88 | 93.75 | +0.87 | 100.00 | 91.67 | 1 / 0 / 7 |
| project_related | 12 | 63.93 | 55.66 | -8.27 | 68.19 | 65.28 | 3 / 8 / 1 |
| semantic | 32 | 39.16 | 30.21 | -8.95 | 50.00 | 23.96 | 3 / 9 / 20 |

[Family result](README.md) · [CTA](cta.md) · [Full metrics](aggregate.json)
