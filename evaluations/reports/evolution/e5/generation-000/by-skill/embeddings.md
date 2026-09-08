# Skill family: embeddings

[General development comparison](../README.md) · [Cost, time and accuracy](../cta.md)

Development retrieval diagnostics; values are not independent validation or official benchmark scores. Primary routes use the predeclared family default. Qualification applies to the whole profile, including every failed cell.

| Dataset | Skill family | Profile | Qualified | Route | Primary | nDCG@10 | Recall@10 | MRR@10 | Query P95 ms |
|---|---|---|---|---|---|---:|---:|---:|---:|
| architecture | embeddings | baseline | True | hybrid | True | 72.38 | 92.08 | 71.54 | 411.20 |
| architecture | embeddings | baseline | True | lexical | False | 72.13 | 92.92 | 71.57 | 418.70 |
| architecture | embeddings | baseline | True | vector | False | 65.56 | 84.38 | 65.99 | 1.19 |
| architecture | embeddings | bm25-low-b | True | hybrid | True | 72.38 | 92.08 | 71.54 | 498.33 |
| architecture | embeddings | bm25-low-b | True | lexical | False | 72.13 | 92.92 | 71.57 | 427.85 |
| architecture | embeddings | bm25-low-b | True | vector | False | 65.56 | 84.38 | 65.99 | 1.64 |
| architecture | embeddings | neural-record | True | hybrid | True | 77.08 | 93.54 | 78.82 | 597.31 |
| architecture | embeddings | neural-record | True | lexical | False | 72.13 | 92.92 | 71.57 | 445.03 |
| architecture | embeddings | neural-record | True | vector | False | 75.73 | 91.25 | 77.65 | 668.06 |
| architecture | embeddings | quarter-expansion | True | hybrid | True | 72.38 | 92.08 | 71.54 | 685.21 |
| architecture | embeddings | quarter-expansion | True | lexical | False | 72.13 | 92.92 | 71.57 | 623.78 |
| architecture | embeddings | quarter-expansion | True | vector | False | 65.56 | 84.38 | 65.99 | 1.87 |
| architecture | embeddings | stronger-titles | True | hybrid | True | 72.38 | 92.08 | 71.54 | 390.27 |
| architecture | embeddings | stronger-titles | True | lexical | False | 72.13 | 92.92 | 71.57 | 387.40 |
| architecture | embeddings | stronger-titles | True | vector | False | 65.56 | 84.38 | 65.99 | 1.12 |
| astro | embeddings | baseline | True | hybrid | True | 78.52 | 85.83 | 85.54 | 99.41 |
| astro | embeddings | baseline | True | lexical | False | 85.95 | 88.75 | 95.42 | 84.04 |
| astro | embeddings | baseline | True | vector | False | 53.34 | 68.75 | 55.19 | 17.28 |
| astro | embeddings | bm25-low-b | True | hybrid | True | 78.52 | 85.83 | 85.54 | 154.16 |
| astro | embeddings | bm25-low-b | True | lexical | False | 85.95 | 88.75 | 95.42 | 124.60 |
| astro | embeddings | bm25-low-b | True | vector | False | 53.34 | 68.75 | 55.19 | 26.02 |
| astro | embeddings | neural-record | True | hybrid | True | 74.34 | 91.04 | 73.62 | 244.34 |
| astro | embeddings | neural-record | True | lexical | False | 85.95 | 88.75 | 95.42 | 84.24 |
| astro | embeddings | neural-record | True | vector | False | 50.65 | 67.71 | 51.92 | 166.95 |
| astro | embeddings | quarter-expansion | True | hybrid | True | 78.52 | 85.83 | 85.54 | 109.11 |
| astro | embeddings | quarter-expansion | True | lexical | False | 85.95 | 88.75 | 95.42 | 83.82 |
| astro | embeddings | quarter-expansion | True | vector | False | 53.34 | 68.75 | 55.19 | 19.18 |
| astro | embeddings | stronger-titles | True | hybrid | True | 78.52 | 85.83 | 85.54 | 106.27 |
| astro | embeddings | stronger-titles | True | lexical | False | 85.95 | 88.75 | 95.42 | 83.77 |
| astro | embeddings | stronger-titles | True | vector | False | 53.34 | 68.75 | 55.19 | 16.88 |
| data-science | embeddings | baseline | True | hybrid | True | 60.04 | 88.96 | 52.00 | 923.95 |
| data-science | embeddings | baseline | True | lexical | False | 63.24 | 83.33 | 58.19 | 959.14 |
| data-science | embeddings | baseline | True | vector | False | 39.38 | 70.42 | 29.13 | 2.36 |
| data-science | embeddings | bm25-low-b | True | hybrid | True | 60.04 | 88.96 | 52.00 | 808.83 |
| data-science | embeddings | bm25-low-b | True | lexical | False | 63.24 | 83.33 | 58.19 | 778.35 |
| data-science | embeddings | bm25-low-b | True | vector | False | 39.38 | 70.42 | 29.13 | 1.99 |
| data-science | embeddings | neural-record | True | hybrid | True | 87.89 | 97.50 | 88.34 | 1092.20 |
| data-science | embeddings | neural-record | True | lexical | False | 63.24 | 83.33 | 58.19 | 969.29 |
| data-science | embeddings | neural-record | True | vector | False | 87.92 | 97.50 | 87.38 | 148.86 |
| data-science | embeddings | quarter-expansion | True | hybrid | True | 60.04 | 88.96 | 52.00 | 1167.35 |
| data-science | embeddings | quarter-expansion | True | lexical | False | 63.24 | 83.33 | 58.19 | 878.48 |
| data-science | embeddings | quarter-expansion | True | vector | False | 39.38 | 70.42 | 29.13 | 2.30 |
| data-science | embeddings | stronger-titles | True | hybrid | True | 60.04 | 88.96 | 52.00 | 831.28 |
| data-science | embeddings | stronger-titles | True | lexical | False | 63.24 | 83.33 | 58.19 | 1565.11 |
| data-science | embeddings | stronger-titles | True | vector | False | 39.38 | 70.42 | 29.13 | 2.34 |
| enterprise | embeddings | baseline | True | hybrid | True | 51.64 | 59.91 | 54.19 | 47.76 |
| enterprise | embeddings | baseline | True | lexical | False | 59.07 | 61.86 | 61.50 | 9.79 |
| enterprise | embeddings | baseline | True | vector | False | 32.56 | 36.92 | 37.72 | 36.21 |
| enterprise | embeddings | bm25-low-b | True | hybrid | True | 51.64 | 59.91 | 54.19 | 48.41 |
| enterprise | embeddings | bm25-low-b | True | lexical | False | 59.07 | 61.86 | 61.50 | 10.08 |
| enterprise | embeddings | bm25-low-b | True | vector | False | 32.56 | 36.92 | 37.72 | 35.73 |
| enterprise | embeddings | neural-record | True | hybrid | True | 63.19 | 68.38 | 64.38 | 194.53 |
| enterprise | embeddings | neural-record | True | lexical | False | 59.07 | 61.86 | 61.50 | 9.77 |
| enterprise | embeddings | neural-record | True | vector | False | 60.70 | 68.94 | 60.82 | 188.18 |
| enterprise | embeddings | quarter-expansion | True | hybrid | True | 51.64 | 59.91 | 54.19 | 47.65 |
| enterprise | embeddings | quarter-expansion | True | lexical | False | 59.07 | 61.86 | 61.50 | 10.70 |
| enterprise | embeddings | quarter-expansion | True | vector | False | 32.56 | 36.92 | 37.72 | 36.13 |
| enterprise | embeddings | stronger-titles | True | hybrid | True | 51.64 | 59.91 | 54.19 | 47.01 |
| enterprise | embeddings | stronger-titles | True | lexical | False | 59.07 | 61.86 | 61.50 | 10.12 |
| enterprise | embeddings | stronger-titles | True | vector | False | 32.56 | 36.92 | 37.72 | 34.56 |
