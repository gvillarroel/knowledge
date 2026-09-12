# EnterpriseRAG E14: Graphify generation 18 paired groups

Compare `versioned-018` with `versioned-016`. Values use a 0–100 scale and full-precision differences. Applications overlap; groups without retrieval references have unavailable quality. No application router is selected or tested.

## Application

| Group | Eligible | Retained nDCG | Candidate nDCG | Delta points | Candidate recall | Candidate MRR | Improved / regressed / tied |
| --- | --- | --- | --- | --- | --- | --- | --- |
| confluence | 39 | 62.87 | 62.75 | -0.12 | 76.82 | 64.25 | 1 / 1 / 37 |
| fireflies | 9 | 70.91 | 70.91 | +0.00 | 83.86 | 67.45 | 0 / 0 / 9 |
| github | 12 | 68.16 | 68.25 | +0.09 | 77.41 | 80.68 | 1 / 0 / 11 |
| gmail | 10 | 68.59 | 68.59 | +0.00 | 95.30 | 61.47 | 0 / 0 / 10 |
| google_drive | 14 | 82.74 | 82.82 | +0.07 | 85.91 | 88.19 | 1 / 0 / 13 |
| hubspot | 9 | 70.96 | 70.96 | +0.00 | 82.76 | 66.95 | 0 / 0 / 9 |
| jira | 26 | 68.97 | 67.92 | -1.05 | 83.33 | 69.43 | 1 / 1 / 24 |
| linear | 15 | 65.23 | 65.23 | +0.00 | 84.17 | 61.94 | 0 / 0 / 15 |
| slack | 24 | 47.11 | 46.88 | -0.24 | 69.70 | 44.13 | 0 / 1 / 23 |

## Category

| Group | Eligible | Retained nDCG | Candidate nDCG | Delta points | Candidate recall | Candidate MRR | Improved / regressed / tied |
| --- | --- | --- | --- | --- | --- | --- | --- |
| basic | 24 | 75.65 | 75.65 | +0.00 | 91.67 | 70.45 | 0 / 0 / 24 |
| completeness | 12 | 52.02 | 52.02 | +0.00 | 56.60 | 66.32 | 0 / 0 / 12 |
| conflicting_info | 4 | 87.53 | 87.53 | +0.00 | 100.00 | 81.25 | 0 / 0 / 4 |
| constrained | 8 | 70.15 | 66.53 | -3.61 | 81.25 | 66.67 | 0 / 1 / 7 |
| high_level | 0 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | 0 / 0 / 0 |
| info_not_found | 0 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | 0 / 0 / 0 |
| intra_document_reasoning | 12 | 88.01 | 88.01 | +0.00 | 100.00 | 84.03 | 0 / 0 / 12 |
| miscellaneous | 8 | 73.97 | 73.97 | +0.00 | 100.00 | 65.62 | 0 / 0 / 8 |
| project_related | 12 | 67.96 | 67.55 | -0.41 | 75.79 | 83.61 | 1 / 1 / 10 |
| semantic | 32 | 32.77 | 32.77 | +0.00 | 59.38 | 24.15 | 0 / 0 / 32 |

[Family result](README.md) · [CTA](cta.md) · [Full metrics](aggregate.json)
