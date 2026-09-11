# Turso starting pair by application and question category

These are weighted native retrieval aggregates from the same fixed development workload. They compare the original E13 reference with the newly reproduced E14 retained profile. They do not select application-specific winners or alter the primary retention decision.

## Applications

| Group | Questions | Eligible | Reference nDCG@10 | Retained nDCG@10 | Delta, points |
| --- | ---: | ---: | ---: | ---: | ---: |
| confluence | 39 | 39 | 52.55 | 69.70 | +17.15 |
| fireflies | 9 | 9 | 69.09 | 78.19 | +9.10 |
| github | 12 | 12 | 24.81 | 62.58 | +37.77 |
| gmail | 10 | 10 | 51.03 | 72.52 | +21.49 |
| google_drive | 14 | 14 | 53.97 | 73.08 | +19.11 |
| hubspot | 9 | 9 | 28.43 | 75.27 | +46.84 |
| jira | 26 | 26 | 49.29 | 77.80 | +28.51 |
| linear | 15 | 15 | 41.52 | 82.16 | +40.65 |
| slack | 24 | 24 | 30.42 | 56.36 | +25.94 |

## Question categories

| Group | Questions | Eligible | Reference nDCG@10 | Retained nDCG@10 | Delta, points |
| --- | ---: | ---: | ---: | ---: | ---: |
| basic | 24 | 24 | 50.75 | 84.44 | +33.68 |
| completeness | 12 | 12 | 15.84 | 55.53 | +39.68 |
| conflicting_info | 4 | 4 | 74.44 | 97.99 | +23.55 |
| constrained | 8 | 8 | 79.12 | 88.05 | +8.92 |
| high_level | 4 | 0 | Unavailable | Unavailable | Unavailable |
| info_not_found | 4 | 0 | Unavailable | Unavailable | Unavailable |
| intra_document_reasoning | 12 | 12 | 73.99 | 100.00 | +26.01 |
| miscellaneous | 8 | 8 | 87.50 | 92.88 | +5.38 |
| project_related | 12 | 12 | 35.20 | 60.68 | +25.47 |
| semantic | 32 | 32 | 17.38 | 40.83 | +23.45 |

Application groups overlap because a question can cite multiple applications. Category groups partition the 120 questions. The four `high_level` and four `info_not_found` questions have no retrieval references; their quality remains unavailable. Group counts and weighted deltas do not create additional independent Harbor tasks.

The [aggregate](aggregate.json) includes Recall@10, MRR@10, full reference coverage, population weights and paired improved/regressed/tied counts for every group. The full-500, full-corpus Classical and Luna answer contracts remain separate.

[Quality and opportunity status](README.md) · [CTA](cta.md) · [Dataset view](../../../datasets/enterprise-rag-stratified-development-120.md)
