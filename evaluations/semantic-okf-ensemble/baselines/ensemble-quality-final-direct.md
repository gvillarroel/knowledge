# Direct Retrieval Replay: ensemble-quality-real-postfix

Status: **pass**. Route: `ensemble_quality`. This report recomputes metrics from retained hits; route provenance is determined by the bound raw report.

| Cohort / identity | Recall@1 | Recall@3 | Recall@5 | Recall@10 | MRR@10 | nDCG@10 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| all_40 / paper | 15.97% | 39.02% | 54.30% | 83.82% | 98.75% | 84.78% |
| all_40 / source | 7.98% | 19.51% | 27.15% | 41.91% | 98.75% | 67.73% |
| original_30 / paper | 13.12% | 32.08% | 50.80% | 79.92% | 100.00% | 84.39% |
| original_30 / source | 6.56% | 16.04% | 25.40% | 39.96% | 100.00% | 71.77% |
| hard_10 / paper | 24.50% | 59.83% | 64.83% | 95.50% | 95.00% | 85.94% |
| hard_10 / source | 12.25% | 29.92% | 32.42% | 47.75% | 95.00% | 55.61% |

Evidence validity: **100.00%** (400/400). Mean/median/p95 query time: 935.06/822.94/992.84 ms.

## Paper-level deltas versus the frozen adaptive incumbent

| Cohort | Recall@10 | MRR@10 | nDCG@10 |
| --- | ---: | ---: | ---: |
| all_40 | -0.0000% | +2.9167% | +1.3480% |
| hard_10 | +0.0000% | +0.0000% | +0.9591% |
