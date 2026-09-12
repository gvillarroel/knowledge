# EnterpriseRAG E14: Graphify generation 23 paired groups

Compare `versioned-023` with `versioned-016`. Values use a 0–100 scale and full-precision differences. Applications overlap; groups without retrieval references have unavailable quality. No application router is selected or tested.

## Application

| Group | Eligible | Retained nDCG | Candidate nDCG | Delta points | Candidate recall | Candidate MRR | Improved / regressed / tied |
| --- | --- | --- | --- | --- | --- | --- | --- |
| confluence | 39 | 62.87 | 56.05 | -6.82 | 77.00 | 58.22 | 4 / 26 / 9 |
| fireflies | 9 | 70.91 | 65.25 | -5.67 | 79.84 | 62.66 | 0 / 5 / 4 |
| github | 12 | 68.16 | 53.37 | -14.79 | 72.19 | 63.21 | 2 / 8 / 2 |
| gmail | 10 | 68.59 | 55.60 | -12.99 | 79.55 | 51.97 | 0 / 7 / 3 |
| google_drive | 14 | 82.74 | 72.35 | -10.40 | 83.10 | 76.65 | 1 / 8 / 5 |
| hubspot | 9 | 70.96 | 60.96 | -10.00 | 82.76 | 53.93 | 0 / 3 / 6 |
| jira | 26 | 68.97 | 57.77 | -11.19 | 75.59 | 59.31 | 3 / 17 / 6 |
| linear | 15 | 65.23 | 60.16 | -5.07 | 82.29 | 57.42 | 0 / 6 / 9 |
| slack | 24 | 47.11 | 33.99 | -13.13 | 56.25 | 35.02 | 2 / 17 / 5 |

## Category

| Group | Eligible | Retained nDCG | Candidate nDCG | Delta points | Candidate recall | Candidate MRR | Improved / regressed / tied |
| --- | --- | --- | --- | --- | --- | --- | --- |
| basic | 24 | 75.65 | 68.76 | -6.89 | 91.67 | 61.53 | 1 / 8 / 15 |
| completeness | 12 | 52.02 | 44.47 | -7.55 | 49.10 | 54.51 | 3 / 9 / 0 |
| conflicting_info | 4 | 87.53 | 73.54 | -13.99 | 100.00 | 61.90 | 0 / 2 / 2 |
| constrained | 8 | 70.15 | 53.64 | -16.51 | 75.00 | 53.54 | 0 / 6 / 2 |
| high_level | 0 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | 0 / 0 / 0 |
| info_not_found | 0 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | 0 / 0 / 0 |
| intra_document_reasoning | 12 | 88.01 | 69.68 | -18.34 | 100.00 | 60.00 | 0 / 7 / 5 |
| miscellaneous | 8 | 73.97 | 60.25 | -13.72 | 100.00 | 47.81 | 0 / 5 / 3 |
| project_related | 12 | 67.96 | 57.54 | -10.43 | 61.62 | 82.29 | 2 / 9 / 1 |
| semantic | 32 | 32.77 | 26.58 | -6.19 | 53.12 | 18.36 | 0 / 14 / 18 |

[Family result](README.md) · [CTA](cta.md) · [Full metrics](aggregate.json)
