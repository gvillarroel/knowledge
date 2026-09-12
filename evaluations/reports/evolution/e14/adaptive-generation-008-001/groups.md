# EnterpriseRAG E14: Adaptive generation 8 paired groups

Compare `versioned-007` with `retained-start`. Values use a 0–100 scale and full-precision differences. Applications overlap; groups without retrieval references have unavailable quality. No application router is selected or tested.

## Application

| Group | Eligible | Retained nDCG | Candidate nDCG | Delta points | Candidate recall | Candidate MRR | Improved / regressed / tied |
| --- | --- | --- | --- | --- | --- | --- | --- |
| confluence | 39 | 68.09 | 67.58 | -0.51 | 75.52 | 74.09 | 1 / 2 / 36 |
| fireflies | 9 | 69.60 | 69.63 | +0.03 | 70.09 | 72.73 | 1 / 0 / 8 |
| github | 12 | 62.71 | 62.81 | +0.10 | 71.31 | 73.14 | 1 / 0 / 11 |
| gmail | 10 | 71.15 | 63.98 | -7.17 | 71.38 | 66.02 | 1 / 1 / 8 |
| google_drive | 14 | 68.73 | 68.81 | +0.08 | 72.06 | 74.54 | 1 / 0 / 13 |
| hubspot | 9 | 59.97 | 59.77 | -0.20 | 65.52 | 58.13 | 0 / 1 / 8 |
| jira | 26 | 69.16 | 69.20 | +0.04 | 78.16 | 76.46 | 1 / 0 / 25 |
| linear | 15 | 81.33 | 80.67 | -0.65 | 83.10 | 84.20 | 0 / 1 / 14 |
| slack | 24 | 50.16 | 50.17 | +0.01 | 62.11 | 56.96 | 1 / 0 / 23 |

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
| project_related | 12 | 60.27 | 59.25 | -1.02 | 64.44 | 82.64 | 1 / 1 / 10 |
| semantic | 32 | 20.22 | 20.14 | -0.07 | 40.62 | 14.30 | 0 / 1 / 31 |

[Family result](README.md) · [CTA](cta.md) · [Full metrics](aggregate.json)
