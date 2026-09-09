# E7 Adaptive: fifth development gain

Setting relevance weight to `1.0` and both novelty weights to `0.0` on the retained `bm25.k1=3.0`, title-weight `1.0`, association/topic-weight `0.175/0.1` base raised primary nDCG@10 to 66.21%. The gain is 0.85 percentage points over candidate-012 and 6.17 over the initial baseline. The controller retained candidate-014 and reset the consecutive-miss counter to zero.

| Configuration | Weighted nDCG@10 | Weighted recall@10 | Weighted MRR@10 | Weighted full qrel coverage@10 |
| --- | ---: | ---: | ---: | ---: |
| baseline | 60.04 | 69.19 | 60.70 | 62.39 |
| candidate-012 | 65.36 | 71.31 | 67.46 | 64.41 |
| candidate-014 | 66.21 | 74.02 | 67.37 | 69.27 |

Quality columns are percentages. The baseline, preceding incumbent and new retained candidate use the same original development questions, category weights and primary route.

Against baseline, 35 eligible questions improve, 12 regress and 65 tie; 8 questions without references remain outside retrieval scoring.

Against candidate-012, 27 eligible questions improve, 12 regress and 73 tie; 8 questions without references remain outside retrieval scoring.

The aggregate gain has material tradeoffs. Against candidate-012, recall gains 2.71 percentage points and full reference coverage gains 4.86, while MRR loses 0.0850 points. Fireflies falls from 80.52% to 69.60% nDCG; Gmail and Jira also regress. Confluence, GitHub, Google Drive, Hubspot, Linear and Slack improve. The fixed global nDCG objective retains candidate-014, while candidate-012 remains archived as complementary development evidence. This report does not select a different profile for each application.

The preceding expansion catalog ended with a miss after the candidate-012 gain. The first relevance-diversity variant now improves and leaves its counter at zero. The next declared variant tests relevance weight `0.9` and both novelty weights approximately `0.05` on this retained base. The exact floating-point settings are preserved in the aggregate and next sealed contract.

The exact fourteen-variant prefix was replayed against the frozen scheduler, native archives and staged profiles. Every recorded event, score, counter and retained profile matched; the next mutation also matched its sealed contract. The [category and application breakdown](subgroups.md) preserves matching denominators and individual regressions.

| Configuration | Native job minutes | Double build and validation minutes | Knowledge MiB | Query P95 ms |
| --- | ---: | ---: | ---: | ---: |
| baseline | 23.13 | 9.82 | 532.05 | 8415.33 |
| candidate-012 | 22.79 | 9.61 | 532.05 | 8579.67 |
| candidate-014 | 23.00 | 9.63 | 532.05 | 8286.94 |

All three original jobs completed with evidence integrity 1.0, no errors and no retries. The separate native diagnostic threshold is 0.8. Durations are original job observations, not campaign wall time, all attempted search time or an invoice. No evaluation was rerun for this report and no language model calls were made.

Scope: 120 stratified development questions, 112 retrieval-eligible questions, eligible population weight 470 and 6,000 reference-enriched complete documents. The family search, all-500 comparison and whole-bundle gates remain pending. No canonical profile is promoted and no answer Overall or official leaderboard rank is established.

[Exact aggregates and evidence hashes](aggregate.json) · [Previous Adaptive gain](../adaptive-progress-004/README.md) · [Campaign](../README.md)
