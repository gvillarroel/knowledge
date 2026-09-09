# Adaptive: first native aspect-allocation trial

Candidate017 sets `adaptive.aspect_weight=0.0` on retained candidate014. Its original native trial ties the incumbent at **66.20879880681476% weighted nDCG@10**. All 120 ordered hit payloads and all 120 per-case metric entries are exactly equal, including the eight no-reference entries. This is the first qualified miss in the aspect-allocation mechanism; candidate014 remains retained.

| Configuration | Weighted nDCG@10 | Weighted recall@10 | Weighted MRR@10 | Weighted full qrel coverage@10 |
| --- | ---: | ---: | ---: | ---: |
| candidate-014 | 66.21 | 74.02 | 67.37 | 69.27 |
| candidate-017 | 66.21 | 74.02 | 67.37 | 69.27 |

Quality columns are percentages. Both jobs use the same 120 stratified development questions, 112 eligible questions, eligible population weight 470 and 6,000 reference-enriched full-text documents. Both completed with evidence integrity 1.0, no errors and no retries. The comparison of original responses excludes timing fields but retains the complete hit payloads and their order. No retrieval run was repeated for this audit.

## What this establishes

Both profiles return ten hits for every query. The [earlier configuration audit](../catalog-audit-001/README.md) proved a conditional mechanism: when ten full-query identities are protected, aspect weights cannot change that top ten. The bridge omits the full-query protection metadata, so ten final hits do not independently establish how many were protected. This report verifies the observed tie without claiming that protection alone caused it.

The exact seventeen-variant prefix, every recorded controller decision and the next sealed mutation replayed. The next variant sets `adaptive.aspect_weight=0.5` on candidate014. The later `1.0` variant also remains subject to the declared controller. Neither a three-miss stop nor catalog exhaustion has occurred in this mechanism, and the family search remains unfinished.

The explicit native diagnostic reporting threshold is 0.8. Falling below that display threshold does not make an error-free qualified retrieval trial an execution failure. Only the fixed development objective drives retention. No private gate, all-500 comparison, answer Overall, public rank or canonical promotion is established here.

[Exact aggregates and native response bindings](aggregate.json) · [Retained Adaptive gain](../adaptive-progress-005/README.md) · [Campaign](../README.md)
