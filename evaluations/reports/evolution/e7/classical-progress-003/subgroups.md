# Classical candidate-006: paired development breakdown

The provisionally retained `bm25.b=1.0, bm25.k1=2.0` profile raises weighted fusion nDCG@10 from 55.04% to 58.24%. Among 112 eligible questions, 13 improve, 4 regress and 95 tie. Eight questions without references have no retrieval score. This describes candidate-006; the family search and final selection remain incomplete.

All groups below use the original native case scores verified by the [third Classical gain report](README.md). No retrieval was rerun and no profile was selected from these subgroup results. Scores are percentages and deltas are percentage points.

## Question categories

| Group | Eligible questions | Baseline nDCG@10 | Candidate-006 nDCG@10 | Delta pp | Improved | Regressed | Tied |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| basic | 24 | 70.83 | 77.08 | +6.25 | 2 | 0 | 22 |
| completeness | 12 | 32.01 | 34.93 | +2.92 | 6 | 0 | 6 |
| conflicting_info | 4 | 90.33 | 90.33 | +0.00 | 0 | 0 | 4 |
| constrained | 8 | 68.16 | 68.16 | +0.00 | 0 | 0 | 8 |
| high_level | 0 | N/A | N/A | N/A | 0 | 0 | 0 |
| info_not_found | 0 | N/A | N/A | N/A | 0 | 0 | 0 |
| intra_document_reasoning | 12 | 100.00 | 100.00 | +0.00 | 0 | 0 | 12 |
| miscellaneous | 8 | 68.75 | 70.39 | +1.64 | 1 | 0 | 7 |
| project_related | 12 | 52.91 | 51.75 | -1.16 | 3 | 3 | 6 |
| semantic | 32 | 11.93 | 14.84 | +2.91 | 1 | 1 | 30 |

## Application groups

| Group | Eligible questions | Baseline nDCG@10 | Candidate-006 nDCG@10 | Delta pp | Improved | Regressed | Tied |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| confluence | 39 | 58.37 | 58.03 | -0.34 | 5 | 3 | 31 |
| fireflies | 9 | 78.69 | 78.68 | -0.01 | 3 | 1 | 5 |
| github | 12 | 48.20 | 58.15 | +9.95 | 4 | 1 | 7 |
| gmail | 10 | 50.02 | 50.06 | +0.04 | 3 | 1 | 6 |
| google_drive | 14 | 55.27 | 56.14 | +0.87 | 3 | 1 | 10 |
| hubspot | 9 | 56.90 | 56.90 | +0.00 | 0 | 0 | 9 |
| jira | 26 | 62.65 | 62.41 | -0.24 | 5 | 3 | 18 |
| linear | 15 | 65.90 | 76.43 | +10.53 | 1 | 0 | 14 |
| slack | 24 | 34.71 | 38.46 | +3.75 | 6 | 2 | 16 |

## Contributions to the overall change

| Question category | Eligible population weight | Contribution to overall delta pp |
| --- | ---: | ---: |
| basic | 175 | +2.3271 |
| completeness | 20 | +0.1241 |
| conflicting_info | 20 | +0.0000 |
| constrained | 30 | +0.0000 |
| high_level | 0 | +0.0000 |
| info_not_found | 0 | +0.0000 |
| intra_document_reasoning | 40 | +0.0000 |
| miscellaneous | 20 | +0.0696 |
| project_related | 40 | -0.0986 |
| semantic | 125 | +0.7735 |

Each category contribution is its weighted score delta times its share of eligible population weight, 470. The unrounded contributions reproduce the overall +3.1957879170-point gain. Application groups overlap, so their counts and deltas must not be summed. Application means renormalize the same category weights within the group. Improved, regressed and tied counts are unweighted and use a 1e-12 tolerance.

These are retrieval results for 120 stratified development questions and 6,000 reference-enriched full-text documents. Category names describe the questions; they are not generated-answer quality metrics. The remaining public questions, private transfer gate and whole-bundle promotion have not been evaluated by this analysis.

[Exact subgroup aggregates and native hashes](subgroups.json) · [Paired native comparison](README.md)
