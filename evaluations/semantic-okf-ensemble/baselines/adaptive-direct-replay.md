# Direct Retrieval Replay: adaptive-fusion-reference

Status: **pass**. Route: `adaptive_fusion`. This report recomputes metrics from retained hits; route provenance is determined by the bound raw report.

| Cohort / identity | Recall@1 | Recall@3 | Recall@5 | Recall@10 | MRR@10 | nDCG@10 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| all_40 / paper | 15.38% | 38.45% | 51.64% | 83.82% | 95.83% | 83.43% |
| all_40 / source | 7.69% | 19.23% | 25.82% | 41.91% | 95.83% | 66.68% |
| original_30 / paper | 12.34% | 32.16% | 47.25% | 79.92% | 96.11% | 82.91% |
| original_30 / source | 6.17% | 16.08% | 23.62% | 39.96% | 96.11% | 70.58% |
| hard_10 / paper | 24.50% | 57.33% | 64.83% | 95.50% | 95.00% | 84.98% |
| hard_10 / source | 12.25% | 28.67% | 32.42% | 47.75% | 95.00% | 54.99% |

Evidence validity: **100.00%** (400/400). Mean/median/p95 query time: 296.45/290.59/407.56 ms.

## Paper-level deltas versus the frozen adaptive incumbent

| Cohort | Recall@10 | MRR@10 | nDCG@10 |
| --- | ---: | ---: | ---: |
| all_40 | -0.0000% | +0.0000% | -0.0000% |
| hard_10 | +0.0000% | +0.0000% | +0.0000% |
