# EnterpriseRAG E14: Graphify generation 8 paired groups

Compare `versioned-008` with `versioned-007`. All values use a 0–100 scale and full-precision differences. Applications overlap. Groups without retrieval references have unavailable quality. No application router is selected or tested.

## Application

| Group | Eligible | Previous nDCG | New nDCG | Delta points | New recall | New MRR | New full coverage | Improved / regressed / tied |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| confluence | 39 | 36.82 | 53.89 | +17.07 | 75.26 | 56.61 | 52.96 | 27 / 1 / 11 |
| fireflies | 9 | 54.19 | 64.34 | +10.15 | 78.84 | 62.15 | 73.20 | 5 / 0 / 4 |
| github | 12 | 36.46 | 51.98 | +15.52 | 70.30 | 61.90 | 41.89 | 8 / 2 / 2 |
| gmail | 10 | 35.27 | 55.05 | +19.78 | 78.66 | 51.86 | 67.27 | 6 / 0 / 4 |
| google_drive | 14 | 62.00 | 71.17 | +9.17 | 81.61 | 76.54 | 66.23 | 6 / 0 / 8 |
| hubspot | 9 | 32.18 | 54.65 | +22.47 | 82.76 | 45.91 | 82.76 | 5 / 0 / 4 |
| jira | 26 | 38.44 | 55.02 | +16.58 | 74.75 | 56.24 | 56.38 | 16 / 3 / 7 |
| linear | 15 | 32.64 | 57.56 | +24.92 | 82.29 | 55.22 | 74.27 | 9 / 0 / 6 |
| slack | 24 | 13.58 | 32.71 | +19.12 | 55.86 | 34.11 | 42.83 | 17 / 2 / 5 |

## Category

| Group | Eligible | Previous nDCG | New nDCG | Delta points | New recall | New MRR | New full coverage | Improved / regressed / tied |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| basic | 24 | 47.47 | 67.09 | +19.62 | 91.67 | 59.52 | 91.67 | 12 / 1 / 11 |
| completeness | 12 | 33.85 | 44.37 | +10.52 | 48.82 | 55.35 | 8.33 | 8 / 2 / 2 |
| conflicting_info | 4 | 50.00 | 73.54 | +23.54 | 100.00 | 61.90 | 100.00 | 2 / 0 / 2 |
| constrained | 8 | 25.00 | 49.13 | +24.13 | 68.75 | 50.12 | 50.00 | 5 / 0 / 3 |
| high_level | 0 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | 0 / 0 / 0 |
| info_not_found | 0 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | 0 / 0 / 0 |
| intra_document_reasoning | 12 | 45.83 | 68.13 | +22.29 | 100.00 | 58.15 | 100.00 | 6 / 0 / 6 |
| miscellaneous | 8 | 45.39 | 59.97 | +14.58 | 100.00 | 47.51 | 100.00 | 4 / 0 / 4 |
| project_related | 12 | 45.00 | 55.23 | +10.23 | 59.54 | 81.25 | 8.33 | 10 / 1 / 1 |
| semantic | 32 | 6.25 | 23.10 | +16.85 | 53.12 | 14.07 | 53.12 | 14 / 0 / 18 |

[Family result](README.md) · [General comparison](comparison.md) · [CTA](cta.md) · [Full metrics](aggregate.json)
