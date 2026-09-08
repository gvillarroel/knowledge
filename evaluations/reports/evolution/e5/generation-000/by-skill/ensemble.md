# Skill family: ensemble

[General development comparison](../README.md) · [Cost, time and accuracy](../cta.md)

Development retrieval diagnostics; values are not independent validation or official benchmark scores. Primary routes use the predeclared family default. Qualification applies to the whole profile, including every failed cell.

| Dataset | Skill family | Profile | Qualified | Route | Primary | nDCG@10 | Recall@10 | MRR@10 | Query P95 ms |
|---|---|---|---|---|---|---:|---:|---:|---:|
| architecture | ensemble | baseline | True | quality | True | 85.01 | 95.21 | 88.00 | 5763.66 |
| architecture | ensemble | baseline | True | fast | False | 86.04 | 95.21 | 89.38 | 4797.89 |
| architecture | ensemble | baseline | True | robust | False | 85.61 | 95.21 | 90.50 | 1905.55 |
| architecture | ensemble | bm25-low-b | True | quality | True | 85.20 | 96.04 | 88.00 | 5732.61 |
| architecture | ensemble | bm25-low-b | True | fast | False | 86.76 | 96.04 | 90.92 | 4295.78 |
| architecture | ensemble | bm25-low-b | True | robust | False | 85.80 | 96.04 | 90.50 | 1903.62 |
| architecture | ensemble | neural-record | True | quality | True | 84.04 | 95.21 | 86.75 | 5578.47 |
| architecture | ensemble | neural-record | True | fast | False | 86.04 | 95.21 | 89.38 | 4696.71 |
| architecture | ensemble | neural-record | True | robust | False | 85.61 | 95.21 | 90.50 | 1869.50 |
| architecture | ensemble | quarter-expansion | True | quality | True | 84.95 | 95.21 | 87.94 | 11204.95 |
| architecture | ensemble | quarter-expansion | True | fast | False | 86.08 | 95.21 | 90.62 | 4737.18 |
| architecture | ensemble | quarter-expansion | True | robust | False | 85.18 | 95.21 | 89.19 | 1716.46 |
| architecture | ensemble | stronger-titles | True | quality | True | 85.55 | 95.83 | 88.00 | 5214.03 |
| architecture | ensemble | stronger-titles | True | fast | False | 86.67 | 95.83 | 89.38 | 4253.79 |
| architecture | ensemble | stronger-titles | True | robust | False | 86.29 | 95.83 | 90.50 | 1668.08 |
| astro | ensemble | baseline | True | quality | True | 82.62 | 88.75 | 90.62 | 5785.08 |
| astro | ensemble | baseline | True | fast | False | 82.62 | 88.75 | 91.46 | 4219.04 |
| astro | ensemble | baseline | True | robust | False | 83.34 | 88.75 | 91.46 | 3051.60 |
| astro | ensemble | bm25-low-b | True | quality | True | 79.57 | 87.08 | 88.02 | 4726.36 |
| astro | ensemble | bm25-low-b | True | fast | False | 77.93 | 87.08 | 85.49 | 4340.73 |
| astro | ensemble | bm25-low-b | True | robust | False | 77.74 | 87.08 | 83.90 | 3048.70 |
| astro | ensemble | neural-record | True | quality | True | 82.46 | 88.75 | 90.62 | 4210.70 |
| astro | ensemble | neural-record | True | fast | False | 82.62 | 88.75 | 91.46 | 3691.36 |
| astro | ensemble | neural-record | True | robust | False | 83.34 | 88.75 | 91.46 | 2759.03 |
| astro | ensemble | quarter-expansion | True | quality | True | 81.28 | 88.75 | 88.75 | 5624.87 |
| astro | ensemble | quarter-expansion | True | fast | False | 80.90 | 88.75 | 88.54 | 3865.82 |
| astro | ensemble | quarter-expansion | True | robust | False | 83.27 | 88.75 | 92.08 | 4399.25 |
| astro | ensemble | stronger-titles | True | quality | True | 81.52 | 86.88 | 91.25 | 4130.72 |
| astro | ensemble | stronger-titles | True | fast | False | 82.09 | 86.88 | 92.08 | 3805.39 |
| astro | ensemble | stronger-titles | True | robust | False | 80.86 | 86.88 | 91.04 | 4434.62 |
| data-science | ensemble | baseline | True | quality | True | 92.78 | 99.17 | 94.11 | 11908.41 |
| data-science | ensemble | baseline | True | fast | False | 94.44 | 99.17 | 96.75 | 10589.14 |
| data-science | ensemble | baseline | True | robust | False | 91.78 | 99.17 | 93.23 | 2611.21 |
| data-science | ensemble | bm25-low-b | True | quality | True | 93.79 | 99.17 | 94.06 | 12193.16 |
| data-science | ensemble | bm25-low-b | True | fast | False | 93.98 | 99.17 | 95.50 | 9948.19 |
| data-science | ensemble | bm25-low-b | True | robust | False | 91.97 | 99.17 | 93.19 | 2591.67 |
| data-science | ensemble | neural-record | True | quality | True | 92.87 | 99.17 | 94.11 | 13592.51 |
| data-science | ensemble | neural-record | True | fast | False | 94.44 | 99.17 | 96.75 | 10205.32 |
| data-science | ensemble | neural-record | True | robust | False | 91.78 | 99.17 | 93.23 | 2499.86 |
| data-science | ensemble | quarter-expansion | True | quality | True | 92.43 | 98.33 | 94.11 | 10205.02 |
| data-science | ensemble | quarter-expansion | True | fast | False | 93.07 | 98.33 | 95.50 | 9021.13 |
| data-science | ensemble | quarter-expansion | True | robust | False | 91.41 | 98.33 | 93.23 | 2270.13 |
| data-science | ensemble | stronger-titles | True | quality | True | 92.88 | 99.17 | 94.11 | 12324.79 |
| data-science | ensemble | stronger-titles | True | fast | False | 93.74 | 99.17 | 95.50 | 9935.37 |
| data-science | ensemble | stronger-titles | True | robust | False | 91.92 | 99.17 | 93.23 | 2915.07 |
| enterprise | ensemble | baseline | True | quality | True | 55.35 | 59.00 | 60.36 | 1736.95 |
| enterprise | ensemble | baseline | True | fast | False | 52.32 | 59.00 | 59.07 | 1613.61 |
| enterprise | ensemble | baseline | True | robust | False | 50.34 | 59.00 | 57.47 | 2068.93 |
| enterprise | ensemble | bm25-low-b | True | quality | True | 53.88 | 59.07 | 57.86 | 1587.11 |
| enterprise | ensemble | bm25-low-b | True | fast | False | 51.68 | 59.07 | 57.73 | 1459.75 |
| enterprise | ensemble | bm25-low-b | True | robust | False | 50.69 | 59.07 | 57.51 | 1419.41 |
| enterprise | ensemble | neural-record | True | quality | True | 55.61 | 59.00 | 60.36 | 1784.70 |
| enterprise | ensemble | neural-record | True | fast | False | 52.32 | 59.00 | 59.07 | 1560.58 |
| enterprise | ensemble | neural-record | True | robust | False | 50.34 | 59.00 | 57.47 | 1590.84 |
| enterprise | ensemble | quarter-expansion | True | quality | True | 54.02 | 56.50 | 59.44 | 1490.69 |
| enterprise | ensemble | quarter-expansion | True | fast | False | 51.51 | 56.50 | 58.73 | 1533.07 |
| enterprise | ensemble | quarter-expansion | True | robust | False | 50.57 | 56.50 | 58.55 | 1544.96 |
| enterprise | ensemble | stronger-titles | True | quality | True | 55.35 | 59.00 | 60.36 | 1497.25 |
| enterprise | ensemble | stronger-titles | True | fast | False | 52.36 | 59.00 | 59.10 | 1510.41 |
| enterprise | ensemble | stronger-titles | True | robust | False | 50.34 | 59.00 | 57.47 | 1358.55 |
