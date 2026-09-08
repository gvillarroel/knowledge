# Construction profile: baseline

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
