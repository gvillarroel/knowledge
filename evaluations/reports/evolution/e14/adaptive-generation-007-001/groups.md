# EnterpriseRAG E14: Adaptive generation 7 paired groups

Compare `versioned-006` with `retained-start`. Values use a 0–100 scale and full-precision differences. Applications overlap; groups without retrieval references have unavailable quality. No application router is selected or tested.

## Application

| Group | Eligible | Retained nDCG | Candidate nDCG | Delta points | Candidate recall | Candidate MRR | Improved / regressed / tied |
| --- | --- | --- | --- | --- | --- | --- | --- |
| confluence | 39 | 68.09 | 52.62 | -15.47 | 68.97 | 53.28 | 6 / 23 / 10 |
| fireflies | 9 | 69.60 | 66.83 | -2.77 | 67.46 | 67.71 | 0 / 3 / 6 |
| github | 12 | 62.71 | 37.96 | -24.76 | 57.42 | 37.34 | 1 / 9 / 2 |
| gmail | 10 | 71.15 | 39.72 | -31.43 | 50.35 | 38.81 | 0 / 6 / 4 |
| google_drive | 14 | 68.73 | 53.71 | -15.02 | 65.45 | 51.80 | 1 / 8 / 5 |
| hubspot | 9 | 59.97 | 47.55 | -12.42 | 65.52 | 42.17 | 0 / 3 / 6 |
| jira | 26 | 69.16 | 55.77 | -13.39 | 60.27 | 59.45 | 2 / 14 / 10 |
| linear | 15 | 81.33 | 57.90 | -23.42 | 76.92 | 53.16 | 1 / 8 / 6 |
| slack | 24 | 50.16 | 26.75 | -23.41 | 38.71 | 28.06 | 1 / 15 / 8 |

## Category

| Group | Eligible | Retained nDCG | Candidate nDCG | Delta points | Candidate recall | Candidate MRR | Improved / regressed / tied |
| --- | --- | --- | --- | --- | --- | --- | --- |
| basic | 24 | 84.72 | 60.81 | -23.91 | 79.17 | 55.10 | 1 / 10 / 13 |
| completeness | 12 | 62.90 | 46.72 | -16.19 | 49.24 | 58.33 | 1 / 11 / 0 |
| conflicting_info | 4 | 96.26 | 67.64 | -28.62 | 87.50 | 61.25 | 0 / 2 / 2 |
| constrained | 8 | 80.70 | 78.83 | -1.86 | 87.50 | 85.42 | 2 / 1 / 5 |
| high_level | 0 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | 0 / 0 / 0 |
| info_not_found | 0 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | 0 / 0 / 0 |
| intra_document_reasoning | 12 | 100.00 | 82.28 | -17.72 | 100.00 | 76.67 | 0 / 4 / 8 |
| miscellaneous | 8 | 87.50 | 64.91 | -22.59 | 87.50 | 57.29 | 0 / 4 / 4 |
| project_related | 12 | 60.27 | 46.09 | -14.17 | 54.72 | 53.78 | 2 / 9 / 1 |
| semantic | 32 | 20.22 | 5.33 | -14.88 | 15.62 | 2.40 | 0 / 13 / 19 |

[Family result](README.md) · [CTA](cta.md) · [Full metrics](aggregate.json)
