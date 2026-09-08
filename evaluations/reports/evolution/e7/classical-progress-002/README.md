# E7 development progress: Classical length normalization

Snapshot: 2026-09-08T18:13:46.964128+00:00. This family is still evolving.

**Classical improved by 2.06 percentage points** on its fixed primary fusion route. The fourth construction mutation sets `bm25.b=1.0`. Following two consecutive qualified misses, it replaces candidate001 and resets the miss counter. Its improvement over the previous retained result is 1.04 percentage points. Subsequent variants still have to complete.

| Arm | Weighted nDCG@10 | Weighted recall@10 | Weighted MRR@10 | Weighted full qrel coverage@10 |
| --- | ---: | ---: | ---: | ---: |
| baseline | 55.04 | 57.08 | 58.94 | 50.07 |
| candidate-004 | 57.10 | 58.79 | 61.76 | 51.92 |

Metric columns in both quality tables are percentages.

Among 112 eligible questions, 11 improved, 2 regressed and 99 tied on paired nDCG@10. These case counts are unweighted; the metric above uses the frozen category weights. Eight questions without references have no retrieval score.

| Diagnostic route | Baseline nDCG@10 | Candidate nDCG@10 | Change (percentage points) |
| --- | ---: | ---: | ---: |
| bm25 | 60.50 | 60.65 | +0.15 |
| topic | 55.02 | 57.08 | +2.06 |
| association | 55.02 | 57.08 | +2.06 |
| fusion | 55.04 | 57.10 | +2.06 |

The primary route remains fusion even when another route has a higher diagnostic score. Route diagnostics cannot change the frozen selection rule.

| Arm | Native job (seconds) | Double build and validation (seconds) | Knowledge (MiB) |
| --- | ---: | ---: | ---: |
| baseline | 1639.79 | 579.06 | 532.05 |
| candidate-004 | 1771.08 | 643.27 | 532.05 |

Both original jobs completed with evidence integrity 1.0, no execution errors and no retries. They remain below the separate 0.8 diagnostic reward threshold. That threshold does not determine qualification or development retention. Timing covers the original native jobs, excluding candidate staging and supervisor overhead. No language model calls were made.

Scope: 120 stratified development questions, 112 with qrels, category weights totaling 470 eligible public questions, and the same 6,000 reference-enriched complete documents. This exposed development result does not establish performance on the remaining public questions, an answer Overall score, or an official public rank.

The full family search, joint replay and freeze, all-500 comparison, and terminal private transfer gate remain pending. No retrieval profile is promoted.

[Exact aggregates and native evidence hashes](aggregate.json) · [First retained Classical gain](../classical-progress-001/README.md) · [Campaign](../README.md)
