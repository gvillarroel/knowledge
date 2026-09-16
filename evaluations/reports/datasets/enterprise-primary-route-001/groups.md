# EnterpriseRAG: application and category observations

All rows use the same 500 public questions, 470 retrieval-eligible questions and 6,000 complete documents. Quality is native nDCG@10 multiplied by 100. Entity Graph and Ensemble execute only their primary outer route; the other six rows retain the earlier all-declared-routes treatment. These are source-linked observations across three jobs, with different mode exposure, cache history and observation times.

The six retained columns are transcribed from the approved previous aggregate. New columns use the native verifier's existing per-question rewards, with identical eligible membership and original weights. Applications overlap. Highest observed is the descriptive maximum among available columns, with no statistical superiority claim.

| Dimension | Group | Eligible questions | legacy | embeddings | classical | adaptive | entity-graph | ensemble | graphify | turso | Highest observed |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| all | all | 470 | 70.72 | 64.04 | 56.16 | 63.61 | 34.96 | Unavailable | 60.50 | 70.72 | legacy, turso |
| application | confluence | 115 | 73.46 | 67.00 | 59.84 | 69.24 | 50.36 | Unavailable | 65.44 | 73.46 | legacy, turso |
| application | fireflies | 25 | 60.14 | 47.36 | 60.46 | 52.52 | 32.86 | Unavailable | 60.47 | 60.14 | graphify |
| application | github | 60 | 66.30 | 71.09 | 57.94 | 64.86 | 22.99 | Unavailable | 59.61 | 66.30 | embeddings |
| application | gmail | 55 | 75.45 | 47.89 | 51.25 | 57.21 | 40.52 | Unavailable | 61.97 | 75.45 | legacy, turso |
| application | google-drive | 60 | 69.55 | 55.53 | 52.48 | 60.64 | 39.06 | Unavailable | 62.64 | 69.55 | legacy, turso |
| application | hubspot | 34 | 65.21 | 59.19 | 47.44 | 56.49 | 14.46 | Unavailable | 55.80 | 65.21 | legacy, turso |
| application | jira | 100 | 78.12 | 77.00 | 63.81 | 70.81 | 44.16 | Unavailable | 69.60 | 78.12 | legacy, turso |
| application | linear | 58 | 75.65 | 74.48 | 67.85 | 75.26 | 37.32 | Unavailable | 66.81 | 75.65 | legacy, turso |
| application | slack | 79 | 62.19 | 62.68 | 50.81 | 58.66 | 26.77 | Unavailable | 48.23 | 62.19 | embeddings |
| category | basic | 175 | 77.70 | 69.13 | 63.92 | 71.56 | 35.59 | Unavailable | 67.64 | 77.70 | legacy, turso |
| category | completeness | 20 | 59.02 | 57.86 | 31.68 | 66.32 | 14.00 | Unavailable | 56.41 | 59.02 | adaptive |
| category | conflicting_info | 20 | 91.96 | 77.83 | 86.42 | 86.84 | 64.78 | Unavailable | 87.14 | 91.96 | legacy, turso |
| category | constrained | 30 | 88.66 | 87.38 | 83.14 | 90.73 | 61.82 | Unavailable | 71.10 | 88.66 | adaptive |
| category | high_level | 0 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable |
| category | info_not_found | 0 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable |
| category | intra_document_reasoning | 40 | 92.95 | 75.38 | 85.00 | 92.87 | 49.00 | Unavailable | 74.86 | 92.95 | legacy, turso |
| category | miscellaneous | 20 | 86.62 | 88.74 | 88.15 | 91.58 | 14.46 | Unavailable | 74.77 | 86.62 | adaptive |
| category | project_related | 40 | 71.25 | 67.24 | 60.26 | 65.89 | 49.50 | Unavailable | 66.87 | 71.25 | legacy, turso |
| category | semantic | 125 | 45.31 | 41.49 | 22.25 | 27.24 | 20.35 | Unavailable | 35.44 | 45.31 | legacy, turso |

**Entity Graph and Ensemble: primary-route-only. All other columns: all-declared-routes.** [Sources and outcomes](README.md) · [Dataset boundaries](datasets.md)
