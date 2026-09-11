# EnterpriseRAG E14: Turso generation 8 paired groups

Compare `versioned-007` with `versioned-001`. All values use a 0–100 scale and full-precision differences. Applications overlap. Groups without retrieval references have unavailable quality. No application router is selected or tested.

## Application

| Group | Eligible | Previous nDCG | New nDCG | Delta points | New recall | New MRR | New full coverage | Improved / regressed / tied |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| confluence | 39 | 69.87 | 69.99 | +0.12 | 78.51 | 73.28 | 62.65 | 5 / 6 / 28 |
| fireflies | 9 | 77.65 | 77.65 | +0.00 | 83.86 | 76.10 | 83.23 | 0 / 0 / 9 |
| github | 12 | 61.99 | 64.76 | +2.77 | 73.20 | 70.75 | 49.47 | 4 / 3 / 5 |
| gmail | 10 | 72.70 | 72.19 | -0.51 | 95.30 | 68.22 | 86.63 | 0 / 2 / 8 |
| google_drive | 14 | 74.96 | 76.29 | +1.33 | 87.07 | 78.14 | 75.16 | 4 / 0 / 10 |
| hubspot | 9 | 74.14 | 74.14 | +0.00 | 82.76 | 71.26 | 82.76 | 0 / 0 / 9 |
| jira | 26 | 80.47 | 79.77 | -0.70 | 85.26 | 84.20 | 67.47 | 3 / 6 / 17 |
| linear | 15 | 82.91 | 83.06 | +0.15 | 86.31 | 83.48 | 79.08 | 1 / 0 / 14 |
| slack | 24 | 56.52 | 56.20 | -0.32 | 69.62 | 54.89 | 55.07 | 2 / 3 / 19 |

## Category

| Group | Eligible | Previous nDCG | New nDCG | Delta points | New recall | New MRR | New full coverage | Improved / regressed / tied |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| basic | 24 | 84.67 | 84.80 | +0.13 | 91.67 | 82.68 | 91.67 | 1 / 0 / 23 |
| completeness | 12 | 58.41 | 55.71 | -2.71 | 61.81 | 63.54 | 25.00 | 0 / 7 / 5 |
| conflicting_info | 4 | 97.99 | 100.00 | +2.01 | 100.00 | 100.00 | 100.00 | 1 / 0 / 3 |
| constrained | 8 | 88.18 | 87.84 | -0.34 | 93.75 | 93.75 | 87.50 | 0 / 1 / 7 |
| high_level | 0 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | 0 / 0 / 0 |
| info_not_found | 0 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | 0 / 0 / 0 |
| intra_document_reasoning | 12 | 100.00 | 100.00 | +0.00 | 100.00 | 100.00 | 100.00 | 0 / 0 / 12 |
| miscellaneous | 8 | 92.88 | 92.88 | +0.00 | 100.00 | 90.62 | 100.00 | 0 / 0 / 8 |
| project_related | 12 | 63.93 | 63.62 | -0.30 | 75.60 | 74.31 | 33.33 | 4 / 2 / 6 |
| semantic | 32 | 39.16 | 40.20 | +1.04 | 59.38 | 34.18 | 59.38 | 1 / 2 / 29 |

[Family result](README.md) · [General comparison](comparison.md) · [CTA](cta.md) · [Full metrics](aggregate.json)
