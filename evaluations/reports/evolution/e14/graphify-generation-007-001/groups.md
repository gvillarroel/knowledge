# EnterpriseRAG E14: Graphify generation 7 paired groups

Compare `versioned-007` with `versioned-004`. All values use a 0–100 scale and full-precision differences. Applications overlap. Groups without retrieval references have unavailable quality. No application router is selected or tested.

## Application

| Group | Eligible | Previous nDCG | New nDCG | Delta points | New recall | New MRR | New full coverage | Improved / regressed / tied |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| confluence | 39 | 28.32 | 36.82 | +8.50 | 36.52 | 48.38 | 22.36 | 13 / 0 / 26 |
| fireflies | 9 | 50.42 | 54.19 | +3.76 | 53.42 | 56.43 | 51.41 | 1 / 0 / 8 |
| github | 12 | 25.75 | 36.46 | +10.71 | 36.10 | 54.32 | 16.45 | 7 / 1 / 4 |
| gmail | 10 | 21.66 | 35.27 | +13.62 | 52.53 | 35.24 | 47.77 | 5 / 0 / 5 |
| google_drive | 14 | 56.85 | 62.00 | +5.14 | 63.92 | 72.93 | 52.84 | 6 / 0 / 8 |
| hubspot | 9 | 32.18 | 32.18 | +0.00 | 32.18 | 32.18 | 32.18 | 0 / 0 / 9 |
| jira | 26 | 31.84 | 38.44 | +6.60 | 37.33 | 47.92 | 26.06 | 9 / 1 / 16 |
| linear | 15 | 23.85 | 32.64 | +8.79 | 41.69 | 36.49 | 36.34 | 6 / 0 / 9 |
| slack | 24 | 9.59 | 13.58 | +3.99 | 13.29 | 24.00 | 6.72 | 5 / 1 / 18 |

## Category

| Group | Eligible | Previous nDCG | New nDCG | Delta points | New recall | New MRR | New full coverage | Improved / regressed / tied |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| basic | 24 | 42.18 | 47.47 | +5.29 | 54.17 | 45.14 | 54.17 | 5 / 0 / 19 |
| completeness | 12 | 30.24 | 33.85 | +3.61 | 30.83 | 46.88 | 8.33 | 3 / 1 / 8 |
| conflicting_info | 4 | 50.00 | 50.00 | +0.00 | 50.00 | 50.00 | 50.00 | 0 / 0 / 4 |
| constrained | 8 | 15.23 | 25.00 | +9.77 | 25.00 | 31.25 | 12.50 | 2 / 0 / 6 |
| high_level | 0 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | 0 / 0 / 0 |
| info_not_found | 0 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | 0 / 0 / 0 |
| intra_document_reasoning | 12 | 38.71 | 45.83 | +7.12 | 50.00 | 44.44 | 50.00 | 2 / 0 / 10 |
| miscellaneous | 8 | 27.37 | 45.39 | +18.02 | 62.50 | 39.58 | 62.50 | 4 / 0 / 4 |
| project_related | 12 | 32.08 | 45.00 | +12.92 | 40.51 | 79.17 | 8.33 | 9 / 0 / 3 |
| semantic | 32 | 2.46 | 6.25 | +3.79 | 9.38 | 5.21 | 9.38 | 3 / 0 / 29 |

[Family result](README.md) · [General comparison](comparison.md) · [CTA](cta.md) · [Full metrics](aggregate.json)
