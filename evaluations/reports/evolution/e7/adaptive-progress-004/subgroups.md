# Adaptive candidate-012 by category and application

All means use the frozen category weights on the same eligible questions in each arm. Delta columns are percentage points. Application groups may overlap and are descriptive; their gains must not be added. A group without reference documents has no quality score.

## Category

| Group | Questions / eligible | Baseline nDCG@10 | Candidate-009 nDCG@10 | Candidate-012 nDCG@10 | Delta vs baseline | Delta vs candidate-009 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| basic | 24 / 24 | 75.92 | 83.33 | 83.33 | +7.42 | +0.00 |
| completeness | 12 / 12 | 51.32 | 53.50 | 53.81 | +2.49 | +0.31 |
| conflicting_info | 4 / 4 | 90.33 | 95.16 | 95.16 | +4.84 | +0.00 |
| constrained | 8 / 8 | 78.62 | 76.20 | 76.33 | -2.29 | +0.14 |
| high_level | 4 / 0 | N/A | N/A | N/A | N/A | N/A |
| info_not_found | 4 / 0 | N/A | N/A | N/A | N/A | N/A |
| intra_document_reasoning | 12 / 12 | 100.00 | 100.00 | 100.00 | +0.00 | +0.00 |
| miscellaneous | 8 / 8 | 73.20 | 87.50 | 87.50 | +14.30 | +0.00 |
| project_related | 12 / 12 | 57.28 | 60.56 | 61.12 | +3.84 | +0.57 |
| semantic | 32 / 32 | 15.87 | 21.15 | 21.38 | +5.51 | +0.23 |

## Application

| Group | Questions / eligible | Baseline nDCG@10 | Candidate-009 nDCG@10 | Candidate-012 nDCG@10 | Delta vs baseline | Delta vs candidate-009 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| confluence | 39 / 39 | 63.89 | 65.07 | 65.30 | +1.41 | +0.23 |
| fireflies | 9 / 9 | 79.20 | 79.64 | 80.52 | +1.32 | +0.88 |
| github | 12 / 12 | 54.21 | 61.34 | 61.36 | +7.15 | +0.02 |
| gmail | 10 / 10 | 58.46 | 71.10 | 71.70 | +13.24 | +0.61 |
| google_drive | 14 / 14 | 59.30 | 67.21 | 67.31 | +8.01 | +0.10 |
| hubspot | 9 / 9 | 59.62 | 59.62 | 59.62 | +0.00 | +0.00 |
| jira | 26 / 26 | 65.44 | 69.69 | 69.93 | +4.49 | +0.24 |
| linear | 15 / 15 | 73.71 | 79.91 | 79.91 | +6.21 | +0.00 |
| slack | 24 / 24 | 41.43 | 48.06 | 48.33 | +6.91 | +0.27 |

The category contributions reconstruct the overall baseline gain without adding overlapping application groups. These are development observations from an unfinished search, with no private validation or promotion claim.

[All metrics, paired counts and category contributions](subgroups.json) · [Native gain report](README.md)
