# Classical starting roles by application and question category

Weighted primary-route metrics use the fixed development questions and existing native verifier case metrics. Application membership may overlap. Category groups partition all 120 questions.

## Applications

| Group | Questions | Eligible | baseline | retained-start |
| --- | ---: | ---: | ---: | ---: |
| confluence | 39 | 39 | 58.37 | 60.05 |
| fireflies | 9 | 9 | 78.69 | 78.91 |
| github | 12 | 12 | 48.20 | 57.63 |
| gmail | 10 | 10 | 50.02 | 50.07 |
| google_drive | 14 | 14 | 55.27 | 62.33 |
| hubspot | 9 | 9 | 56.90 | 56.90 |
| jira | 26 | 26 | 62.65 | 65.61 |
| linear | 15 | 15 | 65.90 | 83.23 |
| slack | 24 | 24 | 34.71 | 46.68 |

## Question categories

| Group | Questions | Eligible | baseline | retained-start |
| --- | ---: | ---: | ---: | ---: |
| basic | 24 | 24 | 70.83 | 79.17 |
| completeness | 12 | 12 | 32.01 | 31.00 |
| conflicting_info | 4 | 4 | 90.33 | 90.33 |
| constrained | 8 | 8 | 68.16 | 71.46 |
| high_level | 4 | 0 | Unavailable | Unavailable |
| info_not_found | 4 | 0 | Unavailable | Unavailable |
| intra_document_reasoning | 12 | 12 | 100.00 | 100.00 |
| miscellaneous | 8 | 8 | 68.75 | 87.50 |
| project_related | 12 | 12 | 52.91 | 54.96 |
| semantic | 32 | 32 | 11.93 | 22.53 |

Quality columns are nDCG@10 on a 0–100 scale. The four `high_level` and four `info_not_found` questions have no retrieval references; their scores stay unavailable. The aggregate also includes Recall@10, MRR@10, full reference coverage and population weights. It also includes paired improved/regressed/tied counts. Subgroups do not create independent native tasks or select a new incumbent.

[Quality and opportunities](README.md) · [CTA](cta.md) · [Aggregate](aggregate.json)
