# EnterpriseRAG E14: Graphify generation 10 paired groups

Compare `versioned-010` with `versioned-009`. All values use a 0–100 scale and full-precision differences. Applications overlap. Groups without retrieval references have unavailable quality. No application router is selected or tested.

## Application

| Group | Eligible | Previous nDCG | New nDCG | Delta points | New recall | New MRR | New full coverage | Improved / regressed / tied |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| confluence | 39 | 57.54 | 62.75 | +5.21 | 76.82 | 64.25 | 59.08 | 22 / 3 / 14 |
| fireflies | 9 | 69.14 | 70.91 | +1.77 | 83.86 | 67.45 | 83.23 | 4 / 0 / 5 |
| github | 12 | 59.45 | 68.25 | +8.80 | 77.41 | 80.68 | 57.04 | 6 / 2 / 4 |
| gmail | 10 | 63.18 | 68.59 | +5.41 | 95.30 | 61.47 | 86.63 | 5 / 0 / 5 |
| google_drive | 14 | 80.14 | 82.82 | +2.68 | 85.91 | 88.19 | 72.19 | 6 / 0 / 8 |
| hubspot | 9 | 64.42 | 70.96 | +6.54 | 82.76 | 66.95 | 82.76 | 2 / 0 / 7 |
| jira | 26 | 60.93 | 67.92 | +6.98 | 83.33 | 69.43 | 68.73 | 13 / 2 / 11 |
| linear | 15 | 62.24 | 65.23 | +2.99 | 84.17 | 61.94 | 74.27 | 5 / 0 / 10 |
| slack | 24 | 40.45 | 46.88 | +6.43 | 69.70 | 44.13 | 58.91 | 14 / 2 / 8 |

## Category

| Group | Eligible | Previous nDCG | New nDCG | Delta points | New recall | New MRR | New full coverage | Improved / regressed / tied |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| basic | 24 | 69.12 | 75.65 | +6.53 | 91.67 | 70.45 | 91.67 | 7 / 0 / 17 |
| completeness | 12 | 47.72 | 52.02 | +4.30 | 56.60 | 66.32 | 25.00 | 8 / 2 / 2 |
| conflicting_info | 4 | 86.39 | 87.53 | +1.14 | 100.00 | 81.25 | 100.00 | 1 / 0 / 3 |
| constrained | 8 | 55.08 | 66.53 | +11.45 | 81.25 | 66.67 | 75.00 | 5 / 0 / 3 |
| high_level | 0 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | 0 / 0 / 0 |
| info_not_found | 0 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | 0 / 0 / 0 |
| intra_document_reasoning | 12 | 71.63 | 88.01 | +16.39 | 100.00 | 84.03 | 100.00 | 7 / 0 / 5 |
| miscellaneous | 8 | 66.73 | 73.97 | +7.24 | 100.00 | 65.62 | 100.00 | 4 / 0 / 4 |
| project_related | 12 | 64.24 | 67.55 | +3.31 | 75.79 | 83.61 | 33.33 | 7 / 2 / 3 |
| semantic | 32 | 31.08 | 32.77 | +1.69 | 59.38 | 24.15 | 59.38 | 7 / 0 / 25 |

[Family result](README.md) · [General comparison](comparison.md) · [CTA](cta.md) · [Full metrics](aggregate.json)
