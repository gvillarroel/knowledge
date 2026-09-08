# E7 development progress: Adaptive BM25 saturation

Snapshot: 2026-09-08T21:24:52.266006+00:00. This family is still evolving.

**Adaptive improved by 1.12 percentage points** on its fixed primary adaptive route. The fifth construction mutation sets `bm25.k1=2.0`. Following one qualified saturation miss, it replaces the initial baseline and resets the miss counter. Its improvement over the previous retained result is 1.12 percentage points. Subsequent variants still have to complete.

| Arm | Weighted nDCG@10 | Weighted recall@10 | Weighted MRR@10 | Weighted full qrel coverage@10 |
| --- | ---: | ---: | ---: | ---: |
| baseline | 60.04 | 69.19 | 60.70 | 62.39 |
| candidate-005 | 61.15 | 69.83 | 62.08 | 62.51 |

Metric columns are percentages.

Among 112 eligible questions, 18 improved, 7 regressed and 87 tied on paired nDCG@10. These case counts are unweighted; the metric above uses the frozen category weights. Eight questions without references have no retrieval score.

The frozen primary route is `adaptive`.

| Arm | Native job (seconds) | Double build and validation (seconds) | Knowledge (MiB) |
| --- | ---: | ---: | ---: |
| baseline | 1388.00 | 589.04 | 532.05 |
| candidate-005 | 1353.92 | 582.60 | 532.05 |

Both original jobs completed with evidence integrity 1.0, no execution errors and no retries. They remain below the separate 0.8 diagnostic reward threshold. That threshold does not determine qualification or development retention. Timing covers the original native jobs, excluding candidate staging and supervisor overhead. No language model calls were made.

Scope: 120 stratified development questions, 112 with qrels, category weights totaling 470 eligible public questions, and the same 6,000 reference-enriched complete documents. This exposed development result does not establish performance on the remaining public questions, an answer Overall score, or an official public rank.

The full family search, joint replay and freeze, all-500 comparison, and terminal private transfer gate remain pending. No retrieval profile is promoted.

[Exact aggregates and native evidence hashes](aggregate.json) · [Category and application breakdown](subgroups.md) · [Initial Adaptive baseline](../adaptive-baseline-001/README.md) · [Campaign](../README.md)
