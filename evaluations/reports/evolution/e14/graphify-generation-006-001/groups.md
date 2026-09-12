# EnterpriseRAG E14: Graphify generation 6 paired groups

Compare `versioned-006` with `versioned-004`. Values use a 0–100 scale and full-precision differences. Applications overlap; groups without retrieval references have unavailable quality. No application router is selected or tested.

## Application

| Group | Eligible | Retained nDCG | Candidate nDCG | Delta points | Candidate recall | Candidate MRR | Improved / regressed / tied |
| --- | --- | --- | --- | --- | --- | --- | --- |
| confluence | 39 | 28.32 | 28.31 | -0.01 | 32.91 | 36.60 | 0 / 1 / 38 |
| fireflies | 9 | 50.42 | 50.42 | +0.00 | 53.42 | 51.41 | 0 / 0 / 9 |
| github | 12 | 25.75 | 25.75 | +0.00 | 29.16 | 43.88 | 0 / 0 / 12 |
| gmail | 10 | 21.66 | 21.66 | +0.00 | 50.54 | 17.91 | 0 / 0 / 10 |
| google_drive | 14 | 56.85 | 56.83 | -0.03 | 61.44 | 67.61 | 0 / 1 / 13 |
| hubspot | 9 | 32.18 | 32.18 | +0.00 | 32.18 | 32.18 | 0 / 0 / 9 |
| jira | 26 | 31.84 | 31.83 | -0.01 | 33.50 | 42.56 | 0 / 1 / 25 |
| linear | 15 | 23.85 | 23.83 | -0.02 | 36.05 | 24.60 | 0 / 1 / 14 |
| slack | 24 | 9.59 | 9.57 | -0.02 | 8.28 | 19.20 | 0 / 1 / 23 |

## Category

| Group | Eligible | Retained nDCG | Candidate nDCG | Delta points | Candidate recall | Candidate MRR | Improved / regressed / tied |
| --- | --- | --- | --- | --- | --- | --- | --- |
| basic | 24 | 42.18 | 42.18 | +0.00 | 54.17 | 38.19 | 0 / 0 / 24 |
| completeness | 12 | 30.24 | 30.24 | +0.00 | 28.40 | 41.67 | 0 / 0 / 12 |
| conflicting_info | 4 | 50.00 | 50.00 | +0.00 | 50.00 | 50.00 | 0 / 0 / 4 |
| constrained | 8 | 15.23 | 15.23 | +0.00 | 18.75 | 14.58 | 0 / 0 / 8 |
| high_level | 0 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | 0 / 0 / 0 |
| info_not_found | 0 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | 0 / 0 / 0 |
| intra_document_reasoning | 12 | 38.71 | 38.71 | +0.00 | 50.00 | 35.56 | 0 / 0 / 12 |
| miscellaneous | 8 | 27.37 | 27.37 | +0.00 | 50.00 | 20.54 | 0 / 0 / 8 |
| project_related | 12 | 32.08 | 32.04 | -0.04 | 31.02 | 65.28 | 0 / 1 / 11 |
| semantic | 32 | 2.46 | 2.46 | +0.00 | 6.25 | 1.30 | 0 / 0 / 32 |

[Family result](README.md) · [CTA](cta.md) · [Full metrics](aggregate.json)
