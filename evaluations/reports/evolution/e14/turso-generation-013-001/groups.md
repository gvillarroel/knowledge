# EnterpriseRAG E14: Turso generation 13 paired groups

Compare `versioned-012` with `versioned-007`. Values use a 0–100 scale and full-precision differences. Applications overlap; groups without retrieval references have unavailable quality. No application router is selected or tested.

## Application

| Group | Eligible | Retained nDCG | Candidate nDCG | Delta points | Candidate recall | Candidate MRR | Improved / regressed / tied |
| --- | --- | --- | --- | --- | --- | --- | --- |
| confluence | 39 | 69.99 | 66.30 | -3.70 | 75.33 | 69.58 | 5 / 15 / 19 |
| fireflies | 9 | 77.65 | 80.24 | +2.58 | 80.47 | 84.48 | 2 / 2 / 5 |
| github | 12 | 64.76 | 49.51 | -15.26 | 57.21 | 56.35 | 1 / 9 / 2 |
| gmail | 10 | 72.19 | 65.60 | -6.59 | 81.28 | 61.38 | 1 / 5 / 4 |
| google_drive | 14 | 76.29 | 67.68 | -8.61 | 70.24 | 70.67 | 1 / 4 / 9 |
| hubspot | 9 | 74.14 | 62.05 | -12.09 | 82.76 | 55.32 | 0 / 3 / 6 |
| jira | 26 | 79.77 | 70.41 | -9.36 | 77.45 | 73.56 | 2 / 13 / 11 |
| linear | 15 | 83.06 | 80.73 | -2.33 | 85.24 | 82.54 | 0 / 4 / 11 |
| slack | 24 | 56.20 | 52.33 | -3.87 | 67.03 | 50.77 | 3 / 10 / 11 |

## Category

| Group | Eligible | Retained nDCG | Candidate nDCG | Delta points | Candidate recall | Candidate MRR | Improved / regressed / tied |
| --- | --- | --- | --- | --- | --- | --- | --- |
| basic | 24 | 84.80 | 81.51 | -3.28 | 87.50 | 79.63 | 0 / 3 / 21 |
| completeness | 12 | 55.71 | 35.34 | -20.37 | 35.69 | 55.87 | 1 / 11 / 0 |
| conflicting_info | 4 | 100.00 | 97.99 | -2.01 | 100.00 | 100.00 | 0 / 1 / 3 |
| constrained | 8 | 87.84 | 88.38 | +0.54 | 93.75 | 93.75 | 2 / 0 / 6 |
| high_level | 0 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | 0 / 0 / 0 |
| info_not_found | 0 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | 0 / 0 / 0 |
| intra_document_reasoning | 12 | 100.00 | 100.00 | +0.00 | 100.00 | 100.00 | 0 / 0 / 12 |
| miscellaneous | 8 | 92.88 | 92.34 | -0.55 | 100.00 | 90.00 | 0 / 1 / 7 |
| project_related | 12 | 63.62 | 55.74 | -7.88 | 68.19 | 65.28 | 3 / 8 / 1 |
| semantic | 32 | 40.20 | 29.52 | -10.68 | 50.00 | 22.97 | 3 / 10 / 19 |

[Family result](README.md) · [CTA](cta.md) · [Full metrics](aggregate.json)
