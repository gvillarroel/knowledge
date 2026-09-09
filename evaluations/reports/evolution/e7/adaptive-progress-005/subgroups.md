# Adaptive candidate-014 by category and application

All means use the frozen category weights on the same eligible questions in each arm. Delta columns are percentage points. Application groups may overlap and are descriptive; their gains must not be added. A group without reference documents has no quality score.

## Category

| Group | Questions / eligible | Baseline nDCG@10 | Candidate-012 nDCG@10 | Candidate-014 nDCG@10 | Delta vs baseline | Delta vs candidate-012 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| basic | 24 / 24 | 75.92 | 83.33 | 84.72 | +8.80 | +1.39 |
| completeness | 12 / 12 | 51.32 | 53.81 | 62.90 | +11.58 | +9.10 |
| conflicting_info | 4 / 4 | 90.33 | 95.16 | 96.26 | +5.93 | +1.09 |
| constrained | 8 / 8 | 78.62 | 76.33 | 80.70 | +2.07 | +4.36 |
| high_level | 4 / 0 | N/A | N/A | N/A | N/A | N/A |
| info_not_found | 4 / 0 | N/A | N/A | N/A | N/A | N/A |
| intra_document_reasoning | 12 / 12 | 100.00 | 100.00 | 100.00 | +0.00 | +0.00 |
| miscellaneous | 8 / 8 | 73.20 | 87.50 | 87.50 | +14.30 | +0.00 |
| project_related | 12 / 12 | 57.28 | 61.12 | 60.27 | +2.99 | -0.86 |
| semantic | 32 / 32 | 15.87 | 21.38 | 20.22 | +4.34 | -1.17 |

## Application

| Group | Questions / eligible | Baseline nDCG@10 | Candidate-012 nDCG@10 | Candidate-014 nDCG@10 | Delta vs baseline | Delta vs candidate-012 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| confluence | 39 / 39 | 63.89 | 65.30 | 68.09 | +4.20 | +2.78 |
| fireflies | 9 / 9 | 79.20 | 80.52 | 69.60 | -9.60 | -10.92 |
| github | 12 / 12 | 54.21 | 61.36 | 62.71 | +8.51 | +1.35 |
| gmail | 10 / 10 | 58.46 | 71.70 | 71.15 | +12.69 | -0.55 |
| google_drive | 14 / 14 | 59.30 | 67.31 | 68.73 | +9.43 | +1.42 |
| hubspot | 9 / 9 | 59.62 | 59.62 | 59.97 | +0.35 | +0.35 |
| jira | 26 / 26 | 65.44 | 69.93 | 69.16 | +3.72 | -0.77 |
| linear | 15 / 15 | 73.71 | 79.91 | 81.33 | +7.62 | +1.41 |
| slack | 24 / 24 | 41.43 | 48.33 | 50.16 | +8.73 | +1.82 |

The category contributions reconstruct the overall baseline gain without adding overlapping application groups. These are development observations from an unfinished search, with no private validation or promotion claim.

[All metrics, paired counts and category contributions](subgroups.json) · [Native gain report](README.md)
