# Five measured EnterpriseRAG families: retained development profiles

This checkpoint adds Classical continuation-002 to the preceding five-family comparison. It transcribes exact published native aggregates; no case is rescored and no candidate is selected by this report.

| Family / retained candidate | nDCG@10 | Recall@10 | MRR@10 | Full qrel coverage@10 |
| --- | ---: | ---: | ---: | ---: |
| adaptive / candidate-014 | 66.21 | 74.02 | 67.37 | 69.27 |
| classical / continuation-002 | 62.10 | 64.17 | 66.38 | 57.82 |
| embeddings / baseline | 63.51 | 80.82 | 61.59 | 75.61 |
| legacy / candidate-009 | 72.38 | 81.99 | 71.51 | 76.43 |
| turso / continuation-001 | 72.08 | 82.51 | 71.61 | 77.26 |

Values are percentages. All five share 120 exposed stratified development questions, 112 eligible questions, category weights totaling 470 and 6,000 reference-enriched complete documents. The exact selection digest and every subgroup denominator/weight match. These are retrieval measurements; the paired all-500 comparison is pending.

Classical improves by 0.21 percentage points over its preceding incumbent after disabling association/topic expansion: one eligible question improves, none regress and 111 tie. Recall rises from 63.93% to 64.17%; MRR and full-qrel coverage are unchanged. This small exposed-subset gain does not establish generalization or statistical significance.

Legacy still has the highest observed aggregate nDCG@10 among the measured families. Turso leads recall, MRR and full-qrel coverage. Their search and acceptance status remain distinct from these descriptive maxima.

## Question categories

| Group | Eligible | adaptive | classical | embeddings | legacy | turso | Highest among these five |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| basic | 24 | 84.72 | 79.17 | 71.54 | 84.80 | 84.44 | legacy |
| completeness | 12 | 62.90 | 31.00 | 52.20 | 55.71 | 55.53 | adaptive |
| conflicting_info | 4 | 96.26 | 90.33 | 78.30 | 100.00 | 97.99 | legacy |
| constrained | 8 | 80.70 | 71.46 | 86.92 | 87.84 | 88.05 | turso |
| high_level | 0 | N/A | N/A | N/A | N/A | N/A | N/A |
| info_not_found | 0 | N/A | N/A | N/A | N/A | N/A | N/A |
| intra_document_reasoning | 12 | 100.00 | 100.00 | 82.89 | 100.00 | 100.00 | adaptive, classical, legacy, turso |
| miscellaneous | 8 | 87.50 | 87.50 | 90.77 | 92.88 | 92.88 | legacy, turso |
| project_related | 12 | 60.27 | 54.96 | 71.66 | 63.62 | 60.68 | embeddings |
| semantic | 32 | 20.22 | 22.53 | 32.90 | 40.20 | 40.83 | turso |

## Application groups

| Group | Eligible | adaptive | classical | embeddings | legacy | turso | Highest among these five |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| confluence | 39 | 68.09 | 60.05 | 70.99 | 69.99 | 69.70 | embeddings |
| fireflies | 9 | 69.60 | 78.91 | 56.10 | 77.65 | 78.19 | classical |
| github | 12 | 62.71 | 57.63 | 67.29 | 64.76 | 62.58 | embeddings |
| gmail | 10 | 71.15 | 50.07 | 49.64 | 72.19 | 72.52 | turso |
| google_drive | 14 | 68.73 | 62.33 | 66.33 | 76.29 | 73.08 | legacy |
| hubspot | 9 | 59.97 | 56.90 | 63.68 | 74.14 | 75.27 | turso |
| jira | 26 | 69.16 | 65.61 | 65.37 | 79.77 | 77.80 | legacy |
| linear | 15 | 81.33 | 83.23 | 69.72 | 83.06 | 82.16 | classical |
| slack | 24 | 50.16 | 46.68 | 62.80 | 56.20 | 56.36 | embeddings |

Application groups overlap; do not sum their counts or scores. Scores retain the frozen category weights. Maximum labels use unrounded values with 1e-12 ties. Unreferenced question categories remain unscored.

Legacy and Embeddings have terminal searches. Classical continues; Adaptive and Turso have incomplete searches after pre-dispatch refusals. Entity Graph and Ensemble have no native baseline, and Graphify has a construction timeout without retrieval fitness. Those three missing families are not zero-score competitors.

All-eight joint replay, one frozen bundle, paired all-500 recalculation and the whole-bundle private gate remain pending. No application router, installed skill improvement, answer Overall or public leaderboard rank is inferred.

[Previous matrix](../retained-cross-family-001/README.md) · [New Classical comparison](../classical-progress-002/README.md) · [Classical CTA](../classical-progress-002/cta.md) · [Turso comparison](../turso-progress-001/README.md) · [Source aggregates and commitments](aggregate.json) · [Campaign](../README.md)
