# Embeddings starting roles by application and question category

Weighted primary-route metrics use the fixed development questions and existing native verifier case metrics. Application membership may overlap. Category groups partition all 120 questions.

## Applications

| Group | Questions | Eligible | baseline |
| --- | ---: | ---: | ---: |
| confluence | 39 | 39 | 70.99 |
| fireflies | 9 | 9 | 56.10 |
| github | 12 | 12 | 67.29 |
| gmail | 10 | 10 | 49.64 |
| google_drive | 14 | 14 | 66.33 |
| hubspot | 9 | 9 | 63.68 |
| jira | 26 | 26 | 65.37 |
| linear | 15 | 15 | 69.72 |
| slack | 24 | 24 | 62.80 |

## Question categories

| Group | Questions | Eligible | baseline |
| --- | ---: | ---: | ---: |
| basic | 24 | 24 | 71.54 |
| completeness | 12 | 12 | 52.20 |
| conflicting_info | 4 | 4 | 78.30 |
| constrained | 8 | 8 | 86.92 |
| high_level | 4 | 0 | Unavailable |
| info_not_found | 4 | 0 | Unavailable |
| intra_document_reasoning | 12 | 12 | 82.89 |
| miscellaneous | 8 | 8 | 90.77 |
| project_related | 12 | 12 | 71.66 |
| semantic | 32 | 32 | 32.90 |

Quality columns are nDCG@10 on a 0–100 scale. The four `high_level` and four `info_not_found` questions have no retrieval references; their scores stay unavailable. The aggregate also includes Recall@10, MRR@10, full reference coverage and population weights. Paired improved/regressed/tied counts are unavailable because only one role is measured. Subgroups do not create independent native tasks or select a new incumbent.

[Quality and opportunities](README.md) · [CTA](cta.md) · [Aggregate](aggregate.json)
