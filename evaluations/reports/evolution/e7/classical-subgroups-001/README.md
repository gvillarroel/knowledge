# E7 Classical: paired category and application evidence

Snapshot: the provisionally retained candidate-004 (`bm25.b=1.0`) improves 11 eligible development questions, regresses on 2 and ties on 99 against the initial configuration. The category-weighted overall nDCG@10 rises from 55.04% to 57.10%. Eight questions without reference documents have no retrieval score. Classical is still evolving; this is not its final selection.

These tables average the original native fusion case scores already bound by the [second Classical gain report](../classical-progress-002/README.md). Every source digest and aggregate was verified against the fixed 120-question selection before grouping. No retrieval was rerun and no candidate was selected by this analysis.

## Question categories

| Group | Eligible questions | Baseline nDCG@10 | Candidate-004 nDCG@10 | Delta pp | Improved | Regressed | Tied |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| basic | 24 | 70.83 | 75.00 | +4.17 | 1 | 0 | 23 |
| completeness | 12 | 32.01 | 34.61 | +2.60 | 4 | 0 | 8 |
| conflicting_info | 4 | 90.33 | 90.33 | +0.00 | 0 | 0 | 4 |
| constrained | 8 | 68.16 | 68.16 | +0.00 | 0 | 0 | 8 |
| high_level | 0 | N/A | N/A | N/A | 0 | 0 | 0 |
| info_not_found | 0 | N/A | N/A | N/A | 0 | 0 | 0 |
| intra_document_reasoning | 12 | 100.00 | 100.00 | +0.00 | 0 | 0 | 12 |
| miscellaneous | 8 | 68.75 | 57.89 | -10.86 | 1 | 1 | 6 |
| project_related | 12 | 52.91 | 52.81 | -0.09 | 3 | 1 | 8 |
| semantic | 32 | 11.93 | 15.19 | +3.26 | 2 | 0 | 30 |

## Application groups

| Group | Eligible questions | Baseline nDCG@10 | Candidate-004 nDCG@10 | Delta pp | Improved | Regressed | Tied |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| confluence | 39 | 58.37 | 56.51 | -1.86 | 4 | 2 | 33 |
| fireflies | 9 | 78.69 | 79.89 | +1.20 | 3 | 0 | 6 |
| github | 12 | 48.20 | 59.12 | +10.92 | 5 | 0 | 7 |
| gmail | 10 | 50.02 | 50.07 | +0.05 | 1 | 0 | 9 |
| google_drive | 14 | 55.27 | 56.93 | +1.66 | 4 | 0 | 10 |
| hubspot | 9 | 56.90 | 56.90 | +0.00 | 0 | 0 | 9 |
| jira | 26 | 62.65 | 62.85 | +0.21 | 5 | 1 | 20 |
| linear | 15 | 65.90 | 76.43 | +10.53 | 1 | 0 | 14 |
| slack | 24 | 34.71 | 34.17 | -0.54 | 2 | 1 | 21 |

## Where the overall gain comes from

The one improved basic question contributes 1.55 percentage points to the net 2.06-point overall gain. The basic category contains 24 eligible sampled questions with total population weight 175, so that single case has a large effect on the weighted development result. This concentration is visible in the case counts; the overall improvement is not evenly distributed.

The semantic category adds 0.87 points to the overall mean. Its own nDCG@10 rises by 3.26 points to 15.19%, with two improved questions and no regressions. Miscellaneous questions subtract 0.46 points from the overall mean: their category score falls by 10.86 points across eight questions, with one improvement and one regression.

GitHub has the largest observed application gain, +10.92 points across 12 questions, with five improvements and no regressions. Confluence falls by 1.86 points across 39 questions, despite four improvements, because two regressions outweigh them under the original sampling weights.

## Interpretation and boundaries

The metric is retrieval nDCG@10. Category names such as completeness describe the question type; they do not measure generated-answer completeness. Zero-reference groups have unavailable scores, and a perfect small-group score does not establish general domain coverage.

Category means use the frozen population-to-sample weights. A category contribution to the overall gain is its score delta multiplied by its share of the total eligible weight, 470; those contributions sum to the reported overall delta. Within each application, normalize the same original weights over its sampled eligible questions. Application groups overlap, so their counts and deltas must not be summed. Improved, regressed and tied counts are unweighted with a 1e-12 tolerance.

The observations describe development on 6,000 reference-enriched complete documents and one exposed Enterprise source group. They do not establish performance on all 500 public questions, independent generalization or a public leaderboard position. The family search and joint selection remain incomplete. No private validation was read and no profile was promoted.

[Exact aggregate and native hashes](aggregate.json) · [Second Classical gain](../classical-progress-002/README.md) · [Campaign](../README.md)
