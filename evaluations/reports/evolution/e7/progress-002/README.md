# E7 development progress: retained Legacy improvement

Partial snapshot at 2026-09-08T14:41:43.076447+00:00. The campaign is still running.

**Legacy improved by 11.02 percentage points** on the stratified development metric. The retained mutation uses the frozen BM25 comparator with k1=2.0. The candidate preserves authoritative records and physical evidence.

| Arm | Weighted nDCG@10 | Weighted recall@10 | Weighted MRR@10 | Evidence integrity | Execution errors |
| --- | ---: | ---: | ---: | ---: | ---: |
| baseline | 61.11% | 71.60% | 61.01% | 1.00 | 0 |
| candidate-003 | 72.13% | 82.11% | 71.06% | 1.00 | 0 |

Both native jobs completed with exact locked provenance and passed the required evidence-integrity gate. Neither reaches the separate 0.8 diagnostic reward threshold; that threshold is not the development selection rule. Selection retains strict qualified improvements and resets the three-miss counter after a gain.

Scope: 120 stratified questions, 112 with qrels, category weights totaling the 470 eligible public questions, and 6,000 reference-enriched complete documents. These are internal development results from one exposed source group. They are not official answer scores or full-corpus/public leaderboard comparisons.

The remaining variants and families, joint freeze, all-500 recalculation and terminal private gate are pending. No retrieval profile has been promoted from this snapshot.

[Exact aggregate and evidence hashes](aggregate.json) Â· [Campaign](../README.md)
