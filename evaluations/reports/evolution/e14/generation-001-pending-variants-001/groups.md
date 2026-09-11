# EnterpriseRAG E14: two pending variants by application and category

These are paired descriptive results on the same stratified development questions. Applications can overlap; categories and applications must not be summed together. Rows without retrieval references have unavailable quality. No subgroup selects a router or changes the retained candidate.

## Turso

The tested candidate is `versioned-000-pending-continuation-002`. Its prior incumbent remains `retained-start`.

### Application

| Group | Eligible | Incumbent nDCG x100 | Candidate nDCG x100 | Delta points | Candidate recall x100 | Candidate MRR x100 | Improved / regressed / tied |
| --- | --- | --- | --- | --- | --- | --- | --- |
| confluence | 39 | 69.70 | 63.59 | -6.10 | 73.95 | 68.60 | 3 / 19 / 17 |
| fireflies | 9 | 78.19 | 78.52 | +0.33 | 84.48 | 78.61 | 1 / 1 / 7 |
| github | 12 | 62.58 | 56.07 | -6.51 | 68.36 | 61.42 | 1 / 6 / 5 |
| gmail | 10 | 72.52 | 71.29 | -1.23 | 94.55 | 68.80 | 1 / 4 / 5 |
| google_drive | 14 | 73.08 | 65.78 | -7.29 | 69.25 | 70.57 | 0 / 6 / 8 |
| hubspot | 9 | 75.27 | 76.40 | +1.13 | 82.76 | 74.14 | 1 / 0 / 8 |
| jira | 26 | 77.80 | 75.35 | -2.46 | 83.02 | 81.91 | 3 / 9 / 14 |
| linear | 15 | 82.16 | 81.08 | -1.09 | 83.63 | 82.68 | 0 / 2 / 13 |
| slack | 24 | 56.36 | 54.67 | -1.69 | 67.16 | 57.55 | 1 / 7 / 16 |

### Category

| Group | Eligible | Incumbent nDCG x100 | Candidate nDCG x100 | Delta points | Candidate recall x100 | Candidate MRR x100 | Improved / regressed / tied |
| --- | --- | --- | --- | --- | --- | --- | --- |
| basic | 24 | 84.44 | 81.46 | -2.98 | 87.50 | 79.58 | 0 / 3 / 21 |
| completeness | 12 | 55.53 | 46.56 | -8.97 | 50.00 | 67.86 | 1 / 9 / 2 |
| conflicting_info | 4 | 97.99 | 95.99 | -2.01 | 100.00 | 100.00 | 0 / 1 / 3 |
| constrained | 8 | 88.05 | 85.77 | -2.28 | 93.75 | 87.50 | 1 / 1 / 6 |
| high_level | 0 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | 0 / 0 / 0 |
| info_not_found | 0 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | 0 / 0 / 0 |
| intra_document_reasoning | 12 | 100.00 | 100.00 | +0.00 | 100.00 | 100.00 | 0 / 0 / 12 |
| miscellaneous | 8 | 92.88 | 92.88 | +0.00 | 100.00 | 90.62 | 0 / 0 / 8 |
| project_related | 12 | 60.68 | 55.30 | -5.38 | 64.72 | 72.92 | 2 / 8 / 2 |
| semantic | 32 | 40.83 | 38.60 | -2.22 | 59.38 | 31.87 | 3 / 4 / 25 |

## Adaptive

The tested candidate is `versioned-000-pending-continuation-001`. Its prior incumbent remains `retained-start`.

### Application

| Group | Eligible | Incumbent nDCG x100 | Candidate nDCG x100 | Delta points | Candidate recall x100 | Candidate MRR x100 | Improved / regressed / tied |
| --- | --- | --- | --- | --- | --- | --- | --- |
| confluence | 39 | 68.09 | 68.92 | +0.83 | 77.63 | 73.49 | 11 / 12 / 16 |
| fireflies | 9 | 69.60 | 67.42 | -2.18 | 68.09 | 68.55 | 0 / 3 / 6 |
| github | 12 | 62.71 | 60.91 | -1.80 | 73.03 | 64.20 | 2 / 6 / 4 |
| gmail | 10 | 71.15 | 58.31 | -12.84 | 68.86 | 61.14 | 0 / 5 / 5 |
| google_drive | 14 | 68.73 | 66.53 | -2.20 | 73.22 | 66.46 | 2 / 4 / 8 |
| hubspot | 9 | 59.97 | 56.90 | -3.07 | 56.90 | 56.90 | 0 / 1 / 8 |
| jira | 26 | 69.16 | 67.67 | -1.49 | 75.23 | 73.66 | 5 / 10 / 11 |
| linear | 15 | 81.33 | 84.54 | +3.22 | 91.68 | 84.05 | 4 / 1 / 10 |
| slack | 24 | 50.16 | 47.56 | -2.60 | 58.16 | 51.73 | 4 / 9 / 11 |

### Category

| Group | Eligible | Incumbent nDCG x100 | Candidate nDCG x100 | Delta points | Candidate recall x100 | Candidate MRR x100 | Improved / regressed / tied |
| --- | --- | --- | --- | --- | --- | --- | --- |
| basic | 24 | 84.72 | 82.17 | -2.56 | 87.50 | 80.62 | 0 / 2 / 22 |
| completeness | 12 | 62.90 | 48.79 | -14.11 | 53.33 | 54.94 | 0 / 12 / 0 |
| conflicting_info | 4 | 96.26 | 96.26 | +0.00 | 100.00 | 100.00 | 0 / 0 / 4 |
| constrained | 8 | 80.70 | 84.35 | +3.65 | 93.75 | 87.50 | 3 / 0 / 5 |
| high_level | 0 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | 0 / 0 / 0 |
| info_not_found | 0 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | 0 / 0 / 0 |
| intra_document_reasoning | 12 | 100.00 | 100.00 | +0.00 | 100.00 | 100.00 | 0 / 0 / 12 |
| miscellaneous | 8 | 87.50 | 82.89 | -4.61 | 87.50 | 81.25 | 0 / 1 / 7 |
| project_related | 12 | 60.27 | 61.48 | +1.21 | 72.59 | 77.78 | 6 / 5 / 1 |
| semantic | 32 | 20.22 | 19.20 | -1.01 | 34.38 | 14.84 | 5 / 6 / 21 |

[Results and search accounting](README.md) · [Cost, time and quality](cta.md) · [Full route and subgroup metrics](aggregate.json)
