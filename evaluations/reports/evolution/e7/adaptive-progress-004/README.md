# E7 Adaptive: fourth development gain

Setting association weight to `0.175` and topic weight to `0.1` on the retained `bm25.k1=3.0`, title-weight `1.0` base raised primary nDCG@10 to 65.36%. The gain is 0.13 percentage points over candidate-009 and 5.33 over the initial baseline. The controller retained candidate-012 and reset the consecutive-miss counter to zero.

| Configuration | Weighted nDCG@10 | Weighted recall@10 | Weighted MRR@10 | Weighted full qrel coverage@10 |
| --- | ---: | ---: | ---: | ---: |
| baseline | 60.04 | 69.19 | 60.70 | 62.39 |
| candidate-009 | 65.23 | 71.23 | 67.33 | 64.41 |
| candidate-012 | 65.36 | 71.31 | 67.46 | 64.41 |

Quality columns are percentages. The baseline, preceding incumbent and new retained candidate use the same original development questions, category weights and primary route.

Against baseline, 30 eligible questions improve, 5 regress and 77 tie; 8 questions without references remain outside retrieval scoring.

Against candidate-009, 5 eligible questions improve, 1 regress and 106 tie; 8 questions without references remain outside retrieval scoring.

The preceding expansion variants, association/topic weights `0.0875/0.05` and `0/0`, produced qualified misses. The third tested variant, `0.175/0.1`, improved and reset the counter. The mechanism continues to its last declared setting, `0.7/0.4`, on the newly retained base. Neither a three-miss stop nor catalog exhaustion occurred at this transition.

The exact twelve-variant prefix was replayed against the frozen scheduler, native archives and staged profiles. Every recorded event, score, counter and retained profile matched; the next mutation also matched its sealed contract. The [category and application breakdown](subgroups.md) preserves matching denominators and individual regressions.

| Configuration | Native job minutes | Double build and validation minutes | Knowledge MiB | Query P95 ms |
| --- | ---: | ---: | ---: | ---: |
| baseline | 23.13 | 9.82 | 532.05 | 8415.33 |
| candidate-009 | 22.92 | 9.74 | 532.05 | 8382.58 |
| candidate-012 | 22.79 | 9.61 | 532.05 | 8579.67 |

All three original jobs completed with evidence integrity 1.0, no errors and no retries. The separate native diagnostic threshold is 0.8. Durations are original job observations, not campaign wall time, all attempted search time or an invoice. No evaluation was rerun for this report and no language model calls were made.

Scope: 120 stratified development questions, 112 retrieval-eligible questions, eligible population weight 470 and 6,000 reference-enriched complete documents. The family search, all-500 comparison and whole-bundle gates remain pending. No canonical profile is promoted and no answer Overall or official leaderboard rank is established.

[Exact aggregates and evidence hashes](aggregate.json) · [Previous Adaptive gain](../adaptive-progress-003/README.md) · [Campaign](../README.md)
