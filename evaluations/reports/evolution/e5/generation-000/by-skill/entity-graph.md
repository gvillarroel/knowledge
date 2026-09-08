# Skill family: entity-graph

[General development comparison](../README.md) · [Cost, time and accuracy](../cta.md)

Development retrieval diagnostics; values are not independent validation or official benchmark scores. Primary routes use the predeclared family default. Qualification applies to the whole profile, including every failed cell.

| Dataset | Skill family | Profile | Qualified | Route | Primary | nDCG@10 | Recall@10 | MRR@10 | Query P95 ms |
|---|---|---|---|---|---|---:|---:|---:|---:|
| architecture | entity-graph | baseline | True | fusion | True | 83.50 | 97.50 | 81.33 | 4298.90 |
| architecture | entity-graph | baseline | True | entity | False | 81.76 | 93.54 | 81.15 | 3056.22 |
| architecture | entity-graph | baseline | True | lexical | False | 88.98 | 98.33 | 89.25 | 3194.62 |
| architecture | entity-graph | baseline | True | traversal | False | 80.30 | 92.92 | 80.92 | 3588.57 |
| architecture | entity-graph | bm25-low-b | True | fusion | True | 83.42 | 97.50 | 81.25 | 3553.18 |
| architecture | entity-graph | bm25-low-b | True | entity | False | 81.76 | 93.54 | 81.15 | 3782.93 |
| architecture | entity-graph | bm25-low-b | True | lexical | False | 87.93 | 97.71 | 88.50 | 3706.87 |
| architecture | entity-graph | bm25-low-b | True | traversal | False | 80.30 | 92.92 | 80.92 | 3296.40 |
| architecture | entity-graph | neural-record | True | fusion | True | 83.50 | 97.50 | 81.33 | 3051.84 |
| architecture | entity-graph | neural-record | True | entity | False | 81.76 | 93.54 | 81.15 | 3145.99 |
| architecture | entity-graph | neural-record | True | lexical | False | 88.98 | 98.33 | 89.25 | 2995.67 |
| architecture | entity-graph | neural-record | True | traversal | False | 80.30 | 92.92 | 80.92 | 2989.88 |
| architecture | entity-graph | quarter-expansion | True | fusion | True | 83.50 | 97.50 | 81.33 | 5589.32 |
| architecture | entity-graph | quarter-expansion | True | entity | False | 81.76 | 93.54 | 81.15 | 3360.44 |
| architecture | entity-graph | quarter-expansion | True | lexical | False | 88.98 | 98.33 | 89.25 | 5744.78 |
| architecture | entity-graph | quarter-expansion | True | traversal | False | 80.30 | 92.92 | 80.92 | 3178.78 |
| architecture | entity-graph | stronger-titles | True | fusion | True | 83.50 | 97.50 | 81.33 | 4710.96 |
| architecture | entity-graph | stronger-titles | True | entity | False | 81.76 | 93.54 | 81.15 | 2839.83 |
| architecture | entity-graph | stronger-titles | True | lexical | False | 88.98 | 98.33 | 89.25 | 2871.58 |
| architecture | entity-graph | stronger-titles | True | traversal | False | 80.30 | 92.92 | 80.92 | 3105.34 |
| astro | entity-graph | baseline | True | fusion | True | 69.47 | 82.29 | 76.71 | 1306.59 |
| astro | entity-graph | baseline | True | entity | False | 68.01 | 87.29 | 68.86 | 1222.59 |
| astro | entity-graph | baseline | True | lexical | False | 72.62 | 82.50 | 82.04 | 1218.73 |
| astro | entity-graph | baseline | True | traversal | False | 32.30 | 50.42 | 30.31 | 1159.26 |
| astro | entity-graph | bm25-low-b | True | fusion | True | 66.67 | 82.29 | 71.65 | 1211.67 |
| astro | entity-graph | bm25-low-b | True | entity | False | 68.01 | 87.29 | 68.86 | 1382.09 |
| astro | entity-graph | bm25-low-b | True | lexical | False | 75.63 | 84.17 | 83.12 | 1445.36 |
| astro | entity-graph | bm25-low-b | True | traversal | False | 32.30 | 50.42 | 30.31 | 1215.95 |
| astro | entity-graph | neural-record | True | fusion | True | 69.47 | 82.29 | 76.71 | 1199.38 |
| astro | entity-graph | neural-record | True | entity | False | 68.01 | 87.29 | 68.86 | 1082.86 |
| astro | entity-graph | neural-record | True | lexical | False | 72.62 | 82.50 | 82.04 | 1109.84 |
| astro | entity-graph | neural-record | True | traversal | False | 32.30 | 50.42 | 30.31 | 1086.75 |
| astro | entity-graph | quarter-expansion | True | fusion | True | 69.47 | 82.29 | 76.71 | 1171.09 |
| astro | entity-graph | quarter-expansion | True | entity | False | 68.01 | 87.29 | 68.86 | 1101.88 |
| astro | entity-graph | quarter-expansion | True | lexical | False | 72.62 | 82.50 | 82.04 | 1072.46 |
| astro | entity-graph | quarter-expansion | True | traversal | False | 32.30 | 50.42 | 30.31 | 1138.79 |
| astro | entity-graph | stronger-titles | True | fusion | True | 69.47 | 82.29 | 76.71 | 1079.68 |
| astro | entity-graph | stronger-titles | True | entity | False | 68.01 | 87.29 | 68.86 | 1052.80 |
| astro | entity-graph | stronger-titles | True | lexical | False | 72.62 | 82.50 | 82.04 | 1100.40 |
| astro | entity-graph | stronger-titles | True | traversal | False | 32.30 | 50.42 | 30.31 | 1072.36 |
| data-science | entity-graph | baseline | True | fusion | True | 85.79 | 97.50 | 86.88 | 8414.53 |
| data-science | entity-graph | baseline | True | entity | False | 80.82 | 96.67 | 79.67 | 9290.45 |
| data-science | entity-graph | baseline | True | lexical | False | 90.31 | 99.17 | 88.75 | 8373.27 |
| data-science | entity-graph | baseline | True | traversal | False | 51.20 | 79.58 | 43.55 | 8172.18 |
| data-science | entity-graph | bm25-low-b | True | fusion | True | 80.74 | 97.50 | 78.36 | 8622.57 |
| data-science | entity-graph | bm25-low-b | True | entity | False | 80.82 | 96.67 | 79.67 | 10356.84 |
| data-science | entity-graph | bm25-low-b | True | lexical | False | 89.22 | 98.33 | 88.96 | 10429.97 |
| data-science | entity-graph | bm25-low-b | True | traversal | False | 51.20 | 79.58 | 43.55 | 8855.73 |
| data-science | entity-graph | neural-record | True | fusion | True | 85.79 | 97.50 | 86.88 | 7766.54 |
| data-science | entity-graph | neural-record | True | entity | False | 80.82 | 96.67 | 79.67 | 7681.21 |
| data-science | entity-graph | neural-record | True | lexical | False | 90.31 | 99.17 | 88.75 | 7450.80 |
| data-science | entity-graph | neural-record | True | traversal | False | 51.20 | 79.58 | 43.55 | 7313.86 |
| data-science | entity-graph | quarter-expansion | True | fusion | True | 85.79 | 97.50 | 86.88 | 7060.49 |
| data-science | entity-graph | quarter-expansion | True | entity | False | 80.82 | 96.67 | 79.67 | 7879.06 |
| data-science | entity-graph | quarter-expansion | True | lexical | False | 90.31 | 99.17 | 88.75 | 8496.25 |
| data-science | entity-graph | quarter-expansion | True | traversal | False | 51.20 | 79.58 | 43.55 | 7293.33 |
| data-science | entity-graph | stronger-titles | True | fusion | True | 85.79 | 97.50 | 86.88 | 8634.08 |
| data-science | entity-graph | stronger-titles | True | entity | False | 80.82 | 96.67 | 79.67 | 7587.34 |
| data-science | entity-graph | stronger-titles | True | lexical | False | 90.31 | 99.17 | 88.75 | 7453.81 |
| data-science | entity-graph | stronger-titles | True | traversal | False | 51.20 | 79.58 | 43.55 | 8272.66 |
| enterprise | entity-graph | baseline | True | fusion | True | 46.73 | 58.04 | 47.33 | 91.83 |
| enterprise | entity-graph | baseline | True | entity | False | 45.25 | 56.58 | 46.67 | 108.48 |
| enterprise | entity-graph | baseline | True | lexical | False | 59.40 | 63.73 | 60.78 | 79.86 |
| enterprise | entity-graph | baseline | True | traversal | False | 43.27 | 50.33 | 46.04 | 106.62 |
| enterprise | entity-graph | bm25-low-b | True | fusion | True | 47.28 | 58.31 | 47.51 | 48.07 |
| enterprise | entity-graph | bm25-low-b | True | entity | False | 45.25 | 56.58 | 46.67 | 49.60 |
| enterprise | entity-graph | bm25-low-b | True | lexical | False | 58.33 | 63.73 | 59.06 | 50.52 |
| enterprise | entity-graph | bm25-low-b | True | traversal | False | 43.27 | 50.33 | 46.04 | 50.24 |
| enterprise | entity-graph | neural-record | True | fusion | True | 46.73 | 58.04 | 47.33 | 56.53 |
| enterprise | entity-graph | neural-record | True | entity | False | 45.25 | 56.58 | 46.67 | 54.25 |
| enterprise | entity-graph | neural-record | True | lexical | False | 59.40 | 63.73 | 60.78 | 69.79 |
| enterprise | entity-graph | neural-record | True | traversal | False | 43.27 | 50.33 | 46.04 | 58.54 |
| enterprise | entity-graph | quarter-expansion | True | fusion | True | 46.73 | 58.04 | 47.33 | 80.93 |
| enterprise | entity-graph | quarter-expansion | True | entity | False | 45.25 | 56.58 | 46.67 | 65.69 |
| enterprise | entity-graph | quarter-expansion | True | lexical | False | 59.40 | 63.73 | 60.78 | 76.70 |
| enterprise | entity-graph | quarter-expansion | True | traversal | False | 43.27 | 50.33 | 46.04 | 69.20 |
| enterprise | entity-graph | stronger-titles | True | fusion | True | 46.73 | 58.04 | 47.33 | 97.23 |
| enterprise | entity-graph | stronger-titles | True | entity | False | 45.25 | 56.58 | 46.67 | 84.35 |
| enterprise | entity-graph | stronger-titles | True | lexical | False | 59.40 | 63.73 | 60.78 | 110.40 |
| enterprise | entity-graph | stronger-titles | True | traversal | False | 43.27 | 50.33 | 46.04 | 86.91 |
