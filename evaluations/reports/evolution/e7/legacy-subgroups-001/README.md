# E7 Legacy: paired category and application evidence

The completed Legacy selection improved 46 eligible development questions, regressed on 9 and tied on 57. The category-weighted overall nDCG@10 increased from 61.11% to 72.38%. The eight questions without reference documents have no retrieval score.

These tables average existing native case scores for the unchanged baseline and candidate-009. They do not rerun retrieval or change selection. Each native aggregate was reproduced from the frozen 120-question selection before grouping; metadata and source evidence are hash-bound.

## Question categories

| Group | Eligible questions | Baseline nDCG@10 | Retained nDCG@10 | Delta pp | Improved | Regressed | Tied |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| basic | 24 | 73.02 | 84.80 | +11.77 | 7 | 0 | 17 |
| completeness | 12 | 20.63 | 55.71 | +35.08 | 11 | 1 | 0 |
| conflicting_info | 4 | 90.71 | 100.00 | +9.29 | 3 | 0 | 1 |
| constrained | 8 | 86.38 | 87.84 | +1.47 | 1 | 2 | 5 |
| high_level | 0 | N/A | N/A | N/A | 0 | 0 | 0 |
| info_not_found | 0 | N/A | N/A | N/A | 0 | 0 | 0 |
| intra_document_reasoning | 12 | 93.85 | 100.00 | +6.15 | 2 | 0 | 10 |
| miscellaneous | 8 | 92.34 | 92.88 | +0.55 | 1 | 0 | 7 |
| project_related | 12 | 51.58 | 63.62 | +12.04 | 10 | 2 | 0 |
| semantic | 32 | 27.67 | 40.20 | +12.54 | 11 | 4 | 17 |

## Application groups

| Group | Eligible questions | Baseline nDCG@10 | Retained nDCG@10 | Delta pp | Improved | Regressed | Tied |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| confluence | 39 | 64.40 | 69.99 | +5.59 | 20 | 6 | 13 |
| fireflies | 9 | 77.90 | 77.65 | -0.24 | 2 | 2 | 5 |
| github | 12 | 42.86 | 64.76 | +21.90 | 10 | 0 | 2 |
| gmail | 10 | 48.54 | 72.19 | +23.65 | 8 | 0 | 2 |
| google_drive | 14 | 63.44 | 76.29 | +12.85 | 8 | 0 | 6 |
| hubspot | 9 | 52.22 | 74.14 | +21.91 | 4 | 0 | 5 |
| jira | 26 | 68.35 | 79.77 | +11.42 | 14 | 1 | 11 |
| linear | 15 | 67.58 | 83.06 | +15.48 | 8 | 0 | 7 |
| slack | 24 | 46.74 | 56.20 | +9.46 | 12 | 3 | 9 |

## What the observed gains support

- Completeness had the largest category gain (+35.08 points, 12 questions), although one case regressed.
- Semantic questions gained 12.54 points across 32 questions. Four cases regressed; the retained 40.20% category score leaves substantial headroom.
- Project-related questions gained 12.04 points across 12 questions, with two regressions.
- Gmail had the largest observed application gain (+23.65 points, 10 questions). Fireflies declined slightly (-0.24 points, 9 questions). An overall improvement does not imply every source application or question improves.

## Interpretation and boundaries

The metric is retrieval nDCG@10, not answer correctness or completeness. A category name such as completeness describes the question type, not a separate answer score. A 100% subgroup score on a small sample is not evidence that all domain questions are solved.

Category weights are the frozen population-to-sample weights. Within each application, normalize those original weights over its sampled eligible questions; the resulting weighted mean is descriptive. Application groups overlap, their sample sizes are small, and their case counts must not be summed. Counts of improved, regressed and tied questions are unweighted, using a 1e-12 score tolerance.

All observations come from development on 6,000 reference-enriched documents and one exposed Enterprise source group. They do not establish independent generalization or public leaderboard placement. No private validation was read, no all-500 result is implied and no profile was promoted.

[Exact aggregate and native hashes](aggregate.json) · [Completed Legacy search](../legacy-complete-001/README.md) · [Campaign](../README.md)
