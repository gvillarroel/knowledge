# Dataset: architecture

[General development comparison](../README.md) · [Cost, time and accuracy](../cta.md)

Development retrieval diagnostics; values are not independent validation or official benchmark scores. Primary routes use the predeclared family default. Qualification applies to the whole profile, including every failed cell.

| Dataset | Skill family | Profile | Qualified | Route | Primary | nDCG@10 | Recall@10 | MRR@10 | Query P95 ms |
|---|---|---|---|---|---|---:|---:|---:|---:|
| architecture | adaptive | baseline | False | adaptive | True | 85.61 | 95.21 | 90.50 | 1745.95 |
| architecture | classical | baseline | False | fusion | True | 92.58 | 97.29 | 97.50 | 729.62 |
| architecture | classical | baseline | False | association | False | 92.56 | 97.29 | 97.50 | 753.94 |
| architecture | classical | baseline | False | bm25 | False | 84.18 | 83.75 | 95.00 | 732.44 |
| architecture | classical | baseline | False | topic | False | 92.56 | 97.29 | 97.50 | 729.07 |
| architecture | embeddings | baseline | False | hybrid | True | 72.38 | 92.08 | 71.54 | 409.04 |
| architecture | embeddings | baseline | False | lexical | False | 72.13 | 92.92 | 71.57 | 380.24 |
| architecture | embeddings | baseline | False | vector | False | 65.56 | 84.38 | 65.99 | 1.05 |
| architecture | ensemble | baseline | False | quality | True | 85.01 | 95.21 | 88.00 | 5328.75 |
| architecture | ensemble | baseline | False | fast | False | 86.04 | 95.21 | 89.38 | 4500.35 |
| architecture | ensemble | baseline | False | robust | False | 85.61 | 95.21 | 90.50 | 1810.16 |
| architecture | entity-graph | baseline | False | fusion | True | 83.50 | 97.50 | 81.33 | 2931.74 |
| architecture | entity-graph | baseline | False | entity | False | 81.76 | 93.54 | 81.15 | 2883.36 |
| architecture | entity-graph | baseline | False | lexical | False | 88.98 | 98.33 | 89.25 | 2891.89 |
| architecture | entity-graph | baseline | False | traversal | False | 80.30 | 92.92 | 80.92 | 2902.55 |
| architecture | graphify | baseline | False | search | True | 57.76 | 59.58 | 68.75 | 93.54 |
| architecture | legacy | baseline | False | lexical | True | 81.55 | 95.00 | 80.62 | 0.22 |
| architecture | turso | baseline | False | lexical-sql | True | 58.40 | 86.25 | 52.72 | 352.11 |
