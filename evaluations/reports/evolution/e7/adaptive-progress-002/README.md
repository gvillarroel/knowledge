# E7 development progress: Adaptive BM25 saturation

Snapshot: 2026-09-08T21:51:36.015843+00:00. This family is still evolving.

**Adaptive improved by 1.46 percentage points** on its fixed primary adaptive route. The sixth construction mutation sets `bm25.k1=3.0`. Following the preceding saturation gain, it replaces candidate005 and resets the miss counter. Its improvement over the previous retained result is 0.34 percentage points. Subsequent variants still have to complete.

| Arm | Weighted nDCG@10 | Weighted recall@10 | Weighted MRR@10 | Weighted full qrel coverage@10 |
| --- | ---: | ---: | ---: | ---: |
| baseline | 60.04 | 69.19 | 60.70 | 62.39 |
| candidate-006 | 61.49 | 70.48 | 62.41 | 63.57 |

Metric columns are percentages.

Among 112 eligible questions, 24 improved, 6 regressed and 82 tied on paired nDCG@10. These case counts are unweighted; the metric above uses the frozen category weights. Eight questions without references have no retrieval score.

Against the previous retained candidate-005, 11 eligible questions improve, 2 regress and 99 tie. This second comparison uses the incumbent as its reference; the metric table uses the initial baseline.

The saturation catalog has used its three declared values, 0.6, 2.0 and 3.0. It ends with a gain and a reset counter. The transition to title weighting follows catalog exhaustion, not three consecutive misses.

The frozen primary route is `adaptive`.

| Arm | Native job (seconds) | Double build and validation (seconds) | Knowledge (MiB) |
| --- | ---: | ---: | ---: |
| baseline | 1388.00 | 589.04 | 532.05 |
| candidate-006 | 1363.60 | 582.38 | 532.05 |

Both original jobs completed with evidence integrity 1.0, no execution errors and no retries. They remain below the separate 0.8 diagnostic reward threshold. That threshold does not determine qualification or development retention. Timing covers the original native jobs, excluding candidate staging and supervisor overhead. No language model calls were made.

Scope: 120 stratified development questions, 112 with qrels, category weights totaling 470 eligible public questions, and the same 6,000 reference-enriched complete documents. This exposed development result does not establish performance on the remaining public questions, an answer Overall score, or an official public rank.

The full family search, joint replay and freeze, all-500 comparison, and terminal private transfer gate remain pending. No retrieval profile is promoted.

[Exact aggregates and native evidence hashes](aggregate.json) · [Category and application breakdown](subgroups.md) · [Previous retained Adaptive gain](../adaptive-progress-001/README.md) · [Campaign](../README.md)
