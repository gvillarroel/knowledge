# Native route diagnostics

[Family report](README.md)

| Route | Candidate | Weighted nDCG@10 | Recall@10 | MRR@10 | Full evidence@10 |
| --- | --- | ---: | ---: | ---: | ---: |
| bm25 | baseline | 60.50 | 67.41 | 61.67 | 60.85 |
| bm25 | continuation-002 | 65.90 | 74.40 | 66.74 | 69.04 |
| bm25 | continuation-014 | 45.50 | 61.63 | 42.66 | 54.91 |
| topic | baseline | 55.02 | 57.08 | 58.91 | 50.07 |
| topic | continuation-002 | 62.10 | 64.17 | 66.38 | 57.82 |
| topic | continuation-014 | 38.95 | 46.71 | 40.47 | 39.74 |
| association | baseline | 55.02 | 57.08 | 58.91 | 50.07 |
| association | continuation-002 | 62.10 | 64.17 | 66.38 | 57.82 |
| association | continuation-014 | 38.95 | 46.71 | 40.47 | 39.74 |
| fusion | baseline | 55.04 | 57.08 | 58.94 | 50.07 |
| fusion | continuation-002 | 62.10 | 64.17 | 66.38 | 57.82 |
| fusion | continuation-014 | 38.95 | 46.71 | 40.47 | 39.74 |
