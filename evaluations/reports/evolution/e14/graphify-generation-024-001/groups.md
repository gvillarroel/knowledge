# EnterpriseRAG E14: Graphify generation 24 paired groups

Compare `versioned-024` with `versioned-016`. Values use a 0–100 scale and full-precision differences. Applications overlap; groups without retrieval references have unavailable quality. No application router is selected or tested.

## Application

| Group | Eligible | Retained nDCG | Candidate nDCG | Delta points | Candidate recall | Candidate MRR | Improved / regressed / tied |
| --- | --- | --- | --- | --- | --- | --- | --- |
| confluence | 39 | 62.87 | 54.21 | -8.65 | 76.60 | 56.63 | 5 / 26 / 8 |
| fireflies | 9 | 70.91 | 64.30 | -6.62 | 78.84 | 62.15 | 0 / 5 / 4 |
| github | 12 | 68.16 | 51.51 | -16.65 | 70.30 | 61.90 | 2 / 8 / 2 |
| gmail | 10 | 68.59 | 55.01 | -13.58 | 78.66 | 51.86 | 0 / 7 / 3 |
| google_drive | 14 | 82.74 | 71.10 | -11.64 | 81.61 | 76.54 | 1 / 8 / 5 |
| hubspot | 9 | 70.96 | 54.65 | -16.30 | 82.76 | 45.91 | 0 / 5 / 4 |
| jira | 26 | 68.97 | 54.79 | -14.18 | 74.75 | 56.24 | 3 / 18 / 5 |
| linear | 15 | 65.23 | 57.56 | -7.67 | 82.29 | 55.22 | 0 / 9 / 6 |
| slack | 24 | 47.11 | 32.69 | -14.42 | 55.86 | 34.11 | 2 / 17 / 5 |

## Category

| Group | Eligible | Retained nDCG | Candidate nDCG | Delta points | Candidate recall | Candidate MRR | Improved / regressed / tied |
| --- | --- | --- | --- | --- | --- | --- | --- |
| basic | 24 | 75.65 | 67.09 | -8.56 | 91.67 | 59.52 | 1 / 10 / 13 |
| completeness | 12 | 52.02 | 44.34 | -7.69 | 48.82 | 55.50 | 4 / 8 / 0 |
| conflicting_info | 4 | 87.53 | 73.54 | -13.99 | 100.00 | 61.90 | 0 / 2 / 2 |
| constrained | 8 | 70.15 | 51.34 | -18.81 | 75.00 | 50.12 | 0 / 6 / 2 |
| high_level | 0 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | 0 / 0 / 0 |
| info_not_found | 0 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | 0 / 0 / 0 |
| intra_document_reasoning | 12 | 88.01 | 68.13 | -19.89 | 100.00 | 58.15 | 0 / 7 / 5 |
| miscellaneous | 8 | 73.97 | 59.97 | -14.00 | 100.00 | 47.51 | 0 / 5 / 3 |
| project_related | 12 | 67.96 | 54.71 | -13.25 | 59.54 | 81.25 | 2 / 10 / 0 |
| semantic | 32 | 32.77 | 23.10 | -9.67 | 53.12 | 14.07 | 0 / 17 / 15 |

[Family result](README.md) · [CTA](cta.md) · [Full metrics](aggregate.json)
