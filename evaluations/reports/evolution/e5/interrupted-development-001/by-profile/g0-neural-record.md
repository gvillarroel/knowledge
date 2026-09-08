# Construction profile: g0-neural-record

[General development comparison](../README.md) · [Cost, time and accuracy](../cta.md)

Development retrieval diagnostics; values are not independent validation or official benchmark scores. Primary routes use the predeclared family default. Qualification applies to the whole profile, including every failed cell.

| Dataset | Skill family | Profile | Qualified | Route | Primary | nDCG@10 | Recall@10 | MRR@10 | Query P95 ms |
|---|---|---|---|---|---|---:|---:|---:|---:|
| architecture | adaptive | g0-neural-record | True | adaptive | True | 85.61 | 95.21 | 90.50 | 2094.72 |
| architecture | classical | g0-neural-record | True | fusion | True | 92.58 | 97.29 | 97.50 | 1034.71 |
| architecture | classical | g0-neural-record | True | association | False | 92.56 | 97.29 | 97.50 | 1052.38 |
| architecture | classical | g0-neural-record | True | bm25 | False | 84.18 | 83.75 | 95.00 | 888.83 |
| architecture | classical | g0-neural-record | True | topic | False | 92.56 | 97.29 | 97.50 | 916.16 |
| architecture | embeddings | g0-neural-record | True | hybrid | True | 77.08 | 93.54 | 78.82 | 597.31 |
| architecture | embeddings | g0-neural-record | True | lexical | False | 72.13 | 92.92 | 71.57 | 445.03 |
| architecture | embeddings | g0-neural-record | True | vector | False | 75.73 | 91.25 | 77.65 | 668.06 |
| architecture | ensemble | g0-neural-record | True | quality | True | 84.04 | 95.21 | 86.75 | 5578.47 |
| architecture | ensemble | g0-neural-record | True | fast | False | 86.04 | 95.21 | 89.38 | 4696.71 |
| architecture | ensemble | g0-neural-record | True | robust | False | 85.61 | 95.21 | 90.50 | 1869.50 |
| architecture | entity-graph | g0-neural-record | True | fusion | True | 83.50 | 97.50 | 81.33 | 3051.84 |
| architecture | entity-graph | g0-neural-record | True | entity | False | 81.76 | 93.54 | 81.15 | 3145.99 |
| architecture | entity-graph | g0-neural-record | True | lexical | False | 88.98 | 98.33 | 89.25 | 2995.67 |
| architecture | entity-graph | g0-neural-record | True | traversal | False | 80.30 | 92.92 | 80.92 | 2989.88 |
| architecture | graphify | g0-neural-record | True | search | True | 57.76 | 59.58 | 68.75 | 98.64 |
| architecture | legacy | g0-neural-record | True | lexical | True | 81.55 | 95.00 | 80.62 | 0.20 |
| architecture | turso | g0-neural-record | True | lexical-sql | True | 58.40 | 86.25 | 52.72 | 348.73 |
| astro | adaptive | g0-neural-record | True | adaptive | True | 83.34 | 88.75 | 91.46 | 2741.02 |
| astro | classical | g0-neural-record | True | fusion | True | 83.34 | 88.75 | 91.46 | 89.67 |
| astro | classical | g0-neural-record | True | association | False | 83.37 | 88.75 | 91.46 | 79.10 |
| astro | classical | g0-neural-record | True | bm25 | False | 83.13 | 88.75 | 92.08 | 62.08 |
| astro | classical | g0-neural-record | True | topic | False | 83.22 | 88.75 | 91.46 | 84.83 |
| astro | embeddings | g0-neural-record | True | hybrid | True | 74.34 | 91.04 | 73.62 | 244.34 |
| astro | embeddings | g0-neural-record | True | lexical | False | 85.95 | 88.75 | 95.42 | 84.24 |
| astro | embeddings | g0-neural-record | True | vector | False | 50.65 | 67.71 | 51.92 | 166.95 |
| astro | ensemble | g0-neural-record | True | quality | True | 82.46 | 88.75 | 90.62 | 4210.70 |
| astro | ensemble | g0-neural-record | True | fast | False | 82.62 | 88.75 | 91.46 | 3691.36 |
| astro | ensemble | g0-neural-record | True | robust | False | 83.34 | 88.75 | 91.46 | 2759.03 |
| astro | entity-graph | g0-neural-record | True | fusion | True | 69.47 | 82.29 | 76.71 | 1199.38 |
| astro | entity-graph | g0-neural-record | True | entity | False | 68.01 | 87.29 | 68.86 | 1082.86 |
| astro | entity-graph | g0-neural-record | True | lexical | False | 72.62 | 82.50 | 82.04 | 1109.84 |
| astro | entity-graph | g0-neural-record | True | traversal | False | 32.30 | 50.42 | 30.31 | 1086.75 |
| astro | graphify | g0-neural-record | True | search | True | 57.79 | 77.29 | 57.92 | 145.63 |
| astro | legacy | g0-neural-record | True | lexical | True | 60.52 | 75.42 | 64.47 | 2.83 |
| astro | turso | g0-neural-record | True | lexical-sql | True | 47.81 | 66.67 | 49.17 | 144.80 |
| data-science | adaptive | g0-neural-record | True | adaptive | True | 91.78 | 99.17 | 93.23 | 2649.52 |
| data-science | classical | g0-neural-record | True | fusion | True | 80.54 | 78.54 | 91.25 | 961.80 |
| data-science | classical | g0-neural-record | True | association | False | 80.54 | 78.54 | 91.25 | 949.53 |
| data-science | classical | g0-neural-record | True | bm25 | False | 93.08 | 98.33 | 94.06 | 910.91 |
| data-science | classical | g0-neural-record | True | topic | False | 80.54 | 78.54 | 91.25 | 942.22 |
| data-science | embeddings | g0-neural-record | True | hybrid | True | 87.89 | 97.50 | 88.34 | 1092.20 |
| data-science | embeddings | g0-neural-record | True | lexical | False | 63.24 | 83.33 | 58.19 | 969.29 |
| data-science | embeddings | g0-neural-record | True | vector | False | 87.92 | 97.50 | 87.38 | 148.86 |
| data-science | ensemble | g0-neural-record | True | quality | True | 92.87 | 99.17 | 94.11 | 13592.51 |
| data-science | ensemble | g0-neural-record | True | fast | False | 94.44 | 99.17 | 96.75 | 10205.32 |
| data-science | ensemble | g0-neural-record | True | robust | False | 91.78 | 99.17 | 93.23 | 2499.86 |
| data-science | entity-graph | g0-neural-record | True | fusion | True | 85.79 | 97.50 | 86.88 | 7766.54 |
| data-science | entity-graph | g0-neural-record | True | entity | False | 80.82 | 96.67 | 79.67 | 7681.21 |
| data-science | entity-graph | g0-neural-record | True | lexical | False | 90.31 | 99.17 | 88.75 | 7450.80 |
| data-science | entity-graph | g0-neural-record | True | traversal | False | 51.20 | 79.58 | 43.55 | 7313.86 |
| data-science | graphify | g0-neural-record | True | search | True | 54.41 | 53.96 | 62.50 | 328.74 |
| data-science | legacy | g0-neural-record | True | lexical | True | 83.22 | 95.00 | 81.75 | 0.43 |
| data-science | turso | g0-neural-record | True | lexical-sql | True | 40.16 | 74.38 | 31.79 | 497.96 |
| enterprise | adaptive | g0-neural-record | True | adaptive | True | 50.34 | 59.00 | 57.47 | 1427.76 |
| enterprise | classical | g0-neural-record | True | fusion | True | 43.42 | 42.46 | 56.25 | 45.92 |
| enterprise | classical | g0-neural-record | True | association | False | 47.21 | 45.86 | 56.25 | 45.64 |
| enterprise | classical | g0-neural-record | True | bm25 | False | 58.93 | 64.56 | 60.59 | 41.72 |
| enterprise | classical | g0-neural-record | True | topic | False | 46.68 | 46.22 | 55.00 | 44.69 |
| enterprise | embeddings | g0-neural-record | True | hybrid | True | 63.19 | 68.38 | 64.38 | 194.53 |
| enterprise | embeddings | g0-neural-record | True | lexical | False | 59.07 | 61.86 | 61.50 | 9.77 |
| enterprise | embeddings | g0-neural-record | True | vector | False | 60.70 | 68.94 | 60.82 | 188.18 |
| enterprise | ensemble | g0-neural-record | True | quality | True | 55.61 | 59.00 | 60.36 | 1784.70 |
| enterprise | ensemble | g0-neural-record | True | fast | False | 52.32 | 59.00 | 59.07 | 1560.58 |
| enterprise | ensemble | g0-neural-record | True | robust | False | 50.34 | 59.00 | 57.47 | 1590.84 |
| enterprise | entity-graph | g0-neural-record | True | fusion | True | 46.73 | 58.04 | 47.33 | 56.53 |
| enterprise | entity-graph | g0-neural-record | True | entity | False | 45.25 | 56.58 | 46.67 | 54.25 |
| enterprise | entity-graph | g0-neural-record | True | lexical | False | 59.40 | 63.73 | 60.78 | 69.79 |
| enterprise | entity-graph | g0-neural-record | True | traversal | False | 43.27 | 50.33 | 46.04 | 58.54 |
| enterprise | graphify | g0-neural-record | True | search | True | 13.63 | 17.37 | 20.42 | 138.01 |
| enterprise | legacy | g0-neural-record | True | lexical | True | 57.50 | 61.92 | 59.86 | 3.32 |
| enterprise | turso | g0-neural-record | True | lexical-sql | True | 40.32 | 49.87 | 40.85 | 40.54 |
