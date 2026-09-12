# EnterpriseRAG E14: Graphify generation 12 paired groups

Compare `versioned-012` with `versioned-010`. Values use a 0–100 scale and full-precision differences. Applications overlap; groups without retrieval references have unavailable quality. No application router is selected or tested.

## Application

| Group | Eligible | Retained nDCG | Candidate nDCG | Delta points | Candidate recall | Candidate MRR | Improved / regressed / tied |
| --- | --- | --- | --- | --- | --- | --- | --- |
| confluence | 39 | 62.75 | 55.84 | -6.90 | 75.66 | 58.44 | 3 / 26 / 10 |
| fireflies | 9 | 70.91 | 65.36 | -5.55 | 79.84 | 62.66 | 0 / 5 / 4 |
| github | 12 | 68.25 | 53.43 | -14.83 | 72.19 | 62.84 | 1 / 8 / 3 |
| gmail | 10 | 68.59 | 55.70 | -12.89 | 79.55 | 51.97 | 0 / 7 / 3 |
| google_drive | 14 | 82.82 | 72.24 | -10.57 | 83.10 | 76.65 | 0 / 8 / 6 |
| hubspot | 9 | 70.96 | 60.96 | -10.00 | 82.76 | 53.93 | 0 / 3 / 6 |
| jira | 26 | 67.92 | 57.83 | -10.08 | 75.59 | 59.14 | 2 / 16 / 8 |
| linear | 15 | 65.23 | 60.16 | -5.07 | 82.29 | 57.42 | 0 / 6 / 9 |
| slack | 24 | 46.88 | 34.15 | -12.73 | 56.25 | 35.15 | 2 / 17 / 5 |

## Category

| Group | Eligible | Retained nDCG | Candidate nDCG | Delta points | Candidate recall | Candidate MRR | Improved / regressed / tied |
| --- | --- | --- | --- | --- | --- | --- | --- |
| basic | 24 | 75.65 | 68.76 | -6.89 | 91.67 | 61.53 | 1 / 8 / 15 |
| completeness | 12 | 52.02 | 44.66 | -7.36 | 49.10 | 54.51 | 3 / 9 / 0 |
| conflicting_info | 4 | 87.53 | 73.54 | -13.99 | 100.00 | 61.90 | 0 / 2 / 2 |
| constrained | 8 | 66.53 | 52.19 | -14.35 | 68.75 | 54.58 | 0 / 5 / 3 |
| high_level | 0 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | 0 / 0 / 0 |
| info_not_found | 0 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | 0 / 0 / 0 |
| intra_document_reasoning | 12 | 88.01 | 69.93 | -18.08 | 100.00 | 60.28 | 0 / 7 / 5 |
| miscellaneous | 8 | 73.97 | 60.25 | -13.72 | 100.00 | 47.81 | 0 / 5 / 3 |
| project_related | 12 | 67.55 | 57.60 | -9.96 | 61.62 | 81.88 | 1 / 9 / 2 |
| semantic | 32 | 32.77 | 26.58 | -6.19 | 53.12 | 18.36 | 0 / 14 / 18 |

[Family result](README.md) · [CTA](cta.md) · [Full metrics](aggregate.json)
