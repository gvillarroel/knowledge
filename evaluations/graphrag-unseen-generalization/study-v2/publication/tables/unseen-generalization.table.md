# Post-v51 unseen-question retrieval ranking

Scope: twenty questions written after all candidates were frozen, over the
same fifteen-paper corpus. Values are medians of three independent process
runs. Stable queries is the share whose complete Top-10 paper order was
identical in all three runs.

| Pos. | Frozen expert strategy | Recall@10 | MRR@10 | nDCG@10 | Stable queries | P95 |
|---:|---|---:|---:|---:|---:|---:|
| 1 | `v43-fielded-bm25` | 100.00% | 100.00% | 99.26% | 100.00% | 136.27 ms |
| 2 | `v48-ensemble-quality-trace` | 100.00% | 97.50% | 98.22% | 100.00% | 3972.52 ms |
| 3 | `v46-ensemble-quality` | 100.00% | 97.50% | 97.92% | 100.00% | 3827.99 ms |
| 4 | `v44-classical-hybrid` | 100.00% | 97.50% | 97.52% | 100.00% | 867.98 ms |
| 5 | `v45-early-confidence` | 100.00% | 97.50% | 97.52% | 100.00% | 868.23 ms |
| 6 | `v51-supervised-profiles` | 88.33% | 44.90% | 52.36% | 20.00% | 61.90 ms |
| 7 | `v39-default-lexical` | 72.08% | 24.39% | 34.85% | 100.00% | 95.21 ms |

All candidates returned exact authoritative evidence and completed every
query without error.

This study measures same-corpus unseen-query retrieval, not unseen-corpus or
generated-answer generalization. Expected answers bind to previously reviewed
claims and source pages, but did not receive a new independent human
adjudication.
