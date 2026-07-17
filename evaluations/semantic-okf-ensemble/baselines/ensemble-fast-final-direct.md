# Direct Retrieval Replay: ensemble-fast-real-final

Status: **pass**. Route: `ensemble_fast`. This report recomputes metrics from retained hits; route provenance is determined by the bound raw report.

| Cohort / identity | Recall@1 | Recall@3 | Recall@5 | Recall@10 | MRR@10 | nDCG@10 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| all_40 / paper | 15.74% | 38.45% | 52.69% | 83.82% | 97.50% | 84.30% |
| all_40 / source | 7.87% | 19.23% | 26.34% | 41.91% | 97.50% | 67.35% |
| original_30 / paper | 12.82% | 32.16% | 47.80% | 79.92% | 98.33% | 83.86% |
| original_30 / source | 6.41% | 16.08% | 23.90% | 39.96% | 98.33% | 71.33% |
| hard_10 / paper | 24.50% | 57.33% | 67.33% | 95.50% | 95.00% | 85.62% |
| hard_10 / source | 12.25% | 28.67% | 33.67% | 47.75% | 95.00% | 55.40% |

Evidence validity: **100.00%** (400/400). Mean/median/p95 query time: 423.96/419.45/521.76 ms.

## Paper-level deltas versus the frozen adaptive incumbent

| Cohort | Recall@10 | MRR@10 | nDCG@10 |
| --- | ---: | ---: | ---: |
| all_40 | -0.0000% | +1.6667% | +0.8776% |
| hard_10 | +0.0000% | +0.0000% | +0.6401% |
