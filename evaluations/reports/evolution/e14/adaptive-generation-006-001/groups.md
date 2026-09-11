# EnterpriseRAG E14: Adaptive generation 6 paired groups

Compare `versioned-005` with `retained-start`. Values use a 0–100 scale and full-precision differences. Applications overlap; groups without retrieval references have unavailable quality. No application router is selected or tested.

## Application

| Group | Eligible | Retained nDCG | Candidate nDCG | Delta points | Candidate recall | Candidate MRR | Improved / regressed / tied |
| --- | --- | --- | --- | --- | --- | --- | --- |
| confluence | 39 | 68.09 | 59.51 | -8.57 | 67.35 | 65.84 | 5 / 21 / 13 |
| fireflies | 9 | 69.60 | 67.81 | -1.79 | 69.09 | 68.34 | 0 / 3 / 6 |
| github | 12 | 62.71 | 49.85 | -12.87 | 69.03 | 50.85 | 0 / 8 / 4 |
| gmail | 10 | 71.15 | 48.81 | -22.34 | 69.75 | 48.47 | 1 / 5 / 4 |
| google_drive | 14 | 68.73 | 62.70 | -6.03 | 72.06 | 64.37 | 1 / 7 / 6 |
| hubspot | 9 | 59.97 | 59.97 | +0.00 | 65.52 | 58.33 | 0 / 0 / 9 |
| jira | 26 | 69.16 | 60.86 | -8.30 | 68.99 | 64.31 | 3 / 11 / 12 |
| linear | 15 | 81.33 | 65.66 | -15.66 | 77.45 | 65.96 | 1 / 7 / 7 |
| slack | 24 | 50.16 | 32.51 | -17.65 | 43.60 | 37.54 | 2 / 14 / 8 |

## Category

| Group | Eligible | Retained nDCG | Candidate nDCG | Delta points | Candidate recall | Candidate MRR | Improved / regressed / tied |
| --- | --- | --- | --- | --- | --- | --- | --- |
| basic | 24 | 84.72 | 67.14 | -17.59 | 83.33 | 61.88 | 0 / 9 / 15 |
| completeness | 12 | 62.90 | 56.33 | -6.57 | 61.53 | 65.90 | 2 / 10 / 0 |
| conflicting_info | 4 | 96.26 | 91.69 | -4.57 | 100.00 | 100.00 | 0 / 2 / 2 |
| constrained | 8 | 80.70 | 82.80 | +2.11 | 87.50 | 93.75 | 2 / 1 / 5 |
| high_level | 0 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | 0 / 0 / 0 |
| info_not_found | 0 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | 0 / 0 / 0 |
| intra_document_reasoning | 12 | 100.00 | 89.68 | -10.32 | 100.00 | 86.11 | 0 / 3 / 9 |
| miscellaneous | 8 | 87.50 | 72.02 | -15.48 | 87.50 | 66.67 | 0 / 3 / 5 |
| project_related | 12 | 60.27 | 50.20 | -10.06 | 56.81 | 64.04 | 2 / 7 / 3 |
| semantic | 32 | 20.22 | 12.16 | -8.05 | 21.88 | 9.38 | 0 / 10 / 22 |

[Family result](README.md) · [CTA](cta.md) · [Full metrics](aggregate.json)
