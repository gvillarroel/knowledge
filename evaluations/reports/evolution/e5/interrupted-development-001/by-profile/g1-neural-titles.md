# Construction profile: g1-neural-titles

[General development comparison](../README.md) · [Cost, time and accuracy](../cta.md)

Development retrieval diagnostics; values are not independent validation or official benchmark scores. Primary routes use the predeclared family default. Qualification applies to the whole profile, including every failed cell.

| Dataset | Skill family | Profile | Qualified | Route | Primary | nDCG@10 | Recall@10 | MRR@10 | Query P95 ms |
|---|---|---|---|---|---|---:|---:|---:|---:|
| architecture | adaptive | g1-neural-titles | True | adaptive | True | 86.29 | 95.83 | 90.50 | 1693.10 |
| architecture | classical | g1-neural-titles | True | fusion | True | 91.85 | 95.83 | 97.50 | 698.39 |
| architecture | classical | g1-neural-titles | True | association | False | 91.32 | 95.00 | 97.50 | 703.29 |
| architecture | classical | g1-neural-titles | True | bm25 | False | 82.37 | 80.83 | 96.25 | 723.26 |
| architecture | classical | g1-neural-titles | True | topic | False | 91.32 | 95.00 | 97.50 | 742.71 |
| architecture | embeddings | g1-neural-titles | True | hybrid | True | 77.08 | 93.54 | 78.82 | 547.10 |
| architecture | embeddings | g1-neural-titles | True | lexical | False | 72.13 | 92.92 | 71.57 | 388.68 |
| architecture | embeddings | g1-neural-titles | True | vector | False | 75.73 | 91.25 | 77.65 | 140.17 |
| architecture | ensemble | g1-neural-titles | True | quality | True | 84.60 | 95.83 | 86.75 | 5266.58 |
| architecture | ensemble | g1-neural-titles | True | fast | False | 86.67 | 95.83 | 89.38 | 4224.49 |
| architecture | ensemble | g1-neural-titles | True | robust | False | 86.29 | 95.83 | 90.50 | 1748.76 |
| architecture | entity-graph | g1-neural-titles | True | fusion | True | 83.50 | 97.50 | 81.33 | 2877.77 |
| architecture | entity-graph | g1-neural-titles | True | entity | False | 81.76 | 93.54 | 81.15 | 2917.60 |
| architecture | entity-graph | g1-neural-titles | True | lexical | False | 88.98 | 98.33 | 89.25 | 2935.49 |
| architecture | entity-graph | g1-neural-titles | True | traversal | False | 80.30 | 92.92 | 80.92 | 2912.43 |
| architecture | graphify | g1-neural-titles | True | search | True | 57.76 | 59.58 | 68.75 | 96.21 |
| architecture | legacy | g1-neural-titles | True | lexical | True | 81.55 | 95.00 | 80.62 | 0.19 |
| architecture | turso | g1-neural-titles | True | lexical-sql | True | 58.40 | 86.25 | 52.72 | 339.36 |
| astro | adaptive | g1-neural-titles | True | adaptive | True | 80.86 | 86.88 | 91.04 | 2627.94 |
| astro | classical | g1-neural-titles | True | fusion | True | 80.86 | 86.88 | 91.04 | 80.70 |
| astro | classical | g1-neural-titles | True | association | False | 80.87 | 86.88 | 91.04 | 76.03 |
| astro | classical | g1-neural-titles | True | bm25 | False | 78.70 | 86.25 | 87.92 | 58.13 |
| astro | classical | g1-neural-titles | True | topic | False | 80.87 | 86.88 | 91.04 | 77.01 |
| astro | embeddings | g1-neural-titles | True | hybrid | True | 74.34 | 91.04 | 73.62 | 247.56 |
| astro | embeddings | g1-neural-titles | True | lexical | False | 85.95 | 88.75 | 95.42 | 81.07 |
| astro | embeddings | g1-neural-titles | True | vector | False | 50.65 | 67.71 | 51.92 | 172.24 |
| astro | ensemble | g1-neural-titles | True | quality | True | 81.57 | 86.88 | 91.67 | 4057.05 |
| astro | ensemble | g1-neural-titles | True | fast | False | 82.09 | 86.88 | 92.08 | 3472.02 |
| astro | ensemble | g1-neural-titles | True | robust | False | 80.86 | 86.88 | 91.04 | 2621.32 |
| astro | entity-graph | g1-neural-titles | True | fusion | True | 69.47 | 82.29 | 76.71 | 1015.00 |
| astro | entity-graph | g1-neural-titles | True | entity | False | 68.01 | 87.29 | 68.86 | 1011.23 |
| astro | entity-graph | g1-neural-titles | True | lexical | False | 72.62 | 82.50 | 82.04 | 1017.02 |
| astro | entity-graph | g1-neural-titles | True | traversal | False | 32.30 | 50.42 | 30.31 | 1033.97 |
| astro | graphify | g1-neural-titles | True | search | True | 57.79 | 77.29 | 57.92 | 150.12 |
| astro | legacy | g1-neural-titles | True | lexical | True | 60.52 | 75.42 | 64.47 | 2.27 |
| astro | turso | g1-neural-titles | True | lexical-sql | True | 47.81 | 66.67 | 49.17 | 136.75 |
| data-science | adaptive | g1-neural-titles | True | adaptive | True | 91.92 | 99.17 | 93.23 | 2437.19 |
| data-science | classical | g1-neural-titles | True | fusion | True | 80.54 | 78.54 | 91.25 | 862.13 |
| data-science | classical | g1-neural-titles | True | association | False | 80.54 | 78.54 | 91.25 | 863.48 |
| data-science | classical | g1-neural-titles | True | bm25 | False | 93.28 | 98.33 | 94.11 | 834.36 |
| data-science | classical | g1-neural-titles | True | topic | False | 80.54 | 78.54 | 91.25 | 797.54 |
| data-science | embeddings | g1-neural-titles | True | hybrid | True | 87.89 | 97.50 | 88.34 | 940.49 |
| data-science | embeddings | g1-neural-titles | True | lexical | False | 63.24 | 83.33 | 58.19 | 763.27 |
| data-science | embeddings | g1-neural-titles | True | vector | False | 87.92 | 97.50 | 87.38 | 143.11 |
| data-science | ensemble | g1-neural-titles | True | quality | True | 92.96 | 99.17 | 94.11 | 10189.20 |
| data-science | ensemble | g1-neural-titles | True | fast | False | 93.74 | 99.17 | 95.50 | 8657.60 |
| data-science | ensemble | g1-neural-titles | True | robust | False | 91.92 | 99.17 | 93.23 | 2165.97 |
| data-science | entity-graph | g1-neural-titles | True | fusion | True | 85.79 | 97.50 | 86.88 | 6960.53 |
| data-science | entity-graph | g1-neural-titles | True | entity | False | 80.82 | 96.67 | 79.67 | 7347.56 |
| data-science | entity-graph | g1-neural-titles | True | lexical | False | 90.31 | 99.17 | 88.75 | 7298.26 |
| data-science | entity-graph | g1-neural-titles | True | traversal | False | 51.20 | 79.58 | 43.55 | 7028.83 |
| data-science | graphify | g1-neural-titles | True | search | True | 54.41 | 53.96 | 62.50 | 323.68 |
| data-science | legacy | g1-neural-titles | True | lexical | True | 83.22 | 95.00 | 81.75 | 0.26 |
| data-science | turso | g1-neural-titles | True | lexical-sql | True | 40.16 | 74.38 | 31.79 | 455.93 |
| enterprise | adaptive | g1-neural-titles | True | adaptive | True | 50.34 | 59.00 | 57.47 | 1302.65 |
| enterprise | classical | g1-neural-titles | True | fusion | True | 43.42 | 42.46 | 56.25 | 39.79 |
| enterprise | classical | g1-neural-titles | True | association | False | 47.21 | 45.86 | 56.25 | 40.58 |
| enterprise | classical | g1-neural-titles | True | bm25 | False | 58.93 | 64.56 | 60.59 | 39.33 |
| enterprise | classical | g1-neural-titles | True | topic | False | 46.68 | 46.22 | 55.00 | 39.59 |
| enterprise | embeddings | g1-neural-titles | True | hybrid | True | 63.19 | 68.38 | 64.38 | 184.70 |
| enterprise | embeddings | g1-neural-titles | True | lexical | False | 59.07 | 61.86 | 61.50 | 9.70 |
| enterprise | embeddings | g1-neural-titles | True | vector | False | 60.70 | 68.94 | 60.82 | 181.96 |
| enterprise | ensemble | g1-neural-titles | True | quality | True | 55.66 | 59.00 | 60.42 | 1643.53 |
| enterprise | ensemble | g1-neural-titles | True | fast | False | 52.36 | 59.00 | 59.10 | 1364.85 |
| enterprise | ensemble | g1-neural-titles | True | robust | False | 50.34 | 59.00 | 57.47 | 1320.44 |
| enterprise | entity-graph | g1-neural-titles | True | fusion | True | 46.73 | 58.04 | 47.33 | 50.29 |
| enterprise | entity-graph | g1-neural-titles | True | entity | False | 45.25 | 56.58 | 46.67 | 50.72 |
| enterprise | entity-graph | g1-neural-titles | True | lexical | False | 59.40 | 63.73 | 60.78 | 54.63 |
| enterprise | entity-graph | g1-neural-titles | True | traversal | False | 43.27 | 50.33 | 46.04 | 51.89 |
| enterprise | graphify | g1-neural-titles | True | search | True | 13.63 | 17.37 | 20.42 | 136.26 |
| enterprise | legacy | g1-neural-titles | True | lexical | True | 57.50 | 61.92 | 59.86 | 3.16 |
| enterprise | turso | g1-neural-titles | True | lexical-sql | True | 40.32 | 49.87 | 40.85 | 39.00 |
