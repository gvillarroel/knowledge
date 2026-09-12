# EnterpriseRAG E14: Turso generation 11 paired groups

Compare `versioned-010` with `versioned-007`. Values use a 0–100 scale and full-precision differences. Applications overlap; groups without retrieval references have unavailable quality. No application router is selected or tested.

## Application

| Group | Eligible | Retained nDCG | Candidate nDCG | Delta points | Candidate recall | Candidate MRR | Improved / regressed / tied |
| --- | --- | --- | --- | --- | --- | --- | --- |
| confluence | 39 | 69.99 | 63.81 | -6.18 | 73.95 | 68.54 | 4 / 19 / 16 |
| fireflies | 9 | 77.65 | 78.52 | +0.86 | 84.48 | 78.61 | 1 / 1 / 7 |
| github | 12 | 64.76 | 59.27 | -5.50 | 68.36 | 65.86 | 2 / 5 / 5 |
| gmail | 10 | 72.19 | 71.18 | -1.01 | 94.55 | 68.80 | 1 / 4 / 5 |
| google_drive | 14 | 76.29 | 66.44 | -9.85 | 69.25 | 70.57 | 0 / 7 / 7 |
| hubspot | 9 | 74.14 | 76.40 | +2.26 | 82.76 | 74.14 | 2 / 0 / 7 |
| jira | 26 | 79.77 | 73.60 | -6.17 | 83.02 | 79.38 | 4 / 11 / 11 |
| linear | 15 | 83.06 | 80.34 | -2.72 | 83.63 | 81.74 | 0 / 4 / 11 |
| slack | 24 | 56.20 | 54.73 | -1.47 | 67.16 | 57.64 | 3 / 8 / 13 |

## Category

| Group | Eligible | Retained nDCG | Candidate nDCG | Delta points | Candidate recall | Candidate MRR | Improved / regressed / tied |
| --- | --- | --- | --- | --- | --- | --- | --- |
| basic | 24 | 84.80 | 81.51 | -3.28 | 87.50 | 79.63 | 0 / 3 / 21 |
| completeness | 12 | 55.71 | 45.90 | -9.81 | 50.00 | 65.36 | 2 / 9 / 1 |
| conflicting_info | 4 | 100.00 | 97.99 | -2.01 | 100.00 | 100.00 | 0 / 1 / 3 |
| constrained | 8 | 87.84 | 85.77 | -2.08 | 93.75 | 87.50 | 1 / 1 / 6 |
| high_level | 0 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | 0 / 0 / 0 |
| info_not_found | 0 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | 0 / 0 / 0 |
| intra_document_reasoning | 12 | 100.00 | 100.00 | +0.00 | 100.00 | 100.00 | 0 / 0 / 12 |
| miscellaneous | 8 | 92.88 | 92.88 | +0.00 | 100.00 | 90.62 | 0 / 0 / 8 |
| project_related | 12 | 63.62 | 55.13 | -8.49 | 64.72 | 72.92 | 2 / 9 / 1 |
| semantic | 32 | 40.20 | 38.10 | -2.10 | 59.38 | 31.25 | 6 / 4 / 22 |

[Family result](README.md) · [CTA](cta.md) · [Full metrics](aggregate.json)
