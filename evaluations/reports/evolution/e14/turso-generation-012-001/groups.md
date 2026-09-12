# EnterpriseRAG E14: Turso generation 12 paired groups

Compare `versioned-011` with `versioned-007`. Values use a 0–100 scale and full-precision differences. Applications overlap; groups without retrieval references have unavailable quality. No application router is selected or tested.

## Application

| Group | Eligible | Retained nDCG | Candidate nDCG | Delta points | Candidate recall | Candidate MRR | Improved / regressed / tied |
| --- | --- | --- | --- | --- | --- | --- | --- |
| confluence | 39 | 69.99 | 70.16 | +0.17 | 78.51 | 75.22 | 9 / 5 / 25 |
| fireflies | 9 | 77.65 | 75.25 | -2.40 | 83.86 | 73.16 | 0 / 2 / 7 |
| github | 12 | 64.76 | 61.34 | -3.42 | 72.82 | 69.71 | 6 / 4 / 2 |
| gmail | 10 | 72.19 | 66.73 | -5.46 | 84.85 | 64.07 | 1 / 3 / 6 |
| google_drive | 14 | 76.29 | 77.97 | +1.68 | 87.07 | 81.77 | 5 / 0 / 9 |
| hubspot | 9 | 74.14 | 74.14 | +0.00 | 82.76 | 71.26 | 0 / 0 / 9 |
| jira | 26 | 79.77 | 80.72 | +0.95 | 85.37 | 85.55 | 7 / 4 / 15 |
| linear | 15 | 83.06 | 83.69 | +0.63 | 86.31 | 85.89 | 2 / 0 / 13 |
| slack | 24 | 56.20 | 56.72 | +0.52 | 69.42 | 56.57 | 3 / 3 / 18 |

## Category

| Group | Eligible | Retained nDCG | Candidate nDCG | Delta points | Candidate recall | Candidate MRR | Improved / regressed / tied |
| --- | --- | --- | --- | --- | --- | --- | --- |
| basic | 24 | 84.80 | 84.43 | -0.36 | 91.67 | 82.19 | 1 / 1 / 22 |
| completeness | 12 | 55.71 | 57.14 | +1.43 | 62.36 | 67.36 | 4 / 2 / 6 |
| conflicting_info | 4 | 100.00 | 100.00 | +0.00 | 100.00 | 100.00 | 0 / 0 / 4 |
| constrained | 8 | 87.84 | 86.93 | -0.91 | 93.75 | 91.67 | 1 / 1 / 6 |
| high_level | 0 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | 0 / 0 / 0 |
| info_not_found | 0 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | 0 / 0 / 0 |
| intra_document_reasoning | 12 | 100.00 | 100.00 | +0.00 | 100.00 | 100.00 | 0 / 0 / 12 |
| miscellaneous | 8 | 92.88 | 92.88 | +0.00 | 100.00 | 90.62 | 0 / 0 / 8 |
| project_related | 12 | 63.62 | 66.99 | +3.37 | 75.60 | 82.64 | 7 / 2 / 3 |
| semantic | 32 | 40.20 | 35.80 | -4.40 | 56.25 | 29.38 | 1 / 6 / 25 |

[Family result](README.md) · [CTA](cta.md) · [Full metrics](aggregate.json)
