# EnterpriseRAG E14: Graphify generation 21 paired groups

Compare `versioned-021` with `versioned-016`. Values use a 0–100 scale and full-precision differences. Applications overlap; groups without retrieval references have unavailable quality. No application router is selected or tested.

## Application

| Group | Eligible | Retained nDCG | Candidate nDCG | Delta points | Candidate recall | Candidate MRR | Improved / regressed / tied |
| --- | --- | --- | --- | --- | --- | --- | --- |
| confluence | 39 | 62.87 | 57.42 | -5.44 | 74.29 | 59.32 | 4 / 21 / 14 |
| fireflies | 9 | 70.91 | 69.14 | -1.77 | 83.86 | 64.86 | 0 / 4 / 5 |
| github | 12 | 68.16 | 59.39 | -8.77 | 77.79 | 67.35 | 3 / 6 / 3 |
| gmail | 10 | 68.59 | 63.18 | -5.41 | 94.55 | 55.15 | 0 / 5 / 5 |
| google_drive | 14 | 82.74 | 80.14 | -2.60 | 85.42 | 85.58 | 1 / 6 / 7 |
| hubspot | 9 | 70.96 | 64.42 | -6.54 | 82.76 | 58.19 | 0 / 2 / 7 |
| jira | 26 | 68.97 | 60.90 | -8.06 | 83.21 | 59.92 | 3 / 14 / 9 |
| linear | 15 | 65.23 | 62.24 | -2.99 | 84.17 | 58.57 | 0 / 5 / 10 |
| slack | 24 | 47.11 | 40.45 | -6.66 | 68.29 | 38.18 | 2 / 14 / 8 |

## Category

| Group | Eligible | Retained nDCG | Candidate nDCG | Delta points | Candidate recall | Candidate MRR | Improved / regressed / tied |
| --- | --- | --- | --- | --- | --- | --- | --- |
| basic | 24 | 75.65 | 69.12 | -6.53 | 91.67 | 62.02 | 0 / 7 / 17 |
| completeness | 12 | 52.02 | 47.76 | -4.26 | 54.65 | 57.29 | 2 / 7 / 3 |
| conflicting_info | 4 | 87.53 | 86.39 | -1.14 | 100.00 | 80.00 | 0 / 1 / 3 |
| constrained | 8 | 70.15 | 55.08 | -15.06 | 75.00 | 53.12 | 0 / 6 / 2 |
| high_level | 0 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | 0 / 0 / 0 |
| info_not_found | 0 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | 0 / 0 / 0 |
| intra_document_reasoning | 12 | 88.01 | 71.63 | -16.39 | 100.00 | 62.43 | 0 / 7 / 5 |
| miscellaneous | 8 | 73.97 | 66.73 | -7.24 | 100.00 | 56.37 | 0 / 4 / 4 |
| project_related | 12 | 67.96 | 64.17 | -3.79 | 73.01 | 83.33 | 3 / 7 / 2 |
| semantic | 32 | 32.77 | 31.08 | -1.69 | 59.38 | 22.09 | 0 / 7 / 25 |

[Family result](README.md) · [CTA](cta.md) · [Full metrics](aggregate.json)
