# EnterpriseRAG E14: Adaptive generation 10 paired groups

Compare `versioned-009` with `retained-start`. Values use a 0–100 scale and full-precision differences. Applications overlap; groups without retrieval references have unavailable quality. No application router is selected or tested.

## Application

| Group | Eligible | Retained nDCG | Candidate nDCG | Delta points | Candidate recall | Candidate MRR | Improved / regressed / tied |
| --- | --- | --- | --- | --- | --- | --- | --- |
| confluence | 39 | 68.09 | 67.70 | -0.38 | 76.80 | 73.68 | 8 / 6 / 25 |
| fireflies | 9 | 69.60 | 69.60 | +0.00 | 70.09 | 72.73 | 0 / 0 / 9 |
| github | 12 | 62.71 | 62.90 | +0.19 | 73.83 | 70.30 | 3 / 4 / 5 |
| gmail | 10 | 71.15 | 71.00 | -0.15 | 71.38 | 75.77 | 1 / 1 / 8 |
| google_drive | 14 | 68.73 | 68.69 | -0.04 | 72.06 | 74.05 | 2 / 3 / 9 |
| hubspot | 9 | 59.97 | 59.97 | +0.00 | 65.52 | 58.33 | 0 / 0 / 9 |
| jira | 26 | 69.16 | 69.60 | +0.44 | 79.95 | 75.25 | 6 / 5 / 15 |
| linear | 15 | 81.33 | 81.32 | -0.01 | 84.70 | 84.20 | 1 / 1 / 13 |
| slack | 24 | 50.16 | 50.37 | +0.22 | 64.16 | 55.28 | 4 / 5 / 15 |

## Category

| Group | Eligible | Retained nDCG | Candidate nDCG | Delta points | Candidate recall | Candidate MRR | Improved / regressed / tied |
| --- | --- | --- | --- | --- | --- | --- | --- |
| basic | 24 | 84.72 | 84.72 | +0.00 | 87.50 | 83.93 | 0 / 0 / 24 |
| completeness | 12 | 62.90 | 61.29 | -1.61 | 66.81 | 67.36 | 1 / 2 / 9 |
| conflicting_info | 4 | 96.26 | 96.93 | +0.67 | 100.00 | 100.00 | 1 / 0 / 3 |
| constrained | 8 | 80.70 | 80.46 | -0.23 | 87.50 | 87.50 | 0 / 1 / 7 |
| high_level | 0 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | 0 / 0 / 0 |
| info_not_found | 0 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | 0 / 0 / 0 |
| intra_document_reasoning | 12 | 100.00 | 100.00 | +0.00 | 100.00 | 100.00 | 0 / 0 / 12 |
| miscellaneous | 8 | 87.50 | 82.89 | -4.61 | 87.50 | 81.25 | 0 / 1 / 7 |
| project_related | 12 | 60.27 | 62.02 | +1.75 | 71.67 | 83.33 | 6 / 4 / 2 |
| semantic | 32 | 20.22 | 19.95 | -0.26 | 40.62 | 14.06 | 2 / 3 / 27 |

[Family result](README.md) · [CTA](cta.md) · [Full metrics](aggregate.json)
