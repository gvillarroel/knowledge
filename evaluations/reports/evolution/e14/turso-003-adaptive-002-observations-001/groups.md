# EnterpriseRAG E14: Turso generation three and Adaptive generation two paired groups

Each candidate is compared with its own previous retained incumbent on the fixed development questions. Applications overlap; groups without retrieval references have unavailable quality. Values use a 0–100 scale, while deltas use unrounded measurements. These groups do not select an application router.

## Turso

Candidate `versioned-002`; reference `versioned-001`; treatment `consultation`.

### Application

| Group | Eligible | Previous nDCG | Candidate nDCG | Delta points | Candidate recall | Candidate MRR | Improved / regressed / tied |
| --- | --- | --- | --- | --- | --- | --- | --- |
| confluence | 39 | 69.87 | 69.98 | +0.11 | 78.71 | 74.02 | 13 / 3 / 23 |
| fireflies | 9 | 77.65 | 71.57 | -6.08 | 83.86 | 68.14 | 0 / 3 / 6 |
| github | 12 | 61.99 | 61.90 | -0.09 | 73.20 | 67.21 | 6 / 3 / 3 |
| gmail | 10 | 72.70 | 67.00 | -5.70 | 85.59 | 63.93 | 1 / 3 / 6 |
| google_drive | 14 | 74.96 | 76.05 | +1.09 | 87.07 | 78.14 | 5 / 0 / 9 |
| hubspot | 9 | 74.14 | 74.14 | +0.00 | 82.76 | 71.26 | 0 / 0 / 9 |
| jira | 26 | 80.47 | 81.38 | +0.91 | 85.82 | 86.01 | 9 / 2 / 15 |
| linear | 15 | 82.91 | 83.25 | +0.33 | 86.31 | 83.48 | 2 / 0 / 13 |
| slack | 24 | 56.52 | 56.76 | +0.24 | 69.94 | 54.93 | 5 / 2 / 17 |

### Category

| Group | Eligible | Previous nDCG | Candidate nDCG | Delta points | Candidate recall | Candidate MRR | Improved / regressed / tied |
| --- | --- | --- | --- | --- | --- | --- | --- |
| basic | 24 | 84.67 | 84.25 | -0.42 | 91.67 | 81.98 | 1 / 1 / 22 |
| completeness | 12 | 58.41 | 59.87 | +1.46 | 64.58 | 68.55 | 5 / 2 / 5 |
| conflicting_info | 4 | 97.99 | 97.99 | +0.00 | 100.00 | 100.00 | 0 / 0 / 4 |
| constrained | 8 | 88.18 | 86.93 | -1.25 | 93.75 | 91.67 | 1 / 1 / 6 |
| high_level | 0 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | 0 / 0 / 0 |
| info_not_found | 0 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | 0 / 0 / 0 |
| intra_document_reasoning | 12 | 100.00 | 96.92 | -3.08 | 100.00 | 95.83 | 0 / 1 / 11 |
| miscellaneous | 8 | 92.88 | 92.88 | +0.00 | 100.00 | 90.62 | 0 / 0 / 8 |
| project_related | 12 | 63.93 | 66.74 | +2.81 | 75.60 | 78.47 | 9 / 0 / 3 |
| semantic | 32 | 39.16 | 36.15 | -3.01 | 56.25 | 29.77 | 0 / 5 / 27 |

## Adaptive

Candidate `versioned-001`; reference `retained-start`; treatment `construction`.

### Application

| Group | Eligible | Previous nDCG | Candidate nDCG | Delta points | Candidate recall | Candidate MRR | Improved / regressed / tied |
| --- | --- | --- | --- | --- | --- | --- | --- |
| confluence | 39 | 68.09 | 66.39 | -1.70 | 77.36 | 69.86 | 10 / 15 / 14 |
| fireflies | 9 | 69.60 | 71.95 | +2.35 | 79.47 | 71.73 | 1 / 3 / 5 |
| github | 12 | 62.71 | 53.55 | -9.16 | 64.58 | 56.35 | 2 / 7 / 3 |
| gmail | 10 | 71.15 | 51.05 | -20.10 | 69.95 | 46.94 | 1 / 5 / 4 |
| google_drive | 14 | 68.73 | 65.96 | -2.77 | 73.05 | 65.46 | 2 / 4 / 8 |
| hubspot | 9 | 59.97 | 56.90 | -3.07 | 56.90 | 56.90 | 0 / 1 / 8 |
| jira | 26 | 69.16 | 66.07 | -3.09 | 72.32 | 70.49 | 6 / 9 / 11 |
| linear | 15 | 81.33 | 83.95 | +2.63 | 85.50 | 86.31 | 3 / 2 / 10 |
| slack | 24 | 50.16 | 44.73 | -5.43 | 49.81 | 48.97 | 5 / 8 / 11 |

### Category

| Group | Eligible | Previous nDCG | Candidate nDCG | Delta points | Candidate recall | Candidate MRR | Improved / regressed / tied |
| --- | --- | --- | --- | --- | --- | --- | --- |
| basic | 24 | 84.72 | 79.42 | -5.30 | 83.33 | 78.12 | 0 / 3 / 21 |
| completeness | 12 | 62.90 | 43.27 | -19.63 | 44.79 | 54.44 | 0 / 12 / 0 |
| conflicting_info | 4 | 96.26 | 94.25 | -2.01 | 100.00 | 100.00 | 0 / 1 / 3 |
| constrained | 8 | 80.70 | 81.81 | +1.12 | 93.75 | 85.42 | 2 / 2 / 4 |
| high_level | 0 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | 0 / 0 / 0 |
| info_not_found | 0 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | 0 / 0 / 0 |
| intra_document_reasoning | 12 | 100.00 | 100.00 | +0.00 | 100.00 | 100.00 | 0 / 0 / 12 |
| miscellaneous | 8 | 87.50 | 78.27 | -9.23 | 87.50 | 75.00 | 0 / 2 / 6 |
| project_related | 12 | 60.27 | 60.14 | -0.12 | 74.91 | 70.83 | 7 / 4 / 1 |
| semantic | 32 | 20.22 | 17.68 | -2.53 | 28.12 | 14.51 | 4 / 7 / 21 |

[Results and accounting](README.md) · [CTA](cta.md) · [Full metrics](aggregate.json)
