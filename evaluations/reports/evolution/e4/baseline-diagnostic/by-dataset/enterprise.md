# Dataset: enterprise

[General development comparison](../README.md) · [Cost, time and accuracy](../cta.md)

Development retrieval diagnostics; values are not independent validation or official benchmark scores. Primary routes use the predeclared family default. Qualification applies to the whole profile, including every failed cell.

| Dataset | Skill family | Profile | Qualified | Route | Primary | nDCG@10 | Recall@10 | MRR@10 | Query P95 ms |
|---|---|---|---|---|---|---:|---:|---:|---:|
| enterprise | adaptive | baseline | False | adaptive | True | 50.34 | 59.00 | 57.47 | 1344.75 |
| enterprise | classical | baseline | False | fusion | True | 43.42 | 42.46 | 56.25 | 41.38 |
| enterprise | classical | baseline | False | association | False | 47.21 | 45.86 | 56.25 | 42.93 |
| enterprise | classical | baseline | False | bm25 | False | 58.93 | 64.56 | 60.59 | 41.24 |
| enterprise | classical | baseline | False | topic | False | 46.68 | 46.22 | 55.00 | 41.92 |
| enterprise | embeddings | baseline | False | hybrid | True | 51.64 | 59.91 | 54.19 | 46.07 |
| enterprise | embeddings | baseline | False | lexical | False | 59.07 | 61.86 | 61.50 | 9.72 |
| enterprise | embeddings | baseline | False | vector | False | 32.56 | 36.92 | 37.72 | 33.94 |
| enterprise | ensemble | baseline | False | quality | True | 55.35 | 59.00 | 60.36 | 1508.28 |
| enterprise | ensemble | baseline | False | fast | False | 52.32 | 59.00 | 59.07 | 1352.88 |
| enterprise | ensemble | baseline | False | robust | False | 50.34 | 59.00 | 57.47 | 1312.92 |
| enterprise | entity-graph | baseline | False | fusion | True | 46.73 | 58.04 | 47.33 | 49.85 |
| enterprise | entity-graph | baseline | False | entity | False | 45.25 | 56.58 | 46.67 | 55.74 |
| enterprise | entity-graph | baseline | False | lexical | False | 59.40 | 63.73 | 60.78 | 52.40 |
| enterprise | entity-graph | baseline | False | traversal | False | 43.27 | 50.33 | 46.04 | 64.66 |
| enterprise | graphify | baseline | False | search | True | 13.63 | 17.37 | 20.42 | 130.67 |
| enterprise | legacy | baseline | False | lexical | True | 57.50 | 61.92 | 59.86 | 3.26 |
| enterprise | turso | baseline | False | lexical-sql | True | 40.32 | 49.87 | 40.85 | 37.86 |
