# E13 Turso baseline: applications, categories and datasets

This is the new generation-zero **Turso reference**, measured on the frozen EnterpriseRAG development subset. Its primary route is `lexical-sql`. These aggregates reconcile the original native verifier cases; no question was reranked or rescored.

Scores are frozen-category-weighted nDCG@10 multiplied by 100. Application groups overlap because one question may reference several applications. Their counts and weighted means must not be added together. Category groups are disjoint. Eight questions without retrieval references remain outside the retrieval denominator.

## Application groups

| Group | Questions | Retrieval eligible | Weighted nDCG@10 x100 | Weighted Recall@10 x100 |
| --- | ---: | ---: | ---: | ---: |
| confluence | 39 | 39 | 52.55 | 56.51 |
| fireflies | 9 | 9 | 69.09 | 76.83 |
| github | 12 | 12 | 24.81 | 33.82 |
| gmail | 10 | 10 | 51.03 | 64.20 |
| google_drive | 14 | 14 | 53.97 | 52.38 |
| hubspot | 9 | 9 | 28.43 | 33.33 |
| jira | 26 | 26 | 49.29 | 52.31 |
| linear | 15 | 15 | 41.52 | 59.43 |
| slack | 24 | 24 | 30.42 | 41.74 |

## Category groups

| Group | Questions | Retrieval eligible | Weighted nDCG@10 x100 | Weighted Recall@10 x100 |
| --- | ---: | ---: | ---: | ---: |
| basic | 24 | 24 | 50.75 | 66.67 |
| completeness | 12 | 12 | 15.84 | 13.33 |
| conflicting_info | 4 | 4 | 74.44 | 75.00 |
| constrained | 8 | 8 | 79.12 | 81.25 |
| high_level | 4 | 0 | Unavailable | Unavailable |
| info_not_found | 4 | 0 | Unavailable | Unavailable |
| intra_document_reasoning | 12 | 12 | 73.99 | 91.67 |
| miscellaneous | 8 | 8 | 87.50 | 87.50 |
| project_related | 12 | 12 | 35.20 | 39.63 |
| semantic | 32 | 32 | 17.38 | 21.88 |

## Dataset availability

| Evaluation contract | E13 result |
| --- | --- |
| EnterpriseRAG stratified development: 120 questions, 112 eligible, 6,000 complete documents | One Turso baseline, 45.43 weighted nDCG@10 x100 |
| Eight-family paired all-500 recalculation | Not completed |
| Independent whole-bundle validation | Unreleased |
| Generated-answer Overall / public leaderboard | No new result |
| Other internal datasets | No E13 evaluation |

This checkpoint does not compare new per-application expert skills or show that application splitting improves retrieval. See the [application-skill experiment](../../../../../docs/enterprise-source-skills.md) and the [historical dataset comparison hub](../../../README.md#historical-retrieval-comparisons) for their separate contracts.

[Eight-family status](README.md) · [CTA](cta.md) · [Aggregate](aggregate.json)
