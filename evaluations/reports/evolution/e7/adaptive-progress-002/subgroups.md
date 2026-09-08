# Adaptive candidate-006: paired development breakdown

The provisionally retained `bm25.k1=3.0` profile raises weighted adaptive nDCG@10 from 60.04% to 61.49%. Among 112 eligible questions, 24 improve, 6 regress and 82 tie. Eight questions without references have no retrieval score. This describes candidate-006; the family search and final selection remain incomplete.

All groups below use the original native case scores verified by the [second Adaptive gain report](README.md). No retrieval was rerun and no profile was selected from these subgroup results. Scores are percentages and deltas are percentage points.

## Question categories

| Group | Eligible questions | Baseline nDCG@10 | Candidate-006 nDCG@10 | Delta pp | Improved | Regressed | Tied |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| basic | 24 | 75.92 | 76.48 | +0.57 | 2 | 0 | 22 |
| completeness | 12 | 51.32 | 52.85 | +1.53 | 9 | 1 | 2 |
| conflicting_info | 4 | 90.33 | 94.76 | +4.43 | 1 | 0 | 3 |
| constrained | 8 | 78.62 | 78.83 | +0.20 | 1 | 0 | 7 |
| high_level | 0 | N/A | N/A | N/A | 0 | 0 | 0 |
| info_not_found | 0 | N/A | N/A | N/A | 0 | 0 | 0 |
| intra_document_reasoning | 12 | 100.00 | 100.00 | +0.00 | 0 | 0 | 12 |
| miscellaneous | 8 | 73.20 | 74.84 | +1.64 | 1 | 0 | 7 |
| project_related | 12 | 57.28 | 58.80 | +1.52 | 6 | 3 | 3 |
| semantic | 32 | 15.87 | 18.81 | +2.94 | 4 | 2 | 26 |

## Application groups

| Group | Eligible questions | Baseline nDCG@10 | Candidate-006 nDCG@10 | Delta pp | Improved | Regressed | Tied |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| confluence | 39 | 63.89 | 65.17 | +1.28 | 14 | 3 | 22 |
| fireflies | 9 | 79.20 | 79.06 | -0.14 | 2 | 1 | 6 |
| github | 12 | 54.21 | 60.70 | +6.50 | 6 | 1 | 5 |
| gmail | 10 | 58.46 | 58.97 | +0.51 | 3 | 1 | 6 |
| google_drive | 14 | 59.30 | 61.68 | +2.38 | 5 | 1 | 8 |
| hubspot | 9 | 59.62 | 59.49 | -0.12 | 0 | 1 | 8 |
| jira | 26 | 65.44 | 66.40 | +0.95 | 7 | 4 | 15 |
| linear | 15 | 73.71 | 74.65 | +0.94 | 3 | 0 | 12 |
| slack | 24 | 41.43 | 42.43 | +1.01 | 8 | 2 | 14 |

## Contributions to the overall change

| Question category | Eligible population weight | Contribution to overall delta pp |
| --- | ---: | ---: |
| basic | 175 | +0.2110 |
| completeness | 20 | +0.0652 |
| conflicting_info | 20 | +0.1886 |
| constrained | 30 | +0.0129 |
| high_level | 0 | +0.0000 |
| info_not_found | 0 | +0.0000 |
| intra_document_reasoning | 40 | +0.0000 |
| miscellaneous | 20 | +0.0696 |
| project_related | 40 | +0.1298 |
| semantic | 125 | +0.7817 |

Each category contribution is its weighted score delta times its share of eligible population weight, 470. The unrounded contributions reproduce the overall +1.4588066167-point gain. Application groups overlap, so their counts and deltas must not be summed. Application means renormalize the same category weights within the group. Improved, regressed and tied counts are unweighted and use a 1e-12 tolerance.

These are retrieval results for 120 stratified development questions and 6,000 reference-enriched full-text documents. Category names describe the questions; they are not generated-answer quality metrics. The remaining public questions, private transfer gate and whole-bundle promotion have not been evaluated by this analysis.

[Exact subgroup aggregates and native hashes](subgroups.json) · [Paired native comparison](README.md)
