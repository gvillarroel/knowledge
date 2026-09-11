# Legacy starting roles by application and question category

Weighted primary-route metrics use the fixed development questions and existing native verifier case metrics. Application membership may overlap. Category groups partition all 120 questions.

## Applications

| Group | Questions | Eligible | baseline | retained-start |
| --- | ---: | ---: | ---: | ---: |
| confluence | 39 | 39 | 64.40 | 69.99 |
| fireflies | 9 | 9 | 77.90 | 77.65 |
| github | 12 | 12 | 42.86 | 64.76 |
| gmail | 10 | 10 | 48.54 | 72.19 |
| google_drive | 14 | 14 | 63.44 | 76.29 |
| hubspot | 9 | 9 | 52.22 | 74.14 |
| jira | 26 | 26 | 68.35 | 79.77 |
| linear | 15 | 15 | 67.58 | 83.06 |
| slack | 24 | 24 | 46.74 | 56.20 |

## Question categories

| Group | Questions | Eligible | baseline | retained-start |
| --- | ---: | ---: | ---: | ---: |
| basic | 24 | 24 | 73.02 | 84.80 |
| completeness | 12 | 12 | 20.63 | 55.71 |
| conflicting_info | 4 | 4 | 90.71 | 100.00 |
| constrained | 8 | 8 | 86.38 | 87.84 |
| high_level | 4 | 0 | Unavailable | Unavailable |
| info_not_found | 4 | 0 | Unavailable | Unavailable |
| intra_document_reasoning | 12 | 12 | 93.85 | 100.00 |
| miscellaneous | 8 | 8 | 92.34 | 92.88 |
| project_related | 12 | 12 | 51.58 | 63.62 |
| semantic | 32 | 32 | 27.67 | 40.20 |

Quality columns are nDCG@10 on a 0–100 scale. The four `high_level` and four `info_not_found` questions have no retrieval references; their scores stay unavailable. The aggregate also includes Recall@10, MRR@10, full reference coverage, population weights and paired improved/regressed/tied counts. Subgroups do not create independent native tasks or select a new incumbent.

[Quality and opportunities](README.md) · [CTA](cta.md) · [Aggregate](aggregate.json)
