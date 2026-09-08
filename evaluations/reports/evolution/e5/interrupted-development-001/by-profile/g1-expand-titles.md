# Construction profile: g1-expand-titles

[General development comparison](../README.md) · [Cost, time and accuracy](../cta.md)

Development retrieval diagnostics; values are not independent validation or official benchmark scores. Primary routes use the predeclared family default. Qualification applies to the whole profile, including every failed cell.

| Dataset | Skill family | Profile | Qualified | Route | Primary | nDCG@10 | Recall@10 | MRR@10 | Query P95 ms |
|---|---|---|---|---|---|---:|---:|---:|---:|
| architecture | adaptive | g1-expand-titles | False | adaptive | True | 85.91 | 95.83 | 89.25 | 1804.95 |
| architecture | classical | g1-expand-titles | False | fusion | True | 91.31 | 95.83 | 96.25 | 690.94 |
| architecture | classical | g1-expand-titles | False | association | False | 91.31 | 95.83 | 96.25 | 700.08 |
| architecture | classical | g1-expand-titles | False | bm25 | False | 82.37 | 80.83 | 96.25 | 717.01 |
| architecture | classical | g1-expand-titles | False | topic | False | 91.31 | 95.83 | 96.25 | 687.35 |
| architecture | embeddings | g1-expand-titles | False | hybrid | True | 72.38 | 92.08 | 71.54 | 417.85 |
| architecture | embeddings | g1-expand-titles | False | lexical | False | 72.13 | 92.92 | 71.57 | 389.38 |
| architecture | embeddings | g1-expand-titles | False | vector | False | 65.56 | 84.38 | 65.99 | 1.17 |
| architecture | ensemble | g1-expand-titles | False | quality | True | 85.47 | 95.83 | 88.00 | 5181.91 |
| architecture | ensemble | g1-expand-titles | False | fast | False | 87.03 | 95.83 | 90.71 | 4347.33 |
| architecture | ensemble | g1-expand-titles | False | robust | False | 85.91 | 95.83 | 89.25 | 1646.97 |
| architecture | entity-graph | g1-expand-titles | False | fusion | True | 83.50 | 97.50 | 81.33 | 2790.41 |
| architecture | entity-graph | g1-expand-titles | False | entity | False | 81.76 | 93.54 | 81.15 | 2763.61 |
| architecture | entity-graph | g1-expand-titles | False | lexical | False | 88.98 | 98.33 | 89.25 | 2776.41 |
| architecture | entity-graph | g1-expand-titles | False | traversal | False | 80.30 | 92.92 | 80.92 | 2798.72 |
| architecture | graphify | g1-expand-titles | False | search | True | 57.76 | 59.58 | 68.75 | 95.09 |
| architecture | legacy | g1-expand-titles | False | lexical | True | 81.55 | 95.00 | 80.62 | 0.28 |
| architecture | turso | g1-expand-titles | False | lexical-sql | True | 58.40 | 86.25 | 52.72 | 333.05 |
| astro | adaptive | g1-expand-titles | False | adaptive | True | 80.06 | 86.25 | 90.42 | 2547.21 |
| astro | classical | g1-expand-titles | False | fusion | True | 80.06 | 86.25 | 90.42 | 73.92 |
| astro | classical | g1-expand-titles | False | association | False | 80.06 | 86.25 | 90.42 | 77.25 |
| astro | classical | g1-expand-titles | False | bm25 | False | 78.70 | 86.25 | 87.92 | 62.81 |
| astro | classical | g1-expand-titles | False | topic | False | 80.06 | 86.25 | 90.42 | 75.16 |
| astro | embeddings | g1-expand-titles | False | hybrid | True | 78.52 | 85.83 | 85.54 | 94.98 |
| astro | embeddings | g1-expand-titles | False | lexical | False | 85.95 | 88.75 | 95.42 | 80.00 |
| astro | embeddings | g1-expand-titles | False | vector | False | 53.34 | 68.75 | 55.19 | 15.66 |
| astro | ensemble | g1-expand-titles | False | quality | True | 79.84 | 86.25 | 89.38 | 3535.82 |
| astro | ensemble | g1-expand-titles | False | fast | False | 80.44 | 86.25 | 90.42 | 3579.76 |
| astro | ensemble | g1-expand-titles | False | robust | False | 80.06 | 86.25 | 90.42 | 2712.08 |
| astro | entity-graph | g1-expand-titles | False | fusion | True | 69.47 | 82.29 | 76.71 | 1024.62 |
| astro | entity-graph | g1-expand-titles | False | entity | False | 68.01 | 87.29 | 68.86 | 1012.61 |
| astro | entity-graph | g1-expand-titles | False | lexical | False | 72.62 | 82.50 | 82.04 | 1029.56 |
| astro | entity-graph | g1-expand-titles | False | traversal | False | 32.30 | 50.42 | 30.31 | 1033.30 |
| astro | graphify | g1-expand-titles | False | search | True | 57.79 | 77.29 | 57.92 | 141.01 |
| astro | legacy | g1-expand-titles | False | lexical | True | 60.52 | 75.42 | 64.47 | 2.16 |
| astro | turso | g1-expand-titles | False | lexical-sql | True | 47.81 | 66.67 | 49.17 | 137.66 |
| data-science | adaptive | g1-expand-titles | False | adaptive | True | 91.89 | 99.17 | 93.23 | 2504.37 |
| data-science | classical | g1-expand-titles | False | fusion | True | 80.54 | 78.54 | 91.25 | 844.96 |
| data-science | classical | g1-expand-titles | False | association | False | 80.54 | 78.54 | 91.25 | 764.16 |
| data-science | classical | g1-expand-titles | False | bm25 | False | 93.28 | 98.33 | 94.11 | 806.86 |
| data-science | classical | g1-expand-titles | False | topic | False | 80.54 | 78.54 | 91.25 | 793.12 |
| data-science | embeddings | g1-expand-titles | False | hybrid | True | 60.04 | 88.96 | 52.00 | 783.67 |
| data-science | embeddings | g1-expand-titles | False | lexical | False | 63.24 | 83.33 | 58.19 | 756.20 |
| data-science | embeddings | g1-expand-titles | False | vector | False | 39.38 | 70.42 | 29.13 | 2.05 |
| data-science | entity-graph | g1-expand-titles | False | fusion | True | 85.79 | 97.50 | 86.88 | 6671.49 |
| data-science | entity-graph | g1-expand-titles | False | entity | False | 80.82 | 96.67 | 79.67 | 7243.98 |
| data-science | entity-graph | g1-expand-titles | False | lexical | False | 90.31 | 99.17 | 88.75 | 7047.50 |
| data-science | entity-graph | g1-expand-titles | False | traversal | False | 51.20 | 79.58 | 43.55 | 6716.62 |
| data-science | graphify | g1-expand-titles | False | search | True | 54.41 | 53.96 | 62.50 | 323.47 |
| data-science | legacy | g1-expand-titles | False | lexical | True | 83.22 | 95.00 | 81.75 | 0.29 |
| data-science | turso | g1-expand-titles | False | lexical-sql | True | 40.16 | 74.38 | 31.79 | 466.47 |
| enterprise | adaptive | g1-expand-titles | False | adaptive | True | 50.57 | 56.50 | 58.55 | 1301.74 |
| enterprise | classical | g1-expand-titles | False | fusion | True | 44.35 | 42.46 | 57.50 | 41.98 |
| enterprise | classical | g1-expand-titles | False | association | False | 47.72 | 45.86 | 57.50 | 40.56 |
| enterprise | classical | g1-expand-titles | False | bm25 | False | 58.93 | 64.56 | 60.59 | 39.78 |
| enterprise | classical | g1-expand-titles | False | topic | False | 48.11 | 46.22 | 57.50 | 40.56 |
| enterprise | embeddings | g1-expand-titles | False | hybrid | True | 51.64 | 59.91 | 54.19 | 45.25 |
| enterprise | embeddings | g1-expand-titles | False | lexical | False | 59.07 | 61.86 | 61.50 | 9.60 |
| enterprise | embeddings | g1-expand-titles | False | vector | False | 32.56 | 36.92 | 37.72 | 35.00 |
| enterprise | ensemble | g1-expand-titles | False | quality | True | 54.02 | 56.50 | 59.44 | 1479.62 |
| enterprise | ensemble | g1-expand-titles | False | fast | False | 51.51 | 56.50 | 58.73 | 1397.23 |
| enterprise | ensemble | g1-expand-titles | False | robust | False | 50.57 | 56.50 | 58.55 | 1319.53 |
| enterprise | entity-graph | g1-expand-titles | False | fusion | True | 46.73 | 58.04 | 47.33 | 50.25 |
| enterprise | entity-graph | g1-expand-titles | False | entity | False | 45.25 | 56.58 | 46.67 | 51.90 |
| enterprise | entity-graph | g1-expand-titles | False | lexical | False | 59.40 | 63.73 | 60.78 | 51.29 |
| enterprise | entity-graph | g1-expand-titles | False | traversal | False | 43.27 | 50.33 | 46.04 | 51.77 |
| enterprise | graphify | g1-expand-titles | False | search | True | 13.63 | 17.37 | 20.42 | 132.31 |
| enterprise | legacy | g1-expand-titles | False | lexical | True | 57.50 | 61.92 | 59.86 | 3.03 |
| enterprise | turso | g1-expand-titles | False | lexical-sql | True | 40.32 | 49.87 | 40.85 | 38.95 |

## Failed cells

| Dataset | Skill family | Profile | Status | Error |
|---|---|---|---|---|
| data-science | ensemble | g1-expand-titles | interrupted-no-native-result | unavailable |
