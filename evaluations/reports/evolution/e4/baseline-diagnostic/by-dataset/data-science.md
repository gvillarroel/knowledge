# Dataset: data-science

[General development comparison](../README.md) · [Cost, time and accuracy](../cta.md)

Development retrieval diagnostics; values are not independent validation or official benchmark scores. Primary routes use the predeclared family default. Qualification applies to the whole profile, including every failed cell.

| Dataset | Skill family | Profile | Qualified | Route | Primary | nDCG@10 | Recall@10 | MRR@10 | Query P95 ms |
|---|---|---|---|---|---|---:|---:|---:|---:|
| data-science | adaptive | baseline | False | adaptive | True | 91.78 | 99.17 | 93.23 | 2684.98 |
| data-science | classical | baseline | False | fusion | True | 80.54 | 78.54 | 91.25 | 1023.25 |
| data-science | classical | baseline | False | association | False | 80.54 | 78.54 | 91.25 | 911.11 |
| data-science | classical | baseline | False | bm25 | False | 93.08 | 98.33 | 94.06 | 888.20 |
| data-science | classical | baseline | False | topic | False | 80.54 | 78.54 | 91.25 | 880.22 |
| data-science | embeddings | baseline | False | hybrid | True | 60.04 | 88.96 | 52.00 | 803.66 |
| data-science | embeddings | baseline | False | lexical | False | 63.24 | 83.33 | 58.19 | 789.84 |
| data-science | embeddings | baseline | False | vector | False | 39.38 | 70.42 | 29.13 | 1.85 |
| data-science | ensemble | baseline | False | quality | True | 92.78 | 99.17 | 94.11 | 9928.14 |
| data-science | ensemble | baseline | False | fast | False | 94.44 | 99.17 | 96.75 | 8632.36 |
| data-science | ensemble | baseline | False | robust | False | 91.78 | 99.17 | 93.23 | 2161.94 |
| data-science | entity-graph | baseline | False | fusion | True | 85.79 | 97.50 | 86.88 | 6874.66 |
| data-science | entity-graph | baseline | False | entity | False | 80.82 | 96.67 | 79.67 | 7456.09 |
| data-science | entity-graph | baseline | False | lexical | False | 90.31 | 99.17 | 88.75 | 7199.18 |
| data-science | entity-graph | baseline | False | traversal | False | 51.20 | 79.58 | 43.55 | 7296.62 |
| data-science | graphify | baseline | False | search | True | 54.41 | 53.96 | 62.50 | 344.84 |
| data-science | legacy | baseline | False | lexical | True | 83.22 | 95.00 | 81.75 | 0.54 |
| data-science | turso | baseline | False | lexical-sql | True | 40.16 | 74.38 | 31.79 | 483.03 |
