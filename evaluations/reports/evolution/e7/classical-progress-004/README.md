# E7 development progress: Classical BM25 saturation

Snapshot: 2026-09-08T19:43:45.881637+00:00. This family is still evolving.

**Classical improved by 3.63 percentage points** on its fixed primary fusion route. The seventh construction mutation sets `bm25.k1=3.0` on the retained `bm25.b=1.0` base. As a second consecutive saturation gain, it replaces candidate006 and resets the miss counter. Its improvement over the previous retained result is 0.43 percentage points. Subsequent variants still have to complete.

| Arm | Weighted nDCG@10 | Weighted recall@10 | Weighted MRR@10 | Weighted full qrel coverage@10 |
| --- | ---: | ---: | ---: | ---: |
| baseline | 55.04 | 57.08 | 58.94 | 50.07 |
| candidate-007 | 58.67 | 62.11 | 62.86 | 54.84 |

Metric columns in both quality tables are percentages.

Among 112 eligible questions, 15 improved, 8 regressed and 89 tied on paired nDCG@10. These case counts are unweighted; the metric above uses the frozen category weights. Eight questions without references have no retrieval score.

The [paired category and application breakdown](subgroups.md) includes every question category, all nine overlapping application groups, and each category's contribution to the overall gain.

| Diagnostic route | Baseline nDCG@10 | Candidate nDCG@10 | Change (percentage points) |
| --- | ---: | ---: | ---: |
| bm25 | 60.50 | 61.54 | +1.04 |
| topic | 55.02 | 58.65 | +3.64 |
| association | 55.02 | 58.65 | +3.64 |
| fusion | 55.04 | 58.67 | +3.63 |

The primary route remains fusion even when another route has a higher diagnostic score. Route diagnostics cannot change the frozen selection rule.

| Arm | Native job (seconds) | Double build and validation (seconds) | Knowledge (MiB) |
| --- | ---: | ---: | ---: |
| baseline | 1639.79 | 579.06 | 532.05 |
| candidate-007 | 1622.31 | 585.02 | 532.05 |

Both original jobs completed with evidence integrity 1.0, no execution errors and no retries. They remain below the separate 0.8 diagnostic reward threshold. That threshold does not determine qualification or development retention. Timing covers the original native jobs, excluding candidate staging and supervisor overhead. No language model calls were made.

Scope: 120 stratified development questions, 112 with qrels, category weights totaling 470 eligible public questions, and the same 6,000 reference-enriched complete documents. This exposed development result does not establish performance on the remaining public questions, an answer Overall score, or an official public rank.

The full family search, joint replay and freeze, all-500 comparison, and terminal private transfer gate remain pending. No retrieval profile is promoted.

[Exact aggregates and native evidence hashes](aggregate.json) · [Previous retained Classical gain](../classical-progress-003/README.md) · [Campaign](../README.md)
