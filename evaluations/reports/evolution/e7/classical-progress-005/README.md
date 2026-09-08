# E7 development progress: Classical title weighting

Snapshot: 2026-09-08T21:11:51.848158+00:00. This family is still evolving.

**Classical improved by 4.97 percentage points** on its fixed primary fusion route. The tenth construction mutation sets `bm25.title_weight=1.0` on the retained `bm25.b=1.0` and `bm25.k1=3.0` base. Following two consecutive qualified title-weight misses, it replaces candidate007 and resets the miss counter. Its improvement over the previous retained result is 1.34 percentage points. Subsequent variants still have to complete.

| Arm | Weighted nDCG@10 | Weighted recall@10 | Weighted MRR@10 | Weighted full qrel coverage@10 |
| --- | ---: | ---: | ---: | ---: |
| baseline | 55.04 | 57.08 | 58.94 | 50.07 |
| candidate-010 | 60.01 | 63.59 | 63.72 | 56.91 |

Metric columns in both quality tables are percentages.

Among 112 eligible questions, 19 improved, 10 regressed and 83 tied on paired nDCG@10. These case counts are unweighted; the metric above uses the frozen category weights. Eight questions without references have no retrieval score.

Against the previous retained candidate-007, 9 eligible questions improve, 7 regress and 96 tie. This second paired comparison uses the incumbent as its reference; the metric and diagnostic tables use the initial baseline.

The title-weight catalog has now used all three declared settings, 4.0, 8.0 and 1.0. Its last setting improves and resets the miss counter. The move to the next mechanism follows catalog exhaustion, not three consecutive misses.

| Diagnostic route | Baseline nDCG@10 | Candidate nDCG@10 | Change (percentage points) |
| --- | ---: | ---: | ---: |
| bm25 | 60.50 | 65.06 | +4.56 |
| topic | 55.02 | 60.01 | +5.00 |
| association | 55.02 | 60.01 | +5.00 |
| fusion | 55.04 | 60.01 | +4.97 |

The primary route remains fusion even when another route has a higher diagnostic score. Route diagnostics cannot change the frozen selection rule.

| Arm | Native job (seconds) | Double build and validation (seconds) | Knowledge (MiB) |
| --- | ---: | ---: | ---: |
| baseline | 1639.79 | 579.06 | 532.05 |
| candidate-010 | 1600.67 | 567.94 | 532.05 |

Both original jobs completed with evidence integrity 1.0, no execution errors and no retries. They remain below the separate 0.8 diagnostic reward threshold. That threshold does not determine qualification or development retention. Timing covers the original native jobs, excluding candidate staging and supervisor overhead. No language model calls were made.

Scope: 120 stratified development questions, 112 with qrels, category weights totaling 470 eligible public questions, and the same 6,000 reference-enriched complete documents. This exposed development result does not establish performance on the remaining public questions, an answer Overall score, or an official public rank.

The full family search, joint replay and freeze, all-500 comparison, and terminal private transfer gate remain pending. No retrieval profile is promoted.

[Exact aggregates and native evidence hashes](aggregate.json) · [Category and application breakdown](subgroups.md) · [Previous retained Classical gain](../classical-progress-004/README.md) · [Campaign](../README.md)
