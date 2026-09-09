# E7 Classical: seventh development gain

Setting `bm25.b=0.5` on the retained `bm25.k1=3.0`, title-weight `1.0`, association/topic-weight `0.0875/0.05` base raised primary fusion nDCG@10 to 60.89%. The gain is 0.79 percentage points over candidate-011 and 5.85 over the initial baseline. The controller retained candidate-020 and reset the consecutive-miss counter to zero.

| Configuration | Weighted nDCG@10 | Weighted recall@10 | Weighted MRR@10 | Weighted full qrel coverage@10 |
| --- | ---: | ---: | ---: | ---: |
| baseline | 55.04 | 57.08 | 58.94 | 50.07 |
| candidate-011 | 60.10 | 63.59 | 63.88 | 56.91 |
| candidate-020 | 60.89 | 63.26 | 65.01 | 56.99 |

Quality columns are percentages. The baseline, preceding incumbent and new retained candidate use the same original development questions, category weights and primary route.

Against baseline, 18 eligible questions improve, 5 regress and 89 tie; 8 questions without references remain outside retrieval scoring.

Against candidate-011, 13 eligible questions improve, 13 regress and 86 tie; 8 questions without references remain outside retrieval scoring.

Compared with candidate-011, recall changes by -0.3292 percentage points, MRR by +1.1325 and full reference coverage by +0.0776. The primary objective remains the preregistered global weighted nDCG.

Application-level nDCG declines against candidate-011 occur in github (-2.30 points), gmail (-2.71 points), google_drive (-1.51 points), linear (-0.29 points). All application means and paired counts remain in the subgroup report; no per-application profile is selected.

This second-round gain follows two qualified length-normalization misses and resets the counter. The remaining `bm25.b=1.0` setting reconstructs the already evaluated candidate-011 profile and is skipped as a duplicate, without a new native trial or miss. The length-normalization catalog then ends, and the next sealed variant tests `bm25.k1=0.6` on the new retained base.

The exact twenty-variant prefix was replayed against the frozen scheduler, native archives and staged profiles. Every recorded event, score, counter and retained profile matched; the next mutation also matched its sealed contract. The [category and application breakdown](subgroups.md) preserves matching denominators and individual regressions.

| Configuration | Native job minutes | Double build and validation minutes | Knowledge MiB | Query P95 ms |
| --- | ---: | ---: | ---: | ---: |
| baseline | 27.33 | 9.65 | 532.05 | 2189.65 |
| candidate-011 | 26.94 | 9.45 | 532.05 | 2189.12 |
| candidate-020 | 26.84 | 9.39 | 532.05 | 2285.89 |

All three original jobs completed with evidence integrity 1.0, no errors and no retries. The separate native diagnostic threshold is 0.8. Durations are original job observations, not campaign wall time, all attempted search time or an invoice. No evaluation was rerun for this report and no language model calls were made.

Scope: 120 stratified development questions, 112 retrieval-eligible questions, eligible population weight 470 and 6,000 reference-enriched complete documents. The family search, all-500 comparison and whole-bundle gates remain pending. No canonical profile is promoted and no answer Overall or official leaderboard rank is established.

[Exact aggregates and evidence hashes](aggregate.json) · [Previous Classical gain](../classical-progress-006/README.md) · [Campaign](../README.md)
