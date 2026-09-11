# EnterpriseRAG E14: Adaptive b=0.5 paired groups

Compare `versioned-002` against `retained-start` on the fixed stratified development workload. Applications can overlap; groups without retrieval references have unavailable quality. Values use a 0–100 scale with full-precision differences. No application router was selected or tested.

## Application

| Group | Eligible | Retained nDCG | Candidate nDCG | Delta points | Candidate recall | Candidate MRR | Improved / regressed / tied |
| --- | --- | --- | --- | --- | --- | --- | --- |
| confluence | 39 | 68.09 | 68.64 | +0.55 | 76.17 | 75.17 | 8 / 11 / 20 |
| fireflies | 9 | 69.60 | 68.43 | -1.17 | 69.72 | 68.71 | 0 / 3 / 6 |
| github | 12 | 62.71 | 60.14 | -2.57 | 70.93 | 66.73 | 1 / 7 / 4 |
| gmail | 10 | 71.15 | 63.08 | -8.08 | 70.49 | 66.02 | 0 / 5 / 5 |
| google_drive | 14 | 68.73 | 67.71 | -1.02 | 72.06 | 71.07 | 1 / 4 / 9 |
| hubspot | 9 | 59.97 | 59.62 | -0.35 | 65.52 | 57.97 | 0 / 1 / 8 |
| jira | 26 | 69.16 | 67.09 | -2.07 | 74.05 | 73.45 | 4 / 9 / 13 |
| linear | 15 | 81.33 | 84.53 | +3.21 | 90.34 | 86.46 | 4 / 1 / 10 |
| slack | 24 | 50.16 | 49.42 | -0.74 | 61.53 | 54.99 | 4 / 7 / 13 |

## Category

| Group | Eligible | Retained nDCG | Candidate nDCG | Delta points | Candidate recall | Candidate MRR | Improved / regressed / tied |
| --- | --- | --- | --- | --- | --- | --- | --- |
| basic | 24 | 84.72 | 83.28 | -1.44 | 87.50 | 81.94 | 1 / 1 / 22 |
| completeness | 12 | 62.90 | 57.48 | -5.43 | 64.31 | 62.78 | 1 / 9 / 2 |
| conflicting_info | 4 | 96.26 | 96.26 | +0.00 | 100.00 | 100.00 | 0 / 0 / 4 |
| constrained | 8 | 80.70 | 81.27 | +0.57 | 87.50 | 87.50 | 1 / 0 / 7 |
| high_level | 0 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | 0 / 0 / 0 |
| info_not_found | 0 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | 0 / 0 / 0 |
| intra_document_reasoning | 12 | 100.00 | 100.00 | +0.00 | 100.00 | 100.00 | 0 / 0 / 12 |
| miscellaneous | 8 | 87.50 | 87.50 | +0.00 | 87.50 | 87.50 | 0 / 0 / 8 |
| project_related | 12 | 60.27 | 59.01 | -1.26 | 67.22 | 79.86 | 4 / 6 / 2 |
| semantic | 32 | 20.22 | 21.75 | +1.53 | 40.62 | 16.27 | 6 / 4 / 22 |

[Family result](README.md) · [CTA](cta.md) · [Full metrics](aggregate.json)
