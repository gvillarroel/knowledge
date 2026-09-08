# Construction profile: quarter-expansion

[General development comparison](../README.md) · [Cost, time and accuracy](../cta.md)

Development retrieval diagnostics; values are not independent validation or official benchmark scores. Primary routes use the predeclared family default. Qualification applies to the whole profile, including every failed cell.

| Dataset | Skill family | Profile | Qualified | Route | Primary | nDCG@10 | Recall@10 | MRR@10 | Query P95 ms |
|---|---|---|---|---|---|---:|---:|---:|---:|
| architecture | adaptive | quarter-expansion | True | adaptive | True | 85.18 | 95.21 | 89.19 | 1684.88 |
| architecture | classical | quarter-expansion | True | fusion | True | 91.72 | 97.29 | 95.00 | 959.85 |
| architecture | classical | quarter-expansion | True | association | False | 91.72 | 97.29 | 95.00 | 926.73 |
| architecture | classical | quarter-expansion | True | bm25 | False | 84.18 | 83.75 | 95.00 | 992.94 |
| architecture | classical | quarter-expansion | True | topic | False | 91.72 | 97.29 | 95.00 | 833.42 |
| architecture | embeddings | quarter-expansion | True | hybrid | True | 72.38 | 92.08 | 71.54 | 685.21 |
| architecture | embeddings | quarter-expansion | True | lexical | False | 72.13 | 92.92 | 71.57 | 623.78 |
| architecture | embeddings | quarter-expansion | True | vector | False | 65.56 | 84.38 | 65.99 | 1.87 |
| architecture | ensemble | quarter-expansion | True | quality | True | 84.95 | 95.21 | 87.94 | 11204.95 |
| architecture | ensemble | quarter-expansion | True | fast | False | 86.08 | 95.21 | 90.62 | 4737.18 |
| architecture | ensemble | quarter-expansion | True | robust | False | 85.18 | 95.21 | 89.19 | 1716.46 |
| architecture | entity-graph | quarter-expansion | True | fusion | True | 83.50 | 97.50 | 81.33 | 5589.32 |
| architecture | entity-graph | quarter-expansion | True | entity | False | 81.76 | 93.54 | 81.15 | 3360.44 |
| architecture | entity-graph | quarter-expansion | True | lexical | False | 88.98 | 98.33 | 89.25 | 5744.78 |
| architecture | entity-graph | quarter-expansion | True | traversal | False | 80.30 | 92.92 | 80.92 | 3178.78 |
| architecture | graphify | quarter-expansion | True | search | True | 57.76 | 59.58 | 68.75 | 102.75 |
| architecture | legacy | quarter-expansion | True | lexical | True | 81.55 | 95.00 | 80.62 | 0.19 |
| architecture | turso | quarter-expansion | True | lexical-sql | True | 58.40 | 86.25 | 52.72 | 416.33 |
| astro | adaptive | quarter-expansion | True | adaptive | True | 83.27 | 88.75 | 92.08 | 2647.68 |
| astro | classical | quarter-expansion | True | fusion | True | 83.27 | 88.75 | 92.08 | 82.33 |
| astro | classical | quarter-expansion | True | association | False | 83.27 | 88.75 | 92.08 | 80.16 |
| astro | classical | quarter-expansion | True | bm25 | False | 83.13 | 88.75 | 92.08 | 81.02 |
| astro | classical | quarter-expansion | True | topic | False | 83.29 | 88.75 | 92.08 | 98.53 |
| astro | embeddings | quarter-expansion | True | hybrid | True | 78.52 | 85.83 | 85.54 | 109.11 |
| astro | embeddings | quarter-expansion | True | lexical | False | 85.95 | 88.75 | 95.42 | 83.82 |
| astro | embeddings | quarter-expansion | True | vector | False | 53.34 | 68.75 | 55.19 | 19.18 |
| astro | ensemble | quarter-expansion | True | quality | True | 81.28 | 88.75 | 88.75 | 5624.87 |
| astro | ensemble | quarter-expansion | True | fast | False | 80.90 | 88.75 | 88.54 | 3865.82 |
| astro | ensemble | quarter-expansion | True | robust | False | 83.27 | 88.75 | 92.08 | 4399.25 |
| astro | entity-graph | quarter-expansion | True | fusion | True | 69.47 | 82.29 | 76.71 | 1171.09 |
| astro | entity-graph | quarter-expansion | True | entity | False | 68.01 | 87.29 | 68.86 | 1101.88 |
| astro | entity-graph | quarter-expansion | True | lexical | False | 72.62 | 82.50 | 82.04 | 1072.46 |
| astro | entity-graph | quarter-expansion | True | traversal | False | 32.30 | 50.42 | 30.31 | 1138.79 |
| astro | graphify | quarter-expansion | True | search | True | 57.79 | 77.29 | 57.92 | 151.20 |
| astro | legacy | quarter-expansion | True | lexical | True | 60.52 | 75.42 | 64.47 | 2.76 |
| astro | turso | quarter-expansion | True | lexical-sql | True | 47.81 | 66.67 | 49.17 | 142.85 |
| data-science | adaptive | quarter-expansion | True | adaptive | True | 91.41 | 98.33 | 93.23 | 6150.57 |
| data-science | classical | quarter-expansion | True | fusion | True | 80.54 | 78.54 | 91.25 | 974.49 |
| data-science | classical | quarter-expansion | True | association | False | 80.54 | 78.54 | 91.25 | 876.56 |
| data-science | classical | quarter-expansion | True | bm25 | False | 93.08 | 98.33 | 94.06 | 933.96 |
| data-science | classical | quarter-expansion | True | topic | False | 80.54 | 78.54 | 91.25 | 894.83 |
| data-science | embeddings | quarter-expansion | True | hybrid | True | 60.04 | 88.96 | 52.00 | 1167.35 |
| data-science | embeddings | quarter-expansion | True | lexical | False | 63.24 | 83.33 | 58.19 | 878.48 |
| data-science | embeddings | quarter-expansion | True | vector | False | 39.38 | 70.42 | 29.13 | 2.30 |
| data-science | ensemble | quarter-expansion | True | quality | True | 92.43 | 98.33 | 94.11 | 10205.02 |
| data-science | ensemble | quarter-expansion | True | fast | False | 93.07 | 98.33 | 95.50 | 9021.13 |
| data-science | ensemble | quarter-expansion | True | robust | False | 91.41 | 98.33 | 93.23 | 2270.13 |
| data-science | entity-graph | quarter-expansion | True | fusion | True | 85.79 | 97.50 | 86.88 | 7060.49 |
| data-science | entity-graph | quarter-expansion | True | entity | False | 80.82 | 96.67 | 79.67 | 7879.06 |
| data-science | entity-graph | quarter-expansion | True | lexical | False | 90.31 | 99.17 | 88.75 | 8496.25 |
| data-science | entity-graph | quarter-expansion | True | traversal | False | 51.20 | 79.58 | 43.55 | 7293.33 |
| data-science | graphify | quarter-expansion | True | search | True | 54.41 | 53.96 | 62.50 | 365.32 |
| data-science | legacy | quarter-expansion | True | lexical | True | 83.22 | 95.00 | 81.75 | 0.37 |
| data-science | turso | quarter-expansion | True | lexical-sql | True | 40.16 | 74.38 | 31.79 | 484.36 |
| enterprise | adaptive | quarter-expansion | True | adaptive | True | 50.57 | 56.50 | 58.55 | 1328.02 |
| enterprise | classical | quarter-expansion | True | fusion | True | 44.35 | 42.46 | 57.50 | 41.79 |
| enterprise | classical | quarter-expansion | True | association | False | 47.72 | 45.86 | 57.50 | 43.58 |
| enterprise | classical | quarter-expansion | True | bm25 | False | 58.93 | 64.56 | 60.59 | 40.47 |
| enterprise | classical | quarter-expansion | True | topic | False | 48.11 | 46.22 | 57.50 | 43.01 |
| enterprise | embeddings | quarter-expansion | True | hybrid | True | 51.64 | 59.91 | 54.19 | 47.65 |
| enterprise | embeddings | quarter-expansion | True | lexical | False | 59.07 | 61.86 | 61.50 | 10.70 |
| enterprise | embeddings | quarter-expansion | True | vector | False | 32.56 | 36.92 | 37.72 | 36.13 |
| enterprise | ensemble | quarter-expansion | True | quality | True | 54.02 | 56.50 | 59.44 | 1490.69 |
| enterprise | ensemble | quarter-expansion | True | fast | False | 51.51 | 56.50 | 58.73 | 1533.07 |
| enterprise | ensemble | quarter-expansion | True | robust | False | 50.57 | 56.50 | 58.55 | 1544.96 |
| enterprise | entity-graph | quarter-expansion | True | fusion | True | 46.73 | 58.04 | 47.33 | 80.93 |
| enterprise | entity-graph | quarter-expansion | True | entity | False | 45.25 | 56.58 | 46.67 | 65.69 |
| enterprise | entity-graph | quarter-expansion | True | lexical | False | 59.40 | 63.73 | 60.78 | 76.70 |
| enterprise | entity-graph | quarter-expansion | True | traversal | False | 43.27 | 50.33 | 46.04 | 69.20 |
| enterprise | graphify | quarter-expansion | True | search | True | 13.63 | 17.37 | 20.42 | 142.97 |
| enterprise | legacy | quarter-expansion | True | lexical | True | 57.50 | 61.92 | 59.86 | 4.71 |
| enterprise | turso | quarter-expansion | True | lexical-sql | True | 40.32 | 49.87 | 40.85 | 40.65 |
