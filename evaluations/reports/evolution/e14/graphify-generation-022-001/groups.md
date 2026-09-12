# EnterpriseRAG E14: Graphify generation 22 paired groups

Compare `versioned-022` with `versioned-016`. Values use a 0–100 scale and full-precision differences. Applications overlap; groups without retrieval references have unavailable quality. No application router is selected or tested.

## Application

| Group | Eligible | Retained nDCG | Candidate nDCG | Delta points | Candidate recall | Candidate MRR | Improved / regressed / tied |
| --- | --- | --- | --- | --- | --- | --- | --- |
| confluence | 39 | 62.87 | 60.39 | -2.47 | 75.81 | 66.53 | 5 / 21 / 13 |
| fireflies | 9 | 70.91 | 67.20 | -3.71 | 79.84 | 65.10 | 0 / 4 / 5 |
| github | 12 | 68.16 | 55.11 | -13.05 | 71.94 | 67.35 | 1 / 8 / 3 |
| gmail | 10 | 68.59 | 57.34 | -11.25 | 79.55 | 54.63 | 0 / 7 / 3 |
| google_drive | 14 | 82.74 | 76.93 | -5.81 | 82.11 | 84.84 | 1 / 8 / 5 |
| hubspot | 9 | 70.96 | 66.63 | -4.33 | 82.76 | 61.35 | 1 / 3 / 5 |
| jira | 26 | 68.97 | 61.31 | -7.66 | 79.26 | 64.69 | 2 / 17 / 7 |
| linear | 15 | 65.23 | 62.42 | -2.81 | 82.29 | 60.13 | 1 / 3 / 11 |
| slack | 24 | 47.11 | 42.16 | -4.95 | 56.44 | 46.05 | 3 / 12 / 9 |

## Category

| Group | Eligible | Retained nDCG | Candidate nDCG | Delta points | Candidate recall | Candidate MRR | Improved / regressed / tied |
| --- | --- | --- | --- | --- | --- | --- | --- |
| basic | 24 | 75.65 | 72.03 | -3.62 | 91.67 | 65.53 | 1 / 6 / 17 |
| completeness | 12 | 52.02 | 47.07 | -4.96 | 51.32 | 59.66 | 3 / 9 / 0 |
| conflicting_info | 4 | 87.53 | 86.59 | -0.94 | 100.00 | 83.33 | 1 / 1 / 2 |
| constrained | 8 | 70.15 | 65.23 | -4.92 | 87.50 | 67.71 | 1 / 4 / 3 |
| high_level | 0 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | 0 / 0 / 0 |
| info_not_found | 0 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | 0 / 0 / 0 |
| intra_document_reasoning | 12 | 88.01 | 78.79 | -9.23 | 100.00 | 71.53 | 0 / 3 / 9 |
| miscellaneous | 8 | 73.97 | 66.96 | -7.01 | 100.00 | 55.95 | 1 / 3 / 4 |
| project_related | 12 | 67.96 | 56.36 | -11.60 | 60.93 | 84.03 | 1 / 10 / 1 |
| semantic | 32 | 32.77 | 31.40 | -1.37 | 53.12 | 24.51 | 2 / 8 / 22 |

[Family result](README.md) · [CTA](cta.md) · [Full metrics](aggregate.json)
