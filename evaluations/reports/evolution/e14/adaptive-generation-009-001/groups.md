# EnterpriseRAG E14: Adaptive generation 9 paired groups

Compare `versioned-008` with `retained-start`. Values use a 0–100 scale and full-precision differences. Applications overlap; groups without retrieval references have unavailable quality. No application router is selected or tested.

## Application

| Group | Eligible | Retained nDCG | Candidate nDCG | Delta points | Candidate recall | Candidate MRR | Improved / regressed / tied |
| --- | --- | --- | --- | --- | --- | --- | --- |
| confluence | 39 | 68.09 | 66.99 | -1.09 | 74.25 | 74.09 | 2 / 6 / 31 |
| fireflies | 9 | 69.60 | 69.63 | +0.03 | 70.09 | 72.73 | 1 / 0 / 8 |
| github | 12 | 62.71 | 62.52 | -0.19 | 71.31 | 73.14 | 1 / 2 / 9 |
| gmail | 10 | 71.15 | 64.26 | -6.90 | 71.38 | 66.02 | 2 / 1 / 7 |
| google_drive | 14 | 68.73 | 68.78 | +0.05 | 72.06 | 74.54 | 1 / 1 / 12 |
| hubspot | 9 | 59.97 | 59.77 | -0.20 | 65.52 | 58.13 | 0 / 1 / 8 |
| jira | 26 | 69.16 | 67.70 | -1.46 | 73.55 | 76.06 | 2 / 4 / 20 |
| linear | 15 | 81.33 | 80.67 | -0.65 | 83.10 | 84.20 | 0 / 1 / 14 |
| slack | 24 | 50.16 | 49.71 | -0.45 | 60.06 | 57.33 | 3 / 2 / 19 |

## Category

| Group | Eligible | Retained nDCG | Candidate nDCG | Delta points | Candidate recall | Candidate MRR | Improved / regressed / tied |
| --- | --- | --- | --- | --- | --- | --- | --- |
| basic | 24 | 84.72 | 83.18 | -1.54 | 87.50 | 81.85 | 0 / 1 / 23 |
| completeness | 12 | 62.90 | 62.95 | +0.05 | 66.81 | 75.00 | 1 / 0 / 11 |
| conflicting_info | 4 | 96.26 | 96.26 | +0.00 | 100.00 | 100.00 | 0 / 0 / 4 |
| constrained | 8 | 80.70 | 79.69 | -1.00 | 87.50 | 85.42 | 0 / 1 / 7 |
| high_level | 0 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | 0 / 0 / 0 |
| info_not_found | 0 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | 0 / 0 / 0 |
| intra_document_reasoning | 12 | 100.00 | 100.00 | +0.00 | 100.00 | 100.00 | 0 / 0 / 12 |
| miscellaneous | 8 | 87.50 | 87.50 | +0.00 | 87.50 | 87.50 | 0 / 0 / 8 |
| project_related | 12 | 60.27 | 57.20 | -3.07 | 60.00 | 82.64 | 2 / 5 / 5 |
| semantic | 32 | 20.22 | 19.47 | -0.74 | 37.50 | 14.24 | 1 / 2 / 29 |

[Family result](README.md) · [CTA](cta.md) · [Full metrics](aggregate.json)
