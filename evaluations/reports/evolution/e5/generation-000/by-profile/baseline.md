# Construction profile: baseline

[General development comparison](../README.md) · [Cost, time and accuracy](../cta.md)

Development retrieval diagnostics; values are not independent validation or official benchmark scores. Primary routes use the predeclared family default. Qualification applies to the whole profile, including every failed cell.

| Dataset | Skill family | Profile | Qualified | Route | Primary | nDCG@10 | Recall@10 | MRR@10 | Query P95 ms |
|---|---|---|---|---|---|---:|---:|---:|---:|
| architecture | adaptive | baseline | True | adaptive | True | 85.61 | 95.21 | 90.50 | 2008.03 |
| architecture | classical | baseline | True | fusion | True | 92.58 | 97.29 | 97.50 | 1491.18 |
| architecture | classical | baseline | True | association | False | 92.56 | 97.29 | 97.50 | 2179.70 |
| architecture | classical | baseline | True | bm25 | False | 84.18 | 83.75 | 95.00 | 861.65 |
| architecture | classical | baseline | True | topic | False | 92.56 | 97.29 | 97.50 | 1933.61 |
| architecture | embeddings | baseline | True | hybrid | True | 72.38 | 92.08 | 71.54 | 411.20 |
| architecture | embeddings | baseline | True | lexical | False | 72.13 | 92.92 | 71.57 | 418.70 |
| architecture | embeddings | baseline | True | vector | False | 65.56 | 84.38 | 65.99 | 1.19 |
| architecture | ensemble | baseline | True | quality | True | 85.01 | 95.21 | 88.00 | 5763.66 |
| architecture | ensemble | baseline | True | fast | False | 86.04 | 95.21 | 89.38 | 4797.89 |
| architecture | ensemble | baseline | True | robust | False | 85.61 | 95.21 | 90.50 | 1905.55 |
| architecture | entity-graph | baseline | True | fusion | True | 83.50 | 97.50 | 81.33 | 4298.90 |
| architecture | entity-graph | baseline | True | entity | False | 81.76 | 93.54 | 81.15 | 3056.22 |
| architecture | entity-graph | baseline | True | lexical | False | 88.98 | 98.33 | 89.25 | 3194.62 |
| architecture | entity-graph | baseline | True | traversal | False | 80.30 | 92.92 | 80.92 | 3588.57 |
| architecture | graphify | baseline | True | search | True | 57.76 | 59.58 | 68.75 | 120.86 |
| architecture | legacy | baseline | True | lexical | True | 81.55 | 95.00 | 80.62 | 0.32 |
| architecture | turso | baseline | True | lexical-sql | True | 58.40 | 86.25 | 52.72 | 355.76 |
| astro | adaptive | baseline | True | adaptive | True | 83.34 | 88.75 | 91.46 | 3213.63 |
| astro | classical | baseline | True | fusion | True | 83.34 | 88.75 | 91.46 | 86.18 |
| astro | classical | baseline | True | association | False | 83.37 | 88.75 | 91.46 | 83.13 |
| astro | classical | baseline | True | bm25 | False | 83.13 | 88.75 | 92.08 | 66.46 |
| astro | classical | baseline | True | topic | False | 83.22 | 88.75 | 91.46 | 84.27 |
| astro | embeddings | baseline | True | hybrid | True | 78.52 | 85.83 | 85.54 | 99.41 |
| astro | embeddings | baseline | True | lexical | False | 85.95 | 88.75 | 95.42 | 84.04 |
| astro | embeddings | baseline | True | vector | False | 53.34 | 68.75 | 55.19 | 17.28 |
| astro | ensemble | baseline | True | quality | True | 82.62 | 88.75 | 90.62 | 5785.08 |
| astro | ensemble | baseline | True | fast | False | 82.62 | 88.75 | 91.46 | 4219.04 |
| astro | ensemble | baseline | True | robust | False | 83.34 | 88.75 | 91.46 | 3051.60 |
| astro | entity-graph | baseline | True | fusion | True | 69.47 | 82.29 | 76.71 | 1306.59 |
| astro | entity-graph | baseline | True | entity | False | 68.01 | 87.29 | 68.86 | 1222.59 |
| astro | entity-graph | baseline | True | lexical | False | 72.62 | 82.50 | 82.04 | 1218.73 |
| astro | entity-graph | baseline | True | traversal | False | 32.30 | 50.42 | 30.31 | 1159.26 |
| astro | graphify | baseline | True | search | True | 57.79 | 77.29 | 57.92 | 146.34 |
| astro | legacy | baseline | True | lexical | True | 60.52 | 75.42 | 64.47 | 2.63 |
| astro | turso | baseline | True | lexical-sql | True | 47.81 | 66.67 | 49.17 | 142.15 |
| data-science | adaptive | baseline | True | adaptive | True | 91.78 | 99.17 | 93.23 | 2932.49 |
| data-science | classical | baseline | True | fusion | True | 80.54 | 78.54 | 91.25 | 987.14 |
| data-science | classical | baseline | True | association | False | 80.54 | 78.54 | 91.25 | 1143.88 |
| data-science | classical | baseline | True | bm25 | False | 93.08 | 98.33 | 94.06 | 1094.24 |
| data-science | classical | baseline | True | topic | False | 80.54 | 78.54 | 91.25 | 1119.91 |
| data-science | embeddings | baseline | True | hybrid | True | 60.04 | 88.96 | 52.00 | 923.95 |
| data-science | embeddings | baseline | True | lexical | False | 63.24 | 83.33 | 58.19 | 959.14 |
| data-science | embeddings | baseline | True | vector | False | 39.38 | 70.42 | 29.13 | 2.36 |
| data-science | ensemble | baseline | True | quality | True | 92.78 | 99.17 | 94.11 | 11908.41 |
| data-science | ensemble | baseline | True | fast | False | 94.44 | 99.17 | 96.75 | 10589.14 |
| data-science | ensemble | baseline | True | robust | False | 91.78 | 99.17 | 93.23 | 2611.21 |
| data-science | entity-graph | baseline | True | fusion | True | 85.79 | 97.50 | 86.88 | 8414.53 |
| data-science | entity-graph | baseline | True | entity | False | 80.82 | 96.67 | 79.67 | 9290.45 |
| data-science | entity-graph | baseline | True | lexical | False | 90.31 | 99.17 | 88.75 | 8373.27 |
| data-science | entity-graph | baseline | True | traversal | False | 51.20 | 79.58 | 43.55 | 8172.18 |
| data-science | graphify | baseline | True | search | True | 54.41 | 53.96 | 62.50 | 329.09 |
| data-science | legacy | baseline | True | lexical | True | 83.22 | 95.00 | 81.75 | 0.46 |
| data-science | turso | baseline | True | lexical-sql | True | 40.16 | 74.38 | 31.79 | 621.73 |
| enterprise | adaptive | baseline | True | adaptive | True | 50.34 | 59.00 | 57.47 | 1552.58 |
| enterprise | classical | baseline | True | fusion | True | 43.42 | 42.46 | 56.25 | 44.55 |
| enterprise | classical | baseline | True | association | False | 47.21 | 45.86 | 56.25 | 45.29 |
| enterprise | classical | baseline | True | bm25 | False | 58.93 | 64.56 | 60.59 | 43.27 |
| enterprise | classical | baseline | True | topic | False | 46.68 | 46.22 | 55.00 | 43.64 |
| enterprise | embeddings | baseline | True | hybrid | True | 51.64 | 59.91 | 54.19 | 47.76 |
| enterprise | embeddings | baseline | True | lexical | False | 59.07 | 61.86 | 61.50 | 9.79 |
| enterprise | embeddings | baseline | True | vector | False | 32.56 | 36.92 | 37.72 | 36.21 |
| enterprise | ensemble | baseline | True | quality | True | 55.35 | 59.00 | 60.36 | 1736.95 |
| enterprise | ensemble | baseline | True | fast | False | 52.32 | 59.00 | 59.07 | 1613.61 |
| enterprise | ensemble | baseline | True | robust | False | 50.34 | 59.00 | 57.47 | 2068.93 |
| enterprise | entity-graph | baseline | True | fusion | True | 46.73 | 58.04 | 47.33 | 91.83 |
| enterprise | entity-graph | baseline | True | entity | False | 45.25 | 56.58 | 46.67 | 108.48 |
| enterprise | entity-graph | baseline | True | lexical | False | 59.40 | 63.73 | 60.78 | 79.86 |
| enterprise | entity-graph | baseline | True | traversal | False | 43.27 | 50.33 | 46.04 | 106.62 |
| enterprise | graphify | baseline | True | search | True | 13.63 | 17.37 | 20.42 | 136.96 |
| enterprise | legacy | baseline | True | lexical | True | 57.50 | 61.92 | 59.86 | 3.50 |
| enterprise | turso | baseline | True | lexical-sql | True | 40.32 | 49.87 | 40.85 | 63.72 |
