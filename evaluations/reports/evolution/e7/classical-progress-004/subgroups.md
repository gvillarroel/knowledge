# Classical candidate-007: paired development breakdown

The provisionally retained `bm25.b=1.0, bm25.k1=3.0` profile raises weighted fusion nDCG@10 from 55.04% to 58.67%. Among 112 eligible questions, 15 improve, 8 regress and 89 tie. Eight questions without references have no retrieval score. This describes candidate-007; the family search and final selection remain incomplete.

All groups below use the original native case scores verified by the [fourth Classical gain report](README.md). No retrieval was rerun and no profile was selected from these subgroup results. Scores are percentages and deltas are percentage points.

## Question categories

| Group | Eligible questions | Baseline nDCG@10 | Candidate-007 nDCG@10 | Delta pp | Improved | Regressed | Tied |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| basic | 24 | 70.83 | 78.72 | +7.89 | 3 | 1 | 20 |
| completeness | 12 | 32.01 | 35.25 | +3.24 | 6 | 0 | 6 |
| conflicting_info | 4 | 90.33 | 90.33 | +0.00 | 0 | 0 | 4 |
| constrained | 8 | 68.16 | 68.16 | +0.00 | 0 | 0 | 8 |
| high_level | 0 | N/A | N/A | N/A | 0 | 0 | 0 |
| info_not_found | 0 | N/A | N/A | N/A | 0 | 0 | 0 |
| intra_document_reasoning | 12 | 100.00 | 100.00 | +0.00 | 0 | 0 | 12 |
| miscellaneous | 8 | 68.75 | 70.39 | +1.64 | 1 | 0 | 7 |
| project_related | 12 | 52.91 | 50.56 | -2.34 | 4 | 5 | 3 |
| semantic | 32 | 11.93 | 14.51 | +2.58 | 1 | 2 | 29 |

## Application groups

| Group | Eligible questions | Baseline nDCG@10 | Candidate-007 nDCG@10 | Delta pp | Improved | Regressed | Tied |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| confluence | 39 | 58.37 | 58.12 | -0.25 | 6 | 4 | 29 |
| fireflies | 9 | 78.69 | 77.44 | -1.25 | 3 | 2 | 4 |
| github | 12 | 48.20 | 56.77 | +8.57 | 4 | 3 | 5 |
| gmail | 10 | 50.02 | 55.23 | +5.21 | 4 | 2 | 4 |
| google_drive | 14 | 55.27 | 56.01 | +0.74 | 3 | 2 | 9 |
| hubspot | 9 | 56.90 | 56.90 | +0.00 | 0 | 0 | 9 |
| jira | 26 | 62.65 | 61.48 | -1.17 | 5 | 4 | 17 |
| linear | 15 | 65.90 | 77.16 | +11.27 | 2 | 1 | 12 |
| slack | 24 | 34.71 | 38.42 | +3.71 | 6 | 4 | 14 |

## Contributions to the overall change

| Question category | Eligible population weight | Contribution to overall delta pp |
| --- | ---: | ---: |
| basic | 175 | +2.9365 |
| completeness | 20 | +0.1377 |
| conflicting_info | 20 | +0.0000 |
| constrained | 30 | +0.0000 |
| high_level | 0 | +0.0000 |
| info_not_found | 0 | +0.0000 |
| intra_document_reasoning | 40 | +0.0000 |
| miscellaneous | 20 | +0.0696 |
| project_related | 40 | -0.1994 |
| semantic | 125 | +0.6861 |

Each category contribution is its weighted score delta times its share of eligible population weight, 470. The unrounded contributions reproduce the overall +3.6306086245-point gain. Application groups overlap, so their counts and deltas must not be summed. Application means renormalize the same category weights within the group. Improved, regressed and tied counts are unweighted and use a 1e-12 tolerance.

These are retrieval results for 120 stratified development questions and 6,000 reference-enriched full-text documents. Category names describe the questions; they are not generated-answer quality metrics. The remaining public questions, private transfer gate and whole-bundle promotion have not been evaluated by this analysis.

[Exact subgroup aggregates and native hashes](subgroups.json) · [Paired native comparison](README.md)
