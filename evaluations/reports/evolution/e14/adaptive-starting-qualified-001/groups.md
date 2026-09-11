# Adaptive starting roles by application and question category

Weighted primary-route metrics use the fixed development questions and existing native verifier case metrics. Application membership may overlap. Category groups partition all 120 questions.

## Applications

| Group | Questions | Eligible | baseline | retained-start |
| --- | ---: | ---: | ---: | ---: |
| confluence | 39 | 39 | 63.89 | 68.09 |
| fireflies | 9 | 9 | 79.20 | 69.60 |
| github | 12 | 12 | 54.21 | 62.71 |
| gmail | 10 | 10 | 58.46 | 71.15 |
| google_drive | 14 | 14 | 59.30 | 68.73 |
| hubspot | 9 | 9 | 59.62 | 59.97 |
| jira | 26 | 26 | 65.44 | 69.16 |
| linear | 15 | 15 | 73.71 | 81.33 |
| slack | 24 | 24 | 41.43 | 50.16 |

## Question categories

| Group | Questions | Eligible | baseline | retained-start |
| --- | ---: | ---: | ---: | ---: |
| basic | 24 | 24 | 75.92 | 84.72 |
| completeness | 12 | 12 | 51.32 | 62.90 |
| conflicting_info | 4 | 4 | 90.33 | 96.26 |
| constrained | 8 | 8 | 78.62 | 80.70 |
| high_level | 4 | 0 | Unavailable | Unavailable |
| info_not_found | 4 | 0 | Unavailable | Unavailable |
| intra_document_reasoning | 12 | 12 | 100.00 | 100.00 |
| miscellaneous | 8 | 8 | 73.20 | 87.50 |
| project_related | 12 | 12 | 57.28 | 60.27 |
| semantic | 32 | 32 | 15.87 | 20.22 |

Quality columns are nDCG@10 on a 0–100 scale. The four `high_level` and four `info_not_found` questions have no retrieval references; their scores stay unavailable. The aggregate also includes Recall@10, MRR@10, full reference coverage, population weights and paired improved/regressed/tied counts. Subgroups do not create independent native tasks or select a new incumbent.

[Quality and opportunities](README.md) · [CTA](cta.md) · [Aggregate](aggregate.json)
