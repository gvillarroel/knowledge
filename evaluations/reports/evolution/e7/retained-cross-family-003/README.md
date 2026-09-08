# E7 retained profiles: provisional category and application comparison

This descriptive snapshot compares the four qualified profiles already retained at 2026-09-08T23:16:35.531431+00:00. Legacy and Embeddings have finished their searches; Classical and Adaptive are still evolving. Entity Graph, Ensemble, Graphify and Turso had no completed baseline and are omitted. The tables do not select or freeze a new profile and are not the final all-500 comparison.

## Observed primary metrics

| Family and retained candidate | Weighted nDCG@10 | Weighted recall@10 | Weighted MRR@10 | Weighted full qrel coverage@10 |
| --- | ---: | ---: | ---: | ---: |
| adaptive / candidate-009 | 65.23 | 71.23 | 67.33 | 64.41 |
| classical / candidate-011 | 60.10 | 63.59 | 63.88 | 56.91 |
| embeddings / baseline | 63.51 | 80.82 | 61.59 | 75.61 |
| legacy / candidate-009 | 72.38 | 81.99 | 71.51 | 76.43 |

The rows are alphabetical, without final ranking positions. Quality columns are percentages. Every value uses the same 120 stratified development questions, 112 eligible questions, eligible population weight 470 and 6,000 reference-enriched complete documents. The routes are fixed: Legacy lexical, Embeddings hybrid, Classical fusion and Adaptive adaptive.

## Question categories

| Group | Eligible questions | adaptive | classical | embeddings | legacy | Highest among these four |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| basic | 24 | 83.33 | 79.71 | 71.54 | 84.80 | legacy |
| completeness | 12 | 53.50 | 31.80 | 52.20 | 55.71 | legacy |
| conflicting_info | 4 | 95.16 | 90.33 | 78.30 | 100.00 | legacy |
| constrained | 8 | 76.20 | 65.33 | 86.92 | 87.84 | legacy |
| high_level | 0 | N/A | N/A | N/A | N/A | N/A |
| info_not_found | 0 | N/A | N/A | N/A | N/A | N/A |
| intra_document_reasoning | 12 | 100.00 | 100.00 | 82.89 | 100.00 | adaptive, classical, legacy |
| miscellaneous | 8 | 87.50 | 87.50 | 90.77 | 92.88 | legacy |
| project_related | 12 | 60.56 | 53.02 | 71.66 | 63.62 | embeddings |
| semantic | 32 | 21.15 | 16.19 | 32.90 | 40.20 | legacy |

## Application groups

| Group | Eligible questions | adaptive | classical | embeddings | legacy | Highest among these four |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| confluence | 39 | 65.07 | 56.41 | 70.99 | 69.99 | embeddings |
| fireflies | 9 | 79.64 | 78.32 | 56.10 | 77.65 | adaptive |
| github | 12 | 61.34 | 58.87 | 67.29 | 64.76 | embeddings |
| gmail | 10 | 71.10 | 52.82 | 49.64 | 72.19 | legacy |
| google_drive | 14 | 67.21 | 62.95 | 66.33 | 76.29 | legacy |
| hubspot | 9 | 59.62 | 56.90 | 63.68 | 74.14 | legacy |
| jira | 26 | 69.69 | 64.77 | 65.37 | 79.77 | legacy |
| linear | 15 | 79.91 | 77.16 | 69.72 | 83.06 | legacy |
| slack | 24 | 48.06 | 43.15 | 62.80 | 56.20 | embeddings |

Each group uses identical questions and denominators across the four profiles. Its mean renormalizes the frozen category weights within that group. Application groups overlap; their counts and scores must not be added. Highest-score labels use unrounded values and preserve ties within 1e-12. Groups without references have no score or highest profile.

All four source jobs completed with evidence integrity 1.0 and no execution errors or retries. This statement concerns the retained jobs: the six failed Embeddings construction attempts remain documented in the completed family report and are not assigned retrieval scores here. The separate native diagnostic threshold is 0.8. This report reaggregates existing native scores. It dispatches no new retrieval trial or benchmark model call and does not open private validation.

The eight-family search, joint replay/freeze, paired all-500 evaluation and private transfer gate remain incomplete. These development means do not establish an answer Overall score, public leaderboard position or a promoted skill bundle.

[Exact aggregates and source hashes](aggregate.json) · [Selection snapshot](../status-019/README.md) · [Embeddings attempts](../embeddings-complete-001/README.md) · [Campaign](../README.md)
