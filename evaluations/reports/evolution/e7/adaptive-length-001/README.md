# E7 Adaptive: three length-normalization misses

Three consecutive qualified variants failed to improve the fixed primary nDCG@10. The controller retains the 60.04% baseline and advances to BM25 saturation, beginning with `bm25.k1=0.6`. The Adaptive family search is still in progress.

| Configuration | Weighted nDCG@10 | Weighted recall@10 | Weighted MRR@10 | Weighted full qrel coverage@10 | Native job minutes |
| --- | ---: | ---: | ---: | ---: | ---: |
| baseline | 60.04 | 69.19 | 60.70 | 62.39 | 23.13 |
| bm25.b=0.25 | 59.69 | 67.30 | 61.30 | 60.37 | 23.09 |
| bm25.b=0 | 58.00 | 67.07 | 58.80 | 59.66 | 22.99 |
| bm25.b=0.5 | 59.64 | 68.37 | 60.61 | 61.56 | 22.92 |

Quality columns are percentages. The report recomputes every metric from the original native case scores and the frozen category weights. Improving another metric does not replace nDCG@10 as the selection objective. All four original jobs have evidence integrity 1.0, no execution errors and no retries. The separate diagnostic threshold is 0.8.

The exact three-attempt prefix was replayed using the digest-locked scheduler and mutation implementation. Each profile, score, miss count, retained baseline and event list matched the original artifacts. The next replayed mutation also matched the already sealed native candidate-004 contract. This is a mechanism-prefix audit, not a terminal family audit.

`bm25.b=1.0` is the one untested option skipped by the three-miss rule in this pass. This report does not claim that the skipped setting or every possible normalization setting is ineffective. A later improving catalog round may revisit this mechanism under the frozen schedule.

The three variant jobs consumed 69.00 minutes in total; including the baseline, the four jobs sum to 92.13 minutes. These are summed original job durations, not campaign wall time or an invoice. No language model calls were made.

Scope: 120 stratified development questions, 112 eligible for retrieval scoring, eligible population weight 470 and 6,000 reference-enriched complete documents. The remaining mechanisms, complete family history, joint replay/freeze, all-500 comparison and private transfer gate remain pending. No answer Overall score or official public rank is established.

[Exact aggregates and native hashes](aggregate.json) · [Initial Adaptive measurement](../adaptive-baseline-001/README.md) · [Campaign](../README.md)
