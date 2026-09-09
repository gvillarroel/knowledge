# Native route diagnostics

[Family report](README.md)

| Route | Candidate | Weighted nDCG@10 | Recall@10 | MRR@10 | Full evidence@10 |
| --- | --- | ---: | ---: | ---: | ---: |
| bm25 | baseline | 60.50 | 67.41 | 61.67 | 60.85 |
| bm25 | continuation-002 | 65.90 | 74.40 | 66.74 | 69.04 |
| bm25 | continuation-013 | 54.19 | 67.03 | 53.73 | 59.79 |
| topic | baseline | 55.02 | 57.08 | 58.91 | 50.07 |
| topic | continuation-002 | 62.10 | 64.17 | 66.38 | 57.82 |
| topic | continuation-013 | 49.18 | 54.93 | 52.04 | 48.19 |
| association | baseline | 55.02 | 57.08 | 58.91 | 50.07 |
| association | continuation-002 | 62.10 | 64.17 | 66.38 | 57.82 |
| association | continuation-013 | 49.18 | 54.93 | 52.04 | 48.19 |
| fusion | baseline | 55.04 | 57.08 | 58.94 | 50.07 |
| fusion | continuation-002 | 62.10 | 64.17 | 66.38 | 57.82 |
| fusion | continuation-013 | 49.18 | 54.93 | 52.04 | 48.19 |
