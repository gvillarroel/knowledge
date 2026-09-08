# Construction profile: g0-bm25-low-b

[General development comparison](../README.md) · [Cost, time and accuracy](../cta.md)

Development retrieval diagnostics; values are not independent validation or official benchmark scores. Primary routes use the predeclared family default. Qualification applies to the whole profile, including every failed cell.

| Dataset | Skill family | Profile | Qualified | Route | Primary | nDCG@10 | Recall@10 | MRR@10 | Query P95 ms |
|---|---|---|---|---|---|---:|---:|---:|---:|
| architecture | adaptive | g0-bm25-low-b | True | adaptive | True | 85.80 | 96.04 | 90.50 | 1912.71 |
| architecture | classical | g0-bm25-low-b | True | fusion | True | 89.83 | 96.46 | 92.92 | 676.42 |
| architecture | classical | g0-bm25-low-b | True | association | False | 89.93 | 96.46 | 93.33 | 689.40 |
| architecture | classical | g0-bm25-low-b | True | bm25 | False | 80.11 | 80.21 | 91.46 | 696.88 |
| architecture | classical | g0-bm25-low-b | True | topic | False | 89.91 | 96.46 | 93.33 | 703.46 |
| architecture | embeddings | g0-bm25-low-b | True | hybrid | True | 72.38 | 92.08 | 71.54 | 498.33 |
| architecture | embeddings | g0-bm25-low-b | True | lexical | False | 72.13 | 92.92 | 71.57 | 427.85 |
| architecture | embeddings | g0-bm25-low-b | True | vector | False | 65.56 | 84.38 | 65.99 | 1.64 |
| architecture | ensemble | g0-bm25-low-b | True | quality | True | 85.20 | 96.04 | 88.00 | 5732.61 |
| architecture | ensemble | g0-bm25-low-b | True | fast | False | 86.76 | 96.04 | 90.92 | 4295.78 |
| architecture | ensemble | g0-bm25-low-b | True | robust | False | 85.80 | 96.04 | 90.50 | 1903.62 |
| architecture | entity-graph | g0-bm25-low-b | True | fusion | True | 83.42 | 97.50 | 81.25 | 3553.18 |
| architecture | entity-graph | g0-bm25-low-b | True | entity | False | 81.76 | 93.54 | 81.15 | 3782.93 |
| architecture | entity-graph | g0-bm25-low-b | True | lexical | False | 87.93 | 97.71 | 88.50 | 3706.87 |
| architecture | entity-graph | g0-bm25-low-b | True | traversal | False | 80.30 | 92.92 | 80.92 | 3296.40 |
| architecture | graphify | g0-bm25-low-b | True | search | True | 57.76 | 59.58 | 68.75 | 96.05 |
| architecture | legacy | g0-bm25-low-b | True | lexical | True | 81.55 | 95.00 | 80.62 | 0.39 |
| architecture | turso | g0-bm25-low-b | True | lexical-sql | True | 58.40 | 86.25 | 52.72 | 354.12 |
| astro | adaptive | g0-bm25-low-b | True | adaptive | True | 77.74 | 87.08 | 83.90 | 5357.10 |
| astro | classical | g0-bm25-low-b | True | fusion | True | 77.74 | 87.08 | 83.90 | 79.81 |
| astro | classical | g0-bm25-low-b | True | association | False | 78.31 | 87.92 | 84.11 | 82.08 |
| astro | classical | g0-bm25-low-b | True | bm25 | False | 78.63 | 87.08 | 84.77 | 65.51 |
| astro | classical | g0-bm25-low-b | True | topic | False | 77.78 | 87.08 | 84.08 | 80.25 |
| astro | embeddings | g0-bm25-low-b | True | hybrid | True | 78.52 | 85.83 | 85.54 | 154.16 |
| astro | embeddings | g0-bm25-low-b | True | lexical | False | 85.95 | 88.75 | 95.42 | 124.60 |
| astro | embeddings | g0-bm25-low-b | True | vector | False | 53.34 | 68.75 | 55.19 | 26.02 |
| astro | ensemble | g0-bm25-low-b | True | quality | True | 79.57 | 87.08 | 88.02 | 4726.36 |
| astro | ensemble | g0-bm25-low-b | True | fast | False | 77.93 | 87.08 | 85.49 | 4340.73 |
| astro | ensemble | g0-bm25-low-b | True | robust | False | 77.74 | 87.08 | 83.90 | 3048.70 |
| astro | entity-graph | g0-bm25-low-b | True | fusion | True | 66.67 | 82.29 | 71.65 | 1211.67 |
| astro | entity-graph | g0-bm25-low-b | True | entity | False | 68.01 | 87.29 | 68.86 | 1382.09 |
| astro | entity-graph | g0-bm25-low-b | True | lexical | False | 75.63 | 84.17 | 83.12 | 1445.36 |
| astro | entity-graph | g0-bm25-low-b | True | traversal | False | 32.30 | 50.42 | 30.31 | 1215.95 |
| astro | graphify | g0-bm25-low-b | True | search | True | 57.79 | 77.29 | 57.92 | 139.87 |
| astro | legacy | g0-bm25-low-b | True | lexical | True | 60.52 | 75.42 | 64.47 | 3.27 |
| astro | turso | g0-bm25-low-b | True | lexical-sql | True | 47.81 | 66.67 | 49.17 | 160.81 |
| data-science | adaptive | g0-bm25-low-b | True | adaptive | True | 91.97 | 99.17 | 93.19 | 3440.59 |
| data-science | classical | g0-bm25-low-b | True | fusion | True | 80.54 | 78.54 | 91.25 | 997.34 |
| data-science | classical | g0-bm25-low-b | True | association | False | 80.54 | 78.54 | 91.25 | 855.92 |
| data-science | classical | g0-bm25-low-b | True | bm25 | False | 93.33 | 98.33 | 94.03 | 895.80 |
| data-science | classical | g0-bm25-low-b | True | topic | False | 80.54 | 78.54 | 91.25 | 834.52 |
| data-science | embeddings | g0-bm25-low-b | True | hybrid | True | 60.04 | 88.96 | 52.00 | 808.83 |
| data-science | embeddings | g0-bm25-low-b | True | lexical | False | 63.24 | 83.33 | 58.19 | 778.35 |
| data-science | embeddings | g0-bm25-low-b | True | vector | False | 39.38 | 70.42 | 29.13 | 1.99 |
| data-science | ensemble | g0-bm25-low-b | True | quality | True | 93.79 | 99.17 | 94.06 | 12193.16 |
| data-science | ensemble | g0-bm25-low-b | True | fast | False | 93.98 | 99.17 | 95.50 | 9948.19 |
| data-science | ensemble | g0-bm25-low-b | True | robust | False | 91.97 | 99.17 | 93.19 | 2591.67 |
| data-science | entity-graph | g0-bm25-low-b | True | fusion | True | 80.74 | 97.50 | 78.36 | 8622.57 |
| data-science | entity-graph | g0-bm25-low-b | True | entity | False | 80.82 | 96.67 | 79.67 | 10356.84 |
| data-science | entity-graph | g0-bm25-low-b | True | lexical | False | 89.22 | 98.33 | 88.96 | 10429.97 |
| data-science | entity-graph | g0-bm25-low-b | True | traversal | False | 51.20 | 79.58 | 43.55 | 8855.73 |
| data-science | graphify | g0-bm25-low-b | True | search | True | 54.41 | 53.96 | 62.50 | 342.62 |
| data-science | legacy | g0-bm25-low-b | True | lexical | True | 83.22 | 95.00 | 81.75 | 0.61 |
| data-science | turso | g0-bm25-low-b | True | lexical-sql | True | 40.16 | 74.38 | 31.79 | 460.87 |
| enterprise | adaptive | g0-bm25-low-b | True | adaptive | True | 50.69 | 59.07 | 57.51 | 1650.22 |
| enterprise | classical | g0-bm25-low-b | True | fusion | True | 44.25 | 43.99 | 56.25 | 47.77 |
| enterprise | classical | g0-bm25-low-b | True | association | False | 47.29 | 45.86 | 56.25 | 47.69 |
| enterprise | classical | g0-bm25-low-b | True | bm25 | False | 58.95 | 64.98 | 60.67 | 45.97 |
| enterprise | classical | g0-bm25-low-b | True | topic | False | 47.80 | 46.22 | 56.25 | 49.02 |
| enterprise | embeddings | g0-bm25-low-b | True | hybrid | True | 51.64 | 59.91 | 54.19 | 48.41 |
| enterprise | embeddings | g0-bm25-low-b | True | lexical | False | 59.07 | 61.86 | 61.50 | 10.08 |
| enterprise | embeddings | g0-bm25-low-b | True | vector | False | 32.56 | 36.92 | 37.72 | 35.73 |
| enterprise | ensemble | g0-bm25-low-b | True | quality | True | 53.88 | 59.07 | 57.86 | 1587.11 |
| enterprise | ensemble | g0-bm25-low-b | True | fast | False | 51.68 | 59.07 | 57.73 | 1459.75 |
| enterprise | ensemble | g0-bm25-low-b | True | robust | False | 50.69 | 59.07 | 57.51 | 1419.41 |
| enterprise | entity-graph | g0-bm25-low-b | True | fusion | True | 47.28 | 58.31 | 47.51 | 48.07 |
| enterprise | entity-graph | g0-bm25-low-b | True | entity | False | 45.25 | 56.58 | 46.67 | 49.60 |
| enterprise | entity-graph | g0-bm25-low-b | True | lexical | False | 58.33 | 63.73 | 59.06 | 50.52 |
| enterprise | entity-graph | g0-bm25-low-b | True | traversal | False | 43.27 | 50.33 | 46.04 | 50.24 |
| enterprise | graphify | g0-bm25-low-b | True | search | True | 13.63 | 17.37 | 20.42 | 155.25 |
| enterprise | legacy | g0-bm25-low-b | True | lexical | True | 57.50 | 61.92 | 59.86 | 3.23 |
| enterprise | turso | g0-bm25-low-b | True | lexical-sql | True | 40.32 | 49.87 | 40.85 | 40.62 |
