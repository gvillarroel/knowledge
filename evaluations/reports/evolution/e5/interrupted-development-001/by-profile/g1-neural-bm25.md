# Construction profile: g1-neural-bm25

[General development comparison](../README.md) · [Cost, time and accuracy](../cta.md)

Development retrieval diagnostics; values are not independent validation or official benchmark scores. Primary routes use the predeclared family default. Qualification applies to the whole profile, including every failed cell.

| Dataset | Skill family | Profile | Qualified | Route | Primary | nDCG@10 | Recall@10 | MRR@10 | Query P95 ms |
|---|---|---|---|---|---|---:|---:|---:|---:|
| architecture | adaptive | g1-neural-bm25 | True | adaptive | True | 85.80 | 96.04 | 90.50 | 1751.59 |
| architecture | classical | g1-neural-bm25 | True | fusion | True | 89.83 | 96.46 | 92.92 | 717.54 |
| architecture | classical | g1-neural-bm25 | True | association | False | 89.93 | 96.46 | 93.33 | 692.29 |
| architecture | classical | g1-neural-bm25 | True | bm25 | False | 80.11 | 80.21 | 91.46 | 702.64 |
| architecture | classical | g1-neural-bm25 | True | topic | False | 89.91 | 96.46 | 93.33 | 716.28 |
| architecture | embeddings | g1-neural-bm25 | True | hybrid | True | 77.08 | 93.54 | 78.82 | 550.15 |
| architecture | embeddings | g1-neural-bm25 | True | lexical | False | 72.13 | 92.92 | 71.57 | 403.27 |
| architecture | embeddings | g1-neural-bm25 | True | vector | False | 75.73 | 91.25 | 77.65 | 136.94 |
| architecture | ensemble | g1-neural-bm25 | True | quality | True | 85.12 | 96.04 | 88.00 | 5540.54 |
| architecture | ensemble | g1-neural-bm25 | True | fast | False | 86.76 | 96.04 | 90.92 | 4266.62 |
| architecture | ensemble | g1-neural-bm25 | True | robust | False | 85.80 | 96.04 | 90.50 | 1788.08 |
| architecture | entity-graph | g1-neural-bm25 | True | fusion | True | 83.42 | 97.50 | 81.25 | 2793.08 |
| architecture | entity-graph | g1-neural-bm25 | True | entity | False | 81.76 | 93.54 | 81.15 | 2802.02 |
| architecture | entity-graph | g1-neural-bm25 | True | lexical | False | 87.93 | 97.71 | 88.50 | 2795.65 |
| architecture | entity-graph | g1-neural-bm25 | True | traversal | False | 80.30 | 92.92 | 80.92 | 2812.17 |
| architecture | graphify | g1-neural-bm25 | True | search | True | 57.76 | 59.58 | 68.75 | 95.57 |
| architecture | legacy | g1-neural-bm25 | True | lexical | True | 81.55 | 95.00 | 80.62 | 0.20 |
| architecture | turso | g1-neural-bm25 | True | lexical-sql | True | 58.40 | 86.25 | 52.72 | 346.25 |
| astro | adaptive | g1-neural-bm25 | True | adaptive | True | 77.74 | 87.08 | 83.90 | 2663.42 |
| astro | classical | g1-neural-bm25 | True | fusion | True | 77.74 | 87.08 | 83.90 | 73.74 |
| astro | classical | g1-neural-bm25 | True | association | False | 78.31 | 87.92 | 84.11 | 73.05 |
| astro | classical | g1-neural-bm25 | True | bm25 | False | 78.63 | 87.08 | 84.77 | 63.19 |
| astro | classical | g1-neural-bm25 | True | topic | False | 77.78 | 87.08 | 84.08 | 76.33 |
| astro | embeddings | g1-neural-bm25 | True | hybrid | True | 74.34 | 91.04 | 73.62 | 234.65 |
| astro | embeddings | g1-neural-bm25 | True | lexical | False | 85.95 | 88.75 | 95.42 | 81.30 |
| astro | embeddings | g1-neural-bm25 | True | vector | False | 50.65 | 67.71 | 51.92 | 156.29 |
| astro | ensemble | g1-neural-bm25 | True | quality | True | 77.66 | 87.08 | 85.10 | 4023.64 |
| astro | ensemble | g1-neural-bm25 | True | fast | False | 77.93 | 87.08 | 85.49 | 3655.15 |
| astro | ensemble | g1-neural-bm25 | True | robust | False | 77.74 | 87.08 | 83.90 | 2809.49 |
| astro | entity-graph | g1-neural-bm25 | True | fusion | True | 66.67 | 82.29 | 71.65 | 1041.03 |
| astro | entity-graph | g1-neural-bm25 | True | entity | False | 68.01 | 87.29 | 68.86 | 1062.53 |
| astro | entity-graph | g1-neural-bm25 | True | lexical | False | 75.63 | 84.17 | 83.12 | 1047.01 |
| astro | entity-graph | g1-neural-bm25 | True | traversal | False | 32.30 | 50.42 | 30.31 | 1036.10 |
| astro | graphify | g1-neural-bm25 | True | search | True | 57.79 | 77.29 | 57.92 | 141.70 |
| astro | legacy | g1-neural-bm25 | True | lexical | True | 60.52 | 75.42 | 64.47 | 2.69 |
| astro | turso | g1-neural-bm25 | True | lexical-sql | True | 47.81 | 66.67 | 49.17 | 137.96 |
| data-science | adaptive | g1-neural-bm25 | True | adaptive | True | 91.97 | 99.17 | 93.19 | 2609.86 |
| data-science | classical | g1-neural-bm25 | True | fusion | True | 80.54 | 78.54 | 91.25 | 881.23 |
| data-science | classical | g1-neural-bm25 | True | association | False | 80.54 | 78.54 | 91.25 | 872.33 |
| data-science | classical | g1-neural-bm25 | True | bm25 | False | 93.33 | 98.33 | 94.03 | 827.75 |
| data-science | classical | g1-neural-bm25 | True | topic | False | 80.54 | 78.54 | 91.25 | 795.72 |
| data-science | embeddings | g1-neural-bm25 | True | hybrid | True | 87.89 | 97.50 | 88.34 | 932.13 |
| data-science | embeddings | g1-neural-bm25 | True | lexical | False | 63.24 | 83.33 | 58.19 | 758.19 |
| data-science | embeddings | g1-neural-bm25 | True | vector | False | 87.92 | 97.50 | 87.38 | 134.28 |
| data-science | ensemble | g1-neural-bm25 | True | quality | True | 93.90 | 99.17 | 94.11 | 10465.37 |
| data-science | ensemble | g1-neural-bm25 | True | fast | False | 93.98 | 99.17 | 95.50 | 8940.53 |
| data-science | ensemble | g1-neural-bm25 | True | robust | False | 91.97 | 99.17 | 93.19 | 2152.08 |
| data-science | entity-graph | g1-neural-bm25 | True | fusion | True | 80.74 | 97.50 | 78.36 | 7109.58 |
| data-science | entity-graph | g1-neural-bm25 | True | entity | False | 80.82 | 96.67 | 79.67 | 7494.57 |
| data-science | entity-graph | g1-neural-bm25 | True | lexical | False | 89.22 | 98.33 | 88.96 | 7349.24 |
| data-science | entity-graph | g1-neural-bm25 | True | traversal | False | 51.20 | 79.58 | 43.55 | 7008.90 |
| data-science | graphify | g1-neural-bm25 | True | search | True | 54.41 | 53.96 | 62.50 | 322.34 |
| data-science | legacy | g1-neural-bm25 | True | lexical | True | 83.22 | 95.00 | 81.75 | 0.49 |
| data-science | turso | g1-neural-bm25 | True | lexical-sql | True | 40.16 | 74.38 | 31.79 | 480.54 |
| enterprise | adaptive | g1-neural-bm25 | True | adaptive | True | 50.69 | 59.07 | 57.51 | 1332.68 |
| enterprise | classical | g1-neural-bm25 | True | fusion | True | 44.25 | 43.99 | 56.25 | 41.50 |
| enterprise | classical | g1-neural-bm25 | True | association | False | 47.29 | 45.86 | 56.25 | 43.23 |
| enterprise | classical | g1-neural-bm25 | True | bm25 | False | 58.95 | 64.98 | 60.67 | 38.96 |
| enterprise | classical | g1-neural-bm25 | True | topic | False | 47.80 | 46.22 | 56.25 | 41.40 |
| enterprise | embeddings | g1-neural-bm25 | True | hybrid | True | 63.19 | 68.38 | 64.38 | 184.38 |
| enterprise | embeddings | g1-neural-bm25 | True | lexical | False | 59.07 | 61.86 | 61.50 | 10.03 |
| enterprise | embeddings | g1-neural-bm25 | True | vector | False | 60.70 | 68.94 | 60.82 | 195.29 |
| enterprise | ensemble | g1-neural-bm25 | True | quality | True | 54.08 | 59.07 | 57.86 | 1665.09 |
| enterprise | ensemble | g1-neural-bm25 | True | fast | False | 51.68 | 59.07 | 57.73 | 1383.86 |
| enterprise | ensemble | g1-neural-bm25 | True | robust | False | 50.69 | 59.07 | 57.51 | 1341.56 |
| enterprise | entity-graph | g1-neural-bm25 | True | fusion | True | 47.28 | 58.31 | 47.51 | 51.87 |
| enterprise | entity-graph | g1-neural-bm25 | True | entity | False | 45.25 | 56.58 | 46.67 | 52.08 |
| enterprise | entity-graph | g1-neural-bm25 | True | lexical | False | 58.33 | 63.73 | 59.06 | 53.72 |
| enterprise | entity-graph | g1-neural-bm25 | True | traversal | False | 43.27 | 50.33 | 46.04 | 53.61 |
| enterprise | graphify | g1-neural-bm25 | True | search | True | 13.63 | 17.37 | 20.42 | 133.02 |
| enterprise | legacy | g1-neural-bm25 | True | lexical | True | 57.50 | 61.92 | 59.86 | 3.41 |
| enterprise | turso | g1-neural-bm25 | True | lexical-sql | True | 40.32 | 49.87 | 40.85 | 39.07 |
