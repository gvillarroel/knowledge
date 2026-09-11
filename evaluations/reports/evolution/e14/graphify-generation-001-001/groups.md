# EnterpriseRAG E14: Graphify depth-zero paired groups

Compare `versioned-001` with the retained `baseline`. Values use a 0–100 display scale and deltas use full precision. Application groups overlap; subgroups without references have unavailable quality. No application router is selected or evaluated.

## Application

| Group | Eligible | Baseline nDCG | Candidate nDCG | Delta points | Candidate recall | Candidate MRR | Improved / regressed / tied |
| --- | --- | --- | --- | --- | --- | --- | --- |
| confluence | 39 | 9.82 | 7.39 | -2.43 | 11.50 | 8.64 | 4 / 2 / 33 |
| fireflies | 9 | 4.75 | 4.75 | +0.00 | 7.52 | 3.76 | 0 / 0 / 9 |
| github | 12 | 11.03 | 11.39 | +0.35 | 16.83 | 15.47 | 1 / 1 / 10 |
| gmail | 10 | 16.88 | 17.88 | +1.00 | 38.32 | 12.02 | 3 / 0 / 7 |
| google_drive | 14 | 17.72 | 7.73 | -9.99 | 12.90 | 10.67 | 2 / 3 / 9 |
| hubspot | 9 | 0.00 | 0.00 | +0.00 | 0.00 | 0.00 | 0 / 0 / 9 |
| jira | 26 | 5.45 | 5.64 | +0.19 | 6.15 | 8.53 | 2 / 1 / 23 |
| linear | 15 | 12.83 | 12.83 | +0.00 | 14.55 | 12.83 | 0 / 0 / 15 |
| slack | 24 | 2.82 | 2.84 | +0.02 | 3.50 | 3.98 | 1 / 1 / 22 |

## Category

| Group | Eligible | Baseline nDCG | Candidate nDCG | Delta points | Candidate recall | Candidate MRR | Improved / regressed / tied |
| --- | --- | --- | --- | --- | --- | --- | --- |
| basic | 24 | 10.13 | 8.88 | -1.25 | 12.50 | 7.64 | 0 / 1 / 23 |
| completeness | 12 | 16.69 | 16.82 | +0.13 | 15.76 | 22.92 | 1 / 1 / 10 |
| conflicting_info | 4 | 18.72 | 0.00 | -18.72 | 0.00 | 0.00 | 0 / 2 / 2 |
| constrained | 8 | 6.05 | 6.39 | +0.34 | 12.50 | 5.95 | 1 / 0 / 7 |
| high_level | 0 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | 0 / 0 / 0 |
| info_not_found | 0 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | 0 / 0 / 0 |
| intra_document_reasoning | 12 | 6.10 | 6.94 | +0.85 | 16.67 | 3.97 | 2 / 0 / 10 |
| miscellaneous | 8 | 18.11 | 18.97 | +0.87 | 37.50 | 12.92 | 1 / 0 / 7 |
| project_related | 12 | 9.44 | 9.95 | +0.51 | 14.12 | 15.58 | 2 / 0 / 10 |
| semantic | 32 | 1.35 | 1.35 | +0.00 | 3.12 | 0.78 | 0 / 0 / 32 |

[Family result](README.md) · [CTA](cta.md) · [Full metrics](aggregate.json)
