# Graphify starting roles by application and question category

Weighted primary-route metrics use the fixed development questions and existing native verifier case metrics. Application membership may overlap. Category groups partition all 120 questions.

## Applications

| Group | Questions | Eligible | baseline |
| --- | ---: | ---: | ---: |
| confluence | 39 | 39 | 9.82 |
| fireflies | 9 | 9 | 4.75 |
| github | 12 | 12 | 11.03 |
| gmail | 10 | 10 | 16.88 |
| google_drive | 14 | 14 | 17.72 |
| hubspot | 9 | 9 | 0.00 |
| jira | 26 | 26 | 5.45 |
| linear | 15 | 15 | 12.83 |
| slack | 24 | 24 | 2.82 |

## Question categories

| Group | Questions | Eligible | baseline |
| --- | ---: | ---: | ---: |
| basic | 24 | 24 | 10.13 |
| completeness | 12 | 12 | 16.69 |
| conflicting_info | 4 | 4 | 18.72 |
| constrained | 8 | 8 | 6.05 |
| high_level | 4 | 0 | Unavailable |
| info_not_found | 4 | 0 | Unavailable |
| intra_document_reasoning | 12 | 12 | 6.10 |
| miscellaneous | 8 | 8 | 18.11 |
| project_related | 12 | 12 | 9.44 |
| semantic | 32 | 32 | 1.35 |

Quality columns are nDCG@10 on a 0–100 scale. The four `high_level` and four `info_not_found` questions have no retrieval references; their scores stay unavailable. The aggregate also includes Recall@10, MRR@10, full reference coverage and population weights. Paired improved/regressed/tied counts are unavailable because only one role is measured. Subgroups do not create independent native tasks or select a new incumbent.

[Quality and opportunities](README.md) · [CTA](cta.md) · [Aggregate](aggregate.json)
