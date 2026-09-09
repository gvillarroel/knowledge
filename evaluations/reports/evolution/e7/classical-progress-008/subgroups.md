# Classical candidate-022 by category and application

All means use the frozen category weights on the same eligible questions in each arm. Delta columns are percentage points. Application groups may overlap and are descriptive; their gains must not be added. A group without reference documents has no quality score.

## Category

| Group | Questions / eligible | Baseline nDCG@10 | Candidate-020 nDCG@10 | Candidate-022 nDCG@10 | Delta vs baseline | Delta vs candidate-020 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| basic | 24 / 24 | 70.83 | 79.17 | 79.17 | +8.33 | +0.00 |
| completeness | 12 / 12 | 32.01 | 31.08 | 31.00 | -1.01 | -0.08 |
| conflicting_info | 4 / 4 | 90.33 | 90.33 | 90.33 | +0.00 | +0.00 |
| constrained | 8 / 8 | 68.16 | 68.63 | 71.46 | +3.30 | +2.83 |
| high_level | 4 / 0 | N/A | N/A | N/A | N/A | N/A |
| info_not_found | 4 / 0 | N/A | N/A | N/A | N/A | N/A |
| intra_document_reasoning | 12 / 12 | 100.00 | 100.00 | 100.00 | +0.00 | +0.00 |
| miscellaneous | 8 / 8 | 68.75 | 87.50 | 87.50 | +18.75 | +0.00 |
| project_related | 12 / 12 | 52.91 | 53.79 | 52.49 | -0.42 | -1.30 |
| semantic | 32 / 32 | 11.93 | 19.00 | 22.53 | +10.60 | +3.53 |

## Application

| Group | Questions / eligible | Baseline nDCG@10 | Candidate-020 nDCG@10 | Candidate-022 nDCG@10 | Delta vs baseline | Delta vs candidate-020 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| confluence | 39 / 39 | 58.37 | 59.10 | 59.34 | +0.97 | +0.24 |
| fireflies | 9 / 9 | 78.69 | 78.91 | 78.91 | +0.22 | +0.00 |
| github | 12 / 12 | 48.20 | 56.57 | 57.63 | +9.43 | +1.06 |
| gmail | 10 / 10 | 50.02 | 50.11 | 50.07 | +0.05 | -0.04 |
| google_drive | 14 / 14 | 55.27 | 61.45 | 62.33 | +7.06 | +0.88 |
| hubspot | 9 / 9 | 56.90 | 56.90 | 56.90 | +0.00 | +0.00 |
| jira | 26 / 26 | 62.65 | 65.14 | 65.61 | +2.97 | +0.47 |
| linear | 15 / 15 | 65.90 | 76.87 | 81.81 | +15.91 | +4.93 |
| slack | 24 / 24 | 34.71 | 46.16 | 46.68 | +11.97 | +0.52 |

The category contributions reconstruct the overall baseline gain without adding overlapping application groups. These are development observations from an unfinished search, with no private validation or promotion claim.

[All metrics, paired counts and category contributions](subgroups.json) · [Native gain report](README.md)
