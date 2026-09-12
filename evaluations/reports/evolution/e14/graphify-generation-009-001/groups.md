# EnterpriseRAG E14: Graphify generation 9 paired groups

Compare `versioned-009` with `versioned-008`. All values use a 0–100 scale and full-precision differences. Applications overlap. Groups without retrieval references have unavailable quality. No application router is selected or tested.

## Application

| Group | Eligible | Previous nDCG | New nDCG | Delta points | New recall | New MRR | New full coverage | Improved / regressed / tied |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| confluence | 39 | 53.89 | 57.54 | +3.64 | 74.29 | 59.30 | 54.01 | 24 / 2 / 13 |
| fireflies | 9 | 64.34 | 69.14 | +4.80 | 83.86 | 64.86 | 83.23 | 4 / 0 / 5 |
| github | 12 | 51.98 | 59.45 | +7.47 | 77.79 | 66.72 | 57.04 | 8 / 1 / 3 |
| gmail | 10 | 55.05 | 63.18 | +8.13 | 94.55 | 55.15 | 86.63 | 6 / 0 / 4 |
| google_drive | 14 | 71.17 | 80.14 | +8.97 | 85.42 | 85.58 | 72.19 | 6 / 0 / 8 |
| hubspot | 9 | 54.65 | 64.42 | +9.77 | 82.76 | 58.19 | 82.76 | 5 / 0 / 4 |
| jira | 26 | 55.02 | 60.93 | +5.92 | 83.21 | 59.64 | 68.73 | 15 / 2 / 9 |
| linear | 15 | 57.56 | 62.24 | +4.68 | 84.17 | 58.57 | 74.27 | 8 / 0 / 7 |
| slack | 24 | 32.71 | 40.45 | +7.74 | 68.29 | 38.18 | 55.07 | 16 / 1 / 7 |

## Category

| Group | Eligible | Previous nDCG | New nDCG | Delta points | New recall | New MRR | New full coverage | Improved / regressed / tied |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| basic | 24 | 67.09 | 69.12 | +2.03 | 91.67 | 62.02 | 91.67 | 9 / 1 / 14 |
| completeness | 12 | 44.37 | 47.72 | +3.36 | 54.65 | 57.18 | 25.00 | 7 / 3 / 2 |
| conflicting_info | 4 | 73.54 | 86.39 | +12.85 | 100.00 | 80.00 | 100.00 | 2 / 0 / 2 |
| constrained | 8 | 49.13 | 55.08 | +5.96 | 75.00 | 53.12 | 62.50 | 4 / 0 / 4 |
| high_level | 0 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | 0 / 0 / 0 |
| info_not_found | 0 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | 0 / 0 / 0 |
| intra_document_reasoning | 12 | 68.13 | 71.63 | +3.50 | 100.00 | 62.43 | 100.00 | 4 / 0 / 8 |
| miscellaneous | 8 | 59.97 | 66.73 | +6.76 | 100.00 | 56.37 | 100.00 | 3 / 0 / 5 |
| project_related | 12 | 55.23 | 64.24 | +9.01 | 73.01 | 82.64 | 25.00 | 11 / 0 / 1 |
| semantic | 32 | 23.10 | 31.08 | +7.98 | 59.38 | 22.09 | 59.38 | 17 / 0 / 15 |

[Family result](README.md) · [General comparison](comparison.md) · [CTA](cta.md) · [Full metrics](aggregate.json)
