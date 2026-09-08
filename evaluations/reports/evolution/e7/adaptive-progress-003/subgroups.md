# Adaptive candidate-009 by category and application

All means use the frozen category weights on the same eligible questions in each arm. Delta columns are percentage points. Application groups may overlap and are descriptive; their gains must not be added. A group without reference documents has no quality score.

## Category

| Group | Questions / eligible | Baseline nDCG@10 | Candidate-006 nDCG@10 | Candidate-009 nDCG@10 | Delta vs baseline | Delta vs candidate-006 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| basic | 24 / 24 | 75.92 | 76.48 | 83.33 | +7.42 | +6.85 |
| completeness | 12 / 12 | 51.32 | 52.85 | 53.50 | +2.18 | +0.65 |
| conflicting_info | 4 / 4 | 90.33 | 94.76 | 95.16 | +4.84 | +0.40 |
| constrained | 8 / 8 | 78.62 | 78.83 | 76.20 | -2.43 | -2.63 |
| high_level | 4 / 0 | N/A | N/A | N/A | N/A | N/A |
| info_not_found | 4 / 0 | N/A | N/A | N/A | N/A | N/A |
| intra_document_reasoning | 12 / 12 | 100.00 | 100.00 | 100.00 | +0.00 | +0.00 |
| miscellaneous | 8 / 8 | 73.20 | 74.84 | 87.50 | +14.30 | +12.66 |
| project_related | 12 / 12 | 57.28 | 58.80 | 60.56 | +3.28 | +1.75 |
| semantic | 32 / 32 | 15.87 | 18.81 | 21.15 | +5.28 | +2.34 |

## Application

| Group | Questions / eligible | Baseline nDCG@10 | Candidate-006 nDCG@10 | Candidate-009 nDCG@10 | Delta vs baseline | Delta vs candidate-006 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| confluence | 39 / 39 | 63.89 | 65.17 | 65.07 | +1.18 | -0.10 |
| fireflies | 9 / 9 | 79.20 | 79.06 | 79.64 | +0.44 | +0.58 |
| github | 12 / 12 | 54.21 | 60.70 | 61.34 | +7.13 | +0.64 |
| gmail | 10 / 10 | 58.46 | 58.97 | 71.10 | +12.64 | +12.13 |
| google_drive | 14 / 14 | 59.30 | 61.68 | 67.21 | +7.91 | +5.53 |
| hubspot | 9 / 9 | 59.62 | 59.49 | 59.62 | +0.00 | +0.12 |
| jira | 26 / 26 | 65.44 | 66.40 | 69.69 | +4.25 | +3.30 |
| linear | 15 / 15 | 73.71 | 74.65 | 79.91 | +6.21 | +5.27 |
| slack | 24 / 24 | 41.43 | 42.43 | 48.06 | +6.64 | +5.63 |

The category contributions reconstruct the overall baseline gain without adding overlapping application groups. These are development observations from an unfinished search, with no private validation or promotion claim.

[All metrics, paired counts and category contributions](subgroups.json) · [Native gain report](README.md)
