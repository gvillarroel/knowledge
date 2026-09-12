# EnterpriseRAG E14: Turso generation 10 paired groups

Compare `versioned-009` with `versioned-007`. Values use a 0–100 scale and full-precision differences. Applications overlap; groups without retrieval references have unavailable quality. No application router is selected or tested.

## Application

| Group | Eligible | Retained nDCG | Candidate nDCG | Delta points | Candidate recall | Candidate MRR | Improved / regressed / tied |
| --- | --- | --- | --- | --- | --- | --- | --- |
| confluence | 39 | 69.99 | 69.53 | -0.46 | 78.79 | 73.32 | 6 / 12 / 21 |
| fireflies | 9 | 77.65 | 78.12 | +0.46 | 83.86 | 78.61 | 1 / 1 / 7 |
| github | 12 | 64.76 | 62.12 | -2.64 | 70.46 | 70.28 | 1 / 6 / 5 |
| gmail | 10 | 72.19 | 72.40 | +0.21 | 95.30 | 68.48 | 2 / 2 / 6 |
| google_drive | 14 | 76.29 | 73.64 | -2.65 | 84.92 | 75.99 | 0 / 5 / 9 |
| hubspot | 9 | 74.14 | 75.27 | +1.13 | 82.76 | 72.70 | 1 / 0 / 8 |
| jira | 26 | 79.77 | 77.51 | -2.27 | 84.14 | 83.24 | 4 / 10 / 12 |
| linear | 15 | 83.06 | 82.16 | -0.90 | 85.77 | 82.68 | 0 / 3 / 12 |
| slack | 24 | 56.20 | 55.93 | -0.27 | 69.19 | 55.52 | 4 / 7 / 13 |

## Category

| Group | Eligible | Retained nDCG | Candidate nDCG | Delta points | Candidate recall | Candidate MRR | Improved / regressed / tied |
| --- | --- | --- | --- | --- | --- | --- | --- |
| basic | 24 | 84.80 | 84.36 | -0.43 | 91.67 | 82.23 | 0 / 2 / 22 |
| completeness | 12 | 55.71 | 54.99 | -0.72 | 59.03 | 69.03 | 4 / 5 / 3 |
| conflicting_info | 4 | 100.00 | 100.00 | +0.00 | 100.00 | 100.00 | 0 / 0 / 4 |
| constrained | 8 | 87.84 | 90.15 | +2.31 | 100.00 | 93.75 | 1 / 0 / 7 |
| high_level | 0 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | 0 / 0 / 0 |
| info_not_found | 0 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | 0 / 0 / 0 |
| intra_document_reasoning | 12 | 100.00 | 100.00 | +0.00 | 100.00 | 100.00 | 0 / 0 / 12 |
| miscellaneous | 8 | 92.88 | 92.88 | +0.00 | 100.00 | 90.62 | 0 / 0 / 8 |
| project_related | 12 | 63.62 | 60.19 | -3.44 | 72.59 | 74.31 | 2 / 9 / 1 |
| semantic | 32 | 40.20 | 39.93 | -0.28 | 59.38 | 33.65 | 5 / 1 / 26 |

[Family result](README.md) · [CTA](cta.md) · [Full metrics](aggregate.json)
