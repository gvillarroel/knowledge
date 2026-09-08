# E7 Adaptive: a recall gain with a ranking loss

Candidate-010 tests association weight `0.0875` and topic weight `0.05` on the retained `bm25.k1=3.0`, title-weight `1.0` base. Recall rises slightly, but primary nDCG and MRR fall. The controller retains candidate-009 and records the first qualified expansion miss.

| Configuration | Weighted nDCG@10 | Weighted recall@10 | Weighted MRR@10 | Weighted full qrel coverage@10 |
| --- | ---: | ---: | ---: | ---: |
| candidate-009 | 65.23 | 71.23 | 67.33 | 64.41 |
| candidate-010 | 64.39 | 71.31 | 66.20 | 64.41 |
| Change in percentage points | -0.8395 | +0.0788 | -1.1243 | +0.0000 |

Metric columns are percentages; the last row is a paired aggregate difference in percentage points. The frozen selection objective remains primary nDCG@10. A gain in a secondary metric does not replace that objective after observing the result.

Against candidate-009, eligible question counts are 6 improved, 5 regressed and 101 tied in nDCG. Eight questions without references remain outside retrieval scoring. Question counts omit gain magnitudes and the frozen population weights; more improving questions do not guarantee a higher weighted mean.

The exact ten-variant prefix was replayed with the frozen scheduler and mutation implementation. Original native scores, weighted case metrics, profiles, events and miss counts matched. The next sealed candidate-011 contract sets both expansion weights to zero; this mechanism is still in progress after one miss.

These expansion weights had previously helped the tested Classical configuration. Their effect differs in this tested Adaptive configuration. The comparison supports keeping family-specific measured profiles; it does not establish a universal expansion setting.

The two original jobs took 22.92 and 25.68 minutes, with evidence integrity 1.0, no errors and no retries. These are observed job durations, not proof that the profile caused the timing difference, campaign wall time or an invoice. The separate native diagnostic threshold is 0.8.

Scope: 120 stratified development questions, 112 eligible questions, eligible population weight 470 and 6,000 reference-enriched complete documents. This report reuses original evidence with no new native trial, language model call or private validation. The complete family search, all-500 comparison and whole-bundle gates remain pending. No profile is promoted.

[Exact aggregates and source hashes](aggregate.json) · [Retained Adaptive gain](../adaptive-progress-003/README.md) · [Classical expansion gain](../classical-progress-006/README.md) · [Campaign](../README.md)
