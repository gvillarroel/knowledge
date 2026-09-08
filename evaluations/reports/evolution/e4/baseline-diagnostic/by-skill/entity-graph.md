# Skill family: entity-graph

[General development comparison](../README.md) · [Cost, time and accuracy](../cta.md)

Development retrieval diagnostics; values are not independent validation or official benchmark scores. Primary routes use the predeclared family default. Qualification applies to the whole profile, including every failed cell.

| Dataset | Skill family | Profile | Qualified | Route | Primary | nDCG@10 | Recall@10 | MRR@10 | Query P95 ms |
|---|---|---|---|---|---|---:|---:|---:|---:|
| architecture | entity-graph | baseline | False | fusion | True | 83.50 | 97.50 | 81.33 | 2931.74 |
| architecture | entity-graph | baseline | False | entity | False | 81.76 | 93.54 | 81.15 | 2883.36 |
| architecture | entity-graph | baseline | False | lexical | False | 88.98 | 98.33 | 89.25 | 2891.89 |
| architecture | entity-graph | baseline | False | traversal | False | 80.30 | 92.92 | 80.92 | 2902.55 |
| astro | entity-graph | baseline | False | fusion | True | 69.47 | 82.29 | 76.71 | 1035.23 |
| astro | entity-graph | baseline | False | entity | False | 68.01 | 87.29 | 68.86 | 1045.70 |
| astro | entity-graph | baseline | False | lexical | False | 72.62 | 82.50 | 82.04 | 1033.27 |
| astro | entity-graph | baseline | False | traversal | False | 32.30 | 50.42 | 30.31 | 1031.33 |
| data-science | entity-graph | baseline | False | fusion | True | 85.79 | 97.50 | 86.88 | 6874.66 |
| data-science | entity-graph | baseline | False | entity | False | 80.82 | 96.67 | 79.67 | 7456.09 |
| data-science | entity-graph | baseline | False | lexical | False | 90.31 | 99.17 | 88.75 | 7199.18 |
| data-science | entity-graph | baseline | False | traversal | False | 51.20 | 79.58 | 43.55 | 7296.62 |
| enterprise | entity-graph | baseline | False | fusion | True | 46.73 | 58.04 | 47.33 | 49.85 |
| enterprise | entity-graph | baseline | False | entity | False | 45.25 | 56.58 | 46.67 | 55.74 |
| enterprise | entity-graph | baseline | False | lexical | False | 59.40 | 63.73 | 60.78 | 52.40 |
| enterprise | entity-graph | baseline | False | traversal | False | 43.27 | 50.33 | 46.04 | 64.66 |
