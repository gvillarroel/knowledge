# EnterpriseRAG E14: Turso generation 9 paired groups

Compare `versioned-008` with `versioned-007`. Values use a 0–100 scale and full-precision differences. Applications overlap; groups without retrieval references have unavailable quality. No application router is selected or tested.

## Application

| Group | Eligible | Retained nDCG | Candidate nDCG | Delta points | Candidate recall | Candidate MRR | Improved / regressed / tied |
| --- | --- | --- | --- | --- | --- | --- | --- |
| confluence | 39 | 69.99 | 70.24 | +0.24 | 78.51 | 74.48 | 1 / 5 / 33 |
| fireflies | 9 | 77.65 | 78.10 | +0.44 | 83.86 | 78.61 | 1 / 1 / 7 |
| github | 12 | 64.76 | 64.58 | -0.18 | 73.20 | 72.96 | 1 / 2 / 9 |
| gmail | 10 | 72.19 | 69.15 | -3.04 | 84.85 | 67.18 | 0 / 2 / 8 |
| google_drive | 14 | 76.29 | 75.89 | -0.40 | 87.07 | 77.71 | 0 / 1 / 13 |
| hubspot | 9 | 74.14 | 74.14 | +0.00 | 82.76 | 71.26 | 0 / 0 / 9 |
| jira | 26 | 79.77 | 80.07 | +0.30 | 85.26 | 85.77 | 1 / 5 / 20 |
| linear | 15 | 83.06 | 83.03 | -0.03 | 86.31 | 83.48 | 0 / 1 / 14 |
| slack | 24 | 56.20 | 56.45 | +0.25 | 69.62 | 55.22 | 1 / 3 / 20 |

## Category

| Group | Eligible | Retained nDCG | Candidate nDCG | Delta points | Candidate recall | Candidate MRR | Improved / regressed / tied |
| --- | --- | --- | --- | --- | --- | --- | --- |
| basic | 24 | 84.80 | 84.67 | -0.13 | 91.67 | 82.54 | 0 / 1 / 23 |
| completeness | 12 | 55.71 | 56.11 | +0.40 | 61.81 | 67.50 | 1 / 5 / 6 |
| conflicting_info | 4 | 100.00 | 100.00 | +0.00 | 100.00 | 100.00 | 0 / 0 / 4 |
| constrained | 8 | 87.84 | 87.84 | +0.00 | 93.75 | 93.75 | 0 / 0 / 8 |
| high_level | 0 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | 0 / 0 / 0 |
| info_not_found | 0 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | 0 / 0 / 0 |
| intra_document_reasoning | 12 | 100.00 | 100.00 | +0.00 | 100.00 | 100.00 | 0 / 0 / 12 |
| miscellaneous | 8 | 92.88 | 92.88 | +0.00 | 100.00 | 90.62 | 0 / 0 / 8 |
| project_related | 12 | 63.62 | 64.58 | +0.96 | 75.60 | 78.47 | 1 / 2 / 9 |
| semantic | 32 | 40.20 | 39.05 | -1.15 | 56.25 | 33.55 | 1 / 3 / 28 |

[Family result](README.md) · [CTA](cta.md) · [Full metrics](aggregate.json)
