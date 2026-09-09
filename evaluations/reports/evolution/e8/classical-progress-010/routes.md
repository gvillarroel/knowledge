# Native route diagnostics

[Family report](README.md)

| Route | Candidate | Weighted nDCG@10 | Recall@10 | MRR@10 | Full evidence@10 |
| --- | --- | ---: | ---: | ---: | ---: |
| bm25 | baseline | 60.50 | 67.41 | 61.67 | 60.85 |
| bm25 | continuation-002 | 65.90 | 74.40 | 66.74 | 69.04 |
| bm25 | continuation-010 | 65.83 | 75.46 | 66.51 | 70.29 |
| topic | baseline | 55.02 | 57.08 | 58.91 | 50.07 |
| topic | continuation-002 | 62.10 | 64.17 | 66.38 | 57.82 |
| topic | continuation-010 | 60.39 | 62.32 | 64.82 | 55.36 |
| association | baseline | 55.02 | 57.08 | 58.91 | 50.07 |
| association | continuation-002 | 62.10 | 64.17 | 66.38 | 57.82 |
| association | continuation-010 | 60.39 | 62.32 | 64.82 | 55.36 |
| fusion | baseline | 55.04 | 57.08 | 58.94 | 50.07 |
| fusion | continuation-002 | 62.10 | 64.17 | 66.38 | 57.82 |
| fusion | continuation-010 | 60.39 | 62.32 | 64.82 | 55.36 |
