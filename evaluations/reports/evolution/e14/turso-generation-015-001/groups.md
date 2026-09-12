# EnterpriseRAG E14: Turso generation 15 paired groups

Compare `versioned-014` with `versioned-007`. Values use a 0–100 scale and full-precision differences. Applications overlap; groups without retrieval references have unavailable quality. No application router is selected or tested.

## Application

| Group | Eligible | Retained nDCG | Candidate nDCG | Delta points | Candidate recall | Candidate MRR | Improved / regressed / tied |
| --- | --- | --- | --- | --- | --- | --- | --- |
| confluence | 39 | 69.99 | 68.00 | -1.99 | 77.46 | 69.90 | 2 / 16 / 21 |
| fireflies | 9 | 77.65 | 77.92 | +0.27 | 83.48 | 78.61 | 1 / 2 / 6 |
| github | 12 | 64.76 | 55.99 | -8.77 | 71.98 | 58.09 | 1 / 8 / 3 |
| gmail | 10 | 72.19 | 70.74 | -1.45 | 94.40 | 63.91 | 1 / 4 / 5 |
| google_drive | 14 | 76.29 | 69.62 | -6.67 | 72.89 | 71.81 | 1 / 5 / 8 |
| hubspot | 9 | 74.14 | 74.14 | +0.00 | 82.76 | 71.26 | 0 / 0 / 9 |
| jira | 26 | 79.77 | 74.86 | -4.91 | 80.25 | 77.54 | 1 / 13 / 12 |
| linear | 15 | 83.06 | 82.35 | -0.71 | 85.77 | 83.48 | 0 / 3 / 12 |
| slack | 24 | 56.20 | 53.78 | -2.42 | 68.61 | 51.10 | 3 / 10 / 11 |

## Category

| Group | Eligible | Retained nDCG | Candidate nDCG | Delta points | Candidate recall | Candidate MRR | Improved / regressed / tied |
| --- | --- | --- | --- | --- | --- | --- | --- |
| basic | 24 | 84.80 | 83.18 | -1.61 | 87.50 | 81.85 | 0 / 1 / 23 |
| completeness | 12 | 55.71 | 47.73 | -7.98 | 53.75 | 59.72 | 1 / 11 / 0 |
| conflicting_info | 4 | 100.00 | 100.00 | +0.00 | 100.00 | 100.00 | 0 / 0 / 4 |
| constrained | 8 | 87.84 | 87.84 | +0.00 | 93.75 | 93.75 | 0 / 0 / 8 |
| high_level | 0 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | 0 / 0 / 0 |
| info_not_found | 0 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | 0 / 0 / 0 |
| intra_document_reasoning | 12 | 100.00 | 100.00 | +0.00 | 100.00 | 100.00 | 0 / 0 / 12 |
| miscellaneous | 8 | 92.88 | 93.75 | +0.87 | 100.00 | 91.67 | 1 / 0 / 7 |
| project_related | 12 | 63.62 | 59.37 | -4.26 | 74.68 | 65.28 | 2 / 9 / 1 |
| semantic | 32 | 40.20 | 34.98 | -5.23 | 56.25 | 28.18 | 2 / 5 / 25 |

[Family result](README.md) · [CTA](cta.md) · [Full metrics](aggregate.json)
