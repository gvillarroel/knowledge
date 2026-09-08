# Dataset: astro

[General development comparison](../README.md) · [Cost, time and accuracy](../cta.md)

Development retrieval diagnostics; values are not independent validation or official benchmark scores. Primary routes use the predeclared family default. Qualification applies to the whole profile, including every failed cell.

| Dataset | Skill family | Profile | Qualified | Route | Primary | nDCG@10 | Recall@10 | MRR@10 | Query P95 ms |
|---|---|---|---|---|---|---:|---:|---:|---:|
| astro | adaptive | baseline | False | adaptive | True | 83.34 | 88.75 | 91.46 | 2591.38 |
| astro | classical | baseline | False | fusion | True | 83.34 | 88.75 | 91.46 | 73.61 |
| astro | classical | baseline | False | association | False | 83.37 | 88.75 | 91.46 | 73.62 |
| astro | classical | baseline | False | bm25 | False | 83.13 | 88.75 | 92.08 | 58.89 |
| astro | classical | baseline | False | topic | False | 83.22 | 88.75 | 91.46 | 77.06 |
| astro | embeddings | baseline | False | hybrid | True | 78.52 | 85.83 | 85.54 | 94.12 |
| astro | embeddings | baseline | False | lexical | False | 85.95 | 88.75 | 95.42 | 79.26 |
| astro | embeddings | baseline | False | vector | False | 53.34 | 68.75 | 55.19 | 16.30 |
| astro | ensemble | baseline | False | quality | True | 82.62 | 88.75 | 90.62 | 3738.00 |
| astro | ensemble | baseline | False | fast | False | 82.62 | 88.75 | 91.46 | 3620.47 |
| astro | ensemble | baseline | False | robust | False | 83.34 | 88.75 | 91.46 | 2687.86 |
| astro | entity-graph | baseline | False | fusion | True | 69.47 | 82.29 | 76.71 | 1035.23 |
| astro | entity-graph | baseline | False | entity | False | 68.01 | 87.29 | 68.86 | 1045.70 |
| astro | entity-graph | baseline | False | lexical | False | 72.62 | 82.50 | 82.04 | 1033.27 |
| astro | entity-graph | baseline | False | traversal | False | 32.30 | 50.42 | 30.31 | 1031.33 |
| astro | graphify | baseline | False | search | True | 57.79 | 77.29 | 57.92 | 140.27 |
| astro | legacy | baseline | False | lexical | True | 60.52 | 75.42 | 64.47 | 2.55 |
| astro | turso | baseline | False | lexical-sql | True | 47.81 | 66.67 | 49.17 | 138.51 |
