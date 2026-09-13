# EnterpriseRAG closure: retained application and category results

These are the original E14 retained development observations. All values are
frozen-category-weighted nDCG@10 ×100 on the 120-question, 6,000-document
workload. Application groups overlap. Unavailable cells are not zero scores.

## Application

| Group | Eligible questions | Legacy | Turso | Adaptive | Graphify | Embeddings | Classical | Entity Graph | Ensemble | Highest retained value |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| confluence | 39 | 69.99 | 69.99 | 68.09 | 62.87 | 70.99 | 60.05 | Unavailable | Unavailable | Embeddings |
| fireflies | 9 | 77.65 | 77.65 | 69.60 | 70.91 | 56.10 | 78.91 | Unavailable | Unavailable | Classical |
| github | 12 | 64.76 | 64.76 | 62.71 | 68.16 | 67.29 | 57.63 | Unavailable | Unavailable | Graphify |
| gmail | 10 | 72.19 | 72.19 | 71.15 | 68.59 | 49.64 | 50.07 | Unavailable | Unavailable | Legacy, Turso |
| google_drive | 14 | 76.29 | 76.29 | 68.73 | 82.74 | 66.33 | 62.33 | Unavailable | Unavailable | Graphify |
| hubspot | 9 | 74.14 | 74.14 | 59.97 | 70.96 | 63.68 | 56.90 | Unavailable | Unavailable | Legacy, Turso |
| jira | 26 | 79.77 | 79.77 | 69.16 | 68.97 | 65.37 | 65.61 | Unavailable | Unavailable | Legacy, Turso |
| linear | 15 | 83.06 | 83.06 | 81.33 | 65.23 | 69.72 | 83.23 | Unavailable | Unavailable | Classical |
| slack | 24 | 56.20 | 56.20 | 50.16 | 47.11 | 62.80 | 46.68 | Unavailable | Unavailable | Embeddings |

## Category

| Group | Eligible questions | Legacy | Turso | Adaptive | Graphify | Embeddings | Classical | Entity Graph | Ensemble | Highest retained value |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| basic | 24 | 84.80 | 84.80 | 84.72 | 75.65 | 71.54 | 79.17 | Unavailable | Unavailable | Legacy, Turso |
| completeness | 12 | 55.71 | 55.71 | 62.90 | 52.02 | 52.20 | 31.00 | Unavailable | Unavailable | Adaptive |
| conflicting_info | 4 | 100.00 | 100.00 | 96.26 | 87.53 | 78.30 | 90.33 | Unavailable | Unavailable | Legacy, Turso |
| constrained | 8 | 87.84 | 87.84 | 80.70 | 70.15 | 86.92 | 71.46 | Unavailable | Unavailable | Legacy, Turso |
| high_level | 0 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable |
| info_not_found | 0 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable |
| intra_document_reasoning | 12 | 100.00 | 100.00 | 100.00 | 88.01 | 82.89 | 100.00 | Unavailable | Unavailable | Adaptive, Classical, Legacy, Turso |
| miscellaneous | 8 | 92.88 | 92.88 | 87.50 | 73.97 | 90.77 | 87.50 | Unavailable | Unavailable | Legacy, Turso |
| project_related | 12 | 63.62 | 63.62 | 60.27 | 67.96 | 71.66 | 54.96 | Unavailable | Unavailable | Embeddings |
| semantic | 32 | 40.20 | 40.20 | 20.22 | 32.77 | 32.90 | 22.53 | Unavailable | Unavailable | Legacy, Turso |

Leaders are descriptive, using the original full-precision comparison and its
tie rule. No statistical significance, application routing or new skill selection
is established. Categories without original retrieval references remain unavailable.

[Final table and limitations](README.md) · [Full precision](aggregate.json) · [CTA](cta.md)
