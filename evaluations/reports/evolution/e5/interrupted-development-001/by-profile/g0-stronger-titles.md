# Construction profile: g0-stronger-titles

[General development comparison](../README.md) · [Cost, time and accuracy](../cta.md)

Development retrieval diagnostics; values are not independent validation or official benchmark scores. Primary routes use the predeclared family default. Qualification applies to the whole profile, including every failed cell.

| Dataset | Skill family | Profile | Qualified | Route | Primary | nDCG@10 | Recall@10 | MRR@10 | Query P95 ms |
|---|---|---|---|---|---|---:|---:|---:|---:|
| architecture | adaptive | g0-stronger-titles | True | adaptive | True | 86.29 | 95.83 | 90.50 | 2168.83 |
| architecture | classical | g0-stronger-titles | True | fusion | True | 91.85 | 95.83 | 97.50 | 808.01 |
| architecture | classical | g0-stronger-titles | True | association | False | 91.32 | 95.00 | 97.50 | 792.71 |
| architecture | classical | g0-stronger-titles | True | bm25 | False | 82.37 | 80.83 | 96.25 | 891.69 |
| architecture | classical | g0-stronger-titles | True | topic | False | 91.32 | 95.00 | 97.50 | 817.86 |
| architecture | embeddings | g0-stronger-titles | True | hybrid | True | 72.38 | 92.08 | 71.54 | 390.27 |
| architecture | embeddings | g0-stronger-titles | True | lexical | False | 72.13 | 92.92 | 71.57 | 387.40 |
| architecture | embeddings | g0-stronger-titles | True | vector | False | 65.56 | 84.38 | 65.99 | 1.12 |
| architecture | ensemble | g0-stronger-titles | True | quality | True | 85.55 | 95.83 | 88.00 | 5214.03 |
| architecture | ensemble | g0-stronger-titles | True | fast | False | 86.67 | 95.83 | 89.38 | 4253.79 |
| architecture | ensemble | g0-stronger-titles | True | robust | False | 86.29 | 95.83 | 90.50 | 1668.08 |
| architecture | entity-graph | g0-stronger-titles | True | fusion | True | 83.50 | 97.50 | 81.33 | 4710.96 |
| architecture | entity-graph | g0-stronger-titles | True | entity | False | 81.76 | 93.54 | 81.15 | 2839.83 |
| architecture | entity-graph | g0-stronger-titles | True | lexical | False | 88.98 | 98.33 | 89.25 | 2871.58 |
| architecture | entity-graph | g0-stronger-titles | True | traversal | False | 80.30 | 92.92 | 80.92 | 3105.34 |
| architecture | graphify | g0-stronger-titles | True | search | True | 57.76 | 59.58 | 68.75 | 98.85 |
| architecture | legacy | g0-stronger-titles | True | lexical | True | 81.55 | 95.00 | 80.62 | 0.20 |
| architecture | turso | g0-stronger-titles | True | lexical-sql | True | 58.40 | 86.25 | 52.72 | 334.88 |
| astro | adaptive | g0-stronger-titles | True | adaptive | True | 80.86 | 86.88 | 91.04 | 2741.56 |
| astro | classical | g0-stronger-titles | True | fusion | True | 80.86 | 86.88 | 91.04 | 77.05 |
| astro | classical | g0-stronger-titles | True | association | False | 80.87 | 86.88 | 91.04 | 82.70 |
| astro | classical | g0-stronger-titles | True | bm25 | False | 78.70 | 86.25 | 87.92 | 66.67 |
| astro | classical | g0-stronger-titles | True | topic | False | 80.87 | 86.88 | 91.04 | 77.82 |
| astro | embeddings | g0-stronger-titles | True | hybrid | True | 78.52 | 85.83 | 85.54 | 106.27 |
| astro | embeddings | g0-stronger-titles | True | lexical | False | 85.95 | 88.75 | 95.42 | 83.77 |
| astro | embeddings | g0-stronger-titles | True | vector | False | 53.34 | 68.75 | 55.19 | 16.88 |
| astro | ensemble | g0-stronger-titles | True | quality | True | 81.52 | 86.88 | 91.25 | 4130.72 |
| astro | ensemble | g0-stronger-titles | True | fast | False | 82.09 | 86.88 | 92.08 | 3805.39 |
| astro | ensemble | g0-stronger-titles | True | robust | False | 80.86 | 86.88 | 91.04 | 4434.62 |
| astro | entity-graph | g0-stronger-titles | True | fusion | True | 69.47 | 82.29 | 76.71 | 1079.68 |
| astro | entity-graph | g0-stronger-titles | True | entity | False | 68.01 | 87.29 | 68.86 | 1052.80 |
| astro | entity-graph | g0-stronger-titles | True | lexical | False | 72.62 | 82.50 | 82.04 | 1100.40 |
| astro | entity-graph | g0-stronger-titles | True | traversal | False | 32.30 | 50.42 | 30.31 | 1072.36 |
| astro | graphify | g0-stronger-titles | True | search | True | 57.79 | 77.29 | 57.92 | 142.91 |
| astro | legacy | g0-stronger-titles | True | lexical | True | 60.52 | 75.42 | 64.47 | 2.33 |
| astro | turso | g0-stronger-titles | True | lexical-sql | True | 47.81 | 66.67 | 49.17 | 147.22 |
| data-science | adaptive | g0-stronger-titles | True | adaptive | True | 91.92 | 99.17 | 93.23 | 2792.22 |
| data-science | classical | g0-stronger-titles | True | fusion | True | 80.54 | 78.54 | 91.25 | 890.75 |
| data-science | classical | g0-stronger-titles | True | association | False | 80.54 | 78.54 | 91.25 | 851.92 |
| data-science | classical | g0-stronger-titles | True | bm25 | False | 93.28 | 98.33 | 94.11 | 824.03 |
| data-science | classical | g0-stronger-titles | True | topic | False | 80.54 | 78.54 | 91.25 | 827.71 |
| data-science | embeddings | g0-stronger-titles | True | hybrid | True | 60.04 | 88.96 | 52.00 | 831.28 |
| data-science | embeddings | g0-stronger-titles | True | lexical | False | 63.24 | 83.33 | 58.19 | 1565.11 |
| data-science | embeddings | g0-stronger-titles | True | vector | False | 39.38 | 70.42 | 29.13 | 2.34 |
| data-science | ensemble | g0-stronger-titles | True | quality | True | 92.88 | 99.17 | 94.11 | 12324.79 |
| data-science | ensemble | g0-stronger-titles | True | fast | False | 93.74 | 99.17 | 95.50 | 9935.37 |
| data-science | ensemble | g0-stronger-titles | True | robust | False | 91.92 | 99.17 | 93.23 | 2915.07 |
| data-science | entity-graph | g0-stronger-titles | True | fusion | True | 85.79 | 97.50 | 86.88 | 8634.08 |
| data-science | entity-graph | g0-stronger-titles | True | entity | False | 80.82 | 96.67 | 79.67 | 7587.34 |
| data-science | entity-graph | g0-stronger-titles | True | lexical | False | 90.31 | 99.17 | 88.75 | 7453.81 |
| data-science | entity-graph | g0-stronger-titles | True | traversal | False | 51.20 | 79.58 | 43.55 | 8272.66 |
| data-science | graphify | g0-stronger-titles | True | search | True | 54.41 | 53.96 | 62.50 | 354.80 |
| data-science | legacy | g0-stronger-titles | True | lexical | True | 83.22 | 95.00 | 81.75 | 0.54 |
| data-science | turso | g0-stronger-titles | True | lexical-sql | True | 40.16 | 74.38 | 31.79 | 450.24 |
| enterprise | adaptive | g0-stronger-titles | True | adaptive | True | 50.34 | 59.00 | 57.47 | 1658.95 |
| enterprise | classical | g0-stronger-titles | True | fusion | True | 43.42 | 42.46 | 56.25 | 42.65 |
| enterprise | classical | g0-stronger-titles | True | association | False | 47.21 | 45.86 | 56.25 | 41.61 |
| enterprise | classical | g0-stronger-titles | True | bm25 | False | 58.93 | 64.56 | 60.59 | 40.91 |
| enterprise | classical | g0-stronger-titles | True | topic | False | 46.68 | 46.22 | 55.00 | 43.04 |
| enterprise | embeddings | g0-stronger-titles | True | hybrid | True | 51.64 | 59.91 | 54.19 | 47.01 |
| enterprise | embeddings | g0-stronger-titles | True | lexical | False | 59.07 | 61.86 | 61.50 | 10.12 |
| enterprise | embeddings | g0-stronger-titles | True | vector | False | 32.56 | 36.92 | 37.72 | 34.56 |
| enterprise | ensemble | g0-stronger-titles | True | quality | True | 55.35 | 59.00 | 60.36 | 1497.25 |
| enterprise | ensemble | g0-stronger-titles | True | fast | False | 52.36 | 59.00 | 59.10 | 1510.41 |
| enterprise | ensemble | g0-stronger-titles | True | robust | False | 50.34 | 59.00 | 57.47 | 1358.55 |
| enterprise | entity-graph | g0-stronger-titles | True | fusion | True | 46.73 | 58.04 | 47.33 | 97.23 |
| enterprise | entity-graph | g0-stronger-titles | True | entity | False | 45.25 | 56.58 | 46.67 | 84.35 |
| enterprise | entity-graph | g0-stronger-titles | True | lexical | False | 59.40 | 63.73 | 60.78 | 110.40 |
| enterprise | entity-graph | g0-stronger-titles | True | traversal | False | 43.27 | 50.33 | 46.04 | 86.91 |
| enterprise | graphify | g0-stronger-titles | True | search | True | 13.63 | 17.37 | 20.42 | 139.69 |
| enterprise | legacy | g0-stronger-titles | True | lexical | True | 57.50 | 61.92 | 59.86 | 3.42 |
| enterprise | turso | g0-stronger-titles | True | lexical-sql | True | 40.32 | 49.87 | 40.85 | 47.52 |
