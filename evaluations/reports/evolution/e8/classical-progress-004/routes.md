# Native route diagnostics

[Family report](README.md)

| Route | Candidate | Weighted nDCG@10 | Recall@10 | MRR@10 | Full evidence@10 |
| --- | --- | ---: | ---: | ---: | ---: |
| bm25 | baseline | 60.50 | 67.41 | 61.67 | 60.85 |
| bm25 | continuation-002 | 65.90 | 74.40 | 66.74 | 69.04 |
| bm25 | continuation-004 | 65.90 | 74.40 | 66.74 | 69.04 |
| topic | baseline | 55.02 | 57.08 | 58.91 | 50.07 |
| topic | continuation-002 | 62.10 | 64.17 | 66.38 | 57.82 |
| topic | continuation-004 | 60.47 | 63.51 | 64.63 | 57.48 |
| association | baseline | 55.02 | 57.08 | 58.91 | 50.07 |
| association | continuation-002 | 62.10 | 64.17 | 66.38 | 57.82 |
| association | continuation-004 | 60.67 | 63.51 | 64.90 | 57.48 |
| fusion | baseline | 55.04 | 57.08 | 58.94 | 50.07 |
| fusion | continuation-002 | 62.10 | 64.17 | 66.38 | 57.82 |
| fusion | continuation-004 | 60.13 | 62.04 | 64.60 | 55.93 |
