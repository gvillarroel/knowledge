# EnterpriseRAG E14: Adaptive generation 5 paired groups

Compare `versioned-004` with `retained-start`. Values use a 0–100 scale and full-precision differences. Applications overlap; groups without retrieval references have unavailable quality. No application router is selected or tested.

## Application

| Group | Eligible | Retained nDCG | Candidate nDCG | Delta points | Candidate recall | Candidate MRR | Improved / regressed / tied |
| --- | --- | --- | --- | --- | --- | --- | --- |
| confluence | 39 | 68.09 | 68.15 | +0.06 | 75.20 | 75.92 | 4 / 8 / 27 |
| fireflies | 9 | 69.60 | 69.60 | +0.00 | 70.09 | 72.73 | 0 / 0 / 9 |
| github | 12 | 62.71 | 62.56 | -0.15 | 71.31 | 73.42 | 1 / 3 / 8 |
| gmail | 10 | 71.15 | 63.96 | -7.20 | 71.38 | 66.02 | 0 / 1 / 9 |
| google_drive | 14 | 68.73 | 68.57 | -0.16 | 72.06 | 74.54 | 1 / 2 / 11 |
| hubspot | 9 | 59.97 | 59.62 | -0.35 | 65.52 | 57.97 | 0 / 1 / 8 |
| jira | 26 | 69.16 | 68.88 | -0.28 | 77.49 | 76.68 | 3 / 3 / 20 |
| linear | 15 | 81.33 | 81.58 | +0.25 | 84.70 | 84.48 | 2 / 1 / 12 |
| slack | 24 | 50.16 | 48.63 | -1.52 | 60.06 | 56.17 | 2 / 4 / 18 |

## Category

| Group | Eligible | Retained nDCG | Candidate nDCG | Delta points | Candidate recall | Candidate MRR | Improved / regressed / tied |
| --- | --- | --- | --- | --- | --- | --- | --- |
| basic | 24 | 84.72 | 83.18 | -1.54 | 87.50 | 81.85 | 0 / 1 / 23 |
| completeness | 12 | 62.90 | 63.13 | +0.22 | 67.85 | 75.00 | 1 / 3 / 8 |
| conflicting_info | 4 | 96.26 | 95.79 | -0.47 | 100.00 | 100.00 | 0 / 1 / 3 |
| constrained | 8 | 80.70 | 83.52 | +2.83 | 87.50 | 93.75 | 1 / 0 / 7 |
| high_level | 0 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | 0 / 0 / 0 |
| info_not_found | 0 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | 0 / 0 / 0 |
| intra_document_reasoning | 12 | 100.00 | 100.00 | +0.00 | 100.00 | 100.00 | 0 / 0 / 12 |
| miscellaneous | 8 | 87.50 | 87.50 | +0.00 | 87.50 | 87.50 | 0 / 0 / 8 |
| project_related | 12 | 60.27 | 57.61 | -2.66 | 62.78 | 82.22 | 1 / 5 / 6 |
| semantic | 32 | 20.22 | 20.32 | +0.11 | 40.62 | 14.43 | 6 / 2 / 24 |

[Family result](README.md) · [CTA](cta.md) · [Full metrics](aggregate.json)
