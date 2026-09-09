# E7 Adaptive: a recall gain with a ranking loss

Candidate-013 tests association weight `0.7` and topic weight `0.4` on the retained `bm25.k1=3.0`, title-weight `1.0` base. Recall and full reference coverage rise, but primary nDCG and MRR fall. The controller retains candidate-012 and records the first miss after that retained gain. The expansion catalog is now exhausted.

| Configuration | Weighted nDCG@10 | Weighted recall@10 | Weighted MRR@10 | Weighted full qrel coverage@10 |
| --- | ---: | ---: | ---: | ---: |
| candidate-012 | 65.36 | 71.31 | 67.46 | 64.41 |
| candidate-013 | 65.03 | 72.10 | 66.77 | 65.95 |
| Change in percentage points | -0.3298 | +0.7878 | -0.6898 | +1.5403 |

Metric columns are percentages; the last row is a paired aggregate difference in percentage points. The frozen selection objective remains primary nDCG@10. A gain in a secondary metric does not replace that objective after observing the result.

Against candidate-012, eligible question counts are 5 improved, 11 regressed and 96 tied in nDCG. Eight questions without references remain outside retrieval scoring. These counts omit gain magnitudes and the frozen population weights used in the aggregate.

The exact thirteen-variant prefix was replayed with the frozen scheduler and mutation implementation. Original native scores, weighted case metrics, profiles, events and miss counts matched. All four declared expansion settings were tested: two initial misses, the candidate-012 gain, and this miss. The mechanism ends by catalog exhaustion with one consecutive miss, not by the three-miss rule. Candidate-014 starts relevance-diversity with relevance `1.0` and both novelty weights `0.0` on retained candidate-012.

The stronger expansion is useful evidence of a coverage/ranking tradeoff. Its exact candidate and native artifacts remain in the development archive, but the secondary metric gains do not replace the fixed nDCG objective or authorize promotion. Any future coverage-oriented objective must be declared before a separate study.

The two original jobs took 22.79 and 22.71 minutes, with evidence integrity 1.0, no errors and no retries. These are observed job durations, not proof that the profile caused the timing difference, campaign wall time or an invoice. The separate native diagnostic threshold is 0.8.

Scope: 120 stratified development questions, 112 eligible questions, eligible population weight 470 and 6,000 reference-enriched complete documents. This report reuses original evidence with no new native trial, language model call or private validation. The complete family search, all-500 comparison and whole-bundle gates remain pending. No profile is promoted.

[Exact aggregates and source hashes](aggregate.json) · [Retained Adaptive gain](../adaptive-progress-004/README.md) · [Classical expansion gain](../classical-progress-006/README.md) · [Campaign](../README.md)
