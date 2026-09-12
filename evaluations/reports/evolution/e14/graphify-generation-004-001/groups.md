# EnterpriseRAG E14: Graphify generation 4 paired groups

Compare `versioned-004` with `versioned-003`. All values use a 0–100 scale and full-precision differences. Applications overlap. Groups without retrieval references have unavailable quality. No application router is selected or tested.

## Application

| Group | Eligible | Previous nDCG | New nDCG | Delta points | New recall | New MRR | New full coverage | Improved / regressed / tied |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| confluence | 39 | 28.07 | 28.32 | +0.25 | 32.91 | 36.60 | 22.36 | 3 / 2 / 34 |
| fireflies | 9 | 49.35 | 50.42 | +1.07 | 53.42 | 51.41 | 51.41 | 1 / 0 / 8 |
| github | 12 | 24.03 | 25.75 | +1.72 | 29.16 | 43.88 | 8.88 | 2 / 1 / 9 |
| gmail | 10 | 21.69 | 21.66 | -0.03 | 50.54 | 17.91 | 47.77 | 1 / 2 / 7 |
| google_drive | 14 | 57.01 | 56.85 | -0.16 | 61.44 | 67.61 | 52.84 | 0 / 2 / 12 |
| hubspot | 9 | 32.18 | 32.18 | +0.00 | 32.18 | 32.18 | 32.18 | 0 / 0 / 9 |
| jira | 26 | 30.72 | 31.84 | +1.12 | 33.50 | 42.56 | 22.70 | 3 / 1 / 22 |
| linear | 15 | 23.85 | 23.85 | +0.00 | 36.05 | 24.60 | 30.70 | 0 / 0 / 15 |
| slack | 24 | 8.92 | 9.59 | +0.67 | 8.28 | 19.20 | 0.00 | 2 / 0 / 22 |

## Category

| Group | Eligible | Previous nDCG | New nDCG | Delta points | New recall | New MRR | New full coverage | Improved / regressed / tied |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| basic | 24 | 42.18 | 42.18 | +0.00 | 54.17 | 38.19 | 54.17 | 0 / 0 / 24 |
| completeness | 12 | 26.69 | 30.24 | +3.55 | 28.40 | 41.67 | 8.33 | 3 / 0 / 9 |
| conflicting_info | 4 | 50.00 | 50.00 | +0.00 | 50.00 | 50.00 | 50.00 | 0 / 0 / 4 |
| constrained | 8 | 17.45 | 15.23 | -2.22 | 18.75 | 14.58 | 12.50 | 0 / 1 / 7 |
| high_level | 0 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | 0 / 0 / 0 |
| info_not_found | 0 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | 0 / 0 / 0 |
| intra_document_reasoning | 12 | 39.33 | 38.71 | -0.62 | 50.00 | 35.56 | 50.00 | 0 / 1 / 11 |
| miscellaneous | 8 | 27.66 | 27.37 | -0.29 | 50.00 | 20.54 | 50.00 | 0 / 1 / 7 |
| project_related | 12 | 30.75 | 32.08 | +1.33 | 31.02 | 65.28 | 0.00 | 1 / 1 / 10 |
| semantic | 32 | 2.55 | 2.46 | -0.10 | 6.25 | 1.30 | 6.25 | 0 / 1 / 31 |

[Family result](README.md) · [General comparison](comparison.md) · [CTA](cta.md) · [Full metrics](aggregate.json)
