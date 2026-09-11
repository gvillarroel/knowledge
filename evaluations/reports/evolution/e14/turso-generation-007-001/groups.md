# EnterpriseRAG E14: Turso generation 7 paired groups

Compare `versioned-006` with `versioned-001`. Values use a 0–100 scale and full-precision differences. Applications overlap; groups without retrieval references have unavailable quality. No application router is selected or tested.

## Application

| Group | Eligible | Retained nDCG | Candidate nDCG | Delta points | Candidate recall | Candidate MRR | Improved / regressed / tied |
| --- | --- | --- | --- | --- | --- | --- | --- |
| confluence | 39 | 69.87 | 69.82 | -0.05 | 78.51 | 72.98 | 3 / 1 / 35 |
| fireflies | 9 | 77.65 | 77.65 | +0.00 | 83.86 | 76.10 | 0 / 0 / 9 |
| github | 12 | 61.99 | 61.98 | -0.01 | 73.20 | 65.33 | 2 / 1 / 9 |
| gmail | 10 | 72.70 | 72.31 | -0.39 | 95.30 | 68.34 | 0 / 1 / 9 |
| google_drive | 14 | 74.96 | 75.39 | +0.43 | 87.07 | 77.15 | 2 / 0 / 12 |
| hubspot | 9 | 74.14 | 74.14 | +0.00 | 82.76 | 71.26 | 0 / 0 / 9 |
| jira | 26 | 80.47 | 80.20 | -0.27 | 85.26 | 84.42 | 3 / 3 / 20 |
| linear | 15 | 82.91 | 82.91 | +0.00 | 86.31 | 82.68 | 0 / 0 / 15 |
| slack | 24 | 56.52 | 56.35 | -0.18 | 69.62 | 54.40 | 1 / 2 / 21 |

## Category

| Group | Eligible | Retained nDCG | Candidate nDCG | Delta points | Candidate recall | Candidate MRR | Improved / regressed / tied |
| --- | --- | --- | --- | --- | --- | --- | --- |
| basic | 24 | 84.67 | 84.80 | +0.13 | 91.67 | 82.68 | 1 / 0 / 23 |
| completeness | 12 | 58.41 | 56.72 | -1.70 | 61.81 | 64.86 | 0 / 3 / 9 |
| conflicting_info | 4 | 97.99 | 97.99 | +0.00 | 100.00 | 100.00 | 0 / 0 / 4 |
| constrained | 8 | 88.18 | 88.18 | +0.00 | 93.75 | 93.75 | 0 / 0 / 8 |
| high_level | 0 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | 0 / 0 / 0 |
| info_not_found | 0 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | 0 / 0 / 0 |
| intra_document_reasoning | 12 | 100.00 | 100.00 | +0.00 | 100.00 | 100.00 | 0 / 0 / 12 |
| miscellaneous | 8 | 92.88 | 92.88 | +0.00 | 100.00 | 90.62 | 0 / 0 / 8 |
| project_related | 12 | 63.93 | 64.10 | +0.18 | 75.60 | 72.92 | 3 / 0 / 9 |
| semantic | 32 | 39.16 | 39.16 | +0.00 | 59.38 | 32.73 | 0 / 0 / 32 |

[Family result](README.md) · [CTA](cta.md) · [Full metrics](aggregate.json)
