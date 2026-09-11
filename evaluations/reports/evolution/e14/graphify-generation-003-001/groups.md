# EnterpriseRAG E14: Graphify generation 3 paired groups

Compare `versioned-003` with `baseline`. All values use a 0–100 scale and full-precision differences. Applications overlap. Groups without retrieval references have unavailable quality. No application router is selected or tested.

## Application

| Group | Eligible | Previous nDCG | New nDCG | Delta points | New recall | New MRR | New full coverage | Improved / regressed / tied |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| confluence | 39 | 9.82 | 28.07 | +18.25 | 33.27 | 36.87 | 22.36 | 17 / 3 / 19 |
| fireflies | 9 | 4.75 | 49.35 | +44.60 | 52.41 | 51.41 | 51.41 | 3 / 1 / 5 |
| github | 12 | 11.03 | 24.03 | +13.00 | 26.51 | 43.88 | 8.88 | 6 / 0 / 6 |
| gmail | 10 | 16.88 | 21.69 | +4.81 | 49.65 | 19.00 | 47.77 | 3 / 2 / 5 |
| google_drive | 14 | 17.72 | 57.01 | +39.29 | 61.44 | 67.72 | 52.84 | 9 / 2 / 3 |
| hubspot | 9 | 0.00 | 32.18 | +32.18 | 32.18 | 32.18 | 32.18 | 2 / 0 / 7 |
| jira | 26 | 5.45 | 30.72 | +25.27 | 31.99 | 42.56 | 22.70 | 12 / 1 / 13 |
| linear | 15 | 12.83 | 23.85 | +11.02 | 36.05 | 24.60 | 30.70 | 5 / 2 / 8 |
| slack | 24 | 2.82 | 8.92 | +6.10 | 7.51 | 19.20 | 0.00 | 6 / 0 / 18 |

## Category

| Group | Eligible | Previous nDCG | New nDCG | Delta points | New recall | New MRR | New full coverage | Improved / regressed / tied |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| basic | 24 | 10.13 | 42.18 | +32.05 | 54.17 | 38.19 | 54.17 | 10 / 3 / 11 |
| completeness | 12 | 16.69 | 26.69 | +10.00 | 24.03 | 41.67 | 8.33 | 4 / 1 / 7 |
| conflicting_info | 4 | 18.72 | 50.00 | +31.28 | 50.00 | 50.00 | 50.00 | 2 / 0 / 2 |
| constrained | 8 | 6.05 | 17.45 | +11.40 | 25.00 | 15.83 | 12.50 | 1 / 1 / 6 |
| high_level | 0 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | 0 / 0 / 0 |
| info_not_found | 0 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | 0 / 0 / 0 |
| intra_document_reasoning | 12 | 6.10 | 39.33 | +33.23 | 50.00 | 36.25 | 50.00 | 4 / 1 / 7 |
| miscellaneous | 8 | 18.11 | 27.66 | +9.55 | 50.00 | 20.83 | 50.00 | 1 / 3 / 4 |
| project_related | 12 | 9.44 | 30.75 | +21.31 | 28.94 | 65.28 | 0.00 | 9 / 1 / 2 |
| semantic | 32 | 1.35 | 2.55 | +1.21 | 6.25 | 1.41 | 6.25 | 1 / 0 / 31 |

[Family result](README.md) · [General comparison](comparison.md) · [CTA](cta.md) · [Full metrics](aggregate.json)
