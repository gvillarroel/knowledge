# Direct Retrieval Replay: ensemble-quality-population-winner

Status: **pass**. Route: `ensemble_quality`. This report recomputes metrics from retained hits; route provenance is determined by the bound raw report.

| Cohort / identity | Recall@1 | Recall@3 | Recall@5 | Recall@10 | MRR@10 | nDCG@10 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| all_40 / paper | 16.59% | 38.49% | 53.79% | 83.82% | 100.00% | 85.20% |
| all_40 / source | 8.30% | 19.24% | 26.90% | 41.91% | 100.00% | 67.97% |
| original_30 / paper | 13.12% | 31.37% | 50.11% | 79.92% | 100.00% | 84.18% |
| original_30 / source | 6.56% | 15.69% | 25.06% | 39.96% | 100.00% | 71.58% |
| hard_10 / paper | 27.00% | 59.83% | 64.83% | 95.50% | 100.00% | 88.27% |
| hard_10 / source | 13.50% | 29.92% | 32.42% | 47.75% | 100.00% | 57.11% |

Evidence validity: **100.00%** (400/400). Mean/median/p95 query time: 1453.97/1173.40/1461.92 ms.

## Paper-level deltas versus the frozen adaptive incumbent

| Cohort | Recall@10 | MRR@10 | nDCG@10 |
| --- | ---: | ---: | ---: |
| all_40 | -0.0000% | +4.1667% | +1.7729% |
| hard_10 | +0.0000% | +5.0000% | +3.2854% |
