# Classical candidate-010: paired development breakdown

The provisionally retained `bm25.b=1.0, bm25.k1=3.0, bm25.title_weight=1.0` profile raises weighted fusion nDCG@10 from 55.04% to 60.01%. Among 112 eligible questions, 19 improve, 10 regress and 83 tie. Eight questions without references have no retrieval score. This describes candidate-010; the family search and final selection remain incomplete.

All groups below use the original native case scores verified by the [fifth Classical gain report](README.md). No retrieval was rerun and no profile was selected from these subgroup results. Scores are percentages and deltas are percentage points.

## Question categories

| Group | Eligible questions | Baseline nDCG@10 | Candidate-010 nDCG@10 | Delta pp | Improved | Regressed | Tied |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| basic | 24 | 70.83 | 79.71 | +8.88 | 3 | 1 | 20 |
| completeness | 12 | 32.01 | 31.80 | -0.22 | 6 | 2 | 4 |
| conflicting_info | 4 | 90.33 | 90.33 | +0.00 | 0 | 0 | 4 |
| constrained | 8 | 68.16 | 64.33 | -3.83 | 0 | 1 | 7 |
| high_level | 0 | N/A | N/A | N/A | 0 | 0 | 0 |
| info_not_found | 0 | N/A | N/A | N/A | 0 | 0 | 0 |
| intra_document_reasoning | 12 | 100.00 | 100.00 | +0.00 | 0 | 0 | 12 |
| miscellaneous | 8 | 68.75 | 87.50 | +18.75 | 2 | 0 | 6 |
| project_related | 12 | 52.91 | 53.02 | +0.11 | 5 | 3 | 4 |
| semantic | 32 | 11.93 | 16.11 | +4.19 | 3 | 3 | 26 |

## Application groups

| Group | Eligible questions | Baseline nDCG@10 | Candidate-010 nDCG@10 | Delta pp | Improved | Regressed | Tied |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| confluence | 39 | 58.37 | 56.19 | -2.18 | 7 | 6 | 26 |
| fireflies | 9 | 78.69 | 78.05 | -0.64 | 3 | 2 | 4 |
| github | 12 | 48.20 | 58.87 | +10.68 | 5 | 2 | 5 |
| gmail | 10 | 50.02 | 52.82 | +2.80 | 4 | 1 | 5 |
| google_drive | 14 | 55.27 | 62.95 | +7.68 | 5 | 1 | 8 |
| hubspot | 9 | 56.90 | 56.90 | +0.00 | 0 | 0 | 9 |
| jira | 26 | 62.65 | 64.77 | +2.12 | 7 | 3 | 16 |
| linear | 15 | 65.90 | 77.16 | +11.27 | 2 | 1 | 12 |
| slack | 24 | 34.71 | 43.15 | +8.44 | 7 | 2 | 15 |

## Contributions to the overall change

| Question category | Eligible population weight | Contribution to overall delta pp |
| --- | ---: | ---: |
| basic | 175 | +3.3060 |
| completeness | 20 | -0.0092 |
| conflicting_info | 20 | +0.0000 |
| constrained | 30 | -0.2446 |
| high_level | 0 | +0.0000 |
| info_not_found | 0 | +0.0000 |
| intra_document_reasoning | 40 | +0.0000 |
| miscellaneous | 20 | +0.7979 |
| project_related | 40 | +0.0095 |
| semantic | 125 | +1.1131 |

Each category contribution is its weighted score delta times its share of eligible population weight, 470. The unrounded contributions reproduce the overall +4.9726244203-point gain. Application groups overlap, so their counts and deltas must not be summed. Application means renormalize the same category weights within the group. Improved, regressed and tied counts are unweighted and use a 1e-12 tolerance.

These are retrieval results for 120 stratified development questions and 6,000 reference-enriched full-text documents. Category names describe the questions; they are not generated-answer quality metrics. The remaining public questions, private transfer gate and whole-bundle promotion have not been evaluated by this analysis.

[Exact subgroup aggregates and native hashes](subgroups.json) · [Paired native comparison](README.md)
