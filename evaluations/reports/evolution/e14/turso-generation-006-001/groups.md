# EnterpriseRAG E14: Turso generation 6 paired groups

Compare `versioned-005` with `versioned-001`. Values use a 0–100 scale and full-precision differences. Applications overlap; groups without retrieval references have unavailable quality. No application router is selected or tested.

## Application

| Group | Eligible | Retained nDCG | Candidate nDCG | Delta points | Candidate recall | Candidate MRR | Improved / regressed / tied |
| --- | --- | --- | --- | --- | --- | --- | --- |
| confluence | 39 | 69.87 | 68.42 | -1.46 | 77.70 | 71.10 | 3 / 14 / 22 |
| fireflies | 9 | 77.65 | 78.46 | +0.81 | 84.48 | 78.61 | 1 / 1 / 7 |
| github | 12 | 61.99 | 56.16 | -5.84 | 71.98 | 58.25 | 1 / 8 / 3 |
| gmail | 10 | 72.70 | 72.04 | -0.66 | 95.30 | 68.37 | 1 / 4 / 5 |
| google_drive | 14 | 74.96 | 69.63 | -5.33 | 72.89 | 71.81 | 2 / 4 / 8 |
| hubspot | 9 | 74.14 | 74.14 | +0.00 | 82.76 | 71.26 | 0 / 0 / 9 |
| jira | 26 | 80.47 | 76.55 | -3.92 | 84.53 | 79.65 | 1 / 12 / 13 |
| linear | 15 | 82.91 | 82.40 | -0.51 | 85.77 | 83.48 | 0 / 2 / 13 |
| slack | 24 | 56.52 | 56.18 | -0.35 | 69.00 | 55.27 | 3 / 6 / 15 |

## Category

| Group | Eligible | Retained nDCG | Candidate nDCG | Delta points | Candidate recall | Candidate MRR | Improved / regressed / tied |
| --- | --- | --- | --- | --- | --- | --- | --- |
| basic | 24 | 84.67 | 83.18 | -1.48 | 87.50 | 81.85 | 0 / 1 / 23 |
| completeness | 12 | 58.41 | 48.97 | -9.44 | 55.42 | 59.72 | 1 / 10 / 1 |
| conflicting_info | 4 | 97.99 | 100.00 | +2.01 | 100.00 | 100.00 | 1 / 0 / 3 |
| constrained | 8 | 88.18 | 88.18 | +0.00 | 93.75 | 93.75 | 0 / 0 / 8 |
| high_level | 0 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | 0 / 0 / 0 |
| info_not_found | 0 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | 0 / 0 / 0 |
| intra_document_reasoning | 12 | 100.00 | 100.00 | +0.00 | 100.00 | 100.00 | 0 / 0 / 12 |
| miscellaneous | 8 | 92.88 | 93.75 | +0.87 | 100.00 | 91.67 | 1 / 0 / 7 |
| project_related | 12 | 63.93 | 60.26 | -3.66 | 74.68 | 69.44 | 2 / 8 / 2 |
| semantic | 32 | 39.16 | 37.13 | -2.03 | 59.38 | 30.14 | 2 / 4 / 26 |

[Family result](README.md) · [CTA](cta.md) · [Full metrics](aggregate.json)
