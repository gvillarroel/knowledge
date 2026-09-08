# E7 Classical zero expansion: a small measured loss

Setting both expansion weights to zero did not improve the fixed primary fusion nDCG@10. The controller retained candidate-011 and counted one qualified miss. Both scores display as 60.10% at two decimal places, but the decision uses their unrounded values.

| Configuration | Weighted nDCG@10 | Weighted recall@10 | Weighted MRR@10 | Weighted full qrel coverage@10 | Native job minutes |
| --- | ---: | ---: | ---: | ---: | ---: |
| candidate-011 | 60.097820 | 63.59 | 63.88 | 56.91 | 26.94 |
| candidate-012 | 60.095906 | 63.59 | 63.88 | 56.91 | 26.28 |

The change is **-0.001915 percentage points**. Quality columns are percentages; nDCG is shown with extra precision to make the small difference visible. Display rounding does not change the strict improvement rule or the 1e-12 comparison tolerance.

Against candidate-011, one eligible question improves, one regresses and 110 tie. Eight questions without references have no retrieval score. The reference is the preceding incumbent, not the study initial baseline. The source audit reaggregated every metric on all four routes from original cases and also preserved the initial-baseline comparison.

Both original jobs qualified with evidence integrity 1.0, no execution errors and no retries. The separate diagnostic threshold is 0.8. Job duration is observed original runtime; it does not replace nDCG as the selection objective and is not a campaign wall-time or invoice measure.

The next sealed mutation tests association weight 0.175 and topic weight 0.1 on the retained BM25 base. This is the first expansion miss, so the mechanism continues. No trial was rerun for this report and no private validation was opened.

Scope: 120 stratified development questions, 112 eligible questions, eligible population weight 470 and 6,000 reference-enriched complete documents. The family search, all-500 comparison and whole-bundle gates remain pending. No profile is promoted.

[Exact aggregates and source hashes](aggregate.json) · [Retained Classical gain](../classical-progress-006/README.md) · [Campaign](../README.md)
