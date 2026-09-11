# EnterpriseRAG E14: Graphify generation 2 paired groups

Compare `versioned-002` with `baseline`. Values use a 0–100 scale and full-precision differences. Applications overlap; groups without retrieval references have unavailable quality. No application router is selected or tested.

## Application

| Group | Eligible | Retained nDCG | Candidate nDCG | Delta points | Candidate recall | Candidate MRR | Improved / regressed / tied |
| --- | --- | --- | --- | --- | --- | --- | --- |
| confluence | 39 | 9.82 | 7.14 | -2.68 | 11.50 | 7.90 | 0 / 2 / 37 |
| fireflies | 9 | 4.75 | 4.75 | +0.00 | 7.52 | 3.76 | 0 / 0 / 9 |
| github | 12 | 11.03 | 11.03 | +0.00 | 16.83 | 14.21 | 0 / 0 / 12 |
| gmail | 10 | 16.88 | 16.88 | +0.00 | 38.32 | 10.61 | 0 / 0 / 10 |
| google_drive | 14 | 17.72 | 7.12 | -10.61 | 12.90 | 9.31 | 0 / 3 / 11 |
| hubspot | 9 | 0.00 | 0.00 | +0.00 | 0.00 | 0.00 | 0 / 0 / 9 |
| jira | 26 | 5.45 | 5.45 | +0.00 | 6.15 | 7.82 | 0 / 0 / 26 |
| linear | 15 | 12.83 | 12.83 | +0.00 | 14.55 | 12.83 | 0 / 0 / 15 |
| slack | 24 | 2.82 | 2.82 | +0.00 | 3.50 | 3.81 | 0 / 0 / 24 |

## Category

| Group | Eligible | Retained nDCG | Candidate nDCG | Delta points | Candidate recall | Candidate MRR | Improved / regressed / tied |
| --- | --- | --- | --- | --- | --- | --- | --- |
| basic | 24 | 10.13 | 8.88 | -1.25 | 12.50 | 7.64 | 0 / 1 / 23 |
| completeness | 12 | 16.69 | 16.69 | +0.00 | 15.76 | 22.02 | 0 / 0 / 12 |
| conflicting_info | 4 | 18.72 | 0.00 | -18.72 | 0.00 | 0.00 | 0 / 2 / 2 |
| constrained | 8 | 6.05 | 6.05 | +0.00 | 12.50 | 5.42 | 0 / 0 / 8 |
| high_level | 0 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | 0 / 0 / 0 |
| info_not_found | 0 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | 0 / 0 / 0 |
| intra_document_reasoning | 12 | 6.10 | 6.10 | +0.00 | 16.67 | 3.01 | 0 / 0 / 12 |
| miscellaneous | 8 | 18.11 | 18.11 | +0.00 | 37.50 | 11.88 | 0 / 0 / 8 |
| project_related | 12 | 9.44 | 9.44 | +0.00 | 14.12 | 13.83 | 0 / 0 / 12 |
| semantic | 32 | 1.35 | 1.35 | +0.00 | 3.12 | 0.78 | 0 / 0 / 32 |

[Family result](README.md) · [CTA](cta.md) · [Full metrics](aggregate.json)
