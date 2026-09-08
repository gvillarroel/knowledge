# Construction profile: g1-baseline

[General development comparison](../README.md) · [Cost, time and accuracy](../cta.md)

Development retrieval diagnostics; values are not independent validation or official benchmark scores. Primary routes use the predeclared family default. Qualification applies to the whole profile, including every failed cell.

| Dataset | Skill family | Profile | Qualified | Route | Primary | nDCG@10 | Recall@10 | MRR@10 | Query P95 ms |
|---|---|---|---|---|---|---:|---:|---:|---:|
| architecture | adaptive | g1-baseline | True | adaptive | True | 85.61 | 95.21 | 90.50 | 1773.58 |
| architecture | classical | g1-baseline | True | fusion | True | 92.58 | 97.29 | 97.50 | 863.38 |
| architecture | classical | g1-baseline | True | association | False | 92.56 | 97.29 | 97.50 | 805.26 |
| architecture | classical | g1-baseline | True | bm25 | False | 84.18 | 83.75 | 95.00 | 878.65 |
| architecture | classical | g1-baseline | True | topic | False | 92.56 | 97.29 | 97.50 | 790.50 |
| architecture | embeddings | g1-baseline | True | hybrid | True | 72.38 | 92.08 | 71.54 | 471.37 |
| architecture | embeddings | g1-baseline | True | lexical | False | 72.13 | 92.92 | 71.57 | 433.12 |
| architecture | embeddings | g1-baseline | True | vector | False | 65.56 | 84.38 | 65.99 | 1.45 |
| architecture | ensemble | g1-baseline | True | quality | True | 85.01 | 95.21 | 88.00 | 5771.96 |
| architecture | ensemble | g1-baseline | True | fast | False | 86.04 | 95.21 | 89.38 | 4665.88 |
| architecture | ensemble | g1-baseline | True | robust | False | 85.61 | 95.21 | 90.50 | 1927.56 |
| architecture | entity-graph | g1-baseline | True | fusion | True | 83.50 | 97.50 | 81.33 | 3983.92 |
| architecture | entity-graph | g1-baseline | True | entity | False | 81.76 | 93.54 | 81.15 | 4160.56 |
| architecture | entity-graph | g1-baseline | True | lexical | False | 88.98 | 98.33 | 89.25 | 3977.82 |
| architecture | entity-graph | g1-baseline | True | traversal | False | 80.30 | 92.92 | 80.92 | 3862.52 |
| architecture | graphify | g1-baseline | True | search | True | 57.76 | 59.58 | 68.75 | 141.26 |
| architecture | legacy | g1-baseline | True | lexical | True | 81.55 | 95.00 | 80.62 | 0.21 |
| architecture | turso | g1-baseline | True | lexical-sql | True | 58.40 | 86.25 | 52.72 | 435.64 |
| astro | adaptive | g1-baseline | True | adaptive | True | 83.34 | 88.75 | 91.46 | 2646.52 |
| astro | classical | g1-baseline | True | fusion | True | 83.34 | 88.75 | 91.46 | 112.86 |
| astro | classical | g1-baseline | True | association | False | 83.37 | 88.75 | 91.46 | 112.07 |
| astro | classical | g1-baseline | True | bm25 | False | 83.13 | 88.75 | 92.08 | 87.15 |
| astro | classical | g1-baseline | True | topic | False | 83.22 | 88.75 | 91.46 | 105.09 |
| astro | embeddings | g1-baseline | True | hybrid | True | 78.52 | 85.83 | 85.54 | 98.72 |
| astro | embeddings | g1-baseline | True | lexical | False | 85.95 | 88.75 | 95.42 | 78.69 |
| astro | embeddings | g1-baseline | True | vector | False | 53.34 | 68.75 | 55.19 | 16.26 |
| astro | ensemble | g1-baseline | True | quality | True | 82.62 | 88.75 | 90.62 | 4244.28 |
| astro | ensemble | g1-baseline | True | fast | False | 82.62 | 88.75 | 91.46 | 4566.46 |
| astro | ensemble | g1-baseline | True | robust | False | 83.34 | 88.75 | 91.46 | 2835.51 |
| astro | entity-graph | g1-baseline | True | fusion | True | 69.47 | 82.29 | 76.71 | 1156.22 |
| astro | entity-graph | g1-baseline | True | entity | False | 68.01 | 87.29 | 68.86 | 1072.47 |
| astro | entity-graph | g1-baseline | True | lexical | False | 72.62 | 82.50 | 82.04 | 1095.99 |
| astro | entity-graph | g1-baseline | True | traversal | False | 32.30 | 50.42 | 30.31 | 1106.09 |
| astro | graphify | g1-baseline | True | search | True | 57.79 | 77.29 | 57.92 | 161.81 |
| astro | legacy | g1-baseline | True | lexical | True | 60.52 | 75.42 | 64.47 | 2.34 |
| astro | turso | g1-baseline | True | lexical-sql | True | 47.81 | 66.67 | 49.17 | 148.76 |
| data-science | adaptive | g1-baseline | True | adaptive | True | 91.78 | 99.17 | 93.23 | 2657.43 |
| data-science | classical | g1-baseline | True | fusion | True | 80.54 | 78.54 | 91.25 | 896.22 |
| data-science | classical | g1-baseline | True | association | False | 80.54 | 78.54 | 91.25 | 871.36 |
| data-science | classical | g1-baseline | True | bm25 | False | 93.08 | 98.33 | 94.06 | 826.50 |
| data-science | classical | g1-baseline | True | topic | False | 80.54 | 78.54 | 91.25 | 830.77 |
| data-science | embeddings | g1-baseline | True | hybrid | True | 60.04 | 88.96 | 52.00 | 819.53 |
| data-science | embeddings | g1-baseline | True | lexical | False | 63.24 | 83.33 | 58.19 | 804.05 |
| data-science | embeddings | g1-baseline | True | vector | False | 39.38 | 70.42 | 29.13 | 2.16 |
| data-science | ensemble | g1-baseline | True | quality | True | 92.78 | 99.17 | 94.11 | 11719.63 |
| data-science | ensemble | g1-baseline | True | fast | False | 94.44 | 99.17 | 96.75 | 9004.43 |
| data-science | ensemble | g1-baseline | True | robust | False | 91.78 | 99.17 | 93.23 | 2784.58 |
| data-science | entity-graph | g1-baseline | True | fusion | True | 85.79 | 97.50 | 86.88 | 10400.85 |
| data-science | entity-graph | g1-baseline | True | entity | False | 80.82 | 96.67 | 79.67 | 7886.22 |
| data-science | entity-graph | g1-baseline | True | lexical | False | 90.31 | 99.17 | 88.75 | 7368.56 |
| data-science | entity-graph | g1-baseline | True | traversal | False | 51.20 | 79.58 | 43.55 | 7973.16 |
| data-science | graphify | g1-baseline | True | search | True | 54.41 | 53.96 | 62.50 | 330.53 |
| data-science | legacy | g1-baseline | True | lexical | True | 83.22 | 95.00 | 81.75 | 0.30 |
| data-science | turso | g1-baseline | True | lexical-sql | True | 40.16 | 74.38 | 31.79 | 557.75 |
| enterprise | adaptive | g1-baseline | True | adaptive | True | 50.34 | 59.00 | 57.47 | 1429.99 |
| enterprise | classical | g1-baseline | True | fusion | True | 43.42 | 42.46 | 56.25 | 68.22 |
| enterprise | classical | g1-baseline | True | association | False | 47.21 | 45.86 | 56.25 | 66.79 |
| enterprise | classical | g1-baseline | True | bm25 | False | 58.93 | 64.56 | 60.59 | 60.35 |
| enterprise | classical | g1-baseline | True | topic | False | 46.68 | 46.22 | 55.00 | 61.73 |
| enterprise | embeddings | g1-baseline | True | hybrid | True | 51.64 | 59.91 | 54.19 | 46.26 |
| enterprise | embeddings | g1-baseline | True | lexical | False | 59.07 | 61.86 | 61.50 | 10.08 |
| enterprise | embeddings | g1-baseline | True | vector | False | 32.56 | 36.92 | 37.72 | 37.61 |
| enterprise | ensemble | g1-baseline | True | quality | True | 55.35 | 59.00 | 60.36 | 1842.68 |
| enterprise | ensemble | g1-baseline | True | fast | False | 52.32 | 59.00 | 59.07 | 1858.99 |
| enterprise | ensemble | g1-baseline | True | robust | False | 50.34 | 59.00 | 57.47 | 1612.29 |
| enterprise | entity-graph | g1-baseline | True | fusion | True | 46.73 | 58.04 | 47.33 | 63.57 |
| enterprise | entity-graph | g1-baseline | True | entity | False | 45.25 | 56.58 | 46.67 | 71.77 |
| enterprise | entity-graph | g1-baseline | True | lexical | False | 59.40 | 63.73 | 60.78 | 73.38 |
| enterprise | entity-graph | g1-baseline | True | traversal | False | 43.27 | 50.33 | 46.04 | 69.97 |
| enterprise | graphify | g1-baseline | True | search | True | 13.63 | 17.37 | 20.42 | 131.64 |
| enterprise | legacy | g1-baseline | True | lexical | True | 57.50 | 61.92 | 59.86 | 4.33 |
| enterprise | turso | g1-baseline | True | lexical-sql | True | 40.32 | 49.87 | 40.85 | 56.23 |
