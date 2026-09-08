# E7 Adaptive: third development gain

Reducing the title weight to `1.0` on the retained `bm25.k1=3.0` base raised primary nDCG@10 to 65.23%. The gain is 3.74 percentage points over candidate-006 and 5.20 over the initial baseline. The controller retained candidate-009 and reset the consecutive-miss counter to zero.

| Configuration | Weighted nDCG@10 | Weighted recall@10 | Weighted MRR@10 | Weighted full qrel coverage@10 |
| --- | ---: | ---: | ---: | ---: |
| baseline | 60.04 | 69.19 | 60.70 | 62.39 |
| candidate-006 | 61.49 | 70.48 | 62.41 | 63.57 |
| candidate-009 | 65.23 | 71.23 | 67.33 | 64.41 |

Quality columns are percentages. The baseline, preceding incumbent and new retained candidate use the same original development questions, category weights and primary route.

Against baseline, 29 eligible questions improve, 6 regress and 77 tie; 8 questions without references remain outside retrieval scoring.

Against candidate-006, 19 eligible questions improve, 6 regress and 87 tie; 8 questions without references remain outside retrieval scoring.

The preceding title weights `4.0` and `8.0` produced qualified misses. The third value `1.0` improved, so this mechanism ends by exhausting its declared catalog with a reset counter. It did not end after three misses. The next sealed mutation tests association weight `0.0875` and topic weight `0.05` on the newly retained base.

The exact nine-variant prefix was replayed against the frozen scheduler, native archives and staged profiles. Every recorded event, score, counter and retained profile matched; the next mutation also matched its sealed contract. The [category and application breakdown](subgroups.md) preserves matching denominators and individual regressions.

| Configuration | Native job minutes | Double build and validation minutes | Knowledge MiB | Query P95 ms |
| --- | ---: | ---: | ---: | ---: |
| baseline | 23.13 | 9.82 | 532.05 | 8415.33 |
| candidate-006 | 22.73 | 9.71 | 532.05 | 8278.94 |
| candidate-009 | 22.92 | 9.74 | 532.05 | 8382.58 |

All three original jobs completed with evidence integrity 1.0, no errors and no retries. The separate native diagnostic threshold is 0.8. Durations are original job observations, not campaign wall time, all attempted search time or an invoice. No evaluation was rerun for this report and no language model calls were made.

Scope: 120 stratified development questions, 112 retrieval-eligible questions, eligible population weight 470 and 6,000 reference-enriched complete documents. The family search, all-500 comparison and whole-bundle gates remain pending. No canonical profile is promoted and no answer Overall or official leaderboard rank is established.

[Exact aggregates and evidence hashes](aggregate.json) · [Previous Adaptive gain](../adaptive-progress-002/README.md) · [Campaign](../README.md)
