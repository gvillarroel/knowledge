# EnterpriseRAG E14: Turso generation 14 paired groups

Compare `versioned-013` with `versioned-007`. Values use a 0–100 scale and full-precision differences. Applications overlap; groups without retrieval references have unavailable quality. No application router is selected or tested.

## Application

| Group | Eligible | Retained nDCG | Candidate nDCG | Delta points | Candidate recall | Candidate MRR | Improved / regressed / tied |
| --- | --- | --- | --- | --- | --- | --- | --- |
| confluence | 39 | 69.99 | 63.18 | -6.82 | 71.27 | 69.29 | 6 / 20 / 13 |
| fireflies | 9 | 77.65 | 79.15 | +1.49 | 78.84 | 83.95 | 2 / 2 / 5 |
| github | 12 | 64.76 | 41.60 | -23.16 | 50.90 | 47.63 | 1 / 9 / 2 |
| gmail | 10 | 72.19 | 50.18 | -22.00 | 70.19 | 44.97 | 0 / 8 / 2 |
| google_drive | 14 | 76.29 | 65.03 | -11.26 | 68.26 | 68.66 | 1 / 6 / 7 |
| hubspot | 9 | 74.14 | 49.04 | -25.10 | 65.52 | 44.33 | 0 / 4 / 5 |
| jira | 26 | 79.77 | 65.23 | -14.54 | 69.96 | 70.77 | 2 / 14 / 10 |
| linear | 15 | 83.06 | 77.53 | -5.53 | 84.43 | 78.86 | 0 / 6 / 9 |
| slack | 24 | 56.20 | 47.50 | -8.69 | 57.72 | 47.65 | 2 / 11 / 11 |

## Category

| Group | Eligible | Retained nDCG | Candidate nDCG | Delta points | Candidate recall | Candidate MRR | Improved / regressed / tied |
| --- | --- | --- | --- | --- | --- | --- | --- |
| basic | 24 | 84.80 | 76.65 | -8.15 | 83.33 | 74.55 | 0 / 5 / 19 |
| completeness | 12 | 55.71 | 26.30 | -29.40 | 27.43 | 45.98 | 1 / 11 / 0 |
| conflicting_info | 4 | 100.00 | 94.92 | -5.08 | 100.00 | 100.00 | 0 / 2 / 2 |
| constrained | 8 | 87.84 | 84.08 | -3.77 | 87.50 | 93.75 | 2 / 1 / 5 |
| high_level | 0 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | 0 / 0 / 0 |
| info_not_found | 0 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | 0 / 0 / 0 |
| intra_document_reasoning | 12 | 100.00 | 96.92 | -3.08 | 100.00 | 95.83 | 0 / 1 / 11 |
| miscellaneous | 8 | 92.88 | 86.83 | -6.05 | 100.00 | 82.81 | 0 / 2 / 6 |
| project_related | 12 | 63.62 | 50.46 | -13.16 | 60.79 | 62.78 | 3 / 9 / 0 |
| semantic | 32 | 40.20 | 22.86 | -17.35 | 37.50 | 18.43 | 2 / 13 / 17 |

[Family result](README.md) · [CTA](cta.md) · [Full metrics](aggregate.json)
