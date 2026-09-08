# Construction profile: g1-neural-expand

[General development comparison](../README.md) · [Cost, time and accuracy](../cta.md)

Development retrieval diagnostics; values are not independent validation or official benchmark scores. Primary routes use the predeclared family default. Qualification applies to the whole profile, including every failed cell.

| Dataset | Skill family | Profile | Qualified | Route | Primary | nDCG@10 | Recall@10 | MRR@10 | Query P95 ms |
|---|---|---|---|---|---|---:|---:|---:|---:|
| architecture | adaptive | g1-neural-expand | True | adaptive | True | 85.18 | 95.21 | 89.19 | 1646.16 |
| architecture | classical | g1-neural-expand | True | fusion | True | 91.72 | 97.29 | 95.00 | 984.23 |
| architecture | classical | g1-neural-expand | True | association | False | 91.72 | 97.29 | 95.00 | 750.43 |
| architecture | classical | g1-neural-expand | True | bm25 | False | 84.18 | 83.75 | 95.00 | 784.26 |
| architecture | classical | g1-neural-expand | True | topic | False | 91.72 | 97.29 | 95.00 | 779.78 |
| architecture | embeddings | g1-neural-expand | True | hybrid | True | 77.08 | 93.54 | 78.82 | 546.50 |
| architecture | embeddings | g1-neural-expand | True | lexical | False | 72.13 | 92.92 | 71.57 | 392.16 |
| architecture | embeddings | g1-neural-expand | True | vector | False | 75.73 | 91.25 | 77.65 | 137.31 |
| architecture | ensemble | g1-neural-expand | True | quality | True | 84.03 | 95.21 | 86.69 | 5514.24 |
| architecture | ensemble | g1-neural-expand | True | fast | False | 86.08 | 95.21 | 90.62 | 4574.66 |
| architecture | ensemble | g1-neural-expand | True | robust | False | 85.18 | 95.21 | 89.19 | 1735.99 |
| architecture | entity-graph | g1-neural-expand | True | fusion | True | 83.50 | 97.50 | 81.33 | 2801.28 |
| architecture | entity-graph | g1-neural-expand | True | entity | False | 81.76 | 93.54 | 81.15 | 2882.26 |
| architecture | entity-graph | g1-neural-expand | True | lexical | False | 88.98 | 98.33 | 89.25 | 2772.22 |
| architecture | entity-graph | g1-neural-expand | True | traversal | False | 80.30 | 92.92 | 80.92 | 2792.17 |
| architecture | graphify | g1-neural-expand | True | search | True | 57.76 | 59.58 | 68.75 | 105.48 |
| architecture | legacy | g1-neural-expand | True | lexical | True | 81.55 | 95.00 | 80.62 | 0.18 |
| architecture | turso | g1-neural-expand | True | lexical-sql | True | 58.40 | 86.25 | 52.72 | 348.66 |
| astro | adaptive | g1-neural-expand | True | adaptive | True | 83.27 | 88.75 | 92.08 | 2598.87 |
| astro | classical | g1-neural-expand | True | fusion | True | 83.27 | 88.75 | 92.08 | 78.06 |
| astro | classical | g1-neural-expand | True | association | False | 83.27 | 88.75 | 92.08 | 77.79 |
| astro | classical | g1-neural-expand | True | bm25 | False | 83.13 | 88.75 | 92.08 | 62.35 |
| astro | classical | g1-neural-expand | True | topic | False | 83.29 | 88.75 | 92.08 | 81.40 |
| astro | embeddings | g1-neural-expand | True | hybrid | True | 74.34 | 91.04 | 73.62 | 233.80 |
| astro | embeddings | g1-neural-expand | True | lexical | False | 85.95 | 88.75 | 95.42 | 79.74 |
| astro | embeddings | g1-neural-expand | True | vector | False | 50.65 | 67.71 | 51.92 | 153.16 |
| astro | ensemble | g1-neural-expand | True | quality | True | 81.26 | 88.75 | 88.96 | 3852.69 |
| astro | ensemble | g1-neural-expand | True | fast | False | 80.90 | 88.75 | 88.54 | 3470.83 |
| astro | ensemble | g1-neural-expand | True | robust | False | 83.27 | 88.75 | 92.08 | 2645.15 |
| astro | entity-graph | g1-neural-expand | True | fusion | True | 69.47 | 82.29 | 76.71 | 1054.78 |
| astro | entity-graph | g1-neural-expand | True | entity | False | 68.01 | 87.29 | 68.86 | 1054.23 |
| astro | entity-graph | g1-neural-expand | True | lexical | False | 72.62 | 82.50 | 82.04 | 1043.98 |
| astro | entity-graph | g1-neural-expand | True | traversal | False | 32.30 | 50.42 | 30.31 | 1040.85 |
| astro | graphify | g1-neural-expand | True | search | True | 57.79 | 77.29 | 57.92 | 166.96 |
| astro | legacy | g1-neural-expand | True | lexical | True | 60.52 | 75.42 | 64.47 | 2.43 |
| astro | turso | g1-neural-expand | True | lexical-sql | True | 47.81 | 66.67 | 49.17 | 138.69 |
| data-science | adaptive | g1-neural-expand | True | adaptive | True | 91.41 | 98.33 | 93.23 | 2628.75 |
| data-science | classical | g1-neural-expand | True | fusion | True | 80.54 | 78.54 | 91.25 | 858.77 |
| data-science | classical | g1-neural-expand | True | association | False | 80.54 | 78.54 | 91.25 | 856.92 |
| data-science | classical | g1-neural-expand | True | bm25 | False | 93.08 | 98.33 | 94.06 | 808.09 |
| data-science | classical | g1-neural-expand | True | topic | False | 80.54 | 78.54 | 91.25 | 792.47 |
| data-science | embeddings | g1-neural-expand | True | hybrid | True | 87.89 | 97.50 | 88.34 | 1366.91 |
| data-science | embeddings | g1-neural-expand | True | lexical | False | 63.24 | 83.33 | 58.19 | 875.88 |
| data-science | embeddings | g1-neural-expand | True | vector | False | 87.92 | 97.50 | 87.38 | 162.69 |
| data-science | ensemble | g1-neural-expand | True | quality | True | 92.47 | 98.33 | 94.11 | 10525.43 |
| data-science | ensemble | g1-neural-expand | True | fast | False | 93.07 | 98.33 | 95.50 | 8927.69 |
| data-science | ensemble | g1-neural-expand | True | robust | False | 91.41 | 98.33 | 93.23 | 2204.20 |
| data-science | entity-graph | g1-neural-expand | True | fusion | True | 85.79 | 97.50 | 86.88 | 6790.87 |
| data-science | entity-graph | g1-neural-expand | True | entity | False | 80.82 | 96.67 | 79.67 | 7353.16 |
| data-science | entity-graph | g1-neural-expand | True | lexical | False | 90.31 | 99.17 | 88.75 | 7188.99 |
| data-science | entity-graph | g1-neural-expand | True | traversal | False | 51.20 | 79.58 | 43.55 | 6921.29 |
| data-science | graphify | g1-neural-expand | True | search | True | 54.41 | 53.96 | 62.50 | 316.88 |
| data-science | legacy | g1-neural-expand | True | lexical | True | 83.22 | 95.00 | 81.75 | 0.30 |
| data-science | turso | g1-neural-expand | True | lexical-sql | True | 40.16 | 74.38 | 31.79 | 486.67 |
| enterprise | adaptive | g1-neural-expand | True | adaptive | True | 50.57 | 56.50 | 58.55 | 1305.94 |
| enterprise | classical | g1-neural-expand | True | fusion | True | 44.35 | 42.46 | 57.50 | 41.14 |
| enterprise | classical | g1-neural-expand | True | association | False | 47.72 | 45.86 | 57.50 | 40.26 |
| enterprise | classical | g1-neural-expand | True | bm25 | False | 58.93 | 64.56 | 60.59 | 39.79 |
| enterprise | classical | g1-neural-expand | True | topic | False | 48.11 | 46.22 | 57.50 | 40.71 |
| enterprise | embeddings | g1-neural-expand | True | hybrid | True | 63.19 | 68.38 | 64.38 | 192.32 |
| enterprise | embeddings | g1-neural-expand | True | lexical | False | 59.07 | 61.86 | 61.50 | 9.93 |
| enterprise | embeddings | g1-neural-expand | True | vector | False | 60.70 | 68.94 | 60.82 | 196.06 |
| enterprise | ensemble | g1-neural-expand | True | quality | True | 54.35 | 56.50 | 59.48 | 1637.60 |
| enterprise | ensemble | g1-neural-expand | True | fast | False | 51.51 | 56.50 | 58.73 | 1367.41 |
| enterprise | ensemble | g1-neural-expand | True | robust | False | 50.57 | 56.50 | 58.55 | 1310.08 |
| enterprise | entity-graph | g1-neural-expand | True | fusion | True | 46.73 | 58.04 | 47.33 | 77.08 |
| enterprise | entity-graph | g1-neural-expand | True | entity | False | 45.25 | 56.58 | 46.67 | 85.55 |
| enterprise | entity-graph | g1-neural-expand | True | lexical | False | 59.40 | 63.73 | 60.78 | 90.13 |
| enterprise | entity-graph | g1-neural-expand | True | traversal | False | 43.27 | 50.33 | 46.04 | 74.75 |
| enterprise | graphify | g1-neural-expand | True | search | True | 13.63 | 17.37 | 20.42 | 134.83 |
| enterprise | legacy | g1-neural-expand | True | lexical | True | 57.50 | 61.92 | 59.86 | 3.50 |
| enterprise | turso | g1-neural-expand | True | lexical-sql | True | 40.32 | 49.87 | 40.85 | 47.71 |
