# EnterpriseRAG E14: Adaptive generation 4 paired groups

Compare `versioned-003` with `retained-start`. Values use a 0–100 scale and full-precision differences. Applications overlap; groups without retrieval references have unavailable quality. No application router is selected or tested.

## Application

| Group | Eligible | Retained nDCG | Candidate nDCG | Delta points | Candidate recall | Candidate MRR | Improved / regressed / tied |
| --- | --- | --- | --- | --- | --- | --- | --- |
| confluence | 39 | 68.09 | 66.91 | -1.18 | 70.99 | 76.78 | 9 / 13 / 17 |
| fireflies | 9 | 69.60 | 68.29 | -1.31 | 69.09 | 68.71 | 0 / 2 / 7 |
| github | 12 | 62.71 | 62.34 | -0.37 | 70.67 | 75.19 | 3 / 4 / 5 |
| gmail | 10 | 71.15 | 59.29 | -11.86 | 71.73 | 60.17 | 1 / 3 / 6 |
| google_drive | 14 | 68.73 | 68.83 | +0.10 | 72.56 | 74.54 | 2 / 4 / 8 |
| hubspot | 9 | 59.97 | 62.95 | +2.98 | 74.14 | 59.70 | 1 / 1 / 7 |
| jira | 26 | 69.16 | 72.18 | +3.02 | 78.24 | 81.53 | 7 / 6 / 13 |
| linear | 15 | 81.33 | 84.71 | +3.39 | 83.90 | 88.71 | 2 / 2 / 11 |
| slack | 24 | 50.16 | 45.06 | -5.10 | 59.57 | 51.65 | 2 / 8 / 14 |

## Category

| Group | Eligible | Retained nDCG | Candidate nDCG | Delta points | Candidate recall | Candidate MRR | Improved / regressed / tied |
| --- | --- | --- | --- | --- | --- | --- | --- |
| basic | 24 | 84.72 | 80.45 | -4.28 | 87.50 | 78.33 | 0 / 3 / 21 |
| completeness | 12 | 62.90 | 60.09 | -2.82 | 62.36 | 77.36 | 4 / 6 / 2 |
| conflicting_info | 4 | 96.26 | 94.94 | -1.32 | 100.00 | 100.00 | 0 / 1 / 3 |
| constrained | 8 | 80.70 | 82.52 | +1.83 | 87.50 | 91.67 | 1 / 1 / 6 |
| high_level | 0 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | 0 / 0 / 0 |
| info_not_found | 0 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | 0 / 0 / 0 |
| intra_document_reasoning | 12 | 100.00 | 100.00 | +0.00 | 100.00 | 100.00 | 0 / 0 / 12 |
| miscellaneous | 8 | 87.50 | 87.50 | +0.00 | 87.50 | 87.50 | 0 / 0 / 8 |
| project_related | 12 | 60.27 | 56.73 | -3.54 | 59.77 | 84.03 | 4 / 7 / 1 |
| semantic | 32 | 20.22 | 24.97 | +4.76 | 40.62 | 20.32 | 6 / 4 / 22 |

[Family result](README.md) · [CTA](cta.md) · [Full metrics](aggregate.json)
