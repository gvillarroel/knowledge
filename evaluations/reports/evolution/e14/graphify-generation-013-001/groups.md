# EnterpriseRAG E14: Graphify generation 13 paired groups

Compare `versioned-013` with `versioned-010`. Values use a 0–100 scale and full-precision differences. Applications overlap; groups without retrieval references have unavailable quality. No application router is selected or tested.

## Application

| Group | Eligible | Retained nDCG | Candidate nDCG | Delta points | Candidate recall | Candidate MRR | Improved / regressed / tied |
| --- | --- | --- | --- | --- | --- | --- | --- |
| confluence | 39 | 62.75 | 53.89 | -8.85 | 75.26 | 56.61 | 3 / 26 / 10 |
| fireflies | 9 | 70.91 | 64.34 | -6.57 | 78.84 | 62.15 | 0 / 5 / 4 |
| github | 12 | 68.25 | 51.98 | -16.27 | 70.30 | 61.90 | 1 / 8 / 3 |
| gmail | 10 | 68.59 | 55.05 | -13.54 | 78.66 | 51.86 | 0 / 7 / 3 |
| google_drive | 14 | 82.82 | 71.17 | -11.64 | 81.61 | 76.54 | 0 / 8 / 6 |
| hubspot | 9 | 70.96 | 54.65 | -16.30 | 82.76 | 45.91 | 0 / 5 / 4 |
| jira | 26 | 67.92 | 55.02 | -12.90 | 74.75 | 56.24 | 2 / 17 / 7 |
| linear | 15 | 65.23 | 57.56 | -7.67 | 82.29 | 55.22 | 0 / 9 / 6 |
| slack | 24 | 46.88 | 32.71 | -14.17 | 55.86 | 34.11 | 2 / 17 / 5 |

## Category

| Group | Eligible | Retained nDCG | Candidate nDCG | Delta points | Candidate recall | Candidate MRR | Improved / regressed / tied |
| --- | --- | --- | --- | --- | --- | --- | --- |
| basic | 24 | 75.65 | 67.09 | -8.56 | 91.67 | 59.52 | 1 / 10 / 13 |
| completeness | 12 | 52.02 | 44.37 | -7.66 | 48.82 | 55.35 | 3 / 8 / 1 |
| conflicting_info | 4 | 87.53 | 73.54 | -13.99 | 100.00 | 61.90 | 0 / 2 / 2 |
| constrained | 8 | 66.53 | 49.13 | -17.41 | 68.75 | 50.12 | 0 / 5 / 3 |
| high_level | 0 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | 0 / 0 / 0 |
| info_not_found | 0 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | 0 / 0 / 0 |
| intra_document_reasoning | 12 | 88.01 | 68.13 | -19.89 | 100.00 | 58.15 | 0 / 7 / 5 |
| miscellaneous | 8 | 73.97 | 59.97 | -14.00 | 100.00 | 47.51 | 0 / 5 / 3 |
| project_related | 12 | 67.55 | 55.23 | -12.32 | 59.54 | 81.25 | 1 / 10 / 1 |
| semantic | 32 | 32.77 | 23.10 | -9.67 | 53.12 | 14.07 | 0 / 17 / 15 |

[Family result](README.md) · [CTA](cta.md) · [Full metrics](aggregate.json)
