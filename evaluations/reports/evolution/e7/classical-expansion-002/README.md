# E7 Classical: three expansion misses after a gain

Candidate-011 remains retained at 60.097820% primary fusion nDCG@10. The three following expansion variants qualified but did not improve it. The controller ends this mechanism after three consecutive misses and advances to relevance versus diversity.

| Configuration | Association / topic weights | Weighted nDCG@10 | Delta vs candidate-011 (pp) | Consecutive misses | Native job minutes |
| --- | --- | ---: | ---: | ---: | ---: |
| candidate-011 | 0.0875 / 0.05 | 60.097820 | +0.000000 | 0 | 26.94 |
| candidate-012 | 0 / 0 | 60.095906 | -0.001915 | 1 | 26.28 |
| candidate-013 | 0.175 / 0.1 | 60.014757 | -0.083063 | 2 | 27.30 |
| candidate-014 | 0.7 / 0.4 | 59.994413 | -0.103408 | 3 | 27.74 |

The first row was a gain over candidate-010. The other rows compare against that new incumbent. Extra precision shows the small losses; display rounding never changes the strict 1e-12 improvement rule. All four original jobs have evidence integrity 1.0, no execution errors and no retries. The separate diagnostic threshold is 0.8.

candidate-012 versus candidate-011, eligible question counts: 1 improved, 1 regressed and 110 tied. Eight questions without references have no retrieval score.

candidate-013 versus candidate-011, eligible question counts: 0 improved, 2 regressed and 110 tied. Eight questions without references have no retrieval score.

candidate-014 versus candidate-011, eligible question counts: 3 improved, 4 regressed and 105 tied. Eight questions without references have no retrieval score.

The exact fourteen-variant prefix was replayed with the frozen scheduler and mutation implementation. Native scores, all route metrics, profiles, events and miss counts matched. The replayed next mutation matches the sealed candidate-015 contract: relevance weight `1.0`, topic novelty `0.0` and source novelty `0.0`, on the retained BM25 and expansion base.

All four declared expansion options were exercised in this round. The terminal event records three consecutive misses with no unused option; the complete family search is still unfinished and an improving later catalog round may revisit expansion.

Scope: 120 stratified development questions, 112 eligible questions, eligible population weight 470 and 6,000 reference-enriched complete documents. Durations are original job observations, not campaign wall time or an invoice. No native trial was rerun for this report, no language model calls were made and private validation remains unopened. The all-500 comparison and whole-bundle gates remain pending; no profile is promoted.

[Exact aggregates and evidence hashes](aggregate.json) · [Retained Classical gain](../classical-progress-006/README.md) · [Earlier zero-expansion detail](../classical-expansion-001/README.md) · [Campaign](../README.md)
