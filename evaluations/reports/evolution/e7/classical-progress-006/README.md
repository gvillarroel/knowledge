# E7 development progress: Classical expansion strength

Snapshot: 2026-09-08T21:43:21.567666+00:00. This family is still evolving.

**Classical improved by 5.06 percentage points** on its fixed primary fusion route. The eleventh construction mutation sets `expansion.association_weight=0.0875` and `expansion.topic_weight=0.05` on the retained `bm25.b=1.0`, `bm25.k1=3.0`, `bm25.title_weight=1.0` base. Following the preceding title-weight gain, it replaces candidate010 and resets the miss counter. Its improvement over the previous retained result is 0.08 percentage points. Subsequent variants still have to complete.

| Arm | Weighted nDCG@10 | Weighted recall@10 | Weighted MRR@10 | Weighted full qrel coverage@10 |
| --- | ---: | ---: | ---: | ---: |
| baseline | 55.04 | 57.08 | 58.94 | 50.07 |
| candidate-011 | 60.10 | 63.59 | 63.88 | 56.91 |

Metric columns in both quality tables are percentages.

Among 112 eligible questions, 19 improved, 10 regressed and 83 tied on paired nDCG@10. These case counts are unweighted; the metric above uses the frozen category weights. Eight questions without references have no retrieval score.

Against the previous retained candidate-010, 2 eligible questions improve, 0 regress and 110 tie. This second paired comparison uses the incumbent as its reference; the metric and diagnostic tables use the initial baseline.

This first expansion-strength variant gains only 0.0831 percentage points over the incumbent. It is a measured development increment, with no statistical or transfer claim. The next declared variant sets both expansion weights to zero; the mechanism and family search remain in progress.

| Diagnostic route | Baseline nDCG@10 | Candidate nDCG@10 | Change (percentage points) |
| --- | ---: | ---: | ---: |
| bm25 | 60.50 | 65.06 | +4.56 |
| topic | 55.02 | 60.10 | +5.08 |
| association | 55.02 | 60.10 | +5.08 |
| fusion | 55.04 | 60.10 | +5.06 |

The primary route remains fusion even when another route has a higher diagnostic score. Route diagnostics cannot change the frozen selection rule.

| Arm | Native job (seconds) | Double build and validation (seconds) | Knowledge (MiB) |
| --- | ---: | ---: | ---: |
| baseline | 1639.79 | 579.06 | 532.05 |
| candidate-011 | 1616.42 | 566.89 | 532.05 |

Both original jobs completed with evidence integrity 1.0, no execution errors and no retries. They remain below the separate 0.8 diagnostic reward threshold. That threshold does not determine qualification or development retention. Timing covers the original native jobs, excluding candidate staging and supervisor overhead. No language model calls were made.

Scope: 120 stratified development questions, 112 with qrels, category weights totaling 470 eligible public questions, and the same 6,000 reference-enriched complete documents. This exposed development result does not establish performance on the remaining public questions, an answer Overall score, or an official public rank.

The full family search, joint replay and freeze, all-500 comparison, and terminal private transfer gate remain pending. No retrieval profile is promoted.

[Exact aggregates and native evidence hashes](aggregate.json) · [Category and application breakdown](subgroups.md) · [Previous retained Classical gain](../classical-progress-005/README.md) · [Campaign](../README.md)
