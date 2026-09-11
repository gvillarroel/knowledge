# EnterpriseRAG E14: Turso generation 5 paired groups

Compare `versioned-004` with `versioned-001`. Values use a 0–100 scale and full-precision differences. Applications overlap; groups without retrieval references have unavailable quality. No application router is selected or tested.

## Application

| Group | Eligible | Retained nDCG | Candidate nDCG | Delta points | Candidate recall | Candidate MRR | Improved / regressed / tied |
| --- | --- | --- | --- | --- | --- | --- | --- |
| confluence | 39 | 69.87 | 62.81 | -7.06 | 70.72 | 69.29 | 6 / 20 / 13 |
| fireflies | 9 | 77.65 | 79.19 | +1.53 | 78.84 | 84.06 | 2 / 2 / 5 |
| github | 12 | 61.99 | 41.62 | -20.37 | 50.90 | 47.33 | 1 / 9 / 2 |
| gmail | 10 | 72.70 | 49.85 | -22.85 | 69.45 | 45.08 | 0 / 8 / 2 |
| google_drive | 14 | 74.96 | 64.85 | -10.11 | 67.76 | 68.66 | 2 / 6 / 6 |
| hubspot | 9 | 74.14 | 49.24 | -24.90 | 65.52 | 44.54 | 0 / 4 / 5 |
| jira | 26 | 80.47 | 65.21 | -15.26 | 69.68 | 70.77 | 2 / 14 / 10 |
| linear | 15 | 82.91 | 77.53 | -5.38 | 84.43 | 78.86 | 0 / 6 / 9 |
| slack | 24 | 56.52 | 47.79 | -8.74 | 57.40 | 48.12 | 3 / 11 / 10 |

## Category

| Group | Eligible | Retained nDCG | Candidate nDCG | Delta points | Candidate recall | Candidate MRR | Improved / regressed / tied |
| --- | --- | --- | --- | --- | --- | --- | --- |
| basic | 24 | 84.67 | 76.65 | -8.02 | 83.33 | 74.55 | 0 / 5 / 19 |
| completeness | 12 | 58.41 | 24.40 | -34.02 | 23.61 | 46.18 | 1 / 11 / 0 |
| conflicting_info | 4 | 97.99 | 94.92 | -3.07 | 100.00 | 100.00 | 1 / 2 / 1 |
| constrained | 8 | 88.18 | 83.55 | -4.63 | 87.50 | 93.75 | 1 / 1 / 6 |
| high_level | 0 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | 0 / 0 / 0 |
| info_not_found | 0 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | 0 / 0 / 0 |
| intra_document_reasoning | 12 | 100.00 | 96.92 | -3.08 | 100.00 | 95.83 | 0 / 1 / 11 |
| miscellaneous | 8 | 92.88 | 87.05 | -5.83 | 100.00 | 83.04 | 0 / 2 / 6 |
| project_related | 12 | 63.93 | 50.74 | -13.19 | 60.79 | 62.78 | 3 / 9 / 0 |
| semantic | 32 | 39.16 | 23.05 | -16.11 | 37.50 | 18.66 | 3 / 13 / 16 |

[Family result](README.md) · [CTA](cta.md) · [Full metrics](aggregate.json)
