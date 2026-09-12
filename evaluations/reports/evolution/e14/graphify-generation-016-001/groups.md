# EnterpriseRAG E14: Graphify generation 16 paired groups

Compare `versioned-016` with `versioned-010`. All values use a 0–100 scale and full-precision differences. Applications overlap. Groups without retrieval references have unavailable quality. No application router is selected or tested.

## Application

| Group | Eligible | Previous nDCG | New nDCG | Delta points | New recall | New MRR | New full coverage | Improved / regressed / tied |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| confluence | 39 | 62.75 | 62.87 | +0.12 | 76.82 | 64.65 | 59.08 | 1 / 1 / 37 |
| fireflies | 9 | 70.91 | 70.91 | +0.00 | 83.86 | 67.45 | 83.23 | 0 / 0 / 9 |
| github | 12 | 68.25 | 68.16 | -0.09 | 77.41 | 80.68 | 57.04 | 0 / 1 / 11 |
| gmail | 10 | 68.59 | 68.59 | +0.00 | 95.30 | 61.47 | 86.63 | 0 / 0 / 10 |
| google_drive | 14 | 82.82 | 82.74 | -0.07 | 85.91 | 88.19 | 72.19 | 0 / 1 / 13 |
| hubspot | 9 | 70.96 | 70.96 | +0.00 | 82.76 | 66.95 | 82.76 | 0 / 0 / 9 |
| jira | 26 | 67.92 | 68.97 | +1.05 | 87.11 | 69.81 | 72.52 | 1 / 1 / 24 |
| linear | 15 | 65.23 | 65.23 | +0.00 | 84.17 | 61.94 | 74.27 | 0 / 0 / 15 |
| slack | 24 | 46.88 | 47.11 | +0.24 | 69.70 | 44.77 | 58.91 | 1 / 0 / 23 |

## Category

| Group | Eligible | Previous nDCG | New nDCG | Delta points | New recall | New MRR | New full coverage | Improved / regressed / tied |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| basic | 24 | 75.65 | 75.65 | +0.00 | 91.67 | 70.45 | 91.67 | 0 / 0 / 24 |
| completeness | 12 | 52.02 | 52.02 | +0.00 | 56.60 | 66.32 | 25.00 | 0 / 0 / 12 |
| conflicting_info | 4 | 87.53 | 87.53 | +0.00 | 100.00 | 81.25 | 100.00 | 0 / 0 / 4 |
| constrained | 8 | 66.53 | 70.15 | +3.61 | 93.75 | 67.92 | 87.50 | 1 / 0 / 7 |
| high_level | 0 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | 0 / 0 / 0 |
| info_not_found | 0 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | 0 / 0 / 0 |
| intra_document_reasoning | 12 | 88.01 | 88.01 | +0.00 | 100.00 | 84.03 | 100.00 | 0 / 0 / 12 |
| miscellaneous | 8 | 73.97 | 73.97 | +0.00 | 100.00 | 65.62 | 100.00 | 0 / 0 / 8 |
| project_related | 12 | 67.55 | 67.96 | +0.41 | 75.79 | 85.00 | 33.33 | 1 / 1 / 10 |
| semantic | 32 | 32.77 | 32.77 | +0.00 | 59.38 | 24.15 | 59.38 | 0 / 0 / 32 |

[Family result](README.md) · [General comparison](comparison.md) · [CTA](cta.md) · [Full metrics](aggregate.json)
