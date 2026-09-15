# EnterpriseRAG: applications and categories

This is a partial diagnostic table: four strategies have qualified observations and four remain unavailable. Values are nDCG@10 multiplied by 100. These are projections of qualified native per-question rewards, using the frozen task weights and eligible membership. Application groups overlap and reflect applications with relevant documents available in the fixed corpus. The highest observed value is descriptive; it is not a promotion decision or a statistical superiority claim.

| Dimension | Group | Eligible questions | legacy | embeddings | classical | adaptive | entity-graph | ensemble | graphify | turso | Highest observed |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| all | all | 470 | 70.72 | 64.04 | 56.16 | 63.61 | Unavailable | Unavailable | Unavailable | Unavailable | legacy |
| application | confluence | 115 | 73.46 | 67.00 | 59.84 | 69.24 | Unavailable | Unavailable | Unavailable | Unavailable | legacy |
| application | fireflies | 25 | 60.14 | 47.36 | 60.46 | 52.52 | Unavailable | Unavailable | Unavailable | Unavailable | classical |
| application | github | 60 | 66.30 | 71.09 | 57.94 | 64.86 | Unavailable | Unavailable | Unavailable | Unavailable | embeddings |
| application | gmail | 55 | 75.45 | 47.89 | 51.25 | 57.21 | Unavailable | Unavailable | Unavailable | Unavailable | legacy |
| application | google-drive | 60 | 69.55 | 55.53 | 52.48 | 60.64 | Unavailable | Unavailable | Unavailable | Unavailable | legacy |
| application | hubspot | 34 | 65.21 | 59.19 | 47.44 | 56.49 | Unavailable | Unavailable | Unavailable | Unavailable | legacy |
| application | jira | 100 | 78.12 | 77.00 | 63.81 | 70.81 | Unavailable | Unavailable | Unavailable | Unavailable | legacy |
| application | linear | 58 | 75.65 | 74.48 | 67.85 | 75.26 | Unavailable | Unavailable | Unavailable | Unavailable | legacy |
| application | slack | 79 | 62.19 | 62.68 | 50.81 | 58.66 | Unavailable | Unavailable | Unavailable | Unavailable | embeddings |
| category | basic | 175 | 77.70 | 69.13 | 63.92 | 71.56 | Unavailable | Unavailable | Unavailable | Unavailable | legacy |
| category | completeness | 20 | 59.02 | 57.86 | 31.68 | 66.32 | Unavailable | Unavailable | Unavailable | Unavailable | adaptive |
| category | conflicting_info | 20 | 91.96 | 77.83 | 86.42 | 86.84 | Unavailable | Unavailable | Unavailable | Unavailable | legacy |
| category | constrained | 30 | 88.66 | 87.38 | 83.14 | 90.73 | Unavailable | Unavailable | Unavailable | Unavailable | adaptive |
| category | high_level | 0 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable |
| category | info_not_found | 0 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable |
| category | intra_document_reasoning | 40 | 92.95 | 75.38 | 85.00 | 92.87 | Unavailable | Unavailable | Unavailable | Unavailable | legacy |
| category | miscellaneous | 20 | 86.62 | 88.74 | 88.15 | 91.58 | Unavailable | Unavailable | Unavailable | Unavailable | adaptive |
| category | project_related | 40 | 71.25 | 67.24 | 60.26 | 65.89 | Unavailable | Unavailable | Unavailable | Unavailable | legacy |
| category | semantic | 125 | 45.31 | 41.49 | 22.25 | 27.24 | Unavailable | Unavailable | Unavailable | Unavailable | legacy |

[All strategies](README.md) · [Dataset scope](datasets.md).
