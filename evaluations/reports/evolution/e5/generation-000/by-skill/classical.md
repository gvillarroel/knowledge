# Skill family: classical

[General development comparison](../README.md) · [Cost, time and accuracy](../cta.md)

Development retrieval diagnostics; values are not independent validation or official benchmark scores. Primary routes use the predeclared family default. Qualification applies to the whole profile, including every failed cell.

| Dataset | Skill family | Profile | Qualified | Route | Primary | nDCG@10 | Recall@10 | MRR@10 | Query P95 ms |
|---|---|---|---|---|---|---:|---:|---:|---:|
| architecture | classical | baseline | True | fusion | True | 92.58 | 97.29 | 97.50 | 1491.18 |
| architecture | classical | baseline | True | association | False | 92.56 | 97.29 | 97.50 | 2179.70 |
| architecture | classical | baseline | True | bm25 | False | 84.18 | 83.75 | 95.00 | 861.65 |
| architecture | classical | baseline | True | topic | False | 92.56 | 97.29 | 97.50 | 1933.61 |
| architecture | classical | bm25-low-b | True | fusion | True | 89.83 | 96.46 | 92.92 | 676.42 |
| architecture | classical | bm25-low-b | True | association | False | 89.93 | 96.46 | 93.33 | 689.40 |
| architecture | classical | bm25-low-b | True | bm25 | False | 80.11 | 80.21 | 91.46 | 696.88 |
| architecture | classical | bm25-low-b | True | topic | False | 89.91 | 96.46 | 93.33 | 703.46 |
| architecture | classical | neural-record | True | fusion | True | 92.58 | 97.29 | 97.50 | 1034.71 |
| architecture | classical | neural-record | True | association | False | 92.56 | 97.29 | 97.50 | 1052.38 |
| architecture | classical | neural-record | True | bm25 | False | 84.18 | 83.75 | 95.00 | 888.83 |
| architecture | classical | neural-record | True | topic | False | 92.56 | 97.29 | 97.50 | 916.16 |
| architecture | classical | quarter-expansion | True | fusion | True | 91.72 | 97.29 | 95.00 | 959.85 |
| architecture | classical | quarter-expansion | True | association | False | 91.72 | 97.29 | 95.00 | 926.73 |
| architecture | classical | quarter-expansion | True | bm25 | False | 84.18 | 83.75 | 95.00 | 992.94 |
| architecture | classical | quarter-expansion | True | topic | False | 91.72 | 97.29 | 95.00 | 833.42 |
| architecture | classical | stronger-titles | True | fusion | True | 91.85 | 95.83 | 97.50 | 808.01 |
| architecture | classical | stronger-titles | True | association | False | 91.32 | 95.00 | 97.50 | 792.71 |
| architecture | classical | stronger-titles | True | bm25 | False | 82.37 | 80.83 | 96.25 | 891.69 |
| architecture | classical | stronger-titles | True | topic | False | 91.32 | 95.00 | 97.50 | 817.86 |
| astro | classical | baseline | True | fusion | True | 83.34 | 88.75 | 91.46 | 86.18 |
| astro | classical | baseline | True | association | False | 83.37 | 88.75 | 91.46 | 83.13 |
| astro | classical | baseline | True | bm25 | False | 83.13 | 88.75 | 92.08 | 66.46 |
| astro | classical | baseline | True | topic | False | 83.22 | 88.75 | 91.46 | 84.27 |
| astro | classical | bm25-low-b | True | fusion | True | 77.74 | 87.08 | 83.90 | 79.81 |
| astro | classical | bm25-low-b | True | association | False | 78.31 | 87.92 | 84.11 | 82.08 |
| astro | classical | bm25-low-b | True | bm25 | False | 78.63 | 87.08 | 84.77 | 65.51 |
| astro | classical | bm25-low-b | True | topic | False | 77.78 | 87.08 | 84.08 | 80.25 |
| astro | classical | neural-record | True | fusion | True | 83.34 | 88.75 | 91.46 | 89.67 |
| astro | classical | neural-record | True | association | False | 83.37 | 88.75 | 91.46 | 79.10 |
| astro | classical | neural-record | True | bm25 | False | 83.13 | 88.75 | 92.08 | 62.08 |
| astro | classical | neural-record | True | topic | False | 83.22 | 88.75 | 91.46 | 84.83 |
| astro | classical | quarter-expansion | True | fusion | True | 83.27 | 88.75 | 92.08 | 82.33 |
| astro | classical | quarter-expansion | True | association | False | 83.27 | 88.75 | 92.08 | 80.16 |
| astro | classical | quarter-expansion | True | bm25 | False | 83.13 | 88.75 | 92.08 | 81.02 |
| astro | classical | quarter-expansion | True | topic | False | 83.29 | 88.75 | 92.08 | 98.53 |
| astro | classical | stronger-titles | True | fusion | True | 80.86 | 86.88 | 91.04 | 77.05 |
| astro | classical | stronger-titles | True | association | False | 80.87 | 86.88 | 91.04 | 82.70 |
| astro | classical | stronger-titles | True | bm25 | False | 78.70 | 86.25 | 87.92 | 66.67 |
| astro | classical | stronger-titles | True | topic | False | 80.87 | 86.88 | 91.04 | 77.82 |
| data-science | classical | baseline | True | fusion | True | 80.54 | 78.54 | 91.25 | 987.14 |
| data-science | classical | baseline | True | association | False | 80.54 | 78.54 | 91.25 | 1143.88 |
| data-science | classical | baseline | True | bm25 | False | 93.08 | 98.33 | 94.06 | 1094.24 |
| data-science | classical | baseline | True | topic | False | 80.54 | 78.54 | 91.25 | 1119.91 |
| data-science | classical | bm25-low-b | True | fusion | True | 80.54 | 78.54 | 91.25 | 997.34 |
| data-science | classical | bm25-low-b | True | association | False | 80.54 | 78.54 | 91.25 | 855.92 |
| data-science | classical | bm25-low-b | True | bm25 | False | 93.33 | 98.33 | 94.03 | 895.80 |
| data-science | classical | bm25-low-b | True | topic | False | 80.54 | 78.54 | 91.25 | 834.52 |
| data-science | classical | neural-record | True | fusion | True | 80.54 | 78.54 | 91.25 | 961.80 |
| data-science | classical | neural-record | True | association | False | 80.54 | 78.54 | 91.25 | 949.53 |
| data-science | classical | neural-record | True | bm25 | False | 93.08 | 98.33 | 94.06 | 910.91 |
| data-science | classical | neural-record | True | topic | False | 80.54 | 78.54 | 91.25 | 942.22 |
| data-science | classical | quarter-expansion | True | fusion | True | 80.54 | 78.54 | 91.25 | 974.49 |
| data-science | classical | quarter-expansion | True | association | False | 80.54 | 78.54 | 91.25 | 876.56 |
| data-science | classical | quarter-expansion | True | bm25 | False | 93.08 | 98.33 | 94.06 | 933.96 |
| data-science | classical | quarter-expansion | True | topic | False | 80.54 | 78.54 | 91.25 | 894.83 |
| data-science | classical | stronger-titles | True | fusion | True | 80.54 | 78.54 | 91.25 | 890.75 |
| data-science | classical | stronger-titles | True | association | False | 80.54 | 78.54 | 91.25 | 851.92 |
| data-science | classical | stronger-titles | True | bm25 | False | 93.28 | 98.33 | 94.11 | 824.03 |
| data-science | classical | stronger-titles | True | topic | False | 80.54 | 78.54 | 91.25 | 827.71 |
| enterprise | classical | baseline | True | fusion | True | 43.42 | 42.46 | 56.25 | 44.55 |
| enterprise | classical | baseline | True | association | False | 47.21 | 45.86 | 56.25 | 45.29 |
| enterprise | classical | baseline | True | bm25 | False | 58.93 | 64.56 | 60.59 | 43.27 |
| enterprise | classical | baseline | True | topic | False | 46.68 | 46.22 | 55.00 | 43.64 |
| enterprise | classical | bm25-low-b | True | fusion | True | 44.25 | 43.99 | 56.25 | 47.77 |
| enterprise | classical | bm25-low-b | True | association | False | 47.29 | 45.86 | 56.25 | 47.69 |
| enterprise | classical | bm25-low-b | True | bm25 | False | 58.95 | 64.98 | 60.67 | 45.97 |
| enterprise | classical | bm25-low-b | True | topic | False | 47.80 | 46.22 | 56.25 | 49.02 |
| enterprise | classical | neural-record | True | fusion | True | 43.42 | 42.46 | 56.25 | 45.92 |
| enterprise | classical | neural-record | True | association | False | 47.21 | 45.86 | 56.25 | 45.64 |
| enterprise | classical | neural-record | True | bm25 | False | 58.93 | 64.56 | 60.59 | 41.72 |
| enterprise | classical | neural-record | True | topic | False | 46.68 | 46.22 | 55.00 | 44.69 |
| enterprise | classical | quarter-expansion | True | fusion | True | 44.35 | 42.46 | 57.50 | 41.79 |
| enterprise | classical | quarter-expansion | True | association | False | 47.72 | 45.86 | 57.50 | 43.58 |
| enterprise | classical | quarter-expansion | True | bm25 | False | 58.93 | 64.56 | 60.59 | 40.47 |
| enterprise | classical | quarter-expansion | True | topic | False | 48.11 | 46.22 | 57.50 | 43.01 |
| enterprise | classical | stronger-titles | True | fusion | True | 43.42 | 42.46 | 56.25 | 42.65 |
| enterprise | classical | stronger-titles | True | association | False | 47.21 | 45.86 | 56.25 | 41.61 |
| enterprise | classical | stronger-titles | True | bm25 | False | 58.93 | 64.56 | 60.59 | 40.91 |
| enterprise | classical | stronger-titles | True | topic | False | 46.68 | 46.22 | 55.00 | 43.04 |
