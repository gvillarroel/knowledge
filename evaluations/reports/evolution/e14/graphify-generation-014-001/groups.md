# EnterpriseRAG E14: Graphify generation 14 paired groups

Compare `versioned-014` with `versioned-010`. Values use a 0–100 scale and full-precision differences. Applications overlap; groups without retrieval references have unavailable quality. No application router is selected or tested.

## Application

| Group | Eligible | Retained nDCG | Candidate nDCG | Delta points | Candidate recall | Candidate MRR | Improved / regressed / tied |
| --- | --- | --- | --- | --- | --- | --- | --- |
| confluence | 39 | 62.75 | 60.26 | -2.48 | 75.83 | 59.06 | 8 / 11 / 20 |
| fireflies | 9 | 70.91 | 62.84 | -8.07 | 83.86 | 56.48 | 1 / 1 / 7 |
| github | 12 | 68.25 | 62.33 | -5.92 | 74.88 | 63.33 | 3 / 5 / 4 |
| gmail | 10 | 68.59 | 67.37 | -1.23 | 95.30 | 60.49 | 3 / 2 / 5 |
| google_drive | 14 | 82.82 | 61.42 | -21.40 | 83.43 | 57.49 | 2 / 7 / 5 |
| hubspot | 9 | 70.96 | 59.08 | -11.88 | 82.76 | 50.86 | 0 / 2 / 7 |
| jira | 26 | 67.92 | 68.65 | +0.73 | 85.43 | 67.59 | 7 / 8 / 11 |
| linear | 15 | 65.23 | 65.41 | +0.18 | 83.36 | 60.47 | 3 / 5 / 7 |
| slack | 24 | 46.88 | 46.24 | -0.64 | 69.06 | 40.25 | 5 / 6 / 13 |

## Category

| Group | Eligible | Retained nDCG | Candidate nDCG | Delta points | Candidate recall | Candidate MRR | Improved / regressed / tied |
| --- | --- | --- | --- | --- | --- | --- | --- |
| basic | 24 | 75.65 | 71.62 | -4.03 | 91.67 | 65.17 | 5 / 5 / 14 |
| completeness | 12 | 52.02 | 52.31 | +0.29 | 57.99 | 64.38 | 5 / 2 / 5 |
| conflicting_info | 4 | 87.53 | 78.80 | -8.73 | 100.00 | 68.75 | 0 / 1 / 3 |
| constrained | 8 | 66.53 | 65.97 | -0.56 | 93.75 | 62.50 | 2 / 1 / 5 |
| high_level | 0 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | 0 / 0 / 0 |
| info_not_found | 0 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | 0 / 0 / 0 |
| intra_document_reasoning | 12 | 88.01 | 79.68 | -8.33 | 100.00 | 72.92 | 2 / 3 / 7 |
| miscellaneous | 8 | 73.97 | 72.25 | -1.73 | 100.00 | 62.92 | 3 / 2 / 3 |
| project_related | 12 | 67.55 | 57.44 | -10.11 | 71.62 | 60.97 | 2 / 8 / 2 |
| semantic | 32 | 32.77 | 34.90 | +2.13 | 59.38 | 27.10 | 4 / 2 / 26 |

[Family result](README.md) · [CTA](cta.md) · [Full metrics](aggregate.json)
